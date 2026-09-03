# v8 — package `mechanics-and-extrapolation` (R3 + R5)

**Status.** Both edits derived, drafted, dry-run integrated and compiled. `paper/paper.tex` and
`paper/DRAFT-v4.md` were **not** edited; nothing was committed; no Slurm job was submitted.

Two things in this package **are already applied to the working tree**, because the brief said to
act on them: the ALICE probe sync (§5) and the Figure 3 redraw (§6, `analysis/c98_figures.py` +
`paper/figures/f3_budget.{pdf,png}`).

> **COUPLING — read before integrating.** `paper/figures/f3_budget.pdf` has already been redrawn
> and now carries **three** slope readings in panel (b). The live caption still says *"The panel is
> drawn on the archive"*, which the redrawn panel makes **false**. The caption replacement in §6.3
> **must land in the same commit as the figure.** If the caption is not applied, revert the figure
> instead: `git checkout -- analysis/c98_figures.py paper/figures/f3_budget.pdf
> paper/figures/f3_budget.png`.

---

## 1. What was verified, and how

### 1.1 The registered scorer, run UNEDITED (RULE 16)

```
python3 analysis/c99_hz3q_score.py --selftest          ->  selftest: 59/59 PASS
python3 analysis/c99_hz3q_score.py --runs ../runs --probes ../runs/hz3
```

Only its own documented arguments were passed; the file was not touched. Its H2 block, verbatim:

```
--- H2  THE PRIMARY.  IS D FLAT FROM 100 TO 300 EPOCHS? ----------------
    delta_s = D(s,300) - D(s,100), plateau5, PAIRED WITHIN SEED.
    verdict: |t| < 2.0 -> FLAT; |t| >= 2.0 -> NOT FLAT, and the sign of
    delta names the direction.  Frozen in band_flat() before hz3q existed.

    hz3 AS PUBLISHED (6 archived seeds; s5 cross-box, cross-class)
      n=6  delta -0.149  se 0.105  t -1.42  df 5  ->  FLAT

    hz3 WITH SEED 5 DROPPED (5 seeds)
      n=5  delta -0.207  se 0.107  t -1.94  df 4  ->  FLAT

    REPAIRED: archived seeds 0-4 + hz3q seed 5  ** THE VERDICT **
      n=6  delta -0.238  se 0.093  t -2.57  df 5  ->  NOT FLAT -- D DECLINES WITH BUDGET
```

**New this session:** with the probe records synced (§5), **H1 now runs and PASSES** where it
previously refused:

```
    node  ep100 coord_lo 0.000000 coord_hi 0.000000 n 500  ep200 ...  ep300 ...
    H1 PASS -- worst coordinate fraction 0.000000 (bar 0.05); EXACTLY ZERO, as the arithmetic requires.
```

That is the number `paper.tex:1163-1166` already prints (*"the worst coordinate fraction over all
four arms at epochs 100, 200 and 300 is exactly 0.000000 on n = 500 coordinates per arm, against a
registered bar of 0.05"*). Before the sync that sentence was true but **not locally re-derivable**;
c99 printed `NO OCCUPANCY IS MEASURABLE`. It is now re-derivable. **No prose change is owed** — see
§5 for why the Data-Availability register's `c99_hz3q` PARTIAL entry is also still correct.

### 1.2 The per-seed ladder everything below rests on

Read with `analysis/c98_figures.py`'s own `series()` / `pl5()` — the same reader `c98_reproduce.py`
uses for §4.8 — over `hz3-{ch,node}-s*.out` with `hz3q`'s seed 5 substituted:

| seed | source | D(100) | D(300) | δ = D(300) − D(100) |
|---|---|---|---|---|
| 0 | hz3 | +0.586 | +0.432 | −0.154 |
| 1 | hz3 | +0.564 | +0.476 | −0.088 |
| 2 | hz3 | +0.622 | +0.168 | **−0.454** |
| 3 | hz3 | +0.990 | +0.550 | **−0.440** |
| 4 | hz3 | +0.548 | +0.650 | +0.102 |
| 5 | hz3 *(archived)* | +0.148 | +0.290 | **+0.142** ← most positive of the archived six |
| 5 | **hz3q** *(repaired)* | +0.482 | +0.086 | **−0.396** ← third most negative of the repaired six |

Repaired means: D(100) +0.6320 (se 0.074), D(200) +0.5120 (se 0.116), D(300) +0.3937 (se 0.090) —
the §4.8 table's third column, re-derived, agreeing.

---

## 2. R3 — the zero-crossing

### 2.1 The arithmetic, confirmed

`0.394 / (0.238/200) = 331.09` → **331 further epochs → a linear zero-crossing at 631.1 epochs.**
The briefing's ~631 figure is right. On the unrounded ladder the same construction gives
`0.39367 / (0.238333/200) = 330.35` → **630.3**, and an ordinary-least-squares line through all
three repaired points gives `D = 0.750889 − 0.00119167·B`, zero at **630.1**. Both routes: **630**.

### 2.2 Why that number must not be used — four measured facts, not an assertion

1. **No upper bound.** The registered 95 % interval on the slope is already in the paper:
   `[−0.477, −0.000]`. Through the same linear model the steep end puts the crossing at
   **465.2 epochs** and the shallow end at **555 530 epochs** — i.e. *never*, because the interval
   reaches zero. The point estimate has a lower bound and no upper one.
2. **The ladder resolves a difference, not a rate.** Split into halves and paired within seed
   exactly as the endpoints are:

   | interval | δ | se | t |
   |---|---|---|---|
   | D(200) − D(100) | −0.1200 | 0.1422 | **−0.84** |
   | D(300) − D(200) | −0.1183 | 0.0964 | **−1.23** |
   | D(300) − D(100) | −0.2383 | 0.0927 | −2.57 |

   **Neither half resolves.** Only the full span does. The measurement licenses an endpoint
   difference and nothing about the shape in between, let alone beyond.
3. **The form is unidentified, and the form matters more than the fit.** Three points, a
   two-parameter family, one residual degree of freedom, against a per-point se of 0.074–0.116 pp:

   | model | fit | worst residual | zero at |
   |---|---|---|---|
   | D linear in B | 0.750889 − 0.00119167·B | 0.0006 pp | **630 epochs** |
   | D linear in ln B | 1.616625 − 0.212222·ln B | 0.0198 pp | **2034 epochs** |
   | D ∝ exp(−B/τ) | 0.807781·exp(−0.00236692·B) | 0.0088 pp | **never** (D(600) = +0.195) |

   All three sit inside 0.020 pp — far under one se — and they disagree by a factor of three, or by
   infinity, about the crossing.
4. **The runs argue against the linear form in particular.** Linearity in D assumes a constant-rate
   catch-up. Both arms are saturating, at different times (paired within run, n = 6):

   | arm | plateau5(100) | plateau5(200) | plateau5(300) | gain 100→200 | gain 200→300 |
   |---|---|---|---|---|---|
   | chunk777 | 92.556 | 93.248 | 93.232 | +0.693 | **−0.016 ± 0.055** |
   | nodewise | 91.924 | 92.736 | 92.838 | +0.813 | **+0.102 ± 0.096** |

   Past 200 epochs neither arm is still measurably improving, so D's apparent constant rate over
   [100, 300] (decrements −0.120 and −0.118, equal to within 0.002 pp) is a property of the window
   measured, not a law to carry past it.

Two further points that cost no numerals: the ladder is **six trajectory pairs read at three
prefixes**, six independent units and not eighteen; and the sign is window-dependent — `c87`'s
registered 50-epoch window returns `GROWS` on the same runs, which §4.8 already discloses.

**Foreclosing "but you have 600-epoch runs":** the corpus holds exactly six, `bg600_cos_s{0,1,2}`
and `bg600_meta_s{0,1,2}` — AdamW base, layerwise partition, box `−15:−2.3026`, against a
cosine-schedule baseline. They carry **no** chunk777–nodewise contrast and cannot extend this
ladder. Verified against `results/all_runs.csv`.

### 2.3 EXACT REPLACEMENT TEXT — R3

**Insertion, not replacement.** Append the block below immediately after the verbatim anchor.
Anchors verified `count == 1` against the live files at HEAD `fe957e4`.

#### `paper/paper.tex` — anchor (append after)

```tex
that reason. Table~\ref{tab:D}'s \arm{hz3} cell is a separate, CSV-based reading of a separate
registration and is unmoved by any of this.
```

#### `paper/paper.tex` — text to append

```tex
\textbf{Where does $\Dstat$ reach zero? We do not know, and three points cannot tell us.} The
arithmetic a referee will do is the linear one, so we do it here rather than leave it implied: at
$-0.238$ pp per 200 epochs, $\Dstat(300) = +0.394$ needs $0.394 / (0.238/200) \approx 331$ further
epochs, putting a linear zero-crossing near 631 epochs --- and on the unrounded ladder both routes
to it, the paired slope applied to $\Dstat(300)$ and least squares through all three repaired
points, give 630. \textbf{That number is not a prediction, and four measured facts say why.}
(i) It has no upper bound. Propagated through the same linear model, the registered 95\% interval
on the slope, $[-0.477,\ -0.000]$, puts the crossing anywhere from about 465 epochs to never,
because the interval reaches zero. (ii) The ladder resolves a difference, not a rate. Split into
its two halves, paired within seed exactly as the endpoints are, the decline reads
$-0.120 \pm 0.142$ ($t\ -0.84$) over 100--200 epochs and $-0.118 \pm 0.096$ ($t\ -1.23$) over
200--300: \emph{neither half resolves}, and only the full 100--300 span does. The measurement
licenses an endpoint difference and says nothing about the shape between those endpoints, let
alone past them. (iii) The functional form is therefore unidentified, and here the choice of form
matters far more than the quality of the fit. $\Dstat$ linear in $B$, linear in $\ln B$, and
decaying exponentially in $B$ all reproduce the three repaired points to within $0.020$ pp ---
well inside a per-point $\se$ of $0.074$ to $0.116$ --- and they put the crossing at 630 epochs, at
2034 epochs, and nowhere at all (the exponential fit gives $\Dstat(600) = +0.195$ and never reaches
zero). (iv) The runs themselves argue against the linear form in particular, because a
constant-rate catch-up is what linearity assumes and both arms are visibly saturating: across
100, 200 and 300 epochs \arm{chunk777} gains $+0.693$ pp and then $-0.016 \pm 0.055$, and
\arm{nodewise} gains $+0.813$ and then $+0.102 \pm 0.096$, so past 200 epochs neither arm is still
measurably improving. \textbf{The measured ladder stops at 300 epochs and so does the claim.} We
report a resolved decline across $[100, 300]$ at one design point, in one batch, on six trajectory
pairs read at three prefixes --- six independent units, not eighteen --- and we report no rate, no
functional form and no crossing beyond it. The corpus's only 600-epoch runs sit at a different
design point (an AdamW base with a layerwise partition, against a cosine-schedule baseline), carry
no \arm{chunk777}--\arm{nodewise} contrast, and cannot extend this ladder; the run that would
settle the question, this cell at 600 epochs, was not submitted. A reader who wants the shape of
$\Dstat(B)$ should read this subsection as a request for it, not as an estimate of it.
```

#### `paper/DRAFT-v4.md` — anchor (append after)

```markdown
Table 2's `hz3` cell is a separate, CSV-based
reading of a separate registration and is unmoved by any of this.
```

#### `paper/DRAFT-v4.md` — text to append

```markdown
**Where does D reach zero? We do not know, and three points cannot tell us.** The arithmetic a
referee will do is the linear one, so we do it here rather than leave it implied: at −0.238 pp per
200 epochs, D(300) = +0.394 needs 0.394 / (0.238/200) ≈ 331 further epochs, putting a linear
zero-crossing near 631 epochs — and on the unrounded ladder both routes to it, the paired slope
applied to D(300) and least squares through all three repaired points, give 630. **That number is
not a prediction, and four measured facts say why.** (i) It has no upper bound. Propagated through
the same linear model, the registered 95% interval on the slope, [−0.477, −0.000], puts the
crossing anywhere from about 465 epochs to never, because the interval reaches zero. (ii) The
ladder resolves a difference, not a rate. Split into its two halves, paired within seed exactly as
the endpoints are, the decline reads −0.120 ± 0.142 (t −0.84) over 100–200 epochs and
−0.118 ± 0.096 (t −1.23) over 200–300: *neither half resolves*, and only the full 100–300 span
does. The measurement licenses an endpoint difference and says nothing about the shape between
those endpoints, let alone past them. (iii) The functional form is therefore unidentified, and here
the choice of form matters far more than the quality of the fit. D linear in B, linear in ln B, and
decaying exponentially in B all reproduce the three repaired points to within 0.020 pp — well
inside a per-point se of 0.074 to 0.116 — and they put the crossing at 630 epochs, at 2034 epochs,
and nowhere at all (the exponential fit gives D(600) = +0.195 and never reaches zero). (iv) The
runs themselves argue against the linear form in particular, because a constant-rate catch-up is
what linearity assumes and both arms are visibly saturating: across 100, 200 and 300 epochs
`chunk777` gains +0.693 pp and then −0.016 ± 0.055, and `nodewise` gains +0.813 and then
+0.102 ± 0.096, so past 200 epochs neither arm is still measurably improving. **The measured ladder
stops at 300 epochs and so does the claim.** We report a resolved decline across [100, 300] at one
design point, in one batch, on six trajectory pairs read at three prefixes — six independent units,
not eighteen — and we report no rate, no functional form and no crossing beyond it. The corpus's
only 600-epoch runs sit at a different design point (an AdamW base with a layerwise partition,
against a cosine-schedule baseline), carry no `chunk777`–`nodewise` contrast, and cannot extend
this ladder; the run that would settle the question, this cell at 600 epochs, was not submitted. A
reader who wants the shape of D(B) should read this subsection as a request for it, not as an
estimate of it.
```

---

## 3. R5 — the reversal's mechanics

### 3.1 Both halves verified numerically

**Half one — deleting seed 5 does NOT produce the reversal.** Confirmed from the scorer itself and
re-derived independently: `n = 5, δ = −0.2068, se = 0.106712, t = −1.9379` → rounds to
**−0.207 ± 0.107, t −1.94**, which is **inside** the frozen `|t| < 2.0` band. **Still FLAT.**

**Half two — the replacement does it, by doing two things at once.**

*Location.* The replacement's δ is −0.396 against the five-seed mean of −0.2068. A sixth
observation moves a mean by exactly one sixth of its distance from that mean:

```
(x − mean₅)/6 = (−0.3960 − (−0.20680))/6 = −0.18920/6 = −0.031533
mean₅ + that  = −0.20680 − 0.031533     = −0.238333   ==  the repaired estimate, exactly
```

*Precision.* Restoring n from 5 to 6 returns the degree of freedom the deletion cost:
se 0.106712 → 0.092661, a 13.2 % cut.

*They compose exactly, and in equal parts.* Because t = δ/se, the |t| move factorises:

| factor | value | share of the log-\|t\| move |
|---|---|---|
| location, \|δ₆/δ₅\| | 1.152482 | **50.1 %** |
| precision, se₅/se₆ | 1.151644 | **49.9 %** |
| product | **1.327249** | = 2.57211 / 1.93793 ✓ |

Neither half does it alone. (Counterfactually — and these are arithmetic, not datasets — the
location alone would give |t| 2.233 and the precision alone 2.232. The reversal is not balanced on
one of the two.)

### 3.2 The part that turns the attack around

The replacement is **not** an extreme value inserted; it is an extreme value **removed**.

* hz3q's δ = −0.396 sits **0.79 sd** inside the five archived seeds' own spread (sd 0.2386) — an
  ordinary draw.
* It is only the **third** most negative of the repaired six; seeds 2 and 3 read −0.454 and −0.440.
* The value it displaces, the archived seed 5's **+0.142**, was the **single most positive** of the
  archived six — the most flatness-favouring observation in the set.

### 3.3 And the honest limit: the sensitivity belongs to n = 6, not to seed 5

Leave-one-out over the repaired six:

| seed dropped | n | δ | se | \|t\| | verdict at the frozen bar |
|---|---|---|---|---|---|
| 0 | 5 | −0.2552 | 0.1116 | 2.287 | NOT FLAT |
| 1 | 5 | −0.2684 | 0.1073 | 2.500 | NOT FLAT |
| 2 | 5 | −0.1952 | 0.1004 | **1.943** | FLAT |
| 3 | 5 | −0.1980 | 0.1022 | **1.938** | FLAT |
| 4 | 5 | −0.3064 | 0.0770 | 3.979 | NOT FLAT |
| 5 | 5 | −0.2068 | 0.1067 | **1.938** | FLAT — *this is the paper's five-clean-seed row* |

Three of six deletions fall back under the bar. That is the honest size of a six-seed paired test
whose two-sided p is 0.050 — the paper already prints that p and the interval `[−0.477, −0.000]` —
and it is emphatically **not** a property of the seed we repaired. Saying so is what converts
*"one seed flipped your headline"* into *"a six-seed design is n = 6, and here is every
single-seed deletion."*

> **The one judgement call in this package.** Including §3.3's leave-one-out table is additive
> disclosure the gate did not ask for. I judge it a net gain: it is the first thing a hostile
> referee computes, the paper already concedes everything it shows (p = 0.050, CI touching zero),
> and it relocates the fragility from *the seed we replaced* — which reads badly — to *n = 6*,
> which is an ordinary, disclosed design limit. If the integrator disagrees, delete the sentence
> beginning **"What the verdict is sensitive to is n = 6"** through the end of that paragraph in
> both markups; nothing else in the package depends on it. Numerals removed then: 2.29, 2.50,
> 1.94 ×3, 3.98, 1.943, 1.938 ×2, 0.050 — delete from **both** files or the numeric diff will fail.

### 3.4 EXACT REPLACEMENT TEXT — R5

**Insertion, not replacement.** Append after the "What the repair moved." paragraph. Anchors
verified `count == 1`.

#### `paper/paper.tex` — anchor (append after)

```tex
\arm{chunk777}, \arm{nodewise1d}, \arm{chunk2325} --- are class-plus-nondeterminism
alone (\S\ref{sec:threats} T9).
```

#### `paper/paper.tex` — text to append

```tex
\textbf{How the reversal actually happens, since deleting the bad seed does not produce it.} The
first objection to a headline that turns on one seed is that it turns on one seed, and the table
above already answers it: delete the contaminated seed and stop there and the reading is
$-0.207 \pm 0.107$, $t\ -1.94$ --- \textbf{still \texttt{FLAT}}. What crosses the bar is the
\emph{replacement}, and it does two things at once, in almost exactly equal measure.
\emph{Location}: \arm{hz3q}'s seed-5 $\delta$ is $-0.396$ against the five clean seeds' mean of
$-0.207$, and a sixth observation moves a mean by exactly one sixth of its distance from that mean
--- here $-0.0315$, which carries $-0.2068$ to $-0.2383$, the table's $-0.207$ and $-0.238$.
\emph{Precision}: restoring $n$ from 5 to 6 returns the degree of freedom the deletion cost and
cuts the $\se$ from $0.107$ to $0.093$. Because $t$ is $\delta/\se$, the two compose exactly:
$|t|$ goes from $1.94$ to $2.57$, a ratio of $1.327$, which is $1.152$ from the location times
$1.152$ from the precision --- 50.1\% and 49.9\% of the move in logs. \textbf{Neither half does it
alone}, and the reader should not have to reconstruct that from the table.

\textbf{The replacement is not an outlier; it displaces one.} \arm{hz3q}'s seed-5 $\delta$ of
$-0.396$ sits $0.79$ standard deviations inside the five archived seeds' own spread, and it is only
the \emph{third} most negative of the repaired six --- seeds 2 and 3 read $-0.454$ and $-0.440$.
The value it replaces, the archived seed 5's $+0.142$, was the \emph{most positive} of the archived
six. The repair takes the single most flatness-favouring observation in the set out and puts an
unremarkable one in; that is the whole of the mechanism. \textbf{What the verdict is sensitive to
is $n = 6$, not seed 5.} Deleting each seed in turn from the repaired pool gives $|t| = 2.29$,
$2.50$, $1.94$, $1.94$, $3.98$ and $1.94$ for seeds 0 through 5 (the three that fall short read
$1.943$, $1.938$ and $1.938$ unrounded), so three of the six single-seed deletions put the reading
back under the bar --- and the last of those three is simply the five-clean-seed row of the table
above. That is the honest size of a six-seed paired test whose two-sided $p$ is $0.050$. It is a
property of the design, not of the seed we repaired, and it is why this subsection reports a
decline resolved at this budget and this design point rather than a law.
```

#### `paper/DRAFT-v4.md` — anchor (append after)

```markdown
`chunk777`, `nodewise1d`, `chunk2325` — are class-plus-nondeterminism alone (§7 T9).
```

#### `paper/DRAFT-v4.md` — text to append

```markdown
**How the reversal actually happens, since deleting the bad seed does not produce it.** The first
objection to a headline that turns on one seed is that it turns on one seed, and the table above
already answers it: delete the contaminated seed and stop there and the reading is −0.207 ± 0.107,
t −1.94 — **still `FLAT`**. What crosses the bar is the *replacement*, and it does two things at
once, in almost exactly equal measure. *Location*: `hz3q`'s seed-5 δ is −0.396 against the five
clean seeds' mean of −0.207, and a sixth observation moves a mean by exactly one sixth of its
distance from that mean — here −0.0315, which carries −0.2068 to −0.2383, the table's −0.207 and
−0.238. *Precision*: restoring n from 5 to 6 returns the degree of freedom the deletion cost and
cuts the se from 0.107 to 0.093. Because t is δ/se, the two compose exactly: \|t\| goes from 1.94
to 2.57, a ratio of 1.327, which is 1.152 from the location times 1.152 from the precision — 50.1%
and 49.9% of the move in logs. **Neither half does it alone**, and the reader should not have to
reconstruct that from the table.

**The replacement is not an outlier; it displaces one.** `hz3q`'s seed-5 δ of −0.396 sits 0.79
standard deviations inside the five archived seeds' own spread, and it is only the *third* most
negative of the repaired six — seeds 2 and 3 read −0.454 and −0.440. The value it replaces, the
archived seed 5's +0.142, was the *most positive* of the archived six. The repair takes the single
most flatness-favouring observation in the set out and puts an unremarkable one in; that is the
whole of the mechanism. **What the verdict is sensitive to is n = 6, not seed 5.** Deleting each
seed in turn from the repaired pool gives \|t\| = 2.29, 2.50, 1.94, 1.94, 3.98 and 1.94 for seeds 0
through 5 (the three that fall short read 1.943, 1.938 and 1.938 unrounded), so three of the six
single-seed deletions put the reading back under the bar — and the last of those three is simply
the five-clean-seed row of the table above. That is the honest size of a six-seed paired test whose
two-sided p is 0.050. It is a property of the design, not of the seed we repaired, and it is why
this subsection reports a decline resolved at this budget and this design point rather than a law.
```

---

## 4. Where these paragraphs go

Both are **insertions inside §4.8 (`sec:budget`)**, in this order:

```
  ... "Read the withdrawal for exactly what it is." paragraph      (unchanged)
  >>> R3: "Where does D reach zero? ..."                           (NEW)
  ... "Why the published reading was wrong ..."                    (unchanged)
  ... "What the repair moved."                                     (unchanged)
  >>> R5: "How the reversal actually happens ..."                  (NEW, 2 paragraphs)
  ... "A control hz3's own design could not run."                  (unchanged)
```

§3.5's R2 block was deliberately **not** touched: it states the three readings, and the mechanics
belong where the ladder is. Nothing outside §4.8 and the Figure 3 caption changes.

---

## 5. Owed item 1 — the empty local probe directories: **SYNCED**

**Before.** `alice-backup/runs/hz3/probe_{node,ch,n1d,c23}_hz3q_s5/` existed and were **empty**
(0 entries, 0 B). `c99_hz3q_score.py` refused correctly rather than passing silently:

```
    c23   no probe.jsonl on disk at ../runs/hz3/probe_c23_hz3q_s5
    ...
    !!! NO OCCUPANCY IS MEASURABLE.  The box claim is UNVERIFIED
```

**Cost, assessed.** Four `probe.jsonl` on ALICE at `/data1/salehkaleybars/metaopt/runs/hz3/`:
341 395 663 + 334 977 070 + 239 384 039 + 238 774 776 = **1 154 531 548 B ≈ 1.08 GiB**, against
**28 GiB free** on the local volume. Read-only `rsync` over the existing key login; **no Slurm job
was submitted** and both queues were left alone.

**Done, and verified byte-for-byte.** sha256 of all four `probe.jsonl`, local vs remote:

```
node  0d85a909e443d29c   ch  f0ef8d88432c4e91   n1d  919b7b3197c53d8d   c23  03e39a1db010e1eb   (both sides)
```

**Consequence.** `c99_hz3q_score.py`, re-run unedited, now reports **`H1 PASS`** with `coord_lo`
and `coord_hi` **exactly 0.000000** on n = 500 coordinates per arm at epochs 100, 200 and 300 —
which is exactly what `paper.tex:1163-1166` and the corresponding DRAFT paragraph already claim.

**No prose change is owed, and two things that look inconsistent are not.**

* §3.5's H1 sentence was already *correct*; it simply was not *locally* re-derivable. It is now.
  The gap was between the paper and the local tree, and the sync closed it in the direction that
  needed no wording change.
* The Data-Availability register's entry — `c99_hz3q`'s H0, H2, H3 and HC regenerable from the
  deposit **"but not its H1 box gate"** — remains **true**. It is a statement about the *deposit*,
  which excludes `probe*.jsonl` for size (≈42 GB). Syncing a local copy does not put them in the
  deposit. Do **not** "fix" that sentence; it is still right.

---

## 6. Owed item 2 — Figure 3 panel (b): **REDRAWN**, and why

### 6.1 The decision, and the argument for it

**Redraw.** The caption's disclosure was the right move while panel (b) merely *lagged*. It is not
enough now, for two reasons that are about the panel's own ink rather than about tidiness:

1. **The panel printed a claim the paper has since withdrawn, inside the panel, with no
   supersession marker.** Its italic annotation read:

   > *neither interval excludes zero: the flat verdict does not turn on the box-mismatched seed —
   > but its t does (−1.42 vs −1.94)*

   On the repaired data the interval **does** exclude zero and the verdict **does** turn on that
   seed. The caption disclosed that the *panel* was archival; it did not retract the *sentence
   drawn inside the panel*. A referee who reads figures before captions — most of them — meets our
   superseded conclusion asserted flatly. That is a liability the caption cannot cover, and it is
   exactly the "assertion-only guard" failure mode R3 was raised about.
2. **It reported two of three readings, which the registration forbids.** `c99_hz3q_score.py`'s own
   combination rule is `ALL THREE ARE REPORTED TOGETHER, ALWAYS`. §4.8's two tables obey it; panel
   (b) did not.

Redrawing loses nothing, because **the archived readings stay in the panel**. The disclosure is
preserved *and* made visual: panel (a) now shows the archived seed-5 trajectory (red, rising across
the budget) beside the repaired one (green, falling), which is R5's mechanism drawn rather than
asserted.

### 6.2 What changed — **ALREADY APPLIED**

`analysis/c98_figures.py`, `fig3()` only:

* reads `hz3q-{ch,node}-s*.out` and builds the repaired pool by **substituting** seed 5 (it adds no
  seed); if those files are absent the panel **degrades to exactly what it drew before** — the two
  archived readings and the old annotation. The repair is opt-in on data presence, not hard-coded.
* panel (a): adds the repaired seed-5 trace and the repaired 6-seed mean; both in-panel annotations
  replaced by legend entries; `figsize` 3.3 → 3.5 in, `wspace` 0.28 → 0.42, `ylim` top → 1.62 to
  seat the 5-entry legend clear of the data.
* panel (b): three rows, repaired first and labelled `REPAIRED, 6`; annotation replaced.
* `--numbers` prints the repaired ladder too.
* new palette constant `REPC = "#007A4D"`.

Regenerated `paper/figures/f3_budget.{pdf,png}`. `--numbers` output agrees with §4.8's tables to
the last digit: repaired D(100) +0.632 / D(200) +0.512 / D(300) +0.394, D(300)−D(100) −0.238
se 0.093 t −2.57. **The figure invents no number.**

### 6.3 EXACT REPLACEMENT TEXT — the Figure 3 caption

The caption's numeral multiset is **unchanged** (`{2.3026, 9.0, 0.149, 0.105, 1.42, 0.207, 0.107,
1.94, 0.238, 0.093, 2.57}` before and after), so this edit cannot move the numeric diff.

#### `paper/paper.tex` — replace verbatim (`count == 1`)

```tex
\caption{\textbf{$\Dstat$ at 1$\times$, 2$\times$ and 3$\times$ the budget, paired WITHIN run,
and what one box-mismatched seed does to it.} \arm{hz3} ran the four arms for 300 epochs at six
seeds, so $\Dstat$ can be read off the same run at three budgets, cancelling seed, run and batch
identically. (a) Faint lines are the six per-seed trajectories; the two heavy lines are the
arm-set means with 95\% intervals. \textbf{Seed 5 is drawn in red because it is not box-matched}:
its chunk arm ran in $\beta$-box $-15{:}{-}2.3026$ and its \arm{nodewise} arm in $-30{:}9.0$, so
that seed's $\Dstat$ is a cross-box difference and the other five are not. (b) The budget slope
both ways. $\Dstat$ is present and resolved at every budget. \textbf{The panel is drawn on the
archive}, in which the slope does not resolve either on all six seeds ($-0.149 \pm 0.105$,
$t\ -1.42$) or on the five box-matched seeds alone ($-0.207 \pm 0.107$, $t\ -1.94$). \textbf{Seed
5 has since been re-run box- and class-matched, and on that repaired pool the slope does resolve:
$-0.238 \pm 0.093$, $t\ -2.57$} (\S\ref{sec:budget}). The red trajectory is therefore the reading
this figure supersedes, kept because the published record is part of the evidence.}
```

#### `paper/paper.tex` — with

```tex
\caption{\textbf{$\Dstat$ at 1$\times$, 2$\times$ and 3$\times$ the budget, paired WITHIN run,
and what one box-mismatched seed did to it.} \arm{hz3} ran the four arms for 300 epochs at six
seeds, so $\Dstat$ can be read off the same run at three budgets, cancelling seed, run and batch
identically. (a) Faint blue lines are the archived per-seed trajectories; the heavy lines are
arm-set means with 95\% intervals. \textbf{Seed 5 is drawn in red because it is not box-matched}:
its chunk arm ran in $\beta$-box $-15{:}{-}2.3026$ and its \arm{nodewise} arm in $-30{:}9.0$, so
that seed's $\Dstat$ is a cross-box difference and the other five are not. The green dotted trace
is that same seed re-run box- and class-matched (\arm{hz3q}): \textbf{the archived reading rises
across the budget and the repaired one falls}, which is the whole of the repair. (b) The budget
slope, \textbf{all three readings together}, which is what the repair's own registered scorer
requires. It does not resolve on the six archived seeds ($-0.149 \pm 0.105$, $t\ -1.42$) or on the
five box-matched seeds alone ($-0.207 \pm 0.107$, $t\ -1.94$), and it does resolve, barely, on the
repaired pool ($\mathbf{-0.238 \pm 0.093}$, $t\ \mathbf{-2.57}$; \S\ref{sec:budget}). The archived
readings are kept in the panel rather than replaced by it, because the published record is part of
the evidence.}
```

#### `paper/DRAFT-v4.md` — replace verbatim (`count == 1`)

```markdown
**Figure 3 — D at 1×, 2× and 3× the budget, paired WITHIN run, and what one box-mismatched seed
does to it.** `hz3` ran the four arms for 300 epochs at six seeds, so D can be read off the same
run at three budgets, cancelling seed, run and batch identically. (a) Faint lines are the six
per-seed trajectories; the two heavy lines are the arm-set means with 95% intervals. **Seed 5 is
drawn in red because it is not box-matched**: its chunk arm ran in β-box −15:−2.3026 and its
nodewise arm in −30:9.0, so that seed's D is a cross-box difference and the other five are not.
(b) The budget slope both ways. D is present and resolved at every budget. **The panel is drawn on
the archive**, in which the slope does not resolve either on all six seeds (−0.149 ± 0.105,
t −1.42) or on the five box-matched seeds alone (−0.207 ± 0.107, t −1.94). **Seed 5 has since been
re-run box- and class-matched, and on that repaired pool the slope does resolve: −0.238 ± 0.093,
t −2.57** (§4.8). The red trajectory is therefore the reading this figure supersedes, kept because
the published record is part of the evidence.
```

#### `paper/DRAFT-v4.md` — with

```markdown
**Figure 3 — D at 1×, 2× and 3× the budget, paired WITHIN run, and what one box-mismatched seed
did to it.** `hz3` ran the four arms for 300 epochs at six seeds, so D can be read off the same
run at three budgets, cancelling seed, run and batch identically. (a) Faint blue lines are the
archived per-seed trajectories; the heavy lines are arm-set means with 95% intervals. **Seed 5 is
drawn in red because it is not box-matched**: its chunk arm ran in β-box −15:−2.3026 and its
nodewise arm in −30:9.0, so that seed's D is a cross-box difference and the other five are not.
The green dotted trace is that same seed re-run box- and class-matched (`hz3q`): **the archived
reading rises across the budget and the repaired one falls**, which is the whole of the repair.
(b) The budget slope, **all three readings together**, which is what the repair's own registered
scorer requires. It does not resolve on the six archived seeds (−0.149 ± 0.105, t −1.42) or on the
five box-matched seeds alone (−0.207 ± 0.107, t −1.94), and it does resolve, barely, on the
repaired pool (**−0.238 ± 0.093, t −2.57**; §4.8). The archived readings are kept in the panel
rather than replaced by it, because the published record is part of the evidence.
```

---

## 7. `analysis/c98_reproduce.py` — 44 new assertions, **DELIVERED AS TEXT, NOT APPLIED**

Every claim-carrying number in §2 and §3 should be asserted, in the paper's own idiom. The block
below was written, applied to a scratch copy, and run: **all 44 new checks PASS.** It is delivered
rather than applied because `c98_reproduce.py` is the file concurrent packages are most likely to
touch, and because the census in §7.1 can only be settled once *all* packages have landed.

Insert immediately after this anchor in `budget()` (`count == 1`):

```python
    chk("epoch the -15 floor first becomes reachable",
        math.ceil((math.log(1e-3) - (-15.0)) / (1e-4 * 500)), 162, "§3.5 R2, §7 T9", "%.0f")
```

```python
    # ---- §4.8 R3: the extrapolation a referee computes, and why it is not usable ----
    D_ = lambda s, B: pl5(CH[s], B) - pl5(ND[s], B)
    D100 = st.mean([D_(s, 100) for s in seeds]); D300 = st.mean([D_(s, 300) for s in seeds])
    slope = m_ / 200.0                              # m_ is the repaired D(300)-D(100)
    chk("epochs past 300 to a LINEAR zero (0.394/(0.238/200))",
        0.394 / (0.238 / 200.0), 331, "§4.8 R3", "%.0f")
    chk("   linear zero-crossing, rounded ladder", 300 + 0.394 / (0.238 / 200.0), 631,
        "§4.8 R3", "%.0f")
    chk("   linear zero-crossing, unrounded ladder", 300 + D300 / (-slope), 630,
        "§4.8 R3", "%.0f")
    n3, sB, sD = 3, sum((100, 200, 300)), D100 + st.mean([D_(s, 200) for s in seeds]) + D300
    Ds = [D100, st.mean([D_(s, 200) for s in seeds]), D300]
    sBB = sum(b * b for b in (100, 200, 300)); sBD = sum(b * d for b, d in zip((100, 200, 300), Ds))
    sl = (n3 * sBD - sB * sD) / (n3 * sBB - sB * sB); ic = (sD - sl * sB) / n3
    chk("   least-squares line through all three points, zero at", -ic / sl, 630,
        "§4.8 R3", "%.0f")
    chk("   crossing at the steep end of the registered CI [-0.477, -0.000]",
        300 + D300 / (0.477 / 200.0), 465, "§4.8 R3", "%.0f")
    for a, b, ed, ese, et in ((100, 200, -0.120, 0.142, -0.84), (200, 300, -0.118, 0.096, -1.23)):
        v = [D_(s, b) - D_(s, a) for s in seeds]
        mm, ss_ = st.mean(v), st.stdev(v) / math.sqrt(len(v))
        chk("D(%d)-D(%d), repaired -- the half-interval" % (b, a), mm, ed, "§4.8 R3")
        chk("   se", ss_, ese, "§4.8 R3", "%.3f")
        chk("   t  (NEITHER half resolves; only the full span does)", mm / ss_, et,
            "§4.8 R3", "%.2f")
    lb = [math.log(b) for b in (100, 200, 300)]
    sB2 = sum(lb); sBB2 = sum(b * b for b in lb); sBD2 = sum(b * d for b, d in zip(lb, Ds))
    sl2 = (n3 * sBD2 - sB2 * sD) / (n3 * sBB2 - sB2 * sB2); ic2 = (sD - sl2 * sB2) / n3
    chk("   log-budget fit, zero at", math.exp(-ic2 / sl2), 2034, "§4.8 R3", "%.0f")
    ld = [math.log(d) for d in Ds]
    sD3 = sum(ld); sBD3 = sum(b * d for b, d in zip((100, 200, 300), ld))
    sl3 = (n3 * sBD3 - sB * sD3) / (n3 * sBB - sB * sB); ic3 = (sD3 - sl3 * sB) / n3
    chk("   exponential fit, D(600) -- it never reaches zero", math.exp(ic3 + sl3 * 600), 0.195,
        "§4.8 R3")
    chk("   worst residual of the three two-parameter fits (pp)",
        max(max(abs(d - (ic + sl * b)) for b, d in zip((100, 200, 300), Ds)),
            max(abs(d - (ic2 + sl2 * b)) for b, d in zip(lb, Ds)),
            max(abs(d - math.exp(ic3 + sl3 * b)) for b, d in zip((100, 200, 300), Ds))),
        0.020, "§4.8 R3 -- all three fit inside the per-point se", "%.3f")
    for tag, A_, g1, g2, se2 in (("chunk777", CH, 0.693, -0.016, 0.055),
                                 ("nodewise", ND, 0.813, 0.102, 0.096)):
        chk("%s paired gain 100->200 (both arms saturate)" % tag,
            st.mean([pl5(A_[s], 200) - pl5(A_[s], 100) for s in seeds]), g1, "§4.8 R3")
        v = [pl5(A_[s], 300) - pl5(A_[s], 200) for s in seeds]
        chk("   %s paired gain 200->300" % tag, st.mean(v), g2, "§4.8 R3")
        chk("      se", st.stdev(v) / math.sqrt(len(v)), se2, "§4.8 R3", "%.3f")

    # ---- §4.8 R5: HOW the reversal happens.  Dropping s5 does NOT produce it. ----
    d5 = [D_(s, 300) - D_(s, 100) for s in seeds if s != 5]          # five clean seeds
    m5, se5 = st.mean(d5), st.stdev(d5) / math.sqrt(len(d5))
    x = dd[5]                                                        # hz3q's seed-5 delta
    chk("dropping seed 5 alone: delta (STILL FLAT)", m5, -0.207, "§4.8 R5, §3.5")
    chk("   se", se5, 0.107, "§4.8 R5", "%.3f")
    chk("   t  (|t| < 2.0 -> the deletion does NOT reverse the verdict)", m5 / se5, -1.94,
        "§4.8 R5", "%.2f")
    chk("hz3q seed-5 delta, the replacement", x, -0.396, "§4.8 R5")
    chk("   LOCATION: (x - mean5)/6, one sixth of its distance from the mean",
        (x - m5) / 6.0, -0.0315, "§4.8 R5", "%+.4f")
    chk("   mean5 unrounded", m5, -0.2068, "§4.8 R5", "%+.4f")
    chk("   mean5 + (x-mean5)/6 == the repaired estimate", m5 + (x - m5) / 6.0, -0.2383,
        "§4.8 R5", "%+.4f")
    chk("   PRECISION: se falls 5 -> 6 seeds", se_, 0.093, "§4.8 R5", "%.3f")
    chk("   |t| ratio 5 -> 6 seeds", abs((m_ / se_) / (m5 / se5)), 1.327, "§4.8 R5", "%.3f")
    chk("      location factor |m6/m5|", abs(m_ / m5), 1.152, "§4.8 R5", "%.3f")
    chk("      precision factor se5/se6", se5 / se_, 1.152, "§4.8 R5", "%.3f")
    chk("      location share of the move, in logs (%)",
        100 * math.log(abs(m_ / m5)) / math.log(abs((m_ / se_) / (m5 / se5))), 50.1,
        "§4.8 R5", "%.1f")
    chk("      precision share (%)",
        100 * math.log(se5 / se_) / math.log(abs((m_ / se_) / (m5 / se5))), 49.9,
        "§4.8 R5", "%.1f")
    chk("the replacement is NOT an outlier: |z| against the five archived seeds' spread",
        abs((x - m5) / st.stdev(d5)), 0.79, "§4.8 R5", "%.2f")
    chk("   its rank among the repaired six, most negative = 1",
        sorted(dd).index(x) + 1, 3, "§4.8 R5", "%.0f")
    arch = [(pl5(ch[s], 300) - pl5(nd[s], 300)) - (pl5(ch[s], 100) - pl5(nd[s], 100))
            for s in seeds]
    chk("   the ARCHIVED seed-5 delta it displaces", arch[5], 0.142, "§4.8 R5")
    chk("   its rank among the archived six, most POSITIVE = 1",
        sorted(arch, reverse=True).index(arch[5]) + 1, 1, "§4.8 R5", "%.0f")
    jt = []
    for i in range(len(seeds)):
        v = [dd[j] for j in range(len(dd)) if j != i]
        jt.append(abs(st.mean(v) / (st.stdev(v) / math.sqrt(len(v)))))
    for i, exp in enumerate((2.29, 2.50, 1.94, 1.94, 3.98, 1.94)):
        chk("   leave-one-out |t|, seed %d dropped" % i, jt[i], exp, "§4.8 R5", "%.2f")
    chk("   how many of the six deletions fall back under |t| = 2.0",
        sum(1 for v in jt if v < 2.0), 3, "§4.8 R5 -- the sensitivity is n=6, not seed 5", "%.0f")
```

### 7.1 MANDATORY follow-up — §3.4's self-census goes stale

`paper.tex:1043-1044` and `DRAFT-v4.md:834-835` print:

> audit executes **584 claim-carrying assertions covering 389 of the 872 distinct
> quantity-numerals** in this manuscript, which is 44.6 % of them.

Adding assertions and adding prose both move all four numbers. With this package's checks applied
to the *unmodified* paper the dry run reported `628 / 392 / 45.0 %`; with this package's prose also
applied the denominator moves again, and other packages will move it further. **Do not copy those
figures.** After every package has landed, run `python3 analysis/c98_reproduce.py`, read the three
census lines it FAILs on, and set §3.4's four numerals to what it prints — **in both markups**.
`c98_reproduce.py` says this of itself: *"A FAIL means that sentence has gone stale."*

### 7.2 Also mandatory — rebuild the release artefact

`release/figures/f3_budget.{pdf,png}` and `release/code/c98_figures.py` are now stale against
`paper/figures/` and `analysis/`, and `release/MANIFEST.md5` still checksums the old figure.
`release/README.md` documents the fix: **`python3 analysis/c98_release.py`**, which recopies the
code, regenerates the figures and rewrites `MANIFEST.md5`. Run it after integration, not before.

---

## 8. Verification log

Everything below was run in this session, on the working tree, at HEAD `fe957e4`.

| check | result |
|---|---|
| `c99_hz3q_score.py --selftest` | `selftest: 59/59 PASS` |
| `c99_hz3q_score.py` unedited, full run | H0 PASS · **H1 PASS (new)** · HC +0.134 pp · H2 `NOT FLAT — D DECLINES WITH BUDGET` |
| hz3q probe sync, sha256 local vs ALICE | 4/4 identical |
| `c98_reproduce.py`, live tree | exit 0, **ALL 592 CHECKS PASS** (unchanged) |
| `paper_numeric_diff.py`, live tree | 3 + 5 = **8 residuals** (the known pre-existing set) |
| **dry-run integration** of all six prose blocks, numeric diff | tex-only `['0.05', '3.0', '39,172']`, md-only `['0.087', '0.279', '3.19', '9.0', '9.0']` — **the same 8, no NEW residuals** |
| dry-run `tectonic -X compile` | **exit 0** |
| dry-run TeX warnings | **117**, identical to the baseline's 117 — no new over/underfull boxes |
| dry-run page count | **75 pp** (baseline 74; the R3 and R5 prose adds one page) |
| `c98_figures.py --fig f3 --numbers` after redraw | repaired ladder matches §4.8's table exactly |
| `tectonic` on live `paper.tex` **with the new figure** | exit 0, **74 pp**, 117 warnings |
| candidate `c98_reproduce.py` + 44 new checks | **all 44 PASS**; only the 3 self-census sites FAIL, as §7.1 predicts |

**Reported honestly:** the page count goes **74 → 75**. That is this package's prose, not a
regression, and it will move again as the other packages land.

### 8.1 Not done, and why

* **No Slurm job was submitted.** Both queues untouched. The 600-epoch run that would settle R3's
  extrapolation is named in the new prose as not run, which is the correct disposition.
* **`paper/paper.tex` and `paper/DRAFT-v4.md` were not edited** and nothing was committed.
* **§3.5, the abstract, T9, the end matter, CRediT, Funding, the author list and the correspondence
  address were not touched** — R1 and R2 are other packages' scope, and the end matter is the
  user's.
* **No ORCID, affiliation, grant number or DOI was invented.**

---

## 9. Integration checklist

1. Append §2.3's tex block after its anchor in `paper/paper.tex`; append §2.3's md block after its
   anchor in `paper/DRAFT-v4.md`.
2. Append §3.4's tex and md blocks after their anchors.
3. Replace the Figure 3 caption in both files with §6.3. **This step is not optional** — the
   figure is already redrawn.
4. Apply §7's `c98_reproduce.py` block.
5. Run `python3 analysis/c98_reproduce.py`; update §3.4's four census numerals in **both** markups
   from its FAIL lines (§7.1).
6. Run `python3 analysis/paper_numeric_diff.py` — expect the same 8 residuals, no more.
7. Run `python3 analysis/c98_reproduce.py` again — expect exit 0.
8. `tectonic -X compile paper.tex` — expect exit 0.
9. `python3 analysis/c98_release.py` (§7.2), then commit.
