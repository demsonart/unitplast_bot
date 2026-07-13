"""
Telegram Image Handler for @UnitgroupAI News Bot
Handles image parsing, caching, AI generation, and policy enforcement
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ImageSource:
    """Represents an image source"""
    url: str
    source_type: str  # "rss" | "telegram" | "ai_generated" | "official_press"
    source_name: str  # RSS feed name or Telegram channel name
    description: str = ""
    file_path: Optional[str] = None
    mime_type: str = "image/jpeg"
    size_bytes: Optional[int] = None
    cached_at: Optional[str] = None
    approval_status: str = "needs_review"  # "needs_review" | "approved" | "rejected"


@dataclass
class ImagePolicy:
    """Image policy for a source"""
    can_use_source_image: bool
    allow_ai_generated: bool
    require_manual_check: bool
    max_image_size_mb: int = 5
    allowed_formats: List[str] = None
    copyright_check_required: bool = True

    def __post_init__(self):
        if self.allowed_formats is None:
            self.allowed_formats = ["image/jpeg", "image/png", "image/webp"]


@dataclass
class VisualPrompt:
    """AI image generation prompt"""
    text: str
    language: str = "ru"
    style: str = "realistic"  # "realistic" | "illustrated" | "technical" | "abstract"
    quality: str = "high"  # "low" | "medium" | "high"
    aspect_ratio: str = "16:9"
    themes: List[str] = None

    def __post_init__(self):
        if self.themes is None:
            self.themes = []


class TelegramImageHandler:
    """Handles all image operations for telegram news bot"""

    def __init__(self, cache_dir: str = "data/image_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self.policy_file = Path("data/image_policies.yaml")
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load image metadata from cache"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """Save image metadata to cache"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    # ═════════════════════════════════════════════════════════════════════════════
    # IMAGE PARSING FROM RSS FEEDS
    # ═════════════════════════════════════════════════════════════════════════════

    def parse_rss_image(
        self,
        feed_name: str,
        article_url: str,
        article_content: Dict
    ) -> Optional[ImageSource]:
        """
        Extract image from RSS article

        Args:
            feed_name: RSS feed name (e.g., "Woodworking Network")
            article_url: Article URL
            article_content: Article data with possible images

        Returns:
            ImageSource if found, None otherwise
        """
        logger.info(f"Parsing RSS image: {feed_name}")

        # Check for media:content
        if "media_content" in article_content:
            for media in article_content["media_content"]:
                if media.get("type", "").startswith("image"):
                    return ImageSource(
                        url=media.get("url"),
                        source_type="rss",
                        source_name=feed_name,
                        description=media.get("description", "RSS article image"),
                        approval_status="needs_review"
                    )

        # Check for image in content
        if "image" in article_content:
            return ImageSource(
                url=article_content["image"],
                source_type="rss",
                source_name=feed_name,
                description="RSS article featured image",
                approval_status="needs_review"
            )

        # Check for thumbnail
        if "thumbnail" in article_content:
            return ImageSource(
                url=article_content["thumbnail"],
                source_type="rss",
                source_name=feed_name,
                description="RSS article thumbnail",
                approval_status="needs_review"
            )

        logger.warning(f"No image found in RSS article from {feed_name}")
        return None

    # ═════════════════════════════════════════════════════════════════════════════
    # IMAGE PARSING FROM TELEGRAM POSTS
    # ═════════════════════════════════════════════════════════════════════════════

    def parse_telegram_image(
        self,
        channel_name: str,
        message_id: str,
        media_info: Dict
    ) -> Optional[ImageSource]:
        """
        Extract image from Telegram message

        Args:
            channel_name: Telegram channel name (e.g., "@cnc_skill")
            message_id: Telegram message ID
            media_info: Media info from Telegram API

        Returns:
            ImageSource if found, None otherwise
        """
        logger.info(f"Parsing Telegram image: {channel_name}/{message_id}")

        if not media_info:
            logger.warning(f"No media info for {channel_name}/{message_id}")
            return None

        # Photo
        if media_info.get("type") == "photo":
            return ImageSource(
                url=media_info.get("file_url"),
                source_type="telegram",
                source_name=channel_name,
                description=f"Telegram post from {channel_name}",
                approval_status="needs_review"
            )

        # Video thumbnail
        if media_info.get("type") == "video":
            if "thumbnail_url" in media_info:
                return ImageSource(
                    url=media_info["thumbnail_url"],
                    source_type="telegram",
                    source_name=channel_name,
                    description=f"Video thumbnail from {channel_name}",
                    approval_status="needs_review"
                )

        # Document with preview
        if media_info.get("type") == "document":
            if "preview_url" in media_info:
                return ImageSource(
                    url=media_info["preview_url"],
                    source_type="telegram",
                    source_name=channel_name,
                    description=f"Document preview from {channel_name}",
                    approval_status="needs_review"
                )

        logger.warning(f"No suitable image in Telegram media from {channel_name}")
        return None

    # ═════════════════════════════════════════════════════════════════════════════
    # IMAGE CACHING
    # ═════════════════════════════════════════════════════════════════════════════

    def cache_image(
        self,
        image_source: ImageSource,
        draft_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Download and cache image locally

        Args:
            image_source: ImageSource object
            draft_id: Draft ID for naming

        Returns:
            (success, file_path)
        """
        try:
            logger.info(f"Caching image for draft {draft_id}")

            # Generate cache filename
            url_hash = hashlib.md5(image_source.url.encode()).hexdigest()[:8]
            ext = self._get_file_extension(image_source.mime_type)
            cache_filename = f"{draft_id}_{url_hash}{ext}"
            cache_path = self.cache_dir / cache_filename

            if cache_path.exists():
                logger.info(f"Image already cached: {cache_path}")
                return True, str(cache_path)

            # Download image
            import requests
            response = requests.get(image_source.url, timeout=10)
            response.raise_for_status()

            # Save to cache
            with open(cache_path, 'wb') as f:
                f.write(response.content)

            # Update metadata
            image_source.file_path = str(cache_path)
            image_source.size_bytes = len(response.content)
            image_source.cached_at = datetime.now().isoformat()

            self.metadata[draft_id] = asdict(image_source)
            self._save_metadata()

            logger.info(f"Image cached: {cache_path}")
            return True, str(cache_path)

        except Exception as e:
            logger.error(f"Failed to cache image: {e}")
            return False, None

    def _get_file_extension(self, mime_type: str) -> str:
        """Get file extension from MIME type"""
        extensions = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif",
        }
        return extensions.get(mime_type, ".jpg")

    # ═════════════════════════════════════════════════════════════════════════════
    # IMAGE POLICY VALIDATION
    # ═════════════════════════════════════════════════════════════════════════════

    def validate_image_policy(
        self,
        image_source: ImageSource,
        source_config: Dict
    ) -> Tuple[bool, str]:
        """
        Validate image against source policy

        Args:
            image_source: ImageSource object
            source_config: Source configuration from media_sources.yaml or telegram_sources.yaml

        Returns:
            (is_valid, message)
        """
        logger.info(f"Validating image policy for {image_source.source_name}")

        # Extract policy from source config
        content_policy = source_config.get("content_policy", {})
        can_use_source_image = content_policy.get("copy_images", False)
        allow_ai_generated = content_policy.get("allow_ai_generated_visual", False)

        # Check source image usage
        if image_source.source_type in ["rss", "telegram"]:
            if not can_use_source_image:
                return False, f"Source {image_source.source_name} does not allow using source images"

            # Require manual media check
            if content_policy.get("require_manual_media_check", True):
                return False, f"Image requires manual approval before use"

        # Check AI-generated
        if image_source.source_type == "ai_generated":
            if not allow_ai_generated:
                return False, f"Source {image_source.source_name} does not allow AI-generated images"

        # Check file size
        if image_source.size_bytes and image_source.size_bytes > 5 * 1024 * 1024:
            return False, "Image exceeds 5MB size limit"

        # Check format
        allowed_formats = content_policy.get("allowed_formats", ["image/jpeg", "image/png"])
        if image_source.mime_type not in allowed_formats:
            return False, f"Image format {image_source.mime_type} not allowed"

        logger.info(f"Image policy validation passed for {image_source.source_name}")
        return True, "Policy validation passed"

    # ═════════════════════════════════════════════════════════════════════════════
    # VISUAL PROMPT GENERATION FOR AI IMAGES
    # ═════════════════════════════════════════════════════════════════════════════

    def generate_visual_prompt(
        self,
        post_text: str,
        category: str,
        content_summary: Dict
    ) -> VisualPrompt:
        """
        Generate AI image prompt based on post content

        Args:
            post_text: Post text for context
            category: Content category
            content_summary: Summary of post content

        Returns:
            VisualPrompt for AI image generation
        """
        logger.info(f"Generating visual prompt for category {category}")

        # Extract key themes from content
        themes = self._extract_themes(post_text, category, content_summary)

        # Generate prompt based on category
        prompt_text = self._build_prompt_text(category, themes, content_summary)

        # Determine style based on category
        style = self._get_style_for_category(category)

        visual_prompt = VisualPrompt(
            text=prompt_text,
            language="ru",
            style=style,
            quality="high",
            aspect_ratio="16:9",
            themes=themes
        )

        logger.info(f"Generated visual prompt: {prompt_text[:100]}...")
        return visual_prompt

    def _extract_themes(
        self,
        post_text: str,
        category: str,
        content_summary: Dict
    ) -> List[str]:
        """Extract visual themes from post content"""
        themes = []

        # Category-based themes
        category_themes = {
            "cnc_machines": ["промышленное оборудование", "станок", "производство"],
            "woodworking": ["деревообработка", "мастерская", "инструменты"],
            "furniture_production": ["мебель", "современный дизайн", "производство"],
            "cad_engineering": ["3D дизайн", "инженерия", "технические чертежи"],
            "business_ideas": ["бизнес", "стартап", "предпринимательство"],
            "industry_news": ["производство", "технологии", "автоматизация"],
            "innovation": ["инновация", "технологии", "будущее"],
            "tools_diy": ["инструменты", "DIY", "практика"],
        }

        themes.extend(category_themes.get(category, []))

        # Content-based themes
        keywords = content_summary.get("keywords", [])
        themes.extend(keywords[:3])

        return list(set(themes))  # Remove duplicates

    def _build_prompt_text(
        self,
        category: str,
        themes: List[str],
        content_summary: Dict
    ) -> str:
        """Build detailed prompt text for AI image generation"""
        title = content_summary.get("title", "")
        summary = content_summary.get("summary", "")

        # Base prompt structure
        prompt = f"Professional industrial photography. {', '.join(themes)}. "
        prompt += f"Title: {title}. "
        prompt += f"Context: {summary[:100]}. "
        prompt += "High resolution, professional lighting, realistic style, "
        prompt += "suitable for business media channel. Russian industrial context."

        return prompt

    def _get_style_for_category(self, category: str) -> str:
        """Get appropriate image style for category"""
        style_mapping = {
            "cnc_machines": "technical",
            "woodworking": "realistic",
            "furniture_production": "realistic",
            "cad_engineering": "technical",
            "business_ideas": "illustrated",
            "industry_news": "realistic",
            "innovation": "abstract",
            "tools_diy": "realistic",
        }
        return style_mapping.get(category, "realistic")

    # ═════════════════════════════════════════════════════════════════════════════
    # IMAGE APPROVAL WORKFLOW
    # ═════════════════════════════════════════════════════════════════════════════

    def request_image_approval(
        self,
        draft_id: str,
        image_source: ImageSource
    ) -> Dict:
        """
        Create image approval request for admin

        Args:
            draft_id: Draft ID
            image_source: ImageSource to approve

        Returns:
            Approval request data
        """
        return {
            "draft_id": draft_id,
            "image_id": f"{draft_id}_image",
            "source": image_source.source_name,
            "source_type": image_source.source_type,
            "image_url": image_source.url or image_source.file_path,
            "description": image_source.description,
            "status": "pending_approval",
            "requires_review": True,
            "approval_options": [
                {"action": "approve", "label": "✅ Use this image"},
                {"action": "reject", "label": "❌ Reject"},
                {"action": "generate_ai", "label": "🤖 Generate AI image"},
                {"action": "skip", "label": "⏭️ Skip image"},
            ]
        }

    def approve_image(
        self,
        draft_id: str,
        image_id: str,
        approval: bool = True
    ):
        """Mark image as approved"""
        if draft_id in self.metadata:
            self.metadata[draft_id]["approval_status"] = "approved" if approval else "rejected"
            self._save_metadata()
            logger.info(f"Image approval status updated: {image_id}")

    # ═════════════════════════════════════════════════════════════════════════════
    # IMAGE SELECTION & FALLBACK
    # ═════════════════════════════════════════════════════════════════════════════

    def select_image_for_draft(
        self,
        draft_id: str,
        available_images: List[ImageSource],
        source_config: Dict
    ) -> Dict:
        """
        Select best image for draft from available options

        Args:
            draft_id: Draft ID
            available_images: List of potential images
            source_config: Source configuration

        Returns:
            Selected image info with recommendation
        """
        logger.info(f"Selecting image for draft {draft_id}")

        selected = None
        recommendation = ""

        # Filter by policy
        valid_images = []
        for img in available_images:
            is_valid, msg = self.validate_image_policy(img, source_config)
            if is_valid:
                valid_images.append(img)

        if valid_images:
            # Use first valid image
            selected = valid_images[0]
            recommendation = "Using source image (approved by policy)"
        else:
            # Fallback to AI generation
            recommendation = "No source image available. Recommend AI generation."

        return {
            "draft_id": draft_id,
            "selected_image": asdict(selected) if selected else None,
            "recommendation": recommendation,
            "requires_approval": True,
            "next_action": "needs_approval" if selected else "needs_ai_generation"
        }

    # ═════════════════════════════════════════════════════════════════════════════
    # STATISTICS & MONITORING
    # ═════════════════════════════════════════════════════════════════════════════

    def get_cache_stats(self) -> Dict:
        """Get image cache statistics"""
        cache_files = list(self.cache_dir.glob("*"))
        image_files = [f for f in cache_files if f.is_file() and f.name != "metadata.json"]

        total_size = sum(f.stat().st_size for f in image_files) / (1024 * 1024)  # MB

        return {
            "total_cached_images": len(image_files),
            "cache_size_mb": round(total_size, 2),
            "cache_dir": str(self.cache_dir),
            "metadata_entries": len(self.metadata)
        }

    def cleanup_cache(self, max_age_days: int = 30):
        """Clean old cached images"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60

        for cache_file in self.cache_dir.glob("*"):
            if cache_file.name == "metadata.json":
                continue

            file_age = current_time - cache_file.stat().st_mtime
            if file_age > max_age_seconds:
                cache_file.unlink()
                logger.info(f"Cleaned old cache file: {cache_file.name}")


# ═════════════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize handler
    handler = TelegramImageHandler()

    # Example: Parse RSS image
    rss_article = {
        "image": "https://example.com/image.jpg",
        "title": "New CNC Machine Released",
        "summary": "Industry news about new machinery"
    }

    image_source = handler.parse_rss_image("Woodworking Network", "https://example.com/article", rss_article)
    if image_source:
        success, path = handler.cache_image(image_source, "draft_001")
        print(f"Image cached: {path}")

    # Print stats
    stats = handler.get_cache_stats()
    print(f"Cache stats: {stats}")
