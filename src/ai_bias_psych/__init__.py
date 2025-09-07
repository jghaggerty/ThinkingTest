"""
AI Bias Psychologist - A diagnostic tool for detecting cognitive biases in LLMs.

This package provides comprehensive bias detection capabilities for Large Language Models,
including 10 core cognitive biases, multi-LLM support, real-time dashboard, and statistical analysis.
"""

__version__ = "0.1.0"
__author__ = "AI Bias Psychologist Team"
__email__ = "team@ai-bias-psych.org"

# Core module imports - import in order to avoid circular dependencies
from . import probes
from . import llm
from . import analytics
from . import storage
from . import api
from . import web

# Main application components
from .main import create_app
from .cli import app as cli_app

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "probes", 
    "llm",
    "analytics",
    "storage",
    "api",
    "web",
    "create_app",
    "cli_app",
]
