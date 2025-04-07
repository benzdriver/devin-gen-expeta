"""
Integration tests for Orchestrator and Event System
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestrator.task_manager import TaskManager
from orchestrator.workflow_engine import WorkflowEngine
from orchestrator.system_monitor import SystemMonitor
from event_system.event_bus import EventBus
from event_system.registry import EventRegistry
from event_system.handlers.base_handler import BaseEventHandler

class TestOrchestratorEventSystemIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.registry = EventRegistry()
        self.event_bus = EventBus()
        
        
        self.task_manager = TaskManager(event_bus=self.event_bus)
        self.workflow_engine = WorkflowEngine(task_manager=self.task_manager, event_bus=self.event_bus)
        self.system_monitor = SystemMonitor(event_bus=self.event_bus)
    
    def test_task_manager_events(self):
        """Test events published by TaskManager"""
        task_events = []
        
        def handle_task_event(event):
            task_events.append(event)
        
        self.event_bus.subscribe("task.created", handle_task_event)
        self.event_bus.subscribe("task.updated", handle_task_event)
        self.event_bus.subscribe("task.completed", handle_task_event)
        
        task_id = self.task_manager.create_task("Test Task", {"param": "value"})
        
        self.task_manager.update_task_status(task_id, "in_progress")
        self.task_manager.update_task_status(task_id, "completed")
        
        self.assertEqual(len(task_events), 3)
        
        created_events = [e for e in task_events if e["type"] == "task.created"]
        self.assertEqual(len(created_events), 1)
        self.assertEqual(created_events[0]["data"]["task_id"], task_id)
        self.assertEqual(created_events[0]["data"]["task"]["name"], "Test Task")
        
        updated_events = [e for e in task_events if e["type"] == "task.updated"]
        self.assertEqual(len(updated_events), 2)
        self.assertEqual(updated_events[0]["data"]["task_id"], task_id)
        self.assertEqual(updated_events[0]["data"]["task"]["status"], "in_progress")
        self.assertEqual(updated_events[1]["data"]["task_id"], task_id)
        self.assertEqual(updated_events[1]["data"]["task"]["status"], "completed")
    
    def test_workflow_engine_events(self):
        """Test events published by WorkflowEngine"""
        workflow_events = []
        
        def handle_workflow_event(event):
            workflow_events.append(event)
        
        self.event_bus.subscribe("workflow.defined", handle_workflow_event)
        self.event_bus.subscribe("workflow.execution.started", handle_workflow_event)
        self.event_bus.subscribe("workflow.execution.completed", handle_workflow_event)
        self.event_bus.subscribe("workflow.step.started", handle_workflow_event)
        self.event_bus.subscribe("workflow.step.completed", handle_workflow_event)
        
        steps = [
            {"type": "function", "function": "test_function"}
        ]
        
        workflow_id = self.workflow_engine.define_workflow("Test Workflow", steps)
        
        self.workflow_engine.register_function("test_function", lambda params, step_params: "test_result")
        
        execution_id = self.workflow_engine.execute_workflow(workflow_id, {"param": "value"})
        
        self.assertGreaterEqual(len(workflow_events), 5)  # defined, execution.started, step.started, step.completed, execution.completed
        
        defined_events = [e for e in workflow_events if e["type"] == "workflow.defined"]
        self.assertEqual(len(defined_events), 1)
        self.assertEqual(defined_events[0]["data"]["workflow_id"], workflow_id)
        self.assertEqual(defined_events[0]["data"]["workflow"]["name"], "Test Workflow")
        
        started_events = [e for e in workflow_events if e["type"] == "workflow.execution.started"]
        self.assertEqual(len(started_events), 1)
        self.assertEqual(started_events[0]["data"]["execution_id"], execution_id)
        self.assertEqual(started_events[0]["data"]["workflow_id"], workflow_id)
        
        completed_events = [e for e in workflow_events if e["type"] == "workflow.execution.completed"]
        self.assertEqual(len(completed_events), 1)
        self.assertEqual(completed_events[0]["data"]["execution_id"], execution_id)
        self.assertEqual(completed_events[0]["data"]["status"], "completed")
        
        step_started_events = [e for e in workflow_events if e["type"] == "workflow.step.started"]
        self.assertEqual(len(step_started_events), 1)
        
        step_completed_events = [e for e in workflow_events if e["type"] == "workflow.step.completed"]
        self.assertEqual(len(step_completed_events), 1)
    
    def test_system_monitor_events(self):
        """Test events published by SystemMonitor"""
        system_events = []
        
        def handle_system_event(event):
            system_events.append(event)
        
        self.event_bus.subscribe("system.component.status", handle_system_event)
        self.event_bus.subscribe("system.component.registered", handle_system_event)
        
        component_info = {
            "name": "Test Component",
            "description": "A test component",
            "health_check": lambda: ("healthy", {"memory_usage": 100})
        }
        
        self.system_monitor.register_component("test-component", component_info)
        
        self.system_monitor.check_component_health("test-component")
        
        self.assertEqual(len(system_events), 2)
        
        registered_events = [e for e in system_events if e["type"] == "system.component.registered"]
        self.assertEqual(len(registered_events), 1)
        self.assertEqual(registered_events[0]["data"]["component_id"], "test-component")
        
        status_events = [e for e in system_events if e["type"] == "system.component.status"]
        self.assertEqual(len(status_events), 1)
        self.assertEqual(status_events[0]["data"]["component_id"], "test-component")
        self.assertEqual(status_events[0]["data"]["status"], "healthy")
        self.assertEqual(status_events[0]["data"]["metrics"]["memory_usage"], 100)
    
    def test_custom_event_handler(self):
        """Test custom event handler integration"""
        class TestEventHandler(BaseEventHandler):
            def __init__(self, event_bus=None):
                super().__init__(event_bus)
                self.handled_events = []
            
            def handle_task_created(self, event):
                self.handled_events.append(event)
                return {"status": "processed"}
            
            def handle_workflow_execution_started(self, event):
                self.handled_events.append(event)
                return {"status": "processed"}
        
        handler = TestEventHandler(self.event_bus)
        
        self.event_bus.subscribe("task.created", handler.handle_event)
        self.event_bus.subscribe("workflow.execution.started", handler.handle_event)
        
        task_id = self.task_manager.create_task("Test Task", {"param": "value"})
        
        steps = [{"type": "function", "function": "test_function"}]
        workflow_id = self.workflow_engine.define_workflow("Test Workflow", steps)
        
        self.workflow_engine.register_function("test_function", lambda params, step_params: "test_result")
        
        execution_id = self.workflow_engine.execute_workflow(workflow_id, {"param": "value"})
        
        self.assertEqual(len(handler.handled_events), 2)
        
        task_events = [e for e in handler.handled_events if e["type"] == "task.created"]
        self.assertEqual(len(task_events), 1)
        self.assertEqual(task_events[0]["data"]["task_id"], task_id)
        
        workflow_events = [e for e in handler.handled_events if e["type"] == "workflow.execution.started"]
        self.assertEqual(len(workflow_events), 1)
        self.assertEqual(workflow_events[0]["data"]["execution_id"], execution_id)
    
    def test_event_driven_workflow(self):
        """Test event-driven workflow execution"""
        steps = [
            {"type": "function", "function": "process_event_data"}
        ]
        
        workflow_id = self.workflow_engine.define_workflow("Event-Driven Workflow", steps)
        
        def process_event_data(params, step_params):
            event_data = params.get("event_data", {})
            return {"processed": f"Processed: {event_data.get('message', 'No message')}"}
        
        self.workflow_engine.register_function("process_event_data", process_event_data)
        
        class WorkflowTriggerHandler(BaseEventHandler):
            def __init__(self, event_bus, workflow_engine):
                super().__init__(event_bus)
                self.workflow_engine = workflow_engine
                self.workflow_id = workflow_id
                self.execution_ids = []
            
            def handle_custom_event(self, event):
                event_data = event["data"]
                
                execution_id = self.workflow_engine.execute_workflow(
                    self.workflow_id,
                    {"event_data": event_data}
                )
                
                self.execution_ids.append(execution_id)
                
                return {"status": "workflow_triggered", "execution_id": execution_id}
        
        handler = WorkflowTriggerHandler(self.event_bus, self.workflow_engine)
        
        self.event_bus.register_event_type("custom.event", {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        })
        
        self.event_bus.subscribe("custom.event", handler.handle_event)
        
        self.event_bus.publish("custom.event", {"message": "Hello, World!"})
        
        self.assertEqual(len(handler.execution_ids), 1)
        
        execution_id = handler.execution_ids[0]
        execution = self.workflow_engine.get_execution(execution_id)
        
        self.assertEqual(execution["status"], "completed")
        self.assertEqual(execution["results"][0]["result"]["processed"], "Processed: Hello, World!")
    
    def test_event_based_error_handling(self):
        """Test error handling through events"""
        self.event_bus.register_event_type("system.error", {
            "type": "object",
            "properties": {
                "source": {"type": "string"},
                "error": {"type": "string"},
                "original_event": {"type": "object"}
            },
            "required": ["source", "error"]
        })
        
        errors = []
        
        def handle_error(event):
            errors.append(event["data"])
        
        self.event_bus.subscribe("system.error", handle_error)
        
        class ErrorHandler(BaseEventHandler):
            def handle_test_event(self, event):
                raise ValueError("Test error")
        
        handler = ErrorHandler(self.event_bus)
        
        self.event_bus.register_event_type("test.event", {})
        self.event_bus.subscribe("test.event", handler.handle_event)
        
        self.event_bus.publish("test.event", {})
        
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["source"], "ErrorHandler")
        self.assertEqual(errors[0]["error"], "Test error")
        self.assertEqual(errors[0]["original_event"]["type"], "test.event")

if __name__ == "__main__":
    unittest.main()
