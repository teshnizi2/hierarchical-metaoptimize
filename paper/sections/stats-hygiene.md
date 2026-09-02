# Rewrite package `stats-hygiene`

**Covers gate items S3 / S5 / S9 and reviewer questions Q03, Q08, Q09, Q12, Q15.**
**Corresponds to R0 checklist items 6, 7, 8, 9, 13 and 14 in `docs/STATUS.md`.**

Written 2 Sep 2026. Every number below was re-derived at write time from
`results/all_runs.csv` (2,113 rows) under the admissibility gate
`window_ok == 1 AND complete == 1 AND plateau5 present`, from the raw `.out` series under
`runs/` and `runs_alice2/`, and — for `sm3`, which is not yet in the CSV — from the twelve
`.out` files on `alice` at `/data1/salehkaleybars/metaopt/runs/sm3-*.out`. §R at the end of
this document gives the derivation for every changed number and the scripts that produced it.

**This file does not edit `paper/DRAFT-v2.md`.** Each block below names the DRAFT-v2 anchor it
replaces, quotes the existing text verbatim under **FIND**, and gives the finished replacement
under **REPLACE WITH**. Blocks are independent; applying any subset leaves the draft consistent.

---

## 0. Index of edits

| # | DRAFT-v2 anchor | edit | why |
|---|---|---|---|
| E1 | §3.3 (new final paragraph) | multiplicity rule stated | S9 / Q08 |
| E2 | §5.4, the twelve-cell table + following prose | Holm over the 12 G contrasts; `ml2` se corrected | **S9 / Q08 (a)** |
| E3 | §3.3 (new paragraph, before *Box occupancy*) | test-set selection ledger | **S5 / Q09 (b)** |
| E4 | §4.5 closing sentence | label `dD = −0.090` an upper bound | S5 / Q09 |
| E5 | §7, new **T12** | test-set selection as a stated threat | S5 / Q09 |
| E6 | §8 (new subsection + Table 3) | **attrition table (c)** | **S3 / Q03** |
| E7 | §3.3 *Admissibility* paragraph | "under 90%" → "under 95%"; locate the 17 | S3 / Q03 |
| E8 | §4.3, after "**D is positive in every cell.**" | **completeness sentence (d)**, verified | **Q12** |
| E9 | title, abstract, §1, §1.1 #4, §5 heading + preamble, §9 | **mechanism count fixed (e)** | S9 / Q15 |
| E10 | §7 **T4** and abstract scope (ii) | **superlative removed (e)** | Q15 |

Two of these carry a correction that originates in a different package (the ARGS audit,
`docs/ARGS-AUDIT.md` / CORRECTIONS 125.1): the `ml2` standard errors. They are flagged
**[ARGS-AUDIT]** wherever they appear. The two packages agree to three decimal places; §R.7
shows the reconciliation.

---

## E1 — §3.3, new final paragraph: the multiplicity rule

**ANCHOR.** §3.3 *Metric, admissibility, and units of replication*, after the
*Unit of replication* paragraph (DRAFT-v2 ≈ line 322–325), before `### 3.4`.

**REPLACE WITH** (insert; nothing is deleted):

> **Multiplicity.** One family of tests in this paper is large enough that an uncorrected
> nominal α would be misleading: the secondary contrast `G`, which is measured once in every
> count-matched cell. We declare the family — the `G` leg of every cell in Table 2 that has
> one, twelve tests — and report Holm–Bonferroni step-down adjusted p-values for all twelve in
> §5.4. The primary `D` is **not** corrected and is not presented as a family of hypothesis
> tests: it is one quantity estimated in seventeen cells, reported as seventeen intervals and
> pooled once, and the claim made of it is "positive in every cell", not "significant in *k*
> cells". Where a p-value is quoted anywhere in this paper it is two-sided; at n = 3 v 3 we
> give the Welch–Satterthwaite value as primary and the normal approximation alongside it,
> because the two differ materially at 2–4 degrees of freedom and the paper's `t` columns are
> the normal-approximation quantity.

---

## E2 — §5.4: Holm over the twelve `G` contrasts

### E2.1 The table

**ANCHOR.** §5.4 *Dead: the tail carries it universally*, the twelve-row `| cell | D | G | D − G | t |`
table (DRAFT-v2 ≈ lines 660–673).

**FIND** (the two rows that change; the other ten are unchanged):

```
| ml2 (SGDm) | +0.456 ± 0.142 | +0.173 ± 0.071 | **+0.282 ± 0.159** | 1.77 |
```

**REPLACE WITH** — the whole table, so the integrator can paste one block:

> | cell | D | G | **D − G** | t |
> |---|---|---|---|---|
> | cc1 (SGDm) | +0.727 ± 0.200 | +0.011 ± 0.147 | **+0.715 ± 0.248** | 2.88 |
> | rl3 @1e-4 (SGDm) | +0.681 ± 0.173 | −0.011 ± 0.087 | **+0.692 ± 0.194** | 3.57 |
> | fa1 (SGDm) | +0.629 ± 0.123 | −0.001 ± 0.076 | **+0.630 ± 0.145** | 4.35 |
> | hz3 (SGDm, 300 ep) | +0.428 ± 0.086 | −0.057 ± 0.061 | **+0.484 ± 0.106** | 4.57 |
> | g3m (SGDm, R34) | +0.666 ± 0.094 | +0.171 ± 0.073 | **+0.495 ± 0.119** | 4.15 |
> | r50 (SGDm, R50) | +0.881 ± 0.261 | +0.153 ± 0.314 | **+0.729 ± 0.409** | 1.78 |
> | gm2 (SGDm, C100) | +1.485 ± 0.238 | +0.068 ± 0.069 | **+1.417 ± 0.248** | 5.72 |
> | nl1 (RMSProp) | +0.973 ± 0.251 | +0.020 ± 0.049 | **+0.953 ± 0.256** | 3.72 |
> | ml2 (SGDm) | +0.456 ± 0.195 | +0.173 ± 0.073 | **+0.282 ± 0.208** | 1.36 |
> | rl3 @3e-4 (SGDm) | +0.591 ± 0.096 | +0.217 ± 0.128 | **+0.375 ± 0.160** | 2.34 |
> | nl1 (SGD) | +1.035 ± 0.109 | +0.525 ± 0.294 | **+0.510 ± 0.314** | 1.63 |
> | **aw1 (AdamW)** | +0.279 ± 0.087 | **+0.232 ± 0.089** | **+0.047 ± 0.124** | **0.38** |
>
> `ml2`'s three standard errors are computed on **three** independent seeds, not six runs: its
> two nominal halves are the same command line including `--seed`, so the batch is three seeds
> run twice rather than six seeds (§6.1). Averaging within seed before differencing gives
> D +0.456 ± 0.195 (t 2.34), G +0.173 ± 0.073 (t 2.38), D − G +0.282 ± 0.208 (t 1.36). **Every
> point estimate is unchanged**; only the standard errors move.

**[ARGS-AUDIT]** — the three `ml2` standard errors above. If the args-audit package has already
applied the `dup_group` patch and a `dup_group`-aware reduction, these values will already be
present; they are byte-identical to what that patch produces (§R.7).

### E2.2 The Holm block

**ANCHOR.** §5.4, immediately after the table and its `ml2` note, **before** the paragraph
beginning "Under SGDm, removing the tail removes the gap."

**REPLACE WITH** (insert):

> **The twelve `G` tests, corrected for multiplicity.** `G` is measured once per count-matched
> cell, so the twelve values above are a family and the three that reach nominal significance
> should not be read one at a time. We declared the family as the `G` leg of every Table 2 cell
> that has one — twelve tests, fixed before the correction was computed — and applied
> Holm–Bonferroni step-down at α = 0.05. Each `p` is the two-sided Welch test on the two arm
> means; `p (z)` is the normal approximation, which is the quantity the paper's `t` columns
> report and is anti-conservative at 2–4 degrees of freedom.
>
> | cell | G | se | t | df | p (Welch) | p Holm | p (z) | p Holm (z) |
> |---|---|---|---|---|---|---|---|---|
> | aw1 (AdamW) | +0.232 | 0.089 | 2.62 | 3.5 | 0.067 | 0.74 | 0.0088 | 0.11 |
> | ml2 (SGDm) | +0.173 | 0.073 | 2.38 | 4.0 | 0.076 | 0.76 | 0.0173 | 0.21 |
> | g3m (SGDm, R34) | +0.171 | 0.073 | 2.34 | 16.0 | **0.033** | 0.39 | 0.0193 | 0.23 |
> | nl1 (SGD) | +0.525 | 0.294 | 1.79 | 2.8 | 0.177 | 1.00 | 0.074 | 0.67 |
> | rl3 @3e-4 (SGDm) | +0.217 | 0.128 | 1.69 | 3.9 | 0.168 | 1.00 | 0.091 | 0.73 |
> | gm2 (SGDm, C100) | +0.068 | 0.069 | 0.99 | 3.5 | 0.386 | 1.00 | 0.322 | 1.00 |
> | hz3 (SGDm, 300 ep) | −0.057 | 0.061 | −0.93 | 6.2 | 0.389 | 1.00 | 0.354 | 1.00 |
> | r50 (SGDm, R50) | +0.153 | 0.314 | 0.49 | 3.9 | 0.653 | 1.00 | 0.627 | 1.00 |
> | nl1 (RMSProp) | +0.020 | 0.049 | 0.41 | 3.4 | 0.710 | 1.00 | 0.686 | 1.00 |
> | rl3 @1e-4 (SGDm) | −0.011 | 0.087 | −0.12 | 2.1 | 0.913 | 1.00 | 0.902 | 1.00 |
> | cc1 (SGDm) | +0.011 | 0.147 | 0.08 | 2.4 | 0.944 | 1.00 | 0.938 | 1.00 |
> | fa1 (SGDm) | −0.001 | 0.076 | −0.01 | 9.8 | 0.993 | 1.00 | 0.993 | 1.00 |
>
> **At most three of the twelve reach nominal α = 0.05 and none survives Holm.** On the normal
> approximation the three are `aw1` (t 2.62), `ml2` (t 2.38) and `g3m` (t 2.34), with smallest
> adjusted p = 0.11; on the Welch degrees of freedom only `g3m` reaches nominal α, with
> smallest adjusted p = 0.39. **We therefore make no claim that `G` is resolved in any
> individual cell**, and the sentence this section previously rested on — that `G` is resolved
> under AdamW — is withdrawn as a per-cell claim.
>
> What survives the correction is not a cell but a **contrast between base optimisers**, which
> is a single pre-specified comparison and needs no family correction: `D − G` is
> +0.047 ± 0.124 (t 0.38) under AdamW against a fixed-effect pool of **+0.514 ± 0.064 (t 8.0)**
> over the six SGDm cells on the same network and dataset (ResNet-18/CIFAR-10; +0.558 ± 0.055
> if the R34, R50 and CIFAR-100 SGDm cells are pooled in as well, which §4.3's commensurability
> rule advises against). The tail accounts for essentially none of `D` under AdamW and for
> essentially all of it under SGDm, and that difference — not any single `G` — is the result.
> It is now measured in two independent AdamW batches: `sm3`, an independent replicate of `aw1`
> at every flag the meta-optimiser reads, gives G = +0.296 ± 0.096 and D − G = −0.155 ± 0.116,
> and the pooled 6 v 6 AdamW figures are D +0.210 ± 0.056, G +0.264 ± 0.060,
> **D − G = −0.054 ± 0.082**.
>
> **Two `G` contrasts exist in the corpus outside this table**, and we name them so the family
> is auditable rather than convenient. `bn1` ran `nodewise1d` and `chunk2325` (m = 4,851 in
> both arms) but no `chunk777` arm, so it yields a `G` and no `D`: G = +0.295 ± 0.048.
> `sm3` yields G = +0.296 ± 0.096. Enlarging the family to all fourteen and re-running Holm
> changes the count but not the verdict on the tabled twelve: on the Welch degrees of freedom
> **nothing survives Holm at fourteen either**; on the normal approximation `bn1`
> (adjusted p = 1.1e-8) and `sm3` (adjusted p = 0.030) survive and no cell in the table does.
> The fourteen-test family is also heterogeneous (Q = 40.1 on 13 df, p = 1.3e-4) where the
> tabled twelve is not (Q = 18.2 on 11 df, p = 0.077), driven by `bn1`; `bn1` and `cc1` are the
> same configuration in different batches and their `G` values differ by 0.284 ± 0.155
> (t 1.83), i.e. not resolved, which is what §6.3's cross-batch bound predicts.

### E2.3 The knock-on sentence in §5.4

**ANCHOR.** §5.4, the paragraph beginning "Under SGDm, removing the tail removes the gap."

**FIND:**

```
Under SGDm, removing the tail removes the gap. **Under AdamW it does not**: G is resolved at
t 2.62 and D − G collapses to +0.047. The pre-registration for that batch said, before the data
existed, that *"a RESOLVED non-null G would say the tail story is base-dependent and must be
re-scoped."* It is, and it is.
```

**REPLACE WITH:**

> Under SGDm, removing the tail removes the gap. **Under AdamW it does not**: `D − G` collapses
> to +0.047 ± 0.124 in `aw1` and to −0.054 ± 0.082 pooled over `aw1` and its replicate `sm3`,
> against +0.514 ± 0.064 pooled over the six ResNet-18/CIFAR-10 SGDm cells. `G` itself is positive under AdamW in
> both batches (+0.232 ± 0.089 and +0.296 ± 0.096) but survives Holm over the `G` family in
> neither (E2.2), so the base-dependence is carried by the `D − G` contrast, which is one
> pre-specified comparison, not by a per-cell `G` verdict. The pre-registration for that batch
> said, before the data existed, that *"a RESOLVED non-null G would say the tail story is
> base-dependent and must be re-scoped."* The re-scoping is warranted on the contrast; the word
> "resolved" is not, and we do not use it.

### E2.4 The §5 index-table row for M4

**ANCHOR.** §5, the index table, row `M4`.

**FIND:**

```
| M4 | The size-1 tail carries it universally | **narrowed to SGDm**: D − G = +0.715 ± 0.248 (SGDm) vs +0.047 ± 0.124 (AdamW) | §5.4 |
```

**REPLACE WITH:**

> | M4 | The size-1 tail carries it universally | **narrowed to SGDm**: D − G = +0.514 ± 0.064 pooled over the 6 ResNet-18/CIFAR-10 SGDm cells vs −0.054 ± 0.082 pooled over the 2 AdamW batches. No individual `G` survives Holm over the 12-test family | §5.4 |

*(The draft currently quotes `cc1`'s single largest SGDm `D − G`, +0.715 ± 0.248, as the SGDm
side of the comparison, and R0 checklist item 15 already asks for the pooled value instead.
**The checklist's +0.499 ± 0.062 is the pre-correction figure and must move to +0.514 ± 0.064**,
because down-weighting `ml2` — whose `D − G` is the lowest of the six — raises the pool. §R.4
reproduces both to three decimals, so the integrator can confirm the substitution is the `ml2`
`dup_group` correction and nothing else. The nine-cell pool including R34, R50 and CIFAR-100 is
+0.558 ± 0.055; we do not use it, because §4.3's commensurability warning forbids averaging
CIFAR-10 and CIFAR-100 effects on one axis.)*

---

## E3 — §3.3: the test-set selection ledger

**ANCHOR.** §3.3, insert as a new paragraph immediately after the *Admissibility* paragraph and
before *Box occupancy*.

**REPLACE WITH** (insert):

> **Selection on the test set, stated in full.** **No validation split was held out anywhere in
> this project.** CIFAR-10 and CIFAR-100 ship a 50,000/10,000 train/test split; we trained on
> the 50,000 and evaluated on the 10,000, and `plateau5` is a mean of five of those test
> evaluations. Every tuning decision in this paper was therefore made on the same 10,000 images
> the paper reports accuracy on. Six places where that matters:
>
> 1. **The metric is the test set.** Every accuracy in this paper, including both numbers in
>    §7 T4, is a test accuracy with no held-out estimate behind it.
> 2. **The operating point.** η = 1e-4 and α₀ = 1e-3 were chosen because both arms score better
>    there (§4.1). `D` depends on η at −0.189 pp per decade within batch (§4.5), so `D` is
>    reported at a test-selected operating point, not at a random one.
> 3. **§4.5's per-arm optima** are argmaxes over a two-rung η ladder taken on the same test
>    accuracies that define `D` (E4).
> 4. **§7 T4's two absolute numbers are both argmaxes**: the MetaOptimize cell is the maximum of
>    a seven-rung α₀ ladder and the baseline the maximum of a four-rung learning-rate grid, both
>    scored on the test set (E10).
> 5. **The β-box** was widened between batches in response to observed clipping, which is an
>    analysis-affecting choice made after seeing runs (§3.3 *Box occupancy*, §6).
> 6. **The metric window.** `plateau5` was made primary after the 20-epoch column produced two
>    withdrawn headlines (§3.3, Appendix A.2). The choice has a mechanical justification — a
>    trailing window longer than the plateau contains the mid-training trough of §4.8 at short
>    budgets and not at long ones — and it has been applied uniformly since, but it was not
>    fixed before the first analysis.
>
> Over the campaign, **418 distinct admissible configuration cells** were scored on that test
> set. Two consequences, and we separate them because they are not the same size.
> **For absolute accuracies the effect is the usual one and it is not small**: every level in
> this paper should be read as an optimistic, selection-inflated estimate, and we make no
> claim that any of them would survive on a genuinely held-out split.
> **For the contrasts it is much smaller, and for a structural reason**: `D`, `G`, `A`, `T` and
> `U` are differences between two arms trained and evaluated identically inside one batch,
> and **no arm and no cell was ever selected** — §4.3 shows that every count-matched contrast
> the corpus contains is reported, including the one that is excluded. What is selected is the
> operating point at which the contrast is measured, not the contrast. A reader should read
> `D = +0.546` as "the effect at a tuned operating point", which is the setting a practitioner
> is in, and should not read any absolute accuracy in this paper as a benchmark result.

---

## E4 — §4.5: label `dD` an upper bound

**ANCHOR.** §4.5, the paragraph after the quoted scorer block, beginning "The reportable
sentence is …".

**FIND:**

```
The reportable sentence is *"D is unchanged at matched optima to within 0.356 pp"*. This closes the
objection **on ResNet-18/CIFAR-10 and nowhere else**: no meta-stepsize ladder exists on ResNet-34,
ResNet-50 or CIFAR-100, and no ladder exists under AdamW.
```

**REPLACE WITH:**

> The reportable sentence is *"D is unchanged at matched optima to within 0.356 pp"*. This closes
> the objection **on ResNet-18/CIFAR-10 and nowhere else**: no meta-stepsize ladder exists on
> ResNet-34, ResNet-50 or CIFAR-100, and no ladder exists under AdamW.
>
> **`dD` is an upper bound in magnitude, and here is why.** The two rungs are η ∈ {1e-4, 3e-4}
> and the argmax was taken on the same test accuracies that define `D` (§3.3). Both arms'
> argmax landed on the same rung, η = 3e-4, so `D_own` is itself a clean within-batch
> count-matched contrast and carries no cross-arm selection. What it does carry is rung
> selection over two rungs at n = 3, and a test-selected argmax rewards the noisier arm more:
> at the selected rung the `nodewise` arm has sd 0.164 against the `chunk777` arm's 0.021
> (`plateau5`, n = 3 each). Selection therefore pushes `D_own` down and pushes the measured
> shrinkage `dD` away from zero, so **−0.090 ± 0.178 is the largest shrinkage this two-rung
> ladder can produce on this metric, not an unbiased estimate of it.** The conclusion — that
> re-tuning does not remove `D` — is conservative in the direction that matters, and we state
> it as a bound rather than as a null.

---

## E5 — §7: new threat T12

**ANCHOR.** §7 *Threats to validity*, after **T11 — Novelty scoping**, as the last item.

**REPLACE WITH** (insert):

> **T12 — Selection on the test set; no validation split.** No held-out validation split exists
> anywhere in this project. `plateau5` is a test-set quantity, the operating point (η, α₀, the
> β-box) was chosen on it, and both absolute numbers in T4 are argmaxes of ladders scored on
> it; 418 distinct configuration cells were scored on that same test set over the campaign
> (§3.3). Every absolute accuracy in this paper is therefore an optimistic estimate and none is
> offered as a benchmark result. The within-batch contrasts are much less exposed — no arm and
> no cell was selected, and §4.3 shows the reported set of count-matched contrasts is complete —
> but they are measured at a test-selected operating point, and `D` moves −0.189 pp per decade
> of η (§4.5). We cannot report a selection-free estimate of anything and we do not claim one.

---

## E6 — §8: the attrition table

**ANCHOR.** §8 *Reproducibility*, insert as a new subsection immediately after the **Data**
paragraph and before **Compute**.

**REPLACE WITH** (insert):

> **Attrition — every job we launched, and where each one went.** The ledger below reconciles
> the Slurm output directories on both clusters against the run table, so that a reader can
> confirm nothing was dropped silently. It is exhaustive: the two categories of loss are
> "crashed before epoch 1" and "budget too short for a plateau window", and neither touches a
> count-matched arm.
>
> **Table 3 — attrition ledger.** Job counts; GPU-hours where a wallclock was recorded.
>
> | stage | n | GPU-h | note |
> |---|---|---|---|
> | Slurm `.out` files on the two clusters | 2,193 | — | `runs/` + `runs_alice2/` + the on-cluster copies |
> | — infrastructure jobs, no training | −4 | — | `gtest`, `gtest2`, `mo-smoke`, `ts-pretok`; no `ARGS` line, no CSV row |
> | **jobs that entered the training script** | **2,189** | — | each logs one `ARGS` line |
> | — crashed or cancelled before epoch 1 | −64 | ≈0 | itemised below; **not one logged a single epoch** |
> | — completed but not yet ingested (`sm3`) | −12 | 10.1 | 12/12 complete at 100 epochs; §5.4 and §6.1 quote them |
> | **rows in `results/all_runs.csv`** | **2,113** | 1,582.2 | 2,098 carry a wallclock |
> | — `window_ok = 0`, `plateau5` present | −400 | } 66.3 | budget ≤ 20 epochs; `window_ok` is `epochs_done > 20` |
> | — `window_ok = 0`, `plateau5` absent | −25 | } | 2–5-epoch smoke tests |
> | — `window_ok = 1`, `complete = 0` | −17 | } | truncated 100-epoch runs; `complete` is `epochs_done ≥ 0.95 × requested` |
> | **admissible** | **1,671** | 1,515.9 | the gate of §3.3 |
>
> **The 64 that never produced an epoch**, by cause, read off their own tracebacks:
>
> | n | cause | batches |
> |---|---|---|
> | 36 | `LAM='na'` reached `float()` in the patched `HF.py` | `am4`, `amx` |
> | 12 | `BETA_CLIP` without the colon separator reached `str.split(':')` | `hs`, `ha` |
> | 6 | a block partition applied to the wrong network depth | `sc` |
> | 6 | CUDA device-side assert (CIFAR-100 label range) | `uc5` |
> | 4 | Slurm `CANCELLED` | `a0`, `g1` |
>
> All 64 died in `build_optimizer` or in the first minibatch, all are configuration errors that
> a later pre-submission guard now catches, and none consumed measurable GPU time. **None is in
> a count-matched arm**, so no contrast in Table 2, §4.6 or §5.4 is affected. Two of the five
> causes do touch material reported elsewhere and we name the contact rather than leave it to be
> found: the four Slurm cancellations are all `scalar`-arm runs (`g1-adamw-scal-s{0,1,2}` at
> α₀ = 1e-6, `a0-scal-1e3-s0` at α₀ = 1e-3), so the `scalar` column of §4.1's α₀ table is short
> by four runs relative to what was submitted — which is one of the reasons that table is
> labelled descriptive and cross-batch there, and why the in-batch η pair above it carries the
> claim; and the 48 `am4`/`amx`/`hs`/`ha` crashes are all hierarchical-pooling runs, in the
> region of §2.4 and §5.9 that Appendix A.9 already marks as carried from the project record
> rather than re-derived.
>
> **The 442 inadmissible rows are not failures; they are short-budget probes.** All 425
> `window_ok = 0` rows requested ≤ 20 epochs (392 at 20, 33 at 2–5) and so could never carry a
> five-epoch plateau at their requested budget. Only 17 of the 442 are 100-epoch runs, and those
> are the truncated ones. By granularity, the 442 are: `layerwise` 136, `weightwise` 111,
> `nodewise` 108, `resnet18_blocks` 56, `scalar` 30, no-partition baseline 1 — i.e. attrition is
> concentrated in the coarse and the maximally fine arms of the exploratory ladders, which is
> where the 20-epoch probes were run.
>
> **Attrition inside the primary contrasts is exactly zero.** The sixteen batches that carry a
> count-matched contrast contribute **272 runs, of which 272 are admissible**. More strongly:
> **every** uniform-chunk, `nodewise1d` and `permnode` run in the corpus — 214 rows — is
> admissible, so no count-matched cell could have been lost to the gate even in principle.
> Submitted `n` equals admissible `n` in all seventeen cells of Table 2 and in the excluded
> `ar1` cell.
>
> **One registration deviation, disclosed here rather than only in §5.4.** `aw1`'s registered
> scorer (`analysis/c88_scorers.py`, committed before the runs) specifies "12 jobs: `nodewise`
> and `chunk777` × 6 seeds". The submission script `bin/c90_awbase.sh` ran 4 arms × 3 seeds =
> 12 jobs instead: the same job count, four arms instead of two, and half the registered
> per-arm power on the primary. Every other batch's realised seed set matches its submission
> script's `SEEDS` line.
>
> *(If `sm3` has been ingested, the run-table line reads 2,125 rows / 1,592.3 GPU-h and the
> admissible line 1,683 / 1,526.0; the 442-row inadmissible block and the 64-job crash block are
> unchanged, since all twelve `sm3` runs are complete 100-epoch runs.)*

---

## E7 — §3.3: fix the *Admissibility* paragraph

**ANCHOR.** §3.3, the *Admissibility* paragraph.

**FIND:**

```
**Admissibility.** A run enters an analysis only if `window_ok == 1 AND complete == 1` and it
carries a readable `plateau5`. The second condition is not redundant: **17 of 2,113 runs pass
`window_ok` while having completed under 90% of their requested epochs**, and one of them
(29 of 100 epochs, `plateau5` 85.228) sits inside a primary arm, where including it moves that
arm's mean by 1.22 pp and inflates its sem 19-fold. Of 2,113 rows, 1,671 are admissible.
```

**REPLACE WITH:**

> **Admissibility.** A run enters an analysis only if `window_ok == 1 AND complete == 1` and it
> carries a readable `plateau5`. `window_ok` is `epochs_done > 20`; `complete` is
> `epochs_done ≥ 0.95 × epochs_requested`. The second condition is not redundant: **17 of 2,113
> runs pass `window_ok` while having completed under 95% of their requested epochs** (16 of the
> 17 finished under 90%; the seventeenth stopped at 94 of 100). The worst of them,
> `rs-blk6-1e4-s2`, ran 29 of 100 epochs and still reports `plateau5` 85.228; it sits in a
> `resnet18_blocks` arm of the `rs` meta-stepsize sweep, where including it moves that arm's
> mean by 1.22 pp and inflates its sem 19-fold. None of the 17 is in a count-matched arm — see
> the attrition ledger in §8, where attrition inside the primary contrasts is zero. Of 2,113
> rows, 1,671 are admissible.

---

## E8 — §4.3: the completeness sentence, verified

**Verification first, because the sentence the panel asked for is not quite true as they
phrased it and the true version is nearly as strong.**

We enumerated every batch in the corpus that ran any partition arm capable of entering a
count-matched contrast (`nodewise`, `nodewise1d`, `permnode*`, and every `chunk*`), split each
batch by the configuration keys that separate its arms (network, dataset, base, η, α₀, β-box,
budget), and listed which arms are present in each. The full listing is §R.5. Result:

* **18 batch-cells carry a `nodewise` arm together with a count-matched uniform-chunk arm.**
  These are exactly the 17 rows of Table 2 plus `ar1`. **No other batch in the corpus contains
  such a pair** — every other batch with a `nodewise` arm has `nodewise` and nothing to match it
  against. So for the primary contrast the panel's sentence is **true**.
* But the corpus contains **two further count-matched contrasts that are not `D`**, and a
  sentence that says "the complete set of count-matched contrasts" without qualification is
  false because of them: `bn1`'s `G` (`chunk2325` vs `nodewise1d`, m = 4,851 in both arms, no
  `chunk777` arm so no `D`), and `pp1`'s `A` (`permnode` vs `nodewise`, m = 14,420 in both arms
  — this is §4.6's alignment leg and is already reported, just not in Table 2).
* `sm3` adds a **19th** `D` cell once ingested, also positive (+0.141 ± 0.064).

So the strongest sentence the evidence supports is scoped to the contrast, not to the word
"count-matched" in general — and with that scope it is exhaustive and verifiable.

**ANCHOR.** §4.3, the paragraph beginning "**D is positive in every cell.**"

**FIND:**

```
**D is positive in every cell.** Sixteen of seventeen are resolved at t ≥ 3; the exception is the
GroupNorm cell at t 1.48. A further cell (`ar1`, D = +0.697 ± 0.118) is **excluded** as
box-void — it bound on the guards asymmetrically, in the direction that inflates D — and is
reported here only so that its exclusion is visible.
```

**REPLACE WITH:**

> **D is positive in every cell.** Sixteen of seventeen are resolved at t ≥ 3; the exception is
> the GroupNorm cell at t 1.48. A further cell (`ar1`, D = +0.697 ± 0.118) is **excluded** as
> box-void — it bound on the guards asymmetrically, in the direction that inflates D — and is
> reported here only so that its exclusion is visible.
>
> **Table 2 together with the excluded `ar1` cell is the complete set of count-matched
> `nodewise`-versus-uniform-chunk contrasts in this corpus. None is omitted, and the excluded
> one is also positive.** We verified this by enumeration rather than by recollection: of the
> 2,113 runs, every batch that ever ran a `nodewise` arm alongside a count-matched uniform-chunk
> arm is one of these eighteen, and every other batch carrying a `nodewise` arm has no arm to
> match it against. The enumeration also shows that no such cell could have been lost to the
> admissibility gate: all 214 uniform-chunk, `nodewise1d` and `permnode` runs in the corpus are
> admissible, and the sixteen batches involved contribute 272 runs of which 272 are admissible
> (§8, Table 3). Two further count-matched contrasts exist in the corpus and are reported
> elsewhere in this paper rather than in Table 2, because neither yields a `D`: `bn1` ran
> `nodewise1d` and `chunk2325` at m = 4,851 without a `chunk777` arm, giving G = +0.295 ± 0.048
> and no `D` (§5.4), and `pp1`'s `permnode` arm is the alignment leg `A` at m = 14,420 (§4.6).
> There is no third.

*(If the `sm3` ingest lands before submission, change "the complete set" clause to read
"Table 2 — including the `sm3` replicate — together with the excluded `ar1` cell", and "these
eighteen" to "these nineteen". Nothing else in the paragraph changes; `sm3`'s D is +0.141 ±
0.064, positive, so "the excluded one is also positive" and "positive in every cell" both
survive.)*

---

## E9 — the mechanism count

**The audit.** The §5 index table documents eight candidate mechanisms with these verdicts:
M1 *untested, not refuted*; M2 *dropped*; M3 *refused*; M4 *narrowed*; M5 *inapplicable*;
M6 *refuted*; M7 *falsified*; M8 *not identifiable*. Counting refutations: **four** (M2, M3, M6,
M7). One is narrowed but alive under SGDm (M4). Three cannot be decided by this instrument or
design at all (M1 untested, M5 inapplicable, M8 not identifiable). 4 + 1 + 3 = 8. The document
therefore does not support "eight dead mechanisms"; it supports "eight candidate mechanisms
examined, four refuted". §5.9's hierarchical partial pooling is a dead *fix*, not a mechanism,
and the draft already says so.

The draft also claims "six of them killed by tests we registered in advance". Within §5 the
document evidences a pre-registered gate for **two**: M2 (§5.2, "its own pre-registered gate")
and M4 (§5.4, "the pre-registration for that batch said, before the data existed"). §4.6's
alignment null is registered five ways. M7 is stated as killed by a reviewer. M3 (§5.3) and M6
(§5.5) are post-hoc contrasts on data collected for other purposes and no registration is quoted
for either. The replacement text below asserts only what the document evidences.

### E9.1 Title

**FIND (line 1):**

```
# The partition, not the count: a count-matched measurement of step-size granularity in online meta-gradient optimisation — and eight mechanisms it is not
```

**REPLACE WITH:**

> `# The partition, not the count: a count-matched measurement of step-size granularity in online meta-gradient optimisation — and the mechanism we could not find`

*Fallback, if the integrator prefers to keep a count in the title:*
`… — and eight candidate mechanisms, four of them refuted`.

### E9.2 Abstract

**FIND:**

```
**What we could not find.** We report eight candidate mechanisms that died, because they are half
the contribution.
```

**REPLACE WITH:**

> **What we could not find.** We examined eight candidate mechanisms and refuted four of them,
> narrowed a fifth to one base optimiser, and found the remaining three undecidable by this
> instrument or this design; we report all eight, because they are half the contribution.

### E9.3 §1, "We do not have a mechanism"

**FIND:**

```
base optimisers — and eight separate candidate explanations for it are dead, six of them killed by
tests we registered in advance and one killed by a reviewer after it had passed its own
cross-validation.
```

**REPLACE WITH:**

> base optimisers — and eight separate candidate explanations for it have now been examined:
> four are refuted, one survives only under an SGDm base, and three cannot be decided by this
> instrument or this design at all. Of the four refutations, one rests on a gate registered
> before its data existed (§5.2), one was killed by a reviewer after it had passed its own
> cross-validation (§5.6), and two are post-hoc contrasts on data collected for other purposes
> (§5.3, §5.5), which we say rather than leave to inference.

### E9.4 §1.1, contribution 4

**FIND:**

```
4. **Eight dead mechanisms and two nulls**, reported as a section rather than an appendix (§5),
   including the identifiability limit that makes the ninth unanswerable from this corpus.
```

**REPLACE WITH:**

> 4. **Eight candidate mechanisms — four refuted, one narrowed to a single base optimiser, three
>    undecidable by this design — and two nulls**, reported as a section rather than an appendix
>    (§5), including the identifiability limit that makes a ninth unanswerable from this corpus.

### E9.5 §5 heading and preamble

**FIND:**

```
## 5. Eight dead mechanisms and two nulls

This section is the second half of the contribution, not an appendix. Six of these were killed by
tests registered before their data existed; one was killed by a reviewer after it had passed its
own cross-validation; one was withdrawn after re-reading the sources it was attributed to.

**Index of the eight, and where each dies.**
```

**REPLACE WITH:**

> `## 5. Eight candidate mechanisms — four refuted — and two nulls`
>
> This section is the second half of the contribution, not an appendix. Of the eight, **four are
> refuted** (M2, M3, M6, M7), **one is narrowed** to an SGDm base and remains alive there (M4),
> and **three cannot be decided by this instrument or this design** (M1 untested, M5
> inapplicable, M8 not identifiable). One refutation rests on a gate registered before its data
> existed (M2); one was killed by a reviewer after it had passed its own cross-validation (M7);
> two are post-hoc contrasts on data collected for other purposes (M3, M6). One further
> candidate, M1, had its literature attribution withdrawn after we re-read the sources.
>
> **The refutations carry their own power limits and we print them with the verdicts.** M3 in
> particular refuses a general *size law* at t 0.87 and cannot rule out a tail-specific effect;
> "refuted" there means the general form is refuted, not that the tail is exonerated (§5.3).
>
> **Index of the eight, the verdict on each, and where each is decided.**

*(The eight-row index table itself is unchanged apart from the M4 row, which E2.4 replaces.
The headings of §5.1–§5.7 that begin "Dead:" are left alone by this package: they name the
hypothesis being tested and the verdict column of the index table carries the calibrated word.
An integrator who wants them consistent should change §5.1's "Dead:" to "Untested:", §5.4's to
"Narrowed:", §5.5's to "Refuted:" and §5.7's already reads "Dead (and un-killable)". That is an
optional consistency pass and no number depends on it.)*

### E9.6 §9 Conclusion

**FIND:**

```
best-fitting one is an arm indicator in disguise. Eight further mechanisms are dead: √N averaging
```

**REPLACE WITH:**

> best-fitting one is an arm indicator in disguise. Eight further mechanisms were examined and
> four are refuted, with the other four narrowed or undecidable: √N averaging

*(The list that follows this clause in §9 already gives each mechanism's true status in
parentheses — "untested, not refuted", "SGDm-specific", "not identifiable" — so no other change
is needed in that sentence.)*

---

## E10 — the T4 superlative

**The audit.** "The best MetaOptimize cell in 2,113 runs is 93.317 ± 0.083" is unsupported as
written, because it depends on a grouping key the sentence does not state. Re-derived over all
admissible cells at n ≥ 3:

* Among cells run with **plain** MetaOptimize (`HIER=none`), 93.317 ± 0.083 (`i3b`, ResNet-18,
  six blocks, AdamW base + Adam meta, η 1e-3, α₀ 3e-4, n = 3) **is** the corpus maximum, on any
  network. The claim is true under that key.
* Among **all** cells run under the MetaOptimize optimiser, including this project's own
  hierarchical variants (`HIER=additive`), the maximum is **93.967 ± 0.074** (`r34f`,
  ResNet-34, layerwise, SGDm + Lion, η 1e-3, α₀ 1e-6, η-ratio 0.025, n = 3) — 0.650 pp higher,
  on a different network.

And the deficit depends on the network, which the current text does not say. Against the
strongest baseline we ran at each network:

| MetaOptimize cell | plateau5 | baseline at that network | deficit |
|---|---|---|---|
| `i3b` R18 six blocks (best plain cell, corpus-wide) | 93.317 ± 0.083 | R18 SGD lr 0.1 + cosine, 95.124 ± 0.047 (n = 5) | **−1.807 ± 0.095** |
| `r34f` R34 layerwise, hierarchical (corpus max) | 93.967 ± 0.074 | R34 AdamW 1e-3 + cosine, 94.823 ± 0.035 (n = 3) | **−0.857 ± 0.081** |
| `g3m` R34 chunk2500 (best plain R34 cell) | 92.265 ± 0.053 (n = 9) | as above | **−2.558 ± 0.063** |
| `r50` R50 chunk884 (best plain R50 cell) | 90.833 ± 0.236 | R50 AdamW 1e-3 + cosine, 95.047 ± 0.110 (n = 3) | **−4.214 ± 0.260** |

The current text quotes the *smallest* of the plain-MetaOptimize deficits and calls it the
corpus's. Reporting the range is both more accurate and less flattering to the method, which is
the right direction for a threats section.

### E10.1 §7 T4

**FIND:**

```
**T4 — Competitiveness.** The best MetaOptimize cell in 2,113 runs is 93.317 ± 0.083 (n = 3;
six blocks, AdamW base + Adam meta, η = 1e-3, α₀ = 3e-4, itself the interior maximum of a 7-rung α₀
ladder). Tuned SGD + cosine at the same budget is 95.124 ± 0.047 (n = 5; lr 0.1, the interior
maximum of a bracketed 4-point grid: 94.172 / 94.844 / **95.124** / 94.181). The deficit is
**−1.807 pp**. MetaOptimize does beat a constant-LR AdamW tuned over four rungs (91.849 ± 0.092),
which is the comparison the parent paper makes. We make no competitiveness claim beyond that.
```

**REPLACE WITH:**

> **T4 — Competitiveness.** We state the grouping key, because the answer depends on it. Among
> the cells in this corpus that run **plain** MetaOptimize (no hierarchical pooling), the
> highest is 93.317 ± 0.083 (n = 3; ResNet-18, six blocks, AdamW base + Adam meta, η = 1e-3,
> α₀ = 3e-4, the interior maximum of a 7-rung α₀ ladder scored on the test set). Tuned
> SGD + cosine on the same network and budget is 95.124 ± 0.047 (n = 5; lr 0.1, the interior
> maximum of a bracketed 4-point grid: 94.172 / 94.844 / **95.124** / 94.181). The deficit is
> **−1.807 ± 0.095 pp**.
>
> That is the *smallest* deficit in the corpus, not a typical one, and the network is doing the
> work. On ResNet-34 the best plain cell is 92.265 ± 0.053 (n = 9) against 94.823 ± 0.035 for
> AdamW + cosine, a deficit of **−2.558 ± 0.063**; on ResNet-50 it is 90.833 ± 0.236 against
> 95.047 ± 0.110, a deficit of **−4.214 ± 0.260**. **The honest range is −1.8 to −4.2 pp behind
> a tuned schedule, and it widens with depth.**
>
> The single highest MetaOptimize cell anywhere in the corpus is not the one above: it is
> 93.967 ± 0.074 (n = 3; ResNet-34, layerwise, SGDm + Lion, η = 1e-3, α₀ = 1e-6, with this
> project's own additive hierarchical pooling at η-ratio 0.025), −0.857 ± 0.081 behind the
> ResNet-34 baseline. We do not lead with it: it is the last rung of a four-rung η-ratio ladder
> within its own batch, so its argmax is at the ladder boundary and is interior only when a
> second batch's rungs are appended, and §5.9 reports that this pooling operator does not
> generalise. It is stated here so that no reader can find a higher cell in the released table
> than the paper admits to.
>
> MetaOptimize does beat a constant-LR AdamW tuned over four rungs (91.849 ± 0.092), which is
> the comparison the parent paper makes. We make no competitiveness claim beyond that, and all
> six numbers in this item are test-set argmaxes with no held-out estimate behind them (T12).

### E10.2 Abstract scope (ii)

**FIND:**

```
allocation (489 of 1000 train classes present, validation set unlabelled). (ii) The best
MetaOptimize cell in the corpus reaches 93.317 ± 0.083 pp against a tuned SGD+cosine baseline at
95.124 ± 0.047 (n=5, the interior maximum of a bracketed grid) — a **1.807 pp deficit**. We make
no competitiveness claim.
```

**REPLACE WITH:**

> allocation (489 of 1000 train classes present, validation set unlabelled). (ii) MetaOptimize
> trails a tuned schedule at every scale we ran: on ResNet-18 its best plain cell reaches
> 93.317 ± 0.083 pp against a tuned SGD+cosine baseline at 95.124 ± 0.047 (n=5, the interior
> maximum of a bracketed grid), a **1.807 pp deficit**, and the deficit widens to 2.56 pp on
> ResNet-34 and 4.21 pp on ResNet-50. We make no competitiveness claim.

*(§7 T4's fourth sentence "(iv) The effect is ≈0.6 pp inside a method that is 1.8 pp behind a
cosine schedule" in the abstract's scope list should read "…that is 1.8 to 4.2 pp behind a
cosine schedule" for consistency. That is the only other place in the abstract the 1.8 figure
appears alone.)*

---

## R. Re-derivations

Everything below was run at write time against `results/all_runs.csv` (2,113 rows, md5 of the
file as read) and the `.out` series. Scripts are in the session scratchpad and are reproduced in
substance here; each is ten lines of pandas and re-derivable from this description alone.

### R.1 The gate, and the corpus totals

```
rows 2113 | admissible 1671 | dropped 442
window_ok==0 & plateau5 present : 400
window_ok==0 & plateau5 absent  :  25
window_ok==1 & complete==0      :  17      (disjoint; 400+25+17 = 442)
GPU-h total 1582.2 (2,098 rows carry a wallclock) | admissible 1515.9 | dropped 66.3
```

`window_ok = int(epochs_done > 20)` and `complete = int(epochs_done >= 0.95*epochs_requested)`,
both read from `analysis/aggregate.py` lines 27–48 and 193–197. This is the source of E7's
"under 95%": the 17 runs' completion fractions are 0.55, 0.50, 0.50, 0.85, 0.81, 0.69, 0.52,
0.89, 0.64, **0.94**, 0.40, 0.59, 0.44, 0.60, 0.29, 0.24, 0.36 — sixteen under 0.90 and one at
0.94, so "under 90%" is false for `rs-node-1e4-s1`.

Dropped rows by requested budget: 392 at 20 epochs, 33 at 2–5 epochs, 17 at 100 epochs.
Dropped rows by granularity: layerwise 136, weightwise 111, nodewise 108, resnet18_blocks 56,
scalar 30, `?` 1.

### R.2 The 64 jobs with an `ARGS` line and no CSV row

Walk `runs/` and `runs_alice2/` recursively (the recursion matters: `runs/failed_hier_v1/`
holds 12 `.out` that a non-recursive glob misses), keep files containing an `ARGS` line, parse
the job id from the `-NNNNNNN.out` suffix, and subtract the 2,113 `job_id` values in the CSV.
2,181 local `.out`, 4 without an `ARGS` line (`gtest`, `gtest2`, `mo-smoke`, `ts-pretok`), 2,177
with one, 64 of which have no CSV row. Classified by grepping their own tracebacks: 36
`ValueError: could not convert string to float: 'na'` at `HF.py:24` (`am4` 21, `amx` 15); 12
`ValueError: not enough values to unpack` at `HF.py:29` (`hs` 8, `ha` 4); 6 `ZeroDivisionError`
at `HF.py:175` (`sc`); 6 `CUDA error: device-side assert triggered` (`uc5`); 4 Slurm `CANCELLED`
(`g1` 3, `a0` 1). **Zero of the 64 contain an `Epoch ` line.** 2,177 local + 12 `sm3` = 2,189,
which reconciles exactly with the ARGS audit's cluster-side count.

### R.3 Holm

Family: the twelve `G = chunk2325-equivalent − nodewise1d` contrasts that are the `G` leg of a
Table 2 cell. Statistic: Welch difference of arm means, `se = sqrt(s²_a/n_a + s²_b/n_b)`,
Welch–Satterthwaite df, two-sided. `ml2` is reduced within seed first (three groups, not six
runs). Holm–Bonferroni step-down with the running-maximum monotonicity fix.

Sorted adjusted p, Welch df: 0.39 (g3m), 0.74 (aw1), 0.76 (ml2), then 1.00 for the rest.
Sorted adjusted p, normal approximation: 0.11 (aw1), 0.19 (ml2), 0.20 (g3m), 0.67, 0.73, then
1.00. **Nothing below 0.05 under either.** Nominal α = 0.05 is reached by g3m alone on Welch df
and by {aw1, ml2, g3m} on the normal approximation — hence E2.2's "at most three of the twelve",
which is true under both conventions.

Fourteen-test family (adding `bn1` and `sm3`): normal-approximation adjusted p = 1.1e-8 (bn1)
and 0.030 (sm3) survive; the next is 0.11 (aw1). Welch-df adjusted p = 0.096 (bn1), 0.53 (sm3),
0.43 (g3m) — none survives. Fixed-effect pool of `G`: over the 12, +0.067 ± 0.023 with
Q = 18.21 on 11 df (p = 0.077); over the 14, +0.119 ± 0.021 with Q = 40.08 on 13 df (p = 1.3e-4).

`hz3` sensitivity, because §7 T9 flags its seed-5 trio: `G` on all six seeds is −0.057 ± 0.061;
on the five seeds sharing the `-30:9.0` box it is −0.050 ± 0.075. `D` moves +0.428 → +0.464.
Neither moves any Holm verdict.

### R.4 The SGDm `D − G` pool, and why the checklist's value moves

Inverse-variance fixed-effect pools of the SGDm rows of §5.4's table, `ml2` seed-collapsed:

```
6 ResNet-18/CIFAR-10 SGDm cells   +0.514 +- 0.064  t 8.00   <- use this
  (cc1 .715/.248, rl3@1e-4 .692/.194, fa1 .630/.145,
   hz3 .484/.106, ml2 .282/.208, rl3@3e-4 .375/.160)
9 SGDm cells, adding g3m/r50/gm2  +0.558 +- 0.055  t 10.21
```

R0 checklist item 15 carries **+0.499 ± 0.062** for this quantity. That is the same six cells
with `ml2`'s **pre-correction** se of 0.159 instead of 0.208; re-running the pool with 0.159
returns +0.499 ± 0.062, t 8.02 exactly. So the checklist value is not wrong, it is stale by one
correction: down-weighting `ml2`, whose `D − G` is the lowest of the six, raises the pool by
0.015 pp. **The substitution +0.499 → +0.514 is attributable entirely to the `ml2` `dup_group`
fix and to nothing else**, which is why it is safe for the integrator to apply mechanically.

### R.5 The count-matched enumeration (E8)

Every batch-cell in the corpus containing at least one of
`{nodewise, nodewise1d, permnode*, chunk*}`, split by (family, network, dataset, base, η, α₀,
β-box, budget). Cells carrying **`nodewise` + a count-matched chunk arm** — i.e. capable of a
`D` — are exactly:

`cc1`, `mm1`, `pp1`, `gn1`-BN, `gn1`-GN, `ml2`, `rl3`@1e-4, `rl3`@3e-4, `fa1`, `hz3`, `aw1`,
`nl1`-SGD, `nl1`-RMSProp, `g3m`, `r50`, `gc1`, `gm2` (= Table 2's seventeen), and `ar1`
(excluded). **Eighteen.**

Every other batch containing a `nodewise` arm has that arm alone: `at1`, `bd7`, `bf8`, `bf9`,
`bl5`, `bo6`, `bo7`, `br6`, `c100f`, `cl5`, `ff5`, `fr5`, `fz`, `fz3`, `gc`, `gn1smoke`, `gp`,
`hz9`, `ml5`, `mx_sig_nodewise_s{0,1,2}`, `n1`, `nd`, `ns5`, `p2`–`p7`, `rs`, `sp8`, `tw0`,
`uc5`, `uc6`, `v_nodewise`, `wc5`. None can form a count-matched pair.

Count-matched pairs that are **not** `D`: `bn1` (`chunk2325` + `nodewise1d`, m = 4,851 both, no
`chunk777`) and `pp1` (`permnode0/1/2` + `nodewise`, m = 14,420 both). `sm3`, once ingested,
becomes the nineteenth `D` cell.

Attrition inside these: the sixteen contributing batches supply 272 runs in count-matched arms,
all 272 admissible. Corpus-wide, all 154 `chunk*` rows, all 57 `nodewise1d` rows and all 3
`permnode` rows are admissible — 214 for 214.

### R.6 `sm3`, re-derived from the cluster

`sm3` is not in `results/all_runs.csv`. Its twelve `.out` on `alice` at
`/data1/salehkaleybars/metaopt/runs/` each log 100 `Epoch` lines and a `RUN_DONE`. Taking the
mean of the last five `Test Accuracy` values per run:

| arm | seeds 0/1/2 | mean ± sem |
|---|---|---|
| `nodewise` | 93.120 / 93.070 / 93.118 | 93.103 ± 0.016 |
| `chunk777` | 93.334 / 93.126 / 93.272 | 93.244 ± 0.062 |
| `nodewise1d` | 92.864 / 93.068 / 93.126 | 93.019 ± 0.079 |
| `chunk2325` | 93.216 / 93.404 / 93.326 | 93.315 ± 0.055 |

D = **+0.141 ± 0.064** (t 2.22); G = **+0.296 ± 0.096** (t 3.07); D − G = **−0.155 ± 0.116**.
Pooled 6 v 6 with `aw1`: D **+0.210 ± 0.056** (t 3.76), G **+0.264 ± 0.060** (t 4.42),
D − G **−0.054 ± 0.082**. Wallclock 608 min = **10.1 GPU-h**. Its own `ARGS` line carries
`--alg-meta RMSProp … --alg-meta Lion`, so it ran Lion; the value quoted in this package is
therefore a Lion replicate of `aw1`, exactly as CORRECTIONS 125.2 records.

### R.7 Reconciliation with the ARGS audit **[ARGS-AUDIT]**

The audit's salvage line for `ml2` gives D +0.456, se 0.142 → 0.195, t 3.20 → 2.34; G +0.173,
se 0.071 → 0.073, t 2.44 → 2.38. Re-deriving here by averaging `plateau5` within seed across the
`ml2-adam-*` / `ml2-rms-*` pair before differencing reproduces all six figures to three decimals.
The two packages agree. The only value this package adds is the knock-on to `D − G`:
+0.282 ± 0.159 (t 1.77) → **+0.282 ± 0.208 (t 1.36)**, because the `D` and `G` standard errors
are combined in quadrature.

### R.8 T4 (E10)

Group all admissible runs by the full configuration key (network, dataset, batch size,
granularity, base, meta, η, α₀, γ, augment, β-box, `HIER`, λ, η-ratio, budget) plus batch, keep
cells at n ≥ 3, sort by mean `plateau5`. Restricting to `HIER` in {none, missing} — plain
MetaOptimize — the maximum over the whole corpus is `i3b` at 93.317 ± 0.083. Without that
restriction the maximum is `r34f` at 93.967 ± 0.074. The `r34f` η-ratio ladder within its own
batch reads 0.005 → 93.307, 0.01 → 93.419, 0.015 → 93.803, 0.025 → 93.967: monotone to the last
rung. Appending the `r34r` batch (0.02 → 93.912, 0.03 → 93.849, 0.04 → 93.494) makes 0.025 an
interior maximum, but across two batches. Baselines: `bl-sgd-01` 95.124 ± 0.047 (n = 5) with the
four-rung grid 94.172 / 94.844 / 95.124 / 94.181 reproducing exactly; `f5cos-r34-1e-3`
94.823 ± 0.035 (n = 3); `f5cos-r50-1e-3` 95.047 ± 0.110 (n = 3). Deficits and their standard
errors (added in quadrature) are in E10's table.

### R.9 Multiplicity denominator (E3)

Distinct admissible configuration cells, grouped on (network, dataset, batch size, granularity,
base, meta, η, α₀, γ, augment, β-box, `HIER`, λ, η-ratio, budget): **418**.

---

## X. Notes for the integrator

1. **Numbers this package changes, and nothing else does.** `ml2`'s three standard errors
   (shared with the ARGS-audit package, verified identical); §5.4's SGDm `D − G` pool; §3.3's
   "under 90%" → "under 95%"; T4's superlative and its two extra deficits; the abstract's scope
   (ii) and (iv); the mechanism count in six places.
2. **Numbers this package deliberately does not touch**, because another package owns them:
   §4.4's Q and τ (the `ml2` se change lowers Q, which the ARGS audit flags as favourable and
   still requiring recomputation); Table 2 row 5's `n` column; §6.1's "two independent
   measurements" wording; §7 T9's `hz3` seed-5 story; the `gn1`-GN removal. Where E2 quotes a
   value that one of those packages will also change, it is marked **[ARGS-AUDIT]**.
3. **The SGDm `D − G` pool moves from +0.499 ± 0.062 to +0.514 ± 0.064** (E2.4, §R.4). This is
   the `ml2` `dup_group` correction propagating and nothing else; R0 checklist item 15 carries
   the pre-correction value and should be updated with it. Use the same figure in §5.4's prose
   and in the §5 index table's M4 row.
4. **If `sm3` is ingested** before submission, four figures in this package move and each is
   given inline where it appears: the run-table row of Table 3 (2,125 / 1,592.3 GPU-h), the
   admissible row (1,683 / 1,526.0), E8's "eighteen" → "nineteen", and the `G` family becomes
   thirteen tests as tabled (still nothing surviving Holm on Welch df).
5. **Nothing in this package requires GPU time.** All five deliverables are re-derivations of
   data already on disk plus one read-only `ssh alice` to recover `sm3`'s twelve `.out`.
