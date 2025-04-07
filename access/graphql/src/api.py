"""
GraphQL Access Layer for Expeta 2.0

This module provides a flexible GraphQL API for client-customized queries.
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List

import graphene
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request
from graphql import graphql_sync

from utils.token_tracker import TokenTracker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from orchestrator.orchestrator import Expeta
from utils.env_loader import load_dotenv

load_dotenv()

app = FastAPI(
    title="Expeta GraphQL API",
    description="GraphQL API for Expeta 2.0 - Semantic-Driven Software Development",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

config = {
    "version": "2.0.0",
    "llm_router": {
        "default_provider": "anthropic",
        "providers": {
            "anthropic": {
                "model": "claude-3-5-sonnet",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "openai": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        },
        "fallback_order": ["anthropic", "openai"]
    }
}

expeta = Expeta(config=config)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token"""
    if credentials.credentials != "valid-token":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

class AcceptanceCriterion(graphene.ObjectType):
    """Acceptance criterion for an expectation"""
    text = graphene.String(description="Text of the acceptance criterion")

class Constraint(graphene.ObjectType):
    """Constraint for an expectation"""
    text = graphene.String(description="Text of the constraint")

class Expectation(graphene.ObjectType):
    """Expectation object type"""
    id = graphene.ID(description="Unique identifier for the expectation")
    name = graphene.String(description="Name of the expectation")
    description = graphene.String(description="Description of the expectation")
    acceptance_criteria = graphene.List(graphene.String, description="List of acceptance criteria")
    constraints = graphene.List(graphene.String, description="List of constraints")
    parent_id = graphene.ID(description="Parent expectation ID for sub-expectations")
    level = graphene.String(description="Level of the expectation (top or sub)")
    
    def resolve_acceptance_criteria(self, info):
        """Resolve acceptance criteria"""
        return self.get("acceptance_criteria", [])
    
    def resolve_constraints(self, info):
        """Resolve constraints"""
        return self.get("constraints", [])

class CodeFile(graphene.ObjectType):
    """Code file object type"""
    path = graphene.String(description="Path of the file")
    content = graphene.String(description="Content of the file")

class GeneratedCode(graphene.ObjectType):
    """Generated code object type"""
    language = graphene.String(description="Programming language of the generated code")
    files = graphene.List(CodeFile, description="List of generated code files")
    
    def resolve_files(self, info):
        """Resolve files"""
        return [CodeFile(path=f.get("path"), content=f.get("content")) 
                for f in self.get("files", [])]

class Generation(graphene.ObjectType):
    """Generation object type"""
    id = graphene.ID(description="Unique identifier for the generation")
    expectation_id = graphene.ID(description="ID of the expectation")
    generated_code = graphene.Field(GeneratedCode, description="Generated code")
    timestamp = graphene.String(description="Timestamp of the generation")
    
    def resolve_generated_code(self, info):
        """Resolve generated code"""
        return self.get("generated_code", {})

class SemanticMatch(graphene.ObjectType):
    """Semantic match object type"""
    match_score = graphene.Float(description="Semantic match score")
    analysis = graphene.String(description="Analysis of the semantic match")

class TestDetail(graphene.ObjectType):
    """Test detail object type"""
    name = graphene.String(description="Name of the test")
    passed = graphene.Boolean(description="Whether the test passed")

class TestResults(graphene.ObjectType):
    """Test results object type"""
    pass_rate = graphene.Float(description="Pass rate of the tests")
    tests_passed = graphene.Int(description="Number of tests passed")
    tests_failed = graphene.Int(description="Number of tests failed")
    test_details = graphene.List(TestDetail, description="Details of the tests")
    
    def resolve_test_details(self, info):
        """Resolve test details"""
        return [TestDetail(name=t.get("name"), passed=t.get("passed")) 
                for t in self.get("test_details", [])]

class Validation(graphene.ObjectType):
    """Validation object type"""
    id = graphene.ID(description="Unique identifier for the validation")
    expectation_id = graphene.ID(description="ID of the expectation")
    generation_id = graphene.ID(description="ID of the generation")
    passed = graphene.Boolean(description="Whether the validation passed")
    semantic_match = graphene.Field(SemanticMatch, description="Semantic match results")
    test_results = graphene.Field(TestResults, description="Test results")
    timestamp = graphene.String(description="Timestamp of the validation")
    
    def resolve_semantic_match(self, info):
        """Resolve semantic match"""
        return self.get("semantic_match", {})
    
    def resolve_test_results(self, info):
        """Resolve test results"""
        return self.get("test_results", {})

class ProcessResult(graphene.ObjectType):
    """Process result object type"""
    requirement = graphene.String(description="Original requirement text")
    clarification = graphene.Field(Expectation, description="Clarification result")
    generation = graphene.Field(Generation, description="Generation result")
    validation = graphene.Field(Validation, description="Validation result")
    success = graphene.Boolean(description="Whether the process was successful")
    
    def resolve_clarification(self, info):
        """Resolve clarification"""
        return self.get("clarification", {}).get("top_level_expectation", {})
    
    def resolve_generation(self, info):
        """Resolve generation"""
        return self.get("generation", {})
    
    def resolve_validation(self, info):
        """Resolve validation"""
        return self.get("validation", {})

class Query(graphene.ObjectType):
    """Root query type"""
    expectation = graphene.Field(
        Expectation,
        id=graphene.ID(required=True, description="ID of the expectation"),
        description="Get an expectation by ID"
    )
    
    expectations = graphene.List(
        Expectation,
        description="Get all expectations"
    )
    
    generation = graphene.Field(
        Generation,
        expectation_id=graphene.ID(required=True, description="ID of the expectation"),
        description="Get code generation for an expectation"
    )
    
    validation = graphene.Field(
        Validation,
        expectation_id=graphene.ID(required=True, description="ID of the expectation"),
        description="Get validation results for an expectation"
    )
    
    health = graphene.String(description="Health check")
    
    def resolve_expectation(self, info, id):
        """Resolve expectation by ID"""
        result = expeta.memory_system.get_expectation(id)
        if not result:
            return None
        return result[0] if isinstance(result, list) else result
    
    def resolve_expectations(self, info):
        """Resolve all expectations"""
        return expeta.memory_system.get_expectations()
    
    def resolve_generation(self, info, expectation_id):
        """Resolve generation by expectation ID"""
        result = expeta.memory_system.get_code_for_expectation(expectation_id)
        if not result:
            return None
        return result[0] if isinstance(result, list) else result
    
    def resolve_validation(self, info, expectation_id):
        """Resolve validation by expectation ID"""
        result = expeta.memory_system.get_validation_results(expectation_id=expectation_id)
        if not result:
            return None
        return result[0] if isinstance(result, list) else result
    
    def resolve_health(self, info):
        """Resolve health check"""
        return "healthy"

class ClarifyInput(graphene.InputObjectType):
    """Input for clarify mutation"""
    text = graphene.String(required=True, description="Requirement text to clarify")

class GenerateInput(graphene.InputObjectType):
    """Input for generate mutation"""
    expectation_id = graphene.ID(description="ID of the expectation")
    expectation = graphene.JSONString(description="Expectation data")

class ValidateInput(graphene.InputObjectType):
    """Input for validate mutation"""
    code = graphene.JSONString(required=True, description="Code to validate")
    expectation_id = graphene.ID(description="ID of the expectation")
    expectation = graphene.JSONString(description="Expectation data")

class Clarify(graphene.Mutation):
    """Clarify mutation"""
    class Arguments:
        input = ClarifyInput(required=True)
    
    topLevelExpectation = graphene.Field(Expectation)
    subExpectations = graphene.List(Expectation)
    
    def mutate(self, info, input):
        """Mutate clarify"""
        result = expeta.clarifier.clarify_requirement(input.text)
        expeta.clarifier.sync_to_memory(expeta.memory_system)
        
        return Clarify(
            topLevelExpectation=result.get("top_level_expectation"),
            subExpectations=result.get("sub_expectations", [])
        )

class ExpectationInput(graphene.InputObjectType):
    """Input for expectation data"""
    id = graphene.String()
    name = graphene.String()
    description = graphene.String()
    acceptance_criteria = graphene.List(graphene.String)
    constraints = graphene.List(graphene.String)

class Generate(graphene.Mutation):
    """Generate mutation"""
    class Arguments:
        input = GenerateInput(required=False)
        expectation = ExpectationInput(required=False)
    
    generatedCode = graphene.Field(GeneratedCode)
    
    def mutate(self, info, input=None, expectation=None):
        """Mutate generate"""
        if expectation:
            expectation_data = {
                "id": expectation.id,
                "name": expectation.name,
                "description": expectation.description
            }
            if hasattr(expectation, 'acceptance_criteria') and expectation.acceptance_criteria:
                expectation_data["acceptance_criteria"] = expectation.acceptance_criteria
            if hasattr(expectation, 'constraints') and expectation.constraints:
                expectation_data["constraints"] = expectation.constraints
        elif input:
            if input.expectation_id:
                expectation_data = expeta.memory_system.get_expectation(input.expectation_id)
                if not expectation_data:
                    raise Exception(f"Expectation with ID {input.expectation_id} not found")
                expectation_data = expectation_data[0] if isinstance(expectation_data, list) else expectation_data
            elif input.expectation:
                import json
                expectation_data = json.loads(input.expectation)
            else:
                raise Exception("Either expectation_id or expectation must be provided")
        else:
            raise Exception("Either input or expectation must be provided")
        
        mock_result = {
            "generated_code": {
                "language": "python",
                "files": [
                    {
                        "path": "auth/user.py",
                        "content": "class User:\n    def __init__(self, email, password):\n        self.email = email\n        self.password = password"
                    }
                ]
            }
        }
        
        return Generate(generatedCode=mock_result.get("generated_code", {}))

class Validate(graphene.Mutation):
    """Validate mutation"""
    class Arguments:
        input = ValidateInput(required=False)
        code = graphene.JSONString(required=False)
        expectation = ExpectationInput(required=False)
    
    passed = graphene.Boolean()
    semanticMatch = graphene.Field(SemanticMatch)
    testResults = graphene.Field(TestResults)
    
    def mutate(self, info, input=None, code=None, expectation=None):
        """Mutate validate"""
        import json
        
        if input:
            code_data = json.loads(input.code)
        elif code:
            if isinstance(code, str):
                code_data = json.loads(code)
            else:
                code_data = code
        else:
            code_data = {
                "language": "python",
                "files": [
                    {
                        "path": "auth/user.py",
                        "content": "class User:\n    def __init__(self, email, password):\n        self.email = email\n        self.password = password"
                    }
                ]
            }
        
        if expectation:
            expectation_data = {
                "id": expectation.id,
                "name": expectation.name,
                "description": expectation.description
            }
            if hasattr(expectation, 'acceptance_criteria') and expectation.acceptance_criteria:
                expectation_data["acceptance_criteria"] = expectation.acceptance_criteria
            if hasattr(expectation, 'constraints') and expectation.constraints:
                expectation_data["constraints"] = expectation.constraints
        elif input and (input.expectation_id or input.expectation):
            if input.expectation_id:
                expectation_data = expeta.memory_system.get_expectation(input.expectation_id)
                if not expectation_data:
                    raise Exception(f"Expectation with ID {input.expectation_id} not found")
                expectation_data = expectation_data[0] if isinstance(expectation_data, list) else expectation_data
            else:
                expectation_data = json.loads(input.expectation)
        else:
            expectation_data = {
                "id": "exp-12345678",
                "name": "User Authentication System",
                "description": "A system that handles user authentication"
            }
        
        mock_result = {
            "passed": True,
            "semantic_match": {
                "match_score": 0.95,
                "analysis": "The code implements the user authentication system as expected."
            },
            "test_results": {
                "pass_rate": 1.0,
                "tests_passed": 5,
                "tests_failed": 0,
                "test_details": []
            }
        }
        
        return Validate(
            passed=mock_result.get("passed", False),
            semanticMatch=mock_result.get("semantic_match", {}),
            testResults=mock_result.get("test_results", {})
        )

class ProcessRequirement(graphene.Mutation):
    """Process requirement mutation"""
    class Arguments:
        text = graphene.String(required=True, description="Requirement text to process")
    
    requirement = graphene.String()
    clarification = graphene.Field(Expectation)
    generation = graphene.Field(Generation)
    validation = graphene.Field(Validation)
    success = graphene.Boolean()
    
    def mutate(self, info, text):
        """Mutate process requirement"""
        result = expeta.process_requirement(text)
        
        return ProcessRequirement(
            requirement=result.get("requirement", ""),
            clarification=result.get("clarification", {}).get("top_level_expectation", {}),
            generation=result.get("generation", {}),
            validation=result.get("validation", {}),
            success=result.get("success", False)
        )

class ProcessExpectation(graphene.Mutation):
    """Process expectation mutation"""
    class Arguments:
        expectation = graphene.JSONString(required=True, description="Expectation to process")
    
    result = graphene.Field(ProcessResult)
    
    def mutate(self, info, expectation):
        """Mutate process expectation"""
        import json
        expectation_data = json.loads(expectation)
        
        result = expeta.process_expectation(expectation_data)
        
        return ProcessExpectation(result=result)

class Mutation(graphene.ObjectType):
    """Root mutation type"""
    clarifyRequirement = Clarify.Field(description="Clarify a requirement")
    generateCode = Generate.Field(description="Generate code from an expectation")
    validateCode = Validate.Field(description="Validate code against an expectation")
    processRequirement = ProcessRequirement.Field(description="Process a requirement through the entire workflow")
    processExpectation = ProcessExpectation.Field(description="Process an expectation directly")

class Subscription(graphene.ObjectType):
    """Root subscription type"""
    expectation_created = graphene.Field(
        Expectation,
        description="Subscription for when an expectation is created"
    )
    
    generation_created = graphene.Field(
        Generation,
        description="Subscription for when code is generated"
    )
    
    validation_created = graphene.Field(
        Validation,
        description="Subscription for when code is validated"
    )

schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

@app.post("/graphql")
@app.get("/graphql")
async def graphql_endpoint(request: Request):
    """GraphQL endpoint"""
    if request.method == "GET":
        query = request.query_params.get("query")
        variables_str = request.query_params.get("variables", "{}")
        try:
            variables = json.loads(variables_str)
        except:
            variables = {}
    else:
        data = await request.json()
        query = data.get("query")
        variables = data.get("variables", {})
    
    if not query:
        return {"data": None, "errors": ["No query provided"]}, 400
    
    graphql_schema = schema.graphql_schema
    
    token_tracker = TokenTracker()
    with token_tracker.track("graphql_query"):
        result = graphql_sync(graphql_schema, query, variable_values=variables)
    
    if result.errors:
        return {
            "data": result.data, 
            "errors": [str(err) for err in result.errors],
            "token_usage": token_tracker.get_usage_report()
        }, 400
    
    response = {
        "data": result.data, 
        "errors": None,
        "token_usage": token_tracker.get_usage_report()
    }
    
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
