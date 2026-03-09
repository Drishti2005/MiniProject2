#!/usr/bin/env python
"""
Comprehensive test runner for Sidekick Medical Assistant Backend
Runs all test suites: unit tests, property-based tests, performance tests, security tests
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*70}")
    print(f"🧪 {description}")
    print(f"{'='*70}")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        return True
    else:
        print(f"❌ {description} - FAILED")
        return False

def main():
    """Run all test suites"""
    print("\n" + "="*70)
    print("🚀 Sidekick Medical Assistant - Backend Test Suite")
    print("="*70)
    
    results = []
    
    # Check if pytest is installed
    try:
        import pytest
        import hypothesis
    except ImportError:
        print("\n❌ Required test libraries not installed")
        print("Install with: pip install pytest pytest-asyncio hypothesis")
        return 1
    
    # 1. Security Tests
    results.append(run_command(
        "python -m pytest backend/tests/test_security.py -v --tb=short",
        "Security Tests"
    ))
    
    # 2. Property-Based Database Tests
    results.append(run_command(
        "python -m pytest backend/tests/test_properties_database.py -v --tb=short",
        "Property-Based Database Tests"
    ))
    
    # 3. Performance Tests
    results.append(run_command(
        "python -m pytest backend/tests/test_performance.py -v --tb=short",
        "Performance Tests"
    ))
    
    # 4. API Endpoint Tests (requires running server)
    print("\n" + "="*70)
    print("⚠️  API Endpoint Tests require a running server")
    print("Start server with: python start_server.py")
    print("Then run: python -m pytest backend/tests/test_api_endpoints.py -v")
    print("="*70)
    
    # 5. Error Handling Tests (requires running server)
    print("\n" + "="*70)
    print("⚠️  Error Handling Tests require a running server")
    print("Start server with: python start_server.py")
    print("Then run: python -m pytest backend/tests/test_error_handling.py -v")
    print("="*70)
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Results Summary")
    print("="*70)
    
    passed = sum(1 for result in results if result)
    total = len(results)
    
    print(f"\n{passed}/{total} test suites passed")
    
    if passed == total:
        print("\n🎉 All automated tests passed!")
        print("\n📝 Next steps:")
        print("1. Start the server: python start_server.py")
        print("2. Run API tests: python -m pytest backend/tests/test_api_endpoints.py -v")
        print("3. Run E2E tests: python test_e2e_integration.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
