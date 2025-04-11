"""
Simple test for the Clarifier conversation recovery functionality.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from clarifier.clarifier import Clarifier
from tests.clarifier.mock_llm_router import MockLLMRouter


class TestClarifierRecovery(unittest.TestCase):
    """Test the conversation recovery in the Clarifier component."""

    @patch('clarifier.clarifier.Clarifier._extract_top_level_expectation')
    @patch('clarifier.clarifier.Clarifier._detect_uncertainty')
    def test_conversation_recovery_behavior(self, mock_detect, mock_extract):
        """Test that the Clarifier now creates a new conversation when ID is not found."""
        mock_router = MockLLMRouter()
        mock_extract.return_value = {"name": "Test Expectation", "id": "test-id"}
        mock_detect.return_value = []
        
        clarifier = Clarifier(llm_router=mock_router)
        
        self.assertEqual(len(clarifier._active_conversations), 0)
        
        test_id = "test_recovery_id"
        
        try:
            result = clarifier.continue_conversation(test_id, "Test message")
            self.assertNotEqual(result.get("error", None), "No active conversation found with this ID")
            print(f"Test passed: Clarifier now creates a new conversation when ID is not found")
        except Exception as e:
            self.fail(f"Clarifier raised an exception: {str(e)}")


if __name__ == "__main__":
    print("Running Clarifier recovery test...")
    unittest.main()
