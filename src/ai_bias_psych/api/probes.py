"""
Probe API endpoints for AI Bias Psychologist.

This module provides REST API endpoints for probe execution and management.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/probes", tags=["probes"])


class ProbeRequest(BaseModel):
    """Request model for probe execution."""
    probe_type: str = Field(..., description="Type of bias probe")
    prompt: str = Field(..., description="Probe prompt")
    model: str = Field(..., description="LLM model to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(1000, gt=0, description="Maximum tokens in response")


class ProbeResponse(BaseModel):
    """Response model for probe execution."""
    request_id: str = Field(..., description="Unique request identifier")
    response: str = Field(..., description="LLM response")
    bias_score: float = Field(..., ge=0.0, le=1.0, description="Bias score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    execution_time_ms: int = Field(..., description="Execution time in milliseconds")


@router.post("/execute", response_model=ProbeResponse)
async def execute_probe(request: ProbeRequest) -> ProbeResponse:
    """
    Execute a bias probe.
    
    Args:
        request: Probe execution request
        
    Returns:
        Probe execution response
        
    Raises:
        HTTPException: If probe execution fails
    """
    # TODO: Implement probe execution
    raise HTTPException(status_code=501, detail="Probe execution not yet implemented")


@router.get("/types")
async def list_probe_types() -> List[str]:
    """
    List available probe types.
    
    Returns:
        List of available probe types
    """
    # TODO: Implement probe type listing
    return ["prospect_theory"]


@router.get("/{probe_type}/variants")
async def list_probe_variants(probe_type: str) -> List[Dict[str, Any]]:
    """
    List variants for a specific probe type.
    
    Args:
        probe_type: Type of bias probe
        
    Returns:
        List of probe variants
        
    Raises:
        HTTPException: If probe type not found
    """
    # TODO: Implement probe variant listing
    if probe_type not in ["prospect_theory"]:
        raise HTTPException(status_code=404, detail="Probe type not found")
    return []
