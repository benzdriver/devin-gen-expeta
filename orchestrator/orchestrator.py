"""
Orchestrator Module for Expeta 2.0

This module coordinates the workflow between all other modules and provides
a unified interface for the system.
"""

class Expeta:
    """Expeta system main orchestrator, coordinates work between modules"""

    def __init__(self, config=None):
        """Initialize Expeta system
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or self._load_default_config()
        
        self.mock_mode = self.config.get("mock_mode", False)
        if self.mock_mode:
            print("Expeta initialized in mock mode - using simulated responses")

        self._clarifier = None
        self._generator = None
        self._validator = None
        self._memory_system = None
        self._llm_router = None
        self._semantic_mediator = None

    @property
    def clarifier(self):
        """Get Clarifier instance (lazy initialization)
        
        Returns:
            Clarifier instance
        """
        if not self._clarifier:
            self._clarifier = self._create_clarifier()
        return self._clarifier

    @property
    def generator(self):
        """Get Generator instance (lazy initialization)
        
        Returns:
            Generator instance
        """
        if not self._generator:
            self._generator = self._create_generator()
        return self._generator

    @property
    def validator(self):
        """Get Validator instance (lazy initialization)
        
        Returns:
            Validator instance
        """
        if not self._validator:
            self._validator = self._create_validator()
        return self._validator

    @property
    def memory_system(self):
        """Get MemorySystem instance (lazy initialization)
        
        Returns:
            MemorySystem instance
        """
        if not self._memory_system:
            self._memory_system = self._create_memory_system()
        return self._memory_system

    @property
    def llm_router(self):
        """Get LLMRouter instance (lazy initialization)
        
        Returns:
            LLMRouter instance
        """
        if not self._llm_router:
            self._llm_router = self._create_llm_router()
        return self._llm_router

    @property
    def semantic_mediator(self):
        """Get SemanticMediator instance (lazy initialization)
        
        Returns:
            SemanticMediator instance
        """
        if not self._semantic_mediator:
            self._semantic_mediator = self._create_semantic_mediator()
        return self._semantic_mediator

    def process_requirement(self, requirement_text):
        """Process complete requirement workflow
        
        Args:
            requirement_text: Natural language requirement text
            
        Returns:
            Dictionary with processing results
        """
        if self.mock_mode:
            from ._mock_data import get_mock_requirement_result
            return get_mock_requirement_result(requirement_text)
        
        clarification = self.clarifier.clarify_requirement(requirement_text)

        code_generation = self.generator.generate(clarification["top_level_expectation"])

        validation = self.validator.validate(
            code_generation["generated_code"],
            clarification["top_level_expectation"]
        )

        self.clarifier.sync_to_memory(self.memory_system)
        self.generator.sync_to_memory(self.memory_system)
        self.validator.sync_to_memory(self.memory_system)

        return {
            "requirement": requirement_text,
            "clarification": clarification,
            "generation": code_generation,
            "validation": validation,
            "success": validation.get("passed", False)
        }

    def process_expectation(self, expectation):
        """Process expectation directly (skip requirement clarification)
        
        Args:
            expectation: Expectation dictionary
            
        Returns:
            Dictionary with processing results
        """
        if self.mock_mode:
            from ._mock_data import get_mock_expectation_result
            return get_mock_expectation_result(expectation)
            
        code_generation = self.generator.generate(expectation)

        validation = self.validator.validate(
            code_generation["generated_code"],
            expectation
        )

        self.generator.sync_to_memory(self.memory_system)
        self.validator.sync_to_memory(self.memory_system)

        return {
            "expectation": expectation,
            "generation": code_generation,
            "validation": validation,
            "success": validation.get("passed", False)
        }
        
    def _load_default_config(self):
        """Load default configuration
        
        Returns:
            Default configuration dictionary
        """
        return {
            "version": "2.0.0",
            "llm_router": {
                "default_provider": "openai",
                "providers": {
                    "openai": {
                        "model": "gpt-4",
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    "anthropic": {
                        "model": "claude-2",
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    "local": {
                        "model": "llama-2-7b",
                        "temperature": 0.7,
                        "max_tokens": 1000
                    }
                },
                "fallback_order": ["openai", "anthropic", "local"]
            },
            "memory_system": {
                "storage_type": "file",
                "storage_path": "~/.expeta/storage"
            }
        }
        
    def _create_clarifier(self):
        """Create Clarifier instance
        
        Returns:
            Clarifier instance
        """
        from clarifier.clarifier import Clarifier
        return Clarifier(llm_router=self.llm_router)
        
    def _create_generator(self):
        """Create Generator instance
        
        Returns:
            Generator instance
        """
        from generator.generator import Generator
        return Generator(llm_router=self.llm_router)
        
    def _create_validator(self):
        """Create Validator instance
        
        Returns:
            Validator instance
        """
        from validator.validator import Validator
        return Validator(llm_router=self.llm_router)
        
    def _create_memory_system(self):
        """Create MemorySystem instance
        
        Returns:
            MemorySystem instance
        """
        from memory.memory_system import MemorySystem
        
        storage_config = self.config.get("memory_system", {})
        storage_type = storage_config.get("storage_type", "file")
        
        if storage_type == "file":
            from memory.storage.file_storage import FileStorage
            storage_path = storage_config.get("storage_path", "~/.expeta/storage")
            storage_provider = FileStorage(base_dir=storage_path)
        else:
            storage_provider = None
            
        return MemorySystem(storage_provider=storage_provider)
        
    def _create_llm_router(self):
        """Create LLMRouter instance
        
        Returns:
            LLMRouter instance
        """
        from llm_router.llm_router import LLMRouter
        
        llm_config = self.config.get("llm_router", {})
        
        return LLMRouter(config=llm_config)
        
    def _create_semantic_mediator(self):
        """Create SemanticMediator instance
        
        Returns:
            SemanticMediator instance
        """
        from semantic_mediator.mediator import SemanticMediator
        return SemanticMediator(llm_router=self.llm_router, memory_system=self.memory_system)
