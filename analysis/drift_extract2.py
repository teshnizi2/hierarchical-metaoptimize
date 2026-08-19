"""Extract drift/step, cross-group sign-agreement and cross-group beta dispersion.

Supersedes bin/drift_extract.py, which had two defects found in cycle 20:
  1. its "structural check" printed spread = beta_true_max - beta_true_min, but the probe
     writes those two fields IDENTICALLY on every arm (layerwise included), so the check
     read 0.0000 by construction and could never fail.  Replaced by sd_beta, the genuine
     standard deviation across the per-group beta vector.
  2. frac_neg on a SCALAR arm is computed over a 1-element list, so per record it is 0.0
     or 1.0 and its mean is the fraction of TIMESTEPS the single coordinate was negative
     -- not cross-coordinate agreement.  It is now reported as n/a.

drift = |mean(beta_last) - mean(beta_first)| / steps, over steps 1000-7500 (FINDINGS c7 §1).
"""
import json, sys, os, statistics as st

LO, HI = 1000, 7500
print(f"{'arm':26s} {'G':>6} {'recs':>5} {'drift/step':>11} {'frac_neg':>9} {'excess%':>8} {'sd_beta':>9} {'range_beta':>11}")
for d in sorted(sys.argv[1:]):
    p = os.path.join(d, "probe.jsonl")
    name = os.path.basename(d)
    if not os.path.exists(p):
        continue
    recs = [json.loads(l) for l in open(p) if l.strip()]
    w = [r for r in recs if LO <= r["step"] <= HI]
    if len(w) < 2:
        print(f"{name:26s} {'':>6} {len(recs):>5}  window has {len(w)} rec(s) -- INCOMPLETE"); continue
    G = len(w[-1]["beta"])
    b0 = sum(w[0]["beta"])/G_first if (G_first:=len(w[0]["beta"])) else 0
    b1 = sum(w[-1]["beta"])/G
    drift = abs(b1-b0)/(w[-1]["step"]-w[0]["step"])
    if G < 2:
        fn_s, ex_s = "      n/a", "     n/a"
    else:
        fn = sum(r["frac_neg"] for r in w)/len(w)
        fn_s, ex_s = f"{fn:>9.4f}", f"{100*abs(fn-0.5):>8.2f}"
    # genuine cross-group dispersion of the log step sizes, averaged over the window
    sds  = [st.pstdev(r["beta"]) for r in w if len(r["beta"]) > 1]
    rngs = [max(r["beta"])-min(r["beta"]) for r in w if len(r["beta"]) > 1]
    sd_s  = f"{st.mean(sds):>9.4f}"  if sds  else "      n/a"
    rng_s = f"{st.mean(rngs):>11.4f}" if rngs else "        n/a"
    print(f"{name:26s} {G:>6} {len(recs):>5} {drift:>11.3e} {fn_s} {ex_s} {sd_s} {rng_s}")
