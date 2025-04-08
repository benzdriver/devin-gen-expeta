"""
Environment Variable Loader for Expeta 2.0

This module provides utilities to load environment variables from .env files.
"""

import os
import re
from pathlib import Path

def load_dotenv(env_file=None):
    """Load environment variables from .env file
    
    Args:
        env_file: Optional path to .env file. If not provided, looks for .env in current directory
        
    Returns:
        Dictionary of loaded variables
    """
    if env_file is None:
        env_file = Path('.env')
    else:
        env_file = Path(env_file)
    
    if not env_file.exists():
        return {}
    
    loaded_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            
            os.environ[key] = value
            loaded_vars[key] = value
    
    return loaded_vars

def load_env_vars(env_file=None):
    """Load environment variables from .env file and set defaults
    
    Args:
        env_file: Optional path to .env file. If not provided, looks for .env in current directory
        
    Returns:
        Dictionary of loaded variables
    """
    loaded_vars = load_dotenv(env_file)
    
    defaults = {
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "OPENAI_PROJECT": os.environ.get("OPENAI_PROJECT", ""),
        "OPENAI_ORGANIZATION": os.environ.get("OPENAI_ORGANIZATION", ""),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
    }
    
    for key, value in defaults.items():
        if key not in loaded_vars and value:
            os.environ[key] = value
            loaded_vars[key] = value
    
    return loaded_vars
