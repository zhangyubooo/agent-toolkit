"""Find which public job board (Greenhouse / Lever / Ashby) a company uses.

Usage:  python3 find_boards.py "Figma" "Teenage Engineering" ...
        (no names = try the starter list below)

Prints one CSV line per board found, ready to paste into companies.csv,
plus how many of its open jobs have "design" in the title. Companies on
other systems (Workday, their own site...) can't be searched by the tool.
Only uses the standard library, so any python3 works.
"""

import json
import ssl
import sys
import urllib.error
import urllib.request

BOARD_URLS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "lever": "https://api.lever.co/v0/postings/{slug}?mode=json",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
}

try:
    import certifi  # present in the .venv (comes with mcp)
    CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CTX = ssl.create_default_context()

STARTER = ["Figma", "Pinterest", "Dropbox", "Spotify", "Notion", "Duolingo", "Discord",
           "Framer", "Snap", "Sonos", "Rivian", "Peloton", "Niantic", "IDEO",
           "Teenage Engineering", "Nothing", "Local Projects"]


def slugs_for(name):
    base = name.lower().strip()
    return list(dict.fromkeys([base.replace(" ", ""), base.replace(" ", "-")]))


def titles(ats, data):
    if ats == "lever":
        return [j.get("text", "") for j in data]
    return [j.get("title", "") for j in data.get("jobs", [])]


for name in sys.argv[1:] or STARTER:
    hits, errors = [], set()
    for ats, url in BOARD_URLS.items():
        for slug in slugs_for(name):
            try:
                req = urllib.request.Request(url.format(slug=slug), headers={"User-Agent": "find-boards (student project)"})
                with urllib.request.urlopen(req, timeout=10, context=CTX) as r:
                    t = titles(ats, json.load(r))
            except urllib.error.HTTPError:
                continue  # 404 = this company is not on this board: expected
            except urllib.error.URLError as e:
                errors.add(str(e.reason)[:80])  # NOT expected: say so
                continue
            except (ValueError, TimeoutError) as e:
                errors.add(type(e).__name__)
                continue
            if t:  # an empty board usually means a wrong or unused slug
                design = sum("design" in x.lower() for x in t)
                hits.append(f"{name},{ats},{slug}    # {len(t)} jobs, {design} with 'design'")
    if hits:
        print("\n".join(hits))
    elif errors:
        print(f"# {name}: COULD NOT CHECK ({'; '.join(sorted(errors))})")
    else:
        print(f"# {name}: not found on Greenhouse/Lever/Ashby")
