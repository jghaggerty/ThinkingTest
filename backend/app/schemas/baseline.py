from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


class StatisticalParams(BaseModel):
    """Schema for statistical parameters."""

    mean: float
    std_dev: float
    sample_size: int


class ZoneThresholds(BaseModel):
    """Schema for zone threshold configuration."""

    green_zone_max: Optional[float] = None
    yellow_zone_max: Optional[float] = None


class BaselineCreate(BaseModel):
    """Schema for creating a baseline."""

    evaluation_id: str
    zone_thresholds: Optional[ZoneThresholds] = None


class BaselineResponse(BaseModel):
    """Schema for baseline response."""

    id: str
    name: str
    green_zone_max: float
    yellow_zone_max: float
    statistical_params: Dict
    created_at: datetime

    class Config:
        from_attributes = True


class TrendData(BaseModel):
    """Schema for trend data."""

    timestamp: datetime
    score: float
    zone: str


class TrendsResponse(BaseModel):
    """Schema for longitudinal trends response."""

    evaluation_id: str
    current_zone: str
    time_series: list
    drift_alerts: list
