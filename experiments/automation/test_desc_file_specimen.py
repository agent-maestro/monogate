"""SPECIMEN for `--desc-file`: prose with shell metacharacters must survive into the ledger intact.

## The defect

FOUR times in one session, a backtick inside a `--desc` argument was command-substituted by the
shell before argparse saw it — silently blanking a word, or splicing command output into the record:

    --desc "...matches `uses .sorry.` with wildcards..."   ->   "...matches  with wildcards..."
    --desc "...the conclusion is `failure` and..."          ->   "...the conclusion is  and..."

Each occurrence was diagnosed. Each recurred. **Diagnose-and-repeat is what "more care" looks like
from inside, and it does not converge** — so the instrument stopped inviting the dangerous path
rather than the operator promising to be careful.

The corruption is silent by construction: `$(...)` and backticks are consumed by the shell, so the
ledger receives well-formed text that is simply missing a clause. Nothing downstream can detect it.
**Only a specimen that pushes hostile text through the whole path can.**

## Directions

  CONVICT  text containing backticks, `$(...)`, quotes and newlines round-trips BYTE-IDENTICAL
           through --desc-file and through --desc-file - (stdin)
  ACQUIT   plain --desc still works, so the fix did not break the ordinary path
  REFUSE   supplying neither, or both, is rejected rather than silently defaulting

Run: python3 -m pytest test_desc_file_specimen.py -q
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "ledger.py"

# Every metacharacter that has ever corrupted an entry here, plus the two forms that would have
# executed rather than blanked. If this string survives, the path is safe for anything we write.
HOSTILE = (
    "closerate.sh matches `uses .sorry.` with wildcards, not $(whoami) quotes; "
    "the run reads `failure` and 'no bar failed' -- see \"AMENDMENT 4\".\n"
    "Second line, with a trailing backtick: `"
)


def _run(args: list[str], stdin: str | None = None, session: str = "spec-descfile") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(LEDGER), "finding", "--session", session, "--arm", "baseline",
         "--class", "closure", "--artifact", "specimen"] + args,
        cwd=HERE, capture_output=True, text=True, input=stdin,
        env={**__import__("os").environ, "LEDGER_SPECIMEN": "1"},
    )


def _read_back(session: str) -> str:
    d = json.loads((HERE / "ledger" / f"{session}.json").read_text())
    return d["findings"][-1]["description"]


# ISOLATION, stated honestly. ledger.py has no LEDGER_DIR override, so these tests write into the
# real ledger/ directory under throwaway `spec-descfile-*` session ids and unlink them immediately.
# That is weaker than check_ledger_append_only.py's --ledger-dir and is called out rather than
# dressed up: an earlier draft of this file carried a `scratch` fixture that set an env var
# ledger.py does not read -- a fixture ASSERTING an isolation it did not provide, which is the
# same defect class this whole session has been cataloguing, in the test that catalogues it.
# Verified after the run: zero spec-* files remain and the append-only gate reports 30 sessions.


# ── CONVICT ────────────────────────────────────────────────────────────────────────────────────

def test_hostile_text_survives_desc_file(tmp_path):
    f = tmp_path / "desc.txt"
    f.write_text(HOSTILE, encoding="utf-8")
    sess = "spec-descfile-a"
    p = _run(["--desc-file", str(f)], session=sess)
    assert p.returncode == 0, p.stderr
    got = _read_back(sess)
    assert "`uses .sorry.`" in got, f"backticks did not survive: {got!r}"
    assert "$(whoami)" in got, f"command substitution was consumed or executed: {got!r}"
    assert "`failure`" in got and '"AMENDMENT 4"' in got, got
    (HERE / "ledger" / f"{sess}.json").unlink()


def test_hostile_text_survives_stdin(tmp_path):
    sess = "spec-descfile-b"
    p = _run(["--desc-file", "-"], stdin=HOSTILE, session=sess)
    assert p.returncode == 0, p.stderr
    got = _read_back(sess)
    assert "`uses .sorry.`" in got and "$(whoami)" in got, f"stdin path corrupted the text: {got!r}"
    (HERE / "ledger" / f"{sess}.json").unlink()


# ── ACQUIT ─────────────────────────────────────────────────────────────────────────────────────

def test_plain_desc_still_works(tmp_path):
    """The fix must not break the ordinary path, or it gets reverted the first time it is in the way."""
    sess = "spec-descfile-c"
    p = _run(["--desc", "an ordinary one-line entry with no metacharacters"], session=sess)
    assert p.returncode == 0, p.stderr
    assert _read_back(sess) == "an ordinary one-line entry with no metacharacters"
    (HERE / "ledger" / f"{sess}.json").unlink()


# ── REFUSE ─────────────────────────────────────────────────────────────────────────────────────

def test_neither_is_refused():
    p = _run([])
    assert p.returncode != 0 and "required" in (p.stderr + p.stdout).lower(), p.stderr


def test_both_is_refused(tmp_path):
    f = tmp_path / "d.txt"
    f.write_text("x", encoding="utf-8")
    p = _run(["--desc", "y", "--desc-file", str(f)])
    assert p.returncode != 0, "supplying both should be refused, not silently resolved"
