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
up. Xie et al. (ICLR 2025, arXiv:2410.08198) were previously cited here as the ready-made formal
home, on the claim that their bound `η·H(L,Φ) + 2√(1−β₂)·Σ_b d_b σ_b` has a smoothness term
that improves with finer partitions and a noise term that does not.

> **UNVERIFIED — DO NOT QUOTE (cycle 88, CORRECTIONS 119.5).** We do **not** hold
> arXiv:2410.08198 locally (`paper/refs/` contains only 2406.16793, 2407.07972, 2506.01049),
> so the bound above was never re-derived from the source. A second reading of the paper's
> abstract-level claim reports the **opposite** of what we need: that `H(L,Φ₁) ≤ H(L,Φ₂)`
> whenever `Φ₁` refines `Φ₂`, i.e. finer partitions give a **monotonically better** bound with
> **no counteracting noise term**. If that is right, this reference is not our formal home —
> it is existing theory that **contradicts** the falling limb we measure, which is a far more
> interesting thing to cite and a far worse thing to misquote.
> **ACTION BEFORE ANY DRAFT:** fetch the PDF, re-derive the bound, and replace this block with
> whichever version survives. Until then neither reading may appear in a draft.


---

# THE CLOSEST PRIOR WORK, AND IT WAS MISSING FROM THIS FILE ENTIRELY

*Added cycle 88 (CORRECTIONS 119.4). Its absence was a hole a referee would have found first.*

## CAM-HD — Jie, Gao, Vasnev & Tran, "Adaptive Hierarchical Hyper-gradient Descent"

**arXiv:2008.07277**, published in *International Journal of Machine Learning and Cybernetics*
(2022). **This paper must be cited in the first paragraph of any granularity claim we make.**

It already does four of the things this campaign thought were its own:

1. **It builds the granularity ladder.** Global / layer-wise / filter-wise / parameter-wise
   learning rates, all learned by hypergradient descent.
2. **It states the small-sample mechanism, in words, four years before us.** *"For the model
   involving a large number of learning rates for different groups of parameters, the updating
   for each learning rate only depends on the average of a small number of examples. Therefore,
   when the batch size is also not large, over-parameterization is an issue to be concerned."*
3. **It reports the non-monotonicity explicitly.** *"usually the optimal performance is neither
   at full global level nor full layer/filter level, but a weighted combination of two levels."*
   An interior optimum, published.
4. **It fixes it with the classically correct remedy** — hierarchical **partial pooling**, an L2
   penalty `λ_layer·Σ_l(α_l − α_g)² + λ_para·Σ_l Σ_p(α_p^l − α_l)²` pulling finer levels toward
   coarser ones.

### What CAM-HD does NOT contain — i.e. what is actually ours

* degenerate / size-1 groups, and any treatment of **1-D tensors** (BatchNorm scale and shift,
  biases) as a distinguished object;
* the **size-distribution vs alignment** decomposition, and the alignment null;
* **count-matching** — its levels differ in group count and in size distribution simultaneously,
  so its interior optimum is exactly the confound we spent the campaign removing;
* MetaOptimize (it predates the parent by four years).

### Why this makes our position BETTER, not worse

A referee who knows this literature asks: *"the classical remedy for noisy small groups is
shrinkage — Stein, Bühlmann credibility `Z = n/(n+k)`, empirical-Bayes moderation — and CAM-HD
already published partial pooling for exactly this. Why a hard rule instead of the soft,
classically optimal, already-published version?"*

**We can answer that with data, and the answer is on disk.** This campaign implemented
hierarchical partial pooling of per-group step sizes in three operators and **all three failed
their own controls** (MASTER-TABLE rows 68/69/70/74/75): `M0 shrink` is **WITHDRAWN** because the
operator saturates (it applies every step, so any λ ≥ 0.001 has a half-life ≤ 693 steps against
~50,000 — the sweep measured full pooling three times over); `M1 additive r` shows a clean
interior optimum at r ≈ 0.05-0.07 worth +1.07 pp, but **76% of it is an α₀=1e-6 escape-rate
artefact** (+1.011 pp becomes +0.239 pp at α₀=1e-3) and it **transfers to no other architecture
or dataset**; `zpool` rescues the per-weight arm by +11.13 pp and still lands **2.30 pp below
plain blk6**. MASTER-TABLE's own bottom line: *the r-dial is a meta-learning-rate knob, not a
pooling knob.*

That is a section, not an excuse. **Do not propose a new pooling design.**

## Two further precedents for special-casing 1-D tensors, all unjustified by their authors

Every one of these ships a **de facto tensor-level floor** that its own paper never names,
never ablates and never justifies. That is the gap our count-matched contrast fills.

| method | what it does to 1-D tensors | its stated reason |
|---|---|---|
| **Adam-mini** (2406.16793) | Algorithm 3 for non-Transformers is verbatim `for name, param in parameters: param_blocks[name] = param` — **one block per tensor**. The Transformer partition falls through to `else param_blocks[name] = param` for exactly the LayerNorm gains and biases. | none — its stated principle is Hessian sub-block **alignment**, which our permutation null refutes as the carrier at −0.009 pp (t −0.06) |
| **Adalayer** (2407.07972) | LayerNorm parameters are a **whole-tensor** block; biases are not learned at all | concludes adaptivity **on** the last layer and LayerNorm is *necessary* — note this is about merging **across** norm tensors vs shattering **within** one, and the paper must state that distinction explicitly |
| **Muon** | 1-D parameters (norm gains, biases), embeddings and the head are routed to **AdamW** | tensor **rank**, justified by the geometry of Newton-Schulz orthogonalisation |
| **LARS / LAMB** (1708.03888) | BatchNorm and bias parameters conventionally **exempted** from the layer-wise trust ratio | folklore: their norms are tiny and the ratio becomes numerically unstable |
| **bitsandbytes** (2110.02861) | tensors with **< 4096 elements** kept at 32-bit | *"small tensors … often contain highly variable parameters (biases) or parameters that require high precision (batch norm, layer norm)"* — precision, not grouping |
| **Shampoo** | `max_preconditioner_dim` (default 128) is a **CAP FROM ABOVE**; 1-D parameters get diagonal Adam, i.e. **per-coordinate** state | cubic preconditioner cost — the *opposite* direction from a floor |
| **Adafactor** | `min_dim_size_to_factor` is a threshold below which it does **not** factor, falling back to full per-coordinate second moments | memory, again the opposite direction |

**No method in the survey imposes a minimum group size on step sizes.** Two impose a maximum.

---

# 2026-09-17 — The BatchNorm-carrier line (mechanism rows 212–227): prior-art sweep, verified

*Added at CORRECTIONS 254; the sections above are unchanged. Two sweeps (normalisation / effective-LR angle, ~35
screened; meta-learned step size / granularity angle, ~32 screened) plus a verification pass that checked every arXiv id
against its abstract page (36/36 exist with the stated titles and authors) and every venue against arXiv
Comments/Journal-ref, official proceedings, OpenReview or the ACM DL. No PDF was read. Items that could not be checked are
marked UNVERIFIED or dropped. Discussion prep: `docs/LIMITS-PREP.md`.*

## The finding being positioned

A scalar (one shared) MetaOptimize step size collapses at the CIFAR-100 cells because the shared Lion meta-update's vote
is dominated by a few last-block normalisation-scale tensors (`ctd1`); isolating them rescues (`ciso1`), a matched
non-carrier BN set does not (`cdep1`); replicated on VGG11_bn, GroupNorm ResNet18 and residual-free PlainNet18; hold
interventions (`cvt4`–`cvt9`) show a large held carrier trajectory is sufficient to stall, graded in dose.

## Verified papers

| paper | id / URL | venue | relation | establishes |
|---|---|---|---|---|
| Arora, Li, Lyu — Theoretical Analysis of Auto Rate-Tuning by Batch Normalization | arXiv:1812.03981; openreview.net/forum?id=rkxQ-nA9FX | ICLR 2019 (forum read; decision page not read) | EXPLAINS-PART | only scale-variant params (gamma/beta, last layer) need a tuned LR; scale-invariant weights converge at any LR (verified in ar5iv body) |
| You, Gitman, Ginsburg — Large Batch Training of Convolutional Networks (LARS) | arXiv:1708.03888 | arXiv | EXPLAINS-PART / ADJACENT | ‖w‖/‖g‖ per layer 5.76 (conv1) vs 1345 (fc6) in AlexNet-BN (ar5iv Table 2); a global LR is limited by a few layers |
| Davis, Frank — Revisiting Batch Norm Initialization | arXiv:2110.13989; github.com/osu-cvl/revisiting-bn-init | ECCV 2022 (official README) | ALREADY-SHOWN (partial) | gamma init ≈ 0.1 and gamma LR ÷ 100 help (LR detail in README, not abstract) |
| Zhou, Wang, Luo, Feng, Li, Zhang — How Does BN Increase Collapsed Neural Network Filters? | arXiv:2001.11216 | UNVERIFIED | CANDIDATE MECHANISM (untested) | BN+ReLU filter collapse, probability ∝ lr², ∝ 1/gamma²; worse with large/adaptive LR |
| Kosson, Messmer, Jaggi — Rotational Equilibrium | arXiv:2305.17212 | ICML 2024 | EXPLAINS-PART | with WD under AdamW/Lion/SGDm, per-layer angular updates equilibrate |
| Lobacheva, Kodryan, Chirkova, Malinin, Vetrov — On the Periodic Behavior of NN Training with BN and WD | arXiv:2106.15739 | NeurIPS 2021 | ADJACENT; live alternative for the 250–430-epoch rescue decay | BN + WD periodic destabilisation |
| Li, Arora — An Exponential Learning Rate Schedule for Deep Learning | arXiv:1910.07454 | ICLR 2020 (openreview.net/forum?id=rJg8TeSFDH) | ADJACENT | exp LR ≡ standard schedules under BN + WD + momentum |
| van Laarhoven — L2 Regularization versus Batch and Weight Normalization | arXiv:1706.05350 | arXiv | ADJACENT | L2 on pre-norm weights only changes effective LR |
| Hoffer, Banner, Golan, Soudry — Norm matters | arXiv:1803.01814 | NeurIPS 2018 (arXiv journal-ref) | ADJACENT | norm / WD / LR coupling |
| Heo, Chun, Oh, Han, Yun, Kim, Uh, Ha — AdamP | arXiv:2006.08217 | ICLR 2021 | ADJACENT | momentum inflates scale-invariant norms, shrinking effective step |
| Mehmeti-Göpel, Wand — On the Weight Dynamics of Deep Normalized Networks | arXiv:2306.00700 | UNVERIFIED | ADJACENT | ELR gaps between layers hurt trainability past a critical LR |
| Kim, Choi, Jang, Lee, Jeong, Kim — Guidelines for the Regularization of Gammas in BN for Deep Residual Networks | arXiv:2205.07260; doi.org/10.1145/3643860 | ACM TIST 15(3), 2024 | ADJACENT (only lead for ResNet 3-vs-1) | gamma handling depends on position in the residual block (L2, not step size) |
| Mueller, Vlaar, Rolnick, Hein — Normalization Layers Are All That SAM Needs | arXiv:2306.04226 | NeurIPS 2023 | ADJACENT (design precedent for ISO vs CTL) | perturbing only norm-affine params beats all; matched sparse sets do not |
| Frankle, Schwab, Morcos — Training BatchNorm and Only BatchNorm | arXiv:2003.00152 | ICLR 2021 | ADJACENT | BN-affine-only training reaches 82% on CIFAR-10 |
| Fei, Dai, Li, Zou, Xiong — MimicNorm | arXiv:2010.09278 | UNVERIFIED | ADJACENT | the last BN layer provides autotuned learning rates (dataset details UNVERIFIED) |
| Jie, Gao, Vasnev, Tran — Adaptive Hierarchical Hyper-gradient Descent (CAM-HD) | arXiv:2008.07277 | journal not re-checked | ADJACENT | multi-level hypergradient LRs (FFN, LeNet-5, ResNet-18/34); no visible scalar collapse or dominance |
| Shea, Schmidt — Why Line Search when you can Plane Search? | arXiv:2406.17954 | arXiv | ADJACENT | per-layer step sizes help on some datasets, hurt on others; one layer's rate runs away (§4.5, HTML) |
| Cutkosky, Defazio, Mehta — Mechanic: A Learning Rate Tuner | arXiv:2306.00144 | NeurIPS 2023 | ADJACENT | scalar learned LR scale; per-layer named as open question; no layer/BN dominance reported |
| Ivgi, Hinder, Carmon — DoG is SGD's Best Friend | arXiv:2302.12022 | ICML 2023 | ADJACENT | per-layer L-DoG beats global DoG |
| Hägele, Hernández-Cano, Kosson, Jaggi — Improving NN Training by Decoupling the Magnitude and Direction of Weight Vectors | arXiv:2606.25971 | arXiv | ADJACENT | magnitude gains on their own LR, by design |
| Amid, Anil, Fifty, Warmuth — Step-size Adaptation Using Exponentiated Gradient Updates | arXiv:2202.00145 | not checked | ADJACENT | global scale + per-coordinate gains, multiplicative updates |
| Baydin, Cornish, Martinez Rubio, Schmidt, Wood — Online Learning Rate Adaptation with Hypergradient Descent | arXiv:1703.04782 | ICLR 2018 | ADJACENT | scalar hypergradient LR works on VGG/CIFAR-10 in its setting |
| Chu, Gao, Ye, Udell — Provable and Practical Online LR Adaptation with Hypergradient Descent | arXiv:2502.11229 | not checked | ADJACENT | HDM instability analysis (convex) |
| Chen, Wang, Ba — Differentiable Self-Adaptive Learning Rate | arXiv:2210.10290 | not checked | ADJACENT | hypergradient LR instability |
| Metz, Maheswaranathan, Nixon, Freeman, Sohl-Dickstein — Understanding and correcting pathologies in the training of learned optimizers | arXiv:1810.10180 | ICML 2019 (PMLR 97) | ADJACENT | truncated meta-gradients biased / exploding |
| Kovaleva, Kulshreshtha, Rogers, Rumshisky — BERT Busters | arXiv:2105.06990 | not checked | ADJACENT (structural) | outlier dimensions ARE LayerNorm scaling factors and biases; about pruning fragility, not step sizes |
| Yu, Wang, Shan, Reed, Wan — The Super Weight in LLMs; Sun, Chen, Kolter, Liu — Massive Activations in LLMs | arXiv:2411.07191; arXiv:2402.17762 | not checked | ADJACENT | a handful of parameters/activations carry disproportionate control (inference) |

Parent paper (arXiv:2402.02342), checked in the local text: no "batch norm" string anywhere; §7.3 ImageNet reports
blockwise no better than scalar; Appendix Table 4 includes a scalar (SGDm, Lion) row (momentum parsed as 0.9, column
alignment UNSURE).

**Dropped as unverified:** Nado et al. (arXiv:2102.06356) "LAMB diverges on all params incl. BN"; "TF LARS excludes BN
from layer adaptation by default" (both exclusion lists default to None; BN/bias is only an example — cite as commonly
configured); Bjorck et al. (arXiv:1806.02375) last-layer-BN claim; Semantic Scholar's 6 MetaOptimize citers.

## Novelty assessment

**Already known — cite, do not claim.**
1. BN gamma benefits from its own, smaller LR (Davis & Frank). "Separate group for gamma helps" is not new as a practice.
2. Scale-variant tensors (gamma/beta, last layer) are where LR sensitivity lives in normalised nets (Arora–Li–Lyu); so it
   is predictable that carriers are norm scales, not conv kernels.
3. One global LR can be limited by a few layers with different scale (LARS); per-layer beats global in several step-size
   methods (L-DoG, CAM-HD), and finer is not always better (Shea & Schmidt; parent §7.3).
4. A tiny norm-affine subset can control an optimiser-level effect where a matched sparse set cannot (SAM-ON).
5. A large LR on BN parameters can collapse filters (Zhou et al.) — candidate mechanism for the dose result, untested.
6. BN + WD produces periodic destabilisations (Lobacheva et al.); WD is 0.1 on the base in every campaign run and is
   applied to gamma (`patches/HF_patched.py` 592–598), so this is a live alternative, not background.

**Looks new (nothing found pre-empts it).**
(a) A meta-learned SHARED step size whose meta-update vote is shown, by per-tensor attribution, to be dominated by a few
identified last-block normalisation-scale tensors. (b) Rescue by isolating only those tensors, with a matched non-carrier
control that does not rescue, replicated across BN, GN and residual-free nets. (c) Hold interventions dissociating dose
and route, with a graded dose effect. arXiv searches combining hypergradient / meta-learned LR with normalisation or
per-layer dominance returned 0 hits; Mechanic names per-layer as future work; MetaOptimize never mentions BN.

**Framing.** A referee will say "of course the gammas — the only scale-variant parameters". The answer is `cdep1` (other
gammas do not rescue) and last-block specificity. If carrier gammas are shown to go to ~0 under the large held dose
(Zhou et al.), novelty narrows to carrier selection and the vote. If S1/N4 (LIMITS-PREP §5.1) show the collapse needs
momentum 0.99 or coupled WD on norm scales, the finding must be stated as a mechanism under that configuration.

---

## Sweep 2026-09-20 — the WEIGHT-DECAY VALUE axis, and coupled vs decoupled decay (CORRECTIONS 281, batch `cwd5`)

*Targeted sweep before registering the coupled weight-decay ladder. Queries and per-paper verdicts are recorded in
full at CORRECTIONS 281.1; this section keeps the two findings that change how a result may be WRITTEN. No `.pdf` was
fetched; arXiv abstract pages and search-result summaries only.*

**1. "There is a critical weight decay for normalised training" is ALREADY OWNED — cite it, do not claim it.**
Li, Zhou, Xu, *Weight-norm Criticality: A Mechanism for Loss Spikes Induced by the Normalization and Weight Decay*
(arXiv:2607.21005, 23 Jul 2026) argues that as the weight-decay coefficient rises, the norms of scale-invariant
weights are driven toward zero, sharpness rises, and training destabilises — a **value threshold at the CLASS
grain**, with no numerical value, no per-tensor exemption, no meta-learned step size and no granularity gap. It was
already listed as ADJACENT at CORRECTIONS 275.1; on the value axis it is the DIRECT neighbour.
**Consequence for the campaign:** a `THRESHOLD-*` verdict from `cwd5` may NOT be written as a discovery that weight
decay has a critical value. It must be written as *"the campaign's cell sits above / below the value at which this
configuration breaks"* — a SCOPE and DIAGNOSTIC statement about our own configuration, which is exactly the framing
the area chair asked for.

**2. A decoupled-decay arm would confound the coupling with the effective learning rate.**
Kosson, Messmer, Jaggi, *Rotational Equilibrium: How Weight Decay Balances Learning Across Neural Networks*
(arXiv:2305.17212, ICML 2024): on scale-invariant vectors, weight decay and gradient updates reach an equilibrium in
which the expected rotation — a proxy for the EFFECTIVE learning rate — is set by the decay, and the paper attributes
part of the AdamW-vs-Adam+L2 difference to exactly this. So swapping coupled for decoupled decay moves the effective
step size of every normalisation scale, which is the quantity under study. Together with the harness fact that
`SGDm_base_update` multiplies the decay by the LEARNED step size and bakes `(1 - wd*a)` into the meta trace — so no
single lambda can match the coupled dose `wd*a` — this is why `cwd5` DESCOPES the decoupled arm rather than running a
confounded one (CORRECTIONS 281.2). `DECOUPLED-NOT-TESTED` is stamped on every `cwd5` FINAL.

**3. Loshchilov & Hutter's id, verified in session:** *Decoupled Weight Decay Regularization*, **arXiv:1711.05101**,
ICLR 2019. It decouples the decay from the optimiser step so the optimal decay factor stops depending on the learning
rate. Nothing in it concerns a shared vs per-group META-LEARNED step size, and it does not bear on whether a collapse
has a decay-value threshold.

**Still looks new (nothing found pre-empts it):** a weight-decay VALUE threshold for a **meta-learned shared-step-size
collapse**, and the **scalar-vs-layerwise granularity gap measured as a function of the coupled decay** — the curve
`cwd5` exists to produce.

---

## Sweep 2026-09-22 — SHORT-HORIZON BIAS as a rival account of the scalar collapse (CORRECTIONS 301, batch `csh1`)

*Targeted sweep before registering the short-horizon γ control (ICML-PLAN row 1.20, threat T-C). Web search and
search-result summaries / abstract pages only; no `.pdf` fetched, nothing downloaded. Queries:
(1) "short-horizon bias meta-learned learning rate hypergradient horizon truncation collapse step size";
(2) "hypergradient descent trace decay factor gamma forgetting IDBD step-size adaptation weight decay interaction";
(3) "MetaOptimize Sharifnassab Salehkaleybar Sutton gamma trace decay step-size optimization";
(4) "\"MetaOptimize\" discount factor gamma ablation step size collapse weight decay";
(5) "truncated backpropagation bias online learning rate adaptation weight decay shortens effective horizon meta-gradient".*

**1. The rival mechanism is owned, and its DIRECTION matches the collapse.** Wu, Ren, Liao, Grosse, *Understanding
Short-Horizon Bias in Stochastic Meta-Optimization* (arXiv:1803.02021, ICLR 2018): meta-objectives defined over
horizons orders of magnitude shorter than training bias stochastic learning-rate meta-optimisation toward SMALL step
sizes (analysed on a noisy quadratic). A collapsed scalar step at the −15 floor is the extreme of that direction, so the
account cannot be dismissed on sign alone. Nothing in it concerns α-scaled weight decay acting as the horizon, a shared
vs per-layer step size, or a matched-horizon control.

**2. Adjacent, not pre-emptive.** Truncated-backprop bias in meta-gradients (e.g. *An Investigation of the Bias-Variance
Tradeoff in Meta-Gradients*, arXiv:2209.11303; adaptive truncation, arXiv:1905.07473) establishes that short truncations
bias the outer gradient — the general fact, not our configuration. FADE (*Learning to Forget: Continual Learning with
Adaptive Weight Decay*, arXiv:2604.27063) meta-learns a per-parameter decay alongside IDBD step sizes; it does not test
whether a decay's shortening of the step-size trace, as opposed to its shrinking of the weights, harms the step size.
The parent (arXiv:2402.02342) defines its regret through a discounted sum of future losses (the harness's `--gamma`);
nothing found in its abstract or summaries runs a γ < 1 control against a decay-induced collapse.

**3. Internal prior art, on file.** The only γ < 1 runs in the corpus are `d3_g999_s0/s1` (CIFAR-10 ResNet18,
weightwise, γ 0.999, no β clip, collapsed to 10.0 %); CORRECTIONS §5 recorded that this control "failed identically"
to γ 1, refuting a trace-overflow cause. Different grain, dataset and clip; it does not decide the scalar question.

**Verdict.** The general bias is known and must be cited; whether shortening the horizon WITHOUT the decay dose
reproduces THIS collapse, at a horizon matched to the collapsing arm's own realised (1 − κα), is not answered anywhere
found. The batch is kept at its planned size plus one bracket cell (18 runs), not shrunk.

## Sweep 2026-09-22 — per-grain re-tuning, tuning-protocol dependence and selection bias (CORRECTIONS 300, batch `crt1`, Track B)

*Targeted sweep before registering the 5e-4 re-tune of the audit's core cell. Web search and arXiv abstract pages only;
no `.pdf` fetched, nothing downloaded (the arXiv abstract tool returned "not found" for every id tried, so the abstract
pages were read directly).* **Queries:** (1) "hypergradient per-parameter vs scalar learning rate meta step size tuning
fairness comparison"; (2) "benchmarking optimizers hyperparameter tuning budget selection bias validation tuning
protocol comparison conclusions change"; (3) "Lion optimizer sign update learning rate initial value travel distance
meta-learned step size initialization sensitivity hypergradient"; (4) "per-layer learning rate groups vs single global
learning rate retuned weight decay ablation tuning artifact CIFAR ResNet"; (5) "winner's curse best-of-k hyperparameter
selection optimistic bias expected maximum Gaussian model comparison deep learning"; (6) "learned step size granularity
scalar vs blockwise vs per-parameter meta step size sensitivity weight decay 5e-4 hypergradient descent CIFAR-10".

**Found, read at abstract level:**
* Sivaprasad, Mai, Vogels, Jaggi, Fleuret, *Optimizer Benchmarking Needs to Account for Hyperparameter Tuning*
  (arXiv:1910.11758, ICML 2020) — which optimiser "wins" depends on the tuning protocol and budget. **MOTIVATES the
  batch, does not answer it:** it is the general reason a ranking obtained at hyperparameters tuned elsewhere (here: at
  wd 0.1) must be re-read after per-condition tuning; it says nothing about meta-learned step-size grains.
* Schmidt, Schneider, Hennig, *Descending through a Crowded Valley* (arXiv:2007.01547) — trying several optimisers at
  defaults does about as well as tuning one. **ADJACENT**: same lesson (tuning changes rankings), different objects.
* Im, Savin, Cho, *Online hyperparameter optimization by real-time recurrent learning* (arXiv:2102.07813) — per-layer
  vs global online hyperparameter adaptation (per the search summary, layerwise beat global on CIFAR-10); the abstract
  page itself does not state the comparison or its tuning. **ADJACENT**, not a test of a scalar-vs-partition gap under
  re-tuning at a fixed decay.
* Chen et al., *Symbolic Discovery of Optimization Algorithms* (Lion, arXiv:2302.06675) — Lion's sign update has a
  uniform per-coordinate magnitude equal to its learning rate. **USED IN THE DESIGN**: with Lion as the META optimiser
  every log step size moves by exactly the meta step size per step, so ms sets both rate and REACH, and alpha0 sets the
  start — which is why `crt1` adds an alpha0 point (300.3).
* The winner's-curse / post-selection literature (search summaries only, e.g. arXiv:2605.05973, arXiv:2605.18887) — the
  best of k noisy estimates is optimistically biased. **USED IN THE DESIGN** as the standard fact behind the registered
  bound B = E[max of 4 iid N(0,1)] x sigma / sqrt(3); no specific paper's method is adopted.
* Already on file: Kosson et al. *Rotational Equilibrium* (arXiv:2305.17212) — at low decay the effective step on
  scale-invariant tensors is not set by the decay, one plausible reason the grains' optimal step sizes move with wd.

**Verdict:** nothing found tests whether a scalar-vs-partition ranking of META-LEARNED step sizes at a fixed decay
survives per-grain re-tuning of the meta step size and initial step size. The general point (rankings depend on
tuning) is owned by Sivaprasad et al. and Schmidt et al. and must be cited, not claimed. The batch is not a replication
of published work and is NOT shrunk on prior-art grounds.
