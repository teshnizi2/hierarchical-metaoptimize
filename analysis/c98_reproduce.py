#!/usr/bin/env python3
"""
c98_reproduce.py -- re-derive every headline number in the paper from the CSV of
record and the raw per-epoch logs, and CHECK each one against the value printed
in the paper.  Exit status 0 iff every check passes.

    python3 analysis/c98_reproduce.py              # the full audit
    python3 analysis/c98_reproduce.py --table2     # one section
    python3 analysis/c98_reproduce.py --quiet      # only failures

Each line prints:  derived value | paper value | PASS/FAIL | where it appears.
The tolerance is half a unit in the last printed digit, so a PASS means the paper
and this script agree to the precision the paper actually claims.

House rules this script obeys, and would fail loudly if the CSV stopped obeying:
  * `plateau5` is the only accuracy metric read; the `plateau` column is banned.
  * admissibility = window_ok AND complete AND a readable plateau5.
  * every contrast is within one batch.
  * rows sharing a dup_group are averaged within the group first (ml2 is 3 v 3).
"""
import argparse, math, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c98_figures as F
from c98_figures import (load, cells, arm, welch, meta, chi2_sf, series, pl5,
                         CSV, ROOT, POOL12)

def cells_with_gn(adm):
    """The cell list INCLUDING the GroupNorm cell, whatever the default is."""
    old, F.WITH_GN = F.WITH_GN, True
    try:    return cells(adm)
    finally: F.WITH_GN = old

FAILS = []

def chk(name, got, paper, where, fmt="%+.3f"):
    """Compare a derived value with the value the paper prints."""
    if paper is None:
        print("  %-46s %s   [derived; no paper value yet]  %s"
              % (name, fmt % got, where)); return
    dec = len((fmt % 0).split(".")[-1]) if "." in (fmt % 0) else 0
    tol = 0.5 * 10 ** (-dec) + 1e-12
    ok = abs(got - paper) <= tol
    if not ok: FAILS.append((name, got, paper, where))
    print("  %-46s %s | paper %s | %s   %s"
          % (name, fmt % got, fmt % paper, "PASS" if ok else "**FAIL**", where))

# --------------------------------------------------------------- the sections
def corpus(rows, adm, args):
    print("\n[1] CORPUS  (§8 Reproducibility, Appendix A.8)")
    chk("rows in results/all_runs.csv", len(rows), 2113, "abstract, §8", "%.0f")
    chk("admissible rows", len(adm), 1671, "§3.3, A.8", "%.0f")
    wc = [float(r["wallclock_min"]) for r in rows if r["wallclock_min"]]
    chk("runs carrying a wallclock", len(wc), 2098, "§8", "%.0f")
    chk("GPU-hours", sum(wc) / 60.0, 1582, "abstract, §8", "%.0f")
    chk("distinct nodes", len({r["node"] for r in rows if r["node"]}), 29, "§8", "%.0f")
    for flag, paper in (("window_ok", 425), ("complete", 17)):
        n = sum(1 for r in rows if r[flag] != "1")
        chk("rows failing %s" % flag, n, paper, "§3.3 attrition", "%.0f")
    chk("rows with no plateau5", sum(1 for r in rows if not r["plateau5"]), 25,
        "§3.3 attrition", "%.0f")

TABLE2 = {   # label -> (D, se) exactly as Table 2 prints them
    "cc1": (0.727, 0.200), "mm1": (0.485, 0.161), "pp1": (0.581, 0.141),
    "gn1 (BN)": (0.587, 0.153), "ml2": (0.456, 0.195), "rl3 @1e-4": (0.681, 0.173),
    "rl3 @3e-4": (0.591, 0.096), "fa1": (0.629, 0.123), "hz3": (0.428, 0.086),
    "gn1 (GN)": (0.202, 0.137), "aw1": (0.279, 0.087), "nl1 (SGD)": (1.035, 0.109),
    "nl1 (RMSProp)": (0.973, 0.251), "g3m": (0.666, 0.094), "r50": (0.881, 0.261),
    "gc1": (1.640, 0.245), "gm2": (1.485, 0.238),
}
def table2(rows, adm, args):
    print("\n[2] TABLE 2 -- D = uniform chunk − aligned nodewise, within batch")
    print("    (ml2 is 3 v 3 after the dup_group collapse, se 0.195, NOT 6 v 6 / 0.142)")
    cs = cells(adm)
    if not F.WITH_GN:
        print("    (the GroupNorm cell is removed by R0 item 1; --with-gn puts it back)")
    for c in cs:
        d, se = TABLE2[c["label"]]
        chk("D  %-14s (n %d v %d)" % (c["label"], c["n"][0], c["n"][1]), c["D"], d,
            "Table 2, Fig. 1")
        chk("   se %-11s" % "", c["seD"], se, "", "%.3f")
    pos = sum(1 for c in cs if c["D"] > 0)
    chk("cells with D > 0", pos, len(cs), "abstract, §4.3", "%.0f")

def heterogeneity(rows, adm, args):
    print("\n[3] HETEROGENEITY  (§4.4, Fig. 2)")
    # The GroupNorm cell is removed from the paper by R0 item 1, so the live pool is
    # the ELEVEN byte-identical cells.  The twelve-cell values are checked too, because
    # they are what the current draft prints and Appendix A.4 records.
    # Both pools are computed from the SAME full cell list, so this section reports
    # the same thing whether or not --with-gn is passed.
    full = [c for c in cells_with_gn(adm) if c["in12"]]
    live = [c for c in full if c["base"] != "SGDm-GN"]
    m, sem_, Q, df, tau = meta([(c["D"], c["seD"]) for c in live])
    chk("live pool, %d byte-identical cells" % len(live), m, 0.571, "§4.4 after R0-1")
    chk("   Q", Q, 36.4, "§4.4 after R0-1", "%.1f")
    chk("   df", df, len(live) - 1, "§4.4", "%.0f")
    chk("   tau", tau, 0.203, "§4.4 after R0-1", "%.3f")
    chk("   rms measurement se", math.sqrt(sum(c["seD"]**2 for c in live) / len(live)),
        0.152, "§4.4 after R0-1", "%.3f")
    m2, s2, Q2, df2, t2 = meta([(c["D"], c["seD"]) for c in full])
    chk("legacy 12-cell pool (with GroupNorm)", m2, 0.546, "§4.4 as drafted, A.4")
    chk("   Q", Q2, 43.2, "§4.4 as drafted, abstract", "%.1f")
    chk("   tau", t2, 0.215, "A.4", "%.3f")
    e = live
    bases = ["SGDm", "SGD", "RMSProp", "AdamW"]
    sub = {b: meta([(c["D"], c["seD"]) for c in e if c["base"] == b]) for b in bases}
    within = sum(sub[b][2] for b in bases); wdf = sum(sub[b][3] for b in bases)
    tot = meta([(c["D"], c["seD"]) for c in e])
    chk("within-SGDm Q (k=8)", within, 4.21, "§4.4 rewrite, Fig. 2", "%.2f")
    chk("within-SGDm p", chi2_sf(within, wdf), 0.76, "§4.4 rewrite", "%.2f")
    chk("within-SGDm pool", sub["SGDm"][0], 0.556, "§4.4 rewrite")
    chk("within-SGDm tau", sub["SGDm"][4], 0.000, "§4.4 rewrite", "%.3f")
    chk("between-base Q", tot[2] - within, 32.2, "§4.4 rewrite, Fig. 2b", "%.1f")
    chk("between-base p", chi2_sf(tot[2] - within, tot[3] - wdf), 0.0, "§4.4 rewrite", "%.6f")
    chk("share of the live Q that is between-base",
        100 * (tot[2] - within) / tot[2], 88.4, "§4.4 rewrite, Fig. 2b", "%.1f")
    chk("...of the legacy 12-cell Q", 100 * (tot[2] - within) / Q2, 74.6,
        "the '~75%' figure, denominator named", "%.1f")

def alignment(rows, adm, args):
    print("\n[4] THE ALIGNMENT NULL  (§4.6)")
    perm = [float(r["plateau5"]) for r in adm
            if r["run"].startswith("pp1-perm") and r["granularity"].startswith("permnode")]
    node, _ = arm(adm, "pp1-node", "nodewise")
    ch, _   = arm(adm, "pp1-ch", "chunk777")
    a, ase, at = welch(perm, node)
    chk("A = permnode − nodewise", a, -0.009, "§4.6, abstract, Fig. 4 caption")
    chk("   se", ase, 0.157, "§4.6", "%.3f")
    chk("   95% CI low", a - 1.96 * ase, -0.317, "§4.6 rewrite")
    # NOTE: docs/STATUS.md R0 item 3 prints the upper limit as +0.299.  Re-derived
    # here it is A + 1.96 se = -0.00867 + 1.96 x 0.156569 = +0.29822 -> +0.298.
    chk("   95% CI high", a + 1.96 * ase, 0.298, "§4.6 rewrite (STATUS says .299)")
    b, bse, bt = welch(ch, perm)
    chk("B = chunk777 − permnode", b, 0.590, "§4.6")
    d, dse, dt = welch(ch, node)
    chk("A + B reconstructs D", a + b, d, "§4.6 (identity)")

def prescription(rows, adm, args):
    print("\n[5] THE PRESCRIPTION T = nodewise1d − nodewise  (§4.7)")
    T = [("bn1", "bn1-n1d", "bn1-node", 0.427), ("ml2", "ml2-", "ml2-", 0.619),
         ("fa1", "fa1-n1d", "fa1-node", 0.649), ("g3m", "g3m-n1d", "g3m-node", 0.758),
         ("cc1", "cc1-n1d", "cc1-node", 0.816), ("r50", "r50-n1d", "r50-node", 1.049),
         ("gm2", "gm2-n1d", "gm2-node", 1.363), ("hz3", "hz3-n1d", "hz3-node", 0.337),
         ("nl1 SGD", "nl1-sgd-n1d", "nl1-sgd-node", 0.692),
         ("nl1 RMSProp", "nl1-rms-n1d", "nl1-rms-node", 0.916),
         ("aw1 AdamW", "aw1-n1d", "aw1-node", 0.091)]
    for lab, a_, b_, paper in T:
        av, _ = arm(adm, a_, "nodewise1d"); bv, _ = arm(adm, b_, "nodewise")
        t, se, tt = welch(av, bv)
        chk("T  %-12s" % lab, t, paper, "§4.7 table")

def tail(rows, adm, args):
    print("\n[6] THE TAIL DECOMPOSITION  D = G + (D − G)  (§5.4, Fig. 4)")
    for c in cells(adm):
        if c["G"] is None: continue
        print("  %-16s D %+0.3f ± %0.3f   G %+0.3f ± %0.3f (t %5.2f)   D−G %+0.3f ± %0.3f (t %5.2f)"
              % (c["label"], c["D"], c["seD"], c["G"], c["seG"], c["tG"],
                 c["DG"], c["seDG"], c["tDG"]))
    cs = {c["label"]: c for c in cells(adm)}
    chk("G under AdamW (aw1)", cs["aw1"]["G"], 0.232, "§5.4, A.2")
    chk("   t", cs["aw1"]["tG"], 2.62, "§5.4", "%.2f")
    chk("D − G under AdamW", cs["aw1"]["DG"], 0.047, "§5.4, abstract")
    chk("D − G under SGDm (cc1)", cs["cc1"]["DG"], 0.715, "§5.4, abstract")
    chk("G under ml2 after the collapse", cs["ml2"]["G"], 0.173, "§5.4 (corrected)")
    chk("   t", cs["ml2"]["tG"], 2.38, "§5.4 (corrected 2.44 → 2.38)", "%.2f")
    # The pool is over CIFAR-10 cells ONLY: §4.3's commensurability rule forbids
    # averaging a CIFAR-10 and a CIFAR-100 effect in percentage points.
    sg = [c for c in cells(adm) if c["G"] is not None and c["base"] == "SGDm"
          and c["dataset"] == "C10"]
    p = meta([(c["DG"], c["seDG"]) for c in sg])
    chk("pooled SGDm/C10 D − G (k=8)", p[0], 0.514, "§9 (quote the pool, not cc1's max)")
    chk("   se", p[1], 0.056, "§9", "%.3f")
    p6 = meta([(c["DG"], c["seDG"]) for c in sg if c["network"] == "ResNet-18"])
    chk("   ...ResNet-18 only (k=6)", p6[0], 0.514, "§9 variant")
    bad = meta([(c["DG"], c["seDG"]) for c in cells(adm)
                if c["G"] is not None and c["base"] == "SGDm"])
    print("        (adding the CIFAR-100 cell would give %+0.3f ± %0.3f with Q %.2f/%d "
          "instead of Q %.2f/%d -- which is why §4.3's commensurability rule is a rule)"
          % (bad[0], bad[1], bad[2], bad[3], p[2], p[3]))

def budget(rows, adm, args):
    print("\n[7] BUDGET  (§4.8, Fig. 3)  -- paired WITHIN run, from the raw .out series")
    ch, nd = series("hz3-ch-s*.out"), series("hz3-node-s*.out")
    seeds = sorted(set(ch) & set(nd))
    if not seeds:
        print("  raw hz3 .out not found -- section skipped"); return
    box = {}
    for r in rows:
        for tag in ("ch", "node"):
            if r["run"].startswith("hz3-%s-s" % tag):
                box.setdefault(int(r["run"].rsplit("-s", 1)[1]), {})[tag] = r["beta_clip"]
    bad = sorted(s for s, v in box.items() if len(v) == 2 and v["ch"] != v["node"])
    chk("box-mismatched seeds in hz3", len(bad), 1, "§4.8, T9, Fig. 3", "%.0f")
    print("        (the mismatched seed is seed %s: chunk in %s, nodewise in %s)"
          % (bad, box[bad[0]]["ch"], box[bad[0]]["node"]))
    for keep, tag, paper in ((seeds, "all %d" % len(seeds), (0.576, 0.514, 0.428, -0.149, -1.42)),
                             ([s for s in seeds if s not in bad], "box-matched %d" % (len(seeds) - len(bad)),
                              (0.662, 0.575, 0.455, -0.207, -1.94))):
        for B, exp in zip((100, 200, 300), paper[:3]):
            d = [pl5(ch[s], B) - pl5(nd[s], B) for s in keep]
            chk("D(%d), %s seeds" % (B, tag), st.mean(d), exp, "§4.8 table, Fig. 3a")
        dd = [(pl5(ch[s], 300) - pl5(nd[s], 300)) - (pl5(ch[s], 100) - pl5(nd[s], 100))
              for s in keep]
        m_, se_ = st.mean(dd), st.stdev(dd) / math.sqrt(len(dd))
        chk("D(300)−D(100), %s seeds" % tag, m_, paper[3], "§4.8, Fig. 3b")
        chk("   t", m_ / se_, paper[4], "§4.8, Fig. 3b", "%.2f")

def competitiveness(rows, adm, args):
    print("\n[8] THE SCOPE LIMIT WE MUST NOT SOFTEN  (abstract (ii), §7 T4)")
    import collections
    g = collections.defaultdict(list)
    for r in adm:
        key = r["run"].rsplit("-s", 1)[0] if "-s" in r["run"] else r["run"]
        g[key].append((float(r["plateau5"]), r))
    def best(pred):
        cand = []
        for k, v in g.items():
            if len(v) < 3 or not pred(v[0][1]): continue
            xs = [x[0] for x in v]
            cand.append((st.mean(xs), st.stdev(xs) / math.sqrt(len(xs)), k, len(xs)))
        return max(cand)
    mo18 = best(lambda r: r["granularity"] not in ("?", "") and
                r["network"] == "ResNet18" and r["dataset"] == "CIFAR10")
    mo   = best(lambda r: r["granularity"] not in ("?", ""))
    base = best(lambda r: r["granularity"] in ("?", "") and r["base"] == "SGD"
                and r["network"] == "ResNet18" and r["dataset"] == "CIFAR10")
    chk("best ResNet-18/C10 MetaOptimize arm", mo18[0], 93.317, "§7 T4, abstract", "%.3f")
    print("        that arm is `%s` (n=%d);  the corpus-wide max over ALL networks is "
          "`%s` %.3f on %s -- so 93.317 is the ResNet-18 max, NOT the corpus max"
          % (mo18[2], mo18[3], mo[2], mo[0],
             [v[0][1]["network"] for k, v in g.items() if k == mo[2]][0]))
    chk("tuned SGD+cosine baseline, ResNet-18/C10", base[0], 95.124, "§7 T4, abstract", "%.3f")
    chk("   se", base[1], 0.047, "§7 T4", "%.3f")
    chk("deficit", base[0] - mo18[0], 1.807, "abstract (ii), §7 T4, §9", "%.3f")

SECTIONS = [("corpus", corpus), ("table2", table2), ("heterogeneity", heterogeneity),
            ("alignment", alignment), ("prescription", prescription), ("tail", tail),
            ("budget", budget), ("competitiveness", competitiveness)]

def main():
    ap = argparse.ArgumentParser()
    for name, _ in SECTIONS: ap.add_argument("--" + name, action="store_true")
    ap.add_argument("--csv", default=CSV)
    ap.add_argument("--with-gn", action="store_true",
                    help="re-include the GroupNorm cell that R0 item 1 removes")
    a = ap.parse_args()
    F.WITH_GN = a.with_gn
    want = [n for n, _ in SECTIONS if getattr(a, n)] or [n for n, _ in SECTIONS]
    rows, adm = load(a.csv)
    print("=" * 78)
    print("REPRODUCTION AUDIT -- %s" % os.path.relpath(a.csv, ROOT))
    print("=" * 78)
    for name, fn in SECTIONS:
        if name in want: fn(rows, adm, a)
    print("\n" + "=" * 78)
    if FAILS:
        print("%d CHECK(S) FAILED:" % len(FAILS))
        for n, got, paper, where in FAILS:
            print("   %-46s derived %s vs paper %s   (%s)" % (n, got, paper, where))
    else:
        print("ALL CHECKS PASS.")
    print("=" * 78)
    return 1 if FAILS else 0

if __name__ == "__main__":
    sys.exit(main())
