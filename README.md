# Sunrise Data Science Research Skills

This repository is a mock data science research workspace for turning business questions into analytical evidence and stakeholder-ready recommendations.

The core purpose is to support high-value decisions through analytics, experimentation, impact measurement, causal inference, and optimization. Each case skill demonstrates the full path from stakeholder prompt to mathematical framing, mock data generation, analysis scripts, CHF impact calculation, and presentation output.

## How A New Agent Should Operate This Repo

Start here, then use the skill docs.

1. Read [.github/skills/README.md](.github/skills/README.md) to identify the right workflow.
2. Always load [.github/skills/data-preprocessing/SKILL.md](.github/skills/data-preprocessing/SKILL.md) first when mock or cleaned telco data is needed.
3. Load the analytical skill matching the business question.
4. Run or adapt the scripts inside that skill folder.
5. Load [.github/skills/presentation-deck/SKILL.md](.github/skills/presentation-deck/SKILL.md) last to generate a Marp + Mermaid.js stakeholder deck.
6. Leave durable artifacts under `notebooks/` and `docs/` when conducting a new research task.

The intended flow is:

```text
business question
  -> analytical framing
  -> mock/clean data
  -> rigorous method
  -> validation and CHF impact
  -> executive recommendation deck
```

## Repository Structure

```text
sunrise/
├── .github/skills/
│   ├── README.md                         # Skill index and agent output contract
│   ├── data-preprocessing/
│   │   ├── SKILL.md                      # When/how to create and clean telco data
│   │   └── telco_preprocessing.py        # Mock data, missing values, encoding, features
│   ├── uplift-modeling/
│   │   ├── SKILL.md                      # Retention targeting via causal uplift
│   │   ├── uplift_churn_model.py         # T/X/S learners using causalml/sklift patterns
│   │   ├── metrics_and_plots.py          # Qini curve and uplift decile charts
│   │   └── pnl_calculator.py             # CHF ROI and optimal targeting size
│   ├── causal-impact/
│   │   ├── SKILL.md                      # Campaign evaluation without control group
│   │   ├── synthetic_control.py          # Counterfactual time-series analysis
│   │   └── dowhy_analysis.py             # Causal graph/refutation alternative
│   ├── ab-test-design/
│   │   ├── SKILL.md                      # Power, duration, CUPED, guardrails
│   │   ├── power_analysis.py             # Sample size and experiment blueprint
│   │   └── cuped_variance_reduction.py   # CUPED and guardrail checks
│   ├── channel-optimization/
│   │   ├── SKILL.md                      # Next-best-action/channel allocation
│   │   └── channel_optimization.py       # Propensity + constrained optimization
│   └── presentation-deck/
│       ├── SKILL.md                      # Marp/Mermaid deck generation instructions
│       └── generate_deck.py              # Code-generated case decks
├── requirements.txt                      # Python analytical dependencies
├── .gitignore                            # Ignores generated charts/decks/cache files
└── README.md                             # This operator guide
```

## Skills At A Glance

| Skill | Use When | Main Output |
|-------|----------|-------------|
| `data-preprocessing` | Generate mock telco data or clean raw customer data | Modeling-ready customer dataset |
| `uplift-modeling` | Decide which customers should receive retention treatment | Uplift ranking, Qini/decile charts, CHF P&L |
| `causal-impact` | Evaluate a campaign/intervention without a control group | Actual vs counterfactual chart, incremental revenue |
| `ab-test-design` | Plan/analyze experiments, rollouts, defaults, pricing tests | Sample size, duration, CUPED result, guardrails |
| `channel-optimization` | Allocate SMS/email/calls under capacity or budget constraints | Optimal channel allocation and ROI comparison |
| `presentation-deck` | Turn analysis into stakeholder communication | Marp Markdown deck with Mermaid diagrams |

## Environment Setup

Use `python3` on macOS.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The requirements install the local `sunrise_style` package in editable mode. Use it for every notebook, plotting script, and generated deck so charts and presentations stay close to the visual language in [sunrise_sample_presentation.pdf](sunrise_sample_presentation.pdf): warm Sunrise orange/coral, cyan/blue accents, clean Avenir Next or Source Sans style typography, light gridlines, and consistent Marp table spacing.

```python
from sunrise_style import apply_matplotlib_style, color, group_color, save_figure

apply_matplotlib_style()
# use color("orange"), group_color("treatment"), and save_figure(fig, path)
```

For Marp decks generated from Python, use:

```python
from sunrise_style import marp_frontmatter

deck = marp_frontmatter(title="Sunrise Case Study") + "# Executive Recommendation\n"
```

The presentation generator itself has no Python package dependency. Exporting Marp decks requires Marp CLI:

```bash
npm install -g @marp-team/marp-cli
```

## Running Existing Skill Scripts

Run scripts from inside their skill folder so relative outputs land next to the skill.

```bash
# Data foundation
cd .github/skills/data-preprocessing
python3 telco_preprocessing.py

# Case 1: retention uplift
cd ../uplift-modeling
python3 uplift_churn_model.py
python3 metrics_and_plots.py
python3 pnl_calculator.py

# Case 2: campaign impact without control group
cd ../causal-impact
python3 synthetic_control.py
python3 dowhy_analysis.py

# Case 3: experiment design and CUPED
cd ../ab-test-design
python3 power_analysis.py
python3 cuped_variance_reduction.py

# Case 4: channel optimization
cd ../channel-optimization
python3 channel_optimization.py

# Presentation decks
cd ../presentation-deck
python3 generate_deck.py              # all decks
python3 generate_deck.py uplift       # one deck only
```

Generated charts and generated `deck_*.md` files are ignored by git. Regenerate them from the scripts when needed.

## Conducting A New Research Case

For a new task, create durable, reviewable artifacts:

```text
docs/<research-slug>/deck.md           # Final Marp presentation
docs/<research-slug>/*.pdf|*.html      # Optional exports
notebooks/<research-slug>.ipynb        # Reproducible analysis audit trail
notebooks/<research-slug>/raw/         # Source-like mock/raw data
notebooks/<research-slug>/processed/   # Processed data/model outputs
notebooks/<research-slug>/charts/      # Figures consumed by the deck
```

The notebook should explain:

1. Business case and decision to support
2. EDA and data wrangling
3. Selected methodology and why simpler approaches fail
4. Calculation, validation, and sensitivity checks
5. Results, CHF impact, assumptions, and recommendation

Include Mermaid diagrams for the data flow and methodology/design when useful.

## Decision-Support Principles

- Translate every business prompt into a clear analytical problem.
- Name the naive trap before presenting the advanced method.
- Prefer causal or experimental evidence over correlation when decisions require impact claims.
- Convert model outputs into CHF, ROI, cost, risk, and operational constraints.
- Use guardrails for customer harm, not only primary revenue metrics.
- End with a concrete recommendation: go, no-go, scale, retest, or investigate.

## Verification Checklist

Before handing off a research result:

- The selected `SKILL.md` was followed and any assumptions are documented.
- Charts and decks use the shared `sunrise_style` package rather than local hard-coded palettes.
- Scripts or notebooks run in the active environment, or missing dependencies are explicitly noted.
- Outputs include at least one business-facing artifact: P&L, counterfactual impact, experiment blueprint, or allocation recommendation.
- The deck matches the evidence and does not claim more certainty than the analysis supports.
- Generated artifacts are either saved under `docs/` / `notebooks/` or intentionally ignored as reproducible outputs.
