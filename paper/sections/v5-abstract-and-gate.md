# Package `abstract-and-gate` — closes G1, G2, G3, G4

**Status: all four items verified closed on BOTH files, with paperfactory's own checkers.**
Built against `paper/paper.tex` and `paper/DRAFT-v4.md` as of repo HEAD `2a499e4`
(both files last modified 2026-09-02 20:56; unchanged while this package was built).
`tectonic paper.tex` on the patched tree: **exit 0, 61 pages, 0 undefined references,
0 undefined citations, 0 `??`** — identical to the pre-patch build.

Nothing here is edited into `paper.tex` or `DRAFT-v4.md` by this package. Every block below is
keyed to a **verbatim, unique** anchor string (uniqueness asserted with `count(...) == 1` in the
build script, not eyeballed), so the edits can be applied in any order relative to other packages
and do not depend on line numbers.

---

## 0. What the gate said, and what it says now

The four items were all *structural*: the content the gate wanted was already in the manuscript,
in the wrong container (G1), missing from the abstract (G2), never named with the word the
matcher looks for (G3), or not separated into the two families the checker requires (G4).
G2 + G3 + G4 were done as one piece because the abstract had to **shrink** from 255 words to
`<= 230` while **gaining** six reporting items; that in-and-out is the whole design constraint.

| item | checker | before | after |
|---|---|---|---|
| G1 | `q1_meta_gate._static_checks` end-matter regex | 0 of 6 found | **6 of 6 found** |
| G2 | `reporting_profile.assess_reporting_completeness` (`se_empirical`) | 10/17, 6 abstract items missing | **17/17, none missing** |
| G3 | same, `methods_obligations` | `Workload or usage profile specified in replicable detail` MISSING | **present** |
| G4 | `text_quality.assess_text_quality` | 255 words (band 120–230); 67-word sentence (cap 62); Threats not separated | **0 defects** |

---

## 1. Verification (run at write time; pasted verbatim)

Run from `/Users/teshnizi/PaperFactory` with `sys.path.insert(0, '.')`, calling
`paperfactory.agents.text_quality.assess_text_quality` / `._abstract_defects`,
`paperfactory.agents.reporting_profile.assess_reporting_completeness`, and the exact
end-matter regex from `paperfactory/agents/q1_meta_gate.py:576-580` +
`:687-693` (`\\section\*?\{\s*(?:<title>)\s*\}`, case-sensitive).
`_abstract_defects` is run on **both** files: on `paper.tex` through
`_extract_abstract` (the `\begin{abstract}` environment), on `DRAFT-v4.md` on the text
between `## Abstract` and the following `---`.

```
==============================================================================
BEFORE  (repo working tree, HEAD 2a499e4)
==============================================================================
paper.tex  assess_text_quality.abstract_defects : ['abstract too long/dense (255 words; target <= 230)', 'abstract contains an overloaded Results-style sentence; split claims across shorter sentences']
paper.tex  assess_text_quality.section_defects  : ['Limitations should separate included-evidence limits from review/process limits']
paper.tex  assess_text_quality.caption_defects  : []
paper.tex  se_empirical score                   : 10/17
paper.tex  abstract obligations missing         : ['Objective and the engineering question', 'Study type and named methodology', 'Artifact or subject systems under study', 'Sampling frame and unit of analysis', 'Comparison against state-of-the-art alternatives', 'Threats to validity and construct validity of the measure']
paper.tex  methods obligations missing          : ['Workload or usage profile specified in replicable detail']
paper.tex  q1_meta_gate end matter FOUND        : []
paper.tex  q1_meta_gate end matter MISSING      : ['Competing Interests', 'Funding', 'Data Availability', 'Code Availability', 'Ethics', 'Author Contributions']
paper.tex  abstract words / longest sentence    : 255 / (67, 414)  overloaded=True
DRAFT-v4.md _abstract_defects                   : ['abstract too long/dense (267 words; target <= 230)', 'abstract contains an overloaded Results-style sentence; split claims across shorter sentences']
DRAFT-v4.md abstract words / longest sentence   : 267 / (70, 412)  overloaded=True
DRAFT-v4.md abstract obligations missing        : ['Objective and the engineering question', 'Study type and named methodology', 'Artifact or subject systems under study', 'Sampling frame and unit of analysis', 'Comparison against state-of-the-art alternatives', 'Threats to validity and construct validity of the measure']
DRAFT-v4.md threats separation cues             : {'included evidence': False, 'review process': False}
DRAFT-v4.md workload cues in file               : []
DRAFT-v4.md end-matter headings                 : {'Competing Interests': 0, 'Funding': 0, 'Data Availability': 0, 'Code Availability': 0, 'Ethics': 0, 'Author Contributions': 0}

==============================================================================
AFTER   (v5-abstract-and-gate applied)
==============================================================================
paper.tex  assess_text_quality.abstract_defects : []
paper.tex  assess_text_quality.section_defects  : []
paper.tex  assess_text_quality.caption_defects  : []
paper.tex  se_empirical score                   : 17/17
paper.tex  abstract obligations missing         : []
paper.tex  methods obligations missing          : []
paper.tex  q1_meta_gate end matter FOUND        : ['Competing Interests', 'Funding', 'Data Availability', 'Code Availability', 'Ethics', 'Author Contributions']
paper.tex  q1_meta_gate end matter MISSING      : []
paper.tex  abstract words / longest sentence    : 215 / (29, 192)  overloaded=False
DRAFT-v4.md _abstract_defects                   : []
DRAFT-v4.md abstract words / longest sentence   : 226 / (31, 196)  overloaded=False
DRAFT-v4.md abstract obligations missing        : []
DRAFT-v4.md threats separation cues             : {'included evidence': True, 'review process': True}
DRAFT-v4.md workload cues in file               : ['workload', 'task suite', 'scenario']
DRAFT-v4.md end-matter headings                 : {'Competing Interests': 1, 'Funding': 1, 'Data Availability': 1, 'Code Availability': 1, 'Ethics': 1, 'Author Contributions': 1}
```

Two further checks, because this package adds prose to `DRAFT-v4.md` and the draft is censused:

```
$ python3 analysis/c98_reproduce.py --census --draft paper/DRAFT-v4.md      # HEAD
     arXiv ids and software versions  = QUANTITIES      1696  (747 distinct)
$ python3 analysis/c98_reproduce.py --census --draft <patched draft>        # this package
     arXiv ids and software versions  = QUANTITIES      1696  (747 distinct)
```

**This package is census-neutral: it adds zero distinct quantity-numerals to the draft.**
That is deliberate. A first draft used numbered markdown headings (`### 7.1 …`, `### 7.2 …`)
for the Threats split and the census counted `7.1` and `7.2` as quantities, moving the
distinct count 747 → 749 and silently changing F2's target. The markdown headings are therefore
**unnumbered**; the LaTeX `\subsection{}`s number themselves and `paper.tex` is not censused.
Every decimal the new Methods paragraph introduces (`3.10.4`, `2.0.1+cu118`, `11.8`, `0.15.2`,
`1.26.4`) is caught by the census's own `_VERSION` filter.

---

## 2. G1 — six sectioning promotions in the End matter (zero content change)

`paperfactory/agents/q1_meta_gate.py:576` declares the required titles and `:687` matches them
with `re.search(r"\\section\*?\{\s*(?:" + alias_pat + r")\s*\}", tex)` — **case-sensitive**,
and only against `\section` / `\section*`. The manuscript had all six statements, but as
`\paragraph{}` blocks with lower-case second words (`Data availability.`), so the regex matched
nothing. The fix is six one-line promotions and **not one word of prose changes**.

### 2.1 `paper/paper.tex`

Six single-line replacements. Each anchor occurs exactly once in the file.

| line (HEAD) | replace this line | with this line |
|---|---|---|
| 3943 | `\paragraph{Data availability.}` | `\section*{Data Availability}` |
| 3971 | `\paragraph{Code availability.}` | `\section*{Code Availability}` |
| 3978 | `\paragraph{Ethics.}` | `\section*{Ethics}` |
| 3985 | `\paragraph{Competing interests.}` | `\section*{Competing Interests}` |
| 4011 | `\paragraph{Funding.}` | `\section*{Funding}` |
| 4026 | `\paragraph{Author contributions.}` | `\section*{Author Contributions}` |

Four end-matter blocks are **deliberately left as `\paragraph{}`**, because each is a sub-item of
the section it now sits under and the gate does not ask for them:

* `\paragraph{A second interest, of a different kind.}` — sits under **Competing Interests**,
  which is where it belongs: it is the second disclosed interest.
* `\paragraph{Acknowledgements.}` — sits under **Funding** (the compute allocation it thanks is
  the funding statement's own subject).
* `\paragraph{Use of AI assistance.}` and `\paragraph{Correspondence.}` — sit under
  **Author Contributions**, the CRediT block they extend.

`\section*{End matter}` and its `\addcontentsline` at line 3940 are **kept unchanged**, as a
divider before the six statements. (If a later cycle prefers to drop the divider, deleting those
two lines does not affect any gate; it is not done here because the brief is zero content change.)

### 2.2 `paper/DRAFT-v4.md`

Six replacements. Each anchor is a bold run-in **including its trailing space**, and each occurs
exactly once.

| line (HEAD) | replace this prefix | with |
|---|---|---|
| 3125 | `**Data availability.** ` | `## Data Availability`, blank line, then the body text |
| 3148 | `**Code availability.** ` | `## Code Availability`, blank line, then the body text |
| 3154 | `**Ethics.** ` | `## Ethics`, blank line, then the body text |
| 3161 | `**Competing interests.** ` | `## Competing Interests`, blank line, then the body text |
| 3184 | `**Funding.** ` | `## Funding`, blank line, then the body text |
| 3196 | `**Author contributions.** ` | `## Author Contributions`, blank line, then the body text |

Mechanically: `"**Data availability.** "` → `"## Data Availability\n\n"`, and so on. The
four sub-items keep their bold run-in form, mirroring the `\paragraph{}`s in the `.tex`.
`## End matter` at line 3123 is kept.

---

## 3. G2 + G4 — the abstract, rewritten

### 3.1 What had to happen at once

* **Out:** 255 → `<= 230` words (`text_quality.ABSTRACT_TARGET_WORDS = (120, 230)`), and the
  67-word sentence 6 split (`MAX_ABSTRACT_SENTENCE_WORDS = 62`; also `<= 430` chars, `< 2`
  semicolons, and not `>= 5` numerals together with a semicolon or two clause-dashes).
* **In:** six `se_empirical` abstract obligations that matched nothing — objective / research
  question; study type and named methodology; artifact or subject system; sampling frame and unit
  of analysis; comparison against state-of-the-art; threats / construct validity. (The seventh,
  *Main result with effect size and measurement stability*, already matched and still does.)
* **Kept, non-negotiable:** the scope limits stay **in** the abstract.

Result: **`paper.tex` 215 words, `DRAFT-v4.md` 226 words**, longest sentence 29 words / 192 chars
(`.tex`) and 31 / 196 (`.md`), zero `_abstract_defects` on both, 7/7 abstract obligations on both.
The two counts differ because the markdown spells out the citation and prints `pp` and the en
dash as literal tokens, where the LaTeX hides them inside `\citep{}`, `\pp` and `--`; the two
abstracts are the same text.

Six sentences carry the six new obligations, and each is a **statement of fact about this study**,
not a keyword hung on the text:

| obligation | the sentence that discharges it |
|---|---|
| Objective / engineering question | *"Our research question is whether it survives holding the count fixed."* |
| Study type and named methodology | *"We answer with a benchmarking experiment on the released MetaOptimize artefact…"* |
| Artifact / subject system | *"…the released MetaOptimize artefact, patched only to add partitions."* |
| Sampling frame and unit of analysis | *"The sampling frame is a 2,173-run CIFAR-10/CIFAR-100 corpus; the unit of analysis is a within-batch count-matched contrast."* |
| Comparison against state-of-the-art | *"Against tuned SGD + cosine, the state-of-the-art alternative, the method trails by 1.8–4.2 pp…"* |
| Threats / construct validity | *"…no held-out validation split, bounding construct validity."* |

Three things were **dropped** to pay for them, all of which survive in the body and none of which
is a claim: the `[-55%, +51%] → [-34%, +28%]` interval narrowing (§4.6, §7 T2), the sentence
*"the draw's own variance component is zero"* (§4.6.1), and *"every contrast taken within one
submission, so batch effects cancel"* — the last is now carried by the phrase **within-batch**
in the unit-of-analysis sentence. The replication's power gain is kept in compressed form as
*"at twice the resolution"*, which is the scorer's own T4 receipt (`se 0.0791` vs `0.157`,
ratio `0.50x`). The mechanism sentence keeps its hedge — **"none is a general carrier"**, not
"none survives" — because §5.1 (√N averaging) is *untested, not refuted* and §5.7 (a
size-distribution summary statistic) is *not identifiable from this design*; "none survives"
alone would overstate both.

**One correction lands here and is not cosmetic.** The old abstract attributed all 2,173 runs to
"ResNet-18, ResNet-34 and ResNet-50". The CSV carries 110 `ResNet10` + 9 `ResNet10_c100` +
1 `ResNet101` = **120 rows outside that list**. The new abstract attaches the network list to the
**count-matched cells**, where it is exactly true (18 ResNet-18 cells, 1 ResNet-34, 1 ResNet-50),
and describes the corpus only by its size. See §6 for the interaction with package **S7**.

### 3.2 `paper/paper.tex` — replace lines 64–88

Replace the whole block from `\begin{abstract}` (line 64) to `\end{abstract}` (line 88),
inclusive, with:

```latex
\begin{abstract}
MetaOptimize \citep{sharifnassab2025metaoptimize} meta-learns one step size per parameter group and
reports that finer partitions help inconsistently, never separating that from the group
\emph{count}. Its own contribution therefore remains unmeasured. Our research question is whether
it survives holding the count fixed. We answer with a benchmarking experiment on the released
MetaOptimize artefact, patched only to add partitions. The sampling frame is a 2{,}173-run
CIFAR-10/CIFAR-100 corpus; the unit of analysis is a within-batch count-matched contrast.

The uniform partition wins in all twenty count-matched cells, spanning ResNet-18, ResNet-34 and
ResNet-50. Pooled over eight SGDm cells the effect size is $+0.556 \pm 0.045\pp$, homogeneous
($Q$ 4.21 on 7 df), while cells differing in base optimiser are strongly heterogeneous. Alignment
is a bounded null: at fixed count and size multiset, permuting group membership is worth
$-0.009 \pm 0.157\pp$, and $-0.018 \pm 0.079\pp$ in a pre-registered replication at twice the
resolution. Of nine candidate mechanisms, none is a general carrier.

Threats to validity: the corpus is CIFAR-resolution vision, and a Lion meta-optimiser carries every
count-matched cell but one. Every accuracy is a test-set quantity with no held-out validation
split, bounding construct validity. Against tuned SGD $+$ cosine, the state-of-the-art
alternative, the method trails by 1.8--4.2\pp, dwarfing this ${\approx}0.6\pp$ effect. This should
be read as a constraint on partition design, not as support for practitioners.
\end{abstract}
```

### 3.3 `paper/DRAFT-v4.md` — replace lines 11–30

Replace the abstract body between `## Abstract` (line 9) and the `---` that follows it (line 32) —
i.e. the paragraphs currently on lines 11–30 — with:

```markdown
MetaOptimize (Sharifnassab, Salehkaleybar & Sutton, ICML 2025) meta-learns one step size per
parameter group and reports that finer partitions help inconsistently, never separating that from
the group *count*. Its own contribution therefore remains unmeasured. Our research question is
whether it survives holding the count fixed. We answer with a benchmarking experiment on the
released MetaOptimize artefact, patched only to add partitions. The sampling frame is a 2,173-run
CIFAR-10/CIFAR-100 corpus; the unit of analysis is a within-batch count-matched contrast.

The uniform partition wins in all twenty count-matched cells, spanning ResNet-18, ResNet-34 and
ResNet-50. Pooled over eight SGDm cells the effect size is +0.556 ± 0.045 pp, homogeneous
(Q 4.21 on 7 df), while cells differing in base optimiser are strongly heterogeneous. Alignment
is a bounded null: at fixed count and size multiset, permuting group membership is worth
−0.009 ± 0.157 pp, and −0.018 ± 0.079 pp in a pre-registered replication at twice the resolution.
Of nine candidate mechanisms, none is a general carrier.

Threats to validity: the corpus is CIFAR-resolution vision, and a Lion meta-optimiser carries every
count-matched cell but one. Every accuracy is a test-set quantity with no held-out validation
split, bounding construct validity. Against tuned SGD + cosine, the state-of-the-art
alternative, the method trails by 1.8–4.2 pp, dwarfing this ≈0.6 pp effect. This should be read as
a constraint on partition design, not as support for practitioners.
```

---

## 4. G3 — the workload / task suite, in replicable detail

`reporting_profile` looks for `\bworkload\b|\busage profile\b|\btask suite\b|\bscenario`
anywhere in the manuscript for the obligation *"Workload or usage profile specified in replicable
detail"*. **None of those four words appeared anywhere in `paper.tex`.** Most of the underlying
facts were in the paper, scattered across §3.3, §7 T12 and §8; none of them was ever collected as
a usage profile, and the network census, the batch size, the augmentation transform and the
budget distribution were nowhere at all.

The new block goes at the **top of §3**, between the section head and `\subsection{The
partitions}`, so **no subsection is renumbered** and no `\ref` moves.

### 4.1 `paper/paper.tex` — insert after line 484

Anchor (occurs once):

```latex
\section{Method and experimental setup}
\label{sec:method}
```

Insert, immediately after it (blank line, then the block, then a blank line, then the existing
`\subsection{The partitions}`):

```latex
\paragraph{The workload, and the task suite it runs on.}
Every number in this paper comes from one usage profile, stated here in the detail a replication
needs rather than left to the submission scripts. \textbf{Task suite.} Supervised image
classification on CIFAR-10 and CIFAR-100 \citep{krizhevsky2009cifar} at native $32 \times 32$
resolution, on the shipped 50{,}000/10{,}000 train/test split, with \textbf{no held-out validation
partition anywhere in the project} (\S\ref{sec:metric}, \S\ref{sec:threats} T12). 1{,}967 of the
2{,}173 runs are CIFAR-10 and 206 are CIFAR-100. \textbf{Subject systems.} Networks are
instantiated by the parent release's \texttt{build\_network.py}: ResNet-18 on 1{,}872 rows (1{,}667
CIFAR-10, 188 CIFAR-100, 17 the GroupNorm variant of \S\ref{sec:threats} T7), ResNet-34 on 150,
ResNet-10 on 119, ResNet-50 on 31 and ResNet-101 on 1. Every count-matched cell of
Table~\ref{tab:D} is ResNet-18 (eighteen cells), ResNet-34 (one) or ResNet-50 (one).
\textbf{Training scenario.} Mini-batch size 100 in all 2{,}173 runs; one test-set evaluation after
every training epoch; augmentation is \texttt{RandomCrop(32, padding=4)} followed by a random
horizontal flip (\texttt{patches/patch\_augment.py}), recorded on in 2{,}059 rows, off in 27, and
unrecorded in 87 early rows --- and on in 534 of the 535 partition-family rows, the one exception
carrying no value in that column. \textbf{Budgets.} 100 epochs is the standard workload (1{,}614
runs); the budget ladder of \S\ref{sec:budget} extends it to 300 (62 runs); 392 runs are 20-epoch
probes, and the remaining 105 sit on other budgets (36 at 80 epochs, 30 at 40, 6 at 600 and 33
on 2--5-epoch smoke runs). \textbf{No learning-rate schedule is applied to any MetaOptimize arm}
--- the step size is what the method learns --- and the tuned cosine-schedule baselines of
\S\ref{sec:threats} T4 are the only arms in the corpus that carry one.
\textbf{Execution environment.} One virtual environment on both cluster accounts (Python 3.10.4,
PyTorch 2.0.1+cu118, CUDA 11.8, torchvision 0.15.2, numpy 1.26.4, Slurm) across NVIDIA L4 24 GB,
RTX 2080 Ti 11 GB, A100 80 GB and A100 MIG 40 GB partitions; 1{,}632 GPU-hours over 29 nodes
(\S\ref{sec:repro}).
```

### 4.2 `paper/DRAFT-v4.md` — insert after line 329

Anchor (occurs once):

```markdown
## 3. Method and experimental setup

### 3.1 The partitions
```

Insert the block between the two headings:

```markdown
**The workload, and the task suite it runs on.** Every number in this paper comes from one usage
profile, stated here in the detail a replication needs rather than left to the submission scripts.
**Task suite.** Supervised image classification on CIFAR-10 and CIFAR-100 (Krizhevsky 2009) at
native 32×32 resolution, on the shipped 50,000/10,000 train/test split, with **no held-out
validation partition anywhere in the project** (§3.3, §7 T12). 1,967 of the 2,173 runs are
CIFAR-10 and 206 are CIFAR-100. **Subject systems.** Networks are instantiated by the parent
release's `build_network.py`: ResNet-18 on 1,872 rows (1,667 CIFAR-10, 188 CIFAR-100, 17 the
GroupNorm variant of §7 T7), ResNet-34 on 150, ResNet-10 on 119, ResNet-50 on 31 and ResNet-101
on 1. Every count-matched cell of Table 2 is ResNet-18 (eighteen cells), ResNet-34 (one) or
ResNet-50 (one). **Training scenario.** Mini-batch size 100 in all 2,173 runs; one test-set
evaluation after every training epoch; augmentation is `RandomCrop(32, padding=4)` followed by a
random horizontal flip (`patches/patch_augment.py`), recorded on in 2,059 rows, off in 27, and
unrecorded in 87 early rows — and on in 534 of the 535 partition-family rows, the one exception
carrying no value in that column. **Budgets.** 100 epochs is the standard workload (1,614 runs);
the budget ladder of §4.8 extends it to 300 (62 runs); 392 runs are 20-epoch probes, and the
remaining 105 sit on other budgets (36 at 80 epochs, 30 at 40, 6 at 600 and 33 on 2–5-epoch smoke
runs). **No learning-rate schedule is applied to any MetaOptimize arm** — the step size is what the
method learns — and the tuned cosine-schedule baselines of §7 T4 are the only arms in the corpus
that carry one. **Execution environment.** One virtual environment
on both cluster accounts (Python 3.10.4, PyTorch 2.0.1+cu118, CUDA 11.8, torchvision 0.15.2,
numpy 1.26.4, Slurm) across NVIDIA L4 24 GB, RTX 2080 Ti 11 GB, A100 80 GB and A100 MIG 40 GB
partitions; 1,632 GPU-hours over 29 nodes (§8).
```

---

## 5. G4 (second half) — the Threats section, split into two families

`text_quality._section_defects` fires on any section whose title contains `limitation` or
`threat` unless its body — lower-cased, with `-` replaced by a space, and with LaTeX commands
stripped — contains `included evidence`, `review process` or `process limitation`. The strings
must therefore live in **running prose**: `_strip_latex_commands` deletes a `\subsection{...}`
together with its argument, so a heading alone does not satisfy the checker (this was tested,
not assumed).

The split is substantive, not decorative. **T1–T8 are limits of the included evidence** — what
427 partition-family runs, one meta-optimiser, one image resolution and `n = 3` in fifteen of
twenty cells can and cannot support; only more runs move them. **T9–T12 are limits of the review
process** — the `ar1` exclusion and the `hz3` split (T9), the row filter (T10), the novelty
scoping against CAM-HD / Zheng & Kwok / Choi (T11), and the decision to select on the test set
with no validation split (T12); a reader can re-make every one of those on the deposited run
table without launching a job. Not one T-item is moved, reworded or dropped.

### 5.1 `paper/paper.tex`

**(a)** Insert after the section head (anchor occurs once):

```latex
\section{Threats to validity}
\label{sec:threats}
```

Insert immediately after it:

```latex
We separate two kinds of limit, because they are not answerable by the same means. T1--T8 are
\textbf{limits of the included evidence}: statements about what the runs in this corpus can and
cannot support, which only more runs would move. T9--T12 are \textbf{limits of the review process}:
decisions we made in excluding, filtering, scoring and scoping this audit, which a reader can
re-make on the deposited run table without running anything new. The two lists are kept apart so
that neither reads as a softening of the other.

\subsection{Limits of the included evidence}
\label{sec:threats-evidence}
```

**(b)** Insert before `\paragraph{T9 --- Excluded data, and one batch that is two.}`
(line 3240; anchor occurs once):

```latex
\subsection{Limits of the review process}
\label{sec:threats-process}
```

`\ref{sec:threats}` still resolves to `7`, so every existing `\S\ref{sec:threats} T4`-style
cross-reference is unaffected; the two new labels are spare handles, not required by anything.

### 5.2 `paper/DRAFT-v4.md`

**(a)** Insert after `## 7. Threats to validity` (line 2410) and before `**T1 — Almost one
meta-optimiser.**`:

```markdown
We separate two kinds of limit, because they are not answerable by the same means. T1–T8 are
**limits of the included evidence**: statements about what the runs in this corpus can and cannot
support, which only more runs would move. T9–T12 are **limits of the review process**: decisions we
made in excluding, filtering, scoring and scoping this audit, which a reader can re-make on the
deposited run table without running anything new. The two lists are kept apart so that neither
reads as a softening of the other.

### Limits of the included evidence
```

**(b)** Insert before `**T9 — Excluded data, and one batch that is two.**` (line 2551):

```markdown
### Limits of the review process
```

The markdown headings are **deliberately unnumbered** — see §1: numbering them puts `7.1` and
`7.2` into the census's quantity set.

---

## 6. Every number that changed, and where it was re-derived

Nothing in this package is quoted from the briefing or from the existing prose. Every figure was
re-derived at write time from `results/all_runs.csv` (2,173 rows), from `analysis/c98_figures.py`'s
own `load()/cells()/meta()` (the same functions `c98_reproduce.py` audits with), or from a
registered scorer run **unedited**.

### 6.1 Numbers carried into the new abstract

| number | re-derivation |
|---|---|
| 2,173 runs | `len(list(csv.DictReader(open('results/all_runs.csv'))))` = **2173**. Also `c98_reproduce.py [1] CORPUS`: `rows in results/all_runs.csv 2173 \| paper 2173 \| PASS`. |
| "all twenty count-matched cells" | `cells(adm)` from `c98_figures` returns **20** cells; `sum(1 for c in cs if c['D'] > 0)` = **20**. |
| "spanning ResNet-18, ResNet-34 and ResNet-50" | `Counter((c['network'], c['dataset']) for c in cells(adm))` = `{('ResNet-18','C10'): 16, ('ResNet-18','C100'): 2, ('ResNet-34','C10'): 1, ('ResNet-50','C10'): 1}` — 18 / 1 / 1, no other network. |
| "eight SGDm cells" | `[c for c in cells(adm) if c['in12'] and c['base'] == 'SGDm']` = `cc1, mm1, pp1, gn1 (BN), rl3 @1e-4, rl3 @3e-4, fa1, hz3` → **8**. |
| $+0.556 \pm 0.045$ pp | `meta([(c['D'], c['seD']) for c in those eight])` → **0.5556, se 0.0448**. |
| $Q$ 4.21 on 7 df | same call → **Q 4.2060, df 7, tau 0.0000**. |
| $-0.009 \pm 0.157$ pp | `python3 analysis/c98_reproduce.py` section `[4] THE ALIGNMENT NULL`: `A = permnode − nodewise  -0.009 \| paper -0.009 \| PASS`; `se 0.157 \| paper 0.157 \| PASS`. |
| $-0.018 \pm 0.079$ pp | `python3 analysis/c97_rp1_score.py` (registered, **unedited**, md5 `7d21c4f5c16ccf25196fd6a5e6391fa9`), T1: `A = permnode - nodewise = -0.018 pp (se 0.079, t -0.23 on 5 df, p 0.8248)`. |
| "at twice the resolution" | same scorer, T4: `se(A) here 0.0791 vs pp1's realised 0.157 -> ratio 0.50x; the design promised ~0.09: MET`. |
| 1.8–4.2 pp | §7 T4: ResNet-18 deficit **−1.807** (`c98_reproduce [8]`: `deficit 1.807 \| paper 1.807 \| PASS`), ResNet-34 **−2.558**, ResNet-50 **−4.214**. |
| ≈0.6 pp | the count-matched effect scale: SGDm pool **+0.556**, live 14-cell pool **+0.530** (`c98_reproduce [3]`). Carried unchanged from the previous abstract. |
| "nine candidate mechanisms" | §5's own register (nine subsections, `c98_reproduce` does not assert it). Carried unchanged. |

### 6.2 New numbers introduced by the G3 workload block

All from `results/all_runs.csv` unless noted.

| number | re-derivation |
|---|---|
| 1,967 CIFAR-10 / 206 CIFAR-100 | `Counter(r['dataset'])` = `{'CIFAR10': 1967, 'CIFAR100': 206}`; sums to 2,173. |
| ResNet-18 on 1,872 rows (1,667 + 188 + 17) | `Counter(r['network'])`: `ResNet18` 1667, `ResNet18_c100` 188, `ResNet18_gn` 17. |
| ResNet-34 on 150 | `ResNet34` 141 + `ResNet34_c100` 9. |
| ResNet-10 on 119 | `ResNet10` 110 + `ResNet10_c100` 9. |
| ResNet-50 on 31, ResNet-101 on 1 | `ResNet50` 31, `ResNet101` 1. **1872 + 150 + 119 + 31 + 1 = 2173.** |
| eighteen / one / one count-matched cells | as §6.1 row 3. |
| mini-batch size 100 in all 2,173 runs | `Counter(r['batch_size'])` = `{'100': 2173}` — a single value. |
| augmentation on in 2,059, off in 27, unrecorded in 87 | `Counter(r['augment'])` = `{'1': 2059, '?': 87, '0': 27}`. |
| on in 534 of 535 partition-family rows | rows whose `granularity` is `nodewise`, `nodewise1d`, `chunk*` or `permnode*`: **535**, of which `augment` is `1` in **534** and `?` in **1**. |
| `RandomCrop(32, padding=4)` + horizontal flip | `patches/patch_augment.py:12`: `transforms.RandomCrop(32, padding=4), transforms.RandomHorizontalFlip()`. |
| `build_network.py` | `bin/c52_c100_boxfree.sh:141` — the guard that instantiates the network from the parent release. |
| budgets 1,614 / 62 / 392 / 105 | `Counter(r['epochs_requested'])` = `{100: 1614, 20: 392, 300: 62, 80: 36, 40: 30, 4: 11, 3: 9, 5: 8, 600: 6, 2: 5}`. The "other 105" is spelled out as **36 at 80, 30 at 40, 6 at 600, 33 on 2–5-epoch smoke runs** (11 + 9 + 8 + 5 = 33; 36 + 30 + 6 + 33 = 105). A first draft called the remainder "shorter ladders", which is **false** — six runs are at 600 epochs. Corrected before it was written down. |
| 1,632 GPU-hours over 29 nodes | `c98_reproduce [1] CORPUS`: `GPU-hours 1632 \| paper 1632 \| PASS`; `distinct nodes 29 \| paper 29 \| PASS`. |
| Python 3.10.4 / PyTorch 2.0.1+cu118 / CUDA 11.8 / torchvision 0.15.2 / numpy 1.26.4 | carried verbatim from §8 *Environment*, unchanged. |

### 6.3 One claim I softened before writing it

The draft workload block said the tuned SGD + cosine comparator "is the only arm in the corpus
that carries" a learning-rate schedule. §7 T4 also reports an **AdamW + cosine** baseline on
ResNet-34 and ResNet-50, so that is wrong as written. It ships as *"the tuned cosine-schedule
baselines of §7 T4 are the only arms in the corpus that carry one"*, which is what the paper's
own T4 supports.

---

## 7. Interaction with the other packages in this cycle

* **S7** (abstract's 2,173-run network attribution). This package **already fixes** the abstract
  half of S7: the network list is now attached to the count-matched cells, not to the corpus.
  If S7 also rewrites the abstract, the two edits collide — apply **one** of them, and prefer
  whichever is later in the merge, checking afterwards that `_abstract_defects` is still empty
  and the word count is still `<= 230` (`.tex`) / `<= 230` (`.md`). S7's remaining work is
  outside this package: `paper.tex:114` still says "ResNet-10, -18, -34 and -50 across the
  corpus" and omits the single `ResNet101` row; §4 of this file gives the full census it needs.
* **F2** (§3.4's "216 of the 725 … 29.8%"). This package is **census-neutral** — the patched
  draft yields the same 747 distinct quantity-numerals as HEAD. F2 can derive its number without
  ordering constraints against this package. (Note that `analysis/c98_reproduce.py` was being
  edited concurrently while this package was built — the assertion-site count moved 283 → 353
  and `censuscheck` currently fails 4 checks at HEAD. None of those four failures is caused by,
  or fixed by, this package.)
* **F1, S1–S6, M1, R1.** No overlap. This package touches only the abstract, the head of §3, the
  head and one interior point of §7, and six end-matter headings. It changes no table, no figure,
  no `\ref`, no scorer and no number in §4, §5, §6, §8, §9 or the appendices.

## 8. Application order

Any. All ten anchors are unique verbatim strings; none of the four regions overlaps another
package's region except the abstract (see S7 above).

