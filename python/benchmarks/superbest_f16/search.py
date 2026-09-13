#!/usr/bin/env python3
"""Exhaustive small-tree search over /framework's F16 (the Lean F1..F16 of AddLowerBound.lean),
natural real semantics.

A tree is VALID on a domain when, at every sample point of the domain, every log argument is > 0
(for F2, F4, F7, F8, F10, F15 the negated argument), both F16fn arguments are > 0, and every value
is finite. Size = number of operator nodes; leaves (variables and constants) are free.

Levels 0..KMAX are enumerated bottom-up and de-duplicated by value fingerprint (a function already
reachable with fewer nodes is dropped). Sizes KMAX+1 .. 2*KMAX are then decided by inverting the root
operator in one argument and looking the required subtree up (recursively when the required subtree
is itself larger than KMAX). Every match is re-verified at 50 digits on a dense grid by verify.py.

Leaves are the variables and the constants 0, 1, -1, 2, 1/2. Validity and equality are decided at
the sample points of each domain, so a "none" result is numerical evidence, not a proof: a tree whose
values exceed 1e300 at a sample, or whose inversion loses more than the lookup tolerance, is not seen.

usage: [KMAX=4] python search.py DOMAIN MAXSIZE [TARGETS]
  DOMAIN in {pos1, all1, nz1, pos2, all2, ynz2}; run from this directory (it imports verify.py).

Runs behind monogate.superbest's F16 recount (2026-09-13; about 7 minutes in all on one core):
  python search.py pos1 3; python search.py all1 3; python search.py pos2 3; python search.py all2 3
  KMAX=4 python search.py nz1 7      # recip, x != 0: none with <= 6 nodes, found at 7
  KMAX=4 python search.py ynz2 7     # div, y != 0: none with <= 7 nodes
"""
from __future__ import annotations

import sys
import time

import numpy as np

np.seterr(all="ignore")

NAMES = {1: "EML", 2: "EMLn", 3: "DEML", 4: "DEMLn", 5: "EMLswap", 6: "EMLnswap", 7: "EMLswapn",
         8: "EMLnswapn", 9: "LEdiv", 10: "LEdivn", 11: "LEAd", 12: "LEAdn", 13: "F13", 14: "F14",
         15: "F15", 16: "F16fn"}
OPS = list(range(1, 17))
BIG = 1e300
REL = 1e-8          # forward-check tolerance (relative) applied at every level
TOL = 1e-6          # lookup tolerance, in asinh scale
import os
KMAX = int(os.environ.get("KMAX", "3"))
CHUNK = 4_000_000   # floats per evaluation block


def F(k, a, b):
    if k == 1:
        v = np.exp(a) - np.log(b); ok = b > 0
    elif k == 2:
        v = np.exp(a) - np.log(-b); ok = b < 0
    elif k == 3:
        v = np.exp(-a) - np.log(b); ok = b > 0
    elif k == 4:
        v = np.exp(-a) - np.log(-b); ok = b < 0
    elif k == 5:
        v = np.exp(b) - np.log(a); ok = a > 0
    elif k == 6:
        v = np.exp(-b) - np.log(a); ok = a > 0
    elif k == 7:
        v = np.exp(b) - np.log(-a); ok = a < 0
    elif k == 8:
        v = np.exp(-b) - np.log(-a); ok = a < 0
    elif k == 9:
        v = a - np.log(b); ok = b > 0
    elif k == 10:
        v = a - np.log(-b); ok = b < 0
    elif k == 11:
        s = np.exp(a) + b; v = np.log(s); ok = s > 0
    elif k == 12:
        s = np.exp(a) - b; v = np.log(s); ok = s > 0
    elif k == 13:
        v = np.exp(a * np.log(b)); ok = b > 0
    elif k == 14:
        v = np.exp(a + np.log(b)); ok = b > 0
    elif k == 15:
        v = np.exp(a + np.log(-b)); ok = b < 0
    else:
        v = np.exp(np.log(a) + np.log(b)); ok = (a > 0) & (b > 0)
    ok = ok & np.isfinite(v) & (np.abs(v) < BIG)
    if k >= 13:
        ok = ok & (v > 0)
    return v, ok


def solve(k, side, t, kn):
    """Root op k with value t. side 'L': kn is the LEFT argument, return the required RIGHT one.
    side 'R': kn is the RIGHT argument, return the required LEFT one. Returns (req, ok)."""
    one = np.ones(np.broadcast(t, kn).shape, bool)
    if k == 1:
        if side == "L": r = np.exp(np.exp(kn) - t); ok = one
        else: s = t + np.log(kn); r = np.log(s); ok = (kn > 0) & (s > 0)
    elif k == 2:
        if side == "L": r = -np.exp(np.exp(kn) - t); ok = one
        else: s = t + np.log(-kn); r = np.log(s); ok = (kn < 0) & (s > 0)
    elif k == 3:
        if side == "L": r = np.exp(np.exp(-kn) - t); ok = one
        else: s = t + np.log(kn); r = -np.log(s); ok = (kn > 0) & (s > 0)
    elif k == 4:
        if side == "L": r = -np.exp(np.exp(-kn) - t); ok = one
        else: s = t + np.log(-kn); r = -np.log(s); ok = (kn < 0) & (s > 0)
    elif k == 5:   # exp(b) - log a
        if side == "L": s = t + np.log(kn); r = np.log(s); ok = (kn > 0) & (s > 0)
        else: r = np.exp(np.exp(kn) - t); ok = one
    elif k == 6:   # exp(-b) - log a
        if side == "L": s = t + np.log(kn); r = -np.log(s); ok = (kn > 0) & (s > 0)
        else: r = np.exp(np.exp(-kn) - t); ok = one
    elif k == 7:   # exp(b) - log(-a)
        if side == "L": s = t + np.log(-kn); r = np.log(s); ok = (kn < 0) & (s > 0)
        else: r = -np.exp(np.exp(kn) - t); ok = one
    elif k == 8:   # exp(-b) - log(-a)
        if side == "L": s = t + np.log(-kn); r = -np.log(s); ok = (kn < 0) & (s > 0)
        else: r = -np.exp(np.exp(-kn) - t); ok = one
    elif k == 9:
        if side == "L": r = np.exp(kn - t); ok = one
        else: r = t + np.log(kn); ok = kn > 0
    elif k == 10:
        if side == "L": r = -np.exp(kn - t); ok = one
        else: r = t + np.log(-kn); ok = kn < 0
    elif k == 11:
        if side == "L": r = np.exp(t) - np.exp(kn); ok = one
        else: s = np.exp(t) - kn; r = np.log(s); ok = s > 0
    elif k == 12:
        if side == "L": r = np.exp(kn) - np.exp(t); ok = one
        else: s = np.exp(t) + kn; r = np.log(s); ok = s > 0
    elif k == 13:
        if side == "L": r = np.exp(np.log(t) / kn); ok = (t > 0) & (kn != 0)
        else:
            lb = np.log(kn); r = np.log(t) / lb; ok = (t > 0) & (kn > 0) & (np.abs(lb) > 1e-12)
    elif k == 14:
        if side == "L": r = t * np.exp(-kn); ok = t > 0
        else: r = np.log(t) - np.log(kn); ok = (t > 0) & (kn > 0)
    elif k == 15:
        if side == "L": r = -t * np.exp(-kn); ok = t > 0
        else: r = np.log(t) - np.log(-kn); ok = (t > 0) & (kn < 0)
    else:
        if side == "L": r = t / kn; ok = (t > 0) & (kn > 0)
        else: r = t / kn; ok = (t > 0) & (kn > 0)
    ok = ok & np.isfinite(r) & (np.abs(r) < BIG)
    return r, ok


rng = np.random.default_rng(20260913)
MULT = rng.integers(1, 2**63, size=64, dtype=np.int64).view(np.uint64) | np.uint64(1)


def fingerprint(V):
    q = np.round(np.arcsinh(V) * 1e6).astype(np.int64).view(np.uint64)
    return (q * MULT[None, : V.shape[1]]).sum(axis=1, dtype=np.uint64)


class Level:
    def __init__(self, vals, prov):
        self.vals = vals                  # (n,S)
        self.prov = prov                  # (n,5) int64: op, llev, lidx, rlev, ridx  (op=0 leaf)
        self.n = len(vals)
        A = np.arcsinh(vals)
        self.p = int(np.argmax(A.std(axis=0))) if self.n > 1 else 0
        order = np.argsort(A[:, self.p], kind="stable")
        self.order = order
        self.A = A[order]
        self.key = self.A[:, self.p].copy()

    def lookup(self, R):
        """R (m,S). Returns (qi, entry index) pairs of matches."""
        Ra = np.arcsinh(R)
        lo = np.searchsorted(self.key, Ra[:, self.p] - TOL)
        hi = np.searchsorted(self.key, Ra[:, self.p] + TOL)
        cnt = hi - lo
        tot = int(cnt.sum())
        if tot == 0:
            return np.empty(0, np.int64), np.empty(0, np.int64)
        qis, eis = [], []
        idx = np.nonzero(cnt)[0]
        # process in blocks bounded by candidate count
        start = 0
        csum = np.cumsum(cnt[idx])
        while start < len(idx):
            base = csum[start - 1] if start else 0
            end = int(np.searchsorted(csum, base + 2_000_000, side="right"))
            end = max(end, start + 1)
            blk = idx[start:end]
            c = cnt[blk]
            qi = np.repeat(blk, c)
            off = np.arange(int(c.sum())) - np.repeat(np.cumsum(c) - c, c)
            ei = lo[qi] + off
            good = np.abs(self.A[ei] - Ra[qi]).max(axis=1) <= TOL
            qis.append(qi[good]); eis.append(self.order[ei[good]])
            start = end
        return np.concatenate(qis), np.concatenate(eis)


def build_levels(leaves, leaf_names, S):
    L0 = Level(np.array(leaves, float), np.zeros((len(leaves), 5), np.int64))
    for i in range(len(leaves)):
        L0.prov[i] = [0, 0, i, 0, 0]
    levels = [L0]
    seen = fingerprint(L0.vals)
    for k in range(1, KMAX + 1):
        t0 = time.time()
        chunks_v, chunks_p, chunks_h = [], [], []
        seen_sorted = np.sort(seen)
        for i in range(k):
            j = k - 1 - i
            A, B = levels[i].vals, levels[j].vals
            blk = max(1, CHUNK // (max(1, len(B)) * S))
            for op in OPS:
                for a0 in range(0, len(A), blk):
                    Ab = A[a0:a0 + blk]
                    v, ok = F(op, Ab[:, None, :], B[None, :, :])
                    okm = ok.all(axis=2)
                    ai, bi = np.nonzero(okm)
                    if len(ai) == 0:
                        continue
                    vv = v[ai, bi]
                    h = fingerprint(vv)
                    pos = np.searchsorted(seen_sorted, h)
                    pos[pos >= len(seen_sorted)] = len(seen_sorted) - 1
                    new = seen_sorted[pos] != h
                    if not new.any():
                        continue
                    vv, h, ai, bi = vv[new], h[new], ai[new], bi[new]
                    _, first = np.unique(h, return_index=True)
                    vv, h, ai, bi = vv[first], h[first], ai[first], bi[first]
                    pr = np.stack([np.full(len(ai), op), np.full(len(ai), i), a0 + ai,
                                   np.full(len(ai), j), bi], axis=1).astype(np.int64)
                    chunks_v.append(vv); chunks_p.append(pr); chunks_h.append(h)
        V = np.concatenate(chunks_v) if chunks_v else np.empty((0, S))
        P = np.concatenate(chunks_p) if chunks_p else np.empty((0, 5), np.int64)
        H = np.concatenate(chunks_h) if chunks_h else np.empty(0, np.uint64)
        _, first = np.unique(H, return_index=True)
        first.sort()
        V, P, H = V[first], P[first], H[first]
        levels.append(Level(V, P))
        seen = np.concatenate([seen, H])
        print(f"  level {k}: {len(V):,} distinct valid functions ({time.time() - t0:.1f}s)", flush=True)
    return levels


def lvl_tree(levels, k, e, leaf_names):
    op, li, lx, ri, rx = (int(z) for z in levels[k].prov[e])
    if op == 0:
        return leaf_names[lx]
    return (op, lvl_tree(levels, li, lx, leaf_names), lvl_tree(levels, ri, rx, leaf_names))


def close(A, B):
    return np.all(np.abs(A - B) <= REL * (1 + np.abs(B)), axis=-1)


def find(levels, T, s, S, cap=8):
    """Queries T (Q,S) at exact size s. Returns {qi: [(witness, values), ...]} (at most cap each).
    Every witness is forward-evaluated in float and must reproduce its query to REL at all samples;
    a lookup hit alone (tolerance TOL in asinh scale) is never accepted."""
    Q = T.shape[0]
    found = {}
    if Q == 0:
        return found
    if s <= KMAX:
        qi, ei = levels[s].lookup(T)
        if len(qi):
            V = levels[s].vals[ei]
            good = close(V, T[qi])
            for q, e in zip(qi[good].tolist(), ei[good].tolist()):
                lst = found.setdefault(q, [])
                if len(lst) < cap:
                    lst.append((("lvl", s, e), levels[s].vals[e]))
        return found
    alive = np.ones(Q, bool)
    for i in range(s):
        j = s - 1 - i
        cands = []
        if i <= KMAX:
            cands.append(("L", i, j))
        if j <= KMAX:
            cands.append(("R", j, i))
        if not cands:
            raise RuntimeError(f"size {s} split ({i},{j}) not decidable with KMAX={KMAX}")
        side, ks, us = min(cands, key=lambda c: levels[c[1]].n)
        KV = levels[ks].vals
        for op in OPS:
            if not alive.any():
                return found
            for c0 in range(0, len(KV), max(1, CHUNK // (max(1, int(alive.sum())) * S))):
                aq = np.nonzero(alive)[0]
                if len(aq) == 0:
                    return found
                blk = max(1, CHUNK // (len(aq) * S))
                Kb = KV[c0:c0 + blk]
                req, ok = solve(op, side, T[aq][:, None, :], Kb[None, :, :])
                okm = ok.all(axis=2)
                mi, ni = np.nonzero(okm)
                if len(mi) == 0:
                    continue
                sub = find(levels, req[mi, ni], us, S, cap)
                for r, lst in sub.items():
                    q = int(aq[mi[r]])
                    kvec = Kb[ni[r]]
                    for w, v in lst:
                        fwd, fok = (F(op, kvec, v) if side == "L" else F(op, v, kvec))
                        if fok.all() and close(fwd, T[q]):
                            out = found.setdefault(q, [])
                            if len(out) < cap:
                                out.append((("op", op, side, ("lvl", ks, int(c0 + ni[r])), w), fwd))
                            if len(out) >= cap:
                                alive[q] = False
                                break
    return found


def witness_tree(levels, w, leaf_names):
    if w[0] == "lvl":
        return lvl_tree(levels, w[1], w[2], leaf_names)
    _, op, side, kn, un = w
    a = witness_tree(levels, kn, leaf_names)
    b = witness_tree(levels, un, leaf_names)
    return (op, a, b) if side == "L" else (op, b, a)


def tstr(t):
    if isinstance(t, str):
        return t
    return f"{NAMES[t[0]]}({tstr(t[1])}, {tstr(t[2])})"


C = {"0": 0.0, "1": 1.0, "-1": -1.0, "2": 2.0, "1/2": 0.5}

DOMAINS = {
    "pos1": dict(pts=[0.043, 0.17, 0.38, 0.71, 1.09, 1.61, 2.38, 3.7, 5.3], vars=1),
    "all1": dict(pts=[-2.63, -1.37, -0.71, -0.29, 0.0, 0.17, 0.53, 0.94, 1.61, 2.38], vars=1),
    "nz1": dict(pts=[-2.63, -1.37, -0.71, -0.29, -0.083, 0.061, 0.17, 0.53, 0.94, 1.61, 2.38], vars=1),
    "pos2": dict(pts=[(0.13, 0.41), (0.41, 2.3), (1.7, 0.29), (2.9, 3.3), (0.77, 1.13), (3.6, 0.07),
                      (1.05, 1.9), (0.52, 0.52), (2.2, 0.9), (0.061, 4.1), (1.33, 2.71), (4.4, 1.6)], vars=2),
    "all2": dict(pts=[(-2.1, -1.7), (-2.1, 0.83), (-0.63, 2.4), (-0.63, -0.38), (0.0, -1.7), (0.0, 0.83),
                      (0.47, 0.0), (-2.1, 0.0), (0.47, -0.38), (1.9, 2.4), (1.9, -1.7), (0.47, 0.83),
                      (1.3, 0.29), (-1.1, -2.2)], vars=2),
    "ynz2": dict(pts=[(-2.1, -1.7), (-2.1, 0.83), (-0.63, 2.4), (-0.63, -0.38), (0.0, -1.7), (0.0, 0.83),
                      (0.47, 0.19), (-2.1, -0.11), (0.47, -0.38), (1.9, 2.4), (1.9, -1.7), (0.47, 0.83),
                      (1.3, 0.29), (-1.1, -2.2)], vars=2),
}

TARGETS = {
    "pos1": {"ln": np.log, "recip": lambda x: 1 / x, "sqrt": np.sqrt},
    "all1": {"neg": lambda x: -x, "abs": np.abs, "exp": np.exp},
    "nz1": {"recip": lambda x: 1 / x},
    "pos2": {"mul": lambda x, y: x * y, "div": lambda x, y: x / y},
    "all2": {"add": lambda x, y: x + y, "sub": lambda x, y: x - y, "mul": lambda x, y: x * y},
    "ynz2": {"div": lambda x, y: x / y},
}


def main():
    dom, maxsize = sys.argv[1], int(sys.argv[2])
    only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    d = DOMAINS[dom]
    pts = np.array(d["pts"], float)
    S = len(pts)
    if d["vars"] == 1:
        X = pts
        leaves = [X] + [np.full(S, c) for c in C.values()]
        leaf_names = ["x"] + list(C.keys())
        tv = {n: f(X) for n, f in TARGETS[dom].items()}
    else:
        X, Y = pts[:, 0], pts[:, 1]
        leaves = [X, Y] + [np.full(S, c) for c in C.values()]
        leaf_names = ["x", "y"] + list(C.keys())
        tv = {n: f(X, Y) for n, f in TARGETS[dom].items()}
    if only:
        tv = {n: v for n, v in tv.items() if n in only}
    print(f"domain {dom}: {S} sample points, leaves {leaf_names}, KMAX={KMAX}, sizes 1..{maxsize}", flush=True)
    levels = build_levels(leaves, leaf_names, S)
    import verify as VF
    vdom = dom
    for name, t in tv.items():
        hit = None
        for s_ in range(0, maxsize + 1):
            t0 = time.time()
            res = find(levels, t[None, :], s_, S, cap=64)
            dt = time.time() - t0
            cands = res.get(0, [])
            rejected = 0
            for w, _v in cands:
                expr = tstr(witness_tree(levels, w, leaf_names))
                if VF.check_quiet(name, expr, vdom):
                    hit = (s_, expr)
                    break
                rejected += 1
            if hit:
                print(f"  {name}: FOUND at size {s_} ({dt:.1f}s; {rejected} float-only candidates rejected at 50 digits): {hit[1]}", flush=True)
                break
            note = f"; {rejected} float-only candidates rejected at 50 digits" if rejected else ""
            capped = " [candidate cap reached: inconclusive]" if len(cands) >= 64 else ""
            print(f"  {name}: none at size {s_} ({dt:.1f}s{note}){capped}", flush=True)
        if hit is None:
            print(f"  {name}: NO TREE with <= {maxsize} nodes", flush=True)

if __name__ == "__main__":
    main()
