"""Inspect beta (log step-size) trajectory -- H3 runaway test."""
import json, sys, math

recs = [json.loads(l) for l in open(sys.argv[1] + "/probe.jsonl")]
print("records=%d" % len(recs))
idx = [0, len(recs)//4, len(recs)//2, 3*len(recs)//4, len(recs)-1]
for i in idx:
    r = recs[i]
    b = r["beta"]
    mn, mx = min(b), max(b)
    avg = sum(b)/len(b)
    nan = sum(1 for v in b if v != v)
    try:
        amax = "%.3e" % math.exp(mx)
    except OverflowError:
        amax = "inf"
    print("  step=%6d  beta: mean=%+.3f min=%+.3f max=%+.3f  alpha_max=%s  nan_groups=%d"
          % (r["step"], avg, mn, mx, amax, nan))
