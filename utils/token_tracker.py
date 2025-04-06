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
