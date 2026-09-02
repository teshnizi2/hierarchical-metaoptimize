# PACKAGE `rp1-into-paper` — closing fold `rp1` in properly

Target files: `paper/paper.tex` and `paper/DRAFT-v4.md`. **Neither was edited by this package.**
Every edit below is given as an exact anchor plus exact replacement text, verified unique by
fixed-string count against the files at HEAD `2a499e4` (working tree clean except
`bin/c98_hz3_s5_box30.sh`, unrelated).

---

## 0. What was already true before this package, and what was not

`rp1` was **not** "still described as in flight" in the body. Commit `d1a714b` had already landed
the arm means, `T1`, `T1b`, `T2`, `T4`, `T5` and Appendix A.3b, and re-derivation below confirms
every one of those numbers. What was still wrong, and is what this package fixes:

| # | defect | where | task item |
|---|---|---|---|
| 1 | §3.5's heading and table caption say **two scored, two in flight**; the section's own next sentence says **three** have completed and been scored | `tex:920`, `tex:943-944`, `tex:931`; `md:726`, `md:733` | (f) |
| 2 | The demotion-to-UNDERDETERMINED clause is **attributed to the scorer**. It is not in the scorer: `UNDERDETERMINED` appears **zero** times in `analysis/c97_rp1_score.py` | `tex:978-982`, `tex:1053-1057`, `tex:1905-1907`; `md:759-762`, `md:820-824`, `md:1481-1483` | (b) |
| 3 | The **void first scorer run** (`V0 16/24` off eight stale mid-flight CSV rows) is disclosed **nowhere** in either manuscript | absent | (e) |
| 4 | The `T2` verdict is quoted as `THE PERMUTATION DRAW IS EXCHANGEABLE`, dropping the scorer's own qualifier `AT THIS RESOLUTION`; the block is labelled **verbatim** but is a condensation | `tex:1884`, `tex:1897`; `md:1459`, `md:1471` | (c) |
| 5 | The printed 95% CI is a **t interval on 5 df** and nothing says so. A reader applying 1.96 × 0.0791 gets 0.155, not the printed 0.203, and concludes the paper cannot multiply | `tex:1894`, `tex:1908`; `md:1469`, `md:1483` | (a) |
| 6 | A.3b states the disagreement but never says **what would settle it** | `tex:3791-3803`; `md:3007-3016` | (d) |
| 7 | The two files' §4.6.1 headings differ ("settles limit 2, doubles the power" vs "settles limits 2 and, partly, the power") | `tex:1865`, `md:1444` | sync |

**Deliberately out of scope**, because concurrent packages own them: the abstract (G2/G4 own the
255→230 word cut and the 67-word sentence; the abstract's `rp1` sentence at `tex:179-186` is
already correct and is left untouched), "sixteen"→"twenty" at `tex:1966` / `md:1535` inside §4.6.1's
last paragraph (S4 owns it — **this package does not touch that paragraph**), and `S2`'s "There is
no third" at `tex:1355` (S2 owns it, though `rp1` is the third contrast it denies).

---

## 1. Re-derivation of every number quoted or changed

Source: `results/all_runs.csv`, 2,173 rows, `plateau5` column (house rule: `plateau` is banned as
primary). 24 `rp1-` rows, all `epochs_done = 100`, all `complete = 1`, all `window_ok = 1`.
Re-derived independently of the scorer (own arithmetic, own incomplete-beta t and F tails), then
checked against the scorer's registered logic by reading `analysis/c97_rp1_score.py`.

```
rp1 rows: 24     seeds: [6, 7, 8, 9, 10, 11]
node   n=6 92.066 +-0.050
p101   n=6 92.053 +-0.050
p202   n=6 92.030 +-0.064
p303   n=6 92.059 +-0.050
per-seed d_s: -0.219, -0.179, +0.065, +0.052, +0.295, -0.125
A = -0.0184  se 0.0791  t -0.233 on 5 df     two-sided p = 0.8248
MDE normal 80%: 0.222        MDE t(5): 0.276
T2 draw     F(2,10) = 0.175   p = 0.8423
T2 run seed F(5,10) = 4.634   p = 0.0190
   sigma_draw^2 = -0.00114 -> truncated to 0.0000
   sigma_seed sd = 0.1000     sigma_resid sd = 0.0908
T3 p101 -0.013 +- 0.082 | p202 -0.036 +- 0.105 | p303 -0.007 +- 0.062 | spread 0.029
T4 se 0.0791 vs pp1 0.157 = 0.50x
D pooled: pp1 (3 v 3) 0.5807, cc1 (3 v 3) 0.7267  ->  +0.6537
A/D = -2.820%      CI/D = [-33.9%, +28.3%]      half of D = 0.3268
```

**Every landed number reproduces exactly — with one thing the manuscript never states.**

**The 95% CI is a *t* interval, not a normal one.** `score_T1b` (line 494) sets
`tcrit = t_quantile(0.95, df)` and `half = tcrit * se`. On 5 df that is
`2.570582 × 0.0791 = 0.2033`, giving `[-0.222, +0.185]` and `half/band = 0.2033/0.15 = 1.36`.
A reader applying the normal factor gets `1.95996 × 0.0791 = 0.155` and cannot reproduce the
printed bounds. The MDEs are the other way round: `mde_z = 2.801586 × se = 0.222` is the
**normal** approximation (the same constant that produced `pp1`'s quoted 0.440 at se 0.157), and
`mde_t = (t_.975,5 + t_.60,5) × se = (2.570582 + 0.919544) × 0.0791 = 0.276`. So the section
prints one *t* quantity and one normal quantity side by side without labelling either. **Edit
TEX-6b / MD-6b below fixes this.**

**Smallest resolvable draw sd.** `mde_sigma_perm = sqrt((F_crit(2,10) − 1) · MS_res / b)`
`= sqrt((4.1028 − 1) × 0.008245 / 6) = 0.0653 pp`. Confirms the printed 0.0653.

**`UNDERDETERMINED` appears zero times in the scorer.**

```
$ grep -ic "underdetermined" analysis/c97_rp1_score.py
0
$ grep -c "UNDERPOWERED" analysis/c97_rp1_score.py
5
$ md5 analysis/c97_rp1_score.py
7d21c4f5c16ccf25196fd6a5e6391fa9
$ python3 analysis/c97_rp1_score.py --selftest   ->   selftest: 147/147 PASS
```

The scorer's own demotion is `T1b`, whose three verdicts are `EQUIVALENT TO ZERO WITHIN ±0.15`,
`CONSISTENT WITH NULL, UNDERPOWERED` and `OUT OF BAND` (lines 501–514). The middle one fired. The
demotion to *underdetermined* exists only in this manuscript's own registration (`tex:978-981`,
`md:759-761`). The paper currently prints the two in the same breath — "The scorer additionally
prints…" — which reads as though the scorer carried both. It carried one.

**The scorer's `T2` verdict string is longer than what the paper quotes.** `score_T2` line 576:
`"THE PERMUTATION DRAW IS EXCHANGEABLE AT THIS RESOLUTION"`. The paper drops the last three words,
which are the ones that keep it a null-with-a-stated-resolution rather than a proof of zero.

**The void first run.** Recorded in `docs/CORRECTIONS.md` §129.2 (authoritative, highest-number-
wins) and nowhere in either manuscript: the first invocation of `c97_rp1_score.py` returned
`V0: 16/24`, eight probe directories reading `ep=86/100`, `84/100` and similar, against `.out`
tails that all 24 read `Epoch 99` + `RUN_DONE`. `gate_V0` reads `epochs_done` from the run table
(line 381), not from the probe, so the table was behind the disk. Eight rows —
`p101-s{10,11}`, `p202-s{9,10,11}`, `p303-s{9,10,11}` — had been ingested mid-flight. Note
`p202-s9` was at 98/100, which **passes** the `complete ≥ 95%` gate and so did not show in the
`complete = 0` count; that is why earlier drafts say **seven** stale rows in the attrition ledger
(`tex:3465`, `tex:3474`) and **eight** in §3.5. Both are right and both stay: seven were
*inadmissible*, eight were *stale*. Verified: `tex:649-651` already states "`rp1`'s eight
mid-flight snapshot rows … so seven of them now pass the `complete` gate."

**One number I deliberately do not carry into the manuscript.** CORRECTIONS §129.3 says
`args_repair.py --apply` writes **36** `dup_group` annotations. The CSV carries **42** non-empty
`dup_group` values, the difference being the name-collision groups `aggregate.py` writes itself. I
cannot separate the two without re-running the pipeline, so the replacement text below names the
step without asserting a count. **UNSURE on 36; the replacement prose does not use it.**

---

## 2. Edits to `paper/paper.tex`

Ten edits. Every OLD block below was confirmed to occur **exactly once** in `paper/paper.tex`.

### TEX-1 — §3.5 heading (item f) · `tex:920`

OLD
```latex
\subsection{Four pre-registered batches: two scored, two still in flight}
```
NEW
```latex
\subsection{Four pre-registered batches: three scored, one never started}
```

### TEX-2 — §3.5 opening paragraph, last clause (item f) · `tex:931`

OLD
```latex
can check that the two verdicts we did read are the ones we said we would read.
```
NEW
```latex
can check that the three verdicts we did read are the ones we said we would read.
```

### TEX-3 — Table~\ref{tab:inflight} caption (item f) · `tex:943-944`

OLD
```latex
\caption{The four pre-registered batches. Two have been scored by running their registered
scorers unedited; the other two contribute no number to this paper.}
```
NEW
```latex
\caption{The four pre-registered batches. Three have been scored by running their registered
scorers unedited; the fourth has never started and contributes no number to this paper.}
```

### TEX-4 — R1's registration, the ownership of the demotion (item b) · `tex:981-983`

OLD
```latex
null.} The scorer additionally prints \arm{pp1}'s registration defect (band half-width
$0.15 <$ realised $\se$ 0.157) whichever way the new data land.
```
NEW
```latex
null.} \textbf{That demotion is this manuscript's registration and not the scorer's, and we
correct our own earlier description of it here}: the string \texttt{UNDERDETERMINED} appears
\textbf{zero} times in \texttt{analysis/c97\_rp1\_score.py}. The scorer supplies the interval and
issues no such verdict. The demotion \emph{it} carries is \texttt{T1b}, which refuses to call any
\texttt{NULL} an equivalence claim unless the entire 95\% interval lies inside the $\pm 0.15$
band, and which prints \arm{pp1}'s registration defect (band half-width $0.15 <$ realised $\se$
0.157) whichever way the new data land. Two rules, two owners, both reported in
\S\ref{sec:rp1}: one of them fired and one of them did not, and it is not the one a reader would
guess.
```

### TEX-5 — R1's status paragraph: the void run and the two demotions (items b, e) · `tex:1047-1058`

OLD
```latex
\textbf{R1 is complete and scored.} All 24 \arm{rp1} runs reach 100 epochs in their own
\texttt{.out} series and all 24 now carry complete rows: eight of the twenty-four had been
ingested mid-flight and carried the partial epoch counts of that snapshot, and re-running
\texttt{analysis/aggregate.py} over the refreshed \texttt{.out} tree corrected exactly those eight
rows and \textbf{changed no other row in the corpus} (0 added, 0 removed, 0 other rows altered).
\texttt{analysis/c97\_rp1\_score.py} was then run \textbf{unedited} --- selftest 147/147 PASS ---
and its verdict is transcribed in \S\ref{sec:alignment}. The clause that binds us did \textbf{not}
fire: the interval does not span half of $\Dstat$, so the alignment leg is reported as a null and
not as underdetermined. That the demotion did not fire is a fact about the data, not a choice; the
arithmetic is printed in \S\ref{sec:alignment} so a reader can check it against the rule as
registered.
```
NEW
```latex
\textbf{R1 is complete and scored --- and the first attempt to score it is void.} All 24
\arm{rp1} runs reach 100 epochs in their own \texttt{.out} series. The \textbf{first} invocation
of \texttt{analysis/c97\_rp1\_score.py} nonetheless returned \texttt{V0: 16/24}, with eight probe
directories reading \texttt{ep=86/100}, \texttt{ep=84/100} and similar, against \texttt{.out}
tails on which all 24 read \texttt{Epoch 99} and \texttt{RUN\_DONE}. The scorer's \texttt{V0}
gate takes \texttt{epochs\_done} from the \textbf{run table} and not from the probe, so what had
failed was the table and not the runs: eight of the twenty-four rows
(\arm{p101}-s\{10,11\}, \arm{p202}-s\{9,10,11\}, \arm{p303}-s\{9,10,11\}) had been ingested
mid-flight and carried the partial epoch counts of that snapshot. \textbf{The verdict of that
first run is void, no number from it appears anywhere in this paper, and we record that it
happened rather than only its replacement}: a paper that asks to be judged on its process does
not get to report only the run that worked. The \texttt{.out} mirror was re-synced from both
clusters and the run table was rebuilt with \texttt{analysis/aggregate.py} followed by
\texttt{analysis/args\_repair.py --apply} --- the second step is not optional, because
\texttt{aggregate.py} alone marks \texttt{dup\_group} only where a \emph{run name} collides and
silently drops the annotations that tag differently-named same-experiment pairs. The rebuild
changed exactly those eight rows and \textbf{no other row in the corpus} (2{,}173 rows in and
out; 0 added, 0 removed, 8 changed, 0 of them outside \arm{rp1}).
\texttt{analysis/c97\_rp1\_score.py} was then run a \textbf{second} time, \textbf{unedited} ---
selftest 147/147 PASS, md5 \texttt{7d21c4f5c16ccf25196fd6a5e6391fa9} --- on the rebuilt table;
every validity gate returned 24/24; and \textbf{only that second run is transcribed}, in
\S\ref{sec:rp1}.

\textbf{The demotion registered in this manuscript did not fire; the demotion registered in the
scorer did.} Ours --- report the leg as \emph{underdetermined} if the interval still spans half of
$\Dstat$ --- does not fire: half of $\Dstat$ is 0.327 pp and the realised interval half-width is
0.203 pp, so the alignment leg is reported as a \textbf{null}. The scorer's --- \texttt{T1b} ---
does fire, and returns \texttt{CONSISTENT WITH NULL, UNDERPOWERED}: the point estimate lies inside
the $\pm 0.15$ band and the 95\% interval does not, so the null may not be written as an
equivalence claim. Neither verdict was selected after the fact and neither is quoted without the
other; the arithmetic for both is printed in \S\ref{sec:rp1} so that a reader can check each
against the rule as registered.
```

### TEX-6 — §4.6.1, the scorer-block lead-in: provenance and honest labelling (items a, e) · `tex:1883-1884`

OLD
```latex
The registered scorer \texttt{analysis/c97\_rp1\_score.py}, run \textbf{unedited}
(\texttt{--selftest} 147/147 PASS), verbatim:
```
NEW
```latex
The registered scorer \texttt{analysis/c97\_rp1\_score.py}, run \textbf{unedited}
(\texttt{--selftest} 147/147 PASS, md5 \texttt{7d21c4f5c16ccf25196fd6a5e6391fa9}) on the rebuilt
run table --- the second of two runs, the first being void and quoted nowhere
(\S\ref{sec:inflight}). Its verdict lines follow, with the printed per-verdict limits and the full
ANOVA table elided and nothing else altered:
```

### TEX-6b — §4.6.1, insert immediately AFTER the `\end{quote}` that closes the scorer block (item a)

This is an **insertion**, not a replacement. Apply it as a find-and-replace on the following
three-line anchor, which occurs **exactly once** in `paper.tex` (verified):

OLD
```latex
T5\ \ A / D = -2.8\%;\ \ 95\% CI = [-33.9\%, +28.3\%] of D\ \ (D pooled = +0.654 pp)
\end{quote}

\paragraph{The binding clause did not fire
```
NEW
```latex
T5\ \ A / D = -2.8\%;\ \ 95\% CI = [-33.9\%, +28.3\%] of D\ \ (D pooled = +0.654 pp)
\end{quote}

\paragraph{One arithmetic note, so that nobody recomputes the interval wrongly.}
The 95\% interval above is a $\mathbf{t}$ \textbf{interval on 5 df}, not a normal one:
$t_{.975,5} = 2.5706$ times $\se = 0.0791$ gives the half-width \textbf{0.203} and the bounds
$[-0.222, +0.185]$. A reader who applies the normal factor 1.96 gets 0.155 and will not reproduce
them. The two minimum detectable effects go the other way and are printed both ways for exactly
that reason: \textbf{0.222 pp} is the normal approximation --- the same $z_{.975} + z_{.80}$
constant that produced \arm{pp1}'s quoted 0.440 pp at $\se = 0.157$, kept so that the two batches
are compared on one formula --- and \textbf{0.276 pp} is the conservative $t$ version on 5 df. We
print the mixed pair rather than silently harmonising them because harmonising would break the
comparison with \arm{pp1} that the whole subsection exists to make.

\paragraph{The binding clause did not fire
```
(Note the NEW block **re-opens** the `\paragraph{The binding clause did not fire` that the anchor
consumed; TEX-8 below then rewrites that paragraph's opening. Apply TEX-6b **before** TEX-8, or
merge the two by hand — TEX-8's OLD block starts at `\paragraph{The binding clause did not fire,
and here is the arithmetic.}`, which after TEX-6b is intact and still unique.)

### TEX-7 — §4.6.1, restore the scorer's full `T2` verdict string (item c) · `tex:1897`

OLD
```latex
T2\ \ draw\ \ \ \ \ F(2,10) = 0.175, p 0.8423\ \ ->\ THE PERMUTATION DRAW IS EXCHANGEABLE\\
```
NEW
```latex
T2\ \ draw\ \ \ \ \ F(2,10) = 0.175, p 0.8423\\
\ \ \ \ ->\ THE PERMUTATION DRAW IS EXCHANGEABLE AT THIS RESOLUTION\\
```
(Split across two lines so the `\ttfamily` line does not overrun the text block. The scorer's
string is `THE PERMUTATION DRAW IS EXCHANGEABLE AT THIS RESOLUTION`, `c97_rp1_score.py:576`; the
paper was dropping the last three words, which are the ones that keep it a null with a stated
resolution rather than a claim of zero.)

### TEX-8 — §4.6.1, the binding-clause paragraph, re-attributed (items a, b) · `tex:1904-1906`

OLD
```latex
\paragraph{The binding clause did not fire, and here is the arithmetic.}
We registered in advance that \emph{if \arm{rp1} returned an interval that still spans half of
$\Dstat$, the alignment leg is to be reported as \textbf{underdetermined} rather than as a null}.
```
NEW
```latex
\paragraph{The binding clause did not fire, and here is the arithmetic --- and whose clause it
is.}
\textbf{This} manuscript registered in advance that \emph{if \arm{rp1} returned an interval that
still spans half of $\Dstat$, the alignment leg is to be reported as \textbf{underdetermined}
rather than as a null}. That rule is ours and not the scorer's, and we say so because we have
previously described it the other way round: the string \texttt{UNDERDETERMINED} appears
\textbf{zero} times in \texttt{analysis/c97\_rp1\_score.py}. The scorer supplies $\Astat$, its
standard error and its interval; the demotion \emph{it} registers is \texttt{T1b}, and
\texttt{T1b} \textbf{fired} (below). Ours did not, and here is why.
```
(The three sentences that follow in the file — "$\Dstat$ pooled over the two batches … is not a
rule." — are unchanged. Their numbers were re-derived and all hold: $\Dstat$ pooled $+0.6537$,
half $0.3268$, half-width $0.203$, normal MDE $0.222$, $t$ MDE $0.276$, interval
$[-33.9\%, +28.3\%]$ of $\Dstat$.)

### TEX-9 — §4.6.1, foreground exchangeability as the finding (item c) · `tex:1918-1921`

OLD
```latex
\item \textbf{Limit 2 is retired --- it is a measured number, not a caveat.} The two-way
  decomposition on the balanced $3 \times 6$ grid puts the permutation draw's variance component at
  \textbf{exactly zero} (truncated from $-0.00114$; $F(2,10) = 0.175$, $p = 0.84$), against a
  residual sd of 0.0908 pp.
```
NEW
```latex
\item \textbf{The permutation draw is exchangeable, and that is a finding rather than a retired
  caveat.} \textbf{Three independent draws of which weights share a group are statistically
  indistinguishable from one another}: on the balanced $3 \times 6$ grid the draw's own $F$ is
  $\mathbf{F(2,10) = 0.175}$, $\mathbf{p = 0.8423}$, and the registered scorer's verdict is
  \texttt{THE PERMUTATION DRAW IS EXCHANGEABLE AT THIS RESOLUTION}. This is a stronger statement
  than \arm{pp1}'s, and of a different kind: \arm{pp1} showed that \emph{one} arbitrary
  same-size regrouping did not move \plateau{}, which leaves open that the draw it happened to
  take was benign; \arm{rp1} shows that \emph{which} regrouping you take does not matter over
  three of them, so $\Astat$ may be read as a statement about the permutation \emph{distribution}
  rather than about one arbitrary draw. This also retires limit 2 as a measured number: the
  draw's variance component is \textbf{exactly zero} (truncated from $-0.00114$), against a
  residual sd of 0.0908 pp.
```
(The remainder of that bullet — "The three per-draw contrasts are $-0.013 \pm 0.082$, … resolved is
0.0653 pp." — is unchanged and its numbers were re-derived: $-0.013 \pm 0.082$,
$-0.036 \pm 0.105$, $-0.007 \pm 0.062$, spread 0.029, resolvable $\sigma_{\text{draw}}$ 0.0653 pp.
The sentence "so a single draw run \arm{pp1}-style would have returned the same verdict from this
experiment" now sits directly under the exchangeability claim it supports, which is where it
belongs.)

### TEX-10 — Appendix A.3b, add what would settle the disagreement (item d) · `tex:3802-3803`

OLD
```latex
effect makes the pairing more valuable rather than less.
```
NEW
```latex
effect makes the pairing more valuable rather than less.
\textbf{What would settle it}, stated so that the disagreement is not left as a shrug. Two
measurements are needed and neither exists yet. \textbf{(i)} The same $3 \times 6$
\arm{permnode} design \textbf{replicated at two or more observations per cell}. At one
observation per cell the residual is interaction-plus-noise, so a draw $\times$ seed interaction
and a genuine seed effect load on the same margin and cannot be told apart; replication separates
them, and it is the only one of the two that costs GPU. \textbf{(ii)} The corpus seed test re-read
\textbf{per cell instead of pooled}. \S\ref{sec:variance}'s $F(30,30) = 1.50$ is a seed term
estimated across 14 configuration cells at once, so a seed effect that is real within cells but
differs between them averages toward null there while showing up inside a single cell here; the
per-cell version is a re-analysis of data we already hold and costs nothing. We do not run it in
this draft, because under STANDING RULE 21 a test that could overturn a published null is
registered before it is read and not after the disagreement that motivates it. Until one of the
two is done, the honest statement is the one we make: two measurements of the same quantity
disagree, we report both, and we have not chosen between them.
```

---

## 3. Edits to `paper/DRAFT-v4.md`

Ten edits, one-to-one with the LaTeX. Every OLD block was confirmed to occur **exactly once**.

### MD-1 — §3.5 heading (item f) · `md:726`

OLD
```markdown
### 3.5 Four pre-registered batches: two scored, two still in flight
```
NEW
```markdown
### 3.5 Four pre-registered batches: three scored, one never started
```

### MD-2 — §3.5 opening paragraph (item f) · `md:733`

OLD
```markdown
record ahead of the numbers, and so that a reader can check that the two verdicts we did read are
```
NEW
```markdown
record ahead of the numbers, and so that a reader can check that the three verdicts we did read are
```

### MD-2b — the §3.5 table's own status column (item f) · `md:745`

The markdown table has no caption to fix, but its R1 row should carry the same pointer the LaTeX
table carries. Optional but recommended for parity.

OLD
```markdown
| R1 | `rp1` | 24 | the alignment null's power **and** its permutation-seed confound (§4.6) | `analysis/c97_rp1_score.py` | **SCORED — null REPLICATED (§4.6.1)** |
```
NEW
```markdown
| R1 | `rp1` | 24 | the alignment null's power **and** its permutation-seed confound (§4.6) | `analysis/c97_rp1_score.py` | **SCORED on the second run — null REPLICATED (§4.6.1)** |
```

### MD-3 — R1's registration, the ownership of the demotion (item b) · `md:761-762`

OLD
```markdown
**underdetermined**, not as a null.* The scorer additionally prints `pp1`'s registration defect
(band half-width 0.15 < realised se 0.157) whichever way the new data land.
```
NEW
```markdown
**underdetermined**, not as a null.* **That demotion is this manuscript's registration and not the
scorer's, and we correct our own earlier description of it here**: the string `UNDERDETERMINED`
appears **zero** times in `analysis/c97_rp1_score.py`. The scorer supplies the interval and issues
no such verdict. The demotion *it* carries is `T1b`, which refuses to call any `NULL` an
equivalence claim unless the entire 95% interval lies inside the ±0.15 band, and which prints
`pp1`'s registration defect (band half-width 0.15 < realised se 0.157) whichever way the new data
land. Two rules, two owners, both reported in §4.6.1: one of them fired and one of them did not,
and it is not the one a reader would guess.
```

### MD-4 — R1's status paragraph: the void run and the two demotions (items b, e) · `md:816-824`

OLD
```markdown
**R1 is complete and scored.** All 24 `rp1` runs reach 100 epochs in their own `.out` series and
all 24 now carry complete rows: eight of the twenty-four had been ingested mid-flight and carried
the partial epoch counts of that snapshot, and re-running `analysis/aggregate.py` over the refreshed
`.out` tree corrected exactly those eight rows and **changed no other row in the corpus** (0 added,
0 removed, 0 other rows altered). `analysis/c97_rp1_score.py` was then run **unedited** — selftest
147/147 PASS — and its verdict is transcribed in §4.6. The clause that binds us did **not** fire:
the interval does not span half of D (§4.6), so the alignment leg is reported as a null and not as
underdetermined. That the demotion did not fire is a fact about the data, not a choice: the
arithmetic is printed in §4.6 so a reader can check it against the rule as registered.
```
NEW
```markdown
**R1 is complete and scored — and the first attempt to score it is void.** All 24 `rp1` runs reach
100 epochs in their own `.out` series. The **first** invocation of `analysis/c97_rp1_score.py`
nonetheless returned `V0: 16/24`, with eight probe directories reading `ep=86/100`, `ep=84/100` and
similar, against `.out` tails on which all 24 read `Epoch 99` and `RUN_DONE`. The scorer's `V0`
gate takes `epochs_done` from the **run table** and not from the probe, so what had failed was the
table and not the runs: eight of the twenty-four rows (`p101-s{10,11}`, `p202-s{9,10,11}`,
`p303-s{9,10,11}`) had been ingested mid-flight and carried the partial epoch counts of that
snapshot. **The verdict of that first run is void, no number from it appears anywhere in this
paper, and we record that it happened rather than only its replacement**: a paper that asks to be
judged on its process does not get to report only the run that worked. The `.out` mirror was
re-synced from both clusters and the run table was rebuilt with `analysis/aggregate.py` followed by
`analysis/args_repair.py --apply` — the second step is not optional, because `aggregate.py` alone
marks `dup_group` only where a *run name* collides and silently drops the annotations that tag
differently-named same-experiment pairs. The rebuild changed exactly those eight rows and **no
other row in the corpus** (2,173 rows in and out; 0 added, 0 removed, 8 changed, 0 of them outside
`rp1`). `analysis/c97_rp1_score.py` was then run a **second** time, **unedited** — selftest 147/147
PASS, md5 `7d21c4f5c16ccf25196fd6a5e6391fa9` — on the rebuilt table; every validity gate returned
24/24; and **only that second run is transcribed**, in §4.6.1.

**The demotion registered in this manuscript did not fire; the demotion registered in the scorer
did.** Ours — report the leg as *underdetermined* if the interval still spans half of D — does not
fire: half of D is 0.327 pp and the realised interval half-width is 0.203 pp, so the alignment leg
is reported as a **null**. The scorer's — `T1b` — does fire, and returns `CONSISTENT WITH NULL,
UNDERPOWERED`: the point estimate lies inside the ±0.15 band and the 95% interval does not, so the
null may not be written as an equivalence claim. Neither verdict was selected after the fact and
neither is quoted without the other; the arithmetic for both is printed in §4.6.1 so that a reader
can check each against the rule as registered.
```

### MD-5 — §4.6.1 heading, synced to `paper.tex` (sync) · `md:1444`

OLD
```markdown
#### 4.6.1 The replication: `rp1` settles limits 2 and, partly, the power — and confirms the null
```
NEW
```markdown
#### 4.6.1 The replication: `rp1` settles limit 2, doubles the power, and confirms the null
```
(`paper.tex:1865-1866` already reads "settles limit 2, doubles the power, and confirms the null".
The two files must match; `T4` gives se 0.0791 against `pp1`'s 0.157, a ratio of 0.50×, so
"doubles the power" is the supported phrasing and "partly" is not.)

### MD-6 — §4.6.1, the scorer-block lead-in (items a, e) · `md:1458-1459`

OLD
```markdown
The registered scorer `analysis/c97_rp1_score.py`, run **unedited** (`--selftest` 147/147 PASS),
verbatim:
```
NEW
```markdown
The registered scorer `analysis/c97_rp1_score.py`, run **unedited** (`--selftest` 147/147 PASS,
md5 `7d21c4f5c16ccf25196fd6a5e6391fa9`) on the rebuilt run table — the second of two runs, the
first being void and quoted nowhere (§3.5). Its verdict lines follow, with the printed per-verdict
limits and the full ANOVA table elided and nothing else altered:
```

### MD-6b — §4.6.1, insert immediately AFTER the closing ``` of the scorer block (item a) · after `md:1476`

Insertion, not a replacement. Apply as a find-and-replace on the following anchor, which occurs
**exactly once** in `DRAFT-v4.md` (verified). The fence below is written with `~~~` to escape this
document; **in the real edit it is a triple-backtick fence**.

OLD
```markdown
T5  A / D = -2.8%;  95% CI = [-33.9%, +28.3%] of D   (D pooled = +0.654 pp)
~~~

**The binding clause did not fire
```
NEW
```markdown
T5  A / D = -2.8%;  95% CI = [-33.9%, +28.3%] of D   (D pooled = +0.654 pp)
~~~

**One arithmetic note, so that nobody recomputes the interval wrongly.** The 95% interval above is
a ***t* interval on 5 df**, not a normal one: t(.975, 5) = 2.5706 times se = 0.0791 gives the
half-width **0.203** and the bounds [−0.222, +0.185]. A reader who applies the normal factor 1.96
gets 0.155 and will not reproduce them. The two minimum detectable effects go the other way and are
printed both ways for exactly that reason: **0.222 pp** is the normal approximation — the same
z(.975) + z(.80) constant that produced `pp1`'s quoted 0.440 pp at se = 0.157, kept so that the two
batches are compared on one formula — and **0.276 pp** is the conservative *t* version on 5 df. We
print the mixed pair rather than silently harmonising them because harmonising would break the
comparison with `pp1` that the whole subsection exists to make.

**The binding clause did not fire
```
(As with TEX-6b, the NEW block re-opens the `**The binding clause did not fire` that the anchor
consumed. Apply MD-6b **before** MD-8; MD-8's OLD block is then intact and still unique.)

### MD-7 — §4.6.1, restore the scorer's full `T2` verdict string (item c) · `md:1471`

OLD
```markdown
T2  draw     F(2,10) = 0.175, p 0.8423   -> THE PERMUTATION DRAW IS EXCHANGEABLE
```
NEW
```markdown
T2  draw     F(2,10) = 0.175, p 0.8423
    -> THE PERMUTATION DRAW IS EXCHANGEABLE AT THIS RESOLUTION
```

### MD-8 — §4.6.1, the binding-clause paragraph, re-attributed (items a, b) · `md:1480-1483`

OLD
```markdown
**The binding clause did not fire, and here is the arithmetic.** We registered in advance that *if
`rp1` returned an interval that still spans half of D, the alignment leg is to be reported as
**underdetermined** rather than as a null*.
```
NEW
```markdown
**The binding clause did not fire, here is the arithmetic — and here is whose clause it is.**
**This** manuscript registered in advance that *if `rp1` returned an interval that still spans half
of D, the alignment leg is to be reported as **underdetermined** rather than as a null*. That rule
is ours and not the scorer's, and we say so because we have previously described it the other way
round: the string `UNDERDETERMINED` appears **zero** times in `analysis/c97_rp1_score.py`. The
scorer supplies `A`, its standard error and its interval; the demotion *it* registers is `T1b`, and
`T1b` **fired** (below). Ours did not, and here is why.
```
(The sentences that follow — "D pooled over the two batches … is not a rule." — are unchanged.)

### MD-9 — §4.6.1, foreground exchangeability as the finding (item c) · `md:1493-1495`

OLD
```markdown
* **Limit 2 is retired — it is a measured number, not a caveat.** The two-way decomposition on the
  balanced 3 × 6 grid puts the permutation draw's variance component at **exactly zero**
  (truncated from −0.00114; F(2,10) = 0.175, p = 0.84), against a residual sd of 0.0908 pp.
```
NEW
```markdown
* **The permutation draw is exchangeable, and that is a finding rather than a retired caveat.**
  **Three independent draws of which weights share a group are statistically indistinguishable
  from one another**: on the balanced 3 × 6 grid the draw's own F is **F(2,10) = 0.175,
  p = 0.8423**, and the registered scorer's verdict is `THE PERMUTATION DRAW IS EXCHANGEABLE AT
  THIS RESOLUTION`. This is a stronger statement than `pp1`'s, and of a different kind: `pp1`
  showed that *one* arbitrary same-size regrouping did not move plateau5, which leaves open that
  the draw it happened to take was benign; `rp1` shows that *which* regrouping you take does not
  matter over three of them, so `A` may be read as a statement about the permutation *distribution*
  rather than about one arbitrary draw. This also retires limit 2 as a measured number: the draw's
  variance component is **exactly zero** (truncated from −0.00114), against a residual sd of
  0.0908 pp.
```

### MD-10 — Appendix A.3b, add what would settle the disagreement (item d) · `md:3015-3016`

OLD
```markdown
not touch `A`: `T1` pairs within run seed, which removes exactly this variance from `A`'s standard
error, so a real seed effect makes the pairing more valuable rather than less.
```
NEW
```markdown
not touch `A`: `T1` pairs within run seed, which removes exactly this variance from `A`'s standard
error, so a real seed effect makes the pairing more valuable rather than less.

**What would settle it**, stated so that the disagreement is not left as a shrug. Two measurements
are needed and neither exists yet. **(i)** The same 3 × 6 `permnode` design **replicated at two or
more observations per cell**. At one observation per cell the residual is interaction-plus-noise,
so a draw × seed interaction and a genuine seed effect load on the same margin and cannot be told
apart; replication separates them, and it is the only one of the two that costs GPU. **(ii)** The
corpus seed test re-read **per cell instead of pooled**. §6.3's F(30,30) = 1.50 is a seed term
estimated across 14 configuration cells at once, so a seed effect that is real within cells but
differs between them averages toward null there while showing up inside a single cell here; the
per-cell version is a re-analysis of data we already hold and costs nothing. We do not run it in
this draft, because under STANDING RULE 21 a test that could overturn a published null is
registered before it is read and not after the disagreement that motivates it. Until one of the two
is done, the honest statement is the one we make: two measurements of the same quantity disagree,
we report both, and we have not chosen between them.
```

---

## 3b. Dry-run verification (already performed by this package)

All 23 OLD blocks above were confirmed to occur **exactly once** in their target file by
fixed-string count. All 23 were then applied to **scratch copies** (never to the real files, per
the concurrency rule) and the result compiled:

```
23/23 anchors unique and applied in the order given
tectonic paper.tex            ->  EXIT 0, paper.pdf written, 62 pages (was 61)
pdftotext | grep -c '??'      ->  0
distinct Overfull hboxes      ->  12.25499 / 20.28241 / 7.28497 pt
                                  i.e. EXACTLY the three pre-existing at HEAD (CORRECTIONS 129.6)
                                  -- this package adds no new overfull box
post-edit string census (whitespace-normalised, both files):
  "EXCHANGEABLE AT THIS RESOLUTION"   x2   (quote block + the §4.6.1 bullet)
  "appears zero times [in the scorer]" x2  (§3.5 R1 registration + §4.6.1 binding clause)
  "16/24"                             x1   (the void-run disclosure, §3.5)
```

**Ordering constraint.** Apply TEX-6b before TEX-8, and MD-6b before MD-8. Both insertion anchors
consume the opening of the binding-clause paragraph and re-emit it; applying them in the other
order still works but is harder to check. Every other edit is order-independent.

---

## 4. Cross-reference checks the applying agent must run after editing

1. **`\S\ref{sec:variance}` in TEX-10.** `\label{sec:variance}` is at `paper.tex:3000`; the target
   is §6.3 in the markdown numbering, which is what MD-10 uses. Confirmed present in both.
2. **`\S\ref{sec:rp1}` in TEX-4, TEX-5, TEX-6.** `\label{sec:rp1}` is at `paper.tex:1867`.
   Confirmed. TEX-5 changes two `\S\ref{sec:alignment}` pointers to `\S\ref{sec:rp1}`, which is the
   correct target: the arithmetic it promises is printed in §4.6.1, not §4.6.
3. **`\S\ref{sec:inflight}` in TEX-6.** `\label{sec:inflight}` is at `paper.tex:921`. Confirmed.
4. **`\plateau{}` in TEX-9.** Macro used throughout; e.g. `paper.tex:643`. Confirmed.
5. **Recompile.** `tectonic paper/paper.tex` must exit 0 with 0 `??`. TEX-7 splits one `\ttfamily`
   line into two inside an existing `quote`; TEX-6b and TEX-10 add prose only. No new labels, no new
   citations, no new floats.
6. **Re-run `python3 analysis/c98_reproduce.py`.** None of these edits changes an asserted numeral:
   every number in the replacement text (2,173 / 8 / 0.327 / 0.203 / 0.222 / 0.276 / 0.0791 /
   0.0908 / 0.0653 / 0.175 / 0.8423 / 4.634 / 0.0190 / +0.654 / −33.9% / +28.3%) already appears in
   the manuscript at the same value. The **only new numerals** are `16/24`, `86/100`, `84/100`,
   `2.5706` and `0.155`, all of which are prose-only and outside the audit's asserted set. The
   `--census` denominator will move by roughly those five; F2's package owns that number and must
   re-run `--census` after this package lands.

---

## 5. What this package deliberately did NOT do

* **Did not touch either file.** Packages run concurrently on `paper.tex` and `DRAFT-v4.md`.
* **Did not touch the abstract.** `tex:179-186` / `md:107-112` already carry the landed `rp1`
  numbers correctly (`−0.018 ± 0.079`, `[−34%, +28%]` of D, `F(2,10) = 0.175, p = 0.84`) and
  re-derivation confirms all of them. G2 and G4 own the abstract. **Hand-off:** if G4 rewrites the
  abstract's `rp1` sentence, the phrase "the permutation draw's variance component measured at
  zero" is weaker than what the scorer licenses and could be strengthened to "three independent
  permutation draws are statistically indistinguishable" at no cost in words.
* **Did not touch §4.6.1's final paragraph** (`tex:1961-1968`, `md:1530-1536`) even though it
  contains the stale "sixteen count-matched cells". **S4 owns that string** and this package's
  anchors deliberately stop short of it.
* **Did not touch `tex:1355` "There is no third".** S2 owns it. Note for whoever holds S2: `rp1`
  is that third count-matched contrast — 4 arms × 6 seeds, all at m = 14,420, reported in §4.6.1
  rather than in Table 2 — and TEX-9's new text makes the three-arm structure more visible, which
  makes the "no third" sentence read worse, not better, until S2 lands.
* **Did not run a Slurm job, commit, or edit any scorer.** `c97_rp1_score.py` was run only with
  `--selftest` (147/147 PASS) and read; the full score could not be re-run locally because the
  probe directories under `../runs/rp1/` are empty on this machine (they live on the cluster), so
  every `T1`/`T2`/`T3`/`T4`/`T5` number above was re-derived independently from
  `results/all_runs.csv` and cross-checked against the scorer's source. All match.

---

## 6. One thing a reviewer of this package should know

The paper is now going to say, in two places, that we described our own registration incorrectly.
That is the point: the false attribution was that the *scorer* would demote the leg to
`UNDERDETERMINED`. It never would have — the string is not in the file. Had the interval come back
wide, nothing automatic would have fired, and the demotion would have depended entirely on us
applying our own rule to a number we had already seen. Saying so is worse for us than staying
quiet, and it is exactly the class of defect §6 of this paper exists to catalogue.
