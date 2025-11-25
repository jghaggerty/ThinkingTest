from sqlalchemy import Column, String, Float, DateTime, JSON
from datetime import datetime
import uuid

from app.database import Base


class Baseline(Base):
    """Baseline model for storing statistical baseline configurations."""

    __tablename__ = "baselines"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    green_zone_max = Column(Float, nullable=False)
    yellow_zone_max = Column(Float, nullable=False)
    statistical_params = Column(JSON, nullable=False)  # Dict with mean, std_dev, sample_size
    created_at = Column(DateTime, default=datetime.utcnow)
