from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class Impact(str, enum.Enum):
    """Impact level enum."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Difficulty(str, enum.Enum):
    """Implementation difficulty enum."""
    EASY = "easy"
    MODERATE = "moderate"
    COMPLEX = "complex"


class Recommendation(Base):
    """Recommendation model for storing mitigation strategies."""

    __tablename__ = "recommendations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id = Column(String, ForeignKey("evaluations.id"), nullable=False)
    heuristic_type = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)  # 1-10
    action_title = Column(String, nullable=False)
    technical_description = Column(String, nullable=False)
    simplified_description = Column(String, nullable=False)
    estimated_impact = Column(Enum(Impact), nullable=False)
    implementation_difficulty = Column(Enum(Difficulty), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="recommendations")
