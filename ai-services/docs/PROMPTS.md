# Prompt Engineering Guide

This document explains the prompt templates used in the Gemini AI service and the engineering decisions behind them.

## Overview

All prompts are designed with these principles:
- **Clarity**: Explicit instructions with no ambiguity
- **Structure**: Consistent JSON output format
- **Patient-Centric**: Focus on patient understanding
- **Medical Accuracy**: Maintain clinical correctness
- **Edge Case Handling**: Handle empty/invalid inputs gracefully

## Prompt Templates

### 1. Medical Term Simplification

**Purpose**: Identify and explain medical terminology in plain language

**Template**:
```
You are a medical language simplifier. Given the following doctor-patient
conversation excerpt, identify ALL medical or clinical terms and explain
each in simple, patient-friendly language.

Transcript: "{transcript}"

Respond in this exact JSON format:
{
  "terms": [
    {"term": "medical term", "explanation": "simple explanation"}
  ]
}

If there are no medical terms, return {"terms": []}.

Guidelines:
- Explain terms at a 6th-grade reading level
- Use everyday language, not medical jargon
- Be concise but complete
- Include abbreviations and acronyms
- Focus on terms patients may not understand
```

**Engineering Decisions**:

1. **Reading Level**: 6th-grade ensures accessibility for most patients
2. **JSON Format**: Structured output for reliable parsing
3. **Empty Case**: Explicit handling of no medical terms
4. **Abbreviations**: Includes common medical abbreviations (BP, HR, etc.)
5. **Completeness**: "ALL medical terms" ensures nothing is missed

**Example Input/Output**:

Input:
```
"Patient has hypertension and tachycardia. ECG shows normal sinus rhythm."
```

Output:
```json
{
  "terms": [
    {"term": "hypertension", "explanation": "high blood pressure"},
    {"term": "tachycardia", "explanation": "fast heart rate"},
    {"term": "ECG", "explanation": "heart rhythm test"},
    {"term": "sinus rhythm", "explanation": "normal heart beat pattern"}
  ]
}
```

---

### 2. Question Suggestion

**Purpose**: Generate relevant clarification questions for patients

**Template**:
```
You are a patient advocate. Based on this doctor-patient conversation,
suggest 2-3 clarification questions the patient could ask to better
understand their condition and treatment.

Conversation so far:
"{full_transcript}"

Respond in this exact JSON format:
{
  "questions": [
    "Question 1?",
    "Question 2?",
    "Question 3?"
  ]
}

Guidelines:
- Generate 2-3 relevant, actionable questions
- Focus on current conversation context
- Prioritize questions about diagnosis, treatment, and next steps
- Avoid repetitive questions
- Make questions specific and helpful
- Questions should be easy for patients to ask
```

**Engineering Decisions**:

1. **Cardinality**: 2-3 questions balances helpfulness with not overwhelming
2. **Patient Advocate Role**: Frames AI as helping patient, not doctor
3. **Actionable**: Questions should lead to useful information
4. **Context-Aware**: Uses full transcript for relevance
5. **Specificity**: Avoids generic questions like "What should I do?"

**Example Input/Output**:

Input:
```
"Doctor: You have high blood pressure. I'm prescribing Lisinopril.
Patient: Okay.
Doctor: Take it once daily in the morning.
Patient: Alright."
```

Output:
```json
{
  "questions": [
    "What are the common side effects of Lisinopril?",
    "How long until my blood pressure improves?",
    "Do I need to take it with food or on an empty stomach?"
  ]
}
```

---

### 3. Visit Summary

**Purpose**: Create structured summary of medical appointment

**Template**:
```
You are a medical visit summarizer. Create a structured summary of this
doctor-patient conversation.

Full transcript:
"{full_transcript}"

Respond in this exact JSON format:
{
  "title": "Brief visit title (e.g., 'Hypertension Follow-up')",
  "diagnosis": "Main diagnosis or concern discussed",
  "medications": ["medication 1 with dosage", "medication 2 with dosage"],
  "instructions": ["instruction 1", "instruction 2"],
  "follow_up": "Follow-up plan (e.g., 'Return in 2 weeks')",
  "key_points": ["key point 1", "key point 2", "key point 3"]
}

Guidelines:
- Extract all medications with dosages if mentioned
- Include all care instructions
- Summarize key discussion points
- Be specific and accurate
- Use patient-friendly language
- If a field has no information, use empty string or empty array
```

**Engineering Decisions**:

1. **Structured Fields**: Ensures all important information captured
2. **Medication Dosages**: Critical for patient safety
3. **Instructions**: Actionable care steps
4. **Follow-up**: Clear next steps
5. **Key Points**: High-level summary for quick review
6. **Empty Handling**: Explicit guidance for missing information

**Example Input/Output**:

Input:
```
"Doctor: Your blood pressure is better. Continue Lisinopril 10mg daily.
Monitor your BP at home. Reduce salt intake. Come back in 3 months.
Patient: Okay, thank you."
```

Output:
```json
{
  "title": "Hypertension Follow-up",
  "diagnosis": "Essential hypertension, improving",
  "medications": ["Lisinopril 10mg once daily"],
  "instructions": [
    "Monitor blood pressure at home daily",
    "Reduce sodium intake in diet"
  ],
  "follow_up": "Return in 3 months",
  "key_points": [
    "Blood pressure showing improvement",
    "Continue current medication",
    "Lifestyle modifications working"
  ]
}
```

---

### 4. Translation

**Purpose**: Translate medical explanations to patient's language

**Template**:
```
Translate the following medical explanation into {target_language}.
Keep it simple and patient-friendly. Do not use technical jargon.

Text: "{text}"

Respond with only the translated text. Ensure the translation:
- Maintains medical accuracy
- Uses culturally appropriate language
- Avoids literal translations that lose meaning
- Is easy for patients to understand
```

**Engineering Decisions**:

1. **Simplicity**: Emphasizes patient-friendly language
2. **Medical Accuracy**: Must maintain clinical correctness
3. **Cultural Appropriateness**: Considers cultural context
4. **No Jargon**: Avoids technical terms in translation
5. **Plain Response**: No JSON needed, just translated text

**Example Input/Output**:

Input (English to Spanish):
```
"High blood pressure means the force of blood against your artery walls is too high."
```

Output:
```
"Presión arterial alta significa que la fuerza de la sangre contra las paredes de sus arterias es demasiado alta."
```

## Prompt Refinement Process

### Testing Methodology

1. **Specialty Testing**: Test with various medical specialties
   - Cardiology: heart conditions
   - Oncology: cancer terminology
   - Endocrinology: diabetes, hormones
   - Orthopedics: bone/joint terms

2. **Edge Cases**:
   - Very short transcripts (< 10 words)
   - Very long transcripts (> 1000 words)
   - Multiple diagnoses
   - No medical terms
   - Abbreviation-heavy text

3. **Language Testing**:
   - Test all 5 supported languages
   - Verify cultural appropriateness
   - Check medical accuracy in translation

### Refinement History

**Version 1.0** (Initial):
- Basic prompts with minimal guidance
- Issues: Inconsistent JSON format, missed abbreviations

**Version 1.1** (Current):
- Added explicit JSON format examples
- Added reading level guidance (6th grade)
- Added abbreviation handling
- Added edge case instructions
- Improved cultural appropriateness for translations

**Future Improvements**:
- Add examples in prompts for few-shot learning
- Specialty-specific prompts (cardiology vs oncology)
- Adaptive reading level based on patient profile

## Best Practices

### 1. Consistent Format

Always use exact JSON format specified:

```python
# Good
{"terms": [{"term": "...", "explanation": "..."}]}

# Bad (will fail parsing)
{"medical_terms": [...]}
```

### 2. Reading Level

Maintain 6th-grade reading level:

```python
# Good
"high blood pressure"

# Bad (too technical)
"elevated systolic and diastolic pressures"
```

### 3. Completeness

Identify ALL medical terms:

```python
# Good
["hypertension", "tachycardia", "ECG", "sinus rhythm"]

# Bad (incomplete)
["hypertension", "tachycardia"]
```

### 4. Context Awareness

Questions should reflect current conversation:

```python
# Good (context: discussing new medication)
"What are the side effects of this medication?"

# Bad (generic)
"What should I do?"
```

### 5. Cultural Sensitivity

Translations should be culturally appropriate:

```python
# Good (Spanish, culturally appropriate)
"presión arterial alta"

# Bad (literal translation, awkward)
"presión de sangre alta"
```

## Prompt Testing

### Unit Tests

Test each prompt with:
- Valid inputs
- Empty inputs
- Edge cases
- Multiple items
- Invalid formats

### Integration Tests

Test prompts in full workflow:
1. Transcript → Simplification
2. Transcript → Questions
3. Full transcript → Summary
4. Simplification → Translation

### Property Tests

Verify properties hold:
- All terms have explanations
- Questions are 2-3 in count
- Summary has all required fields
- Translations maintain meaning

## Troubleshooting

### Issue: Inconsistent JSON Format

**Solution**: Add explicit format example in prompt

```python
# Before
"Respond in JSON format"

# After
"Respond in this exact JSON format:
{
  \"terms\": [{\"term\": \"...\", \"explanation\": \"...\"}]
}"
```

### Issue: Missing Medical Terms

**Solution**: Emphasize completeness

```python
# Before
"Identify medical terms"

# After
"Identify ALL medical or clinical terms"
```

### Issue: Too Technical Explanations

**Solution**: Specify reading level

```python
# Before
"Explain in simple language"

# After
"Explain at a 6th-grade reading level using everyday language"
```

### Issue: Generic Questions

**Solution**: Add specificity guidance

```python
# Before
"Suggest questions"

# After
"Suggest specific, actionable questions about diagnosis, treatment, and next steps"
```

## Monitoring Prompt Quality

### Metrics to Track

1. **Parsing Success Rate**: % of responses that parse correctly
2. **Completeness**: % of medical terms identified
3. **Reading Level**: Automated readability scores
4. **User Feedback**: Patient understanding ratings

### Quality Checks

```python
# Check parsing success
try:
    data = json.loads(response)
    parsing_success = True
except:
    parsing_success = False

# Check completeness
expected_terms = ["hypertension", "tachycardia"]
found_terms = [t["term"] for t in data["terms"]]
completeness = len(found_terms) / len(expected_terms)

# Check reading level
from textstat import flesch_kincaid_grade
reading_level = flesch_kincaid_grade(explanation)
```

## Conclusion

Effective prompt engineering is critical for reliable AI assistance. These prompts have been refined through testing and will continue to evolve based on real-world usage and feedback.

For questions or suggestions, please refer to the main documentation or open an issue.
