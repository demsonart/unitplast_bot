"""
Telegram Rate Limiter

Предотвращает Flood Control ошибки через:
1. Ограничение частоты сообщений (1-2 в минуту)
2. Exponential backoff при ошибках
3. Учет RetryAfter заголовков от Telegram
"""

import time
import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TelegramRateLimiter:
    """Управляет частотой отправки сообщений в Telegram"""

    def __init__(self, max_per_minute: int = 1):
        """
        Args:
            max_per_minute: максимум сообщений в минуту (default: 1)
        """
        self.max_per_minute = max_per_minute
        self.request_times = []
        self.last_retry_after = None

    async def wait_if_needed(self) -> None:
        """
        Ждет если нужно, чтобы не превысить rate limit.
        Вызывать ДО каждой отправки сообщения.
        """
        now = time.time()

        # Учитываем RetryAfter если было
        if self.last_retry_after and self.last_retry_after > now:
            wait_time = self.last_retry_after - now
            logger.warning(f"⏸️ RetryAfter: жду {wait_time:.1f}s")
            await self._async_sleep(wait_time + 1)
            self.last_retry_after = None
            return

        # Удаляем старые записи (старше 1 минуты)
        self.request_times = [t for t in self.request_times if now - t < 60]

        # Проверяем лимит
        if len(self.request_times) >= self.max_per_minute:
            # Нужно ждать
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest)
            if wait_time > 0:
                logger.info(f"⏱️ Rate limit: жду {wait_time:.1f}s ({len(self.request_times)}/{self.max_per_minute})")
                await self._async_sleep(wait_time + 0.5)

        # Записываем текущее время
        self.request_times.append(time.time())

    def handle_retry_after(self, retry_after_seconds: int) -> None:
        """
        Обработать Retry-After заголовок от Telegram.

        Args:
            retry_after_seconds: секунды для ожидания
        """
        self.last_retry_after = time.time() + retry_after_seconds + 1
        logger.warning(f"🚫 Telegram Flood Control: ждем {retry_after_seconds}s")

    @staticmethod
    async def _async_sleep(seconds: float) -> None:
        """Async sleep для использования в asyncio коде"""
        import asyncio
        await asyncio.sleep(seconds)


def truncate_message(text: str, max_length: int = 4096) -> str:
    """
    Обрезает сообщение до максимальной длины Telegram.

    Args:
        text: исходный текст
        max_length: максимум символов (default 4096 для обычных сообщений)

    Returns:
        Обрезанный текст с "..." в конце если было обрезано
    """
    if len(text) <= max_length:
        return text

    # Обрезаем на границе слова
    truncated = text[:max_length].rsplit(' ', 1)[0]

    # Удаляем пунктуацию в конце
    truncated = truncated.rstrip('.,;:!?')

    # Добавляем многоточие
    truncated = truncated + "..."

    logger.warning(f"📏 Обрезал сообщение: {len(text)} → {len(truncated)} символов")

    return truncated


def truncate_caption(text: str, max_length: int = 1024) -> str:
    """
    Обрезает caption для фото (лимит 1024 символа).

    Args:
        text: исходный текст
        max_length: максимум символов (default 1024 для caption)

    Returns:
        Обрезанный текст
    """
    return truncate_message(text, max_length)
