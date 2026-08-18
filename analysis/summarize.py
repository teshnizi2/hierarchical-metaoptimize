"""Group the aggregated runs into decision tables.

PRIMARY metric is epochs-to-target (the parent paper's evidence is learning curves);
final/best accuracy is reported alongside as secondary. See docs/FINDINGS.md.

Usage:  python summarize.py results/all_runs.csv [--min-epochs 100]
"""
import sys, csv, statistics as st
from collections import defaultdict

path = sys.argv[1]
MIN_EP = 100
if "--min-epochs" in sys.argv:
    MIN_EP = int(sys.argv[sys.argv.index("--min-epochs") + 1])

rows = [r for r in csv.DictReader(open(path)) if int(r["epochs_done"] or 0) >= MIN_EP]


def ms(vals):
    if not vals:
        return "-"
    if len(vals) == 1:
        return f"{vals[0]:.2f}"
    return f"{st.mean(vals):.2f}±{st.stdev(vals):.2f}"


def eps(vals, n):
    """Mean epochs-to-target; 'never (k/n)' when some seeds never reach it."""
    hit = [v for v in vals if v != ""]
    if not hit:
        return "never"
    m = f"{st.mean([int(v) for v in hit]):.1f}"
    return m if len(hit) == n else f"{m} ({len(hit)}/{n})"


def hier_label(r):
    if not r["hier"]:
        return "plain"
    return f"{r['hier']}(lam={r['lam']})" if r["hier"] == "shrink" else f"{r['hier']}(r={r['eta_ratio']})"


groups = defaultdict(list)
for r in rows:
    key = (r["base"], r["meta"], r["alpha0"], "guard" if r["beta_clip"] not in ("none", "?") else "noguard")
    groups[key].append(r)

GRAN_ORDER = {"scalar": 0, "resnet18_blocks": 1, "layerwise": 2, "nodewise": 3, "weightwise": 4}
for key in sorted(groups, key=lambda k: (k[0], k[1], k[2], k[3])):
    base, meta, a0, guard = key
    print(f"\n### base={base}  meta={meta}  alpha0={a0}  {guard}")
    print(f"| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |")
    print("|---|---|---|---|---|---|---|---|")
    sub = defaultdict(list)
    for r in groups[key]:
        sub[(r["granularity"], hier_label(r))].append(r)
    for (g, h), rs in sorted(sub.items(), key=lambda kv: (GRAN_ORDER.get(kv[0][0], 9), kv[0][1])):
        n = len(rs)
        print(f"| {g} | {h} | {n} "
              f"| {eps([r['ep_to_85'] for r in rs], n)} "
              f"| {eps([r['ep_to_88'] for r in rs], n)} "
              f"| {eps([r['ep_to_90'] for r in rs], n)} "
              f"| {ms([float(r['best_test']) for r in rs])} "
              f"| {ms([float(r['final_test']) for r in rs])} |")
print(f"\n({len(rows)} runs with >= {MIN_EP} epochs, of {sum(1 for _ in csv.DictReader(open(path)))} total)")
