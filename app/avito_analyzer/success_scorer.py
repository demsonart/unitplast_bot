"""
Success scorer for Avito advertisements
Calculates composite success metric based on seller rating, reviews, activity
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class SuccessScorer:
    """
    Calculates success score for adverts based on multiple factors.

    Score components:
    - Seller rating (40%): higher rating = more trustworthy
    - Review count (30%): more reviews = more activity/success
    - Activity days (20%): longer active = sustained demand
    - Response speed (10%): faster response = professional seller
    """

    # Weights for score components
    WEIGHTS = {
        "rating": 0.40,
        "reviews": 0.30,
        "activity": 0.20,
        "response": 0.10,
    }

    # Thresholds for normalization
    MIN_RATING = 1.0
    MAX_RATING = 5.0
    MIN_REVIEWS = 0
    MAX_REVIEWS = 1000
    MIN_ACTIVITY_DAYS = 0
    MAX_ACTIVITY_DAYS = 365
    MIN_RESPONSE_HOURS = 0
    MAX_RESPONSE_HOURS = 72

    def calculate_score(self, advert: Dict[str, Any]) -> float:
        """
        Calculate success score for a single advert.

        Args:
            advert: Dictionary with advert data from Avito API
                Expected keys: seller_rating, review_count, created_at, response_time_hours

        Returns:
            Normalized score from 0 to 100
        """
        try:
            # Extract metrics (with fallbacks)
            rating = advert.get("seller_rating", self.MIN_RATING)
            reviews = advert.get("review_count", self.MIN_REVIEWS)
            created_at = advert.get("created_at")
            response_hours = advert.get("response_time_hours", self.MAX_RESPONSE_HOURS)

            # Calculate activity days
            activity_days = self._calculate_activity_days(created_at)

            # Normalize each component (0-1 scale)
            rating_norm = self._normalize(rating, self.MIN_RATING, self.MAX_RATING)
            reviews_norm = self._normalize(reviews, self.MIN_REVIEWS, self.MAX_REVIEWS)
            activity_norm = self._normalize(activity_days, self.MIN_ACTIVITY_DAYS, self.MAX_ACTIVITY_DAYS)
            response_norm = 1 - self._normalize(response_hours, self.MIN_RESPONSE_HOURS, self.MAX_RESPONSE_HOURS)

            # Calculate weighted score
            weighted_score = (
                rating_norm * self.WEIGHTS["rating"] +
                reviews_norm * self.WEIGHTS["reviews"] +
                activity_norm * self.WEIGHTS["activity"] +
                response_norm * self.WEIGHTS["response"]
            )

            # Convert to 0-100 scale
            return round(weighted_score * 100, 2)

        except Exception as e:
            logger.error(f"Error calculating score for advert: {e}")
            return 0.0

    def rank_adverts(self, adverts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank adverts by success score in descending order.

        Args:
            adverts: List of advert dictionaries

        Returns:
            Sorted list with added 'success_score' field
        """
        scored = []

        for advert in adverts:
            score = self.calculate_score(advert)
            advert_with_score = {**advert, "success_score": score}
            scored.append(advert_with_score)

        return sorted(scored, key=lambda x: x["success_score"], reverse=True)

    def filter_successful(self, adverts: List[Dict[str, Any]],
                         threshold: float = 50.0) -> List[Dict[str, Any]]:
        """
        Filter adverts above success threshold.

        Args:
            adverts: List of adverts
            threshold: Minimum success score (0-100)

        Returns:
            Filtered and ranked list
        """
        ranked = self.rank_adverts(adverts)
        return [a for a in ranked if a["success_score"] >= threshold]

    @staticmethod
    def _normalize(value: float, min_val: float, max_val: float) -> float:
        """Normalize value to 0-1 range."""
        if max_val == min_val:
            return 0.0
        return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

    @staticmethod
    def _calculate_activity_days(created_at: str) -> int:
        """Calculate days since advert was created."""
        try:
            if not created_at:
                return 0

            # Try ISO format first
            try:
                date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                # Fallback to other formats
                date = datetime.strptime(created_at, "%Y-%m-%d")

            delta = datetime.now(date.tzinfo) - date if date.tzinfo else datetime.now() - date.replace(tzinfo=None)
            return delta.days

        except Exception as e:
            logger.warning(f"Could not parse date {created_at}: {e}")
            return 0
