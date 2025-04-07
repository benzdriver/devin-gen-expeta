"""
REST API Access Layer for Expeta 2.0

This module provides RESTful API endpoints for external systems to interact with Expeta.
"""

import os
import sys
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, Body, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from utils.token_tracker import TokenTracker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from orchestrator.orchestrator import Expeta
from utils.env_loader import load_dotenv

load_dotenv()

app = FastAPI(
    title="Expeta REST API",
    description="RESTful API for Expeta 2.0 - Semantic-Driven Software Development",
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

class RequirementRequest(BaseModel):
    text: str
    
class ExpectationRequest(BaseModel):
    expectation: Dict[str, Any]
    
class ExpectationResponse(BaseModel):
    id: str
    name: str
    description: str
    acceptance_criteria: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    
class GenerationResponse(BaseModel):
    language: str
    files: List[Dict[str, str]]
    
class ValidationResponse(BaseModel):
    passed: bool
    semantic_match: Dict[str, Any]
    test_results: Dict[str, Any]
    
class ProcessResponse(BaseModel):
    requirement: Optional[str] = None
    clarification: Dict[str, Any]
    generation: Dict[str, Any]
    validation: Dict[str, Any]
    success: bool

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token"""
    if credentials.credentials != "valid-token":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

@app.get("/")
async def root():
    """Root endpoint, returns basic API information"""
    return {
        "name": "Expeta REST API",
        "version": "0.1.0",
        "description": "Semantic-Driven Software Development"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/process", response_model=ProcessResponse)
async def process_requirement(request: RequirementRequest):
    """Process a natural language requirement through the entire workflow"""
    try:
        result = expeta.process_requirement(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/expectation")
async def process_expectation(request: ExpectationRequest):
    """Process an expectation directly (skip requirement clarification)"""
    try:
        result = expeta.process_expectation(request.expectation)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clarify")
async def clarify_requirement(request: RequirementRequest):
    """Clarify a natural language requirement"""
    try:
        result = expeta.clarifier.clarify_requirement(request.text)
        expeta.clarifier.sync_to_memory(expeta.memory_system)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_code(expectation: Dict[str, Any] = Body(...)):
    """Generate code from an expectation"""
    try:
        result = expeta.generator.generate(expectation)
        expeta.generator.sync_to_memory(expeta.memory_system)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/validate")
async def validate_code(
    code: Dict[str, Any] = Body(..., embed=True),
    expectation: Dict[str, Any] = Body(..., embed=True)
):
    """Validate code against an expectation"""
    try:
        result = expeta.validator.validate(code, expectation)
        expeta.validator.sync_to_memory(expeta.memory_system)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/expectations/{expectation_id}")
async def get_expectation(expectation_id: str):
    """Get expectation by ID"""
    try:
        result = expeta.memory_system.get_expectation(expectation_id)
        if not result:
            raise HTTPException(status_code=404, detail="Expectation not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/generations/{expectation_id}")
async def get_generation(expectation_id: str):
    """Get code generation for an expectation"""
    try:
        result = expeta.memory_system.get_code_for_expectation(expectation_id)
        if not result:
            raise HTTPException(status_code=404, detail="Generation not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/validations/{expectation_id}")
async def get_validation(expectation_id: str):
    """Get validation results for an expectation"""
    try:
        result = expeta.memory_system.get_validation_results(expectation_id=expectation_id)
        if not result:
            raise HTTPException(status_code=404, detail="Validation not found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/protected")
async def protected_route(token: str = Depends(verify_token)):
    """Protected route example"""
    return {"message": "You have access to this protected resource"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
        headers={"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else {}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )

@app.middleware("http")
async def add_response_metadata(request: Request, call_next):
    """Add metadata to responses"""
    response = await call_next(request)
    
    if response.headers.get("content-type") == "application/json":
        try:
            if hasattr(response, "body"):
                content = response.body
            elif hasattr(response, "body_iterator"):
                return response
            else:
                return response
            
            import json
            try:
                data = json.loads(content)
                
                if isinstance(data, dict):
                    data["_metadata"] = {
                        "timestamp": import_time(),
                        "api_version": "0.1.0",
                        "request_path": request.url.path
                    }
                    
                    return JSONResponse(
                        content=data,
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
            except:
                pass
        except:
            pass
    
    return response

def import_time():
    """Get current time in ISO format"""
    from datetime import datetime
    return datetime.now().isoformat()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
