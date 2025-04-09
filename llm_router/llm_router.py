"""
LLM Router Module for Expeta 2.0

This module handles interactions with large language models, providing a unified
interface for sending requests to different LLM providers and managing responses.
"""

class LLMRouter:
    """LLM router, handles interactions with large language models"""

    def __init__(self, config=None):
        """Initialize the LLM router
        
        Args:
            config: Optional configuration dictionary. If not provided, default config will be loaded.
        """
        self.config = config or self._load_default_config()
        self.providers = self._initialize_providers()
        self._request_history = []
        
        from utils.token_tracker import TokenTracker
        self.token_tracker = TokenTracker()

    def generate(self, prompt, options=None):
        """Generate text response from LLM
        
        Args:
            prompt: The prompt text to send to the LLM
            options: Optional dictionary with generation parameters
            
        Returns:
            The response from the LLM
        """
        opts = self._merge_options(options)
        request = self._prepare_request(prompt, opts)
        
        fallback_order = self.config.get("fallback_order", list(self.providers.keys()))
        
        last_error = None
        for provider_name in fallback_order:
            if provider_name not in self.providers:
                continue
                
            provider = self.providers[provider_name]
            
            try:
                response = provider.send_request(request)
                
                if "usage" in response and not response.get("error", False):
                    self.token_tracker.track_usage(response["provider"], response["usage"], 
                                                operation="generate", model=response.get("model"))
                
                self._record_request(prompt, opts, response)
                return response
                
            except Exception as e:
                last_error = e
                continue  # Try next provider
        
        if last_error:
            raise ValueError(f"All LLM providers failed. Last error: {str(last_error)}")
        else:
            raise ValueError("No LLM providers available")

    def sync_to_memory(self, memory_system):
        """Sync request history to memory system (delayed call)
        
        Args:
            memory_system: The memory system to sync to
            
        Returns:
            Dictionary with sync results
        """
        for request in self._request_history:
            memory_system.record_llm_request(request)

        synced_count = len(self._request_history)
        self._request_history = []

        return {"synced_count": synced_count}
        
    def _load_default_config(self):
        """Load default configuration
        
        Returns:
            Default configuration dictionary
        """
        return {
            "default_provider": "anthropic",
            "providers": {
                "openai": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                "anthropic": {
                    "model": "claude-3-sonnet-20240229",
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                "local": {
                    "model": "llama-2-7b",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            "fallback_order": ["anthropic", "openai", "local"]
        }
        
    def _initialize_providers(self):
        """Initialize LLM providers based on configuration
        
        Returns:
            Dictionary of provider instances
        """
        providers = {}
        provider_configs = self.config.get("providers", {})
        
        if "openai" in provider_configs:
            from .providers.openai_provider import OpenAIProvider
            providers["openai"] = OpenAIProvider(provider_configs["openai"])
            
        if "anthropic" in provider_configs:
            from .providers.anthropic_provider import AnthropicProvider
            config = provider_configs["anthropic"].copy()
            if "proxies" in config:
                del config["proxies"]
            providers["anthropic"] = AnthropicProvider(config)
            
        if "local" in provider_configs:
            from .providers.local_provider import LocalProvider
            providers["local"] = LocalProvider(provider_configs["local"])
            
        return providers
        
    def _merge_options(self, options):
        """Merge provided options with default options
        
        Args:
            options: User-provided options dictionary
            
        Returns:
            Merged options dictionary
        """
        if options is None:
            options = {}
            
        default_provider = self.config.get("default_provider", "openai")
        default_options = self.config.get("providers", {}).get(default_provider, {})
        
        merged = default_options.copy()
        merged.update(options)
        
        return merged
        
    def _select_provider(self, options):
        """Select appropriate provider based on options
        
        Args:
            options: Options dictionary with provider preferences
            
        Returns:
            Selected provider instance
        """
        provider_name = options.get("provider")
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name]
            
        default_provider = self.config.get("default_provider", "openai")
        if default_provider in self.providers:
            return self.providers[default_provider]
            
        fallback_order = self.config.get("fallback_order", list(self.providers.keys()))
        for provider_name in fallback_order:
            if provider_name in self.providers:
                return self.providers[provider_name]
                
        raise ValueError("No LLM provider available")
        
    def _prepare_request(self, prompt, options):
        """Prepare request data
        
        Args:
            prompt: The prompt text
            options: Options dictionary
            
        Returns:
            Request data dictionary
        """
        return {
            "prompt": prompt,
            "options": options,
            "timestamp": self._get_current_timestamp()
        }
        
    def _record_request(self, prompt, options, response):
        """Record request and response to history
        
        Args:
            prompt: The prompt text
            options: Options dictionary
            response: Response from LLM
        """
        request_record = {
            "prompt": prompt,
            "options": options,
            "response": response,
            "timestamp": self._get_current_timestamp()
        }
        
        self._request_history.append(request_record)
        
    def _get_current_timestamp(self):
        """Get current timestamp
        
        Returns:
            Current timestamp string
        """
        from datetime import datetime
        return datetime.now().isoformat()
