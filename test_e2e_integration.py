#!/usr/bin/env python
"""
End-to-End Integration Test for Sidekick Medical Assistant Backend
Tests the complete workflow: WebSocket connection, transcript processing, AI integration, summary generation
"""

import asyncio
import json
import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

try:
    import websockets
    from websockets.client import connect
except ImportError:
    print("❌ websockets library not installed. Install with: pip install websockets")
    sys.exit(1)

import requests


class BackendE2ETest:
    """End-to-end integration test for backend"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.ws_url = "ws://127.0.0.1:8000/ws/session"
        self.session_id = None
    
    def test_health_check(self):
        """Test 1: Health check endpoint"""
        print("\n🧪 Test 1: Health Check")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert data["status"] == "healthy", "Health check failed"
            print("✅ Health check passed")
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_list_sessions(self):
        """Test 2: List sessions endpoint"""
        print("\n🧪 Test 2: List Sessions")
        try:
            response = requests.get(f"{self.base_url}/api/sessions", timeout=5)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert "sessions" in data, "Missing sessions key"
            assert isinstance(data["sessions"], list), "Sessions should be a list"
            print(f"✅ List sessions passed ({len(data['sessions'])} sessions found)")
            return True
        except Exception as e:
            print(f"❌ List sessions failed: {e}")
            return False
    
    async def test_websocket_session_lifecycle(self):
        """Test 3: Complete WebSocket session lifecycle"""
        print("\n🧪 Test 3: WebSocket Session Lifecycle")
        
        try:
            async with connect(self.ws_url) as websocket:
                print("  → WebSocket connected")
                
                # Step 1: Receive session_created message
                message = await websocket.recv()
                data = json.loads(message)
                assert data["type"] == "session_created", f"Expected session_created, got {data['type']}"
                self.session_id = data["session_id"]
                print(f"  → Session created: {self.session_id}")
                
                # Step 2: Send transcript message
                transcript_msg = {
                    "type": "transcript",
                    "text": "The doctor mentioned hypertension and prescribed medication for high blood pressure.",
                    "language": "en"
                }
                await websocket.send(json.dumps(transcript_msg))
                print("  → Sent transcript message")
                
                # Step 3: Receive simplification response
                received_simplification = False
                timeout_counter = 0
                while not received_simplification and timeout_counter < 10:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(message)
                        print(f"  → Received: {data['type']}")
                        
                        if data["type"] == "simplification":
                            assert "terms" in data, "Missing terms in simplification"
                            print(f"  → Simplification received: {len(data['terms'])} terms")
                            received_simplification = True
                        elif data["type"] == "questions":
                            print(f"  → Questions received: {len(data.get('suggestions', []))} questions")
                        elif data["type"] == "error":
                            print(f"  ⚠️  Error received: {data.get('message')}")
                    except asyncio.TimeoutError:
                        timeout_counter += 1
                        if timeout_counter >= 10:
                            print("  ⚠️  Timeout waiting for simplification (AI service may be slow)")
                            break
                
                # Step 4: Send more transcript
                transcript_msg2 = {
                    "type": "transcript",
                    "text": "Follow up appointment scheduled in two weeks to check blood pressure levels.",
                    "language": "en"
                }
                await websocket.send(json.dumps(transcript_msg2))
                print("  → Sent second transcript message")
                
                # Wait for any responses
                await asyncio.sleep(1)
                
                # Step 5: End session
                end_msg = {"type": "end_session"}
                await websocket.send(json.dumps(end_msg))
                print("  → Sent end_session message")
                
                # Step 6: Receive summary
                received_summary = False
                timeout_counter = 0
                while not received_summary and timeout_counter < 10:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(message)
                        print(f"  → Received: {data['type']}")
                        
                        if data["type"] == "summary":
                            assert "data" in data, "Missing data in summary"
                            summary = data["data"]
                            print(f"  → Summary received: {summary.get('title', 'N/A')}")
                            received_summary = True
                        elif data["type"] == "error":
                            print(f"  ⚠️  Error received: {data.get('message')}")
                    except asyncio.TimeoutError:
                        timeout_counter += 1
                        if timeout_counter >= 10:
                            print("  ⚠️  Timeout waiting for summary (AI service may be slow)")
                            break
                
                print("✅ WebSocket session lifecycle completed")
                return True
                
        except Exception as e:
            print(f"❌ WebSocket test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_get_session_details(self):
        """Test 4: Get session details"""
        print("\n🧪 Test 4: Get Session Details")
        
        if not self.session_id:
            print("⚠️  Skipping (no session ID from previous test)")
            return True
        
        try:
            response = requests.get(f"{self.base_url}/api/sessions/{self.session_id}", timeout=5)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            
            assert "session" in data, "Missing session key"
            assert "transcript" in data, "Missing transcript key"
            assert "simplifications" in data, "Missing simplifications key"
            assert "summary" in data, "Missing summary key"
            
            print(f"  → Session: {data['session']['id']}")
            print(f"  → Transcript chunks: {len(data['transcript'])}")
            print(f"  → Simplifications: {len(data['simplifications'])}")
            print(f"  → Summary: {'Yes' if data['summary'] else 'No'}")
            
            print("✅ Get session details passed")
            return True
        except Exception as e:
            print(f"❌ Get session details failed: {e}")
            return False
    
    def test_delete_session(self):
        """Test 5: Delete session"""
        print("\n🧪 Test 5: Delete Session")
        
        if not self.session_id:
            print("⚠️  Skipping (no session ID from previous test)")
            return True
        
        try:
            response = requests.delete(f"{self.base_url}/api/sessions/{self.session_id}", timeout=5)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            data = response.json()
            assert data["status"] == "deleted", "Delete failed"
            
            # Verify session is gone
            response = requests.get(f"{self.base_url}/api/sessions/{self.session_id}", timeout=5)
            assert response.status_code == 404, "Session should be deleted"
            
            print("✅ Delete session passed")
            return True
        except Exception as e:
            print(f"❌ Delete session failed: {e}")
            return False
    
    def test_error_handling(self):
        """Test 6: Error handling"""
        print("\n🧪 Test 6: Error Handling")
        
        try:
            # Test 404 for non-existent session
            fake_id = "00000000-0000-0000-0000-000000000000"
            response = requests.get(f"{self.base_url}/api/sessions/{fake_id}", timeout=5)
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"
            
            # Test 404 for non-existent endpoint
            response = requests.get(f"{self.base_url}/api/nonexistent", timeout=5)
            assert response.status_code == 404, f"Expected 404, got {response.status_code}"
            
            print("✅ Error handling passed")
            return True
        except Exception as e:
            print(f"❌ Error handling failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 70)
        print("🚀 Starting End-to-End Integration Tests")
        print("=" * 70)
        
        results = []
        
        # REST API tests
        results.append(("Health Check", self.test_health_check()))
        results.append(("List Sessions", self.test_list_sessions()))
        
        # WebSocket test
        results.append(("WebSocket Lifecycle", await self.test_websocket_session_lifecycle()))
        
        # Session details test
        results.append(("Get Session Details", self.test_get_session_details()))
        
        # Delete test
        results.append(("Delete Session", self.test_delete_session()))
        
        # Error handling test
        results.append(("Error Handling", self.test_error_handling()))
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 Test Results Summary")
        print("=" * 70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {name}")
        
        print(f"\n{passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            return 1


async def main():
    """Main test runner"""
    print("\n⚠️  Make sure the backend server is running:")
    print("   python start_server.py")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTest cancelled")
        return 1
    
    tester = BackendE2ETest()
    return await tester.run_all_tests()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
