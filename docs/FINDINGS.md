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
