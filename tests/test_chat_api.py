"""
Direct API Test for Chat Session Endpoint

This script tests the chat session API endpoint directly without relying on the UI.
It verifies that the API can handle multi-round conversations and properly maintains context.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_URL = "http://localhost:8000"

def test_chat_session_api():
    """Test the chat session API endpoint directly"""
    print("\n🔍 Testing Chat Session API...")
    
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print(f"❌ API server returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        return False
    
    try:
        response = requests.get(f"{API_URL}/token/usage")
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Token usage endpoint working: {token_data}")
        else:
            print(f"❌ Token usage endpoint returned status code {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing token usage endpoint: {str(e)}")
    
    session_id = None
    try:
        initial_message = "I need a personal website with a blog functionality"
        
        payload = {
            "user_message": initial_message,
            "session_id": None  # Start a new session
        }
        
        print(f"📤 Sending initial message: '{initial_message}'")
        response = requests.post(f"{API_URL}/chat/session", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            messages = data.get("messages", [])
            
            print(f"✅ New chat session created with ID: {session_id}")
            print(f"✅ Received {len(messages)} messages in response")
            
            for i, msg in enumerate(messages):
                print(f"  Message {i+1}: {msg.get('role')} - {msg.get('content')[:50]}...")
            
            requires_clarification = data.get("requires_clarification", False)
            print(f"✅ Requires clarification: {requires_clarification}")
        else:
            print(f"❌ Failed to create chat session: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error creating chat session: {str(e)}")
        return False
    
    if session_id:
        try:
            follow_up_message = "I want to showcase my design work with images and descriptions. The blog should have categories and comments."
            
            payload = {
                "user_message": follow_up_message,
                "session_id": session_id
            }
            
            print(f"\n📤 Sending follow-up message: '{follow_up_message}'")
            response = requests.post(f"{API_URL}/chat/session", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                print(f"✅ Continued chat session successfully")
                print(f"✅ Received {len(messages)} messages in response")
                
                for i, msg in enumerate(messages):
                    if i >= len(messages) - 2:  # Only show the last two messages
                        print(f"  Message {i+1}: {msg.get('role')} - {msg.get('content')[:50]}...")
                
                requires_clarification = data.get("requires_clarification", False)
                print(f"✅ Requires clarification: {requires_clarification}")
            else:
                print(f"❌ Failed to continue chat session: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ Error continuing chat session: {str(e)}")
            return False
        
        try:
            confirmation_message = "Yes, that's correct. I confirm these requirements are what I want."
            
            payload = {
                "user_message": confirmation_message,
                "session_id": session_id
            }
            
            print(f"\n📤 Sending confirmation message: '{confirmation_message}'")
            response = requests.post(f"{API_URL}/chat/session", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                print(f"✅ Confirmation sent successfully")
                print(f"✅ Received {len(messages)} messages in response")
                
                for i, msg in enumerate(messages):
                    if i >= len(messages) - 2:  # Only show the last two messages
                        print(f"  Message {i+1}: {msg.get('role')} - {msg.get('content')[:50]}...")
                
                expectation_id = None
                for msg in messages:
                    content = msg.get('content', '')
                    if 'expectation_id' in content.lower():
                        print(f"✅ Found expectation ID in response")
                        import re
                        match = re.search(r'expectation_id[:\s]+([a-zA-Z0-9_-]+)', content, re.IGNORECASE)
                        if match:
                            expectation_id = match.group(1)
                            print(f"✅ Extracted expectation ID: {expectation_id}")
                
                if not expectation_id:
                    print("⚠️ No expectation ID found in response")
            else:
                print(f"❌ Failed to send confirmation: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ Error sending confirmation: {str(e)}")
            return False
    
    return True

def test_generate_code_api(session_id=None):
    """Test the code generation API endpoint"""
    if not session_id:
        print("\n⚠️ No session ID provided, skipping code generation test")
        return False
    
    print("\n🔍 Testing Code Generation API...")
    
    try:
        payload = {
            "session_id": session_id
        }
        
        print(f"📤 Requesting code generation for session: {session_id}")
        response = requests.post(f"{API_URL}/generate/code", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Code generation request accepted")
            
            generation_id = data.get("generation_id")
            if generation_id:
                print(f"✅ Generation ID: {generation_id}")
                
                max_polls = 10
                poll_interval = 2
                
                for i in range(max_polls):
                    print(f"📊 Polling generation progress ({i+1}/{max_polls})...")
                    progress_response = requests.get(f"{API_URL}/generate/progress/{generation_id}")
                    
                    if progress_response.status_code == 200:
                        progress_data = progress_response.json()
                        progress = progress_data.get("progress", 0)
                        status = progress_data.get("status", "unknown")
                        
                        print(f"✅ Generation progress: {progress}%, Status: {status}")
                        
                        if status.lower() == "completed" or progress >= 100:
                            print("✅ Code generation completed successfully")
                            return True
                        
                        if status.lower() == "failed":
                            print("❌ Code generation failed")
                            return False
                    else:
                        print(f"❌ Failed to get generation progress: {progress_response.status_code}")
                    
                    time.sleep(poll_interval)
                
                print("⚠️ Reached maximum polling attempts, generation may still be in progress")
            else:
                print("❌ No generation ID returned")
        else:
            print(f"❌ Failed to request code generation: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error requesting code generation: {str(e)}")
        return False
    
    return False

def main():
    """Main function to run the tests"""
    print("\n🚀 Starting Direct Chat API Test")
    print("=" * 80)
    
    chat_success = test_chat_session_api()
    
    print("\n📊 Test Summary")
    print("=" * 80)
    print(f"Chat Session API Test: {'✅ PASS' if chat_success else '❌ FAIL'}")
    
    if chat_success:
        print("\n🎉 Chat API test passed successfully!")
    else:
        print("\n⚠️ Chat API test failed. Please check the logs above for details.")

if __name__ == "__main__":
    main()
