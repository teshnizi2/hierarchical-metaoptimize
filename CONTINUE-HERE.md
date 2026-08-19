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

## The state of the science, in one paragraph (rewritten cycle 16)
The **most defensible result is a refutation**: the sqrt(N) noise model fails direct
measurement — 53.1% of 11.17M per-weight meta-gradients agree on sign against a 50.0000%
null, and the predicted drift slope of -0.500 measures -0.113. Drift is set by coordinate
**agreement**, a property of the partition, not by N through sampling noise. The **best
positive result** is M1 additive pooling: a unimodal r-curve peaking at r~0.07 (93.21,
n=6) — **+2.29pp over no pooling** (r=1 == plain layerwise, gate-confirmed twice) and
**+1.01pp over maximal pooling** (r=0). Granularity itself interacts with the base
optimizer: a 3.84pp span under SGDm, a 0.15pp null under AdamW. All of it is
CIFAR-10 / ResNet-18 so far; model scale and CIFAR-100 are queued, not measured.

## Running / next (cycle 16)
* **Blocking a headline number:** `fxcos-*` (9 jobs, alice) — the non-meta AdamW baseline
  with its cosine schedule correctly scaled to 50k steps. The uncorrected baseline is
  91.894 (lr 3e-4, n=4); it was denied its decay and can only move **up**. **Quote no
  pooling-vs-baseline margin until these land.**
* **The headline's one untested confound:** `am4-*` (21 jobs, alice2) — the M1 r-curve at
  **alpha0=1e-4**. The whole §1 curve lives at alpha0=1e-6, which costs 14-25 epochs of
  arm-dependent startup. If the inverted-U flattens at 1e-4 the headline needs an alpha0
  qualifier or withdrawal.
* **Axis 1, model scale:** `sc-*` (36 jobs) — ResNet10/18/34 x {scalar, blocks, layerwise,
  additive} x 3 seeds. **ResNet10 is DONE (cycle 17)**; ResNet18 running, ResNet34 queued.
  Headline: granularity buys +19.9pp at ResNet10 vs +3.0pp at ResNet18, but **M1 pooling
  is a null at ResNet10** (+0.19pp, t=0.66). `r10-*` (24 jobs, alice2) sweeps r there to
  tell "pooling fails at ResNet10" apart from "r* moved".
* **Axis 2, second dataset:** `c100-*` (18 jobs) — CIFAR-100 at alpha0 {1e-6, 1e-3} x 4
  granularities x 2 seeds, plus `rc100-*` (14 jobs) the r-curve at alpha0=1e-3.
  Data is staged and integrity-checked on **both** accounts (cycle 17 verified alice2's
  md5 and build_network.py are identical to alice's — the earlier "alice2 lacks the
  patch" note was wrong, see FINDINGS cycle 17 §5).
* **Axis 3, n->5:** `mx-*` (89 jobs, both accounts) — M1 peak refinement r in
  {0.04..0.08}, batch-size axis {25,50,200}, H4 at n=5, alpha0 controls.
* **Axis 5, meta-optimizer:** `amx-*` (15 jobs, alice2) — Adam-meta additive at r
  {0, 0.05, 0.07}, n=5, on the SAME account as the Lion sweep, to break the
  meta-optimizer/account confound.
* **Throughput is cluster-capped, not queue-capped.** 2 genuinely free GPUs cluster-wide;
  229 of our jobs pending on `Priority`. Deepening the queue buys nothing; **re-ordering
  and widening partition eligibility is the only lever.**

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
