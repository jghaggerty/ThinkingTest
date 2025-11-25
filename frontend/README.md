# AI Bias & Heuristics Diagnostic Tool - Frontend

A React-based diagnostic dashboard for analyzing cognitive heuristics in AI systems, tracking bias patterns, and providing actionable remediation guidance.

## Features

- **Dashboard View**: Monitor all evaluations with zone status indicators
- **Evaluation Creation**: Interactive form to configure and run bias tests
- **Detailed Analysis**: Comprehensive view of heuristic findings with charts
- **Dual-Mode Recommendations**: Toggle between technical and simplified guidance
- **Data Visualization**: Charts and graphs for trend analysis
- **Export Functionality**: Download evaluation results as JSON

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **Routing**: React Router v6
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios

## Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000 (see backend/README.md)

## Quick Start

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

### Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Environment Configuration

Create a `.env` file in the frontend directory:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── Layout.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── OverviewTab.tsx
│   │   ├── HeuristicsTab.tsx
│   │   └── RecommendationsTab.tsx
│   ├── pages/            # Page components
│   │   ├── Dashboard.tsx
│   │   ├── CreateEvaluation.tsx
│   │   └── EvaluationDetail.tsx
│   ├── services/         # API integration
│   │   └── api.ts
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── utils/            # Utility functions
│   │   ├── constants.ts
│   │   └── format.ts
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Key Features

### Dashboard
- List all evaluations with status, zone classification, and scores
- Quick view of heuristic types tested
- Click to view detailed results

### Create Evaluation
- Name your AI system
- Select heuristic types to test (anchoring, loss aversion, etc.)
- Configure iteration count (10-100)
- Automatic execution after creation

### Evaluation Detail

#### Overview Tab
- Overall score and zone status
- Bar chart of severity scores
- Summary of all findings
- Configuration details

#### Heuristics Tab
- Detailed breakdown of each finding
- Severity scoring and confidence levels
- Pattern descriptions
- Example instances from testing

#### Recommendations Tab
- Prioritized mitigation strategies
- Dual-mode display (technical & simplified)
- Impact and difficulty ratings
- Implementation guidance

## API Integration

The frontend communicates with the backend API using Axios. All API calls are centralized in `src/services/api.ts`.

### Main API Endpoints Used:
- `GET /api/evaluations` - List evaluations
- `POST /api/evaluations` - Create evaluation
- `POST /api/evaluations/{id}/execute` - Run evaluation
- `GET /api/evaluations/{id}/heuristics` - Get findings
- `GET /api/evaluations/{id}/recommendations` - Get recommendations

## Accessibility

The application follows WCAG 2.1 AA standards:
- Keyboard navigation support
- Screen reader compatible
- Proper color contrast ratios
- Focus indicators on interactive elements
- Semantic HTML structure

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Development

### Code Style

```bash
# Lint code
npm run lint
```

### Type Checking

```bash
# Run TypeScript compiler
npx tsc --noEmit
```

## Troubleshooting

### Cannot connect to backend

Ensure:
1. Backend is running on http://localhost:8000
2. CORS is enabled in backend configuration
3. `.env` file has correct `VITE_API_BASE_URL`

### Build errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Future Enhancements

- Real-time updates via WebSockets
- PDF report generation
- Comparison view for multiple evaluations
- Custom baseline configuration UI
- Dark mode support
- Mobile responsive design

## License

MIT License

## Support

For issues and questions, please open an issue on the GitHub repository.
