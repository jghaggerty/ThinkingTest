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

from .base import BaseProbe
from .types import ProbeType, ResponseFormat, ProbeVariant, ProbeExecutionResult
from .randomization import ProbeRandomizer, RandomizationConfig, RandomizationStrategy, OrderEffectPrevention, SessionContext
from .response_formats import (
    ResponseFormatProcessor, ResponseFormatConfig, ResponseParseResult,
    MultipleChoiceOptions, NumericRange, StructuredFormatType
)
from .format_examples import (
    create_multiple_choice_variants, create_numeric_variants,
    create_boolean_variants, create_free_text_variants, get_all_format_examples
)

# Import all bias probe implementations
# TODO: Uncomment these imports as probe implementations are completed
from .prospect_theory import ProspectTheoryProbe
# from .anchoring import AnchoringProbe
# from .availability import AvailabilityProbe
# from .framing import FramingProbe
# from .sunk_cost import SunkCostProbe
# from .optimism import OptimismProbe
# from .confirmation import ConfirmationProbe
# from .base_rate import BaseRateProbe
# from .conjunction import ConjunctionProbe
# from .overconfidence import OverconfidenceProbe

# Registry of all available probes
# TODO: Update this registry as probe implementations are completed
PROBE_REGISTRY = {
    "prospect_theory": ProspectTheoryProbe,
    # "anchoring": AnchoringProbe,
    # "availability": AvailabilityProbe,
    # "framing": FramingProbe,
    # "sunk_cost": SunkCostProbe,
    # "optimism": OptimismProbe,
    # "confirmation": ConfirmationProbe,
    # "base_rate": BaseRateProbe,
    # "conjunction": ConjunctionProbe,
    # "overconfidence": OverconfidenceProbe,
}

__all__ = [
    "BaseProbe",
    "ProbeType",
    "ResponseFormat",
    "ProbeVariant",
    "ProbeExecutionResult",
    "ProbeRandomizer",
    "RandomizationConfig",
    "RandomizationStrategy",
    "OrderEffectPrevention",
    "SessionContext",
    "ResponseFormatProcessor",
    "ResponseFormatConfig",
    "ResponseParseResult",
    "MultipleChoiceOptions",
    "NumericRange",
    "StructuredFormatType",
    "create_multiple_choice_variants",
    "create_numeric_variants",
    "create_boolean_variants",
    "create_free_text_variants",
    "get_all_format_examples",
    "PROBE_REGISTRY",
    # TODO: Add probe implementations to __all__ as they are completed
    "ProspectTheoryProbe",
    # "AnchoringProbe",
    # "AvailabilityProbe",
    # "FramingProbe",
    # "SunkCostProbe",
    # "OptimismProbe",
    # "ConfirmationProbe",
    # "BaseRateProbe",
    # "ConjunctionProbe",
    # "OverconfidenceProbe",
]
