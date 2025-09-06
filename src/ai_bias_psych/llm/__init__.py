"""
LLM integration layer for AI Bias Psychologist.

This module provides unified interfaces for interacting with different LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude-3)
- Local models via Ollama (Llama 3, Mistral)
"""

from .base import BaseLLMClient, LLMResponse, LLMError
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .ollama_client import OllamaClient

# Registry of available LLM clients
LLM_CLIENT_REGISTRY = {
    "openai": OpenAIClient,
    "anthropic": AnthropicClient,
    "ollama": OllamaClient,
}

__all__ = [
    "BaseLLMClient",
    "LLMResponse",
    "LLMError",
    "OpenAIClient",
    "AnthropicClient",
    "OllamaClient",
    "LLM_CLIENT_REGISTRY",
]
