"""
Base-rate neglect probe implementation.

This module implements probes to test for base-rate neglect, where people ignore
general statistical information (base rates) in favor of specific case information
when making judgments. This bias occurs when people focus on individuating
information while ignoring the prior probability or base rate.
"""

import re
import math
from typing import Dict, Any, List, Optional, Tuple
from .base import BaseProbe
from .types import ProbeType, ResponseFormat, ProbeVariant
from .types import ProbeRequest


class BaseRateProbe(BaseProbe):
    """
    Base-rate neglect bias probe.
    
    Tests for the tendency to ignore general statistical information (base rates)
    in favor of specific case information when making judgments. This bias occurs
    when people focus on individuating information while ignoring the prior
    probability or base rate, leading to incorrect Bayesian reasoning.
    
    This probe uses Bayesian reasoning scenarios to test for base-rate neglect.
    """
    
    def __init__(self):
        super().__init__(
            probe_type=ProbeType.BASE_RATE,
            name="Base-Rate Neglect",
            description="Tests for ignoring general statistical rates in favor of case-specific details"
        )
        self.variants: Dict[str, ProbeVariant] = {}
    
    def load_variants(self, config: Dict[str, Any]) -> None:
        """
        Load base-rate neglect variants from configuration.
        
        Args:
            config: Configuration dictionary containing variant definitions
        """
        base_rate_config = config.get("probes", {}).get("base_rate", {})
        variants_config = base_rate_config.get("variants", [])
        
        for variant_config in variants_config:
            variant_id = variant_config["id"]
            domain = variant_config["domain"]
            correct_answer = variant_config.get("correct_answer", 0.0)
            
            # Create variant for the base-rate neglect scenario
            variant = ProbeVariant(
                id=variant_id,
                domain=domain,
                prompt=variant_config["problem"],
                expected_bias="base_rate_neglect",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params={
                    "correct_answer": correct_answer,
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "original_id": variant_id,
                    "correct_answer": correct_answer,
                    "scenario_type": "base_rate_neglect"
                }
            )
            
            self.variants[variant.id] = variant
    
    def score_response(self, response: str, variant: ProbeVariant, 
                      execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a model's response for base-rate neglect bias indicators.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            execution_metadata: Additional metadata from the execution
            
        Returns:
            Dictionary containing bias score, confidence, and analysis details
        """
        correct_answer = variant.metadata.get("correct_answer", 0.0)
        scoring_params = variant.scoring_params
        
        # Analyze the probability calculation in the response
        probability_analysis = self._analyze_probability_calculation(response, variant)
        
        # Calculate base-rate neglect bias score
        bias_score = self._calculate_base_rate_bias(
            probability_analysis, correct_answer, scoring_params
        )
        
        # Calculate confidence based on response quality
        confidence = self._calculate_confidence(response, probability_analysis)
        
        return {
            "bias_score": bias_score,
            "confidence": confidence,
            "correct_answer": correct_answer,
            "probability_analysis": probability_analysis,
            "bias_analysis": {
                "extracted_probability": probability_analysis.get("extracted_probability"),
                "calculation_method": probability_analysis.get("calculation_method"),
                "base_rate_mentioned": probability_analysis.get("base_rate_mentioned"),
                "bayesian_reasoning": probability_analysis.get("bayesian_reasoning"),
                "reasoning_quality": probability_analysis.get("reasoning_quality")
            }
        }
    
    def _analyze_probability_calculation(self, response: str, variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze the probability calculation in the response.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Dictionary containing probability analysis
        """
        response_lower = response.lower()
        
        # Extract probability from response
        extracted_probability = self._extract_probability(response)
        
        # Analyze calculation method
        calculation_method = self._analyze_calculation_method(response)
        
        # Check if base rate is mentioned
        base_rate_mentioned = self._check_base_rate_mention(response)
        
        # Assess Bayesian reasoning
        bayesian_reasoning = self._assess_bayesian_reasoning(response)
        
        # Assess reasoning quality
        reasoning_quality = self._assess_reasoning_quality(response)
        
        return {
            "extracted_probability": extracted_probability,
            "calculation_method": calculation_method,
            "base_rate_mentioned": base_rate_mentioned,
            "bayesian_reasoning": bayesian_reasoning,
            "reasoning_quality": reasoning_quality,
            "response_length": len(response)
        }
    
    def _extract_probability(self, response: str) -> Optional[float]:
        """
        Extract probability value from the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Extracted probability value, or None if not found
        """
        # Look for percentage values
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'
        percentage_matches = re.findall(percentage_pattern, response)
        if percentage_matches:
            try:
                return float(percentage_matches[0]) / 100.0
            except ValueError:
                pass
        
        # Look for decimal probabilities
        decimal_pattern = r'(\d+(?:\.\d+)?)\s*(?:probability|chance|likelihood)'
        decimal_matches = re.findall(decimal_pattern, response.lower())
        if decimal_matches:
            try:
                value = float(decimal_matches[0])
                if value <= 1.0:
                    return value
                elif value <= 100.0:
                    return value / 100.0
            except ValueError:
                pass
        
        # Look for fractions
        fraction_pattern = r'(\d+)/(\d+)'
        fraction_matches = re.findall(fraction_pattern, response)
        if fraction_matches:
            try:
                numerator, denominator = map(int, fraction_matches[0])
                if denominator > 0:
                    return numerator / denominator
            except (ValueError, ZeroDivisionError):
                pass
        
        # Look for "out of" expressions
        out_of_pattern = r'(\d+)\s*out\s*of\s*(\d+)'
        out_of_matches = re.findall(out_of_pattern, response.lower())
        if out_of_matches:
            try:
                numerator, denominator = map(int, out_of_matches[0])
                if denominator > 0:
                    return numerator / denominator
            except (ValueError, ZeroDivisionError):
                pass
        
        return None
    
    def _analyze_calculation_method(self, response: str) -> str:
        """
        Analyze the method used for probability calculation.
        
        Args:
            response: The model's response text
            
        Returns:
            Calculation method: "bayesian", "base_rate_neglect", "intuitive", or "unclear"
        """
        response_lower = response.lower()
        
        # Look for Bayesian reasoning indicators
        bayesian_indicators = [
            "bayes", "bayesian", "prior", "posterior", "likelihood", "base rate",
            "prevalence", "population", "statistical", "probability theory",
            "conditional probability", "p(a|b)", "p(b|a)"
        ]
        
        bayesian_count = sum(1 for indicator in bayesian_indicators 
                           if indicator in response_lower)
        
        # Look for base rate neglect indicators
        neglect_indicators = [
            "test result", "positive test", "negative test", "symptom", "characteristic",
            "description", "profile", "appears to be", "seems like", "looks like"
        ]
        
        neglect_count = sum(1 for indicator in neglect_indicators 
                          if indicator in response_lower)
        
        # Look for mathematical reasoning
        math_indicators = [
            "calculate", "formula", "equation", "multiply", "divide", "add", "subtract",
            "0.9", "0.1", "0.05", "0.95", "90%", "10%", "5%", "95%"
        ]
        
        math_count = sum(1 for indicator in math_indicators 
                        if indicator in response_lower)
        
        # Determine calculation method
        if bayesian_count >= 2 or (bayesian_count >= 1 and math_count >= 2):
            return "bayesian"
        elif neglect_count >= 2 and bayesian_count == 0:
            return "base_rate_neglect"
        elif math_count >= 1:
            return "intuitive"
        else:
            return "unclear"
    
    def _check_base_rate_mention(self, response: str) -> bool:
        """
        Check if the base rate is mentioned in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            True if base rate is mentioned, False otherwise
        """
        response_lower = response.lower()
        
        base_rate_indicators = [
            "base rate", "prevalence", "population", "general", "overall",
            "1%", "0.01", "one percent", "rare", "common", "typical"
        ]
        
        return any(indicator in response_lower for indicator in base_rate_indicators)
    
    def _assess_bayesian_reasoning(self, response: str) -> Dict[str, Any]:
        """
        Assess the quality of Bayesian reasoning in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Dictionary containing Bayesian reasoning analysis
        """
        response_lower = response.lower()
        
        # Look for Bayesian components
        prior_mentioned = any(term in response_lower for term in ["prior", "base rate", "prevalence", "1%", "0.01"])
        likelihood_mentioned = any(term in response_lower for term in ["likelihood", "sensitivity", "specificity", "90%", "5%", "0.9", "0.05"])
        posterior_mentioned = any(term in response_lower for term in ["posterior", "result", "answer", "probability"])
        
        # Look for mathematical operations
        has_calculation = any(term in response_lower for term in ["calculate", "multiply", "divide", "formula", "equation"])
        
        # Count Bayesian reasoning quality
        bayesian_components = sum([prior_mentioned, likelihood_mentioned, posterior_mentioned])
        
        if bayesian_components >= 3 and has_calculation:
            quality = "high"
        elif bayesian_components >= 2:
            quality = "medium"
        elif bayesian_components >= 1:
            quality = "low"
        else:
            quality = "none"
        
        return {
            "prior_mentioned": prior_mentioned,
            "likelihood_mentioned": likelihood_mentioned,
            "posterior_mentioned": posterior_mentioned,
            "has_calculation": has_calculation,
            "bayesian_components": bayesian_components,
            "quality": quality
        }
    
    def _assess_reasoning_quality(self, response: str) -> str:
        """
        Assess the overall quality of reasoning in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Quality assessment: "high", "medium", or "low"
        """
        response_lower = response.lower()
        
        # High quality indicators
        high_quality_indicators = [
            "because", "since", "therefore", "thus", "consequently",
            "calculate", "formula", "equation", "probability", "statistical",
            "bayesian", "base rate", "prevalence", "likelihood"
        ]
        
        # Low quality indicators
        low_quality_indicators = [
            "i don't know", "unsure", "maybe", "perhaps", "could be",
            "not sure", "hard to say", "difficult to determine", "guess"
        ]
        
        high_count = sum(1 for indicator in high_quality_indicators 
                        if indicator in response_lower)
        low_count = sum(1 for indicator in low_quality_indicators 
                       if indicator in response_lower)
        
        # Determine quality based on indicators and response length
        if low_count > 0:
            return "low"
        elif high_count >= 4 and len(response) > 150:
            return "high"
        elif high_count >= 2 or len(response) > 100:
            return "medium"
        else:
            return "low"
    
    def _calculate_base_rate_bias(self, probability_analysis: Dict[str, Any], 
                                correct_answer: float, scoring_params: Dict[str, Any]) -> float:
        """
        Calculate base-rate neglect bias score based on probability analysis.
        
        Args:
            probability_analysis: Analysis of the probability calculation
            correct_answer: The correct Bayesian answer
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        extracted_probability = probability_analysis.get("extracted_probability")
        calculation_method = probability_analysis.get("calculation_method", "unclear")
        base_rate_mentioned = probability_analysis.get("base_rate_mentioned", False)
        bayesian_reasoning = probability_analysis.get("bayesian_reasoning", {})
        
        # If no probability was extracted, partial bias
        if extracted_probability is None:
            return 0.3
        
        # Calculate bias based on calculation method
        if calculation_method == "bayesian":
            # Bayesian reasoning - check if answer is close to correct
            if abs(extracted_probability - correct_answer) < 0.05:  # Within 5%
                return 0.0  # No bias
            else:
                return 0.2  # Some bias due to calculation error
        elif calculation_method == "base_rate_neglect":
            # Base rate neglect - strong bias
            base_score = scoring_params.get("base_rate_neglect", 1.0)
            return base_score
        elif calculation_method == "intuitive":
            # Intuitive reasoning - moderate bias
            return 0.5
        else:
            # Unclear reasoning - partial bias
            return 0.4
    
    def _calculate_confidence(self, response: str, probability_analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence in the bias score based on response quality.
        
        Args:
            response: The model's response text
            probability_analysis: Analysis of the probability calculation
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.5
        
        # Adjust based on reasoning quality
        reasoning_quality = probability_analysis.get("reasoning_quality", "low")
        if reasoning_quality == "high":
            base_confidence += 0.3
        elif reasoning_quality == "medium":
            base_confidence += 0.2
        else:  # low
            base_confidence += 0.1
        
        # Adjust based on Bayesian reasoning
        bayesian_reasoning = probability_analysis.get("bayesian_reasoning", {})
        if bayesian_reasoning.get("quality") == "high":
            base_confidence += 0.2
        elif bayesian_reasoning.get("quality") == "medium":
            base_confidence += 0.1
        
        # Adjust based on whether probability was extracted
        if probability_analysis.get("extracted_probability") is not None:
            base_confidence += 0.1
        
        # Adjust based on response length
        response_length = probability_analysis.get("response_length", 0)
        if response_length > 150:
            base_confidence += 0.1
        elif response_length < 50:
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def analyze_base_rate_patterns(self, responses: List[str], 
                                variants: List[ProbeVariant]) -> Dict[str, Any]:
        """
        Analyze base-rate neglect patterns across multiple responses.
        
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
            analysis = self._analyze_probability_calculation(response, variant)
            analyses.append(analysis)
        
        # Calculate aggregate statistics
        bayesian_count = sum(1 for analysis in analyses 
                           if analysis.get("calculation_method") == "bayesian")
        neglect_count = sum(1 for analysis in analyses 
                          if analysis.get("calculation_method") == "base_rate_neglect")
        intuitive_count = sum(1 for analysis in analyses 
                            if analysis.get("calculation_method") == "intuitive")
        unclear_count = sum(1 for analysis in analyses 
                          if analysis.get("calculation_method") == "unclear")
        
        # Calculate base rate mention prevalence
        base_rate_mentioned_count = sum(1 for analysis in analyses 
                                      if analysis.get("base_rate_mentioned", False))
        
        # Calculate average Bayesian reasoning quality
        bayesian_qualities = []
        for analysis in analyses:
            bayesian_reasoning = analysis.get("bayesian_reasoning", {})
            quality = bayesian_reasoning.get("quality", "none")
            if quality == "high":
                bayesian_qualities.append(1.0)
            elif quality == "medium":
                bayesian_qualities.append(0.5)
            elif quality == "low":
                bayesian_qualities.append(0.25)
            else:
                bayesian_qualities.append(0.0)
        
        average_bayesian_quality = sum(bayesian_qualities) / len(bayesian_qualities) if bayesian_qualities else 0.0
        
        return {
            "total_responses": len(responses),
            "bayesian_count": bayesian_count,
            "neglect_count": neglect_count,
            "intuitive_count": intuitive_count,
            "unclear_count": unclear_count,
            "base_rate_neglect_prevalence": (neglect_count + intuitive_count) / len(responses),
            "base_rate_mention_prevalence": base_rate_mentioned_count / len(responses),
            "average_bayesian_quality": average_bayesian_quality,
            "individual_analyses": analyses
        }
    
    def get_bayesian_calculation(self, variant_id: str) -> Dict[str, Any]:
        """
        Get the correct Bayesian calculation for a variant.
        
        Args:
            variant_id: The variant identifier
            
        Returns:
            Dictionary containing Bayesian calculation details
        """
        variant = self.variants.get(variant_id)
        if not variant:
            return {}
        
        correct_answer = variant.metadata.get("correct_answer", 0.0)
        
        # This would typically be calculated from the problem parameters
        # For now, we'll return the correct answer
        return {
            "correct_answer": correct_answer,
            "correct_percentage": correct_answer * 100,
            "domain": variant.domain,
            "scenario_type": variant.metadata.get("scenario_type")
        }
    
    def extract_bayesian_components(self, response: str) -> Dict[str, Any]:
        """
        Extract Bayesian reasoning components from the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Dictionary containing extracted components
        """
        response_lower = response.lower()
        
        # Extract base rate (prior probability)
        base_rate = None
        base_rate_patterns = [
            r'(\d+(?:\.\d+)?)\s*%?\s*(?:prevalence|base rate|population)',
            r'(?:prevalence|base rate|population)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%?'
        ]
        
        for pattern in base_rate_patterns:
            matches = re.findall(pattern, response_lower)
            if matches:
                try:
                    value = float(matches[0])
                    if value <= 1.0:
                        base_rate = value
                    elif value <= 100.0:
                        base_rate = value / 100.0
                    break
                except ValueError:
                    continue
        
        # Extract sensitivity (true positive rate)
        sensitivity = None
        sensitivity_patterns = [
            r'(\d+(?:\.\d+)?)\s*%?\s*(?:sensitivity|true positive)',
            r'(?:sensitivity|true positive)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%?'
        ]
        
        for pattern in sensitivity_patterns:
            matches = re.findall(pattern, response_lower)
            if matches:
                try:
                    value = float(matches[0])
                    if value <= 1.0:
                        sensitivity = value
                    elif value <= 100.0:
                        sensitivity = value / 100.0
                    break
                except ValueError:
                    continue
        
        # Extract specificity (true negative rate)
        specificity = None
        specificity_patterns = [
            r'(\d+(?:\.\d+)?)\s*%?\s*(?:specificity|true negative)',
            r'(?:specificity|true negative)\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*%?'
        ]
        
        for pattern in specificity_patterns:
            matches = re.findall(pattern, response_lower)
            if matches:
                try:
                    value = float(matches[0])
                    if value <= 1.0:
                        specificity = value
                    elif value <= 100.0:
                        specificity = value / 100.0
                    break
                except ValueError:
                    continue
        
        return {
            "base_rate": base_rate,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "has_all_components": all([base_rate is not None, sensitivity is not None, specificity is not None])
        }
