"""
Overconfidence bias probe implementation.

This module implements probes to test for overconfidence bias, where people
tend to be more confident in their judgments than is warranted by their
actual accuracy. This bias manifests as confidence intervals that are too
narrow, leading to overestimation of knowledge and underestimation of uncertainty.

The probe tests for overconfidence by asking for confidence interval estimates
and comparing them to actual accuracy or calibration.
"""

import re
import math
from typing import Dict, Any, List, Optional, Tuple
from .base import BaseProbe
from .types import ProbeType, ResponseFormat, ProbeVariant
from ..models.probe import ProbeRequest


class OverconfidenceProbe(BaseProbe):
    """
    Overconfidence bias probe.
    
    Tests for the tendency to be more confident in judgments than is warranted
    by actual accuracy. This bias manifests as confidence intervals that are
    too narrow, leading to overestimation of knowledge and underestimation
    of uncertainty.
    
    This probe uses confidence interval estimation scenarios to test for overconfidence.
    """
    
    def __init__(self):
        super().__init__(
            probe_type=ProbeType.OVERCONFIDENCE,
            name="Overconfidence Bias",
            description="Tests for excessive confidence in judgments relative to actual accuracy"
        )
        self.variants: Dict[str, ProbeVariant] = {}
    
    def load_variants(self, config: Dict[str, Any]) -> None:
        """
        Load overconfidence bias variants from configuration.
        
        Args:
            config: Configuration dictionary containing variant definitions
        """
        overconfidence_config = config.get("probes", {}).get("overconfidence", {})
        variants_config = overconfidence_config.get("variants", [])
        
        for variant_config in variants_config:
            variant_id = variant_config["id"]
            domain = variant_config["domain"]
            correct_answer = variant_config.get("correct_answer", 0.0)
            
            # Create variant for the overconfidence bias scenario
            variant = ProbeVariant(
                id=variant_id,
                domain=domain,
                prompt=variant_config["question"],
                expected_bias="overconfidence",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params={
                    "correct_answer": correct_answer,
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "original_id": variant_id,
                    "correct_answer": correct_answer,
                    "scenario_type": "overconfidence_estimation"
                }
            )
            
            self.variants[variant.id] = variant
    
    def score_response(self, response: str, variant: ProbeVariant, 
                      execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a model's response for overconfidence bias indicators.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            execution_metadata: Additional metadata from the execution
            
        Returns:
            Dictionary containing bias score, confidence, and analysis details
        """
        correct_answer = variant.metadata.get("correct_answer", 0.0)
        scoring_params = variant.scoring_params
        
        # Analyze the confidence interval estimation in the response
        estimation_analysis = self._analyze_confidence_estimation(response, variant)
        
        # Calculate overconfidence bias score
        bias_score = self._calculate_overconfidence_bias(
            estimation_analysis, correct_answer, scoring_params
        )
        
        # Calculate confidence based on response quality
        confidence = self._calculate_confidence(response, estimation_analysis)
        
        return {
            "bias_score": bias_score,
            "confidence": confidence,
            "correct_answer": correct_answer,
            "estimation_analysis": estimation_analysis,
            "bias_analysis": {
                "central_estimate": estimation_analysis.get("central_estimate"),
                "confidence_interval": estimation_analysis.get("confidence_interval"),
                "interval_width": estimation_analysis.get("interval_width"),
                "overconfidence_level": estimation_analysis.get("overconfidence_level"),
                "calibration_quality": estimation_analysis.get("calibration_quality"),
                "uncertainty_acknowledgment": estimation_analysis.get("uncertainty_acknowledgment")
            }
        }
    
    def _analyze_confidence_estimation(self, response: str, variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze the confidence interval estimation in the response.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Dictionary containing confidence estimation analysis
        """
        response_lower = response.lower()
        
        # Extract central estimate
        central_estimate = self._extract_central_estimate(response)
        
        # Extract confidence interval
        confidence_interval = self._extract_confidence_interval(response)
        
        # Calculate interval width
        interval_width = self._calculate_interval_width(confidence_interval, central_estimate)
        
        # Assess overconfidence level
        overconfidence_level = self._assess_overconfidence_level(interval_width, central_estimate)
        
        # Assess calibration quality
        calibration_quality = self._assess_calibration_quality(response)
        
        # Check uncertainty acknowledgment
        uncertainty_acknowledgment = self._check_uncertainty_acknowledgment(response)
        
        return {
            "central_estimate": central_estimate,
            "confidence_interval": confidence_interval,
            "interval_width": interval_width,
            "overconfidence_level": overconfidence_level,
            "calibration_quality": calibration_quality,
            "uncertainty_acknowledgment": uncertainty_acknowledgment,
            "response_length": len(response)
        }
    
    def _extract_central_estimate(self, response: str) -> Optional[float]:
        """
        Extract the central estimate from the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Central estimate value, or None if not found
        """
        # Look for central estimate indicators
        central_patterns = [
            r'central estimate[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'best estimate[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'point estimate[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'my estimate[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'estimate[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'approximately[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'around[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'about[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'is[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'height[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'tall[:\s]*(\d+(?:,\d{3})*(?:\.\d+)?)'
        ]
        
        for pattern in central_patterns:
            matches = re.findall(pattern, response.lower())
            if matches:
                try:
                    # Remove commas and convert to float
                    value_str = matches[0].replace(',', '')
                    return float(value_str)
                except ValueError:
                    continue
        
        # Look for standalone numbers that might be estimates (prioritize larger numbers)
        number_pattern = r'\b(\d+(?:,\d{3})*(?:\.\d+)?)\b'
        numbers = re.findall(number_pattern, response)
        
        if numbers:
            # Convert to float and return the largest reasonable number
            try:
                float_numbers = [float(num.replace(',', '')) for num in numbers]
                # Filter out very small numbers (likely not the main estimate)
                reasonable_numbers = [num for num in float_numbers if num > 100]
                if reasonable_numbers:
                    return max(reasonable_numbers)
                elif float_numbers:
                    return max(float_numbers)
            except ValueError:
                pass
        
        return None
    
    def _extract_confidence_interval(self, response: str) -> Optional[Tuple[float, float]]:
        """
        Extract the confidence interval from the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Tuple of (lower_bound, upper_bound), or None if not found
        """
        # Look for range patterns with comma support
        range_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*to\s*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*-\s*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*through\s*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*and\s*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'between\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*and\s*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'from\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*to\s*(\d+(?:,\d{3})*(?:\.\d+)?)'
        ]
        
        for pattern in range_patterns:
            matches = re.findall(pattern, response.lower())
            if matches:
                try:
                    lower = float(matches[0][0].replace(',', ''))
                    upper = float(matches[0][1].replace(',', ''))
                    if lower < upper:
                        return (lower, upper)
                except (ValueError, IndexError):
                    continue
        
        # Look for confidence interval specific patterns
        ci_patterns = [
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*±\s*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*plus or minus\s*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*plus/minus\s*(\d+(?:,\d{3})*(?:\.\d+)?)',
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*give or take\s*(\d+(?:,\d{3})*(?:\.\d+)?)'
        ]
        
        for pattern in ci_patterns:
            matches = re.findall(pattern, response.lower())
            if matches:
                try:
                    center = float(matches[0][0].replace(',', ''))
                    margin = float(matches[0][1].replace(',', ''))
                    return (center - margin, center + margin)
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _calculate_interval_width(self, confidence_interval: Optional[Tuple[float, float]], 
                                central_estimate: Optional[float]) -> Optional[float]:
        """
        Calculate the width of the confidence interval.
        
        Args:
            confidence_interval: Tuple of (lower_bound, upper_bound)
            central_estimate: The central estimate value
            
        Returns:
            Interval width as a percentage, or None if not calculable
        """
        if confidence_interval:
            lower, upper = confidence_interval
            width = upper - lower
            if central_estimate and central_estimate != 0:
                return (width / abs(central_estimate)) * 100
            else:
                return width
        
        return None
    
    def _assess_overconfidence_level(self, interval_width: Optional[float], 
                                   central_estimate: Optional[float]) -> str:
        """
        Assess the level of overconfidence based on interval width.
        
        Args:
            interval_width: Width of the confidence interval as percentage
            central_estimate: The central estimate value
            
        Returns:
            Overconfidence level: "high", "medium", "low", or "unclear"
        """
        if interval_width is None:
            return "unclear"
        
        # Define thresholds for overconfidence
        if interval_width < 10:
            return "high"  # Very narrow interval - high overconfidence
        elif interval_width < 25:
            return "medium"  # Moderately narrow interval - medium overconfidence
        elif interval_width < 50:
            return "low"  # Reasonable interval - low overconfidence
        else:
            return "low"  # Wide interval - not overconfident
    
    def _assess_calibration_quality(self, response: str) -> str:
        """
        Assess the quality of calibration in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Calibration quality: "high", "medium", or "low"
        """
        response_lower = response.lower()
        
        # High quality indicators
        high_quality_indicators = [
            "confidence interval", "uncertainty", "margin of error", "range",
            "80%", "90%", "95%", "confidence level", "probability",
            "likely", "probable", "possible", "estimate"
        ]
        
        # Medium quality indicators
        medium_quality_indicators = [
            "approximately", "around", "about", "roughly", "estimate",
            "think", "believe", "suggest", "indicate"
        ]
        
        # Low quality indicators
        low_quality_indicators = [
            "exactly", "precisely", "definitely", "certainly", "surely",
            "i know", "i'm sure", "no doubt", "absolutely"
        ]
        
        high_count = sum(1 for indicator in high_quality_indicators 
                        if indicator in response_lower)
        medium_count = sum(1 for indicator in medium_quality_indicators 
                          if indicator in response_lower)
        low_count = sum(1 for indicator in low_quality_indicators 
                       if indicator in response_lower)
        
        # Determine quality
        if low_count > 0:
            return "low"
        elif high_count >= 3:
            return "high"
        elif high_count >= 1 or medium_count >= 2:
            return "medium"
        else:
            return "low"
    
    def _check_uncertainty_acknowledgment(self, response: str) -> bool:
        """
        Check if the response acknowledges uncertainty.
        
        Args:
            response: The model's response text
            
        Returns:
            True if uncertainty is acknowledged, False otherwise
        """
        response_lower = response.lower()
        
        uncertainty_indicators = [
            "uncertainty", "uncertain", "not sure", "don't know", "unclear",
            "difficult to estimate", "hard to say", "challenging", "complex",
            "depends", "varies", "range", "approximately", "around", "about",
            "roughly", "estimate", "likely", "probable", "possible"
        ]
        
        return any(indicator in response_lower for indicator in uncertainty_indicators)
    
    def _calculate_overconfidence_bias(self, estimation_analysis: Dict[str, Any], 
                                    correct_answer: float, scoring_params: Dict[str, Any]) -> float:
        """
        Calculate overconfidence bias score based on estimation analysis.
        
        Args:
            estimation_analysis: Analysis of the confidence estimation
            correct_answer: The correct answer value
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        overconfidence_level = estimation_analysis.get("overconfidence_level", "unclear")
        calibration_quality = estimation_analysis.get("calibration_quality", "low")
        uncertainty_acknowledgment = estimation_analysis.get("uncertainty_acknowledgment", False)
        
        # Base bias score based on overconfidence level
        if overconfidence_level == "high":
            base_score = scoring_params.get("overconfident", 1.0)
        elif overconfidence_level == "medium":
            base_score = scoring_params.get("overconfident", 1.0) * 0.7
        elif overconfidence_level == "low":
            base_score = scoring_params.get("well_calibrated", 0.0)
        else:
            base_score = 0.5  # Unclear case
        
        # Adjust based on calibration quality
        if calibration_quality == "high":
            base_score *= 0.8  # Slightly reduce bias for high calibration quality
        elif calibration_quality == "medium":
            base_score *= 0.9
        # Low quality keeps the base score
        
        # Adjust based on uncertainty acknowledgment
        if uncertainty_acknowledgment:
            base_score *= 0.8  # Reduce bias if uncertainty is acknowledged
        
        return min(max(base_score, 0.0), 1.0)
    
    def _calculate_confidence(self, response: str, estimation_analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence in the bias score based on response quality.
        
        Args:
            response: The model's response text
            estimation_analysis: Analysis of the confidence estimation
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.5
        
        # Adjust based on calibration quality
        calibration_quality = estimation_analysis.get("calibration_quality", "low")
        if calibration_quality == "high":
            base_confidence += 0.3
        elif calibration_quality == "medium":
            base_confidence += 0.2
        else:  # low
            base_confidence += 0.1
        
        # Adjust based on whether estimates were extracted
        if estimation_analysis.get("central_estimate") is not None:
            base_confidence += 0.1
        
        if estimation_analysis.get("confidence_interval") is not None:
            base_confidence += 0.1
        
        # Adjust based on overconfidence level clarity
        overconfidence_level = estimation_analysis.get("overconfidence_level", "unclear")
        if overconfidence_level != "unclear":
            base_confidence += 0.1
        
        # Adjust based on response length
        response_length = estimation_analysis.get("response_length", 0)
        if response_length > 100:
            base_confidence += 0.1
        elif response_length < 50:
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def analyze_overconfidence_patterns(self, responses: List[str], 
                                     variants: List[ProbeVariant]) -> Dict[str, Any]:
        """
        Analyze overconfidence patterns across multiple responses.
        
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
            analysis = self._analyze_confidence_estimation(response, variant)
            analyses.append(analysis)
        
        # Calculate aggregate statistics
        high_overconfidence_count = sum(1 for analysis in analyses 
                                      if analysis.get("overconfidence_level") == "high")
        medium_overconfidence_count = sum(1 for analysis in analyses 
                                        if analysis.get("overconfidence_level") == "medium")
        low_overconfidence_count = sum(1 for analysis in analyses 
                                     if analysis.get("overconfidence_level") == "low")
        
        # Calculate calibration quality distribution
        high_calibration_count = sum(1 for analysis in analyses 
                                   if analysis.get("calibration_quality") == "high")
        medium_calibration_count = sum(1 for analysis in analyses 
                                     if analysis.get("calibration_quality") == "medium")
        low_calibration_count = sum(1 for analysis in analyses 
                                  if analysis.get("calibration_quality") == "low")
        
        # Calculate uncertainty acknowledgment prevalence
        uncertainty_acknowledged_count = sum(1 for analysis in analyses 
                                           if analysis.get("uncertainty_acknowledgment", False))
        
        # Calculate average interval width
        interval_widths = [analysis.get("interval_width") for analysis in analyses 
                          if analysis.get("interval_width") is not None]
        average_interval_width = sum(interval_widths) / len(interval_widths) if interval_widths else None
        
        return {
            "total_responses": len(responses),
            "high_overconfidence_count": high_overconfidence_count,
            "medium_overconfidence_count": medium_overconfidence_count,
            "low_overconfidence_count": low_overconfidence_count,
            "overconfidence_prevalence": (high_overconfidence_count + medium_overconfidence_count) / len(responses),
            "high_calibration_count": high_calibration_count,
            "medium_calibration_count": medium_calibration_count,
            "low_calibration_count": low_calibration_count,
            "uncertainty_acknowledgment_prevalence": uncertainty_acknowledged_count / len(responses),
            "average_interval_width": average_interval_width,
            "individual_analyses": analyses
        }
    
    def get_estimation_analysis(self, variant_id: str) -> Dict[str, Any]:
        """
        Get estimation analysis for a variant.
        
        Args:
            variant_id: The variant identifier
            
        Returns:
            Dictionary containing estimation analysis
        """
        variant = self.variants.get(variant_id)
        if not variant:
            return {}
        
        correct_answer = variant.metadata.get("correct_answer", 0.0)
        
        return {
            "correct_answer": correct_answer,
            "domain": variant.domain,
            "scenario_type": variant.metadata.get("scenario_type"),
            "expected_bias": variant.expected_bias
        }
    
    def extract_estimation_components(self, response: str) -> Dict[str, Any]:
        """
        Extract estimation components from the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Dictionary containing extracted components
        """
        central_estimate = self._extract_central_estimate(response)
        confidence_interval = self._extract_confidence_interval(response)
        interval_width = self._calculate_interval_width(confidence_interval, central_estimate)
        
        return {
            "central_estimate": central_estimate,
            "confidence_interval": confidence_interval,
            "interval_width": interval_width,
            "has_central_estimate": central_estimate is not None,
            "has_confidence_interval": confidence_interval is not None,
            "has_both_components": central_estimate is not None and confidence_interval is not None
        }
