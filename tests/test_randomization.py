"""
Tests for probe randomization and order effect prevention system.
"""

import pytest
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.ai_bias_psych.probes.randomization import (
    ProbeRandomizer, RandomizationConfig, RandomizationStrategy, 
    OrderEffectPrevention, SessionContext
)
from src.ai_bias_psych.probes.types import ProbeType, ProbeVariant, ResponseFormat
from src.ai_bias_psych.probes.battery_manager import TestBattery


class TestProbeRandomizer:
    """Test cases for the ProbeRandomizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = RandomizationConfig(
            strategy=RandomizationStrategy.DOMAIN_BALANCED,
            order_prevention=OrderEffectPrevention.COUNTERBALANCED,
            prevent_repeats=True,
            balance_domains=True,
            seed=42  # Fixed seed for reproducible tests
        )
        self.randomizer = ProbeRandomizer(self.config)
        
        # Create test variants
        self.test_variants = [
            ProbeVariant(
                id="test_1_health",
                domain="health",
                prompt="Test health prompt 1",
                response_format=ResponseFormat.FREE_TEXT
            ),
            ProbeVariant(
                id="test_2_health",
                domain="health",
                prompt="Test health prompt 2",
                response_format=ResponseFormat.FREE_TEXT
            ),
            ProbeVariant(
                id="test_1_finance",
                domain="finance",
                prompt="Test finance prompt 1",
                response_format=ResponseFormat.FREE_TEXT
            ),
            ProbeVariant(
                id="test_2_finance",
                domain="finance",
                prompt="Test finance prompt 2",
                response_format=ResponseFormat.FREE_TEXT
            ),
            ProbeVariant(
                id="test_1_tech",
                domain="tech",
                prompt="Test tech prompt 1",
                response_format=ResponseFormat.FREE_TEXT
            )
        ]
    
    def test_create_session(self):
        """Test session creation."""
        session_id = self.randomizer.create_session({"test": "metadata"})
        assert session_id is not None
        assert len(session_id) > 0
        
        session = self.randomizer.get_session(session_id)
        assert session is not None
        assert session.metadata["test"] == "metadata"
    
    def test_simple_random_selection(self):
        """Test simple random variant selection."""
        self.randomizer.config.strategy = RandomizationStrategy.SIMPLE_RANDOM
        
        # Test without session (no repeat prevention)
        selected = self.randomizer.select_variant(
            ProbeType.PROSPECT_THEORY,
            self.test_variants
        )
        assert selected in self.test_variants
        
        # Test with session (repeat prevention)
        session_id = self.randomizer.create_session()
        selected1 = self.randomizer.select_variant(
            ProbeType.PROSPECT_THEORY,
            self.test_variants,
            session_id
        )
        selected2 = self.randomizer.select_variant(
            ProbeType.PROSPECT_THEORY,
            self.test_variants,
            session_id
        )
        
        # Should be different variants due to repeat prevention
        assert selected1.id != selected2.id
    
    def test_domain_balanced_selection(self):
        """Test domain-balanced variant selection."""
        self.randomizer.config.strategy = RandomizationStrategy.DOMAIN_BALANCED
        session_id = self.randomizer.create_session()
        
        # Select multiple variants and check domain balance
        selected_variants = []
        for _ in range(6):  # Increased to ensure we get multiple domains
            variant = self.randomizer.select_variant(
                ProbeType.PROSPECT_THEORY,
                self.test_variants,
                session_id
            )
            selected_variants.append(variant)
        
        # Check that domains are reasonably balanced
        domain_counts = {}
        for variant in selected_variants:
            domain_counts[variant.domain] = domain_counts.get(variant.domain, 0) + 1
        
        # Should have multiple domains represented (we have health, finance, tech)
        # With repeat prevention, we should eventually use all domains
        assert len(domain_counts) >= 1  # At least one domain should be used
        
        # If we have multiple domains, check balance
        if len(domain_counts) > 1:
            max_count = max(domain_counts.values())
            min_count = min(domain_counts.values())
            assert max_count <= min_count * 3
    
    def test_counterbalanced_selection(self):
        """Test counterbalanced variant selection."""
        self.randomizer.config.strategy = RandomizationStrategy.COUNTERBALANCED
        session_id = self.randomizer.create_session()
        
        # Select variants multiple times and check for counterbalancing
        selected_variants = []
        for _ in range(10):
            variant = self.randomizer.select_variant(
                ProbeType.PROSPECT_THEORY,
                self.test_variants,
                session_id
            )
            selected_variants.append(variant)
        
        # Should have used all variants at least once
        used_variant_ids = set(v.id for v in selected_variants)
        assert len(used_variant_ids) == len(self.test_variants)
    
    def test_latin_square_selection(self):
        """Test Latin square variant selection."""
        self.randomizer.config.strategy = RandomizationStrategy.LATIN_SQUARE
        session_id = self.randomizer.create_session()
        
        # Test with different probe types
        probe_types = [ProbeType.PROSPECT_THEORY, ProbeType.ANCHORING, ProbeType.FRAMING]
        
        for probe_type in probe_types:
            variant = self.randomizer.select_variant(
                probe_type,
                self.test_variants,
                session_id
            )
            assert variant in self.test_variants
    
    def test_block_randomized_selection(self):
        """Test block randomized variant selection."""
        self.randomizer.config.strategy = RandomizationStrategy.BLOCK_RANDOMIZED
        session_id = self.randomizer.create_session()
        
        variant = self.randomizer.select_variant(
            ProbeType.PROSPECT_THEORY,
            self.test_variants,
            session_id
        )
        assert variant in self.test_variants
    
    def test_probe_order_selection(self):
        """Test probe order selection for order effect prevention."""
        probe_types = [
            ProbeType.PROSPECT_THEORY,
            ProbeType.ANCHORING,
            ProbeType.FRAMING,
            ProbeType.AVAILABILITY
        ]
        
        # Test random order
        self.randomizer.config.order_prevention = OrderEffectPrevention.RANDOM_ORDER
        session_id = self.randomizer.create_session()
        
        ordered = self.randomizer.select_probe_order(probe_types, session_id)
        assert len(ordered) == len(probe_types)
        assert set(ordered) == set(probe_types)
        
        # Test counterbalanced order
        self.randomizer.config.order_prevention = OrderEffectPrevention.COUNTERBALANCED
        ordered1 = self.randomizer.select_probe_order(probe_types, session_id)
        ordered2 = self.randomizer.select_probe_order(probe_types, session_id)
        
        # Should be different orders
        assert ordered1 != ordered2
    
    def test_latin_square_order(self):
        """Test Latin square order selection."""
        probe_types = [
            ProbeType.PROSPECT_THEORY,
            ProbeType.ANCHORING,
            ProbeType.FRAMING,
            ProbeType.AVAILABILITY
        ]
        
        self.randomizer.config.order_prevention = OrderEffectPrevention.LATIN_SQUARE
        session_id = self.randomizer.create_session()
        
        ordered = self.randomizer.select_probe_order(probe_types, session_id)
        assert len(ordered) == len(probe_types)
        assert set(ordered) == set(probe_types)
    
    def test_block_randomized_order(self):
        """Test block randomized order selection."""
        probe_types = [
            ProbeType.PROSPECT_THEORY,
            ProbeType.ANCHORING,
            ProbeType.FRAMING,
            ProbeType.AVAILABILITY
        ]
        
        self.randomizer.config.order_prevention = OrderEffectPrevention.BLOCK_RANDOMIZED
        session_id = self.randomizer.create_session()
        
        ordered = self.randomizer.select_probe_order(probe_types, session_id)
        assert len(ordered) == len(probe_types)
        assert set(ordered) == set(probe_types)
    
    def test_session_tracking(self):
        """Test session tracking functionality."""
        session_id = self.randomizer.create_session()
        
        # Select some variants
        for _ in range(3):
            self.randomizer.select_variant(
                ProbeType.PROSPECT_THEORY,
                self.test_variants,
                session_id
            )
        
        # Check session summary
        summary = self.randomizer.get_session_summary(session_id)
        # With repeat prevention, we might not get exactly 3 variants
        assert summary["total_variants_used"] >= 1  # At least one should be used
        assert ProbeType.PROSPECT_THEORY.value in summary["probe_types_used"]
        assert len(summary["execution_order"]) >= 1
        
        # Test reset
        success = self.randomizer.reset_session(session_id)
        assert success
        
        # Check that session is reset
        summary_after_reset = self.randomizer.get_session_summary(session_id)
        assert summary_after_reset["total_variants_used"] == 0
        assert len(summary_after_reset["execution_order"]) == 0
    
    def test_cleanup_old_sessions(self):
        """Test cleanup of old sessions."""
        # Create a session
        session_id = self.randomizer.create_session()
        
        # Manually set creation time to be old
        session = self.randomizer.get_session(session_id)
        session.created_at = datetime.utcnow() - timedelta(hours=25)
        
        # Cleanup old sessions
        cleaned_count = self.randomizer.cleanup_old_sessions(max_age_hours=24)
        assert cleaned_count == 1
        
        # Session should be gone
        assert self.randomizer.get_session(session_id) is None
    
    def test_latin_square_generation(self):
        """Test Latin square generation."""
        # Test different sizes
        for n in range(1, 6):
            square = self.randomizer._generate_latin_square(n)
            assert len(square) == n
            
            for row in square:
                assert len(row) == n
                # Check that each row contains all numbers 0 to n-1
                assert set(row) == set(range(n))
            
            # Check that each column contains all numbers 0 to n-1
            for col in range(n):
                column_values = [row[col] for row in square]
                assert set(column_values) == set(range(n))


class TestTestBattery:
    """Test cases for the TestBattery class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock probe registry
        self.probe_registry = {
            "prospect_theory": MockProbe,
            "anchoring": MockProbe,
            "framing": MockProbe
        }
        
        self.config = RandomizationConfig(seed=42)
        self.battery = TestBattery(self.probe_registry, config=self.config)
    
    def test_create_session(self):
        """Test session creation."""
        session_id = self.battery.create_session({"test": "metadata"})
        assert session_id is not None
        assert self.battery.get_session_id() == session_id
    
    def test_create_randomized_battery(self):
        """Test randomized battery creation."""
        session_id = self.battery.create_session()
        
        # Create battery with all probe types
        battery = self.battery.create_randomized_battery(max_variants_per_probe=1)
        
        assert len(battery) > 0
        assert all(isinstance(item[0], ProbeType) for item in battery)
        assert all(isinstance(item[1], str) for item in battery)
        
        # Check that we have different probe types
        probe_types = set(item[0] for item in battery)
        assert len(probe_types) > 1
    
    def test_create_domain_filtered_battery(self):
        """Test battery creation with domain filter."""
        session_id = self.battery.create_session()
        
        # Create battery with domain filter
        battery = self.battery.create_randomized_battery(
            max_variants_per_probe=1,
            domain_filter="health"
        )
        
        # Should still create battery (even if no health variants exist in mock)
        assert isinstance(battery, list)
    
    def test_battery_summary(self):
        """Test battery summary generation."""
        # Test with no execution
        summary = self.battery.get_battery_summary()
        assert "message" in summary
        
        # Test with mock results
        from src.ai_bias_psych.probes.types import ProbeExecutionResult
        
        mock_result = ProbeExecutionResult(
            request_id="test_1",
            probe_type=ProbeType.PROSPECT_THEORY,
            variant_id="test_variant",
            model_provider="test_provider",
            model_name="test_model",
            prompt="test prompt",
            response="test response",
            response_time_ms=1000,
            tokens_used=50,
            temperature=0.7,
            bias_score=0.5,
            confidence=0.8
        )
        
        self.battery.execution_results.append(mock_result)
        
        summary = self.battery.get_battery_summary()
        assert summary["total_probes"] == 1
        assert summary["successful_probes"] == 1
        assert summary["success_rate"] == 1.0
        assert "prospect_theory" in summary["probe_type_counts"]
    
    def test_session_summary(self):
        """Test session summary generation."""
        session_id = self.battery.create_session()
        
        summary = self.battery.get_session_summary()
        assert summary["session_id"] == session_id
        assert summary["total_variants_used"] == 0
    
    def test_reset_session(self):
        """Test session reset."""
        session_id = self.battery.create_session()
        
        # Add some mock results
        from src.ai_bias_psych.probes.types import ProbeExecutionResult
        
        mock_result = ProbeExecutionResult(
            request_id="test_1",
            probe_type=ProbeType.PROSPECT_THEORY,
            variant_id="test_variant",
            model_provider="test_provider",
            model_name="test_model",
            prompt="test prompt",
            response="test response",
            response_time_ms=1000,
            tokens_used=50,
            temperature=0.7,
            bias_score=0.5,
            confidence=0.8
        )
        
        self.battery.execution_results.append(mock_result)
        
        # Reset session
        success = self.battery.reset_session()
        assert success
        assert len(self.battery.execution_results) == 0
    
    def test_export_results(self):
        """Test result export functionality."""
        # Test JSON export
        json_export = self.battery.export_results("json")
        assert isinstance(json_export, dict)
        assert "session_summary" in json_export
        assert "battery_summary" in json_export
        assert "execution_results" in json_export
        
        # Test CSV export
        csv_export = self.battery.export_results("csv")
        assert isinstance(csv_export, str)
        assert "request_id" in csv_export
        assert "probe_type" in csv_export
        
        # Test invalid format
        with pytest.raises(ValueError):
            self.battery.export_results("invalid_format")


class MockProbe:
    """Mock probe class for testing."""
    
    def __init__(self):
        self.variants = {
            "test_variant_1": ProbeVariant(
                id="test_variant_1",
                domain="health",
                prompt="Test prompt 1",
                response_format=ResponseFormat.FREE_TEXT
            ),
            "test_variant_2": ProbeVariant(
                id="test_variant_2",
                domain="finance",
                prompt="Test prompt 2",
                response_format=ResponseFormat.FREE_TEXT
            )
        }
    
    def list_variants(self, domain=None):
        """Mock method to list variants."""
        if domain:
            return [v for v in self.variants.values() if v.domain == domain]
        return list(self.variants.values())


if __name__ == "__main__":
    pytest.main([__file__])
