# PACKAGE `budget-reversal` — the withdrawn budget-flatness claim

**Status of this file.** Finished prose plus EXACT replacement text for BOTH `paper/paper.tex`
and `paper/DRAFT-v4.md`, keyed to verbatim anchors each verified `count == 1` against the live
files at HEAD `17b9af7`. Nothing in `paper.tex` or `DRAFT-v4.md` was edited by this package; a
later agent integrates. No Slurm job was submitted; the queue was read only (`squeue -u $USER`
returns an empty table).

---

## 0. WHAT I RAN, AND WHAT IT SAID

### 0.1 The registered scorer, unedited

```
$ python3 analysis/c99_hz3q_score.py --selftest
selftest: 59/59 PASS
```

`sha256(analysis/c99_hz3q_score.py) = 50d95083c8ce444d609fa6b2ae4edb48f0dc7632154151efa12a0e17c68eef8e`
`sha256(analysis/c87_hz3_score.py) = 0be1f5201d43163b0afc9c9f81fa38a62c90e8eb811929caea8deb4b2be7561e`
— the second is byte-equal to `c99`'s own `PARENT_SHA256` pin, so the imported reader is the
registered one.

**A reproducibility defect found while doing this, and it must be recorded.** Run from the local
backup tree (`alice-backup/runs`), the scorer's H1 box gate **cannot be evaluated**: the four
directories `runs/hz3/probe_{node,ch,n1d,c23}_hz3q_s5/` exist locally but are **empty**, and the
scorer prints `no probe.jsonl on disk` four times followed by

> `!!! NO OCCUPANCY IS MEASURABLE.  The box claim is UNVERIFIED; every`
> `!!! number below is reported WITHOUT a box gate and must be written that way.`

The gate refused rather than silently passing, which is the correct behaviour. The probe records
do exist on ALICE (`/data1/salehkaleybars/metaopt/runs/hz3/probe_node_hz3q_s5/probe.jsonl`,
341,395,663 bytes); the rsync into the backup predated them. I therefore staged the two scorers
and `bin/c99_hz3q_quartet.sh` into a repo-shaped directory on ALICE (`c99pkg2/`, sha256-verified
identical to the committed files), re-ran the selftest there (**59/59 PASS**), and ran the scorer
against the real probe tree. **The hz3q probe records must be synced into the backup before the
deposit is cut, or the H1 gate is unreproducible from the artefact we ship.** Left open below.

### 0.2 The verdict, quoted verbatim

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
      **REGISTERED VERDICT: NOT FLAT -- D DECLINES WITH BUDGET**
      123.2's published sentence is: "D is present and resolved at a
      3x budget and is statistically FLAT from 100 to 300 epochs."
      IT DOES NOT STAND on the repaired data.  WITHDRAW IT.

    ALL THREE ARE REPORTED TOGETHER, ALWAYS.  The repaired reading does not
    replace the published one in the record; it is the disclosed repair of
    the one seed whose contrast was cross-box and cross-class.
```

and

```
    H1 PASS -- worst coordinate fraction 0.000000 (bar 0.05); EXACTLY ZERO, as the arithmetic requires.
    ...
    delta = +0.134 pp   bar |delta| <= 1.00 pp
    DISCLOSURE: GPU CLASS NOT FIRST-ORDER ON THE LEVEL
    ...
--- H3  SECONDARY.  D(300), G(300), D-G.  NEVER GATING -----------------
    as published n=6v6  D(300) +0.428 se 0.086 t +4.94 | G(300) -0.057 se 0.061 | D-G +0.484
      re-derivation check: +0.428 vs the record's +0.428 -- AGREES.
    repaired     n=6v6  D(300) +0.394 se 0.093 t +4.25 | G(300) -0.048 se 0.061 | D-G +0.442
```

### 0.2b The three other things I ran, so the paper may assert them

**STANDING RULE 20 sweep on the quartet's own `ARGS:` lines:**
```
$ python3 analysis/argsline_guard.py ../runs/hz3q-{node,ch,n1d,c23}-s5-*.out
  hz3q-node-s5-4864632.out: no repeated flag (20 flags)   [+ 3 more]
argsline_guard: 4 clean, 0 WITH REPEATED FLAGS OR DESIGN MISMATCH, 0 without an ARGS line
VERDICT: PASS
```
Effective values on the `nodewise` arm, read off the run: `--meta-stepsize 1e-4`,
`--alpha0 1e-3`, `--num-epochs 300`, `--seed 5`, `--stepsize-groups nodewise`, `--alg-base SGDm`,
`--alg-meta Lion`, `--dataset CIFAR10`, `--NN-name ResNet18`, `--batch-size 100`, `--gamma 1`.

**Slurm provenance (`sacct -X`), which is what TEX-14/16 and MD-12/14 assert:**
```
4855960   hz3-ch-s5    gpu-2080ti-11g  CANCELLED  00:00:00  None assigned
4855961   hz3-c23-s5   gpu-2080ti-11g  CANCELLED  00:00:00  None assigned
4855962   hz3-n1d-s5   gpu-2080ti-11g  CANCELLED  00:00:00  None assigned
4864632   hz3q-node-s5    gpu-l4-24g   COMPLETED  02:10:59  node883
4864633   hz3q-ch-s5      gpu-l4-24g   COMPLETED  02:36:19  node883
4864634   hz3q-n1d-s5     gpu-l4-24g   COMPLETED  02:31:27  node883
4864635   hz3q-c23-s5     gpu-l4-24g   COMPLETED  02:34:20  node883
```
and for the archived seed-5 quartet, the three partitions T9 now names:
```
4782027   hz3-node-s5  gpu-2080ti-11g  COMPLETED  node855
4814293   hz3-ch-s5      gpu-a100-80g  COMPLETED  node872
4814294   hz3-n1d-s5     gpu-a100-80g  COMPLETED  node873
4814295   hz3-c23-s5      gpu-mig-40g  COMPLETED  node868
```
`squeue -u $USER` returns an empty table. **No job was submitted by this package.**

**Non-overwrite, asserted twice.** `python3 analysis/c87_hz3_score.py --runs ../runs --probes
../runs/hz3`, unedited: `grep -c hz3q` on its output = **0**, and its verdicts are unchanged —
`SURVIVES` ("The partition gap is NOT an artefact of a 100-epoch budget") and `MECHANISM SURVIVES
THE HORIZON`. Separately, `python3 analysis/c98_reproduce.py`'s `[7] BUDGET` block passes all
eleven of its published assertions after the ingest, exactly as before it.

### 0.3 Independent re-derivation — the briefing's figures are CORRECT

Recomputed from the `.out` epoch series through `c87_hz3_score.py`'s own
`series_from_out` / `window_at`, without the scorer:

| pool | n | δ = D(300) − D(100) | se | t | df | two-sided p |
|---|---|---|---|---|---|---|
| as published | 6 | −0.1487 | 0.1047 | −1.419 | 5 | 0.215 |
| seed 5 dropped | 5 | −0.2068 | 0.1067 | −1.938 | 4 | 0.125 |
| **repaired** | 6 | **−0.2383** | **0.0927** | **−2.572** | 5 | **0.0499** |

95% interval on the repaired δ: **[−0.477, −0.000]**.

Per-seed δ: s0 −0.154 · s1 −0.088 · s2 −0.454 · s3 −0.440 · s4 +0.102 · s5(archived) **+0.142**
· s5(repaired) **−0.396**.

D(300) 6 v 6 Welch: as published **+0.4277 ± 0.0865, t 4.944** (Welch df 9.68); repaired
**+0.3937 ± 0.0926, t 4.250** (df 9.97, p 0.0017). Both match the scorer to the printed digit.

**No figure in the briefing is wrong.** Two things it under-states and one it over-states, all
recorded in §7 below.

---

## 1. THE PROSE — what the paper must now say

### 1.1 The claim that is withdrawn

The live paper does **not** contain the sentence CORRECTIONS 123.2 registered. §4.8 already
carries the demotion: *"We do not report flatness as a result."* What it **does** claim, and what
must now be withdrawn, is the sentence immediately before that one:

> **D does not grow with budget from 100 to 300 epochs, and we cannot resolve whether it decays.**

and the subsection title built on it — *"whether it decays is not resolved"* — and the three
downstream restatements of "a decline that does not resolve" (A.2, the contributions list,
Figure 3's caption). **On the repaired data the decay resolves.** The half of the sentence that
said we could not tell is false, and it is deleted, not softened.

### 1.2 The claim that is NOT withdrawn, and the sentence a referee must not be able to write

Contribution 1 is untouched. At 300 epochs, on the repaired pool, the partition gap is
**+0.394 ± 0.093 pp, t 4.25** — positive, resolved, and 4.25 standard errors from zero. The
published reading was +0.428 ± 0.086, t 4.94; the repair moves it by **0.034 pp**, four tenths of
one standard error. Every seed still favours `chunk777` at 300 epochs.

What changed is the *slope*, not the *level*. **D shrinks as the budget grows; it does not go
away.** Extrapolating the repaired slope naively, D would still be positive at 300 epochs by a
wide margin and the interval on the slope reaches zero at its upper end. The correct one-line
statement is:

> The gap survives a 3× budget at full strength, and it declines with budget at a rate our six
> seeds now resolve. Those are two findings, not one; the second does not weaken the first.

### 1.3 Why the published reading was wrong

Seed 5's contrast in `hz3` was **doubly confounded**, and the two confounds bite at different
budgets — which is exactly what a within-run pairing cannot cancel.

**The clip box, measured.** `hz3`'s seed-5 `chunk777`, `nodewise1d` and `chunk2325` runs carry
`BETA_CLIP=-15:-2.3026`; their own seed-5 `nodewise` partner, and all 20 other `hz3` runs, carry
`-30:9.0`. From β₀ = ln(10⁻³) = −6.907755 at ms·(steps/epoch) = 10⁻⁴ × 500 = 0.05 nats/epoch, the
−15 floor first becomes reachable at epoch ⌈8.092245 / 0.05⌉ = **162**. The probe records agree:
coordinate-floor occupancy for those three archived arms is **0.000000 at epoch 100** and
0.000485 / 0.001621 / 0.001443 at 200, rising to 0.008598 / 0.018323 / 0.008900 at 300; the
ceiling is never touched (`coord_hi` 0.000000 at every budget). **So seed 5's archived D(100) is
box-free and its archived D(300) is box-bound.** A within-run difference of the two therefore
carries a defect that is present at one end and absent at the other — the one shape of
contamination that pairing is powerless against, and the reason the archived seed-5 δ came out
**+0.142** when every other clean seed but one came out negative.

**The silicon, measured.** The registered constant `SEED_CLASS` in `c87_hz3_score.py:115` declares
all four seed-5 runs `gpu-2080ti-11g`. Their own headers say otherwise: `hz3-node-s5` on node855,
**RTX 2080 Ti**; `hz3-ch-s5` on node872 and `hz3-n1d-s5` on node873, **A100 80GB PCIe**;
`hz3-c23-s5` on node868, an **A100 MIG slice** — three Slurm partitions for one seed. Both sides
of `c87`'s own selftest for that map are declarations; neither reads a run. **The declared-constant
pattern is the defect, and no amount of care inside the registration could have caught it.**

**The repair, and its pre-registration.** `hz3q` re-runs **all four** arms at seed 5, 300 epochs,
`BETA_CLIP=-30:9.0`, in **one submission on one card** — jobs 4864632–35, all `COMPLETED` on
node883, partition `gpu-l4-24g`, NVIDIA L4, 2:10:59–2:36:19 wall. Box and GPU class are matched
*by construction* rather than by declaration, and the pair is generated internally: nothing depends
on an archived comparator. `c99_hz3q_score.py` was committed **before** those runs existed
(STANDING RULE 21), imports `c87`'s reader unedited (RULE 16), and its H0 provenance gate is
measured from each run's own header, never declared. Turned on the archive it is meant to refuse,
that gate **refuses it**, naming both defects:

```
REFUSED: GPU MODEL IS NOT SHARED across the four arms
REFUSED: BETA_CLIP IS NOT SHARED across the four arms
```

**And the bar that reversed us was frozen first.** `band_flat()` fixed `|t| < 2.0 → FLAT` at the
parent registration's own `CONFIRM_T`, and the file's own comment records that it was written
knowing the archived readings were −1.42 and −1.94 and that "the interesting outcome is the third
one: a repaired seed that pushes |t| past 2.0." It did: **−2.57**. **A threshold we committed to in
advance, in a file whose selftest asserts it, took our own headline away from us. That is the
strongest evidence this paper can offer for the methodological claim it makes, and it should be
stated as such rather than buried in an appendix.**

**What the repair moved, arm by arm** (plateau5, archived → repaired, seed 5 only; at B = 100
*all four* archived arms are box-free, so these are class-plus-nondeterminism differences alone):

| arm | B = 100 | B = 200 | B = 300 |
|---|---|---|---|
| `nodewise` | −0.204 | −0.012 | **+0.134** |
| `chunk777` | +0.130 | −0.026 | −0.070 |
| `nodewise1d` | +0.376 | +0.056 | +0.008 |
| `chunk2325` | +0.212 | +0.240 | +0.058 |

Seed 5's D(100) moves **+0.148 → +0.482** and its D(300) moves **+0.290 → +0.086**. The two ends
move in opposite directions, which is why the repair changes the *slope* far more than it changes
either *level*: repaired D(100) is +0.632 against a published +0.576 (+0.056), repaired D(300) is
+0.394 against +0.428 (−0.034), and the slope moves −0.149 → −0.238.

**T9's "unexplained extreme value" is therefore withdrawn.** It was not unexplained; it was not
reproducible. The archived seed-5 D(100) = +0.148 was an extreme draw of the same-configuration
scatter that the control arm itself displays — the `nodewise` arm, identically flagged and
identically boxed in both submissions, differs by 0.204 pp at B = 100 on its own. The correct
statement is that a matched re-run at the same seed does **not** reproduce it.

### 1.4 The HC cross-class control — what it licenses

`hz3q-node-s5` and `hz3-node-s5` are the **same** configuration, seed, clip box, flags and code.
Only the GPU class differs. plateau5(300): **92.908** (L4) vs **92.774** (RTX 2080 Ti),
**δ = +0.134 pp** against a bar of `|δ| ≤ 1.00` registered before the run.

> **DISCLOSURE: GPU CLASS NOT FIRST-ORDER ON THE LEVEL.**

This is a measurement `hz3`'s own design could not make: there, GPU class is a function of the
seed, so the class term and the seed term are perfectly aliased. It licenses exactly one thing —
that `hz3`'s per-seed **levels** may be read across seeds despite the class assignment — and it
touches **nothing** about D, which is a within-seed, within-class contrast in both batches and in
which the class cancels identically. It also cross-checks §6.3's corpus-wide hardware term: §6.3
measures 2080Ti − L4 = +0.035 pp over n = 45; the direct same-seed control gives −0.134 pp for the
same difference. Opposite sign, both an order of magnitude inside the 1.00 pp bar, and neither is
large enough to carry a claim — which is the point.

### 1.5 One further disclosure the referee will ask for

`c87_hz3_score.py`'s **registered primary window is 50 epochs**, and on `hz3` as published it
returns `GROWS`: +0.229 ± 0.070, t 3.27. That verdict stands unchanged — `c87` was re-run unedited
for this package, admits **zero** `hz3q` files (`grep -c hz3q` on its output = 0), and its printed
verdicts are identical to before (`SURVIVES` and `MECHANISM SURVIVES THE HORIZON`).

For completeness, and marked **unregistered** because `c87` is registered on `hz3` and `c99`'s
registered window is `plateau5`: recomputing `c87`'s own 50-epoch estimator on the repaired pool
gives **+0.161 ± 0.085, t 1.89**, which falls inside `c87`'s own `SAT_HALF` = 0.20 band, i.e. it
would read `SATURATES` rather than `GROWS`. **The repair moves the two windows toward each other,
not apart.** Part of the window discrepancy the paper discloses in §3.4 item 3 was the contaminated
seed. We do not restate `c87`'s verdict on data it was not registered for; we report that we looked.

---

## 2. REPLACEMENT TEXT — `paper/paper.tex`

Anchors verified `count == 1` in `paper/paper.tex` at HEAD `17b9af7` (see §6 for the checker).

### TEX-1 — §4.8 subsection title  (line ~2597)

**FIND (unique):**
```latex
\subsection{Budget: the effect survives 3$\times$ the budget; whether it decays is not resolved}
```
**REPLACE:**
```latex
\subsection{Budget: the effect survives 3$\times$ the budget, and it declines with it}
```

### TEX-2 — §4.8 opening, the "twice" sentence  (line ~2606)

**FIND (unique):**
```latex
2080 Ti (\S\ref{sec:threats} T9). We therefore report the budget contrast \textbf{twice}: as
submitted, and over the five clean seeds.
```
**REPLACE:**
```latex
2080 Ti (\S\ref{sec:threats} T9). That seed has since been re-run: \arm{hz3q} repeats
\textbf{all four} arms at seed 5 for 300 epochs in the batch's own box $-30{:}9.0$, in one
submission on one NVIDIA L4 (node883, jobs 4864632--35, all \texttt{COMPLETED}), so its box and
its GPU class are matched \emph{by construction} rather than by declaration and the seed-5 pair is
generated internally. \arm{hz3q} repairs one seed of \arm{hz3}; it is not a replication, not a new
design point and not a new cell, and it is counted as none of those. We therefore report the
budget contrast \textbf{three ways}: as published, over the five clean seeds, and repaired ---
and, following the repair's own registered scorer, we report all three together, always.
```

### TEX-3 — §4.8 table column spec  (line ~2612)

**FIND (unique):**
```latex
\begin{tabular}{@{}lrrrr@{}}
```
**REPLACE:**
```latex
\begin{tabular}{@{}lrrrrrr@{}}
```

### TEX-4 — §4.8 table body  (lines ~2615--2621)

**FIND (unique):**
```latex
budget & $\Dstat$, 6 seeds as submitted & $\se$ & $\Dstat$, 5 clean seeds & $\se$ \\
\midrule
100 & $+0.576$ & 0.109 & $\mathbf{+0.662}$ & 0.083 \\
200 & $+0.514$ & 0.115 & $\mathbf{+0.575}$ & 0.119 \\
300 & $+0.428$ & 0.071 & $\mathbf{+0.455}$ & 0.081 \\
```
**REPLACE:**
```latex
budget & $\Dstat$, 6 seeds as published & $\se$ & $\Dstat$, 5 clean seeds & $\se$ &
  $\Dstat$, \textbf{repaired} & $\se$ \\
\midrule
100 & $+0.576$ & 0.109 & $+0.662$ & 0.083 & $\mathbf{+0.632}$ & 0.074 \\
200 & $+0.514$ & 0.115 & $+0.575$ & 0.119 & $\mathbf{+0.512}$ & 0.116 \\
300 & $+0.428$ & 0.071 & $+0.455$ & 0.081 & $\mathbf{+0.394}$ & 0.090 \\
```
*(`se` here is the sem of the six per-seed $\Dstat$ values, as in the published columns; the
Welch estimator quoted in the prose is separate and is stated as such.)*

### TEX-5 — §4.8 "The level is robust" paragraph  (lines ~2622--2627)

**FIND (unique):**
```latex
\textbf{The level is robust, and it is the claim we make.} $\Dstat(300)$ reads
$+0.428 \pm 0.086$ at 6 v 6 ($t\ 4.94$) and $+0.455 \pm 0.096$ at 5 v 5 ($t\ 4.75$) on the Welch
estimator used everywhere else in this paper; all six seeds favour \arm{chunk777} at 300 epochs
(exact binomial $p = 0.0156$). \textbf{The partition gap is not an artefact of a 100-epoch
budget.}
```
**REPLACE:**
```latex
\textbf{The level is robust, and it is the claim we make.} $\Dstat(300)$ reads
$+0.428 \pm 0.086$ at 6 v 6 ($t\ 4.94$) as published, $+0.455 \pm 0.096$ at 5 v 5 ($t\ 4.75$),
and $\mathbf{+0.394 \pm 0.093}$ ($t\ \mathbf{4.25}$) repaired, on the Welch
estimator used everywhere else in this paper; all six seeds favour \arm{chunk777} at 300 epochs
on every one of the three readings (exact binomial $p = 0.0156$). The repair moves the level by
$0.034$ pp, four tenths of one $\se$. \textbf{The partition gap is not an artefact of a 100-epoch
budget, and nothing below weakens that.}
```

### TEX-6 — §4.8, THE WITHDRAWAL  (lines ~2628--2641)

**FIND (unique):**
```latex
\textbf{The trend is not robust, and we do not claim it.} Within-run,
```
…through the end of that paragraph. The full paragraph to be replaced runs from that anchor to,
and including, the second anchor:
```latex
(R2, \S\ref{sec:inflight}) is registered and will settle it; until it lands this cell carries its
sensitivity in the text.
```

**REPLACE the whole paragraph with:**
```latex
\textbf{The trend now resolves, and it resolves against a sentence we published.} The previous
version of this subsection said: \emph{``$\Dstat$ does not grow with budget from 100 to 300
epochs, and we cannot resolve whether it decays.''} \textbf{That sentence is withdrawn.} On the
repaired data the decay resolves. Within run, paired within seed at \plateau{},
$\Dstat(300) - \Dstat(100)$ reads

\begin{center}
\small
\begin{tabular}{@{}llrrrr@{}}
\toprule
reading & seeds & $n$ & $\delta$ & $\se$ & $t$ (df) \\
\midrule
as published & archived 0--5 & 6 & $-0.149$ & 0.105 & $-1.42$ (5) \\
seed 5 dropped & archived 0--4 & 5 & $-0.207$ & 0.107 & $-1.94$ (4) \\
\textbf{repaired} & archived 0--4 $+$ \arm{hz3q} seed 5 & 6 & $\mathbf{-0.238}$ & 0.093 &
  $\mathbf{-2.57}$ (5) \\
\bottomrule
\end{tabular}
\end{center}

\noindent
against a bar of $|t| \ge 2$ frozen in \texttt{c99\_hz3q\_score.py}'s \texttt{band\_flat()} at the
parent registration's own \texttt{CONFIRM\_T} \textbf{before \arm{hz3q} was submitted}. The
registered verdict on the repaired reading is \texttt{NOT FLAT --- D DECLINES WITH BUDGET}
($p = 0.050$ two-sided, 95\% interval $[-0.477,\ -0.000]$). \textbf{All three readings are
reported together, always}: the repaired one does not erase the published one from the record, it
is the disclosed repair of the one seed whose contrast was cross-box and cross-class.

\textbf{Read the withdrawal for exactly what it is.} $\Dstat$ \emph{shrinks} as the budget grows;
it does not go away. At 300 epochs it is $+0.394 \pm 0.093$, $t\ 4.25$ --- positive, resolved and
within four tenths of an $\se$ of the published value. The claim that dies is the narrower one
about the \emph{slope}. A reader who takes this paragraph as ``the effect disappears at longer
budgets'' has read it backwards, and \S\ref{sec:conclusion} states the two findings separately for
that reason.

\textbf{Why the published reading was wrong, and why it took a fifth run to see it.} Seed 5's
\arm{chunk777}, \arm{nodewise1d} and \arm{chunk2325} runs sat in a narrower clip box
\emph{and} on different silicon from their own \arm{nodewise} partner, and the two defects bite at
different budgets --- the one shape of contamination a within-run pairing cannot cancel. The
$-15$ floor first becomes reachable at epoch $\lceil 8.092245 / 0.05 \rceil = 162$, and the probe
records agree: floor occupancy for those three arms is $0.000000$ at epoch 100 and rises to
$0.0086$, $0.0183$ and $0.0089$ by epoch 300, with the ceiling never touched. So seed 5's archived
$\Dstat(100)$ is box-free and its archived $\Dstat(300)$ is box-bound. The hardware was worse than
mislabelled: \arm{hz3}'s registered scorer \emph{declares} all four seed-5 runs
\texttt{gpu-2080ti-11g}, while their own headers report an RTX 2080 Ti, two A100 80\,GB cards and
an A100 MIG slice across three Slurm partitions. Both sides of that scorer's own check are
declarations; neither reads a run. \arm{hz3q}'s provenance gate measures instead, and turned on
the archive it is built to refuse it refuses it on both counts.

\textbf{What the repair moved.} Seed 5's $\Dstat(100)$ goes $+0.148 \to +0.482$ and its
$\Dstat(300)$ goes $+0.290 \to +0.086$: the two ends move in \emph{opposite} directions, which is
why the repair changes the slope ($-0.149 \to -0.238$) far more than either level ($+0.576 \to
+0.632$ and $+0.428 \to +0.394$). At $B = 100$ all four archived seed-5 arms are box-free, so the
per-arm archived-to-repaired differences there --- $-0.204$, $+0.130$, $+0.376$, $+0.212$ for
\arm{nodewise}, \arm{chunk777}, \arm{nodewise1d}, \arm{chunk2325} --- are class-plus-nondeterminism
alone. The archived seed-5 $\Dstat(100)$ was not an unexplained extreme value; it was a draw a
matched re-run does not reproduce (\S\ref{sec:threats} T9).

\textbf{A frozen bar reversed our own headline, and that is the point.} The threshold that
withdrew this claim was committed to version control before the data that triggered it existed,
in a file whose selftest asserts it (59/59 PASS) and which imports the parent reader unedited
rather than re-implementing it. We report the reversal here, in full, rather than in an appendix,
because a registration that can only confirm is not a registration.
```

### TEX-7 — §4.8, the HC cross-class control (NEW paragraph)

**Insert immediately after the block replaced in TEX-6, before the paragraph beginning**
`One further reading must be disclosed rather than buried`.

```latex
\textbf{A control \arm{hz3}'s own design could not run.} \arm{hz3q-node-s5} and \arm{hz3-node-s5}
are the same configuration, the same seed, the same box, the same flags and the same code; only
the GPU class differs. Their \plateau{}(300) values are $92.908$ (L4) and $92.774$ (RTX 2080 Ti),
$\delta = \mathbf{+0.134}$ pp against a bar of $|\delta| \le 1.00$ pp registered before the run:
\textbf{GPU class is not first-order on the level}. In \arm{hz3} the class is a function of the
seed, so the class term and the seed term are perfectly aliased and this quantity is not
measurable there at all. It licenses one thing --- that \arm{hz3}'s per-seed \emph{levels} may be
read across seeds despite the class assignment --- and it touches nothing about $\Dstat$, which is
a within-seed, within-class contrast in both batches and in which the class cancels identically.
It also cross-checks \S\ref{sec:variance}, which measures 2080\,Ti $-$ L4 $= +0.035$ pp over
$n = 45$ configurations: the direct same-seed control gives $-0.134$ pp for the same difference.
The signs disagree and both sit an order of magnitude inside the disclosure bar, which is the
finding --- neither is large enough to carry a claim.
```

### TEX-8 — §4.8, the 50-epoch window paragraph, closing sentences  (line ~2660)

**FIND (unique):**
```latex
primary-window reading is a non-significant decline, and a reader is entitled to both. See
Appendix~\ref{app:discrepancy}.2.
```
**REPLACE:**
```latex
primary-window reading is a resolved decline, and a reader is entitled to both. That verdict is
\arm{hz3}'s and stands unchanged: \texttt{c87\_hz3\_score.py} was re-run unedited for this
revision, admits \textbf{no} \arm{hz3q} file, and prints what it printed before. For completeness
and marked \textbf{unregistered} --- \texttt{c87} is registered on \arm{hz3} and \arm{hz3q}'s own
registered window is \plateau{} --- recomputing \texttt{c87}'s 50-epoch estimator on the repaired
pool gives $+0.161 \pm 0.085$, $t\ 1.89$, inside that scorer's own $\pm 0.20$ \texttt{SATURATES}
band. \textbf{The repair moves the two windows toward each other, not apart}: part of the
discrepancy was the contaminated seed. We do not restate a registered verdict on data it was not
registered for; we report that we looked. See Appendix~\ref{app:discrepancy}.2.
```

### TEX-9 — Figure 3 caption  (lines ~2682--2688)

**FIND (unique):**
```latex
both ways. $\Dstat$ is present and resolved at every budget, and the slope does not resolve
either on all six seeds ($-0.149 \pm 0.105$, $t\ -1.42$) or on the five box-matched seeds alone
($-0.207 \pm 0.107$, $t\ -1.94$). Neither interval excludes zero, so the verdict does not turn on
the contaminated seed --- but its $t$ does, and we print both rather than choosing.}
```
**REPLACE:**
```latex
both ways. $\Dstat$ is present and resolved at every budget. \textbf{The panel is drawn on the
archive}, in which the slope does not resolve either on all six seeds ($-0.149 \pm 0.105$,
$t\ -1.42$) or on the five box-matched seeds alone ($-0.207 \pm 0.107$, $t\ -1.94$). \textbf{Seed
5 has since been re-run box- and class-matched, and on that repaired pool the slope does resolve:
$-0.238 \pm 0.093$, $t\ -2.57$} (\S\ref{sec:budget}). The red trajectory is therefore the reading
this figure supersedes, kept because the published record is part of the evidence.}
```
> **INTEGRATOR NOTE.** `analysis/c98_figures.py:469` selects on `re.match(r"hz3-(ch|node)-s(\d+)$")`,
> which does **not** match `hz3q-*`, so `f3_budget.pdf` is unchanged by the `hz3q` ingest and the
> caption above is true of the figure as it stands. Redrawing panel (b) with the repaired seed is
> a separate, desirable change to `c98_figures.py`; it is **left open**, not done here.

### TEX-10 — Table 2 dagger note  (lines ~1465--1470)

**FIND (unique):**
```latex
a 0.086 pp $\se$. Run R2 (\S\ref{sec:inflight}) restores a matched 6 v 6.
```
**REPLACE:**
```latex
a 0.086 pp $\se$. The box- and class-matched re-run of that seed (\arm{hz3q},
\S\ref{sec:inflight}) has since landed and restores a matched 6 v 6:
$\mathbf{+0.394 \pm 0.093}$, $t\ 4.25$, a shift of 0.034 pp. \textbf{Row 9 is not changed to that
value.} The corpus is frozen at the runs the cells were built from, and every pooled quantity in
\S\ref{sec:primary} and \S\ref{sec:moderator} --- including the exact enumeration of all
45{,}045 partitions of the fourteen cells --- is computed on it; \arm{hz3q} repairs one seed and
is disclosed, not substituted.
```

### TEX-11 — §3.4, discrepancy item 3  (lines ~992--995)

**FIND (unique):**
```latex
returns $-0.149 \pm 0.105$ ($t\ -1.42$). We keep \plateau{} for consistency and print the
```
**REPLACE:**
```latex
returns $-0.149 \pm 0.105$ ($t\ -1.42$) on the same archived seeds, and
$\mathbf{-0.238 \pm 0.093}$ ($t\ \mathbf{-2.57}$) once seed 5 is repaired. We keep \plateau{} for
consistency and print the
```

### TEX-12 — §3.5 opening  (line ~1063)

**FIND (unique):**
```latex
\S\ref{sec:threats}. One --- the \arm{hz3} seed-5 trio --- is not scored, and \textbf{no number
from it enters any claim in this paper}.
```
**REPLACE:**
```latex
\S\ref{sec:threats}. The fourth --- the \arm{hz3} seed-5 trio --- was \textbf{cancelled before it
started}, and \textbf{no number from it enters any claim in this paper}; it was superseded by a
four-arm quartet, \arm{hz3q}, whose own registered scorer withdrew one of this paper's claims
(\S\ref{sec:budget}).
```
> **Shared with the `N3` package.** If `N3` also rewrites this sentence, apply one of the two, not
> both.

### TEX-13 — Table 1 (`tab:inflight`) caption  (lines ~1079--1080)

**FIND (unique):**
```latex
scorers unedited; the fourth, the \arm{hz3} seed-5 trio, is queued and has never started and
contributes no number to this paper.
```
**REPLACE:**
```latex
scorers unedited; the fourth, the \arm{hz3} seed-5 trio, was cancelled before it started and
contributes no number to this paper --- it was replaced by the four-arm \arm{hz3q} quartet, which
ran, was scored by a scorer registered before it existed, and reversed one of our own claims.
```

### TEX-14 — Table 1 R2 row  (lines ~1089--1091)

**FIND (unique):**
```latex
R2 & \arm{hz3} seed-5 trio & 3 & the budget cell's clip-box and GPU-class mismatch
     (\S\ref{sec:budget}, \S\ref{sec:threats} T9) & \texttt{c87\_hz3\_score.py}, reused
     unedited & \textbf{queued, not started} \\
```
**REPLACE:**
```latex
R2 & \arm{hz3} seed-5 trio & 3 & the budget cell's clip-box and GPU-class mismatch
     (\S\ref{sec:budget}, \S\ref{sec:threats} T9) & \texttt{c87\_hz3\_score.py}, reused
     unedited & \textbf{CANCELLED before start; superseded by R2$'$} \\
R2$'$ & \arm{hz3q} seed-5 quartet & 4 & the same mismatch, repaired by re-running \textbf{all
     four} arms in one submission on one card & \texttt{c99\_hz3q\_score.py} &
     \textbf{SCORED --- flatness WITHDRAWN; $\Dstat$ DECLINES with budget
     (\S\ref{sec:budget})} \\
```
> **Shared with the `N3` package.**

### TEX-15 — §3.5, the R2 registration paragraph  (lines ~1126--1141)

**FIND (unique, paragraph head):**
```latex
\paragraph{R2 --- the \arm{hz3} seed-5 trio, re-run box- and hardware-matched.}
```
**REPLACE the paragraph head with, and append the new paragraph after the paragraph's existing
final sentence** (`\ldots because writing one would create two registrations for one question.`):
```latex
\paragraph{R2 --- the \arm{hz3} seed-5 trio, re-run box- and hardware-matched (CANCELLED).}
```
**APPEND after that paragraph:**
```latex
\paragraph{R2$'$ --- \arm{hz3q}, the box- and class-matched seed-5 \emph{quartet}.}
R2 was cancelled without ever starting: its three jobs (4855960--62) were priority-starved on
\texttt{gpu-2080ti-11g} with no assigned start time and elapsed \texttt{00:00:00}, so STANDING
RULE 20's post-launch \texttt{ARGS} check was never owed and no number from them exists.
It was replaced by a strictly stronger design. \arm{hz3q} re-runs \textbf{all four} arms ---
\arm{nodewise}, \arm{chunk777}, \arm{nodewise1d}, \arm{chunk2325} --- at seed 5 for 300 epochs at
$-30{:}9.0$ in \textbf{one submission on one card} (jobs 4864632--35, node883, \texttt{gpu-l4-24g},
NVIDIA L4, all \texttt{COMPLETED}), so the box and the GPU class are shared \emph{by construction}
and \textbf{nothing depends on an archived comparator}: R2 would have paired three fresh runs
against an archived \arm{nodewise} partner, and R2$'$ generates the pair internally. Because the
re-runs take \textbf{new names} (\arm{hz3q-\ldots}, probing into
\texttt{probe\_<short>\_hz3q\_s5}), no file of \arm{hz3}'s is renamed, moved, appended to or
deleted, and \texttt{c87\_hz3\_score.py} run unedited returns exactly what it returned before ---
asserted, not assumed, by the new scorer's \texttt{assert\_no\_overwrite()} and confirmed by
re-running \texttt{c87} for this revision. A \textbf{second} scorer exists because the first
\emph{cannot ask the question}: \texttt{c87\_hz3\_score.py:115} \emph{declares}
\texttt{SEED\_CLASS}, and both sides of its own check on that map are declarations. Editing it to
agree with data collected after it was registered is the move RULE 16 forbids, so
\texttt{analysis/c99\_hz3q\_score.py} was committed before any \arm{hz3q} run existed (RULE 21;
selftest 59/59 PASS), \textbf{imports} \texttt{c87}'s reader unedited under a pinned sha256 rather
than re-implementing it, and \textbf{measures} provenance from each run's own header. Its bands
were frozen with the archived readings in hand: $|t| < 2.0 \to$ \texttt{FLAT}, $|t| \ge 2.0 \to$
\texttt{NOT FLAT} with the sign naming the direction; a cross-class disclosure switch at
$1.00$ pp; a box gate whose registered expectation is \emph{exactly} zero. It returned
$t\ -2.57$ and took a claim of ours with it (\S\ref{sec:budget}).
```
> **Shared with the `N3` package.**

### TEX-16 — §3.5, "R2 is still queued"  (lines ~1231--1238)

**FIND (unique, paragraph head):**
```latex
\textbf{R2 is still queued and has never started.}
```
**REPLACE the whole paragraph** — from that anchor through, and including:
```latex
epochs does not exist and \textbf{\S\ref{sec:budget}'s budget verdict is unchanged}.
```
**with:**
```latex
\textbf{R2 was cancelled before it started, and R2$'$ ran in its place.} The three seed-5 jobs
(4855960--62, \arm{hz3-ch-s5}, \arm{hz3-c23-s5}, \arm{hz3-n1d-s5}) sat \texttt{PENDING} with
elapsed \texttt{0:00} and no assigned start time on a congested partition, and were cancelled
rather than left to age; \texttt{sacct} records them \texttt{CANCELLED} at
\texttt{00:00:00} elapsed. No \texttt{.out} file was ever written for any of the three, so
STANDING RULE 20's post-launch \texttt{ARGS} check was never owed and \textbf{no number from R2
exists anywhere in this paper}. The replacement, R2$'$ (\arm{hz3q}), ran to completion on one L4
and was scored by \texttt{analysis/c99\_hz3q\_score.py}, registered before it. Its RULE 20 sweep
returns 4 clean arms and 0 repeated flags. \textbf{\S\ref{sec:budget}'s budget verdict is
therefore changed, and the change is a withdrawal of ours}: the box-matched 6 v 6 at 300 epochs
now exists and reads $+0.394 \pm 0.093$, $t\ 4.25$, while the budget \emph{slope}, which the
previous version reported as unresolved, resolves at $-0.238 \pm 0.093$, $t\ -2.57$.
```
> **Shared with the `N3` package.**

### TEX-17 — §7 T9, the hardware paragraph's last clause  (line ~3850)

**FIND (unique):**
```latex
recorded here, and R2 makes the label true again.
```
**REPLACE:**
```latex
recorded here. The replacement runs (\arm{hz3q}, \S\ref{sec:inflight}) do not repair the label ---
under the file-freeze rule \texttt{c87}'s constant stays as registered --- they make it
unnecessary: \arm{hz3q}'s own scorer reads the GPU model off each run's header instead of
declaring it, and \textbf{that is the general lesson of this threat item}. A registered constant
that no run is ever compared against is a decoration; the repair is to measure, not to re-declare.
```

### TEX-18 — §7 T9, the outlier paragraph  (lines ~3858--3867)

**FIND (unique):**
```latex
Seed 5 is also the batch's per-seed outlier at 100 epochs --- $\Dstat(100) = \mathbf{+0.148}$
```
**REPLACE the whole paragraph** — from that anchor through, and including:
```latex
trio in the original box and on matched hardware is R2 (\S\ref{sec:inflight}).
```
**with:**
```latex
Seed 5 is also the batch's per-seed outlier at 100 epochs --- $\Dstat(100) = \mathbf{+0.148}$
against $\mathbf{+0.548}$, $\mathbf{+0.564}$, $\mathbf{+0.586}$, $\mathbf{+0.622}$,
$\mathbf{+0.990}$ --- and unremarkable at 300 ($+0.290$, against a seed-2 low of $+0.168$). The
previous version of this paragraph called that value \emph{unexplained}, having established that
neither defect could produce it: the box is inert at 100 epochs (floor occupancy measured at
$0.000000$ for all three arms there, the floor first reachable at epoch 162), and the hardware
term (\S\ref{sec:variance}: A100 $-$ 2080\,Ti $= +0.112$ pp) sits on the arm that would
\emph{inflate} $\Dstat$. \textbf{That paragraph is withdrawn, and the correct statement is
weaker and more useful: the value is not unexplained, it is not reproducible.} A box- and
class-matched re-run of the same seed (\arm{hz3q}, \S\ref{sec:inflight}) reads
$\Dstat(100) = \mathbf{+0.482}$, and its \arm{nodewise} arm --- identically flagged, identically
boxed, differing from its archived twin only in GPU class --- moves by $-0.204$ pp at that budget
on its own. The archived $+0.148$ was an extreme draw of same-configuration scatter, and an $n=6$
cell is not powered to tell that from a real seed effect. Because the box binds only after epoch
162, seed 5's archived contrast is \textbf{box-free at 100 epochs and box-bound at 300}
(floor occupancy $0.0086$, $0.0183$, $0.0089$ on \arm{chunk777}, \arm{nodewise1d},
\arm{chunk2325}), which is precisely the asymmetry a within-run pairing cannot cancel, and it is
why the repair moves the budget \emph{slope} much more than either \emph{level}
(\S\ref{sec:budget}). The direct cross-class control the repair makes available ---
\arm{hz3q-node-s5} $-$ \arm{hz3-node-s5} at \plateau{}(300) $= +0.134$ pp against a
pre-registered $1.00$ pp bar --- is reported in \S\ref{sec:budget}; it says GPU class is not
first-order on the \emph{level}, and it says nothing about $\Dstat$, in which the class cancels.
```

### TEX-19 — §8 Conclusion  (lines ~4330--4331)

**FIND (unique):**
```latex
($-0.090 \pm 0.178$, itself an upper bound in magnitude); it is present and resolved at
3$\times$ the budget;
```
**REPLACE:**
```latex
($-0.090 \pm 0.178$, itself an upper bound in magnitude); it is present and resolved at
3$\times$ the budget, at $+0.394 \pm 0.093$, $t\ 4.25$, \textbf{while declining with budget at a
rate that now resolves} ($-0.238 \pm 0.093$, $t\ -2.57$, paired within seed) --- two findings,
of which the second does not weaken the first;
```

### TEX-20 — §8, the experiments list  (lines ~4397--4398)

**FIND (unique):**
```latex
is in \S\ref{sec:alignment}. One remains: the box- and hardware-matched budget trio (R2, queued and
not yet started).
```
**REPLACE:**
```latex
is in \S\ref{sec:alignment}. The fourth, the box- and hardware-matched budget trio (R2), was
cancelled before it started and replaced by the four-arm quartet R2$'$ (\arm{hz3q}), which ran, was
scored against bands frozen before it existed, and withdrew one of our own claims
(\S\ref{sec:budget}). \textbf{All four registrations of \S\ref{sec:inflight} are now discharged.}
```
> **Shared with the `N3` package.**

### TEX-21 — Appendix A.2  (lines ~4457--4460)

**FIND (unique):**
```latex
the budget effect is $\mathbf{-0.149 \pm 0.105}$, $t\ -1.42$, i.e.\ a decline that does not resolve
--- $\mathbf{-0.207 \pm 0.107}$, $t\ -1.94$ once \arm{hz3}'s mismatched seed-5 pair is set aside
(\S\ref{sec:threats} T9, \S\ref{sec:budget}).
```
**REPLACE:**
```latex
the budget effect is $\mathbf{-0.149 \pm 0.105}$, $t\ -1.42$ on the archived seeds, i.e.\ a
decline that does not resolve --- $\mathbf{-0.207 \pm 0.107}$, $t\ -1.94$ once \arm{hz3}'s
mismatched seed-5 pair is set aside, and $\mathbf{-0.238 \pm 0.093}$, $\mathbf{t\ -2.57}$, a
decline that \textbf{does} resolve, once that seed is re-run box- and class-matched
(\S\ref{sec:threats} T9, \S\ref{sec:budget}). All three are reported wherever any of them is.
```

### TEX-22 — Appendix A.11 sensitivity line  (line ~2895)

**FIND (unique):**
```latex
$\Dstat - \Gstat +0.506 \pm 0.121$, $t\ 4.16$ --- same verdict.
```
**REPLACE:**
```latex
$\Dstat - \Gstat +0.506 \pm 0.121$, $t\ 4.16$ --- same verdict; and repaired at 6 v 6 with
\arm{hz3q}'s seed 5, $\Dstat +0.394 \pm 0.093$, $\Gstat -0.048 \pm 0.061$,
$\Dstat - \Gstat +0.442$ --- same verdict again.
```

### TEX-23 — End matter, the withdrawal roll-call  (lines ~4767--4769)

**FIND (unique):**
```latex
a budget flatness claim demoted to
an unresolved trend
```
**REPLACE:**
```latex
a budget flatness claim first demoted to
an unresolved trend and then \textbf{withdrawn outright} when a pre-registered re-run of its one
contaminated seed resolved the trend against us ($t\ -2.57$ against a bar of $2.0$ frozen before
the run existed)
```

---

## 3. REPLACEMENT TEXT — `paper/DRAFT-v4.md`

Same edits, same order, Markdown idiom. Anchors verified `count == 1`.

### MD-1 — §4.8 heading  (line 2057)

**FIND:** `### 4.8 Budget: the effect survives 3× the budget; whether it decays is not resolved`
**REPLACE:** `### 4.8 Budget: the effect survives 3× the budget, and it declines with it`

### MD-2 — §4.8 opening  (lines 2064--2065)

**FIND (unique):**
```
— ran at `−30:9.0` on an L4 or a 2080 Ti (§7 T9). We therefore report the budget contrast **twice**:
as submitted, and over the five clean seeds.
```
**REPLACE:**
```
— ran at `−30:9.0` on an L4 or a 2080 Ti (§7 T9). That seed has since been re-run: `hz3q` repeats
**all four** arms at seed 5 for 300 epochs in the batch's own box `−30:9.0`, in one submission on
one NVIDIA L4 (node883, jobs 4864632–35, all `COMPLETED`), so its box and its GPU class are matched
*by construction* rather than by declaration and the seed-5 pair is generated internally. `hz3q`
repairs one seed of `hz3`; it is not a replication, not a new design point and not a new cell, and
it is counted as none of those. We therefore report the budget contrast **three ways**: as
published, over the five clean seeds, and repaired — and, following the repair's own registered
scorer, we report all three together, always.
```

### MD-3 — §4.8 table  (lines 2067--2071)

**FIND (unique):**
```
| budget | D, 6 seeds as submitted | se | D, 5 clean seeds | se |
|---|---|---|---|---|
| 100 | +0.576 | 0.109 | **+0.662** | 0.083 |
| 200 | +0.514 | 0.115 | **+0.575** | 0.119 |
| 300 | +0.428 | 0.071 | **+0.455** | 0.081 |
```
**REPLACE:**
```
| budget | D, 6 seeds as published | se | D, 5 clean seeds | se | D, **repaired** | se |
|---|---|---|---|---|---|---|
| 100 | +0.576 | 0.109 | +0.662 | 0.083 | **+0.632** | 0.074 |
| 200 | +0.514 | 0.115 | +0.575 | 0.119 | **+0.512** | 0.116 |
| 300 | +0.428 | 0.071 | +0.455 | 0.081 | **+0.394** | 0.090 |
```

### MD-4 — §4.8 "The level is robust"  (lines 2073--2076)

**FIND (unique):**
```
**The level is robust, and it is the claim we make.** D(300) reads +0.428 ± 0.086 at 6 v 6
(t 4.94) and +0.455 ± 0.096 at 5 v 5 (t 4.75) on the Welch estimator used everywhere else in this
paper; all six seeds favour `chunk777` at 300 epochs (exact binomial p = 0.0156). **The partition
gap is not an artefact of a 100-epoch budget.**
```
**REPLACE:**
```
**The level is robust, and it is the claim we make.** D(300) reads +0.428 ± 0.086 at 6 v 6
(t 4.94) as published, +0.455 ± 0.096 at 5 v 5 (t 4.75), and **+0.394 ± 0.093 (t 4.25)** repaired,
on the Welch estimator used everywhere else in this paper; all six seeds favour `chunk777` at 300
epochs on every one of the three readings (exact binomial p = 0.0156). The repair moves the level
by 0.034 pp, four tenths of one se. **The partition gap is not an artefact of a 100-epoch budget,
and nothing below weakens that.**
```

### MD-5 — §4.8, THE WITHDRAWAL  (lines 2078--2090)

**FIND** the whole paragraph, from the anchor
```
**The trend is not robust, and we do not claim it.** Within-run, D(300) − D(100) = **−0.149 ±
```
through, and including,
```
box- and hardware-matched replacement trio (R2, §3.5) is registered and will settle it; until it
lands this cell carries its sensitivity in the text.
```
**REPLACE with:**
```
**The trend now resolves, and it resolves against a sentence we published.** The previous version
of this subsection said: *"D does not grow with budget from 100 to 300 epochs, and we cannot
resolve whether it decays."* **That sentence is withdrawn.** On the repaired data the decay
resolves. Within run, paired within seed at `plateau5`, D(300) − D(100) reads

| reading | seeds | n | δ | se | t (df) |
|---|---|---|---|---|---|
| as published | archived 0–5 | 6 | −0.149 | 0.105 | −1.42 (5) |
| seed 5 dropped | archived 0–4 | 5 | −0.207 | 0.107 | −1.94 (4) |
| **repaired** | archived 0–4 + `hz3q` seed 5 | 6 | **−0.238** | 0.093 | **−2.57** (5) |

against a bar of \|t\| ≥ 2 frozen in `c99_hz3q_score.py`'s `band_flat()` at the parent
registration's own `CONFIRM_T` **before `hz3q` was submitted**. The registered verdict on the
repaired reading is `NOT FLAT — D DECLINES WITH BUDGET` (p = 0.050 two-sided, 95% interval
[−0.477, −0.000]). **All three readings are reported together, always**: the repaired one does not
erase the published one from the record, it is the disclosed repair of the one seed whose contrast
was cross-box and cross-class.

**Read the withdrawal for exactly what it is.** D *shrinks* as the budget grows; it does not go
away. At 300 epochs it is +0.394 ± 0.093, t 4.25 — positive, resolved and within four tenths of an
se of the published value. The claim that dies is the narrower one about the *slope*. A reader who
takes this paragraph as "the effect disappears at longer budgets" has read it backwards, and §8
states the two findings separately for that reason.

**Why the published reading was wrong, and why it took a fifth run to see it.** Seed 5's
`chunk777`, `nodewise1d` and `chunk2325` runs sat in a narrower clip box *and* on different silicon
from their own `nodewise` partner, and the two defects bite at different budgets — the one shape of
contamination a within-run pairing cannot cancel. The −15 floor first becomes reachable at epoch
⌈8.092245 / 0.05⌉ = 162, and the probe records agree: floor occupancy for those three arms is
0.000000 at epoch 100 and rises to 0.0086, 0.0183 and 0.0089 by epoch 300, with the ceiling never
touched. So seed 5's archived D(100) is box-free and its archived D(300) is box-bound. The
hardware was worse than mislabelled: `hz3`'s registered scorer *declares* all four seed-5 runs
`gpu-2080ti-11g`, while their own headers report an RTX 2080 Ti, two A100 80 GB cards and an A100
MIG slice across three Slurm partitions. Both sides of that scorer's own check are declarations;
neither reads a run. `hz3q`'s provenance gate measures instead, and turned on the archive it is
built to refuse it refuses it on both counts.

**What the repair moved.** Seed 5's D(100) goes +0.148 → +0.482 and its D(300) goes +0.290 →
+0.086: the two ends move in *opposite* directions, which is why the repair changes the slope
(−0.149 → −0.238) far more than either level (+0.576 → +0.632 and +0.428 → +0.394). At B = 100 all
four archived seed-5 arms are box-free, so the per-arm archived-to-repaired differences there —
−0.204, +0.130, +0.376, +0.212 for `nodewise`, `chunk777`, `nodewise1d`, `chunk2325` — are
class-plus-nondeterminism alone. The archived seed-5 D(100) was not an unexplained extreme value;
it was a draw a matched re-run does not reproduce (§7 T9).

**A frozen bar reversed our own headline, and that is the point.** The threshold that withdrew this
claim was committed to version control before the data that triggered it existed, in a file whose
selftest asserts it (59/59 PASS) and which imports the parent reader unedited rather than
re-implementing it. We report the reversal here, in full, rather than in an appendix, because a
registration that can only confirm is not a registration.

**A control `hz3`'s own design could not run.** `hz3q-node-s5` and `hz3-node-s5` are the same
configuration, the same seed, the same box, the same flags and the same code; only the GPU class
differs. Their `plateau5`(300) values are 92.908 (L4) and 92.774 (RTX 2080 Ti), δ = **+0.134 pp**
against a bar of |δ| ≤ 1.00 pp registered before the run: **GPU class is not first-order on the
level**. In `hz3` the class is a function of the seed, so the class term and the seed term are
perfectly aliased and this quantity is not measurable there at all. It licenses one thing — that
`hz3`'s per-seed *levels* may be read across seeds despite the class assignment — and it touches
nothing about D, which is a within-seed, within-class contrast in both batches and in which the
class cancels identically. It also cross-checks §6.3, which measures 2080Ti − L4 = +0.035 pp over
n = 45 configurations: the direct same-seed control gives −0.134 pp for the same difference. The
signs disagree and both sit an order of magnitude inside the disclosure bar, which is the finding —
neither is large enough to carry a claim.
```

### MD-6 — §4.8, the 50-epoch paragraph's close  (lines 2098--2100)

**FIND (unique):**
```
primary-window reading is a non-significant decline, and a reader is entitled to both. See
Appendix A.2.
```
**REPLACE:**
```
primary-window reading is a resolved decline, and a reader is entitled to both. That verdict is
`hz3`'s and stands unchanged: `c87_hz3_score.py` was re-run unedited for this revision, admits
**no** `hz3q` file, and prints what it printed before. For completeness and marked **unregistered**
— `c87` is registered on `hz3` and `hz3q`'s own registered window is `plateau5` — recomputing
`c87`'s 50-epoch estimator on the repaired pool gives +0.161 ± 0.085, t 1.89, inside that scorer's
own ±0.20 `SATURATES` band. **The repair moves the two windows toward each other, not apart**: part
of the discrepancy was the contaminated seed. We do not restate a registered verdict on data it was
not registered for; we report that we looked. See Appendix A.2.
```

### MD-7 — Figure 3 caption  (lines 2120--2123)

**FIND (unique):**
```
(b) The budget slope both ways. D is present and resolved at every budget, and the slope does not
resolve either on all six seeds (−0.149 ± 0.105, t −1.42) or on the five box-matched seeds alone
(−0.207 ± 0.107, t −1.94). Neither interval excludes zero, so the verdict does not turn on the
contaminated seed — but its *t* does, and we print both rather than choosing.
```
**REPLACE:**
```
(b) The budget slope both ways. D is present and resolved at every budget. **The panel is drawn on
the archive**, in which the slope does not resolve either on all six seeds (−0.149 ± 0.105,
t −1.42) or on the five box-matched seeds alone (−0.207 ± 0.107, t −1.94). **Seed 5 has since been
re-run box- and class-matched, and on that repaired pool the slope does resolve: −0.238 ± 0.093,
t −2.57** (§4.8). The red trajectory is therefore the reading this figure supersedes, kept because
the published record is part of the evidence.
```

### MD-8 — Table 2 dagger note  (lines 1140--1141)

**FIND (unique):**
```
(0.027 from the rounded table entries) against a 0.086 pp se.
Run R2 (§3.5) restores a matched 6 v 6.
```
**REPLACE:**
```
(0.027 from the rounded table entries) against a 0.086 pp se.
The box- and class-matched re-run of that seed (`hz3q`, §3.5) has since landed and restores a
matched 6 v 6: **+0.394 ± 0.093, t 4.25**, a shift of 0.034 pp. **Row 9 is not changed to that
value.** The corpus is frozen at the runs the cells were built from, and every pooled quantity in
§4.3 and §4.4 — including the exact enumeration of all 45,045 partitions of the fourteen cells —
is computed on it; `hz3q` repairs one seed and is disclosed, not substituted.
```

### MD-9 — §3.4, discrepancy item 3  (line 791)

**FIND (unique):**
```
everywhere else, returns −0.149 ± 0.105 (t −1.42). We keep `plateau5` for consistency and print
```
**REPLACE:**
```
everywhere else, returns −0.149 ± 0.105 (t −1.42) on the same archived seeds, and **−0.238 ± 0.093
(t −2.57)** once seed 5 is repaired. We keep `plateau5` for consistency and print
```

### MD-10 — §3.5 heading  (line 845)

**FIND:** `### 3.5 Four pre-registered batches: three scored, one never started`
**REPLACE:** `### 3.5 Four pre-registered batches, all four now discharged — including one that reversed us`
> **Shared with the `N3` package.**

### MD-11 — §3.5 opening  (line 851)

**FIND (unique):**
```
`hz3` seed-5 trio — is not scored, and **no number from it enters any claim in this paper**. The
```
**REPLACE:**
```
`hz3` seed-5 trio — was **cancelled before it started**, and **no number from it enters any claim
in this paper**; it was superseded by a four-arm quartet, `hz3q`, whose own registered scorer
withdrew one of this paper's claims (§4.8). The
```
> **Shared with the `N3` package.**

### MD-12 — Table (in-flight) R2 row  (line 865)

**FIND (unique):**
```
| R2 | `hz3` seed-5 trio | 3 | the budget cell's clip-box and GPU-class mismatch (§4.8, §7 T9) | `analysis/c87_hz3_score.py`, reused unedited | **queued, not started** |
```
**REPLACE:**
```
| R2 | `hz3` seed-5 trio | 3 | the budget cell's clip-box and GPU-class mismatch (§4.8, §7 T9) | `analysis/c87_hz3_score.py`, reused unedited | **CANCELLED before start; superseded by R2′** |
| R2′ | `hz3q` seed-5 quartet | 4 | the same mismatch, repaired by re-running **all four** arms in one submission on one card | `analysis/c99_hz3q_score.py` | **SCORED — flatness WITHDRAWN; D DECLINES with budget (§4.8)** |
```
> **Shared with the `N3` package.**

### MD-13 — §3.5 R2 registration paragraph head  (line 889)

**FIND (unique):**
```
**R2 — the `hz3` seed-5 trio, re-run box- and hardware-matched.** `hz3-ch-s5`, `hz3-c23-s5` and
```
**REPLACE:**
```
**R2 — the `hz3` seed-5 trio, re-run box- and hardware-matched (CANCELLED).** `hz3-ch-s5`, `hz3-c23-s5` and
```
**and APPEND, after that paragraph's final sentence (`…because writing one would create two registrations for one question.`):**
```
**R2′ — `hz3q`, the box- and class-matched seed-5 *quartet*.** R2 was cancelled without ever
starting: its three jobs (4855960–62) were priority-starved on `gpu-2080ti-11g` with no assigned
start time and elapsed `00:00:00`, so STANDING RULE 20's post-launch `ARGS` check was never owed
and no number from them exists. It was replaced by a strictly stronger design. `hz3q` re-runs
**all four** arms — `nodewise`, `chunk777`, `nodewise1d`, `chunk2325` — at seed 5 for 300 epochs
at `−30:9.0` in **one submission on one card** (jobs 4864632–35, node883, `gpu-l4-24g`, NVIDIA L4,
all `COMPLETED`), so the box and the GPU class are shared *by construction* and **nothing depends
on an archived comparator**: R2 would have paired three fresh runs against an archived `nodewise`
partner, and R2′ generates the pair internally. Because the re-runs take **new names** (`hz3q-…`,
probing into `probe_<short>_hz3q_s5`), no file of `hz3`'s is renamed, moved, appended to or
deleted, and `c87_hz3_score.py` run unedited returns exactly what it returned before — asserted,
not assumed, by the new scorer's `assert_no_overwrite()` and confirmed by re-running `c87` for this
revision. A **second** scorer exists because the first *cannot ask the question*:
`c87_hz3_score.py:115` *declares* `SEED_CLASS`, and both sides of its own check on that map are
declarations. Editing it to agree with data collected after it was registered is the move RULE 16
forbids, so `analysis/c99_hz3q_score.py` was committed before any `hz3q` run existed (RULE 21;
selftest 59/59 PASS), **imports** `c87`'s reader unedited under a pinned sha256 rather than
re-implementing it, and **measures** provenance from each run's own header. Its bands were frozen
with the archived readings in hand: |t| < 2.0 → `FLAT`, |t| ≥ 2.0 → `NOT FLAT` with the sign naming
the direction; a cross-class disclosure switch at 1.00 pp; a box gate whose registered expectation
is *exactly* zero. It returned t −2.57 and took a claim of ours with it (§4.8).
```
> **Shared with the `N3` package.**

### MD-14 — "R2 is still queued"  (lines 977--983)

**FIND** the whole paragraph, from the anchor
```
**R2 is still queued and has never started.**
```
through, and including,
```
the box-matched 6 v 6 at 300 epochs does not exist and **§4.8's budget verdict is unchanged**.
```
**REPLACE with:**
```
**R2 was cancelled before it started, and R2′ ran in its place.** The three seed-5 jobs
(4855960–62, `hz3-ch-s5`, `hz3-c23-s5`, `hz3-n1d-s5`) sat `PENDING` with elapsed `0:00` and no
assigned start time on a congested partition, and were cancelled rather than left to age; `sacct`
records them `CANCELLED` at `00:00:00` elapsed. No `.out` file was ever written for any of the
three, so STANDING RULE 20's post-launch `ARGS` check was never owed and **no number from R2 exists
anywhere in this paper**. The replacement, R2′ (`hz3q`), ran to completion on one L4 and was scored
by `analysis/c99_hz3q_score.py`, registered before it. Its RULE 20 sweep returns 4 clean arms and 0
repeated flags. **§4.8's budget verdict is therefore changed, and the change is a withdrawal of
ours**: the box-matched 6 v 6 at 300 epochs now exists and reads +0.394 ± 0.093, t 4.25, while the
budget *slope*, which the previous version reported as unresolved, resolves at −0.238 ± 0.093,
t −2.57.
```
> **Shared with the `N3` package.**

### MD-15 — §7 T9 hardware close  (lines 3064--3065)

**FIND (unique):**
```
we do not edit a registered scorer after its data exist, so the correction is recorded here, and
R2 makes the label true again.
```
**REPLACE:**
```
we do not edit a registered scorer after its data exist, so the correction is recorded here. The
replacement runs (`hz3q`, §3.5) do not repair the label — under the file-freeze rule `c87`'s
constant stays as registered — they make it unnecessary: `hz3q`'s own scorer reads the GPU model
off each run's header instead of declaring it, and **that is the general lesson of this threat
item**. A registered constant that no run is ever compared against is a decoration; the repair is
to measure, not to re-declare.
```

### MD-16 — §7 T9 outlier paragraph  (lines 3073--3079)

**FIND** the whole paragraph, from the anchor
```
Seed 5 is also the batch's per-seed outlier at 100 epochs — D(100) = **+0.148** against **+0.548,
```
through, and including,
```
on matched hardware is R2 (§3.5).
```
**REPLACE with:**
```
Seed 5 is also the batch's per-seed outlier at 100 epochs — D(100) = **+0.148** against **+0.548,
+0.564, +0.586, +0.622, +0.990** — and unremarkable at 300 (+0.290, against a seed-2 low of
+0.168). The previous version of this paragraph called that value *unexplained*, having established
that neither defect could produce it: the box is inert at 100 epochs (floor occupancy measured at
0.000000 for all three arms there, the floor first reachable at epoch 162), and the hardware term
(§6.3: A100 − 2080 Ti = +0.112 pp) sits on the arm that would *inflate* D. **That paragraph is
withdrawn, and the correct statement is weaker and more useful: the value is not unexplained, it is
not reproducible.** A box- and class-matched re-run of the same seed (`hz3q`, §3.5) reads
D(100) = **+0.482**, and its `nodewise` arm — identically flagged, identically boxed, differing
from its archived twin only in GPU class — moves by −0.204 pp at that budget on its own. The
archived +0.148 was an extreme draw of same-configuration scatter, and an n = 6 cell is not powered
to tell that from a real seed effect. Because the box binds only after epoch 162, seed 5's archived
contrast is **box-free at 100 epochs and box-bound at 300** (floor occupancy 0.0086, 0.0183, 0.0089
on `chunk777`, `nodewise1d`, `chunk2325`), which is precisely the asymmetry a within-run pairing
cannot cancel, and it is why the repair moves the budget *slope* much more than either *level*
(§4.8). The direct cross-class control the repair makes available — `hz3q-node-s5` −
`hz3-node-s5` at `plateau5`(300) = +0.134 pp against a pre-registered 1.00 pp bar — is reported in
§4.8; it says GPU class is not first-order on the *level*, and it says nothing about D, in which
the class cancels.
```

### MD-17 — §8 Conclusion  (lines 3454--3455)

**FIND (unique):**
```
to its own optimum (−0.090 ± 0.178, itself an upper bound in magnitude); it is present and
resolved at 3× the budget;
```
**REPLACE:**
```
to its own optimum (−0.090 ± 0.178, itself an upper bound in magnitude); it is present and
resolved at 3× the budget, at +0.394 ± 0.093, t 4.25, **while declining with budget at a rate that
now resolves** (−0.238 ± 0.093, t −2.57, paired within seed) — two findings, of which the second
does not weaken the first;
```

### MD-18 — §8 experiments list  (lines 3516--3517)

**FIND (unique):**
```
budget trio (R2, queued). To those we add two experiments the last cycle created rather than
closed.
```
**REPLACE:**
```
budget trio (R2), which was cancelled before it started and replaced by the four-arm quartet R2′
(`hz3q`) — that quartet ran, was scored against bands frozen before it existed, and withdrew one of
our own claims (§4.8). **All four registrations of §3.5 are now discharged.** To those we add two
experiments the last cycle created rather than closed.
```
> **Shared with the `N3` package.** Note this md sentence also mis-states R1 as unscored while
> md line 865 records it SCORED; that md/tex divergence is pre-existing and is **not** repaired
> here — see §7 "left open".

### MD-19 — Appendix A.2  (lines 3569--3571)

**FIND (unique):**
```
G(AdamW) = **+0.232 ± 0.089, t 2.62**; and the budget effect is **−0.149 ± 0.105, t −1.42**, i.e. a
decline that does not resolve — **−0.207 ± 0.107, t −1.94** once `hz3`'s mismatched seed-5 pair is
set aside (§7 T9, §4.8).
```
**REPLACE:**
```
G(AdamW) = **+0.232 ± 0.089, t 2.62**; and the budget effect is **−0.149 ± 0.105, t −1.42** on the
archived seeds, i.e. a decline that does not resolve — **−0.207 ± 0.107, t −1.94** once `hz3`'s
mismatched seed-5 pair is set aside, and **−0.238 ± 0.093, t −2.57**, a decline that **does**
resolve, once that seed is re-run box- and class-matched (§7 T9, §4.8). All three are reported
wherever any of them is.
```

### MD-20 — Appendix sensitivity line  (lines 2260--2261)

**FIND (unique):**
```
seed-5 mismatch of §7 T9 reads D +0.455 ± 0.096, G −0.050 ± 0.075, D − G +0.506 ± 0.121, t 4.16 —
same verdict.
```
**REPLACE:**
```
seed-5 mismatch of §7 T9 reads D +0.455 ± 0.096, G −0.050 ± 0.075, D − G +0.506 ± 0.121, t 4.16 —
same verdict; and repaired at 6 v 6 with `hz3q`'s seed 5, D +0.394 ± 0.093, G −0.048 ± 0.061,
D − G +0.442 — same verdict again.
```

### MD-21 — End matter roll-call  (line 3840)

**FIND (unique):**
```
rested on, a budget flatness claim demoted to an unresolved trend, and a variance claim that
```
**REPLACE:**
```
rested on, a budget flatness claim first demoted to an unresolved trend and then **withdrawn
outright** when a pre-registered re-run of its one contaminated seed resolved the trend against us
(t −2.57 against a bar of 2.0 frozen before the run existed), and a variance claim that
```

---

## 4. `analysis/c98_reproduce.py` — NEW ASSERTION SITES

Append to `def budget(rows, adm, args)` (currently ends at the `chk("   t", …)` inside the
two-pool loop, ~line 405). The block below was **executed against the live tree before being
written here**: all 20 assertions PASS. It uses only `series` / `pl5` / `welch` / `chk`, all
already imported at `c98_reproduce.py:50`, and `series("hz3q-…")` cannot collide with
`series("hz3-…")` — the existing globs are `hz3-ch-s*.out` / `hz3-node-s*.out`, which do not match
`hz3q-*`.

```python
    # ---- the hz3q repair: seed 5 re-run box- and class-matched (§4.8, §7 T9) ----
    qch, qnd = series("hz3q-ch-s*.out"),  series("hz3q-node-s*.out")
    qn1, qc2 = series("hz3q-n1d-s*.out"), series("hz3q-c23-s*.out")
    if not (set(qch) == set(qnd) == {5}):
        print("        (hz3q .out series not found -- repaired readings skipped)")
        return
    n1d, c23 = series("hz3-n1d-s*.out"), series("hz3-c23-s*.out")
    CH, ND = dict(ch), dict(nd)
    N1, C2 = dict(n1d), dict(c23)
    CH[5], ND[5], N1[5], C2[5] = qch[5], qnd[5], qn1[5], qc2[5]
    for B, exp, ese in ((100, 0.632, 0.074), (200, 0.512, 0.116), (300, 0.394, 0.090)):
        d = [pl5(CH[s], B) - pl5(ND[s], B) for s in seeds]
        chk("D(%d), REPAIRED 6 seeds" % B, st.mean(d), exp, "§4.8 table col 3")
        chk("   se", st.stdev(d) / math.sqrt(len(d)), ese, "§4.8 table col 3", "%.3f")
    dd = [(pl5(CH[s], 300) - pl5(ND[s], 300)) - (pl5(CH[s], 100) - pl5(ND[s], 100))
          for s in seeds]
    m_, se_ = st.mean(dd), st.stdev(dd) / math.sqrt(len(dd))
    chk("D(300)-D(100), REPAIRED 6 seeds", m_, -0.238, "§4.8 -- c99 H2 REGISTERED VERDICT")
    chk("   se", se_, 0.093, "§4.8 -- c99 H2", "%.3f")
    chk("   t  (bar |t| >= 2.0 frozen pre-run -> NOT FLAT, D DECLINES)",
        m_ / se_, -2.57, "§4.8, §8, A.2, end matter", "%.2f")
    d, se, t = welch([pl5(CH[s], 300) for s in seeds], [pl5(ND[s], 300) for s in seeds])
    chk("D(300) REPAIRED 6 v 6 (Welch)", d, 0.394, "§4.8, Table 2 dagger, §8")
    chk("   se", se, 0.093, "§4.8, Table 2 dagger", "%.3f")
    chk("   t  (Contribution 1 UNTOUCHED)", t, 4.25, "§4.8, Table 2 dagger, §8", "%.2f")
    g = welch([pl5(C2[s], 300) for s in seeds], [pl5(N1[s], 300) for s in seeds])[0]
    chk("G(300) REPAIRED 6 v 6", g, -0.048, "§4.8, A.11")
    chk("(D-G)(300) REPAIRED", d - g, 0.442, "§4.8, A.11")
    chk("HC cross-class hz3q-node-s5 - hz3-node-s5 @300", pl5(qnd[5], 300) - pl5(nd[5], 300),
        0.134, "§4.8 HC, §7 T9 -- bar |delta| <= 1.00 pp")
    chk("   hz3q-node-s5 plateau5(300)", pl5(qnd[5], 300), 92.908, "§4.8 HC", "%.3f")
    chk("   hz3-node-s5  plateau5(300)", pl5(nd[5], 300), 92.774, "§4.8 HC", "%.3f")
    chk("archived seed-5 D(100)", pl5(ch[5], 100) - pl5(nd[5], 100), 0.148, "§7 T9")
    chk("repaired seed-5 D(100)", pl5(qch[5], 100) - pl5(qnd[5], 100), 0.482, "§7 T9")
    chk("archived seed-5 D(300)", pl5(ch[5], 300) - pl5(nd[5], 300), 0.290, "§7 T9")
    chk("repaired seed-5 D(300)", pl5(qch[5], 300) - pl5(qnd[5], 300), 0.086, "§7 T9")
    chk("seed-5 nodewise class-only shift @100", pl5(qnd[5], 100) - pl5(nd[5], 100), -0.204,
        "§7 T9 -- same box, same flags, class only")
    chk("epoch the -15 floor first becomes reachable",
        math.ceil((math.log(1e-3) - (-15.0)) / (1e-4 * 500)), 162, "§3.5 R2, §7 T9", "%.0f")
```

Verified output (run standalone against the live tree, 2026-09-03):

```
  D(100), REPAIRED 6 seeds                       +0.632 | paper +0.632 | PASS
     se                                          0.074 | paper 0.074 | PASS
  D(200), REPAIRED 6 seeds                       +0.512 | paper +0.512 | PASS
     se                                          0.116 | paper 0.116 | PASS
  D(300), REPAIRED 6 seeds                       +0.394 | paper +0.394 | PASS
     se                                          0.090 | paper 0.090 | PASS
  D(300)-D(100), REPAIRED 6 seeds                -0.238 | paper -0.238 | PASS
     se                                          0.093 | paper 0.093 | PASS
     t                                           -2.57 | paper -2.57 | PASS
  D(300) REPAIRED 6 v 6 (Welch)                  +0.394 | paper +0.394 | PASS
     se                                          0.093 | paper 0.093 | PASS
     t                                           4.25 | paper 4.25 | PASS
  G(300) REPAIRED 6 v 6                          -0.048 | paper -0.048 | PASS
  (D-G)(300) REPAIRED                            +0.442 | paper +0.442 | PASS
  HC cross-class ... @300                        +0.134 | paper +0.134 | PASS
     hz3q-node-s5 plateau5(300)                  92.908 | paper 92.908 | PASS
     hz3-node-s5  plateau5(300)                  92.774 | paper 92.774 | PASS
  archived seed-5 D(100)                         +0.148 | paper +0.148 | PASS
  repaired seed-5 D(100)                         +0.482 | paper +0.482 | PASS
  archived seed-5 D(300)                         +0.290 | paper +0.290 | PASS
  repaired seed-5 D(300)                         +0.086 | paper +0.086 | PASS
  epoch the -15 floor first becomes reachable    162 | paper 162 | PASS
```

Also update the registered-scorer roster near `c98_reproduce.py:687`, which currently lists
`("c87_hz3_score", "§4.8 the budget window", "REACHED", …)`, by adding:

```python
 ("c99_hz3q_score", "§4.8 the repaired budget slope", "REACHED",
  "run unedited; selftest 59/59; verdict NOT FLAT -- D DECLINES WITH BUDGET"),
```

**Do NOT touch `[7] BUDGET`'s existing published assertions.** They passed on this tree before and
after the `hz3q` ingest (verified) and they are the record the withdrawal is stated against.

---

## 5. WHAT IS **NOT** CHANGED, AND WHY

1. **Table 2 row 9 keeps `+0.428 ± 0.086, t 4.94`.** The corpus is frozen at the runs the 20 cells
   were built from. Every pooled quantity — the eight-cell SGDm pool, Cochran `Q`, `η²`, and the
   exact enumeration of all 45,045 partitions — is computed on it. `hz3q` repairs one seed and, by
   its own scorer's rule, "must NOT be counted as an 11th design point, an additional independent
   replication, or a new cell in the 20-cell table." The repaired value is **disclosed** in the
   dagger note (TEX-10 / MD-8), never substituted.
2. **"D positive in 20 of 20 count-matched cells" is unchanged**, and would be unchanged even if
   row 9 were repaired: +0.394 is positive.
3. **`c87_hz3_score.py`'s `GROWS` verdict is unchanged**, and `c87` is not edited. Its
   `SEED_CLASS` constant stays wrong-and-registered; T9 now says why that is the right outcome.
4. **`figures/f3_budget.pdf` is unchanged** and the new caption is true of it.
5. **The abstract carries no flatness claim** — no site there. (It does carry a stale `2,173-run`
   corpus size; that belongs to the corpus-count package, not this one.)

---

## 6. ANCHOR VERIFICATION

Every FIND string above was checked with:

```python
tex = open("paper/paper.tex").read();  md = open("paper/DRAFT-v4.md").read()
assert tex.count(anchor) == 1     # for every TEX-n
assert md.count(anchor)  == 1     # for every MD-n
```

All returned `1` at HEAD `17b9af7`. Re-run the check before applying: if the integrator applies
another package first, `TEX-12/13/14/15/16/20` and `MD-10/11/12/13/14/18` (the R2-status sites)
may already have moved — they are **shared with the `N3` package** and are flagged inline.

---

## 7. FINDINGS, CORRECTIONS AND OPEN ITEMS

**The briefing's numbers are all correct.** Three refinements:

1. **The paper does not currently claim flatness.** §4.8 already says *"We do not report flatness
   as a result."* The live claim to withdraw is the sentence before it — *"D does not grow with
   budget from 100 to 300 epochs, and we cannot resolve whether it decays"* — plus the subsection
   title and three downstream restatements. The withdrawal is of the **unresolved-decay** half,
   which is now resolved. Written that way above; a package that hunted only for the word
   "flatness" would have found the end-matter roll-call and missed the actual claim.
2. **H1 is not reproducible from the local backup.** `runs/hz3/probe_*_hz3q_s5/` are empty locally;
   the scorer correctly refuses and prints `NO OCCUPANCY IS MEASURABLE`. It passes with
   `0.000000` at every window on ALICE, where the probe records live. **Sync them before the
   deposit is cut.**
3. **A stronger mechanism than "the box moved" is available and is written in.** The archived
   seed-5 contrast is **box-free at 100 epochs and box-bound at 300** (measured floor occupancy
   0.000000 / 0.000485–0.001621 / 0.008598–0.018323 at 100 / 200 / 300; ceiling never touched;
   floor first reachable at epoch 162). A defect present at one end of a within-run pairing and
   absent at the other is exactly what pairing cannot cancel — that is *why* the slope was the
   quantity that broke while the level barely moved.

**New, not in the briefing:**

4. **On the repaired pool the two windows stop contradicting each other.** `c87`'s own 50-epoch
   estimator, recomputed (unregistered) on the repaired pool, gives **+0.161 ± 0.085, t 1.89** —
   inside `c87`'s own `SAT_HALF` = 0.20 band, i.e. `SATURATES` rather than `GROWS`. Part of the
   window discrepancy the paper discloses in §3.4 item 3 was the contaminated seed. Written in as
   an explicitly unregistered disclosure at TEX-8 / MD-6.
5. **The HC control disagrees in sign with §6.3's corpus hardware term.** §6.3: 2080Ti − L4 =
   **+0.035** pp (n = 45). The direct same-seed control: **−0.134** pp. Both an order of magnitude
   inside the 1.00 pp bar; written in as a cross-check, not hidden.
6. **`c98_reproduce.py` exits 1 with 8 failures, all corpus counts, none of them hz3-related.**
   The `[7] BUDGET` block passes every published assertion unchanged after the `hz3q` ingest —
   a second, independent confirmation of non-overwrite at the CSV level.

**Left open (not mine to close):**

- The 8 corpus-count failures (`2177/2173`, `1735/1731`, `2162/2158`, `1642/1632`, `431/427`,
  `419/415`, `241/238` twice) and the abstract's `2{,}173-run` / A.8's counts — corpus-count
  package.
- Redrawing `f3_budget` panel (b) with the repaired seed (`analysis/c98_figures.py:469` selects
  `hz3-(ch|node)-s(\d+)$`, so `hz3q` is invisible to it). Caption is honest about this meanwhile.
- Syncing `runs/hz3/probe_*_hz3q_s5/probe.jsonl` from ALICE into the backup, so H1 is reproducible
  from the deposit.
- **A pre-existing md/tex divergence:** `DRAFT-v4.md:3514` says R1 is "complete on disk and
  deliberately unscored" while `DRAFT-v4.md:865` and `paper.tex:4394` record it SCORED. Flagged,
  not repaired here.
- A CORRECTIONS entry for this reversal (the register stands at 132; A.8's text says 131).
