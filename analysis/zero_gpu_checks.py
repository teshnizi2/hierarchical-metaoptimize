"""Two zero-GPU checks on logs we already have.

CHECK 1 (falsifier for our own headline): is the SCALAR arm's alpha actually
moving, or stuck near alpha0? If scalar never leaves alpha0 = 1e-6 while
layerwise reaches ~1e-2, then "+3.3pp for granularity" is really "+3.3pp for
having a working step size", i.e. an artifact of a broken scalar run.

CHECK 2: growth of the spread of beta across groups vs t. A free preview of the
horizon hypothesis (noise accumulating as a random walk in log alpha).
"""
import json, sys, os, glob, math

BASE = sys.argv[1] if len(sys.argv) > 1 else "."


def load(d):
    p = os.path.join(d, "probe.jsonl")
    if not os.path.exists(p):
        return None
    recs = []
    for line in open(p):
        try:
            recs.append(json.loads(line))
        except Exception:
            pass
    return recs or None


print("=" * 74)
print("CHECK 1  —  does the scalar arm's step size actually move?")
print("=" * 74)
print(f"{'run':34s}{'beta_0':>9s}{'beta_end':>10s}{'alpha_end':>12s}{'moved?':>8s}")
for d in sorted(glob.glob(os.path.join(BASE, "**", "probe_*"), recursive=True)):
    recs = load(d)
    if not recs:
        continue
    b0 = recs[0]["beta"]
    be = recs[-1]["beta"]
    m0 = sum(b0) / len(b0)
    me = sum(be) / len(be)
    try:
        ae = math.exp(me)
    except OverflowError:
        ae = float("inf")
    moved = "YES" if abs(me - m0) > 0.5 else "NO"
    print(f"{os.path.basename(d):34s}{m0:>9.2f}{me:>10.2f}{ae:>12.2e}{moved:>8s}")

print()
print("=" * 74)
print("CHECK 2  —  spread of beta across groups vs t   (sd ~ t^p; random walk => p=0.5)")
print("=" * 74)
print(f"{'run':34s}{'groups':>7s}{'sd_end':>9s}{'exponent p':>12s}")
for d in sorted(glob.glob(os.path.join(BASE, "**", "probe_*"), recursive=True)):
    recs = load(d)
    if not recs or len(recs[0]["beta"]) < 2:
        continue
    pts = []
    for r in recs:
        b = r["beta"]
        mu = sum(b) / len(b)
        sd = (sum((x - mu) ** 2 for x in b) / len(b)) ** 0.5
        if r["step"] > 0 and sd > 0:
            pts.append((math.log(r["step"]), math.log(sd)))
    if len(pts) < 5:
        continue
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    p_exp = sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx if sxx else float("nan")
    b = recs[-1]["beta"]
    mu = sum(b) / len(b)
    sd_end = (sum((x - mu) ** 2 for x in b) / len(b)) ** 0.5
    print(f"{os.path.basename(d):34s}{len(b):>7d}{sd_end:>9.3f}{p_exp:>12.3f}")
