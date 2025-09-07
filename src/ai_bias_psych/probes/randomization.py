"""
Probe randomization and order effect prevention system.

This module provides comprehensive randomization and order effect prevention
for bias probe execution, ensuring scientific rigor in bias detection.
"""

import random
import uuid
from typing import Dict, Any, List, Optional, Set, Tuple
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging

from .types import ProbeVariant, ProbeType


class RandomizationStrategy(str, Enum):
    """Strategies for probe variant randomization."""
    SIMPLE_RANDOM = "simple_random"
    DOMAIN_BALANCED = "domain_balanced"
    COUNTERBALANCED = "counterbalanced"
    LATIN_SQUARE = "latin_square"
    BLOCK_RANDOMIZED = "block_randomized"


class OrderEffectPrevention(str, Enum):
    """Strategies for preventing order effects."""
    NONE = "none"
    RANDOM_ORDER = "random_order"
    COUNTERBALANCED = "counterbalanced"
    LATIN_SQUARE = "latin_square"
    BLOCK_RANDOMIZED = "block_randomized"


@dataclass
class SessionContext:
    """Context for tracking probe execution within a session."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    used_variants: Set[str] = field(default_factory=set)
    used_probe_types: Set[ProbeType] = field(default_factory=set)
    execution_order: List[str] = field(default_factory=list)
    domain_usage: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_execution: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RandomizationConfig:
    """Configuration for probe randomization."""
    strategy: RandomizationStrategy = RandomizationStrategy.DOMAIN_BALANCED
    order_prevention: OrderEffectPrevention = OrderEffectPrevention.COUNTERBALANCED
    max_variants_per_domain: int = 3
    min_time_between_similar: timedelta = timedelta(minutes=5)
    prevent_repeats: bool = True
    balance_domains: bool = True
    latin_square_size: int = 4
    block_size: int = 6
    seed: Optional[int] = None


class ProbeRandomizer:
    """
    Comprehensive probe randomization and order effect prevention system.
    
    This class provides sophisticated randomization strategies to ensure:
    - Balanced domain representation
    - Prevention of order effects
    - Avoidance of repeated variants within sessions
    - Counterbalancing of probe types and variants
    - Scientific rigor in bias detection
    """
    
    def __init__(self, config: Optional[RandomizationConfig] = None):
        """
        Initialize the probe randomizer.
        
        Args:
            config: Randomization configuration, uses defaults if None
        """
        self.config = config or RandomizationConfig()
        self.logger = logging.getLogger("probe.randomizer")
        
        # Set random seed if provided
        if self.config.seed is not None:
            random.seed(self.config.seed)
            self.logger.info(f"Random seed set to: {self.config.seed}")
        
        # Session tracking
        self.sessions: Dict[str, SessionContext] = {}
        
        # Order effect prevention data structures
        self._latin_squares: Dict[int, List[List[int]]] = {}
        self._counterbalance_orders: Dict[str, deque] = {}
        
    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new probe execution session.
        
        Args:
            metadata: Optional metadata for the session
            
        Returns:
            Session ID for tracking
        """
        session = SessionContext(metadata=metadata or {})
        self.sessions[session.session_id] = session
        
        self.logger.info(f"Created new probe session: {session.session_id}")
        return session.session_id
    
    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Get session context by ID.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Session context if found, None otherwise
        """
        return self.sessions.get(session_id)
    
    def select_variant(self, 
                      probe_type: ProbeType,
                      available_variants: List[ProbeVariant],
                      session_id: Optional[str] = None,
                      domain: Optional[str] = None) -> ProbeVariant:
        """
        Select a variant using the configured randomization strategy.
        
        Args:
            probe_type: The type of probe being executed
            available_variants: List of available variants for this probe
            session_id: Optional session ID for tracking
            domain: Optional domain filter
            
        Returns:
            Selected probe variant
            
        Raises:
            ValueError: If no suitable variant can be selected
        """
        if not available_variants:
            raise ValueError(f"No variants available for probe type: {probe_type}")
        
        # Filter by domain if specified
        if domain:
            available_variants = [v for v in available_variants if v.domain == domain]
            if not available_variants:
                raise ValueError(f"No variants available for domain: {domain}")
        
        # Get session context
        session = None
        if session_id:
            session = self.get_session(session_id)
        
        # Apply randomization strategy
        if self.config.strategy == RandomizationStrategy.SIMPLE_RANDOM:
            selected = self._simple_random_selection(available_variants, session)
        elif self.config.strategy == RandomizationStrategy.DOMAIN_BALANCED:
            selected = self._domain_balanced_selection(available_variants, session)
        elif self.config.strategy == RandomizationStrategy.COUNTERBALANCED:
            selected = self._counterbalanced_selection(available_variants, session, probe_type)
        elif self.config.strategy == RandomizationStrategy.LATIN_SQUARE:
            selected = self._latin_square_selection(available_variants, session, probe_type)
        elif self.config.strategy == RandomizationStrategy.BLOCK_RANDOMIZED:
            selected = self._block_randomized_selection(available_variants, session, probe_type)
        else:
            selected = self._simple_random_selection(available_variants, session)
        
        # Update session tracking
        if session:
            self._update_session_tracking(session, selected, probe_type)
        
        self.logger.debug(
            f"Selected variant {selected.id} for probe {probe_type.value} "
            f"using strategy {self.config.strategy.value}"
        )
        
        return selected
    
    def select_probe_order(self, 
                          probe_types: List[ProbeType],
                          session_id: Optional[str] = None) -> List[ProbeType]:
        """
        Select execution order for multiple probe types to prevent order effects.
        
        Args:
            probe_types: List of probe types to order
            session_id: Optional session ID for tracking
            
        Returns:
            Ordered list of probe types
        """
        if not probe_types:
            return []
        
        if len(probe_types) == 1:
            return probe_types
        
        # Get session context
        session = None
        if session_id:
            session = self.get_session(session_id)
        
        # Apply order effect prevention strategy
        if self.config.order_prevention == OrderEffectPrevention.RANDOM_ORDER:
            ordered = self._random_order(probe_types, session)
        elif self.config.order_prevention == OrderEffectPrevention.COUNTERBALANCED:
            ordered = self._counterbalanced_order(probe_types, session)
        elif self.config.order_prevention == OrderEffectPrevention.LATIN_SQUARE:
            ordered = self._latin_square_order(probe_types, session)
        elif self.config.order_prevention == OrderEffectPrevention.BLOCK_RANDOMIZED:
            ordered = self._block_randomized_order(probe_types, session)
        else:
            ordered = probe_types  # No randomization
        
        self.logger.debug(
            f"Selected probe order: {[p.value for p in ordered]} "
            f"using strategy {self.config.order_prevention.value}"
        )
        
        return ordered
    
    def create_test_battery(self, 
                           probe_registry: Dict[str, Any],
                           session_id: Optional[str] = None,
                           max_variants_per_probe: int = 2) -> List[Tuple[ProbeType, ProbeVariant]]:
        """
        Create a randomized test battery with multiple probes and variants.
        
        Args:
            probe_registry: Registry of available probe types and their implementations
            session_id: Optional session ID for tracking
            max_variants_per_probe: Maximum variants to select per probe type
            
        Returns:
            List of (probe_type, variant) tuples for execution
        """
        battery = []
        session = self.get_session(session_id) if session_id else None
        
        # Get all available probe types
        probe_types = [ProbeType(pt) for pt in probe_registry.keys() 
                      if pt in [p.value for p in ProbeType]]
        
        # Select probe order
        ordered_probes = self.select_probe_order(probe_types, session_id)
        
        # Select variants for each probe
        for probe_type in ordered_probes:
            probe_class = probe_registry.get(probe_type.value)
            if not probe_class:
                continue
            
            # Create probe instance and get variants
            probe_instance = probe_class()
            available_variants = list(probe_instance.variants.values())
            
            if not available_variants:
                continue
            
            # Select variants for this probe
            selected_variants = []
            for _ in range(min(max_variants_per_probe, len(available_variants))):
                try:
                    variant = self.select_variant(
                        probe_type=probe_type,
                        available_variants=available_variants,
                        session_id=session_id
                    )
                    selected_variants.append(variant)
                    
                    # Remove selected variant from available to avoid duplicates
                    available_variants = [v for v in available_variants if v.id != variant.id]
                    
                except ValueError:
                    break  # No more suitable variants
            
            # Add to battery
            for variant in selected_variants:
                battery.append((probe_type, variant))
        
        self.logger.info(
            f"Created test battery with {len(battery)} probe-variant combinations "
            f"for session {session_id or 'no-session'}"
        )
        
        return battery
    
    def _simple_random_selection(self, 
                                variants: List[ProbeVariant],
                                session: Optional[SessionContext]) -> ProbeVariant:
        """Simple random selection without additional constraints."""
        if self.config.prevent_repeats and session:
            # Filter out already used variants
            available = [v for v in variants if v.id not in session.used_variants]
            if available:
                variants = available
        
        return random.choice(variants)
    
    def _domain_balanced_selection(self, 
                                  variants: List[ProbeVariant],
                                  session: Optional[SessionContext]) -> ProbeVariant:
        """Domain-balanced selection to ensure fair representation."""
        if not session:
            return self._simple_random_selection(variants, session)
        
        # Group variants by domain
        domain_groups = defaultdict(list)
        for variant in variants:
            domain_groups[variant.domain].append(variant)
        
        # Find domain with least usage
        min_usage = min(session.domain_usage.values()) if session.domain_usage else 0
        underused_domains = [
            domain for domain, usage in session.domain_usage.items()
            if usage <= min_usage
        ]
        
        # If no domain usage yet, or all domains are equally used, select randomly
        if not underused_domains or len(underused_domains) == len(domain_groups):
            available_domains = list(domain_groups.keys())
        else:
            available_domains = underused_domains
        
        # Select from underused domains
        selected_domain = random.choice(available_domains)
        domain_variants = domain_groups[selected_domain]
        
        # Apply repeat prevention within domain
        if self.config.prevent_repeats:
            domain_variants = [v for v in domain_variants if v.id not in session.used_variants]
            if not domain_variants:
                # Fall back to all variants in domain if all have been used
                domain_variants = domain_groups[selected_domain]
        
        return random.choice(domain_variants)
    
    def _counterbalanced_selection(self, 
                                  variants: List[ProbeVariant],
                                  session: Optional[SessionContext],
                                  probe_type: ProbeType) -> ProbeVariant:
        """Counterbalanced selection to prevent systematic biases."""
        # Create counterbalance key for this probe type
        counterbalance_key = f"{probe_type.value}_variants"
        
        # Initialize counterbalance order if not exists
        if counterbalance_key not in self._counterbalance_orders:
            variant_ids = [v.id for v in variants]
            # Create multiple counterbalanced orders
            orders = []
            for _ in range(4):  # Create 4 different orders
                order = variant_ids.copy()
                random.shuffle(order)
                orders.extend(order)
            self._counterbalance_orders[counterbalance_key] = deque(orders)
        
        # Get next variant in counterbalanced order
        counterbalance_queue = self._counterbalance_orders[counterbalance_key]
        
        # Find next available variant
        while counterbalance_queue:
            next_variant_id = counterbalance_queue.popleft()
            next_variant = next((v for v in variants if v.id == next_variant_id), None)
            
            if next_variant and (not self.config.prevent_repeats or 
                               not session or 
                               next_variant.id not in session.used_variants):
                return next_variant
        
        # Fall back to simple random if counterbalance exhausted
        return self._simple_random_selection(variants, session)
    
    def _latin_square_selection(self, 
                               variants: List[ProbeVariant],
                               session: Optional[SessionContext],
                               probe_type: ProbeType) -> ProbeVariant:
        """Latin square selection for balanced randomization."""
        n = min(len(variants), self.config.latin_square_size)
        
        # Generate or retrieve latin square
        if n not in self._latin_squares:
            self._latin_squares[n] = self._generate_latin_square(n)
        
        latin_square = self._latin_squares[n]
        
        # Determine position in latin square based on session and probe type
        session_hash = hash(session.session_id if session else "default") % n
        probe_hash = hash(probe_type.value) % n
        
        # Get variant index from latin square
        variant_index = latin_square[session_hash][probe_hash]
        
        # Map to actual variant (cycling if needed)
        actual_index = variant_index % len(variants)
        selected_variant = variants[actual_index]
        
        # Apply repeat prevention
        if self.config.prevent_repeats and session and selected_variant.id in session.used_variants:
            return self._simple_random_selection(variants, session)
        
        return selected_variant
    
    def _block_randomized_selection(self, 
                                   variants: List[ProbeVariant],
                                   session: Optional[SessionContext],
                                   probe_type: ProbeType) -> ProbeVariant:
        """Block randomized selection for controlled randomization."""
        # Create blocks of variants
        block_size = min(self.config.block_size, len(variants))
        blocks = [variants[i:i + block_size] for i in range(0, len(variants), block_size)]
        
        # Select block based on session and probe type
        session_hash = hash(session.session_id if session else "default")
        probe_hash = hash(probe_type.value)
        block_index = (session_hash + probe_hash) % len(blocks)
        
        selected_block = blocks[block_index]
        
        # Randomly select from block
        if self.config.prevent_repeats and session:
            available_in_block = [v for v in selected_block if v.id not in session.used_variants]
            if available_in_block:
                selected_block = available_in_block
        
        return random.choice(selected_block)
    
    def _random_order(self, 
                     probe_types: List[ProbeType],
                     session: Optional[SessionContext]) -> List[ProbeType]:
        """Random order selection."""
        ordered = probe_types.copy()
        random.shuffle(ordered)
        return ordered
    
    def _counterbalanced_order(self, 
                              probe_types: List[ProbeType],
                              session: Optional[SessionContext]) -> List[ProbeType]:
        """Counterbalanced order selection."""
        # Create counterbalance key
        counterbalance_key = "probe_order"
        
        # Initialize counterbalance order if not exists
        if counterbalance_key not in self._counterbalance_orders:
            # Create multiple counterbalanced orders
            orders = []
            for _ in range(4):  # Create 4 different orders
                order = [pt.value for pt in probe_types]
                random.shuffle(order)
                orders.append(order)  # Append the entire order, not extend individual items
            self._counterbalance_orders[counterbalance_key] = deque(orders)
        
        # Get next order
        counterbalance_queue = self._counterbalance_orders[counterbalance_key]
        
        if counterbalance_queue:
            next_order_values = counterbalance_queue.popleft()
            # Convert back to ProbeType objects
            ordered = [ProbeType(pt) for pt in next_order_values if pt in [p.value for p in ProbeType]]
            return ordered
        
        # Fall back to random order
        return self._random_order(probe_types, session)
    
    def _latin_square_order(self, 
                           probe_types: List[ProbeType],
                           session: Optional[SessionContext]) -> List[ProbeType]:
        """Latin square order selection."""
        n = len(probe_types)
        
        # Generate or retrieve latin square
        if n not in self._latin_squares:
            self._latin_squares[n] = self._generate_latin_square(n)
        
        latin_square = self._latin_squares[n]
        
        # Determine position in latin square based on session
        session_hash = hash(session.session_id if session else "default") % n
        
        # Get order from latin square
        order_indices = latin_square[session_hash]
        
        # Map to actual probe types
        ordered = [probe_types[i] for i in order_indices]
        return ordered
    
    def _block_randomized_order(self, 
                               probe_types: List[ProbeType],
                               session: Optional[SessionContext]) -> List[ProbeType]:
        """Block randomized order selection."""
        # Create blocks of probe types
        block_size = min(self.config.block_size, len(probe_types))
        blocks = [probe_types[i:i + block_size] for i in range(0, len(probe_types), block_size)]
        
        # Randomize order within each block
        for block in blocks:
            random.shuffle(block)
        
        # Randomize block order
        random.shuffle(blocks)
        
        # Flatten blocks
        ordered = []
        for block in blocks:
            ordered.extend(block)
        
        return ordered
    
    def _generate_latin_square(self, n: int) -> List[List[int]]:
        """Generate a latin square of size n."""
        if n <= 0:
            return []
        
        # Simple algorithm for generating latin squares
        square = []
        for i in range(n):
            row = [(i + j) % n for j in range(n)]
            square.append(row)
        
        # Randomize rows
        random.shuffle(square)
        
        # Note: We don't shuffle individual rows as that would break the Latin square property
        # Instead, we can permute columns if needed, but for now we keep the basic structure
        
        return square
    
    def _update_session_tracking(self, 
                                session: SessionContext,
                                variant: ProbeVariant,
                                probe_type: ProbeType) -> None:
        """Update session tracking information."""
        if session:  # Only update if session exists
            session.used_variants.add(variant.id)
            session.used_probe_types.add(probe_type)
            session.execution_order.append(variant.id)
            session.domain_usage[variant.domain] += 1
            session.last_execution = datetime.utcnow()
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a session.
        
        Args:
            session_id: The session identifier
            
        Returns:
            Dictionary containing session summary statistics
        """
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            "session_id": session_id,
            "created_at": session.created_at.isoformat(),
            "last_execution": session.last_execution.isoformat() if session.last_execution else None,
            "total_variants_used": len(session.used_variants),
            "probe_types_used": [pt.value for pt in session.used_probe_types],
            "domain_usage": dict(session.domain_usage),
            "execution_order": session.execution_order,
            "metadata": session.metadata
        }
    
    def reset_session(self, session_id: str) -> bool:
        """
        Reset a session to clear all tracking information.
        
        Args:
            session_id: The session identifier
            
        Returns:
            True if session was reset, False if not found
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.used_variants.clear()
        session.used_probe_types.clear()
        session.execution_order.clear()
        session.domain_usage.clear()
        session.last_execution = None
        
        self.logger.info(f"Reset session: {session_id}")
        return True
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up old sessions to prevent memory buildup.
        
        Args:
            max_age_hours: Maximum age of sessions to keep
            
        Returns:
            Number of sessions cleaned up
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if session.created_at < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        if sessions_to_remove:
            self.logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
        
        return len(sessions_to_remove)
