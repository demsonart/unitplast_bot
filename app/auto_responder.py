import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AutoResponder:
    """
    Automatic responses for when managers are offline
    """

    def __init__(self):
        self.templates = self._load_templates()
        self.enabled = True

    def _load_templates(self) -> Dict[str, str]:
        """Load auto-response templates"""
        return {
            "instagram_default": """Здравствуйте! 👋

Спасибо за обращение в UNITPLAST.

Мы получили ваше сообщение и ответим в ближайшее время.

Пока вы можете отправить:
✔ Размеры деталей
✔ Материал
✔ Количество
✔ Чертеж или фото

Это ускорит подготовку коммерческого предложения.

С уважением,
UNITPLAST
📞 +7 (495) 924-50-96
🌐 www.unitplast.ru""",

            "instagram_sketch": """Спасибо за чертеж! 🔧

Мы анализируем вашу заявку.

Коммерческое предложение будет готово:
📅 Сегодня до 18:00

Ждите уведомления!""",

            "instagram_waiting": """Спасибо за ваше сообщение!

Менеджер свяжется с вами в течение часа.

В это время вы можете уточнить:
• Точные размеры
• Количество штук
• Материал и цвет
• Дату, когда нужно товар

Это поможет нам быстрее подготовить предложение.""",

            "instagram_offline": """Добрый день! 👋

Наш офис работает:
🕒 Пн-Пт: 09:00 - 18:00
🕒 Сб-Вс: выходной

Мы ответим вам в ближайший рабочий день.

Спасибо за ваше обращение!""",

            "email_default": """Здравствуйте!

Спасибо за вашу заявку.

Мы получили информацию и в ближайшее время свяжемся с вами для уточнения деталей.

Стандартный срок подготовки КП: 1-2 рабочих дня.

С уважением,
UNITPLAST
id@unitplast.ru
+7 (495) 924-50-96""",

            "website_default": """Спасибо за обращение на наш сайт!

Мы получили вашу заявку и свяжемся с вами в ближайшее время.

Наши менеджеры готовы помочь вам с выбором материала и расчетом стоимости.

UNITPLAST - производство пластиковых изделий"""
        }

    def is_enabled(self) -> bool:
        """Check if auto-responder is enabled"""
        return self.enabled

    def toggle(self):
        """Toggle auto-responder on/off"""
        self.enabled = not self.enabled
        logger.info(f"Auto-responder {'enabled' if self.enabled else 'disabled'}")

    def get_response(self, channel: str, trigger: str = "default") -> str:
        """
        Get appropriate auto-response
        channel: instagram, email, telegram, website
        trigger: default, sketch, waiting, offline, etc.
        """
        key = f"{channel}_{trigger}"
        response = self.templates.get(key)

        if not response:
            # Fallback to default
            key = f"{channel}_default"
            response = self.templates.get(key)

        if not response:
            # Ultimate fallback
            response = self.templates.get("instagram_default")

        return response

    def send_auto_response(self, channel: str, recipient_id: str,
                          trigger: str = "default") -> bool:
        """
        Send auto-response to user
        This is a placeholder - actual sending happens in channel-specific code
        """
        if not self.enabled:
            logger.info("Auto-responder disabled")
            return False

        try:
            response = self.get_response(channel, trigger)

            # Log the auto-response
            logger.info(f"Auto-response sent to {recipient_id} via {channel}")

            # In production, this would call the actual channel API
            # e.g., instagram_api.send_message(recipient_id, response)
            #       email_sender.send(recipient_id, response)

            return True

        except Exception as e:
            logger.error(f"Error sending auto-response: {e}")
            return False

    def customize_template(self, channel: str, trigger: str, text: str):
        """Customize auto-response template"""
        key = f"{channel}_{trigger}"
        self.templates[key] = text
        logger.info(f"Template {key} updated")

    def format_quick_replies(self) -> Dict[str, str]:
        """Get quick reply buttons"""
        return {
            "Спасибо за обращение 😊": self.templates.get("instagram_default", ""),
            "Отправьте чертеж": "Пожалуйста, отправьте чертеж или технические требования.",
            "КП будет готово": self.templates.get("instagram_sketch", ""),
            "Минимальный заказ": "Минимальный заказ составляет 100 шт. Для меньшего объема возможны исключения.",
            "Срок изготовления": "Стандартный срок изготовления: 7-14 рабочих дней в зависимости от сложности.",
            "Свяжу менеджера": "Наш менеджер свяжется с вами в течение часа.",
        }

    def suggest_response(self, message_text: str) -> Optional[str]:
        """
        Suggest appropriate response based on message content
        """
        keywords = {
            "чертеж": "Спасибо за чертеж. Анализируем вашу заявку.",
            "сколько стоит": "Стоимость рассчитывается индивидуально. Отправьте чертеж.",
            "срок": "Стандартный срок: 7-14 дней. Срочные заказы возможны.",
            "материал": "Какой материал вас интересует? ABS, PP, PET, PVC?",
            "размер": "Какие размеры вам нужны?",
            "количество": "Какое количество штук?",
            "доставка": "Доставляем по России курьером или самовывоз.",
            "спасибо": "Спасибо за интерес к UNITPLAST!",
        }

        message_lower = message_text.lower()
        for keyword, suggestion in keywords.items():
            if keyword in message_lower:
                return suggestion

        return None
