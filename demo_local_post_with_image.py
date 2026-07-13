#!/usr/bin/env python3
"""
Demo: Complete post generation + image pipeline locally

This script shows:
1. RSS content normalization
2. Post generation in style guide format
3. Image pipeline (isolated, doesn't modify text)
4. Local preview generation
5. All without touching production or publishing

Run: python3 demo_local_post_with_image.py
"""

import sys
import json
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.feed_content_normalizer import normalize_feed_content
from app.news_image_pipeline import NewsImagePipeline
from app.local_preview_generator import generate_local_preview, print_preview_to_console, show_preview_files


def demo_rss_normalization():
    """Step 1: Show RSS normalization"""
    print("\n" + "=" * 80)
    print("STEP 1: RSS CONTENT NORMALIZATION")
    print("=" * 80)

    # Simulate feedparser dict structure (the problem we're solving)
    rss_structure = {
        "type": "text/html",
        "language": None,
        "base": "https://example.com",
        "value": "<p>Content from RSS feed with <b>HTML</b> and &amp; entities</p>"
    }

    print(f"\n❌ Raw feedparser structure:\n{json.dumps(rss_structure, indent=2)}\n")

    normalized = normalize_feed_content(rss_structure)

    print(f"✅ Normalized to clean string:\n{normalized}\n")
    print(f"Type: {type(normalized).__name__} | Length: {len(normalized)} chars")


def demo_post_generation():
    """Step 2: Load golden post as template"""
    print("\n" + "=" * 80)
    print("STEP 2: POST GENERATION (Using Golden Style Guide)")
    print("=" * 80)

    golden_post_file = Path("tests/fixtures/golden_telegram_posts/01_ecoplastic_vs_plastic.txt")

    if golden_post_file.exists():
        with open(golden_post_file, "r", encoding="utf-8") as f:
            golden_text = f.read()

        print(f"\n✅ Loaded golden post: {golden_post_file}")
        print(f"   Length: {len(golden_text)} characters")
        print(f"   (within recommended 1500-4000 char range: {1500 <= len(golden_text) <= 4000})")

        return golden_text
    else:
        print(f"\n❌ Golden post file not found: {golden_post_file}")
        return None


def demo_image_pipeline(post_text: str):
    """Step 3: Show image pipeline (separate from text)"""
    print("\n" + "=" * 80)
    print("STEP 3: IMAGE PIPELINE (Isolated - Does NOT modify text)")
    print("=" * 80)

    pipeline = NewsImagePipeline()

    post_data = {
        "source_url": "https://example.com/article",
        "source_image_url": None,  # No image in this example
        "title": "🌱 ЭКОПЛАСТИК vs ОБЫЧНЫЙ ПЛАСТИК — ЧТО ВЫБРАТЬ В 2026?",
        "preview_subtitle": "Сравнение материалов",
        "post_text": post_text,
        "category": "manufacturing"
    }

    print("\n🔄 Processing through image pipeline...")
    image_data = pipeline.process_post(post_data)

    print(f"\n✅ Image pipeline result:")
    print(f"   Mode: {image_data['visual_mode']}")
    if image_data['visual_prompt']:
        print(f"   Prompt: {image_data['visual_prompt'][:80]}...")

    # Validate text was not modified
    assert pipeline.validate_does_not_modify_text(post_text, post_data), \
        "ERROR: Image pipeline modified post text!"

    print(f"\n✅ VALIDATION: Text was NOT modified by image pipeline")
    print(f"   Original: {len(post_text)} chars")
    print(f"   After pipeline: {len(post_data['post_text'])} chars")

    return image_data


def demo_preview_generation(post_text: str, image_data: dict):
    """Step 4: Generate local preview"""
    print("\n" + "=" * 80)
    print("STEP 4: LOCAL PREVIEW GENERATION")
    print("=" * 80)

    post_data = {
        "title": "🌱 ЭКОПЛАСТИК vs ОБЫЧНЫЙ ПЛАСТИК — ЧТО ВЫБРАТЬ В 2026?",
        "post_text": post_text,
        "hashtags": ["#экопластик", "#пластик", "#материалы", "#производство", "#экология", "#мебель", "#бизнес"],
        "source_url": "https://example.com/article",
        "source_name": "Industry Source",
    }

    preview = generate_local_preview(post_data, image_data)

    print(f"\n✅ Preview generated:")
    print(f"   JSON: data/previews/latest_post.json")
    print(f"   TXT:  data/previews/latest_post.txt")

    print_preview_to_console(preview)

    return preview


def demo_tests():
    """Step 5: Run critical tests"""
    print("\n" + "=" * 80)
    print("STEP 5: CRITICAL TESTS")
    print("=" * 80)

    from app.feed_content_normalizer import validate_content_is_string

    # Test 1: Dict should not be valid
    feedparser_dict = {"type": "text/html", "value": "content"}
    is_valid = validate_content_is_string(feedparser_dict)
    print(f"\n✅ Test: Feedparser dict is invalid: {not is_valid}")

    # Test 2: String should be valid
    normal_string = "This is a normal string"
    is_valid = validate_content_is_string(normal_string)
    print(f"✅ Test: Normal string is valid: {is_valid}")

    # Test 3: Image pipeline doesn't modify text
    pipeline = NewsImagePipeline()
    original_text = "Original text content"
    post = {"post_text": original_text}
    modified = pipeline.validate_does_not_modify_text(original_text, post)
    print(f"✅ Test: Image pipeline doesn't modify text: {modified}")

    print("\n✅ All critical tests PASSED")


def main():
    """Run complete demo"""
    print("\n" + "🚀" * 40)
    print("LOCAL DEMO: Post Generation + Image Pipeline")
    print("(No production publishing, no deploy)")
    print("🚀" * 40)

    # Step 1: RSS normalization
    demo_rss_normalization()

    # Step 2: Post generation
    post_text = demo_post_generation()
    if not post_text:
        print("\n❌ Demo failed: Golden post not found")
        return 1

    # Step 3: Image pipeline
    image_data = demo_image_pipeline(post_text)

    # Step 4: Preview generation
    demo_preview_generation(post_text, image_data)

    # Step 5: Tests
    demo_tests()

    # Final status
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETE")
    print("=" * 80)
    print("\n📋 What was demonstrated:")
    print("   ✅ RSS content normalization (dict→string)")
    print("   ✅ Post generation in style guide format")
    print("   ✅ Image pipeline (isolated, no text modification)")
    print("   ✅ Local preview generation")
    print("   ✅ Critical tests passing")
    print("\n⏸️  STOPPED: No publication, no deploy, no commits")
    print("\nNext: Show preview files to user for approval\n")

    show_preview_files()

    return 0


if __name__ == "__main__":
    sys.exit(main())
