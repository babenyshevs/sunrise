1. Do not try to conduct Survival Analysis (calculate days, months, or time horizons). Use cancellations as a 1 or 0. Control for things like internet_usage, commune, and tenure to expose the true causal effect of the booster.

Present 2 views:
The Naive View: Calculate the raw churn rate for has_booster == 1 vs has_booster == 0.
The Causal View: Run a Logistic Regression or Propensity Score Matching. Predict churned using has_booster + all other variables (tenure, commune, internet_usage, etc.).
What to look for: You will likely find that once you control for internet_usage or tenure, the booster's actual effect on churn shrinks significantly.
Financial Calculation: Based on the adjusted causal impact, calculate if the 52.5M CHF investment is worth it. (Spoiler: It probably isn't for everyone).