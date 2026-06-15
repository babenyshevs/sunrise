---
name: channel-optimization
description: "Use when: allocating customers, offers, next-best actions, or campaign contacts across channels such as SMS, email, and call center under budget or capacity constraints. Combines propensity scores with constrained optimization to maximize CHF ROI."
---

# Channel Optimization (Next Best Action under Constraints)

## When to Use

Use this skill when the business asks something like:
- "We have 1M customers to cross-sell. Should we SMS, email, or call them?"
- "How do we allocate call center capacity across customer segments?"
- "We have a fixed budget — how to maximize campaign ROI?"
- "What's the optimal channel mix for this campaign?"

**Key signal**: Multiple channels/actions exist with different costs, and there are capacity or budget constraints that prevent "just call everyone."

## Agent Usage Contract

Use this skill after `data-preprocessing` when the research task allocates customers, offers, channels, sales actions, service actions, or next-best actions under budget, capacity, contact policy, or operational constraints.

For `make-research` outputs:
- Implement the optimization in `notebooks/<research-slug>.ipynb` or supporting code under `notebooks/<research-slug>/`.
- Follow the shared five-section notebook structure in [`../NOTEBOOK_STRUCTURE.md`](../NOTEBOOK_STRUCTURE.md): Business Case, EDA/Data Wrangling, Selected Methodology, Calculation, and Results.
- Use [`../../../notebooks/ab-test-mock-data.ipynb`](../../../notebooks/ab-test-mock-data.ipynb) as the reference notebook pattern for narrative depth, source-table joins, formulas, charts, saved notebook-adjacent data, and evidence-driven conclusion logic.
- Define action set, eligibility rules, channel capacities, costs, expected value formula, constraints, and fairness or contact-policy limits.
- Include expected profit by customer-action pair, optimized allocation, resource utilization, comparison to baseline strategies, and sensitivity to budget or capacity changes.
- Translate the allocation into CHF expected profit, incremental value versus naive/rules-based approaches, ROI, and operational workload.
- Save source-like data, processed profit matrices, allocation outputs, sensitivity tables, and charts next to the notebook under `notebooks/<research-slug>/raw/`, `notebooks/<research-slug>/processed/`, and `notebooks/<research-slug>/charts/`.
- Feed the final allocation recommendation, comparison charts, assumptions, and implementation plan into `docs/<research-slug>/deck.md` via the `presentation-deck` skill.

## The Trap (Why Propensity Alone Fails)

A propensity model ranks customers by P(convert). The naive action: call everyone with high propensity. But:

| Customer | P(convert\|Call) | P(convert\|Email) | Call Profit | Email Profit |
|----------|-----------------|-------------------|-------------|--------------|
| A | 10% | 8% | CHF 100 | **CHF 119** |
| B | 25% | 5% | **CHF 325** | CHF 74 |

Customer A is better off with email despite lower conversion — because the call costs CHF 50 vs CHF 0.50 for email. You need to optimize *profit*, not *probability*, subject to constraints.

## The Right Approach

Formulate as constrained optimization:
```
Maximize: Σ [P(convert|customer_i, channel_j) × LTV - Cost_j] × x_ij
Subject to:
  Each customer gets at most 1 channel
  Call center hours ≤ 5,000/week
  Email volume ≤ 300,000
  Total budget ≤ B
```

Solve via greedy allocation by marginal value (near-optimal for this problem structure, scales to millions).

## Scripts in This Folder

### `channel_optimization.py`
**What it does**: Complete pipeline from data generation through optimization to strategy comparison.

**How to use**:
```bash
python3 channel_optimization.py
```
- Generates 100K customers with channel-specific conversion probabilities
- Computes expected profit per customer-channel pair
- Runs constrained optimization (greedy by marginal value of scarce resource)
- Compares 4 strategies: Optimized vs Naive vs SMS-only vs Random
- Outputs: `nbo_optimization.png`

**Key functions**:
- `generate_cross_sell_data()` — synthetic customers with `p_convert_sms`, `p_convert_email`, `p_convert_call`
- `compute_expected_profit_per_assignment()` — profit matrix: P(convert) × LTV - Cost for each pair
- `optimize_channel_allocation_scipy()` — constrained allocation (calls first by marginal value, then email, then SMS)
- `compare_strategies()` — head-to-head: optimized vs naive vs sms-only vs random
- `plot_allocation_results()` — 4-panel visualization

## Channel Parameters (Configurable)

| Channel | Cost/Contact | Capacity | Avg Conversion |
|---------|-------------|----------|----------------|
| SMS | CHF 0.08 | 500K/week | ~4% |
| Email | CHF 0.50 | 300K/week | ~6% |
| Call | CHF 50.00 | 5,000 hrs/week (~25K calls) | ~12% |

## Business Output Format

```
Strategy Comparison:
  Optimized (LP):           CHF 2,450,000 expected profit  (100%)
  Naive (call top + SMS):   CHF 1,820,000                  (74%)
  SMS only:                 CHF 1,100,000                  (45%)
  Random allocation:        CHF   890,000                  (36%)

Value of optimization: +CHF 630,000 vs naive approach (+35%)

Resource Utilization:
  Call center: 4,750 / 5,000 hours (95%)
  Email: 180,000 / 300,000 capacity (60%)
  SMS: 320,000 / 500,000 capacity (64%)
```

## Dependencies

`scipy.optimize`, `xgboost`, `numpy`, `pandas`, `matplotlib`
