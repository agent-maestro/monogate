#!/usr/bin/env python3
"""E3 — score the trap set, but ONLY against a key that matches its pre-committed hash.

## The seal, and why it is the whole experiment

A trap set scores the pipeline's ability to catch planted defects. That number is worth nothing if the
answer key could have been edited after the results came in. So:

  1. `e3_traps/manifest.json` commits `answer_key_sha256` BEFORE any trap is evaluated.
  2. The key file itself stays OUT of the repo (orchestrator holds it) until scoring.
  3. This script hashes the key it is handed and compares. A mismatch is a HARD FAILURE and nothing is
     scored -- not a warning, not a score-with-caveat. An unsealed experiment has no result.

This makes "adjust the key after seeing the results" mechanically detectable rather than a matter of
trust, which is the only form of integrity that survives the person checking it being the person who
would benefit.

## What it cannot see

It cannot detect a trap set that was authored badly -- 20 easy traps score the same as 20 hard ones.
Nor can it detect contamination: if the system under test saw the traps beforehand, the hash still
matches and the score is still meaningless. Contamination control is procedural (PROTOCOL.md E3) and
this gate does not substitute for it.

Usage:  score_traps.py --key /path/to/answer_key.json [--records e3_traps/records/]
        score_traps.py --verify-seal-only --key /path/to/answer_key.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
TRAPS = os.path.join(HERE, "e3_traps")
MANIFEST = os.path.join(TRAPS, "manifest.json")
CLASSES = ("TRUE", "SUBTLY_FALSE", "MISFORMALIZED")
STAGES = ("prover", "gates", "certifier", "adversarial_review")


def verify_seal(key_path: str) -> tuple[bool, str, str]:
    if not os.path.exists(MANIFEST):
        return False, "", "no manifest — nothing was ever sealed"
    man = json.load(open(MANIFEST))
    committed = man.get("answer_key_sha256", "")
    if not committed:
        return False, "", "manifest has no answer_key_sha256 — the set was never sealed"
    if not os.path.exists(key_path):
        return False, committed, f"key not found at {key_path}"
    actual = hashlib.sha256(open(key_path, "rb").read()).hexdigest()
    return actual == committed, committed, actual


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--key", required=True, help="answer_key.json, held outside the repo until scoring")
    ap.add_argument("--records", default=os.path.join(TRAPS, "records"))
    ap.add_argument("--verify-seal-only", action="store_true")
    a = ap.parse_args()

    print("E3 TRAP SCORING\n")
    print("1 SEAL")
    ok, committed, actual = verify_seal(a.key)
    print(f"    committed sha256 : {committed or '(none)'}")
    print(f"    key sha256       : {actual or '(unreadable)'}")
    if not ok:
        print("\n    [INVALID EXPERIMENT] the key does not match the hash committed before evaluation.")
        print("    NOTHING IS SCORED. A key that can change after the results are in is not a key,")
        print("    and a score computed from one is not a measurement. If the key was legitimately")
        print("    regenerated, the trap set must be re-sealed and re-run from scratch.")
        print("\nE3 TRAP SCORING: HARD FAILURE — seal broken")
        return 1
    print("    SEAL INTACT — the key is the one sealed before any trap was evaluated.\n")

    if a.verify_seal_only:
        print("E3 TRAP SCORING: SEAL VERIFIED (scoring not requested)")
        return 0

    key = json.load(open(a.key))
    planted = key.get("traps", {})
    if not planted:
        print("[UNAVAILABLE] the key contains no traps. This is instrument failure, not a zero score.")
        return 1

    if not os.path.isdir(a.records):
        print(f"[UNAVAILABLE] no evaluation records at {a.records}.")
        print("  A trap set with no records is unmeasured, NOT a score of zero.")
        return 1

    records = {}
    for f in sorted(os.listdir(a.records)):
        if f.endswith(".json"):
            r = json.load(open(os.path.join(a.records, f)))
            records[r["trap_id"]] = r

    missing = [t for t in planted if t not in records]
    if missing:
        print(f"[UNAVAILABLE] {len(missing)} trap(s) have no evaluation record: {missing[:5]}")
        print("  Reported as unmeasured. They are NOT counted as misses — an unrun trap and a")
        print("  missed trap are different facts, and folding one into the other flatters the score.")
        print()

    print("2 CATCH RATE BY PLANTED CLASS")
    by_class: dict[str, Counter] = {c: Counter() for c in CLASSES}
    for tid, cls in planted.items():
        if tid not in records:
            continue
        caught = records[tid].get("caught_by")
        by_class.setdefault(cls, Counter())
        by_class[cls]["total"] += 1
        by_class[cls]["caught" if caught else "missed"] += 1
        if caught:
            by_class[cls][f"by_{caught}"] += 1

    for c in CLASSES:
        v = by_class.get(c, Counter())
        tot = v.get("total", 0)
        if not tot:
            print(f"    {c:<15} no evaluated traps of this class (UNMEASURED, not 0%)")
            continue
        print(f"    {c:<15} caught {v.get('caught', 0)}/{tot}  "
              f"({100.0 * v.get('caught', 0) / tot:.0f}%)")
        for s in STAGES:
            n = v.get(f"by_{s}", 0)
            if n:
                print(f"        via {s}: {n}")

    print("\n3 STAGE THAT CAUGHT IT")
    stage_counts = Counter(records[t].get("caught_by") or "NONE" for t in planted if t in records)
    for s in list(STAGES) + ["NONE"]:
        if stage_counts.get(s):
            print(f"    {s:<20} {stage_counts[s]}")

    n_eval = sum(1 for t in planted if t in records)
    print(f"\n    evaluated {n_eval}/{len(planted)} traps; {len(missing)} unmeasured")
    print("\nE3 TRAP SCORING: COMPLETE")
    print("  Blind to: trap difficulty, and to contamination. A hash match does not mean the system")
    print("  under test had not already seen the traps — that control is procedural.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
