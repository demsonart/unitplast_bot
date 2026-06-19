import json
import logging
from .config import ENABLE_AI, ANTHROPIC_API_KEY
from .rule_based_parser import RuleBasedOrderParser

logger = logging.getLogger(__name__)

class OrderParser:
    def __init__(self):
        self.use_ai = ENABLE_AI and ANTHROPIC_API_KEY
        if self.use_ai:
            try:
                from anthropic import Anthropic
                self.client = Anthropic()
            except ImportError:
                logger.warning("Anthropic not installed, falling back to rule-based parser")
                self.use_ai = False
        else:
            logger.info("Using rule-based email parser (AI disabled)")

        self.rule_parser = RuleBasedOrderParser()

    def is_order(self, email_subject: str, email_body: str) -> bool:
        """Determines if email is an order using Claude or rule-based parser"""
        if self.use_ai:
            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=100,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""Определи, является ли это письмо заказом для компании Юнитпласт (производство пластиковых изделий)?

Тема письма: {email_subject}

Содержание письма:
{email_body[:1000]}

Ответь только YES или NO."""
                        }
                    ]
                )
                response = message.content[0].text.strip().upper()
                return "YES" in response
            except Exception as e:
                logger.error(f"Error checking if email is order: {e}")
                return False
        else:
            return self.rule_parser.is_order(email_subject, email_body)

    def extract_order_data(self, email_subject: str, email_body: str, from_email: str = "") -> dict:
        """Extracts order data from email using Claude or rule-based parser"""
        if self.use_ai:
            try:
                message = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""Извлеки данные заказа из письма и верни JSON с следующей структурой:
{{
    "client_name": "ФИ клиента или название компании",
    "client_email": "email клиента",
    "client_phone": "телефон клиента",
    "products": "описание изделий",
    "quantity": "количество",
    "material": "материал (пластик, тип и т.д.)",
    "color": "цвет",
    "sizes": "размеры",
    "delivery_type": "способ доставки",
    "deadline": "срок исполнения",
    "comments": "дополнительные комментарии"
}}

Если какие-то данные отсутствуют, оставь поле пустым.

Тема письма: {email_subject}

Содержание письма:
{email_body}

Верни только JSON, без дополнительного текста."""
                        }
                    ]
                )
                response = message.content[0].text.strip()
                # Clean up JSON if wrapped in markdown code blocks
                if response.startswith('```'):
                    response = response.split('```')[1]
                    if response.startswith('json'):
                        response = response[4:]
                    response = response.strip()
                return json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON from AI response: {e}")
                return {}
            except Exception as e:
                logger.error(f"Error extracting order data: {e}")
                return {}
        else:
            return self.rule_parser.extract_order_data(email_subject, email_body, from_email)

    def generate_order_summary(self, order_data: dict) -> str:
        """Generates a brief summary of order for Telegram"""
        if not self.use_ai:
            # Use rule-based parser summary
            summary_text = self.rule_parser.generate_order_summary(order_data)
            return f"📋 <b>{summary_text}</b>"

        summary = f"""📋 <b>Новый заказ:</b>

👤 Клиент: {order_data.get('client_name', 'Не указано')}
📧 Email: {order_data.get('client_email', 'Не указано')}
☎️ Телефон: {order_data.get('client_phone', 'Не указано')}

📦 Изделия: {order_data.get('products', 'Не указано')}
📊 Количество: {order_data.get('quantity', 'Не указано')}
🎨 Материал: {order_data.get('material', 'Не указано')}
🖌️ Цвет: {order_data.get('color', 'Не указано')}
📐 Размеры: {order_data.get('sizes', 'Не указано')}

🚚 Доставка: {order_data.get('delivery_type', 'Не указано')}
⏰ Срок: {order_data.get('deadline', 'Не указано')}
💬 Комментарий: {order_data.get('comments', 'Нет')}"""
        return summary
