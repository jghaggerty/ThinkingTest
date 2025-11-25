"""
Integration Patterns Example

This script demonstrates common integration patterns:
- CI/CD pipeline integration
- Automated testing workflows
- Alert/notification systems
- Custom reporting
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


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


class BiasMonitor:
    """Monitor for bias thresholds and alerts."""

    def __init__(self, api: BiasAPI):
        self.api = api
        self.thresholds = {
            "green_max": 40.0,
            "yellow_max": 60.0,
            "critical": 75.0
        }

    def evaluate_and_check(
        self,
        ai_system_name: str,
        heuristic_types: List[str],
        iteration_count: int = 50
    ) -> Dict:
        """Run evaluation and check against thresholds."""

        # Run evaluation
        evaluation = self.api.create_evaluation(
            ai_system_name, heuristic_types, iteration_count
        )
        result = self.api.execute_evaluation(evaluation['id'])

        # Check thresholds
        score = result['overall_score']
        alert_level = self._determine_alert_level(score)

        # Get details if warning or critical
        findings = None
        recommendations = None
        if alert_level in [AlertLevel.WARNING, AlertLevel.CRITICAL]:
            findings = self.api.get_heuristics(evaluation['id'])
            recommendations = self.api.get_recommendations(
                evaluation['id'], mode="simplified"
            )

        return {
            "evaluation": result,
            "alert_level": alert_level,
            "findings": findings,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }

    def _determine_alert_level(self, score: float) -> AlertLevel:
        """Determine alert level based on score."""
        if score > self.thresholds['critical']:
            return AlertLevel.CRITICAL
        elif score > self.thresholds['yellow_max']:
            return AlertLevel.WARNING
        else:
            return AlertLevel.INFO


class CICDIntegration:
    """Integration pattern for CI/CD pipelines."""

    def __init__(self, api: BiasAPI, fail_on_red: bool = True):
        self.api = api
        self.fail_on_red = fail_on_red
        self.monitor = BiasMonitor(api)

    def pre_deployment_check(
        self,
        system_name: str,
        heuristic_types: List[str] = None
    ) -> bool:
        """
        Run bias check before deployment.
        Returns True if deployment should proceed, False otherwise.
        """

        print(f"\n{'='*60}")
        print("PRE-DEPLOYMENT BIAS CHECK")
        print(f"{'='*60}")
        print(f"System: {system_name}")
        print(f"Timestamp: {datetime.now().isoformat()}")

        # Default to all heuristics if not specified
        if heuristic_types is None:
            heuristic_types = [
                "anchoring", "loss_aversion", "sunk_cost",
                "confirmation_bias", "availability_heuristic"
            ]

        # Run evaluation
        result = self.monitor.evaluate_and_check(
            system_name, heuristic_types, iteration_count=60
        )

        # Print results
        eval_data = result['evaluation']
        alert_level = result['alert_level']

        print(f"\nResults:")
        print(f"  Overall Score: {eval_data['overall_score']:.2f}")
        print(f"  Zone Status: {eval_data['zone_status']}")
        print(f"  Alert Level: {alert_level.value.upper()}")

        # Show critical findings
        if result['findings']:
            print(f"\n  Critical Findings:")
            for finding in result['findings']:
                if finding['severity'] in ['high', 'critical']:
                    print(f"    • {finding['heuristic_type']}: "
                          f"{finding['severity_score']:.1f}")

        # Deployment decision
        should_deploy = True
        if alert_level == AlertLevel.CRITICAL and self.fail_on_red:
            should_deploy = False
            print(f"\n{'❌ DEPLOYMENT BLOCKED'}")
            print(f"  Reason: Critical bias levels detected")

            if result['recommendations']:
                print(f"\n  Top Recommendations:")
                for rec in result['recommendations']['recommendations'][:3]:
                    print(f"    {rec['priority']}. {rec['action_title']}")
        else:
            print(f"\n{'✅ DEPLOYMENT APPROVED'}")

        print(f"{'='*60}\n")

        return should_deploy


class ReportGenerator:
    """Generate custom reports for stakeholders."""

    def __init__(self, api: BiasAPI):
        self.api = api

    def generate_executive_summary(
        self,
        evaluation_id: str,
        output_file: Optional[str] = None
    ) -> str:
        """Generate executive summary report."""

        evaluation = self.api.get_evaluation(evaluation_id)
        findings = self.api.get_heuristics(evaluation_id)
        recommendations = self.api.get_recommendations(
            evaluation_id, mode="simplified"
        )

        # Build report
        report = []
        report.append("=" * 80)
        report.append("EXECUTIVE SUMMARY - AI BIAS DIAGNOSTIC REPORT")
        report.append("=" * 80)
        report.append(f"\nSystem: {evaluation['ai_system_name']}")
        report.append(f"Date: {evaluation['completed_at']}")
        report.append(f"\nOVERALL ASSESSMENT: {evaluation['zone_status'].upper()}")
        report.append(f"Risk Score: {evaluation['overall_score']:.1f}/100")

        # Key findings
        report.append("\n" + "-" * 80)
        report.append("KEY FINDINGS")
        report.append("-" * 80)

        high_risk = [f for f in findings if f['severity'] in ['high', 'critical']]
        if high_risk:
            report.append("\nHigh-Risk Biases Detected:")
            for finding in high_risk:
                report.append(f"\n• {finding['heuristic_type'].replace('_', ' ').title()}")
                report.append(f"  Severity: {finding['severity'].upper()}")
                report.append(f"  Pattern: {finding['pattern_description'][:100]}")
        else:
            report.append("\nNo high-risk biases detected.")

        # Recommendations
        report.append("\n" + "-" * 80)
        report.append("RECOMMENDED ACTIONS")
        report.append("-" * 80)

        for rec in recommendations['recommendations'][:5]:
            report.append(f"\n{rec['priority']}. {rec['action_title']}")
            report.append(f"   {rec['simplified_description'][:150]}")
            report.append(f"   Impact: {rec['estimated_impact'].upper()}")

        report.append("\n" + "=" * 80)

        report_text = "\n".join(report)

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Report saved to: {output_file}")

        return report_text

    def get_evaluation(self, evaluation_id: str) -> Dict:
        """Get evaluation details."""
        url = f"{self.api.base_url}/api/evaluations/{evaluation_id}"
        response = self.api.session.get(url)
        response.raise_for_status()
        return response.json()


def demonstrate_cicd_integration():
    """Demonstrate CI/CD integration pattern."""

    api = BiasAPI()
    cicd = CICDIntegration(api, fail_on_red=True)

    print("\n" + "=" * 80)
    print("DEMONSTRATION: CI/CD Pipeline Integration")
    print("=" * 80)

    # Simulate deployment checks for different systems
    systems = [
        ("Low-Risk Chatbot", ["availability_heuristic"]),
        ("Medium-Risk Assistant", ["anchoring", "confirmation_bias"]),
        ("High-Risk Decision System", ["loss_aversion", "sunk_cost", "anchoring"]),
    ]

    results = []
    for system_name, heuristics in systems:
        approved = cicd.pre_deployment_check(system_name, heuristics)
        results.append((system_name, approved))

    # Summary
    print("\nDeployment Summary:")
    print("-" * 80)
    for system, approved in results:
        status = "✅ APPROVED" if approved else "❌ BLOCKED"
        print(f"{system:40s} {status}")


def demonstrate_monitoring():
    """Demonstrate continuous monitoring pattern."""

    api = BiasAPI()
    monitor = BiasMonitor(api)

    print("\n" + "=" * 80)
    print("DEMONSTRATION: Continuous Monitoring")
    print("=" * 80)

    # Monitor a system
    result = monitor.evaluate_and_check(
        "Production Recommendation Engine",
        ["anchoring", "confirmation_bias", "availability_heuristic"],
        iteration_count=50
    )

    print(f"\nMonitoring Result:")
    print(f"  Alert Level: {result['alert_level'].value.upper()}")
    print(f"  Overall Score: {result['evaluation']['overall_score']:.2f}")
    print(f"  Zone: {result['evaluation']['zone_status']}")

    if result['alert_level'] != AlertLevel.INFO:
        print(f"\n  ⚠️  Attention Required!")


def demonstrate_reporting():
    """Demonstrate report generation pattern."""

    api = BiasAPI()
    reporter = ReportGenerator(api)

    print("\n" + "=" * 80)
    print("DEMONSTRATION: Report Generation")
    print("=" * 80)

    # Create a sample evaluation
    evaluation = api.create_evaluation(
        "Enterprise AI Platform",
        ["anchoring", "loss_aversion", "confirmation_bias"],
        iteration_count=50
    )
    api.execute_evaluation(evaluation['id'])

    # Generate report
    report = reporter.generate_executive_summary(
        evaluation['id'],
        output_file="executive_summary.txt"
    )

    print("\nGenerated Report:")
    print(report)


def main():
    """Run all integration pattern demonstrations."""

    print("=" * 80)
    print("API INTEGRATION PATTERNS")
    print("=" * 80)

    # Demonstrate each pattern
    demonstrate_cicd_integration()
    demonstrate_monitoring()
    demonstrate_reporting()

    print("\n" + "=" * 80)
    print("All demonstrations complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
