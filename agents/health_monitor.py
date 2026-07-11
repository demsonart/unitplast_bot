#!/usr/bin/env python3
"""
UNITPLAST Health Monitor Agent
Monitors /health endpoint every 60 seconds, writes to log
Completely autonomous, runs on VPS without Mac
"""

import requests
import json
import time
import sys
from datetime import datetime
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"

# Ensure directories exist
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

HEALTH_URL = "http://127.0.0.1:5000/health"
CHECK_INTERVAL = 60  # seconds

def log_check(status, response, error=None):
    """Write health check to log file"""
    log_file = LOG_DIR / "health_monitor.log"
    timestamp = datetime.utcnow().isoformat() + "Z"

    log_entry = {
        "timestamp": timestamp,
        "status": status,
        "response": response,
        "error": error
    }

    try:
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Failed to write log: {e}", file=sys.stderr)

def main():
    """Main health monitor loop"""
    print(f"[{datetime.utcnow().isoformat()}] Health Monitor started", file=sys.stderr)

    while True:
        try:
            response = requests.get(HEALTH_URL, timeout=5)

            if response.status_code == 200:
                try:
                    data = response.json()
                    log_check("OK", data)
                except:
                    log_check("OK", {"raw": response.text[:100]})
            else:
                log_check("ERROR", {"status_code": response.status_code})

        except requests.exceptions.Timeout:
            log_check("TIMEOUT", {}, "Request timeout")
        except requests.exceptions.ConnectionError:
            log_check("CONNECTION_ERROR", {}, "Cannot connect to localhost:5000")
        except Exception as e:
            log_check("FAILED", {}, str(e))

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Health Monitor] Stopped by user", file=sys.stderr)
        sys.exit(0)
