#!/usr/bin/env python3
"""
Healthcheck для Telegram Bot контейнера
Проверяет, что процесс бота живой по heartbeat файлу
"""

import os
import time
import sys

HEARTBEAT_FILE = "/tmp/unitgroup-bot-heartbeat"
MAX_AGE_SECONDS = 120


def check_health():
    """Проверить здоровье бота"""
    try:
        if not os.path.exists(HEARTBEAT_FILE):
            print("❌ Bot heartbeat file not found")
            return False

        age = time.time() - os.path.getmtime(HEARTBEAT_FILE)
        
        if age > MAX_AGE_SECONDS:
            print(f"❌ Bot heartbeat stale: {age:.0f}s old (max {MAX_AGE_SECONDS}s)")
            return False

        print(f"✅ Bot heartbeat OK ({age:.1f}s ago)")
        return True

    except Exception as e:
        print(f"❌ Healthcheck error: {e}")
        return False


if __name__ == "__main__":
    healthy = check_health()
    sys.exit(0 if healthy else 1)
