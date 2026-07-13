"""
UNITGROUP AI - TELEGRAM MEDIA BOT CONFIGURATION
For @Media_Unitgroup_bot managing @UnitgroupAI channel
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
(DATA_DIR / "post_drafts").mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MEDIA BOT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Bot credentials
BOT_TOKEN = os.getenv("TELEGRAM_MEDIA_BOT_TOKEN") or os.getenv("MEDIA_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_MEDIA_BOT_TOKEN or MEDIA_BOT_TOKEN not configured in .env")

# Channel configuration
CHANNEL_USERNAME = os.getenv("TELEGRAM_CHANNEL_USERNAME", "@UnitgroupAI")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "-1004497671254")
if not CHANNEL_ID.startswith("-100"):
    CHANNEL_ID = f"-100{CHANNEL_ID}"

# Safety & Approval workflow
DRY_RUN_MODE = os.getenv("TELEGRAM_DRY_RUN", "true").lower() in ("true", "1", "yes")
REQUIRE_APPROVAL = os.getenv("TELEGRAM_REQUIRE_APPROVAL", "true").lower() in ("true", "1", "yes")
ALLOW_AUTO_PUBLISH = False  # HARDCODED - Never auto-publish

# Logging & Storage
POST_LOG_PATH = os.getenv("TELEGRAM_POST_LOG_PATH", str(LOGS_DIR / "telegram_posts.jsonl"))
DRAFT_STORAGE_PATH = os.getenv("TELEGRAM_DRAFT_STORAGE_PATH", str(DATA_DIR / "post_drafts"))
BOT_LOG_PATH = str(LOGS_DIR / "telegram_media_bot.log")

# Create log directory
LOGS_DIR.mkdir(exist_ok=True)

# News sources
NEWS_SOURCES_PATH = os.getenv("NEWS_SOURCES_PATH", str(DATA_DIR / "media_sources.yaml"))

# ═══════════════════════════════════════════════════════════════════════════════
# SAFETY GUARANTEES (DO NOT CHANGE)
# ═══════════════════════════════════════════════════════════════════════════════

class SafetyGuarantees:
    """Safety settings that CANNOT be disabled"""

    # Auto-publish is NEVER allowed
    AUTO_PUBLISH_ENABLED = False

    # Approval is ALWAYS required
    APPROVAL_MANDATORY = True

    # Dry-run mode default (can be overridden but approval still required)
    DRY_RUN_DEFAULT = DRY_RUN_MODE

    # Channel cannot be changed without code changes
    IMMUTABLE_CHANNEL = CHANNEL_USERNAME

    @staticmethod
    def validate():
        """Validate safety settings at startup"""
        assert not SafetyGuarantees.AUTO_PUBLISH_ENABLED, "Auto-publish must never be enabled"
        assert SafetyGuarantees.APPROVAL_MANDATORY, "Approval must always be required"
        assert CHANNEL_USERNAME == "@UnitgroupAI", "Channel must be @UnitgroupAI"
        return True

# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE FLAGS & SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Features
ENABLE_NEWS_FETCHING = True
ENABLE_DRAFT_CREATION = True
ENABLE_APPROVAL_WORKFLOW = True
ENABLE_DRY_RUN = DRY_RUN_MODE

# Admin settings
ADMIN_IDS = []
if os.getenv("TELEGRAM_MEDIA_ADMIN_IDS"):
    ADMIN_IDS = [int(id) for id in os.getenv("TELEGRAM_MEDIA_ADMIN_IDS").split(",")]

# News settings
MIN_NEWS_SCORE = 6  # Minimum score for draft creation
DEFAULT_FETCH_LIMIT = 50  # Max sources to fetch per run
FETCH_TIMEOUT = 30  # Seconds
REWRITE_RULES_PATH = str(BASE_DIR / "skills" / "news_rewrite_for_telegram_skill.md")

# ═══════════════════════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

def validate_media_bot_config():
    """Validate all required configuration at startup"""

    required = {
        "BOT_TOKEN": BOT_TOKEN,
        "CHANNEL_USERNAME": CHANNEL_USERNAME,
        "CHANNEL_ID": CHANNEL_ID,
    }

    missing = {k: v for k, v in required.items() if not v}

    if missing:
        raise ValueError(f"Missing required Media Bot config: {', '.join(missing.keys())}")

    # Validate safety
    SafetyGuarantees.validate()

    # Validate paths exist
    if not os.path.exists(NEWS_SOURCES_PATH):
        raise FileNotFoundError(f"News sources config not found: {NEWS_SOURCES_PATH}")

    return True

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION SUMMARY (Logged at startup)
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG_SUMMARY = f"""
╔════════════════════════════════════════════════════════════════╗
║          TELEGRAM MEDIA BOT CONFIGURATION                     ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Bot: @Media_Unitgroup_bot                                    ║
║  Channel: {CHANNEL_USERNAME}                                     ║
║  Channel ID: {CHANNEL_ID}                                  ║
║                                                                ║
║  🔐 SAFETY SETTINGS (HARDCODED):                              ║
║  ✅ Auto-publish: DISABLED                                    ║
║  ✅ Approval required: YES                                    ║
║  ✅ Dry-run mode: {'ENABLED' if DRY_RUN_MODE else 'DISABLED'}                                  ║
║                                                                ║
║  📝 LOGGING:                                                   ║
║  ✅ Event log: {POST_LOG_PATH}           ║
║  ✅ Bot log: {BOT_LOG_PATH}                    ║
║  ✅ Drafts: {DRAFT_STORAGE_PATH}                  ║
║                                                                ║
║  📰 NEWS SOURCES:                                              ║
║  ✅ Config: {NEWS_SOURCES_PATH}            ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
"""

# Validate on import
validate_media_bot_config()
