---
name: data-preprocessing
description: "Use when: generating mock telco customer data, cleaning raw customer data, handling missing values, encoding categoricals, or creating telco features for downstream modeling. Provides the data foundation for the analytical skills."
---

# Data Preprocessing (Telco Data Pipeline)

## When to Use

Use this skill when you need to:
- Generate synthetic customer data for prototyping or demos
- Clean and prepare raw telco data for any downstream model
- Engineer telco-specific features (engagement score, tenure bucket, high-value flag)
- Handle common telco data issues: missing NPS scores, sparse roaming data, categorical plan types

## Agent Usage Contract

The `make-research` agent must use this skill for every research task before selecting an analytical skill. The purpose is to make the data foundation explicit, auditable, and reusable.

For each research task:
- Create or update the reproducible analysis under `notebooks/`, using a task-specific name such as `notebooks/<research-slug>.ipynb`.
- When creating or editing `.ipynb` files, use valid notebook JSON with `metadata.language` on each cell.
- Follow the shared five-section notebook structure in [`../NOTEBOOK_STRUCTURE.md`](../NOTEBOOK_STRUCTURE.md): Business Case, EDA/Data Wrangling, Selected Methodology, Calculation, and Results.
- Use [`../../../notebooks/ab-test-mock-data.ipynb`](../../../notebooks/ab-test-mock-data.ipynb) as the reference notebook pattern for structure, narrative depth, adjacent data layout, charts, and result files.
- If the user provides data, inspect schema, missingness, target leakage risk, time windows, identifiers, treatment/control availability, and business metric definitions before modeling.
- If no data is provided, generate realistic Sunrise Switzerland telco data and clearly label it as synthetic.
- When generating mock data, mimic realistic source tables and joins rather than only producing one flat file. Save source-like tables under `notebooks/<research-slug>/raw/`.
- Record preprocessing choices in the notebook: missing value strategy, categorical encoding, feature engineering, row filters, train/test or pre/post splits, and assumptions.
- Produce clean modeling inputs that the selected analytical skill can consume, while preserving enough raw columns for stakeholder interpretation. Save processed modeling inputs under `notebooks/<research-slug>/processed/` and EDA charts under `notebooks/<research-slug>/charts/`.

## Scripts in This Folder

### `telco_preprocessing.py`

**What it does**: Generates realistic synthetic Swiss telco customer data and provides a full preprocessing pipeline.

**How to use**:
```bash
python3 telco_preprocessing.py
```

**Key functions**:

- `generate_synthetic_telco_data(n_customers)` — Creates a DataFrame with tenure, charges, product type, contract type, support calls, data usage, NPS, canton, language, family plan, etc. Includes realistic missing values (~15% NPS, ~30% roaming).

- `handle_missing_values(df, strategy)` — Imputes missing values. Strategies: `"median"` (default), `"mean"`, `"zero"`. Categorical columns get mode imputation.

- `encode_categoricals(df, cols, method)` — Encodes categorical features. Methods: `"onehot"` (default, drops first), `"label"`.

- `engineer_telco_features(df)` — Creates derived features:
  - `annual_revenue` — monthly charge × 12
  - `engagement_score` — composite of recency, support calls, data usage
  - `tenure_bucket` — 0-6m, 6-12m, 1-2y, 2-5y, 5y+
  - `is_high_value` — top 20% by revenue
  - `arpu_per_line` — revenue per line on account

- `prepare_modeling_dataset(df, target_col)` — Returns clean `(X, y)` tuple ready for sklearn/xgboost.

## Data Schema

| Column | Type | Description |
|--------|------|-------------|
| customer_id | str | CH00000000 format |
| tenure_months | int | 1–120 |
| monthly_charge_chf | float | 19.90–199.90 |
| product_type | str | mobile_only, internet_only, converged, tv_bundle |
| contract_type | str | month_to_month, 12_month, 24_month |
| num_support_calls_6m | int | Poisson(1.5) |
| data_usage_gb | float | Exponential(15) |
| roaming_usage_chf | float | Exponential(5), 30% missing |
| days_since_last_interaction | int | 0–365 |
| nps_score | float | 0–10, 15% missing |
| age | int | 18–80 |
| canton | str | ZH, BE, VD, GE, AG, SG, LU, TI, VS, BS |
| language | str | DE (65%), FR (25%), IT (10%) |
| has_family_plan | int | 0/1 |
| num_lines | int | 1–4 |

## Dependencies

`numpy`, `pandas`, `scikit-learn`
