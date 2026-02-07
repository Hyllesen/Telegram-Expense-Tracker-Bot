# Migration to google-genai Package

## Background

Google has deprecated the `google-generativeai` package in favor of the new unified `google-genai` SDK. All support for the old package ended on November 30, 2025.

## What Changed

### Package Name
- **Old:** `google-generativeai`
- **New:** `google-genai`

### Import Statements
```python
# Old
import google.generativeai as genai
genai.configure(api_key=API_KEY)

# New
from google import genai
from google.genai import types
client = genai.Client(api_key=API_KEY)
```

### API Calls
```python
# Old
model = genai.GenerativeModel(model_name="gemini-1.5-flash")
response = model.generate_content(content_parts)

# New
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=types.Content(parts=content_parts),
    config=types.GenerateContentConfig(...)
)
```

### Content Parts
```python
# Old
image_part = {
    "mime_type": "image/jpeg",
    "data": image_data
}

# New
image_part = types.Part.from_bytes(
    data=image_data,
    mime_type="image/jpeg"
)
```

## Migration Status

✅ **Completed** - This project has been migrated to `google-genai` v0.2.0+

### Files Updated
1. ✅ `requirements.txt` - Changed dependency
2. ✅ `src/gemini_handler.py` - Complete SDK migration
3. ✅ Tests remain compatible (use mocking)

### Breaking Changes
- Audio files no longer use File API upload/wait pattern
- Audio is now passed directly as bytes (simpler!)
- Client-based initialization instead of global configure

### Benefits
- ✅ Future-proof (supported SDK)
- ✅ Cleaner API design
- ✅ Unified SDK for all Google GenAI models
- ✅ Better type hints with `types` module
- ✅ Simpler audio handling

## Testing After Migration

### Test Collection Fix

After migrating, tests initially failed to collect with:
```
ValueError: Missing key inputs argument! To use the Google AI API, provide (`api_key`) arguments.
```

**Root Cause:** The new SDK's `genai.Client()` initialization at module level required an API key even during test collection.

**Solution:** Conditional initialization based on test mode:

```python
# src/gemini_handler.py
from src.config import GEMINI_API_KEY, GEMINI_MODEL, IS_TESTING

# Skip client init during tests
client = None if IS_TESTING else genai.Client(api_key=GEMINI_API_KEY)

class GeminiHandler:
    def __init__(self):
        global client
        if client is None and not IS_TESTING:
            client = genai.Client(api_key=GEMINI_API_KEY)
        self.client = client
        # ...
```

### Additional API Fixes

The new SDK requires keyword arguments for `Part.from_text()`:

```python
# Old (incorrect)
types.Part.from_text(text_string)

# New (correct)
types.Part.from_text(text=text_string)
```

### Running Tests

```bash
# Install new dependencies
pip install --upgrade -r requirements.txt

# Run tests
pytest tests/ -v

# All 27 tests should pass
```

## Resources

- [Official Migration Guide](https://ai.google.dev/gemini-api/docs/migrate)
- [New SDK Documentation](https://github.com/googleapis/python-genai)
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)

## Version Info

- **Old SDK:** google-generativeai (deprecated)
- **New SDK:** google-genai >= 0.2.0
- **Migration Date:** 2026-02-07
- **Status:** ✅ Complete
