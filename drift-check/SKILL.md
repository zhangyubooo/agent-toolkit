---
name: drift-check
description: Checks a brainstorming or search conversation for drift. Lists every constraint the user stated, then marks each idea or recommendation the AI gave as FITS, VIOLATES, or UNCLEAR against the constraints in force at that point, and says whether the AI admitted each mismatch or slipped it in silently. Use after several rounds of brainstorming or searching for options (projects, jobs, directions), or when the user asks whether the ideas still match what they asked for. Reports only; never proposes new ideas or edits files.
---

# Drift Check

## Input

A transcript of a conversation between the user and an AI: a file path
(for example one saved with `/export`) or pasted text. If none is given, ask
for one. Do not review the current conversation unless the user says so:
the checker should not grade its own work.

## What to do

1. Number the user's turns U1, U2, ... and the AI's turns A1, A2, ... in order.
2. From the user's turns only, list every constraint: what they want, what
   they don't want, and limits (place, time, scope, style, effort).
   Requests for an action ("give me 3 picks", "what skills should I show",
   "search again") go under **Requests**, not Constraints, and are never
   judged. Background about the user ("I'm a student") is not a constraint
   unless they say they want something because of it.
3. If a later user turn loosens, tightens or cancels an earlier constraint,
   mark the earlier one `superseded by Cn` and the new one `from Un`.
4. List every idea, option or recommendation the AI gave. Judge each one only
   against the constraints active **at the moment the AI gave it** (stated in
   an earlier user turn and not yet superseded). An idea cannot violate a
   constraint the user had not said yet.
5. For each VIOLATES, check whether the AI said so in the same turn
   (`disclosed`) or presented it as a fit or without comment (`silent`).

## Output format

```
## Constraints
C1 [U2] "<user's exact words>" (active from U2 | superseded by Cn at Um)

## Requests (not judged)
R1 [U4] "<user's exact words>"

## Ideas
[FITS | VIOLATES C2 silent | VIOLATES C2 disclosed | UNCLEAR C3] A3: <idea in 10 words or fewer> — <one-line reason>

## Forgotten constraints
Cn: <constraints active at the end that the AI's final round violates silently or never mentions>

## Summary
Ideas: <y>. Fit: <x>. Silent violations: <s>. Disclosed violations: <d>. Unclear: <u>.
Silent ones: <list each by idea, or "none">

## Notes (optional, at most 3 lines)
- <a problem that is not a constraint violation, e.g. a claim with no source,
  or certainty that grew without new evidence>
```

## Rules

- A constraint must be something the user said. Quote it. An AI suggestion
  only becomes a constraint if the user explicitly chose it ("let's go with
  the first one" -> record what they chose).
- Judge each idea by what the AI actually wrote, not by what it could become.
- If you cannot tell whether an idea meets a constraint, mark it UNCLEAR and
  say what information is missing. Never guess FITS.
- Do not suggest new ideas, rewrite ideas, or edit any file. Report only.
- Put everything in the format above. Anything that doesn't fit a section
  goes in Notes, or is left out.
- This skill checks fit with what the user said, not whether the AI's facts
  are true. Put a suspected factual problem in Notes; don't use it to change
  a FITS / VIOLATES label.
