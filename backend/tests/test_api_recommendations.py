"""Integration tests for recommendations API endpoints."""
import pytest


@pytest.mark.integration
class TestRecommendationsAPI:
    """Test suite for /api/evaluations/{id}/recommendations endpoints."""

    def test_get_recommendations_evaluation_not_found(self, client):
        """Test getting recommendations for non-existent evaluation."""
        response = client.get("/api/evaluations/nonexistent-id/recommendations")
        assert response.status_code == 404
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "NOT_FOUND"

    def test_get_recommendations_no_findings(self, client, sample_evaluation):
        """Test getting recommendations when evaluation has no findings."""
        response = client.get(f"/api/evaluations/{sample_evaluation.id}/recommendations")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["recommendations"] == []

    def test_get_recommendations_technical_mode(self, client, completed_evaluation):
        """Test getting recommendations in technical mode."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation.id}/recommendations?mode=technical"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert len(data["recommendations"]) > 0

        # Verify structure of recommendations
        rec = data["recommendations"][0]
        assert "id" in rec
        assert "heuristic_type" in rec
        assert "priority" in rec
        assert "action_title" in rec
        assert "technical_description" in rec
        assert "estimated_impact" in rec
        assert "implementation_difficulty" in rec

    def test_get_recommendations_simplified_mode(self, client, completed_evaluation):
        """Test getting recommendations in simplified mode."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation.id}/recommendations?mode=simplified"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert len(data["recommendations"]) > 0

        rec = data["recommendations"][0]
        assert "simplified_description" in rec

    def test_get_recommendations_both_mode(self, client, completed_evaluation):
        """Test getting recommendations in both mode."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation.id}/recommendations?mode=both"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert len(data["recommendations"]) > 0

        rec = data["recommendations"][0]
        assert "technical_description" in rec
        assert "simplified_description" in rec

    def test_get_recommendations_invalid_mode(self, client, completed_evaluation):
        """Test getting recommendations with invalid mode parameter."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation.id}/recommendations?mode=invalid"
        )
        assert response.status_code == 422  # Validation error

    def test_get_recommendations_caching(self, client, completed_evaluation):
        """Test that recommendations are cached after first generation."""
        # First request generates recommendations
        response1 = client.get(
            f"/api/evaluations/{completed_evaluation.id}/recommendations"
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request should return cached recommendations
        response2 = client.get(
            f"/api/evaluations/{completed_evaluation.id}/recommendations"
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # Verify same recommendations returned
        assert data1["total"] == data2["total"]
        assert len(data1["recommendations"]) == len(data2["recommendations"])

    def test_get_recommendation_detail_success(self, client, completed_evaluation):
        """Test getting detailed recommendation."""
        # First get recommendations
        list_response = client.get(
            f"/api/evaluations/{completed_evaluation.id}/recommendations"
        )
        rec_id = list_response.json()["recommendations"][0]["id"]

        # Get detail
        response = client.get(
            f"/api/evaluations/{completed_evaluation.id}/recommendations/{rec_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == rec_id
        assert "heuristic_type" in data
        assert "priority" in data

    def test_get_recommendation_detail_evaluation_not_found(self, client):
        """Test getting recommendation detail for non-existent evaluation."""
        response = client.get(
            "/api/evaluations/nonexistent-id/recommendations/rec-id"
        )
        assert response.status_code == 404
        error = response.json()
        assert error["error"]["code"] == "NOT_FOUND"

    def test_get_recommendation_detail_not_found(self, client, completed_evaluation):
        """Test getting non-existent recommendation detail."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation.id}/recommendations/nonexistent-rec-id"
        )
        assert response.status_code == 404
        error = response.json()
        assert error["error"]["code"] == "NOT_FOUND"

    def test_recommendations_priority_ordering(self, client, completed_evaluation):
        """Test that recommendations are ordered by priority."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation.id}/recommendations"
        )
        assert response.status_code == 200
        data = response.json()

        if len(data["recommendations"]) > 1:
            # Verify priorities are in descending order (high to low)
            priorities = [rec["priority"] for rec in data["recommendations"]]
            priority_values = {"high": 3, "medium": 2, "low": 1}
            priority_nums = [priority_values.get(p, 0) for p in priorities]
            assert priority_nums == sorted(priority_nums, reverse=True)
