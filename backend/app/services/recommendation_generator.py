from typing import List, Dict
from app.models.recommendation import Impact, Difficulty


class RecommendationGenerator:
    """Service for generating mitigation recommendations based on detected heuristics."""

    # Pre-defined recommendation templates for each heuristic type
    RECOMMENDATIONS = {
        "anchoring": [
            {
                "action_title": "Implement multi-perspective prompting",
                "technical_description": "Restructure prompts to present multiple baseline values before eliciting response. Use ensemble methods that aggregate responses from different anchor points to reduce single-anchor dependency.",
                "simplified_description": "Present multiple starting points to prevent over-reliance on first value. Like getting multiple estimates before making a decision.",
                "estimated_impact": Impact.HIGH,
                "implementation_difficulty": Difficulty.EASY,
                "base_priority": 9,
            },
            {
                "action_title": "Add anchor randomization layer",
                "technical_description": "Implement preprocessing that randomly varies initial context values across inference calls. Monitor response variance and flag high-variance outputs for review.",
                "simplified_description": "Change the starting information randomly to see if answers stay consistent. Flag cases where answers change too much.",
                "estimated_impact": Impact.MEDIUM,
                "implementation_difficulty": Difficulty.MODERATE,
                "base_priority": 7,
            },
            {
                "action_title": "Enable anchor-free reasoning mode",
                "technical_description": "Develop alternative reasoning pipeline that derives responses from first principles without reference points. Compare outputs between anchored and anchor-free modes.",
                "simplified_description": "Create a way to think through problems from scratch without initial reference points as a comparison.",
                "estimated_impact": Impact.HIGH,
                "implementation_difficulty": Difficulty.COMPLEX,
                "base_priority": 6,
            },
        ],
        "loss_aversion": [
            {
                "action_title": "Implement gain-loss normalization",
                "technical_description": "Add preprocessing layer that equalizes the salience of gain and loss framing. Apply calibration to ensure equivalent scenarios receive equal weighting regardless of framing.",
                "simplified_description": "Make sure the system treats potential gains and losses equally when they're the same size.",
                "estimated_impact": Impact.HIGH,
                "implementation_difficulty": Difficulty.MODERATE,
                "base_priority": 9,
            },
            {
                "action_title": "Add framing diversity training",
                "technical_description": "Augment training data with equivalent gain/loss scenarios. Fine-tune model to recognize and neutralize asymmetric loss sensitivity.",
                "simplified_description": "Teach the system to recognize when it's being too sensitive to losses compared to gains.",
                "estimated_impact": Impact.MEDIUM,
                "implementation_difficulty": Difficulty.COMPLEX,
                "base_priority": 7,
            },
            {
                "action_title": "Enable risk-neutral evaluation mode",
                "technical_description": "Implement utility-based decision framework that explicitly models risk preferences. Allow configuration of risk tolerance parameters.",
                "simplified_description": "Add settings to control how much the system should care about avoiding losses versus seeking gains.",
                "estimated_impact": Impact.MEDIUM,
                "implementation_difficulty": Difficulty.MODERATE,
                "base_priority": 6,
            },
        ],
        "sunk_cost": [
            {
                "action_title": "Implement prospective-only analysis",
                "technical_description": "Modify decision logic to exclude historical cost information from forward-looking evaluations. Create input filters that strip sunk cost references.",
                "simplified_description": "Make decisions based only on future costs and benefits, ignoring money already spent.",
                "estimated_impact": Impact.HIGH,
                "implementation_difficulty": Difficulty.EASY,
                "base_priority": 8,
            },
            {
                "action_title": "Add sunk cost detection layer",
                "technical_description": "Build classifier to identify when past investments are mentioned in decision contexts. Flag these cases and provide alternative analysis excluding sunk costs.",
                "simplified_description": "Automatically detect when past spending is mentioned and show what the decision would be without considering it.",
                "estimated_impact": Impact.MEDIUM,
                "implementation_difficulty": Difficulty.MODERATE,
                "base_priority": 7,
            },
            {
                "action_title": "Enable zero-based decision mode",
                "technical_description": "Implement reasoning mode that evaluates scenarios as if starting from scratch. Present side-by-side comparison with sunk-cost-aware analysis.",
                "simplified_description": "Show what the decision would be if starting fresh today, for comparison with current approach.",
                "estimated_impact": Impact.HIGH,
                "implementation_difficulty": Difficulty.MODERATE,
                "base_priority": 8,
            },
        ],
        "confirmation_bias": [
            {
                "action_title": "Implement adversarial evidence search",
                "technical_description": "Add dedicated search phase for evidence contradicting initial hypothesis. Weight contradictory evidence equally or higher in final reasoning.",
                "simplified_description": "Actively look for information that disagrees with the first conclusion and give it fair consideration.",
                "estimated_impact": Impact.HIGH,
                "implementation_difficulty": Difficulty.MODERATE,
                "base_priority": 9,
            },
            {
                "action_title": "Enable red team reasoning mode",
                "technical_description": "Implement dual-process reasoning where second pass actively argues against initial conclusion. Synthesize final output from thesis-antithesis analysis.",
                "simplified_description": "Have the system argue against its own first answer, then combine both perspectives.",
                "estimated_impact": Impact.HIGH,
                "implementation_difficulty": Difficulty.COMPLEX,
                "base_priority": 8,
            },
            {
                "action_title": "Add evidence diversity metrics",
                "technical_description": "Track ratio of confirming vs. contradicting evidence in reasoning chain. Alert when ratio exceeds threshold (e.g., >3:1).",
                "simplified_description": "Monitor whether the system is only looking at evidence that supports its initial idea.",
                "estimated_impact": Impact.MEDIUM,
                "implementation_difficulty": Difficulty.EASY,
                "base_priority": 6,
            },
        ],
        "availability_heuristic": [
            {
                "action_title": "Implement base rate integration",
                "technical_description": "Augment reasoning with explicit statistical base rates from reliable sources. Weight base rate information higher than anecdotal examples in probability estimates.",
                "simplified_description": "Use actual statistics and data instead of relying on memorable examples when estimating likelihood.",
                "estimated_impact": Impact.HIGH,
                "implementation_difficulty": Difficulty.MODERATE,
                "base_priority": 9,
            },
            {
                "action_title": "Add recency weighting correction",
                "technical_description": "Implement temporal discounting that reduces influence of recent examples on probability judgments. Calibrate against known frequency distributions.",
                "simplified_description": "Reduce the influence of recent dramatic examples on probability estimates.",
                "estimated_impact": Impact.MEDIUM,
                "implementation_difficulty": Difficulty.MODERATE,
                "base_priority": 7,
            },
            {
                "action_title": "Enable statistical grounding mode",
                "technical_description": "Require all probability estimates to reference empirical frequency data. Flag estimates based solely on examples or intuition.",
                "simplified_description": "Make the system show real data sources for probability claims instead of guessing from examples.",
                "estimated_impact": Impact.HIGH,
                "implementation_difficulty": Difficulty.EASY,
                "base_priority": 8,
            },
        ],
    }

    @staticmethod
    def calculate_priority(
        severity_score: float,
        confidence_level: float,
        base_priority: int,
    ) -> int:
        """
        Calculate recommendation priority score.

        Args:
            severity_score: Severity score of the finding (0-100)
            confidence_level: Confidence level (0-1)
            base_priority: Base priority from recommendation template (1-10)

        Returns:
            Priority score (1-10)
        """
        # Normalize severity to 0-10 scale
        severity_component = (severity_score / 100) * 6  # Max 6 points
        confidence_component = confidence_level * 3  # Max 3 points
        base_component = base_priority * 0.1  # Max 1 point

        priority = severity_component + confidence_component + base_component
        return min(max(round(priority), 1), 10)  # Clamp to 1-10

    def generate_recommendations(
        self, findings: List[Dict], mode: str = "both"
    ) -> List[Dict]:
        """
        Generate prioritized recommendations based on findings.

        Args:
            findings: List of heuristic findings
            mode: "technical", "simplified", or "both"

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []

        for finding in findings:
            heuristic_type = finding.get("heuristic_type")
            severity_score = finding.get("severity_score", 0)
            confidence_level = finding.get("confidence_level", 0)

            if heuristic_type not in self.RECOMMENDATIONS:
                continue

            templates = self.RECOMMENDATIONS[heuristic_type]

            for template in templates:
                priority = self.calculate_priority(
                    severity_score, confidence_level, template["base_priority"]
                )

                recommendation = {
                    "heuristic_type": heuristic_type,
                    "priority": priority,
                    "action_title": template["action_title"],
                    "technical_description": template["technical_description"],
                    "simplified_description": template["simplified_description"],
                    "estimated_impact": template["estimated_impact"],
                    "implementation_difficulty": template["implementation_difficulty"],
                }

                recommendations.append(recommendation)

        # Sort by priority (descending)
        recommendations.sort(key=lambda x: x["priority"], reverse=True)

        # Return top 7 recommendations
        return recommendations[:7]

    @staticmethod
    def format_for_mode(recommendations: List[Dict], mode: str) -> List[Dict]:
        """
        Format recommendations based on requested mode.

        Args:
            recommendations: List of recommendations
            mode: "technical", "simplified", or "both"

        Returns:
            Formatted recommendations
        """
        if mode == "technical":
            for rec in recommendations:
                rec.pop("simplified_description", None)
        elif mode == "simplified":
            for rec in recommendations:
                rec.pop("technical_description", None)
        # If mode is "both", keep all fields

        return recommendations
