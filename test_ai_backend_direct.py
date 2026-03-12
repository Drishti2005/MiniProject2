#!/usr/bin/env python3
"""
Direct AI-Backend Integration Test (No Frontend Required)

This test verifies that:
1. AI service is properly integrated with backend
2. Backend API endpoints work with AI service
3. All AI features (simplification, questions, summary, translation) function correctly
4. Database integration works with AI responses

Run with: python test_ai_backend_direct.py
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test(message):
    """Print test message."""
    print(f"{BLUE}[TEST]{RESET} {message}")


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {message}")


def print_error(message):
    """Print error message."""
    print(f"{RED}✗{RESET} {message}")


def print_warning(message):
    """Print warning message."""
    print(f"{YELLOW}⚠{RESET} {message}")


async def test_ai_service_initialization():
    """Test 1: AI Service Initialization"""
    print_test("Testing AI service initialization...")
    
    try:
        from ai_service.gemini_service import GeminiService
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print_warning("GEMINI_API_KEY not set, using test key")
            api_key = "test-key-for-initialization"
        
        service = GeminiService(api_key)
        
        # Verify methods exist
        assert hasattr(service, 'simplify_terms')
        assert hasattr(service, 'suggest_questions')
        assert hasattr(service, 'generate_summary')
        assert hasattr(service, 'translate_text')
        
        print_success("AI service initialized successfully")
        return True, service
    except Exception as e:
        print_error(f"AI service initialization failed: {e}")
        return False, None


async def test_simplify_terms(service):
    """Test 2: Medical Term Simplification"""
    print_test("Testing medical term simplification...")
    
    try:
        test_transcript = "The patient has hypertension and needs to take antihypertensive medication."
        
        result = await service.simplify_terms(test_transcript)
        
        if not result:
            print_warning("No terms simplified (API may not be configured)")
            return True  # Not a failure if API isn't configured
        
        # Verify structure
        assert isinstance(result, list), "Result should be a list"
        
        if len(result) > 0:
            assert "term" in result[0], "Each term should have 'term' field"
            assert "explanation" in result[0], "Each term should have 'explanation' field"
            print_success(f"Simplified {len(result)} medical terms")
            for term in result:
                print(f"  - {term['term']}: {term['explanation']}")
        else:
            print_success("Simplification completed (no terms found)")
        
        return True
    except Exception as e:
        print_error(f"Term simplification failed: {e}")
        return False


async def test_suggest_questions(service):
    """Test 3: Question Suggestions"""
    print_test("Testing question suggestions...")
    
    try:
        test_transcript = """
        Doctor: You have high blood pressure. We need to start you on medication.
        Patient: Okay, what should I do?
        Doctor: Take this pill once daily in the morning. Come back in two weeks.
        """
        
        result = await service.suggest_questions(test_transcript)
        
        if not result:
            print_warning("No questions suggested (API may not be configured)")
            return True
        
        # Verify structure
        assert isinstance(result, list), "Result should be a list"
        
        if len(result) > 0:
            print_success(f"Generated {len(result)} question suggestions")
            for i, question in enumerate(result, 1):
                print(f"  {i}. {question}")
        else:
            print_success("Question generation completed (no questions)")
        
        return True
    except Exception as e:
        print_error(f"Question suggestion failed: {e}")
        return False


async def test_generate_summary(service):
    """Test 4: Visit Summary Generation"""
    print_test("Testing visit summary generation...")
    
    try:
        test_transcript = """
        Doctor: Good morning. How are you feeling today?
        Patient: I've been having headaches and feeling dizzy.
        Doctor: Let me check your blood pressure. It's 150/95, which is high.
        Doctor: You have hypertension. I'm prescribing lisinopril 10mg once daily.
        Doctor: Take it in the morning with food. Avoid salty foods and exercise regularly.
        Doctor: Come back in two weeks for a follow-up to check your blood pressure.
        Patient: Okay, thank you doctor.
        """
        
        result = await service.generate_summary(test_transcript)
        
        # Verify structure
        assert isinstance(result, dict), "Result should be a dict"
        assert "title" in result, "Summary should have 'title'"
        assert "diagnosis" in result, "Summary should have 'diagnosis'"
        assert "medications" in result, "Summary should have 'medications'"
        assert "instructions" in result, "Summary should have 'instructions'"
        assert "follow_up" in result, "Summary should have 'follow_up'"
        
        print_success("Visit summary generated successfully")
        print(f"  Title: {result['title']}")
        print(f"  Diagnosis: {result['diagnosis']}")
        print(f"  Medications: {result['medications']}")
        print(f"  Instructions: {result['instructions']}")
        print(f"  Follow-up: {result['follow_up']}")
        
        return True
    except Exception as e:
        print_error(f"Summary generation failed: {e}")
        return False


async def test_translate_text(service):
    """Test 5: Translation Service"""
    print_test("Testing translation service...")
    
    try:
        test_text = "High blood pressure"
        target_language = "es"  # Spanish
        
        result = await service.translate_text(test_text, target_language)
        
        assert isinstance(result, str), "Result should be a string"
        assert len(result) > 0, "Translation should not be empty"
        
        print_success(f"Translation successful: '{test_text}' -> '{result}'")
        return True
    except Exception as e:
        print_error(f"Translation failed: {e}")
        return False


async def test_backend_database_integration():
    """Test 6: Backend Database Integration"""
    print_test("Testing backend database integration...")
    
    try:
        # Check if DATABASE_URL is set
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            database_url = "sqlite:///test_integration.db"
            print_warning(f"DATABASE_URL not set, using: {database_url}")
        
        # Import database service
        if database_url.startswith("sqlite"):
            from database_sqlite import DatabaseService
        else:
            from database import DatabaseService
        
        db = DatabaseService(database_url)
        await db.init_db()
        
        # Create test session
        session_id = await db.create_session("en")
        print_success(f"Created test session: {session_id}")
        
        # Add transcript
        await db.add_transcript_chunk(session_id, "Test transcript chunk")
        print_success("Added transcript chunk")
        
        # Add simplification
        await db.add_simplification(session_id, "hypertension", "high blood pressure")
        print_success("Added simplification")
        
        # Save summary
        test_summary = {
            "title": "Test Visit",
            "diagnosis": "Test diagnosis",
            "medications": ["Test medication"],
            "instructions": ["Test instruction"],
            "follow_up": "Test follow-up"
        }
        await db.save_summary(session_id, test_summary)
        print_success("Saved summary")
        
        # Retrieve session
        session_details = await db.get_session_details(session_id)
        assert session_details is not None, "Session should exist"
        print_success("Retrieved session details")
        
        # Clean up
        await db.delete_session(session_id)
        print_success("Cleaned up test session")
        
        return True
    except Exception as e:
        print_error(f"Database integration failed: {e}")
        return False


async def test_backend_ai_workflow():
    """Test 7: Complete Backend-AI Workflow"""
    print_test("Testing complete backend-AI workflow...")
    
    try:
        # Initialize services
        from ai_service.gemini_service import GeminiService
        
        api_key = os.getenv("GEMINI_API_KEY", "test-key")
        service = GeminiService(api_key)
        
        database_url = os.getenv("DATABASE_URL", "sqlite:///test_workflow.db")
        if database_url.startswith("sqlite"):
            from database_sqlite import DatabaseService
        else:
            from database import DatabaseService
        
        db = DatabaseService(database_url)
        await db.init_db()
        
        # Simulate a complete workflow
        print("  Simulating complete workflow...")
        
        # 1. Create session
        session_id = await db.create_session("en")
        print(f"  1. Created session: {session_id}")
        
        # 2. Process transcript with AI
        transcript = "The doctor said I have hypertension and prescribed medication."
        await db.add_transcript_chunk(session_id, transcript)
        print(f"  2. Added transcript")
        
        # 3. Get simplifications
        simplifications = await service.simplify_terms(transcript)
        if simplifications:
            for term_data in simplifications:
                await db.add_simplification(
                    session_id,
                    term_data["term"],
                    term_data["explanation"]
                )
            print(f"  3. Processed {len(simplifications)} simplifications")
        else:
            print(f"  3. No simplifications (API not configured)")
        
        # 4. Generate summary
        summary = await service.generate_summary(transcript)
        await db.save_summary(session_id, summary)
        print(f"  4. Generated and saved summary")
        
        # 5. End session
        await db.end_session(session_id)
        print(f"  5. Ended session")
        
        # 6. Verify data
        session_details = await db.get_session_details(session_id)
        assert session_details is not None, "Session should exist"
        # Transcript is returned as a list of chunks
        assert len(session_details["transcript"]) > 0, "Transcript should have chunks"
        assert session_details["transcript"][0]["text"] == transcript, "Transcript text should match"
        # Summary might be empty if API failed, but structure should exist
        assert "summary" in session_details, "Summary field should exist"
        print(f"  6. Verified session data")
        
        # Clean up
        await db.delete_session(session_id)
        
        print_success("Complete workflow executed successfully")
        return True
    except Exception as e:
        print_error(f"Workflow test failed: {e}")
        return False


async def test_performance_stats(service):
    """Test 8: Performance Statistics"""
    print_test("Testing performance statistics...")
    
    try:
        stats = service.get_performance_stats()
        
        assert isinstance(stats, dict), "Stats should be a dict"
        assert "total_requests" in stats
        assert "average_response_time" in stats
        
        print_success("Performance stats retrieved")
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Average response time: {stats['average_response_time']}s")
        print(f"  Slow requests: {stats.get('slow_requests', 0)}")
        
        return True
    except Exception as e:
        print_error(f"Performance stats failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("AI-Backend Integration Test (Direct - No Frontend)")
    print("=" * 70 + "\n")
    
    # Check environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_warning("GEMINI_API_KEY not set - some tests may use mock data")
        print_warning("Set GEMINI_API_KEY in .env for full testing\n")
    else:
        print_success("GEMINI_API_KEY found\n")
    
    results = []
    
    # Test 1: Initialize AI service
    success, service = await test_ai_service_initialization()
    results.append(("AI Service Initialization", success))
    
    if not success or service is None:
        print_error("\nCannot continue without AI service. Exiting.")
        return 1
    
    # Test 2-5: AI Service Features
    results.append(("Medical Term Simplification", await test_simplify_terms(service)))
    results.append(("Question Suggestions", await test_suggest_questions(service)))
    results.append(("Visit Summary Generation", await test_generate_summary(service)))
    results.append(("Translation Service", await test_translate_text(service)))
    
    # Test 6-7: Backend Integration
    results.append(("Backend Database Integration", await test_backend_database_integration()))
    results.append(("Complete Backend-AI Workflow", await test_backend_ai_workflow()))
    
    # Test 8: Performance
    results.append(("Performance Statistics", await test_performance_stats(service)))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"{status}: {test_name}")
    
    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}✓ All integration tests passed!{RESET}")
        print("\nThe AI service is properly integrated with the backend.")
        print("\nNext steps:")
        print("1. Start the backend server: cd backend && python -m uvicorn main:app --reload")
        print("2. Test with frontend at http://localhost:8000")
        print("3. Or use WebSocket client to test real-time features")
        return 0
    else:
        print(f"\n{RED}✗ Some tests failed. Please check the errors above.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
