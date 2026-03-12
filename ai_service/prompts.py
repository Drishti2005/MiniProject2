"""
Prompt templates for Gemini AI operations.
"""

# Medical Term Simplification Prompt
SIMPLIFICATION_PROMPT = """You are a medical language simplifier. Given the following doctor-patient conversation excerpt, identify ALL medical or clinical terms and explain each in simple, patient-friendly language.

Transcript: "{transcript}"

Respond in this exact JSON format:
{{
  "terms": [
    {{"term": "medical term", "explanation": "simple explanation"}}
  ]
}}

If there are no medical terms, return {{"terms": []}}.

Guidelines:
- Explain terms at a 6th-grade reading level
- Use everyday language, not medical jargon
- Be concise but complete
- Include abbreviations and acronyms
- Focus on terms patients may not understand
"""

# Question Suggestion Prompt
QUESTION_SUGGESTION_PROMPT = """You are a patient advocate. Based on this doctor-patient conversation, suggest 2-3 clarification questions the patient could ask to better understand their condition and treatment.

Conversation so far:
"{full_transcript}"

Respond in this exact JSON format:
{{
  "questions": [
    "Question 1?",
    "Question 2?",
    "Question 3?"
  ]
}}

Guidelines:
- Generate 2-3 relevant, actionable questions
- Focus on current conversation context
- Prioritize questions about diagnosis, treatment, and next steps
- Avoid repetitive questions
- Make questions specific and helpful
- Questions should be easy for patients to ask
"""

# Visit Summary Prompt
VISIT_SUMMARY_PROMPT = """You are a medical visit summarizer. Create a structured summary of this doctor-patient conversation.

Full transcript:
"{full_transcript}"

Respond in this exact JSON format:
{{
  "title": "Brief visit title (e.g., 'Hypertension Follow-up')",
  "diagnosis": "Main diagnosis or concern discussed",
  "medications": ["medication 1 with dosage", "medication 2 with dosage"],
  "instructions": ["instruction 1", "instruction 2"],
  "follow_up": "Follow-up plan (e.g., 'Return in 2 weeks')",
  "key_points": ["key point 1", "key point 2", "key point 3"]
}}

Guidelines:
- Extract all medications with dosages if mentioned
- Include all care instructions
- Summarize key discussion points
- Be specific and accurate
- Use patient-friendly language
- If a field has no information, use empty string or empty array
"""

# Translation Prompt
TRANSLATION_PROMPT = """Translate the following medical explanation into {target_language}. Keep it simple and patient-friendly. Do not use technical jargon.

Text: "{text}"

Respond with only the translated text. Ensure the translation:
- Maintains medical accuracy
- Uses culturally appropriate language
- Avoids literal translations that lose meaning
- Is easy for patients to understand
"""

# Prompt Refinement Notes
"""
Prompt Engineering Decisions:

1. Simplification Prompt:
   - Explicitly requests JSON format for reliable parsing
   - Specifies 6th-grade reading level for accessibility
   - Handles edge case of no medical terms
   - Includes abbreviations/acronyms guidance

2. Question Suggestion Prompt:
   - Limits to 2-3 questions to avoid overwhelming patients
   - Emphasizes actionable, relevant questions
   - Focuses on current context to avoid repetition
   - Prioritizes diagnosis, treatment, next steps

3. Visit Summary Prompt:
   - Structured format ensures all required fields
   - Medication dosage extraction for accuracy
   - Handles multiple diagnoses and medications
   - Patient-friendly language throughout

4. Translation Prompt:
   - Emphasizes medical accuracy with simplicity
   - Cultural appropriateness for better understanding
   - Avoids literal translations that may confuse
   - Simple response format (no JSON needed)

All prompts use:
- Clear instructions
- Explicit output format
- Edge case handling
- Patient-centric language
- Medical accuracy requirements
"""
