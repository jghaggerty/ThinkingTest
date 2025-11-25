# AI Bias & Heuristics Diagnostic Tool

A comprehensive full-stack diagnostic dashboard for analyzing cognitive heuristics in AI systems, tracking bias patterns over time, and providing actionable remediation guidance for both technical and non-technical users.

## 🎯 Overview

This tool helps ML Engineers and Product Managers diagnose and understand bias in AI systems through:
- **Heuristic Analysis**: Detects 5 cognitive biases (anchoring, loss aversion, sunk cost, confirmation bias, availability heuristic)
- **Longitudinal Tracking**: Monitors bias trends over time with statistical baselines
- **Dual-Mode Reporting**: Provides both technical metrics and plain-language recommendations
- **Interactive Dashboard**: Professional web interface with data visualizations

## ✅ Project Status: Fully Implemented MVP

### Completed
- [x] **Backend API** - FastAPI with SQLite, heuristic detection, statistical analysis, recommendations
- [x] **Frontend Dashboard** - React+TypeScript with interactive visualizations and dual-mode display
- [x] **Full Integration** - End-to-end tested and working prototype
- [x] **Documentation** - Comprehensive README files for both backend and frontend

## 🏗️ Architecture

### Backend (Python + FastAPI)
- RESTful API with auto-generated Swagger documentation
- SQLite database for evaluation storage
- Rule-based heuristic detection simulation
- Statistical analysis and baseline calculations
- Recommendation generation engine with priority ranking

**Location**: `/backend`
**Tech Stack**: FastAPI, SQLAlchemy, Pydantic, NumPy, Pandas

[Backend Documentation →](./backend/README.md)

### Frontend (React + TypeScript)
- Modern single-page application with React Router
- Responsive dashboard with multiple views
- Interactive charts using Recharts
- Type-safe API integration with Axios
- Export functionality for evaluation results

**Location**: `/frontend`
**Tech Stack**: React 18, TypeScript, Vite, TailwindCSS, Recharts, Lucide Icons

[Frontend Documentation →](./frontend/README.md)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 18+ with npm

### 1. Start the Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database and seed sample data
python -m app.utils.test_data_generator

# Start the API server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Start the Frontend

```bash
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at http://localhost:5173

## 📊 Features

### Dashboard View
- List all evaluations with status and zone classification (green/yellow/red)
- Quick overview of scores and heuristics tested
- Click-through to detailed analysis

### Create Evaluation
- Configure AI system name
- Select heuristic types to test (1-5 options available)
- Set iteration count (10-100 for statistical reliability)
- Automatic execution after creation

### Evaluation Detail

#### Overview Tab
- Overall score and zone status visualization
- Bar chart showing severity scores by heuristic
- Summary of findings with severity indicators
- Configuration details and metadata

#### Heuristics Tab
- Detailed breakdown of each heuristic finding
- Severity scoring (0-100 scale)
- Confidence levels (0-1 scale)
- Pattern analysis descriptions
- Example instances from testing
- Detection rate statistics

#### Recommendations Tab
- Prioritized mitigation strategies (ranked 1-10)
- **Dual-mode display**: Toggle between technical and simplified descriptions
  - **Technical**: Implementation details for engineers
  - **Simplified**: Plain language for product managers
- Impact estimates (low/medium/high)
- Implementation difficulty ratings (easy/moderate/complex)
- Actionable next steps

### Export Functionality
- Download evaluation results as JSON
- Includes findings, recommendations, and metadata
- Suitable for sharing and reporting

## 📖 API Documentation

The backend provides a RESTful API with comprehensive endpoints:

### Evaluations
- `POST /api/evaluations` - Create new evaluation
- `GET /api/evaluations` - List all evaluations (paginated)
- `GET /api/evaluations/{id}` - Get evaluation details
- `POST /api/evaluations/{id}/execute` - Run heuristic analysis
- `DELETE /api/evaluations/{id}` - Delete evaluation

### Heuristics
- `GET /api/evaluations/{id}/heuristics` - Get all findings
- `GET /api/evaluations/{id}/heuristics/{type}` - Get specific finding

### Recommendations
- `GET /api/evaluations/{id}/recommendations?mode=both` - Get recommendations

### Baselines
- `POST /api/baselines` - Create statistical baseline
- `GET /api/baselines/{id}` - Get baseline details
- `GET /api/baselines/evaluations/{id}/trends` - Get longitudinal trends

Full interactive documentation: http://localhost:8000/docs

## 🧪 How It Works

### Heuristic Detection (Simulated)

The MVP uses rule-based simulation to demonstrate bias detection patterns:

1. **Anchoring Bias**: Tests response variance with different initial values (threshold: 30%)
2. **Loss Aversion**: Compares sensitivity to losses vs. gains (threshold: 2x ratio)
3. **Sunk Cost Fallacy**: Evaluates influence of prior investment on decisions (threshold: 50%)
4. **Confirmation Bias**: Measures dismissal of contradictory evidence (threshold: 60%)
5. **Availability Heuristic**: Checks probability estimation bias from recent examples (threshold: 40%)

### Statistical Analysis

- **Zone Classification**:
  - **Green Zone**: score ≤ mean + (0.5 × std_dev)
  - **Yellow Zone**: mean + (0.5 × std_dev) < score ≤ mean + (1.5 × std_dev)
  - **Red Zone**: score > mean + (1.5 × std_dev)

- **Overall Score**: Weighted average of individual severity scores, with higher weights for worse findings

- **Confidence Level**: `proportion × (1 - 1/√iterations)` capped at 99%

### Recommendation Prioritization

```
priority_score = (severity_score × 0.6) + (confidence × 30) + (base_priority × 0.1)
```

Top 7 recommendations returned, ranked by priority descending.

## 📁 Project Structure

```
ThinkingTest/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── routers/           # API endpoint handlers
│   │   ├── services/          # Business logic
│   │   │   ├── heuristic_detector.py
│   │   │   ├── statistical_analyzer.py
│   │   │   └── recommendation_generator.py
│   │   ├── utils/             # Utilities and test data
│   │   ├── config.py          # Settings management
│   │   ├── database.py        # Database setup
│   │   └── main.py            # FastAPI application
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── Layout.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── OverviewTab.tsx
│   │   │   ├── HeuristicsTab.tsx
│   │   │   └── RecommendationsTab.tsx
│   │   ├── pages/             # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── CreateEvaluation.tsx
│   │   │   └── EvaluationDetail.tsx
│   │   ├── services/          # API client
│   │   │   └── api.ts
│   │   ├── types/             # TypeScript definitions
│   │   ├── utils/             # Constants and formatters
│   │   └── App.tsx
│   ├── package.json
│   ├── tailwind.config.js
│   ├── .env.example
│   └── README.md
│
└── README.md                   # This file
```

## 🎯 Use Cases

### For ML Engineers
- Debug black-box AI behavior through systematic bias testing
- Establish statistical baselines for non-deterministic systems
- Track behavioral drift in production models
- Generate technical documentation for model cards

### For Product Managers
- Understand bias risks in plain language
- Make go/no-go decisions with clear metrics
- Respond to compliance/audit requests
- Prioritize mitigation efforts by impact and feasibility

### For Compliance Officers
- Generate audit-ready reports (dual-mode: technical + executive summary)
- Track remediation progress over time
- Demonstrate due diligence in AI governance
- Document risk mitigation strategies with clear action items

## 🚧 Future Enhancements

The current implementation is a fully functional MVP prototype. Production deployment could add:

**Backend**:
- Live API integration with actual AI systems (OpenAI, Anthropic, etc.)
- Real ML models for bias detection (not rule-based simulation)
- PostgreSQL database with migrations
- Redis caching layer
- Background job processing (Celery/RQ)
- JWT authentication and authorization
- Multi-tenancy support
- Comprehensive test coverage (pytest)

**Frontend**:
- WebSocket support for real-time progress updates
- PDF report generation
- Comparison view for multiple evaluations
- Custom baseline configuration UI
- Dark mode support
- Mobile-responsive design
- Advanced filtering and search

**Infrastructure**:
- Docker containerization
- Kubernetes deployment
- CI/CD pipeline
- Monitoring and logging (ELK stack, Prometheus)
- Horizontal scaling infrastructure
- CDN for static assets

## 🔧 Development

See individual README files for detailed development instructions:
- [Backend Development Guide](./backend/README.md)
- [Frontend Development Guide](./frontend/README.md)

## 📝 License

MIT License

## 🤝 Contributing

This is a prototype project demonstrating the architecture and capabilities of an AI bias diagnostic tool. For production deployment or collaboration, please contact the development team.

## 📮 Support

For issues and questions, please open an issue on the GitHub repository.

---

**Built for responsible AI development** 🎯
