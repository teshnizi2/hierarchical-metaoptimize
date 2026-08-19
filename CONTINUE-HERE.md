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

## The state of the science, in one paragraph (rewritten cycle 21)
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
into result. **(3) Pooling inverts between datasets.** `r` is the RETENTION of the
group-specific update -- **r=1 is plain layerwise (verified: 90.863 +-0.063 vs 90.891) and r=0
is FULL pooling**. On CIFAR-10/ResNet18 the optimum is interior at r~0.07 (+2.31pp over plain
layerwise) and even full pooling helps (+1.39pp); on CIFAR-100 the same r=0.07 costs -43.7pp
and full pooling **collapses the model to 8.98%** (100-class chance is 1%), a -61.13pp penalty.
**The correction that bounds all method claims:** a tuned non-meta baseline now WINS. AdamW +
cosine at lr 1e-3 reaches **94.093 +-0.036** under matched budget (100ep, AUGMENT=1, ResNet18,
CIFAR-10) against the best MetaOptimize arm's **93.306 +-0.140** -- a 0.79pp deficit. Earlier
cycles compared against *constant-LR* AdamW (91.86), which MetaOptimize does beat by +1.38pp.
The gap is the schedule, not the optimizer. Results (1)-(3) are statements about
MetaOptimize's internals and are untouched; any "our method is better" sentence is not.


## Running / next (cycle 23)  -- queues: alice 237, alice2 178 = 415 jobs

**Cycle 23's finding (docs/FINDINGS.md 23.3-23.4):** the M1 pooling gain and the plain
granularity gain run in OPPOSITE directions in model scale. Plain granularity
(layerwise - scalar) decays +19.88 -> +1.73 -> +0.90 over R10/R18/R34 at alpha0=1e-6 and
+20.48 -> +2.32 -> +0.51 at 1e-3 (both now measured; the 1e-3 replication `sa3-*` landed this
cycle). M1 additive at r=0.06 does the reverse: +0.17 -> +2.33 -> +2.62 at 1e-6 and
-2.30 -> +0.83 -> +3.29 at 1e-3. The r-curves explain why: the optimum shifts toward LESS
pooling as the model shrinks (R18 peaks r=0.06 +2.33; R10 peaks r=0.1 +0.97) and full pooling
r=0 goes from +1.26 at R18 to -8.50 at R10. **This is not yet reportable: ResNet34 is sampled
at ONE r.** `r34r-*` fixes that and tests the prediction that R34's optimum is at r<0.06 with
peak >+2.62.

* **`r34r-*` (alice, 27)** -- R34 CIFAR-10 a0=1e-6, r in {0,.02,.03,.04,.05,.08,.1,.2,1} x 3
  seeds. THE experiment: completes the r-curve family at three model sizes. r=1 is the identity
  control (must reproduce plain layerwise 90.220 +-0.011).
* **`r10c-*` (alice2, 18)** -- R10 CIFAR-10 a0=1e-3, r in {0,.05,.1,.2,.5,1} x 3 seeds.
  R10@1e-3 has only r=0.06 and it is NEGATIVE (-2.30); does the optimum shift right at 1e-3 too?
* **`cs-*` (alice, 18)** -- CIFAR-100 x {R10,R34} x {scalar,layerwise,additive} x 3 seeds.
  Cancelled+resubmitted 23:54 19 Aug (ids 4683766+, elapsed 0:00, no data lost). Separates
  task difficulty from parameter count.
* **`m0c-*`/`m0s-*`/`m0l-*`** -- M0 shrink on CIFAR-100 and at scale; still the open question
  of whether M0 is the paper's method.
* **`sa3-ResNet34-*` (alice2)** -- fills the n=1 cells at alpha0=1e-3.
* Niced back to 20000 this cycle: alice 102 jobs, alice2 58. `sc50`/`sc101` cannot produce a
  100-epoch point on `gpu-short` at all (31-34 epochs in 4h) -- they need a 7-day partition.

## Gotchas that cost hours — do not rediscover these
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
  "fixing" anything. **Negative `Nice` is denied** to unprivileged users -- the only way to
  promote a block is to nice *other* jobs back.
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
