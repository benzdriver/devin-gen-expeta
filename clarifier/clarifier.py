"""
Clarifier Module for Expeta 2.0

This module converts natural language requirements into structured semantic expectations
and decomposes high-level expectations into sub-expectations. It supports multi-round
dialogue for interactive requirement clarification.
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
        self._active_conversations = {}  # Store active conversations by conversation_id

    def clarify_requirement(self, requirement_text, conversation_id=None):
        """Clarify fuzzy requirements into structured expectations
        
        Args:
            requirement_text: Natural language requirement text
            conversation_id: Optional conversation ID for multi-round dialogue
            
        Returns:
            Dictionary with clarification results and conversation state
        """
        if not conversation_id:
            import uuid
            conversation_id = f"conv-{uuid.uuid4().hex[:8]}"
            
        top_level_expectation = self._extract_top_level_expectation(requirement_text)
        
        uncertainty_points = self._detect_uncertainty(top_level_expectation)
        
        conversation = {
            "id": conversation_id,
            "current_expectation": top_level_expectation,
            "previous_messages": [
                {"role": "user", "content": requirement_text}
            ],
            "uncertainty_points": uncertainty_points,
            "stage": "initial"
        }
        
        if uncertainty_points:
            response = self._create_follow_up_questions(uncertainty_points)
            conversation["stage"] = "awaiting_details"
            conversation["previous_messages"].append({"role": "system", "content": response})
            
            self._active_conversations[conversation_id] = conversation
            
            return {
                "conversation_id": conversation_id,
                "response": response,
                "current_expectation": top_level_expectation,
                "stage": "awaiting_details",
                "requires_clarification": True
            }
        
        sub_expectations = self._decompose_to_sub_expectations(top_level_expectation)
        
        result = {
            "top_level_expectation": top_level_expectation,
            "sub_expectations": sub_expectations,
            "process_metadata": self._collect_process_metadata()
        }
        
        self._processed_expectations.append(result)
        
        response = self._create_completion_response(top_level_expectation, sub_expectations)
        conversation["stage"] = "completed"
        conversation["result"] = result
        conversation["previous_messages"].append({"role": "system", "content": response})
        
        self._active_conversations[conversation_id] = conversation
        
        return {
            "conversation_id": conversation_id,
            "response": response,
            "current_expectation": top_level_expectation,
            "stage": "completed",
            "requires_clarification": False,
            "result": result
        }

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
        
    def continue_conversation(self, conversation_id, user_message, context=None):
        """Continue an existing clarification conversation
        
        Args:
            conversation_id: Unique identifier for the conversation
            user_message: User's follow-up message
            context: Optional additional context
            
        Returns:
            Dictionary with updated clarification and response
        """
        conversation = self._active_conversations.get(conversation_id, {})
        
        if not conversation:
            return {
                "error": "No active conversation found with this ID",
                "suggestion": "Start a new clarification with clarify_requirement"
            }
            
        current_expectation = conversation.get("current_expectation", {})
        clarification_stage = conversation.get("stage", "initial")
        uncertainty_points = conversation.get("uncertainty_points", [])
        
        if clarification_stage == "awaiting_details":
            updated_expectation = self._incorporate_clarification(current_expectation, user_message, uncertainty_points)
            new_uncertainty_points = self._detect_uncertainty(updated_expectation)
            
            conversation["current_expectation"] = updated_expectation
            conversation["previous_messages"].append({"role": "user", "content": user_message})
            
            if new_uncertainty_points:
                response = self._create_follow_up_questions(new_uncertainty_points)
                conversation["uncertainty_points"] = new_uncertainty_points
                conversation["stage"] = "awaiting_details"
            else:
                sub_expectations = self._decompose_to_sub_expectations(updated_expectation)
                
                result = {
                    "top_level_expectation": updated_expectation,
                    "sub_expectations": sub_expectations,
                    "process_metadata": self._collect_process_metadata()
                }
                
                self._processed_expectations.append(result)
                
                response = self._create_completion_response(updated_expectation, sub_expectations)
                conversation["stage"] = "completed"
                conversation["result"] = result
        else:
            response = self._create_general_response(user_message, current_expectation)
            conversation["previous_messages"].append({"role": "user", "content": user_message})
        
        self._active_conversations[conversation_id] = conversation
        
        conversation["previous_messages"].append({"role": "system", "content": response})
        
        return {
            "conversation_id": conversation_id,
            "response": response,
            "current_expectation": conversation["current_expectation"],
            "stage": conversation["stage"],
            "result": conversation.get("result")
        }
        
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
        
    def _detect_uncertainty(self, expectation):
        """Detect uncertainty points in an expectation
        
        Args:
            expectation: Expectation dictionary
            
        Returns:
            List of uncertainty points
        """
        uncertainty_points = []
        
        if not expectation.get("name") or expectation.get("name") == "Default Expectation":
            uncertainty_points.append({
                "field": "name",
                "issue": "missing_or_default",
                "message": "The expectation name is missing or uses a default value."
            })
            
        if not expectation.get("description") or len(expectation.get("description", "")) < 10:
            uncertainty_points.append({
                "field": "description",
                "issue": "missing_or_short",
                "message": "The expectation description is missing or too short."
            })
            
        if not expectation.get("acceptance_criteria") or len(expectation.get("acceptance_criteria", [])) < 1:
            uncertainty_points.append({
                "field": "acceptance_criteria",
                "issue": "missing_or_empty",
                "message": "No acceptance criteria specified for this expectation."
            })
            
        vague_terms = ["etc", "and so on", "and more", "various", "several", "some", "many"]
        description = expectation.get("description", "").lower()
        
        for term in vague_terms:
            if term in description:
                uncertainty_points.append({
                    "field": "description",
                    "issue": "vague_term",
                    "message": f"The description contains the vague term '{term}'.",
                    "term": term
                })
                
        if expectation.get("description"):
            semantic_uncertainty = self._detect_semantic_uncertainty(expectation)
            uncertainty_points.extend(semantic_uncertainty)
            
        return uncertainty_points
        
    def _detect_semantic_uncertainty(self, expectation):
        """Use LLM to detect semantic uncertainty in expectation
        
        Args:
            expectation: Expectation dictionary
            
        Returns:
            List of semantic uncertainty points
        """
        prompt = f"""
        You are an expert requirements analyst. Analyze the following software expectation for ambiguity, 
        vagueness, or missing information that would make it difficult to implement.
        
        Expectation:
        Name: {expectation.get('name', 'No name provided')}
        Description: {expectation.get('description', 'No description provided')}
        
        Acceptance Criteria:
        {self._format_list_for_prompt(expectation.get('acceptance_criteria', []))}
        
        Constraints:
        {self._format_list_for_prompt(expectation.get('constraints', []))}
        
        Identify up to 3 specific points of uncertainty that need clarification. For each point:
        1. Identify the specific field (name, description, acceptance_criteria, constraints)
        2. Describe the issue (ambiguity, vagueness, contradiction, etc.)
        3. Explain why it's problematic
        4. Suggest a specific question to ask for clarification
        
        Format your response as a JSON array:
        ```json
        [
          {
            "field": "field_name",
            "issue": "issue_type",
            "message": "Description of the issue",
            "question": "Specific question to ask for clarification"
          }
        ]
        ```
        
        If there are no significant uncertainties, return an empty array: []
        """
        
        response = self.llm_router.generate(prompt)
        content = response.get("content", "")
        
        import re
        import json
        
        json_match = re.search(r"```json\s+(.*?)\s+```", content, re.DOTALL)
        
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = content
            
        try:
            uncertainty_points = json.loads(json_content)
            if not isinstance(uncertainty_points, list):
                uncertainty_points = []
        except Exception:
            uncertainty_points = []
            
        return uncertainty_points
        
    def _format_list_for_prompt(self, items):
        """Format a list for inclusion in a prompt
        
        Args:
            items: List of items
            
        Returns:
            Formatted string
        """
        if not items:
            return "None provided"
            
        return "\n".join([f"- {item}" for item in items])
        
    def _create_follow_up_questions(self, uncertainty_points):
        """Create follow-up questions based on uncertainty points
        
        Args:
            uncertainty_points: List of uncertainty points
            
        Returns:
            Response text with follow-up questions
        """
        if not uncertainty_points:
            return "I have all the information I need. Let me finalize the expectation."
            
        response = "I need some clarification to better understand your requirement:\n\n"
        
        for i, point in enumerate(uncertainty_points):
            question = point.get("question")
            if not question:
                field = point.get("field", "requirement")
                issue = point.get("issue", "unclear")
                
                if field == "name":
                    question = "Could you provide a more specific name for this requirement?"
                elif field == "description":
                    if issue == "vague_term":
                        term = point.get("term", "")
                        question = f"You mentioned '{term}' in the description. Could you be more specific about what this includes?"
                    else:
                        question = "Could you provide a more detailed description of what you need?"
                elif field == "acceptance_criteria":
                    question = "What specific criteria would indicate that this requirement has been successfully implemented?"
                elif field == "constraints":
                    question = "Are there any constraints or limitations that should be considered for this requirement?"
                else:
                    question = "Could you provide more details about this requirement?"
                    
            response += f"{i+1}. {question}\n"
            
        return response
        
    def _incorporate_clarification(self, expectation, user_message, uncertainty_points):
        """Incorporate user clarification into expectation
        
        Args:
            expectation: Current expectation dictionary
            user_message: User's clarification message
            uncertainty_points: List of uncertainty points being addressed
            
        Returns:
            Updated expectation dictionary
        """
        prompt = f"""
        You are an expert requirements analyst. You previously identified some uncertainties in a software expectation.
        The user has provided clarification. Update the expectation based on this clarification.
        
        Current Expectation:
        Name: {expectation.get('name', 'No name provided')}
        Description: {expectation.get('description', 'No description provided')}
        
        Acceptance Criteria:
        {self._format_list_for_prompt(expectation.get('acceptance_criteria', []))}
        
        Constraints:
        {self._format_list_for_prompt(expectation.get('constraints', []))}
        
        Uncertainty Points:
        {self._format_uncertainty_points(uncertainty_points)}
        
        User Clarification:
        {user_message}
        
        Provide an updated version of the expectation that incorporates the user's clarification.
        Format your response as YAML:
        
        ```yaml
        name: Updated name
        description: Updated description
        acceptance_criteria:
          - Updated criterion 1
          - Updated criterion 2
        constraints:
          - Updated constraint 1
          - Updated constraint 2
        ```
        """
        
        response = self.llm_router.generate(prompt)
        updated_expectation = self._parse_expectation_from_response(response)
        
        updated_expectation["id"] = expectation.get("id", self._generate_expectation_id())
        updated_expectation["level"] = expectation.get("level", "top")
        updated_expectation["source_text"] = expectation.get("source_text", "")
        
        return updated_expectation
        
    def _format_uncertainty_points(self, uncertainty_points):
        """Format uncertainty points for inclusion in a prompt
        
        Args:
            uncertainty_points: List of uncertainty points
            
        Returns:
            Formatted string
        """
        if not uncertainty_points:
            return "None"
            
        formatted = ""
        for i, point in enumerate(uncertainty_points):
            field = point.get("field", "unknown")
            issue = point.get("issue", "unclear")
            message = point.get("message", "No details provided")
            question = point.get("question", "")
            
            formatted += f"{i+1}. Field: {field}, Issue: {issue}\n   {message}\n"
            if question:
                formatted += f"   Question: {question}\n"
                
        return formatted
        
    def _create_completion_response(self, expectation, sub_expectations):
        """Create response for completed clarification
        
        Args:
            expectation: Finalized top-level expectation
            sub_expectations: List of sub-expectations
            
        Returns:
            Response text
        """
        response = f"I've finalized your requirement into the following expectation:\n\n"
        response += f"**{expectation.get('name', 'Expectation')}**\n"
        response += f"{expectation.get('description', '')}\n\n"
        
        if expectation.get("acceptance_criteria"):
            response += "Acceptance Criteria:\n"
            for criterion in expectation.get("acceptance_criteria", []):
                response += f"- {criterion}\n"
            response += "\n"
            
        if expectation.get("constraints"):
            response += "Constraints:\n"
            for constraint in expectation.get("constraints", []):
                response += f"- {constraint}\n"
            response += "\n"
            
        if sub_expectations:
            response += "I've also broken this down into sub-expectations:\n\n"
            for i, sub in enumerate(sub_expectations):
                response += f"{i+1}. **{sub.get('name', f'Sub-Expectation {i+1}')}**\n"
                response += f"   {sub.get('description', '')}\n"
                
        response += "\nWould you like me to generate code for this expectation?"
        
        return response
        
    def _create_general_response(self, user_message, expectation):
        """Create general response for messages in completed conversations
        
        Args:
            user_message: User's message
            expectation: Current expectation
            
        Returns:
            Response text
        """
        prompt = f"""
        You are an AI assistant helping with software requirements. The user has already completed
        the clarification process for the following expectation, but has sent a new message.
        
        Expectation:
        Name: {expectation.get('name', 'No name provided')}
        Description: {expectation.get('description', 'No description provided')}
        
        User's new message:
        {user_message}
        
        Respond helpfully to the user's message in the context of this expectation.
        If they're asking for changes to the expectation, explain that they can start
        a new clarification process or provide specific updates they want to make.
        """
        
        response = self.llm_router.generate(prompt)
        return response.get("content", "I understand. What would you like to do next with this expectation?")
