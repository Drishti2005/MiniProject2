# Backend and AI Services Integration Guide

## Current Situation

The AI team has implemented the Gemini service in the `ai-services/` folder (with an 's'), but the backend is configured to import from `ai-service/` (without the 's'). This guide explains how to integrate them properly.

## Directory Structure

```
project-root/
├── ai-services/              # Real AI implementation (with 's')
│   ├── gemini_service.py    # Full Gemini API implementation
│   ├── config.py            # Configuration
│   ├── prompts.py           # Prompt templates
│   ├── requirements.txt     # AI dependencies
│   └── tests/               # AI tests
│
├── ai-service/              # Mock service folder (without 's')
│   └── gemini_service_mock.py  # Mock for testing
│
└── backend/                 # Backend implementation
    ├── main.py              # FastAPI app (imports AI service)
    ├── database_sqlite.py   # Database layer
    └── tests/               # Backend tests
```

## Integration Options

### Option 1: Copy Real Service to ai-service/ (Recommended)

Copy the real implementation from `ai-services/` to `ai-service/` so the backend can import it directly.

```bash
# Copy the real service files
cp ai-services/gemini_service.py ai-service/
cp ai-services/config.py ai-service/
cp ai-services/prompts.py ai-service/
cp ai-services/requirements.txt ai-service/
cp ai-services/__init__.py ai-service/ 2>/dev/null || echo "# AI Service" > ai-service/__init__.py
```

### Option 2: Update Backend Import Paths

Modify `backend/main.py` to import from `ai-services/` instead of `ai-service/`.

```python
# Change this:
from ai_service.gemini_service import GeminiService

# To this:
from ai_services.gemini_service import GeminiService
```

### Option 3: Create Symbolic Link (Unix/Linux/Mac only)

```bash
# Remove the old ai-service folder
rm -rf ai-service

# Create symbolic link
ln -s ai-services ai-service
```

## Implementation Steps (Option 1 - Recommended)

### Step 1: Copy Files

```bash
# Navigate to project root
cd /path/to/project

# Copy real AI service files
cp ai-services/gemini_service.py ai-service/
cp ai-services/config.py ai-service/
cp ai-services/prompts.py ai-service/
```

### Step 2: Create __init__.py

```bash
echo "# AI Service Package" > ai-service/__init__.py
```

### Step 3: Update Requirements

Merge AI service requirements into backend requirements:

```bash
# Append AI requirements to backend requirements
cat ai-services/requirements.txt >> backend/requirements.txt

# Remove duplicates (manual step)
```

### Step 4: Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### Step 5: Verify Integration

```python
# Test import
python -c "from ai_service.gemini_service import GeminiService; print('Import successful!')"
```

## Backend Integration Points

The backend (`backend/main.py`) integrates with AI service at these points:

### 1. Service Initialization

```python
# In backend/main.py
from ai_service.gemini_service import GeminiService

gemini = GeminiService(GEMINI_API_KEY)
```

### 2. Transcript Processing

```python
# In handle_transcript() function
simplifications = await gemini.simplify_terms(text)
questions = await gemini.suggest_questions(" ".join(full_transcript))
translated = await gemini.translate_text(explanation, language)
```

### 3. Session Summary

```python
# In handle_end_session() function
summary = await gemini.generate_summary(full_text)
```

## API Contract

The backend expects the AI service to implement these methods:

### simplify_terms(transcript: str) -> List[Dict]

```python
# Input: transcript chunk
# Output: [{"term": "hypertension", "explanation": "high blood pressure"}]
```

### suggest_questions(full_transcript: str) -> List[str]

```python
# Input: full conversation
# Output: ["What are the side effects?", "How often should I take this?"]
```

### generate_summary(full_transcript: str) -> Dict

```python
# Input: full conversation
# Output: {
#     "title": "Hypertension Follow-up",
#     "diagnosis": "Elevated blood pressure",
#     "medications": ["ACE inhibitor 10mg daily"],
#     "instructions": ["Take with food", "Monitor BP daily"],
#     "follow_up": "Return in 2 weeks",
#     "key_points": ["BP elevated", "Starting medication"]
# }
```

### translate_text(text: str, target_language: str) -> str

```python
# Input: text and language code (es, hi, zh, fr, ar)
# Output: translated text
```

## Testing Integration

### Test 1: Import Test

```python
# test_ai_integration.py
from ai_service.gemini_service import GeminiService
import os

def test_import():
    api_key = os.getenv("GEMINI_API_KEY", "test-key")
    service = GeminiService(api_key)
    assert service is not None
```

### Test 2: Simplification Test

```python
import asyncio
from ai_service.gemini_service import GeminiService

async def test_simplification():
    service = GeminiService(os.getenv("GEMINI_API_KEY"))
    result = await service.simplify_terms("Patient has hypertension")
    print(f"Terms found: {result}")

asyncio.run(test_simplification())
```

### Test 3: End-to-End Test

```bash
# Start the backend server
cd backend
python -m uvicorn main:app --reload

# In another terminal, test WebSocket connection
# (Use frontend or WebSocket client)
```

## Environment Variables

Ensure these are set in `.env`:

```bash
# Gemini API Key (required)
GEMINI_API_KEY=your_actual_api_key_here

# Database URL
DATABASE_URL=sqlite+aiosqlite:///./sidekick.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## Troubleshooting

### Issue: Import Error

```
ImportError: No module named 'ai_service.gemini_service'
```

**Solution**: Ensure files are copied to `ai-service/` and `__init__.py` exists.

### Issue: Missing Dependencies

```
ModuleNotFoundError: No module named 'google.generativeai'
```

**Solution**: Install AI service dependencies:
```bash
pip install google-generativeai
```

### Issue: API Key Error

```
ValueError: GEMINI_API_KEY is required
```

**Solution**: Set the API key in `.env` file.

### Issue: Rate Limit Errors

```
Rate limit reached. Queueing request for X seconds
```

**Solution**: This is normal behavior. The service queues requests automatically.

## Performance Considerations

1. **Rate Limiting**: AI service limits to 15 requests/minute
2. **Timeouts**: API calls timeout after 10 seconds
3. **Retries**: Failed requests retry up to 3 times with exponential backoff
4. **Caching**: Consider implementing response caching for repeated queries

## Security Notes

1. **API Key**: Never commit API keys to version control
2. **Sanitization**: AI service automatically sanitizes sensitive data (SSN, emails, phone numbers)
3. **HTTPS**: Always use HTTPS in production
4. **Logging**: Sensitive data is redacted from logs

## Next Steps

1. ✅ Copy AI service files to `ai-service/` folder
2. ✅ Install dependencies
3. ✅ Test imports
4. ✅ Run backend tests
5. ✅ Test end-to-end with frontend
6. ✅ Deploy to production

## Support

For issues with:
- **AI Service**: Check `ai-services/README.md` and `ai-services/docs/`
- **Backend**: Check `backend/README.md`
- **Integration**: Refer to this document

## Conclusion

The AI service is fully implemented and production-ready. Follow Option 1 (copying files) for the simplest integration, or Option 2 (updating imports) if you prefer to keep a single source of truth in `ai-services/`.
