# AI Service Integration Strategy
## How Backend and AI Services Work Together

**Date:** March 9, 2026  
**Status:** ✅ Conflict-Free Design

---

## The Problem You Identified

You're right to be concerned! If both teams create files with the same name, there will be merge conflicts.

---

## The Solution

We use **different filenames** and **smart imports**:

```
ai-service/
├── gemini_service.py          ← AI Team creates this (REAL service)
├── gemini_service_mock.py     ← Backend created this (MOCK service)
└── README.md                  ← Integration guide
```

**No file conflicts!** ✅

---

## How It Works

### Scenario 1: Before AI Team Pushes (Current State)

```
Repository:
├── ai-service/
│   ├── gemini_service_mock.py  ✅ EXISTS
│   └── gemini_service.py       ❌ DOESN'T EXIST

Backend tries to import:
1. Try: from ai_service.gemini_service import GeminiService
   → FAILS (file doesn't exist)
2. Fallback: from ai_service.gemini_service_mock import GeminiService
   → SUCCESS! Uses mock service

Result: Backend uses MOCK service ✅
```

### Scenario 2: After AI Team Pushes

```
Repository:
├── ai-service/
│   ├── gemini_service_mock.py  ✅ EXISTS (mock)
│   └── gemini_service.py       ✅ EXISTS (real)

Backend tries to import:
1. Try: from ai_service.gemini_service import GeminiService
   → SUCCESS! Uses real service
2. Fallback: (never reached)

Result: Backend uses REAL service ✅
```

### Scenario 3: When You Pull from Main

```bash
# You pull AI team's changes
git pull origin main

# What happens:
# - AI team added: ai-service/gemini_service.py (NEW FILE)
# - You have: ai-service/gemini_service_mock.py (DIFFERENT FILE)
# - No conflict! Both files coexist

# Backend automatically switches:
# - Before pull: Used mock service
# - After pull: Uses real service
# - No code changes needed!
```

---

## Import Logic in backend/main.py

```python
# Smart import - tries real service first
try:
    # Try to import REAL service (from AI team)
    from ai_service.gemini_service import GeminiService
    logger.info("Using REAL Gemini AI service")
except ImportError:
    # REAL service doesn't exist yet, use MOCK
    from ai_service.gemini_service_mock import GeminiService
    logger.info("Using MOCK Gemini AI service (for testing)")
```

---

## Timeline

### Week 1 (Now - Backend Team)
```
✅ Backend complete
✅ Mock service created
✅ Tests passing with mock
✅ Push to main
```

### Week 2 (AI Team)
```
⏭️ AI team creates gemini_service.py
⏭️ AI team tests their service
⏭️ AI team pushes to main
```

### Week 3 (Integration)
```
⏭️ Backend team pulls from main
⏭️ Backend automatically uses real service
⏭️ Run integration tests
⏭️ Everything works!
```

---

## What Gets Committed

### Your Commit (Backend Team)
```
✅ ai-service/gemini_service_mock.py
✅ ai-service/README.md (integration guide)
✅ backend/main.py (with smart import)
```

### AI Team's Commit
```
✅ ai-service/gemini_service.py (real service)
✅ ai-service/tests/ (their tests)
```

### No Conflicts Because:
- Different filenames ✅
- Different directories for tests ✅
- Backend code already handles both ✅

---

## Merge Scenarios

### Scenario A: You Pull First
```bash
git pull origin main

# If AI team hasn't pushed yet:
# - Nothing new
# - Still uses mock
# - No conflicts

# If AI team has pushed:
# - Gets gemini_service.py
# - Automatically switches to real service
# - No conflicts
```

### Scenario B: AI Team Pulls First
```bash
# AI team pulls your changes
git pull origin main

# They get:
# - gemini_service_mock.py (doesn't affect them)
# - backend/main.py (already handles their service)
# - No conflicts

# They add:
# - gemini_service.py (new file)
# - Push to main
```

### Scenario C: Simultaneous Development
```bash
# Both teams working at same time

# Backend team commits:
# - gemini_service_mock.py
# - backend/main.py

# AI team commits:
# - gemini_service.py

# When merged:
# - Both files exist
# - No conflicts (different files)
# - Backend uses real service
```

---

## Testing Strategy

### Backend Tests (Your Tests)
```bash
# These work with BOTH mock and real service
python test_e2e_integration.py
python -m pytest backend/tests/
```

### AI Tests (Their Tests)
```bash
# They create their own tests
python -m pytest ai-service/tests/
```

### Integration Tests (Together)
```bash
# Run after both services are ready
python test_e2e_integration.py  # Uses real service
```

---

## Interface Contract

Both services implement the same interface:

```python
class GeminiService:
    def __init__(self, api_key: str)
    async def simplify_terms(self, transcript: str) -> Dict
    async def suggest_questions(self, full_transcript: str) -> Dict
    async def generate_summary(self, full_transcript: str) -> Dict
    async def translate_text(self, text: str, target_language: str) -> str
```

As long as both implement this, everything works! ✅

---

## Benefits of This Approach

1. **No Merge Conflicts** - Different filenames
2. **Independent Development** - Teams work separately
3. **Automatic Switching** - Backend detects real service
4. **Testing Flexibility** - Can test with or without real service
5. **Backward Compatible** - Mock stays for testing
6. **No Code Changes** - Backend code doesn't need updates

---

## What If There's a Conflict?

**Unlikely, but if it happens:**

```bash
# If somehow there's a conflict in backend/main.py
git pull origin main

# Git will show:
<<<<<<< HEAD
# Your version
=======
# Their version
>>>>>>> main

# Resolution: Keep the smart import logic
# (It handles both services)
```

**But this won't happen because:**
- You're only modifying backend files
- AI team only modifies ai-service files
- Different directories = no conflicts

---

## Verification Checklist

Before committing, verify:

- [x] Mock service is `gemini_service_mock.py` (not `gemini_service.py`)
- [x] Backend imports try real service first
- [x] Backend falls back to mock service
- [x] README.md explains integration to AI team
- [x] No hardcoded imports (uses try/except)
- [x] Tests work with mock service

---

## Summary

**Your Concern:** "Won't the mock conflict with the real AI service?"

**Answer:** No! Because:
1. Different filenames (`gemini_service.py` vs `gemini_service_mock.py`)
2. Smart import logic (tries real first, falls back to mock)
3. Both can coexist in the repository
4. Backend automatically uses whichever is available

**Result:** ✅ Zero conflicts, smooth integration!

---

## Next Steps

1. ✅ Commit your backend code (including mock)
2. ⏭️ AI team creates their real service
3. ⏭️ You pull their changes
4. ✅ Backend automatically switches to real service
5. ✅ Everything works!

---

**This design is conflict-free and production-ready!** 🚀
