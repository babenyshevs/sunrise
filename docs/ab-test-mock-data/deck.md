---
marp: true
title: Sunrise A/B Test on Mock Telco Data
description: Synthetic A/B test case study for a personalized roaming-pack prompt
paginate: true
theme: default
header: "Sunrise Data Science & Analytics"
footer: "Stanislav Babenyshev | Case Study Interview"
style: |
  :root {
    --sunrise-orange: #FF5A1F;
    --sunrise-coral: #E84E3C;
    --sunrise-cyan: #72C7E7;
    --sunrise-blue: #147FB8;
    --sunrise-navy: #0B1F2A;
    --sunrise-charcoal: #232A2F;
    --sunrise-slate: #52616B;
    --sunrise-grid: #D7DEE2;
    --sunrise-paper: #F7F8F8;
  }

  section {
    width: 1280px;
    height: 720px;
    padding: 52px 64px 44px;
    background:
      linear-gradient(180deg, #ffffff 0%, #fbfbfa 100%);
    color: var(--sunrise-charcoal);
    font-family: "Avenir Next", "Source Sans 3", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 23px;
    line-height: 1.36;
    letter-spacing: 0;
  }

  section::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at top right, rgba(114,199,231,0.12), transparent 28%),
      linear-gradient(90deg, rgba(247,248,248,0.6), rgba(247,248,248,0));
    pointer-events: none;
  }

  section::after {
    color: var(--sunrise-slate);
    font-size: 12px;
    right: 28px;
    bottom: 18px;
  }

  h1 {
    color: var(--sunrise-navy);
    font-size: 44px;
    line-height: 1.06;
    margin: 0 0 18px;
    font-weight: 700;
    max-width: 1020px;
  }

  h2 {
    color: var(--sunrise-navy);
    font-size: 28px;
    line-height: 1.16;
    margin: 0 0 12px;
    font-weight: 700;
  }

  h3 {
    color: var(--sunrise-charcoal);
    font-size: 22px;
    margin: 16px 0 8px;
  }

  p, li {
    line-height: 1.34;
  }

  ul {
    padding-left: 1.1em;
  }

  li {
    margin: 0.16em 0;
  }

  strong {
    color: var(--sunrise-navy);
  }

  blockquote {
    margin: 14px 0 18px;
    padding: 14px 18px;
    border-left: 4px solid var(--sunrise-orange);
    background: rgba(247,248,248,0.96);
    border-radius: 0 14px 14px 0;
    color: var(--sunrise-charcoal);
    font-size: 22px;
  }

  blockquote strong {
    color: var(--sunrise-orange);
  }

  a {
    color: var(--sunrise-blue);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 18px;
    margin-top: 12px;
    box-shadow: 0 10px 24px rgba(11,31,42,0.05);
    border-radius: 12px;
    overflow: hidden;
  }

  th {
    background: var(--sunrise-navy);
    color: #fff;
    font-weight: 700;
  }

  th, td {
    border: 1px solid var(--sunrise-grid);
    padding: 7px 10px;
  }

  tr:nth-child(even) td {
    background: var(--sunrise-paper);
  }

  img {
    max-height: 390px;
    object-fit: contain;
    border-radius: 16px;
    box-shadow: 0 18px 36px rgba(11,31,42,0.10);
    background: #fff;
    padding: 6px;
  }

  header, footer {
    color: var(--sunrise-slate);
    font-size: 13px;
  }

  mermaid {
    text-align: center;
  }

  code {
    font-family: "SF Mono", "Menlo", "Consolas", monospace;
    font-size: 0.86em;
    background: rgba(247,248,248,0.95);
    padding: 0.08em 0.28em;
    border-radius: 6px;
  }

  pre code {
    display: block;
    padding: 14px 16px;
    line-height: 1.38;
  }

  section.compact p,
  section.compact li,
  section.compact table {
    font-size: 20px;
  }

  .insight {
    color: var(--sunrise-orange);
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    margin-bottom: 10px;
  }

  section.lead {
    background: linear-gradient(112deg, rgba(11,31,42,0.94), rgba(214,65,22,0.78));
    color: #fff;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  section.lead h1,
  section.lead h2,
  section.lead strong,
  section.lead footer,
  section.lead header {
    color: #fff;
  }

  section.lead table,
  section.lead td {
    color: var(--sunrise-charcoal);
  }

  section.lead th {
    color: #fff;
  }

  section.lead::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
      repeating-radial-gradient(ellipse at 78% 35%, rgba(255,255,255,0.42) 0 1px, transparent 1px 12px);
    opacity: 0.5;
    pointer-events: none;
  }
---
<!-- _class: lead -->

# Roll out the personalized roaming prompt to unlock CHF 4.7M annual margin with no guardrail breach.

- A customer-level randomized A/B test on 60,000 synthetic Sunrise app customers shows a conversion lift of **1.10 pp**.
- CUPED estimates **CHF 0.13** incremental margin per eligible customer per 14 days, with a 95% CI of **CHF 0.06 to CHF 0.21**.
- Recommendation: launch through a monitored 25% ramp, then scale to all eligible app customers if guardrails remain green.

---

# The business request was translated into a randomized revenue-and-experience decision framework.

> **Decision lens:** the prompt ships only if commercial upside and customer experience both improve.

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

> **Analytical takeaway:** one headline effect chart is enough here because the precision gain is the key methodological decision.

- Standard conversion test: two-sided difference in proportions at alpha = 5%.
- CHF estimate: Welch mean difference on margin, plus CUPED using pre-period roaming revenue.
- Rigor: customer-level randomization avoids pre/post bias; balance checks reduce sample-selection risk; guardrails prevent revenue-only launch logic.

![CUPED margin confidence intervals](cuped_margin_ci.png)

---

# The treatment creates CHF 4.7M expected annual margin versus the current app experience.

> **Business takeaway:** even the conservative confidence floor supports rollout economics.

| Scenario | Conversion | Margin lift | Annualized margin |
|---|---:|---:|---:|
| Current app experience | 7.61% | CHF 0.00 | CHF 0.0M |
| Personalized prompt | 8.71% | CHF 0.13 / customer / 14d | CHF 4.7M |
| Conservative CI floor | +0.66% | CHF 0.06 / customer / 14d | CHF 2.0M |

![Conversion rate confidence intervals](conversion_rate_ci.png)

---

# A one-week ramp is sufficient to validate production performance before full scale.

> **Operating model:** keep the narrative simple for stakeholders: prove lift, monitor guardrails daily, then scale.

| Launch control | Requirement |
|---|---|
| Power design | 30,655 customers per group to detect a 0.6 pp MDE |
| Traffic assumption | 8,500 eligible customers per day |
| Minimum test duration | 8 days for a fully powered confirmatory read |
| Ramp proposal | 25% for one week, 50% for one week, then 100% if guardrails pass |
| Guardrails | NPS, support contacts, and app opt-outs monitored daily |

---

# Customer-experience guardrails stayed green, so the next decision is operational rollout approval.

> **Risk framing:** the launch case holds because the experience metrics remain inside pre-agreed stop limits.

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
| CUPED theta | 0.245 |
| Standard margin lift | CHF 0.16 |
| CUPED margin lift | CHF 0.13 |
| Variance reduction | 25.2% |
| CUPED p-value | 5.85e-04 |

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
