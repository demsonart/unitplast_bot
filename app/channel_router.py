import logging
from typing import Dict, Optional, Callable
from app.unified_inbox import Channel, UnifiedInbox, LeadStatus

logger = logging.getLogger(__name__)

class ChannelRouter:
    """
    Routes messages from different channels (Telegram, Instagram, Email, etc.)
    to a unified inbox and manages the lead lifecycle
    """

    def __init__(self, inbox: UnifiedInbox):
        self.inbox = inbox
        self.handlers = {}
        self.reply_handlers = {}

    def register_handler(self, channel: Channel, handler: Callable):
        """Register handler for incoming messages from channel"""
        self.handlers[channel.value] = handler
        logger.info(f"Handler registered for {channel.value}")

    def register_reply_handler(self, channel: Channel, handler: Callable):
        """Register handler for sending replies to channel"""
        self.reply_handlers[channel.value] = handler
        logger.info(f"Reply handler registered for {channel.value}")

    async def route_message(self, channel: Channel, data: Dict) -> Optional[str]:
        """
        Route incoming message to unified inbox
        Returns: lead_id
        """
        try:
            lead_id = self.inbox.create_lead(channel, data)

            if not lead_id:
                logger.error(f"Failed to create lead from {channel.value}")
                return None

            # Call channel-specific handler if registered
            if channel.value in self.handlers:
                handler = self.handlers[channel.value]
                if callable(handler):
                    await handler(lead_id, data)

            return lead_id

        except Exception as e:
            logger.error(f"Error routing message from {channel.value}: {e}")
            return None

    async def route_reply(self, lead_id: str, text: str,
                          from_manager: str = None) -> bool:
        """
        Send reply to customer via original channel
        """
        try:
            lead = self.inbox.get_lead(lead_id)

            if not lead:
                logger.error(f"Lead {lead_id} not found")
                return False

            channel = Channel(lead["channel"])

            # Get handler for this channel
            if channel.value not in self.reply_handlers:
                logger.warning(f"No reply handler for {channel.value}")
                return False

            handler = self.reply_handlers[channel.value]

            # Extract recipient ID based on channel
            recipient_id = self._get_recipient_id(lead)

            if not recipient_id:
                logger.error(f"Cannot extract recipient ID from lead {lead_id}")
                return False

            # Send reply
            success = await handler(recipient_id, text)

            if success:
                # Update lead in inbox
                self.inbox.add_message(lead_id, {
                    "text": text,
                    "type": "reply",
                    "sender": from_manager or "System"
                }, channel)

                # Update status
                self.inbox.update_status(lead_id, LeadStatus.IN_PROGRESS)

            return success

        except Exception as e:
            logger.error(f"Error sending reply to {lead_id}: {e}")
            return False

    def _get_recipient_id(self, lead: Dict) -> Optional[str]:
        """Extract recipient ID from lead based on channel"""
        channel = lead.get("channel")

        if channel == "instagram":
            return lead.get("data", {}).get("instagram_id")
        elif channel == "telegram":
            return lead.get("data", {}).get("user_id")
        elif channel == "email":
            return lead.get("data", {}).get("email")
        elif channel == "whatsapp":
            return lead.get("data", {}).get("phone")
        elif channel == "facebook":
            return lead.get("data", {}).get("fb_id")
        elif channel == "website":
            return lead.get("data", {}).get("email")

        return None

    async def distribute_to_telegram(self, lead_id: str, telegram_handler: Callable) -> bool:
        """
        Distribute lead notification to Telegram group
        telegram_handler: async function that sends Telegram message
        """
        try:
            lead = self.inbox.get_lead(lead_id)

            if not lead:
                return False

            # Format notification based on channel
            channel = Channel(lead["channel"])

            notification = self._format_notification(lead, channel)

            # Send to Telegram
            success = await telegram_handler(notification)

            return success

        except Exception as e:
            logger.error(f"Error distributing to Telegram: {e}")
            return False

    def _format_notification(self, lead: Dict, channel: Channel) -> str:
        """Format notification for Telegram based on channel"""
        data = lead.get("data", {})

        if channel == Channel.INSTAGRAM:
            return f"""📷 <b>Новый лид из Instagram</b>

👤 <b>Аккаунт:</b> @{data.get('username', 'Unknown')}
🔑 <b>Instagram ID:</b> {data.get('instagram_id', 'N/A')}

💬 <b>Сообщение:</b>
{data.get('message', 'N/A')}

📎 <b>Вложения:</b> {', '.join(data.get('attachment_types', ['Нет']))}

📅 <b>Время:</b> {lead.get('created_at', 'N/A')}

<b>Источник:</b> Instagram Direct
<b>Статус:</b> {lead.get('status', 'Новый')}

<b>Кнопки:</b>
[✅ Взять] [📄 КП] [📞 Позвонить] [✏️ Ответить]"""

        elif channel == Channel.EMAIL:
            return f"""📧 <b>Новая заявка из Email</b>

👤 <b>От:</b> {data.get('from', 'Unknown')}
📧 <b>Email:</b> {data.get('email', 'N/A')}

💬 <b>Тема:</b> {data.get('subject', 'N/A')}
💬 <b>Сообщение:</b>
{data.get('message', 'N/A')}

📅 <b>Время:</b> {lead.get('created_at', 'N/A')}

<b>Источник:</b> Email
<b>Статус:</b> {lead.get('status', 'Новый')}"""

        elif channel == Channel.WHATSAPP:
            return f"""💚 <b>Новое сообщение из WhatsApp</b>

👤 <b>Контакт:</b> {data.get('contact_name', 'Unknown')}
📱 <b>Номер:</b> {data.get('phone', 'N/A')}

💬 <b>Сообщение:</b>
{data.get('message', 'N/A')}

📅 <b>Время:</b> {lead.get('created_at', 'N/A')}

<b>Источник:</b> WhatsApp
<b>Статус:</b> {lead.get('status', 'Новый')}"""

        elif channel == Channel.FACEBOOK:
            return f"""👥 <b>Новое сообщение из Facebook Messenger</b>

👤 <b>От:</b> {data.get('name', 'Unknown')}
🔑 <b>ID:</b> {data.get('fb_id', 'N/A')}

💬 <b>Сообщение:</b>
{data.get('message', 'N/A')}

📅 <b>Время:</b> {lead.get('created_at', 'N/A')}

<b>Источник:</b> Facebook Messenger
<b>Статус:</b> {lead.get('status', 'Новый')}"""

        else:
            return f"""📨 <b>Новое обращение</b>

💬 <b>Сообщение:</b>
{data.get('message', 'N/A')}

📅 <b>Время:</b> {lead.get('created_at', 'N/A')}
<b>Источник:</b> {channel.value}
<b>Статус:</b> {lead.get('status', 'Новый')}"""

    def get_dashboard_summary(self) -> str:
        """Get dashboard summary for managers"""
        stats = self.inbox.get_statistics()

        dashboard = "📊 <b>Единый Inbox</b>\n\n"

        # By channel
        dashboard += "<b>По каналам:</b>\n"
        channels_data = [
            ("📷", "instagram"),
            ("💬", "telegram"),
            ("📧", "email"),
            ("🌐", "website"),
            ("💚", "whatsapp"),
            ("👥", "facebook")
        ]

        for emoji, channel_name in channels_data:
            count = stats["by_channel"].get(channel_name, 0)
            if count > 0:
                dashboard += f"{emoji} {channel_name.capitalize()}: {count}\n"

        dashboard += f"\n<b>Всего лидов:</b> {stats['total_leads']}\n"

        # By status
        dashboard += "\n<b>По статусам:</b>\n"
        status_order = [
            LeadStatus.NEW.value,
            LeadStatus.IN_PROGRESS.value,
            LeadStatus.WAITING_CLIENT.value,
            LeadStatus.QUOTE_SENT.value,
            LeadStatus.NEGOTIATION.value,
            LeadStatus.CLOSED.value,
            LeadStatus.LOST.value
        ]

        for status in status_order:
            count = stats["by_status"].get(status, 0)
            if count > 0:
                dashboard += f"{status}: {count}\n"

        # Unassigned
        if stats["unassigned"] > 0:
            dashboard += f"\n⚠️ <b>Не назначено:</b> {stats['unassigned']}\n"

        return dashboard
