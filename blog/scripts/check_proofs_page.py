#!/usr/bin/env python3
"""GATE: /proofs quotes monogate-lean truthfully -- verbatim sources, right lines, right counts.

WHY THIS EXISTS. src/data/proofs.ts feeds /proofs and /proofs.lean.txt. They promise "every block is a
verbatim copy of the source" and print per-file statement and sorry counts, and nothing checked either.
On 2026-09-12, audited against monogate-lean 9c6164b:
  * 17 of the 39 flagship sources no longer matched their files;
  * 4 flagships linked the wrong line;
  * Universality.lean's count was off by one;
  * the page's own breakdown (50 + 179 + 237 = 466) did not add up to the 478 it printed.

WHAT IS CHECKED, against the monogate-lean commit that scripts/lean_claims.json pins (read with
`git show`, never from a working tree):
  * each flagship `source` occurs verbatim in its file;
  * each flagship `line` is the line that declares that theorem or lemma;
  * each file's `total` equals its theorem and lemma declarations, and `sorries` its `sorry` tokens
    (comments stripped), with `ok` meaning `sorries === 0`.
`original` is a hand classification and is not checked. Whether each theorem is actually proved is
check_claims.py's job (scripts/lean_claims.json); this gate keeps the page's quotations and counts honest.

    python3 scripts/check_proofs_page.py              # the gate
    python3 scripts/check_proofs_page.py --self-test  # it must fire on planted mismatches
Exit: 0 consistent | 1 a mismatch | 2 could not evaluate (no registry, pin, or repository).
"""
from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

BLOG = Path(__file__).resolve().parents[1]
PROOFS_TS = BLOG / "src" / "data" / "proofs.ts"
REGISTRY = BLOG / "scripts" / "lean_claims.json"
LEAN_TREE = "../../monogate-lean"
_GIT_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
_DECL = re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:(?:private|protected|noncomputable)\s+)*(?:theorem|lemma)\s", re.M)
_FLAGSHIP = re.compile(r"name: '([^']+)',\s*\n\s*line: (\d+),")

Show = Callable[[str], "str | None"]


def strip_comments(src: str) -> str:
    src = re.sub(r"/-.*?-/", lambda m: "\n" * m.group(0).count("\n"), src, flags=re.S)
    return re.sub(r"--[^\n]*", "", src)


def untemplate(s: str) -> str:
    """A TypeScript template literal's body, as the string it denotes."""
    return s.replace("\\${", "${").replace("\\`", "`").replace("\\\\", "\\")


def parse_proofs_ts(text: str) -> list[dict]:
    starts = [m.start() for m in re.finditer(r"\n    file: '", text)] + [len(text)]
    files = []
    for a, b in zip(starts, starts[1:]):
        block = text[a:b]
        head = re.search(r"file: '([^']+)'.*?original: (\d+), total: (\d+), sorries: (\d+), ok: (true|false)", block, re.S)
        if head is None:
            continue
        flagships = []
        for m in _FLAGSHIP.finditer(block):
            src = re.search(r"source: `((?:\\.|[^`\\])*)`", block[m.end():], re.S)
            flagships.append({"name": m.group(1), "line": int(m.group(2)),
                              "source": untemplate(src.group(1)) if src else None})
        files.append({"file": head.group(1), "total": int(head.group(3)), "sorries": int(head.group(4)),
                      "ok": head.group(5) == "true", "flagships": flagships})
    return files


def check(files: list[dict], show: Show) -> list[str]:
    problems: list[str] = []
    for f in files:
        src = show(f"MonogateEML/{f['file']}")
        if src is None:
            problems.append(f"{f['file']}: not in monogate-lean at the pinned commit")
            continue
        code = strip_comments(src)
        decls = len(_DECL.findall(code))
        sorries = len(re.findall(r"\bsorry\b", code))
        if f["total"] != decls:
            problems.append(f"{f['file']}: total {f['total']}, but the file declares {decls} theorems and lemmas")
        if f["sorries"] != sorries:
            problems.append(f"{f['file']}: sorries {f['sorries']}, but the file has {sorries}")
        if f["ok"] != (f["sorries"] == 0):
            problems.append(f"{f['file']}: ok is {str(f['ok']).lower()} while sorries is {f['sorries']}")
        lines = src.splitlines()
        for fl in f["flagships"]:
            short = fl["name"].split(".")[-1]
            decl = re.compile(rf"^(?:@\[[^\]]*\]\s*)?(?:(?:private|protected)\s+)?(?:theorem|lemma)\s+{re.escape(short)}(?![\w'.])")
            if fl["source"] is None or fl["source"].strip() not in src:
                problems.append(f"{f['file']}: flagship {fl['name']} is not a verbatim copy of the file")
            if not (1 <= fl["line"] <= len(lines) and decl.match(lines[fl["line"] - 1])):
                actual = next((i + 1 for i, line in enumerate(lines) if decl.match(line)), None)
                problems.append(f"{f['file']}: flagship {fl['name']} links line {fl['line']}, declared at line {actual}")
    return problems


def self_test(files: list[dict], show: Show) -> int:
    """Each planted mismatch must be reported, and the unmodified page must be clean."""
    def planted(mutate: Callable[[list[dict]], None]) -> list[str]:
        mutated = copy.deepcopy(files)
        mutate(mutated)
        return check(mutated, show)

    target = next(f for f in files if f["flagships"])
    cases = {
        "a count off by one": (lambda fs: fs[files.index(target)].__setitem__("total", target["total"] + 1), "total"),
        "a sorry count that disagrees": (lambda fs: fs[files.index(target)].__setitem__("sorries", target["sorries"] + 1), "sorries"),
        "a flagship line off by one": (lambda fs: fs[files.index(target)]["flagships"][0].__setitem__("line", target["flagships"][0]["line"] + 1), "links line"),
        "a flagship source edited": (lambda fs: fs[files.index(target)]["flagships"][0].__setitem__("source", target["flagships"][0]["source"] + " -- edited"), "verbatim"),
    }
    failed = [name for name, (mutate, needle) in cases.items() if not any(needle in p for p in planted(mutate))]
    clean = check(files, show)
    ok = not failed and not clean
    print(f"SELF-TEST {'OK' if ok else 'FAILED'} ({len(cases)} planted mismatches fire; the page as committed is clean)")
    for name in failed:
        print(f"  did not fire: {name}")
    for p in clean:
        print(f"  committed page is not clean: {p}")
    return 0 if ok else 1


def main() -> int:
    if not REGISTRY.exists():
        print("PROOFS PAGE: UNAVAILABLE -- scripts/lean_claims.json is missing, so there is no pinned commit")
        return 2
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rev = next((env["sources"][LEAN_TREE]["revision"] for env in registry.get("environments", {}).values()
                if LEAN_TREE in env.get("sources", {})), None)
    repo = (BLOG / LEAN_TREE).resolve()
    if rev is None:
        print(f"PROOFS PAGE: UNAVAILABLE -- scripts/lean_claims.json pins no `sources` entry for {LEAN_TREE}")
        return 2
    if subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{rev}^{{commit}}"],
                      capture_output=True, env=_GIT_ENV).returncode != 0:
        print(f"PROOFS PAGE: UNAVAILABLE -- monogate-lean commit {rev[:12]} is not in {repo}")
        return 2

    def show(path: str) -> str | None:
        run = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True, text=True, env=_GIT_ENV)
        return run.stdout if run.returncode == 0 else None

    text = PROOFS_TS.read_text(encoding="utf-8")
    files = parse_proofs_ts(text)
    parsed = sum(len(f["flagships"]) for f in files)
    present = len(_FLAGSHIP.findall(text))
    if not files or parsed != present:
        print(f"PROOFS PAGE: FAIL -- parsed {len(files)} files and {parsed} of {present} flagships from proofs.ts; "
              f"a gate that skips entries proves nothing about them")
        return 1
    if "--self-test" in sys.argv[1:]:
        return self_test(files, show)
    problems = check(files, show)
    for p in problems:
        print(f"  {p}")
    print(f"PROOFS PAGE: {'CONSISTENT' if not problems else 'FAIL'}  ({len(files)} files, {parsed} flagships, "
          f"monogate-lean {rev[:9]})")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
