from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from sunrise_style import apply_matplotlib_style, color, group_color, marp_frontmatter, save_figure, status_color


ROOT = Path(__file__).resolve().parents[2]
SLUG = "ab-test-mock-data"
NOTEBOOK_PATH = ROOT / "notebooks" / f"{SLUG}.ipynb"
ARTIFACT_DIR = ROOT / "notebooks" / SLUG
RAW_DIR = ARTIFACT_DIR / "raw"
PROCESSED_DIR = ARTIFACT_DIR / "processed"
CHART_DIR = ARTIFACT_DIR / "charts"
DOCS_DIR = ROOT / "docs" / SLUG


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-values))


def ensure_dirs() -> None:
    for directory in [RAW_DIR, PROCESSED_DIR, CHART_DIR, DOCS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def generate_mock_tables(seed: int = 20260612, n_customers: int = 60_000) -> tuple[pd.DataFrame, ...]:
    rng = np.random.default_rng(seed)
    customer_id = np.array([f"CH{index:08d}" for index in range(n_customers)])
    canton = rng.choice(["ZH", "BE", "VD", "GE", "AG", "SG", "LU", "TI", "VS", "BS"], size=n_customers,
                        p=[0.19, 0.13, 0.12, 0.10, 0.10, 0.08, 0.07, 0.07, 0.07, 0.07])
    language = np.where(np.isin(canton, ["VD", "GE", "VS"]), rng.choice(["FR", "DE"], n_customers, p=[0.82, 0.18]),
                        np.where(canton == "TI", "IT", rng.choice(["DE", "FR", "IT"], n_customers, p=[0.82, 0.12, 0.06])))
    tenure_months = rng.integers(1, 121, size=n_customers)
    age = np.clip(rng.normal(43, 14, size=n_customers).round(), 18, 82).astype(int)
    contract_type = rng.choice(["month_to_month", "12_month", "24_month"], size=n_customers, p=[0.34, 0.29, 0.37])
    segment = rng.choice(["mobile_only", "converged", "family", "premium"], size=n_customers, p=[0.44, 0.27, 0.20, 0.09])

    segment_uplift = pd.Series(segment).map({"mobile_only": 0, "converged": 12, "family": 18, "premium": 32}).to_numpy()
    pre_monthly_revenue = np.clip(rng.normal(58 + segment_uplift + tenure_months * 0.04, 18, n_customers), 19.9, 189.9)
    pre_roaming_revenue = rng.gamma(shape=1.7, scale=6.2, size=n_customers)
    summer_traveler = rng.binomial(1, sigmoid(-1.0 + 0.035 * pre_roaming_revenue + (segment == "premium") * 0.55), n_customers)
    pre_roaming_revenue = pre_roaming_revenue + summer_traveler * rng.gamma(1.2, 8.0, n_customers)
    gross_margin_rate = np.clip(rng.normal(0.47, 0.07, n_customers), 0.30, 0.65)

    app_sessions_30d = rng.poisson(4.5 + summer_traveler * 2.1 + (segment == "premium") * 1.2, n_customers)
    days_since_last_app = np.clip(rng.gamma(2.0, 7.5, n_customers).round(), 0, 90).astype(int)
    nps_pre = np.clip(rng.normal(34 + (contract_type == "24_month") * 3 - days_since_last_app * 0.08, 17, n_customers), -100, 100)
    missing_nps = rng.binomial(1, 0.12, n_customers).astype(bool)
    nps_pre[missing_nps] = np.nan

    assignment = rng.choice(["Control", "Treatment"], size=n_customers, p=[0.5, 0.5])
    treatment = (assignment == "Treatment").astype(int)
    nps_pre_imputed = np.where(np.isnan(nps_pre), np.nanmedian(nps_pre), nps_pre)

    conversion_logit = (
        -3.05
        + 0.011 * pre_roaming_revenue
        + 0.040 * app_sessions_30d
        + 0.34 * summer_traveler
        + 0.10 * (segment == "premium")
        + 0.165 * treatment
    )
    conversion_probability = sigmoid(conversion_logit)
    pack_conversion_14d = rng.binomial(1, conversion_probability, n_customers)
    pack_margin = np.where(pack_conversion_14d == 1, rng.normal(13.8, 3.1, n_customers), 0.0)
    usage_margin = 0.22 * pre_roaming_revenue + rng.normal(5.6, 2.7, n_customers)
    margin_14d = np.clip(usage_margin + pack_margin, 0, None)
    nps_post = np.clip(nps_pre_imputed + rng.normal(0.1, 11.5, n_customers) - 0.07 * treatment, -100, 100)
    support_contact_14d = rng.binomial(1, sigmoid(-3.55 + 0.025 * treatment + 0.015 * days_since_last_app), n_customers)
    app_optout_14d = rng.binomial(1, sigmoid(-4.57 - 0.01 * treatment + 0.006 * days_since_last_app), n_customers)

    crm = pd.DataFrame({
        "customer_id": customer_id,
        "canton": canton,
        "language": language,
        "tenure_months": tenure_months,
        "age": age,
        "contract_type": contract_type,
        "segment": segment,
    })
    billing = pd.DataFrame({
        "customer_id": customer_id,
        "pre_monthly_revenue_chf": pre_monthly_revenue.round(2),
        "pre_roaming_revenue_chf": pre_roaming_revenue.round(2),
        "gross_margin_rate": gross_margin_rate.round(3),
        "summer_traveler": summer_traveler,
    })
    app = pd.DataFrame({
        "customer_id": customer_id,
        "app_sessions_30d": app_sessions_30d,
        "days_since_last_app": days_since_last_app,
        "nps_pre": np.round(nps_pre, 1),
    })
    assignment_table = pd.DataFrame({
        "customer_id": customer_id,
        "assignment_date": "2026-05-01",
        "experiment_group": assignment,
    })
    outcomes = pd.DataFrame({
        "customer_id": customer_id,
        "pack_conversion_14d": pack_conversion_14d,
        "margin_14d_chf": margin_14d.round(2),
        "nps_post": nps_post.round(1),
        "support_contact_14d": support_contact_14d,
        "app_optout_14d": app_optout_14d,
    })
    return crm, billing, app, assignment_table, outcomes


def save_mock_tables(tables: tuple[pd.DataFrame, ...]) -> pd.DataFrame:
    names = ["crm_customers", "billing_preperiod", "app_engagement", "experiment_assignment", "experiment_outcomes"]
    for name, table in zip(names, tables):
        table.to_csv(RAW_DIR / f"{name}.csv", index=False)
    crm, billing, app, assignment_table, outcomes = tables
    analysis = crm.merge(billing, on="customer_id").merge(app, on="customer_id").merge(assignment_table, on="customer_id").merge(outcomes, on="customer_id")
    analysis["is_treatment"] = (analysis["experiment_group"] == "Treatment").astype(int)
    analysis["nps_pre_imputed"] = analysis["nps_pre"].fillna(analysis["nps_pre"].median())
    analysis.to_csv(PROCESSED_DIR / "analysis_table.csv", index=False)
    analysis.sample(250, random_state=20260612).to_csv(DOCS_DIR / "synthetic_sample.csv", index=False)
    return analysis


def two_proportion_test(control_successes: int, control_total: int, treatment_successes: int, treatment_total: int) -> dict[str, float]:
    control_rate = control_successes / control_total
    treatment_rate = treatment_successes / treatment_total
    pooled_rate = (control_successes + treatment_successes) / (control_total + treatment_total)
    standard_error_pooled = math.sqrt(pooled_rate * (1 - pooled_rate) * (1 / control_total + 1 / treatment_total))
    z_stat = (treatment_rate - control_rate) / standard_error_pooled
    p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    standard_error_unpooled = math.sqrt(control_rate * (1 - control_rate) / control_total + treatment_rate * (1 - treatment_rate) / treatment_total)
    lift = treatment_rate - control_rate
    return {
        "control_rate": control_rate,
        "treatment_rate": treatment_rate,
        "lift": lift,
        "relative_lift": lift / control_rate,
        "z_stat": z_stat,
        "p_value": p_value,
        "ci_low": lift - 1.96 * standard_error_unpooled,
        "ci_high": lift + 1.96 * standard_error_unpooled,
        "standard_error": standard_error_unpooled,
    }


def mean_diff_test(data: pd.DataFrame, metric: str) -> dict[str, float]:
    control_values = data.loc[data["experiment_group"] == "Control", metric]
    treatment_values = data.loc[data["experiment_group"] == "Treatment", metric]
    diff = treatment_values.mean() - control_values.mean()
    standard_error = math.sqrt(control_values.var(ddof=1) / len(control_values) + treatment_values.var(ddof=1) / len(treatment_values))
    statistic, p_value = stats.ttest_ind(treatment_values, control_values, equal_var=False)
    return {
        "control": control_values.mean(),
        "treatment": treatment_values.mean(),
        "difference": diff,
        "standard_error": standard_error,
        "ci_low": diff - 1.96 * standard_error,
        "ci_high": diff + 1.96 * standard_error,
        "p_value": p_value,
        "statistic": statistic,
    }


def run_analysis(data: pd.DataFrame) -> dict[str, object]:
    group_summary = data.groupby("experiment_group").agg(
        users=("customer_id", "count"),
        conversions=("pack_conversion_14d", "sum"),
        conversion_rate=("pack_conversion_14d", "mean"),
        margin_per_user_chf=("margin_14d_chf", "mean"),
        pre_roaming_revenue_chf=("pre_roaming_revenue_chf", "mean"),
        nps_post=("nps_post", "mean"),
        support_rate=("support_contact_14d", "mean"),
        optout_rate=("app_optout_14d", "mean"),
    ).reset_index()
    group_summary.to_csv(PROCESSED_DIR / "metric_summary.csv", index=False)
    group_summary.to_csv(DOCS_DIR / "metric_summary.csv", index=False)

    balance_rows = []
    for covariate in ["pre_monthly_revenue_chf", "pre_roaming_revenue_chf", "tenure_months", "app_sessions_30d", "nps_pre_imputed"]:
        control_values = data.loc[data["experiment_group"] == "Control", covariate]
        treatment_values = data.loc[data["experiment_group"] == "Treatment", covariate]
        pooled_std = math.sqrt((control_values.var(ddof=1) + treatment_values.var(ddof=1)) / 2)
        balance_rows.append({
            "covariate": covariate,
            "control_mean": control_values.mean(),
            "treatment_mean": treatment_values.mean(),
            "standardized_mean_diff": (treatment_values.mean() - control_values.mean()) / pooled_std,
        })
    balance = pd.DataFrame(balance_rows)
    balance.to_csv(PROCESSED_DIR / "randomization_balance.csv", index=False)
    balance.to_csv(DOCS_DIR / "randomization_balance.csv", index=False)

    control = group_summary.loc[group_summary["experiment_group"] == "Control"].iloc[0]
    treatment = group_summary.loc[group_summary["experiment_group"] == "Treatment"].iloc[0]
    conversion = two_proportion_test(int(control.conversions), int(control.users), int(treatment.conversions), int(treatment.users))

    margin_standard = mean_diff_test(data, "margin_14d_chf")
    theta = np.cov(data["margin_14d_chf"], data["pre_roaming_revenue_chf"], ddof=1)[0, 1] / np.var(data["pre_roaming_revenue_chf"], ddof=1)
    data = data.copy()
    data["margin_14d_cuped_chf"] = data["margin_14d_chf"] - theta * (data["pre_roaming_revenue_chf"] - data["pre_roaming_revenue_chf"].mean())
    data.to_csv(PROCESSED_DIR / "analysis_table.csv", index=False)
    margin_cuped = mean_diff_test(data, "margin_14d_cuped_chf")
    variance_reduction = 1 - data["margin_14d_cuped_chf"].var(ddof=1) / data["margin_14d_chf"].var(ddof=1)

    guardrails = pd.DataFrame([
        {"metric": "nps_post", **mean_diff_test(data, "nps_post"), "threshold": -1.5},
        {"metric": "support_contact_14d", **mean_diff_test(data, "support_contact_14d"), "threshold": 0.003},
        {"metric": "app_optout_14d", **mean_diff_test(data, "app_optout_14d"), "threshold": 0.002},
    ])
    guardrails["status"] = np.where(
        ((guardrails["metric"] == "nps_post") & (guardrails["difference"] <= guardrails["threshold"]))
        | ((guardrails["metric"] != "nps_post") & (guardrails["difference"] >= guardrails["threshold"])),
        "Stop",
        "Pass",
    )
    guardrails[["metric", "control", "treatment", "difference", "threshold", "p_value", "status"]].to_csv(PROCESSED_DIR / "guardrails.csv", index=False)
    guardrails[["metric", "control", "treatment", "difference", "threshold", "p_value", "status"]].to_csv(DOCS_DIR / "guardrails.csv", index=False)

    alpha = 0.05
    power_target = 0.80
    mde_abs = 0.006
    baseline_rate = conversion["control_rate"]
    n_per_group = ((stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power_target)) ** 2 * 2 * baseline_rate * (1 - baseline_rate)) / (mde_abs ** 2)
    observed_power = stats.norm.cdf(abs(conversion["lift"]) / conversion["standard_error"] - stats.norm.ppf(1 - alpha / 2))
    annual_eligible_customers = 1_350_000
    periods_per_year = 365 / 14
    annualized_margin = margin_cuped["difference"] * annual_eligible_customers * periods_per_year
    annualized_low = margin_cuped["ci_low"] * annual_eligible_customers * periods_per_year
    annualized_high = margin_cuped["ci_high"] * annual_eligible_customers * periods_per_year

    results = {
        "n_customers": int(len(data)),
        "control_users": int(control.users),
        "treatment_users": int(treatment.users),
        "control_conversion_rate": conversion["control_rate"],
        "treatment_conversion_rate": conversion["treatment_rate"],
        "conversion_lift_abs": conversion["lift"],
        "conversion_lift_rel": conversion["relative_lift"],
        "conversion_p_value": conversion["p_value"],
        "conversion_ci_low": conversion["ci_low"],
        "conversion_ci_high": conversion["ci_high"],
        "standard_margin_diff_chf": margin_standard["difference"],
        "standard_margin_ci_low_chf": margin_standard["ci_low"],
        "standard_margin_ci_high_chf": margin_standard["ci_high"],
        "cuped_margin_diff_chf": margin_cuped["difference"],
        "cuped_margin_ci_low_chf": margin_cuped["ci_low"],
        "cuped_margin_ci_high_chf": margin_cuped["ci_high"],
        "cuped_margin_p_value": margin_cuped["p_value"],
        "cuped_variance_reduction": variance_reduction,
        "cuped_theta": theta,
        "required_n_per_group_for_0_6pp_mde": math.ceil(n_per_group),
        "duration_days_at_8500_daily_traffic": math.ceil(2 * n_per_group / 8500),
        "observed_power": observed_power,
        "annualized_rollout_margin_chf": annualized_margin,
        "annualized_rollout_low_chf": annualized_low,
        "annualized_rollout_high_chf": annualized_high,
        "guardrail_status": "Pass" if (guardrails["status"] == "Pass").all() else "Stop",
    }
    with (PROCESSED_DIR / "ab_test_results.json").open("w") as output:
        json.dump(results, output, indent=2)
    with (DOCS_DIR / "ab_test_results.json").open("w") as output:
        json.dump(results, output, indent=2)
    return {"data": data, "group_summary": group_summary, "balance": balance, "guardrails": guardrails, "results": results}


def plot_charts(analysis: dict[str, object]) -> None:
    apply_matplotlib_style()
    group_summary = analysis["group_summary"]
    balance = analysis["balance"]
    guardrails = analysis["guardrails"]
    results = analysis["results"]

    fig, axis = plt.subplots(figsize=(6.5, 4.0))
    rates = group_summary.set_index("experiment_group").loc[["Control", "Treatment"], "conversion_rate"]
    users = group_summary.set_index("experiment_group").loc[["Control", "Treatment"], "users"]
    errors = 1.96 * np.sqrt(rates * (1 - rates) / users)
    axis.bar(rates.index, rates.values * 100, yerr=errors.values * 100, capsize=6,
             color=[group_color("control"), group_color("treatment")])
    axis.set_ylabel("14-day conversion rate (%)")
    axis.set_title("Treatment increases roaming-pack conversion")
    axis.grid(axis="y")
    for index, value in enumerate(rates.values):
        axis.text(index, value * 100 + 0.25, f"{value:.2%}", ha="center", fontweight="bold")
    save_figure(fig, CHART_DIR / "conversion_rate_ci.png")
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(6.5, 4.0))
    labels = ["Standard", "CUPED"]
    lifts = [results["standard_margin_diff_chf"], results["cuped_margin_diff_chf"]]
    lower = [results["standard_margin_diff_chf"] - results["standard_margin_ci_low_chf"], results["cuped_margin_diff_chf"] - results["cuped_margin_ci_low_chf"]]
    upper = [results["standard_margin_ci_high_chf"] - results["standard_margin_diff_chf"], results["cuped_margin_ci_high_chf"] - results["cuped_margin_diff_chf"]]
    axis.errorbar(labels, lifts, yerr=[lower, upper], fmt="o", capsize=7, markersize=8,
                  color=color("orange"), ecolor=color("blue"))
    axis.axhline(0, color=color("slate"), linewidth=1)
    axis.set_ylabel("Margin lift per customer per 14 days (CHF)")
    axis.set_title("CUPED tightens the CHF margin estimate")
    axis.grid(axis="y")
    save_figure(fig, CHART_DIR / "cuped_margin_ci.png")
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(7.2, 4.0))
    guardrail_display = guardrails.copy()
    guardrail_display["label"] = guardrail_display["metric"].map({
        "nps_post": "NPS points",
        "support_contact_14d": "Support rate pp",
        "app_optout_14d": "Opt-out rate pp",
    })
    differences = guardrail_display["difference"].to_numpy().copy()
    differences[1:] = differences[1:] * 100
    thresholds = guardrail_display["threshold"].to_numpy().copy()
    thresholds[1:] = thresholds[1:] * 100
    y_positions = np.arange(len(guardrail_display))
    axis.barh(y_positions, differences, color=[status_color(status) for status in guardrail_display["status"]])
    axis.scatter(thresholds, y_positions, marker="x", s=90, color=color("coral"), label="Stop threshold")
    axis.axvline(0, color=color("slate"), linewidth=1)
    axis.set_yticks(y_positions, guardrail_display["label"])
    axis.set_title("Guardrails stay inside launch thresholds")
    axis.legend(loc="lower right")
    axis.grid(axis="x")
    save_figure(fig, CHART_DIR / "guardrails.png")
    plt.close(fig)

    fig, axis = plt.subplots(figsize=(7.0, 4.0))
    axis.barh(balance["covariate"], balance["standardized_mean_diff"], color=color("cyan"))
    axis.axvline(0.05, color=color("coral"), linestyle="--", linewidth=1.5)
    axis.axvline(-0.05, color=color("coral"), linestyle="--", linewidth=1.5)
    axis.axvline(0, color=color("slate"), linewidth=1)
    axis.set_xlabel("Standardized mean difference")
    axis.set_title("Randomization balance passes the 0.05 SMD rule")
    axis.grid(axis="x")
    save_figure(fig, CHART_DIR / "balance_smd.png")
    plt.close(fig)

    for chart in ["conversion_rate_ci.png", "cuped_margin_ci.png", "guardrails.png", "balance_smd.png"]:
        shutil.copyfile(CHART_DIR / chart, DOCS_DIR / chart)


def pct(value: float, decimals: int = 2) -> str:
    return f"{value * 100:.{decimals}f}%"


def chf_m(value: float) -> str:
    return f"CHF {value / 1_000_000:.1f}M"


def write_deck(results: dict[str, float]) -> None:
    deck = marp_frontmatter(
        title="Sunrise A/B Test on Mock Telco Data",
        description="Synthetic A/B test case study for a personalized roaming-pack prompt",
    )
    deck += f"""<!-- _class: lead -->

# Roll out the personalized roaming prompt to unlock {chf_m(results['annualized_rollout_margin_chf'])} annual margin with no guardrail breach.

- A customer-level randomized A/B test on 60,000 synthetic Sunrise app customers shows a conversion lift of **{results['conversion_lift_abs'] * 100:.2f} pp**.
- CUPED estimates **CHF {results['cuped_margin_diff_chf']:.2f}** incremental margin per eligible customer per 14 days, with a 95% CI of **CHF {results['cuped_margin_ci_low_chf']:.2f} to CHF {results['cuped_margin_ci_high_chf']:.2f}**.
- Recommendation: launch through a monitored 25% ramp, then scale to all eligible app customers if guardrails remain green.

---

# The business request was translated into a randomized revenue-and-experience decision framework.

> <strong>Decision lens:</strong> the prompt ships only if commercial upside and customer experience both improve.

| Design choice | Specification |
|---|---|
| Stakeholder decision | Ship, iterate, or stop a personalized roaming-pack prompt |
| Randomization unit | Customer, assigned 50/50 to control or treatment |
| Target population | Eligible Sunrise mobile-app customers before summer travel |
| Primary metric | 14-day roaming-pack conversion rate |
| Business metric | 14-day gross margin CHF per customer |
| Decision rule | Significant conversion and CHF lift, with all guardrails passing |

---

# CUPED is the right method because pre-period roaming spend explains margin variation without changing randomization.

> <strong>Analytical takeaway:</strong> one headline effect chart is enough here because the precision gain is the key methodological decision.

- Standard conversion test: two-sided difference in proportions at alpha = 5%.
- CHF estimate: Welch mean difference on margin, plus CUPED using pre-period roaming revenue.
- Rigor: customer-level randomization avoids pre/post bias; balance checks reduce sample-selection risk; guardrails prevent revenue-only launch logic.

![CUPED margin confidence intervals](cuped_margin_ci.png)

---

# The treatment creates {chf_m(results['annualized_rollout_margin_chf'])} expected annual margin versus the current app experience.

> <strong>Business takeaway:</strong> even the conservative confidence floor supports rollout economics.

| Scenario | Conversion | Margin lift | Annualized margin |
|---|---:|---:|---:|
| Current app experience | {pct(results['control_conversion_rate'])} | CHF 0.00 | CHF 0.0M |
| Personalized prompt | {pct(results['treatment_conversion_rate'])} | CHF {results['cuped_margin_diff_chf']:.2f} / customer / 14d | {chf_m(results['annualized_rollout_margin_chf'])} |
| Conservative CI floor | +{pct(results['conversion_ci_low'])} | CHF {results['cuped_margin_ci_low_chf']:.2f} / customer / 14d | {chf_m(results['annualized_rollout_low_chf'])} |

![Conversion rate confidence intervals](conversion_rate_ci.png)

---

# A one-week ramp is sufficient to validate production performance before full scale.

> <strong>Operating model:</strong> keep the narrative simple for stakeholders: prove lift, monitor guardrails daily, then scale.

| Launch control | Requirement |
|---|---|
| Power design | {results['required_n_per_group_for_0_6pp_mde']:,} customers per group to detect a 0.6 pp MDE |
| Traffic assumption | 8,500 eligible customers per day |
| Minimum test duration | {results['duration_days_at_8500_daily_traffic']} days for a fully powered confirmatory read |
| Ramp proposal | 25% for one week, 50% for one week, then 100% if guardrails pass |
| Guardrails | NPS, support contacts, and app opt-outs monitored daily |

---

# Customer-experience guardrails stayed green, so the next decision is operational rollout approval.

> <strong>Risk framing:</strong> the launch case holds because the experience metrics remain inside pre-agreed stop limits.

![Guardrail checks](guardrails.png)

- NPS difference stayed inside the -1.5 point stop threshold.
- Support contact and app opt-out differences stayed below their rate thresholds.
- Retain a 5% post-launch holdout for four weeks to measure persistence and seasonality.

---

# Appendix: Randomization balance supports a causal read of the treatment effect.

![Randomization balance standardized mean differences](balance_smd.png)

- All audited pre-treatment covariates are inside the absolute SMD < 0.05 balance rule.
- Balance was checked before outcome analysis to avoid tuning the design after seeing results.
- Synthetic source tables mimic CRM, billing, app engagement, assignment, and outcome systems.

---

# Appendix: CUPED variance reduction increases precision without changing the estimand.

| Diagnostic | Result |
|---|---:|
| CUPED theta | {results['cuped_theta']:.3f} |
| Standard margin lift | CHF {results['standard_margin_diff_chf']:.2f} |
| CUPED margin lift | CHF {results['cuped_margin_diff_chf']:.2f} |
| Variance reduction | {pct(results['cuped_variance_reduction'], 1)} |
| CUPED p-value | {results['cuped_margin_p_value']:.2e} |

- Pre-period roaming revenue is measured before randomization, so it improves precision without absorbing treatment impact.

---

# Appendix: The project artifacts provide a reproducible audit trail for review and rerun.

```mermaid
graph LR
    A[Raw mock source tables] --> B[Joined analysis table]
    B --> C[Balance and missingness checks]
    B --> D[Conversion test]
    B --> E[CUPED margin test]
    B --> F[Guardrail tests]
    C --> G[Notebook audit trail]
    D --> H[Executive deck]
    E --> H
    F --> H
```

- Notebook: `notebooks/ab-test-mock-data.ipynb`
- Source and processed artifacts: `notebooks/ab-test-mock-data/`
- Stakeholder deck: `docs/ab-test-mock-data/deck.md`
"""
    (DOCS_DIR / "deck.md").write_text(deck)


def markdown_cell(source: str, cell_id: str) -> dict[str, object]:
    return {
        "cell_type": "markdown",
        "metadata": {"language": "markdown", "id": cell_id},
        "source": source.splitlines(keepends=True),
    }


def code_cell(source: str, cell_id: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"language": "python", "id": cell_id},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def write_notebook(results: dict[str, float]) -> None:
    cells = [
    markdown_cell("""# Sunrise A/B Test on Mock Telco Data

## Business Case: What and Why

Sunrise wants to decide whether a personalized roaming-pack prompt should replace the current app experience for eligible mobile-app customers before peak travel. The decision rule is launch only if the treatment improves 14-day pack conversion and CHF margin while NPS, support contacts, and app opt-outs stay inside pre-defined guardrails.

This notebook is the audit trail for the stakeholder deck in `docs/ab-test-mock-data/deck.md`. The data is synthetic and generated to mimic source-like CRM, billing, app, assignment, and outcome tables.

**Notebook improvements:**
- Inline diagnostic and business charts
- Explicit statistical formulas in LaTeX
- Palette/style audit to confirm Sunrise colors are used in figures
- Short slide-ready takeaways after each major analytical block""", "abtest-01"),
    code_cell("""from pathlib import Path
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

ROOT = Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from sunrise_style import apply_matplotlib_style, color, group_color, status_color, SUNRISE_COLORS

apply_matplotlib_style()

SLUG = "ab-test-mock-data"
RAW = ROOT / "notebooks" / SLUG / "raw"
PROCESSED = ROOT / "notebooks" / SLUG / "processed"
CHARTS = ROOT / "notebooks" / SLUG / "charts"

with (PROCESSED / "ab_test_results.json").open() as handle:
    results = json.load(handle)
results""", "abtest-01-code"),
    markdown_cell("""## EDA: Data Sources, Table Structure, and Wrangling

The mock data uses source-like tables rather than a single flat extract. NPS has explicit missingness and is median-imputed for balance checks and CUPED diagnostics. Outcomes are measured after assignment; pre-period revenue, tenure, app sessions, and NPS are measured before randomization, so they are valid for balance and CUPED.

```mermaid
graph LR
    A[CRM customers: one row per customer] --> F[Joined analysis table]
    B[Billing pre-period: revenue and roaming] --> F
    C[App engagement: sessions and NPS] --> F
    D[Experiment assignment: randomized group] --> F
    E[Experiment outcomes: conversion, margin, guardrails] --> F
    F --> G[Processed summaries and diagnostics]
    G --> H[Charts]
    G --> I[Stakeholder deck]
```
""", "abtest-02"),
        code_cell("""tables = {
    "crm": pd.read_csv(RAW / "crm_customers.csv"),
    "billing": pd.read_csv(RAW / "billing_preperiod.csv"),
    "app": pd.read_csv(RAW / "app_engagement.csv"),
    "assignment": pd.read_csv(RAW / "experiment_assignment.csv"),
    "outcomes": pd.read_csv(RAW / "experiment_outcomes.csv"),
}

schema_summary = pd.DataFrame([
    {"table": name, "rows": len(table), "columns": table.shape[1], "grain": "customer_id"}
    for name, table in tables.items()
])
schema_summary""", "abtest-02-code-a"),
    code_cell("""analysis = pd.read_csv(PROCESSED / "analysis_table.csv")
missingness = analysis.isna().mean().sort_values(ascending=False).head(8).rename("missing_rate")
metric_summary = pd.read_csv(PROCESSED / "metric_summary.csv")
balance = pd.read_csv(PROCESSED / "randomization_balance.csv")

display(missingness)
display(metric_summary)
display(balance)""", "abtest-02-code-b"),
    code_cell("""fig, ax = plt.subplots(figsize=(8, 3.5))
missingness.plot(kind="bar", color=color("cyan"), ax=ax)
ax.set_title("Top missingness columns in analysis table")
ax.set_ylabel("Missing share")
ax.set_ylim(0, max(0.14, missingness.max() * 1.2))
ax.grid(axis="y")
plt.show()""", "abtest-03"),
    markdown_cell(r"""## Selected Methodology: Theory and Assumptions

The experiment estimates the intent-to-treat impact of showing the prompt. The primary conversion test uses a two-proportion z-test. CHF impact uses a difference in mean 14-day margin per customer and CUPED adjustment:

$$Y_i^{CUPED} = Y_i - \theta(X_i - \bar{X})$$

The conversion test uses:

$$z = \frac{\hat{p}_T - \hat{p}_C}{\sqrt{\hat{p}(1-\hat{p})(1/n_T + 1/n_C)}}$$

and for planning duration we use the standard approximation:

$$n \approx \frac{\left(z_{1-\alpha/2} + z_{\text{power}}\right)^2\cdot 2\cdot p_0(1-p_0)}{\text{MDE}^2}$$

where `Y` is post-treatment 14-day margin and `X` is pre-treatment roaming revenue. Because `X` is measured before randomization, CUPED improves precision without changing the causal estimand.

```mermaid
graph LR
    A[Eligible app customers] --> B{Random assignment}
    B --> C[Control: current app]
    B --> D[Treatment: personalized prompt]
    E[Pre-period roaming revenue] --> F[CUPED adjustment]
    C --> G[Conversion and margin outcomes]
    D --> G
    G --> H[Primary conversion test]
    G --> F
    G --> I[Guardrail tests]
    H --> J[Launch decision]
    F --> J
    I --> J
```
""", "abtest-04"),
        code_cell("""control = metric_summary.loc[metric_summary.experiment_group == "Control"].iloc[0]
treatment = metric_summary.loc[metric_summary.experiment_group == "Treatment"].iloc[0]

conversion_readout = pd.DataFrame([{
    "control_rate": results["control_conversion_rate"],
    "treatment_rate": results["treatment_conversion_rate"],
    "absolute_lift_pp": 100 * results["conversion_lift_abs"],
    "relative_lift_pct": 100 * results["conversion_lift_rel"],
    "p_value": results["conversion_p_value"],
    "ci_low_pp": 100 * results["conversion_ci_low"],
    "ci_high_pp": 100 * results["conversion_ci_high"],
}])
conversion_readout""", "abtest-05"),
        code_cell("""plot_df = metric_summary.copy()
plot_df["rate_pct"] = 100 * plot_df["conversion_rate"]
plot_df = plot_df.set_index("experiment_group").loc[["Control", "Treatment"]].reset_index()
errors = 1.96 * np.sqrt(
    (plot_df["conversion_rate"] * (1 - plot_df["conversion_rate"])) / plot_df["users"]
)

fig, ax = plt.subplots(figsize=(7.5, 4.2))
ax.bar(
    plot_df["experiment_group"],
    plot_df["rate_pct"],
    yerr=100 * errors,
    capsize=6,
    color=[group_color("control"), group_color("treatment")],
)
ax.set_title("14-day conversion with 95% confidence intervals")
ax.set_ylabel("Conversion rate (%)")
ax.grid(axis="y")
for idx, row in plot_df.iterrows():
    ax.text(idx, row["rate_pct"] + 0.15, f"{row['rate_pct']:.2f}%", ha="center", fontweight="bold")
plt.show()""", "abtest-06"),
    markdown_cell("""**Chart snapshot (saved artifact):**

![Conversion confidence intervals](ab-test-mock-data/charts/conversion_rate_ci.png)
""", "abtest-06-img"),
        markdown_cell(f"""### Slide-ready takeaway

    The treatment improves 14-day conversion by **{results['conversion_lift_abs'] * 100:.2f} pp** with the full 95% confidence interval above the minimum commercially relevant range, which supports keeping conversion as the headline KPI in the deck.
    """, "abtest-06-takeaway"),
        markdown_cell("""## Calculation: Tests, Models, Charts, and CHF Impact

The calculation translates the experimental effect into a rollout case using 1.35M annual eligible app customers and repeated 14-day commercial windows. This keeps the unit economics transparent: margin lift per customer per 14 days times eligible reach times periods per year.""", "abtest-06-md"),
        code_cell("""margin_readout = pd.DataFrame([{
    "standard_margin_lift_chf": results["standard_margin_diff_chf"],
    "cuped_margin_lift_chf": results["cuped_margin_diff_chf"],
    "cuped_ci_low_chf": results["cuped_margin_ci_low_chf"],
    "cuped_ci_high_chf": results["cuped_margin_ci_high_chf"],
    "cuped_variance_reduction_pct": 100 * results["cuped_variance_reduction"],
    "annualized_margin_chf": results["annualized_rollout_margin_chf"],
    "annualized_low_chf": results["annualized_rollout_low_chf"],
    "annualized_high_chf": results["annualized_rollout_high_chf"],
}])
margin_readout""", "abtest-07"),
        code_cell("""fig, ax = plt.subplots(figsize=(7.2, 4.0))
ax.errorbar(
    ["Standard", "CUPED"],
    [results["standard_margin_diff_chf"], results["cuped_margin_diff_chf"]],
    yerr=[
        [
            results["standard_margin_diff_chf"] - results["standard_margin_ci_low_chf"],
            results["cuped_margin_diff_chf"] - results["cuped_margin_ci_low_chf"],
        ],
        [
            results["standard_margin_ci_high_chf"] - results["standard_margin_diff_chf"],
            results["cuped_margin_ci_high_chf"] - results["cuped_margin_diff_chf"],
        ],
    ],
    fmt="o",
    capsize=8,
    color=color("orange"),
    ecolor=color("blue"),
)
ax.axhline(0, color=color("slate"), linewidth=1)
ax.set_title("CUPED narrows uncertainty around the CHF margin lift")
ax.set_ylabel("Margin lift per customer (CHF, 14-day)")
ax.grid(axis="y")
plt.show()""", "abtest-08"),
    markdown_cell("""**Chart snapshot (saved artifact):**

![CUPED margin intervals](ab-test-mock-data/charts/cuped_margin_ci.png)
""", "abtest-08-img"),
        markdown_cell(f"""### Slide-ready takeaway

    CUPED reduces variance by **{results['cuped_variance_reduction'] * 100:.1f}%**, so the margin story can be shown as one clean effect-size chart instead of a longer technical appendix on model precision.
    """, "abtest-08-takeaway"),
        code_cell("""guardrails = pd.read_csv(PROCESSED / "guardrails.csv")
power = pd.DataFrame([{
    "mde_pp": 0.6,
    "required_n_per_group": results["required_n_per_group_for_0_6pp_mde"],
    "duration_days_at_8500_daily_traffic": results["duration_days_at_8500_daily_traffic"],
    "observed_power": results["observed_power"],
}])

display(guardrails)
display(power)""", "abtest-09"),
        code_cell("""guardrail_plot = guardrails.copy()
guardrail_plot["label"] = guardrail_plot["metric"].map(
    {
        "nps_post": "NPS points",
        "support_contact_14d": "Support contacts (pp)",
        "app_optout_14d": "App opt-out (pp)",
    }
)
display_values = guardrail_plot["difference"].to_numpy().copy()
display_values[1:] = 100 * display_values[1:]
threshold_values = guardrail_plot["threshold"].to_numpy().copy()
threshold_values[1:] = 100 * threshold_values[1:]

fig, ax = plt.subplots(figsize=(8, 3.8))
ax.barh(
    guardrail_plot["label"],
    display_values,
    color=[status_color(status) for status in guardrail_plot["status"]],
)
ax.scatter(threshold_values, guardrail_plot["label"], marker="x", s=110, color=color("coral"), label="Stop threshold")
ax.axvline(0, color=color("slate"), linewidth=1)
ax.set_title("Guardrails remain below stop thresholds")
ax.grid(axis="x")
ax.legend(loc="lower right")
plt.show()""", "abtest-10"),
    markdown_cell("""**Chart snapshot (saved artifact):**

![Guardrail status](ab-test-mock-data/charts/guardrails.png)
""", "abtest-10-img"),
        markdown_cell("""### Slide-ready takeaway

    The rollout case remains decision-ready because guardrails are interpreted visually against explicit stop thresholds rather than buried in a detailed table.
    """, "abtest-10-takeaway"),
        code_cell("""# Sunrise palette audit: confirm charts are using shared project colors.
palette_check = pd.Series({
    "control": group_color("control"),
    "treatment": group_color("treatment"),
    "accent_orange": color("orange"),
    "accent_blue": color("blue"),
    "status_pass": status_color("Pass"),
})
display(palette_check)

fig, ax = plt.subplots(figsize=(8, 1.8))
for i, (name, hex_color) in enumerate(palette_check.items()):
    ax.barh([0], [1], left=i, height=0.55, color=hex_color)
    ax.text(i + 0.5, 0, f"{name}: {hex_color}", ha="center", va="center", fontsize=9, color="#0B1F2A")
ax.set_xlim(0, len(palette_check))
ax.set_yticks([])
ax.set_xticks([])
ax.set_title("Palette check against sunrise_style tokens")
for spine in ax.spines.values():
    spine.set_visible(False)
plt.show()""", "abtest-11"),
        markdown_cell(f"""## Results: Conclusion and Recommendation

The treatment wins on the primary metric and clears the business case. Conversion increases by **{results['conversion_lift_abs'] * 100:.2f} pp**, CUPED-adjusted margin increases by **CHF {results['cuped_margin_diff_chf']:.2f} per customer per 14 days**, and the annualized rollout case is **{chf_m(results['annualized_rollout_margin_chf'])}** with a conservative confidence floor of **{chf_m(results['annualized_rollout_low_chf'])}**.

Recommendation: approve a controlled rollout to 25% of eligible app customers for one week, scale to 50% for one more week, then launch to 100% if NPS, support contacts, and app opt-outs remain green. Keep a 5% post-launch holdout for four weeks to validate persistence and monitor travel-season effects.

Limitations: the data is synthetic, the impact assumes the 14-day margin lift persists across annual travel cycles, and interference between household members is not modeled. A real production test should preregister the metric definitions and freeze the analysis before launch.""", "abtest-12"),
    ]
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=2))


def main() -> None:
    ensure_dirs()
    tables = generate_mock_tables()
    analysis_table = save_mock_tables(tables)
    analysis = run_analysis(analysis_table)
    plot_charts(analysis)
    write_deck(analysis["results"])
    write_notebook(analysis["results"])
    print(json.dumps(analysis["results"], indent=2))


if __name__ == "__main__":
    main()