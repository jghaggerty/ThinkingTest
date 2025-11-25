from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class HeuristicType(str, enum.Enum):
    """Heuristic type enum."""
    ANCHORING = "anchoring"
    LOSS_AVERSION = "loss_aversion"
    SUNK_COST = "sunk_cost"
    CONFIRMATION_BIAS = "confirmation_bias"
    AVAILABILITY_HEURISTIC = "availability_heuristic"


class Severity(str, enum.Enum):
    """Severity level enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class HeuristicFinding(Base):
    """Heuristic finding model for storing detected bias patterns."""

    __tablename__ = "heuristic_findings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id = Column(String, ForeignKey("evaluations.id"), nullable=False)
    heuristic_type = Column(Enum(HeuristicType), nullable=False)
    severity = Column(Enum(Severity), nullable=False)
    severity_score = Column(Float, nullable=False)  # 0-100
    confidence_level = Column(Float, nullable=False)  # 0-1
    detection_count = Column(Integer, nullable=False)
    example_instances = Column(JSON, nullable=False)  # List of example texts
    pattern_description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="heuristic_findings")
