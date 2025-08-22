import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# Bot settings
BOT_NAME = "FoxVPN"
BOT_DESCRIPTION = "Откройте мир безопасности и приватности с нами!"

# Marzban settings
MARZBAN_URL = os.getenv("MARZBAN_URL", "http://localhost:8000")
MARZBAN_USERNAME = os.getenv("MARZBAN_USERNAME", "admin")
MARZBAN_PASSWORD = os.getenv("MARZBAN_PASSWORD")

if not MARZBAN_PASSWORD:
    raise ValueError("MARZBAN_PASSWORD environment variable is not set")
