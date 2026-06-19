import logging
from datetime import datetime, timedelta
from typing import Dict, List
from .email_reader import EmailReader
from .ai_parser import OrderParser
from .lead_scorer import LeadScorer
from .database import Database
from .config import YANDEX_EMAIL, YANDEX_PASSWORD, YANDEX_IMAP_SERVER, YANDEX_IMAP_PORT

logger = logging.getLogger(__name__)


class EmailCenterDashboard:
    """Real-time Email Center analytics and insights"""

    def __init__(self):
        self.reader = EmailReader(
            YANDEX_EMAIL, YANDEX_PASSWORD, YANDEX_IMAP_SERVER, YANDEX_IMAP_PORT
        )
        self.parser = OrderParser()
        self.scorer = LeadScorer()
        self.db = Database()

    def get_48_hour_summary(self) -> Dict:
        """Analyze last 48 hours of emails"""
        self.reader.connect()
        self.reader.mail.select("INBOX")

        since_date = (datetime.now() - timedelta(days=2)).strftime("%d-%b-%Y")
        status, messages = self.reader.mail.search(None, "SINCE", since_date)
        recent_ids = messages[0].split()

        summary = {
            "period": "Last 48 hours",
            "total_emails": len(recent_ids),
            "orders_found": 0,
            "high_priority": 0,
            "medium_priority": 0,
            "low_priority": 0,
            "by_type": {},
            "by_route": {},
            "orders": [],
            "timestamp": datetime.now().isoformat(),
        }

        import email

        for email_id in recent_ids[-20:]:
            status, msg_data = self.reader.mail.fetch(email_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            subject = self.reader.decode_str(msg.get("Subject", ""))
            from_email = self.reader.decode_str(msg.get("From", ""))
            body = self.reader.get_email_body(msg)

            if self.parser.is_order(subject, body):
                summary["orders_found"] += 1

                order_data = self.parser.extract_order_data(subject, body, from_email)
                score = self.scorer.score_lead(order_data)
                classification = self.scorer.classify_order_type(subject, body)

                # Categorize by priority
                priority_level = score["priority"]["level"]
                if priority_level == "CRITICAL":
                    summary["high_priority"] += 1
                elif priority_level == "MEDIUM":
                    summary["medium_priority"] += 1
                else:
                    summary["low_priority"] += 1

                # Track by type
                order_type = classification["type"]
                summary["by_type"][order_type] = summary["by_type"].get(order_type, 0) + 1

                # Track by route
                for route in classification["route_to"]:
                    summary["by_route"][route] = summary["by_route"].get(route, 0) + 1

                # Store order details
                summary["orders"].append(
                    {
                        "company": order_data.get("client_name", "Unknown"),
                        "material": order_data.get("material", "N/A"),
                        "quantity": order_data.get("quantity", "N/A"),
                        "score": score["score"],
                        "stars": score["stars"],
                        "priority": score["priority"]["emoji"],
                        "type": order_type,
                        "routes": classification["route_to"],
                    }
                )

        self.reader.disconnect()
        return summary

    def format_report(self, summary: Dict) -> str:
        """Format summary as readable report"""
        report = f"""
╔════════════════════════════════════════════════════════╗
║           EMAIL CENTER DASHBOARD                       ║
╚════════════════════════════════════════════════════════╝

📊 {summary['period']}

Total Emails: {summary['total_emails']}
Orders Found: {summary['orders_found']}

Priority Distribution:
  🔴 Critical: {summary['high_priority']}
  🟡 Medium: {summary['medium_priority']}
  🔵 Low: {summary['low_priority']}

By Order Type:
"""
        for order_type, count in summary["by_type"].items():
            report += f"  {order_type}: {count}\n"

        report += "\nRouting Distribution:\n"
        for route, count in summary["by_route"].items():
            report += f"  {route}: {count} notifications\n"

        report += "\n📋 Order Details:\n"
        for i, order in enumerate(summary["orders"], 1):
            report += f"\n  {i}. {order['priority']} {order['company']}\n"
            report += f"     Material: {order['material']} | Qty: {order['quantity']}\n"
            report += f"     Score: {order['stars']} ({order['score']}/100)\n"
            report += f"     Routes: {', '.join(order['routes'])}\n"

        report += "\n" + "=" * 55
        return report

    def run_dashboard(self) -> str:
        """Run dashboard and return formatted report"""
        summary = self.get_48_hour_summary()
        return self.format_report(summary)
