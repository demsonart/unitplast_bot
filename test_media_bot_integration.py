"""
Test suite for media_bot_integration module.
"""

import unittest
import json
import tempfile
from pathlib import Path
from app.media_bot_integration import MediaBotIntegration


class TestMediaBotIntegration(unittest.TestCase):
    """Test cases for MediaBotIntegration class."""

    def setUp(self):
        """Set up test fixtures."""
        self.integration = MediaBotIntegration()

    def test_get_approval_keyboard(self):
        """Test approval keyboard generation."""
        keyboard = self.integration.get_approval_keyboard("test_draft_001")

        # Check that keyboard has buttons
        self.assertIsNotNone(keyboard)
        self.assertGreater(len(keyboard.inline_keyboard), 0)

        # Check first row (Approve/Reject)
        first_row = keyboard.inline_keyboard[0]
        self.assertEqual(len(first_row), 2)
        self.assertIn("Approve", first_row[0].text)
        self.assertIn("Reject", first_row[1].text)

    def test_format_draft_preview(self):
        """Test draft preview formatting."""
        draft = {
            "id": "draft_test_001",
            "channel": "@UnitgroupAI",
            "status": "draft",
            "source": {
                "source_name": "TestSource",
                "published_date": "2024-07-13",
            },
            "content": {
                "full_text": "Test content for preview",
            },
            "metadata": {
                "brand_module": "UNITPLAST",
                "relevance_score": 0.85,
            },
            "approval_workflow": {
                "status": "waiting_approval",
                "dry_run_mode": True,
                "require_approval": True,
            },
            "validation": {
                "brand_names_check": {"passed": True},
                "safety_check": {"passed": True},
                "format_check": {"has_hook": True},
            },
        }

        preview = self.integration.format_draft_preview(draft)

        # Check that preview includes key info
        self.assertIn("draft_test_001", preview)
        self.assertIn("TestSource", preview)
        self.assertIn("UNITPLAST", preview)
        self.assertIn("0.85", preview)
        self.assertIn("waiting_approval", preview)
        self.assertIn("✅ ON", preview)  # Dry-run mode

    def test_approve_draft(self):
        """Test draft approval."""
        # Create a test draft
        draft = {
            "id": "draft_approve_test",
            "channel": "@UnitgroupAI",
            "approval_workflow": {
                "status": "waiting_approval",
                "approved_by": None,
                "approved_at": None,
            },
        }

        # Save draft
        self.integration.save_draft(draft)

        # Approve it
        result = self.integration.approve_draft("draft_approve_test", admin_id=12345)
        self.assertTrue(result)

        # Verify it was updated
        updated_draft = self.integration.get_draft("draft_approve_test")
        self.assertEqual(updated_draft["approval_workflow"]["status"], "approved")
        self.assertEqual(updated_draft["approval_workflow"]["approved_by"], 12345)
        self.assertIsNotNone(updated_draft["approval_workflow"]["approved_at"])

    def test_reject_draft(self):
        """Test draft rejection."""
        # Create a test draft
        draft = {
            "id": "draft_reject_test",
            "channel": "@UnitgroupAI",
            "approval_workflow": {
                "status": "waiting_approval",
                "rejected_by": None,
                "rejected_at": None,
            },
        }

        # Save draft
        self.integration.save_draft(draft)

        # Reject it
        result = self.integration.reject_draft(
            "draft_reject_test",
            admin_id=12345,
            reason="Needs editing"
        )
        self.assertTrue(result)

        # Verify it was updated
        updated_draft = self.integration.get_draft("draft_reject_test")
        self.assertEqual(updated_draft["approval_workflow"]["status"], "rejected")
        self.assertEqual(updated_draft["approval_workflow"]["rejected_by"], 12345)
        self.assertIsNotNone(updated_draft["approval_workflow"]["rejected_at"])
        self.assertEqual(updated_draft["approval_workflow"]["rejection_reason"], "Needs editing")

    def test_get_drafts_summary(self):
        """Test drafts summary generation."""
        # Create test drafts with different statuses
        drafts = [
            {
                "id": "draft_summary_01",
                "source": {"source_name": "Source1"},
                "approval_workflow": {"status": "waiting_approval"},
            },
            {
                "id": "draft_summary_02",
                "source": {"source_name": "Source2"},
                "approval_workflow": {"status": "approved"},
            },
        ]

        for draft in drafts:
            self.integration.save_draft(draft)

        summary = self.integration.get_drafts_summary()

        # Check summary content
        self.assertIn("Total Drafts", summary)
        self.assertIn("WAITING_APPROVAL", summary)
        self.assertIn("APPROVED", summary)

    def test_list_drafts(self):
        """Test listing drafts."""
        # Create test drafts
        drafts = [
            {
                "id": "draft_list_01",
                "source": {"source_name": "Source1"},
                "approval_workflow": {"status": "waiting_approval"},
            },
            {
                "id": "draft_list_02",
                "source": {"source_name": "Source2"},
                "approval_workflow": {"status": "approved"},
            },
        ]

        for draft in drafts:
            self.integration.save_draft(draft)

        # List drafts
        listed = self.integration.list_drafts()

        # Should have at least our test drafts
        self.assertGreaterEqual(len(listed), 2)

        # Check that our drafts are in the list
        ids = [d["id"] for d in listed]
        self.assertIn("draft_list_01", ids)
        self.assertIn("draft_list_02", ids)

    def test_get_draft(self):
        """Test getting specific draft."""
        # Create test draft
        draft = {
            "id": "draft_get_test",
            "source": {"source_name": "TestSource"},
            "approval_workflow": {"status": "waiting_approval"},
        }

        self.integration.save_draft(draft)

        # Get it back
        retrieved = self.integration.get_draft("draft_get_test")

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["id"], "draft_get_test")
        self.assertEqual(retrieved["source"]["source_name"], "TestSource")

    def test_get_nonexistent_draft(self):
        """Test getting non-existent draft."""
        result = self.integration.get_draft("nonexistent_draft_12345")
        self.assertIsNone(result)

    def test_draft_preview_message(self):
        """Test getting formatted draft preview message."""
        # Create test draft
        draft = {
            "id": "draft_message_test",
            "channel": "@UnitgroupAI",
            "status": "draft",
            "source": {
                "source_name": "TestSource",
                "published_date": "2024-07-13",
            },
            "content": {
                "full_text": "Test content",
            },
            "metadata": {
                "brand_module": "UNITFURNITURE",
                "relevance_score": 0.90,
            },
            "approval_workflow": {
                "status": "waiting_approval",
                "dry_run_mode": True,
                "require_approval": True,
            },
            "validation": {
                "brand_names_check": {"passed": True},
                "safety_check": {"passed": True},
                "format_check": {"has_hook": True},
            },
        }

        self.integration.save_draft(draft)

        # Get preview
        preview = self.integration.get_draft_preview_message("draft_message_test")

        self.assertIsNotNone(preview)
        self.assertIn("draft_message_test", preview)
        self.assertIn("TestSource", preview)
        self.assertIn("UNITFURNITURE", preview)


class TestMediaBotSafeguards(unittest.TestCase):
    """Test safety guarantees in media bot integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.integration = MediaBotIntegration()

    def test_draft_has_safety_settings(self):
        """Test that drafts enforce safety settings."""
        draft = {
            "id": "draft_safety_test",
            "approval_workflow": {
                "dry_run_mode": True,
                "require_approval": True,
                "allow_auto_publish": False,
                "status": "waiting_approval",
            },
        }

        self.integration.save_draft(draft)
        retrieved = self.integration.get_draft("draft_safety_test")

        # Safety guarantees
        self.assertTrue(retrieved["approval_workflow"]["dry_run_mode"])
        self.assertTrue(retrieved["approval_workflow"]["require_approval"])
        self.assertFalse(retrieved["approval_workflow"]["allow_auto_publish"])
        self.assertEqual(retrieved["approval_workflow"]["status"], "waiting_approval")

    def test_approval_workflow_tracking(self):
        """Test that approval workflow is properly tracked."""
        draft = {
            "id": "draft_workflow_test",
            "approval_workflow": {
                "status": "waiting_approval",
                "approved_by": None,
                "approved_at": None,
                "rejected_by": None,
                "rejected_at": None,
            },
        }

        self.integration.save_draft(draft)

        # Approve it
        self.integration.approve_draft("draft_workflow_test", admin_id=111)
        approved = self.integration.get_draft("draft_workflow_test")

        self.assertEqual(approved["approval_workflow"]["status"], "approved")
        self.assertEqual(approved["approval_workflow"]["approved_by"], 111)
        self.assertIsNotNone(approved["approval_workflow"]["approved_at"])


if __name__ == "__main__":
    unittest.main()
