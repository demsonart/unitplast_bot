"""Skill registry - manages available and installed skills"""
import json
import os
from datetime import datetime
from pathlib import Path

class SkillRegistry:
    def __init__(self, registry_path: str = "data/skills.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.skills = self._load_registry()

    def _load_registry(self) -> dict:
        """Load skills from JSON file"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {"skills": [], "metadata": {"created_at": datetime.now().isoformat()}}

    def _save_registry(self):
        """Save skills to JSON file"""
        with open(self.registry_path, 'w') as f:
            json.dump(self.skills, f, indent=2)

    def add_skill(self, skill_data: dict) -> bool:
        """Add new skill to registry"""
        skill_id = skill_data.get('skill_id')

        # Check if skill already exists
        for skill in self.skills['skills']:
            if skill['skill_id'] == skill_id:
                return False  # Skill already exists

        # Add timestamp
        skill_data['registered_at'] = datetime.now().isoformat()
        skill_data['status'] = 'registered'

        self.skills['skills'].append(skill_data)
        self._save_registry()
        return True

    def get_skill(self, skill_id: str) -> dict | None:
        """Retrieve skill by ID"""
        for skill in self.skills['skills']:
            if skill['skill_id'] == skill_id:
                return skill
        return None

    def list_skills(self) -> list:
        """List all available skills"""
        return self.skills.get('skills', [])

    def update_skill_status(self, skill_id: str, status: str) -> bool:
        """Update skill installation status"""
        for skill in self.skills['skills']:
            if skill['skill_id'] == skill_id:
                skill['status'] = status
                skill['updated_at'] = datetime.now().isoformat()
                self._save_registry()
                return True
        return False

    def mark_installed(self, skill_id: str, agent_id: str) -> bool:
        """Mark skill as installed on agent"""
        for skill in self.skills['skills']:
            if skill['skill_id'] == skill_id:
                if 'installed_on' not in skill:
                    skill['installed_on'] = []

                # Check if already installed
                for inst in skill['installed_on']:
                    if inst['agent_id'] == agent_id:
                        return False

                skill['installed_on'].append({
                    'agent_id': agent_id,
                    'timestamp': datetime.now().isoformat()
                })
                self.update_skill_status(skill_id, 'active')
                return True
        return False

    def get_agent_skills(self, agent_id: str) -> list:
        """Get all skills installed on specific agent"""
        agent_skills = []
        for skill in self.skills['skills']:
            if 'installed_on' in skill:
                for inst in skill['installed_on']:
                    if inst['agent_id'] == agent_id:
                        agent_skills.append(skill)
        return agent_skills

    def skill_exists(self, skill_id: str) -> bool:
        """Check if skill is in registry"""
        return self.get_skill(skill_id) is not None
