"""
Avito Lead Poller
Periodically fetches new leads from Avito and forwards them to unified inbox
"""

import logging
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import threading
from app.avito_api_client import AvitoAPIClient, AvitoAPIError
from app.unified_inbox import Channel, UnifiedInbox, LeadStatus

logger = logging.getLogger(__name__)

class AvitoLeadPoller:
    """
    Polls Avito for new leads and integrates them into unified inbox
    """

    def __init__(self, client_id: str, client_secret: str,
                 poll_interval: int = 300, unified_inbox: Optional[UnifiedInbox] = None):
        """
        Initialize Avito Lead Poller

        Args:
            client_id: Avito client ID
            client_secret: Avito client secret
            poll_interval: Poll interval in seconds (default 5 minutes)
            unified_inbox: UnifiedInbox instance for storing leads
        """
        self.client = AvitoAPIClient(client_id, client_secret)
        self.poll_interval = poll_interval
        self.inbox = unified_inbox or UnifiedInbox()
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.last_poll_time = None
        self.last_lead_id = None
        self.processed_leads = set()  # Track processed lead IDs to avoid duplicates

    def normalize_lead_data(self, avito_lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize Avito lead data to standard format

        Args:
            avito_lead: Raw lead data from Avito API

        Returns: Normalized lead dictionary
        """
        return {
            "source": "avito",
            "avito_id": avito_lead.get('id'),
            "buyer_name": avito_lead.get('buyer', {}).get('name', 'Unknown'),
            "buyer_phone": avito_lead.get('buyer', {}).get('phone', ''),
            "buyer_location": avito_lead.get('buyer', {}).get('location', ''),
            "item_id": avito_lead.get('item', {}).get('id'),
            "item_title": avito_lead.get('item', {}).get('title', ''),
            "item_price": avito_lead.get('item', {}).get('price', ''),
            "message": avito_lead.get('message', ''),
            "chat_id": avito_lead.get('chat_id', ''),
            "created_at": avito_lead.get('created_at', datetime.now().isoformat()),
            "status": avito_lead.get('status', 'new'),
            "is_read": avito_lead.get('is_read', False),
            "offer_id": avito_lead.get('offer_id'),
        }

    def process_lead(self, avito_lead: Dict[str, Any]) -> Optional[str]:
        """
        Process a single lead from Avito

        Args:
            avito_lead: Raw lead data from Avito API

        Returns: Lead ID if successfully processed, None otherwise
        """
        try:
            lead_id = avito_lead.get('id')

            # Skip if already processed
            if lead_id in self.processed_leads:
                logger.debug(f"Lead {lead_id} already processed, skipping")
                return None

            # Skip read leads
            if avito_lead.get('is_read'):
                logger.debug(f"Lead {lead_id} is already read, skipping")
                return None

            # Normalize lead data
            normalized_data = self.normalize_lead_data(avito_lead)

            # Create lead in unified inbox
            inbox_lead_id = self.inbox.create_lead(Channel.AVITO, normalized_data)

            if inbox_lead_id:
                self.processed_leads.add(lead_id)
                logger.info(f"Processed Avito lead {lead_id} → inbox lead {inbox_lead_id}")
                return inbox_lead_id

            return None

        except Exception as e:
            logger.error(f"Error processing Avito lead: {e}")
            return None

    def fetch_new_leads(self) -> List[Dict[str, Any]]:
        """
        Fetch new leads from Avito API

        Returns: List of new leads
        """
        try:
            logger.info("Fetching new leads from Avito...")
            leads = self.client.get_new_leads()

            if leads:
                logger.info(f"Found {len(leads)} new leads from Avito")
                return leads
            else:
                logger.debug("No new leads from Avito")
                return []

        except AvitoAPIError as e:
            logger.error(f"Failed to fetch Avito leads: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching Avito leads: {e}")
            return []

    def poll_once(self) -> int:
        """
        Perform a single poll for new leads

        Returns: Number of new leads processed
        """
        try:
            self.last_poll_time = datetime.now()

            # Fetch new leads
            leads = self.fetch_new_leads()

            if not leads:
                return 0

            # Process each lead
            processed_count = 0
            for lead in leads:
                if self.process_lead(lead):
                    processed_count += 1

            logger.info(f"Poll completed: {processed_count} new leads processed")
            return processed_count

        except Exception as e:
            logger.error(f"Error during poll: {e}")
            return 0

    def _polling_loop(self) -> None:
        """Main polling loop (runs in separate thread)"""
        logger.info(f"Avito Lead Poller started (interval: {self.poll_interval}s)")

        while self.is_running:
            try:
                self.poll_once()
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")

            # Sleep until next poll
            time.sleep(self.poll_interval)

        logger.info("Avito Lead Poller stopped")

    def start(self) -> None:
        """Start polling for new leads"""
        if self.is_running:
            logger.warning("Avito Lead Poller already running")
            return

        self.is_running = True
        self.thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.thread.start()
        logger.info("Avito Lead Poller started")

    def stop(self) -> None:
        """Stop polling for new leads"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Avito Lead Poller stopped")

    def get_status(self) -> Dict[str, Any]:
        """
        Get poller status

        Returns: Status dictionary
        """
        return {
            "is_running": self.is_running,
            "last_poll_time": self.last_poll_time.isoformat() if self.last_poll_time else None,
            "processed_leads_count": len(self.processed_leads),
            "poll_interval": self.poll_interval,
        }
