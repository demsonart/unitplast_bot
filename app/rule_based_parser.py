import re
import logging

logger = logging.getLogger(__name__)

# Keywords that indicate an order
ORDER_KEYWORDS = {
    'заказ', 'заявка', 'рассчитать', 'расчет', 'расчёт',
    'стоимость', 'цена', 'счет', 'счёт', 'выставить счет',
    'коммерческое предложение', 'кп', 'изготовить',
    'производство', 'партия', 'количество', 'штук', 'шт',
    'доставка'
}

# Keywords that indicate spam/unwanted emails
SPAM_KEYWORDS = {
    'рассылка', 'акция', 'скидка', 'реклама', 'newsletter',
    'unsubscribe', 'отписаться', 'уведомление', 'noreply', 'no-reply'
}

class RuleBasedOrderParser:
    """Rule-based email parser without AI dependency"""

    @staticmethod
    def is_order(email_subject: str, email_body: str) -> bool:
        """Determines if email is an order using rules and regex"""
        text = f"{email_subject} {email_body}".lower()

        # Check for spam keywords first
        for keyword in SPAM_KEYWORDS:
            if keyword in text:
                logger.info(f"Email marked as spam: contains '{keyword}'")
                return False

        # Check for order keywords
        found_keywords = [kw for kw in ORDER_KEYWORDS if kw in text]
        is_order = len(found_keywords) > 0

        if is_order:
            logger.info(f"Email marked as order: found keywords {found_keywords}")
        else:
            logger.info("Email not marked as order: no order keywords found")

        return is_order

    @staticmethod
    def extract_phone(text: str) -> str:
        """Extract phone number from text using regex"""
        patterns = [
            r'\+?7[-\s]?\(?9\d{2}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}',  # +7-999-123-45-67
            r'\+7\s*\(\d{3}\)\s*\d{3}[-\s]?\d{2}[-\s]?\d{2}',  # +7(999)123-45-67
            r'8\s*\(?9\d{2}\)?[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}',  # 8-999-123-45-67
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()

        return ""

    @staticmethod
    def extract_quantity(text: str) -> str:
        """Extract quantity from text using regex"""
        patterns = [
            r'количество[:\s]+(\d+\s*(?:штук|шт|шт\.|шт,|метров|м|литров|л)?)',
            r'(\d+)\s*(?:штук|шт\.|шт,|шт)',
            r'кол-во[:\s]+(\d+)',
            r'кол[:\s]*во[:\s]*(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if match.lastindex else match.group(0)

        return ""

    @staticmethod
    def extract_email(text: str) -> str:
        """Extract email address from text"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    @staticmethod
    def extract_client_name(text: str, from_email: str) -> str:
        """Extract client name from text"""
        # Try to find name patterns
        patterns = [
            r'(?:от|от\s|от:)\s*([А-Яа-яЁё\s]+?)(?:\s|,|$)',
            r'(?:клиент|заказчик)[:\s]+([А-Яа-яЁё\s]+?)(?:\s|,|$)',
            r'(?:компания|организация)[:\s]+([А-Яа-яЁё\s]+?)(?:\s|,|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2:
                    return name

        # Try to extract from email
        if '@' in from_email:
            email_name = from_email.split('@')[0].replace('.', ' ').replace('_', ' ')
            if len(email_name) > 2:
                return email_name.title()

        return "Не указано"

    @staticmethod
    def extract_products(text: str) -> str:
        """Extract product info from text"""
        patterns = [
            r'(?:изделия|товар|продукт|услуга)[:\s]+([^,\n]+)',
            r'(?:требуется|нужно|закажу)[:\s]+([^,\n]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Return first meaningful line
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 10 and any(kw in line.lower() for kw in ['пластик', 'контейнер', 'труба', 'ёмкость', 'изделие']):
                return line[:200]

        return ""

    @staticmethod
    def extract_delivery(text: str) -> str:
        """Extract delivery info from text"""
        patterns = [
            r'(?:доставка|доставить|отправка)[:\s]+([^,\n]+)',
            r'(?:курьер|почта|тк|транспортная компания)[:\s]*([^,\n]*)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                delivery = match.group(1).strip() if match.lastindex else "Указана"
                return delivery if delivery else "Доставка указана"

        if 'доставка' in text.lower():
            return "Указана"

        return ""

    @staticmethod
    def extract_deadline(text: str) -> str:
        """Extract deadline from text"""
        patterns = [
            r'(?:срок|до|к дате|выполнить к)[:\s]+([^,\n]+)',
            r'(?:дней|дня|дн\.?)[:\s]*(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                deadline = match.group(1).strip()
                return deadline if deadline else "Указан"

        return ""

    @staticmethod
    def extract_material(text: str) -> str:
        """Extract material info from text"""
        materials = ['пластик', 'пэт', 'hdpe', 'ldpe', 'пп', 'полипропилен', 'полиэтилен', 'пэ', 'abs']
        found = []

        for material in materials:
            if material in text.lower():
                found.append(material.upper())

        return ', '.join(found) if found else ""

    @staticmethod
    def extract_color(text: str) -> str:
        """Extract color info from text"""
        colors = {
            'белый': 'белый', 'чёрный': 'чёрный', 'черный': 'черный',
            'прозрачный': 'прозрачный', 'красный': 'красный',
            'синий': 'синий', 'зелёный': 'зеленый', 'желтый': 'желтый'
        }
        found = []

        for color_key, color_val in colors.items():
            if color_key in text.lower():
                found.append(color_val)

        return ', '.join(found) if found else ""

    @staticmethod
    def extract_sizes(text: str) -> str:
        """Extract size/dimension info from text"""
        patterns = [
            r'(?:размер|размеры|размер\s*[мл]|мм|см|х)[:\s]*([^,\n]+)',
            r'(\d+\s*(?:x|×)\s*\d+\s*(?:x|×)?\s*\d*\s*(?:мм|см|м)?)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return ""

    def extract_order_data(self, email_subject: str, email_body: str, from_email: str) -> dict:
        """Extract all available order data using rules"""
        combined_text = f"{email_subject}\n{email_body}"

        data = {
            "client_name": self.extract_client_name(combined_text, from_email),
            "client_email": self.extract_email(combined_text) or from_email,
            "client_phone": self.extract_phone(combined_text),
            "products": self.extract_products(combined_text),
            "quantity": self.extract_quantity(combined_text),
            "material": self.extract_material(combined_text),
            "color": self.extract_color(combined_text),
            "sizes": self.extract_sizes(combined_text),
            "delivery_type": self.extract_delivery(combined_text),
            "deadline": self.extract_deadline(combined_text),
            "comments": email_body[:500],
        }

        return data

    def generate_order_summary(self, order_data: dict) -> str:
        """Generate HTML summary for Telegram"""
        # Determine status based on data completeness
        required_fields = ['client_phone', 'products', 'quantity']
        has_required = all(order_data.get(field) for field in required_fields)
        status = "✅ Новая заявка" if has_required else "⚠️ Требует проверки"

        summary = f"""{status}

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
💬 Комментарий: {order_data.get('comments', 'Нет')[:100]}..."""

        return summary
