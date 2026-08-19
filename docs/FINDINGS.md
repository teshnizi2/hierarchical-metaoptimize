# Measured findings

CIFAR-10, ResNet-18 (11,173,962 params / 62 parameter tensors), 100 epochs,
RandomCrop(32,pad=4)+HorizontalFlip, meta-optimizer Lion, `meta_stepsize=1e-3`,
`alpha0=1e-6`, `gamma=1`. Best test accuracy, 3 seeds unless noted.

| granularity | m | SGDm base | AdamW base |
|---|---|---|---|
| scalar | 1 | 88.09 ± 0.16 | **91.99 ± 0.10** |
| resnet18_blocks | 6 | **91.56 ± 0.03** | 91.86 ± 0.30 |
| layerwise | 62 | 91.34 ± 0.09 | 91.83 ± 0.17 |
| weightwise | 11,173,962 | 66.54 ± 3.26 (3/3 collapsed) | 86.05 ± 0.29 |

**Effect of granularity relative to scalar, same base optimizer** (pooled sd in brackets):

| | m = 6 | m = 62 | m = 11.17M |
|---|---|---|---|
| **SGDm** | **+3.47pp** (0.12, ~30x) | **+3.26pp** (0.13, ~25x) | −21.55pp (2.31, ~9x) |
| **AdamW** | −0.13pp (0.22, ~1x — null) | −0.15pp (0.14, ~1x — null) | −5.93pp (0.22, ~27x) |

## Reading
1. **The proposal's premise does not reproduce at this scale.** Layerwise does not
   lose to scalar; under SGDm it beats it by +3.3 points.
2. **The failure is at `weightwise`, not `layerwise`** — two granularity steps finer
   than the proposal assumed.
3. **The collapse is not runaway beta (H3).** Probe traces show the opposite: peak
   alpha only 5.7e-5 (vs 1.1e-2 for healthy layerwise), whole tensors driven to
   beta ≈ -23.8 (alpha ≈ 5e-11), then beta freezes exactly (Lion's `sign(0)=0`)
   once the network stops producing gradient. Step sizes collapse toward zero, the
   weights freeze, the network dies.
4. **H1 (SNR ∝ √n_b) — preliminary and weak.** Over 62 groups spanning 5.4 decades:
   `log(SNR) = +0.114 log(n_b) − 1.23`, r = +0.40, versus a predicted slope of +0.50.
   Measured over only 1400 steps; needs full-length runs.

## Open confound
`alpha0` and `meta_stepsize` are the values the authors used for scalar/6-block.
Comparing granularities at a fixed meta-step-size may be unfair to the finer arms;
a defensible comparison tunes the meta-step-size per arm at equal search budget.

---

## D1 numerics gate — the collapse is sign-specific, the granularity failure is not

weightwise (m = 11,173,962) + SGDm base, 100 epochs, augmented:

| meta-optimizer | best | final | outcome |
|---|---|---|---|
| **Adam** (non-sign), 3 seeds | 50.35 / 50.29 / 51.61 | 50.35 / 50.23 / 51.58 | stable, no collapse |
| **Lion** (sign), 1 seed | 65.29 | **10.00** | collapsed to chance |

**Two distinct conclusions:**
1. The *collapse* is an artifact of the sign-based meta-update. Swapping Lion → Adam removes
   it in 3/3 seeds. Consistent with Balles & Hennig (ICML 2018): Adam scales its step by
   `1/√(1+η̂²)` in low-SNR coordinates; sign takes a full ±η step regardless.
2. The *granularity failure* is real and survives the fix. Adam-meta is stable but plateaus
   near 50%, still ~40 points below layerwise (91.34) and 6-block (91.56).

**So: per-weight granularity fails regardless of meta-optimizer; the sign convention decides
whether it fails by collapsing or by plateauing.** Do not attribute the granularity result to
`sign(0)=0`.

## Reproducibility floor

Three runs with identical config and seed on the same partition (two with the probe on, one
off) differ from each other by up to ~0.02pp per epoch, with the two probe-on runs differing
from *each other* as much as either differs from the probe-off run. The variation is cuDNN
autotuning, not the probe.

**Runs are reproducible to ~±0.02pp, not bitwise.** Effect sizes below ~0.05pp are not
resolvable without more seeds. The measured effects (+3.3pp granularity, +3.5pp base-optimizer,
−40pp weightwise) are two to three orders of magnitude above that floor.

---

## Gate 1 headline — granularity x base-optimizer is an interaction, not a main effect

**Step-size granularity buys +3.5pp under SGDm and nothing at all under AdamW.** Under AdamW
the differences between m=1, 6 and 62 are ~0.15pp against a pooled sd of ~0.2 — statistically
null. Under SGDm the same contrast is 25–30x the noise.

Reading: **per-coordinate normalization in the base optimizer substitutes for step-size
granularity.** AdamW already divides each coordinate by a running second-moment estimate, so a
learned per-block step size has nothing left to contribute. SGDm does not, so granularity
supplies the missing normalization. This is hypothesis H4, and it is a candidate mechanism for
the parent paper's own unexplained §7.3 result ("the blockwise versions showed no improvement
over the scalar versions").

Per-weight (m = n) is catastrophic under **both** bases — so the fine-granularity failure is
not an artifact of the base optimizer, unlike the +3.5pp benefit.

**Caveat — the paper's exact cell is still untested.** All of the above used meta-optimizer
**Lion** (the released code's default). PILOT.md records the paper's CIFAR-10 config as base
AdamW + meta **Adam**. Since the D1 gate showed the meta-optimizer changes the outcome
qualitatively, base-AdamW + meta-Adam x {scalar, 6-block, layerwise} x 3 seeds is queued as
Gate 2 before any reproduction claim is made.

---

# THE UNIFYING RESULT — granularity buys SPEED, not asymptotic accuracy

Measuring only final/best accuracy was the wrong instrument. MetaOptimize's objective is a
discounted sum of *future losses*, and the parent paper's CIFAR-10 evidence is **Figure 1,
which is learning curves**. Re-analysed as epochs-to-threshold (mean of 3 seeds, augmented,
100 epochs):

### AdamW base + Adam meta — the paper's exact CIFAR-10 configuration

| arm | ep→85% | ep→88% | ep→90% | final | best |
|---|---|---|---|---|---|
| scalar | 9.7 | 18.0 | 29.7 | 91.76 | 91.93 |
| 6-block | 9.0 | 15.0 | 26.3 | 91.83 | 92.06 |
| layerwise | **7.7** | **14.3** | **24.0** | 91.73 | 92.09 |

Monotonic in granularity at every threshold ≥85% — layerwise reaches 90% **19% sooner** than
scalar — while final accuracy is identical to within 0.1pp. **The paper's CIFAR-10 claim
reproduces, on the axis the paper actually plotted.**

### SGDm base + Lion meta

| arm | ep→85% | ep→88% | ep→90% | final |
|---|---|---|---|---|
| scalar | 36.0 | 87.5 | **never** | 87.93 |
| 6-block | 29.0 | 35.0 | 42.0 | 91.41 |
| layerwise | 27.3 | 35.0 | 52.0 | 91.06 |

Same acceleration — but here the scalar arm **never converges within the budget**, so the speed
advantage shows up as a +3.5pp final-accuracy gap.

### The single statement that covers every cell

> **Step-size granularity accelerates optimisation. It shows up as higher final accuracy only
> when the training budget is too short for the coarser arm to catch up.**

This reconciles four results that looked contradictory:
1. Our AdamW final-accuracy null — scalar catches up by epoch 100.
2. Our SGDm +3.5pp — scalar never catches up.
3. The paper's CIFAR-10 blockwise claim — it is a learning-curve claim, and it holds.
4. **The paper's own ImageNet null (§7.3)** — a long budget lets the scalar arm converge, so
   the speed advantage stops converting into a final-accuracy difference. The paper reports
   this as "no improvement" and offers no explanation; this predicts it.

### Consequence for methodology

**Primary metric from here on is epochs/steps-to-target-accuracy (and area under the loss
curve), with final accuracy reported alongside.** Final-accuracy-only comparisons are
underpowered for this method by construction, and every earlier table in this document should
be read with that in mind.

---

## The weightwise failure, mechanism finally measured (and two wrong guesses corrected)

Instrumenting `max|h|` (the condensed trace) through the failure gives an unambiguous answer:

| run | step | max\|h\| | note |
|---|---|---|---|
| γ=1, seed 1 | 12,500 | 3.7e−1 | normal |
| | 23,350 | **1.97e+19** | |
| | 23,400 | **6.69e+33** | +14 orders of magnitude in 50 steps |
| | 23,450 | **NaN** | float32 max is 3.4e38 |
| γ=0.999, seed 1 | 23,400 | 3.7e+14 | |
| | 23,450 | 2.47e+28 | |
| | 23,500 | **NaN** | **same failure, same timing** |

**The trace blows up geometrically at roughly ×1.9 per step, then overflows float32.** Accuracy
peaks around 64–72% and drops to chance the moment the trace goes non-finite.

### Two hypotheses of ours that this REFUTES

1. **"β decays to zero, weights freeze, network dies" (from the g1 per-tensor means).** False.
   At the moment of failure β is in a healthy range and is *not* collapsed.
2. **"γ = 1 leaves the trace undecayed, so it accumulates until it overflows."** False, and
   tested directly: γ = 0.999 gives the trace a ~693-step half-life and **fails identically**
   (72.30 vs 72.08 peak; both → 10.00). A geometric blow-up at ×1.9/step is not something a
   0.999 decay factor can restrain.

The `sign(0)=0` story was wrong earlier too — it is at most the lock after the fact, never the
driver.

### What the evidence now points to

A per-coordinate positive feedback loop: with per-weight step sizes nothing bounds any
individual α, so a few coordinates can be driven to a destabilising value, and the trace — which
is a running sum of updates each proportional to α — amplifies geometrically from there. Note
our probe logged **per-tensor means** of β, which hide exactly these extremes; true
per-coordinate extremes are now logged (`beta_true_min`/`beta_true_max`).

This is the failure mode the classical guards exist to prevent, and it is now being tested
directly with **SwiftTD's published bounds**, `β ∈ [ln(e⁻¹⁵), ln(0.1)]` = `[−15, −2.3026]`,
applied to weightwise and layerwise (`BETA_CLIP=lo:hi`, 3 seeds each).

---

# The guard separates artifact from finding

`BETA_CLIP=-15,-2.3026` implements SwiftTD's published bound
`beta <- clip(beta, ln(e^-15), ln(0.1))` (Javed, Sharifnassab & Sutton, RLC 2024).
SGDm + Lion meta, augmented, 100 epochs, 3 seeds:

| arm | best test accuracy |
|---|---|
| weightwise, **no guard** | collapse to **10.00** (chance) |
| weightwise **+ guard** | **79.70 / 79.59 / 78.86** — stable, 3/3 |
| layerwise + guard | 91.55 / 91.44 / 91.18 (unchanged vs unguarded) |

**Two separate things, now disentangled:**
1. The *collapse* is a numerical artifact of an unguarded exponential parameterisation. A guard
   published in 1992 (IDBD), 2012 (Autostep) and 2024 (SwiftTD) removes it completely. This is
   a rediscovery and must be written up as one.
2. **Per-weight still loses ~12pp to layerwise with the guard in place.** That gap is the real
   granularity effect and is not a numerics story.

The guard is a no-op for layerwise, so it is safe to make it standard in all subsequent runs.

# Granularity also STABILISES training

Gate 3, the paper's own (SGDm, Adam) configuration, 100 epochs, 3 seeds:

| arm | seeds | mean |
|---|---|---|
| 6-block | 90.89 / 90.80 / 90.75 | 90.81 ± 0.07 |
| layerwise | 91.11 / 90.74 / 90.53 | 90.79 ± 0.29 |
| **scalar** | 88.45 / **18.47** / **20.71** | catastrophic on 2 of 3 seeds |

The scalar arm of the parent paper's own configuration fails outright on two thirds of seeds
while every granular arm is stable to within 0.3pp. So granularity delivers **three** distinct
benefits, not one:

* **speed** — 19% fewer epochs to 90% under the paper's AdamW+Adam config;
* **final accuracy**, but only when the budget is too short for the coarse arm to converge;
* **stability** — it rescues seeds on which the scalar arm diverges.

The third is the most robust of the three and, unlike the first two, is visible in the parent
paper's own configuration without any modification.

> **CONFOUND FLAGGED 19 Aug 2026 — this claim is not yet safe to report.** Those Gate 3 runs
> were **unguarded**. The two collapsing scalar seeds (18.47 / 20.71) look exactly like the
> unguarded weightwise collapse that `BETA_CLIP=-15:-2.3026` was later shown to remove
> completely (3/3 seeds). If the guard alone rescues those seeds, then the rescuer is the
> published guard, **not** granularity, and the stability claim as written is wrong.
> `g4-sgdmAdam-{scal,blk6,layer}` x 3 seeds, guard ON, is running to decide it.
> **Do not put the stability claim in a draft until that control reports.**

# Hierarchical method — implemented and validated

`HIER=shrink LAM=x` (M0, pull each group's beta toward the group mean) and
`HIER=additive ETA_RATIO=r` (M1, shared component takes the full meta step, deviations take a
fraction r). Validated by exact identity: **LAM=0 and ETA_RATIO=1 both reproduce plain
layerwise** to within the +-0.02pp non-determinism floor, and LAM=1 (full pooling) correctly
departs from it.

---

# Hierarchical sweep, first results — the fix helps where the method already works
# and hurts where it fails

SGDm base + Lion meta, guard ON (`BETA_CLIP=-15:-2.3026`), augmented, 100 epochs, α₀=1e-6.
Generated by `analysis/summarize.py`; **n as marked — the layerwise cell is still n=1**.

| granularity | hierarchy | n | ep→85 | ep→88 | ep→90 | best | final |
|---|---|---|---|---|---|---|---|
| layerwise | plain | 3 | 28.7 | 36.0 | 54.7 | 91.39 ± 0.19 | 90.98 ± 0.42 |
| layerwise | **shrink λ=0.1** | **1** | 36.0 | 39.0 | **42.0** | **92.55** | **92.46** |
| weightwise | plain (= λ=0 / r=1) | 3 | never | never | never | **79.38 ± 0.46** | 79.38 ± 0.46 |
| weightwise | additive r=0.3 | 1 | never | never | never | 67.13 | 67.13 |
| weightwise | additive r=0.1 | 1 | never | never | never | 49.87 | 49.87 |
| weightwise | shrink λ=0.01 | 2 | never | never | never | 49.73 ± 3.51 | 49.73 ± 3.51 |
| weightwise | shrink λ=0.1 | 2 | never | never | never | 49.07 ± 3.75 | 49.07 ± 3.75 |
| weightwise | shrink λ=0.5 | 1 | never | never | never | 46.37 | 46.37 |

## Two findings, pointing opposite ways

**1. On layerwise, partial pooling is the best result the project has produced.**
92.55 best / 92.46 final against plain layerwise's 91.39 ± 0.19 / 90.98 ± 0.42 — **+1.16pp
best, +1.48pp final, six to eight times the pooled sd**, and it beats every other arm in the
campaign including 6-block (91.55) and the AdamW ceiling (92.09). On the primary metric it
reaches 90% at epoch **42 vs 54.7**, a 23% speed-up.

Note the *shape*: the shrink arm is **slower early** (ep→85 of 36.0 vs 28.7) and faster late.
It gives up early greed and does not stall. That is the signature partial pooling is supposed
to have, and it is the first time in this campaign that hierarchy has bought anything.

**This is n = 1 and must not be reported until it replicates.** Seeds 1 and 2 are running.

**2. On weightwise, pooling is monotonically harmful — the proposal's fix fails exactly where
the proposal predicted it would help.** Ordering by pooling strength, from none to full:

`plain 79.38 → additive r=0.3 67.13 → additive r=0.1 49.87 → shrink (any λ ≥ 0.01) ≈ 48`

Two independently-parameterised mechanisms (M0 shrink, M1 additive) land on the same curve and
the same ≈48% floor. The ~12pp per-weight deficit is not closed by hierarchy; pooling **widens
it to ~30pp**. Whatever per-weight granularity is failing at, it is not a lack of sharing
toward a global mean.

## Methodological catch — λ is a PER-STEP rate, so the sweep range was saturated

`shrink` applies `β ← β − λ(β − β̄)` **every step**. At λ = 0.01 that is a 69-step half-life
against ~50,000 training steps, so λ = 0.01, 0.1 and 0.5 are all effectively *full* pooling on
any timescale training cares about — which is exactly what the three near-identical weightwise
cells (49.7 / 49.1 / 46.4) show. **The sweep as designed did not span the partial-pooling
regime at all; it measured full pooling three times.**

Resolving this: λ ∈ {1e-4, 1e-5} on weightwise, and λ ∈ {0.001, 0.01, 0.1, 0.5, 1.0} on
layerwise, are queued. Any future λ must be quoted with its half-life `ln2/λ` in steps, not as
a bare number.

## Open question this raises

The layerwise win is *not* explained by "pooling ≈ scalar": near-full pooling of layerwise
gives 92.55 while the actual scalar arm gives 88.07 ± 0.12. The two are not the same
computation. Under a **sign-based** meta-optimizer, scalar takes `sign(Σ gᵢ)` — one ±η step
with the magnitude discarded — whereas pooled-layerwise averages 62 separate signs, giving an
effective step of `η · mean(sign(gᵢ))`, a bounded low-variance consensus estimate that keeps
magnitude information the scalar arm throws away.

**Prediction, now being tested:** if that is the mechanism, the shrink win should shrink or
vanish under a non-sign meta-optimizer. `h2A-l-L0p1` (SGDm + **Adam** meta + shrink λ=0.1)
against `h2A-l-plain`, 3 seeds each, is queued to decide it.

## Provenance defect found and fixed

`run_cifar.sh` recorded neither `BETA_CLIP` nor `HIER`/`LAM`/`ETA_RATIO` in the `.out` file, and
on the `salehkaleybars` account it did not record `AUGMENT` either — so `aggregate.py` was
reading `augment=0` for 52 of 65 rows purely because the string was absent. **No run's guard or
hierarchy setting was recoverable from its own artefact.**

Fixed on both accounts: every job now prints
`ENV: AUGMENT=… BETA_CLIP=… HIER=… LAM=… ETA_RATIO=…`.
`aggregate.py` parses it, and reconstructs the setting from the run name for the 109 older runs
while marking those rows `provenance=inferred`, so no analysis can silently treat a
reconstruction as a recorded fact.

---

# REPLICATED — partial pooling on layerwise is the campaign's best result

Seed 1 finished and reproduces seed 0. SGDm + Lion, guard ON, augmented, α₀=1e-6, 100 epochs:

| granularity | hierarchy | n | ep→85 | ep→88 | **ep→90** | best | final |
|---|---|---|---|---|---|---|---|
| layerwise | plain | 3 | 28.7 | 36.0 | 54.7 | 91.39 ± 0.19 | 90.98 ± 0.42 |
| layerwise | **shrink λ=0.1** | **2** | 35.5 | 38.0 | **41.5** | **92.53 ± 0.04** | **92.31 ± 0.22** |

Seeds: **92.55** and **92.50** — they agree to 0.05pp, against a plain-arm spread of 91.55 /
91.44 / 91.18. **+1.14pp best, +1.33pp final**, six times the pooled sd, and on the primary
metric **24% fewer epochs to 90%** (41.5 vs 54.7). Seed 2 (`h2-l-L0p1-s2`) is queued.

**The comparison is single-variable and was verified rather than assumed:** the `ARGS:` lines of
`d4-clipL-s0` (plain) and `hs-l-lam01-s0` (shrink) are byte-identical apart from the seed and
granularity flags, both are `--stepsize-groups layerwise`, and both ran with the guard. The only
difference is `HIER=shrink LAM=0.1`.

This also beats every other arm in the campaign, including 6-block (91.55 ± 0.13) and the AdamW
ceiling (92.09 ± 0.10). It is the first time hierarchy has bought anything in this project.

## What still has to hold before this goes in a draft

1. **Seed 2**, for n=3 (queued).
2. **The λ sweep** — λ ∈ {0.001, 0.01, 0.5, 1.0} × 3 seeds is running. If the effect is flat in
   λ across three decades, it is *pooling per se*; if it peaks, there is a real optimum to
   report. Given the half-life arithmetic (§ "λ is a PER-STEP rate"), λ = 0.1 and λ = 0.5 are
   both full pooling, so a flat top between them would be expected and is not evidence of
   robustness.
3. **The mechanism test** — `h2A-l-L0p1` vs `h2A-l-plain` under meta = **Adam**. The proposed
   mechanism is that under a *sign* meta-optimizer, scalar throws away magnitude
   (`sign(Σ gᵢ)`) while pooled-layerwise keeps it (`η · mean(sign(gᵢ))` over 62 groups). If
   that is right, the win should shrink or vanish without the sign. **If it survives under Adam,
   the sign explanation is wrong and the effect needs a different account.**
4. **6-block** (`h2-b-L0p1`) — does pooling help a partition that is already coarse?

## Weightwise, now n=2 on every cell — the negative result is firm

`plain 79.38 ± 0.46 → additive r=0.3 67.1 → additive r=0.1 49.9 → shrink (λ ≥ 0.01) ≈ 49`

λ = 0.01, 0.1 and 0.5 now sit at 49.73 ± 3.51 / 49.07 ± 3.75 / 49.06 ± 3.80 — statistically
indistinguishable, exactly as the saturation argument predicts. **Pooling toward a global mean
does not close the per-weight deficit; it triples it.** λ ∈ {1e-4, 1e-5} is queued to test
whether a genuinely *weak* pool helps before it hurts.

**So the two granularities respond to the same intervention in opposite directions.** Whatever
per-weight step sizes are failing at, it is not insufficient sharing — and that is a substantive
constraint on any account of the failure.

---

# THE PROPOSAL WORKS — hierarchical shrinkage beats every plain granularity

SGDm base + Lion meta, SwiftTD guard on, augmented, 100 epochs. M0 = shrink each group's beta
toward the group mean every step: `beta_b <- beta_b - lam (beta_b - mean beta)`.

| arm | best test accuracy | n |
|---|---|---|
| scalar | 88.09 ± 0.16 | 3 |
| 6-block (previous best plain arm) | 91.56 ± 0.03 | 3 |
| layerwise + guard | 91.39 ± 0.19 | 3 |
| **layerwise + M0 shrink, lam = 0.1** | **92.53 (92.55 / 92.50)** | 2 |

**+1.14pp over plain layerwise (~8x the pooled sd) and +0.97pp over the best plain arm.** This
is the project's proposal doing what it was designed to do, and it is the best number measured
anywhere in the campaign. Confirmation at 3 seeds plus a lambda curve is running.

## But it does NOT rescue per-weight — it makes it worse

| weightwise (m = 11.17M) variant | best |
|---|---|
| plain + guard (baseline) | **79.4** |
| M1 additive, r = 0.3 | 66.6 |
| M1 additive, r = 0.1 | 51.3 |
| M0 shrink, lam = 0.01 / 0.1 / 0.5 | 49.7 / 49.1 / 49.1 |

Every hierarchical variant is worse than plain weightwise, and **less** pooling is better
(r=0.3 > r=0.1). So partial pooling helps where there is real per-group signal to regularise
(m=62) and hurts where the per-group estimates are hopeless to begin with (m=n).

**Caveat on the parameterisation, stated plainly:** the shrinkage is applied *every step*, so
the effective pooling over T steps is `1 - (1 - lam)^T`, which saturates at 1 for any lam > 0
over 50,000 steps. All three lam values therefore end up near-fully pooled, which is why they
give nearly identical (bad) weightwise numbers. A per-step lam is a *rate*, not a *strength* —
the honest reading is that this sweep varied the time constant (1/lam steps), not the amount of
pooling. Runs at lam = 1e-4 and 1e-5 are queued to probe the regime where the time constant is
comparable to the run length.

---

# 19 Aug 2026 — four new results, one of which threatens the headline

## 1. The λ curve is FLAT across three decades — and λ = 1.0 is at the top

SGDm + Lion, guard on, augmented, α₀ = 1e-6, 100 epochs, all cells complete:

| λ | half-life (steps) | ep→90 | best | final | n |
|---|---|---|---|---|---|
| plain (no pooling) | ∞ | 54.7 | 91.39 ± 0.19 | 90.98 ± 0.42 | 3 |
| 0.001 | 693 | 48 | 92.43 | 92.23 | 1 |
| 0.01 | 69 | 41 | **92.68** | **92.57** | 1 |
| 0.1 | 7 | 41.5 | 92.53 ± 0.04 | 92.31 ± 0.22 | 2 |
| 0.5 | 1 | 42 | 92.51 | 92.51 | 1 |
| **1.0** | **0 (exact)** | 42 | **92.68** | 92.51 | 1 |

**λ = 1.0 sets every group's β to the group mean every step — that is not partial
pooling, it is exact full pooling — and it ties for the best number in the campaign.**
Everything from λ=0.01 to λ=1.0 is indistinguishable (92.51–92.68, spread 0.17pp against
a ±0.02pp determinism floor and a ~0.19pp seed sd). Only λ=0.001, whose 693-step half-life
is the first value that is genuinely partial over a 50,000-step run, sits lower (92.43,
ep→90 = 48) — i.e. *closer to plain*.

**So the effect is monotone in pooling strength and maximal at full pooling.** The
"partial pooling / hierarchical shrinkage" framing is wrong as an explanation: nothing in
the data prefers an interior λ. What wins is *pooling per se*, and the M0 shrink operator
at λ→1 is just an expensive way of writing "one shared β, updated from 62 per-group
meta-gradients."

**This should be reported as what it is.** The contribution is not "a hierarchical
estimator with a tunable shrinkage coefficient"; it is "**averaging the meta-gradient over
a partition beats both the scalar arm and the unpooled partition**," with λ as a knob that
is flat wherever it matters. The λ ∈ {0.03, 0.1, 0.3} × 3-seed confirmation sweep
(`h2-lam*`) plus a matched `h2-base` plain baseline on the same seeds is queued to nail
the plateau down at n=3.

## 2. The sign-based explanation is REFUTED (preliminary)

The prediction on record: the win comes from scalar taking `sign(Σ z_b)` (magnitude
discarded) while pooled-layerwise takes `η · mean(sign(z_b))` over 62 groups (a bounded
consensus estimate) — **so it should shrink or vanish under a non-sign meta-optimizer.**

SGDm + **Adam** meta, guard on, α₀ = 1e-6, seed 0, *both runs still in flight*:

| arm | epochs so far | ep→90 | best so far |
|---|---|---|---|
| `h2A-l-plain` | 61 | 56 | 90.07 |
| `h2A-l-L0p1` | 66 | **20** | **91.96** |

The win does not shrink — on epochs-to-90% it is *larger* under Adam (20 vs 56) than under
Lion (41.5 vs 54.7). **The sign explanation as stated is wrong.** Whatever pooling is
buying, it is not specific to the sign nonlinearity, so the account has to be about the
variance of the per-group meta-gradient estimate itself rather than about how the
meta-optimizer consumes it. Seeds 1–2 of both arms are queued; do not write the sign
mechanism into a draft, and do not write its refutation in either until n=3.

## 3. Pooling does NOT help an already-coarse partition (preliminary)

`h2-b-L0p1` (6-block + shrink λ=0.1), 56 epochs so far: best 90.52, ep→90 = 54, against
plain 6-block's 91.55 ± 0.13 / ep→90 = 43.5. Pooling m=6 looks neutral-to-harmful.

Combined with the weightwise result (pooling m=11.17M is catastrophic: 79.4 → ~49) this
gives a coherent shape: **pooling helps only at intermediate granularity.** Too coarse and
there is nothing to average; too fine and the per-group estimates being averaged are
themselves worthless. m=62 is where the partition is fine enough to have per-group signal
and coarse enough for that signal to be estimable. Seeds 1–2 queued.

## 4. ⚠ THE α₀ CONFOUND IS REAL AND IT THREATENS THE SPEED CLAIM

AdamW + Adam (the paper's exact CIFAR-10 config), guard on, augmented, seed 0. **The
scalar arm is complete at 100 epochs in all three cells:**

| α₀ | ep→85 | ep→88 | **ep→90** | best | final |
|---|---|---|---|---|---|
| 1e-6 (the campaign's value) | 10 | 19 | **30** | 92.12 | 91.41 |
| 1e-4 | 10 | 14 | **27** | 92.37 | 91.98 |
| 1e-3 | 10 | 12 | **18** | **92.76** | **92.56** |

**Raising α₀ alone buys the scalar arm 12 epochs to 90% — more than twice the 5.7-epoch
gap that the campaign's headline speed claim rests on** (layerwise 24.0 vs scalar 29.7 at
α₀=1e-6). And α₀=1e-3 scalar reaches **92.76 best / 92.56 final**, the highest number
measured anywhere in this campaign — above the hierarchical layerwise result (92.68/92.57).

The mechanism is the obvious one: at α₀=1e-6 the step size starts ~3 orders of magnitude
below useful, so the early epochs are spent growing it rather than optimising. A finer
partition has more parallel meta-gradient signal with which to grow it, so **granularity
may be winning a race that a sane initialisation makes unnecessary.**

**Consequences, stated before the confirming seeds land:**
- The headline "granularity buys 19% fewer epochs to 90%" is measured at a step-size
  initialisation that handicaps every arm, and the handicap is larger than the effect.
- The stability claim, the speed claim and the hierarchical win are *all* currently
  measured only at α₀=1e-6.
- **No speed or final-accuracy claim should enter a draft until it is shown at α₀ ≥ 1e-4.**

Caveats held honestly: these are n=1 per cell and the 6-block/layerwise cells of this sweep
are still running (23–82 of 100 epochs), so the *ordering across granularities* at high α₀
is not yet measured — only the scalar arm's own α₀ dependence is. Seeds 1–2 of all nine
cells are queued.

### The control this forced

Every hierarchical result in the campaign lives at α₀ = 1e-6, so the same threat applies to
the project's own proposal. `a0h-*` — {scalar, layerwise plain, layerwise shrink λ=0.1} ×
α₀ ∈ {1e-3, 1e-4} × 2 seeds, plus a 1-seed α₀=1e-6 anchor — was submitted to decide it.
**If the shrink win survives at α₀=1e-3, the proposal is real; if it collapses to the
scalar arm's 92.76, the campaign's best result is an initialisation artifact.**

Run on `gpu-2080ti-11g` rather than L4 (both L4 queues were 59 jobs deep and the 2080ti
partition was idle). All 15 cells share one GPU type so they are mutually comparable; the
α₀=1e-6 row doubles as a cross-GPU-type anchor against the existing L4 numbers. Per
gotcha 3 this is safe because the primary metric is *epochs*-to-target and accuracy, both
GPU-type-independent — but `wallclock_min` for these runs must not be compared to L4 runs.

---

# 19 Aug 2026 — infrastructure findings (zero GPU)

## The ImageNet copy is a genuine half-dataset, and `val` is the real blocker

Audit job 4680826, full table in `docs/PLAN-appendix-infra.md` §3.4. Headline:
**489/1000 classes, 627,329/1,281,167 images, per-class counts spanning the canonical
732–1300 with 0/300 sampled images corrupt.** The classes that are present are intact —
the earlier "capped/derived copy, treat as untrusted" worry is refuted.

But **the devkit is absent**, so the 50,000 `val` JPEGs (flat, no class subdirs) cannot be
labelled from anything on disk. That blocks ImageNet at *any* number of classes and is
independent of the missing 511 training classes. The suspected "second ImageNet copy"
turned out to contain no data at all — it is the authors' training code.

Net effect on the plan: unchanged. **ImageNet-64×64 remains the default scale point**; this
audit only removes the option of quietly using the on-disk copy as-is.

## The dead-granularity defect is in BOTH task copies, not just CIFAR-10

`tinystories/HF.py` accepts `layerwise`/`nodewise`/`weightwise` into `self.stepsize_type` but
assigns `self.beta` only on the `scalar` and `blockwise` branches, so `len(self.beta)` on the
next line raises `AttributeError`. Same defect, different file, found independently.

**The released code advertises three granularities in the argument parser of both task copies
and can execute them in neither.** That is a systematic defect rather than a slip in one file,
and it is a stronger form of the reproduction finding than what is currently written up.

## A question for Saber got much sharper

The authors' own ImageNet launcher on scratch (`cedar_arg_iterator_HF.sh`, 27 Jan 2024) has

```bash
for stepsize_groups in scalar; do # scalar layerwise nodewise weightwise resnet18_blocks
```

i.e. **as configured on disk it sweeps `scalar` only**, with `resnet18_blocks` commented out.
Our unifying result currently *predicts* the paper's §7.3 ImageNet blockwise null — so the
provenance of that blockwise arm should be established before we keep explaining it.
PLAN §4 question (c) is upgraded from "was it the same 6-block partition?" to **"the launcher
on scratch sweeps scalar only — where did the ImageNet blockwise arm come from?"**

This is evidence about unpublished work sitting in the PI's directory, so it is a question to
ask, not a finding to publish. The ~50 Jan-2024 run-output directories next to it were
deliberately **not** read — that needs his permission first (PLAN §4 item (g)) — and nothing
of his has been copied off ALICE.

---

# 19 Aug 2026 (later) — the α₀ control reports at n=2, and it splits the headline in two

All four of the previous section's preliminary results now have their confirming seeds.
Three firm up as written; the α₀ one resolves into something sharper and less comfortable
than either the original claim or the feared refutation.

## 1. α₀ — the speed claim survives at fixed α₀, and dies under per-arm tuning

AdamW + Adam (the paper's exact CIFAR-10 config), SwiftTD guard on, augmented, 100 epochs,
L4. **PRIMARY metric ep→90, n=2 per cell** (n=3 for scalar α₀=1e-3):

| α₀ | scalar | 6-block | layerwise | fastest arm |
|---|---|---|---|---|
| 1e-6 *(the campaign's value)* | 32.5 | 29.5 | **26.5** | layerwise |
| 1e-4 | 28.0 | 27.0 | **18.0** | layerwise |
| 1e-3 | **17.0** | 18.5 | 33.5 | **scalar** |

Best test accuracy over the same cells (seeds still short of 100 epochs marked †, so their
best is a lower bound):

| α₀ | scalar | 6-block | layerwise |
|---|---|---|---|
| 1e-6 | 92.07 ± 0.07 | 92.07 ± 0.24† | 91.91 ± 0.05† |
| 1e-4 | 92.34 ± 0.04 | 92.09 ± 0.21 | 92.19 ± 0.30† |
| 1e-3 | **92.92 ± 0.22** | 92.20 ± 0.08 | 91.01 ± 0.20 |

### Two readings, and they point in opposite directions

**(a) At any fixed α₀ ≤ 1e-4 the granularity speed advantage is real and is *larger* than
the campaign reported.** At α₀=1e-4 layerwise reaches 90% in 18.0 epochs against scalar's
28.0 — **36% fewer**, against the 19% quoted at α₀=1e-6. The confound does not manufacture
the effect; raising α₀ from 1e-6 to 1e-4 *strengthens* it. The fear recorded in the previous
section — that granularity was merely winning a race a sane initialisation makes unnecessary
— is **refuted at α₀=1e-4**.

**(b) At each arm's own best α₀ the advantage disappears completely.** Tuned per arm:
scalar 17.0 (@1e-3), layerwise 18.0 (@1e-4), 6-block 18.5 (@1e-3) — a three-way tie inside
the seed spread — and on accuracy the scalar arm is *highest* (92.92 vs 92.20 / 92.19).
**Under an equal per-arm tuning budget for α₀ alone, granularity buys nothing on this
configuration.**

Both statements are true and neither can be dropped. Which one a paper leads with is a
methodological choice that has to be made explicitly, not by picking the flattering table.

## 2. The new mechanism-bearing fact: optimal α₀ *decreases* with granularity

The α₀ dependence is not a common shift — it has a different shape per arm:

| arm | ep→90 vs α₀ (1e-6 → 1e-4 → 1e-3) | shape | best α₀ |
|---|---|---|---|
| scalar | 32.5 → 28.0 → **17.0** | monotone improving | 1e-3 (or higher) |
| 6-block | 29.5 → 27.0 → **18.5** | monotone improving | 1e-3 (or higher) |
| layerwise | 26.5 → **18.0** → 33.5 | **U-shaped** | 1e-4 |

Layerwise is the only arm that is *hurt* by α₀=1e-3, and it is hurt badly — 33.5 epochs and
91.01 accuracy, the worst cell in the whole sweep. So **the finer the partition, the lower the
step-size initialisation it wants.**

That is mechanistically coherent with everything else in this campaign. A finer partition has
more parallel meta-gradient signal and adapts α upward faster, so it needs less help from the
initialisation — and starting it high overshoots per-group before the meta-optimizer can pull
individual groups back. It also explains why layerwise looked best at α₀=1e-6: that is nearer
*its* optimum than the coarse arms'.

**Consequence for the comparison protocol.** A single shared α₀ across granularities is not a
neutral choice — it necessarily favours whichever arm's optimum it happens to sit near. Any
headline comparison from here must either (i) fix α₀ and say so, or (ii) tune α₀ per arm at
equal budget. This is the same fairness objection recorded against `meta_stepsize` in the very
first "Open confound" note, and it now has a measured instance.

## 3. This is exactly the parent paper's §7.3 null, one level deeper

Our unifying result already predicted that AdamW's per-coordinate normalisation leaves
granularity nothing to contribute (H4). The tuned-α₀ tie is that prediction landing on the
nose: on AdamW + Adam, once α₀ is tuned per arm, m=1, m=6 and m=62 are indistinguishable in
speed and scalar is best in accuracy.

**So the decisive experiment is no longer here.** It is `a0h-*` — the same α₀ ladder under
**SGDm + Lion**, the configuration where granularity actually buys +3.5pp and where the
project's hierarchical proposal lives. If the shrink win survives per-arm α₀ tuning there,
the proposal is real; if it collapses the way this AdamW sweep did, the campaign's best result
is an initialisation artifact. That job set is now running (see §6).

## 4. λ curve — CONFIRMED at n=2: full pooling wins, partial pooling is strictly worse

SGDm + Lion, layerwise, guard on, α₀=1e-6. Both seeds complete except λ=1.0 s1 (59 epochs,
ep→90 already crossed so the primary metric is valid):

| λ | half-life (steps) | ep→90 (n=2) | best |
|---|---|---|---|
| plain (no pooling) | ∞ | 54.7 (n=3) | 91.39 ± 0.19 |
| 0.001 | 693 | 48.0 | 92.60 ± 0.24 |
| 0.01 | 69 | **41.0** | **92.73 ± 0.07** |
| 0.1 | 7 | 41.5 | 92.53 ± 0.04 |
| 0.5 | 1 | 41.5 | 92.57 ± 0.08 |
| 1.0 | 0 (exact) | 41.5 | 92.68 † |

Everything from λ=0.01 to λ=1.0 is flat to within 0.5 epochs and 0.2pp. The single genuinely
*partial* value — λ=0.001, whose 693-step half-life is comparable to the run length — is the
only one that sits apart, and it sits **toward plain** (48.0 epochs, not 41).

**The ordering is monotone in pooling strength with the optimum at full pooling.** The
"hierarchical shrinkage with a tunable coefficient" framing is now refuted at n=2, not just
suggested at n=1: no interior λ is preferred, and moving λ toward the partial regime moves the
result back toward the unpooled arm. The contribution must be stated as **"averaging the
meta-gradient over a partition beats both the scalar arm and the unpooled partition"**, with λ
documented as a knob that is flat wherever it matters.

## 5. The sign explanation is REFUTED on complete runs, and the win is ~3× larger without sign

Both α₀=1e-6 layerwise arms under **Adam** meta have now finished 100 epochs:

| meta-optimizer | plain ep→90 | shrink λ=0.1 ep→90 | gain | plain best | shrink best |
|---|---|---|---|---|---|
| Lion (sign) | 54.7 (n=3) | 41.5 (n=2) | **13.2 epochs** | 91.39 | 92.53 |
| **Adam (non-sign)** | 56 (n=1) | 20 (n=1) | **36 epochs** | 90.68 | 92.29 |

The prediction on record was that the win should *shrink or vanish* without the sign
nonlinearity. It nearly triples. **The sign explanation is wrong**, now on completed runs
rather than in-flight ones. Whatever pooling buys, it is a property of the per-group
meta-gradient estimate itself — its variance — not of how the meta-optimizer consumes it.
Seed 1 of the shrink arm is at ep→90 = 19, consistent. Seeds 1–2 of both arms are queued; the
refutation should not be written up below n=3, but the *original* sign mechanism should not be
written up at all.

## 6. Pooling on 6-block: accuracy-positive, speed-negative (corrects a preliminary note)

`h2-b-L0p1_s0` finished. The previous section read it at 56 epochs as "neutral-to-harmful
(90.52)"; completed, it is neither:

| 6-block (m=6) | ep→90 | best | final |
|---|---|---|---|
| plain | 43.5 | 91.56 ± 0.03 | — |
| + shrink λ=0.1 | 54 | **92.16** | 91.86 |

Pooling m=6 **costs 10 epochs of speed and buys +0.6pp of accuracy** — not the flat null the
in-flight snapshot suggested. So the "pooling helps only at intermediate granularity" shape
needs restating with the two metrics separated:

| m | pooling effect on **speed** | pooling effect on **accuracy** |
|---|---|---|
| 6 | **hurts** (43.5 → 54) | helps (+0.6pp) |
| 62 | **helps** (54.7 → 41.5) | helps (+1.1pp) |
| 11.17M | n/a (never reaches 90%) | **catastrophic** (79.4 → ~49) |

Only m=62 is helped on both axes. Seeds 1–2 are queued (s1 running); this is n=1 and the
+0.6pp is ~4× the seed sd of the plain arm but has no error bar of its own yet.

## 7. Queue actions taken this cycle

* **`a0h-*` (15 jobs) unblocked.** The SGDm α₀ control — the experiment §3 identifies as
  decisive — was pending at the bottom of a 46-deep queue on a 2080ti partition with two nodes
  in maintenance. Its 5:00:00 walltime was ~3× the measured 2080ti run time (89 min for 100
  epochs), which locked it out of `gpu-short` (4 h cap) where 2080ti capacity was idle. Reduced
  to 3:45:00 and given `Partition=gpu-2080ti-11g,gpu-short` with `--gres=gpu:2080_ti:1`
  retained, so GPU type — and therefore timing comparability across the a0h block — is
  unchanged. **Five cells started immediately**; running jobs on the account went 3 → 8.
* **`a0h-blk6-*` (5 jobs) submitted** to complete that design. `a0h` covered
  {scalar, layerwise plain, layerwise shrink} but omitted **6-block**, which is both the
  campaign's best plain arm under SGDm (91.56) and the paper's own partition — without it the
  α₀-controlled SGDm comparison could not reproduce the granularity *ordering*, only a
  two-point contrast. Same base/meta/guard/GPU/walltime as the rest of the block.
* **17 low-value jobs deprioritised** (`nice=5000`, not cancelled — they still run when the
  queue drains): the three `sm-ResNet*` scale smokes, five third seeds of λ cells that are
  already n=2 and mutually indistinguishable, and the nine `h2-lam{003,01,03}` cells, which
  re-measure λ ∈ {0.03, 0.1, 0.3} — entirely inside the plateau §4 has now confirmed twice.

## 8. Standing caveats unchanged by this cycle

* Every number above is **CIFAR-10 / ResNet-18 only**. The scale ladder is not started and
  ImageNet remains blocked on the absent devkit (`val` labels), not on the missing 511 classes.
* The **stability** claim is still confounded by the guard; `g4-*` (15 jobs, alice2) is queued
  behind the a0 sweep and has not started. It is untouched by this cycle's α₀ result, but note
  that a stability claim will eventually need its own α₀ control too.
* The **language modality** is still blocked on the validation-gated optimizer port
  (`tinystories/HF.py` carries neither patch and has the dead-granularity defect independently).

---

# 19 Aug 2026 (cycle 3) — the α₀ control completes at n=3, and the sign refutation becomes the campaign's largest effect

23 new runs landed and 10 in-flight runs completed. Three things resolve; one preliminary
result points the opposite way to the last cycle's headline, which is the point of it.

## 1. α₀ control under AdamW + Adam — COMPLETE at n=3, and the n=2 reading holds

The paper's exact CIFAR-10 config, SwiftTD guard on, augmented, 100 epochs, L4, **all nine
cells now n=3 and all 27 runs at a full 100 epochs.** PRIMARY metric ep→90, ± seed sd:

| α₀ | scalar | 6-block | layerwise |
|---|---|---|---|
| 1e-6 | 32.3 ± 2.5 | 30.7 ± 2.1 | **27.0 ± 1.0** |
| 1e-4 | 27.3 ± 1.5 | 29.3 ± 4.5 | **19.3 ± 2.5** |
| 1e-3 | **17.0 ± 1.0** | 18.7 ± 0.6 | 33.0 ± 4.6 |

Best test accuracy over the same 27 runs:

| α₀ | scalar | 6-block | layerwise |
|---|---|---|---|
| 1e-6 | 92.09 ± 0.06 | 92.03 ± 0.18 | 91.98 ± 0.12 |
| 1e-4 | 92.29 ± 0.09 | 92.03 ± 0.18 | 92.25 ± 0.18 |
| 1e-3 | **92.94 ± 0.16** | 92.19 ± 0.06 | 91.07 ± 0.17 |

**Both of the previous cycle's readings survive the third seed, with one sharpened.**

**(a) At fixed α₀ ≤ 1e-4 the granularity speed win is real and larger than the campaign
reported.** At α₀=1e-4, layerwise 19.3 ± 2.5 against scalar 27.3 ± 1.5 — **29% fewer epochs**,
a ~3.4σ separation, versus the 19% quoted at α₀=1e-6. Raising α₀ off the campaign's value
*strengthens* the effect. (The n=2 snapshot said 36%; the third seed pulls it to 29%, still
comfortably outside noise.)

**(b) At each arm's own best α₀ the speed advantage is a three-way tie — and accuracy favours
the scalar arm outright.** Tuned per arm: scalar **17.0 ± 1.0** (@1e-3), 6-block 18.7 ± 0.6
(@1e-3), layerwise 19.3 ± 2.5 (@1e-4). The scalar-vs-layerwise gap is 2.3 epochs against a
pooled se of 1.6 (Welch t = 1.5, n=3) — **not resolvable at this seed count**, so this must be
reported as a tie and not, as the raw means invite, as a monotone penalty in m.

Accuracy is a different story and is *not* a tie: **92.94 ± 0.16 (scalar) vs 92.25 ± 0.18
(layerwise) and 92.19 ± 0.06 (6-block)** — a 0.69pp scalar advantage at ~4σ. So under an equal
per-arm α₀ tuning budget on AdamW + Adam, granularity buys **nothing on speed and loses
0.7pp on accuracy.**

## 2. Optimal α₀ falls as the partition gets finer — CONFIRMED at n=3

The α₀ response has a different *shape* per arm, and the third seed does not soften it:

| arm | ep→90 across α₀ (1e-6 → 1e-4 → 1e-3) | shape | best α₀ |
|---|---|---|---|
| scalar | 32.3 → 27.3 → **17.0** | monotone improving | 1e-3 (or higher) |
| 6-block | 30.7 → 29.3 → **18.7** | monotone improving | 1e-3 (or higher) |
| layerwise | 27.0 → **19.3** → 33.0 | **U-shaped** | 1e-4 |

Layerwise is the only arm *hurt* by α₀=1e-3, and the damage is far outside noise: 33.0 ± 4.6
epochs and 91.07 ± 0.17 accuracy, the worst cell in the sweep on both metrics. **The finer the
partition, the lower the step-size initialisation it wants** — mechanistically coherent, since
a finer partition has more parallel meta-gradient signal to grow α with and needs less help
from the initialisation, while a high start overshoots per-group before the meta-optimizer can
pull individual groups back.

**Protocol consequence, now measured rather than argued.** A single shared α₀ across
granularities is not a neutral choice: it necessarily favours whichever arm's optimum it sits
nearest, which is exactly why layerwise looked best at the campaign's α₀=1e-6. Every headline
comparison from here must either fix α₀ *and say so*, or tune α₀ per arm at equal budget.

## 3. The sign refutation is now the campaign's largest effect (n=3 on the shrink arm)

SGDm base + **Adam** meta (non-sign), layerwise, guard on, α₀=1e-6, augmented:

| meta | plain ep→90 | shrink λ=0.1 ep→90 | speed-up | plain best | shrink best |
|---|---|---|---|---|---|
| Lion (sign) | 54.7 ± 7.5 (n=3) | 41.5 ± 0.7 (n=2) | 13.2 ep (24%) | 91.39 ± 0.19 | 92.53 ± 0.04 |
| **Adam (non-sign)** | **58.0 ± 2.8** (n=2) | **19.3 ± 0.6** (n=3) | **38.7 ep (67%)** | 90.79 (n=2) | **92.22 ± 0.08** |

The prediction on record was that the pooling win should *shrink or vanish* without the sign
nonlinearity. It is **2.9× larger** — 38.7 epochs at ~14σ, plus +1.4pp accuracy. **The sign
explanation is refuted**, and this is now the strongest single result in the campaign. Whatever
pooling buys is a property of the per-group meta-gradient estimate itself — its variance — not
of how the meta-optimizer consumes it. (Shrink is n=3 with seeds 20/19/19; plain is n=2 with
56/60, its third seed in flight at epoch 24.)

**And it is the result with no α₀ control at all** — which is what this cycle's launch fixes
(§6).

## 4. Pooling on 6-block — CONFIRMED at n=3, and it is a genuine speed/accuracy trade

`h2-b-L0p1` reached n=3. The n=1 reading was right in both directions and now has error bars:

| 6-block (m=6), SGDm+Lion | ep→90 | best |
|---|---|---|
| plain | 43.0 ± 2.0 | 91.56 ± 0.03 |
| + shrink λ=0.1 | **53.3 ± 3.1** | **92.12 ± 0.12** |

Pooling m=6 **costs 10.3 epochs of speed (~3σ) and buys +0.56pp of accuracy (~6σ)**. Both
effects are real. The granularity-dependence of pooling therefore stands as:

| m | pooling effect on **speed** | pooling effect on **accuracy** |
|---|---|---|
| 6 | **hurts** (43.0 → 53.3) | helps (+0.56pp) |
| 62 | **helps** (54.7 → 41.5 Lion; 58.0 → 19.3 Adam) | helps (+1.1 / +1.4pp) |
| 11.17M | n/a (never reaches 90%) | **catastrophic** (79.4 → ~49) |

Only m=62 is helped on both axes, and only m=62 is helped a lot.

## 5. The guard does NOT rescue the diverging scalar arm — the stability claim survives its confound

`g4-sgdmAdam-*` is the guard-on rerun of `g3` (guard off), same base/meta/α₀/augmentation.
This was flagged as the outstanding confound on the stability claim: if the SwiftTD guard alone
rescued the collapsing seeds, "granularity stabilises training" would have been a numerical
artifact. **It does not.**

| SGDm + Adam, scalar, α₀=1e-6 | best test per seed |
|---|---|
| g3, guard **off** (100 ep each) | 88.45 / **18.47** / **20.71** |
| g4, guard **on** (in flight, 56/37/11 ep) | 87.76 / **19.06** / **20.81** |

Two of three seeds collapse to ~19–21% **with the guard on**, reproducing the unguarded
pattern almost value-for-value. Meanwhile the granular arms in the same guarded block are
healthy (layerwise 89.87 / 88.58; 6-block 90.60 / 89.19, both still climbing).

**So the collapse the granular arms are immune to is not the β-overflow artifact the guard
fixes.** This de-confounds the stability claim rather than weakening it. Caveat: g4 is
in-flight (11–56 epochs); g3's seeds stayed collapsed through all 100 epochs, so the pattern is
stable once established, but this should be restated at completion.

## 6. The decisive SGDm α₀ ladder — first seeds, and they point the OTHER way from §1

`a0h-*` is the α₀ control under **SGDm + Lion**, the configuration where granularity actually
buys accuracy and where the hierarchical proposal lives. **n=1 per cell, runs still in flight**
(61–77 of 100 epochs), so this is preliminary — but the direction is already opposite to §1(b):

| α₀ | scalar | layerwise plain | layerwise + shrink λ=0.1 | shrink gain |
|---|---|---|---|---|
| 1e-6 | (in flight) | 51 | **42** | −9 ep (−18%) |
| 1e-3 | **no 90% by ep 61** (best 87.70) | 40 | **24** | −16 ep (−40%) |

**The shrink win does not merely survive a saner α₀ under SGDm — it grows**, from 18% to 40%
fewer epochs, while the scalar arm at α₀=1e-3 has not reached 90% at all by epoch 61. This is
the mirror image of the AdamW result in §1(b), where per-arm α₀ tuning erased the granularity
advantage entirely.

If it holds at n=2 (seeds queued, plus the four 6-block cells and the 1e-4 row), the campaign's
unifying claim survives its own fairness objection in the configuration that matters, and the
**base optimizer — not α₀ — is the controlling variable.** That is the H4 story the campaign
already tells: AdamW's per-coordinate normalisation leaves granularity nothing to contribute,
so the AdamW null in §1(b) is a *prediction landing*, not a refutation.

**Do not write up §1(b) as "granularity buys nothing" without §6 beside it.** They are the same
experiment on two base optimizers and they disagree, which is the finding.

## 7. Queue actions this cycle

* **All 20 `a0h` jobs verified alive** — 5 running, 15 pending, none failed. An earlier
  `squeue | tail` reading that appeared to show 9 missing cells was a truncated listing;
  `sacct` confirms the full block is intact.
* **`a0A-*` (20 jobs) launched on `alice2`** — the α₀ ladder for the **Adam-meta** arm, which
  §3 just made the campaign's largest effect and which has no α₀ control whatsoever. Mirrors
  `a0h` cell-for-cell (SGDm base, guard, augment, 100 epochs, 2080ti pin, 3:45:00, dual-partition
  per gotcha 12) with Adam meta substituted, **and with the 6-block arm included from the
  start** — `a0h` had to be patched later to add it. Design: {scalar, 6-block, layerwise plain,
  layerwise shrink λ=0.1} × α₀ ∈ {1e-3, 1e-4} × 2 seeds, plus a 4-cell α₀=1e-6 anchor row at
  seed 0 that ties the block back to the L4 `h2A` numbers across GPU types.
  Launcher: `bin/a0A_sweep.sh` on `alice2`.
* **Placed on `alice2` deliberately.** Its 2080ti allowance (cap 12) was entirely unused while
  its L4 allowance sat at the cap (8 running, `QOSMaxGRESPerUser` on the 9th) — the additive-cap
  situation of gotcha 13.
* **Pre-flight checks passed before submitting:** `HF.py` is byte-identical across the local
  canonical copy and *both* accounts (md5 `6d10d14b…`, 444 lines), and `alice2`'s `run_cifar.sh`
  emits the `ENV:` provenance line. Gotcha 10 says to check this every time; it cost one SSH
  round-trip and would have invalidated 20 runs silently.

## 8. The cluster is saturated — queue depth, not job count, is the binding constraint

Every GPU partition ALICE offers is fully allocated: `gpu-l4-24g` 7/7 nodes, `gpu-2080ti-11g`
6 usable of 9 (2 `maint`, 1 `drain$`), **all four `gpu-a100-80g` nodes at full `gres/gpu`
allocation, and `gpu-mig-40g` with exactly one free slice across six nodes.** Both accounts are
at or near their effective limits (alice 8 running, alice2 8 + cap-blocked).

**Consequence for this campaign: submitting more jobs does not add throughput, it adds queue
depth.** The A100 and MIG allowances, which no earlier cycle had touched and which looked like
free capacity, are not free. The levers that *do* work are the ones already recorded — right-size
`--time` into `gpu-short` (gotcha 12), use the additive per-GPU-type caps (gotcha 13), and `nice`
the low-value work rather than cancelling it (gotcha 14). This cycle's 20-job launch is queued
against those caps and will drain as capacity frees, which is the intended behaviour.

## 9. Standing caveats unchanged by this cycle

* Every number above is **CIFAR-10 / ResNet-18 only**. The scale ladder has not started.
* **ImageNet stays scoped out.** The on-disk copy is 489/1000 classes and, decisively, the
  devkit is absent, so the 50,000 flat `val` JPEGs cannot be labelled from anything on disk.
* The **language modality** is still blocked on the validation-gated optimizer port.
  `tinystories/HF.py` carries neither patch and has the dead-granularity defect independently;
  pretokenization is done (50/50 shards, 8.5 GB).
* `h2-w-L1e4` / `h2-w-L1e5` — the only *genuinely partial* λ values on weightwise (half-lives
  6,931 and 69,315 steps against ~50,000 steps in a run) — are 1 running / 3 pending. The λ
  curve is otherwise confirmed flat with the optimum at full pooling.

---

# 19 Aug 2026 (cycle 4) — the hierarchy question closes, and last cycle's stability reading is corrected

15 new runs landed and 16 in-flight runs completed (182 runs aggregated, up from 167).
Two campaign questions close outright, one previous claim is **wrong and corrected here**, and
the decisive SGDm α₀ ladder returns its first complete seed.

## 1. CLOSED — hierarchy does not close the per-weight deficit, at any pooling strength

The weightwise pooling ladder is now measured across **six decades of λ**, including the two
genuinely-partial values whose absence invalidated the first sweep. SGDm + Lion, guard on,
augmented, α₀=1e-6, 100 epochs:

| variant | pooling half-life (steps) | best test | n |
|---|---|---|---|
| plain + guard — **no pooling** | ∞ | **79.38 ± 0.46** | 3 |
| M0 shrink λ=1e-5 | 69,315 | 78.98 ± 0.17 | 2 |
| M0 shrink λ=1e-4 | 6,931 | 70.23 ± 0.15 | 2 |
| M1 additive r=0.3 | — | 66.61 ± 0.74 | 2 |
| M1 additive r=0.1 | — | 51.30 ± 2.03 | 2 |
| M0 shrink λ=0.01 | 69 | 49.73 ± 3.51 | 2 |
| M0 shrink λ=0.1 | 7 | 49.07 ± 3.75 | 2 |
| M0 shrink λ=0.5 | 1 | 49.06 ± 3.80 | 2 |

Three things make this decisive rather than suggestive:

1. **The operator is verified, not assumed.** λ=1e-5 has a 69,315-step half-life against
   ~50,000 steps in a run — i.e. it is *effectively no pooling* — and it recovers the unpooled
   arm to within 0.4pp (78.98 vs 79.38). The shrink operator does what it says.
2. **λ=1e-4 is the first genuinely partial value ever measured on weightwise** (half-life 6,931
   steps, ~7 half-lives per run) and it already costs **9.2pp**. The partial-pooling regime the
   first sweep never reached is now measured, and it is monotonically harmful from the first
   step away from zero.
3. **Two independently-parameterised mechanisms interleave on one monotone curve.** Ordering by
   pooling strength: `79.4 (none) → 79.0 (λ1e-5) → 70.2 (λ1e-4) → 66.6 (r=0.3) → 51.3 (r=0.1)
   → ~49 (λ≥0.01)`. M0 and M1 share no parameterisation, so the controlling variable is
   *pooling strength itself*, not either operator's particular form.

**There is no interior optimum and no beneficial regime.** The project's proposed fix does not
close the ~12pp per-weight deficit; monotonically in pooling strength it widens it to ~30pp.
This question needs no further compute — priority item 1 is answered, in the negative, and the
negative is now firm rather than confounded by a saturated sweep.

## 2. CORRECTION — the guard rescues one of the two collapsing scalar seeds

Last cycle recorded, from an **in-flight** snapshot (seeds at 56/37/11 epochs), that "two of
three seeds collapse to ~19–21% with the guard on, reproducing the unguarded pattern almost
value-for-value." **All three seeds have now run the full 100 epochs and that is wrong.**
Seed 2 was read at epoch 11 while at 20.81; it recovered.

SGDm + **Adam** meta, α₀=1e-6, scalar, 100 epochs, n=3:

| | seed 0 | seed 1 | seed 2 | collapsed |
|---|---|---|---|---|
| g3, guard **OFF** | 88.45 | **18.47** | **20.71** | 2/3 |
| g4, guard **ON** | 88.12 | **20.89** | 86.78 | **1/3** |

So the SwiftTD guard **halves** the scalar collapse rate but does not remove it. This is a
weaker statement than the one on record and it is the right one.

### The stability claim survives — but state it on the primary metric, not on collapse counts

Counting collapses undersells the effect and depends on an arbitrary threshold. On
epochs-to-target, with the **guard on** throughout, the picture is unambiguous:

| arm (guard ON) | reaches 85% | reaches 88% | reaches 90% | best |
|---|---|---|---|---|
| **scalar** | 2/3 (ep 23, 78) | **1/3** (ep 69) | **0/3** | 65.26 ± 38.43 |
| layerwise | 3/3 (14, 15, 15) | 3/3 (26, 26, 27) | **3/3** (59.7 ± 0.6) | 90.79 ± 0.06 |
| 6-block | 3/3 (15, 16, 15) | 3/3 (19, 21, 21) | **3/3** (42.0 ± 9.5) | 90.94 ± 0.12 |

**With a published guard already in place, the scalar arm of the parent paper's own
configuration reaches 90% on zero of three seeds; both granular arms reach it on three of
three.** And seed 2's "recovery" is a wounded one — it crosses 85% only at epoch 78 and never
reaches 88% — so treating it as a healthy run flatters the scalar arm.

The confound flagged on 19 Aug is therefore **resolved in the claim's favour, at n=3 and with
the correction above applied**: granularity's stability benefit is not a repackaging of the
guard, because the guard alone leaves the scalar arm unable to reach the target at all. The two
interventions overlap partially and neither substitutes for the other.

## 3. The campaign's largest effect is COMPLETE at n=3 on both arms

`h2A-l-plain` seed 2 finished, so both arms of the Adam-meta contrast are n=3 at 100 epochs.
SGDm base + **Adam** meta (non-sign), layerwise, guard on, α₀=1e-6:

| arm | ep→90 (n=3) | best (n=3) |
|---|---|---|
| plain | 61.0 ± 5.6 (56/60/67) | 90.71 ± 0.17 |
| **+ M0 shrink λ=0.1** | **19.3 ± 0.6** (20/19/19) | **92.22 ± 0.08** |

**41.7 fewer epochs — 68% — at Welch t = 12.9, plus +1.51pp accuracy at t = 14.0.** The third
plain seed (67) widens the plain arm's spread and slightly *grows* the effect over last cycle's
n=2 reading (38.7 epochs). This is the strongest result in the campaign and it is now complete.

It also completes the **refutation of the sign explanation**, which required n=3 before it could
be written up. Against the same contrast under Lion, using the *matched* baseline (§4):

| meta-optimizer | plain ep→90 | shrink ep→90 | speed-up |
|---|---|---|---|
| Lion (sign) | 58.3 ± 2.3 | 41.5 ± 0.7 | 16.8 ep (29%), t = 11.8 |
| **Adam (non-sign)** | 61.0 ± 5.6 | **19.3 ± 0.6** | **41.7 ep (68%), t = 12.9** |

The prediction on record was that pooling's win should *shrink or vanish* without the sign
nonlinearity. It is **2.5× larger**. Whatever pooling buys is a property of the per-group
meta-gradient estimate — its variance — not of how the meta-optimizer consumes it. Both the
original sign mechanism and its refutation are now at n=3; **the mechanism should not be written
up, the refutation may be.**

## 4. A matched plain baseline tightens the Lion-meta contrast (and moves it)

`h2-base` is layerwise-plain submitted on the *same seeds and same launcher* as the h2 shrink
cells, rather than reusing the older `d4_clipL` block:

| baseline | ep→90 | best | n |
|---|---|---|---|
| `d4_clipL` (older, used in every previous table) | 54.7 ± 7.5 | 91.39 ± 0.19 | 3 |
| **`h2-base` (matched)** | **58.3 ± 2.3** | 91.27 ± 0.16 | 3 |

The two agree on accuracy to within noise but the matched baseline's ep→90 is **3.6 epochs
slower and 3× tighter**. Every Lion-meta pooling speed-up quoted against `d4_clipL` is therefore
a slight *under*statement: the win is 16.8 epochs (29%), not the 13.2 (24%) on record. Use
`h2-base` as the Lion plain baseline from here.

## 5. 6-block pooling — confirmed at n=6 across two independent submissions

`h2-b-L0p1` (n=3, complete) and `h2-blk6` (n=3, two seeds at 84/92 epochs but past ep→90, so
the primary metric is valid) are the same configuration submitted twice. They agree closely
(ep→90 53.3 ± 3.1 and 52.7 ± 2.5; best 92.12 ± 0.12 and 91.94 ± 0.36), so they are pooled:

| 6-block (m=6), SGDm + Lion | ep→90 | best | n |
|---|---|---|---|
| plain | 43.0 ± 2.0 | 91.56 ± 0.03 | 3 |
| + shrink λ=0.1 | **53.0 ± 2.5** | **92.03 ± 0.26** | 6 |

Pooling m=6 **costs 10.0 epochs of speed (t = 6.5) and buys +0.47pp of accuracy (t = 4.4)**.
Both effects are real, in opposite directions, now at n=6. The granularity-dependence of
pooling stands as:

| m | pooling effect on **speed** | pooling effect on **accuracy** |
|---|---|---|
| 6 | **hurts** (43.0 → 53.0) | helps (+0.47pp) |
| 62 | **helps** (58.3 → 41.5 Lion; 61.0 → 19.3 Adam) | helps (+1.26 / +1.51pp) |
| 11.17M | never reaches 90% at any λ | **monotonically catastrophic** (79.4 → ~49) |

Only m=62 is helped on both axes, and only m=62 is helped a lot.

## 6. The decisive SGDm α₀ ladder — seed 0 complete, and it points opposite to the AdamW ladder

`a0h-*` at 100 epochs, seed 0, SGDm + Lion, guard on, augmented (n=1 — **preliminary**):

| α₀ | scalar | layerwise plain | layerwise + shrink λ=0.1 |
|---|---|---|---|
| 1e-6 | *(pending)* | 51 / 91.28 | **42** / 92.53 |
| 1e-3 | **never reaches 90%** (best 88.28) | 40 / 91.76 | **24** / 92.50 |

Set beside the completed AdamW + Adam ladder (n=3), the two configurations disagree on every
axis that matters:

| | AdamW + Adam (n=3) | SGDm + Lion (n=1) |
|---|---|---|
| best arm at α₀=1e-3 | **scalar** (17.0 ± 1.0, 92.94 ± 0.16) | **layerwise + shrink** (24; scalar never reaches 90%) |
| effect of α₀=1e-3 on layerwise | **hurts badly** (27.0 → 33.0, U-shaped) | **helps** (51 → 40, monotone) |
| per-arm-tuned comparison | three-way tie; scalar best on accuracy | scalar cannot reach the target at all |

**Two consequences, both preliminary at n=1 but both directional.**

**(a) The campaign's central claim survives its own fairness objection in the configuration
that matters.** Under SGDm, giving the scalar arm its own best α₀ does not rescue it — it fails
to reach 90% in 100 epochs at α₀=1e-3, having also failed at α₀=1e-6. Per-arm α₀ tuning erased
the granularity advantage under AdamW; it does not under SGDm. That is the H4 story landing:
**the base optimizer, not α₀, is the controlling variable.**

**(b) "Optimal α₀ falls as the partition gets finer" does NOT generalise across base
optimizers.** That claim was confirmed at n=3 — but only on AdamW + Adam, where layerwise is
U-shaped in α₀ and uniquely hurt at 1e-3. Under SGDm + Lion layerwise is *monotone improving*
across the same range, plain and shrink alike. **The rule as written in cycle 3 is
over-generalised and must be restated as an AdamW result until the SGDm ladder completes.**

## 7. Queue actions this cycle

* **`a0L-*` (24 cells) submitted and 10 started within a minute.** The SGDm + Lion α₀ ladder,
  **complete and self-contained on one GPU type**: {scalar, 6-block, layerwise plain, layerwise
  shrink λ=0.1} × α₀ ∈ {1e-3, 1e-4, 1e-6} × seeds {0,1}. This exists because `a0h` — the same
  question on 2080ti — is 14/20 still pending behind a saturated partition and has delivered
  seed 0 only, at two α₀ values, for three of the four arms: it carries **no 1e-4 row and no
  6-block arm at any seed**, so it cannot reproduce the granularity *ordering* at a given α₀,
  only a two-point contrast. `a0L` can. `a0h` on 2080ti now serves as independent cross-GPU-type
  replication rather than as the primary measurement.
* **The binding constraint was partition eligibility, not capacity.** `node887` sat **IDLE with
  4 free L4 GPUs** while 32 of our jobs pended, because it belongs to `gpu-short` only and every
  pending L4 job was pinned to `gpu-l4-24g`. Submitting `a0L` as
  `--partition=gpu-l4-24g,gpu-short --gres=gpu:l4:1` (gotcha 12) filled node887, node886,
  node885, node881 and node880 immediately: **running jobs on `alice` went 1 → 11.**
* **`--time` sized from measurement, not habit.** 140 completed 100-epoch L4 runs span 30–48
  min, so `a0L` asks 2:00:00 — 2.5× the slowest ever recorded and comfortably inside the
  `gpu-short` 4 h cap.
* **All 17 remaining L4-pinned pending jobs widened to `gpu-l4-24g,gpu-short`.** GRES stays
  pinned to `l4`, so within-block timing comparability is untouched (gotcha 3). Their walltimes
  (40:00 / 3:00:00) already fitted the 4 h cap; only the partition list was locking them out.
* **The three `sm-ResNet{34,50,101}` scale smokes un-niced.** They are 2-epoch probes costing
  ~5 min of GPU each and they are the only pending work that touches the campaign's largest
  standing caveat — every result to date is ResNet-18 only. The λ-plateau re-measures stay
  niced (gotcha 14).

## 8. Standing caveats after this cycle

* Every number remains **CIFAR-10 / ResNet-18**. The scale ladder is un-niced but has not run.
* **ImageNet stays scoped out** — 489/1000 classes and, decisively, no devkit, so the 50,000
  flat `val` JPEGs cannot be labelled from anything on disk.
* The **language modality** is still blocked on the validation-gated optimizer port;
  pretokenization is done (50/50 shards, 8.5 GB).
* §6 is **n=1**. `a0L` (24 cells) and the `a0h` remainder decide it; nothing from §6 may enter a
  draft yet, and in particular the cycle-3 "optimal α₀ falls with granularity" rule must be
  restated as AdamW-only in the meantime.
* `a0A-*` (20 cells, the α₀ control for §3's effect — the campaign's largest) is **entirely
  pending** on `alice2`'s 2080ti allowance. The single largest result in the campaign still has
  no α₀ control.

---

# 19 Aug 2026 (cycle 4, second pass) — the PRIMARY metric is threshold-sensitive, and it flatters the project's own proposal

This came out of a routine consistency check and it is the most consequential thing in this
cycle. **It does not threaten the campaign's central granularity claim. It does require the
project's own pooling result to be restated as something other than a speed-up.**

## 1. How it surfaced — two identical runs, 6 epochs apart on the primary metric

`a0h` was designed with an α₀=1e-6 row that duplicates existing L4 cells as a cross-GPU-type
anchor. Those anchors have now landed, and they are the same config *and the same seed*,
differing only in GPU type (argument order aside):

| config (seed 0, α₀=1e-6, guard, augmented) | GPU | best | ep→90 |
|---|---|---|---|
| layerwise **+ shrink λ=0.1** (`hs-l-lam01_s0` / `a0h-lsh01-1e6_s0`) | L4 / 2080ti | 92.55 / 92.53 | **42 / 42** |
| layerwise **plain** (`h2-base_s0` / `a0h-lplain-1e6_s0`) | L4 / 2080ti | 91.37 / 91.28 | **57 / 51** |

Accuracy replicates across GPU types to 0.02–0.09pp, consistent with the ±0.02pp determinism
floor — **so the campaign's GPU-independence assumption is sound.** But the *plain* arm's
epochs-to-90% differs by **6 epochs** between two runs that differ only in cuDNN
non-determinism, while the *pooled* arm's is identical. The primary metric is far noisier on
one arm than the other.

## 2. The cause — the unpooled arm asymptotes ON the 90% line

Counting how many of 100 epochs each arm spends inside the [89, 91] band, with its plateau
(mean test accuracy over the last 20 epochs):

| arm | n | epochs in [89,91] | plateau | ep→90 |
|---|---|---|---|---|
| layerwise plain (Lion) | 3 | **51 ± 3** | 90.83 ± 0.13 | 58.3 ± 2.3 |
| layerwise shrink (Lion) | 2 | **4 ± 0** | 92.27 ± 0.04 | 41.5 ± 0.7 |
| layerwise plain (Adam) | 3 | **61 ± 1** | 90.34 ± 0.08 | 61.0 ± 5.6 |
| layerwise shrink (Adam) | 3 | 18 ± 1 | 91.86 ± 0.11 | 19.3 ± 0.6 |

The unpooled arms converge to a plateau of **90.3–90.8%** — i.e. **the 90% threshold is drawn
through their own asymptote**, and they sit inside a ±1pp band around it for half to two-thirds
of the run. For those arms "epochs to 90%" is not measuring convergence speed at all; it is
measuring *when noise first nudged an already-converged curve over a line drawn through it*.
That is why it is late, high-variance, and irreproducible at fixed seed.

## 3. The consequence — the pooling speed-up reverses sign at lower thresholds

Recomputing every headline pooling contrast at all three thresholds instead of one:

### SGDm + Adam meta, layerwise (the campaign's largest effect)

| metric | plain (n=3) | shrink λ=0.1 (n=3) | gain |
|---|---|---|---|
| ep→85 | 15.0 ± 0.0 | 15.0 ± 0.0 | **0.0 ep (0%)** |
| ep→88 | 27.0 ± 0.0 | 16.0 ± 0.0 | +11.0 ep (41%) |
| ep→90 | 61.0 ± 5.6 | 19.3 ± 0.6 | +41.7 ep (68%) |
| **plateau** | 90.34 ± 0.08 | **91.86 ± 0.11** | **+1.52pp** |

### SGDm + Lion meta, layerwise

| metric | plain (n=3) | shrink λ=0.1 (n=2) | gain |
|---|---|---|---|
| ep→85 | 28.7 ± 0.6 | 35.5 ± 0.7 | **−6.8 ep (−24%), t = −11.4** |
| ep→88 | 35.7 ± 0.6 | 38.0 ± 1.4 | **−2.3 ep (−7%), t = −2.2** |
| ep→90 | 58.3 ± 2.3 | 41.5 ± 0.7 | +16.8 ep (29%), t = 11.8 |
| **plateau** | 90.83 ± 0.13 | **92.27 ± 0.04** | **+1.44pp** |

### SGDm + Lion meta, 6-block

| metric | plain (n=3) | shrink λ=0.1 (n=3) | gain |
|---|---|---|---|
| ep→85 | 30.0 ± 1.0 | 31.0 ± 1.0 | −1.0 ep (−3%) |
| ep→88 | 36.0 ± 1.0 | 39.0 ± 1.0 | −3.0 ep (−8%), t = −3.7 |
| ep→90 | 43.0 ± 2.0 | 53.3 ± 3.1 | −10.3 ep (−24%), t = −4.9 |

**Under Lion the sign of the pooling "speed-up" flips between 85% and 90%.** Pooled layerwise
is 24% *slower* to 85% at t = −11.4 — a larger, tighter effect than the +29% at 90% that the
campaign has been quoting — and 6-block pooling is slower at every threshold.

## 4. What this means, stated plainly

**Pooling is not an acceleration. It is a plateau effect.** The one thing it does at every
threshold, in every configuration, at 8–14σ, is raise the asymptote: +0.56pp (m=6), +1.26pp
(m=62, Lion), +1.51pp (m=62, Adam). The apparent speed-up is downstream of that: the unpooled
arm converges just below 90%, so a 90% threshold catches it late and erratically while the
pooled arm's higher plateau crosses it decisively and early.

The correct headline for the project's proposal is therefore:

> Averaging the meta-gradient over a partition **raises the accuracy plateau** by 0.6–1.5pp.
> It does not speed up early training — to 85% it is neutral (Adam meta) or measurably slower
> (Lion meta, −24%). Epochs-to-90% overstates the benefit because the unpooled arm's plateau
> sits on the 90% line.

The earlier note that the shrink arm is "slower early and faster late — the signature partial
pooling is supposed to have" recorded the right observation and drew the wrong conclusion from
it: the campaign then adopted ep→90 as the primary metric and reported that single threshold as
a speed claim. Both halves of that were a mistake, and this section is the correction.

## 5. What this does NOT threaten — the granularity claim is threshold-robust

The same recomputation on the *granularity* comparison (AdamW + Adam, the paper's exact
CIFAR-10 config, guard on, **n=3, all 27 runs at 100 epochs**):

| α₀ | arm | ep→85 | ep→88 | ep→90 |
|---|---|---|---|---|
| 1e-6 | scalar | 10.7 ± 1.2 | 19.0 ± 3.0 | 32.3 ± 2.5 |
| 1e-6 | 6-block | 10.3 ± 0.6 | 16.0 ± 1.0 | 30.7 ± 2.1 |
| 1e-6 | **layerwise** | **10.0 ± 0.0** | **15.0 ± 1.0** | **27.0 ± 1.0** |
| 1e-4 | scalar | 9.0 ± 1.0 | 15.0 ± 1.0 | 27.3 ± 1.5 |
| 1e-4 | 6-block | 9.3 ± 1.2 | 16.3 ± 2.5 | 29.3 ± 4.5 |
| 1e-4 | **layerwise** | **7.7 ± 0.6** | **12.7 ± 1.2** | **19.3 ± 2.5** |
| 1e-3 | **scalar** | 10.0 ± 1.0 | **13.0 ± 1.0** | **17.0 ± 1.0** |
| 1e-3 | 6-block | 8.3 ± 0.6 | 11.7 ± 0.6 | 18.7 ± 0.6 |
| 1e-3 | layerwise | 9.7 ± 0.6 | 15.0 ± 0.0 | 33.0 ± 4.6 |

**The ordering is the same at 85%, 88% and 90% in every α₀ row.** Layerwise leads at 1e-6 and
1e-4 on all three thresholds; scalar/6-block lead at 1e-3 on all three. These arms have
plateaus of 91–93%, comfortably above every threshold, so no threshold is drawn through an
asymptote. **Granularity is a genuine acceleration; the campaign's central claim, and the §7.3
ImageNet explanation that rests on it, are unaffected.**

The distinction is now sharp and should be preserved in the draft:

| comparison | nature of the effect | threshold-robust? |
|---|---|---|
| **granularity** (m = 1 → 6 → 62) | genuine acceleration | **yes** — same ordering at 85/88/90 |
| **pooling** (plain → shrink, fixed m) | **plateau shift**, not acceleration | **no** — sign flips between 85 and 90 |

## 6. Methodological rules this forces

1. **Never quote a single threshold.** Report ep→85 / ep→88 / ep→90 together, or the metric can
   be chosen to suit the conclusion. Every previous table in this document that quotes ep→90
   alone should be read with §3 in hand.
2. **Check the threshold against every arm's plateau before using it.** A threshold inside an
   arm's asymptote measures noise, not speed. Quote the plateau (mean of the last 20 epochs)
   next to the crossing epoch.
3. **Prefer thresholds below every arm's plateau, or report area under the accuracy curve.**
   At 88% — below all four layerwise plateaus — the Adam-meta contrast has *zero* seed variance
   on both arms (27.0 ± 0.0 vs 16.0 ± 0.0), against ±5.6 at 90%. The lower threshold is a
   dramatically better-conditioned estimator of the same effect.
4. **The ±0.02pp determinism floor does not transfer to epochs-to-target.** On a flat curve it
   becomes ~6 epochs (§1). Effect sizes in epochs must be judged against the *arm's own*
   threshold jitter, not against the accuracy floor.

---

# 19 Aug 2026 (cycle 5) — the decisive SGDm α₀ ladder lands, and the train curves expose a budget confound in BOTH headline claims

216 runs aggregated (up from 182): 34 new, 7 in-flight completed. The experiment cycle 3
identified as decisive — the α₀ ladder under **SGDm + Lion**, the configuration where
granularity actually buys accuracy and where the project's proposal lives — is **complete at
seed 0 on all twelve cells**. It answers the fairness objection in the campaign's favour.

Then a routine check of the *train* accuracy column shows that both of the campaign's headline
claims are measured at a budget where the losing arm has not finished fitting the training set,
which is the same confound the campaign's own unifying result is built on. That is not fatal to
either claim, but neither can be written up until it is controlled, and the control is now
running.

## 1. The SGDm + Lion α₀ ladder — COMPLETE at seed 0, and granularity survives per-arm tuning

`a0L-*`, all twelve cells at 100 epochs, guard on, augmented, L4, **n=1 (seed 0)**. Seed 1 is
in flight on all twelve. Per the cycle-4 threshold rule, ep→85/88/90 are quoted together and
each arm's plateau (mean test accuracy over the last 20 epochs) beside them:

| α₀ | arm | ep→85 | ep→88 | ep→90 | plateau | final train |
|---|---|---|---|---|---|---|
| 1e-6 | scalar | 39 | **never** | **never** | 87.73 | 93.74 |
| 1e-6 | 6-block | 29 | 38 | 41 | 91.43 | 99.09 |
| 1e-6 | layerwise plain | 28 | 38 | 52 | 90.84 | 99.69 |
| 1e-6 | layerwise + shrink λ=0.1 | 35 | 38 | 41 | **92.46** | 97.76 |
| 1e-4 | scalar | 27 | **never** | **never** | 87.73 | 93.77 |
| 1e-4 | 6-block | 20 | 27 | 33 | 91.55 | 99.22 |
| 1e-4 | layerwise plain | 19 | 26 | 45 | 90.89 | 99.78 |
| 1e-4 | layerwise + shrink λ=0.1 | 24 | 26 | 31 | **92.28** | 97.99 |
| 1e-3 | scalar | 24 | 66 | **never** | 87.89 | 94.03 |
| 1e-3 | 6-block | 15 | 21 | 29 | 91.64 | 99.30 |
| 1e-3 | layerwise plain | **13** | 23 | 38 | 91.23 | 99.88 |
| 1e-3 | layerwise + shrink λ=0.1 | 18 | 20 | **24** | **92.44** | 98.18 |

**The scalar arm does not reach 90% at any α₀ across three decades.** Its plateau is
87.73 / 87.73 / 87.89 — flat to 0.16pp while α₀ moves by a factor of 1000. Independently
replicated: `g4-sgdmLion-scal` (a separate submission, α₀=1e-6, n=2) gives plateaus 87.66 and
87.76 and never reaches 90% either, so the α₀=1e-6 scalar cell is effectively n=3.

**So the AdamW result does not transfer, and the fairness objection is answered.** Under
AdamW + Adam, giving each arm its own best α₀ erased the granularity advantage entirely and
left scalar best on accuracy (cycle 3 §1b). Under SGDm + Lion, giving the scalar arm its own
best α₀ moves its *speed* a lot (ep→85 39 → 27 → 24) and its *asymptote* not at all. The
granularity gap under SGDm is a plateau gap of 3.3–3.9pp, and α₀ does not touch it.

**The controlling variable is the base optimizer, not α₀** — which is the H4 story the campaign
has told since Gate 1, now measured on both sides of the contrast.

### The threshold-safe comparison

ep→90 is undefined for the SGDm scalar arm at every α₀, so it cannot be the metric here. At
**85%** — below all four plateaus — with every arm at its own best α₀ (which is 1e-3 for all
four, see §3):

| arm | ep→85 @ its best α₀ | plateau |
|---|---|---|
| layerwise plain | **13** | 91.23 |
| 6-block | 15 | 91.64 |
| layerwise + shrink λ=0.1 | 18 | 92.44 |
| scalar | 24 | 87.89 |

Granularity is a genuine acceleration under SGDm as well: layerwise reaches 85% in 13 epochs
against scalar's 24, **46% fewer**, at each arm's own best α₀. And pooling is *slower* than
plain (18 vs 13) while plateauing 1.21pp higher — the same speed/plateau split cycle 4's second
pass established at α₀=1e-6, now reproduced at α₀=1e-3.

## 2. ⚠ BOTH headline claims are measured while the losing arm is still fitting

The train column above is the new fact. Reading the last-20-epoch slope of *train* accuracy at
epoch 100:

| arm | train @ ep 100 | Δtrain per 10 ep | epoch train first ≥ 99% |
|---|---|---|---|
| SGDm+Lion scalar (α₀ 1e-6 / 1e-4 / 1e-3) | 93.74 / 93.77 / 94.03 | **+0.46 / +0.31 / +0.40** | **never reaches 97%** |
| layerwise plain (Lion, n=3) | 99.69 ± 0.06 | +0.16 | **ep 70** |
| layerwise + shrink λ=0.1 (Lion, n=4) | 97.81 ± 0.06 | **+0.34** | **never reaches 99%** |
| layerwise plain (Adam, n=3) | 99.75 ± 0.03 | +0.08 | ep 58 |
| layerwise + shrink λ=0.1 (Adam, n=3) | 97.98 ± 0.08 | **+0.22** | **never reaches 99%** |

Two claims are affected, in the same way, and it is the campaign's own unifying logic turned on
the campaign:

**(a) "Granularity beats scalar under SGDm" may be a RATE claim, not a CEILING claim.** The
scalar arm has never fit the training set — 94% train at epoch 100, still climbing at ~0.4pp
per 10 epochs, at every α₀. Its 87.7% test plateau is flat, but a *train* curve that is still
rising means the run was stopped mid-optimisation. Whether scalar converges to the granular
arms given more epochs is untested.

**(b) Pooling's +1.4pp may be a REGULARISATION gain or merely a slower fit.** The shrink arm's
*test* accuracy has converged (Δtest per 10 ep = −0.10 to +0.17, i.e. noise) while its *train*
accuracy is still climbing and never reaches 99%; the plain arm has finished fitting (99.7%,
99% crossed by epoch 58–70). The observed trade at a 100-epoch budget is a clean −1.9pp train
for +1.4pp test, and it reproduces almost exactly across two very different meta-optimizers
(Lion −1.88/+1.44, Adam −1.77/+1.52), which is what one mechanism looks like. But
"constrains the fit and generalises better" and "fits more slowly and generalises better *along
the way*" are not distinguishable while the train curve is still moving.

**Neither (a) nor (b) may go in a draft as an asymptotic statement until the budget control
reports.** The campaign has spent four cycles explaining the parent paper's ImageNet null as a
budget artifact; it would be indefensible to leave the same artifact unexamined in its own
headline.

### The control this forced — `ext300`, submitted this cycle

{scalar, layerwise plain, layerwise + shrink λ=0.1} × 2 seeds at **300 epochs**, SGDm + Lion,
guard on, augmented, **α₀=1e-3** (the best value for every SGDm+Lion arm, so the scalar arm is
given its best shot rather than the campaign's handicapping 1e-6). Six cells, L4, `bin/ext300.sh`.

**The extension is exactly comparable to the existing runs**, and this was verified rather than
assumed: `train.py` has **no learning-rate scheduler** — the only epoch-dependent terms in the
whole training loop are the loop bound and the time-based break, and the latter is neutralised
by `--max-time 999:00:00`. So epochs 1–100 of an `ext300` run are the identical computation to
the corresponding `a0L` α₀=1e-3 cell, and the 300-epoch runs read as continuations of them.

Predictions on record, so the result cannot be rationalised after the fact:
* If scalar converges toward the granular arms by epoch 300, the SGDm granularity gain is a
  **speed** effect and the campaign's unifying result covers *every* configuration it has
  measured, strengthening the §7.3 ImageNet explanation.
* If scalar stalls near 88%, granularity buys something **asymptotic** under SGDm that it does
  not buy under AdamW, and the unifying result needs a second clause.
* If the shrink arm's train reaches ~99.9% while it keeps its test advantage, pooling is a
  genuine generalisation gain.
* If its test advantage decays as it finishes fitting, the +1.4pp is a snapshot of a slower
  trajectory and the project's proposal has to be restated a third time.

## 3. The cycle-3 rule "optimal α₀ falls as the partition gets finer" is AdamW-ONLY — refuted under SGDm at 12/12 cells

Cycle 3 confirmed at n=3, on AdamW + Adam, that layerwise is U-shaped in α₀ and uniquely hurt
at 1e-3. Cycle 4 flagged that this might not generalise. It does not:

| arm | ep→85 across α₀ (1e-6 → 1e-4 → 1e-3) | shape under SGDm+Lion | shape under AdamW+Adam |
|---|---|---|---|
| scalar | 39 → 27 → 24 | monotone improving | monotone improving |
| 6-block | 29 → 20 → 15 | monotone improving | monotone improving |
| layerwise plain | 28 → 19 → 13 | **monotone improving** | **U-shaped (best 1e-4)** |
| layerwise + shrink | 35 → 24 → 18 | monotone improving | *(not measured)* |

Under SGDm + Lion **every arm, at every threshold, improves monotonically up to α₀=1e-3**, and
the plateaus move the same way or not at all (layerwise plain 90.84 → 90.89 → 91.23). The
U-shape that made "finer partitions want lower α₀" look mechanistic is a property of
AdamW + Adam, not of granularity.

**Restated correctly:** under AdamW + Adam the optimal α₀ falls as the partition gets finer;
under SGDm + Lion it does not, and 1e-3 is best for all four arms. The protocol consequence
from cycle 3 survives untouched and is if anything stronger — a single shared α₀ is not a
neutral choice, and *which* arm it flatters depends on the base optimizer.

## 4. The headline Lion pooling contrast reaches **n=5** — priority item 4 closed on this cell

Both arms completed seeds 3 and 4 during this cycle, so the campaign's central pooling contrast
is now at the five-seed target:

| SGDm + Lion, layerwise, α₀=1e-6, guard | n | ep→85 | ep→90 | plateau | final train |
|---|---|---|---|---|---|
| plain (`h2-base`) | **5** | 29.4 | 58.6 | 90.67 ± 0.23 | 99.66 ± 0.06 |
| **+ shrink λ=0.1** (`hs-l-lam01`) | **5** | 35.6 | 41.4 | **92.28 ± 0.06** | 97.78 ± 0.09 |

Nothing moves. Plateau gain **+1.61pp** against a pooled sd of ~0.17 (~9σ); pooling is **6.2
epochs slower to 85%**; the fit-vs-plateau trade is **−1.88pp train for +1.61pp test**. Cycle 4's
correction — pooling is a plateau effect, not an acceleration — holds at n=5, and the sign flip
between 85% and 90% is now measured on five seeds per arm rather than two.

The matching Adam-meta cell is n=3 plain / n=4 shrink (plateau 90.34 ± 0.08 vs 91.86 ± 0.09,
train 99.75 ± 0.03 vs 98.00 ± 0.07) — the same trade to within 0.1pp on both axes, from a
different meta-optimizer. Its fifth seeds are in flight.

The SGDm + Lion **scalar** arm also reached n=3 on an independent submission
(`g4-sgdmLion-scal`): plateau **87.81 ± 0.19**, final train **93.78 ± 0.24**, and **0 of 3 seeds
reach 90%** — which is the §1 α₀=1e-6 scalar cell replicated, and the direct evidence for §2(a)
that this arm has not finished fitting.

## 5. Pooling at m=6 is NOT the same phenomenon as at m=62

Separating the train and test columns splits the 6-block result away from the layerwise one:

| contrast | Δtrain (shrink − plain) | Δplateau | reading |
|---|---|---|---|
| layerwise m=62, Lion (n=3→4) | **−1.88** | **+1.44** | trades fit for test accuracy |
| layerwise m=62, Adam (n=3→3) | **−1.77** | **+1.52** | same trade, same size |
| 6-block m=6 (n=2→6) | **+0.32** | +0.34 | **no trade — both rise slightly** |
| weightwise m=11.17M (ladder) | train **falls with pooling**: 82.0 → 81.3 → 70.9 → 66.6 → 50.1 → ~47 | falls in lockstep, gap stays 2–4pp | **optimisation failure** |

Three distinct regimes, and only the middle one is the effect the project is claiming:
* At **m=62** pooling gives up training fit and gains test accuracy, identically under two
  meta-optimizers. Whether that is a constraint or a delay is what `ext300` decides (§2b).
* At **m=6** there is no trade at all — train and test both edge up by ~0.3pp. Whatever the
  small 6-block gain is, it is not the m=62 mechanism, and the two should not be described
  together.
* At **m=11.17M** train and test collapse *together* down the entire pooling ladder with the
  generalisation gap shrinking, which is neither overfitting nor regularisation — the model
  simply never fits the data. This is the cleanest statement yet of why the cycle-4 negative is
  a negative: pooling does not fail to help per-weight step sizes, it destroys their ability to
  optimise at all.

## 6. Under AdamW every arm fully fits, which is why granularity has nothing to add

The same train column on the completed AdamW + Adam ladder (n=3, all 27 runs at 100 epochs):
**every arm at every α₀ ends at 99.6–99.9% train.** Scalar, 6-block and layerwise all fit the
training set completely, so the only thing left to differ on is generalisation and speed — and
they barely differ. Under SGDm the scalar arm ends at 94%.

That is H4 stated as a measurement rather than an argument: **AdamW's per-coordinate
normalisation already lets the scalar arm fit the training set, so a learned per-block step size
has nothing left to contribute; SGDm's scalar arm cannot fit it within the budget, and
granularity supplies what is missing.** The one exception is instructive — AdamW + Adam,
layerwise, α₀=1e-3 reaches 99.88% train and plateaus at 90.83, the worst generalisation gap in
the whole sweep (9.05pp), which is the U-shape of §3 showing up as overfitting.

## 7. Threshold safety is now mechanical, not a rule to remember

`analysis/aggregate.py` now emits two columns on every run:
* **`plateau`** — mean test accuracy over the last 20 epochs (blank for runs under 20 epochs);
* **`ep_in_band_90`** — how many epochs the curve spends inside [89, 91].

Cycle 4 made "check the threshold against every arm's plateau before quoting it" a
methodological rule; it is now a column, so the check cannot be skipped by forgetting. It pays
immediately — in the a0L block, plain layerwise sits in the 90% band for **46–58 of 100 epochs**
at every α₀ while the shrink arm sits there for **4–9**, and the scalar arm's count is **0**
because its plateau is 87.7. A metric with that property is not measuring speed on the plain and
scalar arms.

## 8. Queue actions — a wrong cap model was found and corrected, and it was costing throughput

**Gotcha 13 was wrong, in a way that had silently halved both accounts' effective allowance.**
It recorded the concurrency caps as attached to **GPU types** ("2× A100 / 8× L4 / 12× 2080ti,
additive"). Reading the QOS table directly (`sacctmgr show qos`) they are attached to
**partitions**:

| QOS | partition | cap |
|---|---|---|
| `qos-short-gpu` | `gpu-short` | **gres/gpu=12, across all GPU types in it** |
| `qos-gpu-l4` | `gpu-l4-24g` | gres/gpu=8 |
| `qos-gpu-2080ti` | `gpu-2080ti-11g` | gres/gpu=12 |
| `qos-gpu-a100` | `gpu-a100-80g` | gres/gpu=2 |
| `qos-gpu-mig` | `gpu-mig-40g` | gres/gpu=8 |

The numbers in gotcha 13 are real, but they are the *dedicated-partition* caps. `gpu-short` has
its own separate 12-GPU cap that is **shared across L4 and 2080ti alike** — so cycle 4's action
of widening every job to `--partition=<dedicated>,gpu-short` moved almost all of the campaign's
work into one 12-GPU pool, collapsing what was believed to be two additive allowances into one.

`alice2` was the demonstration: **12 running jobs (7 L4 + 5 2080ti), all in `gpu-short`, and all
17 pending jobs hard-blocked with `QOSMaxGRESPerUser`** — while its `gpu-2080ti-11g` allowance
(12) and `gpu-l4-24g` allowance (8) sat *entirely unused*.

Verified by experiment rather than inference: restricting one pending job to
`Partition=gpu-2080ti-11g` flipped its reason from **`QOSMaxGRESPerUser` → `Priority`** — from
"cannot start whatever frees" to "eligible, waiting for a node".

Actions taken:
* **`alice2`: 11 more pending `a0A` cells moved to `gpu-2080ti-11g` only** (12 total). Five were
  deliberately left dual-partition so `gpu-short` slots still backfill as they drain. Pending
  jobs blocked by QOS went **17 → 0**.
* **`alice`: all 15 pending `a0h` cells moved to `gpu-2080ti-11g` only.** `a0h` is demoted to
  cross-GPU-type replication (cycle 4 §7), so it should not be competing with the decisive `a0L`
  and `ext300` L4 work for the single `qos-short-gpu` pool. Running jobs on `alice` went
  **6 → 10** over the cycle.
* GRES stayed pinned to its original type in every case, so within-block timing comparability is
  untouched (gotcha 3). Only partition *eligibility* changed — no cancels, no resubmits, job IDs
  and names preserved.

**The cluster itself is still fully saturated** — every L4, 2080ti, A100 *and* MIG node reports
`AllocTRES gres/gpu` equal to `CfgTRES gres/gpu`. Cycle 3 recorded MIG as having "one free slice";
it now has none. Throughput continues to come from queue *eligibility and ordering*, never from
submitting more.

## 9. Standing caveats after this cycle

* Every number remains **CIFAR-10 / ResNet-18**. The three `sm_ResNet{34,50,101}` scale smokes
  ran but are 2-epoch probes at chance accuracy — they establish that the deeper models *execute*,
  nothing more. The scale ladder proper has not run.
* §1 is **n=1** (seed 0) on all twelve a0L cells; seed 1 is in flight on all twelve. The α₀=1e-6
  scalar cell is effectively n=3 via the independent `g4-sgdmLion-scal` replication, but the rest
  are single-seed and must not be quoted as settled.
* §2 is the binding caveat on the whole campaign: **the two headline claims are not yet
  established as asymptotic**, and `ext300` (6 cells, queued) decides both.
* **ImageNet stays scoped out** — 489/1000 classes and no devkit, so the 50,000 flat `val` JPEGs
  cannot be labelled from anything on disk.
* The **language modality** is still blocked on the validation-gated optimizer port;
  pretokenization is done (50/50 shards, 8.5 GB).
* `a0A` (20 cells — the α₀ control for the campaign's largest effect) is now unblocked but has
  three complete cells and no complete seed.

# 19 Aug 2026 (cycle 6) — the granularity effect is a META-GRADIENT effect, not a step-size effect

235 runs aggregated (up from 216). The `ext300` budget control is running and roughly a quarter
through; the `a0L` α₀ ladder has reached n=2 on eleven of twelve cells and does not move. Neither
is the cycle's main result.

The main result comes from re-reading data the campaign already had. **At λ = 1.0 the M0 shrink
operator sets every group's β to the group mean on every step, so the base optimiser uses exactly
ONE step size for the entire network — the same parameterisation as the `scalar` arm — and it beats
`scalar` by 4.5pp.** The benefit the campaign has been attributing to step-size *granularity*
survives when the granularity is removed.

## 1. Two factors were confounded in every result so far, and they separate cleanly

`_apply_hier()` runs **after** `meta_update()` and before the next step's `beta_to_alpha()`
(HF.py `step()`, lines 81–90), so at λ=1.0 every base update in the run sees a single scalar α.
That makes the shrink arm a control the campaign did not realise it had: it holds the number of
step sizes fixed at one and varies only how finely the meta-gradient was resolved before being
reduced.

SGDm + Lion, α₀ = 1e-6, guard on, augmented, 100 epochs:

| arm | # step sizes the base opt uses | N meta-grad estimates | n | ep→85 | ep→90 | plateau | final train |
|---|---|---|---|---|---|---|---|
| scalar | 1 | 1 | 5 | 37.0 | never | 87.78 ± 0.14 | 93.83 ± 0.21 |
| 6-block plain | 6 | 6 | 4 | 29.2 | 43.5 | 91.41 ± 0.13 | 99.07 ± 0.02 |
| 6-block + λ=0.1 | **1** | 6 | 6 | 31.2 | 53.0 | 91.71 ± 0.15 | 99.38 ± 0.05 |
| layerwise plain | 62 | 62 | 11 | 29.0 | 56.5 | 90.77 ± 0.18 | 99.66 ± 0.07 |
| layerwise + λ=0.1 | **1** | 62 | 7 | 35.7 | 41.4 | 92.30 ± 0.09 | 97.75 ± 0.09 |
| layerwise + λ=1.0 | **1 (exact)** | 62 | 2 | 35.5 | 41.5 | **92.32 ± 0.14** | 97.72 ± 0.00 |
| weightwise plain | 11.17M | 11.17M | 3 | never | never | 77.82 ± 0.45 | 82.02 ± 0.49 |
| weightwise + λ=0.1 | **1** | 11.17M | 2 | never | never | 45.26 ± 3.63 | 47.98 ± 3.92 |

λ=1.0 (exact pooling, n=2) and λ=0.1 (half-life 7 steps, n=7) agree to 0.02pp, so the residual
per-layer spread at λ=0.1 contributes nothing and the two can be read as the same arm.

**Read the rows where the base optimiser has exactly one step size (N = 1 → 6 → 62 → 11.17M):**

> 87.78 → 91.71 → 92.30 → 45.26

**The whole 4.5pp gain from `scalar` to the campaign's best arm is obtained without giving the
network more than one step size.** Whatever the project has been measuring, it is not the value of
per-layer step sizes.

**And the step-size count on its own is neutral-to-harmful.** Holding N fixed and varying only how
many step sizes survive:

| N | many step sizes | one step size | Δ from pooling |
|---|---|---|---|
| 6 | 91.41 | 91.71 | **+0.30** |
| 62 | 90.77 | 92.30 | **+1.53** |
| 11.17M | 77.82 | 45.26 | **−32.56** |

Going from 6 step sizes to 62 *costs* 0.64pp (91.41 → 90.77); pooling them back to one recovers it
and more. The campaign's own headline (+1.61pp for pooling on layerwise, n=5) is that recovery.

## 2. The mechanism this points at — and it is a hypothesis, not yet a measurement

`block_product` partitions the *same* total meta-gradient: the layerwise vector's 62 entries sum
to the scalar arm's single entry. The partition changes nothing about the information available.
What changes is **where the meta-optimiser's nonlinearity sits relative to the reduction**:

* `scalar` computes `sign(Σ_b z_b)` — one Lion sign for the whole network, so β takes a ±η step
  every step regardless of how weak the evidence is.
* `layerwise + λ→1` computes `mean_b sign(z_b)` over 62 groups — a *soft* average in [−1, 1], so β
  moves by a small, well-aimed amount.

Since `mean(sign(·)) ≠ sign(mean(·))`, these are different estimators of the same quantity, and the
finer one is better conditioned. The same argument covers Adam-meta (per-group normalisation then
average, vs global normalisation), which is why the win is *larger* without the sign nonlinearity
(cycle 3 §5) rather than absent — that result refuted "the sign is the cause" but is fully
consistent with "the reduction granularity is the cause".

**Supporting evidence available now, from existing probes** (`z_mean`, `z_std`, `snr` per group,
SGDm base, late in training):

| arm | N groups | median per-group SNR | implied E&#124;mean of N signs&#124; |
|---|---|---|---|
| scalar | 1 | 0.050 | 1.00 |
| 6-block | 6 | 0.129 | 0.42 |
| layerwise | 62 | 0.012 | 0.13 |

Per-group SNR is ~0.01–0.13, i.e. the per-group signs are near-unbiased coin flips, so the pooled
meta-update shrinks roughly as 1/√N. Extrapolated to weightwise (N = 11.17M) the shared β would
move ~3,300× slower than `scalar`'s — which is what a run that plateaus at 45% with 48% train
accuracy looks like. **The weightwise-pooled collapse is predicted by the same mechanism that
predicts the layerwise-pooled win**, and the two have until now been filed as unrelated results
(cycle 5 §5's "three distinct regimes").

**This is not yet measured.** The existing probes cover only *unpooled* arms, so the shared β's
actual drift rate has never been recorded. Six 20-epoch probe-enabled runs (`p2-*`, `bdrift`) were
submitted this cycle to measure it directly across N ∈ {1, 6, 62, ~4.8k, 11.17M}.

### Predictions on record, before the runs report
* β's drift rate per step falls monotonically with N, approximately as 1/√N.
* `nodewise + λ=1.0` (N ≈ 4,800) lands **between** layerwise and weightwise, and closer to the
  collapse: the shared β should move ~70× slower than scalar's.
* If instead nodewise matches layerwise, the 1/√N story is wrong and the effect is something about
  the *layer* as a unit, not about N.

## 3. Consequence: the shrink operator cannot express partial pooling, so the λ curve was never a test of it

Gotcha 9 records that λ is a per-step rate with half-life ln2/λ steps against ~50,000 steps in a
run. Every λ ever run on layerwise — 0.001, 0.01, 0.1, 0.5, 1.0 — has a half-life of 693 steps or
fewer, i.e. **all five are full pooling within the first 1.4% of the run.** The campaign's
conclusion that "the λ curve is flat and the optimum is at full pooling" (cycle 3 §4) is correct,
but it is flat *because the operator saturates*, not because an interior optimum was searched for
and not found. The interpolation between "62 independent step sizes" and "one shared step size"
has never been sampled on layerwise.

The **M1 additive** operator does not have this defect. It rescales the per-group deviation of each
realised update by `ETA_RATIO` for the whole run:

```
d = β − β_prev ;  β = β_prev + mean(d) + η_ratio · (d − mean(d))
```

η_ratio = 1 is exactly plain; η_ratio = 0 freezes the deviations and — since all groups start at
log α₀ — yields exactly one shared β by a completely different route than shrink. Interior values
are genuinely partial *for the entire run*. It had been run only on weightwise (`ha-*`, n=2, where
everything fails anyway) and **never on layerwise, the granularity where hierarchy works.**

Submitted this cycle on `alice2`: `ad-l-r{0,003,01,03}` × 2 seeds, η_ratio ∈ {0, 0.03, 0.1, 0.3},
otherwise identical to the headline cell. η_ratio = 0 doubles as an independent replication of the
λ=1.0 exact-pooling number through a different operator — if it does not land near 92.3, the §1
reading is wrong.

## 4. `ext300` — the budget control is a quarter through, and its comparability is now VERIFIED rather than argued

Cycle 5 argued from code inspection that a 300-epoch run is a continuation of the 100-epoch run
because `train.py` has no learning-rate scheduler. That is now checked against data. Comparing each
`e300` run to its matching `a0L` α₀=1e-3 cell (same seed, same config) over the last 20 epochs of
the overlap:

| pair | overlap | mean Δtest | within-run epoch-to-epoch jitter |
|---|---|---|---|
| scalar s0 | 0–64 | +0.00 pp | 0.25 pp |
| scalar s1 | 0–61 | +0.12 pp | 0.20 pp |
| layerwise plain s0 | 0–89 | +0.25 pp | 0.19 pp |
| layerwise plain s1 | 0–74 | −0.09 pp | 0.23 pp |
| layerwise + λ=0.1 s0 | 0–83 | −0.22 pp | 0.18 pp |
| layerwise + λ=0.1 s1 | 0–65 | +0.04 pp | 0.25 pp |

Every pair agrees to within its own within-run jitter. **The extension is a valid continuation in
distribution** — not bitwise, which cuDNN autotuning rules out (gotcha 17), and the pointwise max
difference over a full overlap is 1.3–4.9pp, so the *windowed* comparison is the one to quote.

Current state (61–89 of 300 epochs), with the slope that decides cycle 5 §2:

| run | last ep | train | test | Δtrain/10ep | Δtest/10ep |
|---|---|---|---|---|---|
| scalar s0 | 64 | 92.62 | 87.79 | **+0.82** | +0.25 |
| scalar s1 | 61 | 92.51 | 87.57 | **+0.88** | +0.37 |
| layerwise plain s0 | 89 | 99.82 | 91.65 | +0.10 | +0.20 |
| layerwise plain s1 | 74 | 99.63 | 90.95 | +0.27 | +0.24 |
| layerwise + λ=0.1 s0 | 83 | 97.68 | 92.34 | +0.31 | +0.04 |
| layerwise + λ=0.1 s1 | 65 | 97.06 | 92.31 | +0.54 | +0.10 |

Nothing is decidable yet. The scalar arm's train curve is still climbing at ~0.85pp/10 epochs, so
cycle 5 §2(a) stands exactly as written: **the two headline claims remain non-asymptotic and must
not be written up as ceiling claims.**

Note that §1 of this cycle does *not* dissolve that caveat — it relocates it. "More pooled
meta-gradient estimates beat fewer" is subject to the same budget question as "finer granularity
beats coarser" was.

## 5. `a0L` at n=2 — cycle 5 §1 holds, with one softening

Eleven of twelve cells now have two seeds (the α₀=1e-6 shrink cell is still n=1):

| α₀ | arm | n | ep→85 | ep→88 | ep→90 | plateau | final train |
|---|---|---|---|---|---|---|---|
| 1e-6 | scalar | 2 | 36.5 | never | never | 87.73 ± 0.01 | 93.89 ± 0.22 |
| 1e-6 | 6-block | 2 | 29.0 | 37.0 | 43.5 | 91.45 ± 0.02 | 99.09 ± 0.01 |
| 1e-6 | layerwise plain | 2 | 28.5 | 37.0 | 56.5 | 90.84 ± 0.01 | 99.70 ± 0.01 |
| 1e-6 | layerwise + λ=0.1 | 1 | 35.0 | 38.0 | 41.0 | 92.46 | 97.76 |
| 1e-4 | scalar | 2 | 26.5 | 66.0 (1/2) | never | 87.93 ± 0.28 | 94.01 ± 0.34 |
| 1e-4 | 6-block | 2 | 20.0 | 27.5 | 34.0 | 91.46 ± 0.12 | 99.25 ± 0.04 |
| 1e-4 | layerwise plain | 2 | 19.5 | 26.5 | 42.0 | 91.00 ± 0.16 | 99.78 ± 0.01 |
| 1e-4 | layerwise + λ=0.1 | 2 | 24.5 | 26.5 | 30.0 | 92.30 ± 0.03 | 98.03 ± 0.05 |
| 1e-3 | scalar | 2 | 24.5 | 77.0 | never | 87.85 ± 0.06 | 94.21 ± 0.25 |
| 1e-3 | 6-block | 2 | 15.5 | 22.0 | 31.0 | 91.53 ± 0.15 | 99.31 ± 0.01 |
| 1e-3 | layerwise plain | 2 | 13.0 | 23.0 | 41.5 | 91.22 ± 0.00 | 99.91 ± 0.04 |
| 1e-3 | layerwise + λ=0.1 | 2 | 18.0 | 20.0 | 23.0 | 92.26 ± 0.26 | 98.19 ± 0.01 |

Unchanged: the scalar plateau is flat to 0.2pp across three decades of α₀ and **never reaches 90%
at any α₀**; every arm improves monotonically up to α₀=1e-3 (the AdamW U-shape does not transfer);
the granularity gain survives per-arm tuning.

**Softening:** cycle 5 reported scalar as never reaching 88% at α₀ ∈ {1e-6, 1e-4}. At n=2 it reaches
88% at α₀=1e-3 on **both** seeds (ep 77) and on one of two seeds at 1e-4 (ep 66). The 90% statement
is unaffected. Quote ep→88 for scalar as threshold-marginal, not as "never".

## 6. Queue actions this cycle

* **Submitted `n1-*` (8 jobs, `alice`, L4 dedicated)** — the §1 ladder run forward rather than
  re-read: `nodewise` plain and pooled (the never-measured rung at N ≈ 4,800), plus exact λ=1.0
  pooling at N=6 and N=11.17M. `nodewise` has never had a run longer than 3 epochs.
* **Submitted `ad-l-*` (8 jobs, `alice2`, L4 dedicated)** — §3's additive interpolation. `alice2`'s
  `gpu-l4-24g` allowance (8) was **entirely unused**; this fills it without touching the shared
  `gpu-short` pool where `ext300` lives.
* **Submitted `p2-*` (6 jobs, `alice2`, 20 epochs, `--time=00:45:00`)** — §2's direct β-drift
  measurement. Sized short deliberately so they backfill (gotcha 12) rather than queue behind
  100-epoch work.
* **Niced 5 pending `h2-lam*` cells to 5000.** λ ∈ {0.03, 0.1, 0.3} have half-lives of 23/7/2 steps
  — all full pooling (gotcha 9) — and layerwise λ=0.1 is already at n=7. They re-measure a settled
  point three times. `nice`, not `scancel` (gotcha 14).
* **Both accounts now report zero `QOSMaxGRESPerUser`**: `alice` 15 running / 28 pending, `alice2`
  5 running / 30 pending, every pending job reading `Priority`. The cluster is still saturated;
  eligibility is correct, so nothing further is buyable by resubmission.

## 7. What this cycle changes about the paper

The framing in `PLAN-appendix-paper.md` — "granularity buys speed and stability" — survives as a
description of the measurements but is **wrong about the cause**, and the correct cause is a
stronger and more surprising claim:

> Partitioning the meta-gradient more finely improves the *estimator* of the shared step size.
> Actually spending those partitions on separate step sizes is neutral at m=6, mildly harmful at
> m=62, and catastrophic at m=11.17M.

This also gives the parent paper's §7.3 ImageNet null a second, sharper reading alongside the
budget one: on a network where the per-group meta-gradient SNR is lower, N is effectively larger
relative to the signal, and the pooled estimator moves too slowly to reach a useful step size
within the budget — the same failure the weightwise arm shows here in miniature.

**Nothing in §1 may be written up until `p2-*` reports** — the mechanism is currently an
interpretation of an outcome table, and the campaign has already been burned once (cycle 4 §2) by
a confident mechanism that a control then corrected.

## 8. Standing caveats after this cycle

* §1's ladder is n=2 at λ=1.0 and n=3 at weightwise-plain. The 4.5pp gap is ~30σ, but the *shape*
  of the curve between N=62 and N=11.17M rests on the `n1-node-*` runs, which have not reported.
* §2 is a hypothesis with consistent supporting evidence, **not a measurement**.
* Cycle 5 §2 is unresolved: both headline claims are still measured at a budget where the scalar
  arm has not finished fitting. `ext300` is ~25% through.
* Every number remains **CIFAR-10 / ResNet-18**, 100 epochs unless stated.
* **ImageNet stays scoped out** (489/1000 classes, no devkit).
* The **language modality** is still blocked on the validation-gated optimizer port; TinyStories
  pretokenization is done (50/50 shards, 8.5 GB).
* `a0A` (the α₀ control for the campaign's largest effect) still has no complete seed.
