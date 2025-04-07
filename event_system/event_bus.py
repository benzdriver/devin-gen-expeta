"""
Event Bus for Expeta 2.0

This module provides a central event bus for publishing and subscribing to events.
"""

import threading
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Callable, Optional, Set

class EventBus:
    """Central event bus for publishing and subscribing to events"""
    
    def __init__(self):
        """Initialize event bus"""
        self.subscribers = {}
        self.event_history = {}
        self.max_history_per_event = 100
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
    
    def publish(self, event_type: str, event_data: Dict[str, Any] = None) -> str:
        """Publish an event
        
        Args:
            event_type: Event type
            event_data: Event data
            
        Returns:
            Event ID
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        event = {
            "id": event_id,
            "type": event_type,
            "data": event_data or {},
            "timestamp": timestamp
        }
        
        with self.lock:
            if event_type not in self.event_history:
                self.event_history[event_type] = []
            
            self.event_history[event_type].append(event)
            
            if len(self.event_history[event_type]) > self.max_history_per_event:
                self.event_history[event_type] = self.event_history[event_type][-self.max_history_per_event:]
            
            if event_type in self.subscribers:
                for subscriber in self.subscribers[event_type]:
                    try:
                        subscriber(event)
                    except Exception as e:
                        self.logger.error(f"Error notifying subscriber for event {event_type}: {str(e)}")
            
            if "*" in self.subscribers:
                for subscriber in self.subscribers["*"]:
                    try:
                        subscriber(event)
                    except Exception as e:
                        self.logger.error(f"Error notifying wildcard subscriber for event {event_type}: {str(e)}")
        
        return event_id
    
    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> str:
        """Subscribe to an event
        
        Args:
            event_type: Event type or "*" for all events
            callback: Callback function
            
        Returns:
            Subscription ID
        """
        subscription_id = str(uuid.uuid4())
        
        with self.lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = set()
            
            self.subscribers[event_type].add(callback)
        
        return subscription_id
    
    def unsubscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """Unsubscribe from an event
        
        Args:
            event_type: Event type
            callback: Callback function
            
        Returns:
            True if unsubscribed, False otherwise
        """
        with self.lock:
            if event_type in self.subscribers and callback in self.subscribers[event_type]:
                self.subscribers[event_type].remove(callback)
                
                if not self.subscribers[event_type]:
                    del self.subscribers[event_type]
                
                return True
        
        return False
    
    def get_event_history(self, event_type: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Get event history
        
        Args:
            event_type: Optional event type filter
            limit: Optional limit on number of events to return
            
        Returns:
            List of events
        """
        with self.lock:
            if event_type:
                events = self.event_history.get(event_type, [])
            else:
                events = []
                for event_list in self.event_history.values():
                    events.extend(event_list)
                
                events.sort(key=lambda e: e["timestamp"], reverse=True)
            
            if limit:
                return events[:limit]
            else:
                return events
    
    def clear_history(self, event_type: str = None) -> None:
        """Clear event history
        
        Args:
            event_type: Optional event type to clear
        """
        with self.lock:
            if event_type:
                if event_type in self.event_history:
                    self.event_history[event_type] = []
            else:
                self.event_history = {}
    
    def get_subscriber_count(self, event_type: str = None) -> int:
        """Get subscriber count
        
        Args:
            event_type: Optional event type filter
            
        Returns:
            Number of subscribers
        """
        with self.lock:
            if event_type:
                return len(self.subscribers.get(event_type, set()))
            else:
                count = 0
                for subscribers in self.subscribers.values():
                    count += len(subscribers)
                return count
    
    def get_event_types(self) -> Set[str]:
        """Get all event types that have been published
        
        Returns:
            Set of event types
        """
        with self.lock:
            return set(self.event_history.keys())
