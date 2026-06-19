import logging
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Dict, List

from .email_reader import EmailReader
from .ai_parser import OrderParser
from .lead_scorer import LeadScorer
from .notification_router import NotificationRouter
from .image_export import ImageExporter
from .database import Database
from .config import YANDEX_EMAIL, YANDEX_PASSWORD, YANDEX_IMAP_SERVER, YANDEX_IMAP_PORT

logger = logging.getLogger(__name__)


class EmailProcessorPipeline:
    """Complete email processing: Parse → Score → Route → Generate PNG → Prepare Notification"""

    def __init__(self):
        self.reader = EmailReader(
            YANDEX_EMAIL, YANDEX_PASSWORD, YANDEX_IMAP_SERVER, YANDEX_IMAP_PORT
        )
        self.parser = OrderParser()
        self.scorer = LeadScorer()
        self.router = NotificationRouter()
        self.exporter = ImageExporter()
        self.db = Database()

    def process_last_48_hours(self) -> Dict:
        """Process all orders from last 48 hours"""
        self.reader.connect()
        self.reader.mail.select("INBOX")

        since_date = (datetime.now() - timedelta(days=2)).strftime("%d-%b-%Y")
        status, messages = self.reader.mail.search(None, "SINCE", since_date)
        recent_ids = messages[0].split()

        results = {
            "processed": 0,
            "orders": 0,
            "notifications": [],
            "errors": [],
        }

        import email

        for email_id in recent_ids[-20:]:
            try:
                status, msg_data = self.reader.mail.fetch(email_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                subject = self.reader.decode_str(msg.get("Subject", ""))
                from_email = self.reader.decode_str(msg.get("From", ""))
                body = self.reader.get_email_body(msg)
                results["processed"] += 1

                # Parse
                if not self.parser.is_order(subject, body):
                    continue

                results["orders"] += 1

                # Extract
                order_data = self.parser.extract_order_data(subject, body, from_email)

                # Score
                score = self.scorer.score_lead(order_data)
                order_data["lead_score"] = score["score"]
                order_data["lead_stars"] = score["stars"]
                order_data["lead_priority"] = score["priority"]

                # Classify
                classification = self.scorer.classify_order_type(subject, body)
                order_data["order_type"] = classification["type"]
                order_data["route_to"] = classification["route_to"]

                # Generate PNG
                kp_number = f"КП-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                png_path = self.exporter.generate_commercial_offer(
                    {
                        "kp_number": kp_number,
                        "date": datetime.now().strftime("%d.%m.%Y"),
                        "company": order_data.get("client_name", "Unknown"),
                        "contact_name": order_data.get("client_name", ""),
                        "email": order_data.get("client_email", ""),
                        "phone": order_data.get("client_phone", ""),
                        "material": order_data.get("material", ""),
                        "quantity": order_data.get("quantity", ""),
                        "size": order_data.get("sizes", ""),
                        "color": order_data.get("color", ""),
                        "lead_time": "7-14 дней",
                        "cost": "По запросу",
                        "description": order_data.get("products", ""),
                    }
                )

                # Route
                routes = self.router.route_order(order_data)

                # Format notification
                notification = self._format_notification(
                    order_data, kp_number, png_path, routes
                )
                results["notifications"].append(notification)

            except Exception as e:
                results["errors"].append(str(e))
                logger.error(f"Error processing email: {e}")

        self.reader.disconnect()
        return results

    def _format_notification(
        self, order_data: Dict, kp_number: str, png_path: str, routes: List
    ) -> Dict:
        """Format notification for Telegram"""
        priority = order_data.get("lead_priority", {})
        stars = order_data.get("lead_stars", "☆☆☆☆☆")
        score = order_data.get("lead_score", 0)

        notification = {
            "kp_number": kp_number,
            "telegram_card": (
                f"{priority.get('emoji', '⚫')} <b>{order_data.get('order_type', '?')}</b>\n\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 <b>Компания:</b> {order_data.get('client_name', '?')}\n"
                f"🧱 <b>Материал:</b> {order_data.get('material', '?')}\n"
                f"📦 <b>Количество:</b> {order_data.get('quantity', '?')}\n"
                f"📐 <b>Размеры:</b> {order_data.get('sizes', '?')}\n\n"
                f"<b>{stars}</b> <code>{score}/100 {priority.get('level', '?')}</code>\n\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"📞 {order_data.get('client_phone', '?')}\n"
                f"📧 {order_data.get('client_email', '?')}"
            ),
            "png_path": png_path,
            "targets": [
                {"target": r["target"], "group_id": r["group_id"]} for r in routes
            ],
            "score": score,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
        }

        return notification

    def generate_report(self, results: Dict) -> str:
        """Generate human-readable report"""
        report = f"""
╔════════════════════════════════════════════════════════╗
║         EMAIL PROCESSING PIPELINE COMPLETE             ║
╚════════════════════════════════════════════════════════╝

📧 Processed: {results['processed']} emails
✅ Orders: {results['orders']} identified

Notifications Ready to Send: {len(results['notifications'])}

"""

        for i, notif in enumerate(results["notifications"], 1):
            report += f"\n📬 Notification #{i}\n"
            report += f"   KP: {notif['kp_number']}\n"
            report += f"   Priority: {notif['priority'].get('emoji')} {notif['priority'].get('level')}\n"
            report += f"   Score: {notif['score']}/100\n"
            report += f"   PNG: {Path(notif['png_path']).name}\n"
            report += f"   Targets: {', '.join([t['target'] for t in notif['targets']])}\n"

        if results["errors"]:
            report += f"\n⚠️ Errors: {len(results['errors'])}\n"
            for error in results["errors"][:3]:
                report += f"   - {error}\n"

        report += "\n" + "=" * 55
        report += "\n✅ EMAIL CENTER OPERATIONAL\n"
        report += f"   Last run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 55

        return report
