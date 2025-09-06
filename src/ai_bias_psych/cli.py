"""
Command-line interface for AI Bias Psychologist.

This module provides Typer-based CLI commands for:
- Running individual bias probes
- Executing full test batteries
- Managing models and configurations
- Exporting results
"""

import typer
from typing import Optional, List
from rich.console import Console
from rich.table import Table

from .probes import PROBE_REGISTRY
from .llm import LLM_CLIENT_REGISTRY

app = typer.Typer(
    name="ai-bias-psych",
    help="AI Bias Psychologist - Detect cognitive biases in LLMs",
    add_completion=False,
)
console = Console()


@app.command()
def run_probe(
    bias_type: str = typer.Argument(..., help="Type of bias to test"),
    model: str = typer.Option("gpt-4", help="LLM model to test"),
    provider: str = typer.Option("openai", help="LLM provider"),
    temperature: float = typer.Option(0.7, help="Sampling temperature"),
    output_format: str = typer.Option("json", help="Output format (json, table, csv)"),
):
    """Run a single bias probe test."""
    
    if bias_type not in PROBE_REGISTRY:
        console.print(f"[red]Error: Unknown bias type '{bias_type}'[/red]")
        console.print(f"Available bias types: {', '.join(PROBE_REGISTRY.keys())}")
        raise typer.Exit(1)
    
    if provider not in LLM_CLIENT_REGISTRY:
        console.print(f"[red]Error: Unknown provider '{provider}'[/red]")
        console.print(f"Available providers: {', '.join(LLM_CLIENT_REGISTRY.keys())}")
        raise typer.Exit(1)
    
    console.print(f"[green]Running {bias_type} probe on {model}...[/green]")
    # TODO: Implement actual probe execution
    console.print("[yellow]Probe execution not yet implemented[/yellow]")


@app.command()
def run_battery(
    models: List[str] = typer.Option(["gpt-4"], help="Models to test"),
    providers: List[str] = typer.Option(["openai"], help="LLM providers"),
    bias_types: Optional[List[str]] = typer.Option(None, help="Specific bias types to test"),
    temperature: float = typer.Option(0.7, help="Sampling temperature"),
    output_dir: str = typer.Option("./data/exports", help="Output directory"),
):
    """Run full bias test battery on specified models."""
    
    if bias_types is None:
        bias_types = list(PROBE_REGISTRY.keys())
    
    console.print(f"[green]Running bias test battery...[/green]")
    console.print(f"Models: {', '.join(models)}")
    console.print(f"Providers: {', '.join(providers)}")
    console.print(f"Bias types: {', '.join(bias_types)}")
    
    # TODO: Implement full battery execution
    console.print("[yellow]Battery execution not yet implemented[/yellow]")


@app.command()
def list_probes():
    """List all available bias probes."""
    
    table = Table(title="Available Bias Probes")
    table.add_column("Bias Type", style="cyan")
    table.add_column("Description", style="white")
    
    probe_descriptions = {
        "prospect_theory": "Prospect Theory / Loss Aversion",
        "anchoring": "Anchoring Bias",
        "availability": "Availability Heuristic",
        "framing": "Framing Effect",
        "sunk_cost": "Sunk Cost Fallacy",
        "optimism": "Optimism Bias",
        "confirmation": "Confirmation Bias",
        "base_rate": "Base-Rate Neglect",
        "conjunction": "Conjunction Fallacy",
        "overconfidence": "Overconfidence Bias",
    }
    
    for bias_type in PROBE_REGISTRY.keys():
        description = probe_descriptions.get(bias_type, "Cognitive bias probe")
        table.add_row(bias_type, description)
    
    console.print(table)


@app.command()
def list_models():
    """List available LLM models and providers."""
    
    table = Table(title="Available LLM Providers and Models")
    table.add_column("Provider", style="cyan")
    table.add_column("Models", style="white")
    
    provider_models = {
        "openai": "gpt-4, gpt-4-turbo, gpt-3.5-turbo",
        "anthropic": "claude-3-opus, claude-3-sonnet, claude-3-haiku",
        "ollama": "llama3, llama3:70b, mistral, codellama",
    }
    
    for provider in LLM_CLIENT_REGISTRY.keys():
        models = provider_models.get(provider, "Various models available")
        table.add_row(provider, models)
    
    console.print(table)


@app.command()
def dashboard():
    """Start the web dashboard."""
    
    console.print("[green]Starting AI Bias Psychologist dashboard...[/green]")
    console.print("[blue]Dashboard will be available at: http://localhost:8000[/blue]")
    
    # TODO: Implement dashboard startup
    console.print("[yellow]Dashboard startup not yet implemented[/yellow]")


if __name__ == "__main__":
    app()
