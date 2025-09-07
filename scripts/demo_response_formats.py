#!/usr/bin/env python3
"""
Demonstration script for enhanced response format handling.

This script shows how to use the enhanced response format system to handle
different types of probe responses with advanced parsing and validation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_bias_psych.probes import (
    ResponseFormatProcessor, ResponseFormatConfig, ResponseFormat,
    MultipleChoiceOptions, NumericRange, StructuredFormatType,
    create_multiple_choice_variants, create_numeric_variants,
    create_boolean_variants, create_free_text_variants
)


def demo_multiple_choice_parsing():
    """Demonstrate multiple choice response parsing."""
    print("=== Multiple Choice Response Parsing Demo ===\n")
    
    # Create processor with multiple choice configuration
    config = ResponseFormatConfig(
        format_type=ResponseFormat.MULTIPLE_CHOICE,
        multiple_choice=MultipleChoiceOptions(
            options=[
                "High-risk investment with high returns",
                "Low-risk investment with low returns", 
                "Medium-risk investment with moderate returns",
                "No investment at all"
            ],
            allow_partial=True,
            case_sensitive=False
        )
    )
    
    processor = ResponseFormatProcessor(config)
    
    # Test various response formats
    test_responses = [
        "A",
        "I choose option B",
        "The high-risk investment sounds good",
        "I prefer the low-risk option",
        "Medium-risk investment",
        "I don't want to invest",
        "E",  # Invalid choice
        "Maybe",  # Unclear response
    ]
    
    for response in test_responses:
        result = processor.parse_response(response)
        print(f"Response: '{response}'")
        print(f"  Success: {result.success}")
        print(f"  Parsed Value: {result.parsed_value}")
        print(f"  Confidence: {result.confidence:.2f}")
        if result.error_message:
            print(f"  Error: {result.error_message}")
        print()


def demo_numeric_parsing():
    """Demonstrate numeric response parsing."""
    print("=== Numeric Response Parsing Demo ===\n")
    
    # Create processor with numeric configuration
    config = ResponseFormatConfig(
        format_type=ResponseFormat.NUMERIC,
        numeric_range=NumericRange(
            min_value=0,
            max_value=100,
            allow_negative=False,
            allow_decimal=True,
            precision=2
        )
    )
    
    processor = ResponseFormatProcessor(config)
    
    # Test various numeric response formats
    test_responses = [
        "42",
        "3.14",
        "The answer is 75",
        "I think it's around 50",
        "$25.50",
        "About 80%",
        "-10",  # Negative not allowed
        "150",  # Above max
        "not a number",
        "The population is approximately 5 million",  # Should extract 5
    ]
    
    for response in test_responses:
        result = processor.parse_response(response)
        print(f"Response: '{response}'")
        print(f"  Success: {result.success}")
        print(f"  Parsed Value: {result.parsed_value}")
        print(f"  Confidence: {result.confidence:.2f}")
        if result.error_message:
            print(f"  Error: {result.error_message}")
        print()


def demo_boolean_parsing():
    """Demonstrate boolean response parsing."""
    print("=== Boolean Response Parsing Demo ===\n")
    
    # Create processor with boolean configuration
    config = ResponseFormatConfig(format_type=ResponseFormat.BOOLEAN)
    processor = ResponseFormatProcessor(config)
    
    # Test various boolean response formats
    test_responses = [
        "yes",
        "no",
        "true",
        "false",
        "I agree",
        "I disagree",
        "correct",
        "wrong",
        "absolutely",
        "definitely not",
        "maybe",  # Unclear
        "I'm not sure",  # Unclear
    ]
    
    for response in test_responses:
        result = processor.parse_response(response)
        print(f"Response: '{response}'")
        print(f"  Success: {result.success}")
        print(f"  Parsed Value: {result.parsed_value}")
        print(f"  Confidence: {result.confidence:.2f}")
        if result.error_message:
            print(f"  Error: {result.error_message}")
        print()


def demo_free_text_analysis():
    """Demonstrate free text response analysis."""
    print("=== Free Text Response Analysis Demo ===\n")
    
    # Create processor with free text configuration
    config = ResponseFormatConfig(format_type=ResponseFormat.FREE_TEXT)
    processor = ResponseFormatProcessor(config)
    
    # Test various free text responses
    test_responses = [
        "This is a well-formed response with proper punctuation and capitalization.",
        "short",
        "This response is quite long and contains multiple sentences. It demonstrates good writing quality with proper grammar and punctuation. The response provides detailed analysis and reasoning.",
        "This response has some issues with capitalization and punctuation but is generally understandable",
        "",  # Empty response
    ]
    
    for response in test_responses:
        result = processor.parse_response(response)
        quality = processor.validate_response_quality(response)
        
        print(f"Response: '{response[:50]}{'...' if len(response) > 50 else ''}'")
        print(f"  Parse Success: {result.success}")
        print(f"  Parse Confidence: {result.confidence:.2f}")
        print(f"  Quality Score: {quality['quality_score']:.2f}")
        print(f"  Word Count: {quality['word_count']}")
        print(f"  Has Punctuation: {quality['has_punctuation']}")
        print(f"  Has Capitalization: {quality['has_capitalization']}")
        print()


def demo_format_conversion():
    """Demonstrate response format conversion."""
    print("=== Response Format Conversion Demo ===\n")
    
    processor = ResponseFormatProcessor()
    
    # Test conversions
    conversions = [
        ("42", ResponseFormat.NUMERIC, ResponseFormat.BOOLEAN),
        ("0", ResponseFormat.NUMERIC, ResponseFormat.BOOLEAN),
        ("true", ResponseFormat.BOOLEAN, ResponseFormat.NUMERIC),
        ("false", ResponseFormat.BOOLEAN, ResponseFormat.NUMERIC),
        ("A", ResponseFormat.MULTIPLE_CHOICE, ResponseFormat.FREE_TEXT),
        ("yes", ResponseFormat.BOOLEAN, ResponseFormat.FREE_TEXT),
    ]
    
    for response, from_format, to_format in conversions:
        result = processor.convert_response_format(response, from_format, to_format)
        print(f"Converting '{response}' from {from_format.value} to {to_format.value}")
        print(f"  Success: {result.success}")
        print(f"  Converted Value: {result.parsed_value}")
        print(f"  Confidence: {result.confidence:.2f}")
        if result.error_message:
            print(f"  Error: {result.error_message}")
        print()


def demo_format_examples():
    """Demonstrate format examples from the examples module."""
    print("=== Format Examples Demo ===\n")
    
    # Get example variants
    mc_variants = create_multiple_choice_variants()
    numeric_variants = create_numeric_variants()
    boolean_variants = create_boolean_variants()
    text_variants = create_free_text_variants()
    
    print(f"Multiple Choice Variants: {len(mc_variants)}")
    for variant in mc_variants[:2]:  # Show first 2
        print(f"  - {variant.id}: {variant.domain}")
        print(f"    Options: {len(variant.scoring_params.get('options', []))}")
    
    print(f"\nNumeric Variants: {len(numeric_variants)}")
    for variant in numeric_variants[:2]:  # Show first 2
        print(f"  - {variant.id}: {variant.domain}")
        print(f"    Range: {variant.scoring_params.get('min_value')} - {variant.scoring_params.get('max_value')}")
    
    print(f"\nBoolean Variants: {len(boolean_variants)}")
    for variant in boolean_variants[:2]:  # Show first 2
        print(f"  - {variant.id}: {variant.domain}")
    
    print(f"\nFree Text Variants: {len(text_variants)}")
    for variant in text_variants[:2]:  # Show first 2
        print(f"  - {variant.id}: {variant.domain}")
        print(f"    Length: {variant.scoring_params.get('min_length')} - {variant.scoring_params.get('max_length')}")


def demo_advanced_parsing():
    """Demonstrate advanced parsing features."""
    print("=== Advanced Parsing Features Demo ===\n")
    
    # Test partial matching
    config = ResponseFormatConfig(
        format_type=ResponseFormat.MULTIPLE_CHOICE,
        multiple_choice=MultipleChoiceOptions(
            options=[
                "High-risk investment with potential 50% return",
                "Low-risk investment with 2% guaranteed return",
                "Medium-risk investment with 8% expected return"
            ],
            allow_partial=True,
            case_sensitive=False
        )
    )
    
    processor = ResponseFormatProcessor(config)
    
    partial_responses = [
        "I prefer the high-risk option",
        "Low-risk sounds good to me",
        "The medium-risk investment seems reasonable",
        "High returns are attractive",
        "I want something safe and low-risk",
    ]
    
    print("Partial Matching Examples:")
    for response in partial_responses:
        result = processor.parse_response(response)
        print(f"  '{response}' -> {result.parsed_value} (confidence: {result.confidence:.2f})")
    
    print("\nQuality Analysis Examples:")
    quality_responses = [
        "A",  # Good multiple choice
        "I choose option A because it seems like the best choice.",  # Verbose but clear
        "Maybe A or B, I'm not sure",  # Unclear
        "The answer is definitely A, no question about it!",  # Very confident
    ]
    
    for response in quality_responses:
        quality = processor.validate_response_quality(response, config)
        print(f"  '{response}' -> Quality Score: {quality['quality_score']:.2f}")


if __name__ == "__main__":
    print("AI Bias Psychologist - Enhanced Response Formats Demo\n")
    print("=" * 60)
    
    try:
        demo_multiple_choice_parsing()
        demo_numeric_parsing()
        demo_boolean_parsing()
        demo_free_text_analysis()
        demo_format_conversion()
        demo_format_examples()
        demo_advanced_parsing()
        
        print("=" * 60)
        print("Demo completed successfully!")
        print("\nThe enhanced response format system provides:")
        print("• Advanced parsing for multiple choice, numeric, boolean, and free text")
        print("• Partial matching and fuzzy recognition")
        print("• Response quality analysis and scoring")
        print("• Format conversion capabilities")
        print("• Configurable validation rules and constraints")
        print("• Comprehensive error handling and confidence scoring")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
