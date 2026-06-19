import logging
import re

logger = logging.getLogger(__name__)


class LeadScorer:
    """Intelligent lead scoring based on email content"""

    SCORE_WEIGHTS = {
        "material_found": 20,
        "quantity_found": 15,
        "company_found": 15,
        "phone_found": 15,
        "email_found": 15,
        "urgent_keywords": 20,
        "repeat_customer": 30,
        "high_quantity": 10,
    }

    URGENT_KEYWORDS = [
        "срочно",
        "срочный",
        "быстро",
        "ASAP",
        "быстрее",
        "спешу",
        "срок",
        "завтра",
        "сегодня",
        "критично",
    ]

    def __init__(self):
        self.max_score = 100

    def score_lead(self, order_data: dict, is_repeat_customer: bool = False) -> dict:
        """
        Calculate lead score and priority level

        Args:
            order_data: Dictionary with extracted order information
            is_repeat_customer: Whether customer has previous orders

        Returns:
            Dictionary with score, stars, and priority
        """
        score = 0

        # Material found
        if order_data.get("material"):
            score += self.SCORE_WEIGHTS["material_found"]

        # Quantity found
        if order_data.get("quantity"):
            score += self.SCORE_WEIGHTS["quantity_found"]
            # Bonus for high quantity
            try:
                qty = int(re.sub(r"\D", "", str(order_data.get("quantity"))))
                if qty >= 500:
                    score += self.SCORE_WEIGHTS["high_quantity"]
            except (ValueError, TypeError):
                pass

        # Company found
        if order_data.get("client_name") and order_data.get("client_name") != "Не указано":
            score += self.SCORE_WEIGHTS["company_found"]

        # Phone found
        if order_data.get("client_phone"):
            score += self.SCORE_WEIGHTS["phone_found"]

        # Email found
        if order_data.get("client_email"):
            score += self.SCORE_WEIGHTS["email_found"]

        # Urgent keywords in text
        combined_text = (
            f"{order_data.get('products', '')} {order_data.get('comments', '')}"
        ).lower()
        if any(kw in combined_text for kw in self.URGENT_KEYWORDS):
            score += self.SCORE_WEIGHTS["urgent_keywords"]

        # Repeat customer bonus
        if is_repeat_customer:
            score += self.SCORE_WEIGHTS["repeat_customer"]

        # Normalize score
        score = min(score, self.max_score)

        return {
            "score": score,
            "stars": self._score_to_stars(score),
            "priority": self._score_to_priority(score),
            "percentage": int((score / self.max_score) * 100),
        }

    def _score_to_stars(self, score: int) -> str:
        """Convert score to star rating"""
        if score >= 90:
            return "★★★★★"
        elif score >= 75:
            return "★★★★☆"
        elif score >= 60:
            return "★★★☆☆"
        elif score >= 45:
            return "★★☆☆☆"
        elif score >= 30:
            return "★☆☆☆☆"
        else:
            return "☆☆☆☆☆"

    def _score_to_priority(self, score: int) -> dict:
        """Convert score to priority level"""
        if score >= 90:
            return {"emoji": "🔴", "level": "CRITICAL", "color": "red"}
        elif score >= 75:
            return {"emoji": "🟠", "level": "HIGH", "color": "orange"}
        elif score >= 60:
            return {"emoji": "🟡", "level": "MEDIUM", "color": "yellow"}
        elif score >= 45:
            return {"emoji": "🔵", "level": "LOW", "color": "blue"}
        else:
            return {"emoji": "⚫", "level": "MINIMAL", "color": "gray"}

    def classify_order_type(self, subject: str, body: str) -> dict:
        """Classify order type and suggest routing"""
        combined = f"{subject} {body}".lower()

        if any(
            kw in combined
            for kw in [
                "производство",
                "ТПА",
                "пресс",
                "форма",
                "литье",
                "параметры",
            ]
        ):
            return {
                "type": "🏭 PRODUCTION",
                "emoji": "🏭",
                "route_to": ["PRODUCTION", "TECHNOLOGISTS"],
            }
        elif any(
            kw in combined
            for kw in [
                "документ",
                "счёт",
                "счет",
                "договор",
                "реквизит",
                "счёт-фактура",
            ]
        ):
            return {
                "type": "🟣 DOCUMENTS",
                "emoji": "🟣",
                "route_to": ["ACCOUNTING", "MANAGEMENT"],
            }
        elif any(
            kw in combined
            for kw in ["цена", "стоимость", "расчёт", "расчет", "КП", "коммерческое"]
        ):
            return {
                "type": "🟡 PRICE_REQUEST",
                "emoji": "🟡",
                "route_to": ["SALES", "MANAGEMENT"],
            }
        else:
            return {
                "type": "🟢 ORDER",
                "emoji": "🟢",
                "route_to": ["SALES", "MANAGEMENT"],
            }
