#!/usr/bin/env python3
"""GATE: the accountability page cannot outlive its evidence.

## What this checks, and what it deliberately does not

`/accountability` grades this project against the Leiden Declaration. Every grade cites an artifact.
The failure mode that would matter most is not a wrong grade — it is a grade whose artifact quietly
stopped existing, leaving prose that reads as verified and is not. So this gate checks the things a
reader would otherwise have to take on trust:

  1. SCHEMA      — the data file has the shape the page renders from.
  2. LINKS       — every artifact URL resolves (2xx/3xx). A 404 or a timeout fails the build.
  3. STALENESS   — no row's `last_verified` is older than 120 days.
  4. MET RIGOUR  — a MET row must have >= 1 artifact and no unresolved `TODO:` placeholder.
                   A row containing `TODO:` anywhere CANNOT be graded MET. This is the rule that
                   stops the page's strongest claims from resting on links that were never written.
  5. HONESTY     — PARTIAL and NOT_YET rows must state a gap AND an upgrade condition. A downgrade
                   with no named gap is a mood, not a grade.

**It does NOT check that a grade is correct.** No script can. It checks that the evidence a grade
points at is reachable, current, and non-placeholder — which is the part that rots silently. The
grade itself is re-read by a human against its artifact at each quarterly re-verification.

UNAVAILABLE IS FAILURE, in one direction only: a link that cannot be reached fails the build, and a
network outage therefore fails it too. That is deliberate and matches the rest of this project's
gates — an offline run must never be readable as "all links fine". Pass `--offline` to skip section 2
explicitly, which prints a loud banner and is not permitted in CI.

Run:  python3 scripts/check_accountability.py [--offline]
Exit: 0 all checks pass · 1 a check failed · 2 the gate could not run
"""
from __future__ import annotations

import concurrent.futures
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "src", "data", "accountability.json")
MAX_AGE_DAYS = 120
GRADES = {"MET", "PARTIAL", "NOT_YET", "NA"}
NEEDS_GAP = {"PARTIAL", "NOT_YET"}
UA = "monogate-accountability-linkcheck"


def fail(msg: str) -> None:
    print(f"  FAIL  {msg}")


def check_url(url: str) -> tuple[str, int | str]:
    """HEAD, falling back to GET — some hosts (arXiv, Zenodo) refuse HEAD but serve GET fine.

    Treating a HEAD-refusing host as a dead link would make the gate cry wolf, and a gate that cries
    wolf gets switched off, which is the only way this one can actually fail.
    """
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                return url, r.status
        except urllib.error.HTTPError as e:
            if method == "GET" or e.code not in (403, 405, 501):
                return url, e.code
        except Exception as e:  # noqa: BLE001 -- any transport failure is a failure
            if method == "GET":
                return url, f"{type(e).__name__}"
    return url, "unreachable"


def main() -> int:
    offline = "--offline" in sys.argv
    if not os.path.exists(DATA):
        print(f"[GATE COULD NOT RUN] no data file at {DATA}")
        return 2
    try:
        data = json.load(open(DATA))
    except json.JSONDecodeError as e:
        print(f"[GATE COULD NOT RUN] {DATA} is not valid JSON: {e}")
        return 2

    errors = 0
    print("ACCOUNTABILITY GATE\n")

    # ---- 1. schema -------------------------------------------------------
    print("1 SCHEMA")
    if data.get("schema") != "monogate-accountability.v1":
        fail(f"unexpected schema tag {data.get('schema')!r}"); errors += 1
    rows = data.get("rows") or []
    if not rows:
        fail("no rows"); errors += 1
    seen_ids: set[str] = set()
    for r in rows:
        rid = r.get("id", "<no id>")
        for k in ("id", "recommendation", "asks", "grade", "summary", "artifacts", "last_verified"):
            if k not in r:
                fail(f"row {rid}: missing required field {k!r}"); errors += 1
        if r.get("grade") not in GRADES:
            fail(f"row {rid}: grade {r.get('grade')!r} not in {sorted(GRADES)}"); errors += 1
        if rid in seen_ids:
            fail(f"duplicate row id {rid!r} — anchors must be unique"); errors += 1
        seen_ids.add(rid)
    for c in data.get("changelog", []):
        if c.get("row") not in seen_ids:
            fail(f"changelog references unknown row {c.get('row')!r}"); errors += 1
    print(f"    {len(rows)} rows, {len(data.get('changelog', []))} changelog entries\n")

    # ---- 2. MET rigour + honesty ----------------------------------------
    print("2 GRADE RIGOUR")
    for r in rows:
        rid, grade = r.get("id"), r.get("grade")
        blob = json.dumps(r)
        if "TODO:" in blob:
            if grade == "MET":
                fail(f"row {rid}: graded MET but contains an unresolved TODO: placeholder"); errors += 1
            else:
                print(f"    note  row {rid}: contains TODO: (allowed for {grade}, blocks MET)")
        if grade == "MET" and not r.get("artifacts"):
            fail(f"row {rid}: MET with no artifact"); errors += 1
        if grade in NEEDS_GAP:
            if not r.get("gap"):
                fail(f"row {rid}: {grade} must name a gap"); errors += 1
            if not r.get("upgrade_condition"):
                fail(f"row {rid}: {grade} must state what would change the grade"); errors += 1
    print()

    # ---- 3. staleness ----------------------------------------------------
    print("3 STALENESS")
    today = dt.date.today()
    for r in rows:
        try:
            age = (today - dt.date.fromisoformat(r["last_verified"])).days
        except (KeyError, ValueError):
            fail(f"row {r.get('id')}: last_verified is missing or not ISO-8601"); errors += 1
            continue
        if age > MAX_AGE_DAYS:
            fail(f"row {r.get('id')}: last verified {age}d ago (max {MAX_AGE_DAYS})"); errors += 1
    print(f"    oldest row: {max((today - dt.date.fromisoformat(r['last_verified'])).days for r in rows if r.get('last_verified'))}d "
          f"(limit {MAX_AGE_DAYS}d)\n")

    # ---- 4. links --------------------------------------------------------
    print("4 LINKS")
    urls: list[str] = []
    for r in rows:
        urls += [a["url"] for a in r.get("artifacts", []) if "url" in a]
    d = data.get("declaration", {})
    urls += [u for u in (d.get("url"), d.get("doi_url")) if u]
    internal = sorted({u for u in urls if u.startswith("/") or "monogate.org" in u})
    external = sorted({u for u in urls if u not in internal})

    # INTERNAL LINKS ARE RESOLVED AGAINST THE BUILD, NOT FETCHED. The first version of this gate
    # skipped them as "served by this build" -- and its own firing specimen proved that wrong: a
    # deliberately dead monogate.org link sailed through. A page that links to its own incident
    # report must fail BEFORE deploy if that report was never built, which HTTP-checking the live
    # site cannot do (the live site still serves yesterday's build). So: check the artifact we are
    # about to ship, not the one already shipped.
    dist = os.path.join(HERE, "..", "dist")
    if os.path.isdir(dist):
        for u in internal:
            path = u.split("monogate.org", 1)[-1] if "monogate.org" in u else u
            path = path.split("#")[0].split("?")[0].strip("/")
            if not path:
                continue
            if not (os.path.exists(os.path.join(dist, path, "index.html"))
                    or os.path.exists(os.path.join(dist, path))):
                fail(f"internal link has no page in dist/: /{path}"); errors += 1
        print(f"    {len(internal)} internal links resolved against dist/")
    else:
        fail("dist/ not found — build the site before running this gate, or internal "
             "links go unchecked (which is how a dead one shipped once already)")
        errors += 1

    if offline:
        print("    ##################################################################")
        print("    # --offline: EXTERNAL LINKS NOT CHECKED. This run proves nothing  #")
        print("    # about whether the evidence is reachable. Not permitted in CI.  #")
        print("    ##################################################################\n")
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            for url, status in ex.map(check_url, external):
                ok = isinstance(status, int) and 200 <= status < 400
                if not ok:
                    fail(f"{status}  {url}"); errors += 1
        print(f"    {len(external)} external URLs checked\n")

    # ---- verdict ---------------------------------------------------------
    print("=" * 66)
    if errors:
        print(f"ACCOUNTABILITY GATE: FAIL — {errors} problem(s).")
        print("  A page that grades itself must be able to fail. This is that.")
        return 1
    print("ACCOUNTABILITY GATE: PASS")
    print("  Scope: the evidence each grade points at is reachable, current and")
    print("  non-placeholder. NOT that any grade is correct — that is re-read by a")
    print("  human against its artifact at each quarterly re-verification.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
