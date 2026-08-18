"""H1 test: does per-group meta-gradient SNR scale as sqrt(n_b)?
Regress log(SNR_b) on log(n_b). H1 predicts slope ~ +0.5."""
import json, sys, math

d = sys.argv[1]
nb = json.load(open(d + "/block_sizes.json"))["n_b"]
recs = [json.loads(l) for l in open(d + "/probe.jsonl")]
last = recs[-1]
snr = last["snr"]
print(f"stepsize_type groups={len(nb)}  probe records={len(recs)}  final step={last['step']}")
print(f"n_b range: {min(nb):,} .. {max(nb):,}  ({math.log10(max(nb)/min(nb)):.1f} decades)")

pts = [(math.log(n), math.log(s)) for n, s in zip(nb, snr) if s > 0 and n > 0]
if len(pts) < 5:
    print("too few usable points"); sys.exit()
n = len(pts)
mx = sum(p[0] for p in pts) / n
my = sum(p[1] for p in pts) / n
sxy = sum((p[0]-mx)*(p[1]-my) for p in pts)
sxx = sum((p[0]-mx)**2 for p in pts)
syy = sum((p[1]-my)**2 for p in pts)
slope = sxy / sxx
r = sxy / math.sqrt(sxx*syy) if sxx*syy > 0 else float('nan')
print(f"\nlog(SNR) = {slope:+.3f} * log(n_b) + {my - slope*mx:+.3f}    r = {r:+.3f}  (n={n})")
print(f"H1 predicts slope = +0.50")
verdict = "CONSISTENT with H1" if 0.3 < slope < 0.7 else ("OPPOSITE sign" if slope < 0 else "NOT consistent")
print(f"=> {verdict}")

# show the extremes
z = sorted(zip(nb, snr))
print("\nsmallest groups:  " + ", ".join(f"n={n:,}:SNR={s:.3f}" for n, s in z[:4]))
print("largest groups:   " + ", ".join(f"n={n:,}:SNR={s:.3f}" for n, s in z[-4:]))
