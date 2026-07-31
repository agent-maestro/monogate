#!/usr/bin/env python3
"""GATE: the E1 ledger only ever grows, and a session that reports wins without work is SUSPECT.

## What this gate checks

  1. SCHEMA      — every ledger file validates against ledger_schema.json.
  2. APPEND-ONLY — versus git HEAD: no session deleted, no entry or finding removed or MUTATED.
                   Growth is fine; anything else is not.
  3. SUSPECT     — a session with findings and ZERO logged interventions is flagged.

## What this gate structurally CANNOT see, stated because a gate's blindness belongs next to the gate

**It cannot detect a session that was never logged at all.** Append-only detects tampering with the
record; it cannot detect an absence from it. This is E1's principal bias risk, because the sessions
least likely to be logged are the least interesting ones — and dropping those inflates
findings-per-session, the headline ratio. The SUSPECT flag is a partial mitigation, not a fix: it
catches "logged the win, skipped the work" and is blind to "skipped the session".

It also cannot see whether a `kind` was classified honestly. `taste` vs `correction` is a human
judgement, and this gate checks only that the value is in the enum.

## Why SUSPECT is not a failure

A findings-only session is suspicious, not invalid — a session can legitimately record a finding whose
interventions were logged under a different session id. So SUSPECT prints loudly, is counted in the
summary, and exits non-zero ONLY under --strict. What it must never do is stay quiet.

Exit: 0 pass · 1 a check failed · 2 the gate could not run
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER_DIR = os.path.join(HERE, "ledger")
# --ledger-dir exists so the append-only branch can be DEMONSTRATED against a committed fixture
# without a specimen session polluting the live ledger E1 actually reports on. A specimen that
# contaminates the dataset it validates is not a specimen.
for _i, _a in enumerate(sys.argv):
    if _a == "--ledger-dir" and _i + 1 < len(sys.argv):
        LEDGER_DIR = os.path.abspath(sys.argv[_i + 1])
SCHEMA = os.path.join(HERE, "ledger_schema.json")
KINDS = {"direction", "correction", "taste", "mechanical"}
CLASSES = {"closure", "surprise", "falsification", "dead_end"}
ARMS = {"baseline", "E2-ai", "E2-human"}

# AMENDMENT 1 took effect at this instant -- the moment `ledger.py log` began REQUIRING `--actor`.
# Entries stamped before it legitimately have no actor and report as `unrecorded`; entries stamped
# after it and lacking one mean the CLI was bypassed. The constant is the amendment's actual commit
# time, not a rounded hour: a guessed cutoff convicted two pre-amendment entries on the first run.
AMENDMENT_2_TS = "2026-07-30T18:50:23"   # derived from the clock at amendment time, not typed from memory of it
AMENDMENT_1_TS = "2026-07-30T18:36:38"


def validate(name: str, d: object) -> list[str]:
    """Hand-rolled against ledger_schema.json's constraints -- no jsonschema dependency in CI."""
    errs: list[str] = []
    if not isinstance(d, dict):
        return [f"{name}: not an object"]
    for k in ("session_id", "date", "arm", "entries", "findings"):
        if k not in d:
            errs.append(f"{name}: missing {k!r}")
    if d.get("arm") not in ARMS:
        errs.append(f"{name}: arm {d.get('arm')!r} not in {sorted(ARMS)}")
    for i, e in enumerate(d.get("entries", []) or []):
        if e.get("kind") not in KINDS:
            errs.append(f"{name}: entries[{i}].kind {e.get('kind')!r} invalid")
        if not e.get("description"):
            errs.append(f"{name}: entries[{i}] has no description")
        # AMENDMENT 1: actor required on entries logged after 2026-07-30. Pre-amendment entries
        # legitimately lack it and must NOT be failed -- they are `unrecorded`, not malformed.
        # AMENDMENT 2: catch-class entries must say WHERE the catch fired.
        if "via" in e and e["via"] not in ("structural", "spontaneous"):
            errs.append(f"{name}: entries[{i}].via {e.get('via')!r} invalid")
        if (e.get("kind") in ("correction", "taste") and "via" not in e
                and e.get("ts", "") > AMENDMENT_2_TS):
            errs.append(f"{name}: entries[{i}] is a catch logged after AMENDMENT 2 with no `via` — "
                        f"cannot distinguish the discipline executing from the outer loop automating")
        if "actor" in e and e["actor"] not in ("human", "ai", "unclear"):
            errs.append(f"{name}: entries[{i}].actor {e.get('actor')!r} invalid")
        if "actor" not in e and (e.get("ts", "") > AMENDMENT_1_TS):
            errs.append(f"{name}: entries[{i}] logged after AMENDMENT 1 with no actor — the claim "
                        f"under test is about the HUMAN outer loop, so an unattributed entry "
                        f"cannot support it")
    for i, f in enumerate(d.get("findings", []) or []):
        if f.get("class") not in CLASSES:
            errs.append(f"{name}: findings[{i}].class {f.get('class')!r} invalid")
        if not f.get("artifact_link"):
            errs.append(f"{name}: findings[{i}] has no artifact_link "
                        f"(house rule 6: no claim without an artifact)")
    return errs


def git_show(rel: str) -> dict | None:
    """The file as of HEAD, or None if it is new. A git failure raises -- never 'looks unchanged'."""
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE,
                          capture_output=True, text=True).stdout.strip()
    p = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=root,
                       capture_output=True, text=True)
    if p.returncode != 0:
        if "does not exist" in p.stderr or "exists on disk" in p.stderr or "unknown revision" in p.stderr:
            return None
        return None
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return None


def main() -> int:
    strict = "--strict" in sys.argv
    if not os.path.exists(SCHEMA):
        print(f"[GATE COULD NOT RUN] no schema at {SCHEMA}")
        return 2
    inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=HERE,
                            capture_output=True, text=True)
    if inside.returncode != 0:
        print("[GATE COULD NOT RUN] not a git work tree — append-only cannot be checked against "
              "history, and an unrunnable check must not read as a passing one.")
        return 2

    print("E1 LEDGER GATE\n")
    errors = suspect = 0
    files = sorted(f for f in os.listdir(LEDGER_DIR)) if os.path.isdir(LEDGER_DIR) else []
    files = [f for f in files if f.endswith(".json")]

    print(f"1 SCHEMA  ({len(files)} ledger file(s))")
    parsed: dict[str, dict] = {}
    for f in files:
        try:
            parsed[f] = json.load(open(os.path.join(LEDGER_DIR, f)))
        except json.JSONDecodeError as e:
            print(f"  FAIL  {f}: invalid JSON ({e})"); errors += 1
            continue
        for e in validate(f, parsed[f]):
            print(f"  FAIL  {e}"); errors += 1
    print()

    print("2 APPEND-ONLY  (vs git HEAD)")
    repo_root = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE,
                               capture_output=True, text=True).stdout.strip()
    # cwd=repo_root, NOT cwd=HERE. The path handed to ls-tree is repo-root-relative, and git
    # resolves pathspecs against the CWD -- so running it from HERE looked for
    # experiments/automation/experiments/automation/..., found nothing, compared nothing, and the
    # gate PASSED a mutated ledger. Caught by the firing specimen, which is what specimens are for:
    # the check was not weak, it was pointed at an empty set and could not tell the difference.
    rel_dir = os.path.relpath(LEDGER_DIR, repo_root)
    prev_files = subprocess.run(["git", "ls-tree", "--name-only", "-r", "HEAD", rel_dir + "/"],
                                cwd=repo_root, capture_output=True, text=True).stdout.split()
    for rel in prev_files:
        if not rel.endswith(".json"):
            continue
        base = os.path.basename(rel)
        if base not in parsed:
            print(f"  FAIL  {base}: existed at HEAD and is now GONE — ledgers are append-only")
            errors += 1
            continue
        old = git_show(rel)
        if old is None:
            continue
        new = parsed[base]
        for field in ("entries", "findings"):
            o, n = old.get(field, []), new.get(field, [])
            if len(n) < len(o):
                print(f"  FAIL  {base}: {field} shrank {len(o)} -> {len(n)}"); errors += 1
                continue
            if n[:len(o)] != o:
                print(f"  FAIL  {base}: existing {field} were MUTATED — append-only means the "
                      f"prefix is immutable, not merely that the file grew"); errors += 1
        if old.get("arm") != new.get("arm"):
            print(f"  FAIL  {base}: arm changed {old.get('arm')!r} -> {new.get('arm')!r}; arm "
                  f"assignment must not follow the result"); errors += 1
    print(f"    {len(prev_files)} file(s) at HEAD compared\n")

    print("3 SUSPECT  (findings with zero logged interventions)")
    for f, d in parsed.items():
        if d.get("findings") and not d.get("entries"):
            print(f"  SUSPECT  {f}: {len(d['findings'])} finding(s), 0 interventions logged.")
            suspect += 1
    if not suspect:
        print("    none")
    else:
        print(f"    {suspect} suspect session(s). Unlogged work is E1's principal bias risk;")
        print("    this flag catches 'logged the win, skipped the work' and is BLIND to")
        print("    'skipped the session'. See the gate docstring.")
    print()

    print("=" * 64)
    if errors or (strict and suspect):
        print(f"E1 LEDGER GATE: FAIL — {errors} error(s), {suspect} suspect.")
        return 1
    print(f"E1 LEDGER GATE: PASS — {len(parsed)} session(s), {suspect} suspect (non-blocking).")
    print("  Blind to: sessions never logged at all, and to whether a kind was classified honestly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
