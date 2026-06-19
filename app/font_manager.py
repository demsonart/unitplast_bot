import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class FontManager:
    """Manages font selection for PDF generation with Cyrillic support"""

    # Possible system font paths (macOS, Linux, Windows)
    SYSTEM_FONT_PATHS = [
        # macOS
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/DejaVuSans.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # Windows
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\DejaVuSans.ttf",
    ]

    PROJECT_FONTS_DIR = Path(__file__).parent.parent / "assets" / "fonts"

    @staticmethod
    def find_font() -> str:
        """Find available font with Cyrillic support"""
        # First check project fonts directory
        if FontManager.PROJECT_FONTS_DIR.exists():
            for font_file in FontManager.PROJECT_FONTS_DIR.glob("*.ttf"):
                logger.info(f"Found project font: {font_file}")
                return str(font_file)

        # Then check system fonts
        for font_path in FontManager.SYSTEM_FONT_PATHS:
            if os.path.exists(font_path):
                logger.info(f"Using system font: {font_path}")
                return font_path

        # Fallback to reportlab built-in fonts (limited Cyrillic support)
        logger.warning("No Cyrillic font found, using reportlab defaults (may display as squares)")
        return None

    @staticmethod
    def get_font_name() -> str:
        """Get font name for reportlab"""
        font_path = FontManager.find_font()
        if font_path:
            return font_path
        return "Helvetica"  # Fallback

    @staticmethod
    def register_fonts():
        """Register fonts for reportlab"""
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        font_path = FontManager.find_font()
        if font_path and font_path.endswith(".ttf"):
            try:
                font_name = "CustomFont"
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                logger.info(f"Registered font: {font_name}")
                return font_name
            except Exception as e:
                logger.error(f"Error registering font: {e}")
                return "Helvetica"

        return "Helvetica"
