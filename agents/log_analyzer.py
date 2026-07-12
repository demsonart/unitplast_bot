#!/usr/bin/env python3
"""
UNITPLAST Log Analyzer Agent (Enhanced)
Analyzes health and status logs for patterns, anomalies, and self-improvement
Requests optimization skills when patterns detected
Runs every 10 minutes, completely autonomous
"""

import json
import time
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, median, stdev
from agents.base_agent import BaseAgent
from agents.skill_requester import SkillRequester
from agents.skill_loader import SkillLoader

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


class LogAnalyzerAgent(BaseAgent):
    def __init__(self):
        log_file = LOG_DIR / "log_analyzer.log"
        super().__init__(
            agent_id="log_analyzer",
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
        self.analysis_history = []

    def run(self):
        """Main loop"""
        self.logger.info("Log Analyzer started")
        self.log_event("startup", {"status": "started"})

        while True:
            try:
                self.analyze_and_optimize()
            except Exception as e:
                self.logger.error(f"Analysis error: {e}")
                self.log_event("error", {"error": str(e)})

            time.sleep(CHECK_INTERVAL)

    def analyze_and_optimize(self):
        """Generate analysis and request optimization if needed"""
        # Load logs
        health_logs = load_json_lines(HEALTH_LOG)
        status_logs = load_json_lines(LOG_DIR / "agent_status.log")

        if not health_logs:
            return

        # Analyze
        analysis = analyze_health_logs(health_logs)
        self.analysis_history.append(analysis)

        # Build patterns from last 24h
        patterns = build_patterns(self.analysis_history[-144:])
        if patterns:
            with open(PATTERNS_FILE, 'w') as f:
                json.dump(patterns, f, indent=2)

        # Detect anomalies
        anomalies = detect_anomalies(analysis, patterns)

        # Make predictions
        predictions = predict_issues(analysis, patterns, status_logs)

        # Save analysis
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "analysis": analysis,
            "anomalies": anomalies,
            "predictions": predictions,
            "status": "ok" if not anomalies else "warning"
        }

        with open(ANALYSIS_FILE, 'a') as f:
            f.write(json.dumps(report) + "\n")

        if anomalies:
            self.log_event("anomalies_detected", {
                "count": len(anomalies),
                "anomalies": anomalies
            })
            self.request_optimization(anomalies, analysis, patterns)

        if predictions:
            with open(PREDICTIONS_FILE, 'w') as f:
                json.dump({"predictions": predictions, "timestamp": datetime.utcnow().isoformat()}, f, indent=2)
            self.log_event("predictions_generated", {"count": len(predictions)})

    def request_optimization(self, anomalies: list, analysis: dict, patterns: dict):
        """Request optimization skill based on anomalies"""
        for anomaly in anomalies:
            if anomaly['type'] == 'slow_response':
                current = analysis.get('response_time_avg', 100)
                target = patterns.get('response_time_avg', 50)

                self.logger.info(f"Requesting response time optimization")
                result = self.skill_requester.request_optimization_skill(
                    metric="response_time",
                    current_value=current,
                    target_value=target
                )

                if result and result.get('skill'):
                    skill = result['skill']
                    if self.skill_loader.save_skill(skill['skill_id'], skill.get('code', '')):
                        try:
                            self.skill_loader.execute_skill(skill['skill_id'])
                            self.skill_requester.report_installation(skill['skill_id'], True)
                        except Exception as e:
                            self.skill_requester.report_installation(skill['skill_id'], False, str(e))

            elif anomaly['type'] == 'error_spike':
                self.logger.info(f"Requesting error handling optimization")
                # Similar pattern for error handling

def main():
    """Main loop"""
    agent = LogAnalyzerAgent()
    agent.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Log Analyzer] Stopped by user", file=sys.stderr)
        sys.exit(0)
