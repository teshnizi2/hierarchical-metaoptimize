# Measured findings

CIFAR-10, ResNet-18 (11,173,962 params / 62 parameter tensors), 100 epochs,
RandomCrop(32,pad=4)+HorizontalFlip, meta-optimizer Lion, `meta_stepsize=1e-3`,
`alpha0=1e-6`, `gamma=1`. Best test accuracy, 3 seeds unless noted.

| granularity | m | SGDm base | AdamW base |
|---|---|---|---|
| scalar | 1 | 88.09 ± 0.16 | (pending) |
| resnet18_blocks | 6 | 91.56 ± 0.03 | 91.86 ± 0.31 |
| layerwise | 62 | 91.34 ± 0.09 | 91.83 ± 0.17 |
| weightwise | 11.17M | seed 0 peaked 70.09 then collapsed to 10.00 | 86.05 ± 0.29 |

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
