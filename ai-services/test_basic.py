#!/usr/bin/env python3
"""Basic functionality tests to verify the implementation works."""

from gemini_service import GeminiService
import json

def test_initialization():
    """Test service initialization."""
    print("\n=== Testing Initialization ===")
    
    # Test 1: Valid API key
    try:
        service = GeminiService(api_key='test_api_key_12345')
        print("✓ Test 1 PASSED: Service initialization with valid API key")
    except Exception as e:
        print(f"✗ Test 1 FAILED: {e}")
        return False
    
    # Test 2: Empty API key should fail
    try:
        service = GeminiService(api_key='')
        print("✗ Test 2 FAILED: Should have raised ValueError for empty API key")
        return False
    except ValueError:
        print("✓ Test 2 PASSED: Correctly rejects empty API key")
    
    # Test 3: Short API key should fail
    try:
        service = GeminiService(api_key='short')
        print("✗ Test 3 FAILED: Should have raised ValueError for invalid API key")
        return False
    except ValueError:
        print("✓ Test 3 PASSED: Correctly rejects invalid API key format")
    
    return True

def test_rate_limiter():
    """Test rate limiter initialization."""
    print("\n=== Testing Rate Limiter ===")
    
    try:
        service = GeminiService(api_key='test_api_key_12345')
        assert service.rate_limiter is not None
        assert service.rate_limiter.max_requests == 15
        print("✓ Test 4 PASSED: Rate limiter properly initialized")
        return True
    except Exception as e:
        print(f"✗ Test 4 FAILED: {e}")
        return False

def test_performance_stats():
    """Test performance statistics."""
    print("\n=== Testing Performance Stats ===")
    
    try:
        service = GeminiService(api_key='test_api_key_12345')
        stats = service.get_performance_stats()
        assert stats['total_requests'] == 0
        assert stats['average_response_time'] == 0
        assert stats['slow_requests'] == 0
        print("✓ Test 5 PASSED: Performance stats initialized correctly")
        return True
    except Exception as e:
        print(f"✗ Test 5 FAILED: {e}")
        return False

def test_sanitization():
    """Test prompt sanitization."""
    print("\n=== Testing Prompt Sanitization ===")
    
    service = GeminiService(api_key='test_api_key_12345')
    
    test_cases = [
        ('Patient SSN is 123-45-6789', True, 'SSN'),
        ('Email: patient@example.com', True, 'email'),
        ('Phone: 1234567890', True, 'phone'),
        ('Normal text without PII', False, 'none')
    ]
    
    all_passed = True
    for text, should_redact, pii_type in test_cases:
        sanitized = service._sanitize_prompt(text)
        has_redacted = '[REDACTED]' in sanitized
        
        if should_redact and has_redacted:
            print(f"✓ Test 6 PASSED: {pii_type} sanitized")
        elif not should_redact and not has_redacted:
            print(f"✓ Test 6 PASSED: {pii_type} unchanged")
        else:
            print(f"✗ Test 6 FAILED: {pii_type} sanitization incorrect")
            all_passed = False
    
    return all_passed

def test_json_parsing():
    """Test JSON response parsing."""
    print("\n=== Testing JSON Parsing ===")
    
    service = GeminiService(api_key='test_api_key_12345')
    all_passed = True
    
    # Test valid JSON
    valid_json = '{"terms": [{"term": "test", "explanation": "test"}]}'
    try:
        result = service._parse_json_response(valid_json, 'test')
        assert 'terms' in result
        print("✓ Test 7.1 PASSED: Valid JSON parsed correctly")
    except Exception as e:
        print(f"✗ Test 7.1 FAILED: {e}")
        all_passed = False
    
    # Test markdown-wrapped JSON
    markdown_json = '```json\n{"terms": []}\n```'
    try:
        result = service._parse_json_response(markdown_json, 'test')
        assert 'terms' in result
        print("✓ Test 7.2 PASSED: Markdown-wrapped JSON parsed correctly")
    except Exception as e:
        print(f"✗ Test 7.2 FAILED: {e}")
        all_passed = False
    
    # Test invalid JSON
    try:
        result = service._parse_json_response('not json', 'test')
        print("✗ Test 7.3 FAILED: Should have raised ValueError for invalid JSON")
        all_passed = False
    except ValueError:
        print("✓ Test 7.3 PASSED: Invalid JSON correctly rejected")
    
    return all_passed

def test_empty_summary():
    """Test empty summary structure."""
    print("\n=== Testing Empty Summary ===")
    
    service = GeminiService(api_key='test_api_key_12345')
    
    try:
        summary = service._empty_summary()
        required_fields = ['title', 'diagnosis', 'medications', 'instructions', 'follow_up', 'key_points']
        
        for field in required_fields:
            assert field in summary, f"Missing field: {field}"
        
        assert isinstance(summary['medications'], list)
        assert isinstance(summary['instructions'], list)
        assert isinstance(summary['key_points'], list)
        
        print("✓ Test 8 PASSED: Empty summary has all required fields")
        return True
    except Exception as e:
        print(f"✗ Test 8 FAILED: {e}")
        return False

def main():
    """Run all basic tests."""
    print("=" * 70)
    print("BASIC FUNCTIONALITY TESTS")
    print("=" * 70)
    
    results = []
    
    results.append(("Initialization", test_initialization()))
    results.append(("Rate Limiter", test_rate_limiter()))
    results.append(("Performance Stats", test_performance_stats()))
    results.append(("Sanitization", test_sanitization()))
    results.append(("JSON Parsing", test_json_parsing()))
    results.append(("Empty Summary", test_empty_summary()))
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:20s} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All basic functionality tests PASSED!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) FAILED")
        return 1

if __name__ == "__main__":
    exit(main())
