# agent-toolkit

A small agent toolkit for 15-114 HW8:

- **`drift-check`** (a skill, a checker): after several rounds of brainstorming
  or searching with an AI, checks whether the AI's ideas still match what I
  actually asked for.
- **`design-jobs`** (an MCP server with one tool, `search_design_jobs`):
  searches the design jobs that the companies I follow are hiring for
  **right now**.

## What drift-check does and when it triggers

Give it a transcript of a conversation with an AI (exported with Claude
Code's `/export`). It:

1. Lists every constraint from **my** turns, with my exact words and which
   turn it came from. A later constraint supersedes an earlier one.
2. Lists requests like "give me 3 picks" separately. They are not
   constraints and are not judged.
3. Marks each idea the AI gave as `FITS`, `VIOLATES` or `UNCLEAR`, judged
   **only against the constraints in force when the AI gave it**.
4. Tells two kinds of violation apart: the AI said the idea doesn't fit
   (`disclosed`), or it handed it over without a word (`silent`). Silent
   drift is what it is there to catch.
5. Reports only. It never suggests new ideas or edits files.

**Trigger:** after several rounds of brainstorming or looking for options
(project directions, jobs…), ask something like "Did the AI drift from what I
asked for?". Claude loads the skill from its description. You can also type
`/drift-check`. **Run it in a new session**, ideally on a different model, so
the AI isn't checking its own work.

**Limits:** it checks fit with what I said, not whether the AI's facts are
true. Suspected factual problems go in its Notes section and don't change a
label. It also can't catch a preference I never said out loud.

## What design-jobs does

`search_design_jobs(keywords, location="", internship_only=False)` queries,
live, the public job boards (Greenhouse, Lever, Ashby; no API key needed) of
the 12 companies in `design-jobs-mcp/companies.csv`. It returns title,
location, team, posting date and link, at most 30 results, newest first, and
ends by saying which companies it searched and which boards it couldn't read.

**It can only search the companies on the list.** "No results" means none of
those companies has a match, not that the job doesn't exist anywhere. The
docstring says so, and in the demos the agent passed that limit on every time.

`find_boards.py` is a helper: give it company names and it tells you which
board each one uses, as lines you can paste into `companies.csv`.

## Why I built these (from my prompt logs)

**drift-check.** When I brainstorm with an AI, after several rounds of ideas
it easily ends up offering things that don't match what I wanted at the
start. In earlier assignments I kept restating my constraints:

- HW6 (Designer Lens): *"I want to do something more spatial."* and later
  *"Most of the ideas we've come up with so far are about people using the
  search function."*
- Project 2 (Napier's Rod Box): Prompt 4 *"I don't want it to be a chat AI."*,
  Prompt 6 *"no voice output either"*, Prompt 8 *"I don't want too much art
  work."*
- HW3 (World Oracle): the AI pitched an Iconify project and I had to ask
  *"In what sense is that a design tool?"* before it admitted it was just a
  search results page.

**design-jobs.** The agent can't reach live data, and what it knows from
memory goes out of date without warning:

- HW3: *"the query service was unreachable from the model's sandbox"* and
  *"The list goes stale silently."*
- HW6: *"Claude's environment couldn't reach Wikipedia, the embedding model
  download or Groq"*

Looking for an internship needs what is open *now*, which memory can't give.

## Install

Replace `<repo>` with the **absolute path** of this repo on your machine
(mine is `/Users/yubozhang/Documents/GitHub/agent-toolkit`, which is specific
to my laptop).

**Skill:**
```bash
ln -s <repo>/drift-check ~/.claude/skills/drift-check
```
(Or copy the `drift-check` folder into `~/.claude/skills/`.)

**MCP server:**
```bash
cd <repo>/design-jobs-mcp
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python server.py --try designer
claude mcp add --scope user --transport stdio design-jobs -- <repo>/design-jobs-mcp/.venv/bin/python <repo>/design-jobs-mcp/server.py
claude mcp list
```
The `--try` line is a quick test and should print real postings. The last
line should show `design-jobs … ✔ Connected`.

Notes:
- Register it with the **absolute path** of the venv's Python. Claude Code
  starts the server, not your terminal, so a bare `python3` may find a Python
  without `mcp` installed.
- `requirements.txt` pins `mcp>=2.3,<3`: mcp 2.x renamed the course
  example's `FastMCP` to `MCPServer`.
- python.org's Mac Python has no root certificates; the code uses `certifi`.
- To follow other companies, run `.venv/bin/python find_boards.py "Company"`
  and paste its output into `companies.csv`.

## Where I confirmed it works

- **Claude Code 2.1.319 on macOS.** The skill loads automatically and with
  `/drift-check`. The server shows `✔ Connected`, and the agent called the
  tool without being told its name. Screenshots in `demos/screenshots/`.
- Opus 5.5 did the work and Sonnet 5.5 ran the checker, each in its own
  Terminal window.
- **Not tested in Codex.** The skill folder follows the open standard, so it
  should work, and Codex registers servers in `~/.codex/config.toml`, but I
  didn't try it.

## Limits and next steps

- The three job boards mostly cover software companies. The physical and
  spatial companies I actually care about (Sonos, Rivian, Teenage
  Engineering, Nothing, Local Projects) aren't on them, so the tool can't see
  them. Next step: an aggregator API like Adzuna, or more boards.
- The checker isn't fully consistent on borderline items (see ITERATION.md).
- I found it genuinely useful. In Project 3 I'll use drift-check to keep
  checking that the AI and I stay on the same track, which helps the whole
  project's development.

## What I borrowed

- `drift-check`'s structure (a fixed output format plus rules that block
  known failures) follows the assignment's `spec-check` example.
- The MCP server started from the assignment's FastMCP example, updated to
  mcp 2.x's `MCPServer`.
- The public job board APIs of Greenhouse, Lever and Ashby.

## How I used AI

- **Claude (Opus 5.5, Claude desktop app):** found the
  evidence in my HW3–HW7 prompt logs; wrote the MCP server, `find_boards.py`
  and all three versions of `drift-check`; diagnosed the checker's mistakes.
- **Me:** chose the direction (a brainstorming-drift checker and a design job
  tool); decided to use Claude Code only, with Opus doing and Sonnet
  checking; ran and registered everything in the Terminal; ran both demos;
  judged whether each of the checker's findings was right and which fixes to
  make.
- Details in `prompt_log.md`.

## Files

| Path | What it is |
|---|---|
| `drift-check/SKILL.md` | The checker skill (v3) |
| `design-jobs-mcp/server.py` | The MCP server |
| `design-jobs-mcp/companies.csv` | Companies the tool searches |
| `design-jobs-mcp/find_boards.py` | Finds which board a company uses |
| `design-jobs-mcp/requirements.txt` | Dependencies |
| `tests/orange-test/SKILL.md` | Trivial skill used to confirm skills load |
| `demos/` | Full exported transcripts of both runs and every checker version |
| `DEMONSTRATION.md` | Evidence that it works |
| `ITERATION.md` | What failed and how I fixed it |
| `prompt_log.md` | Prompts and models used |
