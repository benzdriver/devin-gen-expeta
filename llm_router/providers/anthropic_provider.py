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
            self.client = anthropic.Anthropic(
                api_key=self.config.get("api_key")
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
            "model": self.config.get("model", "claude-2"),
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
        """Call Anthropic API
        
        Args:
            prompt: Prompt text
            params: API parameters
            
        Returns:
            Raw API response
        """
        response = self.client.messages.create(
            model=params["model"],
            max_tokens=params["max_tokens"],
            temperature=params["temperature"],
            messages=[
                {"role": "user", "content": prompt}
            ]
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
            content = response.content[0].text
            
            return {
                "content": content,
                "provider": "anthropic",
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Failed to process response: {str(e)}",
                "provider": "anthropic"
            }
