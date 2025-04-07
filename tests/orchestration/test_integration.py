"""
Integration tests for Orchestration Layer
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestrator.task_manager import TaskManager
from orchestrator.workflow_engine import WorkflowEngine
from event_system.event_bus import EventBus
from event_system.registry import EventRegistry
from api_gateway.request_router import RequestRouter
from api_gateway.auth_manager import AuthManager
from api_gateway.response_formatter import ResponseFormatter

class TestOrchestrationLayerIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.registry = EventRegistry()
        self.event_bus = EventBus()
        
        
        self.task_manager = TaskManager(event_bus=self.event_bus)
        self.workflow_engine = WorkflowEngine(task_manager=self.task_manager, event_bus=self.event_bus)
        
        self.auth_manager = AuthManager(secret_key="test-secret-key")
        self.response_formatter = ResponseFormatter()
        self.request_router = RequestRouter(
            auth_manager=self.auth_manager,
            response_formatter=self.response_formatter
        )
        
        self.auth_manager.register_user("test-user", {
            "name": "Test User",
            "email": "test@example.com"
        })
        
        self.auth_manager.register_role("admin-role", {
            "name": "Admin",
            "permissions": ["workflow.execute", "task.manage"]
        })
        
        self.auth_manager.assign_role_to_user("test-user", "admin-role")
        
        self.auth_token = self.auth_manager.generate_token("test-user")
    
    def test_task_workflow_integration(self):
        """Test integration between TaskManager and WorkflowEngine"""
        steps = [
            {"type": "function", "function": "test_function", "parameters": {"step_param": "value"}}
        ]
        
        workflow_id = self.workflow_engine.define_workflow("Test Workflow", steps)
        
        self.workflow_engine.register_function("test_function", lambda params, step_params: {
            "result": f"Processed {params.get('input')} with {step_params.get('step_param')}"
        })
        
        execution_id = self.workflow_engine.execute_workflow(workflow_id, {"input": "test data"})
        
        execution = self.workflow_engine.get_execution(execution_id)
        self.assertEqual(execution["workflow_id"], workflow_id)
        self.assertEqual(execution["parameters"]["input"], "test data")
        
        task_id = execution["task_id"]
        task = self.task_manager.get_task(task_id)
        self.assertIsNotNone(task)
        self.assertEqual(task["status"], "completed")
        
        self.assertEqual(execution["status"], "completed")
        self.assertEqual(len(execution["results"]), 1)
        self.assertEqual(execution["results"][0]["result"]["result"], "Processed test data with value")
    
    def test_event_system_integration(self):
        """Test integration with the Event System"""
        task_events = []
        workflow_events = []
        
        def handle_task_event(event):
            task_events.append(event)
        
        def handle_workflow_event(event):
            workflow_events.append(event)
        
        self.event_bus.subscribe("task.created", handle_task_event)
        self.event_bus.subscribe("task.updated", handle_task_event)
        self.event_bus.subscribe("task.completed", handle_task_event)
        self.event_bus.subscribe("workflow.defined", handle_workflow_event)
        self.event_bus.subscribe("workflow.execution.started", handle_workflow_event)
        self.event_bus.subscribe("workflow.execution.completed", handle_workflow_event)
        
        steps = [
            {"type": "function", "function": "test_function"}
        ]
        
        workflow_id = self.workflow_engine.define_workflow("Test Workflow", steps)
        
        self.workflow_engine.register_function("test_function", lambda params, step_params: "test_result")
        
        execution_id = self.workflow_engine.execute_workflow(workflow_id, {"param": "value"})
        
        self.assertGreaterEqual(len(task_events), 2)  # At least created and completed
        self.assertGreaterEqual(len(workflow_events), 3)  # At least defined, started, and completed
        
        task_created_events = [e for e in task_events if e["type"] == "task.created"]
        self.assertEqual(len(task_created_events), 1)
        
        workflow_defined_events = [e for e in workflow_events if e["type"] == "workflow.defined"]
        self.assertEqual(len(workflow_defined_events), 1)
        self.assertEqual(workflow_defined_events[0]["data"]["workflow_id"], workflow_id)
        
        workflow_execution_started_events = [e for e in workflow_events if e["type"] == "workflow.execution.started"]
        self.assertEqual(len(workflow_execution_started_events), 1)
        self.assertEqual(workflow_execution_started_events[0]["data"]["execution_id"], execution_id)
    
    def test_api_gateway_integration(self):
        """Test integration with the API Gateway"""
        self.request_router.register_route(
            "/tasks",
            "POST",
            lambda data: {"task_id": self.task_manager.create_task(data["name"], data.get("parameters", {}))},
            auth_required=True
        )
        
        self.request_router.register_route(
            "/tasks/{task_id}",
            "GET",
            lambda data: self.task_manager.get_task(data["task_id"]),
            auth_required=True
        )
        
        self.request_router.register_route(
            "/workflows",
            "POST",
            lambda data: {"workflow_id": self.workflow_engine.define_workflow(data["name"], data["steps"])},
            auth_required=True
        )
        
        self.request_router.register_route(
            "/workflows/{workflow_id}/execute",
            "POST",
            lambda data: {"execution_id": self.workflow_engine.execute_workflow(data["workflow_id"], data.get("parameters", {}))},
            auth_required=True
        )
        
        request_data = {
            "name": "API Task",
            "parameters": {"source": "api"}
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        status_code, response = self.request_router.route_request(
            "/tasks",
            "POST",
            request_data,
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertIn("task_id", response)
        
        task_id = response["task_id"]
        
        status_code, response = self.request_router.route_request(
            f"/tasks/{task_id}",
            "GET",
            {"task_id": task_id},
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["name"], "API Task")
        self.assertEqual(response["parameters"]["source"], "api")
        
        request_data = {
            "name": "API Workflow",
            "steps": [
                {"type": "function", "function": "test_function"}
            ]
        }
        
        status_code, response = self.request_router.route_request(
            "/workflows",
            "POST",
            request_data,
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertIn("workflow_id", response)
        
        workflow_id = response["workflow_id"]
        
        self.workflow_engine.register_function("test_function", lambda params, step_params: "api_result")
        
        request_data = {
            "workflow_id": workflow_id,
            "parameters": {"source": "api"}
        }
        
        status_code, response = self.request_router.route_request(
            f"/workflows/{workflow_id}/execute",
            "POST",
            request_data,
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertIn("execution_id", response)
        
        execution_id = response["execution_id"]
        
        execution = self.workflow_engine.get_execution(execution_id)
        self.assertEqual(execution["status"], "completed")
    
    def test_authentication_authorization(self):
        """Test authentication and authorization integration"""
        def execute_workflow_handler(data):
            user = data.get("user", {})
            user_id = user.get("user_id")
            if not user or not user_id or not self.auth_manager.authorize(user_id, "workflow.execute"):
                raise PermissionError("User not authorized to execute workflows")
            
            return {"execution_id": self.workflow_engine.execute_workflow(data["workflow_id"], data.get("parameters", {}))}
        
        self.request_router.register_route(
            "/secure/workflows/{workflow_id}/execute",
            "POST",
            execute_workflow_handler,
            auth_required=True
        )
        
        steps = [{"type": "function", "function": "test_function"}]
        workflow_id = self.workflow_engine.define_workflow("Secure Workflow", steps)
        
        self.workflow_engine.register_function("test_function", lambda params, step_params: "secure_result")
        
        request_data = {
            "workflow_id": workflow_id,
            "parameters": {"secure": True}
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        status_code, response = self.request_router.route_request(
            f"/secure/workflows/{workflow_id}/execute",
            "POST",
            request_data,
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertIn("execution_id", response)
        
        headers = {"Authorization": "Bearer invalid-token"}
        
        status_code, response = self.request_router.route_request(
            f"/secure/workflows/{workflow_id}/execute",
            "POST",
            request_data,
            headers
        )
        
        self.assertEqual(status_code, 401)
        self.assertIn("error", response)
        
        self.auth_manager.register_user("limited-user", {
            "name": "Limited User",
            "roles": []
        })
        
        limited_token = self.auth_manager.generate_token("limited-user")
        
        headers = {"Authorization": f"Bearer {limited_token}"}
        
        status_code, response = self.request_router.route_request(
            f"/secure/workflows/{workflow_id}/execute",
            "POST",
            request_data,
            headers
        )
        
        self.assertEqual(status_code, 403)
        self.assertIn("error", response)
        self.assertIn("not authorized", response["error"])
    
    def test_end_to_end_workflow(self):
        """Test an end-to-end workflow through the orchestration layer"""
        steps = [
            {"type": "function", "function": "process_input"},
            {"type": "function", "function": "validate_result"},
            {"type": "function", "function": "format_output"}
        ]
        
        workflow_id = self.workflow_engine.define_workflow("End-to-End Workflow", steps)
        
        def process_input(params, step_params):
            return {"processed_data": f"Processed: {params.get('input', 'default')}"}
        
        def validate_result(params, step_params):
            processed_data = params.get("processed_data", "")
            return {"valid": True, "processed_data": processed_data}
        
        def format_output(params, step_params):
            if not params.get("valid", False):
                return {"error": "Validation failed"}
            
            return {"output": f"Output: {params.get('processed_data', '')}"}
        
        self.workflow_engine.register_function("process_input", process_input)
        self.workflow_engine.register_function("validate_result", validate_result)
        self.workflow_engine.register_function("format_output", format_output)
        
        workflow_progress = []
        
        def track_workflow_progress(event):
            if event["type"].startswith("workflow.execution.step."):
                workflow_progress.append(event["data"])
        
        self.event_bus.subscribe("workflow.execution.step.started", track_workflow_progress)
        self.event_bus.subscribe("workflow.execution.step.completed", track_workflow_progress)
        
        self.request_router.register_route(
            "/workflows/{workflow_id}/execute",
            "POST",
            lambda data: {"execution_id": self.workflow_engine.execute_workflow(data["workflow_id"], data.get("parameters", {}))},
            auth_required=True
        )
        
        request_data = {
            "workflow_id": workflow_id,
            "parameters": {"input": "test input"}
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        status_code, response = self.request_router.route_request(
            f"/workflows/{workflow_id}/execute",
            "POST",
            request_data,
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertIn("execution_id", response)
        
        execution_id = response["execution_id"]
        
        execution = self.workflow_engine.get_execution(execution_id)
        self.assertEqual(execution["status"], "completed")
        
        self.assertEqual(len(execution["results"]), 3)
        
        final_result = execution["results"][2]["result"]
        self.assertIn("output", final_result)
        self.assertEqual(final_result["output"], "Output: Processed: test input")
        
        self.assertGreaterEqual(len(workflow_progress), 6)  # 3 steps x 2 events (started, completed)
        
        task = self.task_manager.get_task(execution["task_id"])
        self.assertEqual(task["status"], "completed")

if __name__ == "__main__":
    unittest.main()
