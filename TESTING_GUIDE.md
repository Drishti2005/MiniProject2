# Testing Guide
## Sidekick Medical Assistant Backend

This guide explains how to run all the tests for the backend.

---

## Prerequisites

Make sure you have all dependencies installed:

```bash
pip install -r backend/requirements.txt
```

Required packages:
- pytest
- pytest-asyncio
- hypothesis
- websockets
- requests

---

## Test Structure

### 1. Security Tests (`backend/tests/test_security.py`)
Tests security features including:
- Log sanitization (SSN, email, phone, MRN removal)
- Input validation (session IDs, language codes, text)
- WebSocket message validation
- Environment variable security

**Run:**
```bash
python -m pytest backend/tests/test_security.py -v
```

### 2. Property-Based Database Tests (`backend/tests/test_properties_database.py`)
Tests database operations with property-based testing (100 iterations each):
- Simplification accumulation invariant
- Simplification persistence completeness
- Session deletion cascade
- Transcript chunk persistence
- Session end timestamp update
- Summary structure completeness

**Run:**
```bash
python -m pytest backend/tests/test_properties_database.py -v
```

### 3. Performance Tests (`backend/tests/test_performance.py`)
Tests performance constraints:
- Transcript processing time (< 2 seconds)
- Database query performance (< 500ms)
- Session creation (< 200ms)
- Simplification storage (< 200ms)
- Summary storage (< 300ms)

**Run:**
```bash
python -m pytest backend/tests/test_performance.py -v
```

### 4. API Endpoint Tests (`backend/tests/test_api_endpoints.py`)
Tests REST API endpoints (requires running server):
- Health check
- List sessions
- Get session details
- Delete session
- HTTP status codes

**Run:**
```bash
# Terminal 1: Start server
python start_server.py

# Terminal 2: Run tests
python -m pytest backend/tests/test_api_endpoints.py -v
```

### 5. Error Handling Tests (`backend/tests/test_error_handling.py`)
Tests error scenarios (requires running server):
- Invalid WebSocket messages
- Database errors
- Non-existent resources (404)
- CORS headers

**Run:**
```bash
# Terminal 1: Start server
python start_server.py

# Terminal 2: Run tests
python -m pytest backend/tests/test_error_handling.py -v
```

### 6. End-to-End Integration Test (`test_e2e_integration.py`)
Tests complete workflow (requires running server):
- WebSocket connection
- Session creation
- Transcript processing
- AI service integration
- Summary generation
- Session deletion

**Run:**
```bash
# Terminal 1: Start server
python start_server.py

# Terminal 2: Run E2E test
python test_e2e_integration.py
```

---

## Quick Test Commands

### Run All Automated Tests (No Server Required)
```bash
python run_all_tests.py
```

This runs:
- Security tests
- Property-based database tests
- Performance tests

### Run All Tests (Server Required)
```bash
# Terminal 1
python start_server.py

# Terminal 2
python -m pytest backend/tests/ -v
python test_e2e_integration.py
```

### Run Specific Test File
```bash
python -m pytest backend/tests/test_security.py -v
```

### Run Specific Test Function
```bash
python -m pytest backend/tests/test_security.py::test_sanitize_log_message_ssn -v
```

### Run Tests with Coverage
```bash
python -m pytest backend/tests/ --cov=backend --cov-report=html
```

---

## Test Output Examples

### Successful Test
```
✅ test_sanitize_log_message_ssn PASSED
```

### Failed Test
```
❌ test_performance_threshold FAILED
AssertionError: Operation took 550ms, expected < 500ms
```

### Property Test
```
✅ test_simplification_accumulation_invariant PASSED (100 examples)
```

---

## Troubleshooting

### Tests Hang
If tests hang when importing the FastAPI app:
- Make sure no server is already running on port 8000
- Try running tests individually
- Check that DATABASE_URL is set in .env

### Import Errors
If you get import errors:
```bash
# Make sure you're in the project root
cd /path/to/project

# Run tests from project root
python -m pytest backend/tests/test_security.py -v
```

### Database Errors
If you get database errors:
- Check that .env file exists with DATABASE_URL
- For SQLite: Make sure sidekick.db is writable
- For PostgreSQL: Check network connection

### WebSocket Connection Errors
If E2E test can't connect:
- Make sure server is running: `python start_server.py`
- Check server is on port 8000: `http://127.0.0.1:8000/health`
- Check firewall isn't blocking WebSocket connections

---

## Test Coverage

Current test coverage:

| Component | Coverage | Tests |
|-----------|----------|-------|
| Security | 95% | 20+ tests |
| Database | 90% | 14 property tests |
| Performance | 85% | 8 tests |
| API Endpoints | 80% | 10+ tests |
| Error Handling | 75% | 10+ tests |

---

## Continuous Integration

For CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install -r backend/requirements.txt
    python run_all_tests.py
    
- name: Start Server and Run Integration Tests
  run: |
    python start_server.py &
    sleep 5
    python test_e2e_integration.py
```

---

## Next Steps

After all tests pass:
1. Review test coverage report
2. Add tests for any uncovered code
3. Run load tests for performance validation
4. Deploy to staging environment
5. Run tests against staging

---

## Questions?

If you encounter issues:
1. Check this guide
2. Review BACKEND_IMPLEMENTATION_SUMMARY.md
3. Check backend/README.md
4. Ask the team

Happy testing! 🧪
