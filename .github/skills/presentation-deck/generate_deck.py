"""
Marp Presentation Deck Generator
==================================

Generates Markdown-based slide decks using Marp format with Mermaid.js diagrams.
Each case has a tailored 5-slide structure ready for presentation.

Usage:
    python3 generate_deck.py                    # Generate all case decks
    python3 generate_deck.py uplift             # Generate only Case 1
    python3 generate_deck.py causal             # Generate only Case 2
    python3 generate_deck.py abtest             # Generate only Case 3
    python3 generate_deck.py optimization       # Generate only Case 4

Output: Markdown (.md) files that render via Marp CLI or VS Code Marp extension.

To export to PDF/HTML:
    marp deck_uplift.md --pdf
    marp deck_uplift.md --html
"""

import sys
import os
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

from sunrise_style import MARP_FRONTMATTER


def generate_uplift_deck() -> str:
    """Case 1: Uplift Modeling for Churn Retention."""
    return MARP_FRONTMATTER + """\
# 🚀 Executive Summary
**Business Objective:** Reduce churn via a targeted 20 CHF/month discount campaign for 50,000 at-risk customers.

**Our Recommendation:**
- **Action:** Target only the top 20,000 "Persuadable" customers (not all 50K).
- **Expected ROI:** + CHF 600K annualized net profit.
- **Risk Mitigation:** Execute via a 3-week A/B test before nationwide rollout.

**Why this matters:** We shift from blanket discounting to targeting *incremental* churn reduction — protecting Sunrise's profit margins while retaining the customers who actually respond.

---

# 🧩 1. Translating the Business Problem

**The Business Request:** "Give a 20 CHF discount to 50K at-risk customers to save them."

**The Analytical Trap:** Giving discounts to customers who would have stayed anyway wastes CHF 6M in margin.

**The Mathematical Translation:**
- **Methodology:** Causal Inference → Uplift Modeling (T-Learner / X-Learner)
- **Target Metric:** Incremental Revenue Saved (not churn probability)
- **Hypothesis:** Treating only "Persuadables" maximizes ROI

| Segment | Without Offer | With Offer | Action |
|---------|--------------|------------|--------|
| **Persuadables** | Churn | Stay | ✅ Target |
| Sure Things | Stay | Stay | ❌ Waste |
| Lost Causes | Churn | Churn | ❌ Waste |
| Sleeping Dogs | Stay | Churn | ⚠️ Avoid |

---

# 📊 2. Methodology & Evidence

**Model Selected:** X-Learner (causalml) with XGBoost base learners

**Key Drivers Found:**
1. Contract type: Month-to-month + tenure 6–36 months → highest uplift
2. Support calls: 1–3 calls in 6 months (engaged but frustrated)

**Evaluation:** Qini curve shows model significantly outperforms random targeting

```mermaid
graph LR
    A[Historical RCT Data] --> B[X-Learner Model]
    B --> C[Per-Customer Uplift Score]
    C --> D{Score > Threshold?}
    D -->|Yes: Persuadable| E[Send 20 CHF Discount]
    D -->|No| F[Do Not Intervene]
    E --> G[Measure Incremental Retention]
```

**P&L at Optimal Target Size (20K customers):**
| Metric | Value |
|--------|-------|
| Revenue Saved | CHF 1,200,000 |
| Discount Cost | CHF 600,000 |
| **Net P&L** | **CHF 600,000** |
| ROI | 100% |

---

# 👥 3. Team Execution in a Matrix Setup

**Data Science (Physics/Math Profiles):**
- Rigorous causal model validation (Qini AUC, decile calibration)
- Hyperparameter tuning with time-based cross-validation
- ML pipeline setup with weekly model refresh and concept-drift monitoring

**Analytics (Business/Domain Profiles):**
- Feature engineering: telco-specific signals (roaming patterns, bundle changes)
- Partner with CRM team to define discount delivery mechanics
- Translate uplift scores into actionable customer segments for campaigns

**Joint Deliverable:**
- Automated scoring pipeline → CRM integration → weekly target list refresh

---

# 🔄 4. Test - Learn - Scale

**1. TEST:**
- **Design:** Randomized Control Trial on 5% of the Persuadable segment (1,000 customers)
- **Guardrails:** Monitor NPS, support call volume, and 30-day retention

**2. LEARN:**
- Calculate statistical significance on actual incremental revenue (p < 0.05)
- Validate uplift decile calibration in production data

**3. SCALE:**
- If ROI confirmed → integrate into daily CRM scoring pipeline
- Monitor for concept drift monthly; retrain quarterly

```mermaid
graph LR
    A[Raw CRM Data] --> B(Uplift Model)
    B --> C{Decisioning Layer}
    C -->|High Uplift| D[Send 20 CHF Discount]
    C -->|Low Uplift| E[Do Not Intervene]
    D --> F[Measure Causal Impact]
    F --> G[Retrain Model]
```
"""


def generate_causal_impact_deck() -> str:
    """Case 2: Campaign Evaluation Without Control Group."""
    return MARP_FRONTMATTER + """\
# 🚀 Executive Summary
**Business Objective:** Determine the true incremental effect of the nationwide billboard + TV campaign on Converged plan sales.

**Our Recommendation:**
- **Finding:** Campaign caused ~8% sales lift (not the claimed 15%).
- **Remaining 7%:** Competitor price hike (4%) + seasonal market growth (3%).
- **Action:** Campaign IS profitable but CMO should adjust claims. Set up regional holdouts for future campaigns.

**Why this matters:** Accurate attribution prevents over-investment in channels with inflated perceived returns.

---

# 🧩 1. Translating the Business Problem

**The Business Request:** "Prove the campaign caused the 15% sales increase."

**The Analytical Trap:** Pre/post comparison ignores confounders that happened simultaneously.

**The Mathematical Translation:**
- **Methodology:** Bayesian Structural Time Series (Synthetic Counterfactual)
- **Target Metric:** Incremental daily sales attributable solely to the campaign
- **Hypothesis:** The true causal effect is smaller than the observed 15% lift

**Confounders identified:**
| Confounder | Impact | Direction |
|-----------|--------|-----------|
| Competitor (Salt) price increase | +4% | Inflates |
| Seasonal summer growth | +3% | Inflates |
| General market expansion | Included in model | Controlled |

---

# 📊 2. Methodology & Evidence

**Model Selected:** Bayesian Structural Time Series (CausalImpact) with exogenous regressors

**Covariates (NOT affected by campaign):**
- Competitor average pricing (Salt, Swisscom)
- Temperature / seasonal index
- General telecom market index

**Key Output: The 3-Panel Causal Impact Chart**

```mermaid
graph TD
    A[180 days Pre-Period] -->|Fit Model| B[Structural Time Series]
    B -->|Project Forward| C[Counterfactual: What Sales Would Have Been]
    D[90 days Post-Period] --> E[Actual Sales Observed]
    C --> F[Causal Effect = Actual - Counterfactual]
    E --> F
    F --> G[Campaign caused 8.2% lift]
```

| Metric | Value |
|--------|-------|
| Naive pre/post lift | 15.1% |
| **True campaign effect** | **8.2%** |
| Incremental sales | 740 units |
| Incremental revenue | CHF 720,000 |
| Campaign cost | CHF 2,000,000 |
| Campaign ROI | -64% |

---

# 👥 3. Team Execution in a Matrix Setup

**Data Science (Physics/Math Profiles):**
- Bayesian time series modeling with proper prior specification
- Sensitivity analysis: vary covariates, test robustness of 8% estimate
- Refutation tests (placebo treatment, random common cause)

**Analytics (Business/Domain Profiles):**
- Source competitor pricing data and validate quality
- Identify regional variation for future holdout design
- Translate findings into media mix optimization recommendations

**Recommendation for Future Campaigns:**
- Always set up 2-3 cantons as holdout (no media exposure)
- This converts future evaluations from observational → quasi-experimental

---

# 🔄 4. Test - Learn - Scale

**For THIS campaign:** Analysis complete. Recommendation: adjust ROI claims.

**For FUTURE campaigns — Design for Measurability:**

**1. TEST:**
- **Design:** Geographic holdout (3 cantons without campaign exposure)
- **Guardrails:** Monitor brand awareness in holdout to detect spillover

**2. LEARN:**
- Difference-in-Differences between exposed and holdout regions
- Cross-validate with CausalImpact on the same data

**3. SCALE:**
- Build automated attribution dashboard refreshing weekly
- Feed into media mix model for budget allocation decisions

```mermaid
graph LR
    A[Daily Sales Data] --> B[CausalImpact Model]
    B --> C[Counterfactual Projection]
    C --> D[Incremental Effect]
    D --> E{ROI > 0?}
    E -->|Yes| F[Continue / Increase Spend]
    E -->|No| G[Reallocate Budget]
```
"""


def generate_abtest_deck() -> str:
    """Case 3: A/B Test Design for Auto-Renewal Toggle."""
    return MARP_FRONTMATTER + """\
# 🚀 Executive Summary
**Business Objective:** Test changing the auto-renewal toggle to ON by default on the prepaid mobile app.

**Our Recommendation:**
- **Action:** Run a 5-week experiment on 5% of DAU with CUPED variance reduction.
- **Expected Lift:** ≥5% increase in monthly revenue per user (CHF 1.25/user/month)
- **Risk Mitigation:** Guardrail metrics (NPS, uninstalls, support calls) with hard stop rules.

**Why this matters:** CUPED lets us detect the effect 2x faster than standard testing, while guardrails ensure we don't trade short-term revenue for long-term customer trust.

---

# 🧩 1. Translating the Business Problem

**The Business Request:** "Test this on 5% of users. How long? How to know if it worked?"

**The Analytical Trap:** Just running a t-test on revenue — ignores peeking inflation, guardrails, and variance.

**The Mathematical Translation:**
- **Methodology:** Power Analysis + CUPED Variance Reduction + Guardrail Monitoring
- **Target Metric:** Monthly Revenue per User (ARPU)
- **Hypothesis:** Default-ON increases ARPU by ≥5% without degrading NPS

| Parameter | Value |
|-----------|-------|
| Baseline ARPU | CHF 25.00/month |
| MDE (5% relative) | CHF 1.25 absolute |
| Std deviation | CHF 60.00 |
| Power | 80% |
| α | 0.05 (two-sided) |
| Traffic | 5% of 500K DAU |

---

# 📊 2. Methodology & Evidence

**CUPED: Why We Can Run This Test 2x Faster**

Use pre-experiment revenue (last 30 days) as covariate to reduce metric variance.

Formula: `Y_adj = Y - θ(X_pre - E[X_pre])` where `θ = Cov(Y, X_pre) / Var(X_pre)`

| Method | CI Width | Duration Needed |
|--------|----------|-----------------|
| Standard t-test | ±1.8 CHF | 10 weeks |
| **CUPED-adjusted** | **±0.9 CHF** | **5 weeks** |
| Variance reduction | **~50%** | |

**Guardrail Metrics (Stop Conditions):**

| Metric | Baseline | Threshold | Action |
|--------|----------|-----------|--------|
| App Uninstall Rate | 2.1% | +0.5pp | 🛑 STOP |
| NPS Score | 32 | -3 points | 🛑 STOP |
| Support Call Rate | 1.8% | +0.3pp | ⚠️ FLAG |

---

# 👥 3. Team Execution in a Matrix Setup

**Data Science (Physics/Math Profiles):**
- Implement CUPED pipeline with pre-experiment covariate extraction
- Set up sequential testing boundaries to prevent peeking bias
- Automate guardrail metric dashboards with alerting

**Analytics (Business/Domain Profiles):**
- Define success criteria with Product Owner (revenue vs. engagement tradeoff)
- Design segmented analysis plan (by plan tier, tenure, age)
- Prepare rollout recommendation report for Go/No-Go decision

**Decision Framework:**
```mermaid
graph TD
    A[Experiment Ends at Week 5] --> B{Primary Metric Significant?}
    B -->|Yes| C{Guardrails OK?}
    B -->|No| D[DO NOT SHIP]
    C -->|Yes| E[SHIP to 100%]
    C -->|No| F[INVESTIGATE - Segment Analysis]
    F --> G{Fixable?}
    G -->|Yes| H[Modify & Re-test]
    G -->|No| D
```

---

# 🔄 4. Test - Learn - Scale

**1. TEST:**
- **Design:** User-level randomization (by customer_id hash), 50/50 within 5% bucket
- **Duration:** 5 weeks (35 days) — rounded to full weeks for seasonality
- **Stratification:** By prepaid plan tier

**2. LEARN:**
- Primary analysis at Day 35 (pre-registered, no early peeking)
- CUPED-adjusted treatment effect with 95% CI
- Guardrail check: Bonferroni-corrected for multiple comparisons

**3. SCALE:**
- If SHIP decision → gradual rollout: 5% → 25% → 100% over 2 weeks
- Monitor guardrails at each step
- Set up long-term holdout (1%) for 6-month retention tracking

```mermaid
graph LR
    A[5% Traffic] -->|Week 1-5| B[Experiment]
    B --> C{Decision}
    C -->|SHIP| D[25% Rollout]
    D -->|1 week| E[100% Rollout]
    C -->|NO-SHIP| F[Archive Learnings]
    E --> G[Long-term Holdout Monitoring]
```
"""


def generate_optimization_deck() -> str:
    """Case 4: Channel Optimization for Cross-Sell."""
    return MARP_FRONTMATTER + """\
# 🚀 Executive Summary
**Business Objective:** Cross-sell home fiber internet to 1M mobile-only customers via optimal channel allocation.

**Our Recommendation:**
- **Action:** Use constrained optimization to assign each customer to their highest-ROI channel.
- **Expected ROI:** +35% profit vs. naive "call everyone with high score" approach.
- **Resource Efficiency:** Call center at 95% utilization with zero wasted capacity.

**Why this matters:** We maximize revenue per CHF of marketing spend by treating channel allocation as an optimization problem, not a propensity ranking problem.

---

# 🧩 1. Translating the Business Problem

**The Business Request:** "We have 1M mobile customers. Should we SMS, email, or call them to sell fiber?"

**The Analytical Trap:** Call everyone with high propensity score. But calls cost CHF 50 vs SMS at CHF 0.08 — a customer with 10% via call vs 8% via email yields MORE profit from email.

**The Mathematical Translation:**
- **Methodology:** Constrained Optimization (maximize expected profit)
- **Target Metric:** Total campaign profit (not conversion rate)
- **Hypothesis:** Profit-optimal allocation ≠ propensity-ranked allocation

| Channel | Cost/Contact | Capacity | Avg Conversion |
|---------|-------------|----------|----------------|
| SMS | CHF 0.08 | 500K/week | ~4% |
| Email | CHF 0.50 | 300K/week | ~6% |
| Call | CHF 50.00 | 25K calls (5,000 hrs) | ~12% |

---

# 📊 2. Methodology & Evidence

**Optimization Formulation:**

Maximize: `Σ [P(convert|customer_i, channel_j) × LTV - Cost_j] × x_ij`

Subject to: capacity constraints, budget limit, max 1 channel per customer.

**Solution:** Greedy allocation by marginal value of scarce resource (calls).

```mermaid
graph TD
    A[XGBoost: P_convert per channel] --> B[Expected Profit Matrix]
    B --> C[Rank by Marginal Value of Call]
    C --> D{Call Capacity Available?}
    D -->|Yes| E[Assign Call]
    D -->|No| F{Email Profitable?}
    F -->|Yes| G[Assign Email]
    F -->|No| H{SMS Profitable?}
    H -->|Yes| I[Assign SMS]
    H -->|No| J[No Contact]
```

**Strategy Comparison:**
| Strategy | Expected Profit | vs. Optimized |
|----------|----------------|---------------|
| **Optimized (LP)** | **CHF 2,450K** | **100%** |
| Naive (call top + SMS rest) | CHF 1,820K | 74% |
| SMS only | CHF 1,100K | 45% |
| Random allocation | CHF 890K | 36% |

---

# 👥 3. Team Execution in a Matrix Setup

**Data Science (Physics/Math Profiles):**
- Train channel-specific propensity models (XGBoost per channel)
- Implement optimization solver with capacity constraints
- Set up A/B test framework for validating model predictions

**Analytics (Business/Domain Profiles):**
- Source and validate channel cost and capacity data from operations
- Define LTV assumptions with Finance team (24-month vs 36-month horizon)
- Build operational dashboard for call center capacity planning

**Joint Deliverable:**
- Daily optimized contact list → CRM → channel-specific execution

---

# 🔄 4. Test - Learn - Scale

**1. TEST:**
- **Design:** Random 10% holdout receives naive allocation; 90% gets optimized
- **Guardrails:** Monitor customer complaints, opt-out rate, call center SLA

**2. LEARN:**
- Compare actual conversion rates and profit per channel vs. predictions
- Recalibrate propensity models with observed outcomes
- Validate that optimization outperforms naive by ≥20%

**3. SCALE:**
- Automate daily scoring + allocation pipeline
- Expand to retention and upsell campaigns (same framework)
- Add new channels (WhatsApp, push notifications) as propensity data becomes available

```mermaid
graph LR
    A[Customer Features] --> B[Channel Propensity Models]
    B --> C[Profit Matrix]
    C --> D[Constrained Optimizer]
    D --> E[Daily Contact Lists]
    E --> F[SMS Queue]
    E --> G[Email Queue]
    E --> H[Call Center Queue]
    F --> I[Outcome Tracking]
    G --> I
    H --> I
    I --> B
```
"""


def generate_all_decks(output_dir: str = ".") -> list:
    """Generate all case decks and write to files."""
    decks = {
        "deck_uplift.md": generate_uplift_deck(),
        "deck_causal_impact.md": generate_causal_impact_deck(),
        "deck_abtest.md": generate_abtest_deck(),
        "deck_optimization.md": generate_optimization_deck(),
    }

    generated = []
    for filename, content in decks.items():
        path = os.path.join(output_dir, filename)
        with open(path, "w") as f:
            f.write(content)
        generated.append(path)
        print(f"✅ Generated: {path}")

    return generated


if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))

    # Parse optional argument for single deck generation
    if len(sys.argv) > 1:
        case = sys.argv[1].lower()
        generators = {
            "uplift": ("deck_uplift.md", generate_uplift_deck),
            "causal": ("deck_causal_impact.md", generate_causal_impact_deck),
            "abtest": ("deck_abtest.md", generate_abtest_deck),
            "optimization": ("deck_optimization.md", generate_optimization_deck),
        }
        if case in generators:
            filename, gen_func = generators[case]
            path = os.path.join(output_dir, filename)
            with open(path, "w") as f:
                f.write(gen_func())
            print(f"✅ Generated: {path}")
        else:
            print(f"Unknown case: {case}")
            print(f"Available: {', '.join(generators.keys())}")
            sys.exit(1)
    else:
        print("Generating all presentation decks...\n")
        generated = generate_all_decks(output_dir)
        print(f"\nDone! {len(generated)} decks generated.")
        print("\nTo export to PDF:")
        print("  marp deck_uplift.md --pdf")
        print("\nTo preview in VS Code:")
        print("  Install 'Marp for VS Code' extension, then open any .md file.")
