"""
Token Tracking Utility for Expeta 2.0

This module provides token tracking and reporting for LLM usage.
"""

from datetime import datetime
import json
import os
from pathlib import Path

class TokenTracker:
    """Token usage tracker for LLM operations"""
    
    def __init__(self, log_dir=None):
        """Initialize token tracker
        
        Args:
            log_dir: Optional directory for token usage logs. If not provided, logs to ~/.expeta/logs
        """
        if log_dir is None:
            log_dir = os.path.expanduser("~/.expeta/logs")
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.usage_log = self.log_dir / "token_usage.jsonl"
        self.total_usage = {
            "anthropic": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "requests": 0},
            "openai": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "requests": 0},
            "local": {"total_tokens": 0, "requests": 0}
        }
        self.session_start = datetime.now().isoformat()
        
    class OperationTracker:
        """Context manager for tracking token usage during an operation"""
        
        def __init__(self, tracker, operation):
            self.tracker = tracker
            self.operation = operation
            
        def __enter__(self):
            """Enter the context manager"""
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            """Exit the context manager"""
            pass
    
    def track(self, operation):
        """Track token usage for an operation
        
        Args:
            operation: Operation name (e.g., "process", "clarify", "generate")
            
        Returns:
            Context manager for tracking token usage
        """
        return self.OperationTracker(self, operation)
        
    def track_usage(self, provider, usage_data, operation=None, model=None):
        """Track token usage for a provider
        
        Args:
            provider: Provider name (anthropic, openai, local)
            usage_data: Dictionary with token usage data
            operation: Optional operation description
            model: Optional model name
            
        Returns:
            Updated total usage dictionary
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "provider": provider,
            "operation": operation,
            "model": model,
            "usage": usage_data
        }
        
        with open(self.usage_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        if provider == "anthropic":
            self.total_usage[provider]["input_tokens"] += usage_data.get("input_tokens", 0)
            self.total_usage[provider]["output_tokens"] += usage_data.get("output_tokens", 0)
            self.total_usage[provider]["total_tokens"] += (
                usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0)
            )
            self.total_usage[provider]["requests"] += 1
        elif provider == "openai":
            self.total_usage[provider]["prompt_tokens"] += usage_data.get("prompt_tokens", 0)
            self.total_usage[provider]["completion_tokens"] += usage_data.get("completion_tokens", 0)
            self.total_usage[provider]["total_tokens"] += usage_data.get("total_tokens", 0)
            self.total_usage[provider]["requests"] += 1
        elif provider == "local":
            self.total_usage[provider]["total_tokens"] += usage_data.get("total_tokens", 0)
            self.total_usage[provider]["requests"] += 1
        
        return self.total_usage
        
    def generate_report(self, output_file=None):
        """Generate token usage report
        
        Args:
            output_file: Optional output file path for the report
            
        Returns:
            Report dictionary
        """
        end_time = datetime.now().isoformat()
        
        report = {
            "session_start": self.session_start,
            "session_end": end_time,
            "total_usage": self.total_usage,
            "summary": {
                "total_tokens": sum(provider["total_tokens"] for provider in self.total_usage.values()),
                "total_requests": sum(provider["requests"] for provider in self.total_usage.values()),
                "anthropic_usage": self.total_usage["anthropic"]["total_tokens"],
                "openai_usage": self.total_usage["openai"]["total_tokens"],
                "local_usage": self.total_usage["local"]["total_tokens"]
            }
        }
        
        if output_file:
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2)
        
        return report
        
    def get_usage_report(self):
        """Get a simplified token usage report
        
        Returns:
            Dictionary with token usage by provider
        """
        return {
            "anthropic": {"total": self.total_usage["anthropic"]["total_tokens"]},
            "openai": {"total": self.total_usage["openai"]["total_tokens"]},
            "local": {"total": self.total_usage["local"]["total_tokens"]}
        }
        
    def get_summary(self):
        """Get a summary of token usage (alias for get_usage_report)
        
        Returns:
            Dictionary with token usage summary
        """
        return self.get_usage_report()
        
    def track_memory_usage(self, memory_type, content):
        """Track token usage for memory storage
        
        Args:
            memory_type: Type of memory (expectations, generations, validations)
            content: Content being stored in memory
            
        Returns:
            Estimated token count
        """
        if isinstance(content, str):
            token_count = self.estimate_tokens(content)
        elif isinstance(content, dict) or isinstance(content, list):
            token_count = self.estimate_tokens(json.dumps(content))
        else:
            token_count = 0
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "memory_type": memory_type,
            "token_count": token_count
        }
        
        with open(self.log_dir / "memory_usage.jsonl", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
        return token_count
        
    def estimate_tokens(self, text):
        """Estimate token count for text
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        return len(text) // 4
        
    def get_memory_usage(self):
        """Get memory usage statistics
        
        Returns:
            Dictionary with memory usage statistics
        """
        memory_usage = {
            "expectations": 0,
            "generations": 0,
            "validations": 0,
            "total": 0
        }
        
        try:
            with open(self.log_dir / "memory_usage.jsonl", "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        memory_type = entry.get("memory_type")
                        token_count = entry.get("token_count", 0)
                        
                        if memory_type in memory_usage:
                            memory_usage[memory_type] += token_count
                    except:
                        pass
                        
            memory_usage["total"] = sum([
                memory_usage["expectations"],
                memory_usage["generations"],
                memory_usage["validations"]
            ])
        except:
            pass
            
        return memory_usage
        
    def get_token_limits(self):
        """Get token limits for different models
        
        Returns:
            Dictionary with token limits by model
        """
        return {
            "anthropic/claude-2": 100000,
            "openai/gpt-4": 8192,
            "openai/gpt-3.5-turbo": 4096
        }
        
    def get_available_tokens(self):
        """Calculate available tokens for different models
        
        Returns:
            Dictionary with available tokens by model
        """
        memory_usage = self.get_memory_usage()
        token_limits = self.get_token_limits()
        available = {}
        
        for model, limit in token_limits.items():
            available[model] = max(0, limit - memory_usage["total"])
            
        return available
