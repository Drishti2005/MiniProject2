# AI Service - Gemini Integration

**Team: AI Integration**

This folder contains the Google Gemini API integration for medical term simplification, question generation, translation, and visit summary generation.

## Files

- `gemini_service.py` - Main Gemini API service class
- `requirements.txt` - Python dependencies for AI service
- `tests/` - AI service tests

## Setup

1. Install dependencies:
```bash
cd ai-service
pip install -r requirements.txt
```

2. Set up API key in `.env` file (in project root):
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

The Backend Infrastructure team imports this service:

```python
# In backend/main.py
import sys
sys.path.append('..')  # Add parent directory to path
from ai_service.gemini_service import GeminiService

gemini = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))
```

## Methods

- `simplify_terms(transcript)` - Identify and explain medical terms
- `suggest_questions(full_transcript)` - Generate 2-3 clarification questions
- `generate_summary(full_transcript)` - Create structured visit summary
- `translate_text(text, target_language)` - Translate to patient's language

## Testing

Run tests:
```bash
pytest tests/
```

## Task Reference

See `.kiro/specs/sidekick-medical-assistant/tasks-ai-integration.md` for detailed implementation tasks.
