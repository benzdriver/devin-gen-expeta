"""
Unit tests for Chat Interface Access Layer
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from access.chat.src.chat_interface import ChatInterface, DialogManager, ContextTracker

class TestChatInterface(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.chat_interface = ChatInterface()
    
    @patch('access.chat.src.chat_interface.expeta')
    def test_initialization(self, mock_expeta):
        """Test chat interface initialization"""
        chat = ChatInterface()
        self.assertIsNotNone(chat.dialog_manager)
        self.assertIsNotNone(chat.context_tracker)
        self.assertEqual(chat.config["llm_router"]["default_provider"], "anthropic")
    
    @patch('access.chat.src.chat_interface.expeta')
    def test_process_message(self, mock_expeta):
        """Test processing a chat message"""
        mock_clarifier = MagicMock()
        mock_expeta.clarifier = mock_clarifier
        
        mock_result = {
            "response": "I'll help you create a user authentication system.",
            "expectation": {
                "id": "exp-12345678",
                "name": "User Authentication",
                "description": "A system for user authentication"
            }
        }
        mock_clarifier.process_chat_message.return_value = mock_result
        
        result = self.chat_interface.process_message(
            "Create a user authentication system",
            user_id="user123",
            session_id="session456"
        )
        
        self.assertEqual(result["response"], "I'll help you create a user authentication system.")
        self.assertEqual(result["expectation"]["id"], "exp-12345678")
        mock_clarifier.process_chat_message.assert_called_once()
    
    @patch('access.chat.src.chat_interface.expeta')
    def test_continue_conversation(self, mock_expeta):
        """Test continuing a conversation"""
        mock_clarifier = MagicMock()
        mock_expeta.clarifier = mock_clarifier
        
        mock_result = {
            "response": "I'll add password reset functionality to the authentication system.",
            "updated_expectation": {
                "id": "exp-12345678",
                "name": "User Authentication",
                "description": "A system for user authentication with password reset"
            }
        }
        mock_clarifier.continue_conversation.return_value = mock_result
        
        result = self.chat_interface.continue_conversation(
            "Can you add password reset functionality?",
            user_id="user123",
            session_id="session456"
        )
        
        self.assertEqual(result["response"], "I'll add password reset functionality to the authentication system.")
        self.assertEqual(result["updated_expectation"]["id"], "exp-12345678")
        mock_clarifier.continue_conversation.assert_called_once()
    
    @patch('access.chat.src.chat_interface.expeta')
    def test_generate_from_chat(self, mock_expeta):
        """Test generating code from chat"""
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
        
        result = self.chat_interface.generate_from_chat(
            expectation_id="exp-12345678",
            user_id="user123",
            session_id="session456"
        )
        
        self.assertEqual(result["generated_code"]["language"], "python")
        self.assertEqual(len(result["generated_code"]["files"]), 1)
        mock_generator.generate.assert_called_once()
    
    def test_session_management(self):
        """Test session management"""
        session_id = self.chat_interface.create_session(user_id="user123")
        self.assertIsNotNone(session_id)
        
        session = self.chat_interface.get_session(session_id)
        self.assertIsNotNone(session)
        self.assertEqual(session["user_id"], "user123")
        
        result = self.chat_interface.end_session(session_id)
        self.assertTrue(result)
        
        session = self.chat_interface.get_session(session_id)
        self.assertIsNone(session)
    
    @patch('access.chat.src.chat_interface.TokenTracker')
    def test_token_tracking(self, mock_token_tracker):
        """Test token tracking"""
        mock_tracker_instance = MagicMock()
        mock_token_tracker.return_value = mock_tracker_instance
        
        chat = ChatInterface()
        
        with patch('access.chat.src.chat_interface.expeta'):
            chat.process_message(
                "Create a user authentication system",
                user_id="user123",
                session_id="session456"
            )
        
        mock_tracker_instance.track.assert_called()
        mock_tracker_instance.get_usage_report.assert_called()


class TestDialogManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.dialog_manager = DialogManager()
    
    def test_create_dialog(self):
        """Test creating a dialog"""
        dialog_id = self.dialog_manager.create_dialog(user_id="user123")
        self.assertIsNotNone(dialog_id)
        
        dialog = self.dialog_manager.get_dialog(dialog_id)
        self.assertIsNotNone(dialog)
        self.assertEqual(dialog["user_id"], "user123")
        self.assertEqual(len(dialog["messages"]), 0)
    
    def test_add_message(self):
        """Test adding a message to a dialog"""
        dialog_id = self.dialog_manager.create_dialog(user_id="user123")
        
        self.dialog_manager.add_message(
            dialog_id,
            "user",
            "Create a user authentication system"
        )
        
        dialog = self.dialog_manager.get_dialog(dialog_id)
        self.assertEqual(len(dialog["messages"]), 1)
        self.assertEqual(dialog["messages"][0]["role"], "user")
        self.assertEqual(dialog["messages"][0]["content"], "Create a user authentication system")
    
    def test_get_messages(self):
        """Test getting messages from a dialog"""
        dialog_id = self.dialog_manager.create_dialog(user_id="user123")
        
        self.dialog_manager.add_message(dialog_id, "user", "Hello")
        self.dialog_manager.add_message(dialog_id, "assistant", "Hi there")
        self.dialog_manager.add_message(dialog_id, "user", "How are you?")
        
        messages = self.dialog_manager.get_messages(dialog_id)
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[0]["content"], "Hello")
        self.assertEqual(messages[1]["content"], "Hi there")
        self.assertEqual(messages[2]["content"], "How are you?")
    
    def test_clear_dialog(self):
        """Test clearing a dialog"""
        dialog_id = self.dialog_manager.create_dialog(user_id="user123")
        
        self.dialog_manager.add_message(dialog_id, "user", "Hello")
        self.dialog_manager.add_message(dialog_id, "assistant", "Hi there")
        
        self.dialog_manager.clear_dialog(dialog_id)
        
        dialog = self.dialog_manager.get_dialog(dialog_id)
        self.assertEqual(len(dialog["messages"]), 0)


class TestContextTracker(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.context_tracker = ContextTracker()
    
    def test_create_context(self):
        """Test creating a context"""
        context_id = self.context_tracker.create_context(user_id="user123")
        self.assertIsNotNone(context_id)
        
        context = self.context_tracker.get_context(context_id)
        self.assertIsNotNone(context)
        self.assertEqual(context["user_id"], "user123")
        self.assertEqual(len(context["entities"]), 0)
    
    def test_add_entity(self):
        """Test adding an entity to context"""
        context_id = self.context_tracker.create_context(user_id="user123")
        
        self.context_tracker.add_entity(
            context_id,
            entity_type="expectation",
            entity_id="exp-12345678",
            entity_data={
                "name": "User Authentication",
                "description": "A system for user authentication"
            }
        )
        
        context = self.context_tracker.get_context(context_id)
        self.assertEqual(len(context["entities"]), 1)
        self.assertEqual(context["entities"][0]["type"], "expectation")
        self.assertEqual(context["entities"][0]["id"], "exp-12345678")
    
    def test_update_entity(self):
        """Test updating an entity in context"""
        context_id = self.context_tracker.create_context(user_id="user123")
        
        self.context_tracker.add_entity(
            context_id,
            entity_type="expectation",
            entity_id="exp-12345678",
            entity_data={
                "name": "User Authentication",
                "description": "A system for user authentication"
            }
        )
        
        self.context_tracker.update_entity(
            context_id,
            entity_id="exp-12345678",
            entity_data={
                "name": "User Authentication",
                "description": "A system for user authentication with password reset"
            }
        )
        
        context = self.context_tracker.get_context(context_id)
        self.assertEqual(context["entities"][0]["data"]["description"], 
                         "A system for user authentication with password reset")
    
    def test_get_entity(self):
        """Test getting an entity from context"""
        context_id = self.context_tracker.create_context(user_id="user123")
        
        self.context_tracker.add_entity(
            context_id,
            entity_type="expectation",
            entity_id="exp-12345678",
            entity_data={
                "name": "User Authentication",
                "description": "A system for user authentication"
            }
        )
        
        entity = self.context_tracker.get_entity(context_id, "exp-12345678")
        self.assertIsNotNone(entity)
        self.assertEqual(entity["type"], "expectation")
        self.assertEqual(entity["id"], "exp-12345678")
        self.assertEqual(entity["data"]["name"], "User Authentication")
    
    def test_remove_entity(self):
        """Test removing an entity from context"""
        context_id = self.context_tracker.create_context(user_id="user123")
        
        self.context_tracker.add_entity(
            context_id,
            entity_type="expectation",
            entity_id="exp-12345678",
            entity_data={}
        )
        
        self.context_tracker.remove_entity(context_id, "exp-12345678")
        
        context = self.context_tracker.get_context(context_id)
        self.assertEqual(len(context["entities"]), 0)


if __name__ == "__main__":
    unittest.main()
