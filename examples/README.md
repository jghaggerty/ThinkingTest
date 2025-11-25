# API Integration Examples

This directory contains comprehensive examples demonstrating how to integrate with the AI Bias Diagnostic API programmatically.

## 📁 Contents

### Python Scripts

1. **`basic_api_usage.py`** - Fundamental API operations
   - Creating evaluations
   - Executing analyses
   - Retrieving results
   - Getting recommendations
   - Listing evaluations

2. **`batch_evaluation.py`** - Parallel evaluation workflows
   - Running multiple evaluations concurrently
   - Comparing results across systems
   - Exporting batch results
   - Comparative analysis

3. **`longitudinal_tracking.py`** - Trend analysis over time
   - Simulating monthly evaluations
   - Creating statistical baselines
   - Tracking improvement trends
   - Heuristic-specific analysis

4. **`integration_patterns.py`** - Production integration patterns
   - CI/CD pipeline integration
   - Automated monitoring
   - Alert systems
   - Custom reporting

### Jupyter Notebook

5. **`api_analysis_workflow.ipynb`** - Interactive data analysis
   - Complete analysis workflow
   - Data visualization with matplotlib/seaborn
   - Statistical analysis
   - Custom report generation
   - Data export capabilities

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure the API server is running
# Backend should be available at http://localhost:8000
```

### Running Examples

Each script can be run independently:

```bash
# Basic usage
python basic_api_usage.py

# Batch evaluation
python batch_evaluation.py

# Longitudinal tracking
python longitudinal_tracking.py

# Integration patterns
python integration_patterns.py
```

### Using the Jupyter Notebook

```bash
# Start Jupyter
jupyter notebook

# Open api_analysis_workflow.ipynb in your browser
# Run cells sequentially to see the complete workflow
```

## 📖 Detailed Examples

### 1. Basic API Usage

**File**: `basic_api_usage.py`

**What it demonstrates**:
- Simple API client implementation
- Creating and executing evaluations
- Retrieving heuristic findings
- Getting recommendations in different modes
- Listing all evaluations

**Use case**: Getting started with the API, understanding basic operations

**Sample output**:
```
AI Bias Diagnostic API - Basic Usage Example
============================================================

1. Creating a new evaluation...
   ✓ Created evaluation: abc123...
   System: GPT-4 Customer Service Bot
   Status: pending

2. Executing heuristic analysis...
   ✓ Analysis complete
   Overall Score: 45.32
   Zone Status: yellow

3. Retrieving heuristic findings...
   ✓ Found 3 heuristic patterns
   ...
```

### 2. Batch Evaluation

**File**: `batch_evaluation.py`

**What it demonstrates**:
- Parallel execution with ThreadPoolExecutor
- Comparing multiple AI systems
- Aggregating results
- Exporting comprehensive reports

**Use case**: Evaluating multiple systems or versions simultaneously

**Key features**:
```python
# Define systems to test
systems_to_test = [
    {
        "name": "System A",
        "heuristics": ["anchoring", "confirmation_bias"],
        "iterations": 60
    },
    # ... more systems
]

# Run in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(run_evaluation, config) for config in systems]
```

### 3. Longitudinal Tracking

**File**: `longitudinal_tracking.py`

**What it demonstrates**:
- Tracking bias trends over time
- Creating statistical baselines
- Calculating improvement metrics
- Identifying trend directions

**Use case**: Monitoring AI system behavior over weeks/months, tracking remediation efforts

**Key metrics**:
- Initial vs final scores
- Improvement percentage
- Volatility (standard deviation)
- Zone distribution over time
- Heuristic-specific trends

**Sample analysis**:
```python
trends = {
    "initial_score": 52.3,
    "final_score": 38.7,
    "improvement": 13.6,  # Lower is better
    "improvement_percentage": 26.0,
    "trend": "improving"
}
```

### 4. Integration Patterns

**File**: `integration_patterns.py`

**What it demonstrates**:
- CI/CD pipeline integration
- Pre-deployment bias checks
- Continuous monitoring
- Alert systems based on thresholds
- Executive report generation

**Use case**: Production deployment, automated testing, compliance reporting

**CI/CD Example**:
```python
cicd = CICDIntegration(api, fail_on_red=True)

# Pre-deployment check
approved = cicd.pre_deployment_check(
    "Production AI System",
    ["anchoring", "loss_aversion"]
)

if not approved:
    print("❌ DEPLOYMENT BLOCKED - Critical bias levels detected")
    sys.exit(1)
```

**Monitoring Example**:
```python
monitor = BiasMonitor(api)
result = monitor.evaluate_and_check(system_name, heuristics)

if result['alert_level'] == AlertLevel.CRITICAL:
    send_alert(result)  # Integrate with your alert system
```

### 5. Interactive Analysis Workflow

**File**: `api_analysis_workflow.ipynb`

**What it demonstrates**:
- End-to-end data analysis workflow
- Data visualization techniques
- Statistical analysis
- Custom reporting
- Data export for further processing

**Use case**: Data science analysis, creating custom visualizations, generating insights

**Visualizations included**:
- Bar charts: Overall scores by system
- Heatmaps: Bias patterns across systems
- Scatter plots: Severity vs confidence
- Stacked bars: Recommendations by impact
- Trend lines: Longitudinal analysis

**Example visualization**:
```python
# Heatmap of bias severity
sns.heatmap(
    pivot_data,
    annot=True,
    cmap='YlOrRd',
    cbar_kws={'label': 'Severity Score'}
)
```

## 🔧 API Client Implementation

All examples use a simple, reusable API client class:

```python
class BiasAPI:
    """Simple client for the AI Bias Diagnostic API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def create_evaluation(self, ai_system_name, heuristic_types, iteration_count=50):
        """Create a new evaluation."""
        # Implementation...

    def execute_evaluation(self, evaluation_id):
        """Execute the analysis."""
        # Implementation...

    # ... more methods
```

**Features**:
- Session management for connection pooling
- Error handling with proper exceptions
- Type hints for better IDE support
- Configurable base URL

## 📊 Common Workflows

### Workflow 1: Single System Evaluation

```python
api = BiasAPI()

# Create evaluation
evaluation = api.create_evaluation(
    ai_system_name="My AI System",
    heuristic_types=["anchoring", "loss_aversion"],
    iteration_count=50
)

# Execute analysis
result = api.execute_evaluation(evaluation['id'])

# Get findings and recommendations
findings = api.get_heuristics(evaluation['id'])
recommendations = api.get_recommendations(evaluation['id'], mode="both")

print(f"Score: {result['overall_score']}")
print(f"Top recommendation: {recommendations['recommendations'][0]['action_title']}")
```

### Workflow 2: Comparative Analysis

```python
systems = ["System A", "System B", "System C"]
results = []

for system in systems:
    eval_data = api.create_evaluation(system, heuristics, 50)
    result = api.execute_evaluation(eval_data['id'])
    results.append(result)

# Compare scores
for result in sorted(results, key=lambda x: x['overall_score']):
    print(f"{result['ai_system_name']}: {result['overall_score']:.2f}")
```

### Workflow 3: Monitoring with Baselines

```python
# Collect baseline data
baseline_evals = []
for month in range(3):
    eval_data = api.create_evaluation(system_name, heuristics, 50)
    result = api.execute_evaluation(eval_data['id'])
    baseline_evals.append(result['id'])

# Create baseline
baseline = api.create_baseline(
    evaluation_ids=baseline_evals,
    name="Q1 Baseline"
)

# Compare new evaluation against baseline
new_eval = api.create_evaluation(system_name, heuristics, 50)
new_result = api.execute_evaluation(new_eval['id'])

print(f"New score: {new_result['overall_score']:.2f}")
print(f"Baseline mean: {baseline['mean_score']:.2f}")
```

## 🎯 Integration Use Cases

### Use Case 1: Development Testing

**Scenario**: Test bias before merging code

```python
# In your test suite
def test_bias_levels():
    api = BiasAPI()
    result = api.create_and_execute_evaluation(
        "Feature Branch AI",
        ["anchoring", "confirmation_bias"]
    )

    assert result['overall_score'] < 60, "Bias levels too high"
    assert result['zone_status'] != 'red', "Critical bias detected"
```

### Use Case 2: Production Monitoring

**Scenario**: Daily automated checks

```python
# In your monitoring script (run via cron)
import schedule

def daily_bias_check():
    api = BiasAPI()
    monitor = BiasMonitor(api)

    result = monitor.evaluate_and_check("Production System", heuristics)

    if result['alert_level'] == AlertLevel.CRITICAL:
        send_slack_alert(result)
        create_incident_ticket(result)

schedule.every().day.at("02:00").do(daily_bias_check)
```

### Use Case 3: Compliance Reporting

**Scenario**: Monthly reports for stakeholders

```python
# Generate monthly report
api = BiasAPI()
report_gen = ReportGenerator(api)

# Get all evaluations from last month
evaluations = api.list_evaluations(limit=100)
recent_evals = filter_by_date(evaluations, last_month)

# Generate reports
for eval_data in recent_evals:
    report = report_gen.generate_executive_summary(
        eval_data['id'],
        output_file=f"reports/{eval_data['id']}_summary.txt"
    )
```

### Use Case 4: A/B Testing

**Scenario**: Compare model versions

```python
# Test two model versions
versions = {
    "Model v1.2": ["anchoring", "loss_aversion"],
    "Model v2.0": ["anchoring", "loss_aversion"]
}

results = {}
for version, heuristics in versions.items():
    eval_data = api.create_evaluation(version, heuristics, 100)
    result = api.execute_evaluation(eval_data['id'])
    results[version] = result

# Compare
v1_score = results["Model v1.2"]['overall_score']
v2_score = results["Model v2.0"]['overall_score']

if v2_score < v1_score:
    print(f"✓ Model v2.0 shows {v1_score - v2_score:.1f} point improvement")
```

## 🔌 Advanced Integration

### Error Handling

```python
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout

try:
    result = api.execute_evaluation(evaluation_id)
except HTTPError as e:
    if e.response.status_code == 404:
        print("Evaluation not found")
    elif e.response.status_code == 400:
        error_detail = e.response.json()
        print(f"Validation error: {error_detail['error']['message']}")
    else:
        print(f"API error: {e}")
except (ConnectionError, Timeout):
    print("Cannot connect to API server")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def create_evaluation_with_retry(api, system_name, heuristics):
    return api.create_evaluation(system_name, heuristics, 50)
```

### Async Operations

```python
import asyncio
import aiohttp

async def create_evaluation_async(session, system_config):
    async with session.post(
        f"{BASE_URL}/api/evaluations",
        json=system_config
    ) as response:
        return await response.json()

async def batch_create(systems):
    async with aiohttp.ClientSession() as session:
        tasks = [create_evaluation_async(session, s) for s in systems]
        return await asyncio.gather(*tasks)

# Run async batch
results = asyncio.run(batch_create(systems_to_test))
```

## 📝 API Reference Summary

### Evaluations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/evaluations` | Create new evaluation |
| GET | `/api/evaluations` | List all evaluations (paginated) |
| GET | `/api/evaluations/{id}` | Get evaluation details |
| POST | `/api/evaluations/{id}/execute` | Run analysis |
| DELETE | `/api/evaluations/{id}` | Delete evaluation |

### Heuristics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/evaluations/{id}/heuristics` | Get all findings |
| GET | `/api/evaluations/{id}/heuristics/{type}` | Get specific finding |

### Recommendations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/evaluations/{id}/recommendations?mode={mode}` | Get recommendations |

**Modes**: `technical`, `simplified`, `both`

### Baselines

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/baselines` | Create baseline |
| GET | `/api/baselines/{id}` | Get baseline details |
| GET | `/api/baselines/evaluations/{id}/trends` | Get trends |

## 🤝 Contributing

To add new examples:

1. Follow the existing code structure
2. Include comprehensive docstrings
3. Add example to this README
4. Test with the live API

## 📚 Additional Resources

- **Main Documentation**: See `/README.md` in the project root
- **Backend API Docs**: http://localhost:8000/docs (when running)
- **Backend README**: See `/backend/README.md`
- **Frontend README**: See `/frontend/README.md`

## 💡 Tips

1. **Start the API first**: Ensure backend is running at `http://localhost:8000`
2. **Check API health**: Visit `http://localhost:8000/docs` to verify
3. **Use the notebook**: Great for learning and experimentation
4. **Customize thresholds**: Adjust alert levels in `integration_patterns.py`
5. **Export data**: Use CSV/JSON exports for integration with other tools
6. **Parallel execution**: Use ThreadPoolExecutor for faster batch processing
7. **Monitor rate limits**: Be mindful when running large batch operations

## 🐛 Troubleshooting

### Connection Refused

```
Error: Connection refused to localhost:8000
```

**Solution**: Start the backend API server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Import Errors

```
ModuleNotFoundError: No module named 'requests'
```

**Solution**: Install dependencies

```bash
pip install -r requirements.txt
```

### Jupyter Kernel Issues

**Solution**: Install ipykernel

```bash
python -m pip install ipykernel
python -m ipykernel install --user
```

---

**Happy Integrating!** 🚀

For questions or issues, please refer to the main project documentation or open an issue on GitHub.
