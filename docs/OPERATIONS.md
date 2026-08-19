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

## 11. TinyStories — staged, with one portability defect fixed

`tinystories.py` had `DATA_CACHE_DIR` **hard-coded to the authors' Compute Canada path**
(`/home/asharif/projects/def-sutton/...`), which does not exist on ALICE, so the task would have
failed on first run. It is now environment-overridable:

```python
DATA_CACHE_DIR = os.environ.get("TINYSTORIES_DATA", "/data1/salehkaleybars/metaopt/data/tinystories")
```

Staged on `alice` (login nodes have internet; compute nodes do not — see gotcha 5):
`data/tinystories/TinyStories_all_data/` — **50 shards, 6.97 GB**, receipt in `STAGED.txt`.

**THREE things remained before TinyStories could run** (was two; the third was found 19 Aug 2026).
**Two are now cleared; the optimizer port is the only one left.**
1. **Pretokenization has not been done** and must be a Slurm CPU job, not a login-node job.
2. **`tinystories/HF.py` is a SEPARATE COPY** of the optimizer and carries **neither the
   `BETA_CLIP` guard nor the `HIER` hierarchy patch** — both live only in `cifar10/Optimizers/HF.py`.
   Porting them is a prerequisite for any guarded or hierarchical language-modality run, and a
   run launched without the port would silently be plain and unguarded (see gotcha 10).

3. **`sentencepiece` was missing from the venv** — `tinystories.py pretokenize` and `tokenizer.py`
   both import it and it was never installed. Fixed 19 Aug 2026 with
   `pip install --no-deps sentencepiece` (0.2.2) into `envs/mo`; `--no-deps` so that nothing the
   ~85 in-flight CIFAR jobs depend on could be upgraded underneath them. Pretokenization is now
   **DONE** (job 4680828, `bin/ts_pretok.sh`, cpu-short, 16 cores, ~6 min): vocab_size=0 → the
   shipped Llama-2 tokenizer, `.bin` written beside each `.json`, which is what `train.py`'s
   `vocab_source="llama2"` path globs for. **Receipt: 50/50 `.bin` shards, tree now 8.5 GB,
   `PRETOK_DONE`, no traceback.** Blocker 1 is cleared.

### Correction to blocker 2 — the port is bigger than "add the guard and the hierarchy"

`tinystories/HF.py` is 267 lines against `cifar10/Optimizers/HF.py`'s 444, and they differ by 232
diff-lines. Inspecting it directly:

```python
self.stepsize_type = stepsize_groups if stepsize_groups in ['scalar','layerwise','nodewise','weightwise'] else 'blockwise'
...
if   self.stepsize_type == 'scalar':    self.beta = [...]
elif self.stepsize_type == 'blockwise': self.beta = [...]
self.len_beta_list = len(self.beta)     # <-- AttributeError for layerwise/nodewise/weightwise
```

`self.beta` is assigned **only** on the `scalar` and `blockwise` branches, so any of the three fine
granularities raises `AttributeError` on the very next line. **The dead-granularity defect is present
in the language-modality copy too, independently of the CIFAR-10 one.**

This matters twice over:

* **For the port.** TinyStories needs *all three* of our patches — granularity (`patch_hf2.py`),
  guard, hierarchy — re-derived against a substantially different file, not two patches copied over.
  That is a validation-gated change (PLAN §5), so it was **not** done autonomously: shipping an
  unvalidated optimizer port is precisely the failure mode PLAN §5 exists to prevent.
* **For the paper.** The released code advertises `layerwise`/`nodewise`/`weightwise` in the argument
  parser of **both** task copies and can execute them in **neither**. The defect is systematic, not a
  slip in one file, which is a materially stronger version of the reproduction finding.

## 12. An over-provisioned `--time` silently locks a job out of the idle partition

`gpu-short` has a **4:00:00** cap and is the only GPU partition that is regularly idle —
it holds a mix of 2080ti/L4/A100 nodes that the dedicated partitions do not drain. A job
asking for more than 4 h can never be placed there, however empty it is.

The `a0h-*` α₀ control (15 jobs) was submitted with `--time=5:00:00` against a **measured
89-minute** 100-epoch 2080ti run — a 3.4× over-provision — and sat pending at the bottom of a
46-deep queue behind two 2080ti nodes in `maint`. Cutting the limit to `3:45:00` (still 2.5×
headroom over the slowest run ever recorded) and setting
`Partition=gpu-2080ti-11g,gpu-short` started **five cells within seconds**.

**Rules:**
* Size `--time` from `wallclock_min` in `results/all_runs.csv`, not from a round number.
  100 epochs ≈ 40 min on L4, ≈ 90 min on 2080ti.
* Submit GPU work multi-partition — `--partition=<dedicated>,gpu-short` — so Slurm takes
  whichever frees first.
* Keep `--gres=gpu:<type>:1` pinned when doing so. The partition list may widen; the **GPU
  type must not**, or timing comparability inside the block is lost (gotcha 3). `gpu-short`
  is heterogeneous, so an unpinned `--gres=gpu:1` there will hand out whatever is free.

`scontrol update jobid=<id> TimeLimit=... Partition=...` does all of this on already-pending
jobs — no cancel, no resubmit, job IDs and names preserved.

## 13. The concurrency cap is per *partition*, NOT per GPU type — and `gpu-short` has its own

> **CORRECTED 19 Aug 2026 (cycle 5). The original version of this gotcha said the caps attach to
> GPU types and are additive. They attach to PARTITIONS. Acting on the wrong model silently
> halved both accounts' effective allowance for a full cycle.** The corrected rule is below; the
> original text is kept after it because the *numbers* were right and only their owner was wrong.

Read the caps directly rather than inferring them from behaviour:

```
sacctmgr -n show qos format=Name%20,MaxTRESPU%40
```

| QOS | partition | cap |
|---|---|---|
| `qos-short-gpu` | `gpu-short` | **gres/gpu=12, shared across every GPU type in it** |
| `qos-gpu-l4` | `gpu-l4-24g` | gres/gpu=8 |
| `qos-gpu-2080ti` | `gpu-2080ti-11g` | gres/gpu=12 |
| `qos-gpu-a100` | `gpu-a100-80g` | gres/gpu=2 |
| `qos-gpu-mig` | `gpu-mig-40g` | gres/gpu=8 |

**The trap.** Gotcha 12 says to submit multi-partition (`--partition=<dedicated>,gpu-short`) so
Slurm takes whichever frees first. Do that to *everything* and Slurm places nearly all of it in
`gpu-short`, where a single 12-GPU cap now governs your L4 and 2080ti jobs **together**. The two
allowances you thought you were adding (8 + 12 = 20) collapse into one 12.

`alice2` on 19 Aug 2026: **12 running (7 L4 + 5 2080ti), all in `gpu-short`, all 17 pending jobs
`QOSMaxGRESPerUser`** — while its `gpu-2080ti-11g` (12) and `gpu-l4-24g` (8) allowances were
*completely* unused. It was not out of allowance; it was queued entirely inside the wrong one.

**The fix, and how to confirm it worked.** Move a self-contained block to the dedicated partition
*only*, then read the pending reason — that is the diagnostic, not the job count:

```
scontrol update jobid=$jid Partition=gpu-2080ti-11g
squeue -h -j $jid -o '%i %j %T %r %P'
```

`QOSMaxGRESPerUser` → `Priority` means the job went from *cannot start whatever frees* to
*eligible, waiting for a node*. That flip is the whole point.

**Keep some jobs dual-partition.** If you move every pending job off `gpu-short`, nothing
backfills the `gpu-short` slots your own running jobs release. Split the block — dedicated-only
up to the dedicated cap, the remainder left dual.

**`QOSMaxGRESPerUser` vs `Priority` is the reading that matters.** The first is a cap you can
often route around in one `scontrol` call; the second means the cluster is genuinely full and
nothing but waiting helps. Do not treat them as the same "pending".

GRES must stay pinned to its original type throughout (gotcha 3) — only partition *eligibility*
changes, so within-block timing comparability is untouched, and no cancel or resubmit is needed.

### Original text (numbers correct, attribution wrong)

Caps are 2× A100 / 8× L4 / 12× 2080ti **per user** — these are the *dedicated-partition*
caps. An account whose jobs are all
`gpu-l4-24g` saturates at 8 and stops, with the 2080ti allowance completely unused —
which is exactly where `alice2` sat (26 jobs, all L4, 8 running, 18 pending).

Moving a **self-contained family** of pending jobs onto the other type draws on the other
cap and runs them in parallel with the L4 work. Move whole comparison blocks, never a
subset, or the block ends up split across GPU types.

**Do the GRES change first and verify it took, then the partition** — a job left asking for
`gpu:l4:1` inside `gpu-2080ti-11g` is valid to submit and will simply never schedule:

```
scontrol update jobid=$jid TresPerNode=gres:gpu:2080_ti:1
squeue -h -j $jid -o '%b'          # must show 2080_ti before touching Partition
scontrol update jobid=$jid Partition=gpu-2080ti-11g,gpu-short
```

Applied to the six `g4-sgdmLion` cells, this took `alice2` from 7 running to 8 with the
2080ti allowance now working in parallel; combined with the `a0h` fix, total running jobs
across both accounts went **10 → 16**.

## 14. `nice` deprioritises without discarding

`scontrol update jobid=<id> nice=5000` pushes a job down the queue but leaves it queued, so
redundant-but-not-worthless work still runs once the valuable work drains. Prefer it to
`scancel` whenever the job would be worth having eventually — 17 jobs (λ-plateau re-measures
and scale smokes) were deprioritised this way rather than cancelled.

## 15. Audit a job block with `sacct`, never with `squeue | tail`

Reading a queue through the SSH gateway means tailing (gotcha 7), and `tail -N` on a deep queue
silently drops the rows above the cut. On 19 Aug 2026 a `squeue -u ... | tail -40` against a
31-deep queue appeared to show that **9 of the 20 `a0h` cells — the campaign's decisive
experiment — had vanished**, i.e. failed or been cancelled without a trace. They had not: all 20
were `PENDING`, just above the tail cut.

The near-miss was resubmitting nine duplicate jobs onto a saturated cluster.

**Fix:** audit a named block by name, with the state column, over a bounded window:

```
sacct -u $USER -S 2026-08-17 --format=JobID%12,JobName%22,State%14,Elapsed,ExitCode,Partition%16 -X | grep -E '<prefix>|JobName'
```

`sacct` shows completed, failed and cancelled jobs too, which `squeue` cannot — so it answers
"is this block intact?" and `squeue` never can, at any tail depth.

## 16. The A100 and MIG allowances are not spare capacity — check `AllocTRES`, not `sinfo` state

`sinfo` reports A100 and MIG nodes as `mix`, which reads as "partially free", and neither
account had ever submitted to them — so they looked like an untapped pool worth moving a block
onto. They are not. Per-node `AllocTRES` shows every A100 node at full `gres/gpu` allocation
and `gpu-mig-40g` with exactly **one** free slice across six nodes.

`mix` means *some resource* on the node is free — usually CPU or memory — and says nothing
about whether a **GPU** is. A GPU job placed on a `mix` node with zero free `gres/gpu` simply
queues forever.

**Check before targeting a partition:**

```
scontrol show node <node> | tr ' ' '\n' | grep -E 'CfgTRES|AllocTRES'
```

and compare `gres/gpu=` on the two lines. Equal means full, whatever `sinfo` says.

**Standing conclusion (19 Aug 2026): every GPU partition on ALICE is saturated.** Throughput is
bought by queue *ordering* — right-sized `--time` into `gpu-short` (gotcha 12), the additive
per-GPU-type caps (gotcha 13), and `nice` on low-value work (gotcha 14) — never by submitting
more jobs.

## 17. The ±0.02pp determinism floor does NOT transfer to epochs-to-target

Two runs with **identical config and identical seed**, differing only in GPU type (and therefore
in cuDNN autotuning), on the campaign's PRIMARY metric:

| arm | best | ep→90 |
|---|---|---|
| layerwise **+ shrink λ=0.1** (L4 vs 2080ti) | 92.55 / 92.53 | **42 / 42** |
| layerwise **plain** (L4 vs 2080ti) | 91.37 / 91.28 | **57 / 51** |

Accuracy reproduces to 0.02–0.09pp on both, as gotcha-free replication predicts. But the plain
arm's epochs-to-90% differs by **6 epochs** while the pooled arm's is exact.

**Cause:** the plain arm's asymptote is 90.83 ± 0.13, so the 90% threshold is drawn *through its
own plateau*; it sits inside [89,91] for **51 of 100 epochs**. The pooled arm plateaus at 92.27
and is in that band for **4**. A sub-0.1pp wobble therefore moves the crossing epoch by several
epochs on one arm and not at all on the other.

**Rules:**
* Before using a threshold, compute each arm's plateau (mean test accuracy over the last 20
  epochs) and confirm the threshold is **below** it. A threshold inside an asymptote measures
  noise, not speed.
* Quote ep→85 / ep→88 / ep→90 together, never one alone — under Lion the pooling effect
  *changes sign* between 85% and 90% (FINDINGS, cycle 4 second pass §3).
* Judge an effect in epochs against the arm's own threshold jitter, not against the ±0.02pp
  accuracy floor. At 88% (below every layerwise plateau) both Adam-meta arms have **zero** seed
  variance; at 90% the plain arm has ±5.6.


## 18. The plateau and band columns are emitted, so the threshold check cannot be skipped

Gotcha 17 made "check the threshold against every arm's plateau before quoting it" a rule to
remember. `analysis/aggregate.py` now emits it as data on every run:

* **`plateau`** — mean test accuracy over the last 20 epochs (blank under 20 epochs);
* **`ep_in_band_90`** — epochs spent inside [89, 91].

**Read them before quoting any epochs-to-target number.** A large `ep_in_band_90` means the
threshold is drawn through that arm's own asymptote and its crossing epoch is noise; a `plateau`
below the threshold means the metric is undefined for that arm and no amount of seeds will fix
it.

Worked example from the `a0L` block: plain layerwise has `ep_in_band_90` of 46–58 out of 100 at
every α₀, the shrink arm has 4–9, and the SGDm scalar arm has **0** with a plateau of 87.7 — so
ep→90 measures noise on the first arm and does not exist on the third. The comparison has to
move to 85%, which sits below all four plateaus.

## 19. Check the TRAIN accuracy column before calling any result asymptotic

The campaign spent four cycles explaining the parent paper's ImageNet null as a budget artifact
and then very nearly published two headline claims carrying the same artifact.

At epoch 100, on runs whose *test* curve is flat and looks converged:

| arm | train @ 100 | Δtrain / 10 ep | train ≥ 99% |
|---|---|---|---|
| SGDm+Lion scalar | 93.7–94.0 | **+0.3 to +0.46** | never reaches 97% |
| layerwise + shrink λ=0.1 | 97.8–98.2 | **+0.22 to +0.37** | **never** |
| layerwise plain | 99.7 | +0.16 | epoch 58–70 |

A flat *test* curve does not mean the run converged — it means the test curve converged. If the
*train* curve is still climbing, the run was stopped mid-optimisation and any statement of the
form "arm A plateaus below arm B" is a statement about the budget, not the method.

**Rule: before writing "plateau", "asymptote", "ceiling" or "converged", check `final_train` and
its last-20-epoch slope. If train is still rising, the honest claim is bounded by the budget, and
the fix is a longer run — not more seeds.**

Cheap here, because `train.py` has **no learning-rate scheduler**: the only epoch-dependent terms
in the training loop are the loop bound and the time-based break (neutralised by
`--max-time 999:00:00`). So a 300-epoch run's first 100 epochs are bitwise the same computation
as the 100-epoch run, and the extension reads as a continuation rather than a new experiment.
Verify this before extending any *other* task — it is a property of this code, not a general one.

## 20. A "granularity" arm is not defined by its `--stepsize-groups` flag

`--stepsize-groups layerwise` with `HIER=shrink LAM=1.0` gives the base optimiser **one** step size
for the whole network, not 62. `_apply_hier()` runs after `meta_update()` and before the next
step's `beta_to_alpha()` (HF.py `step()`), so the pooling has already collapsed β by the time any
α is read. At λ=0.1 the half-life is 7 steps, so the same is true after the first ~1% of the run.

For a full cycle the campaign compared "scalar vs layerwise+shrink" believing it was varying the
number of step sizes. It was not: both arms use one. The variable that actually differed was the
number of meta-gradient estimates pooled into it (1 vs 62) — see FINDINGS cycle 6 §1.

**Rule: every arm must be recorded with BOTH numbers —**

| | # step sizes the base opt uses | N meta-grad estimates pooled |
|---|---|---|
| `scalar` | 1 | 1 |
| `layerwise` plain | 62 | 62 |
| `layerwise` + `HIER=shrink LAM≥0.01` | **1** | 62 |
| `weightwise` + `HIER=shrink LAM≥0.01` | **1** | 11.17M |

They coincide only when `HIER` is unset. Any table with a single "granularity" column is
ambiguous between the two and cannot support a causal claim about either.

**Corollary — the λ sweep never tested partial pooling.** Every λ run on layerwise (0.001 … 1.0)
has a half-life ≤ 693 steps against ~50,000, so all of them are full pooling (gotcha 9). Use
`HIER=additive` with `ETA_RATIO` when a genuinely interior pooling strength is wanted: it rescales
the per-group deviation of every realised update for the whole run and does not saturate.

## 21. `HIER=shrink` and `HIER=additive` are NOT two settings of one knob

Both operators were designed as "pooling strength" dials and have been swept as if λ and
`ETA_RATIO` were interchangeable. They are not. Read `_apply_hier()` in `patches/HF_patched.py`
(both the layerwise branch and the global weightwise/nodewise branch):

```
M0 shrink  : β ← β − λ·(β − mean(β))
M1 additive: β ← β_prev + dm + r·(d − dm),   d = β − β_prev,  dm = mean(d)
             ⇒ mean(β_new) = mean(β_prev) + dm,  EXACTLY independent of r
```

**Additive has no direct channel to the shared β's drift rate — it varies only the spread.
Shrink varies both.** So the two ladders answer different questions, and a result that reproduces
across them is a *spread* result, while one that appears only under shrink is a *drift* result
(FINDINGS cycle 7 §2 uses exactly this to separate them).

Two riders:
* The invariance is per-step given identical state. Over a trajectory r changes the spread → the
  base updates → the next `d`, so *realised* drift can still differ. Measure it (`PROBE=100`,
  `beta_true_min/max`), do not assume it.
* **The `BETA_CLIP` clamp runs AFTER `_apply_hier`** (`step()`, lines 86–90), so a binding clip
  breaks mean-preservation by truncating the bottom of the distribution. `p2-lay-plain` sits pinned
  at the −15 floor with a spread of 8.7, so at large spread this is not hypothetical.

Corollary for sweep design: quoting a λ half-life (gotcha 9) tells you when *shrink* saturates and
says nothing about additive, which is genuinely partial for the whole run at every r.

## 22. The probe's `snr` column changes meaning with granularity — do not compare it across arms

`_probe()` builds its per-group vector two different ways:

```python
if self.stepsize_type in ('scalar', 'layerwise', 'blockwise'):
    zv = z[0].reshape(-1)                       # one entry per real group
else:
    zv = stack([zi.mean() for zi in z])         # one entry per TENSOR (62), not per group
```

For `nodewise` and `weightwise` the `beta`, `z_mean`, `z_std` and `snr` lists are therefore
**per-tensor means over the 62 parameter tensors**, not per-group quantities — which is why
`p2-w-L1p0` reports a *high* median SNR (1.12) despite having 11.17M groups. `snr` is also a
**temporal** ratio (`_z_sum` / `_z_sqsum` accumulate over steps), not a within-group spatial one.

Two columns are safe to compare across every arm because they are computed over the full
coordinate set: **`frac_neg`/`frac_zero`** (built from `zall`, all coordinates) and
**`beta_true_min`/`beta_true_max`** (true extremes over every β tensor). Cycle 7 §1 uses only
those. Cycle 6 §2's per-group SNR table was scalar/6-block/layerwise only, so it stays valid.

## 23. Dual-partitioning does not create capacity when the GPU *type* is cluster-saturated

Gotcha 13 says to draw on `gpu-short`'s separate 12-GPU cap by dual-partitioning. That works only
when the bottleneck is your own QOS cap. It does nothing when the bottleneck is the hardware.

`gpu-short`'s L4 nodes **are the same physical nodes as `gpu-l4-24g`** — node880/881/882/885, four
nodes × 4 GPUs = **16 L4 GPUs in the entire cluster**. Adding `gpu-short` to an `--gres=gpu:l4:1`
job widens *eligibility*, not *supply*. On 19 Aug 2026 the `zv-*` identity block flipped correctly
from `QOSMaxGRESPerUser` to `Priority` (the gotcha-13 diagnostic), started one job, and then stalled
— because all 16 L4 GPUs were allocated and only 2 of them were ours.

**Read the reason code together with the hardware census, not either alone:**

```
squeue -h -j $jid -o '%r'                                   # QOSMaxGRESPerUser vs Priority
for n in node880 node881 node882 node885; do                # is the TYPE actually free?
  scontrol show node $n | tr ' ' '\n' | grep -E 'CfgTRES|AllocTRES'
done
```

`QOSMaxGRESPerUser` → route around it with `Partition=`. `Priority` **plus** `CfgTRES == AllocTRES`
on every node of that type → nothing you can do with partitions; the only levers are freeing your
*own* running jobs, or moving the block to a different GPU type (whole block at once, gotcha 3).

**Corollary:** when a small gating block is stuck behind a saturated type, the cheapest fix is
usually to cancel one of *your own* long-running jobs whose result is already known to be
superseded — a slot you release is a slot you can immediately re-take, whereas a queue position
behind other users is not something you can shorten.

## 24. Never quote a granularity comparison at short horizon and small α₀ — it measures the startup transient

At α₀=1e-6 the log step size starts at ln(1e-6) = −13.8 and must climb to its operating point
(β ≈ −6 to −6.5). The finer the partition, the longer that climb takes, so at short horizon most of
what the number measures is the startup cost. Measured at 20 epochs (FINDINGS cycle 8 §4):

| arm | α₀=1e-6 | α₀=1e-3 | Δ |
|---|---|---|---|
| scalar | 70.73 | 84.16 | +13.4 |
| layerwise + pool | 53.14 | 88.34 | +35.2 |
| nodewise + pool | 33.03 | 83.77 | +50.7 |
| weightwise + pool | 14.80 | 77.46 | **+62.7** |

The spread across {scalar, 6-block, layerwise} collapses from **21.2pp to 4.2pp** purely by moving
α₀. Weightwise goes from 55.9pp behind scalar to 6.7pp behind.

**Rules:**
* Any 20-epoch probe at α₀=1e-6 is a *mechanism* probe (drift, spread, sign statistics) and its
  accuracy column is not a granularity result. Do not put it in a table next to 100-epoch numbers.
* At **100** epochs the confound is gone — every arm is flat to ≤0.38pp across α₀ ∈ {1e-3, 1e-4,
  1e-6} (cycle 8 §3) — so the headline grid does *not* need re-running at a larger α₀.
* If a short probe is needed, run it at α₀=1e-3, which starts essentially at the destination.

## 25. An identity check must be run where the arms it distinguishes are DISTINGUISHABLE — verify that first

The `zv-*` block was built to gate every per-weight claim in the paper: it checks that
`HIER=zpool` at `ETA_RATIO=0` reduces *exactly* to the scalar arm. All 7 jobs completed and every
arm agreed to ~0.03pp. Read casually that is a pass. It is worthless.

The block ran **4 epochs at α₀=1e-6**, where the step size has barely left ln(1e-6) and nothing has
trained. Every arm sat at ~13% against a 10% chance baseline — *including the two reference arms
that are supposed to differ*:

| pair | 4 ep @ α₀=1e-6 | 20 ep @ α₀=1e-6 | 100 ep |
|---|---|---|---|
| scalar vs weightwise | **0.02pp** | 55.9pp | 8.7pp |

A test that cannot separate `scalar` from `weightwise` cannot certify that `weightwise + zpool(r=0)`
*equals* `scalar`. Both a correct implementation and a completely broken one produce the same
output. The configs were fine — the `ENV:` lines (gotcha 8) confirmed every variable propagated —
so nothing downstream would have flagged it.

**Rule: every identity/equivalence check ships with a discriminating-power anchor, evaluated
BEFORE the identity, and the checker refuses to report a verdict if the anchor fails.**

```
# anchors that MUST differ; if they don't, the regime is void and nothing else may be read
pow = |ref_A - ref_B|
if pow < threshold:  print("TEST VOID"); exit
# only now compare the pairs that must MATCH
```

Corollaries:
* Pick the regime from a **measured** separation, not from cost. `z3-*` runs at α₀=1e-3 / 20 epochs
  because `p3-*` had already recorded an ~11pp spread across those exact arms there.
* Cheap and early is the wrong instinct for an identity test. The failure mode of running it too
  early is a *false pass*, which is worse than no test — it retires the question.
* Prefer the direct quantity where one exists. Accuracy is a proxy; `PROBE=100` gives the β
  trajectories, which is what the identity is actually about.

## 26. On the additive ladder, n=2 cannot rank cells ~0.1pp apart — it has already failed twice

Cycle 8 §1 read the M1-additive peak as a tie between r=0.03 (93.01 ± 0.17) and r=0.1
(93.02 ± 0.01), both at n=2, and designed the next block around separating them. Taken to n=5:

| cell | n=2 reading | n=5 reading | shift |
|---|---|---|---|
| r=0.03 | 93.01 ± 0.17 | 92.96 ± 0.15 | −0.05 |
| r=0.1 | 93.02 ± **0.01** | 92.86 ± 0.19 | **−0.16** |

Both fell, and the "tie" resolved to r=0.03 by 0.10pp — i.e. **the n=2 ranking was wrong, not
merely imprecise**. Note that r=0.1's n=2 sd was 0.01pp, ~20× tighter than its true n=5 sd of
0.19: two seeds that happen to agree produce a *confidently* wrong error bar, which reads as the
most trustworthy cell on the ladder rather than the least.

**Rules:**
* Any ranking of additive cells whose accuracies are within ~0.3pp requires **n=5**. The ±0.02pp
  determinism floor (FINDINGS, reproducibility) is irrelevant here — seed variance on this ladder
  is ~0.15–0.20pp, an order of magnitude larger.
* **Never read a tight sd at n=2 as precision.** With two samples the sd is one number's distance
  from another; it carries no information about the population spread.
* State a ladder's *shape* (one maximum, in this interval, of this height) at low n and its
  *argmax* only at n=5. Cycle 9 §1 is written that way deliberately.

## 27. "Cancelled" in the write-up is not evidence the jobs are gone — re-read the queue

FINDINGS cycle 8 §7 records the void `z2-*` identity block as "**cancelled before it ran**". At the
start of cycle 9 all six were still `PENDING` — and queued *ahead of `z3-*`, the block written to
replace them*. The write-up recorded an intent, the `scancel` never landed, and nothing in the
queue or the docs flagged the discrepancy for a full cycle.

**Rule: a queue action is not done until its post-state is read back.** Every reprioritise/cancel
script in `bin/` now ends by printing the affected jobs' state (`squeue -h -o '%i %j %T %r %y %P'`),
so the receipt is in the same output as the action. When a write-up says a block was cancelled,
confirm with `sacct` (gotcha 15) — it shows `CANCELLED` explicitly, which `squeue` silence does not.

## 28. A sweep measured on one GPU type must be read only against itself

`zsx-*` runs on 2080ti; `zsw-*`, and essentially every other block in this campaign, runs on L4.
Differencing a `zsx` number against an L4-measured number silently mixes a hardware term into an
effect size (gotcha 3 is about timing; this is about *accuracy*, which the ±0.02pp determinism
floor does not bound across GPU types because it was only ever measured *within* one).

A sweep is safe to relocate to a different GPU type **only if it carries its own anchors**. The
zpool sweep does: `r=0` is exactly the scalar arm and `r=1` is exactly the plain per-group arm
(both identities verified — FINDINGS cycle 10 §1), so every contrast it makes is internal.

```bash
# a relocated block must contain its own endpoints. Check before submitting:
#   does the sweep include the arms it will be compared against?  if not, do not relocate it.
```

The corollary bit the `ad-l-r007` s3–s4 cells this cycle: they are members of an all-L4 ladder
resolving a **0.12pp** difference, so they were deliberately left queued on the saturated L4 pool
rather than run sooner on 2080ti. Waiting is cheaper than an uninterpretable number.

## 29. An empty `AllocTRES` does NOT mean the node is free — read `State` in the same breath

Gotcha 16 said to check `AllocTRES` rather than `sinfo` state. That is right for the question
"is this GPU in use?" and **wrong on its own** for "can I run here?". This cycle three 2080ti
nodes reported a completely empty `AllocTRES`:

```
NodeName=node854  AllocTRES=
NodeName=node856  AllocTRES=
NodeName=node857  AllocTRES=
```

which reads as 12 idle GPUs. They were not idle, they were **unavailable**:

```
$ sinfo -h -n node854,node855,node856,node857 -o '%N %T %G %C'
node857 drained$   gpu:2080_ti:4  0/0/48/48
node[854,856] maint gpu:2080_ti:4 0/96/0/96
node855 allocated  gpu:2080_ti:4  48/0/0/48     # 1 GPU free, but 0 free CPUs
```

`node857` was `drained` for `GPU fail`, `node854`/`node856` were in `maint`, and `node855` had a
free GPU but no free CPU to pair with it. Empty allocation and unusable are the same string.

**Always join the two:**

```bash
sinfo -h -N -p <partition> -o '%N %T'        # state:  idle / mixed / allocated / drained / maint
scontrol show node | grep -A1 'Gres=.*l4'    # alloc:  AllocTRES
# free == state in {idle, mixed} AND AllocTRES gres < CfgTRES gres AND CPUs remain
```

The failure mode is not wasted jobs — Slurm just queues them — it is **a wasted decision**. A
"there are 13 idle GPUs over there" reading nearly moved the headline sweep onto hardware that
did not exist. State the capacity claim with the state column attached, or do not state it.

## 30. An interpolation with exact endpoints can still have a garbage interior — check the COMMON MODE

Both `zpool` endpoints are exact identities, verified numerically twice (cycle 9 β-uniformity,
cycle 10 accuracy gate). That certified the endpoints and **nothing else**. The interior turned
out to sweep the realised step size over a factor of 35 (cycle 12 §2), because

    z'_b = (1-r)*sum_j(z_j) + r*z_b     =>     mean_b(z'_b) = (1-r)*m*z̄ + r*z̄

carries a factor of **m** on the shared term. The pooling axis (dispersion) was correct; the
common mode rode along with it uncontrolled.

**Decompose any group-wise operator into its two modes before trusting a ladder built from it:**

```python
# common mode -- moves the MEAN of beta, i.e. the realised step size
mean_b(z') / mean(z)      # must be ~flat in r, or the ladder is a step-size sweep
# dispersion -- the pooling axis proper
sd_b(z') / sd(z)          # this is what you intended to vary
```

For `zpool` the first runs 62 → 1 and for `zmpool` it is exactly 1 at every r, while the second is
identical (= r) for both. Same intended axis, one confounded and one clean.

**The empirical tell is in the probe you already write.** `mean(beta)` per cell is the diagnostic:
if it is not roughly constant across a ladder, the cells are not running the same optimizer.
Cycle 12's layerwise ladder read −10.69 / −10.83 / −12.49 / −13.64 / −14.11 / −10.58 — a 3.5-nat
swing, i.e. a 35x step-size difference, hiding inside what was labelled a pooling sweep. Plot
`mean(beta)` against the swept parameter **before** reading accuracy against it.

Corollary: an endpoint-only conclusion ("no interior cell beats the endpoint") can still survive a
confounded interior, provided the confound only ever *penalises* the interior. State which of the
two you are relying on.

## Gotcha 29 — `run` is not a unique key; a resubmission silently shadows a finished run

`--run-name` is reused on resubmission, so the same name can carry a completed run and an
in-flight one. Any analysis that keys a dict on `run` keeps whichever was parsed last, which
is usually the *partial* one. Three completed 100-epoch alpha0 controls
(`a0-{scal,layer,blk6}-1e4_s0`) were shadowed by 30-epoch reruns this way.

`aggregate.py` now emits `dup_group` / `superseded` and warns on stderr.
**Every analysis must filter `superseded == 0`.** Job id, not run name, identifies a run.

## Gotcha 30 — before resubmitting a batch, check it has not already completed

The entire queued `a0-*` batch (12 jobs) re-ran configurations already finished at 100/100
epochs. Cheap check, worth doing every time — compare the intended run-names against completed
artefacts before submitting:

```
find runs runs_alice2 -name "<name>-*.out" | while read f; do \
  echo "$f $(grep -c 'Test Accuracy' "$f")"; done
```

Note that argument *order* differs between submission scripts (`--alpha0 X --stepsize-groups Y`
vs the reverse) while being semantically identical, so diff the parsed args, not the raw line.

## Gotcha 31 — a blanket partition widen fails on the long jobs

`gpu-short` and `cpu-short` cap at **4 hours**. `scontrol update Partition=<list incl gpu-short>`
on a 6-hour job (every 300-epoch arm) fails with `Requested time limit is invalid (missing or
exceeds some limit)` — and `scontrol` returns non-zero *silently* in a loop, so the widen
reports success while nothing moved. `bin/widen_long.sh` branches on the job's own time limit:
>4h goes to the four 7-day GPU partitions, everything else also gets `gpu-short`.

Widening the pending queue this way took `salehkaleybars` from 3 running to 8 in one pass.

## Pending verification — carry to next run

The 15 `amx-*` jobs were submitted with `--export=ALL,...,HIER=additive,ETA_RATIO=<r>`, the same
form as the verified `ad-l-*` runs, but Slurm does not expose a pending job's environment so the
propagation is **not yet confirmed**. First check next run:

```
grep -m1 '^ENV:' runs/amx-r07-s0-*.out    # expect HIER=additive ETA_RATIO=0.07
```

If `HIER=none` / `ETA_RATIO=na` appears, the export failed and every `amx` run is a plain
layerwise run wearing an additive name — which would pool into the sweep and corrupt it exactly
as the Adam contamination did. Do not aggregate `amx-*` into any table before this line is read.
