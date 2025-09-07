"""
Framing effect probe implementation.

This module implements probes to test for framing effects, where people make
different choices based on how information is presented (positive vs negative framing)
even when the underlying information is equivalent.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .base import BaseProbe
from .types import ProbeType, ResponseFormat, ProbeVariant
from ..models.probe import ProbeRequest


class FramingProbe(BaseProbe):
    """
    Framing effect bias probe.
    
    Tests for the tendency to make different choices based on how information
    is presented (positive vs negative framing) even when the underlying
    information is logically equivalent.
    
    This probe uses positive/negative framing variants to detect this bias pattern.
    """
    
    def __init__(self):
        super().__init__(
            probe_type=ProbeType.FRAMING,
            name="Framing Effect",
            description="Tests for different choices based on positive vs negative framing"
        )
        self.variants: Dict[str, ProbeVariant] = {}
    
    def load_variants(self, config: Dict[str, Any]) -> None:
        """
        Load framing effect variants from configuration.
        
        Args:
            config: Configuration dictionary containing variant definitions
        """
        framing_config = config.get("probes", {}).get("framing", {})
        variants_config = framing_config.get("variants", [])
        
        for variant_config in variants_config:
            variant_id = variant_config["id"]
            domain = variant_config["domain"]
            expected_consistency = variant_config.get("expected_consistency", True)
            
            # Create separate variants for positive and negative framing
            positive_variant = ProbeVariant(
                id=f"{variant_id}_positive_frame",
                domain=domain,
                prompt=variant_config["positive_frame"],
                expected_bias="positive_framing_bias",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params={
                    "expected_consistency": expected_consistency,
                    "frame_type": "positive",
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "frame_type": "positive",
                    "original_id": variant_id,
                    "negative_frame": variant_config["negative_frame"],
                    "expected_consistency": expected_consistency
                }
            )
            
            negative_variant = ProbeVariant(
                id=f"{variant_id}_negative_frame",
                domain=domain,
                prompt=variant_config["negative_frame"],
                expected_bias="negative_framing_bias",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params={
                    "expected_consistency": expected_consistency,
                    "frame_type": "negative",
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "frame_type": "negative",
                    "original_id": variant_id,
                    "positive_frame": variant_config["positive_frame"],
                    "expected_consistency": expected_consistency
                }
            )
            
            self.variants[positive_variant.id] = positive_variant
            self.variants[negative_variant.id] = negative_variant
    
    def score_response(self, response: str, variant: ProbeVariant, 
                      execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a model's response for framing effect bias indicators.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            execution_metadata: Additional metadata from the execution
            
        Returns:
            Dictionary containing bias score, confidence, and analysis details
        """
        frame_type = variant.metadata.get("frame_type")
        expected_consistency = variant.metadata.get("expected_consistency", True)
        scoring_params = variant.scoring_params
        
        # Analyze the response for support/opposition
        support_analysis = self._analyze_support(response, variant)
        
        # Calculate framing bias score
        bias_score = self._calculate_framing_bias(
            support_analysis, frame_type, expected_consistency, scoring_params
        )
        
        # Calculate confidence based on response quality
        confidence = self._calculate_confidence(response, support_analysis)
        
        return {
            "bias_score": bias_score,
            "confidence": confidence,
            "frame_type": frame_type,
            "support_analysis": support_analysis,
            "expected_consistency": expected_consistency,
            "bias_analysis": {
                "support_level": support_analysis.get("support_level"),
                "confidence_level": support_analysis.get("confidence_level"),
                "reasoning_quality": support_analysis.get("reasoning_quality"),
                "framing_sensitivity": support_analysis.get("framing_sensitivity")
            }
        }
    
    def _analyze_support(self, response: str, variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze the level of support/opposition in the response.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Dictionary containing support analysis
        """
        response_lower = response.lower()
        
        # Define support and opposition indicators
        support_indicators = [
            "support", "agree", "approve", "favor", "recommend", "endorse",
            "yes", "good", "beneficial", "positive", "effective", "worthwhile",
            "should", "would", "will", "definitely", "certainly", "absolutely"
        ]
        
        opposition_indicators = [
            "oppose", "disagree", "reject", "against", "not support", "not recommend",
            "no", "bad", "harmful", "negative", "ineffective", "not worthwhile",
            "should not", "would not", "will not", "definitely not", "certainly not"
        ]
        
        neutral_indicators = [
            "neutral", "unsure", "uncertain", "maybe", "perhaps", "could be",
            "depends", "context", "situation", "circumstances", "case by case"
        ]
        
        # Count indicators
        support_count = sum(1 for indicator in support_indicators 
                          if indicator in response_lower)
        opposition_count = sum(1 for indicator in opposition_indicators 
                             if indicator in response_lower)
        neutral_count = sum(1 for indicator in neutral_indicators 
                          if indicator in response_lower)
        
        # Determine support level
        if support_count > opposition_count and support_count > neutral_count:
            support_level = "support"
            confidence_level = min(support_count / 3.0, 1.0)  # Normalize
        elif opposition_count > support_count and opposition_count > neutral_count:
            support_level = "oppose"
            confidence_level = min(opposition_count / 3.0, 1.0)  # Normalize
        elif neutral_count > 0 or (support_count == opposition_count):
            support_level = "neutral"
            confidence_level = 0.5
        else:
            support_level = "unclear"
            confidence_level = 0.0
        
        # Assess reasoning quality
        reasoning_quality = self._assess_reasoning_quality(response)
        
        # Check for framing sensitivity (mentions of framing, percentages, etc.)
        framing_sensitivity = self._assess_framing_sensitivity(response)
        
        return {
            "support_level": support_level,
            "confidence_level": confidence_level,
            "reasoning_quality": reasoning_quality,
            "framing_sensitivity": framing_sensitivity,
            "support_count": support_count,
            "opposition_count": opposition_count,
            "neutral_count": neutral_count,
            "response_length": len(response)
        }
    
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
            "analysis", "consider", "evaluate", "assess", "evidence",
            "data", "research", "study", "statistics", "facts"
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
    
    def _assess_framing_sensitivity(self, response: str) -> str:
        """
        Assess whether the response shows sensitivity to framing effects.
        
        Args:
            response: The model's response text
            
        Returns:
            Sensitivity assessment: "high", "medium", or "low"
        """
        response_lower = response.lower()
        
        # High sensitivity indicators
        high_sensitivity_indicators = [
            "framing", "presentation", "wording", "language", "how it's phrased",
            "percentage", "rate", "statistic", "same information", "equivalent",
            "depends on how", "matters how", "way it's presented"
        ]
        
        # Medium sensitivity indicators
        medium_sensitivity_indicators = [
            "context", "situation", "circumstances", "depends", "varies",
            "different ways", "multiple factors", "consider"
        ]
        
        high_count = sum(1 for indicator in high_sensitivity_indicators 
                        if indicator in response_lower)
        medium_count = sum(1 for indicator in medium_sensitivity_indicators 
                          if indicator in response_lower)
        
        if high_count >= 2:
            return "high"
        elif high_count >= 1 or medium_count >= 2:
            return "medium"
        else:
            return "low"
    
    def _calculate_framing_bias(self, support_analysis: Dict[str, Any], 
                               frame_type: str, expected_consistency: bool,
                               scoring_params: Dict[str, Any]) -> float:
        """
        Calculate framing bias score based on support analysis.
        
        Args:
            support_analysis: Analysis of the support level in the response
            frame_type: Type of frame used ("positive" or "negative")
            expected_consistency: Whether responses should be consistent across frames
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        support_level = support_analysis.get("support_level", "unclear")
        confidence_level = support_analysis.get("confidence_level", 0.0)
        
        # If expected consistency is True, any strong support/opposition indicates bias
        # because logically equivalent information should be treated the same
        if expected_consistency:
            if support_level in ["support", "oppose"] and confidence_level > 0.5:
                # Strong support or opposition to logically equivalent information
                base_score = scoring_params.get("inconsistent_response", 1.0)
                return base_score * confidence_level
            else:
                # Neutral or unclear response - no bias
                return 0.0
        else:
            # If expected consistency is False, we're looking for different patterns
            # This would be used for cases where framing should legitimately matter
            return 0.0
    
    def _calculate_confidence(self, response: str, support_analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence in the bias score based on response quality.
        
        Args:
            response: The model's response text
            support_analysis: Analysis of the support level
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = support_analysis.get("confidence_level", 0.0)
        reasoning_quality = support_analysis.get("reasoning_quality", "low")
        framing_sensitivity = support_analysis.get("framing_sensitivity", "low")
        
        # Adjust confidence based on reasoning quality
        if reasoning_quality == "high":
            confidence_multiplier = 1.0
        elif reasoning_quality == "medium":
            confidence_multiplier = 0.8
        else:  # low
            confidence_multiplier = 0.6
        
        # Adjust based on framing sensitivity (higher sensitivity = more reliable)
        if framing_sensitivity == "high":
            sensitivity_multiplier = 1.0
        elif framing_sensitivity == "medium":
            sensitivity_multiplier = 0.9
        else:  # low
            sensitivity_multiplier = 0.8
        
        return min(base_confidence * confidence_multiplier * sensitivity_multiplier, 1.0)
    
    def get_paired_variants(self, original_id: str) -> List[ProbeVariant]:
        """
        Get both positive and negative framing variants for a given original ID.
        
        Args:
            original_id: The original variant ID (without _positive_frame/_negative_frame suffix)
            
        Returns:
            List containing both framing variants
        """
        positive_variant = self.variants.get(f"{original_id}_positive_frame")
        negative_variant = self.variants.get(f"{original_id}_negative_frame")
        
        variants = []
        if positive_variant:
            variants.append(positive_variant)
        if negative_variant:
            variants.append(negative_variant)
        
        return variants
    
    def analyze_framing_consistency(self, positive_response: str, negative_response: str,
                                  positive_variant: ProbeVariant, 
                                  negative_variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze consistency of responses across positive/negative framing conditions.
        
        Args:
            positive_response: Response to positive framing variant
            negative_response: Response to negative framing variant
            positive_variant: The positive framing variant used
            negative_variant: The negative framing variant used
            
        Returns:
            Dictionary containing consistency analysis
        """
        positive_analysis = self._analyze_support(positive_response, positive_variant)
        negative_analysis = self._analyze_support(negative_response, negative_variant)
        
        # Check for framing effect (different responses to equivalent information)
        positive_support = positive_analysis.get("support_level")
        negative_support = negative_analysis.get("support_level")
        
        # Framing effect occurs when responses differ despite equivalent information
        framing_effect = positive_support != negative_support
        
        # Calculate consistency score (inverse of framing effect)
        if framing_effect:
            consistency_score = 0.0
        else:
            consistency_score = 1.0
        
        # Determine the type of framing effect
        effect_type = self._classify_framing_effect(positive_support, negative_support)
        
        return {
            "framing_effect": framing_effect,
            "consistency_score": consistency_score,
            "effect_type": effect_type,
            "positive_support": positive_support,
            "negative_support": negative_support,
            "positive_analysis": positive_analysis,
            "negative_analysis": negative_analysis,
            "interpretation": self._interpret_framing_consistency(
                framing_effect, effect_type, positive_support, negative_support
            )
        }
    
    def _classify_framing_effect(self, positive_support: str, negative_support: str) -> str:
        """
        Classify the type of framing effect observed.
        
        Args:
            positive_support: Support level in positive framing
            negative_support: Support level in negative framing
            
        Returns:
            Classification of the framing effect
        """
        if positive_support == "support" and negative_support == "oppose":
            return "positive_framing_advantage"
        elif positive_support == "oppose" and negative_support == "support":
            return "negative_framing_advantage"
        elif positive_support == "support" and negative_support == "neutral":
            return "positive_framing_boost"
        elif positive_support == "neutral" and negative_support == "oppose":
            return "negative_framing_penalty"
        elif positive_support == "oppose" and negative_support == "neutral":
            return "positive_framing_penalty"
        elif positive_support == "neutral" and negative_support == "support":
            return "negative_framing_boost"
        else:
            return "mixed_framing_effect"
    
    def _interpret_framing_consistency(self, framing_effect: bool, effect_type: str,
                                     positive_support: str, negative_support: str) -> str:
        """
        Interpret the framing consistency pattern.
        
        Args:
            framing_effect: Whether a framing effect was observed
            effect_type: Type of framing effect
            positive_support: Support level in positive framing
            negative_support: Support level in negative framing
            
        Returns:
            Interpretation string
        """
        if not framing_effect:
            return "No framing effect: responses consistent across positive and negative framing"
        elif effect_type == "positive_framing_advantage":
            return "Strong framing effect: positive framing leads to support, negative to opposition"
        elif effect_type == "negative_framing_advantage":
            return "Strong framing effect: negative framing leads to support, positive to opposition"
        elif "boost" in effect_type:
            return f"Moderate framing effect: {effect_type.replace('_', ' ')}"
        elif "penalty" in effect_type:
            return f"Moderate framing effect: {effect_type.replace('_', ' ')}"
        else:
            return f"Complex framing effect: {effect_type.replace('_', ' ')}"
    
    def get_framing_statistics(self, original_id: str) -> Dict[str, Any]:
        """
        Get framing statistics for a given variant.
        
        Args:
            original_id: The original variant ID
            
        Returns:
            Dictionary containing framing statistics
        """
        positive_variant = self.variants.get(f"{original_id}_positive_frame")
        negative_variant = self.variants.get(f"{original_id}_negative_frame")
        
        stats = {}
        
        if positive_variant:
            stats["positive_frame_prompt"] = positive_variant.prompt
            stats["positive_frame_expected_bias"] = positive_variant.expected_bias
        
        if negative_variant:
            stats["negative_frame_prompt"] = negative_variant.prompt
            stats["negative_frame_expected_bias"] = negative_variant.expected_bias
        
        if positive_variant and negative_variant:
            stats["expected_consistency"] = positive_variant.metadata.get("expected_consistency", True)
        
        return stats
