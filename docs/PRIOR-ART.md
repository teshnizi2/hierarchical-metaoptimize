# Prior art verdict — the weightwise collapse is a REDISCOVERY

Two independent literature sweeps (~170 papers) reached the same conclusion. Recording it
before any of it reaches a thesis chapter or an email.

## The collapse is a documented failure mode, and the fixes are published

| Source | The fix it publishes | Our run |
|---|---|---|
| **Sutton 1992, IDBD** (AAAI-92) | *"bound each βᵢ from below by, say, **−10**"*; *"limit the change in βᵢ on any one step to ±2"* | our per-weight run **peaked at β = −9.77**, essentially exactly Sutton's floor, then fell through it. **The floor alone would have prevented the entire collapse.** |
| **Mahmood, Sutton, Degris, Pilarski 2012, Autostep** (ICASSP) | normalize the meta-update by a running max `v` so `\|Δ log α\| ≤ μ`; scale α so the effective step size ≤ 1, making divergence *"literally impossible"* | neither present |
| **Javed, Sharifnassab, Sutton 2024, SwiftTD** (RLC) | `β ← clip(β, ln(e⁻¹⁵), ln(0.1))`, and normalize the meta-step by `e^β` | our β reached **−23.7 — 8.7 nats below SwiftTD's hard floor** |

**Autostep exists specifically because per-weight meta-learned step sizes are unstable
without normalization.** Sutton co-authors MetaOptimize; **Sharifnassab (SwiftTD) wrote this
project's proposal.** The remedy is in the family's own prior work.

## Why the meta-gradient vanishes — structural, not incidental

`σ'(β) = dα/dβ = α`, and `h` is a trace of weight updates each ∝ α, so **`z = h·∇f ∝ α`**.
As α → 0 the meta-gradient vanishes *linearly by construction*. SwiftTD's footnote states the
antidote and the reason: *"We normalize θ by e^{β[i]} because the scale of the meta-gradient …
is proportional to e^{β[i]}."*

## Correction to our own diagnosis

We reported `sign(0)=0` as the cause. It is the **lock, not the driver**. Sign is
scale-invariant, so `|Δβ| = η` regardless of how small α is.

Descending β = −9.77 → −23.7 is **13.93 nats**. At η = 1e-3 that needs **≥13,930 steps with
sign = −1**. An unbiased random walk would need ~1.9×10⁸ steps. **So the sign was negative
~90–100% of the time: systematic downward drift, not diffusion.**

Two published candidates for that drift, and telling them apart *is* the research question:
- **Short-horizon bias** (Wu, Ren, Liao, Grosse, ICLR 2018): truncated meta-objectives are
  *"seriously biased towards small step sizes … by multiple orders of magnitude."* The
  meta-gradient genuinely points down.
- **Sign bias under skewed noise** (Karimireddy et al., ICML 2019, Counterexample 1):
  `E[sign(z)]` can oppose `E[z]`.

**Diagnostic that separates them: log `P(sign(z) < 0)` and the skewness of `z` per group,
against block size.**

## What remains genuinely open

1. **SNR vs granularity — unclaimed.** But the correct form is
   **SNR ∝ √(B / (1 + c(B−1)))**, saturating at `1/√c`, where `c` is the within-block
   meta-gradient noise correlation — *not* √B. **Measuring `c` is the empirical core.**
   The strong monotone claim ("finer is always worse") is **contradicted**: STACX improves
   monotonically 2→21 meta-parameters; *Optimistic Meta-Gradients* meta-learns an
   **element-wise** LR for ResNet-50 on ImageNet (~25M meta-parameters) successfully;
   Adalayer finds per-layer *too coarse*. The defensible claim is a **bias–variance optimum
   in granularity**.
2. **`sign(0)=0` as an absorbing state at the *meta* level** — no prior art found. The only
   acknowledgement anywhere is a GitHub issue by signSGD's own author.
3. **No published ablation of sign-meta vs raw-meta** — MetaOptimize reports (Lion,Lion),
   (AdamW,Adam), (RMSProp,Adam), (SGDm,Adam) but never isolates the sign.
4. **MetaOptimize's own unexplained granularity non-monotonicity is the ideal hook.**
   Limitations §9: *"While increasing the number of step sizes is anticipated to enhance
   performance, our experimental findings … reveal that this improvement is not consistent …
   Further investigation is needed."* §7.3: *"Unlike CIFAR10, here the blockwise versions
   showed no improvement over the scalar versions."* **The word "variance" appears zero times
   in the paper.**

## The sharpest theoretical argument against per-weight (μP)

*Tensor Programs V* (Yang & Hu): correct step-size scaling is a function of fan_in/fan_out —
and **every weight in a tensor shares the same fan_in**. So theory says the right step size is
*constant within a tensor*; per-weight granularity adds 11.17M noisy estimators of a quantity
that is shared. Complementary, not contradictory: μP fixes width-scaling analytically and
leaves learning to supply the residual per-tensor, data-dependent part.

## Consequence for framing

*"Per-weight fails, per-layer works"* is **not publishable** — it rediscovers 1992/2012/2024.
*"Here is the SNR / sign-bias mechanism explaining MetaOptimize's own reported granularity
non-monotonicity, and here is the measured `c`"* is.

## Immediately citable fixes to test

1. Clip β to `[ln η_min, ln η]` (SwiftTD / IDBD / RPROP's `Δmin`,`Δmax`).
2. Normalize the meta-step by `e^β` (SwiftTD) or by a running max (Autostep).
3. Meta-optimizer Adam instead of Lion — Balles & Hennig show Adam damps low-SNR coordinates
   by `1/√(1+η̂²)` while sign does not. **MetaOptimize itself suggests this**: *"We could
   instead use softer forms of normalization, such as … RMSProp."*
4. If sign is kept, break the tie stochastically (Safaryan & Richtárik; Gupta et al. 2015).

---

# Addendum — the granularity question is RESOLVED from the paper itself

**MetaOptimize §7.1 defines its "blockwise" as six blocks: *"one for each linear layer and
four blocks for the ResNet modules."*** So the paper's blockwise is **m = 6**, exactly our
`resnet18_blocks = [3,12,15,15,15,2]`.

**Consequences — this settles the plan's single most important open question:**
1. There is **no contradiction** between our results and the paper. Our m=6 cell reproduces
   their setting.
2. **Our `layerwise` (m=62) and `weightwise` (m=11.17M) are genuinely new ground** — the
   released code could not run them (no branch), and the paper never reported them.
3. The email to Saber no longer needs to ask "is your layerwise m=6 or m=62?" — it is m=6.

**MetaOptimize names this exact gap as future work.** §9, *Blockwise step-sizes*:
> "While step sizes can vary much in granularity, our experiments focused on scalar and
> blockwise step-sizes. While increasing the number of step sizes is anticipated to enhance
> performance, our experimental findings in Section 7 reveal that **this improvement is not
> consistent** … **Further investigation is needed in future research.**"

and: *"developing low-complexity methods … especially for adjusting step-sizes at the **layer
and weight levels**, is essential."* §2 already promises the capability: *"or even a unique
step-size per weight, all handled automatically by MetaOptimize"* — **which the released code
does not implement.**

## The strongest quantitative support for learned per-layer step sizes

Everett et al., *Scaling Exponents Across Parameterizations and Optimizers* (ICML 2024,
arXiv:2407.05872), Table 8 — residual per-layer-type multipliers **after** muP's prescribed
width exponents are applied:

| optimizer | embedding | hidden | readout |
|---|---|---|---|
| Adam + muP | 5.303 | 1.258 | **11.723** |
| SGD + muP | **1398.861** | 5.532 | 0.020 |

Theory pins the *exponent*; the *constant* is a large, empirically-determined, per-layer free
parameter — **precisely what a learned per-layer step size supplies.** Also: muP TP5 §D.7
says outright *"to get the best results, one should ideally tune all such hyperparameters"*
per parameter tensor.

## Two objections we must answer, not dodge

1. **SOAP** (arXiv:2409.11321): restoring **full per-coordinate** state in Shampoo's eigenbasis
   *beat* the factored version. So per-coordinate state is not simply noise. The defensible
   distinction is per-coordinate **preconditioning** (worth its noise, in the right basis) vs
   per-coordinate **step-size scale** (what pooling targets).
2. **Adalayer freezing** (Zhao et al., ICLR 2025, arXiv:2407.07972): freezing per-layer second
   moments *at initialization* nearly recovers Adam, except for the last layer and LayerNorm.
   That cuts **toward prescription and away from adaptation** for hidden layers. The exception
   is explained by heavy-tailed token frequency (Kunstner et al., NeurIPS 2024) — exchangeability
   fails at the unembedding and essentially nowhere else.

## The exchangeability argument is unclaimed

No paper justifies block granularity by **estimator variance under within-tensor
exchangeability**. The field uses Hessian block-diagonality (Adam-mini), backprop correlation
`G = ez^T` (Adam-mini, Adafactor), or norm/module semantics (Bernstein). RAdam noticed the
variance angle and named parameter-sharing as the fix — *as future work* — and nobody followed
up. Xie et al. (ICLR 2025, arXiv:2410.08198) provide the ready-made formal home: their bound
`η·H(L,Φ) + 2√(1−β₂)·Σ_b d_b σ_b` has a smoothness term that improves with finer partitions
and a noise term that does not.
