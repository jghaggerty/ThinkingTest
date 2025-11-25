from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class EvaluationStatus(str, enum.Enum):
    """Evaluation status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ZoneStatus(str, enum.Enum):
    """Zone status enum."""
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class Evaluation(Base):
    """Evaluation model for storing AI system evaluation runs."""

    __tablename__ = "evaluations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ai_system_name = Column(String, nullable=False)
    heuristic_types = Column(JSON, nullable=False)  # List of heuristic types
    iteration_count = Column(Integer, nullable=False)
    status = Column(Enum(EvaluationStatus), default=EvaluationStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    overall_score = Column(Float, nullable=True)
    zone_status = Column(Enum(ZoneStatus), nullable=True)

    # Relationships
    heuristic_findings = relationship("HeuristicFinding", back_populates="evaluation", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="evaluation", cascade="all, delete-orphan")
