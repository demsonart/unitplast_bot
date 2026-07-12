"""Base Agent class - foundation for all autonomous agents"""
import json
import logging
from datetime import datetime
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO)

class BaseAgent(ABC):
    def __init__(self, agent_id: str, master_url: str = "http://127.0.0.1:8888",
                 master_token: str = None, log_file: str = None):
        self.agent_id = agent_id
        self.master_url = master_url
        self.master_token = master_token or "unitplast_master_key_2026"
        self.logger = logging.getLogger(agent_id)
        self.skills = {}
        self.start_time = datetime.now()

        # Setup logging
        if log_file:
            handler = logging.FileHandler(log_file)
            self.logger.addHandler(handler)

    @abstractmethod
    def run(self):
        """Main agent loop - implement in subclass"""
        pass

    def request_skill(self, issue: str, skill_type: str = "python_function",
                     error_log: str = None, context: dict = None) -> dict | None:
        """Request a skill from Master Agent"""
        import requests

        url = f"{self.master_url}/api/request_skill"
        headers = {"Authorization": f"Bearer {self.master_token}"}

        payload = {
            "agent_id": self.agent_id,
            "issue": issue,
            "skill_type": skill_type,
            "error_log": error_log,
            "context": context or {}
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code in [200, 201]:
                return response.json()
            else:
                self.logger.error(f"Skill request failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Skill request exception: {e}")
            return None

    def get_skill(self, skill_id: str) -> dict | None:
        """Download specific skill from Master Agent"""
        import requests

        url = f"{self.master_url}/api/skill/{skill_id}"
        headers = {"Authorization": f"Bearer {self.master_token}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Skill download failed: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Skill download exception: {e}")
            return None

    def install_skill(self, skill_data: dict) -> bool:
        """Install skill locally and execute"""
        try:
            skill_id = skill_data.get('skill_id')
            skill_type = skill_data.get('type')

            if skill_type == 'python_function':
                code = skill_data.get('code')
                # Execute code in agent's namespace
                exec(code, globals())
                self.skills[skill_id] = code
                self.logger.info(f"Skill {skill_id} installed successfully")
                return True

            elif skill_type == 'systemd_service':
                # Save service file
                service_content = skill_data.get('service_content')
                service_file = f"/etc/systemd/system/{skill_id}.service"
                # Note: actual installation requires sudo, would be done by Master Agent
                self.logger.info(f"Systemd service {skill_id} ready for installation")
                return True

            else:
                self.logger.error(f"Unknown skill type: {skill_type}")
                return False

        except Exception as e:
            self.logger.error(f"Skill installation failed: {e}")
            return False

    def report_skill_installation(self, skill_id: str, success: bool, message: str = None) -> bool:
        """Report installation result to Master Agent"""
        import requests

        url = f"{self.master_url}/api/report_installation"
        headers = {"Authorization": f"Bearer {self.master_token}"}

        payload = {
            "agent_id": self.agent_id,
            "skill_id": skill_id,
            "success": success,
            "message": message
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Installation report failed: {e}")
            return False

    def get_capabilities(self) -> dict:
        """Get list of installed skills"""
        import requests

        url = f"{self.master_url}/api/agent/{self.agent_id}/capabilities"
        headers = {"Authorization": f"Bearer {self.master_token}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Failed to get capabilities"}
        except Exception as e:
            self.logger.error(f"Get capabilities failed: {e}")
            return {"error": str(e)}

    def log_event(self, event_type: str, data: dict):
        """Log event with timestamp"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "event_type": event_type,
            "data": data
        }
        self.logger.info(json.dumps(event))
        return event

    def uptime(self) -> float:
        """Get uptime in seconds"""
        return (datetime.now() - self.start_time).total_seconds()

    def status(self) -> dict:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "status": "running",
            "uptime_seconds": self.uptime(),
            "skill_count": len(self.skills),
            "timestamp": datetime.now().isoformat()
        }
