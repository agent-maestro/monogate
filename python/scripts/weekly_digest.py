"""weekly_digest.py — generate a markdown digest of changes across
the three public Monogate repos for distribution (LinkedIn, HN, email).

Reads from:
    D:/monogate            (public — blog + python package)
    D:/monogate-dev        (public — Next.js app)
    D:/monogate-research   (PRIVATE — only the *count* of commits is
                            reported, never file names or messages)

Usage:
    python python/scripts/weekly_digest.py --since "7 days ago"
    python python/scripts/weekly_digest.py --since "2026-04-16"
    python python/scripts/weekly_digest.py            # default 7d

Output: markdown to stdout; save to --out weekly_digest.md if provided.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


PUBLIC_REPOS = [
    ("monogate",      Path("D:/monogate")),
    ("monogate-dev",  Path("D:/monogate-dev")),
]
PRIVATE_REPOS = [
    ("monogate-research", Path("D:/monogate-research")),
]


def git(repo: Path, *args: str) -> str:
    res = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=False, encoding="utf-8", errors="replace",
    )
    return res.stdout


def commits(repo: Path, since: str) -> list[dict]:
    fmt = "%H%x1f%h%x1f%an%x1f%ad%x1f%s"
    raw = git(repo, "log", f"--since={since}", f"--pretty=format:{fmt}", "--date=short")
    out = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) < 5:
            continue
        out.append({
            "hash": parts[0], "short": parts[1],
            "author": parts[2], "date": parts[3], "subject": parts[4],
        })
    return out


def new_blog_posts(repo: Path, since: str) -> list[dict]:
    """Detect new files under blog/src/pages/blog/ since <since>."""
    raw = git(repo, "log", f"--since={since}",
              "--name-status", "--pretty=format:%H")
    posts = []
    for block in raw.split("\n\n"):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        for ln in lines[1:]:
            m = re.match(r"^(A|M)\s+(blog/src/pages/blog/[^\s]+)$", ln)
            if not m:
                continue
            path = m.group(2)
            if path.endswith(".md") or path.endswith(".astro"):
                posts.append({"status": m.group(1), "path": path})
    # dedupe on path, keeping the latest status ("A" beats "M")
    seen: dict[str, dict] = {}
    for p in posts:
        cur = seen.get(p["path"])
        if cur is None or (cur["status"] == "M" and p["status"] == "A"):
            seen[p["path"]] = p
    return sorted(seen.values(), key=lambda p: p["path"])


def lean_counts(repo: Path) -> dict:
    """Count Lean files + sorries in the monogate repo (not the separate
    monogate-lean repo; that would require a separate clone)."""
    # We use the card's verification block as the source of truth.
    import json
    card = repo / "capability_card_public.json"
    if not card.exists():
        return {"clean": None, "partial": None, "sorries": None}
    try:
        data = json.loads(card.read_text(encoding="utf-8"))
        v = data.get("verification", {})
        return {
            "clean":   v.get("lean_clean_files"),
            "partial": v.get("lean_partial_files"),
            "sorries": v.get("lean_sorries_total"),
        }
    except Exception:
        return {"clean": None, "partial": None, "sorries": None}


def pypi_version(repo: Path) -> str | None:
    pyproj = repo / "python" / "pyproject.toml"
    if not pyproj.exists():
        return None
    txt = pyproj.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', txt, re.MULTILINE)
    return m.group(1) if m else None


def section_header(level: int, text: str) -> str:
    return "\n" + "#" * level + " " + text + "\n"


def main():
    ap = argparse.ArgumentParser(description="Weekly Monogate digest")
    ap.add_argument("--since", default="7 days ago",
                    help="git-log --since argument (default '7 days ago')")
    ap.add_argument("--out", default=None,
                    help="Optional file to write the digest to")
    args = ap.parse_args()

    lines: list[str] = []
    lines.append(f"# Monogate Weekly Digest — since {args.since}")
    lines.append("")

    # ── public: commits + new posts ─────────────────────────────────────
    public_commit_count = 0
    for name, path in PUBLIC_REPOS:
        cs = commits(path, args.since)
        public_commit_count += len(cs)
        lines.append(section_header(2, f"{name}  ({len(cs)} commits)"))
        if not cs:
            lines.append("_no commits in window_")
            continue
        for c in cs:
            # First line of subject only
            lines.append(f"- **{c['date']}** `{c['short']}`  {c['subject']}")
        # New blog posts surfaced separately for the blog repo
        if name == "monogate":
            posts = new_blog_posts(path, args.since)
            if posts:
                lines.append("")
                lines.append("**New / updated blog posts:**")
                for p in posts:
                    slug = Path(p["path"]).stem
                    lines.append(
                        f"- {p['status']}  `{p['path']}`  -> https://monogate.org/blog/{slug}"
                    )

    # ── private: aggregate count only ──────────────────────────────────
    lines.append(section_header(2, "monogate-research  (aggregate)"))
    priv_total = 0
    for name, path in PRIVATE_REPOS:
        cs = commits(path, args.since)
        priv_total += len(cs)
    lines.append(
        f"- {priv_total} private commits in window "
        "(subjects intentionally omitted; research repo contains IP)."
    )

    # ── verification snapshot ──────────────────────────────────────────
    lines.append(section_header(2, "Verification snapshot"))
    mon = PUBLIC_REPOS[0][1]
    lc = lean_counts(mon)
    ver = pypi_version(mon)
    lines.append(f"- Lean files: **{lc['clean']} clean** + {lc['partial']} partial ({lc['sorries']} sorries total)")
    lines.append(f"- PyPI: `pip install monogate=={ver}`")
    lines.append("- CapCard: https://monogate.org/capability_card.json (v3)")

    # ── footer ─────────────────────────────────────────────────────────
    lines.append(section_header(2, "Distribution checklist"))
    lines.append("- [ ] LinkedIn post (copy from Verification snapshot)")
    lines.append("- [ ] Hacker News: only if new blog post crosses the value threshold")
    lines.append("- [ ] Email to Odrzywołek: if a new Lean result shipped")
    lines.append("- [ ] X/Twitter: one thread per new landing-page change")

    markdown = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).write_text(markdown, encoding="utf-8")
        print(f"wrote {args.out}  ({len(markdown)} bytes)")
    else:
        sys.stdout.write(markdown)


if __name__ == "__main__":
    main()
