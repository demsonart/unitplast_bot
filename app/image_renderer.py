import logging
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageRenderer:
    """
    PNG-based image generator for all documents.
    Replaces PDF generation with PNG for better compatibility.
    """

    # Brand colors
    COLORS = {
        "primary": "#0057C8",      # Dark blue
        "accent": "#FF3333",       # Red
        "text": "#1A1A1A",         # Dark text
        "light_text": "#666666",   # Gray text
        "bg": "#FFFFFF",           # White background
        "border": "#CCCCCC"        # Light border
    }

    # Standard dimensions
    WIDTH = 1080
    PADDING = 40
    LINE_HEIGHT = 1.4

    def __init__(self, font_path: Optional[str] = None):
        """Initialize renderer with system fonts"""
        self.font_path = font_path or self._find_system_font()
        self.fonts = self._load_fonts()
        self._img = None
        self._draw = None

    def _find_system_font(self) -> Optional[str]:
        """Find system font supporting Cyrillic"""
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
            "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS fallback
        ]

        for path in font_paths:
            if Path(path).exists():
                logger.info(f"Found system font: {path}")
                return path

        logger.warning("No system font found, using default")
        return None

    def _load_fonts(self) -> dict:
        """Load fonts at different sizes"""
        fonts = {}

        sizes = {
            "title": 48,
            "heading": 36,
            "subheading": 28,
            "body": 20,
            "small": 16,
            "tiny": 12
        }

        for name, size in sizes.items():
            try:
                if self.font_path:
                    fonts[name] = ImageFont.truetype(self.font_path, size)
                else:
                    fonts[name] = ImageFont.load_default()
            except Exception as e:
                logger.warning(f"Failed to load font {name}: {e}")
                fonts[name] = ImageFont.load_default()

        return fonts

    def create_blank(self, height: int = 1000) -> None:
        """Create blank image"""
        self._img = Image.new(
            "RGB",
            (self.WIDTH, height),
            self._hex_to_rgb(self.COLORS["bg"])
        )
        self._draw = ImageDraw.Draw(self._img)

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def draw_header(self, logo_text: str = "UNITPLAST", y: int = 20) -> int:
        """Draw header with logo"""
        padding = self.PADDING

        # Logo/company name
        self._draw.text(
            (padding, y),
            logo_text,
            fill=self._hex_to_rgb(self.COLORS["primary"]),
            font=self.fonts["title"]
        )

        return y + 70

    def draw_title(self, text: str, y: int, color: str = "primary") -> int:
        """Draw title text"""
        padding = self.PADDING

        self._draw.text(
            (padding, y),
            text,
            fill=self._hex_to_rgb(self.COLORS[color]),
            font=self.fonts["heading"]
        )

        return y + 50

    def draw_section(self, title: str, y: int) -> int:
        """Draw section header"""
        padding = self.PADDING

        # Section title with accent line
        self._draw.text(
            (padding, y),
            title,
            fill=self._hex_to_rgb(self.COLORS["primary"]),
            font=self.fonts["subheading"]
        )

        # Accent line
        self._draw.line(
            [(padding, y + 40), (self.WIDTH - padding, y + 40)],
            fill=self._hex_to_rgb(self.COLORS["accent"]),
            width=3
        )

        return y + 60

    def draw_text(self, text: str, y: int, bold: bool = False,
                  size: str = "body", color: str = "text") -> int:
        """Draw regular text with wrapping"""
        padding = self.PADDING
        max_width = self.WIDTH - (padding * 2)
        font = self.fonts[size]

        # Simple word wrapping
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            bbox = self._draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]

            if line_width > max_width and current_line:
                lines.append(current_line)
                current_line = word + " "
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        # Draw lines
        for line in lines:
            self._draw.text(
                (padding, y),
                line.strip(),
                fill=self._hex_to_rgb(self.COLORS[color]),
                font=font
            )
            y += int(font.size * self.LINE_HEIGHT)

        return y + 10

    def draw_key_value(self, key: str, value: str, y: int) -> int:
        """Draw key-value pair"""
        padding = self.PADDING

        # Key (bold)
        self._draw.text(
            (padding, y),
            key,
            fill=self._hex_to_rgb(self.COLORS["primary"]),
            font=self.fonts["body"]
        )

        # Value
        self._draw.text(
            (padding + 250, y),
            value,
            fill=self._hex_to_rgb(self.COLORS["text"]),
            font=self.fonts["body"]
        )

        return y + 35

    def draw_table(self, headers: List[str], rows: List[List[str]], y: int) -> int:
        """Draw table with headers and rows"""
        padding = self.PADDING
        col_width = (self.WIDTH - padding * 2) // len(headers)
        cell_padding = 10

        # Draw header
        header_y = y
        for i, header in enumerate(headers):
            x = padding + (i * col_width)
            self._draw.text(
                (x + cell_padding, header_y),
                header,
                fill=self._hex_to_rgb(self.COLORS["accent"]),
                font=self.fonts["small"]
            )

        y = header_y + 35

        # Draw border line
        self._draw.line(
            [(padding, y), (self.WIDTH - padding, y)],
            fill=self._hex_to_rgb(self.COLORS["border"]),
            width=2
        )

        y += 10

        # Draw rows
        for row in rows:
            for i, cell in enumerate(row):
                x = padding + (i * col_width)
                self._draw.text(
                    (x + cell_padding, y),
                    cell,
                    fill=self._hex_to_rgb(self.COLORS["light_text"]),
                    font=self.fonts["small"]
                )

            y += 30

        return y + 10

    def draw_divider(self, y: int, style: str = "solid") -> int:
        """Draw divider line"""
        padding = self.PADDING

        if style == "solid":
            self._draw.line(
                [(padding, y), (self.WIDTH - padding, y)],
                fill=self._hex_to_rgb(self.COLORS["border"]),
                width=1
            )
        elif style == "accent":
            self._draw.line(
                [(padding, y), (self.WIDTH - padding, y)],
                fill=self._hex_to_rgb(self.COLORS["accent"]),
                width=2
            )

        return y + 20

    def draw_footer(self, text: str, y: int) -> int:
        """Draw footer"""
        padding = self.PADDING

        self._draw.text(
            (padding, y),
            text,
            fill=self._hex_to_rgb(self.COLORS["light_text"]),
            font=self.fonts["tiny"]
        )

        return y + 20

    def draw_qr_placeholder(self, y: int, size: int = 150) -> int:
        """Draw placeholder for QR code"""
        padding = self.PADDING
        x = self.WIDTH - padding - size

        # Draw border
        self._draw.rectangle(
            [(x, y), (x + size, y + size)],
            outline=self._hex_to_rgb(self.COLORS["border"]),
            width=2
        )

        # Draw QR text
        self._draw.text(
            (x + 10, y + 10),
            "QR Code",
            fill=self._hex_to_rgb(self.COLORS["light_text"]),
            font=self.fonts["tiny"]
        )

        return y + size + 10

    def draw_badge(self, text: str, y: int, bg_color: str = "accent") -> int:
        """Draw colored badge"""
        padding = self.PADDING
        badge_height = 40
        badge_width = 200

        # Background
        self._draw.rectangle(
            [(padding, y), (padding + badge_width, y + badge_height)],
            fill=self._hex_to_rgb(self.COLORS[bg_color])
        )

        # Text
        self._draw.text(
            (padding + 10, y + 8),
            text,
            fill=self._hex_to_rgb(self.COLORS["bg"]),
            font=self.fonts["small"]
        )

        return y + badge_height + 10

    def save(self, filepath: str) -> bool:
        """Save image to file"""
        try:
            if self._img:
                self._img.save(filepath, "PNG", quality=95)
                logger.info(f"Image saved: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False

    def get_image(self) -> Optional[Image.Image]:
        """Get PIL Image object"""
        return self._img

    def resize_image(self, height: int) -> None:
        """Resize image to final height"""
        if self._img:
            # Crop to actual content if image is larger
            if self._img.height > height:
                self._img = self._img.crop((0, 0, self.WIDTH, height))
