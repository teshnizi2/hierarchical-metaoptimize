#!/usr/bin/env python3
r"""THE MEASURED NOISE SCALE OF N_eff/m, PER SEED, ACROSS EVERY PROBE ROOT WE OWN.

WHY THIS EXISTS.  CORRECTIONS 78 added **STANDING RULE (9)**:

    a registered tolerance must be stated against the measured noise of the statistic
    at the budget and unit it is applied to.  A bar imported from another rung, another
    budget, or another source of variation is not a bar.  Report the sd alongside the
    verdict.

The rule was added on the strength of exactly SIX measured cells (FINDINGS 54.2: three
rungs x two budgets, from `br6`) plus one more from `ns6` (54.4).  Every OTHER gate this
campaign has scored -- and every gate the next several ticks will score -- still cites a
bar with no measured sd behind it.  This module supplies the missing table.

WHAT IT IS, AND WHAT IT IS NOT.
  * It IS a DESCRIPTIVE sweep.  No prediction is registered here, because nothing is
    being tested: the output is a noise table that other scorers cite.  Registering a
    prediction for a descriptive sweep would be theatre.
  * It is NOT a re-derivation of any published number.  The seed-MEAN N_eff/m values it
    prints must agree with `neff_instrument.py`'s, and a mismatch is a BUG here, not a
    correction there.  `--crosscheck` asserts exactly that against the shared instrument.

THE STATISTIC.  Per probe dir (i.e. PER SEED):

    N_eff/m = 1 / (1 + (m-1) * rho_s)          VARIANCE instrument, heterogeneity-
                                               corrected, STEADY half (0.5-1.0)

taken from `probe5_window.reduce_dir`, the same selftested reducer every published
N_eff/m in this campaign came through.  It is NOT recomputed here.

THE RESOLUTION ARITHMETIC, stated once so it is not re-derived per tick.  For two cells
of equal size n drawn from the same per-seed sd, the smallest difference separable at
2 standard errors is

    MRD(n) = 2 * sqrt(2) * sd / sqrt(n)

This is the formula CORRECTIONS 80 used to price N1's extra seeds (sd 0.0131, gap 0.0142
-> n=7), reproduced here as a tested function so the next tick prices batches without
re-deriving it.  `--price GAP SD` inverts it: the n needed to resolve GAP.

BOX PROVENANCE.  A per-seed sd computed over arms that were CLIPPED is a sd of the box,
not of the estimator.  Every root's `BETA_CLIP` is registered in `BOXES` below with the
`bin/` script it was read out of, and the box-free flag is computed per seed from
`c52_boxfree.occupancy`.  A root with no registered box is REFUSED, never guessed --
`box_for` raises.  Cells are reported with their box-free seed count so a sd measured
over a mixed cell can never be quoted as a clean one.

KNOWN LIMITS, stated up front.
  * n is 2-4 almost everywhere.  A sd at n=2 has ~50% relative uncertainty; it is
    printed with its n and must be quoted with it.  This table narrows the bar, it does
    not make it exact.
  * The seeds within a cell share a box, a budget and an ms.  This measures SEED noise
    only.  It says nothing about run-to-run reproducibility across accounts or nodes.
  * `blk6` rungs are included where present; the campaign's headline rungs are w/node/lay.

USAGE
  python3 analysis/c55_neff_noise.py --selftest
  python3 analysis/c55_neff_noise.py ../probes_br6 ../probes_cl5 ...
  python3 analysis/c55_neff_noise.py --all            # every root under ..
  python3 analysis/c55_neff_noise.py --price 0.0142 0.0131
  python3 analysis/c55_neff_noise.py --crosscheck ../probes_bo6
"""
import glob
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe5_window import reduce_dir  # noqa: E402
import c52_boxfree  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                 # the repo
# The probe mirrors live BESIDE the repo (../probes_*), not inside it -- the same layout
# every scorer in this campaign is invoked with.  Getting this wrong made `--all` and the
# registry selftest both pass VACUOUSLY on an empty glob, which is the silent-zero failure
# c52_boxfree.records() was hardened against.
PROBE_HOME = os.path.dirname(ROOT)

STEADY = ("steady .5-1", (0.5, 1.0))
RECORDS_PER_EPOCH = 500 // c52_boxfree.STEPS_PER_RECORD   # 500 steps/epoch / 5 = 100
BOXFREE_MAX = 0.05        # the campaign's < 5% of records at either guard
# Symlink views onto another root.  `sweep` de-duplicates WITHIN a root by realpath, but
# --all would still visit these as separate roots and double-count every ml5 cell in the
# roll-ups.  Excluded there; still usable if named explicitly on the command line.
ALIAS_ROOTS = {"ml5_m2", "ml5_m3", "ml5_m4"}

# --------------------------------------------------------------------- box registry
# (lo, hi, source) read out of the submitting script.  NEVER guessed: `box_for` raises
# on an unregistered root, because a wrong box turns a clipped arm into a "clean" sd.
BOXES = {
    "p5":   (-15.0, -2.3026, "bin/c44_probe5_heterogeneity.sh:151"),
    "fr5":  (-15.0, -2.3026, "bin/c48_free_profile_p5.sh:122"),
    "fz3":  (-15.0, -2.3026, "bin/c48_frozen_ladder_p5.sh:139"),
    "ml5":  (-15.0, -2.3026, "bin/c49_ms_ladder_p5.sh:125"),
    # probes_ml5_m{2,3,4} are SYMLINK VIEWS onto probes_ml5, one ms rung each; the same
    # box, and `sweep` de-duplicates them by realpath so they cannot be double-counted.
    "ml5_m2": (-15.0, -2.3026, "alias of ml5 (symlinks)"),
    "ml5_m3": (-15.0, -2.3026, "alias of ml5 (symlinks)"),
    "ml5_m4": (-15.0, -2.3026, "alias of ml5 (symlinks)"),
    "ff5":  (-15.0, -2.3026, "bin/c49_free_family_ladder.sh:176"),
    "wc5":  (-30.0, -2.3026, "bin/c50_wideclip_ladder.sh:121"),
    "uc5":  (-30.0,  0.0,    "bin/c51_unclipped_family.sh:149"),
    "uc6":  (-30.0,  0.0,    "bin/c52_c100_boxfree.sh:147"),
    "bl5":  (-30.0,  0.0,    "bin/c52_budget_ladder.sh:199"),
    "ns5":  (-30.0,  0.0,    "bin/c52_nodemin_onset.sh:162"),
    "ns6":  (-30.0,  0.0,    "bin/c53_ns_thirdseed.sh:113"),
    "bo6":  (-30.0,  0.0,    "bin/c53_base_optimizer.sh:160"),
    "br6":  (-30.0,  2.0,    "bin/c53_budget_replication.sh:177"),
    # cl5 is a CEILING ladder -- the box is per ARM, not per root.
    "cl5:cD": (-30.0, -4.6052, "bin/c51_ceiling_ladder.sh:209"),
    "cl5:cU": (-30.0,  0.0,    "bin/c51_ceiling_ladder.sh:209"),
    # cycle-54 batches, boxes registered from their scripts ahead of the data landing.
    "bd7:c2": (-30.0, 2.0, "bin/c54_budget_curve.sh:313"),
    "bd7:c6": (-30.0, 6.0, "bin/c54_budget_curve.sh:313"),
    "bo7:c2": (-30.0, 2.0, "bin/c54_adamw_ceiling.sh:279"),
    "bo7:c6": (-30.0, 6.0, "bin/c54_adamw_ceiling.sh:279"),
    # cycle-55 span/budget dissociation, submitted and landed in cycle 71.  Single box,
    # read from the script's own BOX= line, not from the data.
    "sp8":  (-30.0,  2.0,    "bin/c55_span_dissociation.sh:189"),
    # cycle-71 FLOOR ladder (the bd7 re-run).  HI is fixed at +2.0 and the FLOOR is
    # the varied axis, so the box is per ARM exactly as for cl5/bd7.  Read from the
    # script's own emitter line, not from the data.
    "bf8:f60": (-60.0, 2.0, "bin/c71_floor_budget.sh:295"),
    "bf8:f90": (-90.0, 2.0, "bin/c71_floor_budget.sh:295"),
    # cycle-73 re-run of bf8 WITH THE INSTRUMENT ON (bf8 never exported PROBE5=1, so
    # it wrote no neg_counts and reduce_root skipped every one of its arms).  ONE floor:
    # bf8 measured the deepest beta_true_min in the whole batch at -46.744, and f60/f90
    # returned the identical guard verdict on 6/6 (rung, seed) pairs, so the second floor
    # is not a dose.  REGISTERED BEFORE ANY bf9 JOB COMPLETED -- read from the script's
    # own LO=/HI= lines, not from the data (CORRECTIONS 102.4).
    "bf9:f60": (-60.0, 2.0, "bin/c73_bf9_probe5.sh:112"),
    # cycle-74 TUNED weightwise operating point, with the instrument on.  This is
    # NOT a new box: it is `wm9`'s box, which is in turn the rs-/ms- reference
    # signature (-15, -2.3026) that p5/fr5/fz3/ml5/ff5 all sit in.  Registered
    # BEFORE ANY tw0 JOB WAS SUBMITTED, read from the script's own CLIP= line.
    "tw0":  (-15.0, -2.3026, "bin/c74_tuned_weightwise_probe.sh:CLIP"),
    # cycle-75 ALL-RUNGS-TUNED agreement ladder: the two rungs tw0 left without a
    # probe at their OWN argmax -- blk6 @ 1e-4 and nodewise @ 3e-4.  Same box as
    # tw0/wm9/ml5, so again NOT a new box.  REGISTERED BEFORE ANY at1 JOB WAS
    # SUBMITTED, read from the script's own CLIP= line, not from the data.
    "at1":  (-15.0, -2.3026, "bin/c75_tuned_agreement_ladder.sh:CLIP"),
    # cycle-75 CHUNK LADDER (PATCH_CHUNKWISE), filling the three-decade hole between
    # nodewise and weightwise.  Same box again -- tw0's, which is wm9's/ml5's.  Its
    # endpoints chunk1 and chunk<huge> are BITWISE weightwise and layerwise, both of
    # which tw0 measured box-free at 0.0000 on all four columns in this box.
    # REGISTERED BEFORE ANY ck1 JOB WAS SUBMITTED, from the script's own CLIP= line.
    "ck1":  (-15.0, -2.3026, "bin/c75_chunk_ladder.sh:CLIP"),
    # `mm1` and `cx2` reuse ck1's box UNCHANGED -- neither is a new box.  All 15 ck1
    # arms and all 3 tw0 nodewise arms were box-free at 0.0000 on all four columns in
    # it, spanning m from 62 to 11,173,962, so both new families sit strictly inside
    # a range already measured slack at both guards.
    # REGISTERED BEFORE ANY mm1/cx2 JOB WAS SUBMITTED, from each script's own CLIP=.
    "mm1":  (-15.0, -2.3026, "bin/c76_matched_m_partition.sh:CLIP"),
    "cx2":  (-15.0, -2.3026, "bin/c76_chunk_coarse_extension.sh:CLIP"),
    # cycle-77 PERMUTED PARTITION (PATCH_PERMNODE), the three-way decomposition of
    # mm1's +0.485 pp into an ALIGNMENT leg and a SIZE-DISTRIBUTION leg.  Same box
    # AGAIN -- ck1's, which is tw0's/wm9's/ml5's.  Not a new box.  Its `node` and
    # `ch` arms are bitwise mm1's two arms, both of which read 0.0000 on all four
    # occupancy columns in this box; the `perm` arm carries nodewise's EXACT
    # group-size multiset, so it sits at the same m in the same range.
    # REGISTERED BEFORE ANY pp1 JOB WAS SUBMITTED, from the script's own CLIP= line.
    "pp1":  (-15.0, -2.3026, "bin/c77_permuted_partition.sh:CLIP"),
    # cycle-78 DEGENERATE-TAIL batch (`bn1`), the matched-count contrast run again with
    # nodewise's 9,610 size-1 groups removed from the architecture-aligned side.  Same
    # box AGAIN -- pp1's, which is mm1's, which is ck1's.  Not a new box.  Its `node`
    # arm is bitwise pp1's and mm1's nodewise arm, which read 0.0000 on all four
    # occupancy columns in this box across 6 runs; `n1d` and `c23` sit at m = 4,851,
    # between ck1's chunk1024 (m=10,944) and cx2's chunk8192 (m=1,407), both of which
    # were also box-free here, so the arms are interior to a measured free range.
    # REGISTERED BEFORE ANY bn1 JOB WAS SUBMITTED, from the script's own CLIP= line.
    "bn1":  (-15.0, -2.3026, "bin/c78_degenerate_tail.sh:CLIP"),
    # `ar1` (cycle 79) -- the SAME box as bn1/pp1/mm1/ck1, so A5's cross-batch meter
    # is comparable.  UNLIKE every probed batch before it, ar1 runs at ms=3e-4, a 3x
    # larger meta stepsize, so beta travels further and a bind at this box is a REAL
    # possibility rather than a formality.  That is registered in the batch script:
    # a bind VOIDS A3 (the field gate) and leaves A1/A2 (accuracy-only) standing.
    # REGISTERED BEFORE ANY ar1 JOB WAS SUBMITTED, from the script's own CLIP= line.
    "ar1":  (-15.0, -2.3026, "bin/c79_argmax_robustness.sh:CLIP"),
}


def root_tag(root):
    """'../probes_br6/' -> 'br6'."""
    base = os.path.basename(os.path.normpath(root))
    return base[len("probes_"):] if base.startswith("probes_") else base


def box_for(tag, fam):
    """(root tag, arm/family tag) -> (lo, hi).  RAISES on an unregistered root.

    A guessed box is worse than no box: it converts a clipped arm into an apparently
    clean sd, which is exactly the failure CORRECTIONS 62/68 spent two cycles undoing.
    """
    for key in (f"{tag}:{fam}", tag):
        if key in BOXES:
            lo, hi, _ = BOXES[key]
            return lo, hi
    raise KeyError(f"no registered BETA_CLIP for root '{tag}' arm '{fam}' -- "
                   f"add it to BOXES with the bin/ line it came from, do not guess")


# ------------------------------------------------------------------------- statistics
def neff_over_m(m, rho_s):
    """1 / (1 + (m-1) rho_s) -- N_eff/m under the exchangeable model.

    Algebraically identical to neff_instrument.neff_from_rho(m, rho)/m; written in the
    ratio form so the 62-vs-11,173,962 dynamic range never passes through a division of
    two large floats.
    """
    if not np.isfinite(rho_s) or m < 1:
        return float("nan")
    den = 1.0 + (m - 1.0) * rho_s
    return 1.0 / den if den > 0 else float("nan")


def mrd(sd, n):
    """Minimum resolvable DIFFERENCE between two equal-n cells at 2 SE.

    MRD = 2 * sqrt(2) * sd / sqrt(n).  The sqrt(2) is the SE of a difference of two
    independent means; the leading 2 is the campaign's 2-SE convention (CORRECTIONS 80).
    """
    if not np.isfinite(sd) or n < 2:
        return float("nan")
    return 2.0 * math.sqrt(2.0) * sd / math.sqrt(n)


def n_for_gap(gap, sd):
    """Smallest integer n per cell with MRD(n) <= gap.  Inverts `mrd`."""
    if not (np.isfinite(gap) and np.isfinite(sd)) or gap <= 0 or sd <= 0:
        return None
    n = 8.0 * (sd / gap) ** 2          # solve 2*sqrt2*sd/sqrt(n) <= gap
    return max(2, int(math.ceil(n - 1e-12)))


def cell_stats(vals):
    """[per-seed values] -> mean / sd(ddof=1) / n / se / MRD.  sd is nan at n<2."""
    v = np.asarray([x for x in vals if np.isfinite(x)], dtype=float)
    n = int(v.size)
    if n == 0:
        return dict(n=0, mean=float("nan"), sd=float("nan"), se=float("nan"),
                    mrd=float("nan"))
    mean = float(np.mean(v))
    sd = float(np.std(v, ddof=1)) if n >= 2 else float("nan")
    se = sd / math.sqrt(n) if n >= 2 else float("nan")
    return dict(n=n, mean=mean, sd=sd, se=se, mrd=mrd(sd, n))


# ------------------------------------------------------------------- adaptation extent
def beta_span(d, window=STEADY[1]):
    """Mean over the window of (beta_true_max - beta_true_min), in LOG UNITS.

    The campaign's "adaptation extent": how far apart the most- and least-adapted
    coordinates are.  It is identically 0.0 on a `--alg-meta fixed` arm by construction
    (HF.py:477 `no_meta_update` returns without touching beta), which is exactly why the
    frozen arms are the zero end of this axis and not a separate category.

    CORRECTIONS 74 (N2) already tested this variable ON THE ns5 LADDER ALONE and rejected
    it in favour of ms.  It is recomputed here across every cell so that rejection is
    re-read against more than one ladder -- reinforcing it or re-opening it, either way
    on data rather than on the one ladder that produced it.
    """
    R = c52_boxfree.records(d)
    lo, hi = int(len(R) * window[0]), int(len(R) * window[1])
    seg = R[lo:hi] or R
    return float(np.mean([r["beta_true_max"] - r["beta_true_min"] for r in seg]))


# ------------------------------------------------------------------------ per-seed row
def per_seed(d, tag, window=STEADY[1]):
    """One probe dir -> the per-SEED row, or None if it does not reduce."""
    r = reduce_dir(d, windows=((STEADY[0], tuple(window)),))
    if not r:
        return None
    w = r["win"].get(STEADY[0])
    if not w:
        return None
    fam, rung, seed = r["fam"], r["rung"], r["seed"]
    lo, hi = box_for(tag, fam)
    try:
        occ = c52_boxfree.occupancy(d, lo, hi)
    except Exception:
        occ = None
    m = float(r["n_tot"])
    try:
        span = beta_span(d, window=window)
    except Exception:
        span = float("nan")
    row = dict(dir=d, fam=fam, rung=rung, seed=seed, m=m,
               rho_s=w["rho_s"], resolved=bool(w["resolved"]),
               neff_m=neff_over_m(m, w["rho_s"]), span=span,
               T=None, epochs=float("nan"),
               rec_lo=float("nan"), rec_hi=float("nan"), boxfree=None)
    if occ:
        row["T"] = occ["T"]
        row["epochs"] = occ["T"] / RECORDS_PER_EPOCH
        row["rec_lo"], row["rec_hi"] = occ["rec_lo"], occ["rec_hi"]
        row["boxfree"] = (occ["rec_lo"] < BOXFREE_MAX and occ["rec_hi"] < BOXFREE_MAX)
    return row


def sweep(root, window=STEADY[1]):
    """probe root -> {(fam, rung): [per-seed rows]}.  Dirs are de-duplicated by realpath
    because probes_ml5_m2/m3/m4 are links onto probes_ml5."""
    tag = root_tag(root)
    cells, seen = {}, set()
    for d in sorted(glob.glob(os.path.join(root, "*"))):
        if not os.path.isdir(d):
            continue
        if not os.path.exists(os.path.join(d, "neg_counts.json")):
            continue
        rp = os.path.realpath(d)
        if rp in seen:
            continue
        seen.add(rp)
        row = per_seed(d, tag, window=window)
        if row is None or row["rung"] is None:
            continue
        cells.setdefault((row["fam"], row["rung"]), []).append(row)
    return cells


# ----------------------------------------------------------------------------- report
def report(roots, window=STEADY[1]):
    print(f"N_eff/m PER-SEED NOISE  --  window {window[0]:g}-{window[1]:g} (steady half)")
    print("MRD = smallest difference two equal-n cells can separate at 2 SE "
          "= 2*sqrt(2)*sd/sqrt(n)\n")
    allrows = []
    for root in roots:
        tag = root_tag(root)
        try:
            cells = sweep(root, window=window)
        except KeyError as e:
            print(f"=== {tag} ===  REFUSED: {e}\n")
            continue
        if not cells:
            continue
        print(f"=== {tag} ===")
        print(f"{'arm':>10} {'rung':>5} {'m':>12} {'ep':>5} {'n':>3} {'bf':>5} "
              f"{'mean':>8} {'sd':>8} {'se':>8} {'MRD':>8}  per-seed")
        for (fam, rung) in sorted(cells, key=lambda k: (k[0], k[1])):
            rows = cells[(fam, rung)]
            st = cell_stats([r["neff_m"] for r in rows])
            nbf = sum(1 for r in rows if r["boxfree"])
            ep = rows[0]["epochs"]
            m = rows[0]["m"]
            per = " ".join(f"{r['neff_m']:.4f}" for r in sorted(rows, key=lambda r: r["seed"] or 0))
            print(f"{fam:>10} {rung:>5} {m:>12,.0f} {ep:>5.0f} {st['n']:>3} "
                  f"{nbf}/{len(rows):>3} {st['mean']:>8.4f} {st['sd']:>8.4f} "
                  f"{st['se']:>8.4f} {st['mrd']:>8.4f}  {per}")
            allrows.append(dict(root=tag, fam=fam, rung=rung, m=m, epochs=ep,
                                nbf=nbf, **st))
        print()
    return allrows


def summarise(allrows):
    """The cross-root roll-up: how the noise scales with the unit and the budget."""
    print("=" * 78)
    print("ROLL-UP 1 -- per-seed sd BY RUNG, box-free cells with n>=2 only")
    print(f"{'rung':>6} {'cells':>6} {'median sd':>10} {'min':>9} {'max':>9} "
          f"{'median m':>12}")
    for rung in ("w", "node", "blk6", "lay"):
        sel = [r for r in allrows if r["rung"] == rung and r["n"] >= 2
               and r["nbf"] == r["n"] and np.isfinite(r["sd"])]
        if not sel:
            continue
        sds = sorted(r["sd"] for r in sel)
        print(f"{rung:>6} {len(sel):>6} {np.median(sds):>10.4f} {sds[0]:>9.4f} "
              f"{sds[-1]:>9.4f} {np.median([r['m'] for r in sel]):>12,.0f}")
    print()
    print("ROLL-UP 2 -- per-seed sd BY BUDGET (epochs), box-free cells with n>=2 only")
    print(f"{'ep':>5} {'cells':>6} {'median sd':>10} {'min':>9} {'max':>9}")
    eps = sorted({round(r["epochs"]) for r in allrows if np.isfinite(r["epochs"])})
    for e in eps:
        sel = [r for r in allrows if round(r["epochs"]) == e and r["n"] >= 2
               and r["nbf"] == r["n"] and np.isfinite(r["sd"])]
        if not sel:
            continue
        sds = sorted(r["sd"] for r in sel)
        print(f"{e:>5} {len(sel):>6} {np.median(sds):>10.4f} {sds[0]:>9.4f} "
              f"{sds[-1]:>9.4f}")
    print()
    print("ROLL-UP 3 -- the +-0.10 blanket bar, in units of each cell's OWN sd")
    print(f"{'root':>6} {'arm':>10} {'rung':>5} {'ep':>4} {'sd':>8} {'0.10/sd':>9}")
    for r in sorted(allrows, key=lambda r: (-(r["sd"] if np.isfinite(r["sd"]) else 0))):
        if not (r["n"] >= 2 and r["nbf"] == r["n"] and np.isfinite(r["sd"]) and r["sd"] > 0):
            continue
        print(f"{r['root']:>6} {r['fam']:>10} {r['rung']:>5} {r['epochs']:>4.0f} "
              f"{r['sd']:>8.4f} {0.10 / r['sd']:>9.1f}")


# ------------------------------------------------------------- the argmin, in SE units
HEADLINE_RUNGS = ("lay", "node", "w")


def se_of_difference(a, b):
    """SE of (mean_a - mean_b) for two independent cells.  sqrt(se_a^2 + se_b^2)."""
    if not (np.isfinite(a["se"]) and np.isfinite(b["se"])):
        return float("nan")
    return math.sqrt(a["se"] ** 2 + b["se"] ** 2)


def argmin_in_se(cells_for_arm):
    """{rung: cell_stats + nbf/n} over the three HEADLINE rungs -> the argmin verdict.

    THE GATE IS CORRECTIONS 79's, APPLIED HERE RATHER THAN RE-DERIVED: an argmin
    inherits the interpretability of EVERY rung it ranks, not just the one it selects.
    A single non-box-free rung -- even one that is nowhere near the minimum -- makes the
    argmin UNINTERPRETABLE.  That is the rule bo6's V2 was read past, four times over.

    Returns dict(status, argmin, runner_up, gap, se, gap_se, blockers).
    `status` is one of: 'UNINTERPRETABLE' (a rung is bound or missing),
    'DECIDED' (gap >= 2 SE), 'UNDECIDED' (gap < 2 SE).
    """
    missing = [r for r in HEADLINE_RUNGS if r not in cells_for_arm]
    blockers = [r for r in HEADLINE_RUNGS
                if r in cells_for_arm and cells_for_arm[r]["nbf"] != cells_for_arm[r]["n"]]
    if missing or blockers:
        return dict(status="UNINTERPRETABLE", argmin=None, runner_up=None,
                    gap=float("nan"), se=float("nan"), gap_se=float("nan"),
                    blockers=blockers, missing=missing)
    order = sorted(HEADLINE_RUNGS, key=lambda r: cells_for_arm[r]["mean"])
    lo, second = order[0], order[1]
    gap = cells_for_arm[second]["mean"] - cells_for_arm[lo]["mean"]
    se = se_of_difference(cells_for_arm[lo], cells_for_arm[second])
    gap_se = gap / se if (np.isfinite(se) and se > 0) else float("nan")
    return dict(status=("DECIDED" if np.isfinite(gap_se) and gap_se >= 2.0
                        else "UNDECIDED"),
                argmin=lo, runner_up=second, gap=gap, se=se, gap_se=gap_se,
                blockers=[], missing=[])


def argmin_report(roots, window=STEADY[1]):
    """Every (root, arm) argmin this campaign owns, re-scored in ITS OWN SE units.

    WHY THIS AND NOT THE +-0.02 BAR.  The campaign has decided argmins against a flat
    0.02 tolerance since cycle 52.  Roll-up 3 shows the per-cell sd spanning 185x, so a
    flat gap bar prices some rungs at 5 SE and others at well under 1.  This restates
    every argmin against the SE of the two cells that produced it, which is what
    STANDING RULE (9) asks for.  It CHANGES NO VERDICT on its own -- it prices them.
    """
    print("=" * 78)
    print("ARGMIN OF N_eff/m OVER {lay, node, w}, PRICED IN ITS OWN SE")
    print("gap/SE >= 2 = DECIDED.  A non-box-free rung ANYWHERE in the ranked set makes")
    print("the argmin UNINTERPRETABLE (CORRECTIONS 79), even when it is not the argmin.")
    print("`span` is the steady-half mean beta_true_max-min in log units, averaged over")
    print("the three rungs -- the adaptation extent CORRECTIONS 74 (N2) tested and rejected")
    print("on the ns5 ladder alone.  It is 0.00 by construction on a frozen (--alg-meta")
    print("fixed) arm.")
    print(f"\n{'root':>7} {'arm':>10} {'ep':>4} {'span':>6} {'argmin':>7} {'2nd':>5} "
          f"{'gap':>8} {'SE':>8} {'gap/SE':>7}  status")
    for root in roots:
        tag = root_tag(root)
        try:
            cells = sweep(root, window=window)
        except KeyError:
            continue
        arms = sorted({fam for (fam, _) in cells})
        for fam in arms:
            byrung = {}
            for (f, rung), rows in cells.items():
                if f != fam or rung not in HEADLINE_RUNGS:
                    continue
                st = cell_stats([r["neff_m"] for r in rows])
                st["nbf"] = sum(1 for r in rows if r["boxfree"])
                st["ep"] = rows[0]["epochs"]
                st["span"] = float(np.nanmean([r["span"] for r in rows]))
                byrung[rung] = st
            if not byrung:
                continue
            v = argmin_in_se(byrung)
            ep = next(iter(byrung.values()))["ep"]
            sp = float(np.nanmean([c["span"] for c in byrung.values()]))
            if v["status"] == "UNINTERPRETABLE":
                why = (f"bound: {','.join(v['blockers'])}" if v["blockers"]
                       else f"missing: {','.join(v['missing'])}")
                print(f"{tag:>7} {fam:>10} {ep:>4.0f} {sp:>6.2f} {'-':>7} {'-':>5} "
                      f"{'-':>8} {'-':>8} {'-':>7}  UNINTERPRETABLE ({why})")
            else:
                print(f"{tag:>7} {fam:>10} {ep:>4.0f} {sp:>6.2f} {v['argmin']:>7} "
                      f"{v['runner_up']:>5} {v['gap']:>8.4f} {v['se']:>8.4f} "
                      f"{v['gap_se']:>7.2f}  {v['status']}")


# ---------------------------------------------------- frozen -> free, the SAME network
# Each pair is (label, frozen root, frozen arm, free root, free arm).  The pairing is
# MATCHED ON THE NETWORK, and that is checked rather than asserted: `lift_report` refuses
# any pair whose per-rung `m` disagrees, because two different networks cannot be a
# frozen-vs-free contrast no matter what the arm is called.
#   frozen = `--alg-meta fixed` -> HF.py:477 `no_meta_update` returns without touching
#   beta, while `_probe` (HF.py:95) still fires: alpha stays uniform across groups and
#   the ONLY difference from the free arm is that beta does not adapt (FINDINGS 7708-24).
#   uc5's own c100 arm is NOT used -- it is the batch voided by the --NN-name bug
#   (CORRECTIONS, cycle 52); uc6 is the re-run and is the comparator here.
FROZEN_FREE_PAIRS = (
    ("r18c10 (ResNet18/CIFAR-10)",  "../probes_p5",  "r18c10", "../probes_cl5", "cU"),
    ("r10    (ResNet10/CIFAR-10)",  "../probes_fz3", "r10",    "../probes_uc5", "r10"),
    ("r34    (ResNet34/CIFAR-10)",  "../probes_fz3", "r34",    "../probes_uc5", "r34"),
    ("c100   (ResNet18/CIFAR-100)", "../probes_fz3", "c100",   "../probes_uc6", "c100"),
)


def lift_report(window=STEADY[1]):
    """N_eff/m(free) / N_eff/m(frozen), per rung, on network-matched pairs.

    WHAT IT IS FOR.  CORRECTIONS 47 measured that adaptation consumes the correlated
    component SCALE-SELECTIVELY (22.92x at k=1, 5.49x at k=775, 0.77x at k=180,225) on
    ONE family, through rho.  This recomputes the same contrast through N_eff/m on four
    network-matched families.  If the ordering holds, the "nodewise minimum" is not a
    property of the nodewise partition at all -- it is where the frozen minimum (always
    weightwise) has been lifted PAST by a larger lift at a finer rung.

    POST-HOC.  These pairs were assembled from data already on disk.  Nothing here is a
    registered test and none of it may overturn a registered gate (CORRECTIONS 76(1),
    read symmetrically per 79).
    """
    print("=" * 78)
    print("FROZEN -> FREE LIFT IN N_eff/m, NETWORK-MATCHED (post-hoc inventory)")
    print("frozen = --alg-meta fixed (beta never moves, so the box is inert and the")
    print("box-free flag on those arms is vacuous BY CONSTRUCTION, not by measurement).")
    print(f"\n{'family':>28} {'rung':>5} {'m':>12} {'frozen':>8} {'free':>8} {'lift':>7}")
    for label, froot, farm, uroot, uarm in FROZEN_FREE_PAIRS:
        fz, fr = sweep(froot, window=window), sweep(uroot, window=window)
        for rung in HEADLINE_RUNGS:
            a, b = fz.get((farm, rung)), fr.get((uarm, rung))
            if not a or not b:
                print(f"{label:>28} {rung:>5}  MISSING on one side -- pair refused")
                continue
            ma, mb = a[0]["m"], b[0]["m"]
            if ma != mb:
                print(f"{label:>28} {rung:>5}  m DISAGREES ({ma:,.0f} vs {mb:,.0f}) "
                      f"-- NOT the same network, pair refused")
                continue
            va = float(np.mean([r["neff_m"] for r in a]))
            vb = float(np.mean([r["neff_m"] for r in b]))
            print(f"{label:>28} {rung:>5} {ma:>12,.0f} {va:>8.4f} {vb:>8.4f} "
                  f"{vb / va:>6.2f}x")
        print()


# ------------------------------------------------------------- absolute-epoch time course
EPOCH_WINDOWS = ((0, 10), (10, 20), (20, 30), (30, 40))


def timecourse(roots, windows=EPOCH_WINDOWS):
    """N_eff/m per rung in ABSOLUTE EPOCH windows, so a 20-epoch and a 40-epoch run are
    read over the same stretch of training rather than over the same FRACTION of it.

    WHY ABSOLUTE.  Every budget comparison this campaign has made contrasts the steady
    HALF of a 20-epoch run with the steady HALF of a 40-epoch run -- two different
    stretches of training.  CORRECTIONS' own B1.5 arm was added for exactly this reason.
    Records 1000-2000 are epochs 10-20 in BOTH runs; expressing the window in epochs
    makes that the default rather than a special case.

    WHAT IT IS FOR.  55.5's mechanism predicts the weightwise lift is TRANSIENT: N_eff/m
    at weightwise rises under adaptation and then falls back, which is the only way the
    argmin can be `node` at 20 epochs and `w` again at 40.  A within-run curve tests that
    without a single new job.

    The box-free flag shown is the WHOLE-RUN one -- a per-window occupancy would be the
    honest column and is not computed here; a run that binds late contaminates its late
    windows only.  Read `first_hi` from c52_boxfree for that.
    """
    print("=" * 78)
    print("N_eff/m IN ABSOLUTE EPOCH WINDOWS (within-run, seeds averaged)")
    print("bf = WHOLE-RUN box-free seed count, not per-window.  A late bind contaminates")
    print("late windows only -- check first_hi in c52_boxfree before quoting a late cell.")
    for root in roots:
        tag = root_tag(root)
        base = sweep(root)                       # for the box-free flags and epochs
        if not base:
            continue
        print(f"\n=== {tag} ===")
        hdr = "  ".join(f"{a}-{b}ep" for a, b in windows)
        print(f"{'arm':>10} {'rung':>5} {'n':>3} {'bf':>4}   {hdr}")
        for (fam, rung) in sorted(base):
            rows = base[(fam, rung)]
            ep_total = rows[0]["epochs"]
            nbf = sum(1 for r in rows if r["boxfree"])
            cells = []
            for (a, b) in windows:
                if b > ep_total + 1e-9:
                    cells.append("     -")
                    continue
                frac = (a / ep_total, b / ep_total)
                vals = []
                for r in rows:
                    red = reduce_dir(r["dir"], windows=(("win", frac),))
                    w = red["win"].get("win") if red else None
                    if w:
                        vals.append(neff_over_m(r["m"], w["rho_s"]))
                cells.append(f"{np.mean(vals):6.4f}" if vals else "     -")
            print(f"{fam:>10} {rung:>5} {len(rows):>3} {nbf}/{len(rows):<2} "
                  + "  ".join(f"{c:>6}" for c in cells))


# --------------------------------------------------------------------------- crosscheck
def crosscheck(root, window=STEADY[1], tol=5e-4):
    """The seed-MEAN of this module's per-seed N_eff/m must reproduce
    `neff_instrument.py`'s published N_eff/m for the same root.

    NOTE the two are NOT identical by construction: neff_instrument averages rho_s over
    seeds and inverts ONCE, this module inverts per seed and averages.  Jensen makes them
    differ by O(curvature * var(rho)).  The check is therefore a CONSISTENCY check with a
    stated tolerance, and a violation is reported with both numbers rather than hidden.
    """
    import neff_instrument
    ref = neff_instrument.reduce_root(root, window=list(window))
    cells = sweep(root, window=window)
    print(f"crosscheck {root_tag(root)}: mean-of-inverses vs inverse-of-mean "
          f"(tol {tol:g})")
    bad = 0
    for (fam, rung), rows in sorted(cells.items()):
        mine = float(np.mean([r["neff_m"] for r in rows]))
        theirs = ref.get(fam, {}).get(rung)
        if not theirs:
            continue
        t = theirs["neff_var"] / theirs["m"]
        ok = abs(mine - t) <= tol
        bad += (not ok)
        print(f"  {fam:>10} {rung:>5}  mine {mine:.6f}  neff_instrument {t:.6f}  "
              f"d {mine - t:+.6f}  {'ok' if ok else 'DIFFERS'}")
    print(f"  -> {bad} cell(s) outside tolerance")
    return bad


# ---------------------------------------------------------------------------- selftest
def _selftest():
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    # --- neff_over_m
    ck("neff_over_m rho=0 -> 1", abs(neff_over_m(1000, 0.0) - 1.0) < 1e-12)
    ck("neff_over_m rho=1 -> 1/m", abs(neff_over_m(1000, 1.0) - 1e-3) < 1e-12)
    ck("neff_over_m m=1 -> 1", abs(neff_over_m(1, 0.5) - 1.0) < 1e-12)
    ck("neff_over_m nan rho -> nan", math.isnan(neff_over_m(10, float("nan"))))
    ck("neff_over_m negative den -> nan",
       math.isnan(neff_over_m(10, -1.0)))          # 1 + 9*(-1) = -8
    # matches neff_instrument's own inversion
    import neff_instrument as NI
    ck("agrees with neff_instrument.neff_from_rho",
       abs(neff_over_m(14420, 0.01) - NI.neff_from_rho(14420, 0.01) / 14420) < 1e-12)

    # --- mrd / n_for_gap, pinned to the ONE case the campaign has already priced
    # CORRECTIONS 80: sd 0.0131, gap 0.0142 -> "n=7 per rung resolves at 2 SE".
    ck("MRD reproduces CORRECTIONS 80 (sd .0131, n=7 -> ~.0140)",
       abs(mrd(0.0131, 7) - 0.01400) < 5e-5)
    ck("MRD(n=7) <= the 0.0142 gap it was priced against", mrd(0.0131, 7) <= 0.0142)
    ck("MRD(n=6) > the gap (7 is the SMALLEST n that works)", mrd(0.0131, 6) > 0.0142)
    ck("n_for_gap inverts MRD", n_for_gap(0.0142, 0.0131) == 7)
    ck("MRD falls as 1/sqrt(n)", abs(mrd(0.02, 8) - mrd(0.02, 2) / 2.0) < 1e-12)
    ck("MRD nan at n<2", math.isnan(mrd(0.02, 1)))
    ck("n_for_gap floors at 2", n_for_gap(10.0, 0.001) == 2)
    ck("n_for_gap None on zero gap", n_for_gap(0.0, 0.01) is None)

    # --- cell_stats
    st = cell_stats([1.0, 2.0, 3.0])
    ck("cell_stats mean", abs(st["mean"] - 2.0) < 1e-12)
    ck("cell_stats sd is ddof=1", abs(st["sd"] - 1.0) < 1e-12)
    ck("cell_stats se", abs(st["se"] - 1.0 / math.sqrt(3)) < 1e-12)
    ck("cell_stats n", st["n"] == 3)
    ck("cell_stats n=1 -> sd nan", math.isnan(cell_stats([5.0])["sd"]))
    ck("cell_stats n=1 -> mean still reported", cell_stats([5.0])["mean"] == 5.0)
    ck("cell_stats drops nan", cell_stats([1.0, float("nan"), 3.0])["n"] == 2)
    ck("cell_stats empty -> n=0", cell_stats([])["n"] == 0)

    # --- box registry: refusal is the point
    ck("box_for known root", box_for("br6", "c2") == (-30.0, 2.0))
    ck("box_for arm-specific beats root", box_for("cl5", "cU") == (-30.0, 0.0))
    ck("box_for arm-specific cD", box_for("cl5", "cD") == (-30.0, -4.6052))
    try:
        box_for("nosuchroot", "x")
        ck("box_for RAISES on unregistered root", False)
    except KeyError:
        ck("box_for RAISES on unregistered root", True)
    # every root that has probe dirs on disk must be registered, or the sweep is partial
    unreg = []
    on_disk = sorted(glob.glob(os.path.join(PROBE_HOME, "probes_*")))
    ck("the probe mirrors were actually FOUND (an empty glob passes vacuously)",
       len(on_disk) > 0)
    for r in on_disk:
        if not glob.glob(os.path.join(r, "*", "neg_counts.json")):
            continue
        t = root_tag(r)
        if t not in BOXES and not any(k.startswith(t + ":") for k in BOXES):
            unreg.append(t)
    ck(f"every on-disk probe root is registered (unregistered: {unreg or 'none'})",
       not unreg)

    # --- records -> epochs
    ck("100 records per epoch", RECORDS_PER_EPOCH == 100)
    ck("bo6's 2000 records = 20 epochs", 2000 / RECORDS_PER_EPOCH == 20)
    # bo6's V0.3 reported first_hi 1603 at epoch 16.0 -- the conversion must reproduce it
    ck("bo6 first_hi 1603 -> epoch 16.0", abs(1603 / RECORDS_PER_EPOCH - 16.03) < 1e-9)

    # --- root_tag
    ck("root_tag strips probes_", root_tag("../probes_br6") == "br6")
    ck("root_tag tolerates trailing slash", root_tag("../probes_br6/") == "br6")

    # --- argmin_in_se, on the LITERAL shapes this campaign has already argued about
    def cell(mean, sd, n, nbf=None):
        return dict(mean=mean, sd=sd, n=n, se=sd / math.sqrt(n),
                    mrd=mrd(sd, n), nbf=(n if nbf is None else nbf))

    # cl5 cU (the SGDm control behind CORRECTIONS 70's nodewise minimum), all box-free
    cl5 = {"lay": cell(0.7262, 0.0227, 3),
           "node": cell(0.4056, 0.0492, 3),
           "w": cell(0.5064, 0.0377, 3)}
    v = argmin_in_se(cl5)
    ck("cl5/cU argmin is node", v["argmin"] == "node")
    ck("cl5/cU runner-up is w", v["runner_up"] == "w")
    ck("cl5/cU gap ~0.1008", abs(v["gap"] - 0.1008) < 5e-4)
    ck("cl5/cU is DECIDED at >=2 SE", v["status"] == "DECIDED")
    # and the point of the whole module: it is 2.8 SE, not the 5x the 0.02 bar implied
    ck("cl5/cU gap is ~2.8 SE, not 5x a flat bar", 2.6 < v["gap_se"] < 3.1)

    # ns5 m2p4 (N1 at ms=2e-4) -- the gap CORRECTIONS 80 could not decide at n=3
    ns5 = {"lay": cell(0.6656, 0.0323, 3),
           "node": cell(0.2275, 0.0123, 3),
           "w": cell(0.2133, 0.0138, 3)}
    v = argmin_in_se(ns5)
    ck("ns5/m2p4 argmin is w", v["argmin"] == "w")
    ck("ns5/m2p4 is UNDECIDED at n=3", v["status"] == "UNDECIDED")
    ck("ns5/m2p4 gap/SE is ~1.3", 1.1 < v["gap_se"] < 1.6)

    # bo6 -- node AND w bound.  The shape c54_score read past FOUR TIMES.
    bo6 = {"lay": cell(0.4294, 0.0051, 2),
           "node": cell(0.1199, 0.0261, 2, nbf=0),
           "w": cell(0.0200, 0.0001, 2, nbf=0)}
    v = argmin_in_se(bo6)
    ck("bo6 argmin is UNINTERPRETABLE", v["status"] == "UNINTERPRETABLE")
    ck("bo6 names BOTH bound rungs", set(v["blockers"]) == {"node", "w"})
    ck("bo6 reports NO argmin rather than defaulting", v["argmin"] is None)

    # ff5 r34 -- ONLY `lay` is bound, and lay is the MAXIMUM, not the argmin.
    # "a bound rung that is NOT the argmin still blocks" (CORRECTIONS 79).
    ff5 = {"lay": cell(0.6285, 0.0147, 2, nbf=0),
           "node": cell(0.3936, 0.0617, 2),
           "w": cell(0.5568, 0.0750, 2)}
    v = argmin_in_se(ff5)
    ck("a bound NON-argmin rung still blocks", v["status"] == "UNINTERPRETABLE")
    ck("the blocker named is lay", v["blockers"] == ["lay"])

    # a missing rung is a blocker too, and is reported as missing rather than as bound
    v = argmin_in_se({"node": cell(0.2, 0.01, 3), "w": cell(0.3, 0.01, 3)})
    ck("a MISSING rung blocks", v["status"] == "UNINTERPRETABLE")
    ck("a missing rung is reported as missing, not bound", v["missing"] == ["lay"])

    # the 2-SE boundary.  NOT tested at exactly 2.0 -- se_of_difference goes through a
    # sqrt, so "exactly 2 SE" is a float artefact and not a state the data can be in.
    two_se = 2.0 * math.sqrt(0.005 ** 2 + 0.005 ** 2)
    just_over = {"lay": cell(0.9, 0.01, 4), "node": cell(0.5, 0.01, 4),
                 "w": cell(0.5 + two_se * 1.001, 0.01, 4)}
    just_under = {"lay": cell(0.9, 0.01, 4), "node": cell(0.5, 0.01, 4),
                  "w": cell(0.5 + two_se * 0.999, 0.01, 4)}
    ck("just over 2 SE is DECIDED", argmin_in_se(just_over)["status"] == "DECIDED")
    ck("just under 2 SE is UNDECIDED", argmin_in_se(just_under)["status"] == "UNDECIDED")
    ck("SE of a difference is sqrt(se_a^2+se_b^2)",
       abs(se_of_difference(cell(0, 0.03, 9), cell(0, 0.04, 16))
           - math.sqrt(0.01 ** 2 + 0.01 ** 2)) < 1e-12)

    ok = sum(1 for _, c in checks if c)
    for name, c in checks:
        if not c:
            print(f"  FAIL: {name}")
    print(f"selftest: {ok}/{len(checks)} PASS")
    return 0 if ok == len(checks) else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    if "--price" in argv:
        i = argv.index("--price")
        gap, sd = float(argv[i + 1]), float(argv[i + 2])
        n = n_for_gap(gap, sd)
        print(f"gap {gap:.4f}, per-seed sd {sd:.4f} -> n={n} per cell "
              f"(MRD {mrd(sd, n):.4f} at 2 SE)")
        return 0
    if "--crosscheck" in argv:
        i = argv.index("--crosscheck")
        return 0 if crosscheck(argv[i + 1]) == 0 else 1
    if "--lift" in argv:
        lift_report()
        return 0
    if "--timecourse" in argv:
        rs = [a for a in argv[1:] if not a.startswith("--")]
        timecourse(rs)
        return 0
    if "--all" in argv:
        roots = sorted(r for r in glob.glob(os.path.join(PROBE_HOME, "probes_*"))
                       if glob.glob(os.path.join(r, "*", "neg_counts.json"))
                       and root_tag(r) not in ALIAS_ROOTS)
    else:
        roots = [a for a in argv[1:] if not a.startswith("--")]
    if not roots:
        print(__doc__)
        return 1
    if "--argmin" in argv:
        argmin_report(roots)
        return 0
    summarise(report(roots))
    print()
    argmin_report(roots)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
