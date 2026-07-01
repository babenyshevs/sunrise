# Nora Bearth — Publications Analysis

Analysis of the papers in [`publications/`](publications/). She publishes as **Nora Bearth** (Swiss Institute for Empirical Economic Research, SEW-HSG, University of St. Gallen; nora.bearth@unisg.ch). Analysis is based on titles, abstracts, and introductions.

> **Scope:** deep analysis covers only papers where she is **first author** (3 of them). Co-authored papers where she is not first author are listed at the end for completeness.

## Authorship map

| Paper | Authors (order) | Her position |
|---|---|---|
| Beyond Baby Blues | **Bearth** (sole) | ✅ First (sole) |
| Causal ML for Moderation Effects | **Bearth**, Lechner | ✅ First |
| Fairness-Aware & Interpretable Policy Learning | **Bearth**, Lechner, Mareckova, Muny | ✅ First |
| From Average Effects to Targeted Assignment | Mascolo, **Bearth**, Muny, Lechner, Mareckova | 2nd |
| Improving Finite-Sample ATE (PS Calibration) — *J. Applied Econometrics 2026* | Ballinari, **Bearth** | 2nd |
| Calibrating doubly-robust estimators | Ballinari (sole) | Acknowledged only |

Recurring collaborators: **Michael Lechner** (her likely PhD supervisor — a leading causal-ML econometrician, SEW-HSG), Jana Mareckova, Fabian Muny, Federica Mascolo (St. Gallen group), and **Daniele Ballinari** (Swiss National Bank; shares the "Ballinari" name — possibly related, inferred).

---

## First-author papers (deep analysis)

### 1. Beyond Baby Blues: The Child Penalty in Mental Health in Switzerland
*Sole author · arXiv 2024/2025 · JEL J13, J16, I10*

- **Question:** What is the causal effect of having a first child on women's mental health in Switzerland?
- **Method:** Staggered **difference-in-differences** on anonymized health-insurance **prescription data** (antidepressant prescriptions as the mental-health proxy). This is a design-based causal-inference approach on **observational administrative data** — no RCT.
- **Findings:** A substantial and *growing* "child penalty": ~+1 p.p. antidepressant prescriptions ~4 years post-birth (+50% vs. pre-birth), rising to +1.7 p.p. (+75%) by 6 years. Larger for employed women — points to life-circumstance/time-constraint mechanisms, not just biology.
- **Signals about her:** Can independently run an end-to-end empirical causal study — sourcing sensitive real-world data (negotiated access with insurers CSS & Swica), design, execution, interpretation. Strong applied-economics and communication chops, not just methods.

### 2. Causal Machine Learning for Moderation Effects
*Bearth & Lechner · arXiv 2025 · JEL C14, C21*

- **Question:** How do you *interpret* why a treatment effect differs between groups, rather than just measuring that it does?
- **Contribution:** Introduces a new estimand, the **Balanced Group Average Treatment Effect (BGATE)** — a GATE holding a chosen covariate distribution fixed — so the difference between two groups can be decomposed into "due to the variable of interest" vs. "due to other covariates." Estimator built on **double/debiased machine learning (DML)**, proven √N-consistent and asymptotically normal; also offers automatic debiased ML and a reweighting estimator.
- **Signals about her:** Genuine **methods-development** capability — proposing a new parameter with formal asymptotic theory plus simulations and an empirical application. Publishable-grade theoretical econometrics.

### 3. Fairness-Aware and Interpretable Policy Learning
*Bearth, Lechner, Mareckova, Muny · Sep 2025 · JEL C14, C21*

- **Question:** How do you build algorithmic decision policies that are both **fair** (w.r.t. sensitive attributes like gender/race) and **interpretable**, without much loss of performance?
- **Contribution:** A framework combining **data pre-processing** (removing dependencies between sensitive attributes and decision features) with **policy trees** (interpretable policy functions), then mapping tree parameters back to the original feature space. Yields policies pairwise-independent of sensitive attributes while staying interpretable. Applied to Swiss **active labor market program (ALMP)** assignment; finds fairness can be improved at relatively low cost in expected employment outcomes.
- **Signals about her:** Works exactly at the intersection of **optimal policy learning + responsible/fair AI + interpretability** — i.e. how to *assign* interventions to people, fairly and transparently.

---

## Why this matters for Sunrise (the "so what")

Her research is startlingly well-matched to a telecom decision-support team:

- **Heterogeneous treatment effects & policy learning = uplift/targeting.** GATE/BGATE and optimal policy trees are the academic backbone of **who to target with which offer/retention action** — the same problem as uplift modeling for CRM, churn, and marketing. She has the theory that Stan and Vincie apply operationally.
- **Causal inference *without* RCTs.** DiD, DML, propensity-score methods on observational admin data map directly onto the round-1 project type *"experiment with no RCT."* This is her home turf.
- **Fairness / interpretability = AI governance.** Directly supports the AI-governance and "constructive challenge / rigorous evidence" parts of the Head-of-DS mandate.
- **A published J. of Applied Econometrics (2026) paper** (as 2nd author) — top field journal; signals real research quality on the team.

**Coaching implication:** her gap is not rigor — it's business translation and pace. The highest-value move is pointing her deep policy-learning/uplift expertise at concrete Sunrise decisions (retention targeting, offer assignment) — where she could quickly become the methods anchor and lift the whole team's causal-inference bar.

---

## Co-authored papers (not first author — brief)

- **From Average Effects to Targeted Assignment** (Mascolo, **Bearth**, Muny, Lechner, Mareckova, 2025): Causal ML (Modified Causal Forest) evaluation of Swiss ALMPs on 2004–2018 admin data; finds small positive effects of Temporary Wage Subsidies, negative effects of Basic Courses, and uses shallow policy trees for targeting guidance. Same targeting/policy theme.
- **Improving the Finite-Sample Estimation of ATE using DML with Propensity-Score Calibration** (Ballinari, **Bearth**, 2025; *J. of Applied Econometrics 2026*): Calibrating propensity scores reduces RMSE of DML ATE estimates in finite samples without harming asymptotics. Practical DML robustness.
- **Calibrating doubly-robust estimators with unbalanced treatment assignment** (Ballinari, sole author, 2024): She is only acknowledged, not an author — undersampling-based calibration for DML under rare treatment. Included in the folder but **not her paper**.
