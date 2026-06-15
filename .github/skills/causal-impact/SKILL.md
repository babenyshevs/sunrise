---
name: causal-impact
description: "Use when: evaluating a campaign, intervention, launch, or policy change without a control group. Builds a synthetic counterfactual from time-series data and covariates to isolate true causal impact from seasonality, market trends, and competitor actions."
---

# Causal Impact (Campaign Evaluation Without Control Group)

## When to Use

Use this skill when the business asks something like:
- "Our campaign launched 3 months ago. Sales are up 15%. Was it the campaign?"
- "We didn't set up a control group. Can we still measure the effect?"
- "The CMO claims credit for the sales increase. Is she right?"

**Key signal**: An intervention happened *without* a randomized control group, and someone is attributing a metric change to it.

## Agent Usage Contract

Use this skill after `data-preprocessing` when the research task evaluates a campaign, launch, intervention, policy, pricing change, or market action without a clean randomized control group.

For `make-research` outputs:
- Implement the analysis in `notebooks/<research-slug>.ipynb` or supporting code under `notebooks/<research-slug>/`.
- Follow the shared five-section notebook structure in [`../NOTEBOOK_STRUCTURE.md`](../NOTEBOOK_STRUCTURE.md): Business Case, EDA/Data Wrangling, Selected Methodology, Calculation, and Results.
- Use [`../../../notebooks/ab-test-mock-data.ipynb`](../../../notebooks/ab-test-mock-data.ipynb) as the reference notebook pattern for narrative depth, source-table joins, formulas, charts, saved notebook-adjacent data, and evidence-driven conclusion logic.
- Define intervention date, pre/post windows, outcome metric, candidate covariates, excluded confounders, and the counterfactual strategy.
- Include pre-period fit diagnostics, counterfactual chart, point and cumulative effect, uncertainty interval, and robustness or placebo checks when feasible.
- Separate observed change from causal impact and translate the difference into CHF incremental revenue, margin, campaign cost, and ROI.
- Save source-like data, processed counterfactual outputs, diagnostics, robustness checks, and charts next to the notebook under `notebooks/<research-slug>/raw/`, `notebooks/<research-slug>/processed/`, and `notebooks/<research-slug>/charts/`.
- Feed the final recommendation, impact attribution, charts, assumptions, and risk view into `docs/<research-slug>/deck.md` via the `presentation-deck` skill.

## The Trap (Why Pre/Post Comparison Is Wrong)

Comparing averages before and after the campaign ignores everything else that changed:
- **Seasonality**: Summer/winter buying patterns
- **Competitor actions**: A rival raised prices (pushes customers to you)
- **Market trends**: General market growth
- **External shocks**: Weather, regulatory changes

The "15% increase" might be 8% campaign + 4% competitor price hike + 3% seasonal trend.

## The Right Approach

Build a **synthetic counterfactual**: use pre-campaign data + exogenous covariates to predict what sales WOULD have been without the campaign. The difference = true causal effect.

## Scripts in This Folder

### `synthetic_control.py`
**What it does**: Full causal impact pipeline — data generation, counterfactual modeling, visualization, executive summary.

**How to use**:
```bash
python3 synthetic_control.py
```
- Generates 270 days of synthetic sales data (180 pre + 90 post campaign)
- Includes confounders: competitor pricing, temperature, market index
- Fits structural time series model on pre-period
- Projects counterfactual into post-period
- Outputs: `causal_impact_chart.png` (the classic 3-panel chart)

**Key functions**:
- `generate_campaign_time_series()` — synthetic data with known true effect (8%) and confounders that inflate naive estimate to ~15%
- `run_causal_impact_tfcausal()` — Google's CausalImpact (Bayesian structural TS)
- `run_causal_impact_statsmodels()` — statsmodels UnobservedComponents (lighter dependency)
- `plot_causal_impact()` — 3-panel chart: actual vs counterfactual, point effect, cumulative effect
- `generate_business_summary()` — executive summary with revenue attribution

### `dowhy_analysis.py`
**What it does**: Alternative approach using Microsoft's DoWhy framework with explicit causal graphs.

**How to use**:
```bash
python3 dowhy_analysis.py
```
- Defines a causal DAG (directed acyclic graph) encoding assumptions
- Identifies the causal estimand
- Estimates effect via backdoor adjustment (linear regression + propensity scores)
- Runs refutation tests (robustness checks)

**Key functions**:
- `run_dowhy_analysis()` — full DoWhy pipeline with graph definition, estimation, refutation

## Business Output Format

The 3-panel chart is the primary deliverable:
1. **Top panel**: Actual sales (blue) vs Counterfactual (red dashed) + 95% CI
2. **Middle panel**: Daily incremental effect (point-wise)
3. **Bottom panel**: Cumulative incremental sales over time

Executive summary:
```
CMO's Claim:  Sales up 15% due to campaign
Our Finding:  Campaign caused 8.2% lift
Remaining 7%: Competitor price increase (4%) + seasonal growth (3%)

Incremental revenue: CHF 720,000
Campaign cost:       CHF 2,000,000
Campaign ROI:        -64% (campaign was NOT cost-effective at this spend level)
```

## Dependencies

`tfcausalimpact`, `statsmodels`, `dowhy`, `numpy`, `pandas`, `matplotlib`
