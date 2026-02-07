"""Main entry point for the Telegram Expense Tracker Bot."""
import sys
import signal
from src.bot import ExpenseBot
from src.logger import setup_logging, get_logger
from src.sheets_handler import get_sheets_handler
from src.config import (
    TELEGRAM_BOT_TOKEN,
    GEMINI_API_KEY,
    GOOGLE_SHEETS_CREDS_FILE,
    GOOGLE_SHEET_NAME,
    GEMINI_MODEL
)

# Setup logging
setup_logging()
logger = get_logger(__name__)


def validate_configuration():
    """Validate that all required configuration is present."""
    logger.info("Validating configuration...")
    
    errors = []
    
    # Check required environment variables
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is not set")
    
    if not GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY is not set")
    
    if not GOOGLE_SHEETS_CREDS_FILE:
        errors.append("GOOGLE_SHEETS_CREDS_FILE is not set")
    
    if errors:
        for error in errors:
            logger.error(f"Configuration error: {error}")
        return False
    
    logger.info("✓ Environment variables validated")
    return True


def verify_sheets_access():
    """Verify Google Sheets access on startup."""
    logger.info("Verifying Google Sheets access...")
    
    try:
        sheets_handler = get_sheets_handler()
        
        if sheets_handler.verify_sheet_access():
            logger.info(f"✓ Successfully connected to sheet: {GOOGLE_SHEET_NAME}")
            return True
        else:
            logger.error(f"✗ Failed to verify sheet access: {GOOGLE_SHEET_NAME}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Sheet verification failed: {e}")
        logger.error("Please check:")
        logger.error(f"  1. Service account credentials file: {GOOGLE_SHEETS_CREDS_FILE}")
        logger.error(f"  2. Sheet name in .env: {GOOGLE_SHEET_NAME}")
        logger.error("  3. Service account has edit access to the sheet")
        return False


def main():
    """Main function to run the bot."""
    logger.info("=" * 60)
    logger.info("Starting Telegram Expense Tracker Bot")
    logger.info("=" * 60)
    logger.info(f"Gemini Model: {GEMINI_MODEL}")
    logger.info(f"Sheet Name: {GOOGLE_SHEET_NAME}")
    logger.info("-" * 60)
    
    # Validate configuration
    if not validate_configuration():
        logger.error("Configuration validation failed. Please check your .env file.")
        sys.exit(1)
    
    # Verify sheets access
    if not verify_sheets_access():
        logger.error("Google Sheets verification failed. Please check your setup.")
        sys.exit(1)
    
    # Initialize and run bot
    try:
        logger.info("Initializing bot...")
        bot = ExpenseBot()
        
        logger.info("✓ Bot initialized successfully")
        logger.info("=" * 60)
        logger.info("Bot is running! Press Ctrl+C to stop.")
        logger.info("=" * 60)
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("\nReceived shutdown signal. Stopping bot...")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Run the bot
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
