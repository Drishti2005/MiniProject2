"""
Smart Mock AI provider — used when no valid API key is available or quota is exhausted.
Uses a comprehensive medical term dictionary so the UI is fully functional for demos.
Logs a clear warning to ai_debug.log.
"""

import asyncio
import logging
import re
from typing import Dict, List

from .base import BaseAIService, _write_debug

logger = logging.getLogger(__name__)

# ── Comprehensive medical term dictionary ─────────────────────
_TERMS = {
    # Endocrine / thyroid
    "hypothyroidism":    ("underactive thyroid — your thyroid gland doesn't make enough hormone, slowing your metabolism", "high"),
    "hyperthyroidism":   ("overactive thyroid — your thyroid makes too much hormone, speeding up body functions", "high"),
    "thyroid":           ("a butterfly-shaped gland in your neck that controls metabolism and energy", "medium"),
    "thyroid hormone":   ("a chemical made by the thyroid gland that controls how fast your body works", "high"),
    "metabolism":        ("the process your body uses to convert food into energy", "medium"),
    "tsh":               ("thyroid-stimulating hormone — a blood test that checks how well your thyroid is working", "high"),
    "levothyroxine":     ("a medication that replaces the thyroid hormone your body isn't making enough of", "high"),
    "endocrine":         ("relating to glands that release hormones directly into the bloodstream", "low"),
    # Cardiovascular
    "hypertension":      ("high blood pressure — the force of blood against artery walls is too high", "high"),
    "blood pressure":    ("the pressure of blood pushing against the walls of your blood vessels", "medium"),
    "cardiovascular":    ("relating to the heart and blood vessels", "medium"),
    "cardiac":           ("relating to the heart", "medium"),
    "arrhythmia":        ("an irregular heartbeat — the heart beats too fast, too slow, or unevenly", "high"),
    "tachycardia":       ("a heart rate that is faster than normal (over 100 beats per minute)", "high"),
    "bradycardia":       ("a heart rate that is slower than normal (under 60 beats per minute)", "high"),
    "ecg":               ("electrocardiogram — a painless test that records the electrical activity of your heart", "medium"),
    "cholesterol":       ("a fatty substance in your blood; high levels can clog arteries", "medium"),
    "ldl":               ("bad cholesterol — high levels can build up in arteries and cause blockages", "high"),
    "hdl":               ("good cholesterol — helps remove bad cholesterol from your arteries", "medium"),
    "lisinopril":        ("a medication (ACE inhibitor) used to lower blood pressure", "high"),
    "statin":            ("a type of medication that lowers cholesterol levels in the blood", "high"),
    "atherosclerosis":   ("hardening and narrowing of the arteries due to plaque buildup", "high"),
    # Diabetes
    "diabetes":          ("a condition where blood sugar levels are too high", "high"),
    "insulin":           ("a hormone that helps your body use sugar for energy", "high"),
    "glucose":           ("blood sugar — the main source of energy for your body's cells", "medium"),
    "hba1c":             ("a blood test showing your average blood sugar level over the past 3 months", "high"),
    "metformin":         ("a medication used to control blood sugar in type 2 diabetes", "high"),
    "hyperglycemia":     ("high blood sugar — when there is too much glucose in the blood", "high"),
    "hypoglycemia":      ("low blood sugar — when blood glucose drops too low, causing dizziness or weakness", "high"),
    # Respiratory
    "asthma":            ("a condition where airways narrow and swell, making breathing difficult", "high"),
    "copd":              ("chronic obstructive pulmonary disease — a lung disease that makes breathing hard", "high"),
    "dyspnea":           ("shortness of breath — difficulty breathing or feeling like you can't get enough air", "high"),
    "bronchitis":        ("inflammation of the airways in the lungs, causing coughing and mucus", "medium"),
    "pneumonia":         ("an infection that inflames the air sacs in one or both lungs", "high"),
    "inhaler":           ("a device that delivers medication directly into the lungs", "medium"),
    # Neurological
    "migraine":          ("a severe headache, often with nausea and sensitivity to light and sound", "medium"),
    "neuropathy":        ("nerve damage that causes pain, numbness, or weakness, usually in hands and feet", "high"),
    "cognitive":         ("relating to mental processes like thinking, memory, and understanding", "low"),
    "cognitive slowing": ("when thinking and mental processing become slower than usual", "medium"),
    "vertigo":           ("a feeling that you or your surroundings are spinning or moving", "medium"),
    "dizziness":         ("a feeling of being lightheaded, unsteady, or faint", "medium"),
    # Musculoskeletal
    "arthritis":         ("inflammation of one or more joints, causing pain and stiffness", "medium"),
    "osteoporosis":      ("a condition where bones become weak and brittle, increasing fracture risk", "high"),
    "muscle cramps":     ("sudden, involuntary contractions of a muscle, causing sharp pain", "low"),
    "fibromyalgia":      ("a condition causing widespread muscle pain, fatigue, and tenderness", "medium"),
    # General
    "fatigue":           ("extreme tiredness that doesn't go away with rest", "medium"),
    "dehydration":       ("when your body loses more fluid than you take in, causing thirst and dizziness", "medium"),
    "inflammation":      ("the body's response to injury or infection — causes redness, swelling, and pain", "medium"),
    "chronic":           ("a condition that lasts a long time or keeps coming back", "low"),
    "acute":             ("a condition that comes on suddenly and is usually severe but short-lived", "low"),
    "benign":            ("not harmful or cancerous", "medium"),
    "malignant":         ("cancerous — cells that can invade and destroy nearby tissue", "high"),
    "biopsy":            ("removing a small sample of tissue to test it for disease", "medium"),
    "prognosis":         ("the likely outcome or course of a disease", "medium"),
    "diagnosis":         ("identifying a disease or condition based on symptoms and tests", "medium"),
    "prescription":      ("a doctor's written order for medication", "low"),
    "dosage":            ("the amount of medication to take and how often", "high"),
    "contraindication":  ("a reason why a treatment should not be used in a particular situation", "high"),
    "side effect":       ("an unwanted effect of a medication in addition to its intended purpose", "medium"),
    "allergy":           ("an immune system reaction to a substance that is normally harmless", "high"),
    "anemia":            ("a condition where you don't have enough healthy red blood cells to carry oxygen", "high"),
    "edema":             ("swelling caused by excess fluid trapped in body tissues", "medium"),
    "sodium":            ("salt — too much can raise blood pressure and cause fluid retention", "medium"),
    "potassium":         ("a mineral important for heart and muscle function", "medium"),
    "bmi":               ("body mass index — a measure of body fat based on height and weight", "low"),
    "obesity":           ("having a body weight significantly above what is considered healthy", "high"),
    "antibiotic":        ("a medication that kills or stops the growth of bacteria", "high"),
    "anti-inflammatory": ("a medication that reduces inflammation and pain", "medium"),
    "beta blocker":      ("a medication that slows the heart rate and lowers blood pressure", "high"),
    "diuretic":          ("a medication that helps your kidneys remove excess fluid from the body", "high"),
    "anticoagulant":     ("a blood thinner — medication that prevents blood clots from forming", "high"),
    "corticosteroid":    ("a medication that reduces inflammation and suppresses the immune system", "high"),
    "mri":               ("magnetic resonance imaging — a scan that uses magnets to create detailed images", "medium"),
    "ct scan":           ("computed tomography — an X-ray scan that creates cross-sectional images", "medium"),
    "ultrasound":        ("a scan that uses sound waves to create images of organs inside the body", "medium"),
}

# ── Question templates by topic ────────────────────────────────
_QUESTION_TEMPLATES = [
    "How will this condition affect my daily life?",
    "What are the warning signs I should watch out for?",
    "Are there lifestyle changes that could help my condition?",
    "What are the possible side effects of this treatment?",
    "How long will I need to take this medication?",
    "Should I make any changes to my diet or exercise routine?",
    "When should I come back for a follow-up appointment?",
    "Are there any activities I should avoid?",
    "Is this condition hereditary — should my family members be tested?",
    "What happens if I don't treat this condition?",
]


def _find_terms(text: str) -> List[Dict[str, str]]:
    lower = text.lower()
    found = []
    seen_terms = set()
    for term in sorted(_TERMS.keys(), key=len, reverse=True):
        if term in lower and term not in seen_terms:
            explanation, importance = _TERMS[term]
            found.append({"term": term, "explanation": explanation, "importance": importance})
            seen_terms.add(term)
            for word in term.split():
                seen_terms.add(word)
    return found


def _pick_questions(terms: List[Dict], transcript: str) -> List[str]:
    """Pick 3 contextually relevant questions."""
    lower = transcript.lower()
    questions = []

    # Context-specific questions
    if any(t in lower for t in ["medication", "drug", "prescription", "mg", "dose"]):
        questions.append("What are the possible side effects of this medication?")
    if any(t in lower for t in ["diet", "food", "eat", "sodium", "weight"]):
        questions.append("Should I make any changes to my diet?")
    if any(t in lower for t in ["exercise", "activity", "walk", "sport"]):
        questions.append("Are there any activities I should avoid?")
    if any(t in lower for t in ["follow", "return", "appointment", "check"]):
        questions.append("When should I schedule my next appointment?")
    if any(t in lower for t in ["family", "hereditary", "genetic", "inherit"]):
        questions.append("Should my family members be tested for this condition?")
    if any(t in lower for t in ["chronic", "long", "permanent", "always"]):
        questions.append("What happens if this condition is left untreated?")

    # Fill up to 3 with generic questions based on found terms
    if terms and len(questions) < 3:
        questions.append(f"Can you explain more about {terms[0]['term']} in simple terms?")
    if len(questions) < 3:
        questions.append("What are the warning signs I should watch out for?")
    if len(questions) < 3:
        questions.append("Are there lifestyle changes that could help my condition?")

    return questions[:3]


class MockProvider(BaseAIService):
    """Smart demo provider — no API key needed, covers real medical vocabulary."""

    _provider_name = "Mock"

    def __init__(self):
        logger.warning(
            "MockProvider active — Gemini quota exhausted and no valid Groq key. "
            "Add a valid GROQ_API_KEY to .env for real AI responses."
        )
        _write_debug(
            "WARN", "Mock", "init",
            "MockProvider active. Gemini quota exhausted. "
            "Add GROQ_API_KEY from https://console.groq.com/keys for real AI."
        )

    async def get_insights(self, transcript: str) -> Dict:
        await asyncio.sleep(0.05)
        terms = _find_terms(transcript)
        questions = _pick_questions(terms, transcript) if terms else [
            "What does this mean for my daily life?",
            "Are there any side effects I should know about?",
            "When should I come back for a follow-up?",
        ]
        key_points = []
        if terms:
            key_points.append(f"{len(terms)} medical term(s) identified in this excerpt")
        key_points.append("Review the Terms Explained panel for plain-language definitions")

        return {
            "medical_terms":       terms,
            "suggested_questions": questions,
            "session_summary":     {"key_points": key_points},
        }

    async def generate_summary(self, full_transcript: str) -> Dict:
        await asyncio.sleep(0.1)
        terms = _find_terms(full_transcript)
        return {
            "title":        "Medical Consultation",
            "diagnosis":    "See transcript for full details",
            "medications":  [],
            "instructions": [
                "Follow your doctor's advice carefully",
                "Take all medications as prescribed",
                "Contact your doctor if symptoms worsen",
            ],
            "follow_up":    "Schedule a follow-up as recommended by your doctor",
            "key_points":   [
                f"{len(terms)} medical term(s) were discussed" if terms else "Session recorded",
                "Add a valid GROQ_API_KEY to .env for AI-generated summaries",
            ],
        }

    async def translate_text(self, text: str, target_language: str) -> str:
        await asyncio.sleep(0.05)
        return f"[{target_language.upper()}] {text}"

    async def explain_question(self, question: str, context: str = "") -> str:
        await asyncio.sleep(0.05)
        return (
            f"This is an important question to ask your doctor. "
            f"When you ask '{question}', listen carefully to understand "
            f"how the answer applies to your specific situation. "
            f"Don't hesitate to ask for clarification if anything is unclear."
        )

    async def simplify_terms(self, transcript: str) -> List[Dict[str, str]]:
        result = await self.get_insights(transcript)
        return result.get("medical_terms", [])

    async def suggest_questions(self, full_transcript: str) -> List[str]:
        result = await self.get_insights(full_transcript)
        return result.get("suggested_questions", [])
