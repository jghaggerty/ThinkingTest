"""
Anchoring bias probe implementation.

This module implements probes to test for anchoring bias, where initial numeric
values (anchors) influence subsequent estimates even when they are irrelevant.
"""

import re
import math
from typing import Dict, Any, List, Optional, Tuple
from .base import BaseProbe
from .types import ProbeType, ResponseFormat, ProbeVariant
from .types import ProbeRequest


class AnchoringProbe(BaseProbe):
    """
    Anchoring bias probe.
    
    Tests for the influence of initial numeric values (anchors) on subsequent
    estimates. The bias occurs when people's estimates are pulled toward the
    anchor value, even when the anchor is irrelevant or random.
    
    This probe uses high/low anchor variants to detect this bias pattern.
    """
    
    def __init__(self):
        super().__init__(
            probe_type=ProbeType.ANCHORING,
            name="Anchoring Bias",
            description="Tests for influence of initial numeric values on subsequent estimates"
        )
        self.variants: Dict[str, ProbeVariant] = {}
    
    def load_variants(self, config: Dict[str, Any]) -> None:
        """
        Load anchoring variants from configuration.
        
        Args:
            config: Configuration dictionary containing variant definitions
        """
        anchoring_config = config.get("probes", {}).get("anchoring", {})
        variants_config = anchoring_config.get("variants", [])
        
        for variant_config in variants_config:
            variant_id = variant_config["id"]
            domain = variant_config["domain"]
            correct_answer = variant_config.get("correct_answer", 0)
            
            # Create separate variants for high and low anchors
            low_anchor_variant = ProbeVariant(
                id=f"{variant_id}_low_anchor",
                domain=domain,
                prompt=variant_config["low_anchor"],
                expected_bias="low_anchor_bias",
                response_format=ResponseFormat.NUMERIC,
                scoring_params={
                    "correct_answer": correct_answer,
                    "anchor_type": "low",
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "anchor_type": "low",
                    "original_id": variant_id,
                    "high_anchor_prompt": variant_config["high_anchor"],
                    "correct_answer": correct_answer
                }
            )
            
            high_anchor_variant = ProbeVariant(
                id=f"{variant_id}_high_anchor",
                domain=domain,
                prompt=variant_config["high_anchor"],
                expected_bias="high_anchor_bias",
                response_format=ResponseFormat.NUMERIC,
                scoring_params={
                    "correct_answer": correct_answer,
                    "anchor_type": "high",
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "anchor_type": "high",
                    "original_id": variant_id,
                    "low_anchor_prompt": variant_config["low_anchor"],
                    "correct_answer": correct_answer
                }
            )
            
            self.variants[low_anchor_variant.id] = low_anchor_variant
            self.variants[high_anchor_variant.id] = high_anchor_variant
    
    def score_response(self, response: str, variant: ProbeVariant, 
                      execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a model's response for anchoring bias indicators.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            execution_metadata: Additional metadata from the execution
            
        Returns:
            Dictionary containing bias score, confidence, and analysis details
        """
        anchor_type = variant.metadata.get("anchor_type")
        correct_answer = variant.metadata.get("correct_answer", 0)
        scoring_params = variant.scoring_params
        
        # Extract numeric estimate from response
        estimate_analysis = self._extract_estimate(response, variant)
        
        if estimate_analysis["estimate"] is None:
            # No numeric estimate found
            return {
                "bias_score": 0.0,
                "confidence": 0.0,
                "anchor_type": anchor_type,
                "estimate_analysis": estimate_analysis,
                "error": "No numeric estimate found in response"
            }
        
        estimate = estimate_analysis["estimate"]
        
        # Calculate anchoring bias score
        if anchor_type == "low":
            bias_score = self._score_low_anchor_bias(
                estimate, correct_answer, scoring_params
            )
        elif anchor_type == "high":
            bias_score = self._score_high_anchor_bias(
                estimate, correct_answer, scoring_params
            )
        else:
            bias_score = 0.0
        
        # Calculate confidence based on response quality
        confidence = self._calculate_confidence(response, estimate_analysis)
        
        return {
            "bias_score": bias_score,
            "confidence": confidence,
            "anchor_type": anchor_type,
            "estimate": estimate,
            "correct_answer": correct_answer,
            "estimate_analysis": estimate_analysis,
            "bias_analysis": {
                "anchor_influence": self._calculate_anchor_influence(
                    estimate, correct_answer, anchor_type
                ),
                "distance_from_correct": abs(estimate - correct_answer),
                "relative_error": abs(estimate - correct_answer) / max(correct_answer, 1)
            }
        }
    
    def _extract_estimate(self, response: str, variant: ProbeVariant) -> Dict[str, Any]:
        """
        Extract numeric estimate from the response text.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Dictionary containing estimate analysis
        """
        # Use the base class method for numeric extraction
        estimate = self.extract_numeric_value(response, variant)
        
        if estimate is None:
            # Try to find numbers in the response using regex
            numbers = re.findall(r'\b\d+(?:\.\d+)?\b', response)
            if numbers:
                # Take the first reasonable number found
                try:
                    estimate = float(numbers[0])
                except ValueError:
                    estimate = None
        
        # Analyze the extraction quality
        extraction_quality = "high" if estimate is not None else "low"
        
        # Check if the response contains reasoning
        reasoning_indicators = [
            "because", "since", "therefore", "based on", "considering",
            "estimate", "approximately", "around", "about", "roughly"
        ]
        
        has_reasoning = any(indicator in response.lower() for indicator in reasoning_indicators)
        
        return {
            "estimate": estimate,
            "extraction_quality": extraction_quality,
            "has_reasoning": has_reasoning,
            "response_length": len(response),
            "contains_numbers": bool(re.search(r'\d+', response))
        }
    
    def _score_low_anchor_bias(self, estimate: float, correct_answer: float, 
                              scoring_params: Dict[str, Any]) -> float:
        """
        Score response for low anchor bias.
        
        Low anchor bias occurs when estimates are pulled downward toward the low anchor.
        
        Args:
            estimate: The model's estimate
            correct_answer: The correct answer
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        threshold = scoring_params.get("anchor_influence_threshold", 0.2)
        base_score = scoring_params.get("low_anchor_bias", 1.0)
        
        # Calculate how much the estimate is pulled toward the low anchor
        # If estimate is significantly below correct answer, it might indicate low anchor bias
        relative_error = (correct_answer - estimate) / max(correct_answer, 1)
        
        # Also check if the estimate is closer to a typical low anchor than to the correct answer
        # This is a heuristic since we don't have the exact anchor value in this context
        if relative_error > threshold:
            # Strong low anchor bias - estimate is much lower than correct
            return base_score
        elif relative_error > threshold / 2:
            # Moderate low anchor bias
            return base_score * 0.5
        else:
            # No significant low anchor bias
            return 0.0
    
    def _score_high_anchor_bias(self, estimate: float, correct_answer: float, 
                               scoring_params: Dict[str, Any]) -> float:
        """
        Score response for high anchor bias.
        
        High anchor bias occurs when estimates are pulled upward toward the high anchor.
        
        Args:
            estimate: The model's estimate
            correct_answer: The correct answer
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        threshold = scoring_params.get("anchor_influence_threshold", 0.2)
        base_score = scoring_params.get("high_anchor_bias", 1.0)
        
        # Calculate how much the estimate is pulled toward the high anchor
        relative_error = (estimate - correct_answer) / max(correct_answer, 1)
        
        if relative_error > threshold:
            # Strong high anchor bias
            return base_score
        elif relative_error > threshold / 2:
            # Moderate high anchor bias
            return base_score * 0.5
        else:
            # No significant high anchor bias
            return 0.0
    
    def _calculate_anchor_influence(self, estimate: float, correct_answer: float, 
                                  anchor_type: str) -> float:
        """
        Calculate the degree of anchor influence on the estimate.
        
        Args:
            estimate: The model's estimate
            correct_answer: The correct answer
            anchor_type: Type of anchor ("low" or "high")
            
        Returns:
            Anchor influence score (0.0 to 1.0)
        """
        if anchor_type == "low":
            # For low anchor, influence is higher when estimate is below correct answer
            if estimate < correct_answer:
                return min((correct_answer - estimate) / correct_answer, 1.0)
            else:
                return 0.0
        elif anchor_type == "high":
            # For high anchor, influence is higher when estimate is above correct answer
            if estimate > correct_answer:
                return min((estimate - correct_answer) / correct_answer, 1.0)
            else:
                return 0.0
        else:
            return 0.0
    
    def _calculate_confidence(self, response: str, estimate_analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence in the bias score based on response quality.
        
        Args:
            response: The model's response text
            estimate_analysis: Analysis of the estimate extraction
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.5  # Start with moderate confidence
        
        # Increase confidence if estimate was successfully extracted
        if estimate_analysis["extraction_quality"] == "high":
            base_confidence += 0.3
        
        # Increase confidence if response contains reasoning
        if estimate_analysis["has_reasoning"]:
            base_confidence += 0.2
        
        # Adjust based on response length (longer responses often more thoughtful)
        if estimate_analysis["response_length"] > 100:
            base_confidence += 0.1
        elif estimate_analysis["response_length"] < 20:
            base_confidence -= 0.2
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def get_paired_variants(self, original_id: str) -> List[ProbeVariant]:
        """
        Get both high and low anchor variants for a given original ID.
        
        Args:
            original_id: The original variant ID (without _low_anchor/_high_anchor suffix)
            
        Returns:
            List containing both high and low anchor variants
        """
        low_variant = self.variants.get(f"{original_id}_low_anchor")
        high_variant = self.variants.get(f"{original_id}_high_anchor")
        
        variants = []
        if low_variant:
            variants.append(low_variant)
        if high_variant:
            variants.append(high_variant)
        
        return variants
    
    def analyze_anchoring_consistency(self, low_response: str, high_response: str,
                                    low_variant: ProbeVariant, 
                                    high_variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze consistency of anchoring effects across high/low anchor conditions.
        
        Args:
            low_response: Response to low anchor variant
            high_response: Response to high anchor variant
            low_variant: The low anchor variant used
            high_variant: The high anchor variant used
            
        Returns:
            Dictionary containing consistency analysis
        """
        low_analysis = self._extract_estimate(low_response, low_variant)
        high_analysis = self._extract_estimate(high_response, high_variant)
        
        if low_analysis["estimate"] is None or high_analysis["estimate"] is None:
            return {
                "anchoring_effect": False,
                "consistency_score": 0.0,
                "error": "Could not extract estimates from one or both responses"
            }
        
        low_estimate = low_analysis["estimate"]
        high_estimate = high_analysis["estimate"]
        correct_answer = low_variant.metadata.get("correct_answer", 0)
        
        # Check for classic anchoring pattern (high estimate > low estimate)
        classic_anchoring = high_estimate > low_estimate
        
        # Calculate anchoring effect size
        if correct_answer > 0:
            low_error = abs(low_estimate - correct_answer) / correct_answer
            high_error = abs(high_estimate - correct_answer) / correct_answer
            effect_size = abs(high_estimate - low_estimate) / correct_answer
        else:
            effect_size = abs(high_estimate - low_estimate)
        
        # Determine consistency score
        if classic_anchoring and effect_size > 0.1:  # 10% difference threshold
            consistency_score = 1.0
        elif classic_anchoring:
            consistency_score = 0.5
        else:
            consistency_score = 0.0
        
        return {
            "anchoring_effect": classic_anchoring,
            "consistency_score": consistency_score,
            "effect_size": effect_size,
            "low_estimate": low_estimate,
            "high_estimate": high_estimate,
            "correct_answer": correct_answer,
            "low_analysis": low_analysis,
            "high_analysis": high_analysis,
            "interpretation": self._interpret_anchoring_consistency(
                classic_anchoring, effect_size
            )
        }
    
    def _interpret_anchoring_consistency(self, classic_anchoring: bool, 
                                       effect_size: float) -> str:
        """
        Interpret the anchoring consistency pattern.
        
        Args:
            classic_anchoring: Whether classic anchoring pattern was observed
            effect_size: Size of the anchoring effect
            
        Returns:
            Interpretation string
        """
        if classic_anchoring and effect_size > 0.2:
            return "Strong anchoring effect: estimates significantly influenced by anchor values"
        elif classic_anchoring and effect_size > 0.1:
            return "Moderate anchoring effect: estimates moderately influenced by anchor values"
        elif classic_anchoring:
            return "Weak anchoring effect: estimates slightly influenced by anchor values"
        else:
            return "No clear anchoring effect: estimates not consistently influenced by anchor values"
    
    def get_anchor_values(self, original_id: str) -> Dict[str, float]:
        """
        Extract anchor values from the prompts for a given variant.
        
        Args:
            original_id: The original variant ID
            
        Returns:
            Dictionary containing low and high anchor values
        """
        low_variant = self.variants.get(f"{original_id}_low_anchor")
        high_variant = self.variants.get(f"{original_id}_high_anchor")
        
        anchor_values = {}
        
        if low_variant:
            # Extract the first significant number from low anchor prompt
            # Look for numbers that are likely to be the anchor value
            numbers = re.findall(r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\b', low_variant.prompt)
            if numbers:
                try:
                    # Take the first number that's likely to be the anchor
                    anchor_values["low"] = float(numbers[0].replace(',', ''))
                except ValueError:
                    pass
        
        if high_variant:
            # Extract the first significant number from high anchor prompt
            numbers = re.findall(r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\b', high_variant.prompt)
            if numbers:
                try:
                    # Take the first number that's likely to be the anchor
                    anchor_values["high"] = float(numbers[0].replace(',', ''))
                except ValueError:
                    pass
        
        return anchor_values
