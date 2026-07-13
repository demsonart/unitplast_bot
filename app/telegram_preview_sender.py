"""
Telegram Preview Sender for Admin Approval
Sends draft previews with inline buttons to admin chat
"""

import logging
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import requests
import json

logger = logging.getLogger(__name__)


@dataclass
class TelegramMessage:
    """Telegram message data"""
    chat_id: int
    text: str
    photo: Optional[str] = None
    reply_markup: Optional[Dict] = None
    parse_mode: str = "HTML"
    disable_web_page_preview: bool = True


class TelegramPreviewSender:
    """Sends admin previews via Telegram with approval buttons"""

    def __init__(self, bot_token: str, admin_chat_id: int):
        self.bot_token = bot_token
        self.admin_chat_id = admin_chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.dry_run = True  # Always true unless explicitly disabled
        self.message_history = {}  # Track sent preview messages

    # ═════════════════════════════════════════════════════════════════════════════
    # SEND PREVIEW WITH IMAGE & BUTTONS
    # ═════════════════════════════════════════════════════════════════════════════

    def send_image_approval_preview(
        self,
        draft_id: str,
        preview_text: str,
        image_url: Optional[str],
        buttons: List[Dict]
    ) -> Tuple[bool, Optional[int]]:
        """
        Send image approval preview to admin

        Args:
            draft_id: Draft ID
            preview_text: Preview message text
            image_url: Image URL (optional)
            buttons: List of button dicts

        Returns:
            (success, message_id)
        """
        logger.info(f"Sending image approval preview for {draft_id}")

        # Build reply markup (inline buttons)
        reply_markup = self._build_inline_keyboard(buttons)

        # Send message
        if image_url:
            return self._send_photo_with_buttons(
                preview_text, image_url, reply_markup, draft_id
            )
        else:
            return self._send_text_with_buttons(
                preview_text, reply_markup, draft_id
            )

    def send_final_approval_preview(
        self,
        draft_id: str,
        preview_text: str,
        image_url: Optional[str],
        buttons: List[Dict]
    ) -> Tuple[bool, Optional[int]]:
        """
        Send final approval preview to admin

        Args:
            draft_id: Draft ID
            preview_text: Full post preview
            image_url: Image URL (optional)
            buttons: List of button dicts

        Returns:
            (success, message_id)
        """
        logger.info(f"Sending final approval preview for {draft_id}")

        reply_markup = self._build_inline_keyboard(buttons)

        if image_url:
            return self._send_photo_with_buttons(
                preview_text, image_url, reply_markup, draft_id
            )
        else:
            return self._send_text_with_buttons(
                preview_text, reply_markup, draft_id
            )

    # ═════════════════════════════════════════════════════════════════════════════
    # TELEGRAM API CALLS
    # ═════════════════════════════════════════════════════════════════════════════

    def _send_text_with_buttons(
        self,
        text: str,
        reply_markup: Dict,
        draft_id: str
    ) -> Tuple[bool, Optional[int]]:
        """Send text message with inline buttons"""
        if self.dry_run:
            logger.info(f"DRY_RUN: Would send preview for {draft_id}")
            return True, None

        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": self.admin_chat_id,
                "text": text,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(reply_markup),
                "disable_web_page_preview": True
            }

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                message_id = result["result"]["message_id"]
                self.message_history[draft_id] = message_id
                logger.info(f"Preview sent: {draft_id} → message_id {message_id}")
                return True, message_id
            else:
                logger.error(f"Telegram error: {result.get('description')}")
                return False, None

        except Exception as e:
            logger.error(f"Failed to send preview: {e}")
            return False, None

    def _send_photo_with_buttons(
        self,
        caption: str,
        photo_url: str,
        reply_markup: Dict,
        draft_id: str
    ) -> Tuple[bool, Optional[int]]:
        """Send photo with caption and inline buttons"""
        if self.dry_run:
            logger.info(f"DRY_RUN: Would send photo preview for {draft_id}")
            return True, None

        try:
            url = f"{self.api_url}/sendPhoto"
            data = {
                "chat_id": self.admin_chat_id,
                "photo": photo_url,
                "caption": caption,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(reply_markup)
            }

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                message_id = result["result"]["message_id"]
                self.message_history[draft_id] = message_id
                logger.info(f"Photo preview sent: {draft_id} → message_id {message_id}")
                return True, message_id
            else:
                logger.error(f"Telegram error: {result.get('description')}")
                return False, None

        except Exception as e:
            logger.error(f"Failed to send photo preview: {e}")
            return False, None

    # ═════════════════════════════════════════════════════════════════════════════
    # BUTTON BUILDING
    # ═════════════════════════════════════════════════════════════════════════════

    def _build_inline_keyboard(self, buttons: List[Dict]) -> Dict:
        """Build Telegram inline keyboard from button list"""
        keyboard = []

        for button in buttons:
            # Telegram format: 2 buttons per row
            if len(keyboard) and len(keyboard[-1]) < 2:
                keyboard[-1].append({
                    "text": button["text"],
                    "callback_data": button["callback_data"]
                })
            else:
                keyboard.append([{
                    "text": button["text"],
                    "callback_data": button["callback_data"]
                }])

        return {"inline_keyboard": keyboard}

    # ═════════════════════════════════════════════════════════════════════════════
    # CALLBACK HANDLING
    # ═════════════════════════════════════════════════════════════════════════════

    def handle_callback_query(
        self,
        callback_query_id: str,
        callback_data: str
    ) -> Tuple[str, str]:
        """
        Parse callback data and return action info

        Args:
            callback_query_id: Telegram callback query ID
            callback_data: Callback data from button

        Returns:
            (action, draft_id)
        """
        # Parse callback_data format: "action_draft_id"
        # Examples: "approve_source_draft_001", "reject_draft_002"

        parts = callback_data.rsplit("_", 1)  # Split from right to get draft_id
        if len(parts) == 2:
            draft_id = parts[1]
            action_part = parts[0]

            # Map to action
            action_map = {
                "approve_source": "approve_source_image",
                "generate_ai": "generate_ai_image",
                "skip_image": "use_no_image",
                "approve": "approve",
                "reject": "reject",
                "edit": "edit",
                "request_changes": "request_changes"
            }

            action = action_map.get(action_part, "unknown")
            return action, draft_id

        return "unknown", ""

    def answer_callback_query(
        self,
        callback_query_id: str,
        text: str,
        show_alert: bool = False
    ) -> bool:
        """
        Send callback query answer (notification)

        Args:
            callback_query_id: Telegram callback query ID
            text: Notification text
            show_alert: Show as alert instead of popup

        Returns:
            Success status
        """
        if self.dry_run:
            logger.info(f"DRY_RUN: Would answer callback {callback_query_id}")
            return True

        try:
            url = f"{self.api_url}/answerCallbackQuery"
            data = {
                "callback_query_id": callback_query_id,
                "text": text,
                "show_alert": show_alert
            }

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            return result.get("ok", False)

        except Exception as e:
            logger.error(f"Failed to answer callback: {e}")
            return False

    # ═════════════════════════════════════════════════════════════════════════════
    # PREVIEW UPDATES
    # ═════════════════════════════════════════════════════════════════════════════

    def update_preview_message(
        self,
        draft_id: str,
        new_text: str,
        new_image_url: Optional[str] = None,
        new_buttons: Optional[List[Dict]] = None
    ) -> bool:
        """
        Update existing preview message

        Args:
            draft_id: Draft ID
            new_text: Updated text
            new_image_url: Updated image (optional)
            new_buttons: Updated buttons (optional)

        Returns:
            Success status
        """
        if draft_id not in self.message_history:
            logger.warning(f"No message history for {draft_id}")
            return False

        message_id = self.message_history[draft_id]

        if self.dry_run:
            logger.info(f"DRY_RUN: Would update preview message {message_id}")
            return True

        try:
            reply_markup = self._build_inline_keyboard(new_buttons) if new_buttons else None

            url = f"{self.api_url}/editMessageCaption"
            data = {
                "chat_id": self.admin_chat_id,
                "message_id": message_id,
                "caption": new_text,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(reply_markup) if reply_markup else None
            }

            # Remove None values
            data = {k: v for k, v in data.items() if v is not None}

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            return result.get("ok", False)

        except Exception as e:
            logger.error(f"Failed to update preview: {e}")
            return False

    def delete_preview_message(self, draft_id: str) -> bool:
        """Delete preview message"""
        if draft_id not in self.message_history:
            return False

        message_id = self.message_history[draft_id]

        if self.dry_run:
            logger.info(f"DRY_RUN: Would delete preview message {message_id}")
            del self.message_history[draft_id]
            return True

        try:
            url = f"{self.api_url}/deleteMessage"
            data = {
                "chat_id": self.admin_chat_id,
                "message_id": message_id
            }

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                del self.message_history[draft_id]
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to delete preview: {e}")
            return False

    # ═════════════════════════════════════════════════════════════════════════════
    # NOTIFICATIONS
    # ═════════════════════════════════════════════════════════════════════════════

    def send_notification(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send notification to admin chat"""
        if self.dry_run:
            logger.info(f"DRY_RUN: Would send notification: {text[:50]}...")
            return True

        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": self.admin_chat_id,
                "text": text,
                "parse_mode": parse_mode
            }

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            result = response.json()
            return result.get("ok", False)

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def send_approval_confirmation(self, draft_id: str, status: str) -> bool:
        """Send approval confirmation notification"""
        messages = {
            "approved": f"✅ Draft {draft_id} approved for publication!",
            "rejected": f"❌ Draft {draft_id} rejected",
            "pending_changes": f"🔄 Changes requested for {draft_id}",
            "ai_generation": f"🤖 AI image generation started for {draft_id}"
        }

        text = messages.get(status, f"📋 Status update for {draft_id}")
        return self.send_notification(text)

    # ═════════════════════════════════════════════════════════════════════════════
    # STATISTICS & MONITORING
    # ═════════════════════════════════════════════════════════════════════════════

    def get_message_history(self) -> Dict[str, int]:
        """Get all tracked preview messages"""
        return self.message_history.copy()

    def get_stats(self) -> Dict:
        """Get preview sender statistics"""
        return {
            "total_previews_sent": len(self.message_history),
            "active_previews": len(self.message_history),
            "dry_run_mode": self.dry_run,
            "bot_token_set": bool(self.bot_token),
            "admin_chat_id": self.admin_chat_id
        }


# ═════════════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Example (would need real bot token and chat ID)
    sender = TelegramPreviewSender(
        bot_token="YOUR_BOT_TOKEN",
        admin_chat_id=-1001234567890
    )

    # Example buttons
    buttons = [
        {
            "text": "✅ Use Image",
            "callback_data": "approve_source_draft_001"
        },
        {
            "text": "🤖 Generate AI",
            "callback_data": "generate_ai_draft_001"
        }
    ]

    # Send preview
    success, message_id = sender.send_image_approval_preview(
        draft_id="draft_001",
        preview_text="Preview text here",
        image_url=None,
        buttons=buttons
    )

    print(f"Preview sent: {success}, message_id: {message_id}")

    # Get stats
    stats = sender.get_stats()
    print(f"Stats: {stats}")
