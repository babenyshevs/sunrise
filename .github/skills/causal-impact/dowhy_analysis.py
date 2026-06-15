"""
DoWhy Implementation for Campaign Causal Effect Estimation
===========================================================

Alternative approach using Microsoft's DoWhy framework.
Good for demonstrating understanding of causal graphs and assumptions.
"""

import numpy as np
import pandas as pd
from typing import Optional


def run_dowhy_analysis(df: pd.DataFrame) -> dict:
    """
    Use DoWhy to estimate campaign causal effect with explicit causal graph.

    DoWhy forces you to:
    1. Define the causal model (DAG)
    2. Identify the estimand
    3. Estimate the effect
    4. Refute the estimate (sensitivity analysis)
    """
    import dowhy
    from dowhy import CausalModel

    # Create binary treatment (post-campaign period)
    df_model = df.copy()
    df_model["treatment"] = (df_model["period"] == "post").astype(int)

    # Define causal graph (DOT format)
    # This encodes our assumptions about what causes what
    causal_graph = """
    digraph {
        treatment -> daily_sales;
        competitor_avg_price -> daily_sales;
        temperature_celsius -> daily_sales;
        market_index -> daily_sales;
        google_trends_competitor -> daily_sales;
        is_weekend -> daily_sales;
        competitor_avg_price -> google_trends_competitor;
    }
    """

    # Create causal model
    model = CausalModel(
        data=df_model,
        treatment="treatment",
        outcome="daily_sales",
        graph=causal_graph,
        common_causes=["competitor_avg_price", "temperature_celsius",
                       "market_index", "is_weekend"]
    )

    # Identify causal effect
    identified_estimand = model.identify_effect(proceed_when_unidentifiable=True)
    print(f"Identified estimand: {identified_estimand}")

    # Estimate using different methods
    # Method 1: Linear regression
    estimate_lr = model.estimate_effect(
        identified_estimand,
        method_name="backdoor.linear_regression"
    )

    # Method 2: Propensity score stratification
    estimate_ps = model.estimate_effect(
        identified_estimand,
        method_name="backdoor.propensity_score_stratification"
    )

    # Refutation: Add random common cause
    refute_random = model.refute_estimate(
        identified_estimand, estimate_lr,
        method_name="random_common_cause"
    )

    # Refutation: Placebo treatment
    refute_placebo = model.refute_estimate(
        identified_estimand, estimate_lr,
        method_name="placebo_treatment_refuter",
        placebo_type="permute"
    )

    results = {
        "linear_regression_ate": estimate_lr.value,
        "propensity_score_ate": estimate_ps.value,
        "refutation_random_cause": refute_random,
        "refutation_placebo": refute_placebo,
        "model": model,
    }

    print(f"\nCausal Effect Estimates:")
    print(f"  Linear Regression ATE: {estimate_lr.value:.2f} sales/day")
    print(f"  Propensity Score ATE: {estimate_ps.value:.2f} sales/day")
    print(f"\nRefutation Tests:")
    print(f"  Random Common Cause: {refute_random}")
    print(f"  Placebo Treatment: {refute_placebo}")

    return results


if __name__ == "__main__":
    from synthetic_control import generate_campaign_time_series

    print("Case 2 (Alternative): DoWhy Causal Analysis")
    print("=" * 50)

    df = generate_campaign_time_series()

    try:
        results = run_dowhy_analysis(df)
    except ImportError:
        print("DoWhy not installed. Install with: pip install dowhy")
