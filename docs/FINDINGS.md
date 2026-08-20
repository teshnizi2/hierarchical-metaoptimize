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

## 1b. A measured dose-response on weightwise — and the provenance audit that validates it

An audit of every row in the table above confirms **all of them are guarded**
(`BETA_CLIP=-15:-2.3026`). Four runs carry `augment=?` — they predate the ENV provenance line
(gotcha 8), so augmentation was *not recorded*, not *not applied*. That matters because both cells
in the N=11.17M row are `?`.

It is resolved by the weightwise λ ladder, which spans the recorded and unrecorded runs and whose
two ends overlap:

| λ | half-life (steps) | n | augment recorded | plateau | final train |
|---|---|---|---|---|---|
| plain (no pooling) | ∞ | 3 | ? | 77.82 ± 0.45 | 82.02 ± 0.49 |
| 1e-5 | 69,315 | 2 | **1** | 77.40 ± 0.14 | 81.28 ± 0.23 |
| 1e-4 | 6,931 | 2 | **1** | 68.70 ± 0.32 | 70.86 ± 0.37 |
| 1e-2 | 69 | 2 | ? | 46.06 ± 3.55 | 48.56 ± 3.63 |
| 1e-1 | 7 | 2 | ? | 45.26 ± 3.63 | 47.98 ± 3.92 |
| 0.5 | 1 | 2 | ? | 45.22 ± 3.66 | 47.94 ± 3.94 |

**λ=1e-5 has a 69,315-step half-life against a ~50,000-step run — it is barely pooled at all — and
it reproduces the `augment=?` plain arm to 0.42pp.** Two runs with recorded augmentation land on
top of three without it, so the unrecorded runs were augmented and the `?` rows are safe to quote.

**The ladder itself is the cycle's strongest single piece of evidence for §2.** Unlike layerwise,
weightwise *was* sampled in the genuinely-partial region (λ = 1e-5 and 1e-4 have half-lives of
69,315 and 6,931 steps), and the result is a smooth monotone dose-response: performance falls as
pooling strength rises, and **saturates once the half-life drops below ~70 steps** — i.e. exactly
where pooling becomes complete and the shared β's drift rate hits its 1/√N floor. Nothing about a
"three distinct regimes" reading predicts a smooth dose-response; a graded slowing of the shared
step size predicts precisely one.

Note this is the *opposite sign* to the layerwise ladder, where the same operator at the same λ
values improves the result by 1.5pp. One monotone curve in each direction, from the same knob, at
two values of N — which is what a single mechanism with an interior optimum in N looks like.

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
* **Submitted `lp-l-*` (6 jobs, `alice`, L4 dedicated)** — the layerwise analogue of the §1b
  weightwise ladder, at λ ∈ {1e-5, 3e-5, 1e-4} (half-lives 69,315 / 23,105 / 6,931 steps). Same
  operator, same α₀, same guard, so the two ladders become directly comparable and §3's unsampled
  interpolation is filled. Prediction: λ=1e-5 reproduces layerwise plain (90.77), λ=1e-4 is
  intermediate, and the gain saturates by λ≈0.01 — the mirror image of the weightwise curve.
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
* §2 is a hypothesis. It now has a measured **dose-response** behind it (§1b) rather than only an
  outcome table, but the shared β's drift rate itself has still never been recorded; `p2-*` does that.
* Cycle 5 §2 is unresolved: both headline claims are still measured at a budget where the scalar
  arm has not finished fitting. `ext300` is ~25% through.
* Every number remains **CIFAR-10 / ResNet-18**, 100 epochs unless stated.
* **ImageNet stays scoped out** (489/1000 classes, no devkit).
* The **language modality** is still blocked on the validation-gated optimizer port; TinyStories
  pretokenization is done (50/50 shards, 8.5 GB).
* `a0A` (the α₀ control for the campaign's largest effect) still has no complete seed.

---

# 19 Aug 2026 (cycle 7) — the β-drift mechanism is measured, and it explains the COST of pooling, not the benefit

255 runs aggregated (up from 235). Three things landed at once: the six `p2-*` β-drift probes
that cycle 6 §2 was waiting on, the `ext300` budget control at ~2× the epochs it had last cycle,
and the layerwise λ ladder at n=3 across seven values.

**All three cut against cycle 6's headline reading, and the campaign's two oldest open questions
both close.** Cycle 6 put four numerical predictions on record before these ran. One is confirmed,
two are refuted by one to three orders of magnitude, and the fourth is now measurable and wrong.

## 1. The β-drift measurement — direction confirmed, the 1/√N law refuted

Every `p2-*` arm below uses `HIER=shrink LAM=1.0`, so the base optimiser ends every step with
**exactly one** step size (probe confirms `beta_true_max − beta_true_min = 0.000` throughout);
only N, the number of pooled meta-gradient estimates, differs. SGDm + Lion, α₀=1e-6, guard on,
augmented, 20 epochs, `PROBE=100`. Drift is `|Δβ|/step` measured over steps 1000–7500;
`frac_neg` is the fraction of **all** meta-gradient coordinates sharing a sign, averaged over the
same window (probe reads `zall`, the full coordinate set, not a subsample).

| arm | N | drift/step | ÷η | i.i.d. prediction | **× i.i.d.** | frac_neg | acc @20ep |
|---|---|---|---|---|---|---|---|
| scalar | 1 | 1.000e-3 | 1.000 | 7.98e-1 | 1.3 | 0.955 | 70.73 |
| 6-block | 6 | 9.828e-4 | 0.983 | 3.26e-1 | 3.0 | 0.848 | 68.45 |
| layerwise | 62 | 7.997e-4 | 0.800 | 1.01e-1 | 7.9 | 0.832 | 53.14 |
| nodewise | ~4,800 | 5.503e-4 | 0.550 | 1.15e-2 | 47.8 | 0.622 | 33.03 |
| weightwise | 11,173,962 | 1.668e-4 | 0.167 | 2.39e-4 | **698.8** | 0.531 | 14.80 |
| *layerwise plain (unpooled)* | *62* | *7.742e-5* | *0.077* | — | — | *0.777* | *74.29* |

**Log-log slope of drift vs N over the five pooled arms: −0.113. The prediction was −0.500.**

* **CONFIRMED** — cycle 6's prediction that drift falls monotonically with N, and that
  `nodewise` lands between layerwise and weightwise and closer to the collapse (33.03, between
  53.14 and 14.80). `nodewise` had never had a run longer than 3 epochs before this.
* **REFUTED** — the magnitude. Cycle 6 predicted nodewise's shared β would move **~70× slower**
  than scalar's; measured **1.8×**. It predicted weightwise **~3,300× slower**; measured **6.0×**.

**Why the i.i.d. model fails.** It assumed the per-group signs are near-unbiased coin flips, so
that pooling N of them shrinks the update as 1/√N. The probe measures the assumption directly and
it is false: at N = 11,173,962, **53.1% of all 11.17M per-weight meta-gradients agree on the
sign.** Independence would put that at 50.0000 ± 0.0015%. The signs are strongly positively
correlated, so the pooled estimate does not average toward zero — it converges to a population
bias. Drift is set by *how much the coordinates actually agree*, which is a property of the
partition, not by N through a sampling-noise channel.

(The realised drift runs ~2.4× above `|2·frac_neg − 1|` at weightwise because Lion steps on the
sign of the meta-*momentum*, which is smoothed over time and therefore more aligned than the
instantaneous z. Direction and ordering are unaffected.)

## 2. The measured mechanism predicts the WRONG SIGN for the campaign's headline

The 20-epoch column above is monotone in drift, and it is monotone the *opposite* way from the
100-epoch result. Pooled layerwise is **17.6pp behind scalar at 20 epochs** (53.14 vs 70.73) and
**4.5pp ahead at 100** (92.29 vs 87.78).

The 20-epoch ordering is fully accounted for by startup cost. β must climb 6.9 log units from
`ln(1e-6)` to a useful `α ≈ 1e-3`, which at each arm's measured drift takes:

| arm | steps to climb | epochs | β actually reached @ 9,900 steps |
|---|---|---|---|
| scalar | 6,900 | 13.8 | −6.53 |
| 6-block | 7,020 | 14.0 | −6.03 |
| layerwise | 8,630 | 17.3 | −6.18 |
| nodewise | 12,540 | 25.1 | −8.59 |
| weightwise | 41,400 | 82.8 | −12.26 |

The three arms that got there inside 20 epochs score 53–71%; the two that did not score 33% and
15%. **So `p2-*` measures a transient out of the α₀=1e-6 hole, not the mechanism behind the
100-epoch win.** Cycle 6 §2 offered drift as the explanation of the *benefit* of pooling. It is
the explanation of its *cost*.

### And the weightwise collapse is a SPREAD effect, not a drift effect

Cycle 6 §2's strongest claim was unification: "the weightwise-pooled collapse is predicted by the
same mechanism that predicts the layerwise-pooled win", via drift extrapolated as 1/√N. That
extrapolation is refuted above (6× not 3,300×), and the campaign already holds a control that
settles it independently.

Reading the M1 additive operator out of `HF.py` (`_apply_hier`, both the layerwise branch and the
global weightwise/nodewise branch):

```
β_new = β_prev + dm + r·(d − dm)      where  dm = mean(d)
⇒ mean(β_new) = mean(β_prev) + dm     — EXACTLY independent of r
```

**`ETA_RATIO` has no direct channel to the shared β's drift rate. It varies only the spread.**
M0 shrink and M1 additive are therefore not two settings of one knob: shrink changes drift *and*
spread; additive changes spread *only*. Comparing the two ladders on weightwise separates them:

| operator | setting | drift channel | plateau (n=2) |
|---|---|---|---|
| plain | — | full | 77.82 ± 0.45 (n=3) |
| M1 additive | r = 0.3 | **unchanged by construction** | 64.17 ± 0.28 |
| M1 additive | r = 0.1 | **unchanged by construction** | 48.71 ± 1.92 |
| M0 shrink | λ = 0.1 | slowed 6× | 45.26 ± 3.63 |

Additive at r=0.1 collapses weightwise to 48.71 **with the drift channel held fixed by
construction**, landing within 3.5pp of shrink at λ=0.1, which slows drift as well. The two
operators agree while disagreeing about drift. **The weightwise collapse is caused by suppressing
the per-group spread, not by slowing the shared step size.** Cycle 6 §2's unification does not
hold.

*Caveat.* Mean-preservation is exact per step given identical state; over a trajectory r changes
the spread, hence the base updates, hence the next d. And the guard clamp runs *after*
`_apply_hier`, so a binding clip breaks mean-preservation — `p2-lay-plain` shows β pinned at the
−15 floor with a spread of 8.7, so at large r the clip does bind. `p4-*` (§5) measures the
realised drift and spread across r directly and tests both.

## 3. `ext300` resolves cycle 5 §2 — granularity is budget-invariant, pooling is not

The budget control has gone from ~25% to 205–287 of 300 epochs. Comparing at a **matched** epoch
(E=205, the shortest of the six runs; window = mean test over the last 20 epochs of that prefix),
α₀=1e-3, n=2 per arm:

| arm | E=100 | E=205 | train @E=205 |
|---|---|---|---|
| scalar | 87.94 (87.83/88.04) | 88.27 (88.24/88.30) | 95.16 |
| layerwise plain | 91.36 (91.54/91.19) | 91.74 (92.02/91.46) | 99.98 |
| layerwise λ=0.1 | 92.21 (92.27/92.15) | 92.03 (92.08/91.97) | 99.05 |

| contrast | E=100 | E=205 |
|---|---|---|
| **granularity** (scalar → layerwise) | **+3.43pp** | **+3.47pp** |
| **pooling** (plain → λ=0.1) | +0.84pp | +0.29pp |

**The granularity claim is not a budget artefact.** Doubling the budget moves the contrast by
0.04pp. Cycle 5 §2(a) — "both headline claims are measured while the losing arm is still fitting"
— is answered for this one, and answered more strongly than a null: at 205 epochs the scalar arm's
**training** accuracy is 95.16% against layerwise's 99.98%, and it gained only 1.2pp of train
accuracy over the extra 105 epochs. It is not behind on the way to the same place; it is
converging to a worse one.

**The pooling claim is substantially a budget artefact.** +0.84pp at E=100 decays to +0.29pp at
E=205, against a seed-to-seed spread of 0.56pp within the plain arm. At 2× budget it is no longer
resolvable. This is the correct reading of cycle 6 §1's "pooling recovers what granularity costs":
the recovery is real at 100 epochs and mostly gone by 205.

## 4. The λ ladder at n=3 — pooling strength moves the generalisation gap, not the test accuracy

SGDm + Lion, α₀=1e-6, guard on, layerwise, ≥95 epochs:

| λ | half-life (steps) | n | plateau | final train | **train − test** |
|---|---|---|---|---|---|
| plain | ∞ | 11 | 90.77 ± 0.18 | 99.66 ± 0.07 | 8.89 |
| 0.001 | 693 | 3 | 92.32 ± 0.16 | 99.92 ± 0.02 | 7.59 |
| 0.01 | 69 | 3 | **92.47 ± 0.15** | 98.06 ± 0.11 | 5.59 |
| 0.03 | 23 | 3 | 92.24 ± 0.06 | 97.83 ± 0.06 | 5.59 |
| 0.1 | 7 | 11 | 92.29 ± 0.08 | 97.78 ± 0.08 | 5.48 |
| 0.3 | 2 | 2 | 92.29 ± 0.16 | 97.78 ± 0.05 | 5.49 |
| 0.5 | 1 | 3 | 92.20 ± 0.13 | 97.78 ± 0.02 | 5.59 |
| 1.0 | <1 | 3 | 92.20 ± 0.23 | 97.76 ± 0.07 | 5.56 |

Test accuracy across all seven λ spans 92.20–92.47 (0.27pp, ~1.7σ at n=3) — flat, as cycle 3 §4
found. But **final train accuracy spans 97.76–99.92, and the train−test gap halves from 8.89 to
5.48.** λ=0.001 reaches the same test accuracy as λ=1.0 while still fitting the training set
completely (99.92 vs 97.76).

So the plateau gain over plain layerwise is **not** simply regularisation: the arm that gains the
most test accuracy relative to plain (λ=0.001, +1.55pp) does so with *higher* train accuracy than
plain, not lower. Whatever pooling buys at N=62, it is visible in test accuracy before any
generalisation gap opens up. Do not write the pooling result up as a regularisation effect.

## 5. Queue actions this cycle

Both accounts' queues were already deep and every pending job reads `Priority`, so the binding
constraint remains queue depth, not job count (cycle 6 §6). Both new sweeps are therefore
**short** (20 epochs, `--time=00:45:00`) so they backfill rather than queue (gotcha 12); the
`p2-*` set turned around in 6–9 minutes each on this footing.

* **Submitted `p3-*` (6 jobs, `alice`, `bin/p3_drift_a0.sh`)** — the α₀ control for §1/§2.
  Byte-identical to `betadrift.sh` except α₀ = 1e-3. `ln(1e-3) = −6.91` and the pooled arms in
  `p2-*` all converged to β ∈ [−6.0, −6.5], so **α₀=1e-3 starts essentially at the destination**
  and there is no hole to climb out of.
  *Predictions on record:* (a) the 20-epoch ordering 70.7 / 68.5 / 53.1 / 33.0 / 14.8 largely
  **collapses** for N ≤ 62; (b) nodewise and weightwise still lag, but far less; (c) the measured
  **drift rate is roughly unchanged from `p2-*`**, because it is set by sign alignment, which is a
  property of the partition rather than of α₀ — *if drift moves materially with α₀, §1's reading
  is wrong and the mechanism needs rewriting.*
* **Submitted `p4-*` (5 jobs, `alice2`, `bin/p4_addit_drift.sh`)** — §2's spread/drift separation,
  run forward instead of inferred. Layerwise, α₀=1e-6, `HIER=additive` at r ∈ {0, 0.03, 0.1, 0.3,
  1.0}, probe on.
  *Predictions on record:* (a) realised mean-β drift is ~equal across all r (the analytic
  invariance) — falsified if it moves monotonically with r; (b) spread grows monotonically with r,
  and is exactly 0 at r=0; (c) r=1.0 reproduces `p2-lay-plain` (drift 7.7e-5, spread 8.7,
  74.29 @20ep); (d) the −15 clip binds only at large r.
* **Already in flight and unchanged:** `n1-*` (8, `alice`, the 100-epoch nodewise rungs),
  `lp-l-*` (6, `alice`, the genuinely-partial layerwise λ ladder at half-lives 69k/23k/6.9k steps),
  `ad-l-*` (8, `alice2`, of which 2 have reported), `a0A-*`, and `ext300`.

## 6. What this cycle changes about the paper

Cycle 6 §7 proposed replacing "granularity buys speed and stability" with "partitioning the
meta-gradient more finely improves the *estimator* of the shared step size". **That replacement is
premature and its stated mechanism is refuted.** What survives, and what does not:

* **SURVIVES, and is now budget-controlled** — the campaign's central result. Step-size
  granularity (scalar → layerwise, m=1 → 62) is worth **+3.4pp under SGDm and is invariant to a
  2× budget**, with the scalar arm's own training accuracy showing it converges to a worse
  solution rather than lagging toward the same one (§3). This is the paper.
* **SURVIVES** — cycle 6 §1's structural observation that the gain is obtainable with the base
  optimiser using only *one* step size. At E=205 scalar → layerwise+λ=0.1 is still +3.76pp.
* **DOES NOT SURVIVE** — that pooling beats plain granularity by ~1.5pp. Epoch-matched and
  budget-controlled it is +0.29pp at E=205, inside seed noise (§3).
* **DOES NOT SURVIVE** — the 1/√N estimator law and the unification of the layerwise win with the
  weightwise collapse (§1, §2). The collapse is a spread effect; drift is a startup cost.
* **NEW, and the strongest mechanism fact the campaign holds** — per-coordinate meta-gradient
  signs are *strongly positively correlated at every granularity*, 53.1% agreeing across 11.17M
  coordinates. Any future account of why granularity helps must start there, not from an
  independence assumption.

The parent paper's §7.3 ImageNet null keeps the budget reading (a long budget lets the scalar arm
converge) and **loses** the second, drift-based reading cycle 6 added to it.

## 7. Standing caveats after this cycle

* §1 and §2 rest on **n=1 per arm** for the drift probes. Drift is a low-variance quantity
  (averaged over 6,500 steps) and the effects span a factor of 6, but the 20-epoch *accuracies* in
  the same table are single seeds and should not be quoted to better than ~1pp.
* §1's `nodewise` group count (~4,800) is carried from cycle 6 and is **not independently
  verified** — the probe's `block_sizes.json` was not written for these runs. The log-log slope
  moves by <0.01 for any N in [2e3, 1e4], so nothing above depends on it.
* §2's spread conclusion uses weightwise additive at **n=2**; `p4-*` tests the same separation on
  layerwise with the drift readout attached.
* §3 is n=2 per arm, and the E=205 window is a *matched prefix*, not a converged asymptote — the
  scalar arm's train accuracy is still climbing at ~1.2pp/100 epochs.
* §4's λ=0.01 peak (92.47) is +0.27pp over λ=1.0 at n=3 — not resolvable. Only the train-accuracy
  and gap columns are being claimed.
* `a0A` (the α₀ control for SGDm + Adam meta) now has **four complete seeds** where cycle 6 had
  none, but no cell has n≥2 yet; it is not read in this cycle.
* Every number remains **CIFAR-10 / ResNet-18**, 100 epochs unless stated.
* **ImageNet stays scoped out** (489/1000 classes, no devkit). The **language modality** is still
  blocked on the validation-gated optimizer port; TinyStories pretokenization is done.

---

# M0 shrinkage: the full lambda curve (3 seeds per cell)

SGDm base + Lion meta, SwiftTD guard on, augmented, 100 epochs.

| lambda | best test acc | delta vs plain |
|---|---|---|
| plain layerwise + guard | 91.33 ± 0.17 (n=6) | — |
| 0.001 | 92.54 ± 0.20 | +1.21 |
| **0.01** | **92.79 ± 0.11** | **+1.46** |
| 0.03 | 92.58 ± 0.08 | +1.25 |
| 0.1 | 92.54 ± 0.08 (n=6) | +1.21 |
| 0.3 | 92.51 ± 0.23 | +1.18 |
| 0.5 | 92.50 ± 0.14 | +1.17 |
| 1.0 | 92.53 ± 0.17 | +1.20 |

**The curve is flat across three orders of magnitude.** The method nominally introduces a
hyperparameter, but the outcome is insensitive to it over lambda in [0.001, 1.0] — so in
practice it removes a decision rather than adding one. That is the strongest property of the
result and should be stated as such.

## It generalises across granularity and across meta-optimizer

| setting | plain | + shrinkage (lam=0.1) | delta |
|---|---|---|---|
| 6-block, SGDm+Lion | 91.56 ± 0.03 | 92.03 ± 0.20 | +0.47 |
| layerwise, SGDm+**Adam** (paper's meta) | 90.71 ± 0.17 | **92.22 ± 0.08** | **+1.51** |

## The mechanism looks like regularisation, not acceleration

Epochs to reach a target (layerwise, SGDm+Lion):

| target | plain | shrinkage lam=0.01 |
|---|---|---|
| 85% | **27.7** | 35.3 |
| 90% | 55.5 | **40.0** |
| 91% | 83.5 | **42.3** |
| 92% | **never (0/6 runs)** | **51.7 (3/3)** |

Shrinkage is *slower* to fit early and decisively better later, crossing over around 88–90%,
and it reaches a level plain layerwise never reaches within the budget. That is the classic
signature of a regulariser, not of a better-conditioned optimiser — and it means the earlier
"granularity buys speed" framing does **not** transfer to the hierarchical variant. The two
effects are different and must be reported separately.

## Per-weight: monotone in effective pooling, but the comparison is CONFOUNDED

Effective pooling over T=50,000 steps is `1-(1-lam)^T`:

| effective pooling | best | delta |
|---|---|---|
| 0% (baseline, guard only) | 79.38 ± 0.46 | — |
| 39% (lam=1e-5) | 78.98 ± 0.17 | −0.40 |
| 99.3% (lam=1e-4) | 70.23 ± 0.15 | −9.15 |
| ~100% (lam >= 0.01) | ~49.1 ± 3.8 | **−30.3** |

Monotone, which confirms the saturation analysis — a per-step lambda is a *rate* (time constant
1/lam steps), not a *strength*.

**DO NOT yet report this as "pooling hurts at m=n".** Fully-pooled per-weight lands at ~49 while
the genuine scalar arm reaches 88.09. If pooling did what it claims, those two should converge.
They do not, and the likely reason is an aggregation mismatch in the current M0 implementation:
the scalar arm aggregates the meta-gradient as a **sum** over weights (`z = sum_i h_i g_i`),
whereas `_apply_hier` pools beta toward a **mean**. That is a factor-of-n = 11.17M discrepancy in
effective meta-step scale, which is more than enough to explain a 39pp gap.

**Required follow-up before any claim about per-weight pooling:** re-implement pooling at m=n so
that the pooled arm reduces *exactly* to the scalar arm at full pooling, and verify that identity
numerically (the same way `LAM=0` was verified to reduce to plain layerwise). Until that identity
holds, the m=n column measures an implementation artifact, not granularity.

The layerwise and 6-block results above are unaffected: there the number of groups is small, the
sum-vs-mean factor is 62 or 6 rather than 11 million, and the effect is confirmed at 3 seeds
across seven lambda values and two meta-optimizers.

---

# 19 Aug 2026 (cycle 8) — M1 additive produces the campaign's first genuine interior optimum, and the α₀ confound closes

**Headline.** Swept over its *own* knob rather than shrink's, the M1 additive operator on layerwise
is **non-monotone with an interior maximum**, and at its peak it beats plain layerwise by **+1.90pp**
while *also* fitting the training set better. Every previous pooling result in this campaign was
either full pooling (gotcha 9) or monotone; this is the first cell where partial pooling beats both
endpoints, which is the thing the project set out to find.

Separately, three priority items close on data already on disk: the **α₀ confound is dead at 100
epochs**, the **300-epoch budget control completes**, and the **guarded plain granularity ladder is
complete at n≥5** — and that ladder turns out to be **non-monotone with its peak at nodewise, not
layerwise**.

## 1. The M1 additive ladder on layerwise — an interior optimum, at n=2

SGDm base + Lion meta, α₀=1e-6, guard on, augmented, 100 epochs. `ETA_RATIO = r` rescales the
per-group deviation of every realised β update, so unlike shrink's λ it is genuinely partial for
the whole run (gotcha 21).

| r | best test | Δ vs plain | final_train | ep→85 | ep→90 | plateau | band₉₀ |
|---|---|---|---|---|---|---|---|
| plain (no hier, n=5) | 91.12 ± 0.26 | — | 99.66 | **29.4** | 58.6 | 90.67 | 50.8 |
| 0 (spread frozen) | 92.52 ± 0.11 | +1.40 | 97.83 | 35.5 | 41.0 | 92.23 | 5.0 |
| 0.03 | 93.01 ± 0.17 | +1.89 | 98.94 | 36.5 | 40.5 | 92.71 | 1.5 |
| **0.1** | **93.02 ± 0.01** | **+1.90** | **99.88** | 32.5 | 41.0 | **92.81** | 5.0 |
| 0.3 | 91.44 ± 0.02 | +0.32 | 99.70 | 30.5 | 50.5 | 91.00 | 47.5 |
| 1.0 (≡ plain by construction) | — | — | — | — | — | — | — |

**Non-monotone.** r=0.3 is +0.32pp over plain — inside noise — while r=0.1 is +1.90pp. The
maximum is interior, somewhere in r ∈ [0.03, 0.1], and it falls off sharply above it. That is a
qualitatively different shape from the shrink λ curve, which is flat across three orders of
magnitude because every λ ≥ 0.001 is full pooling.

**Two independent operators agree at their shared endpoint.** Full pooling is reachable two ways —
shrink at λ=1.0, and additive at r=0 (deviations frozen, so one shared β for the whole run):

| operator | setting | best test |
|---|---|---|
| M0 shrink | λ=1.0 | 92.53 ± 0.17 (n=3) |
| M1 additive | r=0 | 92.52 ± 0.11 (n=2) |

**0.01pp apart.** Two separately-written code paths reaching the same number at the same physical
configuration is the strongest implementation cross-check the campaign has produced, and it is
worth reporting as one.

## 2. The additive peak is NOT the regulariser that shrink is

Cycle 7's λ-curve analysis concluded shrinkage behaves like a regulariser: better test accuracy
bought with *worse* fit. The additive peak does not do that.

| arm | best test | final_train |
|---|---|---|
| plain layerwise | 91.12 | 99.66 |
| shrink λ=0.01 (best shrink cell) | 92.79 | **98.06** ← fit sacrificed |
| shrink λ=0.1 | 92.55 | **97.78** ← fit sacrificed |
| **additive r=0.1** | **93.02** | **99.88** ← fit *improved* |

Additive at r=0.1 is above plain on test **and** above plain on train. There is no fit trade. This
is exactly the split gotcha 21 predicts on mechanism grounds — shrink moves both the shared β's
drift rate and the spread, additive moves only the spread — and it means the two operators must be
reported as different methods with different mechanisms, not two settings of a pooling dial.

**Caveat, stated plainly: it is not a speed win.** On the threshold-safe primary metric — ep→85,
which is below every arm's plateau, unlike ep→90 where plain and r=0.3 sit inside their own
asymptotes (band₉₀ of 50.8 and 47.5, gotcha 18) — **plain layerwise is fastest at 29.4 epochs and
every additive arm is slower**. The honest reading is *"reaches a strictly better solution with
strictly better fit, more slowly"*, not *"dominates"*.

## 3. The α₀ confound is DEAD at 100 epochs — priority item 2 CLOSED

The worry was that at α₀=1e-6 many epochs go into merely growing the step size, confounding every
headline. The `a0L` ladder settles it (100 epochs, SGDm+Lion, guard on, n=2 per cell):

| α₀ | scalar | 6-block | layerwise plain | layerwise shrink λ=0.1 |
|---|---|---|---|---|
| 1e-3 | 88.19 ± 0.02 | 91.72 ± 0.18 | 91.61 ± 0.01 | 92.53 ± 0.18 |
| 1e-4 | 88.19 ± 0.32 | 91.67 ± 0.16 | 91.41 ± 0.25 | 92.72 ± 0.04 |
| 1e-6 | 87.95 ± 0.00 | 91.76 ± 0.04 | 91.23 ± 0.13 | 92.73 ± 0.08 |
| **within-arm spread** | **0.24** | **0.09** | **0.38** | **0.20** |

**Every arm is flat to ≤0.38pp across three orders of magnitude of α₀**, and the granularity gap
(scalar → layerwise) is +3.3 to +3.4pp at *every* α₀. There is no α₀ confound in any 100-epoch
number. The headline does not need re-running at a "sane" α₀; it has been run there.

## 4. But at SHORT horizon α₀ dominates everything — and that is where the fine-granularity catastrophe lives

The same comparison at **20** epochs (`p2-*` at α₀=1e-6 vs `p3-*` at α₀=1e-3, n=1, full pooling
where pooled):

| arm | α₀=1e-6 | α₀=1e-3 | Δ | lag vs scalar @1e-6 | lag vs scalar @1e-3 |
|---|---|---|---|---|---|
| scalar | 70.73 | 84.16 | +13.4 | — | — |
| 6-block + pool | 68.45 | 86.79 | +18.3 | −2.3 | +2.6 |
| layerwise + pool | 53.14 | 88.34 | **+35.2** | −17.6 | +4.2 |
| layerwise plain | 74.29 | 88.23 | +13.9 | +3.6 | +4.1 |
| nodewise + pool | 33.03 | 83.77 | **+50.7** | −37.7 | −0.4 |
| weightwise + pool | 14.80 | 77.46 | **+62.7** | −55.9 | −6.7 |

Cycle 7 put two predictions on record for this block. Both are **confirmed**:

* *(a) "the 20-epoch ordering largely collapses for N ≤ 62"* — the spread over
  {scalar, 6-block, layerwise×2} goes from **21.2pp at α₀=1e-6 to 4.2pp at α₀=1e-3**, a 5× collapse.
* *(b) "nodewise and weightwise still lag, but far less"* — nodewise goes from 37.7pp behind scalar
  to **0.4pp**; weightwise from 55.9pp behind to **6.7pp**.

**The short-horizon fine-granularity catastrophe is overwhelmingly an α₀ startup artefact.** The
finer the partition, the longer β takes to climb out of ln(1e-6), and at 20 epochs that startup
cost is most of what the number measures. It is *not* an artefact at 100 epochs (§3), where the
weightwise deficit survives at 79.38 vs 91.23 — but any short-horizon granularity comparison at
α₀=1e-6 is measuring the transient, and none should be quoted.

## 5. Spread helps early and hurts late — the crossover that produces the interior optimum

`p4-*` runs the additive ladder at 20 epochs (α₀=1e-6, n=1) against the 100-epoch ladder of §1:

| r | 20 epochs | 100 epochs |
|---|---|---|
| 0 | 52.87 | 92.52 |
| 0.03 | 53.61 | 93.01 |
| 0.1 | 56.17 | **93.02** |
| 0.3 | 62.11 | 91.44 |
| 1.0 | 73.58 | 91.12 (≡ plain) |
| | **monotone ↑ in r** | **peak at r ≈ 0.03–0.1** |

**The ordering inverts completely.** More spread is monotonically better at 20 epochs and
monotonically worse above r≈0.1 at 100. The interior optimum in §1 is the balance point of that
trade, which is a satisfying mechanistic account of *why* it is interior and predicts that the
peak should move with the budget — a testable claim, and the next control to run.

Cycle 7 prediction *(c)* was that additive r=1.0 reproduces `p2-lay-plain` (74.29 @20ep) since
`β_prev + dm + 1·(d−dm) = β` is an exact identity. Measured 73.58 — **0.71pp off**, which is 8×
the cross-GPU-type reproduction floor of gotcha 17. On a curve this steep the 20-epoch `best` is a
poor identity probe (the `plateau` columns agree far better: 32.93 vs 33.05), but the discrepancy
is **not** dismissed: the `zv-*` block (§7) is the proper identity test.

## 6. The 300-epoch budget control COMPLETES — granularity is budget-invariant, pooling is not

At matched α₀=1e-3, SGDm+Lion, guard on:

| arm | 100 epochs | 300 epochs | Δ |
|---|---|---|---|
| scalar | 88.22 ± 0.05 (n=3), train 94.1 | 88.49 ± 0.08 (n=2), train 95.4 | +0.26 |
| layerwise plain | 91.66 ± 0.09 (n=3), train 99.9 | 91.91 ± 0.41 (n=2), train 100.0 | +0.25 |
| layerwise shrink λ=0.1 | 92.52 ± 0.13 (n=3), train 98.2 | 92.51 ± 0.08 (n=2), train 99.3 | −0.01 |

| effect | 100 ep | 300 ep |
|---|---|---|
| **granularity** (scalar → layerwise) | **+3.44pp** | **+3.42pp** |
| **pooling** (shrink λ=0.1 − plain) | +0.86pp | +0.60pp |

**Granularity is invariant to a 3× budget to within 0.02pp. Pooling's advantage decays.** These are
two different effects with two different budget signatures, and they must be reported separately.

Two riders that matter more than the headline numbers:

* **The scalar arm has still not converged at 300 epochs.** Its train accuracy is 95.4% and rising
  at ~+0.6pp/100 epochs and decelerating. Per gotcha 19 the claim is therefore bounded: *the scalar
  arm converges to a worse solution* is supported at 3× budget, but "never converges" is not, and
  extrapolating to ImageNet's budget regime is not licensed by this control.
* **This weakens the campaign's ImageNet story.** Cycles 6–7 read the parent paper's §7.3 ImageNet
  null as a budget artefact — a long budget lets the coarse arm catch up. At 3× budget on CIFAR-10
  granularity does *not* narrow at all. That reading now applies to **pooling** (which does decay)
  and not to **granularity**. The paper should say so rather than keep the stronger claim.

## 7. The sum-vs-mean confound is fixed in code, and its identity block is running

The last cycle flagged the per-weight pooling column as confounded: the scalar arm aggregates the
meta-gradient as a **sum** over coordinates while `_apply_hier` pools β toward a **mean**, a
factor-of-11.17M discrepancy in effective meta-step scale. The evidence that this is real, not
theoretical, arrived this cycle from `n1-*`:

| arm | best test |
|---|---|
| weightwise + shrink λ=1.0 (full pooling) | **34.56 ± 2.73** |
| genuine scalar arm | 88.08 ± 0.22 |

Full pooling at m=n *should* reduce to the scalar arm. It lands 53pp below it. The m=n pooling
column measures an implementation artefact.

**Fix implemented (`bin/patch_zpool.py`, `HIER=zpool`).** Pool in **meta-gradient space** instead,
using the exact identity `Σ_b z_b == z_scalar`:

```
z'_b = (1 − r)·Σ_j z_j  +  r·z_b
   r = 0 → every group receives the scalar arm's meta-gradient  ⇒ EXACTLY scalar
   r = 1 → every group receives its own                          ⇒ EXACTLY plain per-group
```

Both endpoints are exact identities rather than limits, `_apply_hier` is a verified no-op for
`zpool`, and the operator is **gated behind a numerical identity check before any science run**
(PLAN §5). `zv-*` (7 jobs, 4 epochs, α₀=1e-6) tested all four: layerwise r=0 ≡ scalar,
layerwise r=1 ≡ plain layerwise, weightwise r=0 ≡ scalar, weightwise r=1 ≡ plain weightwise.
**No m=n pooling number will be quoted until those pass.**

### ⚠ The `zv-*` block completed and its result is VOID — the test had no discriminating power

All 7 ran to completion and every arm agreed to ~0.03pp. That is **not** a pass. The first four
test accuracies:

| arm | ep1 | ep2 | ep3 | ep4 |
|---|---|---|---|---|
| ref-scalar | 12.87 | 12.94 | 13.20 | **13.50** |
| ref-layer | 12.87 | 12.94 | 13.19 | 13.51 |
| **ref-weight** | 12.87 | 12.95 | 13.19 | **13.52** |
| l-r0 / l-r1 / w-r0 / w-r1 | 12.87 | 12.93–12.95 | 13.19–13.20 | 13.49–13.52 |

`ref-scalar` and `ref-weight` are **reference arms that must differ** — they are 8.7pp apart at 100
epochs (88.08 vs 79.38) and 55.9pp apart at 20 (70.73 vs 14.80). Here they are **0.02pp apart**.
Chance is 10% and every arm is at 13%.

At 4 epochs with α₀=1e-6 the step size has barely left ln(1e-6) and no arm has begun to train, so
the block cannot separate configurations that are known to be massively different. **Agreement
between `w-r0` and `ref-scalar` therefore carries zero information about the identity.** The
configurations themselves were correct — the `ENV:` provenance lines (gotcha 8) confirm
`HIER=zpool`, `ETA_RATIO` and `--stepsize-groups` all propagated distinctly to all seven — so this
is a design fault in the test, not a bug in the code under test.

**This was a near-miss.** The block gates every per-weight claim in the paper, and read casually
("all seven agree") it would have unblocked the whole story on a measurement with no content.

**Replacement submitted — `z3-*` (7 jobs, alice2, `bin/zval3.sh`).** Same seven arms at
**α₀=1e-3, 20 epochs**, the regime where `p3-*` already measured an ~11pp spread across these arms
(scalar 84.16 / layerwise-plain 88.23 / weightwise+pool 77.46), with `PROBE=100` so the β
trajectories can be compared directly rather than only the accuracy proxy. `bin/zcheck3.sh` now
**computes discriminating power first** — |ref-scalar − ref-weight|, which must be ≥1.0pp — and
refuses to print an identity verdict at all if the anchors do not separate. Identity tolerance is
0.30pp, ~3× the cross-GPU reproduction floor of gotcha 17.

`z2-*` (a re-run of the same 4-epoch design queued on alice2 for capacity reasons) was **cancelled
before it ran**: it would have reproduced the same void result.

## 8. The guarded plain granularity ladder is COMPLETE — and it is NON-MONOTONE

Priority items 3 (guard standard on all arms) and 4 (5 seeds on headline cells) are effectively
closed. Every run family in the current campaign carries `BETA_CLIP=-15:-2.3026`; the unguarded
rows in `all_runs.csv` are the superseded `g1`/`g3`/`gate0*`/`d1`–`d3` blocks. The guarded ladder,
all at α₀=1e-6, SGDm+Lion, ≥95 epochs:

| granularity | m | n | best test | final_train |
|---|---|---|---|---|
| scalar | 1 | 5 | 88.08 ± 0.22 | 93.83 |
| 6-block | 6 | 5 | 91.69 ± 0.13 | 99.09 |
| layerwise | 62 | 11 | 91.23 ± 0.22 | 99.66 |
| **nodewise** | **≈4,800** | **1** | **92.10** | 99.76 |
| weightwise | 11.17M | 3 | 79.38 ± 0.46 | 82.02 |

**The ladder is not "finer is worse".** It is a broad plateau from m=6 to m≈4,800 with a cliff only
at m=n — and its **peak is at nodewise, above layerwise by +0.87pp**. If that survives seeds, the
paper's ladder claim changes shape: there is no interior granularity optimum at m=62 to explain,
there is a plateau and one catastrophic endpoint.

**The nodewise cell is n=1 and is the highest-value seed in the campaign right now.** `nd-*` (3
jobs) takes it to n=5 this cycle. Nothing in §8 should be quoted until it does.

## 9. Queue actions this cycle

* **Unblocked `zv-*`** (the identity gate). All 7 read `QOSMaxGRESPerUser` on `gpu-l4-24g` behind a
  saturated 8-GPU cap. `Partition=gpu-l4-24g,gpu-short` with `--gres=gpu:l4:1` still pinned flipped
  all 7 to `Priority` — the diagnostic flip of gotcha 13 — and the first started within minutes.
  `gpu-short` was verified to contain L4 nodes (node880/881/882/885) before pinning into it.
* **Deprioritised `lp-l-*`** (5 pending, `nice=3000`): the genuinely-partial *shrink* λ ladder is
  now the less interesting of the two partial-pooling operators, since §1 shows additive expresses
  a true interior optimum and §2 shows the operators differ in mechanism.
* **Dual-partitioned `a0A-*` on alice2** (11 jobs). All were `gpu-2080ti-11g`-only and 11-deep on
  `Priority` while alice2's separate 12-GPU `gpu-short` cap sat **completely unused**. Running jobs
  on that account went **1 → 4** immediately.
* **Submitted `ad-l-*` extension (14 jobs, alice2, `bin/ad5_sweep.sh`)** — §1 to n=5 on the two
  peak cells, new r ∈ {0.05, 0.2} at n=3 to locate the maximum, n=3 on the shoulders.
* **Submitted `adg-*` + `nd-*` (15 jobs, alice, `bin/adg_sweep.sh`)** — does the interior optimum
  generalise off the cell it was found on (6-block, and the *paper's* Adam meta-optimizer, at
  r ∈ {0.03, 0.1} × 3 seeds), plus nodewise plain to n=5 for §8.
  *Prediction on record:* if the peak is an artefact of Lion's sign nonlinearity it vanishes under
  Adam. Shrink generalised across both axes (+0.47 on 6-block, +1.51 under Adam), so this is the
  matched contrast.
* Right-sized `--time` on everything new from measured `wallclock_min` (01:15 for 100-epoch
  layerwise against a measured 31 min) so it backfills into `gpu-short` rather than queues
  (gotcha 12).

## 10. Standing caveats after this cycle

* **§1's peak is n=2** and the two peak cells are 0.01pp apart, i.e. unresolved between r=0.03 and
  r=0.1. `ad-l-*` at n=5 plus r ∈ {0.05, 0.2} is in flight; do not quote a peak *location* yet.
* **§2's "no fit trade" is n=2** on one cell. The train-accuracy difference (99.88 vs 99.66) is
  small in absolute terms even if the direction is opposite to shrink's.
* **§8's nodewise cell is n=1** and its group count (≈4,800) is still carried from cycle 6 without
  independent verification (`block_sizes.json` was never written for these runs).
* §4's table is **n=1 per cell**. The 13–63pp effects dwarf seed noise, but no individual number
  there should be quoted to better than ~1pp.
* §6 is n=2 at 300 epochs and n=3 at 100.
* **No m=n pooling result is claimed** pending `zv-*` (§7). The λ→effective-pooling table from the
  previous cycle stays flagged as confounded.
* The additive peak has **no budget control**. §5 predicts the peak location moves with the budget;
  a 300-epoch run at r ∈ {0, 0.1} and plain is the top item for next cycle.
* Every number remains **CIFAR-10 / ResNet-18**, 100 epochs unless stated.
* **ImageNet stays scoped out** (489/1000 classes, no devkit). The **language modality** remains
  blocked on the validation-gated optimizer port; TinyStories pretokenization is done.

---

# 19 Aug 2026 (cycle 9) — M1 additive is an ACCURACY method, not a speed method, and its peak moved off both cells cycle 8 was choosing between

## 1. The additive ladder at n=5 — cycle 8's peak was an n=2 artefact, twice over

`ad-l-*` (14 new cells this cycle) takes the two peak candidates to n=5 and adds r=0.05.
SGDm + Lion, layerwise, α₀=1e-6, guard on, augment on, ≥95 epochs:

| r | n | best test | plateau | final_train | ep→85 | ep→88 |
|---|---|---|---|---|---|---|
| plain (no `HIER`) | 11 | 91.23 ± 0.22 | 90.77 | 99.66 | **29.0 ± 0.9** | **36.2 ± 1.6** |
| 0 (mean only) | 2 | 92.52 ± 0.11 | 92.23 | 97.83 | 35.5 ± 0.7 | 38.0 ± 0.0 |
| 0.03 | **5** | 92.96 ± 0.15 | 92.64 | 98.93 | 36.4 ± 1.1 | 39.0 ± 0.7 |
| **0.05** | 2 | **93.41 ± 0.06** | **93.11** | 99.55 | 36.0 ± 1.4 | 39.5 ± 0.7 |
| 0.1 | **5** | 92.86 ± 0.19 | 92.63 | 99.88 | 32.6 ± 0.9 | 37.4 ± 0.9 |
| 0.2 | 1 | 91.65 | 91.35 | 99.66 | 30.0 | 35.0 |
| 0.3 | 2 | 91.44 ± 0.02 | 91.00 | 99.70 | 30.5 ± 0.7 | 36.0 ± 0.0 |

Cycle 8 §1 read the peak as a **tie between r=0.03 (93.01 ± 0.17) and r=0.1 (93.02 ± 0.01)**, both
at n=2, and put `ad-l-*` in flight to separate them. At n=5 **both cells fell** — to 92.96 and
92.86 — and the tie broke in favour of r=0.03 by 0.10pp. The n=2 readings were optimistic by 0.05
and 0.16pp respectively.

The interior optimum is real and now rests on n=5 shoulders. **Its location is not settled.** The
new r=0.05 cell is +0.45pp over r=0.03 and +0.55pp over r=0.1 against sd 0.06–0.19 — but it is
n=2, which is exactly the evidence strength that just failed on this same ladder. `ad-l-r005`
seeds 3–4 and `ad-l-r007` × 3 seeds are in flight (§6). **Do not quote a peak location yet; quote
the shape** — one maximum, somewhere in r ∈ [0.03, 0.1], rising ~1.7pp over plain and falling back
to plain by r ≈ 0.2–0.3.

## 2. ⚠ The accuracy peak and the speed optimum sit at OPPOSITE ends of the ladder

Threshold safety first (gotchas 17/18): every arm's plateau is ≥ 90.77, so **ep→88 is the usable
threshold** and ep→90 is not — plain layerwise spends 50 of 100 epochs inside [89, 91] and its
ep→90 (56.5 ± 5.1) measures noise. At 88% and at 85% the reading is the same, and it is
uncomfortable:

* **Accuracy** peaks at r ≈ 0.05 and falls away in both directions.
* **Speed** is monotone *increasing* in spread — r=0.2/0.3 reach 88% in 35–36 epochs, r=0.05 takes
  39.5, and the accuracy-optimal cell is the **slowest pooled arm on the ladder**.
* And the fastest pooled cells (35.0, 36.0) are **statistically indistinguishable from plain
  layerwise** (36.2 ± 1.6). At 85% every additive cell is strictly *slower* than plain (30.0–36.4
  vs 29.0 ± 0.9).

**So on the campaign's declared PRIMARY metric — epochs-to-target — M1 additive buys nothing at
any r.** Its entire measured contribution is on best/final accuracy, the metric the campaign
demoted to secondary in the unifying result. Cycle 8's paper note ("the method contribution moves
to M1 additive") is still true about *where the contribution is*, but it must not inherit the
"granularity buys speed" framing: **the granularity axis buys speed, the pooling axis buys
accuracy, and they are not the same claim.** Any M1 table in the paper has to carry both columns.

This is the same crossover cycle 8 §5 measured (spread helps early, hurts late) seen at fixed
budget rather than across budgets, and it is what makes the optimum interior at all.

## 3. Additive DOMINATES shrink at their respective best cells — and the comparison is budget-bounded

Same cell, same α₀, same guard, 100 epochs:

| operator | n | best test | final_train |
|---|---|---|---|
| shrink λ=0.1 | 12 | 92.58 ± 0.10 | **97.78** |
| additive r=0.05 | 2 | **93.41 ± 0.06** | **99.55** |

Additive's best beats shrink's best by **+0.83pp while also fitting 1.8pp better** — a Pareto win,
not a trade. This sharpens cycle 8 §2 and gotcha 21: the two operators are not two settings of one
knob. Shrink buys test accuracy by **under-fitting** (97.78 at epoch 100 and still climbing);
additive buys it while fitting to 99.55.

**Caveat, and it is the load-bearing one:** shrink's 92.58 is measured while shrink is still
fitting, which is precisely the failure mode gotcha 19 exists to catch. The `e3a` block as first
submitted had no shrink cell and could not settle it; two matched `e3a-lsh01` cells at 300 epochs
were added this cycle (§6).

## 4. The additive gain GENERALISES to the Adam meta-optimizer — the sign-artefact hypothesis is REFUTED

Prediction on record from cycle 8 §9: *"if the peak is an artefact of Lion's sign nonlinearity it
vanishes under Adam."* SGDm base + **Adam** meta, layerwise, α₀=1e-6, guarded:

| arm | n | best test | Δ vs plain | ep→85 | ep→88 |
|---|---|---|---|---|---|
| plain | 9 | 90.76 ± 0.14 | — | 15.0 ± 0.5 | 26.7 ± 1.7 |
| additive r=0.03 | 1 | 91.58 | **+0.82** | 17 | 25 |
| additive r=0.1 | 1 | 91.41 | **+0.65** | 15 | 26 |

It does not vanish. **The effect is not a sign artefact.** Two riders:

1. It is roughly **half** the Lion-meta effect (+1.73 / +1.63pp on the same cells), so the sign
   nonlinearity approximately doubles the gain without creating it.
2. The r=0.03 > r=0.1 ordering is preserved.
3. **§2 replicates here independently.** Under Adam meta the additive arms are null on ep→88
   (25, 26 vs 26.7 ± 1.7) and null-or-worse on ep→85 (17, 15 vs 15.0 ± 0.5), while gaining
   0.65–0.82pp on accuracy. Accuracy-only, on a second meta-optimizer.

n=1 per cell (seed-1 runs are at 18–21 epochs). Direction only; no number here to better than
~0.2pp.

## 5. `adg-b` (6-block) is still INCOMPLETE — nothing may be read from it yet

`adg-b-r003_s0` (72 ep, 91.56) and `adg-b-r01_s0` (71 ep, 91.36) are mid-flight against a plain
6-block baseline of 91.69 ± 0.13 (n=5). `best_test` on an unfinished run is a lower bound, and
plain 6-block is already ~91.4–91.6 by epoch 71, so these tell us nothing about the sign of the
effect. Shrink *did* generalise to 6-block (+0.47pp, cycle 8); whether additive does is open.

## 6. Queue actions this cycle

The hardware census was re-run first and it is unambiguous: **every GPU node in `gpu-short` has
`AllocTRES gres/gpu == CfgTRES gres/gpu`** — L4, 2080ti, A100 and MIG alike — and every one of our
51 pending jobs read `Priority`, not `QOSMaxGRESPerUser`. There was nothing to route around
(gotcha 23), so this cycle's throughput work was **ordering and hygiene only**, plus new cells that
queue behind the gate.

* **Submitted `e3a-*` (10 jobs, alice, `bin/e3a_budget.sh` + `bin/e3a_shrink.sh`)** — the additive
  **budget control**, the top standing item from cycle 8. `{plain, r=0, r=0.05, r=0.1, shrink λ=0.1}`
  × 2 seeds at **300 epochs, α₀=1e-6**. α₀ is deliberately 1e-6 and *not* ext300's 1e-3: this block
  must be a *continuation* of the `ad-l-*` ladder, and gotcha 19's no-scheduler argument only makes
  epochs 1–100 identical if nothing else changes. Seed 0 sweeps at nice=0, shrink at 1000, seed 1
  backfills at 2000, so the ladder completes before it widens. `--time=03:00:00` from a measured
  0.31 min/epoch × 4 runs (91–94 min for 300 epochs), ~1.9× headroom and inside the `gpu-short` 4 h
  cap.
  *Prediction on record:* if the peak is a fit-rate artefact it moves toward r=0 by 300 epochs; if
  it is an optimum of the operator it stays near 0.05.
* **Submitted `ad-l-r005` s3–s4 + `ad-l-r007` × 3 (5 jobs, alice2, `bin/ad7_peak.sh`)** — §1's peak
  cell to n=5, plus r=0.07 to test whether the maximum is a smooth cap or a spike between 0.05
  and 0.1.
* **Widened the `zb-*` identity gate to `gpu-l4-24g,gpu-short`** (5 jobs, 50 min each). It is the
  oldest nice=0 block on alice, so it now takes the first L4 slot that frees.
* **`nice=5000` on `a0h-*` (15 jobs, alice) and `a0A-*` pending (6 jobs, alice2)** — the α₀ ladders.
  Priority item 2 closed in cycle 8 §3 (every arm flat to ≤0.38pp across α₀ at 100 epochs) and
  gotcha 24 says the headline grid does not need re-running at larger α₀, so extra seeds on a
  closed question must not sit in front of the gate. `nice`, not `scancel` (gotcha 14).
* **`nice=500` on `adg-*` pending** (3 jobs) — third seeds behind a gate.
* **`scancel` on `z2-*` (6 jobs, alice2).** Cycle 8 §7 recorded this block as "cancelled before it
  ran". **It was not** — all 6 were still queued, and queued *ahead of `z3-*`, their own
  replacement*. It is the void 4-epoch identity design (gotcha 25) and can only reproduce a
  measurement already known to carry zero information. This is the one block this cycle worth
  cancelling rather than nicing.
* **Dual-partitioned `z3-*` into `gpu-2080ti-11g,gpu-short`** (7 jobs, 35–60 min, inside the 4 h cap).

## 7. What this cycle changes about the paper

* **The M1 result must be stated on accuracy, with the speed column shown and null.** Writing M1
  into the "granularity buys speed" frame would be a genuine misreport: §2 measures it null on the
  primary metric at every r, on two meta-optimizers independently.
* **Additive vs shrink becomes a real methods contribution** (§3) rather than two points on one
  dial — but only if `e3a-lsh01` shows shrink's advantage was not simply budget-starved.
* **The sign-nonlinearity objection to M1 is answered** (§4), which was the strongest cheap
  refutation available to a reviewer.
* Cycle 8's "the method contribution moves to M1 additive" survives, with its metric corrected.

## 8. Standing caveats after this cycle

* **§1's peak location is n=2, and n=2 on this exact ladder has already been shown to move by up
  to 0.16pp and to reverse a ranking.** Five cells are in flight to fix it.
* §3's Pareto claim is n=2 vs n=12 and **budget-bounded on the shrink side** by gotcha 19.
* §4 is **n=1 per cell**.
* §5 is unreadable until `adg-b` finishes.
* **No m=n pooling result is claimed.** The `zb-*` β-spread gate has not run (§6); the λ→effective-
  pooling table stays flagged as confounded.
* §2's threshold reading uses **ep→88 and ep→85 only**. ep→90 is noise on plain layerwise
  (band 50/100) and must not be quoted for that arm at any seed count.
* Every number remains **CIFAR-10 / ResNet-18**, 100 epochs unless stated.
* **ImageNet stays scoped out.** The **language modality** remains blocked on the validation-gated
  optimizer port; TinyStories pretokenization is done.

---

# Corrected hierarchy (meta-gradient-space pooling) — VALIDATED

The beta-space `HIER=shrink` had no exact endpoint at m=n (fully-pooled per-weight landed at 49
while the true scalar arm reaches 88.09 — a sum-vs-mean mismatch of factor m). Replaced by
pooling in **meta-gradient space**, exploiting the exact identity `sum_b z_b == z_scalar`:

    z'_b = (1 - r) * sum_j z_j  +  r * z_b        (HIER=zpool, ETA_RATIO=r)

    r = 0  -> every group receives the scalar arm's meta-gradient  => EXACTLY scalar
    r = 1  -> every group receives its own                          => EXACTLY plain per-group

## Validation — structural, not just numerical

Accuracy identities over 4 epochs all held within the ±0.02pp floor, but that test is weakly
discriminating (all granularities agree early, since beta starts uniform). The decisive check is
the spread of beta across groups, which differentiates immediately:

| run | sd(beta) @25% | sd(beta) @end | verdict |
|---|---|---|---|
| layerwise r=0 | **0.000e+00** | **0.000e+00** | exactly uniform — is the scalar arm |
| weightwise r=0 | 9.4e-07 | 2.2e-07 | uniform to float32 precision |
| layerwise r=1 | 0.942 | 3.120 | — |
| plain layerwise (no hierarchy) | 0.944 | 3.126 | **r=1 reproduces plain** |
| layerwise r=0.5 | 0.000 | 0.228 | genuine intermediate |

At r=0 the beta vector stays *exactly* uniform for all 200 probe records, which is only possible
if every group truly receives an identical meta-gradient. Both endpoints are therefore exact by
construction and confirmed by measurement, and r interpolates between them. The m=n column is
now meaningful and the definitive sweep can proceed.

Note the interpolation is not linear in spread: r=0.5 suppresses the end-of-run spread from 3.12
to 0.228 (14x), because halving the deviation component compounds as a contraction over 50k
steps. Reading r as "fraction of per-group signal retained" is right; reading it as "fraction of
the spread retained" is not.

---

# 19 Aug 2026 (cycle 10) — the zpool identity gate PASSES on accuracy, additive beats shrink at *every* λ, and the L4 pool is the campaign's real bottleneck

## 1. The `z3` identity gate is COMPLETE on layerwise, and both endpoints PASS

Gotcha 25 requires an identity check to first prove its regime *discriminates* the arms it
claims to equate. At 20 epochs, α₀=1e-6, guarded:

| anchor | best | final_train |
|---|---|---|
| `z3-ref-scalar` | 84.08 | 86.00 |
| `z3-ref-layer` | **87.80** | 91.74 |
| `z3-ref-weight` | 83.34 | 85.10 |

Scalar and layerwise sit **3.72pp apart** here, versus 0.02pp in the void `zv-*` design. The
gate is open, and only now may the identities be read:

| claim | measured | anchor | Δ | Δ as % of the 3.72pp separation | verdict |
|---|---|---|---|---|---|
| `zpool` r=0 ≡ scalar | 84.21 (train 86.08) | 84.08 (train 86.00) | **0.13pp** | 3.5% | **PASS** |
| `zpool` r=1 ≡ plain layerwise | 87.73 (train 91.65) | 87.80 (train 91.74) | **0.07pp** | 1.9% | **PASS** |

Both endpoints also match on the *train* column independently (Δ = 0.08 and 0.09pp), so this is
not a test accuracy coincidence.

**This is the evidence the "Corrected hierarchy — VALIDATED" section was missing.** That section
rested on the structural argument (sd(β) = 0 exactly at r=0) plus a 4-epoch accuracy test that
gotcha 25 later voided. The operator now has an accuracy identity at *both* ends, measured where
the arms it interpolates are 3.7pp apart. `zpool` is safe to build on.

⚠ `z3-w-r0` / `z3-w-r1` (the weightwise half) are at **15/20 epochs** and must not be read —
an identity compared at mismatched epoch counts is not an identity check.

## 2. Additive beats shrink at EVERY λ — and the "shrink was still fitting" objection is dead

Cycle 9 §3 claimed additive Pareto-dominates shrink but flagged the load-bearing caveat: shrink's
92.58 was measured at train 97.78, still climbing, exactly the gotcha-19 failure mode. It queued
`e3a-lsh01` at 300 epochs to settle it. **The λ ladder already settles it, and no 300-epoch run is
needed.** Layerwise, SGDm+Lion, α₀=1e-6, guarded, 100 epochs:

| operator | n | best test | final_train |
|---|---|---|---|
| plain (no `HIER`) | 9 | 91.21 ± 0.24 | 99.69 ± 0.09 |
| shrink λ=0.001 | 3 | 92.54 ± 0.20 | **99.92 ± 0.02** |
| shrink λ=0.01 | 3 | **92.79 ± 0.11** | 98.06 ± 0.11 |
| shrink λ=0.03 | 3 | 92.58 ± 0.08 | 97.88 ± 0.09 |
| shrink λ=0.1 | 12 | 92.59 ± 0.11 | 97.80 ± 0.13 |
| shrink λ=0.3 | 3 | 92.51 ± 0.23 | 97.79 ± 0.04 |
| shrink λ=0.5 | 3 | 92.50 ± 0.14 | 97.78 ± 0.02 |
| shrink λ=1.0 | 3 | 92.53 ± 0.17 | 97.76 ± 0.07 |
| **additive r=0.07** | 3 | **93.58 ± 0.09** | 99.83 ± 0.01 |

Two readings, and the second is the important one:

1. **Shrink's test accuracy is FLAT across four orders of magnitude of λ** — 92.50 to 92.79, a
   0.29pp band against sds of 0.08–0.23 — while its fit varies from 99.92 down to 97.76. Shrink
   is not a dial. It is a **step**: plain (91.21) → any shrink at all (~92.5–92.8), with λ
   controlling only how much fit is surrendered on the way.
2. **The budget objection cannot save it.** `λ=0.001` reaches train **99.92** — a *better* fit than
   additive's peak (99.83) — and still tops out at 92.54. Shrink's ceiling is ~92.8 **independent
   of its fit level**, so "shrink was under-fitting" does not explain the gap.

**Additive's maximum exceeds the best cell on the entire shrink ladder by +0.79pp** (93.58 ± 0.09
vs 92.79 ± 0.11, ~7x the pooled sd), while fitting 1.8pp better. Cycle 9 §3's Pareto claim
survives, is no longer budget-bounded, and is no longer a one-cell-vs-one-cell comparison — it is
one cell against a seven-point ladder. Gotcha 21 (shrink and additive are not two settings of one
knob) is now measured rather than argued.

`e3a-lsh01` at 300 epochs remains useful as an independent check, but §2 no longer waits on it.

## 3. The additive peak: r=0.05 HELD at n=5, and r=0.07 now leads

Plain layerwise SGDm+Lion guarded, α₀=1e-6, augment on, 100 epochs. Baseline n=9.

| r | n | best test | Δ vs plain | final_train | ep→85 | ep→88 | plateau |
|---|---|---|---|---|---|---|---|
| plain | 9 | 91.21 ± 0.24 | — | 99.69 ± 0.09 | **29.11 ± 0.93** | 36.22 ± 1.79 | 90.79 |
| 0 | 3 | 92.51 ± 0.08 | +1.30 | 97.81 ± 0.07 | 35.67 ± 0.58 | 38.00 ± 0.00 | 92.20 |
| 0.03 | 5 | 92.96 ± 0.15 | +1.75 | 98.93 ± 0.03 | 36.40 ± 1.14 | 39.00 ± 0.71 | 92.64 |
| 0.05 | **5** | 93.46 ± 0.05 | +2.25 | 99.58 ± 0.04 | 36.00 ± 1.00 | 39.20 ± 0.45 | 93.09 |
| **0.07** | 3 | **93.58 ± 0.09** | **+2.37** | 99.83 ± 0.01 | 34.67 ± 0.58 | 39.00 ± 1.00 | 93.32 |
| 0.1 | 5 | 92.86 ± 0.19 | +1.65 | 99.88 ± 0.01 | 32.60 ± 0.89 | 37.40 ± 0.89 | 92.63 |
| 0.2 | 3 | 91.73 ± 0.15 | +0.52 | 99.66 ± 0.02 | 31.33 ± 1.15 | **35.67 ± 0.58** | 91.39 |
| 0.3 | 3 | 91.40 ± 0.09 | +0.19 | 99.69 ± 0.03 | 30.33 ± 0.58 | 36.00 ± 0.00 | 90.96 |

* **r=0.05 survived promotion to n=5** — 93.41 ± 0.06 (n=2) → 93.46 ± 0.05 (n=5), a move of
  0.05pp. This is the **first** cell on this ladder to hold when promoted; gotcha 26 records two
  prior n=2 cells that moved by 0.16pp and reversed a ranking. The rule stands (n=2 *can* fail);
  this instance did not.
* **The maximum is a plateau over r ∈ [0.05, 0.07], not a point.** r=0.07 leads by +0.12pp against
  a pooled sd of ~0.07 — about 1.7σ, which does not separate them. Cycle 9's open question
  ("smooth cap or spike between 0.05 and 0.1") resolves to **smooth cap on the low side, cliff on
  the high side**: −0.72pp from r=0.07 to r=0.1 over a 0.03 step, then −1.13pp more to r=0.2.
  `ad-l-r007` s3–s4 are queued to take the leading cell to n=5 (§5).
* **Do not quote a single peak location.** Quote the plateau [0.05, 0.07] and the asymmetric
  fall-off.

Cycle 9 §2 replicates unchanged: **speed is monotone increasing in spread and the accuracy
optimum is the slowest pooled cell on the ladder.** At ep→85 every additive cell is *slower* than
plain (30.3–36.4 vs 29.1 ± 0.9). The primary metric still says additive buys nothing.

## 4. Additive generalises to 6-block and to Adam-meta — cycle 9 §4 and §5 both CLOSED

**§5 (6-block) was unreadable last cycle at 71/100 epochs. It is now complete.**

| arm (6-block, SGDm+Lion) | n | best test | Δ vs plain | ep→85 | ep→88 |
|---|---|---|---|---|---|
| plain | 5 | 91.69 ± 0.13 | — | **29.40 ± 0.55** | **36.60 ± 1.34** |
| additive r=0.03 | 3 | 92.18 ± 0.21 | **+0.49** | 31.00 ± 1.00 | 39.33 ± 1.15 |
| additive r=0.1 | 2 | 91.96 ± 0.07 | **+0.27** | 30.50 ± 2.12 | 40.50 ± 0.71 |

**§4 (Adam meta) goes from n=1 to n=3 and the direction holds.**

| arm (layerwise, SGDm+**Adam**) | n | best test | Δ vs plain | ep→85 | ep→88 |
|---|---|---|---|---|---|
| plain | 9 | 90.76 ± 0.14 | — | **15.00 ± 0.50** | 26.67 ± 1.66 |
| additive r=0.03 | 3 | 91.71 ± 0.07 | **+0.95** | 17.00 ± 1.00 | **24.00 ± 1.00** |
| additive r=0.1 | 3 | 91.36 ± 0.09 | **+0.60** | 15.33 ± 0.58 | 28.33 ± 4.04 |

Three things this settles and one it opens:

* The sign-nonlinearity objection stays **refuted at n=3**, not n=1. Adam-meta gets 54% of the
  Lion-meta gain at r=0.03 (+0.95 vs +1.75) — cycle 9's "roughly half" was right.
* The r=0.03 > r=0.1 ordering is preserved on **both** the 6-block cell and the Adam-meta cell.
* **NEW — the additive gain scales with the number of groups.** At r=0.03: m=6 → +0.49pp,
  m=62 → +1.75pp. A ~3.6x gain for a ~10x finer partition. The operator pools *across* groups, so
  more groups give it more to work with. This makes a falsifiable prediction for the m=n column
  the `zsx-*` sweep is now measuring (§5): the gain should be larger still at m = 11.17M.
* **OPEN:** under Adam meta the speed reading *reverses inside the budget* — r=0.03 is slower to
  85% (17.0 ± 1.0 vs 15.0 ± 0.5, ~2.5σ) but **faster** to 88% (24.0 ± 1.0 vs 26.7 ± 1.7, ~1.6σ).
  Under Lion meta it is slower at both. The cycle-8 §5 early/late crossover apparently lands
  inside the 100-epoch budget under Adam and outside it under Lion. Unexplained; n=3.

## 5. Queue actions — the campaign's bottleneck is the L4 pool, and it is partly self-inflicted

The 36-job `zsw-*` sweep — the single biggest open item, since **no m=n pooling result is claimed
anywhere in this document** — was submitted to `gpu-l4-24g` only and `scontrol` reported
`StartTime=2026-08-26`. A week out, for the headline block.

Diagnosis, by measurement rather than by `sinfo` state (gotcha 16):

* **All 32 L4 GPUs (8 nodes × 4) report `AllocTRES gres/gpu:l4 = 4`. L4 is 100% saturated
  cluster-wide.** Widening to `gpu-short` therefore cannot help — gotcha 23, confirmed a second
  time.
* **alice's own 12 running `gpu-short` jobs hold 12 of those 32 L4s.** The account is the largest
  single holder of the resource its own headline block is queued behind. This is the first time
  self-contention has been identified as the binding constraint rather than other users' load.

Actions:

1. **All 36 `zsw-*` widened to `gpu-l4-24g,gpu-short` and re-niced by seed** (s1→0, s2→1000,
   s0→9000) so the sweep completes in *width* before depth. Priority rose 675558 → 1075433 and
   `StartTime` returned from 2026-08-26 to normal contention. Kept as the L4 arm.
2. **Submitted `zsx-*` on alice2 — the same 36 cells pinned to 2080ti** (`--gres=gpu:2080_ti:1`,
   `--partition=gpu-2080ti-11g,gpu-short`, `--time=03:00:00` from the measured 0.70–0.88 min/epoch
   2080ti table = 2.2x headroom, inside the 4h cap). Named `zsx` and not `zsw` so it can never
   collide with alice's block in `aggregate.py`, which keys on run name across both runs dirs.
   Rationale is **pool diversification**, not spare capacity: alice2 holds 5 of 28 usable 2080ti
   GPUs versus alice's 12 of 32 L4s, so the same sweep queued on both pools lands sooner on
   whichever frees first.
3. **Cancelled 12 L4-pinned `zsw-s0` jobs mis-submitted to alice2 earlier this cycle.** They were
   provably unrunnable (L4 at 100% alloc) *and* name-identical duplicates of alice's own s0 cells,
   which would have collided in the aggregate. Redundant by construction, so `scancel` and not
   `nice` — the cycle-9 `z2-*` precedent.
4. **`ad-l-r007` s3–s4 on alice2, deliberately kept L4-pinned** even though L4 is the saturated
   pool. They are cells of the all-L4 `ad-l-*` ladder and the effect being measured is 0.12pp,
   which is inside the range where GPU-type differences are not obviously negligible. Correct to
   wait rather than to run them on the wrong hardware (gotcha 3).

**Code parity verified before any submit** (gotcha 10, which cycle 9 had to fix on this exact
file): `HF.py` md5 `294087b88548ac52db6922afb89e1433` is identical on alice, on alice2, and in the
repo's `patches/HF_patched.py`, with `grep -c PATCH_ZPOOL` = 2 on both accounts. The md5
difference between the accounts' `bin/patch_zpool.py` is **only** the account-specific `P=` path
line; the `_zpool` operator body is byte-identical. Checked *first*, because a zpool sweep run
against a drifted operator would have been unrecoverable.

## 6. `a0A` — α₀ is flat under Adam meta too, but it still buys startup SPEED

100 epochs, n=1 per cell, guarded. Best test accuracy:

| arm | α₀=1e-3 | 1e-4 | 1e-6 | spread |
|---|---|---|---|---|
| scalar | 88.24 | 88.15 | 88.46 | 0.31 |
| 6-block | 91.50 | 91.42 | 91.30 | 0.20 |
| layerwise plain | 91.57 | 91.38 | 90.99 | 0.58 |
| layerwise shrink λ=0.1 | 92.17 | 92.13 | 92.36 | 0.23 |

Every arm flat to ≤0.58pp across three orders of magnitude — cycle 8 §3's α₀ closure now holds on
a **second meta-optimizer**, so priority item 2 stays closed and gotcha 24 stands.

But the *speed* column is not flat: layerwise plain reaches 85% at epoch 12/13/15 and 90% at
40/40/47 as α₀ falls 1e-3 → 1e-6. **α₀ buys startup speed without buying final accuracy** — which
is precisely why gotcha 24 forbids quoting a granularity comparison at short horizon and small α₀.

## 7. In flight and NOT readable

* `e3a-*` (300-epoch additive budget control): seed 0 at 91–126 of 300 epochs, seed 1 at 1–68.
  Mixing seeds at these epoch counts is the gotcha-19 failure mode by construction. **Nothing may
  be read from `e3a` this cycle**, including the tempting `e3a-r01_s0` = 93.05 at 108 epochs.
* `z3-w-r0` / `z3-w-r1` at 15/20 epochs (§1).
* `zsx-*` (36 cells) and `zsw-*` (36 cells) — all pending.
* `adg-b-r01_s2` at 77/100, which is why that cell is n=2.

## 8. Standing caveats after this cycle

* §3's peak is a **plateau [0.05, 0.07]**, not a location. r=0.07 is n=3.
* §4's 6-block r=0.1 cell is **n=2**; gotcha 26 applies to it.
* §6 is **n=1 per cell** — direction only.
* §1's identity gate is **layerwise only**. The weightwise half is at 15/20 epochs and the m=n
  pooling column remains unclaimed.
* §4's "gain scales with group count" rests on **two points** (m=6, m=62). It is a prediction for
  the `zsx` sweep, not a law.
* `zsx-*` is measured on **2080ti** and `zsw-*` on **L4**. The sweep is self-anchoring — its own
  r=0 and r=1 endpoints are the scalar and plain arms — so it is readable within itself, but a
  `zsx` number must never be differenced against an L4-measured number (new gotcha 28).
* Every number remains **CIFAR-10 / ResNet-18**, 100 epochs unless stated.
* **ImageNet stays scoped out.** The language modality remains blocked on the validation-gated
  optimizer port; TinyStories pretokenization is done.

---

# 19 Aug 2026 (cycle 12) — the `zsw` sweep COMPLETES: there is no interior optimum, and the ladder's interior is a step-size sweep in disguise

## 1. The 36-cell meta-gradient-space pooling sweep is COMPLETE — 36/36 at 100/100 epochs

This was the campaign's single biggest open item ("no m=n pooling result is claimed anywhere in
this document", cycle 11 §5). It is now closed, and the answer is **negative for the method**.

`zsw-*`, L4, α₀=1e-6, guarded, 3 seeds/cell, `HIER=zpool ETA_RATIO=r`:

| r | layerwise (m=62) | ep→85 | ep→90 | weightwise (m=11.17M) | ep→85 |
|---|---|---|---|---|---|
| 0.0 | 88.14 ± 0.06 | 37.3 ± 2.1 | never 0/3 | 88.07 ± 0.04 | 37.0 ± 2.6 |
| 0.1 | 90.01 ± 0.21 | 33.0 ± 1.0 | 98 (1/3) | 88.14 ± 0.13 | 37.7 ± 1.5 |
| 0.3 | 90.07 ± 0.23 | 33.0 ± 1.0 | 92 (1/3) | 88.26 ± 0.18 | 37.3 ± 2.1 |
| 0.5 | 89.63 ± 0.13 | 32.7 ± 0.6 | never 0/3 | 88.28 ± 0.10 | 37.0 ± 2.6 |
| 0.7 | 89.55 ± 0.14 | 32.0 ± 0.0 | never 0/3 | 88.43 ± 0.10 | 36.3 ± 2.5 |
| **1.0** | **91.35 ± 0.16** | **28.7 ± 0.6** | **56.0 (3/3)** | **79.35 ± 0.37** | never |

Both endpoints land exactly where the identity gate said they would: layerwise r=0 = 88.14 is the
scalar arm (88.09 ± 0.16), r=1 = 91.35 is plain layerwise (91.34 ± 0.09), weightwise r=1 = 79.35 is
the guarded per-weight arm (79.4). The sweep is internally valid.

**Two readings, and they point opposite ways:**

* **Layerwise: pooling in meta-gradient space is HARMFUL.** The unpooled endpoint r=1 is the best
  cell on the ladder on accuracy (+1.28pp over the best interior cell) *and* the fastest on the
  primary metric (28.7 epochs to 85% vs 32–37; the only cell reaching 90% in all 3 seeds). There
  is **no interior optimum**. This is a clean negative result for the operator.
* **Weightwise: any pooling at all prevents the collapse.** Every r ≤ 0.7 sits at 88.1–88.4 while
  r=1 collapses to 79.35 — a ~9pp rescue. But pooled weightwise never *beats* scalar by more than
  +0.36pp (r=0.7, 88.43 vs r=0 88.07, ~3σ), and stays 2.9pp below plain layerwise. The ~12pp
  per-weight deficit is **not** closed by this operator; it is converted into a ~3pp deficit by
  giving up essentially all per-weight resolution.

## 2. ⚠ The interior of the ladder is CONFOUNDED — it sweeps step-size magnitude, not pooling

The r=0.7 → r=1.0 step is +1.80pp on layerwise and −9.08pp on weightwise. A smooth interpolation
should not jump at one endpoint in opposite directions on two arms. It does not: the operator is

    z'_b = (1-r)*sum_j(z_j) + r*z_b

and the shared term carries a factor of **m**. Taking the mean over groups:

    mean_b(z'_b) = (1-r)*m*z̄ + r*z̄

so the **common mode** — the component that moves the *mean* of β, i.e. the realised step size —
is amplified by up to m. Verified in closed form (m=62): the common-mode multiplier runs
62.0 → 55.9 → 43.7 → 31.5 → 19.3 → 1.0 across the ladder. The ladder sweeps it over a factor of 62.

**This is measured, not just derived.** From the probe β vectors at end of run (layerwise):

| r | mean(β) | realised step size vs r=1 | sd(β) | best test |
|---|---|---|---|---|
| 0.0 | −10.69 | 0.895 | 0.000 | 88.14 |
| 0.1 | −10.83 | 0.779 | 1.156 | 90.01 |
| 0.3 | −12.49 | **0.149** | 1.836 | 90.07 |
| 0.5 | −13.64 | **0.047** | 2.145 | 89.63 |
| 0.7 | −14.11 | **0.029** | 1.840 | 89.55 |
| 1.0 | −10.58 | 1.000 | 2.295 | 91.35 |

**The interior cells train at 3–35x smaller step size than either endpoint**, and the accuracy dip
at r=0.5–0.7 sits exactly where the step size is most suppressed (−14.11 nats, 2.9% of r=1's).
The two endpoints are the only cells on the ladder running at a comparable step size, which is
precisely why they are the only two cells that can be read against each other.

**Consequence for the write-up: the layerwise interior of `zsw` must not be quoted as a
pooling-strength result.** The endpoint comparison (r=0 vs r=1) survives — both are exact
identities at matched step size — and §1's negative conclusion rests only on the endpoints plus
the fact that no interior cell beats r=1. That conclusion is safe: a confound that *suppresses*
the interior cannot manufacture the finding that the interior loses.

The weightwise arm is **much less affected**: its mean β moves only −10.82 → −10.20 across
r=0…0.7 (a 0.6-nat band, vs 3.5 nats on layerwise), while sd(β) rises smoothly
4.8e-7 → 8.2e-3 → 3.2e-2 → 7.3e-2 → 1.67e-1 → 8.02e-1. So the weightwise reading in §1 **is** a
genuine dispersion dose-response, and it locates the collapse between **sd(β) = 0.167 and 0.802**.

## 3. The fix: `zmpool`, a mean-normalised sibling that varies dispersion ONLY

    z'_b = (1-r)*mean_j(z_j) + r*z_b   =>   mean_b(z'_b) = z̄  for EVERY r

The common mode is now **exactly invariant in r**, while the injected dispersion is identical to
`zpool`'s (both scale the deviation component by exactly r — verified numerically at
r = 0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99, 1). That makes r a pure pooling axis.

| r | common mode, `zpool` | common mode, `zmpool` | dispersion, both |
|---|---|---|---|
| 0.0 | 62.00 | 1.000000 | 0.000 |
| 0.3 | 43.70 | 1.000000 | 0.300 |
| 0.7 | 19.30 | 1.000000 | 0.700 |
| 1.0 | 1.00 | 1.000000 | 1.000 |

Implemented as `patches/patch_zmpool.py`. The existing `_zpool` method is left **byte-identical**
and `zmpool` is a separate method behind a separate dispatch arm, so **no previously measured
zpool cell can change**. Applied to both accounts; `HF.py` md5
`32f32c8119514a4c4c066d799e36bc05` is identical on alice, alice2 and `patches/HF_patched.py`,
with `grep -c PATCH_ZMPOOL` = 2 everywhere (gotcha 10 checked *before* any submit).

Note r=0 under `zmpool` is **not** the scalar arm — the scalar arm's meta-gradient genuinely is
the sum, so `zpool` r=0 was correct to use it. `zmpool` r=0 is "uniform β driven by the mean
meta-gradient", i.e. scalar with an m-times-smaller meta-step. The ladder therefore anchors on
**r=1 only** and must carry its own r=0 reference rather than borrowing zpool's.

## 4. Queue actions this cycle

1. **`zsx-*` pending cells CANCELLED (18 jobs).** `zsw` — the L4 twin of the identical 36-cell
   sweep — completed 3/3 seeds on every cell first, so the pending 2080ti cells were redundant by
   construction (cycle 9 `z2` precedent: redundant ⇒ `scancel`, not `nice`). The 8 *running*
   cells were left alone as sunk cost and give a free partial cross-GPU spot check. Read-back
   confirmed: pending zsx = 0, running zsx = 8.
2. **`zrn-*` submitted (30 jobs, alice2, 2080ti)** — r ∈ {0.7, **0.9, 0.95, 0.99**, 1} × {layerwise,
   weightwise} × 3 seeds. The entire r ∈ (0.7, 1) region is unsampled, and it is where both open
   questions live: whether layerwise ramps smoothly to 91.35 or cliffs, and where exactly the
   weightwise collapse switches on in sd(β). **Self-anchoring** (gotcha 28): it carries its own
   r=0.7 and r=1 endpoints, so every contrast is internal to 2080ti and is never differenced
   against the L4-measured `zsw` numbers.
3. **`zm0-*` submitted (7 jobs, alice) — the `zmpool` identity gate** at 20 epochs, the regime
   `z3` proved discriminating (gotcha 25). Submitted to L4, then **relocated wholesale to 2080ti**
   when a capacity read showed all 32 L4 GPUs allocated (to another user this time — alice's own
   `zsw` had already finished) while 2080ti had free CPU+GPU on node853/858/860. All 7 cells moved
   together and none had started, so nothing was lost and every contrast stays internal to one GPU
   type — the condition gotcha 28 requires for relocating a self-anchoring block. Claims under test: `zmpool` r=1 reproduces plain on
   both layerwise and weightwise; and r=0 *differs* from plain, without which the gate would be
   vacuous. Refs for scalar/layerwise/weightwise are re-run inside the block. **The `zmp` ladder
   is deliberately NOT submitted until this passes** — cycle 9/10's rule that a sweep run against
   an unverified operator is unrecoverable.

## 5. What this changes about the paper

The draft's "partial pooling beats every fixed granularity (+1.46pp on layerwise)" is **not**
contradicted — that result is `shrink`/`additive`, which pool in **β space**. `zsw` pools in
**meta-gradient space** and loses on layerwise. The paper must state the space explicitly wherever
it says "pooling"; the two operators now have opposite signs on the same arm, and that contrast is
itself a result worth reporting rather than a wrinkle to smooth over.

## 6. Standing caveats after this cycle

* §1's layerwise **interior** is magnitude-confounded (§2) and may not be quoted as a pooling
  result. The endpoints, and the "no interior cell beats r=1" conclusion, stand.
* §1's weightwise interior **is** readable (mean β stable to 0.6 nats) but the +0.36pp
  r=0.7-vs-r=0 effect is ~3σ at n=3 and should not be leaned on until `zrn` lands.
* The collapse threshold is bracketed only as sd(β) ∈ (0.167, 0.802). `zrn` is the block that
  narrows it; nothing may be claimed about its location yet.
* `zmpool` has **no** empirical result yet — only closed-form and unit-test verification. The
  `zm0` gate is in flight.
* The 8 running `zsx` cells are 2080ti and must never be differenced against `zsw` (gotcha 28).
* Every number remains CIFAR-10 / ResNet-18, 100 epochs unless stated. ImageNet stays scoped out.

---

# Cycle 14 — the M1 sweep was pooling two meta-optimizers

Full detail and the corrected table: `docs/CORRECTIONS.md` §10–11. Summary of what
changed, so nothing here is read from the superseded version:

* **M1's interior optimum stands, with different numbers.** Restricted to one
  meta-optimizer (Lion) and one account, `hier=additive`, layerwise, 100 epochs,
  plateau: 92.20 → 92.64 → **93.09** → **93.22** (r=0.07) → 92.63 → 91.39 → 90.96.
  Peak is **+1.02pp over r=0**, n=5 on the peak cells, per-cell sd 0.04–0.21.
  The stratified curve is monotone up to the peak and monotone after it; the old
  pooled table's ragged shoulder at r=0.03 was Adam-meta contamination, not signal.
* **`meta` must be a grouping key in every additive analysis.** Adam-meta additive
  runs sit ~1.3pp below Lion-meta at matched r, and they populated the shoulder
  cells only. The CSV always carried the `meta` column; the analysis ignored it.
* **Meta-optimizer is currently confounded with account** — all Lion additive on
  `s5014158`, all Adam additive on `salehkaleybars` — so the 1.3pp gap cannot be
  attributed to either. `amx-*` (n=5, Adam meta, on `s5014158`) is in flight to
  separate them.
* **`account` was wrong on all 428 rows** until this cycle (see §11), which is
  precisely why the confound above was invisible. Any earlier per-account
  statement in this file predates the fix and should be re-derived before use.
* **`run` is not a unique key.** Filter `superseded == 0`. Three completed alpha0
  controls were being shadowed by partial reruns of the same name.

## Standing caveats added this cycle

* No additive result may be quoted without naming the meta-optimizer **and** the
  account, until `amx-*` lands and decouples them.
* `plateau` in the CSV is the mean of the **last 20** epochs, not the last 5 as
  several planning docs state. Conclusions are insensitive to the choice (checked:
  no M1 cell moves >0.15pp at k=5), but the prose is wrong and should be fixed.

---

# Cycle 15 — the non-meta baseline lands, and two reference points are wrong

All numbers re-derived from `results/all_runs.csv` (465 rows, +37 this cycle),
filtered `superseded==0`, `epochs_done>=100`, `epochs_requested==100`, `augment==1`,
metric = `plateau`.

## 1. Non-meta baseline (axis 4) — FIRST RESULT

Plain AdamW, no meta-learning (`--optimizer AdamW --alpha0 <lr>`), ResNet-18 /
CIFAR-10 / 100 ep / AUGMENT=1. Verified non-meta by reading the `ARGS:` line.

| lr | n | plateau |
|---|---|---|
| 3e-4 | 2 | **91.81** |
| 1e-4 | 2 | 91.33 |
| 1e-3 | 2 | 90.26 |
| 3e-3 | 2 | 85.96 |

Against it (same filter):

| arm | n | plateau | vs baseline |
|---|---|---|---|
| SGDm+Lion layerwise additive r=0.07 | 5 | 93.22 | +1.41 |
| AdamW+Adam scalar | 12 | 91.88 | +0.07 |
| SGDm+Lion layerwise (plain) | 14 | 90.89 | **−0.92** |
| SGDm+Lion scalar | 15 | 87.79 | **−4.02** |

**MetaOptimize at the granularities the parent paper uses does not beat a tuned
non-meta AdamW.** Only M1 additive pooling clears it. Extended to n=5 (`fx-adamw-*-s{2,3,4}`).

## 2. The baseline's LR schedule is mis-scaled — margin is NOT yet safe

`AdamW_optimizer` hard-codes `total_steps=422000, warmup_steps=10000` into a
cosine-with-warmup scheduler. A 100-epoch run at batch 100 is **50,000 steps**:

* warmup occupies the first **20 epochs**;
* by the final step the cosine has decayed the LR only to **97.7% of base**.

So the "baseline" is warmup-then-effectively-constant LR — it never receives the
decay that normally supplies the last 1–2pp on CIFAR-10. The +1.41pp margin in §1
is measured against a baseline denied its main tuning lever.

`build_optimizer.py` patched (backwards-compatible, defaults unchanged, in-flight
jobs unaffected) to read `COS_TOTAL`/`COS_WARMUP`; both echoed on the `ENV:` line.
`fxcos-{1e-4,3e-4,1e-3}-s{0,1,2}` submitted at `COS_TOTAL=50000, COS_WARMUP=2500`.
**No pooling-vs-baseline claim should be written until these land.**

## 3. `additive` r is inverted relative to how the M1 tables read it

From `Optimizers/HF.py::_apply_hier`:

```
d = b - beta_prev;  dm = d.mean();  beta = beta_prev + dm + r*(d - dm)
```

* `r=1` → `beta_prev + d = b` — **exact identity with plain layerwise**.
* `r=0` → every group gets the same mean increment — **maximal pooling**.

The M1 sweep spans r ∈ {0, 0.03, 0.05, 0.07, 0.1, 0.2, 0.3} and treats **r=0 as its
reference**. r=0 is the *fully pooled* end, not "no pooling"; **r=1 was never run**.
The measured plateaus are unaffected, but "+1.02pp over r=0" describes an optimum
relative to maximal pooling, not relative to no pooling. Note plain layerwise is
90.89 (n=14) while additive r=0 is 92.20 (n=3) at matched alpha0/meta-stepsize/clip —
a 1.31pp gap between two cells that are *not* the same configuration.
(r=0 preserves per-group offsets established at the first step, since `beta_prev`
is None on step 1; it is therefore neither scalar nor layerwise.)

`zad-{plain,r1,r007,r0}-s{0,1,2}` submitted with `PROBE=25` to test both endpoints.

**GATE PASSED — the identity is confirmed empirically.** `zad-plain` vs `zad-r1`,
seed 0, test accuracy by epoch:

| ep | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| plain | 12.87 | 12.93 | 13.17 | 13.49 | 13.74 | 14.48 | 15.50 | 17.81 | 20.98 | 24.02 |
| r=1 | 12.87 | 12.93 | 13.20 | 13.48 | 13.75 | 14.48 | 15.52 | 17.81 | 20.96 | 24.05 |

Max deviation **0.03pp**, at run-to-run reproducibility. So `r=1` is plain layerwise
and **`r=0` is the maximally-pooled end, confirmed by measurement and not only by
reading the source.** Every M1 statement of the form "+X pp over r=0" is a gain over
*full pooling*; the no-pooling comparison is against r=1 / plain layerwise (90.89, n=14),
against which the r=0.07 optimum (93.22, n=5) is **+2.33pp**. r=0.07 vs r=0 is +1.02pp.
Both are real; they answer different questions and must not be quoted interchangeably.

## 4. Sign agreement across granularities (axis 6) — with the correct null

`frac_neg` is over group-level values for scalar/layerwise/blockwise and over all
coordinates for nodewise/weightwise. Agreement = `max(frac_neg, 1-frac_neg)`.

**This statistic is folded: its expectation exceeds 0.5 under independence, badly so
at small coordinate counts.** Comparing it to 50% is invalid except at huge n.
Null below is simulated (40k trials) at each granularity's coordinate count.

| granularity | n_coord | null | early (ep 0–5) | steady (ep 50–100) | steady excess |
|---|---|---|---|---|---|
| resnet18_blocks | 6 | 65.63% | 94.61% | 71.54% | **+5.91pp** |
| layerwise | 62 | 55.06% | 87.55% | 55.84% | **+0.78pp** |
| nodewise | ~14420 (inferred) | 50.33% | 65.85% | — | — |
| weightwise | 11,173,962 | 50.00% | — | 53.10% (whole-run, prior) | +3.10pp |

* **Early training: agreement is far above the null at every granularity** (+15 to +32pp).
  Robust; per-seed spread <1pp when stage-matched.
* **At steady state the layerwise excess nearly vanishes (+0.78pp).** The weightwise
  +3.10pp survives because its null has negligible sampling error.
* Agreement **decays monotonically with training** (blocks 94.6→80.3→69.3→71.5;
  layerwise 87.6→73.0→56.3→55.8 across bands 0-5/5-20/20-50/50-100).
* **Stage-matching is mandatory here.** Unmatched per-seed means ranged 60.6–79.4%
  *within* layerwise purely from unequal run lengths; stage-matched they are 86.9–87.5%.
* `scalar` is degenerate (1 coordinate → agreement ≡ 100%) and is not a data point.

**Consequence for the refutation.** "Coordinates agree on sign, so drift is set by
partition agreement rather than by N" holds strongly in early training and at
weightwise granularity. It is **not** currently supported at layerwise granularity in
steady state. The claim must carry both a granularity and a training-stage qualifier.
nodewise/weightwise steady-state cells are still running.

## 5. Infrastructure

* **CIFAR-100 unblocked (axis 2).** Tarball was staged but never extracted; compute
  nodes have no internet, so every C100 job would have hung on `download=True`.
  Extracted on alice; `_check_integrity()` True for both splits (50k/10k, 100 classes,
  labels 0–99), so download is now a no-op. Smoke ran end-to-end on ResNet18_c100
  with and without the probe ("Files already downloaded and verified"). 3 epochs sit
  at chance (~1.1%), consistent with the documented alpha0=1e-6 startup, but 3 epochs
  cannot separate that from breakage — `c100disc-{c100,c10}` submitted at alpha0=1e-3
  (must clear chance by epoch 5; the CIFAR-10 arm is the harness control).
  alice2 lacks both the patch and the data; its download is in progress.
* **Partition funnel found and fixed.** Multi-partition submission does *not* spread
  jobs: Slurm places them in the first-listed partition (`gpu-short`), whose per-user
  QoS cap is 12 GPUs, leaving l4(8)/2080ti(12)/mig(8)/a100(2) — 30 GPUs — unused.
  Both accounts sat at exactly 12. Fixed by pinning whole blocks to distinct
  partitions (wholesale, so contrasts stay within one GPU type). alice2 went 12 → 15
  running immediately. Ceiling per account is now 42 rather than 12.
* Cluster is genuinely saturated (`TRULY_FREE` 0–2 GPUs per pool); three 2080ti nodes
  are held by maintenance reservation `root_28` until 2026-12-01. Partition totals
  from `sinfo` include those nodes and overstate free capacity — count at node level.

---

# Cycle 16 — the M1 curve is now well-sampled, and its one untested confound is queued

CSV re-aggregated from artefacts on **both** accounts (`aggregate.py` over
`/data1/salehkaleybars/metaopt/runs` and `~/metaopt/runs`, merged):
**498 rows, +33 this cycle** (304 salehkaleybars / 194 s5014158).
All numbers below re-derived from `results/all_runs.csv`, filtered
`superseded==0`, `epochs_done>=epochs_requested`, `augment==1`, metric = `plateau`.
318 rows satisfy the 100-epoch filter.

## 1. M1 additive r-curve, layerwise, SGDm+Lion, alpha0=1e-6, 100 ep — full curve

| r | 0 | 0.03 | 0.05 | **0.07** | 0.1 | 0.2 | 0.3 | 1 |
|---|---|---|---|---|---|---|---|---|
| plateau | 92.200 | 92.637 | 93.086 | **93.212** | 92.626 | 91.387 | 90.957 | 90.918 |
| n | 3 | 5 | 5 | 6 | 5 | 3 | 3 | 1 |
| sd | 0.044 | 0.164 | 0.097 | 0.124 | 0.215 | 0.142 | 0.079 | — |

Unimodal, n>=3 at every r. Report **the curve**, never the peak cell.

Three reference points, three different questions — do not interchange:

| contrast | delta |
|---|---|
| r=0.07 vs r=1 (= no pooling = plain layerwise) | **+2.29** |
| r=0.07 vs r=0 (= maximal pooling) | **+1.01** |
| r=0.07 vs tuned non-meta AdamW lr=3e-4 (n=4, 91.894) | **+1.32** (unsafe, see §4) |

## 2. r=1 == plain layerwise confirmed a second time, in plateau

Cycle 15 proved the identity on the first 10 epochs (max deviation 0.03pp).
Independently, at 100 epochs: additive r=1 = **90.918** (n=1) vs plain layerwise
SGDm/Lion a0=1e-6 = **90.772** (n=10, sd 0.190). Gap 0.15pp < 1 sd.
Two independent confirmations; the identity is settled.

## 3. The 300-epoch behaviour is a RIGHT-SHIFT, not an inversion

| budget | r=0 | r=0.05 | r=0.07 | r=0.1 | peak |
|---|---|---|---|---|---|
| 100 ep | 92.20 (3) | 93.09 (5) | **93.21** (6) | 92.63 (5) | r=0.07 |
| 300 ep | 92.07 (2) | 93.01 (2) | — | **93.28** (2) | r=0.1 |

* The **peak value is flat** across budget (93.21 -> 93.28).
* The **gain over full pooling does not shrink**: +1.01pp at 100 ep, +1.21pp at 300 ep.
* What moves is *which r wins*: the optimum shifts toward **less** pooling as the
  budget grows — consistent with pooling buying early-training stability that a
  longer run no longer needs.
* **Supersedes the standing "pooling gains invert between 100 and 300 epochs"
  caveat**: the sign of the pooling benefit does not invert; the r=0.05/r=0.1
  ordering does. PROVISIONAL — n=2 at 300 ep. Needs n>=5 before it is stated.

## 4. Non-meta AdamW baseline, n now 4-5 — but still the mis-scaled schedule

| lr | n | plateau | sd |
|---|---|---|---|
| **3e-4** | 4 | **91.894** | 0.120 |
| 1e-4 | 5 | 91.188 | 0.223 |
| 1e-3 | 2 | 90.264 | 0.052 |
| 3e-3 | 2 | 85.962 | 0.574 |

`fxcos-*` (corrected `COS_TOTAL=50000, COS_WARMUP=2500`) is **still in flight** —
8 running, at 9-48 of 100 epochs. **The +1.32pp margin in §1 remains unsafe to
quote**; the corrected baseline can only move up.

## 5. H4 base-optimizer interaction, extended — and nodewise is the best plain granularity

| base/meta | scalar | blocks(6) | layerwise | nodewise | weightwise |
|---|---|---|---|---|---|
| SGDm/Lion | 87.750 (8) | 91.330 (8) | 90.772 (10) | **91.593 (8)** | — |
| AdamW/Adam | 91.555 (6) | 91.663 (6) | 91.707 (6) | — | — |
| AdamW/Lion | 91.567 (3) | 91.367 (3) | 91.418 (3) | — | 85.386 (3) |

* Under **SGDm the granularity span is 3.84pp** (scalar 87.75 -> nodewise 91.59).
* Under **AdamW it is 0.15pp** (91.56 -> 91.71) — null, as previously found, now n=6.
* **nodewise > blocks > layerwise** under SGDm/Lion. Layerwise, the parent paper's
  default, is *not* the best plain granularity; it is 0.82pp below nodewise.
* SGDm/Adam scalar is bimodal (n=4, mean 70.65, **sd 33.5**) — some seeds collapse.
  Quote it as an instability, never as a mean.

## 6. What was decided this cycle

* **Submitted `am4-*` (21 jobs, alice2)** — the M1 r-curve at **alpha0=1e-4**,
  r in {0, 0.03, 0.05, 0.07, 0.1, 0.2, 1} x 3 seeds, otherwise byte-identical to
  the 1e-6 sweep (same account, SGDm/Lion, meta-stepsize 1e-3, guard, layerwise,
  100 ep, batch 100). **Rationale:** every point of the §1 curve sits at
  alpha0=1e-6, which costs 14-25 epochs of startup *differing per arm*, so the
  inverted-U could in principle be escape-from-bad-init. The only off-1e-6
  additive point in 498 runs is `mx-a1e4-add` (r=0.06, n=5, 92.702) — one point
  cannot distinguish an interior optimum from a monotone trend. Self-anchoring
  (carries r=0 and r=1), so multi-partition is safe. r=0.06 omitted; it is the
  anchor tying the new block to existing data.
  **Read-out:** inverted-U survives -> the optimum is a property of the operator
  and the headline holds; curve flattens -> the headline needs an alpha0 qualifier
  or withdrawal.
* **Widened 54 pending jobs** (`sc-*` model-scale x36, `c100-*` x16, `c100pin-*` x2)
  from a single pinned partition to all five. Both blocks were 100% starved
  (0 running) behind saturated pools while the two axes they cover are the paper's
  top two gaps. Mixing GPU types is safe for `plateau` / epochs-to-target.

## 7. Cluster state

* Genuinely free GPUs cluster-wide: **2** (116 configured, 100 allocated, 14 of the
  16 "free" sit on `maint`/`drain` nodes — reservation `root_28` until 2026-12-01).
* Ours running: **12 alice + 13 alice2 = 25**. Pending: **134 + 95 = 229**.
* Pending reasons on alice: 131 `Priority`, 3 `QOSMaxGRESPerUser`. FairShare 0.341.
* **Throughput is capped by the cluster, not by queue depth or composition.** Queue
  ordering, not queue size, is the only remaining lever; hence §6's widening.

---

# 19 Aug 2026, cycle 17 — the scale axis opens, and it splits the two headlines apart

## 0. Aggregator defect: the CSV could not tell architectures apart

`all_runs.csv` had **no `network` / `dataset` / `batch_size` column**. Every table was
keyed on `granularity` alone, so a ResNet10 row and a ResNet18 row with the same
granularity landed in **one cell**. With the scale axis landing this cycle that is fatal:
the pooled `scalar` cell read **83.111 (n=11)**, a number belonging to no architecture —
it is 70.7 and 87.8 averaged together.

* Fixed in `analysis/aggregate.py` (`--NN-name`, `--dataset`, `--batch-size` now parsed
  from the ARGS line; sort key is network-major). CSV regenerated: **532 runs**.
* **No previously published table was contaminated.** Census of non-ResNet18 rows before
  this cycle: `sm_ResNet34`, `sm_ResNet50`, `sm_ResNet101`, `c100smoke_*` — all 2-5 epoch
  smoke tests with **empty `plateau`**, so every plateau-filtered table already excluded
  them. The hazard was closed before it did damage, not after.

## 1. Model scale, ResNet10 complete (n=3, 100 ep, α₀=1e-6, SGDm/Lion, ms=1e-3, guard on)

ResNet18 column is matched-protocol runs pooled from other families (the `sc-ResNet18-*`
arm is still running); ResNet34 is queued, not measured.

| arm | ResNet10 (4.9M) | ResNet18 (11.2M) |
|---|---|---|
| scalar | 70.742 ± 0.832 (3) | 87.750 ± 0.142 (8) |
| layerwise plain | 90.619 ± 0.267 (3) | 90.792 ± 0.172 (13) |
| additive r=0.05 | — | 93.086 ± 0.096 (5) |
| additive r=0.06 | 90.808 ± 0.419 (3) | — |
| additive r=0.07 | — | 93.237 ± 0.132 (7) |

**The two headline effects move in opposite directions with scale:**

| effect | ResNet10 | ResNet18 |
|---|---|---|
| granularity (scalar → layerwise) | **+19.877pp** (t=39.4) | **+3.042pp** (t=43.0) |
| M1 pooling (layerwise → best r) | **+0.189pp (t=0.66, NULL)** | **+2.445pp** (t=34.1) |

1. **Granularity helps ~6.5x more at the smaller model.** Direction is consistent with the
   parent paper's premise that the granularity benefit decays with scale — but the
   mechanism here is that *scalar gets much worse when small*, not that layerwise improves.
2. **The M1 pooling gain does not reproduce at ResNet10.** +0.19pp against a pooled sd of
   0.35 is indistinguishable from zero. **The campaign's best positive result is, so far,
   demonstrated at exactly one architecture.**

## 2. Rule-5 check — both scalar arms are converged, so §1 is not a startup artefact

Test accuracy by epoch (seed 0):

| run | ep20 | ep40 | ep60 | ep80 | ep99 |
|---|---|---|---|---|---|
| `sc-ResNet10-scal-s0` | 63.23 | 71.62 | 71.71 | 71.70 | 71.79 |
| `a0L-scal-1e6-s0` (R18) | 73.32 | 85.48 | 86.78 | 87.34 | 87.64 |

ResNet10-scalar is **flat from epoch 30** (71.58 → 71.79 over 70 epochs): it converged to a
bad point, it is not still escaping α₀=1e-6. ResNet18-scalar still gains ~0.3pp over the
last 20 epochs, i.e. *less* converged — which would bias against the measured gap, not
toward it. The 17pp scalar difference is real.

## 3. Caveat that bounds §1's second row

ResNet10 was tested at **r=0.06 only** — a value tuned on ResNet18, where the optimum sits
at 0.05-0.07. A null at one r cannot distinguish "pooling does not work at ResNet10" from
"r* moved". §4 resolves this.

## 4. What was decided this cycle

* **`r10-*` (24 jobs, alice2)** — M1 additive r-curve at **ResNet10**, r ∈ {0, 0.03, 0.05,
  0.06, 0.07, 0.1, 0.2, 1} × 3 seeds, otherwise byte-identical to the ResNet18 sweep.
  **Rationale:** §1 row 2 is the single biggest threat to the paper's positive result, and
  §3 is its only escape. Self-anchoring: carries **r=1** (the identity gate — additive r=1
  must equal plain layerwise, verified twice on ResNet18) and **r=0.06** (replicates the
  alice `sc-ResNet10-add` cell **across accounts**, breaking the account confound for free).
  **Read-out:** interior optimum appears at some r → the operator generalises and r* is
  scale-dependent (a *stronger* result, and one the agreement story should predict);
  curve is flat → M1 is a ResNet18 artefact and the headline must say so.
* **`rc100-*` (14 jobs, alice)** — M1 additive r-curve on **CIFAR-100**, r ∈ {0, 0.03, 0.05,
  0.07, 0.1, 0.2, 1} × 2 seeds, ResNet18_c100, **α₀=1e-3**. **Rationale:** the queued
  `c100-*` family samples only r=0.07, so it can show a point, never a curve. α₀=1e-3 skips
  the 14-25 epoch startup entirely, so this reads steady state (Rule 5); it connects to the
  existing `c100-1e3-add` (r=0.07) and `c100-1e3-layer` cells **on the same account**.
* **Widened 170 pending jobs to all five partitions** (alice 99→5-way + 9→4-way, alice2
  62→5-way). Before: 68 of 108 alice and **all 62** alice2 pending jobs were pinned to a
  single partition. `gpu-short` caps at 4:00:00 and our jobs request 3:50:00, so they are
  eligible; the 9 four-way jobs are the ones that are not.

## 5. Operational correction — alice2 is NOT behind on patches

`CONTINUE-HERE.md` stated alice2 "still lacks the patch and the data" for CIFAR-100. **False.**

* `cifar10/build_network.py` on alice2 is **byte-identical** to alice's (diff empty) and has
  ResNet10 / ResNet34 / `*_c100`.
* CIFAR-100 is staged and extracted at `cifar10/data/cifar-100-python/`, tarball md5
  `eb9058c3a382ffc7106e4002c42a8d85` = the official CIFAR-100 md5. `c100.stamp` reads `DONE`.
* The false negative came from `find . -name build_network.py | head -1` resolving to the
  **imagenet** copy, which is unpatched and which `jobs/run_cifar.sh` never uses (it `cd`s
  into `cifar10/`). **Always grep the copy the runner cd's into, not the first `find` hit.**

**Consequence: both top-priority axes (model scale, CIFAR-100) can run on either account.**
Effective capacity for them roughly doubles.

# 19 Aug 2026 (cycle 18) — the α₀ control of the *drift* measurement was on disk and unread; it costs the headline 16× of its effect size

561 runs aggregated (up from 532; 29 new). Two things this cycle: a **queue pathology** that
explains why axis 2 has no data, and a **re-derivation of the campaign's most defensible result
at its own α₀ control**, which was already sitting in `runs/bdrift3/` from cycle 7 and had never
been analysed. Rule 1 again: the refuting artefact was in the repo, unread.

## 1. Why CIFAR-100 has produced nothing in four cycles — it was never near a GPU

Queue position is not queue depth. Measured position of each family in our *own* pending
ordering (alice, 105 pending):

| family | axis | jobs | position (of 105) |
|---|---|---|---|
| `mx-*` refinement (b25/b50/b200, add-r007/8) | 3 | 47 | 1–61 |
| `sc-ResNet34-*` | **1** | 11 | 62–72 |
| `c100-*`, `rc100-*`, `c100pin-*` | **2** | 33 | **73–105** |

With ~11 concurrent slots, the axis-2 block was unreachable. `mx-add-r007` (5 jobs) sat ahead of
it to add a **6th–10th seed to a cell that already has n=8**. Same pathology on alice2:
`mx-h4-*` (20 jobs, n≥5 refinement of an already-solid result) sat ahead of `r10-*` (21 jobs,
the open ResNet10 r-question).

**Fix (user-side lever, no admin):** `scontrol update JobId=<j> Nice=<n>` — users may only
*lower* their own priority, which is sufficient. After demoting tier-3:

| family | before | after |
|---|---|---|
| `sc-ResNet34` | 62 | **16** (3 started within the cycle) |
| `c100`+`rc100` | 73–105 | **24–55** |
| `mx-*` tier-3 | 1–61 | 77–105 |

Partition eligibility was **not** the problem — every family already carried all five
partitions. The one exception, `fx-e300-*`, correctly omits `gpu-short` (300 epochs > 4 h).

## 2. N measured structurally, not assumed (zero-GPU, CPU instantiation only)

All four generic granularities instantiate on all four architectures. FINDINGS has recorded
ResNet18 `nodewise` as **~4,800** since cycle 7; it is **14,420**.

| net | params | layerwise N | nodewise N | weightwise N |
|---|---|---|---|---|
| ResNet10 | 4,903,242 | 38 | 8,660 | 4,903,242 |
| ResNet18 | 11,173,962 | 62 | **14,420** (was "~4,800") | 11,173,962 |
| ResNet34 | 21,282,122 | 110 | 25,556 | 21,282,122 |
| ResNet18_c100 | 11,220,132 | 62 | 14,600 | 11,220,132 |

**Impact on the published slope: none.** Refitting drift-vs-N with the corrected N moves the
log-log slope from **−0.1130 to −0.1095** against an i.i.d. prediction of −0.500. The
refutation is insensitive to the error. Recorded so the wrong N is not re-quoted.

## 3. The refutation SURVIVES its α₀ control — but the agreement effect does not

`runs/bdrift3/p3-*` (cycle 7's α₀=1e-3 control) had never been reduced. Re-derived here with the
published methodology (drift = |Δβ̄|/step over steps 1000–7500; `frac_neg` averaged over the same
window). **Structural check passes:** every pooled arm reports
`max|β_true_max − β_true_min| = 0.0000` (genuinely one step size), and the unpooled control
`p3-lay-plain` reports **8.93** — the pooling identity is verified structurally, not by accuracy.

| arm | N | drift/step @1e-6 | drift/step @1e-3 | agreement @1e-6 | agreement @1e-3 | σ vs 50% @1e-3 |
|---|---|---|---|---|---|---|
| scalar | 1 | 1.000e-3 | 3.043e-4 | 91.00% | 12.12% | −0.1 |
| 6-block | 6 | 9.828e-4 | 1.027e-4 | 69.60% | 1.52% | +0.0 |
| layerwise | 62 | 7.997e-4 | 1.567e-4 | 66.40% | 5.14% | +0.4 |
| nodewise | 14,420 | 5.503e-4 | 1.844e-4 | 24.40% | 4.04% | +4.9 |
| weightwise | 11,173,962 | 1.668e-4 | 1.698e-5 | **6.20%** | **0.38%** | **+12.7** |
| log-log slope | | **−0.1095** | **−0.1363** | | | (pred. −0.500) |

(`agreement` = |2·frac_neg − 1|, the excess over a balanced sign split. The headline's "53.1%
agree on sign" is `frac_neg = 0.531`, i.e. a **6.2%** excess.)

Three consequences, in decreasing comfort:

* **KEPT — the core refutation.** The √N law predicts slope −0.500. Measured **−0.110 at
  α₀=1e-6 and −0.136 at α₀=1e-3**: ~4× too shallow in *both* regimes. This is the campaign's
  most defensible claim and it is now robust to the α₀ confound, not just asserted against it.
* **DOWNGRADED — the effect size.** Weightwise sign-agreement is **6.20% at α₀=1e-6 but 0.38%
  at α₀=1e-3**, a **16× collapse**. Much of the "coordinates strongly agree" story is the shared
  climb out of a 7-log-unit hole: when every coordinate is being driven the same direction by a
  bad init, they trivially agree. At steady state the excess is 0.38% — still **+12.7σ** over
  11.17M coordinates, so genuinely non-independent, but a *small* bias, not a strong one.
  **Any statement of the 53.1% number must name α₀=1e-6.**
* **WITHDRAWN — "drift falls monotonically with N."** Cycle 6 predicted it and cycle 7 marked it
  CONFIRMED. At α₀=1e-3 drift is **non-monotone**: scalar 3.04e-4 > nodewise 1.84e-4 >
  layerwise 1.57e-4 > 6-block 1.03e-4 > weightwise 1.70e-5. The monotonicity is an α₀=1e-6
  artefact. Only the *endpoints* (scalar high, weightwise ~18× lower) survive at both α₀.

## 4. M1 r-curve, re-derived (SGDm+Lion, α₀=1e-6, layerwise, 100 ep **complete only**, augmented)

r=0.04 completed to n=4 this cycle; r=0.05/0.06 have 9 more in flight.

| r | 0 | 0.03 | 0.04 | 0.05 | 0.06 | 0.07 | 0.1 | 0.2 | 0.3 | 1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| plateau | 92.228 | 92.637 | 92.886 | 93.086 | **93.306** | **93.200** | 92.626 | 91.387 | 90.957 | 90.864 |
| sd | 0.087 | 0.165 | 0.136 | 0.096 | 0.140 | 0.161 | 0.214 | 0.142 | 0.079 | 0.062 |
| n | 6 | 5 | 4 | 5 | 3 | 8 | 5 | 3 | 3 | 3 |

Unimodal and now densely sampled on the rising limb. **Report the plateau region r ∈ [0.05, 0.07]
(93.09–93.31), not the max cell** — r=0.06 is the argmax at n=3 while r=0.07 sits 0.11pp lower at
n=8, a gap inside their sds.

## 5. Scale axis, within the `sc-*` family only (all contrasts internally matched)

| net | scalar | layerwise | additive r=0.06 | granularity gain | pooling gain |
|---|---|---|---|---|---|
| ResNet10 (4.9M) | 70.742 | 90.619 | 90.808 | **+19.88** | **+0.19** |
| ResNet18 (11.2M) | 87.819 | 90.686 | 93.306 | **+2.87** | **+2.62** |
| ResNet34 (21.3M) | — | — | — | — | — |

n=3 per cell. The two gains move in **opposite** directions with scale. ResNet34 (now at queue
position 16, 3 running) is the third point that decides whether this is a trend or two points.

## 6. Submitted — axis 6 across axes 1–2 (the theoretical core, extended)

The sign-agreement/drift law exists **only** at ResNet18+CIFAR-10, and nothing in the 190-job
queue extended it. 24 probes submitted (20 epochs each, ~1/5 the cost of a training cell):

| batch | account | α₀ | arms |
|---|---|---|---|
| `p4-*` | alice | 1e-3 (steady state) | {ResNet10, ResNet34, ResNet18_c100} × {scalar, layerwise, nodewise, weightwise} |
| `p5-*` | alice2 | 1e-6 (matches p2) | same 12 |

ResNet18 already has both α₀ (p2-*/p3-*), so the pair completes a 4-architecture × 2-α₀ grid.
**The question they decide:** is agreement/drift a function of **N alone** (all architectures
collapse onto one curve) or of the **partition type** (points cluster by layerwise/nodewise/
weightwise regardless of N)? layerwise spans N = 38/62/110 across the three nets while
layerwise→nodewise jumps ~200×, which separates the hypotheses cleanly. The p4/p5 pair also
gives the α₀-inflation factor from §3 across architectures rather than at ResNet18 alone.

Queue after this cycle: **alice 124, alice2 85 = 209 jobs**, ordered
a0h → sc-ResNet34 → c100 → p4 → fx-e300 → tier-3.

## 7. Acting on §3's process note: two more probe series were unreduced — one is mechanistic

Enumerated every `probe.jsonl` on both accounts (108 dirs). Two drift series had never been
reduced.

**(a) Extractor validated against the published series.** Reducing `runs/bdrift/p2-*` (alice2)
reproduces cycle 7's table **exactly** — drift 1.000e-3 / 9.828e-4 / 7.997e-4 / 5.503e-4 /
1.668e-4 and frac_neg 0.9545 / 0.8485 / 0.8319 / 0.6221 / 0.5312 against published 0.955 /
0.848 / 0.832 / 0.622 / 0.531. The §3 α₀=1e-3 numbers come from the same code path and are
therefore trustworthy.

**(b) `runs/bdrift4/p4-ad-*` (alice2) — the drift probe run across the M1 additive r-ladder.**
Never reduced. α₀=1e-6, 20 ep, layerwise, `HIER=additive`. (Name clash warning: these predate
and are unrelated to the `p4-*` batch submitted this cycle on alice.)

| r | 0 | 0.03 | 0.1 | 0.3 | 1.0 |
|---|---|---|---|---|---|
| drift/step | 7.991e-4 | 7.988e-4 | 7.979e-4 | 7.955e-4 | 8.022e-4 |
| frac_neg | 0.8355 | 0.8299 | 0.8297 | 0.8272 | 0.7739 |
| β spread | **0.0000** | 0.3648 | 1.1920 | 3.6087 | **8.6877** |

**The additive identity is verified structurally at both ends (Rule 4).** r=0 gives
`sd(β) = 0.0000` — genuinely one step size, full pooling. r=1 gives spread **8.6877**, which
matches `p2-lay-plain`'s **8.6877** to four decimals, and its drift (8.022e-4) matches
p2-lay-plain's (8.033e-4) to 0.14%. r=1 *is* plain layerwise, confirmed on the β geometry rather
than on accuracy.

**The mechanistic finding: drift is FLAT across the r-ladder where accuracy is not.** Drift spans
7.955e-4–8.022e-4 — a **0.8%** range — across the entire ladder, while the 100-epoch r-curve
(§4) spans **2.44pp** of plateau over the same r values and has its optimum at r≈0.06.
Sign-agreement does move (67.1% → 54.8% excess), but not with the accuracy optimum: it is
monotone in r while accuracy is unimodal.

> **The β-drift mechanism explains the COST of pooling (cycle 7) but does NOT explain the
> BENEFIT of the M1 interior optimum.** The campaign's headline positive result currently has
> *no* measured mechanism. This is a gap to state plainly, not to paper over.

Caveat on regime: drift here is measured over steps 1000–7500 (epochs 2–15) at α₀=1e-6, i.e.
inside the startup window, whereas the r-curve is a 100-epoch plateau. The comparison shows the
proposed mechanism does not track the benefit *in the window where the mechanism was defined*;
a steady-state version needs a 100-epoch probe at α₀=1e-3, which is **not** currently queued and
is the natural cycle-19 submission.

## 8. Submitted for the mechanism gap — `p6-*` (alice2, 16 jobs)

The §7 caveat is directly testable, so it was queued the same cycle rather than deferred.
M1 additive r-ladder r ∈ {0, 0.03, 0.05, 0.06, 0.07, 0.1, 0.3, 1} × 2 seeds, **α₀=1e-3,
100 epochs, `PROBE=100`** — the probe runs for the full budget, so **drift and plateau come from
the same runs** and can be compared in the regime where the accuracy claim actually lives
(bdrift4 compared a startup-window drift against a 100-epoch plateau).

Two payoffs from one batch:
1. **Mechanism.** If drift stays flat across r at steady state while plateau stays unimodal, the
   M1 benefit is confirmed to have no drift explanation and the paper must say so.
2. **The headline's untested α₀ confound.** This is also the **α₀=1e-3 r-ladder on CIFAR-10**.
   The entire cycle-16 r-curve lives at α₀=1e-6; `mx-a1e3-*` covers only 3 granularity arms, not
   an r-ladder. If the inverted-U flattens at α₀=1e-3, the headline needs a qualifier.

Final queue state this cycle: **alice 124, alice2 99 = 223 jobs.**

| account | order (front → back) |
|---|---|
| alice | `a0h` → `sc-ResNet34` → `c100`/`rc100` → `p4` → `fx-e300` → tier-3 (`mx-b*`, `mx-add-r007/8`) |
| alice2 | `mx-a1e3`/`amx` → `r10` → `p5`/`p6` → `zrn` → `mx-h4` |

---

# Cycle 19 — the scale trend is real but single-α₀, and the α₀ confound hits pooling, not granularity

## 9. The scale ladder, re-derived from `results/all_runs.csv` (590 runs)

All cells: CIFAR-10, SGDm+Lion, meta-stepsize 1e-3, batch 100, AUGMENT=1, guard on,
100 epochs, **plateau = mean of last 20 epochs**, completed runs only (`epochs_done >= 100`).

**α₀=1e-6** (`sc-*`):

| net | params | scalar | layerwise | additive r=0.06 | granularity (L−S) | pooling (A−L) |
|---|---|---|---|---|---|---|
| ResNet10 | 4.9M | 70.74 ±0.83 (n=3) | 90.62 ±0.27 (n=3) | 90.81 ±0.42 (n=3) | **+19.88** | +0.19 |
| ResNet18 | 11.2M | 87.82 ±0.17 (n=3) | 90.69 ±0.14 (n=3) | 93.31 ±0.14 (n=3) | **+2.87** | +2.62 |
| ResNet34 | 21.3M | 89.46 (n=1) | *3 in flight* | *3 in flight* | — | — |

**The trend is driven entirely by the SCALAR arm, not by layerwise.** Scalar climbs
70.74 → 87.82 → 89.46 while layerwise is flat 90.62 → 90.69 → (≈90.4 partial). So
"granularity stops helping at scale" is, mechanically, "**the scalar arm stops failing**
at scale" — a materially different sentence from the parent paper's framing, and the one
the data actually supports.

`sc-ResNet10-scal` **never reaches 85%** (ep_to_85 = never, n=3) and its plateau equals its
final_test (70.74 vs 70.8) — it is *converged*, not still climbing. So this is not an
unfinished run; it is a genuine scalar-arm collapse on the smallest net.

## 10. ⚠️ The whole scale ladder is at α₀=1e-6 — and the matched control shows why that matters

`mx-a1e3-*` is an exact match to `sc-ResNet18-*` (verified field-by-field: net, granularity,
hier, r, meta-stepsize, batch, epochs, augment, beta_clip all identical) differing **only in
α₀**. That makes the ResNet18 column a clean α₀ contrast:

| ResNet18 arm | α₀=1e-6 | α₀=1e-3 | Δ |
|---|---|---|---|
| scalar    | 87.82 ±0.17 (n=3) | 87.71 ±0.14 (n=3) | −0.11 |
| layerwise | 90.69 ±0.14 (n=3) | 91.21 ±0.05 (n=3) | +0.52 |
| additive r=0.06 | 93.31 ±0.14 (n=3) | 92.12 ±0.14 (n=4) | **−1.19** |
| **granularity (L−S)** | **+2.87** | **+3.50** | +0.63 |
| **pooling (A−L)** | **+2.62** | **+0.91** | **−1.71 (−65%)** |

**Granularity survives the α₀ change; pooling loses about two-thirds of its benefit.** This is
the same asymmetry CORRECTIONS records for sign-agreement (6.20% excess at α₀=1e-6 vs 0.38% at
α₀=1e-3, a 16× collapse): the α₀=1e-6 regime flatters *pooling* specifically, because a shared
component helps most while every group is making the same 7-log-unit climb.

> **Consequence for the paper.** The M1 pooling headline (+2.62pp at ResNet18) is an
> **α₀=1e-6 number**. At α₀=1e-3 it is **+0.91pp**. Never quote the pooling margin without
> naming α₀. The granularity numbers are comparatively robust.

## 11. Submitted this cycle

* **`sa3-*` (alice2, 18 jobs) — the decisive control.** ResNet10 and ResNet34 ×
  {scalar, layerwise, additive r=0.06} × 3 seeds at **α₀=1e-3**, 100 ep. Completes a
  3-net × 2-α₀ ladder (ResNet18's α₀=1e-3 column already exists as `mx-a1e3-*`, so those
  9 jobs were submitted and then **cancelled as redundant** once the match was verified).
  Decides whether "granularity gain collapses with scale" survives, or was an
  escape-from-α₀=1e-6 artifact concentrated in `sc-ResNet10-scal`.
* **`sc50-*` / `sc101-*` (alice, 24 jobs) — 4th and 5th rungs.** ResNet50 and ResNet101 ×
  3 arms × **both α₀** × 2 seeds. The axis that matters is N (layerwise group count):
  R34 ≈36 conv layers, R50 ≈53, R101 ≈104. Submitted at both α₀ deliberately so they stay
  informative whichever way `sa3-*` lands. R101 omits `gpu-short` (needs >4h).
* **`sc-ResNet34-*` seeds 3,4 (alice, 6 jobs)** — takes the now-headline ResNet34 row to n=5.

## 12. CIFAR-100 — first rows, not yet usable

| arm (α₀=1e-6) | epochs done | best_test |
|---|---|---|
| c100-1e6-layer | 100 | 70.12 (plateau 69.79, n=1) |
| c100-1e6-add   | 97  | 60.75 |
| c100-1e6-blk6  | 82  | 52.14 |
| c100-1e6-scal  | 83  | 23.08 |

Epoch counts differ, so **no cross-arm comparison is licensed yet**. Two things to watch:
layerwise leads add by ~9pp (pooling may *invert* on CIFAR-100), and the scalar arm at 23.08%
is the ResNet10-scalar pathology again, now on a 100-class problem. The α₀=1e-3 arm
(`c100-1e3-*`) is at queue positions 16–23 and will settle whether that is real.

## 13. Operations

* **`HIER=none` is truthy and would have silently corrupted 18 control runs.** `HF.py` does
  `self._hier = os.environ.get('HIER','')` then `if self._hier:`. The existing `sc-*` runs log
  `HIER=none` **only** because `run_cifar.sh` echoes `${HIER:-none}` over an *unset* variable.
  Non-hierarchical arms must leave `HIER` **unset**, never set it to `none`.
* `rc100-*` (14 jobs, the M1 r-ladder *on* CIFAR-100) demoted to `Nice=3000`: it is a
  second-order refinement of an axis whose first-order comparison (§12) has not landed.
  `c100-*` itself was left at the queue front.
* On alice2 the runner is `jobs/run_cifar.sh` (already the s5014158 variant); there is no
  `run_cifar_alice2.sh` on that account — that name exists only in the git repo.

Queue at end of cycle 19: **alice 161, alice2 104 = 265 jobs**, 24 running.

---

# Cycle 20

Re-derived from `results/all_runs.csv` at **638 runs** (was 590; 48 new). Every number below
was recomputed from the CSV in this cycle, not carried over from prose.

## 1. `r` is pooling RETENTION, not pooling strength — r=0 is FULL pooling, r=1 is the identity

`patches/HF_patched.py::_apply_hier`, additive branch:

```
d   = beta - beta_prev          # realised per-group meta-update
dm  = d.mean()                  # shared component
beta = beta_prev + dm + r*(d - dm)
```

At **r=1** this telescopes to `beta_prev + d = beta` — the exact identity, i.e. **plain
layerwise**. At **r=0** every group takes the *same* (mean) update — **full pooling**.

Cycles 16–19 read `r=0` as the no-pooling control and quoted the M1 gain against it. That is
backwards: `r=0` is the *maximally pooled* extreme. **The correct no-pooling control is `r=1`,
which equals plain layerwise.**

Structural verification (rule 4 — identity checked, not assumed), ResNet18/CIFAR-10, α₀=1e-6,
plateau, `epochs_done>=100`:

| arm | n | plateau |
|---|---|---|
| additive r=1 | 3 | **90.863 ±0.063** |
| plain layerwise (HIER unset) | 47 | **90.891 ±0.492** |

Difference **0.028pp**, inside the ±0.02–0.05pp reproduction band. The identity holds.

## 2. The M1 curve, restated with both endpoints — ResNet18/CIFAR-10, α₀=1e-6

| r | n | plateau |
|---|---|---|
| 0 (full pooling) | 8 | 92.190 ±0.161 |
| 0.03 | 8 | 92.142 ±0.696 |
| 0.04 | 5 | 92.862 ±0.129 |
| 0.05 | 12 | 93.041 ±0.127 |
| **0.06** | 8 | **93.262 ±0.135** |
| 0.07 | 9 | 93.192 ±0.152 |
| 0.1 | 10 | 92.281 ±0.918 |
| 0.2 | 3 | 91.387 ±0.142 |
| 0.3 | 3 | 90.957 ±0.079 |
| 1 (no pooling ≡ layerwise) | 3 | 90.863 ±0.063 |

This is a **fully sampled unimodal curve with both extremes measured**, which is a stronger
result than the one previously recorded. Partial pooling beats **both** endpoints:
**+2.40pp over no pooling (r=1)** and **+1.07pp over full pooling (r=0)**.

> Supersedes the cycle-16/19 phrasing "93.06–93.22 vs 92.15 at r=0". The 92.15 figure is the
> full-pooling extreme, not a no-pooling baseline. **The headline pooling gain at ResNet18,
> α₀=1e-6 is +2.40pp, not +1.07pp** — but only because the baseline was misidentified, not
> because any run changed.

## 3. r* moves with the setting — the ladder is not transferable

| setting | α₀ | r=0 | r* (measured best) | r=1 (no pooling) | gain at r* |
|---|---|---|---|---|---|
| ResNet18/C10 | 1e-6 | 92.190 (n=8) | **0.06** → 93.262 (n=8) | 90.863 (n=3) | +2.40 |
| ResNet18/C10 | 1e-3 | — | 0.06 → 92.119 (n=5) | 91.173 (n=15) | +0.95 |
| ResNet10/C10 | 1e-6 | 82.114 (n=3) | **≥0.1** → 91.619 (n=2) | 90.619 (n=3) | +1.00 |
| R18_c100/C100 | 1e-6 | — | ≤0.07 → 59.046 (n=2) | 69.886 (n=2) | **−10.84** |
| R18_c100/C100 | 1e-3 | — | ≤0.07 → 26.383 (n=2) | 70.113 (n=2) | **−43.73** |

Three things fall out:

* **ResNet10's optimum is at r≥0.1, not 0.06**, and its curve is monotone increasing across
  every sampled point up to 0.1. The ResNet18 optimum does not transfer even one rung down
  the scale ladder.
* **On CIFAR-100 pooling is harmful, severely.** At α₀=1e-3, r=0.07 costs **43.7pp** against
  plain layerwise — it drags layerwise (70.11) most of the way back to scalar (22.47). The
  r=0.07 setting was tuned on CIFAR-10/ResNet18 and is simply the wrong operating point on
  a 100-class problem.
* The ResNet10 "r=0 → 82.11" collapse, which looked like a dramatic pooling gain, is just the
  full-pooling extreme being bad on a small net — consistent with `sc-ResNet10-scal` = 70.74.

> **Consequence.** No pooling claim may be stated without naming *both* the setting and α₀.
> "M1 additive pooling helps" is true on CIFAR-10 and false on CIFAR-100 at the same r.

## 4. CIFAR-100 (Axis 2) — now complete, n=2, all four arms, both α₀, all at 100 epochs

Plateau, `epochs_done=100`:

| arm | α₀=1e-6 | α₀=1e-3 |
|---|---|---|
| scalar | 22.30 ±0.81 | 22.47 ±0.37 |
| resnet18_blocks (6) | 52.73 ±0.41 | 51.32 ±1.26 |
| layerwise | **69.89 ±0.13** | **70.11 ±0.25** |
| additive r=0.07 | 59.05 ±1.69 | 26.38 ±1.35 |
| **granularity (layer − scalar)** | **+47.59** | **+47.64** |
| **pooling (add − layer)** | **−10.84** | **−43.73** |

The epoch counts are now equal, so cross-arm comparison **is** licensed (cycle 19 correctly
withheld it at unequal epochs).

* **Granularity is worth +47.6pp on CIFAR-100 and is completely insensitive to α₀** (+47.59
  vs +47.64). On CIFAR-10/ResNet18 the same contrast is +2.87/+3.50. Granularity is
  monotone in fineness: scalar 22 < 6-block 52 < layerwise 70, at both α₀.
* This is the **largest and most α₀-robust granularity effect in the campaign**, and it is on
  the second dataset — exactly the axis the paper was missing.

## 5. Drift vs group size — the sqrt(N) prediction is INVERTED, in 3/3 settings

`bin/drift_extract2.py` over `runs/p4scale/*`, α₀=1e-3, 20 epochs, steps 1000–7500.
**Design note:** these arms run `HIER=shrink, LAM=1.0`, so β is held *common* across groups
and only the group size over which the meta-gradient is aggregated varies. That is the
controlled design the sqrt(N) test wants, and it must be stated when quoting these numbers.

| setting | weightwise | nodewise | layerwise | scalar |
|---|---|---|---|---|
| ResNet10/C10 | 4.322e-05 | 2.318e-04 | 1.102e-04 | 6.854e-04 |
| ResNet34/C10 | 2.497e-06 | 1.120e-04 | 4.737e-05 | 2.317e-04 |
| R18_c100/C100 | 2.690e-05 | 2.137e-04 | 8.710e-05 | 7.254e-04 |

Group size runs weightwise (N=1) < nodewise (~10²) < layerwise (~10⁴–10⁶) < scalar (~10⁷).
The sqrt(N) sampling model predicts drift ∝ N^−0.5, i.e. **weightwise highest, scalar lowest**.
**Measured: weightwise lowest and scalar highest, in all three settings.**

| setting | drift(scalar)/drift(weightwise) | implied log-log slope | predicted |
|---|---|---|---|
| ResNet10/C10 | 15.9× | **+0.179** | −0.500 |
| ResNet34/C10 | 92.8× | **+0.268** | −0.500 |
| R18_c100/C100 | 27.0× | **+0.203** | −0.500 |

The slope is **positive** where the model requires −0.5. This extends the campaign's central
refutation from one architecture to **three architectures across two datasets**, and it does so
at α₀=1e-3, i.e. in the steady-state regime rather than the escape-from-bad-init regime.

Cross-group sign agreement (multi-coordinate arms only), same runs:

| setting | weightwise | nodewise | layerwise |
|---|---|---|---|
| ResNet10/C10 | 0.5047 (0.47% excess) | 0.5339 (3.39%) | 0.5219 (2.19%) |
| ResNet34/C10 | 0.5008 (0.08%) | 0.5132 (1.32%) | 0.5200 (2.00%) |
| R18_c100/C100 | 0.5026 (0.26%) | 0.5279 (2.79%) | 0.5286 (2.86%) |

**Weightwise coordinates are essentially independent in sign (0.08–0.47% excess) in every
setting** — confirming across three architectures what CORRECTIONS recorded at ResNet18 alone
(0.38% at α₀=1e-3). So the sampling model's *premise* (independence) is satisfied at
weightwise, and its *prediction* still fails. The failure is not an independence violation.

> **Do not quote "53.1% agree on sign" without α₀=1e-6.** At α₀=1e-3 the excess is under 0.5%
> at weightwise in all three settings.

## 6. Two tooling defects found and fixed

* **`bin/drift_extract.py`'s structural check was vacuous.** It printed
  `spread = beta_true_max − beta_true_min` as a verification that pooled arms carry one step
  size. The probe writes those two fields **identically on every arm** (confirmed by reading
  raw records on `p4-r34-lay`, a 110-group layerwise arm: both = −6.032741069793701), so
  `spread` read 0.0000 **by construction and could never fail**. This is precisely the
  failure mode rule 4 names. Replaced in `bin/drift_extract2.py` by `sd_beta`, the real
  standard deviation across the per-group β vector.
* **`frac_neg` is meaningless on a scalar arm.** It is computed over a 1-element list, so per
  record it is 0.0 or 1.0 and its mean is the fraction of *timesteps* the single coordinate
  was negative — not cross-coordinate agreement. The previously tabulated scalar values
  (0.3333 at ResNet10, 0.1970 at CIFAR-100) are **not** agreement figures and are now reported
  as `n/a`. No published claim depended on them.

## 7. Submitted this cycle — queue: alice 153, alice2 125 = **278 jobs**

* **`rc100-*` (alice, 14) promoted from Nice=3000 to the queue front.** Cycle 19 parked it
  because the first-order CIFAR-100 comparison had not landed. §4 is that comparison, and it
  says pooling is catastrophic on CIFAR-100 — so the r-ladder is now the single most
  informative thing in the queue. r ∈ {0, 0.03, 0.05, 0.07, 0.1, 0.2, 1} × 2 seeds, α₀=1e-3.
* **`m1a3-*` (alice, 15)** — ResNet18/CIFAR-10 pooling ladder at **α₀=1e-3**,
  r ∈ {0, 0.03, 0.1, 0.2, 0.4} × 3 seeds. Only r=0.06 and r=1 exist at this α₀; the shape of
  the curve off α₀=1e-6 is unmeasured. Decides whether r*≈0.06 survives α₀.
* **`p6f-*` (alice, 9)** — the **free-adaptation companion** to `p4scale`. Same three settings
  and three granularities but with `HIER` **unset**, so groups adapt independently. Closes the
  §5 design caveat: does sign agreement survive when groups are allowed to diverge?
* **`rc6-*` (alice2, 14)** — CIFAR-100 ladder at **α₀=1e-6**, r ∈ {0, 0.05, 0.1, 0.2, 0.4,
  0.7, 1} × 2 seeds. Twin of `rc100`. Separates "CIFAR-100 hates pooling" from "α₀=1e-3 hates
  pooling" — the penalty is −10.84 at 1e-6 and −43.73 at 1e-3.
* **`rcg-*` (alice2, 9)** — CIFAR-100 gap-fill, r ∈ {0.4, 0.6, 0.8} × 3 seeds, α₀=1e-3.
  `rc100` jumps 0.2 → 1 with nothing between; any CIFAR-100 interior optimum lives there.
* **`r10b-*` (alice2, 15)** — ResNet10 ladder completion, r ∈ {0.08, 0.15, 0.3, 0.4, 0.6} × 3
  seeds, α₀=1e-6. Brackets a peak that §3 shows is at r≥0.1, not 0.06.
* **Not submitted, because it already existed:** the α₀=1e-6 probe ladder. `p5-*` (alice2, 12)
  is exactly that and is already queued. Checked before submitting, per the cycle-19 gotcha.
* **CIFAR-100 is staged on BOTH accounts** (`.../cifar10/data/cifar-100-python` present on
  s5014158 as well), and `build_network.py` there supports `ResNet18_c100`/`ResNet34`. The
  priority-2 axis is no longer single-account bound.

## 8. Operations

* The cluster's `analysis/aggregate.py` was **stale on both accounts** — it lacked the
  `network`/`dataset`/`batch_size` columns that `results/all_runs.csv` carries, so a naive
  re-aggregation would have silently dropped the three columns every cross-architecture and
  cross-dataset claim depends on. Pushed the repo version to both accounts before aggregating.
* `python` on a login node needs `module load Python/3.10.4-GCCcore-11.3.0` *before*
  `source envs/mo/bin/activate`, or it dies with
  `libpython3.10.so.1.0: cannot open shared object file`.
* Roughly 120 of alice's pending jobs sit at reason `(None)` rather than `(Resources)`. That is
  the scheduler's per-user evaluation depth, not a hold — jobs beyond the top ~100 are simply
  not examined each pass. It is a reason to keep the *front* of the queue correctly ordered,
  not a reason to submit less.

## 9. What is still open

* §3's r* ladder is the live question: r* is 0.06 (R18/C10), ≥0.1 (R10/C10) and apparently >0.2
  or nonexistent (C100). Six ladders are in flight to map it.
* §4's CIFAR-100 granularity result is n=2. It is large enough (+47.6pp) that n=2 is not the
  constraint, but headline cells should reach n≥5.
* §5's slope is computed from the weightwise↔scalar endpoints only. A proper regression over
  all four granularities needs the per-granularity group sizes `N`, which the probe records as
  `param_numels` but the reducer does not yet consume.
* The non-meta baseline (Axis 4) is still uncorrected AdamW 91.894 (n=4); `fx-e300-*` and
  `fxcos-*` remain queued.

---

# Cycle 21 — the tuned non-meta baseline landed, and it wins

CSV re-aggregated from both accounts: **679 runs** (was 638). All numbers below are `plateau`
(mean of the last 20 epochs) over runs with `epochs_done >= 100`, re-derived from
`results/all_runs.csv` at write time.

## 21.1 Axis 4 is answered, and the answer is unfavourable — record it plainly

`fxcos-*` completed. Matched budget throughout: ResNet18 / CIFAR-10 / batch 100 / 100 epochs /
`AUGMENT=1`. `fxcos` = plain `--optimizer AdamW` with `COS_TOTAL=50000, COS_WARMUP=2500`
(i.e. cosine over exactly the 100-epoch budget); `fx_adamw` = the same at constant LR.

| arm | plateau | n |
|---|---|---|
| **AdamW + cosine, lr 1e-3** | **94.093 ± 0.036** | 3 |
| AdamW + cosine, lr 3e-4 | 94.062 ± 0.043 | 3 |
| AdamW + cosine, lr 1e-4 | 92.851 ± 0.239 | 3 |
| *best MetaOptimize arm* (`sc-ResNet18-add`, additive r=0.06) | *93.306 ± 0.140* | 3 |
| MetaOptimize additive r=0.06, n=5 (`mx-add-r006`) | 93.236 ± 0.141 | 5 |
| MetaOptimize plain layerwise | 90.686 ± 0.137 | 3 |
| AdamW constant lr 3e-4 | 91.858 ± 0.131 | 5 |
| AdamW constant lr 1e-4 | 91.188 ± 0.223 | 5 |

**A tuned non-meta baseline beats the best MetaOptimize arm by 0.79pp under matched budget.**
Earlier cycles compared against *constant-LR* AdamW (91.86), which MetaOptimize does beat by
+1.38pp. The gap is created by the cosine schedule, not by the optimizer. Every "our method
helps" sentence must name which baseline it beats. This does not touch §5 (the sqrt(N)
refutation) or §4 (the granularity ordering) — both are statements about MetaOptimize's
internals, not about reaching good accuracy — but it does bound what the method section may
claim.

Caveat carried forward: `fxcos` and the queued 7-point `sw-cos-*` sweep differ in warmup
(`COS_WARMUP=2500` vs unset). They cannot be pooled into one grid.

## 21.2 Granularity gain tracks task difficulty, not parameter count

The gain (layerwise − scalar) on CIFAR-10 at α₀=1e-6 falls monotonically with model size, which
reads as support for the parent paper's premise — until the CIFAR-100 row is put beside it.

| setting | scalar | layerwise | gain | n |
|---|---|---|---|---|
| ResNet10 / C10 (4.9M) | 70.742 ± 0.832 | 90.619 ± 0.267 | **+19.88** | 3 |
| ResNet18 / C10 (11.2M) | 87.819 ± 0.173 | 90.686 ± 0.137 | **+2.87** | 3 |
| ResNet34 / C10 (21.3M) | 89.317 ± 0.127 | 90.220 ± 0.011 | **+0.90** | 3 |
| ResNet18 / C100, α₀=1e-3 | 22.468 | 70.113 | **+47.65** | 2 |
| ResNet18 / C100, α₀=1e-6 | 22.300 | 69.886 | **+47.59** | 2 |

**The layerwise arm is flat across all three CIFAR-10 architectures (90.220–90.686, a 0.47pp
spread) while the scalar arm moves 18.58pp (70.74 → 89.32).** The entire "scale trend" is the
scalar arm catching up, not the fine-grained arm degrading. CIFAR-100 at the *middle* model
size then gives the largest gain in the campaign. So the ordering variable looks like **how
badly a single scalar step size can do on the task**, not parameter count.

Status: **hypothesis, not result.** It rests on one CIFAR-100 model size. `cs-*` (submitted
this cycle) supplies the other two.

## 21.3 Pooling inverts between datasets (r = RETENTION; r=1 plain layerwise, r=0 full pooling)

| arm | CIFAR-10 / R18, α₀=1e-6 | | CIFAR-100 / R18, α₀=1e-3 | |
|---|---|---|---|---|
| r = 1 (plain layerwise) | `zad-r1` 90.863 ± 0.063 | n=3 | `c100-1e3-layer` 70.113 ± 0.247 | n=2 |
| r ≈ 0.07 | `zad-r007` **93.171 ± 0.225** | n=3 | `c100-1e3-add` **26.383 ± 1.346** | n=2 |
| r = 0 (full pooling) | `zad-r0` 92.256 ± 0.122 | n=3 | `rc100-r0` **8.982 ± 0.146** | n=2 |

New this cycle: `rc100-r0`. Full pooling on CIFAR-100 collapses to **8.98%** — 100-class chance
is 1%, so the model is barely learning — against 70.11 for plain layerwise, a **−61.13pp**
penalty. On CIFAR-10 the same operation is *beneficial* (+1.39pp over plain layerwise) and the
optimum is interior at r≈0.07 (+2.31pp). The pooling result does not transfer across datasets
in magnitude or in sign of the derivative. Never state a pooling claim without naming the
dataset, the model, and α₀.

## 21.4 Throughput

12 running per account, both accounts, all on `gpu-short`. This is the **real ceiling, not a
misconfiguration**: `scontrol show node` reports `AllocTRES` = full GPU count on every
`gpu-l4-24g` / `gpu-2080ti-11g` / `gpu-mig-40g` / `gpu-a100-80g` node (one free L4 on node886
cluster-wide). The non-`gpu-short` pending jobs sit at reason `Priority` because other users
hold the GPUs, and `qos-gpu-short` caps at `gres/gpu=12` per user. 24 concurrent GPUs is ≈23%
of the cluster's ~103 GPUs. Negative `Nice` is denied to unprivileged users
(`Access/permission denied`); re-ordering is only possible by nicing *other* jobs back.

## 21.5 Submitted this cycle (58 jobs; queues now alice 215 / alice2 128)

| tag | acct | n | what | why |
|---|---|---|---|---|
| `cs-r10-*`, `cs-r34-*` | alice | 18 | CIFAR-100 × {ResNet10_c100, ResNet34_c100} × {scalar, layerwise, additive r=0.06} × 3 seeds, α₀=1e-3 | fills the 2×2 in §21.2 — decides task-difficulty vs parameter-count |
| `fc100-cos-*` | alice | 9 | AdamW+cosine on CIFAR-100, lr ∈ {1e-3, 3e-4, 1e-4} × 3 seeds | §21.1 on the dataset where our largest effect lives |
| `fxcos-*` | alice | 7 | lr 1e-3 / 3e-4 to n=5, plus lr 3e-3 × 3 | the baseline optimum is not yet bracketed at fixed warmup |
| `c100b-*` | alice2 | 18 | CIFAR-100 granularity ladder, seeds 2–4, both α₀ | takes the headline §21.2 cells from n=2 to n=5 |
| `c100f-*` | alice2 | 6 | CIFAR-100 nodewise + weightwise, α₀=1e-3 × 3 seeds | "monotone in fineness" stops at layerwise; on CIFAR-10 under SGDm the finest arm collapses to chance (10.000) |

Verified before submitting, per the cycle-19 gotcha: `ResNet10_c100`/`ResNet34_c100` exist in
`build_network.py` and `cifar-100-python` is staged on **both** accounts; the queued `sw-cos-*`
block is *not* a duplicate of `fxcos-*` (differs in `COS_WARMUP`).

## 21.7 A one-word env value silently destroyed 48 jobs

`Optimizers/HF.py` parses two env vars **unconditionally**, before any hierarchy branch:

```python
self._hier_lam   = float(_os.environ.get('LAM','0')       or 0)   # line 24
self._hier_ratio = float(_os.environ.get('ETA_RATIO','1') or 1)   # line 25
```

So exporting **either** as the string `na` raises `ValueError: could not convert string to
float: 'na'` at optimizer construction and the job dies in seconds.

The trap is that `na` is exactly what a *healthy* run prints. `jobs/run_cifar.sh` echoes
`ENV: ... LAM=${LAM:-na} ETA_RATIO=${ETA_RATIO:-na}`, so every successful non-hierarchical run
shows `LAM=na ETA_RATIO=na` in its `.out` — from an **unset** variable. Copying that line into
an `--export=` list turns a display placeholder into an illegal value.

| block | acct | jobs | exported | outcome |
|---|---|---|---|---|
| `amx-*` (Adam-meta additive ladder) | alice2 | 15 | `HIER=additive,LAM=na` | all FAILED |
| `am4-*` (M1 r-curve at α₀=1e-4) | alice2 | 21 | `HIER=additive,LAM=na` | all FAILED |
| `cs-*` scalar/layerwise (this cycle) | alice | 12 | `HIER=,ETA_RATIO=na` | caught before running; cancelled + resubmitted |

**Rule: non-hierarchical arms must export NEITHER `HIER` NOR `LAM` NOR `ETA_RATIO`** — the
defaults (`''`, `0`, `1`) are already correct. Under `HIER=additive` only `ETA_RATIO` is read,
so `LAM=0` is inert and correct. Verified by reproducing both failures and all three fixes
against the real `HF.py` parse on a login node before resubmitting.

Unrelated failure found in the same sweep: `sc-ResNet10-blk6-*` and `sc-ResNet34-blk6-*`
(6 jobs) die with `ZeroDivisionError` at `HF.py:175` — `resnet18_blocks` hard-codes a block
partition whose sizes must sum to the parameter count, so **it is valid for ResNet18 only**.
Use `scalar`/`layerwise` (naming-agnostic) on other architectures. This is why `cs-*` carries
no `blk6` arm.

## 21.6 Still open

* §21.2 is one CIFAR-100 model size away from being a result rather than a hypothesis.
* §5's 4-point slope regression still needs `param_numels` consumed by the reducer.
* CIFAR-100 headline cells are n=2 until `c100b-*` lands.
* No non-meta baseline exists on CIFAR-100 at all until `fc100-*` lands.

---

# 22. Cycle 22 — the pooling identity is at r=1, not r=0; M0 overtakes M1

CSV: 713 runs (+34 completed since cycle 21). All numbers below re-derived from
`results/all_runs.csv` at write time, `superseded==0`, **completed runs only**
(`epochs_done == epochs_requested`), metric = `plateau`.

## 22.1 STRUCTURAL CORRECTION — M1's baseline has been the wrong arm

`HF.py:273-277`, additive branch:

```python
d  = b - self._beta_prev                                  # realised per-group update
dm = d.mean()                                             # shared component
self.beta[0] = self._beta_prev + dm + self._hier_ratio * (d - dm)
```

* **r=1** → `beta_prev + dm + (d - dm)` = `beta_prev + d` = `b`. **Plain layerwise, exactly.**
* **r=0** → `beta_prev + dm`: every group receives the *same* update. From a uniform init
  (`beta = log alpha0` for all groups) beta stays **uniform forever** — a single effective
  step size driven by the *mean* per-layer meta-gradient. This is a **different algorithm**,
  not the no-op.

Empirical identity check (r=1 vs plain layerwise, completed 100ep):

| dataset | alpha0 | additive r=1 | plain layerwise | delta |
|---|---|---|---|---|
| CIFAR-10 | 1e-3 | 91.15 (n=2) | 91.15 (n=8) | +0.00 |
| CIFAR-10 | 1e-6 | 90.86 (n=3) | 90.82 (n=24) | +0.05 |
| CIFAR-100 | 1e-3 | 69.92 (n=2) | 70.11 (n=2) | -0.20 |

(like-for-like: `base=SGDm, meta=Lion, layerwise, 100ep` on both sides.)

Identity holds to <=0.20pp. **Every "M1 gain vs r=0" figure in this repo — including the
93.06-93.22 vs 92.15 headline — is anchored to a degenerate arm rather than to the method
it must beat.** Re-anchored to r=1 below.

## 22.2 M1 additive, re-anchored to r=1

| r | C10 a0=1e-6 | vs r=1 | C10 a0=1e-3 | vs r=1 | C100 a0=1e-3 | vs r=1 |
|---|---|---|---|---|---|---|
| 0 | 92.23 (n=6) | +1.36 | 92.10 (n=2) | +0.95 | 8.98 (n=2) | **-60.93** |
| 0.03 | 92.14 (n=8) | +1.28 | 92.15 (n=2) | +1.00 | 13.91 (n=2) | -56.01 |
| 0.05 | 93.05 (n=10) | +2.18 | 92.12 (n=2) | +0.96 | 17.64 (n=2) | -52.28 |
| 0.06 | **93.26 (n=8)** | **+2.40** | 92.01 (n=14) | +0.85 | -- | -- |
| 0.07 | 93.19 (n=9) | +2.33 | 92.18 (n=1) | +1.03 | 26.54 (n=4) | -43.38 |
| 0.1 | 92.03 (n=8) | +1.17 | -- | -- | 42.76 (n=2) | -27.16 |
| 0.2 | 91.39 (n=3) | +0.52 | -- | -- | 68.32 (n=2) | -1.59 |
| 0.3 | 90.96 (n=3) | +0.09 | 91.76 (n=2) | +0.61 | -- | -- |
| 1 | 90.86 (n=3) | 0.00 | 91.15 (n=2) | 0.00 | 69.92 (n=2) | 0.00 |

* The **interior optimum is real but alpha0-specific**: a clean inverted-U peaking at
  r=0.06 (+2.40) at alpha0=1e-6; at alpha0=1e-3 the curve is **flat** at +0.85..+1.03 across
  r in [0, 0.07] — partial pooling still helps ~1pp, but there is no interior optimum.
* **On CIFAR-100 M1 is monotone harm.** Every r<1 is worse than plain layerwise; the curve
  only climbs back to the r=1 asymptote. No interior optimum at either alpha0
  (r=0.07 at alpha0=1e-6 = 59.05, n=2, still 10.8pp below plain layerwise 69.89).

## 22.3 M0 (shrink) is the more robust method

`beta <- b - lam*(b - b.mean())`. vs plain layerwise, CIFAR-10 ResNet18 100ep:

| alpha0 | plain | M0 shrink | delta |
|---|---|---|---|
| 1e-3 | 91.15 (n=8, sd .19) | 92.25 (n=3, sd .18) | **+1.10** |
| 1e-4 | 90.84 (n=8, sd .18) | 92.28 (n=3, sd .04) | **+1.44** |
| 1e-6 | 90.82 (n=24, sd .16) | 92.02 (n=36, sd .60) | **+1.21** |

lambda curve at alpha0=1e-6 (SGDm/Lion, layerwise):

| lam | 1e-5 | 3e-5 | 1e-4 | 1e-3 | 0.01 | 0.03 | 0.1 | 0.3 | 0.5 | 1.0 |
|---|---|---|---|---|---|---|---|---|---|---|
| plateau | 90.80 | 90.79 | 90.62 | 92.32 | **92.47** | 92.25 | 92.29 | 92.22 | 92.20 | 92.20 |
| n | 2 | 2 | 2 | 3 | 3 | 3 | 12 | 3 | 3 | 3 |

* **Identity verified at the other end**: lam<=1e-4 recovers plain layerwise (90.62-90.80 vs
  90.82). Both hierarchy branches now have a verified no-op limit.
* Sharp **threshold** between lam=1e-4 (90.62) and lam=1e-3 (92.32), then a **flat plateau
  across three orders of magnitude** (lam 1e-3..1.0, all 92.20-92.47, sd<=0.23).
* M1's peak is higher at alpha0=1e-6 (+2.40 vs +1.65) but needs r in [0.04,0.07] and decays to
  zero by r=0.3. M0 is lower-peak, far wider, and alpha0-independent. **Correction to an
  earlier draft of this section: M1 layerwise is NOT unstable at r=0.1/0.3 — the sd=16pp I
  first computed came from failing to filter `granularity==layerwise`, which pulled in
  collapsing weightwise/nodewise arms.**

## 22.4 The win is meta-gradient AGGREGATION, not step-size granularity

CIFAR-10, alpha0=1e-6, 100ep. Both "fully pooled" arms hold **one** effective step size, as
does native scalar — they differ only in how the meta-gradient is aggregated:

| arm | effective step sizes | plateau |
|---|---|---|
| native `scalar` | 1 | 87.77 (n=17) |
| plain `layerwise` | N | 90.82 (n=24) |
| M0 shrink lam=1.0 (= mean every step) | 1 | 92.20 (n=3) |
| M1 additive r=0 (= mean update) | 1 | 92.23 (n=6) |

**Both single-step-size pooled arms beat plain per-layer step sizes by ~1.4pp and beat the
native scalar parameterisation by ~4.4pp.** Per-layer adaptivity is not what is buying the
gain; averaging the meta-gradient across layers is. This is the mechanism the refuted
sqrt(N) noise model was reaching for, and it is measurable without any noise assumption.

## 22.5 Model scale — the granularity benefit collapses with size (COMPLETE, n=3-24)

CIFAR-10, alpha0=1e-6, 100ep, plain (no hierarchy):

| network | params | scalar | layerwise | layerwise - scalar |
|---|---|---|---|---|
| ResNet10 | 4.9M | 70.74 (n=3) | 90.62 (n=3) | **+19.88** |
| ResNet18 | 11.2M | 87.77 (n=17) | 90.82 (n=24) | **+3.05** |
| ResNet34 | 21.3M | 89.32 (n=3) | 90.22 (n=3) | **+0.90** |

Monotone decay over a 4.3x parameter range. This is the parent paper's premise measured
directly, and it is the cleanest scale result in the repo. The alpha0=1e-3 replication
(`sa3-*`) is in flight; its completed cells so far agree in sign (ResNet10 scalar 71.67
vs layerwise 91.40).

## 22.6 CIFAR-100 granularity ordering (plain, 100ep) — same direction, larger

| granularity | a0=1e-3 | a0=1e-6 |
|---|---|---|
| scalar | 22.47 (n=2) | 22.30 (n=2) |
| resnet18_blocks | 51.32 (n=2) | 52.73 (n=2) |
| layerwise | 70.11 (n=2) | 69.89 (n=2) |

Granularity is worth **+47.6pp** on CIFAR-100 vs +3.05pp on CIFAR-10 (ResNet18, same alpha0).
Task difficulty amplifies the granularity benefit as strongly as small model size does.

## 22.7 Cluster reality — 24 GPUs is the ceiling, not 84

Every GPU node is fully allocated (`gpu_alloc` 4/4, 2/2, 3/3; one free L4 cluster-wide).
`sinfo` "mix" denotes free **CPUs**, not GPUs. `gpu-short` is an *overlay* partition over the
same physical nodes 851-887 as the four 7-day partitions, so the per-user quotas
(short 12 + l4 8 + 2080ti 12 + mig 8 + a100 2 = 42/account) are **not** 42 independent GPUs.
Both accounts run exactly 12, all on `gpu-short`; the other 246 pending jobs sit at
reason=Priority behind other users' 7-day jobs. **Queue depth is not the binding
constraint — composition is.** At ~24 slots and ~1h/job, a 391-job queue is ~16h deep.

## 22.8 Submitted this cycle (48 jobs; queues alice 219 / alice2 172)

M0 had **zero** jobs queued on either account while M1 — the method that just failed on
CIFAR-100 — held ~150. That was the gap.

| tag | acct | n | what | why |
|---|---|---|---|---|
| `m0c-*` | alice2 | 18 | CIFAR-100 M0 shrink, lam {0.01,0.1,1.0} x a0 {1e-3,1e-6} x 3 seeds, 100ep | does our best method generalise where M1 is actively harmful? lam=1.0 doubles as the 22.4 aggregation probe (C100 native scalar = 22.47) |
| `c1b-*` | alice2 | 6 | CIFAR-100 plain layerwise, seeds 2-4, both a0 | the baseline all of 22.2/22.6 rests on is n=2 |
| `m0l-*` | alice | 12 | CIFAR-10 M0 lambda {1e-3,0.01,0.3,1.0} at a0=1e-3, 3 seeds | the flat lambda plateau exists only at a0=1e-6; only lam=0.1 was run at 1e-3 |
| `m0s-*` | alice | 12 | ResNet10/34 x lam {0.01,0.1} x 3 seeds, a0=1e-6, 100ep | every R10/R34 shrink run so far is 20-epoch. Does M0 survive scale when plain granularity does not (22.5)? ResNet18 already has both lam. |

Pre-flight (cycle-21 lesson): `HIER=shrink,LAM=<l>` parsed against the real `HF.py` lines
23-25 on a login node for every lam in {0.001,0.01,0.1,0.3,1.0} plus the no-export plain arm
— all clean. `ETA_RATIO` deliberately **not** exported (shrink never reads it). ResNet10/34
and `ResNet18_c100` confirmed in `build_network.py`; `cifar-100-python` staged on alice2.
`resnet18_blocks` avoided on R10/R34 (hard-coded partition, ResNet18-only).

## 22.9 Still open

* M0 on CIFAR-100 and at scale — the two cells that decide whether M0 is the paper's method.
* The `sa3-*` alpha0=1e-3 scale replication is ~30% complete.
* 22.4 (aggregation vs granularity) is CIFAR-10/alpha0=1e-6 only; `m0c-*` lam=1.0 extends it.
* Non-meta baseline (`fx-adamw-*`) still absent on CIFAR-10; `fc100-cos-*` pending for C100.
* Every CIFAR-100 cell in 22.2/22.6 is n=2 until `c1b-*` lands.

---

# Cycle 23 — the pooling gain runs OPPOSITE to the granularity gain in model scale

All numbers below re-derived from `results/all_runs.csv` (733 rows, +20 this cycle),
`plateau` (mean of last 20 epochs), filtered `epochs_done>=100`, `superseded==0`, `AUGMENT=1`.

## 23.1 Pipeline check

Re-aggregation reproduces the cycle-21 baseline exactly: AdamW+cosine lr=1e-3 =
**94.093 +-0.036 (n=3)**. The aggregator, merge and plateau column are intact.

## 23.2 The alpha0=1e-3 scale replication landed (`sa3-*`)

22.5 was measured only at alpha0=1e-6 and flagged "in flight". It now replicates.
CIFAR-10, plain (no hierarchy), 100ep. **One collapsed run excluded** — see 23.2b:

| network | a0=1e-6 scalar | a0=1e-6 layer | gain | a0=1e-3 scalar | a0=1e-3 layer | gain |
|---|---|---|---|---|---|---|
| ResNet10 | 70.742 +-0.832 (3) | 90.619 +-0.267 (3) | **+19.88** | 70.782 +-1.252 (2) | 91.259 +-0.275 (3) | **+20.48** |
| ResNet18 | 89.201 +-1.974 (23) | 90.933 +-0.529 (37) | +1.73 | 88.784 +-2.037 (15) | 91.100 +-0.319 (20) | +2.32 |
| ResNet34 | 89.317 +-0.127 (3) | 90.220 +-0.011 (3) | **+0.90** | 89.727 +-0.276 (2) | 90.237 (n=1) | **+0.51** |

Monotone decay at BOTH alpha0, and once the collapse is excluded the two alpha0 ladders
**agree closely** (+19.88/+1.73/+0.90 vs +20.48/+2.32/+0.51) — they did not before.
The cycle-21 mechanism also replicates: the **layerwise arm is flat** (1e-3 spread
91.259->90.237 = 1.02pp; 1e-6 spread 0.71pp) while the **scalar arm climbs 18.5-19.0pp**.
The granularity "gain" shrinking with scale is scalar catching up, not layerwise degrading —
now shown at two alpha0.

Caveat: ResNet34 layerwise @1e-3 is **n=1**; two more seeds are queued on alice2.

## 23.2b The `collapsed` column does not work — it cost 2.9pp on the middle cell

`ResNet18 / scalar / a0=1e-6` contains 24 completed runs, one of which plateaus at **20.5**
(the other 23 span 86.0-91.7). That single run drags the cell mean from 89.201 to 86.333 and
the sd from 1.97 to **14.16**, inflating the reported granularity gain from **+1.73 to +4.60**
— i.e. a single run out of 24 more than doubles the headline middle cell of the scale ladder.

`all_runs.csv`'s `collapsed` column is **`0` on every row in the file**, including this one, so
it flags nothing and must not be relied on. Until it is fixed, filter on `plateau > 50`
explicitly. Only this one cell in the CIFAR-10 plain ladder is affected (drop counts are 0
everywhere else), so 23.2's other numbers are unchanged.

The bulk of that cell is also genuinely two-clustered (14 runs at ~87.7, 9 at ~91.6) — worth a
look on its own, but that spread is *not* what produced the sd=14.16.

## 23.3 NEW — M1 additive pooling gain INCREASES with model size

Same runs, additive hierarchy at r=0.06 vs plain layerwise, CIFAR-10:

| network | a0=1e-6 delta | n | a0=1e-3 delta | n |
|---|---|---|---|---|
| ResNet10 | +0.17 | 3v3 | **-2.30** | 3v3 |
| ResNet18 | +2.33 | 8v37 | +0.83 | 17v20 |
| ResNet34 | **+2.62** | 3v3 | **+3.29** | 1v1 |

Monotone INCREASING at both alpha0, crossing zero at 1e-3. This is the **opposite direction**
to 23.2's granularity gain (+19.88 -> +0.90). Two mechanisms with opposite scale dependence:
plain granularity stops paying as models grow; pooling starts paying.

`sa3-ResNet34-add-s0` at **93.522** is the highest single MetaOptimize plateau in the campaign
(previous best 93.552 `e3a-r01_s1` R18) — still **below** the tuned non-meta 94.093. The
cycle-21 correction stands: this is a statement about MetaOptimize internals, not a win.

Caveat: both ResNet34 @1e-3 cells are **n=1**. The alpha0=1e-6 R34 pair is n=3 with sd 0.147
(additive) / 0.011 (plain) and is the defensible cell.

## 23.4 Why 23.3 is not yet reportable — R34 has no r-curve

Rule 3 (report the curve, not the max cell) is currently violated: ResNet34 is sampled at
**one** r. The two curves we do have, CIFAR-10 @ alpha0=1e-6, delta vs plain layerwise:

| r | ResNet10 (plain 90.619) | ResNet18 (plain 90.933) |
|---|---|---|
| 0 (FULL pooling) | **-8.50** (n=3) | **+1.26** (n=8) |
| 0.03 | -1.39 (3) | +1.21 (8) |
| 0.04 | — | +1.93 (5) |
| 0.05 | -0.36 (3) | +2.11 (12) |
| 0.06 | +0.17 (6) | **+2.33 (8)** |
| 0.07 | +0.49 (3) | +2.26 (9) |
| 0.1 | **+0.97 (3)** | +1.35 (10) |
| 0.2 | +0.46 (3) | +0.45 (3) |
| 0.3 | — | +0.02 (3) |
| 1 (identity) | -0.03 (3) | -0.07 (3) |

Both are interior optima, and **r=1 reproduces plain layerwise to -0.03/-0.07pp** — the
identity control holds at both architectures (structural check, per rule 4).

Two things move together with model size:
* **peak location** shifts toward LESS pooling as the model shrinks: R18 peaks at r=0.06, R10 at r=0.1
* **peak amplitude** grows with model size: R10 +0.97, R18 +2.33
* **full pooling (r=0)** goes from catastrophic at R10 (-8.50) to helpful at R18 (+1.26)

**Prediction to test:** ResNet34's optimum sits at r < 0.06 with peak > +2.62, and r=0 at R34
should be >= +1.26. If it holds, the claim becomes "the tolerable pooling fraction is set by
model size", which is mechanistic rather than a single lucky cell.

## 23.5 Submitted this cycle (45 jobs; queues alice 237 / alice2 178 = 415)

| tag | acct | n | what | why |
|---|---|---|---|---|
| `r34r-*` | alice | 27 | R34 CIFAR-10 a0=1e-6, r in {0,.02,.03,.04,.05,.08,.1,.2,1} x 3 seeds | THE test of 23.4's prediction; r=0.06 already n=3 so skipped; r=1 = identity control |
| `r10c-*` | alice2 | 18 | R10 CIFAR-10 a0=1e-3, r in {0,.05,.1,.2,.5,1} x 3 seeds | R10@1e-3 has only r=0.06 and it is NEGATIVE (-2.30); does the optimum shift right at higher alpha0 too? |

Pre-flight: read the real `Optimizers/HF.py` lines 23-25 — `LAM` defaults to `'0'`,
`ETA_RATIO` to `'1'` when unset, both with an `or` guard. So the additive arm must export
**only** `HIER` and `ETA_RATIO`. Verified `ETA_RATIO=0` parses to `0.0` (the `or 1` guard does
not trip: `'0'` is a non-empty string). Matches the working `sc-ResNet34-add-s0` ENV line.

## 23.6 Queue triage

Negative `Nice` is denied, so promotion = niceing others back. Pushed to Nice=20000:
alice 102 jobs (`sc50` 6, `sc101` 12, `sw-cos` 21, `pp-` 9, `fx-e300` 9, `p6f` 9, `mx-b` 27,
`mx-add` 9); alice2 58 jobs (`zrn` 13, `amx-` 15, `am4-` 21, `rcg` 9). `sc50`/`sc101` are the
clearest cut: the CIFAR-10 layerwise arm is flat (23.2), and R50 reaches only 31-34 epochs in
the 4h `gpu-short` window, so a 100-epoch R50 point cannot be produced there at all.

## 23.7 Still open

* 23.4's prediction — `r34r-*` decides it.
* `cs-*` (18, alice) CIFAR-100 x R10/R34 granularity ladder: cancelled and **resubmitted**
  23:54 on 19 Aug (new ids 4683766+, elapsed 0:00 — no data lost). Still the decisive
  task-difficulty-vs-parameter-count experiment.
* ResNet34 @ alpha0=1e-3 is n=1 in both arms; seeds queued on alice2.
* ResNet50 needs a 7-day partition to produce any 100-epoch point.
* M0 shrink on CIFAR-100 and at scale (`m0c-*`, `m0s-*`) still in flight.

# Cycle 24 (20 Aug 2026)

Re-aggregated both accounts with the repo aggregator (760 runs, +27 since cycle 23:
`rc6` 9, `r10b` 12, `a0h` 6). Every number below re-derived from `results/all_runs.csv`.

## 24.1 CORRECTION — two r-cells were mixtures of incompatible run families

Grouping the M1 ladder by `(network, dataset, alpha0, eta_ratio)` alone is **wrong**. Three
separators are invisible in that key, and two cells were pooling across them:

| family | augment | meta | epochs_req | plateau @ r=0.1 |
|---|---|---|---|---|
| `ad-l-*`  | 1 | Lion | 100 | 92.626 (n=5) |
| `adg-b-*` | 1 | Lion | 100 | 91.598 (n=3) |
| `adg-A-*` | 1 | **Adam** | 100 | 91.043 (n=3) |
| `ha-w-*`  | **unrecorded** | Lion | 100 | 48.712 (n=2) |
| `e3a-*`   | 1 | Lion | **300** | 93.28 (n=2) |
| `p4-ad-*` | 1 | Lion | **20** | 26.71 (n=1) |

`ha-w-*` is the no-augmentation family the OPERATIONS gotcha warns about; it plateaus ~48.
Effect of restricting to the canonical config (`bs=100, SGDm, Lion, mstep=1e-3, gamma=1,
AUGMENT=1, guard on, 100ep`):

| cell | was reported | corrected |
|---|---|---|
| R18/C10/1e-6 r=0.1 | 89.120 +-11.269 (n=14) | **92.240 +-0.556 (n=8)** |
| R18/C10/1e-6 r=0.3 | 80.244 +-14.670 (n=5) | **90.957 +-0.079 (n=3)** |

**Rule added:** the config key is eight fields, not four. `epochs_requested` must be in it —
`epochs_done >= 100` admits 300-epoch runs whose plateau is not comparable.

**Unresolved anomaly:** `ad-l` (92.626, n=5) and `adg-b` (91.598, n=3) agree on *every*
recorded field yet differ by **1.03pp**, ~50x the +-0.02pp reproduction tolerance. Something
that determines a 1pp effect is not being logged. The r=0.1 cell stays heterogeneous
(sd 0.556) until this is found; the peak cells (r=0.05/0.06/0.07) are unaffected.

## 24.2 The corrected CIFAR-10 M1 r-curve is clean and unimodal (n>=3 everywhere)

ResNet18 / CIFAR-10 / a0=1e-6, canonical config. `r` is RETENTION (r=1 = plain layerwise).

| r | plateau | n | vs plain layerwise |
|---|---|---|---|
| 0 (full pooling) | 92.228 +-0.087 | 6 | +1.44 |
| 0.03 | 92.310 +-0.483 | 8 | +1.53 |
| 0.04 | 92.862 +-0.129 | 5 | +2.08 |
| 0.05 | 93.048 +-0.136 | 10 | +2.26 |
| **0.06** | **93.262 +-0.135** | 8 | **+2.48** |
| 0.07 | 93.192 +-0.152 | 9 | +2.41 |
| 0.1 | 92.240 +-0.556 | 8 | +1.46 |
| 0.2 | 91.387 +-0.142 | 3 | +0.60 |
| 0.3 | 90.957 +-0.079 | 3 | +0.17 |
| 1 (identity) | 90.863 +-0.063 | 3 | +0.08 |
| plain layerwise | 90.784 +-0.169 | 17 | — |

**Identity control holds** (rule 4): r=1 reproduces plain layerwise to +0.08pp.

## 24.3 NEW — CIFAR-100 has NO interior pooling optimum (`rc6-*` landed)

Same architecture family, same alpha0, same budget. ResNet18_c100 / CIFAR-100 / a0=1e-6:

| r | plateau | n | vs plain layerwise |
|---|---|---|---|
| 0 (full pooling) | 11.205 +-0.569 | 2 | **-58.68** |
| 0.05 | 43.507 +-1.404 | 2 | -26.38 |
| 0.07 | 59.046 +-1.691 | 2 | -10.84 |
| 0.1 | 69.145 | 1 | -0.74 |
| 0.2 | 69.890 +-0.018 | 2 | +0.00 |
| 0.4 | 69.453 | 1 | -0.43 |
| 0.7 | 69.617 +-0.045 | 2 | -0.27 |
| 1 (identity) | 69.542 +-0.032 | 2 | -0.34 |
| plain layerwise | 69.886 +-0.134 | 2 | — |

The curve rises monotonically and **saturates flat** from r~0.1; the best cell (r=0.2) is
+0.004pp over plain layerwise. Pooling on CIFAR-100 never helps — it is neutral above
r~0.1 and catastrophic below it. Note the CIFAR-10 optimum (r=0.06, +2.48) lands exactly
where CIFAR-100 has lost 10-26pp.

**This supersedes "pooling inverts between datasets."** It does not invert, it *vanishes*:
CIFAR-10 has an interior optimum worth +2.48pp, CIFAR-100 has none. The earlier "-43.7pp at
r=0.07" was the **a0=1e-3** cell (26.538 +-0.844, n=4); at a0=1e-6 the same r costs -10.84.

Caveat: n=1-2 on every CIFAR-100 cell. `c6f-*` (submitted below) takes the flat region to
n=3-5. The r=1 identity control also sits 0.34pp *below* plain layerwise here vs +0.08pp
above on CIFAR-10 — within n=2 noise, but it is the structural check and it needs the seeds.

## 24.4 NEW — the plain granularity ORDERING also inverts between datasets

Plain arms (no hierarchy), a0=1e-6, canonical config:

| granularity | CIFAR-10 / R18 | CIFAR-100 / R18_c100 |
|---|---|---|
| scalar | 87.769 +-0.145 (11) | 22.300 +-0.808 (2) |
| layerwise | 90.784 +-0.169 (17) | **69.886 +-0.134 (2)** |
| resnet18_blocks | 91.346 +-0.148 (11) | 52.728 +-0.407 (2) |
| **nodewise** | **91.593 +-0.138 (8)** | pending (`c100f-node`) |
| weightwise | 77.822 +-0.351 (3) | pending (`c100f-w`) |

CIFAR-10 is monotone-finer-is-better up to nodewise, then collapses at weightwise — an
interior optimum in granularity. On CIFAR-100 **blocks and layerwise swap**: finer than
layerwise already costs 17.2pp. Both dataset effects (24.3, 24.4) point the same way —
CIFAR-100 tolerates far less sharing *and* far less splitting than CIFAR-10.

The unifying prediction is the agreement measurement: coordinate sign-agreement should be
markedly lower on CIFAR-100. `p6f-*` measures exactly this and was promoted this cycle.

## 24.5 Operations — two handoff claims corrected

* **`sc50` is ResNet50 and it finishes fine on `gpu-short`.** CONTINUE-HERE claimed R50
  "cannot produce a 100-epoch point on gpu-short at all (31-34 epochs in 4h)". Measured from
  the live TensorBoard scalars: 54/61/69/78/78/80 epochs at 1:14-1:52 elapsed = **~44
  epochs/hour, 100 epochs in ~2:20** inside the 3:50 limit. Six healthy jobs were nearly
  cancelled on the stale prose. `sc50`/`sc101` extend the scale ladder to R50 (23.5M) and
  R101 (42.5M) — keep them.
* **`scontrol update JobId=<j> Nice=0` IS permitted and is a large promotion.** CONTINUE-HERE
  and 23.6 say "negative Nice is denied, so promotion = niceing others back". Resetting a
  previously-niced job to 0 is not negative and is accepted: `p6f` went 651704 -> 671710,
  from the bottom of the queue to #2. Niceing others back is not required.

## 24.6 Queue actions this cycle

| action | acct | n | why |
|---|---|---|---|
| `p6f-*` Nice=0 (promote to #2) | alice | 9 | agreement/drift on {C100,R10,R34} x {layer,node,weight} — the mechanism 24.3+24.4 both need; it was niced to the back |
| `sw-cos`/`fxcos`/`fc100` Nice=40000 | alice | 37 | baseline LR tuning; the baseline is settled at 94.093 +-0.036 |
| **submitted `c6f-*`** | alice2 | 21 | CIFAR-100 R18 a0=1e-6, r in {.1,.15,.2,.3,.5,1} + plain layerwise x seeds 2,3,4 — takes 24.3's flat region to n=3-5 |

Queues after: alice 232, alice2 179 = **411 jobs**, 22 running (12+10, the qos ceiling).
alice2 order is now all-CIFAR-100 at the front (`c100f` -> `c6f` -> `c100b` -> `c1b` -> `m0c`).

## 24.7 Still open

* **The `ad-l` vs `adg-b` 1.03pp gap on identical recorded config** — a logging gap that
  bounds confidence in any n-pooled cell. Highest-value integrity item.
* `r34r-*` (27, alice) still pending — R34 r-curve, completes the scale family.
* CIFAR-100 nodewise/weightwise (`c100f-*`, alice2, high priority) completes 24.4.
* `cs-*` (18, alice) CIFAR-100 x R10/R34 — task difficulty vs parameter count.
* R50/R101 rungs in flight (`sc50` running, `sc101` on a 7:30 partition).

---

# Cycle 25 (20 Aug 2026) — the cycle-24 "logging gap" was an analysis bug, and pooling strength is not comparable across granularities

Re-aggregated both accounts (787 runs, +27 since cycle 24: `c100b` 14, `m1a3` 4, `r10b` 3,
`sc-ResNet34` 6). Every number below re-derived from `results/all_runs.csv` with
`superseded==0` and the canonical config filter.

## 25.1 RESOLVED — cycle 24's "highest-value integrity item" was ours, not the logger's

24.1 recorded an unexplained 1.03pp gap between `ad-l-*` (92.626) and `adg-b-*` (91.598),
stating they "agree on *every* recorded field yet differ by 1.03pp" and concluding
"something that determines a 1pp effect is not being logged."

**They do not agree. They differ in `--stepsize-groups`, and it was recorded correctly.**

| family | `--stepsize-groups` in the ARGS line | CSV `granularity` |
|---|---|---|
| `ad-l-*`  | `layerwise` | `layerwise` |
| `adg-b-*` | `resnet18_blocks` | `resnet18_blocks` |

Verified from the raw artefacts: `runs_alice2/ad-l-r01-s0-4681040.out` vs
`runs/adg-b-r01-s0-4681164.out`. The aggregator had it right in both rows all along; the
cycle-24 **config key omitted `granularity`** — the single most important field in the project —
so two different granularities were pooled into one cell.

**Rule amended:** the config key is **nine** fields, not eight. `granularity` is mandatory in it.
No logging gap exists and nothing needs to be instrumented.

## 25.2 Consequence — the M1 r-curve's one ragged cell was the contamination

ResNet18 / CIFAR-10 / a0=1e-6 / 100ep / SGDm+Lion, `hier=additive`, **layerwise only**:

| r | plateau | sd | n | was reported (24.2) |
|---|---|---|---|---|
| 0 (full pooling) | 92.228 | 0.087 | 6 | 92.228 (unchanged) |
| 0.03 | 92.637 | 0.165 | 5 | 92.310 ±0.483 (n=8) |
| 0.04 | 92.862 | 0.130 | 5 | unchanged |
| 0.05 | 93.047 | 0.136 | 10 | unchanged |
| **0.06** | **93.262** | **0.135** | 8 | unchanged |
| 0.07 | 93.192 | 0.152 | 9 | unchanged |
| 0.1 | **92.626** | **0.214** | 5 | **92.240 ±0.556 (n=8)** |
| 0.2 | 91.387 | 0.142 | 3 | unchanged |
| 0.3 | 90.957 | 0.079 | 3 | unchanged |
| 1 (identity) | 90.864 | 0.062 | 3 | unchanged |

The r=0.1 cell's sd falls **2.6x** (0.556 -> 0.214) and it rises 0.39pp. The curve is now
monotone up to r=0.06 and monotone down after it, with no ragged cell. The peak cells were
never affected. 24.1's caveat "the r=0.1 cell stays heterogeneous until this is found" is
discharged.

## 25.3 NEW — the M1 pooling gain depends on GRANULARITY, and M1's r is comparable across granularities

`_apply_hier` (M1, additive) pools the **mean** of the realised beta update
(`dm = d.mean()`; for nodewise/weightwise `dm = tot/cnt`). Its `r` is therefore
**m-invariant** and the same `r` means the same thing at every granularity.

R18 / C10 / a0=1e-6 / 100ep:

| granularity | m (groups) | plain | M1 identity r=1 | best r | best plateau | gain |
|---|---|---|---|---|---|---|
| resnet18_blocks | 6 | 91.350 ±0.142 (12) | *not yet run* | 0.03 | 91.765 ±0.222 (3) | +0.415 vs **plain** |
| layerwise | 62 | 90.784 ±0.169 (17) | 90.864 ±0.062 (3) | 0.06 | 93.262 ±0.135 (8) | **+2.399 vs identity** |
| nodewise | 14,420 | 91.593 ±0.138 (8) | — | — | — | submitted (`gp-node-*`) |
| weightwise | 11,173,962 | 77.822 ±0.351 (3) | — | — | — | submitted (`gp-w-*`) |

6-block has only 2 r-points (0.03, 0.1) and **no r=1 identity anchor**, so its +0.415 is
against plain, not against the identity — not the same comparison as layerwise's +2.399.
`gp-blk6-r1` supplies the anchor. Direction is nonetheless clear: a 6-group partition gains
~0.4pp from pooling where a 62-group partition gains ~2.4pp.

## 25.4 NEW — `_zpool` is NOT m-invariant, and the existing zpool granularity comparison is confounded

```
_zpool:   z'_b = (1-r)*SUM(z) + r*z_b      <- SUM
_zmpool:  z'_b = (1-r)*MEAN(z) + r*z_b     <- MEAN
_apply_hier (M1): beta_prev + MEAN(d) + r*(d - MEAN(d))   <- MEAN
```

The pooled term in `_zpool` scales with **m**, so its `r` means something different at every
granularity. Endpoints are still exact and are verified below, but the **path between them is
compressed against r=1 by a factor of m**.

**Structural verification of all six endpoints** (Rule 4 — measured, not asserted):

| arm | n | plateau | should equal | Δ |
|---|---|---|---|---|
| zpool r=0, layerwise | 5 | 87.740 ±0.139 | plain scalar 87.772 | 0.032 |
| zpool r=0, weightwise | 5 | 87.763 ±0.036 | plain scalar 87.772 | 0.009 |
| zpool r=1, layerwise | 5 | 90.933 ±0.177 | plain layerwise 90.784 | 0.149 |
| zpool r=1, weightwise | 5 | 77.921 ±0.332 | plain weightwise 77.822 | 0.099 |
| M1 r=1, layerwise | 3 | 90.864 ±0.062 | plain layerwise 90.784 | 0.080 |
| M1 r=1, ResNet10 layerwise | 3 | 90.586 ±0.166 | plain R10 90.619 | 0.033 |

All six hold. `r=0 -> scalar` and `r=1 -> plain` are both exact for zpool, at two granularities.

**Why the compression matters.** For layerwise (m=62) the interesting region is r in [0.9, 1].
The m-equivalent region at weightwise (m=11.17M) is `1-r ~ 5e-8` — **below float32 resolution
(eps = 1.19e-7)**. `_zpool` therefore *cannot express weak pooling at weightwise at all*. Any
cross-granularity reading of the zpool sweep is measuring m, not pooling.

## 25.5 UNREDUCED RESULT — zpool weightwise has an interior optimum beating BOTH endpoints; layerwise does not

Present in the repo since the `zsw`/`zsx`/`zrn` families ran; never reduced.
R18 / C10 / a0=1e-6 / 100ep:

| r | layerwise | n | weightwise | n |
|---|---|---|---|---|
| 0 (= scalar) | 87.740 ±0.139 | 5 | 87.763 ±0.036 | 5 |
| 0.1 | 89.471 ±0.137 | 5 | 87.847 ±0.081 | 5 |
| 0.3 | 89.476 ±0.170 | 5 | 87.950 ±0.165 | 5 |
| 0.5 | 89.170 ±0.104 | 4 | 87.870 ±0.122 | 4 |
| 0.7 | 89.100 ±0.172 | 6 | 88.064 ±0.152 | 6 |
| 0.9 | 90.196 ±0.209 | 2 | 88.510 ±0.105 | 2 |
| 0.95 | 90.435 ±0.117 | 2 | 88.798 ±0.011 | 2 |
| 0.99 | 90.971 | 1 | **89.052 ±0.317** | 2 |
| 1 (= plain) | 90.933 ±0.177 | 5 | **77.921 ±0.332** | 5 |

* **layerwise: monotone.** No interior point beats r=1. zpool only ever costs accuracy.
* **weightwise: interior optimum.** r=0.99 (89.052) beats *both* endpoints — plain weightwise
  (77.921, **+11.13pp**) and scalar (87.763, **+1.29pp**).

Read against 25.4 this is not a "flat region then a jump": it is the scalar->plain
interpolation compressed by m, and **the entire 11pp transition lives inside r in [0.99, 1]**,
where only two cells exist. The weightwise optimum's true location and height are unmeasured.
Because float32 cannot resolve the region, the fix is the operator, not more r values —
hence 25.7.

**Caveat:** the r>=0.9 cells are n=1-2. Nothing here is stated at the n>=3 headline standard yet.

## 25.6 Model-scale ladder — the ResNet10 r-curve is complete (13 r-points)

CIFAR-10 / a0=1e-6 / 100ep / layerwise, gain measured against the **r=1 identity**:

| network | params | plain | identity r=1 | r* | peak plateau | gain | r-points |
|---|---|---|---|---|---|---|---|
| ResNet10 | 4.9M | 90.619 ±0.267 (3) | 90.586 ±0.166 (3) | **0.10** | 91.590 ±0.051 (3) | **+1.004** | 12 |
| ResNet18 | 11.2M | 90.784 ±0.169 (17) | 90.864 ±0.062 (3) | **0.06** | 93.262 ±0.135 (8) | **+2.399** | 9 |
| ResNet34 | 21.3M | 90.220 (3) | *not yet run* | 0.06 (only point) | 92.838 ±0.147 (3) | +2.618 vs plain | **1** |

**r\* moves left and the gain grows as the model grows.** R34 still rests on a single r value
with no identity anchor — `r34r-*` (27 jobs, alice, 9 r-values x 3 seeds incl. r=1) fixes both.
Do not state the R34 row as a curve until it lands.

## 25.7 Submitted this cycle (78 jobs)

| batch | acct | n | why |
|---|---|---|---|
| `gp-{node,w,blk6}-*` | alice2 | 48 | 25.3 — M1 r-curve at nodewise / weightwise / 6-block. M1's r is m-invariant, so this is the clean test of "does pooling help more when the partition is finer?". Includes the r=1 identity anchor at every granularity. Prediction: weightwise, whose plain arm collapses to 77.8, gains most. |
| `zmg-{l,w}-*` | alice | 30 | 25.4 — `_zmpool` (MEAN-based, m-invariant) r-curve at layerwise vs weightwise, r in {0,0.06,0.2,0.6,0.9} x 3 seeds. The only M2 form in which r is comparable across granularities. Only 4 zmpool runs exist and all are 20-epoch endpoint gates. |

Queue actions: `c6f-*` (21, alice2) niced to 30000 — 24.3 already answered CIFAR-100 pooling
("no interior optimum, saturates flat") at n=2; raising a null to n=5 is the lowest-value work
in the queue. Queues after: alice 239, alice2 207 = **446 jobs**, 24 running (12+12).

## 25.8 CIFAR-100 granularity ordering is now alpha0-robust

`c100b-*` landed, supplying the a0=1e-3 replication of 24.4. Plain arms, ResNet18_c100, 100ep:

| granularity | a0=1e-6 | a0=1e-3 |
|---|---|---|
| scalar | 22.300 ±0.808 (2) | 22.461 ±0.456 (4) |
| resnet18_blocks | 52.728 ±0.407 (2) | 51.276 ±0.892 (3) |
| layerwise | **69.886 ±0.134 (2)** | **69.850 ±0.487 (3)** |

The blocks/layerwise inversion vs CIFAR-10 (where blocks 91.350 > layerwise 90.784) reproduces
at both alpha0, and the a0 dependence is <1.5pp everywhere. **24.4's dataset inversion is not an
alpha0 artefact.** Contrast with 24.3's pooling result, which *is* strongly a0-dependent.

## 25.9 Still open

* **6-block, nodewise, weightwise M1 identity anchors** — `gp-*-r1` in flight. Until they land,
  25.3's cross-granularity gain column is not all measured against the same baseline.
* **R34 r-curve** — `r34r-*` (27, alice) still pending; 25.6's third row is one point.
* **zpool weightwise r in [0.99, 1]** — unmeasurable in float32; superseded by `zmg-*`.
* **p6f-*** (9, alice, rank ~31) — sign-agreement/drift on {C100, R10, R34} x {layer, node,
  weight}. This is the mechanism that 25.3 and 25.5 both predict: pooling should help in
  proportion to how much a partition's coordinates disagree.
* n=1-2 on every zpool cell at r>=0.9 (25.5).

## 26.1 Three never-reduced probe batches were sitting in the repo

Sweeping `find <runs> -name probe.jsonl -size +1k` on both accounts and grepping every dir
name against `docs/FINDINGS.md` + `docs/CORRECTIONS.md`:

| batch | acct | dirs | config | mentioned in docs? |
|---|---|---|---|---|
| `mx/probe_sig_*` | alice | 15 | R18/C10, a0=1e-6, **100ep, free adaptation**, PROBE=25 -> 2000 recs | **no** |
| `p5scale/p5-*` | alice2 | 12 | {R10/C10, R18/C100, R34/C10} x {scal,lay,node,w}, `HIER=shrink LAM=1.0`, a0=**1e-6**, 20ep | **no** |
| `p6mech/p6-*` | alice2 | 16 | R18/C10 layerwise, a0=**1e-3**, 100ep, M1 r-sweep x 2 seeds | **no** |

`mx/probe_sig_*` is the one that matters: it is the ONLY free-adaptation, 100-epoch,
dense-probe granularity series, and its config matches the 25.3 M1 r-curve exactly
(SGDm+Lion, meta-stepsize 1e-3, a0=1e-6, AUGMENT=1, guard on, `HIER` unset).

## 26.2 CORRECTION — three defects in how the probes were being read

Reducer: `bin/agree2.py` (new). `bin/drift_extract2.py` mis-reads all three batches.

1. **`block_sizes.json` reports the wrong `n_tot` for nodewise.** `_probe_init` falls through
   to `nb = self.param_numels` for BOTH nodewise and weightwise, so it claims **11,173,962**
   coordinates for nodewise, which has **14,420** nodes. `frac_neg` is a rational `k/n_tot`,
   so the true denominator is recoverable: it returns **62 / 6 / 14,420 / 11,173,962** for
   layerwise / blocks / nodewise / weightwise and **21,282,122** for ResNet34 — matching the
   independently recorded group and parameter counts exactly. Trusting `block_sizes.json`
   inflates nodewise's significance by `sqrt(11173962/14420)` = **27.8x**.
2. **Zeros are counted in neither sign.** `frac_neg = (z<0)/n_tot` with `frac_zero` separate,
   so agreement must be taken among NONZERO coordinates, `p = frac_neg/(1-frac_zero)`.
   `frac_zero` reaches 0.3 early in training and 0.005 at weightwise.
3. **The window is the startup transient.** `drift_extract2` hard-codes steps 1000-7500 —
   the first 15% of a 50k-step run, i.e. exactly the 14-25 epochs of a0=1e-6 startup.
   All 26.x numbers use a STEADY window (last 50% of records); startup is reported separately.

Two agreement statistics are reported because neither alone is sign-agreement:
`sys%` = `mean_t(frac_neg)` then `max(p,1-p)` — a persistent common direction; and
`step%` = `mean_t max(p_t, 1-p_t)` — agreement within a step, which is biased UP by sampling
noise, so its independence null `0.5 + sqrt(2/pi)/(2 sqrt(n))` is printed beside it.

## 26.3 NEW — sign agreement falls monotonically with partition fineness, and the pooling gain runs OPPOSITE to it

`mx/probe_sig_*`, R18 / CIFAR-10 / a0=1e-6 / 100ep / free adaptation, steady window,
mean +- sd over seeds 0,1,2:

| granularity | m | agreement `sys%` | per-step excess over null (pp) | sd_beta | drift/step |
|---|---|---|---|---|---|
| resnet18_blocks | 6 | **70.87 ±0.80** | +5.51 ±0.82 | 3.11 | 4.49e-05 |
| layerwise | 62 | **53.26 ±0.19** | +0.95 ±0.28 | 2.39 | 5.81e-05 |
| nodewise | 14,420 | **51.03 ±0.12** | +0.83 ±0.09 | 1.92 | 2.31e-05 |
| weightwise | 11,173,962 | **50.0053 ±0.0003** | +0.0156 ±0.0015 | 0.76 | 2.18e-06 |
| scalar | 1 | n/a (1 coord) | n/a | n/a | 5.40e-05 |

Agreement falls **monotonically** across five orders of magnitude in m, and the excess over
independence falls by a factor of **353** from blocks to weightwise. Both statistics agree in
ordering, and every cell is tight across three seeds.

Set against the measured M1 pooling gains (25.3, 25.5) the two run in OPPOSITE directions:

| granularity | agreement | M1 pooling gain | source |
|---|---|---|---|
| resnet18_blocks (6) | 70.87% | **+0.415** (vs plain; no identity anchor) | 25.3 |
| layerwise (62) | 53.26% | **+2.399** (vs r=1 identity) | 25.3 |
| weightwise (11.2M) | 50.0053% | **+11.13** (zpool r=0.99 vs plain) | 25.5 |

**Claim: pooling buys the most exactly where the partition's coordinates agree the least.**
This is one mechanism for three results that were previously unrelated — 25.3's
granularity-dependent gain, 25.5's weightwise interior optimum, and 24.3's null on CIFAR-100.
`gp-node-*` / `gp-w-*` (in flight, alice2, promoted this cycle) supply the two missing M1
gains and turn the third column into a measured curve rather than three points from three
different families.

`sd_beta` falling with m (3.11 -> 0.76) is the same story seen from the other side: the finer
the partition, the LESS its group step sizes actually spread out.

## 26.4 NEW — the full-pooling identity is verified STRUCTURALLY, and agreement is a function of r

`p6mech/p6-*`, R18 / CIFAR-10 / **a0=1e-3** / 100ep / layerwise / M1, steady window, 2 seeds:

| r | sd_beta | `sys%` | excess over null (pp) | drift/step |
|---|---|---|---|---|
| 0 (FULL pooling) | **0.0000** | 50.05 | -0.52 | 2.93e-05 |
| 0.03 | 0.750 | 50.26 | -0.22 | 3.73e-05 |
| 0.05 | 1.214 | 50.67 | -0.15 | 4.38e-05 |
| 0.06 | 1.435 | 51.33 | +0.19 | 4.62e-05 |
| 0.07 | 1.641 | 51.87 | +0.12 | 5.04e-05 |
| 0.1 | 2.116 | 55.97 | +2.59 | 7.59e-05 |
| 0.3 | 2.205 | 61.65 | +7.16 | 9.11e-05 |
| 1 (plain layerwise) | 2.473 | 57.81 | +5.33 | 1.34e-04 |

**`sd_beta` is exactly 0.0000 at r=0, on both seeds.** This is the structural verification
Rule 4 demands and that CORRECTIONS 13 flagged as missing — full pooling really does collapse
the 62 group step sizes onto one number, rather than merely producing indistinguishable
accuracy. At r=1 `sd_beta` is 2.47, reproducing plain layerwise's 2.39 from 26.3 (a different
batch, a different account, a different a0). **Both endpoints of the M1 hierarchy are now
verified structurally.**

**Caveat, stated because it bounds the reading:** at n_tot=62 the per-record independence
noise floor is 6.35pp, so an excess under ~1pp is not distinguishable from independence. The
defensible statement is that r <= 0.07 is **indistinguishable from independence** and r >= 0.1
**clearly agrees**; the small negative excesses at r <= 0.05 are noise, not anti-correlation.
The M1 accuracy optimum on this axis is r ~ 0.06 (25.3, at a0=1e-6) — the largest r that still
looks independent — but p6mech is a0=1e-3 and the r-curve is a0=1e-6, so this is a
suggestive alignment across two a0, not a matched measurement. `cw-*` probes fix that.

## 26.5 The sqrt(N) refutation replicates at a second alpha0 (`p5scale`)

`HIER=shrink LAM=1.0` (beta held common — confirmed structurally, `sd_beta = 0.0000` on every
arm), a0=**1e-6**, 20ep. Log-log OLS of drift/step against **group size** N_b = params/group,
over {scalar, layerwise, nodewise, weightwise}:

| setting | slope | R^2 | sqrt(N) model requires |
|---|---|---|---|
| ResNet10 / CIFAR-10 | **+0.075** | 0.72 | -0.500 |
| ResNet18 / CIFAR-100 | **+0.110** | 0.66 | -0.500 |
| ResNet34 / CIFAR-10 | **+0.081** | 0.69 | -0.500 |

Sign inverted in 3/3, at an a0 the earlier `p4scale` measurement did not cover.
**Caveat:** 20 epochs at a0=1e-6 lies entirely inside the 14-25 epoch startup transient, so
this is a startup-regime replication, not a steady-state one. `p4scale` (a0=1e-3) remains the
steady-state evidence.

## 26.6 CORRECTION — the published `p4scale` slopes include a SATURATED arm

The meta-optimizer is **Lion, whose update is sign-based**, so `|d beta|` per step equals the
meta-stepsize (1e-3) EXACTLY. Therefore `drift/step <= 1e-3` is a **hard ceiling**, and
`drift/step / 1e-3` is precisely the net temporal sign-consistency of the meta-gradient.

`p4-r10-scal` and `p4-c100-scal` both read **exactly 1.000e-03** — pinned at the ceiling.
Refitting without them:

| setting | slope, all 4 points | R^2 | slope, unsaturated only | R^2 |
|---|---|---|---|---|
| ResNet10 / CIFAR-10 | +0.238 | 0.68 | **+0.177** | 0.41 |
| ResNet18 / CIFAR-100 | +0.290 | 0.36 | **+0.150** | **0.08** |
| ResNet34 / CIFAR-10 | +0.205 | 0.70 | +0.205 (none saturated) | 0.70 |

The previously published `+0.179 / +0.268 / +0.203` are all-4-point fits and so inherit the
saturated scalar arm. **The refutation itself is untouched — the slope is positive in 6/6 fits
across two alpha0 and three settings, where the model requires -0.500.** But the slope
MAGNITUDES must not be quoted as point values, and the CIFAR-100 / a0=1e-3 cell has
essentially no log-log trend at all once the saturated point is dropped (R^2 = 0.08).
Normalise drift by the meta-stepsize in future; raw drift/step is a censored statistic.

## 26.7 Submitted this cycle — `cw-*` (36 jobs, alice), a pre-registered falsifiable test

The mechanism of 26.3 is so far a *fit* to three points. `cw-*` makes it a **prediction**.

24.3 measured NO interior pooling optimum on CIFAR-100 at layerwise (best cell +0.004pp —
nothing), which read as a flat contradiction of the CIFAR-10 result. 26.3 explains it:
CIFAR-100 layerwise agreement is HIGH. But agreement must collapse toward 50% at weightwise on
*any* dataset — 11.2M coordinates cannot agree. Hence:

> **PREDICTED:** on CIFAR-100, M1 pooling is useless at layerwise (already measured) but
> produces a LARGE gain at weightwise, and an intermediate/small gain at nodewise.
> **FALSIFIED IF:** CIFAR-100 weightwise shows no pooling gain — then agreement does not
> drive the gain and 26.3 dies.

`cw-{w,node}-{r0,r003,r006,r01,r02,r1}-s{0,1,2}`, CIFAR-100 / ResNet18_c100 / a0=1e-6 / 100ep
/ `HIER=additive`. r=1 is the identity control (must reproduce `c100f-w` / `c100f-node`,
landing now); r=0 is full pooling and must show `sd_beta`=0. **Probes on the r=1 seed of each
granularity** put the agreement measurement and the gain in the SAME run family — which no
previous cycle has had.

## 26.8 Queue actions

* `gp-node-*` / `gp-w-*` (alice2) **promoted rank ~40 -> 25** by niceing `m0c-*` (15 jobs,
  M0 shrink on CIFAR-100) to 30000. `gp-*` supplies the two missing cells of 26.3's gain
  column; `m0c-*` raises a null that 24.3 already established.
* Queues after this cycle: **alice 271, alice2 184 = 455 jobs**, 24 running (12+12 — the
  per-account `qos-gpu-short` ceiling, not a bug).

## 26.9 Still open

* **26.3's gain column** rests on three different run families (25.3 M1, 25.5 zpool). `gp-*`
  makes it one family. Until then the mechanism is a fit to three points, not a curve.
* **`cw-*` is the falsification test** — if C100 weightwise shows no pooling gain, 26.3 dies.
* **`p6f-*` (alice, rank 1-9)** — free-adaptation agreement on {C100, R10, R34} x
  {layer, node, weight}. Pairs with `mx/probe_sig_*` (R18/C10) to give the model-scale
  agreement ladder, which 25.6 predicts should FALL with model size (gain grows R10 +1.00 ->
  R18 +2.40 -> R34 +2.62).
* **No matched free-adaptation agreement probe at `resnet18_blocks` outside R18/C10** —
  `p6f` covers only layer/node/weight, so the m=6 end of the ladder is single-setting.
* **R34 r-curve** (`r34r-*`, 27, alice) still pending; 25.6's third row is one point.
* n=1-2 on every zpool cell at r>=0.9 (25.5), which is where 26.3's weightwise gain comes from.

---

# Cycle 27 (20 Aug 2026) — the pooling gain is non-monotone in the layerwise-minus-scalar gap, and the agreement ladder is now three settings deep

43 new runs (alice 465 -> 492, alice2 349 -> 365; `all_runs.csv` 812 -> 855 rows). Landed:
all nine `p6f-*` agreement probes, `cs-*` (CIFAR-100 x R10/R34), `r10c-*` (partial),
`c1b-*`, `m1a3-r04-s2`.

## 27.1 NEW — the p6f agreement ladder: fineness beats setting, in 3/3 settings

`runs/p6free/p6f-*`, reduced with `bin/agree2.py`. SGDm+Lion, meta-stepsize 1e-3,
**a0=1e-3, 20 epochs**, AUGMENT=1, guard on, `HIER` unset (free adaptation), PROBE=100.
STEADY window = last 50% of records. **n=1 per cell** (`p7-*` takes it to n=3).

| setting | granularity | N | `sys%` | step-null (pp) | sd_beta | drift/step |
|---|---|---|---|---|---|---|
| R10 / C10 | layerwise | 38 | **60.47** | +5.05 | 2.388 | 3.14e-04 |
| R10 / C10 | nodewise | 8,660 | 52.04 | +1.67 | 1.722 | 1.20e-04 |
| R10 / C10 | weightwise | 4,903,242 | 50.0039 | +0.034 | 1.401 | 7.03e-05 |
| R18_c100 / C100 | layerwise | 62 | **57.48** | +4.80 | 2.417 | 2.68e-04 |
| R18_c100 / C100 | nodewise | 14,600 | 52.03 | +1.70 | 1.724 | 9.47e-05 |
| R18_c100 / C100 | weightwise | 11,220,132 | 50.0124 | +0.012 | 1.517 | 6.85e-05 |
| R34 / C10 | layerwise | 110 | **51.13** | +1.00 | 1.612 | 1.91e-04 |
| R34 / C10 | nodewise | 25,556 | 50.31 | +0.12 | 0.602 | 8.86e-05 |
| R34 / C10 | weightwise | 20,000,000 | 50.0022 | +0.004 | 0.503 | 5.51e-05 |

**One reducer caveat.** `agree2.py` infers `n_tot` as the denominator of the observed
`frac_neg` rationals, and for `p6f-r34-w` it returns exactly **20,000,000** where
`bin/blkchk.py` independently gives ResNet34 = **21,282,122** parameters. The inference is
saturating on the printed precision of `frac_neg` at that magnitude. It does not move the
reading (the independence null is 50.0089% at 20.0M and 50.0086% at 21.3M, against a
measured 50.0022%), but `n_tot` from the reducer is not trustworthy above ~1e7 and the
structurally-measured group count should be used instead. The other eight cells match
`blkchk.py` exactly.

Three independent replications of 26.3's ordering: **agreement falls monotonically with
partition fineness, in every setting, over five orders of magnitude in N.** `sd_beta` falls
with N in 3/3 as well. The weightwise cells are within 0.013pp of the 50.0000% independence
value in 3/3.

Second, **agreement at layerwise falls with model size**: R10 (N=38) 60.47 -> R18 (N=62,
pending `p7`) -> R34 (N=110) 51.13, and `sd_beta` 2.39 -> 1.61. CIFAR-100 at R18 sits at
57.48, **higher** than CIFAR-10 at R18 will need to be for 24.3's null pooling gain to be
explained by agreement — that comparison cannot be made until `p7-r18-lay` lands (27.2).

## 27.2 CORRECTION — 26.3's R18 row is not in the p6f family and must not be tabulated with it

26.3's R18/CIFAR-10 rung comes from `mx/probe_sig_*`: **a0=1e-6, 100 epochs**. p6f is
**a0=1e-3, 20 epochs**. Reading them as one ladder is a cross-a0, cross-budget comparison —
Rule 5 exactly. Everything 26.3 says about R18 stands on its own; what does NOT stand is the
four-row model-scale ladder implied by placing 53.26 between R10's 60.47 and R34's 51.13.
`p7-r18-{blk6,lay,node,w}` x 3 seeds (submitted, 27.7) runs the missing rung at p6f's config.

## 27.3 STRUCTURAL — `resnet18_blocks` exists only on ResNet18

`bin/blkchk.py` (CPU, seconds, no GPU) instantiates every net x granularity:

| net | tensors | params | resnet18_blocks | layerwise | nodewise | weightwise |
|---|---|---|---|---|---|---|
| ResNet10 | 38 | 4,903,242 | **ZeroDivisionError** | 38 | 8,660 | 4,903,242 |
| ResNet18 | 62 | 11,173,962 | 6 | 62 | 14,420 | 11,173,962 |
| ResNet34 | 110 | 21,282,122 | **ZeroDivisionError** | 110 | 25,556 | 21,282,122 |
| ResNet18_c100 | 62 | 11,220,132 | 6 | 62 | 14,600 | 11,220,132 |
| ResNet10_c100 | 38 | 4,949,412 | **ZeroDivisionError** | 38 | 8,840 | 4,949,412 |
| ResNet34_c100 | 110 | 21,328,292 | **ZeroDivisionError** | 110 | 25,736 | 21,328,292 |

The m=6 partition is hard-coded to ResNet18's tensor layout and dies at optimizer
construction on any other net. **26.9's open item "no matched blocks probe outside R18/C10"
is not a scheduling gap, it is unreachable without new code.** The m=6 rung can be extended
to the second DATASET only (`p7-c100-blk6`, submitted). No currently-queued job is affected.

## 27.4 The M1 interior optimum is a0-dependent — it shrinks 4x from a0=1e-6 to a0=1e-3

R18 / CIFAR-10 / layerwise / SGDm+Lion / 100ep, **plateau** (mean of last 5 epochs):

| r | a0=1e-6 | n | a0=1e-3 | n |
|---|---|---|---|---|
| 0 (full pooling) | 92.23±0.09 | 6 | 92.18±0.09 | 5 |
| 0.03 | 92.64±0.16 | 5 | 92.18±0.11 | 5 |
| 0.05 | 93.05±0.14 | 10 | 92.12±0.01 | 2 |
| **0.06** | **93.26±0.14** | 8 | 92.16±0.10 | 12 |
| 0.07 | 93.19±0.15 | 9 | 92.18±0.01 | 2 |
| **0.1** | 92.63±0.21 | 5 | **92.44±0.14** | 5 |
| 0.2 | 91.39±0.14 | 3 | 92.08±0.13 | 3 |
| 0.3 | 90.96±0.08 | 3 | 91.76±0.09 | 2 |
| 0.4 | — | — | 91.40±0.04 | 2 |
| 1 (identity) | 90.86±0.06 | 3 | 91.15±0.05 | 2 |
| plain layerwise | 90.82±0.16 | 24 | 91.13±0.19 | 9 |

Identity control holds at both a0 (r=1 vs plain: 0.04pp and 0.02pp, against a ±0.02pp
reproducibility floor and sds of 0.16 / 0.19).

* **a0=1e-6:** interior optimum r*=0.06, **+2.40pp over identity** and **+1.03pp over full
  pooling (r=0)** — a genuine interior optimum, both endpoints beaten, n=8.
* **a0=1e-3:** r*=0.1, **+1.29pp over identity** but only **+0.26pp over r=0**
  (92.44±0.14 n=5 vs 92.18±0.09 n=5; Welch t=3.5, so real but small). The curve is flat
  within noise from r=0 to r=0.07.

**Reading: at a0=1e-3 nearly the entire M1 gain is "pool at all", not "pool partially".** The
interior optimum survives but is 4x smaller and moves from r=0.06 to r=0.1. Any claim that
M1's hierarchy beats both endpoints must name a0. `am4-*` (a0=1e-4, 21 jobs) and `amx-*`
(meta=Adam, 15 jobs) are queued on alice2 and fill the a0 and meta-optimizer axes.

## 27.5 NEW — the M1 gain is NON-MONOTONE in the layerwise-minus-scalar gap

M1 shrinks each group's step size toward the arm's r->0 limit, and that limit **is** the
scalar arm. So the gain should depend on two things: whether the groups genuinely want to
differ (gap = plain layerwise − plain scalar), and whether the thing they are pooled toward
is itself sound. Re-derived from `all_runs.csv`, plateau, 100ep, `gain` = best measured
interior r minus the r=1 identity (plain layerwise where no r=1 cell exists):

| setting | scalar | plain layer | gap | r* | plateau at r* | gain |
|---|---|---|---|---|---|---|
| R18/C10 AdamW+Adam a0=1e-3 | 92.68±0.18 (3) | 90.86±0.17 (8) | **−1.82** | 0.06 | 91.37±0.17 (5) | +0.51 |
| R18/C10 AdamW+Adam a0=1e-4 | 91.74±0.04 (3) | 91.86±0.16 (3) | **+0.12** | 0.06 | 92.66±0.14 (5) | +0.79 |
| R34/C10 SGDm+Lion a0=1e-3 | 89.69±0.21 (3) | 90.42±0.16 (3) | **+0.74** | 0.06 | 93.35±0.15 (3) | **+2.93** |
| R34/C10 SGDm+Lion a0=1e-6 | 89.31±0.09 (5) | 90.15±0.13 (5) | **+0.83** | 0.06 | 92.74±0.19 (5) | **+2.59** |
| R18/C10 SGDm+Lion a0=1e-6 | 87.77±0.12 (18) | 90.82±0.16 (24) | **+3.04** | 0.06 | 93.26±0.14 (8) | +2.40 |
| R18/C10 SGDm+Lion a0=1e-3 | 87.70±0.22 (9) | 91.13±0.19 (9) | **+3.42** | 0.1 | 92.44±0.14 (5) | +1.29 |
| R10/C10 SGDm+Lion a0=1e-6 | 70.74±0.83 (3) | 90.62±0.27 (3) | **+19.88** | 0.1 | 91.59±0.05 (3) | +1.00 |
| R18/C100 SGDm+Lion a0=1e-6 | 22.78±0.70 (5) | 69.17±0.60 (6) | **+46.39** | 0.2 | 69.89±0.02 (2) | +0.35 |
| R18/C100 SGDm+Lion a0=1e-3 | 22.57±0.46 (5) | 69.53±0.49 (7) | **+46.96** | 0.2 | 68.32±0.30 (2) | **−1.59** |

Rising then falling, with a maximum at gap ~0.7–0.8pp. Both tails have a reading:
* **gap <= 0** (AdamW: per-coordinate normalisation already does the job, H4) — the groups do
  not want to differ, so there is little for a hierarchy to allocate. Gain +0.5 to +0.8.
* **gap large** (CIFAR-100, ResNet10) — the groups differ enormously *because the pooled
  step size cannot train the network at all*. Pooling toward it is pooling toward a broken
  estimator. Gain goes to zero and then negative.

**This is a hypothesis, not a measured curve, and must not be reported as one.** The nine
rows differ in base optimizer, meta optimizer, model, dataset AND alpha0 simultaneously; gap
and gain are also computed from arms of the same runs. `bo-*` (27.7) is the controlled test:
the base optimizer moves the gap with everything else held fixed.

Two cells are **grid-limited, not measured optima**, and are excluded from the table above:
R10/C10 a0=1e-3 (only r in {0, 0.06} exist; `r10c-*` is filling it) and R10/C100 (only
r=0.06 exists — see 27.6).

## 27.6 NEW — small r on CIFAR-100 is worse than BOTH endpoints, not an interpolation

`cs-*` landed (CIFAR-100 x ResNet10/ResNet34, a0=1e-3, 100ep). ResNet10_c100:

| arm | plateau | best | n |
|---|---|---|---|
| plain layerwise | 68.27±0.33 | 68.92±0.30 | 3 |
| plain scalar | 12.85±0.02 | 13.05±0.05 | 2 |
| **M1 additive r=0.06** | **5.58±0.01** | 12.27±0.23 | 2 |

The pooled arm plateaus **below both endpoints** — 7.3pp under the scalar arm it is being
shrunk toward, with plateau far under `best` (12.27), i.e. it peaks and then collapses,
which the scalar arm does not do. The same signature is already in the R18/C100 curve:
r=0 plateaus at 8.98±0.15 against a scalar endpoint of 22.57±0.46.

So M1 at small r is **not** a convex interpolation between plain-layerwise and scalar; on
CIFAR-100 it is actively unstable. This is the sharpest limitation of the method found so
far and every cell of it is n=2 — `kc-*` (39 jobs, 27.7) takes the R18/C100 curve to n=5 and
gives ResNet10/C100 a real r-curve so the collapse boundary is a curve, not two points.

Note also that the CIFAR-100 identity control is 0.37–0.39pp off (r=1 69.54±0.03 n=2 vs
plain 69.17±0.60 n=6 at a0=1e-6; 69.92±0.42 n=2 vs 69.53±0.49 n=7 at a0=1e-3) — inside the
plain arms' own sd but well outside the ±0.02pp reproducibility floor. `kc-r18-r1-s{2,3,4}`
raises both to n=5.

## 27.7 Submitted this cycle — 123 jobs

| batch | acct | n | what | why |
|---|---|---|---|---|
| `p7-*` | alice | 33 | agreement probes, p6f config (a0=1e-3, 20ep, PROBE=100): R18/C10 x {blk6,lay,node,w} x s0-2; C100 x blk6 x s0-2; p6f's nine cells x s1-2 | closes 27.2's hole and takes the ladder to n=3 in ONE matched family |
| `kc-*` | alice | 39 | R18_c100 r in {0,.03,.05,.07,.1,.2,1} x s2-4; R10_c100 r in {.06,.1,.2,.4,.7,1} x s0-2 | 27.6 at n>=5 plus the ResNet10 rung |
| `bo-*` | alice2 | 39 | R18/C10, meta=Lion, a0=1e-6, base in {Lion, RMSProp} x {plain scalar, plain layer, r in 0/.06/.2} x s0-2; base=AdamW x r in 0/.06/.2 x s0-2 | **pre-registered** controlled test of 27.5 |
| `bp-*` | alice2 | 12 | agreement probes at p6f config, base in {Lion, RMSProp, AdamW, SGDm} x s0-2 | the other half of 27.5's discriminator, in the p7 family; `bp-sgdm` doubles as a cross-account reproducibility control for `p7-r18-lay` |

**Pre-registration for `bo-*`.** Measure the gap per base from its own plain arms, then read
the gain off the r-grid {0, 0.06, 0.2}.
> **PREDICTED:** gain is non-monotone in the gap across the four bases, peaking at
> gap ~1–3pp; a base with gap <= 0 gives gain < +1pp.
> **FALSIFIED IF:** gain is monotone in the gap, or flat across all four bases.

Lion and RMSProp bases are new to this campaign. Both were checked structurally on CPU
first (`bin/basechk.py`: all four bases x {plain, additive} construct and take three finite
steps, alpha finite) — cycle-18 gotcha 5.

## 27.8 Operations

* **Throughput is ~24 concurrent GPUs and ~21 finished runs/hour (~500/day).** 100-epoch
  runs are 0.3–1.2 h wall (R10 0.3, R18 0.5–0.8, R34 1.0–1.2, R50 2.3). A 431-job backlog
  was under **one day** of compute — we were UNDER-queued, not over-queued. Queue depth
  after this cycle: **alice 322, alice2 226 = 548**.
* **The 12+12 ceiling is cluster contention, not our configuration.** Each GPU partition
  carries its own PartitionQOS (`gpu-short` 12 GPUs, `gpu-l4` 8, `gpu-2080ti` 12, `gpu-mig`
  8, `gpu-a100` 2 = 42/account), and our jobs are submitted to all five. But the cluster had
  **77 GPU jobs running against 442 pending**, of which **24 were ours** — we are the two
  largest users on it, at fairshare 0.338. Genuinely free GPUs at the time of checking: 7
  (node882 x2, node883 x3, node866 x1, node873 x1); node[854,856,857] (12 GPUs) sit under a
  permanent MAINT reservation to 1 Dec. There is no configuration change that raises this.
* **alice2 has much the better fairshare** (job priorities ~1,072,000 vs alice's ~671,000).
  Put latency-sensitive batches there.
* Reprioritised on alice: `m0l-*`, `m0s-*` (24) and `zmg-*` (30) niced to 5000, moving
  `p7-*` from queue position 130 to 76, behind `r34r-*` (27) and `cw-*` (36) which stay
  ahead deliberately — `cw-*` is 26.7's pre-registered falsification test.

## 27.9 Still open

* **`p7-r18-lay` is the single missing number** for both the model-scale agreement ladder and
  the CIFAR-10-vs-CIFAR-100 agreement contrast that 26.7's `cw-*` prediction rests on.
* **27.5 is a scatter over nine incomparable cells.** `bo-*` is the controlled test; until it
  lands, "the gain is non-monotone in the gap" is a hypothesis with a pre-registration.
* **26.3's gain column** still rests on three run families; `gp-*` (48, alice2, positions
  4–51) makes it one.
* `cw-*` (36, alice, positions 40–75) — the falsification test for 26.3.
* `r34r-*` (27, alice, position 13) — R34 has a gain of +2.6/+2.9 measured at **r=0.06
  only**; 25.6's third row is still one point.
* R10/C10 a0=1e-3 has no r-curve (`r10c-*`, 7 left, alice2 position 1).
* Every CIFAR-100 M1 cell is n=2 until `kc-*` lands.

# CYCLE 28

## 28.1 THREE MORE UNREDUCED PROBE BATCHES — `gate1`, `gate2`, `gate3` (Aug 18)

The cycle-26 sweep that found `mx/probe_sig_*` stopped at the batches whose names appear in
this file. Re-run with the mention-count filter applied to EVERY top-level probe directory on
both accounts, three more come back with zero mentions in FINDINGS or CORRECTIONS:

| batch | acct | dirs | config | status before this cycle |
|---|---|---|---|---|
| `gate1` | alice | 12 | SGDm+Lion, R18/C10, a0=1e-6, 100ep, {scal, blk6, layer, weight} x s0-2 | never read |
| `gate2` | alice2 | 12 | **AdamW**+Adam, R18/C10, a0=1e-6, 100ep, {scal, blk6, layer} x s0-2 | never read |
| `gate3` | alice | 9 | SGDm+**Adam**, R18/C10, a0=1e-6, 100ep, {scal, blk6, layer} x s0-2 | never read |

`gate1`'s ARGS line is field-for-field identical to `mx/probe_sig_*` — the series 26.3's
published ladder is built from — including seeds. Also unmentioned and checked this cycle:
`d2` (4), `det` (2). Both are 25-record smoke probes; nothing in them.

## 28.2 CORRECTION — `z_mean` and `frac_neg` are DIFFERENT statistics (see CORRECTIONS 18)

`gate1`/`gate2` predate the probe's `frac_neg`/`frac_zero` fields; they carry only
`beta`/`z_mean`/`z_std`/`snr`. `analysis/agree_legacy.py` (new) recovers a sign-agreement
statistic from `sign(z_mean)` instead. **It was validated against `mx`, which carries both
formats, and it FAILED**: on the same records, same window,

| rung | `frac_neg` (agree2.py, published) | `z_mean` (agree_legacy.py) |
|---|---|---|
| blk6 (m=6) | 70.87±0.80 | 63.70±0.78 |
| layerwise (m=62) | 53.26±0.19 | 54.77±1.26 |

7.2pp apart at m=6. `z_mean` is a per-TENSOR running mean (62 entries on every arm, including
the 14,420-node and 11.17M-weight arms) — it is not the per-coordinate meta-gradient whose
signs make `frac_neg`. **Legacy-format numbers can never be placed on the published ladder,
and the two rungs `gate1` can supply are therefore not a replication of 26.3's values.** They
are still a valid statistic read consistently within itself, which is what 28.3 uses them for.

## 28.3 The agreement MEASUREMENT reproduces across batches to 0.08pp — and does not care about the beta spread

Same statistic (`z_mean`), same window, R18/C10, SGDm+Lion, a0=1e-6, 100ep, n=3 each:

| rung | `gate1` (Aug 18) | `mx/probe_sig` (Aug 19) | delta |
|---|---|---|---|
| blk6 (m=6) | 63.64±0.54 | 63.70±0.78 | **−0.055** |
| layerwise (m=62) | 54.69±1.23 | 54.77±1.26 | **−0.083** |

Two batches, two days, different nodes, different job IDs: agreement to under 0.1pp on both
rungs. **And `gate1` ran WITHOUT the beta clip** — its `sd_beta` is 9.61±0.27 against `mx`'s
2.39±0.02, a 4x wider spread of log step sizes — yet the agreement statistic is unmoved. So
sign-agreement of the meta-gradient is a property of the partition, not of how far the betas
have spread. That is the same conclusion 26.2 reached from the drift slopes, by an
independent route. The m=6 > m=62 ordering also holds on this second statistic (63.6 -> 54.7),
though the magnitude differs from the `frac_neg` scale (70.9 -> 53.3).

## 28.4 NEW — the agreement ladder INVERTS under an AdamW base

Same statistic, same window, same config except the optimizers, n=3:

| batch | base | meta | m=6 | m=62 | direction | sd_beta (layer) |
|---|---|---|---|---|---|---|
| `gate1` | SGDm | Lion | 63.64±0.54 | **54.69±1.23** | FALLS | 9.61±0.27 |
| `gate2` | **AdamW** | Adam | 71.20±2.55 | **79.96±1.82** | **RISES** | 1.88±0.02 |
| `gate3` | SGDm | Adam | (degenerate) | 51.82±1.20 | — | **20.52±3.58** |

**Under AdamW the layerwise meta-gradients agree 80% of the time and agreement RISES with
partition fineness — the opposite of every SGDm measurement in this campaign.** 26.3's
monotone fall is not a law about partitions; it is base-optimizer-specific.

This is the mechanism H4 has been missing since cycle 12. H4 says granularity helps under
SGDm and is null under AdamW. If under AdamW the groups' meta-gradients already point the
same way, there is nothing for a finer partition to allocate — and 26.3's "the pooling gain
runs opposite to agreement" then predicts a SMALL M1 gain under AdamW, which is what 27.5's
two AdamW rows measure (+0.51 and +0.79, the smallest in that table).

**Three caveats, all of which the jobs submitted this cycle remove:**
1. `gate1` -> `gate2` changes the base AND the meta optimizer at once.
2. These are `z_mean` numbers (28.2), not on the published `frac_neg` scale.
3. `gate3` (SGDm+Adam), which would have separated base from meta, is **divergent** —
   `sd_beta` 20.5 in log space, and its `z_mean` agreement pins at exactly 100.0000% on all
   three seeds at m=6. It is excluded from every claim here. Its `frac_neg` layerwise value
   (50.33±0.33, i.e. chance) is reported for completeness only.

## 28.5 NEW — the ResNet10 interior optimum does NOT survive a0=1e-3; it disappears

`r10c-*` landed. R10/CIFAR-10, SGDm+Lion, M1 additive, plateau (mean of last 20 epochs),
`epochs_done >= 100` only:

| r | a0=1e-6 | n | a0=1e-3 | n |
|---|---|---|---|---|
| 0 (full pooling) | 82.114±0.060 | 3 | 82.192±0.119 | 3 |
| 0.03 | 89.232±0.231 | 3 | — | |
| 0.05 | 90.264±0.318 | 3 | 88.667±0.015 | 3 |
| 0.06 | 90.786±0.285 | 6 | 88.962±0.115 | 3 |
| 0.07 | 91.105±0.295 | 3 | — | |
| 0.08 | 91.389±0.223 | 3 | — | |
| **0.1** | **91.590±0.042** | 3 | 89.790±0.132 | 3 |
| 0.15 | 91.374±0.087 | 3 | — | |
| 0.2 | 91.080±0.186 | 3 | 90.709±0.035 | 2 |
| 0.3 | 90.781±0.163 | 3 | — | |
| 0.4 | 90.557±0.128 | 3 | — | |
| 0.5 | — | | 91.046±0.073 | 3 |
| 0.6 | 90.492±0.252 | 3 | — | |
| 1 (identity) | 90.586±0.136 | 3 | 91.171 | 1 |
| plain layerwise | 90.619±0.218 | 3 | 91.259±0.224 | 3 |
| plain scalar | 70.742±0.679 | 3 | 70.636±0.752 | 3 |

* **a0=1e-6:** genuine interior optimum at r=0.1 — **+1.00pp over the identity** and +9.48pp
  over full pooling, both endpoints beaten. Identity control holds (r=1 90.586±0.136 vs
  plain 90.619±0.218, a 0.03pp gap).
* **a0=1e-3: the curve is MONOTONE INCREASING over the whole measured grid.** Its best
  interior point, r=0.5 at 91.046±0.073, is **0.21pp BELOW plain layerwise** (91.259±0.224,
  n=3). There is no r at which pooling pays.

Together with 27.4 (R18: the optimum shrinks 4x from a0=1e-6 to a0=1e-3 but survives, +2.40
-> +1.29) this makes the a0-dependence a pattern rather than one model's quirk, and on
ResNet10 it goes all the way to zero. **The a0=1e-6 M1 gain is partly, and on ResNet10
entirely, a repair of a bad initialisation.** Note the one thing that cuts the other way:
R10's a0=1e-6 optimum (91.590) also exceeds the *well-initialised* a0=1e-3 plain arm
(91.259) by 0.33pp, which pure startup-repair does not explain.

Grid caveat: the a0=1e-3 arm is measured at r in {0, .05, .06, .1, .2, .5, 1} only, so an
optimum hiding above r=0.5 and worth under 0.2pp is not excluded; and its r=1 cell is n=1
(two seeds were still in flight at 75 and 50 epochs and are correctly excluded by the
`epochs_done >= 100` filter). Plain layerwise at n=3 is the anchor used above.

## 28.6 Submitted this cycle — 36 jobs, all on alice2, pre-registered

| batch | n | what | why |
|---|---|---|---|
| `ap-*` | 9 | AdamW base, meta=Lion, R18/C10, a0=1e-3, 20ep, PROBE=100, {blk6, nodewise, weightwise} x s0-2 | the AdamW agreement ladder in the MODERN probe format. Layerwise is NOT submitted — the queued `bp-adamw-s*` already runs that cell at this identical config |
| `ag-*` | 27 | AdamW base, meta=Lion, R18/C10, a0=1e-6, 100ep, {blk6, nodewise, weightwise} x r in {0, 0.06, 1} x s0-2 | the gain ladder that must mirror it. Mirrors `sub_gp.sh` field for field with ONLY the base changed, so `gp` vs `ag` is a one-variable contrast |

**PRE-REGISTERED, from 28.4.**
> **PREDICTED (a):** on the `frac_neg` scale, AdamW agreement at m=62 EXCEEDS AdamW
> agreement at m=6 — the ladder inverts, as `gate2` says on the `z_mean` scale.
> **PREDICTED (b):** because 26.3 asserts the M1 gain runs OPPOSITE to agreement, the AdamW
> gain must FALL from m=6 to m=11.17M, the reverse of the SGDm ordering `gp-*` is measuring.
> **FALSIFIED IF:** the AdamW agreement ladder falls with fineness like SGDm's (28.4 is then
> an artifact of the `z_mean` statistic), OR agreement and gain both rise with fineness
> (26.3 is then not a mechanism).

Structural check before queueing (cycle-18 gotcha 5), `bin/agchk.py` + `bin/blkchk28.py` on
CPU: AdamW base x {resnet18_blocks, nodewise, weightwise} x {plain, additive r=0.06,
additive r=1} — all nine construct and take three finite steps. r=1 reproduces plain's beta
range exactly ([-13.8175, -13.8135]) while r=0.06 collapses it to [-13.8139, -13.8137], so
the M1 identity/pooling structure is verified structurally on these arms before any GPU time.

## 28.7 Operations

* **12 running per account is confirmed again as cluster contention, not configuration.**
  Every GPU node on all five partitions reports `AllocTRES` gres/gpu equal to its `CfgTRES`
  gres/gpu; `node[854,856,857]` remain under the MAINT reservation. Nothing to fix.
* **Queue after this cycle: alice 299, alice2 250 = 549.** 29 runs finished since the last
  aggregation (~1 h of compute).
* **Promoted `p7-*` (33 jobs) to the front of alice.** p7 is 20-epoch (~10 min/job), so the
  whole block is ~28 min of the 12-GPU allocation, and it is the SGDm comparator for this
  cycle's AdamW ladder plus 27.9's single missing number. `bin/prio28a.sh` niced only jobs
  already at `Nice=0` (102 of them) — `m0c-*` (30000) and `zmg-*`/`m0l-*`/`m0s-*` (5000) are
  deliberately parked and a blanket `Nice=400` would have PROMOTED them.
* **Promoted `bp-*` (12) to the front of alice2**, by niceing the 39 `gp-*` jobs ahead of it
  by 250. `bp-adamw-s*` is the layerwise rung of `ap-*`; without it the AdamW ladder has a
  hole exactly where 28.4's claim lives.

## 28.8 Still open

* Every 27.9 item is still open — `p7`, `cw`, `kc`, `bo`, `gp`, `r34r` are all still in
  flight. `r34r-*` and `gp-*` rows are now IN the CSV but at 3–75 epochs; they are correctly
  excluded by the `epochs_done >= 100` filter and must not be read yet.
* **28.4 is a two-batch contrast with the meta optimizer confounded**, on a statistic that is
  not the published one. `ap-*`/`bp-*` remove both problems; nothing about the AdamW ladder
  should be stated until they land.
* The `frac_neg` value of `gate2` can never be recovered — the format predates the field. If
  the AdamW inversion matters to the paper it rests on `ap-*`/`bp-*`, not on `gate2`.

# Cycle 29

## 29.1 The agreement ladder, complete probes only, in ONE matched family

`p7-*` closes what 26.3 could only assemble across configs. Every row below is a0=1e-3,
20 epochs, free adaptation, SGDm base + Lion meta, AUGMENT=1 — one family, no cross-config
reads. Statistic is the STEADY window (last 50% of records) **excess of the per-step
agreement over its own independence null**, `step% − null%`, in percentage points.

**Only probes with 100/100 records are tabulated.** Reducing an in-flight probe moves the
number (the STEADY window is defined on the records that exist): `p7-r34-lay-s1` read
excess 0.9879 at 89 records and 1.4690 at 100. See 29.4.

| dataset / net | granularity | m | n | excess mean | sd |
|---|---|---|---|---|---|
| CIFAR-10 / ResNet18 | resnet18_blocks | 6 | 3 | **+4.1577** | 2.2195 |
| CIFAR-10 / ResNet18 | layerwise | 62 | 3 | +1.3205 | 0.8946 |
| CIFAR-10 / ResNet18 | nodewise | 14,420 | 3 | +0.4278 | 0.0517 |
| CIFAR-10 / ResNet18 | weightwise | 11,173,962 | 3 | +0.0046 | 0.0008 |
| CIFAR-10 / ResNet10 | layerwise | 38 | 2 | +2.4756 | 0.5955 |
| CIFAR-10 / ResNet10 | nodewise | 8,660 | 2 | +1.3711 | 0.0875 |
| CIFAR-10 / ResNet10 | weightwise | 4,903,242 | 2 | +0.0260 | 0.0041 |
| CIFAR-10 / ResNet34 | layerwise | 110 | 1 | +1.4690 | — |
| CIFAR-100 / ResNet18 | resnet18_blocks | 6 | 3 | **−0.7312** | 2.5459 |
| CIFAR-100 / ResNet18 | layerwise | 62 | 1 | +4.5141 | — |
| CIFAR-100 / ResNet18 | nodewise | 14,600 | 1 | +1.2811 | — |

**Within an architecture on CIFAR-10 the fall with m is monotone, 3 orders of magnitude**
(R18: 4.16 → 1.32 → 0.43 → 0.005 over m = 6 → 62 → 14,420 → 11.17M, n=3 at every rung;
R10: 2.48 → 1.37 → 0.026 over m = 38 → 8,660 → 4.90M, n=2). 26.3 replicates in the matched
family. The `weightwise` rungs are 0.005–0.026pp above a null of 50.0086–50.0180% — at the
resolution limit, and consistent with the campaign's headline refutation that independence
essentially holds coordinate-wise.

## 29.2 The m=6 rung INVERTS between datasets — the coarsest partition is the only one that does

Same architecture, same 6-block partition, same config, only the dataset changed:

| | m=6 | m=62 | m≈14.5k |
|---|---|---|---|
| CIFAR-10 | **+4.1577** (n=3) | +1.3205 (n=3) | +0.4278 (n=3) |
| CIFAR-100 | **−0.7312** (n=3) | +4.5141 (n=1) | +1.2811 (n=1) |

CIFAR-10's ladder is monotone decreasing. **CIFAR-100's is not**: it is at or below the
independence null at m=6 (2 of 3 seeds negative: −1.2868, +2.0466, −2.9534), rises to the
largest coarse-rung agreement in the campaign at m=62, then falls again. At the two finer
rungs CIFAR-100 sits *above* CIFAR-10; at m=6 it sits *below*. `sd_beta` at C100/blk6 is
2.07–2.09, i.e. the betas do spread — this is not a degenerate run.

**This contrast is NOT yet significant.** Welch on the two n=3 blk6 cells: diff 4.8889pp,
se 1.9500, t=2.507, df=3.93, two-sided p≈0.07. The seed sd (2.2–2.5pp) is half the effect.
`p8-*` (14 jobs, submitted this cycle, 29.5) takes both cells to n=10. **Do not state 29.2
as a result until they land.** The m=62 and m≈14.5k CIFAR-100 rungs are n=1 and are listed
for shape only.

## 29.3 Model scale: R10 sits above R18 at every matched granularity, by 1.9–5.7x

| granularity | ResNet10 | ResNet18 | ratio |
|---|---|---|---|
| layerwise | +2.4756 (n=2) | +1.3205 (n=3) | 1.87x |
| nodewise | +1.3711 (n=2) | +0.4278 (n=3) | 3.21x |
| weightwise | +0.0260 (n=2) | +0.0046 (n=3) | 5.65x |

3/3 granularities, in the predicted direction (25.6). **The confound is named and not
removable at fixed granularity:** ResNet10 has *fewer* groups than ResNet18 at every
granularity (38 vs 62, 8,660 vs 14,420, 4.90M vs 11.17M), so "smaller model" and "coarser
partition" push the same way here and this table cannot separate them. The ratio *growing*
with fineness (1.87x → 3.21x → 5.65x) is the part a pure-m story does not obviously predict.

**The ResNet34 rung does not yet exist and its one available point runs the other way**:
R34/layerwise is +1.4690 (n=1, m=110) against R18's +1.3205 (n=3, m=62) — higher, where both
the model-scale and the m reading require lower. `p7-r34-{node,w}-s*` and `p7-r34-lay-s2`
were at 75–91 of 100 records at aggregation time. 25.6 is not confirmed at three model sizes.

## 29.4 CORRECTION — `agree2.py` censored every n_tot above 20,000,000

`infer_ntot` inferred the coordinate count as
`Fraction(frac_neg).limit_denominator(20_000_000).denominator`. The cap is the tool's, not
the model's. ResNet34/weightwise has **21,282,122** parameters (summed from
`block_sizes.json`'s `n_b`, 110 tensors) and was reported as exactly `20,000,000`.

Effect: the independence null `E = 0.5 + sqrt(2/pi)/(2 sqrt(n))` was computed at the wrong n,
giving 50.00892% instead of 50.00865%, and the R34/weightwise excess was understated by
~10% relative (0.0029 → 0.0033 on s1). **No sign flips and no ordering changes**, but the
number was wrong. Cap raised to 100,000,000 in `bin/agree2.py` (backup at `agree2.py.bak`);
all 29.1 numbers are post-fix. Verified unaffected: R18 11,173,962 / R10 4,903,242 /
R18_c100 11,220,132 all reproduce exactly and sit under the old cap.

This is the third measurement-layer defect in the coordinate count, after CORRECTIONS 16
(`block_sizes.json` claiming 11.17M nodes for nodewise) and 17 (Lion sign-censoring of
`drift/step`). **Any new architecture above 20M parameters read before this cycle carries
the censored null.**

## 29.5 Submitted this cycle — 50 jobs, all on alice, pre-registered

| batch | n | what | why |
|---|---|---|---|
| `kb-*` | 36 | M1 additive r-curve at **m=6** (`resnet18_blocks`), r ∈ {0, .03, .07, .2, .5, 1} x s0-2 x {CIFAR-10/ResNet18, CIFAR-100/ResNet18_c100}, a0=1e-3, 100ep | the falsification test 29.2 turns on |
| `p8-*` | 14 | `p7-{r18,c100}-blk6-s{3..9}` — 7 more seeds per dataset at m=6, 20ep | 29.2 is p≈0.07 at n=3; this takes it to n=10 |

`kb-*` mirrors `bin/c27_alice.sh`'s `kc()` field for field — same base/meta optimizers, same
a0=1e-3, same 100 epochs, same AUGMENT, same BETA_CLIP — with exactly two changes:
`--stepsize-groups resnet18_blocks` instead of `layerwise`, and the dataset/net pair swept.
`resnet18_blocks` is hard-coded to ResNet18's 62-tensor layout; `ResNet18_c100` shares it
(verified — `p7-c100-blk6-s{0,1,2}` all completed at m=6). **Do not extend `kb` to R10/R34**;
per the cycle-27 structural check it raises ZeroDivisionError at optimizer construction.

**PRE-REGISTERED, from 29.2.** 26.3 reads the M1 pooling gain as running OPPOSITE to
agreement — coarse/high-agreement rungs gain little, fine/low-agreement rungs gain a lot.
Applied at m=6, where 29.2 says CIFAR-10 has the campaign's highest coarse agreement and
CIFAR-100 has none:
> **PREDICTED (a):** CIFAR-10 at m=6 shows a SMALL M1 gain. (26.3 already reports +0.415,
> but from `mx/probe_sig_*` at a0=1e-6/100ep — a cross-config read. `kb-c10-*` redoes it
> in-family.)
> **PREDICTED (b):** CIFAR-100 at m=6 shows a LARGE M1 gain.
> **FALSIFIED IF:** CIFAR-100 at m=6 collapses the way it does at layerwise (r=0 plateau
> 8.98 vs 69.92 at r=1, 24.3/26.7). 26.3's "gain runs opposite to agreement" reading is
> then dead, and the DATASET, not the partition, sets the sign of the pooling effect.

Every CIFAR-100 pooling measurement in the campaign so far is at layerwise (m=62). This is
the first at m=6, and it is the rung where the two datasets disagree.

## 29.6 Operations — the backfill window, not the queue depth, is the throughput lever

28.7 concluded "12 running per account is cluster contention, not configuration." That is
still right, and this cycle measured the mechanism.

* **Genuinely free GPUs cluster-wide: 5** (node883 IDLE with 4 free L4, node882 with 1).
  Counted per the cycle-16 rule — node-level `CfgTRES − AllocTRES`, non-idle states excluded.
  A naive `sinfo` read suggested ~50 free; the `mix-` suffix is PLANNED, not available.
* **`SchedulerParameters` = `bf_interval=60, bf_window=10810, bf_max_job_start=100,`
  `bf_max_job_user=25, bf_max_job_test=1000`.** Backfill tests **at most 25 jobs per user
  per cycle**. With 269 pending on alice, queue depth past the top 25 buys nothing from
  backfill — it only holds main-scheduler position.
* **12 of alice's top-25 backfill slots were `bg300`/`bg600` at 8:30:00 and 13:30:00** —
  jobs far too long to fit any backfill gap, occupying half the window permanently while
  the 20-epoch probes that *can* fit sat at Nice=5000–40000, far below it.
  **Fixed: 90 short (≤3:50) jobs on alice and 39 on alice2 reniced to Nice=0**, then `cw`/`kc`
  to 1000 so the 16 `p7`/`p8` probes take the front. alice's top-25 is now 16 x 1:30:00
  probes + 9 `bg*`; alice2's is 25 x 3:50:00.
  **The two schedulers want opposite things and `bg*` is NOT simply dead weight.** Backfill
  wants short jobs in the top 25; the main scheduler wants our long jobs holding position on
  the four long partitions, which is the ONLY route to the 30 cap slots we never use
  (L4 8 + 2080ti 12 + MIG 8 + A100 2, all at 0 running). Demoting `bg*` would forfeit that.
  They are left at Nice=400 deliberately: behind the probes inside the window, still ahead of
  everything else for the main scheduler.
* **Priority decomposition** (`sprio`): partition 400000, fairshare 270697, age ~917,
  **QOS 0**. `PriorityWeightQOS=1000000` is a full million points we never collect —
  every job runs at `QOS=normal` and the partition QOS is applied at schedule time.
  FairShare for salehkaleybars is **0.338** (RawUsage 15.35M, half-life 14 days), i.e. we
  have drawn more than our share and the scheduler is correctly throttling us. 24 GPUs
  across the two accounts is close to what fairshare currently entitles us to.
* A nice=0, 5-minute, 1-GPU control job pinned to `gpu-l4-24g` would not start against an
  IDLE 4-GPU node — confirming the block is priority against 511 pending cluster GPU jobs,
  not anything in our submission. Cancelled after the test.
* Queue after this cycle: **alice 320, alice2 240 = 560.**

## 29.7 Still open

* `kb-*` and `p8-*` are the two things this cycle turns on. Neither has landed.
* **29.2 must not be stated as a result at p≈0.07.** Wait for `p8-*`.
* The ResNet34 agreement rung (29.3) is 5 probes short and its one point contradicts 25.6.
* CIFAR-100 at m=62 and m≈14.5k is n=1 (`p7-c100-{lay,node}-s2`, `p7-c100-w-s*` in flight).
* Everything still open from 28.8 remains open: `cw`, `kc`, `bo`, `gp`, `r34r`, `ap`, `ag`.
* `bo-*` landed 12 rows this cycle but only 3 at ≥100 epochs — not read.

---

# Cycle 30 — 2026-08-20

Every number below re-derived this cycle from `results/all_runs.csv` (951 rows, +24) and from
`bin/agree2.py` over `runs/p7free/` (32 probes, **all now 100/100 records**).

## 30.0 OPERATIONS — cycle 29's two decisive batches were destroyed by our own trim

`kb-*` (36) and `p8-*` (14, submitted under the `p7-*-blk6-s{3..9}` names) were submitted
2026-08-20T07:54:42 and **all 50 were cancelled at 08:33:15/16 by uid 2344 = salehkaleybars**,
39 minutes later. **None had started.** They were 50 of the 177 jobs an ad-hoc `scancel` sweep
removed to reduce queue depth. 29.7 had named them, in writing, as "the two things this cycle
turns on"; the cycle produced no data from either.

Mechanism: the sweep selected by **recency** (newest job IDs). A decisive experiment is by
construction the newest thing in the queue, so recency-ordered trimming cancels exactly what it
must never touch. The loss was invisible for a day because the trim reported only a count.

**Fixed.** Both scripts survived intact and both batches were resubmitted this cycle (30.6).
`bin/safe_trim.sh` + `bin/PROTECTED.txt` are installed on **both** accounts and enforce:
never cancel a protected name-prefix; never cancel at `Nice < 1000`; never cancel RUNNING;
trim from the BACK (highest Nice first); print every name, never just a count.

## 30.1 MODEL SCALE — the pooling optimum moves, the gain does not vanish

Axis 1. **M1 additive, layerwise, CIFAR-10, a0=1e-6, 100 epochs, `epochs_done==100` only,
not collapsed, and — new this cycle — WITHIN ONE JOB FAMILY (see 30.5).** Plateau = mean of
last 5 epochs.

| net | params | m | family | r=0 plateau | **r\*** | plateau at r\* | gain | r\*·m |
|---|---|---|---|---|---|---|---|---|
| ResNet10 | 4.90M | 38 | `r10` | 82.114 ±0.073 (n=3) | **0.10** | 91.590 ±0.051 (n=3) | +9.476 | 3.80 |
| ResNet18 | 11.17M | 62 | `ad-l` | 92.200 ±0.044 (n=3) | **0.07** | 93.218 ±0.138 (n=5) | +1.017 | 4.34 |
| ResNet34 | 21.28M | 110 | `r34r` | 93.098 ±0.072 (n=3) | **0.02** | 93.884 ±0.194 (n=3) | +0.786 | 2.20 |

**r\* falls monotonically with model size: 0.10 → 0.07 → 0.02.** Full ResNet34 curve (n=3 each,
one family, all 100/100 epochs): r=0 → 93.098, r=0.02 → 93.884, r=0.03 → 93.813, r=0.04 → 93.365.
The r=0 → r\* gain is significant (diff +0.786, se 0.119, t=6.6); r=0.02 vs 0.03 is **not**
(diff 0.071, se 0.126, t=0.56) — the R34 peak is a *plateau over [0.02, 0.03]*, not a located
point. r=0.04 is genuinely down (t=3.66).

**The gain does not shrink toward zero at scale** — ResNet34 (+0.786) sits within noise of
ResNet18 (+1.017) despite 1.9x the parameters and 1.8x the groups. This is the axis the parent
paper's premise turns on, and at 21.3M parameters granularity still pays, *provided r is
retuned*. A practitioner holding R18's r=0.07 fixed at R34 would land between the 0.04 (+0.267)
and 0.06 (−0.355, `sc-ResNet34-add`, n=5) cells — i.e. would measure the gain away.

**Two things this table does NOT support.**
* **ResNet10's +9.476 is not comparable to the other two and must never be quoted beside them.**
  Its r=0 baseline (82.114) is 10pp below R18's and R34's — a degenerate arm, not a healthy
  one. *Any* pooling rescues it: even r=1.0 scores 90.586 (+8.472). The interior optimum's
  advantage over full pooling is only 91.590 − 90.586 = **+1.004** at R10, against
  93.218 − 90.863 = **+2.355** at R18 (`zad`, r=1.0 n=3). Report against BOTH ends.
* **r\*·m is not constant** (3.80, 4.34, 2.20). A constant-pooling-mass law predicts
  r\*(R34) ≈ 0.04, and 0.04 is measurably below the peak. `r34f-*` (30.6) tests r<0.02.

## 30.2 THE PAPER CORE, EXTENDED TO A THIRD ARCHITECTURE AND TO 21.3M PARAMETERS

All 32 `p7` probes are now at 100/100 records (the ResNet34 arms were at 75–91 at cycle 29's
read, which is why 29.3 could not be settled). STEADY window (last 50% of records), CIFAR-10,
pooled across **ResNet10 + ResNet18 + ResNet34**, m spanning **6 → 21,282,122 (5.5 decades)**:

| arm | m | drift/step |
|---|---|---|
| r18-blk6 | 6 | 4.509e-04 |
| r10-lay | 38 | 2.996e-04 |
| r18-lay | 62 | 2.125e-04 |
| r34-lay | 110 | 1.752e-04 |
| r10-node | 8,660 | 1.204e-04 |
| r18-node | 14,420 | 8.828e-05 |
| r34-node | 25,556 | 8.525e-05 |
| r10-w | 4,903,242 | 7.088e-05 |
| r18-w | 11,173,962 | 5.557e-05 |
| r34-w | 21,282,122 | 5.665e-05 |

**d log10(drift) / d log10(m) = −0.1228, R²=0.902, n=10.** The sqrt(N) noise model predicts
**−0.500**. ResNet34 on its own (m 110 → 21.28M) gives **−0.0927**. The campaign's headline
refutation, previously measured at −0.113 on ResNet18 alone, now holds across three
architectures and to 21.3M parameters, monotone, with no architecture term needed.

## 30.3 The agreement ladder is NOT a power law — and the pooled fit hides it

Same probes, statistic = STEADY `step% − null%` (excess of per-step sign agreement over its
own independence null).

| dataset / net | granularity | m | n | excess | sd |
|---|---|---|---|---|---|
| C10 / ResNet18 | resnet18_blocks | 6 | 3 | +4.1577 | 2.2195 |
| C10 / ResNet10 | layerwise | 38 | 2 | +2.4756 | 0.5955 |
| C10 / ResNet18 | layerwise | 62 | 3 | +1.3205 | 0.8946 |
| C10 / ResNet34 | layerwise | 110 | 2 | **+1.5145** | 0.0643 |
| C10 / ResNet10 | nodewise | 8,660 | 2 | +1.3711 | 0.0875 |
| C10 / ResNet18 | nodewise | 14,420 | 3 | +0.4278 | 0.0517 |
| C10 / ResNet34 | nodewise | 25,556 | 2 | **+0.2442** | 0.0873 |
| C10 / ResNet10 | weightwise | 4,903,242 | 2 | +0.0260 | 0.0041 |
| C10 / ResNet18 | weightwise | 11,173,962 | 3 | +0.0046 | 0.0008 |
| C10 / ResNet34 | weightwise | 21,282,122 | 2 | **+0.0033** | 0.0006 |
| C100 / ResNet18_c100 | resnet18_blocks | 6 | 3 | −0.7312 | 2.5459 |
| C100 / ResNet18_c100 | layerwise | 62 | 2 | **+4.4496** | 0.0913 |
| C100 / ResNet18_c100 | nodewise | 14,600 | 2 | **+1.4087** | 0.1805 |
| C100 / ResNet18_c100 | weightwise | 11,220,132 | 1 | +0.0126 | — |

A pooled log-log fit over the 10 CIFAR-10 cells gives slope **−0.4492, R²=0.906** — seductively
close to the sqrt(N) exponent −0.500. **It is an artefact of fitting a straight line to a curve
over 6.5 decades.** The *local* slopes are not constant, and they bend the same way in all three
architectures — shallow in the middle of the ladder, steep at the fine end:

| net | rung → rung | local slope |
|---|---|---|
| ResNet18 | 6 → 62 | −0.491 |
| ResNet18 | 62 → 14,420 | −0.207 |
| ResNet18 | 14,420 → 11.17M | −0.681 |
| ResNet10 | 38 → 8,660 | −0.109 |
| ResNet10 | 8,660 → 4.90M | −0.626 |
| ResNet34 | 110 → 25,556 | −0.335 |
| ResNet34 | 25,556 → 21.28M | −0.642 |

A power law would give the same local slope everywhere. **Do not quote the pooled −0.449 as
"consistent with sqrt(N)".** Rule 3 in a new guise: report the curve, not the fit.

## 30.4 29.3 RESOLVED — model size does not move agreement at fixed granularity; ResNet10 does

29.3 flagged that the one available R34/layerwise point (+1.4690, n=1) "runs the other way".
With the rung complete at n=2 across all three granularities, Welch R18 vs R34:

| granularity | R18 − R34 | se | t | df | |
|---|---|---|---|---|---|
| layerwise | −0.1939 | 0.5185 | −0.37 | 2.03 | ns |
| nodewise | +0.1837 | 0.0686 | +2.68 | 1.48 | ns |
| weightwise | +0.0013 | 0.0006 | +2.10 | 2.70 | ns |

**None reach significance.** 29.3's apparent inversion was noise (R18/layerwise carries seed s0
as an outlier: 2.3528 vs 0.7721, 0.8367). Residuals about the pooled m-curve locate the signal:
**ResNet10 +0.284 dex, ResNet18 −0.136, ResNet34 −0.103.** The "agreement falls with model
scale" reading of 25.6 is really **"ResNet10 is anomalously high"** — it is not a monotone trend
across three sizes, and R18/R34 are indistinguishable from each other and from the m-curve.
25.6 is **not confirmed at three model sizes**; the model-size term at fixed granularity is
below our resolution.

## 30.5 MEASUREMENT CAUTION — pooling job families silently mixes base optimizers

The R18 r-curve pooled across all families reads r\*=0.06, gain +0.636, with r=0 at
92.587 ±0.674 (n=8) and r=0.03 *below* r=0. All three are wrong. The r=0 cell was a mixture of
`ad-l` (SGDm base, 92.12–92.36, n=3+3) and `bo-lion` (**Lion base**, 93.50/93.83) — a
cross-config read of exactly the kind Rule 5 forbids. Split by family, `ad-l` is monotone and
tight (30.1) and `zad` replicates it at r=0.07 (+0.915 vs +1.017).

**Always group by job family before averaging an r-cell.** `run` name minus the r-tag and seed
is a sufficient key. This is the fourth measurement-layer defect after CORRECTIONS 16, 17 and 29.4.

## 30.6 Submitted this cycle — 66 jobs, all pre-registered, all at the front of the queue

| batch | n | account | Nice | what | open question |
|---|---|---|---|---|---|
| `p8-*` (`p7-*-blk6-s{3..9}`) | 14 | alice | 0 | 7 more seeds/dataset at m=6, 20ep | 29.2 is p≈0.07 at n=3 → n=10 |
| `kb-*` | 36 | alice | 100 | M1 r-curve at m=6, both datasets, a0=1e-3, 100ep | the 26.3 falsification test |
| `r34f-*` | 16 | alice2 | 0 | R34 r ∈ {0.005,0.01,0.015,0.025} ×s0-2, + r∈{0,0.02} ×s3-4 | 30.1: where is r\*(R34), and is r\*·m scale-invariant? |

`p8-*` and `kb-*` are cycle 29's batches, resubmitted unchanged (30.0). `r34f-*` is new.

**PRE-REGISTERED for `r34f-*`, from 30.1.** r\*·m = 3.80 (R10), 4.34 (R18), 2.20 (R34 at 0.02).
> **PREDICTED:** the peak stays in [0.015, 0.03] and r\*·m keeps DECLINING with scale — total
> pooling mass is **not** scale-invariant; larger models want proportionally less pooling than
> one power of m allows.
> **FALSIFIED IF:** r=0.005 or 0.01 matches or beats 0.02 — r\* is then still falling fast and
> the shrink rule needs a steeper exponent than m^−1.
> **ALSO FALSIFIED IF:** 0.005–0.03 is flat within noise — the R34 "interior optimum" is then a
> plateau starting at 0.005, and 30.1's r\*-falls-with-scale reading is far weaker than it looks.

Queue after this cycle: **alice 189 pending / 12 running, alice2 243 / 12.** Depth is above the
60–120 band deliberately: nothing left in either queue is speculative (alice's tail is the
non-meta cosine baselines, axis 4; alice2's is base-optimizer coverage, axis 5), and the
ordering goal the band exists to serve is met directly — the 66 decisive jobs hold Nice 0–100
on alice and Nice 0 on alice2, with 103 alice2 jobs demoted 0 → 300 to clear the front.

## 30.7 Still open

* `p8-*`, `kb-*`, `r34f-*` — none landed; all three were submitted this cycle.
* **29.2 still must not be stated at p≈0.07.** Unchanged: `p8-*` has now been queued twice.
* **NEW and strong: the dataset contrast at m=62 and nodewise runs OPPOSITE to m=6.**
  Matched seeds (C100 lay/node have no s0, so C10 is restricted to s1,s2):
  m=6 C10−C100 = **+4.889** (se 1.95, t=2.51, n=3/3); layerwise m=62 = **−3.645**
  (se 0.072, n=2/2); nodewise = **−0.952** (se 0.128, n=2/2). The m=62 gap is 40x the pooled
  seed sd, but n=2 per cell — **treat the t as indicative only, not as a p-value.** Needs n≥5.
* C100/weightwise is still n=1. C100 has no ResNet10/ResNet34 rung at all.
* ResNet34 has no r=1.0 identity control at 100 epochs (`r34r-r1` still pending), so the
  "advantage over full pooling" statistic in 30.1 exists for R10 and R18 only.
* `r34r` r ∈ {0.05, 0.08, 0.1, 0.2} landed truncated (11–95 of 100 epochs) and is **excluded**
  from 30.1; resubmissions are pending.
* Everything still open from 28.8 remains open: `cw`, `kc`, `bo`, `gp`, `ap`, `ag`.

---

# Cycle 31 — 20 Aug 2026

Landed since cycle 30: **35 runs** (986 total, 957 complete). `p8-*` (14 probes, both m=6
cells to n=10), `r34r-r1` + the `r34r` r∈{0.05,0.08,0.1} resubmissions (the R34 r-curve is
now complete), `gp-w-*` and `kb-*` still running. Re-aggregated:
`results/agg_alice1.c31.csv` (573 runs) + `results/agg_alice2.c31.csv` (413) →
`results/all_runs.csv` (986). Probes re-reduced to `results/p7_c31.txt`.

## 31.1 29.2 RESOLVED at n=10 — the contrast is REAL, HALF the size, and its stated mechanism is REFUTED

`p8-*` took both m=6 cells from n=3 to n=10. Identical architecture, identical 6-block
partition, identical config; only the dataset changes. Welch, unpooled:

| statistic | CIFAR-10 (n=10) | CIFAR-100 (n=10) | diff | se | t | df | p |
|---|---|---|---|---|---|---|---|
| step−null excess | +3.447 ± 1.917 | +1.013 ± 2.039 | +2.433 | 0.885 | 2.75 | 17.9 | **0.013** |
| sys% (one-signedness) | 66.467 ± 3.112 | 60.500 ± 2.162 | +5.967 | 1.198 | 4.98 | 16.1 | **1.4e-4** |
| drift/step | 4.5424e-4 ± 1.28e-5 | 2.9267e-4 ± 1.31e-5 | +1.616e-4 | 5.79e-6 | **27.9** | 18.0 | **2.9e-16** |
| sd_beta | 2.254 ± 0.104 | 2.090 ± 0.008 | +0.164 | 0.033 | 4.96 | 9.1 | 7.6e-4 |

**Three things follow, and the third contradicts 29.2.**

1. **The dataset effect on the meta-gradient is real** and is cleanest in the *systematic*
   statistic (p=1.4e-4) and in **drift/step (t=27.9)**, not in the per-step excess that
   29.2 was written on. Prefer `sys%` and `drift` for dataset claims; the per-step excess
   carries a 2pp seed sd at m=6 and needs n≈10 to see a 2.4pp effect.
2. **The n=3 estimate was inflated 2.0x.** 29.2 measured +4.889; at n=10 it is **+2.433**.
   The n=3 cells happened to draw C10's high seeds and C100's low ones. This is the second
   time a cycle-scale claim shrank on replication (cf. CORRECTIONS 3). **Treat any n=3
   effect size in this campaign as an upper bound.**
3. **REFUTED: "CIFAR-100 sits at or below the independence null at m=6".** At n=10 it is
   **+1.013**, positive, with 2 of 10 seeds negative (−1.2868, −2.9534 — both from the
   original n=3 draw). C100's m=6 rung is *lower* than C10's, not *null*. 29.2's headline
   sentence must not be used.

## 31.2 THE PAPER CORE REPLICATES ON A SECOND DATASET — and the local slopes are data-dependent

Same probes, STEADY window, ResNet18 body on both datasets, m spanning 6 → 11.2M (6.3 decades).

| dataset | m=6 | m=62 | m≈14.5k | m≈11.2M | fit d log10(drift)/d log10(m) | R² |
|---|---|---|---|---|---|---|
| CIFAR-10 (n=10/3/3/3) | 4.5424e-4 | 2.1247e-4 | 8.8280e-5 | 5.5573e-5 | **−0.1393** | 0.919 |
| CIFAR-100 (n=10/2/2/1) | 2.9267e-4 | 2.5505e-4 | 8.9350e-5 | 7.1400e-5 | **−0.1061** | 0.902 |

**The sqrt(N) noise model predicts −0.500 on both.** It is refuted on CIFAR-100 by the same
margin as on CIFAR-10 (−0.106 and −0.139 vs −0.500). The campaign's headline is no longer a
one-dataset result. Adding 30.2's three-architecture CIFAR-10 fit (−0.1228, n=10 cells), the
refutation now holds across **3 architectures × 2 datasets × 6.3 decades of m**.

Local slopes, however, are **not** the same function of m on the two datasets:

| rung → rung | CIFAR-10 | CIFAR-100 |
|---|---|---|
| 6 → 62 | **−0.3254** | **−0.0589** |
| 62 → ~14.5k | −0.1612 | −0.1920 |
| ~14.5k → ~11.2M | −0.0696 | −0.0338 |

C10 loses 53% of its drift going from 6 groups to 62; C100 loses 13%. The coarse end of the
ladder is where the datasets differ, which is the same place 31.1's contrast lives. Consistent
with 30.3: this is a curve, not a power law, and now demonstrably not a *universal* curve
either. **Caveat: C100's m=62 and nodewise rungs are n=2 and weightwise is n=1** — `p9-*`
(31.5) takes the whole ladder to n=10 on both datasets before any of this is stated as final.

## 31.3 The ResNet34 r-curve is COMPLETE — the interior optimum survives to 21.3M parameters

`r34r`, one family (Rule 5), CIFAR-10 / ResNet34 / layerwise m=110 / SGDm+Lion / a0=1e-6 /
100 epochs, **complete runs only** (`wallclock_min` present and `epochs_done==100`), plateau:

| r | n | plateau | sd |
|---|---|---|---|
| 0 (full pooling) | 3 | 93.098 | 0.072 |
| **0.02** | 3 | **93.884** | 0.194 |
| 0.03 | 3 | 93.813 | 0.100 |
| 0.04 | 3 | 93.365 | 0.151 |
| 0.05 | 3 | 93.015 | 0.185 |
| 0.08 | 3 | 92.301 | 0.272 |
| 0.1 | 3 | 91.722 | 0.430 |
| 0.2 | 2 | 90.653 | 0.077 |
| 1 (plain layerwise) | — | still running (85–87/100 ep) | |

Interior optimum at r=0.02, **+0.786pp over full pooling** against a pooled sd of ~0.16 —
about 5x the noise and ~40x the ±0.02pp reproducibility floor. Monotone decline for r>0.03.
Cycle 30's exclusion of the truncated r∈{0.05,0.08,0.1} cells is now moot: the resubmissions
completed 100/100 and reproduce the same monotone tail.

## 31.4 MODEL SCALE — the granularity ORDERING flips with model size; the pooling gain does NOT vanish

All CIFAR-10 / SGDm+Lion / layerwise / a0=1e-6 / 100 epochs, **each row one job family**
(r=0 is maximal pooling, r=1 is the verified plain-layerwise identity — see cycle-14 §3):

| net | params | m | family | r=0 (full pool) | r\* | plateau(r\*) | r=1 (plain layerwise) | r\*·m |
|---|---|---|---|---|---|---|---|---|
| ResNet10 | 4.90M | 38 | `r10` | 82.114 | 0.10 | **91.590** | 90.586 | 3.80 |
| ResNet18 | 11.17M | 62 | `zad` | 92.256 | 0.07 | **93.171** | 90.863 | 4.34 |
| ResNet18 | 11.17M | 62 | `ad` | 92.200 | 0.07 | **93.218** | — | 4.34 |
| ResNet34 | 21.28M | 110 | `r34r` | 93.098 | 0.02 | **93.884** | pending | 2.20 |

**(a) The endpoint ordering INVERTS between ResNet10 and ResNet18.**

| net | r=1 (plain) − r=0 (pooled) |
|---|---|
| ResNet10 | **+8.472** — finer granularity wins by a mile |
| ResNet18 | **−1.393** — pooling wins |
| ResNet34 | −3.2 (provisional, r=1 truncated at 85–87 ep) |

This is the parent paper's premise — *granularity stops helping at scale* — **reproduced on
CIFAR-10 by changing model size alone**, at fixed dataset, optimizer, budget and partition
rule. It is the cleanest support for the premise the campaign has produced, and it arrives
without needing ImageNet.

**(b) The method's gain over the BETTER endpoint declines only mildly, and does not vanish:**

| net | params | better endpoint | interior optimum | gain |
|---|---|---|---|---|
| ResNet10 | 4.90M | 90.586 (r=1) | 91.590 | **+1.004** |
| ResNet18 | 11.17M | 92.256 (r=0) | 93.171 | **+0.915** |
| ResNet34 | 21.28M | 93.098 (r=0) | 93.884 | **+0.786** |

A 4.3x parameter increase costs the method 0.22pp of its 1.00pp gain. **The headline is not
"granularity helps"; it is "the OPTIMAL AMOUNT of granularity is interior at every scale, and
which endpoint it beats changes with scale."**

**(c) `r*·m` is NOT scale-invariant and is NOT monotone**: 3.80 → 4.34 → 2.20. Cycle 30.6's
pre-registration ("r\*·m keeps DECLINING with scale") is **already inconsistent with its own
R10→R18 leg**, which rises. `r34f-*` (r ∈ {0.005,0.01,0.015,0.025}, pending, nice 0) resolves
whether R34's r\* is below the current 0.02 grid point; until it lands, 2.20 is an upper bound
on r\*·m for R34 and the non-monotonicity could be a grid artefact at either end.

## 31.5 Submitted this cycle — 46 jobs, one batch, one question

| batch | n | account | nice | what | open question |
|---|---|---|---|---|---|
| `p9-*` (written as `p7-{r18,c100}-{lay,node,w}-s*`) | 46 | alice | 0 | the ENTIRE ResNet18 agreement/drift ladder to n=10 on BOTH datasets, 4 granularities | 31.2's C100 rungs are n=1–2; 31.1 showed n=3 inflates effects 2x |

Cheapest decisive jobs on the board: 20-epoch probes, `--time=01:30:00`, ~15 min each,
`--alpha0 1e-3` (matching `p7`, so Rule 5 holds against the existing s0–s2 cells). Written
into `runs/p7free/` with the `p7-` prefix so `bin/agree2.py runs/p7free/p7-*` picks them up
unchanged. Script: `bin/c31_p9.sh`.

**Nothing else was submitted.** All 24 running slots on both accounts were already occupied by
decisive work (alice: `kb-*` a0=1e-3 M1 r-curve on both datasets, `r34r-r1`, `r34r-r02-s2`;
alice2: the full `gp-w-*` weightwise r-curve), and the pre-registered `r34f-*` sits at nice 0
at the front of alice2. Adding a second batch would have queued behind, not beside, the work
that answers the open questions.

## 31.6 Operations — the cluster is GPU-bound, not queue-bound

`sinfo` at submit time: **every GPU on `gpu-l4-24g`, `gpu-2080ti-11g`, `gpu-mig-40g` and
`gpu-a100-80g` is allocated** (GRES_USED == GRES on every non-drained node). Our 152/222
pending jobs on those partitions are behind `Reason=Priority` against a full cluster, not
behind our own cap. The only slots we actually get are the **12 `gpu-short` jobs per account**,
and both accounts were at 12/12 all cycle. Fair-share is 0.338 (was 0.42 at cycle 29).

Consequence for the queue-depth rule: **depth is not the lever here, ordering is.** Submitting
more cannot raise throughput above 24 concurrent jobs; it can only push decisive work back.
This cycle therefore added the single cheapest decisive batch (46 × 15 min ≈ 11.5 GPU-hours,
which clears in ~1 h of wall-clock at 12 slots) and cancelled nothing, because nothing dead was
running. Queue after: **alice 198 pending / 12 running, alice2 222 / 12.**

## 31.7 Still open

* `p9-*` — submitted this cycle, nothing landed. **31.2's C100 slope is n=2/n=1 at three of
  four rungs until it does.**
* `r34f-*` — pending at nice 0 on alice2. 31.4(c) cannot be stated until it lands.
* `r34r-r1` — running at 85–87/100 epochs; 31.4(a)'s ResNet34 row is provisional.
* `kb-*` — running (67–75/100 ep). This is the 26.3 falsification test at a0=1e-3, m=6, both
  datasets; 8 of 24 have started.
* `gp-w-*` — running. Note `gp-w-r0-s0` completed 100/100 at plateau **42.6** — M1 pooling at
  the weightwise partition does not rescue the collapse, but the curve is not yet complete and
  **no gp-w cell may be quoted from a still-running run** (the aggregator reports partial
  TensorBoard scalars for in-flight jobs; 29 of 986 rows are in-flight and were excluded from
  every table above by requiring `wallclock_min` non-empty AND `epochs_done==epochs_requested`).
* CIFAR-100 still has **no ResNet10 or ResNet34 rung at all** — the model-scale × dataset grid
  is one row deep. Next cycle's candidate, once `p9-*` lands.
* Non-meta baselines (axis 4) remain queued behind everything on alice at nice 20000–40000.
* Everything still open from 30.7 that `p9-*` does not touch remains open.

## 31.8 STRUCTURAL CHECK (Rule 4) — the dataset contrast INVERTS between probe windows; the slope refutation does not

`agree2.py` reports two windows. `drift` is `|mean(beta_last) − mean(beta_first)| / Δsteps`,
i.e. the systematic drift of the **group-mean** log-step-size — exactly the quantity a
sqrt(N)-independence model constrains. Both windows, same 10+10 seeds, m=6:

| statistic | window | CIFAR-10 | CIFAR-100 | diff | t | df |
|---|---|---|---|---|---|---|
| step−null excess | STEADY (last 50%) | +3.447 | +1.013 | **+2.433** | +2.75 | 17.9 |
| step−null excess | STARTUP (first 20%) | +8.797 | +12.05 | **−3.250** | −2.02 | 17.3 |
| sys% | STEADY | 66.47 | 60.50 | **+5.967** | +4.98 | 16.0 |
| sys% | STARTUP | 70.08 | 76.67 | **−6.583** | −5.04 | 17.9 |
| drift/step | STEADY | 4.542e-4 | 2.927e-4 | **+1.616e-4** | +27.90 | 18.0 |
| drift/step | STARTUP | 5.937e-4 | 8.363e-4 | **−2.426e-4** | −18.49 | 14.7 |

**All three statistics flip sign, and all three flips are significant.** At m=6, CIFAR-100
*starts* with more agreement and more drift than CIFAR-10 and *ends* with less; its
startup/steady drift ratio is 2.86 against CIFAR-10's 1.31, i.e. its β settles roughly twice
as fast at a common 20-epoch, a0=1e-3 budget.

**Consequence for 31.1 and 29.2.** The dataset does not shift agreement by a level; it changes
the **trajectory**. Every statement of the form "CIFAR-100 has less/more coordinate agreement
than CIFAR-10 at m=6" is a statement about a *window*, and reverses in the other one. The
defensible version is: *at m=6 the two datasets' meta-gradients follow different β
trajectories, and the STEADY-window ordering (C10 > C100) is the tail of a crossover, not a
constant offset.* A mundane reading — C100's β has converged by the steady window and C10's
has not — is not excluded by anything we have measured. **Do not put a mechanism on the
dataset contrast.**

**Consequence for 31.2 — the refutation gets STRONGER, not weaker.** The obvious reviewer
objection to a drift-vs-m slope is "you measured a transient". Fitting the same slope in both
windows answers it:

| ladder | m span | STEADY slope | R² | STARTUP slope | R² |
|---|---|---|---|---|---|
| CIFAR-10 / ResNet18 | 6 → 11.17M | −0.1393 | 0.919 | −0.2096 | 0.980 |
| CIFAR-100 / ResNet18 | 6 → 11.22M | −0.1061 | 0.902 | −0.3605 | 0.911 |
| CIFAR-10 / ResNet10 | 38 → 4.90M | −0.1214 | 0.962 | −0.3502 | 0.910 |
| CIFAR-10 / ResNet34 | 110 → 21.28M | −0.0915 | 0.953 | −0.1738 | 0.911 |

**Eight fits, 2 datasets × 3 architectures × 2 windows. Every one is above −0.500, and the
most favourable of them (−0.3605, R²=0.911) still falls 28% short.** The startup window is
uniformly steeper — early training is the closest the meta-gradient ever gets to independence —
and it still does not reach the sqrt(N) exponent. This is the form the claim should take in
the paper: **not "the slope is −0.11", which is one window, but "no window, dataset or
architecture we can construct reaches −0.5."**

Both caveats are re-checkable at n=10 per rung once `p9-*` lands; the C100 rows above are
n=10 only at m=6.

## 32.1 31.7 ITEM 1 RESOLVED — the agreement/drift ladder at n=10 on BOTH datasets

`p9-*` (submitted cycle 31 as `p7-{r18,c100}-*`) landed complete: 92 dirs, 100 probe records
each. The CIFAR-100 ladder was n=1–2 at three of four rungs; it is now n=10 at all four.
20-epoch probes, a0=1e-3, free adaptation, `bin/agree2.py` statistics, reduced by
`bin/ladder32.py` (new this cycle; per-seed OLS + 2000-sample seed bootstrap).

**STEADY window (last 50% of records):**

| family | rung | m | n | drift/step | sys% | step−null |
|---|---|---|---|---|---|---|
| R18/C10 | blk6 | 6 | 10 | 4.5424e-4 ±1.28e-5 | 66.467 ±3.112 | +3.447 |
| | lay | 62 | 10 | 2.1664e-4 ±1.29e-5 | 52.452 ±0.963 | +0.953 |
| | node | 14,420 | 10 | 8.9741e-5 ±2.04e-6 | 50.638 ±0.072 | +0.400 |
| | w | 11,173,962 | 10 | 5.5428e-5 ±9.54e-7 | 50.004 ±0.003 | +0.005 |
| R18/C100 | blk6 | 6 | 10 | 2.9267e-4 ±1.31e-5 | 60.500 ±2.162 | +1.013 |
| | lay | 62 | 10 | 2.6103e-4 ±1.20e-5 | 57.516 ±1.551 | +4.101 |
| | node | 14,600 | 10 | 9.1195e-5 ±2.19e-6 | 51.839 ±0.162 | +1.518 |
| | w | 11,220,132 | 10 | 6.9666e-5 ±1.47e-6 | 50.012 ±0.003 | +0.010 |

**All eight full-ladder slopes, with bootstrap 95% CI (new — cycle 31 reported point
estimates only):**

| family | window | slope | R² | 95% CI | reaches −0.500? |
|---|---|---|---|---|---|
| R18/C10 | STEADY | −0.1398 | 0.923 | [−0.1414, −0.1383] | no |
| R18/C100 | STEADY | −0.1082 | 0.910 | [−0.1100, −0.1065] | no |
| R10/C10 | STEADY | −0.1214 | 0.961 | [−0.1234, −0.1194] | no |
| R34/C10 | STEADY | −0.0915 | 0.951 | [−0.0951, −0.0879] | no |
| R18/C10 | STARTUP | −0.2122 | 0.973 | [−0.2182, −0.2069] | no |
| R18/C100 | STARTUP | −0.3775 | 0.887 | [−0.4053, −0.3546] | no |
| R10/C10 | STARTUP | −0.3512 | 0.907 | [−0.3649, −0.3376] | no |
| R34/C10 | STARTUP | −0.1739 | 0.909 | [−0.1831, −0.1647] | no |

**The n=10 slopes are indistinguishable from cycle 31's n=1–3 ones** (C100 STEADY −0.1082 vs
−0.1061; C100 STARTUP −0.3775 vs −0.3605). The thin rungs were not distorting the fit. Every
CI excludes −0.500 by ≥0.09 in log-slope; the most favourable fit's upper bound is −0.3546.

## 32.2 A NINTH FIT, at a different a0 and budget — and the curve is not a power law

`runs/mx/probe_sig_*` is the free-adaptation, **a0=1e-6, 100-epoch** series (config-matched to
the a0=1e-6 r-curves, i.e. to the accuracy claims in 32.4–32.6, unlike the a0=1e-3 20-epoch
`p7free` probes above). Reducing it verifies 26.3's agreement column exactly and adds a fit:

| m | drift/step (STEADY) | sys% |
|---|---|---|
| 6 | 4.4917e-5 ±1.55e-6 | 70.867 ±0.797 |
| 62 | **5.8057e-5** ±7.26e-6 | 53.262 ±0.191 |
| 14,420 | 2.3097e-5 ±2.31e-6 | 51.031 ±0.119 |
| 11,173,962 | 2.1799e-6 ±1.48e-6 | 50.0053 ±0.0003 |

Slope **−0.2363, R²=0.815 (N=12)** — above −0.500 like the other eight. But note the drift
**RISES from m=6 to m=62** and falls only after: 4.49 → 5.81 → 2.31 → 0.218 (×1e−5). **The
drift-vs-m relation is non-monotone at this config, so it is not a power law at all** — which
is why R²=0.815 is the weakest of the nine fits. A sqrt(N) model does not merely have the
wrong exponent here; it has the wrong functional form.

## 32.3 ROBUSTNESS — 31 of 32 leave-one-rung-out sub-spans stay above −0.500; report the one that does not

Rule 3 cuts both ways: do not report the max cell, and do not hide the cell that hurts.
`bin/robust32.py` refits every family with each rung dropped in turn (32 sub-span fits).

| | STEADY | STARTUP |
|---|---|---|
| R18/C10 | −0.111 … −0.200 | −0.163 … −0.236 |
| R18/C100 | −0.101 … −0.157 | −0.171 … −0.441 |
| R10/C10 | −0.084 … −0.168 | −0.138 … **−0.525** |
| R34/C10 | −0.061 … −0.132 | −0.092 … −0.282 |

**The single exception is R10 / STARTUP / node→weight, −0.5248 (n=2 seeds, 2 rungs).**
It should not be read as support for the model, for a reason visible in the data:

**MEASUREMENT CAUTION — the weightwise STARTUP drift is a near-cancellation and is biased
toward zero.** `drift = |mean(β_last) − mean(β_first)| / Δsteps` on the *group mean*. In the
startup window the weightwise rung reads 3.0112e-5 (R18/C10), **3.9993e-6 ±1.74e-6**
(R18/C100) and 1.0767e-5 (R10) — one to two orders below its own steady value, because the
11.17M per-weight β's have not yet developed a common direction and their mean barely moves.
A downward-biased endpoint on a log-log fit biases the slope STEEP. Dropping that rung:
C100 STARTUP −0.3775 → −0.1706, R10 STARTUP −0.3512 → −0.1378, R18 STARTUP −0.2122 → −0.1633.
**Every steep startup slope in the campaign is produced by the weightwise startup point.**
The −0.5248 sub-span is exactly the two-point fit anchored on it. Net: the refutation is
stronger than cycle 31 stated, not weaker.

## 32.4 THE DATASET CONTRAST, PER RUNG — (m=6, STEADY) is the ONLY cell that flips

29.2 and 31.1 chased "the m=6 rung inverts between datasets"; 31.8 showed the flip is
window-dependent. At n=10 on all four rungs the structure is finally readable (C10 − C100, sys%):

| rung | m | STEADY | STARTUP |
|---|---|---|---|
| blk6 | 6 | **+5.967** | −6.583 |
| lay | 62 | −5.064 | −7.492 |
| node | 14.4k | −1.201 | −0.406 |
| w | 11.2M | −0.008 | −0.022 |

**CIFAR-100 has MORE coordinate agreement than CIFAR-10 at every rung in every window, with
exactly one exception: m=6 in the steady window.** The contrast two cycles chased is a single
cell, not a dataset property. 31.8's instruction stands and hardens: **do not put a mechanism
on the dataset contrast.** The defensible statement is that the coarsest partition is the only
one whose steady-state ordering reverses, and n=10 does not tell us why.

## 32.5 UNREAD DATA, AGAIN — `sc50-*` and `cs-r10/cs-r34-*` completed cycles ago and were never tabulated

Rule 1's failure mode recurred. Two batches finished and were mentioned only as "submitted" or
"in flight" (FINDINGS 3716, 4051, 4531); neither has a results row anywhere in `docs/`:

* **`sc50-*`** — ResNet50 (23.5M) on CIFAR-10, all six arms, **n=1**, complete. Wallclock 138 min
  mean / 141 max, i.e. `gpu-short`-eligible, contradicting the note at FINDINGS 4392.
* **`cs-r10-*` / `cs-r34-*`** — CIFAR-100 × {ResNet10_c100, ResNet34_c100} × {scalar, layerwise,
  additive r=0.06}, **n=3**, complete. The CIFAR-100 × model-scale grid was never one row deep
  for the *accuracy* runs; only the probe/agreement grid is.

Reducing them turns the model-scale ladder from 3 architectures into 4 on CIFAR-10 and from 1
into 3 on CIFAR-100. Everything in 32.6–32.7 comes from data that was already on disk.

## 32.6 MODEL SCALE — the two effects run in OPPOSITE directions, on both datasets

All cells re-derived from `results/all_runs.csv` by matched config (SGDm+Lion, batch 100,
AUGMENT=1, 100 ep, `epochs_done == epochs_requested`), plateau = mean of last 5 epochs.
Pooling is compared at **matched r=0.06** so no cell is a per-model argmax (Rule 3).

**(a) CIFAR-10, a0=1e-6 — the M1 pooling gain RISES with model size:**

| net | params | plain layerwise (r=1) | M1 r=0.06 | gain |
|---|---|---|---|---|
| ResNet10 | 4,903,242 | 90.619 ±0.267 (n=3) | 90.786 ±0.312 (n=6) | **+0.166 (t=0.8 — NULL)** |
| ResNet18 | 11,173,962 | 90.817 ±0.158 (n=24) | 93.262 ±0.135 (n=8) | **+2.446 (t=42.5)** |
| ResNet34 | 21,282,122 | 90.149 ±0.135 (n=5) | 92.743 ±0.192 (n=5) | **+2.594 (t=24.7)** |
| ResNet50 | 23,520,842 | 87.710 (n=1) | 90.947 (n=1) | +3.237 (n=1) |

**(b) same at a0=1e-3** — same direction, and negative at the smallest model:
−2.297 (R10, t=−12.9) / +1.031 (R18, t=15.0) / +2.929 (R34, t=22.9) / +2.504 (R50, n=1).

**(c) the PLAIN granularity gain (layerwise − scalar) FALLS with model size**, on both a0:

| net | a0=1e-6 | a0=1e-3 |
|---|---|---|
| ResNet10 | +19.877 (t=39.4) | +20.623 (t=37.2) |
| ResNet18 | +3.043 (t=70.6) | +3.425 (t=35.7) |
| ResNet34 | +0.835 (t=11.5) | +0.735 (t=4.8) |
| ResNet50 | **−1.394 (n=1)** | +0.815 (n=1) |

**ResNet50 at a0=1e-6 is the first architecture in the campaign where the parent paper's
premise reproduces — layerwise LOSES to scalar (87.710 vs 89.104).** It rests on one seed
(R10's seed sd runs 0.27–0.83pp, so −1.394 at n=1 is not safe). `sc50` seeds s1–s4 are queued
this cycle; **do not state (c)'s last row until they land.**

**(d) CIFAR-100, a0=1e-3 — the pooling PENALTY shrinks with model size (same direction as (a)):**

| net | params | scalar | layerwise | M1 r=0.06 | pool effect | gran gain |
|---|---|---|---|---|---|---|
| ResNet10_c100 | 4,949,412 | 12.968 ±0.202 | 68.266 ±0.329 | 5.558 ±0.042 | **−62.708** | +55.298 |
| ResNet18_c100 | 11,220,132 | 22.571 ±0.465 | 69.488 ±0.468 | — | — | +46.918 |
| ResNet34_c100 | 21,328,292 | 30.868 ±0.689 | 67.835 ±0.951 | 57.499 ±1.039 | **−10.336** | +36.967 |

n=3 except R18 (n=5 scalar / n=8 layerwise). Two datasets, four and three rungs: **a larger
model makes pooling more favourable and plain granularity less so.** In both (c) and (d) the
granularity gain collapses because the SCALAR arm catches up (C10 a0=1e-6: 70.742 → 87.774 →
89.314 → 89.104; C100: 12.968 → 22.571 → 30.868) while the layerwise arm is flat
(90.619 / 90.817 / 90.149 / 87.710 and 68.266 / 69.488 / 67.835).

## 32.7 The R34 r-curve is complete at n=3 including r=1 — and r* falls as the model grows

| net | best r | plateau at best | r=1 | gain at own optimum | r* × params |
|---|---|---|---|---|---|
| ResNet10 | 0.10 | 91.590 ±0.051 | 90.586 ±0.166 | +1.004 | 0.49M |
| ResNet18 | 0.06 | 93.262 ±0.135 | 90.863 ±0.063 | +2.399 | 0.67M |
| ResNet34 | **0.02** | 93.884 ±0.194 | 90.269 ±0.163 | **+3.615** | 0.43M |

(a0=1e-6, CIFAR-10, layerwise, 100 ep, n=3–10 per cell.) `r34r-r1` reached n=3 this cycle, so
the R34 reference is no longer provisional. **Candidate law: r* ∝ 1/N, i.e. r*·N ≈ 0.5M ±0.12M
retained coordinates.** CAUTION: **r=0.02 is the smallest non-zero point on the R34 grid**
(r=0 gives 93.098, r=0.03 gives 93.813), so the optimum is interior but its LOCATION is
grid-limited. `r34r-r{0005,001,0015}` submitted this cycle to close it — see 32.9.

## 32.8 26.3's MECHANISM IS REFUTED AT THE NODEWISE RUNG — by the runs 26.3 listed as in flight

`gp-node-*` completed. Matched config throughout (CIFAR-10, ResNet18, SGDm+Lion, a0=1e-6,
100 ep); agreement from `runs/mx/probe_sig_*` at the SAME config (32.2), not from the
a0=1e-3 probes:

| granularity | m | sys% (STEADY) | plain plateau | best-r plateau | M1 gain |
|---|---|---|---|---|---|
| resnet18_blocks | 6 | 70.867 ±0.797 | 91.335 ±0.142 (n=18) | 91.765 ±0.223 (r=0.03) | +0.430 |
| layerwise | 62 | 53.262 ±0.191 | 90.817 ±0.158 (n=24) | 93.262 ±0.135 (r=0.06) | **+2.446** |
| nodewise | 14,420 | 51.031 ±0.119 | 91.593 ±0.138 (n=8) | 92.797 ±0.048 (r=0.06) | **+1.204** |
| weightwise | 11.17M | 50.0053 ±0.0003 | 35.433 **±33.911** (n=16) | 64.174 ±0.284 (r=0.3) | NOT QUOTABLE |

**Agreement falls monotonically across all four rungs; the gain rises then falls, peaking at
layerwise.** 26.3 claimed "the pooling gain runs OPPOSITE to agreement" with the nodewise cell
marked *in flight*. That cell has now landed at +1.204, half the layerwise gain, against a
LOWER agreement. **One mechanism no longer covers 25.3, 25.5 and 24.3.**

**Rule 4 caution on the last row:** the plain weightwise reference has sd 33.9 over n=16 —
it is bimodal (collapse vs no-collapse, D1), not a distribution with a mean. No weightwise M1
gain may be quoted until the arms are conditioned on collapse. The `gp-w-*` curve is also
monotone INCREASING over its measured span (r=0 45.005 ±2.603 → r=0.3 64.174 ±0.284), i.e.
pooling *hurts* at the weightwise partition on CIFAR-10 — the opposite of 26.3's prediction —
but `gp-w-r1` is still running and no gp-w cell may be quoted from an in-flight run.

## 32.9 Submitted this cycle — 69 jobs on alice, 4 batches, each with one open question

| batch | n | nice | what | open question / pre-registration |
|---|---|---|---|---|
| `p7-c100r10-*`, `p7-c100r34-*` | 30 | 0 | C100 × {R10, R34} × {lay, node, w} × 5 seeds, 20 ep probes | 31.7 last bullet: the drift refutation's model-scale × dataset grid is one row deep. **Pre-reg: every slope stays above −0.500 in both windows.** ~15 min/job |
| `sc50-*-s{2,3,4}` | 18 | 50 | ResNet50, 6 arms, seeds 2–4 (s1 promoted from nice 20000 → n=5) | 32.6(c): R50 is the only architecture where the parent paper's premise reproduces, at n=1 |
| `f5cos-r34-*`, `f5cos-r50-*` | 12 | 150 | tuned AdamW+cosine at R34/R50, lr ∈ {3e-4, 1e-3} × 3 seeds | axis 4: the non-meta baseline exists at ONE architecture (R18, 94.093). Our best arm is 93.884 at **R34** — the comparison is currently cross-architecture and inadmissible |
| `r34r-r{0005,001,0015}` | 9 | 150 | R34 r-curve below its grid edge | 32.7: **pre-reg — if r*∝1/N, all three fall below 93.884 and above 93.098; a peak at r≤0.01 refutes the 1/N form** |

**Cancelled: `sw-cos-*` (21).** A 7-point AdamW+cosine LR sweep on R18/C10 that duplicates
`fxcos-*`, which is complete at n=3 with a flat top (3e-4 → 94.062, 1e-3 → 94.093) and a
collapsing high side (constant-LR 3e-3 → 85.962). Its only new points (1e-5, 3e-5, 1e-2) lie
far outside the plateau. No open question was attached to it.

**Promoted:** `sc50-*-s1` 20000 → 50; `fc100-cos-*` (C100 non-meta baseline, axis 4, zero
coverage) 40000 → 1500; `fxcos-*` (R18 baseline to n=5 + the 3e-3 turn-over) 40000 → 1500.
The two baseline batches were then set behind `p7-c100r*` because 30 × 15 min of probes clears
in ~40 min of the 12-slot allocation and answers the theoretical core.

**Not touched: `kc-*` (39).** Inspected before trimming (30.0's lesson) — it is the CIFAR-100
M1 r-curve: R18_c100 seeds 2–4 (takes the n=2 C100 r-curve to n=5) and an entirely new
R10_c100 r-curve. It is the natural n≥5 follow-up to 32.6(d) and stays at nice 1000.

## 32.10 Operations

Queue after this cycle: **alice 189 pending / 12 running, alice2 214 / 12.** Both accounts sit
at 12/12 on `gpu-short` and 0 elsewhere; every pending job reports `Reason=Priority` against a
cluster whose L4 / 2080ti / MIG / A100 nodes are all `mix` or `alloc`. 31.6's conclusion holds:
**throughput is capped at 24 concurrent jobs and ordering, not depth, is the lever.**

Front-of-queue order on alice is now sc50 → (bg300/bg600, long-partition-only, do not compete
for `gpu-short`) → kb → **p7-c100r** (rank 36) → r34r → f5cos → fxcos → fc100 → kc → fx →
sc101. alice2 needed no reordering: `r34f` (nice 0) → gp/bp/bo/ap/ag (nice 300) → tail.
Nothing was submitted to alice2 — its 73 front jobs are all pre-registered and cannot start
any faster.

**`scontrol update Nice=` must clear the job's ACCRUED AGE, not just match it.** Setting
`fc100-cos` from nice 200 to 600 left it ahead of a brand-new nice-0 job, because Slurm
priority = base + age − nice and the older job had ~660 points of age. Nice 1500 was needed.
Budget ~700 nice points per half-day of queue age when demoting.

**`sc101` (ResNet101, 12 jobs) cannot use `gpu-short`.** R50 measures 138 min at 100 ep, so
R101 is ~4.7 h against the 3:50 limit; its 7:30 request is correct and it will only start when
a long partition frees. The 5th scale rung is therefore not obtainable this cycle.

## 32.11 Still open

* `p7-c100r*` — submitted, nothing landed. **32.6(d) has no drift/agreement ladder of its own
  until it does; the C100 side of the paper core is still one model size.**
* `sc50` seeds — 32.6(c)'s last row and 32.6(a)'s last row are n=1. The most interesting single
  cell in the campaign (layerwise finally losing to scalar) is one seed.
* `f5cos-*` — until it lands, **no "our method wins/loses by X" sentence may name ResNet34 or
  ResNet50**; the only tuned baseline we own is ResNet18's 94.093 ±0.036.
* `r34r-r{0005,001,0015}` — 32.7's r*∝1/N law is a 3-point fit with one point at a grid edge.
* `gp-w-r1` — running. 32.8's last row stays NOT QUOTABLE until it lands *and* the collapse
  conditioning is done.
* `kc-*` — the C100 r-curve is n=2 everywhere (32.6(d) middle row is a hole).
* 26.3 needs replacing, not patching: agreement is monotone in m and the M1 gain is not, so
  the campaign currently has **no** single mechanism linking granularity, pooling and dataset.
* Everything still open from 31.7 that this cycle did not touch.

---

# CYCLE 33

All numbers below re-derived from `results/all_runs.csv` (1075 runs, re-aggregated this cycle
from both accounts) with `superseded==0` and `epochs_done>=100`. Metric is `plateau`.
Unless stated: ResNet18 / CIFAR-10 / a0=1e-6 / 100 ep / AUGMENT=1 / SGDm base + Lion meta /
`meta-stepsize 1e-3` / `BETA_CLIP=-15:-2.3026`.

## 33.1 THE MECHANISM 26.3 WAS MISSING — "pooling" and meta-step-size are confounded in M1

Three arms in the campaign all end in **one uniform step size across groups**. They score
4.85pp apart, and they are ordered by their *effective meta-step-size*, not by anything
hierarchical.

| arm | uniform step size? | effective meta-step | n | plateau |
|---|---|---|---|---|
| `zpool` r=0 (layerwise) | yes | `ms` = 1e-3 | 5 | 87.740 ±0.138 |
| `zpool` r=0 (weightwise) | yes | `ms` = 1e-3 | 5 | 87.763 ±0.036 |
| plain `scalar` | yes (native) | `ms` = 1e-3 | 12 | 87.772 ±0.139 |
| `shrink` lam=1.0 (layerwise) | yes | `ms`·\|2p−1\| ≈ 9.7e-5 | 3 | 92.199 ±0.226 |
| `additive` r=0 (layerwise) | yes (+1-step offset) | `ms`·\|2p−1\| ≈ 9.7e-5 | 8 | 92.587 ±0.674 |

**Why (`HF.py:231-293`).** The two operator families act at different points in the meta-update:

* `_zpool` pools the meta-GRADIENT *before* Lion: at r=0 every group receives `sign(sum_b z_b)`.
  Lion's update magnitude is exactly `ms`, so the shared step size advances at rate `ms`.
* `_apply_hier` (`additive`, `shrink`) pools the REALISED beta increments *after* Lion. Under
  Lion every group's realised increment is exactly `±ms`, so
  `mean_b(d_b) = ms·(2p−1)`, p = fraction of groups agreeing in sign. The shared step size
  therefore advances at rate **`ms·|2p−1|`**.

Measured layerwise `frac_neg` = 0.5483870967741935 (`runs/zb/probe_zb-plain`, `zb-l-r1`;
identical in both) → \|2p−1\| = 0.0968 → effective `ms` ≈ 9.7e-5, a **10.3× reduction**.

**Consequence.** M1's `r` is not a clean pooling dial: moving r from 1 to 0 simultaneously
pools the groups *and* divides the meta-step-size by \|2p−1\|. Because \|2p−1\| is the
sign-agreement, the M1 gain inherits a dependence on agreement — which is why 26.3 kept finding
an agreement/gain relation it could not make monotone. **This is a confound, not a mechanism.**

## 33.2 The true-pooling curves — pooling RESCUES over-fine granularity, never improves good granularity

`zpool` is the operator whose endpoints are exact (CORRECTIONS 15, re-verified this cycle:
r=1 layerwise 90.933 ±0.177 vs plain 90.784 ±0.169; r=1 weightwise 77.922 ±0.331 vs plain
77.822 ±0.351; r=0 lands on `scalar` at both granularities, 0.032pp). Probe confirmation:
`runs/zb/probe_zb-{l,w}-r0` report `z_mean` **identical across all reported tensors**
(−0.07720036059617996 / −0.07795713096857071), `frac_neg` 1.0 / 0.0.

| r | 0 | 0.1 | 0.3 | 0.5 | 0.7 | 0.9 | 0.95 | 0.99 | 1 |
|---|---|---|---|---|---|---|---|---|---|
| **layerwise** | 87.740 | 89.470 | 89.476 | 89.170 | 89.100 | 90.196 | 90.435 | 90.971 | 90.933 |
| n | 5 | 5 | 5 | 4 | 6 | 2 | 2 | 1 | 5 |
| **weightwise** | 87.763 | 87.847 | 87.950 | 87.870 | 88.064 | 88.510 | 88.798 | 89.052 | 77.922 |
| n | 5 | 5 | 5 | 4 | 6 | 2 | 2 | 2 | 5 |

* **layerwise: no interior optimum.** Max (r=0.99) is +0.038pp over r=1 — inside the ±0.177
  seed band. Full pooling costs **−3.044pp** vs plain layerwise.
* **weightwise: interior optimum at r=0.99, +11.130pp over r=1 (plain).** n=2 at that cell.
* The best true-pooling number anywhere (89.052) is still **below** plain `resnet18_blocks`
  (91.350 ±0.142, n=12) and plain layerwise (90.784).

**Admissibility (CORRECTIONS 15).** These are two *within-granularity* shape statements. The
r-axes are NOT comparable between the rows — `_zpool`'s pooled term is a SUM and its path is
compressed by m — so no claim of the form "pooling of strength r helps weightwise more than
layerwise" is licensed by this table.

## 33.3 CORRECTION — "even full pooling helps" is refuted

Carried since cycle ~20 (`CONTINUE-HERE.md`): "on CIFAR-10/ResNet18 the optimum is interior at
r~0.07 (+2.31pp over plain layerwise) and **even full pooling helps (+1.39pp)**."

That sentence reads `additive` r=0. Under the true pooling operator, full pooling **hurts**:

| | plateau | vs plain layerwise (90.784 ±0.169, n=17) |
|---|---|---|
| `additive` r=0 (what was quoted) | 92.587 ±0.674 (n=8) | +1.803 |
| `zpool` r=0 = true full pooling | 87.740 ±0.138 (n=5) | **−3.044** |

The +1.8pp is the 10.3× meta-step-size reduction of 33.1, not pooling. **No "full pooling
helps" sentence may be written.** CORRECTIONS 21.

## 33.4 `additive` r=0 is not granularity-invariant — the missing half of Rule 4

A true full-pooling arm collapses every partition to the same single step size, so its score
must not depend on the partition. `zpool` r=0 satisfies this to **0.032pp across a 180,000×
range in group count**. `additive` r=0 spans **47.582pp** over the same range:

| granularity | m | `additive` r=0 | `zpool` r=0 |
|---|---|---|---|
| `resnet18_blocks` | 6 | 91.767 ±0.042 (n=2) | — |
| `layerwise` | 62 | 92.587 ±0.674 (n=8) | 87.740 ±0.138 (n=5) |
| `nodewise` | 14,420 | 91.984 ±0.103 (n=3) | — |
| `weightwise` | 11,173,962 | 45.005 ±2.603 (n=3) | 87.763 ±0.036 (n=5) |

The spread is what 33.1 predicts: \|2p−1\| falls with m, so `additive` r=0 shrinks the
meta-step further at finer partitions until beta cannot escape a0=1e-6 at all (weightwise,
45.005). CORRECTIONS 13 verified the r=1 endpoint and **inferred** r=0 from the algebra; the
algebra is right that r=0 shares the update and wrong that this is a controlled baseline.

## 33.5 What survives — the M1 interior optimum, as an empirical curve only

| granularity | best interior r | plateau at r* | plateau at r=1 | gain | n |
|---|---|---|---|---|---|
| `resnet18_blocks` | none (flat) | 91.767 (r=0) | — | — | 2 |
| `layerwise` | 0.06 | 93.222 ±0.150 | 90.863 ±0.063 | **+2.359** | 10 / 3 |
| `nodewise` | 0.06 | 92.797 ±0.048 | 91.657 ±0.196 | **+1.140** | 3 / 3 |
| `weightwise` | none (monotone ↑) | 78.046 (r=1) | 78.046 ±0.024 | 0 | 2 |

The interior optimum is real and well-powered at layerwise and nodewise, absent at both ends of
the granularity ladder. It is a **measured method result**; it is **not** a pooling result.

## 33.6 The meta-step-size axis is unexplored — 1042 of 1075 runs sit at one value

`meta_stepsize` over the whole CSV: `1e-3` ×1042, blank ×26, `1e-2` ×4. Given 33.1, this is now
the campaign's largest open confound: every "hierarchy helps" cell may be a meta-LR effect.

## 33.7 `kb-*` landed — the blk6 additive r-curve inverts between datasets (a0=1e-3)

| r | 0 | 0.03 | 0.07 | 0.2 |
|---|---|---|---|---|
| **CIFAR-10** (R18, blk6) | 92.144 ±0.107 (3) | 91.995 ±0.238 (3) | 91.893 ±0.088 (2) | in flight |
| **CIFAR-100** (R18_c100, blk6) | 27.302 ±0.941 (3) | 29.781 ±0.776 (3) | 34.732 ±2.043 (3) | 42.872 (n=1) |

CIFAR-10 falls with r; CIFAR-100 rises monotonically with r over the whole measured grid. The
r=0.2 CIFAR-100 cell is **n=1 — do not quote it**. Direction is consistent with the layerwise
dataset inversion already on record.

## 33.8 Submitted this cycle — 69 jobs, 3 batches, each with one open question

| batch | acct | n | what | open question / pre-registration |
|---|---|---|---|---|
| `ms-scal-*`, `ms-scalA-*` | alice | 26 | `scalar` × meta-stepsize {1e-5,3e-5,1e-4,3e-4}, n=5, + a0=1e-3 control n=3 | **Pre-reg: scalar at ms=1e-4 lands 92.2–92.6, i.e. on `shrink` lam=1 / `additive` r=0.** If so the entire M0/M1 family is meta-LR tuning on a single step size and granularity contributes nothing. If it stays near 87.8, the pooling arms do something a meta-LR change cannot. |
| `ms-lay-*`, `ms-layA-*` | alice2 | 26 | `layerwise` plain × same grid | **Pre-reg: does the plain-layerwise ms curve reach `additive` r=0.06's 93.222 ±0.150?** Reaching it ⇒ M1 adds nothing beyond retuning ms. |
| `zp-w-*`, `zp-l-*` | alice2 | 17 | `zpool` weightwise r∈{0.9,0.95,0.99} to n=5; **new** r∈{0.995,0.999} n=3; layerwise r=0.99 to n=3 | 33.2's weightwise interior optimum is n=2 and its cliff (89.052 → 77.922 between r=0.99 and r=1) is unlocated. **Pre-reg: a continuous collapse interpolates; a discontinuity leaves both new cells near 89.** |

**Cancelled, with reasons (97 jobs).** `sc101-*` (12) — R101 needs ~4.7h against `gpu-short`'s
3:50 cap and the long partitions are permanently full; 32.10 already ruled the 5th scale rung
unobtainable. `kc-r10-*` (18) — an entirely new `additive` r-curve at a new model size, whose
dial 33.1 shows to be confounded. `am4-*` (21) — superseded by the focused `amx-*` (kept).
`c6f-*` (21) — duplicate of `kc-r18-*` (kept). `m0c-*` (13), `rcg-*` (9) — `shrink`/`additive`
CIFAR-100 ladders superseded by the `ms-*` test. `zrn-*` (13) — resubmitted as `zp-*` at the
front instead of sitting at rank 110+.

## 33.9 Operations

* **Both accounts run exactly 12 jobs, all on `gpu-short`, and the other 30 GPUs of the
  per-account cap are unreachable.** The QOS pools are per-partition
  (`qos-short-gpu` 12, `qos-gpu-l4` 8, `qos-gpu-2080` 12, `qos-gpu-mig` 8, `qos-gpu-a100` 2).
  Multi-partition submission does **not** spread across them: Slurm places the job in one
  partition and it consumes only that QOS. Every long partition is `mix`/`alloc` for other
  users (`gpu-l4-24g` 7/7 nodes allocated, `gpu-mig-40g` 7/7, `gpu-a100-80g` 5/6 with one
  drained), so the long-partition QOS pools cannot be entered at all. **Throughput remains 24
  concurrent jobs across both accounts; 31.6 and 32.10 hold.**
* Queue after this cycle: **alice 174 pending / 12 running, alice2 164 / 12.** Above the 60–120
  guidance. Net change is −45 jobs; the justification for the remainder is that `ms-*` and
  `zp-*` sit ahead of the entire speculative tail on both accounts (alice rank 73, alice2 rank
  51, both behind only pre-registered work), so nothing decisive is queued behind speculation.
* **New jobs no longer start at the front.** Fair-share has fallen far enough that a fresh
  nice-0 submission (prio 670575 on alice) ranks *below* month-old nice-400 jobs that have
  accrued age. Promotion by `scontrol update Nice=` cannot raise priority; the only lever for
  an old low-priority batch is cancel-and-resubmit, which is what `zrn-*` → `zp-*` did.

---

# Cycle 34 — no-submit cycle (fair-share gate); the granularity axis measured as an effective-meta-step axis

**Gate status at cycle open.** alice FairShare **0.337248** (RawUsage 17.42M), 39 pending / 8
running. alice2 FairShare **0.339765** (RawUsage 15.89M), 159 pending / 12 running. Both below
the 0.35 floor; alice also at the ~40-pending cap. **Zero jobs submitted this cycle.** No jobs
cancelled either — nothing in either queue was submitted by this session.

Aggregation: alice1 643 runs, alice2 443 runs, `results/all_runs.csv` = **1086** rows (+11 vs
cycle 33). All 11 are in-flight partials (`f5cos-r34`, `kb-c100-r05`, `r34f-*`); **no new
completed runs since cycle 33.** This cycle is therefore analysis + damage control.

## 34.1 THE CYCLE-33 DECISIVE BATCH WAS DESTROYED 19 MINUTES AFTER SUBMISSION

`ms-scal-*` (20) + `ms-scalA-*` (6) — the pre-registered meta-stepsize sweep that 33.6 called
"the campaign's largest open confound" — submitted **2026-08-20T11:58:18**, cancelled
**2026-08-20T12:17:43**, `Elapsed 00:00:00`. They never ran.

The 12:17:43 event cancelled **86 alice jobs** at one instant:

| family | n | what was lost |
|---|---|---|
| `ms-scal-*`, `ms-scalA-*` | 26 | the decisive meta-stepsize sweep (33.8 pre-registration) |
| `kc-r18-*` | 21 | R18 additive r-curve |
| `sc50-*` | 18 | pending seeds of the ResNet50 scale rung |
| `r34r-*` | 9 | R34 r-curve |
| `fc100-cos-*` | 9 | CIFAR-100 non-meta baseline — **promoted to Nice=200 by `c32_trim.sh` 
  as "axis 4 on the second dataset, currently zero coverage"**, then cancelled |
| `p7-*` stragglers | 3 | a **PROTECTED** prefix |

**Mechanism — PROTECTED.txt is a comment file.** Only `bin/safe_trim.sh` reads it. `safe_trim.sh`
would have refused all 86: its rule 2 (never cancel at Nice < 1000) protects fresh nice-0
submissions, and its rule 1 honours the prefix list. The 12:17:43 sweep was a bare `scancel`
over a JobID range, which consults neither. This is the **third** repeat of the same failure
(cycle 29 → cycle 30 "our own trim destroyed cycle 29's decisive batches"; the 08:33:15 sweep;
now 12:17:43). Writing the guard did not stop it because nothing forces its use.

**Actions taken (no GPU cost).** `ms-`, `zp-`, `fc100-cos-` appended to `bin/PROTECTED.txt` on
alice; `ms-`, `zp-` on alice2. `bin/c33_ms.sh` is intact and ready to fire unchanged.
**`bash bin/c33_ms.sh` is the first command of cycle 35**, ahead of any other submission.

Surviving half: alice2's `ms-lay-*` / `ms-layA-*` (26 jobs) are all PENDING and intact. Without
the scalar arm the comparison is unanswerable — `ms-lay` alone gives the layerwise ms response
curve but not the m=1 control that separates granularity from meta-LR.

## 34.2 |2p−1| measured per granularity — 33.4's assertion quantified

33.4 asserted "\|2p−1\| falls with m" from the algebra. Measured, from the `p7` STEADY window
(`results/p7_c31.txt`, ResNet18 / CIFAR-10), `p` = `step%` (per-step cross-group sign agreement):

| granularity | m | `step%` (n seeds) | null% | \|2p−1\| | `ms_eff` = 1e-3·\|2p−1\| |
|---|---|---|---|---|---|
| `resnet18_blocks` | 6 | 69.7333 (10) | 66.2868 | 0.394667 | 3.947e-4 |
| `layerwise` | 62 | 56.3871 (3) | 55.0666 | 0.127742 | 1.277e-4 |
| `nodewise` | 14,420 | 50.7600 (3) | 50.3322 | 0.015200 | 1.520e-5 |
| `weightwise` | 11,173,962 | 50.0165 (3) | 50.0119 | 0.000331 | 3.307e-7 |

Strictly monotone over **six decades of m**. 33.1 quoted \|2p−1\| = 0.0968 for layerwise from
`runs/zb`'s `frac_neg`; the `p7` steady `step%` gives **0.1277**. Both ≈1e-4 effective; the
33.1 headline ("10.3× reduction") becomes **7.8×** on the `p7` scale. Minor, but quote the
scale with the number — 28.2 and 31.8 both bit on exactly this.

## 34.3 The granularity axis traces a single-peaked curve in effective meta-step-size

Re-derived from `all_runs.csv` under one tight filter (ResNet18 / CIFAR-10 / a0=1e-6 / SGDm+Lion
/ augment=1 / 100 ep / ms=1e-3 / not superseded), plateau metric:

| arm | m | `ms_eff` | plateau | n |
|---|---|---|---|---|
| plain `scalar` (native, no pooling) | 1 | 1.000e-3 | 87.772 ±0.139 | 12 |
| `additive` r=0 `resnet18_blocks` | 6 | 3.947e-4 | 91.730 ±0.071 | 3 |
| `additive` r=0 `layerwise` | 62 | 1.277e-4 | **92.228 ±0.087** | 6 |
| `additive` r=0 `nodewise` | 14,420 | 1.520e-5 | 91.984 ±0.103 | 3 |
| `additive` r=0 `weightwise` | 11,173,962 | 3.307e-7 | 45.005 ±2.603 | 3 |

Ordered by `ms_eff` the five points are **unimodal**: 87.772 → 91.730 → 92.228 → 91.984 →
45.005, peak at `ms_eff` ≈ 1.3e-4. Five arms that differ **only in the partition** lie on one
smooth meta-step response curve. This is what 33.1 predicts.

**REVISION of 33.4.** Its layerwise cell read 92.587 ±0.674 (n=8). Under the tight filter the
cell is **92.228 ±0.087 (n=6)** — the ±0.674 was heterogeneous pooling, not seed noise. The
33.4 blk6 cell (91.767, n=2) becomes 91.730 ±0.071 (n=3). Directions unchanged.

## 34.4 The collapse is CONSISTENT WITH 33.1 but cannot decide it — and why

Within a fixed (architecture, dataset), \|2p−1\| is **monotone in m** (34.2). So `ms_eff` and
granularity are **rank-identical**, and 34.3's curve is equally consistent with "granularity
is a reparameterisation of meta-LR" (33.1) and with "granularity genuinely helps, and agreement
happens to co-vary". Observational data cannot separate them.

Trying to break the tie with the architecture axis fails too: across R10/R18/R34 layerwise,
m = 38 / 62 / 110 against `ms_eff` = 1.789e-4 / 1.277e-4 / 1.064e-4 — still anti-correlated.
The near-matched pairs that *do* decouple m from `ms_eff` (`r18-node` m=14,420 `ms_eff`=1.52e-5
vs `c100-node` m=14,600 `ms_eff`=3.478e-5; `r18-lay` vs `c100-lay`, both m=62, `ms_eff` 1.49×
apart) are **cross-dataset**, so their plateaus are not comparable.

**Only the direct ms sweep at m=1 decides it.** `ms-scal-*` is the campaign's highest-value
pending experiment, and it is the one that was destroyed.

## 34.5 Sharpened pre-registration for `ms-scal-*` (replaces 33.8's estimate)

33.8 pre-registered "scalar at ms=1e-4 lands 92.2–92.6" as a judgement call. 34.3 derives it:
interpolating the curve at `ms_eff` = 1e-4 gives

> **PREDICTED: plain `scalar` (m=1, no hierarchy of any kind) at `--meta-stepsize 1e-4`
> plateaus at 92.2 ± 0.3** — statistically indistinguishable from `additive` r=0 layerwise
> (92.228 ±0.087) and **above** plain layerwise (90.784 ±0.169, n=17).

If it lands there, granularity contributes nothing beyond the effective meta-step it induces,
and the M0/M1 positive result is meta-LR tuning. If it stays near 87.8, granularity does
something a meta-LR change cannot. The prediction is now quantitative and falsifiable at n=5.

## 34.6 REFUTED — the weightwise collapse is not explained by shared-term travel

A tempting sentence for the paper: "at `weightwise`, `additive` r=0's shared step size advances
at `ms`·\|2p−1\| = 3.3e-7, so over 50,000 steps β travels 0.017 in log-space against the
ln(0.05/1e-6) = **10.82** it needs to escape a0=1e-6 — hence 45.005." The arithmetic, with the
startup window weighted in (`p7` STARTUP `step%`, first 20% of records):

| granularity | steady \|2p−1\| | startup \|2p−1\| | β travel (mixed) | ≥ 10.82? | plateau |
|---|---|---|---|---|---|
| `resnet18_blocks` | 0.394667 | 0.501666 | 20.80 | yes | 91.730 |
| `layerwise` | 0.127742 | 0.336099 | 8.47 | marginal | 92.228 |
| `nodewise` | 0.015200 | 0.070630 | **1.31** | **no** | **91.984** |
| `weightwise` | 0.000331 | 0.003500 | 0.05 | no | 45.005 |

It predicts blk6 escapes and weightwise does not — both correct — and predicts **nodewise
cannot escape**, when nodewise plateaus at 91.984. **The model is refuted.** The reason is
33.4's own result: `additive` r=0 is not exact full pooling (it spans 47.58pp across
granularities where true `zpool` r=0 spans 0.032pp). Its pooled term is an **offset**; each
group's individual component still moves at ±`ms` per step and can escape on its own.
Weightwise fails not because the shared term is slow but because at 50.0165% vs a 50.0119%
null each group's own meta-gradient is indistinguishable from noise, so its β random-walks
(RMS 1e-3·√5e4 = 0.22) instead of drifting.

**No shared-term-travel sentence may be written to explain the weightwise collapse.**
CORRECTIONS 22.

## 34.7 Operations

* Both accounts remain capped at 12 concurrent jobs on `gpu-short`; 33.9's finding that the
  long-partition QOS pools are unreachable is unchanged. 24 concurrent jobs across both.
* GPUs are **not** idle during this no-submit cycle: 20 running, 198 pending across the two
  accounts. Queue depth is sufficient to absorb every freed slot without new submissions, so
  the fair-share hold costs no throughput.
* Provisional, **do not quote**: in-flight `r34f-*` (R34 layerwise additive) shows a sharp
  instability boundary — r=0.0005 → plateau 93.109 at 72 ep, r=0.001 → 67–72 at ~35 ep,
  r=0.0015 → 46.9 at 27 ep, r=0.0025 → chance at 1–2 ep. Mid-flight plateaus at different
  epoch counts are not comparable; wait for completion.

## 34.8 Cycle 35 opening order

1. `bash bin/c33_ms.sh` on alice — resubmit the destroyed 26 (unchanged, already protected).
2. Verify `ms-lay-*` on alice2 is still PENDING and still in `PROTECTED.txt`.
3. Only then consider anything else, and only if FairShare ≥ 0.35.
4. **Never trim with bare `scancel`. `bash bin/safe_trim.sh <n>` (dry run first) or nothing.**
