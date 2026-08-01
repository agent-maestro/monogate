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
CATCH_KINDS = ("correction", "taste")   # AMENDMENT 2: these are the "catch" kinds `via` describes
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
    # AMENDMENT 4: `preventive` becomes a REQUIRED ternary on catch-class entries rather than an
    # optional boolean. AMENDMENT 3 made it optional, and a cross-derivation on 2026-07-31 measured
    # 3 flagged entries against 13 whose text named a decline/refusal/stop-before-execution — a 4x
    # undercount, because an optional flag applied ad hoc by the party writing the entries is not a
    # count of anything. Absence must now be impossible, so `false` means "declared not preventive"
    # rather than "nobody said".
    if a.kind in CATCH_KINDS and a.preventive is None:
        print(f"[REFUSED] one of --preventive / --not-preventive is required for {a.kind!r} "
              f"(AMENDMENT 4). The optional form under-counted preventives 4x, because a flag that "
              f"may be omitted is applied by whoever remembers it — and the party writing the entry "
              f"is the party the count flatters. Absence and `false` are different facts.",
              file=sys.stderr)
        raise SystemExit(2)
    if a.kind in CATCH_KINDS and not a.via:
        print(f"[REFUSED] --via is required for {a.kind!r} (AMENDMENT 2). A catch that does not say "
              f"whether it fired inside a human-installed structure or arose unprompted cannot "
              f"distinguish the discipline executing from the outer loop automating — and that "
              f"distinction is unrecoverable once the session is over.", file=sys.stderr)
        raise SystemExit(2)
    d = load_or_init(a.session, a.arm)
    e = {"ts": dt.datetime.now().isoformat(timespec="seconds"), "kind": a.kind,
         "actor": a.actor, "description": a.desc}
    if a.via:
        e["via"] = a.via
    if a.preventive is not None:
        e["preventive"] = a.preventive
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


def cmd_dual(a: argparse.Namespace) -> int:
    """AMENDMENT 6 — the human's INDEPENDENT label for an entry already logged by the AI.

    Written to a SEPARATE file (`ledger/dual/<session>.json`), never into the entry, because the
    ledger is append-only and because a second labeller who can edit the first labeller's record is
    not a second labeller. Agreement is computed by `report`, not asserted here.
    """
    print("=" * 78, file=sys.stderr)
    print("AMENDMENT 6 — THIS COMMAND IS FOR THE HUMAN. AN AI-SUPPLIED DUAL LABEL IS", file=sys.stderr)
    print("VACUOUS AND WORSE THAN NONE: it manufactures agreement with the labeller it", file=sys.stderr)
    print("was built to audit, and the resulting agreement figure would then be quoted", file=sys.stderr)
    print("as a correction factor. Nothing here can enforce that; it is an attestation,", file=sys.stderr)
    print("the same grade as `actor`, and it belongs on the same list of limits.", file=sys.stderr)
    print("=" * 78, file=sys.stderr)
    d = load_or_init(a.session, a.arm)
    if a.index < 0 or a.index >= len(d["entries"]):
        print(f"[REFUSED] session {a.session!r} has {len(d['entries'])} entries; "
              f"index {a.index} is out of range.", file=sys.stderr)
        raise SystemExit(2)
    ddir = os.path.join(LEDGER_DIR, "dual")
    os.makedirs(ddir, exist_ok=True)
    p = os.path.join(ddir, f"{a.session}.json")
    cur = json.load(open(p)) if os.path.exists(p) else {"session_id": a.session, "labels": []}
    if any(l["index"] == a.index for l in cur["labels"]):
        print(f"[REFUSED] entry {a.index} already dual-labelled. A second label revised after "
              f"seeing the disagreement is not an independent label.", file=sys.stderr)
        raise SystemExit(2)
    ai = d["entries"][a.index]
    cur["labels"].append({"ts": dt.datetime.now().isoformat(timespec="seconds"),
                          "index": a.index, "human_kind": a.kind, "human_actor": a.actor,
                          "ai_kind": ai["kind"], "ai_actor": ai.get("actor", "unrecorded"),
                          "note": a.note or ""})
    json.dump(cur, open(p, "w"), indent=2)
    agree = (a.kind == ai["kind"]) and (a.actor == ai.get("actor"))
    print(f"dual-labelled entry {a.index} of {a.session}: "
          f"human={a.kind}/{a.actor}  ai={ai['kind']}/{ai.get('actor','unrecorded')}  "
          f"{'AGREE' if agree else '*** DISAGREE ***'}")
    print(f"  {len(cur['labels'])} of {len(d['entries'])} entries in this session dual-labelled")
    return 0


def dual_agreement() -> tuple[int, int, list[str]]:
    """Inter-rater agreement over every dual-labelled entry. Returns (agreed, total, notes)."""
    ddir = os.path.join(LEDGER_DIR, "dual")
    if not os.path.isdir(ddir):
        return 0, 0, []
    agreed = total = 0
    detail: list[str] = []
    for f in sorted(os.listdir(ddir)):
        if not f.endswith(".json"):
            continue
        for l in json.load(open(os.path.join(ddir, f)))["labels"]:
            total += 1
            if l["human_kind"] == l["ai_kind"] and l["human_actor"] == l["ai_actor"]:
                agreed += 1
            else:
                detail.append(f"{f[:-5]}[{l['index']}]  human {l['human_kind']}/{l['human_actor']}"
                              f"  vs  ai {l['ai_kind']}/{l['ai_actor']}")
    return agreed, total, detail


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
    preventive_n = sum(1 for s in sessions for e in s["entries"] if e.get("preventive"))
    ai_catch_via = Counter(e.get("via", "unrecorded") for s in sessions for e in s["entries"]
                           if e.get("actor") == "ai" and e["kind"] in CATCH_KINDS)
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

    agreed, dtotal, ddetail = dual_agreement()
    print("!" * 78)
    if dtotal:
        agree_pct = 100.0 * agreed / dtotal   # NOT `pct` -- that is a module-level function used
                                              # earlier in this same body, and rebinding the name
                                              # made it local for the WHOLE function, so the
                                              # INTERVENTIONS BY KIND table above crashed.
        print(f"INTER-RATER AGREEMENT (AMENDMENT 6): {agreed}/{dtotal} = {agree_pct:.0f}% "
              f"over dual-labelled entries")
        for line in ddetail[:6]:
            print(f"    DISAGREE  {line}")
        if len(ddetail) > 6:
            print(f"    … and {len(ddetail) - 6} more")
        print(f"  The DISAGREEMENT RATE is itself a finding: 'how differently do the human and")
        print(f"  the AI perceive who did what' is a sharper question than the ratio it corrupts.")
        print(f"  n={dtotal} is small; this corrects nothing yet, it only starts measuring.")
    else:
        print("INTER-RATER AGREEMENT (AMENDMENT 6): [UNAVAILABLE] no entries dual-labelled yet.")
        print("  Not zero agreement — UNMEASURED. `ledger.py dual` is the instrument.")
    print()
    print("CONFOUND — READ BEFORE THE TABLE BELOW. THE BY-ACTOR RATIO IS NOT YET A")
    print("MEASUREMENT, AND MORE SESSIONS WILL NOT MAKE IT ONE.")
    print()
    print("  Two hypotheses are OBSERVATIONALLY EQUIVALENT in this data:")
    print("    (a) human interventions really are overwhelmingly `direction` — the")
    print("        central claim's cleanest confirmation; or")
    print("    (b) the AI logs its own catches generously and compresses the human's")
    print("        terse redirections into `direction` by default.")
    print()
    print("  THE CONFOUND IS IN THE LABELLING FUNCTION, NOT THE SAMPLE SIZE. The")
    print("  classifier is a party to the dispute. More sessions logged by the same")
    print("  classifier converge on the SAME BIASED RATIO WITH TIGHTER ERROR BARS —")
    print("  the most dangerous kind of wrong number, which is a precise one.")
    print()
    print("  Resolved only by a second labeller. Two are in progress: the retrospective")
    print("  (inter-rater agreement on the overlap set = the correction factor) and")
    print("  DUAL-LABELLING going forward (`ledger.py dual`). Until one reports, this")
    print("  ratio must not be quoted without this block attached.")
    print("!" * 78)
    print()
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

    print("AI CATCHES BY VIA  (AMENDMENT 2 — where the chain terminates)")
    tot_ai = sum(ai_catch_via.values())
    if tot_ai:
        for k in ("structural", "spontaneous", "unrecorded"):
            if ai_catch_via.get(k):
                print(f"  {k:<14} {ai_catch_via[k]:>4}   {pct(ai_catch_via[k], tot_ai)}")
        st, sp = ai_catch_via.get("structural", 0), ai_catch_via.get("spontaneous", 0)
        if st and not sp:
            print("  READ: every AI catch so far fired inside a human-installed structure. That is")
            print("  the discipline executing, NOT the outer loop automating. The distinction is the")
            print("  refined claim's whole content — do not report AI catch counts without it.")
    else:
        print("  [UNAVAILABLE] no AI catch-class entries carry via yet.")
    print()

    catch_n = sum(1 for s in sessions for e in s["entries"] if e["kind"] in CATCH_KINDS)
    undeclared = sum(1 for s in sessions for e in s["entries"]
                     if e["kind"] in CATCH_KINDS and "preventive" not in e)
    print(f"PREVENTIVE CATCHES  (AMENDMENT 3/4) : {preventive_n} declared true "
          f"of {catch_n} catch-class entries")
    if undeclared:
        print(f"  [PARTIAL] {undeclared} catch entries predate AMENDMENT 4 and declare NOTHING. "
              f"They are UNDECLARED,")
        print("  not false. The optional-flag era under-counted preventives 4x (3 flagged vs 13")
        print("  described); any tally over the pre-amendment span must derive from descriptions,")
        print("  not from this field. See ledger/MIGRATIONS.md.")
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
    lg.add_argument("--via", choices=("structural", "spontaneous"),
                    help="AMENDMENT 2, required for correction/taste. structural = fired inside a "
                         "human-installed structure (specimen, gate, pre-registered bar); "
                         "spontaneous = arose unprompted in open work.")
    pv = lg.add_mutually_exclusive_group()
    pv.add_argument("--preventive", dest="preventive", action="store_true", default=None,
                    help="AMENDMENT 3/4: the catch stopped an act BEFORE it executed. Required "
                         "(with its negation) on correction/taste since AMENDMENT 4.")
    pv.add_argument("--not-preventive", dest="preventive", action="store_false",
                    help="AMENDMENT 4: explicitly NOT preventive — the act had already executed. "
                         "Must be stated; absence is refused, because absence and false are "
                         "different facts and only one of them is a measurement.")
    lg.add_argument("--boundary", action="store_true",
                    help="the `?` flag: the kind was a judgement call. Flag it, never drop it.")
    lg.set_defaults(fn=cmd_log)

    du = sub.add_parser("dual", help="AMENDMENT 6: the human's INDEPENDENT label for an AI-logged entry")
    du.add_argument("--session", required=True)
    du.add_argument("--arm", required=True, choices=ARMS)
    du.add_argument("--index", required=True, type=int, help="0-based index of the entry being labelled")
    du.add_argument("--kind", required=True, choices=KINDS)
    du.add_argument("--actor", required=True, choices=("human", "ai", "unclear"))
    du.add_argument("--note", help="why this kind and not the adjacent one")
    du.set_defaults(fn=cmd_dual)

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
