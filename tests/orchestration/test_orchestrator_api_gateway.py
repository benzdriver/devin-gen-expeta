"""
Integration tests for Orchestrator and API Gateway
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestrator.task_manager import TaskManager
from orchestrator.workflow_engine import WorkflowEngine
from api_gateway.request_router import RequestRouter
from api_gateway.auth_manager import AuthManager
from api_gateway.response_formatter import ResponseFormatter
from event_system.event_bus import EventBus
from event_system.registry import EventRegistry

class TestOrchestratorApiGatewayIntegration(unittest.TestCase):
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
        
        self._register_api_routes()
    
    def _register_api_routes(self):
        """Register API routes for testing"""
        self.request_router.register_route(
            "/tasks",
            "GET",
            self._get_tasks_handler,
            auth_required=True
        )
        
        self.request_router.register_route(
            "/tasks",
            "POST",
            self._create_task_handler,
            auth_required=True
        )
        
        self.request_router.register_route(
            "/tasks/{task_id}",
            "GET",
            self._get_task_handler,
            auth_required=True
        )
        
        self.request_router.register_route(
            "/tasks/{task_id}/status",
            "PUT",
            self._update_task_status_handler,
            auth_required=True
        )
        
        self.request_router.register_route(
            "/workflows",
            "GET",
            self._get_workflows_handler,
            auth_required=True
        )
        
        self.request_router.register_route(
            "/workflows",
            "POST",
            self._define_workflow_handler,
            auth_required=True
        )
        
        self.request_router.register_route(
            "/workflows/{workflow_id}",
            "GET",
            self._get_workflow_handler,
            auth_required=True
        )
        
        self.request_router.register_route(
            "/workflows/{workflow_id}/execute",
            "POST",
            self._execute_workflow_handler,
            auth_required=True
        )
        
        self.request_router.register_route(
            "/executions/{execution_id}",
            "GET",
            self._get_execution_handler,
            auth_required=True
        )
    
    def _get_tasks_handler(self, data):
        """Handler for GET /tasks"""
        return {"tasks": list(self.task_manager.tasks.values())}
    
    def _create_task_handler(self, data):
        """Handler for POST /tasks"""
        task_id = self.task_manager.create_task(data["name"], data.get("parameters", {}))
        return {"task_id": task_id}
    
    def _get_task_handler(self, data):
        """Handler for GET /tasks/{task_id}"""
        task = self.task_manager.get_task(data["task_id"])
        if not task:
            raise ValueError("Task not found")
        return task
    
    def _update_task_status_handler(self, data):
        """Handler for PUT /tasks/{task_id}/status"""
        self.task_manager.update_task_status(data["task_id"], data["status"])
        return {"success": True}
    
    def _get_workflows_handler(self, data):
        """Handler for GET /workflows"""
        return {"workflows": list(self.workflow_engine.workflows.values())}
    
    def _define_workflow_handler(self, data):
        """Handler for POST /workflows"""
        workflow_id = self.workflow_engine.define_workflow(data["name"], data["steps"])
        return {"workflow_id": workflow_id}
    
    def _get_workflow_handler(self, data):
        """Handler for GET /workflows/{workflow_id}"""
        workflow = self.workflow_engine.get_workflow(data["workflow_id"])
        if not workflow:
            raise ValueError("Workflow not found")
        return workflow
    
    def _execute_workflow_handler(self, data):
        """Handler for POST /workflows/{workflow_id}/execute"""
        execution_id = self.workflow_engine.execute_workflow(
            data["workflow_id"],
            data.get("parameters", {})
        )
        return {"execution_id": execution_id}
    
    def _get_execution_handler(self, data):
        """Handler for GET /executions/{execution_id}"""
        execution = self.workflow_engine.get_execution(data["execution_id"])
        if not execution:
            raise ValueError("Execution not found")
        return execution
    
    def test_task_api_integration(self):
        """Test integration between TaskManager and API Gateway"""
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
            "task_id": task_id,
            "status": "in_progress"
        }
        
        status_code, response = self.request_router.route_request(
            f"/tasks/{task_id}/status",
            "PUT",
            request_data,
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertTrue(response["success"])
        
        status_code, response = self.request_router.route_request(
            f"/tasks/{task_id}",
            "GET",
            {"task_id": task_id},
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["status"], "in_progress")
        
        status_code, response = self.request_router.route_request(
            "/tasks",
            "GET",
            {},
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertIn("tasks", response)
        self.assertEqual(len(response["tasks"]), 1)
        self.assertEqual(response["tasks"][0]["name"], "API Task")
    
    def test_workflow_api_integration(self):
        """Test integration between WorkflowEngine and API Gateway"""
        request_data = {
            "name": "API Workflow",
            "steps": [
                {"type": "function", "function": "test_function"}
            ]
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        status_code, response = self.request_router.route_request(
            "/workflows",
            "POST",
            request_data,
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertIn("workflow_id", response)
        
        workflow_id = response["workflow_id"]
        
        status_code, response = self.request_router.route_request(
            f"/workflows/{workflow_id}",
            "GET",
            {"workflow_id": workflow_id},
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["name"], "API Workflow")
        self.assertEqual(len(response["steps"]), 1)
        
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
        
        status_code, response = self.request_router.route_request(
            f"/executions/{execution_id}",
            "GET",
            {"execution_id": execution_id},
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["workflow_id"], workflow_id)
        self.assertEqual(response["status"], "completed")
        
        status_code, response = self.request_router.route_request(
            "/workflows",
            "GET",
            {},
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertIn("workflows", response)
        self.assertEqual(len(response["workflows"]), 1)
        self.assertEqual(response["workflows"][0]["name"], "API Workflow")
    
    def test_error_handling(self):
        """Test error handling in API Gateway integration"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        status_code, response = self.request_router.route_request(
            "/tasks/non-existent",
            "GET",
            {"task_id": "non-existent"},
            headers
        )
        
        self.assertEqual(status_code, 500)
        self.assertIn("error", response)
        
        status_code, response = self.request_router.route_request(
            "/workflows/non-existent",
            "GET",
            {"workflow_id": "non-existent"},
            headers
        )
        
        self.assertEqual(status_code, 500)
        self.assertIn("error", response)
        
        status_code, response = self.request_router.route_request(
            "/executions/non-existent",
            "GET",
            {"execution_id": "non-existent"},
            headers
        )
        
        self.assertEqual(status_code, 500)
        self.assertIn("error", response)
    
    def test_authentication_integration(self):
        """Test authentication integration"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        status_code, response = self.request_router.route_request(
            "/tasks",
            "GET",
            {},
            headers
        )
        
        self.assertEqual(status_code, 200)
        
        headers = {"Authorization": "Bearer invalid-token"}
        
        status_code, response = self.request_router.route_request(
            "/tasks",
            "GET",
            {},
            headers
        )
        
        self.assertEqual(status_code, 401)
        self.assertIn("error", response)
        
        status_code, response = self.request_router.route_request(
            "/tasks",
            "GET",
            {}
        )
        
        self.assertEqual(status_code, 401)
        self.assertIn("error", response)
    
    def test_authorization_integration(self):
        """Test authorization integration"""
        self.auth_manager.register_user("limited-user", {
            "name": "Limited User",
            "roles": []
        })
        
        limited_token = self.auth_manager.generate_token("limited-user")
        
        def secure_handler(data):
            user = data.get("user", {})
            user_id = user.get("user_id")
            if not user or not user_id or not self.auth_manager.authorize(user_id, "workflow.execute"):
                raise PermissionError("User not authorized")
            
            return {"success": True}
        
        self.request_router.register_route(
            "/secure",
            "GET",
            secure_handler,
            auth_required=True
        )
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        status_code, response = self.request_router.route_request(
            "/secure",
            "GET",
            {},
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertTrue(response["success"])
        
        headers = {"Authorization": f"Bearer {limited_token}"}
        
        status_code, response = self.request_router.route_request(
            "/secure",
            "GET",
            {},
            headers
        )
        
        self.assertEqual(status_code, 403)
        self.assertIn("error", response)
    
    def test_middleware_integration(self):
        """Test middleware integration"""
        def timestamp_middleware(path, method, request_data, headers, version):
            request_data["timestamp"] = "test-timestamp"
            return request_data
        
        self.request_router.register_middleware(timestamp_middleware)
        
        def timestamp_handler(data):
            return {"timestamp": data.get("timestamp")}
        
        self.request_router.register_route(
            "/timestamp",
            "GET",
            timestamp_handler,
            auth_required=True
        )
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        status_code, response = self.request_router.route_request(
            "/timestamp",
            "GET",
            {},
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["timestamp"], "test-timestamp")
    
    def test_response_formatter_integration(self):
        """Test response formatter integration"""
        def simple_handler(data):
            return {"data": "value"}
        
        self.request_router.register_route(
            "/formatted",
            "GET",
            simple_handler,
            auth_required=True
        )
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        status_code, response = self.request_router.route_request(
            "/formatted",
            "GET",
            {},
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["data"], "value")
        self.assertIn("_metadata", response)
        self.assertEqual(response["_metadata"]["path"], "/formatted")
        self.assertEqual(response["_metadata"]["method"], "GET")
        
        self.response_formatter.set_include_metadata(False)
        
        status_code, response = self.request_router.route_request(
            "/formatted",
            "GET",
            {},
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["data"], "value")
        self.assertNotIn("_metadata", response)
        
        self.response_formatter.set_include_metadata(True)
    
    def test_complex_workflow_api_integration(self):
        """Test integration with a complex workflow"""
        request_data = {
            "name": "Complex API Workflow",
            "steps": [
                {"type": "function", "function": "step1"},
                {"type": "function", "function": "step2"},
                {"type": "function", "function": "step3"}
            ]
        }
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        status_code, response = self.request_router.route_request(
            "/workflows",
            "POST",
            request_data,
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertIn("workflow_id", response)
        
        workflow_id = response["workflow_id"]
        
        def step1(params, step_params):
            return {"step1_result": f"Step 1 processed: {params.get('input', 'default')}"}
        
        def step2(params, step_params):
            return {"step2_result": f"Step 2 processed: {params.get('step1_result', 'default')}"}
        
        def step3(params, step_params):
            return {"final_result": f"Final result: {params.get('step2_result', 'default')}"}
        
        self.workflow_engine.register_function("step1", step1)
        self.workflow_engine.register_function("step2", step2)
        self.workflow_engine.register_function("step3", step3)
        
        request_data = {
            "workflow_id": workflow_id,
            "parameters": {"input": "complex test"}
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
        
        status_code, response = self.request_router.route_request(
            f"/executions/{execution_id}",
            "GET",
            {"execution_id": execution_id},
            headers
        )
        
        self.assertEqual(status_code, 200)
        self.assertEqual(response["workflow_id"], workflow_id)
        self.assertEqual(response["status"], "completed")
        
        self.assertEqual(len(response["results"]), 3)
        self.assertEqual(response["results"][0]["result"]["step1_result"], "Step 1 processed: complex test")
        self.assertEqual(response["results"][1]["result"]["step2_result"], "Step 2 processed: Step 1 processed: complex test")
        self.assertEqual(response["results"][2]["result"]["final_result"], "Final result: Step 2 processed: Step 1 processed: complex test")

if __name__ == "__main__":
    unittest.main()
