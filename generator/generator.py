"""
Generator Module for Expeta 2.0

This module generates code based on semantic expectations.
"""

class Generator:
    """Code generator, generates code implementations based on expectations"""

    def __init__(self, llm_router=None):
        """Initialize with optional LLM router
        
        Args:
            llm_router: Optional LLM router. If not provided, default router will be created.
        """
        self.llm_router = llm_router or self._create_default_llm_router()
        self._generation_results = []

    def generate(self, expectation):
        """Generate code based on expectation
        
        Args:
            expectation: Expectation dictionary
            
        Returns:
            Dictionary with generated code and metadata
        """
        key_concepts = self._extract_key_concepts(expectation)
        constraints = self._extract_constraints(expectation)

        code = self._generate_code_from_concepts(key_concepts, constraints)

        result = {
            "expectation_id": expectation.get("id"),
            "generated_code": code,
            "generation_metadata": self._collect_metadata()
        }

        self._generation_results.append(result)

        return result

    def sync_to_memory(self, memory_system):
        """Sync generation results to memory system (delayed call)
        
        Args:
            memory_system: Memory system to sync to
            
        Returns:
            Dictionary with sync results
        """
        for result in self._generation_results:
            memory_system.record_generation(result)

        synced_count = len(self._generation_results)
        self._generation_results = []

        return {"synced_count": synced_count}
        
    def _create_default_llm_router(self):
        """Create default LLM router
        
        Returns:
            Default LLM router instance
        """
        from ..llm_router.llm_router import LLMRouter
        return LLMRouter()
        
    def _extract_key_concepts(self, expectation):
        """Extract key concepts from expectation
        
        Args:
            expectation: Expectation dictionary
            
        Returns:
            Dictionary of key concepts
        """
        prompt = self._create_concept_extraction_prompt(expectation)
        
        response = self.llm_router.generate(prompt)
        
        concepts = self._parse_concepts_from_response(response)
        
        return concepts
        
    def _extract_constraints(self, expectation):
        """Extract constraints from expectation
        
        Args:
            expectation: Expectation dictionary
            
        Returns:
            List of constraints
        """
        explicit_constraints = expectation.get("constraints", [])
        
        implicit_constraints = self._extract_implicit_constraints(expectation)
        
        all_constraints = explicit_constraints + implicit_constraints
        
        unique_constraints = list(set(all_constraints))
        
        return unique_constraints
        
    def _generate_code_from_concepts(self, key_concepts, constraints):
        """Generate code from key concepts and constraints
        
        Args:
            key_concepts: Dictionary of key concepts
            constraints: List of constraints
            
        Returns:
            Generated code dictionary
        """
        prompt = self._create_code_generation_prompt(key_concepts, constraints)
        
        response = self.llm_router.generate(prompt, {"temperature": 0.2})
        
        code = self._parse_code_from_response(response)
        
        validation_result = self._self_validate_code(code, key_concepts, constraints)
        
        if not validation_result["valid"]:
            fixed_code = self._fix_code_issues(code, validation_result["issues"])
            code = fixed_code
        
        return code
        
    def _create_concept_extraction_prompt(self, expectation):
        """Create prompt for extracting key concepts
        
        Args:
            expectation: Expectation dictionary
            
        Returns:
            Prompt text
        """
        return f"""
        You are an expert software architect. Your task is to extract key concepts from the following software expectation.
        
        Expectation:
        Name: {expectation.get('name')}
        Description: {expectation.get('description')}
        Acceptance Criteria:
        {self._format_list_items(expectation.get('acceptance_criteria', []))}
        Constraints:
        {self._format_list_items(expectation.get('constraints', []))}
        
        Please identify the key concepts, entities, and relationships in this expectation.
        
        Format your response as a JSON object with the following structure:
        ```json
        {{
            "entities": [
                {{
                    "name": "EntityName",
                    "description": "Description of the entity",
                    "attributes": ["attribute1", "attribute2", ...]
                }},
                ...
            ],
            "relationships": [
                {{
                    "source": "EntityName1",
                    "target": "EntityName2",
                    "type": "one-to-many/many-to-one/etc.",
                    "description": "Description of the relationship"
                }},
                ...
            ],
            "actions": [
                {{
                    "name": "ActionName",
                    "description": "Description of the action",
                    "inputs": ["input1", "input2", ...],
                    "outputs": ["output1", "output2", ...]
                }},
                ...
            ]
        }}
        ```
        
        Focus on semantic concepts, not implementation details.
        """
        
    def _create_code_generation_prompt(self, key_concepts, constraints):
        """Create prompt for generating code
        
        Args:
            key_concepts: Dictionary of key concepts
            constraints: List of constraints
            
        Returns:
            Prompt text
        """
        import json
        
        concepts_json = json.dumps(key_concepts, indent=2)
        constraints_text = "\n".join([f"- {constraint}" for constraint in constraints])
        
        return f"""
        You are an expert software developer. Your task is to generate high-quality code based on the following concepts and constraints.
        
        Key Concepts:
        {concepts_json}
        
        Constraints:
        {constraints_text}
        
        Please generate code that implements these concepts while respecting the constraints.
        
        Your code should be:
        1. Well-structured and organized
        2. Properly documented with comments
        3. Following best practices and design patterns
        4. Maintainable and extensible
        5. Efficient and performant
        
        Format your response as a JSON object with the following structure:
        ```json
        {{
            "language": "python/javascript/etc.",
            "files": [
                {{
                    "path": "path/to/file.ext",
                    "content": "file content here"
                }},
                ...
            ],
            "explanation": "Explanation of your implementation approach"
        }}
        ```
        
        Focus on implementing the semantic concepts correctly, not just the technical details.
        """
        
    def _parse_concepts_from_response(self, response):
        """Parse key concepts from LLM response
        
        Args:
            response: LLM response
            
        Returns:
            Dictionary of key concepts
        """
        content = response.get("content", "")
        
        import re
        json_match = re.search(r"```json\s+(.*?)\s+```", content, re.DOTALL)
        
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = content
            
        import json
        try:
            concepts = json.loads(json_content)
        except Exception:
            concepts = {
                "entities": [],
                "relationships": [],
                "actions": []
            }
            
        return concepts
        
    def _parse_code_from_response(self, response):
        """Parse code from LLM response
        
        Args:
            response: LLM response
            
        Returns:
            Code dictionary
        """
        content = response.get("content", "")
        
        import re
        json_match = re.search(r"```json\s+(.*?)\s+```", content, re.DOTALL)
        
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = content
            
        import json
        try:
            code = json.loads(json_content)
        except Exception:
            code = self._simple_parse_code(content)
            
        return code
        
    def _simple_parse_code(self, content):
        """Simple parsing for code when JSON parsing fails
        
        Args:
            content: Text content to parse
            
        Returns:
            Code dictionary
        """
        import re
        code_blocks = re.findall(r"```(\w+)\s+(.*?)\s+```", content, re.DOTALL)
        
        files = []
        
        for i, (language, code) in enumerate(code_blocks):
            files.append({
                "path": f"file{i+1}.{language}",
                "content": code
            })
            
        return {
            "language": code_blocks[0][0] if code_blocks else "unknown",
            "files": files,
            "explanation": "Extracted from code blocks in response"
        }
        
    def _extract_implicit_constraints(self, expectation):
        """Extract implicit constraints from expectation
        
        Args:
            expectation: Expectation dictionary
            
        Returns:
            List of implicit constraints
        """
        prompt = f"""
        You are an expert software requirements analyst. Your task is to identify implicit constraints from the following software expectation.
        
        Expectation:
        Name: {expectation.get('name')}
        Description: {expectation.get('description')}
        Acceptance Criteria:
        {self._format_list_items(expectation.get('acceptance_criteria', []))}
        
        Please identify any implicit constraints that are not explicitly stated but are implied by the expectation.
        
        Format your response as a list of constraints, one per line, starting with a dash.
        """
        
        response = self.llm_router.generate(prompt)
        
        content = response.get("content", "")
        
        constraints = []
        
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("-"):
                constraint = line[1:].strip()
                if constraint:
                    constraints.append(constraint)
                    
        return constraints
        
    def _self_validate_code(self, code, key_concepts, constraints):
        """Perform self-validation on generated code
        
        Args:
            code: Generated code dictionary
            key_concepts: Dictionary of key concepts
            constraints: List of constraints
            
        Returns:
            Validation result dictionary
        """
        import json
        
        code_json = json.dumps(code, indent=2)
        concepts_json = json.dumps(key_concepts, indent=2)
        constraints_text = "\n".join([f"- {constraint}" for constraint in constraints])
        
        prompt = f"""
        You are an expert code reviewer. Your task is to validate the following code against the provided concepts and constraints.
        
        Code:
        {code_json}
        
        Key Concepts:
        {concepts_json}
        
        Constraints:
        {constraints_text}
        
        Please review the code and identify any issues or missing elements.
        
        Format your response as a JSON object with the following structure:
        ```json
        {{
            "valid": true/false,
            "issues": [
                {{
                    "type": "missing_concept/constraint_violation/etc.",
                    "description": "Description of the issue",
                    "suggestion": "Suggestion for fixing the issue"
                }},
                ...
            ]
        }}
        ```
        
        If there are no issues, set "valid" to true and provide an empty "issues" array.
        """
        
        response = self.llm_router.generate(prompt)
        
        validation_result = self._parse_validation_result(response)
        
        return validation_result
        
    def _fix_code_issues(self, code, issues):
        """Fix issues in generated code
        
        Args:
            code: Generated code dictionary
            issues: List of issues to fix
            
        Returns:
            Fixed code dictionary
        """
        import json
        
        code_json = json.dumps(code, indent=2)
        issues_json = json.dumps(issues, indent=2)
        
        prompt = f"""
        You are an expert software developer. Your task is to fix the following issues in the provided code.
        
        Code:
        {code_json}
        
        Issues:
        {issues_json}
        
        Please provide the fixed code.
        
        Format your response as a JSON object with the following structure:
        ```json
        {{
            "language": "python/javascript/etc.",
            "files": [
                {{
                    "path": "path/to/file.ext",
                    "content": "file content here"
                }},
                ...
            ],
            "explanation": "Explanation of your fixes"
        }}
        ```
        """
        
        response = self.llm_router.generate(prompt, {"temperature": 0.2})
        
        fixed_code = self._parse_code_from_response(response)
        
        return fixed_code
        
    def _parse_validation_result(self, response):
        """Parse validation result from LLM response
        
        Args:
            response: LLM response
            
        Returns:
            Validation result dictionary
        """
        content = response.get("content", "")
        
        import re
        json_match = re.search(r"```json\s+(.*?)\s+```", content, re.DOTALL)
        
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = content
            
        import json
        try:
            validation_result = json.loads(json_content)
        except Exception:
            validation_result = {
                "valid": True,
                "issues": []
            }
            
        return validation_result
        
    def _format_list_items(self, items):
        """Format list items for prompt
        
        Args:
            items: List of items
            
        Returns:
            Formatted text
        """
        return "\n".join([f"- {item}" for item in items])
        
    def _collect_metadata(self):
        """Collect metadata about the generation process
        
        Returns:
            Process metadata dictionary
        """
        from datetime import datetime
        
        return {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "generator_id": id(self)
        }
