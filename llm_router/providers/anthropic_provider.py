"""
Anthropic Provider for LLM Router

This module implements the Anthropic provider for the LLM Router.
"""

class AnthropicProvider:
    """Provider for Anthropic LLM services"""
    
    def __init__(self, config=None):
        """Initialize the Anthropic provider
        
        Args:
            config: Configuration dictionary for the provider
        """
        self.config = config or {}
        self._initialize_client()
        
    def send_request(self, request):
        """Send request to Anthropic API
        
        Args:
            request: Request data dictionary
            
        Returns:
            Response from Anthropic API
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
                "provider": "anthropic"
            }
            
    def _initialize_client(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            import os
            import requests
            from utils.env_loader import load_dotenv
            
            load_dotenv()
            
            api_key = self.config.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key not found. Set it in config or ANTHROPIC_API_KEY environment variable.")
            
            # Configure proxy settings from environment variables
            proxies = {}
            http_proxy = os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy")
            https_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
            
            if http_proxy:
                proxies["http"] = http_proxy
            if https_proxy:
                proxies["https"] = https_proxy
                
            # Create session with proxy settings if needed
            session = requests.Session()
            if proxies:
                session.proxies.update(proxies)
                
            # Initialize Anthropic client with custom session
            self.client = anthropic.Anthropic(
                api_key=api_key,
                http_client=session
            )
            
        except ImportError:
            raise ImportError("Anthropic package not installed. Install with 'pip install anthropic'")
        except Exception as e:
            raise Exception(f"Failed to initialize Anthropic client: {str(e)}")
            
    def _prepare_parameters(self, options):
        """Prepare parameters for Anthropic API
        
        Args:
            options: Options dictionary
            
        Returns:
            Parameters dictionary for API call
        """
        params = {
            "model": self.config.get("model", "claude-3-sonnet-20240229"),
            "max_tokens": self.config.get("max_tokens", 1000),
            "temperature": self.config.get("temperature", 0.7)
        }
        
        if "model" in options:
            params["model"] = options["model"]
        if "max_tokens" in options:
            params["max_tokens"] = options["max_tokens"]
        if "temperature" in options:
            params["temperature"] = options["temperature"]
            
        return params
        
    def _call_api(self, prompt, params):
        """Call Anthropic API
        
        Args:
            prompt: Prompt text
            params: Parameters dictionary
            
        Returns:
            API response
        """
        try:
            response = self.client.messages.create(
                model=params["model"],
                max_tokens=params["max_tokens"],
                temperature=params["temperature"],
                messages=[{"role": "user", "content": prompt}]
            )
            return response
        except Exception as e:
            raise Exception(f"Anthropic API call failed: {str(e)}")
            
    def _process_response(self, response):
        """Process API response
        
        Args:
            response: API response
            
        Returns:
            Processed response dictionary
        """
        try:
            return {
                "content": response.content[0].text,
                "provider": "anthropic",
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
        except Exception as e:
            raise Exception(f"Failed to process Anthropic response: {str(e)}")
