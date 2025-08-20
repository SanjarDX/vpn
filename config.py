import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# Bot settings
BOT_NAME = "FoxVPN"
BOT_DESCRIPTION = "Откройте мир безопасности и приватности с нами!"
