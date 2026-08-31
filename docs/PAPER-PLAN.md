# PAPER-PLAN — the chosen framing, the abstract, and the claim ledger

**Written cycle 88. Every number below was RE-DERIVED from `results/all_runs.csv` in this pass
under the gate `window_ok==1 AND complete==1` (CORRECTIONS 119.3), not copied from FINDINGS or
MASTER-TABLE.** Where a number is quoted from another document without re-derivation it is
marked **[NOT RE-DERIVED]** and may not enter a draft in that state.

Supersession: **CORRECTIONS > FINDINGS > everything else.** This file is a plan, not a result;
where it disagrees with CORRECTIONS, CORRECTIONS wins.

---

## 0. THE HEADLINE DECISION, AND WHAT WAS KILLED TO REACH IT

### KILLED: "degenerate groups explain the parent paper's granularity anomaly"

This was the proposed reframe. It is **dead on four independent counts**, each verifiable from
files on disk in under a minute, and it must not appear in any draft in any form.

| # | the kill | verified how |
|---|---|---|
| K1 | **The parent never makes the claim we proposed to explain.** §7.1's only stated CIFAR-10 finding (line 4645) is *"In every tested combination, MetaOptimize outperforms its corresponding fixed-step-size baseline"* — MetaOptimize vs a tuned fixed LR, **not** blockwise vs scalar. The positive half exists only as an inference from the §7.3 aside and one appendix figure covering two (base, meta) pairs. No table, **no error bars** (`grep -icE "error bar\|shaded\|standard deviation\|confidence interval"` = **0**), and **no seed count for §7.1**. | direct grep of `~/.arxiv-mcp-server/papers/2402.02342.md` |
| K2 | **The §9 sentence is indexed by APPROXIMATION, and every prior internal quotation elided the clause.** Verbatim (lines 5308-5311): *"…this improvement is not consistent **across the MetaOptimize approximations evaluated**."* It is not a statement about an accuracy-vs-*m* curve. And **all 112** `chunk*`/`nodewise1d` rows in the corpus are `base=SGDm, meta=Lion` — we have never varied the axis the sentence names. | grep; CSV census |
| K3 | **At the parent's own η=1e-3 the mechanism points the wrong way, in 5 batches of 5.** `br6` 89.612→**90.865**, `bl5` 89.645→**90.910**, `bf8` 91.015→**92.099**, `bf9` 90.995→**91.983**, `sp8` 89.903→**90.660** (layerwise → nodewise). The 66.6%-singleton partition **wins** by +0.76 to +1.25 pp across three boxes and two horizons. The direction reverses only at η=1e-4. The parent fixes η=1e-3 everywhere and says it needs no tuning. | re-derived, this pass |
| K4 | **Removing 100% of the singletons buys nothing.** Inside one batch (`ck1`): chunk1 (m=11,173,962, 100% singletons) 90.979 → chunk2 (m=5,586,981, **0%** singletons) 91.095. Step **+0.115, se 0.133, t +0.87 — not resolved**, against a count-only prediction of +0.131 to +0.161, i.e. an excess of **−0.046 to −0.016**. The ladder is smooth in log *m* with no kink at the one step where singleton fraction collapses from 100% to 0%. | re-derived, this pass |

**Also struck: the word "variance" as our mechanism.** The corpus's drift-vs-group-size
slopes are **positive in 6 of 6 fits** where a 1/√N model requires −0.500 — and, worse,
*drift* is the per-step magnitude `|Δβ̄|`, a **net systematic movement**, not an estimator
variance, and it is **censored at the meta-stepsize** by Lion's sign update. It cannot refute
a variance claim and must not be presented as doing so. (See §6.)

### CHOSEN: **"A granularity gain is a tuning gain."**

> **A granularity gain is a tuning gain: ranking what actually moves accuracy in meta-learned
> step sizes.**

The thesis: *"the number of step sizes"* is not one experimental variable. It is at least four
— the shared meta-stepsize, the initial step size, the group **count**, and the group-**size
distribution** — and each moves the measured granularity effect by **more than the effect
itself**. Once all four are controlled, the partition is a **second-order knob**, and the
parent's own §9 sentence has a direct answer: *at a shared meta-stepsize, a granularity
comparison measures distance-from-optimum, not the partition, so of course it is not consistent
across instantiations.*

### Why this beats the runner-up (framing C, the methods / reproducibility paper)

Three tests, applied in order, and the same paper wins all three.

1. **The external-instance test** — *name one instance of this claim outside our own repo.*
   C passes on exactly one item (the parent fixes η=1e-3 for every experiment and states no
   tuning is needed) and fails on the rest; its catalogue is our code, our CSV, our prose.
   The chosen paper passes on that same item — which is also its *target* — and its
   prescription passes on five more (Adam-mini, Adalayer, Muon, LARS/LAMB, bitsandbytes all
   ship a tensor-level rule none of them justifies).
2. **The afternoon test** — *what can a reader falsify on their own hardware today?*
   Chosen paper: "re-tune both arms and most of your granularity gain disappears"; "merge your
   1-D tensors, +0.43 to +0.82 pp". C's headline needs our CSV to check.
3. **The parent-paper test** — *which answers §9 as written?* §9 is indexed by approximation.
   A tuning/configuration answer addresses the sentence they wrote. A degenerate-group answer
   does not, since the parent's only granularities are m=1 and m=6, and six blocks on a
   ResNet-18 **cannot contain a size-1 group** (min block size = **1,856**, re-derived).

C also fails on its own headline. It was to be sold on *"23.2% of 56 published contrasts were
contaminated, 62% flipped"*. **The registered rate is 6/56 = 10.7%** against a pre-registered
<10% bar — FINDINGS 70.2 says in its own words that it *"clears its bar by one cell"* — and the
56 are **not** published contrasts but mechanically enumerated scorable cells. 23.2% is the
post-hoc any-pair supplement which FINDINGS 70.5 itself says *"may not overturn a registered
gate … it bounds that gate's coverage."* A reproducibility paper whose headline inflates its own
one-cell-fragile registered rate is self-refuting on page one. (Logged as CORRECTIONS 119.6.)

**C is not discarded — it becomes §7 of the chosen paper**, where it is load-bearing machinery
rather than a confession.

---

## 1. THE ABSTRACT, AS IT WOULD APPEAR

> **A granularity gain is a tuning gain: ranking what actually moves accuracy in meta-learned
> step sizes**
>
> MetaOptimize (Sharifnassab, Salehkaleybar & Sutton, ICML 2025) meta-learns a step size per
> parameter group, and closes by noting that finer partitions help inconsistently: *"while
> increasing the number of step sizes is anticipated to enhance performance, our experimental
> findings reveal that this improvement is not consistent across the MetaOptimize approximations
> evaluated."* We take that question up with 1,960 runs (~1,200 GPU-hours) on ResNet-10/18/34/50
> and CIFAR-10/100, and report that **"the number of step sizes" is not one experimental
> variable but at least four**, each of which moves the measured granularity effect by more than
> the effect itself.
>
> **(1) The shared meta-stepsize dominates.** In a single batch at fixed seeds, layerwise minus
> scalar is **+3.291 pp (se 0.108, t 22.6)** at the paper's own default η = 1e-3, and **+0.655 pp
> (se 0.176, t 3.72)** with both arms at their own bracketed optimum η = 1e-4. Four fifths of the
> reported granularity benefit is tolerance to an over-large meta-step, not accuracy. Across the
> full surface the gap runs −0.135 / +0.219 / +0.198 / +0.624 / +3.182 / +4.066 pp as η rises
> over six rungs. The parent fixes η = 1e-3 for every experiment and states that no tuning is
> needed.
>
> **(2) The initial step size sets the sign.** At the parent's exact (AdamW, Adam, η = 1e-3)
> configuration the ordering is monotone increasing at α₀ = 1e-6 and monotone decreasing at
> α₀ = 1e-3, a reversal that survives per-arm α₀ tuning.
>
> **(3) The group count is a smooth convex function of log m, not a slope.** Holding the
> partition *family* fixed — uniform chunks of K weights — accuracy runs 92.887 (m = 62) /
> 92.858 / 92.763 / 92.812 / 92.526 / 92.582 / 92.159 / 91.411 / 91.095 / 90.979 (m = 11.2M)
> across ten rungs and 5.25 decades, with the five-rung ascent K = 1 → 1024 inside **one batch**
> (+1.547 pp, se 0.152, t 10.2). Local secants of that one curve run from **−0.09 to +0.83
> pp/decade**, which is why four mutually incompatible "count slopes" can be fitted to one
> corpus.
>
> **(4) The group-size distribution at fixed count — the variable no method controls.** Replacing
> the architecture-aligned partition by a uniform one **at matched group count** (m = 14,420 vs
> 14,421, one group apart) is worth **+0.727 / +0.485 / +0.581 / +0.587 pp** in four independent
> within-batch ResNet-18 batches (mean **+0.595, se 0.050**), **+0.666 (se 0.094, t 7.08, 9 v 9
> seeds)** on ResNet-34, and **+1.640 (t 6.71)** on CIFAR-100. Architecture *alignment* is refuted
> as the carrier: permuting which weights share a group while holding the count **and the exact
> per-tensor size multiset** is worth **−0.009 pp (t −0.06)** against a pre-registered symmetric
> null band. The effect is localised to the shattering of **41 one-dimensional tensors** — every
> BatchNorm scale and shift plus the classifier bias, 9,610 of nodewise's 14,420 groups (66.6%)
> over **0.086% of the weights**. Merging them is worth **+0.427 / +0.649 / +0.758 / +0.816 pp**
> in four in-batch paired cells, for free.
>
> **We also report the mechanism we could not find, because it is the obvious one.** Size-1
> groups are *not* the carrier: inside one batch, removing **100%** of the network's singletons
> (per-weight → pairs) is worth +0.115 pp (t 0.87) against a count-only prediction of +0.13 to
> +0.16. The unit is the **tensor**, not the group size. The natural estimator-variance
> explanation fails on our own instrument in three ways, and we report all three.
>
> **Scope, stated plainly rather than confessed.** All partition contrasts use an SGDm base with
> a Lion meta-optimizer at meta-stepsizes ≤ 3e-4 and a 100-epoch budget. The best MetaOptimize
> cell in 1,960 runs reaches **93.317** against a tuned SGD-with-cosine baseline at **95.124** —
> a **1.807 pp deficit** — and we make no competitiveness claim. Every primary is a within-batch
> contrast, because a batch × seed ANOVA over 42 configurations gives batch **F(62,85) = 5.47,
> p = 6.9e-13, sd ≈ 0.21 pp** against a statistically null seed effect (F = 1.21, p = 0.213) with
> GPU class excluded by direct measurement across three classes and 23 nodes.
> **[ANOVA and baseline-vs-frozen figures: NOT RE-DERIVED this pass — see the ledger.]**

---

## 2. THE CLAIM LEDGER

Every sentence that would appear in the paper, the runs behind it, and its resolution.
`W` = within-batch. Batch floor for cross-batch contrasts: **√(2/k)·0.21 pp**.

### §3 — THE RANKING (the headline)

| # | claim | runs | n | estimate | se / t | W? | status |
|---|---|---|---|---|---|---|---|
| 3.1 | At a shared η the granularity gain is ~5× its tuned value | batch `ms`, jobs 4687145-79 | 3 v 3 | +3.291 (η=1e-3) vs **+0.655** (η=1e-4) | se 0.146 / t 22.6; se 0.176 / t 3.72 | **YES** | **RESOLVED** |
| 3.2 | The gain rises monotonically with η across six rungs | all families, primary cell | 3-101 v 3-14 | −0.135 / +0.219 / +0.198 / +0.624 / +3.182 / +4.066 | t −0.79 … +52.9 | no | **RESOLVED as a trend**; the 1e-3 rung pools 101 runs of mixed composition — quote the `ms` in-batch pair as primary |
| 3.3 | Mistuning η by one decade costs more than the whole ladder spans | primary cell | 5 v 3 | scalar **−4.424**; layerwise −0.981 | — | no | **RESOLVED for scalar.** Layerwise reads −0.981 here vs MASTER-TABLE's −1.670 on a stricter key — **filter-sensitive, quote with its filter** |
| 3.4 | The method is 1.807 pp behind a tuned schedule | best MO cell `i3b` 93.317 (n=3) vs `bl-sgd-01` 95.124 (n=5, sem 0.047) | — | **−1.807** | — | no | **RESOLVED. Belongs in the abstract, not the limitations.** |
| 3.5 | Adaptation is worth +2.551 over frozen β and +1.551 over fixed-step | MASTER-TABLE | — | — | — | — | **[NOT RE-DERIVED]** — must be re-derived before it enters a draft |

### §4 — WHAT "MORE STEP SIZES" VARIES

| # | claim | runs | n | estimate | se / t | W? | status |
|---|---|---|---|---|---|---|---|
| 4.1 | Count, family fixed: convex in log m over 5.25 decades | 10 rungs, primary cell | 3-13 | 92.887 → 90.979 | — | no | **shape RESOLVED**, assembled cross-batch — descriptive only |
| 4.2 | The five-rung ascent K=1→1024 is inside one batch | `ck1`, jobs 4708251-65 | 3/rung | **+1.547** | se 0.152 / t 10.21 | **YES** | **RESOLVED** |
| 4.3 | The "count slope" is a secant, not a constant | same | — | local secants **−0.090 … +0.828** pp/dec | — | — | **RESOLVED — never import a count slope across cells** |
| 4.4 | **D** = uniform − aligned at matched count, R18 | `cc1`,`mm1`,`pp1`,`gn1` | 3-4 v 3-4 each | **+0.727 / +0.485 / +0.581 / +0.587**, mean **+0.595** | t 3.63 / 3.01 / 4.11 / 3.83; se(mean) 0.050 | **YES ×4** | **RESOLVED — the strongest partition result in the corpus** |
| 4.5 | D on ResNet-34 | `g3m` | 9 v 9 | **+0.666** | se 0.094 / t 7.08 | **YES** | **RESOLVED** |
| 4.6 | D on CIFAR-100 | `gc1` | 4 v 4 | **+1.640** | se 0.245 / t 6.71 | **YES** | **RESOLVED in pp.** On *relative* error reduction it is the **smallest** effect in the corpus, not the largest — pick one scale and use it everywhere including the abstract |
| 4.7 | **Alignment is refuted as the carrier** | `pp1` permnode vs nodewise | 3 v 3 | **−0.009** | se 0.157 / t −0.06 | **YES** | **RESOLVED NULL**, pre-registered band |
| 4.8 | D is **batch-transportable** even though accuracy is not | the four D batches | — | sd(D) across batches **0.0994** vs **0.1719** expected from seed noise alone at n=3v3 | — | — | **RESOLVED.** This is why the anchor need not be re-run, and it repairs the design error in gf1 |
| 4.9 | The peak EXISTS (rise then fall) | `ms`/`rs` rising; `tw0` falling | 3 v 3 each | +0.655 / +0.626; −1.705 | t 3.72 / 3.03; t −10.56 | **YES** | **RESOLVED for existence** |
| 4.10 | The peak is **at** rung X | — | — | — | — | — | **NOT RESOLVED, AND MUST NOT BE CLAIMED.** CLOSEOUT 5.1 withdrew it; on the box-free n=6 replicate `fa1` the three rival rungs read +0.089/+0.070/+0.089, a third of the floor. The argmax also **moves with η**, not with the partition |

### §5 — THE PRESCRIPTION

| # | claim | runs | n | estimate | se / t | W? | status |
|---|---|---|---|---|---|---|---|
| 5.1 | Merging the 41 one-D tensors is worth +0.43 to +0.82 pp | `bn1` / `cc1` / `fa1` / `g3m` | 3v3, 3v3, 6v6, 9v9 | **+0.427 / +0.816 / +0.649 / +0.758** | t 10.4 / 5.13 / 5.88 / 8.13 | **YES ×4** | **RESOLVED.** Range is **+0.43 to +0.82** across four clean cells — CORRECTIONS 117.10 quotes only three; do not narrow it back |
| 5.2 | The census: 9,610 of 14,420 groups (66.64%) are size 1, over 0.086% of the weights, on 41 one-D tensors | `analysis/c82_singleton_census.py`, 7/7 self-checks | — | exact | — | — | **RESOLVED analytically**, re-derived this pass |
| 5.3 | **It is not a size law — the unit is the tensor** | `ck1` chunk1→chunk2 | 3 v 3 | **+0.115** | se 0.133 / t **0.87** | **YES** | **RESOLVED as a refusal.** Report against our own interest, *with its power limit*: that step re-groups 100% of 11.17M coordinates while the tail is 0.086% of the weights, so it refuses a **general size law** and cannot rule out a tail-specific effect |
| 5.4 | Every major optimizer ships a tensor-level rule and none justifies it | Adam-mini Alg. 3; Adalayer; Muon; LARS/LAMB; bitsandbytes; Shampoo; Adafactor | — | — | — | — | **RESOLVED from sources** — see the new table in `docs/PRIOR-ART.md` |

### §6 — WHAT WE COULD NOT SHOW (report as negatives, do not headline)

| # | claim | status |
|---|---|---|
| 6.1 | Net drift does not fall like 1/√N (6 of 6 fits positive) | **TRUE BUT MISNAMED.** *Drift* = \|Δβ̄\|/step is net systematic movement, **not** an estimator variance; it is **censored at the meta-stepsize** by Lion's sign update (two published fits ran through arms pinned at exactly 1.000e-03); surviving fits are 4-point log-log OLS with R² as low as **0.08**. **It cannot refute a variance claim.** Admissible sentence only: *"the net drift of a group's step-size exponent does not fall like 1/√(group size); we did not measure the estimator variance."* |
| 6.2 | N_eff/m anti-predicts accuracy (t −11.14) and dissociates (t −23.26) | Sound as a negative about **our own diagnostic**. Small audience; belongs in §6, never in the abstract |
| 6.3 | Hierarchical partial pooling — the classically correct remedy — fails | **M0 shrink WITHDRAWN** (operator saturates, half-life ≤693 steps against ~50,000); **M1** interior optimum is **76% an α₀ artefact** and transfers nowhere; **zpool** rescues +11.13 pp and still lands 2.30 pp *below* plain blk6. **[NOT RE-DERIVED — MASTER-TABLE 68/69/70/74/75]**. This is the section that disarms the "why not shrinkage?" referee question |
| 6.4 | The slope sign confusion | The name *"the drift-vs-N slope"* carries **−0.113/−0.110/−0.136** in CORRECTIONS 8b/12 and **+0.179/+0.268/+0.203** in 98.6/100.7. They are **two different axes** (drift vs log m, and drift vs group size). **Never quote a slope without naming its axis, its window (STARTUP vs STEADY) and its instrument version**, and quote ranges, not point values |

### §7 — METHODS (the runner-up, demoted to machinery, which is where it is strongest)

| # | claim | status |
|---|---|---|
| 7.1 | Batch is the unit of replication; seed is null | **[NOT RE-DERIVED]** F(62,85)=5.47, p=6.9e-13, sd≈0.21 vs F=1.21, p=0.213. **Reframe required:** our own CLOSEOUT diagnoses this as *tree/code/config state at submission* with hardware excluded by measurement — a **diagnosable bias**, not a general property of shared clusters. Claim the useful version: *pin and hash the tree per batch, report the hash, gate pooling on composition.* Disclose the `I1` incident (a batch that ran with an unidentified schedule active, `HF.py.bak_sched` timestamped 33 s before submission) as the mechanism |
| 7.2 | A free batch-effect ruler with the science held exactly fixed | `chunk1` (ck1) 90.979 n=3 and `weightwise` (tw0/wm9) 91.146 n=5 are the **same partition** (m = 11,173,962 both) in different batches: **+0.167 pp**. Almost nobody measures this |
| 7.3 | Composition audit | Quote the **registered 6/56 = 10.7%**, note it clears its bar by one cell, and give 13/56 as the post-hoc **coverage bound**. Never the reverse |
| 7.4 | Box occupancy must be read per-coordinate | `n_at_lo`/`n_at_hi`, **per seed, never pooled**. The per-tensor summary reported 0.000000 on 24 runs clipped in every record and **inverted an arm ranking** |
| 7.5 | `window_ok` does not mean "finished" | **NEW, cycle 88.** 16 runs of 1,960 are `window_ok=1` with `epochs_done < 0.9×requested`, and **`rs-blk6-1e4-s2` (29/100 epochs, plateau5 85.228) sits in the primary cell's blk6 arm**: including it moves the arm from **92.530 (sem 0.064) to 91.313 (sem 1.218)** — 1.22 pp and a 19× sem inflation, turning on an unregistered filter. Fixed by the `complete` column |

---

## 3. HONEST LIMITATIONS — the list a referee will assemble anyway

1. **One (base, meta) pair.** All **112** `chunk*`/`nodewise1d` rows are `SGDm + Lion` at
   η ∈ {1e-4, 3e-4}. **Zero** at η = 1e-3, zero under AdamW, and the N_eff ordering is known to
   invert under AdamW. This is simultaneously the paper's biggest hole **and** the axis §9 names.
   → **`aw1`, 12 jobs, no new code, is the cheapest reviewer-facing purchase in the programme.**
2. **The only cell that touches the parent's actual experiment is guard-unverified at a setting
   arithmetic says must bind.** The 18 `augment=0` runs sit at β₀ = ln(1e-6) = **−13.8155**
   against a **−15** floor (1.1845 nats) and a **−2.3026** ceiling (11.5129 nats). Under Lion
   \|Δβ\| = η per step, and 500 steps/epoch × 100 epochs = **50 nats of travel**: the floor is
   reachable at **epoch 2.4** and the ceiling at **epoch 23.0**. `runs/PP` holds only
   `Tensorboard_outputs` — **no `probe.jsonl` exists**, so occupancy is unmeasured in both
   directions. A floor bind on the single-group scalar arm while the 6-group arm differentiates
   away from it is exactly the mechanism that manufactures the +0.522. → **`ub9`, 9 jobs.**
3. **The peak's location is not resolved and must never be claimed** (ledger 4.10).
4. **The interior maximum is never observed inside one batch at n ≥ 2 per arm.** `ms` has only
   the rising limb, `tw0` only the falling limb; `rs` spans both with a **single** complete seed
   on the far side. Present the two in-batch legs as primary, the 15-rung curve as descriptive.
5. **RULE 11 is open on the partition contrast.** No chunk arm has ever been tuned. Partial
   defence: D holds at η=1e-4 (+0.485…+0.727) **and** at η=3e-4 (+0.630, `fa1`), and 3e-4 is
   nodewise's *own* bracketed argmax. But `fa1`'s nodewise arm **grazes the ceiling in 5 of 6
   seeds**, so that defence must travel with its caveat. `rl3` (running) closes this on R18 over
   (0, 3.18e-4] **and nowhere else** — above `ms_max_free = 3.18e-4` no rail is provably free at
   this budget, which is arithmetic, not a compute limit.
6. **100-epoch scope is real.** D goes significantly negative mid-training on `cc1` (−0.560,
   t −5.20 @ep55) and `g3m` (−0.518, t −4.06 @ep55), recovering by ep100; `mm1`/`pp1`/`fa1` are
   unresolved; `gc1` shows none. Publish the trajectory whatever `hz3` says.
7. **BatchNorm vs "size-1 tail" is under-identified.** Five measurements, all on nets whose only
   1-D tensors are normalisation parameters. `gn1`, the designated separator, **issued no
   verdict** — its pre-registered T0.6 commensurability gate fired on a 1.37× error-budget ratio.
   Its face values may **not** be quoted as a transfer result. Correct wording throughout:
   *"normalisation scalars or, more generally, one-dimensional tensors."*
8. **`ar1` is box-void** (floor-bound on all arms, asymmetrically, in the direction that inflates
   D). Its +0.697/+0.698 stay out of the primaries.
9. **Commensurability.** A percentage point is not comparable across error budgets. R18/C10 sits
   on a ~7-8 pp budget and C100 on ~29-30 pp; do not plot them on one axis or average them.
10. **Numbers are filter-sensitive.** Ledger 3.3 moves 0.69 pp between two defensible filters.
    **Re-derive every number at write time and state which filter produced it.**
11. **Prior art gap now closed but previously open.** CAM-HD (arXiv:2008.07277, IJMLC 2022) was
    absent from `docs/PRIOR-ART.md` entirely. It already builds the granularity ladder, already
    names the small-sample mechanism, already reports the interior optimum, and already fixes it
    with hierarchical partial pooling. It must be cited in the **first paragraph** of any
    granularity claim. What is ours: degenerate groups, 1-D tensors, the size-vs-alignment
    decomposition, count-matching, and MetaOptimize.
12. **`arXiv:2410.08198` may say the opposite of what PRIOR-ART claims.** Flagged UNVERIFIED; the
    PDF is not held locally. Re-derive before any draft.

---

## 4. WHAT THE CENTREPIECE EXPERIMENT WOULD ADD

### 4a. The briefed two-ladder centrepiece: **KILLED, and it is already on disk anyway**

The brief asked for a standard ladder vs a **size-floored** ladder, predicting the peak moves
finer or the curve becomes monotone. It fails on arithmetic, before any statistics:

| rung | standard m | min group size | floored m (k=8) | verdict |
|---|---|---|---|---|
| scalar | 1 | **11,173,962** | 1 | **BITWISE IDENTICAL** |
| blk6 | 6 | **1,856** | 6 | **BITWISE IDENTICAL** |
| layerwise | 62 | **10** | 62 | **BITWISE IDENTICAL** |
| nodewise | 14,420 | 1 | 6,011 | 0.380 dec of count exposure |
| weightwise | 11,173,962 | 1 | 1,396,745 | 0.903 dec of count exposure |

Any floor k ≤ 10 is the **identity** at three of five rungs — **including the primary cell's
argmax** (layerwise, m=62, 92.887, n=11, sem 0.052). So the peak cannot move, and the design's
own refutation condition ("both ladders share their peak") is **entailed by its construction**.
A design whose refutation is entailed by its construction cannot be registered.

Worse, `FLOOR_k(weightwise)` **is** chunkwise-K to within the ragged tail — verified: k=16 →
698,373 = chunk16 **exactly**; k=8 → 1,396,745 vs 1,396,746; k=128 → 87,302 vs 87,303; k=1024 →
10,943 vs 10,944. The "new" fine arm is the already-run `ck1` family. And the entire count
exposure is concentrated in exactly the two rungs meant to carry the result, in a region where
the local secants of the singleton-free family span **−0.09 to +0.83 pp/decade** and change sign
— so no covariate can rescue it.

**Killing this is a success under the project's own rule, and it costs nothing.**

### 4b. `gf1` as designed also had **zero power**, and that is now executable evidence

`gf1` registered *"TOST on DD at ±0.30"* as its equivalence branch. With the pooled within-arm
sd re-derived this pass (**0.2105**, df 18), at 4 arms × 5 seeds se(DD) = **0.1883**, so the TOST
bound is 0.30 − 1.746 × 0.1883 = **−0.0287 — negative**. The branch can **never** fire, whatever
the data say: the same unreachable-band mistake `gn1` already made at ±0.15. Under `gf1`'s own
stated prior the modal verdict was UNRESOLVED at ~100%. 80% TOST power would need **n = 14 per
arm (56 jobs)**. `analysis/c88_scorers.py --power` prints this.

Its two hypotheses were also strawmen: the only mechanism motivating the experiment (1/√N_g)
predicts DD ≈ **0.19**, inside `gf1`'s own pre-declared UNRESOLVED band.

### 4c. **`gf2` — the repaired design, same 20 jobs, a rule that can fire.** REGISTERED, APPENDIX-GRADE.

Two repairs, both forced by numbers re-derived this pass:

* **Drop the in-batch anchor.** `gf1` spent half its batch re-measuring D(1), justified by
  *"a cross-batch anchor would sit on the 0.21 pp floor"*. It would not — that floor is on
  **accuracy**, and D is a within-batch difference, so batch offsets cancel inside it. Observed
  sd of D across the four batches is **0.0994**, **below** the 0.1719 expected from seed noise
  alone. **D is batch-transportable.** The anchor is free; all four arms buy new information.
* **Buy two dose points, not one.** Singleton fraction is 66.64% at k=1 and **exactly 0% at every
  k ≥ 2**, so along `gf1`'s single axis "degeneracy removed" and "count reduced" are the same
  event (corr = −1) — the identical collinearity that killed the singleton ladder. One interior
  point cannot separate a step from a slope.

| arm | granularity | m | comparator | m | gap |
|---|---|---|---|---|---|
| A1 | `nodefloor2` | **9,615** | | | |
| A2 | `chunk1167` | | | **9,619** | 4 groups = 0.00018 dec |
| A3 | `nodefloor4` | **7,212** | | | |
| A4 | `chunk1560` | | | **7,212** | **EXACT** |

Statistic **S = D(2) + D(4)**, se(S) = **0.1883**. Three pre-registered points, **2.60 and 2.66
se apart**, giving **81-91% correct classification** at n=5:

| hypothesis | S | meaning |
|---|---|---|
| `H_SINGLETON` | **0.20** | the harm is specific to size-1 groups; pairs suffice |
| `H_SMOOTH` | **0.69** | harm declines smoothly in group size → shrinkage is the right instrument, and CAM-HD already published it |
| `H_TENSOR` | **1.19** | only a **whole** 1-D tensor recovers it — the first empirical justification for a rule five shipped optimizers all use and none justifies |

Decision rule: nearest point wins **and must be ≥ 1.5 se closer than the runner-up**; otherwise
**UNRESOLVED**, report the interval, and **do not call it "mixed evidence."**
Registered cross-check, fixed now so it cannot be dropped later: whatever `gf2` says must agree
in sign with `ck1`'s chunk1→chunk2 datum (ledger 5.3).

**What it adds:** it converts *"the unit is the tensor"* from an inference into a measured
dose-response. **What it does not add:** the paper does not depend on it. Ranked **below** `ub9`
and `aw1`.

**Blocker:** `gf2` needs `PATCH_NODEFLOOR`, which does not exist. Its spec is corrected in
CORRECTIONS 119.7 — the original spec had **two errors that would have failed its own equivalence
suite** (an `E6` assertion that is arithmetically false, and `E5` rows at k=3 and k=6 that are
**ragged and unimplementable** on the existing uniform `groups × gsize` machinery).

---

## 5. THE QUEUE, IN PRIORITY ORDER

| rank | tag | jobs | GPU-h | new code? | buys |
|---|---|---|---|---|---|
| 1 | **`ub9`** | 9 | ~9 | **no** | the only cell touching the parent's real experiment, currently arithmetically guaranteed to hit both rails by epoch 23 with no probe |
| 2 | **`aw1`** | 12 | ~11 | **no** | the corpus's single largest external-validity hole, and the axis §9 is indexed by |
| 3 | `lad1` | 12 | ~12 | no | scalar/blk6/layerwise/nodewise at n≥3 in **one** batch, so the interior maximum is observed rather than assembled |
| 4 | `gf2` | 20 | ~18 | **YES — `PATCH_NODEFLOOR`** | appendix-grade mechanism dose-response |

**Both accounts are committed** (`hz3` 24 jobs on alice, `rl3` 24 jobs on alice2). **Nothing may
be submitted from an analysis session.** Order of operations for `gf2` if it is ever funded:
`rl3` lands → confirm η=1e-4 is still the bracketed argmax → apply `PATCH_NODEFLOOR` on **alice**
(the reference `HF.py`) → run its equivalence suite green on CPU → hash `analysis/c88_scorers.py`
→ submit as **one** batch.

---

## 6. IS THIS A GOOD PAPER?

**It is now a good paper. It was not the paper that was proposed, and the proposed one was
unpublishable.**

What makes it good: the headline is a **measurement**, not a citation, and it is a measurement
nobody has made — the first granularity ladder with every rung at its own bracketed optimum, and
the first count-matched isolation of the group-size distribution from the group count. The
alignment null at t = −0.06 is a genuinely surprising result that contradicts Adam-mini's stated
principle in our regime. It makes two predictions a reader can falsify on their own hardware in
an afternoon. It reports three refutations of its own most attractive mechanism. And the
prescription — merge your one-dimensional tensors — is the first empirical justification for a
rule that Adam-mini, Muon, LARS/LAMB, bitsandbytes and Adafactor all ship and none of them
defends.

What keeps it from being a **great** paper, and this should not be papered over: the effect is
0.6 pp inside a method that is 1.8 pp behind a cosine schedule, and the whole partition story
currently rests on one base optimizer. `aw1` is 12 jobs and closes the second of those. The first
is not closeable by compute and must be answered by making scale the thesis rather than the
caveat — which is exactly what the chosen framing does.
