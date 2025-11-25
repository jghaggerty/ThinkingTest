from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from app.models.evaluation import EvaluationStatus, ZoneStatus


class EvaluationCreate(BaseModel):
    """Schema for creating a new evaluation."""

    ai_system_name: str = Field(..., min_length=1, max_length=200)
    heuristic_types: List[str] = Field(..., min_items=1)
    iteration_count: int = Field(..., ge=10, le=100)

    @validator("heuristic_types")
    def validate_heuristic_types(cls, v):
        valid_types = {
            "anchoring",
            "loss_aversion",
            "sunk_cost",
            "confirmation_bias",
            "availability_heuristic",
        }
        for htype in v:
            if htype not in valid_types:
                raise ValueError(
                    f"Invalid heuristic type: {htype}. Must be one of {valid_types}"
                )
        return v


class EvaluationResponse(BaseModel):
    """Schema for evaluation response."""

    id: str
    ai_system_name: str
    heuristic_types: List[str]
    iteration_count: int
    status: EvaluationStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    overall_score: Optional[float] = None
    zone_status: Optional[ZoneStatus] = None

    class Config:
        from_attributes = True


class EvaluationList(BaseModel):
    """Schema for paginated evaluation list."""

    evaluations: List[EvaluationResponse]
    total: int
    limit: int
    offset: int
