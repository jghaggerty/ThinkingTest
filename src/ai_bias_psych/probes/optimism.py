"""
Optimism bias probe implementation.

This module implements probes to test for optimism bias, where people systematically
underestimate risks or overestimate positive outcomes. This includes unrealistic
optimism about timelines, probabilities, and future events.
"""

import re
import math
from typing import Dict, Any, List, Optional, Tuple
from .base import BaseProbe
from .types import ProbeType, ResponseFormat, ProbeVariant
from ..models.probe import ProbeRequest


class OptimismProbe(BaseProbe):
    """
    Optimism bias probe.
    
    Tests for systematic underestimation of risks or overestimation of positive
    outcomes. This includes unrealistic optimism about timelines, probabilities,
    and future events. The bias occurs when people are overly optimistic about
    their own abilities, timelines, or the likelihood of positive outcomes.
    
    This probe uses timeline and probability estimation variants to detect optimism bias.
    """
    
    def __init__(self):
        super().__init__(
            probe_type=ProbeType.OPTIMISM,
            name="Optimism Bias",
            description="Tests for systematic underestimation of risks or overestimation of positive outcomes"
        )
        self.variants: Dict[str, ProbeVariant] = {}
    
    def load_variants(self, config: Dict[str, Any]) -> None:
        """
        Load optimism bias variants from configuration.
        
        Args:
            config: Configuration dictionary containing variant definitions
        """
        optimism_config = config.get("probes", {}).get("optimism", {})
        variants_config = optimism_config.get("variants", [])
        
        for variant_config in variants_config:
            variant_id = variant_config["id"]
            domain = variant_config["domain"]
            baseline_realistic = variant_config.get("baseline_realistic", 0)
            
            # Create variant for the optimism scenario
            variant = ProbeVariant(
                id=variant_id,
                domain=domain,
                prompt=variant_config["question"],
                expected_bias="optimism_bias",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params={
                    "baseline_realistic": baseline_realistic,
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "original_id": variant_id,
                    "baseline_realistic": baseline_realistic,
                    "scenario_type": "optimism_estimation"
                }
            )
            
            self.variants[variant.id] = variant
    
    def score_response(self, response: str, variant: ProbeVariant, 
                      execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a model's response for optimism bias indicators.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            execution_metadata: Additional metadata from the execution
            
        Returns:
            Dictionary containing bias score, confidence, and analysis details
        """
        baseline_realistic = variant.metadata.get("baseline_realistic", 0)
        scoring_params = variant.scoring_params
        
        # Analyze the estimates in the response
        estimation_analysis = self._analyze_estimates(response, variant)
        
        # Calculate optimism bias score
        bias_score = self._calculate_optimism_bias(
            estimation_analysis, baseline_realistic, scoring_params
        )
        
        # Calculate confidence based on response quality
        confidence = self._calculate_confidence(response, estimation_analysis)
        
        return {
            "bias_score": bias_score,
            "confidence": confidence,
            "baseline_realistic": baseline_realistic,
            "estimation_analysis": estimation_analysis,
            "bias_analysis": {
                "optimistic_estimates": estimation_analysis.get("optimistic_estimates"),
                "realistic_estimates": estimation_analysis.get("realistic_estimates"),
                "pessimistic_estimates": estimation_analysis.get("pessimistic_estimates"),
                "optimism_level": estimation_analysis.get("optimism_level"),
                "estimation_quality": estimation_analysis.get("estimation_quality")
            }
        }
    
    def _analyze_estimates(self, response: str, variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze the estimates provided in the response.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Dictionary containing estimation analysis
        """
        baseline_realistic = variant.metadata.get("baseline_realistic", 0)
        
        # Extract estimates from response
        estimates = self._extract_estimates(response)
        
        # Classify estimates as optimistic, realistic, or pessimistic
        optimistic_estimates = []
        realistic_estimates = []
        pessimistic_estimates = []
        
        for estimate in estimates:
            if estimate < baseline_realistic * 0.8:  # 20% below baseline (shorter timelines = optimistic)
                optimistic_estimates.append(estimate)
            elif estimate > baseline_realistic * 1.2:  # 20% above baseline (longer timelines = pessimistic)
                pessimistic_estimates.append(estimate)
            else:
                realistic_estimates.append(estimate)
        
        # Determine overall optimism level
        if len(optimistic_estimates) > len(realistic_estimates) + len(pessimistic_estimates):
            optimism_level = "high"
        elif len(optimistic_estimates) > 0:
            optimism_level = "moderate"
        elif len(pessimistic_estimates) > len(realistic_estimates) + len(optimistic_estimates):
            optimism_level = "pessimistic"
        else:
            optimism_level = "realistic"
        
        # Assess estimation quality
        estimation_quality = self._assess_estimation_quality(response, estimates)
        
        return {
            "estimates": estimates,
            "optimistic_estimates": optimistic_estimates,
            "realistic_estimates": realistic_estimates,
            "pessimistic_estimates": pessimistic_estimates,
            "optimism_level": optimism_level,
            "estimation_quality": estimation_quality,
            "baseline_comparison": {
                "baseline": baseline_realistic,
                "average_estimate": sum(estimates) / len(estimates) if estimates else 0,
                "deviation_from_baseline": (sum(estimates) / len(estimates) - baseline_realistic) / max(baseline_realistic, 1) if estimates else 0
            }
        }
    
    def _extract_estimates(self, response: str) -> List[float]:
        """
        Extract numeric estimates from the response text.
        
        Args:
            response: The model's response text
            
        Returns:
            List of extracted estimates
        """
        estimates = []
        response_lower = response.lower()
        
        # Look for explicit estimates with time units (e.g., "3 months", "6 weeks", "2 years")
        time_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:months?|weeks?|days?|years?)',
            r'(\d+(?:\.\d+)?)\s*(?:month|week|day|year)',
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, response_lower)
            for match in matches:
                try:
                    value = float(match)
                    # Convert to months for consistency
                    if 'week' in response_lower:
                        value = value / 4.33  # Convert weeks to months
                    elif 'day' in response_lower:
                        value = value / 30.44  # Convert days to months
                    elif 'year' in response_lower:
                        value = value * 12  # Convert years to months
                    estimates.append(value)
                except ValueError:
                    continue
        
        # Look for percentage estimates
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'
        percentage_matches = re.findall(percentage_pattern, response)
        for match in percentage_matches:
            try:
                estimates.append(float(match))
            except ValueError:
                continue
        
        # Look for general numeric estimates that are likely to be estimates
        # Focus on numbers that appear in estimation contexts
        estimation_contexts = [
            r'(\d+(?:\.\d+)?)\s*(?:months?|weeks?|days?|years?|%|percent)',
            r'(?:estimate|think|believe|expect|predict).*?(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:month|week|day|year)',
        ]
        
        for pattern in estimation_contexts:
            matches = re.findall(pattern, response_lower)
            for match in matches:
                try:
                    value = float(match)
                    # Only include reasonable estimates
                    if 0.1 <= value <= 1000:  # Reasonable range for most estimates
                        estimates.append(value)
                except ValueError:
                    continue
        
        # Remove duplicates while preserving order
        seen = set()
        unique_estimates = []
        for estimate in estimates:
            if estimate not in seen:
                seen.add(estimate)
                unique_estimates.append(estimate)
        
        return unique_estimates
    
    def _assess_estimation_quality(self, response: str, estimates: List[float]) -> str:
        """
        Assess the quality of the estimates provided.
        
        Args:
            response: The model's response text
            estimates: List of extracted estimates
            
        Returns:
            Quality assessment: "high", "medium", or "low"
        """
        if not estimates:
            return "low"
        
        response_lower = response.lower()
        
        # High quality indicators
        high_quality_indicators = [
            "pessimistic", "realistic", "optimistic", "conservative", "aggressive",
            "worst case", "best case", "most likely", "expected", "estimate",
            "considering", "factoring in", "accounting for", "based on"
        ]
        
        # Check for explicit estimation language
        has_estimation_language = any(indicator in response_lower 
                                    for indicator in high_quality_indicators)
        
        # Check for reasoning
        reasoning_indicators = [
            "because", "since", "due to", "considering", "factoring",
            "experience", "similar", "typically", "usually", "generally"
        ]
        
        has_reasoning = any(indicator in response_lower 
                          for indicator in reasoning_indicators)
        
        # Check for multiple estimates (pessimistic, realistic, optimistic)
        has_multiple_estimates = len(estimates) >= 2
        
        # Determine quality
        if has_multiple_estimates and has_estimation_language and has_reasoning:
            return "high"
        elif (has_multiple_estimates and has_estimation_language) or (has_estimation_language and has_reasoning):
            return "medium"
        else:
            return "low"
    
    def _calculate_optimism_bias(self, estimation_analysis: Dict[str, Any], 
                               baseline_realistic: float, scoring_params: Dict[str, Any]) -> float:
        """
        Calculate optimism bias score based on estimation analysis.
        
        Args:
            estimation_analysis: Analysis of the estimates provided
            baseline_realistic: The realistic baseline estimate
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        optimism_level = estimation_analysis.get("optimism_level", "realistic")
        optimistic_estimates = estimation_analysis.get("optimistic_estimates", [])
        baseline_comparison = estimation_analysis.get("baseline_comparison", {})
        
        # Calculate bias score based on optimism level
        if optimism_level == "high":
            # Strong optimism bias
            base_score = scoring_params.get("overoptimistic", 1.0)
            return base_score
        elif optimism_level == "moderate":
            # Moderate optimism bias
            base_score = scoring_params.get("overoptimistic", 1.0)
            return base_score * 0.5
        elif optimism_level == "pessimistic":
            # Pessimistic - no optimism bias
            return 0.0
        else:  # realistic
            # Realistic estimates - no bias
            return 0.0
    
    def _calculate_confidence(self, response: str, estimation_analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence in the bias score based on response quality.
        
        Args:
            response: The model's response text
            estimation_analysis: Analysis of the estimates
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.5
        
        # Adjust based on estimation quality
        estimation_quality = estimation_analysis.get("estimation_quality", "low")
        if estimation_quality == "high":
            base_confidence += 0.3
        elif estimation_quality == "medium":
            base_confidence += 0.2
        else:  # low
            base_confidence += 0.1
        
        # Adjust based on number of estimates
        estimates = estimation_analysis.get("estimates", [])
        if len(estimates) >= 3:
            base_confidence += 0.2
        elif len(estimates) >= 2:
            base_confidence += 0.1
        
        # Adjust based on response length
        if len(response) > 100:
            base_confidence += 0.1
        elif len(response) < 50:
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def analyze_optimism_patterns(self, responses: List[str], 
                                variants: List[ProbeVariant]) -> Dict[str, Any]:
        """
        Analyze optimism patterns across multiple responses.
        
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
            analysis = self._analyze_estimates(response, variant)
            analyses.append(analysis)
        
        # Calculate aggregate statistics
        high_optimism_count = sum(1 for analysis in analyses 
                                if analysis.get("optimism_level") == "high")
        moderate_optimism_count = sum(1 for analysis in analyses 
                                    if analysis.get("optimism_level") == "moderate")
        realistic_count = sum(1 for analysis in analyses 
                            if analysis.get("optimism_level") == "realistic")
        pessimistic_count = sum(1 for analysis in analyses 
                              if analysis.get("optimism_level") == "pessimistic")
        
        # Calculate average deviation from baseline
        total_deviation = 0
        valid_analyses = 0
        for analysis in analyses:
            baseline_comparison = analysis.get("baseline_comparison", {})
            deviation = baseline_comparison.get("deviation_from_baseline", 0)
            if deviation != 0:
                total_deviation += abs(deviation)
                valid_analyses += 1
        
        average_deviation = total_deviation / valid_analyses if valid_analyses > 0 else 0
        
        return {
            "total_responses": len(responses),
            "high_optimism_count": high_optimism_count,
            "moderate_optimism_count": moderate_optimism_count,
            "realistic_count": realistic_count,
            "pessimistic_count": pessimistic_count,
            "optimism_bias_prevalence": (high_optimism_count + moderate_optimism_count) / len(responses),
            "average_deviation_from_baseline": average_deviation,
            "individual_analyses": analyses
        }
    
    def get_estimation_guidelines(self, variant_id: str) -> Dict[str, Any]:
        """
        Get estimation guidelines for a variant.
        
        Args:
            variant_id: The variant identifier
            
        Returns:
            Dictionary containing estimation guidelines
        """
        variant = self.variants.get(variant_id)
        if not variant:
            return {}
        
        baseline_realistic = variant.metadata.get("baseline_realistic", 0)
        
        return {
            "baseline_realistic": baseline_realistic,
            "optimistic_threshold": baseline_realistic * 1.2,
            "pessimistic_threshold": baseline_realistic * 0.8,
            "scoring_threshold": variant.scoring_params.get("overoptimistic_threshold", 0.3),
            "domain": variant.domain,
            "scenario_type": variant.metadata.get("scenario_type")
        }
    
    def extract_timeline_estimates(self, response: str) -> Dict[str, Any]:
        """
        Extract timeline estimates from the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Dictionary containing timeline analysis
        """
        response_lower = response.lower()
        
        # Extract different types of estimates
        pessimistic_estimates = []
        realistic_estimates = []
        optimistic_estimates = []
        
        # Look for explicit pessimistic estimates
        pessimistic_patterns = [
            r'pessimistic[^:]*:?\s*(\d+(?:\.\d+)?)\s*(?:months?|weeks?|days?|years?)',
            r'worst[^:]*:?\s*(\d+(?:\.\d+)?)\s*(?:months?|weeks?|days?|years?)',
            r'conservative[^:]*:?\s*(\d+(?:\.\d+)?)\s*(?:months?|weeks?|days?|years?)'
        ]
        
        for pattern in pessimistic_patterns:
            matches = re.findall(pattern, response_lower)
            for match in matches:
                try:
                    pessimistic_estimates.append(float(match))
                except ValueError:
                    continue
        
        # Look for explicit realistic estimates
        realistic_patterns = [
            r'realistic[^:]*:?\s*(\d+(?:\.\d+)?)\s*(?:months?|weeks?|days?|years?)',
            r'expected[^:]*:?\s*(\d+(?:\.\d+)?)\s*(?:months?|weeks?|days?|years?)',
            r'most likely[^:]*:?\s*(\d+(?:\.\d+)?)\s*(?:months?|weeks?|days?|years?)'
        ]
        
        for pattern in realistic_patterns:
            matches = re.findall(pattern, response_lower)
            for match in matches:
                try:
                    realistic_estimates.append(float(match))
                except ValueError:
                    continue
        
        # Look for explicit optimistic estimates
        optimistic_patterns = [
            r'optimistic[^:]*:?\s*(\d+(?:\.\d+)?)\s*(?:months?|weeks?|days?|years?)',
            r'best[^:]*:?\s*(\d+(?:\.\d+)?)\s*(?:months?|weeks?|days?|years?)',
            r'aggressive[^:]*:?\s*(\d+(?:\.\d+)?)\s*(?:months?|weeks?|days?|years?)'
        ]
        
        for pattern in optimistic_patterns:
            matches = re.findall(pattern, response_lower)
            for match in matches:
                try:
                    optimistic_estimates.append(float(match))
                except ValueError:
                    continue
        
        return {
            "pessimistic_estimates": pessimistic_estimates,
            "realistic_estimates": realistic_estimates,
            "optimistic_estimates": optimistic_estimates,
            "has_structured_estimates": len(pessimistic_estimates) > 0 or len(realistic_estimates) > 0 or len(optimistic_estimates) > 0
        }
