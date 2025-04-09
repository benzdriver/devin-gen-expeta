"""
REST API Access Layer for Expeta 2.0

This module provides RESTful API endpoints for external systems to interact with Expeta.
"""

import os
import sys
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, Body, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import io
import zipfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from orchestrator.orchestrator import Expeta
from utils.token_tracker import TokenTracker
from utils.env_loader import load_dotenv
from memory.storage.file_storage import FileStorage

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

config["memory_system"] = {
    "storage_type": "file",
    "storage_path": FileStorage()._get_default_base_dir()
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
        
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.get("/download/expectation/{expectation_id}")
async def download_expectation(expectation_id: str, format: str = "yaml"):
    """Download expectation as YAML or JSON
    
    Args:
        expectation_id: ID of the expectation
        format: Format to download (yaml, json)
    """
    try:
        expectation = expeta.memory_system.get_expectation(expectation_id)
        if not expectation:
            raise HTTPException(status_code=404, detail="Expectation not found")
        
        if isinstance(expectation, list) and len(expectation) > 0:
            expectation = expectation[0]
        
        if format.lower() == "json":
            import json
            content = json.dumps(expectation, indent=2)
            content_type = "application/json"
            filename = f"expectation_{expectation_id}.json"
        else:  # Default to YAML
            import yaml
            content = yaml.dump(expectation, default_flow_style=False)
            content_type = "text/yaml"
            filename = f"expectation_{expectation_id}.yaml"
        
        buffer = io.BytesIO(content.encode('utf-8'))
        
        return StreamingResponse(
            buffer,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory/generations/{expectation_id}")
async def get_generation(expectation_id: str):
    """Get code generation for an expectation"""
    try:
        result = expeta.memory_system.get_code_for_expectation(expectation_id)
        if not result:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        if isinstance(result, list) and len(result) > 0:
            return result[0]
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/code/{expectation_id}")
async def download_code(expectation_id: str, format: str = "zip"):
    """Download generated code for an expectation
    
    Args:
        expectation_id: ID of the expectation
        format: Format to download (zip, tar, individual)
    """
    try:
        generation = expeta.memory_system.get_code_for_expectation(expectation_id)
        if not generation:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        if isinstance(generation, list) and len(generation) > 0:
            generation = generation[0]
        
        files = generation.get("files", [])
        if not files:
            raise HTTPException(status_code=404, detail="No files found in generation")
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                file_name = file.get("name", "unknown.txt")
                file_content = file.get("content", "")
                zip_file.writestr(file_name, file_content)
        
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=code_{expectation_id}.zip"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/file/{expectation_id}/{file_name}")
async def download_single_file(expectation_id: str, file_name: str):
    """Download a single file from generated code
    
    Args:
        expectation_id: ID of the expectation
        file_name: Name of the file to download
    """
    try:
        generation = expeta.memory_system.get_code_for_expectation(expectation_id)
        if not generation:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        if isinstance(generation, list) and len(generation) > 0:
            generation = generation[0]
        
        files = generation.get("files", [])
        if not files:
            raise HTTPException(status_code=404, detail="No files found in generation")
        
        file_data = None
        for file in files:
            if file.get("name") == file_name:
                file_data = file
                break
        
        if not file_data:
            raise HTTPException(status_code=404, detail=f"File {file_name} not found")
        
        content = file_data.get("content", "")
        buffer = io.BytesIO(content.encode('utf-8'))
        
        content_type = "text/plain"
        if file_name.endswith(".py"):
            content_type = "text/x-python"
        elif file_name.endswith(".js"):
            content_type = "application/javascript"
        elif file_name.endswith(".html"):
            content_type = "text/html"
        elif file_name.endswith(".css"):
            content_type = "text/css"
        elif file_name.endswith(".json"):
            content_type = "application/json"
        
        return StreamingResponse(
            buffer,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )
    except HTTPException:
        raise
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
