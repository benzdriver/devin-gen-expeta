"""
Clarifier Module for Expeta 2.0

This module converts natural language requirements into structured semantic expectations
and decomposes high-level expectations into sub-expectations.
"""

class Clarifier:
    """Requirement clarifier, decomposes high-level expectations into sub-expectations"""

    def __init__(self, llm_router=None):
        """Initialize with optional LLM router
        
        Args:
            llm_router: Optional LLM router. If not provided, default router will be created.
        """
        self.llm_router = llm_router or self._create_default_llm_router()
        self._processed_expectations = []

    def clarify_requirement(self, requirement_text):
        """Clarify fuzzy requirements into structured expectations
        
        Args:
            requirement_text: Natural language requirement text
            
        Returns:
            Dictionary with top-level expectation, sub-expectations, and process metadata
        """
        top_level_expectation = self._extract_top_level_expectation(requirement_text)
        sub_expectations = self._decompose_to_sub_expectations(top_level_expectation)

        result = {
            "top_level_expectation": top_level_expectation,
            "sub_expectations": sub_expectations,
            "process_metadata": self._collect_process_metadata()
        }

        self._processed_expectations.append(result)

        return result

    def sync_to_memory(self, memory_system):
        """Sync processed results to memory system (delayed call)
        
        Args:
            memory_system: Memory system to sync to
            
        Returns:
            Dictionary with sync results
        """
        for expectation_data in self._processed_expectations:
            memory_system.record_expectations(expectation_data)

        synced_count = len(self._processed_expectations)
        self._processed_expectations = []

        return {"synced_count": synced_count}
        
    def _create_default_llm_router(self):
        """Create default LLM router
        
        Returns:
            Default LLM router instance
        """
        from ..llm_router.llm_router import LLMRouter
        return LLMRouter()
        
    def _extract_top_level_expectation(self, requirement_text):
        """Extract top-level expectation from requirement text
        
        Args:
            requirement_text: Natural language requirement text
            
        Returns:
            Top-level expectation dictionary
        """
        prompt = self._create_extraction_prompt(requirement_text)
        
        response = self.llm_router.generate(prompt)
        
        expectation = self._parse_expectation_from_response(response)
        
        expectation["source_text"] = requirement_text
        expectation["level"] = "top"
        expectation["id"] = self._generate_expectation_id()
        
        return expectation
        
    def _decompose_to_sub_expectations(self, top_level_expectation):
        """Decompose top-level expectation into sub-expectations
        
        Args:
            top_level_expectation: Top-level expectation dictionary
            
        Returns:
            List of sub-expectation dictionaries
        """
        prompt = self._create_decomposition_prompt(top_level_expectation)
        
        response = self.llm_router.generate(prompt)
        
        sub_expectations = self._parse_sub_expectations_from_response(response)
        
        for sub_exp in sub_expectations:
            sub_exp["parent_id"] = top_level_expectation["id"]
            sub_exp["level"] = "sub"
            sub_exp["id"] = self._generate_expectation_id()
            
        return sub_expectations
        
    def _create_extraction_prompt(self, requirement_text):
        """Create prompt for extracting top-level expectation
        
        Args:
            requirement_text: Natural language requirement text
            
        Returns:
            Prompt text
        """
        return f"""
        You are an expert software requirements analyst. Your task is to extract the core semantic expectation from the following requirement text.
        
        Focus on WHAT the system should do, not HOW it should be implemented. Avoid technical implementation details.
        
        Requirement text:
        {requirement_text}
        
        Please provide a clear, concise semantic expectation in the following format:
        
        ```yaml
        name: [Short name for the expectation]
        description: [Clear description of what is expected]
        acceptance_criteria:
          - [Criterion 1]
          - [Criterion 2]
          ...
        constraints:
          - [Constraint 1]
          - [Constraint 2]
          ...
        ```
        """
        
    def _create_decomposition_prompt(self, top_level_expectation):
        """Create prompt for decomposing top-level expectation
        
        Args:
            top_level_expectation: Top-level expectation dictionary
            
        Returns:
            Prompt text
        """
        return f"""
        You are an expert software requirements analyst. Your task is to decompose the following high-level expectation into smaller, more specific sub-expectations.
        
        Focus on WHAT each component should do, not HOW it should be implemented. Avoid technical implementation details.
        
        High-level expectation:
        Name: {top_level_expectation.get('name')}
        Description: {top_level_expectation.get('description')}
        
        Please provide 3-7 sub-expectations in the following format:
        
        ```yaml
        - name: [Short name for sub-expectation 1]
          description: [Clear description of what is expected]
          acceptance_criteria:
            - [Criterion 1]
            - [Criterion 2]
            ...
          constraints:
            - [Constraint 1]
            - [Constraint 2]
            ...
            
        - name: [Short name for sub-expectation 2]
          ...
        ```
        
        Ensure that the sub-expectations:
        1. Are logically coherent with each other
        2. Collectively fulfill the high-level expectation
        3. Are at an appropriate level of granularity (not too broad or too specific)
        4. Focus on semantic meaning, not implementation details
        """
        
    def _parse_expectation_from_response(self, response):
        """Parse expectation from LLM response
        
        Args:
            response: LLM response
            
        Returns:
            Expectation dictionary
        """
        content = response.get("content", "")
        
        import re
        yaml_match = re.search(r"```yaml\s+(.*?)\s+```", content, re.DOTALL)
        
        if yaml_match:
            yaml_content = yaml_match.group(1)
        else:
            yaml_content = content
            
        import yaml
        try:
            expectation = yaml.safe_load(yaml_content)
            if expectation is None:
                expectation = {
                    "name": "Default Expectation",
                    "description": "Generated from unparseable response",
                    "acceptance_criteria": [],
                    "constraints": []
                }
        except Exception:
            expectation = self._simple_parse_expectation(content)
        
        if not isinstance(expectation, dict):
            expectation = {
                "name": "Default Expectation",
                "description": str(expectation) if expectation else "Generated from unparseable response",
                "acceptance_criteria": [],
                "constraints": []
            }
            
        return expectation
        
    def _parse_sub_expectations_from_response(self, response):
        """Parse sub-expectations from LLM response
        
        Args:
            response: LLM response
            
        Returns:
            List of sub-expectation dictionaries
        """
        content = response.get("content", "")
        
        import re
        yaml_match = re.search(r"```yaml\s+(.*?)\s+```", content, re.DOTALL)
        
        if yaml_match:
            yaml_content = yaml_match.group(1)
        else:
            yaml_content = content
            
        import yaml
        try:
            if not yaml_content.strip().startswith("-"):
                yaml_content = "- " + yaml_content.replace("\n- ", "\n\n- ")
                
            sub_expectations = yaml.safe_load(yaml_content)
            
            if sub_expectations is None:
                sub_expectations = [{
                    "name": "Default Sub-Expectation",
                    "description": "Generated from unparseable response",
                    "acceptance_criteria": [],
                    "constraints": []
                }]
            elif not isinstance(sub_expectations, list):
                sub_expectations = [sub_expectations]
                
        except Exception:
            sub_expectations = self._simple_parse_sub_expectations(content)
        
        for i, sub_exp in enumerate(sub_expectations):
            if sub_exp is None or not isinstance(sub_exp, dict):
                sub_expectations[i] = {
                    "name": f"Default Sub-Expectation {i+1}",
                    "description": str(sub_exp) if sub_exp else "Generated from unparseable response",
                    "acceptance_criteria": [],
                    "constraints": []
                }
            
        return sub_expectations
        
    def _simple_parse_expectation(self, content):
        """Simple parsing for expectation when YAML parsing fails
        
        Args:
            content: Text content to parse
            
        Returns:
            Expectation dictionary
        """
        lines = content.strip().split("\n")
        expectation = {
            "name": "",
            "description": "",
            "acceptance_criteria": [],
            "constraints": []
        }
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
                
            if line.lower().startswith("name:"):
                expectation["name"] = line[5:].strip()
            elif line.lower().startswith("description:"):
                expectation["description"] = line[12:].strip()
            elif line.lower() == "acceptance_criteria:":
                current_section = "acceptance_criteria"
            elif line.lower() == "constraints:":
                current_section = "constraints"
            elif line.startswith("-") and current_section:
                expectation[current_section].append(line[1:].strip())
                
        return expectation
        
    def _simple_parse_sub_expectations(self, content):
        """Simple parsing for sub-expectations when YAML parsing fails
        
        Args:
            content: Text content to parse
            
        Returns:
            List of sub-expectation dictionaries
        """
        import re
        blocks = re.split(r"\n\s*-\s*name:", content)
        
        sub_expectations = []
        
        for i, block in enumerate(blocks):
            if i == 0 and not block.strip().lower().startswith("name:"):
                continue
                
            if i > 0:
                block = "name:" + block
                
            expectation = self._simple_parse_expectation(block)
            sub_expectations.append(expectation)
            
        return sub_expectations
        
    def _collect_process_metadata(self):
        """Collect metadata about the clarification process
        
        Returns:
            Process metadata dictionary
        """
        from datetime import datetime
        
        return {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "clarifier_id": id(self)
        }
        
    def _generate_expectation_id(self):
        """Generate unique ID for expectation
        
        Returns:
            Unique ID string
        """
        import uuid
        return f"exp-{uuid.uuid4().hex[:8]}"
