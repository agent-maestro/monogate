"""Selected FEF-P2 source fixture."""

import math


def gaussian(x: float) -> float:
    return math.exp(-0.5 * x * x)
