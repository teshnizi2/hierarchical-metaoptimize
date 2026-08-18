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
