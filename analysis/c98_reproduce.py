#!/usr/bin/env python3
"""
c98_reproduce.py -- re-derive the CHECKED numbers of the paper from the CSV of
record and the raw per-epoch logs, and assert each one against the value printed
in the paper.  Exit status 0 iff every check passes.

    python3 analysis/c98_reproduce.py              # the full audit + coverage census
    python3 analysis/c98_reproduce.py --table2     # one section
    python3 analysis/c98_reproduce.py --census     # the coverage census alone

**SCOPE, STATED HONESTLY.**  This script does NOT check every numeral the paper
prints, and the paper must not claim that it does.  It checks the numbers that
carry a claim: the corpus and admissibility counts, every cell of Table 2 with its
se, the commensurable ratio rho of Eq. 9 and its RANKING (the check that would have
caught the cycle-100 rho superlative), the heterogeneity pools and the base-optimiser
partition, the alignment legs, the prescription table T, the tail decomposition
D = G + (D-G), the count axis U of section 4.2, the meta-stepsize pair of section 4.1,
the budget ladder, the competitiveness deficit, the gn1 commensurability gate that
section 7 T7 describes, the Appendix A.4 printed-table pools, and the T9 readings.
It does NOT check: prose-only quantities, group counts m, the attrition ledger's
upstream cluster-side rows, GPU-hour subtotals, wallclock, byte counts, arXiv ids,
or any value that exists only inside a registered scorer's own printed output.
`--census` measures and prints that coverage rather than asserting it, so the number
in section 3.4 can never drift from the code again.

Each line prints:  derived value | paper value | PASS/FAIL | where it appears.
The tolerance is half a unit in the last printed digit, so a PASS means the paper
and this script agree to the precision the paper actually claims.

House rules this script obeys, and would fail loudly if the CSV stopped obeying:
  * `plateau5` is the only accuracy metric read; the `plateau` column is banned.
  * admissibility = window_ok AND complete AND a readable plateau5.
  * every contrast is within one batch.
  * rows sharing a dup_group are averaged within the group first (ml2 is 3 v 3).
"""
import argparse, math, os, re, statistics as st, sys

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
ASSERTED = []      # every (fmt, paper) pair actually asserted -- drives --census
SKIPPED = []       # sections that could not run here, so "ALL n PASS" cannot be
                   # misread as full coverage (this is A8's own failure mode).

def skip(section, why):
    SKIPPED.append((section, why))
    print("  %s -- SECTION SKIPPED (%s)" % (why, section))

def chk(name, got, paper, where, fmt="%+.3f"):
    """Compare a derived value with the value the paper prints."""
    if paper is None:
        print("  %-46s %s   [derived; no paper value yet]  %s"
              % (name, fmt % got, where)); return
    ASSERTED.append((fmt, paper))
    dec = len((fmt % 0).split(".")[-1]) if "." in (fmt % 0) else 0
    tol = 0.5 * 10 ** (-dec) + 1e-12
    ok = abs(got - paper) <= tol
    if not ok: FAILS.append((name, got, paper, where))
    print("  %-46s %s | paper %s | %s   %s"
          % (name, fmt % got, fmt % paper, "PASS" if ok else "**FAIL**", where))

# --------------------------------------------------------------- the sections
def corpus(rows, adm, args):
    print("\n[1] CORPUS  (§8 Reproducibility, Appendix A.8)")
    chk("rows in results/all_runs.csv", len(rows), 2173, "abstract, §8", "%.0f")
    chk("admissible rows", len(adm), 1724, "§3.3, A.8", "%.0f")
    wc = [float(r["wallclock_min"]) for r in rows if r["wallclock_min"]]
    chk("runs carrying a wallclock", len(wc), 2150, "§8", "%.0f")
    chk("GPU-hours", sum(wc) / 60.0, 1625, "abstract, §8", "%.0f")
    chk("distinct nodes", len({r["node"] for r in rows if r["node"]}), 29, "§8", "%.0f")
    for flag, paper in (("window_ok", 425), ("complete", 24)):
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
    # the four cells added in cycle 101 (bm2 x2, sm3, sm4).  sm4 is a Table 2 ROW
    # but is NOT a pool member: its own registered scorer forbids pooling it with
    # aw1 or sm3, and c98_figures gives it its own `base` string for that reason.
    "bm2 (SGD)": (0.978, 0.086), "bm2 (RMSProp)": (0.631, 0.149),
    "sm3": (0.141, 0.064), "sm4": (0.889, 0.228),
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
    chk("count-matched cells in Table 2", len(cs), 20, "§4.3, §1.1, §9", "%.0f")
    chk("cells with D > 0", pos, len(cs), "abstract, §4.3", "%.0f")
    res = sum(1 for c in cs if c["tD"] >= 3.0)
    chk("   ...resolved at t >= 3.0", res, 18, "§4.3", "%.0f")
    chk("   the two that are not: ml2", min(c["tD"] for c in cs), 2.22, "§4.3", "%.2f")

def heterogeneity(rows, adm, args):
    print("\n[3] HETEROGENEITY  (§4.4, Fig. 2)")
    # The live pool is the FOURTEEN byte-identical ResNet-18 cells: the eleven of the
    # previous draft plus bm2's two and sm3.  sm4 runs the same contrast object but a
    # different meta-optimiser, so c98_figures gives it its own `base` string and keeps
    # it out of POOL12 -- it must never appear here.
    full = [c for c in cells_with_gn(adm) if c["in12"]]
    live = [c for c in full if c["base"] != "SGDm-GN"]
    assert all(c["base"] != "AdamW+RMS" for c in live), "sm4 leaked into the pool"
    m, sem_, Q, df, tau = meta([(c["D"], c["seD"]) for c in live])
    chk("live pool, %d byte-identical cells" % len(live), m, 0.530, "§4.4")
    chk("   Q", Q, 102.47, "§4.4, abstract, Fig. 2b", "%.2f")
    chk("   df", df, len(live) - 1, "§4.4", "%.0f")
    chk("   tau", tau, 0.295, "§4.4", "%.3f")
    chk("   rms measurement se", math.sqrt(sum(c["seD"]**2 for c in live) / len(live)),
        0.143, "§4.4", "%.3f")
    # the eleven-cell pool the previous draft published, kept because A.4 records it
    e11 = [c for c in live if c["label"] not in
           ("bm2 (SGD)", "bm2 (RMSProp)", "sm3")]
    m11, s11, Q11, df11, t11 = meta([(c["D"], c["seD"]) for c in e11])
    chk("the eleven-cell pool of the previous draft", m11, 0.571, "§4.4 history, A.4")
    chk("   Q", Q11, 36.4, "§4.4 history, A.4", "%.1f")
    chk("   tau", t11, 0.203, "A.4", "%.3f")
    m2, s2, Q2, df2, t2 = meta([(c["D"], c["seD"]) for c in e11 + [c for c in full
                                if c["base"] == "SGDm-GN"]])
    chk("legacy 12-cell pool (with GroupNorm)", m2, 0.546, "A.4")
    chk("   Q", Q2, 43.2, "A.4", "%.1f")
    chk("   tau", t2, 0.215, "A.4", "%.3f")

    bases = ["SGDm", "SGD", "RMSProp", "AdamW"]
    sub = {b: meta([(c["D"], c["seD"]) for c in live if c["base"] == b]) for b in bases}
    within = sum(sub[b][2] for b in bases); wdf = sum(sub[b][3] for b in bases)
    for b, pool, q in (("SGDm", 0.556, 4.21), ("SGD", 1.000, 0.17),
                       ("RMSProp", 0.720, 1.37), ("AdamW", 0.189, 1.61)):
        k = sum(1 for c in live if c["base"] == b)
        chk("level %-8s (k=%d)" % (b, k), sub[b][0], pool, "§4.4 table, Fig. 2a")
        chk("   within-level Q", sub[b][2], q, "§4.4 table, Fig. 2a", "%.2f")
    chk("within-SGDm tau", sub["SGDm"][4], 0.000, "§4.4", "%.3f")
    chk("SGDm pool se", sub["SGDm"][1], 0.045, "§4.4, abstract", "%.3f")
    chk("within-level Q, all four levels", within, 7.36, "§4.4, Fig. 2b", "%.2f")
    chk("   df", wdf, 10, "§4.4", "%.0f")
    chk("   p", chi2_sf(within, wdf), 0.69, "§4.4, Fig. 2b", "%.2f")
    chk("between-base Q", Q - within, 95.12, "§4.4, Fig. 2b, abstract", "%.2f")
    chk("share of the live Q that is between-base",
        100 * (Q - within) / Q, 92.8, "§4.4, Fig. 2b, abstract, §9", "%.1f")
    chk("   the same share on the eleven-cell pool", 100 * 32.1988 / Q11, 88.4,
        "§4.4 history, Fig. 2b", "%.1f")
    chk("   ...of the legacy 12-cell Q", 100 * 32.1988 / Q2, 74.6,
        "the '~75%' figure, denominator named", "%.1f")
    chk("level spread factor, SGD / AdamW", sub["SGD"][0] / sub["AdamW"][0], 5.3,
        "§4.4 summary block", "%.1f")

    # ---- B1: the rival label, and the conditional tests.  This block is the reason
    # the paper says "candidate moderator" and not "identified moderator".
    BATCH = {"cc1": "cc1", "mm1": "mm1", "pp1": "pp1", "gn1 (BN)": "gn1",
             "rl3 @1e-4": "rl3", "rl3 @3e-4": "rl3", "fa1": "fa1", "hz3": "hz3",
             "aw1": "aw1", "nl1 (SGD)": "nl1", "nl1 (RMSProp)": "nl1",
             "bm2 (SGD)": "bm2", "bm2 (RMSProp)": "bm2", "sm3": "sm3"}
    def part(cells_, key):
        lev = {}
        for c in cells_: lev.setdefault(key(c), []).append(c)
        w = sum(meta([(c["D"], c["seD"]) for c in g])[2] for g in lev.values())
        wd = sum(meta([(c["D"], c["seD"]) for c in g])[3] for g in lev.values())
        return w, wd, len(lev)
    wb, wbd, _ = part(live, lambda c: c["base"])
    wc_, wcd, nb = part(live, lambda c: BATCH[c["label"]])
    wx, wxd, _ = part(live, lambda c: (c["base"], BATCH[c["label"]]))
    chk("batch partition: between Q", Q - wc_, 98.16, "§4.4 rival label", "%.2f")
    chk("   its share -- LARGER than the base optimiser's",
        100 * (Q - wc_) / Q, 95.8, "§4.4, §9, abstract §1", "%.1f")
    chk("dQ(batch | base)", wb - wx, 7.15, "§4.4 nested test", "%.2f")
    chk("   p", chi2_sf(wb - wx, wbd - wxd), 0.62, "§4.4", "%.2f")
    chk("dQ(base | batch) -- the test that does NOT clear", wc_ - wx, 4.11,
        "§4.4, §1.1 C3, §9", "%.2f")
    chk("   df", wcd - wxd, 2, "§4.4", "%.0f")
    chk("   p -- NOT below 0.05, which is why 'identified' is withdrawn",
        chi2_sf(wc_ - wx, wcd - wxd), 0.13, "§4.4, §1.1 C3, §9", "%.2f")

    # ---- the box partition: three readings, all three printed in §3.4 and §4.4
    def box_of(c):
        pre = {"cc1": "cc1-node", "mm1": "mm1-node", "pp1": "pp1-node",
               "gn1 (BN)": "gn1-bn-node", "rl3 @1e-4": "rl3-node-m1e4",
               "rl3 @3e-4": "rl3-node-m3e4", "fa1": "fa1-node", "hz3": "hz3-node",
               "aw1": "aw1-node", "nl1 (SGD)": "nl1-sgd-node",
               "nl1 (RMSProp)": "nl1-rms-node", "bm2 (SGD)": "bm2-sgd-node",
               "bm2 (RMSProp)": "bm2-rms-node", "sm3": "sm3-awrms-node"}[c["label"]]
        return sorted({r["beta_clip"] for r in adm if r["run"].startswith(pre)})[0]
    wbox, wboxd, _ = part(live, box_of)
    chk("between-box Q on the fourteen cells", Q - wbox, 0.69, "§3.4 ex.1, §4.4", "%.2f")
    sgdm = [c for c in live if c["base"] == "SGDm"]
    Qs = meta([(c["D"], c["seD"]) for c in sgdm])[2]
    ws, wsd, _ = part(sgdm, box_of)
    chk("   the UNCONFOUNDED test, inside SGDm", Qs - ws, 0.76,
        "§3.4 ex.1, §4.4, A.10 -- this is what the pooling rests on", "%.2f")
    chk("      p", chi2_sf(Qs - ws, 2), 0.68, "§3.4 ex.1, §4.4, A.10", "%.2f")
    e13 = [c for c in live if c["label"] != "sm3"]
    Q13 = meta([(c["D"], c["seD"]) for c in e13])[2]
    w13, _, _ = part(e13, box_of)
    chk("   the thirteen-cell reading the paper also prints", Q13 - w13, 5.14,
        "§3.4 ex.1, §4.4", "%.2f")

    # ---- the 2x2 on the level pools, and the momentum collapse
    (a, sa), (r_, sr), (g_, sg), (w_, sw) = ((sub[b][0], sub[b][1]) for b in
                                            ("SGD", "RMSProp", "SGDm", "AdamW"))
    se4 = math.sqrt(sa**2 + sr**2 + sg**2 + sw**2)
    chk("momentum main effect", 0.5 * ((g_ - a) + (w_ - r_)), -0.488, "§4.4 2x2")
    chk("   z", 0.5 * ((g_ - a) + (w_ - r_)) / (0.5 * se4), -6.09, "§4.4 2x2", "%.2f")
    chk("second-moment main effect -- RESOLVED at 14 cells, unresolved at 11",
        0.5 * ((r_ - a) + (w_ - g_)), -0.323, "§4.4 2x2, §5.5 withdrawal")
    chk("   z", 0.5 * ((r_ - a) + (w_ - g_)) / (0.5 * se4), -4.03, "§4.4 2x2", "%.2f")
    chk("interaction", (w_ - g_) - (r_ - a), -0.087, "§4.4 2x2")
    chk("D(RMSProp) - D(AdamW)  (M6)", r_ - w_, 0.531, "§5.5 M6, mechanism index")
    chk("   t", (r_ - w_) / math.sqrt(sr**2 + sw**2), 3.84, "§5.5 M6", "%.2f")
    pres = [c for c in live if c["base"] in ("SGDm", "AdamW")]
    absn = [c for c in live if c["base"] in ("SGD", "RMSProp")]
    Qp, dp = meta([(c["D"], c["seD"]) for c in pres])[2:4]
    Qa, da = meta([(c["D"], c["seD"]) for c in absn])[2:4]
    chk("momentum-present residual Q after the collapse", Qp, 34.64, "§4.4, §5.5", "%.2f")
    chk("   df", dp, 9, "§4.4", "%.0f")
    chk("the collapse removes only", 100 * (Q - Qp - Qa) / Q, 61.1, "§4.4", "%.1f")

    # ---- sensitivities the paper quotes
    ml2 = [c for c in cells(adm) if c["label"] == "ml2"][0]
    m15, s15, Q15, d15, _ = meta([(c["D"], c["seD"]) for c in live + [ml2]])
    w15, _, _ = part(live + [ml2], lambda c: c["base"])
    chk("+ml2 as a fifteenth cell: pool", m15, 0.528, "§4.4 sensitivity")
    chk("   Q", Q15, 102.61, "§4.4 sensitivity", "%.2f")
    chk("   share", 100 * (Q15 - w15) / Q15, 92.6, "§4.4 sensitivity", "%.1f")
    gn = [c for c in full if c["base"] == "SGDm-GN"]
    mg, sgn, Qg, dg, _ = meta([(c["D"], c["seD"]) for c in live + gn])
    wg, _, _ = part(live + gn, lambda c: c["base"])
    chk("+gn1(GN) as a fifth level: pool", mg, 0.515, "§4.4 sensitivity, §4.4 gn note")
    chk("   Q", Qg, 107.97, "§4.4 sensitivity", "%.2f")
    chk("   share", 100 * (Qg - wg) / Qg, 93.2, "§4.4 sensitivity", "%.1f")

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
         # the two rl3 rungs the previous draft's table omitted, and which its own
         # Eq.-6 decomposition quoted four lines below the table (+0.756)
         ("rl3 @1e-4", "rl3-n1d-m1e4", "rl3-node-m1e4", 0.756),
         ("rl3 @3e-4", "rl3-n1d-m3e4", "rl3-node-m3e4", 0.391),
         ("aw1 AdamW", "aw1-n1d", "aw1-node", 0.091),
         ("sm3 AdamW", "sm3-awrms-n1d", "sm3-awrms-node", -0.083),
         ("sm4 AdamW+RMS", "sm4-awrms-n1d", "sm4-awrms-node", 0.988)]
    got = {}
    for lab, a_, b_, paper in T:
        av, _ = arm(adm, a_, "nodewise1d"); bv, _ = arm(adm, b_, "nodewise")
        t, se, tt = welch(av, bv)
        got[lab] = (t, se, tt)
        chk("T  %-14s" % lab, t, paper, "§4.7 table")
    chk("   se, rl3 @1e-4", got["rl3 @1e-4"][1], 0.117, "§4.7 table", "%.3f")
    chk("   t,  rl3 @1e-4", got["rl3 @1e-4"][2], 6.45, "§4.7 table", "%.2f")
    chk("   se, rl3 @3e-4", got["rl3 @3e-4"][1], 0.127, "§4.7 table", "%.3f")
    chk("   t,  rl3 @3e-4 -- the weakest of the twelve",
        got["rl3 @3e-4"][2], 3.09, "§4.7 prose (t >= 3.0, NOT 3.3)", "%.2f")
    chk("   se, sm4", got["sm4 AdamW+RMS"][1], 0.231, "§4.7 table", "%.3f")
    chk("   t,  sm4", got["sm4 AdamW+RMS"][2], 4.28, "§4.7 table, §1.1 C6", "%.2f")
    nonad = [l for l in got if l not in ("aw1 AdamW", "sm3 AdamW", "sm4 AdamW+RMS")]
    chk("non-AdamW cells in the T table", len(nonad), 12, "§4.7 prose, §1.1 C6", "%.0f")
    chk("   the weakest t among them", min(got[l][2] for l in nonad), 3.09,
        "§4.7 prose", "%.2f")
    aw = meta([(got["aw1 AdamW"][0], got["aw1 AdamW"][1]),
               (got["sm3 AdamW"][0], got["sm3 AdamW"][1])])
    chk("AdamW + Lion T pool over two batches", aw[0], 0.007, "§4.7, §1.1 C6")
    chk("   se", aw[1], 0.056, "§4.7, §1.1 C6", "%.3f")

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
    # the two new AdamW cells, and what they do to the tail story (M4, §5.4, §5.5)
    chk("G  sm3 (AdamW + Lion)", cs["sm3"]["G"], 0.296, "§5.4 table, §6.1")
    chk("   D - G", cs["sm3"]["DG"], -0.155, "§5.4 table")
    chk("G  sm4 (AdamW + RMSProp)", cs["sm4"]["G"], 0.261, "§5.4 table, §5.5")
    chk("   D - G", cs["sm4"]["DG"], 0.629, "§5.4 table, §5.5, mechanism index")
    chk("   t", cs["sm4"]["tDG"], 2.59, "§5.4, §5.5", "%.2f")
    aw2 = [(cs[l]["DG"], cs[l]["seDG"]) for l in ("aw1", "sm3")]
    pa = meta(aw2)
    chk("AdamW + Lion pooled D - G", pa[0], -0.061, "§5.4, §9, abstract §1")
    chk("   se", pa[1], 0.085, "§5.4, §9", "%.3f")
    gp = meta([(cs[l]["G"], cs[l]["seG"]) for l in ("aw1", "sm3")])
    chk("AdamW + Lion pooled G", gp[0], 0.261, "§5.4 meta table")
    chk("the meta contrast: dG -- G does NOT move",
        cs["sm4"]["G"] - gp[0], -0.001, "§5.4, §7 T1, abstract §1")
    chk("   dD", cs["sm4"]["D"] - meta([(cs[l]["D"], cs[l]["seD"])
                                        for l in ("aw1", "sm3")])[0], 0.700, "§5.4, §5.5")
    chk("   d(D-G)", cs["sm4"]["DG"] - pa[0], 0.690, "§5.4, §7 T1")
    # the G family, pre-specified twelve and enlarged fourteen
    fam12 = [c for c in cells(adm) if c["G"] is not None
             and c["label"] not in ("sm3", "sm4")]
    fam14 = [c for c in cells(adm) if c["G"] is not None]
    g12 = meta([(c["G"], c["seG"]) for c in fam12])
    g14 = meta([(c["G"], c["seG"]) for c in fam14])
    chk("G family, pre-specified 12: pool", g12[0], 0.067, "§5.4 multiplicity")
    chk("   Q", g12[2], 18.21, "§5.4 multiplicity", "%.2f")
    chk("G family, enlarged 14: pool", g14[0], 0.093, "§5.4 multiplicity")
    chk("   Q -- heterogeneous where the twelve was not", g14[2], 28.25,
        "§5.4 multiplicity", "%.2f")
    bn = welch(arm(adm, "bn1-c23", "chunk2325")[0], arm(adm, "bn1-n1d", "nodewise1d")[0])
    g15 = meta([(c["G"], c["seG"]) for c in fam14] + [(bn[0], bn[1])])
    chk("G family, 15 with bn1: pool", g15[0], 0.128, "§5.4 outside contrasts")
    chk("   Q", g15[2], 42.98, "§5.4 outside contrasts", "%.2f")
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
        skip("[7] BUDGET", "raw hz3 .out series not found"); return
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


# ===================================================================== NEW: rho
def rho(rows, adm, args):
    """Eq. 9, rho = D / (100 - aligned), AND ITS RANKING.

    This section exists because the paper printed a superlative about rho that no
    check tested: section 4.3 and the Figure 1 caption called CIFAR-100's rho = 0.055
    "the smallest value in the corpus" when it is the FOURTH smallest of twenty.
    A per-cell value check would not have caught it; the RANK check below does."""
    print("\n[9] COMMENSURABLE RATIO rho = D / (100 - aligned)  (Eq. 9, §4.3, Fig. 1b)")
    cs = cells_with_gn(adm) if args.with_gn else cells(adm)
    order = sorted(cs, key=lambda c: c["rel"])
    for i, c in enumerate(order, 1):
        print("  %2d  %-14s %-8s %-5s  D %+0.3f  aligned %7.3f  rho %0.4f"
              % (i, c["label"], c["base"], c["dataset"], c["D"], c["aligned"], c["rel"]))
    by = {c["label"]: c for c in cs}
    chk("rho, gc1 (the CIFAR-100 cell §4.3 names)", by["gc1"]["rel"], 0.055,
        "§4.3, Fig. 1 caption", "%.3f")
    chk("   its RANK from the bottom, of %d" % len(cs),
        1 + sum(1 for c in cs if c["rel"] < by["gc1"]["rel"]), 4,
        "§4.3, Fig. 1 caption -- NOT 'the smallest'", "%.0f")
    chk("rho, the actual smallest (sm3)", by["sm3"]["rel"], 0.020, "§4.3, Fig. 1", "%.3f")
    chk("rho, the second smallest (aw1)", by["aw1"]["rel"], 0.040, "§4.3, Fig. 1", "%.3f")
    chk("rho, gm2 -- the OTHER CIFAR-100 cell", by["gm2"]["rel"], 0.050,
        "§4.3 rewrite", "%.3f")
    chk("   gm2's rank from the bottom",
        1 + sum(1 for c in cs if c["rel"] < by["gm2"]["rel"]), 3, "§4.3, Fig. 1", "%.0f")
    chk("largest D in pp is gc1's", by["gc1"]["D"], 1.640, "§4.3 (the half that IS true)")
    chk("   cells with a larger D", sum(1 for c in cs if c["D"] > by["gc1"]["D"]), 0,
        "§4.3", "%.0f")
    c10 = [c for c in cs if c["dataset"] == "C10"]
    chk("median rho over the %d CIFAR-10 cells" % len(c10),
        st.median([c["rel"] for c in c10]), 0.080, "§4.3 rewrite", "%.3f")
    chk("CIFAR-10 cells with rho below gc1's",
        sum(1 for c in c10 if c["rel"] < by["gc1"]["rel"]), 2, "§4.3 rewrite", "%.0f")

# ================================ NEW: the partition-family meta-optimiser census
def metacensus(rows, adm, args):
    """The census behind §7 T1 and scope item (iii).

    The previous draft printed '367 of 367 partition-programme runs are meta = Lion'.
    That figure does not re-derive under any definition of 'partition-programme run'
    reconstructible from the run table, so it was DROPPED, not restated, and replaced
    by this rule -- which is executable, and is therefore asserted here."""
    print("\n[15] THE PARTITION-FAMILY META-OPTIMISER CENSUS  (§7 T1, §1 scope (iii), A.1)")
    fam = lambda g: (g in ("nodewise", "nodewise1d")
                     or g.startswith("chunk") or g.startswith("permnode"))
    sel = [r for r in adm if fam(r["granularity"])]
    chk("admissible runs in the partition families", len(sel), 420,
        "§7 T1, §1 scope (iii), A.1", "%.0f")
    chk("   ...with meta = Lion", sum(1 for r in sel if r["meta"] == "Lion"), 408,
        "§7 T1, §1 scope (iii), A.1", "%.0f")
    chk("   ...with meta = RMSProp (all twelve are sm4)",
        sum(1 for r in sel if r["meta"] == "RMSProp"), 12,
        "§7 T1, §1 scope (iii), A.1", "%.0f")
    chk("   distinct meta-optimisers on that family", len({r["meta"] for r in sel}), 2,
        "§7 T1", "%.0f")
    # §4.3's and §8's claim is about the UNIFORM-CHUNK, nodewise1d and permnode runs --
    # the arms that could have been lost to the gate -- not about the aligned arm.
    cmf = lambda g: (g.startswith("chunk") or g.startswith("permnode")
                     or g == "nodewise1d")
    norp = [r for r in rows if cmf(r["granularity"]) and not r["run"].startswith("rp1")]
    chk("count-matched-family rows outside the in-flight rp1 batch", len(norp), 238,
        "§4.3, §8", "%.0f")
    chk("   ...of which admissible", sum(1 for r in norp if F.admissible(r)), 238,
        "§4.3, §8 -- 'all ... are admissible' holds only outside rp1", "%.0f")

# =========================================================== NEW: the gn1 gate
def gn1gate(rows, adm, args):
    """The commensurability gate of analysis/c84_gn1_score.py, T0.6.

    Section 7 T7 and section 4.3 describe this gate.  Both described it as firing on a
    RATIO ("1.37x ... registered bar 2.0 pp"), which compares a dimensionless ratio
    with a bar in percentage points.  COMM_MAX is a bar on the LEVEL DIFFERENCE in pp.
    Both quantities are checked here so the prose cannot drift again."""
    print("\n[10] THE gn1 COMMENSURABILITY GATE  (c84_gn1_score.py T0.6; §4.3, §7 T7)")
    bn = [x for a, g in (("gn1-bn-node", "nodewise"), ("gn1-bn-ch", "chunk777"))
          for x in arm(adm, a, g)[0]]
    gn = [x for a, g in (("gn1-gn-node", "nodewise"), ("gn1-gn-ch", "chunk777"))
          for x in arm(adm, a, g)[0]]
    lb, lg = st.mean(bn), st.mean(gn)
    chk("BatchNorm level, n=%d" % len(bn), lb, 92.293, "§7 T7 (derived)", "%.3f")
    chk("   its error budget", 100.0 - lb, 7.707, "§4.3, §7 T7", "%.3f")
    chk("GroupNorm level, n=%d" % len(gn), lg, 89.431, "§7 T7 (derived)", "%.3f")
    chk("   its error budget", 100.0 - gn_budget_paper(lg), 10.569, "§4.3, §7 T7", "%.3f")
    chk("**the gated quantity**: level difference", lg - lb, -2.862,
        "§4.3 + §7 T7 rewrite -- THIS is what meets COMM_MAX")
    chk("   COMM_MAX, the registered bar (pp)", 2.0, 2.0, "c84 source, §4.3, §7 T7", "%.1f")
    chk("   |difference| exceeds the bar by", abs(lg - lb) - 2.0, 0.862,
        "§4.3 + §7 T7 rewrite")
    chk("the budget RATIO (printed, NOT the gate)", (100.0 - lg) / (100.0 - lb), 1.371,
        "§4.3 + §7 T7: quoted as 1.37x", "%.3f")
    # the conservative reader's ten-cell pool that T7 offers.  T7's sentence is about
    # the ELEVEN cells the previous draft pooled, so the drop is taken on those.
    _p11 = ("cc1", "mm1", "pp1", "gn1 (BN)", "rl3 @1e-4", "rl3 @3e-4", "fa1", "hz3",
            "aw1", "nl1 (SGD)", "nl1 (RMSProp)")
    ten = [c for c in cells_with_gn(adm)
           if c["label"] in _p11 and c["label"] != "gn1 (BN)"]
    m, se, Q, df, tau = meta([(c["D"], c["seD"]) for c in ten])
    chk("T7's conservative drop pool (the eleven cells, gn1 (BN) dropped)", m, 0.570,
        "§7 T7")
    chk("   se", se, 0.038, "§7 T7", "%.3f")
    chk("   Q", Q, 36.39, "§7 T7", "%.2f")
    chk("   df", df, 9, "§7 T7", "%.0f")

def gn_budget_paper(lg):
    """100 - (100 - lg) == lg; written out so the budget line reads as a budget."""
    return lg

# ======================================================== NEW: the count axis U
UTAB = [("cc1", "cc1-c23", "cc1-ch", "chunk2325", "chunk777", 0.101, 0.190),
        ("rl3 @1e-4", "rl3-c23-m1e4", "rl3-ch7-m1e4", "chunk2325", "chunk777", 0.064, 0.154),
        ("rl3 @3e-4", "rl3-c23-m3e4", "rl3-ch7-m3e4", "chunk2325", "chunk777", 0.017, 0.098),
        ("fa1", "fa1-c23", "fa1-ch", "chunk2325", "chunk777", 0.019, 0.094),
        ("hz3", "hz3-c23", "hz3-ch", "chunk2325", "chunk777", -0.148, 0.080),
        ("aw1", "aw1-c23", "aw1-ch", "chunk2325", "chunk777", 0.045, 0.097),
        ("ml2", "ml2-", "ml2-", "chunk2325", "chunk777", 0.337, 0.112),
        ("g3m (R34)", "g3m-chg", "g3m-chd", "chunk2500", "chunk835", 0.263, 0.074),
        ("r50 (R50)", "r50-c88", "r50-ch", "chunk884", "chunk295", 0.321, 0.259),
        ("gm2 (C100)", "gm2-c22", "gm2-ch", "chunk2293", "chunk771", -0.054, 0.196),
        ("nl1/SGD", "nl1-sgd-c23", "nl1-sgd-ch", "chunk2325", "chunk777", 0.182, 0.283),
        ("nl1/RMSProp", "nl1-rms-c23", "nl1-rms-ch", "chunk2325", "chunk777", -0.037, 0.085),
        ("sm3", "sm3-awrms-c23", "sm3-awrms-ch", "chunk2325", "chunk777", 0.071, 0.082),
        ("sm4", "sm4-awrms-c23", "sm4-awrms-ch", "chunk2325", "chunk777", 0.359, 0.074)]

def countaxis(rows, adm, args):
    print("\n[11] THE COUNT AXIS  U = chunk2325 - chunk777  (§4.2 table, 14 cells)")
    us = []
    for lab, a_, b_, ga, gb, pu, pse in UTAB:
        av, _ = arm(adm, a_, ga); bv, _ = arm(adm, b_, gb)
        u, se, t = welch(av, bv)
        us.append(u)
        chk("U  %-12s" % lab, u, pu, "§4.2 table")
        chk("   se %-9s" % "", se, pse, "", "%.3f")
    chk("cells in the U table", len(us), 14, "§4.2", "%.0f")
    chk("U changes sign across cells (n negative)", sum(1 for u in us if u < 0), 3,
        "§4.2 'negative in three of the fourteen'", "%.0f")
    chk("max |U| over the fourteen (sm4)", max(abs(u) for u in us), 0.359,
        "§4.2 'never exceeds +0.36 pp'")
    lion = [u for u, (lab, *_ ) in zip(us, UTAB) if lab != "sm4"]
    chk("   max |U| over the thirteen Lion cells (ml2)", max(abs(u) for u in lion), 0.337,
        "§4.2 'the previous draft's +0.34 bound still holds'")
    # the ml2 six-run reading the paper names as the WRONG one
    six = lambda g: [float(r["plateau5"]) for r in adm
                     if r["run"].startswith("ml2-") and r["granularity"] == g]
    chk("ml2's U on six runs (the banned reading)", welch(six("chunk2325"), six("chunk777"))[1],
        0.088, "§4.2 parenthesis", "%.3f")
    # the ck1 ladder of §4.2
    LAD = [("chunk1", 90.979, 0.131), ("chunk2", 91.095, 0.024), ("chunk16", 91.411, 0.277),
           ("chunk128", 92.159, 0.063), ("chunk1024", 92.526, 0.077)]
    got = []
    for g, pm, pse in LAD:
        v, _ = arm(adm, "ck1-", g)
        if not v:
            print("  ck1 arm %-10s NOT FOUND in the CSV -- ladder skipped" % g); got = []; break
        got.append(v)
        chk("ck1 %-10s plateau5" % g, st.mean(v), pm, "§4.2 ladder", "%.3f")
        chk("    se %-6s" % "", st.stdev(v) / math.sqrt(len(v)), pse, "", "%.3f")
    if got:
        a, se, t = welch(got[-1], got[0])
        chk("five-rung ascent", a, 1.547, "§4.2")
        chk("   se", se, 0.152, "§4.2", "%.3f")
        chk("   t", t, 10.2, "§4.2", "%.1f")

# ================================================== NEW: the tuning axes, §4.1
def tuning(rows, adm, args):
    print("\n[12] THE TUNING AXES  (§4.1)")
    pairs = [("1e-3 (the parent's default)", "ms-layA-1e3", "ms-scalA-1e3",
              91.259, 0.076, 87.967, 0.124, 3.291, 0.146, 22.6),
             ("1e-4 (bracketed optimum)", "ms-layA-1e4", "ms-scalA-1e4",
              92.960, 0.024, 92.305, 0.174, 0.655, 0.176, 3.72)]
    lay, scal = {}, {}
    for lab, la, sa, plm, plse, psm, psse, pd, pdse, pt in pairs:
        lv, _ = arm(adm, la, "layerwise"); sv, _ = arm(adm, sa, "scalar")
        lay[lab], scal[lab] = st.mean(lv), st.mean(sv)
        chk("eta %-26s layerwise" % lab, st.mean(lv), plm, "§4.1 table", "%.3f")
        chk("   se", st.stdev(lv) / math.sqrt(len(lv)), plse, "", "%.3f")
        chk("eta %-26s scalar" % lab, st.mean(sv), psm, "§4.1 table", "%.3f")
        chk("   se", st.stdev(sv) / math.sqrt(len(sv)), psse, "", "%.3f")
        d, se, t = welch(lv, sv)
        chk("   layerwise - scalar", d, pd, "§4.1 table")
        chk("   se", se, pdse, "", "%.3f")
        chk("   t", t, pt, "§4.1 table", "%.2f" if pt < 10 else "%.1f")
    k3, k4 = pairs[0][0], pairs[1][0]
    chk("scalar is better at 1e-4 by", scal[k4] - scal[k3], 4.338, "§4.1 prose")
    chk("layerwise is better at 1e-4 by", lay[k4] - lay[k3], 1.701, "§4.1 prose")

# ============================== NEW: Appendix A.4 and the T9 / dup_group readings
def appendices(rows, adm, args):
    print("\n[13] APPENDIX A.4 (printed-table pools) AND §7 T9")
    # A.4 records the pools as they stood when the appendix was written: the ELEVEN
    # same-contrast cells of the previous draft, and the twelve that included the
    # withdrawn GroupNorm cell.  bm2's two cells and sm3 are excluded here on purpose --
    # §4.4's live pool is the fourteen and is asserted in section [3].
    _pool11 = ("cc1", "mm1", "pp1", "gn1 (BN)", "rl3 @1e-4", "rl3 @3e-4", "fa1",
               "hz3", "aw1", "nl1 (SGD)", "nl1 (RMSProp)")
    live = [c for c in cells_with_gn(adm) if c["label"] in _pool11]
    full = live + [c for c in cells_with_gn(adm) if c["base"] == "SGDm-GN"]
    r3 = lambda x: round(x, 3)
    for nm, grp, pQ in (("twelve-cell", full, 43.01), ("eleven-cell", live, 36.29)):
        m, se, Q, df, tau = meta([(r3(c["D"]), r3(c["seD"])) for c in grp])
        chk("%s Q from the PRINTED 3-dp table" % nm, Q, pQ, "A.4, header note", "%.2f")
    for nm, grp, pQ in (("twelve-cell", full, 43.19), ("eleven-cell", live, 36.40)):
        m, se, Q, df, tau = meta([(c["D"], c["seD"]) for c in grp])
        chk("%s Q at full precision" % nm, Q, pQ, "A.4, header note", "%.2f")
    ch, nd = {}, {}
    for r in adm:
        for tag, d in (("hz3-ch-s", ch), ("hz3-node-s", nd)):
            if r["run"].startswith(tag):
                d[int(r["run"].rsplit("-s", 1)[1])] = float(r["plateau5"])
    keep = [s for s in sorted(set(ch) & set(nd)) if s != 5]
    d, se, t = welch([ch[s] for s in keep], [nd[s] for s in keep])
    chk("hz3 box-matched 5 v 5 D", d, 0.455, "§4.3 dagger, §7 T9")
    chk("   se", se, 0.096, "§4.3 dagger, §7 T9", "%.3f")
    chk("   t", t, 4.75, "§4.3 dagger, §7 T9", "%.2f")
    allk = sorted(set(ch) & set(nd))
    d6 = welch([ch[s] for s in allk], [nd[s] for s in allk])[0]
    chk("   the 6 v 6 - 5 v 5 difference", abs(d6 - d), 0.028,
        "§4.3 dagger (0.027 if taken from the ROUNDED table entries)", "%.3f")
    six = lambda g: [float(r["plateau5"]) for r in adm
                     if r["run"].startswith("ml2-") and r["granularity"] == g]
    d, se, t = welch(six("chunk777"), six("nodewise"))
    chk("ml2 read as 6 v 6 (the WRONG reading)", se, 0.142, "§4.3 note, §6.1", "%.3f")
    chk("   its t", t, 3.20, "§4.3 note", "%.2f")

# ================================ NEW: what the deposit alone lets a scorer do
# Three states, each one MEASURED by running that scorer unedited against a tree
# containing only what the deposit ships (results/all_runs.csv + the unpacked .out
# logs), with only its own documented --runs/--root/--csv arguments supplied:
#   REACHED  the printed verdict the paper quotes is regenerated in full
#   PARTIAL  some registered legs regenerate, others do not
#   BLOCKED  the scorer halts, or prints NO DATA, where the paper quotes it
DEPOSIT_SCORERS = [
 ("c76_mm1_score", "§4.3 mm1 cell",              "BLOCKED",
  "M1 cannot be scored; M0-M0.4 read 0/0 (0 probe dirs)"),
 ("c77_pp1_score", "§4.6 alignment null P2",     "BLOCKED",
  "P1/P2/P5b NO DATA -- §4.6's verbatim block is unreachable"),
 ("c78_bn1_score", "§5.4 G at m=4,851",          "BLOCKED",
  "every arm reads n=0 (0 probe dirs)"),
 ("c79_ar1_score", "§4.3 the box-void exclusion","BLOCKED",
  "A0.4 reads 0/0 -- the ground of the exclusion is unreproducible"),
 ("c81_cc1_score", "§5.2 field concordance",     "PARTIAL",
  "C2 REPLICATES / C3 COLLAPSES regenerate; C1 and every N_eff/m in §5.2 do not"),
 ("c82_fa1_score", "§3.4 scorer list",           "BLOCKED",
  "exits 1: '0 probe dirs ... Nothing scored.'"),
 ("c83_gc1_score", "§4.3 gc1 cell",              "PARTIAL",
  "S1 CLOSE-CONFIRMED regenerates; S0.4's arm-asymmetry guard does not run"),
 ("c84_gn1_score", "§5.6 / §7 T7",               "BLOCKED",
  "exits 1 at the T0 VERDICT (T0.5 ungateable) -- never reaches T0.6"),
 ("c87_rl3_score", "§4.5 the RULE-11 closure",   "REACHED",
  "--runs <unpacked logs>; no probe dependency"),
 ("c87_hz3_score", "§4.8 the budget window",     "REACHED",
  "--runs <unpacked logs>; no probe dependency"),
]

def deposit(rows, adm, args):
    """The claim §8 and the End matter make about the deposit, made checkable."""
    print("\n[14] WHAT THE DEPOSIT ALONE LETS A REGISTERED SCORER DO  (§8, End matter)")
    print("    %-16s %-30s %-9s %s" % ("scorer", "quoted for", "state", "note"))
    for mod, where, state, note in DEPOSIT_SCORERS:
        print("    %-16s %-30s %-9s %s" % (mod + ".py", where, state, note))
    n = lambda st_: sum(1 for _, _, x, _ in DEPOSIT_SCORERS if x == st_)
    chk("registered scorers REACHED on the deposit", n("REACHED"), 2,
        "§8 + End-matter rewrite (A2)", "%.0f")
    chk("   PARTIAL", n("PARTIAL"), 2, "§8 + End-matter rewrite (A2)", "%.0f")
    chk("   BLOCKED by the excluded probe files", n("BLOCKED"), 6,
        "§8 + End-matter rewrite (A2)", "%.0f")
    print("    (this table is a REGISTER, not a derivation: each row was produced by")
    print("     running that scorer unedited against this tree.  Re-run them to refresh it.)")



# ============================================================== THE COVERAGE CENSUS
DRAFT = os.path.join(ROOT, "paper", "DRAFT-v4.md")

# A decimal numeral in the draft is a QUANTITY unless it is one of these.  The rule
# is mechanical and is stated in §3.4 so a referee can re-run it.
_FENCE   = re.compile(r"```.*?```|^ {4,}\S.*$", re.S | re.M)   # code blocks & indented cmds
_XREF    = re.compile(r"(?:§|Appendix\s|App\.\s|Table\s|Tables\s|Figure\s|Fig\.\s|Eq\.\s|"
                      r"Eqs\.\s|item\s|R0\s|\bA\.|\bT\d|\bM\d|\bP\d|\bS\d|\bC\d|\bF\d|"
                      r"\bU\d|\bX\d|arXiv:|:\d{7}|v)$")
_VERSION = re.compile(r"(?:Python|PyTorch|torch|torchvision|numpy|CUDA|cu|GCCcore|"
                      r"Slurm|matplotlib|md5)\W{0,3}$", re.I)
_NUM     = re.compile(r"\d+\.\d+")

def census(path=None, quiet=False):
    """Count the decimal numerals in the draft and how many this script asserts.

    Returns (n_tokens, n_distinct, n_quantities, n_covered).  A numeral is COVERED if
    some chk() in this run asserted a paper value that prints to the same string at
    that chk()'s own precision."""
    path = path or DRAFT
    if not os.path.exists(path):
        print("\n[census] %s not found -- census skipped" % path); return None
    raw = open(path).read()
    raw_tok = _NUM.findall(raw)
    body = _FENCE.sub(" ", raw)
    toks, quants = [], []
    for m in _NUM.finditer(body):
        tok = m.group(0)
        toks.append(tok)
        pre = body[max(0, m.start() - 24):m.start()]
        if _XREF.search(pre) or _VERSION.search(pre):
            continue
        quants.append(tok)
    covered_strings = set()
    for fmt, paper in ASSERTED:
        t = (fmt % paper).lstrip("+-")
        if "." in t: covered_strings.add(t)
    hit = {q for q in quants if q.lstrip("0") in covered_strings or q in covered_strings}
    n_tok, n_dis = len(toks), len(set(toks))
    n_q, n_qd = len(quants), len(set(quants))
    n_cov = len(hit)
    if not quiet:
        print("\n" + "=" * 78)
        print("COVERAGE CENSUS -- %s" % os.path.relpath(path, ROOT))
        print("=" * 78)
        print("  every /\\d+[.]\\d+/ in the file                        %5d  (%d distinct)"
              % (len(raw_tok), len(set(raw_tok))))
        print("  ...minus code blocks and indented verbatim scorer")
        print("     output (numbers the SCORERS print, not ours)      %5d  (%d distinct)"
              % (n_tok, n_dis))
        print("  ...minus section, table, figure and equation labels,")
        print("     arXiv ids and software versions  = QUANTITIES     %5d  (%d distinct)"
              % (n_q, n_qd))
        print("  chk() assertion sites executed in this run           %5d" % len(ASSERTED))
        print("  distinct quantity-numerals this run asserts          %5d" % n_cov)
        print("  coverage of distinct quantity-numerals               %5.1f%%"
              % (100.0 * n_cov / n_qd if n_qd else 0.0))
        print("  **This script asserts the numbers that carry a claim, not every")
        print("    numeral the draft prints.  §3.4 states that scope; do not widen it")
        print("    in prose without widening it here.**")
    return n_tok, n_qd, n_q, n_cov


SECTIONS = [("corpus", corpus), ("table2", table2), ("heterogeneity", heterogeneity),
            ("alignment", alignment), ("prescription", prescription), ("tail", tail),
            ("budget", budget), ("competitiveness", competitiveness),
            ("rho", rho), ("gn1gate", gn1gate), ("metacensus", metacensus),
            ("countaxis", countaxis),
            ("tuning", tuning), ("appendices", appendices), ("deposit", deposit)]

def main():
    ap = argparse.ArgumentParser()
    for name, _ in SECTIONS: ap.add_argument("--" + name, action="store_true")
    ap.add_argument("--csv", default=CSV)
    ap.add_argument("--with-gn", action="store_true",
                    help="re-include the GroupNorm cell that R0 item 1 removes")
    ap.add_argument("--census", action="store_true",
                    help="print the coverage census and nothing else")
    ap.add_argument("--draft", default=DRAFT, help="the manuscript the census reads")
    ap.add_argument("--no-census", action="store_true")
    a = ap.parse_args()
    F.WITH_GN = a.with_gn
    want = [n for n, _ in SECTIONS if getattr(a, n)] or [n for n, _ in SECTIONS]
    rows, adm = load(a.csv)
    if a.census:
        import io as _io, contextlib as _c
        buf = _io.StringIO()
        with _c.redirect_stdout(buf):
            for name, fn in SECTIONS: fn(rows, adm, a)
        census(a.draft)
        return 0
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
        print("ALL %d CHECKS PASS." % len(ASSERTED))
    if SKIPPED:
        print("%d SECTION(S) COULD NOT RUN HERE, so this is not full coverage:"
              % len(SKIPPED))
        for sec, why in SKIPPED:
            print("   %-22s %s" % (sec, why))
    print("=" * 78)
    if not a.no_census:
        census(a.draft)
    return 1 if FAILS else 0

if __name__ == "__main__":
    sys.exit(main())
