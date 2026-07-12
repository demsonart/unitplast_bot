#!/usr/bin/env python3
"""
UNITPLAST Health Monitor Agent (Enhanced)
Monitors /health endpoint every 60 seconds
Can request healing skills if issues detected
Autonomous 24/7 operation on VPS
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path
from agents.base_agent import BaseAgent
from agents.skill_requester import SkillRequester
from agents.skill_loader import SkillLoader

PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"

LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

HEALTH_URL = "http://127.0.0.1:5000/health"
CHECK_INTERVAL = 60

class HealthMonitorAgent(BaseAgent):
    def __init__(self):
        log_file = LOG_DIR / "health_monitor.log"
        super().__init__(
            agent_id="health_monitor",
            master_url=os.getenv("MASTER_URL", "http://127.0.0.1:8888"),
            master_token=os.getenv("MASTER_TOKEN", "unitplast_master_key_2026"),
            log_file=str(log_file)
        )
        self.skill_requester = SkillRequester(
            self.agent_id,
            self.master_url,
            self.master_token
        )
        self.skill_loader = SkillLoader(PROJECT_ROOT / "agents" / "skills")
        self.error_count = 0
        self.last_error = None

    def run(self):
        """Main health monitoring loop"""
        self.logger.info("Health Monitor started")
        self.log_event("startup", {"status": "started"})

        consecutive_errors = 0

        while True:
            try:
                response = requests.get(HEALTH_URL, timeout=5)

                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.log_event("health_check", {
                            "status": "OK",
                            "response_time": response.elapsed.total_seconds()
                        })
                        consecutive_errors = 0
                    except:
                        self.log_event("health_check", {
                            "status": "JSON_PARSE_ERROR",
                            "raw": response.text[:100]
                        })
                else:
                    self.error_count += 1
                    consecutive_errors += 1
                    self.last_error = f"Status code: {response.status_code}"
                    self.log_event("health_check", {
                        "status": "ERROR",
                        "status_code": response.status_code,
                        "consecutive_errors": consecutive_errors
                    })

                    if consecutive_errors >= 3:
                        self.request_healing(f"Health endpoint returned {response.status_code}")

            except requests.exceptions.Timeout:
                self.error_count += 1
                consecutive_errors += 1
                self.last_error = "Request timeout"
                self.log_event("health_check", {
                    "status": "TIMEOUT",
                    "consecutive_errors": consecutive_errors
                })

                if consecutive_errors >= 3:
                    self.request_healing("Health endpoint timeout - service may be unresponsive")

            except requests.exceptions.ConnectionError:
                self.error_count += 1
                consecutive_errors += 1
                self.last_error = "Connection refused"
                self.log_event("health_check", {
                    "status": "CONNECTION_ERROR",
                    "consecutive_errors": consecutive_errors
                })

                if consecutive_errors >= 3:
                    self.request_healing("Cannot connect to health endpoint")

            except Exception as e:
                self.error_count += 1
                self.logger.error(f"Unexpected error: {e}")
                self.log_event("health_check", {
                    "status": "FAILED",
                    "error": str(e)
                })

            time.sleep(CHECK_INTERVAL)

    def request_healing(self, issue: str):
        """Request healing skill for health issue"""
        self.logger.info(f"Requesting healing skill for: {issue}")

        result = self.skill_requester.request_healing_skill(
            issue=issue,
            error_log=self.last_error
        )

        if result and result.get('skill'):
            skill = result['skill']
            self.logger.info(f"Received skill: {skill.get('skill_id')}")

            if self.skill_loader.save_skill(skill['skill_id'], skill.get('code', '')):
                # Try to execute healing
                try:
                    self.skill_loader.execute_skill(skill['skill_id'])
                    self.skill_requester.report_installation(skill['skill_id'], True)
                except Exception as e:
                    self.skill_requester.report_installation(skill['skill_id'], False, str(e))

if __name__ == "__main__":
    try:
        agent = HealthMonitorAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\n[Health Monitor] Stopped by user", file=sys.stderr)
        sys.exit(0)
