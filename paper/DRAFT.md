# Step-Size Granularity in Online Meta-Gradient Optimisation is an Estimation Problem

*Working draft. Numbers marked ✅ are confirmed (≥3 seeds); ⏳ are in flight; ⚠️ are not yet
trustworthy. Do not circulate rows that are not ✅.*

---

## Abstract (sketch)

MetaOptimize learns optimiser step sizes online from a discounted meta-gradient, and its
granularity — how many weights share a step size — is set by a free partition. The original work
reports that blockwise step sizes help on CIFAR-10 but give **no improvement on ImageNet**, and
explicitly leaves this unexplained. We show the discrepancy is not about scale but about
**budget**: granularity accelerates convergence and stabilises it, and only converts into higher
final accuracy when the budget is too short for the coarser arm to catch up. We then show that
partially pooling the per-group step sizes — shrinking each group's log step size toward a shared
component — improves on every fixed granularity we tested, and is insensitive to its own pooling
strength across three orders of magnitude. Along the way we report three defects in the released
implementation, one of which means the finer granularities the paper discusses were never
executable.

---

## 1. What the parent paper claims, and the gap

MetaOptimize (Sharifnassab, Salehkaleybar & Sutton, ICML 2025) adapts step sizes online via
`α = exp(β)` with β driven by an eligibility-trace meta-gradient. Granularity is a partition
choice: `m = 1` scalar, `m = 6` blockwise (their setting: "one for each linear layer and four
blocks for the ResNet modules"), up to `m = n` per weight.

Two statements in that paper set up this work:

> §7.3: "**Unlike CIFAR10**, here the blockwise versions of MetaOptimize showed no improvement
> over the scalar versions."

> §9: "While increasing the number of step sizes is anticipated to enhance performance, our
> experimental findings … reveal that **this improvement is not consistent** … Further
> investigation is needed in future research."

The word *variance* does not appear in the paper. The mechanism is unclaimed.

## 2. Three defects in the released implementation

These are reported as a contribution, not a complaint — each changes what the code measures.

1. **No data augmentation.** ResNet-18 reaches ~0 training loss on CIFAR-10 within one epoch, so
   there is no optimisation headroom left for a step-size method to exploit. Every comparison
   run without augmentation is uninformative about optimisation.
2. **A second, silent truncation.** `train.py` carries its own wall-clock break inside the epoch
   loop, independent of the scheduler's limit. It truncated runs to 81 and 85 of 100 epochs,
   producing non-comparable arms with no error.
3. **The finer granularities were never executable.** `layerwise`, `nodewise` and `weightwise`
   are accepted as argument values but have no branch in `init_meta`, `beta_to_alpha` or
   `block_product`, so every such run raises `AttributeError`. The authors' fuller `MetaStep`
   code does contain branches, but they cannot run (`.cuda()` applied to a Python list;
   `torch.log` of a Python float). **The granularities §9 calls for future work on could not be
   run by the released code.** We implement them and validate against the authors' own working
   `blockwise` path via exact identities (`layerwise == blockwise[1,…,1]`, `scalar ==
   blockwise[62]`, all granularities identical at `meta_stepsize = 0`; max |diff| 7.5e-9).

## 3. Granularity buys speed and stability, not asymptotic accuracy ✅

CIFAR-10, ResNet-18, augmented, 100 epochs, 3 seeds. Under the paper's own configuration
(AdamW base + Adam meta):

| arm | ep→85% | ep→88% | ep→90% | final acc |
|---|---|---|---|---|
| scalar (m=1) | 9.7 | 18.0 | 29.7 | 91.76 |
| 6-block (m=6) | 9.0 | 15.0 | 26.3 | 91.83 |
| layerwise (m=62) | **7.7** | **14.3** | **24.0** | 91.73 |

Monotone in granularity at every threshold ≥85% — layerwise reaches 90% **19% sooner** — while
final accuracy is identical to within 0.1pp. The parent paper's CIFAR-10 evidence is Figure 1,
a *learning curve*; on that axis the claim reproduces exactly.

Under a base optimiser without per-coordinate normalisation (SGDm), the same acceleration
appears, but the scalar arm **never converges within the budget**, so the advantage shows up as
final accuracy instead:

| arm | ep→85% | ep→90% | final |
|---|---|---|---|
| scalar | 36.0 | **never** | 88.09 |
| 6-block | 29.0 | 42.0 | 91.56 |
| layerwise | 27.3 | 52.0 | 91.34 |

**One statement covers every cell:** *granularity accelerates optimisation; it shows up as higher
final accuracy only when the budget is too short for the coarser arm to catch up.* This predicts
the parent paper's own ImageNet null — a long budget lets the scalar arm converge, so the speed
advantage stops converting into a final-accuracy gap.

### 3.1 A third benefit: stability ✅

In the paper's own (SGDm, Adam) configuration the **scalar** arm fails outright on 2 of 3 seeds
(18.47, 20.71 vs 88.45) while every granular arm holds to ±0.3pp. Granularity is not only faster,
it rescues seeds on which a single shared step size diverges.

## 4. Partial pooling improves on every fixed granularity ✅

Shrink each group's log step size toward the group mean each step,
`β_b ← β_b − λ(β_b − mean β)`. SGDm + Lion, guard on, 3 seeds:

| λ | best test acc | Δ vs plain layerwise |
|---|---|---|
| plain layerwise | 91.33 ± 0.17 (n=6) | — |
| 0.001 | 92.54 ± 0.20 | +1.21 |
| **0.01** | **92.79 ± 0.11** | **+1.46** |
| 0.03 – 1.0 | 92.50 – 92.58 | +1.17 … +1.25 |

**The curve is flat over three orders of magnitude.** The method nominally adds a hyperparameter
whose value does not matter — in practice it removes a decision rather than adding one. It
generalises: +0.47pp on 6-block, and **+1.51pp** under the paper's own Adam meta-optimiser.

The mechanism is regularisation, not acceleration — and this is the one place the §3 framing does
**not** carry over:

| target | plain layerwise | + pooling (λ=0.01) |
|---|---|---|
| 85% | **27.7** | 35.3 |
| 90% | 55.5 | **40.0** |
| 91% | 83.5 | **42.3** |
| 92% | **never (0/6)** | **51.7 (3/3)** |

Slower to fit early, decisively better later, and it reaches a level plain layerwise never
reaches within the budget.

## 5. The per-weight failure is a rediscovery, and a residual

Unguarded per-weight runs collapse to chance. Instrumentation shows the meta-gradient going
non-finite in a single step (62/62 tensors NaN at step ~23,650) while β is still in a healthy
range — a float32 overflow of an undecayed trace (`γ = 1` leaves `h ← h − Δw` an unbounded
running sum), **not** a step-size phenomenon.

**This is a rediscovery and must be written up as one.** The guard is published three times over:
IDBD (Sutton 1992) bounds β from below "by, say, −10" — our run peaked at β = −9.77 and fell
through exactly that floor; Autostep (Mahmood, Sutton et al. 2012) exists *specifically* because
per-weight meta-learned step sizes are unstable without normalisation; SwiftTD (Javed,
Sharifnassab & Sutton 2024) clips β to `[ln e⁻¹⁵, ln 0.1]`. Applying SwiftTD's clip removes the
collapse in 3/3 seeds (79.4 ± 0.5 instead of 10.0), and is a no-op for coarser granularities.

**A real deficit survives the fix**: guarded per-weight reaches 79.4 against layerwise's 91.4.
That ~12pp gap is the genuine granularity effect and is not a numerics story.

## 6. ⏳ Where the optimum lies (in flight)

Pooling in β-space has no exact endpoint at `m = n`. Using the identity `Σ_b z_b = z_scalar`, we
instead interpolate in **meta-gradient space**, `z'_b = (1−r)·Σ_j z_j + r·z_b`, for which r=0 is
*exactly* the scalar arm and r=1 *exactly* the plain per-group arm. Both endpoints are confirmed
structurally: at r=0 the β vector stays uniform to machine precision (sd = 0.000e+00 across 200
probe records), and at r=1 the β spread matches the plain arm (3.120 vs 3.126). A 36-run sweep
over r ∈ {0, 0.1, 0.3, 0.5, 0.7, 1} × {layerwise, weightwise} × 3 seeds is running.

## 7. Limitations, stated plainly

* **Single dataset.** CIFAR-10 / ResNet-18 only. ImageNet was scoped out: the available copy has
  **489 of 1000 classes**, and completing it requires credentials we will not automate. CIFAR-100
  and an explicit budget sweep replace it as the scale axis — the latter tests the §3 mechanism
  *directly*, which ImageNet would only test by proxy.
* **Augmentation deviates from the paper.** Necessary (see §2.1) but it means absolute numbers
  are not directly comparable to the published ones.
* **Reproducibility floor.** Runs reproduce to ~±0.02pp, not bitwise (cuDNN autotuning). Effects
  below ~0.05pp are not resolvable at 3 seeds. All effects reported here are ≥1pp.
* **α₀ = 1e-6 is a confound.** Runs spend many epochs merely growing the step size from a
  deliberately tiny start, so arms are partly compared on recovery speed from a bad
  initialisation. A control at α₀ ∈ {1e-4, 1e-3} is running.
* ⚠️ **Not yet claimed.** Any statement about pooling at `m = n` awaits §6.

## 8. Related work

The IDBD lineage (Sutton 1992 → Schraudolph SMD 1999 → Autostep 2012 → SwiftTD 2024) is the
direct ancestry and contains the guards. On sign-based meta-updates, Balles & Hennig (2018) show
Adam damps low-SNR coordinates by `1/√(1+η̂²)` while `sign` does not — consistent with our
finding that the collapse is sign-specific (Adam meta: no collapse in 3/3; Lion meta: collapse).
On granularity from theory, μP (Yang & Hu) implies the correct step-size scale is constant within
a tensor, since all weights in a tensor share fan_in — an argument *against* per-weight
granularity that complements our measurement. Counterweights we must address rather than dodge:
SOAP restores full per-coordinate state in the right basis and wins; Adalayer finds per-layer
scales frozen at initialisation nearly recover Adam.
