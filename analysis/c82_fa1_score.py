#!/usr/bin/env python3
"""c82_fa1_score.py -- score `fa1`.  THE A3 FIELD-vs-ACCURACY READING AT A CEILING
THAT CANNOT BIND, AND THE BOX CONTROL THAT MAKES IT READABLE.

REGISTERED GATES, transcribed from `bin/c82_field_wideclip.sh`.  Every constant
below is asserted by the selftest against THAT SCRIPT'S OWN TEXT so the
registration and the batch cannot drift -- STANDING RULE (19).

WRITTEN, SELFTESTED AND GIT-COMMITTED BEFORE ANY `fa1` JOB WAS SUBMITTED, WHILE NO
`fa1` RUN EXISTED IN THE CSV AT ALL.  Not merely before the verdict was read --
before the data could exist.

THE FOUR ARMS, one batch, ms=3e-4, 100 ep, seeds 0-2 (**deliberately ar1's OWN
seeds**, so F3 is paired at zero extra compute).  TWO MATCHED-COUNT PAIRS:
    node  nodewise    m=14,420   |  ch   chunk777    m=14,421   (1 group apart)
    n1d   nodewise1d  m= 4,851   |  c23  chunk2325   m= 4,851   (EXACT)
ONE FIELD CHANGES FROM `ar1`: **BETA_CLIP -15:-2.3026 -> -25:9.0.**

WHY, AND THE DEFLATION FIRST.  `ar1` VOIDED A3 with 12/12 arms on the LOW guard
(rec_lo 0.4521-0.4597, first pin at step 27,020-27,395 of 50,000).  **But the
scientific question A3 asked is already CLOSED**: `cc1` ran the same test at
ms=1e-4, 12/12 box-free, and C1 returned MIXED -- ANTI-CONCORDANT on chunk777 -
nodewise (d_acc +0.727 t +3.63, d_N_eff/m -0.0237 t -11.14) and DISSOCIATION on
chunk2325 - nodewise1d (d_acc +0.011 t +0.08, d_N_eff/m -0.0529 t -23.26).
**DIRECTION C IS DROPPED (CORRECTIONS 110.2, 110.5(1)) AND NOTHING BELOW REOPENS
IT.**  What fa1 uniquely buys is narrower: every 100-ep ResNet18 probe at ms=1e-4
in the old box is box-FREE (39/39) and every one at ms=3e-4 is LO-BOUND (15/15), so
the campaign's stepsize axis is perfectly confounded with its box-binding axis --
a STANDING RULE 10 violation sitting under a headline.  fa1 changes one field and
retires it.

**CAN fa1 RE-READ ar1's A1/A2?  NO.  THIS BATCH IS INSTRUMENT-ONLY.**  The guard
bound DIFFERENTIALLY across exactly the arms A1 compares: at the final record
nodewise has 11.25-11.74% of its 14,420 coordinates on the floor against chunk777's
0.159-0.173% of 14,421, a 68-71x difference (85x over all records); the clamp was
live for the final 45.2-46.0% of training, which is the half plateau5 is read from;
and in n1d/ch/c23 15-17 of the 41 one-dimensional tensors had their single group
pinned -- the very size-1 tail A1-A2 exists to isolate.  Therefore **F2's D_w may
NOT be appended to the mm1/pp1/ar1/cc1 D series as a fifth replication**, and every
fa1 number is quoted with its box.  Whether freeing the floor helps or hurts
nodewise is **UNSURE** -- that is why F3 is mandatory, not optional.

  F0    VALIDITY.  n_records == 10000; beta moved; epochs_done == requested == 100.
  F0.2  n_beta EXACT on EVERY record: node 14420, ch 14421, n1d 4851, c23 4851.
        All four MEASURED by the batch script's guard 4 from the ALLOCATED beta on
        the real built network, which ALSO asserted D_w's pair <= 1 group apart and
        G_w's EXACT.
  F0.3  THE INSTRUMENT FIRED.  neg_counts.json, n_tot == n_beta, npy shape READ FROM
        ITS HEADER == (n_tot,).  (Header, never file size -- that inference produced
        c74's false VOID on 12/12 arms.)
  F0.4  **THE BOX-OCCUPANCY GATE, SCORED PER SEED.**  The published rec_-based 5%
        gate at BOTH guards, PRIMARY and UNCHANGED.  **A BIND VOIDS F1, THIS BATCH'S
        OWN PRIMARY TEST** -- the same rule ar1 wrote in advance and then had fire on
        itself.  F2 and F3 are accuracy-only and stand, but every number they produce
        is then reported with its measured occupancy beside it (rule 5).  Occupancy
        is printed for all 12 arms whatever the outcome.
  F0.5  **THE IDENTITY GATE.**  HF.py's Lion meta update is
        beta <- (1 - ms*wd_meta)*beta - ms*sign(.) and every fa1 job carries
        --weight-decay-meta 0, so each update moves each coordinate by exactly 0 or
        +-ms and beta is confined to [ln(alpha0) - ms*T, ln(alpha0) + ms*T] =
        [-21.907755, +8.092245] at alpha0=1e-3, ms=3e-4, T = 100 ep x 500 = 50,000.
        The box (-25, +9.0) lies strictly outside on both sides, so **a record at
        either guard is ALGEBRAICALLY IMPOSSIBLE and means the config is not what the
        header says** (wd_meta != 0, wrong ms, wrong step count, a resumed run).  If
        F0.5 fires the batch is **VOID -- do not rescore, debug the config.**  The
        bound is checked here with the documented one-update offset: HF.py clamps
        (PATCH_CLIP) before it probes (PATCH_PROBE), so the record labelled step 0
        has already taken one update, and on ar1's 120,000 records the worst slack is
        exactly -0.000300 = one ms step with ZERO violations beyond it.

  F1    **THE PRIMARY.  THE CONCORDANCE READING AT ms=3e-4 UNDER A NON-BINDING BOX.**
        For each matched-count pair: d_acc = dplateau5, d_fld = dN_eff/m, each with a
        Welch t at n=3.  A channel is RESOLVED at |t| >= 2.0.
        **CONVENTION, TRANSCRIBED UNCHANGED FROM `analysis/c81_cc1_score.py`'s C1
        (itself unchanged from `c79_ar1_score.py`'s A3): higher N_eff/m -> higher
        plateau5 = CONCORDANT.**  That is the direction the noise-averaging
        literature implies (more effective independence = more information per
        meta-step).
          both pairs resolved on BOTH channels, both ANTI-CONCORDANT
             -> REPLICATES cc1's ANTI-CONCORDANT leg at a second stepsize and a
                non-binding box.  Direction C stays DROPPED.
          MIXED (any combination of CONCORDANT / ANTI-CONCORDANT / DISSOCIATION)
             -> REPLICATES cc1's own MIXED verdict.  Direction C stays DROPPED.
          both pairs resolved on BOTH channels, both CONCORDANT
             -> **DISCREPANCY WITH cc1, LOGGED FOR THE RECORD.**  It does NOT reopen
                direction C: it would say the field's sign is stepsize- or
                box-dependent, which makes it LESS of a design variable, not more.
          a pair RESOLVED on field, UNRESOLVED on accuracy -> DISSOCIATION.
          a pair UNRESOLVED on FIELD -> UNINFORMATIVE, reported, NOT folded in.
        **F1 IS VOID IF F0.4 FAILS ON ANY ARM.**  A void here is not another owed
        re-run -- the question is closed; a second void would only say this box
        binds too.

  F2    THE ACCURACY CONTRASTS **IN THIS BOX, AND ONLY IN THIS BOX.**
          D_w = plateau5(chunk777)  - plateau5(nodewise)     m 14,421 vs 14,420
          G_w = plateau5(chunk2325) - plateau5(nodewise1d)   m 4,851 EXACT
        FOUR BANDS, FIXED NOW, IDENTICAL FOR D_w AND G_w, calibrated against the
        three BOX-FREE readings of D the campaign owns (mm1 +0.485, pp1 +0.581,
        cc1 +0.727) so that SURVIVES means "indistinguishable from the box-free
        evidence":
          >= +0.45       -> SURVIVES     (not a guard artefact)
          [+0.15, +0.45) -> ATTENUATED   (box-dependent; ar1's +0.697 acquires an
                                          "at BETA_CLIP=-15:-2.3026" qualifier,
                                          permanently)
          (-0.15, +0.15) -> COLLAPSES    (the ms=3e-4 cell is a guard artefact and is
                                          dropped from the D series)
          <= -0.15       -> INVERTS      (the strongest available refutation; never
                                          softened to "collapses")
        The negative side is deliberately NOT subdivided.  PRIOR EXPECTATION ON G_w,
        stated so it cannot be claimed afterwards: ar1 read -0.139 and cc1 read
        +0.011, so G_w is EXPECTED to COLLAPSE; a G_w outside that band with
        |t| >= 2 would say the guard was doing arm-specific work on the tail-FREE
        contrast too, which UNDERCUTS the tail interpretation of A1-A2.

  F3    **THE PAIRED BOX EFFECT, PER ARM.  THE CONTROL THAT MAKES F2 READABLE.**
        Delta_arm = plateau5(fa1 arm, seed s) - plateau5(ar1 arm, seed s), paired over
        s in {0,1,2}; RESOLVED at |t| >= 2.0 on the paired differences.
          resolved on ANY arm -> **THE BOX CHANGED THE OPTIMISER, NOT MERELY THE
             INSTRUMENT.**  D_w may not be pooled with ar1's D under any
             circumstances and every sentence about D carries its box thereafter.
          no arm resolved -> **UNRESOLVED at this test's own ~0.20-0.25 pp floor.**
             **This may NOT be written as "the box is accuracy-neutral."**  Declared
             now, because the campaign has previously written exactly that sentence
             off an underpowered null.

  F4    THE CLIP METER.  DESCRIPTIVE.  rec_lo / rec_hi / coord_lo / coord_hi and
        beta_true_min/max per arm, printed AFTER F1-F3.  Its only job is to document
        how much headroom the hard bound actually left.  It cannot gate F1, F2 or F3
        beyond the F0.4 void it already feeds.

WHAT THIS SCORER WILL NOT DO
  * It will not reopen direction C under ANY F1 outcome.  cc1's five-way
    pre-registered test decided it and the question is CLOSED.
  * It will not pool D_w with ar1's D, and it will not print D_w as a fifth
    replication of the D series.
  * It will not let F4 gate, annotate or reorder F1, F2 or F3.
  * It will not read F1 if any arm is box-bound.
  * It will not write "the box is accuracy-neutral" off an unresolved F3.
  * It will not claim any arm's argmax.  Two stepsizes are two points.
  * It will not separate "the group-size distribution" from "the parameter role" on
    the 1-D tensors -- on ResNet18 those coincide EXACTLY (FINDINGS 78.1).
  * It will not re-derive an independence null on the fly (CORRECTIONS 26), and it
    will not print "53.1%".

USAGE
  python3 analysis/c82_fa1_score.py --selftest
  python3 analysis/c82_fa1_score.py --root ../probes_fa1 --csv results/all_runs.csv
"""
import argparse
import csv
import glob
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
SCRIPT = os.path.join(REPO, "bin", "c82_field_wideclip.sh")

from c52_boxfree import occupancy, records           # noqa: E402

# --- THE REGISTRATION -------------------------------------------------------
LO, HI = -25.0, 9.0                 # `fa1`, registered in c55_neff_noise.BOXES
CLIP_REF = "-15:-2.3026"            # ar1's box: LO-bound 12/12, HI-bound 1/12
EPOCHS = 100
N_RECORDS = 10000
MST = "3e-4"                        # ar1's stepsize, UNCHANGED -- the box is the axis
ALPHA0 = 1e-3
BATCH = 100
STEPS_PER_EPOCH = 500               # MEASURED by the script's guard 4d, not assumed
CHUNK_K = 777
CHUNK_K2 = 2325
NJOBS = 12
SEEDS = ("0", "1", "2")             # ar1's OWN seeds -- F3 is paired
REF_FAM = "ar1"
ARMS = ("node", "ch", "n1d", "c23")
# n_beta per arm, MEASURED from the ALLOCATED beta by the script's guard 4.
M_OF_ARM = {"node": 14420, "ch": 14421, "n1d": 4851, "c23": 4851}
GRAN_OF_ARM = {"node": "nodewise", "ch": "chunk777",
               "n1d": "nodewise1d", "c23": "chunk2325"}

# The Lion identity the box was BUDGETED from (F0.5).  Not a fit, not a trace.
T_UPDATES = EPOCHS * STEPS_PER_EPOCH             # 50,000
MS = float(MST)
BETA0 = math.log(ALPHA0)                         # -6.907755
SPAN = MS * T_UPDATES                            # 15.0
REACH_LO, REACH_HI = BETA0 - SPAN, BETA0 + SPAN  # -21.907755, +8.092245

# The FOUR-WAY accuracy band, IDENTICAL for D_w and G_w.
SURVIVES_AT = 0.45          # the lowest BOX-FREE reading of D is mm1's +0.485
NULL_HALF = 0.15            # the campaign's null half-width, unchanged
RESOLVED_T = 2.0            # a channel / a paired Delta is RESOLVED at |t| >= 2.0
BOXFREE_MAX = 0.05          # the published rec_-based 5% gate, unchanged

# The three BOX-FREE anchors F2's bands are calibrated against.  POST-HOC and
# DESCRIPTIVE: used to place a threshold, never quoted as a prediction.
D_BOXFREE_ANCHORS = {"mm1": 0.485, "pp1": 0.581, "cc1": 0.727}
D_AR1_BOUND = 0.697         # ar1's own D, measured with 12/12 arms box-bound
G_AR1_BOUND = -0.139
G_CC1_FREE = 0.011

# The two matched-count pairs.  (gate, hi arm, lo arm, what it isolates)
PAIRS = (
    ("D_w", "ch", "node", "aligned vs uniform at m=14,420"),
    ("G_w", "c23", "n1d", "aligned vs uniform at m=4,851, size-1 tail already gone"),
)


def _sem(v):
    return statistics.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else float("nan")


def _t(a, b):
    se = math.sqrt(_sem(a) ** 2 + _sem(b) ** 2)
    if not (se > 0):
        return float("nan")
    return (statistics.mean(a) - statistics.mean(b)) / se


def _t_paired(d):
    """One-sample t on the paired differences -- F3's statistic."""
    if len(d) < 2:
        return float("nan")
    s = _sem(d)
    if not (s > 0):
        return float("nan")
    return statistics.mean(d) / s


def band(g):
    """The FOUR-WAY registered accuracy verdict, shared by D_w and G_w."""
    if g >= SURVIVES_AT:
        return "SURVIVES"
    if g >= NULL_HALF:
        return "ATTENUATED"
    if g > -NULL_HALF:
        return "COLLAPSES"
    return "INVERTS"


def arm_rows(csv_path, fam, arm):
    """{seed: plateau5} for one arm of one family -- keyed by seed, so F3 pairs."""
    out = {}
    with open(csv_path) as fh:
        for r in csv.DictReader(fh):
            if not r["run"].startswith("%s-%s-s" % (fam, arm)):
                continue
            if int(r["epochs_done"] or 0) != EPOCHS or not r["plateau5"]:
                continue
            out[r["seed"]] = float(r["plateau5"])
    return out


def arm_of_dir(d):
    parts = os.path.basename(d).split("_")
    return parts[1] if len(parts) > 2 and parts[0] == "probe" else None


def neff_of_dir(d):
    import probe5_window as p5w
    w = p5w.reduce_dir(d, windows=(("steady .5-1", (0.5, 1.0)),))
    if w is None:
        return None
    ww = w["win"].get("steady .5-1")
    if not ww or ww["rho_s"] is None:
        return None
    mm, rho = float(w["n_tot"]), ww["rho_s"]
    return 1.0 / (1.0 + (mm - 1.0) * rho)


def identity_slack(d):
    """min over records of the distance to the Lion bound, with the one-update
    offset.  Negative by more than one ms step == the config is not the header."""
    worst = float("inf")
    n = 0
    for r in records(d):
        st = int(r.get("step", 0))
        worst = min(worst,
                    r["beta_true_min"] - (BETA0 - MS * st),
                    (BETA0 + MS * st) - r["beta_true_max"])
        n += 1
    return worst, n


# ---------------------------------------------------------------------------
def selftest():
    p = n = 0

    def ck(name, cond):
        nonlocal p, n
        n += 1
        p += bool(cond)
        print("    %-72s %s" % (name, "ok" if cond else "FAIL"))

    src = open(SCRIPT).read() if os.path.exists(SCRIPT) else ""
    doc = __doc__
    me = open(os.path.abspath(__file__)).read()
    flat = lambda s: " ".join(s.split())
    # The batch script's prose lives in a COMMENT BLOCK, so a sentence that wraps
    # carries a leading "#" on its continuation line.  flat_sh strips the comment
    # markers before normalising whitespace, so an assertion is about the SENTENCE
    # rather than the column it happened to wrap at.
    flat_sh = lambda s: " ".join(
        l.lstrip().lstrip("#").strip() for l in s.splitlines()).replace("  ", " ")

    print("c82_fa1_score selftest")
    print("  -- the constants, asserted against the BATCH SCRIPT's own text --")
    ck("the batch script exists at bin/c82_field_wideclip.sh", bool(src))
    ck("script CLIP= is this scorer's box", "CLIP=-25:9.0" in src)
    ck("script CLIP_REF= is ar1's box", "CLIP_REF=%s" % CLIP_REF in src)
    ck("script MST= is %s" % MST, "MST=%s" % MST in src)
    ck("script ALPHA0= is 1e-3", "ALPHA0=1e-3" in src)
    ck("script EPOCHS= is %d" % EPOCHS, "EPOCHS=%d" % EPOCHS in src)
    ck("script BATCH= is %d" % BATCH, "BATCH=%d" % BATCH in src)
    ck("script STEPS_PER_EPOCH= is %d" % STEPS_PER_EPOCH,
       "STEPS_PER_EPOCH=%d" % STEPS_PER_EPOCH in src)
    ck("script NJOBS= is %d" % NJOBS, "NJOBS=%d" % NJOBS in src)
    ck("script CHUNK_K= is %d" % CHUNK_K, "CHUNK_K=%d" % CHUNK_K in src)
    ck("script CHUNK_K2= is %d" % CHUNK_K2, "CHUNK_K2=%d" % CHUNK_K2 in src)
    ck("script SEEDS= are ar1's own seeds", 'SEEDS="%s"' % " ".join(SEEDS) in src)
    ck("script REF_FAM= is %s" % REF_FAM, "REF_FAM=%s" % REF_FAM in src)
    for a, m in sorted(M_OF_ARM.items()):
        keyed = {"node": "M_NODE", "ch": "M_CHUNK", "n1d": "M_N1D", "c23": "M_CHUNK2"}[a]
        ck("script %s=%d matches arm %r" % (keyed, m, a), "%s=%d" % (keyed, m) in src)
    ck("script's arm loop is exactly the 4 declared arms",
       all(tok in src for tok in ('"nodewise:node"', '"chunk${CHUNK_K}:ch"',
                                  '"nodewise1d:n1d"', '"chunk${CHUNK_K2}:c23"')))
    ck("GRAN_OF_ARM['ch'] is what the script's CHUNK_K expands to",
       GRAN_OF_ARM["ch"] == "chunk%d" % CHUNK_K)
    ck("GRAN_OF_ARM['c23'] is what the script's CHUNK_K2 expands to",
       GRAN_OF_ARM["c23"] == "chunk%d" % CHUNK_K2)
    ck("GRAN_OF_ARM's two non-chunk arms are literal in the script",
       GRAN_OF_ARM["node"] == "nodewise" and GRAN_OF_ARM["n1d"] == "nodewise1d")
    ck("script writes run names fa1-<arm>-s<seed>", 'RN="fa1-${SHORT}-s${S}"' in src)
    ck("script's probe dir carries the fa1 tag", "probe_${SHORT}_fa1_s${S}" in src)
    ck("script exports PROBE=5 AND PROBE5=1", "PROBE=5,PROBE5=1" in src)
    ck("script registers fa1 in c55 BOXES before submitting",
       '"fa1" not in c55.BOXES' in src)
    ck("script passes --weight-decay-meta 0 (the bound's precondition)",
       "--weight-decay-meta 0" in src)

    print("  -- the box, really registered, and really DIFFERENT from ar1's --")
    import c55_neff_noise as c55
    ck("fa1 is registered in c55 BOXES", "fa1" in c55.BOXES)
    ck("fa1's box equals this scorer's (LO, HI)",
       c55.BOXES.get("fa1", (0, 0, ""))[:2] == (LO, HI))
    ck("ar1 is registered in c55 BOXES", "ar1" in c55.BOXES)
    ck("fa1's box is NOT ar1's (F3 is a real contrast)",
       c55.BOXES.get("fa1", (0, 0, ""))[:2] != c55.BOXES.get("ar1", (1, 1, ""))[:2])
    ck("ar1's registered box is the CLIP_REF this scorer pairs against",
       c55.BOXES.get("ar1", (0, 0, ""))[:2]
       == tuple(float(x) for x in CLIP_REF.split(":")))

    print("  -- THE IDENTITY.  The whole ceiling rests on this arithmetic --")
    ck("T = EPOCHS * STEPS_PER_EPOCH = 50,000", T_UPDATES == 50000)
    ck("beta_0 = ln(alpha0) = -6.907755", abs(BETA0 + 6.907755279) < 1e-6)
    ck("ms*T = 15.0 exactly", abs(SPAN - 15.0) < 1e-9)
    ck("the reachable floor is -21.907755", abs(REACH_LO + 21.907755279) < 1e-6)
    ck("the reachable ceiling is +8.092245", abs(REACH_HI - 8.092245) < 1e-6)
    ck("the registered floor is STRICTLY below the reachable floor", LO < REACH_LO)
    ck("the registered ceiling is STRICTLY above the reachable ceiling", HI > REACH_HI)
    ck("floor headroom is more than the batch's own horizon",
       (BETA0 - LO) / (MS * STEPS_PER_EPOCH) > EPOCHS)
    ck("ceiling headroom is more than the batch's own horizon",
       (HI - BETA0) / (MS * STEPS_PER_EPOCH) > EPOCHS)
    ck("ar1's OLD floor was NOT reachable-proof (it is above the reachable floor)",
       float(CLIP_REF.split(":")[0]) > REACH_LO)
    ck("the script derives the bound rather than asserting it (GUARD H)",
       "GUARD H" in src and "HARD BOUND" in src)
    ck("the script validates the identity against ar1's own records",
       "guard H3" in src and "identity validated" in src)
    ck("the script asserts the clamp still runs BEFORE the probe",
       "clamps before PATCH_PROBE probes" in src)
    ck("the script MEASURES len(trainloader) rather than assuming T",
       "len(trainloader)" in src and "guard 4d" in src)
    ck("the script VOIDS the ceiling if Lion_meta_update changed",
       "THE BOUND IS VOID" in src)

    print("  -- the matched-count claims --")
    ck("D_w's pair is matched to <= 1 group",
       abs(M_OF_ARM["ch"] - M_OF_ARM["node"]) <= 1)
    ck("G_w's pair is matched EXACTLY", M_OF_ARM["c23"] == M_OF_ARM["n1d"])
    ck("the two pairs sit at DIFFERENT counts", M_OF_ARM["node"] != M_OF_ARM["n1d"])
    ck("exactly 2 pairs are declared", len(PAIRS) == 2)
    ck("every pair's arms are fa1 arms",
       all(h in ARMS and l in ARMS for _, h, l, _ in PAIRS))

    print("  -- the FOUR-WAY accuracy band, fixed here and in the script --")
    ck("+0.46 -> SURVIVES", band(+0.46) == "SURVIVES")
    ck("+0.45 -> SURVIVES (the boundary is CLOSED on the SURVIVES side)",
       band(+0.45) == "SURVIVES")
    ck("+0.44 -> ATTENUATED", band(+0.44) == "ATTENUATED")
    ck("+0.15 -> ATTENUATED", band(+0.15) == "ATTENUATED")
    ck("+0.14 -> COLLAPSES", band(+0.14) == "COLLAPSES")
    ck("0.00 -> COLLAPSES", band(0.0) == "COLLAPSES")
    ck("-0.14 -> COLLAPSES", band(-0.14) == "COLLAPSES")
    ck("-0.15 -> INVERTS", band(-0.15) == "INVERTS")
    ck("-0.60 -> INVERTS", band(-0.60) == "INVERTS")
    ck("the null band is SYMMETRIC about 0 at +-0.15",
       band(+0.149) == "COLLAPSES" and band(-0.149) == "COLLAPSES")
    ck("every box-free D anchor would read SURVIVES under these bands",
       all(band(v) == "SURVIVES" for v in D_BOXFREE_ANCHORS.values()))
    ck("the SURVIVES line sits BELOW the lowest box-free anchor",
       SURVIVES_AT < min(D_BOXFREE_ANCHORS.values()))
    ck("ar1's own bound D=+0.697 would read SURVIVES", band(D_AR1_BOUND) == "SURVIVES")
    ck("ar1's G=-0.139 would read COLLAPSES", band(G_AR1_BOUND) == "COLLAPSES")
    ck("cc1's G=+0.011 would read COLLAPSES", band(G_CC1_FREE) == "COLLAPSES")
    ck("the script states the same four bands",
       all(w in src for w in ("SURVIVES", "ATTENUATED", "COLLAPSES", "INVERTS")))
    ck("the script fixes the SURVIVES line at +0.45", ">= +0.45" in src)
    ck("the script declares the negative side deliberately not subdivided",
       "deliberately NOT subdivided" in src)

    print("  -- the statistics --")
    ck("_t of identical samples is 0", _t([1., 2., 3.], [1., 2., 3.]) == 0.0)
    ck("_t is antisymmetric",
       abs(_t([2., 3., 4.], [1., 2., 3.]) + _t([1., 2., 3.], [2., 3., 4.])) < 1e-12)
    ck("_sem of n=1 is nan", math.isnan(_sem([1.0])))
    ck("_t_paired of all-zero differences is nan (no spread, no claim)",
       math.isnan(_t_paired([0.0, 0.0, 0.0])))
    ck("_t_paired of a constant offset with spread is finite and signed",
       _t_paired([0.4, 0.5, 0.6]) > 0 and _t_paired([-0.4, -0.5, -0.6]) < 0)

    print("  -- the sign convention, the thing that must not drift --")
    conv = "higher N_eff/m -> higher plateau5 = CONCORDANT"
    ck("the convention is stated in the batch script", conv in flat(src))
    ck("the convention is stated in this scorer", conv in flat(doc))
    cc1 = open(os.path.join(HERE, "c81_cc1_score.py")).read()
    a3 = open(os.path.join(HERE, "c79_ar1_score.py")).read()
    ck("cc1's C1 convention line is byte-identical to F1's", conv in flat(cc1))
    ck("ar1's A3 convention line is byte-identical to F1's", conv in flat(a3))
    ck("the convention is declared transcribed unchanged",
       "TRANSCRIBED UNCHANGED" in src.upper() and "TRANSCRIBED UNCHANGED" in doc.upper())
    ck("the resolved threshold is |t| >= 2.0", RESOLVED_T == 2.0 and "|t| >= 2.0" in src)

    print("  -- F1 is a REPLICATION of a CLOSED question, and says so --")
    ck("the script names direction C as DROPPED",
       "DIRECTION C IS DROPPED" in src.upper())
    ck("the script forbids reopening it", "may reopen" in src or "REOPEN" in src.upper())
    ck("this scorer refuses to reopen direction C under ANY outcome",
       "will not reopen direction C under ANY F1 outcome" in flat(doc))
    ck("a CONCORDANT reading is registered as a DISCREPANCY, not a re-opening",
       "DISCREPANCY WITH cc1" in src and "DISCREPANCY WITH cc1" in doc)
    ck("cc1's own verdict is quoted with both channels' t",
       "-11.14" in doc and "-23.26" in doc and "-11.14" in src and "-23.26" in src)
    ck("the UNINFORMATIVE branch is registered",
       "UNINFORMATIVE" in src and "UNINFORMATIVE" in doc)
    ck("the DISSOCIATION branch is registered",
       "DISSOCIATION" in src and "DISSOCIATION" in doc)

    print("  -- THE BOX-OCCUPANCY GATE, and that it VOIDS the batch's OWN primary --")
    ck("the box gate is scored PER SEED in the script", "SCORED PER SEED" in src)
    ck("a bind VOIDS F1 in the script", "A BIND VOIDS F1" in src.upper())
    ck("a bind VOIDS F1 in this scorer", "A BIND VOIDS F1" in doc.upper())
    ck("the scorer will not read F1 when box-bound",
       "will not read F1 if any arm is box-bound" in doc)
    ck("the box-free gate is the published 5%", BOXFREE_MAX == 0.05)
    ck("occupancy is reported for all 12 arms regardless of outcome",
       "whatever the outcome" in src and "whatever the outcome" in doc)
    ck("F0.5 declares a bind ALGEBRAICALLY IMPOSSIBLE",
       "ALGEBRAICALLY IMPOSSIBLE" in doc.upper() or "algebraically impossible" in doc)
    ck("F0.5 sends a bind to VOID-and-debug, never to a rescore",
       "do not rescore" in doc and "do not rescore" in src.lower().replace("DO NOT RESCORE", "do not rescore"))

    print("  -- INSTRUMENT-ONLY: the comparability finding, stated in advance --")
    ck("the script states the batch is INSTRUMENT-ONLY", "INSTRUMENT-ONLY" in src)
    ck("this scorer states the batch is INSTRUMENT-ONLY", "INSTRUMENT-ONLY" in doc)
    ck("the script answers 'can fa1 re-read A1/A2?' with NO",
       "CAN fa1 RE-READ ar1's A1 / A2?  **NO." in src)
    # Both files wrap these sentences across comment/docstring line breaks, so the
    # assertions compare WHITESPACE-NORMALISED text: the check is about the
    # SENTENCE, not the column it happened to wrap at (the c77 precedent -- correct
    # the SCORER's assertion, never the batch script).
    ck("this scorer answers the same question with NO",
       flat("CAN fa1 RE-READ ar1's A1/A2?  NO.") in flat(doc))
    ck("the differential bind is quoted WITH its denominator (rule 21)",
       "of its 14,420 coordinates" in flat(src) and "14,420 coordinates" in flat(doc))
    ck("D_w is declared NOT a fifth replication",
       "fifth replication" in src and "fifth replication" in doc)
    ck("the scorer refuses to pool D_w with ar1's D",
       "will not pool D_w with ar1's D" in doc)
    ck("the sign of the box effect is declared UNSURE in advance",
       "UNSURE" in src and "UNSURE" in doc)
    ck("F3 is declared mandatory BECAUSE the sign is unpredictable",
       "why F3 is mandatory" in flat(src) or "that is why F3 is mandatory" in flat(doc))
    ck("F3's null is pre-emptively forbidden from becoming 'accuracy-neutral'",
       "accuracy-neutral" in src and "accuracy-neutral" in doc)

    print("  -- the premise, ASSERTED by the script rather than quoted --")
    ck("the script re-derives ar1's bind from the probes (guard 7)",
       "GUARD 7" in src and "the premise holds" in src)
    ck("guard 7 fails loudly if ar1 is not 12/12 bound", "only %d/12" in src)
    ck("the script re-derives the box-free D anchors from the CSV (guard 2d)",
       "guard 2d" in src and "0.485" in src and "0.581" in src and "0.727" in src)
    ck("guard 2 asserts beta_clip is the ONLY axis that moves",
       "the ONLY axis that moves" in src)
    # The guard's message is assembled from two adjacent Python string literals, so
    # the sentence is broken by quote characters that no whitespace normalisation
    # removes.  Assert the distinctive fragment plus the condition it guards.
    ck("guard 2c asserts the pairing partner exists at the SAME ms",
       "box+stepsize contrast" in src and "rows are not at ms=%s" in src)
    ck("the ms/box confound this batch retires is named with its counts",
       "39/39" in src and "15/15" in src and "39/39" in doc and "15/15" in doc)
    ck("STANDING RULE 10 is named as what the confound violates",
       "STANDING RULE 10" in src and "STANDING RULE 10" in doc)

    print("  -- the limits, stated in the scorer itself --")
    ck("scorer states it predates the data entirely", "before the data could exist" in doc)
    ck("the argmax limit is stated", "will not claim any arm's argmax" in doc)
    ck("the BN-vs-size non-identifiability is carried forward",
       "coincide EXACTLY (FINDINGS 78.1)" in doc)
    ck("the layer-boundary limit is carried forward in the script",
       "Layer boundaries stay untested" in src)
    ck("the n=3, one-architecture limit is stated in the script",
       "does not establish a law" in src)
    ck("scorer refuses to write the 53.1% sentence", 'will not print "53.1%"' in doc)
    ck("F4 is declared descriptive and unable to gate",
       flat("cannot gate F1, F2 or F3") in flat_sh(src)
       and "will not let F4 gate" in doc)
    ck("plateau5 is declared PRIMARY over best_test in the script",
       "plateau5 is PRIMARY" in src)

    print("selftest: %d/%d %s" % (p, n, "PASS" if p == n else "FAIL"))
    return 0 if p == n else 1


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(REPO, "..", "probes_fa1"))
    ap.add_argument("--csv", default=os.path.join(REPO, "results", "all_runs.csv"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    dirs = sorted(glob.glob(os.path.join(a.root, "probe_*")))
    print("=" * 78)
    print("c82 -- fa1: THE FIELD READING AT A CEILING THAT CANNOT BIND.  %d probe dirs"
          % len(dirs))
    print("box = (%.1f, %+.1f)   ms=%s   %d ep   seeds %s   (ar1's box was %s)"
          % (LO, HI, MST, EPOCHS, ",".join(SEEDS), CLIP_REF))
    print("D_w node/ch at m=14,420  |  G_w n1d/c23 at m=4,851 EXACT")
    print("**INSTRUMENT-ONLY: this batch does NOT re-read ar1's A1/A2.**")
    print("=" * 78)
    if not dirs:
        print("\n0 probe dirs.  **THAT IS ALWAYS A SYNC FAULT, NEVER A FINDING**")
        print("(CORRECTIONS 110.1): a probe-reading scorer needs the FULL probe_*")
        print("dirs including probe.jsonl, not just neg_counts.*.  Nothing scored.")
        return 1

    # --- F0 -----------------------------------------------------------------
    print("\n--- F0  VALIDITY (n_records==%d, beta moved, ep==%d)" % (N_RECORDS, EPOCHS))
    ok0 = 0
    for d in dirs:
        R = records(d)
        good = len(R) == N_RECORDS and R[-1]["beta_true_min"] != R[0]["beta_true_min"]
        ok0 += good
        print("    %-26s %s  n_rec=%d" % (os.path.basename(d),
                                          "PASS" if good else "FAIL", len(R)))
    print("    F0: %d/%d" % (ok0, len(dirs)))

    # --- F0.2 ---------------------------------------------------------------
    print("\n--- F0.2  n_beta EXACT on EVERY record")
    ok2 = 0
    for d in dirs:
        arm = arm_of_dir(d)
        want = M_OF_ARM.get(arm)
        nb = sorted({r.get("n_beta") for r in records(d)})
        good = nb == [want]
        ok2 += good
        print("    %-26s %s  n_beta=%s  want %s = %s"
              % (os.path.basename(d), "PASS" if good else "FAIL", nb,
                 GRAN_OF_ARM.get(arm), want))
    print("    F0.2: %d/%d" % (ok2, len(dirs)))

    # --- F0.3 ---------------------------------------------------------------
    print("\n--- F0.3  THE INSTRUMENT FIRED (npy shape from its HEADER)")
    import numpy as np
    ok3 = 0
    for d in dirs:
        want = M_OF_ARM.get(arm_of_dir(d))
        jp, npp = os.path.join(d, "neg_counts.json"), os.path.join(d, "neg_counts.npy")
        good, shape, ntot = False, None, None
        if os.path.exists(jp) and os.path.exists(npp):
            ntot = json.load(open(jp)).get("n_tot")
            with open(npp, "rb") as fh:
                np.lib.format.read_magic(fh)
                shape = np.lib.format.read_array_header_1_0(fh)[0]
            good = (ntot == want) and (shape == (want,))
        ok3 += good
        print("    %-26s %s  n_tot=%s  npy_shape=%s"
              % (os.path.basename(d), "PASS" if good else "FAIL", ntot, shape))
    print("    F0.3: %d/%d" % (ok3, len(dirs)))

    # --- F0.4 ---------------------------------------------------------------
    print("\n--- F0.4  **THE BOX GATE, PER SEED.  A BIND VOIDS F1.**")
    occ, free, fld = {}, 0, {}
    for d in dirs:
        o = occupancy(d, LO, HI)
        occ[d] = o
        f = o["rec_lo"] < BOXFREE_MAX and o["rec_hi"] < BOXFREE_MAX
        free += f
        print("    %-26s %-8s rec_lo %.4f  rec_hi %.4f  bmin %8.3f  bmax %+8.3f"
              % (os.path.basename(d), "free" if f else "BOUND",
                 o["rec_lo"], o["rec_hi"], o["min_final"], o["max_final"]))
        nf = neff_of_dir(d)
        if nf is not None:
            fld.setdefault(arm_of_dir(d), []).append(nf)
    print("    F0.4: %d/%d box-free" % (free, len(dirs)))
    f1_void = free != len(dirs)

    # --- F0.5 ---------------------------------------------------------------
    print("\n--- F0.5  **THE IDENTITY GATE.**  beta in [%.6f, %+.6f] is FORCED by"
          % (REACH_LO, REACH_HI))
    print("    beta <- (1-ms*wd)*beta - ms*sign(.) with wd_meta=0, ms=%s, T=%d."
          % (MST, T_UPDATES))
    print("    A guard touch here is ALGEBRAICALLY IMPOSSIBLE -> the config is not")
    print("    what the header says.  If this fires: VOID, do not rescore, debug.")
    ok5 = 0
    for d in dirs:
        slack, nrec = identity_slack(d)
        o = occ[d]
        touched = o["rec_lo"] > 0 or o["rec_hi"] > 0
        good = (slack >= -1.5 * MS) and not touched
        ok5 += good
        print("    %-26s %s  worst slack %+.6f = %.2f ms steps  guard-touch %s"
              % (os.path.basename(d), "PASS" if good else "**VOID**", slack,
                 abs(slack) / MS, "YES" if touched else "no"))
    print("    F0.5: %d/%d" % (ok5, len(dirs)))
    if ok5 != len(dirs):
        print("    **THE BATCH IS VOID.**  The Lion identity forces |beta - beta_0|")
        print("    <= %.1f; a violation means wd_meta != 0, the wrong ms, the wrong" % SPAN)
        print("    step count or a resumed run.  DEBUG THE CONFIG.  Do not rescore.")

    # --- the cells ----------------------------------------------------------
    cells = {arm: arm_rows(a.csv, "fa1", arm) for arm in ARMS}
    ref = {arm: arm_rows(a.csv, REF_FAM, arm) for arm in ARMS}
    print("\n--- plateau5 per arm, from the CSV (per seed, so F3 can pair)")
    for arm in ARMS:
        v = cells[arm]
        vals = [v[s] for s in sorted(v)]
        print("    %-12s m=%-8d n=%d  %s  %s"
              % (GRAN_OF_ARM[arm], M_OF_ARM[arm], len(vals),
                 ("%.3f +-%.3f" % (statistics.mean(vals), _sem(vals)))
                 if len(vals) > 1 else "-",
                 " ".join("s%s=%.3f" % (s, v[s]) for s in sorted(v))))

    # --- F1 -----------------------------------------------------------------
    print("\n--- F1  **THE PRIMARY.  THE CONCORDANCE READING AT ms=%s.**" % MST)
    print("    convention: higher N_eff/m -> higher plateau5 = CONCORDANT")
    print("    **REPLICATION ONLY.  Direction C is CLOSED (cc1's C1 was MIXED);")
    print("    no outcome below reopens it.**")
    if f1_void:
        print("    -> **VOID**: %d/%d arms box-bound, so N_eff/m is not interpretable."
              % (len(dirs) - free, len(dirs)))
        print("       Registered in advance.  This is NOT another owed re-run: the")
        print("       question is closed and a second void would only say this box")
        print("       binds too.  F2 and F3 below are accuracy-only and stand, but")
        print("       every number they give is reported WITH its occupancy.")
    else:
        labels = []
        for gate, hi, lo, what in PAIRS:
            ah = [cells[hi][s] for s in sorted(cells[hi])]
            al = [cells[lo][s] for s in sorted(cells[lo])]
            if len(ah) < 2 or len(al) < 2 or hi not in fld or lo not in fld:
                print("    %s: accuracy or field absent on an arm -> UNINFORMATIVE" % gate)
                labels.append("UNINFORMATIVE")
                continue
            da, ta = statistics.mean(ah) - statistics.mean(al), _t(ah, al)
            df, tf = (statistics.mean(fld[hi]) - statistics.mean(fld[lo]),
                      _t(fld[hi], fld[lo]))
            ares, fres = abs(ta) >= RESOLVED_T, abs(tf) >= RESOLVED_T
            if not fres:
                lab = "UNINFORMATIVE"
            elif not ares:
                lab = "DISSOCIATION"
            elif (df > 0) == (da > 0):
                lab = "CONCORDANT"
            else:
                lab = "ANTI-CONCORDANT"
            labels.append(lab)
            print("\n    %s  %s - %s  (%s)"
                  % (gate, GRAN_OF_ARM[hi], GRAN_OF_ARM[lo], what))
            print("      dplateau5 = %+7.3f pp  (t %6.2f)  %s"
                  % (da, ta, "resolved" if ares else "UNRESOLVED"))
            print("      dN_eff/m  = %+7.4f     (t %6.2f)  %s"
                  % (df, tf, "resolved" if fres else "UNRESOLVED"))
            print("      -> **%s**" % lab)
        s = set(l for l in labels if l != "UNINFORMATIVE")
        print("\n    F1 VERDICT over %d pairs: %s" % (len(labels), ", ".join(labels)))
        if not s:
            print("    -> **UNINFORMATIVE**: the field did not resolve on either pair.")
        elif s == {"ANTI-CONCORDANT"} and len(s) == 1 and labels.count("ANTI-CONCORDANT") == 2:
            print("    -> **REPLICATES cc1's ANTI-CONCORDANT LEG** at a second stepsize")
            print("       and a non-binding box.  Direction C stays DROPPED.")
        elif s == {"CONCORDANT"} and labels.count("CONCORDANT") == 2:
            print("    -> **DISCREPANCY WITH cc1, LOGGED FOR THE RECORD.**  This does")
            print("       NOT reopen direction C.  A field whose sign depends on the")
            print("       stepsize or the box is LESS of a design variable, not more.")
        else:
            print("    -> **REPLICATES cc1's MIXED VERDICT.**  The field is not a")
            print("       sufficient statistic.  Direction C stays DROPPED.")

    # --- F2 -----------------------------------------------------------------
    print("\n--- F2  THE ACCURACY CONTRASTS **IN THIS BOX, AND ONLY IN THIS BOX.**")
    print("    registered: >= +%.2f SURVIVES | [+%.2f,+%.2f) ATTENUATED | "
          "(-%.2f,+%.2f) COLLAPSES | <= -%.2f INVERTS"
          % (SURVIVES_AT, NULL_HALF, SURVIVES_AT, NULL_HALF, NULL_HALF, NULL_HALF))
    got = {}
    for gate, hi, lo, what in PAIRS:
        ah = [cells[hi][s] for s in sorted(cells[hi])]
        al = [cells[lo][s] for s in sorted(cells[lo])]
        if len(ah) < 2 or len(al) < 2:
            print("    %s: INSUFFICIENT n" % gate)
            continue
        g = statistics.mean(ah) - statistics.mean(al)
        se = math.sqrt(_sem(ah) ** 2 + _sem(al) ** 2)
        got[gate] = g
        print("\n    %s  isolates: %s" % (gate, what))
        print("    %-12s (m=%d) %.3f +-%.3f (n=%d)"
              % (GRAN_OF_ARM[hi], M_OF_ARM[hi], statistics.mean(ah), _sem(ah), len(ah)))
        print("    %-12s (m=%d) %.3f +-%.3f (n=%d)"
              % (GRAN_OF_ARM[lo], M_OF_ARM[lo], statistics.mean(al), _sem(al), len(al)))
        print("    %s = %+.3f pp  (se %.3f, t %.2f -- DESCRIPTIVE; the gate is the "
              "threshold on the difference)" % (gate, g, se, _t(ah, al)))
        print("    -> **%s**  [at BETA_CLIP=%g:%g]" % (band(g), LO, HI))
        if gate == "D_w":
            print("    box-free anchors: %s;  ar1 (BOX-BOUND 12/12) read %+.3f"
                  % (", ".join("%s %+.3f" % kv for kv in
                               sorted(D_BOXFREE_ANCHORS.items())), D_AR1_BOUND))
            print("    **NOT a fifth replication of D.  fa1 is a different box and")
            print("    pooling across boxes is the error F3 exists to detect.**")
        else:
            print("    prior expectation, registered in advance: ar1 %+.3f, cc1 %+.3f,"
                  % (G_AR1_BOUND, G_CC1_FREE))
            print("    so COLLAPSES was expected; a resolved reading OUTSIDE the null")
            print("    band UNDERCUTS the tail interpretation of A1-A2.")

    # --- F3 -----------------------------------------------------------------
    print("\n--- F3  **THE PAIRED BOX EFFECT, PER ARM.  fa1 (%g:%g) - %s (%s).**"
          % (LO, HI, REF_FAM, CLIP_REF))
    print("    %-12s %10s %10s %10s   %s" % ("arm", "fa1", REF_FAM, "Delta", "per-seed"))
    resolved_any = False
    for arm in ARMS:
        pairs = [(s, cells[arm][s], ref[arm][s])
                 for s in sorted(set(cells[arm]) & set(ref[arm]))]
        if len(pairs) < 2:
            print("    %-12s INSUFFICIENT pairs (%d)" % (GRAN_OF_ARM[arm], len(pairs)))
            continue
        dd = [b - c for _, b, c in pairs]
        tt = _t_paired(dd)
        res = (not math.isnan(tt)) and abs(tt) >= RESOLVED_T
        resolved_any |= res
        print("    %-12s %10.3f %10.3f %+10.3f   %s  t %s  -> %s"
              % (GRAN_OF_ARM[arm],
                 statistics.mean([b for _, b, _ in pairs]),
                 statistics.mean([c for _, _, c in pairs]),
                 statistics.mean(dd),
                 " ".join("s%s %+0.3f" % (s, b - c) for s, b, c in pairs),
                 ("%+.2f" % tt) if not math.isnan(tt) else "  nan",
                 "**RESOLVED**" if res else "unresolved"))
    if resolved_any:
        print("    -> **THE BOX CHANGED THE OPTIMISER, NOT MERELY THE INSTRUMENT.**")
        print("       D_w may NOT be pooled with ar1's D, and every prose sentence")
        print("       about D must carry its box from here on.")
    else:
        print("    -> **UNRESOLVED at this test's own ~0.20-0.25 pp floor (n=3 pairs).**")
        print("       **This is NOT 'the box is accuracy-neutral'** -- declared in")
        print("       advance, because that sentence has been written off an")
        print("       underpowered null in this campaign before.")

    # --- F4 -----------------------------------------------------------------
    print("\n--- F4  THE CLIP METER.  **DESCRIPTIVE.  CANNOT GATE F1, F2 OR F3.**")
    print("    %-26s %8s %8s %10s %10s %10s %10s"
          % ("dir", "rec_lo", "rec_hi", "coord_lo", "coord_hi", "bmin", "bmax"))
    for d in dirs:
        o = occ[d]
        cl = ("%10.6f" % o["coord_lo"]) if o["coord_lo"] is not None else "        NA"
        ch = ("%10.6f" % o["coord_hi"]) if o["coord_hi"] is not None else "        NA"
        print("    %-26s %8.4f %8.4f %s %s %10.3f %+10.3f"
              % (os.path.basename(d), o["rec_lo"], o["rec_hi"], cl, ch,
                 o["min_final"], o["max_final"]))
    print("    headroom the hard bound left: floor %.3f below the reachable %.3f,"
          % (REACH_LO - LO, REACH_LO))
    print("    ceiling %.3f above the reachable %+.3f." % (HI - REACH_HI, REACH_HI))
    return 0


if __name__ == "__main__":
    sys.exit(main())
