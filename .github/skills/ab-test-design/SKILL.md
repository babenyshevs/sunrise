---
name: ab-test-design
description: "Use when: planning or analyzing an A/B test, experiment, feature rollout, pricing test, or product default change. Designs power analysis, CUPED variance reduction, guardrail metrics, and a stakeholder-ready experiment blueprint."
---

# A/B Test Design (Power Analysis + CUPED + Guardrails)

## When to Use

Use this skill when the business asks something like:
- "We want to test a product change on 5% of users. How long should we run it?"
- "Can we detect a 5% revenue lift with our traffic?"
- "How do we know the test won't hurt customer satisfaction?"
- "The test has been running 2 weeks — can we call it?"

**Key signal**: An experiment is being *planned* or *analyzed*, and you need rigorous statistical design or variance reduction.

## Agent Usage Contract

Use this skill after `data-preprocessing` when the research task is about designing, sizing, monitoring, or analyzing an experiment, rollout, default change, pricing test, or product feature test.

For `make-research` outputs:
- Implement the design or analysis in `notebooks/<research-slug>.ipynb` or supporting code under `notebooks/<research-slug>/`.
- Follow the shared five-section notebook structure in [`../NOTEBOOK_STRUCTURE.md`](../NOTEBOOK_STRUCTURE.md): Business Case, EDA/Data Wrangling, Selected Methodology, Calculation, and Results.
- Use [`../../../notebooks/ab-test-mock-data.ipynb`](../../../notebooks/ab-test-mock-data.ipynb) as the reference notebook pattern for an A/B test with mock source tables, joins, formulas, CUPED, guardrails, charts, saved outputs, and conclusion logic.
- Define hypothesis, primary metric, unit of randomization, target population, baseline, MDE, alpha, power, allocation, duration, and decision rule.
- Include power analysis, CUPED or variance reduction when relevant, guardrail metrics, peeking/sequential testing guidance, and launch/no-launch criteria.
- Translate expected impact into CHF where possible using baseline revenue, margin, adoption, rollout size, and risk trade-offs.
- Save source-like data, processed test outputs, and charts next to the notebook under `notebooks/<research-slug>/raw/`, `notebooks/<research-slug>/processed/`, and `notebooks/<research-slug>/charts/`.
- Feed the experiment blueprint, charts, assumptions, guardrails, and decision recommendation into `docs/<research-slug>/deck.md` via the `presentation-deck` skill.

## The Trap (Why "Just Run a t-test" Fails)

Three common mistakes:
1. **Underpowered tests** — running too short, concluding "no effect" when you just couldn't detect it
2. **Peeking** — checking p-values daily inflates false positive rate from 5% to 20%+
3. **No guardrails** — a change that spikes short-term revenue but causes app uninstalls won't be caught by a revenue-only test

## The Right Approach

1. **Power analysis** → calculate required sample size for your MDE
2. **CUPED** → reduce metric variance using pre-experiment data (run tests 2-3x faster)
3. **Guardrail metrics** → define hard stop conditions for customer harm
4. **Experiment blueprint** → pre-register the full decision framework

## Scripts in This Folder

### `power_analysis.py`
**What it does**: Calculates sample size, test duration, and generates a complete experiment blueprint document.

**How to use**:
```bash
python3 power_analysis.py
```
- Computes required sample size for given baseline, MDE, and variance
- Translates sample size into calendar days given traffic constraints
- Generates power curves (detectable effect vs statistical power)
- Produces a full "Experiment Blueprint" — the document you present to stakeholders

**Key functions**:
- `compute_sample_size()` — n per group given baseline, MDE, std, alpha, power
- `compute_test_duration()` — days needed given daily traffic and % allocation
- `power_curve()` — power as function of effect size (for a given sample)
- `generate_experiment_blueprint()` — complete stakeholder-ready document with hypothesis, metrics, duration, guardrails, decision framework

### `cuped_variance_reduction.py`
**What it does**: Implements CUPED (Controlled-experiment Using Pre-Experiment Data) and demonstrates how it shrinks confidence intervals.

**How to use**:
```bash
python3 cuped_variance_reduction.py
```
- Generates synthetic experiment data (50K users, auto-renewal toggle test)
- Runs standard t-test → shows wide CI, borderline significance
- Runs CUPED-adjusted t-test → shows narrower CI, clear significance
- Checks guardrail metrics (uninstalls, NPS, support calls)
- Outputs: `cuped_comparison.png`

**Key functions**:
- `generate_experiment_data()` — synthetic A/B data with pre-period covariate
- `cuped_adjustment()` — the core CUPED formula: `Y_adj = Y - θ(X_pre - E[X_pre])`
- `run_ab_test_standard()` — plain t-test
- `run_ab_test_cuped()` — CUPED-adjusted t-test (shows variance reduction %)
- `check_guardrail_metrics()` — evaluates stop conditions for NPS, uninstalls, support calls
- `plot_cuped_comparison()` — side-by-side CI comparison

## Key Formulas

**Sample size**:
```
n = (1.96 + 0.84)² × 2σ² / MDE²
```

**CUPED**:
```
θ = Cov(Y, X_pre) / Var(X_pre)
Y_adjusted = Y - θ × (X_pre - mean(X_pre))
Typical variance reduction: 30-60%
```

## Business Output Format

Experiment Blueprint (the stakeholder deliverable):
```
Hypothesis:     Defaulting auto-renewal ON increases revenue by ≥5%
Primary Metric: Monthly revenue per user (baseline CHF 25)
MDE:            5% relative = CHF 1.25 absolute
Sample Size:    92,000 total (46,000 per group)
Duration:       5 weeks (at 5% traffic allocation)
Guardrails:     Uninstall rate (+0.5pp → STOP), NPS (-3pts → STOP)
Decision:       Significant + no guardrail violation → SHIP
```

## Dependencies

`scipy`, `numpy`, `pandas`, `matplotlib` (no exotic packages needed)
