from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Evaluation, EvaluationStatus, HeuristicFinding
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationResponse,
    EvaluationList,
)
from app.services.heuristic_detector import HeuristicDetector
from app.services.statistical_analyzer import StatisticalAnalyzer
from app.config import settings

router = APIRouter(prefix="/api/evaluations", tags=["evaluations"])


@router.post("", response_model=EvaluationResponse, status_code=201)
def create_evaluation(
    evaluation_data: EvaluationCreate,
    db: Session = Depends(get_db),
):
    """Create a new evaluation run."""
    # Validate iteration count
    if not (
        settings.min_iterations
        <= evaluation_data.iteration_count
        <= settings.max_iterations
    ):
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": f"Iteration count must be between {settings.min_iterations} and {settings.max_iterations}",
                    "details": {
                        "field": "iteration_count",
                        "value": evaluation_data.iteration_count,
                    },
                }
            },
        )

    # Create evaluation
    evaluation = Evaluation(
        ai_system_name=evaluation_data.ai_system_name,
        heuristic_types=evaluation_data.heuristic_types,
        iteration_count=evaluation_data.iteration_count,
        status=EvaluationStatus.PENDING,
    )

    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    return evaluation


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    """Retrieve evaluation details and current status."""
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

    return evaluation


@router.get("", response_model=EvaluationList)
def list_evaluations(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all evaluations with pagination."""
    total = db.query(Evaluation).count()
    evaluations = (
        db.query(Evaluation)
        .order_by(Evaluation.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )

    return {
        "evaluations": evaluations,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("/{evaluation_id}/execute", response_model=EvaluationResponse)
def execute_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    """Run the heuristic analysis simulation."""
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

    if evaluation.status == EvaluationStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "EVALUATION_FAILED",
                    "message": "Evaluation has already been completed",
                }
            },
        )

    try:
        # Update status to running
        evaluation.status = EvaluationStatus.RUNNING
        db.commit()

        # Run heuristic detection
        detector = HeuristicDetector(evaluation.iteration_count)
        findings = detector.run_detection(evaluation.heuristic_types)

        # Save findings to database
        severity_scores = []
        for finding_data in findings:
            finding = HeuristicFinding(
                evaluation_id=evaluation.id,
                heuristic_type=finding_data["heuristic_type"],
                severity=finding_data["severity"],
                severity_score=finding_data["severity_score"],
                confidence_level=finding_data["confidence_level"],
                detection_count=finding_data["detection_count"],
                example_instances=finding_data["example_instances"],
                pattern_description=finding_data["pattern_description"],
            )
            db.add(finding)
            severity_scores.append(finding_data["severity_score"])

        # Calculate overall score
        analyzer = StatisticalAnalyzer()
        overall_score = analyzer.calculate_overall_score(severity_scores)

        # Determine zone status (using default baseline for now)
        baseline = analyzer.calculate_baseline([])
        zone_status = analyzer.determine_zone_status(
            overall_score, baseline["green_zone_max"], baseline["yellow_zone_max"]
        )

        # Update evaluation
        evaluation.overall_score = overall_score
        evaluation.zone_status = zone_status
        evaluation.status = EvaluationStatus.COMPLETED
        evaluation.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(evaluation)

        return evaluation

    except Exception as e:
        evaluation.status = EvaluationStatus.FAILED
        db.commit()
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "EVALUATION_FAILED",
                    "message": f"Evaluation execution failed: {str(e)}",
                }
            },
        )


@router.delete("/{evaluation_id}", status_code=204)
def delete_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    """Remove evaluation from database."""
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

    db.delete(evaluation)
    db.commit()

    return None
