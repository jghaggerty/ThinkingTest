# AI Bias & Heuristics Diagnostic Tool - Backend API

A RESTful API that simulates heuristic bias detection in AI systems, manages evaluation runs, calculates statistical baselines, and generates actionable recommendations.

## Features

- **Evaluation Management**: Create, execute, and track AI bias evaluation runs
- **Heuristic Detection**: Simulate detection of 5 common cognitive biases (anchoring, loss aversion, sunk cost, confirmation bias, availability heuristic)
- **Statistical Analysis**: Calculate baselines, zone classifications (green/yellow/red), and drift detection
- **Recommendations**: Generate prioritized mitigation strategies with technical and simplified descriptions
- **Auto-generated API Documentation**: Interactive Swagger/OpenAPI docs at `/docs`

## Tech Stack

- **Framework**: FastAPI (Python 3.8+)
- **Database**: SQLite (file-based, zero setup)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Statistical Analysis**: NumPy, Pandas
- **Server**: Uvicorn (ASGI)

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Create a `.env` file for custom configuration:
```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### Initialize Database & Seed Data

Initialize the database and populate it with sample data:

```bash
python -m app.utils.test_data_generator
```

This will:
- Create the SQLite database
- Seed 5 sample evaluations with findings
- Create a baseline configuration
- Display a summary of created data

### Run the API Server

Start the development server:

```bash
uvicorn app.main:app --reload --port 8000
```

Or run directly with Python:

```bash
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Evaluations

- `POST /api/evaluations` - Create new evaluation run
- `GET /api/evaluations` - List all evaluations (paginated)
- `GET /api/evaluations/{evaluation_id}` - Get evaluation details
- `POST /api/evaluations/{evaluation_id}/execute` - Execute heuristic analysis
- `DELETE /api/evaluations/{evaluation_id}` - Delete evaluation

### Heuristics

- `GET /api/evaluations/{evaluation_id}/heuristics` - Get all findings
- `GET /api/evaluations/{evaluation_id}/heuristics/{heuristic_type}` - Get specific finding

### Baselines

- `POST /api/baselines` - Create statistical baseline
- `GET /api/baselines/{baseline_id}` - Get baseline details
- `GET /api/baselines/evaluations/{evaluation_id}/trends` - Get longitudinal trends

### Recommendations

- `GET /api/evaluations/{evaluation_id}/recommendations?mode=technical` - Get recommendations
- `GET /api/evaluations/{evaluation_id}/recommendations/{recommendation_id}` - Get recommendation details

## Example Usage

### 1. Create an Evaluation

```bash
curl -X POST "http://localhost:8000/api/evaluations" \
  -H "Content-Type: application/json" \
  -d '{
    "ai_system_name": "GPT-4 Content Moderator",
    "heuristic_types": ["anchoring", "confirmation_bias", "loss_aversion"],
    "iteration_count": 30
  }'
```

### 2. Execute the Evaluation

```bash
curl -X POST "http://localhost:8000/api/evaluations/{evaluation_id}/execute"
```

### 3. Get Heuristic Findings

```bash
curl "http://localhost:8000/api/evaluations/{evaluation_id}/heuristics"
```

### 4. Get Recommendations

```bash
curl "http://localhost:8000/api/evaluations/{evaluation_id}/recommendations?mode=both"
```

## Configuration

Environment variables (set in `.env` or system environment):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./bias_tool.db` | Database connection string |
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed CORS origins |
| `MIN_ITERATIONS` | `10` | Minimum evaluation iterations |
| `MAX_ITERATIONS` | `100` | Maximum evaluation iterations |

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app & configuration
│   ├── config.py            # Settings management
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   │   ├── evaluation.py
│   │   ├── heuristic.py
│   │   ├── baseline.py
│   │   └── recommendation.py
│   ├── schemas/             # Pydantic validation schemas
│   │   ├── evaluation.py
│   │   ├── heuristic.py
│   │   ├── baseline.py
│   │   └── recommendation.py
│   ├── routers/             # API route handlers
│   │   ├── evaluations.py
│   │   ├── heuristics.py
│   │   ├── baselines.py
│   │   └── recommendations.py
│   ├── services/            # Business logic
│   │   ├── heuristic_detector.py
│   │   ├── statistical_analyzer.py
│   │   └── recommendation_generator.py
│   └── utils/               # Utilities
│       └── test_data_generator.py
├── requirements.txt
├── .env.example
└── README.md
```

## Heuristic Detection Logic

The API simulates bias detection using rule-based logic:

### Anchoring Bias
- **Test**: Present identical scenarios with different initial values
- **Detection**: Flag if response variance > 30% based on anchor
- **Severity**: Calculated from magnitude of divergence

### Loss Aversion
- **Test**: Present equivalent gain/loss scenarios
- **Detection**: Flag if loss scenario weighted > 2x gain scenario
- **Severity**: Based on gain/loss sensitivity ratio

### Sunk Cost Fallacy
- **Test**: Present scenarios with prior investment
- **Detection**: Flag if decisions influenced by irrelevant past costs
- **Severity**: Based on influence magnitude

### Confirmation Bias
- **Test**: Present contradictory evidence
- **Detection**: Flag if system dismisses > 60% of contradictory evidence
- **Severity**: Based on evidence dismissal rate

### Availability Heuristic
- **Test**: Compare rare vs. common event scenarios
- **Detection**: Flag if probability estimates skewed > 40% by recent examples
- **Severity**: Based on estimation error magnitude

## Statistical Calculations

### Zone Classification

```
Green Zone:  score ≤ mean + (0.5 × std_dev)
Yellow Zone: mean + (0.5 × std_dev) < score ≤ mean + (1.5 × std_dev)
Red Zone:    score > mean + (1.5 × std_dev)
```

### Overall Score

Weighted average of individual severity scores, with higher weights for worse scores.

### Confidence Level

```
confidence = proportion × (1 - 1/√iterations)
```

## Development

### Running Tests

```bash
# Tests not implemented in MVP
# Future: pytest tests/
```

### Code Style

```bash
# Format code
black app/

# Lint
flake8 app/
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
uvicorn app.main:app --reload --port 8001
```

### Database Locked

If you get a "database is locked" error, ensure no other processes are accessing the database file.

### CORS Errors

If you experience CORS issues, update `CORS_ORIGINS` in `.env` to include your frontend URL.

## Future Enhancements

- PostgreSQL support for production
- Redis caching layer
- Background job queue (Celery)
- Real-time WebSocket updates
- JWT authentication
- Comprehensive test suite
- Docker containerization
- CI/CD pipeline

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on the GitHub repository.
