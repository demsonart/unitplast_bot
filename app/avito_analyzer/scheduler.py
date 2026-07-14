"""
Scheduler for automatic Avito analysis
Runs analysis 2 times per day and sends reports to admin
"""

import logging
import asyncio
from typing import Optional, Callable
from datetime import datetime

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
except ImportError:
    logging.warning("apscheduler not installed - use: pip install apscheduler")
    AsyncIOScheduler = None
    CronTrigger = None

logger = logging.getLogger(__name__)


class AnalysisScheduler:
    """
    Schedules automatic Avito analysis runs.
    """

    def __init__(self,
                 admin_id: int,
                 schedule_hours: str = "9,17",
                 callback: Optional[Callable] = None):
        """
        Initialize scheduler.

        Args:
            admin_id: Telegram admin ID for reports
            schedule_hours: Hours to run analysis (e.g., "9,17" for 9:00 and 17:00)
            callback: Async callback function(admin_id, report_text) for sending reports
        """
        if AsyncIOScheduler is None:
            raise ImportError("apscheduler required: pip install apscheduler")

        self.scheduler = AsyncIOScheduler()
        self.admin_id = admin_id
        self.callback = callback
        self.is_running = False

        # Parse schedule hours
        self.hours = [int(h.strip()) for h in schedule_hours.split(",")]

        logger.info(f"Scheduler initialized for hours: {self.hours}")

    def start(self, analysis_func: Callable):
        """
        Start scheduler.

        Args:
            analysis_func: Async function that performs full analysis
                          Should return report_text string
        """
        if self.is_running:
            logger.warning("Scheduler already running")
            return

        try:
            # Schedule for each hour
            for hour in self.hours:
                self.scheduler.add_job(
                    self._run_analysis_task,
                    CronTrigger(hour=hour, minute=0, timezone="Europe/Moscow"),
                    id=f"analysis_{hour:02d}",
                    name=f"Avito analysis at {hour:02d}:00",
                    args=(analysis_func,),
                )
                logger.info(f"Scheduled analysis at {hour:02d}:00")

            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler started")

        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")

    async def _run_analysis_task(self, analysis_func: Callable):
        """
        Run analysis task.

        Args:
            analysis_func: Async function that performs analysis
        """
        try:
            logger.info("Starting scheduled analysis...")

            # Run analysis
            result = await analysis_func()

            # Check if we have a callback to send report
            if self.callback and isinstance(result, str):
                try:
                    await self.callback(self.admin_id, result)
                    logger.info(f"Report sent to admin {self.admin_id}")
                except Exception as e:
                    logger.error(f"Error sending report: {e}")

            logger.info("Analysis task completed successfully")

        except Exception as e:
            logger.error(f"Error in analysis task: {e}")
            # Send error notification
            if self.callback:
                error_msg = f"❌ Ошибка при анализе рынка Avito:\n<code>{str(e)}</code>"
                try:
                    await self.callback(self.admin_id, error_msg)
                except:
                    pass

    def stop(self):
        """Stop scheduler."""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")

    def pause(self):
        """Pause scheduler."""
        try:
            if self.scheduler.running:
                self.scheduler.pause()
                logger.info("Scheduler paused")
        except Exception as e:
            logger.error(f"Error pausing scheduler: {e}")

    def resume(self):
        """Resume scheduler."""
        try:
            if self.scheduler.running:
                self.scheduler.resume()
                logger.info("Scheduler resumed")
        except Exception as e:
            logger.error(f"Error resuming scheduler: {e}")

    def get_jobs(self) -> list:
        """Get list of scheduled jobs."""
        return self.scheduler.get_jobs() if self.scheduler else []

    def remove_job(self, job_id: str):
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job {job_id} removed")
        except Exception as e:
            logger.error(f"Error removing job {job_id}: {e}")
