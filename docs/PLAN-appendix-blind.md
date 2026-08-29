# Adversarial review — Hierarchical MetaOptimize

*Prepared as a hostile reviewer. Everything below assumes the plan is "fix the code, sweep granularity on CIFAR, test the hierarchical fix, write a paper." Confidence flags: **[HIGH]** = I'd bet on it, **[MED]** = plausible and cheap to check, **[SPEC]** = speculative but consequential if true.*

---

## 0. The four things that should change what you do tomorrow

1. **There is no standard baseline in the table.** ResNet-18 + CIFAR-10 + augmentation + 100 epochs with tuned SGDm/cosine is a well-known **94.5–95.5%**. Every number you have (88–92) is 3–6pp below that. If MetaOptimize's *best* granularity is 3pp below a first-year-PhD baseline, no reviewer will care which granularity won. Until a tuned fixed-LR and tuned-cosine baseline sits in that table, you do not know whether you are studying a method or studying a misconfiguration. **[HIGH]**
2. **The scalar run may be broken, not the layerwise run good.** 88.09 for scalar is anomalously low relative to both the 6-block runs and to Gate 0's AdamW scalar (92.13). "Layerwise beats scalar by +3.3pp" and "scalar is pathological under SGDm+Lion-meta from α₀=1e-6" are observationally identical from accuracy alone. You already have the logs to distinguish them: plot scalar's α(t) against the *geometric mean* of the layerwise α(t). If they differ by an order of magnitude, Gate 1's headline conclusion inverts. **[MED, and this is the cheapest high-stakes check you have.]**
3. **You have discarded your only external validation anchor.** The parent paper's published numbers exist only for the *unaugmented* setup. You correctly ruled unaugmented runs scientifically void — but they are the only thing on earth that can tell you whether your reimplementation of the *scalar and 6-block* paths still matches the authors'. "Void for science" ≠ "void for verification." Run the unaugmented config once, per granularity, and compare to the paper's table.
4. **You are still planning against a 2060.** NOTES §8 and PILOT are built around ~700 free GPU-h/month and "we almost certainly cannot afford ImageNet-90-epoch." You have 2×A100 + 8×L4 + 12×2080ti, uncapped, free. The binding constraint is now your attention and analysis throughput, not GPU-hours — and that should change the design: per-granularity meta-LR tuning at matched search budget, 5 seeds not 3, horizon sweeps, and yes, ImageNet is affordable (~30–40 A100-h/run with a fast input pipeline). Re-derive the plan under the real budget before running anything else.

---

## 1. What could make every result so far wrong

Ordered by (probability × damage).

### 1.1 The new granularity code paths are unvalidated against anything
"Byte-identical inertness on the untouched scalar/blockwise paths" proves the *old* paths are unharmed. It says nothing about whether the *new* paths compute the right thing. A subtly wrong `z_b` would produce exactly the results you see: coarse granularity fine, fine granularity degrading, weightwise collapsing.

**Validation protocol nobody has scheduled (all cheap, all decisive):**

| Test | What it catches |
|---|---|
| **Tie-all-blocks equivalence.** Run the *generic* layerwise path with all 62 blocks forced to share one β. Must match the scalar path to float tolerance, step for step. | Reduction/broadcast bugs, block-index misalignment |
| **Partition-equivalence.** Express the authors' 6-block partition through the new generic code. Must match the legacy 6-block path step for step. | The single strongest test available; if it passes, the generic machinery is sound |
| **Finite-difference meta-gradient.** On a ~200-parameter MLP with γ small and a 10-step horizon, compare implemented `z_b` against numerically differentiated ∂F/∂β_b, and against a brute-force forward-mode `H` (full n×m). | Sign errors, off-by-one in trace timing, wrong Jacobian term |
| **Permutation invariance.** Relabel blocks; results must be identical under a fixed seed. | Indexing/ordering bugs |
| **Off-by-one audit.** Does the meta-update consume `H_t` (pre-base-update) or `H_{t+1}`? Does the trace decay use `α_t` or `α_{t+1}`? | A one-step-stale `H` penalizes fine granularity far more than coarse — it would *manufacture* your headline finding |
| **κ·α broadcast at weightwise.** `H_{t+1} = γ(1−κα_t)H_t + Δw` with α a length-n vector. | Silent shape-broadcast errors |

None of these need a GPU-hour. Do them before another sweep.

### 1.2 The weightwise "collapse" is very likely a numerical absorbing state, not a granularity phenomenon **[MED→HIGH]**
Your own diagnostics describe the mechanism precisely: α → ~5e-11 → Δw underflows → `H` stops accumulating → `z` → 0 → `sign(0)=0` → β frozen forever. That is an **absorbing state created by the interaction of exp-parameterization, sign-based meta-updates, and finite precision** — not evidence about the statistics of per-coordinate step sizes.

Three specific things to check before this becomes a claim in a paper:
- **Dtype / AMP.** A per-coordinate `H_i·g_i` is a product of two very small numbers. If any part of the trace or the `z` accumulation touches fp16/bf16, it flushes to zero and the collapse is a rounding artifact, full stop.
- **`sign(0)` convention.** PyTorch returns 0. That is what freezes β. Try `sign(0) → +1`, or a floor `β ≥ β_min`, or an α clamp. If the collapse disappears, the "weightwise fails" result evaporates.
- **The trace time constant is α-dependent** — see §3.3 below. This is the deeper version of the same problem.

If weightwise-SGDm is your only surviving instance of "finer is worse," and it turns out to be `sign(0)`, the project has no failure case at all.

### 1.3 α₀ = 1e-6 is not the same initialization across granularities **[HIGH]**
At m=1, one α bootstraps from a `z` pooled over 11.17M coordinates. At m=11.17M, each α must bootstrap from a single coordinate's signal — and at α≈0, `Δw≈0`, so `H≈0`, so `z≈0`. Fine granularity is being asked to escape a near-flat region with ~1/√n_b of the signal. **The comparison at fixed (α₀, η) is structurally unfair to fine granularity**, independent of any statistical argument. You already flagged the meta-LR confound; α₀ is the larger half of it. Minimum fix: per-granularity (α₀, η) tuning at *equal search budget*, or warm-start every granularity from a converged scalar α.

### 1.4 "Best test accuracy" is doing three illegitimate jobs at once **[HIGH]**
- It is a **max over ~100 noisy draws** — upward biased, and biased *more* for high-variance runs. Weightwise-SGDm "peaked 70.09 then collapsed to chance" is reported as 70.09. That is not a summary statistic, it's a bug in the metric.
- It is **test-set model selection**. There is no val split. Any reviewer will flag this; carve 45k/5k from train.
- It launders instability into a respectable number, which is precisely the failure mode you are trying to study.

### 1.5 Seed plumbing and effect sizes **[MED]**
`91.56 ± 0.03` over 3 seeds on CIFAR-10 is tighter than typical seed spread (±0.1–0.3pp). Verify the seed actually varies *init + data order + augmentation RNG*, not just `torch.manual_seed` while the dataloader worker seeds are fixed. If it doesn't, your error bars are fictional and the 91.56-vs-91.34 comparison is noise. Also: you are accumulating a many-cell table with no multiple-comparison discipline.

### 1.6 Gate 0 and Gate 1 disagree and nobody has reconciled them **[HIGH]**
Gate 0: AdamW scalar 92.13 vs 6-block 91.76 — **scalar wins**. Gate 1: 6-block AdamW 91.86, scalar still running. Gate 0's scalar (92.13) beats *every* Gate 1 number. Either the configs are not nested ("matched η" in Gate 0 vs. authors' η in Gate 1?) or something changed between the two. **The missing AdamW-scalar cell is the single most important number in the project** — if it lands near 92, then under AdamW the ordering is scalar > 6-block > layerwise, the anomaly *does* reproduce at CIFAR scale, and it is a **base-optimizer** story (H4), not a scale story. That reframes the entire paper. Finish that run before anything else.

---

## 2. Metric and objective mismatch

You are evaluating an **online, γ-discounted future-loss** method with a **stationary, i.i.d., 100-epoch, best-test-accuracy** protocol. This is close to the worst available testbed for the method's stated selling point.

**Not measured, should be primary:**
- **Cumulative online training loss** (area under the loss curve) — the closest observable proxy to Fᵗᵞ, and the thing the meta-gradient actually descends.
- **Final** (and mean-of-last-5-epochs) test accuracy, with bootstrap CIs over paired seeds. **[AMENDED, CORRECTIONS 115.]** "Paired seeds" is valid only WITHIN a submission batch. Across batches the seed label carries nothing (sd_seed ≈ 0.044 vs sd_resid ≈ 0.152; seed F(60,85)=1.21, p=0.213) and the bootstrap must be over independent arms with the sqrt(2/k_eff)·sd_batch floor added.
- **Train loss separately from test accuracy.** Right now you cannot tell whether granularity is an *optimization* effect or an *implicit-regularization* effect. If layerwise reaches the same train loss but different test accuracy, the entire H1/SNR framing is the wrong lens and the paper is about generalization. This is a fork in the road and it is free — the numbers are already in your logs.
- **Wall-clock-matched comparison.** MetaOptimize costs +44% time. Give the fixed-LR baseline 1.44× the epochs. Under an equal-wall-clock budget several of your wins may not survive.
- **Actual memory/time per granularity.** The "no additional computational overhead" claim is inherited, not verified. At m = n the trace/state vectors are a different story; measure it.

**Being measured, doesn't matter:**
- 0.2pp orderings between 6-block and layerwise at n=3.
- Best-test-accuracy anywhere.
- The 1400-step H1 regression (see §3.1 — it's confounded, not just underpowered).

---

## 3. Scientific confounds and mechanisms being ignored

### 3.1 The H1 regression is confounded by layer identity, and the fix is nearly free **[HIGH]**
`log SNR ~ 0.114·log n_b` across 62 parameter tensors conflates **block size** with **what kind of parameter it is**. BN scales are small *and* scale-invariant; the classifier is small *and* has different gradient statistics; conv weights are large *and* deep. You cannot read a size effect off this.

**The control nobody has proposed: random partitions.** Partition the *same* network into m blocks of randomly assigned coordinates, with the *same size distribution* as the layerwise partition. Then:
- **SNR vs n_b** is measured with layer identity destroyed → a clean test of H1.
- **random-62 vs layerwise-62** answers a question that could end the project: *does layer structure carry any information at all?* If random-62 performs as well as layerwise-62, there is no layerwise structure being learned, "early layers want bigger steps" is fiction, and shrinking toward a flat scalar is the wrong prior.

This is the single cleanest experiment available and costs a handful of L4-hours.

### 3.2 SNR ∝ √n_eff, not √n_b — the refinement that explains your data **[MED, and potentially your best theoretical contribution]**
H1 assumes the terms `H_i·g_i` within a block are weakly correlated. They are not — coordinates in a layer share activations. With average within-block correlation ρ̄, the effective sample size is `n_eff = n_b / (1 + (n_b−1)ρ̄)`, which **saturates near 1/ρ̄**. At ρ̄ = 0.01, n_eff caps around 100 regardless of whether n_b is 10³ or 10⁶ — which would explain a measured slope of **0.114 instead of 0.50**. Measure ρ̄ directly; it converts a failed prediction into a quantitative one, and it hands M3 a *computable* shrinkage coefficient rather than a tuned λ.

### 3.3 H7 — the eligibility trace's time constant is α-dependent, creating positive feedback **[SPEC, but mechanistically tight and nobody has written it down]**
`H_{t+1} = γ(1 − κα_t)H_t + Δw` with γ = 1. The **only** decay is `(1 − κα_t)`. So:
- α = 1e-2, κ = 0.1 → trace horizon ~1000 steps.
- α = 5e-11 → decay factor ≈ 1 → **the trace never forgets**, and since Δw ≈ 0, it freezes at a stale value.

A block with a small α therefore accumulates an increasingly stale sensitivity estimate, whose inner product with fresh gradients is noise with a fixed direction. Under a sign-based meta-update, that drives β monotonically. **Small α → long/stale trace → wrong-sign z → smaller α.** That is a self-reinforcing collapse, it is granularity-dependent only because fine blocks are more likely to reach small α first, and it is *fixable*: decouple the trace decay from α (explicit γ_H < 1). If this is the mechanism, the "right" hierarchical fix is not shrinkage at all — it's a trace-horizon fix, and you'd be publishing something more interesting than Eq. (1).

### 3.4 The β random walk is super-diffusive, and that makes horizon the prime suspect **[MED]**
Under Lion-meta a pure-noise block moves β by exactly ±η every step, with momentum ρ̄ = 0.99 autocorrelating the sign — so β spread across blocks grows faster than √T. Back of envelope: CIFAR is 50k steps, ImageNet-90ep at bs256 is **450k steps — 9×**. Diffusive drift alone gives ~3× more spread; super-diffusion gives more. Across 62 independent blocks the max/min α ratio goes from ~e² on CIFAR to ~e⁶ on ImageNet.

**This is testable on CIFAR for ~40 L4-hours: run 100 / 300 / 900 epochs at every granularity.** If the layerwise-vs-scalar gap shrinks and inverts with horizon, you have explained ImageNet without running ImageNet, and "scale" in the paper's title becomes "horizon." PILOT gates this experiment behind "only if Gate 1 shows no failure" — Gate 1 *did* show no failure, so this is now your top experiment, not a contingency. It is also directly measurable from existing logs: fit the growth exponent of β-spread vs t.

### 3.5 "Scale" is four confounded variables, and the parent paper varied all of them at once
CIFAR-10 → ImageNet changed: dataset size, task difficulty, input resolution, **batch size (100 → 256)**, **step count (9×)**, and — crucially — the **parameter-to-task-difficulty ratio**. CIFAR-10/ResNet-18 is grossly overparameterized (your own defect #1: it memorizes in epoch 1 without augmentation). ImageNet/ResNet-18 is *under*parameterized. That capacity regime, not "size," may be the whole effect — and it is testable on CIFAR in hours: use a much smaller ResNet, or CIFAR-100, or add label noise, to enter the capacity-limited regime while holding everything else fixed. Nobody has proposed the capacity-ratio axis.

### 3.6 "Layerwise" here means "per parameter tensor" (62), not "per module" (~20)
The pilot specified ~20. You ran 62, which gives BN scales and biases their own step sizes — exactly the parameters with scale-invariance pathologies (H5). Add a **module-grouped m≈20** point, and a **"62 tensors but BN/bias pinned to the scalar"** variant. If pinning BN fixes things, H5 is your story and the hierarchical prior should be structured by *parameter role*, not by depth.

### 3.7 LARS, LAMB, Adam-mini, and μP are the elephant in the related-work section **[HIGH]**
LARS and LAMB are **per-layer step-size adaptation that demonstrably works at ImageNet and BERT scale**. μP prescribes per-layer scalings that work at LLM scale. Adam-mini shows blockwise (coarse) second-moment sharing matching or beating per-coordinate. None appear in your reading list.

This is fatal to the current framing and generative for a better one: if per-layer step sizes provably work at scale *when set by a rule*, then the failure is not in the **parameterization** but in the **online estimation** of it. The paper then becomes: *"learning per-layer step sizes online is statistically unidentifiable at fine granularity; the fix is a prior — and the right prior may be μP/LARS scaling rather than a flat scalar."* That is a stronger, more defensible, and more current paper than "shrink toward scalar," and it makes M2 the headline instead of an afterthought. A reviewer will ask "why does LARS work?" with certainty.

---

## 4. The premise itself

**The proposal's central claim is not supported by the parent paper.** The paper reports 6-block-on-ImageNet not helping. The proposal says *"layerwise often underperforms scalar in large networks."* Those are different claims, and you have evidence the layerwise code path never executed. So the sentence the whole project rests on is based on runs that either (a) are unpublished internal experiments, (b) come from a different codebase, or (c) don't exist.

**This must be resolved before further compute is spent, and it is a one-email question.** Frame it neutrally and technically — you are asking a co-author of an ICML paper about his own code, and your supervisor is the other co-author:

> "We implemented the layerwise/weightwise paths since the public `cifar10_HF.py` recognizes the names but has no branch, and the MetaStep branches raise on `.cuda()` over a list and `torch.log(float)`. Before we build on it: which runs is the 'layerwise underperforms in large networks' observation based on — is there a separate codebase or a set of logs we can look at? And was the ImageNet blockwise run the same 6-block partition as CIFAR-10?"

Attach the minimal repro script. Do not editorialize. Send it this week.

**If the answer is "it's intuition / unpublished":** the framing must change from *"we explain a known anomaly"* to *"we characterize when granularity helps."* Which brings me to the strategic point —

**Your contribution should be restructured so it survives the anomaly not existing.** Right now: no failure case → M0/M1 have nothing to fix → "our method doesn't hurt" → not a paper. Instead, pose it as: **"granularity in MetaOptimize is a bias–variance tradeoff; here is the estimator that makes m a non-decision."** M3 (empirical-Bayes λ from the meta-optimizer's own second-moment trace, free) delivers that whether or not layerwise ever loses. Then the anomaly, if you find it, is a *bonus* section rather than a load-bearing wall.

---

## 5. Project-level risks nobody has addressed

| Risk | Severity | Fix |
|---|---|---|
| **No backup anywhere. ~1 month scratch retention. DMP filed but unsigned. Off-cluster master copy required and nonexistent.** | **Highest expected loss in the project**, and a one-hour fix | Today: GitLab repo, `rsync` all logs to the 2TB home on s5014158, nightly cron. Get the PI to sign the DMP. |
| Work living on the **shared legacy account** (salehkaleybars) | Access can vanish; not yours | Migrate everything to s5014158 now |
| **ImageNet shows 489/1000 class dirs** | E5 silently impossible, discovered late | Verify completeness + file counts *before* any planning that depends on it. Consider ImageNet-100 / ImageNet-64 / Tiny-ImageNet as better science per GPU-hour anyway |
| **Bus factor 1**, single student, unfunded | Thesis and paper both single-threaded | Written weekly state file in the repo; supervisor gets read access to logs, not just summaries |
| **Scooping — from the proposer, not from strangers** | The proposal is 9 months old; Arsalan's group is the most likely party to run it | Ask directly: is anyone else working on this? Is there a draft? Settle authorship and submission authority in writing *before* results exist, not after |
| **No deadline, only a venue list** | ICML ~Jan 2027 needs science done by Dec — 4 months. NeurIPS ~May 2027 is the realistic target. TMLR is the correct default for a diagnosis-heavy paper | Pick one. Plan backwards. Write the abstract and the figure list now |
| **Thesis vs. paper objectives conflict** | Thesis tolerates a null result; the paper doesn't. Unmanaged, this creates pressure to keep chasing an effect | Declare the thesis primary and the paper optional, in writing, now |
| **PaperFactory on the front half** | (a) its experiment backend targets a 2060, not ALICE — so `experiment_run` designs against the wrong substrate; (b) using autonomous idea-generation on a project whose premise is already contested amplifies the wrong thing; (c) ICML/NeurIPS **require** LLM-use disclosure, and Leiden has its own thesis rules | Use it for `review_loop`, `hard_questions`, `red_team`, `novelty_gate` — adversarial and literature stages. Not `idea_generation` or `experiment_design` here. Check the university's rules before it touches thesis prose |
| **Compute plan is an order of magnitude stale** | Experiment design still shaped by "we can't afford it" | Rewrite NOTES §8 against ALICE. L4s carry CIFAR (~50 runs/day); A100s carry ImageNet/LM. 1400 A100-h at a 2-A100 cap = 29 days at 100% duty — feasible but schedule it |
| **No pre-registration of metric/analysis** | Table is growing; garden of forking paths | Freeze the primary metric, the seed count, and the comparison set in the repo, dated, before the next sweep |

---

## 6. The five questions nobody has asked

**Q1. Is the scalar baseline broken rather than layerwise being good?**
Compare scalar's α(t) to the geometric mean of layerwise α(t) in the logs you already have. If scalar is stuck near α₀ or oscillating, "+3.3pp for granularity" is an artifact of an unfair scalar run and Gate 1's conclusion inverts. *Cost: an afternoon with existing data. Highest information-per-hour in the project.*

**Q2. Does the effect track number of steps rather than model or data size?**
100 / 300 / 900 epochs × all granularities on CIFAR. If the gap shrinks and inverts with horizon, "scale" is "horizon," ImageNet is explained without ImageNet, and the paper's central variable changes. *~40 L4-hours.*

**Q3. Is layer *identity* doing any work, or only block *count*?**
Random partitions with matched size distributions, as both an H1 control and a structure test. If random-62 ≈ layerwise-62, there is no layerwise structure to learn and shrinkage-toward-scalar is the wrong prior — you'd want μP-centered or role-centered instead. *A few L4-hours; could redirect the entire method design.*

**Q4. What is the effective sample size inside a block?**
Measure within-block correlation of `H_i·g_i`. If n_eff saturates, SNR ∝ √n_eff quantitatively explains your 0.114 slope, replaces a failed prediction with a working one, and yields a computable shrinkage coefficient for M3 instead of a tuned λ. *Instrumentation only.*

**Q5. Why do LARS, LAMB, Adam-mini, and μP succeed with per-layer scaling at exactly the scale where MetaOptimize-layerwise allegedly fails?**
If per-layer step sizes work at scale when *prescribed*, the failure is in online *estimation*, not in the parameterization — and the paper's thesis becomes "meta-learned granularity needs a prior, and the right prior is a known scaling law." Stronger, more current, and it pre-empts a guaranteed reviewer question.

*Runners-up, both cheap and both forks in the road:* **(Q6)** Is this an optimization effect or a generalization effect — decompose every result into train loss and generalization gap. **(Q7)** Does the collapse survive a `sign(0)→+1` change and an fp32-everywhere audit? If not, you have no failure case at all.

---

## 7. Suggested next ten days (no new science until these land)

1. Backups + GitLab + Data Store; migrate to s5014158; get the DMP signed. *(hours)*
2. Finish the **AdamW-scalar** Gate 1 cell. Reconcile it with Gate 0's 92.13. *(GPU-hours)*
3. Run the **implementation-equivalence suite** in §1.1 — tie-all-blocks, partition-equivalence, finite-difference `z_b`, off-by-one audit, dtype/AMP audit. *(CPU only)*
4. Add **tuned fixed-LR and tuned-cosine SGDm baselines**. Confirm you can hit ~94.5–95% in this harness at all.
5. From existing logs: **scalar α(t) vs layerwise mean α(t)** (Q1); **β-spread growth exponent** (Q2 preview); **within-block correlation ρ̄** (Q4); **train loss vs test acc split** (Q6).
6. Send the one email to Saber/Arsalan (§4) — premise provenance, ImageNet partition, existing layerwise logs, and whether anyone else is working on this.
7. Rewrite NOTES §8 and PILOT against ALICE, and pick **one** venue with a date.

If (2) shows AdamW scalar ≈ 92 and (5) shows scalar's α is healthy, you have the anomaly at CIFAR scale under AdamW and the project accelerates. If (5) shows scalar's α is pathological, you have been measuring a different phenomenon than you think — and finding that out in week one is worth more than three months of sweeps.