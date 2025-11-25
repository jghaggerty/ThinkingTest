"""
Quick Start Example

The fastest way to get started with the AI Bias Diagnostic API.
This is a minimal example showing the essential operations.
"""

import requests


# Simple API wrapper
class BiasAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def evaluate(self, system_name, heuristics=None, iterations=50):
        """
        One-shot evaluation: create, execute, and return results.

        Args:
            system_name: Name of your AI system
            heuristics: List of heuristic types to test (default: all)
            iterations: Number of test iterations (10-100)

        Returns:
            dict with evaluation results
        """
        # Default to common heuristics
        if heuristics is None:
            heuristics = ["anchoring", "confirmation_bias", "loss_aversion"]

        # Create evaluation
        response = requests.post(
            f"{self.base_url}/api/evaluations",
            json={
                "ai_system_name": system_name,
                "heuristic_types": heuristics,
                "iteration_count": iterations
            }
        )
        evaluation = response.json()

        # Execute analysis
        response = requests.post(
            f"{self.base_url}/api/evaluations/{evaluation['id']}/execute"
        )
        result = response.json()

        return result


def main():
    """Quick start demonstration."""

    # Initialize API
    api = BiasAPI()

    print("AI Bias Diagnostic - Quick Start")
    print("=" * 50)

    # Run a simple evaluation
    result = api.evaluate(
        system_name="My AI Assistant",
        heuristics=["anchoring", "confirmation_bias"],
        iterations=50
    )

    # Display results
    print(f"\nSystem: {result['ai_system_name']}")
    print(f"Overall Score: {result['overall_score']:.2f}/100")
    print(f"Status: {result['zone_status'].upper()}")

    # Interpret results
    if result['zone_status'] == 'green':
        print("\n✓ Good! Bias levels are within acceptable range.")
    elif result['zone_status'] == 'yellow':
        print("\n⚠ Warning! Moderate bias levels detected.")
    else:
        print("\n❌ Critical! High bias levels require attention.")

    print("\nFor detailed findings and recommendations:")
    print(f"Visit: http://localhost:8000/api/evaluations/{result['id']}/heuristics")
    print(f"   or: http://localhost:8000/api/evaluations/{result['id']}/recommendations")

    print("=" * 50)


if __name__ == "__main__":
    main()
