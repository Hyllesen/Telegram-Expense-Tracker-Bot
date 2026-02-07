"""Unit tests for Gemini Handler."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.gemini_handler import GeminiHandler


@pytest.fixture
def gemini_handler():
    """Create a GeminiHandler instance for testing."""
    with patch('src.gemini_handler.genai.configure'):
        with patch('src.gemini_handler.genai.GenerativeModel'):
            handler = GeminiHandler()
            return handler


class TestGeminiHandler:
    """Test suite for GeminiHandler."""
    
    @pytest.mark.unit
    def test_initialization(self, gemini_handler):
        """Test that GeminiHandler initializes correctly."""
        assert gemini_handler is not None
        assert gemini_handler.model is not None
    
    @pytest.mark.unit
    def test_analyze_text_only(self, gemini_handler):
        """Test text-only expense extraction."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '{"date": "2026-02-07", "item": "Coffee", "amount": 5.50, "currency": "USD", "paid_by": "Me"}'
        
        gemini_handler.model.generate_content = Mock(return_value=mock_response)
        
        # Test
        result = gemini_handler.analyze_content(text="Coffee 5.50 USD")
        
        # Assertions
        assert result['date'] == '2026-02-07'
        assert result['item'] == 'Coffee'
        assert result['amount'] == 5.50
        assert result['currency'] == 'USD'
        assert result['paid_by'] == 'Me'
    
    @pytest.mark.unit
    def test_analyze_with_paid_by(self, gemini_handler):
        """Test extraction of 'Paid By' field."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '{"date": "2026-02-07", "item": "Bananas", "amount": 100, "currency": "Peso", "paid_by": "Stefan"}'
        
        gemini_handler.model.generate_content = Mock(return_value=mock_response)
        
        # Test
        result = gemini_handler.analyze_content(text="Stefan paid for bananas 100 peso")
        
        # Assertions
        assert result['paid_by'] == 'Stefan'
        assert result['item'] == 'Bananas'
        assert result['amount'] == 100
    
    @pytest.mark.unit
    def test_process_image(self, gemini_handler):
        """Test image processing."""
        # Create a mock image file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(b'fake image data')
            tmp_path = tmp.name
        
        try:
            # Test
            result = gemini_handler._process_image(tmp_path)
            
            # Assertions
            assert 'mime_type' in result
            assert 'data' in result
            assert result['mime_type'] == 'image/jpeg'
            assert result['data'] == b'fake image data'
        finally:
            import os
            os.remove(tmp_path)
    
    @pytest.mark.unit
    def test_invalid_json_response(self, gemini_handler):
        """Test handling of invalid JSON responses."""
        # Mock invalid response
        mock_response = Mock()
        mock_response.text = 'Not valid JSON'
        
        gemini_handler.model.generate_content = Mock(return_value=mock_response)
        
        # Test - should raise exception
        with pytest.raises(Exception, match="Failed to extract structured expense data"):
            gemini_handler.analyze_content(text="Coffee")
    
    @pytest.mark.unit
    @patch('src.gemini_handler.genai.upload_file')
    @patch('src.gemini_handler.genai.get_file')
    def test_process_audio(self, mock_get_file, mock_upload_file, gemini_handler):
        """Test audio file processing."""
        # Create mock audio file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
            tmp.write(b'fake audio data')
            tmp_path = tmp.name
        
        try:
            # Mock file upload response
            mock_file = Mock()
            mock_file.name = 'uploaded_file'
            mock_file.state.name = 'ACTIVE'
            mock_upload_file.return_value = mock_file
            
            # Test
            result = gemini_handler._process_audio(tmp_path)
            
            # Assertions
            assert result is not None
            mock_upload_file.assert_called_once()
        finally:
            import os
            os.remove(tmp_path)
    
    @pytest.mark.unit
    def test_retry_logic(self, gemini_handler):
        """Test exponential backoff retry logic."""
        # Mock to fail twice, then succeed
        mock_response = Mock()
        mock_response.text = '{"date": "2026-02-07", "item": "Coffee", "amount": 5.50, "currency": "USD", "paid_by": "Me"}'
        
        gemini_handler.model.generate_content = Mock(
            side_effect=[Exception("API Error"), Exception("API Error"), mock_response]
        )
        
        # Test - should succeed after retries
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = gemini_handler._generate_with_retry(['test'])
            assert result == mock_response
    
    @pytest.mark.unit
    def test_max_retries_exceeded(self, gemini_handler):
        """Test that max retries raises exception."""
        # Mock to always fail
        gemini_handler.model.generate_content = Mock(side_effect=Exception("API Error"))
        
        # Test - should raise after max retries
        with patch('time.sleep'):  # Mock sleep to speed up test
            with pytest.raises(Exception, match="API Error"):
                gemini_handler._generate_with_retry(['test'], max_retries=3)
