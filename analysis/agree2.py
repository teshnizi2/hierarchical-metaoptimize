"""Cross-coordinate sign-agreement of the meta-gradient, done defensibly.

Three defects it fixes relative to a naive read of probe.jsonl:

 1. n_tot.  block_sizes.json writes n_b = param_numels for BOTH nodewise and weightwise,
    so it claims 11,173,962 coordinates for nodewise, which actually has 14,420 nodes.
    We instead INFER n_tot as the denominator of the observed frac_neg rationals.
    Verified: this returns 62 / 6 / 14,420 / 11,173,962 for layerwise / blocks / nodewise
    / weightwise, matching the independently-recorded group counts exactly.

 2. Zeros.  frac_neg = (z<0)/n_tot, with exact zeros counted in neither direction.
    Agreement is measured among NONZERO coordinates: p = frac_neg/(1-frac_zero).

 3. Time-averaging vs per-step.  mean(frac_neg) then max(p,1-p) measures whether the
    meta-gradient is SYSTEMATICALLY one-signed across the window; it reads 50% if the
    coordinates agree strongly at each step but the majority sign flips over time.
    We therefore also report the per-step statistic mean_r max(p_r, 1-p_r).  That one is
    biased UP by sampling noise, so we print its independence expectation
    E = 0.5 + sqrt(2/pi)/(2 sqrt(n_nz)) beside it.  A claim needs BOTH: 'sys' says there
    is a persistent common direction, 'step' above its own null says coordinates agree
    within a step.  Neither alone is sign-agreement.
"""
import json, sys, os, math, statistics as st
from fractions import Fraction

SQ2PI = math.sqrt(2.0 / math.pi)


def load(d):
    p = os.path.join(d, "probe.jsonl")
    if not os.path.exists(p):
        return []
    out = []
    for l in open(p):
        l = l.strip()
        if not l:
            continue
        try:
            out.append(json.loads(l))
        except Exception:
            pass
    return out


def infer_ntot(recs):
    best = 1
    seen = 0
    for r in recs:
        for k in ("frac_neg", "frac_zero"):
            v = r.get(k)
            if v is not None and 0 < v < 1:
                best = max(best, Fraction(v).limit_denominator(100_000_000).denominator)
                seen += 1
        if seen > 400:
            break
    return best


def block(recs, ntot, lo, hi):
    n = len(recs)
    w = recs[int(lo * n): max(int(hi * n), int(lo * n) + 2)]
    if len(w) < 2:
        return None
    G = len(w[-1]["beta"])
    fz = st.mean(r["frac_zero"] for r in w)
    fn = st.mean(r["frac_neg"] for r in w)
    n_nz = ntot * (1 - fz)

    p_sys = fn / (1 - fz) if fz < 1 else float("nan")
    agree_sys = max(p_sys, 1 - p_sys)

    ps = []
    for r in w:
        z = r["frac_zero"]
        if z >= 1:
            continue
        pr = r["frac_neg"] / (1 - z)
        ps.append(max(pr, 1 - pr))
    agree_step = st.mean(ps) if ps else float("nan")
    null_step = 0.5 + SQ2PI * 0.5 / math.sqrt(n_nz) if n_nz > 0 else float("nan")

    b0, b1 = st.mean(w[0]["beta"]), st.mean(w[-1]["beta"])
    ds = w[-1]["step"] - w[0]["step"]
    drift = abs(b1 - b0) / ds if ds else float("nan")
    sds = [st.pstdev(r["beta"]) for r in w if len(r["beta"]) > 1]
    return dict(G=G, ntot=ntot, fz=fz, agree_sys=agree_sys, agree_step=agree_step,
                null_step=null_step, drift=drift,
                sd_beta=st.mean(sds) if sds else float("nan"), beta_end=b1)


def run(dirs, lo, hi, label):
    print(f"\n### {label}")
    hdr = (f"{'arm':30s} {'n_tot':>11} {'frac0':>7} {'sys%':>9} {'step%':>9} "
           f"{'null%':>9} {'step-null':>10} {'sd_beta':>9} {'drift/step':>11}")
    print(hdr); print("-" * len(hdr))
    for d in sorted(dirs):
        recs = load(d)
        nm = os.path.basename(d)
        if not recs:
            print(f"{nm:30s}  (no records)"); continue
        nt = infer_ntot(recs)
        s = block(recs, nt, lo, hi)
        if not s:
            print(f"{nm:30s}  (window too short)"); continue
        if nt < 2:
            print(f"{nm:30s} {nt:>11} {s['fz']:>7.3f} {'n/a':>9} {'n/a':>9} {'n/a':>9} "
                  f"{'n/a':>10} {'n/a':>9} {s['drift']:>11.3e}")
            continue
        print(f"{nm:30s} {nt:>11,} {s['fz']:>7.3f} {100*s['agree_sys']:>9.4f} "
              f"{100*s['agree_step']:>9.4f} {100*s['null_step']:>9.4f} "
              f"{100*(s['agree_step']-s['null_step']):>10.4f} "
              f"{s['sd_beta']:>9.4f} {s['drift']:>11.3e}")


if __name__ == "__main__":
    dirs = [a for a in sys.argv[1:] if not a.startswith("-")]
    run(dirs, 0.50, 1.00, "STEADY window (last 50% of records)")
    run(dirs, 0.00, 0.20, "STARTUP window (first 20% of records)")
