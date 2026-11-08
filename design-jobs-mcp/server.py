"""design-jobs MCP server: one tool, search_design_jobs.

Searches the public job boards (Greenhouse, Lever, Ashby) of the companies
listed in companies.csv. These boards need no API key, but they only work
per company: there is no "search every job on the internet" endpoint. So the
tool can only ever see the companies in companies.csv, and it says so.

Run by an MCP client (Claude Code) over stdio. Never print() to stdout
while running as a server: stdout is the protocol channel. Logs go to stderr.
"""

import csv
import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

# mcp 2.x renamed FastMCP to MCPServer (the course example uses the 1.x name)
from mcp.server.mcpserver import MCPServer

# ---------------------------------------------------------------------------
# 1. Settings
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent
COMPANIES_FILE = HERE / "companies.csv"
TIMEOUT_SEC = 10        # per company board
MAX_RESULTS = 30        # keep the agent's context small
# whole words only: a plain substring check matched "International" as "intern"
INTERN_RE = re.compile(r"\b(intern|interns|internship|internships|co-?op)\b", re.IGNORECASE)

BOARD_URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
}


def log(msg: str) -> None:
    """Log to stderr, never stdout (stdout carries the MCP protocol)."""
    print(f"[design-jobs] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# 2. Reading the company list
# ---------------------------------------------------------------------------

def load_companies() -> list[dict]:
    """Rows of companies.csv: name, ats, slug. Lines starting with # are skipped."""
    with open(COMPANIES_FILE, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["name"] and not r["name"].startswith("#")]
    # anything after "#" in the slug column is a note (find_boards.py adds one)
    return [{"name": r["name"].strip(), "ats": r["ats"].strip().lower(),
             "slug": r["slug"].split("#")[0].strip()} for r in rows]


# ---------------------------------------------------------------------------
# 3. Fetching one board and normalising it
#    Each ATS names its fields differently; every job becomes the same dict.
# ---------------------------------------------------------------------------

def make_ssl_context() -> ssl.SSLContext:
    """python.org's Mac Python ships without root certificates, so plain
    urllib fails with CERTIFICATE_VERIFY_FAILED. certifi (installed with mcp)
    provides them."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL_CONTEXT = make_ssl_context()


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "design-jobs-mcp (student project)"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC, context=SSL_CONTEXT) as resp:
        return json.load(resp)


def date_only(value) -> str:
    """Greenhouse/Ashby give ISO strings, Lever gives milliseconds since 1970."""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    return str(value or "")[:10]


def normalise(company: dict, data) -> list[dict]:
    ats, name = company["ats"], company["name"]
    jobs = []
    if ats == "greenhouse":
        for j in data.get("jobs", []):
            jobs.append({
                "company": name, "title": j.get("title", ""),
                "location": (j.get("location") or {}).get("name", ""),
                "team": "", "type": "",
                "posted": date_only(j.get("first_published") or j.get("updated_at")),
                "url": j.get("absolute_url", ""),
            })
    elif ats == "lever":
        for j in data:
            cat = j.get("categories") or {}
            jobs.append({
                "company": name, "title": j.get("text", ""),
                "location": cat.get("location", ""), "team": cat.get("team", ""),
                "type": " ".join(x for x in [cat.get("commitment", ""), j.get("workplaceType", "")] if x),
                "posted": date_only(j.get("createdAt")),
                "url": j.get("hostedUrl", ""),
            })
    elif ats == "ashby":
        for j in data.get("jobs", []):
            if j.get("isListed") is False:
                continue
            jobs.append({
                "company": name, "title": j.get("title", ""),
                "location": j.get("location", ""),
                "team": " / ".join(x for x in [j.get("department", ""), j.get("team", "")] if x),
                "type": " ".join(x for x in [j.get("employmentType", ""), j.get("workplaceType", "")] if x),
                "posted": date_only(j.get("publishedAt")),
                "url": j.get("jobUrl", ""),
            })
    return jobs


def fetch_company(company: dict):
    """Returns (jobs, error). An error is reported to the agent, not hidden."""
    template = BOARD_URLS.get(company["ats"])
    if not template:
        return [], f"unknown ats '{company['ats']}'"
    try:
        return normalise(company, fetch_json(template.format(slug=company["slug"]))), None
    except urllib.error.HTTPError as e:
        return [], f"HTTP {e.code}"
    except urllib.error.URLError as e:  # DNS, refused, SSL certificate...
        return [], f"URLError: {e.reason}"
    except Exception as e:  # timeout, bad JSON
        return [], type(e).__name__


# ---------------------------------------------------------------------------
# 4. Filtering
# ---------------------------------------------------------------------------

def matches(job: dict, keywords: list[str], location: str, internship_only: bool) -> bool:
    title_team = f"{job['title']} {job['team']}".lower()
    if keywords and not any(k in title_team for k in keywords):
        return False
    if location:
        where = f"{job['location']} {job['type']}".lower()
        if not any(part.strip() in where for part in location.lower().split(",") if part.strip()):
            return False
    if internship_only:
        if not INTERN_RE.search(f"{job['title']} {job['type']}"):
            return False
    return True


# ---------------------------------------------------------------------------
# 5. The MCP tool
# ---------------------------------------------------------------------------

mcp = MCPServer("design-jobs")


@mcp.tool()
def search_design_jobs(keywords: str, location: str = "", internship_only: bool = False) -> str:
    """Search live job postings at the companies listed in my companies.csv.

    Use this when the user wants real, current job or internship openings
    (design, UX, creative technologist, etc.) instead of guesses from memory.

    IMPORTANT LIMITS: it only searches the companies in companies.csv (their
    public Greenhouse / Lever / Ashby boards). "No results" means none of THOSE
    companies match, not that no such jobs exist anywhere. Every result line
    comes from the live board; do not add jobs, companies or details that are
    not in the output.

    Args:
        keywords: comma-separated words matched against the job title and team,
            e.g. "designer, design, creative technologist". Case-insensitive.
        location: optional comma-separated places matched against location and
            workplace type, e.g. "new york, remote". Empty = anywhere.
        internship_only: true to keep only intern / internship / co-op roles.

    Returns: one line per job (company | title | location | team | type |
    posted date | url), newest first, at most 30, followed by which companies
    were searched and which boards failed.
    """
    companies = load_companies()
    kw = [k.strip().lower() for k in keywords.split(",") if k.strip()]

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(fetch_company, companies))

    found, failed = [], []
    for company, (jobs, error) in zip(companies, results):
        if error:
            failed.append(f"{company['name']} ({error})")
        found += [j for j in jobs if matches(j, kw, location, internship_only)]
    found.sort(key=lambda j: j["posted"], reverse=True)
    log(f"keywords={kw} location={location!r} intern={internship_only} -> {len(found)} matches")

    lines = [f"{len(found)} matching posting(s)" + (f", showing newest {MAX_RESULTS}" if len(found) > MAX_RESULTS else "") + ":"]
    for j in found[:MAX_RESULTS]:
        lines.append(" | ".join([j["company"], j["title"], j["location"] or "-", j["team"] or "-",
                                 j["type"] or "-", j["posted"] or "-", j["url"]]))
    ok = [c["name"] for c, (_, e) in zip(companies, results) if not e]
    lines.append(f"\nSearched {len(ok)} companies: {', '.join(ok)}")
    if failed:
        lines.append(f"Could not read: {', '.join(failed)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 6. Entry point
#    `python server.py`            -> run as an MCP server (what Claude Code does)
#    `python server.py --try ...`  -> call the tool once by hand, for testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--try":
        print(search_design_jobs(" ".join(sys.argv[2:]) or "design"))
    else:
        mcp.run()
