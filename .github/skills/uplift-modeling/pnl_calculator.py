"""
P&L Calculator for Uplift-Based Retention Campaign
====================================================

This is the BUSINESS OUTPUT that makes a data scientist's work actionable.
It translates model predictions into CHF revenue impact.

Key Formula:
  ROI = (Revenue Saved from Prevented Churn) - (Cost of Discounts Given)

The critical insight: You only want to give discounts to PERSUADABLES.
Giving discounts to "Sure Things" or "Lost Causes" is pure waste.
"""

import numpy as np
import pandas as pd
from typing import Dict


# Business parameters for Sunrise Switzerland
DEFAULT_PARAMS = {
    "discount_chf_per_month": 20.0,       # CHF monthly discount
    "discount_duration_months": 6,         # Duration of retention offer
    "avg_monthly_arpu_chf": 65.0,          # Average revenue per user
    "avg_customer_lifetime_months": 36.0,  # Expected remaining lifetime if retained
    "target_population": 50_000,           # Number of customers to potentially target
    "cost_of_contact_chf": 2.0,            # Cost to reach out (SMS/email/call)
    "margin_pct": 0.55,                    # Gross margin on revenue
}


def calculate_campaign_pnl(
    uplift_scores: np.ndarray,
    treatment_top_n: int,
    params: Dict = None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Calculate P&L for targeting top-N customers by uplift score.

    Args:
        uplift_scores: Predicted uplift for each customer (probability of
                      churn reduction due to treatment). Positive = treatment helps.
        treatment_top_n: Number of customers to target (sorted by uplift)
        params: Business parameters dict
        verbose: Print detailed P&L breakdown

    Returns:
        DataFrame with P&L breakdown
    """
    if params is None:
        params = DEFAULT_PARAMS.copy()

    # Sort customers by uplift (highest first = most persuadable)
    sorted_indices = np.argsort(-uplift_scores)  # Descending
    targeted_uplift = uplift_scores[sorted_indices[:treatment_top_n]]

    # --- REVENUE SAVED ---
    # Expected churns prevented = sum of uplift probabilities for targeted customers
    expected_churns_prevented = targeted_uplift.sum()

    # Revenue saved per prevented churn (remaining lifetime value)
    remaining_ltv_per_customer = (
        params["avg_monthly_arpu_chf"]
        * params["avg_customer_lifetime_months"]
        * params["margin_pct"]
    )

    total_revenue_saved = expected_churns_prevented * remaining_ltv_per_customer

    # --- COSTS ---
    # Cost 1: Discount given to ALL targeted customers (including Sure Things)
    total_discount_cost = (
        treatment_top_n
        * params["discount_chf_per_month"]
        * params["discount_duration_months"]
    )

    # Cost 2: Contact/operational cost
    total_contact_cost = treatment_top_n * params["cost_of_contact_chf"]

    # Total cost
    total_cost = total_discount_cost + total_contact_cost

    # --- NET P&L ---
    net_pnl = total_revenue_saved - total_cost
    roi_pct = (net_pnl / total_cost * 100) if total_cost > 0 else 0

    # --- Comparison: What if we targeted randomly? ---
    mean_uplift_random = uplift_scores.mean()
    random_churns_prevented = mean_uplift_random * treatment_top_n
    random_revenue_saved = random_churns_prevented * remaining_ltv_per_customer
    random_net_pnl = random_revenue_saved - total_cost

    results = {
        "Metric": [
            "Customers Targeted",
            "Avg Uplift (Targeted)",
            "Avg Uplift (Random)",
            "Expected Churns Prevented (Uplift Model)",
            "Expected Churns Prevented (Random)",
            "---",
            "Revenue Saved (Uplift Model)",
            "Revenue Saved (Random)",
            "---",
            "Total Discount Cost",
            "Total Contact Cost",
            "Total Campaign Cost",
            "---",
            "Net P&L (Uplift Model)",
            "Net P&L (Random Targeting)",
            "Incremental Value of Uplift Model",
            "ROI % (Uplift Model)",
            "ROI % (Random Targeting)",
        ],
        "Value": [
            f"{treatment_top_n:,}",
            f"{targeted_uplift.mean():.4f}",
            f"{mean_uplift_random:.4f}",
            f"{expected_churns_prevented:,.0f}",
            f"{random_churns_prevented:,.0f}",
            "---",
            f"CHF {total_revenue_saved:,.0f}",
            f"CHF {random_revenue_saved:,.0f}",
            "---",
            f"CHF {total_discount_cost:,.0f}",
            f"CHF {total_contact_cost:,.0f}",
            f"CHF {total_cost:,.0f}",
            "---",
            f"CHF {net_pnl:,.0f}",
            f"CHF {random_net_pnl:,.0f}",
            f"CHF {net_pnl - random_net_pnl:,.0f}",
            f"{roi_pct:.1f}%",
            f"{(random_net_pnl / total_cost * 100) if total_cost > 0 else 0:.1f}%",
        ]
    }

    results_df = pd.DataFrame(results)

    if verbose:
        print("\n" + "=" * 60)
        print("P&L CALCULATOR: Uplift-Based Retention Campaign")
        print("=" * 60)
        print(f"\nBusiness Parameters:")
        print(f"  - Discount: CHF {params['discount_chf_per_month']}/month × {params['discount_duration_months']} months")
        print(f"  - Average ARPU: CHF {params['avg_monthly_arpu_chf']}/month")
        print(f"  - Avg remaining lifetime: {params['avg_customer_lifetime_months']} months")
        print(f"  - Gross margin: {params['margin_pct']*100:.0f}%")
        print(f"  - LTV per retained customer: CHF {remaining_ltv_per_customer:,.0f}")
        print()
        print(results_df.to_string(index=False))
        print("\n" + "=" * 60)

        # Decision recommendation
        if net_pnl > 0:
            print(f"\n✅ RECOMMENDATION: PROCEED with campaign targeting top {treatment_top_n:,} customers")
            print(f"   Expected net profit: CHF {net_pnl:,.0f}")
            print(f"   The uplift model adds CHF {net_pnl - random_net_pnl:,.0f} vs random targeting")
        else:
            print(f"\n❌ RECOMMENDATION: DO NOT proceed at this targeting level")
            print(f"   Expected net loss: CHF {net_pnl:,.0f}")
            print(f"   Consider reducing target population or increasing discount selectivity")

    return results_df


def find_optimal_target_size(
    uplift_scores: np.ndarray,
    params: Dict = None,
    step: int = 1000
) -> pd.DataFrame:
    """
    Find the optimal number of customers to target by sweeping target sizes.
    Shows diminishing returns as you move down the uplift ranking.
    """
    if params is None:
        params = DEFAULT_PARAMS.copy()

    n_total = len(uplift_scores)
    sorted_uplift = np.sort(uplift_scores)[::-1]  # Descending

    remaining_ltv = (
        params["avg_monthly_arpu_chf"]
        * params["avg_customer_lifetime_months"]
        * params["margin_pct"]
    )
    cost_per_customer = (
        params["discount_chf_per_month"] * params["discount_duration_months"]
        + params["cost_of_contact_chf"]
    )

    results = []
    for n_target in range(step, min(n_total, params["target_population"]) + 1, step):
        targeted = sorted_uplift[:n_target]
        revenue_saved = targeted.sum() * remaining_ltv
        cost = n_target * cost_per_customer
        net_pnl = revenue_saved - cost
        marginal_uplift = sorted_uplift[n_target - 1] if n_target <= n_total else 0

        results.append({
            "n_targeted": n_target,
            "avg_uplift": targeted.mean(),
            "marginal_uplift": marginal_uplift,
            "revenue_saved_chf": revenue_saved,
            "cost_chf": cost,
            "net_pnl_chf": net_pnl,
            "roi_pct": (net_pnl / cost * 100) if cost > 0 else 0,
        })

    results_df = pd.DataFrame(results)

    # Find optimal point
    optimal_idx = results_df["net_pnl_chf"].idxmax()
    optimal_n = results_df.loc[optimal_idx, "n_targeted"]
    optimal_pnl = results_df.loc[optimal_idx, "net_pnl_chf"]

    print(f"\n📊 Optimal target size: {optimal_n:,} customers")
    print(f"   Maximum Net P&L: CHF {optimal_pnl:,.0f}")
    print(f"   ROI at optimum: {results_df.loc[optimal_idx, 'roi_pct']:.1f}%")

    return results_df


def plot_pnl_curve(pnl_df: pd.DataFrame, save_path: str = None):
    """Plot the P&L curve as function of target size."""
    import matplotlib.pyplot as plt
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from sunrise_style import apply_matplotlib_style, color, save_figure

    apply_matplotlib_style()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Top: Net P&L
    ax1.plot(pnl_df["n_targeted"], pnl_df["net_pnl_chf"] / 1000,
             color=color("orange"), linewidth=2.4, label="Net P&L")
    ax1.axhline(y=0, color=color("coral"), linestyle="--", linewidth=1)

    # Mark optimal point
    optimal_idx = pnl_df["net_pnl_chf"].idxmax()
    ax1.axvline(x=pnl_df.loc[optimal_idx, "n_targeted"], color=color("blue"),
                linestyle=":", linewidth=1.5, label="Optimal Target Size")
    ax1.scatter([pnl_df.loc[optimal_idx, "n_targeted"]],
               [pnl_df.loc[optimal_idx, "net_pnl_chf"] / 1000],
               color=color("blue"), s=100, zorder=5)

    ax1.set_ylabel("Net P&L (kCHF)", fontsize=11)
    ax1.set_title("Campaign P&L vs Target Population Size", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Bottom: Marginal uplift
    ax2.plot(pnl_df["n_targeted"], pnl_df["marginal_uplift"] * 100,
             color=color("cyan"), linewidth=2.4)
    ax2.axhline(y=0, color=color("coral"), linestyle="--", linewidth=1)
    ax2.set_xlabel("Number of Customers Targeted", fontsize=11)
    ax2.set_ylabel("Marginal Uplift (%)", fontsize=11)
    ax2.set_title("Marginal Uplift of Next Customer Added", fontsize=12)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    plt.show()


if __name__ == "__main__":
    from uplift_churn_model import generate_uplift_experiment_data

    print("Generating data for P&L calculation...")
    df = generate_uplift_experiment_data(n_customers=50_000)

    # Simulate uplift scores (in practice from trained model)
    rng = np.random.default_rng(42)
    uplift_scores = (-df["true_uplift"].values + rng.normal(0, 0.005, len(df))).clip(0, 0.1)

    # Calculate P&L for targeting top 20,000 customers
    print("\n" + "=" * 60)
    print("SCENARIO: Target top 20,000 customers by uplift score")
    calculate_campaign_pnl(uplift_scores, treatment_top_n=20_000)

    # Find optimal target size
    print("\n\nFinding optimal target population...")
    pnl_df = find_optimal_target_size(uplift_scores, step=2000)
    plot_pnl_curve(pnl_df, save_path="pnl_curve.png")

    # Compare: What if marketing just targets all 50,000?
    print("\n" + "=" * 60)
    print("SCENARIO: Marketing's original plan - target ALL 50,000")
    calculate_campaign_pnl(uplift_scores, treatment_top_n=50_000)
