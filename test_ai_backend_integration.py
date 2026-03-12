#!/usr/bin/env python3
"""
Test script to verify AI service and backend integration.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        from ai_service.gemini_service import GeminiService
        print("✓ GeminiService import successful")
    except ImportError as e:
        print(f"✗ Failed to import GeminiService: {e}")
        return False
    
    try:
        from ai_service.config import GEMINI_MODEL, SUPPORTED_LANGUAGES
        print(f"✓ Config import successful (Model: {GEMINI_MODEL})")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    try:
        from ai_service.prompts import SIMPLIFICATION_PROMPT
        print("✓ Prompts import successful")
    except ImportError as e:
        print(f"✗ Failed to import prompts: {e}")
        return False
    
    return True


def test_service_initialization():
    """Test that GeminiService can be initialized."""
    print("\nTesting service initialization...")
    
    try:
        from ai_service.gemini_service import GeminiService
        
        # Test with mock API key
        service = GeminiService(api_key="test-api-key-for-testing-only")
        print("✓ GeminiService initialized successfully")
        
        # Check methods exist
        assert hasattr(service, 'simplify_terms'), "Missing simplify_terms method"
        assert hasattr(service, 'suggest_questions'), "Missing suggest_questions method"
        assert hasattr(service, 'generate_summary'), "Missing generate_summary method"
        assert hasattr(service, 'translate_text'), "Missing translate_text method"
        print("✓ All required methods present")
        
        return True
    except Exception as e:
        print(f"✗ Service initialization failed: {e}")
        return False


def test_backend_integration():
    """Test that backend can import and use AI service."""
    print("\nTesting backend integration...")
    
    try:
        # Simulate backend import pattern
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        
        # This is how backend/main.py imports the service
        from ai_service.gemini_service import GeminiService
        
        print("✓ Backend can import AI service")
        
        # Test initialization with environment variable
        api_key = os.getenv("GEMINI_API_KEY", "test-key")
        service = GeminiService(api_key)
        print("✓ Backend can initialize AI service")
        
        return True
    except Exception as e:
        print(f"✗ Backend integration failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("AI Service and Backend Integration Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Import Test", test_imports()))
    results.append(("Service Initialization", test_service_initialization()))
    results.append(("Backend Integration", test_backend_integration()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All integration tests passed!")
        print("\nNext steps:")
        print("1. Set GEMINI_API_KEY in .env file")
        print("2. Run: cd backend && python -m uvicorn main:app --reload")
        print("3. Test with frontend at http://localhost:8000")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
