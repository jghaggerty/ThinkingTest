# Prompt for Cursor

You are to act as a senior product manager writing a **Product Requirements Document (PRD)** for the following application:

**Application Concept:**  
An "AI Clinical Psychologist" tool that detects, diagnoses, and tracks cognitive biases and heuristics in other generative AIs (e.g., ChatGPT, Claude, Llama). The system uses structured probes (inspired by Daniel Kahneman’s work in judgment and decision-making, behavioral economics, and utility theory) to evaluate models across a battery of cognitive bias tests (e.g., loss aversion, anchoring, framing). Results are logged, scored, and tracked longitudinally, with dashboards and recommendations for mitigation.

## Instructions

Write the PRD with the following structure and content:

1. **Overview**
   - One-paragraph product summary.
   - Why this tool matters (biases in LLMs parallel but differ from human heuristics).
   - Target audience: AI researchers, compliance teams, product leaders, and regulators.

2. **Goals & Non-Goals**
   - Explicit product goals (bias detection, longitudinal tracking, education, mitigation).
   - Clear non-goals (not building a new LLM, not enforcing fairness across all use cases).

3. **User Stories / Personas**
   - Example personas: AI researcher, compliance officer, product PM, educator.
   - User stories drawn from discovery notes (detection engine, dashboard, education, mitigation).

4. **Key Features**
   - **Probe Engine:** Defines and runs tests for 10+ biases (loss aversion, availability, anchoring, optimism bias, framing, sunk cost, prospect theory, base-rate neglect, conjunction fallacy, overconfidence).
   - **Metrics Layer:** Calculates effect sizes, calibration error, drift over time.
   - **Results Logging:** JSON schema for responses, provenance, and scoring.
   - **Dashboard:** Visualization of probe outcomes, trends, and cross-model comparisons.
   - **Recommendations:** Mitigation playbook linking detected bias to corrective actions.
   - **Educational Module:** Explanations of biases and how they appear in AIs.

5. **Example Bias Probes**
   - Provide 2–3 short probe examples for each bias type, showing how prompts differ across conditions (gain vs. loss frame, high vs. low anchors, etc.).

6. **MVP Scope**
   - Probe engine with 10 biases, CLI runner, JSONL logging, minimal dashboard.
   - Longitudinal storage for drift detection.
   - Report export (CSV/JSON/HTML).
   - Education module stub.

7. **Out of Scope**
   - No reinforcement training loop in v1.
   - No advanced mitigation beyond recommendations.
   - No integration with proprietary vendor APIs beyond simple adapters.

8. **Technical Considerations**
   - Backend: Python (FastAPI, Typer CLI, Pydantic, Pandas, SciPy).
   - Frontend: lightweight web dashboard (Next.js or Flask + HTMX).
   - Data: JSONL logs, optional Postgres/Supabase.
   - CI/CD: GitHub Actions with linting, type checks, tests.
   - Repo setup: `ai-bias-psych` (backend), `ai-bias-psych-web`, `ai-bias-psych-probes`, `ai-bias-psych-notebooks`.

9. **Success Metrics**
   - Accuracy of bias detection (effect size significance).
   - Calibration quality (coverage vs. confidence).
   - Usability: researchers can run tests and get clear reports in <10 minutes.
   - Adoption: initial partner teams integrate into workflow.

10. **Risks & Open Questions**
    - Defining “ground truth” for biases in LLMs.
    - Vendor rate limits and API costs.
    - Bias test contamination (models memorizing probe patterns).
    - Ethical implications of labeling one model “more biased” than another.

## Output Format
- Deliver the PRD as **Markdown**.
- Use clear headings, bullet points, and tables where appropriate.
- Keep each section concise but specific enough for engineers and designers to begin work.
