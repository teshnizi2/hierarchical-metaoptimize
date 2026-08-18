# Operational gotchas (hard-won)

## 1. Job progress is invisible unless output is unbuffered
Python block-buffers stdout when it is redirected to a file, so a *running* job's
`.out` file shows **zero epochs** no matter how far along it is; the buffer only
flushes when the process exits. Reading that as "the job is stalled" is wrong.

**Cost of learning this:** three healthy jobs were cancelled on a misdiagnosis
(~4 GPU-hours plus an hour of wall-clock).

**Fix (applied):** `run_cifar.sh` now sets `PYTHONUNBUFFERED=1` and runs `python -u`.

**Checking a running job's true progress:** read `PROBE_DIR/probe.jsonl` — the probe
opens, appends and closes each record, so it flushes immediately. `last_step / 500`
= epochs completed (batch size 100, 50k train images).

## 2. Compare wall-clock per epoch, not raw wall-clock
`analysis/aggregate.py` records `wallclock_min` and `epochs_done`; divide. Measured
on an L4: ~23–30 s/epoch for most arms, ~40 s/epoch for `scalar` (its
`beta_to_alpha` returns a NumPy float64 via `.cpu().numpy()` once per layer per
step, which costs host syncs). Not pathological, but it makes `scalar` the slowest
arm despite being the simplest.

## 3. Pin the GPU type for any comparison
Runs were scheduled across L4 and RTX 2080 Ti nodes. Accuracy is unaffected, but
timing comparisons are meaningless across types. Pin with
`--partition=gpu-l4-24g --gres=gpu:l4:1`.

## 4. Do not launch many jobs that extract the same dataset archive at once
Several jobs starting simultaneously in the same directory can race on the
torchvision extraction. Stage and extract once from a login node first.

## 5. The compute nodes have no internet
Datasets must be staged from a login node. `download=True` will hang, not fail fast.

## 6. `/tmp` is node-local and the login nodes round-robin — use shared storage for scripts

ALICE alternates between `nodelogin03` and `nodelogin04`. `/tmp` is **per-node**, so a helper
script `scp`-ed in one SSH session frequently does not exist in the next:

```
bash: /tmp/final_watch.sh: No such file or directory
```

This caused a string of "silent" failures where a command appeared to do nothing. Keep helper
scripts on the shared filesystem instead — `/data1/$USER/metaopt/bin/` — and never rely on
`/tmp` persisting between invocations.

Related: use `scp` **without** `-q` when transferring, or the failure is invisible.

## 7. Reading command output over this gateway

The SSH banner is printed on every connection and is ~18 lines. Piping through
`sed -n '/MARKER/,$p'` proved unreliable here; `2>&1 | tail -N` works. Prefer printing a unique
marker line first and tailing generously.

## 8. Every run must record its own environment — args alone are not provenance

`BETA_CLIP`, `HIER`, `LAM`, `ETA_RATIO` and `AUGMENT` are passed as **environment variables**
via `sbatch --export`, so they never appeared on the `ARGS:` line. Until 19 Aug 2026 no `.out`
file recorded them, which meant a finished run could not be told apart from an unguarded or
non-hierarchical one except by trusting its job name. `aggregate.py` silently reported
`augment=0` for 52 of 65 rows for the same reason.

**Fix (applied to both accounts):** `run_cifar.sh` now prints

```
ENV: AUGMENT=1 BETA_CLIP=-15:-2.3026 HIER=shrink LAM=0.1 ETA_RATIO=na
```

Anything configured by environment variable must be echoed there, or it is not measured.

## 9. `HIER=shrink`'s λ is a per-step rate — always quote its half-life

`β ← β − λ(β − β̄)` runs **every optimiser step**, so the pooling half-life is `ln2/λ` steps
against ~50,000 steps in a 100-epoch CIFAR-10 run:

| λ | half-life (steps) | effect over a run |
|---|---|---|
| 0.5 | 1 | full pooling |
| 0.1 | 7 | full pooling |
| 0.01 | 69 | full pooling |
| 1e-4 | 6,931 | genuinely partial |
| 1e-5 | 69,315 |effectively no pooling |

The first hierarchical sweep used λ ∈ {0.01, 0.1, 0.5} and therefore measured full pooling
three times over. **Quote λ with its half-life, or the sweep will not span what it claims to.**

## 10. The two accounts' code can silently drift apart

`alice2` was still running an unpatched `HF.py` (no `BETA_CLIP`, no `HIER`) long after `alice`
had both, so any guarded or hierarchical job submitted there would have run **unguarded and
non-hierarchical while reporting the right job name**. Nothing would have flagged it.

Before submitting to an account, check the feature is actually present:

```
ssh alice2 "grep -c 'PATCH_HIER\|PATCH_CLIP' ~/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10/Optimizers/HF.py"
```

`patches/HF_patched.py` in this repo is the canonical copy; push it to both and delete
`Optimizers/__pycache__` afterwards.
