"""Skill Requester - handles skill requests and installation"""
import json
import requests
from datetime import datetime
from typing import Callable

class SkillRequester:
    def __init__(self, agent_id: str, master_url: str, master_token: str):
        self.agent_id = agent_id
        self.master_url = master_url
        self.master_token = master_token
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {master_token}"})

    def request_healing_skill(self, issue: str, error_log: str = None) -> dict | None:
        """Request a healing skill for specific issue"""
        url = f"{self.master_url}/api/request_skill"
        payload = {
            "agent_id": self.agent_id,
            "issue": issue,
            "skill_type": "healing",
            "error_log": error_log
        }

        try:
            response = self.session.post(url, json=payload, timeout=30)
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            print(f"Error requesting healing skill: {e}")
            return None

    def request_optimization_skill(self, metric: str, current_value: float,
                                   target_value: float) -> dict | None:
        """Request optimization skill for specific metric"""
        url = f"{self.master_url}/api/request_skill"
        payload = {
            "agent_id": self.agent_id,
            "issue": metric,
            "skill_type": "optimization",
            "current_value": current_value,
            "target_value": target_value
        }

        try:
            response = self.session.post(url, json=payload, timeout=30)
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception as e:
            print(f"Error requesting optimization skill: {e}")
            return None

    def get_skill(self, skill_id: str) -> dict | None:
        """Download skill code/content"""
        url = f"{self.master_url}/api/skill/{skill_id}"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error downloading skill: {e}")
            return None

    def install_and_execute(self, skill_data: dict, execute_func: Callable = None) -> bool:
        """Install skill and optionally execute it"""
        if not skill_data:
            return False

        skill_id = skill_data.get('skill_id')
        skill_type = skill_data.get('type')

        try:
            if skill_type == 'python_function':
                code = skill_data.get('code')
                if execute_func:
                    result = execute_func(code)
                else:
                    # Default: execute in current namespace
                    result = exec(code)
                success = result is not None
            else:
                success = False

            # Report back
            self.report_installation(skill_id, success)
            return success

        except Exception as e:
            print(f"Error installing skill {skill_id}: {e}")
            self.report_installation(skill_id, False, str(e))
            return False

    def report_installation(self, skill_id: str, success: bool, message: str = None) -> bool:
        """Report installation result"""
        url = f"{self.master_url}/api/report_installation"
        payload = {
            "agent_id": self.agent_id,
            "skill_id": skill_id,
            "success": success,
            "message": message
        }

        try:
            response = self.session.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error reporting installation: {e}")
            return False

    def list_available_skills(self) -> list | None:
        """Get all available skills from Master"""
        url = f"{self.master_url}/api/skills"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('skills', [])
            return None
        except Exception as e:
            print(f"Error listing skills: {e}")
            return None

    def get_my_skills(self) -> list | None:
        """Get skills installed on this agent"""
        url = f"{self.master_url}/api/agent/{self.agent_id}/capabilities"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('skills', [])
            return None
        except Exception as e:
            print(f"Error getting my skills: {e}")
            return None

    def is_master_online(self) -> bool:
        """Check if Master Agent is accessible"""
        url = f"{self.master_url}/health"
        try:
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
