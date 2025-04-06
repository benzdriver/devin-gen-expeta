"""
OpenAI Provider for LLM Router

This module implements the OpenAI provider for the LLM Router.
"""

class OpenAIProvider:
    """Provider for OpenAI LLM services"""
    
    def __init__(self, config=None):
        """Initialize the OpenAI provider
        
        Args:
            config: Configuration dictionary for the provider
        """
        self.config = config or {}
        self._initialize_client()
        
    def send_request(self, request):
        """Send request to OpenAI API
        
        Args:
            request: Request data dictionary
            
        Returns:
            Response from OpenAI API
        """
        try:
            prompt = request.get("prompt", "")
            options = request.get("options", {})
            
            params = self._prepare_parameters(options)
            
            response = self._call_api(prompt, params)
            
            return self._process_response(response)
            
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "provider": "openai"
            }
            
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            import openai
            import os
            from utils.env_loader import load_dotenv
            
            load_dotenv()
            
            api_key = self.config.get("api_key") or os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found. Set it in config or OPENAI_API_KEY environment variable.")
            
            org_id = os.environ.get("OPENAI_ORGANIZATION")
            client_args = {"api_key": api_key}
            if org_id:
                client_args["organization"] = org_id
                
            self.client = openai.OpenAI(**client_args)
        except ImportError:
            raise ImportError("OpenAI package not installed. Install with 'pip install openai'")
        except Exception as e:
            raise Exception(f"Failed to initialize OpenAI client: {str(e)}")
            
    def _prepare_parameters(self, options):
        """Prepare parameters for OpenAI API
        
        Args:
            options: Options dictionary
            
        Returns:
            Parameters dictionary for API call
        """
        params = {
            "model": self.config.get("model", "gpt-4"),
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 1000)
        }
        
        if "model" in options:
            params["model"] = options["model"]
        if "temperature" in options:
            params["temperature"] = options["temperature"]
        if "max_tokens" in options:
            params["max_tokens"] = options["max_tokens"]
            
        return params
        
    def _call_api(self, prompt, params):
        """Call OpenAI API
        
        Args:
            prompt: Prompt text
            params: API parameters
            
        Returns:
            Raw API response
        """
        messages = [{"role": "user", "content": prompt}]
        
        response = self.client.chat.completions.create(
            messages=messages,
            **params
        )
        
        return response
        
    def _process_response(self, response):
        """Process API response
        
        Args:
            response: Raw API response
            
        Returns:
            Processed response dictionary
        """
        try:
            content = response.choices[0].message.content
            
            return {
                "content": content,
                "provider": "openai",
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to process response: {str(e)}",
                "provider": "openai"
            }
