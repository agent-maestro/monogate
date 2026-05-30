"""Round-trip target — should decompile to the structural twin of
forge/examples/gaussian.eml.
"""

import math


def gaussian(mu: float, sigma: float, x: float) -> float:
    dx = x - mu
    return math.exp(-dx * dx / (2.0 * sigma * sigma)) / sigma
