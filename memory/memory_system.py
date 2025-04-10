"""
Memory System Module for Expeta 2.0

This module provides storage and retrieval functionality for expectations,
code generations, and validation results.
"""

class MemorySystem:
    """Memory system, stores and retrieves system data"""

    def __init__(self, storage_provider=None):
        """Initialize with optional storage provider
        
        Args:
            storage_provider: Optional storage provider. If not provided, default storage will be used.
        """
        self.storage = storage_provider or self._create_default_storage()

    def record_expectations(self, expectation_data):
        """Record expectation data
        
        Args:
            expectation_data: Expectation data to record
            
        Returns:
            Storage result
        """
        return self.storage.store("expectations", expectation_data)

    def record_generation(self, generation_data):
        """Record code generation data
        
        Args:
            generation_data: Generation data to record
            
        Returns:
            Storage result
        """
        return self.storage.store("generations", generation_data)

    def record_validation(self, validation_data):
        """Record validation result
        
        Args:
            validation_data: Validation data to record
            
        Returns:
            Storage result
        """
        return self.storage.store("validations", validation_data)
        
    def record_llm_request(self, request_data):
        """Record LLM request data
        
        Args:
            request_data: LLM request data to record
            
        Returns:
            Storage result
        """
        return self.storage.store("llm_requests", request_data)

    def get_expectation(self, expectation_id):
        """Get expectation data
        
        Args:
            expectation_id: ID of the expectation to retrieve
            
        Returns:
            Expectation data
        """
        return self.storage.retrieve("expectations", {"id": expectation_id})

    def get_code_for_expectation(self, expectation_id):
        """Get code generated for an expectation
        
        Args:
            expectation_id: ID of the expectation
            
        Returns:
            Generated code data
        """
        return self.storage.retrieve("generations", {"expectation_id": expectation_id})

    def get_validation_results(self, expectation_id=None, code_id=None):
        """Get validation results
        
        Args:
            expectation_id: Optional ID of the expectation
            code_id: Optional ID of the code
            
        Returns:
            Validation results matching the query
        """
        query = {}
        if expectation_id:
            query["expectation_id"] = expectation_id
        if code_id:
            query["code_id"] = code_id
        return self.storage.retrieve("validations", query)
        
    def get_all_expectations(self):
        """Get all stored expectations
        
        Returns:
            List of all stored expectations
        """
        return self.storage.retrieve("expectations", {})

    def _create_default_storage(self):
        """Create default storage provider
        
        Returns:
            Default storage provider instance
        """
        from .storage.file_storage import FileStorage
        return FileStorage()
