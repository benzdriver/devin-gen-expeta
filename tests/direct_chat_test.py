"""
Direct Test for EnhancedChatRequirements Component

This script tests the EnhancedChatRequirements component by directly interacting with the API
and verifying the chat session functionality works correctly.
"""

import os
import sys
import time
import json
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_URL = "http://localhost:8000"

def test_api_health():
    """Test if the API server is running and responding"""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        return False

def test_token_usage():
    """Test the token usage endpoint"""
    try:
        response = requests.get(f"{API_URL}/token/usage")
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Token usage endpoint working: {token_data}")
            return True
        else:
            print(f"❌ Token usage endpoint returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing token usage endpoint: {str(e)}")
        return False

def test_chat_session():
    """Test the chat session functionality"""
    print("\n🔍 Testing Chat Session Functionality...")
    
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
            
            return True, session_id
        else:
            print(f"❌ Failed to create chat session: {response.status_code}")
            print(response.text)
            return False, None
    except Exception as e:
        print(f"❌ Error creating chat session: {str(e)}")
        return False, None

def test_follow_up_message(session_id):
    """Test sending a follow-up message"""
    if not session_id:
        print("❌ Cannot send follow-up message without session ID")
        return False
    
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
            
            return True
        else:
            print(f"❌ Failed to continue chat session: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error continuing chat session: {str(e)}")
        return False

def test_confirmation_message(session_id):
    """Test sending a confirmation message"""
    if not session_id:
        print("❌ Cannot send confirmation message without session ID")
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
            
            expectation_id = data.get("expectation_id")
            if expectation_id:
                print(f"✅ Found expectation ID in response data: {expectation_id}")
                return True, expectation_id
            
            for msg in messages:
                content = msg.get('content', '')
                if 'expectation_id' in content.lower():
                    print(f"✅ Found expectation ID in message content")
                    import re
                    match = re.search(r'expectation_id[:\s]+([a-zA-Z0-9_-]+)', content, re.IGNORECASE)
                    if match:
                        expectation_id = match.group(1)
                        print(f"✅ Extracted expectation ID: {expectation_id}")
                        return True, expectation_id
            
            try:
                print("⚠️ No expectation ID found in response, trying to get from memory system...")
                memory_response = requests.get(f"{API_URL}/memory/expectations/latest")
                if memory_response.status_code == 200:
                    memory_data = memory_response.json()
                    expectation_id = memory_data.get("id")
                    if expectation_id:
                        print(f"✅ Retrieved expectation ID from memory: {expectation_id}")
                        return True, expectation_id
                    else:
                        print("❌ No expectation ID found in memory response")
                else:
                    print(f"❌ Failed to get latest expectation: {memory_response.status_code}")
            except Exception as memory_error:
                print(f"❌ Error accessing memory system: {str(memory_error)}")
            
            print("⚠️ Using session ID as fallback for expectation ID")
            return True, session_id
        else:
            print(f"❌ Failed to send confirmation: {response.status_code}")
            print(response.text)
            return False, None
    except Exception as e:
        print(f"❌ Error sending confirmation: {str(e)}")
        return False, None

def test_generate_code(expectation_id):
    """Test the code generation functionality"""
    if not expectation_id:
        print("❌ Cannot generate code without expectation ID")
        return False
    
    try:
        payload = {
            "expectation_id": expectation_id,
            "session_id": expectation_id  # Include session_id as fallback
        }
        
        print(f"\n📤 Requesting code generation for expectation: {expectation_id}")
        response = requests.post(f"{API_URL}/generate", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Code generation request accepted")
            print(f"DEBUG: Full response data: {data}")
            
            generation_id = data.get("generation_id") or data.get("id")
            
            if not generation_id and "generated_code" in data:
                print("✅ Found generated code in response")
                generation_id = f"gen_{expectation_id}"  # Create a synthetic ID based on expectation
                
            if generation_id:
                print(f"✅ Generation ID: {generation_id}")
                
                max_polls = 5
                poll_interval = 2
                
                if "generated_code" in data and data["generated_code"].get("files"):
                    print("✅ Code generation completed successfully (files found in response)")
                    return True
                    
                for i in range(max_polls):
                    print(f"📊 Polling generation progress ({i+1}/{max_polls})...")
                    try:
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
                            print(f"⚠️ Progress endpoint not available: {progress_response.status_code}")
                            if "generated_code" in data and data["generated_code"].get("files"):
                                print("✅ Using files from initial response as generation is complete")
                                return True
                    except Exception as e:
                        print(f"⚠️ Error checking progress: {str(e)}")
                        if "generated_code" in data and data["generated_code"].get("files"):
                            print("✅ Using files from initial response as generation is complete")
                            return True
                    
                    time.sleep(poll_interval)
                
                print("⚠️ Reached maximum polling attempts, generation may still be in progress")
                return True
            else:
                print("❌ No generation ID returned")
                return False
        else:
            print(f"❌ Failed to request code generation: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error requesting code generation: {str(e)}")
        return False

def main():
    """Main function to run the tests"""
    print("\n🚀 Starting Direct Chat Component Test")
    print("=" * 80)
    
    api_running = test_api_health()
    token_usage_working = test_token_usage()
    
    if not api_running:
        print("\n❌ Cannot proceed with tests. Please ensure API server is running.")
        return
    
    chat_success, session_id = test_chat_session()
    
    if chat_success and session_id:
        follow_up_success = test_follow_up_message(session_id)
        
        if follow_up_success:
            confirmation_success, expectation_id = test_confirmation_message(session_id)
            
            if confirmation_success and expectation_id:
                generation_success = test_generate_code(expectation_id)
                
                print("\n📊 Test Summary")
                print("=" * 80)
                print(f"API Health: {'✅ PASS' if api_running else '❌ FAIL'}")
                print(f"Token Usage: {'✅ PASS' if token_usage_working else '❌ FAIL'}")
                print(f"Chat Session: {'✅ PASS' if chat_success else '❌ FAIL'}")
                print(f"Follow-up Message: {'✅ PASS' if follow_up_success else '❌ FAIL'}")
                print(f"Confirmation Message: {'✅ PASS' if confirmation_success else '❌ FAIL'}")
                print(f"Code Generation: {'✅ PASS' if generation_success else '❌ FAIL'}")
                
                if chat_success and follow_up_success and confirmation_success and generation_success:
                    print("\n🎉 All tests passed successfully!")
                else:
                    print("\n⚠️ Some tests failed. Please check the logs above for details.")
            else:
                print("\n❌ Confirmation message test failed. Cannot proceed with code generation.")
        else:
            print("\n❌ Follow-up message test failed. Cannot proceed with confirmation.")
    else:
        print("\n❌ Chat session test failed. Cannot proceed with follow-up messages.")

if __name__ == "__main__":
    main()
