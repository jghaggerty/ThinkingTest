"""
Availability heuristic probe implementation.

This module implements probes to test for availability heuristic bias, where people
over-weight easily recalled or recently encountered information when making judgments.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .base import BaseProbe
from .types import ProbeType, ResponseFormat, ProbeVariant
from ..models.probe import ProbeRequest


class AvailabilityProbe(BaseProbe):
    """
    Availability heuristic bias probe.
    
    Tests for the tendency to over-weight easily recalled or recently encountered
    information when making judgments. This bias occurs when people judge the
    frequency or probability of events based on how easily examples come to mind.
    
    This probe uses priming scenarios to test for availability bias effects.
    """
    
    def __init__(self):
        super().__init__(
            probe_type=ProbeType.AVAILABILITY,
            name="Availability Heuristic",
            description="Tests for over-weighting of easily recalled or recent events"
        )
        self.variants: Dict[str, ProbeVariant] = {}
    
    def load_variants(self, config: Dict[str, Any]) -> None:
        """
        Load availability heuristic variants from configuration.
        
        Args:
            config: Configuration dictionary containing variant definitions
        """
        availability_config = config.get("probes", {}).get("availability", {})
        variants_config = availability_config.get("variants", [])
        
        for variant_config in variants_config:
            variant_id = variant_config["id"]
            domain = variant_config["domain"]
            correct_ranking = variant_config.get("correct_ranking", [])
            
            # Create separate variants for different priming conditions
            shark_prime_variant = ProbeVariant(
                id=f"{variant_id}_shark_prime",
                domain=domain,
                prompt=variant_config["shark_prime"],
                expected_bias="shark_overweight",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params={
                    "correct_ranking": correct_ranking,
                    "prime_type": "shark",
                    "primed_item": "shark_attacks",
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "prime_type": "shark",
                    "original_id": variant_id,
                    "rip_current_prime": variant_config["rip_current_prime"],
                    "correct_ranking": correct_ranking
                }
            )
            
            rip_current_prime_variant = ProbeVariant(
                id=f"{variant_id}_rip_current_prime",
                domain=domain,
                prompt=variant_config["rip_current_prime"],
                expected_bias="rip_current_overweight",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params={
                    "correct_ranking": correct_ranking,
                    "prime_type": "rip_current",
                    "primed_item": "rip_currents",
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "prime_type": "rip_current",
                    "original_id": variant_id,
                    "shark_prime": variant_config["shark_prime"],
                    "correct_ranking": correct_ranking
                }
            )
            
            self.variants[shark_prime_variant.id] = shark_prime_variant
            self.variants[rip_current_prime_variant.id] = rip_current_prime_variant
    
    def score_response(self, response: str, variant: ProbeVariant, 
                      execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a model's response for availability heuristic bias indicators.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            execution_metadata: Additional metadata from the execution
            
        Returns:
            Dictionary containing bias score, confidence, and analysis details
        """
        prime_type = variant.metadata.get("prime_type")
        primed_item = variant.scoring_params.get("primed_item")
        correct_ranking = variant.metadata.get("correct_ranking", [])
        scoring_params = variant.scoring_params
        
        # Analyze the ranking in the response
        ranking_analysis = self._analyze_ranking(response, variant)
        
        # Calculate availability bias score
        bias_score = self._calculate_availability_bias(
            ranking_analysis, prime_type, primed_item, correct_ranking, scoring_params
        )
        
        # Calculate confidence based on response quality
        confidence = self._calculate_confidence(response, ranking_analysis)
        
        return {
            "bias_score": bias_score,
            "confidence": confidence,
            "prime_type": prime_type,
            "primed_item": primed_item,
            "ranking_analysis": ranking_analysis,
            "correct_ranking": correct_ranking,
            "bias_analysis": {
                "primed_item_position": ranking_analysis.get("primed_item_position"),
                "correct_position": ranking_analysis.get("correct_position"),
                "overweight_detected": ranking_analysis.get("overweight_detected", False),
                "ranking_quality": ranking_analysis.get("ranking_quality", "unknown")
            }
        }
    
    def _analyze_ranking(self, response: str, variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze the risk ranking in the response.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Dictionary containing ranking analysis
        """
        primed_item = variant.scoring_params.get("primed_item")
        correct_ranking = variant.metadata.get("correct_ranking", [])
        
        # Extract ranking from response
        extracted_ranking = self._extract_ranking(response)
        
        # Find position of primed item in the ranking
        primed_item_position = None
        if extracted_ranking and primed_item:
            try:
                primed_item_position = extracted_ranking.index(primed_item) + 1  # 1-based
            except ValueError:
                pass
        
        # Find correct position of primed item
        correct_position = None
        if primed_item in correct_ranking:
            correct_position = correct_ranking.index(primed_item) + 1  # 1-based
        
        # Determine if primed item is overweighted (ranked higher than it should be)
        overweight_detected = False
        if primed_item_position is not None and correct_position is not None:
            overweight_detected = primed_item_position < correct_position
        
        # Assess ranking quality
        ranking_quality = self._assess_ranking_quality(response, extracted_ranking)
        
        return {
            "extracted_ranking": extracted_ranking,
            "primed_item_position": primed_item_position,
            "correct_position": correct_position,
            "overweight_detected": overweight_detected,
            "ranking_quality": ranking_quality,
            "response_length": len(response),
            "contains_ranking": bool(extracted_ranking)
        }
    
    def _extract_ranking(self, response: str) -> List[str]:
        """
        Extract risk ranking from the response text.
        
        Args:
            response: The model's response text
            
        Returns:
            List of risk items in order of ranking (most to least dangerous)
        """
        response_lower = response.lower()
        
        # Define the risk items to look for
        risk_items = {
            "shark_attacks": ["shark", "shark attack", "shark attacks"],
            "rip_currents": ["rip current", "rip currents", "rip tide"],
            "sunburn": ["sunburn", "sun burn", "uv exposure"],
            "drowning": ["drowning", "drown", "water safety"]
        }
        
        # Look for numbered lists or explicit rankings
        ranking = []
        
        # Try to find numbered rankings (1. 2. 3. etc.)
        numbered_pattern = r'(\d+)\.?\s*([^.\n]+)'
        numbered_matches = re.findall(numbered_pattern, response)
        
        if numbered_matches:
            # Sort by number and extract items
            sorted_matches = sorted(numbered_matches, key=lambda x: int(x[0]))
            for _, text in sorted_matches:
                item = self._identify_risk_item(text, risk_items)
                if item:
                    ranking.append(item)
        
        # If no numbered ranking found, try to find explicit mentions
        if not ranking:
            # Look for phrases like "most dangerous", "least dangerous", etc.
            for item, keywords in risk_items.items():
                if any(keyword in response_lower for keyword in keywords):
                    ranking.append(item)
        
        return ranking
    
    def _identify_risk_item(self, text: str, risk_items: Dict[str, List[str]]) -> Optional[str]:
        """
        Identify which risk item is mentioned in the given text.
        
        Args:
            text: Text to analyze
            risk_items: Dictionary mapping risk items to their keywords
            
        Returns:
            Risk item name if found, None otherwise
        """
        text_lower = text.lower()
        
        for item, keywords in risk_items.items():
            if any(keyword in text_lower for keyword in keywords):
                return item
        
        return None
    
    def _assess_ranking_quality(self, response: str, extracted_ranking: List[str]) -> str:
        """
        Assess the quality of the ranking in the response.
        
        Args:
            response: The model's response text
            extracted_ranking: The extracted ranking
            
        Returns:
            Quality assessment: "high", "medium", or "low"
        """
        if not extracted_ranking:
            return "low"
        
        # High quality indicators
        high_quality_indicators = [
            "rank", "ranking", "order", "most dangerous", "least dangerous",
            "priority", "severity", "risk level", "threat level"
        ]
        
        # Check for explicit ranking language
        has_ranking_language = any(indicator in response.lower() 
                                 for indicator in high_quality_indicators)
        
        # Check for reasoning
        reasoning_indicators = [
            "because", "since", "due to", "based on", "considering",
            "statistics", "data", "evidence", "research"
        ]
        
        has_reasoning = any(indicator in response.lower() 
                          for indicator in reasoning_indicators)
        
        # Determine quality
        if len(extracted_ranking) >= 3 and has_ranking_language and has_reasoning:
            return "high"
        elif len(extracted_ranking) >= 2 and (has_ranking_language or has_reasoning):
            return "medium"
        else:
            return "low"
    
    def _calculate_availability_bias(self, ranking_analysis: Dict[str, Any], 
                                   prime_type: str, primed_item: str,
                                   correct_ranking: List[str], 
                                   scoring_params: Dict[str, Any]) -> float:
        """
        Calculate availability bias score based on ranking analysis.
        
        Args:
            ranking_analysis: Analysis of the ranking in the response
            prime_type: Type of prime used ("shark" or "rip_current")
            primed_item: The item that was primed
            correct_ranking: The correct ranking of items
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        if not ranking_analysis.get("contains_ranking"):
            return 0.0
        
        overweight_detected = ranking_analysis.get("overweight_detected", False)
        primed_item_position = ranking_analysis.get("primed_item_position")
        correct_position = ranking_analysis.get("correct_position")
        
        if not overweight_detected:
            return 0.0
        
        # Calculate bias score based on how much the primed item is overweighted
        if primed_item_position is not None and correct_position is not None:
            position_difference = correct_position - primed_item_position
            max_difference = len(correct_ranking) - 1
            
            # Normalize the difference to get bias score
            bias_score = position_difference / max_difference
            
            # Apply scoring parameters
            base_score = scoring_params.get("primed_item_overweight", 1.0)
            return min(bias_score * base_score, 1.0)
        
        return 0.0
    
    def _calculate_confidence(self, response: str, ranking_analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence in the bias score based on response quality.
        
        Args:
            response: The model's response text
            ranking_analysis: Analysis of the ranking
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.5
        
        # Increase confidence if ranking was successfully extracted
        if ranking_analysis.get("contains_ranking"):
            base_confidence += 0.3
        
        # Adjust based on ranking quality
        ranking_quality = ranking_analysis.get("ranking_quality", "low")
        if ranking_quality == "high":
            base_confidence += 0.2
        elif ranking_quality == "medium":
            base_confidence += 0.1
        
        # Adjust based on response length
        response_length = ranking_analysis.get("response_length", 0)
        if response_length > 100:
            base_confidence += 0.1
        elif response_length < 50:
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def get_paired_variants(self, original_id: str) -> List[ProbeVariant]:
        """
        Get both primed variants for a given original ID.
        
        Args:
            original_id: The original variant ID (without _shark_prime/_rip_current_prime suffix)
            
        Returns:
            List containing both primed variants
        """
        shark_variant = self.variants.get(f"{original_id}_shark_prime")
        rip_current_variant = self.variants.get(f"{original_id}_rip_current_prime")
        
        variants = []
        if shark_variant:
            variants.append(shark_variant)
        if rip_current_variant:
            variants.append(rip_current_variant)
        
        return variants
    
    def analyze_availability_consistency(self, shark_response: str, rip_current_response: str,
                                       shark_variant: ProbeVariant, 
                                       rip_current_variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze consistency of availability effects across different priming conditions.
        
        Args:
            shark_response: Response to shark priming variant
            rip_current_response: Response to rip current priming variant
            shark_variant: The shark priming variant used
            rip_current_variant: The rip current priming variant used
            
        Returns:
            Dictionary containing consistency analysis
        """
        shark_analysis = self._analyze_ranking(shark_response, shark_variant)
        rip_current_analysis = self._analyze_ranking(rip_current_response, rip_current_variant)
        
        # Check for availability bias pattern
        shark_overweight = shark_analysis.get("overweight_detected", False)
        rip_current_overweight = rip_current_analysis.get("overweight_detected", False)
        
        # Classic availability pattern: primed items are overweighted
        classic_pattern = shark_overweight and rip_current_overweight
        
        # Calculate consistency score
        if classic_pattern:
            consistency_score = 1.0
        elif shark_overweight or rip_current_overweight:
            consistency_score = 0.5
        else:
            consistency_score = 0.0
        
        return {
            "availability_effect": classic_pattern,
            "consistency_score": consistency_score,
            "shark_overweight": shark_overweight,
            "rip_current_overweight": rip_current_overweight,
            "shark_analysis": shark_analysis,
            "rip_current_analysis": rip_current_analysis,
            "interpretation": self._interpret_availability_consistency(
                classic_pattern, shark_overweight, rip_current_overweight
            )
        }
    
    def _interpret_availability_consistency(self, classic_pattern: bool, 
                                          shark_overweight: bool, 
                                          rip_current_overweight: bool) -> str:
        """
        Interpret the availability consistency pattern.
        
        Args:
            classic_pattern: Whether classic availability pattern was observed
            shark_overweight: Whether shark attacks were overweighted
            rip_current_overweight: Whether rip currents were overweighted
            
        Returns:
            Interpretation string
        """
        if classic_pattern:
            return "Strong availability effect: primed items consistently overweighted in rankings"
        elif shark_overweight and not rip_current_overweight:
            return "Partial availability effect: shark attacks overweighted but rip currents not"
        elif rip_current_overweight and not shark_overweight:
            return "Partial availability effect: rip currents overweighted but shark attacks not"
        else:
            return "No clear availability effect: primed items not consistently overweighted"
    
    def get_priming_items(self, original_id: str) -> Dict[str, str]:
        """
        Get the priming items for a given variant.
        
        Args:
            original_id: The original variant ID
            
        Returns:
            Dictionary containing priming items
        """
        shark_variant = self.variants.get(f"{original_id}_shark_prime")
        rip_current_variant = self.variants.get(f"{original_id}_rip_current_prime")
        
        priming_items = {}
        
        if shark_variant:
            priming_items["shark"] = shark_variant.scoring_params.get("primed_item", "shark_attacks")
        
        if rip_current_variant:
            priming_items["rip_current"] = rip_current_variant.scoring_params.get("primed_item", "rip_currents")
        
        return priming_items
