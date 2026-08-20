# Continue here — self-contained handoff

Any fresh session (primary account, `claude2`, or a scheduled task) can resume from this file.
Nothing below depends on prior conversation context.

## Access
* `ssh alice`  — user `salehkaleybars`, workspace `/data1/salehkaleybars/metaopt` (5 TB scratch)
* `ssh alice2` — user `s5014158` (Reza's own), workspace `~/metaopt` (2 TB home)
* Both are passwordless key auth from this Mac. Slurm scheduler. Compute is free and uncapped;
  per-user concurrency caps are 2x A100 / 8x L4 / 12x 2080ti, so **use both accounts**.
* This repo is mirrored at `/data1/salehkaleybars/metaopt/hierarchical-metaoptimize`.

## Read these first, in order
1. `docs/FINDINGS.md`   — every measured result, with confirmed/pending status
2. `paper/DRAFT.md`     — the write-up; rows tagged ✅ confirmed / ⏳ in flight / ⚠️ untrustworthy
3. `docs/OPERATIONS.md` — the gotchas below, in full
4. `docs/PAPER-CONFIG.md` — the parent paper's exact config, extracted from its PDF
5. `docs/PRIOR-ART.md`  — what is novel vs a rediscovery (read before claiming anything)

## The state of the science, in one paragraph (rewritten cycle 21; see cycle 26 above for the mechanism)
Three results now carry the paper. **(1) The sqrt(N) noise model is refuted with the sign
INVERTED**, in three architectures across two datasets: holding beta common (`HIER=shrink,
LAM=1.0`) and varying only the group size, drift *rises* with group size (log-log slopes
+0.179 / +0.268 / +0.203 where the model requires -0.500), at alpha0=1e-3 and with
weightwise sign-agreement excess of only 0.08-0.47% -- so independence *holds* and the
prediction *still* fails. **(2) The granularity gain tracks TASK DIFFICULTY, not parameter
count.** On CIFAR-10 at alpha0=1e-6 the gain (layerwise - scalar) falls 19.88 -> 2.87 -> 0.90
across ResNet10/18/34, which looks like the parent paper's premise -- but the LAYERWISE arm is
flat (90.220-90.686, a 0.47pp spread) while the SCALAR arm moves 18.58pp; the whole trend is
scalar catching up. CIFAR-100 at the *middle* model size then gives **+47.6pp**, the campaign's
largest effect, and it does not care about alpha0 (+47.59 at 1e-6, +47.64 at 1e-3). `cs-*`
(submitted cycle 21) supplies the missing CIFAR-100 model sizes that turn this from hypothesis
into result. **(3) M1's `r` is NOT a pooling dial (cycle 33; CORRECTIONS 21).** `r=1` is plain layerwise
(verified: 90.863 +-0.063 vs 90.891). `r=0` was believed to be FULL pooling; it is not. Under
Lion every group's realised beta increment has magnitude exactly `ms`, so `additive`'s mean-of-
increments shrinks the shared step to `ms*|2p-1|` -- a 10.3x meta-step-size cut at layerwise.
`additive` r=0 therefore spans 47.58pp across granularities (45.005 weightwise -> 92.587
layerwise) where a true pooling arm must be granularity-invariant; `zpool` r=0 is, to 0.032pp.
**"Even full pooling helps" is REFUTED**: true full pooling is -3.044pp vs plain layerwise.
The M1 interior optimum survives as an EMPIRICAL curve (layerwise +2.359pp n=10, nodewise
+1.140pp n=3, absent at blk6 and weightwise) but has no pooling interpretation. On CIFAR-100
the same r=0.07 costs -43.7pp. **Do not write any "pooling helps" sentence.**
**The correction that bounds all method claims:** a tuned non-meta baseline now WINS. AdamW +
cosine at lr 1e-3 reaches **94.093 +-0.036** under matched budget (100ep, AUGMENT=1, ResNet18,
CIFAR-10) against the best MetaOptimize arm's **93.306 +-0.140** -- a 0.79pp deficit. Earlier
cycles compared against *constant-LR* AdamW (91.86), which MetaOptimize does beat by +1.38pp.
The gap is the schedule, not the optimizer. Results (1)-(3) are statements about
MetaOptimize's internals and are untouched; any "our method is better" sentence is not.


## Running / next (cycle 38) -- COLLECTION CYCLE, nothing submitted

**The pre-registered meta-step control fired against granularity (FINDINGS 38.1).** At a0=1e-3,
R18/CIFAR-10, SGDm+Lion: plain `scalar` with ms tuned 1e-3 -> 1e-4 scores **92.405 +-0.071
(n=2)** -- inside cycle 33's pre-registered [92.2,92.6] window. That matches the BEST
hierarchical arm (`additive` r=0.1, 92.449 +-0.192, n=3) to **0.044pp** and beats plain
layerwise (91.093 +-0.220, n=5) by 1.312pp. The whole +4.87pp scalar->layerwise "granularity
gain" is reproduced by changing one scalar hyperparameter. With 33.1 (r rescales the effective
meta-step by |2p-1| ~ 0.097) this closes the loop: **the hierarchy's only measured contribution
is dividing the meta-step by ~10, and doing that directly with one group is equal or better.**

* **`ms-layA-1e4` (3 seeds, PENDING alice2) is now the most informative job in the campaign.**
  Layerwise at the tuned ms=1e-4 / a0=1e-3. Above 92.405 => granularity earns something back at
  its own tuned meta-step. Level => 38.1 is the whole story.
* `ms-scalA-1e4` is **n=2**; s2 sits at 89/100 and must not be read. Needs n=5.
* **alpha0=1e-6 escape confound quantified: 51.04pp** (ms=1e-4 scores 41.368 at a0=1e-6 vs
  92.405 at a0=1e-3). It inverts the SHAPE of the ms curve. No ms claim off a0=1e-6 runs.
* **Baseline win holds across architecture.** R34 now n=3 both sides: 94.674 +-0.026 vs 93.930
  +-0.143 = 0.744pp, matching R18's 0.787pp. Not a ResNet18 artefact; does not close at scale.
  lr=1e-3 is argmax at R18/R34/R50 -- the baseline's tuning transfers. R50 baseline is n=1.
* **LR grid decensored** (answers 36's objection): 1e-4 92.851 / 3e-4 94.062 / 1e-3 94.093 /
  1e-2 92.728. 1e-3 is an INTERIOR maximum. A 10x-mistuned cosine still beats the best matched-a0
  meta arm by 0.28pp.
* **Ops: submitted NOTHING.** FairShare 0.3356 / 0.3381 (below the 0.35 floor); pending 59 / 94
  (above the 40 cap); 93 of 94 alice2 pendings blocked on `QOSMaxGRESPerUser` = GPU-cap-bound,
  not priority-bound, so extra jobs could not have started anything sooner. Every open question
  above already has its deciding cell queued.
* Priority inversion (LR sweep ahead of `bg300`/`bg600`) noted and **deliberately not corrected**
  -- post-36.1 the sweep is the decisive line and `bg` is downstream of it.

## Running / next (cycle 33)  -- queues: alice 174, alice2 164 = 338 jobs

**Cycle 33 refuted the campaign's pooling story and found the mechanism 26.3 was missing.**
Three arms that all end in ONE uniform step size score 4.85pp apart, ordered by their
EFFECTIVE meta-step-size and nothing else (FINDINGS 33.1):

| arm | effective meta-step | n | plateau |
|---|---|---|---|
| `zpool` r=0 / plain `scalar` | `ms` = 1e-3 | 5 / 12 | 87.740 / 87.772 |
| `shrink` lam=1.0 | `ms`*\|2p-1\| ~ 9.7e-5 | 3 | 92.199 |
| `additive` r=0 | `ms`*\|2p-1\| ~ 9.7e-5 | 8 | 92.587 |

`_zpool` pools the meta-GRADIENT before Lion (magnitude survives); `_apply_hier` pools the
REALISED increments after Lion (magnitude collapses to the sign-agreement excess). So M1's `r`
moves pooling and meta-step-size together. **The M1 gain depends on agreement because the
effective meta-LR does** -- that is the mechanism, and it is a confound, not a result.

**The meta-step-size axis is unexplored: 1042 of 1075 runs sit at `ms`=1e-3.**

* **`ms-scal-*` (26, alice) / `ms-lay-*` (26, alice2) -- PRE-REGISTERED, DECISIVE.**
  `scalar` and plain `layerwise` x ms in {1e-5, 3e-5, 1e-4, 3e-4}, n=5, plus a0=1e-3 controls.
  **Pre-reg: `scalar` at ms=1e-4 lands 92.2-92.6** (on `shrink` lam=1 / `additive` r=0) => the
  whole M0/M1 family is meta-LR tuning and granularity contributes nothing. Staying near 87.8
  saves the pooling arms. Whether the layerwise ms curve reaches 93.222 decides M1.
* **`zp-w-*` / `zp-l-*` (17, alice2) -- PRE-REGISTERED.** True-pooling curve: weightwise
  r in {0.9,0.95,0.99} to n=5, NEW cells r in {0.995,0.999}, layerwise r=0.99 to n=3.
  33.2's weightwise interior optimum (+11.130pp at r=0.99) is n=2 and its cliff is unlocated.
* Still front-of-queue from cycle 32: `p7-c100r*` (30), `sc50-*` (18+6 running), `r34r-*` (9),
  `f5cos-*` (12) on alice; `r34f-*` (11), `bp-*`/`bo-*` (~39), `ag-*`/`ap-*` (36),
  `mx-h4-*` (20) on alice2. All pre-registered; none is blocked by this cycle's submissions.
* **Cancelled 97 jobs**, each with a reason recorded in FINDINGS 33.8. Net queue change -45.
* Ops: throughput is STILL 24 concurrent. The per-account cap of 42 GPUs is not reachable --
  the QOS pools are per-partition and every long partition is fully allocated by other users,
  so multi-partition submission cannot spread into them (FINDINGS 33.9). Also: fair-share has
  fallen far enough that a fresh nice-0 job now ranks BELOW old nice-400 jobs; the only way to
  promote an old low-priority batch is cancel-and-resubmit.

## Running / next (cycle 32)  -- queues: alice 189, alice2 214 = 403 jobs

**Cycle 32 found two batches that finished cycles ago and were never tabulated** (`sc50-*` =
ResNet50 n=1; `cs-r10/cs-r34-*` = CIFAR-100 x model scale n=3). Reducing them gives a
FOUR-architecture model-scale ladder on CIFAR-10 and a THREE-row one on CIFAR-100, and the two
scale effects run in OPPOSITE directions (FINDINGS 32.5-32.6):

| | R10 4.9M | R18 11.2M | R34 21.3M | R50 23.5M |
|---|---|---|---|---|
| M1 pooling gain (r=0.06 vs r=1), a0=1e-6 | +0.166 (null) | +2.446 | +2.594 | +3.237 (n=1) |
| plain granularity gain (layerwise - scalar) | +19.877 | +3.043 | +0.835 | **-1.394 (n=1)** |

**ResNet50 at a0=1e-6 is the first architecture where the parent paper's premise reproduces**
-- layerwise loses to scalar. It is ONE SEED. `sc50` s1-s4 are queued at nice 50; do not state
it until they land.

**The paper core got stronger.** `p9-*` landed: the agreement/drift ladder is n=10 at all four
rungs on BOTH datasets, and all 8 slopes have bootstrap 95% CIs that exclude -0.500 (32.1).
A 9th fit at a0=1e-6/100ep gives -0.2363 and shows the drift-vs-m curve is **non-monotone**
(rises 6 -> 62, then falls), so sqrt(N) has the wrong FUNCTIONAL FORM, not just the wrong
exponent (32.2). 31 of 32 leave-one-rung-out sub-spans also stay above -0.500; the one
exception (-0.5248, R10/STARTUP/node->weight, n=2) is anchored on the weightwise startup drift,
which is a near-cancellation biased toward zero and therefore biases that slope steep (32.3).

**26.3's mechanism is refuted.** `gp-node-*` landed at M1 gain +1.204 against a LOWER agreement
than layerwise's +2.446. Agreement is monotone in m; the gain is not (32.8). The campaign has
no single mechanism right now.

* **`p7-c100r10-*` / `p7-c100r34-*` (30, alice, nice 0) -- PRE-REGISTERED.** C100 x {R10,R34}
  agreement ladder; predicts every slope stays above -0.500. 20-ep probes, ~15 min each.
* **`sc50-*-s{2,3,4}` (18, nice 50)** + s1 promoted -> n=5 on the ResNet50 rung.
* **`f5cos-r34-*` / `f5cos-r50-*` (12, nice 150).** The tuned non-meta baseline exists only at
  ResNet18 (94.093). Our best arm is 93.884 at **R34** -- currently a cross-architecture
  comparison. Until these land, no "wins/loses by X" sentence may name R34 or R50.
* **`r34r-r{0005,001,0015}` (9, nice 150) -- PRE-REGISTERED.** R34's optimum r=0.02 is the
  smallest non-zero point on its grid. Candidate law r* ~ 1/N (r*.N = 0.5M +-0.12M): predicts
  all three land below 93.884 and above 93.098; a peak at r<=0.01 refutes the 1/N form.
* **Cancelled `sw-cos-*` (21)** -- duplicate of the already-complete `fxcos-*` sweep.
* **Not touched: `kc-*` (39)** -- inspected first (30.0's lesson); it is the C100 M1 r-curve
  (R18_c100 to n=5, plus a new R10_c100 curve) and is the n>=5 follow-up to 32.6(d).
* Ops: throughput is still capped at 24 concurrent `gpu-short` jobs on a full cluster.
  `scontrol update Nice=` must EXCEED the job's accrued age (~700 points per half-day), not
  just beat the other job's nice -- see 32.10.

## Running / next (cycle 28)  -- queues: alice 299, alice2 250 = 549 jobs

**Cycle 28 found three more unreduced probe batches, and one of them inverts the mechanism.**
`gate1`/`gate2`/`gate3` (Aug 18, 33 dirs across both accounts) had zero mentions in FINDINGS
or CORRECTIONS. `gate2` is base **AdamW**, and its sign-agreement RISES with partition
fineness (m=6 71.20 -> m=62 79.96) where every SGDm batch in the campaign has it FALL
(`gate1`: 63.64 -> 54.69). 26.3's monotone fall is base-optimizer-specific, and that is the
mechanism H4 has been missing since cycle 12. See FINDINGS 28.4.

**Do not tabulate those numbers with 26.3's.** `gate1`/`gate2` predate the probe's `frac_neg`
field; the recovered `z_mean` statistic disagrees with the published one by 7.2pp at m=6.
Validated and recorded as CORRECTIONS 18. `gate3` is divergent (`sd_beta` 20.5) and excluded.

**Also this cycle:** `r10c-*` landed and the ResNet10 M1 interior optimum **disappears** at
a0=1e-3 -- the r-curve is monotone increasing over the whole grid and its best interior point
is 0.21pp BELOW plain layerwise, against a clean +1.00pp interior optimum at a0=1e-6 (28.5).
With 27.4 (R18: +2.40 -> +1.29) the a0-dependence of the M1 gain is now a pattern, and on
ResNet10 it goes to zero.

* **`ap-*` (9) + `ag-*` (27), alice2, submitted this cycle -- PRE-REGISTERED.** The AdamW
  agreement ladder in the modern probe format ({blk6, node, weight}; layerwise is the already
  queued `bp-adamw-s*`), plus the AdamW M1 r-curve that mirrors `sub_gp.sh` field for field
  with only the base changed. Predicts (a) the ladder inverts on `frac_neg` too, (b) the gain
  ladder therefore runs the opposite way to SGDm's. See FINDINGS 28.6.
* **`p7-*` (33) promoted to the front of alice**, `bp-*` (12) to the front of alice2. Both are
  20-epoch probe blocks; together they cost ~40 min of the 24-GPU allocation and they are what
  makes this cycle's contrast readable.
* `r34r-*` and `gp-*` rows are now in the CSV at 3-75 epochs -- IN FLIGHT, correctly excluded
  by the `epochs_done >= 100` filter. Do not read them yet.

## Running / next (cycle 26)  -- queues: alice 271, alice2 184 = 455 jobs

**Cycle 26 found the mechanism, in data that was already on disk.** Three probe batches had
never been reduced (`mx/probe_sig_*`, `p5scale`, `p6mech` -- 43 dirs, zero mentions in
FINDINGS or CORRECTIONS). Reducing `mx/probe_sig_*` (the only free-adaptation, 100-epoch,
dense-probe granularity series, config-matched to the 25.3 r-curve) gives:

| granularity | m | sign agreement | M1 pooling gain |
|---|---|---|---|
| resnet18_blocks | 6 | **70.87 ±0.80 %** | +0.415 |
| layerwise | 62 | **53.26 ±0.19 %** | +2.399 |
| nodewise | 14,420 | **51.03 ±0.12 %** | in flight (`gp-node-*`) |
| weightwise | 11,173,962 | **50.0053 ±0.0003 %** | +11.13 (zpool, 25.5) |

**Agreement falls monotonically with partition fineness and the pooling gain runs OPPOSITE
to it.** One mechanism for three previously unrelated results: 25.3's granularity-dependent
gain, 25.5's weightwise interior optimum, and 24.3's null on CIFAR-100. See FINDINGS 26.3.

Also this cycle: **the full-pooling identity is verified STRUCTURALLY at last** -- `p6mech`
shows `sd_beta` = exactly 0.0000 at r=0 on both seeds, and 2.47 at r=1 against plain
layerwise's 2.39 (26.4). Rule 4 satisfied; CORRECTIONS 13's open item closed.

* **`cw-*` (alice, 36) -- submitted this cycle. THE falsification test.** CIFAR-100 x
  {weightwise, nodewise} M1 r-curve, with agreement probes on the r=1 seed so gain and
  agreement come from the SAME run family. Pre-registered prediction: pooling is useless at
  C100/layerwise (already measured, 24.3) but LARGE at C100/weightwise. If it is not, 26.3
  dies. See FINDINGS 26.7.
* **`gp-node-*` / `gp-w-*` (alice2, 48) -- PROMOTED rank ~40 -> 25** by niceing `m0c-*` to
  30000. These supply the two missing cells of the gain column above and make it one run
  family instead of three.
* **`p6f-*` (alice, rank 1-9)** -- free-adaptation agreement on {C100, R10, R34} x
  {layer, node, weight}. Pairs with `mx/probe_sig_*` for the model-scale agreement ladder,
  which 25.6 predicts should FALL with model size.
* **`r34r-*` (alice, 27)** -- R34 r-curve; 25.6's third row is still one point.
* Niced to 30000: `m0c-*` (15, M0 shrink on CIFAR-100 -- raises a null 24.3 settled).

**Two corrections this cycle, both in the measurement layer, both recorded (CORRECTIONS
16-17):** `block_sizes.json` reports 11,173,962 coordinates for nodewise arms that have
14,420 (a 27.8x significance inflation if trusted); and `drift/step` is **censored** by
Lion's sign update at exactly the meta-stepsize, with two published `p4scale` slopes sitting
on that ceiling. The sqrt(N) refutation survives both (positive slope in 6/6 fits across two
alpha0); the slope magnitudes do not.

## Gotchas that cost hours — do not rediscover these
* **A probe directory with no `frac_zero` field is on the LEGACY statistic.** `gate1`/`gate2`
  carry only `beta`/`z_mean`/`z_std`/`snr`. `z_mean` is a per-TENSOR running mean (62 entries
  on every arm, including the 14,420-node and 11.17M-weight ones) and its agreement disagrees
  with the published `frac_neg` one by **7.2pp at m=6**. `analysis/agree_legacy.py` prints the
  same columns as `agree2.py` deliberately -- that makes the two easy to paste into one table.
  Do not. CORRECTIONS 18.
* **The Aug-18 `gate*` batches were STILL unread at cycle 27**, two cycles after the sweep
  that was supposed to catch exactly this. Sweeping by `find -name probe.jsonl` is not enough
  -- grep every top-level probe DIRECTORY name against FINDINGS and CORRECTIONS and reduce the
  ones that come back zero. Cycle 28 did that and found 33 dirs, one of which inverts 26.3.
* **Three probe batches sat unreduced for multiple cycles and one of them was the
  mechanism.** Before submitting ANY new probe run, sweep both accounts with
  `find <runs> -name probe.jsonl -size +1k` and grep every dir name against FINDINGS and
  CORRECTIONS. Cycle 26 found 43 unreduced dirs, including the only free-adaptation
  100-epoch granularity series in the campaign.
* **`block_sizes.json`'s `n_b` is WRONG for nodewise** (reports total params, 11.17M, for a
  14,420-node arm). Infer `n_tot` from the `frac_neg` rational denominators instead --
  `analysis/infer_ntot.py`. Verified against five independently recorded counts.
* **`drift/step` is censored at the meta-stepsize.** Lion's update is sign-based, so
  `|d beta|` per step is exactly `meta_stepsize`; `drift/step = 1.000e-03` means "pinned at
  the ceiling", not "very fast". Two published slopes were fitted through such a point.
  Normalise by the meta-stepsize before regressing.
* **`drift_extract2.py`'s window (steps 1000-7500) is the a0=1e-6 STARTUP transient** on any
  100-epoch run (50k steps). Use `analysis/agree2.py`, which reports a steady window (last
  50%) and startup separately.
* **Sign-agreement excess must be read against its own noise floor.** At n_tot=62 the
  per-record independence floor is 6.35pp, at n_tot=11.17M it is 0.015pp -- a 400x
  difference. Raw excess is NOT comparable across granularities without it.
* **`LAM=na` / `ETA_RATIO=na` KILL the job.** `HF.py` lines 24-25 `float()` both env vars
  unconditionally. `na` is what `run_cifar.sh` *echoes* for an UNSET variable, so healthy runs
  display it -- copying that into `--export=` cost 48 jobs. Non-hierarchical arms must export
  **none** of `HIER`/`LAM`/`ETA_RATIO`; under `HIER=additive` use `LAM=0`.
* **The `collapsed` column in `all_runs.csv` is `0` on EVERY row — it flags nothing.** One
  ResNet18/scalar/a0=1e-6 run plateaus at 20.5; it inflated that cell's sd to 14.16 and the
  reported granularity gain from +1.73 to **+4.60**. Filter `plateau > 50` explicitly until the
  aggregator is fixed. Audited cycle 23: this is the only affected cell in the CIFAR-10 plain
  ladder, and the additive r-curves have no collapses at all.
* **`resnet18_blocks` is ResNet18-only** -- `ZeroDivisionError` at `HF.py:175` on ResNet10/34
  (6 `sc-*-blk6` jobs died). Use `scalar`/`layerwise` on other architectures.
* **12 running per account IS the ceiling, not a bug.** Every non-`gpu-short` GPU node reports
  `AllocTRES` = its full GPU count (other users hold them); `qos-gpu-short` caps at
  `gres/gpu=12` per user. Confirm with `scontrol show node <n> | grep AllocTRES` before
  "fixing" anything. Negative `Nice` is denied, **but `scontrol update JobId=<j> Nice=0` on a
  previously-niced job IS accepted and is a large promotion** (cycle 24: `p6f` went 651704 ->
  671710, back of the queue to #2). You do NOT have to nice other blocks back to promote one.
* **Compare against a SCHEDULED baseline, not a constant-LR one.** AdamW+cosine 94.09 beats
  the best MetaOptimize arm 93.31; constant-LR AdamW 91.86 loses to it by 1.38pp. Which
  baseline you pick flips the sign of the headline method claim.
* **`r` in the additive hierarchy is RETENTION: r=1 = plain layerwise, r=0 = FULL pooling.**
  Three cycles quoted the M1 gain against r=0 as if it were the no-pooling control. See
  CORRECTIONS 13.
* **`bin/drift_extract.py`'s `spread` column is a verification that cannot fail** -- it reads
  `beta_true_max - beta_true_min`, which the probe writes identically on every arm. Use
  `bin/drift_extract2.py` (`sd_beta`) instead. Its `frac_neg` is also meaningless on scalar
  arms (1-element list -> it measures a time-fraction, not agreement).
* **The cluster's `analysis/aggregate.py` drifts stale.** It lost the
  `network`/`dataset`/`batch_size` columns; re-aggregating without pushing the repo version
  first silently drops every cross-architecture and cross-dataset claim. `scp` it before use.
* **Login-node python needs `module load Python/3.10.4-GCCcore-11.3.0` BEFORE
  `source envs/mo/bin/activate`**, else `libpython3.10.so.1.0: cannot open shared object file`.
* **CIFAR-100 is staged on BOTH accounts** (`.../cifar10/data/cifar-100-python`), and alice2's
  `build_network.py` supports `ResNet18_c100`/`ResNet34`. It is not single-account bound.
* Pending jobs at reason `(None)` are not held -- that is the scheduler's per-user evaluation
  depth (~top 100). Order the front of the queue; do not submit less.
* **`HIER=none` is TRUTHY and silently enables the hierarchy branch.** `HF.py` does
  `self._hier = os.environ.get('HIER','')` then `if self._hier:`. Existing `sc-*` runs log
  `HIER=none` **only** because `run_cifar.sh` echoes `${HIER:-none}` over an *unset* variable.
  Non-hierarchical arms must leave `HIER` **unset**. This nearly corrupted 18 control runs.
* **On alice2 the runner is `jobs/run_cifar.sh`** (already the s5014158 variant, with
  `/home/s5014158` paths baked in). `run_cifar_alice2.sh` exists only in the git repo, not on
  that account -- using that name gives `sbatch: error: Unable to open file`.
* **`sc50` = ResNet50, `sc101` = ResNet101 -- and R50 DOES finish inside `gpu-short`.**
  Measured cycle 24 from live TensorBoard scalars: ~44 epochs/hour, 100 epochs in ~2:20
  inside the 3:50 limit. The cycle-23 prose "31-34 epochs in 4h, needs a 7-day partition"
  was wrong and nearly cost six healthy running jobs. Read the event files, not the prose.
* **A running job's progress is readable without `probe.jsonl`.** `sc50` had no probe dir;
  `EventAccumulator` over `runs/<b>/Tensorboard_outputs/<run>/events*` gives the epoch count
  directly (`len(a.Scalars('Performance/train_accuracy'))`). Use it before cancelling anything.
* **`gpu-short` caps at 4:00:00** (`sinfo`); the other four GPU partitions allow 7 days. Use
  `--time=03:50:00` to stay eligible, and drop `gpu-short` for anything longer.
* **Check whether an "alpha0 control" already exists before submitting one.** `mx-a1e3-*` was
  an exact match to `sc-ResNet18-*` on every field but alpha0; 9 of 27 submitted jobs were
  redundant and had to be cancelled. Grep the CSV for the config, not the run-name prefix.
* Helper scripts go in `/data1/salehkaleybars/metaopt/bin`, **never `/tmp`** (node-local; the
  login nodes round-robin between nodelogin03/04, so scp'd files vanish between calls).
* Pattern that works: write locally → `scp` to that dir → `ssh alice 'bash <path>' 2>&1 | tail -N`.
  Filtering with `sed` over the SSH banner is unreliable; use `tail`.
* **Always** `--max-time 999:00:00` — `train.py` has its own truncation break that silently
  shortens runs.
* **Always** `--export=ALL,AUGMENT=1` — without augmentation ResNet-18 memorises CIFAR-10 in
  epoch 1 and the comparison is meaningless.
* `BETA_CLIP` uses a **colon** (`-15:-2.3026`); a comma breaks both the parser and `sbatch --export`.
* Pin GPUs: `--partition=gpu-l4-24g --gres=gpu:l4:1`. Mixing GPU types makes timing incomparable.
* A running job's `.out` shows **0 epochs** because Python buffers stdout. Read
  `PROBE_DIR/probe.jsonl` for true progress (`last_step / 500` = epochs). Three healthy jobs were
  killed on this misreading.
* Runs reproduce to ~**±0.02pp, not bitwise** (cuDNN autotuning). Effects under ~0.05pp need more
  seeds.
* **Reduce every probe dir that already exists BEFORE submitting new ones.** Cycle 18 found
  two complete, never-analysed drift series (`bdrift3/p3-*`, `bdrift4/p4-ad-*`); one of them
  downgraded a headline effect 16x and the other showed the headline has no mechanism. Sweep:
  `find <runs> -name probe.jsonl -size +1k`. Reducer: `bin/drift_extract.py` (validated -- it
  reproduces the published p2 table exactly).
* **`plateau` is the mean of the last 20 epochs, not 5** (code wins over prose; see
  CORRECTIONS 11). Filter `epochs_done >= 100` before comparing plateaus -- in-flight runs
  carry a plateau value that is not comparable.
* Pin GPUs **only** when timing matters. For epochs-to-target/plateau claims mix freely and
  always submit all five partitions; `gpu-short` caps at 4h so 300-epoch arms must omit it.
* Name new probe batches carefully: `p4-*` already existed on alice2 (`runs/bdrift4`) and was
  unrelated to cycle 18's `p4-*` on alice.
* ImageNet on `/data1` is **489 of 1000 classes** — scoped out; do not train on it and call it
  ImageNet.

## Standing instruction
Full autonomy was granted: decide and act, do not ask permission. The one thing that genuinely
needs the account holder is ImageNet credentials (and it is already scoped out).
