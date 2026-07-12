"""Master Agent Configuration"""
import os
from pathlib import Path

# Server settings
MASTER_HOST = os.getenv("MASTER_AGENT_HOST", "127.0.0.1")
MASTER_PORT = int(os.getenv("MASTER_AGENT_PORT", 8888))
MASTER_URL = f"http://{MASTER_HOST}:{MASTER_PORT}"

# Authentication
AUTH_TOKEN = os.getenv("MASTER_AGENT_TOKEN", "unitplast_master_key_2026")

# Claude API
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-8")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / "data" / "skills"
SKILLS_REGISTRY = PROJECT_ROOT / "data" / "skills.json"
SKILLS_REPORTS = PROJECT_ROOT / "data" / "skill_installation_reports.jsonl"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# VPS Configuration
VPS_HOST = os.getenv("VPS_HOST", "193.104.33.29")
VPS_PORT = int(os.getenv("VPS_PORT", 9000))
VPS_API_URL = f"http://{VPS_HOST}:{VPS_PORT}"
VPS_SSH_USER = os.getenv("VPS_SSH_USER", "unitplast")
VPS_SSH_KEY = os.getenv("VPS_SSH_KEY")

# Safety settings
SKILL_TIMEOUT = 30  # seconds
MAX_SKILL_SIZE = 10000  # bytes
ENABLE_SKILL_EXECUTION = True
ENABLE_ROLLBACK = True

# Features
ENABLE_AUTO_GENERATION = True
ENABLE_AUTO_INSTALLATION = False
AUTO_INSTALL_ON_ERROR = True
AUTO_HEAL_ON_FAILURE = True

# Maintenance
CLEANUP_FAILED_SKILLS_AFTER_DAYS = 7
BACKUP_SKILLS_ON_UPDATE = True

print(f"Master Agent Config Loaded")
print(f"  Host: {MASTER_HOST}:{MASTER_PORT}")
print(f"  VPS: {VPS_HOST}:{VPS_PORT}")
print(f"  Auth: {AUTH_TOKEN[:10]}...")
