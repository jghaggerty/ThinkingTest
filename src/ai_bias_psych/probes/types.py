"""
Common types and enums for bias probes.

This module contains shared types and enums used across the probe system
to avoid circular import issues.
"""

from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ProbeType(str, Enum):
    """Enumeration of all supported bias probe types."""
    PROSPECT_THEORY = "prospect_theory"
    ANCHORING = "anchoring"
    AVAILABILITY = "availability"
    FRAMING = "framing"
    SUNK_COST = "sunk_cost"
    OPTIMISM = "optimism"
    CONFIRMATION = "confirmation"
    BASE_RATE = "base_rate"
    CONJUNCTION = "conjunction"
    OVERCONFIDENCE = "overconfidence"


class ResponseFormat(str, Enum):
    """Enumeration of supported response formats."""
    FREE_TEXT = "free_text"
    MULTIPLE_CHOICE = "multiple_choice"
    NUMERIC = "numeric"
    BOOLEAN = "boolean"


class ProbeVariant(BaseModel):
    """Configuration for a specific probe variant."""
    id: str = Field(..., description="Unique variant identifier")
    domain: str = Field(..., description="Domain context (health, finance, etc.)")
    prompt: str = Field(..., description="The probe prompt text")
    expected_bias: Optional[str] = Field(None, description="Expected bias pattern")
    response_format: ResponseFormat = Field(
        ResponseFormat.FREE_TEXT, description="Expected response format"
    )
    scoring_params: Dict[str, Any] = Field(
        default_factory=dict, description="Scoring parameters"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional variant metadata"
    )


class ProbeRequest(BaseModel):
    """Request to execute a bias probe."""
    probe_type: str = Field(..., description="Type of bias probe")
    variant_id: str = Field(..., description="Specific variant to use")
    model_provider: str = Field(..., description="LLM provider")
    model_name: str = Field(..., description="LLM model name")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(1000, gt=0, description="Maximum tokens in response")
    session_id: Optional[str] = Field(None, description="Session identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ProbeResponse(BaseModel):
    """Response from a bias probe execution."""
    request_id: str = Field(..., description="Unique request identifier")
    probe_type: str = Field(..., description="Type of bias probe")
    variant_id: str = Field(..., description="Variant that was used")
    model_provider: str = Field(..., description="LLM provider used")
    model_name: str = Field(..., description="LLM model used")
    prompt: str = Field(..., description="Prompt that was sent")
    response: str = Field(..., description="Model's response")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    tokens_used: int = Field(..., description="Number of tokens used")
    temperature: float = Field(..., description="Temperature used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ProbeExecutionResult(BaseModel):
    """Result of executing a bias probe."""
    request_id: str = Field(..., description="Unique request identifier")
    probe_type: ProbeType = Field(..., description="Type of bias probe")
    variant_id: str = Field(..., description="Variant that was used")
    model_provider: str = Field(..., description="LLM provider used")
    model_name: str = Field(..., description="LLM model used")
    prompt: str = Field(..., description="Prompt that was sent")
    response: str = Field(..., description="Model's response")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    tokens_used: int = Field(..., description="Number of tokens used")
    temperature: float = Field(..., description="Temperature used")
    bias_score: float = Field(..., ge=0.0, le=1.0, description="Normalized bias score (0-1)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the bias score")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Execution timestamp"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional execution metadata"
    )
