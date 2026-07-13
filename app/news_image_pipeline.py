"""
News Image Pipeline

Handles image extraction and preparation for Telegram posts.

CRITICAL CONSTRAINT:
- This pipeline NEVER modifies post_text, title, or any content
- Image selection is completely separate from text generation
- Pipeline can return "no_image" and post still publishes as text-only
"""

import os
import logging
from typing import Dict, Optional, Any
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class NewsImagePipeline:
    """
    Prepare images for Telegram posts without modifying text content.
    """

    def __init__(self, cache_dir: str = "data/image_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Image generation config
        self.image_provider = os.getenv("IMAGE_PROVIDER", "none").lower()  # none, dalle, stable-diffusion
        self.image_api_key = os.getenv("IMAGE_API_KEY", None)
        self.image_enabled = self.image_provider != "none" and self.image_api_key

    def process_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a post to add image metadata (does NOT modify post_text).

        Input:
        {
            "source_url": "https://...",
            "source_image_url": "https://...",  # optional
            "title": "Post title",
            "preview_subtitle": "Brief summary",
            "post_text": "Full post text",
            "category": "manufacturing"
        }

        Output:
        {
            "visual_mode": "source_image|generated_image|prompt_only|no_image",
            "local_path": "/path/to/image.jpg",  # if downloaded/created
            "source_image_url": "https://...",   # if source
            "visual_prompt": "Description for generation",
            "rights_status": "free_to_use|requires_attribution|unknown",
            "error": None or "error message"
        }

        IMPORTANT: Never modifies post_text
        """
        result = {
            "visual_mode": "no_image",
            "local_path": None,
            "source_image_url": None,
            "visual_prompt": None,
            "rights_status": None,
            "error": None,
        }

        try:
            # Step 1: Try to extract source image from RSS
            if post_data.get("source_image_url"):
                source_image_result = self._process_source_image(post_data)
                if source_image_result["visual_mode"] != "no_image":
                    return source_image_result

            # Step 2: Try to generate image (if provider available)
            if self.image_enabled:
                generated_result = self._generate_image(post_data)
                if generated_result["visual_mode"] != "no_image":
                    return generated_result

            # Step 3: Create prompt for manual generation
            visual_prompt = self._create_visual_prompt(post_data)
            result["visual_mode"] = "prompt_only"
            result["visual_prompt"] = visual_prompt

            return result

        except Exception as e:
            logger.error(f"Error in image pipeline: {e}", exc_info=True)
            result["error"] = str(e)
            result["visual_mode"] = "no_image"
            return result

    def _process_source_image(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Try to use image from source (RSS feed).

        Returns: result dict with visual_mode, local_path, etc
        """
        result = {
            "visual_mode": "no_image",
            "local_path": None,
            "source_image_url": post_data.get("source_image_url"),
            "visual_prompt": None,
            "rights_status": "unknown",
            "error": None,
        }

        source_url = post_data.get("source_image_url")
        if not source_url:
            return result

        try:
            # Validate image URL
            if not self._is_valid_image_url(source_url):
                logger.warning(f"Source image URL not valid: {source_url}")
                return result

            # In production, would download and cache the image
            # For now, just mark as "source_image" mode (will send from source)
            result["visual_mode"] = "source_image"
            result["rights_status"] = "requires_attribution"  # Conservative default
            logger.info(f"Source image accepted: {source_url}")

            return result

        except Exception as e:
            logger.debug(f"Error processing source image: {e}")
            return result

    def _generate_image(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate image using configured provider (DALLE, Stable Diffusion, etc).

        Returns: result dict with visual_mode, local_path, etc
        """
        result = {
            "visual_mode": "no_image",
            "local_path": None,
            "source_image_url": None,
            "visual_prompt": self._create_visual_prompt(post_data),
            "rights_status": "generated",
            "error": None,
        }

        if not self.image_enabled:
            logger.debug("Image generation disabled: provider not configured")
            return result

        try:
            # Placeholder for actual image generation
            # In real implementation, would call DALLE API, Stable Diffusion, etc
            logger.info(f"Image generation placeholder: {self.image_provider}")

            # For now, just return the prompt (production will fill this in)
            # result["visual_mode"] = "generated_image"
            # result["local_path"] = "/path/to/generated.jpg"

            return result

        except Exception as e:
            logger.warning(f"Image generation failed: {e}")
            return result

    def _is_valid_image_url(self, url: str) -> bool:
        """
        Quick validation of image URL.

        Checks:
        - HTTPS or HTTP
        - Has image extension
        - Is not favicon/logo/tracking pixel
        """
        if not url or not isinstance(url, str):
            return False

        url_lower = url.lower()

        # Must be HTTP/HTTPS
        if not url_lower.startswith(("http://", "https://")):
            return False

        # Must have image extension
        valid_extensions = (".jpg", ".jpeg", ".png", ".webp", ".gif")
        if not any(url_lower.endswith(ext) for ext in valid_extensions):
            return False

        # Reject common false positives
        false_positives = ("favicon", "logo", "pixel", "tracking", "1x1", ".ico")
        if any(false in url_lower for false in false_positives):
            return False

        return True

    def _create_visual_prompt(self, post_data: Dict[str, Any]) -> str:
        """
        Create a text prompt for manual or automated image generation.

        Does NOT modify post_text.
        """
        title = post_data.get("title", "")
        category = post_data.get("category", "manufacturing")

        # Create a prompt based on title and category
        prompt = f"{title}. Category: {category}. "
        prompt += "Professional industrial or manufacturing setting. High quality."

        return prompt

    def should_use_photo_caption_mode(self, post_text: str) -> bool:
        """
        Determine if post should use send_photo(caption=...) vs separate send_message.

        Rule: If post is <= 1024 characters, use caption mode.
        Otherwise use text-only (too long for caption) or split into photo + message.
        """
        return len(post_text) <= 1024

    def validate_does_not_modify_text(self, original_text: str, final_post: Dict[str, Any]) -> bool:
        """
        Assert that image pipeline did not modify the post text.

        This validation runs before publishing to ensure isolation.
        """
        final_text = final_post.get("post_text", "")

        if original_text != final_text:
            logger.error(
                f"ALERT: Image pipeline modified post text!\n"
                f"Original ({len(original_text)} chars): {original_text[:100]}...\n"
                f"Final ({len(final_text)} chars): {final_text[:100]}..."
            )
            return False

        return True
