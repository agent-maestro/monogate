#!/usr/bin/env python3
"""E2 — generate the arm-assignment schedule ONCE, then freeze it.

The schedule says which upcoming sessions are AI-selected and which are human-selected. It is generated
before any E2 session runs and never regenerated, because choosing arms as you go — in a study you are
also scoring — is how an ablation stops measuring anything. `check_e2_schedule_frozen.py` enforces that
mechanically: the schedule's hash is pinned once the first E2 session is logged.

The seed is recorded so the assignment is reproducible and auditable: anyone can re-derive the schedule
and confirm it was not hand-picked.

Usage:  e2_schedule.py generate --n 20 [--seed 20260730] [--mode alternating|random]
        e2_schedule.py show
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEDULE = os.path.join(HERE, "e2_schedule.json")
ARMS = ("E2-ai", "E2-human")


def digest(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def cmd_generate(a: argparse.Namespace) -> int:
    if os.path.exists(SCHEDULE):
        print(f"[REFUSED] {os.path.basename(SCHEDULE)} already exists.")
        print("  The schedule is generated ONCE. Regenerating it after sessions have run would let")
        print("  arm assignment follow the results, which is the single thing this file prevents.")
        print("  If it genuinely must change, record an amendment in PROTOCOL.md first and say why.")
        return 2
    seed = a.seed if a.seed is not None else int(dt.date.today().strftime("%Y%m%d"))
    if a.mode == "alternating":
        assign = [ARMS[i % 2] for i in range(a.n)]
    else:
        rng = random.Random(seed)
        # Balanced then shuffled: a pure coin flip can hand one arm 14 of 20 sessions, and an
        # imbalance that large is a power problem we would discover only after running them.
        assign = [ARMS[0]] * (a.n // 2) + [ARMS[1]] * (a.n - a.n // 2)
        rng.shuffle(assign)
    doc = {
        "schema": "monogate-e2-schedule.v1",
        "generated": dt.date.today().isoformat(),
        "mode": a.mode,
        "seed": seed,
        "n": a.n,
        "note": ("Frozen at first use by check_e2_schedule_frozen.py. Seed recorded so the assignment "
                 "is re-derivable by anyone who doubts it was not hand-picked."),
        "sessions": [{"index": i + 1, "arm": arm, "session_id": None} for i, arm in enumerate(assign)],
    }
    json.dump(doc, open(SCHEDULE, "w"), indent=2)
    print(f"wrote {os.path.basename(SCHEDULE)}: n={a.n} mode={a.mode} seed={seed}")
    print(f"  sha256 = {digest(SCHEDULE)}")
    print("  COMMIT THIS FILE NOW, before the first E2 session.")
    return 0


def cmd_show(a: argparse.Namespace) -> int:
    if not os.path.exists(SCHEDULE):
        print("[UNAVAILABLE] no schedule generated yet. This is not 'no sessions scheduled' —")
        print("  it is 'the instrument does not exist'. Run: e2_schedule.py generate --n N")
        return 2
    d = json.load(open(SCHEDULE))
    print(f"E2 SCHEDULE  mode={d['mode']} seed={d['seed']} n={d['n']} generated={d['generated']}")
    print(f"  sha256 = {digest(SCHEDULE)}")
    counts: dict[str, int] = {}
    for s in d["sessions"]:
        counts[s["arm"]] = counts.get(s["arm"], 0) + 1
    for arm in ARMS:
        print(f"  {arm:<10} {counts.get(arm, 0)}")
    assigned = sum(1 for s in d["sessions"] if s["session_id"])
    print(f"  assigned so far: {assigned}/{d['n']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--n", type=int, default=20)
    g.add_argument("--seed", type=int)
    g.add_argument("--mode", choices=["alternating", "random"], default="random")
    g.set_defaults(fn=cmd_generate)
    s = sub.add_parser("show")
    s.set_defaults(fn=cmd_show)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
