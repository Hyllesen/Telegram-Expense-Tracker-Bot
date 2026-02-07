"""Telegram bot handlers for expense tracking."""
import os
import tempfile
from pathlib import Path
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from src.config import TELEGRAM_BOT_TOKEN
from src.constants import (
    MESSAGE_START,
    MESSAGE_HELP,
    MESSAGE_PROCESSING,
    MESSAGE_ERROR_GENERIC,
    MESSAGE_ERROR_INVALID_FILE,
    MESSAGE_ERROR_SHEET_ACCESS,
    format_confirmation_message,
    format_summary_message
)
from src.gemini_handler import get_gemini_handler
from src.sheets_handler import get_sheets_handler
from src.logger import get_logger

logger = get_logger(__name__)


class ExpenseBot:
    """Telegram bot for expense tracking."""
    
    def __init__(self):
        """Initialize the Telegram bot."""
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.gemini = get_gemini_handler()
        self.sheets = get_sheets_handler()
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Expense bot initialized")
    
    def _register_handlers(self):
        """Register all command and message handlers."""
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("summary", self.cmd_summary))
        
        # Message handlers
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        
        logger.info("Handlers registered")
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        try:
            logger.info(f"User {update.effective_user.id} started bot")
            await update.message.reply_text(MESSAGE_START)
        except Exception as e:
            logger.error(f"Error in /start: {e}")
            await update.message.reply_text(MESSAGE_ERROR_GENERIC)
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        try:
            logger.info(f"User {update.effective_user.id} requested help")
            await update.message.reply_text(MESSAGE_HELP, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in /help: {e}")
            await update.message.reply_text(MESSAGE_ERROR_GENERIC)
    
    async def cmd_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /summary command."""
        try:
            logger.info(f"User {update.effective_user.id} requested summary")
            
            # Get recent expenses from sheet
            expenses = self.sheets.get_recent_expenses()
            
            # Format and send message
            message = format_summary_message(expenses)
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in /summary: {e}")
            await update.message.reply_text(MESSAGE_ERROR_SHEET_ACCESS)
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (expense descriptions)."""
        try:
            user_id = update.effective_user.id
            user_name = update.effective_user.first_name or "Me"
            text = update.message.text
            
            logger.info(f"User {user_id} ({user_name}) sent text: {text[:50]}...")
            
            # Send processing message
            await update.message.reply_text(MESSAGE_PROCESSING)
            
            # Extract expense data using Gemini
            expense_data = self.gemini.analyze_content(text=text, default_paid_by=user_name)
            
            # Save to Google Sheets
            self.sheets.add_expense(expense_data)
            
            # Send confirmation
            confirmation = format_confirmation_message(expense_data)
            await update.message.reply_text(confirmation, parse_mode='Markdown')
            
            logger.info(f"Successfully processed text expense for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling text: {e}")
            await update.message.reply_text(MESSAGE_ERROR_GENERIC)
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages (receipt images)."""
        try:
            user_id = update.effective_user.id
            user_name = update.effective_user.first_name or "Me"
            caption = update.message.caption or ""
            
            logger.info(f"User {user_id} ({user_name}) sent photo with caption: {caption[:50] if caption else 'None'}")
            
            # Send processing message
            await update.message.reply_text(MESSAGE_PROCESSING)
            
            # Download photo (get largest size)
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                tmp_path = tmp_file.name
                await photo_file.download_to_drive(tmp_path)
            
            try:
                # Extract expense data using Gemini
                expense_data = self.gemini.analyze_content(
                    text=caption if caption else None,
                    media_path=tmp_path,
                    media_type='image',
                    default_paid_by=user_name
                )
                
                # Save to Google Sheets
                self.sheets.add_expense(expense_data)
                
                # Send confirmation
                confirmation = format_confirmation_message(expense_data)
                await update.message.reply_text(confirmation, parse_mode='Markdown')
                
                logger.info(f"Successfully processed photo expense for user {user_id}")
                
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    logger.debug(f"Cleaned up temp file: {tmp_path}")
            
        except Exception as e:
            logger.error(f"Error handling photo: {e}")
            await update.message.reply_text(MESSAGE_ERROR_INVALID_FILE)
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages (expense descriptions)."""
        try:
            user_id = update.effective_user.id
            user_name = update.effective_user.first_name or "Me"
            
            logger.info(f"User {user_id} ({user_name}) sent voice message")
            
            # Send processing message
            await update.message.reply_text(MESSAGE_PROCESSING)
            
            # Download voice file (OGG format)
            voice_file = await update.message.voice.get_file()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as tmp_file:
                tmp_path = tmp_file.name
                await voice_file.download_to_drive(tmp_path)
            
            try:
                # Extract expense data using Gemini
                expense_data = self.gemini.analyze_content(
                    media_path=tmp_path,
                    media_type='audio',
                    default_paid_by=user_name
                )
                
                # Save to Google Sheets
                self.sheets.add_expense(expense_data)
                
                # Send confirmation
                confirmation = format_confirmation_message(expense_data)
                await update.message.reply_text(confirmation, parse_mode='Markdown')
                
                logger.info(f"Successfully processed voice expense for user {user_id}")
                
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    logger.debug(f"Cleaned up temp file: {tmp_path}")
            
        except Exception as e:
            logger.error(f"Error handling voice: {e}")
            await update.message.reply_text(MESSAGE_ERROR_INVALID_FILE)
    
    def run(self):
        """Start the bot."""
        logger.info("Starting Telegram bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down bot...")
        await self.app.stop()
        await self.app.shutdown()
