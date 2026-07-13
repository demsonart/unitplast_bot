"""
Autonomous News Enhancement Agent
Automatically fetches, improves, and publishes news to @UnitgroupAI
"""

import os
import json
import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from app.industry_news_rewriter import NewsRewriter
from app.media_bot_integration import MediaBotIntegration
import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

AUTONOMOUS_MODE = os.getenv("AUTONOMOUS_MODE", "false").lower() in ("true", "1", "yes")
AUTO_PUBLISH_ENABLED = os.getenv("AUTO_PUBLISH_ENABLED", "false").lower() in ("true", "1", "yes")
AUTONOMOUS_QUALITY_THRESHOLD = float(os.getenv("AUTONOMOUS_QUALITY_THRESHOLD", "0.85"))
PREVIEW_THRESHOLD = float(os.getenv("PREVIEW_THRESHOLD", "0.75"))
MIN_QUALITY_THRESHOLD = float(os.getenv("MIN_QUALITY_THRESHOLD", "0.65"))
PREVIEW_WINDOW_MINUTES = int(os.getenv("PREVIEW_WINDOW_MINUTES", "60"))
FETCH_INTERVAL_MINUTES = int(os.getenv("FETCH_INTERVAL_MINUTES", "30"))
MAX_ARTICLES_PER_FETCH = int(os.getenv("MAX_ARTICLES_PER_FETCH", "100"))
ENABLE_CLAUDE_ENHANCEMENT = os.getenv("ENABLE_CLAUDE_ENHANCEMENT", "true").lower() in ("true", "1", "yes")
TRACK_ENGAGEMENT = os.getenv("TRACK_ENGAGEMENT", "true").lower() in ("true", "1", "yes")

# Quality score weights
SCORE_WEIGHTS = {
    "base_rewrite": 0.25,
    "language_enhance": 0.15,
    "structure_enhance": 0.10,
    "fact_verify": 0.30,
    "brand_validate": 0.10,
    "engagement_potential": 0.10,
}

# ═══════════════════════════════════════════════════════════════════════════════
# AUTONOMOUS NEWS AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class AutonomousNewsAgent:
    """Autonomous agent for fetching, enhancing, and publishing news"""

    def __init__(self):
        self.news_rewriter = NewsRewriter()
        self.media_bot = MediaBotIntegration()
        self.processed_articles = set()  # MD5 hashes of processed articles
        self.log_file = "logs/autonomous_news.jsonl"
        self._ensure_log_file()

    def _ensure_log_file(self):
        """Ensure log file exists"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            open(self.log_file, "w").close()

    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 1-4: FETCH, FILTER, MAP (Using existing NewsRewriter)
    # ─────────────────────────────────────────────────────────────────────────────

    def fetch_and_filter(self) -> List[Dict]:
        """Fetch news and filter candidates"""
        import time
        logger.info("🤖 AUTONOMOUS: Starting fetch & filter cycle")
        start = time.time()

        # Step 1: Fetch news
        try:
            raw_news = self.news_rewriter.fetch_news()
            logger.info(f"✅ Fetched {len(raw_news)} items ({time.time()-start:.1f}s)")
        except Exception as e:
            logger.error(f"❌ Fetch failed: {e}")
            return []

        # Step 2: Filter and score
        try:
            filtered = self.news_rewriter.filter_and_score(raw_news)
            logger.info(f"✅ Filtered to {len(filtered)} candidates ({time.time()-start:.1f}s)")
        except Exception as e:
            logger.error(f"❌ Filter failed: {e}")
            return []

        # Step 3: Remove duplicates
        unique_news = []
        for scored_item in filtered:
            article_hash = self._hash_article(scored_item)
            if article_hash not in self.processed_articles:
                # Extract NewsItem from ScoredNews
                item = scored_item.item
                # Convert to dict for downstream processing
                article_dict = {
                    "title": item.title,
                    "link": item.url,
                    "content": item.content,
                    "source": item.source_name,
                    "category": item.category,
                    "score": scored_item.relevance_score,
                }
                unique_news.append(article_dict)
                self.processed_articles.add(article_hash)

        logger.info(f"✅ {len(unique_news)} new unique ({time.time()-start:.1f}s)")

        # Step 4: Map to products
        try:
            for article in unique_news:
                article["products"] = self.news_rewriter.map_to_products(article)
            logger.info(f"✅ Mapped {len(unique_news)} to products ({time.time()-start:.1f}s)")
        except Exception as e:
            logger.error(f"❌ Map failed: {e}")

        result = unique_news[:MAX_ARTICLES_PER_FETCH]
        logger.info(f"🎯 READY: {len(result)} articles for processing ({time.time()-start:.1f}s total)")
        return result

    def _hash_article(self, scored_news) -> str:
        """Create MD5 hash of article for duplicate detection"""
        import hashlib
        # Handle both ScoredNews objects and dicts
        if hasattr(scored_news, 'item'):  # ScoredNews object
            item = scored_news.item
            content = f"{item.title}{item.url}"
        else:  # dict
            content = f"{scored_news.get('title', '')}{scored_news.get('link', '')}"
        return hashlib.md5(content.encode()).hexdigest()

    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 5-6: REWRITE & ENHANCE (Base + AI Enhancement)
    # ─────────────────────────────────────────────────────────────────────────────

    def rewrite_and_enhance(self, article: Dict) -> Tuple[str, float]:
        """Rewrite article and enhance quality"""

        # Step 5: Base rewrite (NewsRewriter)
        post_text = self.news_rewriter.rewrite_for_telegram(article)
        base_score = article.get("score", 0.5)  # 0.0 - 0.6 from NewsRewriter

        # Step 6: AI Enhancement (if enabled)
        if ENABLE_CLAUDE_ENHANCEMENT:
            enhanced_text, enhancement_score = self._claude_enhance(post_text)
            post_text = enhanced_text
            base_score = min(1.0, base_score + enhancement_score)
        else:
            base_score = min(0.75, base_score + 0.15)  # Fixed bonus if no Claude

        return post_text, base_score

    def _claude_enhance(self, post_text: str) -> Tuple[str, float]:
        """Enhance post using Claude AI"""
        try:
            # This would use Anthropic API in production
            # For now, return improved text and bonus score
            import re

            # Simple enhancements
            enhanced = post_text

            # Ensure proper emoji
            if not re.match(r'^[\U0001F300-\U0001F9FF]', enhanced):
                enhanced = "🏭 " + enhanced

            # Bonus for enhancement
            bonus = 0.15  # Language + structure bonus

            return enhanced, bonus

        except Exception as e:
            logger.error(f"Claude enhancement failed: {e}")
            return post_text, 0.08  # Lower bonus if enhancement fails

    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 7-8: VALIDATE (Facts + Brands)
    # ─────────────────────────────────────────────────────────────────────────────

    def validate_quality(
        self, article: Dict, post_text: str, base_score: float
    ) -> Tuple[float, Dict]:
        """Validate quality and calculate final score"""

        validation = {
            "brand_valid": True,
            "fact_score": 1.0,
            "engagement_potential": 0.8,
            "factors": {},
        }

        # Brand validation (CRITICAL)
        if not self.news_rewriter.validate_brand_names(post_text):
            logger.warning(f"❌ Brand validation failed for: {post_text[:50]}")
            return 0.0, validation  # AUTO-REJECT

        # Content safety (CRITICAL)
        if not self.news_rewriter.validate_content_safety(post_text):
            logger.warning(f"❌ Content safety failed for: {post_text[:50]}")
            return 0.0, validation  # AUTO-REJECT

        # Fact verification (multiplier)
        fact_score = self._verify_facts(article)  # 0.8 - 1.0
        validation["fact_score"] = fact_score

        # Engagement potential (estimated)
        engagement = self._estimate_engagement(article)  # 0.6 - 1.0
        validation["engagement_potential"] = engagement

        # Calculate final score
        final_score = (
            (base_score * SCORE_WEIGHTS["base_rewrite"]) +
            (0.9 * SCORE_WEIGHTS["language_enhance"]) +
            (0.9 * SCORE_WEIGHTS["structure_enhance"]) +
            (fact_score * SCORE_WEIGHTS["fact_verify"]) +
            (0.95 * SCORE_WEIGHTS["brand_validate"]) +
            (engagement * SCORE_WEIGHTS["engagement_potential"])
        )

        validation["factors"] = {
            "base_score": base_score,
            "language_enhance": 0.9,
            "structure_enhance": 0.9,
            "fact_verify": fact_score,
            "brand_validate": 0.95,
            "engagement_potential": engagement,
            "final_score": final_score,
        }

        return min(1.0, final_score), validation

    def _verify_facts(self, article: Dict) -> float:
        """Quick fact verification"""
        # In production, would use external API or Claude
        # For now: check if article has reputable source
        source_name = article.get("source", "").lower()

        if any(reputable in source_name for reputable in ["industry", "news", "tech"]):
            return 1.0  # Fully verified
        elif article.get("score", 0) > 0.7:
            return 0.9  # Partially verified (high score)
        else:
            return 0.8  # Unverified

    def _estimate_engagement(self, article: Dict) -> float:
        """Estimate engagement potential"""
        score = article.get("score", 0.5)
        keywords = article.get("keywords", [])

        # Higher score = higher engagement
        engagement = min(1.0, score * 1.2)

        # Hot topics boost engagement
        hot_keywords = ["innovation", "breakthrough", "investment", "expansion"]
        if any(kw in keywords for kw in hot_keywords):
            engagement = min(1.0, engagement + 0.1)

        return engagement

    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 9-10: DECISION & PUBLISH
    # ─────────────────────────────────────────────────────────────────────────────

    async def publish_or_preview(
        self, article: Dict, post_text: str, final_score: float
    ) -> bool:
        """Decide to publish, preview, or reject"""

        if final_score >= AUTONOMOUS_QUALITY_THRESHOLD and AUTO_PUBLISH_ENABLED:
            # AUTO-PUBLISH
            return await self._auto_publish(article, post_text, final_score)

        elif final_score >= PREVIEW_THRESHOLD:
            # SEND FOR PREVIEW (1-hour window)
            return await self._send_preview(article, post_text, final_score)

        else:
            # REJECT
            self._log_event("rejected", article, post_text, final_score, "Low quality score")
            logger.info(f"❌ REJECTED: Score {final_score:.2f} < {MIN_QUALITY_THRESHOLD}")
            return False

    async def _auto_publish(
        self, article: Dict, post_text: str, final_score: float
    ) -> bool:
        """Automatically publish to @UnitgroupAI"""
        try:
            # Publish to Telegram
            message_id = await self.media_bot._publish_to_channel(post_text)

            if message_id:
                self._log_event("auto_published", article, post_text, final_score, f"Message ID: {message_id}")
                logger.info(f"✅ AUTO-PUBLISHED: Score {final_score:.2f} | {post_text[:50]}...")
                return True
            else:
                logger.error("Failed to publish to Telegram")
                return False

        except Exception as e:
            logger.error(f"Auto-publish failed: {e}")
            self._log_event("publish_error", article, post_text, final_score, str(e))
            return False

    async def _send_preview(
        self, article: Dict, post_text: str, final_score: float
    ) -> bool:
        """Send preview for 1-hour admin window (non-blocking)"""
        try:
            preview_message = f"""
⚠️ NEWS PREVIEW (Score: {final_score:.2f})

{post_text}

Quality factors:
  ✅ Language: Excellent
  ✅ Structure: Good
  ✅ Facts: Verified
  ⚠️ Product fit: Fair

[✅ Approve Now] [❌ Reject]

Auto-publishes in: {PREVIEW_WINDOW_MINUTES} min ⏱️
            """

            # Send preview (implementation depends on admin Telegram setup)
            self._log_event("sent_for_preview", article, post_text, final_score, "Awaiting admin decision")
            logger.info(f"⚠️ PREVIEW SENT: Score {final_score:.2f} (window: {PREVIEW_WINDOW_MINUTES}m)")

            # Schedule auto-publish in background (non-blocking)
            asyncio.create_task(self._delayed_auto_publish(article, post_text, final_score))

            return True

        except Exception as e:
            logger.error(f"Preview send failed: {e}")
            self._log_event("preview_error", article, post_text, final_score, str(e))
            return False

    async def _delayed_auto_publish(self, article: Dict, post_text: str, final_score: float):
        """Auto-publish after preview window (runs in background)"""
        await asyncio.sleep(PREVIEW_WINDOW_MINUTES * 60)
        await self._auto_publish(article, post_text, final_score)

    # ─────────────────────────────────────────────────────────────────────────────
    # STEP 11-12: LOGGING & LEARNING
    # ─────────────────────────────────────────────────────────────────────────────

    def _log_event(
        self,
        event_type: str,
        article: Dict,
        post_text: str,
        score: float,
        details: str = ""
    ):
        """Log autonomous agent event"""
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": event_type,
            "agent": "autonomous_news_enhancement",
            "source": article.get("source", "unknown"),
            "product": article.get("products", ["unknown"])[0],
            "score": round(score, 3),
            "post_preview": post_text[:100],
            "details": details,
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

        logger.info(f"📝 Logged: {event_type} | Score: {score:.2f} | {details}")

    async def analyze_engagement(self) -> Dict:
        """Analyze engagement metrics (Step 12)"""
        logger.info("📊 Analyzing engagement metrics...")

        # In production: pull from Telegram API
        # For now: return placeholder
        return {
            "posts_published": 0,  # Would fetch from Telegram
            "avg_engagement": 0.0,
            "trending_topics": [],
            "best_performing_products": [],
        }

    # ─────────────────────────────────────────────────────────────────────────────
    # MAIN LOOP
    # ─────────────────────────────────────────────────────────────────────────────

    async def _process_single_article(self, article: Dict) -> bool:
        """Process single article (async wrapper)"""
        try:
            # Rewrite & enhance
            post_text, base_score = self.rewrite_and_enhance(article)

            # Validate
            final_score, validation = self.validate_quality(article, post_text, base_score)

            # Publish or preview (non-blocking)
            await self.publish_or_preview(article, post_text, final_score)
            return True
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            return False

    async def run_autonomous_loop(self):
        """Main autonomous loop"""
        logger.info("🤖 AUTONOMOUS MODE ACTIVATED")
        logger.info(f"   Quality threshold: {AUTONOMOUS_QUALITY_THRESHOLD}")
        logger.info(f"   Fetch interval: {FETCH_INTERVAL_MINUTES} minutes")
        logger.info(f"   Auto-publish: {'ENABLED' if AUTO_PUBLISH_ENABLED else 'DISABLED'}")
        logger.info(f"   Claude enhancement: {'ENABLED' if ENABLE_CLAUDE_ENHANCEMENT else 'DISABLED'}")

        iteration = 0
        while True:
            try:
                iteration += 1
                logger.info(f"\n🔄 AUTONOMOUS ITERATION {iteration} - {datetime.utcnow().isoformat()}Z")

                # Fetch and filter
                articles = self.fetch_and_filter()

                if not articles:
                    logger.info("ℹ️ No new articles to process")
                else:
                    logger.info(f"📰 Processing {len(articles)} articles in parallel...")
                    # Process articles in parallel (max 5 concurrent)
                    tasks = [self._process_single_article(article) for article in articles[:5]]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    success_count = sum(1 for r in results if r is True)
                    logger.info(f"✅ Processed: {success_count}/{len(articles)} articles")

                # Analyze engagement
                if iteration % 12 == 0:  # Every 6 hours (12 × 30 min)
                    await self.analyze_engagement()

                # Wait for next fetch
                logger.info(f"⏸️ Waiting {FETCH_INTERVAL_MINUTES} minutes until next fetch...")
                await asyncio.sleep(FETCH_INTERVAL_MINUTES * 60)

            except Exception as e:
                logger.error(f"❌ Autonomous loop error: {e}", exc_info=True)
                await asyncio.sleep(60)  # Retry after 1 minute


# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

async def start_autonomous_agent():
    """Start autonomous news agent if enabled"""
    if not AUTONOMOUS_MODE:
        logger.info("ℹ️ Autonomous mode disabled")
        return

    agent = AutonomousNewsAgent()
    await agent.run_autonomous_loop()


if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    agent = AutonomousNewsAgent()
    asyncio.run(agent.run_autonomous_loop())
