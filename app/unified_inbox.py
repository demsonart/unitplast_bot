import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class Channel(Enum):
    """Available communication channels"""
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"
    EMAIL = "email"
    WEBSITE = "website"
    WHATSAPP = "whatsapp"
    FACEBOOK = "facebook"

class LeadStatus(Enum):
    """Lead statuses"""
    NEW = "🟢 Новый"
    IN_PROGRESS = "🟡 В работе"
    WAITING_CLIENT = "🟠 Ждем ответа клиента"
    QUOTE_SENT = "🔵 КП отправлено"
    NEGOTIATION = "🟣 Согласование"
    CLOSED = "⚫ Закрыта"
    LOST = "⚫ Потеряна"

class UnifiedInbox:
    """
    Unified inbox for all communication channels
    Combines Telegram, Instagram, Email, Website, WhatsApp, Facebook
    """

    def __init__(self, db=None):
        self.db = db
        self.leads = {}  # In-memory storage (use DB in production)

    def create_lead(self, channel: Channel, data: Dict) -> str:
        """
        Create new lead from any channel
        Returns: lead_id
        """
        try:
            lead_id = self._generate_lead_id()

            lead = {
                "id": lead_id,
                "channel": channel.value,
                "status": LeadStatus.NEW.value,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "data": data,
                "messages": [],
                "attachments": [],
                "assigned_to": None,
                "tags": [],
                "notes": []
            }

            # Store in database
            if self.db:
                # self.db.add_lead(lead)
                pass

            self.leads[lead_id] = lead
            logger.info(f"Lead {lead_id} created from {channel.value}")

            return lead_id

        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            return None

    def add_message(self, lead_id: str, message: Dict, channel: Channel):
        """Add message to lead"""
        try:
            if lead_id in self.leads:
                self.leads[lead_id]["messages"].append({
                    "channel": channel.value,
                    "timestamp": datetime.now().isoformat(),
                    "text": message.get("text"),
                    "type": message.get("type", "text"),
                    "sender": message.get("sender"),
                    "data": message
                })
                self.leads[lead_id]["updated_at"] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Error adding message: {e}")

    def update_status(self, lead_id: str, status: LeadStatus):
        """Update lead status"""
        if lead_id in self.leads:
            self.leads[lead_id]["status"] = status.value
            self.leads[lead_id]["updated_at"] = datetime.now().isoformat()
            logger.info(f"Lead {lead_id} status updated to {status.value}")

    def assign_manager(self, lead_id: str, manager_name: str):
        """Assign lead to manager"""
        if lead_id in self.leads:
            self.leads[lead_id]["assigned_to"] = manager_name
            self.leads[lead_id]["updated_at"] = datetime.now().isoformat()
            logger.info(f"Lead {lead_id} assigned to {manager_name}")

    def add_tags(self, lead_id: str, tags: List[str]):
        """Add tags to lead"""
        if lead_id in self.leads:
            self.leads[lead_id]["tags"].extend(tags)
            self.leads[lead_id]["tags"] = list(set(self.leads[lead_id]["tags"]))

    def add_note(self, lead_id: str, note: str, author: str):
        """Add internal note"""
        if lead_id in self.leads:
            self.leads[lead_id]["notes"].append({
                "timestamp": datetime.now().isoformat(),
                "author": author,
                "text": note
            })

    def get_lead(self, lead_id: str) -> Optional[Dict]:
        """Get full lead information"""
        return self.leads.get(lead_id)

    def get_leads_by_status(self, status: LeadStatus) -> List[Dict]:
        """Get all leads with specific status"""
        return [lead for lead in self.leads.values()
                if lead["status"] == status.value]

    def get_leads_by_channel(self, channel: Channel) -> List[Dict]:
        """Get all leads from specific channel"""
        return [lead for lead in self.leads.values()
                if lead["channel"] == channel.value]

    def get_leads_by_manager(self, manager_name: str) -> List[Dict]:
        """Get all leads assigned to specific manager"""
        return [lead for lead in self.leads.values()
                if lead["assigned_to"] == manager_name]

    def get_unassigned_leads(self) -> List[Dict]:
        """Get all unassigned leads"""
        return [lead for lead in self.leads.values()
                if lead["assigned_to"] is None]

    def get_pending_leads(self) -> List[Dict]:
        """Get leads waiting for manager response (>2 days)"""
        from datetime import timedelta
        now = datetime.now()
        pending = []

        for lead in self.leads.values():
            if lead["status"] in ["🟢 Новый", "🟡 В работе"]:
                updated = datetime.fromisoformat(lead["updated_at"])
                if now - updated > timedelta(days=2):
                    pending.append(lead)

        return pending

    def get_statistics(self) -> Dict:
        """Get inbox statistics"""
        stats = {
            "total_leads": len(self.leads),
            "by_channel": {},
            "by_status": {},
            "by_manager": {},
            "unassigned": 0
        }

        for lead in self.leads.values():
            # By channel
            channel = lead["channel"]
            stats["by_channel"][channel] = stats["by_channel"].get(channel, 0) + 1

            # By status
            status = lead["status"]
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # By manager
            manager = lead["assigned_to"]
            if manager:
                stats["by_manager"][manager] = stats["by_manager"].get(manager, 0) + 1
            else:
                stats["unassigned"] += 1

        return stats

    def format_inbox_dashboard(self) -> str:
        """Format dashboard for telegram"""
        stats = self.get_statistics()

        dashboard = "📊 <b>Единый Inbox</b>\n\n"

        # By channel
        dashboard += "<b>По каналам:</b>\n"
        for channel, count in stats["by_channel"].items():
            emoji = self._get_channel_emoji(channel)
            dashboard += f"{emoji} {channel}: {count}\n"

        dashboard += f"\n<b>Всего лидов:</b> {stats['total_leads']}\n"

        # By status
        dashboard += "\n<b>По статусам:</b>\n"
        for status, count in stats["by_status"].items():
            dashboard += f"{status}: {count}\n"

        # Unassigned
        dashboard += f"\n<b>Не назначено:</b> {stats['unassigned']}\n"

        return dashboard

    def _generate_lead_id(self) -> str:
        """Generate unique lead ID"""
        return f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    @staticmethod
    def _get_channel_emoji(channel: str) -> str:
        """Get emoji for channel"""
        emojis = {
            "telegram": "💬",
            "instagram": "📷",
            "email": "📧",
            "website": "🌐",
            "whatsapp": "💚",
            "facebook": "👥"
        }
        return emojis.get(channel, "📨")
