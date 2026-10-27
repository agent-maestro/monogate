"""A fully-EML tree for sin(x): leaves 1 and x only, eml(a, b) = exp(a) - Log(b), principal Log.

The measurement behind COST_SIN's "fully EML over C" row (monogate.org/theorems#COST_SIN). It is an
UPPER BOUND by explicit construction: every step below is an identity, and the tree is evaluated
against sin(x) at two precisions. It says nothing about how small such a tree can be.

Run:  python3 python/research/sin_fully_eml.py      (writes python/research/results/sin_fully_eml.json)

BRANCH CUT. Principal Log puts the cut on the negative real axis with Log(-r) = ln r + i*pi. Two
values in this tree land EXACTLY on it, both exact reals by derivation:
  (1) -1 itself, in Log(-1) = i*pi;
  (2) exp(e - i*pi) = -e^e, in LOG(-1) below, whose exact value is therefore e - (e + i*pi) = -i*pi.
Floating point puts a ~1e-60 residue on (2) whose sign is noise, and an earlier version of this
construction silently relied on that noise (+i*pi instead of -i*pi). The evaluator here snaps a value
that is negative real to within 10^(20 - dps) of |value| onto the cut, logs every snap, refuses any
snap not at (1) or (2), and checks that 60- and 120-digit runs agree — a genuinely off-axis value
would snap at one precision and not the other.

WHY IT IS LARGE. x enters a tree only via exp(x) or Log(x). Here u = w - x is exact for every real x:
eml(z, eml(x, 1)) = e^z - Log(e^x) = w - x (w = e^z, Im w != 0, so u != 0). sin x = a - b with
a = -(i/2) e^{ix}, b = -(i/2) e^{-ix} needs two chains of x, each needing i twice — a rotation
(Log u -/+ i*pi/2) and a phase (w = +-(pi/2 - i ln 2)). The imaginary unit costs 29 nodes from 1.

DERIVATION. LOG(y) = eml(1, eml(eml(1, y), 1)) == Log y (mod 2*pi*i), so exp(LOG(y)) = y exactly.
EXP(y) = eml(y, 1).
  -1  = eml(LOG(e-1), e^e) = (e-1) - e                        2 = eml(1, EXP(e-2)), e-2 = eml(LOG(e-1), e)
  -2  = eml(LOG(e-2), e^e) = (e-2) - e                        1/2 = EXP(eml(1, eml(e, EXP(EXP(eml(1, -1))))))
        (eml(1, -1) = e - i*pi by (1); EXP -> -e^e, used only under exp; e^e + e^e = 2e^e; e - Log 2e^e = -ln 2)
  NIPI = LOG(-1)               = -i*pi                        by (2)
  C_M  = eml(LOG(LOG(NIPI)), 2): exp(C_M) = exp(LOG(NIPI)) / 2 = -i*pi/2
  NI   = EXP(EXP(C_M))         = e^{-i*pi/2} = -i
Half-chain for constants Z, c, k:   u = eml(Z, eml(x, 1)) = w - x
  A = eml(c, eml(eml(k, u), 1)) == e^c - e^k + Log u (mod 2*pi*i);   H = eml(A, 1) = exp(A) = e^{e^c - e^k} u
  P: c = LOG(NIPI) (e^c = -i*pi), k = C_M (e^k = -i*pi/2):  e^c - e^k = -i*pi/2   => H = -i u
  V: c = LOG(eml(1, NI)) (e^c = e + i*pi/2), k = 1:        e^c - e^k = +i*pi/2   => H = +i u
  Z_P = eml(LOG(LOG(eml(C_M, 2))), NI):   eml(C_M, 2) = -i*pi/2 - ln 2 = L,  exp(Z_P) = L * i = pi/2 - i ln 2
  Z_V = eml(LOG(LOG(L')), NI), L' = eml(LOG(eml(1, NI)), EXP(eml(1, 2))) = (e + i*pi/2) - (e - ln 2) = ln 2 + i*pi/2,
        exp(Z_V) = L' * i = -pi/2 + i ln 2
  exp(P) = e^{-i(w_P - x)} = e^{ix} e^{-i pi/2} e^{-ln 2} = a;   exp(V) = e^{i(w_V - x)} = b
sin x = eml(P, eml(eml(V, 1), 1)) = exp(P) - Log(exp(b)) = a - b, since |Im b| <= 1/2 < pi.
"""
import json
import pathlib
import random

import mpmath as mp

ONE, X = ("1",), ("x",)


def eml(a, b):
    return ("eml", a, b)


def LOG(y):
    return eml(ONE, eml(eml(ONE, y), ONE))


def EXP(y):
    return eml(y, ONE)


def nodes(t):
    return 0 if t[0] != "eml" else 1 + nodes(t[1]) + nodes(t[2])


def show(t):
    return t[0] if t[0] != "eml" else f"eml({show(t[1])}, {show(t[2])})"


def ev(t, x, snaps):
    """principal-branch evaluation; a value on the negative real axis up to rounding is put ON the cut"""
    if t[0] == "1":
        return mp.mpc(1)
    if t[0] == "x":
        return mp.mpc(x)
    a, b = ev(t[1], x, snaps), ev(t[2], x, snaps)
    if b == 0:
        raise ZeroDivisionError("Log of 0")
    if b.real < 0 and abs(b.imag) <= mp.mpf(10) ** (20 - mp.mp.dps) * abs(b.real):
        snaps.add(mp.nstr(b.real, 12))
        return mp.exp(a) - (mp.log(-b.real) + 1j * mp.pi)
    return mp.exp(a) - mp.log(b)


ALLOWED_SNAPS = {"-1.0", mp.nstr(-mp.exp(mp.e), 12)}     # (1) and (2) of the docstring


def value(t, x=0):
    """the same evaluation at 60 and 120 digits; they must agree, and every snap must be (1) or (2)"""
    out = []
    for dps in (60, 120):
        with mp.workdps(dps):
            snaps = set()
            out.append(ev(t, mp.mpf(x), snaps))
            assert snaps <= ALLOWED_SNAPS, f"unexpected value on the branch cut: {snaps - ALLOWED_SNAPS}"
    assert abs(out[0] - out[1]) < mp.mpf("1e-50"), "precision-dependent value: a branch decided by rounding"
    return out[1]


def check(name, t, want):
    got = value(t)
    assert abs(got - want) < mp.mpf("1e-50"), f"{name}: {mp.nstr(got, 20)} != {want}"
    return t


mp.mp.dps = 60
E = eml(ONE, ONE)
LN_E_MINUS_1 = LOG(eml(ONE, E))
NEG1 = check("-1", eml(LN_E_MINUS_1, EXP(E)), -1)
E_MINUS_2 = eml(LN_E_MINUS_1, E)
TWO = check("2", eml(ONE, EXP(E_MINUS_2)), 2)
NEG2 = check("-2", eml(LOG(E_MINUS_2), EXP(E)), -2)
HALF = check("1/2", EXP(eml(ONE, eml(E, EXP(EXP(eml(ONE, NEG1)))))), mp.mpf(1) / 2)
NIPI = check("-i*pi", LOG(NEG1), -1j * mp.pi)
C_M = eml(LOG(LOG(NIPI)), TWO)
check("exp C_M", EXP(C_M), -1j * mp.pi / 2)
NI = check("-i", EXP(EXP(C_M)), -1j)
L = check("L", eml(C_M, TWO), -mp.log(2) - 1j * mp.pi / 2)
L2 = check("L'", eml(LOG(eml(ONE, NI)), EXP(eml(ONE, TWO))), mp.log(2) + 1j * mp.pi / 2)
Z_P = eml(LOG(LOG(L)), NI)
check("w_P", EXP(Z_P), mp.pi / 2 - 1j * mp.log(2))
Z_V = eml(LOG(LOG(L2)), NI)
check("w_V", EXP(Z_V), -mp.pi / 2 + 1j * mp.log(2))


def half(z, c, k):
    u = eml(z, eml(X, ONE))
    return eml(eml(c, eml(eml(k, u), ONE)), ONE)


P = half(Z_P, LOG(NIPI), C_M)
V = half(Z_V, LOG(eml(ONE, NI)), ONE)
SIN = eml(P, eml(eml(V, ONE), ONE))

random.seed(20261026)
xs = [mp.mpf(0), mp.mpf("1e-30"), -mp.mpf("1e-30"), mp.mpf(1), mp.mpf(-1), mp.pi, -mp.pi, mp.pi / 2,
      mp.mpf(100), mp.mpf(-100), mp.mpf(1000), mp.mpf(-1000), mp.mpf(10000), mp.mpf(-10000)]
xs += [mp.mpf(random.uniform(-60, 60)) for _ in range(500)]
xs += [k * mp.pi + random.choice((-1, 1)) * mp.mpf("1e-25") for k in range(-25, 26)]
worst = worst_im = mp.mpf(0)
for x in xs:
    y = value(SIN, x)
    worst = max(worst, abs(y.real - mp.sin(x)))
    worst_im = max(worst_im, abs(y.imag))
assert worst < mp.mpf("1e-50") and worst_im < mp.mpf("1e-50"), (worst, worst_im)

result = {
    "what": "fully-EML tree for sin(x), leaves {1, x}, principal Log; an upper bound by explicit construction",
    "nodes": nodes(SIN),
    "parts": {"-i": nodes(NI), "P": nodes(P), "V": nodes(V), "-1": nodes(NEG1), "2": nodes(TWO),
              "1/2": nodes(HALF), "-2": nodes(NEG2)},
    "branch_cut": "two values lie exactly on the cut by derivation (-1 and -e^e); each is put on it, "
                  "every other value is required to be clear of it, and 60- and 120-digit runs must agree",
    "check": {"points": len(xs), "range": "[-10000, 10000], incl. 0, +-1e-30 and k*pi +- 1e-25",
              "digits": [60, 120], "max_abs_error": mp.nstr(worst, 3), "max_abs_imag": mp.nstr(worst_im, 3)},
    "tree": show(SIN),
}
out = pathlib.Path(__file__).resolve().parent / "results" / "sin_fully_eml.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(result, indent=1) + "\n")
print(f"sin(x): {result['nodes']} eml nodes; {len(xs)} points at 60 and 120 digits, "
      f"max |error| {result['check']['max_abs_error']}, max |Im| {result['check']['max_abs_imag']}")
