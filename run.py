#!/usr/bin/env python3
"""
UNITPLAST BOT - Main Entry Point
Runs Flask server + Telegram Bot + Email polling together
"""

import os
import sys
import asyncio
import threading
import logging
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_flask_server():
    """Run Flask server in separate thread"""
    try:
        from app.app import create_app
        from app.config import PORT

        app = create_app()
        logger.info(f"Starting Flask server on 0.0.0.0:{PORT}")
        app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask server error: {e}", exc_info=True)

def run_telegram_bot():
    """Run Telegram bot in asyncio event loop"""
    try:
        from app.main import main
        asyncio.run(main())
    except ImportError as e:
        # aiogram not installed (e.g., on local dev with Python 3.13 Rust issue)
        logger.warning(f"⚠️  Telegram bot dependencies missing: {e}")
        logger.warning("⚠️  Flask server is running, but Telegram bot is disabled")
        logger.warning("⚠️  On Railway with Docker, all dependencies will be available")
        # Keep Flask running - don't exit
        import time
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Telegram bot interrupted")
    except Exception as e:
        logger.error(f"Telegram bot error: {e}", exc_info=True)

def main():
    """Main entry point"""
    logger.info("="*60)
    logger.info("🤖 UNITPLAST BOT - UNIFIED STARTUP")
    logger.info("="*60)

    # Start Flask server in background thread
    flask_thread = threading.Thread(
        target=run_flask_server,
        daemon=True,
        name="FlaskServer"
    )
    flask_thread.start()
    logger.info("✓ Flask server thread started")

    # Start Telegram bot in main thread (blocking)
    logger.info("✓ Starting Telegram bot in main thread...")
    run_telegram_bot()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
