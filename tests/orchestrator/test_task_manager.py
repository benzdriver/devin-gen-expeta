"""
Unit tests for Task Manager
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestrator.task_manager import TaskManager

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.event_bus = MagicMock()
        self.task_manager = TaskManager(event_bus=self.event_bus)
    
    def test_create_task(self):
        """Test creating a new task"""
        task_id = self.task_manager.create_task("Test Task", {"param": "value"})
        
        self.assertIsNotNone(task_id)
        self.assertIn(task_id, self.task_manager.tasks)
        
        task = self.task_manager.get_task(task_id)
        self.assertEqual(task["name"], "Test Task")
        self.assertEqual(task["parameters"]["param"], "value")
        self.assertEqual(task["status"], "created")
        
        self.event_bus.publish.assert_called_once_with("task.created", {
            "task_id": task_id,
            "task": task
        })
    
    def test_get_task(self):
        """Test getting a task by ID"""
        task_id = self.task_manager.create_task("Test Task")
        
        task = self.task_manager.get_task(task_id)
        
        self.assertEqual(task["id"], task_id)
        self.assertEqual(task["name"], "Test Task")
        self.assertEqual(task["status"], "created")
        
        non_existent_task = self.task_manager.get_task("non-existent-id")
        self.assertIsNone(non_existent_task)
    
    def test_get_all_tasks(self):
        """Test getting all tasks"""
        task_id1 = self.task_manager.create_task("Task 1")
        task_id2 = self.task_manager.create_task("Task 2")
        
        tasks = self.task_manager.get_all_tasks()
        
        self.assertEqual(len(tasks), 2)
        self.assertTrue(any(task["id"] == task_id1 for task in tasks))
        self.assertTrue(any(task["id"] == task_id2 for task in tasks))
    
    def test_update_task_status(self):
        """Test updating task status"""
        task_id = self.task_manager.create_task("Test Task")
        
        self.event_bus.reset_mock()
        
        result = self.task_manager.update_task_status(task_id, "in_progress")
        
        self.assertTrue(result)
        
        task = self.task_manager.get_task(task_id)
        self.assertEqual(task["status"], "in_progress")
        
        self.event_bus.publish.assert_called_once_with("task.updated", {
            "task_id": task_id,
            "task": task,
            "status": "in_progress"
        })
        
        result = self.task_manager.update_task_status("non-existent-id", "in_progress")
        self.assertFalse(result)
    
    def test_update_task_parameters(self):
        """Test updating task parameters"""
        task_id = self.task_manager.create_task("Test Task", {"param1": "value1"})
        
        self.event_bus.reset_mock()
        
        result = self.task_manager.update_task_parameters(task_id, {"param2": "value2"})
        
        self.assertTrue(result)
        
        task = self.task_manager.get_task(task_id)
        self.assertEqual(task["parameters"]["param1"], "value1")
        self.assertEqual(task["parameters"]["param2"], "value2")
        
        self.event_bus.publish.assert_called_once_with("task.updated", {
            "task_id": task_id,
            "task": task,
            "parameters": {"param2": "value2"}
        })
        
        result = self.task_manager.update_task_parameters("non-existent-id", {"param": "value"})
        self.assertFalse(result)
    
    def test_complete_task(self):
        """Test completing a task"""
        task_id = self.task_manager.create_task("Test Task")
        
        self.event_bus.reset_mock()
        
        result = self.task_manager.complete_task(task_id, {"result": "success"})
        
        self.assertTrue(result)
        
        task = self.task_manager.get_task(task_id)
        self.assertEqual(task["status"], "completed")
        self.assertEqual(task["result"]["result"], "success")
        self.assertIsNotNone(task["completed_at"])
        
        self.event_bus.publish.assert_called_once_with("task.completed", {
            "task_id": task_id,
            "task": task,
            "result": {"result": "success"}
        })
        
        result = self.task_manager.complete_task("non-existent-id", {"result": "success"})
        self.assertFalse(result)
    
    def test_fail_task(self):
        """Test failing a task"""
        task_id = self.task_manager.create_task("Test Task")
        
        self.event_bus.reset_mock()
        
        result = self.task_manager.fail_task(task_id, "Error message")
        
        self.assertTrue(result)
        
        task = self.task_manager.get_task(task_id)
        self.assertEqual(task["status"], "failed")
        self.assertEqual(task["result"]["error"], "Error message")
        
        self.event_bus.publish.assert_called_once_with("task.failed", {
            "task_id": task_id,
            "task": task,
            "error": "Error message"
        })
        
        result = self.task_manager.fail_task("non-existent-id", "Error message")
        self.assertFalse(result)
    
    def test_delete_task(self):
        """Test deleting a task"""
        task_id = self.task_manager.create_task("Test Task")
        
        self.event_bus.reset_mock()
        
        result = self.task_manager.delete_task(task_id)
        
        self.assertTrue(result)
        
        self.assertNotIn(task_id, self.task_manager.tasks)
        
        self.event_bus.publish.assert_called_once()
        self.assertEqual(self.event_bus.publish.call_args[0][0], "task.deleted")
        self.assertEqual(self.event_bus.publish.call_args[0][1]["task_id"], task_id)
        
        result = self.task_manager.delete_task("non-existent-id")
        self.assertFalse(result)
    
    def test_get_tasks_by_status(self):
        """Test getting tasks by status"""
        task_id1 = self.task_manager.create_task("Task 1")
        task_id2 = self.task_manager.create_task("Task 2")
        task_id3 = self.task_manager.create_task("Task 3")
        
        self.task_manager.update_task_status(task_id1, "in_progress")
        self.task_manager.update_task_status(task_id2, "in_progress")
        self.task_manager.update_task_status(task_id3, "completed")
        
        in_progress_tasks = self.task_manager.get_tasks_by_status("in_progress")
        completed_tasks = self.task_manager.get_tasks_by_status("completed")
        
        self.assertEqual(len(in_progress_tasks), 2)
        self.assertEqual(len(completed_tasks), 1)
        self.assertTrue(any(task["id"] == task_id1 for task in in_progress_tasks))
        self.assertTrue(any(task["id"] == task_id2 for task in in_progress_tasks))
        self.assertTrue(any(task["id"] == task_id3 for task in completed_tasks))
    
    def test_get_tasks_by_name(self):
        """Test getting tasks by name"""
        task_id1 = self.task_manager.create_task("Task A")
        task_id2 = self.task_manager.create_task("Task B")
        task_id3 = self.task_manager.create_task("Task A")
        
        tasks_a = self.task_manager.get_tasks_by_name("Task A")
        tasks_b = self.task_manager.get_tasks_by_name("Task B")
        
        self.assertEqual(len(tasks_a), 2)
        self.assertEqual(len(tasks_b), 1)
        self.assertTrue(any(task["id"] == task_id1 for task in tasks_a))
        self.assertTrue(any(task["id"] == task_id3 for task in tasks_a))
        self.assertTrue(any(task["id"] == task_id2 for task in tasks_b))

if __name__ == "__main__":
    unittest.main()
