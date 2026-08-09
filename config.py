import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Command prefix configuration
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", ".")

# Whitelisted User IDs allowed to execute self-bot commands
_whitelisted_raw = os.getenv("WHITELISTED_USERS", "")
WHITELISTED_USERS = [
    int(uid.strip()) for uid in _whitelisted_raw.split(",") if uid.strip().isdigit()
]

# Startup notification target Chat ID
_startup_chat = os.getenv("STARTUP_NOTIFICATION_CHAT", "")
STARTUP_NOTIFICATION_CHAT = int(_startup_chat) if _startup_chat.isdigit() else None