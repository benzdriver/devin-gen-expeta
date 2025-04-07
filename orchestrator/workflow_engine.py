"""
Workflow Engine for Expeta 2.0

This module defines and executes workflows within the Expeta system.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable

class WorkflowEngine:
    """Defines and executes workflows within the Expeta system"""
    
    def __init__(self, task_manager=None, event_bus=None):
        """Initialize workflow engine
        
        Args:
            task_manager: Optional task manager for tracking workflow tasks
            event_bus: Optional event bus for publishing workflow events
        """
        self.workflows = {}
        self.task_manager = task_manager
        self.event_bus = event_bus
        self.executions = {}
    
    def define_workflow(self, name: str, steps: List[Dict[str, Any]]) -> str:
        """Define a new workflow
        
        Args:
            name: Workflow name
            steps: List of workflow steps
            
        Returns:
            Workflow ID
        """
        workflow_id = str(uuid.uuid4())
        
        workflow = {
            "id": workflow_id,
            "name": name,
            "steps": steps,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.workflows[workflow_id] = workflow
        
        if self.event_bus:
            self.event_bus.publish("workflow.defined", {
                "workflow_id": workflow_id,
                "workflow": workflow
            })
        
        return workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow data or None if not found
        """
        return self.workflows.get(workflow_id)
    
    def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows
        
        Returns:
            List of all workflows
        """
        return list(self.workflows.values())
    
    def update_workflow(self, workflow_id: str, name: str = None, steps: List[Dict[str, Any]] = None) -> bool:
        """Update workflow
        
        Args:
            workflow_id: Workflow ID
            name: Optional new workflow name
            steps: Optional new workflow steps
            
        Returns:
            True if workflow was updated, False otherwise
        """
        if workflow_id not in self.workflows:
            return False
        
        if name:
            self.workflows[workflow_id]["name"] = name
        
        if steps:
            self.workflows[workflow_id]["steps"] = steps
        
        self.workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
        
        if self.event_bus:
            self.event_bus.publish("workflow.updated", {
                "workflow_id": workflow_id,
                "workflow": self.workflows[workflow_id]
            })
        
        return True
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            True if workflow was deleted, False otherwise
        """
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows.pop(workflow_id)
        
        if self.event_bus:
            self.event_bus.publish("workflow.deleted", {
                "workflow_id": workflow_id,
                "workflow": workflow
            })
        
        return True
    
    def execute_workflow(self, workflow_id: str, parameters: Dict[str, Any] = None) -> str:
        """Execute a workflow
        
        Args:
            workflow_id: Workflow ID
            parameters: Optional workflow parameters
            
        Returns:
            Execution ID
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        execution_id = str(uuid.uuid4())
        
        execution = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "parameters": parameters or {},
            "status": "started",
            "current_step": 0,
            "results": [],
            "started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None
        }
        
        self.executions[execution_id] = execution
        
        if self.task_manager:
            task_id = self.task_manager.create_task(
                f"Execute workflow: {workflow['name']}",
                {
                    "workflow_id": workflow_id,
                    "execution_id": execution_id,
                    "parameters": parameters
                }
            )
            execution["task_id"] = task_id
        
        if self.event_bus:
            self.event_bus.publish("workflow.execution.started", {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "execution": execution
            })
        
        self._execute_workflow_steps(execution_id)
        
        return execution_id
    
    def _execute_workflow_steps(self, execution_id: str):
        """Execute workflow steps
        
        Args:
            execution_id: Execution ID
        """
        execution = self.executions[execution_id]
        workflow = self.workflows[execution["workflow_id"]]
        
        try:
            for i, step in enumerate(workflow["steps"]):
                execution["current_step"] = i
                execution["updated_at"] = datetime.now().isoformat()
                
                if self.event_bus:
                    self.event_bus.publish("workflow.execution.step.started", {
                        "execution_id": execution_id,
                        "workflow_id": execution["workflow_id"],
                        "step": step,
                        "step_index": i
                    })
                
                step_result = self._execute_step(step, execution["parameters"])
                
                execution["results"].append({
                    "step": i,
                    "result": step_result
                })
                
                if self.event_bus:
                    self.event_bus.publish("workflow.execution.step.completed", {
                        "execution_id": execution_id,
                        "workflow_id": execution["workflow_id"],
                        "step": step,
                        "step_index": i,
                        "result": step_result
                    })
                
                if "condition" in step and not self._evaluate_condition(step["condition"], step_result, execution["parameters"]):
                    if "next" in step:
                        next_step = step["next"]
                        for j, s in enumerate(workflow["steps"][i+1:], i+1):
                            if s.get("label") == next_step:
                                execution["current_step"] = j - 1  # Will be incremented in next loop
                                break
            
            execution["status"] = "completed"
            execution["completed_at"] = datetime.now().isoformat()
            
            if self.task_manager and "task_id" in execution:
                self.task_manager.complete_task(execution["task_id"], {
                    "execution_id": execution_id,
                    "results": execution["results"]
                })
            
            if self.event_bus:
                self.event_bus.publish("workflow.execution.completed", {
                    "execution_id": execution_id,
                    "workflow_id": execution["workflow_id"],
                    "execution": execution
                })
                
        except Exception as e:
            execution["status"] = "failed"
            execution["error"] = str(e)
            execution["updated_at"] = datetime.now().isoformat()
            
            if self.task_manager and "task_id" in execution:
                self.task_manager.fail_task(execution["task_id"], str(e))
            
            if self.event_bus:
                self.event_bus.publish("workflow.execution.failed", {
                    "execution_id": execution_id,
                    "workflow_id": execution["workflow_id"],
                    "execution": execution,
                    "error": str(e)
                })
    
    def _execute_step(self, step: Dict[str, Any], parameters: Dict[str, Any]) -> Any:
        """Execute a workflow step
        
        Args:
            step: Step definition
            parameters: Workflow parameters
            
        Returns:
            Step result
        """
        step_type = step.get("type")
        
        if step_type == "function":
            function_name = step.get("function")
            if function_name in self.registered_functions:
                return self.registered_functions[function_name](parameters, step.get("parameters", {}))
            else:
                raise ValueError(f"Function {function_name} not registered")
        elif step_type == "subprocess":
            subprocess_workflow_id = step.get("workflow_id")
            subprocess_parameters = {**parameters, **(step.get("parameters", {}))}
            return self.execute_workflow(subprocess_workflow_id, subprocess_parameters)
        elif step_type == "parallel":
            results = []
            for parallel_step in step.get("steps", []):
                results.append(self._execute_step(parallel_step, parameters))
            return results
        else:
            if step_type in self.step_handlers:
                return self.step_handlers[step_type](parameters, step)
            else:
                raise ValueError(f"Unknown step type: {step_type}")
    
    def _evaluate_condition(self, condition: Dict[str, Any], step_result: Any, parameters: Dict[str, Any]) -> bool:
        """Evaluate a condition
        
        Args:
            condition: Condition definition
            step_result: Result of the step
            parameters: Workflow parameters
            
        Returns:
            True if condition is met, False otherwise
        """
        condition_type = condition.get("type")
        
        if condition_type == "equals":
            return self._get_value(condition.get("left"), step_result, parameters) == self._get_value(condition.get("right"), step_result, parameters)
        elif condition_type == "not_equals":
            return self._get_value(condition.get("left"), step_result, parameters) != self._get_value(condition.get("right"), step_result, parameters)
        elif condition_type == "greater_than":
            return self._get_value(condition.get("left"), step_result, parameters) > self._get_value(condition.get("right"), step_result, parameters)
        elif condition_type == "less_than":
            return self._get_value(condition.get("left"), step_result, parameters) < self._get_value(condition.get("right"), step_result, parameters)
        elif condition_type == "contains":
            return self._get_value(condition.get("right"), step_result, parameters) in self._get_value(condition.get("left"), step_result, parameters)
        elif condition_type == "custom":
            condition_function = condition.get("function")
            if condition_function in self.condition_handlers:
                return self.condition_handlers[condition_function](step_result, parameters)
            else:
                raise ValueError(f"Unknown condition function: {condition_function}")
        else:
            raise ValueError(f"Unknown condition type: {condition_type}")
    
    def _get_value(self, value_def: Any, step_result: Any, parameters: Dict[str, Any]) -> Any:
        """Get a value from a value definition
        
        Args:
            value_def: Value definition
            step_result: Result of the step
            parameters: Workflow parameters
            
        Returns:
            Resolved value
        """
        if isinstance(value_def, dict) and "type" in value_def:
            if value_def["type"] == "parameter":
                return parameters.get(value_def.get("name"))
            elif value_def["type"] == "result":
                return step_result
            elif value_def["type"] == "result_path":
                path = value_def.get("path", "").split(".")
                value = step_result
                for key in path:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        return None
                return value
            else:
                return value_def
        else:
            return value_def
    
    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution by ID
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution data or None if not found
        """
        return self.executions.get(execution_id)
    
    def get_all_executions(self) -> List[Dict[str, Any]]:
        """Get all executions
        
        Returns:
            List of all executions
        """
        return list(self.executions.values())
    
    def get_executions_by_workflow(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get executions by workflow ID
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            List of executions for the specified workflow
        """
        return [execution for execution in self.executions.values() if execution["workflow_id"] == workflow_id]
    
    def register_function(self, name: str, function: Callable) -> None:
        """Register a function for use in workflow steps
        
        Args:
            name: Function name
            function: Function to register
        """
        if not hasattr(self, "registered_functions"):
            self.registered_functions = {}
        
        self.registered_functions[name] = function
    
    def register_step_handler(self, step_type: str, handler: Callable) -> None:
        """Register a step handler for custom step types
        
        Args:
            step_type: Step type
            handler: Handler function
        """
        if not hasattr(self, "step_handlers"):
            self.step_handlers = {}
        
        self.step_handlers[step_type] = handler
    
    def register_condition_handler(self, condition_type: str, handler: Callable) -> None:
        """Register a condition handler for custom condition types
        
        Args:
            condition_type: Condition type
            handler: Handler function
        """
        if not hasattr(self, "condition_handlers"):
            self.condition_handlers = {}
        
        self.condition_handlers[condition_type] = handler
