"""
Base Event Handler for Expeta 2.0

This module provides a base class for event handlers.
"""

import logging
from typing import Dict, Any, Optional

class BaseEventHandler:
    """Base class for event handlers"""
    
    def __init__(self, event_bus=None):
        """Initialize base event handler
        
        Args:
            event_bus: Optional event bus for publishing events
        """
        self.event_bus = event_bus
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def handle_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle an event
        
        Args:
            event: Event to handle
            
        Returns:
            Optional result of handling the event
        """
        event_type = event.get("type")
        
        handler_method = self._get_handler_method(event_type)
        if handler_method:
            try:
                return handler_method(event)
            except Exception as e:
                self.logger.error(f"Error handling event {event_type}: {str(e)}")
                self._publish_error_event(event, str(e))
                return {"error": str(e)}
        else:
            self.logger.warning(f"No handler method found for event type: {event_type}")
            return None
    
    def _get_handler_method(self, event_type: str) -> Optional[callable]:
        """Get handler method for event type
        
        Args:
            event_type: Event type
            
        Returns:
            Handler method or None if not found
        """
        method_name = f"handle_{event_type.replace('.', '_')}"
        return getattr(self, method_name, None)
    
    def _publish_error_event(self, original_event: Dict[str, Any], error: str) -> None:
        """Publish error event
        
        Args:
            original_event: Original event that caused the error
            error: Error message
        """
        if self.event_bus:
            self.event_bus.publish("system.error", {
                "source": self.__class__.__name__,
                "error": error,
                "original_event": original_event
            })
