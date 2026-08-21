#!/usr/bin/env python3
"""IDEA 3 reducer -- alpha0-robustness width, head to head.

Written and unit-tested BEFORE the data landed, so the analysis is pre-registered
rather than chosen after seeing the curves (docs/IDEA3-robustness.md).

Reports, per arm:
    (i)   WIDTH of the region within 1pp / 2pp of that arm's OWN best, in decades
    (ii)  WORST-CASE plateau across the whole grid
    (iii) PEAK plateau
and then the tradeoff sentence: "costs X pp of peak, buys N decades of alpha0
insensitivity", where X is measured against the tuned AdamW+cosine reference.

Width convention (stated because it changes the number):
  the grid is 7 points spanning log10 alpha0 in [-6, -1].  A cell is IN-BAND if its
  plateau >= (arm's own best - tol).  Width is the span of the LARGEST CONTIGUOUS run
  of in-band cells, measured in decades between the first and last in-band grid point.
  A single in-band cell has width 0 decades and is reported as such -- it is not
  padded out to half a grid spacing.  Contiguity is required: a non-contiguous
  in-band set means the curve is not a plateau and the width is not meaningful, so
  the reducer prints a WARNING and reports only the largest contiguous run.

Usage:  python3 analysis/idea3_robustness.py [results/all_runs.csv]
        python3 analysis/idea3_robustness.py --selftest
"""
import csv
import math
import sys

# CORRECTIONS 30: the tuned non-meta peak reference, n=5, 100ep, AUGMENT=1, R18/C10.
TUNED_COSINE_REF = 94.417
TUNED_COSINE_SD = 0.113

GRID = [1e-6, 1e-5, 1e-4, 3e-4, 1e-3, 1e-2, 1e-1]

ARMS = {
    # label: (run-name prefix, human description)
    "A  fixed-lr AdamW": "i3a-",
    "B  MetaOptimize m=6": "i3b-",
    "B' clip control": "i3bc-",
}


def load(path):
    """Rows that are readable as final results, per the standing filters."""
    out = []
    for r in csv.DictReader(open(path)):
        if r.get("superseded") not in ("0", ""):
            continue
        try:
            if int(r["epochs_done"]) < 100:
                continue
            plateau = float(r["plateau"])
        except (ValueError, KeyError, TypeError):
            continue
        # CONTINUE-HERE gotcha: `collapsed` flags nothing; filter explicitly.
        r["_plateau"] = plateau
        out.append(r)
    return out


def cells(rows, prefix):
    """{alpha0: [plateau, ...]} for one arm, keyed by the float alpha0."""
    acc = {}
    for r in rows:
        if not r["run"].startswith(prefix):
            continue
        # i3b- must not swallow i3bc-
        if prefix == "i3b-" and r["run"].startswith("i3bc-"):
            continue
        acc.setdefault(float(r["alpha0"]), []).append(r["_plateau"])
    return acc


def mean_sd(v):
    m = sum(v) / len(v)
    if len(v) < 2:
        return m, float("nan")
    var = sum((x - m) ** 2 for x in v) / (len(v) - 1)
    return m, math.sqrt(var)


def width_decades(grid, means, tol):
    """Largest contiguous in-band run, in decades.  Returns (decades, lo, hi, gapped)."""
    present = [g for g in grid if g in means]
    if not present:
        return float("nan"), None, None, False
    best = max(means[g] for g in present)
    flags = [means[g] >= best - tol for g in present]
    gapped = False
    # find longest contiguous True run
    bi = bj = -1
    i = 0
    runs = 0
    while i < len(flags):
        if flags[i]:
            runs += 1
            j = i
            while j + 1 < len(flags) and flags[j + 1]:
                j += 1
            if bi < 0 or (j - i) > (bj - bi):
                bi, bj = i, j
            i = j + 1
        else:
            i += 1
    if runs > 1:
        gapped = True
    lo, hi = present[bi], present[bj]
    return math.log10(hi) - math.log10(lo), lo, hi, gapped


def report(path):
    rows = load(path)
    summary = {}
    for label, prefix in ARMS.items():
        acc = cells(rows, prefix)
        if not acc:
            print(f"\n=== {label} ({prefix}*) -- NO ROWS YET ===")
            continue
        means = {a: mean_sd(v)[0] for a, v in acc.items()}
        print(f"\n=== {label} ({prefix}*) ===")
        print(f"{'alpha0':>8} {'n':>3} {'plateau':>9} {'sd':>7}")
        for a in sorted(acc):
            m, s = mean_sd(acc[a])
            print(f"{a:>8.0e} {len(acc[a]):>3} {m:>9.3f} {s:>7.3f}")
        missing = [g for g in GRID if g not in acc]
        if missing:
            print("  INCOMPLETE -- missing grid points: "
                  + ", ".join(f"{g:.0e}" for g in missing))
        peak = max(means.values())
        worst = min(means.values())
        peak_a0 = max(means, key=lambda k: means[k])
        print(f"  (iii) PEAK      {peak:.3f} at alpha0={peak_a0:.0e}")
        print(f"  (ii)  WORST     {worst:.3f}   (grid span {peak - worst:.3f} pp)")
        for tol in (1.0, 2.0):
            w, lo, hi, gapped = width_decades(GRID, means, tol)
            flag = "  [WARNING: in-band set is NOT contiguous]" if gapped else ""
            print(f"  (i)   WIDTH within {tol:.0f}pp of own best: "
                  f"{w:.1f} decades  [{lo:.0e} .. {hi:.0e}]{flag}")
        summary[label] = dict(peak=peak, worst=worst, means=means,
                              w1=width_decades(GRID, means, 1.0)[0],
                              w2=width_decades(GRID, means, 2.0)[0],
                              complete=not missing)

    a = next((v for k, v in summary.items() if k.startswith("A")), None)
    b = next((v for k, v in summary.items() if k.startswith("B ")), None)
    bc = next((v for k, v in summary.items() if k.startswith("B'")), None)

    print("\n=== THE TRADEOFF ===")
    print(f"peak reference: tuned AdamW+cosine {TUNED_COSINE_REF:.3f} "
          f"+-{TUNED_COSINE_SD:.3f} (n=5, CORRECTIONS 30)")
    if not (a and b):
        print("  both arms needed; not computable yet.")
        return
    if not (a["complete"] and b["complete"]):
        print("  PROVISIONAL -- at least one arm is missing grid points (see above).")
    cost = TUNED_COSINE_REF - b["peak"]
    buys1 = b["w1"] - a["w1"]
    buys2 = b["w2"] - a["w2"]
    print(f"  MetaOptimize peak      {b['peak']:.3f}  -> costs {cost:+.3f} pp "
          f"of peak vs the tuned baseline")
    print(f"  fixed-lr AdamW peak    {a['peak']:.3f}")
    print(f"  width within 1pp:  arm A {a['w1']:.1f} dec   arm B {b['w1']:.1f} dec"
          f"   -> buys {buys1:+.1f} decades")
    print(f"  width within 2pp:  arm A {a['w2']:.1f} dec   arm B {b['w2']:.1f} dec"
          f"   -> buys {buys2:+.1f} decades")
    print(f"  worst case:        arm A {a['worst']:.3f}      arm B {b['worst']:.3f}"
          f"   -> {b['worst'] - a['worst']:+.3f} pp")
    if buys1 > 0:
        print(f"\n  CLAIM: MetaOptimize costs {cost:.2f} pp of peak accuracy and buys "
              f"{buys1:.1f} decades of alpha0 insensitivity (1pp band).")
    else:
        print("\n  REFUTED: MetaOptimize is NOT flatter than a fixed step size on this "
              "grid.  The parent paper's own robustness claim fails at m=6 on "
              "ResNet18/CIFAR-10.  Write it as the negative result it is.")

    if bc:
        top = 1e-1
        if top in b["means"] and top in bc["means"]:
            d = bc["means"][top] - b["means"][top]
            print(f"\n=== CLIP CONTROL (alpha0=1e-1) ===")
            print(f"  BETA_CLIP=-15:-2.3026 (alpha<=0.1)  {b['means'][top]:.3f}")
            print(f"  BETA_CLIP=-15:0       (alpha<=1.0)  {bc['means'][top]:.3f}")
            print(f"  delta {d:+.3f} pp -- "
                  + ("guard is NOT doing the work at the top end; arm B's top-end "
                     "flatness is real." if abs(d) < 1.0 else
                     "the guard IS part of arm B's top-end flatness. State it."))


# --------------------------------------------------------------------------
def selftest():
    """The width rule is the only non-obvious thing here, so it is the thing tested."""
    g = GRID
    ok = 0

    def chk(name, got, want):
        nonlocal ok
        assert abs(got - want) < 1e-9, f"{name}: got {got}, want {want}"
        ok += 1

    # flat everywhere -> full 5-decade span
    m = {a: 92.0 for a in g}
    chk("flat-1pp", width_decades(g, m, 1.0)[0], 5.0)

    # a single peak, everything else far below -> 0 decades, not half a spacing
    m = {a: 10.0 for a in g}
    m[1e-3] = 94.0
    chk("spike", width_decades(g, m, 1.0)[0], 0.0)

    # collapse at the bottom: 1e-6/1e-5 dead, 1e-4..1e-1 within 1pp -> 3 decades
    m = {1e-6: 20.0, 1e-5: 60.0, 1e-4: 93.5, 3e-4: 94.0, 1e-3: 94.2, 1e-2: 93.4, 1e-1: 93.3}
    chk("collapse-lo-1pp", width_decades(g, m, 1.0)[0], 3.0)
    # at 2pp the 1e-5 cell is still 34pp down, so the width does not grow
    chk("collapse-lo-2pp", width_decades(g, m, 2.0)[0], 3.0)

    # non-contiguous in-band set -> flagged, and only the longest run counted
    m = {1e-6: 92.0, 1e-5: 80.0, 1e-4: 92.0, 3e-4: 92.0, 1e-3: 92.0, 1e-2: 80.0, 1e-1: 92.0}
    w, lo, hi, gapped = width_decades(g, m, 1.0)
    assert gapped, "should flag a gapped in-band set"
    chk("gapped-longest-run", w, 1.0)  # 1e-4 .. 1e-3

    # partial grid (mid-batch read) must not crash and must use only present cells
    m = {1e-6: 91.5, 1e-5: 91.8}
    chk("partial", width_decades(g, m, 1.0)[0], 1.0)

    # tolerance boundary is inclusive: exactly 1.00pp down is IN band
    m = {a: 90.0 for a in g}
    m[1e-3] = 91.0
    chk("boundary-inclusive", width_decades(g, m, 1.0)[0], 5.0)

    # mean/sd
    mm, ss = mean_sd([1.0, 2.0, 3.0])
    assert abs(mm - 2.0) < 1e-12 and abs(ss - 1.0) < 1e-12
    ok += 1
    assert math.isnan(mean_sd([5.0])[1])
    ok += 1

    print(f"selftest: {ok}/{ok} PASS")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        report(sys.argv[1] if len(sys.argv) > 1 else "results/all_runs.csv")
