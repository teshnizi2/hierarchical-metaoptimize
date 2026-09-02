# PACKAGE `contradictions` — S1–S7

Seven internal contradictions and fifteen orphan labels. Every number below was re-derived at
write time from `results/all_runs.csv` (2,173 rows) through the paper's own
`analysis/c98_figures.py` `load()` / `cells()` / `arm()` / `welch()` / `dup_group` logic. No
registered scorer was edited or run out of contract. Two standalone re-derivation scripts were
written for this package and are quoted in full where they matter:
`scratchpad/loo.py` (§5.8) and `scratchpad/level.py` + `scratchpad/level2.py` (§5.6).

**Both re-derivation scripts were validated by first reproducing the published numbers they
replace, to four decimal places, before being run on the enlarged cell set.** Details in
§"Re-derivations" at the end.

**Concurrency warning.** Item **S7** edits the abstract, which the `abstract` package (G2/G4)
also rewrites. My S7 change is a single-clause swap; whichever package lands second must keep the
corrected attribution (the network list belongs to the twenty count-matched cells, not to the
2,173 rows). Item **S4c** touches §5.6, which no other listed item claims.

---

## S1 — §3.5's heading contradicts its own next paragraph

Three of the four pre-registered batches (`bm2`, `sm4`, `rp1`) are scored; only the `hz3` seed-5
trio (R2) is still out. The heading, the table caption and the paragraph's closing clause all
still say two.

### paper.tex

**(a) heading — line 920**

REPLACE
```
\subsection{Four pre-registered batches: two scored, two still in flight}
```
WITH
```
\subsection{Four pre-registered batches: three scored, one still in flight}
```

**(b) the paragraph's opening — add the missing Table pointer (also closes S6/`tab:inflight`)**

REPLACE
```
are addressed by four batches submitted while this draft was being written.
```
WITH
```
are addressed by the four batches of Table~\ref{tab:inflight}, submitted while this draft was
being written.
```

**(c) the paragraph's closing clause**

REPLACE
```
can check that the two verdicts we did read are the ones we said we would read.
```
WITH
```
can check that the three verdicts we did read are the ones we said we would read.
```

**(d) caption of `tab:inflight` — lines 943–944**

REPLACE
```
\caption{The four pre-registered batches. Two have been scored by running their registered
scorers unedited; the other two contribute no number to this paper.}
```
WITH
```
\caption{The four pre-registered batches. Three have been scored by running their registered
scorers unedited; the fourth, \arm{hz3}-R2, is still queued and contributes no number to this
paper.}
```

### DRAFT-v4.md

**(a) heading — line 719**

REPLACE
```
### 3.5 Four pre-registered batches: two scored, two still in flight
```
WITH
```
### 3.5 Four pre-registered batches: three scored, one still in flight
```

**(b)**

REPLACE
```
run, are
addressed by four batches submitted while this draft was being written.
```
WITH
```
run, are
addressed by the four batches tabulated below, submitted while this draft was being written.
```

**(c)**

REPLACE
```
can check that the two verdicts we did read are
the ones we said we would read.
```
WITH
```
can check that the three verdicts we did read are
the ones we said we would read.
```

**(d) md table caption line — the md table has no caption; instead REPLACE the sentence
immediately preceding it is unnecessary. No further md change for (d).**

---

## S2 — "There is no third" is false: `rp1` is a third

`rp1` is a fourth-arm count-matched contrast: `nodewise` against `permnode101/202/303`, four arms
× six run seeds (6–11) = 24 runs, **all four arms at m = 14,420** (verified from the CSV:
`rp1` contributes `nodewise` 6, `permnode101` 6, `permnode202` 6, `permnode303` 6). Like `pp1`'s
`permnode` arm it yields an `A`, not a `D`, which is exactly why it sits in §4.6.1 rather than in
Table 2 — so the fix is to *state that reason for all three*, not to move it into Table 2.

### paper.tex — lines 1352–1355

REPLACE (one contiguous block, verified unique)
```
Two further count-matched contrasts exist in the
corpus and are reported elsewhere in this paper rather than in Table~\ref{tab:D}, because neither
yields a $\Dstat$: \arm{bn1} ran \arm{nodewise1d} and \arm{chunk2325} at $m = 4{,}851$ without a
\arm{chunk777} arm, giving $\Gstat = +0.295 \pm 0.048$ and no $\Dstat$ (\S\ref{sec:tail}), and
\arm{pp1}'s \arm{permnode} arm is the alignment leg $\Astat$ at $m = 14{,}420$
(\S\ref{sec:alignment}). There is no third.
```
WITH
```
Three further count-matched contrasts exist in the
corpus and are reported elsewhere in this paper rather than in Table~\ref{tab:D}, and the reason
is the same in all three cases --- none of them yields a $\Dstat$. \arm{bn1} ran \arm{nodewise1d}
and \arm{chunk2325} at $m = 4{,}851$ without a \arm{chunk777} arm, giving
$\Gstat = +0.295 \pm 0.048$ and no $\Dstat$ (\S\ref{sec:tail}). \arm{pp1}'s \arm{permnode} arm is
the alignment leg $\Astat$ of Eq.~\ref{eq:A} at $m = 14{,}420$ (\S\ref{sec:alignment}). And
\arm{rp1} re-runs that same alignment contrast at higher power --- \arm{nodewise} against
\arm{permnode101}, \arm{permnode202} and \arm{permnode303}, four arms $\times$ six run seeds,
\textbf{all four arms at $m = 14{,}420$} --- which is again an $\Astat$ and not a $\Dstat$, and is
reported in \S\ref{sec:rp1}. There is no fourth.
```

*(this replacement also closes S6/`eq:A`.)*

### DRAFT-v4.md — lines 1026–1029

REPLACE
```
Two further count-matched contrasts exist in the corpus and are reported
elsewhere in this paper rather than in Table 2, because neither yields a `D`: `bn1` ran `nodewise1d`
and `chunk2325` at m = 4,851 without a `chunk777` arm, giving G = +0.295 ± 0.048 and no `D` (§5.4),
and `pp1`'s `permnode` arm is the alignment leg `A` at m = 14,420 (§4.6). There is no third.
```
WITH
```
Three further count-matched contrasts exist in the corpus and are reported
elsewhere in this paper rather than in Table 2, and the reason is the same in all three cases —
none of them yields a `D`. `bn1` ran `nodewise1d` and `chunk2325` at m = 4,851 without a
`chunk777` arm, giving G = +0.295 ± 0.048 and no `D` (§5.4). `pp1`'s `permnode` arm is the
alignment leg `A` at m = 14,420 (§4.6). And `rp1` re-runs that same alignment contrast at higher
power — `nodewise` against `permnode101`, `permnode202` and `permnode303`, four arms × six run
seeds, **all four arms at m = 14,420** — which is again an `A` and not a `D`, and is reported in
§4.6.1. There is no fourth.
```

---

## S3 — §4.3's absolute contradicts §4.4's sensitivity check

§4.3 says the GroupNorm cell's `D` is quoted nowhere; §4.4 quotes it. The **sensitivity check in
§4.4 is legitimate and stays untouched.** §4.3's absolute is the false claim and is corrected to
say exactly where the one permitted quotation lives.

Re-derived (`c98_figures.cells()` with `WITH_GN = True`): `gn1` GroupNorm cell
**D = +0.2023, se = 0.1366, t = 1.48, n = 8 v 8**, aligned 89.330, uniform 89.532 — i.e. exactly
the `+0.202 ± 0.137` §4.4 prints.

### paper.tex — lines 1336–1338

REPLACE
```
We therefore quote no $\Dstat$ for it here or anywhere else; its
arm means are in Appendix~\ref{app:arms} and its role in the design is discussed under T7 in
\S\ref{sec:threats}.
```
WITH
```
We therefore give it no row in Table~\ref{tab:D} and admit it to no pool: a cell whose scorer
issued no verdict cannot be a forest row or a pool member. Its $\Dstat$ is quoted \textbf{once} in
this paper and nowhere else --- $+0.202 \pm 0.137$ ($t\ 1.48$, 8 v 8) in \S\ref{sec:moderator},
solely to show that the base-optimiser decomposition does not depend on the exclusion --- and it
is never reported as a normalisation-scheme result. Its arm means are in
Table~\ref{tab:arms} and its role in the design is discussed under T7 in \S\ref{sec:threats}.
```

*(this replacement also closes S6/`tab:arms`.)*

### DRAFT-v4.md — lines 1013–1015

REPLACE
```
here or anywhere else; its arm means are in Appendix B and its role in the design is discussed under
T7 in §7.
```
WITH
```
in Table 2 and admit it to no pool: a cell whose scorer issued no verdict cannot be a forest row
or a pool member. Its `D` is quoted **once** in this paper and nowhere else — +0.202 ± 0.137
(t 1.48, 8 v 8) in §4.4, solely to show that the base-optimiser decomposition does not depend on
the exclusion — and it is never reported as a normalisation-scheme result. Its arm means are in
Appendix B and its role in the design is discussed under T7 in §7.
```
*(the preceding words in md read `We therefore quote no D for it` — after this replacement the
sentence reads "We therefore quote no D for it in Table 2 and admit it to no pool: …". Verified
against md line 1013: `…ISSUED … THIS IS NOT A NULL"** before reaching the contrast at all. We
therefore quote no D for it` / line 1014 begins `here or anywhere else;`.)*

---

## S4a — the two stale **batch** counts (tex 1349, tex 3469)

These two are *batch* counts, not cell counts, and both re-derive.

**Definition used (unchanged from the previous draft, recovered by reproducing its numbers):** a
batch "carries a count-matched contrast" iff it appears in Table 2, or is the box-void `ar1` cell,
or is `bn1` (a count-matched `G` with no `D`), or — new — is `rp1` (a count-matched `A`, see S2).
Batch = the run-name prefix before the first hyphen. Runs = every row of `all_runs.csv` belonging
to those batches.

| set | batches | runs | admissible |
|---|---|---|---|
| previous draft: 14 Table-2 batches + `ar1` + `bn1` | **16** | **272** | 272 |
| now: 17 Table-2 batches + `ar1` + `bn1` + `rp1` | **20** | **332** | 332 |

The previous draft's pair (16, 272) reproduces exactly, which is what licenses the extension.
The three new Table-2 batches are `bm2`, `sm3`, `sm4`; `rp1` is added because S2 establishes it
as a count-matched contrast.

Independently re-derived and **unchanged**: 256 uniform-chunk / `nodewise1d` / `permnode` rows,
all 256 admissible, 238 outside `rp1` and 18 inside it. (Granularity census: `chunk*` 172,
`nodewise1d` 63, `permnode0/1/2` 3, `permnode101/202/303` 18.)

### paper.tex — line 1349

REPLACE
```
sixteen batches involved contribute 272 runs of which 272 are admissible
```
WITH
```
twenty batches involved contribute 332 runs of which 332 are admissible
```

### paper.tex — lines 3469–3470

REPLACE
```
\textbf{Attrition inside the primary contrasts is exactly zero.} The sixteen batches that carry a
count-matched contrast contribute \textbf{272 runs, of which 272 are admissible}.
```
WITH
```
\textbf{Attrition inside the primary contrasts is exactly zero.} The twenty batches that carry a
count-matched contrast --- the seventeen of Table~\ref{tab:D}, plus \arm{ar1}, \arm{bn1} and
\arm{rp1} --- contribute \textbf{332 runs, of which 332 are admissible}.
```

### DRAFT-v4.md — lines 1025–1026

REPLACE
```
and the sixteen batches involved
contribute 272 runs of which 272 are admissible
```
WITH
```
and the twenty batches involved
contribute 332 runs of which 332 are admissible
```

### DRAFT-v4.md — lines 2735–2736

REPLACE
```
**Attrition inside the primary contrasts is exactly zero.** The sixteen batches that carry a
count-matched contrast contribute **272 runs, of which 272 are admissible**.
```
WITH
```
**Attrition inside the primary contrasts is exactly zero.** The twenty batches that carry a
count-matched contrast — the seventeen of Table 2, plus `ar1`, `bn1` and `rp1` — contribute
**332 runs, of which 332 are admissible**.
```

---

## S4b — the two stale **cell** counts in §4.6 and §4.6.1 (tex 1860, 1965)

Table 2 has twenty rows across **three networks** (ResNet-18 ×18, ResNet-34 ×1, ResNet-50 ×1),
**two datasets** (CIFAR-10 ×18, CIFAR-100 ×2), **four base optimisers** (SGDm, SGD, RMSProp,
AdamW) and **two meta-optimisers** (Lion ×19, RMSProp ×1, the `sm4` cell) — all four counts
re-derived from `cells()`. That matches §1.1's contribution-1 wording exactly, which is the
phrasing these two sentences should have carried all along.

### paper.tex — line 1860

REPLACE
```
  $\Dstat$ is measured in sixteen count-matched within-batch cells across three networks, two
  datasets and four base optimisers. The two results are not on the same evidential footing and
```
WITH
```
  $\Dstat$ is measured in twenty count-matched within-batch cells across three networks, two
  datasets, four base optimisers and two meta-optimisers. The two results are not on the same
  evidential footing and
```

### paper.tex — lines 1965–1966

REPLACE
```
$\eta$ rather than at its own argmax of $3\times10^{-4}$ --- against a $\Dstat$ measured in sixteen
count-matched cells across three networks, two datasets and four base optimisers.
```
WITH
```
$\eta$ rather than at its own argmax of $3\times10^{-4}$ --- against a $\Dstat$ measured in twenty
count-matched cells across three networks, two datasets, four base optimisers and two
meta-optimisers.
```

### DRAFT-v4.md — lines 1440–1442

REPLACE
```
`D` is measured in sixteen count-matched within-batch
   cells across three networks, two datasets and four base optimisers.
```
WITH
```
`D` is measured in twenty count-matched within-batch
   cells across three networks, two datasets, four base optimisers and two meta-optimisers.
```

### DRAFT-v4.md — lines 1534–1535

REPLACE
```
inherited η rather than at its own argmax of 3e-4 — against a `D` measured in sixteen
count-matched cells across three networks, two datasets and four base optimisers.
```
WITH
```
inherited η rather than at its own argmax of 3e-4 — against a `D` measured in twenty
count-matched cells across three networks, two datasets, four base optimisers and two
meta-optimisers.
```

---

## S4c — §5.8's LOO-RMSE table, **recomputed on all twenty cells**

### Answer to the question asked

> *"Report whether the conclusion (the mean wins inside CIFAR-10) survives."*

**The premise is itself stale, and the answer is a clean no-change.** "The mean wins inside
CIFAR-10" was the *project record's* reading (0.2791 vs 0.2863, sign test 8/11); Appendix A.3.5
already superseded it — on the sixteen-cell set the best headroom model *beat* the mean inside
CIFAR-10, 0.2791 → 0.2395 (−14%). On all twenty cells the same thing happens and by the same
margin: **0.2637 → 0.2222, −16%.** The sign tests move from 8/10 and 7/9 to 9/11 and 8/10 —
`p = 0.065` and `p = 0.109`, both still short of 0.05. **The §5.8 null survives unchanged.**

### The design-point rule, stated because the recomputation exposed that it was never stated

The old parenthetical named two collapses (the six R18/SGDm/1e-4/100 batches; the two CIFAR-100
batches) and left the rest implicit. Applied to twenty cells the implicit rule is ambiguous, so
this package states it: **two cells are one design point when they run the same network, dataset,
base–meta pairing, η and budget in different submissions.** That gives **11 design points**:

| design point | cells | D | level |
|---|---|---|---|
| R18/SGDm/1e-4/100 ep | cc1, mm1, pp1, gn1(BN), ml2, rl3@1e-4 | +0.5861 | 91.986 |
| CIFAR-100 | gc1, gm2 | +1.5623 | 70.440 |
| AdamW + Lion | aw1, sm3 | +0.2100 | 93.040 |
| SGD | nl1(SGD), bm2(SGD) | +1.0067 | 91.179 |
| RMSProp | nl1(RMSProp), bm2(RMSProp) | +0.8023 | 92.331 |
| rl3@3e-4 | rl3@3e-4 | +0.5913 | 92.507 |
| fa1 | fa1 | +0.6293 | 92.327 |
| hz3 | hz3 | +0.4277 | 92.816 |
| g3m | g3m | +0.6658 | 91.336 |
| r50 | r50 | +0.8813 | 89.631 |
| sm4 (only RMSProp meta) | sm4 | +0.8893 | 90.785 |

**This matters, and the alternative is a trap.** Treating each of the four new cells as its own
fold gives 14 design points and turns the sign test into 12/14, `p = 0.013` — apparently
significant. It is leakage: a fold holding out `bm2`(SGD) while `nl1`(SGD) sits in the training
set is not out of sample. Four new *cells* bought one new *design point*, and the honest table
says so.

### paper.tex — §5.8, lines 2799–2828 (block replacement)

REPLACE
```
The sixteen $\Dstat$ cells of Table~\ref{tab:D} collapse to \textbf{10 distinct design points}
(the six identical ResNet-18/SGDm/$\eta = 10^{-4}$/100-epoch batches are one point; the two
CIFAR-100 batches are one). Leave-one-design-point-out, refitting each single-predictor model on
the held-in 9:

\begin{center}
\small
\begin{tabular}{@{}lrl@{}}
\toprule
model & LOO RMSE & vs ``predict the corpus mean'' \\
\midrule
\textbf{mean (baseline)} & \textbf{0.3859} & --- \\
$\Dstat \propto k\cdot\log(\text{headroom})$ & 0.2693 & $-30\%$ \\
CIFAR-100 dummy & 0.3765 & $-2\%$ \\
$\Dstat \propto k\cdot\text{headroom}$ & 0.3796 & $-2\%$ \\
$\Dstat \propto \text{level}$ (OLS) & 0.8379 & \textbf{$+117\%$ WORSE} \\
\bottomrule
\end{tabular}
\end{center}

\textbf{None of this is a result, and here is why.} The margin is dominated by the single
CIFAR-100 fold: the mean errs by $-0.888$ there and $k\cdot\log(\text{headroom})$ by $-0.457$, and
restricted to the nine CIFAR-10 folds the best model wins by 0.040 RMSE
($0.2791 \rightarrow 0.2395$, $-14\%$; the level model, 0.2358, $-16\%$), with a sign test of 7/9,
two-sided $p = 0.180$. Over all ten folds the sign test is 8/10, $p = 0.109$. The functional form
is itself the winner of about ten candidates scored on the same points, so any apparent
improvement is a best-of-ten selection statistic before it is anything else. And the power bound
is decisive: \textbf{at 10 design points a predictor needs $|r| \ge 0.632$ --- it must explain
$\ge 40\%$ of the between-design-point variance --- to be visible at $p < 0.05$}; seeing
$|r| = 0.4$ would need $\approx 25$ design points, which is not reachable by brute force.
```
WITH
```
The twenty $\Dstat$ cells of Table~\ref{tab:D} collapse to \textbf{11 distinct design points}
under the rule that two cells are one design point when they run the same network, dataset,
base--meta pairing, $\eta$ and budget in different submissions: the six identical
ResNet-18/SGDm/$\eta = 10^{-4}$/100-epoch batches are one point; the two CIFAR-100 batches are
one; \arm{aw1} and \arm{sm3} are one; \arm{nl1}/SGD and \arm{bm2}/SGD are one;
\arm{nl1}/RMSProp and \arm{bm2}/RMSProp are one; \arm{sm4}, the corpus's only RMSProp meta, is its
own. \textbf{Collapsing replicate batches is not cosmetic, and the alternative is a trap we
report rather than take}: a fold that holds out \arm{bm2}/SGD while \arm{nl1}/SGD remains in the
training set is not out of sample, and scoring the four new cells as four new folds would turn the
sign test below from 9/11 ($p = 0.065$) into 12/14 ($p = 0.013$) without a single new
configuration having been measured. Four new cells bought \textbf{one} new design point.
Leave-one-design-point-out, refitting each single-predictor model on the held-in 10:

\begin{center}
\small
\begin{tabular}{@{}lrl@{}}
\toprule
model & LOO RMSE & vs ``predict the corpus mean'' \\
\midrule
\textbf{mean (baseline)} & \textbf{0.3685} & --- \\
$\Dstat \propto k\cdot\log(\text{headroom})$ & 0.2548 & $-31\%$ \\
CIFAR-100 dummy & 0.3601 & $-2\%$ \\
$\Dstat \propto k\cdot\text{headroom}$ & 0.3467 & $-6\%$ \\
$\Dstat \propto \text{level}$ (OLS) & 0.8678 & \textbf{$+135\%$ WORSE} \\
\bottomrule
\end{tabular}
\end{center}

\textbf{None of this is a result, and here is why.} The margin is still dominated by the single
CIFAR-100 fold: the mean errs by $-0.893$ there and $k\cdot\log(\text{headroom})$ by $-0.470$, and
restricted to the ten CIFAR-10 folds the best model wins by 0.042 RMSE
($0.2637 \rightarrow 0.2222$, $-16\%$; the level model, 0.2163, $-18\%$), with a sign test of
8/10, two-sided $p = 0.109$. Over all eleven folds the sign test is 9/11, $p = 0.065$. \textbf{The
verdict is unchanged from the sixteen-cell table this replaces}: nothing crosses a threshold, and
the pattern --- one CIFAR-100 fold carrying the margin, a headroom model that leads inside
CIFAR-10 without reaching significance --- is the same to within a percentage point of RMSE. The
functional form is itself the winner of about ten candidates scored on the same points, so any
apparent improvement is a best-of-ten selection statistic before it is anything else. And the
power bound is still decisive: \textbf{at 11 design points a predictor needs $|r| \ge 0.602$ ---
it must explain $\ge 36\%$ of the between-design-point variance --- to be visible at
$p < 0.05$}; seeing $|r| = 0.4$ would need $\approx 25$ design points, which is not reachable by
brute force.
```

### paper.tex — §5.8, the level-model sentence (lines 2830–2832)

REPLACE
```
The level model earns its own sentence. Fitted on the nine CIFAR-10 points it predicts
$\Dstat(\text{CIFAR-100}) = \mathbf{+4.11}$ against $\mathbf{+1.56}$ observed, an error of
$+2.55$ pp --- nearly three times the error of simply predicting the corpus mean.
```
WITH
```
The level model earns its own sentence. Fitted on the ten CIFAR-10 points it predicts
$\Dstat(\text{CIFAR-100}) = \mathbf{+4.36}$ against $\mathbf{+1.56}$ observed, an error of
$+2.80$ pp --- more than three times the error of simply predicting the corpus mean.
```

### paper.tex — §5.9's draft sentence (line 2853)

REPLACE
```
than the corpus mean by a margin this design, at 10 design points, can resolve.}
```
WITH
```
than the corpus mean by a margin this design, at 11 design points, can resolve.}
```

### paper.tex — §1.1 power-bound aside (line 211)

REPLACE
```
($|r| \ge 0.632$ needed at 10 design points). A cross-validated \emph{null} at $n = 10$ is
defensible in a way a cross-validated success at $n = 10$ never is; we report both, and the null
```
WITH
```
($|r| \ge 0.602$ needed at 11 design points). A cross-validated \emph{null} at $n = 11$ is
defensible in a way a cross-validated success at $n = 11$ never is; we report both, and the null
```

### paper.tex — Appendix A.5 (lines 3823–3833, block replacement)

REPLACE
```
\arm{gn1}-GroupNorm removal the design-point set is 10, the best model wins inside CIFAR-10 by 0.040
RMSE ($0.2791 \rightarrow 0.2395$, $-14\%$) and the sign tests are 8/10 ($p\ 0.109$) overall and 7/9
($p\ 0.180$) inside CIFAR-10. The verdict is unchanged --- nothing reaches significance, the margin
is dominated by one CIFAR-100 fold, the functional form is a best-of-ten selection, and the power
bound $|r| \ge 0.632$ is not approached --- but the null now holds by a narrower margin than the
record implied, and we report the margin that re-derives rather than the record's phrasing.
```
WITH
```
\arm{gn1}-GroupNorm removal the design-point set was 10, the best model won inside CIFAR-10 by
0.040 RMSE ($0.2791 \rightarrow 0.2395$, $-14\%$) and the sign tests were 8/10 ($p\ 0.109$) overall
and 7/9 ($p\ 0.180$) inside CIFAR-10. With \arm{bm2}, \arm{sm3} and \arm{sm4} ingested the set is
\textbf{11} --- those four cells add one design point, not four, because three of them replicate a
configuration already present --- and the readings are 0.042 RMSE
($0.2637 \rightarrow 0.2222$, $-16\%$) with sign tests 9/11 ($p\ 0.065$) overall and 8/10
($p\ 0.109$) inside CIFAR-10. The verdict is unchanged at every step --- nothing reaches
significance, the margin is dominated by one CIFAR-100 fold, the functional form is a best-of-ten
selection, and the power bound, now $|r| \ge 0.602$, is not approached --- but the null holds by a
narrower margin than the record implied, and we report the margin that re-derives rather than the
record's phrasing.
```

### DRAFT-v4.md — §5.8, lines 2170–2196 (block replacement)

REPLACE
```
The sixteen D cells of Table 2 collapse to **10 distinct design points** (the six identical
ResNet-18/SGDm/η=1e-4/100-epoch batches are one point; the two CIFAR-100 batches are one).
Leave-one-design-point-out, refitting each single-predictor model on the held-in 9:

| model | LOO RMSE | vs "predict the corpus mean" |
|---|---|---|
| **mean (baseline)** | **0.3859** | — |
| D ∝ k·log(headroom) | 0.2693 | −30% |
| CIFAR-100 dummy | 0.3765 | −2% |
| D ∝ k·headroom | 0.3796 | −2% |
| D ∝ level (OLS) | 0.8379 | **+117% WORSE** |

**None of this is a result, and here is why.** The margin is dominated by the single CIFAR-100
fold: the mean errs by −0.888 there and `k·log(headroom)` by −0.457, and restricted to the nine
CIFAR-10 folds the best model wins by 0.040 RMSE (0.2791 → 0.2395, −14%; the level model,
0.2358, −16%), with a sign test of 7/9, two-sided p = 0.180. Over all ten folds the sign test is
8/10, p = 0.109. The functional form is itself the winner of about ten candidates scored on
the same points, so any apparent improvement is a best-of-ten selection statistic before it is
anything else. And the power bound is decisive: **at 10 design points a predictor needs |r| ≥
0.632 — it must explain ≥ 40% of the between-design-point variance — to be visible at p < 0.05**;
seeing |r| = 0.4 would need ≈ 25 design points, which is not reachable by brute force.

The level model earns its own sentence. Fitted on the nine CIFAR-10 points it predicts
D(CIFAR-100) = **+4.11 against +1.56 observed**, an error of +2.55 pp — nearly three times the
error of simply predicting the corpus mean.
```
WITH
```
The twenty D cells of Table 2 collapse to **11 distinct design points** under the rule that two
cells are one design point when they run the same network, dataset, base–meta pairing, η and
budget in different submissions: the six identical ResNet-18/SGDm/η=1e-4/100-epoch batches are one
point; the two CIFAR-100 batches are one; `aw1` and `sm3` are one; `nl1`/SGD and `bm2`/SGD are one;
`nl1`/RMSProp and `bm2`/RMSProp are one; `sm4`, the corpus's only RMSProp meta, is its own.
**Collapsing replicate batches is not cosmetic, and the alternative is a trap we report rather than
take**: a fold that holds out `bm2`/SGD while `nl1`/SGD remains in the training set is not out of
sample, and scoring the four new cells as four new folds would turn the sign test below from 9/11
(p = 0.065) into 12/14 (p = 0.013) without a single new configuration having been measured. Four
new cells bought **one** new design point. Leave-one-design-point-out, refitting each
single-predictor model on the held-in 10:

| model | LOO RMSE | vs "predict the corpus mean" |
|---|---|---|
| **mean (baseline)** | **0.3685** | — |
| D ∝ k·log(headroom) | 0.2548 | −31% |
| CIFAR-100 dummy | 0.3601 | −2% |
| D ∝ k·headroom | 0.3467 | −6% |
| D ∝ level (OLS) | 0.8678 | **+135% WORSE** |

**None of this is a result, and here is why.** The margin is still dominated by the single
CIFAR-100 fold: the mean errs by −0.893 there and `k·log(headroom)` by −0.470, and restricted to
the ten CIFAR-10 folds the best model wins by 0.042 RMSE (0.2637 → 0.2222, −16%; the level model,
0.2163, −18%), with a sign test of 8/10, two-sided p = 0.109. Over all eleven folds the sign test
is 9/11, p = 0.065. **The verdict is unchanged from the sixteen-cell table this replaces**:
nothing crosses a threshold, and the pattern — one CIFAR-100 fold carrying the margin, a headroom
model that leads inside CIFAR-10 without reaching significance — is the same to within a
percentage point of RMSE. The functional form is itself the winner of about ten candidates scored
on the same points, so any apparent improvement is a best-of-ten selection statistic before it is
anything else. And the power bound is still decisive: **at 11 design points a predictor needs
|r| ≥ 0.602 — it must explain ≥ 36% of the between-design-point variance — to be visible at
p < 0.05**; seeing |r| = 0.4 would need ≈ 25 design points, which is not reachable by brute force.

The level model earns its own sentence. Fitted on the ten CIFAR-10 points it predicts
D(CIFAR-100) = **+4.36 against +1.56 observed**, an error of +2.80 pp — more than three times the
error of simply predicting the corpus mean.
```

### DRAFT-v4.md — §5.9 draft sentence (lines 2211–2212)

REPLACE
```
> predicts D out of sample better than the corpus mean by a margin this design, at 10 design
> points, can resolve.*
```
WITH
```
> predicts D out of sample better than the corpus mean by a margin this design, at 11 design
> points, can resolve.*
```

### DRAFT-v4.md — §1.1 power-bound aside (lines 133–135)

REPLACE
```
power bound (|r| ≥ 0.632 needed at 10 design points). A cross-validated *null* at n = 10 is
defensible in a way a cross-validated success at n = 10 never is; we report both, and the null is
```
WITH
```
power bound (|r| ≥ 0.602 needed at 11 design points). A cross-validated *null* at n = 11 is
defensible in a way a cross-validated success at n = 11 never is; we report both, and the null is
```

### DRAFT-v4.md — A.5 (lines 3036–3043)

REPLACE
```
design-point set is 10, the best model wins inside CIFAR-10 by 0.040 RMSE (0.2791 → 0.2395, −14%)
and the sign tests are 8/10 (p 0.109) overall and 7/9 (p 0.180) inside CIFAR-10. The verdict is
unchanged — nothing reaches significance, the margin is dominated by one CIFAR-100 fold, the
functional form is a best-of-ten selection, and the power bound |r| ≥ 0.632 is not approached — but
the null now holds by a narrower margin than the record implied, and we report the margin that
re-derives rather than the record's phrasing.
```
WITH
```
design-point set was 10, the best model won inside CIFAR-10 by 0.040 RMSE (0.2791 → 0.2395, −14%)
and the sign tests were 8/10 (p 0.109) overall and 7/9 (p 0.180) inside CIFAR-10. With `bm2`,
`sm3` and `sm4` ingested the set is **11** — those four cells add one design point, not four,
because three of them replicate a configuration already present — and the readings are 0.042 RMSE
(0.2637 → 0.2222, −16%) with sign tests 9/11 (p 0.065) overall and 8/10 (p 0.109) inside CIFAR-10.
The verdict is unchanged at every step — nothing reaches significance, the margin is dominated by
one CIFAR-100 fold, the functional form is a best-of-ten selection, and the power bound, now
|r| ≥ 0.602, is not approached — but the null holds by a narrower margin than the record implied,
and we report the margin that re-derives rather than the record's phrasing.
```

---

## S4d — §5.6 shares the design-point set and must move with §5.8

**Not on the S1–S7 list, but S4c forces it**: §5.6 opens "Over all 10 design points" and the whole
subsection is computed on the superseded sixteen-cell set. Leaving it would replace one
contradiction with another, so it is recomputed here. **Two of its four bullets change verdict.**
This is the only place in the package where a scientific reading moves, and it moves *against* the
paper's framing, so it is flagged rather than buried.

### Re-derived, sixteen cells → twenty cells

| quantity | 16 cells / 10 pts (published) | 20 cells / 11 pts (new) |
|---|---|---|
| slope over all points | −0.044 ± 0.011, t −4.06, r −0.821 | **−0.045 ± 0.010, t −4.52, r −0.833** |
| CIFAR-10 levels span | 89.63–92.98 (9 pts) | **89.63–93.04 (10 pts)** |
| slope inside CIFAR-10 | −0.161 ± 0.067, t −2.38, r −0.669 | **−0.173 ± 0.051, t −3.37, r −0.766** |
| exact permutation p | 0.0454 over 9! = 362,880 | **0.0097 over 10! = 3,628,800** |
| critical \|r\| | 0.666 at 9 pts | **0.632 at 10 pts** |
| base fixed at SGDm | −0.119 ± 0.022 (6 pts) | −0.119 ± 0.022 (6 pts, unchanged) |
| network fixed at R18 | −0.386 ± 0.105 (7 pts) | **−0.282 ± 0.068 (8 pts)** |
| both fixed | −0.187 ± 0.125, t −1.49, p 0.333 | −0.187 ± 0.125, t −1.49, p 0.333 (unchanged) |
| independent instrument | −0.167 ± 0.101, t −1.65 | **−0.204 ± 0.082, t −2.49** |
| with the GroupNorm point back in | −0.021 ± 0.077, t −0.27 | **−0.044 ± 0.070, t −0.63** |

All ten published values reproduce to the printed precision, which is what licenses the new
column. **What changes:** the within-CIFAR-10 association is no longer on its critical value
(|r| 0.766 against a critical 0.632, permutation p 0.0097), and the independent instrument now
clears |t| ≥ 2. **What does not change, and is still the whole argument:** holding both the
network and the base fixed leaves −0.187 ± 0.125, t −1.49, exact permutation p = 0.333 —
unresolved, on the same four points as before. The confound story survives; the "coin landing on
its edge" framing does not, because merging replicate batches into their design points reduces
measurement error in *both* columns and de-attenuates the slope.

**One number is deleted rather than updated.** The published mechanical slope cites "the mean
sampling variance of a `nodewise` arm mean, 0.01808". That value does **not** re-derive under
either reading: averaging var/n over the CIFAR-10 cells of the sixteen-cell set gives 0.01693,
over all sixteen gives 0.01926. It is replaced with values that do re-derive.

### paper.tex — §5.6, lines 2696–2721 (block replacement)

REPLACE
```
Over all 10 design points, regressing $\Dstat$ on the aligned arm's \plateau{} gives slope
$\mathbf{-0.044 \pm 0.011}$, $t\ -4.06$, $r\ -0.821$ --- which looks like a law and is not one,
because level and dataset are the same column: the single CIFAR-100 design point sits at level
70.44 and the nine CIFAR-10 design points at 89.63--92.98.

Inside CIFAR-10 the slope is $\mathbf{-0.161 \pm 0.067}$, $t\ -2.38$, $r\ -0.669$ over 9 design
points (exact permutation over all $9! = 362{,}880$ orderings, $p = 0.0454$). We report that it is
nominally resolved, and then report the four things that stop it being a mechanism.

\begin{itemize}
\item \textbf{It is at the resolution floor by construction.} At 9 design points the two-sided
  5\% critical correlation is $|r| = 0.666$. The realised $|r|$ is 0.669. A result that clears its
  own critical value in the third decimal place is a coin landing on its edge, not a law.
\item \textbf{It is aliased with the network and with the base optimiser, and the alias is the
  whole effect.} The two lowest-level CIFAR-10 design points are \arm{r50} (a different network)
  and \arm{nl1}/SGD (a different base optimiser). Holding the base fixed at SGDm (6 points,
  spanning ResNet-18/34/50) gives $\mathbf{-0.119 \pm 0.022}$; holding the network fixed at
  ResNet-18 (7 points, spanning four bases) gives $\mathbf{-0.386 \pm 0.105}$; holding
  \textbf{both} fixed --- the only four points where ``level'' varies with nothing else structural
  --- gives $\mathbf{-0.187 \pm 0.125}$, $t\ -1.49$, exact permutation $p = 0.333$,
  \textbf{unresolved}. A slope whose magnitude moves by $3.2\times$ depending on which confound
  you hold, and which vanishes when you hold both, is measuring the confounds.
\item \textbf{An instrument that does not share an arm with $\Dstat$ does not resolve it.}
  $\Dstat$ and level share the \arm{nodewise} arm. The mechanical slope this induces is $-0.017$
  (the mean sampling variance of a \arm{nodewise} arm mean, 0.01808, over the variance of level
  across the nine points, 1.07971), one tenth of $-0.161$, so the artefact is not the explanation.
  But replacing level by an independent instrument --- the mean of the \arm{chunk2325} and
  \arm{nodewise1d} arms, neither of which enters $\Dstat$ --- gives $\mathbf{-0.167 \pm 0.101}$,
  $t\ -1.65$ within CIFAR-10 and does not clear the bar.
```
WITH
```
Over all 11 design points (\S\ref{sec:prediction} states the grouping rule), regressing $\Dstat$
on the aligned arm's \plateau{} gives slope $\mathbf{-0.045 \pm 0.010}$, $t\ -4.52$, $r\ -0.833$
--- which looks like a law and is not one, because level and dataset are the same column: the
single CIFAR-100 design point sits at level 70.44 and the ten CIFAR-10 design points at
89.63--93.04.

Inside CIFAR-10 the slope is $\mathbf{-0.173 \pm 0.051}$, $t\ -3.37$, $r\ -0.766$ over 10 design
points (exact permutation over all $10! = 3{,}628{,}800$ orderings, $p = 0.0097$). \textbf{This is
a strengthening we did not want and report anyway}: on the sixteen-cell set the same regression
read $-0.161 \pm 0.067$, $r\ 0.669$ against a critical 0.666, and the previous draft called it a
coin landing on its edge. Ingesting \arm{bm2}, \arm{sm3} and \arm{sm4} merges three pairs of cells
into their design points, which reduces measurement error in \emph{both} columns and de-attenuates
the slope. So the association is now resolved, and the three things that stop it being a mechanism
are the ones that matter.

\begin{itemize}
\item \textbf{It is aliased with the network and with the base optimiser, and the alias is the
  whole effect.} The two lowest-level CIFAR-10 design points are \arm{r50} (a different network)
  and \arm{sm4} (a different meta-optimiser), with \arm{nl1}/\arm{bm2}/SGD next. Holding the base
  fixed at SGDm (6 points, spanning ResNet-18/34/50) gives $\mathbf{-0.119 \pm 0.022}$; holding
  the network fixed at ResNet-18 (8 points, spanning five base--meta pairings) gives
  $\mathbf{-0.282 \pm 0.068}$; holding \textbf{both} fixed --- the only four points where
  ``level'' varies with nothing else structural --- gives $\mathbf{-0.187 \pm 0.125}$,
  $t\ -1.49$, exact permutation $p = 0.333$, \textbf{unresolved, and unmoved by the ingest}. A
  slope whose magnitude moves by $2.4\times$ depending on which confound you hold, and which
  does not resolve when you hold both, is measuring the confounds.
\item \textbf{An instrument that does not share an arm with $\Dstat$ does not settle it either.}
  $\Dstat$ and level share the \arm{nodewise} arm. The mechanical slope this induces is
  $\mathbf{-0.016}$ --- the mean sampling variance of a \arm{nodewise} arm mean over the 18
  CIFAR-10 cells, 0.01724, over the variance of level across the ten design points, 1.11080 ---
  under a tenth of $-0.173$, so the artefact is not the explanation. (An earlier draft printed
  0.01808 for the first of those two inputs; that value does not re-derive under either a
  cell-level or a point-level average and is replaced rather than restated.) Replacing level by an
  independent instrument --- the mean of the \arm{chunk2325} and \arm{nodewise1d} arms, neither of
  which enters $\Dstat$ --- gives $\mathbf{-0.204 \pm 0.082}$, $t\ -2.49$ within CIFAR-10, which
  now clears $|t| \ge 2$ where the sixteen-cell reading ($-0.167 \pm 0.101$, $t\ -1.65$) did not.
  The association is therefore not an arm-sharing artefact; it is still not separable from the
  network and the base.
```

*(the fourth bullet — `rl3`'s within-batch contrast — and everything after it are unchanged; note
the list is now three bullets, so the lead-in sentence's "four things" is replaced above.)*

### paper.tex — §5.6, the GroupNorm counterfactual (lines 2743–2745)

REPLACE
```
low-level point that flattened the within-CIFAR-10 slope, which without it moves from
$-0.021 \pm 0.077$ ($t\ -0.27$) to the $-0.161 \pm 0.067$ above.
```
WITH
```
low-level point that flattened the within-CIFAR-10 slope, which without it moves from
$-0.044 \pm 0.070$ ($t\ -0.63$) to the $-0.173 \pm 0.051$ above.
```

### paper.tex — §5.6, closing paragraph (lines 2748–2750)

REPLACE
```
at 9 CIFAR-10 design points and a critical $|r|$ of 0.666. We do not claim it is a carrier; we do
```
WITH
```
at 10 CIFAR-10 design points, where it is resolved ($|r|$ 0.766 against a critical 0.632) and
still collapses to $t\ -1.49$ the moment the network and the base are both held fixed. We do not
claim it is a carrier; we do
```

### DRAFT-v4.md — §5.6 (lines 2079–2104, block replacement)

REPLACE
```
Over all 10 design points, regressing D on the aligned arm's `plateau5` gives slope
**−0.044 ± 0.011, t −4.06, r −0.821** — which looks like a law and is not one, because level and
dataset are the same column: the single CIFAR-100 design point sits at level 70.44 and the nine
CIFAR-10 design points at 89.63–92.98.

Inside CIFAR-10 the slope is **−0.161 ± 0.067, t −2.38, r −0.669** over 9 design points (exact
permutation over all 9! = 362,880 orderings, p = 0.0454). We report that it is nominally resolved,
and then report the four things that stop it being a mechanism.

* **It is at the resolution floor by construction.** At 9 design points the two-sided 5% critical
  correlation is |r| = 0.666. The realised |r| is 0.669. A result that clears its own critical
  value in the third decimal place is a coin landing on its edge, not a law.
* **It is aliased with the network and with the base optimiser, and the alias is the whole
  effect.** The two lowest-level CIFAR-10 design points are `r50` (a different network) and
  `nl1`/SGD (a different base optimiser). Holding the base fixed at SGDm (6 points, spanning
  ResNet-18/34/50) gives **−0.119 ± 0.022**; holding the network fixed at ResNet-18 (7 points,
  spanning four bases) gives **−0.386 ± 0.105**; holding **both** fixed — the only four points
  where "level" varies with nothing else structural — gives **−0.187 ± 0.125, t −1.49, exact
  permutation p = 0.333, unresolved.** A slope whose magnitude moves by 3.2× depending on which
  confound you hold, and which vanishes when you hold both, is measuring the confounds.
* **An instrument that does not share an arm with D does not resolve it.** D and level share the
  `nodewise` arm. The mechanical slope this induces is −0.017 (the mean sampling variance of a
  `nodewise` arm mean, 0.01808, over the variance of level across the nine points, 1.07971), one
  tenth of −0.161, so the artefact is not the explanation. But replacing level by an independent
  instrument — the mean of the `chunk2325` and `nodewise1d` arms, neither of which enters D —
  gives **−0.167 ± 0.101, t −1.65** within CIFAR-10 and does not clear the bar.
```
WITH
```
Over all 11 design points (§5.8 states the grouping rule), regressing D on the aligned arm's
`plateau5` gives slope **−0.045 ± 0.010, t −4.52, r −0.833** — which looks like a law and is not
one, because level and dataset are the same column: the single CIFAR-100 design point sits at
level 70.44 and the ten CIFAR-10 design points at 89.63–93.04.

Inside CIFAR-10 the slope is **−0.173 ± 0.051, t −3.37, r −0.766** over 10 design points (exact
permutation over all 10! = 3,628,800 orderings, p = 0.0097). **This is a strengthening we did not
want and report anyway**: on the sixteen-cell set the same regression read −0.161 ± 0.067, r 0.669
against a critical 0.666, and the previous draft called it a coin landing on its edge. Ingesting
`bm2`, `sm3` and `sm4` merges three pairs of cells into their design points, which reduces
measurement error in *both* columns and de-attenuates the slope. So the association is now
resolved, and the three things that stop it being a mechanism are the ones that matter.

* **It is aliased with the network and with the base optimiser, and the alias is the whole
  effect.** The two lowest-level CIFAR-10 design points are `r50` (a different network) and `sm4`
  (a different meta-optimiser), with `nl1`/`bm2`/SGD next. Holding the base fixed at SGDm
  (6 points, spanning ResNet-18/34/50) gives **−0.119 ± 0.022**; holding the network fixed at
  ResNet-18 (8 points, spanning five base–meta pairings) gives **−0.282 ± 0.068**; holding
  **both** fixed — the only four points where "level" varies with nothing else structural — gives
  **−0.187 ± 0.125, t −1.49, exact permutation p = 0.333, unresolved, and unmoved by the ingest.**
  A slope whose magnitude moves by 2.4× depending on which confound you hold, and which does not
  resolve when you hold both, is measuring the confounds.
* **An instrument that does not share an arm with D does not settle it either.** D and level share
  the `nodewise` arm. The mechanical slope this induces is **−0.016** — the mean sampling variance
  of a `nodewise` arm mean over the 18 CIFAR-10 cells, 0.01724, over the variance of level across
  the ten design points, 1.11080 — under a tenth of −0.173, so the artefact is not the
  explanation. (An earlier draft printed 0.01808 for the first of those two inputs; that value
  does not re-derive under either a cell-level or a point-level average and is replaced rather
  than restated.) Replacing level by an independent instrument — the mean of the `chunk2325` and
  `nodewise1d` arms, neither of which enters D — gives **−0.204 ± 0.082, t −2.49** within
  CIFAR-10, which now clears |t| ≥ 2 where the sixteen-cell reading (−0.167 ± 0.101, t −1.65) did
  not. The association is therefore not an arm-sharing artefact; it is still not separable from
  the network and the base.
```

### DRAFT-v4.md — §5.6 GroupNorm counterfactual (lines 2124–2125)

REPLACE
```
which without it moves from −0.021 ± 0.077 (t −0.27) to the −0.161 ± 0.067 above.
```
WITH
```
which without it moves from −0.044 ± 0.070 (t −0.63) to the −0.173 ± 0.051 above.
```

### DRAFT-v4.md — §5.6 closing (lines 2127–2128)

REPLACE
```
of the aligned arm is not separable from the network and the base optimiser in this corpus, at 9
CIFAR-10 design points and a critical |r| of 0.666. We do not claim it is a carrier; we do not
```
WITH
```
of the aligned arm is not separable from the network and the base optimiser in this corpus, at 10
CIFAR-10 design points, where it is resolved (|r| 0.766 against a critical 0.632) and still
collapses to t −1.49 the moment the network and the base are both held fixed. We do not claim it
is a carrier; we do not
```

**Fallback if the orchestrator declines S4d.** Then §5.6's numbers must be explicitly scoped
rather than silently left: change `Over all 10 design points` to `Over the 10 design points of the
sixteen-cell set superseded in \S\ref{sec:prediction}` in both files. That is a factual
correction, not a hedge, but it leaves §5.6 measuring a set the paper no longer uses, so S4d is
the better close.

---

## S5 — the withdrawn F(62,85) = 5.47 is still load-bearing in two places

**Checked: it does not reproduce, and it must go.** §6.3 already withdraws it ("no cell definition
we could construct reproduced the record's F(62,85) = 5.47") and Appendix A.3 records the
non-reproduction. Independently, four reductions built for this package span three orders of
magnitude around it — the paper's own reduction gives F(39,172) = 0.71; restricting to full-budget
runs at plateau5 ≥ 85 with n ≥ 3 per batch gives F ≈ 28 at the same within-arm sd of 0.193 pp that
A.3 quotes; leaving the short-budget probes in gives F ≈ 418. A statistic whose value depends that
strongly on the cell definition cannot carry an argument, whatever its value. Both load-bearing
uses are removed and replaced with what §6.3 actually measures.

### paper.tex — §4.4, lines 1477–1481

REPLACE
```
\paragraph{The rival label, measured.}
The variable most likely to induce this grouping by accident is batch identity, which this
paper's own methods section makes a large random effect ($F(62,85) = 5.47$,
$p\ 6.9\times10^{-13}$). Partitioning the fourteen cells by submission gives eleven levels,
```
WITH
```
\paragraph{The rival label, measured.}
The variable most likely to induce this grouping by accident is batch identity, because the two
partitions very nearly coincide: the fourteen cells fall into eleven submissions, so a four-way
split on the base optimiser is close to a split on which submission a cell came from. (An earlier
version of this paragraph motivated the test instead with a batch random effect of
$F(62,85) = 5.47$ carried from the project record. That statistic is \textbf{withdrawn} --- it
does not re-derive under any cell definition we could build; see \S\ref{sec:variance} and
Appendix~\ref{app:discrepancy}.3 --- and the test below never depended on it. The rival is worth
testing because of how the design is confounded, not because of a variance estimate.)
Partitioning the fourteen cells by submission gives eleven levels,
```

### paper.tex — §5.5, lines 2544–2547

REPLACE
```
\textbf{cross-batch} comparisons and carry the batch floor this paper measures elsewhere
($F(62,85) = 5.47$, $p\ 6.9\times10^{-13}$), which neither pairing nor Welch removes; they are
```
WITH
```
\textbf{cross-batch} comparisons and carry the cross-batch offset this paper measures elsewhere
--- bounded at about 0.32 pp at matched science and not separable from within-arm noise
(\S\ref{sec:variance}); the $F(62,85) = 5.47$ this sentence used to cite is withdrawn and does not
re-derive (Appendix~\ref{app:discrepancy}.3) --- which neither pairing nor Welch removes; they are
```

### DRAFT-v4.md — §4.4, lines 1117–1119

REPLACE
```
**The rival label, measured.** The variable most likely to induce this grouping by accident is
batch identity, which this paper's own methods section makes a large random effect
(F(62,85) = 5.47, p 6.9e-13). Partitioning the fourteen cells by submission gives eleven levels,
```
WITH
```
**The rival label, measured.** The variable most likely to induce this grouping by accident is
batch identity, because the two partitions very nearly coincide: the fourteen cells fall into
eleven submissions, so a four-way split on the base optimiser is close to a split on which
submission a cell came from. (An earlier version of this paragraph motivated the test instead with
a batch random effect of F(62,85) = 5.47 carried from the project record. That statistic is
**withdrawn** — it does not re-derive under any cell definition we could build; see §6.3 and
Appendix A.3 — and the test below never depended on it. The rival is worth testing because of how
the design is confounded, not because of a variance estimate.) Partitioning the fourteen cells by
submission gives eleven levels,
```

### DRAFT-v4.md — §5.5, lines 1961–1963

REPLACE
```
elsewhere (F(62,85) = 5.47, p 6.9e-13), which neither pairing nor Welch removes; they are labelled
```
WITH
```
elsewhere — bounded at about 0.32 pp at matched science and not separable from within-arm noise
(§6.3); the F(62,85) = 5.47 this sentence used to cite is withdrawn and does not re-derive
(Appendix A.3) — which neither pairing nor Welch removes; they are labelled
```
### DRAFT-v4.md — §5.5, the preceding line

REPLACE
```
table above are **cross-batch** comparisons and carry the batch floor this paper measures
```
WITH
```
table above are **cross-batch** comparisons and carry the cross-batch offset this paper measures
```

---

## S6 — the fifteen orphan labels

Audited mechanically (all `\label{}` minus all `\ref/\eqref/\autoref/\cref/\pageref` targets):
**72 labels, 57 referenced, 15 orphans** — `sec:contributions`, `sec:rw-metaoptimize`,
`sec:rw-zheng`, `sec:method`, `sec:partitions`, `sec:contrasts`, `eq:A`, `eq:U`, `tab:inflight`,
`tab:T`, `tab:mechanisms`, `tab:DG`, `tab:holm`, `fig:decomposition`, `tab:arms`. **Every one is
cross-referenced; none is deleted.** Four are already closed by edits above:

| label | closed by |
|---|---|
| `tab:inflight` | S1(b) |
| `eq:A` | S2 |
| `tab:arms` | S3 |

The remaining eleven follow. **This item is paper.tex-only** — DRAFT-v4.md has no label
machinery; where the fix adds real prose (the two roadmap sentences) the md counterpart is given.

**`eq:U` — §4.2 opening, line 1178**

REPLACE
```
Holding the partition family fixed (uniform chunks) inside \textbf{one} batch (\arm{ck1}),
```
WITH
```
The pure count axis $\Ustat$ of Eq.~\ref{eq:U} holds the partition family fixed (uniform chunks)
inside \textbf{one} batch (\arm{ck1}),
```

**`tab:T` — §4.7, line 1975**

REPLACE
```
$\Tstat = \arm{nodewise1d} - \arm{nodewise}$ (Eq.~\ref{eq:T}), within batch:
```
WITH
```
$\Tstat = \arm{nodewise1d} - \arm{nodewise}$ (Eq.~\ref{eq:T}), within batch, it reads as in
Table~\ref{tab:T}:
```

**`tab:mechanisms` — §5 opening, lines 2224–2226**

REPLACE
```
effect; ``refuted'' there means the general form is refuted, not that the tail is exonerated
(\S\ref{sec:size1}).
```
WITH
```
effect; ``refuted'' there means the general form is refuted, not that the tail is exonerated
(\S\ref{sec:size1}). Table~\ref{tab:mechanisms} indexes all nine candidates, the verdict on each,
and the subsection that decides it.
```

**`tab:DG` and `fig:decomposition` — §5.4 opening, lines 2353–2355**

REPLACE
```
$\Gstat$ is the same contrast with the tail already removed from both arms, count-matched
exactly.
```
WITH
```
$\Gstat$ is the same contrast with the tail already removed from both arms, count-matched
exactly. Table~\ref{tab:DG} gives the split cell by cell and Figure~\ref{fig:decomposition} plots
it, stacked in panel (a) and as the tail component alone in panel (b).
```

**`tab:holm` — §5.4, line 2412**

REPLACE
```
fourteen, so that the effect of enlarging the family is visible rather than absorbed.
```
WITH
```
fourteen, so that the effect of enlarging the family is visible rather than absorbed
(Table~\ref{tab:holm}).
```

**`sec:contributions` and `sec:method` — §1, line 238**

REPLACE
```
\S\ref{sec:related} states exactly what is left.
```
WITH
```
\S\ref{sec:related} states exactly what is left, \S\ref{sec:contributions} lists what this paper
adds, and \S\ref{sec:method} fixes the partitions, the contrasts and the metric before any result
is read.
```

**DRAFT-v4.md — line 154.** REPLACE
```
ladder and its interior optimum; §2 states exactly what is left.
```
WITH
```
ladder and its interior optimum; §2 states exactly what is left, §1.1 lists what this paper adds,
and §3 fixes the partitions, the contrasts and the metric before any result is read.
```

**`sec:rw-metaoptimize` and `sec:rw-zheng` — new §2 roadmap sentence, after line 293**

REPLACE
```
\section{Related work, and what is left}
\label{sec:related}

```
WITH
```
\section{Related work, and what is left}
\label{sec:related}

\S\ref{sec:rw-metaoptimize} fixes the parent method and the configuration this paper inherits from
it. \S\ref{sec:rw-choi}, \S\ref{sec:rw-zheng}, \S\ref{sec:rw-camhd} and \S\ref{sec:rw-tensor} then
place the four literatures this measurement sits inside, and state in each case what is already
pre-empted and what is not.

```

**DRAFT-v4.md — line 201.** REPLACE
```
## 2. Related work, and what is left
```
WITH
```
## 2. Related work, and what is left

§2.1 fixes the parent method and the configuration this paper inherits from it. §2.2, §2.3, §2.4
and §2.5 then place the four literatures this measurement sits inside, and state in each case what
is already pre-empted and what is not.
```

**`sec:partitions` and `sec:contrasts` — new §3 roadmap sentence, after line 484**

REPLACE
```
\section{Method and experimental setup}
\label{sec:method}

```
WITH
```
\section{Method and experimental setup}
\label{sec:method}

\S\ref{sec:partitions} constructs the partitions and their group counts, \S\ref{sec:contrasts}
defines the four differences that carry every claim in this paper, and \S\ref{sec:metric} fixes
the metric, the admissibility gate and the unit of replication --- all three before any result is
read.

```

**DRAFT-v4.md — line 329.** REPLACE
```
## 3. Method and experimental setup
```
WITH
```
## 3. Method and experimental setup

§3.1 constructs the partitions and their group counts, §3.2 defines the four differences that
carry every claim in this paper, and §3.3 fixes the metric, the admissibility gate and the unit of
replication — all three before any result is read.
```

---

## S7 — the abstract attributes all 2,173 runs to ResNet-18/34/50

**Verified against the CSV.** Network census over all 2,173 rows: ResNet18 1,667;
ResNet18_c100 188; ResNet34 141; **ResNet10 110**; ResNet50 31; ResNet18_gn 17;
**ResNet10_c100 9**; ResNet34_c100 9; **ResNet101 1**. The `_c100` and `_gn` strings are
ResNet-18/34 variants (CIFAR-100 head, GroupNorm), so the rows genuinely outside the
ResNet-18/34/50 family are **110 + 9 + 1 = 120**.

The twenty count-matched cells, by contrast, are exactly ResNet-18 ×18, ResNet-34 ×1,
ResNet-50 ×1 and CIFAR-10 ×18, CIFAR-100 ×2 (from `cells()`). So the network list is true of the
cells and false of the corpus, and the fix is to attach it to the cells. The replacement is
**two words shorter** than what it replaces, which matters because G4 has the abstract at 255
words against a (120, 230) band.

### paper.tex — abstract, lines 68–70

REPLACE
```
channel) for uniform chunks, over 2{,}173 runs on CIFAR-10 and CIFAR-100 with ResNet-18,
ResNet-34 and ResNet-50, every contrast taken within one submission, so batch effects cancel.
```
WITH
```
channel) for uniform chunks, in twenty count-matched contrasts on ResNet-18/34/50 drawn from
2{,}173 runs on CIFAR-10 and CIFAR-100, each contrast taken within one submission, so batch
effects cancel.
```

### DRAFT-v4.md — abstract, lines 15–16

REPLACE
```
channel) for uniform chunks, over 2,173 runs on CIFAR-10 and CIFAR-100 with ResNet-18,
ResNet-34 and ResNet-50, every contrast taken within one submission, so batch effects cancel.
```
WITH
```
channel) for uniform chunks, in twenty count-matched contrasts on ResNet-18/34/50 drawn from
2,173 runs on CIFAR-10 and CIFAR-100, each contrast taken within one submission, so batch
effects cancel.
```

### Optional, and recommended — put the census where a reader can check it

The corpus's non-ResNet-18/34/50 rows are documented nowhere. One sentence in §8's compute
paragraph closes that. **Offered, not required** (it adds a numeral the reproduce script does not
yet assert).

paper.tex — after `\paragraph{Compute.}`'s first sentence, ADD
```
By network the 2{,}173 rows are ResNet-18 and its CIFAR-100 and GroupNorm variants 1{,}872,
ResNet-34 and its CIFAR-100 variant 150, ResNet-50 31, ResNet-10 and its CIFAR-100 variant 119,
and one ResNet-101 --- the last 120 being exploratory probes that carry no count-matched contrast
and appear in no cell of Table~\ref{tab:D}.
```
(1,667 + 188 + 17 = 1,872; 141 + 9 = 150; 110 + 9 = 119; 1. Total 2,173. Re-derived.)

---

# Re-derivations

Every number this package changes, with the check that licenses it. Scripts live in the session
scratchpad and were run against `results/all_runs.csv` at HEAD, through
`analysis/c98_figures.py`'s own `load()`, `admissible()`, `arm()` (with `dup_group` collapsing),
`welch()` and `cells()`. **`plateau5` is the only accuracy column read.** No registered scorer was
edited; none was run.

## 1. Cell set

`cells()` returns **20** cells (GroupNorm excluded by default, `WITH_GN=True` adds it as a 21st).
Networks 18/1/1 across ResNet-18/34/50; datasets 18/2 across CIFAR-10/100; bases SGDm, SGD,
RMSProp, AdamW; metas Lion (19) and RMSProp (`sm4`, 1).

## 2. §5.8 LOO-RMSE — validation before extension

Models, fitted per fold on the held-in design points: `mean` (intercept only);
`k·log(headroom)` and `k·headroom` (single slope through the origin); `CIFAR-100 dummy` and
`level` (two-parameter OLS). `headroom = 100 − aligned arm mean`. Design-point covariates are the
mean over the cells in the point.

**Validation on the sixteen cells / 10 design points the paper prints:**

```
mean (baseline)          0.3859   (paper 0.3859)
D ~ k*log(headroom)      0.2693   (paper 0.2693)   -30%
CIFAR-100 dummy          0.3765   (paper 0.3765)   -2%
D ~ k*headroom           0.3796   (paper 0.3796)   -2%
D ~ level (OLS)          0.8379   (paper 0.8379)   +117%
CIFAR-10 folds: mean 0.2791 -> klog 0.2395 (-14%); level 0.2358 (-16%)   [paper: identical]
sign tests 8/10 all folds, 7/9 CIFAR-10                                  [paper: identical]
CIFAR-100 fold error: mean -0.888, klog -0.457                           [paper: identical]
```

Every published value reproduces to four decimals. **On the twenty cells / 11 design points:**

```
mean (baseline)          0.3685    ---
D ~ k*log(headroom)      0.2548    -31%
CIFAR-100 dummy          0.3601    -2%
D ~ k*headroom           0.3467    -6%
D ~ level (OLS)          0.8678    +135%
CIFAR-10 folds: mean 0.2637 -> klog 0.2222 (-16%); level 0.2163 (-18%)
sign tests 9/11 all folds (p 0.0654), 8/10 CIFAR-10 (p 0.1094)
CIFAR-100 fold error: mean -0.893, klog -0.470
level model fitted on the ten CIFAR-10 points predicts D(C100) +4.36 vs +1.56 observed
```

Sign-test p-values are exact two-sided binomial at p = 0.5:
9/11 → 2·(55+11+1)/2048 = 0.0654; 8/10 → 2·(45+10+1)/1024 = 0.1094; 12/14 → 2·106/16384 = 0.0129.
The 7/9 → 0.1797 and 8/10 → 0.1094 of the published text reproduce under the same convention.

**Grouping sensitivity, reported because the choice is load-bearing:** treating each new batch as
its own design point gives 14 points, LOO RMSE mean 0.3709 → klog 0.2777 (−25%), CIFAR-10 folds
0.2947 → 0.2583 (−12%), and sign tests 12/14 (p 0.013) and 11/13 (p 0.022). That reading is
rejected as leakage, not preferred, and the rejection is stated in the replacement text.

**Power bound.** Critical two-sided 5% Pearson r, from the exact Student-t quantile,
r = t/√(t²+df): n = 9 → 0.666; n = 10 → **0.632**; n = 11 → **0.602**; n = 14 → 0.532;
n = 25 → 0.396. The published 0.666 at 9 and 0.632 at 10 both reproduce, which validates the
machinery that produces 0.602 at 11. 0.602² = 0.362 → "≥ 36%". "|r| = 0.4 needs ≈ 25 design
points" is unchanged.

## 3. §5.6 level slope — validation before extension

Same design-point construction; OLS of D on level; permutation p is exact over all orderings of
the D column against a fixed level column.

```
16 cells / 10 pts   ALL       -0.044 +- 0.011  t -4.06  r -0.821    [paper: identical]
                    CIFAR-10  -0.161 +- 0.067  t -2.38  r -0.669  perm p 0.0454 over 9!
                                                                     [paper: identical]
                    base=SGDm (6 pts)  -0.119 +- 0.022               [paper: identical]
                    net=R18   (7 pts)  -0.386 +- 0.105               [paper: identical]
                    both fixed (4 pts) -0.187 +- 0.125 t -1.49 perm p 0.333
                                                                     [paper: identical]
                    independent instrument -0.167 +- 0.101 t -1.65   [paper: identical]
                    +GroupNorm point       -0.021 +- 0.077 t -0.27   [paper: identical]

20 cells / 11 pts   ALL       -0.045 +- 0.010  t -4.52  r -0.833
                    CIFAR-10  -0.173 +- 0.051  t -3.37  r -0.766  perm p 0.0097 over 10!
                    base=SGDm (6 pts)  -0.119 +- 0.022   (unchanged)
                    net=R18   (8 pts)  -0.282 +- 0.068
                    both fixed (4 pts) -0.187 +- 0.125 t -1.49 perm p 0.333  (unchanged)
                    independent instrument -0.204 +- 0.082 t -2.49
                    +GroupNorm point       -0.044 +- 0.070 t -0.63
```

Seven of seven published values reproduce exactly. The mechanical-slope numerator does not:
mean var/n of a `nodewise` arm mean is 0.01693 over the sixteen-cell CIFAR-10 cells and 0.01926
over all sixteen, against the printed 0.01808. On the twenty-cell set the corresponding values are
0.01724 (18 CIFAR-10 cells) and 0.01907 (all 20); var(level) over the ten CIFAR-10 design points is
1.11080. 0.01724 / 1.11080 = 0.0155 → −0.016.

## 4. Batch counts (S4a)

```
batches carrying a count-matched contrast      batches   runs   admissible
  14 Table-2 batches + ar1 + bn1  (published)     16      272      272
  17 Table-2 batches + ar1 + bn1 + rp1  (now)     20      332      332
```
Batch = run-name prefix before the first hyphen. Also re-derived and unchanged: 256
uniform-chunk / `nodewise1d` / `permnode` rows, 256 admissible, 238 outside `rp1`, 18 inside.

## 5. GroupNorm cell (S3)

`cells()` with `WITH_GN = True`: D **+0.2023**, se **0.1366**, t **1.48**, n 8 v 8,
aligned 89.330, uniform 89.532. Matches §4.4's printed `+0.202 ± 0.137`.

## 6. Network census (S7)

ResNet18 1,667 · ResNet18_c100 188 · ResNet34 141 · **ResNet10 110** · ResNet50 31 ·
ResNet18_gn 17 · **ResNet10_c100 9** · ResNet34_c100 9 · **ResNet101 1** = 2,173.
Outside the ResNet-18/34/50 family: **120**.

## 7. Label audit (S6)

72 labels, 57 referenced, 15 orphans, enumerated in the S6 section above.

---

# Things this package deliberately did NOT do

* **`tab:D`'s caption is stale and is left alone.** It reads "Every cell is a separate contiguous
  submission except the two `rl3` rungs and the two `nl1` bases, which share a batch, and `hz3`".
  Table 2 now also has **two `bm2` rows, which share a batch**. This is a real defect, adjacent to
  S4 but not on the S1–S7 list, and it is flagged rather than silently patched here because it may
  belong to whichever package owns Table 2.
* **The §6.3 / A.3 batch-effect reduction is not re-litigated.** A crude matched-science one-way
  ANOVA built for S5 reaches within-arm sd = 0.193 pp — exactly A.3's figure — yet a batch F of
  ~28, where A.3 reports F(39,172) = 0.71. My cell key is built from CSV columns and may conflate
  runs whose `ARGS:` lines differ (precisely the RULE-20 failure mode this paper documents), so I
  cannot say which reduction is right. **UNSURE, logged, not written into the paper.** It does not
  affect S5's disposition: 0.71, 28 and 418 across three reductions is itself the reason the
  statistic cannot be load-bearing.
* **Nothing was committed, and neither `paper.tex` nor `DRAFT-v4.md` was edited.**
