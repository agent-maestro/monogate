#!/usr/bin/env python3
"""Check F16-only constructions at 50 digits on a dense sample of their stated domains.

Semantics are the natural real ones: a tree is defined at a point only if every log argument is > 0
there (the negated argument for F2, F4, F7, F8, F10, F15) and both F16fn arguments are > 0. A
construction passes if it is defined at every sample point and agrees with the target to a relative
1e-40.

usage: python verify.py                      # the constructions below, two of them negative controls
       python verify.py TARGET EXPR DOMAIN   # one tree, e.g. div "F16fn(x, F13(-1, y))" pos2
python/tests/test_superbest_f16_constructions.py runs the same check on monogate.superbest's table.
"""
from __future__ import annotations

import random
import re
import sys

import mpmath as mp

mp.mp.dps = 50
REL = mp.mpf(10) ** -40


def op(name, a, b):
    e, lg = mp.exp, mp.log
    if name == "EML":       return (b > 0), (lambda: e(a) - lg(b))
    if name == "EMLn":      return (b < 0), (lambda: e(a) - lg(-b))
    if name == "DEML":      return (b > 0), (lambda: e(-a) - lg(b))
    if name == "DEMLn":     return (b < 0), (lambda: e(-a) - lg(-b))
    if name == "EMLswap":   return (a > 0), (lambda: e(b) - lg(a))
    if name == "EMLnswap":  return (a > 0), (lambda: e(-b) - lg(a))
    if name == "EMLswapn":  return (a < 0), (lambda: e(b) - lg(-a))
    if name == "EMLnswapn": return (a < 0), (lambda: e(-b) - lg(-a))
    if name == "LEdiv":     return (b > 0), (lambda: a - lg(b))
    if name == "LEdivn":    return (b < 0), (lambda: a - lg(-b))
    if name == "LEAd":      return (e(a) + b > 0), (lambda: lg(e(a) + b))
    if name == "LEAdn":     return (e(a) - b > 0), (lambda: lg(e(a) - b))
    if name == "F13":       return (b > 0), (lambda: e(a * lg(b)))
    if name == "F14":       return (b > 0), (lambda: e(a + lg(b)))
    if name == "F15":       return (b < 0), (lambda: e(a + lg(-b)))
    if name == "F16fn":     return (a > 0 and b > 0), (lambda: e(lg(a) + lg(b)))
    raise KeyError(name)


def parse(s):
    s = s.replace(" ", "")
    pos = 0

    def expr():
        nonlocal pos
        m = re.match(r"[A-Za-z][A-Za-z0-9]*\(", s[pos:])
        if m:
            name = m.group(0)[:-1]
            pos += len(m.group(0))
            a = expr()
            assert s[pos] == ","; pos += 1
            b = expr()
            assert s[pos] == ")"; pos += 1
            return (name, a, b)
        m = re.match(r"-?[0-9]+(/[0-9]+)?|[a-z]", s[pos:])
        assert m, s[pos:]
        pos += len(m.group(0))
        return m.group(0)

    t = expr()
    assert pos == len(s)
    return t


def nodes(t):
    return 0 if isinstance(t, str) else 1 + nodes(t[1]) + nodes(t[2])


def ev(t, env):
    if isinstance(t, str):
        if t in env:
            return env[t]
        if "/" in t:
            p, q = t.split("/")
            return mp.mpf(p) / mp.mpf(q)
        return mp.mpf(t)
    a = ev(t[1], env)
    b = ev(t[2], env)
    if a is None or b is None:
        return None
    ok, f = op(t[0], a, b)
    return f() if ok else None


rnd = random.Random(20260913)


def samples(domain, n=400):
    out = []
    mags = [mp.mpf("1e-3"), mp.mpf("0.05"), mp.mpf("0.4"), mp.mpf("1"), mp.mpf("3"), mp.mpf("9")]

    def r(pos=False, nz=False, allow0=True):
        m = rnd.choice(mags)
        v = m * mp.mpf(rnd.uniform(0.5, 2.0))
        if not pos and rnd.random() < 0.5:
            v = -v
        return v

    for i in range(n):
        if domain == "pos1":
            out.append({"x": r(pos=True), "n": mp.mpf(rnd.uniform(-4, 4))})
        elif domain == "all1":
            out.append({"x": mp.mpf(0) if i == 0 else r()})
        elif domain == "nz1":
            out.append({"x": r()})
        elif domain == "pos2":
            out.append({"x": r(pos=True), "y": r(pos=True)})
        elif domain == "all2":
            x = mp.mpf(0) if i % 7 == 0 else r()
            y = mp.mpf(0) if i % 5 == 0 else r()
            out.append({"x": x, "y": y})
        elif domain == "ynz2":
            x = mp.mpf(0) if i % 7 == 0 else r()
            out.append({"x": x, "y": r()})
    return out


def check_quiet(target, expr, domain, n=120):
    t = parse(expr)
    for p in samples(domain, n):
        val = ev(t, p)
        if val is None:
            return False
        ref = TARGET[target](p)
        if abs(val - ref) / max(1, abs(ref)) >= REL:
            return False
    return True


TARGET = {
    "exp": lambda v: mp.exp(v["x"]), "ln": lambda v: mp.log(v["x"]), "neg": lambda v: -v["x"],
    "recip": lambda v: 1 / v["x"], "sqrt": lambda v: mp.sqrt(v["x"]), "pow": lambda v: v["x"] ** v["n"],
    "add": lambda v: v["x"] + v["y"], "sub": lambda v: v["x"] - v["y"], "mul": lambda v: v["x"] * v["y"],
    "div": lambda v: v["x"] / v["y"], "abs": lambda v: abs(v["x"]),
}


def check(label, target, expr, domain):
    t = parse(expr)
    pts = samples(domain)
    worst = mp.mpf(0)
    undefined = 0
    for p in pts:
        val = ev(t, p)
        if val is None:
            undefined += 1
            continue
        ref = TARGET[target](p)
        err = abs(val - ref) / max(1, abs(ref))
        worst = max(worst, err)
    verdict = "PASS" if undefined == 0 and worst < REL else "FAIL"
    print(f"{verdict}  {label:<22} {nodes(t)}n  on {domain:<5} ({len(pts)} pts): "
          f"undefined at {undefined}, max rel err {mp.nstr(worst, 3)}   {expr}")
    return verdict == "PASS"


CONSTRUCTIONS = [
    ("exp (all x)", "exp", "EML(x, 1)", "all1"),
    ("ln (x>0)", "ln", "LEdiv(0, F13(-1, x))", "pos1"),
    ("neg (all x)", "neg", "LEdiv(0, EML(x, 1))", "all1"),
    ("add (all x,y)", "add", "LEdiv(x, DEML(y, 1))", "all2"),
    ("sub (all x,y)", "sub", "LEdiv(x, EML(y, 1))", "all2"),
    ("mul (x,y>0)", "mul", "F16fn(x, y)", "pos2"),
    ("div (x,y>0)", "div", "F16fn(x, F13(-1, y))", "pos2"),
    ("recip (x>0)", "recip", "F13(-1, x)", "pos1"),
    ("pow (x>0, real n)", "pow", "F13(n, x)", "pos1"),
    ("sqrt (x>0)", "sqrt", "F13(1/2, x)", "pos1"),
    ("mul (all x,y)", "mul", "LEdiv(0, F13(y, DEML(x, 1)))", "all2"),
    ("recip (x!=0)", "recip", "LEdiv(0, F13(F13(-1, LEdiv(0, F13(x, DEML(x, 1)))), DEML(x, 1)))", "nz1"),
    ("div (y!=0)", "div", "LEdiv(0, F13(x, F13(F13(-1, LEdiv(0, F13(y, DEML(y, 1)))), DEML(y, 1))))", "ynz2"),
    # expected failures, to show the checker rejects sign-restricted trees on signed domains
    ("[neg ctl] div pos tree on y!=0", "div", "F16fn(x, F13(-1, y))", "ynz2"),
    ("[neg ctl] mul pos tree on all", "mul", "F16fn(x, y)", "all2"),
]

if __name__ == "__main__":
    if len(sys.argv) == 4:
        ok = check("cli", sys.argv[1], sys.argv[2], sys.argv[3])
        sys.exit(0 if ok else 1)
    results = [check(*c) for c in CONSTRUCTIONS]
    print(f"{sum(results)}/{len(results)} PASS (the two [neg ctl] rows must FAIL)")
