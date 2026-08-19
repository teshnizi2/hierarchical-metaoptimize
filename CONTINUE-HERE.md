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

## The state of the science, in one paragraph (rewritten cycle 20)
Two results now carry the paper, and both got stronger this cycle. **(1) The sqrt(N) noise
model is refuted with the sign INVERTED, in three architectures across two datasets.** Holding
beta common (`HIER=shrink, LAM=1.0`) and varying only the group size over which the
meta-gradient is aggregated, drift *rises* with group size: weightwise is the slowest-drifting
arm and scalar the fastest, giving log-log slopes of **+0.179 / +0.268 / +0.203** (ResNet10,
ResNet34, ResNet18_c100) where the model requires **-0.500**. This is at alpha0=1e-3, i.e.
steady state, and weightwise sign-agreement excess is 0.08-0.47% -- so independence *holds*
and the prediction *still* fails. **(2) CIFAR-100 gives granularity +47.6pp, and it does not
care about alpha0** (+47.59 at 1e-6, +47.64 at 1e-3), monotone in fineness: scalar 22 <
6-block 52 < layerwise 70. That is the second dataset the paper needed, and the largest,
most robust effect in the campaign. **The correction that reframes everything else:** in
`_apply_hier`, `r` is the RETENTION of the group-specific update -- **r=1 is plain layerwise
(verified: 90.863 +-0.063 vs 90.891) and r=0 is FULL pooling**. Cycles 16-19 quoted the M1
gain against r=0 while calling it the no-pooling control. Corrected, ResNet18/CIFAR-10 at
alpha0=1e-6 is **+2.40pp over no pooling** (a bigger number), but the ladder does not
transfer: r*=0.06 at ResNet18, r*>=0.1 at ResNet10, and on CIFAR-100 that same r=0.07 costs
**-43.7pp**. Never state a pooling claim without naming both the setting and alpha0.

## Running / next (cycle 20)  -- queue: alice 153, alice2 125 = 278 jobs
* **Six pooling ladders are in flight to map r\*(setting).** This is the live question: r\* is
  0.06 (ResNet18/C10), >=0.1 (ResNet10/C10), and >0.2-or-nonexistent (CIFAR-100).
  `rc100-*` (alice, 14, C100 @1e-3, **promoted to the queue front**), `rc6-*` (alice2, 14,
  C100 @1e-6), `rcg-*` (alice2, 9, C100 gap-fill r in {0.4,0.6,0.8}), `m1a3-*` (alice, 15,
  R18/C10 @1e-3), `r10b-*` (alice2, 15, R10 r in {0.08,0.15,0.3,0.4,0.6}).
* **`p6f-*` (alice, 9)** -- free-adaptation companion to `p4scale`: same nets/granularities
  with `HIER` **unset**, so groups diverge. `p4`/`p5` measured agreement under a COMMON beta
  (LAM=1.0); this closes that caveat.
* **`p5-*` (alice2, 12)** -- the alpha0=1e-6 probe ladder. Already queued; do NOT resubmit it.
* Still open: CIFAR-100 granularity is n=2 (effect is +47.6pp so n is not the constraint, but
  headline cells want n>=5); the §5 slope uses only the weightwise<->scalar endpoints, and a
  4-point regression needs `param_numels`, which the probe records but the reducer ignores;
  Axis 4's non-meta baseline is still uncorrected AdamW 91.894 (n=4), `fx-e300-*` queued.
* Deprioritised, unchanged: `mx-b*`/`mx-add-r007/8`/`zrn-*` (tier-3, Nice=6000-10000).

## Gotchas that cost hours — do not rediscover these
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
