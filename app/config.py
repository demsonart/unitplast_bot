import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "unitplast.db"))

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Telegram (Main Bot)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = int(os.getenv("TELEGRAM_GROUP_ID", 0))
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", 0))

# Telegram Media Bot (Industry News)
TELEGRAM_MEDIA_BOT_TOKEN = os.getenv("TELEGRAM_MEDIA_BOT_TOKEN") or os.getenv("MEDIA_BOT_TOKEN")
TELEGRAM_CHANNEL_USERNAME = os.getenv("TELEGRAM_CHANNEL_USERNAME", "@UnitgroupAI")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
TELEGRAM_DRY_RUN = os.getenv("TELEGRAM_DRY_RUN", "true").lower() in ("true", "1", "yes")
TELEGRAM_REQUIRE_APPROVAL = os.getenv("TELEGRAM_REQUIRE_APPROVAL", "true").lower() in ("true", "1", "yes")
TELEGRAM_POST_LOG_PATH = os.getenv("TELEGRAM_POST_LOG_PATH", str(BASE_DIR / "logs" / "telegram_posts.jsonl"))
TELEGRAM_DRAFT_STORAGE_PATH = os.getenv("TELEGRAM_DRAFT_STORAGE_PATH", str(DATA_DIR / "post_drafts"))

# Yandex Mail
YANDEX_EMAIL = os.getenv("YANDEX_EMAIL")
YANDEX_PASSWORD = os.getenv("YANDEX_PASSWORD")
YANDEX_IMAP_SERVER = os.getenv("YANDEX_IMAP_SERVER", "imap.yandex.ru")
YANDEX_IMAP_PORT = int(os.getenv("YANDEX_IMAP_PORT", 993))

# AI Mode
ENABLE_AI = os.getenv("ENABLE_AI", "false").lower() in ("true", "1", "yes")

# Anthropic (optional, only needed if ENABLE_AI=true)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Company
COMPANY_NAME = os.getenv("COMPANY_NAME", "Юнитпласт")
COMPANY_EMAIL = os.getenv("COMPANY_EMAIL", "id@unitplast.ru")
COMPANY_EMAIL_SECONDARY = os.getenv("COMPANY_EMAIL_SECONDARY", "info@unitplast.ru")
COMPANY_PHONE = os.getenv("COMPANY_PHONE", "+7 (495) 924-50-96")
COMPANY_SITE = os.getenv("COMPANY_SITE", "www.unitplast.ru")
COMPANY_ADDRESS = os.getenv("COMPANY_ADDRESS", "г. Долгопрудный, ул. Летная, д. 1, территория «ДКБА»")
COMPANY_LEGAL_NAME = os.getenv("COMPANY_LEGAL_NAME", "ИП Демин И. А.")

# Email processing
PROCESS_ONLY_UNSEEN = os.getenv("PROCESS_ONLY_UNSEEN", "false").lower() in ("true", "1", "yes")
EMAIL_CHECK_INTERVAL = int(os.getenv("EMAIL_CHECK_INTERVAL", "300"))

# Server
PORT = int(os.getenv("PORT", 5000))

# Validation
def validate_config():
    required = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_GROUP_ID",
        "YANDEX_EMAIL",
        "YANDEX_PASSWORD",
    ]
    missing = [var for var in required if not os.getenv(var)]

    if ENABLE_AI and not os.getenv("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
