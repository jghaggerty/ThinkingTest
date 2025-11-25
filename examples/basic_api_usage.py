"""
Basic API Usage Example

This script demonstrates the fundamental operations of the AI Bias Diagnostic API:
- Creating an evaluation
- Executing the analysis
- Retrieving results
- Getting recommendations
"""

import requests
import json
import time
from typing import Dict, List


class BiasAPI:
    """Simple client for the AI Bias Diagnostic API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def create_evaluation(
        self,
        ai_system_name: str,
        heuristic_types: List[str],
        iteration_count: int = 50
    ) -> Dict:
        """Create a new evaluation run."""
        url = f"{self.base_url}/api/evaluations"
        payload = {
            "ai_system_name": ai_system_name,
            "heuristic_types": heuristic_types,
            "iteration_count": iteration_count
        }

        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def execute_evaluation(self, evaluation_id: str) -> Dict:
        """Execute the heuristic analysis for an evaluation."""
        url = f"{self.base_url}/api/evaluations/{evaluation_id}/execute"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()

    def get_evaluation(self, evaluation_id: str) -> Dict:
        """Get evaluation details and status."""
        url = f"{self.base_url}/api/evaluations/{evaluation_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def list_evaluations(self, limit: int = 10, offset: int = 0) -> Dict:
        """List all evaluations with pagination."""
        url = f"{self.base_url}/api/evaluations"
        params = {"limit": limit, "offset": offset}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_heuristics(self, evaluation_id: str) -> List[Dict]:
        """Get heuristic findings for an evaluation."""
        url = f"{self.base_url}/api/evaluations/{evaluation_id}/heuristics"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_recommendations(
        self,
        evaluation_id: str,
        mode: str = "both"
    ) -> Dict:
        """Get recommendations for an evaluation.

        Args:
            evaluation_id: The evaluation ID
            mode: 'technical', 'simplified', or 'both'
        """
        url = f"{self.base_url}/api/evaluations/{evaluation_id}/recommendations"
        params = {"mode": mode}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def delete_evaluation(self, evaluation_id: str) -> None:
        """Delete an evaluation."""
        url = f"{self.base_url}/api/evaluations/{evaluation_id}"
        response = self.session.delete(url)
        response.raise_for_status()


def main():
    """Demonstrate basic API usage."""

    # Initialize API client
    api = BiasAPI()

    print("=" * 60)
    print("AI Bias Diagnostic API - Basic Usage Example")
    print("=" * 60)

    # Step 1: Create an evaluation
    print("\n1. Creating a new evaluation...")
    evaluation = api.create_evaluation(
        ai_system_name="GPT-4 Customer Service Bot",
        heuristic_types=[
            "anchoring",
            "confirmation_bias",
            "availability_heuristic"
        ],
        iteration_count=50
    )

    evaluation_id = evaluation["id"]
    print(f"   ✓ Created evaluation: {evaluation_id}")
    print(f"   System: {evaluation['ai_system_name']}")
    print(f"   Status: {evaluation['status']}")

    # Step 2: Execute the evaluation
    print("\n2. Executing heuristic analysis...")
    result = api.execute_evaluation(evaluation_id)
    print(f"   ✓ Analysis complete")
    print(f"   Overall Score: {result['overall_score']:.2f}")
    print(f"   Zone Status: {result['zone_status']}")

    # Step 3: Get heuristic findings
    print("\n3. Retrieving heuristic findings...")
    findings = api.get_heuristics(evaluation_id)
    print(f"   ✓ Found {len(findings)} heuristic patterns\n")

    for finding in findings:
        print(f"   • {finding['heuristic_type'].replace('_', ' ').title()}")
        print(f"     Severity: {finding['severity']} "
              f"(Score: {finding['severity_score']:.1f})")
        print(f"     Confidence: {finding['confidence_level']:.1%}")
        print(f"     Detection Rate: {finding['detection_count']}/{evaluation['iteration_count']}")
        print()

    # Step 4: Get recommendations
    print("4. Getting recommendations...")
    recommendations = api.get_recommendations(evaluation_id, mode="both")
    print(f"   ✓ Generated {recommendations['total']} recommendations\n")

    for i, rec in enumerate(recommendations['recommendations'][:3], 1):
        print(f"   {i}. {rec['action_title']}")
        print(f"      Priority: {rec['priority']}")
        print(f"      Impact: {rec['estimated_impact']}")
        print(f"      Difficulty: {rec['implementation_difficulty']}")
        print(f"      Technical: {rec['technical_description'][:100]}...")
        print()

    # Step 5: List all evaluations
    print("5. Listing all evaluations...")
    all_evals = api.list_evaluations(limit=5)
    print(f"   ✓ Total evaluations: {all_evals['total']}\n")

    for eval_item in all_evals['evaluations'][:3]:
        print(f"   • {eval_item['ai_system_name']}")
        print(f"     ID: {eval_item['id']}")
        print(f"     Status: {eval_item['status']}")
        if eval_item['overall_score']:
            print(f"     Score: {eval_item['overall_score']:.2f} "
                  f"({eval_item['zone_status']})")
        print()

    print("=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
