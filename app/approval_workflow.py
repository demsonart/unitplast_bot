"""
Approval Workflow for @UnitgroupAI News Bot
Handles admin preview, approval decisions, and draft rejection
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ApprovalStage(Enum):
    """Stages in approval workflow"""
    CONTENT_VALIDATION = "content_validation"
    IMAGE_APPROVAL = "image_approval"
    FINAL_REVIEW = "final_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


class ApprovalAction(Enum):
    """Admin approval actions"""
    # Image approval
    APPROVE_SOURCE_IMAGE = "approve_source_image"
    APPROVE_RSS_IMAGE = "approve_rss_image"
    GENERATE_AI_IMAGE = "generate_ai_image"
    USE_NO_IMAGE = "use_no_image"

    # Final approval
    APPROVE = "approve"
    REJECT = "reject"
    EDIT = "edit"
    REQUEST_CHANGES = "request_changes"


@dataclass
class ApprovalDecision:
    """Represents an admin approval decision"""
    draft_id: str
    action: ApprovalAction
    admin_id: int
    admin_username: str
    decision_at: str
    reason: Optional[str] = None
    notes: Optional[str] = None
    changes_requested: Optional[Dict] = None

    def to_dict(self):
        return {
            "draft_id": self.draft_id,
            "action": self.action.value,
            "admin_id": self.admin_id,
            "admin_username": self.admin_username,
            "decision_at": self.decision_at,
            "reason": self.reason,
            "notes": self.notes,
            "changes_requested": self.changes_requested
        }


@dataclass
class PreviewMessage:
    """Admin preview message data"""
    draft_id: str
    message_id: Optional[int] = None
    chat_id: int = 0
    content: str = ""
    image_url: Optional[str] = None
    buttons: List[Dict] = field(default_factory=list)
    created_at: str = ""

    def to_dict(self):
        return asdict(self)


class ApprovalWorkflow:
    """Manages draft approval workflow"""

    def __init__(
        self,
        drafts_dir: str = "data/post_drafts",
        approvals_log: str = "logs/approvals.jsonl"
    ):
        self.drafts_dir = Path(drafts_dir)
        self.approvals_log = Path(approvals_log)
        self.approvals_log.parent.mkdir(parents=True, exist_ok=True)

    # ═════════════════════════════════════════════════════════════════════════════
    # PREVIEW GENERATION
    # ═════════════════════════════════════════════════════════════════════════════

    def generate_image_approval_preview(
        self,
        draft_id: str,
        draft_data: Dict
    ) -> PreviewMessage:
        """
        Generate admin preview for image approval stage

        Args:
            draft_id: Draft ID
            draft_data: Full draft JSON

        Returns:
            PreviewMessage with images and buttons
        """
        logger.info(f"Generating image approval preview for {draft_id}")

        images_section = draft_data.get("images", {})
        primary_image = images_section.get("primary_image", {})

        # Build preview text
        title = draft_data.get("content", {}).get("title", "")
        body_preview = draft_data.get("content", {}).get("body", "")[:200] + "..."

        preview_text = f"""
🖼️ **IMAGE APPROVAL REQUEST**

📰 **Post:** {title}

📝 **Preview:** {body_preview}

🎯 **Image Options:**
1️⃣ Source image from {primary_image.get('source_name', 'source')}
2️⃣ AI-generated image
3️⃣ Skip image (not recommended)

Choose action:
"""

        # Build buttons for image approval
        buttons = self._build_image_approval_buttons(draft_id)

        image_url = primary_image.get("url") or primary_image.get("file_path")

        preview = PreviewMessage(
            draft_id=draft_id,
            content=preview_text,
            image_url=image_url,
            buttons=buttons,
            created_at=datetime.now().isoformat()
        )

        return preview

    def generate_final_approval_preview(
        self,
        draft_id: str,
        draft_data: Dict
    ) -> PreviewMessage:
        """
        Generate admin preview for final approval stage

        Args:
            draft_id: Draft ID
            draft_data: Full draft JSON

        Returns:
            PreviewMessage with full post and buttons
        """
        logger.info(f"Generating final approval preview for {draft_id}")

        content = draft_data.get("content", {})
        images = draft_data.get("images", {})

        # Build full post preview
        title = content.get("title", "")
        subtitle = content.get("subtitle", "")
        body = content.get("body", "")
        cta = content.get("soft_cta", "")
        hashtags = " ".join(content.get("hashtags", []))

        preview_text = f"""
✅ **FINAL APPROVAL REQUEST**

{title}

{subtitle}

{body}

💬 {cta}

{hashtags}

---
✅ Image: {"Approved" if images.get("selected_image") else "Pending"}
✅ Content: Valid
✅ Brand: Compliant

Ready to publish?
"""

        buttons = self._build_final_approval_buttons(draft_id)

        # Use selected image if available
        selected_image = images.get("selected_image", {})
        image_url = selected_image.get("url") or selected_image.get("file_path")

        preview = PreviewMessage(
            draft_id=draft_id,
            content=preview_text,
            image_url=image_url,
            buttons=buttons,
            created_at=datetime.now().isoformat()
        )

        return preview

    # ═════════════════════════════════════════════════════════════════════════════
    # BUTTON GENERATION FOR TELEGRAM UI
    # ═════════════════════════════════════════════════════════════════════════════

    def _build_image_approval_buttons(self, draft_id: str) -> List[Dict]:
        """Build Telegram inline buttons for image approval"""
        return [
            {
                "text": "✅ Use Source Image",
                "callback_data": f"approve_source_{draft_id}",
                "action": "approve_source_image"
            },
            {
                "text": "🤖 Generate AI Image",
                "callback_data": f"generate_ai_{draft_id}",
                "action": "generate_ai_image"
            },
            {
                "text": "⏭️ Skip Image",
                "callback_data": f"skip_image_{draft_id}",
                "action": "use_no_image"
            },
            {
                "text": "❌ Reject Draft",
                "callback_data": f"reject_{draft_id}",
                "action": "reject"
            }
        ]

    def _build_final_approval_buttons(self, draft_id: str) -> List[Dict]:
        """Build Telegram inline buttons for final approval"""
        return [
            {
                "text": "✅ Approve & Publish",
                "callback_data": f"approve_{draft_id}",
                "action": "approve"
            },
            {
                "text": "✏️ Edit",
                "callback_data": f"edit_{draft_id}",
                "action": "edit"
            },
            {
                "text": "🔄 Request Changes",
                "callback_data": f"request_changes_{draft_id}",
                "action": "request_changes"
            },
            {
                "text": "❌ Reject",
                "callback_data": f"reject_{draft_id}",
                "action": "reject"
            }
        ]

    # ═════════════════════════════════════════════════════════════════════════════
    # APPROVAL DECISION HANDLING
    # ═════════════════════════════════════════════════════════════════════════════

    def handle_image_approval_decision(
        self,
        draft_id: str,
        action: str,
        admin_id: int,
        admin_username: str,
        notes: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Handle admin decision on image approval

        Args:
            draft_id: Draft ID
            action: Action from button (approve_source, generate_ai, skip, reject)
            admin_id: Admin Telegram ID
            admin_username: Admin Telegram username
            notes: Optional admin notes

        Returns:
            (success, message)
        """
        logger.info(f"Image approval decision: {action} for {draft_id}")

        draft_path = self.drafts_dir / f"{draft_id}.json"
        if not draft_path.exists():
            return False, f"Draft not found: {draft_id}"

        # Load draft
        with open(draft_path, 'r') as f:
            draft = json.load(f)

        # Process decision
        if action == "approve_source_image":
            draft["images"]["selected_image"] = draft["images"]["primary_image"]
            draft["approval_workflow"]["image_approval"]["status"] = "approved"
            draft["approval_workflow"]["image_approval"]["admin_response"] = "approved_source"
            next_stage = "final_review"
            message = "Source image approved"

        elif action == "generate_ai_image":
            draft["approval_workflow"]["image_approval"]["status"] = "pending"
            draft["approval_workflow"]["image_approval"]["admin_response"] = "generate_ai"
            next_stage = "ai_generation"
            message = "AI image generation queued"

        elif action == "use_no_image":
            draft["images"]["selected_image"] = None
            draft["approval_workflow"]["image_approval"]["status"] = "approved"
            draft["approval_workflow"]["image_approval"]["admin_response"] = "skip"
            next_stage = "final_review"
            message = "Image skipped"

        elif action == "reject":
            return self.reject_draft(draft_id, admin_id, admin_username, notes or "Rejected at image stage")

        else:
            return False, f"Unknown action: {action}"

        # Update draft
        draft["approval_workflow"]["current_stage"] = next_stage
        draft["approval_workflow"]["image_approval"]["admin_id"] = admin_id
        draft["approval_workflow"]["image_approval"]["admin_username"] = admin_username
        draft["approval_workflow"]["image_approval"]["admin_decision_at"] = datetime.now().isoformat()
        draft["approval_workflow"]["image_approval"]["admin_notes"] = notes

        # Save updated draft
        with open(draft_path, 'w') as f:
            json.dump(draft, f, indent=2)

        # Log decision
        self._log_approval_decision(
            draft_id, action, admin_id, admin_username, notes
        )

        return True, message

    def handle_final_approval_decision(
        self,
        draft_id: str,
        action: str,
        admin_id: int,
        admin_username: str,
        notes: Optional[str] = None,
        changes: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Handle admin decision on final approval

        Args:
            draft_id: Draft ID
            action: Action from button (approve, edit, request_changes, reject)
            admin_id: Admin Telegram ID
            admin_username: Admin Telegram username
            notes: Optional admin notes
            changes: Dict of requested changes

        Returns:
            (success, message)
        """
        logger.info(f"Final approval decision: {action} for {draft_id}")

        draft_path = self.drafts_dir / f"{draft_id}.json"
        if not draft_path.exists():
            return False, f"Draft not found: {draft_id}"

        # Load draft
        with open(draft_path, 'r') as f:
            draft = json.load(f)

        # Process decision
        if action == "approve":
            draft["approval_workflow"]["final_approval"]["status"] = "approved"
            draft["approval_workflow"]["final_approval"]["admin_response"] = "approved"
            draft["approval_workflow"]["current_stage"] = "approved"
            draft["publication"]["ready_to_publish"] = True
            message = "✅ Draft approved for publication!"

        elif action == "edit":
            draft["approval_workflow"]["final_approval"]["status"] = "pending_edit"
            draft["approval_workflow"]["final_approval"]["admin_response"] = "edit_requested"
            draft["approval_workflow"]["current_stage"] = "edit"
            message = "📝 Draft returned for editing"

        elif action == "request_changes":
            draft["approval_workflow"]["final_approval"]["status"] = "pending_changes"
            draft["approval_workflow"]["final_approval"]["admin_response"] = "changes_requested"
            draft["approval_workflow"]["final_approval"]["changes_requested"] = changes
            draft["approval_workflow"]["current_stage"] = "content_validation"
            message = "🔄 Changes requested"

        elif action == "reject":
            return self.reject_draft(draft_id, admin_id, admin_username, notes or "Rejected at final stage")

        else:
            return False, f"Unknown action: {action}"

        # Update draft
        draft["approval_workflow"]["final_approval"]["admin_id"] = admin_id
        draft["approval_workflow"]["final_approval"]["admin_username"] = admin_username
        draft["approval_workflow"]["final_approval"]["admin_decision_at"] = datetime.now().isoformat()
        draft["approval_workflow"]["final_approval"]["admin_notes"] = notes

        # Save updated draft
        with open(draft_path, 'w') as f:
            json.dump(draft, f, indent=2)

        # Log decision
        self._log_approval_decision(
            draft_id, action, admin_id, admin_username, notes
        )

        return True, message

    # ═════════════════════════════════════════════════════════════════════════════
    # DRAFT REJECTION
    # ═════════════════════════════════════════════════════════════════════════════

    def reject_draft(
        self,
        draft_id: str,
        admin_id: int,
        admin_username: str,
        reason: str
    ) -> Tuple[bool, str]:
        """
        Reject draft and move to rejected state

        Args:
            draft_id: Draft ID
            admin_id: Admin Telegram ID
            admin_username: Admin Telegram username
            reason: Rejection reason

        Returns:
            (success, message)
        """
        logger.info(f"Rejecting draft: {draft_id}")

        draft_path = self.drafts_dir / f"{draft_id}.json"
        if not draft_path.exists():
            return False, f"Draft not found: {draft_id}"

        # Load draft
        with open(draft_path, 'r') as f:
            draft = json.load(f)

        # Update rejection status
        draft["approval_workflow"]["status"] = "rejected"
        draft["approval_workflow"]["current_stage"] = "rejected"

        # Add rejection record
        rejection_record = {
            "admin_id": admin_id,
            "admin_username": admin_username,
            "rejected_at": datetime.now().isoformat(),
            "reason": reason
        }

        if "rejections" not in draft["approval_workflow"]:
            draft["approval_workflow"]["rejections"] = []

        draft["approval_workflow"]["rejections"].append(rejection_record)

        # Save rejected draft
        with open(draft_path, 'w') as f:
            json.dump(draft, f, indent=2)

        # Archive rejected draft
        archive_dir = self.drafts_dir / "rejected"
        archive_dir.mkdir(exist_ok=True)
        archive_path = archive_dir / f"{draft_id}.json"
        with open(archive_path, 'w') as f:
            json.dump(draft, f, indent=2)

        # Log rejection
        self._log_approval_decision(
            draft_id, "reject", admin_id, admin_username, reason
        )

        return True, f"❌ Draft rejected: {reason}"

    # ═════════════════════════════════════════════════════════════════════════════
    # LOGGING & TRACKING
    # ═════════════════════════════════════════════════════════════════════════════

    def _log_approval_decision(
        self,
        draft_id: str,
        action: str,
        admin_id: int,
        admin_username: str,
        notes: Optional[str]
    ):
        """Log approval decision to JSONL file"""
        decision = {
            "timestamp": datetime.now().isoformat(),
            "draft_id": draft_id,
            "action": action,
            "admin_id": admin_id,
            "admin_username": admin_username,
            "notes": notes
        }

        with open(self.approvals_log, 'a') as f:
            f.write(json.dumps(decision) + '\n')

        logger.info(f"Logged approval decision: {draft_id} → {action}")

    def get_draft_approval_history(self, draft_id: str) -> List[Dict]:
        """Get approval history for a draft"""
        history = []

        if not self.approvals_log.exists():
            return history

        with open(self.approvals_log, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                decision = json.loads(line)
                if decision.get("draft_id") == draft_id:
                    history.append(decision)

        return history

    # ═════════════════════════════════════════════════════════════════════════════
    # DRAFT STATISTICS & MONITORING
    # ═════════════════════════════════════════════════════════════════════════════

    def get_approval_stats(self) -> Dict:
        """Get approval workflow statistics"""
        stats = {
            "total_drafts": 0,
            "pending_approval": 0,
            "awaiting_image": 0,
            "awaiting_final": 0,
            "approved": 0,
            "rejected": 0,
            "published": 0
        }

        if not self.drafts_dir.exists():
            return stats

        for draft_file in self.drafts_dir.glob("*.json"):
            if draft_file.name == "DRAFT_STRUCTURE_V2_WITH_IMAGES.json":
                continue

            stats["total_drafts"] += 1

            try:
                with open(draft_file, 'r') as f:
                    draft = json.load(f)

                status = draft.get("approval_workflow", {}).get("status", "unknown")

                if status == "approved":
                    stats["approved"] += 1
                elif status == "rejected":
                    stats["rejected"] += 1
                else:
                    stage = draft.get("approval_workflow", {}).get("current_stage", "")
                    if stage == "image_approval":
                        stats["awaiting_image"] += 1
                    elif stage == "final_review":
                        stats["awaiting_final"] += 1
                    else:
                        stats["pending_approval"] += 1

                if draft.get("publication", {}).get("published_to_channel"):
                    stats["published"] += 1

            except Exception as e:
                logger.error(f"Error reading draft {draft_file}: {e}")

        return stats

    def get_pending_approvals(self) -> List[Dict]:
        """Get list of drafts awaiting approval"""
        pending = []

        if not self.drafts_dir.exists():
            return pending

        for draft_file in self.drafts_dir.glob("*.json"):
            if draft_file.name == "DRAFT_STRUCTURE_V2_WITH_IMAGES.json":
                continue

            try:
                with open(draft_file, 'r') as f:
                    draft = json.load(f)

                status = draft.get("approval_workflow", {}).get("status")
                if status not in ["approved", "rejected", "published"]:
                    pending.append({
                        "draft_id": draft_file.stem,
                        "title": draft.get("content", {}).get("title", ""),
                        "current_stage": draft.get("approval_workflow", {}).get("current_stage", ""),
                        "created_at": draft.get("tracking", {}).get("created_timestamp", ""),
                        "needs_image_approval": draft.get("approval_workflow", {}).get("image_approval", {}).get("status") == "pending"
                    })
            except Exception as e:
                logger.error(f"Error reading draft {draft_file}: {e}")

        return pending


# ═════════════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    workflow = ApprovalWorkflow()

    # Example: Load sample draft
    sample_draft = {
        "draft_id": "draft_test_001",
        "content": {
            "title": "Test Post",
            "body": "Test content"
        },
        "images": {
            "primary_image": {
                "url": "https://example.com/image.jpg",
                "source_name": "@test"
            }
        },
        "approval_workflow": {
            "status": "pending",
            "current_stage": "image_approval",
            "image_approval": {"status": "pending"},
            "final_approval": {}
        },
        "publication": {"ready_to_publish": False}
    }

    # Generate preview
    preview = workflow.generate_image_approval_preview("draft_test_001", sample_draft)
    print(f"Preview: {preview.content[:100]}...")
    print(f"Buttons: {len(preview.buttons)} options")

    # Get stats
    stats = workflow.get_approval_stats()
    print(f"Stats: {stats}")
