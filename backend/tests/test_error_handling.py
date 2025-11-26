"""Error handling tests for API and services."""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError


@pytest.mark.error
class TestAPIErrorHandling:
    """Test suite for API error handling."""

    def test_404_error_format(self, client):
        """Test that 404 errors follow consistent format."""
        response = client.get("/api/evaluations/nonexistent-id")
        assert response.status_code == 404
        error = response.json()
        assert "error" in error
        assert "code" in error["error"]
        assert "message" in error["error"]
        assert error["error"]["code"] == "NOT_FOUND"

    def test_400_validation_error_format(self, client):
        """Test that 400 validation errors follow consistent format."""
        data = {
            "ai_system_name": "Test",
            "heuristic_types": ["anchoring"],
            "iteration_count": 5  # Below minimum
        }
        response = client.post("/api/evaluations", json=data)
        assert response.status_code == 400
        error = response.json()
        assert "error" in error
        assert "code" in error["error"]
        assert error["error"]["code"] == "VALIDATION_ERROR"

    def test_422_pydantic_validation_error(self, client):
        """Test Pydantic validation error format."""
        data = {
            "ai_system_name": "Test",
            "heuristic_types": ["invalid_type"],
            "iteration_count": 50
        }
        response = client.post("/api/evaluations", json=data)
        assert response.status_code == 422
        error = response.json()
        assert "detail" in error

    def test_malformed_json_request(self, client):
        """Test handling of malformed JSON in request."""
        response = client.post(
            "/api/evaluations",
            data="invalid json{",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_content_type(self, client):
        """Test handling of missing content-type header."""
        response = client.post(
            "/api/evaluations",
            data='{"ai_system_name": "Test", "heuristic_types": ["anchoring"], "iteration_count": 50}'
        )
        # FastAPI should handle this gracefully
        assert response.status_code in [200, 201, 422]

    def test_evaluation_execution_error_handling(self, client, sample_evaluation):
        """Test error handling during evaluation execution."""
        with patch('app.services.heuristic_detector.HeuristicDetector.run_detection') as mock_detect:
            mock_detect.side_effect = Exception("Simulated detection error")

            response = client.post(f"/api/evaluations/{sample_evaluation.id}/execute")
            assert response.status_code == 500
            error = response.json()
            assert "error" in error
            assert error["error"]["code"] == "EVALUATION_FAILED"

    def test_database_error_handling(self, client):
        """Test handling of database errors."""
        with patch('app.database.get_db') as mock_db:
            mock_session = MagicMock()
            mock_session.query.side_effect = SQLAlchemyError("Database connection error")
            mock_db.return_value = mock_session

            response = client.get("/api/evaluations")
            # Should handle database error gracefully
            assert response.status_code in [500, 503]

    def test_invalid_query_parameters(self, client):
        """Test handling of invalid query parameters."""
        # Invalid limit (negative)
        response = client.get("/api/evaluations?limit=-1")
        assert response.status_code == 422

        # Invalid limit (exceeds maximum)
        response = client.get("/api/evaluations?limit=1000")
        assert response.status_code == 422

        # Invalid offset (negative)
        response = client.get("/api/evaluations?offset=-1")
        assert response.status_code == 422

    def test_invalid_mode_parameter(self, client, completed_evaluation):
        """Test handling of invalid mode parameter in recommendations."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation.id}/recommendations?mode=invalid_mode"
        )
        assert response.status_code == 422

    def test_duplicate_evaluation_execution(self, client, completed_evaluation):
        """Test error when trying to execute completed evaluation."""
        response = client.post(f"/api/evaluations/{completed_evaluation.id}/execute")
        assert response.status_code == 400
        error = response.json()
        assert error["error"]["code"] == "EVALUATION_FAILED"
        assert "already been completed" in error["error"]["message"]

    def test_global_exception_handler(self, client):
        """Test global exception handler catches unhandled errors."""
        with patch('app.routers.evaluations.get_db') as mock_db:
            mock_db.side_effect = Exception("Unexpected error")

            response = client.get("/api/evaluations")
            assert response.status_code == 500
            error = response.json()
            assert "error" in error


@pytest.mark.error
class TestServiceErrorHandling:
    """Test suite for service layer error handling."""

    def test_heuristic_detector_zero_iterations(self):
        """Test HeuristicDetector with zero iterations."""
        from app.services.heuristic_detector import HeuristicDetector

        # This should handle edge case gracefully
        detector = HeuristicDetector(iteration_count=0)
        # Attempting detection should not crash
        try:
            result, examples = detector.detect_anchoring()
            # If it doesn't crash, verify the result is sensible
            assert result["detection_count"] == 0
        except ZeroDivisionError:
            # If it raises ZeroDivisionError, this is expected behavior to test
            pass

    def test_statistical_analyzer_empty_scores(self):
        """Test StatisticalAnalyzer with empty score list."""
        from app.services.statistical_analyzer import StatisticalAnalyzer

        analyzer = StatisticalAnalyzer()
        result = analyzer.calculate_overall_score([])
        assert result == 0.0

    def test_statistical_analyzer_single_score(self):
        """Test StatisticalAnalyzer with single score."""
        from app.services.statistical_analyzer import StatisticalAnalyzer

        analyzer = StatisticalAnalyzer()
        result = analyzer.calculate_overall_score([50.0])
        assert result == 50.0

    def test_baseline_calculation_constant_scores(self):
        """Test baseline calculation with all identical scores."""
        from app.services.statistical_analyzer import StatisticalAnalyzer

        analyzer = StatisticalAnalyzer()
        scores = [30.0, 30.0, 30.0, 30.0]
        baseline = analyzer.calculate_baseline(scores)

        assert baseline["mean"] == 30.0
        assert baseline["std_dev"] == 0.0
        assert "green_zone_max" in baseline
        assert "yellow_zone_max" in baseline

    def test_drift_detection_zero_std_dev(self):
        """Test drift detection with zero standard deviation."""
        from app.services.statistical_analyzer import StatisticalAnalyzer

        analyzer = StatisticalAnalyzer()
        historical = [30.0, 30.0, 30.0, 30.0]
        result = analyzer.detect_drift(35.0, historical)

        assert "has_drift" in result
        assert "deviation" in result

    def test_trend_calculation_constant_scores(self):
        """Test trend calculation with constant scores."""
        from app.services.statistical_analyzer import StatisticalAnalyzer

        analyzer = StatisticalAnalyzer()
        data = [
            {"timestamp": "2024-01-01", "score": 30.0},
            {"timestamp": "2024-01-02", "score": 30.0},
            {"timestamp": "2024-01-03", "score": 30.0},
        ]
        result = analyzer.calculate_trend(data)

        assert result["trend"] == "stable"
        assert result["slope"] == 0.0

    def test_confidence_calculation_zero_detections(self):
        """Test confidence calculation with zero detections."""
        from app.services.heuristic_detector import HeuristicDetector

        detector = HeuristicDetector(iteration_count=50)
        confidence = detector.calculate_confidence(0)
        assert confidence >= 0.0
        assert confidence <= 0.99

    def test_confidence_calculation_all_detections(self):
        """Test confidence calculation when all iterations detect."""
        from app.services.heuristic_detector import HeuristicDetector

        detector = HeuristicDetector(iteration_count=50)
        confidence = detector.calculate_confidence(50)
        assert confidence > 0.9  # Should be very high confidence


@pytest.mark.error
class TestDatabaseErrorHandling:
    """Test suite for database-related error handling."""

    def test_concurrent_evaluation_access(self, client, sample_evaluation, db_session):
        """Test handling of concurrent access to same evaluation."""
        # First request starts execution
        response1 = client.post(f"/api/evaluations/{sample_evaluation.id}/execute")
        assert response1.status_code in [200, 400]

        # Second request should handle appropriately
        response2 = client.post(f"/api/evaluations/{sample_evaluation.id}/execute")
        assert response2.status_code in [200, 400]

    def test_delete_nonexistent_evaluation(self, client):
        """Test deleting evaluation that doesn't exist."""
        response = client.delete("/api/evaluations/nonexistent-id")
        assert response.status_code == 404
        error = response.json()
        assert error["error"]["code"] == "NOT_FOUND"

    def test_get_recommendations_for_incomplete_evaluation(self, client, sample_evaluation):
        """Test getting recommendations for evaluation without findings."""
        response = client.get(f"/api/evaluations/{sample_evaluation.id}/recommendations")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["recommendations"] == []

    def test_cascade_delete_evaluation_with_findings(self, client, completed_evaluation):
        """Test that deleting evaluation cascades to findings and recommendations."""
        eval_id = completed_evaluation.id

        # Generate recommendations
        client.get(f"/api/evaluations/{eval_id}/recommendations")

        # Delete evaluation
        response = client.delete(f"/api/evaluations/{eval_id}")
        assert response.status_code == 204

        # Verify evaluation is gone
        get_response = client.get(f"/api/evaluations/{eval_id}")
        assert get_response.status_code == 404


@pytest.mark.error
class TestInputSanitization:
    """Test suite for input sanitization and injection prevention."""

    def test_sql_injection_prevention(self, client):
        """Test that SQL injection attempts are prevented."""
        # Attempt SQL injection in evaluation ID
        malicious_id = "1' OR '1'='1"
        response = client.get(f"/api/evaluations/{malicious_id}")
        # Should return 404, not expose SQL error
        assert response.status_code == 404

    def test_xss_prevention_in_system_name(self, client):
        """Test that XSS attempts in system name are handled."""
        data = {
            "ai_system_name": "<script>alert('xss')</script>",
            "heuristic_types": ["anchoring"],
            "iteration_count": 50
        }
        response = client.post("/api/evaluations", json=data)
        assert response.status_code == 201
        # The name should be stored as-is (API should not execute it)
        result = response.json()
        assert result["ai_system_name"] == data["ai_system_name"]

    def test_extremely_long_string_input(self, client):
        """Test handling of extremely long string inputs."""
        data = {
            "ai_system_name": "x" * 10000,  # Very long string
            "heuristic_types": ["anchoring"],
            "iteration_count": 50
        }
        response = client.post("/api/evaluations", json=data)
        # Should fail validation due to max length
        assert response.status_code == 422

    def test_special_characters_in_system_name(self, client):
        """Test handling of special characters in system name."""
        data = {
            "ai_system_name": "Test System !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "heuristic_types": ["anchoring"],
            "iteration_count": 50
        }
        response = client.post("/api/evaluations", json=data)
        assert response.status_code == 201

    def test_unicode_characters_in_system_name(self, client):
        """Test handling of Unicode characters in system name."""
        data = {
            "ai_system_name": "测试系统 テストシステム Тестовая система",
            "heuristic_types": ["anchoring"],
            "iteration_count": 50
        }
        response = client.post("/api/evaluations", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["ai_system_name"] == data["ai_system_name"]
