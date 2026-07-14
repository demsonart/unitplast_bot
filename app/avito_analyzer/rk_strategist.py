"""
RK (Advertising Campaign) Strategist
Generates campaign strategy and recommendations based on market analysis
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, time

logger = logging.getLogger(__name__)


class RKStrategist:
    """
    Generates advertising campaign strategy.
    """

    def __init__(self):
        """Initialize strategist."""
        pass

    def generate_campaign_strategy(self,
                                   competitor_analysis: Dict[str, Any],
                                   advert_analysis: Dict[str, Any],
                                   budget_rubles: float = 5000.0) -> Dict[str, Any]:
        """
        Generate complete RK strategy.

        Args:
            competitor_analysis: Results from CompetitorAnalyzer
            advert_analysis: Results from ClaudeAnalyzer
            budget_rubles: Monthly budget in rubles

        Returns:
            Campaign strategy dictionary
        """
        try:
            # Get market metrics
            avg_score = competitor_analysis.get("average_score", 0)
            successful_count = competitor_analysis.get("successful_count", 0)

            # Calculate campaign parameters
            budget_allocation = self._allocate_budget(budget_rubles)
            optimal_hours = self._get_optimal_posting_hours()
            target_audience = self._define_target_audience(advert_analysis)
            kpis = self._define_kpis(avg_score, successful_count)

            return {
                "campaign_period_days": 30,
                "total_budget_rubles": budget_rubles,
                "budget_allocation": budget_allocation,
                "target_audience": target_audience,
                "optimal_posting_hours": optimal_hours,
                "recommended_rotation": self._get_advert_rotation(),
                "kpis": kpis,
                "risk_factors": self._identify_risks(),
                "recommendations": self._get_recommendations(avg_score, successful_count),
            }

        except Exception as e:
            logger.error(f"Error generating campaign strategy: {e}")
            return {}

    def _allocate_budget(self, total_budget: float) -> Dict[str, Any]:
        """
        Allocate budget across channels and phases.

        Args:
            total_budget: Total budget in rubles

        Returns:
            Budget allocation dictionary
        """
        return {
            "phase_1_launch_7days": {
                "amount": total_budget * 0.40,
                "goal": "максимальная видимость, сбор статистики",
            },
            "phase_2_optimization_15days": {
                "amount": total_budget * 0.35,
                "goal": "оптимизация под лучшие ключевые слова",
            },
            "phase_3_scaling_8days": {
                "amount": total_budget * 0.25,
                "goal": "масштабирование лучших вариантов",
            },
            "daily_average": round(total_budget / 30, 2),
        }

    @staticmethod
    def _get_optimal_posting_hours() -> Dict[str, Any]:
        """
        Get optimal times for posting adverts.

        Returns:
            Posting schedule
        """
        return {
            "primary_slots": [
                {"time": "09:00-10:00", "rationale": "начало рабочего дня, высокая активность"},
                {"time": "13:00-14:00", "rationale": "обеденный перерыв, пик активности"},
                {"time": "17:00-18:00", "rationale": "конец рабочего дня"},
            ],
            "days_to_emphasize": ["Вторник", "Среда", "Четверг"],
            "days_to_reduce": ["Суббота", "Воскресенье"],
        }

    @staticmethod
    def _define_target_audience(advert_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define target audience based on analysis.

        Args:
            advert_analysis: Analysis results

        Returns:
            Target audience profile
        """
        return {
            "primary": {
                "segment": "B2B производители",
                "characteristics": ["заводы", "производственные компании", "поставщики"],
                "location": "Россия, фокус на Москву и ЦФО",
                "budget": "средний и высокий",
                "intent": "закупка сырья и оборудования",
            },
            "secondary": {
                "segment": "Оптовые покупатели",
                "characteristics": ["переторговцы", "дилеры", "интернет-магазины"],
                "location": "Россия",
                "budget": "средний",
            },
            "tertiary": {
                "segment": "Розничные покупатели",
                "characteristics": ["предприниматели", "мастерские"],
                "location": "Москва и МО",
                "budget": "низкий-средний",
            },
        }

    @staticmethod
    def _get_advert_rotation() -> Dict[str, Any]:
        """
        Get advert rotation strategy.

        Returns:
            Rotation recommendations
        """
        return {
            "rotation_frequency_hours": 4,
            "variant_count": 3,
            "variants": [
                {
                    "type": "premium",
                    "description": "выделенное объявление с фото",
                    "investment_percent": 50,
                },
                {
                    "type": "standard",
                    "description": "стандартное объявление",
                    "investment_percent": 30,
                },
                {
                    "type": "text_light",
                    "description": "облегченный вариант с минимумом фото",
                    "investment_percent": 20,
                },
            ],
            "split_test_duration_days": 7,
        }

    @staticmethod
    def _define_kpis(avg_score: float, successful_count: int) -> Dict[str, Any]:
        """
        Define KPIs for campaign.

        Args:
            avg_score: Average success score of competitors
            successful_count: Number of successful adverts found

        Returns:
            KPI definitions
        """
        # Estimate targets based on market data
        target_views_daily = max(50, successful_count * 3)
        target_responses_daily = max(5, target_views_daily * 0.1)

        return {
            "views_daily": {
                "target": target_views_daily,
                "success_threshold": target_views_daily * 0.8,
            },
            "responses_daily": {
                "target": target_responses_daily,
                "success_threshold": target_responses_daily * 0.8,
            },
            "ctr": {
                "target": 0.15,
                "unit": "15%",
                "success_threshold": 0.12,
            },
            "response_rate": {
                "target": 0.12,
                "unit": "12% of views",
                "success_threshold": 0.10,
            },
            "conversion_rate": {
                "target": 0.05,
                "unit": "5% of responses to deals",
                "success_threshold": 0.03,
            },
            "roi": {
                "target": 3.0,
                "unit": "3x (каждый рубль инвестиции дает 3 рубля дохода)",
                "success_threshold": 1.5,
            },
        }

    @staticmethod
    def _identify_risks() -> List[Dict[str, str]]:
        """Identify potential risks in campaign."""
        return [
            {
                "risk": "высокая конкуренция",
                "mitigation": "уникальное позиционирование, выделение преимуществ",
            },
            {
                "risk": "сезонность спроса",
                "mitigation": "адаптация бюджета в зависимости от сезона",
            },
            {
                "risk": "нестабильность цен",
                "mitigation": "гибкая ценовая стратегия, мониторинг конкурентов",
            },
            {
                "risk": "качество контактов",
                "mitigation": "фильтрация лидов по критериям, quick response",
            },
        ]

    @staticmethod
    def _get_recommendations(avg_score: float, successful_count: int) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []

        if avg_score > 70:
            recommendations.append("✅ Рынок активен - хорошие условия для входа")
        else:
            recommendations.append("⚠️ Рынок имеет среднюю активность - требуется особое внимание к выделению")

        if successful_count > 20:
            recommendations.append("📊 Много конкурентов - фокусируйся на уникальности")
        else:
            recommendations.append("🎯 Низкая конкуренция - возможность захватить долю рынка")

        recommendations.extend([
            "📝 Используй результаты анализа Claude для оптимальной структуры объявления",
            "🔄 Ротируй варианты объявлений каждые 4 часа",
            "⏰ Размещай объявления в пиковые часы (9:00, 13:00, 17:00)",
            "📈 Отслеживай метрики ежедневно и адаптируй стратегию",
            "💬 Отвечай на все входящие сообщения в течение 1 часа",
        ])

        return recommendations
