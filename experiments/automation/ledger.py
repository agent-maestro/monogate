#!/usr/bin/env python3
"""E1 — intervention ledger. Log interventions and findings; compute the report.

## Why the report is computed and never templated

PROTOCOL.md house rule 3 is enumerate-then-count: the tool that enumerated produces the summary. This
matters more here than anywhere else in the program, because E1's whole output is ratios, and a ratio
transcribed by hand into prose is a number with no mechanism behind it. Every figure `report` prints is
derived from the ledger files it just read, in the same run.

## Why UNAVAILABLE is not zero

A session with no ledger file is **not** a session with zero interventions. `report` counts sessions it
can read and states how many it could not, separately. Folding an unreadable session into the
denominator as a zero would bias exactly the ratio E1 exists to measure.

Usage:
    ledger.py log     --session S --arm baseline --kind direction --desc "..." [--artifact URL] [--boundary]
    ledger.py finding --session S --arm baseline --class closure  --desc "..."  --artifact URL
    ledger.py report  [--json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER_DIR = os.path.join(HERE, "ledger")
KINDS = ("direction", "correction", "taste", "mechanical")
CLASSES = ("closure", "surprise", "falsification", "dead_end")
ARMS = ("baseline", "E2-ai", "E2-human")


def path_for(session: str) -> str:
    safe = "".join(c for c in session if c.isalnum() or c in "-_")
    if safe != session:
        print(f"[REFUSED] session id {session!r} has characters outside [A-Za-z0-9-_]", file=sys.stderr)
        raise SystemExit(2)
    return os.path.join(LEDGER_DIR, f"{safe}.json")


def load_or_init(session: str, arm: str) -> dict:
    p = path_for(session)
    if os.path.exists(p):
        d = json.load(open(p))
        if d["arm"] != arm:
            # Changing a session's arm after the fact would let arm assignment follow the result.
            print(f"[REFUSED] session {session} is already arm {d['arm']!r}; refusing to relabel as "
                  f"{arm!r}. Arm assignment is fixed at first write on purpose.", file=sys.stderr)
            raise SystemExit(2)
        return d
    return {"session_id": session, "date": dt.date.today().isoformat(), "arm": arm,
            "entries": [], "findings": []}


def save(d: dict) -> str:
    os.makedirs(LEDGER_DIR, exist_ok=True)
    p = path_for(d["session_id"])
    json.dump(d, open(p, "w"), indent=2)
    return p


def cmd_log(a: argparse.Namespace) -> int:
    d = load_or_init(a.session, a.arm)
    e = {"ts": dt.datetime.now().isoformat(timespec="seconds"), "kind": a.kind,
         "actor": a.actor, "description": a.desc}
    if a.artifact:
        e["artifact_link"] = a.artifact
    if a.boundary:
        e["boundary"] = True
    d["entries"].append(e)
    p = save(d)
    flag = "  [boundary — flagged, counted separately]" if a.boundary else ""
    print(f"logged {a.kind} to {os.path.relpath(p, HERE)} "
          f"({len(d['entries'])} entries, {len(d['findings'])} findings){flag}")
    return 0


def cmd_finding(a: argparse.Namespace) -> int:
    d = load_or_init(a.session, a.arm)
    d["findings"].append({"description": a.desc, "class": getattr(a, "class"),
                          "artifact_link": a.artifact})
    p = save(d)
    print(f"logged {getattr(a, 'class')} finding to {os.path.relpath(p, HERE)} "
          f"({len(d['entries'])} entries, {len(d['findings'])} findings)")
    if not d["entries"]:
        print("  NOTE: this session has findings and ZERO interventions. The append-only gate will")
        print("  flag it SUSPECT. That is not a bug — see PROTOCOL.md E1 'Known blindness'.")
    return 0


def read_all() -> tuple[list[dict], list[str]]:
    """Returns (sessions, unreadable). Unreadable is reported, never silently counted as empty."""
    sessions, unreadable = [], []
    if not os.path.isdir(LEDGER_DIR):
        return sessions, unreadable
    for f in sorted(os.listdir(LEDGER_DIR)):
        if not f.endswith(".json"):
            continue
        try:
            sessions.append(json.load(open(os.path.join(LEDGER_DIR, f))))
        except Exception as e:  # noqa: BLE001
            unreadable.append(f"{f}: {type(e).__name__}")
    return sessions, unreadable


def pct(n: int, d: int) -> str:
    return f"{100.0 * n / d:5.1f}%" if d else "  n/a "


def cmd_report(a: argparse.Namespace) -> int:
    sessions, unreadable = read_all()
    if not sessions and not unreadable:
        print("E1 LEDGER REPORT\n\n  no sessions logged yet — the ledger is live but empty.")
        print("  This is a real zero (no files), not an unavailable measurement.")
        return 0

    kinds = Counter(e["kind"] for s in sessions for e in s["entries"])
    actors = Counter(e.get("actor", "unrecorded") for s in sessions for e in s["entries"])
    human_kinds = Counter(e["kind"] for s in sessions for e in s["entries"]
                          if e.get("actor") == "human")
    boundary = sum(1 for s in sessions for e in s["entries"] if e.get("boundary"))
    classes = Counter(f["class"] for s in sessions for f in s["findings"])
    by_arm: dict[str, dict] = {}
    for s in sessions:
        a_ = by_arm.setdefault(s["arm"], {"sessions": 0, "entries": 0, "findings": Counter()})
        a_["sessions"] += 1
        a_["entries"] += len(s["entries"])
        a_["findings"].update(f["class"] for f in s["findings"])

    n_e, n_f = sum(kinds.values()), sum(classes.values())

    if a.json:
        print(json.dumps({
            "sessions": len(sessions), "unreadable": unreadable,
            "interventions": dict(kinds), "boundary_flagged": boundary,
            "findings": dict(classes),
            "by_arm": {k: {"sessions": v["sessions"], "entries": v["entries"],
                           "findings": dict(v["findings"])} for k, v in by_arm.items()},
            "series": [{"session": s["session_id"], "date": s["date"], "arm": s["arm"],
                        "entries": len(s["entries"]), "findings": len(s["findings"])}
                       for s in sessions],
        }, indent=2))
        return 1 if unreadable else 0

    print("E1 LEDGER REPORT")
    print(f"  every number below is computed from {len(sessions)} ledger file(s) read this run\n")

    if unreadable:
        print(f"  [INSTRUMENT FAILURE] {len(unreadable)} ledger file(s) could not be read:")
        for u in unreadable:
            print(f"      {u}")
        print("  These are NOT counted as zero. Ratios below exclude them and are therefore")
        print("  measurements of a partial ledger — treat accordingly.\n")

    print("INTERVENTIONS BY KIND")
    for k in KINDS:
        print(f"  {k:<12} {kinds.get(k, 0):>4}   {pct(kinds.get(k, 0), n_e)}")
    print(f"  {'TOTAL':<12} {n_e:>4}")
    print(f"  boundary-flagged: {boundary} ({pct(boundary, n_e)} of entries) — judgement calls, "
          f"counted but separable\n")

    print("BY ACTOR  (AMENDMENT 1 — the claim under test is about the HUMAN outer loop)")
    for k in ("human", "ai", "unclear", "unrecorded"):
        if actors.get(k):
            note = "  <- pre-amendment; NOT folded into any actor" if k == "unrecorded" else ""
            print(f"  {k:<12} {actors[k]:>4}   {pct(actors[k], n_e)}{note}")
    hk = sum(human_kinds.values())
    print(f"\n  HUMAN-ONLY intervention mix (the figure the central claim rests on):")
    if hk:
        for k in KINDS:
            print(f"    {k:<12} {human_kinds.get(k, 0):>4}   {pct(human_kinds.get(k, 0), hk)}")
    else:
        print("    [UNAVAILABLE] no entries carry actor=human yet. This is not 'humans did nothing' —")
        print("    it is 'the ledger cannot yet say'. Do not read the mix above as the human mix.")
    print()

    print("FINDINGS BY CLASS")
    for c in CLASSES:
        print(f"  {c:<14} {classes.get(c, 0):>4}   {pct(classes.get(c, 0), n_f)}")
    print(f"  {'TOTAL':<14} {n_f:>4}\n")

    print("BY ARM")
    print(f"  {'arm':<10} {'sessions':>8} {'entries':>8} {'findings':>9} {'find/sess':>10}")
    for arm in ARMS:
        if arm not in by_arm:
            continue
        v = by_arm[arm]
        tot = sum(v["findings"].values())
        print(f"  {arm:<10} {v['sessions']:>8} {v['entries']:>8} {tot:>9} "
              f"{tot / v['sessions']:>10.2f}")
    print()

    print("FINDINGS PER SESSION (time series)")
    for s in sessions:
        print(f"  {s['date']}  {s['session_id']:<24} {s['arm']:<9} "
              f"{len(s['entries']):>3} int  {len(s['findings']):>2} find")

    return 1 if unreadable else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    lg = sub.add_parser("log", help="append an intervention")
    lg.add_argument("--session", required=True)
    lg.add_argument("--arm", required=True, choices=ARMS)
    lg.add_argument("--kind", required=True, choices=KINDS)
    lg.add_argument("--desc", required=True)
    lg.add_argument("--artifact")
    lg.add_argument("--actor", required=True, choices=("human", "ai", "unclear"),
                    help="WHO intervened. Required since AMENDMENT 1: the claim under test is about "
                         "the HUMAN outer loop, so an unattributed `taste` entry cannot support it.")
    lg.add_argument("--boundary", action="store_true",
                    help="the `?` flag: the kind was a judgement call. Flag it, never drop it.")
    lg.set_defaults(fn=cmd_log)

    fd = sub.add_parser("finding", help="append a finding")
    fd.add_argument("--session", required=True)
    fd.add_argument("--arm", required=True, choices=ARMS)
    fd.add_argument("--class", required=True, choices=CLASSES, dest="class")
    fd.add_argument("--desc", required=True)
    fd.add_argument("--artifact", required=True, help="house rule 6: no claim without an artifact")
    fd.set_defaults(fn=cmd_finding)

    rp = sub.add_parser("report", help="compute the report (never templated)")
    rp.add_argument("--json", action="store_true")
    rp.set_defaults(fn=cmd_report)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
