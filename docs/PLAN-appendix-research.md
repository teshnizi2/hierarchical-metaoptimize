# Research Plan — Hierarchical MetaOptimize, post-mortem and reformulation

**Status: the proposal's premise is falsified at CIFAR-10 scale. This is good news, not bad — but the project must be re-aimed now, before another GPU-hour is spent.**

---

## 0. The reframe in one paragraph

The measured grid does not say "layerwise hurts." It says something sharper and more publishable: **the marginal value of step-size granularity is non-monotone, saturates very early, and the saturation point is set by how much per-coordinate adaptivity the base optimizer already supplies.** Under SGDm, m=1→6 buys +3.5pp; 6→62 buys nothing; 62→n is catastrophic. Under AdamW, m=1→6 buys nothing (possibly negative), 6→62 nothing, 62→n costs ~6pp. That is a two-axis story (granularity × base-optimizer adaptivity) with an interior optimum, plus a hard failure at the fine end. The hierarchical fix is still worth building, but it must be aimed at the failure that actually exists (m→n), not the one in the proposal (m=layerwise).

Everything below is prioritized on that reading.

---

## 1. What the current data actually supports (and what it doesn't)

| | m=1 | m=6 | m=62 | m=n |
|---|---|---|---|---|
| SGDm | 88.09 | **91.56** | 91.34 | collapse (1/3 seeds confirmed) |
| AdamW | 92.13† | 91.86 | 91.83 | 86.05 |

† Gate 0, n=2, **different campaign**. This is the single most load-bearing number in the project and it is not comparable. Re-run it under Gate-1 conditions, 3 seeds, before drawing the conclusion above. If AdamW-scalar lands at ~92 while AdamW-6-block is 91.9, the "adaptivity substitutes for granularity" story is confirmed and it is the paper's spine. If it lands at 90, the story collapses.

**Two things nobody has flagged that will get the paper rejected if left alone:**

1. **Every arm is ~3pp below a competently tuned baseline.** Standard ResNet-18 / CIFAR-10 / SGD+momentum / cosine / wd 5e-4 / 100 epochs with the same augmentation is 94.5–95.3%. Your best arm is 91.9. So the entire granularity comparison is happening in a regime dominated by something else (bs=100, no schedule, κ=0.1 coupled decay, α₀=1e-6 warmup cost). Reviewers will ask "why is your 91.9 interesting when SGD+cosine gets 95?" Locate the ceiling **first** — it may be that the parent paper's CIFAR-10 numbers sit in the same place, in which case the honest framing is "schedule-free / online setting" and you say so in the abstract.
2. **"Best test accuracy over epochs" is a biased estimator, and the bias is not equal across arms.** It rewards noisy trajectories that spike, and it credits a collapsing weightwise run with its pre-collapse peak (70.09 → 10.00 becomes "70.09"). The bias grows with trajectory variance, which is exactly the quantity that differs between granularities. This metric is silently confounded with the treatment. Fix before any further analysis (§3).

---

## 2. Q1 — Experiments in priority order

Costs in "CIFAR-runs" (one ResNet-18 / 100-epoch / MetaOptimize run; measure the real number before trusting anything below — call it 1.2–1.8 A100-h, ~3 h on an L4).

### P0 — Correctness insurance (≈0 GPU, 1 day) — **do this first, it is cheap and it can void everything**

The finer-granularity results rest entirely on code the original authors never executed. Before you publish a curve from it, prove the implementation is right with **exact** tests, not eyeballed curves:

- **Sum identity.** From identical `(w, H, batch)`, the layerwise/weightwise meta-gradients must satisfy `Σ_b z_b == z_scalar` to floating-point tolerance. This is exact, costs one step, and is the strongest single check.
- **Partition invariance.** Run the weightwise code path with a partition of exactly one block, same seed → must reproduce the scalar run bit-for-bit. Same for a 6-block partition through the weightwise path vs. the native blockwise path.
- **Tied-β control.** Compute per-coordinate `z_b` but force all β equal → must match scalar. This separates "the partition machinery is wrong" from "fine granularity genuinely behaves differently."
- **Finite-difference check.** For 3–5 blocks, perturb β_b by ±ε and compare the measured change in the one-step loss against `z_b`. Catches sign errors and missing factors.
- **η=0 control.** Weightwise with the meta-step disabled is just fixed α₀=1e-6 SGDm. It should train badly but must not collapse. If it collapses, the collapse is not about meta-learning at all.

Also: assert epochs-completed in every run manifest (the `--max-time` truncation defect must be structurally impossible to repeat, not remembered), and emit `{git SHA, config hash, seed, epochs, wall-clock}` per run so truncated runs are auto-excluded from analysis rather than silently averaged in.

### P1 — Complete and de-confound the grid (≈160 runs)

The full fair-comparison campaign of §3: base ∈ {SGDm, AdamW} (add Lion and RMSProp if throughput allows — the adaptivity axis wants ≥3 points) × granularity ∈ {1, 6, 62, n} × a **fixed, identical (η, α₀) grid** × 5 confirmation seeds, plus tuned-fixed-LR and tuned-cosine baselines at matched search budget. This single campaign answers Q2, kills the tuning confound, and produces the paper's Table 1. It is the highest-value ~250 A100-h you will spend.

### P2 — The granularity curve as a *curve*, with a randomized control (≈60 runs)

Four granularity points is not a curve. Run m ∈ {1, 2, 6, 20, 62, ~500 (channel-wise), ~10⁴, n} at the per-arm best (η, α₀) from P1. Then the control that makes it science:

- **Random partitions at matched cardinality.** Partition all 11.17M coordinates uniformly at random into m blocks of equal size, for the same m values. Random-m has the same block count and similar block sizes but no semantic structure. If random-62 ≈ layerwise-62, the effect is **statistical (block size / SNR)**. If layerwise-62 ≫ random-62, the effect is **structural (layers really are the right unit)**. Nobody has run this control, in this literature or the parent paper, and it cleanly separates H1 from every structure-based story.

### P3 — Horizon (≈24 runs) — the cheapest test of H1's central prediction

H1 predicts degradation accumulates with step count. CIFAR-10 at bs=100 is 50k steps; ImageNet-90ep is ~450k. Run {6, 62, n} × {100, 300, 600 epochs} × 3 seeds. If layerwise degrades relative to 6-block as horizon grows, you have reproduced the ImageNet phenomenon at 1/50 the cost and the parent paper's null becomes explicable. **This is the highest-information-per-GPU-hour experiment in the whole plan.** Do it before ImageNet is even discussed.

### P4 — Weightwise collapse mechanism (≈40 runs) — see §4

### P5 — The SNR money plot (≈5 runs + instrumentation) — see §6. Nearly free, because it rides on inert probes inside runs you are doing anyway.

### P6 — Model-scale axis at fixed dataset (≈36 runs)

Width-multiplier ResNet-18 at {0.25×, 0.5×, 1×, 2×} × {1, 6, 62} × 3 seeds. This tests the proposal's actual claim — "large networks" — while holding dataset, horizon and block *count* fixed. It is the only clean way to attribute anything to n. Cheap, and it's the experiment the parent paper needed and never ran.

### P7 — Normalization / architecture (≈18 runs)

Same net with GroupNorm and with no-norm, at {1, 6, 62}. Tests H5 and buys architectural external validity for a few GPU-days.

### P8 — Method: hierarchical variants (≈80 runs) — see §5

### P9 — Scale confirmation — see §7.

**Zero-GPU, do today:** ask Saber and Arsalan (a) for the ICML ImageNet per-block logs and β trajectories, (b) to confirm the ImageNet runs used the same 6-block partition, (c) whether the layerwise/nodewise/weightwise branches ever executed. Item (c) is delicate — frame it as "we found these paths don't run in the public repo and we've implemented them; did you have a working internal version?" not as an accusation. The answer determines whether your contribution is "first working implementation" or "reimplementation", and it changes the related-work paragraph.

---

## 3. Q2 — Separating granularity from the tuning confound

The confound is real and currently fatal: α₀=1e-6 and η=1e-3 were the authors' values, tuned for m∈{1,6}. Any comparison at fixed (η, α₀) measures "granularity, given hyperparameters chosen for coarse granularity." Fix it with a pre-registered, equal-budget protocol.

**Arm definition.** An arm = (base optimizer, granularity). Tunable per arm: **η** and **α₀** only. Everything else (ρ, λ, c, κ, γ, meta-optimizer, batch size, epochs, augmentation, architecture) is frozen at the parent paper's values and identical across arms. Two tunables is the right scope: it covers the mechanism-relevant knobs and keeps the campaign to ~160 runs.

**Search.** Fully-crossed identical grid for every arm — η ∈ {1e-4, 3e-4, 1e-3, 3e-3, 1e-2}, α₀ ∈ {1e-6, 1e-4, 1e-2} = 15 configs × 1 seed. Equal budget holds *by construction*, which is more defensible than matched random-search budgets and lets you do paired analysis. Widen η downward for m=n only if the boundary is hit — and if you do, **widen it for every arm** and report the enlarged grid.

**Selection.** Carve a fixed 5,000-image validation split out of train, identical across all runs. Select the config on mean validation accuracy over the last 5 epochs (more stable than the argmax). **Report test accuracy for the selected config on 5 fresh seeds** that were not used for selection. Never select on test; never report best-over-epochs test as the headline number. Report final-epoch test as primary and val-early-stopped test as secondary.

**The primitive that actually settles the question: tuning curves.** From the 15-point grid, plot *expected best validation accuracy as a function of trial budget k* (Dodge et al.'s expected-max-performance) for each arm, with bootstrap CIs. This is what lets you say "layerwise beats scalar at every tuning budget" or "layerwise only wins if you can afford 10 trials." It costs nothing extra and it is exactly the analysis that pre-empts the reviewer question "did you just tune one arm harder?"

**Second axis nobody reports: robustness volume.** For each arm, the fraction of the grid within 1pp of that arm's best. If finer granularity has a higher peak but a much smaller feasible region, the honest finding is *granularity trades peak performance for tuning fragility* — and that becomes a target the hierarchical method can fix even where mean accuracy ties. Report it as a headline number, not an appendix.

**Variance control.** **[AMENDED, CORRECTIONS 115 — THIS PARAGRAPH STATED THE NEGATION OF STANDING RULE 14 AND WAS THE REGISTERED VARIANCE-CONTROL DESIGN FOR AN UNRUN EXPERIMENT.]** Common random numbers: seed index k fixes init and data order identically across arms; per-seed differences (paired Wilcoxon / paired bootstrap) are then legitimate *within one submission batch*. They do **not** "cut the CI substantially at 5 seeds" on this cluster: the measured variance components are sd_seed ≈ 0.044 against sd_resid ≈ 0.152, so pairing on seed removes roughly **8%** of variance, and a two-way batch × seed ANOVA on 42 complete cells finds SEED statistically null (F(60,85)=1.21, p=0.213) while BATCH is overwhelming (F(62,85)=5.47, p=6.9e-13, sd_batch ≈ 0.21 pp). Across batches, common random numbers buy nothing at all. Pre-register the effect size that counts (suggest: Δ ≥ 0.5pp) with a 95% *paired* CI only for within-batch contrasts and a Welch CI plus the sqrt(2/k_eff)·sd_batch floor otherwise, and the number of seeds, before looking.

**Compute matching.** Primary comparison at equal epochs. Report a secondary table at equal wall-clock (MetaOptimize costs +44% time / +33% memory; weightwise costs more). A method that wins per-epoch and loses per-second should be described as such.

**Pre-register.** Write the analysis plan — arms, grid, metric, selection rule, statistics, decision rules — commit it with a hash *before* launching P1. Given that the project's premise already changed once under the data, this is cheap credibility and it protects the student from HARKing accusations at review time.

---

## 4. Q3 — Is the weightwise collapse real?

**Split it into two events; they have different answers.**

- **Event A — the descent.** β driven to −23.8 (α ≈ 5e-11) across whole tensors, uniformly, over tens of thousands of steps.
- **Event B — the freeze.** β bit-identical between step 37,500 and 49,900 because Lion's `sign(0) = 0`.

**Event B is almost certainly a numerical artifact.** `z_i = H_i · g_i` for a *single* coordinate is a product of two tiny numbers; at α ≈ 5e-11 it will underflow to exact zero (or the meta-momentum m̄ will), and `sign(0)=0` then freezes β forever. That is an implementation pathology, not a phenomenon. Prove it in one run: store H, z, m̄ in float64 (or rescale z by a fixed constant) and check whether the freeze disappears while the descent remains. Also add an explicit "z underflowed to exactly 0" counter to the probe — it costs one line and it is diagnostic.

**Event A is probably real, and it is the interesting part.** Note what the numbers already rule out: a pure unbiased random walk in β with η=1e-3 and Lion meta-momentum gives a spread of order 0.3–1.0 over 50k steps. Reaching −23.8 requires ~24,000 net downward steps out of ~50,000 — i.e. `E[sign(z_i)] ≈ +0.48`. That is a **systematic bias**, not noise. Naive H1 (SNR→0 ⇒ random walk) does not explain it.

**H7 — the sign/median hypothesis (new, and I think this is the mechanism).** Sign-based meta-optimizers descend on the **median** of the meta-gradient, not the mean. `z_b = Σ_{i∈b} H_i g_i` is a sum of products of correlated near-zero-mean variables: strongly **skewed** for small n_b, Gaussianized by the CLT for large n_b. For a skewed distribution the median and the mean can have **opposite signs**. So per-coordinate, Lion can be systematically descending in the wrong direction, while at n_b=10⁵ the CLT restores median≈mean and the same code behaves correctly. This predicts:

- The collapse is **specific to sign-based meta-optimizers**. Re-run weightwise with meta=Adam and meta=SGD. If the collapse vanishes or reverses direction, H7 is confirmed and you have a mechanism the parent paper does not have.
- `E[sign(z_b)]` vs `sign(E[z_b])` should disagree only at small n_b. **Measurable from the probe you already have**, plus two new logged fields: the median of z_b and the fraction of positive signs per window.
- The magnitude of β drift per block should be predictable from `E[sign(z_b)]` × η × steps. Closing that loop turns a statistic into an explanation.

**Then rule out the two boring explanations.**
- *Tuning.* η=1e-3 with sign updates means β moves by exactly ±1e-3 per step regardless of n_b — so the natural per-granularity rescale is **η**, not z. Sweep η down to 1e-5 for m=n in P1's grid (and for every arm, symmetric). If weightwise at η=1e-5 is fine, the collapse is a tuning artifact and should be reported as such.
- *Implementation.* The P0 tests, especially tied-β and η=0.

**Treat collapse as a Bernoulli outcome, not a mean.** With 1/3 seeds collapsed, you have essentially no information. Run ≥8 seeds and report the **collapse rate with a Clopper–Pearson CI** plus the distribution of collapse epoch (a survival curve). Averaging a collapsed run with two healthy ones produces a number that describes nothing.

**Design: 8 seeds × {fp32, fp64} × {Lion, Adam meta} × {η default, η tuned} — trim to the 2×2 that matters after the fp64 probe (~40 runs).**

---

## 5. Q4 — Is the hierarchical fix still worth testing, and against what?

**Yes, but re-aimed.** Four candidate failures exist in the data; rank them by whether pooling is plausibly the right medicine:

| Failure | Exists? | Is shrinkage the right fix? |
|---|---|---|
| **F1: m=n collapse / degradation** | Yes, large (10% and 86% vs 91.9%) | **Yes — directly.** If the mechanism is per-coordinate noise/skew, pooling toward a shared β is precisely the estimator-theoretic remedy |
| **F2: tuning fragility at fine m** | To be measured in P1 | Yes — pooling should widen the feasible (η, α₀) region |
| **F3: no marginal gain 6→62** | Yes | Maybe — pooling lets informative blocks deviate while noisy ones shrink |
| **F4: blockwise doesn't help AdamW** | Probably (pending scalar re-run) | **No** — that's redundancy (H4), a different paper section |
| F5: layerwise < scalar (the proposal's premise) | **No, not at this scale** | n/a |

**Reformulated research questions:**

- **RQ1 (descriptive).** How does the benefit of step-size granularity vary with block count/size, and what sets the optimum? *Claim: non-monotone with an interior optimum m\*, and m\* shifts toward coarser as the base optimizer's own per-coordinate adaptivity increases.*
- **RQ2 (mechanistic).** Why does the fine end fail? Candidates: meta-gradient SNR ~ √(n_b/(1+(n_b−1)ρ_b)) (H1, corrected); sign/median bias (H7); redundancy with base adaptivity (H4); numerics.
- **RQ3 (methodological) — the thesis.** **Can hierarchical partial pooling remove granularity as a hyperparameter?** Success criterion: for all m, `hierarchical(m) ≥ max_m' plain(m')`, and in particular `hierarchical(n)` matches or beats the best hand-chosen partition — while inheriting the robustness volume of the scalar arm. *"You should never have to choose a partition; set m=n and let the method pool"* is a clean, checkable, quotable thesis, and it is strictly stronger than the original proposal.
- **RQ4 (scope).** Does the mechanism and the fix survive changes of base optimizer, normalization, horizon, model width and dataset?

**Method ladder** (from NOTES §5, re-prioritized against F1): M1 (additive reparam β_b = β₀ + δ_b with η₀ ≫ η_δ) as the workhorse — it gives β₀ the full-n SNR *by construction*, which is exactly the H1/H7 remedy, and M0 is a special case of it. Then M3 (empirical-Bayes λ_b from the meta-optimizer's own running variance v̄_b — free, and it makes the shrinkage *derived* rather than tuned) as the principled contribution. M5 (trust region on δ) as the blunt baseline that shrinkage must beat. M4 (z_b/n_b) belongs in the ablation as the obvious alternative — and note it is **a no-op for sign-based meta**, which is itself a sharp prediction that validates the mechanism. M2 (multi-level tree) is the version that earns the title, but only attempt it after M1+M3 works.

**Honest assessment of the ceiling.** If hierarchical(n) merely recovers 91.9 — i.e. ties the best hand-picked partition — the contribution is "removes a hyperparameter, plus a mechanism." That is a solid TMLR paper and a good MSc thesis; it is not an ICML headline. It becomes an ICML-grade result only if (a) hierarchical(n) *exceeds* the best plain arm by a real margin, or (b) the mechanism (H7 / the SNR law) is validated tightly enough to be a contribution on its own, or (c) it transfers to a setting where nobody knows the right partition (a transformer). Plan for (b) as the reliable deliverable and treat (a) as upside.

---

## 6. Q5 — Making H1 testable (the money plot, done properly)

The current regression (slope +0.114 vs predicted +0.50, r=0.40, 1,400 steps, one run) has four defects. Fix all four.

**Defect 1 — the theory is under-specified.** H1's √n_b assumes weakly-correlated summands. If within-block terms have mean correlation ρ_b, then `SNR_b ∝ √(n_b / (1 + (n_b−1)ρ_b))`, which **saturates** at `1/√ρ_b`. A slope of 0.11 instead of 0.50 is exactly what that predicts. So don't test slope=0.5 — **measure ρ_b directly** and test the two-parameter curve. A plot of measured SNR against the correlation-corrected prediction, with no free parameters, is a far stronger figure than a log-log regression with r=0.40.

**Defect 2 — the estimator confounds non-stationarity with noise.** `|running mean| / running std` over a window inflates the denominator with genuine drift. Replace it with a **frozen-point variance decomposition**: at K≈10 checkpoints spread across training, freeze (w, H) and evaluate z_b on M=64 independent minibatches. Signal = mean over the M (an unbiased estimate of the full-batch z_b); noise = std over the M. At 2–3 checkpoints also compute the exact full-batch z_b over all 50k images as ground truth. No windows, no detrending, no non-stationarity, and it costs ~M forward/backward passes per checkpoint.

**Defect 3 — n_b is confounded with block identity.** Across 62 tensors, log n_b is collinear with layer type (BN params and biases are small *and* statistically different) and with depth. That regression cannot attribute anything to size. **Use random partitions in the inert probe**: partition all coordinates uniformly at random into blocks of prescribed sizes s ∈ {1, 10, 10², 10³, 10⁴, 10⁵, 10⁶, n}, with many blocks per size. Now n_b is randomized with respect to layer identity — a genuine controlled design. Crucially, the probe is measurement-only, so **one training run yields the entire curve**, with as many nested partitions as you like. Then overlay the structured partitions: their vertical residual from the random-partition curve at matched n_b *is* the "structure premium," which is a second figure and an independent answer to P2.

**Defect 4 — horizon and replication.** 1,400 steps is 3% of training and SNR is strongly non-stationary. Measure across the full 50k steps, 5 seeds. Analyze with a mixed-effects model (random intercepts per run and per checkpoint) or cluster-robust SEs — blocks within a run are not independent observations and naive OLS CIs will be far too narrow.

**And the figure that actually closes the loop.** SNR is an intermediate quantity; what determines behavior under a sign-based meta-optimizer is `E[sign(z_b)]` (≈ `2Φ(SNR) − 1` under Gaussianity — and the deviation from that formula *is* the skew, i.e. the H7 signal). Plot: (i) SNR vs n_b with the correlation-corrected theory curve; (ii) E[sign z_b] vs n_b, with the Gaussian prediction, and the gap labeled as skew; (iii) **predicted β drift rate (η × E[sign z_b] × steps) vs. measured β drift**, per block. Panel (iii) is the money plot — it goes from a statistic to the observed step-size dynamics with no free parameters. If it lands, the mechanism section is done.

---

## 7. Q6 — Does ImageNet still need running?

**Not now, and not as premise-reproduction.** The parent paper's ImageNet run held granularity fixed at 6 blocks, so it never tested the axis you now study; going CIFAR→ImageNet changed dataset, model scale and horizon simultaneously. Reproducing it would confirm someone else's null on a different axis at a cost (~500–900 A100-h for a multi-seed multi-granularity arm) that would consume the entire budget and preclude P1–P5.

**What it would add, in order of value:** (i) horizon — 450k steps vs 50k, an order of magnitude, which is the one dimension H1 predicts is decisive; (ii) external validity for the granularity curve; (iii) the direct link to the parent paper's reported null, which reviewers will look for; (iv) the credibility of one non-toy result, which ICML/NeurIPS effectively require.

**Buy (i) cheaply first.** P3 (CIFAR at 300/600 epochs) tests the horizon prediction for ~24 runs. If layerwise/weightwise degrade with horizon on CIFAR, you have explained ImageNet without running it — and that is a much better paper anyway, because it's a controlled attribution rather than a scale anecdote.

**Then, mid-scale before full-scale.** ImageNet-64×64 (full 1.28M images, full class count, full step count, ~10× cheaper) or ImageNet-100. ImageNet-64 is the better choice: it preserves dataset scale and horizon, which are the variables that matter, and sacrifices only resolution.

**Reserve full ImageNet for one final confirmation table** — {scalar, 6-block, layerwise, weightwise, best-hierarchical} × 2 seeds, ~300–400 A100-h — run only after the mechanism is established and only if the following blockers are cleared.

**Blocking infrastructure items (these can silently destroy the campaign):**
- The ImageNet train directory shows **489 of 1000 class dirs**. Verify completeness and per-class counts against the official manifest *before* any ImageNet planning. A partial ImageNet trains a different task and produces plausible, wrong numbers.
- **No backup anywhere on ALICE, ~1 month scratch retention.** A 200-run campaign whose logs live only on scratch is one retention sweep away from being unreproducible. Set up the LIACS GitLab mirror + Leiden Data Store collection now — it is required by the filed DMP anyway, and the DMP is still unsigned by the PI.
- Write all results to the student's own 2TB home (s5014158), not the shared legacy account, with per-run config hashes and an append-only results index.

**On PaperFactory:** use it for the front half only — literature scan, related-work drafting, red-team/hard-questions passes on the manuscript. Do **not** route experiments through its RTX-2060 backend for this project: the compute is on ALICE, and results that will appear in a thesis and a submission need one provenance chain, not two. Its `novelty_gate` and `hard_questions` stages are genuinely useful against the reframed RQs — run them on §5's RQ1–RQ4 before committing.

---

## 8. Uncertainty register — what I could be wrong about

1. **The AdamW-scalar number.** The entire "adaptivity substitutes for granularity" spine rests on 92.13 from n=2 in a different campaign. Re-run it before believing §0. *(High impact, cheap to resolve, do first.)*
2. **H7 (sign/median) is my inference from the arithmetic of the β descent, not a measurement.** The −23.8 endpoint requires a systematic bias, which rules out naive random-walk-H1; skew under `sign()` is the most parsimonious explanation I see, but "the per-coordinate meta-gradient genuinely has a negative mean" is an alternative that the frozen-point full-batch z_b measurement distinguishes immediately. *(High impact, cheap.)*
3. **The 3pp gap to a tuned baseline** might be inherent to the parent framework's CIFAR-10 setup rather than something wrong in your setup. If it's inherent, the paper's framing must change (schedule-free/online), not its experiments. *(High impact on framing, one run to check.)*
4. **The hierarchical fix might only recover parity**, not gain. Plan the paper so the mechanism section stands alone if so.
5. **Random-partition controls could show the effect is entirely structural**, which would demote H1/H7 and promote a completely different (curvature / H2) story. I think this is unlikely given the block-size dependence already visible, but P2 is designed to find out rather than assume.
6. **Weightwise may simply be an artifact of η** — sign-based meta means β moves ±η per step irrespective of n_b, so a granularity-independent η is arguably the *wrong* default and the collapse may be uninteresting. P1's shared η grid settles this. If it does turn out to be pure tuning, say so plainly; "the anomaly was a hyperparameter" is a legitimate, publishable negative result in this literature and is far better than defending it.