"""
Case 3: A/B Test Design & Power Analysis
==========================================

Business Context:
- Product wants to change auto-renewal toggle to 'ON' by default (prepaid app)
- Test on 5% of users
- Need to know: How long to run? How to detect success without hurting NPS?

Key Insight:
This isn't just "run a t-test on revenue." You need:
1. Proper power analysis (can you detect the effect with 5% traffic?)
2. Guardrail metrics (NPS, uninstalls, support calls)
3. Variance reduction (CUPED) to run tests faster
4. Sequential testing considerations (peeking problem)

The trap: An aggressive change might spike short-term revenue but cause
long-term app uninstalls. Guard against this with guardrail metrics.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple, Optional


# =============================================================================
# POWER ANALYSIS
# =============================================================================

def compute_sample_size(
    baseline_metric: float,
    mde_relative: float,
    alpha: float = 0.05,
    power: float = 0.80,
    metric_std: Optional[float] = None,
    two_sided: bool = True,
    ratio: float = 1.0,
) -> Dict:
    """
    Calculate required sample size for A/B test.

    Args:
        baseline_metric: Current value of primary metric (e.g., ARPU = 25 CHF)
        mde_relative: Minimum Detectable Effect as relative change (e.g., 0.05 = 5%)
        alpha: Significance level (Type I error rate)
        power: Statistical power (1 - Type II error rate)
        metric_std: Standard deviation of the metric. If None, estimated from baseline.
        two_sided: Whether to use two-sided test
        ratio: Ratio of control to treatment size (1.0 = equal split)

    Returns:
        Dict with sample size per group, total, and duration estimate
    """
    mde_absolute = baseline_metric * mde_relative

    if metric_std is None:
        # For revenue metrics, std is typically 2-3x the mean
        metric_std = baseline_metric * 2.5

    # Z-scores
    z_alpha = stats.norm.ppf(1 - alpha / (2 if two_sided else 1))
    z_beta = stats.norm.ppf(power)

    # Sample size formula (per group)
    n_per_group = (
        (z_alpha + z_beta) ** 2
        * (metric_std ** 2 * (1 + 1/ratio))
        / mde_absolute ** 2
    )

    n_per_group = int(np.ceil(n_per_group))
    n_total = int(np.ceil(n_per_group * (1 + ratio)))

    return {
        "n_per_group": n_per_group,
        "n_total": n_total,
        "n_treatment": n_per_group,
        "n_control": int(np.ceil(n_per_group * ratio)),
        "mde_absolute": mde_absolute,
        "mde_relative_pct": mde_relative * 100,
        "alpha": alpha,
        "power": power,
        "metric_std": metric_std,
    }


def compute_test_duration(
    n_required: int,
    daily_traffic: int,
    traffic_fraction: float = 0.05,
) -> Dict:
    """
    Calculate how long to run the test given traffic constraints.

    Args:
        n_required: Total sample size needed
        daily_traffic: Daily active users
        traffic_fraction: Fraction of traffic allocated to experiment (e.g., 0.05 = 5%)
    """
    daily_experiment_users = daily_traffic * traffic_fraction
    days_needed = int(np.ceil(n_required / daily_experiment_users))

    # Add buffer for weekly seasonality (round up to full weeks)
    weeks_needed = int(np.ceil(days_needed / 7))
    days_with_buffer = weeks_needed * 7

    return {
        "days_minimum": days_needed,
        "days_recommended": days_with_buffer,
        "weeks_recommended": weeks_needed,
        "daily_experiment_users": daily_experiment_users,
        "effective_daily_per_group": daily_experiment_users / 2,
    }


def power_curve(
    baseline_metric: float,
    metric_std: float,
    n_per_group: int,
    alpha: float = 0.05,
    mde_range: Optional[np.ndarray] = None,
) -> pd.DataFrame:
    """Generate power curve for different effect sizes."""
    if mde_range is None:
        mde_range = np.linspace(0.01, 0.20, 50)

    results = []
    for mde in mde_range:
        mde_abs = baseline_metric * mde
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        se = metric_std * np.sqrt(2 / n_per_group)
        z_beta = mde_abs / se - z_alpha
        power = stats.norm.cdf(z_beta)

        results.append({
            "mde_relative_pct": mde * 100,
            "mde_absolute": mde_abs,
            "power": power,
        })

    return pd.DataFrame(results)


# =============================================================================
# EXPERIMENT BLUEPRINT
# =============================================================================

def generate_experiment_blueprint(
    experiment_name: str = "Auto-Renewal Default ON",
    primary_metric: str = "Monthly Revenue per User (CHF)",
    baseline_value: float = 25.0,
    metric_std: float = 60.0,
    mde_relative: float = 0.05,
    daily_dau: int = 500_000,
    traffic_fraction: float = 0.05,
    guardrail_metrics: Optional[list] = None,
) -> str:
    """
    Generate a complete experiment blueprint document.
    This is what you present to stakeholders before running the test.
    """
    if guardrail_metrics is None:
        guardrail_metrics = [
            {"name": "App Uninstall Rate", "baseline": "2.1%", "threshold": "+0.5%",
             "action": "STOP test if degradation > 0.5pp"},
            {"name": "NPS Score", "baseline": "32", "threshold": "-3 points",
             "action": "STOP test if NPS drops > 3 points"},
            {"name": "Support Call Rate", "baseline": "1.8%", "threshold": "+0.3%",
             "action": "FLAG for review if > 0.3pp increase"},
            {"name": "30-day Retention", "baseline": "78%", "threshold": "-2%",
             "action": "STOP test if retention drops > 2pp"},
        ]

    # Compute sample size
    ss = compute_sample_size(baseline_value, mde_relative, metric_std=metric_std)
    duration = compute_test_duration(ss["n_total"], daily_dau, traffic_fraction)

    blueprint = f"""
{'='*70}
EXPERIMENT BLUEPRINT: {experiment_name}
{'='*70}

1. HYPOTHESIS
   Changing the auto-renewal toggle default to ON will increase monthly
   revenue per user by at least {mde_relative*100:.0f}% (CHF {ss['mde_absolute']:.2f}/user/month)
   without materially degrading customer satisfaction.

2. PRIMARY METRIC
   {primary_metric}
   - Baseline: CHF {baseline_value:.2f}
   - MDE: {mde_relative*100:.1f}% relative = CHF {ss['mde_absolute']:.2f} absolute
   - Standard deviation: CHF {metric_std:.2f}

3. SAMPLE SIZE & DURATION
   - Required per group: {ss['n_per_group']:,} users
   - Total required: {ss['n_total']:,} users
   - Traffic allocation: {traffic_fraction*100:.0f}% of DAU ({daily_dau:,})
   - Daily users in experiment: {duration['daily_experiment_users']:,.0f}
   - Minimum duration: {duration['days_minimum']} days
   - Recommended duration: {duration['days_recommended']} days ({duration['weeks_recommended']} weeks)

4. STATISTICAL PARAMETERS
   - Significance level (α): {ss['alpha']}
   - Statistical power (1-β): {ss['power']}
   - Test type: Two-sided
   - Analysis: CUPED-adjusted (see variance reduction section)

5. GUARDRAIL METRICS (STOP CONDITIONS)
"""
    for gm in guardrail_metrics:
        blueprint += f"   ⚠️  {gm['name']}: Baseline={gm['baseline']}, Threshold={gm['threshold']}\n"
        blueprint += f"       Action: {gm['action']}\n"

    blueprint += f"""
6. RANDOMIZATION
   - Unit: User-level (by customer_id hash)
   - Allocation: 50/50 within experiment traffic
   - Stratification: By product type (prepaid plan tier)

7. ANALYSIS PLAN
   - Primary analysis at day {duration['days_recommended']} (pre-registered)
   - No peeking before minimum duration ({duration['days_minimum']} days)
   - Use CUPED with 30-day pre-experiment revenue as covariate
   - Bonferroni correction for guardrail metrics

8. DECISION FRAMEWORK
   - IF primary metric significant AND no guardrail violations → SHIP
   - IF primary metric significant BUT guardrail violated → INVESTIGATE
   - IF primary metric NOT significant → DO NOT SHIP
   - IF guardrail violated regardless of primary → STOP immediately

{'='*70}
"""
    return blueprint


if __name__ == "__main__":
    print("=" * 60)
    print("Case 3: A/B Test Power Analysis & Experiment Design")
    print("=" * 60)

    # Scenario: Auto-renewal toggle test
    print("\n1. Power Analysis for Auto-Renewal Test")
    print("-" * 40)

    # Parameters for prepaid mobile
    baseline_arpu = 25.0  # CHF/month
    arpu_std = 60.0       # High variance (many zero-revenue days)
    mde = 0.05            # 5% relative lift
    daily_dau = 500_000   # Daily active users
    traffic_pct = 0.05    # 5% experiment traffic

    ss = compute_sample_size(
        baseline_metric=baseline_arpu,
        mde_relative=mde,
        metric_std=arpu_std,
        power=0.80
    )

    print(f"  Baseline ARPU: CHF {baseline_arpu}")
    print(f"  Target MDE: {mde*100:.0f}% = CHF {ss['mde_absolute']:.2f}")
    print(f"  Required sample size per group: {ss['n_per_group']:,}")
    print(f"  Total sample required: {ss['n_total']:,}")

    duration = compute_test_duration(ss["n_total"], daily_dau, traffic_pct)
    print(f"\n  With {traffic_pct*100:.0f}% traffic ({daily_dau:,} DAU):")
    print(f"  Minimum test duration: {duration['days_minimum']} days")
    print(f"  Recommended duration: {duration['days_recommended']} days ({duration['weeks_recommended']} weeks)")

    # Power curve
    print("\n2. Power Curve Analysis")
    print("-" * 40)
    pc = power_curve(baseline_arpu, arpu_std, ss["n_per_group"])
    print("  MDE%  | Power")
    print("  ------|------")
    for _, row in pc[pc["mde_relative_pct"].isin([2, 3, 5, 7, 10, 15])].iterrows():
        print(f"  {row['mde_relative_pct']:5.1f}% | {row['power']:.3f}")

    # Generate blueprint
    print("\n3. Experiment Blueprint")
    blueprint = generate_experiment_blueprint()
    print(blueprint)
