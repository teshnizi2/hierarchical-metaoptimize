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
