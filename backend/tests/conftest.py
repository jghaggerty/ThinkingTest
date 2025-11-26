"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Evaluation, HeuristicFinding, Recommendation, Baseline


@pytest.fixture(scope="function")
def db_session():
    """Create a clean database session for each test."""
    # Use in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_evaluation_data():
    """Sample evaluation data for testing."""
    return {
        "ai_system_name": "Test AI System",
        "heuristic_types": ["anchoring", "loss_aversion"],
        "iteration_count": 50
    }


@pytest.fixture
def sample_evaluation(db_session, sample_evaluation_data):
    """Create a sample evaluation in the database."""
    from app.models.evaluation import EvaluationStatus

    evaluation = Evaluation(
        ai_system_name=sample_evaluation_data["ai_system_name"],
        heuristic_types=sample_evaluation_data["heuristic_types"],
        iteration_count=sample_evaluation_data["iteration_count"],
        status=EvaluationStatus.PENDING,
    )
    db_session.add(evaluation)
    db_session.commit()
    db_session.refresh(evaluation)

    return evaluation


@pytest.fixture
def completed_evaluation(db_session, sample_evaluation):
    """Create a completed evaluation with findings."""
    from app.models.evaluation import EvaluationStatus
    from app.models.heuristic import Severity
    from datetime import datetime

    # Update evaluation status
    sample_evaluation.status = EvaluationStatus.COMPLETED
    sample_evaluation.overall_score = 45.5
    sample_evaluation.zone_status = "yellow"
    sample_evaluation.completed_at = datetime.utcnow()

    # Add findings
    finding1 = HeuristicFinding(
        evaluation_id=sample_evaluation.id,
        heuristic_type="anchoring",
        severity=Severity.HIGH,
        severity_score=55.2,
        confidence_level=0.85,
        detection_count=40,
        example_instances=["Example 1", "Example 2"],
        pattern_description="High anchoring bias detected"
    )
    finding2 = HeuristicFinding(
        evaluation_id=sample_evaluation.id,
        heuristic_type="loss_aversion",
        severity=Severity.MEDIUM,
        severity_score=35.8,
        confidence_level=0.72,
        detection_count=30,
        example_instances=["Example 3"],
        pattern_description="Moderate loss aversion detected"
    )

    db_session.add(finding1)
    db_session.add(finding2)
    db_session.commit()

    db_session.refresh(sample_evaluation)
    return sample_evaluation
