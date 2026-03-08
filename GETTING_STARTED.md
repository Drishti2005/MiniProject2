# Getting Started - Sidekick Medical Assistant

Welcome to the Sidekick Medical Assistant project! This guide will help you get started quickly.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Team Structure](#team-structure)
3. [Prerequisites](#prerequisites)
4. [Initial Setup](#initial-setup)
5. [Your Team's Responsibilities](#your-teams-responsibilities)
6. [Daily Workflow](#daily-workflow)
7. [Important Files](#important-files)
8. [Integration & Coordination](#integration--coordination)
9. [Testing](#testing)
10. [GitHub Workflow](#github-workflow)
11. [Common Issues](#common-issues)
12. [Getting Help](#getting-help)

---

## 🎯 Project Overview

**Sidekick** is a real-time AI-powered medical appointment assistant that:
- 🎤 Transcribes doctor-patient conversations using Web Speech API
- 💡 Simplifies medical terminology in real-time
- ❓ Suggests clarification questions for patients
- 🌐 Translates explanations to patient's language
- 📋 Generates structured visit summaries
- 📚 Maintains session history

**Tech Stack:**
- Frontend: Vanilla HTML/CSS/JavaScript
- Backend: Python + FastAPI + WebSocket
- AI: Google Gemini API
- Database: Supabase PostgreSQL

---

## 👥 Team Structure

### Team 1: Backend Infrastructure
**Folder:** `backend/`
**Files:** main.py, database.py, models.py, requirements.txt
**Responsibilities:**
- Database operations (Supabase PostgreSQL)
- WebSocket communication
- REST API endpoints
- Server setup and configuration

### Team 2: AI Integration
**Folder:** `ai-service/`
**Files:** gemini_service.py, requirements.txt
**Responsibilities:**
- Google Gemini API integration
- Medical term simplification
- Question generation
- Translation services
- Visit summary generation

### Team 3: Frontend
**Folder:** `frontend/`
**Files:** HTML, CSS, JavaScript
**Responsibilities:**
- User interface design
- Web Speech API integration
- WebSocket client
- Real-time UI updates
- Session history page

---

## ✅ Prerequisites

### All Teams Need:
- Git installed
- GitHub account
- Code editor (VS Code recommended)
- Basic understanding of Git commands

### Backend Infrastructure Team:
- Python 3.9 or higher
- pip (Python package manager)
- Supabase account (free tier)

### AI Integration Team:
- Python 3.9 or higher
- pip (Python package manager)
- Google Gemini API key (free tier)

### Frontend Team:
- Modern web browser (Chrome or Edge for Web Speech API)
- Basic HTML/CSS/JavaScript knowledge

---

## 🚀 Initial Setup

### Step 1: Clone the Repository

```bash
# Clone the repo
git clone https://github.com/YOUR-ORG/sidekick-medical-assistant.git
cd sidekick-medical-assistant

# Create develop branch
git checkout -b develop
git push origin develop
```

### Step 2: Set Up Your Environment

#### Backend Infrastructure Team:
```bash
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example ../.env
# Edit .env and add your credentials
```

#### AI Integration Team:
```bash
# Navigate to ai-service folder
cd ai-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Get Gemini API key from: https://makersuite.google.com/app/apikey
# Add to .env file in project root
```

#### Frontend Team:
```bash
# Navigate to frontend folder
cd frontend

# No installation needed! Just open files in your editor
# Test by opening index.html in browser (will need backend running later)
```

### Step 3: Verify Setup

#### Backend Infrastructure:
```bash
cd backend
python -c "import fastapi; print('✅ FastAPI installed')"
python -c "import asyncpg; print('✅ asyncpg installed')"
```

#### AI Integration:
```bash
cd ai-service
python -c "import google.generativeai; print('✅ Gemini SDK installed')"
```

#### Frontend:
```bash
cd frontend
ls -la  # Should see index.html, history.html, css/, js/
```

---

## 📂 Your Team's Responsibilities

### Backend Infrastructure Team

**Your Folder:** `backend/`

**Your Task File:** `.kiro/specs/sidekick-medical-assistant/tasks-backend-infrastructure.md`

**Your Files:**
1. **main.py** - FastAPI application
   - WebSocket endpoint: `ws://localhost:8000/ws/session`
   - REST endpoints: GET /, GET /api/sessions, GET /api/sessions/{id}, DELETE /api/sessions/{id}
   - Imports AI service: `from ai_service.gemini_service import GeminiService`

2. **database.py** - Database service
   - Connection to Supabase PostgreSQL
   - Methods: create_session, end_session, add_transcript_chunk, add_simplification, save_summary, get_all_sessions, get_session_details, delete_session

3. **models.py** - Pydantic models (THE CONTRACT)
   - Defines message formats for WebSocket
   - Shared by all teams - DO NOT change without coordination

4. **requirements.txt** - Python dependencies

**Key Integration Points:**
- Import AI service from `ai-service/`
- Use models.py for all message formats
- Coordinate with Frontend on WebSocket messages

---

### AI Integration Team

**Your Folder:** `ai-service/`

**Your Task File:** `.kiro/specs/sidekick-medical-assistant/tasks-ai-integration.md`

**Your Files:**
1. **gemini_service.py** - Gemini API service
   - `simplify_terms(transcript)` - Identify and explain medical terms
   - `suggest_questions(full_transcript)` - Generate 2-3 questions
   - `generate_summary(full_transcript)` - Create structured summary
   - `translate_text(text, target_language)` - Translate to patient's language
   - Rate limiting: 15 requests per minute
   - Timeout: 10 seconds per request
   - Retry logic: 3 attempts with exponential backoff

2. **requirements.txt** - Python dependencies

3. **__init__.py** - Package initialization

**Key Integration Points:**
- Backend imports your service: `from ai_service.gemini_service import GeminiService`
- Return data in formats defined in backend/models.py
- Coordinate with Backend on method signatures

---

### Frontend Team

**Your Folder:** `frontend/`

**Your Task File:** `.kiro/specs/sidekick-medical-assistant/tasks-frontend.md`

**Your Files:**
1. **index.html** - Main application page
   - Three-panel layout: Transcript, Simplified Terms, Questions
   - Recording controls
   - Language selector
   - Translation panel

2. **history.html** - Session history page
   - List of past sessions
   - Session details view
   - Delete functionality

3. **css/style.css** - All styles
   - Medical-themed color scheme
   - Responsive layout (min-width 768px)
   - Animations and transitions

4. **js/speech.js** - Speech recognition
   - Web Speech API wrapper
   - Continuous recognition mode
   - Error handling with auto-restart

5. **js/app.js** - WebSocket client
   - Connection to `ws://localhost:8000/ws/session`
   - Message routing
   - Reconnection logic

6. **js/ui.js** - UI manager
   - Update transcript, terms, questions
   - Display translations and summaries
   - Recording state management

7. **js/history.js** - History page logic
   - Fetch sessions from API
   - Display session details
   - Delete sessions

**Key Integration Points:**
- WebSocket messages must match backend/models.py format
- Coordinate with Backend on message structure
- Test with Backend team for integration

---

## 🔄 Daily Workflow

### 1. Start Your Day

```bash
# Pull latest changes
git checkout develop
git pull origin develop

# Create your feature branch
git checkout -b feature/[team]-[task-name]

# Examples:
# Backend: git checkout -b feature/backend-database-setup
# AI: git checkout -b feature/ai-gemini-integration
# Frontend: git checkout -b feature/frontend-speech-recognition
```

### 2. Check Your Tasks

Open your team's task file:
- Backend: `.kiro/specs/sidekick-medical-assistant/tasks-backend-infrastructure.md`
- AI: `.kiro/specs/sidekick-medical-assistant/tasks-ai-integration.md`
- Frontend: `.kiro/specs/sidekick-medical-assistant/tasks-frontend.md`

Pick a task that's not started yet.

### 3. Work on Your Task

```bash
# Navigate to your folder
cd backend/    # or ai-service/ or frontend/

# Edit files
# Write code
# Add comments
```

### 4. Test Your Changes

**Backend:**
```bash
cd backend
pytest tests/
flake8 .
```

**AI Service:**
```bash
cd ai-service
pytest tests/
flake8 .
```

**Frontend:**
```bash
# Open index.html in browser
# Test functionality manually
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat(team): description"

# Commit message examples:
# feat(backend): implement database service
# fix(ai): handle API timeout errors
# feat(frontend): add speech recognition UI
# docs: update README
```

### 6. Push and Create PR

```bash
git push origin feature/[team]-[task-name]
```

Then on GitHub:
1. Click "Create Pull Request"
2. Target branch: `develop`
3. Fill in PR template
4. Request review from your team
5. Wait for CI checks ✅

### 7. Code Review & Merge

- Get 1 approval from your team
- Ensure all CI checks pass
- Resolve any comments
- Merge to `develop`

---

## 📄 Important Files

### For All Teams:

1. **README.md** - Project overview
2. **CONTRIBUTING.md** - Development guidelines
3. **GETTING_STARTED.md** - This file!
4. **.kiro/specs/sidekick-medical-assistant/**
   - `requirements.md` - All requirements
   - `design.md` - System design and architecture
   - `tasks.md` - Master task list
   - `tasks-[team].md` - Your team's tasks

### Backend Infrastructure:

1. **backend/models.py** - THE CONTRACT (coordinate changes!)
2. **backend/main.py** - FastAPI app
3. **backend/database.py** - Database service
4. **.env** - Environment variables (DO NOT commit!)

### AI Integration:

1. **ai-service/gemini_service.py** - Your main file
2. **ai-service/requirements.txt** - Dependencies
3. **.env** - API keys (DO NOT commit!)

### Frontend:

1. **frontend/index.html** - Main page
2. **frontend/js/app.js** - WebSocket client
3. **frontend/js/speech.js** - Speech recognition
4. **frontend/js/ui.js** - UI updates

---

## 🤝 Integration & Coordination

### Backend ↔ AI Integration

**How Backend calls AI:**
```python
# In backend/main.py
import sys
sys.path.append('..')
from ai_service.gemini_service import GeminiService

gemini = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))

# Call AI methods
simplifications = await gemini.simplify_terms(transcript)
questions = await gemini.suggest_questions(full_transcript)
```

**Coordination Points:**
- Method signatures in gemini_service.py
- Return data formats (must match models.py)
- Error handling

### Backend ↔ Frontend

**How Frontend connects:**
```javascript
// In frontend/js/app.js
const ws = new WebSocket('ws://localhost:8000/ws/session');

// Send message
ws.send(JSON.stringify({
    type: "transcript",
    text: "Your blood pressure is elevated",
    language: "en"
}));

// Receive message
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    // message.type: "simplification", "questions", "translation", "summary"
};
```

**Coordination Points:**
- WebSocket message formats (defined in backend/models.py)
- REST API endpoints
- Error messages

### AI ↔ Frontend

**No direct connection!** All communication goes through Backend.

Frontend → Backend → AI → Backend → Frontend

---

## 🧪 Testing

### Unit Tests

**Backend:**
```bash
cd backend
pytest tests/test_database.py -v
pytest tests/test_websocket.py -v
```

**AI Service:**
```bash
cd ai-service
pytest tests/test_gemini_service.py -v
```

### Integration Tests

```bash
# Run from project root
pytest tests/integration/ -v
```

### Manual Testing

**Full Flow Test:**
1. Start backend: `cd backend && uvicorn main:app --reload`
2. Open frontend: Open `http://localhost:8000` in browser
3. Click "Start Recording"
4. Speak: "The patient has hypertension"
5. Verify:
   - ✅ Transcript appears
   - ✅ Simplification shows: "hypertension → high blood pressure"
   - ✅ Questions appear
6. Click "Stop Recording"
7. Verify:
   - ✅ Summary modal appears

---

## 🔀 GitHub Workflow

### Branch Strategy

```
main (production)
  ↑
develop (integration)
  ↑
feature/backend-*
feature/ai-*
feature/frontend-*
```

### Creating a PR

1. **Push your branch**
```bash
git push origin feature/[team]-[task-name]
```

2. **On GitHub:**
   - Click "Compare & pull request"
   - Base: `develop`
   - Fill in template
   - Add reviewers

3. **Wait for CI:**
   - ✅ lint
   - ✅ backend-tests
   - ✅ ai-tests
   - ✅ frontend-tests
   - ✅ integration-tests

4. **Get approval and merge**

### CI/CD Pipeline

**Automatic checks on every PR:**
- Code linting (flake8)
- Unit tests (pytest)
- Integration tests
- Code coverage

**View results:**
- Go to PR → "Checks" tab
- Click on failed check to see logs
- Fix issues and push again

---

## ⚠️ Common Issues

### Issue 1: Import Errors (Backend/AI)

**Problem:**
```python
ModuleNotFoundError: No module named 'ai_service'
```

**Solution:**
```python
# Add to backend/main.py
import sys
sys.path.append('..')
from ai_service.gemini_service import GeminiService
```

### Issue 2: Environment Variables Not Found

**Problem:**
```
KeyError: 'GEMINI_API_KEY'
```

**Solution:**
```bash
# Create .env file in project root
cp .env.example .env
# Edit .env and add your keys
```

### Issue 3: Tests Failing Locally

**Problem:**
```
pytest: command not found
```

**Solution:**
```bash
pip install pytest pytest-asyncio
```

### Issue 4: WebSocket Connection Failed (Frontend)

**Problem:**
```
WebSocket connection to 'ws://localhost:8000/ws/session' failed
```

**Solution:**
```bash
# Make sure backend is running
cd backend
uvicorn main:app --reload --port 8000
```

### Issue 5: Merge Conflicts

**Problem:**
```
CONFLICT (content): Merge conflict in backend/models.py
```

**Solution:**
```bash
# Pull latest develop
git checkout develop
git pull origin develop

# Merge into your branch
git checkout feature/your-branch
git merge develop

# Resolve conflicts in editor
# Then:
git add .
git commit -m "fix: resolve merge conflicts"
git push
```

---

## 📞 Getting Help

### 1. Check Documentation
- Read your team's task file
- Review design.md and requirements.md
- Check CONTRIBUTING.md

### 2. Ask Your Team
- Comment on your PR
- Tag team members: @username
- Use GitHub Discussions

### 3. Coordinate with Other Teams
- Tag other team in PR: "Hey @ai-team, can you review this?"
- Schedule integration sync meetings
- Use checkpoints in task files

### 4. Common Resources
- **Gemini API Docs**: https://ai.google.dev/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Web Speech API**: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
- **Supabase Docs**: https://supabase.com/docs

---

## 🎯 Quick Reference

### Backend Infrastructure Commands
```bash
cd backend
pip install -r requirements.txt
pytest tests/
flake8 .
uvicorn main:app --reload --port 8000
```

### AI Integration Commands
```bash
cd ai-service
pip install -r requirements.txt
pytest tests/
flake8 .
```

### Frontend Commands
```bash
cd frontend
# Open index.html in browser
# Or use backend to serve: http://localhost:8000
```

### Git Commands
```bash
git checkout develop
git pull origin develop
git checkout -b feature/team-task
git add .
git commit -m "feat(team): description"
git push origin feature/team-task
```

---

## ✨ Success Checklist

Before you start coding:
- [ ] Repository cloned
- [ ] Virtual environment created (Backend/AI teams)
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Task file reviewed
- [ ] Feature branch created

Before creating a PR:
- [ ] Code tested locally
- [ ] Tests pass
- [ ] Code linted
- [ ] Commit messages follow format
- [ ] No merge conflicts

Before merging:
- [ ] PR template filled
- [ ] CI checks pass ✅
- [ ] Code reviewed and approved
- [ ] Integration points verified

---

## 🚀 Ready to Start!

1. **Read your team's task file**
2. **Pick your first task**
3. **Create a feature branch**
4. **Start coding!**

Welcome to the team! Let's build something amazing! 🎉

---

**Questions?** Open a GitHub Discussion or ask in your PR comments.

**Found a bug in this guide?** Create a PR to fix it!
