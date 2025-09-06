# AI Bias Psychologist

A diagnostic tool that systematically detects, measures, and tracks cognitive biases in Large Language Models (LLMs) using structured behavioral probes inspired by Kahneman's research in judgment and decision-making.

## Project Status: Planning Phase ✅

### Completed
- [x] **Product Requirements Document (PRD)** - Comprehensive v0.1 specification
- [x] **Task Breakdown** - 66 detailed implementation tasks across 7 major categories
- [x] **Architecture Planning** - Python-based system with FastAPI, real-time dashboard, and multi-LLM support

### Current Phase
**Planning & Architecture** - Ready to begin implementation

## Overview

The AI Bias Psychologist addresses the critical need to understand and quantify how AI systems exhibit human-like cognitive biases, which can lead to systematic errors in reasoning, decision-making, and output generation.

### Key Features (v0.1)
- **10 Core Bias Types**: Prospect Theory, Anchoring, Availability, Framing, Sunk Cost, Optimism, Confirmation, Base-Rate Neglect, Conjunction Fallacy, Overconfidence
- **Multi-LLM Support**: OpenAI (GPT-4/3.5), Anthropic (Claude-3), Local models (Llama 3, Mistral)
- **Real-time Dashboard**: Live bias monitoring with trend analysis and sparkline visualizations
- **Statistical Analysis**: Normalized scoring, effect sizes, calibration error, contradiction detection
- **Multi-modal Responses**: Both multiple-choice and free-text analysis with sentiment scoring

## Target Audience
- AI researchers
- Compliance teams  
- Product leaders
- Regulators

## Technical Stack
- **Backend**: Python, FastAPI, Typer CLI, Pydantic
- **Analytics**: Pandas, NumPy, SciPy for statistical analysis
- **Storage**: SQLite, JSONL logging
- **Frontend**: HTML/CSS/JS with real-time updates
- **LLM Integration**: OpenAI API, Anthropic API, Ollama

## Project Structure
```
src/ai_bias_psych/
├── probes/          # 10 bias probe implementations
├── llm/            # LLM client integrations
├── analytics/      # Scoring and statistical analysis
├── storage/        # Data management and persistence
├── api/           # FastAPI routes and endpoints
└── web/           # Frontend dashboard
```

## Getting Started

### Prerequisites
- Python 3.9+
- OpenAI API key (optional)
- Anthropic API key (optional)
- Ollama (for local models)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd ai-bias-psychologist

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python scripts/setup_db.py
```

### Usage
```bash
# Run full bias test battery
python -m ai_bias_psych.cli run-battery --model gpt-4

# Run specific bias probe
python -m ai_bias_psych.cli run-probe --bias anchoring --model claude-3

# Start dashboard
python -m ai_bias_psych.main
```

## Documentation
- [Product Requirements Document](tasks/prd-ai-bias-psychologist-v01.md)
- [Implementation Tasks](tasks/tasks-prd-ai-bias-psychologist-v01.md)

## Contributing
This project is in active development. See the task list for current implementation priorities.

## License
[To be determined]