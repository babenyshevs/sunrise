"""
Uplift Evaluation Metrics: Qini Curves & Uplift Decile Charts
==============================================================

These are the KEY charts that demonstrate you understand uplift modeling.
They show that targeting the top uplift deciles yields better ROI than
random targeting or propensity-based targeting.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sunrise_style import apply_matplotlib_style, color, group_color, save_figure


def compute_qini_curve(y_true: np.ndarray, uplift_scores: np.ndarray,
                       treatment: np.ndarray) -> dict:
    """
    Compute Qini curve data points.

    The Qini curve shows the incremental number of positive outcomes
    (prevented churns) as we target more customers, ordered by uplift score.

    A good uplift model will have a Qini curve well above the diagonal (random).
    """
    n = len(y_true)

    # Sort by predicted uplift (descending - most negative uplift first for churn)
    # For churn: negative uplift means treatment REDUCES churn
    order = np.argsort(uplift_scores)  # ascending = most negative first = best

    y_sorted = y_true[order]
    t_sorted = treatment[order]

    # Compute cumulative Qini
    n_t = np.cumsum(t_sorted)
    n_c = np.cumsum(1 - t_sorted)

    # Avoid division by zero
    n_t = np.maximum(n_t, 1)
    n_c = np.maximum(n_c, 1)

    # Cumulative outcomes
    cum_y_t = np.cumsum(y_sorted * t_sorted)
    cum_y_c = np.cumsum(y_sorted * (1 - t_sorted))

    # Qini: (outcomes_treatment / n_treatment - outcomes_control / n_control) * n_total_so_far
    # For churn prevention: we want FEWER churns in treatment
    qini = (cum_y_c / n_c - cum_y_t / n_t) * np.arange(1, n + 1)

    # Random baseline
    total_uplift = qini[-1]
    random_qini = np.linspace(0, total_uplift, n)

    # Fraction targeted
    fraction = np.arange(1, n + 1) / n

    return {
        "fraction_targeted": fraction,
        "qini": qini,
        "random_qini": random_qini,
        "qini_auc": np.trapz(qini, fraction) - np.trapz(random_qini, fraction)
    }


def compute_uplift_by_decile(y_true: np.ndarray, uplift_scores: np.ndarray,
                             treatment: np.ndarray, n_bins: int = 10) -> pd.DataFrame:
    """
    Compute actual uplift by decile of predicted uplift.

    This is the "money chart" - shows that top deciles have real uplift
    while bottom deciles may have zero or negative uplift.
    """
    df = pd.DataFrame({
        "y": y_true,
        "treatment": treatment,
        "uplift_score": uplift_scores
    })

    # Create deciles based on predicted uplift
    df["decile"] = pd.qcut(df["uplift_score"], n_bins, labels=False, duplicates="drop")

    results = []
    for decile in sorted(df["decile"].unique()):
        subset = df[df["decile"] == decile]
        treated = subset[subset["treatment"] == 1]
        control = subset[subset["treatment"] == 0]

        churn_rate_treated = treated["y"].mean() if len(treated) > 0 else 0
        churn_rate_control = control["y"].mean() if len(control) > 0 else 0

        # Uplift = churn_control - churn_treated (positive = treatment helps)
        actual_uplift = churn_rate_control - churn_rate_treated
        mean_predicted = subset["uplift_score"].mean()

        results.append({
            "decile": decile + 1,
            "n_customers": len(subset),
            "n_treated": len(treated),
            "n_control": len(control),
            "churn_rate_treated": churn_rate_treated,
            "churn_rate_control": churn_rate_control,
            "actual_uplift": actual_uplift,
            "mean_predicted_uplift": mean_predicted
        })

    return pd.DataFrame(results)


def plot_qini_curve(qini_data: dict, title: str = "Qini Curve - Uplift Model Performance",
                    save_path: Optional[str] = None):
    """Plot the Qini curve with random baseline."""
    apply_matplotlib_style()
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    ax.plot(qini_data["fraction_targeted"], qini_data["qini"],
            label=f"Uplift Model (Qini AUC: {qini_data['qini_auc']:.4f})",
        color=color("orange"), linewidth=2.4)
    ax.plot(qini_data["fraction_targeted"], qini_data["random_qini"],
        label="Random Targeting", color=color("slate"), linestyle="--", linewidth=1.5)
    ax.fill_between(qini_data["fraction_targeted"],
                    qini_data["random_qini"], qini_data["qini"],
            alpha=0.16, color=color("orange"))

    ax.set_xlabel("Fraction of Customers Targeted", fontsize=12)
    ax.set_ylabel("Incremental Churns Prevented", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color=color("charcoal"), linewidth=0.8)

    plt.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    plt.show()


def plot_uplift_deciles(decile_df: pd.DataFrame,
                        title: str = "Uplift by Decile - Who Actually Responds?",
                        save_path: Optional[str] = None):
    """Plot uplift decile chart - the business-friendly visualization."""
    apply_matplotlib_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Left: Actual uplift by decile
    colors = [color("green") if x > 0 else color("coral") for x in decile_df["actual_uplift"]]
    ax1.bar(decile_df["decile"], decile_df["actual_uplift"] * 100, color=colors, linewidth=0.5)
    ax1.axhline(y=0, color=color("charcoal"), linewidth=0.8)
    ax1.set_xlabel("Uplift Decile (1 = Highest Predicted Uplift)", fontsize=11)
    ax1.set_ylabel("Actual Churn Reduction (%)", fontsize=11)
    ax1.set_title("Actual Uplift by Predicted Decile", fontsize=12, fontweight="bold")
    ax1.set_xticks(decile_df["decile"])
    ax1.grid(True, alpha=0.3, axis="y")

    # Annotate
    for _, row in decile_df.iterrows():
        ax1.annotate(f"{row['actual_uplift']*100:.1f}%",
                     xy=(row["decile"], row["actual_uplift"] * 100),
                     ha="center", va="bottom" if row["actual_uplift"] > 0 else "top",
                     fontsize=9)

    # Right: Churn rates comparison
    x = np.arange(len(decile_df))
    width = 0.35
    ax2.bar(x - width/2, decile_df["churn_rate_control"] * 100, width,
            label="Control (No Discount)", color=group_color("control"), alpha=0.82)
    ax2.bar(x + width/2, decile_df["churn_rate_treated"] * 100, width,
            label="Treated (With Discount)", color=group_color("treatment"), alpha=0.82)
    ax2.set_xlabel("Uplift Decile", fontsize=11)
    ax2.set_ylabel("Churn Rate (%)", fontsize=11)
    ax2.set_title("Churn Rates: Treated vs Control", fontsize=12, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(decile_df["decile"])
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    plt.show()


if __name__ == "__main__":
    from uplift_churn_model import generate_uplift_experiment_data

    print("Generating evaluation data...")
    df = generate_uplift_experiment_data(n_customers=30_000)

    # Simulate uplift scores (in practice these come from your model)
    # Using true uplift + noise as proxy
    rng = np.random.default_rng(123)
    simulated_uplift_scores = df["true_uplift"].values + rng.normal(0, 0.01, len(df))

    y = df["churned"].values
    treatment = df["treatment"].values

    # Compute and plot Qini curve
    print("\nComputing Qini curve...")
    qini_data = compute_qini_curve(y, simulated_uplift_scores, treatment)
    print(f"Qini AUC: {qini_data['qini_auc']:.4f}")
    plot_qini_curve(qini_data, save_path="qini_curve.png")

    # Compute and plot deciles
    print("\nComputing uplift deciles...")
    decile_df = compute_uplift_by_decile(y, simulated_uplift_scores, treatment)
    print(decile_df.to_string(index=False))
    plot_uplift_deciles(decile_df, save_path="uplift_deciles.png")
