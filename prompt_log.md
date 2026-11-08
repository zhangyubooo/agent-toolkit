# Prompt log

## Tools and models

| Tool | Model | Used for |
|---|---|---|
| Claude app (desktop, Cowork mode, with access to my local repo folder) | Claude Opus 5.5 | Reading my HW3–HW7 prompt logs for evidence, choosing the skill and MCP ideas, writing the MCP server and the three versions of `drift-check`, diagnosing the checker's mistakes |
| Claude Code 2.1.319 (Terminal) | Opus 5.5 | The "doer" in both demo runs, with the `design-jobs` MCP server |
| Claude Code 2.1.319 (Terminal, separate window) | Sonnet 5.5 | The checker: running `drift-check` on the exported transcripts |

For the demo runs, Claude drafted the wording
from things I had told it about my direction, and I checked each one before
sending it. Many of my turns were just a screenshot of the Terminal; those are
noted, not quoted.

---

## Part 1: Planning (Claude app, Opus 5.5)

**1. Understanding the brief**
> What can I do for this hw?

**2. Evidence**
> Do I have to have evidence? Does it have to come from projects I did in 113?

Claude: yes, quotes from the HW3–HW7 logs (Grounding is 15 points), but the
tool and the demo task don't have to be about 113.

> Read the files and give me some directions.

Claude read my prompt logs for HW3 (World Oracle), HW4 (Ask Yubo), Project 2
(Napier's Rod Box), HW6 (Designer Lens) and HW7 (both phases). HW5 had no log.

**3. Choosing the idea**
> What else could the skill and MCP be? Give me a few more that fit the requirements.

> Could the skill be about brainstorming with AI: after several rounds of ideas, the AI tends to give things that don't actually match what I wanted at the start? Could the MCP be about design job hunting?

This is where both pieces came from. The skill idea is my own friction; the
evidence for it is in README.md.

> OK, let's go with this pair. First tell me all the steps from start to finish, then start.

**4. Which tool**
> Does it have to be Codex?

Claude: no; the brief only asks for a separate session and ideally a
different model. Options: Codex + Claude Code, Claude Code with two models,
or Codex only.

> Claude code, then.

(Option B: Claude Code only, with Opus doing the work and Sonnet checking it.)

**5. Building and registering the server** (mostly screenshots)
- *[screenshot: `find_boards.py` says every company is "not found"]* → Claude
  found the cause: python.org's Mac Python has no root certificates, and the
  script hid the error.
- *[screenshot: `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`]*
  → `mcp` 2.x renamed `FastMCP` to `MCPServer`.
- *[screenshot: `claude mcp list` → `design-jobs … ✔ Connected`]*

> Can it only search these three systems?

Claude listed other options (more boards like SmartRecruiters, an aggregator
API like Adzuna) and recommended keeping three for now and writing the gap in
the README.

**6. Running the demos**
> Let's go one step at a time. Tell me exactly what to send, and I'll copy and paste it.

**7. Revising the checker**
- After Claude listed v1's problems (judging early ideas by later rules; not
  telling disclosed from silent violations; requests listed as constraints):
  > Agreed. I already pushed v1.
- After the two v2 runs both listed a request as a constraint:
  > Agreed to v3.

**8. Finalizing**
> Answer to question 1: I still held to it.

Claude fixed the problem.

---

## Part 2: Claude Code (verbatim)

### Checking that the skill and server load (Opus 5.5)

```
/skills
orange check
/clear
/orange-test hello   # (typed in Chinese)
/clear
Are there any design internships open right now at the companies I'm tracking?
```

### Run 1, doer (Opus 5.5) → `demos/run1-doer.txt`

```
I'm a design student at CMU (School of Design, Environments track) looking for a summer 2027 internship. What design internships are open right now?
```
```
I'm less interested in pure screen-based UI work. I want roles that involve physical prototyping, interactive installations, or hardware, something like a creative technologist or an interaction designer who builds things. Can you search again with that in mind?
```
```
OK. Since nothing matches exactly, I'm open to design roles that are partly screen-based, as long as the product connects to physical objects or spaces, like hardware, devices, or venues. It also has to be in the US. Search again with that.
```
```
Got it. Even so, I need to apply to something this cycle. Give me your final top 3 picks to apply to, with one line each on why.
```

### Run 2, doer (Opus 5.5) → `demos/run2-doer.txt`

```
Different question this time. I want to plan my portfolio for next year's applications. What design roles at any level are open at the companies I'm tracking, in New York or remote?
```
```
Leave out research, writing, and management roles. I only care about roles where you actually design and make things.
```
```
Also drop anything senior, staff, lead or principal. I'm a student, so I want roles I could realistically grow into in two or three years.
```
```
Based only on these postings, what three skills should my portfolio show?
```

### Checker (Sonnet 5.5, new window each time)

Used for v1, v2 and v3 on run 1 (`run1-checker.txt`, `run1-checker-v2.txt`,
`run1-checker-v3.txt`):
```
Here's a transcript of me looking for internships with an AI: demos/run1-doer.txt. Did the AI drift from what I actually asked for?
```

Used for v2 on run 2 (`run2-checker.txt`):
```
Here's a transcript of me planning my portfolio with an AI: demos/run2-doer.txt. Did the AI drift from what I actually asked for?
```

The checker prompts never name the skill on purpose, to test whether the
description alone makes Claude load it. It did every time
(`Skill(drift-check)` at the top of each checker transcript).
