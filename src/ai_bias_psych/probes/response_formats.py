"""
Comprehensive response format handling for bias probes.

This module provides advanced response format processing, validation, and conversion
capabilities for different types of probe responses including multiple-choice,
free-text, numeric, boolean, and structured formats.
"""

import re
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field, field_validator
import logging

from .types import ResponseFormat


class StructuredFormatType(str, Enum):
    """Types of structured response formats."""
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    CSV = "csv"
    KEY_VALUE = "key_value"


@dataclass
class ResponseParseResult:
    """Result of parsing a response in a specific format."""
    success: bool
    parsed_value: Any
    confidence: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MultipleChoiceOptions(BaseModel):
    """Configuration for multiple choice questions."""
    options: List[str] = Field(..., description="List of choice options")
    correct_answer: Optional[str] = Field(None, description="Correct answer if known")
    allow_partial: bool = Field(False, description="Allow partial matches")
    case_sensitive: bool = Field(False, description="Case sensitive matching")

    @field_validator('options')
    @classmethod
    def validate_options(cls, v):
        if len(v) < 2:
            raise ValueError("Must have at least 2 options")
        if len(v) > 10:
            raise ValueError("Too many options (max 10)")
        return v


class NumericRange(BaseModel):
    """Configuration for numeric response validation."""
    min_value: Optional[float] = Field(None, description="Minimum allowed value")
    max_value: Optional[float] = Field(None, description="Maximum allowed value")
    allow_negative: bool = Field(True, description="Allow negative numbers")
    allow_decimal: bool = Field(True, description="Allow decimal numbers")
    precision: Optional[int] = Field(None, description="Decimal precision")


class ResponseFormatConfig(BaseModel):
    """Configuration for response format processing."""
    format_type: ResponseFormat
    multiple_choice: Optional[MultipleChoiceOptions] = None
    numeric_range: Optional[NumericRange] = None
    structured_type: Optional[StructuredFormatType] = None
    validation_strict: bool = Field(True, description="Strict validation mode")
    fallback_formats: List[ResponseFormat] = Field(default_factory=list, description="Fallback formats to try")


class ResponseFormatProcessor:
    """
    Advanced response format processor for bias probes.
    
    This class provides comprehensive parsing, validation, and conversion
    capabilities for different response formats with configurable options
    and fallback mechanisms.
    """
    
    def __init__(self, config: Optional[ResponseFormatConfig] = None):
        """
        Initialize the response format processor.
        
        Args:
            config: Configuration for response format processing
        """
        self.config = config or ResponseFormatConfig(format_type=ResponseFormat.FREE_TEXT)
        self.logger = logging.getLogger("probe.response_formats")
        
        # Common patterns for different formats
        self._choice_patterns = [
            r'I\s+CHOOSE\s+([A-Z])',  # "I choose A" - specific patterns first
            r'THE\s+ANSWER\s+IS\s+([A-Z])',  # "The answer is A"
            r'([A-Z])\s+IS\s+CORRECT',  # "A is correct"
            r'option\s+([A-Z])',
            r'choice\s+([A-Z])',
            r'choose\s+([A-Z])',
            r'select\s+([A-Z])',
            r'pick\s+([A-Z])',
            r'answer:\s*([A-Z])',
            r'response:\s*([A-Z])',
            r'^([A-Z])\s*[\.\):]',
            r'^([A-Z])\s*$',
            r'\b([A-Z])\b'  # General pattern last
        ]
        
        self._boolean_patterns = {
            'true': ['true', 'yes', 'y', '1', 'correct', 'right', 'accept'],
            'false': ['false', 'no', 'n', '0', 'incorrect', 'wrong', 'reject']
        }
        
        self._numeric_patterns = [
            r'-?\d+\.?\d*',  # Basic number
            r'\$[\d,]+\.?\d*',  # Currency
            r'\d+%',  # Percentage
            r'\d+/\d+',  # Fraction
            r'\d+:\d+',  # Ratio
        ]
    
    def parse_response(self, response: str, 
                      format_config: Optional[ResponseFormatConfig] = None) -> ResponseParseResult:
        """
        Parse a response according to the specified format configuration.
        
        Args:
            response: The response text to parse
            format_config: Format configuration, uses default if None
            
        Returns:
            ResponseParseResult with parsing details
        """
        config = format_config or self.config
        
        try:
            if config.format_type == ResponseFormat.MULTIPLE_CHOICE:
                return self._parse_multiple_choice(response, config)
            elif config.format_type == ResponseFormat.NUMERIC:
                return self._parse_numeric(response, config)
            elif config.format_type == ResponseFormat.BOOLEAN:
                return self._parse_boolean(response, config)
            elif config.format_type == ResponseFormat.FREE_TEXT:
                return self._parse_free_text(response, config)
            else:
                return ResponseParseResult(
                    success=False,
                    parsed_value=None,
                    confidence=0.0,
                    error_message=f"Unsupported format: {config.format_type}"
                )
        except Exception as e:
            self.logger.error(f"Error parsing response: {e}")
            return ResponseParseResult(
                success=False,
                parsed_value=None,
                confidence=0.0,
                error_message=str(e)
            )
    
    def _parse_multiple_choice(self, response: str, config: ResponseFormatConfig) -> ResponseParseResult:
        """Parse multiple choice response."""
        if not config.multiple_choice:
            return ResponseParseResult(
                success=False,
                parsed_value=None,
                confidence=0.0,
                error_message="Multiple choice configuration required"
            )
        
        response_clean = response.strip()
        if not response_clean:
            return ResponseParseResult(
                success=False,
                parsed_value=None,
                confidence=0.0,
                error_message="Empty response"
            )
        
        # Try to extract choice letter
        choice = self._extract_choice_letter(response_clean)
        if choice:
            # Validate choice is in allowed options
            max_options = len(config.multiple_choice.options)
            if ord(choice) - ord('A') < max_options:
                confidence = self._calculate_choice_confidence(response_clean, choice)
                return ResponseParseResult(
                    success=True,
                    parsed_value=choice,
                    confidence=confidence,
                    metadata={
                        "choice_index": ord(choice) - ord('A'),
                        "choice_text": config.multiple_choice.options[ord(choice) - ord('A')] if ord(choice) - ord('A') < len(config.multiple_choice.options) else None
                    }
                )
        
        # Try partial matching if allowed
        if config.multiple_choice.allow_partial:
            partial_match = self._find_partial_choice_match(response_clean, config.multiple_choice)
            if partial_match:
                return ResponseParseResult(
                    success=True,
                    parsed_value=partial_match,
                    confidence=0.7,  # Lower confidence for partial matches
                    metadata={"match_type": "partial"}
                )
        
        return ResponseParseResult(
            success=False,
            parsed_value=None,
            confidence=0.0,
            error_message="No valid choice found"
        )
    
    def _parse_numeric(self, response: str, config: ResponseFormatConfig) -> ResponseParseResult:
        """Parse numeric response."""
        response_clean = response.strip()
        if not response_clean:
            return ResponseParseResult(
                success=False,
                parsed_value=None,
                confidence=0.0,
                error_message="Empty response"
            )
        
        # Extract numeric value
        numeric_value = self._extract_numeric_value(response_clean)
        if numeric_value is None:
            return ResponseParseResult(
                success=False,
                parsed_value=None,
                confidence=0.0,
                error_message="No numeric value found"
            )
        
        # Validate against range if specified
        if config.numeric_range:
            if not self._validate_numeric_range(numeric_value, config.numeric_range):
                return ResponseParseResult(
                    success=False,
                    parsed_value=numeric_value,
                    confidence=0.0,
                    error_message=f"Value {numeric_value} outside allowed range"
                )
        
        confidence = self._calculate_numeric_confidence(response_clean, numeric_value)
        return ResponseParseResult(
            success=True,
            parsed_value=numeric_value,
            confidence=confidence,
            metadata={
                "original_text": response_clean,
                "extraction_method": "regex"
            }
        )
    
    def _parse_boolean(self, response: str, config: ResponseFormatConfig) -> ResponseParseResult:
        """Parse boolean response."""
        response_clean = response.strip().lower()
        if not response_clean:
            return ResponseParseResult(
                success=False,
                parsed_value=None,
                confidence=0.0,
                error_message="Empty response"
            )
        
        # Check for specific phrases first
        if "i agree" in response_clean or "i disagree" in response_clean:
            if "i agree" in response_clean:
                return ResponseParseResult(
                    success=True,
                    parsed_value=True,
                    confidence=0.8,
                    metadata={"matched_pattern": "i agree"}
                )
            else:  # "i disagree"
                return ResponseParseResult(
                    success=True,
                    parsed_value=False,
                    confidence=0.8,
                    metadata={"matched_pattern": "i disagree"}
                )
        
        # Check for true patterns (exact word matches)
        for pattern in self._boolean_patterns['true']:
            if f" {pattern} " in f" {response_clean} " or response_clean == pattern:
                confidence = self._calculate_boolean_confidence(response_clean, 'true')
                return ResponseParseResult(
                    success=True,
                    parsed_value=True,
                    confidence=confidence,
                    metadata={"matched_pattern": pattern}
                )
        
        # Check for false patterns (exact word matches)
        for pattern in self._boolean_patterns['false']:
            if f" {pattern} " in f" {response_clean} " or response_clean == pattern:
                confidence = self._calculate_boolean_confidence(response_clean, 'false')
                return ResponseParseResult(
                    success=True,
                    parsed_value=False,
                    confidence=confidence,
                    metadata={"matched_pattern": pattern}
                )
        
        return ResponseParseResult(
            success=False,
            parsed_value=None,
            confidence=0.0,
            error_message="No boolean value found"
        )
    
    def _parse_free_text(self, response: str, config: ResponseFormatConfig) -> ResponseParseResult:
        """Parse free text response."""
        response_clean = response.strip()
        if not response_clean:
            return ResponseParseResult(
                success=False,
                parsed_value=None,
                confidence=0.0,
                error_message="Empty response"
            )
        
        # Basic validation for free text
        confidence = self._calculate_free_text_confidence(response_clean)
        
        return ResponseParseResult(
            success=True,
            parsed_value=response_clean,
            confidence=confidence,
            metadata={
                "length": len(response_clean),
                "word_count": len(response_clean.split()),
                "has_punctuation": any(c in response_clean for c in '.,!?;:')
            }
        )
    
    def _extract_choice_letter(self, response: str) -> Optional[str]:
        """Extract choice letter from response."""
        response_upper = response.upper().strip()
        
        # First check for simple single letter responses
        if len(response_upper) == 1 and response_upper in 'ABCDEFGHIJ':
            return response_upper
        
        # Then check for patterns
        for pattern in self._choice_patterns:
            match = re.search(pattern, response_upper)
            if match:
                return match.group(1)
        
        return None
    
    def _find_partial_choice_match(self, response: str, 
                                  options: MultipleChoiceOptions) -> Optional[str]:
        """Find partial match for choice options."""
        response_lower = response.lower()
        
        for i, option in enumerate(options.options):
            option_lower = option.lower()
            if not options.case_sensitive:
                # Check if response contains significant portion of option text
                words = option_lower.split()
                if len(words) > 1:
                    # Check if response contains key words from option
                    key_words = [w for w in words if len(w) > 3]  # Skip short words
                    if key_words and all(word in response_lower for word in key_words):
                        return chr(ord('A') + i)
                else:
                    # Single word option
                    if option_lower in response_lower:
                        return chr(ord('A') + i)
        
        return None
    
    def _extract_numeric_value(self, response: str) -> Optional[float]:
        """Extract numeric value from response."""
        # Try different numeric patterns
        for pattern in self._numeric_patterns:
            matches = re.findall(pattern, response)
            if matches:
                try:
                    # Clean the match (remove currency symbols, etc.)
                    clean_match = matches[0].replace('$', '').replace(',', '').replace('%', '')
                    return float(clean_match)
                except ValueError:
                    continue
        
        return None
    
    def _validate_numeric_range(self, value: float, range_config: NumericRange) -> bool:
        """Validate numeric value against range configuration."""
        if range_config.min_value is not None and value < range_config.min_value:
            return False
        if range_config.max_value is not None and value > range_config.max_value:
            return False
        if not range_config.allow_negative and value < 0:
            return False
        if not range_config.allow_decimal and value != int(value):
            return False
        
        return True
    
    def _calculate_choice_confidence(self, response: str, choice: str) -> float:
        """Calculate confidence for choice extraction."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence for explicit choice patterns
        if re.search(rf'\b{choice}\b', response.upper()):
            confidence += 0.3
        
        # Increase confidence for clear choice indicators
        choice_indicators = ['option', 'choice', 'select', 'choose', 'pick']
        if any(indicator in response.lower() for indicator in choice_indicators):
            confidence += 0.2
        
        # Decrease confidence if response is very long (might be explanation)
        if len(response) > 200:
            confidence -= 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_numeric_confidence(self, response: str, value: float) -> float:
        """Calculate confidence for numeric extraction."""
        confidence = 0.7  # Base confidence for numeric extraction
        
        # Increase confidence for standalone numbers
        if re.match(r'^-?\d+\.?\d*$', response.strip()):
            confidence += 0.2
        
        # Increase confidence for clear numeric indicators
        numeric_indicators = ['number', 'value', 'amount', 'quantity', 'count']
        if any(indicator in response.lower() for indicator in numeric_indicators):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_boolean_confidence(self, response: str, boolean_value: str) -> float:
        """Calculate confidence for boolean extraction."""
        confidence = 0.6  # Base confidence
        
        # Increase confidence for exact matches
        if response.strip().lower() in self._boolean_patterns[boolean_value]:
            confidence += 0.3
        
        # Increase confidence for clear boolean indicators
        boolean_indicators = ['yes', 'no', 'true', 'false', 'correct', 'incorrect']
        if any(indicator in response.lower() for indicator in boolean_indicators):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_free_text_confidence(self, response: str) -> float:
        """Calculate confidence for free text response."""
        confidence = 0.8  # Base confidence for free text
        
        # Adjust based on response characteristics
        word_count = len(response.split())
        if word_count < 3:
            confidence -= 0.2  # Very short responses
        elif word_count > 100:
            confidence -= 0.1  # Very long responses
        
        # Increase confidence for well-formed responses
        if any(c in response for c in '.,!?;:'):
            confidence += 0.1  # Has punctuation
        
        return min(confidence, 1.0)
    
    def convert_response_format(self, response: str, 
                               from_format: ResponseFormat,
                               to_format: ResponseFormat,
                               config: Optional[ResponseFormatConfig] = None) -> ResponseParseResult:
        """
        Convert response from one format to another.
        
        Args:
            response: The response to convert
            from_format: Source format
            to_format: Target format
            config: Format configuration
            
        Returns:
            ResponseParseResult with conversion details
        """
        # First parse in source format
        source_config = config or ResponseFormatConfig(format_type=from_format)
        
        # For simple conversions, we can handle some cases without full parsing
        if from_format == ResponseFormat.MULTIPLE_CHOICE and to_format == ResponseFormat.FREE_TEXT:
            # Simple conversion: just return the response as free text
            return ResponseParseResult(
                success=True,
                parsed_value=response,
                confidence=0.8,
                metadata={
                    "conversion": True,
                    "source_format": from_format,
                    "target_format": to_format,
                    "simple_conversion": True
                }
            )
        
        parse_result = self.parse_response(response, source_config)
        
        if not parse_result.success:
            return ResponseParseResult(
                success=False,
                parsed_value=None,
                confidence=0.0,
                error_message=f"Failed to parse source format: {parse_result.error_message}"
            )
        
        # Convert to target format
        try:
            if to_format == ResponseFormat.FREE_TEXT:
                converted_value = str(parse_result.parsed_value)
            elif to_format == ResponseFormat.NUMERIC:
                if isinstance(parse_result.parsed_value, (int, float)):
                    converted_value = float(parse_result.parsed_value)
                else:
                    converted_value = self._extract_numeric_value(str(parse_result.parsed_value))
                    if converted_value is None:
                        raise ValueError("Cannot convert to numeric")
            elif to_format == ResponseFormat.BOOLEAN:
                if isinstance(parse_result.parsed_value, bool):
                    converted_value = parse_result.parsed_value
                else:
                    # Try to infer boolean from other formats
                    converted_value = self._infer_boolean_from_value(parse_result.parsed_value)
            else:
                raise ValueError(f"Conversion to {to_format} not supported")
            
            return ResponseParseResult(
                success=True,
                parsed_value=converted_value,
                confidence=parse_result.confidence * 0.9,  # Slightly lower confidence for conversion
                metadata={
                    "conversion": True,
                    "source_format": from_format,
                    "target_format": to_format,
                    "original_confidence": parse_result.confidence
                }
            )
            
        except Exception as e:
            return ResponseParseResult(
                success=False,
                parsed_value=None,
                confidence=0.0,
                error_message=f"Conversion failed: {str(e)}"
            )
    
    def _infer_boolean_from_value(self, value: Any) -> bool:
        """Infer boolean value from other types."""
        if isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value != 0
        elif isinstance(value, str):
            return len(value.strip()) > 0
        else:
            return bool(value)
    
    def validate_response_quality(self, response: str, 
                                 format_config: Optional[ResponseFormatConfig] = None) -> Dict[str, Any]:
        """
        Validate response quality and provide detailed analysis.
        
        Args:
            response: The response to validate
            format_config: Format configuration
            
        Returns:
            Dictionary with quality metrics and analysis
        """
        config = format_config or self.config
        parse_result = self.parse_response(response, config)
        
        quality_metrics = {
            "format_compliance": parse_result.success,
            "confidence": parse_result.confidence,
            "response_length": len(response.strip()),
            "word_count": len(response.strip().split()),
            "has_punctuation": any(c in response for c in '.,!?;:'),
            "has_capitalization": any(c.isupper() for c in response),
            "parse_result": parse_result,
            "quality_score": 0.0
        }
        
        # Calculate overall quality score
        quality_score = 0.0
        
        if parse_result.success:
            quality_score += 0.4  # Format compliance
            quality_score += parse_result.confidence * 0.3  # Confidence
        
        # Length appropriateness
        word_count = quality_metrics["word_count"]
        if config.format_type == ResponseFormat.MULTIPLE_CHOICE:
            if 1 <= word_count <= 10:
                quality_score += 0.2
        elif config.format_type == ResponseFormat.NUMERIC:
            if 1 <= word_count <= 5:
                quality_score += 0.2
        elif config.format_type == ResponseFormat.BOOLEAN:
            if 1 <= word_count <= 3:
                quality_score += 0.2
        else:  # FREE_TEXT
            if 5 <= word_count <= 100:
                quality_score += 0.2
        
        # Clarity indicators
        if quality_metrics["has_punctuation"]:
            quality_score += 0.1
        
        quality_metrics["quality_score"] = min(quality_score, 1.0)
        
        return quality_metrics
