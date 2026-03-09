# AI Service Integration Guide
## For AI Integration Team

**Status:** Waiting for real AI service implementation  
**Current:** Using mock service for testing

---

## Overview

The backend is currently using a **mock AI service** (`gemini_service_mock.py`) for testing. When you implement the real AI service, the backend will automatically switch to using it.

---

## File Structure

```
ai-service/
├── gemini_service.py          # ← YOUR REAL SERVICE (to be created by AI team)
├── gemini_service_mock.py     # ← MOCK SERVICE (for testing, keep this)
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

---

## How It Works

The backend (`backend/main.py`) tries to import services in this order:

1. **First:** Try to import `ai_service.gemini_service` (real service)
2. **Fallback:** If not found, use `ai_service.gemini_service_mock` (mock service)

```python
# backend/main.py automatically does this:
try:
    from ai_service.gemini_service import GeminiService  # Real service
    logger.info("Using REAL Gemini AI service")
except ImportError:
    from ai_service.gemini_service_mock import GeminiService  # Mock service
    logger.info("Using MOCK Gemini AI service (for testing)")
```

---

## Required Interface

Your real service (`gemini_service.py`) must implement this interface:

```python
class GeminiService:
    """Real Gemini AI service"""
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini service with API key
        
        Args:
            api_key: Google Gemini API key from environment
        """
        pass
    
    async def simplify_terms(self, transcript: str) -> Dict:
        """
        Identify medical terms and provide simple explanations
        
        Args:
            transcript: Text from speech recognition
            
        Returns:
            {
                "terms": [
                    {
                        "term": "hypertension",
                        "explanation": "high blood pressure"
                    },
                    ...
                ]
            }
        """
        pass
    
    async def suggest_questions(self, full_transcript: str) -> Dict:
        """
        Generate relevant questions based on conversation
        
        Args:
            full_transcript: Complete conversation so far
            
        Returns:
            {
                "questions": [
                    "What are the side effects?",
                    "How often should I take this?",
                    ...
                ]
            }
        """
        pass
    
    async def generate_summary(self, full_transcript: str) -> Dict:
        """
        Generate structured visit summary
        
        Args:
            full_transcript: Complete conversation transcript
            
        Returns:
            {
                "title": "Visit Summary - March 9, 2026",
                "diagnosis": "Hypertension (High Blood Pressure)",
                "medications": [
                    "Lisinopril 10mg - Take once daily",
                    ...
                ],
                "instructions": [
                    "Monitor blood pressure daily",
                    ...
                ],
                "follow_up": "Schedule follow-up in 2 weeks",
                "key_points": [
                    "Blood pressure is elevated",
                    ...
                ]
            }
        """
        pass
    
    async def translate_text(self, text: str, target_language: str) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: ISO 639-1 language code (e.g., 'es', 'fr')
            
        Returns:
            Translated text string
        """
        pass
```

---

## Integration Steps

### Step 1: Create Your Service

Create `ai-service/gemini_service.py` with the interface above.

### Step 2: Test Your Service

```bash
# Test your service independently
cd ai-service
python -c "
from gemini_service import GeminiService
import asyncio
import os

async def test():
    service = GeminiService(os.getenv('GEMINI_API_KEY'))
    result = await service.simplify_terms('The doctor mentioned hypertension')
    print(result)

asyncio.run(test())
"
```

### Step 3: Backend Will Auto-Switch

Once your `gemini_service.py` exists, the backend will automatically use it!

```bash
# Start backend - it will detect and use your real service
python start_server.py
```

You'll see in the logs:
```
[INFO] Using REAL Gemini AI service
```

### Step 4: Verify Integration

Run the E2E test to verify everything works:

```bash
python test_e2e_integration.py
```

---

## Mock Service Reference

See `gemini_service_mock.py` for a reference implementation. Your real service should:

1. Use the same method signatures
2. Return the same data structure
3. Handle errors gracefully
4. Use async/await

---

## Prompts for Gemini API

The design document (`.kiro/specs/sidekick-medical-assistant/design.md`) contains the exact prompts to use for each function. Key sections:

- **Simplification Prompt:** Section 2.2
- **Question Suggestions Prompt:** Section 3.2
- **Summary Generation Prompt:** Section 5.2
- **Translation Prompt:** Section 6.2

---

## Error Handling

Your service should handle these errors:

```python
try:
    # Call Gemini API
    response = await gemini_api.call(...)
except Exception as e:
    logger.error(f"Gemini API error: {e}")
    # Return empty result or raise exception
    return {"terms": []}  # or raise
```

The backend will catch exceptions and send error messages to the client.

---

## Testing

### Unit Tests

Create tests in `ai-service/tests/`:

```python
# ai-service/tests/test_gemini_service.py
import pytest
from gemini_service import GeminiService

@pytest.mark.asyncio
async def test_simplify_terms():
    service = GeminiService("test-api-key")
    result = await service.simplify_terms("hypertension")
    assert "terms" in result
    assert len(result["terms"]) > 0
```

### Integration Tests

The backend already has integration tests that will work with your service:

```bash
# These tests will use your real service automatically
python test_e2e_integration.py
python -m pytest backend/tests/test_api_endpoints.py
```

---

## Environment Variables

Your service will receive the API key from environment:

```python
# In backend/main.py
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini = GeminiService(GEMINI_API_KEY)
```

Make sure your `.env` file has:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

---

## Performance Requirements

From the design document:

- **Simplification:** < 2 seconds per request
- **Questions:** < 2 seconds per request
- **Summary:** < 10 seconds per request
- **Translation:** < 2 seconds per request

The backend has performance monitoring that will log warnings if these are exceeded.

---

## Model Recommendation

Use `gemini-2.5-flash` model (verified working):

```python
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')
```

---

## Merge Strategy

When you push your `gemini_service.py`:

1. **No Conflicts:** Your file is `gemini_service.py`, mock is `gemini_service_mock.py`
2. **Auto-Switch:** Backend automatically uses your service
3. **Keep Mock:** The mock stays for testing without API calls
4. **No Changes Needed:** Backend code doesn't need modification

---

## Questions?

- **Backend Integration:** Check `backend/main.py` lines 20-35
- **Interface Details:** See `ai-service/gemini_service_mock.py`
- **Prompts:** See `.kiro/specs/sidekick-medical-assistant/design.md`
- **Requirements:** See `.kiro/specs/sidekick-medical-assistant/requirements.md`

---

## Status Checklist

- [ ] Create `gemini_service.py`
- [ ] Implement all 4 required methods
- [ ] Test with Gemini API
- [ ] Verify backend auto-switches
- [ ] Run integration tests
- [ ] Push to repository

---

**Good luck with the implementation!** 🚀

The backend is ready and waiting for your service.
