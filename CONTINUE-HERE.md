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

## The state of the science, in one paragraph
Granularity in MetaOptimize buys **convergence speed** and **stability**, and converts into final
accuracy only when the budget is too short for the coarser arm to catch up — which explains the
parent paper's own unexplained ImageNet null (§7.3). Partially pooling the per-group step sizes
beats every fixed granularity (+1.46pp on layerwise) and is insensitive to the pooling strength
across three orders of magnitude. The per-weight collapse is a float32 overflow and a
rediscovery of a guard published in 1992/2012/2024; a real ~12pp deficit survives the fix.

## Running / next
* **DONE — the 36-cell `zsw` sweep completed (cycle 12).** Meta-gradient-space pooling has **no
  interior optimum**: on layerwise the unpooled endpoint r=1 wins on both accuracy (91.35) and
  speed (28.7 ep→85). On weightwise any r<1 prevents the collapse (88.1-88.4 vs 79.35) but never
  beats scalar by more than +0.36pp. **The layerwise interior is confounded** — it runs at 3-35x
  smaller step size (see FINDINGS cycle 12 §2 and gotcha 30); quote the endpoints only.
* **In flight:** `zrn-*` (30 jobs, alice2/2080ti) fills the unsampled r in (0.7, 1) and locates
  the weightwise collapse threshold, currently bracketed only as sd(beta) in (0.167, 0.802).
  Self-anchoring, so it carries its own endpoints.
* **In flight:** `zm0-*` (7 jobs, alice/2080ti) — identity gate for the new `zmpool` operator
  (mean-normalised pooling; holds the common mode exactly fixed so r is a pure pooling axis).
  **Do not launch the `zmp` ladder until this gate passes.**
* Then: the `zmp` ladder on L4 (same hardware as `zsw`, so the two operators are comparable);
  seeds -> 5 on headline cells; CIFAR-100 as the second dataset; finish the draft.

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
* ImageNet on `/data1` is **489 of 1000 classes** — scoped out; do not train on it and call it
  ImageNet.

## Standing instruction
Full autonomy was granted: decide and act, do not ask permission. The one thing that genuinely
needs the account holder is ImageNet credentials (and it is already scoped out).
