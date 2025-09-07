"""
Conjunction fallacy probe implementation.

This module implements probes to test for the conjunction fallacy, where people
judge the probability of a conjunction (A and B) to be greater than the probability
of one of its constituents (A or B). This violates the basic laws of probability
where P(A and B) ≤ P(A) and P(A and B) ≤ P(B).

The classic example is the "Linda problem" where people judge "Linda is a bank
teller and is active in the feminist movement" as more probable than "Linda is
a bank teller."
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .base import BaseProbe
from .types import ProbeType, ResponseFormat, ProbeVariant
from .types import ProbeRequest


class ConjunctionProbe(BaseProbe):
    """
    Conjunction fallacy bias probe.
    
    Tests for the tendency to judge the probability of a conjunction (A and B)
    to be greater than the probability of one of its constituents (A or B).
    This violates the basic laws of probability where P(A and B) ≤ P(A) and 
    P(A and B) ≤ P(B).
    
    This probe uses "Linda problem" style variants to test for conjunction fallacy.
    """
    
    def __init__(self):
        super().__init__(
            probe_type=ProbeType.CONJUNCTION,
            name="Conjunction Fallacy",
            description="Tests for judging conjunctions as more probable than their constituents"
        )
        self.variants: Dict[str, ProbeVariant] = {}
    
    def load_variants(self, config: Dict[str, Any]) -> None:
        """
        Load conjunction fallacy variants from configuration.
        
        Args:
            config: Configuration dictionary containing variant definitions
        """
        conjunction_config = config.get("probes", {}).get("conjunction", {})
        variants_config = conjunction_config.get("variants", [])
        
        for variant_config in variants_config:
            variant_id = variant_config["id"]
            domain = variant_config["domain"]
            correct_answer = variant_config.get("correct_answer", "constituent")
            
            # Create variant for the conjunction fallacy scenario
            description = variant_config.get("description", "")
            question = variant_config.get("question", "")
            prompt = f"{description}\n\n{question}"
            
            variant = ProbeVariant(
                id=variant_id,
                domain=domain,
                prompt=prompt,
                expected_bias="conjunction_fallacy",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params={
                    "correct_answer": correct_answer,
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "original_id": variant_id,
                    "correct_answer": correct_answer,
                    "scenario_type": "conjunction_fallacy"
                }
            )
            
            self.variants[variant.id] = variant
    
    def score_response(self, response: str, variant: ProbeVariant, 
                      execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a model's response for conjunction fallacy bias indicators.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            execution_metadata: Additional metadata from the execution
            
        Returns:
            Dictionary containing bias score, confidence, and analysis details
        """
        correct_answer = variant.metadata.get("correct_answer", "constituent")
        scoring_params = variant.scoring_params
        
        # Analyze the probability judgment in the response
        probability_analysis = self._analyze_probability_judgment(response, variant)
        
        # Calculate conjunction fallacy bias score
        bias_score = self._calculate_conjunction_bias(
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
                "chosen_option": probability_analysis.get("chosen_option"),
                "reasoning_type": probability_analysis.get("reasoning_type"),
                "probability_mentioned": probability_analysis.get("probability_mentioned"),
                "conjunction_mentioned": probability_analysis.get("conjunction_mentioned"),
                "constituent_mentioned": probability_analysis.get("constituent_mentioned"),
                "reasoning_quality": probability_analysis.get("reasoning_quality")
            }
        }
    
    def _analyze_probability_judgment(self, response: str, variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze the probability judgment in the response.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Dictionary containing probability judgment analysis
        """
        response_lower = response.lower()
        
        # Determine which option was chosen
        chosen_option = self._determine_chosen_option(response, variant)
        
        # Analyze reasoning type
        reasoning_type = self._analyze_reasoning_type(response)
        
        # Check if probability concepts are mentioned
        probability_mentioned = self._check_probability_mention(response)
        
        # Check if conjunction is mentioned
        conjunction_mentioned = self._check_conjunction_mention(response)
        
        # Check if constituent is mentioned
        constituent_mentioned = self._check_constituent_mention(response)
        
        # Assess reasoning quality
        reasoning_quality = self._assess_reasoning_quality(response)
        
        return {
            "chosen_option": chosen_option,
            "reasoning_type": reasoning_type,
            "probability_mentioned": probability_mentioned,
            "conjunction_mentioned": conjunction_mentioned,
            "constituent_mentioned": constituent_mentioned,
            "reasoning_quality": reasoning_quality,
            "response_length": len(response)
        }
    
    def _determine_chosen_option(self, response: str, variant: ProbeVariant) -> str:
        """
        Determine which option was chosen in the response.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Chosen option: "conjunction", "constituent", "both", or "unclear"
        """
        response_lower = response.lower()
        
        # Look for explicit option choices (A, B, option A, option B)
        if "option a" in response_lower or "choice a" in response_lower:
            return "constituent"
        elif "option b" in response_lower or "choice b" in response_lower:
            return "conjunction"
        
        # Look for explicit choices
        choice_indicators = [
            "choose", "select", "pick", "prefer", "more likely", "more probable",
            "better", "correct", "right", "answer"
        ]
        
        # Look for conjunction indicators
        conjunction_indicators = [
            "both", "and", "also", "additionally", "furthermore", "moreover",
            "conjunction", "combined", "together", "simultaneously", "teacher and poet"
        ]
        
        # Look for constituent indicators
        constituent_indicators = [
            "single", "alone", "just", "only", "merely", "simply",
            "constituent", "individual", "separate", "independent", "just a teacher"
        ]
        
        # Count mentions of each type
        conjunction_count = sum(1 for indicator in conjunction_indicators 
                              if indicator in response_lower)
        constituent_count = sum(1 for indicator in constituent_indicators 
                              if indicator in response_lower)
        
        # Look for explicit probability comparisons
        if "more likely" in response_lower or "more probable" in response_lower:
            if conjunction_count > constituent_count:
                return "conjunction"
            elif constituent_count > conjunction_count:
                return "constituent"
        
        # Look for explicit choices
        if any(indicator in response_lower for indicator in choice_indicators):
            if conjunction_count > constituent_count:
                return "conjunction"
            elif constituent_count > conjunction_count:
                return "constituent"
        
        # If both are mentioned equally, check for other indicators
        if conjunction_count > 0 and constituent_count > 0:
            return "both"
        elif conjunction_count > 0:
            return "conjunction"
        elif constituent_count > 0:
            return "constituent"
        else:
            return "unclear"
    
    def _analyze_reasoning_type(self, response: str) -> str:
        """
        Analyze the type of reasoning used in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Reasoning type: "representativeness", "probability", "logical", or "unclear"
        """
        response_lower = response.lower()
        
        # Look for representativeness heuristic indicators
        representativeness_indicators = [
            "typical", "characteristic", "representative", "stereotypical",
            "fits", "matches", "describes", "portrays", "seems like",
            "appears to be", "looks like", "sounds like", "reminds me of"
        ]
        
        # Look for probability theory indicators
        probability_indicators = [
            "probability", "probable", "likely", "chance", "odds",
            "mathematical", "statistical", "logical", "reasoning",
            "conjunction", "constituent", "independent", "mutually exclusive"
        ]
        
        # Look for logical reasoning indicators
        logical_indicators = [
            "because", "therefore", "thus", "consequently", "hence",
            "logical", "reasoning", "analysis", "evaluation", "assessment"
        ]
        
        # Count mentions of each type
        representativeness_count = sum(1 for indicator in representativeness_indicators 
                                    if indicator in response_lower)
        probability_count = sum(1 for indicator in probability_indicators 
                              if indicator in response_lower)
        logical_count = sum(1 for indicator in logical_indicators 
                          if indicator in response_lower)
        
        # Determine reasoning type
        if representativeness_count >= 2 and probability_count == 0:
            return "representativeness"
        elif probability_count >= 2 or logical_count >= 2:
            return "probability"
        elif logical_count >= 1:
            return "logical"
        else:
            return "unclear"
    
    def _check_probability_mention(self, response: str) -> bool:
        """
        Check if probability concepts are mentioned in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            True if probability concepts are mentioned, False otherwise
        """
        response_lower = response.lower()
        
        probability_indicators = [
            "probability", "probable", "likely", "chance", "odds",
            "more likely", "less likely", "most likely", "least likely",
            "mathematical", "statistical", "logical", "reasoning"
        ]
        
        return any(indicator in response_lower for indicator in probability_indicators)
    
    def _check_conjunction_mention(self, response: str) -> bool:
        """
        Check if conjunction concepts are mentioned in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            True if conjunction concepts are mentioned, False otherwise
        """
        response_lower = response.lower()
        
        conjunction_indicators = [
            "conjunction", "both", "and", "also", "additionally",
            "combined", "together", "simultaneously", "jointly"
        ]
        
        return any(indicator in response_lower for indicator in conjunction_indicators)
    
    def _check_constituent_mention(self, response: str) -> bool:
        """
        Check if constituent concepts are mentioned in the response.
        
        Args:
            response: The model's response text
            
        Returns:
            True if constituent concepts are mentioned, False otherwise
        """
        response_lower = response.lower()
        
        constituent_indicators = [
            "constituent", "single", "alone", "just", "only",
            "individual", "separate", "independent", "merely"
        ]
        
        return any(indicator in response_lower for indicator in constituent_indicators)
    
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
            "probability", "mathematical", "logical", "reasoning",
            "analysis", "evaluation", "assessment", "consideration"
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
    
    def _calculate_conjunction_bias(self, probability_analysis: Dict[str, Any], 
                                  correct_answer: str, scoring_params: Dict[str, Any]) -> float:
        """
        Calculate conjunction fallacy bias score based on probability analysis.
        
        Args:
            probability_analysis: Analysis of the probability judgment
            correct_answer: The correct answer (should be "constituent")
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        chosen_option = probability_analysis.get("chosen_option", "unclear")
        reasoning_type = probability_analysis.get("reasoning_type", "unclear")
        probability_mentioned = probability_analysis.get("probability_mentioned", False)
        
        # If constituent is chosen (correct), no bias
        if chosen_option == "constituent":
            return 0.0
        
        # If conjunction is chosen (incorrect), calculate bias
        elif chosen_option == "conjunction":
            # Base bias score
            base_score = scoring_params.get("conjunction_fallacy", 1.0)
            
            # Adjust based on reasoning type
            if reasoning_type == "representativeness":
                # Strong bias - using representativeness heuristic
                return base_score
            elif reasoning_type == "probability":
                # Moderate bias - some probability awareness but still wrong
                return base_score * 0.7
            elif reasoning_type == "logical":
                # Lower bias - logical reasoning but wrong conclusion
                return base_score * 0.5
            else:
                # Unclear reasoning - partial bias
                return base_score * 0.8
        
        # If both are chosen or unclear, partial bias
        elif chosen_option in ["both", "unclear"]:
            return 0.3
        
        # Default case
        return 0.5
    
    def _calculate_confidence(self, response: str, probability_analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence in the bias score based on response quality.
        
        Args:
            response: The model's response text
            probability_analysis: Analysis of the probability judgment
            
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
        
        # Adjust based on whether probability concepts are mentioned
        if probability_analysis.get("probability_mentioned", False):
            base_confidence += 0.1
        
        # Adjust based on reasoning type clarity
        reasoning_type = probability_analysis.get("reasoning_type", "unclear")
        if reasoning_type != "unclear":
            base_confidence += 0.1
        
        # Adjust based on response length
        response_length = probability_analysis.get("response_length", 0)
        if response_length > 150:
            base_confidence += 0.1
        elif response_length < 50:
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def analyze_conjunction_patterns(self, responses: List[str], 
                                  variants: List[ProbeVariant]) -> Dict[str, Any]:
        """
        Analyze conjunction fallacy patterns across multiple responses.
        
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
            analysis = self._analyze_probability_judgment(response, variant)
            analyses.append(analysis)
        
        # Calculate aggregate statistics
        conjunction_count = sum(1 for analysis in analyses 
                              if analysis.get("chosen_option") == "conjunction")
        constituent_count = sum(1 for analysis in analyses 
                              if analysis.get("chosen_option") == "constituent")
        both_count = sum(1 for analysis in analyses 
                        if analysis.get("chosen_option") == "both")
        unclear_count = sum(1 for analysis in analyses 
                          if analysis.get("chosen_option") == "unclear")
        
        # Calculate reasoning type distribution
        representativeness_count = sum(1 for analysis in analyses 
                                     if analysis.get("reasoning_type") == "representativeness")
        probability_count = sum(1 for analysis in analyses 
                              if analysis.get("reasoning_type") == "probability")
        logical_count = sum(1 for analysis in analyses 
                          if analysis.get("reasoning_type") == "logical")
        
        # Calculate probability mention prevalence
        probability_mentioned_count = sum(1 for analysis in analyses 
                                        if analysis.get("probability_mentioned", False))
        
        # Calculate average reasoning quality
        quality_scores = []
        for analysis in analyses:
            quality = analysis.get("reasoning_quality", "low")
            if quality == "high":
                quality_scores.append(1.0)
            elif quality == "medium":
                quality_scores.append(0.5)
            else:
                quality_scores.append(0.0)
        
        average_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        return {
            "total_responses": len(responses),
            "conjunction_count": conjunction_count,
            "constituent_count": constituent_count,
            "both_count": both_count,
            "unclear_count": unclear_count,
            "conjunction_fallacy_prevalence": conjunction_count / len(responses),
            "representativeness_count": representativeness_count,
            "probability_count": probability_count,
            "logical_count": logical_count,
            "probability_mention_prevalence": probability_mentioned_count / len(responses),
            "average_reasoning_quality": average_quality,
            "individual_analyses": analyses
        }
    
    def get_conjunction_analysis(self, variant_id: str) -> Dict[str, Any]:
        """
        Get conjunction fallacy analysis for a variant.
        
        Args:
            variant_id: The variant identifier
            
        Returns:
            Dictionary containing conjunction analysis
        """
        variant = self.variants.get(variant_id)
        if not variant:
            return {}
        
        correct_answer = variant.metadata.get("correct_answer", "constituent")
        
        return {
            "correct_answer": correct_answer,
            "domain": variant.domain,
            "scenario_type": variant.metadata.get("scenario_type"),
            "expected_bias": variant.expected_bias
        }
    
    def extract_reasoning_components(self, response: str) -> Dict[str, Any]:
        """
        Extract reasoning components from the response.
        
        Args:
            response: The model's response text
            
        Returns:
            Dictionary containing extracted components
        """
        response_lower = response.lower()
        
        # Extract representativeness indicators
        representativeness_indicators = [
            "typical", "characteristic", "representative", "stereotypical",
            "fits", "matches", "describes", "portrays", "seems like",
            "appears to be", "looks like", "sounds like", "reminds me of"
        ]
        
        representativeness_mentions = []
        for indicator in representativeness_indicators:
            if indicator in response_lower:
                representativeness_mentions.append(indicator)
        
        # Extract probability indicators
        probability_indicators = [
            "probability", "probable", "likely", "chance", "odds",
            "more likely", "less likely", "most likely", "least likely"
        ]
        
        probability_mentions = []
        for indicator in probability_indicators:
            if indicator in response_lower:
                probability_mentions.append(indicator)
        
        # Extract logical reasoning indicators
        logical_indicators = [
            "because", "therefore", "thus", "consequently", "hence",
            "logical", "reasoning", "analysis", "evaluation", "assessment"
        ]
        
        logical_mentions = []
        for indicator in logical_indicators:
            if indicator in response_lower:
                logical_mentions.append(indicator)
        
        return {
            "representativeness_mentions": representativeness_mentions,
            "probability_mentions": probability_mentions,
            "logical_mentions": logical_mentions,
            "has_representativeness": len(representativeness_mentions) > 0,
            "has_probability": len(probability_mentions) > 0,
            "has_logical": len(logical_mentions) > 0
        }
