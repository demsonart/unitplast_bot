#!/usr/bin/env python3
"""
News Agent Worker - Entry Point for Autonomous News Agent
Runs: python3 app/news_agent_worker.py OR python3 -m app.news_agent_worker
"""

import asyncio
import logging
import sys
from pathlib import Path

# Ensure proper path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for autonomous news agent"""
    try:
        logger.info("="*70)
        logger.info("🤖 AUTONOMOUS NEWS AGENT - STARTING")
        logger.info("="*70)

        from app.autonomous_news_agent import AutonomousNewsAgent

        agent = AutonomousNewsAgent()
        logger.info("✅ Agent initialized successfully")

        logger.info("🔄 Starting autonomous loop...")
        await agent.run_autonomous_loop()

    except KeyboardInterrupt:
        logger.info("⏹️  Autonomous agent stopped by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ FATAL ERROR in autonomous agent: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    logger.info("News Agent Worker started")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown by user")
        sys.exit(0)
