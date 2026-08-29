# Paper Strategy — Hierarchical MetaOptimize

> **⚠ SUPERSEDED IN PART BY FINDINGS CYCLE 7 (19 Aug 2026). Read `docs/FINDINGS.md` §6 of cycle 7
> before drafting from this file.** Three changes, none of which this document reflects yet:
> 1. The **granularity** claim is now budget-controlled and survives intact (+3.43pp at E=100 →
>    +3.47pp at E=205, `ext300`). It is the paper's spine and it is stronger than when this file
>    was written.
> 2. The **pooling-beats-plain** claim (~+1.5pp) does **not** survive the budget control — +0.29pp
>    at E=205, inside seed noise. Do not build a section on it.
> 3. Cycle 6's proposed replacement framing ("finer partitioning improves the *estimator*",
>    drift ∝ 1/√N) is **refuted by measurement** — exponent −0.113, and the weightwise collapse is
>    a spread effect, not a drift effect. The surviving mechanism fact is that per-coordinate
>    meta-gradient signs are strongly positively correlated (53.1% agree across 11.17M coordinates).


## 0. Executive summary

**The proposal's premise is dead at the tested scale, but a better paper is sitting inside the wreckage.** The interesting phenomenon is not "layerwise hurts" — it's that **step-size granularity has a hard failure boundary, not a gentle degradation curve**, and that the failure has a specific, diagnosable mechanism (collapse → freeze → absorbing state, made permanent by a sign-based meta-optimizer). That is a more novel and more defensible claim than the one you set out to make.

**Recommended primary narrative:** a granularity study whose backbone is the *mechanism of the weightwise failure*, with hierarchical pooling as the final "and here is the fix" section — contingent, not load-bearing.

**Recommended primary venue: TMLR**, with a NeurIPS **OPT workshop** paper as the 4–6-month milestone, and a NeurIPS/ICML main-conference attempt only if the method section lands *and* you get one scale point outside CIFAR-10 vision.

**Before any narrative is choosable, one confound must be closed:** per-granularity meta-hyperparameter tuning at equal search budget. Every current result — including the headline weightwise collapse — is currently attributable to "you used the authors' scalar-tuned `meta-stepsize=1e-3, alpha0=1e-6` at m = 11.17M." A competent reviewer kills the paper on this in two sentences. It is not a robustness check; it is the load-bearing experiment.

---

## 1. What the evidence actually supports right now

| Claim | Status |
|---|---|
| Blockwise (m=6) > scalar under SGDm on augmented CIFAR-10/ResNet-18 | **Supported** (+3.5pp, 3 seeds, tight variance) |
| Layerwise (m=62) ≈ blockwise, ≫ scalar under SGDm | **Supported at this setting** |
| Granularity is roughly irrelevant under AdamW between m=6 and m=62 | **Supported** (91.86 vs 91.83) — consistent with H4 |
| Weightwise degrades (AdamW) / collapses (SGDm) | **Observed, confounded** — untuned meta-LR not ruled out |
| Collapse mechanism is α→0 freeze, not β runaway | **Well-supported by the probe**; kills H3 |
| SNR ∝ √n_b (H1) | **Not supported.** Slope +0.114 vs predicted +0.50, r=0.40, 1400 steps, and n_b is confounded with layer type and depth. Currently this is *evidence against the stated magnitude* |
| "Layerwise hurts at scale" (the proposal's premise) | **Untested.** You tested CIFAR-10. The parent claim was ImageNet. Not reproducing it at CIFAR-10 is not refuting it |
| Granularity survives per-arm α₀ tuning under SGDm; it does not under AdamW | **Supported, n=1 per cell** (FINDINGS cycle 5 §1). SGDm scalar never reaches 90% at any α₀ in three decades and its plateau moves 0.16pp. Seed 1 in flight on all 12 cells |
| Pooling (m=62) raises the accuracy plateau by 1.4–1.5pp | **Supported at n=3–4, budget-bounded.** Reproduces under both meta-optimizers. Whether it is asymptotic is what `ext300` decides |
| Pooling accelerates training | **REFUTED** (cycle 4 second pass, confirmed n=4 in cycle 5). It is 24% *slower* to 85% under Lion. The ep→90 speed-up was an artifact of the unpooled arm's plateau sitting on the 90% line |
| Hierarchy rescues per-weight granularity — the project's founding proposal | **CLOSED, negative** (cycle 4 §1). Monotone in pooling strength across six decades of λ, two independent operators, no interior optimum, no beneficial regime |
| The released code can execute the granularities it advertises | **Refuted, and systematically** — the dead-granularity defect is present independently in *both* task copies (cifar10 and tinystories). See §6 for how to say this |

That last row is the single most important honesty constraint in this document. You have not contradicted the parent paper. You have shown its *proposed extrapolation* does not appear one scale down. Those are different statements and reviewers will punish the conflation.

---

## 2. Candidate narratives, ranked

### **A — "Granularity has an optimum and a cliff, and here is the mechanism"** ★ recommended
*Framing:* Online meta-gradient step-size adaptation faces a bias–variance tradeoff along the **partition** axis. Coarse partitions average meta-gradient noise but cannot express heterogeneity; fine partitions can, but past a boundary the system enters a self-reinforcing collapse. The boundary is not a smooth accuracy decline — it is a phase transition, it is predictable from gradient noise, and sign-based meta-optimizers make it **absorbing** (`sign(0)=0` ⇒ β freezes forever).

*Why it's strongest:* it is true given what you've measured, it absorbs the negative result honestly rather than hiding it, it has a falsifiable prediction (below), and the "cliff not slope" observation is genuinely new. It does not depend on the hierarchical method working.

*Honesty grade:* A. *Ceiling:* TMLR comfortably; main conference if a scale point lands.

### **B — "The weightwise failure mode"** (narrative (d) standalone)
*Framing:* A tight instability paper. Per-parameter meta-learned step sizes die in a specific way; here is the causal chain, the phase diagram in (α₀, meta-LR, m), and a minimal fix (β floor / trust region / normalized meta-gradient).

*Why it ranks second:* smallest evidence bill, highest probability of *some* venue, and it's the intellectual core of A anyway. Its weakness is scope — it's a note about a failure in one method, not a statement about optimizers.

*Honesty grade:* A. *Ceiling:* strong workshop, plausible TMLR. Weak main-conference case alone.

### **C — "Hierarchical MetaOptimize" (the method paper)**
*Framing must change.* The original pitch (pull layerwise toward scalar) targets a failure you did not observe. The surviving pitch is: **partial pooling is what makes per-parameter step-size learning viable at all**, and it removes granularity as a hyperparameter. β_b = β_global + δ_b with shrinkage λ; classic hierarchical-prior / James–Stein motivation; the shared level supplies the noise-averaged signal, the residual level supplies heterogeneity.

*Why it ranks third despite being the "real" thesis goal:* it is contingent on results you don't have, it needs everything A and B need **plus** wins, and the defensible claim is likely the modest one ("matches the best-tuned granularity without knowing it in advance; makes m=n usable") rather than "beats everything." Optimizer method papers face the most hostile reviewer pool in the field.

*Honesty grade:* A **if** the claim is scoped to robustness rather than superiority; C if it's oversold. *Ceiling:* highest of any option — and highest variance.

### **D — Negative result / replication** (narrative (a))
*Framing:* "We could not reproduce the granularity anomaly; here is why, including three defects in the released pipeline."

*Why it ranks last as a standalone:* it is honest and it is the guaranteed floor, but it undersells what you have. The mechanism work in A/B is worth more than the null. **Make this Section 2 of paper A, not a paper.** Keep it in reserve as the thesis-safe fallback if the mechanism work doesn't converge.

*Honesty grade:* A. *Ceiling:* TMLR / MLRC / ICLR Blogposts.

### **Recommended composite**
One paper: **A (spine) + B (mechanism core) + D (as the setup/reproduction section) + C (as a final, clearly-scoped method section that the paper survives without).** This is a TMLR-shaped object. Split B off early as the workshop paper to bank a result.

---

## 3. Minimum evidence per narrative

### Shared spine (required for *all* of them — do this first)
1. **Per-granularity meta-hyperparameter sweep at equal search budget.** α₀ × meta-stepsize grid (≥4×4), independently for m ∈ {1, 6, 62, n}, best-of-budget selection, then ≥3 seeds at the winner. Without this you have no result, only a confound.
2. **Competently tuned fixed-schedule baselines.** SGDm+cosine and AdamW+cosine, tuned at comparable budget. "MetaOptimize vs MetaOptimize" is not an experiment a reviewer accepts.
3. **≥3 seeds everywhere, 5 for headline numbers**, mean ± std, paired-seed comparisons **within a single submission batch only** — across batches use Welch and add the batch floor (**[AMENDED, CORRECTIONS 115]**; seed is statistically null on this cluster, batch is not) — and *report the full sweep*, not just the winner.
4. **Backups.** See §9 — this is a paper-strategy item, not an IT item.

### A additionally requires
- **Granularity curve**, ≥4 points on log m, × ≥2 architectures × ≥2 datasets. At minimum: ResNet-18 (BN) + a GroupNorm or ViT variant (tests H5 and shows the effect isn't BN-specific); CIFAR-10 + CIFAR-100 or TinyImageNet.
- **The mechanism intervention — highest-value experiment you can run.** Correlational SNR regressions will not convince anyone. Two cheap, decisive designs:
  - **Random-partition control.** Blocks of size k formed by *randomly* assigning parameters vs. structural layers of the same size. If the effect is pure meta-gradient noise ∝ block size, they behave identically. If structure matters, they don't. Cheap, and it cleanly deconfounds n_b from layer type/depth — which currently invalidates your H1 regression.
  - **Batch-size shift.** If the driver is meta-gradient noise, increasing batch size should move the failure boundary to *finer* m. Figure: failure boundary in the (m, batch size) plane. This is the falsifiable prediction that converts your paper from description to mechanism, and it is the figure an AC remembers.
- **A predictive test:** fit the boundary on setting 1, predict it on a held-out architecture/dataset, show the prediction holds.
- **Redone SNR analysis** over full training, per-architecture, with layer type and depth as covariates. Be prepared to report that H1's √n_b law is quantitatively wrong.

### B additionally requires
- Collapse reproduced across ≥3 seeds and ≥2 architectures.
- Causal chain established stepwise with logged evidence: α↓ → update magnitude → activation/gradient magnitude → z_b → `sign(0)=0` → β frozen.
- **Meta-optimizer ablation:** replace Lion with Adam/SGD as the meta-optimizer. Is the absorbing state specific to sign-based updates? This is the sharpest claim available to you and it's one cheap run-set away.
- Phase diagram over (α₀, meta-LR, m) showing collapse persists across a *range*, not a point.
- Minimal fix demonstrated (β floor, trust region, or normalized meta-gradient) restoring weightwise to at least parity with blockwise.

### C additionally requires
- Precise estimator + derivation of the meta-gradient under the two-level parameterization, including how the eligibility trace decomposes across levels.
- λ sensitivity curve; ideally λ learned, with a fallback default.
- **Wins:** matches or beats the best *tuned* single granularity on ≥2 datasets × ≥2 architectures at matched tuning budget — the honest framing being "removes granularity as a hyperparameter."
- **One scale point outside small-image vision.** Either ImageNet (verify the 489/1000 class dirs first) or a ~100M-parameter transformer LM on WikiText-103/OpenWebText. Without this, C is dismissed as CIFAR-only regardless of merit.

### D additionally requires
- Faithful reproduction under the authors' original config, then the corrected config, with each delta (augmentation, epoch truncation, per-granularity tuning) isolated and quantified.
- Correspondence with the original authors on record.

---

## 4. Venue fit and honest odds

Base rates to hold in mind: ICML/NeurIPS ≈ 25% overall, and **optimizer papers sit well below base rate** — the reviewer pool is trained to ask "did you tune the baseline" and "does it hold at scale," and an MSc compute envelope (~1400 A100-hours) cannot answer the second the way reviewers now expect.

| Narrative | Venue | Odds | Notes |
|---|---|---|---|
| A, full evidence + non-vision scale point + predictive test | NeurIPS/ICML main | **20–30%** | Needs the mechanism intervention to land cleanly |
| A, CIFAR/TinyImageNet only | NeurIPS/ICML main | **8–12%** | "Small-scale study" desk-level skepticism |
| A, full evidence | **TMLR** | **60–70%** | Best fit. No novelty bar, rewards thoroughness, rolling deadlines, and it's a real journal for the thesis |
| B standalone | NeurIPS OPT / "Has it Trained Yet?" / ICML workshop | **70–80%** | Bank this early |
| B standalone | TMLR | **45–60%** | Scope is thin but the mechanism is clean |
| C, wins at ImageNet or LM scale | NeurIPS/ICML main | **25–35%** | The only path to a top-tier main-conference accept |
| C, CIFAR-only wins | main conference | **<10%** | Will read as an incremental tweak |
| C, scoped as robustness | TMLR (inside A) | folds into A's odds | Recommended |
| D standalone | TMLR / MLRC / ICLR Blogposts | **45–60%** | Fallback only |
| D standalone | main conference | **~5%** | Don't |

**Calendar reality (06/08/2026 – 06/08/2027).** ICLR 2027 (~Sept 2026) is unreachable — you'd be submitting on confounded data. ICML 2027 (~Jan 2027) is reachable only if the shared spine finishes by November. NeurIPS 2027 (~May 2027) is the realistic main-conference shot and lines up with thesis submission. NeurIPS 2026 OPT workshop (~Sept/Oct 2026) is the right early milestone for B + the reproducibility note. TMLR is rolling — submit A when it's ready, which decouples you from deadline gambling. *Verify all dates; I'm reasoning from typical cycles.*

---

## 5. Gate structure (what result routes where)

**Gate A — close the confound.** Per-granularity meta-LR sweep.
- Weightwise recovers to ≈ blockwise with a tuned meta-LR → **the failure was a tuning artifact.** Narrative B collapses; A becomes "granularity is largely irrelevant once meta-hyperparameters are tuned per granularity, and here's why (H4 + noise averaging)" — still a real, publishable negative-plus-mechanism result, and it makes the *tuning-budget* point the contribution. C is dead; say so early and pivot.
- Weightwise still fails across the whole grid → **A and B are both live.** Proceed.

**Gate B — mechanism intervention.** Random-partition control + batch-size shift.
- Boundary moves with batch size as predicted → **mechanism confirmed.** This is your main-conference ticket. Push hard.
- No movement → the driver isn't meta-gradient noise. Report it as a refutation of H1 (which the current regression already hints at) and hunt for the real driver (conditioning? BN scale invariance? trace horizon γ?). Timeline slips ~2 months.

**Gate C — method.** Only start implementing hierarchical pooling after Gates A and B.
- Beats/matches best-tuned granularity on 2 datasets × 2 archs → write C as the final section, attempt NeurIPS.
- Doesn't → **cut it, keep the paper.** A survives without C. This is why C must not be the spine.

**Gate D — scale.** Verify ImageNet completeness *now* (489 vs 1000 class dirs) before planning any budget around it. If it's incomplete and can't be repaired, substitute a small transformer LM — which is arguably a *better* scale point in 2026 anyway, since it tests the granularity claim on an architecture where per-tensor heterogeneity is known to be large.

---

## 6. Handling the "never implemented / never executed" finding

This is simultaneously your most valuable finding and your most delicate one. Sequence matters.

**Step 1 — social, before a word is written.** Talk to Salehkaleybar and Sharifnassab. Ask, neutrally: *which* codebase produced the paper's granularity experiments, and does the released repo differ from it? You are not accusing anyone; you are asking a reproducibility question with an entirely plausible innocent answer (research code diverges from release code constantly). **Do not write this section before you have their account.** Getting this wrong damages a supervisory relationship and an MSc, and it is unrecoverable.

**Step 2 — separate three claims with three different evidence levels.**

| Claim | Evidence | Write it? |
|---|---|---|
| The public repo at commit `<hash>` has no branch for layerwise/nodewise/weightwise; passing those names raises `AttributeError` | Directly verifiable | **Yes, plainly**, with commit hash and file/line references |
| The MetaStep code contains granularity branches that cannot execute (`.cuda()` on a Python list; `torch.log(float)`) | Directly verifiable | **Yes, plainly**, as a factual observation |
| Therefore the parent paper held granularity at 6 blocks because the finer path never ran | **Inference about code you cannot see** | **No.** Maximum permissible: "the released code does not support granularities beyond the block partition, so we implemented them" |

The third row is where a paper gets retracted or a relationship gets destroyed. It is the most interesting sentence you could write and you must not write it.

**Step 3 — framing and placement.** Main text gets one neutral sentence in the experimental setup: *"The reference implementation supports scalar and block granularities; we extend it to layerwise, nodewise, and per-parameter partitions (App. X)."* Verb is **extend**, never *fix*, *fail*, or *broken*. The forensic detail goes in an appendix titled **"Reproducibility notes on the reference implementation"** — factual, itemized, no blame verbs, framed as a service to anyone building on the repo. Include the three defects together (missing branches, no augmentation, the `--max-time` truncation) with their measured effect on numbers, and state explicitly that your numbers are therefore **not directly comparable to the parent paper's table**. That statement protects you more than it costs you.

**Step 4 — the co-authorship judo.** If Salehkaleybar is a co-author (he will be), the appendix is **self-disclosure by the original team**, which is the strongest possible framing and neutralizes the criticism entirely. Push for exactly this. It converts "student critiques supervisor" into "the authors document and correct their own release" — which reviewers read as unusual integrity.

**Step 5 — if the supervisor asks you to omit it.** Take it seriously and don't escalate. But note the cost honestly: without it, your layerwise/weightwise experiments are unreproducible from the public artifact and the paper has an unexplained gap. Middle path: the one-line main-text sentence plus a patched public code release with a documented diff — the facts are then available to anyone who looks, without a forensic narrative. Include your **byte-identical-inertness test** for the untouched scalar/blockwise paths in the release; it's evidence of care and it preempts "did your changes perturb the baseline?"

---

## 7. Claims that must not be made

1. **"Layerwise step sizes do not hurt."** You have one dataset, one architecture, one base-optimizer pair, one meta-optimizer, one meta-LR. Scope every sentence.
2. **"The granularity anomaly does not exist" / "the parent paper's ImageNet result is wrong."** You have not run ImageNet, and the ImageNet directory is unverified. Not tested ≠ refuted.
3. **"Finer granularities were never run in the original work."** Inference about private code. See §6.
4. **"Weightwise fails."** Until Gate A closes: "weightwise fails *under the meta-hyperparameters tuned for coarser granularities*." That qualifier is the difference between a finding and an error.
5. **"SNR ∝ √n_b" / "H1 confirmed."** Slope 0.114 vs 0.50, r=0.40, 1400 steps, n_b confounded with layer type and depth. As it stands the data **argues against** the stated magnitude. Present it that way or not at all.
6. **"β runaway."** H3 is refuted by your own probe (collapse, frozen β at α≈5e-11). Retire it explicitly rather than quietly.
7. **Any superiority claim over hand-tuned schedules** without having run tuned SGDm+cosine / AdamW+cosine.
8. **Theory-flavored justification of hierarchical pooling.** James–Stein / empirical-Bayes shrinkage is a *motivation*. Unless you prove something about the online meta-gradient setting specifically, do not let analogy wear the costume of a guarantee. Reviewers of optimizer papers are unusually good at spotting this.
9. **"Adaptive optimizers make per-block α redundant" (H4)** as a general claim from one dead heat (91.86 vs 91.83). It's a hypothesis with one supporting data point.
10. **Compute or scale claims** contingent on ImageNet before the dataset is verified complete.
11. **Any word from the family "plateau", "asymptote", "ceiling", "converges to" — about the
    SGDm scalar arm or the unpooled layerwise arm.** Added 19 Aug 2026 (FINDINGS cycle 5 §2).
    Both are still climbing in **training** accuracy at epoch 100 (scalar 94%, +0.4pp/10ep, never
    reaching 97%; pooled layerwise 97.8%, never reaching 99%) while their *test* curves are flat.
    A converged test curve is not a converged run. Until `ext300` reports, the only defensible
    form is **"within a 100-epoch budget"** — and note that the campaign's entire explanation of
    the parent paper's §7.3 ImageNet null is that a longer budget dissolves this kind of gap, so
    a reviewer will apply the campaign's own argument to the campaign. Say it first.
12. **"Hierarchical pooling regularises the step-size field."** The trade is real and reproduces
    across two meta-optimizers (−1.9pp train for +1.4pp test, Lion and Adam within 0.15pp of each
    other), but "constrains the fit" and "fits more slowly and generalises better along the way"
    are not separable while the pooled arm's train curve is still rising. `ext300` decides it.
    Related: do **not** present m=6, m=62 and m=11.17M pooling as one curve. They are three
    phenomena — no trade at m=6 (train and test both rise ~0.3pp), a fit-for-generalisation trade
    at m=62, and outright optimisation failure at m=11.17M (train and test collapse *together*
    with the gap shrinking). The single-curve framing is the one the first sweep invited and it
    is wrong twice over.

---

## 8. Title and abstract sketch (Narrative A)

**Primary title:**
> **How Fine Is Too Fine? The Granularity–Noise Tradeoff in Online Meta-Learned Step Sizes**

**Alternates:**
- *Step-Size Granularity Has a Cliff, Not a Slope: Collapse Dynamics in Online Meta-Optimization*
- *From Scalar to Per-Parameter: Where Meta-Learned Step Sizes Stop Working, and Why*
- *Partition Matters: Noise, Collapse, and Partial Pooling in Meta-Gradient Step-Size Adaptation*

**Abstract sketch** (bracketed items are placeholders that must be filled by measurement, not by prose):

> Online meta-gradient methods learn optimizer step sizes during training by partitioning a network's parameters into blocks and adapting one step size per block. The partition granularity — from a single scalar to one step size per parameter — is a free design choice that prior work has largely left unexplored. We study it directly. Extending the reference MetaOptimize implementation to support layerwise, nodewise, and per-parameter partitions, we sweep granularity across [K] settings, [2] architectures, and [2] datasets, tuning meta-hyperparameters independently at each granularity under a matched search budget. We find that (i) intermediate granularities improve substantially over a scalar step size under SGD with momentum (+3.5 points on CIFAR-10/ResNet-18) while offering little benefit under AdamW, consistent with adaptive methods already normalizing per coordinate; and (ii) performance does not degrade smoothly as granularity increases — beyond a boundary, training enters a self-reinforcing collapse in which step sizes shrink toward zero, weights freeze, meta-gradients vanish, and sign-based meta-optimizers make the resulting state absorbing. We characterize this boundary as a function of meta-gradient noise: [it shifts to finer granularities as batch size grows / random partitions of matched size behave identically to structural layers], supporting a noise-averaging account over a structural one. Finally, we show that partially pooling fine-grained step sizes toward a shared global step size [restores per-parameter adaptation to parity with the best hand-selected granularity], removing partition granularity as a hyperparameter. We release corrected code and document three defects in the public reference implementation that affect reproducibility.

Note the abstract's last sentence: the reproducibility note is a **contribution line**, stated flatly, no drama. That is the correct register.

---

## 9. Risks and blockers (ordered by how badly they end the project)

1. **No backup. One-month scratch retention. No off-cluster master copy.** Every narrative in this document is built on run logs that currently exist in exactly one place, on a filesystem that deletes things. This is the single highest-severity item on the project and it outranks every experiment. Set up the GitLab repo + Leiden Data Store collection **this week**, and get the DMP signed. An unsigned DMP with an undeployed backup is also a compliance exposure for the PI, so this is an easy ask.
2. **Gate A goes the wrong way** (weightwise recovers under tuning). Survivable — it becomes a tuning-budget paper — but it kills C and shrinks B. Plan the pivot language now so you don't spend a month in denial.
3. **Compute estimate is soft.** 1400 A100-hours (range 700–3500) with a 2×A100 cap is roughly 30–70 wall-clock days of saturated usage before contention. The 8×L4 and 12×RTX2080ti pools should carry the sweep grid; reserve A100s for the scale point. Budget the sweep in L4-hours explicitly.
4. **ImageNet completeness unverified** (489/1000 class dirs). Verify before any planning depends on it. Have the LM substitute ready.
5. **Sole-author-plus-supervisor dynamics on §6.** Handle early, in person, not in a draft.

---

## 10. On using PaperFactory

Use it for the **back half only**: `figures`, `writing`, `review_loop`, `hard_questions`, `red_team`, `polish`. The red-team and hard-questions stages are genuinely valuable here — they will find the tuning confound and the H1 magnitude problem, and it is cheaper to hear it from a pipeline than from Reviewer 2.

**Do not use the front half.** `trend_scan`, `idea_generation`, and `novelty_gate` solve a problem you do not have — the idea is fixed and the binding constraint is measurement, not ideation. Running them invites narrative drift toward whatever sounds publishable, which is precisely the failure mode this project is one bad decision away from.

**Never use `experiment_run`.** It targets a local RTX 2060; results from it are not comparable to ALICE runs and cannot enter the paper. Every number in the manuscript must trace to an ALICE job ID and a logged config. Enforce that as a hard rule: an autonomous writing pipeline that can generate plausible numbers, attached to a project whose central finding is that other people's code silently didn't do what it claimed, is a research-integrity risk worth naming out loud in your own methods section.
---

# Cycle-8 reconciliation (19 Aug 2026) — what the evidence now licenses

Narrative A above is built on *"granularity has an optimum and a cliff"*. After cycle 8 the first
half of that is wrong and the second half is stronger than when it was written. §8 of FINDINGS
records the complete guarded ladder; this section records what it does to the paper.

## 1. The ladder is a PLATEAU with a cliff, not an optimum with a slope

| granularity | m | n | best test |
|---|---|---|---|
| scalar | 1 | 5 | 88.08 ± 0.22 |
| 6-block | 6 | 5 | 91.69 ± 0.13 |
| layerwise | 62 | 11 | 91.23 ± 0.22 |
| nodewise | ≈4,800 | **1** | **92.10** |
| weightwise | 11.17M | 3 | 79.38 ± 0.46 |

There is a **+3.6pp step from m=1 to m=6, a flat plateau of ±0.5pp from m=6 to m≈4,800, and a
−12.7pp cliff at m=n.** No interior maximum at m=62 exists to be explained, and the nodewise cell —
currently the *highest* point on the ladder — is n=1.

**Consequences for the paper:**
* **Retitle away from "how fine is too fine".** The question the data answers is *"why is there a
  step at m>1 and a cliff at m=n, and nothing in between"*, which is a two-boundary story, not a
  tradeoff curve.
* **The "granularity–noise tradeoff" framing is not supported.** A noise-averaging account predicts
  smooth degradation as blocks shrink. The measurement is flat across three orders of magnitude of
  m and then falls off a cliff. Cycle 7 already refuted the 1/√N estimator law directly; this is the
  same refutation arriving from the accuracy side.
* **`nd-*` (nodewise to n=5) gates this entire section.** Nothing in §1 may be written until it lands.

## 2. The method contribution is now M1 additive, not M0 shrink

Cycle 8 §1–2 changes which operator the method section is about.

| | M0 shrink | M1 additive |
|---|---|---|
| λ / r curve shape | **flat** over λ ∈ [0.001, 1.0] | **non-monotone, interior peak** at r ∈ [0.03, 0.1] |
| why | every λ ≥ 0.001 is full pooling (gotcha 9) | genuinely partial for the whole run |
| best cell vs plain layerwise | +1.67pp (λ=0.01) | **+2.18pp** (r=0.05, n=2) / +1.73pp (r=0.03, n=5) |
| effect on training fit | **worse** (97.8–98.1 vs 99.66) | **better** (99.88 vs 99.66) |
| mechanism | drift rate *and* spread | spread only |
| character | regulariser | finds a better solution, more slowly |

**Write both, as two methods with two mechanisms.** The temptation is to present one "hierarchical
MetaOptimize" with a pooling strength dial; §2 of FINDINGS shows that is factually wrong and gotcha
21 shows why on structural grounds. The honest framing is: *pooling the log step sizes toward a
shared value regularises; rescaling the per-group deviation of the update finds a better optimum.*

**The strongest single property to lead with is still shrink's flatness** — a method that nominally
adds a hyperparameter but whose outcome is insensitive to it over three orders of magnitude removes
a decision rather than adding one. Additive does *not* have that property (r=0.3 is already back
near plain), so additive's peak must be reported with its sensitivity, not without.

### ⚠ CORRECTED cycle 9 — M1's contribution is on ACCURACY, and it is NULL on the primary metric

Two things in the table above were written from n=2 cells and have since moved (FINDINGS cycle 9
§1–2). Both corrections tighten the paper rather than weaken it, but neither is optional:

1. **The "+1.90pp (r=0.1)" cell was optimistic.** At n=5, r=0.1 is 92.86 ± 0.19 (+1.63pp) and
   r=0.03 is 92.96 ± 0.15 (+1.73pp); the r=0.1 n=2 reading carried a 0.01pp sd that was ~20× too
   tight (gotcha 26). The leading cell is now r=0.05 at 93.41 ± 0.06 (+2.18pp) — **at n=2, i.e. the
   same evidence strength that just failed.** Report the ladder's *shape* until `ad-l-r005` s3–s4
   and `ad-l-r007` land; do not print an argmax.

2. **M1 must not be written into the "granularity buys speed" frame.** On epochs-to-target — the
   metric this paper declares primary — additive is **null at every r**: at ep→88 the accuracy-optimal
   cell is the *slowest* pooled arm (39.5 vs plain's 36.2 ± 1.6) and the fastest cells (r=0.2/0.3,
   35–36) are indistinguishable from plain; at ep→85 every additive cell is strictly slower than
   plain. This replicates independently under the Adam meta-optimizer. The row "character | finds a
   better solution, more slowly" was right, and it is the whole story: **the granularity axis buys
   speed, the pooling axis buys accuracy, and they are separate claims that must not share a
   sentence.** Every M1 table needs both columns, with the speed column shown and null.

One objection is now answered rather than open: the additive gain **survives the Adam
meta-optimizer** (+0.82 / +0.65pp over a 9-seed plain baseline, n=1 per cell), so it is not an
artefact of Lion's sign nonlinearity — the cheapest refutation a reviewer had. It arrives at roughly
half the Lion-meta size, so the sign nonlinearity doubles the effect without creating it.

Still open before this section can be drafted: `e3a-*` (the 300-epoch budget control, 10 cells) must
confirm the peak does not migrate toward r=0, and its matched `e3a-lsh01` cells must confirm that
shrink's apparent inferiority to additive is not simply shrink being budget-starved (its 97.78 train
accuracy at epoch 100 is still climbing — gotcha 19).

**The cross-operator agreement at full pooling** (shrink λ=1.0 → 92.53 ± 0.17; additive r=0 →
92.52 ± 0.11, two separately-written code paths 0.01pp apart) belongs in the paper as an
implementation-validation result, in the same section as the V1–V5 suite. It is the only place the
campaign has two independent implementations of one physical configuration.

## 3. Two claims are now BUDGET-CONTROLLED, and one of them got weaker

At matched α₀=1e-3, 100 vs 300 epochs (FINDINGS §6):

| effect | 100 ep | 300 ep | verdict |
|---|---|---|---|
| granularity (scalar → layerwise) | +3.44pp | +3.42pp | **invariant** — safe to claim |
| pooling (shrink λ=0.1 − plain) | +0.86pp | +0.60pp | **decays** — must be stated with its budget |

* **Table 1's headline is now budget-controlled at 3×.** State it that way; it is a materially
  stronger claim than an uncontrolled 100-epoch number and it pre-empts the obvious review attack.
* **⚠ Our own ImageNet explanation gets weaker and the paper must say so.** Cycles 6–7 read the
  parent paper's §7.3 ImageNet null as a budget artefact — a long budget lets the coarse arm catch
  up. At 3× budget on CIFAR-10 the granularity gap does not narrow *at all*. That reading now
  applies to **pooling**, which does decay, and not to **granularity**. Do **not** carry
  "granularity buys speed that a long budget erases, which explains §7.3" into the draft. The
  supportable sentence is: *at 3× budget on CIFAR-10 the granularity gap is invariant, so a pure
  budget account of the ImageNet null is not supported at this scale; whether it holds at ImageNet's
  budget ratio is untested and we do not test it.*
* **The scalar arm still has not converged at 300 epochs** (train 95.4%, rising +0.6pp/100ep). Per
  gotcha 19 the claim is bounded: *converges to a worse solution* is supported at 3×; *never
  converges* is not.

## 4. One reviewer attack is now closed, and it should be closed IN the paper

The α₀ confound (every hierarchical result living at α₀=1e-6, where fine partitions have more
parallel signal with which to grow the step size) is **dead at 100 epochs**: all four arms are flat
to ≤0.38pp across α₀ ∈ {1e-3, 1e-4, 1e-6}, and the granularity gap is +3.3 to +3.4pp at every α₀
(FINDINGS §3). Put the ladder in an appendix table rather than waiting to be asked for it.

The mirror finding is a **methods-section rule, not a result**: at 20 epochs α₀ dominates
everything, and the fine-granularity catastrophe is mostly a startup transient (weightwise
14.8 → 77.5 purely from α₀). Any short-horizon granularity comparison in the paper must be labelled
a mechanism probe, never a performance number (OPERATIONS gotcha 24).

## 5. §7's "claims that must not be made" — three additions

Appending to the existing list:

* **No m=n pooling claim of any kind** until the `zv-*` identity block passes. The shipped M0
  operator pools β toward a *mean* while the scalar arm aggregates the meta-gradient as a *sum*, a
  factor-of-11.17M mismatch; full pooling at m=n lands at 34.56 where it must reduce to the scalar
  arm's 88.08. `HIER=zpool` fixes this in meta-gradient space with both endpoints as exact
  identities. Until it is verified numerically, the m=n pooling column measures our own bug.
* **No claim that partial pooling "removes partition granularity as a hyperparameter"** — the
  abstract in §8 asserts it as a placeholder. It requires per-weight parity with the best plain
  granularity, which is exactly what the confound above currently prevents measuring.
* **No "granularity–noise tradeoff"** and no smooth-degradation language (§1 above).

## 6. Revised abstract sketch

Replacing §8's, with every unmeasured placeholder removed rather than bracketed:

> Online meta-gradient methods learn optimizer step sizes during training by partitioning a
> network's parameters into blocks and adapting one step size per block. The partition granularity —
> from a single scalar to one step size per parameter — is a free design choice that prior work has
> left largely unexplored, and which the reference implementation advertises but cannot execute. We
> implement it and measure it. On CIFAR-10/ResNet-18 under SGD with momentum, moving from one step
> size to six is worth +3.6 points; from six to roughly five thousand is worth nothing; and moving
> to one step size per parameter costs 12.7 points. The gain is invariant to a 3× training budget,
> and the coarse arm's training accuracy shows it converges to a worse solution rather than more
> slowly to the same one. The per-parameter collapse is a rediscovery of a failure documented in the
> IDBD/Autostep lineage and is largely repaired by a published guard, after which a granularity
> deficit survives. We then show that the two natural ways to pool step sizes hierarchically are
> different methods, not two settings of one dial: shrinking the log step sizes toward their mean
> acts as a regulariser, improving test accuracy by up to 1.7 points while *reducing* training fit,
> and is insensitive to its own strength over three orders of magnitude — removing a decision rather
> than adding one; whereas rescaling the per-group deviation of each realised update has an interior
> optimum, is worth 1.9 points, and improves training fit as well. We release corrected code and
> document three defects in the public reference implementation that affect reproducibility.

Gated on: `nd-*` (the m≈4,800 rung, currently n=1), `ad-l-*` at n=5 (the interior optimum, currently
n=2), and `zv-*` (the identity gate, before any per-weight pooling sentence).
