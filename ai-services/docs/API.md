# Gemini Service API Documentation

Complete API reference for the GeminiService class.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [GeminiService Class](#geminiservice-class)
- [Methods](#methods)
- [Error Handling](#error-handling)
- [Performance Monitoring](#performance-monitoring)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

Optional configuration in `config.py`:

```python
GEMINI_MODEL = "gemini-2.0-flash-exp"
MAX_REQUESTS_PER_MINUTE = 15
API_TIMEOUT_SECONDS = 10
MAX_RETRY_ATTEMPTS = 3
TEMPERATURE = 0.3
```

## GeminiService Class

### Initialization

```python
from gemini_service import GeminiService

service = GeminiService(api_key="your_api_key")
```

**Parameters:**
- `api_key` (str, required): Google Gemini API key

**Raises:**
- `ValueError`: If API key is missing or invalid

**Example:**
```python
import os
from gemini_service import GeminiService

api_key = os.getenv("GEMINI_API_KEY")
service = GeminiService(api_key=api_key)
```

## Methods

### simplify_terms

Simplify medical terms in a transcript chunk.

```python
async def simplify_terms(transcript: str) -> List[Dict[str, str]]
```

**Parameters:**
- `transcript` (str): Transcript chunk containing potential medical terms

**Returns:**
- `List[Dict[str, str]]`: List of dictionaries with 'term' and 'explanation' keys

**Example:**
```python
terms = await service.simplify_terms(
    "Patient has hypertension and tachycardia"
)

print(terms)
# [
#     {"term": "hypertension", "explanation": "high blood pressure"},
#     {"term": "tachycardia", "explanation": "fast heart rate"}
# ]
```

**Behavior:**
- Returns empty list if no medical terms found
- Returns empty list if transcript is empty
- Handles errors gracefully by returning empty list
- Response time: < 2 seconds

---

### suggest_questions

Generate question suggestions based on conversation context.

```python
async def suggest_questions(full_transcript: str) -> List[str]
```

**Parameters:**
- `full_transcript` (str): Complete conversation transcript

**Returns:**
- `List[str]`: List of 2-3 suggested questions

**Example:**
```python
questions = await service.suggest_questions(
    "Doctor discussed blood pressure medication. "
    "Patient asked about side effects. "
    "Doctor explained the benefits and risks."
)

print(questions)
# [
#     "What are the most common side effects?",
#     "How long until the medication takes effect?",
#     "Do I need to take it with food?"
# ]
```

**Behavior:**
- Requires minimum 50 words for sufficient context
- Returns empty list if context insufficient
- Returns 2-3 questions (limited to 3 max)
- Handles errors gracefully by returning empty list
- Response time: < 2 seconds

---

### generate_summary

Generate structured visit summary from full transcript.

```python
async def generate_summary(full_transcript: str) -> Dict
```

**Parameters:**
- `full_transcript` (str): Complete conversation transcript

**Returns:**
- `Dict`: Dictionary with keys:
  - `title` (str): Brief visit title
  - `diagnosis` (str): Main diagnosis or concern
  - `medications` (List[str]): List of medications with dosages
  - `instructions` (List[str]): Care instructions
  - `follow_up` (str): Follow-up plan
  - `key_points` (List[str]): Key discussion points

**Example:**
```python
summary = await service.generate_summary(full_transcript)

print(summary)
# {
#     "title": "Hypertension Follow-up",
#     "diagnosis": "Essential hypertension, well-controlled",
#     "medications": ["Lisinopril 10mg daily", "Aspirin 81mg daily"],
#     "instructions": ["Monitor BP daily", "Reduce sodium intake"],
#     "follow_up": "Return in 3 months",
#     "key_points": ["BP improved", "Continue medications"]
# }
```

**Behavior:**
- Returns empty summary structure if transcript empty
- Validates all required fields present
- Normalizes invalid field types
- Handles errors gracefully by returning empty summary
- Response time: < 10 seconds

---

### translate_text

Translate text to target language.

```python
async def translate_text(text: str, target_language: str) -> str
```

**Parameters:**
- `text` (str): Text to translate
- `target_language` (str): Target language code
  - Supported: `es` (Spanish), `hi` (Hindi), `zh` (Mandarin), `fr` (French), `ar` (Arabic)

**Returns:**
- `str`: Translated text

**Raises:**
- `ValueError`: If language not supported

**Example:**
```python
translated = await service.translate_text(
    "High blood pressure",
    "es"
)

print(translated)
# "Presión arterial alta"
```

**Behavior:**
- Returns empty string if text is empty
- Returns original text on error
- Maintains medical accuracy
- Uses patient-friendly language
- Response time: < 2 seconds

---

### get_performance_stats

Get performance statistics for monitoring.

```python
def get_performance_stats() -> Dict
```

**Returns:**
- `Dict`: Dictionary with keys:
  - `total_requests` (int): Total API requests made
  - `average_response_time` (float): Average response time in seconds
  - `slow_requests` (int): Number of slow requests (>5 seconds)
  - `slow_request_percentage` (float): Percentage of slow requests

**Example:**
```python
stats = service.get_performance_stats()

print(stats)
# {
#     "total_requests": 42,
#     "average_response_time": 1.23,
#     "slow_requests": 2,
#     "slow_request_percentage": 4.76
# }
```

## Error Handling

The service implements comprehensive error handling:

### Timeout Errors

- API calls timeout after 10 seconds
- Automatic retry with exponential backoff (1s, 2s, 4s)
- Up to 3 retry attempts

```python
try:
    result = await service.simplify_terms(transcript)
except Exception as e:
    print(f"Error: {e}")
    # Service already logged the error
```

### Rate Limiting

- Maximum 15 requests per minute
- Excess requests automatically queued
- Transparent to caller

### API Errors

- All API errors logged with context
- User-friendly error messages returned
- Operations return safe defaults on error:
  - `simplify_terms`: empty list
  - `suggest_questions`: empty list
  - `generate_summary`: empty summary structure
  - `translate_text`: original text

### JSON Parsing Errors

- Handles malformed JSON responses
- Extracts JSON from markdown code blocks
- Validates response structure
- Returns safe defaults on parsing failure

## Performance Monitoring

### Logging

The service logs:
- All API calls with operation type
- Response times
- Slow requests (>5 seconds)
- All errors with context

```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)

# Service will log:
# INFO: API call: simplify_terms (attempt 1/3)
# INFO: API response: simplify_terms completed in 1.23s
# WARNING: Slow request: generate_summary took 6.45s
# ERROR: Error on simplify_terms (attempt 1): API timeout
```

### Performance Stats

Track performance over time:

```python
# Make some API calls
await service.simplify_terms(transcript1)
await service.suggest_questions(transcript2)
await service.generate_summary(transcript3)

# Check performance
stats = service.get_performance_stats()
print(f"Average response time: {stats['average_response_time']}s")
print(f"Slow requests: {stats['slow_request_percentage']}%")
```

## Security Features

### Prompt Sanitization

Sensitive data automatically redacted:
- Social Security Numbers (SSN)
- Email addresses
- Phone numbers

```python
# Input: "Patient SSN is 123-45-6789"
# Sanitized: "Patient SSN is [REDACTED]"
```

### HTTPS Enforcement

All API calls use HTTPS protocol (enforced by Gemini SDK).

### API Key Validation

API key format validated on initialization:

```python
try:
    service = GeminiService(api_key="short")
except ValueError as e:
    print(e)  # "Invalid GEMINI_API_KEY format"
```

## Best Practices

### 1. Error Handling

Always handle potential errors:

```python
try:
    terms = await service.simplify_terms(transcript)
    if not terms:
        print("No medical terms found")
except Exception as e:
    logger.error(f"Simplification failed: {e}")
```

### 2. Context Requirements

Ensure sufficient context for questions:

```python
# Check word count before calling
word_count = len(transcript.split())
if word_count >= 50:
    questions = await service.suggest_questions(transcript)
else:
    print("Insufficient context for questions")
```

### 3. Performance Monitoring

Monitor performance regularly:

```python
stats = service.get_performance_stats()
if stats['slow_request_percentage'] > 10:
    logger.warning("High percentage of slow requests")
```

### 4. Rate Limiting

The service handles rate limiting automatically, but be aware:

```python
# These calls will be automatically queued if rate limit reached
for transcript in transcripts:
    await service.simplify_terms(transcript)
    # Service handles queueing transparently
```

## Complete Example

```python
import os
import asyncio
from gemini_service import GeminiService

async def main():
    # Initialize service
    api_key = os.getenv("GEMINI_API_KEY")
    service = GeminiService(api_key=api_key)
    
    # Simplify medical terms
    transcript = "Patient has hypertension and tachycardia"
    terms = await service.simplify_terms(transcript)
    print("Simplified terms:", terms)
    
    # Generate questions
    full_transcript = " ".join(["Medical conversation"] * 20)
    questions = await service.suggest_questions(full_transcript)
    print("Suggested questions:", questions)
    
    # Generate summary
    summary = await service.generate_summary(full_transcript)
    print("Visit summary:", summary)
    
    # Translate
    translated = await service.translate_text("High blood pressure", "es")
    print("Translation:", translated)
    
    # Check performance
    stats = service.get_performance_stats()
    print("Performance stats:", stats)

if __name__ == "__main__":
    asyncio.run(main())
```
