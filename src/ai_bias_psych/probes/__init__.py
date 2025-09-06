"""
Bias probe implementations for AI Bias Psychologist.

This module contains all 10 core cognitive bias probes with their variants:
- Prospect Theory / Loss Aversion
- Anchoring
- Availability Heuristic
- Framing Effect
- Sunk Cost Fallacy
- Optimism Bias
- Confirmation Bias
- Base-Rate Neglect
- Conjunction Fallacy
- Overconfidence Bias
"""

from .base import BaseProbe, ProbeType, ResponseFormat

# Import all bias probe implementations
from .prospect_theory import ProspectTheoryProbe
from .anchoring import AnchoringProbe
from .availability import AvailabilityProbe
from .framing import FramingProbe
from .sunk_cost import SunkCostProbe
from .optimism import OptimismProbe
from .confirmation import ConfirmationProbe
from .base_rate import BaseRateProbe
from .conjunction import ConjunctionProbe
from .overconfidence import OverconfidenceProbe

# Registry of all available probes
PROBE_REGISTRY = {
    "prospect_theory": ProspectTheoryProbe,
    "anchoring": AnchoringProbe,
    "availability": AvailabilityProbe,
    "framing": FramingProbe,
    "sunk_cost": SunkCostProbe,
    "optimism": OptimismProbe,
    "confirmation": ConfirmationProbe,
    "base_rate": BaseRateProbe,
    "conjunction": ConjunctionProbe,
    "overconfidence": OverconfidenceProbe,
}

__all__ = [
    "BaseProbe",
    "ProbeType",
    "ResponseFormat",
    "ProspectTheoryProbe",
    "AnchoringProbe",
    "AvailabilityProbe",
    "FramingProbe",
    "SunkCostProbe",
    "OptimismProbe",
    "ConfirmationProbe",
    "BaseRateProbe",
    "ConjunctionProbe",
    "OverconfidenceProbe",
    "PROBE_REGISTRY",
]
