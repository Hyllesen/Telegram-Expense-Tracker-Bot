"""Google Sheets handler for expense logging."""
from typing import Dict, Any, List
import gspread
from google.oauth2.service_account import Credentials

from src.config import GOOGLE_SHEETS_CREDS_FILE, GOOGLE_SHEET_NAME, SUMMARY_LIMIT
from src.logger import get_logger

logger = get_logger(__name__)

# Google Sheets API scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


class SheetsHandler:
    """Handler for Google Sheets operations."""
    
    def __init__(self):
        """Initialize the Sheets handler with service account credentials."""
        try:
            logger.info(f"Initializing Google Sheets client with: {GOOGLE_SHEETS_CREDS_FILE}")
            
            # Authenticate with service account
            creds = Credentials.from_service_account_file(
                GOOGLE_SHEETS_CREDS_FILE,
                scopes=SCOPES
            )
            self.client = gspread.authorize(creds)
            
            logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            raise
    
    def get_sheet(self):
        """
        Get the configured Google Sheet.
        
        Returns:
            Worksheet object
            
        Raises:
            Exception: If sheet cannot be accessed
        """
        try:
            logger.debug(f"Accessing sheet: {GOOGLE_SHEET_NAME}")
            
            # Open sheet by name
            spreadsheet = self.client.open(GOOGLE_SHEET_NAME)
            
            # Get first worksheet
            worksheet = spreadsheet.sheet1
            
            logger.info(f"Successfully accessed sheet: {GOOGLE_SHEET_NAME}")
            return worksheet
            
        except gspread.SpreadsheetNotFound:
            logger.error(f"Sheet not found: {GOOGLE_SHEET_NAME}")
            raise Exception(f"Sheet '{GOOGLE_SHEET_NAME}' not found. Please check the name in .env")
        except Exception as e:
            logger.error(f"Error accessing sheet: {e}")
            raise
    
    def add_expense(self, expense_data: Dict[str, Any]) -> bool:
        """
        Add expense row to Google Sheet.
        
        Args:
            expense_data: Dictionary with keys: date, item, amount, paid_by
            
        Returns:
            True if successful
            
        Raises:
            Exception: If adding expense fails
        """
        try:
            logger.info(f"Adding expense to sheet: {expense_data}")
            
            # Get worksheet
            worksheet = self.get_sheet()
            
            # Format row: [Date, Item, Amount, Paid By]
            row = [
                expense_data.get('date', ''),
                expense_data.get('item', ''),
                expense_data.get('amount', 0),
                expense_data.get('paid_by', 'Me')
            ]
            
            # Append row to sheet
            worksheet.append_row(row, value_input_option='USER_ENTERED')
            
            logger.info(f"Successfully added expense row: {row}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding expense to sheet: {e}")
            raise
    
    def get_recent_expenses(self, limit: int = SUMMARY_LIMIT) -> List[List[str]]:
        """
        Get recent expenses from the sheet.
        
        Args:
            limit: Maximum number of expenses to retrieve
            
        Returns:
            List of expense rows (each row is a list)
        """
        try:
            logger.debug(f"Fetching last {limit} expenses")
            
            # Get worksheet
            worksheet = self.get_sheet()
            
            # Get all values
            all_values = worksheet.get_all_values()
            
            # Skip header row and get last N rows
            if len(all_values) <= 1:
                logger.info("No expense data found in sheet")
                return []
            
            # Get last N rows (excluding header)
            expenses = all_values[1:]  # Skip header
            recent = expenses[-limit:] if len(expenses) > limit else expenses
            
            # Reverse to show most recent first
            recent.reverse()
            
            logger.info(f"Retrieved {len(recent)} recent expenses")
            return recent
            
        except Exception as e:
            logger.error(f"Error fetching recent expenses: {e}")
            return []
    
    def verify_sheet_access(self) -> bool:
        """
        Verify that the sheet is accessible and properly configured.
        
        Returns:
            True if accessible, False otherwise
        """
        try:
            worksheet = self.get_sheet()
            
            # Check if header row exists
            headers = worksheet.row_values(1)
            
            expected_headers = ['Date', 'Item', 'Amount', 'Paid By']
            
            if not headers:
                logger.warning("Sheet has no headers. Creating header row...")
                worksheet.append_row(expected_headers)
                logger.info("Header row created")
            elif headers != expected_headers:
                logger.warning(f"Sheet headers mismatch. Expected: {expected_headers}, Got: {headers}")
            
            logger.info("Sheet access verified successfully")
            return True
            
        except Exception as e:
            logger.error(f"Sheet verification failed: {e}")
            return False


# Singleton instance
_sheets_handler = None


def get_sheets_handler() -> SheetsHandler:
    """Get or create singleton Sheets handler instance."""
    global _sheets_handler
    if _sheets_handler is None:
        _sheets_handler = SheetsHandler()
    return _sheets_handler
