# REWRITE PACKAGE — `production`

Gate **S1** (figures) · **S2** (numbered equations) · **S6** (end matter) · **S11**
(artefact / reproducibility) · Q17–Q22.

**Scope.** This package delivers the four things the desk-reject fired on that are not
science: real figures on one palette, numbered equations, a complete end matter, and a
deposit-ready artefact. It does **not** touch the claims. Where a number moves, the
re-derivation is shown in §7 below.

**Concurrency.** `paper/DRAFT-v2.md` is **not edited by this package.** Every change below
is given as *exact replacement text keyed to an anchor line that already exists in the
draft*. Anchors are quoted verbatim, line-break-exact, so an integrator can `grep` them.
Two of the four figure insertions land in sections other packages are rewriting (§4.4 and
§5.4); those are flagged **[SHARED SECTION]** with a collision note, a fallback anchor, and
a list of which numbers must move together.

**Nothing in this package was typed from prose.** Every figure and every number below is
produced by code that reads `results/all_runs.csv` and the raw `.out` series at build
time. `python3 analysis/c98_reproduce.py` re-derives all of them and checks each against
what the paper prints; it currently exits **0 — ALL CHECKS PASS** on all 99 checks.

---

## 0. New files created by this package

| path | md5 | what |
|---|---|---|
| `analysis/c98_figures.py` | `feb568bfbdcc4f62b03b4e3e2f7ad0be` | the four figures, from the CSV, one palette. `--numbers` prints every plotted value |
| `analysis/c98_reproduce.py` | `41cff1656c6365371c36ecc08ba776a0` | the reproduction audit: re-derives every headline and checks it against the paper. Exit 0 iff all pass |
| `analysis/c98_release.py` | `027746b9f4e02bcd72214ecf13c22c2a` | builds `release/`; **refuses to build if the audit fails** |
| `paper/figures/f1_forest_D.pdf` / `.png` | `52153b4a144243742ef1c00a1e2c435f` | Figure 1 |
| `paper/figures/f2_base_moderator.pdf` / `.png` | `2f752c811d55a120232296efad8000ed` | Figure 2 |
| `paper/figures/f3_budget.pdf` / `.png` | `61fc17e5f51628e882dd9dcb38d3359e` | Figure 3 |
| `paper/figures/f4_decomposition.pdf` / `.png` | `e1d69a96a0da68499207ada2ad0e7a76` | Figure 4 |
| `release/` | see `release/MANIFEST.md5` | 137 files, 6.1 MB, self-verifying deposit |

Rebuild everything with three commands, each of which is idempotent:

```
python3 analysis/c98_figures.py --all --numbers     # the four figures + every plotted value
python3 analysis/c98_reproduce.py                   # the audit; exit 0 iff every headline reproduces
python3 analysis/c98_release.py                     # the deposit; refuses to build on a failed audit
```

The figures are **byte-reproducible**: no build timestamp is embedded, so
`release/MANIFEST.md5` still verifies after `make figures` regenerates them.

---

## 1. Gate S1 — the four figures

All four share one palette. **Colour encodes the base optimiser** (Okabe–Ito,
colour-blind safe: SGDm `#0072B2`, SGD `#E69F00`, RMSProp `#009E73`, AdamW `#D55E00`,
SGDm-GroupNorm `#CC79A7`); **marker shape encodes the dataset** (circle CIFAR-10,
diamond CIFAR-100); **marker size encodes network depth** (R18 / R34 / R50). Ink
`#1B1B1B`, grid `#D9D6D0`, annotation grey `#7A7A7A`. Fonts embedded (Type 42), 300 dpi
PNG plus vector PDF.

The figure code enforces the paper's own house rules, so a figure cannot silently break
one. In particular **R-D: CIFAR-10 and CIFAR-100 effects are never placed on one
percentage-point axis** — §4.3 states that rule and Figures 1 and 4 both carry it as a
hard horizontal rule with the commensurable quantity supplied alongside. That rule is not
decoration; see §7.4 for what it is worth numerically.

**The GroupNorm cell is excluded, by default, in code.** R0 checklist item 1 removes
`gn1`-GroupNorm from Table 2, from the pool and from the counts, because its own
registered scorer halts at its commensurability gate and prints *"THIS IS NOT A NULL"*;
the `scorer-violation` package implements that removal in the prose. The figures follow it
**automatically**: `GN_CELL` is excluded unless `--with-gn` is passed, and every count,
pool, Q, τ, legend entry and axis label in all four figures is derived from the cell list
rather than typed, so both worlds render correctly from one code path. As shipped the
figures therefore show **sixteen** Table 2 cells and an **eleven**-cell byte-identical
pool (+0.571 ± 0.037, Q 36.40 on 10 df, τ 0.203, rms se 0.152). If the integrator decides
to keep the cell, `python3 analysis/c98_figures.py --all --with-gn` regenerates seventeen
cells and the twelve-cell pool (+0.546 ± 0.036, Q 43.19 on 11 df, τ 0.215) with no edit,
and `analysis/c98_reproduce.py` checks **both** sets of values in either mode.

### 1.1 Figure 1 — the forest

**INSERT** at the end of §4.3, i.e. immediately **after** the anchor line

> `on one axis.`

and immediately **before** the line `### 4.4 D is genuinely heterogeneous`.

```markdown
![Figure 1](figures/f1_forest_D.png)

**Figure 1 — D in every count-matched cell, and the same effect made commensurable.**
(a) D = uniform chunk − architecture-aligned nodewise, `plateau5`, taken within batch,
with 95% intervals from the Welch standard error of Table 2. Colour is the base
optimiser, marker shape the dataset, marker size the network depth. **D is positive in
every one of the sixteen cells.** The horizontal rule separates CIFAR-10 from
CIFAR-100: the two sit on ≈7–8 pp and ≈29–30 pp error budgets and a percentage point does
not mean the same thing across it, so panel (a) must not be read across the rule.
(b) The same sixteen contrasts as a share of the aligned arm's remaining error,
D / (100 − aligned), which *is* commensurable. On that scale CIFAR-100's +1.640 pp is
0.055 — the **smallest** value among the CIFAR-10 cells, not the largest. The inset
gives the fixed-effect pool over the eleven cells that share a byte-identical contrast.
```

LaTeX form for the eventual build:

```latex
\begin{figure}[t]\centering
  \includegraphics[width=\linewidth]{figures/f1_forest_D.pdf}
  \caption{...as above...}\label{fig:forest}
\end{figure}
```

### 1.2 Figure 2 — the base-optimiser moderator **[SHARED SECTION: §4.4]**

**INSERT** at the end of §4.4, immediately **before** the line
`### 4.5 Tuning each arm to its own optimum does not remove D`.

> **Collision note.** R0 item 2 rewrites §4.4 into a decomposition. This figure *is* that
> decomposition and its numbers are re-derived from the same code, so the two agree by
> construction: within-SGDm **Q 4.21 on 7 df, p 0.76, τ 0.000, pool +0.556 ± 0.045**;
> between-base **Q 32.20 on 3 df**. If the §4.4 package has already inserted its own
> closing paragraph, put the figure after it. If §4.4 has been renumbered, the fallback
> anchor is the string `Dropping the GroupNorm cell: Q = 36.4 on 10 df`.

```markdown
![Figure 2](figures/f2_base_moderator.png)

**Figure 2 — the heterogeneity in D is a base-optimiser effect, not an unattributable
one.** (a) The eleven byte-identical ResNet-18 cells, grouped by base optimiser; each
group's band is its own inverse-variance pool ± 1.96 se. The eight SGDm cells — six
separate submissions, two meta-stepsizes, two budgets, two normalisation schemes — are
**homogeneous**: Q 4.21 on 7 df, p 0.76, DerSimonian–Laird τ = 0.000, pooling to
+0.556 ± 0.045. (b) Partitioning the eleven-cell Cochran Q: **32.20 of 36.40 (88%) is
between base optimisers**, on 3 df, p 4.8e-7. (Against the twelve-cell Q of 43.2 that the
withdrawn GroupNorm cell used to enter, the same 32.20 is 74.6% — the "~75%" figure, whose
denominator must always be named.) This is the figure that replaces "for reasons we cannot
attribute".
```

### 1.3 Figure 3 — budget, with the seed-5 sensitivity shown

**INSERT** at the end of §4.8, immediately **before** the `---` that precedes
`## 5. Eight dead mechanisms and two nulls`.

```markdown
![Figure 3](figures/f3_budget.png)

**Figure 3 — D at 1×, 2× and 3× the budget, paired WITHIN run, and what one
box-mismatched seed does to it.** `hz3` ran the four arms for 300 epochs at six seeds in
one batch, so D can be read off the same run at three budgets, cancelling seed, run,
batch, β-box and GPU class identically. (a) Faint lines are the six per-seed
trajectories; the two heavy lines are the arm-set means with 95% intervals. **Seed 5 is
drawn in red because it is not box-matched**: its chunk arm ran in β-box −15:−2.3026 and
its nodewise arm in −30:9.0, so that seed's D is a cross-box difference and the other
five are not. (b) The budget slope both ways. D is present and resolved at every budget,
and the slope is **flat** on all six seeds (−0.149 ± 0.105, t −1.42) and on the five
box-matched seeds alone (−0.207 ± 0.107, t −1.94). Neither interval excludes zero, so the
verdict does not turn on the contaminated seed — but its *t* does, and we print both
rather than choosing.
```

### 1.4 Figure 4 — the D / G / D−G decomposition **[SHARED SECTION: §5.4]**

**INSERT** at the end of §5.4, immediately **before** the line
`### 5.5 Dead: base-optimiser normalisation`.

> **Collision note.** The G-decision-rule package (R0 item 8) rewrites §5.4's verdict
> language and applies Holm over the twelve G tests. This figure plots the *estimates and
> intervals*, not the verdicts, so the two are compatible; but the figure's `ml2` row now
> reads **G +0.173 ± 0.073, t 2.38** (not t 2.44) after the `dup_group` collapse — the
> §5.4 table must move with it. Fallback anchor:
> `> **"The gap lives in the degenerate size-1 tail" may not be written as a general claim.**`

```markdown
![Figure 4](figures/f4_decomposition.png)

**Figure 4 — D splits into a tail-free part G and a size-1-tail part D − G, and the split
is base-dependent.** (a) For every batch that ran all four arms, D is drawn as the sum of
G (hatched: the same uniform-vs-aligned contrast with the size-1 tail *already removed
from both arms*, count-matched exactly at m = 4,851) and D − G (solid: what the tail
contributes). The black tick and whisker are D itself with its 95% interval. Under an
SGDm base the hatched part is ≈0 and the tail carries essentially all of D. Under
**AdamW** it does not: G is +0.232 ± 0.089 and D − G collapses to +0.047 ± 0.124.
(b) D − G alone, with 95% intervals and each cell's *t*. CIFAR-100 is placed below the
rule for the reason given in Figure 1. The pooled SGDm/CIFAR-10 value is
**+0.514 ± 0.056** over eight cells (Q 4.52 on 7 df); we quote that pool rather than
`cc1`'s +0.715, which is the maximum.
```

### 1.5 One line to add to §3.4 so the figures are inside the registration discipline

**REPLACE** the last sentence of §3.4 — anchor
`md5 \`0363bcccb4d3bbad50beb19c9281b9be\`).` — appending:

```markdown
Every figure in this paper is generated by `analysis/c98_figures.py` directly from
`results/all_runs.csv` and the raw `.out` series; `--numbers` prints each plotted value,
and `analysis/c98_reproduce.py` re-derives every number in the text and asserts it
against what is printed here. No figure contains a value that was typed.
```

---

## 2. Gate S2 / Q17 — numbered equations

The draft currently contains **no display mathematics at all**: D, G, A, U, T,
`plateau5` and the admissibility predicate are defined in prose bullets and are then
referred to by name for forty pages. Twelve numbered equations below replace §3.2 and the
first two paragraphs of §3.3.

### 2.1 REPLACE §3.2 in full

**Anchor start:** `### 3.2 The contrasts`
**Anchor end (exclusive):** `### 3.3 Metric, admissibility, and units of replication`

```markdown
### 3.2 The contrasts

Write $\mathcal{P}$ for a partition of the network's weights into $m$ step-size groups
and $\mu(\mathcal{P})$ for the mean `plateau5` of the arm that trains under it, taken over
the seeds of one batch. All four differences below are **within batch** and
**count-matched by construction**.

The primary contrast replaces an architecture-aligned partition by a uniform one at the
same group count:

$$
D \;=\; \mu(\texttt{chunk777}) \;-\; \mu(\texttt{nodewise}),
\qquad m = 14{,}421 \ \text{vs}\ 14{,}420
\tag{1}
$$

— one group apart, $3\times10^{-5}$ decades of count. The same contrast with the
degenerate size-1 tail **already removed from both arms**, count-matched exactly, is

$$
G \;=\; \mu(\texttt{chunk2325}) \;-\; \mu(\texttt{nodewise1d}),
\qquad m = 4{,}851 \ \text{exactly}
\tag{2}
$$

so that $D - G$ is the tail's contribution and, being a difference of two within-batch
differences taken in the same batch, carries no cross-batch floor. The alignment leg holds
the count *and* the exact per-tensor group-size multiset and randomises only which weights
share a group, within each tensor:

$$
A \;=\; \mu(\texttt{permnode}) \;-\; \mu(\texttt{nodewise}),
\qquad m = 14{,}420,\ \ \text{size multiset identical}
\tag{3}
$$

The pure count axis holds the partition *family* fixed and moves only $m$:

$$
U \;=\; \mu(\texttt{chunk2325}) \;-\; \mu(\texttt{chunk777}),
\qquad \log_{10}\!\big(14{,}421/4{,}851\big) = 0.4732\ \text{decades}
\tag{4}
$$

and the practitioner's move — merge each one-dimensional tensor into a single group — is

$$
T \;=\; \mu(\texttt{nodewise1d}) \;-\; \mu(\texttt{nodewise}).
\tag{5}
$$

$T$ is count-confounded by construction, and the confound is exact rather than
approximate:

$$
T \;=\; (D - G) \;+\; U .
\tag{6}
$$

Two further identities are used and are exact by construction, not by fitting. With
$B = \mu(\texttt{chunk777}) - \mu(\texttt{permnode})$,

$$
A + B \;=\; D ,
\tag{7}
$$

which is what licenses reporting alignment and size-distribution as *shares* of one
effect in §4.6.

Every difference in (1)–(5) is reported with a Welch standard error formed from the two
arms' own variances, never from a pooled or an assumed one:

$$
\widehat{\mathrm{se}}(\mu_1-\mu_2)\;=\;\sqrt{\frac{s_1^{2}}{n_1}+\frac{s_2^{2}}{n_2}}\,,
\qquad t=\frac{\mu_1-\mu_2}{\widehat{\mathrm{se}}} .
\tag{8}
$$

Because a percentage point is not comparable across error budgets, the commensurable
companion to $D$ is the share of the aligned arm's remaining error that it removes:

$$
\rho \;=\; \frac{D}{100 - \mu(\texttt{nodewise})} .
\tag{9}
$$

Figure 1(b) plots $\rho$; §4.3 states, and this paper obeys, the rule that CIFAR-10 and
CIFAR-100 values of $D$ are never averaged and never placed on one percentage-point axis.

On ResNet-34, ResNet-50 and ResNet-18/CIFAR-100 the count matching in (1) is close but not
exact: chunk835 25,562 vs nodewise 25,556 (R34); chunk295 79,796 vs 79,700 and chunk884
26,715 vs 26,677 (R50); chunk771 14,595 vs 14,600 and chunk2293 4,943 vs 4,941 (C100). The
largest mismatch, 0.14% of the count, is 685× below the resolution floor at the measured
count slope.

**A structural caveat specific to ResNet-50.** Its largest 1-D tensor has 2,048 elements,
which exceeds K = 295, so `chunk295` **splits** some 1-D tensors across groups instead of
giving each one a single group. It still contains no size-1 group (min group size 10).
ResNet-18, ResNet-34 and ResNet-18/CIFAR-100 all have largest 1-D tensor 512 < K, so their
chunk arms give each 1-D tensor exactly one group. The ResNet-50 $D$ is therefore a
slightly different object and is reported as such.
```

### 2.2 REPLACE the first two paragraphs of §3.3

**Anchor start:** `**Metric.** \`plateau5\`, the mean test accuracy over the last 5 epochs`
**Anchor end (exclusive):** `**Box occupancy.** β is clipped to a box`

```markdown
**Metric.** For a run $r$ that completed $E_r$ test epochs with accuracies
$a_r(1),\dots,a_r(E_r)$, the primary metric throughout is

$$
\texttt{plateau5}(r)\;=\;\frac{1}{5}\sum_{e=E_r-4}^{E_r} a_r(e).
\tag{10}
$$

The 20-epoch analogue $\frac{1}{20}\sum_{e=E_r-19}^{E_r} a_r(e)$ is present in the corpus
as the CSV's `plateau` column and is **not used**: two of this project's headlines were
withdrawn for quoting it (Appendix A.2), and it is banned as a primary.

**Admissibility.** A run enters an analysis iff

$$
\mathrm{adm}(r)\;=\;\big[\,\texttt{window\_ok}(r)=1\,\big]\ \wedge\
\big[\,\texttt{complete}(r)=1\,\big]\ \wedge\
\big[\,\texttt{plateau5}(r)\ \text{readable}\,\big],
\tag{11}
$$

where $\texttt{window\_ok}(r) = [\,E_r > 20\,]$ — the tail in (10) must be a genuine
plateau and not most of a short probe — and
$\texttt{complete}(r) = [\,E_r \ge 0.95\,E^{\mathrm{req}}_r\,]$. The second condition is not
redundant: **17 of 2,113 runs pass `window_ok` while having completed under 90% of their
requested epochs**, and one of them (29 of 100 epochs, `plateau5` 85.228) sits inside a
primary arm, where including it moves that arm's mean by 1.22 pp and inflates its sem
19-fold. Of 2,113 rows, **1,671 are admissible**.

**Heterogeneity.** Across $k$ cells with estimates $y_i$ and standard errors
$\mathrm{se}_i$, writing $w_i = \mathrm{se}_i^{-2}$ and
$\bar{y} = \sum w_i y_i / \sum w_i$, we report Cochran's

$$
Q\;=\;\sum_{i=1}^{k} w_i\,(y_i-\bar{y})^2
\quad\text{on } k-1 \text{ df},
\qquad
\hat\tau^{2}=\max\!\left(0,\ \frac{Q-(k-1)}{\sum w_i-\dfrac{\sum w_i^{2}}{\sum w_i}}\right)
\tag{12}
$$

(DerSimonian–Laird), and, where a moderator is claimed, the exact partition of $Q$ into
its within-level and between-level parts, $Q = Q_{\mathrm{within}} + Q_{\mathrm{between}}$
with degrees of freedom adding likewise. Figure 2(b) is that partition.
```

### 2.3 Cross-reference edits (optional, low-collision, one line each)

These make the equations do work rather than sit there. Apply as many as survive the other
packages; none is load-bearing.

| § | find | replace with |
|---|---|---|
| §4.3 caption | `**Table 2 — D = uniform chunk − architecture-aligned nodewise` | `**Table 2 — D (Eq. 1) = uniform chunk − architecture-aligned nodewise` |
| §4.3 | `Welch difference of arm means; se from the two arm variances` | `Welch difference of arm means (Eq. 8); se from the two arm variances` |
| §4.3 | `reduction CIFAR-100's +1.640 pp is D/headroom = 0.055` | `reduction (Eq. 9) CIFAR-100's +1.640 pp is D/headroom = 0.055` |
| §4.4 | `DerSimonian–Laird **τ = 0.215 pp**` | `DerSimonian–Laird **τ = 0.203 pp** (Eq. 12)` — **and note that the whole sentence is rewritten by the `scorer-violation` package, which drops the GroupNorm cell; apply the `(Eq. 12)` tag to whatever that package leaves behind rather than to this string** |
| §4.6 | `by construction A + B = D and the shares are` | `by construction A + B = D (Eq. 7) and the shares are` |
| §4.7 | `Decomposing T = (D − G) + U on \`rl3\`` | `Decomposing T by Eq. 6 on \`rl3\`` |
| §5.4 | `\`D − G\` isolates the size-1 tail's contribution` | `\`D − G\` (Eqs. 1–2) isolates the size-1 tail's contribution` |
| §3.3 | *(the `window_ok`/`complete` prose that used to define admissibility)* | *superseded by Eq. 11; delete the duplicate sentence if 2.2 was applied* |

---

## 3. Gate S6 — the end matter, both placeholders filled

**REPLACE** everything from the anchor line `## End matter` to the end of the file.

Two things below are the authors' to confirm and are marked `⟨…⟩`: the grant identifiers
(only the authors know whether any exist) and the final author list. Everything else is
filled from the project record. **Nothing is invented**: the ALICE acknowledgement is the
facility's own required wording, quoted from `README.md`; the contribution statement is
CRediT and matches the authorship allocation recorded in
`docs/PLAN-appendix-collab.md`.

```markdown
## End matter

**Data availability.** The complete run table (`results/all_runs.csv`, 2,113 rows), the
raw per-epoch Slurm logs for every run (2,181 `.out` files, 17 MB, each carrying its own
`ARGS:` and `ENV:` line), all submission scripts (`bin/`), all optimiser patches
(`patches/`), all registered scorers (`analysis/`), the figure code and the reproduction
audit are deposited as a single archive. **DOI: pending** — a reserved DOI is minted at
submission and inserted here and in `CITATION.cff`; until then the artefact is identified
by repository commit `06d6539`. The archive is 6.1 MB, carries an md5 manifest for every
file, and reproduces every number in this paper with `make reproduce` on a laptop in
seconds, with no GPU and no dependency beyond `python3` and `matplotlib`. **No number in
this paper requires data that is not in that deposit.** The single exception, stated
because it is an exception: the per-group β trajectories (`probe*.jsonl`, ≈42 GB) are
excluded for size and are available from the authors on request; the box-occupancy
summaries derived from them are in the run table's `beta_clip` column and in the scorers'
printed output.

**Code availability.** The optimiser is the released MetaOptimize `HF.py` plus the patches
in `patches/`, distributed as patches rather than as a fork, each carrying an identity test
against the authors' own working `blockwise` path (`tests/`). Analysis code, figure code
and the reproduction audit are released under MIT; the run table, logs and documentation
under CC-BY-4.0; the patches carry the parent work's license.

**Ethics.** No human or animal subjects and no personal data. CIFAR-10 and CIFAR-100 are
standard public benchmarks used under their stated terms; no other data was collected. The
work is a methodological audit of an optimisation method and we see no dual-use or
deployment risk specific to it. The one ethical exposure we do carry is a conflict of
interest, disclosed in full below rather than in a footnote, and the mitigation for it was
put in place before the results existed rather than after.

**Competing interests.** **A supervising author of this work is a co-author of
MetaOptimize (Sharifnassab, Salehkaleybar & Sutton), the method this paper audits.** We
state this plainly because several of this paper's results are negative about that method:
the 1.807 pp deficit against a tuned SGD+cosine baseline (§7 T4), the finding that four
fifths of the reported granularity benefit at the parent's own default meta-stepsize is
tolerance to an over-large meta-step rather than accuracy (§4.1), and the eight dead
mechanisms of §5. The mitigation is procedural and is auditable in the deposit: every
decision rule and acceptance band for the negative results was committed to version
control **before** the corresponding runs were submitted, in a scorer that is run unedited
and whose printed verdict is quoted rather than paraphrased (§3.4, §6.2); the supervising
author had no role in setting those rules; and where a batch has **no** such
pre-registered scorer we say so explicitly in the provenance table in §8 rather than
letting the reader assume coverage. ⟨If the final author list includes a further co-author
of the parent paper, that must be stated here in the same sentence, and §5.9's negative
result on hierarchical partial pooling — an idea originated by a proposed co-author — must
be disclosed as a second, independent conflict of the same kind.⟩ The authors declare no
financial competing interests.

**Funding.** ⟨To be completed by the authors with any grant identifiers.⟩ This work was
carried out as an MSc research project at LIACS, Leiden University, and received no
dedicated project funding; compute was drawn from the institutional allocation
acknowledged below. The absence of a compute budget is a scope limit rather than a
formality: it is the reason ImageNet-scale replication is out of reach (§7) and the reason
the additive tail experiment proposed in §9 is registered but unfunded.

**Acknowledgements.** This work was performed using the compute resources from the
Academic Leiden Interdisciplinary Cluster Environment (ALICE) provided by Leiden
University. We thank the ALICE support team. ⟨Any further acknowledgements to be added by
the authors; note that a contribution of idea origination is co-authorship, not an
acknowledgement — see Author contributions.⟩

**Author contributions.** Stated in CRediT terms. ⟨The author list is to be finalised by
the authors; the roles below describe the work as it was actually done and must be
reassigned, not rewritten, if the list changes.⟩
**M. Ahmaditeshnizi** — Conceptualization (equal), Methodology, Software (the chunkwise,
1-D-tensor, permuted-node and probe partitions and their identity tests, as patches to the
released MetaOptimize implementation), Validation, Formal analysis, Investigation (all
2,113 runs), Data curation, Writing – original draft, Visualization, Project
administration.
**S. Salehkaleybar** — Conceptualization (equal), Supervision, Resources, Funding
acquisition, Writing – review & editing, and continuity with the parent work. Explicitly
**not** involved in setting the pre-registered decision rules or acceptance bands used for
the negative results in §5, for the reason given under Competing interests.
⟨A third contributor originated the hierarchical partial-pooling design evaluated and
withdrawn in §2.4 and §5.9. Idea origination of that specificity is a substantial
intellectual contribution and is co-authorship rather than an acknowledgement; the authors
are to settle inclusion and order before submission.⟩
All authors accept accountability for the integrity of the work as a whole.

**Use of AI assistance.** Analysis scripts, batch submission scripts, the correction
register, the figures and this draft were produced with substantial assistance from a
large language model operating on the project repository under human direction, including
at the analysis-design stage and not only at the writing stage. We disclose this as a
first-class integrity item rather than a footnote, and we state the controls that make it
checkable rather than asking to be trusted. Every number in this paper is re-derived from
the run table or the raw logs by committed code at build time and asserted against what the
paper prints (`analysis/c98_reproduce.py`, in the deposit; it exits non-zero if any
headline fails to reproduce); registered decision rules and bands were committed to version
control before the corresponding runs were submitted; and the discrepancies this procedure
surfaced between the project's internal record and the data are recorded in Appendix A
rather than corrected silently. Three claims were withdrawn by that procedure during
writing, and one whole batch was found to have run a different experiment from the one it
declared (§6.1); both outcomes are reported.

**Correspondence.** ⟨author email⟩.
```

---

## 4. Gate S11 / Q20–Q22 — §8 Reproducibility, rewritten

**REPLACE** everything from the anchor line `## 8. Reproducibility` up to, but not
including, the line `## 9. Conclusion` (keep the `---` separator).

```markdown
## 8. Reproducibility

**One command.** The deposit reproduces every number in this paper:

    make reproduce            # every headline, re-derived and checked against the paper
    make reproduce-table2     # Table 2 and Figure 1 alone
    make figures              # regenerate all four figures from the CSV
    make verify               # md5 every file against the manifest

`make reproduce` runs in seconds on a laptop, needs `python3` and `matplotlib` and nothing
else — no GPU, no PyTorch, no cluster — and **exits non-zero if any headline fails to
reproduce**. It prints one line per number: *derived value | paper value | PASS/FAIL |
where it appears in this paper*. Its output at the time of writing is included in the
deposit as `REPRODUCTION-AUDIT.txt`.

**Artefact and DOI.** The deposit is 6.1 MB in 137 files, with `MANIFEST.md5` covering
every one of them. **DOI: pending**; a reserved DOI is minted at submission and written
into the paper, into `CITATION.cff` and into the Data-availability statement before
camera-ready. Until then the artefact is identified by repository commit `06d6539`.

**Data.** `data/all_runs.csv`, 2,113 rows, one per run, with the full configuration
(network, dataset, batch size, granularity, base, meta, η, α₀, γ, augmentation, β-box,
hierarchical mode, λ, r, seed), the outcome columns (`best_test`, `final_test`,
`plateau5`, `plateau`, `auc`, epochs-to-threshold), the provenance columns (`job_id`,
`account`, `node`, `wallclock_min`), the two admissibility flags (`window_ok`,
`complete`), and a `dup_group` column marking the eighteen pairs of differently-named runs
that resolve to the same experiment (see below). Raw per-epoch series are the 2,181 Slurm
`.out` files in `logs/raw_out.tar.gz`; each carries its own `ARGS:` and `ENV:` line, which
is the authority on what that run actually did.

**Compute.** 2,098 runs carry a wallclock; they total **1,582 GPU-hours** over 29 distinct
nodes and two accounts, on NVIDIA L4 24 GB, RTX 2080 Ti 11 GB, A100 80 GB and A100 MIG
40 GB partitions. GPU class is recorded per run and was measured to carry no systematic
offset between arms (§6.3); every primary is within batch, so a per-node offset shared by
the two arms cancels identically.

**Environment.** One virtual environment, both accounts, verified identical at write time:

| | |
|---|---|
| Python | 3.10.4 (`Python/3.10.4-GCCcore-11.3.0`) |
| PyTorch | **2.0.1+cu118** |
| CUDA (torch build) | **11.8** |
| torchvision | 0.15.2+cu118 |
| numpy | 1.26.4 (torch 2.0.1 is incompatible with numpy ≥ 2) |
| scheduler | Slurm |

**Seeds.** Every run records its seed; seeds are 0–8. Batches specify their seed set in the
submission script and the scorers assert the registered set is present before scoring. The
table below gives, per batch, the seeds actually realised — which is not always the
registered set, and where it is not, we say so.

**Per-batch provenance.** Every batch behind a cell in Table 2, with the script that
submitted it, the scorer registered for it, that scorer's md5, the seeds realised, the
β-box, and the account. **Five batches have no scorer that was registered before their
runs existed**; we mark them rather than let the reader infer coverage from §3.4.

| batch | submission script | registered scorer | scorer md5 (first 12) | seeds realised | n | β-box | account |
|---|---|---|---|---|---|---|---|
| `cc1` | `c81_concordance.sh` | `c81_cc1_score.py` | `c138eab327c1` | 3,4,5 | 12 | −15:−2.3026 | A |
| `mm1` | `c76_matched_m_partition.sh` | `c76_mm1_score.py` | `57e48c32e066` | 0,1,2 | 6 | −15:−2.3026 | A |
| `pp1` | `c77_permuted_partition.sh` | `c77_pp1_score.py` | `3c6aa6f97627` | 0,1,2 | 9 | −15:−2.3026 | A |
| `bn1` | `c78_degenerate_tail.sh` | `c78_bn1_score.py` | `285632b3b8a6` | 0,1,2 | 9 | −15:−2.3026 | A |
| `gn1` | `c84_normaliser_transfer.sh` | `c84_gn1_score.py` | `82c515d1ad49` | 0–7 | 24 | −15:−2.3026 | B |
| `ml2` | `c94_meta_ladder.sh` | **none registered** | — | 0,1,2 (each run twice) | 24 | −15:−2.3026 | B |
| `rl3` | `c87_rule11_ladder.sh` | `c87_rl3_score.py` | `b008216753a0` | 0,1,2 | 24 | −30:9.0 | B |
| `fa1` | `c82_field_wideclip.sh` | `c82_fa1_score.py` | `b96ab2080cfa` | 0–5 | 24 | −25:−2.3026 | A |
| `hz3` | `c87_horizon_300ep.sh` | `c87_hz3_score.py` | `16769a161630` | 0–5 | 24 | −15:−2.3026 **and** −30:9.0 | A |
| `aw1` | `c90_awbase.sh` | `c88_scorers.py` | `0363bcccb4d3` | 0,1,2 | 12 | −15:−2.3026 | B |
| `nl1` | `c92_norm_ladder.sh` | **none registered** | — | 0,1,2 | 24 | −15:−2.3026 | A |
| `g3m` | `c83_gen_r34_merged.sh` | `c83_gen_score.py` | `ffdabe0a1790` | 0–8 | 36 | −15:−2.3026 | A |
| `r50` | `c93_resnet50.sh` | **none registered** | — | 0,1,2 | 12 | −15:−2.3026 | A |
| `gc1` | `c83_gen_c100_screen.sh` | `c83_gc1_score.py` | `5e775f417031` | 0,1,2,3 | 8 | −15:−2.3026 | A |
| `gm2` | `c91_c100_mech.sh` | **none registered** | — | 0,1,2 | 12 | −15:−2.3026 | B |
| `ar1` (excluded) | `c79_argmax_robustness.sh` | `c79_ar1_score.py` | `2396e5cf2372` | 0,1,2 | 12 | −15:−2.3026 | A |

Three things this table is meant to stop a reader from having to guess.
(i) **The β-box is not constant across cells**, so `rl3` (−30:9.0) and `fa1`
(−25:−2.3026) are not box-matched to the rest, and `hz3` contains one seed whose two arms
sit in *different* boxes (Figure 3, §4.8). Nothing here is pooled across boxes.
(ii) **`ml2`'s three seeds were each run twice** under two names; the CSV's `dup_group`
column records the eighteen such pairs corpus-wide, and any n, se or t computed over rows
sharing a `dup_group` averages within the group first and counts n as the number of
distinct groups. That is what makes `ml2` a 3 v 3 cell with se 0.195, not a 6 v 6 cell with
se 0.142 (§6.1). The reproduction audit enforces the rule, so a reader cannot accidentally
recover the wrong number.
(iii) **Five batches have no pre-registered scorer** — `ml2`, `nl1`, `r50`, `gm2`, and the
`sm3` batch discussed in §6.1. `nl1` alone supplies two of Table 2's rows and both of the
single-batch levels of the base-optimiser moderator in §4.4. Their CSV values were checked
field-by-field against their own runs' `ARGS:` lines and are correct; what is missing is
not the data but the commitment-before-the-fact, and we mark it rather than claim coverage
we do not have.

**Code.** The optimiser is the released MetaOptimize `HF.py` plus the patches in
`patches/` (`patch_chunkwise.py`, `patch_nodebn.py`, `patch_permnode.py`,
`patch_zpool.py`, the probe patches, and the augmentation patch), each of which carries an
identity test against the authors' own working `blockwise` path. Analysis is 60+ scorers
under `analysis/`; the ones that gate a verdict are named in §3.4 and quoted verbatim. The
figures are `analysis/c98_figures.py` and contain no typed value.

**Registration.** Batches carry a submission script under `bin/` with numbered
pre-submission guards: the run table must be present; the required patches must be present
in the live tree; group counts are **measured** on the instantiated optimiser and asserted
equal to the registered values; there must be no name collision; the comparator batch must
exist; and there must be disk and queue headroom. Decision rules and bands are committed
before submission. `analysis/c88_scorers.py --selftest` runs 31 assertions in both
directions; it currently reports one failure, `S6e`, which asserts that the count-matched
partition rows are all one base optimiser — an assertion made true at cycle 88 and made
false, deliberately, by the `aw1` and `nl1` batches.

**An integrity check a reader can run on our own logs.**
`analysis/argsline_guard.py` sweeps every run's own `ARGS:` line for a repeated flag,
because argparse silently takes the last occurrence and a submission script can therefore
run a different experiment from the one it declares. Over the 2,189 runs carrying an
`ARGS:` line on both clusters it finds exactly 36 with a repeated flag, in two batches, and
those two batches are reported as void-as-designed in §6.1. The partition axis, the budget
axis and the step-size axis (`--alg-base`, `--stepsize-groups`, `--meta-stepsize`,
`--alpha0`, `--num-epochs`, `--seed`, `--normalizer-param-*`) are single-occurrence in every
run in the corpus. We recommend the check to anyone running batch experiments through a
shell wrapper; it cost us two batches to learn.

**Deviations from the parent's configuration, stated so absolute numbers are not
misread.** (i) We enable RandomCrop + horizontal flip; the parent's text and released code
appear not to. Without augmentation ResNet-18 memorises CIFAR-10 within an epoch and there
is no optimisation headroom for a step-size method to exploit, so we regard augmentation as
scientifically necessary — but it means our absolute accuracies are not comparable to the
parent's. (ii) Our headline partition programme uses a Lion meta-optimiser where the
parent's SGDm arm uses Adam. (iii) We clip β to a box; the parent mentions no clipping.
Box occupancy is measured per run, **per coordinate** from the `n_at_lo`/`n_at_hi` rails
and never from the 62-element per-tensor summary — reading the summary instead reported
0.000000 occupancy on 24 runs that were clipped in every record and inverted an arm
ranking, which voided the `ar1` batch (§3.3).

**What a reader can falsify on their own hardware in an afternoon.** Merge your
one-dimensional tensors into one step-size group each and measure the difference at fixed
group count; and re-tune both arms of any granularity comparison you have and see how much
of the gap survives.
```

---

## 5. What the reader of the deposit gets

`release/` (137 files, 6.1 MB) is built by `analysis/c98_release.py` and verifies against
its own manifest. Layout:

```
release/
  README.md               DOI PENDING, layout, the house rules the code enforces
  Makefile                reproduce | reproduce-table2 | figures | logs | verify | all
  MANIFEST.md5            md5 + size of all 137 files; `make verify` checks them
  REPRODUCTION-AUDIT.txt  the audit as captured at build time
  ENVIRONMENT.md          exact versions; how to re-run an experiment
  CITATION.cff            DOI field reads PENDING, with why
  data/all_runs.csv       the run table of record
  logs/raw_out.tar.gz     2,181 raw .out files (17 MB unpacked) — `make logs`
  code/                   the audit, the figure code, the aggregator, the args guard,
                          the dup_group repair, scorers/, patches/, tests/,
                          verify_manifest.py
  scripts/                every batch submission script, with its guards
  figures/                the four figures, PDF + PNG
  docs/                   CORRECTIONS.md, ARGS-AUDIT.md, DATASETS.md, OPERATIONS.md,
                          MASTER-TABLE.md
```

Three properties worth stating to a reviewer:

1. **The build refuses to ship a stale number.** `c98_release.py` runs the audit and exits
   without writing the deposit if any check fails.
2. **The README's headline numbers are generated, not typed** — they are the audit's own
   output, pasted in by the builder.
3. **The figures are byte-reproducible**, so `make verify` still passes after
   `make figures`. Nothing in the deposit depends on when it was built.

Before minting the DOI: rebuild from a **clean** checkout. The current build stamps a
warning into `release/README.md` because the working tree was dirty when it ran; that
warning disappears on a clean rebuild and its presence is the check.

---

## 6. Integrator checklist

| # | action | anchor | shared? |
|---|---|---|---|
| 1 | insert Fig. 1 block | end of §4.3, after `on one axis.` | no |
| 2 | insert Fig. 2 block | end of §4.4, before `### 4.5` | **§4.4** |
| 3 | insert Fig. 3 block | end of §4.8, before the `---` | no |
| 4 | insert Fig. 4 block | end of §5.4, before `### 5.5` | **§5.4** |
| 5 | append the figure sentence to §3.4 | after the `c88_scorers.py` md5 | no |
| 6 | replace §3.2 in full (Eqs. 1–9) | `### 3.2 The contrasts` | no |
| 7 | replace §3.3's first two paragraphs (Eqs. 10–12) | `**Metric.** \`plateau5\`` | no |
| 8 | apply the cross-reference edits | table in §2.3 | partly |
| 9 | replace `## 8. Reproducibility` in full | `## 8. Reproducibility` | no |
| 10 | replace `## End matter` in full | `## End matter` | no |
| 11 | resolve the four `⟨…⟩` author-only items | end matter | authors |
| 12 | if the integrator **keeps** the GroupNorm cell, regenerate with `--with-gn` and swap "sixteen"→"seventeen" and "eleven-cell"→"twelve-cell" in the Fig. 1 and Fig. 2 captions | figure captions | **§4.4 / scorer-violation** |
| 13 | `python3 analysis/c98_reproduce.py` must exit 0 before submission | — | no |
| 14 | rebuild `release/` from a clean checkout; mint the DOI; paste it into §8, the end matter and `CITATION.cff` | — | no |

Items 2 and 4 land in sections another package is rewriting; each carries a fallback
anchor and a note on which numbers must move together.

---

## 7. Every number this package changed, with the re-derivation

Nothing here is a science change. Four of the five are corrections to values quoted in
`docs/STATUS.md` that did not survive re-derivation at the printed precision, and the
fifth is a rule violation this package found in its own first draft of Figure 4.

### 7.1 `ml2`: se 0.142 → **0.195**, t 3.20 → **2.34**; and G t 2.44 → **2.38**

The ARGS audit established that `ml2`'s two halves resolve to the same command line
*including* `--seed`, so the batch is three seeds run twice, not six seeds. Averaging
within the pair before differencing:

```
ml2 D  = +0.455667   se 0.195115   t 2.3354      (3 groups v 3 groups)
ml2 G  = +0.173333   se 0.072717   t 2.3837
```

The **point estimates are unchanged** — +0.456 and +0.173 to three decimals — and both
survive at nominal α. This is implemented once, in `analysis/c98_figures.py`'s `arm()`,
which reads the CSV's `dup_group` column and falls back to the registered table in
`analysis/args_repair.py` when the repair has not yet been applied. The figures therefore
give the corrected value **whether or not `args_repair.py --apply` has been run**, and give
the same value after it is.

Consequences that must move together: Table 2 row 5 (`6 v 6` → `3 v 3 (×2 reruns)`,
± 0.142 → ± 0.195, t 3.20 → 2.34); the §5.4 G table's `ml2` row (t 2.44 → 2.38); and §6.1's
"two independent 3 v 3 measurements", which is false — the halves share their seeds, so the
0.197 pp spread it quotes is a **nondeterminism** bound, not a seed or batch bound. Over the
twelve same-seed pairs the nondeterminism bound is mean |Δ plateau5| **0.163 pp**, max
**0.472 pp**.

The twelve-cell pool, Q and τ are **untouched**: `ml2` is not one of the twelve
byte-identical cells (Table 2 rows 1–4, 6–13). Q remains 43.19 on 11 df, τ 0.215.

### 7.2 §4.6's alignment interval: upper limit +0.299 → **+0.298**

`docs/STATUS.md` R0 item 3 prints the bounded null as `[−0.317, +0.299]`. Re-derived:

```
A = -0.009333,  se = 0.156918
A ± 1.96 se  =  [-0.316892, +0.298225]   ->  [-0.317, +0.298]
```

A one-in-the-last-digit correction, but it is a *registered interval* and the paper is
about not letting those drift. Use **[−0.317, +0.298]**. Nothing else in §4.6 moves:
A = −0.009 ± 0.157, B = +0.590, A + B = +0.581 = D exactly.

### 7.3 The §4.4 decomposition, at printed precision

`docs/STATUS.md` gives `Q 4.22/7, pool +0.555 ± 0.045, between-base Q 32.1/3`. Re-derived
from the CSV by inverse-variance meta-analysis over the eleven byte-identical ResNet-18
cells (GroupNorm excluded):

| quantity | STATUS | re-derived | use |
|---|---|---|---|
| within-SGDm Q (k=8) | 4.22 | **4.21** on 7 df | 4.21 |
| within-SGDm p | 0.75 | **0.76** | 0.76 |
| within-SGDm pool | +0.555 ± 0.045 | **+0.556 ± 0.045** | +0.556 |
| within-SGDm τ | 0.000 | **0.000** | 0.000 |
| between-base Q | 32.1 on 3 df | **32.20** on 3 df, p 4.8e-7 | 32.2 |
| share of Q | "~75%" | **88.4%** of the live 11-cell Q; **74.6%** of the legacy 12-cell Q | say which |

The last row matters. "The base optimiser explains ~75% of Q" is the share of the
**twelve**-cell Q (32.20 / 43.19) — a denominator that contains the GroupNorm cell, which
R0 item 1 removes from the paper. Against the eleven-cell Q that the decomposition is
actually computed on, it is **88.4%** (32.20 / 36.40). Both are true of different denominators;
quoting one without its denominator is how "~75%" reads as though the GroupNorm cell were
in the partition, which after R0-1 it is not. Figure 2(b) prints the eleven-cell version
and labels its denominator on the axis.

### 7.4 The pooled SGDm D − G: +0.499 → **+0.514**, and a rule violation caught

`docs/STATUS.md` R0 item 15 asks §9 to quote "the POOLED SGDm D − G (+0.499 ± 0.062)"
instead of `cc1`'s maximum. That value is the six ResNet-18/CIFAR-10 SGDm cells pooled
**with `ml2` at its uncollapsed se**. After §7.1 it moves:

| pool | value | Q |
|---|---|---|
| k=6, ResNet-18/CIFAR-10 SGDm, old `ml2` se | +0.500 ± 0.062 | — |
| k=6, ResNet-18/CIFAR-10 SGDm, corrected | **+0.514 ± 0.064** | 4.22 / 5 |
| k=8, all CIFAR-10 SGDm cells (adds R34, R50) | **+0.514 ± 0.056** | 4.52 / 7 |
| k=9, adding the CIFAR-100 cell | +0.558 ± 0.055 | **17.17 / 8** |

Use **+0.514 ± 0.056** (k=8). The last row is the interesting one and is worth a sentence
in §9: adding a single CIFAR-100 cell to a percentage-point pool moves the estimate by
+0.044 and multiplies Q by 3.8, which is §4.3's commensurability rule doing measurable
work rather than being a stylistic preference. **This package's own first draft of Figure 4
committed that violation** — it pooled the CIFAR-100 cell and reported +0.558 — and it was
caught by the rule being written into the figure code as an assertion rather than kept in
prose. That is the argument for putting house rules in the code.

### 7.5 The `hz3` seed-5 sensitivity: t −1.93 → **−1.94**

The red-team note records the box-matched slope as t −1.93. Re-derived from the raw epoch
series, paired within run:

```
D(300) - D(100), 5 box-matched seeds = -0.206800   se 0.106712   t -1.9379  ->  -1.94
```

The verdict is unchanged in both directions: −0.149 ± 0.105 (t −1.42) on all six seeds and
−0.207 ± 0.107 (t −1.94) on the five, neither excluding zero. Figure 3 prints both, which
is the honest form of the sensitivity the red team asked for.

### 7.6 Nothing else moved

Every other number the four figures and the audit touch reproduces the draft **exactly**:
all seventeen Table 2 D's and their ses (sixteen after R0-1 removes the GroupNorm row);
the legacy twelve-cell pool +0.546, Q 43.19/11, τ 0.215; the live eleven-cell pool
+0.571 ± 0.037, Q 36.40/10, τ 0.203, rms se 0.152; all eleven T values; all twelve G and
D − G values; the alignment null and the A + B = D identity; the budget table at 100/200/300;
and §7 T4's 93.317 / 95.124 / 1.807. The audit output is in
`release/REPRODUCTION-AUDIT.txt`.

---

## 8. New weaknesses this package found

### 8.1 STANDING RULE 21 was breached **five** times, not twice — and it touches live cells

`docs/ARGS-AUDIT.md` records that `sm3` and `ml2` ran with no registered scorer. Searching
`analysis/` for every batch behind a Table 2 row finds **three more**:

| batch | Table 2 rows it supplies | scorer in `analysis/` |
|---|---|---|
| `ml2` | 5 | none |
| `nl1` | **12 (SGD) and 13 (RMSProp)** | none |
| `r50` | 15 | none |
| `gm2` | 17 | none |
| `sm3` | (the 18th cell, pending ingest) | none |

`nl1` is the serious one. It is a single sbatch loop that produced **both** the SGD rungs
and the RMSProp rungs, and those two cells are exactly the two single-batch levels on which
the §4.4 rewrite's "the base optimiser explains most of Q" rests. So the new headline's
weakest flank is also its unregistered one. `analysis/c97_bm2_score.py` — the registered
scorer for the *planned* `bm2` replication — says this in its own header, independently of
this package.

**What to do.** Nothing in the science changes: all CSV values for these batches were
reconciled field-by-field against their own runs' `ARGS:` lines with zero mismatches, and
this package re-derived every one of their contrasts from the raw data. What must change is
the *claim of coverage*. §3.4 currently lists eight scorers as "the scorers used here",
which reads as coverage; the §8 provenance table above marks the five gaps explicitly, and
§6.2 should say "five batches, including two that supply live cells in Table 2" where it
now implies the rule was broken once. The R3 replication batch (`bm2`) is the fix, and it
is already registered.

### 8.2 `analysis/argsline_guard.py` does not recurse

Its `collect_files` globs `<dir>/*.out` and does not descend, so it silently skips the
twelve local `.out` under `runs/failed_hier_v1/`. Those twelve are clean and none is in the
CSV, so nothing is wrong today — but the guard is the corpus's defence against exactly the
defect that voided two batches, and a guard with a blind spot is worse than a guard with a
known limit. `analysis/c98_figures.py`'s `series()` was written to recurse for this reason.
One-line fix, not applied here because `argsline_guard.py` is not this package's file.

### 8.3 The local `.out` mirror is short by twelve

The deposit ships 2,181 raw `.out` files. The two clusters together hold 2,189 with an
`ARGS:` line, plus `sm3`'s 12 which are not mirrored locally at all. Before the DOI is
minted the mirror should be completed, or the deposit's README should state the shortfall.
It currently states the count it actually ships, which is honest but not complete.

### 8.4 `sm3` is not in the CSV, so the figures show sixteen cells, not seventeen

`sm3`'s twelve rows are still un-ingested (2,113 → 2,125). Its arm means, re-derived from
the cluster's own `.out` files during this package's work, are nodewise 93.103, chunk777
93.244, nodewise1d 93.019, chunk2325 93.315, giving **D +0.141 ± 0.064 (t 2.22)** and
**G +0.296 ± 0.096 (t 3.07)** — an eighteenth count-matched cell, still positive, and a
second independent AdamW design point. `analysis/c98_figures.py` picks it up **with no
edit** the moment `aggregate.py` ingests it: the cell list is keyed on run-name prefix and
granularity, so adding `("sm3", "ResNet-18", "C10", "AdamW", "1e-4", 100,
("sm3-awrms-ch","chunk777"), ("sm3-awrms-node","nodewise"), ("sm3-awrms-c23","chunk2325"),
("sm3-awrms-n1d","nodewise1d"))` to `CELLS` is the whole change, and the pool, the counts
and the captions follow on their own. Until then the figures say sixteen — seventeen with
`--with-gn` — and the paper must say the same number the figures do.

### 8.5 The attrition arithmetic needs its denominator stated

2,113 − 1,671 = 442 dropped. The three flags are **not** disjoint: 425 rows fail
`window_ok`, 25 have no readable `plateau5`, 17 fail `complete`. The partition that sums to
442 is *no plateau5* 25, then *window_ok=0* 400, then *incomplete* 17 — i.e. the "400" in
the R0 checklist is `window_ok=0` **after** removing the 25 with no `plateau5`, not the
count of rows failing `window_ok`, which is 425. Both are correct; only one is 400. The
attrition-table package should print the order of exclusion. One defusing fact re-derived
here: **all 425 of the `window_ok` failures requested ≤ 20 epochs**, i.e. they are probes,
not casualties.

---

## 9. Left open

* The `⟨…⟩` items in the end matter — grant identifiers, the final author list, the third
  contributor's inclusion, and the correspondence address — are the authors' and cannot be
  filled from the repository.
* **The DOI itself.** No DOI can be minted from here: it requires an account action on
  Zenodo or the institutional repository, and this package states it as pending in all four
  places it appears rather than inventing one.
* `sm3`'s ingest (§8.4), the `argsline_guard.py` recursion fix (§8.2) and the `.out` mirror
  completion (§8.3) belong to the housekeeping package, not this one; each is named here
  with the exact change so it is not lost.
