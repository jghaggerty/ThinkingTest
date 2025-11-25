from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.models.heuristic import HeuristicType, Severity


class HeuristicFindingResponse(BaseModel):
    """Schema for heuristic finding response."""

    id: str
    evaluation_id: str
    heuristic_type: HeuristicType
    severity: Severity
    severity_score: float
    confidence_level: float
    detection_count: int
    example_instances: List[str]
    pattern_description: str
    created_at: datetime

    class Config:
        from_attributes = True


class HeuristicFindingsList(BaseModel):
    """Schema for list of heuristic findings."""

    findings: List[HeuristicFindingResponse]
    total: int
