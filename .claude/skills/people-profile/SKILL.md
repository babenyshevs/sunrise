---
name: people-profile
description: Create or update a durable profile for a person the user works with — a direct report, their manager, or a cross-org stakeholder. Maintains role, org context, priorities, working style, open threads, a visual career/education timeline, and a dated interaction log. Use when the user says "profile X", "update X's file", "log my interaction with X", "who is X", or after a note mentions someone worth tracking.
---

# people-profile

You maintain one durable file per person. Profiles are for people the user has an ongoing working relationship with (team, manager, stakeholders) — this is how the user navigates a matrix org and honors the "meet as many people as possible" onboarding mandate.

## Where profiles live

- `me.md` (repo root) — the **user's own profile**. Same structure as everyone else. It's the reference point for finding common ground; read it whenever you create or update another profile.
- `team/<slug>.md` — direct reports and the user's manager
- `stakeholders/<slug>.md` — cross-org: product owners, business partners, senior leaders, peers in other chapters

`<slug>` is kebab-case of the full name, e.g. `klaus-lamel.md`, `fernando-<last>.md`. If you know only a first name, use it and note that the last name is TBD.

**Two forms — file or folder.** A person is either a single file (`team/<slug>.md`) or, when they have attachments (publications, docs, etc.), a folder `team/<slug>/` containing the profile as `team/<slug>/<slug>.md` plus attachment subfolders (e.g. `publications/`). Always name the profile file after the slug — **never `README.md`** (an uninformative editor tab). When searching, check both `team/<slug>.md` and `team/<slug>/<slug>.md`. To convert a file to a folder: `mkdir team/<slug>/`, move the file to `team/<slug>/<slug>.md`, and fix inbound links (they change from `<slug>.md` to `<slug>/<slug>.md`).

**Attachments (e.g. publications).** When a person has documents, analyse them and write a sibling summary (e.g. `publications-analysis.md`) linked from the profile's own section. For academic publications specifically: identify author order and **deep-analyse only the papers where the person is first (or sole) author**; list the rest briefly with their authorship position. Always tie findings back to relevance for the user's team/role, not just a neutral summary.

## Steps

1. **Find the existing profile.** Search `team/` and `stakeholders/` for a matching file (fuzzy — match on first name if needed). If one exists, you **update** it. If not, you **create** it.

2. **If creating and the folder is ambiguous** (team vs stakeholder), infer from context; ask only if genuinely unclear.

3. **Create** from the template below (omit sections you have nothing for — don't leave placeholders). The `## Timeline` block is a Mermaid gantt — see "Building the timeline" for how to fill it.

~~~markdown
---
name: <Full Name>
role: <title>
org: <unit / chapter / team, e.g. "ADAO — Data Science">
reports_to: <name or "—">
relation: manager | report | stakeholder | peer
home_country: <inferred nationality/origin — mark "(inferred)">
languages: [<inferred spoken languages, mark "(inferred)">]
updated: YYYY-MM-DD
---

# <Full Name>

## Snapshot
<1-3 sentences: who they are and why they matter to the user's work.>

## Priorities & what they care about
- <what drives them, their goals, their pressures>

## How to work with them
- <communication style, preferences, dos/don'ts, decision style>

## Common ground with you
- <shared connection points read from me.md — see "Finding common ground". Omit this section on me.md itself.>

## Open threads
- [ ] <ongoing item, commitment, or thing to raise next time>

## Timeline
<Mermaid gantt — see "Building the timeline".>

## Career & education history
- **YYYY–YYYY** — <role / degree> @ <org> — <one-line note>

## Interests & hobbies
- <climbing, running, music, languages… — feeds common-ground matching; omit if unknown>

## Interaction log
- **YYYY-MM-DD** — <what happened / what was discussed / what you learned>
~~~

## Building the timeline

The `## Timeline` section is a Mermaid `gantt` chart. Encode three dimensions:

- **Horizontal axis = time.** Use `dateFormat YYYY-MM` and `axisFormat %Y`. Use the first of the month; if only a year is known, use `-01` and note the approximation.
- **Make it wide.** Start the diagram with an init directive to force a fixed pixel width so long role labels fit and the bars spread out:
  `%%{init: {"gantt": {"useWidth": 1600, "barHeight": 22, "barGap": 5, "fontSize": 12}}}%%`
  Bump `useWidth` higher for longer careers. `tickInterval 2year` (or `1year`) controls axis-label density.
- **Scope: university and work only.** Do NOT include pre-university / secondary schooling (high school, Matura, Gymnasium) in the timeline or the history list — it's not useful. Start education at the first university degree.
- **Sections (vertical grouping) = the *category*:**
  - Work → split into `Work — IC · <org>` and `Work — Managerial · <org>` (IC vs. people-management is the key distinction).
  - Education → group by field, e.g. `Education — Economics (University)`, `Education — STEM (University)`.
- **Task tags = colour, used for organisation/school identity.** Assign each distinct employer/school a tag so same-company vs. different-company is visible at a glance. Available tags: `done`, `active`, `crit`, plus untagged (4 distinct colours). Reuse the same tag for the same org. Add a one-line legend comment above the chart mapping tag → org.
  - Use `crit` to highlight the **current / most-recent** role even if it reuses an org's colour — currency matters most.
  - Use `:milestone,` for point-in-time events like a degree being awarded (optional).

Put a short `%%`-style HTML comment legend right before the fenced block, e.g.
`<!-- colour legend: done = University of Zurich · active = UPC/Sunrise · crit = current role -->`

Order sections chronologically top-to-bottom (education first, then work IC, then work managerial) so the eye reads early-career → now.

## Finding common ground

When creating or updating anyone's profile (not `me.md`), read `me.md` and populate `## Common ground with you` with genuine overlaps that make good rapport-openers:

- **Shared languages** — especially less-common ones (Romansh, Czech, etc. land harder than English).
- **Same institutions** — universities, past employers; note if tenures **overlapped in time** (you may have crossed paths).
- **Shared field / methods** — e.g. both econometrics / causal inference / a specific technique.
- **Home country or region.**
- **Hobbies & interests** — climbing, skiing, music, running, etc.
- **Career parallels** — similar path (academia→industry), same prior industry, etc.

Rules: list only real matches (skip the section if there are none); put the strongest/most specific first; keep each a short phrase, not a paragraph. If `me.md` doesn't exist yet, skip the section and note that it's pending.

## Updating an existing profile

Do NOT rewrite the file. Specifically:
- **Append** a new dated bullet to `## Interaction log` (most recent at the bottom).
- Add to `Priorities`, `How to work with them`, or `Open threads` only when there's genuinely new signal. Check off or remove resolved open threads.
- Extend `## Timeline` and `## Career & education history` when a new role/degree comes to light; move the prior current-role tag off `crit`.
- Refresh the `updated:` frontmatter date.
- Leave everything else untouched.

Then **report back** concisely: file path, whether created or updated, and what changed. Don't paste the whole profile.

## Rules

- Facts only — capture what the user actually observed or was told. Mark inferences as inferences.
- **Infer `home_country` and `languages`** from available signal: name origin, education/work locations, degree language, country of employers. Always tag inferred values "(inferred)" and keep them tentative — these are best-guesses to confirm later, not facts. E.g. schooling + career entirely in German-speaking Switzerland → home_country: Switzerland (inferred); languages: [German (inferred), English (inferred)].
- Convert relative dates ("last Tuesday", "next week") to absolute `YYYY-MM-DD` using the environment date.
- The interaction log is append-only history; never edit past entries.
- If a `capture-note` note relates to this person, you may reference it as `[note](../notes/<file>.md)`.
- Link related people with a relative markdown link, e.g. `[Klaus Lamel](klaus-lamel.md)`.
