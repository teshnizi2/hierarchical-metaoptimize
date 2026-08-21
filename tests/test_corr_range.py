"""Ground-truth validation for analysis/corr_range.py.

The claim the inversion supports is "rho_w implied FALLS with block size, therefore the
correlation is short-range".  That claim is only worth anything if the inversion returns a
CONSTANT rho_w on data that really does come from a single global factor.  VALIDATION 2 is
the one that matters: it simulates a genuine global factor over 11.17M coordinates and
checks the inversion does NOT manufacture a spurious scale dependence.
"""
import os, sys, math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis"))
from corr_range import implied_rho_w, group_rho_from_weight, sign_to_latent  # noqa: E402
from twochannel import decompose  # noqa: E402

RNG = np.random.default_rng(20260821)


def _Phi(x):
    return 0.5 * (1.0 + np.vectorize(math.erf)(np.asarray(x, float) / math.sqrt(2.0)))


def one_factor_frac(T, m, rho_g, rng, thresh=0.0):
    """EXACT one-factor draw of the negative-fraction over m exchangeable coordinates.

    Simulating m coordinates as `min(m, 30000)` explicit columns and then drawing
    Binom(m, colmean) is WRONG at large m: the proxy columns inject sampling variance
    0.25/30000, which at m = 11.17M is 375x the true binomial floor and swamps the very
    common mode being measured.  That artefact -- not the estimator -- is what made the
    first version of VALIDATION 2 fail.  Conditioning on the latent factor f_t and drawing
    K_t ~ Binom(m, P(u < thresh | f_t)) is exact for any m.
    """
    f = rng.standard_normal(T)
    p = _Phi((thresh - math.sqrt(rho_g) * f) / math.sqrt(max(1.0 - rho_g, 1e-12)))
    K = rng.binomial(m, np.clip(p, 1e-12, 1 - 1e-12))
    return K / m


def test_c1_forward_inverse_roundtrip():
    """VALIDATION 1: implied_rho_w is the exact inverse of group_rho_from_weight."""
    for rho_w in (1e-8, 1e-6, 1e-4, 1e-2):
        for k in (1, 775, 180_225, 11_173_962):
            rs = group_rho_from_weight(rho_w, k)
            back = implied_rho_w(rs, k)
            assert abs(back - rho_w) < 1e-9 + 0.02 * rho_w, (
                f"roundtrip failed rho_w={rho_w} k={k}: got {back:.4g}")


def test_c2_global_factor_gives_CONSTANT_implied_rho_w():
    """VALIDATION 2 (the load-bearing one).  Simulate a TRUE single global factor over
    N coordinates, aggregate into m groups at four granularities, run the SAME estimator
    the real pipeline uses, and invert.  A global factor must give a flat rho_w across
    rungs -- if the pipeline manufactured a falling profile here, the real falling profile
    would be an artefact."""
    N, T = 11_173_962, 400
    rho_w = 3.0e-6                       # latent per-weight correlation, global
    got = {}
    for m in (62, 14_420, N):
        k = N / m
        rho_g = rho_w * k / (1.0 + (k - 1) * rho_w)      # latent corr between group sums
        frac = one_factor_frac(T, m, rho_g, RNG)
        r = decompose(frac, np.zeros(T), m)
        got[m] = implied_rho_w(r["rho_s"], k)
    vals = [v for v in got.values() if np.isfinite(v)]
    assert len(vals) == 3, f"inversion produced non-finite values: {got}"
    spread = max(vals) / min(vals)
    assert spread < 3.0, (
        f"a TRUE global factor produced a {spread:.1f}x spread in implied rho_w -- the "
        f"inversion manufactures scale dependence: {got}")


def test_c3_short_range_factor_gives_FALLING_implied_rho_w():
    """VALIDATION 3: the converse.  When correlation is confined to blocks of size B, the
    inversion must report a rho_w that FALLS once k exceeds B -- the signature the real
    data is being read for."""
    N, T, B = 11_173_962, 400, 1000
    rho_local = 3.0e-3                   # correlation inside a block of B coordinates only
    got = {}
    for m in (62, 14_420, N):
        k = N / m
        # a sum of k coordinates contains min(k,B) correlated ones per block, k/B blocks;
        # the shared component between two disjoint sums is zero unless they share a block
        shared = 0.0 if k > B else rho_local * k / (1.0 + (k - 1) * rho_local)
        frac = one_factor_frac(T, m, shared, RNG)
        r = decompose(frac, np.zeros(T), m)
        got[m] = implied_rho_w(r["rho_s"], k)
    fine, coarse = got[N], got[62]
    assert np.isfinite(fine) and fine > 0, f"fine rung lost: {got}"
    assert (not np.isfinite(coarse)) or coarse < fine / 10.0, (
        f"short-range structure did not produce a falling profile: {got}")


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS  {name}")
            except AssertionError as e:
                fails += 1
                print(f"FAIL  {name}: {e}")
    print(f"\n{'ALL PASS' if not fails else str(fails) + ' FAILURES'}")
    sys.exit(1 if fails else 0)
