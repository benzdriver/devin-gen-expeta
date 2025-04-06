"""
Mock Data Module for Expeta 2.0

This module provides mock data for testing the Expeta system without LLM providers.
"""

def get_mock_requirement_result(requirement_text):
    """Get mock result for requirement processing
    
    Args:
        requirement_text: Natural language requirement text
        
    Returns:
        Mock processing results
    """
    function_name = "process_data"
    if "factorial" in requirement_text.lower():
        function_name = "factorial"
    elif "add" in requirement_text.lower():
        function_name = "add_numbers"
    elif "reverse" in requirement_text.lower():
        function_name = "reverse_string"
        
    return {
        "requirement": requirement_text,
        "clarification": {
            "top_level_expectation": {
                "name": f"{function_name.title()} Function Implementation",
                "description": f"A function that implements {function_name} functionality"
            },
            "sub_expectations": [
                {"name": "Input Validation"}, 
                {"name": f"{function_name.title()} Implementation"}, 
                {"name": "Error Handling"}
            ]
        },
        "generation": {
            "generated_code": {
                "language": "python",
                "files": [
                    {
                        "path": f"{function_name}.py",
                        "content": f"def {function_name}(a, b=None):\n    \"\"\"Implementation of {function_name} function\"\"\"\n    if b is None:\n        # Handle single argument case\n        return process_single_arg(a)\n    return a + b if b is not None else a"
                    }
                ]
            }
        },
        "validation": {
            "passed": True,
            "semantic_match": {"match_score": 0.95},
            "test_results": {"pass_rate": 1.0}
        },
        "success": True
    }

def get_mock_expectation_result(expectation):
    """Get mock result for expectation processing
    
    Args:
        expectation: Expectation dictionary
        
    Returns:
        Mock processing results
    """
    function_name = expectation.get("name", "process_data").lower().replace(" ", "_")
    
    return {
        "expectation": expectation,
        "generation": {
            "generated_code": {
                "language": "python",
                "files": [
                    {
                        "path": f"{function_name}.py",
                        "content": f"def {function_name}(data):\n    \"\"\"Implementation of {function_name} function\"\"\"\n    # Process data according to expectation\n    result = process_data_for_expectation(data)\n    return result"
                    }
                ]
            }
        },
        "validation": {
            "passed": True,
            "semantic_match": {"match_score": 0.98},
            "test_results": {"pass_rate": 1.0}
        },
        "success": True,
        "clarification": {
            "top_level_expectation": expectation,
            "sub_expectations": [
                {"name": "Input Validation"}, 
                {"name": f"{function_name.title()} Implementation"}, 
                {"name": "Error Handling"}
            ]
        }
    }
