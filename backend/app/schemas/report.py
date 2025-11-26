"""Schemas for report generation endpoints."""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


class ReportMetadata(BaseModel):
    """Report metadata schema."""
    generated_at: str
    report_type: str
    format_version: str


class EvaluationOverview(BaseModel):
    """Evaluation overview for reports."""
    ai_system_name: str
    evaluation_id: str
    evaluation_date: Optional[str]
    overall_score: Optional[float]
    zone_status: Optional[str]
    total_iterations: int


class KeyFindings(BaseModel):
    """Key findings summary."""
    total_heuristics_detected: int
    severity_breakdown: Dict[str, int]
    critical_issues: int
    high_priority_issues: int


class TopConcern(BaseModel):
    """Top concern schema."""
    heuristic_type: str
    severity: str
    severity_score: float
    detection_count: int
    pattern_description: str


class RiskAssessment(BaseModel):
    """Risk assessment schema."""
    risk_level: str
    assessment: str
    key_concerns: str


class Recommendation(BaseModel):
    """Recommendation schema."""
    priority: str
    recommendation: str


class ExecutiveSummary(BaseModel):
    """Executive summary response schema."""
    report_metadata: ReportMetadata
    evaluation_overview: EvaluationOverview
    key_findings: KeyFindings
    top_concerns: List[TopConcern]
    risk_assessment: RiskAssessment
    recommendations: List[Recommendation]


class JSONReportResponse(BaseModel):
    """Full JSON report response schema."""
    report_metadata: ReportMetadata
    evaluation: Dict[str, Any]
    findings: List[Dict[str, Any]]
    summary: Dict[str, Any]
