import numpy as np
from typing import List, Dict, Optional


class StatisticalAnalyzer:
    """Service for calculating statistical baselines and trends."""

    @staticmethod
    def calculate_baseline(historical_scores: List[float]) -> Dict:
        """
        Calculate baseline parameters from historical scores.

        Args:
            historical_scores: List of historical severity scores

        Returns:
            Dictionary with mean, std_dev, green_zone_max, yellow_zone_max
        """
        if not historical_scores:
            # Default baseline if no history
            return {
                "mean": 30.0,
                "std_dev": 15.0,
                "green_zone_max": 37.5,
                "yellow_zone_max": 52.5,
                "sample_size": 0,
            }

        scores_array = np.array(historical_scores)
        mean = float(np.mean(scores_array))
        std_dev = float(np.std(scores_array))

        # Calculate zone thresholds
        green_zone_max = mean + (0.5 * std_dev)
        yellow_zone_max = mean + (1.5 * std_dev)
        # Red zone is anything above yellow_zone_max

        return {
            "mean": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "green_zone_max": round(green_zone_max, 2),
            "yellow_zone_max": round(yellow_zone_max, 2),
            "sample_size": len(historical_scores),
        }

    @staticmethod
    def determine_zone_status(score: float, green_max: float, yellow_max: float) -> str:
        """
        Determine which zone a score falls into.

        Args:
            score: The score to evaluate
            green_max: Maximum value for green zone
            yellow_max: Maximum value for yellow zone

        Returns:
            Zone status: "green", "yellow", or "red"
        """
        if score <= green_max:
            return "green"
        elif score <= yellow_max:
            return "yellow"
        else:
            return "red"

    @staticmethod
    def calculate_overall_score(severity_scores: List[float]) -> float:
        """
        Calculate overall score from individual severity scores.
        Uses weighted average with higher weights for worse scores.

        Args:
            severity_scores: List of individual heuristic severity scores

        Returns:
            Overall score (0-100)
        """
        if not severity_scores:
            return 0.0

        # Sort scores in descending order
        sorted_scores = sorted(severity_scores, reverse=True)

        # Weight higher scores more heavily
        weights = [1.0 / (i + 1) for i in range(len(sorted_scores))]
        total_weight = sum(weights)

        weighted_sum = sum(score * weight for score, weight in zip(sorted_scores, weights))
        overall = weighted_sum / total_weight

        return round(overall, 2)

    @staticmethod
    def detect_drift(
        current_score: float,
        historical_scores: List[float],
        threshold: float = 2.0,
    ) -> Dict:
        """
        Detect if current score shows significant drift from baseline.

        Args:
            current_score: Current evaluation score
            historical_scores: List of historical scores
            threshold: Number of standard deviations for drift alert

        Returns:
            Dictionary with drift status and details
        """
        if len(historical_scores) < 3:
            return {
                "has_drift": False,
                "message": "Insufficient historical data for drift detection",
            }

        scores_array = np.array(historical_scores)
        mean = np.mean(scores_array)
        std_dev = np.std(scores_array)

        if std_dev == 0:
            return {
                "has_drift": current_score != mean,
                "message": f"Score differs from constant baseline of {mean:.2f}",
                "deviation": abs(current_score - mean),
            }

        # Calculate z-score
        z_score = (current_score - mean) / std_dev

        has_drift = abs(z_score) > threshold

        return {
            "has_drift": has_drift,
            "z_score": round(z_score, 2),
            "deviation": round(abs(current_score - mean), 2),
            "message": f"Score is {abs(z_score):.2f} standard deviations from baseline"
            if has_drift
            else "No significant drift detected",
        }

    @staticmethod
    def calculate_trend(scores_over_time: List[Dict]) -> Dict:
        """
        Calculate trend direction and magnitude.

        Args:
            scores_over_time: List of dicts with 'timestamp' and 'score'

        Returns:
            Dictionary with trend analysis
        """
        if len(scores_over_time) < 2:
            return {
                "trend": "insufficient_data",
                "direction": None,
                "magnitude": 0,
            }

        # Extract scores
        scores = [item["score"] for item in scores_over_time]

        # Calculate simple linear trend
        n = len(scores)
        x = np.arange(n)
        y = np.array(scores)

        # Calculate slope (trend direction)
        x_mean = np.mean(x)
        y_mean = np.mean(y)

        numerator = np.sum((x - x_mean) * (y - y_mean))
        denominator = np.sum((x - x_mean) ** 2)

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        # Determine trend direction
        if abs(slope) < 0.5:
            direction = "stable"
        elif slope > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return {
            "trend": direction,
            "slope": round(slope, 3),
            "magnitude": round(abs(slope), 3),
            "start_score": scores[0],
            "end_score": scores[-1],
            "change": round(scores[-1] - scores[0], 2),
        }
