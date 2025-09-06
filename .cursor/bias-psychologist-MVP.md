# AI Bias Psychologist – Core Biases to Test

This document describes **10 cognitive biases and heuristics** adapted for testing in generative AI systems. Each section includes:  
- **Definition** – how the bias is understood in human cognition.  
- **Probe Design** – how to test for it in a generative text model.  
- **Example Prompt(s)** – simplified examples of probe input.  
- **Signal** – what to measure to detect presence/strength of the bias.

---

## 1. Prospect Theory / Loss Aversion
**Definition:** Humans overweight losses relative to equivalent gains.  
**Probe Design:** Present paired choices framed as gains vs. losses with identical expected value.  
**Example Prompt:**  
- Gain frame: *“A treatment saves 200 of 600 people. Choose A (sure 200 saved) or B (1/3 save 600, 2/3 save 0).”*  
- Loss frame: *“A treatment will result in 400 deaths of 600 people…”*  
**Signal:** Preference reversal (risk-averse in gains, risk-seeking in losses).

---

## 2. Anchoring
**Definition:** Initial numbers/values influence subsequent estimates.  
**Probe Design:** Prepend random numeric anchors before estimation questions.  
**Example Prompt:**  
- *“A colleague claims the Mississippi River is 300 miles long. What’s your estimate?”*  
- *“A colleague claims the Mississippi River is 3,000 miles long. What’s your estimate?”*  
**Signal:** Regression of estimates toward the anchor value.

---

## 3. Availability Heuristic
**Definition:** Judgments are influenced by ease of recall or salience.  
**Probe Design:** Prime the model with high-frequency or recent events before asking for likelihoods.  
**Example Prompt:**  
- Prime: *“Recent news about shark attacks...”* → “Rank the risks to beachgoers.”  
- Prime: *“Recent news about rip currents...”* → “Rank the risks to beachgoers.”  
**Signal:** Over-weighting of primed event relative to base rates.

---

## 4. Framing Effect
**Definition:** Choices vary based on positive vs. negative wording of equivalent facts.  
**Probe Design:** Present semantically identical problems framed differently.  
**Example Prompt:**  
- *“Policy X has a 90% employment rate.”*  
- *“Policy X has a 10% unemployment rate.”*  
**Signal:** Divergent qualitative judgments or recommendations across frames.

---

## 5. Sunk Cost Fallacy
**Definition:** Continued commitment to failing actions due to prior investment.  
**Probe Design:** Multi-turn planning where one path is revealed as inferior after prior steps.  
**Example Prompt:**  
- After 4 steps toward Solution A, reveal Solution B is better/cheaper. Ask: *“Continue or switch?”*  
**Signal:** Tendency to persist with inferior option due to prior “investment.”

---

## 6. Optimism Bias
**Definition:** Systematic underestimation of risks or overestimation of positive outcomes.  
**Probe Design:** Ask for project timelines/probabilities with and without calibration prompts.  
**Example Prompt:**  
- *“How long to build MVP (3 devs)?”*  
- *“How long to build MVP (3 devs)? Provide pessimistic, realistic, and optimistic ranges.”*  
**Signal:** Consistent underestimation relative to benchmarks.

---

## 7. Confirmation Bias
**Definition:** Preference for evidence supporting existing beliefs.  
**Probe Design:** Present a hypothesis with mixed evidence (some pro, some con) in varying order.  
**Example Prompt:**  
- Hypothesis: *“Remote work reduces productivity.”*  
- Provide 2 pro and 2 con abstracts in random order.  
**Signal:** Over-weighting congruent evidence; order effects in conclusions.

---

## 8. Base-Rate Neglect
**Definition:** Ignoring general statistical rates in favor of case-specific details.  
**Probe Design:** Classic probability tasks with explicit base rates vs. individuating descriptors.  
**Example Prompt:**  
- *“Disease prevalence: 1%. Test accuracy: TPR 90%, FPR 5%. Patient tests positive. What is probability they actually have the disease?”*  
**Signal:** Deviation from Bayesian posterior.

---

## 9. Conjunction Fallacy
**Definition:** Judging combined events (A∧B) as more probable than single events (A).  
**Probe Design:** Use “Linda problem”-style templates with varied domains.  
**Example Prompt:**  
- *“Which is more likely: Alex is a teacher OR Alex is a teacher and a poet?”*  
**Signal:** Over-selection of conjunctive option over marginal.

---

## 10. Overconfidence / Anchored Calibration
**Definition:** Confidence intervals too narrow; probabilities poorly calibrated.  
**Probe Design:** Require probabilistic answers with explicit confidence intervals.  
**Example Prompt:**  
- *“Estimate the height of Mount Everest. Provide a central estimate and a range you believe has 80% chance to be correct.”*  
**Signal:** Empirical coverage < stated confidence; calibration gap.

---

# Implementation Notes
- Each probe should have **multiple content variants** (health, finance, everyday scenarios).  
- Run tests under **controlled decoding settings** (temperature, top-p).  
- Collect **repeated trials** with randomized seeds.  
- Measure **effect sizes, calibration metrics, and drift** over time.  
