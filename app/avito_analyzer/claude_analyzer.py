"""
Claude-powered analyzer for deep text analysis
Uses Claude API to extract insights from successful adverts
"""

import logging
import json
from typing import Dict, Any, List
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudeAnalyzer:
    """
    Uses Claude API to analyze successful adverts and generate recommendations.
    """

    def __init__(self, api_key: str):
        """
        Initialize Claude analyzer.

        Args:
            api_key: Anthropic API key
        """
        self.client = Anthropic()
        self.model = "claude-opus-4-8"

    def analyze_adverts(self, successful_adverts: List[Dict[str, Any]],
                       patterns: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze successful adverts using Claude API.

        Args:
            successful_adverts: List of successful advert dictionaries
            patterns: Extracted patterns from competitor analysis

        Returns:
            Analysis results with recommendations
        """
        try:
            # Prepare data for Claude
            advert_summaries = self._prepare_advert_summaries(successful_adverts[:10])

            prompt = f"""Проанализируй успешные объявления пластмассы, пресс-форм и литья на Avito.

УСПЕШНЫЕ ОБЪЯВЛЕНИЯ:
{advert_summaries}

ПАТТЕРНЫ:
- Средняя длина заголовка: {patterns.get('avg_title_length', 0):.0f} символов
- Средняя длина описания: {patterns.get('avg_description_length', 0):.0f} символов
- Средняя цена: {patterns.get('avg_price', 0):.0f} руб
- Диапазон цен: {patterns.get('price_range', {{}}).get('min', 0):.0f} - {patterns.get('price_range', {{}}).get('max', 0):.0f} руб
- Популярные слова: {', '.join(patterns.get('common_words', []))}

ЗАДАЧА: Найди паттерны успеха:
1. Структура заголовков (что привлекает внимание)
2. Ключевые фразы в описаниях
3. Оптимальная ценовая стратегия
4. Требования к фото и визуалу
5. Психологические триггеры (что побуждает к контакту)
6. Рекомендуемая длина текста
7. Оптимальное расположение информации

Дай конкретные, практические рекомендации для создания нового успешного объявления.
Ответь на РУССКОМ языке в формате JSON:
{{
    "title_pattern": "структура оптимального заголовка",
    "title_examples": ["пример1", "пример2"],
    "description_structure": "рекомендуемая структура описания",
    "key_phrases": ["фраза1", "фраза2"],
    "price_strategy": "рекомендация по цене",
    "photo_requirements": "требования к фото",
    "psychological_triggers": ["триггер1", "триггер2"],
    "critical_success_factors": ["фактор1", "фактор2"]
}}
"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Try to parse JSON from response
            try:
                # Extract JSON from response (Claude might add text around it)
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    analysis = json.loads(json_str)
                else:
                    analysis = {"raw_analysis": response_text}
            except json.JSONDecodeError:
                analysis = {"raw_analysis": response_text}

            return {
                "status": "success",
                "analysis": analysis,
                "model": self.model,
            }

        except Exception as e:
            logger.error(f"Error analyzing adverts with Claude: {e}")
            return {
                "status": "error",
                "error": str(e),
                "analysis": {},
            }

    def generate_advert_draft(self, analysis: Dict[str, Any],
                             product_info: str) -> str:
        """
        Generate a complete advert draft based on analysis.

        Args:
            analysis: Analysis results from analyze_adverts()
            product_info: Information about the product to advertise

        Returns:
            Generated advert text
        """
        try:
            prompt = f"""На основе анализа успешных объявлений напиши оптимальное объявление.

АНАЛИЗ УСПЕШНОСТИ:
{json.dumps(analysis.get('analysis', {}), ensure_ascii=False, indent=2)}

ИНФОРМАЦИЯ О ПРОДУКТЕ:
{product_info}

Напиши полное объявление для Avito, включающее:
1. Привлекательный заголовок
2. Структурированное описание
3. Ключевые преимущества
4. Информацию для контакта

Используй все паттерны из анализа. Ответь только на русском языке.
Формат - готовое к публикации объявление.
"""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text

        except Exception as e:
            logger.error(f"Error generating advert draft: {e}")
            return ""

    @staticmethod
    def _prepare_advert_summaries(adverts: List[Dict[str, Any]]) -> str:
        """
        Prepare summaries of adverts for Claude analysis.

        Args:
            adverts: List of advert dictionaries

        Returns:
            Formatted string for Claude
        """
        summaries = []

        for i, advert in enumerate(adverts, 1):
            summary = f"""
{i}. Объявление (скор: {advert.get('success_score', 0):.0f}/100)
Заголовок: {advert.get('title', 'N/A')}
Описание: {advert.get('description', 'N/A')[:200]}...
Цена: {advert.get('price', 'N/A')} руб
Продавец: рейтинг {advert.get('seller_rating', 0)}, {advert.get('review_count', 0)} отзывов
"""
            summaries.append(summary)

        return "\n".join(summaries)
