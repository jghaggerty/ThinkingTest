"""
Batch Evaluation Example

This script demonstrates how to:
- Run multiple evaluations in parallel
- Compare results across different AI systems
- Export results for reporting
- Track evaluation progress
"""

import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from datetime import datetime


class BiasAPI:
    """Simple client for the AI Bias Diagnostic API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def create_evaluation(self, ai_system_name: str, heuristic_types: List[str],
                         iteration_count: int = 50) -> Dict:
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
        url = f"{self.base_url}/api/evaluations/{evaluation_id}/execute"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()

    def get_evaluation(self, evaluation_id: str) -> Dict:
        url = f"{self.base_url}/api/evaluations/{evaluation_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_heuristics(self, evaluation_id: str) -> List[Dict]:
        url = f"{self.base_url}/api/evaluations/{evaluation_id}/heuristics"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_recommendations(self, evaluation_id: str, mode: str = "both") -> Dict:
        url = f"{self.base_url}/api/evaluations/{evaluation_id}/recommendations"
        params = {"mode": mode}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()


def run_single_evaluation(api: BiasAPI, system_config: Dict) -> Dict:
    """Run a single evaluation and return full results."""

    print(f"Starting evaluation for: {system_config['name']}")

    # Create evaluation
    evaluation = api.create_evaluation(
        ai_system_name=system_config['name'],
        heuristic_types=system_config['heuristics'],
        iteration_count=system_config.get('iterations', 50)
    )

    evaluation_id = evaluation['id']

    # Execute analysis
    result = api.execute_evaluation(evaluation_id)

    # Get detailed findings
    findings = api.get_heuristics(evaluation_id)
    recommendations = api.get_recommendations(evaluation_id, mode="both")

    print(f"✓ Completed: {system_config['name']} - "
          f"Score: {result['overall_score']:.2f} ({result['zone_status']})")

    return {
        "evaluation": result,
        "findings": findings,
        "recommendations": recommendations['recommendations'],
        "config": system_config
    }


def compare_systems(results: List[Dict]) -> None:
    """Print comparison of multiple system evaluations."""

    print("\n" + "=" * 80)
    print("COMPARATIVE ANALYSIS")
    print("=" * 80)

    # Sort by overall score (higher is worse)
    sorted_results = sorted(
        results,
        key=lambda x: x['evaluation']['overall_score'],
        reverse=True
    )

    print("\nRanking (by bias severity):")
    print("-" * 80)

    for i, result in enumerate(sorted_results, 1):
        eval_data = result['evaluation']
        print(f"\n{i}. {eval_data['ai_system_name']}")
        print(f"   Overall Score: {eval_data['overall_score']:.2f}")
        print(f"   Zone: {eval_data['zone_status']}")
        print(f"   Heuristics Tested: {len(result['findings'])}")
        print(f"   Recommendations: {len(result['recommendations'])}")

        # Show top finding
        if result['findings']:
            worst_finding = max(result['findings'],
                              key=lambda x: x['severity_score'])
            print(f"   Worst Finding: {worst_finding['heuristic_type']} "
                  f"(Score: {worst_finding['severity_score']:.1f})")

    # Compare by heuristic type
    print("\n" + "-" * 80)
    print("Heuristic Comparison:")
    print("-" * 80)

    all_heuristics = set()
    for result in results:
        for finding in result['findings']:
            all_heuristics.add(finding['heuristic_type'])

    for heuristic in sorted(all_heuristics):
        print(f"\n{heuristic.replace('_', ' ').title()}:")
        for result in results:
            finding = next(
                (f for f in result['findings'] if f['heuristic_type'] == heuristic),
                None
            )
            if finding:
                print(f"  • {result['evaluation']['ai_system_name'][:30]:30} "
                      f"Score: {finding['severity_score']:5.1f} "
                      f"Confidence: {finding['confidence_level']:5.1%}")


def export_results(results: List[Dict], filename: str = None) -> str:
    """Export results to JSON file."""

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bias_evaluation_results_{timestamp}.json"

    export_data = {
        "export_date": datetime.now().isoformat(),
        "total_evaluations": len(results),
        "results": results
    }

    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)

    print(f"\n✓ Results exported to: {filename}")
    return filename


def main():
    """Run batch evaluation of multiple AI systems."""

    api = BiasAPI()

    # Define systems to evaluate
    systems_to_test = [
        {
            "name": "GPT-4 Customer Support Bot",
            "heuristics": ["anchoring", "confirmation_bias", "availability_heuristic"],
            "iterations": 60
        },
        {
            "name": "Claude Financial Advisor",
            "heuristics": ["loss_aversion", "sunk_cost", "anchoring"],
            "iterations": 60
        },
        {
            "name": "Gemini Content Moderator",
            "heuristics": ["confirmation_bias", "availability_heuristic"],
            "iterations": 50
        },
        {
            "name": "Custom Recommendation Engine",
            "heuristics": ["anchoring", "loss_aversion", "sunk_cost"],
            "iterations": 50
        }
    ]

    print("=" * 80)
    print("BATCH EVALUATION - Multiple AI Systems")
    print("=" * 80)
    print(f"\nEvaluating {len(systems_to_test)} AI systems...")
    print()

    # Run evaluations in parallel
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(run_single_evaluation, api, config)
            for config in systems_to_test
        ]

        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"✗ Evaluation failed: {e}")

    # Compare results
    if results:
        compare_systems(results)

        # Export results
        export_results(results)

    print("\n" + "=" * 80)
    print("Batch evaluation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
