"""Infer the TRUE n_tot frac_neg was computed over, from the rational denominators.

block_sizes.json records n_b = param_numels for nodewise AND weightwise alike, so it
reports 11.17M for both -- but nodewise's z vector is one entry per NODE, not per weight.
frac_neg = k/n_tot for integer k, so the true n_tot is the smallest N making every
observed frac_neg an integer multiple of 1/N.
"""
import json, sys, os
from fractions import Fraction

for d in sorted(sys.argv[1:]):
    p = os.path.join(d, "probe.jsonl")
    if not os.path.exists(p):
        continue
    vals = []
    for l in open(p):
        l = l.strip()
        if not l:
            continue
        try:
            r = json.loads(l)
        except Exception:
            continue
        for key in ("frac_neg", "frac_zero"):
            v = r.get(key)
            if v is not None and 0 < v < 1:
                vals.append(v)
    if not vals:
        print(f"{os.path.basename(d):30s} no usable fractions"); continue
    # limit_denominator over many samples: the true N is the LCM-ish upper envelope
    best = 1
    for v in vals[:400]:
        f = Fraction(v).limit_denominator(60_000_000)
        best = max(best, f.denominator)
    print(f"{os.path.basename(d):30s} inferred n_tot ~ {best:>12,}   (from {len(vals)} fractions)")
