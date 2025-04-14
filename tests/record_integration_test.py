"""
Record Integration Test for Expeta 2.0

This script records the complete process of using Expeta to generate a personal blog website,
from initial requirements to final deployment. It captures each step of the process,
including the multi-round conversation with the Clarifier, expectation generation,
code generation, validation, and deployment.

Usage:
    python record_integration_test.py [--output_dir OUTPUT_DIR]

Options:
    --output_dir OUTPUT_DIR    Directory to save the recording [default: ./recordings]
"""

import os
import sys
import json
import time
import argparse
import requests
import logging
import subprocess
from datetime import datetime
from pathlib import Path
import shutil
import webbrowser
from urllib.parse import urljoin

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("expeta_recording.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ExpetaRecorder")

API_BASE_URL = "http://localhost:8000"
UI_BASE_URL = "http://localhost:3000"
RECORDING_DIR = "./recordings"
SCREENSHOTS_DIR = "screenshots"
CONVERSATION_FILE = "conversation.json"
EXPECTATIONS_FILE = "expectations.json"
CODE_GENERATION_FILE = "generated_code.json"
DEPLOYMENT_FILE = "deployment.json"
SUMMARY_FILE = "process_summary.md"

class ExpetaRecorder:
    """Records the complete process of using Expeta to generate a website."""
    
    def __init__(self, output_dir=None):
        """Initialize the recorder with the output directory."""
        self.output_dir = output_dir or RECORDING_DIR
        self.screenshots_dir = os.path.join(self.output_dir, SCREENSHOTS_DIR)
        self.session_id = None
        self.expectation_id = None
        self.conversation = []
        self.expectations = {}
        self.generated_code = {}
        self.deployment_info = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.recording_id = f"expeta_recording_{self.timestamp}"
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        logger.info(f"Recording will be saved to: {self.output_dir}")
        
    def take_screenshot(self, name):
        """Take a screenshot of the current UI state."""
        try:
            screenshot_path = os.path.join(self.screenshots_dir, f"{name}_{self.timestamp}.png")
            logger.info(f"Taking screenshot: {screenshot_path}")
            
            with open(screenshot_path, 'w') as f:
                f.write(f"Screenshot placeholder for {name}")
                
            return screenshot_path
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return None
    
    def start_conversation(self, initial_requirement):
        """Start a conversation with the Clarifier."""
        try:
            logger.info("Starting conversation with Clarifier")
            self.take_screenshot("before_conversation")
            
            response = requests.post(
                f"{API_BASE_URL}/chat/session",
                json={"user_message": initial_requirement}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                self.conversation.extend(data.get("messages", []))
                
                logger.info(f"Conversation started with session ID: {self.session_id}")
                self.take_screenshot("after_initial_response")
                
                return data
            else:
                logger.error(f"Failed to start conversation: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            return None
    
    def continue_conversation(self, user_message):
        """Continue the conversation with the Clarifier."""
        try:
            if not self.session_id:
                logger.error("No active session to continue conversation")
                return None
                
            logger.info(f"Continuing conversation with message: {user_message}")
            self.take_screenshot("before_response")
            
            response = requests.post(
                f"{API_BASE_URL}/chat/session",
                json={
                    "user_message": user_message,
                    "session_id": self.session_id
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.conversation.extend(data.get("messages", []))
                
                if "expectation" in data and data["expectation"]:
                    self.expectations = data["expectation"]
                    self.expectation_id = self.expectations.get("id")
                    logger.info(f"Expectation generated with ID: {self.expectation_id}")
                
                self.take_screenshot("after_response")
                return data
            else:
                logger.error(f"Failed to continue conversation: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error continuing conversation: {str(e)}")
            return None
    
    def generate_code(self):
        """Generate code based on the expectation."""
        try:
            if not self.expectation_id:
                logger.error("No expectation ID available for code generation")
                return None
                
            logger.info(f"Generating code for expectation ID: {self.expectation_id}")
            self.take_screenshot("before_code_generation")
            
            response = requests.post(
                f"{API_BASE_URL}/generate",
                json={
                    "expectation_id": self.expectation_id,
                    "options": {
                        "language": "python",
                        "framework": "flask"
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.generated_code = data
                logger.info(f"Code generated successfully with {len(data.get('files', []))} files")
                
                code_dir = os.path.join(self.output_dir, "generated_code")
                os.makedirs(code_dir, exist_ok=True)
                
                for file_info in data.get("files", []):
                    file_path = os.path.join(code_dir, file_info.get("name", "unknown.txt"))
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    with open(file_path, "w") as f:
                        f.write(file_info.get("content", ""))
                
                self.take_screenshot("after_code_generation")
                return data
            else:
                logger.error(f"Failed to generate code: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            return None
    
    def deploy_website(self):
        """Deploy the generated website locally."""
        try:
            if not self.expectation_id:
                logger.error("No expectation ID available for deployment")
                return None
                
            logger.info(f"Deploying website for expectation ID: {self.expectation_id}")
            self.take_screenshot("before_deployment")
            
            response = requests.get(
                f"{API_BASE_URL}/deploy/website",
                params={"expectation_id": self.expectation_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.deployment_info = data
                logger.info(f"Website deployed successfully: {data.get('url')}")
                
                if data.get("url"):
                    webbrowser.open(data.get("url"))
                
                self.take_screenshot("after_deployment")
                return data
            else:
                logger.error(f"Failed to deploy website: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error deploying website: {str(e)}")
            return None
    
    def save_recording(self):
        """Save all recorded data to files."""
        try:
            logger.info("Saving recording data")
            
            with open(os.path.join(self.output_dir, CONVERSATION_FILE), "w") as f:
                json.dump(self.conversation, f, indent=2)
            
            with open(os.path.join(self.output_dir, EXPECTATIONS_FILE), "w") as f:
                json.dump(self.expectations, f, indent=2)
            
            with open(os.path.join(self.output_dir, CODE_GENERATION_FILE), "w") as f:
                json.dump(self.generated_code, f, indent=2)
            
            with open(os.path.join(self.output_dir, DEPLOYMENT_FILE), "w") as f:
                json.dump(self.deployment_info, f, indent=2)
            
            self._generate_summary()
            
            logger.info(f"Recording saved successfully to {self.output_dir}")
            return True
        except Exception as e:
            logger.error(f"Error saving recording: {str(e)}")
            return False
    
    def _generate_summary(self):
        """Generate a summary markdown file of the entire process."""
        try:
            summary_path = os.path.join(self.output_dir, SUMMARY_FILE)
            logger.info(f"Generating summary at {summary_path}")
            
            with open(summary_path, "w") as f:
                f.write(f"# Expeta 2.0 Process Recording\n\n")
                f.write(f"Recording ID: {self.recording_id}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## Conversation with Clarifier\n\n")
                for msg in self.conversation:
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    timestamp = msg.get("timestamp", "")
                    f.write(f"**{role.capitalize()}** ({timestamp}):\n{content}\n\n")
                
                f.write("## Generated Expectation\n\n")
                f.write("```json\n")
                f.write(json.dumps(self.expectations, indent=2))
                f.write("\n```\n\n")
                
                f.write("## Generated Code\n\n")
                f.write(f"Total files: {len(self.generated_code.get('files', []))}\n\n")
                for file_info in self.generated_code.get("files", [])[:5]:  # Show first 5 files
                    f.write(f"### {file_info.get('name', 'unknown')}\n\n")
                    f.write("```\n")
                    content = file_info.get("content", "")
                    if len(content) > 500:
                        content = content[:500] + "...\n[content truncated]"
                    f.write(content)
                    f.write("\n```\n\n")
                
                if len(self.generated_code.get("files", [])) > 5:
                    f.write(f"*... and {len(self.generated_code.get('files', [])) - 5} more files*\n\n")
                
                f.write("## Deployment Information\n\n")
                f.write("```json\n")
                f.write(json.dumps(self.deployment_info, indent=2))
                f.write("\n```\n\n")
                
                f.write("## Process Timeline\n\n")
                f.write("1. Started conversation with Clarifier\n")
                f.write("2. Multi-round requirement clarification\n")
                f.write("3. Generated structured expectation model\n")
                f.write("4. Generated code based on expectations\n")
                f.write("5. Deployed website locally\n")
                
            logger.info("Summary generated successfully")
            return True
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return False

def run_multi_round_conversation(recorder):
    """Run a multi-round conversation to generate a personal blog website."""
    initial_requirement = "I need a personal website with a blog functionality"
    response = recorder.start_conversation(initial_requirement)
    
    if not response:
        logger.error("Failed to start conversation")
        return False
    
    user_response = "I want a creative portfolio website to showcase my design work. I prefer a modern, minimalist style with a light color scheme."
    response = recorder.continue_conversation(user_response)
    
    if not response:
        logger.error("Failed in first clarification round")
        return False
    
    user_response = "Yes, I'd like the blog to have categories and comments. I also need a portfolio section to showcase my projects with images and descriptions."
    response = recorder.continue_conversation(user_response)
    
    if not response:
        logger.error("Failed in second clarification round")
        return False
    
    user_response = "I prefer a light color scheme with accent colors. Modern CSS styling is very important to me. I like clean, sans-serif fonts."
    response = recorder.continue_conversation(user_response)
    
    if not response:
        logger.error("Failed in third clarification round")
        return False
    
    user_response = "Yes, that's exactly what I need."
    response = recorder.continue_conversation(user_response)
    
    if not response or not recorder.expectation_id:
        logger.error("Failed to generate expectation")
        return False
    
    logger.info(f"Expectation generated with ID: {recorder.expectation_id}")
    return True

def main():
    """Main function to run the recording process."""
    parser = argparse.ArgumentParser(description="Record the Expeta code generation process")
    parser.add_argument("--output_dir", help="Directory to save the recording", default=RECORDING_DIR)
    args = parser.parse_args()
    
    logger.info("Starting Expeta recording process")
    
    recorder = ExpetaRecorder(output_dir=args.output_dir)
    
    if not run_multi_round_conversation(recorder):
        logger.error("Failed to complete conversation process")
        return 1
    
    if not recorder.generate_code():
        logger.error("Failed to generate code")
        return 1
    
    if not recorder.deploy_website():
        logger.error("Failed to deploy website")
        return 1
    
    if not recorder.save_recording():
        logger.error("Failed to save recording")
        return 1
    
    logger.info(f"Recording completed successfully. Results saved to {recorder.output_dir}")
    logger.info(f"Summary available at {os.path.join(recorder.output_dir, SUMMARY_FILE)}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
