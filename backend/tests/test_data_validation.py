"""Data validation tests for schemas and models."""
import pytest
from pydantic import ValidationError
from app.schemas.evaluation import EvaluationCreate
from app.schemas.baseline import BaselineCreate
from app.models.evaluation import EvaluationStatus, ZoneStatus
from app.models.heuristic import HeuristicType, Severity


@pytest.mark.validation
class TestEvaluationSchemaValidation:
    """Test suite for evaluation schema validation."""

    def test_valid_evaluation_create(self):
        """Test creating evaluation with valid data."""
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": ["anchoring", "loss_aversion"],
            "iteration_count": 50
        }
        evaluation = EvaluationCreate(**data)
        assert evaluation.ai_system_name == "Test System"
        assert len(evaluation.heuristic_types) == 2
        assert evaluation.iteration_count == 50

    def test_evaluation_name_min_length(self):
        """Test evaluation name minimum length validation."""
        data = {
            "ai_system_name": "",  # Empty string
            "heuristic_types": ["anchoring"],
            "iteration_count": 50
        }
        with pytest.raises(ValidationError) as exc_info:
            EvaluationCreate(**data)
        assert "ai_system_name" in str(exc_info.value)

    def test_evaluation_name_max_length(self):
        """Test evaluation name maximum length validation."""
        data = {
            "ai_system_name": "x" * 201,  # Exceeds 200 char limit
            "heuristic_types": ["anchoring"],
            "iteration_count": 50
        }
        with pytest.raises(ValidationError) as exc_info:
            EvaluationCreate(**data)
        assert "ai_system_name" in str(exc_info.value)

    def test_evaluation_iteration_count_min(self):
        """Test iteration count minimum validation."""
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": ["anchoring"],
            "iteration_count": 5  # Below minimum of 10
        }
        with pytest.raises(ValidationError) as exc_info:
            EvaluationCreate(**data)
        assert "iteration_count" in str(exc_info.value)

    def test_evaluation_iteration_count_max(self):
        """Test iteration count maximum validation."""
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": ["anchoring"],
            "iteration_count": 150  # Above maximum of 100
        }
        with pytest.raises(ValidationError) as exc_info:
            EvaluationCreate(**data)
        assert "iteration_count" in str(exc_info.value)

    def test_evaluation_heuristic_types_empty(self):
        """Test heuristic types cannot be empty."""
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": [],
            "iteration_count": 50
        }
        with pytest.raises(ValidationError) as exc_info:
            EvaluationCreate(**data)
        assert "heuristic_types" in str(exc_info.value)

    def test_evaluation_heuristic_types_invalid(self):
        """Test invalid heuristic type is rejected."""
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": ["invalid_heuristic"],
            "iteration_count": 50
        }
        with pytest.raises(ValidationError) as exc_info:
            EvaluationCreate(**data)
        assert "Invalid heuristic type" in str(exc_info.value)

    def test_evaluation_heuristic_types_mixed_valid_invalid(self):
        """Test mixed valid and invalid heuristic types."""
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": ["anchoring", "invalid_type"],
            "iteration_count": 50
        }
        with pytest.raises(ValidationError) as exc_info:
            EvaluationCreate(**data)
        assert "Invalid heuristic type" in str(exc_info.value)

    def test_evaluation_all_valid_heuristic_types(self):
        """Test all valid heuristic types are accepted."""
        valid_types = [
            "anchoring",
            "loss_aversion",
            "sunk_cost",
            "confirmation_bias",
            "availability_heuristic"
        ]
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": valid_types,
            "iteration_count": 50
        }
        evaluation = EvaluationCreate(**data)
        assert set(evaluation.heuristic_types) == set(valid_types)

    def test_evaluation_missing_required_field(self):
        """Test validation fails when required field is missing."""
        data = {
            "heuristic_types": ["anchoring"],
            "iteration_count": 50
            # Missing ai_system_name
        }
        with pytest.raises(ValidationError) as exc_info:
            EvaluationCreate(**data)
        assert "ai_system_name" in str(exc_info.value)

    def test_evaluation_extra_fields_ignored(self):
        """Test that extra fields are ignored by default."""
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": ["anchoring"],
            "iteration_count": 50,
            "extra_field": "should be ignored"
        }
        # Should not raise error, extra fields ignored
        evaluation = EvaluationCreate(**data)
        assert not hasattr(evaluation, "extra_field")


@pytest.mark.validation
class TestBaselineSchemaValidation:
    """Test suite for baseline schema validation."""

    def test_valid_baseline_create(self):
        """Test creating baseline with valid data."""
        data = {
            "evaluation_id": "test-eval-123",
            "zone_thresholds": {
                "green_zone_max": 30.0,
                "yellow_zone_max": 50.0
            }
        }
        baseline = BaselineCreate(**data)
        assert baseline.evaluation_id == "test-eval-123"
        assert baseline.zone_thresholds.green_zone_max == 30.0
        assert baseline.zone_thresholds.yellow_zone_max == 50.0

    def test_baseline_without_thresholds(self):
        """Test creating baseline without zone thresholds."""
        data = {
            "evaluation_id": "test-eval-123"
        }
        baseline = BaselineCreate(**data)
        assert baseline.evaluation_id == "test-eval-123"
        assert baseline.zone_thresholds is None

    def test_baseline_missing_evaluation_id(self):
        """Test baseline creation fails without evaluation_id."""
        data = {
            "zone_thresholds": {
                "green_zone_max": 30.0,
                "yellow_zone_max": 50.0
            }
        }
        with pytest.raises(ValidationError) as exc_info:
            BaselineCreate(**data)
        assert "evaluation_id" in str(exc_info.value)

    def test_zone_thresholds_validation(self):
        """Test zone thresholds schema validation."""
        from app.schemas.baseline import ZoneThresholds

        thresholds = ZoneThresholds(
            green_zone_max=30.0,
            yellow_zone_max=50.0
        )
        assert thresholds.green_zone_max == 30.0
        assert thresholds.yellow_zone_max == 50.0

    def test_zone_thresholds_optional_fields(self):
        """Test that zone threshold fields are optional."""
        from app.schemas.baseline import ZoneThresholds

        thresholds = ZoneThresholds()
        assert thresholds.green_zone_max is None
        assert thresholds.yellow_zone_max is None


@pytest.mark.validation
class TestEnumValidation:
    """Test suite for enum model validation."""

    def test_evaluation_status_values(self):
        """Test all EvaluationStatus enum values."""
        assert EvaluationStatus.PENDING.value == "pending"
        assert EvaluationStatus.RUNNING.value == "running"
        assert EvaluationStatus.COMPLETED.value == "completed"
        assert EvaluationStatus.FAILED.value == "failed"

    def test_zone_status_values(self):
        """Test all ZoneStatus enum values."""
        assert ZoneStatus.GREEN.value == "green"
        assert ZoneStatus.YELLOW.value == "yellow"
        assert ZoneStatus.RED.value == "red"

    def test_heuristic_type_values(self):
        """Test all HeuristicType enum values."""
        assert HeuristicType.ANCHORING.value == "anchoring"
        assert HeuristicType.LOSS_AVERSION.value == "loss_aversion"
        assert HeuristicType.SUNK_COST.value == "sunk_cost"
        assert HeuristicType.CONFIRMATION_BIAS.value == "confirmation_bias"
        assert HeuristicType.AVAILABILITY_HEURISTIC.value == "availability_heuristic"

    def test_severity_values(self):
        """Test all Severity enum values."""
        assert Severity.LOW.value == "low"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.HIGH.value == "high"
        assert Severity.CRITICAL.value == "critical"

    def test_severity_ordering(self):
        """Test that Severity enum can be compared."""
        # Note: Enum comparison depends on implementation
        assert Severity.LOW != Severity.CRITICAL
        assert Severity.MEDIUM != Severity.HIGH


@pytest.mark.validation
class TestDataConstraints:
    """Test suite for data constraint validation."""

    def test_confidence_level_range(self):
        """Test confidence level is within valid range."""
        # Confidence should be between 0 and 1
        from app.services.heuristic_detector import HeuristicDetector

        detector = HeuristicDetector(iteration_count=50)
        confidence = detector.calculate_confidence(25)
        assert 0 <= confidence <= 0.99

    def test_severity_score_range(self):
        """Test severity score is within valid range (0-100)."""
        from app.services.heuristic_detector import HeuristicDetector

        detector = HeuristicDetector(iteration_count=50)
        result, _ = detector.detect_anchoring()
        assert 0 <= result["severity_score"] <= 100

    def test_overall_score_range(self):
        """Test overall score is within valid range."""
        from app.services.statistical_analyzer import StatisticalAnalyzer

        analyzer = StatisticalAnalyzer()
        score = analyzer.calculate_overall_score([30.0, 50.0, 70.0])
        assert 0 <= score <= 100

    def test_detection_count_non_negative(self):
        """Test detection count is non-negative."""
        from app.services.heuristic_detector import HeuristicDetector

        detector = HeuristicDetector(iteration_count=50)
        result, _ = detector.detect_anchoring()
        assert result["detection_count"] >= 0

    def test_detection_count_not_exceeds_iterations(self):
        """Test detection count doesn't exceed iteration count."""
        from app.services.heuristic_detector import HeuristicDetector

        iteration_count = 50
        detector = HeuristicDetector(iteration_count=iteration_count)
        result, _ = detector.detect_anchoring()
        assert result["detection_count"] <= iteration_count
