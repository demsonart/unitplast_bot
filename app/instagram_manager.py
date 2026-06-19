import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class InstagramManager:
    """
    Instagram Direct Messages Integration
    Receives messages via Meta Webhooks and creates unified leads
    """

    def __init__(self, verify_token: str = None, app_secret: str = None):
        """
        Initialize Instagram Manager
        verify_token: Token from Meta webhook verification
        app_secret: App secret from Meta
        """
        self.verify_token = verify_token
        self.app_secret = app_secret
        self.webhook_verified = False

    def verify_webhook(self, token: str) -> bool:
        """Verify webhook token from Meta"""
        if token == self.verify_token:
            self.webhook_verified = True
            logger.info("Instagram webhook verified")
            return True
        return False

    def process_webhook(self, data: Dict) -> Dict:
        """
        Process incoming webhook from Meta
        Returns: lead_data or None
        """
        try:
            # Meta sends data in specific format
            if "entry" not in data:
                return None

            entries = data.get("entry", [])
            for entry in entries:
                messaging = entry.get("messaging", [])
                for message in messaging:
                    # Extract message data
                    sender = message.get("sender", {})
                    recipient = message.get("recipient", {})
                    timestamp = message.get("timestamp")
                    msg = message.get("message", {})

                    # Check for text message
                    if "text" in msg:
                        return self._create_lead_from_message(
                            instagram_id=sender.get("id"),
                            username=sender.get("username"),
                            message_text=msg.get("text"),
                            timestamp=timestamp,
                            full_data=message
                        )

                    # Check for attachments (photos, videos, files)
                    elif "attachments" in msg:
                        return self._create_lead_from_attachments(
                            instagram_id=sender.get("id"),
                            username=sender.get("username"),
                            attachments=msg.get("attachments"),
                            timestamp=timestamp,
                            full_data=message
                        )

        except Exception as e:
            logger.error(f"Error processing Instagram webhook: {e}")

        return None

    def _create_lead_from_message(self, instagram_id: str, username: str,
                                  message_text: str, timestamp: int,
                                  full_data: Dict) -> Dict:
        """Create lead from text message"""
        return {
            "source": "instagram",
            "instagram_id": instagram_id,
            "username": username,
            "message": message_text,
            "timestamp": datetime.fromtimestamp(timestamp / 1000).isoformat(),
            "full_data": full_data,
            "attachment_type": None,
            "attachment_url": None
        }

    def _create_lead_from_attachments(self, instagram_id: str, username: str,
                                      attachments: List[Dict], timestamp: int,
                                      full_data: Dict) -> Dict:
        """Create lead from message with attachments"""
        attachment_types = []
        attachment_urls = []

        for attachment in attachments:
            att_type = attachment.get("type")  # image, video, file, etc.
            att_payload = attachment.get("payload", {})
            att_url = att_payload.get("url")

            attachment_types.append(att_type)
            if att_url:
                attachment_urls.append(att_url)

        return {
            "source": "instagram",
            "instagram_id": instagram_id,
            "username": username,
            "message": "Отправлены файлы/изображения",
            "timestamp": datetime.fromtimestamp(timestamp / 1000).isoformat(),
            "full_data": full_data,
            "attachment_types": attachment_types,
            "attachment_urls": attachment_urls,
            "attachments": attachments
        }

    def format_notification(self, lead_data: Dict) -> str:
        """Format notification for Telegram managers group"""
        return f"""
📩 <b>Новый лид из Instagram</b>

👤 <b>Аккаунт:</b> @{lead_data.get('username', 'Unknown')}
🔑 <b>Instagram ID:</b> {lead_data.get('instagram_id', 'N/A')}

💬 <b>Сообщение:</b>
{lead_data.get('message', 'N/A')}

📎 <b>Вложения:</b> {', '.join(lead_data.get('attachment_types', ['Нет']))}

📅 <b>Время:</b> {lead_data.get('timestamp', 'N/A')}

<b>Источник:</b> Instagram Direct

<b>Кнопки:</b>
[✅ Взять] [📄 КП] [📞 Позвонить] [✏️ Ответить]
"""

    def get_quick_replies(self) -> List[Dict]:
        """Get predefined quick replies for Instagram"""
        return [
            {
                "id": 1,
                "text": "Спасибо за обращение 😊",
                "template": "Спасибо за обращение в UNITPLAST. Мы получили ваше сообщение и ответим в ближайшее время."
            },
            {
                "id": 2,
                "text": "Отправьте чертеж",
                "template": "Пожалуйста, отправьте чертеж или технические характеристики изделия."
            },
            {
                "id": 3,
                "text": "КП будет готово",
                "template": "КП будет готово сегодня до 18:00."
            },
            {
                "id": 4,
                "text": "Минимальный заказ",
                "template": "Минимальный заказ составляет 100 штук. Для меньшего объема возможны исключения."
            },
            {
                "id": 5,
                "text": "Срок изготовления",
                "template": "Стандартный срок изготовления 7-14 рабочих дней в зависимости от сложности."
            },
            {
                "id": 6,
                "text": "Связь с менеджером",
                "template": "Мой менеджер свяжется с вами сегодня."
            }
        ]

    def get_auto_tags(self, message_text: str) -> List[str]:
        """Auto-tag message based on keywords"""
        tags = []

        keywords_mapping = {
            "abs": ["ABS"],
            "пп": ["PP"],
            "pet": ["PET"],
            "pvc": ["PVC"],
            "пс": ["PS"],
            "поликарбонат": ["Поликарбонат"],
            "акрил": ["Акрил"],
            "пластик": ["Пластик"],
            "лист": ["Лист"],
            "труба": ["Труба"],
            "стержень": ["Стержень"],
            "формовка": ["Формовка"],
            "вакуум": ["Вакуум-формовка"],
            "производство": ["Производство"],
            "чертеж": ["Чертеж"],
            "образец": ["Образец"],
            "срочно": ["Срочно"],
            "доставка": ["Доставка"],
            "цена": ["Цена"],
            "прайс": ["Прайс"]
        }

        message_lower = message_text.lower()

        for keyword, tag_list in keywords_mapping.items():
            if keyword in message_lower:
                tags.extend(tag_list)

        return list(set(tags))  # Remove duplicates
