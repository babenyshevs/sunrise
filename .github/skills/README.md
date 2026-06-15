# Skills Index

Each subfolder is a self-contained skill: a `SKILL.md` (with frontmatter) explaining when and how to use it, plus the runnable scripts.

## End-to-End Research Workflow

For a complete data science research task, the `make-research` agent uses the skills in this order:

1. `data-preprocessing/` — always use first to create, inspect, clean, and feature-engineer the data foundation.
2. One or more analytical skills — choose `uplift-modeling/`, `causal-impact/`, `ab-test-design/`, or `channel-optimization/` when the research question matches the skill trigger.
3. `presentation-deck/` — always use last to generate a stakeholder-ready Marp deck that translates the evidence into an executive recommendation.

The repo is designed to move from business question → analytical framing → rigorous evidence → stakeholder decision.

## Agent Output Contract

Every research task must leave durable, reviewable artifacts in the repository:

- Presentation deck: create a separate folder under `docs/`, for example `docs/<research-slug>/`, and place the final Marp deck there as `deck.md`. Put exported PDF/HTML/PPTX files and deck images in the same folder when generated.
- Reproducible analysis: create the corresponding notebook under `notebooks/`, for example `notebooks/<research-slug>.ipynb`. If supporting Python modules are needed, place them under `notebooks/<research-slug>/`.
- Notebook format: when creating or editing `.ipynb` files, use valid notebook JSON. Each cell must include `cell_type`, `metadata.language`, and structured `source` content.
- Notebook structure: every case notebook must follow the five-section audit-trail structure in [`NOTEBOOK_STRUCTURE.md`](NOTEBOOK_STRUCTURE.md): Business Case, EDA/Data Wrangling, Selected Methodology, Calculation, and Results.
- Reference notebook: use [`notebooks/ab-test-mock-data.ipynb`](../../notebooks/ab-test-mock-data.ipynb) and its adjacent data folder [`notebooks/ab-test-mock-data/`](../../notebooks/ab-test-mock-data/) as the concrete pattern for future case notebooks.
- The notebook is the audit trail: it should cover data preparation, chosen analytical method, validation, charts, CHF impact calculation, assumptions, and key outputs consumed by the deck.
- Mermaid schemas: every notebook must include a data-flow Mermaid diagram in the EDA section and a methodology/design Mermaid diagram in the Selected Methodology section.
- Notebook-adjacent data: save source-like data, processed outputs, and charts under `notebooks/<research-slug>/raw/`, `notebooks/<research-slug>/processed/`, and `notebooks/<research-slug>/charts/`. Deck artifacts remain under `docs/<research-slug>/`.
- Shared styling: use the local `sunrise_style` package for every matplotlib chart and generated Marp deck. Do not introduce local hard-coded palettes unless the shared theme lacks a needed semantic color.
- If no existing analytical skill fits the task, adapt the closest skill pattern or create a new skill folder with a `SKILL.md` before proceeding. Still use `data-preprocessing/` and `presentation-deck/`.

## Available Skills

| Folder | Use When… |
|--------|-----------|
| [`data-preprocessing/`](data-preprocessing/SKILL.md) | You need to generate synthetic telco data or clean/feature-engineer raw customer data |
| [`uplift-modeling/`](uplift-modeling/SKILL.md) | You need to decide WHO to target with a retention offer (discount, outreach) |
| [`causal-impact/`](causal-impact/SKILL.md) | A campaign launched without a control group and you need to measure its true effect |
| [`ab-test-design/`](ab-test-design/SKILL.md) | You're designing an experiment and need sample size, duration, and guardrails |
| [`channel-optimization/`](channel-optimization/SKILL.md) | You need to allocate customers across channels (SMS/email/call) under constraints |
| [`presentation-deck/`](presentation-deck/SKILL.md) | You need a structured slide deck to present case results to stakeholders |

## How to Use

1. Read this table to find the matching analytical skill.
2. Open `data-preprocessing/SKILL.md`, the selected analytical skill's `SKILL.md`, and `presentation-deck/SKILL.md`.
3. Build the research notebook/code in `notebooks/` and the deck in a separate `docs/` folder.
4. Run or validate the notebook/code and ensure the deck reflects the analytical evidence.
