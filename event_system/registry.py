"""
Event Registry for Expeta 2.0

This module provides a registry for event types and handlers.
"""

import logging
from typing import Dict, Any, List, Callable, Optional, Set

class EventRegistry:
    """Registry for event types and handlers"""
    
    def __init__(self):
        """Initialize event registry"""
        self.event_types = {}
        self.handlers = {}
        self.logger = logging.getLogger(__name__)
    
    def register_event_type(self, event_type: str, schema: Dict[str, Any] = None) -> bool:
        """Register an event type
        
        Args:
            event_type: Event type
            schema: Optional event schema
            
        Returns:
            True if event type was registered, False if it already exists
        """
        if event_type in self.event_types:
            return False
        
        self.event_types[event_type] = {
            "type": event_type,
            "schema": schema or {}
        }
        
        return True
    
    def get_event_type(self, event_type: str) -> Optional[Dict[str, Any]]:
        """Get event type
        
        Args:
            event_type: Event type
            
        Returns:
            Event type data or None if not found
        """
        return self.event_types.get(event_type)
    
    def get_all_event_types(self) -> Dict[str, Dict[str, Any]]:
        """Get all event types
        
        Returns:
            Dictionary of event types
        """
        return self.event_types
    
    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], None], handler_id: str = None) -> str:
        """Register an event handler
        
        Args:
            event_type: Event type
            handler: Handler function
            handler_id: Optional handler ID
            
        Returns:
            Handler ID
        """
        if handler_id is None:
            import uuid
            handler_id = str(uuid.uuid4())
        
        if event_type not in self.handlers:
            self.handlers[event_type] = {}
        
        self.handlers[event_type][handler_id] = handler
        
        return handler_id
    
    def unregister_handler(self, event_type: str, handler_id: str) -> bool:
        """Unregister an event handler
        
        Args:
            event_type: Event type
            handler_id: Handler ID
            
        Returns:
            True if handler was unregistered, False otherwise
        """
        if event_type in self.handlers and handler_id in self.handlers[event_type]:
            del self.handlers[event_type][handler_id]
            
            if not self.handlers[event_type]:
                del self.handlers[event_type]
            
            return True
        
        return False
    
    def get_handlers(self, event_type: str) -> Dict[str, Callable[[Dict[str, Any]], None]]:
        """Get handlers for an event type
        
        Args:
            event_type: Event type
            
        Returns:
            Dictionary of handlers
        """
        return self.handlers.get(event_type, {})
    
    def get_all_handlers(self) -> Dict[str, Dict[str, Callable[[Dict[str, Any]], None]]]:
        """Get all handlers
        
        Returns:
            Dictionary of handlers by event type
        """
        return self.handlers
    
    def validate_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Validate event data against schema
        
        Args:
            event_type: Event type
            event_data: Event data
            
        Returns:
            True if event is valid, False otherwise
        """
        if event_type not in self.event_types:
            return False
        
        schema = self.event_types[event_type].get("schema")
        if not schema:
            return True
        
        try:
            self._validate_against_schema(event_data, schema)
            return True
        except Exception as e:
            self.logger.error(f"Event validation failed for {event_type}: {str(e)}")
            return False
    
    def _validate_against_schema(self, data: Any, schema: Dict[str, Any]) -> None:
        """Validate data against schema
        
        Args:
            data: Data to validate
            schema: Schema to validate against
            
        Raises:
            ValueError: If validation fails
        """
        schema_type = schema.get("type")
        
        if schema_type == "object":
            if not isinstance(data, dict):
                raise ValueError(f"Expected object, got {type(data).__name__}")
            
            properties = schema.get("properties", {})
            required = schema.get("required", [])
            
            for prop in required:
                if prop not in data:
                    raise ValueError(f"Missing required property: {prop}")
            
            for prop, prop_schema in properties.items():
                if prop in data:
                    self._validate_against_schema(data[prop], prop_schema)
        
        elif schema_type == "array":
            if not isinstance(data, list):
                raise ValueError(f"Expected array, got {type(data).__name__}")
            
            items_schema = schema.get("items")
            if items_schema:
                for item in data:
                    self._validate_against_schema(item, items_schema)
        
        elif schema_type == "string":
            if not isinstance(data, str):
                raise ValueError(f"Expected string, got {type(data).__name__}")
            
            pattern = schema.get("pattern")
            if pattern:
                import re
                if not re.match(pattern, data):
                    raise ValueError(f"String does not match pattern: {pattern}")
        
        elif schema_type == "number" or schema_type == "integer":
            if schema_type == "integer" and not isinstance(data, int):
                raise ValueError(f"Expected integer, got {type(data).__name__}")
            elif not isinstance(data, (int, float)):
                raise ValueError(f"Expected number, got {type(data).__name__}")
            
            minimum = schema.get("minimum")
            maximum = schema.get("maximum")
            
            if minimum is not None and data < minimum:
                raise ValueError(f"Value {data} is less than minimum {minimum}")
            
            if maximum is not None and data > maximum:
                raise ValueError(f"Value {data} is greater than maximum {maximum}")
        
        elif schema_type == "boolean":
            if not isinstance(data, bool):
                raise ValueError(f"Expected boolean, got {type(data).__name__}")
        
        elif schema_type == "null":
            if data is not None:
                raise ValueError(f"Expected null, got {type(data).__name__}")
