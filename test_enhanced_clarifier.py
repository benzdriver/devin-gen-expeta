"""
Test script for Enhanced Clarifier with real LLMs

This script tests the enhanced clarifier with real LLM providers and tracks token usage.
"""

import os
import json
from utils.env_loader import load_dotenv
from enhanced_clarifier.enhanced_clarifier import EnhancedClarifier
from llm_router.llm_router import LLMRouter

def test_enhanced_clarifier():
    """Test the enhanced clarifier with real LLM providers"""
    load_dotenv()
    
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not anthropic_key:
        print("ERROR: ANTHROPIC_API_KEY not found in environment or .env file")
        return False
    
    if not openai_key:
        print("WARNING: OPENAI_API_KEY not found. Will only use Anthropic as provider.")
    
    print("Initializing Enhanced Clarifier with real LLM...")
    clarifier = EnhancedClarifier()
    
    test_requirements = [
        "Create a function that sends an email to a user when they sign up.",
        "Implement a secure authentication system using JWT."
    ]
    
    print(f"\nTesting {len(test_requirements)} requirements:")
    
    for i, req in enumerate(test_requirements, 1):
        print(f"\n--- Requirement {i}: {req[:40]}... ---")
        result = clarifier.clarify_requirement(req)
        
        print(f"Top-level expectation: {result['top_level_expectation']['name']}")
        print(f"Sub-expectations: {len(result['sub_expectations'])}")
        
        current_usage = clarifier.token_tracker.total_usage
        print("\nCurrent token usage:")
        if "anthropic" in current_usage:
            anthropic_usage = current_usage["anthropic"]
            print(f"  Anthropic: {anthropic_usage.get('total_tokens', 0)} tokens " +
                  f"({anthropic_usage.get('input_tokens', 0)} input, {anthropic_usage.get('output_tokens', 0)} output)")
        
        if "openai" in current_usage:
            openai_usage = current_usage["openai"]
            print(f"  OpenAI: {openai_usage.get('total_tokens', 0)} tokens " +
                  f"({openai_usage.get('prompt_tokens', 0)} prompt, {openai_usage.get('completion_tokens', 0)} completion)")
    
    report_file = "clarifier_report.json"
    report = clarifier.generate_report(output_file=report_file)
    
    print(f"\nToken usage report generated and saved to {report_file}")
    print("\nSummary:")
    print(f"Total requirements processed: {report['summary']['total_requirements']}")
    print(f"Total tokens used: {report['summary']['total_tokens']}")
    print(f"Anthropic tokens: {report['summary']['anthropic_tokens']}")
    print(f"OpenAI tokens: {report['summary']['openai_tokens']}")
    
    return True

if __name__ == "__main__":
    success = test_enhanced_clarifier()
    print("\nTest completed successfully!" if success else "\nTest failed!")
