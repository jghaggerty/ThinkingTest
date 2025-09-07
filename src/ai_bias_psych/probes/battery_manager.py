"""
Test battery manager for comprehensive bias testing.

This module provides a high-level interface for creating and managing
test batteries that execute multiple bias probes with proper randomization
and order effect prevention.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import logging

from .base import BaseProbe
from .types import ProbeType, ProbeExecutionResult
from .randomization import ProbeRandomizer, RandomizationConfig, SessionContext
from ..llm.base import BaseLLMClient
from ..models.probe import ProbeRequest


class TestBattery:
    """
    A test battery for comprehensive bias testing across multiple probe types.
    
    This class manages the execution of multiple bias probes with proper
    randomization, order effect prevention, and session tracking.
    """
    
    def __init__(self, 
                 probe_registry: Dict[str, BaseProbe],
                 randomizer: Optional[ProbeRandomizer] = None,
                 config: Optional[RandomizationConfig] = None):
        """
        Initialize the test battery.
        
        Args:
            probe_registry: Registry of available probe types and their implementations
            randomizer: Optional probe randomizer, creates default if None
            config: Optional randomization configuration
        """
        self.probe_registry = probe_registry
        self.randomizer = randomizer or ProbeRandomizer(config)
        self.logger = logging.getLogger("probe.battery")
        
        # Session tracking
        self.current_session_id: Optional[str] = None
        self.execution_results: List[ProbeExecutionResult] = []
        
    def create_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new test session.
        
        Args:
            metadata: Optional metadata for the session
            
        Returns:
            Session ID for tracking
        """
        self.current_session_id = self.randomizer.create_session(metadata)
        self.execution_results.clear()
        
        self.logger.info(f"Created test battery session: {self.current_session_id}")
        return self.current_session_id
    
    def get_session_id(self) -> Optional[str]:
        """
        Get the current session ID.
        
        Returns:
            Current session ID if exists, None otherwise
        """
        return self.current_session_id
    
    def create_randomized_battery(self, 
                                 probe_types: Optional[List[ProbeType]] = None,
                                 max_variants_per_probe: int = 2,
                                 domain_filter: Optional[str] = None) -> List[Tuple[ProbeType, str]]:
        """
        Create a randomized test battery with specified probe types and variants.
        
        Args:
            probe_types: Optional list of probe types to include, uses all if None
            max_variants_per_probe: Maximum variants to select per probe type
            domain_filter: Optional domain filter for variant selection
            
        Returns:
            List of (probe_type, variant_id) tuples for execution
        """
        if not self.current_session_id:
            raise ValueError("No active session. Call create_session() first.")
        
        # Use all probe types if none specified
        if probe_types is None:
            probe_types = [ProbeType(pt) for pt in self.probe_registry.keys() 
                          if pt in [p.value for p in ProbeType]]
        
        battery = []
        
        # Select probe order
        ordered_probes = self.randomizer.select_probe_order(probe_types, self.current_session_id)
        
        # Select variants for each probe
        for probe_type in ordered_probes:
            probe_class = self.probe_registry.get(probe_type.value)
            if not probe_class:
                continue
            
            # Create probe instance and get variants
            probe_instance = probe_class()
            available_variants = list(probe_instance.variants.values())
            
            if not available_variants:
                continue
            
            # Filter by domain if specified
            if domain_filter:
                available_variants = [v for v in available_variants if v.domain == domain_filter]
                if not available_variants:
                    continue
            
            # Select variants for this probe
            selected_variants = []
            for _ in range(min(max_variants_per_probe, len(available_variants))):
                try:
                    variant = self.randomizer.select_variant(
                        probe_type=probe_type,
                        available_variants=available_variants,
                        session_id=self.current_session_id,
                        domain=domain_filter
                    )
                    selected_variants.append(variant)
                    
                    # Remove selected variant from available to avoid duplicates
                    available_variants = [v for v in available_variants if v.id != variant.id]
                    
                except ValueError:
                    break  # No more suitable variants
            
            # Add to battery
            for variant in selected_variants:
                battery.append((probe_type, variant.id))
        
        self.logger.info(
            f"Created randomized battery with {len(battery)} probe-variant combinations "
            f"for session {self.current_session_id}"
        )
        
        return battery
    
    async def execute_battery(self, 
                             battery: List[Tuple[ProbeType, str]],
                             llm_client: BaseLLMClient,
                             temperature: float = 0.7,
                             max_tokens: int = 500,
                             concurrent_limit: int = 3) -> List[ProbeExecutionResult]:
        """
        Execute a test battery with the specified LLM client.
        
        Args:
            battery: List of (probe_type, variant_id) tuples to execute
            llm_client: The LLM client to use for execution
            temperature: Temperature setting for LLM generation
            max_tokens: Maximum tokens for LLM responses
            concurrent_limit: Maximum number of concurrent executions
            
        Returns:
            List of execution results
        """
        if not self.current_session_id:
            raise ValueError("No active session. Call create_session() first.")
        
        self.logger.info(f"Executing battery with {len(battery)} probes")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        # Create execution tasks
        tasks = []
        for probe_type, variant_id in battery:
            task = self._execute_probe_with_semaphore(
                semaphore, probe_type, variant_id, llm_client, temperature, max_tokens
            )
            tasks.append(task)
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        execution_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Probe execution failed: {result}")
                # Create error result
                error_result = ProbeExecutionResult(
                    request_id=f"error_{i}",
                    probe_type=battery[i][0],
                    variant_id=battery[i][1],
                    model_provider=llm_client.provider_name,
                    model_name=llm_client.model_name,
                    prompt="",
                    response=f"Error: {str(result)}",
                    response_time_ms=0,
                    tokens_used=0,
                    temperature=temperature,
                    bias_score=0.0,
                    confidence=0.0,
                    metadata={"error": str(result)}
                )
                execution_results.append(error_result)
            else:
                execution_results.append(result)
        
        # Store results
        self.execution_results.extend(execution_results)
        
        self.logger.info(f"Battery execution completed: {len(execution_results)} results")
        return execution_results
    
    async def _execute_probe_with_semaphore(self, 
                                          semaphore: asyncio.Semaphore,
                                          probe_type: ProbeType,
                                          variant_id: str,
                                          llm_client: BaseLLMClient,
                                          temperature: float,
                                          max_tokens: int) -> ProbeExecutionResult:
        """
        Execute a single probe with semaphore for concurrency control.
        
        Args:
            semaphore: Semaphore for concurrency control
            probe_type: The probe type to execute
            variant_id: The variant ID to execute
            llm_client: The LLM client to use
            temperature: Temperature setting
            max_tokens: Maximum tokens
            
        Returns:
            Execution result
        """
        async with semaphore:
            return await self._execute_single_probe(
                probe_type, variant_id, llm_client, temperature, max_tokens
            )
    
    async def _execute_single_probe(self, 
                                   probe_type: ProbeType,
                                   variant_id: str,
                                   llm_client: BaseLLMClient,
                                   temperature: float,
                                   max_tokens: int) -> ProbeExecutionResult:
        """
        Execute a single probe.
        
        Args:
            probe_type: The probe type to execute
            variant_id: The variant ID to execute
            llm_client: The LLM client to use
            temperature: Temperature setting
            max_tokens: Maximum tokens
            
        Returns:
            Execution result
        """
        # Get probe instance
        probe_class = self.probe_registry.get(probe_type.value)
        if not probe_class:
            raise ValueError(f"Probe type not found: {probe_type.value}")
        
        probe_instance = probe_class()
        
        # Create probe request
        request = ProbeRequest(
            probe_type=probe_type.value,
            variant_id=variant_id,
            model_provider=llm_client.provider_name,
            model_name=llm_client.model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            metadata={
                "session_id": self.current_session_id,
                "battery_execution": True
            }
        )
        
        # Execute probe
        result = await probe_instance.execute(request, llm_client)
        
        self.logger.debug(
            f"Executed {probe_type.value} variant {variant_id}: "
            f"score={result.bias_score:.3f}, confidence={result.confidence:.3f}"
        )
        
        return result
    
    def get_battery_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for the current battery execution.
        
        Returns:
            Dictionary containing battery summary statistics
        """
        if not self.execution_results:
            return {"message": "No battery executed yet"}
        
        # Calculate summary statistics
        total_probes = len(self.execution_results)
        successful_probes = len([r for r in self.execution_results if r.bias_score >= 0])
        
        # Group by probe type
        probe_type_counts = {}
        probe_type_scores = {}
        
        for result in self.execution_results:
            probe_type = result.probe_type.value
            if probe_type not in probe_type_counts:
                probe_type_counts[probe_type] = 0
                probe_type_scores[probe_type] = []
            
            probe_type_counts[probe_type] += 1
            probe_type_scores[probe_type].append(result.bias_score)
        
        # Calculate average scores by probe type
        avg_scores = {}
        for probe_type, scores in probe_type_scores.items():
            avg_scores[probe_type] = sum(scores) / len(scores) if scores else 0.0
        
        # Calculate overall statistics
        all_scores = [r.bias_score for r in self.execution_results]
        avg_bias_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        max_bias_score = max(all_scores) if all_scores else 0.0
        min_bias_score = min(all_scores) if all_scores else 0.0
        
        # Calculate confidence statistics
        all_confidences = [r.confidence for r in self.execution_results]
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        
        # Calculate response time statistics
        all_response_times = [r.response_time_ms for r in self.execution_results]
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0.0
        
        return {
            "session_id": self.current_session_id,
            "total_probes": total_probes,
            "successful_probes": successful_probes,
            "success_rate": successful_probes / total_probes if total_probes > 0 else 0.0,
            "probe_type_counts": probe_type_counts,
            "average_scores_by_type": avg_scores,
            "overall_statistics": {
                "average_bias_score": avg_bias_score,
                "max_bias_score": max_bias_score,
                "min_bias_score": min_bias_score,
                "average_confidence": avg_confidence,
                "average_response_time_ms": avg_response_time
            },
            "execution_timestamp": datetime.utcnow().isoformat()
        }
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for the current session.
        
        Returns:
            Dictionary containing session summary statistics
        """
        if not self.current_session_id:
            return {"message": "No active session"}
        
        return self.randomizer.get_session_summary(self.current_session_id)
    
    def reset_session(self) -> bool:
        """
        Reset the current session to clear all tracking information.
        
        Returns:
            True if session was reset, False if no active session
        """
        if not self.current_session_id:
            return False
        
        success = self.randomizer.reset_session(self.current_session_id)
        if success:
            self.execution_results.clear()
            self.logger.info(f"Reset session: {self.current_session_id}")
        
        return success
    
    def configure_randomization(self, config: RandomizationConfig) -> None:
        """
        Configure the randomization strategy for the battery.
        
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
    
    def export_results(self, format: str = "json") -> Union[Dict[str, Any], str]:
        """
        Export battery execution results in the specified format.
        
        Args:
            format: Export format ("json" or "csv")
            
        Returns:
            Exported results in the specified format
        """
        if format == "json":
            return {
                "session_summary": self.get_session_summary(),
                "battery_summary": self.get_battery_summary(),
                "execution_results": [
                    {
                        "request_id": r.request_id,
                        "probe_type": r.probe_type.value,
                        "variant_id": r.variant_id,
                        "model_provider": r.model_provider,
                        "model_name": r.model_name,
                        "bias_score": r.bias_score,
                        "confidence": r.confidence,
                        "response_time_ms": r.response_time_ms,
                        "tokens_used": r.tokens_used,
                        "temperature": r.temperature,
                        "created_at": r.created_at.isoformat(),
                        "metadata": r.metadata
                    }
                    for r in self.execution_results
                ]
            }
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "request_id", "probe_type", "variant_id", "model_provider", 
                "model_name", "bias_score", "confidence", "response_time_ms",
                "tokens_used", "temperature", "created_at"
            ])
            
            # Write data
            for result in self.execution_results:
                writer.writerow([
                    result.request_id,
                    result.probe_type.value,
                    result.variant_id,
                    result.model_provider,
                    result.model_name,
                    result.bias_score,
                    result.confidence,
                    result.response_time_ms,
                    result.tokens_used,
                    result.temperature,
                    result.created_at.isoformat()
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
