"""Tests for the Wilson-interval helpers."""

from d2b.stats import fmt_rate, wilson_ci


def test_empty_is_full_interval():
    assert wilson_ci(0, 0) == (0.0, 1.0)


def test_zero_successes_lo_is_zero_hi_below_one():
    lo, hi = wilson_ci(0, 5)
    assert lo == 0.0
    assert 0.0 < hi < 1.0  # under-powered: hi is well above 0 (~0.43)


def test_all_successes_hi_is_one_lo_above_zero():
    lo, hi = wilson_ci(5, 5)
    assert hi == 1.0
    assert 0.0 < lo < 1.0  # ~0.57


def test_symmetry():
    lo0, hi0 = wilson_ci(0, 5)
    lo5, hi5 = wilson_ci(5, 5)
    assert abs(lo0 - (1 - hi5)) < 1e-9
    assert abs(hi0 - (1 - lo5)) < 1e-9


def test_interval_contains_point_estimate():
    for k in range(6):
        lo, hi = wilson_ci(k, 5)
        assert lo <= k / 5 <= hi


def test_more_data_tightens_interval():
    wide = wilson_ci(1, 4)
    narrow = wilson_ci(25, 100)  # same 0.25 rate, more data
    assert (narrow[1] - narrow[0]) < (wide[1] - wide[0])


def test_fmt_rate_string():
    assert fmt_rate(0, 5).startswith("0/5 = 0.00 [0.00, ")
    assert fmt_rate(5, 5).endswith(", 1.00]")


def test_fisher_p_extreme_is_significant_and_noise_is_not():
    from d2b.stats import fisher_p

    assert fisher_p(0, 5, 5, 5) < 0.01  # 0/5 vs 5/5 is significant
    assert fisher_p(4, 4, 2, 4) > 0.10  # 4/4 vs 2/4 at n=4 is not (~0.43)
