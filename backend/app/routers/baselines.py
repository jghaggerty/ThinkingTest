from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Baseline, Evaluation
from app.schemas.baseline import (
    BaselineCreate,
    BaselineResponse,
    TrendsResponse,
)
from app.services.statistical_analyzer import StatisticalAnalyzer

router = APIRouter(prefix="/api/baselines", tags=["baselines"])


@router.post("", response_model=BaselineResponse, status_code=201)
def create_baseline(
    baseline_data: BaselineCreate,
    db: Session = Depends(get_db),
):
    """Create or update statistical baseline."""
    # Verify evaluation exists
    evaluation = (
        db.query(Evaluation).filter(Evaluation.id == baseline_data.evaluation_id).first()
    )
    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Evaluation with id {baseline_data.evaluation_id} not found",
                }
            },
        )

    # Get historical scores (for demo, use current evaluation score repeated)
    historical_scores = []
    if evaluation.overall_score:
        # In a real system, would query multiple evaluation scores
        # For demo, create synthetic history
        historical_scores = [evaluation.overall_score]

    # Calculate baseline
    analyzer = StatisticalAnalyzer()
    baseline_params = analyzer.calculate_baseline(historical_scores)

    # Override with custom thresholds if provided
    if baseline_data.zone_thresholds:
        if baseline_data.zone_thresholds.green_zone_max is not None:
            baseline_params["green_zone_max"] = baseline_data.zone_thresholds.green_zone_max
        if baseline_data.zone_thresholds.yellow_zone_max is not None:
            baseline_params["yellow_zone_max"] = baseline_data.zone_thresholds.yellow_zone_max

    # Create baseline record
    baseline = Baseline(
        name=f"Baseline for {evaluation.ai_system_name}",
        green_zone_max=baseline_params["green_zone_max"],
        yellow_zone_max=baseline_params["yellow_zone_max"],
        statistical_params={
            "mean": baseline_params["mean"],
            "std_dev": baseline_params["std_dev"],
            "sample_size": baseline_params["sample_size"],
        },
    )

    db.add(baseline)
    db.commit()
    db.refresh(baseline)

    return baseline


@router.get("/{baseline_id}", response_model=BaselineResponse)
def get_baseline(baseline_id: str, db: Session = Depends(get_db)):
    """Retrieve baseline configuration and statistics."""
    baseline = db.query(Baseline).filter(Baseline.id == baseline_id).first()

    if not baseline:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Baseline with id {baseline_id} not found",
                }
            },
        )

    return baseline


@router.get("/evaluations/{evaluation_id}/trends", response_model=TrendsResponse)
def get_evaluation_trends(evaluation_id: str, db: Session = Depends(get_db)):
    """Calculate longitudinal trends and zone status."""
    # Verify evaluation exists
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Evaluation with id {evaluation_id} not found",
                }
            },
        )

    if not evaluation.overall_score:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "EVALUATION_FAILED",
                    "message": "Evaluation has not been executed yet",
                }
            },
        )

    # For demo purposes, create synthetic time series data
    # In production, this would query historical evaluations
    time_series = [
        {
            "timestamp": evaluation.created_at.isoformat(),
            "score": evaluation.overall_score,
            "zone": evaluation.zone_status.value if evaluation.zone_status else "unknown",
        }
    ]

    # Calculate baseline for drift detection
    analyzer = StatisticalAnalyzer()
    baseline_params = analyzer.calculate_baseline([evaluation.overall_score])

    # Check for drift (with minimal data, won't detect drift)
    drift_info = analyzer.detect_drift(
        evaluation.overall_score, [evaluation.overall_score]
    )

    drift_alerts = []
    if drift_info.get("has_drift"):
        drift_alerts.append(
            {
                "message": drift_info["message"],
                "z_score": drift_info.get("z_score"),
                "deviation": drift_info.get("deviation"),
            }
        )

    return {
        "evaluation_id": evaluation_id,
        "current_zone": evaluation.zone_status.value if evaluation.zone_status else "unknown",
        "time_series": time_series,
        "drift_alerts": drift_alerts,
    }
