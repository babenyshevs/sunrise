# SuperBooster Churn Campaign Repository

## Purpose
This repository contains the analytical work and presentation assets used to support a C-level decision on a planned churn-reduction campaign: offering a free Wi-Fi booster to internet customers.

The core question is whether a large-scale rollout is likely to reduce cancellations enough to justify the investment.

## Business Context
- Stakeholder: Chief Consumer Officer and monthly leadership forum.
- Decision to support: full rollout vs. targeted rollout vs. no rollout.
- Campaign economics used in the case:
    - Prevented cancellation value: CHF 100 per month for 18 months (CHF 1,800 total).
    - Booster unit cost: CHF 35.
    - Potential rollout size: 1.5 million customers.

## What This Repo Includes
- Data preparation and quality checks.
- Exploratory analysis to understand churn patterns.
- Multiple estimation approaches:
    - Naive comparison (raw churn-rate gap).
    - Causal-adjusted logistic model.
    - Propensity score matching (ATT) with diagnostics.
- Financial business case translating estimated churn impact into ROI.
- Presentation artifact for executive communication.

## Repository Structure

### 1) `case_study/`
- `Case Study Instructions.txt`: assignment brief, assumptions, and required outputs.
- `Data/`: raw source files used in the analysis:
    - `cust_details.csv`
    - `SuperBooster.csv`
    - `cancellations.csv`
- `WiFi Booster Impact.pptx`: presentation deck intended for leadership review.

### 2) `notebooks/`
- `01_data_wrangling.ipynb`: combines sources, creates analysis-ready dataset.
- `02_eda.ipynb`: descriptive analysis and churn drivers exploration.
- `3.1_naive.ipynb`: baseline, non-causal churn comparison.
- `3.2_logit_AME.ipynb`: adjusted churn effect via logistic regression (average marginal effect view).
- `3.2_psm_ATT.ipynb`: propensity score matching estimate (ATT).
- `3.3_psm_diagnostics.ipynb`: overlap and balance diagnostics for matching quality.
- `06_financial_business_case.ipynb`: campaign economics, break-even logic, and ROI framing.
- `helpers.py`, `psm_helpers.py`, `config.py`: reusable utilities, matching helpers, and shared plotting/style constants.
- `processed/df_analysis.csv`: analysis-ready dataset produced by wrangling.

## Analytical Narrative (High Level)
1. Build one customer-level table with booster status and cancellation outcome.
2. Show the naive churn difference for transparency.
3. Correct for observed selection effects using adjusted methods (logit and PSM).
4. Convert estimated prevented churn into financial outcomes.
5. Package findings into an executive-ready recommendation.

## Key Assumptions and Boundaries
- Timing and time-to-event effects are out of scope for this case (as specified in the brief).
- Results rely on observed variables; unobserved confounding can still bias causal interpretation.
- Naive estimates are directional only and should not be used as final decision evidence.

## Intended Audience
- Primary: C-level leadership requiring a decision on campaign scale and expected value.
- Secondary: analytics reviewers who need to audit methods, assumptions, and reproducibility.

## How to Use This Repository
1. Read `case_study/Case Study Instructions.txt` for requirements and constraints.
2. Follow notebooks in numeric order from wrangling to business case.
3. Use the final business-case outputs to inform the presentation narrative in the deck.
