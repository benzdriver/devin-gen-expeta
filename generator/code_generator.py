"""
Code Generator Module for Expeta 2.0

This module extends the Generator to provide specific code generation capabilities.
"""

from .generator import Generator

class CodeGenerator(Generator):
    """Code generator specifically for generating complete code implementations"""

    def generate_code(self, generation_input):
        """Generate code based on expectations and target technology
        
        Args:
            generation_input: Dictionary containing expectations, target technology, and output format
            
        Returns:
            Dictionary with generated files and metadata
        """
        expectations = generation_input.get("expectations", {})
        target_tech = generation_input.get("target_technology", {})
        output_format = generation_input.get("output_format", "complete_files")
        
        top_level = expectations.get("top_level_expectation", {})
        sub_expectations = expectations.get("sub_expectations", [])
        
        prompt = self._create_comprehensive_code_prompt(top_level, sub_expectations, target_tech, output_format)
        
        response = self.llm_router.generate(prompt, {"temperature": 0.2})
        
        result = self._parse_comprehensive_code(response)
        
        result["metadata"] = {
            "expectation_id": top_level.get("id", "unknown"),
            "generation_timestamp": self._collect_metadata().get("timestamp"),
            "target_technology": target_tech
        }
        
        return result
    
    def _create_comprehensive_code_prompt(self, top_level, sub_expectations, target_tech, output_format):
        """Create a comprehensive prompt for code generation
        
        Args:
            top_level: Top-level expectation dictionary
            sub_expectations: List of sub-expectation dictionaries
            target_tech: Target technology dictionary
            output_format: Desired output format
            
        Returns:
            Prompt text
        """
        import json
        
        sub_exp_text = ""
        for i, sub_exp in enumerate(sub_expectations):
            sub_exp_text += f"\n{i+1}. {sub_exp.get('name')}: {sub_exp.get('description')}\n"
            
            if "acceptance_criteria" in sub_exp and sub_exp["acceptance_criteria"]:
                sub_exp_text += "   Acceptance Criteria:\n"
                for criterion in sub_exp["acceptance_criteria"]:
                    sub_exp_text += f"   - {criterion}\n"
            
            if "constraints" in sub_exp and sub_exp["constraints"]:
                sub_exp_text += "   Constraints:\n"
                for constraint in sub_exp["constraints"]:
                    sub_exp_text += f"   - {constraint}\n"
        
        tech_text = json.dumps(target_tech, indent=2)
        
        return f"""
        You are an expert software developer. Your task is to generate complete, production-ready code for the following project:
        
        PROJECT OVERVIEW:
        Name: {top_level.get('name')}
        Description: {top_level.get('description')}
        
        ACCEPTANCE CRITERIA:
        {self._format_list_items(top_level.get('acceptance_criteria', []))}
        
        CONSTRAINTS:
        {self._format_list_items(top_level.get('constraints', []))}
        
        DETAILED REQUIREMENTS:
        {sub_exp_text}
        
        TARGET TECHNOLOGY:
        {tech_text}
        
        OUTPUT FORMAT:
        {output_format}
        
        Please generate complete, well-structured code that implements all requirements. Your code should be:
        1. Fully functional and ready to run
        2. Well-documented with comments explaining key components
        3. Following best practices for the target technology
        4. Organized in a logical file structure
        5. Aesthetically pleasing and user-friendly (for UI components)
        
        Format your response as a JSON object with the following structure:
        ```json
        {{
            "files": [
                {{
                    "filename": "path/to/file.ext",
                    "content": "file content here"
                }},
                ...
            ],
            "instructions": "Instructions for running or deploying the code"
        }}
        ```
        
        Ensure that all files necessary for the project are included and that the code is complete and functional.
        """
    
    def _parse_comprehensive_code(self, response):
        """Parse comprehensive code from LLM response
        
        Args:
            response: LLM response
            
        Returns:
            Dictionary with files and instructions
        """
        content = response.get("content", "")
        
        import re
        import json
        
        json_match = re.search(r"```json\s+(.*?)\s+```", content, re.DOTALL)
        
        if json_match:
            json_content = json_match.group(1)
        else:
            json_content = content
        
        try:
            result = json.loads(json_content)
        except Exception:
            result = self._extract_code_blocks_from_response(content)
        
        if "files" not in result:
            result["files"] = []
        
        if "instructions" not in result:
            result["instructions"] = "No specific instructions provided."
        
        return result
    
    def _extract_code_blocks_from_response(self, content):
        """Extract code blocks from response when JSON parsing fails
        
        Args:
            content: Response content
            
        Returns:
            Dictionary with files and instructions
        """
        import re
        
        code_blocks = re.findall(r"```(\w+)(?::([^\n]+))?\n(.*?)```", content, re.DOTALL)
        
        files = []
        instructions = "Instructions extracted from response:"
        
        for i, block in enumerate(code_blocks):
            language, filename, code = block
            
            if not filename:
                ext = language if language != "language" else "txt"
                filename = f"file{i+1}.{ext}"
            
            files.append({
                "filename": filename,
                "content": code.strip()
            })
        
        instruction_blocks = re.split(r"```.*?```", content, flags=re.DOTALL)
        for block in instruction_blocks:
            if block.strip():
                instructions += "\n" + block.strip()
        
        return {
            "files": files,
            "instructions": instructions
        }
