"""
Prompt templates for all AI providers.
All prompts return a unified JSON schema with keys:
  medical_terms, suggested_questions, session_summary
for the combined insight call, or individual keys for separate calls.
"""

# ── Combined single-call prompt (used for real-time insights) ─
# Returns all three insight types in one LLM call to minimise latency.
COMBINED_INSIGHT_PROMPT = """You are a clinical AI assistant helping patients understand their medical appointment in real time.

Given this transcript excerpt, return a JSON object with exactly these three keys:

{{
  "medical_terms": [
    {{
      "term": "...",
      "explanation": "plain-English explanation at 6th-grade level",
      "importance": "high|medium|low"
    }}
  ],
  "suggested_questions": [
    "Question the patient could ask their doctor?"
  ],
  "session_summary": {{
    "key_points": ["brief point 1", "brief point 2"]
  }}
}}

Rules:
- medical_terms: list every clinical/medical term. If none, return [].
- importance: "high" = diagnosis/critical medication/urgent symptom, "medium" = treatment/test/condition, "low" = general medical vocabulary
- suggested_questions: 2-3 actionable questions. If insufficient context, return [].
- session_summary.key_points: 1-2 bullet points capturing what was just discussed.
- Return ONLY valid JSON. No markdown, no explanation outside the JSON.

Transcript excerpt:
"{transcript}"
"""

# ── Question explanation prompt ───────────────────────────────
QUESTION_EXPLANATION_PROMPT = """You are a patient-friendly medical explainer.

A patient is about to ask their doctor this question:
"{question}"

Based on the conversation context below, write a clear, plain-English explanation (2-4 sentences) of:
1. Why this question is important
2. What a typical answer might involve
3. What the patient should listen for

Keep it at a 6th-grade reading level. Be warm and reassuring.

Conversation context:
"{context}"

Return ONLY the explanation text — no JSON, no headers.
"""

# ── Full summary prompt (used on session end) ─────────────────
VISIT_SUMMARY_PROMPT = """You are a medical visit summarizer. Create a structured summary of this full doctor-patient conversation.

Full transcript:
"{full_transcript}"

Return ONLY this JSON (no markdown fences, no extra text):
{{
  "title": "Brief visit title (e.g. Hypertension Follow-up)",
  "diagnosis": "Main diagnosis or concern discussed",
  "medications": ["medication 1 with dosage if mentioned"],
  "instructions": ["care instruction 1", "care instruction 2"],
  "follow_up": "Follow-up plan or empty string",
  "key_points": ["key point 1", "key point 2", "key point 3"]
}}

If a field has no data, use empty string or empty array. Be specific and accurate.
"""

# ── Translation prompt ────────────────────────────────────────
TRANSLATION_PROMPT = """Translate the following medical explanation into {target_language}.
Keep it simple, patient-friendly, and medically accurate.
Return ONLY the translated text — no labels, no JSON.

Text: "{text}"
"""
