"""Integration tests for evaluations API endpoints."""
import pytest
from app.models.evaluation import EvaluationStatus


@pytest.mark.integration
class TestEvaluationsAPI:
    """Test suite for /api/evaluations endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AI Bias & Heuristics Diagnostic Tool API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_create_evaluation_success(self, client, sample_evaluation_data):
        """Test successful evaluation creation."""
        response = client.post("/api/evaluations", json=sample_evaluation_data)
        assert response.status_code == 201
        data = response.json()
        assert data["ai_system_name"] == sample_evaluation_data["ai_system_name"]
        assert data["heuristic_types"] == sample_evaluation_data["heuristic_types"]
        assert data["iteration_count"] == sample_evaluation_data["iteration_count"]
        assert data["status"] == EvaluationStatus.PENDING.value
        assert "id" in data
        assert "created_at" in data

    def test_create_evaluation_invalid_iteration_count_too_low(self, client):
        """Test evaluation creation fails with iteration count below minimum."""
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": ["anchoring"],
            "iteration_count": 5  # Below minimum of 10
        }
        response = client.post("/api/evaluations", json=data)
        assert response.status_code == 400
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "VALIDATION_ERROR"

    def test_create_evaluation_invalid_iteration_count_too_high(self, client):
        """Test evaluation creation fails with iteration count above maximum."""
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": ["anchoring"],
            "iteration_count": 150  # Above maximum of 100
        }
        response = client.post("/api/evaluations", json=data)
        assert response.status_code == 400
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "VALIDATION_ERROR"

    def test_create_evaluation_invalid_heuristic_type(self, client):
        """Test evaluation creation fails with invalid heuristic type."""
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": ["invalid_heuristic"],
            "iteration_count": 50
        }
        response = client.post("/api/evaluations", json=data)
        assert response.status_code == 422  # Pydantic validation error

    def test_create_evaluation_empty_heuristic_list(self, client):
        """Test evaluation creation fails with empty heuristic types list."""
        data = {
            "ai_system_name": "Test System",
            "heuristic_types": [],
            "iteration_count": 50
        }
        response = client.post("/api/evaluations", json=data)
        assert response.status_code == 422

    def test_create_evaluation_missing_required_field(self, client):
        """Test evaluation creation fails when required field is missing."""
        data = {
            "heuristic_types": ["anchoring"],
            "iteration_count": 50
            # Missing ai_system_name
        }
        response = client.post("/api/evaluations", json=data)
        assert response.status_code == 422

    def test_get_evaluation_success(self, client, sample_evaluation):
        """Test retrieving an existing evaluation."""
        response = client.get(f"/api/evaluations/{sample_evaluation.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_evaluation.id
        assert data["ai_system_name"] == sample_evaluation.ai_system_name
        assert data["status"] == sample_evaluation.status.value

    def test_get_evaluation_not_found(self, client):
        """Test retrieving non-existent evaluation returns 404."""
        response = client.get("/api/evaluations/nonexistent-id")
        assert response.status_code == 404
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "NOT_FOUND"

    def test_list_evaluations_empty(self, client):
        """Test listing evaluations when none exist."""
        response = client.get("/api/evaluations")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["evaluations"] == []
        assert data["limit"] == 10
        assert data["offset"] == 0

    def test_list_evaluations_with_data(self, client, sample_evaluation):
        """Test listing evaluations with existing data."""
        response = client.get("/api/evaluations")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["evaluations"]) == 1
        assert data["evaluations"][0]["id"] == sample_evaluation.id

    def test_list_evaluations_pagination(self, client, db_session):
        """Test evaluation listing with pagination parameters."""
        from app.models import Evaluation

        # Create multiple evaluations
        for i in range(15):
            eval = Evaluation(
                ai_system_name=f"System {i}",
                heuristic_types=["anchoring"],
                iteration_count=50,
                status=EvaluationStatus.PENDING
            )
            db_session.add(eval)
        db_session.commit()

        # Test limit
        response = client.get("/api/evaluations?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["evaluations"]) == 5
        assert data["total"] == 15

        # Test offset
        response = client.get("/api/evaluations?limit=5&offset=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["evaluations"]) == 5
        assert data["offset"] == 10

    def test_execute_evaluation_success(self, client, sample_evaluation):
        """Test successful evaluation execution."""
        response = client.post(f"/api/evaluations/{sample_evaluation.id}/execute")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == EvaluationStatus.COMPLETED.value
        assert data["overall_score"] is not None
        assert data["zone_status"] is not None
        assert data["completed_at"] is not None

    def test_execute_evaluation_not_found(self, client):
        """Test executing non-existent evaluation returns 404."""
        response = client.post("/api/evaluations/nonexistent-id/execute")
        assert response.status_code == 404
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "NOT_FOUND"

    def test_execute_evaluation_already_completed(self, client, completed_evaluation):
        """Test executing already completed evaluation returns error."""
        response = client.post(f"/api/evaluations/{completed_evaluation.id}/execute")
        assert response.status_code == 400
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "EVALUATION_FAILED"

    def test_delete_evaluation_success(self, client, sample_evaluation):
        """Test successful evaluation deletion."""
        eval_id = sample_evaluation.id
        response = client.delete(f"/api/evaluations/{eval_id}")
        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(f"/api/evaluations/{eval_id}")
        assert get_response.status_code == 404

    def test_delete_evaluation_not_found(self, client):
        """Test deleting non-existent evaluation returns 404."""
        response = client.delete("/api/evaluations/nonexistent-id")
        assert response.status_code == 404
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "NOT_FOUND"

    def test_evaluation_workflow_end_to_end(self, client, sample_evaluation_data):
        """Test complete evaluation workflow from creation to deletion."""
        # Create evaluation
        create_response = client.post("/api/evaluations", json=sample_evaluation_data)
        assert create_response.status_code == 201
        eval_id = create_response.json()["id"]

        # Execute evaluation
        execute_response = client.post(f"/api/evaluations/{eval_id}/execute")
        assert execute_response.status_code == 200
        assert execute_response.json()["status"] == EvaluationStatus.COMPLETED.value

        # Get evaluation
        get_response = client.get(f"/api/evaluations/{eval_id}")
        assert get_response.status_code == 200

        # Delete evaluation
        delete_response = client.delete(f"/api/evaluations/{eval_id}")
        assert delete_response.status_code == 204
