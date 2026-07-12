"""Skill manager - handles skill creation, validation, and deployment"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from master_agent.safety import SkillValidator
from master_agent.skill_registry import SkillRegistry

class SkillManager:
    def __init__(self, skills_dir: str = "data/skills", registry_path: str = "data/skills.json"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.registry = SkillRegistry(registry_path)
        self.validator = SkillValidator()

    def create_python_skill(self, skill_id: str, code: str, dependencies: list = None) -> dict | None:
        """Create and validate a Python skill"""
        # Validate code
        valid, message = self.validator.validate_python_code(code)
        if not valid:
            return {"error": f"Validation failed: {message}"}

        # Create skill metadata
        skill = {
            "skill_id": skill_id,
            "type": "python_function",
            "code": code,
            "dependencies": dependencies or [],
            "created_at": datetime.now().isoformat(),
            "code_hash": hashlib.sha256(code.encode()).hexdigest()[:8],
            "auto_activate": True
        }

        # Add to registry
        if not self.registry.add_skill(skill):
            return {"error": f"Skill {skill_id} already exists"}

        # Save code file
        skill_file = self.skills_dir / f"{skill_id}.py"
        with open(skill_file, 'w') as f:
            f.write(code)

        return skill

    def create_systemd_skill(self, skill_id: str, service_content: str) -> dict | None:
        """Create and validate a systemd service skill"""
        # Validate service
        valid, message = self.validator.validate_systemd_service(service_content)
        if not valid:
            return {"error": f"Validation failed: {message}"}

        skill = {
            "skill_id": skill_id,
            "type": "systemd_service",
            "service_content": service_content,
            "created_at": datetime.now().isoformat(),
            "content_hash": hashlib.sha256(service_content.encode()).hexdigest()[:8],
            "auto_activate": False
        }

        if not self.registry.add_skill(skill):
            return {"error": f"Skill {skill_id} already exists"}

        skill_file = self.skills_dir / f"{skill_id}.service"
        with open(skill_file, 'w') as f:
            f.write(service_content)

        return skill

    def get_skill_for_vps(self, skill_id: str) -> dict | None:
        """Get skill packaged for VPS installation"""
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return None

        # Load code/content if needed
        if skill['type'] == 'python_function':
            skill_file = self.skills_dir / f"{skill_id}.py"
            if skill_file.exists():
                with open(skill_file, 'r') as f:
                    skill['code'] = f.read()

        elif skill['type'] == 'systemd_service':
            skill_file = self.skills_dir / f"{skill_id}.service"
            if skill_file.exists():
                with open(skill_file, 'r') as f:
                    skill['service_content'] = f.read()

        return skill

    def install_skill_report(self, agent_id: str, skill_id: str, success: bool, message: str = None):
        """Record skill installation result"""
        if success:
            self.registry.mark_installed(skill_id, agent_id)
            status = "installed"
        else:
            status = "failed"

        # Log report
        report = {
            "agent_id": agent_id,
            "skill_id": skill_id,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        reports_file = self.skills_dir.parent / "skill_installation_reports.jsonl"
        with open(reports_file, 'a') as f:
            f.write(json.dumps(report) + "\n")

        return report

    def list_all_skills(self) -> list:
        """List all available skills"""
        return self.registry.list_skills()

    def get_agent_capabilities(self, agent_id: str) -> dict:
        """Get all capabilities (skills) of an agent"""
        skills = self.registry.get_agent_skills(agent_id)
        return {
            "agent_id": agent_id,
            "skill_count": len(skills),
            "skills": [{"skill_id": s["skill_id"], "type": s["type"]} for s in skills]
        }
