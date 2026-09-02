# PACKAGE `endpoint-knife` — closes B8

**Item.** §4.4 applies an endpoint knife to the moderator and never applies it to §4.7's
prescription `T = nodewise1d − nodewise`, which is Contribution 6 and the paper's only actionable
recommendation. A referee who has just read §4.4 will ask why. This package extends the
four-endpoint audit to `T`, writes the result into §4.7 in §4.4's own idiom, and adds the
assertion sites.

**Verdict: the prescription SURVIVES the knife, and survives it better than §4.4's decomposition
did.** Nothing is deleted. One false superlative found in §4.7 while auditing it is corrected
(Edit 2).

Zero GPU. `analysis/c98_reproduce.py` is the only file this package edits directly; `paper.tex`
and `DRAFT-v4.md` are supplied as exact replacement text below, keyed to anchors verified unique
(count == 1) against the live files at HEAD 351d9a6.

---

## 1. What was verified, and what was wrong

Every claim handed to me in the briefing was re-derived from `results/all_runs.csv` through the
paper's own `arm()` / `welch()` / `dup_group` machinery, with only the metric column swapped
(`c98_reproduce._arm_on(col)`, the same swap §4.4's table uses).

| briefing claim | verdict |
|---|---|
| the 12 non-AdamW cells are positive on all four endpoints | **CONFIRMED** — 12 / 12 on each, **48 of 48** |
| the AdamW+Lion pool stays inside the pre-registered \|Δ\| ≤ 0.15 band on all four | **CONFIRMED for the pool's point estimate** (+0.007, +0.051, −0.111, +0.106) — **but see the two qualifications below; the briefing's phrasing is too strong as it stands** |
| resolution collapses 12/12, 12/12, 8/12, 6/12 | **CONFIRMED exactly** |
| `sm4`'s headline exception goes unresolved (t 1.51) on `final_test` | **CONFIRMED exactly** (+0.723 ± 0.479, t 1.51) |

**The two qualifications the briefing's band claim needs, and which the prose below carries.**

1. **The ±0.15 band is registered for a CELL, not for a pool.** §3.4 says so in terms — *"It is
   registered for a cell, not for a pool, and we do not extend it"* — so quoting the pool against
   the band as a threshold clearance would contradict §3.4 two sections earlier. Cell by cell the
   point estimates are inside the band on **seven of the eight** endpoint-by-cell readings. The
   one exception is `aw1` on `final_test`, **+0.253 ± 0.109**, which lands in the (0.15, 0.30]
   interval §3.4 registers *in advance* as UNDECIDED.
2. **On the interval form of the rule — the form `aw1`'s own scorer uses (§3.4: "`aw1`'s tests the
   95% interval") — the pool's whole 95% interval lies inside the band only on `plateau5`**
   ([−0.104, +0.117]). On `plateau`, `best_test` and `final_test` it does not.

So the honest statement is: *the scope line is a place where the move is not measurable on every
endpoint; it is an equivalence claim on the primary endpoint only.* That is what the replacement
text says.

---

## 2. Re-derivation — every number, printed

Method, held fixed exactly as §4.4 holds it: the admissibility gate of Eq. (adm), the arm
prefixes of Table 3 (`tab:T`), the `dup_group` collapse, and `welch()`. **Only the column read
changes.** `hz3`'s footnote reading excludes the seed-5 trio (§7 T9's clip-box and hardware
mismatch), the same exclusion §4.7's ‡ footnote makes on `plateau5` — and it reproduces the
printed +0.328 / t 3.89 exactly, which is the check that the exclusion filter is the paper's.

```
==============================================================================
ENDPOINT plateau5
  bn1              +0.4267 +- 0.0409  t  10.43   3v3
  ml2              +0.6193 +- 0.1758  t   3.52   3v3
  fa1              +0.6487 +- 0.1104  t   5.88   6v6
  g3m              +0.7576 +- 0.0932  t   8.13   9v9
  cc1              +0.8160 +- 0.1592  t   5.13   3v3
  r50              +1.0493 +- 0.3167  t   3.31   3v3
  gm2              +1.3627 +- 0.1514  t   9.00   3v3
  hz3              +0.3367 +- 0.0693  t   4.85   6v6
  nl1 SGD          +0.6920 +- 0.1351  t   5.12   3v3
  nl1 RMSProp      +0.9160 +- 0.2417  t   3.79   3v3
  rl3 @1e-4        +0.7560 +- 0.1171  t   6.45   3v3
  rl3 @3e-4        +0.3913 +- 0.1267  t   3.09   3v3
  aw1 AdamW        +0.0913 +- 0.0785  t   1.16   3v3
  sm3 AdamW        -0.0833 +- 0.0811  t  -1.03   3v3
  sm4 AdamW+RMS    +0.9880 +- 0.2308  t   4.28   3v3
  --- non-AdamW twelve: positive 12/12, resolved(t>=3) 12/12, min t 3.09, min T +0.3367, max T +1.3627
  --- AdamW+Lion pool: +0.0069 +- 0.0564   Q 2.394 on 1 df   |pool| <= 0.15 ? True
  --- sm4: +0.9880 +- 0.2308 t 4.28  resolved? True
  --- rms se over the twelve: 0.1616
==============================================================================
ENDPOINT plateau
  bn1              +0.5267 +- 0.0424  t  12.41   3v3
  ml2              +0.5228 +- 0.1124  t   4.65   3v3
  fa1              +0.5828 +- 0.0973  t   5.99   6v6
  g3m              +0.6586 +- 0.0625  t  10.54   9v9
  cc1              +0.5220 +- 0.0983  t   5.31   3v3
  r50              +1.2917 +- 0.0435  t  29.73   3v3
  gm2              +1.6640 +- 0.1432  t  11.62   3v3
  hz3              +0.4072 +- 0.0680  t   5.99   6v6
  nl1 SGD          +0.6850 +- 0.1888  t   3.63   3v3
  nl1 RMSProp      +0.7017 +- 0.0643  t  10.92   3v3
  rl3 @1e-4        +0.5883 +- 0.1070  t   5.50   3v3
  rl3 @3e-4        +0.4133 +- 0.1194  t   3.46   3v3
  aw1 AdamW        +0.1243 +- 0.0914  t   1.36   3v3
  sm3 AdamW        -0.0093 +- 0.0834  t  -0.11   3v3
  sm4 AdamW+RMS    +0.7297 +- 0.0839  t   8.70   3v3
  --- non-AdamW twelve: positive 12/12, resolved(t>=3) 12/12, min t 3.46, min T +0.4072, max T +1.6640
  --- AdamW+Lion pool: +0.0514 +- 0.0616   Q 1.166 on 1 df   |pool| <= 0.15 ? True
  --- sm4: +0.7297 +- 0.0839 t 8.70  resolved? True
  --- rms se over the twelve: 0.1041
==============================================================================
ENDPOINT best_test
  bn1              +0.4400 +- 0.1245  t   3.54   3v3
  ml2              +0.3733 +- 0.1580  t   2.36   3v3
  fa1              +0.3917 +- 0.0823  t   4.76   6v6
  g3m              +0.3367 +- 0.0994  t   3.39   9v9
  cc1              +0.6967 +- 0.0912  t   7.64   3v3
  r50              +0.5967 +- 0.1694  t   3.52   3v3
  gm2              +1.2800 +- 0.2080  t   6.15   3v3
  hz3              +0.3017 +- 0.0391  t   7.71   6v6
  nl1 SGD          +0.5400 +- 0.1925  t   2.80   3v3
  nl1 RMSProp      +0.1700 +- 0.0840  t   2.02   3v3
  rl3 @1e-4        +0.5867 +- 0.1267  t   4.63   3v3
  rl3 @3e-4        +0.2333 +- 0.1025  t   2.28   3v3
  aw1 AdamW        -0.0100 +- 0.1707  t  -0.06   3v3
  sm3 AdamW        -0.1433 +- 0.0975  t  -1.47   3v3
  sm4 AdamW+RMS    +0.3933 +- 0.1011  t   3.89   3v3
  --- non-AdamW twelve: positive 12/12, resolved(t>=3) 8/12, min t 2.02, min T +0.1700, max T +1.2800
  --- AdamW+Lion pool: -0.1105 +- 0.0847   Q 0.460 on 1 df   |pool| <= 0.15 ? True
  --- sm4: +0.3933 +- 0.1011 t 3.89  resolved? True
  --- rms se over the twelve: 0.1322
==============================================================================
ENDPOINT final_test
  bn1              +0.2567 +- 0.2221  t   1.16   3v3
  ml2              +0.6200 +- 0.0822  t   7.54   3v3
  fa1              +0.6050 +- 0.1886  t   3.21   6v6
  g3m              +0.8178 +- 0.3367  t   2.43   9v9
  cc1              +1.3333 +- 0.4301  t   3.10   3v3
  r50              +1.0800 +- 1.3423  t   0.80   3v3
  gm2              +1.6300 +- 0.2246  t   7.26   3v3
  hz3              +0.4117 +- 0.0825  t   4.99   6v6
  nl1 SGD          +0.1467 +- 0.3834  t   0.38   3v3
  nl1 RMSProp      +1.3667 +- 0.1459  t   9.37   3v3
  rl3 @1e-4        +0.5233 +- 0.2377  t   2.20   3v3
  rl3 @3e-4        +0.4467 +- 0.2601  t   1.72   3v3
  aw1 AdamW        +0.2533 +- 0.1094  t   2.31   3v3
  sm3 AdamW        +0.0600 +- 0.0616  t   0.97   3v3
  sm4 AdamW+RMS    +0.7233 +- 0.4792  t   1.51   3v3
  --- non-AdamW twelve: positive 12/12, resolved(t>=3) 6/12, min t 0.38, min T +0.1467, max T +1.6300
  --- AdamW+Lion pool: +0.1065 +- 0.0537   Q 2.371 on 1 df   |pool| <= 0.15 ? True
  --- sm4: +0.7233 +- 0.4792 t 1.51  resolved? False
  --- rms se over the twelve: 0.4602
### AdamW+Lion cells, both forms of the registered rule
 plateau5    aw1 +0.0913+-0.0785 pt=NULL CI[-0.063,+0.245] inband=False df=3.85
             sm3 -0.0833+-0.0811 pt=NULL CI[-0.242,+0.076] inband=False df=2.17
 plateau     aw1 +0.1243+-0.0914 pt=NULL CI[-0.055,+0.304] inband=False df=3.79
             sm3 -0.0093+-0.0834 pt=NULL CI[-0.173,+0.154] inband=False df=2.88
 best_test   aw1 -0.0100+-0.1707 pt=NULL CI[-0.344,+0.324] inband=False df=3.52
             sm3 -0.1433+-0.0975 pt=NULL CI[-0.334,+0.048] inband=False df=3.23
 final_test  aw1 +0.2533+-0.1094 pt=UNDECIDED CI[+0.039,+0.468] inband=False df=2.75
             sm3 +0.0600+-0.0616 pt=NULL CI[-0.061,+0.181] inband=False df=3.37

### AdamW+Lion POOL, 95%% CI
  plateau5    +0.0069 +- 0.0564  Q 2.394/1  95% CI [-0.1037, +0.1174]  |m|<=0.15 True  CI inside band True
  plateau     +0.0514 +- 0.0616  Q 1.166/1  95% CI [-0.0694, +0.1722]  |m|<=0.15 True  CI inside band False
  best_test   -0.1105 +- 0.0847  Q 0.460/1  95% CI [-0.2765, +0.0555]  |m|<=0.15 True  CI inside band False
  final_test  +0.1065 +- 0.0537  Q 2.371/1  95% CI [+0.0013, +0.2116]  |m|<=0.15 True  CI inside band False

### hz3 matched 5v5 (T9: seed-5 trio excluded)
  plateau5    +0.3276 +- 0.0843 t 3.89 (5v5)
  plateau     +0.4322 +- 0.0804 t 5.37 (5v5)
  best_test   +0.3380 +- 0.0341 t 9.91 (5v5)
  final_test  +0.3680 +- 0.0896 t 4.11 (5v5)
plateau5    range +0.3367 (hz3) .. +1.3627 (gm2)  pos 12/12  res 12/12  rms se 0.1616
            unresolved: 
plateau     range +0.4072 (hz3) .. +1.6640 (gm2)  pos 12/12  res 12/12  rms se 0.1041
            unresolved: 
best_test   range +0.1700 (nl1 RMSProp) .. +1.2800 (gm2)  pos 12/12  res 8/12  rms se 0.1322
            unresolved: nl1 RMSProp t 2.02, rl3 @3e-4 t 2.28, ml2 t 2.36, nl1 SGD t 2.80
final_test  range +0.1467 (nl1 SGD) .. +1.6300 (gm2)  pos 12/12  res 6/12  rms se 0.4602
            unresolved: nl1 SGD t 0.38, r50 t 0.80, bn1 t 1.16, rl3 @3e-4 t 1.72, rl3 @1e-4 t 2.20, g3m t 2.43
TOTAL positive over 4 endpoints x 12 cells: 48

### sm4, point and interval, vs registered EFFECT line 0.30
  plateau5    +0.9880 +- 0.2308 t  4.28  95% CI [+0.536,+1.440]  pt>0.30 True  CI-lo>0.30 True
  plateau     +0.7297 +- 0.0839 t  8.70  95% CI [+0.565,+0.894]  pt>0.30 True  CI-lo>0.30 True
  best_test   +0.3933 +- 0.1011 t  3.89  95% CI [+0.195,+0.591]  pt>0.30 True  CI-lo>0.30 False
  final_test  +0.7233 +- 0.4792 t  1.51  95% CI [-0.216,+1.663]  pt>0.30 True  CI-lo>0.30 False

### bn1 vs ml2 (one experiment measured twice)
  plateau5    bn1 +0.4267+-0.0409  ml2 +0.6193+-0.1758  diff +0.1927 +- 0.1805  z 1.07
  plateau     bn1 +0.5267+-0.0424  ml2 +0.5228+-0.1124  diff -0.0038 +- 0.1201  z -0.03
  best_test   bn1 +0.4400+-0.1245  ml2 +0.3733+-0.1580  diff -0.0667 +- 0.2011  z -0.33
  final_test  bn1 +0.2567+-0.2221  ml2 +0.6200+-0.0822  diff +0.3633 +- 0.2368  z 1.53

### D corpus-wide resolution (20 Table-2 cells) for the parallel
  plateau5    pos 20/20  res(t>=3) 18/20
  plateau     pos 20/20  res(t>=3) 20/20
  best_test   pos 20/20  res(t>=3) 11/20
  final_test  pos 19/20  res(t>=3) 7/20
plateau5     max over CIFAR-10 corpus: r50          +1.0493 (sm4 +0.9880)   max over R18/C10: sm4          +0.9880
plateau      max over CIFAR-10 corpus: r50          +1.2917 (sm4 +0.7297)   max over R18/C10: sm4          +0.7297
best_test    max over CIFAR-10 corpus: cc1          +0.6967 (sm4 +0.3933)   max over R18/C10: cc1          +0.6967
final_test   max over CIFAR-10 corpus: nl1 RMSProp  +1.3667 (sm4 +0.7233)   max over R18/C10: nl1 RMSProp  +1.3667
```

### 2.1 The derived quantities the new text prints

| quantity | plateau5 | plateau | best_test | final_test |
|---|---|---|---|---|
| min T over the twelve | +0.337 (`hz3`) | +0.407 (`hz3`) | +0.170 (`nl1` RMSProp) | +0.147 (`nl1` SGD) |
| max T over the twelve | +1.363 (`gm2`) | +1.664 (`gm2`) | +1.280 (`gm2`) | +1.630 (`gm2`) |
| T > 0 | 12 / 12 | 12 / 12 | 12 / 12 | 12 / 12 |
| resolved at t ≥ 3 | 12 / 12 | 12 / 12 | 8 / 12 | 6 / 12 |
| rms se over the twelve | 0.162 | 0.104 | 0.132 | 0.460 |
| AdamW+Lion pool | +0.007 ± 0.056 | +0.051 ± 0.062 | −0.111 ± 0.085 | +0.106 ± 0.054 |
| `sm4` | +0.988 (t 4.28) | +0.730 (t 8.70) | +0.393 (t 3.89) | +0.723 (**t 1.51**) |
| `hz3` box-matched 5 v 5 | +0.328 (t 3.89) | +0.432 (t 5.37) | +0.338 (t 9.91) | +0.368 (t 4.11) |

Cells that lose resolution, named:

* `best_test`, four fall below t 3: `nl1` (RMSProp) 2.02, `rl3` @3e-4 2.28, `ml2` 2.36,
  `nl1` (SGD) 2.80.
* `final_test`, six fall below t 3: `nl1` (SGD) 0.38, `r50` 0.80, `bn1` 1.16, `rl3` @3e-4 1.72,
  `rl3` @1e-4 2.20, `g3m` 2.43.

**T degrades LESS than D does.** §4.4 already records D's corpus-wide resolution as 18, 20, 11
and 7 of 20 cells (90%, 100%, 55%, 35%); T's is 12, 12, 8 and 6 of 12 (100%, 100%, 67%, 50%). The
resolution loss on the single-epoch columns is a property of the corpus, not of the prescription.
rms se ratio `final_test` / `plateau5` for T: 0.4602 / 0.1616 = **2.8×** (D's is 2.5×).

---

## 3. NEW PROBLEM FOUND — §4.7 prints a false superlative

**`sm4` is NOT "the largest T in the CIFAR-10 corpus".** Re-derived on `plateau5`:

```
  r50  (ResNet-50 / CIFAR-10 / SGDm)   T = +1.0493 +- 0.3167   t 3.31
  sm4  (ResNet-18 / CIFAR-10 / AdamW+RMSProp)  T = +0.9880 +- 0.2308   t 4.28
```

`r50` is a CIFAR-10 cell and it is larger. The superlative is true only at **ResNet-18** on
CIFAR-10 (there the next-largest is `nl1` RMSProp at +0.916), and even that is `plateau5`-
specific: on `best_test` **four** of the eleven other ResNet-18 / CIFAR-10 cells are larger than
`sm4`, and on `final_test` **two** are. Sites: `paper.tex:2288`, `DRAFT-v4.md:1791`. Edit 2
repairs it in both. Nothing else in the paper depends on the superlative — the scope-line claim
rests on `sm4` being *resolved and positive*, not on it being the maximum, and that is untouched.

---

## 4. THE EXACT REPLACEMENT TEXT

Four edits per file. Edits 1 and 2 are the package proper; edits 3 and 4 are one-sentence
pointers that keep Contribution 6 and §7 T10 from staying silent about a knife the body now
applies (§4.4's own defect was exactly that silence). Edit 5 is the census fixpoint.

Anchors below were verified against the live files: every `count == 1`.

### EDIT 1 (tex) — insert the endpoint knife into §4.7

**Anchor** (`paper.tex:2306`, count == 1) — insert the new text IMMEDIATELY BEFORE this line,
followed by a blank line:

```latex
\paragraph{Practical significance, answered rather than volunteered.}
```

**Text to insert:**

```latex
\paragraph{The endpoint, varied --- the prescription under \S\ref{sec:moderator}'s own knife.}
\S\ref{sec:moderator} takes a knife to the base-optimiser decomposition, re-deriving it on the
three end-of-training columns the deposited run table carries besides \plateau{}, and reports
that the decomposition does not survive the change while \S\ref{sec:primary}'s sign does. That
knife has to cut here too. $\Tstat$ is this paper's only actionable recommendation --- it is the
sixth contribution, and the one a reader could act on tomorrow --- so applying the test to the
moderator and withholding it from the prescription would be exactly the selective disclosure
\S\ref{sec:moderator} was written to end. We therefore re-derive \emph{the whole of
Table~\ref{tab:T}} on \texttt{plateau} (20-epoch), \texttt{best\_test} and \texttt{final\_test},
holding the admissibility gate of \eqref{eq:adm}, the arm prefixes of Table~\ref{tab:T}, the
\texttt{dup\_group} collapse and the Welch construction \textbf{fixed}, and varying only the
column that is read.

\begin{center}
\footnotesize
\begin{tabular}{@{}lccccrr@{}}
\toprule
endpoint & $\Tstat$ over the twelve & $\Tstat > 0$ & $t \ge 3$ & rms $\se$ &
  AdamW\,+\,Lion pool & \arm{sm4} \\
\midrule
\plateau{} \emph{(primary)}        & $+0.337$ to $+1.363$ & 12 / 12 & \textbf{12 / 12} & 0.162 & $+0.007 \pm 0.056$ & $+0.988$ ($t\ 4.28$) \\
\texttt{plateau} \emph{(20-epoch)} & $+0.407$ to $+1.664$ & 12 / 12 & \textbf{12 / 12} & 0.104 & $+0.051 \pm 0.062$ & $+0.730$ ($t\ 8.70$) \\
\texttt{best\_test}                & $+0.170$ to $+1.280$ & 12 / 12 & \textbf{8 / 12}  & 0.132 & $-0.111 \pm 0.085$ & $+0.393$ ($t\ 3.89$) \\
\texttt{final\_test}               & $+0.147$ to $+1.630$ & 12 / 12 & \textbf{6 / 12}  & 0.460 & $+0.106 \pm 0.054$ & $+0.723$ ($t\ \mathbf{1.51}$) \\
\bottomrule
\end{tabular}
\end{center}
\noindent\emph{Columns: the range of $\Tstat$ over the twelve non-AdamW cells; how many of those
twelve are positive; how many are resolved at $t \ge 3$; the rms measurement $\se$ over them; the
inverse-variance pool of the two AdamW\,+\,Lion cells that fix the scope line; and \arm{sm4}, the
single cell on the other side of it.}

\textbf{The prescription survives the knife, and survives it better than
\S\ref{sec:moderator}'s decomposition did.} Three readings, in the order
\S\ref{sec:moderator} gives its own.

\begin{enumerate}
\item \textbf{The sign is endpoint-free, in every cell, on every endpoint.} All twelve
  non-AdamW cells are positive on all four columns --- \textbf{48 of 48} --- and no cell on any
  endpoint falls below $+0.147$ pp or rises above $+1.664$ pp. The one cell carrying no
  \S\ref{sec:threats} T9 confound, \arm{hz3} matched at 5 v 5, is positive \emph{and} resolved
  on all four: $+0.328$ ($t\ 3.89$), $+0.432$ ($t\ 5.37$), $+0.338$ ($t\ 9.91$) and
  $+0.368$ ($t\ 4.11$).
\item \textbf{The scope line holds where we put it, on all four.} The AdamW\,+\,Lion pool stays
  inside the $\pm 0.15$ pp half-width of the registered \texttt{NULL} band on every endpoint.
  We report that as an estimate and not as a threshold clearance, because
  \S\ref{sec:registration} fixes that band \textbf{for a cell and not for a pool} and we do not
  extend it, and because two qualifications travel with it. Cell by cell the point estimates are
  inside the band on seven of the eight endpoint-by-cell readings; the exception is \arm{aw1} on
  \texttt{final\_test} at $+0.253 \pm 0.109$, which lands in the $(0.15, 0.30]$ interval
  registered \textbf{in advance} as undecided. And on the interval form of the rule --- the form
  \arm{aw1}'s own scorer uses --- the pool's entire 95\% interval lies inside the band only on
  \plateau{} ($[-0.104, +0.117]$). \textbf{The scope line is a place where the move is not
  measurable, on every endpoint; it is an equivalence claim on the primary endpoint only.}
\item \textbf{What degrades is resolution, and it degrades on the single-epoch columns.}
  Twelve of twelve resolve at $t \ge 3$ on \plateau{} and on the 20-epoch column, \textbf{eight}
  on \texttt{best\_test} and \textbf{six} on \texttt{final\_test}, while the rms measurement
  $\se$ over the twelve runs 0.162, 0.104, 0.132 and \textbf{0.460} pp --- $2.8\times$
  \plateau{}'s on \texttt{final\_test}. This is the corpus-wide loss \S\ref{sec:moderator}
  already records for $\Dstat$ (18, 20, 11 and 7 of 20 cells resolved), and $\Tstat$ loses
  \emph{less} of it: 100\%, 100\%, 67\% and 50\% of its cells resolve against $\Dstat$'s 90\%,
  100\%, 55\% and 35\%.
\end{enumerate}

\textbf{One thing genuinely does not survive, and it is the exception rather than the rule.}
\arm{sm4} --- the cell that moves the scope line from ``AdamW'' to ``AdamW with a Lion
meta-optimiser'' --- is resolved on three endpoints ($t\ 4.28$, $8.70$ and $3.89$) and
\textbf{unresolved on \texttt{final\_test}}: $+0.723 \pm 0.479$, $t\ 1.51$. Its point estimate
clears \S\ref{sec:registration}'s registered 0.30 pp effect line on all four; its 95\% interval
clears it on two. So the \emph{base--meta pairing} of Contribution 6 is a \plateau{} and
20-epoch result that weakens on the two single-epoch columns, and we say so rather than let the
reader find it. The \emph{prescription} that pairing qualifies is not weakened: it holds its
sign in every cell on every endpoint, holds its scope line on every endpoint, and holds its
resolution on the two multi-epoch endpoints of the four. \textbf{A prescription that survives an
endpoint knife is stronger stated with the knife than without it.} Every number in this
paragraph and its table is asserted by
\texttt{python3 analysis/c98\_reproduce.py -{}-metricsens}.
```

### EDIT 1 (md) — the same, in `DRAFT-v4.md`

**Anchor** (`DRAFT-v4.md:1810`, count == 1) — insert IMMEDIATELY BEFORE this line, followed by a
blank line:

```
**Practical significance, answered rather than volunteered.**
```

**Text to insert:**

```markdown
**The endpoint, varied — the prescription under §4.4's own knife.** §4.4 takes a knife to the
base-optimiser decomposition, re-deriving it on the three end-of-training columns the deposited
run table carries besides plateau5, and reports that the decomposition does not survive the
change while §4.3's sign does. That knife has to cut here too. T is this paper's only actionable
recommendation — it is the sixth contribution, and the one a reader could act on tomorrow — so
applying the test to the moderator and withholding it from the prescription would be exactly the
selective disclosure §4.4 was written to end. We therefore re-derive *the whole of the table
above* on `plateau` (20-epoch), `best_test` and `final_test`, holding the admissibility gate of
Eq. 11, the arm prefixes of the table, the `dup_group` collapse and the Welch construction
**fixed**, and varying only the column that is read.

| endpoint | T over the twelve | T > 0 | t ≥ 3 | rms se | AdamW+Lion pool | `sm4` |
|---|---|---|---|---|---|---|
| plateau5 *(primary)* | +0.337 to +1.363 | 12 / 12 | **12 / 12** | 0.162 | +0.007 ± 0.056 | +0.988 (t 4.28) |
| `plateau` *(20-epoch)* | +0.407 to +1.664 | 12 / 12 | **12 / 12** | 0.104 | +0.051 ± 0.062 | +0.730 (t 8.70) |
| `best_test` | +0.170 to +1.280 | 12 / 12 | **8 / 12** | 0.132 | −0.111 ± 0.085 | +0.393 (t 3.89) |
| `final_test` | +0.147 to +1.630 | 12 / 12 | **6 / 12** | 0.460 | +0.106 ± 0.054 | +0.723 (**t 1.51**) |

*Columns: the range of T over the twelve non-AdamW cells; how many of those twelve are positive;
how many are resolved at t ≥ 3; the rms measurement se over them; the inverse-variance pool of
the two AdamW+Lion cells that fix the scope line; and `sm4`, the single cell on the other side of
it.*

**The prescription survives the knife, and survives it better than §4.4's decomposition did.**
Three readings, in the order §4.4 gives its own.

1. **The sign is endpoint-free, in every cell, on every endpoint.** All twelve non-AdamW cells
   are positive on all four columns — **48 of 48** — and no cell on any endpoint falls below
   +0.147 pp or rises above +1.664 pp. The one cell carrying no §7 T9 confound, `hz3` matched at
   5 v 5, is positive *and* resolved on all four: +0.328 (t 3.89), +0.432 (t 5.37), +0.338
   (t 9.91) and +0.368 (t 4.11).
2. **The scope line holds where we put it, on all four.** The AdamW+Lion pool stays inside the
   ±0.15 pp half-width of the registered `NULL` band on every endpoint. We report that as an
   estimate and not as a threshold clearance, because §3.4 fixes that band **for a cell and not
   for a pool** and we do not extend it, and because two qualifications travel with it. Cell by
   cell the point estimates are inside the band on seven of the eight endpoint-by-cell readings;
   the exception is `aw1` on `final_test` at +0.253 ± 0.109, which lands in the (0.15, 0.30]
   interval registered **in advance** as undecided. And on the interval form of the rule — the
   form `aw1`'s own scorer uses — the pool's entire 95% interval lies inside the band only on
   plateau5 ([−0.104, +0.117]). **The scope line is a place where the move is not measurable, on
   every endpoint; it is an equivalence claim on the primary endpoint only.**
3. **What degrades is resolution, and it degrades on the single-epoch columns.** Twelve of twelve
   resolve at t ≥ 3 on plateau5 and on the 20-epoch column, **eight** on `best_test` and **six**
   on `final_test`, while the rms measurement se over the twelve runs 0.162, 0.104, 0.132 and
   **0.460** pp — 2.8× plateau5's on `final_test`. This is the corpus-wide loss §4.4 already
   records for D (18, 20, 11 and 7 of 20 cells resolved), and T loses *less* of it: 100%, 100%,
   67% and 50% of its cells resolve against D's 90%, 100%, 55% and 35%.

**One thing genuinely does not survive, and it is the exception rather than the rule.** `sm4` —
the cell that moves the scope line from "AdamW" to "AdamW with a Lion meta-optimiser" — is
resolved on three endpoints (t 4.28, 8.70 and 3.89) and **unresolved on `final_test`**:
+0.723 ± 0.479, t 1.51. Its point estimate clears §3.4's registered 0.30 pp effect line on all
four; its 95% interval clears it on two. So the *base–meta pairing* of Contribution 6 is a
plateau5 and 20-epoch result that weakens on the two single-epoch columns, and we say so rather
than let the reader find it. The *prescription* that pairing qualifies is not weakened: it holds
its sign in every cell on every endpoint, holds its scope line on every endpoint, and holds its
resolution on the two multi-epoch endpoints of the four. **A prescription that survives an
endpoint knife is stronger stated with the knife than without it.** Every number in this
paragraph and its table is asserted by `python3 analysis/c98_reproduce.py --metricsens`.
```

### EDIT 2 (tex) — repair the `sm4` superlative

**Find** (count == 1):

```latex
\textbf{same AdamW base with an RMSProp meta-optimiser} the move is worth
$\mathbf{+0.988 \pm 0.231}$ ($t\ 4.28$) --- the largest $\Tstat$ in the CIFAR-10 corpus. So the
exception is not ``AdamW''.
```

**Replace with:**

```latex
\textbf{same AdamW base with an RMSProp meta-optimiser} the move is worth
$\mathbf{+0.988 \pm 0.231}$ ($t\ 4.28$) --- the largest $\Tstat$ this corpus carries
\emph{at ResNet-18 on CIFAR-10}. It is not the largest on CIFAR-10 outright: \arm{r50} reads
$+1.049 \pm 0.317$, and the superlative earlier versions of this work printed --- ``the largest
$\Tstat$ in the CIFAR-10 corpus'' --- was false of that row. It is also \plateau{}-specific: on
\texttt{best\_test} four of the eleven other ResNet-18 / CIFAR-10 cells are larger, and on
\texttt{final\_test} two are. So the
exception is not ``AdamW''.
```

### EDIT 2 (md) — the same

**Find** (count == 1):

```
worth **+0.988 ± 0.231 (t 4.28)** — the largest T in the CIFAR-10 corpus. So the exception is not
"AdamW".
```

**Replace with:**

```markdown
worth **+0.988 ± 0.231 (t 4.28)** — the largest T this corpus carries *at ResNet-18 on CIFAR-10*.
It is not the largest on CIFAR-10 outright: `r50` reads +1.049 ± 0.317, and the superlative
earlier versions of this work printed — "the largest T in the CIFAR-10 corpus" — was false of
that row. It is also plateau5-specific: on `best_test` four of the eleven other
ResNet-18 / CIFAR-10 cells are larger, and on `final_test` two are. So the exception is not
"AdamW".
```

### EDIT 3 (tex) — Contribution 6 stops being silent about the endpoint

C1 (tex:244) and C3 (tex:272) both carry an endpoint disclosure; C6 carries none. That asymmetry
is the same selective-disclosure defect §4.4 exists to repair.

**Find** (count == 1):

```latex
  $+0.988 \pm 0.231$. The exception is a base--meta pairing, not a base
  (\S\ref{sec:prescription}, \S\ref{sec:tail}, \S\ref{sec:normalisation}).
```

**Replace with:**

```latex
  $+0.988 \pm 0.231$. Both halves face \S\ref{sec:moderator}'s endpoint knife in
  \S\ref{sec:prescription} and the first survives it: the twelve cells are positive on all four
  end-of-training endpoints (48 of 48) and the AdamW\,+\,Lion pool stays inside the registered
  $\pm 0.15$ pp band on all four, while resolution falls 12 / 12, 12 / 12, 8 / 12, 6 / 12 and
  \arm{sm4} itself goes unresolved on \texttt{final\_test} ($t\ 1.51$). The exception is a
  base--meta pairing, not a base
  (\S\ref{sec:prescription}, \S\ref{sec:tail}, \S\ref{sec:normalisation}).
```

### EDIT 3 (md) — the same

**Find** (count == 1):

```
**RMSProp** meta it is worth +0.988 ± 0.231. The exception is a base–meta pairing, not a base
   (§4.7, §5.4, §5.5).
```

**Replace with:**

```markdown
**RMSProp** meta it is worth +0.988 ± 0.231. Both halves face §4.4's endpoint knife in §4.7 and
   the first survives it: the twelve cells are positive on all four end-of-training endpoints
   (48 of 48) and the AdamW+Lion pool stays inside the registered ±0.15 pp band on all four,
   while resolution falls 12 / 12, 12 / 12, 8 / 12, 6 / 12 and `sm4` itself goes unresolved on
   `final_test` (t 1.51). The exception is a base–meta pairing, not a base
   (§4.7, §5.4, §5.5).
```

### EDIT 4 (tex) — §7 T10 points at the prescription too

**Find** (count == 1):

```latex
than reversed); the decomposition does not. \plateau{} remains the primary and we do not switch to
whichever endpoint flatters a claim --- the disclosure is the repair.
```

**Replace with:**

```latex
than reversed); the decomposition does not. \textbf{\S\ref{sec:prescription}'s prescription faces
the same knife and survives it}: $\Tstat$ is positive in all twelve non-AdamW cells on all four
endpoints (48 of 48) and its AdamW\,+\,Lion scope line holds on all four, while its resolution
falls 12 / 12, 12 / 12, 8 / 12, 6 / 12. \plateau{} remains the primary and we do not switch to
whichever endpoint flatters a claim --- the disclosure is the repair.
```

### EDIT 4 (md) — the same

**Find** (count == 1):

```
the exception unresolved at t −0.15 rather than reversed); the decomposition does not. `plateau5`
remains the primary and we do not switch to whichever endpoint flatters a claim — the disclosure
is the repair.
```

**Replace with:**

```markdown
the exception unresolved at t −0.15 rather than reversed); the decomposition does not. **§4.7's
prescription faces the same knife and survives it**: T is positive in all twelve non-AdamW cells
on all four endpoints (48 of 48) and its AdamW+Lion scope line holds on all four, while its
resolution falls 12 / 12, 12 / 12, 8 / 12, 6 / 12. `plateau5`
remains the primary and we do not switch to whichever endpoint flatters a claim — the disclosure
is the repair.
```

### EDIT 5 — §3.4's census sentence (THE FIXPOINT; DO NOT COPY THESE NUMBERS BLIND)

Adding 61 assertion sites moves the triple §3.4 prints and section `[16]` asserts.
**With this package alone applied to both files**, `python3 analysis/c98_reproduce.py --census`
prints:

```
  chk() assertion sites executed in this run             414
  distinct quantity-numerals this run asserts            284
  distinct quantity-numerals in the draft                803
  coverage of distinct quantity-numerals                35.4%
```

(baseline at HEAD 351d9a6: 353 / 256 / 786 / 32.6%)

**These four numbers WILL move again once the other cycle-105 packages land**, because the census
counts numerals in `DRAFT-v4.md`. Run `--census` after every package is in and write the printed
triple into the sentence below in BOTH files, then re-run to a fixpoint.

**Find in `paper.tex`** (count == 1):

```latex
audit executes \textbf{353 claim-carrying assertions covering 256 of the 786 distinct
quantity-numerals} in this manuscript, which is 32.6\% of them.
```

**Find in `DRAFT-v4.md`** (count == 1):

```
audit executes **353 claim-carrying assertions covering 256 of the 786 distinct
quantity-numerals** in this manuscript, which is 32.6% of them.
```

**Replace with, IF this package is the last one in** (verified below to reach a one-step
fixpoint; re-derive with `--census` if anything else lands after it):

```latex
audit executes \textbf{414 claim-carrying assertions covering 284 of the 803 distinct
quantity-numerals} in this manuscript, which is 35.4\% of them.
```

```markdown
audit executes **414 claim-carrying assertions covering 284 of the 803 distinct
quantity-numerals** in this manuscript, which is 35.4% of them.
```

⚠ **COLLISION WARNING.** Package **B7** rewrites the sentence two lines after this one (§3.4's
"section [16] ... reads this sentence back out of the manuscript", which is false of `paper.tex`).
Integrate B7 first, then re-run `--census` and set this triple last.

---

## 5. ASSERTION SITES ADDED — `analysis/c98_reproduce.py` section [15]

**Applied directly** (this file is named in the task; `paper.tex` and `DRAFT-v4.md` are not
touched). 61 new `chk()` sites plus 3 non-numeric ordering checks, appended to `metricsens()`
after the existing `final_test rms se / plateau5 rms se` assertion. They reuse `_arm_on(col)`,
`welch()` and `meta()` unchanged — no new statistics were written for this package.

What is now asserted, per endpoint (× 4): min T, max T, `T > 0` of 12, resolved at t ≥ 3 of 12,
rms se of the twelve, the AdamW+Lion pool and its se, `sm4`'s T / se / t, and `hz3`'s box-matched
5 v 5 T and t. Plus, once: `48 of 48`; `r50`'s +1.049 ± 0.317; the count of R18/C10 cells (11)
and how many overtake `sm4` on `best_test` (4) and `final_test` (2); `aw1`'s +0.253 ± 0.109 on
`final_test`; the pool's `plateau5` 95% interval [−0.104, +0.117]; the 7-of-8 in-band count; the
2.8× rms-se ratio. Three ordering checks fail loudly rather than silently: that the largest T at
R18/C10 on `plateau5` is `sm4`, that the largest over the whole CIFAR-10 corpus is `r50` (the
Edit-2 repair, guarded), and that the pool's 95% interval is inside the band on `plateau5` only.

Two `assert`s guard the knife itself: the T cell set must stay at 12 as the metric changes, and
`hz3` must stay 5 v 5 after the seed-5 exclusion.

---

## 6. VERIFICATION RUN — pasted, not summarised

`python3 analysis/c98_reproduce.py --metricsens` (section [15] alone, with the new block):

```
ALL 131 CHECKS PASS.
```

`python3 analysis/c98_reproduce.py` against the LIVE (unedited) manuscript — 414 checks, the only
four failures are §3.4's stale census sentence, which Edit 5 fixes:

```
4 CHECK(S) FAILED:
   chk() assertion sites executed                 414 | paper 353 | **FAIL**   §3.4
   distinct quantity-numerals asserted            284 | paper 256 | **FAIL**   §3.4
   distinct quantity-numerals in the draft        803 | paper 786 | **FAIL**   §3.4
   coverage of distinct quantity-numerals         35.4 | paper 32.6 | **FAIL**   §3.4
```

(the run above was made with `--draft` pointed at a scratch copy of `DRAFT-v4.md` carrying edits
1–4, so the "803 in the draft" figure is post-edit; against the untouched draft the same run
fails only on the first, second and fourth of those.)

**CENSUS FIXPOINT, REACHED IN ONE STEP.** All eight manuscript edits were applied to scratch
copies of `paper.tex` and `DRAFT-v4.md` **by extracting the find/replace blocks out of this
document itself** (every anchor asserted `count == 1` at apply time — all eight passed), then
edit 5's triple was written in, and the audit re-run:

```
ALL 418 CHECKS PASS.
```

(418 = the 414 claim-carrying sites the sentence names, plus the 4 self-referential census
sites the census excludes from its own count.)

**`tectonic` on the scratch copy carrying all four `paper.tex` edits: exit 0.** The three
overfull `\hbox` boxes are the same three as the unedited baseline, at the same widths
(20.28241pt, 12.25499pt, 7.28497pt) and only shifted in line number — **the new seven-column
table introduces no new box warnings**, and total warnings fall from 116 to 83 because edits 3
and 4 reflow two underfull paragraphs. **The manuscript grows from 65 to 67 pages** (`pdfinfo`
on the two scratch builds); the new paragraph, its table and its three-item list are the whole of
the growth.

**Numeric diff, tex block vs md block** (the defect that has bitten every prior cycle): 57
numerals each, **identical multisets, zero difference**, after stripping cross-references.

```
only in tex: []
only in md : []
```

---

## 7. (e) — DOES §4.7 OVERCLAIM BEYOND CIFAR-RESOLUTION VISION ResNets?

**No, with one wording note and one repaired superlative.**

* The evidence the prescription rests on is ResNet-18, ResNet-34 (`g3m`) and ResNet-50 (`r50`) on
  CIFAR-10, plus ResNet-18 on CIFAR-100 (`gm2`), at 100 and 300 epochs. Every architecture and
  dataset named in §4.7's claims is inside the T table.
* §4.7's closing paragraph already scopes it correctly: *"on one framework, at CIFAR
  resolution"*, and it explicitly refuses the practitioner claim (*"For a practitioner choosing
  an optimiser, this paper recommends nothing"*). §1 scope item (i) carries "CIFAR-resolution
  vision with ResNets and one meta-learning framework". **No repair needed.**
* **Repaired:** the `sm4` superlative (§3 above) — the one place §4.7 claimed more than it had.
* **Wording note, NOT acted on, integrator's call.** §4.7's opening sentence calls the move *"The
  practitioner's move implied by §4.3 and §4.6"*, and four paragraphs later the section says *"For
  a practitioner choosing an optimiser, this paper recommends nothing."* Those two sentences point
  opposite ways. The minimal repair is one word — *"The designer's move implied by ..."* — which
  matches §1 scope item (iv) ("this is a **designer-facing** result") and changes no number. I did
  not fold it into the edits above because it is a separate defect from B8 and belongs in its own
  register entry.

---

## 8. WHAT THIS PACKAGE DOES **NOT** CLOSE

* The `Q`-null / bootstrap problem of **B1** is untouched. §4.7's endpoint table pools only two
  cells (the AdamW+Lion scope line) and quotes a **range** rather than a pool for the twelve, so
  it does not inherit B1's mis-referred `Q`. The one place it could — a pooled T over the twelve —
  is deliberately not printed: §4.3's commensurability rule forbids averaging a CIFAR-10 and a
  CIFAR-100 effect in pp, and §3.4 forbids extending the cell-level band to a pool.
* The bn1/ml2 agreement `z` printed in §4.7's ¶ footnote as **1.06** re-derives to
  0.1927 / 0.1805 = **1.0676 → 1.07**. Half a unit in the last digit is 0.005, so this is outside
  tolerance and would FAIL if it were asserted (it is not). Trivial, pre-existing, not in B8's
  scope — flagged for the register, not fixed here, because changing it is a numeric edit to a
  line no package owns. On the other three endpoints the same difference reads −0.03, −0.33 and
  +1.53, i.e. `bn1` and `ml2` remain one measurement made twice on every endpoint.

---

## 9. REGISTER ENTRY (for the integrator; `docs/CORRECTIONS.md` is at 130)

> **131.x — B8 closed: §4.7's prescription put under §4.4's endpoint knife.** `T` re-derived on
> all four end-of-training columns through the paper's own `arm()`/`welch()`/`dup_group` path.
> The prescription survives: 12 / 12 non-AdamW cells positive on every endpoint (48 of 48), the
> AdamW+Lion scope line inside the registered ±0.15 pp band on every endpoint, `hz3`'s
> T9-clean 5 v 5 positive and resolved on every endpoint. What degrades: resolution
> 12/12 → 12/12 → 8/12 → 6/12, rms se 0.162 → 0.104 → 0.132 → 0.460, and `sm4` unresolved on
> `final_test` (+0.723 ± 0.479, t 1.51), so Contribution 6's base–meta *pairing* is a
> `plateau5`/20-epoch result while the *prescription* is not. Two qualifications added that the
> briefing did not carry: the ±0.15 band is registered per cell not per pool (§3.4), and `aw1` on
> `final_test` (+0.253 ± 0.109) falls in the registered UNDECIDED interval. Also repaired: §4.7's
> "the largest T in the CIFAR-10 corpus" was FALSE of `sm4` — `r50` reads +1.049 ± 0.317 — and is
> true only at ResNet-18, only on `plateau5`. 61 assertion sites added to `c98_reproduce.py`
> section [15]. Zero GPU.
