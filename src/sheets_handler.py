"""Google Sheets handler for expense logging."""
from datetime import datetime
from typing import Dict, Any, List, Optional
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

# Monthly worksheet layout
FULL_HEADERS = ['Date', 'Description', 'Amount', 'Paid By', '', 'Total Stefan Paid']
FORMULA_STEFAN = '=SUMIF(D:D,"Stefan",C:C)'
FORMULA_TINE = '=SUMIF(D:D,"Tine",C:C)'
OLD_HEADERS = ['Date', 'Item', 'Amount', 'Paid By']
TOTAL_ROW_TINE = ['', '', '', '', '', 'Total Tine Paid:', FORMULA_TINE]


class SheetsHandler:
    """Handler for Google Sheets operations."""

    def __init__(self):
        """Initialize the Sheets handler with service account credentials."""
        try:
            logger.info(f"Initializing Google Sheets client with: {GOOGLE_SHEETS_CREDS_FILE}")

            creds = Credentials.from_service_account_file(
                GOOGLE_SHEETS_CREDS_FILE,
                scopes=SCOPES
            )
            self.client = gspread.authorize(creds)

            logger.info("Google Sheets client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            raise

    def _get_month_worksheet_name(self) -> str:
        """Get worksheet name for the current month (e.g. '2026-06')."""
        return datetime.now().strftime('%Y-%m')

    def _format_new_worksheet(self, worksheet: gspread.Worksheet):
        """Set up a new monthly worksheet with headers, totals, and dropdown."""
        worksheet.append_row(
            FULL_HEADERS + [FORMULA_STEFAN],
            value_input_option='USER_ENTERED'
        )
        worksheet.append_row(TOTAL_ROW_TINE, value_input_option='USER_ENTERED')
        worksheet.add_validation(
            range='D2:D',
            condition_type='ONE_OF_LIST',
            values=['Stefan', 'Tine'],
            inputMessage='Select who paid',
            strict=True
        )
        logger.info("New worksheet formatted with headers, totals, and dropdown")

    def _upgrade_sheet_format(self, worksheet: gspread.Worksheet):
        """Upgrade an old-format worksheet to the new full format."""
        headers = worksheet.row_values(1)
        if len(headers) >= 6 and headers[1] != 'Item':
            return

        logger.info(f"Upgrading worksheet '{worksheet.title}' to new format")

        # Update header row: B1 "Item" → "Description", add E1/F1/G1
        worksheet.update('A1:G1', [FULL_HEADERS + [FORMULA_STEFAN]],
                         value_input_option='USER_ENTERED')

        # Insert totals row at row 2 (shifts existing data down)
        worksheet.insert_rows([TOTAL_ROW_TINE], row=2,
                              value_input_option='USER_ENTERED')

        # Add dropdown on Paid By column
        try:
            worksheet.add_validation(
                range='D3:D',
                condition_type='ONE_OF_LIST',
                values=['Stefan', 'Tine'],
                inputMessage='Select who paid',
                strict=True
            )
        except Exception as e:
            logger.warning(f"Could not add dropdown validation: {e}")

        logger.info(f"Worksheet '{worksheet.title}' upgraded successfully")

    def get_sheet(self, worksheet_name: Optional[str] = None) -> gspread.Worksheet:
        """
        Get the monthly worksheet from the configured Google Sheet.
        Creates or upgrades the worksheet as needed.

        Args:
            worksheet_name: Name of the worksheet, defaults to current month (YYYY-MM)

        Returns:
            Worksheet object

        Raises:
            Exception: If sheet cannot be accessed
        """
        try:
            if worksheet_name is None:
                worksheet_name = self._get_month_worksheet_name()

            logger.debug(f"Accessing spreadsheet: {GOOGLE_SHEET_NAME}, worksheet: {worksheet_name}")

            spreadsheet = self.client.open(GOOGLE_SHEET_NAME)

            try:
                worksheet = spreadsheet.worksheet(worksheet_name)
                logger.info(f"Found existing worksheet: {worksheet_name}")
                self._upgrade_sheet_format(worksheet)
            except gspread.WorksheetNotFound:
                logger.info(f"Creating new worksheet: {worksheet_name}")
                worksheet = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=26)
                self._format_new_worksheet(worksheet)

            return worksheet

        except gspread.SpreadsheetNotFound:
            logger.error(f"Spreadsheet not found: {GOOGLE_SHEET_NAME}")
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

            worksheet = self.get_sheet()

            row = [
                expense_data.get('date', ''),
                expense_data.get('item', ''),
                expense_data.get('amount', 0),
                expense_data.get('paid_by', 'Me')
            ]

            worksheet.append_row(row, value_input_option='USER_ENTERED')

            logger.info(f"Successfully added expense row: {row}")
            return True

        except Exception as e:
            logger.error(f"Error adding expense to sheet: {e}")
            raise

    def get_recent_expenses(self, limit: int = SUMMARY_LIMIT) -> List[List[str]]:
        """
        Get recent expenses from the monthly sheet.
        Skips header row (row 1) and totals row (row 2).

        Args:
            limit: Maximum number of expenses to retrieve

        Returns:
            List of expense rows (each row is a list)
        """
        try:
            logger.debug(f"Fetching last {limit} expenses")

            worksheet = self.get_sheet()

            all_values = worksheet.get_all_values()

            # Skip header row (1) and totals row (2)
            if len(all_values) <= 2:
                logger.info("No expense data found in sheet")
                return []

            expenses = all_values[2:]
            recent = expenses[-limit:] if len(expenses) > limit else expenses
            recent.reverse()

            logger.info(f"Retrieved {len(recent)} recent expenses")
            return recent

        except Exception as e:
            logger.error(f"Error fetching recent expenses: {e}")
            return []

    def verify_sheet_access(self) -> bool:
        """
        Verify that the spreadsheet is accessible and current month's worksheet exists.

        Returns:
            True if accessible, False otherwise
        """
        try:
            self.get_sheet()
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
