# Quick Start Guide
## Sidekick Medical Assistant Backend

Get up and running in 5 minutes!

---

## 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

## 2. Configure Environment

Make sure `.env` file exists with:
```
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite+aiosqlite:///sidekick.db
```

---

## 3. Start the Server

```bash
python start_server.py
```

Server will start at: `http://127.0.0.1:8000`

---

## 4. Test the Server

### Option A: Quick Health Check
```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Sidekick Medical Assistant",
  "version": "1.0.0"
}
```

### Option B: Run E2E Test
```bash
# In a new terminal (server must be running)
python test_e2e_integration.py
```

### Option C: Run All Tests
```bash
# Automated tests (no server required)
python run_all_tests.py

# API tests (server must be running)
python -m pytest backend/tests/test_api_endpoints.py -v
```

---

## 5. Access API Documentation

Open in browser:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## 6. Test WebSocket Connection

Use the E2E test or connect with a WebSocket client:

```javascript
// JavaScript example
const ws = new WebSocket('ws://127.0.0.1:8000/ws/session');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

// Send transcript
ws.send(JSON.stringify({
  type: 'transcript',
  text: 'The doctor mentioned hypertension.',
  language: 'en'
}));
```

---

## Common Commands

### Start Server
```bash
python start_server.py
```

### Run All Tests
```bash
python run_all_tests.py
```

### Run E2E Test
```bash
python test_e2e_integration.py
```

### Check Database
```bash
python test_database_sqlite.py
```

### Verify API Key
```bash
python test_gemini_api.py
```

---

## Troubleshooting

### Server won't start
- Check `.env` file exists
- Check port 8000 is not in use
- Check DATABASE_URL is valid

### Tests fail
- Make sure server is running (for API tests)
- Check `.env` file is configured
- Check database file is writable

### WebSocket connection fails
- Make sure server is running
- Check firewall settings
- Try http://127.0.0.1:8000 instead of localhost

---

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database_sqlite.py   # Database service
│   ├── models.py            # Data models
│   ├── performance.py       # Performance monitoring
│   ├── security.py          # Security utilities
│   └── tests/               # Test files
├── ai-service/
│   └── gemini_service_mock.py  # Mock AI service
├── frontend/
│   └── index.html           # Frontend files
├── start_server.py          # Server startup
├── test_e2e_integration.py  # E2E test
└── .env                     # Configuration
```

---

## API Endpoints

### REST API
- `GET /` - Serve frontend
- `GET /health` - Health check
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session details
- `DELETE /api/sessions/{id}` - Delete session

### WebSocket
- `ws://localhost:8000/ws/session` - Real-time communication

---

## Next Steps

1. ✅ Server running
2. ✅ Tests passing
3. → Integrate with frontend
4. → Replace mock AI service with real one
5. → Deploy to production

---

## Need Help?

Check these files:
- `BACKEND_IMPLEMENTATION_SUMMARY.md` - Complete implementation details
- `TESTING_GUIDE.md` - Comprehensive testing guide
- `SESSION_SUMMARY.md` - Latest session summary
- `backend/README.md` - Backend documentation

---

**You're all set! 🚀**
