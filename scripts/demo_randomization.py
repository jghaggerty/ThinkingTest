#!/usr/bin/env python3
"""
Demonstration script for probe randomization and order effect prevention.

This script shows how to use the randomization system to create
scientifically rigorous bias testing sessions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_bias_psych.probes import (
    ProbeRandomizer, RandomizationConfig, RandomizationStrategy, 
    OrderEffectPrevention, ProbeType, ProbeVariant, ResponseFormat
)


def demo_randomization_strategies():
    """Demonstrate different randomization strategies."""
    print("=== Probe Randomization Strategies Demo ===\n")
    
    # Create test variants
    test_variants = [
        ProbeVariant(
            id="health_1",
            domain="health",
            prompt="Health scenario 1",
            response_format=ResponseFormat.FREE_TEXT
        ),
        ProbeVariant(
            id="health_2", 
            domain="health",
            prompt="Health scenario 2",
            response_format=ResponseFormat.FREE_TEXT
        ),
        ProbeVariant(
            id="finance_1",
            domain="finance", 
            prompt="Finance scenario 1",
            response_format=ResponseFormat.FREE_TEXT
        ),
        ProbeVariant(
            id="finance_2",
            domain="finance",
            prompt="Finance scenario 2", 
            response_format=ResponseFormat.FREE_TEXT
        ),
        ProbeVariant(
            id="tech_1",
            domain="tech",
            prompt="Tech scenario 1",
            response_format=ResponseFormat.FREE_TEXT
        )
    ]
    
    # Test different strategies
    strategies = [
        RandomizationStrategy.SIMPLE_RANDOM,
        RandomizationStrategy.DOMAIN_BALANCED,
        RandomizationStrategy.COUNTERBALANCED,
        RandomizationStrategy.LATIN_SQUARE,
        RandomizationStrategy.BLOCK_RANDOMIZED
    ]
    
    for strategy in strategies:
        print(f"--- {strategy.value.upper()} Strategy ---")
        
        config = RandomizationConfig(
            strategy=strategy,
            order_prevention=OrderEffectPrevention.RANDOM_ORDER,
            prevent_repeats=True,
            seed=42
        )
        
        randomizer = ProbeRandomizer(config)
        session_id = randomizer.create_session()
        
        # Select 6 variants to see the pattern
        selected = []
        for i in range(6):
            try:
                variant = randomizer.select_variant(
                    ProbeType.PROSPECT_THEORY,
                    test_variants,
                    session_id
                )
                selected.append(variant.id)
            except ValueError:
                break  # No more variants available
        
        print(f"Selected variants: {selected}")
        
        # Show domain distribution
        domain_counts = {}
        for variant_id in selected:
            domain = next(v.domain for v in test_variants if v.id == variant_id)
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        print(f"Domain distribution: {domain_counts}")
        print()


def demo_order_effect_prevention():
    """Demonstrate order effect prevention strategies."""
    print("=== Order Effect Prevention Demo ===\n")
    
    probe_types = [
        ProbeType.PROSPECT_THEORY,
        ProbeType.ANCHORING,
        ProbeType.FRAMING,
        ProbeType.AVAILABILITY
    ]
    
    strategies = [
        OrderEffectPrevention.RANDOM_ORDER,
        OrderEffectPrevention.COUNTERBALANCED,
        OrderEffectPrevention.LATIN_SQUARE,
        OrderEffectPrevention.BLOCK_RANDOMIZED
    ]
    
    for strategy in strategies:
        print(f"--- {strategy.value.upper()} Order Prevention ---")
        
        config = RandomizationConfig(
            strategy=RandomizationStrategy.SIMPLE_RANDOM,
            order_prevention=strategy,
            seed=42
        )
        
        randomizer = ProbeRandomizer(config)
        session_id = randomizer.create_session()
        
        # Get multiple orders to see the pattern
        orders = []
        for i in range(3):
            try:
                order = randomizer.select_probe_order(probe_types, session_id)
                orders.append([pt.value for pt in order])
            except Exception as e:
                print(f"Error: {e}")
                break
        
        for i, order in enumerate(orders):
            print(f"  Order {i+1}: {order}")
        print()


def demo_session_tracking():
    """Demonstrate session tracking functionality."""
    print("=== Session Tracking Demo ===\n")
    
    config = RandomizationConfig(
        strategy=RandomizationStrategy.DOMAIN_BALANCED,
        order_prevention=OrderEffectPrevention.COUNTERBALANCED,
        prevent_repeats=True,
        seed=42
    )
    
    randomizer = ProbeRandomizer(config)
    session_id = randomizer.create_session({"demo": "session_tracking"})
    
    print(f"Created session: {session_id}")
    
    # Create test variants
    test_variants = [
        ProbeVariant(
            id=f"variant_{i}",
            domain=["health", "finance", "tech"][i % 3],
            prompt=f"Test prompt {i}",
            response_format=ResponseFormat.FREE_TEXT
        )
        for i in range(9)
    ]
    
    # Execute some probes
    probe_types = [ProbeType.PROSPECT_THEORY, ProbeType.ANCHORING, ProbeType.FRAMING]
    
    for probe_type in probe_types:
        try:
            variant = randomizer.select_variant(
                probe_type,
                test_variants,
                session_id
            )
            print(f"Selected {probe_type.value}: {variant.id} (domain: {variant.domain})")
        except ValueError as e:
            print(f"Error selecting variant for {probe_type.value}: {e}")
    
    # Show session summary
    summary = randomizer.get_session_summary(session_id)
    print(f"\nSession Summary:")
    print(f"  Total variants used: {summary['total_variants_used']}")
    print(f"  Probe types used: {summary['probe_types_used']}")
    print(f"  Domain usage: {summary['domain_usage']}")
    print(f"  Execution order: {summary['execution_order']}")
    
    # Reset session
    print(f"\nResetting session...")
    success = randomizer.reset_session(session_id)
    print(f"Reset successful: {success}")
    
    # Show summary after reset
    summary_after = randomizer.get_session_summary(session_id)
    print(f"After reset - Total variants used: {summary_after['total_variants_used']}")


def demo_test_battery():
    """Demonstrate test battery creation."""
    print("=== Test Battery Demo ===\n")
    
    from ai_bias_psych.probes.battery_manager import TestBattery
    
    # Mock probe registry
    class MockProbe:
        def __init__(self):
            self.variants = {
                f"variant_{i}": ProbeVariant(
                    id=f"variant_{i}",
                    domain=["health", "finance", "tech"][i % 3],
                    prompt=f"Test prompt {i}",
                    response_format=ResponseFormat.FREE_TEXT
                )
                for i in range(6)
            }
        
        def list_variants(self, domain=None):
            if domain:
                return [v for v in self.variants.values() if v.domain == domain]
            return list(self.variants.values())
    
    probe_registry = {
        "prospect_theory": MockProbe,
        "anchoring": MockProbe,
        "framing": MockProbe
    }
    
    config = RandomizationConfig(
        strategy=RandomizationStrategy.DOMAIN_BALANCED,
        order_prevention=OrderEffectPrevention.COUNTERBALANCED,
        prevent_repeats=True,
        seed=42
    )
    
    battery = TestBattery(probe_registry, config=config)
    session_id = battery.create_session({"demo": "test_battery"})
    
    print(f"Created test battery session: {session_id}")
    
    # Create randomized battery
    test_battery = battery.create_randomized_battery(max_variants_per_probe=2)
    
    print(f"Created battery with {len(test_battery)} probe-variant combinations:")
    for probe_type, variant_id in test_battery:
        print(f"  {probe_type.value}: {variant_id}")
    
    # Show battery summary
    summary = battery.get_battery_summary()
    print(f"\nBattery Summary:")
    print(f"  Total probes: {summary.get('total_probes', 0)}")
    print(f"  Success rate: {summary.get('success_rate', 0):.2%}")


if __name__ == "__main__":
    print("AI Bias Psychologist - Randomization System Demo\n")
    print("=" * 60)
    
    try:
        demo_randomization_strategies()
        demo_order_effect_prevention()
        demo_session_tracking()
        demo_test_battery()
        
        print("=" * 60)
        print("Demo completed successfully!")
        print("\nThe randomization system provides:")
        print("• Multiple randomization strategies for variant selection")
        print("• Order effect prevention for probe sequences")
        print("• Session tracking to prevent repeated variants")
        print("• Domain balancing for fair representation")
        print("• Test battery management for comprehensive testing")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
