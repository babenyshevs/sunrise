---
name: capture-note
description: Turn a raw dump (meeting, 1:1, interview, or ad-hoc thought) into a clean, consistently-structured markdown note filed in notes/, with extracted decisions, action items, and open questions, and links to the people involved. Use whenever the user pastes messy notes, a meeting transcript, or says "capture this" / "log this meeting" / "note from my 1:1 with X".
---

# capture-note

You convert raw, unstructured input into one well-structured note file. This is the backbone of the repo — everything else (people profiles, weekly review) reads these notes, so **consistency of structure matters more than prose polish**.

## Inputs

The raw content may be in the skill args, the current message, a pasted block, or a file the user points to. If you have nothing to work with, ask the user to paste the notes or name the source file. Do not invent content — only structure what you're given.

## Steps

1. **Classify the note type** from the content:
   - `1:1` — one-on-one with a team member or manager
   - `meeting` — group / stakeholder / project meeting
   - `interview` — hiring interview (candidate or the user's own process)
   - `idea` — a thought, plan, or observation with no meeting attached
   
2. **Determine the date.** Use the date the user gives. If none, use today's date from the environment context. Format `YYYY-MM-DD`.

3. **Identify people mentioned.** For each, note whether they look like a team member, a stakeholder, or external. You'll link to their profiles in step 5.

4. **Write the note** to `notes/YYYY-MM-DD-<short-slug>.md` (kebab-case slug from the topic, e.g. `2026-07-02-adao-kickoff.md`). Use this exact template:

```markdown
---
date: YYYY-MM-DD
type: 1:1 | meeting | interview | idea
title: <short human title>
people: [<name>, <name>]
tags: [<topic>, <topic>]
---

# <title>

## Summary
<2-4 sentences: what this was and the single most important takeaway.>

## Key points
- <the substantive content, cleaned up into clear bullets>

## Decisions
- <decision made, if any — omit the section if none>

## Action items
- [ ] <action> — owner: <name> — due: <date or "TBD">

## Open questions
- <unresolved question or thing to follow up on>

## People
- [<Name>](../team/<slug>.md) — <one line of relevant context from this note>
```

5. **Cross-link people.** For each person, point the link at `team/<slug>.md` or `stakeholders/<slug>.md` (kebab-case, e.g. `klaus-lamel.md`). The profile file may not exist yet — that's fine, the link marks it as worth creating. If the note contains meaningful new information about a person (a priority they voiced, a working-style signal, a commitment they made), offer to run **people-profile** to append it to their profile.

6. **Report back** concisely: the file path created, the count of action items and open questions, and any suggested people-profile updates. Do not paste the whole note back.

## Rules

- One note per file. Never overwrite an existing note — if the slug collides, append `-2`.
- Preserve the user's meaning; never fabricate decisions, owners, or dates. Use "TBD" when unknown.
- Keep action items atomic and checkbox-formatted so the weekly review can scan them.
- Omit empty sections rather than leaving them blank.
