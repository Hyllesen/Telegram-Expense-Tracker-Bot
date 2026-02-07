"""Integration tests for the expense tracker bot.

These tests verify end-to-end flows but use mocked external APIs
to avoid real API calls during testing.
"""
import pytest
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock


@pytest.fixture
def test_assets_dir():
    """Get path to test assets directory."""
    return Path(__file__).parent.parent / "test-assets"


@pytest.fixture
def sample_image(test_assets_dir):
    """Get path to sample receipt image."""
    image_files = list(test_assets_dir.glob("*.jpeg")) + list(test_assets_dir.glob("*.jpg"))
    if image_files:
        return str(image_files[0])
    return None


@pytest.fixture
def sample_audio(test_assets_dir):
    """Get path to sample voice note."""
    audio_files = list(test_assets_dir.glob("*.ogg"))
    if audio_files:
        return str(audio_files[0])
    return None


@pytest.mark.integration
@patch('src.gemini_handler.client')
def test_text_to_sheets_flow(mock_client):
    """Test complete flow: text input -> Gemini -> Sheets."""
    from src.gemini_handler import GeminiHandler
    
    # Mock Gemini response
    mock_response = Mock()
    mock_response.text = '{"date": "2026-02-07", "item": "Coffee", "amount": 5.50, "currency": "USD", "paid_by": "Me"}'
    
    mock_client.models.generate_content = Mock(return_value=mock_response)
    
    # Test Gemini extraction
    handler = GeminiHandler()
    result = handler.analyze_content(text="Coffee 5.50 USD")
    
    # Assertions
    assert result['item'] == 'Coffee'
    assert result['amount'] == 5.50
    assert result['currency'] == 'USD'


@pytest.mark.integration
@pytest.mark.slow
@patch('src.sheets_handler.Credentials.from_service_account_file')
@patch('src.sheets_handler.gspread.authorize')
def test_sheets_integration(mock_authorize, mock_creds):
    """Test Google Sheets integration."""
    from src.sheets_handler import SheetsHandler
    
    # Mock gspread client
    mock_worksheet = Mock()
    mock_worksheet.row_values.return_value = ['Date', 'Item', 'Amount', 'Currency', 'Paid By']
    mock_worksheet.append_row = Mock()
    
    mock_spreadsheet = Mock()
    mock_spreadsheet.sheet1 = mock_worksheet
    
    mock_client = Mock()
    mock_client.open = Mock(return_value=mock_spreadsheet)
    
    mock_authorize.return_value = mock_client
    mock_creds.return_value = Mock()
    
    # Test
    handler = SheetsHandler()
    
    # Verify access
    assert handler.verify_sheet_access() is True
    
    # Add expense
    expense = {
        'date': '2026-02-07',
        'item': 'Coffee',
        'amount': 5.50,
        'currency': 'USD',
        'paid_by': 'Stefan'
    }
    
    result = handler.add_expense(expense)
    assert result is True
    mock_worksheet.append_row.assert_called_once()


@pytest.mark.integration
@patch('src.gemini_handler.client')
def test_image_processing_flow(mock_client, sample_image):
    """Test image processing with Gemini."""
    from src.gemini_handler import GeminiHandler
    
    if not sample_image or not os.path.exists(sample_image):
        pytest.skip("No sample image available")
    
    # Mock Gemini response
    mock_response = Mock()
    mock_response.text = '{"date": "2026-02-07", "item": "Groceries", "amount": 353.50, "currency": "PHP", "paid_by": "Tine"}'
    
    mock_client.models.generate_content = Mock(return_value=mock_response)
    
    # Test
    handler = GeminiHandler()
    result = handler.analyze_content(
        text="Paid by Tine",
        media_path=sample_image,
        media_type='image'
    )
    
    # Assertions
    assert 'item' in result
    assert 'amount' in result
    assert 'currency' in result


@pytest.mark.integration
@pytest.mark.slow
@patch('src.gemini_handler.client')
def test_audio_processing_flow(mock_client, sample_audio):
    """Test audio processing with Gemini."""
    from src.gemini_handler import GeminiHandler
    
    if not sample_audio or not os.path.exists(sample_audio):
        pytest.skip("No sample audio available")
    
    # Mock Gemini response
    mock_response = Mock()
    mock_response.text = '{"date": "2026-02-07", "item": "Bananas", "amount": 100, "currency": "Peso", "paid_by": "Stefan"}'
    
    mock_client.models.generate_content = Mock(return_value=mock_response)
    
    # Test
    handler = GeminiHandler()
    result = handler.analyze_content(
        media_path=sample_audio,
        media_type='audio'
    )
    
    # Assertions
    assert 'item' in result
    assert 'amount' in result


@pytest.mark.integration
def test_paid_by_extraction_variations():
    """Test different variations of 'Paid By' extraction."""
    from src.gemini_handler import GeminiHandler
    
    test_cases = [
        ("Paid by Stefan: Coffee 5 USD", "Stefan"),
        ("John paid for dinner 50 USD", "John"),
        ("Tine bought fish for 100 PHP", "Tine"),
        ("Coffee 5 dollars", "Me"),
        ("Lunch 25 peso", "Me"),
    ]
    
    with patch('src.gemini_handler.client') as mock_client:
        handler = GeminiHandler()
        
        for text, expected_paid_by in test_cases:
            # Mock response based on expected result
            mock_response = Mock()
            mock_response.text = f'{{"date": "2026-02-07", "item": "Item", "amount": 10, "currency": "USD", "paid_by": "{expected_paid_by}"}}'
            
            mock_client.models.generate_content = Mock(return_value=mock_response)
            
            result = handler.analyze_content(text=text)
            assert result['paid_by'] == expected_paid_by, f"Failed for: {text}"


@pytest.mark.integration
def test_end_to_end_mock_flow():
    """Test complete end-to-end flow with all mocks."""
    with patch('src.gemini_handler.client') as mock_gemini_client:
        with patch('src.sheets_handler.Credentials.from_service_account_file'):
            with patch('src.sheets_handler.gspread.authorize') as mock_gspread:
                from src.gemini_handler import GeminiHandler
                from src.sheets_handler import SheetsHandler
                
                # Setup Gemini mock
                mock_response = Mock()
                mock_response.text = '{"date": "2026-02-07", "item": "Test Item", "amount": 99.99, "currency": "USD", "paid_by": "TestUser"}'
                
                mock_gemini_client.models.generate_content = Mock(return_value=mock_response)
                
                # Setup Sheets mock
                mock_worksheet = Mock()
                mock_worksheet.row_values.return_value = ['Date', 'Item', 'Amount', 'Currency', 'Paid By']
                mock_worksheet.append_row = Mock()
                
                mock_spreadsheet = Mock()
                mock_spreadsheet.sheet1 = mock_worksheet
                
                mock_client = Mock()
                mock_client.open = Mock(return_value=mock_spreadsheet)
                mock_gspread.return_value = mock_client
                
                # Test flow
                gemini = GeminiHandler()
                sheets = SheetsHandler()
                
                # 1. Extract expense
                expense = gemini.analyze_content(text="Test Item 99.99 USD paid by TestUser")
                
                # 2. Save to sheets
                result = sheets.add_expense(expense)
                
                # Assertions
                assert expense['item'] == 'Test Item'
                assert expense['amount'] == 99.99
                assert expense['paid_by'] == 'TestUser'
                assert result is True
                mock_worksheet.append_row.assert_called_once()
