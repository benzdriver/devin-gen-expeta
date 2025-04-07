"""
Task Manager for Expeta 2.0

This module manages the lifecycle of tasks within the Expeta system.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

class TaskManager:
    """Manages task lifecycle within the Expeta system"""
    
    def __init__(self, event_bus=None):
        """Initialize task manager
        
        Args:
            event_bus: Optional event bus for publishing task events
        """
        self.tasks = {}
        self.event_bus = event_bus
    
    def create_task(self, name: str, parameters: Dict[str, Any] = None) -> str:
        """Create a new task
        
        Args:
            name: Task name
            parameters: Optional task parameters
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        
        task = {
            "id": task_id,
            "name": name,
            "parameters": parameters or {},
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None,
            "result": None
        }
        
        self.tasks[task_id] = task
        
        if self.event_bus:
            self.event_bus.publish("task.created", {
                "task_id": task_id,
                "task": task
            })
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID
        
        Args:
            task_id: Task ID
            
        Returns:
            Task data or None if not found
        """
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks
        
        Returns:
            List of all tasks
        """
        return list(self.tasks.values())
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status
        
        Args:
            task_id: Task ID
            status: New status
            
        Returns:
            True if task was updated, False otherwise
        """
        if task_id not in self.tasks:
            return False
        
        self.tasks[task_id]["status"] = status
        self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
        
        if self.event_bus:
            self.event_bus.publish("task.updated", {
                "task_id": task_id,
                "task": self.tasks[task_id],
                "status": status
            })
        
        return True
    
    def update_task_parameters(self, task_id: str, parameters: Dict[str, Any]) -> bool:
        """Update task parameters
        
        Args:
            task_id: Task ID
            parameters: New parameters
            
        Returns:
            True if task was updated, False otherwise
        """
        if task_id not in self.tasks:
            return False
        
        self.tasks[task_id]["parameters"].update(parameters)
        self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
        
        if self.event_bus:
            self.event_bus.publish("task.updated", {
                "task_id": task_id,
                "task": self.tasks[task_id],
                "parameters": parameters
            })
        
        return True
    
    def complete_task(self, task_id: str, result: Dict[str, Any] = None) -> bool:
        """Complete a task
        
        Args:
            task_id: Task ID
            result: Optional task result
            
        Returns:
            True if task was completed, False otherwise
        """
        if task_id not in self.tasks:
            return False
        
        self.tasks[task_id]["status"] = "completed"
        self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
        self.tasks[task_id]["completed_at"] = datetime.now().isoformat()
        self.tasks[task_id]["result"] = result or {}
        
        if self.event_bus:
            self.event_bus.publish("task.completed", {
                "task_id": task_id,
                "task": self.tasks[task_id],
                "result": result
            })
        
        return True
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed
        
        Args:
            task_id: Task ID
            error: Error message
            
        Returns:
            True if task was marked as failed, False otherwise
        """
        if task_id not in self.tasks:
            return False
        
        self.tasks[task_id]["status"] = "failed"
        self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
        self.tasks[task_id]["result"] = {"error": error}
        
        if self.event_bus:
            self.event_bus.publish("task.failed", {
                "task_id": task_id,
                "task": self.tasks[task_id],
                "error": error
            })
        
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if task was deleted, False otherwise
        """
        if task_id not in self.tasks:
            return False
        
        task = self.tasks.pop(task_id)
        
        if self.event_bus:
            self.event_bus.publish("task.deleted", {
                "task_id": task_id,
                "task": task
            })
        
        return True
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get tasks by status
        
        Args:
            status: Task status
            
        Returns:
            List of tasks with the specified status
        """
        return [task for task in self.tasks.values() if task["status"] == status]
    
    def get_tasks_by_name(self, name: str) -> List[Dict[str, Any]]:
        """Get tasks by name
        
        Args:
            name: Task name
            
        Returns:
            List of tasks with the specified name
        """
        return [task for task in self.tasks.values() if task["name"] == name]
