"""
Base probe class and interfaces for AI Bias Psychologist.

This module defines the abstract base class and common interfaces that all
bias probe implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import asyncio
import logging

from ..models.probe import ProbeRequest, ProbeResponse
from ..llm.base import BaseLLMClient
from .types import ProbeType, ProbeVariant, ProbeExecutionResult, ResponseFormat
from .randomization import ProbeRandomizer, RandomizationConfig, SessionContext
from .response_formats import ResponseFormatProcessor, ResponseFormatConfig, ResponseParseResult


class BaseProbe(ABC):
    """
    Abstract base class for all bias probe implementations.
    
    This class defines the common interface and behavior that all bias probes
    must implement. It provides the framework for:
    - Probe execution with LLM clients
    - Response scoring and bias detection
    - Variant management and randomization
    - Error handling and logging
    """
    
    def __init__(self, probe_type: ProbeType, name: str, description: str, 
                 randomizer: Optional[ProbeRandomizer] = None):
        """
        Initialize the base probe.
        
        Args:
            probe_type: The type of bias this probe tests for
            name: Human-readable name of the probe
            description: Description of what this probe tests for
            randomizer: Optional probe randomizer for variant selection
        """
        self.probe_type = probe_type
        self.name = name
        self.description = description
        self.variants: Dict[str, ProbeVariant] = {}
        self.logger = logging.getLogger(f"probe.{probe_type.value}")
        self.randomizer = randomizer or ProbeRandomizer()
        self.response_processor = ResponseFormatProcessor()
        
    @abstractmethod
    def load_variants(self, config: Dict[str, Any]) -> None:
        """
        Load probe variants from configuration.
        
        Args:
            config: Configuration dictionary containing variant definitions
        """
        pass
    
    @abstractmethod
    def score_response(self, response: str, variant: ProbeVariant, 
                      execution_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a model's response for bias indicators.
        
        Args:
            response: The model's response text
            variant: The probe variant that was used
            execution_metadata: Additional metadata from the execution
            
        Returns:
            Dictionary containing bias score, confidence, and analysis details
        """
        pass
    
    def get_random_variant(self, domain: Optional[str] = None, 
                          session_id: Optional[str] = None) -> ProbeVariant:
        """
        Get a random variant for this probe type using the configured randomization strategy.
        
        Args:
            domain: Optional domain filter for variant selection
            session_id: Optional session ID for tracking and repeat prevention
            
        Returns:
            A randomly selected probe variant
        """
        available_variants = self.list_variants(domain)
        if not available_variants:
            raise ValueError(f"No variants available for domain: {domain}")
        
        return self.randomizer.select_variant(
            probe_type=self.probe_type,
            available_variants=available_variants,
            session_id=session_id,
            domain=domain
        )
    
    def get_variant(self, variant_id: str) -> Optional[ProbeVariant]:
        """
        Get a specific variant by ID.
        
        Args:
            variant_id: The variant identifier
            
        Returns:
            The probe variant if found, None otherwise
        """
        return self.variants.get(variant_id)
    
    def list_variants(self, domain: Optional[str] = None) -> List[ProbeVariant]:
        """
        List all available variants, optionally filtered by domain.
        
        Args:
            domain: Optional domain filter
            
        Returns:
            List of probe variants matching the criteria
        """
        if domain is None:
            return list(self.variants.values())
        return [v for v in self.variants.values() if v.domain == domain]
    
    async def execute(self, request: ProbeRequest, llm_client: BaseLLMClient) -> ProbeExecutionResult:
        """
        Execute a bias probe with the given LLM client.
        
        Args:
            request: The probe execution request
            llm_client: The LLM client to use for execution
            
        Returns:
            The execution result with bias score and analysis
            
        Raises:
            ValueError: If the requested variant is not found
            RuntimeError: If the LLM execution fails
        """
        # Validate request
        if request.probe_type != self.probe_type.value:
            raise ValueError(f"Probe type mismatch: expected {self.probe_type.value}, got {request.probe_type}")
        
        variant = self.get_variant(request.variant_id)
        if variant is None:
            raise ValueError(f"Variant {request.variant_id} not found for probe {self.probe_type.value}")
        
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Execute the probe
        start_time = datetime.utcnow()
        
        try:
            # Send request to LLM
            llm_response = await llm_client.generate_response(
                prompt=variant.prompt,
                model=request.model_name,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                metadata={
                    "probe_type": self.probe_type.value,
                    "variant_id": request.variant_id,
                    "request_id": request_id,
                    **request.metadata
                }
            )
            
            end_time = datetime.utcnow()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Score the response
            scoring_result = self.score_response(
                response=llm_response.content,
                variant=variant,
                execution_metadata={
                    "response_time_ms": response_time_ms,
                    "tokens_used": llm_response.tokens_used,
                    "temperature": request.temperature,
                    "model_provider": request.model_provider,
                    "model_name": request.model_name,
                }
            )
            
            # Create execution result
            result = ProbeExecutionResult(
                request_id=request_id,
                probe_type=self.probe_type,
                variant_id=request.variant_id,
                model_provider=request.model_provider,
                model_name=request.model_name,
                prompt=variant.prompt,
                response=llm_response.content,
                response_time_ms=response_time_ms,
                tokens_used=llm_response.tokens_used,
                temperature=request.temperature,
                bias_score=scoring_result.get("bias_score", 0.0),
                confidence=scoring_result.get("confidence", 0.0),
                metadata={
                    "scoring_details": scoring_result,
                    "variant_metadata": variant.metadata,
                    **request.metadata
                }
            )
            
            self.logger.info(
                f"Probe execution completed: {self.probe_type.value} "
                f"(variant: {request.variant_id}, score: {result.bias_score:.3f}, "
                f"confidence: {result.confidence:.3f})"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Probe execution failed: {self.probe_type.value} - {str(e)}")
            raise RuntimeError(f"Probe execution failed: {str(e)}") from e
    
    def validate_response_format(self, response: str, expected_format: ResponseFormat, 
                                variant: Optional[ProbeVariant] = None) -> ResponseParseResult:
        """
        Validate that a response matches the expected format using advanced parsing.
        
        Args:
            response: The response text to validate
            expected_format: The expected response format
            variant: Optional probe variant for format-specific configuration
            
        Returns:
            ResponseParseResult with validation details
        """
        # Create format configuration
        format_config = ResponseFormatConfig(format_type=expected_format)
        
        # Add variant-specific configuration
        if variant and variant.scoring_params:
            if expected_format == ResponseFormat.MULTIPLE_CHOICE:
                from .response_formats import MultipleChoiceOptions
                options = variant.scoring_params.get('options', ['A', 'B', 'C', 'D'])
                format_config.multiple_choice = MultipleChoiceOptions(
                    options=options,
                    allow_partial=variant.scoring_params.get('allow_partial', False),
                    case_sensitive=variant.scoring_params.get('case_sensitive', False)
                )
        elif expected_format == ResponseFormat.NUMERIC and variant and variant.scoring_params:
                from .response_formats import NumericRange
                format_config.numeric_range = NumericRange(
                    min_value=variant.scoring_params.get('min_value'),
                    max_value=variant.scoring_params.get('max_value'),
                    allow_negative=variant.scoring_params.get('allow_negative', True),
                    allow_decimal=variant.scoring_params.get('allow_decimal', True)
                )
        
        return self.response_processor.parse_response(response, format_config)
    
    def extract_numeric_value(self, response: str, variant: Optional[ProbeVariant] = None) -> Optional[float]:
        """
        Extract numeric value from a response text using advanced parsing.
        
        Args:
            response: The response text
            variant: Optional probe variant for format-specific configuration
            
        Returns:
            The extracted numeric value, or None if not found
        """
        format_config = ResponseFormatConfig(format_type=ResponseFormat.NUMERIC)
        
        if variant and variant.scoring_params:
            from .response_formats import NumericRange
            format_config.numeric_range = NumericRange(
                min_value=variant.scoring_params.get('min_value'),
                max_value=variant.scoring_params.get('max_value'),
                allow_negative=variant.scoring_params.get('allow_negative', True),
                allow_decimal=variant.scoring_params.get('allow_decimal', True)
            )
        
        parse_result = self.response_processor.parse_response(response, format_config)
        return parse_result.parsed_value if parse_result.success else None
    
    def extract_choice(self, response: str, variant: Optional[ProbeVariant] = None) -> Optional[str]:
        """
        Extract choice selection from a response text using advanced parsing.
        
        Args:
            response: The response text
            variant: Optional probe variant for format-specific configuration
            
        Returns:
            The extracted choice (A, B, C, etc.), or None if not found
        """
        format_config = ResponseFormatConfig(format_type=ResponseFormat.MULTIPLE_CHOICE)
        
        if variant and variant.scoring_params:
            from .response_formats import MultipleChoiceOptions
            options = variant.scoring_params.get('options', ['A', 'B', 'C', 'D'])
            format_config.multiple_choice = MultipleChoiceOptions(
                options=options,
                allow_partial=variant.scoring_params.get('allow_partial', False),
                case_sensitive=variant.scoring_params.get('case_sensitive', False)
            )
        
        parse_result = self.response_processor.parse_response(response, format_config)
        return parse_result.parsed_value if parse_result.success else None
    
    def extract_boolean_value(self, response: str) -> Optional[bool]:
        """
        Extract boolean value from a response text using advanced parsing.
        
        Args:
            response: The response text
            
        Returns:
            The extracted boolean value, or None if not found
        """
        format_config = ResponseFormatConfig(format_type=ResponseFormat.BOOLEAN)
        parse_result = self.response_processor.parse_response(response, format_config)
        return parse_result.parsed_value if parse_result.success else None
    
    def analyze_response_quality(self, response: str, variant: Optional[ProbeVariant] = None) -> Dict[str, Any]:
        """
        Analyze response quality and provide detailed metrics.
        
        Args:
            response: The response text to analyze
            variant: Optional probe variant for format-specific analysis
            
        Returns:
            Dictionary with quality metrics and analysis
        """
        expected_format = variant.response_format if variant else ResponseFormat.FREE_TEXT
        format_config = ResponseFormatConfig(format_type=expected_format)
        
        # Add variant-specific configuration
        if variant and variant.scoring_params:
            if expected_format == ResponseFormat.MULTIPLE_CHOICE:
                from .response_formats import MultipleChoiceOptions
                options = variant.scoring_params.get('options', ['A', 'B', 'C', 'D'])
                format_config.multiple_choice = MultipleChoiceOptions(
                    options=options,
                    allow_partial=variant.scoring_params.get('allow_partial', False),
                    case_sensitive=variant.scoring_params.get('case_sensitive', False)
                )
            elif expected_format == ResponseFormat.NUMERIC:
                from .response_formats import NumericRange
                format_config.numeric_range = NumericRange(
                    min_value=variant.scoring_params.get('min_value'),
                    max_value=variant.scoring_params.get('max_value'),
                    allow_negative=variant.scoring_params.get('allow_negative', True),
                    allow_decimal=variant.scoring_params.get('allow_decimal', True)
                )
        
        return self.response_processor.validate_response_quality(response, format_config)
    
    def __str__(self) -> str:
        """String representation of the probe."""
        return f"{self.name} ({self.probe_type.value})"
    
    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new probe execution session.
        
        Args:
            metadata: Optional metadata for the session
            
        Returns:
            Session ID for tracking
        """
        return self.randomizer.create_session(metadata)
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Dictionary containing session summary statistics
        """
        return self.randomizer.get_session_summary(session_id)
    
    def reset_session(self, session_id: str) -> bool:
        """
        Reset a session to clear all tracking information.
        
        Args:
            session_id: The session identifier
            
        Returns:
            True if session was reset, False if not found
        """
        return self.randomizer.reset_session(session_id)
    
    def configure_randomization(self, config: RandomizationConfig) -> None:
        """
        Configure the randomization strategy for this probe.
        
        Args:
            config: Randomization configuration
        """
        self.randomizer.config = config
        self.logger.info(f"Updated randomization config: {config.strategy.value}")
    
    def get_randomization_config(self) -> RandomizationConfig:
        """
        Get the current randomization configuration.
        
        Returns:
            Current randomization configuration
        """
        return self.randomizer.config
    
    def __repr__(self) -> str:
        """Detailed string representation of the probe."""
        return f"<{self.__class__.__name__}(type={self.probe_type.value}, variants={len(self.variants)})>"
