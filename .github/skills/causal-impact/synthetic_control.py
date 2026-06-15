"""
Case 2: Causal Impact Analysis - Campaign Evaluation Without A/B Test
======================================================================

Business Context:
- Nationwide billboard + TV campaign for Converged Internet+Mobile plan
- No control group was set up
- CMO claims sales are up 15% due to the campaign
- Question: Was the 15% increase actually caused by the campaign?

Key Insight:
Without a control group, we construct a SYNTHETIC COUNTERFACTUAL using:
1. Time series of the target metric (daily sales)
2. Covariates that were NOT affected by the campaign (competitor pricing,
   weather, seasonality, Google Trends for competitor brands)

The synthetic control tells us: "What WOULD sales have been without the campaign?"
The difference between actual and counterfactual = campaign's causal effect.

Packages: CausalImpact (tfcausalimpact), DoWhy, statsmodels
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Tuple, Optional


def generate_campaign_time_series(
    n_days_pre: int = 180,
    n_days_post: int = 90,
    true_campaign_effect_pct: float = 0.08,  # True effect is 8%, not the claimed 15%
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic daily sales data for causal impact analysis.

    The data includes:
    - Pre-campaign period (180 days): used to build the counterfactual model
    - Post-campaign period (90 days): where we measure the effect

    The true campaign effect is 8%, but raw pre/post comparison shows ~15%
    because of confounding factors (seasonality, competitor exit, etc.)
    """
    rng = np.random.default_rng(seed)
    n_total = n_days_pre + n_days_post

    # Date index
    start_date = datetime(2025, 4, 1)
    dates = pd.date_range(start=start_date, periods=n_total, freq="D")
    campaign_start = dates[n_days_pre]

    # Base sales trend (slight upward)
    trend = np.linspace(100, 115, n_total)

    # Seasonality (weekly pattern + monthly pattern)
    weekly = 8 * np.sin(2 * np.pi * np.arange(n_total) / 7)
    monthly = 5 * np.sin(2 * np.pi * np.arange(n_total) / 30)

    # Competitor effect: competitor raised prices mid-campaign (confound!)
    competitor_price_increase = np.zeros(n_total)
    competitor_change_day = n_days_pre + 20  # 20 days after campaign start
    competitor_price_increase[competitor_change_day:] = 7  # +7 sales/day from competitor spillover

    # Weather effect (summer = slightly lower sales for home internet)
    day_of_year = np.array([(start_date + timedelta(days=i)).timetuple().tm_yday for i in range(n_total)])
    weather_effect = -3 * np.sin(2 * np.pi * (day_of_year - 80) / 365)

    # Google Trends for "Sunrise Internet" (proxy for organic interest)
    google_trends = trend * 0.3 + rng.normal(0, 2, n_total)

    # Market growth (general market expansion)
    market_growth = np.zeros(n_total)
    market_growth[n_days_pre:] = np.linspace(0, 5, n_days_post)  # Market growing anyway

    # TRUE campaign effect (only in post period)
    campaign_effect = np.zeros(n_total)
    campaign_effect[n_days_pre:] = true_campaign_effect_pct * trend[n_days_pre:]

    # Actual daily sales
    noise = rng.normal(0, 4, n_total)
    daily_sales = (
        trend + weekly + monthly + competitor_price_increase +
        weather_effect + market_growth + campaign_effect + noise
    ).clip(50, 200)

    # Covariates (observable but not affected by campaign)
    df = pd.DataFrame({
        "date": dates,
        "daily_sales": daily_sales.round(0).astype(int),
        # Covariates for the model
        "competitor_avg_price": 59.90 + rng.normal(0, 1, n_total) + np.where(
            np.arange(n_total) >= competitor_change_day, 10, 0
        ),
        "google_trends_competitor": 50 + rng.normal(0, 5, n_total) - np.where(
            np.arange(n_total) >= competitor_change_day, 8, 0
        ),
        "temperature_celsius": 10 + 15 * np.sin(2 * np.pi * (day_of_year - 80) / 365) + rng.normal(0, 3, n_total),
        "is_weekend": pd.Series(dates).dt.dayofweek.isin([5, 6]).astype(int).values,
        "google_trends_sunrise": google_trends.round(1),
        "market_index": 100 + np.cumsum(rng.normal(0.02, 0.5, n_total)),
    })

    # Mark periods
    df["period"] = np.where(df["date"] >= campaign_start, "post", "pre")
    df["campaign_start"] = campaign_start

    return df


def run_causal_impact_tfcausal(
    df: pd.DataFrame,
    target_col: str = "daily_sales",
    covariate_cols: Optional[list] = None,
) -> dict:
    """
    Run CausalImpact analysis using tfcausalimpact.

    This constructs a Bayesian structural time-series model on the
    pre-period, then projects what would have happened without intervention.
    """
    from tfcausalimpact import CausalImpact

    if covariate_cols is None:
        covariate_cols = [
            "competitor_avg_price", "google_trends_competitor",
            "temperature_celsius", "market_index"
        ]

    # Prepare data: target + covariates, indexed by date
    analysis_df = df[["date", target_col] + covariate_cols].copy()
    analysis_df = analysis_df.set_index("date")

    # Define pre and post periods
    campaign_start = df["campaign_start"].iloc[0]
    pre_period = [analysis_df.index[0], campaign_start - timedelta(days=1)]
    post_period = [campaign_start, analysis_df.index[-1]]

    # Run CausalImpact
    ci = CausalImpact(
        analysis_df,
        pre_period,
        post_period,
        prior_level_sd=None  # Auto-detect
    )

    # Extract results
    summary = ci.summary()
    report = ci.summary(output="report")

    results = {
        "model": ci,
        "summary_text": summary,
        "report": report,
        "pre_period": pre_period,
        "post_period": post_period,
    }

    return results


def run_causal_impact_statsmodels(
    df: pd.DataFrame,
    target_col: str = "daily_sales",
    covariate_cols: Optional[list] = None,
) -> dict:
    """
    Alternative: Synthetic control using statsmodels (Bayesian structural time series).
    Useful if tfcausalimpact has dependency issues.
    """
    import statsmodels.api as sm
    from statsmodels.tsa.statespace.structural import UnobservedComponents

    if covariate_cols is None:
        covariate_cols = [
            "competitor_avg_price", "google_trends_competitor",
            "temperature_celsius", "market_index"
        ]

    campaign_start = df["campaign_start"].iloc[0]
    pre_df = df[df["date"] < campaign_start].copy()
    post_df = df[df["date"] >= campaign_start].copy()

    # Fit structural time series on pre-period
    y_pre = pre_df[target_col].values
    X_pre = pre_df[covariate_cols].values

    # Build model with trend + seasonality + covariates
    model = UnobservedComponents(
        y_pre,
        level="local linear trend",
        seasonal=7,  # Weekly seasonality
        exog=X_pre,
    )
    fitted = model.fit(disp=False)

    # Predict counterfactual for post period
    X_post = post_df[covariate_cols].values
    n_post = len(post_df)

    forecast = fitted.get_forecast(steps=n_post, exog=X_post)
    counterfactual = forecast.predicted_mean
    ci_lower = forecast.conf_int()[:, 0]
    ci_upper = forecast.conf_int()[:, 1]

    # Actual vs counterfactual
    actual_post = post_df[target_col].values
    point_effect = actual_post - counterfactual
    cumulative_effect = np.cumsum(point_effect)

    # Relative effect
    relative_effect = point_effect.sum() / counterfactual.sum()

    results = {
        "dates_post": post_df["date"].values,
        "actual": actual_post,
        "counterfactual": counterfactual,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "point_effect": point_effect,
        "cumulative_effect": cumulative_effect,
        "total_incremental_sales": point_effect.sum(),
        "relative_effect_pct": relative_effect * 100,
        "avg_daily_lift": point_effect.mean(),
    }

    return results


def plot_causal_impact(results: dict, df: pd.DataFrame,
                       target_col: str = "daily_sales",
                       save_path: Optional[str] = None):
    """
    Create the classic 3-panel causal impact chart:
    1. Actual vs Counterfactual
    2. Point-wise effect
    3. Cumulative effect
    """
    import matplotlib.pyplot as plt
    import sys
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[3]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from sunrise_style import apply_matplotlib_style, color, save_figure

    campaign_start = df["campaign_start"].iloc[0]
    pre_df = df[df["date"] < campaign_start]

    apply_matplotlib_style()
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)

    # Panel 1: Actual vs Counterfactual
    ax = axes[0]
    ax.plot(pre_df["date"], pre_df[target_col], color=color("charcoal"), linewidth=1, label="Pre-period (Actual)")
    ax.plot(results["dates_post"], results["actual"], color=color("blue"), linewidth=1.7, label="Post-period (Actual)")
    ax.plot(results["dates_post"], results["counterfactual"], color=color("coral"), linewidth=1.7,
            linestyle="--", label="Counterfactual (No Campaign)")
    ax.fill_between(results["dates_post"], results["ci_lower"], results["ci_upper"],
                    color=color("coral"), alpha=0.12, label="95% CI")
    ax.axvline(x=campaign_start, color=color("charcoal"), linestyle=":", linewidth=1.5, label="Campaign Start")
    ax.set_ylabel("Daily Sales", fontsize=11)
    ax.set_title("Causal Impact Analysis: Billboard + TV Campaign", fontsize=13, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(True, alpha=0.3)

    # Panel 2: Point-wise effect
    ax = axes[1]
    ax.plot(results["dates_post"], results["point_effect"], color=color("orange"), linewidth=1.7)
    ax.fill_between(results["dates_post"],
                    results["point_effect"] - (results["ci_upper"] - results["counterfactual"]),
                    results["point_effect"] + (results["counterfactual"] - results["ci_lower"]),
                    color=color("orange"), alpha=0.15)
    ax.axhline(y=0, color=color("charcoal"), linestyle="-", linewidth=0.8)
    ax.axvline(x=campaign_start, color=color("charcoal"), linestyle=":", linewidth=1.5)
    ax.set_ylabel("Point Effect\n(Sales Lift)", fontsize=11)
    ax.set_title("Daily Incremental Sales Due to Campaign", fontsize=12)
    ax.grid(True, alpha=0.3)

    # Panel 3: Cumulative effect
    ax = axes[2]
    ax.plot(results["dates_post"], results["cumulative_effect"], color=color("cyan"), linewidth=2.2)
    ax.fill_between(results["dates_post"], 0, results["cumulative_effect"],
                    color=color("cyan"), alpha=0.16)
    ax.axhline(y=0, color=color("charcoal"), linestyle="-", linewidth=0.8)
    ax.axvline(x=campaign_start, color=color("charcoal"), linestyle=":", linewidth=1.5)
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Cumulative Effect\n(Total Extra Sales)", fontsize=11)
    ax.set_title(f"Cumulative Incremental Sales: {results['total_incremental_sales']:.0f} total", fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        save_figure(fig, save_path)
    plt.show()


def generate_business_summary(results: dict, campaign_cost_chf: float = 2_000_000) -> str:
    """
    Generate executive summary for the CMO.
    Translates statistical results into business language.
    """
    total_lift = results["total_incremental_sales"]
    relative_pct = results["relative_effect_pct"]
    avg_daily = results["avg_daily_lift"]

    # Assume avg revenue per sale
    avg_revenue_per_sale = 89.90  # CHF for converged plan
    incremental_revenue = total_lift * avg_revenue_per_sale
    roi = (incremental_revenue - campaign_cost_chf) / campaign_cost_chf * 100

    summary = f"""
{'='*60}
EXECUTIVE SUMMARY: Campaign Causal Impact Analysis
{'='*60}

FINDING: The campaign DID have a positive effect, but smaller than claimed.

CMO's Claim: Sales up 15% due to the campaign
Our Finding: Campaign caused a {relative_pct:.1f}% lift in sales

The remaining ~{15 - relative_pct:.0f}% was due to:
  - Competitor price increase (Salt raised prices by CHF 10/month)
  - Seasonal market growth
  - General market trend

KEY METRICS:
  - Total incremental sales (campaign-caused): {total_lift:.0f} units
  - Average daily sales lift: {avg_daily:.1f} units/day
  - Estimated incremental revenue: CHF {incremental_revenue:,.0f}
  - Campaign cost: CHF {campaign_cost_chf:,.0f}
  - Campaign ROI: {roi:.1f}%

RECOMMENDATION:
  {'✅ Campaign was profitable (ROI > 0%)' if roi > 0 else '❌ Campaign was not cost-effective'}
  - The campaign IS effective but the CMO should not claim the full 15%
  - For future campaigns, set up regional holdout groups for cleaner measurement
{'='*60}
"""
    return summary


if __name__ == "__main__":
    print("=" * 60)
    print("Case 2: Causal Impact - Campaign Without Control Group")
    print("=" * 60)

    # Generate synthetic data
    print("\n1. Generating time series data...")
    df = generate_campaign_time_series(
        n_days_pre=180,
        n_days_post=90,
        true_campaign_effect_pct=0.08
    )
    print(f"   Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"   Campaign start: {df['campaign_start'].iloc[0].date()}")
    print(f"   Pre-period avg sales: {df[df['period']=='pre']['daily_sales'].mean():.1f}")
    print(f"   Post-period avg sales: {df[df['period']=='post']['daily_sales'].mean():.1f}")
    naive_lift = (
        df[df["period"] == "post"]["daily_sales"].mean() /
        df[df["period"] == "pre"]["daily_sales"].mean() - 1
    ) * 100
    print(f"   Naive pre/post lift: {naive_lift:.1f}% (THIS IS MISLEADING!)")

    # Run statsmodels version (always available)
    print("\n2. Running structural time series counterfactual...")
    try:
        results = run_causal_impact_statsmodels(df)
        print(f"   ✓ True campaign effect: {results['relative_effect_pct']:.1f}%")
        print(f"   ✓ Total incremental sales: {results['total_incremental_sales']:.0f}")
        print(f"   ✓ Average daily lift: {results['avg_daily_lift']:.1f} sales/day")

        # Plot
        plot_causal_impact(results, df, save_path="causal_impact_chart.png")

        # Business summary
        print(generate_business_summary(results))

    except Exception as e:
        print(f"   ⚠ Error: {e}")
        print("   Ensure statsmodels is installed: pip install statsmodels")

    # Try tfcausalimpact
    print("\n3. Attempting tfcausalimpact (Google's CausalImpact)...")
    try:
        ci_results = run_causal_impact_tfcausal(df)
        print(ci_results["summary_text"])
    except ImportError:
        print("   ⚠ tfcausalimpact not installed")
        print("   Install with: pip install tfcausalimpact")
    except Exception as e:
        print(f"   ⚠ Error: {e}")
