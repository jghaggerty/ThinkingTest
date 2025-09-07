"""
Prospect Theory / Loss Aversion probe implementation.

This module implements probes to test for prospect theory effects, specifically
risk-averse behavior in gains vs risk-seeking behavior in losses.
"""

import random
import re
from typing import Dict, Any, List, Optional
from .base import BaseProbe
from .types import ProbeType, ResponseFormat, ProbeVariant
from ..models.probe import ProbeRequest


class ProspectTheoryProbe(BaseProbe):
    """
    Prospect Theory / Loss Aversion bias probe.
    
    Tests for the classic prospect theory effect where people are:
    - Risk-averse when facing gains (prefer certain gains over risky gains)
    - Risk-seeking when facing losses (prefer risky losses over certain losses)
    
    This probe uses gain/loss framing variants to detect this bias pattern.
    """
    
    def __init__(self):
        super().__init__(
            probe_type=ProbeType.PROSPECT_THEORY,
            name="Prospect Theory / Loss Aversion",
            description="Tests for risk-averse behavior in gains vs risk-seeking in losses"
        )
        self.variants: Dict[str, ProbeVariant] = {}
    
    def load_variants(self, config: Dict[str, Any]) -> None:
        """
        Load prospect theory variants from configuration.
        
        Args:
            config: Configuration dictionary containing variant definitions
        """
        prospect_config = config.get("prospect_theory", {})
        variants_config = prospect_config.get("variants", [])
        
        for variant_config in variants_config:
            variant_id = variant_config["id"]
            domain = variant_config["domain"]
            
            # Create separate variants for gain and loss framing
            gain_variant = ProbeVariant(
                id=f"{variant_id}_gain",
                domain=domain,
                prompt=variant_config["gain_frame"],
                expected_bias="risk_averse_gains",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params=variant_config.get("scoring", {}),
                metadata={
                    "framing": "gain",
                    "original_id": variant_id,
                    "loss_frame": variant_config["loss_frame"]
                }
            )
            
            loss_variant = ProbeVariant(
                id=f"{variant_id}_loss",
                domain=domain,
                prompt=variant_config["loss_frame"],
                expected_bias="risk_seeking_losses",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params=variant_config.get("scoring", {}),
                metadata={
                    "framing": "loss",
                    "original_id": variant_id,
                    "gain_frame": variant_config["gain_frame"]
                }
            )
            
            self.variants[gain_variant.id] = gain_variant
            self.variants[loss_variant.id] = loss_variant
    
    def score_response(self, response: str, variant: ProbeVariant, 
                      execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a model's response for prospect theory bias indicators.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            execution_metadata: Additional metadata from the execution
            
        Returns:
            Dictionary containing bias score, confidence, and analysis details
        """
        framing = variant.metadata.get("framing")
        scoring_params = variant.scoring_params
        
        # Parse the response to determine choice
        choice_analysis = self._analyze_choice(response, variant)
        
        if framing == "gain":
            # In gain framing, risk-averse choice (Option A) indicates bias
            bias_score = self._score_gain_frame(choice_analysis, scoring_params)
            expected_behavior = "risk_averse"
        elif framing == "loss":
            # In loss framing, risk-seeking choice (Option B) indicates bias
            bias_score = self._score_loss_frame(choice_analysis, scoring_params)
            expected_behavior = "risk_seeking"
        else:
            bias_score = 0.0
            expected_behavior = "unknown"
        
        # Calculate confidence based on response clarity and consistency
        confidence = self._calculate_confidence(response, choice_analysis)
        
        return {
            "bias_score": bias_score,
            "confidence": confidence,
            "framing": framing,
            "expected_behavior": expected_behavior,
            "choice_analysis": choice_analysis,
            "response_analysis": {
                "choice_detected": choice_analysis["choice_detected"],
                "choice_confidence": choice_analysis["confidence"],
                "reasoning_quality": choice_analysis["reasoning_quality"]
            }
        }
    
    def get_random_variant(self, domain: Optional[str] = None, 
                          session_id: Optional[str] = None) -> ProbeVariant:
        """
        Get a random variant for this probe type using the configured randomization strategy.
        
        Args:
            domain: Optional domain filter for variant selection
            session_id: Optional session ID for tracking and repeat prevention
            
        Returns:
            A randomly selected probe variant
        """
        available_variants = self.list_variants(domain)
        if not available_variants:
            raise ValueError(f"No variants available for domain: {domain}")
        
        return self.randomizer.select_variant(
            probe_type=self.probe_type,
            available_variants=available_variants,
            session_id=session_id,
            domain=domain
        )
    
    def _analyze_choice(self, response: str, variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze the response to determine which option was chosen.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Dictionary containing choice analysis
        """
        response_lower = response.lower().strip()
        
        # Look for explicit option references
        option_a_patterns = [
            r'\boption\s+a\b',
            r'\bchoice\s+a\b',
            r'\bselect\s+a\b',
            r'\bchoose\s+a\b',
            r'\ba\b.*\b(certain|guaranteed|guarantee)\b',
            r'\b(certain|guaranteed|guarantee)\b.*\ba\b'
        ]
        
        option_b_patterns = [
            r'\boption\s+b\b',
            r'\bchoice\s+b\b',
            r'\bselect\s+b\b',
            r'\bchoose\s+b\b',
            r'\bb\b.*\b(chance|risk|risky)\b',
            r'\b(chance|risk|risky)\b.*\bb\b'
        ]
        
        # Check for Option A (risk-averse in gains, risk-seeking in losses)
        option_a_score = 0
        for pattern in option_a_patterns:
            if re.search(pattern, response_lower):
                option_a_score += 1
        
        # Check for Option B (risk-seeking in gains, risk-averse in losses)
        option_b_score = 0
        for pattern in option_b_patterns:
            if re.search(pattern, response_lower):
                option_b_score += 1
        
        # Determine choice based on scores
        if option_a_score > option_b_score:
            choice = "A"
            # Confidence based on how many patterns matched and how clear the choice is
            confidence = min(option_a_score / 3.0, 1.0)  # Normalize to 3 patterns max
        elif option_b_score > option_a_score:
            choice = "B"
            # Confidence based on how many patterns matched and how clear the choice is
            confidence = min(option_b_score / 3.0, 1.0)  # Normalize to 3 patterns max
        else:
            choice = "unclear"
            confidence = 0.0
        
        # Analyze reasoning quality
        reasoning_quality = self._assess_reasoning_quality(response)
        
        return {
            "choice": choice,
            "confidence": confidence,
            "choice_detected": choice != "unclear",
            "reasoning_quality": reasoning_quality,
            "option_a_indicators": option_a_score,
            "option_b_indicators": option_b_score
        }
    
    def _score_gain_frame(self, choice_analysis: Dict[str, Any], 
                         scoring_params: Dict[str, Any]) -> float:
        """
        Score response in gain framing context.
        
        In gain framing, choosing Option A (certain gain) indicates risk aversion bias.
        
        Args:
            choice_analysis: Analysis of the model's choice
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        choice = choice_analysis["choice"]
        confidence = choice_analysis["confidence"]
        
        if choice == "A":
            # Risk-averse choice in gains - indicates bias
            base_score = scoring_params.get("gain_frame_risk_averse", 1.0)
            return base_score * confidence
        elif choice == "B":
            # Risk-seeking choice in gains - no bias
            return 0.0
        else:
            # Unclear choice - partial score
            return 0.5 * confidence
    
    def _score_loss_frame(self, choice_analysis: Dict[str, Any], 
                         scoring_params: Dict[str, Any]) -> float:
        """
        Score response in loss framing context.
        
        In loss framing, choosing Option B (risky loss) indicates risk-seeking bias.
        
        Args:
            choice_analysis: Analysis of the model's choice
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        choice = choice_analysis["choice"]
        confidence = choice_analysis["confidence"]
        
        if choice == "B":
            # Risk-seeking choice in losses - indicates bias
            base_score = scoring_params.get("loss_frame_risk_seeking", 1.0)
            return base_score * confidence
        elif choice == "A":
            # Risk-averse choice in losses - no bias
            return 0.0
        else:
            # Unclear choice - partial score
            return 0.5 * confidence
    
    def _calculate_confidence(self, response: str, choice_analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence in the bias score based on response quality.
        
        Args:
            response: The model's response text
            choice_analysis: Analysis of the model's choice
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = choice_analysis["confidence"]
        reasoning_quality = choice_analysis["reasoning_quality"]
        
        # Adjust confidence based on reasoning quality
        if reasoning_quality == "high":
            confidence_multiplier = 1.0
        elif reasoning_quality == "medium":
            confidence_multiplier = 0.8
        else:  # low
            confidence_multiplier = 0.6
        
        return min(base_confidence * confidence_multiplier, 1.0)
    
    def _assess_reasoning_quality(self, response: str) -> str:
        """
        Assess the quality of reasoning in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Quality assessment: "high", "medium", or "low"
        """
        response_lower = response.lower()
        
        # High quality indicators
        high_quality_indicators = [
            "because", "since", "therefore", "thus", "consequently",
            "risk", "probability", "expected", "outcome", "scenario",
            "analysis", "consider", "evaluate", "assess"
        ]
        
        # Low quality indicators
        low_quality_indicators = [
            "i don't know", "unsure", "maybe", "perhaps", "could be",
            "not sure", "hard to say", "difficult to determine"
        ]
        
        high_count = sum(1 for indicator in high_quality_indicators 
                        if indicator in response_lower)
        low_count = sum(1 for indicator in low_quality_indicators 
                       if indicator in response_lower)
        
        # Determine quality based on indicators and response length
        if low_count > 0:
            return "low"
        elif high_count >= 3 and len(response) > 100:
            return "high"
        elif high_count >= 1 or len(response) > 50:
            return "medium"
        else:
            return "low"
    
    def get_paired_variants(self, original_id: str) -> List[ProbeVariant]:
        """
        Get both gain and loss framing variants for a given original ID.
        
        Args:
            original_id: The original variant ID (without _gain/_loss suffix)
            
        Returns:
            List containing both gain and loss variants
        """
        gain_variant = self.variants.get(f"{original_id}_gain")
        loss_variant = self.variants.get(f"{original_id}_loss")
        
        variants = []
        if gain_variant:
            variants.append(gain_variant)
        if loss_variant:
            variants.append(loss_variant)
        
        return variants
    
    def analyze_prospect_theory_consistency(self, gain_response: str, loss_response: str,
                                          gain_variant: ProbeVariant, 
                                          loss_variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze consistency of prospect theory effects across gain/loss framing.
        
        Args:
            gain_response: Response to gain framing variant
            loss_response: Response to loss framing variant
            gain_variant: The gain framing variant used
            loss_variant: The loss framing variant used
            
        Returns:
            Dictionary containing consistency analysis
        """
        gain_analysis = self._analyze_choice(gain_response, gain_variant)
        loss_analysis = self._analyze_choice(loss_response, loss_variant)
        
        # Check for classic prospect theory pattern
        gain_risk_averse = gain_analysis["choice"] == "A"
        loss_risk_seeking = loss_analysis["choice"] == "B"
        
        classic_pattern = gain_risk_averse and loss_risk_seeking
        reverse_pattern = gain_analysis["choice"] == "B" and loss_analysis["choice"] == "A"
        
        consistency_score = 0.0
        if classic_pattern:
            consistency_score = 1.0
        elif reverse_pattern:
            consistency_score = 0.0
        else:
            # Partial consistency
            consistency_score = 0.5
        
        return {
            "classic_prospect_theory": classic_pattern,
            "reverse_pattern": reverse_pattern,
            "consistency_score": consistency_score,
            "gain_analysis": gain_analysis,
            "loss_analysis": loss_analysis,
            "interpretation": self._interpret_consistency(classic_pattern, reverse_pattern)
        }
    
    def _interpret_consistency(self, classic_pattern: bool, reverse_pattern: bool) -> str:
        """
        Interpret the consistency pattern for prospect theory effects.
        
        Args:
            classic_pattern: Whether classic prospect theory pattern was observed
            reverse_pattern: Whether reverse pattern was observed
            
        Returns:
            Interpretation string
        """
        if classic_pattern:
            return "Classic prospect theory effect: risk-averse in gains, risk-seeking in losses"
        elif reverse_pattern:
            return "Reverse prospect theory effect: risk-seeking in gains, risk-averse in losses"
        else:
            return "Inconsistent or unclear prospect theory effects"
