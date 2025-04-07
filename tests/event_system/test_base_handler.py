"""
Unit tests for Base Event Handler
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from event_system.handlers.base_handler import BaseEventHandler

class TestBaseEventHandler(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.event_bus = MagicMock()
        self.handler = BaseEventHandler(event_bus=self.event_bus)
    
    def test_handle_event(self):
        """Test handling an event"""
        class TestHandler(BaseEventHandler):
            def handle_test_event(self, event):
                return {"result": "success"}
        
        test_handler = TestHandler(event_bus=self.event_bus)
        
        event = {"type": "test_event", "data": {"key": "value"}}
        result = test_handler.handle_event(event)
        
        self.assertEqual(result, {"result": "success"})
    
    def test_handle_event_no_handler(self):
        """Test handling an event with no handler method"""
        event = {"type": "unknown_event", "data": {"key": "value"}}
        result = self.handler.handle_event(event)
        
        self.assertIsNone(result)
    
    def test_handle_event_exception(self):
        """Test handling an event that raises an exception"""
        class TestHandler(BaseEventHandler):
            def handle_test_event(self, event):
                raise ValueError("Test exception")
        
        test_handler = TestHandler(event_bus=self.event_bus)
        
        event = {"type": "test_event", "data": {"key": "value"}}
        result = test_handler.handle_event(event)
        
        self.assertEqual(result, {"error": "Test exception"})
        
        self.event_bus.publish.assert_called_once_with("system.error", {
            "source": "TestHandler",
            "error": "Test exception",
            "original_event": event
        })
    
    def test_get_handler_method(self):
        """Test getting handler method for event type"""
        class TestHandler(BaseEventHandler):
            def handle_test_event(self, event):
                return {"result": "success"}
            
            def handle_test_nested_event(self, event):
                return {"result": "nested"}
        
        test_handler = TestHandler()
        
        handler_method = test_handler._get_handler_method("test_event")
        
        self.assertEqual(handler_method.__name__, "handle_test_event")
        
        handler_method = test_handler._get_handler_method("test.nested.event")
        
        self.assertEqual(handler_method.__name__, "handle_test_nested_event")
        
        handler_method = test_handler._get_handler_method("unknown_event")
        
        self.assertIsNone(handler_method)
    
    def test_publish_error_event(self):
        """Test publishing error event"""
        event = {"type": "test_event", "data": {"key": "value"}}
        self.handler._publish_error_event(event, "Test error")
        
        self.event_bus.publish.assert_called_once_with("system.error", {
            "source": "BaseEventHandler",
            "error": "Test error",
            "original_event": event
        })
        
        handler = BaseEventHandler()
        handler._publish_error_event(event, "Test error")
        

if __name__ == "__main__":
    unittest.main()
