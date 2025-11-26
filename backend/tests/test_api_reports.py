"""Tests for the evaluation reports API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.main import app
from app.models.evaluation import Evaluation, EvaluationStatus, ZoneStatus
from app.models.heuristic import HeuristicFinding, HeuristicType, Severity


@pytest.fixture
def completed_evaluation_with_findings(db_session: Session):
    """Create a completed evaluation with multiple findings for testing."""
    evaluation = Evaluation(
        ai_system_name="Test AI System",
        heuristic_types=["anchoring", "loss_aversion", "confirmation_bias"],
        iteration_count=50,
        status=EvaluationStatus.COMPLETED,
        overall_score=45.5,
        zone_status=ZoneStatus.YELLOW,
        completed_at=datetime.utcnow()
    )
    db_session.add(evaluation)
    db_session.commit()
    db_session.refresh(evaluation)

    # Add some findings
    findings = [
        HeuristicFinding(
            evaluation_id=evaluation.id,
            heuristic_type=HeuristicType.ANCHORING,
            severity=Severity.HIGH,
            severity_score=75.0,
            confidence_level=0.85,
            detection_count=15,
            example_instances=["example1", "example2"],
            pattern_description="Strong anchoring bias detected in pricing decisions"
        ),
        HeuristicFinding(
            evaluation_id=evaluation.id,
            heuristic_type=HeuristicType.LOSS_AVERSION,
            severity=Severity.MEDIUM,
            severity_score=55.0,
            confidence_level=0.72,
            detection_count=8,
            example_instances=["example3", "example4"],
            pattern_description="Moderate loss aversion patterns in risk assessment"
        ),
        HeuristicFinding(
            evaluation_id=evaluation.id,
            heuristic_type=HeuristicType.CONFIRMATION_BIAS,
            severity=Severity.CRITICAL,
            severity_score=92.0,
            confidence_level=0.95,
            detection_count=25,
            example_instances=["example5", "example6"],
            pattern_description="Critical confirmation bias in data selection"
        )
    ]

    for finding in findings:
        db_session.add(finding)

    db_session.commit()

    return evaluation


@pytest.fixture
def pending_evaluation(db_session: Session):
    """Create a pending evaluation for testing error cases."""
    evaluation = Evaluation(
        ai_system_name="Pending AI System",
        heuristic_types=["anchoring"],
        iteration_count=30,
        status=EvaluationStatus.PENDING
    )
    db_session.add(evaluation)
    db_session.commit()
    db_session.refresh(evaluation)
    return evaluation


class TestReportsEndpoint:
    """Test suite for the /api/evaluations/{id}/reports endpoint."""

    def test_generate_json_report(self, client: TestClient, completed_evaluation_with_findings: Evaluation):
        """Test JSON report generation."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation_with_findings.id}/reports?format=json"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify report structure
        assert "report_metadata" in data
        assert "evaluation" in data
        assert "findings" in data
        assert "summary" in data

        # Verify metadata
        assert data["report_metadata"]["report_type"] == "full_export"
        assert data["report_metadata"]["format_version"] == "1.0.0"

        # Verify evaluation data
        assert data["evaluation"]["id"] == completed_evaluation_with_findings.id
        assert data["evaluation"]["ai_system_name"] == "Test AI System"
        assert data["evaluation"]["overall_score"] == 45.5
        assert data["evaluation"]["zone_status"] == "yellow"
        assert data["evaluation"]["status"] == "completed"

        # Verify findings
        assert len(data["findings"]) == 3
        assert all("heuristic_type" in f for f in data["findings"])
        assert all("severity" in f for f in data["findings"])
        assert all("severity_score" in f for f in data["findings"])

        # Verify summary
        assert "severity_breakdown" in data["summary"]
        assert "critical_findings_count" in data["summary"]
        assert data["summary"]["critical_findings_count"] == 1

    def test_generate_executive_summary(self, client: TestClient, completed_evaluation_with_findings: Evaluation):
        """Test executive summary generation."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation_with_findings.id}/reports?format=summary"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify summary structure
        assert "report_metadata" in data
        assert "evaluation_overview" in data
        assert "key_findings" in data
        assert "top_concerns" in data
        assert "risk_assessment" in data
        assert "recommendations" in data

        # Verify metadata
        assert data["report_metadata"]["report_type"] == "executive_summary"

        # Verify evaluation overview
        overview = data["evaluation_overview"]
        assert overview["ai_system_name"] == "Test AI System"
        assert overview["overall_score"] == 45.5
        assert overview["zone_status"] == "yellow"

        # Verify key findings
        key_findings = data["key_findings"]
        assert key_findings["total_heuristics_detected"] == 3
        assert key_findings["critical_issues"] == 1
        assert key_findings["high_priority_issues"] == 1

        # Verify top concerns (should be sorted by severity score)
        assert len(data["top_concerns"]) <= 3
        assert data["top_concerns"][0]["severity"] == "critical"
        assert data["top_concerns"][0]["severity_score"] == 92.0

        # Verify risk assessment
        risk = data["risk_assessment"]
        assert "risk_level" in risk
        assert "assessment" in risk
        assert "key_concerns" in risk

        # Verify recommendations
        assert len(data["recommendations"]) > 0
        assert all("priority" in r for r in data["recommendations"])
        assert all("recommendation" in r for r in data["recommendations"])

    def test_generate_pdf_report(self, client: TestClient, completed_evaluation_with_findings: Evaluation):
        """Test PDF report generation."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation_with_findings.id}/reports?format=pdf"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert f"evaluation_{completed_evaluation_with_findings.id}_report.pdf" in response.headers["content-disposition"]

        # Verify PDF content is not empty
        assert len(response.content) > 0

        # Verify it's actually a PDF (starts with PDF magic number)
        assert response.content[:4] == b'%PDF'

    def test_report_default_format_is_json(self, client: TestClient, completed_evaluation_with_findings: Evaluation):
        """Test that default report format is JSON."""
        response = client.get(f"/api/evaluations/{completed_evaluation_with_findings.id}/reports")

        assert response.status_code == 200
        data = response.json()
        assert "report_metadata" in data
        assert data["report_metadata"]["report_type"] == "full_export"

    def test_report_invalid_format(self, client: TestClient, completed_evaluation_with_findings: Evaluation):
        """Test report generation with invalid format."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation_with_findings.id}/reports?format=invalid"
        )

        assert response.status_code == 422  # Validation error

    def test_report_evaluation_not_found(self, client: TestClient):
        """Test report generation for non-existent evaluation."""
        response = client.get("/api/evaluations/nonexistent-id/reports?format=json")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"]["code"] == "NOT_FOUND"

    def test_report_evaluation_not_completed(self, client: TestClient, pending_evaluation: Evaluation):
        """Test report generation for incomplete evaluation."""
        response = client.get(
            f"/api/evaluations/{pending_evaluation.id}/reports?format=json"
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"]["code"] == "EVALUATION_NOT_COMPLETED"
        assert data["detail"]["error"]["details"]["current_status"] == "pending"

    def test_json_report_with_no_findings(self, db_session: Session, client: TestClient):
        """Test JSON report generation when there are no findings."""
        evaluation = Evaluation(
            ai_system_name="No Findings System",
            heuristic_types=["anchoring"],
            iteration_count=10,
            status=EvaluationStatus.COMPLETED,
            overall_score=10.0,
            zone_status=ZoneStatus.GREEN
        )
        db_session.add(evaluation)
        db_session.commit()
        db_session.refresh(evaluation)

        response = client.get(f"/api/evaluations/{evaluation.id}/reports?format=json")

        assert response.status_code == 200
        data = response.json()
        assert len(data["findings"]) == 0
        assert data["summary"]["critical_findings_count"] == 0

    def test_summary_report_with_no_findings(self, db_session: Session, client: TestClient):
        """Test executive summary when there are no findings."""
        evaluation = Evaluation(
            ai_system_name="No Findings System",
            heuristic_types=["anchoring"],
            iteration_count=10,
            status=EvaluationStatus.COMPLETED,
            overall_score=10.0,
            zone_status=ZoneStatus.GREEN
        )
        db_session.add(evaluation)
        db_session.commit()
        db_session.refresh(evaluation)

        response = client.get(f"/api/evaluations/{evaluation.id}/reports?format=summary")

        assert response.status_code == 200
        data = response.json()
        assert data["key_findings"]["total_heuristics_detected"] == 0
        assert len(data["top_concerns"]) == 0

    def test_pdf_report_with_no_findings(self, db_session: Session, client: TestClient):
        """Test PDF report generation when there are no findings."""
        evaluation = Evaluation(
            ai_system_name="No Findings System",
            heuristic_types=["anchoring"],
            iteration_count=10,
            status=EvaluationStatus.COMPLETED,
            overall_score=10.0,
            zone_status=ZoneStatus.GREEN
        )
        db_session.add(evaluation)
        db_session.commit()
        db_session.refresh(evaluation)

        response = client.get(f"/api/evaluations/{evaluation.id}/reports?format=pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0

    def test_report_severity_breakdown_accuracy(self, client: TestClient, completed_evaluation_with_findings: Evaluation):
        """Test that severity breakdown is accurate in reports."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation_with_findings.id}/reports?format=json"
        )

        assert response.status_code == 200
        data = response.json()

        severity_breakdown = data["summary"]["severity_breakdown"]
        assert severity_breakdown["critical"] == 1
        assert severity_breakdown["high"] == 1
        assert severity_breakdown["medium"] == 1

    def test_report_risk_assessment_levels(self, db_session: Session, client: TestClient):
        """Test risk assessment for different zone statuses."""
        # Test GREEN zone
        green_eval = Evaluation(
            ai_system_name="Green System",
            heuristic_types=["anchoring"],
            iteration_count=10,
            status=EvaluationStatus.COMPLETED,
            overall_score=15.0,
            zone_status=ZoneStatus.GREEN
        )
        db_session.add(green_eval)
        db_session.commit()
        db_session.refresh(green_eval)

        response = client.get(f"/api/evaluations/{green_eval.id}/reports?format=summary")
        assert response.status_code == 200
        data = response.json()
        assert data["risk_assessment"]["risk_level"] == "LOW"

        # Test RED zone
        red_eval = Evaluation(
            ai_system_name="Red System",
            heuristic_types=["anchoring"],
            iteration_count=10,
            status=EvaluationStatus.COMPLETED,
            overall_score=85.0,
            zone_status=ZoneStatus.RED
        )
        db_session.add(red_eval)
        db_session.commit()
        db_session.refresh(red_eval)

        response = client.get(f"/api/evaluations/{red_eval.id}/reports?format=summary")
        assert response.status_code == 200
        data = response.json()
        assert data["risk_assessment"]["risk_level"] == "HIGH"

    def test_report_top_concerns_sorting(self, client: TestClient, completed_evaluation_with_findings: Evaluation):
        """Test that top concerns are sorted by severity score."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation_with_findings.id}/reports?format=summary"
        )

        assert response.status_code == 200
        data = response.json()

        top_concerns = data["top_concerns"]
        # Verify sorted in descending order by severity_score
        for i in range(len(top_concerns) - 1):
            assert top_concerns[i]["severity_score"] >= top_concerns[i + 1]["severity_score"]

    def test_report_recommendations_for_critical_findings(self, client: TestClient, completed_evaluation_with_findings: Evaluation):
        """Test that recommendations include urgent actions for critical findings."""
        response = client.get(
            f"/api/evaluations/{completed_evaluation_with_findings.id}/reports?format=summary"
        )

        assert response.status_code == 200
        data = response.json()

        recommendations = data["recommendations"]
        # Should have urgent recommendation for critical finding
        priorities = [r["priority"] for r in recommendations]
        assert "URGENT" in priorities

    def test_all_report_formats_for_same_evaluation(self, client: TestClient, completed_evaluation_with_findings: Evaluation):
        """Test that all three report formats work for the same evaluation."""
        formats = ["json", "pdf", "summary"]

        for fmt in formats:
            response = client.get(
                f"/api/evaluations/{completed_evaluation_with_findings.id}/reports?format={fmt}"
            )
            assert response.status_code == 200, f"Format {fmt} failed"

            if fmt == "pdf":
                assert response.headers["content-type"] == "application/pdf"
            else:
                assert response.headers["content-type"] == "application/json"
