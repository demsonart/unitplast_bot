"""Skill generator - creates skills using Claude API"""
import json
import os
from datetime import datetime
from anthropic import Anthropic

class SkillGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-opus-4-8"

    def generate_python_skill(self, skill_id: str, requirement: str, context: dict = None) -> dict | None:
        """Generate Python skill code via Claude API"""
        context_str = json.dumps(context, indent=2) if context else "None"

        prompt = f"""You are a Python code generator for autonomous agents.

Generate a Python function that solves this requirement:
Skill ID: {skill_id}
Requirement: {requirement}
Context: {context_str}

Rules:
1. Function must be self-contained
2. No external dependencies beyond stdlib
3. Must handle errors gracefully
4. Return dict with result: {{"success": bool, "data": dict, "error": str}}
5. Add docstring
6. Maximum 100 lines

Output ONLY the Python code, no explanation."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        code = message.content[0].text
        return {
            "skill_id": skill_id,
            "type": "python_function",
            "code": code,
            "generated_at": datetime.now().isoformat(),
            "model": self.model
        }

    def generate_systemd_skill(self, skill_id: str, requirement: str) -> dict | None:
        """Generate systemd service via Claude API"""
        prompt = f"""Generate a systemd service file for this requirement:
Skill ID: {skill_id}
Requirement: {requirement}

Rules:
1. Must have [Unit], [Service], [Install] sections
2. User=unitplast (not root)
3. Restart=always for auto-recovery
4. StandardOutput=journal for logging
5. Add description

Output ONLY the systemd config, no explanation."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = message.content[0].text
        return {
            "skill_id": skill_id,
            "type": "systemd_service",
            "service_content": content,
            "generated_at": datetime.now().isoformat(),
            "model": self.model
        }

    def generate_healing_skill(self, agent_id: str, issue: str, error_log: str = None) -> dict | None:
        """Generate a healing/remediation skill for specific issue"""
        context = {
            "agent_id": agent_id,
            "issue": issue,
            "error_log": error_log[:500] if error_log else None
        }

        prompt = f"""Generate a Python healing function for this agent issue:
Agent: {agent_id}
Issue: {issue}
Error Log: {error_log[:300] if error_log else "None"}

The function should:
1. Detect the problem
2. Attempt automatic remediation
3. Return success/failure with details
4. Log all actions

Output ONLY Python code."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        code = message.content[0].text
        skill_id = f"heal_{agent_id}_{int(datetime.now().timestamp())}"

        return {
            "skill_id": skill_id,
            "type": "python_function",
            "code": code,
            "purpose": f"Heal {issue} for {agent_id}",
            "generated_at": datetime.now().isoformat(),
            "model": self.model
        }

    def generate_optimization_skill(self, metric: str, current_value: float, target_value: float) -> dict | None:
        """Generate optimization skill to improve specific metric"""
        prompt = f"""Generate a Python optimization function:
Metric: {metric}
Current: {current_value}
Target: {target_value}

The function should analyze and improve the metric.
Output ONLY Python code."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        code = message.content[0].text
        skill_id = f"opt_{metric}_{int(datetime.now().timestamp())}"

        return {
            "skill_id": skill_id,
            "type": "python_function",
            "code": code,
            "purpose": f"Optimize {metric}",
            "target_improvement": target_value,
            "generated_at": datetime.now().isoformat(),
            "model": self.model
        }
