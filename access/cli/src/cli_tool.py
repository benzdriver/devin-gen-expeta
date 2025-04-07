"""
CLI Tool Access Layer for Expeta 2.0

This module provides a command-line interface for interacting with Expeta.
"""

import os
import sys
import json
import click
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from orchestrator.orchestrator import Expeta
from utils.env_loader import load_dotenv
from utils.token_tracker import TokenTracker

load_dotenv()

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
token_tracker = TokenTracker()

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Expeta CLI - Semantic-Driven Software Development"""
    pass

@cli.command()
@click.argument("requirement", required=True)
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.option("--format", "-f", type=click.Choice(["text", "json", "yaml"]), default="text", help="Output format")
def process(requirement, output, format):
    """Process a requirement through the entire workflow"""
    click.echo("Processing requirement...")
    
    try:
        with token_tracker.track("process"):
            result = expeta.process_requirement(requirement)
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return 1
    
    if not result:
        click.echo("Error: Failed to process requirement")
        return 1
    
    formatted_output = format_output(result, format)
    
    if output:
        try:
            with open(output, "w") as f:
                f.write(formatted_output)
            click.echo(f"Results written to {output}")
        except Exception as e:
            click.echo(f"Error writing to file: {str(e)}")
            return 1
    else:
        click.echo(formatted_output)
    
    try:
        token_usage = token_tracker.get_usage_report()
        click.echo("\nToken Usage:")
        for provider, usage in token_usage.items():
            click.echo(f"{provider}: {usage.get('total', 0)} tokens")
    except Exception as e:
        click.echo(f"Warning: Could not get token usage report: {str(e)}")
    
    return 0

@cli.command()
@click.argument("requirement", required=True)
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.option("--format", "-f", type=click.Choice(["text", "json", "yaml"]), default="text", help="Output format")
def clarify(requirement, output, format):
    """Clarify a requirement into structured expectations"""
    click.echo("Clarifying requirement...")
    
    try:
        with token_tracker.track("clarify"):
            result = expeta.clarifier.clarify_requirement(requirement)
            expeta.clarifier.sync_to_memory(expeta.memory_system)
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return 1
    
    if not result:
        click.echo("Error: Failed to clarify requirement")
        return 1
    
    formatted_output = format_output(result, format)
    
    if output:
        try:
            with open(output, "w") as f:
                f.write(formatted_output)
            click.echo(f"Results written to {output}")
        except Exception as e:
            click.echo(f"Error writing to file: {str(e)}")
            return 1
    else:
        click.echo(formatted_output)
    
    try:
        token_usage = token_tracker.get_usage_report()
        click.echo("\nToken Usage:")
        for provider, usage in token_usage.items():
            click.echo(f"{provider}: {usage.get('total', 0)} tokens")
    except Exception as e:
        click.echo(f"Warning: Could not get token usage report: {str(e)}")
    
    return 0

@cli.command()
@click.argument("expectation_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.option("--format", "-f", type=click.Choice(["text", "json", "yaml"]), default="text", help="Output format")
def generate(expectation_file, output, format):
    """Generate code from an expectation file"""
    click.echo("Generating code...")
    
    try:
        with open(expectation_file, "r") as f:
            if expectation_file.endswith(".json"):
                expectation = json.load(f)
            elif expectation_file.endswith(".yaml") or expectation_file.endswith(".yml"):
                import yaml
                expectation = yaml.safe_load(f)
            else:
                click.echo("Error: Expectation file must be JSON or YAML")
                return 1
    except Exception as e:
        click.echo(f"Error reading expectation file: {str(e)}")
        return 1
    
    try:
        with token_tracker.track("generate"):
            result = expeta.generator.generate(expectation)
            expeta.generator.sync_to_memory(expeta.memory_system)
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return 1
    
    if not result:
        click.echo("Error: Failed to generate code")
        return 1
    
    formatted_output = format_output(result, format)
    
    if output:
        try:
            with open(output, "w") as f:
                f.write(formatted_output)
            click.echo(f"Results written to {output}")
        except Exception as e:
            click.echo(f"Error writing to file: {str(e)}")
            return 1
    else:
        click.echo(formatted_output)
    
    try:
        token_usage = token_tracker.get_usage_report()
        click.echo("\nToken Usage:")
        for provider, usage in token_usage.items():
            click.echo(f"{provider}: {usage.get('total', 0)} tokens")
    except Exception as e:
        click.echo(f"Warning: Could not get token usage report: {str(e)}")
    
    return 0

@cli.command()
@click.argument("code_file", type=click.Path(exists=True))
@click.argument("expectation_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.option("--format", "-f", type=click.Choice(["text", "json", "yaml"]), default="text", help="Output format")
def validate(code_file, expectation_file, output, format):
    """Validate code against an expectation"""
    click.echo("Validating code...")
    
    try:
        with open(code_file, "r") as f:
            if code_file.endswith(".json"):
                code = json.load(f)
            elif code_file.endswith(".yaml") or code_file.endswith(".yml"):
                import yaml
                code = yaml.safe_load(f)
            else:
                code = {
                    "language": "python",  # Guess language from extension
                    "files": [
                        {
                            "path": os.path.basename(code_file),
                            "content": f.read()
                        }
                    ]
                }
    except Exception as e:
        click.echo(f"Error reading code file: {str(e)}")
        return 1
    
    try:
        with open(expectation_file, "r") as f:
            if expectation_file.endswith(".json"):
                expectation = json.load(f)
            elif expectation_file.endswith(".yaml") or expectation_file.endswith(".yml"):
                import yaml
                expectation = yaml.safe_load(f)
            else:
                click.echo("Error: Expectation file must be JSON or YAML")
                return 1
    except Exception as e:
        click.echo(f"Error reading expectation file: {str(e)}")
        return 1
    
    try:
        with token_tracker.track("validate"):
            result = expeta.validator.validate(code, expectation)
            expeta.validator.sync_to_memory(expeta.memory_system)
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return 1
    
    if not result:
        click.echo("Error: Failed to validate code")
        return 1
    
    formatted_output = format_output(result, format)
    
    if output:
        try:
            with open(output, "w") as f:
                f.write(formatted_output)
            click.echo(f"Results written to {output}")
        except Exception as e:
            click.echo(f"Error writing to file: {str(e)}")
            return 1
    else:
        click.echo(formatted_output)
    
    try:
        token_usage = token_tracker.get_usage_report()
        click.echo("\nToken Usage:")
        for provider, usage in token_usage.items():
            click.echo(f"{provider}: {usage.get('total', 0)} tokens")
    except Exception as e:
        click.echo(f"Warning: Could not get token usage report: {str(e)}")
    
    return 0

@cli.command()
@click.argument("expectation_id", required=True)
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.option("--format", "-f", type=click.Choice(["text", "json", "yaml"]), default="text", help="Output format")
def get_expectation(expectation_id, output, format):
    """Get expectation by ID"""
    click.echo(f"Getting expectation {expectation_id}...")
    
    try:
        result = expeta.memory_system.get_expectation(expectation_id)
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return 1
    
    if not result:
        click.echo(f"Error: Expectation {expectation_id} not found")
        return 1
    
    formatted_output = format_output(result, format)
    
    if output:
        try:
            with open(output, "w") as f:
                f.write(formatted_output)
            click.echo(f"Results written to {output}")
        except Exception as e:
            click.echo(f"Error writing to file: {str(e)}")
            return 1
    else:
        click.echo(formatted_output)
    
    return 0

@cli.command()
@click.argument("expectation_id", required=True)
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.option("--format", "-f", type=click.Choice(["text", "json", "yaml"]), default="text", help="Output format")
def get_generation(expectation_id, output, format):
    """Get code generation for an expectation"""
    click.echo(f"Getting generation for expectation {expectation_id}...")
    
    try:
        result = expeta.memory_system.get_code_for_expectation(expectation_id)
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return 1
    
    if not result:
        click.echo(f"Error: Generation for expectation {expectation_id} not found")
        return 1
    
    formatted_output = format_output(result, format)
    
    if output:
        try:
            with open(output, "w") as f:
                f.write(formatted_output)
            click.echo(f"Results written to {output}")
        except Exception as e:
            click.echo(f"Error writing to file: {str(e)}")
            return 1
    else:
        click.echo(formatted_output)
    
    return 0

@cli.command()
@click.argument("expectation_id", required=True)
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.option("--format", "-f", type=click.Choice(["text", "json", "yaml"]), default="text", help="Output format")
def get_validation(expectation_id, output, format):
    """Get validation results for an expectation"""
    click.echo(f"Getting validation results for expectation {expectation_id}...")
    
    try:
        result = expeta.memory_system.get_validation_results(expectation_id=expectation_id)
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        return 1
    
    if not result:
        click.echo(f"Error: Validation results for expectation {expectation_id} not found")
        return 1
    
    formatted_output = format_output(result, format)
    
    if output:
        try:
            with open(output, "w") as f:
                f.write(formatted_output)
            click.echo(f"Results written to {output}")
        except Exception as e:
            click.echo(f"Error writing to file: {str(e)}")
            return 1
    else:
        click.echo(formatted_output)
    
    return 0

@cli.command()
def interactive():
    """Start interactive mode"""
    click.echo("Starting interactive mode...")
    click.echo("Type 'exit' to quit")
    click.echo()
    
    while True:
        try:
            requirement = click.prompt("Enter requirement")
        except Exception:
            return 1
        
        if requirement.lower() == "exit":
            break
        
        click.echo("Processing requirement...")
        
        try:
            with token_tracker.track("process"):
                result = expeta.process_requirement(requirement)
        except Exception as e:
            click.echo(f"Error: {str(e)}")
            click.echo()
            continue
        
        if not result:
            click.echo("Error: Failed to process requirement")
            click.echo()
            continue
        
        formatted_output = format_output(result, "text")
        click.echo(formatted_output)
        
        try:
            token_usage = token_tracker.get_usage_report()
            click.echo("\nToken Usage:")
            for provider, usage in token_usage.items():
                click.echo(f"{provider}: {usage.get('total', 0)} tokens")
        except Exception as e:
            click.echo(f"Warning: Could not get token usage report: {str(e)}")
        
        click.echo()
    
    return 0

def format_output(data, format_type):
    """Format output based on format type
    
    Args:
        data: Data to format
        format_type: Format type (text, json, yaml)
        
    Returns:
        Formatted output string
    """
    if format_type == "json":
        return json.dumps(data, indent=2)
    elif format_type == "yaml":
        import yaml
        return yaml.dump(data, default_flow_style=False)
    else:  # text
        return format_as_text(data)

def format_as_text(data, indent=0):
    """Format data as text
    
    Args:
        data: Data to format
        indent: Indentation level
        
    Returns:
        Formatted text string
    """
    if data is None:
        return "None"
    
    if isinstance(data, str):
        return data
    
    if isinstance(data, (int, float, bool)):
        return str(data)
    
    if isinstance(data, list):
        if not data:
            return "[]"
        
        result = ""
        for item in data:
            result += "\n" + " " * indent + "- " + format_as_text(item, indent + 2).lstrip()
        return result
    
    if isinstance(data, dict):
        if not data:
            return "{}"
        
        result = ""
        for key, value in data.items():
            formatted_value = format_as_text(value, indent + 2)
            if "\n" in formatted_value:
                result += "\n" + " " * indent + f"{key}:" + formatted_value
            else:
                result += "\n" + " " * indent + f"{key}: {formatted_value}"
        return result
    
    return str(data)

if __name__ == "__main__":
    cli()
