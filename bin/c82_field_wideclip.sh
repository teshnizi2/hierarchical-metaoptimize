#!/bin/bash
# =============================================================================
# c82_field_wideclip.sh -- `fa1`, THE A3 FIELD-vs-ACCURACY RE-RUN AT A CEILING
# THAT CANNOT BIND.  Runs on ALICE ONLY (needs PATCH_CHUNKWISE and PATCH_NODEBN).
# 12 jobs: {nodewise, chunk777, nodewise1d, chunk2325} x seeds 0-2, ms=3e-4,
# 100 ep, probe ON, **BETA_CLIP=-25:9.0**.  NO NEW PATCH -- every granularity
# here already ships and is already covered by an equivalence suite.  ONE FIELD
# CHANGES FROM `ar1`: THE BOX.
#
# -----------------------------------------------------------------------------
# WHY THIS BATCH EXISTS -- AND THE HONEST DEFLATION, STATED FIRST
# -----------------------------------------------------------------------------
#   Cycle 79 registered A3 -- "does the sign-agreement field predict accuracy?" --
#   and `ar1` VOIDED it: 12/12 arms sat on the LOW guard.  Re-derived this tick
#   from `probes_ar1` (not quoted from prose): rec_lo 0.4521-0.4597 on all twelve,
#   rec_hi 0.1196 on ar1-node-s2, first pin at step 27,020-27,395 of 50,000.
#
#   **THE SCIENTIFIC QUESTION A3 ASKED IS ALREADY ANSWERED AND CLOSED.**  `cc1`
#   ran the same test at ms=1e-4, 12/12 box-free (rec_lo == rec_hi == 0.0000
#   EXACTLY, re-derived here), and C1 came back MIXED: chunk777-nodewise
#   ANTI-CONCORDANT (d_acc +0.727 t +3.63 vs d_N_eff/m -0.0237 t -11.14) and
#   chunk2325-nodewise1d DISSOCIATED (d_acc +0.011 t +0.08 vs d_N_eff/m -0.0529
#   t -23.26).  **DIRECTION C IS DROPPED** (CORRECTIONS 110.2, 110.5(1)).
#   **NOTHING fa1 RETURNS MAY REOPEN IT.**  F1 below is registered strictly as a
#   REPLICATION of a CLOSED result at a second stepsize; a CONCORDANT reading here
#   is logged as a discrepancy for the record and is NOT a re-opening.  This is
#   written down BEFORE the data exist precisely so it cannot be revised after.
#
#   SO WHAT DOES fa1 ACTUALLY BUY?  ONE THING, AND IT IS A RULE-10 REPAIR.
#   Census re-derived this tick over every 100-epoch ResNet18 probe dir on disk in
#   the box (-15, -2.3026):
#       ms=1e-4   mm1 6 + pp1 9 + bn1 9 + cc1 12 + at1(blk6) 3  = **39/39 BOX-FREE**
#       ms=3e-4   ar1 12 + at1(node) 3                          = **15/15 LO-BOUND**
#   **THE STEPSIZE AXIS AND THE BOX-BINDING AXIS ARE PERFECTLY CONFOUNDED IN THIS
#   CORPUS.**  STANDING RULE 10 says a series across any axis must hold the arm
#   fixed; the campaign's ms series does not hold the BOX fixed.  fa1 changes one
#   field and retires that confound.  Buy it for that reason or do not buy it.
#   **Do NOT buy it to rescue A3: A3 is already rescued by cc1.**
#
# -----------------------------------------------------------------------------
# CAN fa1 RE-READ ar1's A1 / A2?  **NO.  THIS BATCH IS INSTRUMENT-ONLY.**
# -----------------------------------------------------------------------------
#   Stated here, before the data, because the temptation to pool will exist after.
#   (a) THE GUARD BOUND DIFFERENTIALLY ACROSS EXACTLY THE ARMS A1 COMPARES.  Both
#       fractions below name their denominator (STANDING RULE 21) and both are
#       re-derived from `probes_ar1` this tick.  AT THE FINAL RECORD, per COORDINATE:
#       nodewise 11.25-11.74% of its 14,420 coordinates sit on the floor; chunk777
#       0.159-0.173% of its 14,421.  **A 68-71x difference in clamped mass between
#       the two arms of A1.**  Over ALL 10,000 records the same split reads 3.43% vs
#       0.040% = 85x (guard 7b prints this one).  The clamp is not a shared
#       background that cancels in the difference -- it is doing ARM-SPECIFIC work on
#       the exact contrast.  For A2 the asymmetry is mild (nodewise1d 0.557% of 4,851
#       vs chunk2325 0.39-0.43% of 4,851, ~1.3x), so A1 and A2 are NOT equally
#       contaminated and cannot be rescued by one argument.
#   (b) IT BOUND FOR THE HALF OF TRAINING THAT SETS THE PRIMARY.  First pin at
#       27,020-27,395 of 50,000 steps; the clamp is live for 45.2-46.0% of
#       training -- the whole second half, which is the half plateau5 is read from.
#   (c) IT CLAMPED THE COORDINATES THE MECHANISM CLAIM IS ABOUT.  MEASURED, from the
#       final record of every ar1 probe: in n1d, ch and c23, **15-17 of the 41
#       one-dimensional (BatchNorm + linear.bias) tensors have their group at the
#       floor** -- exact, because in those three arms every 1-D tensor is ONE group,
#       so the probe's per-tensor beta IS that group's value.  The size-1 tail whose
#       contribution A1-A2 exists to isolate is the tail the guard was holding up.
#       **For nodewise itself the attribution is UNSURE and is left that way.**  Its
#       probe carries 62 per-TENSOR values against 14,420 groups, and those means
#       cannot resolve it: only 1 of 41 one-D tensor MEANS sits at the floor while
#       1,622-1,693 coordinates do.  That gap is exactly the per-tensor-mean
#       resolution error CORRECTIONS 50 was written about, so no nodewise split is
#       quoted here in either direction.
#   (d) THE SIGN OF THE CHANGE IS NOT PREDICTABLE.  **UNSURE, genuinely.**  Freeing
#       the floor could help nodewise (its one-term singleton meta-gradient
#       estimators stop injecting noise once alpha decays away) or hurt it (the BN
#       scales freeze).  That is why F3 is a mandatory within-design control and
#       not an optional extra.
#   CONSEQUENCE, REGISTERED: **F2's D_w and G_w may NOT be appended to the
#   mm1/pp1/ar1/cc1 D series as a fifth replication.**  fa1 is a different box and
#   pooling across boxes is the exact error F3 exists to detect.  Every fa1 number
#   is quoted WITH ITS BOX, always.
#
# -----------------------------------------------------------------------------
# THE CEILING, AND WHY IT IS ALGEBRAIC RATHER THAN EXTRAPOLATED
# -----------------------------------------------------------------------------
#   HF.py:675 (read read-only over ssh this tick, file untouched) implements Lion's
#   meta update as
#       beta[i] <- (1 - ms*wd_meta)*beta[i] - ms*sign(...)
#   Every job in this family is submitted with `--weight-decay-meta 0`, so the decay
#   term VANISHES IDENTICALLY and each update moves each coordinate by exactly 0 or
#   +-ms.  Therefore, for T updates and ANY velocity profile whatsoever,
#       beta_T in [ln(alpha0) - ms*T, ln(alpha0) + ms*T]     per coordinate.
#   With alpha0=1e-3, ms=3e-4, T = 100 ep x 500 steps = 50,000:
#       beta in [-21.907755, +8.092245]     ->  **-25:9.0 CANNOT BE REACHED.**
#   A box that cannot be reached cannot clamp, and is therefore byte-identical to
#   running unboxed, while leaving headroom to 120.6 epochs at the floor and 106.1
#   at the ceiling.  GUARD H computes all of this from this script's OWN CLIP=,
#   MST=, ALPHA0= and EPOCHS= lines -- it is not a comment, it is a gate.
#
#   VALIDATED, NOT ASSUMED.  GUARD H also checks the identity against all 120,000
#   ar1 probe records: worst slack on either side is exactly -0.000300 = ONE ms
#   step, and it occurs at the record labelled step 0, because HF.py clamps
#   (PATCH_CLIP) and probes (PATCH_PROBE) in that order, so record "step 0" has
#   already taken one update.  With that one-update offset the bound holds with
#   ZERO violations and is EXACTLY TIGHT at the first update.
#
#   WHY NOT A MEASURED CEILING.  CORRECTIONS 72: a worst-seed extrapolated headroom
#   was optimistic by 2.2x because the top coordinate's velocity is non-monotone and
#   seed-dependent, which produced the rule *measure the headroom, or BUDGET the
#   box; an extrapolation may earn a GATE, never a PRESUMPTION*.  There is NO
#   box-free HI measurement at ms=3e-4 at any horizon and none at 100 epochs at any
#   ms; the only datum is a LOWER bound of >= +4.605 from ar1-node-s2 sitting on the
#   old ceiling.  The corpus already contains the price of guessing there, re-derived
#   from `probes_bd7` this tick (ms=1e-3, 80 ep = 40,000 steps, from the CSV):
#   **the +2.0 ceiling bound 2 of its 6 arms (rec_hi 0.1406 and 0.6209, both pinned
#   at exactly +2.000), while the SAME family at HI=+6.0 was free on 6/6 and reached
#   +3.436** -- 1.44 above the ceiling that had been chosen, with 2 of those 6 free
#   arms exceeding +2.0.  Margin above a provably unreachable bound is FREE -- two
#   boxes that never bind produce identical trajectories -- so this batch buys margin
#   rather than precision.
#
#   EXPLICITLY REJECTED CEILINGS, with the reason:
#     -15:-2.3026  ar1's box.  LO binds 12/12, HI 1/12.  Provably impossible to keep.
#     -30:0.0      LO fine; HI 0.0 is 8.09 BELOW the hard ceiling and is a guess.
#     -30:2.0      br6's box.  HI +2.0 is 6.09 below the hard ceiling AND is measured
#                  to bind at ms=1e-3/80 ep (2 of 6 bd7 arms at HI, 10 of 12 at LO).
#                  br6's box-free record at 40 ep is NOT transferable: 40 ep is half
#                  the span.  A ceiling free at one horizon is not evidence about
#                  another -- the free/bound verdict flips on a budget doubling.
#
# -----------------------------------------------------------------------------
# THE PRE-REGISTERED GATES.  Nothing below may be edited after the data lands.
# -----------------------------------------------------------------------------
#
#   F0    VALIDITY.  n_records == 10000; beta moved; epochs_done == requested == 100.
#   F0.2  n_beta EXACT on EVERY record: node 14420, ch 14421, n1d 4851, c23 4851.
#         Guard 4 MEASURES all four from the ALLOCATED beta on the real built
#         network before anything is submitted.
#   F0.3  THE INSTRUMENT FIRED.  neg_counts.json, n_tot == n_beta, npy shape read
#         from its HEADER == (n_tot,).  (Header, never file size -- that inference
#         produced c74's false VOID on 12/12 arms.)
#   F0.4  **THE BOX-OCCUPANCY GATE, SCORED PER SEED (STANDING RULE 6/8).**  The
#         published rec_-based 5% gate at BOTH guards, PRIMARY and UNCHANGED.
#         **A BIND VOIDS F1, THIS BATCH'S OWN PRIMARY TEST** -- exactly the rule
#         ar1 wrote in advance and then had fire on itself.  F2 and F3 are
#         accuracy-only and stand, but every one of their numbers is then reported
#         with its measured occupancy beside it (rule 5).  Box occupancy is printed
#         for all 12 arms whatever the outcome.
#   F0.5  **THE IDENTITY GATE.**  On EVERY record, beta_true_min > -25 + 1e-6 and
#         beta_true_max < 9.0 - 1e-6, and |beta - ln(alpha0)| <= ms*T + one ms step.
#         **This is a PREDICTION WITH AN ALGEBRAIC PROOF BEHIND IT, not a hope.**
#         The Lion identity forces |beta - beta_0| <= 15.0, so a single record at
#         either guard means the identity is violated and THE CONFIG IS NOT WHAT THE
#         HEADER SAYS (wd_meta != 0, wrong ms, wrong step count, a resumed run).
#         If F0.5 fires the batch is **VOID -- do not rescore, debug the config.**
#
#   F1    **THE PRIMARY.  THE CONCORDANCE READING, AT ms=3e-4 UNDER A BOX THAT
#         CANNOT BIND.  CONVENTION AND BANDS FIXED HERE, BEFORE ANY fa1 RUN EXISTS.**
#         For each matched-count pair (ch - node, c23 - n1d):
#           d_acc = dplateau5, d_fld = dN_eff/m, each with a Welch t at n=3.
#           A channel is RESOLVED at |t| >= 2.0.
#         **CONVENTION, TRANSCRIBED UNCHANGED FROM `analysis/c81_cc1_score.py`'s C1
#         (itself unchanged from A3): higher N_eff/m -> higher plateau5 =
#         CONCORDANT.**  That is the direction the noise-averaging literature
#         implies (more effective independence = more information per meta-step).
#         Registered readings over the two pairs:
#           both pairs resolved on BOTH channels, both ANTI-CONCORDANT
#              -> **REPLICATES cc1's ANTI-CONCORDANT LEG AT A SECOND STEPSIZE AND A
#                 NON-BINDING BOX.**  Direction C stays DROPPED; the anti-prediction
#                 is strengthened, not re-opened.
#           MIXED (any combination of CONCORDANT / ANTI-CONCORDANT / DISSOCIATION)
#              -> **REPLICATES cc1's OWN MIXED VERDICT.**  Direction C stays DROPPED.
#           both pairs resolved on BOTH channels, both CONCORDANT
#              -> **DISCREPANCY WITH cc1, LOGGED FOR THE RECORD.**  This does NOT
#                 reopen direction C.  It says the field's sign is stepsize- or
#                 box-dependent, which makes it LESS of a design variable, not more.
#           a pair RESOLVED on field, UNRESOLVED on accuracy -> DISSOCIATION.
#           a pair UNRESOLVED on FIELD -> UNINFORMATIVE, reported, NOT folded in.
#         **F1 IS VOID IF F0.4 FAILS ON ANY ARM** -- a box-bound arm's N_eff/m is
#         not interpretable (rule 5).  A void here is NOT another owed re-run: the
#         question is closed, and a second void would only say this box binds too.
#
#   F2    THE ACCURACY CONTRASTS **IN THIS BOX, AND ONLY IN THIS BOX.**
#           D_w = plateau5(chunk777)  - plateau5(nodewise)     m 14,421 vs 14,420
#           G_w = plateau5(chunk2325) - plateau5(nodewise1d)   m 4,851 EXACT
#         FOUR BANDS, FIXED NOW, IDENTICAL FOR D_w AND G_w, calibrated against the
#         three BOX-FREE readings of D the campaign owns (mm1 +0.485, pp1 +0.581,
#         cc1 +0.727 -- all re-derived from the CSV this tick) so that SURVIVES
#         means "indistinguishable from the box-free evidence":
#           >= +0.45           -> **SURVIVES**.  Not a guard artefact; the ms=3e-4
#                                 cell joins the series without a box qualifier.
#           [+0.15, +0.45)     -> **ATTENUATED**.  Box-dependent; every quotation of
#                                 ar1's +0.697 acquires "at BETA_CLIP=-15:-2.3026",
#                                 permanently.
#           (-0.15, +0.15)     -> **COLLAPSES**.  The ms=3e-4 cell is a guard
#                                 artefact and is dropped from the D series, leaving
#                                 three box-free cells.
#           <= -0.15           -> **INVERTS**.  The strongest available refutation;
#                                 reported as such, never softened to "collapses".
#         The negative side is deliberately NOT subdivided: an inversion of any
#         resolvable size is the strongest outcome available and there is nothing
#         to gain by grading it.  PRIOR EXPECTATION ON G_w, stated so it cannot be
#         claimed afterwards: ar1 read -0.139 and cc1 read +0.011, so G_w is
#         expected to COLLAPSE.  A G_w outside that band with |t| >= 2 is the
#         informative outcome -- it would say the guard was doing arm-specific work
#         on the tail-FREE contrast too, which UNDERCUTS the tail interpretation of
#         A1-A2 rather than supporting it.
#
#   F3    **THE PAIRED BOX EFFECT, PER ARM.  THE CONTROL THAT MAKES F2 READABLE.**
#         Delta_arm = plateau5(fa1 arm, seed s) - plateau5(ar1 arm, seed s), paired
#         over s in {0,1,2} -- fa1 deliberately reuses ar1's OWN seeds, so ar1 is
#         the narrow-box half of a paired box-vs-box comparison at ZERO extra
#         compute.  RESOLVED at |t| >= 2.0 on the paired differences.
#           |Delta| resolved on ANY arm -> **THE BOX CHANGED THE OPTIMISER, NOT
#              MERELY THE INSTRUMENT.**  D_w may not be pooled with ar1's D under
#              any circumstances, and every prose sentence about D must thereafter
#              carry its box.  Predicted largest on nodewise (12% clamped mass) and
#              smallest on chunk777 (0.16%) -- stated as an expectation, not a gate.
#           no arm resolved -> **UNRESOLVED at this test's own ~0.20-0.25 pp floor.**
#              **This may NOT be written as "the box is accuracy-neutral."**
#              Declared now, because the campaign has previously written exactly
#              that sentence off an underpowered null.  n=3 pairs does not resolve
#              0.12 pp seed-noise-scale effects.
#
#   F4    THE CLIP METER.  **DESCRIPTIVE.**  rec_lo / rec_hi / coord_lo / coord_hi
#         and beta_true_min/max per arm, printed AFTER F1-F3.  Its only job is to
#         document how much headroom the hard bound actually left.  It cannot gate
#         F1, F2 or F3 beyond the F0.4 void it already feeds.
#
# WHAT THIS BATCH EXPLICITLY DOES NOT CLAIM
#   * It does NOT reopen direction C.  That question was decided by cc1's own
#     five-way pre-registered test and is CLOSED.
#   * It does NOT re-read ar1's A1 or A2, and its D_w is NOT a fifth replication.
#   * It does NOT measure any arm's argmax.  Two stepsizes are two points.
#   * It does NOT separate "the group-size distribution" from "the parameter role"
#     on the 1-D tensors -- on ResNet18 those coincide EXACTLY (FINDINGS 78.1).
#   * Every arm is a WITHIN-TENSOR partition.  Layer boundaries stay untested.
#   * F1 is two pairs at n=3 on one architecture and one dataset.  It registers a
#     replication; it does not establish a law.
#
# STRUCTURAL CHECKS BEFORE USING ANY NUMBER (Rule 4)
#   1. python3 tests/test_nodebn.py           (CPU, N0 asserts determinism first)
#   2. python3 tests/test_chunkwise.py        (CPU)
#   3. python3 analysis/c55_neff_noise.py --selftest
#   4. python3 analysis/c82_fa1_score.py --selftest   (registered BEFORE the data)
#   5. `fa1` registered in c55_neff_noise.BOXES BEFORE scoring, from THIS CLIP=.
#   6. plateau5 is PRIMARY.  best_test inflates ~0.27-0.42 pp.
#
# USAGE
#   bash c82_field_wideclip.sh            # dry run -- emits, submits nothing
#   bash c82_field_wideclip.sh --submit   # submits, ONLY if EVERY guard passes
#
# DRY RUN OFF THE CLUSTER.  Every guard below is MANDATORY for --submit: the first
# failure aborts and nothing is submitted.  In DRY RUN a guard failure is counted,
# printed loudly, and execution continues so the EMITTER itself can be validated on
# a machine that has no /data1 -- the script then exits NON-ZERO with a banner.  A
# dry run that reports failed guards is NOT a green light; it means exactly that the
# emitter is syntactically sound and the guards have not been satisfied yet.
# =============================================================================
set -u

SUBMIT=0
[ "${1:-}" = "--submit" ] && SUBMIT=1

GUARD_FAILS=0
guard_fail() {
  GUARD_FAILS=$((GUARD_FAILS + 1))
  echo "!!! GUARD FAIL: $1"
  if [ "$SUBMIT" = "1" ]; then
    echo "!!! SUBMIT ABORTED -- nothing was submitted."
    exit 1
  fi
  echo "    (dry run: continuing so the emitter can be validated off-cluster."
  echo "     THIS BATCH MUST NOT BE SUBMITTED UNTIL THIS GUARD PASSES ON ALICE.)"
}

USER_NAME="${USER:-$(whoami)}"
WS=/data1/salehkaleybars/metaopt
RUNNER=$WS/jobs/run_cifar.sh
SAVE=$WS/runs/fa1
WALL=04:00:00
PARTS=gpu-short,gpu-l4-24g,gpu-2080ti-11g,gpu-mig-40g,gpu-a100-80g

NJOBS=12
CLIP=-25:9.0                   # **THE ONE FIELD THAT CHANGES FROM ar1.**  Provably
                               # unreachable: see GUARD H, which derives it.
CLIP_REF=-15:-2.3026           # ar1's box -- LO-bound on 12/12, HI on 1/12
MST=3e-4                       # ar1's stepsize, UNCHANGED, so the box is the only axis
ALPHA0=1e-3                    # beta_0 = ln(alpha0) = -6.907755
EPOCHS=100
BATCH=100
STEPS_PER_EPOCH=500            # 50,000 CIFAR-10 train images / batch 100; GUARD 4 MEASURES it
WRITE_EVERY=500
CHUNK_K=777                    # m(777)  = 14,421 = m(nodewise) + 1
CHUNK_K2=2325                  # m(2325) =  4,851 = m(nodewise1d) EXACTLY
M_NODE=14420
M_CHUNK=14421
M_N1D=4851
M_CHUNK2=4851
SEEDS="0 1 2"                  # DELIBERATELY ar1's OWN seeds -- F3 is paired
REF_FAM=ar1                    # the narrow-box half of F3's pairing

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CSVP="$REPO/results/all_runs.csv"

echo "=============================================================="
echo "  fa1 -- THE A3 FIELD READING AT A CEILING THAT CANNOT BIND"
echo "    BETA_CLIP=$CLIP  (ar1's was $CLIP_REF, LO-bound 12/12)"
echo "    ms=$MST, alpha0=$ALPHA0, ${EPOCHS}ep, batch $BATCH, seeds $SEEDS = $NJOBS jobs"
echo "    node(m=$M_NODE)/ch${CHUNK_K}(m=$M_CHUNK) and n1d(m=$M_N1D)/c${CHUNK_K2}(m=$M_CHUNK2)"
echo "    F1 (PRIMARY): concordance, convention FIXED HERE --"
echo "       higher N_eff/m -> higher plateau5 = CONCORDANT"
echo "       REPLICATION ONLY.  Direction C is CLOSED (cc1 C1 MIXED); no outcome reopens it."
echo "       **F1 IS VOID IF ANY ARM BINDS AT EITHER GUARD (F0.4).**"
echo "    F2: D_w / G_w IN THIS BOX ONLY -- NOT a fifth replication of D"
echo "    F3: paired box effect vs $REF_FAM at the SAME seeds"
echo "    **INSTRUMENT-ONLY: this batch CANNOT re-read ar1's A1/A2.**"
echo "=============================================================="

# --- GUARD 0 ---------------------------------------------------------------
[ -f "$CSVP" ] || guard_fail "guard 0: no CSV at $CSVP"
[ -f "$RUNNER" ] || guard_fail "guard 0: no runner at $RUNNER"
[ -f "$CSVP" ] && echo "guard 0: CSV present ($(wc -l < "$CSVP") CSV lines)"

# --- GUARD 1 -- the probe patch is present AND ENABLED (STANDING RULE 19) ---
python3 - "$WS" "$REPO" "$0" <<'PYEOF' || guard_fail "guard 1a-c: probe wiring"
import os, re, sys
ws, repo, me = sys.argv[1], sys.argv[2], sys.argv[3]
hf = os.path.join(ws, "MetaOptimize", "codes", "Supervised_tasks", "MetaOptimize",
                  "cifar10", "Optimizers", "HF.py")
if not os.path.exists(hf):
    sys.exit("GUARD FAIL: %s absent" % hf)
src = open(hf).read()
if not re.search(r"os\.environ\.get\(\s*['\"]PROBE5['\"].*?\)\s*==\s*['\"]1['\"]", src):
    sys.exit("GUARD FAIL: HF.py's PROBE5 gate is not the =='1' form this script exports for")
print("guard 1a: HF.py gates the sign-count writer on PROBE5 == '1'")
mine = [l for l in open(me).read().splitlines()
        if l.strip().startswith('--export="ALL,') and "PROBE_DIR" in l]
if len(mine) != 1:
    sys.exit("GUARD FAIL: expected exactly 1 --export line with PROBE_DIR, found %d" % len(mine))
for need in ("PROBE=5", "PROBE5=1", "PROBE5_WRITE_EVERY="):
    if need not in mine[0]:
        sys.exit("GUARD FAIL: export line missing %r -- that is bf8's bug" % need)
print("guard 1b: this script exports PROBE=5 AND PROBE5=1 AND PROBE5_WRITE_EVERY")
tw0 = os.path.join(repo, "bin", "c74_tuned_weightwise_probe.sh")
ref = [l for l in open(tw0).read().splitlines()
       if l.strip().startswith('--export="ALL,') and "PROBE_DIR" in l]
def keys(l):
    return sorted(k.split("=")[0] for k in re.search(r'"ALL,([^"]+)"', l).group(1).split(","))
if keys(mine[0]) != keys(ref[0]):
    sys.exit("GUARD FAIL: export KEYS differ from tw0's CONFIRMED-FIRING line")
print("guard 1c: export keys identical to tw0's CONFIRMED-FIRING line")
PYEOF

# --- GUARD 1d -- THE TWO PATCHES THIS BATCH NEEDS, AND nodewise1d ISOLATION -
python3 - "$WS" <<'PYEOF' || guard_fail "guard 1d: PATCH_CHUNKWISE / PATCH_NODEBN"
import os, sys
hf = os.path.join(sys.argv[1], "MetaOptimize", "codes", "Supervised_tasks",
                  "MetaOptimize", "cifar10", "Optimizers", "HF.py")
src = open(hf).read()
for marker, needs in (("PATCH_CHUNKWISE", ("chunkwise", "chunk_size")),
                      ("PATCH_NODEBN", ("nodewise1d", "n1d_groups", "n1d_gsize",
                                        "n1d_shape", "n1d_numel"))):
    if marker not in src:
        sys.exit("GUARD FAIL: %s is NOT applied to %s" % (marker, hf))
    for need in needs:
        if need not in src:
            sys.exit("GUARD FAIL: %s present but %r missing -- partial patch"
                     % (marker, need))
if src.count("self.stepsize_type == 'nodewise1d'") != 3:
    sys.exit("GUARD FAIL: expected 3 nodewise1d branches, found %d"
             % src.count("self.stepsize_type == 'nodewise1d'"))
if "'weightwise', 'nodewise1d'" not in src:
    sys.exit("GUARD FAIL: nodewise1d is not in the exact-match dispatch list")
# A SUBSTRING dispatch on 'nodewise' would silently route nodewise1d into nodewise.
if "'nodewise' in self.stepsize_type" in src or '"nodewise" in self.stepsize_type' in src:
    sys.exit("GUARD FAIL: a SUBSTRING dispatch on nodewise exists -- nodewise1d would leak")
if src.count("self.stepsize_type == 'nodewise'") != 3:
    sys.exit("GUARD FAIL: the plain nodewise branches were disturbed")
print("guard 1d: PATCH_CHUNKWISE and PATCH_NODEBN present, nodewise1d reachable, "
      "plain nodewise undisturbed")
PYEOF

# --- GUARD 1e -- THE EQUIVALENCE SUITES PASS ON THIS TREE, ON CPU ----------
# STANDING RULE 20: an equivalence suite must run on a deterministic device and its
# FIRST assertion must be that a configuration equals ITSELF.
(
  module load Python/3.10.4-GCCcore-11.3.0 >/dev/null 2>&1
  # shellcheck disable=SC1091
  source "$WS/envs/mo/bin/activate"
  cd "$REPO" || exit 1
  for T in tests/test_nodebn.py tests/test_chunkwise.py; do
    NODEBN_TEST_DEVICE=cpu python3 "$T" > /tmp/fa1_t.$$ 2>&1
    if [ $? -ne 0 ]; then
      echo "  $T did NOT pass on this tree:"; tail -25 /tmp/fa1_t.$$
      rm -f /tmp/fa1_t.$$; exit 1
    fi
    echo "guard 1e: $T $(grep -c PASS /tmp/fa1_t.$$) PASS, 0 FAIL, on CPU, LIVE tree"
    rm -f /tmp/fa1_t.$$
  done
) || guard_fail "guard 1e: equivalence suites on the live tree"

# --- GUARD H -- **THE CEILING.  DERIVED HERE, NOT ASSERTED.** ---------------
# Three parts: (H1) the Lion update is still the identity this box is budgeted
# from; (H2) the box lies strictly outside [beta0 - ms*T, beta0 + ms*T], computed
# from THIS SCRIPT'S OWN constants; (H3) the identity is VALIDATED against every
# ar1 probe record on disk, with the clamp-then-probe one-update offset.
python3 - "$WS" "$0" "$CLIP" "$MST" "$ALPHA0" "$EPOCHS" "$STEPS_PER_EPOCH" \
  <<'PYEOF' || guard_fail "guard H: the ceiling derivation"
import glob, json, math, os, sys
ws, me, clip, mst, alpha0, epochs, spe = sys.argv[1:8]
ms, a0, ep, spe = float(mst), float(alpha0), int(epochs), int(spe)
lo, hi = (float(x) for x in clip.split(":"))

# --- H1: the Lion meta update is still the form the bound is derived from ---
hf = os.path.join(ws, "MetaOptimize", "codes", "Supervised_tasks", "MetaOptimize",
                  "cifar10", "Optimizers", "HF.py")
if not os.path.exists(hf):
    sys.exit("GUARD FAIL: %s absent -- the ceiling cannot be validated" % hf)
src = open(hf).read()
DECAY = ("(1-self.args_meta['meta_stepsize']*self.args_meta['weight_decay'])"
         "*self.beta[i]")
STEP = "- self.args_meta['meta_stepsize'] * torch.sign("
if src.count("def Lion_meta_update") != 1:
    sys.exit("GUARD FAIL: expected exactly 1 Lion_meta_update, found %d"
             % src.count("def Lion_meta_update"))
body = src.split("def Lion_meta_update", 1)[1].split("\n    def ", 1)[0]
if DECAY not in body or STEP not in body:
    sys.exit("GUARD FAIL: HF.py's Lion_meta_update is no longer "
             "beta <- (1-ms*wd)*beta - ms*sign(.).  THE BOUND IS VOID; "
             "re-derive the ceiling from scratch before submitting.")
print("guard H1: HF.py Lion_meta_update is beta <- (1-ms*wd)*beta - ms*sign(.)")
# the clamp must still run BEFORE the probe, or H3's one-update offset is wrong
i_clamp = src.find("clamp(self._beta_lo, self._beta_hi)")
i_probe = src.find("self._probe(HtT_gradft)")
if i_clamp < 0 or i_probe < 0 or i_clamp > i_probe:
    sys.exit("GUARD FAIL: PATCH_CLIP no longer clamps BEFORE PATCH_PROBE probes")
print("guard H1b: PATCH_CLIP clamps before PATCH_PROBE probes (the one-update offset)")

# --- H1c: wd_meta == 0 on THIS script's own submit line ---------------------
mine = open(me).read()
for need in ("--weight-decay-meta 0",
             "--meta-stepsize \"$MST\"", "--alpha0 \"$ALPHA0\"",
             "--num-epochs \"$EPOCHS\"", "--batch-size \"$BATCH\""):
    if need not in mine:
        sys.exit("GUARD FAIL: this script's submit line does not carry %r -- the "
                 "bound's precondition is unverified" % need)
print("guard H1c: the submit line carries --weight-decay-meta 0 and passes ms, "
      "alpha0, epochs and batch size from the constants the bound uses")

# --- H2: the box is provably unreachable -----------------------------------
T = ep * spe
beta0 = math.log(a0)
span = ms * T
b_lo, b_hi = beta0 - span, beta0 + span
print("guard H2: beta_0 = ln(%g) = %.6f;  T = %d ep x %d = %d updates;  ms*T = %.4f"
      % (a0, beta0, ep, spe, T, span))
print("guard H2: HARD BOUND  beta in [%.6f, %+.6f]   BOX (%.4f, %+.4f)"
      % (b_lo, b_hi, lo, hi))
if lo > b_lo:
    sys.exit("GUARD FAIL: floor %.4f is ABOVE the reachable minimum %.6f -- it WILL "
             "bind, exactly as -15 did at this ms" % (lo, b_lo))
if hi < b_hi:
    sys.exit("GUARD FAIL: ceiling %+.4f is BELOW the reachable maximum %+.6f -- it "
             "CAN bind, and there is no free HI measurement at this ms to argue "
             "otherwise" % (hi, b_hi))
ep_lo = (beta0 - lo) / (ms * spe)
ep_hi = (hi - beta0) / (ms * spe)
print("guard H2: headroom  LO %.1f ep,  HI %.1f ep  (the batch runs %d ep) -- the "
      "box CANNOT be reached, so it cannot clamp" % (ep_lo, ep_hi, ep))
if ep_lo < ep * 1.05 or ep_hi < ep * 1.05:
    sys.exit("GUARD FAIL: less than 5%% budget slack on a guard -- widen the box, "
             "margin above an unreachable bound is free")

# --- H3: VALIDATE the identity against every ar1 record on disk ------------
# The bound is an identity, but an identity about code that must still be running.
# ar1 is the same optimiser, the same ms, the same alpha0 and the same horizon.
ar1 = sorted(glob.glob(os.path.join(ws, "runs", "ar1", "probe_*")))
if not ar1:
    ar1 = sorted(glob.glob(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(me))), "..", "probes_ar1", "probe_*")))
if len(ar1) < 12:
    sys.exit("GUARD FAIL: found %d ar1 probe dirs, expected 12 -- the identity "
             "cannot be validated against real records" % len(ar1))
worst, nrec, nviol = 0.0, 0, 0
for d in ar1:
    with open(os.path.join(d, "probe.jsonl")) as fh:
        for line in fh:
            r = json.loads(line)
            st = int(r.get("step", 0))
            nrec += 1
            s = min(r["beta_true_min"] - (beta0 - ms * st),
                    (beta0 + ms * st) - r["beta_true_max"])
            worst = min(worst, s)
            if s < -1.5 * ms:            # more than the ONE documented ms step
                nviol += 1
if nviol:
    sys.exit("GUARD FAIL: %d of %d ar1 records violate the Lion bound by more than "
             "one ms step -- the identity does NOT describe the live code and the "
             "ceiling is VOID" % (nviol, nrec))
print("guard H3: identity validated on %d ar1 records across %d arms; worst slack "
      "%+.6f = %.2f ms steps (the documented clamp-then-probe offset), 0 violations"
      % (nrec, len(ar1), worst, abs(worst) / ms))
PYEOF

# --- GUARD 2 -- the axis signature, re-derived FROM THE CSV -----------------
# **beta_clip is the ONE axis that deliberately differs.**  Guard 2 asserts every
# OTHER axis matches the ladder reference AND that beta_clip really has moved --
# a fa1 that accidentally reran ar1's box would be 12 wasted jobs.
python3 - "$CSVP" "$CLIP" "$CLIP_REF" "$EPOCHS" "$MST" "$ALPHA0" "$BATCH" "$REF_FAM" \
  <<'PYEOF' || guard_fail "guard 2: axis signature / CSV premises"
import csv, sys, math, statistics
csvp, clip, clip_ref, epochs, mst, alpha0, batch, ref_fam = sys.argv[1:9]
rd = list(csv.DictReader(open(csvp)))
ref = [r for r in rd if r['run'].startswith('rs-lay-1e4')]
if not ref:
    sys.exit("GUARD FAIL: no rs-lay-1e4 reference row")
sig = ref[0]
mine = {'network': 'ResNet18', 'dataset': 'CIFAR10', 'batch_size': batch,
        'base': 'SGDm', 'meta': 'Lion', 'alpha0': alpha0, 'gamma': '1',
        'augment': '1', 'epochs_done': epochs}
bad = [(a, mine[a], sig[a]) for a in mine if mine[a] != sig[a]]
if bad:
    for a, m, s in bad:
        print("  axis %s: this batch %r vs reference %r" % (a, m, s))
    sys.exit("GUARD FAIL: fa1 does not match the ladder's axis signature")
print("guard 2: every axis EXCEPT beta_clip matches the rs-lay-1e4 signature "
      "read FROM THE CSV")
if clip == clip_ref:
    sys.exit("GUARD FAIL: CLIP equals ar1's box -- this batch changes NOTHING")
if sig['beta_clip'] != clip_ref:
    sys.exit("GUARD FAIL: the reference row's box is %r, not ar1's %r -- the one "
             "axis this batch moves is not the axis it thinks it is"
             % (sig['beta_clip'], clip_ref))
print("guard 2b: beta_clip moves %s -> %s, and it is the ONLY axis that moves"
      % (clip_ref, clip))

# guard 2c: the pairing partner must exist, at the same ms, in the OLD box.
def cell(prefix):
    return sorted(float(r['plateau5']) for r in rd
                  if r['run'].startswith(prefix) and r.get('plateau5', '').strip()
                  and r['epochs_done'] == epochs)
seeds_seen = sorted(r['seed'] for r in rd if r['run'].startswith(ref_fam + '-node-s'))
for arm in ('node', 'ch', 'n1d', 'c23'):
    v = cell('%s-%s-s' % (ref_fam, arm))
    if len(v) != 3:
        sys.exit("GUARD FAIL: %s-%s has %d scored runs, not the 3 F3 pairs against"
                 % (ref_fam, arm, len(v)))
rows = [r for r in rd if r['run'].startswith(ref_fam + '-')]
if any(r['beta_clip'] != clip_ref for r in rows):
    sys.exit("GUARD FAIL: some %s rows are not in the %s box -- F3's pairing is not "
             "a clean box contrast" % (ref_fam, clip_ref))
if any(r['meta_stepsize'] != mst for r in rows):
    sys.exit("GUARD FAIL: some %s rows are not at ms=%s -- F3 would not be a box "
             "contrast, it would be a box+stepsize contrast" % (ref_fam, mst))
print("guard 2c: %s has 4 arms x 3 seeds at ms=%s in box %s -- F3 has its paired "
      "partner and the pairing moves ONE field" % (ref_fam, mst, clip_ref))

# guard 2d: the three BOX-FREE readings of D that F2's bands are calibrated on,
# re-derived from the CSV rather than quoted.
for fam, want in (("mm1", 0.485), ("pp1", 0.581), ("cc1", 0.727)):
    a, b = cell('%s-ch-s' % fam), cell('%s-node-s' % fam)
    if len(a) < 3 or len(b) < 3:
        sys.exit("GUARD FAIL: %s's D cell is thin (%d vs %d)" % (fam, len(a), len(b)))
    d = statistics.mean(a) - statistics.mean(b)
    if abs(d - want) > 0.01:
        sys.exit("GUARD FAIL: %s's D re-reads %+.3f, not the %+.3f F2's bands were "
                 "calibrated on.  The CSV moved; re-derive the bands." % (fam, d, want))
    print("guard 2d: %s D = %+.3f (box-free anchor for F2's +0.45 SURVIVES line)"
          % (fam, d))

# guard 2e: no name collision.
clash = [r['run'] for r in rd if r['run'].startswith('fa1-')]
if clash:
    sys.exit("GUARD FAIL: %d fa1-* runs already in the CSV: %s"
             % (len(clash), clash[:5]))
print("guard 2e: no fa1-* run name already exists in the CSV")
PYEOF

# --- GUARD 3 -- the box is registered BEFORE any job runs -------------------
python3 - "$REPO" "$CLIP" "$CLIP_REF" <<'PYEOF' || guard_fail "guard 3: box registration"
import sys, os
repo, clip, clip_ref = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(repo, "analysis"))
import c55_neff_noise as c55
if "fa1" not in c55.BOXES:
    sys.exit("GUARD FAIL: `fa1` is not registered in c55_neff_noise.BOXES.  Register "
             "it from THIS script's CLIP= line BEFORE submitting or the root is skipped.")
lo, hi, prov = c55.BOXES["fa1"]
want = tuple(float(x) for x in clip.split(":"))
if (lo, hi) != want:
    sys.exit("GUARD FAIL: c55 registers fa1 as %s but CLIP= is %s" % ((lo, hi), want))
ref = c55.BOXES.get("ar1", (None, None, None))[:2]
if (lo, hi) == ref:
    sys.exit("GUARD FAIL: fa1's box equals ar1's -- F3 would be a null contrast")
if ref != tuple(float(x) for x in clip_ref.split(":")):
    sys.exit("GUARD FAIL: c55 registers ar1 as %s, not the %s this script pairs "
             "against" % (ref, clip_ref))
print("guard 3: fa1 registered as (%.1f, %+.1f) from %s; ar1 is (%.1f, %.4f) -- "
      "F3's two boxes are DIFFERENT and both are registered" % (lo, hi, prov,
                                                                ref[0], ref[1]))
PYEOF

# --- GUARD 4 -- ALL FOUR m FROM THE ALLOCATED BETA, AND len(trainloader) ---
# The m block is lifted VERBATIM from bin/c79_argmax_robustness.sh (gate names
# A1/A2 -> F2's D_w/G_w); it is the proven block and is not re-derived.  The
# trainloader assertion is NEW and is load-bearing: T = EPOCHS * len(trainloader)
# is the T the ceiling was budgeted from, so it is MEASURED, never assumed.
(
  module load Python/3.10.4-GCCcore-11.3.0 >/dev/null 2>&1
  # shellcheck disable=SC1091
  source "$WS/envs/mo/bin/activate"
  cd "$WS/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10" || exit 1
  python - "$CHUNK_K" "$CHUNK_K2" "$M_NODE" "$M_CHUNK" "$M_N1D" "$M_CHUNK2" "$MST" \
           "$BATCH" "$STEPS_PER_EPOCH" <<'PYEOF' || exit 1
import sys, torch
sys.path.insert(0, ".")
from build_network import build_network
from Optimizers.HF import HF
K, K2, want_node, want_chunk, want_n1d, want_chunk2 = (int(x) for x in sys.argv[1:7])
MST = float(sys.argv[7])
BATCH, SPE = int(sys.argv[8]), int(sys.argv[9])

BASE = {"alg": "SGDm", "weight_decay": 0.1, "momentum_param": 0.99}
META = {"alg": "Lion", "meta_stepsize": MST, "momentum_param": 0.99,
        "Lion_beta2": 0.9, "weight_decay": 0}

class NullWriter:
    def add_scalar(self, *a, **k):
        pass

def build(gran):
    torch.manual_seed(0)
    net = build_network("ResNet18", "cpu")
    return HF(net, stepsize_groups=gran, alpha0=1e-3, args_base=dict(BASE),
              args_meta=dict(META), gamma=1, writer=NullWriter())

def m_of(opt):
    return int(sum(int(b.numel()) for b in opt.beta))

net = build_network("ResNet18", "cpu")
shapes = [tuple(p.shape) for p in net.parameters()]

got = {}
for name, gran, want in (("nodewise", "nodewise", want_node),
                         ("chunk%d" % K, "chunk%d" % K, want_chunk),
                         ("nodewise1d", "nodewise1d", want_n1d),
                         ("chunk%d" % K2, "chunk%d" % K2, want_chunk2)):
    m = m_of(build(gran))
    got[name] = m
    print("guard 4: %-12s ALLOCATED beta m=%-8d (registered %d)" % (name, m, want))
    if m != want:
        sys.exit("GUARD FAIL: m(%s) is %d, not the %d registered" % (name, m, want))

d1 = abs(got["chunk%d" % K] - got["nodewise"])
d2 = abs(got["chunk%d" % K2] - got["nodewise1d"])
if d1 > 1:
    sys.exit("GUARD FAIL: D_w's arms are %d groups apart, not <= 1" % d1)
if d2 != 0:
    sys.exit("GUARD FAIL: G_w's arms are %d groups apart, not 0" % d2)
print("guard 4b: D_w's pair is %d group apart (m=%d vs %d); G_w's pair is EXACT at m=%d"
      % (d1, got["chunk%d" % K], got["nodewise"], got["nodewise1d"]))

o_n1d = build("nodewise1d")
want_groups = [1 if len(s) == 1 else s[0] for s in shapes]
if list(o_n1d.n1d_groups) != want_groups:
    sys.exit("GUARD FAIL: nodewise1d group counts are not (1 per 1-D tensor, shape[0] else)")
n_deg = sum(s[0] for s in shapes if len(s) == 1)
if n_deg != 9610:
    sys.exit("GUARD FAIL: nodewise has %d size-1 groups, not the 9,610 FINDINGS 77.6 "
             "measured -- the network changed under the finding" % n_deg)
print("guard 4c: nodewise1d isolates exactly the 1-D tensors; the size-1 tail is "
      "still %d groups, as FINDINGS 77.6 measured" % n_deg)

# --- guard 4d: T, MEASURED.  The ceiling is budgeted from ms*T. -------------
from load_data import load_data
trainloader, _ = load_data("CIFAR10", BATCH, 0)
n_steps = len(trainloader)
print("guard 4d: len(trainloader) = %d at batch %d (registered %d)"
      % (n_steps, BATCH, SPE))
if n_steps != SPE:
    sys.exit("GUARD FAIL: len(trainloader) is %d, not the %d the ceiling was "
             "budgeted from.  ms*T is wrong and BETA_CLIP MUST BE RE-DERIVED."
             % (n_steps, SPE))
PYEOF
) || guard_fail "guard 4: allocated beta / len(trainloader)"

# --- GUARD 5 -- disk -------------------------------------------------------
python3 - "$WS" "$NJOBS" <<'PYEOF' || guard_fail "guard 5: disk"
import shutil, sys
free_gb = shutil.disk_usage(sys.argv[1]).free / 1e9
need_gb = int(sys.argv[2]) * 0.060
if free_gb < 20 * need_gb:
    sys.exit("GUARD FAIL: %.1f GB free vs ~%.2f GB needed (20x wanted)" % (free_gb, need_gb))
print("guard 5: %.0f GB free vs ~%.2f GB needed  OK" % (free_gb, need_gb))
PYEOF

# --- GUARD 6 -- queue depth ------------------------------------------------
FS=$(sshare -U -u "$USER_NAME" -n -o FairShare 2>/dev/null | tr -d ' ' | head -1)
PEND=$(squeue -h -u "$USER_NAME" -t PENDING 2>/dev/null | wc -l | tr -d ' ')
RUN=$(squeue -h -u "$USER_NAME" -t RUNNING 2>/dev/null | wc -l | tr -d ' ')
echo "guard 6: FairShare=${FS:-unknown} (informational), pending=$PEND running=$RUN, adding $NJOBS"
if [ "$PEND" -gt 40 ]; then
  guard_fail "guard 6: $PEND already pending, over the 40 cap"
fi

# --- GUARD 7 -- **THE PREMISE: ar1 REALLY DID BIND, RE-DERIVED FROM DISK** --
# The batch exists because the old box bound.  Assert that from the probes rather
# than quote it, and assert the differential that makes fa1 INSTRUMENT-ONLY.
python3 - "$WS" "$REPO" "$CLIP_REF" <<'PYEOF' || guard_fail "guard 7: ar1's bind"
import glob, os, sys
ws, repo, clip_ref = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(repo, "analysis"))
from c52_boxfree import occupancy
lo, hi = (float(x) for x in clip_ref.split(":"))
dirs = sorted(glob.glob(os.path.join(ws, "runs", "ar1", "probe_*")))
if not dirs:
    dirs = sorted(glob.glob(os.path.join(repo, "..", "probes_ar1", "probe_*")))
if len(dirs) != 12:
    sys.exit("GUARD FAIL: %d ar1 probe dirs, expected 12" % len(dirs))
bound = 0
cl = {}
for d in dirs:
    o = occupancy(d, lo, hi)
    b = not (o["rec_lo"] < 0.05 and o["rec_hi"] < 0.05)
    bound += b
    arm = os.path.basename(d).split("_")[1]
    if o["coord_lo"] is not None:
        cl.setdefault(arm, []).append(o["coord_lo"])
if bound != 12:
    sys.exit("GUARD FAIL: only %d/12 ar1 arms are box-bound in %s -- the premise "
             "of this batch is weaker than stated; re-read before submitting"
             % (bound, clip_ref))
print("guard 7: ar1 is box-bound on 12/12 arms in %s -- the premise holds" % clip_ref)
if "node" in cl and "ch" in cl:
    n, c = max(cl["node"]), max(cl["ch"])
    print("guard 7b: clamped coordinate mass over ALL (record, coordinate) cells "
          "[denominator 10,000 records x m]: nodewise %.4f vs chunk777 %.4f = %.0fx "
          "-- the guard bound DIFFERENTIALLY across D's own two arms, which is why "
          "fa1 is INSTRUMENT-ONLY and may not re-read A1"
          % (n, c, n / c if c else float("inf")))
PYEOF

# ---------------------------------------------------------------------------
if [ "$SUBMIT" = "1" ]; then
  mkdir -p "$SAVE" || { echo "GUARD FAIL: cannot create $SAVE"; exit 1; }
else
  mkdir -p "$SAVE" 2>/dev/null || true
fi
N=0
FAIL=0
SGDM=(--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base 0.1
      --alg-meta Lion --momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0)
for S in $SEEDS; do
  for ARM in "nodewise:node" "chunk${CHUNK_K}:ch" "nodewise1d:n1d" "chunk${CHUNK_K2}:c23"; do
    GRAN="${ARM%%:*}"; SHORT="${ARM##*:}"
    RN="fa1-${SHORT}-s${S}"
    CMD=(sbatch --job-name="$RN" --partition="$PARTS" --gres=gpu:1 --cpus-per-task=6
      --mem=14G --time="$WALL" --nice=0
      --export="ALL,AUGMENT=1,BETA_CLIP=${CLIP},PROBE=5,PROBE5=1,PROBE5_WRITE_EVERY=${WRITE_EVERY},PROBE_DIR=$SAVE/probe_${SHORT}_fa1_s${S}"
      "$RUNNER" "${SGDM[@]}"
      --dataset CIFAR10 --NN-name ResNet18 --batch-size "$BATCH"
      --max-time 999:00:00 --gamma 1 --meta-stepsize "$MST" --alpha0 "$ALPHA0"
      --num-epochs "$EPOCHS" --stepsize-groups "$GRAN" --seed "$S"
      --save-directory "$SAVE" --run-name "$RN")
    # COUNT WHAT SLURM ACCEPTED, NOT WHAT WE TRIED (CORRECTIONS 71).
    if [ "$SUBMIT" = "1" ]; then
      if "${CMD[@]}" >/dev/null; then N=$((N+1)); else FAIL=$((FAIL+1)); fi
    else
      N=$((N+1)); printf '%s\n' "${CMD[*]}"
    fi
  done
done
echo "---- $N jobs ($( [ "$SUBMIT" = 1 ] && echo ACCEPTED BY SLURM || echo 'dry run, nothing submitted' )); $FAIL rejected ----"
[ "$N" = "$NJOBS" ] || echo "!!! expected $NJOBS jobs, built $N -- DO NOT TREAT AS SUBMITTED"
[ "$FAIL" -gt 0 ] && echo "!!! $FAIL sbatch calls FAILED -- do not treat this batch as submitted"
if [ "$GUARD_FAILS" -gt 0 ]; then
  echo "=============================================================="
  echo "!!! $GUARD_FAILS GUARD(S) FAILED.  The emitter above is VALIDATED; the batch is NOT."
  echo "!!! Nothing was submitted and nothing may be submitted until every guard"
  echo "!!! passes ON ALICE.  A dry run with failed guards is not a green light."
  echo "=============================================================="
  exit 2
fi
exit 0
