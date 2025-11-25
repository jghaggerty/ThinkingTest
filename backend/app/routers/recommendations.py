from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Recommendation, Evaluation, HeuristicFinding
from app.schemas.recommendation import RecommendationResponse, RecommendationsList
from app.services.recommendation_generator import RecommendationGenerator

router = APIRouter(prefix="/api/evaluations", tags=["recommendations"])


@router.get("/{evaluation_id}/recommendations", response_model=RecommendationsList)
def get_recommendations(
    evaluation_id: str,
    mode: str = Query("technical", regex="^(technical|simplified|both)$"),
    db: Session = Depends(get_db),
):
    """Generate prioritized mitigation recommendations."""
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

    # Check if recommendations already exist
    existing_recommendations = (
        db.query(Recommendation)
        .filter(Recommendation.evaluation_id == evaluation_id)
        .all()
    )

    if existing_recommendations:
        # Return existing recommendations
        formatted = RecommendationGenerator.format_for_mode(
            [
                {
                    "id": rec.id,
                    "evaluation_id": rec.evaluation_id,
                    "heuristic_type": rec.heuristic_type,
                    "priority": rec.priority,
                    "action_title": rec.action_title,
                    "technical_description": rec.technical_description,
                    "simplified_description": rec.simplified_description,
                    "estimated_impact": rec.estimated_impact,
                    "implementation_difficulty": rec.implementation_difficulty,
                    "created_at": rec.created_at,
                }
                for rec in existing_recommendations
            ],
            mode,
        )
        return {"recommendations": formatted, "total": len(formatted)}

    # Get heuristic findings
    findings = (
        db.query(HeuristicFinding)
        .filter(HeuristicFinding.evaluation_id == evaluation_id)
        .all()
    )

    if not findings:
        return {"recommendations": [], "total": 0}

    # Convert findings to dict format
    findings_data = [
        {
            "heuristic_type": f.heuristic_type.value,
            "severity_score": f.severity_score,
            "confidence_level": f.confidence_level,
        }
        for f in findings
    ]

    # Generate recommendations
    generator = RecommendationGenerator()
    recommendations_data = generator.generate_recommendations(findings_data, mode)

    # Save recommendations to database
    saved_recommendations = []
    for rec_data in recommendations_data:
        recommendation = Recommendation(
            evaluation_id=evaluation_id,
            heuristic_type=rec_data["heuristic_type"],
            priority=rec_data["priority"],
            action_title=rec_data["action_title"],
            technical_description=rec_data["technical_description"],
            simplified_description=rec_data["simplified_description"],
            estimated_impact=rec_data["estimated_impact"],
            implementation_difficulty=rec_data["implementation_difficulty"],
        )
        db.add(recommendation)
        saved_recommendations.append(recommendation)

    db.commit()

    # Refresh to get IDs and timestamps
    for rec in saved_recommendations:
        db.refresh(rec)

    # Format for response
    formatted = RecommendationGenerator.format_for_mode(
        [
            {
                "id": rec.id,
                "evaluation_id": rec.evaluation_id,
                "heuristic_type": rec.heuristic_type,
                "priority": rec.priority,
                "action_title": rec.action_title,
                "technical_description": rec.technical_description,
                "simplified_description": rec.simplified_description,
                "estimated_impact": rec.estimated_impact,
                "implementation_difficulty": rec.implementation_difficulty,
                "created_at": rec.created_at,
            }
            for rec in saved_recommendations
        ],
        mode,
    )

    return {"recommendations": formatted, "total": len(formatted)}


@router.get(
    "/{evaluation_id}/recommendations/{recommendation_id}",
    response_model=RecommendationResponse,
)
def get_recommendation_detail(
    evaluation_id: str, recommendation_id: str, db: Session = Depends(get_db)
):
    """Get detailed recommendation with examples and resources."""
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

    # Get specific recommendation
    recommendation = (
        db.query(Recommendation)
        .filter(
            Recommendation.id == recommendation_id,
            Recommendation.evaluation_id == evaluation_id,
        )
        .first()
    )

    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Recommendation with id {recommendation_id} not found",
                }
            },
        )

    return recommendation
