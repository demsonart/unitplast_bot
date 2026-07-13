"""
Local Preview Generator

Creates a complete preview of a Telegram post with image metadata.
Used for testing and showing the user the final result before publication.

Output: Saves to data/previews/latest_post.* files
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_local_preview(post_data: Dict[str, Any], image_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a complete preview for display/testing.

    Args:
        post_data: The final post (title, text, hashtags, etc)
        image_data: Image info from news_image_pipeline

    Returns:
        Preview structure
    """
    # Ensure preview directory exists
    preview_dir = Path("data/previews")
    preview_dir.mkdir(parents=True, exist_ok=True)

    preview = {
        "timestamp": datetime.now().isoformat(),
        "post": {
            "title": post_data.get("title", ""),
            "text": post_data.get("post_text", ""),
            "hashtags": post_data.get("hashtags", []),
            "source_url": post_data.get("source_url", ""),
            "source_name": post_data.get("source_name", ""),
        },
        "image": {
            "visual_mode": image_data.get("visual_mode", "no_image"),
            "visual_prompt": image_data.get("visual_prompt", ""),
            "source_image_url": image_data.get("source_image_url", ""),
            "local_path": image_data.get("local_path", ""),
            "rights_status": image_data.get("rights_status", ""),
        },
        "metadata": {
            "text_length": len(post_data.get("post_text", "")),
            "has_image": image_data.get("visual_mode") != "no_image",
            "requires_caption_mode": len(post_data.get("post_text", "")) <= 1024,
        },
    }

    # Save as JSON
    json_path = preview_dir / "latest_post.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(preview, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ Saved JSON preview to {json_path}")

    # Save as TXT (readable)
    txt_path = preview_dir / "latest_post.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"PREVIEW GENERATED: {preview['timestamp']}\n")
        f.write("=" * 80 + "\n\n")

        f.write("📰 POST CONTENT\n")
        f.write("-" * 80 + "\n")
        f.write(f"{post_data.get('title', '')}\n\n")
        f.write(f"{post_data.get('post_text', '')}\n\n")
        if post_data.get("hashtags"):
            f.write(" ".join(post_data.get("hashtags", [])) + "\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("🖼 IMAGE INFO\n")
        f.write("-" * 80 + "\n")
        f.write(f"Mode: {image_data.get('visual_mode')}\n")
        if image_data.get("visual_prompt"):
            f.write(f"Prompt: {image_data.get('visual_prompt')}\n")
        if image_data.get("source_image_url"):
            f.write(f"Source: {image_data.get('source_image_url')}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("📊 METADATA\n")
        f.write("-" * 80 + "\n")
        f.write(f"Source: {post_data.get('source_name')} ({post_data.get('source_url')})\n")
        f.write(f"Text length: {len(post_data.get('post_text', ''))} characters\n")
        f.write(f"Uses caption mode: {preview['metadata']['requires_caption_mode']}\n")

    logger.info(f"✅ Saved TXT preview to {txt_path}")

    return preview


def print_preview_to_console(preview: Dict[str, Any]) -> None:
    """Pretty print preview to console"""
    print("\n" + "=" * 80)
    print("📰 TELEGRAM POST PREVIEW")
    print("=" * 80 + "\n")

    print(preview["post"]["title"])
    print("\n" + "-" * 80 + "\n")
    print(preview["post"]["text"])

    if preview["post"]["hashtags"]:
        print("\n" + " ".join(preview["post"]["hashtags"]))

    print("\n" + "=" * 80)
    print("🖼 IMAGE")
    print("=" * 80)
    print(f"Mode: {preview['image']['visual_mode']}")
    if preview["image"]["visual_prompt"]:
        print(f"Prompt: {preview['image']['visual_prompt']}")
    if preview["image"]["source_image_url"]:
        print(f"Source: {preview['image']['source_image_url']}")

    print("\n" + "=" * 80)
    print(f"Text: {preview['metadata']['text_length']} chars | ", end="")
    print(f"Image: {preview['image']['visual_mode']}")
    print("=" * 80 + "\n")


def show_preview_files():
    """Display contents of preview files to user"""
    preview_dir = Path("data/previews")

    txt_file = preview_dir / "latest_post.txt"
    if txt_file.exists():
        print("\n" + "=" * 80)
        print("📄 PREVIEW FILE: latest_post.txt")
        print("=" * 80)
        with open(txt_file, "r", encoding="utf-8") as f:
            print(f.read())

    json_file = preview_dir / "latest_post.json"
    if json_file.exists():
        print("\n📄 JSON saved to: " + str(json_file))
        print("   (Machine-readable format for testing)")

    image_file = preview_dir / "latest_image.jpg"
    if image_file.exists():
        print("\n🖼 Image saved to: " + str(image_file))
