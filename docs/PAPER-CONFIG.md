# The parent paper's exact configuration — extracted from the PDF

Source: MetaOptimize (Sharifnassab, Salehkaleybar, Sutton), arXiv:2402.02342v6, §7.1 and
Appendix Table 2. Extracted directly from the paper, so nothing here depends on recollection.

## CIFAR-10 (§7.1)

| item | value |
|---|---|
| model / data | ResNet-18, CIFAR-10, **batch size 100** |
| (base, meta) combinations tested | **(AdamW, Adam), (Lion, Lion), (RMSProp, Adam), (SGDm, Adam)** |
| meta step size η | **1e-3** for every MetaOptimize row |
| initial step size α₀ | **1e-6** for MetaOptimize rows; **1e-5** for the fixed-step-size AdamW baseline |
| discount γ | **1** |
| AdamW base | ρ = 0.9, λ = 0.999, κ = 0.1 |
| meta momentum c̄ | 0.9 |
| **blockwise partition** | **six blocks — "one for each linear layer and four blocks for the ResNet modules"** |
| **data augmentation** | **NOT MENTIONED ANYWHERE IN THE PAPER.** `augment`, `random crop`, `flip` return zero hits across the full text. The released code has none either. |
| seeds | curves "averaged over 5 random seeds" |

## The claim we are testing

§7.3, ImageNet: *"**Unlike CIFAR10**, here the blockwise versions of MetaOptimize showed no
improvement over the scalar versions."*

So the paper asserts blockwise **does** improve over scalar on CIFAR-10 and **does not** on
ImageNet. §7.1 itself only claims the weaker *"In every tested combination, MetaOptimize
outperforms its corresponding fixed-step-size baseline"* — i.e. MetaOptimize > fixed LR, not
blockwise > scalar. The blockwise>scalar claim on CIFAR-10 rests on the §7.3 aside and Fig. 1.

## Sensitivity (§7.5)

* η: *"there is generally no need for tuning, and the default value η = 1e-3 works universally
  well… All experiments in this section used this default value with no sweeping required."*
* γ: *"γ for values γ ≥ 0.999 … performance begins to degrade with smaller values of γ."*
  So **γ = 0.999 is inside the paper's own sanctioned range.**
* No clipping or bounding of β or the step sizes is mentioned anywhere.

## Deviations in our runs, now identified

1. **Meta-optimizer.** Our Gate 1 used meta = **Lion** for the SGDm arm; the paper's SGDm arm
   is **(SGDm, Adam)**. Gate 3 re-runs the SGDm arm with Adam meta to match.
2. **Augmentation.** We enable RandomCrop+Flip; the paper appears not to. Ours is the
   scientifically necessary choice (without it the task is memorised in epoch 1 and there is no
   optimisation headroom), but it means our absolute numbers are not directly comparable to
   the paper's, and any reproduction claim must say so.
3. **γ = 1 has a consequence the paper does not discuss.** With γ = 1 and α tiny, the trace
   update `h ← γ(1 − wd·α)h − Δw` has effectively **no decay term**, so `h` is an unbounded
   running sum. See `docs/FINDINGS.md` — the weightwise failure is a float32 overflow of this
   trace, not a step-size collapse. γ = 0.999 gives the trace a ~693-step half-life and should
   bound it; that experiment is running.
