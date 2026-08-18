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
