import random
from typing import List, Dict, Tuple
from app.models.heuristic import HeuristicType, Severity


class HeuristicDetector:
    """Service for simulating heuristic bias detection in AI systems."""

    def __init__(self, iteration_count: int):
        self.iteration_count = iteration_count

    def detect_anchoring(self) -> Tuple[Dict, List[str]]:
        """
        Detect anchoring bias.
        Tests if responses vary significantly based on initial anchor values.
        """
        detections = 0
        divergences = []

        for _ in range(self.iteration_count):
            # Simulate test with different anchor values
            anchor_low = random.uniform(10, 30)
            anchor_high = random.uniform(70, 90)

            # Simulate response variance (30% threshold for detection)
            response_variance = random.uniform(5, 60)
            divergences.append(response_variance)

            if response_variance > 30:
                detections += 1

        avg_divergence = sum(divergences) / len(divergences)
        severity_score = min(avg_divergence * 1.5, 100)

        examples = [
            f"Response varied by {divergences[i]:.1f}% when anchor changed from {random.randint(20, 40)} to {random.randint(60, 80)}"
            for i in random.sample(range(len(divergences)), min(3, len(divergences)))
        ]

        result = {
            "detection_count": detections,
            "severity_score": severity_score,
            "severity": self._calculate_severity(severity_score, "anchoring"),
            "pattern_description": f"System over-weighted first piece of information by {avg_divergence:.1f}%",
        }

        return result, examples

    def detect_loss_aversion(self) -> Tuple[Dict, List[str]]:
        """
        Detect loss aversion bias.
        Tests if loss scenarios receive disproportionate weight vs equivalent gains.
        """
        detections = 0
        sensitivity_ratios = []

        for _ in range(self.iteration_count):
            # Simulate gain/loss sensitivity ratio (2x threshold for detection)
            ratio = random.uniform(1.0, 3.5)
            sensitivity_ratios.append(ratio)

            if ratio > 2.0:
                detections += 1

        avg_ratio = sum(sensitivity_ratios) / len(sensitivity_ratios)
        severity_score = min((avg_ratio - 1.0) * 40, 100)

        examples = [
            f"Loss scenario weighted {sensitivity_ratios[i]:.2f}x higher than equivalent gain scenario"
            for i in random.sample(range(len(sensitivity_ratios)), min(3, len(sensitivity_ratios)))
        ]

        result = {
            "detection_count": detections,
            "severity_score": severity_score,
            "severity": self._calculate_severity(severity_score, "loss_aversion"),
            "pattern_description": f"System showed {avg_ratio:.2f}x stronger response to potential losses than equivalent gains",
        }

        return result, examples

    def detect_sunk_cost(self) -> Tuple[Dict, List[str]]:
        """
        Detect sunk cost fallacy.
        Tests if decisions are influenced by irrelevant past costs.
        """
        detections = 0
        influence_rates = []

        for _ in range(self.iteration_count):
            # Simulate influence of sunk costs (threshold varies)
            influence = random.uniform(0, 100)
            influence_rates.append(influence)

            if influence > 50:
                detections += 1

        avg_influence = sum(influence_rates) / len(influence_rates)
        severity_score = min(avg_influence * 0.9, 100)

        examples = [
            f"Prior investment of ${random.randint(1000, 50000)} influenced decision despite irrelevance"
            for _ in range(min(3, detections))
        ]

        result = {
            "detection_count": detections,
            "severity_score": severity_score,
            "severity": self._calculate_severity(severity_score, "sunk_cost"),
            "pattern_description": f"Prior investment influenced {avg_influence:.1f}% of continuation decisions",
        }

        return result, examples

    def detect_confirmation_bias(self) -> Tuple[Dict, List[str]]:
        """
        Detect confirmation bias.
        Tests if system dismisses contradictory evidence.
        """
        detections = 0
        dismissal_rates = []

        for _ in range(self.iteration_count):
            # Simulate evidence dismissal rate (60% threshold)
            dismissal = random.uniform(0, 95)
            dismissal_rates.append(dismissal)

            if dismissal > 60:
                detections += 1

        avg_dismissal = sum(dismissal_rates) / len(dismissal_rates)
        severity_score = min(avg_dismissal * 1.1, 100)

        examples = [
            f"Dismissed {dismissal_rates[i]:.1f}% of contradictory evidence after initial position"
            for i in random.sample(range(len(dismissal_rates)), min(3, len(dismissal_rates)))
        ]

        result = {
            "detection_count": detections,
            "severity_score": severity_score,
            "severity": self._calculate_severity(severity_score, "confirmation_bias"),
            "pattern_description": f"System dismissed {avg_dismissal:.1f}% of contradictory evidence after initial position",
        }

        return result, examples

    def detect_availability_heuristic(self) -> Tuple[Dict, List[str]]:
        """
        Detect availability heuristic.
        Tests if probability estimates are skewed by recent/memorable examples.
        """
        detections = 0
        estimation_errors = []

        for _ in range(self.iteration_count):
            # Simulate probability estimation error (40% threshold)
            error = random.uniform(0, 80)
            estimation_errors.append(error)

            if error > 40:
                detections += 1

        avg_error = sum(estimation_errors) / len(estimation_errors)
        severity_score = min(avg_error * 1.3, 100)

        examples = [
            f"Recent examples biased probability estimate by {estimation_errors[i]:.1f}% for event with actual {random.randint(1, 10)}% likelihood"
            for i in random.sample(range(len(estimation_errors)), min(3, len(estimation_errors)))
        ]

        result = {
            "detection_count": detections,
            "severity_score": severity_score,
            "severity": self._calculate_severity(severity_score, "availability_heuristic"),
            "pattern_description": f"Recent examples biased probability estimates by {avg_error:.1f}%",
        }

        return result, examples

    def _calculate_severity(self, score: float, heuristic_type: str) -> Severity:
        """Calculate severity category based on score and heuristic type."""
        thresholds = {
            "anchoring": {"critical": 75, "high": 50, "medium": 25},
            "loss_aversion": {"critical": 80, "high": 60, "medium": 35},
            "sunk_cost": {"critical": 70, "high": 50, "medium": 30},
            "confirmation_bias": {"critical": 75, "high": 55, "medium": 35},
            "availability_heuristic": {"critical": 70, "high": 50, "medium": 30},
        }

        threshold = thresholds.get(heuristic_type, {"critical": 75, "high": 50, "medium": 25})

        if score >= threshold["critical"]:
            return Severity.CRITICAL
        elif score >= threshold["high"]:
            return Severity.HIGH
        elif score >= threshold["medium"]:
            return Severity.MEDIUM
        else:
            return Severity.LOW

    def calculate_confidence(self, detection_count: int) -> float:
        """
        Calculate confidence level based on detection count and total iterations.
        """
        proportion = detection_count / self.iteration_count
        # Adjust for sample size using simple formula
        confidence = proportion * (1 - (1 / (self.iteration_count ** 0.5)))
        return min(confidence, 0.99)  # Cap at 99%

    def run_detection(self, heuristic_types: List[str]) -> List[Dict]:
        """
        Run detection for specified heuristic types.
        Returns list of findings with all details.
        """
        detectors = {
            "anchoring": self.detect_anchoring,
            "loss_aversion": self.detect_loss_aversion,
            "sunk_cost": self.detect_sunk_cost,
            "confirmation_bias": self.detect_confirmation_bias,
            "availability_heuristic": self.detect_availability_heuristic,
        }

        findings = []

        for htype in heuristic_types:
            if htype in detectors:
                result, examples = detectors[htype]()
                confidence = self.calculate_confidence(result["detection_count"])

                finding = {
                    "heuristic_type": htype,
                    "severity": result["severity"].value,
                    "severity_score": result["severity_score"],
                    "confidence_level": confidence,
                    "detection_count": result["detection_count"],
                    "example_instances": examples,
                    "pattern_description": result["pattern_description"],
                }

                findings.append(finding)

        return findings
