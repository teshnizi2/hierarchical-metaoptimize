"""RULE-4 VALIDATION of the N_eff estimator used by frozen_agreement.py.

The estimator claims:  given per-record (frac_neg, frac_zero) over n coordinates,

    N / N_eff  =  ( (A - 1/2) / (A_null(n) - 1/2) )^2 ,   A = mean_t max(p_t, 1-p_t)

We check it against SIMULATED sign data with a KNOWN effective count.  Two generative
models, because the estimator must not be tuned to one of them:

  (1) BLOCK model.  n coordinates in K independent blocks of n/K perfectly-correlated
      signs.  Ground truth N_eff = K exactly.
  (2) COMMON-MODE model.  s_i = sign(c*u + sqrt(1-c^2)*e_i), u ~ N(0,1) shared,
      e_i ~ N(0,1) independent.  Here N_eff has no closed form in general, so this run
      reports what the estimator returns and checks the two limits c->0 (N_eff -> n) and
      c->1 (N_eff -> 1) come out right, plus MONOTONICITY in c.

A third check: the estimator must return N/N_eff ~= 1 on genuinely independent signs at
every n we use in the paper (6, 62, 14420, 11173962) -- i.e. no small-n or large-n bias.
"""
import math
import numpy as np

SQ2PI = math.sqrt(2.0 / math.pi)
RNG = np.random.default_rng(7)


def exact_null(n):
    if n > 5000:
        return 0.5 + SQ2PI * 0.5 / math.sqrt(n)
    n = int(round(n))
    lg = math.lgamma
    return sum(math.exp(lg(n + 1) - lg(k + 1) - lg(n - k + 1) - n * math.log(2.0))
               * max(k / n, 1 - k / n) for k in range(n + 1))


def estimate(P, n):
    """P[T] = fraction negative per record.  Returns estimated N/N_eff."""
    A = float(np.mean(np.maximum(P, 1 - P)))
    e0 = exact_null(n) - 0.5
    return ((A - 0.5) / e0) ** 2, A


def sim_block(n, K, T=500):
    """K independent blocks; every coordinate in a block shares one sign."""
    b = RNG.integers(0, 2, size=(T, K)) * 2 - 1
    sizes = np.full(K, n // K)
    sizes[: n - sizes.sum()] += 1
    P = ((b < 0) * sizes).sum(1) / n
    return estimate(P, n)


def sim_common(n, c, T=500):
    u = RNG.standard_normal((T, 1))
    e = RNG.standard_normal((T, n))
    s = np.sign(c * u + math.sqrt(max(0.0, 1 - c * c)) * e)
    return estimate((s < 0).mean(1), n)


def main():
    print("=" * 92)
    print("VALIDATION 1 -- BLOCK model, ground-truth N_eff = K exactly")
    print("=" * 92)
    print(f"{'n':>12} {'true K':>10} {'true N/Neff':>13} {'estimated':>12} {'ratio est/true':>16}")
    print("-" * 92)
    worst = 0.0
    for n in (62, 14420, 1_000_000):
        for K in (1, 2, 8, 64, 512):
            if K > n:
                continue
            est, _ = sim_block(n, K, T=4000)
            true = n / K
            r = est / true
            worst = max(worst, abs(math.log(r)))
            print(f"{n:>12,} {K:>10} {true:>13,.1f} {est:>12,.1f} {r:>16.3f}")
    print(f"\n  worst |log(est/true)| = {worst:.3f}  "
          f"({'PASS' if worst < 0.25 else 'FAIL'} at the 25%-in-log tolerance)")

    print("\n" + "=" * 92)
    print("VALIDATION 2 -- INDEPENDENT signs must give N/Neff ~ 1 at every n we report")
    print("=" * 92)
    print(f"{'n':>14} {'agree%':>10} {'null%':>10} {'N/Neff (want 1.00)':>22}")
    print("-" * 92)
    for n in (6, 62, 14_420, 11_173_962):
        # sample the binomial directly; simulating 11.17M bernoullis per record is wasteful
        P = RNG.binomial(n, 0.5, size=20000) / n
        est, A = estimate(P, n)
        print(f"{n:>14,} {100*A:>10.4f} {100*exact_null(n):>10.4f} {est:>22.3f}")

    print("\n" + "=" * 92)
    print("VALIDATION 3 -- COMMON-MODE model: monotone in c, correct limits")
    print("=" * 92)
    n = 14_420
    print(f"n = {n:,}")
    print(f"{'c (common-mode wt)':>20} {'agree%':>10} {'N/Neff':>12} {'implied Neff':>14}")
    print("-" * 92)
    prev = None
    mono = True
    for c in (0.0, 0.01, 0.03, 0.1, 0.3, 0.6, 0.9, 0.99):
        est, A = sim_common(n, c, T=4000)
        if prev is not None and est < prev - 0.05 * prev:
            mono = False
        prev = est
        print(f"{c:>20.2f} {100*A:>10.4f} {est:>12,.1f} {n/est:>14,.1f}")
    print(f"\n  monotone in c: {'PASS' if mono else 'FAIL'}")
    print("  c=0 must give N/Neff~1 and c=0.99 must give Neff~1 (a single shared sign).")


if __name__ == "__main__":
    main()
