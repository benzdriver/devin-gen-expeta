"""
Mock LLM Router for testing the Clarifier component.
"""

class MockLLMRouter:
    """A mock implementation of the LLMRouter for testing purposes."""
    
    def __init__(self):
        """Initialize the mock router."""
        self.completion_calls = []
        self.generate_calls = []
        self.last_response = None
    
    def completion(self, prompt, model=None, temperature=0.7, max_tokens=1000, stop=None):
        """Mock completion method that returns a predefined response."""
        self.completion_calls.append({
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": stop
        })
        
        response = {
            "choices": [
                {
                    "text": """
I'll help clarify your requirements.

Based on your description, here's what I understand:

```yaml
name: Test Application
id: test-app-123
description: A test application for demonstration purposes
type: web_application
features:
  - name: User Authentication
    description: Basic login and registration functionality
  - name: Dashboard
    description: Simple dashboard showing key metrics
```

Is there anything else you'd like to add or modify about these requirements?
"""
                }
            ]
        }
        
        self.last_response = response
        return response
    
    def generate(self, prompt, model=None, temperature=0.7, max_tokens=1000, stop=None):
        """Mock generate method that returns a predefined response."""
        self.generate_calls.append({
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": stop
        })
        
        return {
            "content": """
Based on the top-level expectation, here are the sub-expectations:

```yaml
- name: User Authentication Module
  id: auth-module-001
  description: Handles user registration, login, and session management
  type: module
  parent_id: test-app-123
  
- name: Dashboard Module
  id: dashboard-module-001
  description: Displays key metrics and user statistics
  type: module
  parent_id: test-app-123
```

These sub-expectations break down the main components needed for the application.
"""
        }
    
    def set_next_response(self, response_text):
        """Set the next response to be returned by the completion method."""
        self.last_response = {
            "choices": [
                {
                    "text": response_text
                }
            ]
        }
