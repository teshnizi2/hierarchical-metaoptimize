"""Direction C, done under a CONTROLLED trajectory: meta-gradient sign agreement at FROZEN beta.

WHY THIS BATCH IS THE RIGHT ONE.  Every earlier agreement measurement in this campaign
(mx/probe_sig_*, gate*, p7free, p9) let beta adapt, so the five granularity arms had
*different training trajectories* by the time agreement was read.  Agreement and trajectory
were confounded and the confound runs the wrong way: a coarse arm that escapes a0 earlier
sits at a different loss-surface point than a fine arm that does not.

`fz-*` (alice2, 50 runs, 20 epochs, PROBE=100 -> 100 records) freezes beta
(`beta_true_min == beta_true_max == ln(a0)` on every record, verified below).  With beta
frozen the partition has NO effect on the parameter update, so all five arms run the
*identical* base trajectory and differ only in how the meta-gradient is aggregated.
This is the controlled version of the measurement.

THE STATISTIC AND ITS NULL.  Per record we observe frac_neg and frac_zero over the arm's
n_tot coordinates.  Let n = n_tot*(1-frac_zero) be the number of coordinates with a nonzero
meta-gradient and p = frac_neg/(1-frac_zero) the fraction of those that are negative.  We
report the cross-sectional majority

    A = mean_over_records max(p, 1-p)

Under independent coordinate signs p ~ Binom(n, 1/2)/n and

    E[max(p,1-p)] = 0.5 + E|p-0.5| -> 0.5 + sqrt(2/pi)/(2 sqrt(n))          (CLT)

which is the "null%" column.  This floor is NOT 0.5 and it is n-dependent: 6.35pp at n=62,
0.0150pp at n=11.17M.  Comparing a raw agreement percentage across granularities without
dividing by the floor is meaningless -- that error is what makes "53.1% vs 50.0000%" look
like a large effect when the same arm's own floor is 55.07%.

EFFECTIVE SAMPLE SIZE.  The whole 1/sqrt(N) noise-averaging argument for coarse step-size
granularity says: average N coordinate meta-gradients, get a sqrt(N) variance reduction.
If the coordinates are correlated the reduction is only sqrt(N_eff).  Because the majority
statistic's excess over 0.5 scales as 1/sqrt(n), the measured excess directly yields

    N / N_eff = ( excess_measured / excess_null )^2

reported as `N/Neff`.  This is the number the Adam-mini / Adalayer / SGG line assumes is 1.

EXACT NULL.  For small n (the m=6 arm) the CLT floor is wrong, so we also compute the exact
binomial E[max(p,1-p)] and use it whenever n < 1000.
"""
import json, os, math, glob, collections, statistics as st
import numpy as np
from fractions import Fraction

ROOT = os.path.join(os.path.dirname(__file__), "killtest_data", "fz")
SQ2PI = math.sqrt(2.0 / math.pi)
RESNET18_BLOCKS = [3, 12, 15, 15, 15, 2]

GRAN = {"scal": ("scalar", 1), "blk6": ("resnet18_blocks", 6), "lay": ("layerwise", 62),
        "node": ("nodewise", 14420), "w": ("weightwise", 11173962)}


def exact_null(n):
    """E[max(p,1-p)] for p = Binom(n,1/2)/n, computed exactly for moderate n."""
    if n > 5000:
        return 0.5 + SQ2PI * 0.5 / math.sqrt(n)
    n = int(round(n))
    if n < 1:
        return float("nan")
    lg = math.lgamma
    tot = 0.0
    for k in range(n + 1):
        lp = lg(n + 1) - lg(k + 1) - lg(n - k + 1) - n * math.log(2.0)
        tot += math.exp(lp) * max(k / n, 1 - k / n)
    return tot


_NULL_GRID = None


def neff_from_agreement(A):
    """Invert the exact null: return the K whose independent-coordinate majority statistic
    equals the observed A.  Using the CLT form 0.5+sqrt(2/pi)/(2 sqrt(K)) instead biases the
    answer by 1.57x at K=1 and 0.74x at K=2 (analysis/neff_validate.py, VALIDATION 1); it is
    accurate only for K >= 8.  Exact inversion removes that bias at every K."""
    global _NULL_GRID
    if _NULL_GRID is None:
        ks = np.unique(np.round(np.logspace(0, 3.7, 900)).astype(int))
        _NULL_GRID = (ks, np.array([exact_null(int(k)) for k in ks]))
    ks, vs = _NULL_GRID
    if A <= vs[-1]:                       # deep in the CLT-valid regime; invert analytically
        e = A - 0.5
        return (SQ2PI * 0.5 / e) ** 2 if e > 0 else float("inf")
    if A >= vs[0]:
        return 1.0
    i = int(np.searchsorted(-vs, -A))     # vs is decreasing in k
    k0, k1, v0, v1 = ks[i - 1], ks[i], vs[i - 1], vs[i]
    t = (v0 - A) / (v0 - v1) if v0 != v1 else 0.0
    return float(math.exp(math.log(k0) + t * (math.log(k1) - math.log(k0))))


def infer_ntot(recs):
    """block_sizes.json lies on nodewise (CORRECTIONS 16). Recover n_tot from the rational
    denominator of frac_neg / frac_zero instead."""
    nt = 1
    for r in recs[:400]:
        for v in (r.get("frac_neg"), r.get("frac_zero")):
            if v is not None and 0 < v < 1:
                nt = max(nt, Fraction(v).limit_denominator(20_000_000).denominator)
    return nt


def load(d):
    recs = []
    for l in open(os.path.join(d, "probe.jsonl")):
        l = l.strip()
        if l:
            try:
                recs.append(json.loads(l))
            except Exception:
                pass
    return recs


def frozen_check(recs):
    """Verify beta really is frozen: beta_true_min == beta_true_max on every record."""
    bad = [r["step"] for r in recs
           if abs(r.get("beta_true_max", 0) - r.get("beta_true_min", 0)) > 1e-9]
    return len(bad), (recs[0]["beta_true_min"] if recs else float("nan"))


def arm_stats(d, window=0.5):
    recs = load(d)
    if len(recs) < 8:
        return None
    nfrozen, b0 = frozen_check(recs)
    w = recs[int(len(recs) * (1 - window)):]
    nt = infer_ntot(recs)
    A, NN, NUL = [], [], []
    for r in w:
        fz, fn = r["frac_zero"], r["frac_neg"]
        if fz >= 1.0:
            continue
        n = nt * (1.0 - fz)
        if n < 2:
            continue
        p = fn / (1.0 - fz)
        A.append(max(p, 1 - p))
        NN.append(n)
        NUL.append(exact_null(n))
    if not A:
        return None
    a, nul = float(np.mean(A)), float(np.mean(NUL))
    exc, exc0 = a - 0.5, nul - 0.5
    nbar = float(np.mean(NN))
    neff = neff_from_agreement(a)
    return dict(run=os.path.basename(d), n_tot=nt, T=len(A), nbar=nbar,
                agree=a, null=nul, excess=exc, excess_null=exc0,
                ratio=(exc / exc0 if exc0 > 0 else float("nan")),
                neff=neff, n_over_neff=nbar / neff,
                fz=float(np.mean([r["frac_zero"] for r in w])),
                nfrozen=nfrozen, beta0=b0)


def powerlaw(by, a0):
    """N_eff = m / (N/Neff).  Fit log10 N_eff = c + s*log10 m, per seed, and report the
    spread over seeds.  s = 1 is the independence assumption the literature makes."""
    gs = [g for g in ("blk6", "lay", "node", "w") if by.get((g, a0))]
    if len(gs) < 3:
        return
    nseed = min(len(by[(g, a0)]) for g in gs)
    x = np.array([math.log10(GRAN[g][1]) for g in gs])
    slopes, inters = [], []
    for k in range(nseed):
        y = np.array([math.log10(by[(g, a0)][k]["neff"]) for g in gs])
        s, c = np.polyfit(x, y, 1)
        slopes.append(s); inters.append(c)
    s, sd = float(np.mean(slopes)), float(np.std(slopes, ddof=1))
    print(f"    power-law fit over m = {', '.join(format(GRAN[g][1], ',') for g in gs)}:")
    print(f"      N_eff  ~  m^({s:.3f} +- {sd:.3f})      "
          f"[independence assumption requires the exponent to be 1.000]")
    print(f"      per-seed exponents: " + ", ".join(f"{v:.3f}" for v in slopes))
    # per-decade increments, to show whether the power law is actually straight
    y = np.array([math.log10(np.mean([r["neff"] for r in by[(g, a0)]])) for g in gs])
    seg = [(gs[i], gs[i + 1], (y[i + 1] - y[i]) / (x[i + 1] - x[i])) for i in range(len(gs) - 1)]
    print("      segment slopes: " + ",  ".join(f"{a}->{b}: {v:.3f}" for a, b, v in seg))


def main():
    dirs = sorted(d for d in glob.glob(os.path.join(ROOT, "fz-*")) if os.path.isdir(d))
    by = collections.defaultdict(list)
    early = collections.defaultdict(list)
    for d in dirs:
        s = arm_stats(d)
        if s is None:
            continue
        name = os.path.basename(d)                      # fz-<gran>-a<3|6>-s<k>
        parts = name.split("-")
        g, a0 = parts[1], parts[2]
        by[(g, a0)].append(s)
        e = arm_stats(d, window=1.0)                    # whole run, incl. startup
        if e:
            early[(g, a0)].append(e)

    print("=" * 118)
    print("FROZEN-BETA meta-gradient sign agreement  (fz-*, alice2, R18/CIFAR-10, SGDm, "
          "20 ep, AUGMENT=1, steady window = last 50%)")
    print("=" * 118)
    nonfroz = sum(s["nfrozen"] for v in by.values() for s in v)
    print(f"beta-frozen verification: {nonfroz} records out of "
          f"{sum(s['T'] for v in by.values() for s in v)} have beta_true_max != beta_true_min "
          f"(0 expected)")
    for a0, lab in (("a3", "alpha0 = 1e-3"), ("a6", "alpha0 = 1e-6")):
        print(f"\n### {lab}")
        h = (f"{'granularity':18s} {'m':>12s} {'seeds':>5s} {'nonzero n':>13s} {'agree%':>10s} "
             f"{'null%':>10s} {'excess pp':>10s} {'null pp':>9s} {'N_eff':>10s} {'N/Neff':>9s}")
        print(h); print("-" * len(h))
        for g in ("scal", "blk6", "lay", "node", "w"):
            v = by.get((g, a0), [])
            if not v:
                continue
            gn, m = GRAN[g]
            def mu(k): return float(np.mean([s[k] for s in v]))
            def sd(k): return float(np.std([s[k] for s in v], ddof=1)) if len(v) > 1 else 0.0
            print(f"{gn:18s} {m:>12,} {len(v):>5d} {mu('nbar'):>13,.0f} "
                  f"{100*mu('agree'):>10.4f} {100*mu('null'):>10.4f} "
                  f"{100*mu('excess'):>10.4f} {100*mu('excess_null'):>9.4f} "
                  f"{mu('neff'):>10.1f} {mu('n_over_neff'):>9.2f}")
            print(f"{'':18s} {'':>12s} {'':>5s} {'':>13s} "
                  f"{'+-'+format(100*sd('agree'),'.4f'):>10s} {'':>10s} "
                  f"{'':>10s} {'':>9s} "
                  f"{'+-'+format(sd('neff'),'.1f'):>10s} {'+-'+format(sd('n_over_neff'),'.2f'):>9s}")
        powerlaw(by, a0)

    print("\n### robustness: steady window (last 50%) vs whole run, N_eff")
    h = f"{'granularity':18s} " + " ".join(f"{a:>18s}" for a in ("a0=1e-3 last50 / all", "a0=1e-6 last50 / all"))
    print(h)
    for g in ("blk6", "lay", "node", "w"):
        cells = []
        for a0 in ("a3", "a6"):
            v, e = by.get((g, a0), []), early.get((g, a0), [])
            if v and e:
                cells.append(f"{np.mean([s['neff'] for s in v]):8.1f} /{np.mean([s['neff'] for s in e]):8.1f}")
            else:
                cells.append(f"{'-':>18s}")
        print(f"{GRAN[g][0]:18s} " + " ".join(f"{c:>18s}" for c in cells))


if __name__ == "__main__":
    main()
