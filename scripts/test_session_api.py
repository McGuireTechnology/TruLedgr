#!/usr/bin/env python3
"""
Test script for session analytics API endpoints.
Tests the database-backed session management system via HTTP API.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_session_analytics_api():
    """Test the session analytics API endpoints"""
    print("🔍 Testing Session Analytics API")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Test health check first
        print("\n1. Testing API health...")
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    print("✅ API is healthy and running")
                else:
                    print(f"❌ API health check failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            return
        
        # 2. Test user registration to create test data
        print("\n2. Creating test user...")
        user_data = {
            "username": "testuser_analytics",
            "email": "analytics@test.com",
            "password": "Xy9$kN2mP8@vQ1zL"  # Very random, strong password
        }
        
        try:
            async with session.post(f"{BASE_URL}/users", json=user_data) as response:
                if response.status in [200, 201]:
                    user_response = await response.json()
                    print(f"✅ Test user created: {user_response.get('username')}")
                elif response.status == 409:
                    print("✅ Test user already exists")
                else:
                    error_text = await response.text()
                    print(f"⚠️ User creation response: {response.status} - {error_text}")
        except Exception as e:
            print(f"⚠️ User creation error: {e}")
        
        # 3. Test user login to create session
        print("\n3. Testing user login (creates session)...")
        login_data = {
            "username": "testuser_analytics",
            "password": "Xy9$kN2mP8@vQ1zL"  # Match the registration password
        }
        
        auth_token = None
        try:
            async with session.post(f"{BASE_URL}/users/auth/login", json=login_data) as response:
                if response.status == 200:
                    login_response = await response.json()
                    auth_token = login_response.get("access_token")
                    print("✅ User login successful, session created")
                else:
                    error_text = await response.text()
                    print(f"❌ Login failed: {response.status} - {error_text}")
                    return
        except Exception as e:
            print(f"❌ Login error: {e}")
            return
        
        if not auth_token:
            print("❌ No auth token received")
            return
        
        # Prepare headers for authenticated requests
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # 4. Test session list endpoint
        print("\n4. Testing user sessions endpoint...")
        try:
            async with session.get(f"{BASE_URL}/users/me/sessions", headers=headers) as response:
                if response.status == 200:
                    sessions_data = await response.json()
                    print(f"✅ Sessions retrieved: {sessions_data.get('total_sessions', 0)} total")
                    print(f"   Active sessions: {sessions_data.get('active_sessions', 0)}")
                    
                    # Show session details
                    sessions = sessions_data.get('sessions', [])
                    if sessions:
                        session_info = sessions[0]
                        print(f"   Current session IP: {session_info.get('client_ip')}")
                        print(f"   Login method: {session_info.get('login_method', 'password')}")
                        print(f"   Device: {session_info.get('device_fingerprint', 'unknown')}")
                else:
                    error_text = await response.text()
                    print(f"❌ Sessions endpoint failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Sessions endpoint error: {e}")
        
        # 5. Test session analytics endpoint (if implemented)
        print("\n5. Testing session analytics endpoint...")
        try:
            async with session.get(f"{BASE_URL}/users/me/sessions/analytics", headers=headers) as response:
                if response.status == 200:
                    analytics_data = await response.json()
                    print("✅ Session analytics retrieved:")
                    print(f"   Total sessions: {analytics_data.get('total_sessions', 0)}")
                    print(f"   Active sessions: {analytics_data.get('active_sessions', 0)}")
                    print(f"   Login methods: {analytics_data.get('login_methods', {})}")
                    print(f"   Device types: {analytics_data.get('sessions_by_device', {})}")
                    print(f"   Recent activities: {len(analytics_data.get('recent_activities', []))}")
                elif response.status == 404:
                    print("⚠️ Session analytics endpoint not found (not implemented yet)")
                else:
                    error_text = await response.text()
                    print(f"❌ Analytics endpoint failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Analytics endpoint error: {e}")
        
        # 6. Test admin session analytics (if admin endpoints exist)
        print("\n6. Testing admin session endpoints...")
        try:
            async with session.get(f"{BASE_URL}/admin/sessions", headers=headers) as response:
                if response.status == 200:
                    admin_data = await response.json()
                    print("✅ Admin session analytics retrieved")
                    print(f"   Total system sessions: {admin_data.get('total_sessions', 0)}")
                elif response.status == 403:
                    print("⚠️ Admin access denied (user not admin)")
                elif response.status == 404:
                    print("⚠️ Admin session endpoints not found")
                else:
                    error_text = await response.text()
                    print(f"❌ Admin endpoint failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Admin endpoint error: {e}")
        
        # 7. Test logout (session revocation)
        print("\n7. Testing logout (session revocation)...")
        try:
            async with session.post(f"{BASE_URL}/users/auth/logout", headers=headers) as response:
                if response.status in [200, 204]:
                    print("✅ Logout successful, session revoked")
                else:
                    error_text = await response.text()
                    print(f"❌ Logout failed: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ Logout error: {e}")
        
        # 8. Verify session is revoked
        print("\n8. Verifying session revocation...")
        try:
            async with session.get(f"{BASE_URL}/users/me/sessions", headers=headers) as response:
                if response.status == 401:
                    print("✅ Session properly revoked (unauthorized access)")
                elif response.status == 200:
                    sessions_data = await response.json()
                    active_sessions = sessions_data.get('active_sessions', 0)
                    if active_sessions == 0:
                        print("✅ No active sessions remaining")
                    else:
                        print(f"⚠️ Still have {active_sessions} active sessions")
                else:
                    print(f"⚠️ Unexpected response: {response.status}")
        except Exception as e:
            print(f"❌ Session verification error: {e}")

    print("\n" + "=" * 50)
    print("🏁 Session Analytics API Testing Complete")

if __name__ == "__main__":
    asyncio.run(test_session_analytics_api())
