# Contributing to Sidekick Medical Assistant

Thank you for contributing! This guide will help you get started.

## Team Structure

- **Backend Infrastructure Team**: Works in `backend/` folder
- **AI Integration Team**: Works in `ai-service/` folder
- **Frontend Team**: Works in `frontend/` folder

## Development Workflow

### 1. Pick a Task

Check your team's task file:
- Backend: `.kiro/specs/sidekick-medical-assistant/tasks-backend-infrastructure.md`
- AI: `.kiro/specs/sidekick-medical-assistant/tasks-ai-integration.md`
- Frontend: `.kiro/specs/sidekick-medical-assistant/tasks-frontend.md`

### 2. Create a Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/[team]-[task-name]

# Examples:
# git checkout -b feature/backend-database-setup
# git checkout -b feature/ai-gemini-integration
# git checkout -b feature/frontend-speech-recognition
```

### 3. Make Changes

Work in your team's folder:
```bash
# Backend Infrastructure
cd backend/
# Edit main.py, database.py, models.py

# AI Integration
cd ai-service/
# Edit gemini_service.py

# Frontend
cd frontend/
# Edit HTML, CSS, JS files
```

### 4. Test Locally

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
cd frontend
# Validate your changes
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat(team): description of changes"

# Commit message format:
# feat(backend): implement database service
# fix(ai): handle API timeout errors
# feat(frontend): add speech recognition
# docs: update README
```

### 6. Push and Create PR

```bash
git push origin feature/[team]-[task-name]
```

Then on GitHub:
1. Click "Create Pull Request"
2. Fill in the PR template
3. Request review from your team
4. Wait for CI checks to pass ✅

### 7. Code Review

- Minimum 1 approval from your team
- All CI checks must pass
- Resolve all comments
- Merge when approved

## Code Style

### Python (Backend & AI)
- Follow PEP 8
- Max line length: 100 characters
- Use type hints
- Add docstrings to functions

```python
async def create_session(self, language: str = "en") -> str:
    """
    Create a new session in the database
    
    Args:
        language: User's preferred language (default: "en")
        
    Returns:
        session_id: UUID of the created session
    """
    pass
```

### JavaScript (Frontend)
- Use ES6+ features
- Add JSDoc comments
- Use meaningful variable names

```javascript
/**
 * Update transcript panel with new text
 * 
 * @param {string} text - Transcript text
 * @param {boolean} isFinal - Whether this is a final result
 */
updateTranscript(text, isFinal) {
    // Implementation
}
```

## Testing

### Write Tests for:
- All new functions
- Bug fixes
- Integration points

### Test Structure:
```python
# backend/tests/test_database.py
import pytest

@pytest.mark.asyncio
async def test_create_session():
    """Test session creation"""
    db = DatabaseService(connection_string)
    session_id = await db.create_session("en")
    assert session_id is not None
```

## Integration Points

### Backend ↔ AI
Backend imports AI service:
```python
from ai_service.gemini_service import GeminiService
```

### Backend ↔ Frontend
Use `models.py` for message formats:
```python
# Backend sends
SimplificationMessage(
    type="simplification",
    terms=[{"term": "...", "explanation": "..."}]
)
```

### Coordinate Changes
If your change affects another team:
1. Discuss in PR comments
2. Tag the other team
3. Test integration together

## Common Issues

### Import Errors
```bash
# Add parent directory to path
import sys
sys.path.append('..')
```

### Test Failures
1. Check GitHub Actions logs
2. Run tests locally
3. Ask for help in PR comments

### Merge Conflicts
1. Pull latest develop
2. Resolve conflicts
3. Test again
4. Push

## Getting Help

- Check task files for detailed instructions
- Ask in PR comments
- Coordinate with other teams
- Review design.md and requirements.md

## Questions?

Contact your team lead or open a GitHub Discussion.
