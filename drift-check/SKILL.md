---
name: drift-check
description: Checks a brainstorming or search conversation for drift. Lists every constraint the user stated, then marks each idea or recommendation the AI gave as FITS, VIOLATES, or UNCLEAR against those constraints. Use after several rounds of brainstorming or searching for options (projects, jobs, directions), or when the user asks whether the ideas still match what they asked for. Reports only; never proposes new ideas or edits files.
---

# Drift Check

## Input

A transcript of a conversation between the user and an AI: a file path
(for example one saved with `/export`) or pasted text. If none is given, ask
for one. Do not review the current conversation unless the user says so:
the checker should not grade its own work.

## What to do

1. Number the user's turns U1, U2, ... and the AI's turns A1, A2, ...
2. From the user's turns only, list every constraint: what they want, what
   they don't want, and limits (place, time, scope, style, effort).
3. If a later user turn changes or cancels an earlier constraint, mark the
   earlier one as superseded and judge only against the later one.
4. List every idea, option or recommendation the AI gave, and check each one
   against every active constraint.

## Output format

```
## Constraints
C1 [U2] "<user's exact words>" (active | superseded by Cn)

## Ideas
[FITS | VIOLATES C2, C5 | UNCLEAR C3] A3: <idea in 10 words or fewer> — <one-line reason>

## Forgotten constraints
Cn: <active constraints that the AI's final round of ideas violates or never mentions>

## Summary
<x> of <y> ideas fit every active constraint. Most violated: Cn.
```

## Rules

- A constraint must be something the user said. Quote it. An AI suggestion
  only becomes a constraint if the user explicitly chose it ("let's go with
  the first one" -> record what they chose).
- Judge each idea by what the AI actually wrote, not by what it could become.
- If you cannot tell whether an idea meets a constraint, mark it UNCLEAR and
  say what information is missing. Never guess FITS.
- Do not suggest new ideas, rewrite ideas, or edit any file. Report only.
