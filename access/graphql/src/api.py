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
    matchScore = graphene.Float(description="Semantic match score (camelCase alias)")
    matchScore = graphene.Float(description="Semantic match score (camelCase alias)")
    analysis = graphene.String(description="Analysis of the semantic match")
    
    def resolve_match_score(self, info):
        """Resolve match_score"""
        return self.get("match_score", 0)
    
    def resolve_matchScore(self, info):
        """Resolve matchScore (camelCase alias)"""
        return self.get("match_score", 0)
    
    def resolve_match_score(self, info):
        """Resolve match_score"""
        return self.get("match_score", 0)
    
    def resolve_matchScore(self, info):
        """Resolve matchScore (camelCase alias)"""
        return self.get("match_score", 0)

class TestDetail(graphene.ObjectType):
    """Test detail object type"""
    name = graphene.String(description="Name of the test")
    passed = graphene.Boolean(description="Whether the test passed")

class TestResults(graphene.ObjectType):
    """Test results object type"""
    pass_rate = graphene.Float(description="Pass rate of the tests")
    passRate = graphene.Float(description="Pass rate of the tests (camelCase alias)")
    passRate = graphene.Float(description="Pass rate of the tests (camelCase alias)")
    tests_passed = graphene.Int(description="Number of tests passed")
    tests_failed = graphene.Int(description="Number of tests failed")
    test_details = graphene.List(TestDetail, description="Details of the tests")
    
    def resolve_pass_rate(self, info):
        """Resolve pass_rate"""
        return self.get("pass_rate", 0)
    
    def resolve_passRate(self, info):
        """Resolve passRate (camelCase alias)"""
        return self.get("pass_rate", 0)
    
    def resolve_tests_passed(self, info):
        """Resolve tests_passed"""
        return self.get("tests_passed", 0)
    
    def resolve_tests_failed(self, info):
        """Resolve tests_failed"""
        return self.get("tests_failed", 0)
    
    def resolve_pass_rate(self, info):
        """Resolve pass_rate"""
        return self.get("pass_rate", 0)
    
    def resolve_passRate(self, info):
        """Resolve passRate (camelCase alias)"""
        return self.get("pass_rate", 0)
    
    def resolve_tests_passed(self, info):
        """Resolve tests_passed"""
        return self.get("tests_passed", 0)
    
    def resolve_tests_failed(self, info):
        """Resolve tests_failed"""
        return self.get("tests_failed", 0)
    
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
        text = graphene.String(required=True, description="Requirement text to clarify")
        text = graphene.String(required=True, description="Requirement text to clarify")
    
    topLevelExpectation = graphene.Field(Expectation)
    subExpectations = graphene.List(Expectation)
    
    def mutate(self, info, text):
    def mutate(self, info, text):
        """Mutate clarify"""
        result = expeta.clarifier.clarify_requirement(text)
        result = expeta.clarifier.clarify_requirement(text)
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
        expectation = graphene.Argument(ExpectationInput, description="Expectation data as input object")
        input = graphene.JSONString(description="Expectation data as JSON string")
    
    generatedCode = graphene.Field(GeneratedCode)
    language = graphene.String()
    files = graphene.List(CodeFile)
    generatedCode = graphene.Field(GeneratedCode)
    language = graphene.String()
    files = graphene.List(CodeFile)
    
    def mutate(self, info, expectation=None, input=None):
        """Mutate generate"""
        import json
        
        if expectation:
            expectation_data = {
                "id": expectation.id,
                "name": expectation.name,
                "description": expectation.description,
                "acceptance_criteria": expectation.acceptance_criteria,
                "constraints": expectation.constraints
            }
        elif input:
            expectation_data = json.loads(input)
        else:
            try:
                expectation_data = json.loads(expectation) if isinstance(expectation, str) else expectation
            except (TypeError, json.JSONDecodeError):
                expectation_data = {"name": "Test Expectation", "description": "Test description"}
        
        expectation_data = {k: v for k, v in expectation_data.items() if v is not None}
        
        result = expeta.generator.generate(expectation_data)
        result = expeta.generator.generate(expectation_data)
        expeta.generator.sync_to_memory(expeta.memory_system)
        
        generated_code = result.get("generated_code", {})
        language = generated_code.get("language", "")
        files = generated_code.get("files", [])
        
        file_objects = [
            CodeFile(path=f.get("path"), content=f.get("content"))
            for f in files
        ]
        
        return Generate(
            generatedCode=generated_code,
            language=language,
            files=file_objects
        )
        generated_code = result.get("generated_code", {})
        language = generated_code.get("language", "")
        files = generated_code.get("files", [])
        
        file_objects = [
            CodeFile(path=f.get("path"), content=f.get("content"))
            for f in files
        ]
        
        return Generate(
            generatedCode=generated_code,
            language=language,
            files=file_objects
        )

class Validate(graphene.Mutation):
    """Validate mutation"""
    class Arguments:
        code = graphene.JSONString(required=True, description="Code to validate")
        expectation = graphene.JSONString(description="Expectation data")
        code = graphene.JSONString(required=True, description="Code to validate")
        expectation = graphene.JSONString(description="Expectation data")
    
    passed = graphene.Boolean()
    semanticMatch = graphene.Field(SemanticMatch)
    testResults = graphene.Field(TestResults)
    passed = graphene.Boolean()
    semanticMatch = graphene.Field(SemanticMatch)
    testResults = graphene.Field(TestResults)
    
    def mutate(self, info, code, expectation):
    def mutate(self, info, code, expectation):
        """Mutate validate"""
        import json
        code_data = json.loads(code)
        expectation_data = json.loads(expectation)
        
        result = expeta.validator.validate(code_data, expectation_data)
        code_data = json.loads(code)
        expectation_data = json.loads(expectation)
        
        result = expeta.validator.validate(code_data, expectation_data)
        expeta.validator.sync_to_memory(expeta.memory_system)
        
        return Validate(
            passed=result.get("passed", False),
            semanticMatch=result.get("semantic_match", {}),
            testResults=result.get("test_results", {})
        )
        return Validate(
            passed=result.get("passed", False),
            semanticMatch=result.get("semantic_match", {}),
            testResults=result.get("test_results", {})
        )

class ProcessRequirement(graphene.Mutation):
    """Process requirement mutation"""
    class Arguments:
        text = graphene.String(required=True, description="Requirement text to process")
    
    requirement = graphene.String()
    success = graphene.Boolean()
    clarification = graphene.Field(Expectation)
    generation = graphene.Field(Generation)
    validation = graphene.Field(Validation)
    requirement = graphene.String()
    success = graphene.Boolean()
    clarification = graphene.Field(Expectation)
    generation = graphene.Field(Generation)
    validation = graphene.Field(Validation)
    
    def mutate(self, info, text):
        """Mutate process requirement"""
        result = expeta.process_requirement(text)
        
        return ProcessRequirement(
            requirement=result.get("requirement", ""),
            success=result.get("success", False),
            clarification=result.get("clarification", {}).get("top_level_expectation", {}),
            generation=result.get("generation", {}),
            validation=result.get("validation", {})
        )
        return ProcessRequirement(
            requirement=result.get("requirement", ""),
            success=result.get("success", False),
            clarification=result.get("clarification", {}).get("top_level_expectation", {}),
            generation=result.get("generation", {}),
            validation=result.get("validation", {})
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
