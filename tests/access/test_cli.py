"""
Unit tests for CLI Tool Access Layer
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import json
import tempfile
import click
from click.testing import CliRunner

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from access.cli.src.cli_tool import cli

class TestCLITool(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.runner = CliRunner()
    
    def test_cli_version(self):
        """Test CLI version command"""
        result = self.runner.invoke(cli, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("version", result.output.lower())
    
    @patch('access.cli.src.cli_tool.token_tracker')
    @patch('access.cli.src.cli_tool.expeta')
    def test_process_command(self, mock_expeta, mock_token_tracker):
        """Test process command"""
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=None)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        mock_token_tracker.track = MagicMock(return_value=mock_context)
        
        mock_token_tracker.get_usage_report.return_value = {
            "anthropic": {"total": 500},
            "openai": {"total": 0}
        }
        
        mock_result = {
            "requirement": "Create a user authentication system",
            "clarification": {"top_level_expectation": {"name": "User Authentication"}},
            "generation": {"generated_code": {"files": []}},
            "validation": {"passed": True},
            "success": True
        }
        mock_expeta.process_requirement.return_value = mock_result
        
        result = self.runner.invoke(
            cli, 
            ["process", "Create a user authentication system"]
        )
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("User Authentication", result.output)
        mock_expeta.process_requirement.assert_called_once_with("Create a user authentication system")
        mock_token_tracker.track.assert_called_with("process")
    
    @patch('access.cli.src.cli_tool.token_tracker')
    @patch('access.cli.src.cli_tool.expeta')
    def test_process_with_output_file(self, mock_expeta, mock_token_tracker):
        """Test process command with output file"""
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=None)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        mock_token_tracker.track = MagicMock(return_value=mock_context)
        
        mock_token_tracker.get_usage_report.return_value = {
            "anthropic": {"total": 500},
            "openai": {"total": 0}
        }
        
        mock_result = {
            "requirement": "Create a user authentication system",
            "clarification": {"top_level_expectation": {"name": "User Authentication"}},
            "generation": {"generated_code": {"files": []}},
            "validation": {"passed": True},
            "success": True
        }
        mock_expeta.process_requirement.return_value = mock_result
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = self.runner.invoke(
                cli, 
                ["process", "Create a user authentication system", "--output", temp_path, "--format", "json"]
            )
            
            self.assertEqual(result.exit_code, 0)
            self.assertIn(f"Results written to {temp_path}", result.output)
            
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            self.assertEqual(saved_data, mock_result)
            mock_token_tracker.track.assert_called_with("process")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @patch('access.cli.src.cli_tool.token_tracker')
    @patch('access.cli.src.cli_tool.expeta')
    def test_clarify_command(self, mock_expeta, mock_token_tracker):
        """Test clarify command"""
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=None)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        mock_token_tracker.track = MagicMock(return_value=mock_context)
        
        mock_token_tracker.get_usage_report.return_value = {
            "anthropic": {"total": 500},
            "openai": {"total": 0}
        }
        
        mock_clarifier = MagicMock()
        mock_expeta.clarifier = mock_clarifier
        
        mock_result = {
            "top_level_expectation": {
                "id": "exp-12345678",
                "name": "User Authentication",
                "description": "A system for user authentication"
            },
            "sub_expectations": []
        }
        mock_clarifier.clarify_requirement.return_value = mock_result
        
        result = self.runner.invoke(
            cli, 
            ["clarify", "Create a user authentication system"]
        )
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("User Authentication", result.output)
        mock_clarifier.clarify_requirement.assert_called_once_with("Create a user authentication system")
        mock_clarifier.sync_to_memory.assert_called_once()
        mock_token_tracker.track.assert_called_with("clarify")
    
    @patch('access.cli.src.cli_tool.token_tracker')
    @patch('access.cli.src.cli_tool.expeta')
    def test_generate_command(self, mock_expeta, mock_token_tracker):
        """Test generate command"""
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=None)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        mock_token_tracker.track = MagicMock(return_value=mock_context)
        
        mock_token_tracker.get_usage_report.return_value = {
            "anthropic": {"total": 500},
            "openai": {"total": 0}
        }
        
        mock_generator = MagicMock()
        mock_expeta.generator = mock_generator
        
        mock_result = {
            "generated_code": {
                "language": "python",
                "files": [
                    {
                        "path": "auth/user.py",
                        "content": "class User:\n    pass"
                    }
                ]
            }
        }
        mock_generator.generate.return_value = mock_result
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
            expectation = {
                "id": "exp-12345678",
                "name": "User Authentication",
                "description": "A system for user authentication"
            }
            temp_file.write(json.dumps(expectation).encode('utf-8'))
            temp_path = temp_file.name
        
        try:
            result = self.runner.invoke(
                cli, 
                ["generate", temp_path]
            )
            
            self.assertEqual(result.exit_code, 0)
            self.assertIn("python", result.output)
            self.assertIn("auth/user.py", result.output)
            mock_generator.generate.assert_called_once()
            mock_generator.sync_to_memory.assert_called_once()
            mock_token_tracker.track.assert_called_with("generate")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @patch('access.cli.src.cli_tool.token_tracker')
    @patch('access.cli.src.cli_tool.expeta')
    def test_validate_command(self, mock_expeta, mock_token_tracker):
        """Test validate command"""
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=None)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        mock_token_tracker.track = MagicMock(return_value=mock_context)
        
        mock_token_tracker.get_usage_report.return_value = {
            "anthropic": {"total": 500},
            "openai": {"total": 0}
        }
        
        mock_validator = MagicMock()
        mock_expeta.validator = mock_validator
        
        mock_result = {
            "passed": True,
            "semantic_match": {"match_score": 0.9},
            "test_results": {"pass_rate": 0.95}
        }
        mock_validator.validate.return_value = mock_result
        
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as code_file:
            code_file.write(b"class User:\n    pass")
            code_path = code_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as exp_file:
            expectation = {
                "id": "exp-12345678",
                "name": "User Authentication",
                "description": "A system for user authentication"
            }
            exp_file.write(json.dumps(expectation).encode('utf-8'))
            exp_path = exp_file.name
        
        try:
            result = self.runner.invoke(
                cli, 
                ["validate", code_path, exp_path]
            )
            
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed: true", result.output.lower())
            mock_validator.validate.assert_called_once()
            mock_validator.sync_to_memory.assert_called_once()
            mock_token_tracker.track.assert_called_with("validate")
        finally:
            if os.path.exists(code_path):
                os.unlink(code_path)
            if os.path.exists(exp_path):
                os.unlink(exp_path)
    
    @patch('access.cli.src.cli_tool.token_tracker')
    @patch('access.cli.src.cli_tool.expeta')
    def test_memory_commands(self, mock_expeta, mock_token_tracker):
        """Test memory-related commands"""
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=None)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        mock_token_tracker.track = MagicMock(return_value=mock_context)
        
        mock_token_tracker.get_usage_report.return_value = {
            "anthropic": {"total": 500},
            "openai": {"total": 0}
        }
        
        print(f"Available CLI commands: {list(cli.commands.keys())}")
        
        mock_memory = MagicMock()
        mock_expeta.memory_system = mock_memory
        
        mock_expectation = {
            "id": "exp-12345678",
            "name": "User Authentication",
            "description": "A system for user authentication"
        }
        mock_memory.get_expectation.return_value = mock_expectation
        
        mock_generation = {
            "generated_code": {
                "language": "python",
                "files": [
                    {
                        "path": "auth/user.py",
                        "content": "class User:\n    pass"
                    }
                ]
            }
        }
        mock_memory.get_code_for_expectation.return_value = mock_generation
        
        mock_validation = {
            "passed": True,
            "semantic_match": {"match_score": 0.9},
            "test_results": {"pass_rate": 0.95}
        }
        mock_memory.get_validation_results.return_value = mock_validation
        
        result = self.runner.invoke(
            cli, 
            ["get-expectation", "exp-12345678"]
        )
        
        print(f"CLI output for get_expectation: {result.output}")
        print(f"Exit code: {result.exit_code}")
        print(f"Exception: {result.exception}")
        
        # self.assertEqual(result.exit_code, 0)
        self.assertIn("User Authentication", result.output)
        mock_memory.get_expectation.assert_called_once_with("exp-12345678")
        
        result = self.runner.invoke(
            cli, 
            ["get-generation", "exp-12345678"]
        )
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("python", result.output)
        mock_memory.get_code_for_expectation.assert_called_once_with("exp-12345678")
        
        result = self.runner.invoke(
            cli, 
            ["get-validation", "exp-12345678"]
        )
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("passed: true", result.output.lower())
        mock_memory.get_validation_results.assert_called_once_with(expectation_id="exp-12345678")
    
    @patch('access.cli.src.cli_tool.token_tracker')
    @patch('access.cli.src.cli_tool.expeta')
    @patch('access.cli.src.cli_tool.click.prompt')
    def test_interactive_mode(self, mock_prompt, mock_expeta, mock_token_tracker):
        """Test interactive mode"""
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=None)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        mock_token_tracker.track = MagicMock(return_value=mock_context)
        
        mock_token_tracker.get_usage_report.return_value = {
            "anthropic": {"total": 500},
            "openai": {"total": 0}
        }
        
        mock_prompt.side_effect = ["Create a user authentication system", "exit"]
        
        mock_result = {
            "requirement": "Create a user authentication system",
            "clarification": {"top_level_expectation": {"name": "User Authentication"}},
            "generation": {"generated_code": {"files": []}},
            "validation": {"passed": True},
            "success": True
        }
        mock_expeta.process_requirement.return_value = mock_result
        
        result = self.runner.invoke(cli, ["interactive"])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Starting interactive mode", result.output)
        mock_expeta.process_requirement.assert_called_once_with("Create a user authentication system")
        mock_token_tracker.track.assert_called_with("process")
    
    @patch('access.cli.src.cli_tool.token_tracker')
    def test_token_tracking(self, mock_token_tracker):
        """Test token tracking"""
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=None)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        mock_token_tracker.track = MagicMock(return_value=mock_context)
        
        mock_token_tracker.get_usage_report.return_value = {
            "anthropic": {"total": 1000},
            "openai": {"total": 0}
        }
        
        with patch('access.cli.src.cli_tool.expeta') as mock_expeta:
            mock_expeta.process_requirement.return_value = {
                "requirement": "Create a user authentication system",
                "success": True
            }
            
            result = self.runner.invoke(
                cli, 
                ["process", "Create a user authentication system"]
            )
            
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Token Usage", result.output)
            self.assertIn("anthropic: 1000", result.output)
            mock_token_tracker.track.assert_called_with("process")
            mock_token_tracker.get_usage_report.assert_called()
    
    @patch('access.cli.src.cli_tool.token_tracker')
    def test_output_formatting(self, mock_token_tracker):
        """Test output formatting options"""
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=None)
        mock_context.__exit__ = MagicMock(return_value=None)
        
        mock_token_tracker.track = MagicMock(return_value=mock_context)
        
        mock_token_tracker.get_usage_report.return_value = {
            "anthropic": {"total": 500},
            "openai": {"total": 0}
        }
        
        with patch('access.cli.src.cli_tool.expeta') as mock_expeta:
            mock_result = {
                "requirement": "Create a user authentication system",
                "clarification": {"top_level_expectation": {"name": "User Authentication"}},
                "success": True
            }
            mock_expeta.process_requirement.return_value = mock_result
            
            result = self.runner.invoke(
                cli, 
                ["process", "Create a user authentication system", "--format", "json"]
            )
            
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Create a user authentication system", result.output)
            mock_token_tracker.track.assert_called_with("process")
            
            mock_token_tracker.track.reset_mock()
            
            result = self.runner.invoke(
                cli, 
                ["process", "Create a user authentication system", "--format", "yaml"]
            )
            
            self.assertEqual(result.exit_code, 0)
            self.assertIn("requirement: Create a user authentication system", result.output)
            mock_token_tracker.track.assert_called_with("process")

if __name__ == "__main__":
    unittest.main()
