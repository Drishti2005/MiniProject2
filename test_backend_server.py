#!/usr/bin/env python3
"""
Test backend server endpoints
Run this while the server is running
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

print("="*60)
print("Backend Server Test")
print("="*60)

# Test 1: Health Check
print("\n1. Testing Health Check Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Health check passed!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Health check failed with status {response.status_code}")
except Exception as e:
    print(f"❌ Health check failed: {e}")
    print("\n⚠️  Make sure the server is running:")
    print("   python -m uvicorn backend.main:app --reload")
    exit(1)

# Test 2: List Sessions (should be empty initially)
print("\n2. Testing GET /api/sessions...")
try:
    response = requests.get(f"{BASE_URL}/api/sessions")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Sessions endpoint working!")
        print(f"   Found {len(data['sessions'])} session(s)")
    else:
        print(f"❌ Sessions endpoint failed with status {response.status_code}")
except Exception as e:
    print(f"❌ Sessions endpoint failed: {e}")

# Test 3: Get non-existent session (should return 404)
print("\n3. Testing GET /api/sessions/{id} with invalid ID...")
try:
    response = requests.get(f"{BASE_URL}/api/sessions/00000000-0000-0000-0000-000000000000")
    if response.status_code == 404:
        print("✅ 404 handling working correctly!")
    else:
        print(f"⚠️  Expected 404, got {response.status_code}")
except Exception as e:
    print(f"❌ Test failed: {e}")

# Test 4: Try to serve frontend
print("\n4. Testing GET / (frontend)...")
try:
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("✅ Frontend endpoint working!")
    else:
        print(f"⚠️  Frontend returned status {response.status_code}")
except Exception as e:
    print(f"❌ Frontend test failed: {e}")

print("\n" + "="*60)
print("✅ Basic backend tests completed!")
print("="*60)
print("\nNext steps:")
print("1. Test WebSocket connection (requires frontend or WebSocket client)")
print("2. Test full session lifecycle with transcript processing")
print("3. Test AI service integration")
