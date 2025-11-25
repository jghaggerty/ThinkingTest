"""
Test data generator for seeding the database with sample evaluations.
Run with: python -m app.utils.test_data_generator
"""

import random
from datetime import datetime, timedelta

from app.database import SessionLocal, init_db
from app.models import (
    Evaluation,
    EvaluationStatus,
    ZoneStatus,
    HeuristicFinding,
    HeuristicType,
    Severity,
    Baseline,
)
from app.services.heuristic_detector import HeuristicDetector
from app.services.statistical_analyzer import StatisticalAnalyzer


def seed_evaluations():
    """Seed database with sample evaluations."""
    db = SessionLocal()

    try:
        # Sample AI system names
        ai_systems = [
            "GPT-4 Content Moderator",
            "BERT Sentiment Analyzer",
            "LLaMA Financial Advisor",
            "Claude Legal Assistant",
            "T5 Medical Diagnosis Aid",
        ]

        # Heuristic types
        all_heuristics = [
            "anchoring",
            "loss_aversion",
            "sunk_cost",
            "confirmation_bias",
            "availability_heuristic",
        ]

        evaluations_data = []
        overall_scores = []

        # Create 5 sample evaluations
        for i, system_name in enumerate(ai_systems):
            # Random subset of heuristics
            num_heuristics = random.randint(2, 5)
            selected_heuristics = random.sample(all_heuristics, num_heuristics)

            # Random iteration count
            iteration_count = random.choice([10, 20, 30, 50])

            # Create evaluation
            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))

            evaluation = Evaluation(
                ai_system_name=system_name,
                heuristic_types=selected_heuristics,
                iteration_count=iteration_count,
                status=EvaluationStatus.COMPLETED,
                created_at=created_at,
                completed_at=created_at + timedelta(seconds=random.randint(2, 10)),
            )

            db.add(evaluation)
            db.flush()  # Get the ID

            # Generate findings using detector
            detector = HeuristicDetector(iteration_count)
            findings = detector.run_detection(selected_heuristics)

            severity_scores = []
            for finding_data in findings:
                finding = HeuristicFinding(
                    evaluation_id=evaluation.id,
                    heuristic_type=finding_data["heuristic_type"],
                    severity=finding_data["severity"],
                    severity_score=finding_data["severity_score"],
                    confidence_level=finding_data["confidence_level"],
                    detection_count=finding_data["detection_count"],
                    example_instances=finding_data["example_instances"],
                    pattern_description=finding_data["pattern_description"],
                    created_at=evaluation.completed_at,
                )
                db.add(finding)
                severity_scores.append(finding_data["severity_score"])

            # Calculate overall score
            analyzer = StatisticalAnalyzer()
            overall_score = analyzer.calculate_overall_score(severity_scores)
            overall_scores.append(overall_score)

            # Assign zone status to ensure we have examples of each zone
            if i == 0:
                # Force green zone
                overall_score = min(overall_score, 30)
                zone_status = ZoneStatus.GREEN
            elif i == 1:
                # Force yellow zone
                overall_score = min(max(overall_score, 40), 55)
                zone_status = ZoneStatus.YELLOW
            elif i == 2:
                # Force red zone
                overall_score = max(overall_score, 65)
                zone_status = ZoneStatus.RED
            else:
                # Natural zone assignment
                baseline = analyzer.calculate_baseline(overall_scores[:-1])
                zone_status_str = analyzer.determine_zone_status(
                    overall_score, baseline["green_zone_max"], baseline["yellow_zone_max"]
                )
                zone_status = ZoneStatus(zone_status_str)

            evaluation.overall_score = overall_score
            evaluation.zone_status = zone_status

            evaluations_data.append(evaluation)

        db.commit()

        # Create a baseline using the evaluations
        if overall_scores:
            analyzer = StatisticalAnalyzer()
            baseline_params = analyzer.calculate_baseline(overall_scores)

            baseline = Baseline(
                name="Default System Baseline",
                green_zone_max=baseline_params["green_zone_max"],
                yellow_zone_max=baseline_params["yellow_zone_max"],
                statistical_params={
                    "mean": baseline_params["mean"],
                    "std_dev": baseline_params["std_dev"],
                    "sample_size": baseline_params["sample_size"],
                },
            )
            db.add(baseline)
            db.commit()

        print(f"✓ Successfully seeded {len(evaluations_data)} evaluations")
        print(f"✓ Created baseline with parameters: {baseline_params}")

        # Print summary
        print("\nEvaluation Summary:")
        for eval in evaluations_data:
            print(
                f"  - {eval.ai_system_name}: Score={eval.overall_score:.1f}, Zone={eval.zone_status.value}"
            )

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Initialize database and seed with test data."""
    print("Initializing database...")
    init_db()
    print("✓ Database initialized")

    print("\nSeeding test data...")
    seed_evaluations()

    print("\n✓ Database seeding complete!")
    print("\nYou can now start the API server with:")
    print("  uvicorn app.main:app --reload --port 8000")


if __name__ == "__main__":
    main()
