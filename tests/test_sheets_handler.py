"""Unit tests for Sheets Handler."""
import pytest
from unittest.mock import Mock, patch, MagicMock
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
    def test_get_sheet_success(self, sheets_handler):
        """Test successful sheet retrieval."""
        # Mock spreadsheet and worksheet
        mock_worksheet = Mock()
        mock_spreadsheet = Mock()
        mock_spreadsheet.sheet1 = mock_worksheet
        
        sheets_handler.client.open = Mock(return_value=mock_spreadsheet)
        
        # Test
        result = sheets_handler.get_sheet()
        
        # Assertions
        assert result == mock_worksheet
        sheets_handler.client.open.assert_called_once()
    
    @pytest.mark.unit
    def test_get_sheet_not_found(self, sheets_handler):
        """Test handling of sheet not found error."""
        import gspread
        sheets_handler.client.open = Mock(side_effect=gspread.SpreadsheetNotFound)
        
        # Test - should raise exception
        with pytest.raises(Exception, match="not found"):
            sheets_handler.get_sheet()
    
    @pytest.mark.unit
    def test_add_expense(self, sheets_handler):
        """Test adding expense to sheet."""
        # Mock worksheet
        mock_worksheet = Mock()
        sheets_handler.get_sheet = Mock(return_value=mock_worksheet)
        
        # Test data
        expense_data = {
            'date': '2026-02-07',
            'item': 'Coffee',
            'amount': 5.50,
            'currency': 'USD',
            'paid_by': 'Stefan'
        }
        
        # Test
        result = sheets_handler.add_expense(expense_data)
        
        # Assertions
        assert result is True
        mock_worksheet.append_row.assert_called_once()
        
        # Check row format
        call_args = mock_worksheet.append_row.call_args
        row = call_args[0][0]
        assert row == ['2026-02-07', 'Coffee', 5.50, 'USD', 'Stefan']
    
    @pytest.mark.unit
    def test_add_expense_defaults(self, sheets_handler):
        """Test adding expense with default values."""
        # Mock worksheet
        mock_worksheet = Mock()
        sheets_handler.get_sheet = Mock(return_value=mock_worksheet)
        
        # Test data with missing fields
        expense_data = {
            'date': '2026-02-07',
            'item': 'Coffee',
            'amount': 5.50
        }
        
        # Test
        result = sheets_handler.add_expense(expense_data)
        
        # Assertions
        assert result is True
        call_args = mock_worksheet.append_row.call_args
        row = call_args[0][0]
        assert row[3] == ''  # Currency defaults to empty
        assert row[4] == 'Me'  # Paid by defaults to 'Me'
    
    @pytest.mark.unit
    def test_get_recent_expenses(self, sheets_handler):
        """Test retrieving recent expenses."""
        # Mock worksheet with data
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['Date', 'Item', 'Amount', 'Currency', 'Paid By'],  # Header
            ['2026-02-05', 'Coffee', '5.50', 'USD', 'Me'],
            ['2026-02-06', 'Lunch', '15.00', 'USD', 'John'],
            ['2026-02-07', 'Dinner', '25.00', 'USD', 'Sarah']
        ]
        
        sheets_handler.get_sheet = Mock(return_value=mock_worksheet)
        
        # Test
        result = sheets_handler.get_recent_expenses(limit=2)
        
        # Assertions - should return last 2 in reverse order (most recent first)
        assert len(result) == 2
        assert result[0][1] == 'Dinner'  # Most recent
        assert result[1][1] == 'Lunch'
    
    @pytest.mark.unit
    def test_get_recent_expenses_empty(self, sheets_handler):
        """Test retrieving expenses from empty sheet."""
        # Mock empty worksheet
        mock_worksheet = Mock()
        mock_worksheet.get_all_values.return_value = [
            ['Date', 'Item', 'Amount', 'Currency', 'Paid By']  # Only header
        ]
        
        sheets_handler.get_sheet = Mock(return_value=mock_worksheet)
        
        # Test
        result = sheets_handler.get_recent_expenses()
        
        # Assertions
        assert result == []
    
    @pytest.mark.unit
    def test_verify_sheet_access_with_headers(self, sheets_handler):
        """Test sheet verification with existing headers."""
        # Mock worksheet
        mock_worksheet = Mock()
        mock_worksheet.row_values.return_value = ['Date', 'Item', 'Amount', 'Currency', 'Paid By']
        
        sheets_handler.get_sheet = Mock(return_value=mock_worksheet)
        
        # Test
        result = sheets_handler.verify_sheet_access()
        
        # Assertions
        assert result is True
    
    @pytest.mark.unit
    def test_verify_sheet_access_without_headers(self, sheets_handler):
        """Test sheet verification creates headers if missing."""
        # Mock worksheet without headers
        mock_worksheet = Mock()
        mock_worksheet.row_values.return_value = []
        
        sheets_handler.get_sheet = Mock(return_value=mock_worksheet)
        
        # Test
        result = sheets_handler.verify_sheet_access()
        
        # Assertions
        assert result is True
        mock_worksheet.append_row.assert_called_once()
    
    @pytest.mark.unit
    def test_verify_sheet_access_failure(self, sheets_handler):
        """Test sheet verification handles errors."""
        sheets_handler.get_sheet = Mock(side_effect=Exception("Connection error"))
        
        # Test
        result = sheets_handler.verify_sheet_access()
        
        # Assertions
        assert result is False
