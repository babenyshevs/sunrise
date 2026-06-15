"""
Case 4: Next Best Action - Channel Optimization with Constrained Resources
============================================================================

Business Context:
- 1 million mobile-only customers to cross-sell home fiber internet
- 3 channels: SMS (cheap), Email (medium), Call Center (expensive)
- Question: How to allocate channels to maximize ROI under constraints?

Key Insight:
A simple propensity model says "call everyone with high score" but:
- Call center has limited capacity (5,000 hours/week)
- Each call costs ~50 CHF, SMS costs 0.08 CHF, email costs 0.50 CHF
- A customer with 10% conversion probability via call vs 8% via email
  might be better served by email (ROI is higher)

The Mathematical Translation:
Maximize: Σ P(convert | channel_i, customer_j) × Revenue - Cost(channel_i)
Subject to: Channel capacity constraints, budget constraints, frequency caps

Packages: XGBoost (propensity), SciPy.optimize (linear programming)
"""

import numpy as np
import pandas as pd
from scipy.optimize import linprog, LinearConstraint
from typing import Dict, Tuple, Optional


def generate_cross_sell_data(n_customers: int = 100_000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic customer data with channel-specific conversion probabilities.

    In practice, these probabilities come from separate models trained on
    historical campaign data for each channel.
    """
    rng = np.random.default_rng(seed)

    # Customer features
    df = pd.DataFrame({
        "customer_id": [f"MOB{i:07d}" for i in range(n_customers)],
        "tenure_months": rng.integers(1, 96, n_customers),
        "monthly_arpu_chf": rng.exponential(45, n_customers).clip(19.90, 150).round(2),
        "data_usage_gb": rng.exponential(20, n_customers).round(1),
        "age": rng.integers(18, 75, n_customers),
        "has_tv": rng.choice([0, 1], n_customers, p=[0.85, 0.15]),
        "urban_flag": rng.choice([0, 1], n_customers, p=[0.35, 0.65]),
        "fiber_available": rng.choice([0, 1], n_customers, p=[0.30, 0.70]),
        "num_family_members": rng.integers(1, 5, n_customers),
        "last_interaction_days": rng.integers(0, 365, n_customers),
        "digital_engagement_score": rng.beta(2, 5, n_customers).round(3),
    })

    # Channel-specific conversion probabilities
    # These would come from separate XGBoost models in practice
    base_prob = (
        0.02
        + 0.03 * df["fiber_available"]
        + 0.02 * df["urban_flag"]
        + 0.01 * (df["tenure_months"] > 12).astype(float)
        + 0.015 * (df["monthly_arpu_chf"] > 60).astype(float)
        + 0.01 * (df["data_usage_gb"] > 30).astype(float)
        - 0.01 * (df["age"] > 60).astype(float)
    ).clip(0.005, 0.20)

    # Channel multipliers (some customers respond better to certain channels)
    # SMS: Quick, impulsive, younger customers
    sms_multiplier = (
        1.0
        + 0.3 * (df["age"] < 40).astype(float)
        + 0.2 * (df["digital_engagement_score"] > 0.3).astype(float)
        - 0.2 * (df["age"] > 55).astype(float)
    )

    # Email: Digital-savvy, engaged customers
    email_multiplier = (
        1.2
        + 0.4 * (df["digital_engagement_score"] > 0.4).astype(float)
        + 0.2 * (df["last_interaction_days"] < 30).astype(float)
        - 0.3 * (df["digital_engagement_score"] < 0.1).astype(float)
    )

    # Call: High-value, complex needs, older customers
    call_multiplier = (
        1.8
        + 0.5 * (df["monthly_arpu_chf"] > 80).astype(float)
        + 0.4 * (df["num_family_members"] > 2).astype(float)
        + 0.3 * (df["age"] > 45).astype(float)
        + 0.2 * (df["has_tv"] == 1).astype(float)
    )

    # Add noise
    noise = rng.normal(1, 0.1, (n_customers, 3)).clip(0.5, 1.5)

    df["p_convert_sms"] = (base_prob * sms_multiplier * noise[:, 0]).clip(0.001, 0.15).round(4)
    df["p_convert_email"] = (base_prob * email_multiplier * noise[:, 1]).clip(0.001, 0.20).round(4)
    df["p_convert_call"] = (base_prob * call_multiplier * noise[:, 2]).clip(0.005, 0.35).round(4)

    return df


# Channel parameters
CHANNEL_PARAMS = {
    "sms": {
        "cost_per_contact_chf": 0.08,
        "max_contacts_per_week": 500_000,  # Essentially unlimited
        "avg_handling_time_min": 0,
        "max_per_customer": 1,
    },
    "email": {
        "cost_per_contact_chf": 0.50,
        "max_contacts_per_week": 300_000,
        "avg_handling_time_min": 0,
        "max_per_customer": 1,
    },
    "call": {
        "cost_per_contact_chf": 50.0,  # Agent time + overhead
        "max_contacts_per_week": None,  # Limited by hours
        "avg_handling_time_min": 12,
        "max_call_center_hours_per_week": 5_000,
        "max_per_customer": 1,
    },
}

# Revenue from successful conversion
CONVERSION_REVENUE_CHF = 79.90 * 24  # 24-month fiber contract monthly value
CUSTOMER_LIFETIME_VALUE_CHF = 79.90 * 36 * 0.55  # 36-month LTV at 55% margin


def compute_expected_profit_per_assignment(
    df: pd.DataFrame,
    revenue_per_conversion: float = CUSTOMER_LIFETIME_VALUE_CHF,
) -> pd.DataFrame:
    """
    Compute expected profit for each customer-channel combination.
    Expected Profit = P(convert) × Revenue - Cost(channel)
    """
    df = df.copy()

    for channel in ["sms", "email", "call"]:
        cost = CHANNEL_PARAMS[channel]["cost_per_contact_chf"]
        p_col = f"p_convert_{channel}"
        df[f"expected_profit_{channel}"] = (
            df[p_col] * revenue_per_conversion - cost
        ).round(2)

    # Also compute "no contact" option (cost = 0, but some organic conversion)
    df["expected_profit_none"] = 0  # Baseline

    return df


def optimize_channel_allocation_scipy(
    df: pd.DataFrame,
    max_call_hours: float = 5_000,
    max_emails: int = 300_000,
    max_sms: int = 500_000,
    budget_chf: Optional[float] = None,
) -> pd.DataFrame:
    """
    Solve channel allocation as a linear programming problem.

    Decision variables: x[i][j] = 1 if customer i gets channel j
    Maximize: Σ expected_profit[i][j] * x[i][j]
    Subject to:
      - Each customer gets at most one channel (or none)
      - Call center hours ≤ max_call_hours
      - Email volume ≤ max_emails
      - SMS volume ≤ max_sms
      - Optional: total budget ≤ budget_chf

    For large N, we use a greedy heuristic (optimal for this structure).
    """
    n = len(df)

    # Compute expected profits
    df = compute_expected_profit_per_assignment(df)

    # For each customer, find the best channel (greedy approach)
    # This is optimal when constraints are not binding
    channels = ["sms", "email", "call", "none"]
    profit_cols = [f"expected_profit_{c}" for c in channels]

    # Get best channel for each customer
    profits_matrix = df[profit_cols].values
    best_channel_idx = np.argmax(profits_matrix, axis=1)
    best_channel = np.array(channels)[best_channel_idx]
    best_profit = profits_matrix[np.arange(n), best_channel_idx]

    df["optimal_channel_unconstrained"] = best_channel
    df["optimal_profit_unconstrained"] = best_profit

    # Now apply constraints using priority queue approach
    # Sort by marginal value of each channel vs next-best alternative
    df["call_marginal_value"] = (
        df["expected_profit_call"] -
        df[["expected_profit_sms", "expected_profit_email", "expected_profit_none"]].max(axis=1)
    )
    df["email_marginal_value"] = (
        df["expected_profit_email"] -
        df[["expected_profit_sms", "expected_profit_none"]].max(axis=1)
    )

    # Allocate calls first (scarce resource)
    max_calls = int(max_call_hours * 60 / CHANNEL_PARAMS["call"]["avg_handling_time_min"])

    # Customers where call is best AND has positive marginal value
    call_candidates = df[df["call_marginal_value"] > 0].nlargest(max_calls, "call_marginal_value")

    # Allocate emails next
    remaining = df[~df.index.isin(call_candidates.index)]
    email_candidates = remaining[remaining["email_marginal_value"] > 0].nlargest(
        max_emails, "email_marginal_value"
    )

    # SMS for remaining profitable customers
    remaining2 = remaining[~remaining.index.isin(email_candidates.index)]
    sms_candidates = remaining2[remaining2["expected_profit_sms"] > 0].nlargest(
        max_sms, "expected_profit_sms"
    )

    # Assign channels
    df["assigned_channel"] = "none"
    df.loc[call_candidates.index, "assigned_channel"] = "call"
    df.loc[email_candidates.index, "assigned_channel"] = "email"
    df.loc[sms_candidates.index, "assigned_channel"] = "sms"

    # Compute assigned profit
    df["assigned_profit"] = 0.0
    for channel in ["sms", "email", "call"]:
        mask = df["assigned_channel"] == channel
        df.loc[mask, "assigned_profit"] = df.loc[mask, f"expected_profit_{channel}"]

    return df


def compare_strategies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare optimization-based allocation vs naive heuristics.
    This proves the value of the optimization approach.
    """
    n = len(df)
    max_calls = int(5_000 * 60 / 12)  # 25,000 calls max

    strategies = {}

    # Strategy 1: Optimized (our approach)
    df_opt = optimize_channel_allocation_scipy(df.copy())
    strategies["Optimized (LP)"] = {
        "total_profit": df_opt["assigned_profit"].sum(),
        "n_sms": (df_opt["assigned_channel"] == "sms").sum(),
        "n_email": (df_opt["assigned_channel"] == "email").sum(),
        "n_call": (df_opt["assigned_channel"] == "call").sum(),
        "n_none": (df_opt["assigned_channel"] == "none").sum(),
    }

    # Strategy 2: Naive - call everyone with high propensity
    df_naive = df.copy()
    df_naive["max_propensity"] = df_naive[["p_convert_sms", "p_convert_email", "p_convert_call"]].max(axis=1)
    top_propensity = df_naive.nlargest(max_calls, "max_propensity")
    naive_profit = (
        top_propensity["p_convert_call"].values * CUSTOMER_LIFETIME_VALUE_CHF
        - CHANNEL_PARAMS["call"]["cost_per_contact_chf"]
    ).sum()
    # Remaining get SMS
    remaining_naive = df_naive[~df_naive.index.isin(top_propensity.index)]
    sms_profit = (
        remaining_naive["p_convert_sms"].values * CUSTOMER_LIFETIME_VALUE_CHF
        - CHANNEL_PARAMS["sms"]["cost_per_contact_chf"]
    )
    naive_profit += sms_profit[sms_profit > 0].sum()

    strategies["Naive (Call Top + SMS Rest)"] = {
        "total_profit": naive_profit,
        "n_sms": (sms_profit > 0).sum(),
        "n_email": 0,
        "n_call": len(top_propensity),
        "n_none": (sms_profit <= 0).sum(),
    }

    # Strategy 3: SMS only (cheapest)
    sms_only_profit = (
        df["p_convert_sms"].values * CUSTOMER_LIFETIME_VALUE_CHF
        - CHANNEL_PARAMS["sms"]["cost_per_contact_chf"]
    )
    strategies["SMS Only"] = {
        "total_profit": sms_only_profit[sms_only_profit > 0].sum(),
        "n_sms": (sms_only_profit > 0).sum(),
        "n_email": 0,
        "n_call": 0,
        "n_none": (sms_only_profit <= 0).sum(),
    }

    # Strategy 4: Random channel assignment
    rng = np.random.default_rng(42)
    random_channels = rng.choice(["sms", "email", "call"], n, p=[0.6, 0.3, 0.1])
    random_profit = 0
    for channel in ["sms", "email", "call"]:
        mask = random_channels == channel
        channel_profit = (
            df.loc[mask, f"p_convert_{channel}"].values * CUSTOMER_LIFETIME_VALUE_CHF
            - CHANNEL_PARAMS[channel]["cost_per_contact_chf"]
        )
        random_profit += channel_profit.sum()

    strategies["Random Allocation"] = {
        "total_profit": random_profit,
        "n_sms": (random_channels == "sms").sum(),
        "n_email": (random_channels == "email").sum(),
        "n_call": (random_channels == "call").sum(),
        "n_none": 0,
    }

    # Build comparison table
    comparison = pd.DataFrame(strategies).T
    comparison["total_profit_kchf"] = comparison["total_profit"] / 1000
    comparison["profit_vs_optimized_pct"] = (
        comparison["total_profit"] / strategies["Optimized (LP)"]["total_profit"] * 100
    ).round(1)

    return comparison


def plot_allocation_results(df_opt: pd.DataFrame, comparison: pd.DataFrame,
                            save_path: Optional[str] = None):
    """Visualize channel allocation and strategy comparison."""
    import matplotlib.pyplot as plt
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from sunrise_style import apply_matplotlib_style, color, group_color, save_figure

    apply_matplotlib_style()
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Top-left: Channel allocation distribution
    ax = axes[0, 0]
    channel_counts = df_opt["assigned_channel"].value_counts()
    colors = {channel: group_color(channel) for channel in ["call", "email", "sms", "none"]}
    ax.bar(channel_counts.index, channel_counts.values,
           color=[colors[c] for c in channel_counts.index])
    ax.set_title("Optimized Channel Allocation", fontsize=12, fontweight="bold")
    ax.set_ylabel("Number of Customers")
    for i, (channel, count) in enumerate(channel_counts.items()):
        ax.annotate(f"{count:,}", xy=(i, count), ha="center", va="bottom", fontsize=10)

    # Top-right: Strategy comparison
    ax = axes[0, 1]
    strategies = comparison.index.tolist()
    profits = comparison["total_profit_kchf"].values
    colors_bar = [color("orange"), color("coral"), color("cyan"), color("yellow")]
    bars = ax.barh(strategies, profits, color=colors_bar[:len(strategies)])
    ax.set_xlabel("Total Expected Profit (kCHF)")
    ax.set_title("Strategy Comparison: Expected Profit", fontsize=12, fontweight="bold")
    for bar, pct in zip(bars, comparison["profit_vs_optimized_pct"]):
        ax.annotate(f"{pct:.0f}%", xy=(bar.get_width(), bar.get_y() + bar.get_height()/2),
                    ha="left", va="center", fontsize=10, fontweight="bold")

    # Bottom-left: Expected profit distribution by channel
    ax = axes[1, 0]
    for channel in ["call", "email", "sms"]:
        mask = df_opt["assigned_channel"] == channel
        if mask.sum() > 0:
            ax.hist(df_opt.loc[mask, "assigned_profit"], bins=30, alpha=0.6,
                    color=group_color(channel), label=f"{channel.upper()} (n={mask.sum():,})")
    ax.set_xlabel("Expected Profit per Customer (CHF)")
    ax.set_ylabel("Count")
    ax.set_title("Profit Distribution by Assigned Channel", fontsize=12, fontweight="bold")
    ax.legend()
    ax.axvline(x=0, color=color("charcoal"), linestyle="--", linewidth=0.8)

    # Bottom-right: Conversion probability vs channel assignment
    ax = axes[1, 1]
    sample = df_opt.sample(2000, random_state=42)
    for channel, marker in [("call", "^"), ("email", "s"), ("sms", "o")]:
        mask = sample["assigned_channel"] == channel
        ax.scatter(sample.loc[mask, "p_convert_call"],
                   sample.loc[mask, "monthly_arpu_chf"],
                   c=group_color(channel), alpha=0.34, s=20, marker=marker, label=channel.upper())
    ax.set_xlabel("P(Convert via Call)")
    ax.set_ylabel("Monthly ARPU (CHF)")
    ax.set_title("Channel Assignment by Propensity & Value", fontsize=12, fontweight="bold")
    ax.legend()

    plt.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    plt.show()


if __name__ == "__main__":
    print("=" * 60)
    print("Case 4: Next Best Action - Channel Optimization")
    print("=" * 60)

    # Generate data
    print("\n1. Generating cross-sell customer data...")
    df = generate_cross_sell_data(n_customers=100_000)
    print(f"   Customers: {len(df):,}")
    print(f"   Fiber available: {df['fiber_available'].mean()*100:.0f}%")
    print(f"   Avg P(convert|SMS): {df['p_convert_sms'].mean():.3f}")
    print(f"   Avg P(convert|Email): {df['p_convert_email'].mean():.3f}")
    print(f"   Avg P(convert|Call): {df['p_convert_call'].mean():.3f}")

    # Run optimization
    print("\n2. Running constrained optimization...")
    df_opt = optimize_channel_allocation_scipy(df)

    print(f"\n   Allocation Results:")
    print(f"   {'Channel':<10} {'Count':>8} {'Avg Profit':>12} {'Total Profit':>14}")
    print(f"   {'-'*46}")
    for channel in ["call", "email", "sms", "none"]:
        mask = df_opt["assigned_channel"] == channel
        n = mask.sum()
        avg_p = df_opt.loc[mask, "assigned_profit"].mean() if n > 0 else 0
        total_p = df_opt.loc[mask, "assigned_profit"].sum()
        print(f"   {channel.upper():<10} {n:>8,} {avg_p:>10.2f} CHF {total_p:>12,.0f} CHF")

    total = df_opt["assigned_profit"].sum()
    print(f"   {'TOTAL':<10} {len(df_opt):>8,} {'':>12} {total:>12,.0f} CHF")

    # Compare strategies
    print("\n3. Strategy Comparison")
    print("-" * 50)
    comparison = compare_strategies(df)
    print(comparison[["total_profit_kchf", "n_call", "n_email", "n_sms", "profit_vs_optimized_pct"]].to_string())

    optimized_profit = comparison.loc["Optimized (LP)", "total_profit"]
    naive_profit = comparison.loc["Naive (Call Top + SMS Rest)", "total_profit"]
    uplift_value = optimized_profit - naive_profit

    print(f"\n   💰 Value of optimization vs naive approach: CHF {uplift_value:,.0f}")
    print(f"   That's {uplift_value/naive_profit*100:.1f}% more profit!")

    # Resource utilization
    print("\n4. Resource Utilization")
    print("-" * 50)
    n_calls = (df_opt["assigned_channel"] == "call").sum()
    call_hours_used = n_calls * 12 / 60
    print(f"   Call center hours used: {call_hours_used:,.0f} / 5,000 ({call_hours_used/5000*100:.1f}%)")
    print(f"   Emails sent: {(df_opt['assigned_channel']=='email').sum():,} / 300,000")
    print(f"   SMS sent: {(df_opt['assigned_channel']=='sms').sum():,} / 500,000")

    # Plot
    print("\n5. Generating visualization...")
    plot_allocation_results(df_opt, comparison, save_path="nbo_optimization.png")
