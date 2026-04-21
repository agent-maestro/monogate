"""SuperBEST v5 cost predictor.

v5 changes (ADD-T1, 2026-04-20):
  - add=2n for ALL real x, y (LEdiv(x, DEML(y,1)) = x+y)
  - add_gen: 11n → 2n (no domain restriction needed)
  - add_pos: 3n → 2n (subsumed by unified add=2n)
  - The positive/general-domain split is eliminated.
  - Reference: ADD_T1_General_Addition_2n.tex, SuperBEST_v5_Structural_Audit.tex
"""
from __future__ import annotations

UNIT: dict[str, int] = {
    'exp': 1, 'ln': 1, 'log': 1,
    'neg': 2, 'recip': 1, 'mul': 2, 'sub': 2,
    'div': 2, 'pow': 3,
    'add': 2,       # v5 (ADD-T1): add=2n for ALL reals (was add_pos=3n)
    'add_pos': 2,   # legacy alias → same as add in v5
    'add_gen': 2,   # legacy alias → same as add in v5 (was 11n in v4/v3)
}

# bonus = NaiveCost(pattern) - 1
PATTERN_BONUS: dict[str, int] = {
    'EML':    3,   # exp(x)-ln(y), naive=4
    'DEML':   5,   # exp(-x)-ln(y), naive=6
    'EXL':    3,   # exp(x)*ln(y), naive=4
    'EDL':    2,   # exp(x)/ln(y), naive=3
    'EAL':    4,   # exp(x)+ln(y), naive=5
    'LEAd':   4,   # ln(exp(x)+y), naive=5
    'ELAd':   4,   # exp(x)*y, naive=5
    'LEdiv':  2,   # ln(exp(x)/y), naive=3
    'LEprod': 3,   # ln(exp(x)*y), naive=4
    'ELSb':   1,   # exp(x)-y, naive=4 (conservative)
    'EMN':    3,   # exp(x)*exp(y)=exp(x+y), naive=4
}


def naive_cost(ops: dict[str, int]) -> int:
    """Return NaiveCost for a dict of {op_name: count}."""
    return sum(UNIT.get(op, 2) * cnt for op, cnt in ops.items())


def predict_cost(
    ops: dict[str, int],
    patterns: list[str] | None = None,
    shared: int = 0,
) -> int:
    """
    Predict SuperBEST v3 node count.

    Args:
        ops: dict mapping operation name to count,
             e.g. {'exp': 1, 'mul': 2, 'div': 1}
        patterns: matched compound pattern names, e.g. ['EML', 'EXL']
        shared: sharing discount (0 for single-formula expressions)

    Returns:
        Predicted node count (>= 0).
    """
    nc = naive_cost(ops)
    pb = sum(PATTERN_BONUS.get(p, 0) for p in (patterns or []))
    return max(0, nc - shared - pb)
