"""Small stats helpers for honest reporting of small-n rates.

We report Wilson score intervals for proportions: at n=5 the point estimates are saturated (0/5 and
5/5) and a bootstrap over identical samples is degenerate, whereas Wilson gives a sensible interval
that makes the under-powering explicit (e.g. 0/5 -> [0.00, 0.43], 5/5 -> [0.57, 1.00]).
"""

from __future__ import annotations

from math import sqrt


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for k successes out of n (default 95%). n=0 -> the whole [0,1]."""
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def fmt_rate(k: int, n: int) -> str:
    """'k/n = 0.00 [lo, hi]' with a 95% Wilson interval."""
    lo, hi = wilson_ci(k, n)
    rate = (k / n) if n else 0.0
    return f"{k}/{n} = {rate:.2f} [{lo:.2f}, {hi:.2f}]"


def fisher_p(k1: int, n1: int, k2: int, n2: int) -> float:
    """Two-sided Fisher exact p-value for the difference between two proportions.

    Tests the DIFFERENCE directly (unlike comparing whether two CIs overlap, which is not a test).
    NOTE: valid only if the samples are independent draws — here they are resamples of ONE base
    trajectory/prompt, so a small p means "a large effect here", not a task-population claim.
    """
    from scipy.stats import fisher_exact

    _, p = fisher_exact([[k1, n1 - k1], [k2, n2 - k2]])
    return float(p)
