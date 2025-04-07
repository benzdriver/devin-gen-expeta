"""
Unit tests for Workflow Engine
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestrator.workflow_engine import WorkflowEngine

class TestWorkflowEngine(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.task_manager = MagicMock()
        self.event_bus = MagicMock()
        self.workflow_engine = WorkflowEngine(
            task_manager=self.task_manager,
            event_bus=self.event_bus
        )
    
    def test_define_workflow(self):
        """Test defining a new workflow"""
        steps = [
            {"type": "function", "function": "test_function"},
            {"type": "subprocess", "workflow_id": "sub-workflow-id"}
        ]
        
        workflow_id = self.workflow_engine.define_workflow("Test Workflow", steps)
        
        self.assertIsNotNone(workflow_id)
        self.assertIn(workflow_id, self.workflow_engine.workflows)
        
        workflow = self.workflow_engine.get_workflow(workflow_id)
        self.assertEqual(workflow["name"], "Test Workflow")
        self.assertEqual(workflow["steps"], steps)
        
        self.event_bus.publish.assert_called_once_with("workflow.defined", {
            "workflow_id": workflow_id,
            "workflow": workflow
        })
    
    def test_get_workflow(self):
        """Test getting a workflow by ID"""
        steps = [{"type": "function", "function": "test_function"}]
        workflow_id = self.workflow_engine.define_workflow("Test Workflow", steps)
        
        workflow = self.workflow_engine.get_workflow(workflow_id)
        
        self.assertEqual(workflow["id"], workflow_id)
        self.assertEqual(workflow["name"], "Test Workflow")
        self.assertEqual(workflow["steps"], steps)
        
        non_existent_workflow = self.workflow_engine.get_workflow("non-existent-id")
        self.assertIsNone(non_existent_workflow)
    
    def test_get_all_workflows(self):
        """Test getting all workflows"""
        workflow_id1 = self.workflow_engine.define_workflow("Workflow 1", [])
        workflow_id2 = self.workflow_engine.define_workflow("Workflow 2", [])
        
        workflows = self.workflow_engine.get_all_workflows()
        
        self.assertEqual(len(workflows), 2)
        self.assertTrue(any(workflow["id"] == workflow_id1 for workflow in workflows))
        self.assertTrue(any(workflow["id"] == workflow_id2 for workflow in workflows))
    
    def test_update_workflow(self):
        """Test updating a workflow"""
        steps = [{"type": "function", "function": "test_function"}]
        workflow_id = self.workflow_engine.define_workflow("Test Workflow", steps)
        
        self.event_bus.reset_mock()
        
        new_steps = [
            {"type": "function", "function": "new_function"},
            {"type": "subprocess", "workflow_id": "sub-workflow-id"}
        ]
        result = self.workflow_engine.update_workflow(
            workflow_id,
            name="Updated Workflow",
            steps=new_steps
        )
        
        self.assertTrue(result)
        
        workflow = self.workflow_engine.get_workflow(workflow_id)
        self.assertEqual(workflow["name"], "Updated Workflow")
        self.assertEqual(workflow["steps"], new_steps)
        
        self.event_bus.publish.assert_called_once_with("workflow.updated", {
            "workflow_id": workflow_id,
            "workflow": workflow
        })
        
        result = self.workflow_engine.update_workflow("non-existent-id", name="New Name")
        self.assertFalse(result)
    
    def test_delete_workflow(self):
        """Test deleting a workflow"""
        workflow_id = self.workflow_engine.define_workflow("Test Workflow", [])
        
        self.event_bus.reset_mock()
        
        result = self.workflow_engine.delete_workflow(workflow_id)
        
        self.assertTrue(result)
        
        self.assertNotIn(workflow_id, self.workflow_engine.workflows)
        
        self.event_bus.publish.assert_called_once()
        self.assertEqual(self.event_bus.publish.call_args[0][0], "workflow.deleted")
        self.assertEqual(self.event_bus.publish.call_args[0][1]["workflow_id"], workflow_id)
        
        result = self.workflow_engine.delete_workflow("non-existent-id")
        self.assertFalse(result)
    
    def test_execute_workflow(self):
        """Test executing a workflow"""
        steps = [{"type": "function", "function": "test_function"}]
        workflow_id = self.workflow_engine.define_workflow("Test Workflow", steps)
        
        self.workflow_engine.register_function("test_function", lambda params, step_params: "test_result")
        
        self.event_bus.reset_mock()
        
        with patch.object(self.workflow_engine, '_execute_workflow_steps') as mock_execute:
            execution_id = self.workflow_engine.execute_workflow(workflow_id, {"param": "value"})
            
            self.assertIsNotNone(execution_id)
            self.assertIn(execution_id, self.workflow_engine.executions)
            
            execution = self.workflow_engine.executions[execution_id]
            self.assertEqual(execution["workflow_id"], workflow_id)
            self.assertEqual(execution["parameters"]["param"], "value")
            self.assertEqual(execution["status"], "started")
            
            self.task_manager.create_task.assert_called_once()
            self.assertEqual(self.task_manager.create_task.call_args[0][0], "Execute workflow: Test Workflow")
            
            self.event_bus.publish.assert_called_once()
            self.assertEqual(self.event_bus.publish.call_args[0][0], "workflow.execution.started")
            
            mock_execute.assert_called_once_with(execution_id)
    
    def test_execute_workflow_steps(self):
        """Test executing workflow steps"""
        steps = [
            {"type": "function", "function": "step1_function"},
            {"type": "function", "function": "step2_function"}
        ]
        workflow_id = self.workflow_engine.define_workflow("Test Workflow", steps)
        
        self.workflow_engine.register_function("step1_function", lambda params, step_params: "step1_result")
        self.workflow_engine.register_function("step2_function", lambda params, step_params: "step2_result")
        
        execution_id = str(unittest.mock.sentinel.execution_id)
        self.workflow_engine.executions[execution_id] = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "parameters": {"param": "value"},
            "status": "started",
            "current_step": 0,
            "results": [],
            "started_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "completed_at": None,
            "task_id": "task-id"
        }
        
        self.workflow_engine._execute_workflow_steps(execution_id)
        
        execution = self.workflow_engine.executions[execution_id]
        self.assertEqual(execution["status"], "completed")
        self.assertIsNotNone(execution["completed_at"])
        self.assertEqual(len(execution["results"]), 2)
        self.assertEqual(execution["results"][0]["result"], "step1_result")
        self.assertEqual(execution["results"][1]["result"], "step2_result")
        
        self.task_manager.complete_task.assert_called_once()
        self.assertEqual(self.task_manager.complete_task.call_args[0][0], "task-id")
        
        self.assertEqual(self.event_bus.publish.call_count, 5)  # 2 step starts, 2 step completions, 1 execution completion
    
    def test_execute_workflow_with_error(self):
        """Test executing a workflow with an error"""
        steps = [
            {"type": "function", "function": "failing_function"}
        ]
        workflow_id = self.workflow_engine.define_workflow("Test Workflow", steps)
        
        def failing_function(params, step_params):
            raise ValueError("Test error")
        
        self.workflow_engine.register_function("failing_function", failing_function)
        
        execution_id = str(unittest.mock.sentinel.execution_id)
        self.workflow_engine.executions[execution_id] = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "parameters": {},
            "status": "started",
            "current_step": 0,
            "results": [],
            "started_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
            "completed_at": None,
            "task_id": "task-id"
        }
        
        self.workflow_engine._execute_workflow_steps(execution_id)
        
        execution = self.workflow_engine.executions[execution_id]
        self.assertEqual(execution["status"], "failed")
        self.assertEqual(execution["error"], "Test error")
        
        self.task_manager.fail_task.assert_called_once()
        self.assertEqual(self.task_manager.fail_task.call_args[0][0], "task-id")
        self.assertEqual(self.task_manager.fail_task.call_args[0][1], "Test error")
        
        self.assertEqual(self.event_bus.publish.call_count, 2)  # 1 step start, 1 execution failure
    
    def test_execute_step(self):
        """Test executing a step"""
        test_function = MagicMock(return_value="test_result")
        self.workflow_engine.register_function("test_function", test_function)
        
        step = {"type": "function", "function": "test_function", "parameters": {"step_param": "value"}}
        result = self.workflow_engine._execute_step(step, {"workflow_param": "value"})
        
        test_function.assert_called_once_with({"workflow_param": "value"}, {"step_param": "value"})
        self.assertEqual(result, "test_result")
        
        step = {"type": "function", "function": "unknown_function"}
        with self.assertRaises(ValueError):
            self.workflow_engine._execute_step(step, {})
        
        step = {"type": "unknown_type"}
        with self.assertRaises(ValueError):
            self.workflow_engine._execute_step(step, {})
    
    def test_evaluate_condition(self):
        """Test evaluating conditions"""
        condition = {"type": "equals", "left": "value1", "right": "value1"}
        self.assertTrue(self.workflow_engine._evaluate_condition(condition, None, {}))
        
        condition = {"type": "equals", "left": "value1", "right": "value2"}
        self.assertFalse(self.workflow_engine._evaluate_condition(condition, None, {}))
        
        condition = {"type": "not_equals", "left": "value1", "right": "value2"}
        self.assertTrue(self.workflow_engine._evaluate_condition(condition, None, {}))
        
        condition = {"type": "not_equals", "left": "value1", "right": "value1"}
        self.assertFalse(self.workflow_engine._evaluate_condition(condition, None, {}))
        
        condition = {"type": "greater_than", "left": 10, "right": 5}
        self.assertTrue(self.workflow_engine._evaluate_condition(condition, None, {}))
        
        condition = {"type": "greater_than", "left": 5, "right": 10}
        self.assertFalse(self.workflow_engine._evaluate_condition(condition, None, {}))
        
        condition = {"type": "less_than", "left": 5, "right": 10}
        self.assertTrue(self.workflow_engine._evaluate_condition(condition, None, {}))
        
        condition = {"type": "less_than", "left": 10, "right": 5}
        self.assertFalse(self.workflow_engine._evaluate_condition(condition, None, {}))
        
        condition = {"type": "contains", "left": ["a", "b", "c"], "right": "b"}
        self.assertTrue(self.workflow_engine._evaluate_condition(condition, None, {}))
        
        condition = {"type": "contains", "left": ["a", "b", "c"], "right": "d"}
        self.assertFalse(self.workflow_engine._evaluate_condition(condition, None, {}))
        
        condition = {
            "type": "equals",
            "left": {"type": "parameter", "name": "test_param"},
            "right": "test_value"
        }
        self.assertTrue(self.workflow_engine._evaluate_condition(condition, None, {"test_param": "test_value"}))
        
        condition = {
            "type": "equals",
            "left": {"type": "result"},
            "right": "test_result"
        }
        self.assertTrue(self.workflow_engine._evaluate_condition(condition, "test_result", {}))
        
        condition = {
            "type": "equals",
            "left": {"type": "result_path", "path": "nested.value"},
            "right": "test_value"
        }
        result = {"nested": {"value": "test_value"}}
        self.assertTrue(self.workflow_engine._evaluate_condition(condition, result, {}))
        
        condition = {"type": "unknown_type"}
        with self.assertRaises(ValueError):
            self.workflow_engine._evaluate_condition(condition, None, {})

if __name__ == "__main__":
    unittest.main()
