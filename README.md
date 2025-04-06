# Expeta 2.0

A semantic-driven software development system that transforms natural language requirements into working code.

## Core Principles

- **Pure semantic expectations**: Requirements expressed semantically without technical details
- **Module autonomy**: Each module operates independently with delayed external dependencies
- **Semantic validation**: Code validation through semantic understanding rather than interface matching

## Key Components

- **Clarifier**: Transforms natural language requirements into structured expectations
- **Generator**: Creates code based on semantic expectations
- **Validator**: Verifies code against expectations through semantic understanding
- **Memory System**: Stores expectations, code, and validation results
- **Orchestrator**: Coordinates workflow between modules
- **LLM Router**: Manages interactions with large language models
- **Semantic Mediator**: Enables semantic-driven interactions between modules

## Getting Started

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest
```

## Project Structure

The project follows a modular structure with each component in its own directory:

- `orchestrator/`: System orchestration
- `clarifier/`: Requirement clarification
- `generator/`: Code generation
- `validator/`: Code validation
- `memory/`: Data storage and retrieval
- `llm_router/`: LLM interaction
- `semantic_mediator/`: Semantic-driven module interaction
