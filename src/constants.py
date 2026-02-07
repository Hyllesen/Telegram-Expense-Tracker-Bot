"""Constants for system prompts, messages, and configuration."""
from datetime import datetime

# Gemini System Prompt for Expense Extraction
EXPENSE_EXTRACTION_PROMPT = f"""You are an expense tracking assistant. Extract structured expense data from the provided input (text, image, or audio).

Current date: {datetime.now().strftime('%Y-%m-%d')}

Output MUST be valid JSON matching this exact schema:
{{
  "date": "YYYY-MM-DD",
  "item": "string",
  "amount": float,
  "currency": "string",
  "paid_by": "string"
}}

RULES:
1. **Date**: If date is mentioned, use it. Otherwise, use today's date ({datetime.now().strftime('%Y-%m-%d')}).
2. **Item**: Brief description of what was purchased (e.g., "Coffee", "Groceries", "Gas").
3. **Amount**: Numeric value only (e.g., 45.50, 100).
4. **Currency**: ISO code or common abbreviation (e.g., "USD", "PHP", "EUR", "Peso").
5. **Paid By**: 
   - If text/caption/audio says "Paid by [Name]" or "Bought by [Name]" or "[Name] paid", extract [Name]
   - If no name mentioned, default to "Me"
   - Common variations: "Stefan paid", "paid by Tine", "John bought this"

For images:
- Read text from receipts (OCR)
- Extract total amount, date, items
- Consider both image content AND any caption text together

For voice/audio:
- Transcribe the audio
- Extract expense details from transcription

Return ONLY the JSON object, no additional text or explanation.
"""

# Bot Command Messages
MESSAGE_START = """👋 Welcome to the Expense Tracker Bot!

I help you track expenses using AI. Just send me:
📝 Text: "Coffee 5.50 USD"
📸 Receipt photos (with optional caption)
🎤 Voice notes: "Paid 100 pesos for groceries"

I'll automatically extract and log your expenses to Google Sheets!

Use /help to see more examples."""

MESSAGE_HELP = """📖 **How to Use the Expense Tracker Bot**

**Text Messages:**
• "Lunch at restaurant 25.50 USD"
• "Paid by John: Gas 50 EUR"
• "Coffee 5 dollars"

**Receipt Images:**
• Send photo of receipt
• Add caption: "Paid by Sarah"
• Or just send without caption (defaults to "Me")

**Voice Notes:**
• Record: "Stefan paid 100 pesos for bananas"
• Or: "Bought fish for 75 PHP"

**Commands:**
• /start - Show welcome message
• /help - Show this help text
• /summary - View last 10 expenses

**"Paid By" Logic:**
If you mention a name (e.g., "Paid by John"), I'll log it.
Otherwise, I'll default to "Me".

🤖 Powered by Google Gemini AI"""

MESSAGE_PROCESSING = "⏳ Processing your expense..."

MESSAGE_ERROR_GENERIC = "❌ Oops! Something went wrong. Please try again."

MESSAGE_ERROR_INVALID_FILE = "❌ Sorry, I couldn't process that file. Please try again."

MESSAGE_ERROR_SHEET_ACCESS = "❌ Unable to access Google Sheets. Please contact admin."

MESSAGE_NO_SUMMARY_DATA = "📊 No expenses found in the sheet yet. Start logging!"

# Response Templates
def format_confirmation_message(expense_data: dict) -> str:
    """Format a confirmation message for logged expense."""
    return f"""✅ **Expense Logged!**

📅 Date: {expense_data.get('date', 'N/A')}
🛒 Item: {expense_data.get('item', 'N/A')}
💰 Amount: {expense_data.get('amount', 'N/A')} {expense_data.get('currency', '')}
👤 Paid By: {expense_data.get('paid_by', 'Me')}

Saved to Google Sheets! 📊"""


def format_summary_message(expenses: list) -> str:
    """Format a summary message for recent expenses."""
    if not expenses:
        return MESSAGE_NO_SUMMARY_DATA
    
    message = "📊 **Recent Expenses (Last 10)**\n\n"
    for idx, expense in enumerate(expenses, 1):
        message += f"{idx}. {expense[1]} - {expense[2]} {expense[3]} - {expense[4]} ({expense[0]})\n"
    
    return message
