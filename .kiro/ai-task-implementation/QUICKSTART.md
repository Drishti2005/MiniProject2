# Quick Start Guide

Get the AI service running in 5 minutes.

## Prerequisites

- Python 3.8+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# GEMINI_API_KEY=your_actual_api_key_here
```

Or set directly:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

### 3. Verify Installation

```bash
python -c "from gemini_service import GeminiService; print('✓ Installation successful')"
```

## Basic Usage

### Example 1: Simplify Medical Terms

```python
import asyncio
import os
from gemini_service import GeminiService

async def main():
    # Initialize service
    service = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Simplify medical terms
    transcript = "Patient has hypertension and tachycardia"
    terms = await service.simplify_terms(transcript)
    
    print("Simplified Terms:")
    for term in terms:
        print(f"  {term['term']}: {term['explanation']}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Output**:
```
Simplified Terms:
  hypertension: high blood pressure
  tachycardia: fast heart rate
```

### Example 2: Generate Questions

```python
import asyncio
import os
from gemini_service import GeminiService

async def main():
    service = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Generate questions
    transcript = """
    Doctor: You have high blood pressure. I'm prescribing Lisinopril.
    Take it once daily in the morning. Monitor your blood pressure at home.
    Come back in 3 months for a follow-up.
    """
    
    questions = await service.suggest_questions(transcript)
    
    print("Suggested Questions:")
    for i, question in enumerate(questions, 1):
        print(f"  {i}. {question}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Output**:
```
Suggested Questions:
  1. What are the common side effects of Lisinopril?
  2. How long until my blood pressure improves?
  3. What blood pressure readings should I watch for?
```

### Example 3: Generate Visit Summary

```python
import asyncio
import os
from gemini_service import GeminiService

async def main():
    service = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Generate summary
    transcript = """
    Doctor: Your blood pressure is better. Continue Lisinopril 10mg daily.
    Monitor your BP at home. Reduce salt intake. Come back in 3 months.
    Patient: Okay, thank you.
    """
    
    summary = await service.generate_summary(transcript)
    
    print("Visit Summary:")
    print(f"  Title: {summary['title']}")
    print(f"  Diagnosis: {summary['diagnosis']}")
    print(f"  Medications: {', '.join(summary['medications'])}")
    print(f"  Follow-up: {summary['follow_up']}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Output**:
```
Visit Summary:
  Title: Hypertension Follow-up
  Diagnosis: Essential hypertension, improving
  Medications: Lisinopril 10mg once daily
  Follow-up: Return in 3 months
```

### Example 4: Translate Text

```python
import asyncio
import os
from gemini_service import GeminiService

async def main():
    service = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Translate to Spanish
    text = "High blood pressure"
    translated = await service.translate_text(text, "es")
    
    print(f"English: {text}")
    print(f"Spanish: {translated}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Output**:
```
English: High blood pressure
Spanish: Presión arterial alta
```

## Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_simplification.py
```

### Run with Coverage

```bash
pytest --cov=. tests/
```

### Run Property-Based Tests

```bash
pytest tests/test_properties.py
```

## Common Issues

### Issue: API Key Not Found

**Error**: `ValueError: GEMINI_API_KEY is required`

**Solution**:
```bash
# Check if environment variable is set
echo $GEMINI_API_KEY

# If empty, set it
export GEMINI_API_KEY="your_api_key_here"
```

### Issue: Import Error

**Error**: `ModuleNotFoundError: No module named 'google.generativeai'`

**Solution**:
```bash
pip install google-generativeai
```

### Issue: Rate Limit Exceeded

**Error**: Requests taking a long time

**Solution**: The service automatically queues requests. Wait for queue to process.

```python
# Check performance stats
stats = service.get_performance_stats()
print(f"Total requests: {stats['total_requests']}")
```

## Next Steps

1. ✅ Basic usage working
2. 📖 Read [API.md](docs/API.md) for complete API reference
3. 🔧 Read [INTEGRATION.md](docs/INTEGRATION.md) to integrate with backend
4. 📝 Read [PROMPTS.md](docs/PROMPTS.md) to understand prompt engineering
5. 🚀 Deploy to production

## Complete Example

Here's a complete example using all features:

```python
import asyncio
import os
from gemini_service import GeminiService

async def process_medical_conversation():
    """Complete example using all AI features."""
    
    # Initialize service
    api_key = os.getenv("GEMINI_API_KEY")
    service = GeminiService(api_key=api_key)
    
    # Sample medical conversation
    transcript = """
    Doctor: Your blood pressure is 140/90, which is elevated. 
    You have hypertension. I'm prescribing Lisinopril 10mg once daily.
    Take it in the morning with food. Monitor your BP at home daily.
    Reduce sodium intake and exercise regularly.
    Come back in 3 months for follow-up.
    Patient: What are the side effects?
    Doctor: Common side effects include dizziness and dry cough.
    """
    
    print("=" * 60)
    print("MEDICAL CONVERSATION PROCESSING")
    print("=" * 60)
    
    # 1. Simplify medical terms
    print("\n1. SIMPLIFIED MEDICAL TERMS:")
    terms = await service.simplify_terms(transcript)
    for term in terms:
        print(f"   • {term['term']}: {term['explanation']}")
    
    # 2. Generate questions
    print("\n2. SUGGESTED QUESTIONS:")
    questions = await service.suggest_questions(transcript)
    for i, question in enumerate(questions, 1):
        print(f"   {i}. {question}")
    
    # 3. Generate summary
    print("\n3. VISIT SUMMARY:")
    summary = await service.generate_summary(transcript)
    print(f"   Title: {summary['title']}")
    print(f"   Diagnosis: {summary['diagnosis']}")
    print(f"   Medications:")
    for med in summary['medications']:
        print(f"     - {med}")
    print(f"   Instructions:")
    for inst in summary['instructions']:
        print(f"     - {inst}")
    print(f"   Follow-up: {summary['follow_up']}")
    
    # 4. Translate (example: to Spanish)
    print("\n4. TRANSLATION (Spanish):")
    if terms:
        first_term = terms[0]
        translated = await service.translate_text(
            first_term['explanation'], 
            "es"
        )
        print(f"   {first_term['term']}: {translated}")
    
    # 5. Performance stats
    print("\n5. PERFORMANCE STATS:")
    stats = service.get_performance_stats()
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Average response time: {stats['average_response_time']}s")
    print(f"   Slow requests: {stats['slow_requests']}")
    
    print("\n" + "=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(process_medical_conversation())
```

**Run it**:
```bash
python complete_example.py
```

## Support

- 📖 Documentation: See `docs/` folder
- 🐛 Issues: Check troubleshooting sections in docs
- 💬 Questions: Refer to API.md and INTEGRATION.md

## Success!

You're now ready to use the AI service. For production deployment, follow the [Integration Guide](docs/INTEGRATION.md).
