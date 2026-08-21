"""Synthetic ground-truth validation for analysis/twochannel.py.

Standing rule (CORRECTIONS 28.3): validate an estimator against simulated ground truth
BEFORE reducing real data with it.  The CLT-floor bug that CORRECTIONS 26 and 28.3 both
came from was caught exactly this way.

Standing rule (CORRECTIONS 33): a null may not be reported as evidence of absence until the
minimum effect the test could resolve has been computed.  VALIDATION 5 checks that the
reducer's printed rho_min really is its 2-sd resolution, by measuring the false-positive and
detection rates against simulation.

Two structurally DIFFERENT generators are used, so the estimator cannot pass by merely
recovering its own assumptions:
  * GEN-A  latent population fraction  P_t, then K_t ~ Binom(n, P_t)   (matches the model)
  * GEN-B  one-factor model on INDIVIDUAL coordinate signs, with a per-coordinate marginal
           bias and a shared latent factor -- the estimator never sees individual signs.

Run:  python3 -m pytest tests/test_twochannel.py -q
  or: python3 tests/test_twochannel.py
"""
import os, sys, math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis"))
from twochannel import decompose, infer_ntot  # noqa: E402

RNG = np.random.default_rng(20260821)


# ----------------------------------------------------------------- generators
def gen_A(T, n, pbar, rho, rng):
    """Latent population fraction with intraclass correlation rho, then binomial draws."""
    pq = pbar * (1.0 - pbar)
    sd = math.sqrt(max(rho, 0.0) * pq)
    P = np.clip(pbar + sd * rng.standard_normal(T), 1e-6, 1 - 1e-6)
    K = rng.binomial(n, P)
    frac_neg = K / n
    return frac_neg, np.zeros(T)


def gen_B(T, n, pbar, rho, rng, n_coord=4000):
    """One-factor model on individual signs.  Coordinate i is negative when
    u_i,t < thresh, with u_i,t = sqrt(rho)*f_t + sqrt(1-rho)*e_i,t (both standard normal),
    so the latent pairwise correlation of the underlying variable is exactly rho.
    n_coord coordinates are simulated and the fraction negative is scaled to n."""
    thresh = _probit(pbar)
    f = rng.standard_normal((T, 1))
    e = rng.standard_normal((T, n_coord))
    u = math.sqrt(rho) * f + math.sqrt(1.0 - rho) * e
    frac = (u < thresh).mean(axis=1)
    # resample to the requested n so the independent floor matches n, not n_coord
    K = rng.binomial(n, np.clip(frac, 1e-6, 1 - 1e-6))
    return K / n, np.zeros(T)


def _probit(p):
    # Acklam-free: bisection is plenty at this precision
    lo, hi = -8.0, 8.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0))) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# ----------------------------------------------------------------- validations
def test_v1_pure_independence_is_a_null():
    """VALIDATION 1: rho=0, no bias -> v_common consistent with 0, and the whole budget
    is the independent channel."""
    bad = []
    for n in (62, 14420, 1_000_000):
        zs = []
        for rep in range(40):
            fn, fz = gen_A(100, n, 0.5, 0.0, RNG)
            r = decompose(fn, fz, n)
            zs.append(r["z_common"])
        z = float(np.mean(zs))
        if abs(z) > 0.6:                      # mean of 40 z-scores; se ~ 1/sqrt(40) = 0.16
            bad.append((n, z))
    assert not bad, f"independence null is biased: {bad}"


def test_v2_recovers_known_rho_genA():
    """VALIDATION 2: rho is recovered over 5 decades of n and 3 of rho -- but only to the
    precision the test's OWN power bound allows.  Asserting 20% recovery at a rho below
    rho_min would be asserting precision the instrument does not have, which is the error
    CORRECTIONS 33 was written about.  Above 3*rho_min we demand 20%; below it we demand
    only consistency within the stated resolution."""
    bad = []
    for n in (62, 14420, 11_173_962):
        for rho in (1e-3, 1e-2, 1e-1):
            est, rmins = [], []
            for rep in range(30):
                fn, fz = gen_A(100, n, 0.5, rho, RNG)
                r = decompose(fn, fz, n)
                est.append(r["rho_s"])
                rmins.append(r["rho_min"])
            got = float(np.mean(est))
            rho_min = float(np.mean(rmins))
            if rho >= 3 * rho_min:
                if not (0.8 * rho <= got <= 1.2 * rho):
                    bad.append(("resolved", n, rho, got, rho_min))
            elif abs(got - rho) > rho_min:
                bad.append(("unresolved", n, rho, got, rho_min))
    assert not bad, f"rho_s not recovered: {bad}"


def test_v3_recovers_known_rho_genB_structurally_different():
    """VALIDATION 3: the same recovery on a one-factor model over individual signs.
    The sign correlation is smaller than the latent-variable rho (tetrachoric shrinkage),
    so we check the estimator tracks the SIGN correlation implied by the generator."""
    for n in (14420, 1_000_000):
        for rho_lat in (0.01, 0.05):
            est, truth = [], []
            for rep in range(30):
                fn, fz = gen_B(100, n, 0.5, rho_lat, RNG, n_coord=20000)
                est.append(decompose(fn, fz, n)["rho_s"])
                # ground truth for the SIGN correlation at pbar=0.5 is the orthant formula
                truth.append((2.0 / math.pi) * math.asin(rho_lat))
            got, want = float(np.mean(est)), float(np.mean(truth))
            assert abs(got - want) < 0.35 * want + 2e-4, (
                f"gen-B n={n} rho_lat={rho_lat}: got {got:.5g} want {want:.5g}")


def test_v4_bias_and_common_mode_are_separated():
    """VALIDATION 4: the channel the estimator attributes must match the channel simulated.
    Pure bias must NOT leak into v_common, and pure common mode must NOT leak into v_bias."""
    n, T = 14420, 100
    # (a) pure marginal bias, zero common mode
    fn, fz = gen_A(T, n, 0.53, 0.0, RNG)
    r = decompose(fn, fz, n)
    assert r["share_bias"] > 0.95, f"bias not attributed to bias: {r['share_bias']:.3f}"
    assert abs(r["z_common"]) < 4.0, f"bias leaked into common mode: z={r['z_common']:.2f}"
    # (b) pure common mode, zero bias
    fn, fz = gen_A(T, n, 0.5, 0.02, RNG)
    r = decompose(fn, fz, n)
    assert r["share_common"] > 0.9, f"common mode not attributed: {r['share_common']:.3f}"
    assert r["v_bias"] < 0.15 * r["v_common"], "common mode leaked into bias"


def test_v5_rho_min_is_the_true_2sd_resolution():
    """VALIDATION 5: the printed power bound must be honest.  At rho = rho_min the test
    should detect most of the time; at rho = 0 it should almost never fire."""
    n, T = 14420, 100
    r0 = decompose(*gen_A(T, n, 0.5, 0.0, RNG), n)
    rho_min = r0["rho_min"]
    fp = sum(decompose(*gen_A(T, n, 0.5, 0.0, RNG), n)["z_common"] > 2.0 for _ in range(200))
    tp = sum(decompose(*gen_A(T, n, 0.5, rho_min, RNG), n)["z_common"] > 2.0 for _ in range(200))
    assert fp / 200 < 0.10, f"false-positive rate {fp/200:.3f} too high for a 2-sd threshold"
    assert tp / 200 > 0.40, f"detection at rho_min only {tp/200:.3f}"


def test_v6_rho_min_falls_with_n():
    """VALIDATION 6: the claim that motivates using this instrument instead of kt2's
    pairwise test -- resolution IMPROVES with aggregation."""
    prev = None
    for n in (62, 14420, 11_173_962):
        r = decompose(*gen_A(100, n, 0.5, 0.0, RNG), n)
        if prev is not None:
            assert r["rho_min"] < prev / 10.0, f"rho_min did not fall with n at n={n}"
        prev = r["rho_min"]


def test_v7_fast_slow_split():
    """VALIDATION 7: a smooth drift must land in v_slow_common, not v_fast_common."""
    n, T = 14420, 200
    pbar = 0.5
    drift = np.linspace(-0.01, 0.01, T)           # smooth trend, no fast fluctuation
    K = RNG.binomial(n, np.clip(pbar + drift, 1e-6, 1 - 1e-6))
    r = decompose(K / n, np.zeros(T), n)
    assert r["v_slow_common"] > 3.0 * abs(r["v_fast_common"]), (
        f"drift misattributed: slow={r['v_slow_common']:.3g} fast={r['v_fast_common']:.3g}")
    # and a purely fast common mode must land the other way
    fn, fz = gen_A(T, n, 0.5, 0.02, RNG)
    r = decompose(fn, fz, n)
    assert r["v_fast_common"] > 0.5 * r["v_common"], "fast common mode lost to the slow bin"


def test_v10_autocorrelation_correction():
    """VALIDATION 10: probe records are 25 optimiser steps apart in a smooth run, so p_t is
    autocorrelated and the chi-square sd would overstate z.  tau must be ~1 on white noise
    (so the correction is inert where it should be) and >1 on an AR(1) common mode."""
    n, T = 14420, 400
    # white-noise common mode -> tau ~ 1
    fn, fz = gen_A(T, n, 0.5, 0.02, RNG)
    r_white = decompose(fn, fz, n)
    assert r_white["tau"] < 1.6, f"tau inflated on white noise: {r_white['tau']:.2f}"
    # AR(1) common mode with the SAME marginal variance -> tau clearly >1, z deflated
    phi, pbar, rho = 0.8, 0.5, 0.02
    pq = pbar * (1 - pbar)
    sd_innov = math.sqrt(rho * pq * (1 - phi ** 2))
    P, x = np.empty(T), 0.0
    for t in range(T):
        x = phi * x + sd_innov * RNG.standard_normal()
        P[t] = pbar + x
    K = RNG.binomial(n, np.clip(P, 1e-6, 1 - 1e-6))
    r_ar = decompose(K / n, np.zeros(T), n)
    assert r_ar["tau"] > 2.0, f"tau did not detect AR(1): {r_ar['tau']:.2f}"
    # the point estimate of rho_s must be UNAFFECTED by autocorrelation
    assert 0.7 * rho < r_ar["rho_s"] < 1.3 * rho, (
        f"autocorrelation corrupted the point estimate: {r_ar['rho_s']:.4g}")
    # ...but the reported resolution must get WORSE, not better
    assert r_ar["rho_min"] > r_white["rho_min"], "rho_min did not widen under autocorrelation"


def test_v11_heterogeneity_is_conservative():
    """VALIDATION 11: real coordinates are NOT identically distributed -- each weight has its
    own marginal sign preference.  Independent-but-heterogeneous coordinates have
    Var(frac_neg) = mean_i p_i(1-p_i)/n <= pbar(1-pbar)/n, so the estimator must NEVER
    report a positive common mode for them.  This is what makes a positive reading a lower
    bound rather than an artefact."""
    n_coord, T = 20000, 200
    p_i = RNG.beta(2.0, 2.0, size=n_coord)          # strong per-coordinate heterogeneity
    draws = (RNG.random((T, n_coord)) < p_i).mean(axis=1)
    r = decompose(draws, np.zeros(T), n_coord)
    assert r["z_common"] < 2.0, (
        f"heterogeneity produced a spurious common mode: z={r['z_common']:.2f}, "
        f"rho_s={r['rho_s']:.3g}")


def test_v8_infer_ntot_matches_known_denominator():
    """VALIDATION 8: n_tot recovery, which CORRECTIONS 16 says cannot come from config."""
    for n in (62, 14420, 11_173_962):
        K = RNG.integers(1, n, size=50)
        recs = [{"frac_neg": float(k) / n, "frac_zero": 0.0} for k in K]
        assert infer_ntot(recs) == n, f"n_tot mis-inferred at n={n}"


def test_v9_frac_zero_is_honoured():
    """VALIDATION 9: with a third of coordinates exactly zero, the effective n is n_tot*2/3
    and the independent floor must scale accordingly, else rho is inflated 1.5x."""
    n_tot, T, fzv = 30000, 150, 1.0 / 3.0
    n_eff = int(n_tot * (1 - fzv))
    K = RNG.binomial(n_eff, 0.5, size=T)
    p = K / n_eff
    fn = p * (1 - fzv)
    r = decompose(fn, np.full(T, fzv), n_tot)
    assert abs(r["nbar"] - n_eff) < 2, f"nbar={r['nbar']} != {n_eff}"
    assert abs(r["z_common"]) < 3.0, f"frac_zero mishandled: z={r['z_common']:.2f}"


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
