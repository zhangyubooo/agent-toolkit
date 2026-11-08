# DEMONSTRATION

> Full, untrimmed transcripts are in `demos/`. Screenshots are in
> `demos/screenshots/`.

## Setup

- **Tool:** Claude Code 2.1.319 in the macOS Terminal.
- **Doer:** Opus 5.5, with the `design-jobs` MCP server.
- **Checker:** Sonnet 5.5, in a **separate Terminal window** started with
  `claude --model sonnet`. It only saw the exported transcript file, not the
  doer's session.
- Transcripts were exported with Claude Code's `/export <file>`.
- In neither session did I name the tool or the skill. Both were picked from
  their descriptions: the doer shows `Called design-jobs`, the checker shows
  `Skill(drift-check)`.

Before the real task I checked that both pieces load:

| Check | Evidence |
|---|---|
| Server registered | `claude mcp list` → `design-jobs … ✔ Connected` (`01`) |
| Tool visible to the agent | `/mcp` → `design-jobs`, 1 tool, `search_design_jobs` (`02`, `03`) |
| Test skill loads automatically | "orange check" → `Skill(orange-test)` → "🍊 orange-test skill loaded" (`05`) |
| Test skill loads by name | `/orange-test hello` (typed in Chinese) → "🍊 orange-test skill loaded" (`06`) |
| Agent calls the tool unprompted | "Are there any design internships open right now at the companies I'm tracking?" → `Called design-jobs` (`07`) |

## The real task

I'm looking for a **summer 2027 internship** and starting to plan my
**portfolio for next year's applications**. The tool searches the live job
boards of the 12 companies in `design-jobs-mcp/companies.csv`.

---

## Run 1: finding a summer 2027 internship

**Files:** `demos/run1-doer.txt` (doer), `demos/run1-checker.txt` (v1),
`demos/run1-checker-v2.txt` (v2), `demos/run1-checker-v3.txt` (v3)

### What the doer did (trimmed)

```
❯ I'm a design student at CMU (School of Design, Environments track) looking
  for a summer 2027 internship. What design internships are open right now?

  Called design-jobs (ctrl+o to expand)

⏺ I searched the live job boards of the 12 companies in your companies.csv
  (...). I found 2 internships worth looking at. None of them is an
  Environments role.
  Good fits
  - Figma: Product Design Intern (2027), SF or NYC, posted Sep 14, 2026. ...
  - Palantir: Product Designer, Internship (US Government), Palo Alto ...
  What this search doesn't cover
  - These results only come from the 12 companies in your list ...

❯ I'm less interested in pure screen-based UI work. I want roles that involve
  physical prototyping, interactive installations, or hardware, something like
  a creative technologist or an interaction designer who builds things. Can
  you search again with that in mind?

  Called design-jobs 2 times (ctrl+o to expand)

⏺ None of the 12 companies on your list has a hands-on, build-things
  internship open right now.
  What I searched: internships only, using the keywords creative
  technologist, prototyping, interaction, installation, hardware, ...

❯ OK. Since nothing matches exactly, I'm open to design roles that are partly
  screen-based, as long as the product connects to physical objects or
  spaces, like hardware, devices, or venues. It also has to be in the US.
  Search again with that.

  Called design-jobs 2 times (ctrl+o to expand)

⏺ Even with the looser criteria, none of the open US design internships at
  your 12 companies involves a product tied to physical objects or spaces.
  [table: Figma, Palantir, Pinterest, Figma PhD — each with "why it doesn't fit"]

❯ Got it. Even so, I need to apply to something this cycle. Give me your
  final top 3 picks to apply to, with one line each on why.

⏺ None of these meets your physical-product criterion. All three are software
  roles. Here are the best picks among what's actually open:
  1. Figma: Product Design Intern (2027) ...
  2. Palantir: Product Designer, Internship, US Government ...
  3. Pinterest: UX Quantitative Research Intern (USA) ... This is a weak third.
```

The tool was called 5 times, always between my question and the answer
(screenshot `08`). The answers stayed inside what the tool returned and
repeated its limit ("only come from the 12 companies in your list").

### What the checker caught (final version, v3)

```
Constraints
C1 [U1] "looking for a summer 2027 internship" (active from U1)
C2 [U1] "What design internships are open right now?" (design internships; active from U1)
C3 [U2] "I'm less interested in pure screen-based UI work. I want roles that involve
   physical prototyping, interactive installations, or hardware" (active from U2; the
   screen-based part is superseded by C4 at U3)
C4 [U3] "I'm open to design roles that are partly screen-based, as long as the product
   connects to physical objects or spaces ..." (active from U3; loosens C3)
C5 [U3] "It also has to be in the US." (active from U3)

[FITS] A1: Figma Product Design Intern (2027), SF/NYC — design internship, targets 2027
[VIOLATES C4 disclosed] A4: Figma Product Design Intern — A4 opened with "None of these
   meets your physical-product criterion"
[UNCLEAR C4] A4: Palantir Product Designer Intern — the listing doesn't say whether it
   involves hardware or venues ...; the year is also unconfirmed (C1)
[VIOLATES C2 disclosed] A4: Pinterest UX Quantitative Research Intern — A4 said "It's
   research, not design" and "a weak third"

Summary
Ideas: 13. Fit: 9. Silent violations: 0. Disclosed violations: 2. Unclear: 2.
```

v1 got this run wrong in ways described in ITERATION.md (it said the round-1
Figma pick already violated rules I only stated later).

---

## Run 2: planning my portfolio from what's actually open

**Files:** `demos/run2-doer.txt` (doer), `demos/run2-checker.txt` (v2)

### What the doer did (trimmed)

```
❯ Different question this time. I want to plan my portfolio for next year's
  applications. What design roles at any level are open at the companies I'm
  tracking, in New York or remote?

  Called design-jobs 3 times, ran 1 shell command (ctrl+o to expand)

⏺ I found about 25 design roles open right now at your 12 tracked companies,
  in New York or remote. ... all 12 loaded without errors.
  [list grouped by level: internship / mid-level / senior / leadership]
  - Hidden posts: my first, broader search found 46 postings but showed only
    the newest 30. I narrowed the keywords until the results fit ...

❯ Leave out research, writing, and management roles. I only care about roles
  where you actually design and make things.

⏺ Here's the list with leadership roles taken out. ... That leaves 22 roles
  ... Staff-level roles are still individual-contributor work, so I kept them.
  ...
  Your portfolio should probably show product design work ... That's what
  most of these roles ask for.

❯ Also drop anything senior, staff, lead or principal. I'm a student, so I
  want roles I could realistically grow into in two or three years.

⏺ Here's the list with every Senior, Staff, Lead and Principal role removed.
  ... That leaves 15 roles.
  - Unstated seniority: I sorted these by title only, and I haven't opened
    the postings. ...

❯ Based only on these postings, what three skills should my portfolio show?

⏺ I can only partly answer this. The search tool returns titles, teams and
  locations, not the full job descriptions, so I haven't seen what any of
  these postings actually require. Going by the 15 titles alone:
  1. Product design ... About 11 of the 15 roles are Product Designer roles:
     all the Palantir roles, ...
  2. Brand and motion design ...
  3. Designing in code or for the web. This signal is much weaker. ...
```

Two things worth noticing about the tool here: when the first search hit the
30-result cap, the agent saw the "46 matching postings, showing newest 30"
line and narrowed its search; and in the last turn it stated the tool's real
limit (titles only, no descriptions) instead of inventing requirements.

### What the checker caught (v2)

```
[FITS] A1: Figma Director, Figma Manager and Duolingo VP roles listed.
   Management was not yet excluded.
[VIOLATES C2 disclosed] A1: Spotify Staff Product Designer, London. The AI
   flagged that "remote" likely means UK/EU, not NY.
[UNCLEAR C1] A1–A3: Palantir 2017/2019 (and 2024–25) posts listed as open roles.
   A1 hedged that they're "probably" left open. A2 and A3 state "(left open to
   collect applications)" as fact, and nothing shows whether they're hiring.
[FITS] A2: Portfolio advice. But "That's what most of these roles ask for" is
   unsupported, since A4 admits the postings were never read.
[FITS] A4: Skill 1, product design. ... The count slips by listing "all the
   Palantir roles" as product design, though Web Design Engineer is a coding role.

Summary
Ideas: 18. Fit: 10. Silent violations: 0. Disclosed violations: 2. Unclear: 6.
```

The second and third findings aren't really constraint violations; they're
claims without evidence. That is why v3 says drift-check checks fit with what
I said, not whether the AI is right, and puts such findings in Notes (see
ITERATION.md).
