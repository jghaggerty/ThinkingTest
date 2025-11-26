"""Unit tests for business logic services."""
import pytest
from app.services.heuristic_detector import HeuristicDetector
from app.services.statistical_analyzer import StatisticalAnalyzer
from app.models.heuristic import Severity


@pytest.mark.unit
class TestHeuristicDetector:
    """Test suite for HeuristicDetector service."""

    def test_detector_initialization(self):
        """Test HeuristicDetector initialization."""
        detector = HeuristicDetector(iteration_count=50)
        assert detector.iteration_count == 50

    def test_detect_anchoring(self):
        """Test anchoring bias detection."""
        detector = HeuristicDetector(iteration_count=50)
        result, examples = detector.detect_anchoring()

        assert "detection_count" in result
        assert "severity_score" in result
        assert "severity" in result
        assert "pattern_description" in result
        assert isinstance(result["detection_count"], int)
        assert 0 <= result["severity_score"] <= 100
        assert isinstance(result["severity"], Severity)
        assert isinstance(examples, list)
        assert len(examples) <= 3

    def test_detect_loss_aversion(self):
        """Test loss aversion bias detection."""
        detector = HeuristicDetector(iteration_count=50)
        result, examples = detector.detect_loss_aversion()

        assert "detection_count" in result
        assert "severity_score" in result
        assert 0 <= result["severity_score"] <= 100
        assert isinstance(result["severity"], Severity)
        assert isinstance(examples, list)

    def test_detect_sunk_cost(self):
        """Test sunk cost fallacy detection."""
        detector = HeuristicDetector(iteration_count=50)
        result, examples = detector.detect_sunk_cost()

        assert "detection_count" in result
        assert "severity_score" in result
        assert isinstance(result["severity"], Severity)
        assert isinstance(examples, list)

    def test_detect_confirmation_bias(self):
        """Test confirmation bias detection."""
        detector = HeuristicDetector(iteration_count=50)
        result, examples = detector.detect_confirmation_bias()

        assert "detection_count" in result
        assert "severity_score" in result
        assert isinstance(result["severity"], Severity)

    def test_detect_availability_heuristic(self):
        """Test availability heuristic detection."""
        detector = HeuristicDetector(iteration_count=50)
        result, examples = detector.detect_availability_heuristic()

        assert "detection_count" in result
        assert "severity_score" in result
        assert isinstance(result["severity"], Severity)

    def test_calculate_severity_critical(self):
        """Test severity calculation for critical level."""
        detector = HeuristicDetector(iteration_count=50)
        severity = detector._calculate_severity(80, "anchoring")
        assert severity == Severity.CRITICAL

    def test_calculate_severity_high(self):
        """Test severity calculation for high level."""
        detector = HeuristicDetector(iteration_count=50)
        severity = detector._calculate_severity(60, "anchoring")
        assert severity == Severity.HIGH

    def test_calculate_severity_medium(self):
        """Test severity calculation for medium level."""
        detector = HeuristicDetector(iteration_count=50)
        severity = detector._calculate_severity(30, "anchoring")
        assert severity == Severity.MEDIUM

    def test_calculate_severity_low(self):
        """Test severity calculation for low level."""
        detector = HeuristicDetector(iteration_count=50)
        severity = detector._calculate_severity(10, "anchoring")
        assert severity == Severity.LOW

    def test_calculate_confidence_high_iterations(self):
        """Test confidence calculation with high iteration count."""
        detector = HeuristicDetector(iteration_count=100)
        confidence = detector.calculate_confidence(detection_count=90)
        assert 0 <= confidence <= 0.99
        assert confidence > 0.8  # High detection rate should yield high confidence

    def test_calculate_confidence_low_iterations(self):
        """Test confidence calculation with low iteration count."""
        detector = HeuristicDetector(iteration_count=10)
        confidence = detector.calculate_confidence(detection_count=5)
        assert 0 <= confidence <= 0.99

    def test_run_detection_single_heuristic(self):
        """Test running detection for a single heuristic type."""
        detector = HeuristicDetector(iteration_count=50)
        findings = detector.run_detection(["anchoring"])

        assert len(findings) == 1
        assert findings[0]["heuristic_type"] == "anchoring"
        assert "severity_score" in findings[0]
        assert "confidence_level" in findings[0]
        assert "example_instances" in findings[0]

    def test_run_detection_multiple_heuristics(self):
        """Test running detection for multiple heuristic types."""
        detector = HeuristicDetector(iteration_count=50)
        heuristic_types = ["anchoring", "loss_aversion", "sunk_cost"]
        findings = detector.run_detection(heuristic_types)

        assert len(findings) == 3
        found_types = [f["heuristic_type"] for f in findings]
        assert set(found_types) == set(heuristic_types)

    def test_run_detection_all_heuristics(self):
        """Test running detection for all available heuristic types."""
        detector = HeuristicDetector(iteration_count=50)
        all_types = [
            "anchoring",
            "loss_aversion",
            "sunk_cost",
            "confirmation_bias",
            "availability_heuristic"
        ]
        findings = detector.run_detection(all_types)

        assert len(findings) == 5

    def test_run_detection_invalid_heuristic(self):
        """Test running detection with invalid heuristic type is ignored."""
        detector = HeuristicDetector(iteration_count=50)
        findings = detector.run_detection(["invalid_heuristic"])
        assert len(findings) == 0


@pytest.mark.unit
class TestStatisticalAnalyzer:
    """Test suite for StatisticalAnalyzer service."""

    def test_calculate_baseline_no_history(self):
        """Test baseline calculation with no historical data."""
        analyzer = StatisticalAnalyzer()
        baseline = analyzer.calculate_baseline([])

        assert baseline["mean"] == 30.0
        assert baseline["std_dev"] == 15.0
        assert baseline["sample_size"] == 0
        assert "green_zone_max" in baseline
        assert "yellow_zone_max" in baseline

    def test_calculate_baseline_with_history(self):
        """Test baseline calculation with historical scores."""
        analyzer = StatisticalAnalyzer()
        scores = [20.0, 25.0, 30.0, 35.0, 40.0]
        baseline = analyzer.calculate_baseline(scores)

        assert baseline["sample_size"] == 5
        assert baseline["mean"] == 30.0
        assert baseline["std_dev"] > 0
        assert baseline["green_zone_max"] > baseline["mean"]
        assert baseline["yellow_zone_max"] > baseline["green_zone_max"]

    def test_determine_zone_status_green(self):
        """Test zone status determination for green zone."""
        analyzer = StatisticalAnalyzer()
        zone = analyzer.determine_zone_status(20.0, green_max=30.0, yellow_max=50.0)
        assert zone == "green"

    def test_determine_zone_status_yellow(self):
        """Test zone status determination for yellow zone."""
        analyzer = StatisticalAnalyzer()
        zone = analyzer.determine_zone_status(40.0, green_max=30.0, yellow_max=50.0)
        assert zone == "yellow"

    def test_determine_zone_status_red(self):
        """Test zone status determination for red zone."""
        analyzer = StatisticalAnalyzer()
        zone = analyzer.determine_zone_status(60.0, green_max=30.0, yellow_max=50.0)
        assert zone == "red"

    def test_determine_zone_status_boundary_green(self):
        """Test zone status at green zone boundary."""
        analyzer = StatisticalAnalyzer()
        zone = analyzer.determine_zone_status(30.0, green_max=30.0, yellow_max=50.0)
        assert zone == "green"

    def test_determine_zone_status_boundary_yellow(self):
        """Test zone status at yellow zone boundary."""
        analyzer = StatisticalAnalyzer()
        zone = analyzer.determine_zone_status(50.0, green_max=30.0, yellow_max=50.0)
        assert zone == "yellow"

    def test_calculate_overall_score_empty(self):
        """Test overall score calculation with no scores."""
        analyzer = StatisticalAnalyzer()
        score = analyzer.calculate_overall_score([])
        assert score == 0.0

    def test_calculate_overall_score_single(self):
        """Test overall score calculation with single score."""
        analyzer = StatisticalAnalyzer()
        score = analyzer.calculate_overall_score([50.0])
        assert score == 50.0

    def test_calculate_overall_score_multiple(self):
        """Test overall score calculation with multiple scores."""
        analyzer = StatisticalAnalyzer()
        scores = [30.0, 50.0, 70.0]
        overall = analyzer.calculate_overall_score(scores)

        # Should weight higher scores more heavily
        assert 0 <= overall <= 100
        assert overall > 30.0  # Should be weighted toward higher values

    def test_calculate_overall_score_weighting(self):
        """Test that higher scores are weighted more heavily."""
        analyzer = StatisticalAnalyzer()
        scores1 = [90.0, 10.0, 10.0]
        scores2 = [10.0, 10.0, 90.0]

        overall1 = analyzer.calculate_overall_score(scores1)
        overall2 = analyzer.calculate_overall_score(scores2)

        # Both should produce same result due to weighting
        assert overall1 == overall2

    def test_detect_drift_insufficient_data(self):
        """Test drift detection with insufficient historical data."""
        analyzer = StatisticalAnalyzer()
        result = analyzer.detect_drift(50.0, [30.0, 35.0])

        assert result["has_drift"] is False
        assert "Insufficient" in result["message"]

    def test_detect_drift_no_drift(self):
        """Test drift detection when no significant drift exists."""
        analyzer = StatisticalAnalyzer()
        historical = [30.0, 35.0, 40.0, 45.0, 50.0]
        result = analyzer.detect_drift(42.0, historical, threshold=2.0)

        assert result["has_drift"] is False
        assert "z_score" in result
        assert "deviation" in result

    def test_detect_drift_with_drift(self):
        """Test drift detection when significant drift exists."""
        analyzer = StatisticalAnalyzer()
        historical = [30.0, 31.0, 32.0, 33.0, 34.0]
        result = analyzer.detect_drift(100.0, historical, threshold=2.0)

        assert result["has_drift"] is True
        assert result["z_score"] > 2.0
        assert "deviation" in result

    def test_detect_drift_constant_baseline(self):
        """Test drift detection with constant baseline values."""
        analyzer = StatisticalAnalyzer()
        historical = [30.0, 30.0, 30.0, 30.0]
        result = analyzer.detect_drift(50.0, historical)

        assert result["has_drift"] is True
        assert "deviation" in result

    def test_calculate_trend_insufficient_data(self):
        """Test trend calculation with insufficient data."""
        analyzer = StatisticalAnalyzer()
        result = analyzer.calculate_trend([{"timestamp": "2024-01-01", "score": 30.0}])

        assert result["trend"] == "insufficient_data"
        assert result["direction"] is None

    def test_calculate_trend_increasing(self):
        """Test trend calculation for increasing trend."""
        analyzer = StatisticalAnalyzer()
        data = [
            {"timestamp": "2024-01-01", "score": 20.0},
            {"timestamp": "2024-01-02", "score": 30.0},
            {"timestamp": "2024-01-03", "score": 40.0},
            {"timestamp": "2024-01-04", "score": 50.0},
        ]
        result = analyzer.calculate_trend(data)

        assert result["trend"] == "increasing"
        assert result["slope"] > 0
        assert result["start_score"] == 20.0
        assert result["end_score"] == 50.0
        assert result["change"] == 30.0

    def test_calculate_trend_decreasing(self):
        """Test trend calculation for decreasing trend."""
        analyzer = StatisticalAnalyzer()
        data = [
            {"timestamp": "2024-01-01", "score": 50.0},
            {"timestamp": "2024-01-02", "score": 40.0},
            {"timestamp": "2024-01-03", "score": 30.0},
            {"timestamp": "2024-01-04", "score": 20.0},
        ]
        result = analyzer.calculate_trend(data)

        assert result["trend"] == "decreasing"
        assert result["slope"] < 0

    def test_calculate_trend_stable(self):
        """Test trend calculation for stable trend."""
        analyzer = StatisticalAnalyzer()
        data = [
            {"timestamp": "2024-01-01", "score": 30.0},
            {"timestamp": "2024-01-02", "score": 30.5},
            {"timestamp": "2024-01-03", "score": 29.5},
            {"timestamp": "2024-01-04", "score": 30.0},
        ]
        result = analyzer.calculate_trend(data)

        assert result["trend"] == "stable"
        assert abs(result["slope"]) < 0.5
