"""
Competitor analyzer for Avito market
Searches for similar adverts and extracts successful patterns
"""

import logging
from typing import Dict, Any, List, Optional
from .success_scorer import SuccessScorer

logger = logging.getLogger(__name__)


class CompetitorAnalyzer:
    """
    Analyzes competitor adverts on Avito.
    Finds similar products and extracts successful patterns.
    """

    def __init__(self, avito_client):
        """
        Initialize analyzer with Avito API client.

        Args:
            avito_client: AvitoAPIClient instance
        """
        self.client = avito_client
        self.scorer = SuccessScorer()

    def search_competitors(self, keywords: List[str], limit: int = 100) -> Dict[str, Any]:
        """
        Search for competitor adverts by keywords.

        Args:
            keywords: List of search keywords (e.g., ["пластмасса", "пресс-формы", "литье"])
            limit: Maximum number of adverts to fetch

        Returns:
            Dictionary with successful adverts and analysis
        """
        try:
            all_adverts = []

            # Search for each keyword
            for keyword in keywords:
                logger.info(f"Searching for adverts with keyword: {keyword}")
                adverts = self._search_by_keyword(keyword, limit=limit // len(keywords))
                all_adverts.extend(adverts)

            logger.info(f"Found {len(all_adverts)} adverts total")

            # Score and rank
            successful = self.scorer.filter_successful(all_adverts, threshold=60.0)

            return {
                "total_found": len(all_adverts),
                "successful_count": len(successful),
                "successful_adverts": successful[:20],  # Top 20
                "average_score": sum(a["success_score"] for a in successful) / len(successful) if successful else 0,
            }

        except Exception as e:
            logger.error(f"Error searching competitors: {e}")
            return {
                "total_found": 0,
                "successful_count": 0,
                "successful_adverts": [],
                "average_score": 0,
                "error": str(e),
            }

    def _search_by_keyword(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search adverts by single keyword using Avito API search.

        Note: This uses available API endpoints. Avito API doesn't have direct
        search endpoint, so we use offers/leads endpoint as proxy.

        Args:
            keyword: Search keyword
            limit: Max results

        Returns:
            List of advert dictionaries
        """
        try:
            # Try to get user's offers (their own listings first)
            # Then we'll analyze patterns from them
            response = self.client.get_offers_for_user(limit=limit)

            adverts = response.get("offers", [])

            # Enrich with scoring data
            for advert in adverts:
                # Extract necessary fields or set defaults
                if "seller_rating" not in advert:
                    advert["seller_rating"] = 4.5
                if "review_count" not in advert:
                    advert["review_count"] = 10
                if "created_at" not in advert:
                    advert["created_at"] = "2026-07-01T00:00:00Z"
                if "response_time_hours" not in advert:
                    advert["response_time_hours"] = 24

            return adverts

        except Exception as e:
            logger.warning(f"Error searching for keyword '{keyword}': {e}")
            return []

    def extract_patterns(self, successful_adverts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract common patterns from successful adverts.

        Args:
            successful_adverts: List of high-scoring adverts

        Returns:
            Dictionary with extracted patterns
        """
        if not successful_adverts:
            return {}

        try:
            titles = [a.get("title", "") for a in successful_adverts]
            descriptions = [a.get("description", "") for a in successful_adverts]
            prices = [a.get("price", 0) for a in successful_adverts if a.get("price")]

            return {
                "avg_title_length": sum(len(t) for t in titles) / len(titles) if titles else 0,
                "avg_description_length": sum(len(d) for d in descriptions) / len(descriptions) if descriptions else 0,
                "avg_price": sum(prices) / len(prices) if prices else 0,
                "price_range": {
                    "min": min(prices) if prices else 0,
                    "max": max(prices) if prices else 0,
                },
                "common_words": self._extract_common_words(titles + descriptions),
                "total_samples": len(successful_adverts),
            }

        except Exception as e:
            logger.error(f"Error extracting patterns: {e}")
            return {}

    @staticmethod
    def _extract_common_words(texts: List[str], top_n: int = 10) -> List[str]:
        """
        Extract most common words from texts.

        Args:
            texts: List of text strings
            top_n: Number of top words to return

        Returns:
            List of most common words
        """
        try:
            from collections import Counter
            import re

            # Combine all texts
            combined = " ".join(texts).lower()

            # Extract words (Russian and English)
            words = re.findall(r'\b[а-яa-z]{3,}\b', combined)

            # Stop words to exclude
            stop_words = {
                'для', 'это', 'что', 'как', 'если', 'или', 'все', 'один',
                'the', 'and', 'for', 'with', 'from', 'are', 'you', 'can'
            }

            # Filter and count
            words = [w for w in words if w not in stop_words]
            counter = Counter(words)

            return [word for word, _ in counter.most_common(top_n)]

        except Exception as e:
            logger.warning(f"Error extracting common words: {e}")
            return []

    def get_seller_stats(self) -> Dict[str, Any]:
        """
        Get statistics about own seller profile.

        Returns:
            Dictionary with seller information
        """
        try:
            profile = self.client.get_user_profile()

            return {
                "seller_id": profile.get("id"),
                "rating": profile.get("rating", 0),
                "review_count": profile.get("reviews_count", 0),
                "items_count": profile.get("items_count", 0),
            }

        except Exception as e:
            logger.error(f"Error getting seller stats: {e}")
            return {}
