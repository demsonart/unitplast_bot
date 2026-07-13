"""
Test suite for industry_news_rewriter module.
"""

import unittest
import json
from pathlib import Path
from app.industry_news_rewriter import (
    NewsRewriter,
    NewsItem,
    ScoredNews,
)


class TestNewsRewriter(unittest.TestCase):
    """Test cases for NewsRewriter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.rewriter = NewsRewriter()

    def test_validate_brand_names_correct(self):
        """Test brand name validation with correct names."""
        text = "UNITPLAST and UNITFURNITURE and UNITMETALL work together in UNITGROUP"
        passed, errors = self.rewriter.validate_brand_names(text)
        self.assertTrue(passed)
        self.assertEqual(len(errors), 0)

    def test_validate_brand_names_wrong(self):
        """Test brand name validation with wrong names."""
        text = "UNIFURNITURE and UNIMETALL are incorrect"
        passed, errors = self.rewriter.validate_brand_names(text)
        self.assertFalse(passed)
        self.assertGreater(len(errors), 0)

    def test_validate_content_safety(self):
        """Test content safety validation."""
        item = NewsItem(
            url="https://example.com",
            title="Real Manufacturing News",
            content="Real industry content with verified facts",
            source_name="IndustryWeek",
            published_date="2024-07-13",
            category="manufacturing",
        )
        passed, errors = self.rewriter.validate_content_safety(item)
        self.assertTrue(passed)

    def test_map_to_products_plastic(self):
        """Test product mapping for plastic news."""
        item = NewsItem(
            url="https://example.com",
            title="Plastic injection molding efficiency",
            content="New techniques for plastic injection molding",
            source_name="PlasticsToday",
            published_date="2024-07-13",
            category="plastics",
        )
        products = self.rewriter.map_to_products(item)
        self.assertIn("UNITPLAST", products)

    def test_map_to_products_furniture(self):
        """Test product mapping for furniture news."""
        item = NewsItem(
            url="https://example.com",
            title="Furniture manufacturing with MDF",
            content="Smart manufacturing for furniture",
            source_name="FurnitureToday",
            published_date="2024-07-13",
            category="furniture",
        )
        products = self.rewriter.map_to_products(item)
        self.assertIn("UNITFURNITURE", products)

    def test_map_to_products_metal(self):
        """Test product mapping for metal news."""
        item = NewsItem(
            url="https://example.com",
            title="Metal fabrication with welding",
            content="Advanced metal welding techniques",
            source_name="TheFabricator",
            published_date="2024-07-13",
            category="metal",
        )
        products = self.rewriter.map_to_products(item)
        self.assertIn("UNITMETALL", products)

    def test_map_to_products_ai(self):
        """Test product mapping for AI news (maps to all)."""
        item = NewsItem(
            url="https://example.com",
            title="AI improves manufacturing efficiency",
            content="Artificial intelligence in production",
            source_name="AIWeekly",
            published_date="2024-07-13",
            category="ai",
        )
        products = self.rewriter.map_to_products(item)
        # Should map to all products
        self.assertIn("UNITPLAST", products)
        self.assertIn("UNITFURNITURE", products)
        self.assertIn("UNITMETALL", products)

    def test_filter_and_score_filters_by_keywords(self):
        """Test filtering filters out non-relevant news."""
        long_content = " ".join(["word"] * 100)  # Ensure min word count
        items = [
            NewsItem(
                url="https://example.com/1",
                title="Manufacturing automation increases efficiency",
                content=f"This article talks about automation and cost reduction in manufacturing. {long_content}",
                source_name="Source1",
                published_date="2024-07-13",
                category="manufacturing",
            ),
            NewsItem(
                url="https://example.com/2",
                title="Weather forecast for next week",
                content="It will be sunny next week with temperatures around 25 degrees " + " ".join(["word"] * 50),
                source_name="Source2",
                published_date="2024-07-13",
                category="weather",
            ),
        ]
        scored = self.rewriter.filter_and_score(items)
        # Should only have the first item (not weather)
        self.assertEqual(len(scored), 1)
        self.assertEqual(scored[0].item.title, "Manufacturing automation increases efficiency")

    def test_rewrite_for_telegram_adds_emoji(self):
        """Test rewrite adds emoji hook."""
        item = NewsItem(
            url="https://example.com",
            title="Automation reduces costs",
            content="AI automation content",
            source_name="IndustryWeek",
            published_date="2024-07-13",
            category="automation",
        )
        products = ["UNITPLAST"]
        rewritten = self.rewriter.rewrite_for_telegram(item, products)

        self.assertIn("emoji_hook", rewritten)
        self.assertIn("headline", rewritten)
        self.assertIn("body", rewritten)
        self.assertIn("cta_text", rewritten)
        # Should have emoji
        self.assertTrue(len(rewritten["emoji_hook"]) > 0)

    def test_rewrite_for_telegram_unitfurniture(self):
        """Test rewrite includes UNITFURNITURE context."""
        item = NewsItem(
            url="https://example.com",
            title="Furniture manufacturing",
            content="Smart manufacturing for furniture",
            source_name="FurnitureToday",
            published_date="2024-07-13",
            category="furniture",
        )
        products = ["UNITFURNITURE"]
        rewritten = self.rewriter.rewrite_for_telegram(item, products)

        self.assertIn("UNITFURNITURE", rewritten["body"])
        self.assertIn("ЛДСП", rewritten["body"])
        self.assertIn("МДФ", rewritten["body"])

    def test_create_draft_has_required_fields(self):
        """Test draft creation includes all required fields."""
        item = NewsItem(
            url="https://example.com",
            title="Test News",
            content="Test content",
            source_name="TestSource",
            published_date="2024-07-13",
            category="test",
        )
        products = ["UNITPLAST"]
        rewritten = self.rewriter.rewrite_for_telegram(item, products)

        draft = self.rewriter.create_draft(
            item,
            products,
            rewritten,
            relevance_score=0.85,
            validation_passed=True,
        )

        # Check required fields
        self.assertIn("id", draft)
        self.assertIn("channel", draft)
        self.assertIn("status", draft)
        self.assertIn("source", draft)
        self.assertIn("content", draft)
        self.assertIn("metadata", draft)
        self.assertIn("validation", draft)
        self.assertIn("approval_workflow", draft)

        # Check values
        self.assertEqual(draft["channel"], "@UnitgroupAI")
        self.assertEqual(draft["status"], "draft")
        self.assertEqual(draft["metadata"]["brand_module"], "UNITPLAST")
        self.assertEqual(draft["approval_workflow"]["dry_run_mode"], True)
        self.assertEqual(draft["approval_workflow"]["require_approval"], True)
        self.assertEqual(draft["approval_workflow"]["allow_auto_publish"], False)

    def test_draft_safety_guarantees(self):
        """Test that draft has all safety guarantees."""
        item = NewsItem(
            url="https://example.com",
            title="Test",
            content="Test",
            source_name="Test",
            published_date="2024-07-13",
            category="test",
        )
        products = ["UNITPLAST"]
        rewritten = self.rewriter.rewrite_for_telegram(item, products)

        draft = self.rewriter.create_draft(
            item,
            products,
            rewritten,
            relevance_score=0.85,
            validation_passed=True,
        )

        # Safety guarantees
        self.assertTrue(draft["approval_workflow"]["dry_run_mode"], "Dry-run mode must be ON")
        self.assertTrue(draft["approval_workflow"]["require_approval"], "Approval must be required")
        self.assertFalse(draft["approval_workflow"]["allow_auto_publish"], "Auto-publish must be disabled")
        self.assertEqual(draft["approval_workflow"]["status"], "waiting_approval", "Draft must be waiting for approval")


class TestNewsItem(unittest.TestCase):
    """Test cases for NewsItem dataclass."""

    def test_news_item_creation(self):
        """Test creating a NewsItem."""
        item = NewsItem(
            url="https://example.com",
            title="Test Title",
            content="Test Content",
            source_name="Test Source",
            published_date="2024-07-13",
            category="test",
        )

        self.assertEqual(item.url, "https://example.com")
        self.assertEqual(item.title, "Test Title")
        self.assertEqual(item.source_name, "Test Source")
        self.assertEqual(item.language, "en")  # default


class TestScoredNews(unittest.TestCase):
    """Test cases for ScoredNews dataclass."""

    def test_scored_news_creation(self):
        """Test creating a ScoredNews."""
        item = NewsItem(
            url="https://example.com",
            title="Test",
            content="Test",
            source_name="Test",
            published_date="2024-07-13",
            category="test",
        )
        scored = ScoredNews(
            item=item,
            relevance_score=0.85,
            matched_keywords=["automation", "efficiency"],
        )

        self.assertEqual(scored.relevance_score, 0.85)
        self.assertEqual(len(scored.matched_keywords), 2)


if __name__ == "__main__":
    unittest.main()
