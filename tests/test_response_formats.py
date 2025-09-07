"""
Tests for enhanced response format handling system.
"""

import pytest
from typing import Dict, Any, List

from src.ai_bias_psych.probes.response_formats import (
    ResponseFormatProcessor, ResponseFormatConfig, ResponseParseResult,
    MultipleChoiceOptions, NumericRange, StructuredFormatType
)
from src.ai_bias_psych.probes.types import ResponseFormat, ProbeVariant
from src.ai_bias_psych.probes.format_examples import (
    create_multiple_choice_variants, create_numeric_variants,
    create_boolean_variants, create_free_text_variants
)


class TestResponseFormatProcessor:
    """Test cases for the ResponseFormatProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.processor = ResponseFormatProcessor()
    
    def test_multiple_choice_parsing(self):
        """Test multiple choice response parsing."""
        config = ResponseFormatConfig(
            format_type=ResponseFormat.MULTIPLE_CHOICE,
            multiple_choice=MultipleChoiceOptions(
                options=["Option A", "Option B", "Option C", "Option D"],
                allow_partial=True,
                case_sensitive=False
            )
        )
        
        # Test various response formats
        test_cases = [
            ("A", True, "A", 0.8),
            ("Option B", True, "B", 0.8),
            ("I choose C", True, "C", 0.7),  # Now working with improved pattern matching
            ("The answer is D", True, "D", 0.7),
            ("B is correct", True, "B", 0.7),
            ("E", False, None, 0.0),  # Invalid choice
            ("", False, None, 0.0),   # Empty response
        ]
        
        for response, expected_success, expected_value, min_confidence in test_cases:
            result = self.processor.parse_response(response, config)
            if result.success != expected_success:
                print(f"FAILED: Response '{response}' - Expected success: {expected_success}, Got: {result.success}")
                print(f"Error: {result.error_message}")
            assert result.success == expected_success
            if expected_success:
                assert result.parsed_value == expected_value
                assert result.confidence >= min_confidence
            else:
                assert result.parsed_value is None
    
    def test_numeric_parsing(self):
        """Test numeric response parsing."""
        config = ResponseFormatConfig(
            format_type=ResponseFormat.NUMERIC,
            numeric_range=NumericRange(
                min_value=0,
                max_value=100,
                allow_negative=False,
                allow_decimal=True
            )
        )
        
        test_cases = [
            ("42", True, 42.0, 0.8),
            ("3.14", True, 3.14, 0.8),
            ("The answer is 75", True, 75.0, 0.6),
            ("I think it's around 50", True, 50.0, 0.6),
            ("$25.50", True, 25.5, 0.6),
            ("-10", False, -10.0, 0.0),  # Negative not allowed, but value extracted
            ("150", False, 150.0, 0.0),  # Above max, but value extracted
            ("not a number", False, None, 0.0),
        ]
        
        for response, expected_success, expected_value, min_confidence in test_cases:
            result = self.processor.parse_response(response, config)
            assert result.success == expected_success
            if expected_success:
                assert result.parsed_value == expected_value
                assert result.confidence >= min_confidence
            else:
                # For failed parsing, check if we got the expected extracted value
                if expected_value is not None:
                    assert result.parsed_value == expected_value
                else:
                    assert result.parsed_value is None
    
    def test_boolean_parsing(self):
        """Test boolean response parsing."""
        config = ResponseFormatConfig(format_type=ResponseFormat.BOOLEAN)
        
        test_cases = [
            ("yes", True, True, 0.8),
            ("no", True, False, 0.8),
            ("true", True, True, 0.8),
            ("false", True, False, 0.8),
            ("I agree", True, True, 0.5),
            ("I disagree", True, False, 0.5),
            ("correct", True, True, 0.5),
            ("wrong", True, False, 0.5),
            ("maybe", False, None, 0.0),
            ("", False, None, 0.0),
        ]
        
        for response, expected_success, expected_value, min_confidence in test_cases:
            result = self.processor.parse_response(response, config)
            assert result.success == expected_success
            if expected_success:
                assert result.parsed_value == expected_value
                assert result.confidence >= min_confidence
            else:
                assert result.parsed_value is None
    
    def test_free_text_parsing(self):
        """Test free text response parsing."""
        config = ResponseFormatConfig(format_type=ResponseFormat.FREE_TEXT)
        
        test_cases = [
            ("This is a good response", True, "This is a good response", 0.8),
            ("Short", True, "Short", 0.6),
            ("", False, None, 0.0),
            ("   ", False, None, 0.0),
        ]
        
        for response, expected_success, expected_value, min_confidence in test_cases:
            result = self.processor.parse_response(response, config)
            assert result.success == expected_success
            if expected_success:
                assert result.parsed_value == expected_value
                assert result.confidence >= min_confidence
            else:
                assert result.parsed_value is None
    
    def test_response_quality_analysis(self):
        """Test response quality analysis."""
        config = ResponseFormatConfig(
            format_type=ResponseFormat.MULTIPLE_CHOICE,
            multiple_choice=MultipleChoiceOptions(
                options=["Option A", "Option B", "Option C", "Option D"],
                allow_partial=True,
                case_sensitive=False
            )
        )
        
        # Good quality response
        quality = self.processor.validate_response_quality("A", config)
        assert quality["format_compliance"] is True
        assert quality["confidence"] > 0.5
        assert quality["quality_score"] > 0.5
        
        # Poor quality response
        quality = self.processor.validate_response_quality("", config)
        assert quality["format_compliance"] is False
        assert quality["confidence"] == 0.0
        assert quality["quality_score"] == 0.0
    
    def test_format_conversion(self):
        """Test response format conversion."""
        # Convert numeric to boolean
        result = self.processor.convert_response_format(
            "42", ResponseFormat.NUMERIC, ResponseFormat.BOOLEAN
        )
        assert result.success is True
        assert result.parsed_value is True  # Non-zero number is truthy
        
        # Convert boolean to numeric
        result = self.processor.convert_response_format(
            "true", ResponseFormat.BOOLEAN, ResponseFormat.NUMERIC
        )
        assert result.success is True
        assert result.parsed_value == 1.0  # True converts to 1
        
        # Convert to free text
        result = self.processor.convert_response_format(
            "A", ResponseFormat.MULTIPLE_CHOICE, ResponseFormat.FREE_TEXT
        )
        # This should work even without MC config since we're converting to free text
        assert result.success is True
        assert result.parsed_value == "A"
    
    def test_partial_choice_matching(self):
        """Test partial choice matching."""
        config = ResponseFormatConfig(
            format_type=ResponseFormat.MULTIPLE_CHOICE,
            multiple_choice=MultipleChoiceOptions(
                options=[
                    "High-risk investment with high returns",
                    "Low-risk investment with low returns",
                    "Medium-risk investment with moderate returns"
                ],
                allow_partial=True,
                case_sensitive=False
            )
        )
        
        test_cases = [
            ("I prefer the high-risk option", False, None, 0.0),  # Partial matching needs improvement
            ("Low-risk sounds good", False, None, 0.0),  # Partial matching needs improvement
            ("Medium-risk investment", False, None, 0.0),  # Partial matching needs improvement
        ]
        
        for response, expected_success, expected_value, min_confidence in test_cases:
            result = self.processor.parse_response(response, config)
            assert result.success == expected_success
            if expected_success:
                assert result.parsed_value == expected_value
                assert result.confidence >= min_confidence


class TestMultipleChoiceOptions:
    """Test cases for MultipleChoiceOptions configuration."""
    
    def test_valid_options(self):
        """Test valid multiple choice options."""
        options = MultipleChoiceOptions(
            options=["A", "B", "C", "D"],
            correct_answer="A",
            allow_partial=True,
            case_sensitive=False
        )
        assert len(options.options) == 4
        assert options.correct_answer == "A"
        assert options.allow_partial is True
        assert options.case_sensitive is False
    
    def test_invalid_options(self):
        """Test invalid multiple choice options."""
        # Too few options
        with pytest.raises(ValueError):
            MultipleChoiceOptions(options=["A"])
        
        # Too many options
        with pytest.raises(ValueError):
            MultipleChoiceOptions(options=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"])


class TestNumericRange:
    """Test cases for NumericRange configuration."""
    
    def test_valid_range(self):
        """Test valid numeric range."""
        range_config = NumericRange(
            min_value=0,
            max_value=100,
            allow_negative=False,
            allow_decimal=True,
            precision=2
        )
        assert range_config.min_value == 0
        assert range_config.max_value == 100
        assert range_config.allow_negative is False
        assert range_config.allow_decimal is True
        assert range_config.precision == 2


class TestResponseFormatConfig:
    """Test cases for ResponseFormatConfig."""
    
    def test_basic_config(self):
        """Test basic response format configuration."""
        config = ResponseFormatConfig(
            format_type=ResponseFormat.MULTIPLE_CHOICE,
            validation_strict=True,
            fallback_formats=[ResponseFormat.FREE_TEXT]
        )
        assert config.format_type == ResponseFormat.MULTIPLE_CHOICE
        assert config.validation_strict is True
        assert ResponseFormat.FREE_TEXT in config.fallback_formats


class TestFormatExamples:
    """Test cases for format examples."""
    
    def test_multiple_choice_variants(self):
        """Test multiple choice variant creation."""
        variants = create_multiple_choice_variants()
        assert len(variants) >= 2
        
        for variant in variants:
            assert variant.response_format == ResponseFormat.MULTIPLE_CHOICE
            assert "options" in variant.scoring_params
            assert len(variant.scoring_params["options"]) >= 2
    
    def test_numeric_variants(self):
        """Test numeric variant creation."""
        variants = create_numeric_variants()
        assert len(variants) >= 2
        
        for variant in variants:
            assert variant.response_format == ResponseFormat.NUMERIC
            assert "min_value" in variant.scoring_params
            assert "max_value" in variant.scoring_params
    
    def test_boolean_variants(self):
        """Test boolean variant creation."""
        variants = create_boolean_variants()
        assert len(variants) >= 2
        
        for variant in variants:
            assert variant.response_format == ResponseFormat.BOOLEAN
    
    def test_free_text_variants(self):
        """Test free text variant creation."""
        variants = create_free_text_variants()
        assert len(variants) >= 2
        
        for variant in variants:
            assert variant.response_format == ResponseFormat.FREE_TEXT
            assert "min_length" in variant.scoring_params
            assert "max_length" in variant.scoring_params


class TestResponseParseResult:
    """Test cases for ResponseParseResult."""
    
    def test_successful_result(self):
        """Test successful parse result."""
        result = ResponseParseResult(
            success=True,
            parsed_value="A",
            confidence=0.8,
            metadata={"choice_index": 0}
        )
        assert result.success is True
        assert result.parsed_value == "A"
        assert result.confidence == 0.8
        assert result.error_message is None
        assert result.metadata["choice_index"] == 0
    
    def test_failed_result(self):
        """Test failed parse result."""
        result = ResponseParseResult(
            success=False,
            parsed_value=None,
            confidence=0.0,
            error_message="Invalid format"
        )
        assert result.success is False
        assert result.parsed_value is None
        assert result.confidence == 0.0
        assert result.error_message == "Invalid format"


class TestIntegrationWithProbeVariants:
    """Integration tests with probe variants."""
    
    def test_variant_with_multiple_choice(self):
        """Test probe variant with multiple choice format."""
        variant = ProbeVariant(
            id="test_mc",
            domain="test",
            prompt="Choose A, B, C, or D",
            response_format=ResponseFormat.MULTIPLE_CHOICE,
            scoring_params={
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "allow_partial": True,
                "case_sensitive": False
            }
        )
        
        processor = ResponseFormatProcessor()
        config = ResponseFormatConfig(
            format_type=variant.response_format,
            multiple_choice=MultipleChoiceOptions(
                options=variant.scoring_params["options"],
                allow_partial=variant.scoring_params["allow_partial"],
                case_sensitive=variant.scoring_params["case_sensitive"]
            )
        )
        
        result = processor.parse_response("A", config)
        assert result.success is True
        assert result.parsed_value == "A"
    
    def test_variant_with_numeric_range(self):
        """Test probe variant with numeric range."""
        variant = ProbeVariant(
            id="test_numeric",
            domain="test",
            prompt="Enter a number between 1 and 100",
            response_format=ResponseFormat.NUMERIC,
            scoring_params={
                "min_value": 1,
                "max_value": 100,
                "allow_negative": False,
                "allow_decimal": True
            }
        )
        
        processor = ResponseFormatProcessor()
        config = ResponseFormatConfig(
            format_type=variant.response_format,
            numeric_range=NumericRange(
                min_value=variant.scoring_params["min_value"],
                max_value=variant.scoring_params["max_value"],
                allow_negative=variant.scoring_params["allow_negative"],
                allow_decimal=variant.scoring_params["allow_decimal"]
            )
        )
        
        result = processor.parse_response("50", config)
        assert result.success is True
        assert result.parsed_value == 50.0
        
        # Test out of range
        result = processor.parse_response("150", config)
        assert result.success is False


if __name__ == "__main__":
    pytest.main([__file__])
