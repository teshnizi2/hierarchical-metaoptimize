"""Gated identity check for HIER=zpool endpoints (OPERATIONS gotcha 25).

Compares the FULL per-epoch trajectory, not the final number: a single endpoint
can agree by coincidence where the arms happen to cross, and the anchor
separation itself varies by an order of magnitude over a run.

Verdict rule:
    power = max over epochs |ref_A - ref_B|      (discriminating power)
    dev   = max over epochs |arm - its reference| (identity deviation)
    PASS iff power >= POWER_MIN and dev <= DEV_FRAC * power
"""
import sys, re, glob, os

POWER_MIN = 2.0    # pp; below this the regime cannot certify anything
DEV_FRAC  = 0.10   # identity deviation must be <=10% of discriminating power

def curve(rundir, name):
    fs = glob.glob(os.path.join(rundir, f"{name}-*.out"))
    if not fs:
        return None
    txt = open(fs[0], errors="ignore").read()
    return [float(x) for x in re.findall(r"Test Accuracy: ([0-9.]+)", txt)]

def dev(a, b):
    n = min(len(a), len(b))
    return max(abs(a[i] - b[i]) for i in range(n)), n

rundir = sys.argv[1]
prefix = sys.argv[2] if len(sys.argv) > 2 else "z3"
C = {k: curve(rundir, f"{prefix}-{k}") for k in
     ("ref-scalar", "ref-layer", "ref-weight", "l-r0", "l-r1", "w-r0", "w-r1")}
missing = [k for k, v in C.items() if not v]
if missing:
    print(f"MISSING: {missing}"); sys.exit(1)
ep = min(len(v) for v in C.values())
lens = {k: len(v) for k, v in C.items()}
if len(set(lens.values())) != 1:
    print(f"!! epoch counts differ, comparing first {ep}: {lens}")

for half, refA, refB, pairs in (
    ("layerwise",  "ref-scalar", "ref-layer",  [("l-r0", "ref-scalar"), ("l-r1", "ref-layer")]),
    ("weightwise", "ref-scalar", "ref-weight", [("w-r0", "ref-scalar"), ("w-r1", "ref-weight")]),
):
    power, _ = dev(C[refA], C[refB])
    print(f"\n=== {half} half ===")
    print(f"anchor {refA} vs {refB}: max separation over {ep} epochs = {power:.2f}pp "
          f"(final-epoch separation = {abs(C[refA][ep-1]-C[refB][ep-1]):.2f}pp)")
    if power < POWER_MIN:
        print(f"  TEST VOID — anchors separate by < {POWER_MIN}pp; nothing may be read.")
        continue
    for arm, ref in pairs:
        d, _ = dev(C[arm], C[ref])
        fin = abs(C[arm][ep-1] - C[ref][ep-1])
        frac = d / power
        ok = "PASS" if frac <= DEV_FRAC else "FAIL"
        print(f"  {arm:6s} == {ref:11s}: max dev {d:.2f}pp ({frac:5.1%} of power), "
              f"final dev {fin:.2f}pp  -> {ok}")
