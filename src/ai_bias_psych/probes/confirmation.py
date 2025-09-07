"""
Confirmation bias probe implementation.

This module implements probes to test for confirmation bias, where people tend to
search for, interpret, and recall information in a way that confirms their
pre-existing beliefs or hypotheses, while giving disproportionately less attention
to information that contradicts their beliefs.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from .base import BaseProbe
from .types import ProbeType, ResponseFormat, ProbeVariant
from ..models.probe import ProbeRequest


class ConfirmationProbe(BaseProbe):
    """
    Confirmation bias probe.
    
    Tests for the tendency to search for, interpret, and recall information in a way
    that confirms pre-existing beliefs or hypotheses, while giving disproportionately
    less attention to information that contradicts those beliefs.
    
    This probe uses mixed evidence presentation to test for confirmation bias.
    """
    
    def __init__(self):
        super().__init__(
            probe_type=ProbeType.CONFIRMATION,
            name="Confirmation Bias",
            description="Tests for preference for evidence supporting existing beliefs"
        )
        self.variants: Dict[str, ProbeVariant] = {}
    
    def load_variants(self, config: Dict[str, Any]) -> None:
        """
        Load confirmation bias variants from configuration.
        
        Args:
            config: Configuration dictionary containing variant definitions
        """
        confirmation_config = config.get("probes", {}).get("confirmation", {})
        variants_config = confirmation_config.get("variants", [])
        
        for variant_config in variants_config:
            variant_id = variant_config["id"]
            domain = variant_config["domain"]
            hypothesis = variant_config.get("hypothesis", "")
            expected_balanced = variant_config.get("expected_balanced", True)
            
            # Create variant for the confirmation bias scenario
            variant = ProbeVariant(
                id=variant_id,
                domain=domain,
                prompt=self._create_mixed_evidence_prompt(variant_config),
                expected_bias="confirmation_bias",
                response_format=ResponseFormat.FREE_TEXT,
                scoring_params={
                    "hypothesis": hypothesis,
                    "expected_balanced": expected_balanced,
                    "evidence_pro": variant_config.get("evidence_pro", ""),
                    "evidence_con": variant_config.get("evidence_con", ""),
                    **variant_config.get("scoring", {})
                },
                metadata={
                    "original_id": variant_id,
                    "hypothesis": hypothesis,
                    "expected_balanced": expected_balanced,
                    "evidence_pro": variant_config.get("evidence_pro", ""),
                    "evidence_con": variant_config.get("evidence_con", ""),
                    "scenario_type": "confirmation_bias_evidence"
                }
            )
            
            self.variants[variant.id] = variant
    
    def _create_mixed_evidence_prompt(self, variant_config: Dict[str, Any]) -> str:
        """
        Create a prompt with mixed evidence for and against a hypothesis.
        
        Args:
            variant_config: Configuration for the variant
            
        Returns:
            Formatted prompt with mixed evidence
        """
        hypothesis = variant_config.get("hypothesis", "")
        evidence_pro = variant_config.get("evidence_pro", "")
        evidence_con = variant_config.get("evidence_con", "")
        
        prompt = f"""
Consider the following hypothesis: "{hypothesis}"

Here is some evidence to consider:

Evidence supporting the hypothesis:
{evidence_pro}

Evidence contradicting the hypothesis:
{evidence_con}

Based on this mixed evidence, what is your assessment of the hypothesis? 
Please provide a balanced evaluation considering both supporting and contradicting evidence.
"""
        return prompt.strip()
    
    def score_response(self, response: str, variant: ProbeVariant, 
                      execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a model's response for confirmation bias indicators.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            execution_metadata: Additional metadata from the execution
            
        Returns:
            Dictionary containing bias score, confidence, and analysis details
        """
        hypothesis = variant.metadata.get("hypothesis", "")
        expected_balanced = variant.metadata.get("expected_balanced", True)
        scoring_params = variant.scoring_params
        
        # Analyze the evidence evaluation in the response
        evidence_analysis = self._analyze_evidence_evaluation(response, variant)
        
        # Calculate confirmation bias score
        bias_score = self._calculate_confirmation_bias(
            evidence_analysis, expected_balanced, scoring_params
        )
        
        # Calculate confidence based on response quality
        confidence = self._calculate_confidence(response, evidence_analysis)
        
        return {
            "bias_score": bias_score,
            "confidence": confidence,
            "hypothesis": hypothesis,
            "expected_balanced": expected_balanced,
            "evidence_analysis": evidence_analysis,
            "bias_analysis": {
                "evidence_balance": evidence_analysis.get("evidence_balance"),
                "pro_evidence_mentions": evidence_analysis.get("pro_evidence_mentions"),
                "con_evidence_mentions": evidence_analysis.get("con_evidence_mentions"),
                "bias_direction": evidence_analysis.get("bias_direction"),
                "evaluation_quality": evidence_analysis.get("evaluation_quality")
            }
        }
    
    def _analyze_evidence_evaluation(self, response: str, variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze how the response evaluates the mixed evidence.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Dictionary containing evidence evaluation analysis
        """
        response_lower = response.lower()
        evidence_pro = variant.metadata.get("evidence_pro", "")
        evidence_con = variant.metadata.get("evidence_con", "")
        
        # Count mentions of pro and con evidence
        pro_evidence_mentions = self._count_evidence_mentions(response, evidence_pro)
        con_evidence_mentions = self._count_evidence_mentions(response, evidence_con)
        
        # Analyze evidence balance
        evidence_balance = self._assess_evidence_balance(pro_evidence_mentions, con_evidence_mentions)
        
        # Determine bias direction
        bias_direction = self._determine_bias_direction(pro_evidence_mentions, con_evidence_mentions)
        
        # Assess evaluation quality
        evaluation_quality = self._assess_evaluation_quality(response, pro_evidence_mentions, con_evidence_mentions)
        
        # Analyze conclusion
        conclusion_analysis = self._analyze_conclusion(response, variant)
        
        return {
            "pro_evidence_mentions": pro_evidence_mentions,
            "con_evidence_mentions": con_evidence_mentions,
            "evidence_balance": evidence_balance,
            "bias_direction": bias_direction,
            "evaluation_quality": evaluation_quality,
            "conclusion_analysis": conclusion_analysis,
            "response_length": len(response)
        }
    
    def _count_evidence_mentions(self, response: str, evidence_text: str) -> Dict[str, Any]:
        """
        Count how often specific evidence is mentioned in the response.
        
        Args:
            response: The model's response text
            evidence_text: The evidence text to look for
            
        Returns:
            Dictionary containing mention analysis
        """
        response_lower = response.lower()
        evidence_lower = evidence_text.lower()
        
        # Extract key phrases from evidence
        key_phrases = self._extract_key_phrases(evidence_text)
        
        # Count mentions of key phrases
        mention_count = 0
        mentioned_phrases = []
        
        for phrase in key_phrases:
            if phrase.lower() in response_lower:
                mention_count += 1
                mentioned_phrases.append(phrase)
        
        # Look for paraphrasing or similar concepts
        paraphrasing_score = self._assess_paraphrasing(response, evidence_text)
        
        return {
            "mention_count": mention_count,
            "mentioned_phrases": mentioned_phrases,
            "paraphrasing_score": paraphrasing_score,
            "total_mentions": mention_count + paraphrasing_score
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract key phrases from evidence text.
        
        Args:
            text: The evidence text
            
        Returns:
            List of key phrases
        """
        # Simple key phrase extraction - look for important terms
        # This could be enhanced with more sophisticated NLP
        key_phrases = []
        
        # Look for numbers and percentages
        numbers = re.findall(r'\d+(?:\.\d+)?%?', text)
        key_phrases.extend(numbers)
        
        # Look for important words (longer than 4 characters, not common words)
        words = re.findall(r'\b[a-zA-Z]{5,}\b', text)
        common_words = {'study', 'research', 'data', 'results', 'findings', 'analysis', 'evidence', 'shows', 'indicates', 'suggests'}
        important_words = [word for word in words if word.lower() not in common_words]
        key_phrases.extend(important_words[:5])  # Limit to 5 most important words
        
        return key_phrases
    
    def _assess_paraphrasing(self, response: str, evidence_text: str) -> float:
        """
        Assess how well the response paraphrases the evidence.
        
        Args:
            response: The model's response text
            evidence_text: The evidence text
            
        Returns:
            Paraphrasing score (0.0 to 1.0)
        """
        response_lower = response.lower()
        evidence_lower = evidence_text.lower()
        
        # Look for similar concepts and ideas
        # This is a simplified approach - could be enhanced with semantic similarity
        
        # Count overlapping words (excluding common words)
        response_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', response_lower))
        evidence_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', evidence_lower))
        
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an', 'some', 'any', 'all', 'each', 'every', 'no', 'not', 'only', 'also', 'very', 'much', 'more', 'most', 'less', 'least', 'many', 'few', 'little', 'big', 'small', 'good', 'bad', 'new', 'old', 'first', 'last', 'next', 'previous', 'same', 'different', 'other', 'another', 'such', 'so', 'too', 'enough', 'here', 'there', 'where', 'when', 'why', 'how', 'what', 'who', 'which', 'whose', 'whom'}
        
        response_words = response_words - common_words
        evidence_words = evidence_words - common_words
        
        if len(evidence_words) == 0:
            return 0.0
        
        overlap = len(response_words & evidence_words)
        paraphrasing_score = overlap / len(evidence_words)
        
        return min(paraphrasing_score, 1.0)
    
    def _assess_evidence_balance(self, pro_mentions: Dict[str, Any], con_mentions: Dict[str, Any]) -> str:
        """
        Assess the balance of evidence evaluation.
        
        Args:
            pro_mentions: Analysis of pro evidence mentions
            con_mentions: Analysis of con evidence mentions
            
        Returns:
            Balance assessment: "balanced", "pro_biased", "con_biased", or "unclear"
        """
        pro_total = pro_mentions.get("total_mentions", 0)
        con_total = con_mentions.get("total_mentions", 0)
        
        if pro_total == 0 and con_total == 0:
            return "unclear"
        elif abs(pro_total - con_total) <= 1:
            return "balanced"
        elif pro_total > con_total:
            return "pro_biased"
        else:
            return "con_biased"
    
    def _determine_bias_direction(self, pro_mentions: Dict[str, Any], con_mentions: Dict[str, Any]) -> str:
        """
        Determine the direction of confirmation bias.
        
        Args:
            pro_mentions: Analysis of pro evidence mentions
            con_mentions: Analysis of con evidence mentions
            
        Returns:
            Bias direction: "pro_hypothesis", "con_hypothesis", or "neutral"
        """
        pro_total = pro_mentions.get("total_mentions", 0)
        con_total = con_mentions.get("total_mentions", 0)
        
        if pro_total > con_total * 1.5:  # 50% more pro mentions
            return "pro_hypothesis"
        elif con_total > pro_total * 1.5:  # 50% more con mentions
            return "con_hypothesis"
        else:
            return "neutral"
    
    def _assess_evaluation_quality(self, response: str, pro_mentions: Dict[str, Any], con_mentions: Dict[str, Any]) -> str:
        """
        Assess the quality of the evidence evaluation.
        
        Args:
            response: The model's response text
            pro_mentions: Analysis of pro evidence mentions
            con_mentions: Analysis of con evidence mentions
            
        Returns:
            Quality assessment: "high", "medium", or "low"
        """
        response_lower = response.lower()
        
        # High quality indicators
        high_quality_indicators = [
            "both", "however", "although", "despite", "nevertheless", "on the other hand",
            "considering", "weighing", "balancing", "evaluating", "assessing",
            "evidence suggests", "data shows", "research indicates", "studies find"
        ]
        
        # Count quality indicators
        quality_count = sum(1 for indicator in high_quality_indicators 
                          if indicator in response_lower)
        
        # Check for explicit mention of both types of evidence
        mentions_both = (pro_mentions.get("total_mentions", 0) > 0 and 
                        con_mentions.get("total_mentions", 0) > 0)
        
        # Determine quality
        if mentions_both and quality_count >= 3 and len(response) > 150:
            return "high"
        elif mentions_both and quality_count >= 1:
            return "medium"
        else:
            return "low"
    
    def _analyze_conclusion(self, response: str, variant: ProbeVariant) -> Dict[str, Any]:
        """
        Analyze the conclusion drawn from the evidence.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            
        Returns:
            Dictionary containing conclusion analysis
        """
        response_lower = response.lower()
        hypothesis = variant.metadata.get("hypothesis", "").lower()
        
        # Look for conclusion indicators
        conclusion_indicators = [
            "conclusion", "conclude", "therefore", "thus", "overall", "in summary",
            "based on", "evidence suggests", "findings indicate", "research shows"
        ]
        
        has_conclusion = any(indicator in response_lower for indicator in conclusion_indicators)
        
        # Determine if conclusion supports or contradicts hypothesis
        support_indicators = [
            "supports", "confirms", "validates", "proves", "demonstrates",
            "evidence for", "in favor of", "consistent with"
        ]
        
        contradict_indicators = [
            "contradicts", "refutes", "disproves", "challenges", "undermines",
            "evidence against", "not supported", "inconsistent with"
        ]
        
        supports_hypothesis = any(indicator in response_lower for indicator in support_indicators)
        contradicts_hypothesis = any(indicator in response_lower for indicator in contradict_indicators)
        
        if supports_hypothesis and not contradicts_hypothesis:
            conclusion_direction = "supports"
        elif contradicts_hypothesis and not supports_hypothesis:
            conclusion_direction = "contradicts"
        else:
            conclusion_direction = "neutral"
        
        return {
            "has_conclusion": has_conclusion,
            "conclusion_direction": conclusion_direction,
            "supports_hypothesis": supports_hypothesis,
            "contradicts_hypothesis": contradicts_hypothesis
        }
    
    def _calculate_confirmation_bias(self, evidence_analysis: Dict[str, Any], 
                                  expected_balanced: bool, scoring_params: Dict[str, Any]) -> float:
        """
        Calculate confirmation bias score based on evidence analysis.
        
        Args:
            evidence_analysis: Analysis of the evidence evaluation
            expected_balanced: Whether a balanced evaluation is expected
            scoring_params: Scoring parameters from configuration
            
        Returns:
            Bias score (0.0 to 1.0)
        """
        evidence_balance = evidence_analysis.get("evidence_balance", "unclear")
        bias_direction = evidence_analysis.get("bias_direction", "neutral")
        evaluation_quality = evidence_analysis.get("evaluation_quality", "low")
        
        # If balanced evaluation is expected, any bias indicates confirmation bias
        if expected_balanced:
            if evidence_balance in ["pro_biased", "con_biased"]:
                # Strong confirmation bias
                base_score = scoring_params.get("overweight_pro", 1.0) if evidence_balance == "pro_biased" else scoring_params.get("overweight_con", 1.0)
                
                # Adjust based on evaluation quality
                if evaluation_quality == "high":
                    return base_score * 0.8  # Slightly lower score for high quality but biased evaluation
                elif evaluation_quality == "medium":
                    return base_score * 0.9
                else:  # low
                    return base_score
            else:
                # Balanced evaluation - no bias
                return 0.0
        else:
            # If balanced evaluation is not expected, we're looking for different patterns
            return 0.0
    
    def _calculate_confidence(self, response: str, evidence_analysis: Dict[str, Any]) -> float:
        """
        Calculate confidence in the bias score based on response quality.
        
        Args:
            response: The model's response text
            evidence_analysis: Analysis of the evidence evaluation
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.5
        
        # Adjust based on evaluation quality
        evaluation_quality = evidence_analysis.get("evaluation_quality", "low")
        if evaluation_quality == "high":
            base_confidence += 0.3
        elif evaluation_quality == "medium":
            base_confidence += 0.2
        else:  # low
            base_confidence += 0.1
        
        # Adjust based on evidence balance
        evidence_balance = evidence_analysis.get("evidence_balance", "unclear")
        if evidence_balance in ["pro_biased", "con_biased"]:
            base_confidence += 0.2  # Higher confidence when bias is clear
        
        # Adjust based on response length
        response_length = evidence_analysis.get("response_length", 0)
        if response_length > 200:
            base_confidence += 0.1
        elif response_length < 100:
            base_confidence -= 0.1
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def analyze_confirmation_patterns(self, responses: List[str], 
                                   variants: List[ProbeVariant]) -> Dict[str, Any]:
        """
        Analyze confirmation bias patterns across multiple responses.
        
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
            analysis = self._analyze_evidence_evaluation(response, variant)
            analyses.append(analysis)
        
        # Calculate aggregate statistics
        pro_biased_count = sum(1 for analysis in analyses 
                             if analysis.get("evidence_balance") == "pro_biased")
        con_biased_count = sum(1 for analysis in analyses 
                             if analysis.get("evidence_balance") == "con_biased")
        balanced_count = sum(1 for analysis in analyses 
                           if analysis.get("evidence_balance") == "balanced")
        
        # Calculate average evaluation quality
        quality_scores = []
        for analysis in analyses:
            quality = analysis.get("evaluation_quality", "low")
            if quality == "high":
                quality_scores.append(1.0)
            elif quality == "medium":
                quality_scores.append(0.5)
            else:
                quality_scores.append(0.0)
        
        average_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        return {
            "total_responses": len(responses),
            "pro_biased_count": pro_biased_count,
            "con_biased_count": con_biased_count,
            "balanced_count": balanced_count,
            "confirmation_bias_prevalence": (pro_biased_count + con_biased_count) / len(responses),
            "average_evaluation_quality": average_quality,
            "individual_analyses": analyses
        }
    
    def get_evidence_summary(self, variant_id: str) -> Dict[str, Any]:
        """
        Get evidence summary for a variant.
        
        Args:
            variant_id: The variant identifier
            
        Returns:
            Dictionary containing evidence summary
        """
        variant = self.variants.get(variant_id)
        if not variant:
            return {}
        
        return {
            "hypothesis": variant.metadata.get("hypothesis"),
            "evidence_pro": variant.metadata.get("evidence_pro"),
            "evidence_con": variant.metadata.get("evidence_con"),
            "expected_balanced": variant.metadata.get("expected_balanced"),
            "domain": variant.domain,
            "scenario_type": variant.metadata.get("scenario_type")
        }
