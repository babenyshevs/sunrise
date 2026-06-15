---
name: uplift-modeling
description: "Use when: deciding which customers to target with a retention campaign, discount, offer, or outreach. Predicts who changes behavior due to treatment, not just who churns, and converts uplift into CHF ROI."
---

# Uplift Modeling (Causal ML for Retention)

## When to Use

Use this skill when the business asks something like:
- "Should we give a discount/offer to at-risk customers?"
- "Which customers should we target with a retention campaign?"
- "How do we avoid wasting money on people who'd stay anyway?"

**Key signal**: There's a *treatment* (discount, call, offer) and the question is *who actually changes behavior* because of it — not just who is likely to churn.

## Agent Usage Contract

Use this skill after `data-preprocessing` when the research task is about targeting customers with a treatment, offer, discount, retention action, outreach, or next-best intervention.

For `make-research` outputs:
- Implement the analysis in `notebooks/<research-slug>.ipynb` or supporting code under `notebooks/<research-slug>/`.
- Follow the shared five-section notebook structure in [`../NOTEBOOK_STRUCTURE.md`](../NOTEBOOK_STRUCTURE.md): Business Case, EDA/Data Wrangling, Selected Methodology, Calculation, and Results.
- Use [`../../../notebooks/ab-test-mock-data.ipynb`](../../../notebooks/ab-test-mock-data.ipynb) as the reference notebook pattern for narrative depth, source-table joins, formulas, charts, saved notebook-adjacent data, and evidence-driven conclusion logic.
- Document treatment definition, outcome window, control/treatment comparability, randomization or identification assumptions, and target population.
- Include uplift-specific validation such as Qini curve, uplift by decile, incremental retention, and sensitivity to target size.
- Convert uplift into CHF impact: saved margin or LTV, treatment cost, net P&L, ROI, and comparison against random, propensity-only, and blanket targeting.
- Save source-like data, processed scores, validation outputs, P&L tables, and charts next to the notebook under `notebooks/<research-slug>/raw/`, `notebooks/<research-slug>/processed/`, and `notebooks/<research-slug>/charts/`.
- Feed the final recommendation, charts, assumptions, and ROI table into `docs/<research-slug>/deck.md` via the `presentation-deck` skill.

## The Trap (Why This Isn't a Simple Propensity Model)

A propensity model predicts **who will churn**. But that's the wrong question. You need to predict **who will change their behavior IF given the treatment**. Four customer types exist:

| Segment | Without Offer | With Offer | What to Do |
|---------|---------------|------------|------------|
| **Persuadables** | Churn | Stay | ✅ Target these |
| Sure Things | Stay | Stay | ❌ Waste of money |
| Lost Causes | Churn | Churn | ❌ Waste of money |
| Sleeping Dogs | Stay | Churn | ⚠️ Avoid! |

## Scripts in This Folder

### `uplift_churn_model.py`
**What it does**: Trains uplift models using `causalml` (T-Learner, X-Learner) and `sklift` (SoloModel, ClassTransformation).

**How to use**:
```bash
python3 uplift_churn_model.py
```
- Generates synthetic RCT data (50K customers with random treatment assignment)
- Trains models that estimate per-customer treatment effect
- Outputs: mean uplift scores, model objects ready for scoring new customers

**Key functions**:
- `generate_uplift_experiment_data()` — creates training data simulating a past A/B test
- `train_uplift_model_causalml()` — T-Learner and X-Learner via causalml
- `train_uplift_model_sklift()` — SoloModel and ClassTransformation via sklift

### `metrics_and_plots.py`
**What it does**: Generates Qini curves and uplift decile charts — the evaluation metrics specific to uplift modeling.

**How to use**:
```bash
python3 metrics_and_plots.py
```
- Outputs: `qini_curve.png`, `uplift_deciles.png`
- Shows that top uplift deciles have real treatment effect, bottom deciles don't

**Key functions**:
- `compute_qini_curve()` — Qini curve data (analogous to ROC for uplift)
- `compute_uplift_by_decile()` — actual uplift broken down by model-predicted decile
- `plot_qini_curve()` / `plot_uplift_deciles()` — publication-ready charts

### `pnl_calculator.py`
**What it does**: Translates uplift scores into a CHF P&L statement. This is the business deliverable.

**How to use**:
```bash
python3 pnl_calculator.py
```
- Takes uplift scores + business parameters (discount amount, LTV, margin)
- Calculates: revenue saved, discount cost, net P&L, ROI
- Compares uplift-based targeting vs random targeting vs blanket approach
- Finds the optimal number of customers to target (diminishing returns curve)

**Key functions**:
- `calculate_campaign_pnl()` — full P&L for a given target size
- `find_optimal_target_size()` — sweep target sizes to find maximum profit
- `plot_pnl_curve()` — net P&L vs target population chart

## Business Output Format

```
Revenue Saved:     CHF 1,200,000  (from prevented churn × LTV)
Discount Cost:     CHF   600,000  (20 CHF × 6 months × N targeted)
Net P&L:           CHF   600,000
ROI:               100%

vs Random Targeting: CHF 150,000 (our approach is 4x better)
```

## Dependencies

`causalml`, `scikit-uplift`, `xgboost`, `sklearn`, `numpy`, `pandas`, `matplotlib`
