"""
Feed Content Normalizer

Converts any feedparser RSS/Atom content format to clean string.
Handles dict, list, CDATA, HTML, entities - outputs only plain text.

This module prevents raw Python dict structures like:
  {'type': 'text/html', 'language': None, 'value': '...'}
from being published to Telegram.
"""

import re
import html
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def normalize_feed_content(value: Any, max_length: int = 5000) -> str:
    """
    Convert any feedparser content format to clean string.

    Handles:
    - strings, dicts, lists, bytes, None
    - HTML tags and entities
    - CDATA sections
    - Nested structures
    - Unicode and encoding

    Args:
        value: Raw feedparser content (any format)
        max_length: Maximum characters to return

    Returns:
        Clean string without technical markers

    Raises:
        ValueError: If value is completely unusable
    """
    try:
        # Step 1: Handle None and empty values
        if value is None or value == "":
            return ""

        # Step 2: If it's already a string, just clean it
        if isinstance(value, str):
            return _clean_string(value, max_length)

        # Step 3: Handle bytes
        if isinstance(value, bytes):
            try:
                value = value.decode("utf-8")
            except (UnicodeDecodeError, AttributeError):
                return ""
            return _clean_string(value, max_length)

        # Step 4: Handle dict (common feedparser format)
        if isinstance(value, dict):
            # Try common keys in order
            for key in ["value", "content", "summary", "text", "body", "data"]:
                if key in value and value[key]:
                    extracted = value[key]
                    # Recursively normalize the extracted value
                    return normalize_feed_content(extracted, max_length)
            # If no recognized key, return empty
            logger.debug(f"Dict has no recognized content keys: {list(value.keys())}")
            return ""

        # Step 5: Handle list (multiple content parts)
        if isinstance(value, (list, tuple)):
            parts = []
            for item in value:
                normalized = normalize_feed_content(item, max_length=max_length // len(value) if value else max_length)
                if normalized:
                    parts.append(normalized)
            # Join with space, clean up
            result = " ".join(parts)
            return _clean_string(result, max_length)

        # Step 6: Unknown type - try to convert to string
        logger.warning(f"Unknown content type: {type(value)}")
        return _clean_string(str(value), max_length)

    except Exception as e:
        logger.error(f"Error normalizing content: {e}", exc_info=True)
        return ""


def _clean_string(text: str, max_length: int = 5000) -> str:
    """
    Clean a string of HTML, entities, CDATA, and extra whitespace.

    Args:
        text: String to clean
        max_length: Max characters to return

    Returns:
        Cleaned string
    """
    if not text:
        return ""

    # Remove CDATA markers if present
    text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text, flags=re.DOTALL)

    # Remove script and style tags completely (with content)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Decode HTML entities (&amp; → &, etc)
    text = html.unescape(text)

    # Normalize whitespace
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\n+', '\n\n', text)
    # Remove leading/trailing whitespace
    text = text.strip()

    # Limit length
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0]  # Cut at last word boundary
        text = text.rstrip('.,;:!?')  # Remove trailing punctuation
        text = text + "..."

    return text


def validate_content_is_string(content: Any, source_name: str = "unknown") -> bool:
    """
    Validate that content is a string, not a dict/list/object.

    Args:
        content: Content to validate
        source_name: Name of source (for logging)

    Returns:
        True if valid string, False otherwise
    """
    if isinstance(content, str):
        return True

    logger.error(
        f"Content from {source_name} is not a string: type={type(content).__name__}. "
        f"Content: {str(content)[:100]}"
    )
    return False


def extract_text_from_structure(value: Any) -> Optional[str]:
    """
    Extract plain text from complex feedparser structure.

    This is a simpler alternative to normalize_feed_content() that just
    extracts without aggressive cleaning.

    Args:
        value: Raw feedparser value

    Returns:
        Extracted text or None
    """
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    if isinstance(value, list) and value:
        return " ".join(str(v) for v in value)
    return None
