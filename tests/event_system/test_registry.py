"""
Unit tests for Event Registry
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from event_system.registry import EventRegistry

class TestEventRegistry(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.registry = EventRegistry()
    
    def test_register_event_type(self):
        """Test registering an event type"""
        schema = {"type": "object"}
        result = self.registry.register_event_type("test.event", schema)
        
        self.assertTrue(result)
        
        self.assertIn("test.event", self.registry.event_types)
        self.assertEqual(self.registry.event_types["test.event"]["schema"], schema)
        
        result = self.registry.register_event_type("test.event", schema)
        self.assertFalse(result)
    
    def test_get_event_type(self):
        """Test getting an event type"""
        schema = {"type": "object"}
        self.registry.register_event_type("test.event", schema)
        
        event_type = self.registry.get_event_type("test.event")
        
        self.assertEqual(event_type["type"], "test.event")
        self.assertEqual(event_type["schema"], schema)
        
        non_existent_event_type = self.registry.get_event_type("non-existent")
        self.assertIsNone(non_existent_event_type)
    
    def test_get_all_event_types(self):
        """Test getting all event types"""
        self.registry.register_event_type("event1", {"type": "object"})
        self.registry.register_event_type("event2", {"type": "object"})
        
        event_types = self.registry.get_all_event_types()
        
        self.assertEqual(len(event_types), 2)
        self.assertIn("event1", event_types)
        self.assertIn("event2", event_types)
    
    def test_register_handler(self):
        """Test registering a handler"""
        handler = MagicMock()
        handler_id = self.registry.register_handler("test.event", handler)
        
        self.assertIsNotNone(handler_id)
        
        self.assertIn("test.event", self.registry.handlers)
        self.assertIn(handler_id, self.registry.handlers["test.event"])
        self.assertEqual(self.registry.handlers["test.event"][handler_id], handler)
        
        custom_id = "custom-id"
        handler2 = MagicMock()
        handler_id2 = self.registry.register_handler("test.event", handler2, custom_id)
        
        self.assertEqual(handler_id2, custom_id)
        
        self.assertIn(custom_id, self.registry.handlers["test.event"])
        self.assertEqual(self.registry.handlers["test.event"][custom_id], handler2)
    
    def test_unregister_handler(self):
        """Test unregistering a handler"""
        handler = MagicMock()
        handler_id = self.registry.register_handler("test.event", handler)
        
        result = self.registry.unregister_handler("test.event", handler_id)
        
        self.assertTrue(result)
        
        self.assertNotIn(handler_id, self.registry.handlers.get("test.event", {}))
        
        result = self.registry.unregister_handler("test.event", "non-existent")
        self.assertFalse(result)
        
        result = self.registry.unregister_handler("non-existent", handler_id)
        self.assertFalse(result)
    
    def test_get_handlers(self):
        """Test getting handlers for an event type"""
        handler1 = MagicMock()
        handler2 = MagicMock()
        handler_id1 = self.registry.register_handler("test.event", handler1)
        handler_id2 = self.registry.register_handler("test.event", handler2)
        
        handlers = self.registry.get_handlers("test.event")
        
        self.assertEqual(len(handlers), 2)
        self.assertIn(handler_id1, handlers)
        self.assertIn(handler_id2, handlers)
        self.assertEqual(handlers[handler_id1], handler1)
        self.assertEqual(handlers[handler_id2], handler2)
        
        handlers = self.registry.get_handlers("non-existent")
        self.assertEqual(handlers, {})
    
    def test_get_all_handlers(self):
        """Test getting all handlers"""
        handler1 = MagicMock()
        handler2 = MagicMock()
        handler_id1 = self.registry.register_handler("event1", handler1)
        handler_id2 = self.registry.register_handler("event2", handler2)
        
        handlers = self.registry.get_all_handlers()
        
        self.assertEqual(len(handlers), 2)
        self.assertIn("event1", handlers)
        self.assertIn("event2", handlers)
        self.assertIn(handler_id1, handlers["event1"])
        self.assertIn(handler_id2, handlers["event2"])
    
    def test_validate_event(self):
        """Test validating an event"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number"}
            },
            "required": ["name", "value"]
        }
        self.registry.register_event_type("test.event", schema)
        
        valid_event = {"name": "test", "value": 42}
        result = self.registry.validate_event("test.event", valid_event)
        
        self.assertTrue(result)
        
        invalid_event = {"name": "test"}
        result = self.registry.validate_event("test.event", invalid_event)
        
        self.assertFalse(result)
        
        invalid_event = {"name": "test", "value": "not a number"}
        result = self.registry.validate_event("test.event", invalid_event)
        
        self.assertFalse(result)
        
        result = self.registry.validate_event("non-existent", {})
        
        self.assertFalse(result)
        
        self.registry.register_event_type("no.schema.event")
        
        result = self.registry.validate_event("no.schema.event", {})
        
        self.assertTrue(result)
    
    def test_validate_against_schema(self):
        """Test validating data against schema"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number"}
            },
            "required": ["name"]
        }
        
        valid_object = {"name": "test", "value": 42}
        try:
            self.registry._validate_against_schema(valid_object, schema)
        except ValueError:
            self.fail("_validate_against_schema raised ValueError unexpectedly")
        
        invalid_object = {"value": 42}
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_object, schema)
        
        invalid_object = {"name": 42}
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_object, schema)
        
        schema = {
            "type": "array",
            "items": {"type": "string"}
        }
        
        valid_array = ["a", "b", "c"]
        try:
            self.registry._validate_against_schema(valid_array, schema)
        except ValueError:
            self.fail("_validate_against_schema raised ValueError unexpectedly")
        
        invalid_array = [1, 2, 3]
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_array, schema)
        
        invalid_array = "not an array"
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_array, schema)
        
        schema = {
            "type": "string",
            "pattern": "^test"
        }
        
        valid_string = "test string"
        try:
            self.registry._validate_against_schema(valid_string, schema)
        except ValueError:
            self.fail("_validate_against_schema raised ValueError unexpectedly")
        
        invalid_string = "not a test string"
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_string, schema)
        
        invalid_string = 42
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_string, schema)
        
        schema = {
            "type": "number",
            "minimum": 0,
            "maximum": 100
        }
        
        valid_number = 42
        try:
            self.registry._validate_against_schema(valid_number, schema)
        except ValueError:
            self.fail("_validate_against_schema raised ValueError unexpectedly")
        
        invalid_number = -1
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_number, schema)
        
        invalid_number = 101
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_number, schema)
        
        invalid_number = "not a number"
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_number, schema)
        
        schema = {
            "type": "integer",
            "minimum": 0,
            "maximum": 100
        }
        
        valid_integer = 42
        try:
            self.registry._validate_against_schema(valid_integer, schema)
        except ValueError:
            self.fail("_validate_against_schema raised ValueError unexpectedly")
        
        invalid_integer = 42.5
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_integer, schema)
        
        schema = {
            "type": "boolean"
        }
        
        valid_boolean = True
        try:
            self.registry._validate_against_schema(valid_boolean, schema)
        except ValueError:
            self.fail("_validate_against_schema raised ValueError unexpectedly")
        
        invalid_boolean = "not a boolean"
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_boolean, schema)
        
        schema = {
            "type": "null"
        }
        
        valid_null = None
        try:
            self.registry._validate_against_schema(valid_null, schema)
        except ValueError:
            self.fail("_validate_against_schema raised ValueError unexpectedly")
        
        invalid_null = "not null"
        with self.assertRaises(ValueError):
            self.registry._validate_against_schema(invalid_null, schema)

if __name__ == "__main__":
    unittest.main()
