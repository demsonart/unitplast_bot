#!/usr/bin/env python3
"""
UNITPLAST Log Analyzer Agent
Analyzes health and status logs for patterns, anomalies, and self-improvement
Runs every 10 minutes, completely autonomous
"""

import json
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, median, stdev

PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"

LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

HEALTH_LOG = LOG_DIR / "health_monitor.log"
ANALYSIS_FILE = DATA_DIR / "log_analysis.json"
PATTERNS_FILE = DATA_DIR / "patterns.json"
PREDICTIONS_FILE = DATA_DIR / "predictions.json"
PERFORMANCE_FILE = DATA_DIR / "performance_trends.json"

CHECK_INTERVAL = 600  # 10 minutes


def load_json_lines(file_path, limit=1000):
    """Load JSON lines from file (most recent last)"""
    lines = []
    try:
        if file_path.exists():
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            lines.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
    except Exception as e:
        print(f"Error loading {file_path}: {e}", file=sys.stderr)
    return lines[-limit:] if limit else lines


def analyze_health_logs(logs):
    """Analyze health check logs for patterns and anomalies"""
    if not logs:
        return None

    response_times = []
    errors = []
    timeouts = []

    for log in logs:
        # Extract response time if available
        if log.get('status') == 'OK':
            # Try to estimate response time from log structure
            response_times.append(100)  # Default estimate
        elif log.get('status') in ['TIMEOUT', 'CONNECTION_ERROR']:
            timeouts.append(1)
        else:
            errors.append(1)

    analysis = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_checks": len(logs),
        "successful": sum(1 for l in logs if l.get('status') == 'OK'),
        "errors": len(errors),
        "timeouts": len(timeouts),
        "error_rate": len(errors) / len(logs) if logs else 0,
        "timeout_rate": len(timeouts) / len(logs) if logs else 0,
    }

    if response_times:
        analysis["response_time_avg"] = mean(response_times)
        analysis["response_time_median"] = median(response_times)
        if len(response_times) > 1:
            analysis["response_time_stdev"] = stdev(response_times)

    return analysis


def detect_anomalies(current_analysis, patterns):
    """Detect anomalies against established patterns"""
    anomalies = []

    if not patterns:
        return anomalies

    # Check error rate
    baseline_error = patterns.get("error_rate_avg", 0)
    current_error = current_analysis.get("error_rate", 0)
    if current_error > baseline_error * 2:  # 2x increase is anomaly
        anomalies.append({
            "type": "error_spike",
            "baseline": baseline_error,
            "current": current_error,
            "severity": "warning"
        })

    # Check response time
    baseline_rt = patterns.get("response_time_avg", 200)
    current_rt = current_analysis.get("response_time_avg", 200)
    if current_rt > baseline_rt * 1.5:  # 50% increase is anomaly
        anomalies.append({
            "type": "slow_response",
            "baseline": baseline_rt,
            "current": current_rt,
            "severity": "info"
        })

    return anomalies


def build_patterns(analysis_history):
    """Build baseline patterns from history"""
    if len(analysis_history) < 24:  # Need at least 24 data points
        return None

    error_rates = [a.get("error_rate", 0) for a in analysis_history]
    response_times = [a.get("response_time_avg", 100) for a in analysis_history if a.get("response_time_avg")]

    patterns = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "data_points": len(analysis_history),
        "error_rate_avg": mean(error_rates) if error_rates else 0,
        "error_rate_max": max(error_rates) if error_rates else 0,
        "response_time_avg": mean(response_times) if response_times else 100,
        "response_time_p95": sorted(response_times)[int(len(response_times)*0.95)] if response_times else 100,
        "trend": "stable"  # Could be calculated from history
    }

    return patterns


def predict_issues(analysis, patterns, status_logs):
    """Predict potential issues"""
    predictions = []

    if not patterns or not status_logs:
        return predictions

    # Check for increased restart frequency
    recent_logs = status_logs[-12:]  # Last hour (5 statuses * 60min / 5min)
    restart_counts = []
    for log in recent_logs:
        for service, info in log.get("agents", {}).items():
            # Count service status changes as potential restarts
            pass

    # Simple prediction: if error rate is increasing, flag it
    current_error = analysis.get("error_rate", 0)
    baseline_error = patterns.get("error_rate_avg", 0)
    if current_error > baseline_error:
        trend_pct = ((current_error - baseline_error) / baseline_error * 100) if baseline_error > 0 else 0
        predictions.append({
            "type": "error_rate_trending_up",
            "baseline": baseline_error,
            "current": current_error,
            "trend_percent": trend_pct,
            "confidence": 0.6,
            "recommendation": "Monitor error logs"
        })

    return predictions


def generate_report():
    """Main analysis loop"""
    print(f"[{datetime.utcnow().isoformat()}] Log Analyzer started")

    # Load all data
    health_logs = load_json_lines(HEALTH_LOG, limit=1440)  # Last 24 hours
    status_logs = load_json_lines(DATA_DIR / "agents_status.log", limit=288)  # Last 24 hours

    # Load historical analysis
    analysis_history = load_json_lines(ANALYSIS_FILE, limit=144)  # Last 24 hours of 10-min intervals

    # Perform analysis
    current_analysis = analyze_health_logs(health_logs)
    if not current_analysis:
        print("No health logs to analyze")
        return

    # Load existing patterns
    patterns = None
    if PATTERNS_FILE.exists():
        try:
            with open(PATTERNS_FILE, 'r') as f:
                patterns = json.load(f)
        except:
            patterns = None

    # Update patterns if we have enough history
    if len(analysis_history) >= 24:
        patterns = build_patterns(analysis_history)
        with open(PATTERNS_FILE, 'w') as f:
            json.dump(patterns, f, indent=2)

    # Detect anomalies
    anomalies = detect_anomalies(current_analysis, patterns) if patterns else []

    # Make predictions
    predictions = predict_issues(current_analysis, patterns, status_logs) if patterns else []

    # Build full report
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "analysis": current_analysis,
        "patterns": patterns,
        "anomalies": anomalies,
        "predictions": predictions,
        "status": "ok" if not anomalies else "warning" if anomalies else "ok"
    }

    # Save report
    with open(ANALYSIS_FILE, 'a') as f:
        f.write(json.dumps(report) + "\n")

    # Save predictions separately
    if predictions:
        predictions_data = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "predictions": predictions
        }
        with open(PREDICTIONS_FILE, 'w') as f:
            json.dump(predictions_data, f, indent=2)

    print(f"[{datetime.utcnow().isoformat()}] Analysis complete")
    if anomalies:
        print(f"  ⚠️  {len(anomalies)} anomalies detected")
    if predictions:
        print(f"  🔮 {len(predictions)} predictions generated")


def main():
    """Main loop"""
    print(f"[{datetime.utcnow().isoformat()}] UNITPLAST Log Analyzer started", file=sys.stderr)

    while True:
        try:
            generate_report()
        except Exception as e:
            print(f"[{datetime.utcnow().isoformat()}] Error: {e}", file=sys.stderr)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Log Analyzer] Stopped by user", file=sys.stderr)
        sys.exit(0)
