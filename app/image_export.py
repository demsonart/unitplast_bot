import logging
from typing import Dict, Optional
from pathlib import Path
from io import BytesIO
from PIL import Image
from app.image_templates import ImageTemplates

logger = logging.getLogger(__name__)

class ImageExporter:
    """
    Main interface for generating and exporting PNG documents.
    Replaces all PDF functionality with high-quality PNG images.
    """

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.templates = ImageTemplates()

    def generate_commercial_offer(self, data: Dict) -> Optional[str]:
        """
        Generate commercial offer as PNG image.

        Args:
            data: Dictionary with:
                - kp_number: Offer number (e.g., "КП-20260617-001")
                - date: Date string
                - company: Customer company name
                - contact_name: Customer contact name
                - email: Customer email
                - phone: Customer phone
                - material: Material type
                - quantity: Quantity in pieces
                - size: Dimensions
                - color: Color
                - lead_time: Lead time (e.g., "7-14 дней")
                - cost: Total cost (e.g., "50000")
                - description: Order description

        Returns:
            Path to generated PNG file or None if failed
        """
        try:
            filepath = self.templates.generate_commercial_offer(data)
            if filepath:
                logger.info(f"Commercial offer generated: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error generating commercial offer: {e}")
            return None

    def generate_product_catalog(self, products: list) -> Optional[str]:
        """
        Generate product catalog with multiple pages as PNG.

        Args:
            products: List of product dictionaries

        Returns:
            Path to generated PNG file
        """
        try:
            if not products:
                return None

            # Generate individual product cards
            filepaths = []
            for product in products:
                filepath = self.templates.generate_product_card(product)
                if filepath:
                    filepaths.append(filepath)

            if filepaths:
                logger.info(f"Generated {len(filepaths)} product cards")
                return filepaths[0]  # Return first for main reference

        except Exception as e:
            logger.error(f"Error generating product catalog: {e}")

        return None

    def generate_price_list(self, materials: list) -> Optional[str]:
        """
        Generate price list as PNG.

        Args:
            materials: List of material dictionaries with:
                - name: Material name
                - min_order: Minimum order quantity
                - price: Price per unit

        Returns:
            Path to generated PNG file
        """
        try:
            filepath = self.templates.generate_price_list(materials)
            if filepath:
                logger.info(f"Price list generated: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error generating price list: {e}")
            return None

    def generate_order_confirmation(self, order: Dict) -> Optional[str]:
        """
        Generate order confirmation as PNG.

        Args:
            order: Dictionary with:
                - order_id: Order ID
                - date: Order date
                - expected_date: Expected completion date

        Returns:
            Path to generated PNG file
        """
        try:
            filepath = self.templates.generate_order_confirmation(order)
            if filepath:
                logger.info(f"Order confirmation generated: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error generating order confirmation: {e}")
            return None

    def generate_invoice(self, invoice: Dict) -> Optional[str]:
        """
        Generate invoice as PNG.

        Args:
            invoice: Dictionary with:
                - invoice_number: Invoice number
                - date: Invoice date
                - company: Customer company
                - inn: Customer INN
                - address: Customer address
                - items: List of items with description, quantity, price

        Returns:
            Path to generated PNG file
        """
        try:
            filepath = self.templates.generate_invoice(invoice)
            if filepath:
                logger.info(f"Invoice generated: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error generating invoice: {e}")
            return None

    async def generate_and_send_to_telegram(self, bot, chat_id: int,
                                            doc_type: str, data: Dict) -> bool:
        """
        Generate document and send as PNG image to Telegram.

        Args:
            bot: Telegram bot instance
            chat_id: Chat ID to send to
            doc_type: Document type (commercial_offer, order_confirmation, etc.)
            data: Document data

        Returns:
            True if sent successfully
        """
        try:
            # Generate image
            filepath = None

            if doc_type == "commercial_offer":
                filepath = self.generate_commercial_offer(data)
            elif doc_type == "order_confirmation":
                filepath = self.generate_order_confirmation(data)
            elif doc_type == "invoice":
                filepath = self.generate_invoice(data)
            elif doc_type == "price_list":
                filepath = self.generate_price_list(data)

            if not filepath:
                logger.error(f"Failed to generate {doc_type}")
                return False

            # Send to Telegram
            with open(filepath, "rb") as photo:
                await bot.send_photo(
                    chat_id,
                    photo,
                    caption=f"📄 {self._get_doc_caption(doc_type)}"
                )

            logger.info(f"Document sent to Telegram: {doc_type}")
            return True

        except Exception as e:
            logger.error(f"Error sending document to Telegram: {e}")
            return False

    def get_image_as_bytes(self, filepath: str) -> Optional[bytes]:
        """Read image file as bytes"""
        try:
            with open(filepath, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading image: {e}")
            return None

    def delete_image(self, filepath: str) -> bool:
        """Delete image file"""
        try:
            Path(filepath).unlink()
            return True
        except Exception as e:
            logger.error(f"Error deleting image: {e}")
            return False

    @staticmethod
    def _get_doc_caption(doc_type: str) -> str:
        """Get caption for document type"""
        captions = {
            "commercial_offer": "📄 Коммерческое предложение",
            "order_confirmation": "✅ Подтверждение заказа",
            "invoice": "🧾 Счет-фактура",
            "price_list": "💰 Прайс-лист",
            "product_card": "📦 Карточка товара"
        }
        return captions.get(doc_type, "📄 Документ")
