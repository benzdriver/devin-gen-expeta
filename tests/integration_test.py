"""
Integration test for Expeta 2.0 workflow from requirement input to code generation.
This test verifies the entire process including:
1. Clarifier multi-round dialogue
2. Expectation creation
3. Code generation
4. File download
"""

import sys
import os
import json
import requests
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE_URL = "http://localhost:8000"
TEST_SESSION_ID = "test_session_fixed_id"
TEST_REQUIREMENT = "I need a personal website with a portfolio section and a blog functionality"

def log_step(step_name):
    """Log a test step with timestamp"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {step_name}")
    print("=" * 80)

def test_chat_session():
    """Test the chat session API for multi-round dialogue"""
    log_step("Testing chat session API (Clarifier)")
    
    url = f"{API_BASE_URL}/chat/session"
    
    log_step("Step 1: Sending initial requirement")
    payload = {
        "user_message": TEST_REQUIREMENT,
        "session_id": TEST_SESSION_ID
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Clarifier response: {data.get('response', 'No response')}")
            
            log_step("Step 2: Providing additional details")
            payload = {
                "user_message": "I want the portfolio to showcase my design work with images and descriptions. The blog should have categories and comments.",
                "session_id": TEST_SESSION_ID
            }
            
            response = requests.post(url, json=payload)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Clarifier response: {data.get('response', 'No response')}")
                
                log_step("Step 3: Confirming requirements")
                payload = {
                    "user_message": "Yes, that's correct. I confirm these requirements are what I want.",
                    "session_id": TEST_SESSION_ID
                }
                
                response = requests.post(url, json=payload)
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Clarifier response: {data.get('response', 'No response')}")
                    print(f"Full response data: {data}")
                    
                    expectation_id = data.get('expectation_id')
                    if expectation_id:
                        print(f"Expectation created with ID: {expectation_id}")
                        return expectation_id
                    else:
                        print("No expectation ID returned")
                        return None
            
        return None
    except Exception as e:
        print(f"Error in chat session: {str(e)}")
        return None

def test_get_expectation(expectation_id):
    """Test retrieving the created expectation"""
    log_step(f"Testing get expectation API for ID: {expectation_id}")
    
    if not expectation_id:
        print("No expectation ID provided")
        return None
    
    url = f"{API_BASE_URL}/memory/expectations/{expectation_id}"
    
    try:
        response = requests.get(url)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Expectation data: {json.dumps(data, indent=2)}")
            return data
        
        return None
    except Exception as e:
        print(f"Error getting expectation: {str(e)}")
        return None

def test_generate_code(expectation_id):
    """Test code generation API"""
    log_step(f"Testing code generation API for expectation ID: {expectation_id}")
    
    if not expectation_id:
        print("No expectation ID provided")
        return None
    
    url = f"{API_BASE_URL}/generate"
    
    payload = {
        "expectation_id": expectation_id,
        "options": {
            "language": "python",
            "framework": "flask",
            "includeTests": True,
            "includeDocumentation": True
        }
    }
    
    try:
        print(f"Sending request to generate code with payload: {json.dumps(payload, indent=2)}")
        response = requests.post(url, json=payload)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Generated code summary: {len(data.get('files', []))} files generated")
            
            for i, file in enumerate(data.get('files', [])[:3]):
                print(f"\nFile {i+1}: {file.get('path', 'Unknown path')}")
                print(f"Content preview: {file.get('content', 'No content')[:200]}...")
            
            return data
        
        return None
    except Exception as e:
        print(f"Error generating code: {str(e)}")
        return None

def test_download_code(expectation_id):
    """Test code download API"""
    log_step(f"Testing code download API for expectation ID: {expectation_id}")
    
    if not expectation_id:
        print("No expectation ID provided")
        return False
    
    url = f"{API_BASE_URL}/download/code/{expectation_id}"
    
    try:
        response = requests.get(url)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            content_disposition = response.headers.get('Content-Disposition', '')
            
            print(f"Content-Type: {content_type}")
            print(f"Content-Disposition: {content_disposition}")
            
            filename = f"code_{expectation_id}.zip"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded code saved to: {filename}")
            return True
        
        return False
    except Exception as e:
        print(f"Error downloading code: {str(e)}")
        return False

def run_integration_test():
    """Run the full integration test"""
    log_step("Starting Expeta 2.0 Integration Test")
    
    expectation_id = test_chat_session()
    
    if not expectation_id:
        print("Failed to create expectation. Integration test failed.")
        return False
    
    expectation = test_get_expectation(expectation_id)
    
    if not expectation:
        print("Failed to retrieve expectation. Integration test failed.")
        return False
    
    generated_code = test_generate_code(expectation_id)
    
    if not generated_code:
        print("Failed to generate code. Integration test failed.")
        return False
    
    download_success = test_download_code(expectation_id)
    
    if not download_success:
        print("Failed to download code. Integration test failed.")
        return False
    
    log_step("Integration Test Completed Successfully")
    return True

if __name__ == "__main__":
    success = run_integration_test()
    print(f"\nIntegration test {'PASSED' if success else 'FAILED'}")
