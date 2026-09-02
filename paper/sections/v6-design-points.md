# PACKAGE `design-points` — closes B6

**Finding.** §5.8 states a design-point rule and then prints an enumeration that does not obey it.
The rule collapses two cells into one design point when they run the same **network, dataset,
base–meta pairing, η and budget** in different submissions. Applied as written it yields **ten**
points, not the eleven every number in §5.6 and §5.8 is keyed to, because `rl3` at
η = 3×10⁻⁴ and `fa1` are identical on every element of that key and are nevertheless printed as
two points. The only thing that separates them is the step-size clip box (`-30:9.0` vs
`-25:-2.3026`) — a field the same enumeration **already collapses across** inside its own
six-batch point, and which §4.4 measures and rejects as a moderator.

**Disposition: option (ii). The rule is applied exactly as written. §5.8 is reprinted at ten
design points and §5.6 at nine CIFAR-10 points.** The alternative — naming the clip box in the
key, which gives **twelve** points, not eleven — is reported as a sensitivity and rejected, for
three reasons given below, the third of which is that it is the *only* reading anywhere in this
package under which a statistic in §5.8 crosses 0.05.

**No verdict flips under option (ii).** §5.8 stays a null (sign test 8/10, *p* 0.109; 7/9,
*p* 0.180); §5.6's association stays resolved inside CIFAR-10 (|r| 0.767 against a critical 0.666)
and still collapses when the network and the base are both held fixed (*t* −1.27). Two verdicts
*would* move under option (i), and that is reported rather than buried: the all-folds sign test
reaches 10/12, *p* 0.039, and §5.6's both-fixed leg reaches *t* −2.19 (exact permutation
*p* 0.100). See **§C** below.

Every number here was fitted from scratch against `results/all_runs.csv` through
`analysis/c98_figures.py`'s own `load()`, `admissible()`, `arm()` (with `dup_group` collapsing),
`welch()` and `cells()`. `plateau5` is the only accuracy column read. No published number was
adjusted; the machinery was first validated by reproducing the **eleven**-point table exactly
(§B.1) before being applied to ten and twelve. No registered scorer was edited or run.

---

## A. The evidence that `rl3`@3e-4 and `fa1` are one design point

### A.1 The key fields, from the CSV of record

All 24 `rl3-*-m3e4-*` rows and all 24 `fa1-*` rows agree on every field the rule names and on
several it does not:

| field | `rl3-*-m3e4-*` | `fa1-*` |
|---|---|---|
| `network` | ResNet18 | ResNet18 |
| `dataset` | CIFAR10 | CIFAR10 |
| `batch_size` | 100 | 100 |
| `base` | SGDm | SGDm |
| `meta` | Lion | Lion |
| `meta_stepsize` (η) | 3e-4 | 3e-4 |
| `alpha0` | 1e-3 | 1e-3 |
| `gamma` | 1 | 1 |
| `augment` | 1 | 1 |
| `epochs_requested` | 100 | 100 |
| `hier` / `lam` / `eta_ratio` | (none) / na / na | (none) / na / na |
| **`beta_clip`** | **-30:9.0** | **-25:-2.3026** |

`beta_clip` is the only difference.

### A.2 RULE 20 — the runs' own `ARGS:` lines, not the CSV

`runs_alice2/rl3-node-m3e4-s0-4782158.out` and `runs/fa1-node-s0-4737876.out`:

```
ARGS: --optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base 0.1
      --alg-meta Lion --momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0
      --dataset CIFAR10 --NN-name ResNet18 --batch-size 100 --max-time 999:00:00 --gamma 1
      --meta-stepsize 3e-4 --alpha0 1e-3 --num-epochs 100 --stepsize-groups nodewise --seed 0
      --save-directory ... --run-name ...
```

The two `ARGS:` lines are identical apart from `--save-directory` and `--run-name`. The same holds
for the `chunk777` arms (`rl3-ch7-m3e4-s0` vs `fa1-ch-s0`). The clip box does not appear on the
command line at all; it is carried on the `ENV:` line, where the two differ in exactly one token:

```
ENV: AUGMENT=1 BETA_CLIP=-30:9.0     HIER=none LAM=na ETA_RATIO=na ...   (rl3)
ENV: AUGMENT=1 BETA_CLIP=-25:-2.3026 HIER=none LAM=na ETA_RATIO=na ...   (fa1)
```

### A.3 The two cells agree, as measurements

| | D (pp) | se | n |
|---|---|---|---|
| `rl3` @ η 3×10⁻⁴ | +0.5913 | 0.0957 | 3 v 3 |
| `fa1` | +0.6293 | 0.1232 | 6 v 6 |
| **difference** | **+0.0380** | **0.1560** | **z +0.24** |

Aligned-arm means 92.507 and 92.327; uniform-chunk means 93.098 and 92.957. The two cells are the
same measurement made twice.

### A.4 The enumeration already collapses across the clip box

The six cells the published text calls "the six identical ResNet-18/SGDm/η = 10⁻⁴/100-epoch
batches" do **not** share a box. Five of them (`cc1`, `mm1`, `pp1`, `gn1`-BN, `ml2`) ran in
`-15:-2.3026`; the sixth (`rl3` @ η 10⁻⁴) ran in `-30:9.0`. So the enumeration that printed eleven
points collapses across two boxes in one place and refuses to in another. That is not a rule; it is
two rules.

### A.5 §4.4 removes the defence

§4.4 partitions the fourteen-cell Cochran Q by β-box and, over the eight SGDm cells that between
them span all three boxes, finds **between-box Q = 0.76 on 2 df, p = 0.68** — the number the
paper's own pooling across boxes rests on. A field the paper argues is not a moderator of D cannot
be a component of the key that decides which measurements of D are replicates of each other.

### A.6 GPU class is not an alternative key

`rl3`@3e-4's twelve runs are all A100; `fa1`'s twenty-four are 20 A100 + 4 L4. But hardware is
mixed **within** almost every batch in the corpus (`cc1` 10/2, `ml2` 19/5, `nl1` 20/3/1,
`g3m` 30/6, `hz3` 9/12/3 across RTX 2080 Ti / L4 / A100), so GPU class does not discriminate
batches and cannot be a design-point key. It is named here only so the reader knows it was checked.

---

## B. Re-derivation

### B.1 Validation first: the published eleven-point set reproduces exactly

Fitting from scratch under the published enumeration (six-batch point; `rl3`@3e-4; `fa1`; `hz3`;
`aw1`+`sm3`; `nl1`/SGD+`bm2`/SGD; `nl1`/RMSProp+`bm2`/RMSProp; `g3m`; `r50`; `gc1`+`gm2`; `sm4`):

```
mean (baseline)        0.3685   (paper 0.3685)
D ~ k*log(headroom)    0.2548   (paper 0.2548)   -31%
CIFAR-100 dummy        0.3601   (paper 0.3601)    -2%
D ~ k*headroom         0.3467   (paper 0.3467)    -6%
D ~ level (OLS)        0.8678   (paper 0.8678)  +135%
CIFAR-10 folds: 0.2637 -> 0.2222 (-16%); level 0.2163 (-18%)   [paper: identical]
sign tests 9/11 p 0.0654 ; 8/10 p 0.1094                       [paper: identical]
C100 fold errors: mean -0.8933, klog -0.4697                   [paper: -0.893, -0.470]
critical |r| n=11 0.6021 (r^2 0.3625) ; n=10 0.6319            [paper: 0.602, 0.632]
level model on 10 C10 points -> D(C100) +4.358 vs +1.562 obs   [paper: +4.36 vs +1.56]
slopes: all -0.045+-0.010 t -4.52 r -0.833 ; C10 -0.173+-0.051 t -3.37 r -0.766,
        exact perm p 0.0097 over 10! ; SGDm(6) -0.119+-0.022 ; R18(8) -0.282+-0.068 ;
        both(4) -0.187+-0.125 t -1.49 perm p 0.333 ; instrument -0.204+-0.082 t -2.49 ;
        mech 0.01724 / 1.11080 = 0.0155 -> -0.016               [paper: all identical]
```

Every published value reproduces. The machinery is therefore not adjusting the paper's numbers; it
is producing them.

### B.2 The ten design points (rule as written)

Design-point D, level and headroom are the unweighted mean over the cells in the point.
`headroom = 100 − aligned arm mean`. The instrument is the mean of the `chunk2325` and
`nodewise1d` arm means, averaged over the cells in the point that carry both arms.

| design point (cells) | D | level | headroom | dataset |
|---|---|---|---|---|
| `nl1`/SGD + `bm2`/SGD | +1.0067 | 91.179 | 8.821 | C10 |
| `sm4` | +0.8893 | 90.785 | 9.215 | C10 |
| `r50` | +0.8813 | 89.631 | 10.369 | C10 |
| `nl1`/RMSProp + `bm2`/RMSProp | +0.8023 | 92.331 | 7.669 | C10 |
| `g3m` | +0.6658 | 91.336 | 8.664 | C10 |
| **`rl3`@3e-4 + `fa1`** | **+0.6103** | **92.417** | **7.583** | C10 |
| `cc1`+`mm1`+`pp1`+`gn1`(BN)+`ml2`+`rl3`@1e-4 | +0.5861 | 91.986 | 8.014 | C10 |
| `hz3` | +0.4277 | 92.816 | 7.184 | C10 |
| `aw1` + `sm3` | +0.2100 | 93.040 | 6.960 | C10 |
| `gc1` + `gm2` | +1.5623 | 70.440 | 29.560 | C100 |

Nine CIFAR-10 points, one CIFAR-100 point. "Four new cells bought one new design point" still
holds: the sixteen-cell set gives **nine** points under this rule, the twenty-cell set gives ten,
and the new point is `sm4`.

### B.3 §5.8's LOO-RMSE table, refit

Leave-one-design-point-out, each model refitted on the held-in nine. `mean` is intercept-only;
`k·log(headroom)` and `k·headroom` are single slopes through the origin; `CIFAR-100 dummy` and
`level` are two-parameter OLS (in the fold that holds out the single CIFAR-100 point the dummy is
constant and the fit degenerates to the intercept, which is the correct minimum-norm behaviour).

```
model                    LOO RMSE (all 10)   vs mean      CIFAR-10 folds (9)   vs mean
mean (baseline)              0.3868            ---             0.2809            ---
D ~ k*log(headroom)          0.2667           -31%             0.2352           -16%
CIFAR-100 dummy              0.3775            -2%             0.2663            -5%
D ~ k*headroom               0.3654            -6%             0.2444           -13%
D ~ level (OLS)              0.9319          +141%             0.2309           -18%

CIFAR-100 fold error:  mean -0.8868 ; k*log(headroom) -0.4623
sign test, all 10 folds:  8/10, exact two-sided binomial p = 0.1094
sign test, 9 C10 folds :  7/9,  exact two-sided binomial p = 0.1797
CIFAR-10 margin        :  0.2809 - 0.2352 = 0.046 RMSE
critical |r| at n = 10 :  0.6319  (t* 2.3060 on 8 df) ; r^2 = 0.3993 -> 39.9%
critical |r| at n = 9  :  0.6664
|r| = 0.4 first visible at n = 25 (critical 0.3961; at n = 24 it is 0.4044)  [unchanged]
level model fitted on the 9 C10 points -> D(C100) +4.427 vs +1.562 observed, error +2.864
corpus mean over the 9 C10 points      -> +0.676, error -0.887   (2.864 / 0.887 = 3.23x)
```

### B.4 §5.6's slopes, refit

```
ALL 10 points          -0.045 +- 0.011  t -4.21  r -0.830
9 CIFAR-10 points      -0.176 +- 0.056  t -3.16  r -0.767   exact perm p 0.0151 over 9! = 362,880
  base fixed SGDm (5)  -0.126 +- 0.022  t -5.74  r -0.957
  net fixed R18   (7)  -0.287 +- 0.075  t -3.83  r -0.864
  both fixed      (3)  -0.188 +- 0.148  t -1.27  r -0.785   exact perm p 0.667 over 3! = 6
  ratio 0.287 / 0.126 = 2.3x
independent instrument (9 pts)  -0.208 +- 0.089  t -2.33  r -0.661
mechanical slope: 0.01724 (mean var of a nodewise arm mean over the 18 CIFAR-10 cells)
                / 1.19374 (var of level over the 9 CIFAR-10 points) = 0.01444 -> -0.014
                  which is 8.2% of -0.176
levels: 9 CIFAR-10 points span 89.63-93.04 ; the CIFAR-100 point is 70.44
lowest-level CIFAR-10 points: r50 89.63, sm4 90.79, nl1|bm2/SGD 91.18   [ordering unchanged]
```

Historical comparators, recomputed under the **same** rule so the comparison is like-for-like:

```
sixteen-cell set, rule as written (9 pts / 8 C10):  -0.162 +- 0.074  t -2.19  r -0.666
                                                   against a critical 0.707 at n=8: UNRESOLVED
  (the published text compared -0.161 +- 0.067, r 0.669 against a critical 0.666 at n=9,
   which is what the superseded ten-point grouping of the same sixteen cells gives)
sixteen-cell instrument, rule as written (8 pts):   -0.168 +- 0.112  t -1.50
GroupNorm point re-included, rule as written (10 C10 pts): -0.045 +- 0.076  t -0.59
  (published, 11 C10 pts: -0.044 +- 0.070, t -0.63)
```

The `rl3` within-batch consistency check is a cell-level quantity and is unaffected by the
grouping: level +0.599 pp (91.908 → 92.507), D −0.090 (+0.681 → +0.591), implied slope
−0.150 ± 0.331, *t* −0.45.

---

## C. The rejected alternative, and the one threshold it crosses

Naming `beta_clip` in the key gives **twelve** points, not eleven: it splits `rl3`@1e-4 away from
the five otherwise-identical batches it currently sits with, **and** keeps `rl3`@3e-4 and `fa1`
apart.

```
12 points:  mean 0.3514 ; k*log(headroom) 0.2437 (-31%) ; C100 dummy 0.3439 (-2%) ;
            k*headroom 0.3317 (-6%) ; level 0.8314 (+137%)
            CIFAR-10 folds (11): 0.2491 -> 0.2112 (-15%) ; level 0.2050 (-18%)
            sign tests: 10/12 p 0.0386  <-- CROSSES 0.05 ;  9/11 p 0.0654
            critical |r| n=12 0.5760
            §5.6 both-fixed leg at 5 points: -0.201 +- 0.092, t -2.19, exact perm p 0.100
```

Three reasons this reading is reported and not taken:

1. **§4.4 forbids it.** Box is measured there and is not a moderator (between-box *Q* 0.76 on 2 df,
   *p* 0.68 over the eight SGDm cells).
2. **It is the leakage §5.8 already rejects, in the opposite direction.** Splitting `rl3`@1e-4 out
   of the six-batch point creates a fold that is held out while five batches identical to it on
   every key field remain in the training set — the exact structure the paragraph rejects for
   `bm2`/SGD against `nl1`/SGD.
3. **It is the only reading in this package under which anything in §5.8 crosses 0.05,** and it
   also pushes §5.6's both-fixed leg to *t* −2.19, weakening the negative claim that section
   rests on. A grouping choice that manufactures two threshold crossings, when the choice itself
   is one the paper argues against, is a grouping choice to decline.

For completeness, the leakage variant §5.8 already names — scoring the four new cells as four new
folds — becomes **13** points under the rule as written, with a sign test of **11/13, p 0.022**
(it was 14 points and 12/14, p 0.013 under the eleven-point base).

**One instability worth printing, because a referee will find it.** Under the rule as written the
*superseded* sixteen-cell set reads 9 points with a sign test of **8/9, p 0.039**, and the live
twenty-cell set reads 10 points with **8/10, p 0.109**. The sign test crosses 0.05 in both
directions as a single fold is added or removed. That is not a result in either direction; it is
part of the null, and the corrected §5.8 says so.

---

# EXACT REPLACEMENT TEXT

All 28 anchors below were verified `count == 1` against the live files at HEAD 351d9a6.
**Apply the same change to both files.**

---

## paper/paper.tex

### T1 — §1, the power-bound parenthesis (line ~207)

REPLACE
```
($|r| \ge 0.602$ needed at 11 design points). A cross-validated \emph{null} at $n = 11$ is
defensible in a way a cross-validated success at $n = 11$ never is; we report both, and the null
is the one that survives.
```
WITH
```
($|r| \ge 0.632$ needed at 10 design points). A cross-validated \emph{null} at $n = 10$ is
defensible in a way a cross-validated success at $n = 10$ never is; we report both, and the null
is the one that survives.
```

### T2 — §5.6, opening paragraph (line ~2950)

REPLACE
```
Over all 11 design points (\S\ref{sec:prediction} states the grouping rule), regressing $\Dstat$
on the aligned arm's \plateau{} gives slope $\mathbf{-0.045 \pm 0.010}$, $t\ -4.52$, $r\ -0.833$
--- which looks like a law and is not one, because level and dataset are the same column: the
single CIFAR-100 design point sits at level 70.44 and the ten CIFAR-10 design points at
89.63--93.04.
```
WITH
```
Over all 10 design points (\S\ref{sec:prediction} states the grouping rule), regressing $\Dstat$
on the aligned arm's \plateau{} gives slope $\mathbf{-0.045 \pm 0.011}$, $t\ -4.21$, $r\ -0.830$
--- which looks like a law and is not one, because level and dataset are the same column: the
single CIFAR-100 design point sits at level 70.44 and the nine CIFAR-10 design points at
89.63--93.04.
```

### T3 — §5.6, second paragraph (line ~2956)

REPLACE
```
Inside CIFAR-10 the slope is $\mathbf{-0.173 \pm 0.051}$, $t\ -3.37$, $r\ -0.766$ over 10 design
points (exact permutation over all $10! = 3{,}628{,}800$ orderings, $p = 0.0097$). \textbf{This is
a strengthening we did not want and report anyway}: on the sixteen-cell set the same regression
read $-0.161 \pm 0.067$, $r\ 0.669$ against a critical 0.666, and the previous version of this paper called it a
coin landing on its edge.
```
WITH
```
Inside CIFAR-10 the slope is $\mathbf{-0.176 \pm 0.056}$, $t\ -3.16$, $r\ -0.767$ over 9 design
points (exact permutation over all $9! = 362{,}880$ orderings, $p = 0.0151$). \textbf{This is
a strengthening we did not want and report anyway}: on the sixteen-cell set, grouped by the same
rule, the same regression read $-0.162 \pm 0.074$, $r\ 0.666$ against a critical 0.707 at eight
points --- unresolved, and the previous version of this paper, which split two cells that this
rule joins and so read the sixteen cells at nine CIFAR-10 points, got $r\ 0.669$ against a
critical 0.666 and called it a coin landing on its edge.
```

### T4 — §5.6, first bullet (line ~2969)

REPLACE
```
  fixed at SGDm (6 points, spanning ResNet-18/34/50) gives $\mathbf{-0.119 \pm 0.022}$; holding
  the network fixed at ResNet-18 (8 points, spanning five base--meta pairings) gives
  $\mathbf{-0.282 \pm 0.068}$; holding \textbf{both} fixed --- the only four points where
  ``level'' varies with nothing else structural --- gives $\mathbf{-0.187 \pm 0.125}$,
  $t\ -1.49$, exact permutation $p = 0.333$, \textbf{unresolved, and unmoved by the ingest}. A
  slope whose magnitude moves by $2.4\times$ depending on which confound you hold, and which
  does not resolve when you hold both, is measuring the confounds.
```
WITH
```
  fixed at SGDm (5 points, spanning ResNet-18/34/50) gives $\mathbf{-0.126 \pm 0.022}$; holding
  the network fixed at ResNet-18 (7 points, spanning five base--meta pairings) gives
  $\mathbf{-0.287 \pm 0.075}$; holding \textbf{both} fixed --- the only three points where
  ``level'' varies with nothing else structural --- gives $\mathbf{-0.188 \pm 0.148}$,
  $t\ -1.27$, \textbf{unresolved}. At three points the exact permutation test carries no
  information: its smallest attainable two-sided $p$ is $2/3! = 0.333$ and the observed slope
  reaches only $p = 0.667$, so the $t$ is the only reading available. It is also the reading that
  matters. A slope whose magnitude moves by $2.3\times$ depending on which confound you hold, and
  which does not resolve when you hold both, is measuring the confounds.
```

### T5 — §5.6, second bullet, the mechanical slope (line ~2977)

REPLACE
```
  $\mathbf{-0.016}$ --- the mean sampling variance of a \arm{nodewise} arm mean over the 18
  CIFAR-10 cells, 0.01724, over the variance of level across the ten design points, 1.11080 ---
  under a tenth of $-0.173$, so the artefact is not the explanation.
```
WITH
```
  $\mathbf{-0.014}$ --- the mean sampling variance of a \arm{nodewise} arm mean over the 18
  CIFAR-10 cells, 0.01724, over the variance of level across the nine design points, 1.19374 ---
  under a tenth of $-0.176$, so the artefact is not the explanation.
```

### T6 — §5.6, second bullet, the instrument (line ~2983)

REPLACE
```
  independent instrument --- the mean of the \arm{chunk2325} and \arm{nodewise1d} arms, neither of
  which enters $\Dstat$ --- gives $\mathbf{-0.204 \pm 0.082}$, $t\ -2.49$ within CIFAR-10, which
  now clears $|t| \ge 2$ where the sixteen-cell reading ($-0.167 \pm 0.101$, $t\ -1.65$) did not.
```
WITH
```
  independent instrument --- the mean of the \arm{chunk2325} and \arm{nodewise1d} arms, neither of
  which enters $\Dstat$ --- gives $\mathbf{-0.208 \pm 0.089}$, $t\ -2.33$ within CIFAR-10, which
  now clears $|t| \ge 2$ where the sixteen-cell reading ($-0.168 \pm 0.112$, $t\ -1.50$) did not.
```

### T7 — §5.6, the withdrawn GroupNorm leg (line ~3005)

REPLACE
```
low-level point that flattened the within-CIFAR-10 slope, which without it moves from
$-0.044 \pm 0.070$ ($t\ -0.63$) to the $-0.173 \pm 0.051$ above.
```
WITH
```
low-level point that flattened the within-CIFAR-10 slope, which without it moves from
$-0.045 \pm 0.076$ ($t\ -0.59$) to the $-0.176 \pm 0.056$ above.
```

### T8 — §5.6, closing paragraph (line ~3012)

REPLACE
```
at 10 CIFAR-10 design points, where it is resolved ($|r|$ 0.766 against a critical 0.632) and
still collapses to $t\ -1.49$ the moment the network and the base are both held fixed.
```
WITH
```
at 9 CIFAR-10 design points, where it is resolved ($|r|$ 0.767 against a critical 0.666) and
still collapses to $t\ -1.27$ the moment the network and the base are both held fixed.
```

### T9 — §5.8, the grouping rule (line ~3064) — **this replacement also inserts the sensitivity paragraph**

REPLACE
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
```
WITH
```
The twenty $\Dstat$ cells of Table~\ref{tab:D} collapse to \textbf{10 distinct design points}
under the rule that two cells are one design point when they run the same network, dataset,
base--meta pairing, $\eta$ and budget, whatever submission they arrived in and whatever step-size
clip box they ran in: the six identical ResNet-18/SGDm/$\eta = 10^{-4}$/100-epoch batches are one
point; \arm{rl3} at $\eta = 3{\times}10^{-4}$ and \arm{fa1} are one; the two CIFAR-100 batches are
one; \arm{aw1} and \arm{sm3} are one; \arm{nl1}/SGD and \arm{bm2}/SGD are one;
\arm{nl1}/RMSProp and \arm{bm2}/RMSProp are one; \arm{hz3}, \arm{g3m}, \arm{r50} and \arm{sm4} ---
the last the corpus's only RMSProp meta --- are each their own. \textbf{Collapsing replicate
batches is not cosmetic, and the alternative is a trap we report rather than take}: a fold that
holds out \arm{bm2}/SGD while \arm{nl1}/SGD remains in the training set is not out of sample, and
scoring the four new cells as four new folds would turn the sign test below from 8/10
($p = 0.109$) into 11/13 ($p = 0.022$) without a single new configuration having been measured.
Four new cells bought \textbf{one} new design point.

\textbf{The clip box is deliberately not in the key, and a previous version of this paper had it
both ways.} \arm{rl3} at $\eta = 3{\times}10^{-4}$ and \arm{fa1} agree on every field the key
names --- and on batch size, $\alpha_0$, $\gamma$, augmentation and the hierarchical flags as well;
their runs' own \texttt{ARGS:} lines are identical up to the save directory and the run name --- and
differ only in \texttt{BETA\_CLIP} ($-30{:}9.0$ against $-25{:}{-}2.3026$). As measurements they
agree: $+0.591 \pm 0.096$ against $+0.629 \pm 0.123$, a difference of $+0.038 \pm 0.156$
($z\ 0.24$). The previous version of this paper nevertheless printed them as two points while
collapsing five \texttt{-15:-2.3026} batches together with \arm{rl3} at $\eta = 10^{-4}$, which
sits in $-30{:}9.0$, into one. We apply the rule as written. Naming the box in the key instead
gives \textbf{twelve} points, not eleven, and we report what that reading does rather than only
asserting that we rejected it: LOO RMSE 0.3514 for the mean against 0.2437 for
$k\cdot\log(\text{headroom})$ ($-31\%$, unchanged), but the all-folds sign test becomes 10/12,
$p = 0.039$, and \S\ref{sec:level}'s both-fixed leg becomes $-0.201 \pm 0.092$, $t\ -2.19$ (exact
permutation $p = 0.100$) on five points. \textbf{That is the only reading anywhere in this paper
under which a statistic in this section crosses $0.05$, and it buys the crossing by holding out
\arm{rl3} at $\eta = 10^{-4}$ while five batches identical to it on every key field stay in the
training set} --- the same leakage the previous paragraph rejects for \arm{bm2}/SGD. It is also
the box axis that \S\ref{sec:moderator} measures and rejects as a moderator (between-box
$Q = 0.76$ on 2 df, $p = 0.68$, over the eight SGDm cells that span all three boxes). We report
it, and we do not take it.

Leave-one-design-point-out, refitting each single-predictor model on the held-in 9:
```

### T10 — §5.8, the LOO table body (line ~3083)

REPLACE
```
\textbf{mean (baseline)} & \textbf{0.3685} & --- \\
$\Dstat \propto k\cdot\log(\text{headroom})$ & 0.2548 & $-31\%$ \\
CIFAR-100 dummy & 0.3601 & $-2\%$ \\
$\Dstat \propto k\cdot\text{headroom}$ & 0.3467 & $-6\%$ \\
$\Dstat \propto \text{level}$ (OLS) & 0.8678 & \textbf{$+135\%$ WORSE} \\
```
WITH
```
\textbf{mean (baseline)} & \textbf{0.3868} & --- \\
$\Dstat \propto k\cdot\log(\text{headroom})$ & 0.2667 & $-31\%$ \\
CIFAR-100 dummy & 0.3775 & $-2\%$ \\
$\Dstat \propto k\cdot\text{headroom}$ & 0.3654 & $-6\%$ \\
$\Dstat \propto \text{level}$ (OLS) & 0.9319 & \textbf{$+141\%$ WORSE} \\
```

### T11 — §5.8, "None of this is a result" (line ~3091)

REPLACE
```
\textbf{None of this is a result, and here is why.} The margin is still dominated by the single
CIFAR-100 fold: the mean errs by $-0.893$ there and $k\cdot\log(\text{headroom})$ by $-0.470$, and
restricted to the ten CIFAR-10 folds the best model wins by 0.042 RMSE
($0.2637 \rightarrow 0.2222$, $-16\%$; the level model, 0.2163, $-18\%$), with a sign test of
8/10, two-sided $p = 0.109$. Over all eleven folds the sign test is 9/11, $p = 0.065$.
```
WITH
```
\textbf{None of this is a result, and here is why.} The margin is still dominated by the single
CIFAR-100 fold: the mean errs by $-0.887$ there and $k\cdot\log(\text{headroom})$ by $-0.462$, and
restricted to the nine CIFAR-10 folds the best model wins by 0.046 RMSE
($0.2809 \rightarrow 0.2352$, $-16\%$; the level model, 0.2309, $-18\%$), with a sign test of
7/9, two-sided $p = 0.180$. Over all ten folds the sign test is 8/10, $p = 0.109$. \textbf{And the
sign test is not a stable statistic at this $n$}: on the sixteen cells this table replaces,
grouped by the same rule, it read 8/9 ($p\ 0.039$); adding four cells and one design point moves
it to 8/10 ($p\ 0.109$). A statistic that crosses $0.05$ in either direction when one fold is
added or removed is not evidence that a predictor works, and we read the RMSE margins rather than
the sign test wherever the two disagree.
```

### T12 — §5.8, the power bound and the level model (line ~3102)

REPLACE
```
power bound is still decisive: \textbf{at 11 design points a predictor needs $|r| \ge 0.602$ ---
it must explain $\ge 36\%$ of the between-design-point variance --- to be visible at
$p < 0.05$}; seeing $|r| = 0.4$ would need $\approx 25$ design points, which is not reachable by
brute force.

The level model earns its own sentence. Fitted on the ten CIFAR-10 points it predicts
$\Dstat(\text{CIFAR-100}) = \mathbf{+4.36}$ against $\mathbf{+1.56}$ observed, an error of
$+2.80$ pp --- more than three times the error of simply predicting the corpus mean.
```
WITH
```
power bound is still decisive: \textbf{at 10 design points a predictor needs $|r| \ge 0.632$ ---
it must explain $\ge 39.9\%$ of the between-design-point variance --- to be visible at
$p < 0.05$}; seeing $|r| = 0.4$ would need $\approx 25$ design points, which is not reachable by
brute force.

The level model earns its own sentence. Fitted on the nine CIFAR-10 points it predicts
$\Dstat(\text{CIFAR-100}) = \mathbf{+4.43}$ against $\mathbf{+1.56}$ observed, an error of
$+2.86$ pp --- more than three times the error of simply predicting the corpus mean.
```

### T13 — §5.8, the draft sentence (line ~3130)

REPLACE
```
than the corpus mean by a margin this design, at 11 design points, can resolve.}
```
WITH
```
than the corpus mean by a margin this design, at 10 design points, can resolve.}
```

### T14 — Appendix A.5 (line ~4152)

REPLACE
```
marginally ahead inside CIFAR-10 and the sign test was 9/11, $p = 0.065$. After the
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
WITH
```
marginally ahead inside CIFAR-10 and the sign test was 9/11, $p = 0.065$. After the
\arm{gn1}-GroupNorm removal the design-point set was recorded as 10, the best model won inside
CIFAR-10 by 0.040 RMSE ($0.2791 \rightarrow 0.2395$, $-14\%$) and the sign tests were 8/10
($p\ 0.109$) overall and 7/9 ($p\ 0.180$) inside CIFAR-10. Those counts are quoted as record: they
were produced by an enumeration that split \arm{rl3} at $\eta = 3{\times}10^{-4}$ from \arm{fa1},
two cells identical on every field of the stated key, while collapsing five batches together with
a sixth in a different clip box. \textbf{With \arm{bm2}, \arm{sm3} and \arm{sm4} ingested and the
rule applied as written the set is 10, not the \textbf{11} the record carried} --- those four
cells add one design point, not four, because three of them replicate a configuration already
present --- and the readings are 0.046 RMSE ($0.2809 \rightarrow 0.2352$, $-16\%$) with sign tests
8/10 ($p\ 0.109$) overall and 7/9 ($p\ 0.180$) inside CIFAR-10. The verdict is unchanged at every
step --- nothing reaches a threshold that survives adding or removing one fold, the margin is
dominated by one CIFAR-100 fold, the functional form is a best-of-ten selection, and the power
bound, now $|r| \ge 0.632$, is not approached. Two things are worth logging rather than smoothing.
The sixteen-cell step, regrouped by the corrected rule, would have read 9 points with a sign test
of 8/9 ($p\ 0.039$), so that statistic has crossed $0.05$ in both directions as folds were added;
and naming the clip box in the key --- the enumeration the record half-applied --- gives 12 points
and a sign test of 10/12 ($p\ 0.039$), which \S\ref{sec:prediction} reports and declines. The null
holds on the RMSE margins, which are stable, and by a narrower margin than the record implied.
```

---

## paper/DRAFT-v4.md

### M1 — §1, the power-bound parenthesis (line ~131)

REPLACE
```
power bound (|r| ≥ 0.602 needed at 11 design points). A cross-validated *null* at n = 11 is
defensible in a way a cross-validated success at n = 11 never is; we report both, and the null is
the one that survives.
```
WITH
```
power bound (|r| ≥ 0.632 needed at 10 design points). A cross-validated *null* at n = 10 is
defensible in a way a cross-validated success at n = 10 never is; we report both, and the null is
the one that survives.
```

### M2 — §5.6, opening paragraph (line ~2282)

REPLACE
```
Over all 11 design points (§5.8 states the grouping rule), regressing D on the aligned arm's
`plateau5` gives slope **−0.045 ± 0.010, t −4.52, r −0.833** — which looks like a law and is not
one, because level and dataset are the same column: the single CIFAR-100 design point sits at
level 70.44 and the ten CIFAR-10 design points at 89.63–93.04.
```
WITH
```
Over all 10 design points (§5.8 states the grouping rule), regressing D on the aligned arm's
`plateau5` gives slope **−0.045 ± 0.011, t −4.21, r −0.830** — which looks like a law and is not
one, because level and dataset are the same column: the single CIFAR-100 design point sits at
level 70.44 and the nine CIFAR-10 design points at 89.63–93.04.
```

### M3 — §5.6, second paragraph (line ~2287)

REPLACE
```
Inside CIFAR-10 the slope is **−0.173 ± 0.051, t −3.37, r −0.766** over 10 design points (exact
permutation over all 10! = 3,628,800 orderings, p = 0.0097). **This is a strengthening we did not
want and report anyway**: on the sixteen-cell set the same regression read −0.161 ± 0.067, r 0.669
against a critical 0.666, and the previous version of this paper called it a coin landing on its edge.
```
WITH
```
Inside CIFAR-10 the slope is **−0.176 ± 0.056, t −3.16, r −0.767** over 9 design points (exact
permutation over all 9! = 362,880 orderings, p = 0.0151). **This is a strengthening we did not
want and report anyway**: on the sixteen-cell set, grouped by the same rule, the same regression
read −0.162 ± 0.074, r 0.666 against a critical 0.707 at eight points — unresolved, and the
previous version of this paper, which split two cells that this rule joins and so read the sixteen
cells at nine CIFAR-10 points, got r 0.669 against a critical 0.666 and called it a coin landing
on its edge.
```

### M4 — §5.6, first bullet (line ~2298)

REPLACE
```
  (6 points, spanning ResNet-18/34/50) gives **−0.119 ± 0.022**; holding the network fixed at
  ResNet-18 (8 points, spanning five base–meta pairings) gives **−0.282 ± 0.068**; holding
  **both** fixed — the only four points where "level" varies with nothing else structural — gives
  **−0.187 ± 0.125, t −1.49, exact permutation p = 0.333, unresolved, and unmoved by the ingest.**
  A slope whose magnitude moves by 2.4× depending on which confound you hold, and which does not
  resolve when you hold both, is measuring the confounds.
```
WITH
```
  (5 points, spanning ResNet-18/34/50) gives **−0.126 ± 0.022**; holding the network fixed at
  ResNet-18 (7 points, spanning five base–meta pairings) gives **−0.287 ± 0.075**; holding
  **both** fixed — the only three points where "level" varies with nothing else structural — gives
  **−0.188 ± 0.148, t −1.27, unresolved.** At three points the exact permutation test carries no
  information: its smallest attainable two-sided p is 2/3! = 0.333 and the observed slope reaches
  only p = 0.667, so the t is the only reading available. It is also the reading that matters.
  A slope whose magnitude moves by 2.3× depending on which confound you hold, and which does not
  resolve when you hold both, is measuring the confounds.
```

### M5 — §5.6, the mechanical slope (line ~2305)

REPLACE
```
  of a `nodewise` arm mean over the 18 CIFAR-10 cells, 0.01724, over the variance of level across
  the ten design points, 1.11080 — under a tenth of −0.173, so the artefact is not the
  explanation.
```
WITH
```
  of a `nodewise` arm mean over the 18 CIFAR-10 cells, 0.01724, over the variance of level across
  the nine design points, 1.19374 — under a tenth of −0.176, so the artefact is not the
  explanation.
```

**Also in M5's sentence, two lines above the anchor, the bold value `**−0.016**` becomes
`**−0.014**`.** The full corrected bullet opening reads: *"D and level share the `nodewise` arm.
The mechanical slope this induces is **−0.014** — the mean sampling variance …"*. (The token
`**−0.016**` is not unique in the file, which is why it is described rather than anchored; make
the change inside this bullet only, at DRAFT-v4.md line ~2304.)

### M6 — §5.6, the instrument (line ~2309)

REPLACE
```
  `nodewise1d` arms, neither of which enters D — gives **−0.204 ± 0.082, t −2.49** within
  CIFAR-10, which now clears |t| ≥ 2 where the sixteen-cell reading (−0.167 ± 0.101, t −1.65) did
  not.
```
WITH
```
  `nodewise1d` arms, neither of which enters D — gives **−0.208 ± 0.089, t −2.33** within
  CIFAR-10, which now clears |t| ≥ 2 where the sixteen-cell reading (−0.168 ± 0.112, t −1.50) did
  not.
```

### M7 — §5.6, the withdrawn GroupNorm leg (line ~2331)

REPLACE
```
within-batch test, and it was also the low-level point that flattened the within-CIFAR-10 slope,
which without it moves from −0.044 ± 0.070 (t −0.63) to the −0.173 ± 0.051 above.
```
WITH
```
within-batch test, and it was also the low-level point that flattened the within-CIFAR-10 slope,
which without it moves from −0.045 ± 0.076 (t −0.59) to the −0.176 ± 0.056 above.
```

### M8 — §5.6, closing paragraph (line ~2335)

REPLACE
```
of the aligned arm is not separable from the network and the base optimiser in this corpus, at 10
CIFAR-10 design points, where it is resolved (|r| 0.766 against a critical 0.632) and still
collapses to t −1.49 the moment the network and the base are both held fixed.
```
WITH
```
of the aligned arm is not separable from the network and the base optimiser in this corpus, at 9
CIFAR-10 design points, where it is resolved (|r| 0.767 against a critical 0.666) and still
collapses to t −1.27 the moment the network and the base are both held fixed.
```

### M9 — §5.8, the grouping rule (line ~2382) — **also inserts the sensitivity paragraph**

REPLACE
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
```
WITH
```
The twenty D cells of Table 2 collapse to **10 distinct design points** under the rule that two
cells are one design point when they run the same network, dataset, base–meta pairing, η and
budget, whatever submission they arrived in and whatever step-size clip box they ran in: the six
identical ResNet-18/SGDm/η=1e-4/100-epoch batches are one point; `rl3` at η = 3e-4 and `fa1` are
one; the two CIFAR-100 batches are one; `aw1` and `sm3` are one; `nl1`/SGD and `bm2`/SGD are one;
`nl1`/RMSProp and `bm2`/RMSProp are one; `hz3`, `g3m`, `r50` and `sm4` — the last the corpus's only
RMSProp meta — are each their own. **Collapsing replicate batches is not cosmetic, and the
alternative is a trap we report rather than take**: a fold that holds out `bm2`/SGD while
`nl1`/SGD remains in the training set is not out of sample, and scoring the four new cells as four
new folds would turn the sign test below from 8/10 (p = 0.109) into 11/13 (p = 0.022) without a
single new configuration having been measured. Four new cells bought **one** new design point.

**The clip box is deliberately not in the key, and a previous version of this paper had it both
ways.** `rl3` at η = 3e-4 and `fa1` agree on every field the key names — and on batch size, α₀, γ,
augmentation and the hierarchical flags as well; their runs' own `ARGS:` lines are identical up to
the save directory and the run name — and differ only in `BETA_CLIP` (−30:9.0 against
−25:−2.3026). As measurements they agree: +0.591 ± 0.096 against +0.629 ± 0.123, a difference of
+0.038 ± 0.156 (z 0.24). The previous version of this paper nevertheless printed them as two
points while collapsing five `-15:-2.3026` batches together with `rl3` at η = 1e-4, which sits in
−30:9.0, into one. We apply the rule as written. Naming the box in the key instead gives **twelve**
points, not eleven, and we report what that reading does rather than only asserting that we
rejected it: LOO RMSE 0.3514 for the mean against 0.2437 for k·log(headroom) (−31%, unchanged),
but the all-folds sign test becomes 10/12, p = 0.039, and §5.6's both-fixed leg becomes
−0.201 ± 0.092, t −2.19 (exact permutation p = 0.100) on five points. **That is the only reading
anywhere in this paper under which a statistic in this section crosses 0.05, and it buys the
crossing by holding out `rl3` at η = 1e-4 while five batches identical to it on every key field
stay in the training set** — the same leakage the previous paragraph rejects for `bm2`/SGD. It is
also the box axis that §4.4 measures and rejects as a moderator (between-box Q = 0.76 on 2 df,
p = 0.68, over the eight SGDm cells that span all three boxes). We report it, and we do not take
it.

Leave-one-design-point-out, refitting each single-predictor model on the held-in 9:
```

### M10 — §5.8, the LOO table body (line ~2396)

REPLACE
```
| **mean (baseline)** | **0.3685** | — |
| D ∝ k·log(headroom) | 0.2548 | −31% |
| CIFAR-100 dummy | 0.3601 | −2% |
| D ∝ k·headroom | 0.3467 | −6% |
| D ∝ level (OLS) | 0.8678 | **+135% WORSE** |
```
WITH
```
| **mean (baseline)** | **0.3868** | — |
| D ∝ k·log(headroom) | 0.2667 | −31% |
| CIFAR-100 dummy | 0.3775 | −2% |
| D ∝ k·headroom | 0.3654 | −6% |
| D ∝ level (OLS) | 0.9319 | **+141% WORSE** |
```

### M11 — §5.8, "None of this is a result" (line ~2402)

REPLACE
```
**None of this is a result, and here is why.** The margin is still dominated by the single
CIFAR-100 fold: the mean errs by −0.893 there and `k·log(headroom)` by −0.470, and restricted to
the ten CIFAR-10 folds the best model wins by 0.042 RMSE (0.2637 → 0.2222, −16%; the level model,
0.2163, −18%), with a sign test of 8/10, two-sided p = 0.109. Over all eleven folds the sign test
is 9/11, p = 0.065.
```
WITH
```
**None of this is a result, and here is why.** The margin is still dominated by the single
CIFAR-100 fold: the mean errs by −0.887 there and `k·log(headroom)` by −0.462, and restricted to
the nine CIFAR-10 folds the best model wins by 0.046 RMSE (0.2809 → 0.2352, −16%; the level model,
0.2309, −18%), with a sign test of 7/9, two-sided p = 0.180. Over all ten folds the sign test is
8/10, p = 0.109. **And the sign test is not a stable statistic at this n**: on the sixteen cells
this table replaces, grouped by the same rule, it read 8/9 (p 0.039); adding four cells and one
design point moves it to 8/10 (p 0.109). A statistic that crosses 0.05 in either direction when
one fold is added or removed is not evidence that a predictor works, and we read the RMSE margins
rather than the sign test wherever the two disagree.
```

### M12 — §5.8, the power bound and the level model (line ~2411)

REPLACE
```
And the power bound is still decisive: **at 11 design points a predictor needs
|r| ≥ 0.602 — it must explain ≥ 36% of the between-design-point variance — to be visible at
p < 0.05**; seeing |r| = 0.4 would need ≈ 25 design points, which is not reachable by brute force.

The level model earns its own sentence. Fitted on the ten CIFAR-10 points it predicts
D(CIFAR-100) = **+4.36 against +1.56 observed**, an error of +2.80 pp — more than three times the
error of simply predicting the corpus mean.
```
WITH
```
And the power bound is still decisive: **at 10 design points a predictor needs
|r| ≥ 0.632 — it must explain ≥ 39.9% of the between-design-point variance — to be visible at
p < 0.05**; seeing |r| = 0.4 would need ≈ 25 design points, which is not reachable by brute force.

The level model earns its own sentence. Fitted on the nine CIFAR-10 points it predicts
D(CIFAR-100) = **+4.43 against +1.56 observed**, an error of +2.86 pp — more than three times the
error of simply predicting the corpus mean.
```

### M13 — §5.8, the draft sentence (line ~2436)

REPLACE
```
> predicts D out of sample better than the corpus mean by a margin this design, at 11 design
> points, can resolve.*
```
WITH
```
> predicts D out of sample better than the corpus mean by a margin this design, at 10 design
> points, can resolve.*
```

### M14 — Appendix A.5 (line ~3305)

REPLACE
```
ahead inside CIFAR-10 and the sign test was 9/11, p = 0.065. After the `gn1`-GroupNorm removal the
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
WITH
```
ahead inside CIFAR-10 and the sign test was 9/11, p = 0.065. After the `gn1`-GroupNorm removal the
design-point set was recorded as 10, the best model won inside CIFAR-10 by 0.040 RMSE
(0.2791 → 0.2395, −14%) and the sign tests were 8/10 (p 0.109) overall and 7/9 (p 0.180) inside
CIFAR-10. Those counts are quoted as record: they were produced by an enumeration that split `rl3`
at η = 3e-4 from `fa1`, two cells identical on every field of the stated key, while collapsing five
batches together with a sixth in a different clip box. **With `bm2`, `sm3` and `sm4` ingested and
the rule applied as written the set is 10, not the 11 the record carried** — those four cells add
one design point, not four, because three of them replicate a configuration already present — and
the readings are 0.046 RMSE (0.2809 → 0.2352, −16%) with sign tests 8/10 (p 0.109) overall and 7/9
(p 0.180) inside CIFAR-10. The verdict is unchanged at every step — nothing reaches a threshold
that survives adding or removing one fold, the margin is dominated by one CIFAR-100 fold, the
functional form is a best-of-ten selection, and the power bound, now |r| ≥ 0.632, is not
approached. Two things are worth logging rather than smoothing. The sixteen-cell step, regrouped
by the corrected rule, would have read 9 points with a sign test of 8/9 (p 0.039), so that
statistic has crossed 0.05 in both directions as folds were added; and naming the clip box in the
key — the enumeration the record half-applied — gives 12 points and a sign test of 10/12
(p 0.039), which §5.8 reports and declines. The null holds on the RMSE margins, which are stable,
and by a narrower margin than the record implied.
```

---

# ASSERTION SITES — new section for `analysis/c98_reproduce.py`

Insert the block below immediately before the `SECTIONS = [...]` list, and add
`("designpoints", designpoints),` to that list **immediately before** `("censuscheck",
censuscheck)` — which must stay last, because it freezes `CENSUS_MARK`. The list is reproduced
below as it stood at HEAD 351d9a6; other packages may have added entries by the time this is
applied, so insert the one tuple rather than pasting the whole list.

```python
SECTIONS = [("corpus", corpus), ("table2", table2), ("heterogeneity", heterogeneity),
            ("alignment", alignment), ("prescription", prescription), ("tail", tail),
            ("budget", budget), ("competitiveness", competitiveness),
            ("rho", rho), ("gn1gate", gn1gate), ("metacensus", metacensus),
            ("countaxis", countaxis),
            ("tuning", tuning), ("appendices", appendices), ("deposit", deposit),
            ("metricsens", metricsens),
            ("designpoints", designpoints),
            ("censuscheck", censuscheck)]      # MUST stay last: it freezes CENSUS_MARK
```

The section as printed below was extracted from this file and executed against the live CSV
through `c98_reproduce`'s own `chk()`, `arm()`, `cells()` and `welch()`: **71 assertions, 71
PASS, 0 FAIL.**

```python
# ================================================ NEW: the design-point set, §5.6 / §5.8
# B6.  §5.8 states a design-point rule -- same network, dataset, base--meta pairing,
# eta and budget -- and the enumeration that follows it printed ELEVEN points while the
# rule itself yields TEN: `rl3` at eta 3e-4 and `fa1` are identical on every element of
# the key and differ only in the step-size clip box, which the same enumeration already
# collapses across for its six-batch point and which §4.4 measures and rejects as a
# moderator.  This section applies the rule as written and asserts every number §5.6 and
# §5.8 print under it, including the 12-point sensitivity the paper reports and rejects.
DP_KEY = lambda c: (c["network"], c["dataset"], c["base"], c["eta"], c["epochs"])

def _dp_instr(adm):
    """The tail-free instrument of §5.6: mean of the chunk2325 and nodewise1d arms."""
    out = {}
    for (lab, net, ds, base, eta, ep, ch, nd, c23, n1d) in F.CELLS:
        if lab == F.GN_CELL and not F.WITH_GN: continue
        if not (c23 and n1d): continue
        gv, _ = arm(adm, *c23); hv, _ = arm(adm, *n1d)
        if gv and hv: out[lab] = 0.5 * (st.mean(gv) + st.mean(hv))
    return out

def _dp_box(rows):
    """The beta_clip box(es) each cell's own D arms ran in, read off the CSV."""
    out = {}
    for (lab, net, ds, base, eta, ep, ch, nd, c23, n1d) in F.CELLS:
        if lab == F.GN_CELL and not F.WITH_GN: continue
        b = set()
        for pre, gran in (ch, nd):
            b |= {r["beta_clip"] for r in rows
                  if r["run"].startswith(pre) and r["granularity"] == gran}
        out[lab] = "+".join(sorted(b))
    return out

def _dp_points(cs, keyfn, instr):
    g = {}
    for c in cs: g.setdefault(keyfn(c), []).append(c)
    pts = []
    for cl in g.values():
        ins = [instr[c["label"]] for c in cl if c["label"] in instr]
        pts.append(dict(labels=[c["label"] for c in cl],
                        D=st.mean([c["D"] for c in cl]),
                        level=st.mean([c["aligned"] for c in cl]),
                        headroom=st.mean([c["headroom"] for c in cl]),
                        instr=(st.mean(ins) if ins else None),
                        dataset=cl[0]["dataset"], network=cl[0]["network"],
                        base=cl[0]["base"]))
    return sorted(pts, key=lambda p: (p["dataset"], -p["D"]))

def _dp_fit_mean(tr):
    m = st.mean([q["D"] for q in tr]);  return lambda p: m
def _dp_fit_origin(tr, x):
    k = sum(x(q) * q["D"] for q in tr) / sum(x(q) ** 2 for q in tr)
    return lambda p: k * x(p)
def _dp_fit_ols(tr, x):
    n = len(tr); xs = [x(q) for q in tr]; ys = [q["D"] for q in tr]
    mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((v - mx) ** 2 for v in xs)
    if sxx == 0: return lambda p: my           # dummy is constant in this fold
    b = sum((v - mx) * (y - my) for v, y in zip(xs, ys)) / sxx
    return lambda p: (my - b * mx) + b * x(p)
DP_MODELS = [
    ("mean (baseline)",   _dp_fit_mean),
    ("k*log(headroom)",   lambda tr: _dp_fit_origin(tr, lambda q: math.log(q["headroom"]))),
    ("CIFAR-100 dummy",   lambda tr: _dp_fit_ols(tr, lambda q: 1.0 if q["dataset"] == "C100" else 0.0)),
    ("k*headroom",        lambda tr: _dp_fit_origin(tr, lambda q: q["headroom"])),
    ("level (OLS)",       lambda tr: _dp_fit_ols(tr, lambda q: q["level"]))]

def _dp_loo(pts):
    out = {}
    for name, fit in DP_MODELS:
        e = [fit([q for j, q in enumerate(pts) if j != i])(p) - p["D"]
             for i, p in enumerate(pts)]
        c10 = [v for v, p in zip(e, pts) if p["dataset"] == "C10"]
        out[name] = (math.sqrt(sum(v * v for v in e) / len(e)),
                     math.sqrt(sum(v * v for v in c10) / len(c10)), e)
    return out

def _dp_binom2(w, n):
    from math import comb
    lo = min(w, n - w)
    return min(1.0, 2.0 * sum(comb(n, i) for i in range(lo + 1)) / 2 ** n)

def _dp_ols(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    sxx = sum((v - mx) ** 2 for v in xs)
    sxy = sum((v - mx) * (y - my) for v, y in zip(xs, ys))
    b = sxy / sxx; a = my - b * mx
    res = [y - (a + b * v) for v, y in zip(xs, ys)]
    se = math.sqrt(sum(r * r for r in res) / (n - 2) / sxx) if n > 2 else float("nan")
    syy = sum((y - my) ** 2 for y in ys)
    return b, se, b / se, sxy / math.sqrt(sxx * syy)

def _dp_perm(xs, ys):
    """Exact two-sided permutation p for the OLS slope.  sxx and both means are fixed
    under permutation of y, so |b| is monotone in |sum(x_i y_sigma(i)) - n mx my|."""
    import itertools
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n; c = n * mx * my
    obs = abs(sum(a * b for a, b in zip(xs, ys)) - c)
    hit = tot = 0
    for pm in itertools.permutations(ys):
        tot += 1
        if abs(sum(a * b for a, b in zip(xs, pm)) - c) >= obs - 1e-9: hit += 1
    return hit / tot

def _dp_critr(n):
    """Two-sided 5% critical Pearson r at df = n-2: bisect the Student-t survival
    function, written as a regularised incomplete beta (Numerical Recipes 6.4)."""
    df = n - 2
    def _betacf(a, b, x):
        tiny = 1e-30; c = 1.0; d = 1 - (a + b) * x / (a + 1)
        if abs(d) < tiny: d = tiny
        d = 1 / d; h = d
        for m in range(1, 300):
            m2 = 2 * m
            aa = m * (b - m) * x / ((a + m2 - 1) * (a + m2))
            d = 1 + aa * d; c = 1 + aa / c
            if abs(d) < tiny: d = tiny
            if abs(c) < tiny: c = tiny
            d = 1 / d; h *= d * c
            aa = -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1))
            d = 1 + aa * d; c = 1 + aa / c
            if abs(d) < tiny: d = tiny
            if abs(c) < tiny: c = tiny
            d = 1 / d; de = d * c; h *= de
            if abs(de - 1) < 1e-14: break
        return h
    def _betainc(a, b, x):
        if x <= 0: return 0.0
        if x >= 1: return 1.0
        lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        if x < (a + 1) / (a + b + 2):
            return math.exp(math.log(x) * a + math.log(1 - x) * b + lb) * _betacf(a, b, x) / a
        return 1 - math.exp(math.log(1 - x) * b + math.log(x) * a + lb) * _betacf(b, a, 1 - x) / b
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _betainc(df / 2, 0.5, df / (df + mid * mid)) > 0.05: lo = mid
        else: hi = mid
    t = (lo + hi) / 2
    return t / math.sqrt(t * t + df)

def designpoints(rows, adm, args):
    print("\n[17] THE DESIGN-POINT SET  (§5.8's rule, applied as written; §5.6's slopes)")
    cs    = cells(adm)
    instr = _dp_instr(adm)
    box   = _dp_box(rows)

    # --- the collapse the previous enumeration missed, at cell level.  RULE 20 was
    #     checked against the runs' own ARGS:/ENV: lines; see
    #     paper/sections/v6-design-points.md §A.2.
    d = {c["label"]: c for c in cs}
    chk("rl3 @3e-4 and fa1 share every key field", 1.0 if
        DP_KEY(d["rl3 @3e-4"]) == DP_KEY(d["fa1"]) else 0.0, 1.0, "§5.8", "%.0f")
    chk("...and differ in the clip box", 0.0 if box["rl3 @3e-4"] == box["fa1"] else 1.0,
        1.0, "§5.8", "%.0f")
    dd  = d["fa1"]["D"] - d["rl3 @3e-4"]["D"]
    sed = math.sqrt(d["fa1"]["seD"] ** 2 + d["rl3 @3e-4"]["seD"] ** 2)
    chk("fa1 - rl3@3e-4, as cells", dd, +0.038, "§5.8")
    chk("   se", sed, 0.156, "§5.8", "%.3f")
    chk("   z",  dd / sed, +0.24, "§5.8", "%.2f")
    chk("cells of the six-batch point in the -15 box",
        float(sum(1 for l in ("cc1", "mm1", "pp1", "gn1 (BN)", "ml2")
                  if box[l] == "-15:-2.3026")), 5, "§5.8", "%.0f")

    pts = _dp_points(cs, DP_KEY, instr)
    c10 = [p for p in pts if p["dataset"] == "C10"]
    chk("design points under the rule as written", len(pts), 10, "§5.8", "%.0f")
    chk("   of which CIFAR-10",                    len(c10),  9, "§5.6", "%.0f")

    res = _dp_loo(pts)
    for name, paper, paper10 in [("mean (baseline)", 0.3868, 0.2809),
                                 ("k*log(headroom)", 0.2667, 0.2352),
                                 ("CIFAR-100 dummy", 0.3775, None),
                                 ("k*headroom",      0.3654, None),
                                 ("level (OLS)",     0.9319, 0.2309)]:
        chk("LOO RMSE  %-16s" % name, res[name][0], paper, "§5.8 table", "%.4f")
        if paper10 is not None:
            chk("   CIFAR-10 folds", res[name][1], paper10, "§5.8 prose", "%.4f")
    base, alt = res["mean (baseline)"][2], res["k*log(headroom)"][2]
    w  = sum(1 for i in range(len(pts)) if abs(alt[i]) < abs(base[i]))
    w9 = sum(1 for i, p in enumerate(pts) if p["dataset"] == "C10" and abs(alt[i]) < abs(base[i]))
    chk("sign test, all folds (wins)", w, 8, "§5.8", "%.0f")
    chk("   p", _dp_binom2(w, len(pts)), 0.109, "§5.8", "%.3f")
    chk("sign test, CIFAR-10 folds (wins)", w9, 7, "§5.8", "%.0f")
    chk("   p", _dp_binom2(w9, len(c10)), 0.180, "§5.8", "%.3f")
    for e, nm, pv in [(base, "mean", -0.887), (alt, "k*log(headroom)", -0.462)]:
        for v, q in zip(e, pts):
            if q["dataset"] == "C100":
                chk("CIFAR-100 fold error, %-16s" % nm, v, pv, "§5.8")
    chk("critical |r| at 10 design points", _dp_critr(10), 0.632, "§5.8", "%.3f")
    chk("   its r^2 (share of variance needed)", 100 * _dp_critr(10) ** 2, 39.9,
        "§5.8", "%.1f")
    chk("critical |r| at 9 CIFAR-10 points", _dp_critr(9), 0.666, "§5.6", "%.3f")
    chk("|r| = 0.4 first visible at n =",
        float(min(n for n in range(5, 60) if _dp_critr(n) <= 0.4)), 25, "§5.8", "%.0f")

    # the level model, out of sample
    f = _dp_fit_ols(c10, lambda q: q["level"]); m = _dp_fit_mean(c10)
    for p in pts:
        if p["dataset"] == "C100":
            chk("level model predicts D(CIFAR-100)", f(p), +4.43, "§5.8", "%.2f")
            chk("   observed",                      p["D"], +1.56, "§5.8", "%.2f")
            chk("   its error",                     f(p) - p["D"], +2.86, "§5.8", "%.2f")
            chk("   the corpus mean's error",       m(p) - p["D"], -0.89, "§5.8", "%.2f")

    # --- §5.6's slopes on the same points
    def sl(sel, nm, pb, pse, pt, pr=None):
        b, se, t, r = _dp_ols([p["level"] for p in sel], [p["D"] for p in sel])
        chk("slope %-26s" % nm, b, pb, "§5.6")
        chk("   se", se, pse, "", "%.3f")
        chk("   t",  t,  pt,  "", "%.2f")
        if pr is not None: chk("   r", r, pr, "", "%.3f")
        return b
    sl(pts, "all 10 points",          -0.045, 0.011, -4.21, -0.830)
    sl(c10, "9 CIFAR-10 points",      -0.176, 0.056, -3.16, -0.767)
    chk("   exact permutation p over 9!",
        _dp_perm([p["level"] for p in c10], [p["D"] for p in c10]), 0.0151, "§5.6", "%.4f")
    sgdm = [p for p in c10 if p["base"] == "SGDm"]
    r18  = [p for p in c10 if p["network"] == "ResNet-18"]
    both = [p for p in r18 if p["base"] == "SGDm"]
    chk("CIFAR-10 points with base SGDm",  len(sgdm), 5, "§5.6", "%.0f")
    chk("CIFAR-10 points on ResNet-18",    len(r18),  7, "§5.6", "%.0f")
    chk("CIFAR-10 points with both fixed", len(both), 3, "§5.6", "%.0f")
    bs = sl(sgdm, "base fixed at SGDm",   -0.126, 0.022, -5.74)
    br = sl(r18,  "network fixed at R18", -0.287, 0.075, -3.83)
    sl(both,      "both fixed",           -0.188, 0.148, -1.27)
    chk("ratio of the two held-one slopes", br / bs, 2.3, "§5.6", "%.1f")
    chk("both-fixed exact permutation p over 3!",
        _dp_perm([p["level"] for p in both], [p["D"] for p in both]), 0.667, "§5.6", "%.3f")
    ins = [p for p in c10 if p["instr"] is not None]
    b, se, t, _ = _dp_ols([p["instr"] for p in ins], [p["D"] for p in ins])
    chk("slope on the independent instrument", b, -0.208, "§5.6")
    chk("   se", se, 0.089, "", "%.3f"); chk("   t", t, -2.33, "", "%.2f")
    # the arm-sharing artefact
    mv = []
    for (lab, net, ds, base, eta, ep, ch, nd, c23, n1d) in F.CELLS:
        if lab == F.GN_CELL and not F.WITH_GN: continue
        if ds != "C10": continue
        nv, _ = arm(adm, *nd); mv.append(st.variance(nv) / len(nv))
    chk("mean var of a nodewise arm mean, 18 C10 cells", st.mean(mv), 0.01724, "§5.6", "%.5f")
    vl = st.variance([p["level"] for p in c10])
    chk("var of level over the 9 CIFAR-10 points", vl, 1.19374, "§5.6", "%.5f")
    chk("mechanical slope", -st.mean(mv) / vl, -0.014, "§5.6")

    # --- the sensitivity §5.8 reports and rejects: the clip box in the key -> 12 points
    p12 = _dp_points(cs, lambda c: DP_KEY(c) + (box[c["label"]],), instr)
    chk("design points if the clip box enters the key", len(p12), 12, "§5.8", "%.0f")
    r12 = _dp_loo(p12)
    chk("   LOO RMSE, mean baseline",   r12["mean (baseline)"][0], 0.3514, "§5.8", "%.4f")
    chk("   LOO RMSE, k*log(headroom)", r12["k*log(headroom)"][0], 0.2437, "§5.8", "%.4f")
    b12, a12 = r12["mean (baseline)"][2], r12["k*log(headroom)"][2]
    w12 = sum(1 for i in range(len(p12)) if abs(a12[i]) < abs(b12[i]))
    chk("   sign test wins", w12, 10, "§5.8", "%.0f")
    chk("   its p (the one threshold this reading crosses)",
        _dp_binom2(w12, len(p12)), 0.039, "§5.8", "%.3f")
    b5 = [p for p in p12 if p["dataset"] == "C10" and p["base"] == "SGDm"
          and p["network"] == "ResNet-18"]
    bb5, se5, t5, _ = _dp_ols([p["level"] for p in b5], [p["D"] for p in b5])
    chk("   §5.6's both-fixed leg at 5 points", bb5, -0.201, "§5.8")
    chk("      se", se5, 0.092, "", "%.3f"); chk("      t", t5, -2.19, "", "%.2f")
    chk("      its exact permutation p over 5!",
        _dp_perm([p["level"] for p in b5], [p["D"] for p in b5]), 0.100, "§5.8", "%.3f")

    # --- the leakage variant §5.8 names and rejects
    NEW = ("sm3", "bm2 (SGD)", "bm2 (RMSProp)", "sm4")
    p13 = _dp_points(cs, lambda c: ("E", c["label"]) if c["label"] in NEW else DP_KEY(c), instr)
    chk("design points if the four new cells are new folds", len(p13), 13, "§5.8", "%.0f")
    r13 = _dp_loo(p13)
    b13, a13 = r13["mean (baseline)"][2], r13["k*log(headroom)"][2]
    w13 = sum(1 for i in range(len(p13)) if abs(a13[i]) < abs(b13[i]))
    chk("   sign test wins", w13, 11, "§5.8", "%.0f")
    chk("   its p", _dp_binom2(w13, len(p13)), 0.022, "§5.8", "%.3f")
```

---

# NOTES FOR THE INTEGRATOR

1. **The census is already out of fixpoint in the working tree, before this package.** A run of
   `python3 analysis/c98_reproduce.py` at HEAD 351d9a6 prints 414 assertion sites / 267 covered /
   786 distinct and **3 FAILS**, all of them §3.4 staleness (§3.4 still says 353 / 256 / 32.6%).
   A concurrent package has already added sites. This package adds 71 more. **Do not copy any
   census triple out of this document**; run `--census` after all packages are merged and write
   the printed triple into §3.4 of both files, then re-run to a fixpoint.
2. **Numeric diff between paper.tex and DRAFT-v4.md.** Every replacement above is paired
   (T*n* ↔ M*n*). The one change that is described rather than anchored is the `−0.016` → `−0.014`
   token inside DRAFT-v4.md's §5.6 mechanical-slope bullet (note under M5); its LaTeX twin is
   inside T5's anchored block. Check that one by eye.
3. **Nothing outside §1, §5.6, §5.8 and Appendix A.5 changes.** The other occurrences of "design
   point" — tex 256, 455, 1620, 1881, 2215, 3167, 3505, 3981 and their DRAFT-v4.md twins — carry
   no point count and are correct as they stand.
4. **Table 2, Figure 1, Figure 2, §4.4's heterogeneity pools and every cell-level number are
   untouched.** The design point is a §5.6/§5.8 construct only.
5. Re-run `tectonic` after applying; nothing here changes float placement or adds a label.

---

# VERIFICATION RUN FOR THIS PACKAGE

* All 28 anchors above re-checked against `paper/paper.tex` and `paper/DRAFT-v4.md` at HEAD
  351d9a6: **every OLD block occurs exactly once.**
* **Dry run.** All 28 replacements plus the described `−0.016` → `−0.014` token were applied to a
  scratch copy of `paper/`; `tectonic paper.tex` **exit 0**, 701.99 KiB PDF, no new warnings.
* **Numeric diff, tex against md, on the changed regions.** §5.6–§5.8: 118 numerals in the tex,
  129 in the Markdown, and the eleven-token difference is exactly the Markdown's inline section
  cross-references (`§5.6` ×3, `§5.7` ×1, `§5.8` ×4, `§4.4` ×3), which are `\S\ref{}` in the tex.
  Appendix A.5: same, one `§5.8`. The §1 parenthesis: identical. **No numeral differs.**
* **Assertion section**: extracted from this file and executed against `results/all_runs.csv`
  through `c98_reproduce`'s own `chk()` — **71 assertions, 71 PASS, 0 FAIL.**
* **Nothing was committed and neither `paper.tex` nor `DRAFT-v4.md` was edited.**
