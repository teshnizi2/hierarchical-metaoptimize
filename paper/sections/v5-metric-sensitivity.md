# PACKAGE `metric-sensitivity` — closes M1

**Item.** Contribution 3 is conditional on a post-hoc metric choice and the paper never says so.

**Status.** Re-derived, confirmed, and written. All of the briefing's figures reproduce exactly.
Assertion sites added to `analysis/c98_reproduce.py` (new `--metricsens` section, 70 checks, all
PASS). **`paper/paper.tex` and `paper/DRAFT-v4.md` were NOT edited** — the exact replacement text
is below, keyed to verbatim, verified-unique anchors.

---

## 1. The re-derivation

### 1.1 What was varied, and what was held fixed

The paper's own machinery was used unedited: `c98_figures.arm()` (admissible rows of one arm,
`dup_group`-collapsed per rule R-E), `c98_figures.welch()`, `c98_figures.cells()` over the
declared `CELLS` table, and `c98_figures.meta()` (DerSimonian–Laird). **Only the metric column
`arm()` reads was swapped.** Held fixed, deliberately:

* the admissibility gate of Eq. (9) — `window_ok ∧ complete ∧ plateau5 readable`. It is **not**
  re-derived per metric. Re-deriving it would change the row set and turn this into row-filter
  sensitivity, which is §7 T10's axis, not this one. 1,731 admissible rows in all four passes.
* the arm prefixes and granularity strings of `CELLS`;
* the `dup_group` collapse (so `ml2` stays 3 v 3);
* the pool membership: the fourteen byte-identical ResNet-18 cells of `POOL12` minus the
  withdrawn GroupNorm cell, `sm4` excluded by its own scorer's scope note (asserted in code);
* the twenty count-matched Table 2 cells for the sign count.

Guard assertions in the new code fail loudly if the cell set moves with the metric
(`len(live) == 14 and len(cs20) == 20`) or if `sm4` leaks into the pool.

### 1.2 The briefing's table — CONFIRMED, with two corrections of rounding

| quantity | briefing | re-derived (full precision) | verdict |
|---|---|---|---|
| plateau5 `Q`/13 | 102.47 | 102.473885 | confirmed |
| plateau5 `p` | 5.5e-16 | 5.493e-16 | confirmed |
| plateau5 `τ` | 0.295 | 0.294846 | confirmed |
| plateau5 base share | 92.8% | 92.818951% | confirmed |
| plateau `Q` | 29.37 | 29.367672 | confirmed |
| plateau `p` | 0.0058 | 0.005803 | confirmed |
| plateau base share | 62.5% | 62.505237% | confirmed |
| best_test `Q` | 9.87 | 9.872911 | confirmed |
| best_test `p` | 0.704 | 0.70428 | confirmed |
| best_test `τ` | 0.000 | 0.000000 | confirmed |
| best_test base share | 37.5% | 37.465862% | confirmed |
| final_test `Q` | 39.91 | 39.911303 | confirmed |
| final_test `p` | 1.4e-4 | 1.4288e-4 | confirmed |
| final_test base share | 86.8% | 86.844855% | confirmed |
| sign count | 20/20, 20/20, 20/20, 19/20 | identical | confirmed |

**Two corrections to the briefing, both minor and both now in the paper text:**

1. **`τ` on the `plateau` column is 0.101, not 0.102.** Full precision 0.101472; the briefing did
   not quote it, but a 3-dp reader would round it wrong. Asserted at 0.101.
2. **`best_test` and `final_test` do not appear "ZERO times" in `paper.tex`.** They appear
   **once each**, at `tex:3372–3373` / `md:2667`, in §8's listing of the deposited CSV's schema —
   as column names, never as an analysis. The defect is unchanged in substance (no reader could
   learn anything about them), but the manuscript text says "only as column names in §8's schema
   listing" rather than "nowhere", because the latter would be false.

### 1.3 The full four-endpoint table, as re-derived

Fourteen-cell byte-identical ResNet-18 pool; `df = 13`; between-base on 3 df.

| endpoint | pooled D | Q/13 | p | τ | I² | between-base Q/3 | share | cells D>0 | resolved t≥3 | rms se | sd(D) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `plateau5` (primary) | +0.5297 ± 0.0294 | 102.4739 | 5.49e-16 | 0.2948 | 87.3% | 95.1152 (p 1.7e-20) | 92.82% | 20/20 | 18/20 | 0.1433 | 0.2549 |
| `plateau` (20-epoch) | +0.4493 ± 0.0238 | 29.3677 | 0.005803 | 0.1015 | 55.7% | 18.3563 (p 3.7e-4) | 62.51% | 20/20 | 20/20 | 0.1124 | 0.1594 |
| `best_test` | +0.3956 ± 0.0251 | **9.8729** | **0.7043** | **0.0000** | **0.0%** | **3.6990 (p 0.296)** | 37.47% | 20/20 | 11/20 | 0.1374 | **0.0843** |
| `final_test` | +0.6144 ± 0.0426 | 39.9113 | 1.43e-04 | 0.2509 | 67.4% | 34.6609 (p 1.4e-7) | 86.84% | **19/20** | 7/20 | 0.3552 | 0.3936 |

Within-level Q (10 df, all four levels): 7.3587 (p 0.691), 11.0113 (p 0.357), 6.1739 (p 0.800),
5.2504 (p 0.874).

**The `best_test` null is not an error-inflation artefact.** Its rms measurement se over the
fourteen cells is 0.1374 pp against `plateau5`'s 0.1433 pp — within 5%. What collapses is the
*spread*: sd(D) falls from 0.2549 pp to 0.0843 pp, i.e. below the measurement error, which is why
`Q = 9.87` sits *under* its own 13 df and DerSimonian–Laird returns `τ = 0`. There is nothing to
decompose.

### 1.4 Base-level pools and the rank inversion

| endpoint | SGD | RMSProp | SGDm | AdamW | spread (max/min) | rank, best to worst |
|---|---|---|---|---|---|---|
| `plateau5` | +1.00006 ± 0.06730 | +0.72039 ± 0.12832 | +0.55562 ± 0.04481 | +0.18911 ± 0.05151 | 5.29 | SGD, RMSProp, SGDm, AdamW |
| `plateau` | +0.73663 ± 0.10466 | +0.63411 ± 0.08120 | +0.43834 ± 0.02859 | +0.31481 ± 0.05739 | 2.34 | SGD, RMSProp, SGDm, AdamW |
| `best_test` | +0.43196 ± 0.06205 | +0.38573 ± 0.07247 | +0.41145 ± 0.03212 | +0.26056 ± 0.07678 | 1.66 | SGD, SGDm, RMSProp, AdamW |
| `final_test` | +0.13871 ± 0.37258 | +1.51788 ± 0.16707 | +0.58819 ± 0.04909 | +0.42041 ± 0.10365 | 10.94 | **RMSProp, SGDm, AdamW, SGD** |

**SGD is the largest level on `plateau5` and the smallest on `final_test`.** The paper's "factor
of 5.3" is 2.3 / 1.7 / 10.9 on the other three. On `best_test` the four levels span a 0.17 pp
band that no pair of them resolves.

### 1.5 (d) — which cell drops on `final_test`, and why

**`bm2 (SGD)`.** Derived: `D = −0.0733`, `se = 0.5000`, `t = −0.15`.

The six runs, all admissible, all 100/100 epochs:

| arm | run | plateau5 | best_test | final_test |
|---|---|---|---|---|
| uniform `chunk777` | `bm2-sgd-ch-s3` | 92.162 | 92.85 | 91.31 |
| | `bm2-sgd-ch-s4` | 92.064 | 92.92 | 92.22 |
| | `bm2-sgd-ch-s5` | 92.316 | 92.92 | 91.95 |
| aligned `nodewise` | `bm2-sgd-node-s3` | 91.288 | 92.41 | 91.13 |
| | `bm2-sgd-node-s4` | 91.138 | 92.58 | 92.58 |
| | `bm2-sgd-node-s5` | 91.182 | 92.39 | 91.99 |

Arm means and within-arm sds:

| | uniform mean | uniform sd | nodewise mean | nodewise sd | D | se | t |
|---|---|---|---|---|---|---|---|
| `plateau5` | 92.1807 | 0.1270 | 91.2027 | 0.0771 | +0.9780 | 0.0858 | **+11.40** |
| `final_test` | 91.8267 | 0.4674 | 91.9000 | 0.7292 | −0.0733 | 0.5000 | **−0.15** |

**It is a resolution loss, not a reversal.** `final_test` is a single epoch's evaluation; the
within-arm sd of that one reading inflates 3.7× (uniform) and 9.5× (nodewise) relative to
`plateau5`, the cell's se inflates **5.83×** (0.0858 → 0.5000), and |D| lands well inside one se.
On the identical six runs `plateau5` reads +0.978 ± 0.086, `t` 11.40 — **the most resolved cell in
Table 2**. The paper reports it as the 19/20 exception, explicitly *not* as a counter-example,
and prints the se-inflation arithmetic so a referee can check that reading.

The resolution loss is corpus-wide, not peculiar to `bm2`: cells resolved at `t ≥ 3` go
18 → 20 → 11 → 7 of 20 across `plateau5`, `plateau`, `best_test`, `final_test`, and the rms
measurement se on `final_test` is 2.48× `plateau5`'s.

### 1.6 What Contribution 1 actually survives

* sign: **20/20, 20/20, 20/20, 19/20**;
* pooled level: positive and of one order on all four endpoints, **+0.396 to +0.614 pp**;
* the sole negative cell is unresolved (`t = −0.15`), not reversed.

Contribution 1 is the part that does not depend on the endpoint. Contribution 3 is not.

### 1.7 Command that re-derives everything above

```
python3 analysis/c98_reproduce.py --metricsens --no-census
```
→ `ALL 70 CHECKS PASS.` (run 2026-09-02 against `results/all_runs.csv`, 2,173 rows, 1,731
admissible.)

---

## 2. Code change already applied — `analysis/c98_reproduce.py`

Three edits, all made:

1. **House-rule docstring**, so the metric ban is not silently broken. Replaced
   `  * \`plateau5\` is the only accuracy metric read; the \`plateau\` column is banned.`
   with a five-line statement that `plateau5` remains the only **primary**, and that the
   metric-sensitivity section reads all four columns side by side as a **disclosure**, making none
   of them primary.
2. **New section** `metricsens` (`MS_METRICS`, `_arm_on`, `_cells_on`, `METRIC_TABLE`,
   `METRIC_LEVELS`, `METRIC_SPREAD`, `METRIC_RANK`, `def metricsens`), inserted immediately before
   the `# --- the census, ASSERTED not measured` banner. 70 `chk()` sites: pool D and se, Q, τ,
   between-base Q, share, D>0 count, t≥3 count, rms se, sd(D) and all four level pools **per
   endpoint**, plus the level spread factor and an exact rank-order string comparison, plus the
   `bm2 (SGD)` se-inflation block.
3. **`SECTIONS`**: `("metricsens", metricsens)` inserted **before** `("censuscheck", censuscheck)`,
   which must stay last because it freezes `CENSUS_MARK`.

### 2.1 KNOWN CONSEQUENCE — the §3.4 census triple moves, by design

`censuscheck` now FAILS, exactly as its own comment says it should:

```
chk() assertion sites executed      353 | paper 283 | **FAIL**
distinct quantity-numerals asserted 231 | paper 216 | **FAIL**
distinct quantity-numerals in draft 747 | paper 747 | PASS
coverage of distinct quantity-numerals 30.9 | paper 28.9 | **FAIL**
```

That is not a broken result; it is the audit reporting that §3.4's coverage sentence has gone
stale because this package widened the audit. **This is a cross-package interaction with the F2
package and must be resolved by whoever lands last, not by me** — the triple depends on both the
new assertions (mine) and the new §4.4 prose (mine) and on F2's own §3.4 rewrite, and it must be
iterated to a fixpoint after *all* packages have landed:

```
python3 analysis/c98_reproduce.py --census        # read the printed triple
# copy it into CENSUS_PAPER in analysis/c98_reproduce.py AND into the §3.4 sentence
# in BOTH paper/paper.tex and paper/DRAFT-v4.md, then re-run until fixpoint
```

Measured on a scratch copy of `DRAFT-v4.md` with **only** this package's manuscript edits
applied, the triple lands at **assertions 353, covered 256, distinct 775, pct 33.0%**, and it
reaches that fixpoint in one iteration (writing the new triple into §3.4 does not move it again).
**Provisional**: other packages are moving the draft concurrently, so the integrator must re-run
the loop above rather than paste these four numbers.

---

## 3. Replacement text for `paper/paper.tex`

Four edits. Every anchor below was verified **verbatim and unique** (`str.count(...) == 1`)
against `paper/paper.tex` at the time of writing. Re-verify before applying: other packages are
editing the same file.

---

### TEX EDIT 1 — §4.4, insert the endpoint block (anchor: end of "Say which denominator.")

**ANCHOR (unique, count 1) — lines 1604–1607:**

```
earlier versions of this work quoted. All are true of different denominators; none may be quoted
without naming its own.

\paragraph{What we may not conclude from the direction.}
```

**REPLACE WITH:**

```latex
earlier versions of this work quoted. All are true of different denominators; none may be quoted
without naming its own.

\paragraph{The endpoint, varied --- and the part of this subsection that does not survive it.}
Everything above is computed on \plateau{}, and \S\ref{sec:metric} concedes, as the sixth of its
selection items, that \plateau{} was made primary \emph{after} the 20-epoch column produced two
withdrawn headlines: the choice has a mechanical justification, it has been applied uniformly
since, and \textbf{it was not fixed before the first analysis}. A decomposition of between-cell
heterogeneity is a statement about a \emph{spread}, and a spread is a property of the endpoint at
least as much as of the runs. We therefore re-derive this entire subsection on the three other
end-of-training endpoints the deposited run table already carries --- the 20-epoch
\texttt{plateau} column, the best test epoch \texttt{best\_test}, and the last test epoch
\texttt{final\_test} --- holding the admissibility gate of \eqref{eq:adm}, the arm definitions,
the \texttt{dup\_group} collapse and the fourteen-cell pool \textbf{fixed}, and varying only the
column that is read. This is not \S\ref{sec:threats} T10, which varies the row filter at a fixed
endpoint; it is the other axis, and no previous version of this paper reported the decomposition
on any endpoint but \plateau{}.

\begin{center}
\footnotesize
\begin{tabular}{@{}lrrrrrrr@{}}
\toprule
endpoint & pooled $\Dstat$ & $Q$ / 13 df & $p$ & $\tau$ &
  between-base $Q$ & share & $\Dstat > 0$ \\
\midrule
\plateau{} \emph{(primary)}         & $+0.530 \pm 0.029$ & 102.47 & $5.5\times10^{-16}$ & 0.295 & 95.12 & \textbf{92.8\%} & 20 / 20 \\
\texttt{plateau} \emph{(20-epoch)}  & $+0.449 \pm 0.024$ &  29.37 & 0.0058              & 0.101 & 18.36 & 62.5\%          & 20 / 20 \\
\texttt{best\_test}                 & $+0.396 \pm 0.025$ &   \textbf{9.87} & \textbf{0.70} & \textbf{0.000} & 3.70 & 37.5\% & 20 / 20 \\
\texttt{final\_test}                & $+0.614 \pm 0.043$ &  39.91 & $1.4\times10^{-4}$  & 0.251 & 34.66 & 86.8\%          & \textbf{19 / 20} \\
\bottomrule
\end{tabular}
\end{center}
\noindent\emph{Columns: pooled $\Dstat$ in pp over the fourteen cells; Cochran $Q$ on 13 df with
its $p$; DerSimonian--Laird $\tau$ in pp; the between-base component of $Q$ on 3 df; its share of
$Q$; and how many of the twenty count-matched cells of Table~\ref{tab:D} are positive.}

\noindent The same four endpoints, split by base optimiser --- the table this subsection is built
on, recomputed three more times:

\begin{center}
\small
\begin{tabular}{@{}lrrrrl@{}}
\toprule
endpoint & SGD & RMSProp & SGDm & AdamW & rank order, largest to smallest \\
\midrule
\plateau{} \emph{(primary)}        & $+1.000$ & $+0.720$ & $+0.556$ & $+0.189$ & SGD, RMSProp, SGDm, AdamW \\
\texttt{plateau} \emph{(20-epoch)} & $+0.737$ & $+0.634$ & $+0.438$ & $+0.315$ & SGD, RMSProp, SGDm, AdamW \\
\texttt{best\_test}                & $+0.432$ & $+0.386$ & $+0.411$ & $+0.261$ & SGD, SGDm, RMSProp, AdamW \\
\texttt{final\_test}               & $+0.139$ & $+1.518$ & $+0.588$ & $+0.420$ & \textbf{RMSProp, SGDm, AdamW, SGD} \\
\bottomrule
\end{tabular}
\end{center}

Three readings, stated plainly rather than buried.

\begin{enumerate}
\item \textbf{On \texttt{best\_test} there is no heterogeneity to decompose at all.} $Q = 9.87$ on
  13 df is \emph{below its own degrees of freedom}: $p = 0.70$, $I^2 = 0\%$, DerSimonian--Laird
  $\tau = 0.000$, and between base optimisers $Q$ is 3.70 on 3 df ($p = 0.30$). This is not an
  error-inflation artefact --- \texttt{best\_test}'s rms measurement $\se$ over the fourteen cells
  is 0.137 pp against \plateau{}'s 0.143 pp, within 5\% --- it is that the between-cell spread is
  gone: the sd of the fourteen $\Dstat$ is 0.084 pp on \texttt{best\_test} against 0.255 pp on
  \plateau{}, i.e.\ \emph{smaller than the measurement error}. On that endpoint the base-optimiser
  decomposition is not a weaker result. It is not a result.
\item \textbf{The base-level ordering inverts between \plateau{} and \texttt{final\_test}.} SGD is
  the largest of the four levels on \plateau{} ($+1.000$) and the \emph{smallest} on
  \texttt{final\_test} ($+0.139$), while RMSProp moves from second to first. The factor of 5.3
  quoted above is 2.3 on the 20-epoch column, 1.7 on \texttt{best\_test} --- where the four levels
  sit inside a 0.17 pp band that no pair of them resolves --- and 10.9 on \texttt{final\_test}.
  The momentum / second-moment $2 \times 2$ of the next paragraph is a reading of the \plateau{}
  ordering and does not survive either single-epoch endpoint.
\item \textbf{The endpoint this project chose is the one on which the decomposition is
  strongest.} A referee is entitled to write that sentence, so we write it first: of the four,
  \plateau{} maximises $Q$, maximises $\tau$ and maximises the between-base share.
\end{enumerate}

\textbf{What survives the change of endpoint is \S\ref{sec:primary}'s measurement, not this
subsection's decomposition.} The fourteen-cell pool is positive and of one order on all four
($+0.396$ to $+0.614$ pp), and the count-matched sign result of Table~\ref{tab:D} reads
\textbf{20 / 20, 20 / 20, 20 / 20 and 19 / 20} cells. The single exception is \arm{bm2} (SGD) on
\texttt{final\_test}: $\Dstat = -0.073 \pm 0.500$, $t = -0.15$. \textbf{That is a cell the
endpoint cannot read, not a cell that reverses.} \texttt{final\_test} is one epoch's evaluation,
and inside \arm{bm2}'s two arms the sd of that single reading is 0.467 and 0.729 pp against 0.127
and 0.077 pp for \plateau{}, so the cell's $\se$ inflates 5.8-fold, from 0.086 to 0.500 pp, and
$|\Dstat|$ falls well inside it; on the same six runs \plateau{} reads $+0.978 \pm 0.086$,
$t\ 11.40$, the most resolved cell in Table~\ref{tab:D}. The resolution loss is corpus-wide and
not peculiar to that cell: of the twenty, 18 are resolved at $t \ge 3$ on \plateau{} and 20 on the
20-epoch column, against 11 on \texttt{best\_test} and 7 on \texttt{final\_test}, and the rms
measurement $\se$ on \texttt{final\_test} is $2.5\times$ \plateau{}'s. \textbf{The sign is what
survives; the resolution and the decomposition are not endpoint-free.}

\paragraph{The conditional form, which is the form this claim should have carried from the start.}
\S\ref{sec:contributions}'s third contribution is therefore not ``the heterogeneity in $\Dstat$
has a base-optimiser structure''. It is:

\begin{quote}
\textbf{On the 5-epoch plateau endpoint --- an endpoint this project chose after seeing data
(\S\ref{sec:metric}, selection item 6) --- the heterogeneity in $\Dstat$ has a base-optimiser
structure accounting for 92.8\% of Cochran $Q$. On the last-epoch endpoint that structure is
weaker but present (86.8\%), with the level ordering inverted. On the best-epoch endpoint there
is no heterogeneity to decompose.}
\end{quote}

We are not arguing that \plateau{} is wrong and one of the others right, and \textbf{we do not
change the primary metric}: \plateau{} has the mechanical justification \S\ref{sec:metric} gives,
it is the endpoint every other number in this paper is computed on, and switching endpoint to suit
a claim is precisely the failure mode \S\ref{sec:metric-column} records this project committing
twice. The defect these two tables repair is a \emph{silence}. Until this draft
\texttt{best\_test} and \texttt{final\_test} appeared in this paper only as column names in
\S\ref{sec:repro}'s schema listing, so a reader had no way to learn that the third contribution is
conditional on a post-hoc choice while the first is not. \S\ref{sec:threats} T10 carries the
pointer, and every number in both tables is asserted by
\texttt{python3 analysis/c98\_reproduce.py -{}-metricsens}.

\paragraph{What we may not conclude from the direction.}
```

---

### TEX EDIT 2 — §1.1, Contribution 1 gains its endpoint-survival clause

**ANCHOR (unique, count 1) — lines 241–245:**

```
\item \textbf{A count-matched isolation of the group-size distribution from the group count}
  in meta-learned step sizes, replicated in 20 within-batch cells across three networks,
  2 datasets, 4 base optimisers and 2 meta-optimisers (\S\ref{sec:primary}--\S\ref{sec:rule11},
  Table~\ref{tab:D}, Figure~\ref{fig:forest}).
```

**REPLACE WITH:**

```latex
\item \textbf{A count-matched isolation of the group-size distribution from the group count}
  in meta-learned step sizes, replicated in 20 within-batch cells across three networks,
  2 datasets, 4 base optimisers and 2 meta-optimisers (\S\ref{sec:primary}--\S\ref{sec:rule11},
  Table~\ref{tab:D}, Figure~\ref{fig:forest}). \textbf{This is the part of the paper that does not
  depend on the endpoint we chose}: re-derived on all four end-of-training columns the corpus
  carries, the sign holds in 20 / 20 cells on \plateau{}, 20 / 20 on the 20-epoch column, 20 / 20
  on \texttt{best\_test} and 19 / 20 on \texttt{final\_test}, and the pooled level stays between
  $+0.396$ and $+0.614$ pp. The one exception is unresolved rather than reversed --- \arm{bm2}
  (SGD) at $-0.073 \pm 0.500$, $t\ -0.15$, a cell whose $\se$ inflates 5.8-fold on a single-epoch
  reading (\S\ref{sec:moderator}).
```

---

### TEX EDIT 3 — §1.1, Contribution 3 restated as conditional

**ANCHOR (unique, count 1) — the last line of Contribution 3, line 268:**

```
  (\S\ref{sec:moderator}, Figure~\ref{fig:moderator}).
```

**REPLACE WITH:**

```latex
  (\S\ref{sec:moderator}, Figure~\ref{fig:moderator}). \textbf{And that it is conditional on the
  endpoint}, which \S\ref{sec:metric} concedes was chosen after seeing data: recomputed on the
  three other end-of-training columns the corpus carries, the base-optimiser share is 86.8\% on
  \texttt{final\_test} with the level ordering \emph{inverted} (SGD moves from the largest level
  to the smallest), 62.5\% on the 20-epoch column, and on \texttt{best\_test} there is no
  heterogeneity to decompose at all ($Q\ 9.87$ on 13 df, $p\ 0.70$, $\tau = 0.000$, $I^2 = 0\%$).
  Of the four endpoints, the one this project chose is the one on which the decomposition is
  strongest. We disclose that rather than change the primary metric.
```

---

### TEX EDIT 4 — §7 T10 gains the endpoint axis

**ANCHOR (unique, count 1) — lines 3297–3300:**

```
\paragraph{T10 --- Filter sensitivity.}
Several quantities in this corpus move by 0.5--0.7 pp between two defensible row filters. Every
number here is re-derived at write time under the single stated gate (Eq.~\ref{eq:adm}), and we
recommend the same discipline to anyone reusing the data.
```

**REPLACE WITH:**

```latex
\paragraph{T10 --- Filter sensitivity, and endpoint sensitivity.}
Several quantities in this corpus move by 0.5--0.7 pp between two defensible row filters. Every
number here is re-derived at write time under the single stated gate (Eq.~\ref{eq:adm}), and we
recommend the same discipline to anyone reusing the data. \textbf{That is the row axis. The
endpoint axis is separate and, for one of our three headline claims, larger}, and
\S\ref{sec:moderator} now reports it in full: recomputed on the four end-of-training columns of
the deposited run table with the row filter and the cell set held fixed, the base-optimiser
decomposition accounts for 92.8\% of Cochran $Q$ on \plateau{}, 86.8\% on \texttt{final\_test}
with the level ordering inverted, 62.5\% on the 20-epoch column, and on \texttt{best\_test} it
accounts for nothing, because $Q = 9.87$ on 13 df ($p\ 0.70$, $\tau = 0.000$) leaves no
heterogeneity to decompose. \textbf{The count-matched sign result of \S\ref{sec:primary} survives
all four} (20 / 20, 20 / 20, 20 / 20, 19 / 20 cells, the exception unresolved at $t\ -0.15$ rather
than reversed); the decomposition does not. \plateau{} remains the primary and we do not switch to
whichever endpoint flatters a claim --- the disclosure is the repair.
```

---

### TEX EDIT 5 — §9 Conclusion, two clauses

**5a. ANCHOR (unique, count 1) — line 3665:**

```
survives conditioning on it only at $\Delta Q$ 4.11 on 2 df, $p$ 0.13. A registered replication
```

**REPLACE WITH:**

```latex
survives conditioning on it only at $\Delta Q$ 4.11 on 2 df, $p$ 0.13. It is also conditional on
the endpoint, and \S\ref{sec:moderator} says so where it is stated: on \texttt{best\_test} the
same fourteen cells are homogeneous ($Q\ 9.87$ / 13 df, $p\ 0.70$, $\tau\ 0.000$) and there is
nothing to decompose, and on \texttt{final\_test} the level ordering inverts --- whereas the
count-matched sign result above holds on all four endpoints the corpus carries (20 / 20, 20 / 20,
20 / 20, 19 / 20 cells). The measurement survives the choice of endpoint; the moderator does not.
A registered replication
```

**5b. ANCHOR (unique, count 1) — lines 3699–3701:**

```
measurement in twenty cells; a candidate moderator for its heterogeneity, replicated at all four of
its levels and homogeneous inside each, and still not separated from the batch identity it
co-varies with; a single-batch bounded null that excludes the mechanism most people would guess as
```

**REPLACE WITH:**

```latex
measurement in twenty cells, robust to all four end-of-training endpoints; a candidate moderator
for its heterogeneity, replicated at all four of
its levels and homogeneous inside each, still not separated from the batch identity it
co-varies with, and conditional on an endpoint we chose after seeing data;
a single-batch bounded null that excludes the mechanism most people would guess as
```

---

## 4. Replacement text for `paper/DRAFT-v4.md`

Same five edits. Anchors verified verbatim and unique against `paper/DRAFT-v4.md`.

---

### MD EDIT 1 — §4.4, insert the endpoint block

**ANCHOR (unique, count 1) — lines 1224–1226:**

```
quoted. All are true of different denominators; none may be quoted without naming its own.

**What we may not conclude from the direction.**
```

**REPLACE WITH:**

```markdown
quoted. All are true of different denominators; none may be quoted without naming its own.

**The endpoint, varied — and the part of this subsection that does not survive it.** Everything
above is computed on `plateau5`, and §3.3 concedes, as the sixth of its selection items, that
`plateau5` was made primary *after* the 20-epoch column produced two withdrawn headlines: the
choice has a mechanical justification, it has been applied uniformly since, and **it was not fixed
before the first analysis**. A decomposition of between-cell heterogeneity is a statement about a
*spread*, and a spread is a property of the endpoint at least as much as of the runs. We therefore
re-derive this entire subsection on the three other end-of-training endpoints the deposited run
table already carries — the 20-epoch `plateau` column, the best test epoch `best_test`, and the
last test epoch `final_test` — holding the admissibility gate of Eq. 11, the arm definitions, the
`dup_group` collapse and the fourteen-cell pool **fixed**, and varying only the column that is
read. This is not §7 T10, which varies the row filter at a fixed endpoint; it is the other axis,
and no previous version of this paper reported the decomposition on any endpoint but `plateau5`.

| endpoint | pooled D (pp) | Q / 13 df | p | τ (pp) | between-base Q / 3 df | share of Q | cells D > 0 |
|---|---|---|---|---|---|---|---|
| `plateau5` *(primary)* | +0.530 ± 0.029 | 102.47 | 5.5e−16 | 0.295 | 95.12 | **92.8%** | 20 / 20 |
| `plateau` *(20-epoch)* | +0.449 ± 0.024 | 29.37 | 0.0058 | 0.101 | 18.36 | 62.5% | 20 / 20 |
| `best_test` | +0.396 ± 0.025 | **9.87** | **0.70** | **0.000** | 3.70 | 37.5% | 20 / 20 |
| `final_test` | +0.614 ± 0.043 | 39.91 | 1.4e−4 | 0.251 | 34.66 | 86.8% | **19 / 20** |

The same four endpoints, split by base optimiser — the table this subsection is built on,
recomputed three more times:

| endpoint | SGD | RMSProp | SGDm | AdamW | rank order, largest to smallest |
|---|---|---|---|---|---|
| `plateau5` *(primary)* | +1.000 | +0.720 | +0.556 | +0.189 | SGD, RMSProp, SGDm, AdamW |
| `plateau` *(20-epoch)* | +0.737 | +0.634 | +0.438 | +0.315 | SGD, RMSProp, SGDm, AdamW |
| `best_test` | +0.432 | +0.386 | +0.411 | +0.261 | SGD, SGDm, RMSProp, AdamW |
| `final_test` | +0.139 | +1.518 | +0.588 | +0.420 | **RMSProp, SGDm, AdamW, SGD** |

Three readings, stated plainly rather than buried.

1. **On `best_test` there is no heterogeneity to decompose at all.** Q = 9.87 on 13 df is *below
   its own degrees of freedom*: p = 0.70, I² = 0%, DerSimonian–Laird τ = 0.000, and between base
   optimisers Q is 3.70 on 3 df (p = 0.30). This is not an error-inflation artefact — `best_test`'s
   rms measurement se over the fourteen cells is 0.137 pp against `plateau5`'s 0.143 pp, within
   5% — it is that the between-cell spread is gone: the sd of the fourteen D is 0.084 pp on
   `best_test` against 0.255 pp on `plateau5`, i.e. *smaller than the measurement error*. On that
   endpoint the base-optimiser decomposition is not a weaker result. It is not a result.
2. **The base-level ordering inverts between `plateau5` and `final_test`.** SGD is the largest of
   the four levels on `plateau5` (+1.000) and the *smallest* on `final_test` (+0.139), while
   RMSProp moves from second to first. The factor of 5.3 quoted above is 2.3 on the 20-epoch
   column, 1.7 on `best_test` — where the four levels sit inside a 0.17 pp band that no pair of
   them resolves — and 10.9 on `final_test`. The momentum / second-moment 2 × 2 of the next
   paragraph is a reading of the `plateau5` ordering and does not survive either single-epoch
   endpoint.
3. **The endpoint this project chose is the one on which the decomposition is strongest.** A
   referee is entitled to write that sentence, so we write it first: of the four, `plateau5`
   maximises Q, maximises τ and maximises the between-base share.

**What survives the change of endpoint is §4.3's measurement, not this subsection's
decomposition.** The fourteen-cell pool is positive and of one order on all four (+0.396 to
+0.614 pp), and the count-matched sign result of Table 2 reads **20 / 20, 20 / 20, 20 / 20 and
19 / 20** cells. The single exception is `bm2` (SGD) on `final_test`: D = −0.073 ± 0.500,
t = −0.15. **That is a cell the endpoint cannot read, not a cell that reverses.** `final_test` is
one epoch's evaluation, and inside `bm2`'s two arms the sd of that single reading is 0.467 and
0.729 pp against 0.127 and 0.077 pp for `plateau5`, so the cell's se inflates 5.8-fold, from 0.086
to 0.500 pp, and |D| falls well inside it; on the same six runs `plateau5` reads +0.978 ± 0.086,
t 11.40, the most resolved cell in Table 2. The resolution loss is corpus-wide and not peculiar to
that cell: of the twenty, 18 are resolved at t ≥ 3 on `plateau5` and 20 on the 20-epoch column,
against 11 on `best_test` and 7 on `final_test`, and the rms measurement se on `final_test` is
2.5× `plateau5`'s. **The sign is what survives; the resolution and the decomposition are not
endpoint-free.**

**The conditional form, which is the form this claim should have carried from the start.** §1.1's
third contribution is therefore not "the heterogeneity in D has a base-optimiser structure". It
is:

> **On the 5-epoch plateau endpoint — an endpoint this project chose after seeing data (§3.3,
> selection item 6) — the heterogeneity in D has a base-optimiser structure accounting for 92.8%
> of Cochran Q. On the last-epoch endpoint that structure is weaker but present (86.8%), with the
> level ordering inverted. On the best-epoch endpoint there is no heterogeneity to decompose.**

We are not arguing that `plateau5` is wrong and one of the others right, and **we do not change
the primary metric**: `plateau5` has the mechanical justification §3.3 gives, it is the endpoint
every other number in this paper is computed on, and switching endpoint to suit a claim is
precisely the failure mode §6.2 records this project committing twice. The defect these two tables
repair is a *silence*. Until this draft `best_test` and `final_test` appeared in this paper only
as column names in §8's schema listing, so a reader had no way to learn that the third
contribution is conditional on a post-hoc choice while the first is not. §7 T10 carries the
pointer, and every number in both tables is asserted by
`python3 analysis/c98_reproduce.py --metricsens`.

**What we may not conclude from the direction.**
```

---

### MD EDIT 2 — §1.1, Contribution 1

**ANCHOR (unique, count 1) — lines 158–160:**

```
1. **A count-matched isolation of the group-size distribution from the group count** in
   meta-learned step sizes, replicated in 20 within-batch cells across three networks, 2 datasets,
   4 base optimisers and 2 meta-optimisers (§4.3–§4.5, Table 2, Figure 1).
```

**REPLACE WITH:**

```markdown
1. **A count-matched isolation of the group-size distribution from the group count** in
   meta-learned step sizes, replicated in 20 within-batch cells across three networks, 2 datasets,
   4 base optimisers and 2 meta-optimisers (§4.3–§4.5, Table 2, Figure 1). **This is the part of
   the paper that does not depend on the endpoint we chose**: re-derived on all four
   end-of-training columns the corpus carries, the sign holds in 20 / 20 cells on `plateau5`,
   20 / 20 on the 20-epoch column, 20 / 20 on `best_test` and 19 / 20 on `final_test`, and the
   pooled level stays between +0.396 and +0.614 pp. The one exception is unresolved rather than
   reversed — `bm2` (SGD) at −0.073 ± 0.500, t −0.15, a cell whose se inflates 5.8-fold on a
   single-epoch reading (§4.4).
```

---

### MD EDIT 3 — §1.1, Contribution 3

**ANCHOR (unique, count 1) — line 178:**

```
   survives conditioning on batch only at ΔQ 4.11 on 2 df, p 0.13 (§4.4, Figure 2).
```

**REPLACE WITH:**

```markdown
   survives conditioning on batch only at ΔQ 4.11 on 2 df, p 0.13 (§4.4, Figure 2). **And that it
   is conditional on the endpoint**, which §3.3 concedes was chosen after seeing data: recomputed
   on the three other end-of-training columns the corpus carries, the base-optimiser share is
   86.8% on `final_test` with the level ordering *inverted* (SGD moves from the largest level to
   the smallest), 62.5% on the 20-epoch column, and on `best_test` there is no heterogeneity to
   decompose at all (Q 9.87 on 13 df, p 0.70, τ = 0.000, I² = 0%). Of the four endpoints, the one
   this project chose is the one on which the decomposition is strongest. We disclose that rather
   than change the primary metric.
```

---

### MD EDIT 4 — §7 T10

**ANCHOR (unique, count 1) — lines 2604–2606:**

```
**T10 — Filter sensitivity.** Several quantities in this corpus move by 0.5–0.7 pp between two
defensible row filters. Every number here is re-derived at write time under the single stated gate
(Eq. 11), and we recommend the same discipline to anyone reusing the data.
```

**REPLACE WITH:**

```markdown
**T10 — Filter sensitivity, and endpoint sensitivity.** Several quantities in this corpus move by
0.5–0.7 pp between two defensible row filters. Every number here is re-derived at write time under
the single stated gate (Eq. 11), and we recommend the same discipline to anyone reusing the data.
**That is the row axis. The endpoint axis is separate and, for one of our three headline claims,
larger**, and §4.4 now reports it in full: recomputed on the four end-of-training columns of the
deposited run table with the row filter and the cell set held fixed, the base-optimiser
decomposition accounts for 92.8% of Cochran Q on `plateau5`, 86.8% on `final_test` with the level
ordering inverted, 62.5% on the 20-epoch column, and on `best_test` it accounts for nothing,
because Q = 9.87 on 13 df (p 0.70, τ = 0.000) leaves no heterogeneity to decompose. **The
count-matched sign result of §4.3 survives all four** (20 / 20, 20 / 20, 20 / 20, 19 / 20 cells,
the exception unresolved at t −0.15 rather than reversed); the decomposition does not. `plateau5`
remains the primary and we do not switch to whichever endpoint flatters a claim — the disclosure
is the repair.
```

---

### MD EDIT 5 — §9 Conclusion, two clauses

**5a. ANCHOR (unique, count 1) — lines 2894–2895:**

```
identity accounts for 95.8% of the same Q, and the base optimiser survives conditioning on it only
at ΔQ 4.11 on 2 df, p 0.13. A registered replication (`bm2`) gave the SGD and RMSProp levels a
```

**REPLACE WITH:**

```markdown
identity accounts for 95.8% of the same Q, and the base optimiser survives conditioning on it only
at ΔQ 4.11 on 2 df, p 0.13. It is also conditional on the endpoint, and §4.4 says so where it is
stated: on `best_test` the same fourteen cells are homogeneous (Q 9.87 / 13 df, p 0.70, τ 0.000)
and there is nothing to decompose, and on `final_test` the level ordering inverts — whereas the
count-matched sign result above holds on all four endpoints the corpus carries (20 / 20, 20 / 20,
20 / 20, 19 / 20 cells). The measurement survives the choice of endpoint; the moderator does not.
A registered replication (`bm2`) gave the SGD and RMSProp levels a
```

**5b. ANCHOR (unique, count 1) — lines 2924–2927:**

```
The honest description of this paper is therefore: **a robust, replicated, count-matched
measurement in twenty cells; a candidate moderator for its heterogeneity, replicated at all four
of its levels and homogeneous inside each, and still not separated from the batch identity it
co-varies with; a single-batch bounded null that excludes the mechanism most people would guess as
```

**REPLACE WITH:**

```markdown
The honest description of this paper is therefore: **a robust, replicated, count-matched
measurement in twenty cells, robust to all four end-of-training endpoints; a candidate moderator
for its heterogeneity, replicated at all four
of its levels and homogeneous inside each, still not separated from the batch identity it
co-varies with, and conditional on an endpoint we chose after seeing data;
a single-batch bounded null that excludes the mechanism most people would guess as
```

---

## 5. What this package deliberately does NOT do

* **It does not switch the primary metric.** `plateau5` stays primary; the `plateau` column stays
  banned as a primary. Task item (e).
* **It does not soften any existing claim's wording without a number behind it.** Every clause
  added carries a re-derived figure, and every one of those figures is asserted in code.
* **It does not touch §7 T10's row-filter content**, only extends it with the orthogonal axis and
  a pointer.
* **It does not touch the abstract** (G2/G4 packages own it). If the abstract's 92.8% survives
  their rewrite, one clause there would be worth adding on a later pass; that is flagged, not
  done.
* **It does not resolve the §3.4 census triple**, which now needs a post-merge fixpoint pass —
  see §2.1 above.

## 6. Open / for another package

* **§3.4 census fixpoint.** Mandatory after all packages land. Command in §2.1.
* **Abstract.** Currently attributes heterogeneity to base optimiser with no endpoint caveat; a
  one-clause conditional would match the new §1.1 C3. Left to the abstract package.
* **Figure 2 caption** (`fig:moderator`) still reads as if 92.8% were endpoint-free. A one-sentence
  caption addition pointing at §4.4's endpoint table would close that; not done here to avoid
  racing the figure package.
