from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.models.recommendation import Impact, Difficulty


class RecommendationResponse(BaseModel):
    """Schema for recommendation response."""

    id: str
    evaluation_id: str
    heuristic_type: str
    priority: int
    action_title: str
    technical_description: str
    simplified_description: str
    estimated_impact: Impact
    implementation_difficulty: Difficulty
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationsList(BaseModel):
    """Schema for list of recommendations."""

    recommendations: List[RecommendationResponse]
    total: int


class RecommendationsQuery(BaseModel):
    """Schema for recommendations query parameters."""

    mode: str = "technical"  # technical, simplified, or both
