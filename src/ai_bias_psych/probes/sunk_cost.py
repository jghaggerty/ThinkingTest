"""
Sunk cost fallacy probe implementation.

This module implements probes to test for sunk cost fallacy, where people continue
to invest in failing actions due to prior investment, even when it would be more
rational to abandon the project and cut losses.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .base import BaseProbe
from .types import ProbeType, ResponseFormat, ProbeVariant
from .types import ProbeRequest


class SunkCostProbe(BaseProbe):
    """
    Sunk cost fallacy bias probe.
    
    Tests for the tendency to continue investing in failing actions due to prior
    investment, even when it would be more rational to abandon the project and
    cut losses. This bias occurs when people feel compelled to "get their money's worth"
    from past investments.
    
    This probe uses multi-turn conversation scenarios to test for sunk cost bias.
    """
    
    def __init__(self):
        super().__init__(
            probe_type=ProbeType.SUNK_COST,
            name="Sunk Cost Fallacy",
            description="Tests for continued commitment to failing actions due to prior investment"
        )
        self.variants: Dict[str, ProbeVariant] = {}
    
    def load_variants(self, config: Dict[str, Any]) -> None:
        """
        Load sunk cost fallacy variants from configuration.
        
        Args:
            config: Configuration dictionary containing variant definitions
        """
        sunk_cost_config = config.get("probes", {}).get("sunk_cost", {})
        variants_config = sunk_cost_config.get("variants", [])
        
        for variant_config in variants_config:
            variant_id = variant_config["id"]
            domain = variant_config["domain"]
            expected_choice = variant_config.get("expected_choice", "switch")
            
            # Create variant for the sunk cost scenario
            variant = ProbeVariant(
                id=variant_id,
                domain=domain,
                prompt=variant_config["scenario"],
                expected_bias="sunk_cost_fallacy",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params={
                    "expected_choice": expected_choice,
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "original_id": variant_id,
                    "expected_choice": expected_choice,
                    "scenario_type": "sunk_cost_decision"
                }
            )
            
            self.variants[variant.id] = variant
    
    def score_response(self, response: str, variant: ProbeVariant, 
                      execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a model's response for sunk cost fallacy bias indicators.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            execution_metadata: Additional metadata from the execution
            
        Returns:
            Dictionary containing bias score, confidence, and analysis details
        """
        expected_choice = variant.metadata.get("expected_choice", "switch")
        scoring_params = variant.scoring_params
        
        # Analyze the decision in the response
        decision_analysis = self._analyze_decision(response, variant)
        
        # Calculate sunk cost bias score
        bias_score = self._calculate_sunk_cost_bias(
            decision_analysis, expected_choice, scoring_params
        )
        
        # Calculate confidence based on response quality
        confidence = self._calculate_confidence(response, decision_analysis)
        
        return {
            "bias_score": bias_score,
            "confidence": confidence,
            "expected_choice": expected_choice,
            "decision_analysis": decision_analysis,
            "bias_analysis": {
                "decision": decision_analysis.get("decision"),
                "sunk_cost_mentions": decision_analysis.get("sunk_cost_mentions"),
                "rational_reasoning": decision_analysis.get("rational_reasoning"),
                "emotional_reasoning": decision_analysis.get("emotional_reasoning"),
                "decision_confidence": decision_analysis.get("decision_confidence")
            }
        }
    
    def _analyze_decision(self, response: str, variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze the decision made in the response.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Dictionary containing decision analysis
        """
        response_lower = response.lower()
        
        # Define decision indicators
        continue_indicators = [
            "continue", "keep going", "stick with", "persist", "push through",
            "finish what we started", "see it through", "don't give up",
            "already invested", "too much invested", "can't quit now"
        ]
        
        switch_indicators = [
            "switch", "change", "abandon", "cut losses", "start over",
            "new approach", "better option", "more efficient", "cost-effective",
            "rational decision", "logical choice", "move on"
        ]
        
        # Count decision indicators
        continue_count = sum(1 for indicator in continue_indicators 
                           if indicator in response_lower)
        switch_count = sum(1 for indicator in switch_indicators 
                         if indicator in response_lower)
        
        # Determine decision
        if continue_count > switch_count:
            decision = "continue"
            decision_confidence = min(continue_count / 3.0, 1.0)
        elif switch_count > continue_count:
            decision = "switch"
            decision_confidence = min(switch_count / 3.0, 1.0)
        else:
            decision = "unclear"
            decision_confidence = 0.0
        
        # Analyze sunk cost mentions
        sunk_cost_mentions = self._analyze_sunk_cost_mentions(response)
        
        # Analyze reasoning types
        rational_reasoning = self._analyze_rational_reasoning(response)
        emotional_reasoning = self._analyze_emotional_reasoning(response)
        
        return {
            "decision": decision,
            "decision_confidence": decision_confidence,
            "continue_count": continue_count,
            "switch_count": switch_count,
            "sunk_cost_mentions": sunk_cost_mentions,
            "rational_reasoning": rational_reasoning,
            "emotional_reasoning": emotional_reasoning,
            "response_length": len(response)
        }
    
    def _analyze_sunk_cost_mentions(self, response: str) -> Dict[str, Any]:
        """
        Analyze mentions of sunk costs in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Dictionary containing sunk cost analysis
        """
        response_lower = response.lower()
        
        # Sunk cost indicators
        sunk_cost_indicators = [
            "already spent", "already invested", "money spent", "time invested",
            "can't waste", "throwing away", "lose the investment", "sunk cost",
            "too much to lose", "have to finish", "get our money's worth"
        ]
        
        # Count sunk cost mentions
        sunk_cost_count = sum(1 for indicator in sunk_cost_indicators 
                            if indicator in response_lower)
        
        # Determine if sunk cost reasoning is present
        has_sunk_cost_reasoning = sunk_cost_count > 0
        
        return {
            "has_sunk_cost_reasoning": has_sunk_cost_reasoning,
            "sunk_cost_count": sunk_cost_count,
            "sunk_cost_strength": min(sunk_cost_count / 3.0, 1.0)
        }
    
    def _analyze_rational_reasoning(self, response: str) -> Dict[str, Any]:
        """
        Analyze rational reasoning in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Dictionary containing rational reasoning analysis
        """
        response_lower = response.lower()
        
        # Rational reasoning indicators
        rational_indicators = [
            "cost-benefit", "return on investment", "efficiency", "effectiveness",
            "better option", "more cost-effective", "logical", "rational",
            "data shows", "evidence suggests", "analysis indicates",
            "future costs", "opportunity cost", "marginal benefit"
        ]
        
        # Count rational indicators
        rational_count = sum(1 for indicator in rational_indicators 
                           if indicator in response_lower)
        
        return {
            "has_rational_reasoning": rational_count > 0,
            "rational_count": rational_count,
            "rational_strength": min(rational_count / 3.0, 1.0)
        }
    
    def _analyze_emotional_reasoning(self, response: str) -> Dict[str, Any]:
        """
        Analyze emotional reasoning in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Dictionary containing emotional reasoning analysis
        """
        response_lower = response.lower()
        
        # Emotional reasoning indicators
        emotional_indicators = [
            "feel", "emotion", "pride", "ego", "reputation", "face",
            "can't give up", "failure", "waste", "regret", "disappointment",
            "stubborn", "persistent", "determined", "committed"
        ]
        
        # Count emotional indicators
        emotional_count = sum(1 for indicator in emotional_indicators 
                            if indicator in response_lower)
        
        return {
            "has_emotional_reasoning": emotional_count > 0,
            "emotional_count": emotional_count,
            "emotional_strength": min(emotional_count / 3.0, 1.0)
        }
    
    def _calculate_sunk_cost_bias(self, decision_analysis: Dict[str, Any], 
                                expected_choice: str, scoring_params: Dict[str, Any]) -> float:
        """
        Calculate sunk cost bias score based on decision analysis.
        
        Args:
            decision_analysis: Analysis of the decision made
            expected_choice: The expected rational choice
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        decision = decision_analysis.get("decision", "unclear")
        sunk_cost_mentions = decision_analysis.get("sunk_cost_mentions", {})
        rational_reasoning = decision_analysis.get("rational_reasoning", {})
        emotional_reasoning = decision_analysis.get("emotional_reasoning", {})
        
        # Sunk cost fallacy occurs when decision is to continue despite better alternatives
        if decision == "continue" and expected_choice == "switch":
            # Check if sunk cost reasoning is present
            if sunk_cost_mentions.get("has_sunk_cost_reasoning", False):
                # Strong sunk cost bias
                base_score = scoring_params.get("continue_current", 1.0)
                sunk_cost_strength = sunk_cost_mentions.get("sunk_cost_strength", 0.0)
                return base_score * sunk_cost_strength
            else:
                # Moderate sunk cost bias (continuing but not explicitly mentioning sunk costs)
                return 0.5
        elif decision == "switch" and expected_choice == "switch":
            # Rational decision - no bias
            return 0.0
        elif decision == "unclear":
            # Unclear decision - partial bias
            return 0.3
        else:
            # Other cases
            return 0.0
    
    def _calculate_confidence(self, response: str, decision_analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence in the bias score based on response quality.
        
        Args:
            response: The model's response text
            decision_analysis: Analysis of the decision
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = decision_analysis.get("decision_confidence", 0.0)
        rational_reasoning = decision_analysis.get("rational_reasoning", {})
        emotional_reasoning = decision_analysis.get("emotional_reasoning", {})
        
        # Increase confidence if there's clear reasoning
        if rational_reasoning.get("has_rational_reasoning", False):
            base_confidence += 0.2
        if emotional_reasoning.get("has_emotional_reasoning", False):
            base_confidence += 0.1
        
        # Adjust based on response length
        response_length = decision_analysis.get("response_length", 0)
        if response_length > 100:
            base_confidence += 0.1
        elif response_length < 50:
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def analyze_sunk_cost_patterns(self, responses: List[str], 
                                 variants: List[ProbeVariant]) -> Dict[str, Any]:
        """
        Analyze patterns across multiple sunk cost responses.
        
        Args:
            responses: List of responses to analyze
            variants: List of corresponding variants
            
        Returns:
            Dictionary containing pattern analysis
        """
        if len(responses) != len(variants):
            raise ValueError("Number of responses must match number of variants")
        
        analyses = []
        for response, variant in zip(responses, variants):
            analysis = self._analyze_decision(response, variant)
            analyses.append(analysis)
        
        # Calculate aggregate statistics
        continue_count = sum(1 for analysis in analyses 
                           if analysis.get("decision") == "continue")
        switch_count = sum(1 for analysis in analyses 
                         if analysis.get("decision") == "switch")
        unclear_count = sum(1 for analysis in analyses 
                          if analysis.get("decision") == "unclear")
        
        # Calculate sunk cost reasoning prevalence
        sunk_cost_reasoning_count = sum(1 for analysis in analyses 
                                      if analysis.get("sunk_cost_mentions", {}).get("has_sunk_cost_reasoning", False))
        
        # Calculate rational reasoning prevalence
        rational_reasoning_count = sum(1 for analysis in analyses 
                                     if analysis.get("rational_reasoning", {}).get("has_rational_reasoning", False))
        
        return {
            "total_responses": len(responses),
            "continue_decisions": continue_count,
            "switch_decisions": switch_count,
            "unclear_decisions": unclear_count,
            "sunk_cost_reasoning_prevalence": sunk_cost_reasoning_count / len(responses),
            "rational_reasoning_prevalence": rational_reasoning_count / len(responses),
            "sunk_cost_bias_prevalence": continue_count / len(responses),
            "individual_analyses": analyses
        }
    
    def get_scenario_details(self, variant_id: str) -> Dict[str, Any]:
        """
        Get detailed scenario information for a variant.
        
        Args:
            variant_id: The variant identifier
            
        Returns:
            Dictionary containing scenario details
        """
        variant = self.variants.get(variant_id)
        if not variant:
            return {}
        
        return {
            "scenario": variant.prompt,
            "domain": variant.domain,
            "expected_choice": variant.metadata.get("expected_choice"),
            "scenario_type": variant.metadata.get("scenario_type")
        }
    
    def extract_investment_amounts(self, response: str) -> Dict[str, Any]:
        """
        Extract investment amounts mentioned in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Dictionary containing investment analysis
        """
        # Look for monetary amounts
        money_pattern = r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)'
        money_matches = re.findall(money_pattern, response)
        
        # Look for time investments
        time_pattern = r'(\d+)\s*(?:months?|years?|weeks?|days?)'
        time_matches = re.findall(time_pattern, response.lower())
        
        return {
            "monetary_amounts": [float(amount.replace(',', '')) for amount in money_matches],
            "time_investments": [int(time) for time in time_matches],
            "total_monetary_mentioned": sum(float(amount.replace(',', '')) for amount in money_matches),
            "total_time_mentioned": sum(int(time) for time in time_matches)
        }
