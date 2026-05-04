# Sidekick - AI Medical Appointment Assistant

A real-time AI-powered web application that assists patients during medical appointments by simplifying medical terminology, suggesting clarification questions, and generating visit summaries.

## Team Structure

This project is developed by a team of 3:

### Team 1: Backend Infrastructure
- **Folder**: `backend/`
- **Files**: main.py, database.py, models.py, requirements.txt
- **Responsibilities**: Database, WebSocket, REST API, server setup

### Team 2: AI Integration  
- **Folder**: `ai-service/`
- **Files**: gemini_service.py, requirements.txt
- **Responsibilities**: Gemini API, medical term simplification, question generation, translation

### Team 3: Frontend
- **Folder**: `frontend/`
- **Files**: HTML, CSS, JavaScript
- **Responsibilities**: UI, speech recognition, WebSocket client, user interface

## Project Structure

```
sidekick-medical-assistant/
├── backend/                 [Backend Infrastructure Team]
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── requirements.txt
│   └── tests/
│
├── ai-service/              [AI Integration Team]
│   ├── gemini_service.py
│   ├── requirements.txt
│   ├── __init__.py
│   └── tests/
│
├── frontend/                [Frontend Team]
│   ├── index.html
│   ├── history.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── app.js
│   │   ├── speech.js
│   │   ├── ui.js
│   │   └── history.js
│   └── tests/
│
├── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Modern web browser (Chrome or Edge for Web Speech API)
- Google Gemini API key
- Supabase account

### Backend Setup (Backend Infrastructure Team)

1. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

### AI Service Setup (AI Integration Team)

1. Install AI service dependencies:
```bash
cd ai-service
pip install -r requirements.txt
```

### Running the Application

From the project root:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

The backend will automatically import the AI service from `../ai-service/`.

### Frontend Setup (Frontend Team)

No build step required! Just open `http://localhost:8000` in your browser.

## Development Workflow

See the task files for detailed implementation steps:
- Backend Infrastructure: `.kiro/specs/sidekick-medical-assistant/tasks-backend-infrastructure.md`
- AI Integration: `.kiro/specs/sidekick-medical-assistant/tasks-ai-integration.md`
- Frontend: `.kiro/specs/sidekick-medical-assistant/tasks-frontend.md`

## CI/CD Status

![CI](https://github.com/YOUR-USERNAME/sidekick-medical-assistant/actions/workflows/ci.yml/badge.svg)

## Features

- 🎤 Real-time speech recognition
- 💡 Medical terminology simplification
- ❓ Intelligent question suggestions
- 🌐 Multi-language translation
- 📋 Structured visit summaries
- 📚 Session history management

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript, Web Speech API
- **Backend**: Python, FastAPI, WebSocket
- **AI**: Google Gemini API
- **Database**: Supabase PostgreSQL

- # 🚀 Live Deployment
Frontend:  https://sidekick-frontend.onrender.com
Backend API: https://sidekick-backend-a3ec.onrender.com
## 📖 Project Overview
Brief description of what the project does, its features, and tech stack.

## 🛠️ Tech Stack
- FastAPI (Backend)
- React + Vite (Frontend)
- Render (Deployment)
- Sqlite (Database)

## ⚙️ Setup Instructions
Steps to run locally, install dependencies, and configure environment variables.

## License

MIT
