# Prior-art check: two proposed extensions to MetaOptimize

Date: 2026-08-21. Method: arXiv full-text/metadata search + web search, ~30 queries across the
hypergradient, IDBD/step-size-adaptation, learned-optimizer, learning-rate-schedule, and
block-adaptive-optimizer literatures. Verdicts are deliberately unkind.

Baseline context: MetaOptimize (Sharifnassab, Salehkaleybar & Sutton, arXiv:2402.02342, ICML 2025),
α = exp(β), β driven by a γ-discounted meta-gradient with an eligibility trace.

---

## IDEA 1 — Schedule as prior, meta-learn the residual: α_t = cosine(t) · exp(β_t)

### VERDICT: **PARTIALLY DONE.** Not published in this exact form, but the *shape* is crowded.

Three separate literatures have already built "fixed schedule × online-learned multiplicative
factor". Nobody has built it with (a) a **meta-gradient**-driven residual, (b) **per-block**, or
(c) motivated as a **short-horizon-bias correction**. That intersection is genuinely unoccupied —
but it is a narrow gap between three occupied cells, not open ground.

### Closest prior work

**1. Mechanic (Cutkosky, Defazio & Mehta, NeurIPS 2023, arXiv:2306.00144)** — the single most
dangerous hit. Its stated contribution is tuning "the learning rate **scale factor** of any base
optimization algorithm **and schedule**". That is literally α_t = schedule(t) · s_t with s_t learned
online, evaluated across varying batch sizes, schedules, and base optimizers. Differences: s_t is
derived from an **online-convex-optimization reduction** (a parameter-free / coin-betting style
wrapper), **not** a meta-gradient with an eligibility trace; and the paper frames s_t as a single
scale factor rather than a per-block quantity. *Caveat: I confirmed the global framing from the
abstract/OpenReview page only — I did not read the full method section, and I could not rule out a
per-layer variant in the released implementation. Check this before writing an intro claiming
novelty on "multiplicative correction to a schedule."*

**2. D-Adaptation (Defazio & Mishchenko, ICML 2023, arXiv:2301.07733) and Prodigy (Mishchenko &
Defazio, arXiv:2306.06101).** Both set the step size as γ_t · d_t, where γ_t is a user-supplied
schedule (cosine is the recommended default) and d_t is an online lower-bound estimate of the
initialization-to-solution distance D. Again exactly "schedule × learned scalar", again global,
again not meta-gradient-driven. Combined with Mechanic, these establish that "keep the schedule,
learn the scale" is standard practice in the learning-rate-free community, not a new framing.

**3. LARS / LAMB (You, Gitman & Ginsburg, arXiv:1708.03888; You et al., ICLR 2020).** α_{layer,t} =
schedule(t) × trust-ratio(‖w_layer‖ / ‖g_layer‖). This is precisely "global schedule × **per-block**
multiplicative correction" — the structural form Idea 1 proposes — with the correction
*hand-designed* rather than meta-learned. This is the strongest structural precedent and the
obvious ablation a reviewer will demand: does a meta-learned residual beat a norm-ratio residual?

**4. Adaptive Hierarchical Hyper-gradient Descent / CAM-HD (Jie, Gao, Vasnev & Tran,
arXiv:2008.07277, 2020).** Hypergradient-learned learning rates at global, layer, unit, and
parameter granularity, fused as α\* = γ₁α̂_p + γ₂α̂_l + γ₃α̂_g with the γ's themselves learned. This is
the closest existing "coarse prior + fine residual" construction in the hypergradient lineage.
Two differences that preserve room: the coarse level is itself *learned*, not a fixed schedule, and
the combination is **additive**, not multiplicative. Results are modest (ResNet-34 93.47% vs 92.93%
for SGDN on CIFAR-10) and the paper never re-partitions.

**5. Baydin, Cornish, Martínez Rubio, Schmidt & Wood, ICLR 2018 (arXiv:1703.04782); Chandra, Xie,
Ragan-Kelley & Meijer, NeurIPS 2022 (arXiv:1909.13371).** Hypergradient descent, including a
**multiplicative** update rule (noted as rescaling-invariant and faster-adapting than the additive
form), and its recursive stacking. Neither uses a fixed schedule as a prior — they position
themselves as schedule *replacements*. MetaOptimize contains Baydin's HD as the γ=0 special case.

Supporting: Wu, Ren, Liao & Grosse, ICLR 2018 (arXiv:1803.02021) — short-horizon bias, and
critically the direction of the bias: **toward small step sizes**. Agarwal, Anil, Hazan, Koren &
Zhang (arXiv:2002.11803) — "grafting", which decomposes an update into magnitude-from-one-optimizer
× direction-from-another; the closest thing to an explicit LR decomposition study. Henheik, Eimer &
Lindauer, "Revisiting Learning Rate Control" (arXiv:2507.01724) — finds online LR-control methods
"perform very well on selected deep learning tasks but are not reliable across settings", i.e.
independent confirmation of the (a) result.

### What is left that is novel

1. Residual driven by the **discounted meta-gradient with eligibility trace** (the MetaOptimize/IDBD
   mechanism) rather than an OCO regret reduction or a distance estimate. Nobody has done this.
2. **Per-block** residual on a global schedule where the correction is *learned* — the meta-learned
   analogue of LARS. This is the cleanest novelty claim and it couples directly to your granularity
   work.
3. The **framing**: schedule supplies the long-horizon component that Wu et al. prove the
   meta-gradient cannot see; the meta-gradient supplies only the local correction it *can* see. That
   is a principled division of labour nobody has argued for explicitly. MetaOptimize's own paper
   treats hand-crafted schedules purely as competitors ("MetaOptimize automatically discovers similar
   patterns"), never as priors.

### Single strongest reason it fails

**The residual's honest optimum is exp(β)=1, so the best plausible outcome is "ties the tuned
baseline" — which is not a result.** And the likely outcome is worse than a tie, for a specific
reason: short-horizon bias points *downward*. Wu et al.'s finding is that greedy short-horizon
meta-objectives bias toward **small** step sizes. Your β_t has no access to t/T and therefore no way
to know the schedule is already decaying; its greedy pull will *compound* cosine's decay, so
α_t = cosine(t)·exp(β_t) under-shoots late in training exactly where your (a) measurement says the
gap already widens with horizon. The fixed point is then set entirely by the meta-step size — a
hyperparameter you must now tune, reintroducing the tuning burden MetaOptimize existed to remove.

**Pre-register the control:** the schedule-only arm (exp(β) frozen at 1) and a LARS-style
hand-designed residual arm. If the meta-learned residual doesn't beat *both*, the idea is dead and
you will know within one cycle.

---

## IDEA 2 — Granularity from measured meta-gradient correlation, not architecture

### VERDICT: **PARTIALLY DONE — and one 2025 paper lands uncomfortably close.**

Data-driven, online, re-clustered parameter grouping for learning-rate sharing **is published**
(SGG, June 2025). What is *not* published is clustering by pairwise **meta-gradient correlation /
sign-agreement between coordinates**, or partitions that cross architectural boundaries, or any
theory of the optimal partition for step-size estimation under correlated coordinates.

### Closest prior work

**1. SGG — "Taming LLMs by Scaling Learning Rates with Gradient Grouping" (Li, Tian, Wang, Jin, Liu,
Zhang & Xu, arXiv:2506.01049, June 2025).** The direct hit. An optimizer wrapper that runs
**mini-batch k-means over momentum vectors within each layer**, **re-clusters every 5–10% of
training**, and applies cluster-specific multiplicative scaling to the per-parameter learning rates
(α ← α · S[C]). Evaluated on 60M–1B LLMs; beats Adam-mini on C4 across all scales. Four ways your
idea still differs: (i) SGG clusters on momentum **magnitude/value**, not on pairwise **correlation
or sign-agreement between coordinates**; (ii) grouping is **within-layer only** — the partition is
still architecturally bounded; (iii) it clusters **gradients**, not **meta-gradients**; (iv) it
*scales* per-parameter rates rather than deciding which coordinates *share* one. These are real
differences, but a reviewer will demand SGG as a baseline and will ask why correlation beats
magnitude. **Have that answer ready.**

**2. Adam-mini (Zhang, Chen, Li, Ding, Wu, Kingma, Ye, Luo & Sun, arXiv:2406.16793, ICLR 2025).**
Partitions by the smallest dense sub-block of the Hessian — Q/K by head, V whole, MLP by layer.
Crucially, it *states the principle* your idea wants to make measurable: parameters within a densely
coupled block are the ones that should share a rate. Its partition is **assumed** from architecture,
never estimated. Idea 2 is best positioned as the empirical-estimation version of Adam-mini's
assumed structure.

**3. "Towards Quantifying the Hessian Structure of Neural Networks" (Dong, Zhang, Yao & Sun,
arXiv:2505.02809, 2025).** The nearest thing to *theory on the optimal partition*. Decomposes
near-block-diagonality into a static force (architecture) and a dynamic force (training), with
off-diagonal influence decaying as O(1/C) / O(1/C²) in class count. Read this before committing:
it argues architecture **largely determines** the blocks, which partially undercuts the premise that
measurement will discover non-architectural structure. On CIFAR-10, C=10 — a regime where its theory
says off-diagonal coupling is *not* yet negligible, which is mildly in your favour.

**4. Adalayer / blockwise BAGM (Zhao, Morwani, Brandfonbrener, Vyas & Kakade, arXiv:2407.07972).**
Layerwise Adam; explicitly generalises to averaging the second moment over a "block" that may be a
subset of a layer — but blocks are hand-chosen. Finds adaptivity matters mainly for the last layer
and LayerNorm, i.e. that the *right* partition is highly non-uniform. Good evidence that partition
choice has real leverage.

**5. LANTON — "Noise-Adaptive Layerwise Learning Rates" (Hao, Gong, Xu, Wang & Liu,
arXiv:2510.14009, 2025).** Dynamically estimates gradient variance per layer and assigns layerwise
rates that adapt over training — a *measured* statistic driving the rate, with an *architectural*
partition. Together with SGG this brackets your idea from both sides.

Also relevant: CAM-HD (arXiv:2008.07277) for multi-granularity fusion with learned weights, though
its granularity levels are fixed and never re-partitioned; and the gradient-conflict line
(GradDrop, PCGrad) which uses sign agreement across **tasks**, not across **coordinates**.

### What is left that is novel

1. **The statistic.** Pairwise meta-gradient sign-agreement/correlation *between coordinates* as the
   clustering criterion. Not done. SGG's momentum-magnitude k-means is a different object.
2. **Crossing architectural boundaries.** Every method found — SGG, Adam-mini, Adalayer, LANTON,
   CAM-HD — keeps groups inside a layer or tensor. A cluster that spans layers would be new.
3. **Split/merge adaptive granularity** with a measured stopping criterion. SGG re-clusters at fixed
   k; nothing adaptively chooses the *number* of blocks.
4. **The theory (this is your real contribution).** Nobody has written the bias–variance analysis of
   partition choice for step-size *estimation* under correlated coordinates: the 1/√N noise-averaging
   assumption holds only at independence, and your measurement (53.1% sign agreement vs a
   50.0000 ± 0.0015% null) supplies the effective N. That result — "the standard justification for
   coarse granularity is quantitatively false, here is the correction" — is publishable even if the
   clustering algorithm built on top of it fails.

### Single strongest reason it fails

**The correlation estimate is O(d²) and statistically dead at the effect size you measured.** You
have 11.17M coordinates and a 3.1pp deviation from chance. Per pair, a sign-agreement estimate over
T samples has standard error ≈ 0.5/√T, so separating 53.1% from 50% needs T ≈ 260 samples for a
single σ and thousands for a clustering-usable signal — per pair, over O(d²) pairs, while the
correlation structure itself drifts (SGG re-clusters every 5–10% of training precisely because it
does). Any affordable estimator — sketched, low-rank, or sampled — will return clusters dominated by
estimation noise, and a noise-driven partition is a random partition. The Adam-mini / Hessian-
structure line then predicts you lose to the architectural baseline, because architecture is a
strong, free, **zero-variance** prior. And the failure mode is silent: if most of the 3.1pp mass
sits *within* existing architectural blocks, your measured partition will expensively re-derive
"layers" and you will report a null while believing the method is untested.

**Cheapest kill-test:** before building any clustering, take the meta-gradients you already have,
compute sign-agreement *within* vs *across* existing architectural blocks, and check whether the
3.1pp excess is explained by architecture. If it is, Idea 2 is dead for free.

---

## Bottom line

Neither idea is scooped outright. Idea 1 is the weaker of the two: the mechanism is unoccupied but
the shape is crowded (Mechanic, D-Adaptation/Prodigy, LARS) and the expected outcome is a tie with
the baseline. Idea 2 has a live novelty claim on the *statistic* and a genuinely open theory
question, but a 2025 paper (SGG) already owns "dynamic measured-statistic clustering for LR
sharing", and the estimation problem at your measured effect size is brutal.

**The most defensible paper in this material is not either algorithm — it is measurement (b).** The
1/√N independence assumption underpinning coarse step-size granularity is quantitatively false, you
have 11.17M samples proving it, and no one in the Adam-mini / Adalayer / SGG line has measured it.
Lead with that; make the clustering algorithm the application, not the claim.

## Citations

```bibtex
@misc{cutkosky2023mechanic, title={Mechanic: A Learning Rate Tuner}, author={Ashok Cutkosky and Aaron Defazio and Harsh Mehta}, year={2023}, eprint={2306.00144}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{defazio2023learningratefree, title={Learning-Rate-Free Learning by D-Adaptation}, author={Aaron Defazio and Konstantin Mishchenko}, year={2023}, eprint={2301.07733}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{mishchenko2023prodigy, title={Prodigy: An Expeditiously Adaptive Parameter-Free Learner}, author={Konstantin Mishchenko and Aaron Defazio}, year={2023}, eprint={2306.06101}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{you2017large, title={Large Batch Training of Convolutional Networks}, author={Yang You and Igor Gitman and Boris Ginsburg}, year={2017}, eprint={1708.03888}, archivePrefix={arXiv}, primaryClass={cs.CV}}
@misc{jie2020adaptive, title={Adaptive Hierarchical Hyper-gradient Descent}, author={Renlong Jie and Junbin Gao and Andrey Vasnev and Minh-Ngoc Tran}, year={2020}, eprint={2008.07277}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{baydin2017online, title={Online Learning Rate Adaptation with Hypergradient Descent}, author={Atilim Gunes Baydin and Robert Cornish and David Martinez Rubio and Mark Schmidt and Frank Wood}, year={2017}, eprint={1703.04782}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{chandra2019gradient, title={Gradient Descent: The Ultimate Optimizer}, author={Kartik Chandra and Audrey Xie and Jonathan Ragan-Kelley and Erik Meijer}, year={2019}, eprint={1909.13371}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{wu2018understanding, title={Understanding Short-Horizon Bias in Stochastic Meta-Optimization}, author={Yuhuai Wu and Mengye Ren and Renjie Liao and Roger Grosse}, year={2018}, eprint={1803.02021}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{agarwal2020disentangling, title={Disentangling Adaptive Gradient Methods from Learning Rates}, author={Naman Agarwal and Rohan Anil and Elad Hazan and Tomer Koren and Cyril Zhang}, year={2020}, eprint={2002.11803}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{li2025taming, title={Taming LLMs by Scaling Learning Rates with Gradient Grouping}, author={Siyuan Li and Juanxi Tian and Zedong Wang and Xin Jin and Zicheng Liu and Wentao Zhang and Dan Xu}, year={2025}, eprint={2506.01049}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{zhang2024adammini, title={Adam-mini: Use Fewer Learning Rates To Gain More}, author={Yushun Zhang and Congliang Chen and Ziniu Li and Tian Ding and Chenwei Wu and Diederik P. Kingma and Yinyu Ye and Zhi-Quan Luo and Ruoyu Sun}, year={2024}, eprint={2406.16793}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{zhao2024deconstructing, title={Deconstructing What Makes a Good Optimizer for Language Models}, author={Rosie Zhao and Depen Morwani and David Brandfonbrener and Nikhil Vyas and Sham Kakade}, year={2024}, eprint={2407.07972}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{hao2025noiseadaptive, title={Noise-Adaptive Layerwise Learning Rates}, author={Jie Hao and Xiaochuan Gong and Jie Xu and Zhengdao Wang and Mingrui Liu}, year={2025}, eprint={2510.14009}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{dong2025towards, title={Towards Quantifying the Hessian Structure of Neural Networks}, author={Zhaorui Dong and Yushun Zhang and Jianfeng Yao and Ruoyu Sun}, year={2025}, eprint={2505.02809}, archivePrefix={arXiv}, primaryClass={cs.LG}}
@misc{sharifnassab2024metaoptimize, title={MetaOptimize: A Framework for Optimizing Step Sizes and Other Meta-parameters}, author={Arsalan Sharifnassab and Saber Salehkaleybar and Richard Sutton}, year={2024}, eprint={2402.02342}, archivePrefix={arXiv}, primaryClass={cs.LG}}
```
