"""
Unit tests for Event Bus
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, call

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from event_system.event_bus import EventBus

class TestEventBus(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.registry = MagicMock()
        self.event_bus = EventBus(registry=self.registry)
    
    def test_publish(self):
        """Test publishing an event"""
        self.registry.validate_event.return_value = True
        
        handler1 = MagicMock()
        handler2 = MagicMock()
        self.registry.get_handlers.return_value = {
            "handler1": handler1,
            "handler2": handler2
        }
        
        event_data = {"key": "value"}
        result = self.event_bus.publish("test.event", event_data)
        
        self.assertTrue(result)
        
        self.registry.validate_event.assert_called_once_with("test.event", event_data)
        self.registry.get_handlers.assert_called_once_with("test.event")
        
        handler1.assert_called_once()
        handler2.assert_called_once()
        
        self.assertEqual(handler1.call_args[0][0]["type"], "test.event")
        self.assertEqual(handler1.call_args[0][0]["data"]["key"], "value")
        self.assertEqual(handler2.call_args[0][0]["type"], "test.event")
        self.assertEqual(handler2.call_args[0][0]["data"]["key"], "value")
    
    def test_publish_invalid_event(self):
        """Test publishing an invalid event"""
        self.registry.validate_event.return_value = False
        
        event_data = {"key": "value"}
        result = self.event_bus.publish("test.event", event_data)
        
        self.assertFalse(result)
        
        self.registry.validate_event.assert_called_once_with("test.event", event_data)
        
        self.registry.get_handlers.assert_not_called()
    
    def test_publish_no_handlers(self):
        """Test publishing an event with no handlers"""
        self.registry.validate_event.return_value = True
        
        self.registry.get_handlers.return_value = {}
        
        event_data = {"key": "value"}
        result = self.event_bus.publish("test.event", event_data)
        
        self.assertTrue(result)
        
        self.registry.validate_event.assert_called_once_with("test.event", event_data)
        self.registry.get_handlers.assert_called_once_with("test.event")
    
    def test_publish_handler_exception(self):
        """Test publishing an event where a handler raises an exception"""
        self.registry.validate_event.return_value = True
        
        handler1 = MagicMock()
        handler2 = MagicMock(side_effect=Exception("Test exception"))
        handler3 = MagicMock()
        self.registry.get_handlers.return_value = {
            "handler1": handler1,
            "handler2": handler2,
            "handler3": handler3
        }
        
        event_data = {"key": "value"}
        result = self.event_bus.publish("test.event", event_data)
        
        self.assertTrue(result)
        
        self.registry.validate_event.assert_called_once_with("test.event", event_data)
        self.registry.get_handlers.assert_called_once_with("test.event")
        
        handler1.assert_called_once()
        handler2.assert_called_once()
        handler3.assert_called_once()
    
    def test_subscribe(self):
        """Test subscribing to an event"""
        self.registry.register_handler.return_value = "handler-id"
        
        handler = MagicMock()
        handler_id = self.event_bus.subscribe("test.event", handler)
        
        self.assertEqual(handler_id, "handler-id")
        
        self.registry.register_handler.assert_called_once_with("test.event", handler, None)
    
    def test_subscribe_with_id(self):
        """Test subscribing to an event with a specific handler ID"""
        self.registry.register_handler.return_value = "custom-id"
        
        handler = MagicMock()
        handler_id = self.event_bus.subscribe("test.event", handler, "custom-id")
        
        self.assertEqual(handler_id, "custom-id")
        
        self.registry.register_handler.assert_called_once_with("test.event", handler, "custom-id")
    
    def test_unsubscribe(self):
        """Test unsubscribing from an event"""
        self.registry.unregister_handler.return_value = True
        
        result = self.event_bus.unsubscribe("test.event", "handler-id")
        
        self.assertTrue(result)
        
        self.registry.unregister_handler.assert_called_once_with("test.event", "handler-id")
    
    def test_unsubscribe_failure(self):
        """Test unsubscribing from an event that fails"""
        self.registry.unregister_handler.return_value = False
        
        result = self.event_bus.unsubscribe("test.event", "handler-id")
        
        self.assertFalse(result)
        
        self.registry.unregister_handler.assert_called_once_with("test.event", "handler-id")
    
    def test_publish_async(self):
        """Test publishing an event asynchronously"""
        self.registry.validate_event.return_value = True
        
        handler1 = MagicMock()
        handler2 = MagicMock()
        self.registry.get_handlers.return_value = {
            "handler1": handler1,
            "handler2": handler2
        }
        
        with patch('event_system.event_bus.threading.Thread') as mock_thread:
            event_data = {"key": "value"}
            result = self.event_bus.publish_async("test.event", event_data)
            
            self.assertTrue(result)
            
            self.registry.validate_event.assert_called_once_with("test.event", event_data)
            self.registry.get_handlers.assert_called_once_with("test.event")
            
            mock_thread.assert_called_once()
            mock_thread.return_value.start.assert_called_once()
    
    def test_publish_async_invalid_event(self):
        """Test publishing an invalid event asynchronously"""
        self.registry.validate_event.return_value = False
        
        with patch('event_system.event_bus.threading.Thread') as mock_thread:
            event_data = {"key": "value"}
            result = self.event_bus.publish_async("test.event", event_data)
            
            self.assertFalse(result)
            
            self.registry.validate_event.assert_called_once_with("test.event", event_data)
            
            mock_thread.assert_not_called()
    
    def test_register_event_type(self):
        """Test registering an event type"""
        self.registry.register_event_type.return_value = True
        
        schema = {"type": "object"}
        result = self.event_bus.register_event_type("test.event", schema)
        
        self.assertTrue(result)
        
        self.registry.register_event_type.assert_called_once_with("test.event", schema)
    
    def test_register_event_type_failure(self):
        """Test registering an event type that fails"""
        self.registry.register_event_type.return_value = False
        
        schema = {"type": "object"}
        result = self.event_bus.register_event_type("test.event", schema)
        
        self.assertFalse(result)
        
        self.registry.register_event_type.assert_called_once_with("test.event", schema)
    
    def test_get_event_types(self):
        """Test getting all event types"""
        event_types = {
            "event1": {"type": "event1"},
            "event2": {"type": "event2"}
        }
        self.registry.get_all_event_types.return_value = event_types
        
        result = self.event_bus.get_event_types()
        
        self.assertEqual(result, event_types)
        
        self.registry.get_all_event_types.assert_called_once()
    
    def test_get_handlers(self):
        """Test getting all handlers"""
        handlers = {
            "event1": {"handler1": MagicMock()},
            "event2": {"handler2": MagicMock()}
        }
        self.registry.get_all_handlers.return_value = handlers
        
        result = self.event_bus.get_handlers()
        
        self.assertEqual(result, handlers)
        
        self.registry.get_all_handlers.assert_called_once()
    
    def test_get_handlers_for_event(self):
        """Test getting handlers for a specific event"""
        handlers = {
            "handler1": MagicMock(),
            "handler2": MagicMock()
        }
        self.registry.get_handlers.return_value = handlers
        
        result = self.event_bus.get_handlers_for_event("test.event")
        
        self.assertEqual(result, handlers)
        
        self.registry.get_handlers.assert_called_once_with("test.event")

if __name__ == "__main__":
    unittest.main()
