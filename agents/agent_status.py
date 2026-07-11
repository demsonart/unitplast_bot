#!/usr/bin/env python3
"""
UNITPLAST Agent Status Collector
Collects systemd service status every 5 minutes
Completely autonomous, runs on VPS without Mac
"""

import subprocess
import json
import time
import sys
from datetime import datetime
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

SERVICES = [
    "unitplast.service",
    "unitplast-health-monitor.service",
    "unitplast-agent-status.service",
]

CHECK_INTERVAL = 300  # 5 minutes

def get_service_status(service):
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
        return f"error: {str(e)}"

def get_service_enabled(service):
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

def main():
    """Main agent status collector loop"""
    print(f"[{datetime.utcnow().isoformat()}] Agent Status Collector started", file=sys.stderr)

    while True:
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"
            statuses = {}

            for service in SERVICES:
                statuses[service] = {
                    "active": get_service_status(service),
                    "enabled": get_service_enabled(service)
                }

            data = {
                "timestamp": timestamp,
                "agents": statuses,
                "collection_count": None  # Will be updated by app if needed
            }

            # Write to JSON file
            status_file = DATA_DIR / "agents_status.json"
            with open(status_file, "w") as f:
                json.dump(data, f, indent=2)

            # Also log to file
            log_file = LOG_DIR / "agent_status.log"
            with open(log_file, "a") as f:
                f.write(json.dumps(data) + "\n")

        except Exception as e:
            print(f"[{datetime.utcnow().isoformat()}] Error: {e}", file=sys.stderr)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Agent Status] Stopped by user", file=sys.stderr)
        sys.exit(0)
