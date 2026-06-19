"""
Manager Dashboard API
Provides real-time order data for managers
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict
from .database import Database
from .email_reader import EmailReader
from .ai_parser import OrderParser
from .lead_scorer import LeadScorer
from .config import YANDEX_EMAIL, YANDEX_PASSWORD, YANDEX_IMAP_SERVER, YANDEX_IMAP_PORT

logger = logging.getLogger(__name__)


class ManagerAPI:
    """Provides real-time dashboard data for managers"""

    def __init__(self):
        self.db = Database()
        self.reader = EmailReader(
            YANDEX_EMAIL, YANDEX_PASSWORD, YANDEX_IMAP_SERVER, YANDEX_IMAP_PORT
        )
        self.parser = OrderParser()
        self.scorer = LeadScorer()

    def get_all_orders(self, limit: int = 50, days: int = 7) -> List[Dict]:
        """Get all orders from last N days"""
        orders = []

        self.reader.connect()
        self.reader.mail.select("INBOX")

        since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
        status, messages = self.reader.mail.search(None, "SINCE", since_date)
        email_ids = messages[0].split()[-limit:]

        import email

        for email_id in email_ids:
            try:
                status, msg_data = self.reader.mail.fetch(email_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                subject = self.reader.decode_str(msg.get("Subject", ""))
                from_email = self.reader.decode_str(msg.get("From", ""))
                body = self.reader.get_email_body(msg)

                if not self.parser.is_order(subject, body):
                    continue

                order_data = self.parser.extract_order_data(subject, body, from_email)
                score = self.scorer.score_lead(order_data)

                order = {
                    "id": len(orders) + 1,
                    "company": order_data.get("client_name", "Unknown"),
                    "material": order_data.get("material", "Unknown"),
                    "quantity": order_data.get("quantity", "?"),
                    "size": order_data.get("sizes", "?"),
                    "score": score["score"],
                    "priority": score["priority"]["level"].lower(),
                    "stars": score["stars"],
                    "phone": order_data.get("client_phone", "?"),
                    "email": order_data.get("client_email", "?"),
                    "assigned": False,  # In production, check assignment
                    "timestamp": datetime.now().isoformat(),
                }

                orders.append(order)
            except Exception as e:
                logger.error(f"Error processing email: {e}")
                continue

        self.reader.disconnect()
        return orders

    def get_statistics(self) -> Dict:
        """Get dashboard statistics"""
        orders = self.get_all_orders(limit=100)

        critical = sum(1 for o in orders if o["priority"] == "critical")
        high = sum(1 for o in orders if o["priority"] == "high")
        assigned = sum(1 for o in orders if o["assigned"])

        return {
            "total_orders": len(orders),
            "critical_count": critical,
            "high_count": high,
            "assigned_count": assigned,
            "unassigned_count": len(orders) - assigned,
            "avg_response_time": "<5 min",
        }

    def assign_manager(self, order_id: int, manager_name: str) -> bool:
        """Assign order to manager"""
        try:
            # In production, save to database
            logger.info(f"Order {order_id} assigned to {manager_name}")
            return True
        except Exception as e:
            logger.error(f"Error assigning order: {e}")
            return False

    def create_kp(self, order_id: int) -> Dict:
        """Create commercial proposal for order"""
        try:
            # In production, generate KP
            return {
                "success": True,
                "kp_number": f"КП-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "message": "Commercial proposal created",
            }
        except Exception as e:
            logger.error(f"Error creating KP: {e}")
            return {"success": False, "error": str(e)}
