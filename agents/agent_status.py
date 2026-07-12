#!/usr/bin/env python3
"""
UNITPLAST Agent Status Collector (Enhanced)
Collects systemd service status every 5 minutes
Can request remediation skills if services fail
Autonomous 24/7 operation on VPS
"""

import subprocess
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
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

SERVICES = [
    "unitplast.service",
    "unitplast-health-monitor.service",
    "unitplast-agent-status.service",
    "unitplast-log-analyzer.service",
]

CHECK_INTERVAL = 300

class AgentStatusAgent(BaseAgent):
    def __init__(self):
        log_file = LOG_DIR / "agent_status.log"
        super().__init__(
            agent_id="agent_status",
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
        self.service_failures = {}

    def run(self):
        """Main agent status collector loop"""
        self.logger.info("Agent Status Collector started")
        self.log_event("startup", {"status": "started"})

        while True:
            try:
                timestamp = datetime.utcnow().isoformat() + "Z"
                statuses = {}

                for service in SERVICES:
                    active = self.get_service_status(service)
                    enabled = self.get_service_enabled(service)

                    statuses[service] = {
                        "active": active,
                        "enabled": enabled
                    }

                    # Track failures
                    if active != "active":
                        if service not in self.service_failures:
                            self.service_failures[service] = 0
                        self.service_failures[service] += 1

                        if self.service_failures[service] >= 2:
                            self.request_remediation(service, active)
                    else:
                        if service in self.service_failures:
                            del self.service_failures[service]

                data = {
                    "timestamp": timestamp,
                    "agents": statuses,
                    "collection_count": int(time.time())
                }

                # Write to JSON file
                status_file = DATA_DIR / "agents_status.json"
                with open(status_file, "w") as f:
                    json.dump(data, f, indent=2)

                self.log_event("status_collection", {
                    "services_checked": len(SERVICES),
                    "service_failures": len(self.service_failures)
                })

            except Exception as e:
                self.logger.error(f"Status collection error: {e}")
                self.log_event("error", {"error": str(e)})

            time.sleep(CHECK_INTERVAL)

    def get_service_status(self, service):
        """Get systemd service status"""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception as e:
            return f"error"

    def get_service_enabled(self, service):
        """Check if service is enabled"""
        try:
            result = subprocess.run(
                ["systemctl", "is-enabled", service],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except:
            return "unknown"

    def request_remediation(self, service: str, current_status: str):
        """Request remediation skill for failed service"""
        self.logger.info(f"Requesting remediation for {service}")

        result = self.skill_requester.request_healing_skill(
            issue=f"Service {service} is {current_status}",
            error_log=f"Service status check failed. Current status: {current_status}"
        )

        if result and result.get('skill'):
            skill = result['skill']
            if self.skill_loader.save_skill(skill['skill_id'], skill.get('code', '')):
                try:
                    self.skill_loader.execute_skill(skill['skill_id'])
                    self.skill_requester.report_installation(skill['skill_id'], True)
                except Exception as e:
                    self.skill_requester.report_installation(skill['skill_id'], False, str(e))

if __name__ == "__main__":
    try:
        agent = AgentStatusAgent()
        agent.run()
    except KeyboardInterrupt:
        print("\n[Agent Status] Stopped by user", file=sys.stderr)
        sys.exit(0)
