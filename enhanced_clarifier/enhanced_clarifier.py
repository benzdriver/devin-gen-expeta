"""
Enhanced Clarifier Module for Expeta 2.0

This module extends the base Clarifier with token tracking and reporting capabilities.
"""

import json
from datetime import datetime

from clarifier.clarifier import Clarifier
from llm_router.llm_router import LLMRouter
from utils.token_tracker import TokenTracker
from utils.env_loader import load_dotenv

class EnhancedClarifier(Clarifier):
    """Enhanced Clarifier with token tracking and real LLM integration"""
    
    def __init__(self, llm_router=None, token_tracker=None):
        """Initialize enhanced clarifier
        
        Args:
            llm_router: Optional LLM router. If not provided, default router with real LLM will be created.
            token_tracker: Optional token tracker. If not provided, a new one will be created.
        """
        load_dotenv()
        
        self.token_tracker = token_tracker or TokenTracker()
        
        if llm_router is None:
            llm_router = self._create_real_llm_router()
        
        super().__init__(llm_router=llm_router)
        
        self.results = []
    
    def _create_real_llm_router(self):
        """Create LLM router with real providers
        
        Returns:
            LLM router instance with token tracking
        """
        router = LLMRouter()
        router.token_tracker = self.token_tracker
        return router
    
    def clarify_requirement(self, requirement_text):
        """Clarify requirements with token tracking
        
        Args:
            requirement_text: Natural language requirement text
            
        Returns:
            Dictionary with top-level expectation, sub-expectations, and process metadata
        """
        start_time = datetime.now().isoformat()
        
        result = super().clarify_requirement(requirement_text)
        
        end_time = datetime.now().isoformat()
        
        result_record = {
            "requirement": requirement_text,
            "result": result,
            "start_time": start_time,
            "end_time": end_time,
            "token_usage": self.token_tracker.total_usage
        }
        
        self.results.append(result_record)
        
        return result
    
    def generate_report(self, output_file=None):
        """Generate token usage report
        
        Args:
            output_file: Optional output file path for the report
            
        Returns:
            Report dictionary with clarification results and token usage
        """
        token_report = self.token_tracker.generate_report()
        
        report = {
            "token_usage": token_report,
            "clarification_results": self.results,
            "summary": {
                "total_requirements": len(self.results),
                "total_tokens": token_report["summary"]["total_tokens"],
                "anthropic_tokens": token_report["summary"]["anthropic_usage"],
                "openai_tokens": token_report["summary"]["openai_usage"]
            }
        }
        
        if output_file:
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2)
        
        return report
