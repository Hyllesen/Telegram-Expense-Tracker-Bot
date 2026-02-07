"""Configuration module for loading environment variables."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if running in test mode
IS_TESTING = "pytest" in sys.modules or os.getenv("TESTING") == "1"

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN and not IS_TESTING:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env file")

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY and not IS_TESTING:
    raise ValueError("GEMINI_API_KEY is not set in .env file")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

# Google Sheets Configuration
GOOGLE_SHEETS_CREDS_FILE = os.getenv("GOOGLE_SHEETS_CREDS_FILE")
if not GOOGLE_SHEETS_CREDS_FILE and not IS_TESTING:
    raise ValueError("GOOGLE_SHEETS_CREDS_FILE is not set in .env file")

GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Expense_Tracker")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "expense_bot.log"

# Application Settings
MAX_FILE_SIZE_MB = 20  # Maximum file size for uploads
SUMMARY_LIMIT = 10  # Number of recent expenses to show in /summary
