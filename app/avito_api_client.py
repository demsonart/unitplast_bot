"""
Avito API Client for lead aggregation
Handles OAuth2 authentication and API requests
"""

import requests
import logging
import json
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from functools import wraps
import time

logger = logging.getLogger(__name__)

class AvitoAPIError(Exception):
    """Base exception for Avito API errors"""
    pass

class AvitoAuthError(AvitoAPIError):
    """Authentication error"""
    pass

class AvitoAPIClient:
    """
    Avito API Client
    Handles OAuth2 authentication and API requests for leads
    """

    BASE_URL = "https://api.avito.ru"
    AUTH_URL = "https://api.avito.ru/oauth"

    def __init__(self, client_id: str, client_secret: str, access_token: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.token_expires_at = None
        self.session = requests.Session()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Avito API"""
        url = f"{self.BASE_URL}{endpoint}"

        if self.access_token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.access_token}'
            kwargs['headers'] = headers

        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise AvitoAuthError(f"Authentication failed: {e}")
            raise AvitoAPIError(f"API request failed: {e}")
        except requests.exceptions.RequestException as e:
            raise AvitoAPIError(f"Request failed: {e}")

    def get_access_token(self, client_id: Optional[str] = None,
                        client_secret: Optional[str] = None) -> str:
        """
        Get OAuth2 access token using Client Credentials flow
        Returns: access_token
        """
        client_id = client_id or self.client_id
        client_secret = client_secret or self.client_secret

        try:
            payload = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            }

            response = self.session.post(
                f"{self.AUTH_URL}",
                data=payload,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            self.access_token = data.get('access_token')

            # Set expiration time (usually 1 hour, but use 55 minutes for safety)
            expires_in = data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

            logger.info(f"Avito access token obtained, expires at {self.token_expires_at}")
            return self.access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Avito access token: {e}")
            raise AvitoAuthError(f"Failed to obtain access token: {e}")

    def is_token_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.token_expires_at:
            return True
        return datetime.now() >= self.token_expires_at

    def ensure_token(self) -> None:
        """Ensure we have a valid access token"""
        if not self.access_token or self.is_token_expired():
            self.get_access_token()

    def get_seller_items(self, seller_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get seller's active items/listings

        Args:
            seller_id: Avito seller/user ID
            limit: Number of items to fetch
            offset: Pagination offset

        Returns: Dictionary with items list
        """
        self.ensure_token()

        params = {
            "limit": limit,
            "offset": offset,
            "statuses": ["active"]
        }

        response = self._make_request(
            "GET",
            f"/core/v1/seller/{seller_id}/items",
            params=params
        )

        return response

    def get_item_details(self, item_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific item

        Args:
            item_id: Avito item ID

        Returns: Item details dictionary
        """
        self.ensure_token()

        response = self._make_request(
            "GET",
            f"/core/v1/items/{item_id}"
        )

        return response

    def get_item_offers(self, item_id: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Get offers (leads/inquiries) for a specific item

        Args:
            item_id: Avito item ID
            limit: Number of offers to fetch
            offset: Pagination offset

        Returns: Dictionary with offers list
        """
        self.ensure_token()

        params = {
            "limit": limit,
            "offset": offset
        }

        response = self._make_request(
            "GET",
            f"/core/v1/items/{item_id}/offers",
            params=params
        )

        return response

    def get_chats(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Get list of chats (conversations)

        Args:
            limit: Number of chats to fetch
            offset: Pagination offset

        Returns: Dictionary with chats list
        """
        self.ensure_token()

        params = {
            "limit": limit,
            "offset": offset
        }

        response = self._make_request(
            "GET",
            "/core/v1/chats",
            params=params
        )

        return response

    def get_chat_messages(self, chat_id: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get messages from a specific chat

        Args:
            chat_id: Chat ID
            limit: Number of messages to fetch

        Returns: Dictionary with messages list
        """
        self.ensure_token()

        params = {
            "limit": limit
        }

        response = self._make_request(
            "GET",
            f"/core/v1/chats/{chat_id}/messages",
            params=params
        )

        return response

    def send_message(self, chat_id: str, text: str) -> Dict[str, Any]:
        """
        Send a message in chat

        Args:
            chat_id: Chat ID
            text: Message text

        Returns: Response with message details
        """
        self.ensure_token()

        payload = {
            "text": text
        }

        response = self._make_request(
            "POST",
            f"/core/v1/chats/{chat_id}/messages",
            json=payload
        )

        return response

    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get current user profile information

        Returns: User profile dictionary
        """
        self.ensure_token()

        response = self._make_request(
            "GET",
            "/core/v1/user/profile"
        )

        return response

    def get_offers_for_user(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Get all offers (inquiries/leads) for current user's items

        Args:
            limit: Number of offers to fetch
            offset: Pagination offset

        Returns: Dictionary with offers list
        """
        self.ensure_token()

        params = {
            "limit": limit,
            "offset": offset,
            "sort": "-created_at"  # Sort by newest first
        }

        response = self._make_request(
            "GET",
            "/core/v1/offers",
            params=params
        )

        return response

    def get_leads(self, limit: int = 100, offset: int = 0,
                  status: Optional[str] = None) -> Dict[str, Any]:
        """
        Get leads from Avito

        Args:
            limit: Number of leads to fetch
            offset: Pagination offset
            status: Optional status filter (new, responded, archived)

        Returns: Dictionary with leads list
        """
        self.ensure_token()

        params = {
            "limit": limit,
            "offset": offset
        }

        if status:
            params["status"] = status

        response = self._make_request(
            "GET",
            "/core/v1/leads",
            params=params
        )

        return response

    def mark_lead_as_read(self, lead_id: str) -> Dict[str, Any]:
        """
        Mark a lead as read

        Args:
            lead_id: Lead ID

        Returns: Response dictionary
        """
        self.ensure_token()

        response = self._make_request(
            "PUT",
            f"/core/v1/leads/{lead_id}",
            json={"status": "read"}
        )

        return response

    def get_new_leads(self) -> List[Dict[str, Any]]:
        """
        Get new unread leads

        Returns: List of lead dictionaries
        """
        self.ensure_token()

        try:
            response = self.get_leads(limit=100, status="new")
            return response.get('leads', [])
        except AvitoAPIError as e:
            logger.error(f"Failed to get new leads: {e}")
            return []
