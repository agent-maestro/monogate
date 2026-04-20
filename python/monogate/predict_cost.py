"""SuperBEST v3 cost predictor."""
from __future__ import annotations

UNIT: dict[str, int] = {
    'exp': 1, 'ln': 1, 'log': 1,
    'neg': 2, 'recip': 2, 'mul': 2, 'sub': 2,
    'div': 1, 'pow': 3,
    'add': 3,       # positive domain default
    'add_gen': 11,
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
