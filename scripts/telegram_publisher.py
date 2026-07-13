#!/usr/bin/env python3
"""
Telegram Publisher for @UnitgroupAI
Публикует посты с картинками в канал Telegram
"""

import os
import json
import requests
from typing import Optional
from pathlib import Path
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramPublisher:
    """Публикует посты в Telegram канал с картинками"""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.channel_id = os.getenv("TELEGRAM_CHANNEL_ID", "")
        self.admin_id = os.getenv("TELEGRAM_ADMIN_ID", "")
        self.dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
        self.require_approval = os.getenv("REQUIRE_APPROVAL", "true").lower() == "true"

        if not self.bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
        if not self.channel_id:
            logger.error("❌ TELEGRAM_CHANNEL_ID не установлен!")

    def send_photo_with_caption(self, photo_path: str, caption: str, **kwargs) -> dict:
        """
        Отправляет фото с подписью в Telegram

        Args:
            photo_path: Путь к файлу картинки или URL
            caption: Текст подписи

        Returns:
            Ответ от Telegram API
        """

        if self.dry_run:
            logger.info(f"🧪 DRY_RUN mode: Сообщение НЕ будет отправлено")
            return {'dry_run': True}

        if self.require_approval:
            logger.warning(f"⚠️  REQUIRE_APPROVAL=true: Отправка ждет одобрения админа")
            return {'requires_approval': True}

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"

            # Подготавливаем файл
            if photo_path.startswith(('http://', 'https://')):
                # Это URL - отправляем напрямую
                files = None
                data = {
                    'chat_id': self.channel_id,
                    'photo': photo_path,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }
            else:
                # Это локальный файл - отправляем с multipart
                files = {'photo': open(photo_path, 'rb')}
                data = {
                    'chat_id': self.channel_id,
                    'caption': caption,
                    'parse_mode': 'HTML'
                }

            logger.info(f"📤 Отправляем фото в Telegram...")

            response = requests.post(url, data=data, files=files)
            response.raise_for_status()

            result = response.json()

            if result.get('ok'):
                message_id = result['result']['message_id']
                logger.info(f"✅ Пост опубликован! Message ID: {message_id}")
                return {'success': True, 'message_id': message_id}
            else:
                logger.error(f"❌ Ошибка Telegram API: {result.get('description', 'Unknown')}")
                return {'success': False, 'error': result.get('description')}

        except Exception as e:
            logger.error(f"❌ Ошибка при отправке: {e}")
            return {'success': False, 'error': str(e)}

    def send_message(self, text: str, **kwargs) -> dict:
        """
        Отправляет текстовое сообщение (без картинки)

        Используется для постов без изображения
        """

        if self.dry_run:
            logger.info(f"🧪 DRY_RUN mode: Сообщение НЕ будет отправлено")
            return {'dry_run': True}

        if self.require_approval:
            logger.warning(f"⚠️  REQUIRE_APPROVAL=true: Отправка ждет одобрения админа")
            return {'requires_approval': True}

        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            data = {
                'chat_id': self.channel_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }

            logger.info(f"📤 Отправляем текстовое сообщение в Telegram...")

            response = requests.post(url, data=data)
            response.raise_for_status()

            result = response.json()

            if result.get('ok'):
                message_id = result['result']['message_id']
                logger.info(f"✅ Пост опубликован! Message ID: {message_id}")
                return {'success': True, 'message_id': message_id}
            else:
                logger.error(f"❌ Ошибка Telegram API: {result.get('description', 'Unknown')}")
                return {'success': False, 'error': result.get('description')}

        except Exception as e:
            logger.error(f"❌ Ошибка при отправке: {e}")
            return {'success': False, 'error': str(e)}

    def send_draft_preview(self, post_title: str, post_text: str,
                          image_path: Optional[str] = None) -> dict:
        """
        Отправляет превью поста админу для одобрения (если REQUIRE_APPROVAL=true)
        """

        if not self.admin_id:
            logger.warning("⚠️  TELEGRAM_ADMIN_ID не установлен. Превью не будет отправлено.")
            return {'warning': 'No admin_id'}

        try:
            # Форматируем превью
            preview_text = f"""
<b>🔍 ПРЕВЬЮ ПОСТА</b>

<b>Название:</b> {post_title}

<b>Текст:</b>
{post_text[:300]}...

<b>Картинка:</b> {'✅ Есть' if image_path else '⚠️ Нет'}

<b>Действия:</b>
/approve_{post_title.replace(' ', '_')} - Одобрить
/reject_{post_title.replace(' ', '_')} - Отклонить
            """

            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            data = {
                'chat_id': self.admin_id,
                'text': preview_text,
                'parse_mode': 'HTML'
            }

            response = requests.post(url, data=data)
            logger.info(f"📨 Превью отправлено админу")
            return {'sent': True}

        except Exception as e:
            logger.error(f"❌ Ошибка при отправке превью: {e}")
            return {'error': str(e)}

    def publish_post(self, post_data: dict) -> dict:
        """
        Публикует пост с картинкой (или без)

        Args:
            post_data: {
                'title': '...',
                'text': '...',
                'image_path': '/path/to/image.jpg' или None,
                'has_image': True/False
            }

        Returns:
            Результат публикации
        """

        logger.info(f"🚀 Публикуем пост: {post_data.get('title', 'Unknown')}")

        post_title = post_data.get('title', 'Unknown')
        post_text = post_data.get('text', '')
        image_path = post_data.get('image_path')
        has_image = post_data.get('has_image', False)

        # Если требуется одобрение - отправляем превью админу
        if self.require_approval:
            logger.info("📋 Отправляем превью на одобрение...")
            self.send_draft_preview(post_title, post_text, image_path)

            # В mode одобрения - возвращаем статус "ожидает одобрения"
            return {
                'status': 'pending_approval',
                'title': post_title,
                'dry_run': self.dry_run,
                'require_approval': self.require_approval
            }

        # Публикуем пост
        if has_image and image_path:
            # Отправляем фото с подписью
            result = self.send_photo_with_caption(image_path, post_text)
        else:
            # Отправляем только текст
            result = self.send_message(post_text)

        return {
            **result,
            'title': post_title,
            'dry_run': self.dry_run,
            'has_image': has_image
        }


def publish_all_posts_from_file(posts_file: str = "data/posts_with_images.json"):
    """
    Загружает посты из файла и публикует их

    Args:
        posts_file: Путь к JSON-файлу с постами
    """

    print("📂 Загружаем посты из файла...")

    try:
        with open(posts_file, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Файл не найден: {posts_file}")
        return

    print(f"✅ Загружено {len(posts_data)} постов")

    publisher = TelegramPublisher()

    print(f"\n{'=' * 60}")
    print(f"Режим: DRY_RUN={'🟢 ON' if publisher.dry_run else '🔴 OFF'}")
    print(f"Режим: REQUIRE_APPROVAL={'🟢 ON' if publisher.require_approval else '🔴 OFF'}")
    print(f"{'=' * 60}\n")

    results = []

    for i, post_data in enumerate(posts_data, 1):
        print(f"\n[{i}/{len(posts_data)}] {post_data.get('title', 'Unknown')}")

        result = publisher.publish_post(post_data)
        results.append(result)

        print(f"   Статус: {result.get('status', result.get('success'))}")

        if post_data.get('has_image'):
            print(f"   📸 Картинка: Да")
        else:
            print(f"   ⚠️  Картинка: Нет")

    # Статистика
    print(f"\n{'=' * 60}")
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   Всего постов: {len(results)}")
    print(f"   Успешно: {sum(1 for r in results if r.get('success'))}")
    print(f"   Ошибок: {sum(1 for r in results if not r.get('success') and r.get('error'))}")
    print(f"   Ожидают одобрения: {sum(1 for r in results if r.get('status') == 'pending_approval')}")
    print(f"   Сухой запуск: {sum(1 for r in results if r.get('dry_run'))}")
    print(f"{'=' * 60}\n")

    # Сохраняем результаты
    output_file = Path("data/publication_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ Результаты сохранены в: {output_file}")


if __name__ == '__main__':
    print("🚀 Telegram Publisher для @UnitgroupAI")
    print("=" * 60)

    # Проверяем переменные окружения
    if not os.getenv("TELEGRAM_BOT_TOKEN"):
        print("⚠️  Требуется TELEGRAM_BOT_TOKEN в .env файле")
        print("   Пример: TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZ")
        exit(1)

    if not os.getenv("TELEGRAM_CHANNEL_ID"):
        print("⚠️  Требуется TELEGRAM_CHANNEL_ID в .env файле")
        print("   Пример: TELEGRAM_CHANNEL_ID=-1001234567890")
        exit(1)

    # Публикуем посты
    publish_all_posts_from_file()
