from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HeuristicFinding, Evaluation
from app.schemas.heuristic import HeuristicFindingResponse, HeuristicFindingsList

router = APIRouter(prefix="/api/evaluations", tags=["heuristics"])


@router.get("/{evaluation_id}/heuristics", response_model=HeuristicFindingsList)
def get_heuristics(evaluation_id: str, db: Session = Depends(get_db)):
    """Get all heuristic findings for an evaluation."""
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

    # Get all findings
    findings = (
        db.query(HeuristicFinding)
        .filter(HeuristicFinding.evaluation_id == evaluation_id)
        .order_by(HeuristicFinding.severity_score.desc())
        .all()
    )

    return {"findings": findings, "total": len(findings)}


@router.get(
    "/{evaluation_id}/heuristics/{heuristic_type}",
    response_model=HeuristicFindingResponse,
)
def get_heuristic_detail(
    evaluation_id: str, heuristic_type: str, db: Session = Depends(get_db)
):
    """Get detailed analysis for specific heuristic type."""
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

    # Get specific finding
    finding = (
        db.query(HeuristicFinding)
        .filter(
            HeuristicFinding.evaluation_id == evaluation_id,
            HeuristicFinding.heuristic_type == heuristic_type,
        )
        .first()
    )

    if not finding:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Heuristic finding '{heuristic_type}' not found for evaluation {evaluation_id}",
                }
            },
        )

    return finding
