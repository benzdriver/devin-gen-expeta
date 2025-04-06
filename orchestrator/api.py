"""
API Module for Expeta 2.0

This module provides a FastAPI interface for the Expeta system.
"""

import os
import json
from typing import Dict, Any, Optional, List

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .orchestrator import Expeta

app = FastAPI(
    title="Expeta API",
    description="API for Expeta 2.0 - Semantic-Driven Software Development",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

expeta = Expeta()

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

@app.get("/")
async def root():
    """Root endpoint, returns basic API information"""
    return {
        "name": "Expeta API",
        "version": "0.1.0",
        "description": "Semantic-Driven Software Development"
    }

@app.post("/process", response_model=ProcessResponse)
async def process_requirement(request: RequirementRequest):
    """Process a natural language requirement through the entire workflow"""
    try:
        result = expeta.process_requirement(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/expectation", response_model=ProcessResponse)
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
