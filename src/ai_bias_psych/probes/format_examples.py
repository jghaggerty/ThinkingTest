"""
Example probe variants demonstrating enhanced response format support.

This module provides example configurations for different response formats
to show how the enhanced response format system can be used.
"""

from typing import Dict, Any, List
from .types import ProbeVariant, ResponseFormat


def create_multiple_choice_variants() -> List[ProbeVariant]:
    """Create example multiple choice probe variants."""
    variants = []
    
    # Basic multiple choice
    variants.append(ProbeVariant(
        id="mc_basic_health",
        domain="health",
        prompt="""A new medical treatment has a 90% success rate but costs $10,000.
An alternative treatment has a 70% success rate but costs $2,000.
Which treatment would you recommend?

A) The expensive treatment with 90% success rate
B) The cheaper treatment with 70% success rate
C) Neither treatment
D) Need more information""",
        expected_bias="cost_anchoring",
        response_format=ResponseFormat.MULTIPLE_CHOICE,
        scoring_params={
            "options": [
                "The expensive treatment with 90% success rate",
                "The cheaper treatment with 70% success rate",
                "Neither treatment",
                "Need more information"
            ],
            "allow_partial": True,
            "case_sensitive": False,
            "correct_answer": "D"  # Need more information is most rational
        }
    ))
    
    # Multiple choice with partial matching
    variants.append(ProbeVariant(
        id="mc_partial_finance",
        domain="finance",
        prompt="""You have $10,000 to invest. Which option do you choose?

A) High-risk stock with potential 50% return
B) Medium-risk bond with 5% guaranteed return  
C) Low-risk savings account with 2% return
D) Diversified portfolio with 8% expected return""",
        expected_bias="risk_preference",
        response_format=ResponseFormat.MULTIPLE_CHOICE,
        scoring_params={
            "options": [
                "High-risk stock with potential 50% return",
                "Medium-risk bond with 5% guaranteed return",
                "Low-risk savings account with 2% return", 
                "Diversified portfolio with 8% expected return"
            ],
            "allow_partial": True,
            "case_sensitive": False
        }
    ))
    
    return variants


def create_numeric_variants() -> List[ProbeVariant]:
    """Create example numeric probe variants."""
    variants = []
    
    # Anchoring bias with numeric response
    variants.append(ProbeVariant(
        id="num_anchoring_estimation",
        domain="general",
        prompt="""The population of Australia is approximately 25 million people.
Now, please estimate the population of New Zealand. 
Provide your estimate as a number.""",
        expected_bias="anchoring",
        response_format=ResponseFormat.NUMERIC,
        scoring_params={
            "min_value": 0,
            "max_value": 100000000,  # 100 million
            "allow_negative": False,
            "allow_decimal": False,
            "correct_answer": 5000000  # Approximately 5 million
        }
    ))
    
    # Confidence interval estimation
    variants.append(ProbeVariant(
        id="num_confidence_interval",
        domain="statistics",
        prompt="""A survey of 1000 people found that 60% support a new policy.
What is the 95% confidence interval for this percentage?
Please provide the lower bound of the confidence interval as a percentage.""",
        expected_bias="overconfidence",
        response_format=ResponseFormat.NUMERIC,
        scoring_params={
            "min_value": 0,
            "max_value": 100,
            "allow_negative": False,
            "allow_decimal": True,
            "precision": 1
        }
    ))
    
    return variants


def create_boolean_variants() -> List[ProbeVariant]:
    """Create example boolean probe variants."""
    variants = []
    
    # Confirmation bias test
    variants.append(ProbeVariant(
        id="bool_confirmation_bias",
        domain="psychology",
        prompt="""A study found that people who exercise regularly are more likely to be successful.
Do you agree with this statement? Answer with Yes or No.""",
        expected_bias="confirmation_bias",
        response_format=ResponseFormat.BOOLEAN,
        scoring_params={
            "correct_answer": None,  # No objectively correct answer
            "bias_indicator": "Agreeing without considering alternative explanations"
        }
    ))
    
    # Base rate neglect
    variants.append(ProbeVariant(
        id="bool_base_rate",
        domain="statistics",
        prompt="""In a city, 1% of people have a rare disease. A test for the disease is 99% accurate.
If someone tests positive, is it more likely than not that they have the disease?
Answer with Yes or No.""",
        expected_bias="base_rate_neglect",
        response_format=ResponseFormat.BOOLEAN,
        scoring_params={
            "correct_answer": False,  # Due to low base rate, false positive rate is high
            "explanation": "With 1% base rate, even with 99% accuracy, false positives dominate"
        }
    ))
    
    return variants


def create_free_text_variants() -> List[ProbeVariant]:
    """Create example free text probe variants."""
    variants = []
    
    # Framing effect with free text
    variants.append(ProbeVariant(
        id="text_framing_positive",
        domain="health",
        prompt="""A new medical procedure has a 90% survival rate.
Please explain your thoughts about this procedure and whether you would recommend it.""",
        expected_bias="framing_effect",
        response_format=ResponseFormat.FREE_TEXT,
        scoring_params={
            "min_length": 20,
            "max_length": 500,
            "keywords": ["safe", "effective", "recommend", "good", "positive"],
            "bias_indicators": ["overly positive", "ignores 10% mortality"]
        }
    ))
    
    # Availability heuristic
    variants.append(ProbeVariant(
        id="text_availability_heuristic",
        domain="risk_assessment",
        prompt="""Recent news has been reporting many shark attacks at beaches.
Please describe your thoughts about the safety of swimming at the beach.""",
        expected_bias="availability_heuristic",
        response_format=ResponseFormat.FREE_TEXT,
        scoring_params={
            "min_length": 30,
            "max_length": 400,
            "bias_indicators": ["overestimates shark attack risk", "ignores base rates"],
            "rational_indicators": ["considers actual statistics", "mentions other risks"]
        }
    ))
    
    return variants


def create_mixed_format_variants() -> List[ProbeVariant]:
    """Create variants that can handle multiple response formats."""
    variants = []
    
    # Prospect theory with multiple choice and free text
    variants.append(ProbeVariant(
        id="mixed_prospect_theory",
        domain="decision_making",
        prompt="""You are given two options:

Option A: Receive $50 guaranteed
Option B: 50% chance to receive $100, 50% chance to receive $0

Which option do you choose? (A or B)
Then explain your reasoning in 2-3 sentences.""",
        expected_bias="prospect_theory",
        response_format=ResponseFormat.FREE_TEXT,  # Can handle both choice and explanation
        scoring_params={
            "extract_choice": True,  # Extract A or B from free text
            "analyze_reasoning": True,
            "expected_choice": "A",  # Risk-averse choice in gains
            "reasoning_keywords": ["guaranteed", "certain", "safe", "risk"]
        }
    ))
    
    return variants


def get_all_format_examples() -> Dict[str, List[ProbeVariant]]:
    """Get all example variants organized by format type."""
    return {
        "multiple_choice": create_multiple_choice_variants(),
        "numeric": create_numeric_variants(),
        "boolean": create_boolean_variants(),
        "free_text": create_free_text_variants(),
        "mixed_format": create_mixed_format_variants()
    }


def create_format_demo_config() -> Dict[str, Any]:
    """Create a configuration demonstrating all response formats."""
    return {
        "format_demo": {
            "name": "Response Format Demonstration",
            "description": "Demonstrates all supported response formats",
            "variants": [
                {
                    "id": "demo_mc",
                    "domain": "demo",
                    "prompt": "Choose A, B, C, or D",
                    "response_format": "multiple_choice",
                    "scoring": {
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "allow_partial": True
                    }
                },
                {
                    "id": "demo_numeric",
                    "domain": "demo", 
                    "prompt": "Enter a number between 1 and 100",
                    "response_format": "numeric",
                    "scoring": {
                        "min_value": 1,
                        "max_value": 100,
                        "allow_decimal": True
                    }
                },
                {
                    "id": "demo_boolean",
                    "domain": "demo",
                    "prompt": "Answer Yes or No",
                    "response_format": "boolean"
                },
                {
                    "id": "demo_text",
                    "domain": "demo",
                    "prompt": "Write a short explanation",
                    "response_format": "free_text",
                    "scoring": {
                        "min_length": 10,
                        "max_length": 200
                    }
                }
            ]
        }
    }
