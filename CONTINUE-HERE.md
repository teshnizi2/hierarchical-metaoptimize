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

## The state of the science, in one paragraph (rewritten cycle 19)
The **most defensible result is a refutation, and it now survives its own control**: the
sqrt(N) noise model predicts a log-log drift-vs-N slope of -0.500; measured **-0.110 at
alpha0=1e-6 and -0.136 at alpha0=1e-3**. But the *effect size* behind it is much smaller
than the headline says -- weightwise sign-agreement is **6.20% excess at alpha0=1e-6 and
only 0.38% at alpha0=1e-3** (16x collapse). **Never quote "53.1% agree on sign" without
saying alpha0=1e-6.** Cycle 19 found **the same alpha0 asymmetry in the method result**:
on ResNet18, granularity (layerwise-scalar) is +2.87pp at alpha0=1e-6 and **+3.50pp** at
alpha0=1e-3 (robust), but M1 pooling (additive-layerwise) is +2.62pp at alpha0=1e-6 and
only **+0.91pp** at alpha0=1e-3 -- **a 65% loss**. The pooling headline is an alpha0=1e-6
number; never quote it without naming alpha0. The **scale axis** is the emerging spine:
granularity buys **+19.88pp at ResNet10, +2.87pp at ResNet18**, and this is driven
**entirely by the scalar arm improving** (70.74 -> 87.82 -> 89.46 partial at ResNet34)
while layerwise stays flat (90.62 -> 90.69). So the parent paper's "granularity stops
helping at scale" is mechanically "**the scalar arm stops failing**". That whole ladder is
at alpha0=1e-6 and is now under its own control (`sa3-*`). CIFAR-100 has its **first four
rows** but at unequal epoch counts -- no cross-arm comparison is licensed yet.

## Running / next (cycle 19)  -- queue: alice 161, alice2 104 = 265 jobs
* **`sa3-*` (alice2, 18) is the decisive job of the campaign right now.** ResNet10 + ResNet34
  x {scalar, layerwise, additive r=0.06} x 3 seeds at **alpha0=1e-3**. The entire scale ladder
  is alpha0=1e-6, and `sc-ResNet10-scal` collapses to 70.74 (never reaches 85%, but *converged*
  -- plateau == final_test, so it is not an unfinished run). If that collapse is an
  escape-from-1e-6 artifact, the +19.88pp granularity gain at ResNet10 is too, and the scale
  trend dies. ResNet18's alpha0=1e-3 column already exists as `mx-a1e3-*` (verified an exact
  config match to `sc-ResNet18-*`), so those 9 sa3 jobs were cancelled as redundant.
* **`sc50-*` / `sc101-*` (alice, 24)** -- 4th and 5th rungs, ResNet50/ResNet101 x 3 arms x
  **both alpha0** x 2 seeds. The real axis is N (layerwise group count): R34 ~36 conv layers,
  R50 ~53, R101 ~104. Both alpha0 on purpose so they survive whichever way `sa3-*` lands.
  R101 omits `gpu-short` (needs >4h).
* **`sc-ResNet34-*` s3,s4 (alice, 6)** -- takes the now-headline ResNet34 row to n=5.
* **`p6-*` (alice2, 16)** -- M1 r-ladder at alpha0=1e-3, 100 ep, probe on for the full budget.
  Gives steady-state drift and plateau from the SAME runs. Still the best shot at the
  missing mechanism.
* **`p4-*` (alice, 12) / `p5-*` (alice2, 12)** -- agreement/drift vs granularity across
  {ResNet10, ResNet34, ResNet18_c100}. Question: is agreement a function of **N alone** or of
  **partition type**? This is what would JOIN the refutation to the scale axis -- if agreement
  at layerwise rises with scale, it explains why layerwise stops beating scalar.
* **Axis 2, CIFAR-100:** first four rows landed (layer 69.79 @100ep; add 60.75 @97ep;
  blk6 52.14 @82ep; scal 23.08 @83ep). **Unequal epochs -- compare nothing yet.** `c100-1e3-*`
  is at positions 16-23. Watch for pooling *inverting* on CIFAR-100.
* **Axis 4, non-meta baseline:** uncorrected AdamW 91.894 (lr 3e-4, n=4); `fxcos-*` supersedes.
* Deprioritised: `rc100-*` (Nice=3000, second-order refinement of an axis with no first-order
  result yet), `mx-b*`/`mx-add-r007/8`/`mx-h4-*`/`zrn-*` (tier-3, Nice=6000-10000).

## Gotchas that cost hours — do not rediscover these
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
