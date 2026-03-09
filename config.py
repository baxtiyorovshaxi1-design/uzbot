"""
⚙️ Bot Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot Settings
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Admin IDs (comma separated in .env)
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip()]

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "bot_database.db")

# Shazam / Music Recognition
# Uses shazamio library (free, no API key needed)

# Download settings
MAX_FILE_SIZE_MB = 50  # Telegram limit
DOWNLOAD_TIMEOUT = 120  # seconds

# Uzbekistan regions
UZBEKISTAN_REGIONS = [
    "Toshkent shahri",
    "Toshkent viloyati",
    "Samarqand",
    "Buxoro",
    "Andijon",
    "Farg'ona",
    "Namangan",
    "Qashqadaryo",
    "Surxondaryo",
    "Xorazm",
    "Navoiy",
    "Jizzax",
    "Sirdaryo",
    "Qoraqalpog'iston"
]
