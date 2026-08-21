# IDEA 3 — the alpha0-robustness tradeoff

**Status: SUBMITTED, cycle 45. 45 jobs, 28 on alice + 17 on alice2. Nothing read yet.**
Submit script: `bin/c45_idea3_alpha0_robustness.sh` (runs unchanged on both accounts).
Reducer: `analysis/idea3_robustness.py` (self-test 9/9 PASS, written before the data).

---

## 1. Why this experiment exists

Every method claim this campaign has made has been a **peak-accuracy** claim, and MetaOptimize
loses all of them. The best MetaOptimize arm plateaus at **92.795 ±0.177**; the tuned non-meta
baseline (AdamW + cosine, lr 3e-3) reaches **94.417 ±0.113 (n=5)** — a **1.622pp** deficit
(CORRECTIONS 30). Against SGD-momentum + cosine at lr 0.03 (94.767 ±0.097) the deficit is
larger still. The long-horizon escape was tested and closed: the deficit is 1.622 / 1.967 /
1.937 pp at 100 / 300 / 600 epochs — it does not narrow (FINDINGS 44.1).

**But peak accuracy was never the method's claim.** The parent paper claims

> "remarkable robustness to initial step-sizes, even for initial step sizes several orders of
> magnitude smaller than the optimal fixed step-size"

and this campaign has never tested it. Worse, it has spent cycles treating the evidence *for*
it as a nuisance. CORRECTIONS 8c is the clearest case: it quantifies the alpha0=1e-6 "escape
confound" and rules that every short-budget comparison must be read with it in mind. That is
correct as methodology and exactly backwards as science — the thing being controlled away *is*
the advertised property.

The hint is already in the CSV. At the paper's own configuration (AdamW base + Adam meta,
`--stepsize-groups resnet18_blocks`, m=6, ResNet18/CIFAR-10, 100 epochs, AUGMENT=1):

| alpha0 | n | plateau | batch |
|---|---|---|---|
| 1e-6 | 6 | 91.663 | `a0-blk6-1e6` |
| 1e-4 | 3 | 91.638 | `a0-blk6-1e4` |
| 1e-3 | 6 | 92.071 | `a0-blk6-1e3` / `I1_blk6` |

**Three decades of alpha0, 0.43pp of spread.** A *fixed* learning rate of 1e-6 would not train
a ResNet18 in 100 epochs at all. Nobody in this project has ever put those two facts on the
same axis.

That is what this batch does: it makes robustness the **measured quantity** rather than the
controlled-for nuisance, and it reports the result as a **tradeoff** — a form of claim this
project has not yet been able to make, because a tradeoff survives a peak-accuracy loss.

## 2. Design

| | Arm A | Arm B |
|---|---|---|
| name | `i3a-*` | `i3b-*` |
| optimizer | plain AdamW, **fixed lr, no schedule, no warmup** | MetaOptimize: AdamW base + Adam meta |
| step-size groups | — | `resnet18_blocks` (**m=6, the paper's setting**) |
| swept | lr ∈ {1e-6, 1e-5, 1e-4, 3e-4, 1e-3, 1e-2, 1e-1} | alpha0, same 7 values |
| guard | n/a | `BETA_CLIP=-15:-2.3026` (on) |
| meta-stepsize | — | 1e-3 |

Held fixed across all 42 main-grid jobs: ResNet18 / CIFAR-10 / batch 100 / **100 epochs** /
`AUGMENT=1` / `gamma 1` / `--max-time 999:00:00` / 3 seeds {0,1,2} / all five GPU partitions.

**Peak reference, not re-run:** tuned AdamW+cosine **94.417 ±0.113 (n=5)** (CORRECTIONS 30).
Note this is the corrected value — *not* 94.093, 94.24 or "94.4".

### 2.1 Arm A is a new arm, and that is not obvious

`AdamW_optimizer` in `Optimizers/build_optimizer.py` **always** constructs a
`CosineDecayWithWarmupScheduler`. There is no un-scheduled code path. Consequently every
"fixed-LR AdamW" row already in `all_runs.csv` carries a schedule:

* `fx_adamw_*`, `bl-adw-*`, `fxcos-*` — the 422000/10000 defaults, i.e. a **10,000-step
  (20-epoch) linear warmup** followed by decay to 0.977 of base. Near-constant *after* warmup.
* `SW_*` — `COS_TOTAL=50000`, a true horizon-matched cosine.

A warmup is a schedule, and at the top of a learning-rate sweep it is the difference between
diverging and not. **So this campaign has never measured a genuinely fixed learning rate**, and
an LR-robustness comparison against a warmed-up arm would be rigged in the baseline's favour on
precisely the axis under test.

Arm A sets `COS_WARMUP=0, COS_TOTAL=100000000`. **Verified on the cluster against the real
scheduler object** rather than inferred from the algebra:

| step | 0 | 1 | 10 | 1 000 | 10 000 | 25 000 | 50 000 |
|---|---|---|---|---|---|---|---|
| lr | 1.000000000e-3 | 9.999999999e-4 | 9.999999998e-4 | 9.999999998e-4 | 9.9999998e-4 | 9.9999985e-4 | 9.9999938e-4 |

Constant to **6.2e-7 relative** over the full 50,000-step run, with no warmup ramp. That is a
fixed learning rate.

### 2.2 The clip control `i3bc-*`, and why it is 3 extra jobs rather than a caveat

`BETA_CLIP=-15:-2.3026` bounds alpha to `[3.06e-7, 0.09999985]`. The top grid point
`alpha0 = 1e-1` therefore sits **at arm B's ceiling**: `HF.py:204-220` sets `beta = log(alpha0)`
un-clamped at init, and `HF.py:100-102` clamps from the first meta update onward, so the arm
starts pinned and can only move down. If arm B turns out flat all the way to 1e-1, part of that
top-end flatness could be the guard rather than the method.

`i3bc-1e1-s{0,1,2}` re-runs that one cell with `BETA_CLIP=-15:0` (alpha ≤ 1.0), everything else
byte-matched.

* lands on `i3b-1e1` → the guard is not doing the work; arm B's top end is the method.
* lands far below → arm B's top-end flatness is **partly the guard**, and the width claim must
  be stated over the sub-grid where the guard is not binding.

This follows the project's own Rule 4 as amended by CORRECTIONS 21: **verify a dial at both
extremes** instead of writing the caveat in prose. Three cycles were lost to `additive r=0`
being *inferred* to be full pooling; the same mistake is available here and is being paid for
in 3 jobs instead.

### 2.3 Account balance is part of the design

CORRECTIONS 10 lost an entire generalisation claim because meta-optimizer was confounded with
account. So the split is by **seed**, never by arm:

* **alice** (`salehkaleybars`): seeds 0 and 1 of **both** arms — 28 jobs.
* **alice2** (`s5014158`): seed 2 of **both** arms, plus the 3 clip controls — 17 jobs.

Every main-grid cell therefore has the identical account composition `{alice ×2, alice2 ×1}`.
Account cannot confound any alpha0 contrast or the A-vs-B contrast. Both accounts stay well
under the 40-PENDING cap, so no wave split was needed.

## 3. The analysis, pre-registered

Primary metric: **`plateau`** (mean of the last 20 epochs — code wins over prose,
CORRECTIONS 11), read only at `epochs_done >= 100` and `superseded == 0`.

For each arm, `analysis/idea3_robustness.py` reports:

* **(i) WIDTH** — the span, in decades, of the largest **contiguous** run of grid points within
  1pp / 2pp of *that arm's own best*.
* **(ii) WORST-CASE** plateau across the whole grid.
* **(iii) PEAK** plateau.

**The width convention is stated up front because it changes the number.** A cell is in-band if
`plateau >= own_best - tol`. Width is measured between the first and last in-band point of the
longest contiguous run, so a lone in-band cell has width **0 decades** and is not padded out to
half a grid spacing. If the in-band set is non-contiguous the reducer prints a WARNING and
reports only the longest run — a gapped in-band set means the curve is not a plateau and the
width is not a meaningful summary of it. All six rules are unit-tested (`--selftest`, 9/9).

The output sentence, if the effect is there, is:

> MetaOptimize costs **X pp** of peak accuracy and buys **N decades** of alpha0 insensitivity.

## 4. Pre-registered predictions — write the verdict against these

* **(P1)** Arm A collapses at the bottom: lr=1e-6 below 60, lr=1e-5 below 85. Arm A's
  within-1pp width is **≤ 1.5 decades**.
* **(P2)** Arm B is flat over **≥ 3 decades**: every alpha0 in [1e-6, 1e-3] within 1pp of arm
  B's own best. *This is nearly forced by the three existing cells in §1, so the sweep's real
  information is at 1e-5, 3e-4, 1e-2 and 1e-1* — the four points nobody has run.
* **(P3)** Arm B's peak is below arm A's peak, and both are below 94.417.

**Refutation conditions, and both are publishable.**

1. If arm B's within-1pp width is **not strictly wider** than arm A's, then the parent paper's
   own robustness claim fails on its own configuration (m=6, ResNet18, CIFAR-10, matched
   budget). Write it as the negative result it is — it is a direct refutation of a published
   claim, not a null.
2. If arm A at lr=1e-6 does **not** collapse, the premise that a small fixed step size cannot
   train is wrong and the tradeoff has no denominator. The whole framing goes.

## 5. What this batch cannot say

* **One granularity.** m is fixed at 6. Robustness measured at one m is one cell; do not
  generalise the width to layerwise/nodewise/weightwise without running them.
* **One task, one architecture.** ResNet18 / CIFAR-10 only. FINDINGS 32.6 already showed the
  granularity gain reverses sign on CIFAR-100, so cross-task transfer is not assumable here
  either.
* **One meta-stepsize.** `ms` is pinned at 1e-3. CORRECTIONS 24 established that ~81% of an
  apparent granularity gain was meta-step tuning; an arm-B width measured at a single `ms`
  cannot separate "robust to alpha0" from "robust to alpha0 *at this ms*". A width that holds
  at one `ms` is a real measurement; a claim that the method is tuning-free is not supported by
  it, and the honest framing trades **one** hyperparameter (lr) for **another** (`ms`) plus a
  peak-accuracy loss. Say that explicitly in any write-up.
* **The guard.** Arm B runs with `BETA_CLIP` on throughout, which bounds alpha to
  `[3.06e-7, 0.1]` regardless of alpha0. `i3bc-*` tests the top end only; the bottom end
  (alpha ≥ 3.06e-7) is not binding at init anywhere on this grid, since the smallest grid
  point is 1e-6.
* **Nothing about peak accuracy changes.** CORRECTIONS 30's 1.622pp deficit stands and must be
  reported in the same breath as any width claim.

## 6. Operational record

* **The FairShare floor was overridden, deliberately and by operator instruction.** FairShare
  read **0.333054** (alice) / **0.335570** (alice2) at submission — below the standing 0.35
  floor. CORRECTIONS 35 measured why waiting does not fix this: `PriorityDecayHalfLife` is
  **14 days**, usage decays 4.9%/day, and a full idle cycle with both queues at zero moved
  FairShare by less than 1e-4. The rule's premise — that waiting works — is false on the
  timescale it assumes. The operator gave an explicit launch instruction for this batch; the
  override is recorded in the submit script as `--force-fairshare` so it is visible in the
  script's own log rather than being a silent deviation. Both queues were at **0 PENDING /
  0 RUNNING** beforehand, so nothing was displaced.
* Batch cost ≈ 45 × ~35 min ≈ 26 GPU-hours, ≈ 0.4% of RawUsage.
* `run_cifar.sh` writes `.out` to the **root** of `runs/`, not to `runs/i3/`. The
  `--save-directory` only receives TensorBoard output.
* No probe directories: this batch measures plateaus, not meta-gradient statistics, so
  `PROBE` is unset and nothing here adds to the unreduced-probe backlog.
