import logging
from typing import Dict, Optional
from datetime import datetime
from app.image_renderer import ImageRenderer

logger = logging.getLogger(__name__)

class ImageTemplates:
    """Pre-built templates for common documents"""

    def __init__(self):
        self.renderer = None

    def _init_renderer(self):
        """Initialize renderer"""
        if not self.renderer:
            self.renderer = ImageRenderer()

    def generate_commercial_offer(self, data: Dict) -> Optional[str]:
        """Generate commercial offer as PNG"""
        try:
            self._init_renderer()
            renderer = ImageRenderer()

            # Start with large canvas for dynamic height
            renderer.create_blank(height=2000)

            y = 20

            # Header
            y = renderer.draw_header("UNITPLAST", y)
            y = renderer.draw_title("КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ", y)

            # Offer number and date
            y = renderer.draw_text(
                f"№ КП: {data.get('kp_number', 'КП-0001')}  |  "
                f"Дата: {data.get('date', datetime.now().strftime('%d.%m.%Y'))}",
                y, size="small", color="light_text"
            )

            y = renderer.draw_divider(y)

            # Client info section
            y = renderer.draw_section("КЛИЕНТ", y)
            y = renderer.draw_key_value("Компания:", data.get("company", ""), y)
            y = renderer.draw_key_value("Контакт:", data.get("contact_name", ""), y)
            y = renderer.draw_key_value("Email:", data.get("email", ""), y)
            y = renderer.draw_key_value("Телефон:", data.get("phone", ""), y)

            y = renderer.draw_divider(y)

            # Order info
            y = renderer.draw_section("ЗАКАЗ", y)

            # Order details table
            headers = ["Параметр", "Значение"]
            rows = [
                ["Материал", data.get("material", "")],
                ["Количество", f"{data.get('quantity', 0)} шт"],
                ["Размер", data.get("size", "")],
                ["Цвет", data.get("color", "")],
                ["Срок изготовления", data.get("lead_time", "7-14 дней")],
            ]

            y = renderer.draw_table(headers, rows, y)

            y = renderer.draw_divider(y)

            # Description
            y = renderer.draw_section("ОПИСАНИЕ", y)
            y = renderer.draw_text(
                data.get("description", "Производство пластиковых изделий по ТУ заказчика"),
                y, size="body"
            )

            y = renderer.draw_divider(y)

            # Cost section
            y = renderer.draw_section("СТОИМОСТЬ", y)

            cost = data.get("cost", "По запросу")
            y = renderer.draw_badge(f"Итого: {cost} ₽", y, bg_color="accent")

            y = renderer.draw_divider(y)

            # Terms
            y = renderer.draw_section("УСЛОВИЯ", y)
            y = renderer.draw_text("✓ НДС: включен в стоимость", y, size="small")
            y = renderer.draw_text("✓ Доставка: по согласованию", y, size="small")
            y = renderer.draw_text("✓ Оплата: 50% авансом, 50% по факту", y, size="small")

            y = renderer.draw_divider(y)

            # Footer
            y = renderer.draw_section("КОНТАКТНАЯ ИНФОРМАЦИЯ", y)
            y = renderer.draw_text("UNITPLAST", y, size="body", color="primary")
            y = renderer.draw_text("+7 (495) 924-50-96", y, size="body")
            y = renderer.draw_text("id@unitplast.ru", y, size="body")
            y = renderer.draw_text("www.unitplast.ru", y, size="small", color="light_text")

            y += 20

            # Resize to actual height
            renderer.resize_image(y)

            # Save
            filepath = f"./output/kp_{data.get('kp_number', 'unknown')}.png"
            if renderer.save(filepath):
                return filepath

        except Exception as e:
            logger.error(f"Error generating commercial offer: {e}")

        return None

    def generate_product_card(self, product: Dict) -> Optional[str]:
        """Generate product catalog card as PNG"""
        try:
            renderer = ImageRenderer()
            renderer.create_blank(height=1500)

            y = 20

            # Header
            y = renderer.draw_header("UNITPLAST", y)
            y = renderer.draw_title(product.get("name", "Материал"), y)

            y = renderer.draw_divider(y)

            # Product info
            y = renderer.draw_section("ОПИСАНИЕ", y)
            y = renderer.draw_text(
                product.get("description", ""),
                y, size="body"
            )

            y = renderer.draw_divider(y)

            # Characteristics
            y = renderer.draw_section("ХАРАКТЕРИСТИКИ", y)

            chars = product.get("characteristics", {})
            for key, value in chars.items():
                y = renderer.draw_key_value(key + ":", str(value), y)

            y = renderer.draw_divider(y)

            # Advantages
            y = renderer.draw_section("ПРЕИМУЩЕСТВА", y)
            advantages = product.get("advantages", [])
            for advantage in advantages:
                y = renderer.draw_text(f"✓ {advantage}", y, size="small")

            y = renderer.draw_divider(y)

            # CTA
            y = renderer.draw_badge("Заказать", y, bg_color="accent")

            y = renderer.draw_divider(y)

            # Footer
            y = renderer.draw_text(
                "+7 (495) 924-50-96 | id@unitplast.ru",
                y, size="small", color="light_text"
            )

            renderer.resize_image(y + 40)

            filepath = f"./output/product_{product.get('id', 'unknown')}.png"
            if renderer.save(filepath):
                return filepath

        except Exception as e:
            logger.error(f"Error generating product card: {e}")

        return None

    def generate_price_list(self, materials: list) -> Optional[str]:
        """Generate price list as PNG"""
        try:
            renderer = ImageRenderer()
            renderer.create_blank(height=2500)

            y = 20

            # Header
            y = renderer.draw_header("UNITPLAST", y)
            y = renderer.draw_title("ПРАЙС-ЛИСТ", y)
            y = renderer.draw_text(
                f"Актуально на: {datetime.now().strftime('%d.%m.%Y')}",
                y, size="small", color="light_text"
            )

            y = renderer.draw_divider(y)

            # Materials table
            headers = ["Материал", "Минимум", "Цена за шт"]
            rows = []

            for mat in materials:
                rows.append([
                    mat.get("name", ""),
                    f"{mat.get('min_order', 100)} шт",
                    f"{mat.get('price', 'По запросу')} ₽"
                ])

            y = renderer.draw_table(headers, rows, y)

            y = renderer.draw_divider(y)

            # Notes
            y = renderer.draw_section("ПРИМЕЧАНИЯ", y)
            y = renderer.draw_text(
                "• Цены указаны за штуку при минимальном заказе",
                y, size="small"
            )
            y = renderer.draw_text(
                "• При больших объемах предоставляются скидки",
                y, size="small"
            )
            y = renderer.draw_text(
                "• Доставка рассчитывается отдельно",
                y, size="small"
            )

            y = renderer.draw_divider(y)

            # Footer
            y = renderer.draw_text(
                "Свяжитесь с нами для уточнения стоимости и сроков",
                y, size="body", color="primary"
            )
            y = renderer.draw_text(
                "+7 (495) 924-50-96 | id@unitplast.ru",
                y, size="small"
            )

            renderer.resize_image(y + 40)

            filepath = "./output/price_list.png"
            if renderer.save(filepath):
                return filepath

        except Exception as e:
            logger.error(f"Error generating price list: {e}")

        return None

    def generate_order_confirmation(self, order: Dict) -> Optional[str]:
        """Generate order confirmation as PNG"""
        try:
            renderer = ImageRenderer()
            renderer.create_blank(height=1800)

            y = 20

            # Header
            y = renderer.draw_header("UNITPLAST", y)

            # Confirmation badge
            y = renderer.draw_badge("✓ ЗАКАЗ ПРИНЯТ", y, bg_color="accent")

            y = renderer.draw_title(f"Номер заказа: {order.get('order_id', '')}", y)

            y = renderer.draw_divider(y)

            # Order details
            y = renderer.draw_section("ДЕТАЛИ ЗАКАЗА", y)

            y = renderer.draw_key_value("Дата заказа:", order.get("date", ""), y)
            y = renderer.draw_key_value("Статус:", "✓ Принят в производство", y)
            y = renderer.draw_key_value("Ожидаемая дата выполнения:", order.get("expected_date", ""), y)

            y = renderer.draw_divider(y)

            # What's next
            y = renderer.draw_section("ЧТО ДАЛЬШЕ?", y)
            y = renderer.draw_text("1. Мы начали производство вашего заказа", y, size="small")
            y = renderer.draw_text("2. На указанный вами телефон придет СМС с обновлениями", y, size="small")
            y = renderer.draw_text("3. Готовую продукцию отправим курьером или по самовывозу", y, size="small")

            y = renderer.draw_divider(y)

            # Contact
            y = renderer.draw_section("ЕСТЬ ВОПРОСЫ?", y)
            y = renderer.draw_text(
                "Менеджер всегда готов помочь:",
                y, size="body"
            )
            y = renderer.draw_text("+7 (495) 924-50-96", y, size="body", color="primary")
            y = renderer.draw_text("Пн-Пт: 09:00-18:00", y, size="small", color="light_text")

            renderer.resize_image(y + 40)

            filepath = f"./output/order_confirmation_{order.get('order_id', 'unknown')}.png"
            if renderer.save(filepath):
                return filepath

        except Exception as e:
            logger.error(f"Error generating order confirmation: {e}")

        return None

    def generate_invoice(self, invoice: Dict) -> Optional[str]:
        """Generate invoice as PNG"""
        try:
            renderer = ImageRenderer()
            renderer.create_blank(height=2000)

            y = 20

            # Header
            y = renderer.draw_header("UNITPLAST", y)
            y = renderer.draw_title("СЧЕТ-ФАКТУРА", y)

            y = renderer.draw_divider(y)

            # Invoice details
            y = renderer.draw_key_value("№ Счета:", invoice.get("invoice_number", ""), y)
            y = renderer.draw_key_value("Дата:", invoice.get("date", ""), y)

            y = renderer.draw_divider(y)

            # Bill to
            y = renderer.draw_section("СЧЕТ ДЛЯ", y)
            y = renderer.draw_key_value("Компания:", invoice.get("company", ""), y)
            y = renderer.draw_key_value("ИНН:", invoice.get("inn", ""), y)
            y = renderer.draw_key_value("Адрес:", invoice.get("address", ""), y)

            y = renderer.draw_divider(y)

            # Items
            y = renderer.draw_section("ПОЗИЦИИ", y)

            headers = ["Описание", "Кол-во", "Цена", "Сумма"]
            rows = []

            items = invoice.get("items", [])
            total = 0

            for item in items:
                qty = item.get("quantity", 0)
                price = float(item.get("price", 0))
                amount = qty * price
                total += amount

                rows.append([
                    item.get("description", ""),
                    str(qty),
                    f"{price:.0f} ₽",
                    f"{amount:.0f} ₽"
                ])

            y = renderer.draw_table(headers, rows, y)

            y = renderer.draw_divider(y)

            # Total
            y = renderer.draw_badge(f"ИТОГО: {total:.0f} ₽", y, bg_color="accent")

            y = renderer.draw_divider(y)

            # Footer
            y = renderer.draw_text("Счет действителен 5 рабочих дней", y, size="small", color="light_text")

            renderer.resize_image(y + 40)

            filepath = f"./output/invoice_{invoice.get('invoice_number', 'unknown')}.png"
            if renderer.save(filepath):
                return filepath

        except Exception as e:
            logger.error(f"Error generating invoice: {e}")

        return None
