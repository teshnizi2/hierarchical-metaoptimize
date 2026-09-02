# Rewrite package `scorer-violation`

**Scope.** Gate S-EXTRA, red-team blocking item #1, Q05, and R0 checklist item 1
(`docs/STATUS.md`). Removes the `gn1` **GroupNorm** cell from the paper, because the cell's own
registered scorer refuses to issue a verdict on it, and re-derives every downstream number that
moves.

**Do not apply by hand-editing numbers.** Every figure below was recomputed from
`results/all_runs.csv` at commit `06d6539`; the re-derivation scripts are transcribed in §7 of this
document so an integrator or a referee can rerun them.

**Concurrency note for the integrator.** Two numbers in this package are also touched by the
`args-audit` package (`ml2`'s standard error, `0.142 → 0.195`). Every place where the two packages
interact is flagged **[ml2-interaction]** and both forms are given. Nothing else in this package
depends on another package.

---

## 1. What the scorer says

The cell is scored by `analysis/c84_gn1_score.py` (md5 `82c515d1ad490228ecb20f83288a510f`), written,
selftested and committed **before any `gn1` run existed in the CSV at all** — its own header says
so, and `docs/REGISTER-ideas-ABC.md` §4 registers it. Run unedited, on the raw run directory, per
STANDING RULE 16:

```
$ python3 analysis/c84_gn1_score.py --root ../runs_alice2/gn1
$ echo $?
1
```

It clears T0.5 (box occupancy `rec_lo = rec_hi = 0.0000` on all 24 probe dirs), clears T0.1–T0.4
(24/24 seeds pass), prints `--- T0 VERDICT: 0 of 4 arms void or dropped (none)` and the mandatory
four-arm table, and then **halts**, verbatim:

```
--- T0.6  **THE COMMENSURABILITY GATE.**  D_GN and D_BN are compared in
    PERCENTAGE POINTS, which only means something if the two nets sit on
    comparable ERROR BUDGETS.
    BN level 92.293 (budget 7.707 pp)   GN level 89.431 (budget 10.569 pp)
    difference -2.862 pp;  budget ratio 1.37x;  registered bar |diff| <= 2.0
    -> **FAIL -- GroupNorm sits in a DIFFERENT ACCURACY REGIME**
    **NO TRANSFER VERDICT IS ISSUED.**  D_GN and D_BN are not
    commensurable in pp at a 1.37x difference in error budget: if the gap
    is even partly MULTIPLICATIVE in the budget, D_GN is distorted by
    several times its own se, straddling both the +0.30 line and the
    [-0.15,+0.15] null band.  **THIS IS NOT A NULL** and it may not be
    written as one.  Registered in advance at cycle-84 review.
```

The scorer exits non-zero and **never reaches T1 or T2**. It therefore prints no `D_BN`, no `D_GN`
and no `dD`. Its own "WHAT THIS SCORER WILL NOT DO" list contains the line *"It will not report an
underpowered null as 'no gap'"*, and its T3.2 forbids rebranding the batch.

**The defect being fixed.** DRAFT-v2 states the scorer's verdict correctly in §7 (T7: *"`gn1` was
the designated separator and **issued no verdict**"*) and then contradicts itself three times:
Table 2 row 10 quotes `D_GN` as a cell, §4.4 counts it in the twelve-cell heterogeneity pool, and
§5.6 calls `dD = D_GN − D_BN` *"the decisive within-batch test"* that falsifies mechanism M7. §3.4
makes *"run the registered scorer unedited and quote its verdict"* a stated contribution of the
paper. Overriding it in the same document is the single most damaging item in the review, and it is
damaging in proportion to how loudly §3.4 advertises the discipline.

**What is removed.** The `gn1` **GroupNorm** contrast, everywhere: Table 2 row 10, the twelve-cell
pool, the design-point set, the abstract's counts, and the whole of §5.6's falsification argument.

**What is kept, and why.** The `gn1` **BatchNorm** contrast (Table 2 row 4) stays. T0.6 gates the
*comparison of D_GN with D_BN in percentage points*; it says nothing about `bn-ch − bn-node`, which
is an ordinary ResNet-18/BatchNorm/CIFAR-10/SGDm count-matched within-batch contrast of exactly the
kind `cc1`, `mm1` and `pp1` supply. The scorer's T0 verdict on those two arms is printed and is
`OK` on 4/4 seeds each. Two honesty conditions attach to keeping it, and both are met in the
replacement text below:

1. The scorer halts before T1, so `D_BN = +0.587 ± 0.153` is **not** a scorer verdict. It is a
   re-derivation from the four arm means the scorer *does* print, and it must be presented that
   way. (For the record: had the scorer reached T1, `D_BN` would have cleared it — the registered
   bar is `D_BN ≥ +0.30` and `t ≥ 2`, realised `+0.587`, `t 3.83`.)
2. The `gn1` GroupNorm **arm means** are still reported, in Appendix B, because the registration's
   T3.4 requires the four-arm table to be reported whole. What is deleted is the *contrast* formed
   from them and every statistic that pools it.

A maximally conservative integrator could instead drop **both** `gn1` rows on the grounds that the
scorer issued no verdict on either. That option is costed in §6 so the choice is informed; it
changes the pool by 0.001 pp and is not recommended, because it would discard a clean measurement
to punish a gate that was not aimed at it.

---

## 2. The re-derivation, cell by cell

`plateau5` (mean of the last 5 test epochs), Welch difference of arm means, `se` from the two arm
variances, unpaired. All seventeen drafted cells reproduce the drafted values exactly from
`results/all_runs.csv`:

| cell | n | nodewise | chunk | D | se | t | drafted |
|---|---|---|---|---|---|---|---|
| cc1 | 3v3 | 91.890 | 92.617 | +0.727 | 0.200 | 3.63 | matches |
| mm1 | 3v3 | 92.044 | 92.529 | +0.485 | 0.161 | 3.01 | matches |
| pp1 | 3v3 | 92.012 | 92.593 | +0.581 | 0.141 | 4.11 | matches |
| gn1 (BN) | 4v4 | 92.000 | 92.587 | +0.587 | 0.153 | 3.83 | matches |
| ml2 | 6v6 | 92.064 | 92.519 | +0.456 | 0.142 | 3.20 | matches **[ml2-interaction]** |
| rl3 @1e-4 | 3v3 | 91.908 | 92.589 | +0.681 | 0.173 | 3.93 | matches |
| rl3 @3e-4 | 3v3 | 92.507 | 93.098 | +0.591 | 0.096 | 6.18 | matches |
| fa1 | 6v6 | 92.327 | 92.957 | +0.629 | 0.123 | 5.11 | matches |
| hz3 | 6v6 | 92.816 | 93.244 | +0.428 | 0.086 | 4.94 | matches |
| **gn1 (GN)** | 8v8 | 89.330 | 89.532 | **+0.202** | **0.137** | **1.48** | **REMOVED** |
| aw1 | 3v3 | 92.978 | 93.257 | +0.279 | 0.087 | 3.19 | matches |
| nl1 (SGD) | 3v3 | 91.156 | 92.191 | +1.035 | 0.109 | 9.54 | matches |
| nl1 (RMSProp) | 3v3 | 92.155 | 93.129 | +0.973 | 0.251 | 3.87 | matches |
| g3m (R34) | 9v9 | 91.336 | 92.002 | +0.666 | 0.094 | 7.08 | matches (`chd`, chunk835) |
| r50 (R50) | 3v3 | 89.631 | 90.513 | +0.881 | 0.261 | 3.37 | matches |
| gc1 (C100) | 4v4 | 70.311 | 71.951 | +1.640 | 0.245 | 6.71 | matches |
| gm2 (C100) | 3v3 | 70.569 | 72.054 | +1.485 | 0.238 | 6.24 | matches |

`ar1` (`+0.697 ± 0.118`, t 5.90) also reproduces and remains excluded as box-void.

**Cell count: 17 → 16.** The removed cell was the only ResNet-18-GroupNorm cell and the only cell
using a normaliser other than BatchNorm.

**Minimum |t| among the sixteen survivors: 3.01 (`mm1`).** So the sentence *"Sixteen of seventeen
are resolved at t ≥ 3; the exception is the GroupNorm cell at t 1.48"* becomes *"All sixteen are
resolved at t ≥ 3.0"*. **[ml2-interaction]** if `ml2`'s se is corrected to 0.195 in the same pass,
`ml2`'s t becomes 2.34 and the sentence is instead *"Fifteen of sixteen are resolved at t ≥ 3.0;
the exception is `ml2` at t 2.34, whose three independent seeds were run twice under two names."*

---

## 3. Replacement text, keyed to DRAFT-v2 headings

### 3.1 Abstract — paragraph "**The measurement.**" (DRAFT-v2 ≈ L22–31)

**Replace the whole paragraph with:**

> **The measurement.** Replacing an architecture-aligned partition (one step size per output
> channel, `nodewise`) by a uniform one of the *same group count* (fixed-size chunks of K weights)
> is worth a positive amount of final accuracy in **every one of 16 within-batch, count-matched
> cells we measured**, spanning three networks (ResNet-18, ResNet-34, ResNet-50), 2 datasets,
> 4 base optimisers, 2 meta-stepsizes and 2 budgets. On ResNet-18/CIFAR-10 with an SGDm base the
> effect D = +0.456 ± 0.142 to +0.727 ± 0.200 pp across **six independent batches**; on ResNet-34
> D = +0.666 ± 0.094 (9 v 9); on ResNet-50 D = +0.881 ± 0.261; on CIFAR-100 D = +1.640 ± 0.245 and
> +1.485 ± 0.238. Over the eleven cells sharing an identical ResNet-18 partition contrast the
> fixed-effect pool is +0.571 with **Q = 36.4 on 10 df, p = 7.2e-5** — D varies genuinely across
> configurations (τ = 0.203 pp against 0.152 pp rms measurement error), not just noisily.

Three deletions inside that paragraph, each load-bearing:

* `17` → `16`;
* `four network variants (ResNet-18, ResNet-18 with GroupNorm, ResNet-34, ResNet-50)` → `three
  networks (ResNet-18, ResNet-34, ResNet-50)`. **GroupNorm was never a fourth network in the
  claimable corpus; it was a fourth network in a cell that has no verdict.**
* `and 2 normalisation schemes` → deleted outright. With the GroupNorm cell gone, **every cell in
  this paper uses BatchNorm.** This is the single most misleading phrase in the abstract, because it
  advertises exactly the generalisation the scorer refused to license.

**[ml2-interaction]** if `ml2`'s se is corrected in the same pass, the D-range clause reads
`+0.456 ± 0.195 to +0.727 ± 0.200`, and the pool/Q line becomes `+0.567 with Q = 36.7 on 11 df,
p = 1.3e-4, τ = 0.196 against 0.156 rms` (twelve cells: the eleven plus `ml2`).

### 3.2 Abstract — paragraph "**What we could not find.**" (DRAFT-v2 ≈ L38–46)

Two edits.

* `We report eight candidate mechanisms that died` → `We report seven candidate mechanisms that
  died and one that we cannot separate`. (See §3.7 for the M-index row and §5 for why the count is
  now inescapably a matter for R0 item 13.)
* `(|r| ≥ 0.602 needed at 11 design points` → `(|r| ≥ 0.632 needed at 10 design points`.

  *Re-derivation.* Two-sided 5% critical correlation at n design points is
  `t_crit(n−2)/sqrt(t_crit² + n − 2)`. n = 11: `2.262/sqrt(5.117+9) = 0.602` (reproduces the
  drafted value). n = 10: `2.306/sqrt(5.318+8) = 0.632`. The "≈ 25 design points to see |r| = 0.4"
  clause is unchanged (n = 25 gives r_crit 0.396).

### 3.3 §1, paragraph "**We do not have a mechanism.**" (DRAFT-v2 ≈ L96–101)

> **We do not have a mechanism.** We think that is worth saying in the first section rather than the
> last. The result is robust — 16 cells, every one positive, three networks, two datasets, four
> base optimisers — and seven separate candidate explanations for it are dead, five of them killed
> by tests we registered in advance and one killed by a reviewer after it had passed its own
> cross-validation. An eighth, the accuracy-level covariate, we can neither confirm nor separate
> from the network and base-optimiser axes it is aliased with (§5.6). A cross-validated *null* at
> n = 10 is defensible in a way a cross-validated success at n = 10 never is; we report both, and
> the null is the one that survives.

### 3.4 §1.1 Contributions, items 1 and 4 (DRAFT-v2 ≈ L105–113)

* Item 1: `replicated in 17 within-batch cells across four network variants, 2 datasets and 4 base
  optimisers` → `replicated in 16 within-batch cells across three networks, 2 datasets and 4 base
  optimisers`.
* Item 4: `**Eight dead mechanisms and two nulls**` → `**Seven dead mechanisms, one that the design
  cannot separate, and two nulls**`.

### 3.5 §4.3 Table 2 (DRAFT-v2 ≈ L419–443)

**Delete row 10 in its entirety** (`| 10 | gn1 | ResNet-18 (**GroupNorm**) | C10 | SGDm | 1e-4 | 100
| 8 v 8 | **+0.202** | 0.137 | 1.48 |`) **and renumber rows 11–17 as 10–16.** The replacement
table body:

```
| # | batch | network | dataset | base | η | epochs | n | **D (pp)** | se | t |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | cc1 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | 3 v 3 | **+0.727** | 0.200 | 3.63 |
| 2 | mm1 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | 3 v 3 | **+0.485** | 0.161 | 3.01 |
| 3 | pp1 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | 3 v 3 | **+0.581** | 0.141 | 4.11 |
| 4 | gn1 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | 4 v 4 | **+0.587** | 0.153 | 3.83 |
| 5 | ml2 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | 6 v 6 | **+0.456** | 0.142 | 3.20 |
| 6 | rl3 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | 3 v 3 | **+0.681** | 0.173 | 3.93 |
| 7 | rl3 | ResNet-18 | C10 | SGDm | 3e-4 | 100 | 3 v 3 | **+0.591** | 0.096 | 6.18 |
| 8 | fa1 | ResNet-18 | C10 | SGDm | 3e-4 | 100 | 6 v 6 | **+0.629** | 0.123 | 5.11 |
| 9 | hz3 | ResNet-18 | C10 | SGDm | 1e-4 | **300** | 6 v 6 | **+0.428** | 0.086 | 4.94 |
| 10 | aw1 | ResNet-18 | C10 | **AdamW** | 1e-4 | 100 | 3 v 3 | **+0.279** | 0.087 | 3.19 |
| 11 | nl1 | ResNet-18 | C10 | **SGD** | 1e-4 | 100 | 3 v 3 | **+1.035** | 0.109 | 9.54 |
| 12 | nl1 | ResNet-18 | C10 | **RMSProp** | 1e-4 | 100 | 3 v 3 | **+0.973** | 0.251 | 3.87 |
| 13 | g3m | **ResNet-34** | C10 | SGDm | 1e-4 | 100 | 9 v 9 | **+0.666** | 0.094 | 7.08 |
| 14 | r50 | **ResNet-50** | C10 | SGDm | 1e-4 | 100 | 3 v 3 | **+0.881** | 0.261 | 3.37 |
| 15 | gc1 | ResNet-18 | **C100** | SGDm | 1e-4 | 100 | 4 v 4 | **+1.640** | 0.245 | 6.71 |
| 16 | gm2 | ResNet-18 | **C100** | SGDm | 1e-4 | 100 | 3 v 3 | **+1.485** | 0.238 | 6.24 |
```

Note that row 4's network cell loses the `(BN)` qualifier: with no GroupNorm row left there is
nothing to distinguish it from, and the whole table is BatchNorm. **This also discharges the Table 2
caption sub-item of R0 checklist item 15** ("gn1's two rows share a batch") — `gn1` now has one row.

**Replace the paragraph immediately after the table with:**

> **D is positive in every cell, and all sixteen are resolved at t ≥ 3.0** (minimum `mm1`, t 3.01).
> A further cell (`ar1`, D = +0.697 ± 0.118) is **excluded** as box-void — it bound on the guards
> asymmetrically, in the direction that inflates D — and is reported here only so that its exclusion
> is visible. A **seventeenth** contrast exists and is also excluded: `gn1`'s ResNet-18/GroupNorm
> arms. Its registered scorer's commensurability gate fired (BN error budget 7.707 pp vs GN 10.569
> pp, ratio 1.37×, registered bar 2.0 pp) and the scorer printed **"NO TRANSFER VERDICT IS ISSUED …
> THIS IS NOT A NULL"** before reaching the contrast at all. We therefore quote no D for it here or
> anywhere else; its arm means are in Appendix B and its role in the design is discussed under T7 in
> §7.

**[ml2-interaction]** first sentence becomes: *"D is positive in every cell; fifteen of sixteen are
resolved at t ≥ 3.0, the exception being `ml2` at t 2.34 (§6.x)."*

### 3.6 §4.4 "D is genuinely heterogeneous" (DRAFT-v2 ≈ L451–462)

**Replace the whole subsection body with:**

> Over the **eleven** cells that share an identical ResNet-18 partition contrast
> (`nodewise` → `chunk777`; rows 1–4 and 6–12 above), the fixed-effect pool is **+0.571 ± 0.037**
> with
>
> > **Q = 36.4 on 10 df, p = 7.2e-5**; DerSimonian–Laird **τ = 0.203 pp** against an rms measurement
> > se of **0.152 pp**.
>
> Adding `ml2` as a twelfth cell: pool **+0.563**, Q = 37.0 on 11 df, p = 1.2e-4, τ = 0.194. So D
> varies across configurations by roughly **1.3×** its measurement error. §4.4a decomposes that
> heterogeneity; it is not unattributable.

Two things the integrator must not carry over:

* The sentence *"Dropping the GroupNorm cell: Q = 36.4 on 10 df, p = 7.2e-5"* is deleted, because
  the dropped cell is now the reported one. Quoting the twelve-cell figure as the primary and the
  eleven-cell figure as a sensitivity is exactly the inversion this package exists to undo.
* *"for reasons we cannot attribute"* is deleted here as well as in the abstract and §9 — that is
  R0 checklist item 2's edit, not this package's, but the two edits land on the same sentence and
  the integrator should apply item 2's decomposition text in place of the deleted clause.

*Re-derivation of every number in that block.* Inverse-variance fixed-effect pool
`Σw_i D_i / Σw_i` with `w_i = 1/se_i²`; `Q = Σ w_i (D_i − pool)²`; DerSimonian–Laird
`τ² = max(0, (Q − df)/(Σw − Σw²/Σw))`; rms se `sqrt(Σse_i²/k)`.

| pool | k | fixed-effect pool | Q | df | p | τ | rms se |
|---|---|---|---|---|---|---|---|
| 12 cells, as drafted | 12 | +0.546 ± 0.036 | 43.19 | 11 | 1.0e-5 | 0.215 | 0.151 |
| **11 cells, gn1-GN removed** | **11** | **+0.571 ± 0.037** | **36.40** | **10** | **7.2e-5** | **0.203** | **0.152** |
| 13 cells (12 + ml2), as drafted | 13 | +0.540 ± 0.035 | 43.56 | 12 | 1.8e-5 | 0.206 | 0.150 |
| **12 cells (11 + ml2)** | **12** | **+0.563 ± 0.036** | **37.02** | **11** | **1.2e-4** | **0.194** | **0.151** |
| **[ml2-interaction]** 12 cells, ml2 at se 0.195 | 12 | +0.567 ± 0.036 | 36.74 | 11 | 1.3e-4 | 0.196 | 0.156 |

The drafted 12-cell row reproduces the draft's `Q = 43.2 / 11, τ = 0.215, rms 0.151` exactly, which
is the receipt that the eleven-cell row was computed the same way and not re-tuned.

**Heterogeneity survives the removal, and so does the paper's use of it.** Q falls from 43.19 to
36.40, p from 1.0e-5 to 7.2e-5, and the excess-over-noise ratio τ/rms from 1.42× to 1.34×. Removing
the GroupNorm cell also *raises* the pooled D (+0.546 → +0.571), because the removed cell was the
smallest D in the pool. **Nothing in §4.4 depended on the removed cell.** Reporting that plainly is
worth more than the 0.02 of τ it costs.

### 3.7 §5 opening and the mechanism index (DRAFT-v2 ≈ L573–590)

* Section title `## 5. Eight dead mechanisms and two nulls` → `## 5. Seven dead mechanisms, one
  unseparable covariate, and two nulls`.
* Opening sentence `Six of these were killed by tests registered before their data existed` → `Five
  of these were killed by tests registered before their data existed`.
* `**Index of the eight, and where each dies.**` → `**Index of the eight candidates, and where each
  stands.**`
* **Replace the M7 row with:**

```
| M7 | D tracks the aligned arm's accuracy level | **not separable**: the registered within-batch separator issued no verdict; the remaining slope is aliased with network and base optimiser (−0.119 ± 0.022 holding base, −0.386 ± 0.105 holding network, −0.187 ± 0.125 holding both) | §5.6 |
```

* Title of the paper (`— and eight mechanisms it is not`) and §1's counts now disagree with the
  index in a second, independent way. **This package does not fix the title**; R0 checklist item 13
  already owns the count, and it now has one more input: the honest tally is **three mechanisms
  outright refuted** (M2, M3, M6), **one narrowed** (M4), **one untested** (M1), **one inapplicable**
  (M5), **one not identifiable** (M8) and **one not separable** (M7). Item 13's integrator should be
  told that M7 moved.

### 3.8 §5.6 — the section that has to be rewritten from scratch (DRAFT-v2 ≈ L698–718)

The drafted §5.6 rests on three legs. **One is deleted by this package and one reverses sign.**

| leg, as drafted | status after removing `gn1`-GN |
|---|---|
| "Inside CIFAR-10 the slope is zero: −0.021 ± 0.077, t −0.27, r −0.096 over 10 design points" | **reverses.** The removed cell *was* the flattening point. Over the 9 remaining CIFAR-10 design points the slope is **−0.161 ± 0.067, t −2.38, r −0.669**, exact permutation p = 0.0454 over all 9! = 362,880 orderings. |
| "The decisive within-batch test falsifies it" (`gn1` BN vs GN, dD = −0.385 ± 0.205, wrong-signed by 2.2–7.0 se) | **deleted.** It is the contrast the scorer refuses to issue. |
| "It is not a shared-arm artefact" | **survives.** The mechanically induced slope from the shared `nodewise` arm is −0.017 over the 9 points (mean sampling variance of a nodewise arm mean 0.01808; variance of level across the 9 points 1.07971), about one tenth of −0.161. |

**So M7's falsification does not stand.** Saying that plainly is the point of the package: the paper
claimed a mechanism was dead on the strength of a contrast its own registration forbade, and when
that contrast is withdrawn the surviving evidence points, weakly, the *other* way. What the corpus
can still say is that the level covariate is **not separable** from the axes it is aliased with, and
that no version of it survives being held to one network and one base optimiser at a time.

**Replace §5.6 in full with:**

> ### 5.6 Not dead, not separable: D and the aligned arm's accuracy level
>
> Over all 10 design points, regressing D on the aligned arm's `plateau5` gives slope
> **−0.044 ± 0.011, t −4.06, r −0.821** — which looks like a law and is not one, because level and
> dataset are the same column: the single CIFAR-100 design point sits at level 70.44 and the nine
> CIFAR-10 design points at 89.63–92.98.
>
> Inside CIFAR-10 the slope is **−0.161 ± 0.067, t −2.38, r −0.669** over 9 design points (exact
> permutation over all 9! orderings, p = 0.0454). We report that it is nominally resolved, and then
> report the four things that stop it being a mechanism.
>
> * **It is at the resolution floor by construction.** At 9 design points the two-sided 5% critical
>   correlation is |r| = 0.666. The realised |r| is 0.669. A result that clears its own critical
>   value in the third decimal place is a coin landing on its edge, not a law.
> * **It is aliased with the network and with the base optimiser, and the alias is the whole
>   effect.** The two lowest-level CIFAR-10 design points are `r50` (a different network) and
>   `nl1`/SGD (a different base optimiser). Holding the base fixed at SGDm (6 points, spanning
>   ResNet-18/34/50) gives **−0.119 ± 0.022**; holding the network fixed at ResNet-18 (7 points,
>   spanning four bases) gives **−0.386 ± 0.105**; holding **both** fixed — the only four points
>   where "level" varies with nothing else structural — gives **−0.187 ± 0.125, t −1.49, exact
>   permutation p = 0.333, unresolved.** A slope whose magnitude moves by 3.2× depending on which
>   confound you hold, and which vanishes when you hold both, is measuring the confounds.
> * **An instrument that does not share an arm with D does not resolve it.** D and level share the
>   `nodewise` arm. The mechanical slope this induces is −0.017, one tenth of −0.161, so the
>   artefact is not the explanation. But replacing level by an independent instrument — the mean of
>   the `chunk2325` and `nodewise1d` arms, neither of which enters D — gives **−0.167 ± 0.101,
>   t −1.65** within CIFAR-10 and does not clear the bar.
> * **The one within-batch contrast left in the corpus does not resolve it either.** `rl3` ran both
>   meta-stepsize rungs in one batch: level moves +0.599 pp (91.908 → 92.507) and D moves −0.090
>   (+0.681 → +0.591), an implied within-batch slope of **−0.150 ± 0.331 (t −0.45)**. Same sign as
>   the between-point slope, and an interval that contains zero and all three sub-slopes above. It is
>   also confounded with η, which is why it is a consistency check and not a test.
>
> **The registered within-batch separator issued no verdict.** `gn1` was built to answer exactly
> this question — one batch, one variable changed (BatchNorm → GroupNorm), batch cancels — and its
> pre-registered commensurability gate fired: the two halves sit on error budgets of 7.707 pp and
> 10.569 pp, a 1.37× ratio against a registered bar of 2.0 pp, so a percentage-point contrast
> between them is not defined. Its scorer prints **"NO TRANSFER VERDICT IS ISSUED … THIS IS NOT A
> NULL"** and halts before computing either contrast. An earlier version of this paper quoted that
> batch's face values as a falsification of the level model. We withdraw that, and we withdraw the
> falsification with it.
>
> **What is left is an honest negative-space statement, not a dead mechanism.** The accuracy level
> of the aligned arm is not separable from the network and the base optimiser in this corpus, at 9
> CIFAR-10 design points and a critical |r| of 0.666. We do not claim it is a carrier; we do not
> claim it is not; and §5.8 shows that as a *predictor* it is the worst of the four models we tried,
> out of sample. The design needed to separate it — a level contrast at fixed network, fixed base
> and commensurable error budget — is stated in §9.

### 3.9 §5.8 "Null: D is not predictable from configuration properties" (DRAFT-v2 ≈ L758–790)

The design points are defined by collapsing Table 2's cells: the six identical
ResNet-18/SGDm/η=1e-4/100-epoch batches (`cc1`, `mm1`, `pp1`, `gn1`-BN, `ml2`, `rl3`@1e-4) are one
point, the two CIFAR-100 batches are one, `gn1`-GN was one, and the rest are one each. Removing
`gn1`-GN takes the set from 11 to 10. *(Receipt that the reconstruction is the draft's own: the
11-point protocol reproduces the drafted LOO table to within 0.0002 RMSE on all five rows.)*

**Replace the opening sentence and the table with:**

> The sixteen D cells of Table 2 collapse to **10 distinct design points** (the six identical
> ResNet-18/SGDm/η=1e-4/100-epoch batches are one point; the two CIFAR-100 batches are one).
> Leave-one-design-point-out, refitting each single-predictor model on the held-in 9:
>
> | model | LOO RMSE | vs "predict the corpus mean" |
> |---|---|---|
> | **mean (baseline)** | **0.3857** | — |
> | D ∝ k·log(headroom) | 0.2691 | −30% |
> | CIFAR-100 dummy | 0.3763 | −2% |
> | D ∝ k·headroom | 0.3795 | −2% |
> | D ∝ level (OLS) | 0.8370 | **+117% WORSE** |

**Replace the paragraph "None of this is a result, and here is why" with:**

> **None of this is a result, and here is why.** The margin is dominated by the single CIFAR-100
> fold: the mean errs by −0.888 there and `k·log(headroom)` by −0.457, and restricted to the nine
> CIFAR-10 folds the best model wins by 0.040 RMSE (0.2788 → 0.2392, −14%), with a sign test of 7/9,
> two-sided p = 0.180. The functional form is itself the winner of about ten candidates scored on
> the same points, so any apparent improvement is a best-of-ten selection statistic before it is
> anything else. And the power bound is decisive: **at 10 design points a predictor needs |r| ≥
> 0.632 — it must explain ≥ 40% of the between-design-point variance — to be visible at p < 0.05**;
> seeing |r| = 0.4 would need ≈ 25 design points, which is not reachable by brute force.
>
> The level model earns its own sentence. Fitted on the nine CIFAR-10 points it predicts
> D(CIFAR-100) = **+4.11 against +1.56 observed**, an error of +2.55 pp — three times the error of
> simply predicting the corpus mean. A covariate that is nominally resolved *within* CIFAR-10
> (§5.6) and catastrophic the moment it is asked to leave it is a within-regime association, not a
> law.

**Replace the final block-quoted draft sentence with:**

> > **The draft sentence:** *D is real, replicated across 16 count-matched within-batch cells, and
> > varies genuinely across configurations (τ = 0.203 pp against 0.152 pp measurement noise). No
> > measurable property of a configuration predicts D out of sample better than the corpus mean by a
> > margin this design can resolve.*

*(The three-aliasings paragraph that follows is unchanged except that "1-vs-10 leverage contrasts"
becomes "1-vs-9 leverage contrasts".)*

### 3.10 §7 T7 (DRAFT-v2 ≈ L934–940)

The drafted T7 is already correct about the scorer and is the passage the rest of the draft
contradicted. It needs one added sentence so a referee can see the discipline was actually applied:

> **T7 — BatchNorm and "size-1 tail" are under-identified.** On every network we ran, the only 1-D
> tensors are normalisation parameters and one bias, so "the groups are degenerate" and "the groups
> are on the normalisation parameters" coincide exactly. `gn1` was the designated separator and
> **issued no verdict**: its pre-registered commensurability gate fired on a 1.37× error-budget
> ratio between the BatchNorm and GroupNorm halves (7.707 pp vs 10.569 pp against a registered bar
> of 2.0 pp), and its scorer halts before computing either contrast. **We therefore report its
> GroupNorm arm means (Appendix B) and no GroupNorm contrast: no D from those arms enters Table 2,
> the heterogeneity pool of §4.4, the design-point set of §5.8, or any count in the abstract.**
> Consequently **every cell in this paper uses BatchNorm**, and throughout we write *"normalisation
> scalars or, more generally, one-dimensional tensors"* rather than committing. The design that
> would separate them — a level contrast at fixed network, fixed base and commensurable error budget
> — is `gn2a`/`gn2b`, specified in advance in `bin/c84_normaliser_transfer.sh` and not run.

### 3.11 §7 T8 (DRAFT-v2 ≈ L942)

`n = 3 in ten of seventeen cells` → `n = 3 in ten of sixteen cells`. *(Re-derived: the ten 3 v 3
cells are `cc1`, `mm1`, `pp1`, `rl3`@1e-4, `rl3`@3e-4, `aw1`, `nl1`/SGD, `nl1`/RMSProp, `r50`,
`gm2`. The removed cell was 8 v 8, so the numerator is unchanged and only the denominator moves.)*

### 3.12 §9 (DRAFT-v2 ≈ L1017–1030)

* `**every one of 17 within-batch cells** across four network variants, two datasets, four base
  optimisers` → `**every one of 16 within-batch cells** across three networks, two datasets, four
  base optimisers`.
* `(Q 43.2 / 11 df, τ 0.215 pp against 0.151 pp noise)` → `(Q 36.4 / 10 df, τ 0.203 pp against
  0.152 pp noise)`.
* `Eight further mechanisms are dead:` → `Seven further mechanisms are dead:`.
* Delete the clause `accuracy level (wrong-signed within batch at every slope anyone has fitted, by
  2.2 to 7.0 se),` from the list and add, after the list: *"An eighth candidate, the aligned arm's
  accuracy level, is neither confirmed nor separable: it is aliased with the network and the base
  optimiser, and the within-batch separator we registered for it issued no verdict (§5.6, §7 T7)."*
* Add to §9's "the experiment that would break the degeneracy": *"and, for the level covariate, a
  normaliser or width contrast run at a commensurable error budget — `gn1` failed its own
  commensurability gate at a 1.37× budget ratio, and `gn2a`/`gn2b` were specified for this and not
  run."*

### 3.13 Appendix A.4 (DRAFT-v2 ≈ L1086–1090)

**Replace with:**

> **A.4 — Heterogeneity τ.** The record carried τ = 0.285 pp against 0.137 pp measurement noise.
> DerSimonian–Laird on the eleven ResNet-18/BatchNorm cells with Welch standard errors gives
> **τ = 0.203 pp** against an **rms se of 0.152 pp**. Q reproduces the record exactly on the
> record's own cell set (43.19 vs 43.0 on 11 df including the GroupNorm cell; 36.40 vs 36.3 on 10 df
> excluding it), and the excluding figure is now the reported one, because that cell's scorer issued
> no verdict (§7 T7). The conclusion — heterogeneity exceeds measurement error — is unchanged; the
> ratio is 1.3×, not 2×.

### 3.14 Appendix B (DRAFT-v2 ≈ L1130–1148)

**Keep both `gn1` rows** — the registration's T3.4 requires the four-arm table to be reported whole
— but relabel and footnote them:

```
| gn1 | 92.000 | 92.587 | — | — |
| gn1 GroupNorm arms (no contrast formed) | 89.330 | 89.532 | — | — |
```

with the footnote:

> The `gn1` GroupNorm arms are reported here for completeness because the batch's registration
> requires its four-arm table to be reported whole. **No contrast is formed from them anywhere in
> this paper**: the registered scorer's commensurability gate fired at a 1.37× error-budget ratio and
> issued no verdict (§7 T7). The two `gn1` lines above share one batch and 24 runs.

### 3.15 §3.4 "Registration discipline" (DRAFT-v2 ≈ L328–337) — a defect this package also closes

§3.4 lists the scorers used in the paper: `c76_mm1_score.py`, `c77_pp1_score.py`,
`c78_bn1_score.py`, `c81_cc1_score.py`, `c82_fa1_score.py`, `c83_gc1_score.py`, `c87_rl3_score.py`
and `c88_scorers.py`. **`analysis/c84_gn1_score.py` is not on that list, although the paper quotes
its batch four times.** Omitting the one scorer whose verdict the draft overrode is not a
coincidence worth leaving in place. **Append to the scorer list:**

> …`c87_rl3_score.py`, `c88_scorers.py` (committed at `5129e74`, before any `ub9`/`aw1` run existed;
> md5 `0363bcccb4d3bbad50beb19c9281b9be`), and `c84_gn1_score.py` (md5
> `82c515d1ad490228ecb20f83288a510f`), **which halted `gn1` at its commensurability gate and issued
> no verdict; we report that outcome rather than the contrast it declined to compute (§7 T7).**

§6.2 restates the same rule (*"if a batch has a registered scorer, it is scored by that scorer,
unedited, and its output is quoted, not paraphrased"*). Add one sentence after it:

> The most expensive application of that rule in this paper is `gn1`: its scorer halts before
> computing the contrast a whole subsection had been written around, and the subsection was rewritten
> rather than the scorer overridden (§5.6, §7 T7).

---

## 4. Every number this package changes, in one list

For the integrator's checklist. Left column is DRAFT-v2 as it stands; right column is the value
after removal. All right-column values are re-derived in §2, §3.6, §3.8, §3.9 and §7.

| where | was | becomes |
|---|---|---|
| cell count (abstract, §1, §1.1, §5.8, §7 T8, §9) | 17 | **16** |
| networks (abstract, §1, §1.1, §9) | four network variants incl. ResNet-18 GroupNorm | **three networks** |
| normalisation schemes (abstract) | 2 | **1 — clause deleted** |
| Table 2 rows | 17 | **16** (row 10 deleted, 11–17 renumbered 10–16) |
| resolved-at-t≥3 (§4.3) | 16 of 17, exception t 1.48 | **all 16, minimum t 3.01** |
| heterogeneity pool k (§4.4, A.4) | 12 | **11** |
| fixed-effect pool (abstract, §4.4) | +0.546 | **+0.571 ± 0.037** |
| Q (abstract, §4.4, §9, A.4) | 43.2 on 11 df, p 1.0e-5 | **36.40 on 10 df, p 7.2e-5** |
| τ (abstract, §4.4, §9, A.4) | 0.215 pp | **0.203 pp** |
| rms measurement se (abstract, §4.4, A.4) | 0.151 pp | **0.152 pp** |
| τ/noise ratio (§4.4) | 1.4× | **1.3×** |
| pool with `ml2` (§4.4) | 13 cells, Q 43.6/12, τ 0.206 | **12 cells, +0.563, Q 37.02/11, p 1.2e-4, τ 0.194** |
| design points (abstract, §5.6, §5.8) | 11 | **10** |
| critical \|r\| (abstract, §5.8) | 0.602 | **0.632** |
| all-design-point level slope (§5.6) | −0.043 ± 0.014, t −3.20, r −0.729 | **−0.044 ± 0.011, t −4.06, r −0.821** |
| within-CIFAR-10 level slope (§5.6, M-index) | −0.021 ± 0.077, t −0.27, r −0.096 | **−0.161 ± 0.067, t −2.38, r −0.669, perm p 0.0454** |
| shared-arm mechanical slope (§5.6) | −0.013 | **−0.017** (one tenth of the effect, not one twentieth) |
| gn1 within-batch dD (§5.6) | −0.385 ± 0.205, "falsifies" M7 | **DELETED — no verdict** |
| M7 verdict (§5, §9) | falsified within batch | **not separable** |
| dead-mechanism count (title, §1, §1.1, §5, §9) | eight | **seven + one unseparable** (final wording is R0 item 13's) |
| §5.8 LOO baseline | 0.4052 | **0.3857** |
| §5.8 level model | 0.3161, −22% | **0.8370, +117% WORSE** |
| §5.8 log-headroom | 0.3293, −19% | **0.2691, −30%** |
| §5.8 headroom | 0.3441, −15% | **0.3795, −2%** |
| §5.8 C100 dummy | 0.3972, −2% | **0.3763, −2%** |
| §5.8 within-CIFAR-10 margin | 0.006–0.012 RMSE, "nothing" | **0.040 RMSE (0.2788 → 0.2392), −14%, sign test 7/9, p 0.180** |
| §5.8 sign test | 9/11, p 0.065 | **8/10, p 0.109** (`k·log(headroom)`) |
| §5.8 leverage phrasing | 1-vs-10 | **1-vs-9** |
| §3.4 scorer list | 8 scorers, `c84_gn1_score.py` absent | **9 scorers, `c84_gn1_score.py` listed with its no-verdict outcome** |

---

## 5. Does anything get worse? Yes, and it must be stated

Three of the paper's claims are genuinely weaker after this removal, and hiding that would be the
same failure in a new place.

1. **M7's falsification is gone, and the surviving slope points the other way.** The drafted §5.6
   said the level model was falsified within batch and null inside CIFAR-10. Both legs came from the
   removed cell — it *was* the within-batch test, and it *was* the point that flattened the
   within-CIFAR-10 slope. Without it the within-CIFAR-10 slope is −0.161 ± 0.067 (t −2.38, exact
   permutation p 0.0454), nominally resolved. **M7 is downgraded from "dead" to "not separable".**
   The paper cannot claim eight dead mechanisms on this corpus.
2. **The corpus is narrower than advertised.** "Four network variants … and 2 normalisation
   schemes" becomes three networks and one normalisation scheme. Every cell in the paper uses
   BatchNorm. The T7 under-identification limitation (normalisation-scalars vs 1-D-tensors) is
   therefore *un-probed*, not probed-and-null.
3. **§5.8's within-CIFAR-10 null loosens.** The drafted margin over the corpus mean inside CIFAR-10
   was 0.006–0.012 RMSE ("nothing"); at 9 folds it is 0.040 (−14% for the best model, −16% for the
   level model). It still fails the sign test (7/9, p 0.180) and the power bound (|r| 0.669 against
   a critical 0.666 is not a margin), so the null holds — but it holds by less, and the sentence
   quantifying it must say so.

Against that, three things get **better**, and they are not cosmetic:

1. **The paper stops contradicting itself.** §7 T7 and §5.6/Table 2/§4.4 said opposite things about
   the same batch. After this package they agree.
2. **§3.4's contribution becomes true.** "Run the registered scorer unedited and quote its verdict"
   is now a claim the document honours in the one place where honouring it costs something.
3. **The primary gets stronger, not weaker.** The removed cell was the smallest D and the only one
   below t 3. The pool rises +0.546 → +0.571, and "positive in every cell, all resolved at t ≥ 3"
   is a cleaner sentence than "positive in every cell, sixteen of seventeen resolved".

---

## 6. The conservative alternative, costed

If a referee argues that the scorer's halt voids **both** `gn1` contrasts (it never reached T1, so
`D_BN` has no verdict either), the corpus becomes 15 cells and a 10-cell pool:

| pool | k | fixed-effect pool | Q | df | p | τ | rms se |
|---|---|---|---|---|---|---|---|
| 11 cells (recommended: drop `gn1`-GN only) | 11 | +0.571 ± 0.037 | 36.40 | 10 | 7.2e-5 | 0.203 | 0.152 |
| 10 cells (drop both `gn1` rows) | 10 | +0.570 ± 0.038 | 36.39 | 9 | 3.4e-5 | 0.215 | 0.152 |

The pool moves by 0.001 pp and Q by 0.01. **The choice is immaterial to every claim in the paper**,
which is itself the argument for keeping `D_BN`: nothing is being defended by keeping it except a
clean measurement. The recommendation stands — keep `gn1`-BN, present it as a re-derivation from the
arm means the scorer printed rather than as a scorer verdict, and say in §7 T7 that the scorer halts
before T1.

---

## 7. Re-derivation receipts

All from `results/all_runs.csv` at commit `06d6539` (2,113 rows; `sm3` not yet ingested and not used
here). `plateau5` throughout — never the CSV `plateau` column, which is mean-of-last-20 and banned
as primary.

**Scorer.** `python3 analysis/c84_gn1_score.py --root ../runs_alice2/gn1`, exit code 1, output
transcribed in §1. Scorer md5 `82c515d1ad490228ecb20f83288a510f`. No flag, no edit, no `--csv`
override.

**Cells.** Arms are selected by exact run name (`<batch>-<arm>-s<seed>`), one CSV row each, asserted
unique. `D = mean(chunk) − mean(node)`; `se = sqrt(sem_chunk² + sem_node²)`; unpaired (RULE 14).
Arm-name map used: `ch`/`ch7`/`chd` = the count-matched chunk arm, `node` = nodewise. `g3m` uses
`chd` (chunk835), which is the count match to `node`; `chg` (chunk2500) is the match to `n1d` and is
*not* the D arm — using `chg` would give +0.929 ± 0.094 instead of the correct +0.666 ± 0.094.

**Meta-analysis.** Inverse-variance fixed effect; `Q = Σ w_i (D_i − pool)²`; DerSimonian–Laird
`τ² = max(0, (Q−df)/C)` with `C = Σw − Σw²/Σw`; χ² survival for p.

**Design points and regressions.** Design points are the unweighted mean of D and of the nodewise
level over the batches collapsed into each point. The 11-point set reproduces the drafted §5.6
slopes (`−0.043 ± 0.014, t −3.20, r −0.729` over all; `−0.021 ± 0.077, t −0.27, r −0.096` within
CIFAR-10) and the drafted §5.8 LOO table to ≤ 0.0002 RMSE on every row — that agreement is the
receipt that the 10-point figures were produced by the same code path with one point removed and
nothing else changed.

**Permutation tests** are exact and exhaustive over all n! orderings of the response against a fixed
predictor: 9! = 362,880 for the 9-point CIFAR-10 slope (16,487 orderings reach |r| ≥ 0.669,
p = 0.0454) and 4! = 24 for the SGDm+ResNet-18 subset (8/24, p = 0.333).

**Independent instrument** for the level slope is the mean of the `chunk2325` and `nodewise1d` arm
means, neither of which enters D. It is available on 9 of the 10 design points (`gn1` ran only two
arms, so the instrument never included the removed cell in the first place — which is why its value
is identical, −0.167 ± 0.101, before and after the removal).

**Shared-arm mechanical slope** is `−var(nodewise arm mean sampling error)/var(level across design
points)` = `−0.01808/1.07971 = −0.0167`.

**Critical correlations** `t_crit(n−2)/sqrt(t_crit² + n − 2)`: n = 9 → 0.666, n = 10 → 0.632,
n = 11 → 0.602.

---

## 8. What this package does NOT touch

* `ml2`'s standard error (`args-audit` package). Every interaction is flagged **[ml2-interaction]**.
* The §4.4 base-optimiser decomposition (R0 item 2). This package deletes the *"for reasons we
  cannot attribute"* clause's host sentence; item 2 supplies the replacement.
* The title's mechanism count and the M-index re-partition (R0 item 13). This package supplies one
  more input to it: M7 moved from "dead" to "not separable".
* The word "byte-identical" (R0 item 4). §4.4's replacement text above already says "identical
  ResNet-18 partition contrast" instead, so item 4's integrator will find that phrase already gone
  from §4.4 and should still remove it from the abstract, Table 2's preamble and Appendix B.
* `hz3`, `ar1`, alignment, G, and every other cell.
