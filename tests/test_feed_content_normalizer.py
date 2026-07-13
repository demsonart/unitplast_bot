"""
Tests for feed_content_normalizer.py

Ensures that raw feedparser structures are properly converted to strings.
This prevents dict/HTML/JSON from being published to Telegram.
"""

import pytest
from app.feed_content_normalizer import normalize_feed_content, validate_content_is_string


class TestNormalizeFeedContent:
    """Test normalize_feed_content() function"""

    def test_string_passthrough(self):
        """Simple string should pass through"""
        text = "This is normal text"
        assert normalize_feed_content(text) == text

    def test_none_returns_empty_string(self):
        """None should return empty string"""
        assert normalize_feed_content(None) == ""

    def test_empty_string_returns_empty(self):
        """Empty string should return empty"""
        assert normalize_feed_content("") == ""

    def test_bytes_decoded_to_string(self):
        """Bytes should be decoded to UTF-8 string"""
        text_bytes = "Hello world".encode("utf-8")
        result = normalize_feed_content(text_bytes)
        assert isinstance(result, str)
        assert result == "Hello world"

    def test_dict_with_value_field(self):
        """Dict with 'value' field should extract text"""
        data = {"type": "text/html", "language": "en", "value": "Content here"}
        result = normalize_feed_content(data)
        assert result == "Content here"
        assert "{" not in result  # No dict structure in output

    def test_dict_with_content_field(self):
        """Dict with 'content' field should extract text"""
        data = {"content": "Important content"}
        result = normalize_feed_content(data)
        assert result == "Important content"

    def test_nested_dict_structure(self):
        """Nested dict should extract deeply"""
        data = {
            "type": "text/html",
            "value": {
                "content": "Deeply nested text"
            }
        }
        result = normalize_feed_content(data)
        assert "Deeply nested text" in result
        assert "{" not in result

    def test_html_tags_removed(self):
        """HTML tags should be stripped"""
        html_text = "<p>Hello <b>world</b></p>"
        result = normalize_feed_content(html_text)
        assert result == "Hello world"
        assert "<" not in result

    def test_html_entities_decoded(self):
        """HTML entities should be decoded"""
        text = "Hello &amp; goodbye &lt;test&gt;"
        result = normalize_feed_content(text)
        assert result == "Hello & goodbye <test>"
        assert "&amp;" not in result

    def test_cdata_removed(self):
        """CDATA markers should be removed"""
        text = "<![CDATA[Content inside CDATA]]>"
        result = normalize_feed_content(text)
        assert result == "Content inside CDATA"
        assert "CDATA" not in result

    def test_script_tag_removed_with_content(self):
        """Script tags and content should be removed"""
        html = "Text <script>alert('xss')</script> more text"
        result = normalize_feed_content(html)
        assert "script" not in result.lower()
        assert "alert" not in result
        assert result == "Text  more text"

    def test_style_tag_removed_with_content(self):
        """Style tags and content should be removed"""
        html = "Text <style>.class { color: red; }</style> more"
        result = normalize_feed_content(html)
        assert "style" not in result.lower()
        assert ".class" not in result

    def test_multiple_spaces_normalized(self):
        """Multiple spaces should become single space"""
        text = "Text   with    multiple     spaces"
        result = normalize_feed_content(text)
        assert result == "Text with multiple spaces"

    def test_multiple_newlines_normalized(self):
        """Multiple newlines should become double newline"""
        text = "Line 1\n\n\n\nLine 2"
        result = normalize_feed_content(text)
        assert result == "Line 1\n\nLine 2"

    def test_list_of_strings_joined(self):
        """List of strings should be joined"""
        items = ["First", "Second", "Third"]
        result = normalize_feed_content(items)
        assert "First" in result
        assert "Second" in result
        assert "Third" in result

    def test_list_of_dicts_processed(self):
        """List of dicts should extract from each"""
        items = [
            {"value": "Part 1"},
            {"value": "Part 2"},
            {"value": "Part 3"}
        ]
        result = normalize_feed_content(items)
        assert "Part 1" in result
        assert "Part 2" in result
        assert "Part 3" in result

    def test_max_length_respected(self):
        """Result should not exceed max_length"""
        long_text = "A" * 10000
        result = normalize_feed_content(long_text, max_length=100)
        assert len(result) <= 105  # Some buffer for "..."
        assert "..." in result

    def test_feedparser_structure_from_rss(self):
        """Real feedparser dict structure should be cleaned"""
        # This is what feedparser actually returns
        data = {
            "type": "text/html",
            "language": "en",
            "base": "https://example.com",
            "value": "<p>Real content from RSS</p>"
        }
        result = normalize_feed_content(data)
        assert isinstance(result, str)
        assert "{" not in result
        assert "<" not in result
        assert "Real content from RSS" in result


class TestValidateContentIsString:
    """Test validate_content_is_string() function"""

    def test_string_is_valid(self):
        """Normal string should be valid"""
        assert validate_content_is_string("Hello world") is True

    def test_dict_is_invalid(self):
        """Dict should be invalid"""
        assert validate_content_is_string({"value": "text"}) is False

    def test_list_is_invalid(self):
        """List should be invalid"""
        assert validate_content_is_string(["text"]) is False

    def test_none_is_invalid(self):
        """None should be invalid"""
        assert validate_content_is_string(None) is False

    def test_feedparser_dict_is_invalid(self):
        """Feedparser dict should be invalid"""
        feedparser_dict = {
            "type": "text/html",
            "value": "Content"
        }
        assert validate_content_is_string(feedparser_dict) is False


@pytest.mark.integration
class TestRealRSSScenarios:
    """Test with real RSS-like structures"""

    def test_cnn_rss_structure(self):
        """Simulate CNN RSS structure"""
        rss_item = {
            "summary": "<p>News article content</p>",
            "summary_detail": {
                "type": "text/html",
                "language": "en",
                "base": "https://cnn.com",
                "value": "<p>News article content</p>"
            }
        }
        # Normalizer should handle summary_detail
        result = normalize_feed_content(rss_item["summary_detail"]["value"])
        assert "News article content" in result
        assert "<" not in result

    def test_podcast_rss_structure(self):
        """Simulate podcast RSS structure"""
        rss_item = {
            "summary": "Show description with HTML",
            "value": "<b>Description</b> with <i>formatting</i>"
        }
        result = normalize_feed_content(rss_item["value"])
        assert "Description" in result
        assert "<" not in result

    def test_unicode_content(self):
        """Non-ASCII Unicode content should be preserved"""
        text = "Тестовый текст на русском с юникодом: 你好 مرحبا"
        result = normalize_feed_content(text)
        assert result == text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
