# ITERATION

> Drafted by Claude (Opus 5.5) from the transcripts in `demos/` and the git
> history; checked and approved by Yubo. Every quote below is copied from a
> file in `demos/`.

The skill went through three versions. Each version is a commit, so the
exact before/after is one `git diff` away:

| Version | Commit | Tested on |
|---|---|---|
| v1 | `49d7a5d` (first commit) | `demos/run1-checker.txt` |
| v2 | `1263ed2` | `demos/run1-checker-v2.txt`, `demos/run2-checker.txt` |
| v3 | `50e0ada` | `demos/run1-checker-v3.txt` |

All checker runs used **Sonnet 5.5** in a fresh Claude Code window. The work
being checked was done by **Opus 5.5** in a different window.

---

## Failure 1 (v1): it judged early ideas against rules I hadn't said yet

**What went wrong.** In run 1, the AI's first answer (A1) recommended Figma's
*Product Design Intern (2027)*. At that point I had only asked for a summer
2027 design internship. One turn later I said "I'm less interested in pure
screen-based UI work." v1 marked the A1 recommendation as a violation of that
later rule:

```
I judged each idea against the constraints active at the end.

[VIOLATES C2, C4] A1: Figma Product Design Intern, labeled "Good fit" — Figma
is all software.
```

That's not drift. The AI couldn't have known a rule I hadn't stated yet.
Because every early idea got judged this way, the summary ("0 of 11 ideas fit
every active constraint") made the AI look much worse than it was.

**Why.** My v1 said "check each one against every active constraint" and
never said *active when*. The model picked "active at the end", which is the
simplest reading.

**Fix (v2).** Step 4 now says: judge each idea only against the constraints
active **at the moment the AI gave it**, and "an idea cannot violate a
constraint the user had not said yet." Each constraint now records when it
started and when it was superseded (`active from U2 | superseded by Cn at Um`).

**Rerun.** Same transcript, v2:

```
[FITS] A1: Figma Product Design Intern (2027), SF/NYC — design internship,
targets summer 2027, posted Sep 2026. Only C1 and C2 were active.
```

It held on a new transcript too (run 2): "Management was not yet excluded",
"Staff wasn't excluded yet."

## Failure 2 (v1): it couldn't tell honest mismatches from silent drift

**What went wrong.** For my final top 3, the AI opened with "None of these
meets your physical-product criterion" and called pick #3 "a weak third".
v1 gave these the same `VIOLATES` label it would give a mismatch the AI
hid. It only mentioned the difference in an extra paragraph outside the
format ("The AI was open about the mismatch…").

**Why it matters.** The thing I kept correcting in my old logs was the AI
quietly handing me something that didn't match. An AI that says "this
doesn't fit, but it's the best available" is doing its job.

**Fix (v2).** New step 5 and two labels: `VIOLATES Cn silent` and
`VIOLATES Cn disclosed`. The summary counts them separately, silent first.

**Rerun.** Run 1 with v2: "Silent violations: 0. Disclosed violations: 7."
Run 2 with v2: "Silent violations: 0. Disclosed violations: 2." (the Spotify
London role, flagged by the AI both times).

## Failure 3 (v2): a rule saying "don't" was ignored twice

**What went wrong.** v2 said "A request for an action ('give me 3 picks',
'search again') is not a constraint." The checker listed it as one anyway, in
both v2 runs:

- run 1: `C7 [U4] "Give me your final top 3 picks to apply to, with one line each on why." (active from U4)`
- run 2: `C9 [U4] "what three skills should my portfolio show" (active from U4)`

In run 1 this produced a nitpick reported as drift:

```
Forgotten constraints
C7: The Palantir and Pinterest picks run 2–3 sentences, not "one line each".
```

v2 also said "No extra sections", and both runs still added free paragraphs
after the summary. Some of those paragraphs were useful (run 2 caught an
unsupported claim, "That's what most of these roles ask for").

**Why.** The model wants to put everything the user said *somewhere*. A
prohibition with no alternative place loses to that habit. The course tip
"specify the output format" turned out to apply here too: format beats
instructions.

**Fix (v3).** Instead of forbidding, give it a place:

- a `Requests (not judged)` section for things like "give me 3 picks"
- a `Notes (optional, at most 3 lines)` section for useful observations that
  aren't constraint violations
- a rule that this skill checks fit with what I said, not whether facts are
  true; factual worries go in Notes and don't change a label

**Rerun.** Run 1 with v3:

```
Requests (not judged)
R4 [U4] "Give me your final top 3 picks to apply to, with one line each on why."

Forgotten constraints
None. A4 opens by naming the physical-product criterion, and all three picks
are US-based (C5).
```

The extra observations moved into Notes. One of them asked a question only I
can answer: whether "Even so, I need to apply to something this cycle" was
meant to relax the physical-product requirement. (My answer is in
DEMONSTRATION.md.)

## Still not fixed

- **Borderline items aren't labeled consistently.** On the same run 1
  transcript, v1 / v2 / v3 counted 11 / 19 / 13 ideas. The AI's lists of
  "companies to consider (not confirmed openings)" were UNCLEAR in v1 and v2
  and FITS in v3, even though v3 didn't change anything about them. It
  depends on whether the checker reads "look at these companies" as a
  recommended job or a recommended direction. I'm leaving this documented
  rather than adding more rules.
- **It only sees what I said out loud.** In my old logs, some constraints only
  appeared when I corrected the AI ("I want to do something more spatial").
  The checker can't catch a mismatch with a preference I never stated.

---

## The MCP server's failures (found while building it)

These came up before the demos, while running the server by hand.

1. **"International" counted as an internship.** With `internship_only=True`,
   "Staff Experience Designer, International" came back as an internship,
   because I matched the letters `intern` anywhere in the title. Found by
   running the tool against saved API responses. Fix: match whole words only
   (`\b(intern|internship|co-?op)\b`).
2. **Errors reported as "not found".** `find_boards.py` said every company
   (Figma, Pinterest, Spotify…) was "not found". curl worked, so the boards
   existed. The real error was `CERTIFICATE_VERIFY_FAILED`: python.org's Mac
   Python has no root certificates, and the script swallowed every error as
   "not found". This is the failure the assignment warns about, a tool that
   doesn't do what it says. Fix: use `certifi`'s certificates, and treat a 404
   ("not on this board") differently from a network error ("COULD NOT CHECK").
   The server itself reports unreadable boards in its output instead of
   dropping them.
3. **The course example didn't run.** `pip install mcp` gave version 2.3.0,
   where `FastMCP` was renamed `MCPServer`. Fix: use the new name and pin
   `mcp>=2.3,<3` in `requirements.txt`.
