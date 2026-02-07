"""Gemini AI handler for expense extraction from multimodal inputs."""
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
import google.generativeai as genai

from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.constants import EXPENSE_EXTRACTION_PROMPT
from src.logger import get_logger

logger = get_logger(__name__)

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Response schema for structured JSON output
EXPENSE_SCHEMA = {
    "type": "object",
    "properties": {
        "date": {
            "type": "string",
            "description": "Date in YYYY-MM-DD format"
        },
        "item": {
            "type": "string",
            "description": "Description of the item or expense"
        },
        "amount": {
            "type": "number",
            "description": "Numeric amount of the expense"
        },
        "currency": {
            "type": "string",
            "description": "Currency code or name (e.g., USD, PHP, Peso)"
        },
        "paid_by": {
            "type": "string",
            "description": "Name of person who paid, or 'Me' if not specified"
        }
    },
    "required": ["date", "item", "amount", "currency", "paid_by"]
}


class GeminiHandler:
    """Handler for Google Gemini API interactions."""
    
    def __init__(self):
        """Initialize the Gemini handler."""
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config={
                "temperature": 0.1,  # Low temperature for consistent extraction
                "response_mime_type": "application/json",
            }
        )
        logger.info(f"Initialized Gemini handler with model: {GEMINI_MODEL}")
    
    def analyze_content(
        self,
        text: Optional[str] = None,
        media_path: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze content (text, image, or audio) and extract expense data.
        
        Args:
            text: Text input or caption
            media_path: Path to media file (image or audio)
            media_type: Type of media ('image' or 'audio')
            
        Returns:
            Dictionary containing extracted expense data
            
        Raises:
            Exception: If analysis fails after retries
        """
        try:
            logger.info(f"Analyzing content - text: {bool(text)}, media: {media_type}")
            
            # Build content parts
            content_parts = [EXPENSE_EXTRACTION_PROMPT]
            
            # Add text if provided
            if text:
                content_parts.append(f"\nUser input: {text}")
            
            # Handle media
            if media_path and media_type:
                if media_type == "image":
                    content_parts.append(self._process_image(media_path))
                elif media_type == "audio":
                    content_parts.append(self._process_audio(media_path))
                else:
                    raise ValueError(f"Unsupported media type: {media_type}")
            
            # Generate response with retries
            response = self._generate_with_retry(content_parts)
            
            # Parse JSON response
            expense_data = json.loads(response.text)
            
            logger.info(f"Successfully extracted expense: {expense_data}")
            return expense_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response.text if 'response' in locals() else 'N/A'}")
            raise Exception("Failed to extract structured expense data")
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            raise
    
    def _process_image(self, image_path: str) -> Any:
        """Process image file for Gemini API."""
        try:
            logger.debug(f"Processing image: {image_path}")
            
            # Read image file
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Determine mime type
            path = Path(image_path)
            if path.suffix.lower() in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif path.suffix.lower() == '.png':
                mime_type = 'image/png'
            else:
                mime_type = 'image/jpeg'  # Default
            
            # Create image part
            image_part = {
                "mime_type": mime_type,
                "data": image_data
            }
            
            return image_part
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def _process_audio(self, audio_path: str) -> Any:
        """Process audio file using Gemini File API."""
        try:
            logger.debug(f"Processing audio: {audio_path}")
            
            # Upload file using File API
            audio_file = genai.upload_file(path=audio_path, mime_type="audio/ogg")
            logger.info(f"Uploaded audio file: {audio_file.name}")
            
            # Wait for file to be processed
            while audio_file.state.name == "PROCESSING":
                logger.debug("Waiting for audio processing...")
                time.sleep(2)
                audio_file = genai.get_file(audio_file.name)
            
            if audio_file.state.name == "FAILED":
                raise Exception("Audio file processing failed")
            
            logger.info("Audio file ready for processing")
            return audio_file
            
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            raise
    
    def _generate_with_retry(self, content_parts: list, max_retries: int = 3) -> Any:
        """Generate response with exponential backoff retry logic."""
        for attempt in range(max_retries):
            try:
                logger.debug(f"Generation attempt {attempt + 1}/{max_retries}")
                response = self.model.generate_content(content_parts)
                return response
                
            except Exception as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries exceeded")
                    raise


# Singleton instance
_gemini_handler = None


def get_gemini_handler() -> GeminiHandler:
    """Get or create singleton Gemini handler instance."""
    global _gemini_handler
    if _gemini_handler is None:
        _gemini_handler = GeminiHandler()
    return _gemini_handler
