#!/usr/bin/env python3
"""GATE: the E2 arm schedule is frozen once the first E2 session is logged.

The schedule decides which sessions are AI-selected and which are human-selected. If it can change
after sessions have run, the ablation measures nothing: whoever holds the file can move a bad session
into the other arm. So the hash is pinned at first use and compared thereafter.

FREEZE POINT: the moment any ledger file has arm E2-ai or E2-human. Before that, the schedule is still
being designed and may change freely. After it, `e2_schedule.lock` holds the sha256 and any difference
is a hard failure.

BLIND TO: whether the sessions were actually run in the assigned arm. This gate compares a file to its
hash; it cannot see whether a session labelled E2-ai really had its target chosen by the AI. That
remains an honesty requirement on the operator, and PROTOCOL.md states it as one rather than pretending
the gate covers it.

Exit: 0 pass · 1 the schedule moved after freeze · 2 the gate could not run
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEDULE = os.path.join(HERE, "e2_schedule.json")
LOCK = os.path.join(HERE, "e2_schedule.lock")
LEDGER_DIR = os.path.join(HERE, "ledger")


def digest(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def e2_sessions_logged() -> list[str]:
    out = []
    if not os.path.isdir(LEDGER_DIR):
        return out
    for f in sorted(os.listdir(LEDGER_DIR)):
        if not f.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(LEDGER_DIR, f)))
        except Exception:  # noqa: BLE001 -- an unreadable ledger is the ledger gate's problem
            continue
        if d.get("arm", "").startswith("E2-"):
            out.append(f)
    return out


def main() -> int:
    print("E2 SCHEDULE FREEZE GATE\n")
    logged = e2_sessions_logged()

    if not os.path.exists(SCHEDULE):
        if logged:
            print(f"  FAIL  {len(logged)} E2 session(s) logged but no schedule file exists.")
            print("        An arm assignment with no committed schedule is not an ablation.")
            return 1
        print("  no schedule yet, no E2 sessions yet — nothing to freeze.")
        print("E2 SCHEDULE FREEZE GATE: PASS (pre-registration phase)")
        return 0

    cur = digest(SCHEDULE)
    print(f"  schedule sha256 : {cur}")
    print(f"  E2 sessions     : {len(logged)}")

    if not logged:
        print("\n  Not yet frozen — no E2 session has run, so the schedule may still change.")
        print("  It freezes automatically on the first E2 session logged.")
        print("E2 SCHEDULE FREEZE GATE: PASS (not yet frozen)")
        return 0

    if not os.path.exists(LOCK):
        json.dump({"sha256": cur, "frozen_because": logged[0]}, open(LOCK, "w"), indent=2)
        print(f"\n  FROZEN NOW: first E2 session ({logged[0]}) is logged.")
        print(f"  wrote {os.path.basename(LOCK)} — commit it in the same commit as that session.")
        print("E2 SCHEDULE FREEZE GATE: PASS (freeze established)")
        return 0

    lock = json.load(open(LOCK))
    if lock.get("sha256") != cur:
        print(f"\n  FAIL  schedule changed after freeze.")
        print(f"        locked : {lock.get('sha256')}")
        print(f"        now    : {cur}")
        print(f"        frozen because: {lock.get('frozen_because')}")
        print("        Arm assignment must not follow the results. If this change is legitimate,")
        print("        record an amendment in PROTOCOL.md and re-freeze deliberately.")
        print("E2 SCHEDULE FREEZE GATE: FAIL")
        return 1

    print("\n  schedule matches the lock recorded at first E2 session.")
    print("E2 SCHEDULE FREEZE GATE: PASS")
    print("  Blind to: whether a session labelled E2-ai really had its target chosen by the AI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
