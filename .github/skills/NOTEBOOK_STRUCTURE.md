# Research Notebook Structure

Use this structure for every case notebook created by the `make-research` workflow, regardless of analytical method.

Reference implementation: [`notebooks/ab-test-mock-data.ipynb`](../../notebooks/ab-test-mock-data.ipynb)

Supporting data pattern: [`notebooks/ab-test-mock-data/`](../../notebooks/ab-test-mock-data/)

## Required Notebook Sections

1. **Business Case: What and Why**
   - State the business decision, stakeholder question, why the analysis matters, and the decision rule.
   - Define the target population, outcome, value metric, and operational constraints.

2. **EDA: Data Sources, Table Structure, and Wrangling**
   - Describe the data sources and table grains.
   - Mimic realistic joins when using synthetic data, such as CRM, billing, product, channel, assignment, and outcome tables.
   - Add a Mermaid **Data Flow Schema** showing how source tables flow through joins, cleaning, feature engineering, modeling tables, analysis outputs, and saved artifacts.
   - Inspect schema, missingness, identifiers, time windows, leakage risk, and preprocessing choices.
   - Save source-like mock tables and processed modeling tables next to the notebook under `notebooks/<research-slug>/`.

3. **Selected Methodology: Theory and Assumptions**
   - Explain why the method is appropriate and what naive approach it replaces.
   - Include formulas in LaTeX where useful.
   - Add a Mermaid **methodology schema** showing the analytical design, such as treatment/control assignment, covariates, outcomes, guardrails, constraints, counterfactual path, or optimization objective.
   - Add explanatory graphs or diagrams for statistical tests, model mechanics, optimization constraints, counterfactual logic, or uplift evaluation.
   - Make assumptions, identification strategy, uncertainty, and decision thresholds explicit.

4. **Calculation: Tests, Models, Charts, and CHF Impact**
   - Run the actual statistical tests, model fits, optimization, counterfactual estimation, or uplift scoring.
   - Generate validation charts and diagnostic tables.
   - Convert the analytical result into CHF impact using transparent assumptions.
   - Save outputs next to the notebook under `notebooks/<research-slug>/processed/` and `notebooks/<research-slug>/charts/`.

5. **Results: Conclusion and Recommendation**
   - Summarize what was found, what decision it supports, and what should happen next.
   - Include limitations, residual risks, guardrails, sensitivity, and follow-up experiments or monitoring.
   - Ensure the final recommendation follows the evidence, even if the answer is no-launch, iterate, or inconclusive.

## Notebook JSON Requirements

- Create or edit `.ipynb` files as valid notebook JSON.
- Each cell must include `cell_type`, `metadata.language`, and structured `source` content.
- Existing cells must retain a stable `metadata.id` when the editor preserves it.
- Keep code cells small enough that a reviewer can rerun and debug sections independently.
- Mermaid schemas must be markdown cells with fenced `mermaid` blocks. Do not generate them as images unless the user explicitly asks for exported diagrams.

## Required Mermaid Schemas

Every case notebook must include at least two Mermaid diagrams:

1. **Data Flow Schema** in the EDA/Data Wrangling section.
   - Show source-like tables, their grain, join path, cleaning or feature engineering, modeling table, downstream analysis, and saved raw/processed/chart artifacts.
   - For synthetic data, make the mock source system explicit instead of hiding all generation in one flat table.

2. **Methodology or Experiment Design Schema** in the Selected Methodology section.
   - For A/B tests: show random assignment, treatment/control, pre-treatment covariates, primary metric, business metric, CUPED or variance-reduction path, guardrails, and launch decision.
   - For uplift: show treatment, outcome, control/treatment comparison, uplift score, targeting decision, cost, and CHF impact.
   - For causal impact: show intervention, pre/post windows, covariates, counterfactual model, observed outcome, point/cumulative effect, and ROI.
   - For channel optimization: show eligible customers, actions/channels, propensity or expected-value inputs, constraints, optimization objective, allocation, and operational outputs.

## Adjacent Artifact Layout

For each notebook `notebooks/<research-slug>.ipynb`, create an adjacent folder:

```text
notebooks/<research-slug>/
├── raw/          # source-like mock or extracted input tables
├── processed/    # joined modeling tables, results, summaries, diagnostics
└── charts/       # EDA, methodology, validation, result charts
```

Deck artifacts remain under `docs/<research-slug>/`; notebook data and diagnostics stay under `notebooks/<research-slug>/`.