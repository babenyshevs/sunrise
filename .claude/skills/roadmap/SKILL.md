---
name: roadmap
description: Create and maintain the user's living onboarding/strategy roadmap (e.g. a first-90-days plan) in roadmap/. Keeps a checklist-driven plan (ROADMAP.md), the input synthesis it's derived from (CONTEXT.md), and an append-only changelog (LOG.md) in sync as time passes. Use when the user says "create a roadmap", "update the roadmap", "mark X done", "what's next on the roadmap", "check in on the plan", or after notes/1:1s produce progress worth reflecting.
---

# roadmap

You maintain **one living roadmap** for the user's role — a time-boxed plan (typically first-90-days, but any horizon) that evolves as the user learns and delivers. It's the strategic counterpart to [capture-note](../capture-note/SKILL.md) and [people-profile](../people-profile/SKILL.md): those capture inputs; this is where inputs turn into a plan and the plan gets tracked against reality.

## Where it lives — files in `roadmap/`

| File | What it is | Cadence |
|---|---|---|
| `roadmap/ROADMAP.md` | The **overview** — a status header, a Mermaid **gantt timeline**, a phase table linking to the per-phase files, the JD-mandate mapping, and success signals. This is the single page the user opens; it holds no per-item checklists itself. | Edited in place as phases start/finish and the gantt shifts. |
| `roadmap/phase-N-<slug>.md` | **Per-phase detail** — one file per phase, with the phase goal, checkbox items grouped by theme, and the exit criterion (◆). This is where item-level progress is tracked. | Edited in place as items move. |
| `roadmap/CONTEXT.md` | The **synthesis** the plan is derived from — the "what the context tells me" table, sources, guardrails/risks. Reference, not daily reading. | Updated only when an *input* changes (new mandate, new stakeholder read, revised hypothesis). |
| `roadmap/LOG.md` | **Append-only changelog** — dated entries of what moved and why. Mirrors the interaction-log pattern. | One entry per update session. Never edit past entries. |

Keep the layers **separate on purpose**: the overview is scannable at a glance, phase detail is one click away, and the reasoning (CONTEXT) doesn't clutter the daily view. ROADMAP.md links to the phase files, CONTEXT.md, and LOG.md; don't inline phase checklists or the context table back into ROADMAP.md.

## The gantt timeline

`ROADMAP.md` carries a Mermaid `gantt` as its centrepiece — same conventions as the people-profile timelines:
- Start with `%%{init: {"gantt": {"useWidth": 1600, "barHeight": 22, "barGap": 5, "fontSize": 12}}}%%` so labels fit; `dateFormat YYYY-MM-DD`, a readable `axisFormat` (e.g. `%d %b`), and `tickInterval 1week`.
- **One `section` per phase.** Inside it, a bar per major workstream (anchored to real start dates + durations) and a `:milestone,` for the phase's exit criterion (◆).
- Anchor every date to the roadmap **start date**; recompute the whole chart if the start shifts. Use `crit` to highlight the flagship/highest-stakes delivery.
- Put a one-line `<!-- colour legend: … -->` comment above the fenced block.

## Two modes

### Create (bootstrap a new roadmap)
Use when no `roadmap/` exists (or the user asks for a fresh plan).

1. **Gather the inputs.** Pull from whatever the role's context lives in — the JD, the manager's profile, HR/onboarding notes, the interview history, team profiles, and any dated `notes/`. Read `me.md` for the user's own strengths/lens. Don't invent; synthesise what's there.
2. **Write `CONTEXT.md`** — a source→signal→implication table (one row per input), plus a guardrails/risks section. Each implication should point at something in the plan.
3. **Write the overview `ROADMAP.md`:**
   - A **status block** (owner, manager, BU, start, horizon, current phase, day N/total, last-updated).
   - The **gantt timeline** (see above) — one section per phase, a bar per workstream, a milestone per exit criterion.
   - A **phase table** with window, theme, exit criterion, and a link to each `phase-N-<slug>.md`.
   - A table **mapping the role's mandates** (from the JD) to where each is executed across phases — so nothing in the mandate is silently dropped.
   - A **success-signals** checklist for the whole horizon.
   - Convert relative dates to absolute using the environment date; anchor phase windows to the start date.
4. **Write one `phase-N-<slug>.md` per phase** — window (absolute dates + day range), one-line goal, checkbox items grouped by theme, and the ◆ exit criterion. Link back to the overview.
5. **Seed `LOG.md`** with a creation entry.
6. Match the repo's conventions: relative markdown links to `../team/…`, `../intreview/…`, `../notes/…`; a status/legend block kept current.

### Update (the common case — keep it living)
Use when the user reports progress, points at new notes, or asks for a check-in.

1. **Read the overview + the relevant phase file(s)** first (and CONTEXT/LOG if an input or history matters).
2. **Update item status in the phase file(s)** using the legend — `[ ]` not started · `[~]` in progress · `[x]` done · `[-]` dropped/deferred. Only change what actually moved; don't rewrite prose. Item-level checkboxes live in the phase files, not the overview.
3. **Refresh the overview**: recompute *Day N / total* from start date and the environment date, set *Current phase*, bump *Last updated*. If a workstream's real start/duration shifted, adjust its gantt bar (and dependent bars) to match.
4. **Pull progress from notes.** If recent `notes/` (from capture-note) contain completed action items or decisions that map to roadmap items, reflect them — and reference the note as `[note](../notes/<file>.md)` in the log entry.
5. **Add or re-scope items** when reality diverges: new work surfaced, a hypothesis was validated/killed, a phase slipped. Keep exit criteria honest.
6. **Update `CONTEXT.md` only if an input changed** — e.g. a stakeholder read shifts, the mandate is clarified, a guardrail is resolved. Otherwise leave it.
7. **Append one dated entry to `LOG.md`**: what moved to done, what changed and why, what's next. Most recent at the bottom.
8. **Report back** concisely: current phase + day, what you checked off, what changed, and the top 2–3 next actions. Don't paste the whole roadmap.

## Rules
- One roadmap. Edit in place — never fork a "v2" file. History lives in `LOG.md`, not in duplicated plans.
- The plan is checkbox-driven so progress is scannable at a glance (same spirit as capture-note's action items). Keep items atomic.
- Facts and the user's actual intent only — never fabricate progress, dates, or decisions. Use "TBD" when unknown.
- Keep `CONTEXT.md` out of the daily view; keep `LOG.md` append-only.
- Recompute *Day N / total* from real dates every update; a roadmap that lies about where it is in time is worse than none.
- When a note or person is relevant, link it (`../notes/…`, `../team/…`) rather than restating.
- If the horizon has elapsed (day > total), flag it and offer to roll a follow-on plan (e.g. months 4–6) rather than silently extending.
</content>
