"""
Script to generate Access Layer modules from expectations.yaml files
using the Expeta system.
"""

import os
import sys
import yaml
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.orchestrator import Expeta

def load_expectation(yaml_path):
    """Load expectation from YAML file"""
    with open(yaml_path, 'r') as f:
        expectation = yaml.safe_load(f)
    
    if 'id' not in expectation:
        import uuid
        expectation['id'] = f"exp-{uuid.uuid4().hex[:8]}"
    
    return expectation

def generate_module(module_name):
    """Generate code for a module based on its expectations.yaml"""
    base_path = Path(f"/home/ubuntu/expeta/access/{module_name}")
    yaml_path = base_path / "expectations.yaml"
    
    if not yaml_path.exists():
        print(f"Error: expectations.yaml not found for {module_name}")
        return False
    
    print(f"Generating code for {module_name} module...")
    
    config = {
        "version": "2.0.0",
        "llm_router": {
            "default_provider": "anthropic",
            "providers": {
                "anthropic": {
                    "model": "claude-3-5-sonnet",
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                "openai": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            },
            "fallback_order": ["anthropic", "openai"]
        }
    }
    
    expeta = Expeta(config=config)
    
    expectation = load_expectation(yaml_path)
    
    result = expeta.process_expectation(expectation)
    
    if result.get("success", False):
        generated_code = result["generation"]["generated_code"]
        for file_info in generated_code.get("files", []):
            file_path = base_path / file_info["path"]
            os.makedirs(file_path.parent, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(file_info["content"])
            
            print(f"Created: {file_path}")
        
        print(f"Successfully generated code for {module_name} module")
        return True
    else:
        print(f"Failed to generate code for {module_name} module")
        print(f"Error: {result.get('validation', {}).get('error', 'Unknown error')}")
        return False

def main():
    """Generate code for all access layer modules"""
    modules = ["rest_api", "graphql", "chat", "cli", "ui"]
    
    success_count = 0
    for module in modules:
        print(f"\n===== Processing {module} module =====")
        if generate_module(module):
            success_count += 1
    
    print(f"\nGenerated code for {success_count}/{len(modules)} modules")

if __name__ == "__main__":
    main()
