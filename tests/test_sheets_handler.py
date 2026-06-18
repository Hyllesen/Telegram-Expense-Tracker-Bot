"""Unit tests for Sheets Handler."""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
from src.sheets_handler import SheetsHandler


@pytest.fixture
def mock_credentials():
    """Mock Google credentials."""
    with patch('src.sheets_handler.Credentials.from_service_account_file') as mock_creds:
        mock_creds.return_value = Mock()
        yield mock_creds


@pytest.fixture
def mock_gspread():
    """Mock gspread client."""
    with patch('src.sheets_handler.gspread.authorize') as mock_auth:
        mock_client = Mock()
        mock_auth.return_value = mock_client
        yield mock_client


@pytest.fixture
def sheets_handler(mock_credentials, mock_gspread):
    """Create a SheetsHandler instance for testing."""
    handler = SheetsHandler()
    handler.client = mock_gspread
    return handler


class TestSheetsHandler:
    """Test suite for SheetsHandler."""

    @pytest.mark.unit
    def test_initialization(self, sheets_handler):
        """Test that SheetsHandler initializes correctly."""
        assert sheets_handler is not None
        assert sheets_handler.client is not None

    @pytest.mark.unit
    def test_get_month_worksheet_name_format(self, sheets_handler):
        """Test that month worksheet name follows YYYY-MM format."""
        name = sheets_handler._get_month_worksheet_name()
        assert len(name) == 7
        assert name[4] == '-'
        parts = name.split('-')
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert parts[1].isdigit()

    @pytest.mark.unit
    def test_format_new_worksheet(self, sheets_handler):
        """Test that new worksheet is formatted with headers, totals, and dropdown."""
        mock_worksheet = Mock()

        sheets_handler._format_new_worksheet(mock_worksheet)

        # Should append header row with formula
        header_call = mock_worksheet.append_row.call_args_list[0]
        assert header_call[0][0][0] == 'Date'
        assert header_call[0][0][1] == 'Description'
        assert header_call[0][0][5] == 'Total Stefan Paid'
        assert 'SUMIF' in str(header_call[0][0][6])

        # Should append Tine totals row
        tine_call = mock_worksheet.append_row.call_args_list[1]
        assert tine_call[0][0][5] == 'Total Tine Paid:'
        assert 'SUMIF' in str(tine_call[0][0][6])

        # Should add dropdown
        mock_worksheet.add_validation.assert_called_once()

    @pytest.mark.unit
    def test_get_sheet_creates_new_monthly(self, sheets_handler):
        """Test creating a new monthly worksheet with full formatting."""
        mock_worksheet = Mock()
        mock_spreadsheet = Mock()

        sheets_handler.client.open = Mock(return_value=mock_spreadsheet)
        mock_spreadsheet.worksheet = Mock(side_effect=Mock(side_effect=_raise_worksheet_not_found))
        mock_spreadsheet.add_worksheet = Mock(return_value=mock_worksheet)

        sheets_handler._format_new_worksheet = Mock()

        result = sheets_handler.get_sheet(worksheet_name='2026-07')

        assert result == mock_worksheet
        mock_spreadsheet.add_worksheet.assert_called_once_with(title='2026-07', rows=1000, cols=26)
        sheets_handler._format_new_worksheet.assert_called_once_with(mock_worksheet)

    @pytest.mark.unit
    def test_get_sheet_existing_month(self, sheets_handler):
        """Test retrieving an existing monthly worksheet."""
        mock_worksheet = Mock()
        mock_spreadsheet = Mock()

        sheets_handler.client.open = Mock(return_value=mock_spreadsheet)
        mock_spreadsheet.worksheet = Mock(return_value=mock_worksheet)
        sheets_handler._upgrade_sheet_format = Mock()

        result = sheets_handler.get_sheet(worksheet_name='2026-06')

        assert result == mock_worksheet
        mock_spreadsheet.worksheet.assert_called_once_with('2026-06')
        sheets_handler._upgrade_sheet_format.assert_called_once_with(mock_worksheet)

    @pytest.mark.unit
    def test_get_sheet_defaults_to_current_month(self, sheets_handler):
        """Test that get_sheet() without args uses current month."""
        mock_worksheet = Mock()
        mock_spreadsheet = Mock()

        sheets_handler.client.open = Mock(return_value=mock_spreadsheet)
        mock_spreadsheet.worksheet = Mock(return_value=mock_worksheet)
        sheets_handler._upgrade_sheet_format = Mock()

        current_month = datetime.now().strftime('%Y-%m')
        result = sheets_handler.get_sheet()

        assert result == mock_worksheet
        mock_spreadsheet.worksheet.assert_called_once_with(current_month)

    @pytest.mark.unit
    def test_get_sheet_spreadsheet_not_found(self, sheets_handler):
        """Test handling of spreadsheet not found error."""
        import gspread
        sheets_handler.client.open = Mock(side_effect=gspread.SpreadsheetNotFound)

        with pytest.raises(Exception, match="not found"):
            sheets_handler.get_sheet()

    @pytest.mark.unit
    def test_upgrade_sheet_format_skips_already_formatted(self, sheets_handler):
        """Test that upgrade skips already-formatted sheets."""
        mock_worksheet = Mock()
        mock_worksheet.row_values.return_value = ['Date', 'Description', 'Amount', 'Paid By', '', 'Total Stefan Paid']

        sheets_handler._upgrade_sheet_format(mock_worksheet)

        mock_worksheet.update.assert_not_called()
        mock_worksheet.insert_rows.assert_not_called()

    @pytest.mark.unit
    def test_upgrade_sheet_format_upgrades_old(self, sheets_handler):
        """Test that old-format sheets get upgraded."""
        mock_worksheet = Mock()
        mock_worksheet.row_values.return_value = ['Date', 'Item', 'Amount', 'Paid By']

        sheets_handler._upgrade_sheet_format(mock_worksheet)

        mock_worksheet.update.assert_called_once()
        mock_worksheet.insert_rows.assert_called_once()
        mock_worksheet.add_validation.assert_called_once()

    @pytest.mark.unit
    def test_add_expense(self, sheets_handler):
        """Test adding expense to sheet."""
        mock_worksheet = Mock()
        sheets_handler.get_sheet = Mock(return_value=mock_worksheet)

        expense_data = {
            'date': '2026-02-07',
            'item': 'Coffee',
            'amount': 5.50,
            'paid_by': 'Stefan'
        }

        result = sheets_handler.add_expense(expense_data)

        assert result is True
        mock_worksheet.append_row.assert_called_once()

        call_args = mock_worksheet.append_row.call_args
        row = call_args[0][0]
        assert row == ['2026-02-07', 'Coffee', 5.50, 'Stefan']

    @pytest.mark.unit
    def test_add_expense_defaults(self, sheets_handler):
        """Test adding expense with default values."""
        mock_worksheet = Mock()
        sheets_handler.get_sheet = Mock(return_value=mock_worksheet)

        expense_data = {
            'date': '2026-02-07',
            'item': 'Coffee',
            'amount': 5.50
        }

        result = sheets_handler.add_expense(expense_data)

        assert result is True
        call_args = mock_worksheet.append_row.call_args
        row = call_args[0][0]
        assert row[3] == 'Me'

    @pytest.mark.unit
    def test_get_recent_expenses(self, sheets_handler):
        """Test retrieving recent expenses (skipping header and totals rows)."""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['Date', 'Description', 'Amount', 'Paid By', '', 'Total Stefan Paid', '0'],
            ['', '', '', '', '', 'Total Tine Paid:', '0'],
            ['2026-02-05', 'Coffee', '5.50', 'Me', '', '', ''],
            ['2026-02-06', 'Lunch', '15.00', 'John', '', '', ''],
            ['2026-02-07', 'Dinner', '25.00', 'Sarah', '', '', '']
        ]

        sheets_handler.get_sheet = Mock(return_value=mock_worksheet)

        result = sheets_handler.get_recent_expenses(limit=2)

        assert len(result) == 2
        assert result[0][1] == 'Dinner'
        assert result[1][1] == 'Lunch'

    @pytest.mark.unit
    def test_get_recent_expenses_empty(self, sheets_handler):
        """Test retrieving expenses from sheet with only header and totals rows."""
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['Date', 'Description', 'Amount', 'Paid By', '', 'Total Stefan Paid', '0'],
            ['', '', '', '', '', 'Total Tine Paid:', '0']
        ]

        sheets_handler.get_sheet = Mock(return_value=mock_worksheet)

        result = sheets_handler.get_recent_expenses()

        assert result == []

    @pytest.mark.unit
    def test_verify_sheet_access_success(self, sheets_handler):
        """Test sheet verification passes."""
        sheets_handler.get_sheet = Mock(return_value=Mock())

        result = sheets_handler.verify_sheet_access()

        assert result is True

    @pytest.mark.unit
    def test_verify_sheet_access_failure(self, sheets_handler):
        """Test sheet verification handles errors."""
        sheets_handler.get_sheet = Mock(side_effect=Exception("Connection error"))

        result = sheets_handler.verify_sheet_access()

        assert result is False


def _raise_worksheet_not_found(*args, **kwargs):
    import gspread
    raise gspread.WorksheetNotFound("Mock not found")
