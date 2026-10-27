"""T14 numerical sweep (monogate.org/theorems#T14): every real EML tree over leaves {1, x} of EML depth <= 4.

eml(a, b) = exp(a) - ln(b), REAL semantics: a value is undefined where some ln argument is <= 0.
T14 (CONJECTURE): a tree of depth k, not identically zero, has at most 2^k zeros on any open interval
where it is defined. This counts SIGN CHANGES on a grid, per maximal run of defined samples:
  - "undefined" is tracked as its own mask, never inferred from NaN: an ln argument <= 0;
  - a sample whose float evaluation overflowed (inf, or inf - inf) is UNKNOWN: it carries no sign
    and does not split the interval, because the tree is defined there;
  - a sample whose |value| is within 8x its propagated rounding bound carries no sign;
  - a tree with no signed sample among >= 16 trustworthy ones is reported identically zero and
    excluded, and every such tree is then re-checked at 50 digits (mpmath) at random points.
Sign changes bound zeros from BELOW (a double root, or two zeros between grid points, are missed)
and the windows are finite, so a clean sweep is evidence, not a proof.

Run (about 25 minutes, up to ~10 GB; keep it under a memory cap):
  systemd-run --user --scope -p MemoryMax=16G -p MemorySwapMax=0 python3 python/research/t14_zero_sweep.py
writes python/research/results/t14_zero_sweep.json
"""
import json
import pathlib
import random
import time

import mpmath as mp
import numpy as np

WINDOWS = [(-40.0, 40.0, 8001), (-1000.0, 1000.0, 8001), (-5.0, 5.0, 20001)]
EPS = np.finfo(float).eps
SLACK, MIN_TRUSTED = 8.0, 16


def node(VA, EA, UA, DA, VB, EB, UB, DB):
    """eml over rows. V value, E rounding bound, U unknown (overflowed), D undefined."""
    with np.errstate(all="ignore"):
        D = DA | DB | (~UB & ~DB & (VB <= 0))          # ln of a known non-positive value
        eA = np.exp(VA)
        lB = np.log(VB)
        V = eA - lB
        E = eA * (EA + EPS) + EB / np.abs(VB) + EPS * np.abs(lB) + EPS * np.abs(V)
        U = ~D & (UA | UB | ~np.isfinite(V) | ~np.isfinite(E))
    return V, E, U, D


def tally(V, E, U, D, G):
    """per row: identically zero?, most sign changes on any one defined interval"""
    rows = V.shape[0]
    trusted = ~D & ~U
    known = trusted & (np.abs(V) > SLACK * E)
    sign = np.where(known, np.sign(V), 0)
    gap_start = D & np.concatenate([np.ones((rows, 1), bool), ~D[:, :-1]], axis=1)
    interval = np.cumsum(gap_start, axis=1)          # same id <=> same maximal defined run
    r, c = np.nonzero(known)
    s, iv = sign[r, c], interval[r, c]
    flip = (r[1:] == r[:-1]) & (iv[1:] == iv[:-1]) & (s[1:] != s[:-1])
    maxc = np.zeros(rows, int)
    if flip.any():
        keys = r[1:][flip] * (G + 2) + iv[1:][flip]
        uk, counts = np.unique(keys, return_counts=True)
        np.maximum.at(maxc, uk // (G + 2), counts)
    izero = (trusted.sum(axis=1) >= MIN_TRUSTED) & (known.sum(axis=1) == 0)
    return izero, maxc


def sweep(lo, hi, G):
    xs = np.linspace(lo, hi, G)
    V = np.vstack([np.ones(G), xs])
    E = np.zeros((2, G))
    U = np.zeros((2, G), bool)
    D = np.zeros((2, G), bool)
    depth = [0, 0]
    kids = [None, None]                               # (a, b) row ids, or None for a leaf
    for d in (1, 2, 3):
        n = len(V)
        ia, ib = (m.ravel() for m in np.meshgrid(np.arange(n), np.arange(n), indexing="ij"))
        keep = np.maximum(np.array(depth)[ia], np.array(depth)[ib]) == d - 1
        ia, ib = ia[keep], ib[keep]
        v, e, u, dd = node(V[ia], E[ia], U[ia], D[ia], V[ib], E[ib], U[ib], D[ib])
        V, E, U, D = np.vstack([V, v]), np.vstack([E, e]), np.vstack([U, u]), np.vstack([D, dd])
        depth += [d] * len(v)
        kids += list(zip(ia.tolist(), ib.tolist()))
    depth = np.array(depth)
    report = {"window": [lo, hi], "grid": G, "by_depth": {}, "violations": [], "identically_zero": []}

    def record(d, izero, maxc, label):
        b = report["by_depth"].setdefault(str(d), {"trees": 0, "identically_zero": 0, "max_sign_changes": 0, "bound": 2 ** d})
        b["trees"] += len(maxc)
        b["identically_zero"] += int(izero.sum())
        live = ~izero
        if live.any():
            b["max_sign_changes"] = max(b["max_sign_changes"], int(maxc[live].max()))
        report["violations"] += [{"depth": d, "tree": label(j), "sign_changes": int(maxc[j])}
                                 for j in np.nonzero(live & (maxc > 2 ** d))[0][:50]]
        report["identically_zero"] += [label(j) for j in np.nonzero(izero)[0]]

    def show(row):
        return ("1", "x")[row] if kids[row] is None else f"eml({show(kids[row][0])}, {show(kids[row][1])})"

    for d in (0, 1, 2, 3):
        rows = np.nonzero(depth == d)[0]
        iz, mc = tally(V[rows], E[rows], U[rows], D[rows], G)
        record(d, iz, mc, lambda j, rows=rows: show(int(rows[j])))
    deep = np.nonzero(depth == 3)[0]
    for a in range(len(V)):                           # depth 4: eml(A, B) with max child depth 3
        bsel = np.arange(len(V)) if depth[a] == 3 else deep
        rep = (len(bsel), G)
        v, e, u, dd = node(np.broadcast_to(V[a], rep), np.broadcast_to(E[a], rep), np.broadcast_to(U[a], rep),
                           np.broadcast_to(D[a], rep), V[bsel], E[bsel], U[bsel], D[bsel])
        iz, mc = tally(v, e, u, dd, G)
        record(4, iz, mc, lambda j, a=a, bsel=bsel: f"eml({show(a)}, {show(int(bsel[j]))})")
    return report


def ev(s, x):
    """exact-ish real evaluation of a printed tree at 50 digits; None where undefined"""
    mp.mp.dps = 50
    def go(t, i):
        if t.startswith("1", i):
            return mp.mpf(1), i + 1
        if t.startswith("x", i):
            return mp.mpf(x), i + 1
        a, i = go(t, i + 4)                           # "eml("
        b, i = go(t, i + 2)                           # ", "
        # mpmath never overflows: exp(exp(exp(40))) would need an exponent of ~1e17 bits and
        # exhaust memory. A point whose exp argument is that large is skipped, not evaluated.
        if a is None or b is None or b <= 0 or a > 1e4:
            return None, i + 1
        return mp.exp(a) - mp.log(b), i + 1           # ")"
    return go(s, 0)[0]


def confirm_zero(tree, lo, hi):
    """identically zero at 50 digits at random points of [-3, 3] where the tree is defined and evaluable"""
    rng = random.Random(tree)
    vals = [ev(tree, mp.mpf(rng.uniform(max(lo, -3.0), min(hi, 3.0)))) for _ in range(40)]
    vals = [v for v in vals if v is not None]
    return len(vals) >= 3 and all(abs(v) < mp.mpf("1e-40") for v in vals)


if __name__ == "__main__":
    out = {"conjecture": "T14: a real EML tree over {1, x} of EML depth k, not identically zero, has at most "
                         "2^k zeros on any open interval where it is defined",
           "method": __doc__.split("\n\n")[1].strip(), "windows": []}
    for lo, hi, g in WINDOWS:
        t0 = time.time()
        rep = sweep(lo, hi, g)
        rep["identically_zero_confirmed_at_50_digits"] = all(confirm_zero(t, lo, hi) for t in rep["identically_zero"])
        rep["seconds"] = round(time.time() - t0)
        out["windows"].append(rep)
        print(f"[{lo:g}, {hi:g}] x {g}: " + "  ".join(
            f"d{d}: {b['max_sign_changes']}/{b['bound']}" for d, b in rep["by_depth"].items())
            + f"  zero-trees {len(rep['identically_zero'])} (confirmed {rep['identically_zero_confirmed_at_50_digits']})"
            + f"  violations {len(rep['violations'])}  {rep['seconds']}s", flush=True)
    path = pathlib.Path(__file__).resolve().parent / "results" / "t14_zero_sweep.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + "\n")
