#!/usr/bin/env python3
"""
Media Integration Pipeline for @UnitgroupAI
Парсинг картинок из источников + AI-генерация как fallback
"""

import os
import json
import requests
from typing import Optional, Tuple
from pathlib import Path
import feedparser
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MediaIntegration:
    """Парсинг и генерация изображений для постов"""

    def __init__(self):
        self.media_cache = Path("data/media_cache")
        self.media_cache.mkdir(exist_ok=True)
        self.dry_run = os.getenv("DRY_RUN", "true").lower() == "true"

    def parse_rss_images(self, rss_url: str, post_keywords: list) -> Optional[str]:
        """
        Парсит RSS-фид и ищет изображения по ключевым словам

        Args:
            rss_url: URL RSS-фида
            post_keywords: Ключевые слова для поиска (например, ["AI", "качество", "мебель"])

        Returns:
            URL картинки или None
        """
        try:
            logger.info(f"📡 Парсим RSS: {rss_url}")
            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:10]:  # Ищем в первых 10 записях
                # Проверяем есть ли ключевые слова в заголовке/описании
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()

                keywords_match = sum(1 for kw in post_keywords if kw.lower() in title or kw.lower() in summary)

                if keywords_match >= 2:  # Минимум 2 совпадения
                    # Ищем изображения в Entry
                    if 'media_content' in entry:
                        for media in entry.media_content:
                            if media.get('type', '').startswith('image'):
                                img_url = media.get('url')
                                logger.info(f"✅ Найдена картинка: {img_url}")
                                return img_url

                    # Ищем в links
                    for link in entry.get('links', []):
                        if link.get('rel') == 'image':
                            logger.info(f"✅ Найдена картинка в links: {link.get('href')}")
                            return link.get('href')

            logger.warning(f"⚠️  Картинок не найдено в RSS: {rss_url}")
            return None

        except Exception as e:
            logger.error(f"❌ Ошибка при парсинге RSS: {e}")
            return None

    def parse_html_images(self, website_url: str, post_keywords: list) -> Optional[str]:
        """
        Парсит HTML страницу и ищет релевантные изображения

        Args:
            website_url: URL сайта
            post_keywords: Ключевые слова для поиска

        Returns:
            URL картинки или None
        """
        try:
            logger.info(f"🔍 Сканируем сайт: {website_url}")

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(website_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Простой парсинг: ищем теги img с релевантным alt/src
            from html.parser import HTMLParser

            class ImageParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.images = []

                def handle_starttag(self, tag, attrs):
                    if tag == 'img':
                        attrs_dict = dict(attrs)
                        src = attrs_dict.get('src', '')
                        alt = attrs_dict.get('alt', '').lower()

                        # Фильтруем по ключевым словам в alt или src
                        keywords_match = sum(1 for kw in post_keywords if kw.lower() in alt)

                        if keywords_match >= 1 and src:
                            self.images.append(src)

            parser = ImageParser()
            parser.feed(response.text)

            if parser.images:
                img_url = parser.images[0]  # Берем первую
                # Конвертим относительный путь в абсолютный
                if not img_url.startswith(('http://', 'https://')):
                    from urllib.parse import urljoin
                    img_url = urljoin(website_url, img_url)

                logger.info(f"✅ Найдена картинка: {img_url}")
                return img_url

            logger.warning(f"⚠️  Картинок не найдено на странице: {website_url}")
            return None

        except Exception as e:
            logger.error(f"❌ Ошибка при парсинге HTML: {e}")
            return None

    def get_image_for_post(self, post_data: dict) -> Optional[str]:
        """
        Получает изображение для поста: сначала парсит источники, потом генерирует

        Args:
            post_data: Данные поста {
                'title': 'AI КОНТРОЛИРУЕТ КАЧЕСТВО',
                'category': 'manufacturing_news',
                'sources': ['IndustryWeek', 'PlasticsToday'],
                'keywords': ['AI', 'quality', 'manufacturing'],
                'ai_prompt': 'промпт для генерации...'
            }

        Returns:
            Путь к сохраненной картинке или None
        """

        post_id = post_data.get('id', 'unknown')
        keywords = post_data.get('keywords', [])
        sources = post_data.get('sources', [])

        # Шаг 1: Парсим из RSS-источников
        source_mapping = {
            'IndustryWeek': 'https://www.industryweek.com/feed',
            'PlasticsToday': 'https://www.plasticstoday.com/feed',
            'Statista': 'https://www.statista.com/study/manufacturing',
            'Gartner': 'https://www.gartner.com/en/newsroom',
            'McKinsey': 'https://www.mckinsey.com/industries/manufacturing-supply-chain/our-research',
        }

        for source in sources:
            if source in source_mapping:
                rss_url = source_mapping[source]
                img_url = self.parse_rss_images(rss_url, keywords)

                if img_url:
                    return self._cache_image(img_url, post_id)

        # Шаг 2: Генерируем AI-картинку если парсинг не дал результатов
        logger.info(f"🤖 Генерируем AI-картинку для поста: {post_id}")

        ai_prompt = post_data.get('ai_prompt', '')

        if not ai_prompt:
            logger.error(f"❌ Нет AI-промпта для генерации картинки: {post_id}")
            return None

        # Используем DALL-E API (если доступен)
        ai_image_path = self._generate_ai_image(ai_prompt, post_id)

        return ai_image_path

    def _cache_image(self, image_url: str, post_id: str) -> str:
        """
        Скачивает и кэширует изображение локально
        """
        try:
            # Определяем расширение файла
            ext = '.jpg'
            if '.png' in image_url.lower():
                ext = '.png'
            elif '.gif' in image_url.lower():
                ext = '.gif'

            cache_path = self.media_cache / f"{post_id}{ext}"

            if cache_path.exists():
                logger.info(f"📦 Картинка уже в кэше: {cache_path}")
                return str(cache_path)

            logger.info(f"⬇️  Скачиваем картинку: {image_url}")

            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # Сохраняем локально
            with open(cache_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"✅ Картинка сохранена: {cache_path}")
            return str(cache_path)

        except Exception as e:
            logger.error(f"❌ Ошибка при кэшировании картинки: {e}")
            return None

    def _generate_ai_image(self, prompt: str, post_id: str) -> Optional[str]:
        """
        Генерирует картинку используя DALL-E API

        Требует:
        - OPENAI_API_KEY в .env
        - Лимиты на генерацию
        """

        openai_key = os.getenv("OPENAI_API_KEY", "")

        if not openai_key:
            logger.warning("⚠️  OPENAI_API_KEY не установлен. AI-генерация недоступна.")
            return None

        try:
            import openai
            openai.api_key = openai_key

            logger.info(f"🎨 Генерируем картинку через DALL-E...")
            logger.info(f"📝 Промпт: {prompt[:100]}...")

            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="standard",
                style="natural"
            )

            image_url = response['data'][0]['url']

            # Кэшируем AI-картинку
            cache_path = self._cache_image(image_url, f"{post_id}_ai")

            return cache_path

        except ImportError:
            logger.error("❌ openai библиотека не установлена. Установите: pip install openai")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка при генерации AI-картинки: {e}")
            return None

    def prepare_post_with_image(self, post_data: dict) -> dict:
        """
        Подготавливает пост с изображением для публикации

        Args:
            post_data: Данные поста

        Returns:
            Обновленные данные поста с путем к картинке
        """

        logger.info(f"🎬 Подготавливаем пост: {post_data.get('title', 'Unknown')}")

        # Получаем картинку (парсинг + генерация)
        image_path = self.get_image_for_post(post_data)

        post_data['image_path'] = image_path
        post_data['has_image'] = image_path is not None

        # Логируем результат
        if image_path:
            logger.info(f"✅ Пост готов с картинкой: {image_path}")
        else:
            logger.warning(f"⚠️  Пост готов БЕЗ картинки (не удалось получить)")

        return post_data


class PostProcessor:
    """Обработка постов перед публикацией"""

    @staticmethod
    def optimize_emojis(text: str) -> str:
        """
        Оптимизирует использование эмодзи:
        - Убирает лишние
        - Оставляет только для разделения и подчеркивания
        """

        # Правила оптимизации
        # Убираем дублирующиеся эмодзи в одной строке
        import re

        lines = text.split('\n')
        optimized_lines = []

        for line in lines:
            # Если строка содержит более 2 эмодзи, оставляем максимум 2
            emoji_pattern = r'[\U0001F300-\U0001F9FF]|[☀-➿]|[✀-➿]'
            emojis = re.findall(emoji_pattern, line)

            if len(emojis) > 2:
                # Берем первый и последний эмодзи, остальное ищем в начале
                first_emoji = emojis[0] if emojis else ''

                # Заменяем все эмодзи в строке, кроме первого
                line = first_emoji + re.sub(emoji_pattern, '', line).strip()

            optimized_lines.append(line)

        return '\n'.join(optimized_lines)

    @staticmethod
    def format_for_telegram(post_text: str, image_path: Optional[str] = None) -> dict:
        """
        Форматирует пост для Telegram Bot API

        Returns:
            {
                'text': 'Текст поста',
                'parse_mode': 'HTML',
                'image_path': '/path/to/image.jpg' или None
            }
        """

        return {
            'text': post_text,
            'parse_mode': 'HTML',
            'image_path': image_path
        }


# Примеры использования
POSTS_WITH_IMAGE_METADATA = [
    {
        'id': 'post_001_ai_quality',
        'title': 'AI КОНТРОЛИРУЕТ КАЧЕСТВО МЕБЕЛИ',
        'category': 'manufacturing_news',
        'sources': ['IndustryWeek', 'PlasticsToday'],
        'keywords': ['AI', 'quality control', 'manufacturing', 'inspection'],
        'ai_prompt': (
            "Industrial factory conveyor line with AI computer vision system. "
            "Red laser inspection lines scanning wooden furniture parts. "
            "Close-up of AI camera detecting defects in wood surfaces. "
            "Quality control monitoring screen showing 95% accuracy. "
            "Professional German manufacturing facility. "
            "High resolution, photorealistic, industrial lighting."
        )
    },
    {
        'id': 'post_002_coworking_tables',
        'title': 'НИША: СТОЛЫ ДЛЯ КОВОРКИНГОВ',
        'category': 'business_ideas',
        'sources': ['Statista', 'LinkedIn'],
        'keywords': ['coworking', 'tables', 'furniture', 'interior'],
        'ai_prompt': (
            "Modern coworking space interior design. "
            "Bright white and natural wood ergonomic desks with modular tables. "
            "Young professionals working on laptops. "
            "Green plants and natural lighting from large windows. "
            "Minimalist Scandinavian style furniture. "
            "Contemporary workspace, Instagram-worthy, professional photography, "
            "warm natural light, high resolution."
        )
    },
    {
        'id': 'post_003_cnc_machines',
        'title': 'ВЫБИРАЕМ ФРЕЗЕРНЫЙ СТАНОК — ТОП-5',
        'category': 'machinery',
        'sources': ['IndustryWeek', 'Machinery Values'],
        'keywords': ['CNC', 'router', 'machinery', 'equipment'],
        'ai_prompt': (
            "Collage of 5 different CNC routing machines displayed side by side. "
            "German HOMAG Costanza professional woodworking router on left. "
            "Italian SCM Group machine in center. "
            "Chinese WEIKE affordable CNC router. "
            "Korean SHODA machine on right. "
            "Industrial workshop setting with professional lighting. "
            "Technical specifications visible on each machine. "
            "High resolution technical photography, industrial style."
        )
    },
    {
        'id': 'post_004_eco_plastic',
        'title': 'ЭКОПЛАСТИК vs ОБЫЧНЫЙ ПЛАСТИК',
        'category': 'materials',
        'sources': ['PlasticsToday', 'Materials Today'],
        'keywords': ['eco-plastic', 'material', 'comparison', 'sustainability'],
        'ai_prompt': (
            "Split comparison image: left side shows eco-friendly green plastic "
            "granules, right side shows black conventional plastic granules. "
            "Both piles on white laboratory surface. "
            "Left side has green leaf or plant visible. "
            "Scientific photography, clean white background, "
            "professional studio lighting, macro photography, "
            "high resolution, educational style."
        )
    },
    {
        'id': 'post_005_price_forecast',
        'title': 'ПРОГНОЗ ЦЕН НА ПЛАСТИК Q4 2026',
        'category': 'trends',
        'sources': ['McKinsey', 'Gartner'],
        'keywords': ['price forecast', 'plastic', 'economics', 'trends'],
        'ai_prompt': (
            "Financial chart showing rising price trend. "
            "Red upward arrow line graph from July 2026 to December 2026. "
            "Y-axis shows prices in rubles 95-130. "
            "X-axis shows months. "
            "Oil barrel icon with warning symbol. "
            "Cargo container ship in background. "
            "Red color scheme, economic warning atmosphere, "
            "professional financial chart style, high resolution."
        )
    }
]


def main():
    """Главная функция: подготавливает все посты с картинками"""

    print("🚀 Запуск системы интеграции медиа для @UnitgroupAI")
    print("=" * 60)

    media = MediaIntegration()

    posts_prepared = []

    for post_data in POSTS_WITH_IMAGE_METADATA:
        print(f"\n📝 Обработка поста: {post_data['title']}")

        # Подготавливаем пост с картинкой
        prepared_post = media.prepare_post_with_image(post_data)
        posts_prepared.append(prepared_post)

    print("\n" + "=" * 60)
    print("✅ Готово! Статистика:")
    print(f"   📊 Всего постов: {len(posts_prepared)}")
    print(f"   ✓ С картинками: {sum(1 for p in posts_prepared if p.get('has_image'))}")
    print(f"   ✗ Без картинок: {sum(1 for p in posts_prepared if not p.get('has_image'))}")

    # Сохраняем результаты
    output_file = Path("data/posts_with_images.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posts_prepared, f, ensure_ascii=False, indent=2)

    print(f"\n📁 Результаты сохранены в: {output_file}")

    # Вывод для проверки
    for post in posts_prepared:
        print(f"\n  🎬 {post['title']}")
        if post.get('has_image'):
            print(f"     📸 Картинка: {post['image_path']}")
        else:
            print(f"     ⚠️  БЕЗ картинки")


if __name__ == '__main__':
    main()
