"""
Tests for the base probe class and interfaces.

This module tests the core functionality of the BaseProbe class and related components.
"""

import pytest
from datetime import datetime
from src.ai_bias_psych.probes.base import (
    BaseProbe, ProbeType, ResponseFormat, ProbeVariant, ProbeExecutionResult
)
from src.ai_bias_psych.llm.base import BaseLLMClient, LLMResponse, LLMError
from src.ai_bias_psych.models.probe import ProbeRequest


class MockLLMClient(BaseLLMClient):
    """Mock LLM client for testing."""
    
    def __init__(self):
        super().__init__("mock-api-key")
    
    def _validate_config(self):
        pass
    
    async def generate_response(self, prompt: str, model: str, temperature: float = 0.7, 
                              max_tokens: int = 1000, **kwargs):
        # Simulate some processing time
        import asyncio
        await asyncio.sleep(0.1)  # 100ms delay
        
        return LLMResponse(
            content="Test response",
            model=model,
            provider="mock",
            tokens_used=10,
            response_time_ms=100,
            temperature=temperature,
            metadata=kwargs.get("metadata", {})
        )
    
    def list_models(self):
        """List available models."""
        return ["test-model"]
    
    def validate_model(self, model: str) -> bool:
        """Validate model."""
        return model == "test-model"
    
    async def health_check(self):
        return True


class TestProbe(BaseProbe):
    """Test probe implementation for testing the base class."""
    
    def __init__(self):
        super().__init__(
            probe_type=ProbeType.ANCHORING,
            name="Test Probe",
            description="A test probe for unit testing"
        )
        # Add a test variant
        self.variants["test_variant"] = ProbeVariant(
            id="test_variant",
            domain="test",
            prompt="This is a test prompt",
            expected_bias="test_bias",
            response_format=ResponseFormat.FREE_TEXT,
            scoring_params={"test_param": 1.0}
        )
    
    def load_variants(self, config):
        pass
    
    def score_response(self, response, variant, execution_metadata):
        return {
            "bias_score": 0.5,
            "confidence": 0.8,
            "analysis": "Test analysis"
        }
    
    def get_random_variant(self, domain=None):
        return self.variants["test_variant"]


class TestBaseProbe:
    """Test cases for the BaseProbe class."""
    
    def test_probe_initialization(self):
        """Test that a probe can be initialized correctly."""
        probe = TestProbe()
        
        assert probe.probe_type == ProbeType.ANCHORING
        assert probe.name == "Test Probe"
        assert probe.description == "A test probe for unit testing"
        assert len(probe.variants) == 1
        assert "test_variant" in probe.variants
    
    def test_get_variant(self):
        """Test getting a variant by ID."""
        probe = TestProbe()
        
        variant = probe.get_variant("test_variant")
        assert variant is not None
        assert variant.id == "test_variant"
        assert variant.domain == "test"
        
        # Test non-existent variant
        assert probe.get_variant("nonexistent") is None
    
    def test_list_variants(self):
        """Test listing variants with and without domain filter."""
        probe = TestProbe()
        
        # List all variants
        all_variants = probe.list_variants()
        assert len(all_variants) == 1
        assert all_variants[0].id == "test_variant"
        
        # List variants by domain
        test_variants = probe.list_variants("test")
        assert len(test_variants) == 1
        
        other_variants = probe.list_variants("other")
        assert len(other_variants) == 0
    
    def test_get_random_variant(self):
        """Test getting a random variant."""
        probe = TestProbe()
        
        variant = probe.get_random_variant()
        assert variant is not None
        assert variant.id == "test_variant"
    
    def test_validate_response_format(self):
        """Test response format validation."""
        probe = TestProbe()
        
        # Test free text format
        result = probe.validate_response_format("This is a response", ResponseFormat.FREE_TEXT)
        assert result.success
        result = probe.validate_response_format("", ResponseFormat.FREE_TEXT)
        assert not result.success
        
        # Test multiple choice format - need to provide variant with options
        from src.ai_bias_psych.probes.types import ProbeVariant
        variant = ProbeVariant(
            id="test_variant",
            domain="test",
            prompt="Test prompt",
            response_format=ResponseFormat.MULTIPLE_CHOICE,
            scoring_params={
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "allow_partial": True,
                "case_sensitive": False
            }
        )
        
        result = probe.validate_response_format("A", ResponseFormat.MULTIPLE_CHOICE, variant)
        assert result.success
        result = probe.validate_response_format("Option B", ResponseFormat.MULTIPLE_CHOICE, variant)
        assert result.success
        result = probe.validate_response_format("Invalid choice", ResponseFormat.MULTIPLE_CHOICE, variant)
        assert not result.success
        
        # Test numeric format
        result = probe.validate_response_format("123.45", ResponseFormat.NUMERIC)
        assert result.success
        result = probe.validate_response_format("-67", ResponseFormat.NUMERIC)
        assert result.success
        result = probe.validate_response_format("not a number", ResponseFormat.NUMERIC)
        assert not result.success
        
        # Test boolean format
        result = probe.validate_response_format("true", ResponseFormat.BOOLEAN)
        assert result.success
        result = probe.validate_response_format("yes", ResponseFormat.BOOLEAN)
        assert result.success
        result = probe.validate_response_format("1", ResponseFormat.BOOLEAN)
        assert result.success
        result = probe.validate_response_format("maybe", ResponseFormat.BOOLEAN)
        assert not result.success
    
    def test_extract_numeric_value(self):
        """Test extracting numeric values from responses."""
        probe = TestProbe()
        
        assert probe.extract_numeric_value("The answer is 42") == 42.0
        assert probe.extract_numeric_value("I think it's 3.14") == 3.14
        assert probe.extract_numeric_value("Negative: -5.5") == -5.5
        assert probe.extract_numeric_value("No numbers here") is None
    
    def test_extract_choice(self):
        """Test extracting choice selections from responses."""
        probe = TestProbe()
        
        # Create a variant with multiple choice options for testing
        from src.ai_bias_psych.probes.types import ProbeVariant
        variant = ProbeVariant(
            id="test_variant",
            domain="test",
            prompt="Test prompt",
            response_format=ResponseFormat.MULTIPLE_CHOICE,
            scoring_params={
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "allow_partial": True,
                "case_sensitive": False
            }
        )
        
        assert probe.extract_choice("I choose A", variant) == "A"
        assert probe.extract_choice("Option B is correct", variant) == "B"
        assert probe.extract_choice("C.", variant) == "C"
        assert probe.extract_choice("D", variant) == "D"
        assert probe.extract_choice("No clear choice", variant) is None
    
    @pytest.mark.asyncio
    async def test_execute_probe(self):
        """Test executing a probe with a mock LLM client."""
        probe = TestProbe()
        llm_client = MockLLMClient()
        
        request = ProbeRequest(
            probe_type="anchoring",
            variant_id="test_variant",
            model_provider="mock",
            model_name="test-model",
            temperature=0.7,
            max_tokens=1000
        )
        
        result = await probe.execute(request, llm_client)
        
        assert isinstance(result, ProbeExecutionResult)
        assert result.probe_type == ProbeType.ANCHORING
        assert result.variant_id == "test_variant"
        assert result.model_provider == "mock"
        assert result.model_name == "test-model"
        assert result.response == "Test response"
        assert result.bias_score == 0.5
        assert result.confidence == 0.8
        assert result.tokens_used == 10
        assert result.response_time_ms >= 100  # Should be at least 100ms due to sleep
    
    @pytest.mark.asyncio
    async def test_execute_probe_invalid_variant(self):
        """Test executing a probe with an invalid variant ID."""
        probe = TestProbe()
        llm_client = MockLLMClient()
        
        request = ProbeRequest(
            probe_type="anchoring",
            variant_id="nonexistent",
            model_provider="mock",
            model_name="test-model"
        )
        
        with pytest.raises(ValueError, match="Variant nonexistent not found"):
            await probe.execute(request, llm_client)
    
    @pytest.mark.asyncio
    async def test_execute_probe_type_mismatch(self):
        """Test executing a probe with wrong probe type."""
        probe = TestProbe()
        llm_client = MockLLMClient()
        
        request = ProbeRequest(
            probe_type="framing",  # Wrong type
            variant_id="test_variant",
            model_provider="mock",
            model_name="test-model"
        )
        
        with pytest.raises(ValueError, match="Probe type mismatch"):
            await probe.execute(request, llm_client)
    
    def test_string_representations(self):
        """Test string representations of the probe."""
        probe = TestProbe()
        
        assert str(probe) == "Test Probe (anchoring)"
        assert "TestProbe" in repr(probe)
        assert "anchoring" in repr(probe)
        assert "variants=1" in repr(probe)


class TestProbeType:
    """Test cases for the ProbeType enum."""
    
    def test_probe_type_values(self):
        """Test that all expected probe types are defined."""
        expected_types = [
            "prospect_theory", "anchoring", "availability", "framing",
            "sunk_cost", "optimism", "confirmation", "base_rate",
            "conjunction", "overconfidence"
        ]
        
        for probe_type in expected_types:
            assert hasattr(ProbeType, probe_type.upper())
            assert getattr(ProbeType, probe_type.upper()).value == probe_type


class TestResponseFormat:
    """Test cases for the ResponseFormat enum."""
    
    def test_response_format_values(self):
        """Test that all expected response formats are defined."""
        expected_formats = [
            "multiple_choice", "free_text", "numeric", "boolean"
        ]
        
        for fmt in expected_formats:
            assert hasattr(ResponseFormat, fmt.upper())
            assert getattr(ResponseFormat, fmt.upper()).value == fmt


if __name__ == "__main__":
    pytest.main([__file__])
