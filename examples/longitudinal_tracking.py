"""
Longitudinal Tracking Example

This script demonstrates how to:
- Track bias trends over time
- Create statistical baselines
- Monitor improvements after remediation
- Generate trend reports
"""

import requests
import json
from typing import List, Dict
from datetime import datetime, timedelta
import time


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

    def list_evaluations(self, limit: int = 100, offset: int = 0) -> Dict:
        url = f"{self.base_url}/api/evaluations"
        params = {"limit": limit, "offset": offset}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_heuristics(self, evaluation_id: str) -> List[Dict]:
        url = f"{self.base_url}/api/evaluations/{evaluation_id}/heuristics"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def create_baseline(self, evaluation_ids: List[str], name: str,
                       description: str = "") -> Dict:
        url = f"{self.base_url}/api/baselines"
        payload = {
            "evaluation_ids": evaluation_ids,
            "name": name,
            "description": description
        }
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_baseline(self, baseline_id: str) -> Dict:
        url = f"{self.base_url}/api/baselines/{baseline_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_trends(self, evaluation_id: str) -> Dict:
        url = f"{self.base_url}/api/baselines/evaluations/{evaluation_id}/trends"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()


def simulate_monthly_evaluations(api: BiasAPI, system_name: str,
                                 months: int = 6) -> List[Dict]:
    """Simulate monthly evaluations to demonstrate trend tracking."""

    print(f"\nSimulating {months} months of evaluations for: {system_name}")
    print("-" * 60)

    heuristics = ["anchoring", "loss_aversion", "confirmation_bias"]
    evaluations = []

    for month in range(months):
        print(f"Month {month + 1}: ", end="", flush=True)

        # Create and execute evaluation
        eval_data = api.create_evaluation(
            ai_system_name=f"{system_name} (Month {month + 1})",
            heuristic_types=heuristics,
            iteration_count=50
        )

        result = api.execute_evaluation(eval_data['id'])
        evaluations.append(result)

        print(f"Score: {result['overall_score']:.2f} ({result['zone_status']})")

        # Small delay to simulate time passing
        time.sleep(0.5)

    return evaluations


def analyze_trends(evaluations: List[Dict]) -> Dict:
    """Analyze trends across multiple evaluations."""

    scores = [e['overall_score'] for e in evaluations]
    zones = [e['zone_status'] for e in evaluations]

    # Calculate trend metrics
    initial_score = scores[0]
    final_score = scores[-1]
    improvement = initial_score - final_score  # Lower is better
    improvement_pct = (improvement / initial_score * 100) if initial_score > 0 else 0

    # Count zone changes
    green_count = zones.count('green')
    yellow_count = zones.count('yellow')
    red_count = zones.count('red')

    # Calculate volatility (standard deviation)
    mean_score = sum(scores) / len(scores)
    variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
    volatility = variance ** 0.5

    return {
        "initial_score": initial_score,
        "final_score": final_score,
        "improvement": improvement,
        "improvement_percentage": improvement_pct,
        "mean_score": mean_score,
        "volatility": volatility,
        "green_months": green_count,
        "yellow_months": yellow_count,
        "red_months": red_count,
        "total_evaluations": len(evaluations),
        "trend": "improving" if improvement > 0 else "worsening" if improvement < 0 else "stable"
    }


def print_trend_report(system_name: str, evaluations: List[Dict],
                      trends: Dict) -> None:
    """Print a formatted trend analysis report."""

    print("\n" + "=" * 80)
    print(f"LONGITUDINAL TREND REPORT: {system_name}")
    print("=" * 80)

    # Timeline
    print("\nTimeline:")
    print("-" * 80)
    for i, eval_data in enumerate(evaluations, 1):
        print(f"Month {i:2d}: Score {eval_data['overall_score']:5.2f} "
              f"[{eval_data['zone_status'].upper():6s}] "
              f"- {eval_data['ai_system_name']}")

    # Summary statistics
    print("\nSummary Statistics:")
    print("-" * 80)
    print(f"Initial Score:     {trends['initial_score']:.2f}")
    print(f"Final Score:       {trends['final_score']:.2f}")
    print(f"Mean Score:        {trends['mean_score']:.2f}")
    print(f"Volatility (σ):    {trends['volatility']:.2f}")
    print(f"Overall Trend:     {trends['trend'].upper()}")

    if trends['improvement'] != 0:
        direction = "↓" if trends['improvement'] > 0 else "↑"
        print(f"Change:            {direction} {abs(trends['improvement']):.2f} "
              f"({abs(trends['improvement_percentage']):.1f}%)")

    # Zone distribution
    print("\nZone Distribution:")
    print("-" * 80)
    total = trends['total_evaluations']
    print(f"Green Zone:  {trends['green_months']:2d} months "
          f"({trends['green_months']/total*100:5.1f}%)")
    print(f"Yellow Zone: {trends['yellow_months']:2d} months "
          f"({trends['yellow_months']/total*100:5.1f}%)")
    print(f"Red Zone:    {trends['red_months']:2d} months "
          f"({trends['red_months']/total*100:5.1f}%)")

    # Interpretation
    print("\nInterpretation:")
    print("-" * 80)
    if trends['trend'] == "improving":
        print("✓ Positive trend detected. Bias mitigation efforts are working.")
    elif trends['trend'] == "worsening":
        print("⚠ Negative trend detected. Immediate attention required.")
    else:
        print("→ Stable performance. Continue monitoring.")

    if trends['volatility'] > 10:
        print("⚠ High volatility detected. Performance is inconsistent.")
    else:
        print("✓ Low volatility. Performance is stable.")


def track_heuristic_improvements(api: BiasAPI, evaluations: List[Dict]) -> None:
    """Track improvements for specific heuristic types over time."""

    print("\n" + "=" * 80)
    print("HEURISTIC-SPECIFIC TRENDS")
    print("=" * 80)

    # Get findings for each evaluation
    all_findings = {}
    for eval_data in evaluations:
        findings = api.get_heuristics(eval_data['id'])
        month = eval_data['ai_system_name'].split('(Month ')[-1].rstrip(')')
        all_findings[month] = {f['heuristic_type']: f for f in findings}

    # Analyze each heuristic type
    heuristic_types = set()
    for findings in all_findings.values():
        heuristic_types.update(findings.keys())

    for heuristic in sorted(heuristic_types):
        print(f"\n{heuristic.replace('_', ' ').title()}:")
        print("-" * 60)

        scores = []
        for month in sorted(all_findings.keys(), key=int):
            if heuristic in all_findings[month]:
                finding = all_findings[month][heuristic]
                score = finding['severity_score']
                scores.append(score)
                print(f"  Month {month}: {score:5.1f} "
                      f"[{finding['severity'].upper():8s}] "
                      f"Confidence: {finding['confidence_level']:.1%}")

        if len(scores) > 1:
            change = scores[0] - scores[-1]
            change_pct = (change / scores[0] * 100) if scores[0] > 0 else 0
            direction = "↓" if change > 0 else "↑" if change < 0 else "→"
            print(f"  Change: {direction} {abs(change):.1f} ({abs(change_pct):.1f}%)")


def main():
    """Demonstrate longitudinal tracking capabilities."""

    api = BiasAPI()

    print("=" * 80)
    print("LONGITUDINAL BIAS TRACKING")
    print("=" * 80)

    # Simulate 6 months of evaluations
    system_name = "Production Customer Service AI"
    evaluations = simulate_monthly_evaluations(api, system_name, months=6)

    # Analyze overall trends
    trends = analyze_trends(evaluations)
    print_trend_report(system_name, evaluations, trends)

    # Track heuristic-specific improvements
    track_heuristic_improvements(api, evaluations)

    # Create baseline from first 3 months
    print("\n" + "=" * 80)
    print("BASELINE CREATION")
    print("=" * 80)

    baseline_eval_ids = [e['id'] for e in evaluations[:3]]
    baseline = api.create_baseline(
        evaluation_ids=baseline_eval_ids,
        name=f"{system_name} - Baseline (Q1)",
        description="First quarter baseline for comparison"
    )

    print(f"\n✓ Created baseline: {baseline['id']}")
    print(f"  Name: {baseline['name']}")
    print(f"  Mean Score: {baseline['mean_score']:.2f}")
    print(f"  Std Dev: {baseline['std_dev']:.2f}")
    print(f"  Green Zone: ≤ {baseline['green_zone_max']:.2f}")
    print(f"  Yellow Zone: ≤ {baseline['yellow_zone_max']:.2f}")
    print(f"  Red Zone: > {baseline['yellow_zone_max']:.2f}")

    print("\n" + "=" * 80)
    print("Longitudinal tracking complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
