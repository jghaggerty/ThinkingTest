"""
Base LLM client interface for AI Bias Psychologist.

This module defines the abstract base class and common data structures
for all LLM client implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class LLMResponse(BaseModel):
    """Response from an LLM client."""
    content: str = Field(..., description="The response content")
    model: str = Field(..., description="Model used for the response")
    provider: str = Field(..., description="LLM provider")
    tokens_used: int = Field(..., description="Number of tokens used")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    temperature: float = Field(..., description="Temperature used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LLMError(Exception):
    """Exception raised by LLM clients."""
    def __init__(self, message: str, provider: str, model: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.provider = provider
        self.model = model
        self.error_code = error_code


class BaseLLMClient(ABC):
    """
    Abstract base class for all LLM client implementations.
    
    This class defines the common interface that all LLM providers must implement.
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the LLM client.
        
        Args:
            api_key: API key for the LLM provider
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The input prompt
            model: Model name to use
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional model-specific parameters
            
        Returns:
            LLMResponse object with the generated content
            
        Raises:
            LLMError: If the request fails
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models for this provider.
        
        Returns:
            List of available model names
        """
        pass
    
    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """
        Validate that a model is available for this provider.
        
        Args:
            model: Model name to validate
            
        Returns:
            True if model is available, False otherwise
        """
        pass
    
    def get_provider_name(self) -> str:
        """
        Get the name of this LLM provider.
        
        Returns:
            Provider name
        """
        return self.__class__.__name__.replace("Client", "").lower()
