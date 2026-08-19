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

## The state of the science, in one paragraph (rewritten cycle 18)
The **most defensible result is a refutation, and it now survives its own control**: the
sqrt(N) noise model predicts a log-log drift-vs-N slope of -0.500; measured **-0.110 at
alpha0=1e-6 and -0.136 at alpha0=1e-3**. But the *effect size* behind it is much smaller
than the headline says -- weightwise sign-agreement is **6.20% excess at alpha0=1e-6 and
only 0.38% at alpha0=1e-3** (16x collapse), because much of the agreement is the shared
climb out of a 7-log-unit hole. **Never quote "53.1% agree on sign" without saying
alpha0=1e-6.** The **best positive result** is M1 additive pooling: a unimodal r-curve whose
plateau region r in [0.05, 0.07] reaches **93.09-93.31** (n=3-8) vs **90.86 at r=1** (plain
layerwise, gate-confirmed) and **92.23 at r=0** (full pooling). It has **no measured
mechanism** -- drift is flat across the whole r-ladder where accuracy moves 2.44pp.
Granularity interacts with the base optimizer (3.84pp span under SGDm, 0.15pp null under
AdamW) and with **scale**, in opposite directions: granularity buys +19.88pp at ResNet10
but +2.87pp at ResNet18, while pooling buys +0.19pp at ResNet10 and +2.62pp at ResNet18.
ResNet34 is running and decides whether that is a trend. CIFAR-100 has **no usable data
yet** -- it was queue-starved, not blocked, and is now unblocked.


## Running / next (cycle 18)  -- queue: alice 124, alice2 99 = 223 jobs
* **Queue ORDER is the lever, not depth.** Cluster is contended; ~11-12 of our jobs run at a
  time. Axis 2 (CIFAR-100, 33 jobs) had sat at positions **73-105 of 105** for four cycles
  behind tier-3 refinement and had therefore produced nothing. Users cannot raise their own
  priority but **can lower it**: `scontrol update JobId=<j> Nice=<n>`. After demoting tier-3,
  c100 moved to 24-55 and `sc-ResNet34` from 62 to 16 (3 promptly started).
  **Check queue POSITION every cycle, not just depth.**
* **Decides the headline's last confound:** `p6-*` (16 jobs, alice2) -- the M1 r-ladder at
  **alpha0=1e-3, 100 ep, with the probe on for the full budget**. Gives steady-state drift and
  plateau from the SAME runs, so it tests both the missing mechanism and whether the
  inverted-U survives at alpha0=1e-3. The whole cycle-16 curve is alpha0=1e-6.
* **The theoretical core, extended:** `p4-*` (12, alice, alpha0=1e-3) and `p5-*` (12, alice2,
  alpha0=1e-6) -- {ResNet10, ResNet34, ResNet18_c100} x {scalar, layerwise, nodewise,
  weightwise}, 20 ep. With ResNet18's existing p2/p3 this completes a 4-architecture x
  2-alpha0 grid. **Question:** is agreement/drift a function of **N alone** or of the
  **partition type**? layerwise spans N=38/62/110 across nets while layerwise->nodewise jumps
  ~200x, which separates the hypotheses.
* **Axis 1, scale:** `sc-ResNet34-*` running. ResNet10 and ResNet18 are done (numbers above).
* **Axis 2, CIFAR-100:** `c100-*` (18) + `rc100-*` (14), unblocked this cycle, data staged and
  verified on both accounts. Still **zero** usable rows -- treat any c100 claim as unmeasured.
* **Axis 4, non-meta baseline:** uncorrected AdamW is 91.894 (lr 3e-4, n=4); the cosine-corrected
  `fxcos-*` supersedes it. **Quote no pooling-vs-baseline margin until those land.**
* Deprioritised on purpose (tier-3): `mx-b*` batch-size axis, `mx-add-r007/8`, `mx-h4-*`, `zrn-*`.


## Gotchas that cost hours — do not rediscover these
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
