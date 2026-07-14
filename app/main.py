import asyncio
import logging
import sys
from datetime import datetime
from .config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID,
    YANDEX_EMAIL, YANDEX_PASSWORD, YANDEX_IMAP_SERVER, YANDEX_IMAP_PORT,
    COMPANY_NAME, COMPANY_EMAIL, COMPANY_PHONE, EMAIL_CHECK_INTERVAL, PROCESS_ONLY_UNSEEN,
    AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, AVITO_POLL_INTERVAL, AVITO_ENABLED,
    validate_config
)
from .email_reader import EmailReader
from .ai_parser import OrderParser
from .image_export import ImageExporter
from .database import Database
from .telegram_final_bot import TelegramFinalBot
from .lead_scorer import LeadScorer
from .notification_router import NotificationRouter
from .avito_lead_poller import AvitoLeadPoller
from .unified_inbox import Channel, LeadStatus
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrderBot:
    def __init__(self):
        validate_config()
        self.email_reader = EmailReader(
            YANDEX_EMAIL,
            YANDEX_PASSWORD,
            YANDEX_IMAP_SERVER,
            YANDEX_IMAP_PORT
        )
        self.parser = OrderParser()
        self.image_exporter = ImageExporter()
        self.db = Database()
        self.telegram_bot = TelegramFinalBot()
        self.lead_scorer = LeadScorer()
        self.notification_router = NotificationRouter()

        # Initialize Avito Lead Poller if enabled
        self.avito_poller = None
        if AVITO_ENABLED and AVITO_CLIENT_ID and AVITO_CLIENT_SECRET:
            self.avito_poller = AvitoLeadPoller(
                client_id=AVITO_CLIENT_ID,
                client_secret=AVITO_CLIENT_SECRET,
                poll_interval=AVITO_POLL_INTERVAL,
                unified_inbox=self.telegram_bot.inbox
            )
            logger.info("Avito Lead Poller initialized")
        else:
            logger.warning("Avito integration disabled or credentials missing")

        self.running = True

    def connect_email(self):
        try:
            self.email_reader.connect()
            logger.info("Connected to email server")
        except Exception as e:
            logger.error(f"Failed to connect to email: {e}")
            raise

    def disconnect_email(self):
        self.email_reader.disconnect()
        logger.info("Disconnected from email server")

    async def process_emails(self):
        """Process new emails and create orders"""
        try:
            # Get emails based on config
            if PROCESS_ONLY_UNSEEN:
                emails = self.email_reader.get_unread_emails()
                logger.info(f"Found {len(emails)} unread emails")
            else:
                emails = self.email_reader.get_new_emails(limit=20)
                logger.info(f"Found {len(emails)} recent emails (unprocessed only)")

            for message_id, subject, from_email, body in emails:
                # Check if already processed
                if self.db.is_email_processed(message_id):
                    logger.info(f"Email {message_id} already processed")
                    continue

                logger.info(f"Processing email from {from_email}: {subject}")

                # Check if it's an order
                if not self.parser.is_order(subject, body):
                    logger.info(f"Email is not an order")
                    self.db.add_processed_email(message_id, subject, from_email, is_order=False)
                    continue

                # Extract order data
                order_data = self.parser.extract_order_data(subject, body, from_email)
                if not order_data:
                    logger.warning(f"Failed to extract order data")
                    self.db.add_processed_email(message_id, subject, from_email, is_order=False)
                    continue

                logger.info(f"Order data extracted: {order_data}")

                # [NEW] Score the lead
                score_result = self.lead_scorer.score_lead(order_data)
                order_data['lead_score'] = score_result['score']
                order_data['lead_stars'] = score_result['stars']
                order_data['lead_priority'] = score_result['priority']
                logger.info(f"Lead scored: {score_result['stars']} ({score_result['score']}/100) - {score_result['priority']['level']}")

                # [NEW] Classify order type
                classification = self.lead_scorer.classify_order_type(subject, body)
                order_data['order_type'] = classification['type']
                order_data['route_to'] = classification['route_to']
                logger.info(f"Order type: {classification['type']} → Route to: {', '.join(classification['route_to'])}")

                # Generate commercial offer as PNG image
                kp_number = f"КП-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                image_path = self.image_exporter.generate_commercial_offer({
                    "kp_number": kp_number,
                    "date": datetime.now().strftime('%d.%m.%Y'),
                    "company": order_data.get('client_name', 'Unknown'),
                    "contact_name": order_data.get('client_name', ''),
                    "email": order_data.get('client_email', ''),
                    "phone": order_data.get('client_phone', ''),
                    "material": order_data.get('material', ''),
                    "quantity": order_data.get('quantity', ''),
                    "size": order_data.get('size', ''),
                    "color": order_data.get('color', ''),
                    "lead_time": "7-14 дней",
                    "cost": "По запросу",
                    "description": order_data.get('products', '')
                })

                if not image_path:
                    logger.error(f"Failed to generate PNG image")
                    self.db.add_processed_email(message_id, subject, from_email, is_order=False)
                    continue

                # Save to database
                email_id = self.db.add_processed_email(
                    message_id,
                    subject,
                    from_email,
                    is_order=True,
                    order_data=str(order_data)
                )

                order_id = self.db.add_order(
                    email_id=email_id,
                    client_name=order_data.get('client_name', ''),
                    client_email=order_data.get('client_email', ''),
                    client_phone=order_data.get('client_phone', ''),
                    products=order_data.get('products', ''),
                    delivery_type=order_data.get('delivery_type', ''),
                    deadline=order_data.get('deadline', ''),
                    comments=order_data.get('comments', ''),
                    pdf_path=image_path
                )

                logger.info(f"Order saved with ID: {order_id}")

                # [NEW] Generate beautiful notification card
                priority_emoji = order_data.get('lead_priority', {}).get('emoji', '⚫')
                priority_level = order_data.get('lead_priority', {}).get('level', 'LOW')
                stars = order_data.get('lead_stars', '☆☆☆☆☆')
                score = order_data.get('lead_score', 0)

                summary = (
                    f"{priority_emoji} <b>{order_data.get('order_type', '🟢 НОВЫЙ ЗАКАЗ')}</b>\n\n"
                    f"━━━━━━━━━━━━━━━━━━\n\n"
                    f"📋 <b>Компания:</b> {order_data.get('client_name', 'Не указано')}\n"
                    f"🧱 <b>Материал:</b> {order_data.get('material', 'Не указано')}\n"
                    f"📦 <b>Количество:</b> {order_data.get('quantity', 'Не указано')}\n"
                    f"📐 <b>Размеры:</b> {order_data.get('sizes', 'Не указано')}\n\n"
                    f"<b>{stars}</b> <code>{score}/100 {priority_level}</code>\n\n"
                    f"━━━━━━━━━━━━━━━━━━\n\n"
                    f"📞 {order_data.get('client_phone', '?')}\n"
                    f"📧 {order_data.get('client_email', '?')}"
                )

                # [NEW] Route to appropriate targets
                routes = self.notification_router.route_order(order_data)
                sent_count = 0

                for route in routes:
                    target_name = route['target']
                    group_id = route['group_id']

                    if group_id:
                        try:
                            await self.telegram_bot.send_order_to_group(summary, image_path, group_id)
                            sent_count += 1
                            logger.info(f"Order sent to {target_name} (group_id: {group_id})")
                        except Exception as e:
                            logger.error(f"Failed to send to {target_name}: {e}")
                    else:
                        logger.warning(f"Target {target_name} has no group_id configured")

                logger.info(f"Order notification sent to {sent_count} targets")

        except Exception as e:
            logger.error(f"Error processing emails: {e}")

    async def email_polling_loop(self):
        """Polling loop for checking new emails"""
        while self.running:
            try:
                self.connect_email()
                await self.process_emails()
                self.disconnect_email()
            except Exception as e:
                logger.error(f"Error in email polling loop: {e}")

            # Wait before next check
            await asyncio.sleep(EMAIL_CHECK_INTERVAL)

    async def avito_inbox_monitor(self):
        """Monitor unified inbox for new Avito leads and send notifications"""
        if not self.avito_poller:
            return

        last_lead_count = 0

        while self.running:
            try:
                # Get current Avito leads
                avito_leads = self.telegram_bot.inbox.get_leads_by_channel(Channel.AVITO)

                # Check for new leads
                if len(avito_leads) > last_lead_count:
                    new_leads_count = len(avito_leads) - last_lead_count
                    new_leads = avito_leads[-new_leads_count:]

                    for lead in new_leads:
                        await self._notify_avito_lead(lead)

                    last_lead_count = len(avito_leads)

            except Exception as e:
                logger.error(f"Error monitoring Avito inbox: {e}")

            # Check every 10 seconds
            await asyncio.sleep(10)

    async def _notify_avito_lead(self, lead: dict):
        """Send notification about new Avito lead"""
        try:
            data = lead.get("data", {})
            lead_id = lead.get("id", "")

            # Format notification
            notification = (
                f"📱 <b>AVITO ЛИД</b>\n\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"👤 <b>Имя:</b> {data.get('buyer_name', '?')}\n"
                f"📞 <b>Телефон:</b> {data.get('buyer_phone', '?')}\n"
                f"📍 <b>Локация:</b> {data.get('buyer_location', '?')}\n\n"
                f"🏷️ <b>Товар:</b> {data.get('item_title', '?')}\n"
                f"💰 <b>Цена:</b> {data.get('item_price', '?')}\n\n"
                f"💬 <b>Сообщение:</b>\n{data.get('message', '—')}\n\n"
                f"━━━━━━━━━━━━━━━━━━\n\n"
                f"<code>Лид ID: {lead_id}</code>"
            )

            # Get targets for Avito notifications
            routes = self.notification_router.route_order({
                "order_type": "AVITO_LEAD",
                "priority": {"level": "NORMAL"},
                "score": 50
            })

            # Send to all configured targets
            sent_count = 0
            for route in routes:
                try:
                    group_id = route.get("group_id")
                    if group_id:
                        await self.telegram_bot.bot.send_message(
                            chat_id=group_id,
                            text=notification,
                            parse_mode="HTML"
                        )
                        sent_count += 1
                        logger.info(f"Sent Avito lead notification to {route['target']}")
                except Exception as e:
                    logger.error(f"Failed to send to {route['target']}: {e}")

            # Also send to main group if no targets configured
            if sent_count == 0 and TELEGRAM_GROUP_ID:
                try:
                    await self.telegram_bot.bot.send_message(
                        chat_id=TELEGRAM_GROUP_ID,
                        text=notification,
                        parse_mode="HTML"
                    )
                    logger.info(f"Sent Avito lead to main group")
                except Exception as e:
                    logger.error(f"Failed to send to main group: {e}")

            logger.info(f"Avito lead {lead_id} notification sent to {sent_count} targets")

        except Exception as e:
            logger.error(f"Error notifying Avito lead: {e}")

    async def run(self):
        """Start bot, email polling, and Avito lead poller"""
        logger.info("Starting OrderBot...")

        # Start email polling in background
        email_task = asyncio.create_task(self.email_polling_loop())

        # Start Avito Lead Poller if initialized
        avito_task = None
        inbox_task = None
        if self.avito_poller:
            try:
                self.avito_poller.start()
                logger.info("✅ Avito Lead Poller started")
                # Monitor inbox for new Avito leads
                inbox_task = asyncio.create_task(self.avito_inbox_monitor())
                logger.info("✅ Avito inbox monitor started")
            except Exception as e:
                logger.error(f"Failed to start Avito poller: {e}")

        # Start Telegram bot
        try:
            await self.telegram_bot.start()
        except KeyboardInterrupt:
            logger.info("Bot interrupted")
        finally:
            self.running = False

            # Stop Avito poller
            if self.avito_poller:
                try:
                    self.avito_poller.stop()
                    logger.info("Avito Lead Poller stopped")
                except Exception as e:
                    logger.error(f"Error stopping Avito poller: {e}")

            # Cancel tasks
            email_task.cancel()
            if inbox_task:
                inbox_task.cancel()

            await self.telegram_bot.stop()

async def main():
    logger.info("="*60)
    logger.info("🤖 UNITPLAST BOT STARTED - REAL_BOT_FIX_20260618")
    logger.info("="*60)

    bot = OrderBot()

    # Check for --check-once flag
    if "--check-once" in sys.argv:
        logger.info("Running in check-once mode...")
        bot.connect_email()
        await bot.process_emails()
        bot.disconnect_email()
        logger.info("Email check complete. Exiting.")
        return

    # Normal mode - continuous polling
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
