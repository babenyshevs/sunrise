"""
CUPED: Controlled-experiment Using Pre-Experiment Data
=======================================================

Variance Reduction technique that uses pre-experiment data as a covariate
to reduce the variance of the treatment effect estimator.

Key Insight:
If a user spent CHF 50/month before the experiment, they'll probably spend
~CHF 50/month during the experiment too. By conditioning on pre-experiment
behavior, we can dramatically reduce variance → smaller sample sizes → faster tests.

Typical variance reduction: 30-60% (meaning you can run tests 2-3x faster!)

Reference: Deng et al. (2013) "Improving the Sensitivity of Online Controlled
Experiments by Utilizing Pre-Experiment Data"
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Dict, Optional


def proportions_ztest(counts, nobs) -> Tuple[float, float]:
    """Two-sided z-test for difference in two independent proportions."""
    counts = np.asarray(counts, dtype=float)
    nobs = np.asarray(nobs, dtype=float)
    proportions = counts / nobs
    pooled = counts.sum() / nobs.sum()
    standard_error = np.sqrt(pooled * (1 - pooled) * (1 / nobs[0] + 1 / nobs[1]))
    if standard_error == 0:
        return 0.0, 1.0
    z_stat = (proportions[0] - proportions[1]) / standard_error
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    return z_stat, p_value


def generate_experiment_data(
    n_users: int = 50_000,
    true_effect: float = 1.25,  # CHF 1.25 lift (5% of 25 CHF baseline)
    pre_period_days: int = 30,
    experiment_days: int = 28,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate synthetic A/B test data with pre-experiment covariates.

    Simulates the auto-renewal toggle experiment.
    """
    rng = np.random.default_rng(seed)

    # User-level baseline spend (heterogeneous)
    user_baseline = rng.exponential(25, n_users)  # Average 25 CHF

    # Treatment assignment (50/50)
    treatment = rng.choice([0, 1], n_users)

    # Pre-experiment metric (correlated with during-experiment behavior)
    # This is what CUPED uses as the covariate
    pre_experiment_revenue = user_baseline + rng.normal(0, 10, n_users)
    pre_experiment_revenue = pre_experiment_revenue.clip(0, 200)

    # During-experiment metric
    # Highly correlated with pre-period (this is what makes CUPED work!)
    correlation_noise = rng.normal(0, 15, n_users)
    experiment_revenue = (
        user_baseline
        + treatment * true_effect  # True causal effect
        + correlation_noise
    ).clip(0, 200)

    # Guardrail metrics
    # NPS score (slightly negatively affected by aggressive toggle)
    nps_pre = rng.integers(0, 11, n_users)
    nps_during = nps_pre + rng.choice([-1, 0, 0, 0, 1], n_users) - treatment * 0.3

    # App uninstall (binary, slightly higher for treatment)
    uninstall_prob = 0.021 + treatment * 0.002  # Small negative effect
    uninstalled = (rng.random(n_users) < uninstall_prob).astype(int)

    # Support calls
    support_calls_pre = rng.poisson(0.3, n_users)
    support_calls_during = rng.poisson(0.3 + treatment * 0.05, n_users)

    df = pd.DataFrame({
        "user_id": [f"U{i:07d}" for i in range(n_users)],
        "treatment": treatment,
        "pre_revenue": pre_experiment_revenue.round(2),
        "experiment_revenue": experiment_revenue.round(2),
        "nps_pre": nps_pre,
        "nps_during": nps_during.round(1),
        "uninstalled": uninstalled,
        "support_calls_pre": support_calls_pre,
        "support_calls_during": support_calls_during,
    })

    return df


def cuped_adjustment(
    y: np.ndarray,
    x_pre: np.ndarray,
    treatment: np.ndarray,
) -> Tuple[np.ndarray, float]:
    """
    Apply CUPED variance reduction.

    CUPED formula: Y_adjusted = Y - θ * (X_pre - E[X_pre])

    Where θ = Cov(Y, X_pre) / Var(X_pre)

    This removes the variance component explained by pre-experiment behavior.
    """
    # Compute theta (optimal coefficient)
    # Using control group only to avoid bias
    control_mask = treatment == 0
    theta = np.cov(y[control_mask], x_pre[control_mask])[0, 1] / np.var(x_pre[control_mask])

    # Adjust Y
    x_centered = x_pre - x_pre.mean()
    y_adjusted = y - theta * x_centered

    # Variance reduction achieved
    var_original = np.var(y)
    var_adjusted = np.var(y_adjusted)
    variance_reduction_pct = (1 - var_adjusted / var_original) * 100

    return y_adjusted, variance_reduction_pct


def run_ab_test_standard(df: pd.DataFrame, metric_col: str = "experiment_revenue") -> Dict:
    """Run standard t-test without variance reduction."""
    treatment = df[df["treatment"] == 1][metric_col]
    control = df[df["treatment"] == 0][metric_col]

    # Two-sample t-test
    t_stat, p_value = stats.ttest_ind(treatment, control)

    # Effect size
    effect = treatment.mean() - control.mean()
    pooled_std = np.sqrt((treatment.var() + control.var()) / 2)
    ci_95 = 1.96 * pooled_std * np.sqrt(1/len(treatment) + 1/len(control))

    return {
        "method": "Standard t-test",
        "effect": effect,
        "ci_lower": effect - ci_95,
        "ci_upper": effect + ci_95,
        "t_statistic": t_stat,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "std_treatment": treatment.std(),
        "std_control": control.std(),
    }


def run_ab_test_cuped(
    df: pd.DataFrame,
    metric_col: str = "experiment_revenue",
    covariate_col: str = "pre_revenue",
) -> Dict:
    """Run CUPED-adjusted t-test."""
    y = df[metric_col].values
    x_pre = df[covariate_col].values
    treatment = df["treatment"].values

    # Apply CUPED
    y_adjusted, var_reduction = cuped_adjustment(y, x_pre, treatment)

    # Run t-test on adjusted values
    treatment_adj = y_adjusted[treatment == 1]
    control_adj = y_adjusted[treatment == 0]

    t_stat, p_value = stats.ttest_ind(treatment_adj, control_adj)

    effect = treatment_adj.mean() - control_adj.mean()
    pooled_std = np.sqrt((treatment_adj.var() + control_adj.var()) / 2)
    ci_95 = 1.96 * pooled_std * np.sqrt(1/len(treatment_adj) + 1/len(control_adj))

    return {
        "method": "CUPED-adjusted t-test",
        "effect": effect,
        "ci_lower": effect - ci_95,
        "ci_upper": effect + ci_95,
        "t_statistic": t_stat,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "variance_reduction_pct": var_reduction,
        "std_treatment_adjusted": treatment_adj.std(),
        "std_control_adjusted": control_adj.std(),
    }


def check_guardrail_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check guardrail metrics for the experiment.
    These are STOP conditions - if violated, halt the test.
    """
    results = []

    # Guardrail 1: Uninstall rate
    uninstall_treatment = df[df["treatment"] == 1]["uninstalled"].mean()
    uninstall_control = df[df["treatment"] == 0]["uninstalled"].mean()
    uninstall_diff = uninstall_treatment - uninstall_control
    _, p_uninstall = proportions_ztest(
        [df[df["treatment"] == 1]["uninstalled"].sum(), df[df["treatment"] == 0]["uninstalled"].sum()],
        [len(df[df["treatment"] == 1]), len(df[df["treatment"] == 0])]
    )
    results.append({
        "metric": "App Uninstall Rate",
        "treatment": f"{uninstall_treatment*100:.2f}%",
        "control": f"{uninstall_control*100:.2f}%",
        "difference": f"{uninstall_diff*100:+.3f}pp",
        "p_value": p_uninstall,
        "threshold": "+0.5pp",
        "violated": abs(uninstall_diff) > 0.005,
        "status": "⚠️ WATCH" if abs(uninstall_diff) > 0.003 else "✅ OK"
    })

    # Guardrail 2: NPS
    nps_treatment = df[df["treatment"] == 1]["nps_during"].mean()
    nps_control = df[df["treatment"] == 0]["nps_during"].mean()
    nps_diff = nps_treatment - nps_control
    _, p_nps = stats.ttest_ind(
        df[df["treatment"] == 1]["nps_during"],
        df[df["treatment"] == 0]["nps_during"]
    )
    results.append({
        "metric": "NPS Score",
        "treatment": f"{nps_treatment:.2f}",
        "control": f"{nps_control:.2f}",
        "difference": f"{nps_diff:+.3f}",
        "p_value": p_nps,
        "threshold": "-3 points",
        "violated": nps_diff < -3,
        "status": "⚠️ WATCH" if nps_diff < -1 else "✅ OK"
    })

    # Guardrail 3: Support calls
    calls_treatment = df[df["treatment"] == 1]["support_calls_during"].mean()
    calls_control = df[df["treatment"] == 0]["support_calls_during"].mean()
    calls_diff = calls_treatment - calls_control
    _, p_calls = stats.ttest_ind(
        df[df["treatment"] == 1]["support_calls_during"],
        df[df["treatment"] == 0]["support_calls_during"]
    )
    results.append({
        "metric": "Support Calls",
        "treatment": f"{calls_treatment:.3f}",
        "control": f"{calls_control:.3f}",
        "difference": f"{calls_diff:+.4f}",
        "p_value": p_calls,
        "threshold": "+0.3pp",
        "violated": calls_diff > 0.003,
        "status": "⚠️ WATCH" if calls_diff > 0.002 else "✅ OK"
    })

    return pd.DataFrame(results)


def plot_cuped_comparison(df: pd.DataFrame, save_path: Optional[str] = None):
    """Visualize the impact of CUPED on confidence intervals."""
    import matplotlib.pyplot as plt
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from sunrise_style import apply_matplotlib_style, color, group_color, save_figure

    standard = run_ab_test_standard(df)
    cuped = run_ab_test_cuped(df)

    apply_matplotlib_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Left: CI comparison
    methods = ["Standard\nt-test", "CUPED\nadjusted"]
    effects = [standard["effect"], cuped["effect"]]
    ci_lowers = [standard["ci_lower"], cuped["ci_lower"]]
    ci_uppers = [standard["ci_upper"], cuped["ci_upper"]]

    colors = [group_color("standard"), group_color("cuped")]
    for i, (method, effect, ci_l, ci_u, color) in enumerate(
        zip(methods, effects, ci_lowers, ci_uppers, colors)
    ):
        ax1.errorbar(i, effect, yerr=[[effect - ci_l], [ci_u - effect]],
                     fmt="o", color=color, markersize=10, capsize=8, capthick=2, linewidth=2)

    ax1.axhline(y=0, color=color("coral"), linestyle="--", linewidth=1, alpha=0.85)
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(methods, fontsize=11)
    ax1.set_ylabel("Treatment Effect (CHF)", fontsize=11)
    ax1.set_title("CUPED Reduces Confidence Interval Width", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3, axis="y")

    # Annotate CI widths
    for i, (ci_l, ci_u) in enumerate(zip(ci_lowers, ci_uppers)):
        width = ci_u - ci_l
        ax1.annotate(f"CI width: {width:.3f}", xy=(i, ci_u + 0.1),
                     ha="center", fontsize=9, color=colors[i])

    # Right: Distribution comparison
    y = df["experiment_revenue"].values
    x_pre = df["pre_revenue"].values
    treatment = df["treatment"].values
    y_adjusted, var_red = cuped_adjustment(y, x_pre, treatment)

    ax2.hist(y[treatment == 1] - y[treatment == 0].mean(), bins=50,
             alpha=0.55, color=group_color("standard"), label="Original", density=True)
    ax2.hist(y_adjusted[treatment == 1] - y_adjusted[treatment == 0].mean(), bins=50,
             alpha=0.55, color=group_color("cuped"), label=f"CUPED (−{var_red:.0f}% variance)", density=True)
    ax2.set_xlabel("Revenue (CHF)", fontsize=11)
    ax2.set_ylabel("Density", fontsize=11)
    ax2.set_title("Revenue Distribution: Original vs CUPED-Adjusted", fontsize=12, fontweight="bold")
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    plt.show()


if __name__ == "__main__":
    print("=" * 60)
    print("Case 3: CUPED Variance Reduction for A/B Testing")
    print("=" * 60)

    # Generate experiment data
    print("\n1. Generating experiment data (auto-renewal toggle test)...")
    df = generate_experiment_data(n_users=50_000, true_effect=1.25)
    print(f"   Users: {len(df):,}")
    print(f"   Treatment/Control split: {df['treatment'].value_counts().to_dict()}")

    # Standard analysis
    print("\n2. Standard A/B Test Analysis")
    print("-" * 40)
    standard = run_ab_test_standard(df)
    print(f"   Effect: CHF {standard['effect']:.3f}")
    print(f"   95% CI: [{standard['ci_lower']:.3f}, {standard['ci_upper']:.3f}]")
    print(f"   p-value: {standard['p_value']:.4f}")
    print(f"   Significant: {'✅ Yes' if standard['significant'] else '❌ No'}")

    # CUPED analysis
    print("\n3. CUPED-Adjusted Analysis")
    print("-" * 40)
    cuped = run_ab_test_cuped(df)
    print(f"   Effect: CHF {cuped['effect']:.3f}")
    print(f"   95% CI: [{cuped['ci_lower']:.3f}, {cuped['ci_upper']:.3f}]")
    print(f"   p-value: {cuped['p_value']:.6f}")
    print(f"   Significant: {'✅ Yes' if cuped['significant'] else '❌ No'}")
    print(f"   Variance reduction: {cuped['variance_reduction_pct']:.1f}%")

    ci_reduction = (
        (standard["ci_upper"] - standard["ci_lower"]) -
        (cuped["ci_upper"] - cuped["ci_lower"])
    ) / (standard["ci_upper"] - standard["ci_lower"]) * 100
    print(f"   CI width reduction: {ci_reduction:.1f}%")

    # Guardrail metrics
    print("\n4. Guardrail Metrics Check")
    print("-" * 40)
    guardrails = check_guardrail_metrics(df)
    print(guardrails[["metric", "treatment", "control", "difference", "status"]].to_string(index=False))

    # Plot
    print("\n5. Generating visualization...")
    plot_cuped_comparison(df, save_path="cuped_comparison.png")
