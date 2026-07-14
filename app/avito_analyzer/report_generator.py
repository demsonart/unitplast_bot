"""
Report generator for Avito analyzer results
Formats analysis into readable reports for Telegram
"""

import logging
import json
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates formatted reports for Telegram.
    """

    def generate_telegram_report(self,
                                 competitor_analysis: Dict[str, Any],
                                 advert_analysis: Dict[str, Any],
                                 campaign_strategy: Dict[str, Any]) -> str:
        """
        Generate complete analysis report for Telegram.

        Args:
            competitor_analysis: Results from CompetitorAnalyzer
            advert_analysis: Results from ClaudeAnalyzer
            campaign_strategy: Results from RKStrategist

        Returns:
            Formatted HTML message for Telegram
        """
        try:
            timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")

            # Build report sections
            sections = []

            # Header
            sections.append(
                f"<b>📊 AVITO ANALYZER - Автоматический отчет</b>\n"
                f"<i>{timestamp}</i>\n"
            )

            # Market analysis
            sections.append(self._format_market_analysis(competitor_analysis))

            # Advert recommendations
            sections.append(self._format_advert_recommendations(advert_analysis))

            # Campaign strategy
            sections.append(self._format_campaign_strategy(campaign_strategy))

            # Footer
            sections.append(
                f"\n✅ <b>Статус:</b> Готово\n"
                f"📋 Следующий анализ: автоматически в указанное время"
            )

            return "\n".join(sections)

        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return f"❌ Ошибка при генерации отчета: {str(e)}"

    @staticmethod
    def _format_market_analysis(competitor_analysis: Dict[str, Any]) -> str:
        """Format market analysis section."""
        total = competitor_analysis.get("total_found", 0)
        successful = competitor_analysis.get("successful_count", 0)
        avg_score = competitor_analysis.get("average_score", 0)

        return (
            f"\n<b>🔍 АНАЛИЗ РЫНКА</b>\n"
            f"📈 Найдено объявлений: <code>{total}</code>\n"
            f"⭐ Успешных объявлений: <code>{successful}</code>\n"
            f"📊 Средний скор: <code>{avg_score:.1f}/100</code>\n"
            f"{'✅ Рынок активен' if avg_score > 70 else '⚠️ Умеренная активность' if avg_score > 50 else '❌ Низкая активность'}"
        )

    @staticmethod
    def _format_advert_recommendations(advert_analysis: Dict[str, Any]) -> str:
        """Format advert analysis and recommendations."""
        if advert_analysis.get("status") != "success":
            return "\n<b>⚠️ РЕКОМЕНДАЦИИ ПО ОБЪЯВЛЕНИЮ</b>\n❌ Ошибка при анализе"

        analysis = advert_analysis.get("analysis", {})

        report = "\n<b>💡 РЕКОМЕНДАЦИИ ПО ОБЪЯВЛЕНИЮ</b>\n"

        # Title pattern
        if "title_pattern" in analysis:
            report += f"📝 <b>Структура заголовка:</b>\n{analysis['title_pattern']}\n"

        # Key phrases
        if "key_phrases" in analysis:
            phrases = ", ".join(analysis.get("key_phrases", [])[:5])
            report += f"🔑 <b>Ключевые фразы:</b> {phrases}\n"

        # Price strategy
        if "price_strategy" in analysis:
            report += f"💰 <b>Ценовая стратегия:</b> {analysis['price_strategy']}\n"

        # Photo requirements
        if "photo_requirements" in analysis:
            report += f"📸 <b>Требования к фото:</b> {analysis['photo_requirements']}\n"

        # Critical success factors
        if "critical_success_factors" in analysis:
            report += "<b>⚡ Критические факторы успеха:</b>\n"
            for factor in analysis.get("critical_success_factors", [])[:3]:
                report += f"  • {factor}\n"

        return report

    @staticmethod
    def _format_campaign_strategy(campaign_strategy: Dict[str, Any]) -> str:
        """Format RK strategy section."""
        if not campaign_strategy:
            return "\n<b>📋 СТРАТЕГИЯ РК</b>\n❌ Ошибка при планировании"

        budget = campaign_strategy.get("total_budget_rubles", 0)
        allocation = campaign_strategy.get("budget_allocation", {})
        kpis = campaign_strategy.get("kpis", {})
        recommendations = campaign_strategy.get("recommendations", [])

        report = f"\n<b>📋 СТРАТЕГИЯ РК (Рекламной Кампании)</b>\n"
        report += f"💵 <b>Бюджет:</b> <code>{budget:,.0f} руб/месяц</code>\n"
        report += f"⏳ <b>Период:</b> 30 дней\n"

        # Budget phases
        report += "\n<b>📊 Распределение бюджета:</b>\n"
        report += f"  1️⃣ Запуск (7 дн): <code>{allocation.get('phase_1_launch_7days', {}).get('amount', 0):,.0f} руб</code>\n"
        report += f"  2️⃣ Оптимизация (15 дн): <code>{allocation.get('phase_2_optimization_15days', {}).get('amount', 0):,.0f} руб</code>\n"
        report += f"  3️⃣ Масштабирование (8 дн): <code>{allocation.get('phase_3_scaling_8days', {}).get('amount', 0):,.0f} руб</code>\n"

        # KPIs
        report += "\n<b>🎯 Целевые метрики:</b>\n"
        if "views_daily" in kpis:
            views = kpis["views_daily"].get("target", 0)
            report += f"  👀 Просмотры/день: <code>{views:.0f}</code>\n"
        if "responses_daily" in kpis:
            responses = kpis["responses_daily"].get("target", 0)
            report += f"  💬 Отклики/день: <code>{responses:.0f}</code>\n"
        if "roi" in kpis:
            roi = kpis["roi"].get("target", 0)
            report += f"  📈 ROI цель: <code>{roi:.1f}x</code>\n"

        # Recommendations
        report += "\n<b>✨ Рекомендации:</b>\n"
        for i, rec in enumerate(recommendations[:5], 1):
            report += f"  {i}. {rec}\n"

        return report

    @staticmethod
    def format_error_report(error_msg: str) -> str:
        """Format error report."""
        return (
            f"❌ <b>ОШИБКА АНАЛИЗА</b>\n"
            f"<code>{error_msg}</code>\n\n"
            f"Попробуй позже или проверь конфигурацию."
        )

    @staticmethod
    def format_json_report(data: Dict[str, Any]) -> str:
        """Format raw JSON report for debugging."""
        return (
            f"<b>📋 Детальные данные анализа</b>\n"
            f"<pre>{json.dumps(data, ensure_ascii=False, indent=2)[:2000]}</pre>"
        )
