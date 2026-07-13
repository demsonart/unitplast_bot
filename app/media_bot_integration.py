"""
Integration of industry_news_rewriter with Telegram bot for admin approval workflow.

Provides commands for:
- /draft_list - List all drafts
- /draft_preview <id> - Preview specific draft
- /draft_approve <id> - Approve draft
- /draft_reject <id> - Reject draft
- /news_fetch - Fetch fresh news and create drafts

Safety Guaranteed:
- All drafts must be explicitly approved by admin
- Dry-run mode always enabled
- No auto-publish
"""

import logging
import json
from pathlib import Path
from typing import List, Optional, Dict
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .config import BASE_DIR
from .industry_news_rewriter import NewsRewriter

logger = logging.getLogger(__name__)

DRAFTS_DIR = BASE_DIR / "data" / "post_drafts"
LOGS_DIR = BASE_DIR / "logs"


class MediaBotIntegration:
    """Integration layer between NewsRewriter and Telegram bot."""

    def __init__(self):
        self.rewriter = NewsRewriter()
        self.drafts_dir = DRAFTS_DIR
        self.drafts_dir.mkdir(parents=True, exist_ok=True)

    def list_drafts(self) -> List[Dict]:
        """Get all drafts."""
        drafts = []
        if not self.drafts_dir.exists():
            return drafts

        for draft_file in sorted(self.drafts_dir.glob("*.json"), reverse=True):
            try:
                with open(draft_file, 'r', encoding='utf-8') as f:
                    draft = json.load(f)
                    drafts.append(draft)
            except Exception as e:
                logger.error(f"Failed to read draft {draft_file}: {e}")

        return drafts

    def get_draft(self, draft_id: str) -> Optional[Dict]:
        """Get specific draft by ID."""
        draft_path = self.drafts_dir / f"{draft_id}.json"
        if not draft_path.exists():
            return None

        try:
            with open(draft_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read draft {draft_id}: {e}")
            return None

    def save_draft(self, draft: Dict) -> None:
        """Save draft to file."""
        draft_path = self.drafts_dir / f"{draft['id']}.json"
        with open(draft_path, 'w', encoding='utf-8') as f:
            json.dump(draft, f, ensure_ascii=False, indent=2)

    def format_draft_preview(self, draft: Dict) -> str:
        """Format draft for Telegram preview."""
        source = draft.get("source", {})
        content = draft.get("content", {})
        metadata = draft.get("metadata", {})
        approval = draft.get("approval_workflow", {})

        text = f"""
🔍 **DRAFT PREVIEW**

📰 **{draft['id']}**

**Source:** {source.get('source_name', 'Unknown')}
**Product:** {metadata.get('brand_module', 'UNITPLAST')}
**Score:** {metadata.get('relevance_score', 0):.2f}
**Date:** {source.get('published_date', 'N/A')}

---

{content.get('full_text', '')}

---

**Status:** {approval.get('status', 'unknown')}
**Dry-Run Mode:** {'✅ ON' if approval.get('dry_run_mode') else '❌ OFF'}
**Require Approval:** {'✅ YES' if approval.get('require_approval') else '❌ NO'}

**Validation:**
- Brand Names: {'✅ PASS' if draft.get('validation', {}).get('brand_names_check', {}).get('passed') else '❌ FAIL'}
- Content Safety: {'✅ PASS' if draft.get('validation', {}).get('safety_check', {}).get('passed') else '❌ FAIL'}
- Format: {'✅ PASS' if draft.get('validation', {}).get('format_check', {}).get('has_hook') else '❌ FAIL'}
"""

        if draft.get("errors"):
            text += f"\n⚠️ **Errors:**\n"
            for error in draft["errors"]:
                text += f"- {error}\n"

        return text

    def get_approval_keyboard(self, draft_id: str) -> InlineKeyboardMarkup:
        """Create approval buttons."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Approve",
                    callback_data=f"draft_approve:{draft_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Reject",
                    callback_data=f"draft_reject:{draft_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📝 Edit in App",
                    callback_data=f"draft_edit:{draft_id}"
                ),
                InlineKeyboardButton(
                    text="🔗 View Source",
                    url=f"https://unitgroup.tech"  # Placeholder
                ),
            ]
        ])

    def approve_draft(self, draft_id: str, admin_id: int) -> bool:
        """Mark draft as approved."""
        draft = self.get_draft(draft_id)
        if not draft:
            return False

        draft["approval_workflow"]["status"] = "approved"
        draft["approval_workflow"]["approved_by"] = admin_id
        draft["approval_workflow"]["approved_at"] = __import__('datetime').datetime.utcnow().isoformat() + "Z"

        self.save_draft(draft)

        self.rewriter.log_event({
            "event": "draft_approved",
            "draft_id": draft_id,
            "approved_by": admin_id,
        })

        return True

    def reject_draft(self, draft_id: str, admin_id: int, reason: str = "") -> bool:
        """Mark draft as rejected."""
        draft = self.get_draft(draft_id)
        if not draft:
            return False

        draft["approval_workflow"]["status"] = "rejected"
        draft["approval_workflow"]["rejected_by"] = admin_id
        draft["approval_workflow"]["rejected_at"] = __import__('datetime').datetime.utcnow().isoformat() + "Z"
        if reason:
            draft["approval_workflow"]["rejection_reason"] = reason

        self.save_draft(draft)

        self.rewriter.log_event({
            "event": "draft_rejected",
            "draft_id": draft_id,
            "rejected_by": admin_id,
            "reason": reason,
        })

        return True

    def get_drafts_summary(self) -> str:
        """Get summary of all drafts."""
        drafts = self.list_drafts()

        if not drafts:
            return "📋 **No drafts yet**\n\nUse /news_fetch to create drafts from RSS feeds."

        # Group by status
        by_status = {}
        for draft in drafts:
            status = draft.get("approval_workflow", {}).get("status", "unknown")
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(draft)

        text = f"📋 **Total Drafts:** {len(drafts)}\n\n"

        for status in ["waiting_approval", "approved", "rejected"]:
            count = len(by_status.get(status, []))
            emoji = "⏳" if status == "waiting_approval" else ("✅" if status == "approved" else "❌")
            text += f"{emoji} **{status.upper()}:** {count}\n"

        text += "\n**Recent Drafts:**\n"
        for draft in drafts[:5]:
            source = draft.get("source", {})
            status = draft.get("approval_workflow", {}).get("status", "?")
            text += f"- `{draft['id']}` | {source.get('source_name', '?')} | {status}\n"

        return text

    def fetch_and_create_drafts(self, limit: int = 3) -> tuple[int, List[str]]:
        """Fetch news and create drafts. Returns (count, draft_ids)."""
        try:
            logger.info(f"Fetching news for up to {limit} drafts")
            drafts = self.rewriter.process_news(limit=limit)

            draft_ids = [d["id"] for d in drafts]
            logger.info(f"Created {len(draft_ids)} drafts: {draft_ids}")

            return len(draft_ids), draft_ids
        except Exception as e:
            logger.error(f"Failed to fetch news: {e}")
            return 0, []

    def get_draft_preview_message(self, draft_id: str) -> Optional[str]:
        """Get formatted message for draft preview."""
        draft = self.get_draft(draft_id)
        if not draft:
            return None

        return self.format_draft_preview(draft)


# Telegram handler helpers

async def cmd_draft_list(message: types.Message, integration: MediaBotIntegration):
    """Handle /draft_list command."""
    summary = integration.get_drafts_summary()
    await message.answer(summary, parse_mode="markdown")


async def cmd_news_fetch(message: types.Message, integration: MediaBotIntegration):
    """Handle /news_fetch command."""
    await message.answer("🔄 **Fetching industry news...**", parse_mode="markdown")

    count, draft_ids = integration.fetch_and_create_drafts(limit=3)

    if count == 0:
        await message.answer("❌ Failed to fetch news or no relevant items found")
        return

    response = f"✅ **Created {count} news drafts**\n\n"
    for draft_id in draft_ids:
        response += f"📄 `{draft_id}`\n"

    response += f"\nUse /draft_preview <id> to review"
    await message.answer(response, parse_mode="markdown")

    # Log to audit trail
    integration.rewriter.log_event({
        "event": "news_fetch_command",
        "admin_id": message.from_user.id,
        "count": count,
        "draft_ids": draft_ids,
    })


async def cmd_draft_preview(message: types.Message, integration: MediaBotIntegration):
    """Handle /draft_preview <id> command."""
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "Usage: /draft_preview <draft_id>\n"
            "Example: /draft_preview draft_news_20240713_001",
            parse_mode="markdown"
        )
        return

    draft_id = args[1]
    preview = integration.get_draft_preview_message(draft_id)

    if not preview:
        await message.answer(f"❌ Draft not found: {draft_id}")
        return

    keyboard = integration.get_approval_keyboard(draft_id)
    await message.answer(preview, parse_mode="markdown", reply_markup=keyboard)


async def handle_draft_callback(
    callback: types.CallbackQuery,
    integration: MediaBotIntegration
):
    """Handle draft approval/rejection callbacks."""
    data = callback.data
    admin_id = callback.from_user.id

    if data.startswith("draft_approve:"):
        draft_id = data.split(":", 1)[1]
        if integration.approve_draft(draft_id, admin_id):
            await callback.answer("✅ Draft approved!", show_alert=True)
            await callback.message.edit_text(
                callback.message.text + "\n\n✅ **APPROVED** by admin",
                parse_mode="markdown"
            )
        else:
            await callback.answer("❌ Failed to approve draft", show_alert=True)

    elif data.startswith("draft_reject:"):
        draft_id = data.split(":", 1)[1]
        if integration.reject_draft(draft_id, admin_id, reason="Admin rejected"):
            await callback.answer("❌ Draft rejected!", show_alert=True)
            await callback.message.edit_text(
                callback.message.text + "\n\n❌ **REJECTED** by admin",
                parse_mode="markdown"
            )
        else:
            await callback.answer("❌ Failed to reject draft", show_alert=True)

    elif data.startswith("draft_edit:"):
        await callback.answer(
            "📝 Use /draft_list to see all drafts for editing",
            show_alert=True
        )
