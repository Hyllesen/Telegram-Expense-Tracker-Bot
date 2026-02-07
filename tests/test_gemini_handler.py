"""Unit tests for Gemini Handler."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.gemini_handler import GeminiHandler


@pytest.fixture
def gemini_handler():
    """Create a GeminiHandler instance for testing."""
    with patch('src.gemini_handler.client') as mock_client:
        handler = GeminiHandler()
        handler.client = mock_client
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
        mock_response.text = '{"date": "2026-02-07", "item": "Coffee", "amount": 5.50, "paid_by": "Me"}'
        
        gemini_handler.client.models.generate_content = Mock(return_value=mock_response)
        
        # Test
        result = gemini_handler.analyze_content(text="Coffee 5.50")
        
        # Assertions
        assert result['date'] == '2026-02-07'
        assert result['item'] == 'Coffee'
        assert result['amount'] == 5.50
        assert result['paid_by'] == 'Me'
    
    @pytest.mark.unit
    def test_analyze_with_paid_by(self, gemini_handler):
        """Test extraction of 'Paid By' field."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '{"date": "2026-02-07", "item": "Bananas", "amount": 100, "paid_by": "Stefan"}'
        
        gemini_handler.client.models.generate_content = Mock(return_value=mock_response)
        
        # Test
        result = gemini_handler.analyze_content(text="Stefan paid for bananas 100")
        
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
            
            # Assertions - check it's a Part object (mocked, but structure valid)
            assert result is not None
        finally:
            import os
            os.remove(tmp_path)
    
    @pytest.mark.unit
    def test_invalid_json_response(self, gemini_handler):
        """Test handling of invalid JSON responses."""
        # Mock invalid response
        mock_response = Mock()
        mock_response.text = 'Not valid JSON'
        
        gemini_handler.client.models.generate_content = Mock(return_value=mock_response)
        
        # Test - should raise exception
        with pytest.raises(Exception, match="Failed to extract structured expense data"):
            gemini_handler.analyze_content(text="Coffee")
    
    @pytest.mark.unit
    def test_process_audio(self, gemini_handler):
        """Test audio file processing."""
        # Create mock audio file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
            tmp.write(b'fake audio data')
            tmp_path = tmp.name
        
        try:
            # Test
            result = gemini_handler._process_audio(tmp_path)
            
            # Assertions - check it's a Part object
            assert result is not None
        finally:
            import os
            os.remove(tmp_path)
    
    @pytest.mark.unit
    def test_retry_logic(self, gemini_handler):
        """Test exponential backoff retry logic."""
        # Mock to fail twice, then succeed
        mock_response = Mock()
        mock_response.text = '{"date": "2026-02-07", "item": "Coffee", "amount": 5.50, "paid_by": "Me"}'
        
        gemini_handler.client.models.generate_content = Mock(
            side_effect=[Exception("API Error"), Exception("API Error"), mock_response]
        )
        
        # Test - should succeed after retries
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = gemini_handler._generate_with_retry([])
            assert result == mock_response
    
    @pytest.mark.unit
    def test_max_retries_exceeded(self, gemini_handler):
        """Test that max retries raises exception."""
        # Mock to always fail
        gemini_handler.client.models.generate_content = Mock(side_effect=Exception("API Error"))
        
        # Test - should raise after max retries
        with patch('time.sleep'):  # Mock sleep to speed up test
            with pytest.raises(Exception, match="API Error"):
                gemini_handler._generate_with_retry([], max_retries=3)
