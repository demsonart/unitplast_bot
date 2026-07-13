#!/usr/bin/env python3
"""
Full Deployment Pipeline для @UnitgroupAI
Полный цикл: подготовка → интеграция картинок → оптимизация эмодзи → публикация
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FullDeployment:
    """Полный процесс развертывания контента"""

    def __init__(self):
        self.dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
        self.require_approval = os.getenv("REQUIRE_APPROVAL", "true").lower() == "true"
        self.log_file = Path("logs/deployment.log")
        self.log_file.parent.mkdir(exist_ok=True)

    def log(self, message: str, level: str = "info"):
        """Логирует сообщение"""
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(message)

        # Также пишем в файл
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")

    def step_1_prepare_content(self) -> bool:
        """
        Шаг 1: Подготовка контента

        - Загружает посты из POSTS_WITH_IMAGES_AND_PROMPTS.md
        - Парсит текст и создает JSON с данными
        """

        self.log("🎬 ШАГ 1: ПОДГОТОВКА КОНТЕНТА")
        self.log("=" * 60)

        posts_file = Path("docs/POSTS_WITH_IMAGES_AND_PROMPTS.md")

        if not posts_file.exists():
            self.log(f"❌ Файл не найден: {posts_file}", "error")
            return False

        self.log(f"✅ Найден файл контента: {posts_file}")

        # Здесь должен быть парсинг markdown файла
        # Для простоты - используем заранее подготовленные данные

        posts_data = [
            {
                'id': 'post_001',
                'title': '🔧 AI КОНТРОЛИРУЕТ КАЧЕСТВО МЕБЕЛИ',
                'text': self._load_post_text('post_001'),
                'category': 'manufacturing_news',
                'sources': ['IndustryWeek', 'PlasticsToday'],
                'keywords': ['AI', 'quality control', 'manufacturing'],
                'ai_prompt': "Industrial factory conveyor line with AI computer vision system..."
            },
            {
                'id': 'post_002',
                'title': '💡 НИША: СТОЛЫ ДЛЯ КОВОРКИНГОВ',
                'text': self._load_post_text('post_002'),
                'category': 'business_ideas',
                'sources': ['Statista'],
                'keywords': ['coworking', 'furniture', 'market'],
                'ai_prompt': "Modern coworking space interior design..."
            },
            {
                'id': 'post_003',
                'title': '⚙️ ВЫБИРАЕМ ФРЕЗЕРНЫЙ СТАНОК — ТОП-5',
                'text': self._load_post_text('post_003'),
                'category': 'machinery',
                'sources': ['IndustryWeek', 'Machinery Values'],
                'keywords': ['CNC', 'machinery', 'equipment'],
                'ai_prompt': "Collage of 5 different CNC routing machines..."
            },
            {
                'id': 'post_004',
                'title': '🌱 ЭКОПЛАСТИК vs ОБЫЧНЫЙ ПЛАСТИК',
                'text': self._load_post_text('post_004'),
                'category': 'materials',
                'sources': ['PlasticsToday', 'Materials Today'],
                'keywords': ['eco-plastic', 'material', 'comparison'],
                'ai_prompt': "Split comparison image: eco-friendly green plastic..."
            },
            {
                'id': 'post_005',
                'title': '📈 ПРОГНОЗ ЦЕН НА ПЛАСТИК Q4 2026',
                'text': self._load_post_text('post_005'),
                'category': 'trends',
                'sources': ['McKinsey', 'Gartner'],
                'keywords': ['price forecast', 'economics', 'trends'],
                'ai_prompt': "Financial chart showing rising price trend..."
            }
        ]

        # Сохраняем подготовленные посты
        output_file = Path("data/posts_prepared.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, ensure_ascii=False, indent=2)

        self.log(f"✅ Подготовлено постов: {len(posts_data)}")
        self.log(f"📁 Сохранено в: {output_file}")

        return True

    def step_2_integrate_media(self) -> bool:
        """
        Шаг 2: Интеграция медиа

        - Парсит RSS-фиды источников
        - Скачивает картинки
        - Генерирует AI-картинки если нужно
        """

        self.log("\n🎬 ШАГ 2: ИНТЕГРАЦИЯ МЕДИА (КАРТИНКИ)")
        self.log("=" * 60)

        try:
            # Запускаем скрипт медиа-интеграции
            result = subprocess.run(
                ['python3', 'scripts/media_integration.py'],
                capture_output=True,
                text=True,
                timeout=300
            )

            self.log(f"📊 Вывод скрипта медиа-интеграции:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    self.log(f"   {line}")

            if result.returncode != 0:
                self.log(f"❌ Ошибка: {result.stderr}", "error")
                return False

            self.log("✅ Медиа интегрирована успешно")
            return True

        except subprocess.TimeoutExpired:
            self.log("❌ Timeout при интеграции медиа", "error")
            return False
        except Exception as e:
            self.log(f"❌ Ошибка: {e}", "error")
            return False

    def step_3_optimize_emojis(self) -> bool:
        """
        Шаг 3: Оптимизация эмодзи

        - Убирает лишние эмодзи
        - Оставляет только для разделения и подчеркивания ключевых моментов
        """

        self.log("\n🎬 ШАГ 3: ОПТИМИЗАЦИЯ ЭМОДЗИ")
        self.log("=" * 60)

        try:
            posts_file = Path("data/posts_with_images.json")

            if not posts_file.exists():
                self.log(f"⚠️  Файл не найден: {posts_file} (возможно медиа еще не готова)", "warning")
                return False

            with open(posts_file, 'r', encoding='utf-8') as f:
                posts_data = json.load(f)

            # Оптимизируем эмодзи в каждом посте
            import re

            for post in posts_data:
                text = post.get('text', '')

                # Правило: оставляем эмодзи только:
                # 1. В начале поста (заголовок + подтема)
                # 2. Для разделения абзацев (максимум 1-2 эмодзи)
                # 3. В конце для подчеркивания (максимум 1)

                lines = text.split('\n')
                optimized_lines = []

                for i, line in enumerate(lines):
                    # Если это заголовок или подзаголовок - оставляем эмодзи
                    if i < 3 or line.strip().startswith('#'):
                        optimized_lines.append(line)
                    else:
                        # Для остальных строк - убираем все эмодзи, кроме концевого
                        # Найдем эмодзи в начале
                        emoji_match = re.match(r'^([\U0001F300-\U0001F9FF]+)\s*', line)

                        if emoji_match:
                            # Оставляем только первый эмодзи
                            emoji = emoji_match.group(1)[0]
                            rest = line[len(emoji_match.group(0)):]
                            optimized_lines.append(f"{emoji} {rest}")
                        else:
                            optimized_lines.append(line)

                post['text'] = '\n'.join(optimized_lines)

            # Сохраняем оптимизированные посты
            with open(posts_file, 'w', encoding='utf-8') as f:
                json.dump(posts_data, f, ensure_ascii=False, indent=2)

            self.log(f"✅ Оптимизировано {len(posts_data)} постов")
            self.log(f"📁 Обновлено в: {posts_file}")

            return True

        except Exception as e:
            self.log(f"❌ Ошибка: {e}", "error")
            return False

    def step_4_publish_to_telegram(self) -> bool:
        """
        Шаг 4: Публикация в Telegram

        - Отправляет посты в канал @UnitgroupAI
        - С картинками и оптимизированными эмодзи
        """

        self.log("\n🎬 ШАГ 4: ПУБЛИКАЦИЯ В TELEGRAM")
        self.log("=" * 60)

        if self.dry_run:
            self.log("🧪 DRY_RUN=true: Посты НЕ будут отправлены в канал")

        if self.require_approval:
            self.log("🔒 REQUIRE_APPROVAL=true: Требуется одобрение админа")

        try:
            # Запускаем скрипт публикации
            result = subprocess.run(
                ['python3', 'scripts/telegram_publisher.py'],
                capture_output=True,
                text=True,
                timeout=300
            )

            self.log(f"📊 Вывод скрипта публикации:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    self.log(f"   {line}")

            if result.returncode != 0:
                self.log(f"❌ Ошибка: {result.stderr}", "error")
                return False

            self.log("✅ Публикация завершена")
            return True

        except subprocess.TimeoutExpired:
            self.log("❌ Timeout при публикации", "error")
            return False
        except Exception as e:
            self.log(f"❌ Ошибка: {e}", "error")
            return False

    def run_full_pipeline(self):
        """Запускает полный процесс"""

        self.log("\n" + "=" * 60)
        self.log("🚀 ЗАПУСК ПОЛНОГО ПРОЦЕССА РАЗВЕРТЫВАНИЯ")
        self.log("=" * 60)
        self.log(f"Время: {datetime.now().isoformat()}")
        self.log(f"DRY_RUN: {self.dry_run}")
        self.log(f"REQUIRE_APPROVAL: {self.require_approval}")
        self.log("=" * 60 + "\n")

        steps = [
            ("Подготовка контента", self.step_1_prepare_content),
            ("Интеграция медиа", self.step_2_integrate_media),
            ("Оптимизация эмодзи", self.step_3_optimize_emojis),
            ("Публикация в Telegram", self.step_4_publish_to_telegram),
        ]

        results = {}

        for step_name, step_func in steps:
            try:
                success = step_func()
                results[step_name] = "✅ OK" if success else "❌ FAILED"

                if not success:
                    self.log(f"\n⚠️  Процесс остановлен на шаге: {step_name}", "warning")
                    break

            except Exception as e:
                self.log(f"❌ Критическая ошибка на шаге '{step_name}': {e}", "error")
                results[step_name] = "❌ ERROR"
                break

        # Итоговый отчет
        self.log("\n" + "=" * 60)
        self.log("📊 ИТОГОВЫЙ ОТЧЕТ")
        self.log("=" * 60)

        for step_name, status in results.items():
            self.log(f"{status} {step_name}")

        self.log("=" * 60)

        if all("✅" in status for status in results.values()):
            self.log("\n✅ ВЕСЬ ПРОЦЕСС ЗАВЕРШЕН УСПЕШНО!")
            self.log("📱 Посты готовы к публикации в @UnitgroupAI")

            if self.require_approval:
                self.log("📋 Ожидание одобрения админа...")

            if self.dry_run:
                self.log("🧪 (DRY_RUN mode - реальная публикация не произошла)")

        else:
            self.log("\n❌ ПРОЦЕСС ЗАВЕРШЕН С ОШИБКАМИ")
            self.log(f"📁 Подробности в логе: {self.log_file}")

        return results

    def _load_post_text(self, post_id: str) -> str:
        """Загружает текст поста (placeholder)"""
        # Это просто заглушка - реальный текст берется из markdown файла
        return f"[Текст поста {post_id}]"


def main():
    """Главная точка входа"""

    print("🚀 FULL DEPLOYMENT PIPELINE для @UnitgroupAI")
    print("=" * 60)

    # Проверяем обязательные переменные окружения
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("⚠️  Требуется TELEGRAM_BOT_TOKEN в .env")
        exit(1)

    # Запускаем полный процесс
    deployment = FullDeployment()
    deployment.run_full_pipeline()


if __name__ == '__main__':
    main()
