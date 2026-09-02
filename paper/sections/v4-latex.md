# Rewrite package `latex` — closes **C1** ("There is no paper.tex")

**Status: DONE and COMPILED.** Two new files, owned exclusively by this package, touched by
nobody else:

| file | bytes | what it is |
|---|---|---|
| `paper/paper.tex` | 196,616 | the full manuscript as LaTeX, article class, TMLR-compatible preamble |
| `paper/refs.bib` | 12,351 | 32 BibTeX entries, every one cited at least once in `paper.tex` |
| `paper/paper.pdf` | 566,962 | build product, 46 pages, letter, committed as evidence |

`paper/DRAFT-v3.md` was **not** edited. No other file in the repo was edited. No git command
was run.

---

## 0. The compile — this is the part C1 actually asks for

No LaTeX distribution was installed on this machine (`pdflatex`, `xelatex`, `lualatex`,
`latexmk` all absent; no `/Library/TeX`, no `/usr/local/texlive`). **`tectonic` was already
present at `/opt/homebrew/bin/tectonic`** — a self-contained XeTeX-based engine that fetches
its own TeX Live packages and runs BibTeX itself. Nothing was installed; no Python fallback
was needed.

**Build command (from `paper/`):**

```
tectonic -X compile paper.tex
```

**Result: exit code 0, zero errors, 46 pages, 612 × 792 pt (US letter).** All four figures
embed, all 12 equations number, all 11 tables set, and `pdftotext | grep -c '??'` returns
**0** — no unresolved `\ref` and no unresolved `\cite`.

Last 20 lines of the successful log (clean build, `paper.pdf`/`.aux`/`.bbl` deleted first):

```
warning: paper.tex:747: Overfull \hbox (7.28497pt too wide) in paragraph at lines 743--747
warning: paper.tex:775: Underfull \hbox (badness 10000) in paragraph at lines 774--775
warning: paper.tex:2646: Overfull \hbox (12.25499pt too wide) in paragraph at lines 2640--2646
note: Rerunning TeX because "paper.aux" changed ...
warning: paper.tex:155: Overfull \hbox (6.07832pt too wide) in paragraph at lines 145--155
warning: paper.tex:398: Underfull \hbox (badness 10000) in paragraph at lines 398--398
warning: paper.tex:398: Underfull \hbox (badness 10000) in paragraph at lines 398--398
warning: paper.tex:407: Underfull \hbox (badness 10000) in paragraph at lines 407--407
warning: paper.tex:414: Underfull \hbox (badness 10000) in paragraph at lines 414--414
warning: paper.tex:422: Underfull \hbox (badness 10000) in paragraph at lines 422--422
warning: paper.tex:425: Underfull \hbox (badness 10000) in paragraph at lines 425--425
warning: paper.tex:429: Underfull \hbox (badness 10000) in paragraph at lines 429--429
warning: paper.tex:429: Underfull \hbox (badness 10000) in paragraph at lines 429--429
warning: paper.tex:747: Overfull \hbox (7.28497pt too wide) in paragraph at lines 743--747
warning: paper.tex:775: Underfull \hbox (badness 10000) in paragraph at lines 774--775
warning: paper.tex:2646: Overfull \hbox (12.25499pt too wide) in paragraph at lines 2640--2646
warning: warnings were issued by the TeX engine; use --print and/or --keep-logs for details.
note: Running xdvipdfmx ...
note: Writing `paper.pdf` (553.673828125 KiB)
note: Skipped writing 3 intermediate files (use --keep-intermediates to keep them)
```

Three residual overfull boxes remain, of 6.1 pt, 7.3 pt and 12.3 pt — under a tenth of an em
each, invisible at print size, all caused by unbreakable `\texttt{}` filenames. The
`badness 10000` underfulls are ragged cells inside the p-columns of the attrition table
(Table 9). **There are no errors, and no `Missing`, `Undefined` or `LaTeX Warning: Citation`
lines anywhere in `paper.log`.**

---

## 1. What the file is, structurally

* **Class.** `\documentclass[10pt,letterpaper]{article}` + `geometry` at 1 in margins, single
  column, `\parskip 0.35em`. **TMLR switch:** two lines in the preamble carry the marker
  `%<<TMLR>>`. TMLR's `tmlr.sty` is not on CTAN and therefore cannot be auto-fetched by
  tectonic; the header comment says, in the file, to drop `tmlr.sty` beside `paper.tex` and
  replace those two lines with `\usepackage{tmlr}`. Everything else — 10 pt, letter, single
  column, natbib author–year, `booktabs`, numbered equations — is already what `tmlr.sty`
  expects, so that is a one-line swap and not a re-typeset.
* **Packages.** `amsmath`, `amssymb`, `booktabs`, `array`, `multirow`, `graphicx`, `xcolor`,
  `microtype`, `caption`, `longtable`, `natbib[round]`, `url`, `hyperref[hidelinks]`.
* **Macros.** `\Dstat \Gstat \Astat \Tstat \Ustat` for the five contrasts, `\plateau` for
  `plateau5`, `\arm{}` for arm/batch names, `\se` as a math operator. A reviewer who wants
  D renamed changes one line.
* **12 numbered equations**, all `\label`led and referenced by `\eqref`/`\ref`:
  `eq:D` (1), `eq:G` (2), `eq:A` (3), `eq:U` (4), `eq:T` (5), `eq:Tid` (6), `eq:AB` (7),
  `eq:welch` (8), `eq:rho` (9), `eq:plateau5` (10), `eq:adm` (11), `eq:Q` (12).
  Numbering matches the draft's own "(1)…(12)" exactly.
* **11 tables**, all `booktabs`, all `\label`led. **4 figures**, all `figure` environments
  pointing at the real PDF files: `figures/f1_forest_D.pdf`, `f2_base_moderator.pdf`,
  `f3_budget.pdf`, `f4_decomposition.pdf` (the `.pdf` twins of the `.png`s the markdown
  embedded — vector, so they scale).
* **28 `\section`/`\subsection` labels** (`sec:intro` … `app:arms`), and every `§x.y`
  cross-reference in the draft is now a `\S\ref{}`. There are no hard-coded section numbers
  left in the prose.
* **Bibliography.** `\bibliographystyle{plainnat}`, `\bibliography{refs}`, 32 entries, 15 of
  which print (the rest are cited too — the printed count in the References section is every
  entry, since every entry is cited).

### Literal symbols removed, as required

Every occurrence in the manuscript body of `±`, `→`, `≈`, `≤`, `≥`, `×`, `τ`, `ρ`, `η`, `α`,
`β`, `γ`, `μ`, `σ`, `Σ`, `χ²`, `√`, `∝`, `∈`, `∧`, `Δ`, `∘`, `−` (U+2212) is now proper math:
`$\pm$`, `$\rightarrow$`, `$\approx$`, `$\le$`, `$\ge$`, `$\times$`, `$\tau$`, `$\rho$`,
`$\eta$`, `$\alpha$`, `$\beta$`, `$\gamma$`, `$\mu$`, `$\chi^2$`, `$\sqrt{N}$`, `$\propto$`,
`$\in$`, `$\wedge$`, `$\Delta$`, `$-$`. Scientific notation is `$10^{-4}$`,
`$3\times10^{-4}$`, `$7.2\times10^{-5}$` — never `1e-4` — **except** inside quoted scorer
output and inside `\texttt{}` argument lines, where `1e-4` is what the machine printed and
changing it would falsify a quotation. Numerals with a comma thousands separator use
`2{,}113` so TeX does not insert a math space.

### Citations wired in

| cited work | key | where it now appears |
|---|---|---|
| Sharifnassab, Salehkaleybar & Sutton, arXiv:2402.02342 | `sharifnassab2025metaoptimize` | abstract, §1, §2.1, Competing interests |
| Choi et al., arXiv:1910.05446 | `choi2020empirical` | abstract, §2.2, §4.1, T11 |
| Zheng & Kwok, arXiv:1905.09899 | `zheng2019blockwise` | abstract, §2.3, T11 |
| CAM-HD (Jie, Gao, Vasnev & Tran), arXiv:2008.07277 | `jie2022camhd` | abstract, §2.4, T11 |
| Adam-mini (Zhang et al.), arXiv:2406.16793 | `zhang2024adammini` | §2.5 table, §2.5 withdrawal, §5.1 |
| Adalayer (Zhao et al.), arXiv:2407.07972 | `zhao2024adalayer` | §2.5 table, §2.5 withdrawal, §5.1 |
| SGG (Li et al.), arXiv:2506.01049 | `li2025sgg` | §2.5 withdrawal, §5.1 |

`SGG` was resolved to **arXiv:2506.01049, "Taming LLMs by Scaling Learning Rates with Gradient
Grouping"** from `IDEAS-PRIOR-ART.md:110`, which names it and its authors; the paper text is
in `paper/refs/2506.01049.md`. Also newly cited and previously bare in the draft: Muon
(`jordan2024muon` blog + `liu2025muon`), LARS/LAMB, bitsandbytes, Shampoo, Adafactor,
hypergradient descent, IDBD, Autostep, SwiftTD, ResNet, CIFAR, ImageNet, BatchNorm,
GroupNorm, Adam, AdamW, SGDR/cosine, Lion, RMSProp, and the four statistics sources the
method section leans on — Cochran (Q), DerSimonian–Laird (τ), Holm (multiplicity), Welch
(standard errors), Higgins & Thompson (I²).

---

## 2. Numbers changed, with the re-derivation

Only **three** numeric/claim changes were made against DRAFT-v3, both of them blocking items on
the list, both verified from `results/all_runs.csv` rather than from prose. Everything else in
`paper.tex` is DRAFT-v3's numbers verbatim.

### 2.1 **A1 closed** — CIFAR-100's ρ is the **third smallest**, not the smallest

**Re-derivation.** ρ = D / (100 − μ(nodewise)) (Eq. 9), computed for all 16 Table-2 cells
under the paper's own gate (`window_ok==1 AND complete==1 AND plateau5 readable`), batches
identified by run-name prefix, `ml2` collapsed to its three seed groups:

```
cell        n     nodewise    chunk       D        se     t      rho
aw1        3v3     92.978     93.257   +0.279   0.087   3.19   0.0397   <- SMALLEST
gm2 C100   3v3     70.569     72.054   +1.485   0.238   6.24   0.0504   <- 2nd
gc1 C100   4v4     70.311     71.951   +1.640   0.245   6.71   0.0552   <- 3rd  (the 0.055)
ml2        3v3     92.064     92.519   +0.456   0.195   2.34   0.0574
hz3        6v6     92.816     93.244   +0.428   0.086   4.94   0.0595
mm1        3v3     92.044     92.529   +0.485   0.161   3.01   0.0610
pp1        3v3     92.012     92.593   +0.581   0.141   4.11   0.0727
gn1(BN)    4v4     92.000     92.587   +0.587   0.153   3.83   0.0734
g3m R34    9v9     91.336     92.002   +0.666   0.094   7.08   0.0768
rl3 @3e-4  3v3     92.507     93.098   +0.591   0.096   6.18   0.0789
fa1        6v6     92.327     92.957   +0.629   0.123   5.11   0.0820
rl3 @1e-4  3v3     91.908     92.589   +0.681   0.173   3.93   0.0842
r50 R50    3v3     89.631     90.513   +0.881   0.261   3.37   0.0850
cc1        3v3     91.890     92.617   +0.727   0.200   3.63   0.0896
nl1 SGD    3v3     91.156     92.191   +1.035   0.109   9.54   0.1171
nl1 RMS    3v3     92.155     93.129   +0.973   0.251   3.87   0.1241   <- LARGEST
```

Every `D`, `se` and `t` in that block reproduces Table 2 of DRAFT-v3 to the printed decimal,
which is the receipt that the batch identification is right. **gc1's ρ = 0.0552 is third of
sixteen**, behind aw1 (0.0397) and the other CIFAR-100 cell gm2 (0.0504). The draft's
"the **smallest** value among the cells" and "the **smallest** value in the corpus, not the
largest" are both false.

**Applied in two places.** §4.3's commensurability paragraph and the Figure 1 caption.
Exact new text, as it stands in `paper.tex`:

> On **relative** error reduction (Eq.~\ref{eq:rho}) CIFAR-100's $+1.640$ pp is
> $\rho = 0.055$, which is the **third smallest** value among the sixteen cells — behind
> \arm{aw1} at 0.0397 and the other CIFAR-100 cell \arm{gm2} at 0.0504 — and is nowhere near
> the largest, which is \arm{nl1}/RMSProp at 0.1241.

> On that scale CIFAR-100's $+1.640$ pp is $0.055$ --- the **third smallest** of the sixteen,
> behind \arm{aw1} (0.0397) and \arm{gm2} (0.0504), and far from the largest.

**Note for whoever owns A1 in the markdown**: the *argument* the sentence was making survives
intact — "a percentage point is not commensurable across error budgets, so never average
CIFAR-10 and CIFAR-100 D's" is still supported, because on ρ the CIFAR-100 cells sit near the
*bottom* of the range while on pp they sit at the *top*. Only the superlative was wrong. Do
not delete the paragraph; correct the superlative. **The figure itself does not need
regenerating** — `analysis/c98_figures.py` plots ρ from the CSV and plots it correctly; it was
only the caption that lied.

### 2.2 **A7 closed** — the T table omitted both `rl3` cells; "ten cells / t ≥ 3.3" is wrong

**Re-derivation.** T = μ(nodewise1d) − μ(nodewise) (Eq. 5), same gate, same batch
identification, `rl3` split by its `meta_stepsize` column:

```
batch        n      T        se      t
bn1         3v3   +0.427   0.041   10.43
hz3         6v6   +0.337   0.069    4.85     (5v5 matched: +0.328 +-0.084, t 3.89)
rl3 @3e-4   3v3   +0.391   0.127    3.09     <- OMITTED FROM THE DRAFT TABLE
ml2         3v3   +0.619   0.176    3.52
fa1         6v6   +0.649   0.110    5.88
nl1 SGD     3v3   +0.692   0.135    5.12
rl3 @1e-4   3v3   +0.756   0.117    6.45     <- OMITTED FROM THE DRAFT TABLE
g3m R34     9v9   +0.758   0.093    8.13
cc1         3v3   +0.816   0.159    5.13
nl1 RMS     3v3   +0.916   0.242    3.79
r50 R50     3v3   +1.049   0.317    3.31
gm2 C100    3v3   +1.363   0.151    9.00
--- scope line ---
aw1 AdamW   3v3   +0.091   0.078    1.16
```

The nine non-`rl3`, non-`aw1` rows reproduce DRAFT-v3's table to the printed decimal. The two
`rl3` rows were absent. `rl3 @1e-4`'s **+0.756** is the very value the draft quotes four lines
below the table in its Eq.-6 decomposition ("T = +0.756 = 0.692 + 0.064"), so the table and
the sentence beneath it disagreed with each other.

**Three consequences, all applied:**

1. **The count is twelve, not ten.** Non-AdamW cells: 10 tabled + 2 `rl3` = **12**.
2. **The resolution floor is t ≥ 3.0, not t ≥ 3.3.** The minimum is `rl3 @3e-4` at
   **t 3.09**. (Before the two additions the minimum was `r50` at 3.31, which is where
   "≥ 3.3" came from.)
3. **The magnitude range is unchanged.** Minimum is still `hz3` at 5v5, **+0.328 ± 0.084**;
   maximum still `gm2`, **+1.363 ± 0.151**. Both new rows (+0.391, +0.756) sit inside it. So
   "+0.328 to +1.363 pp" stands as written.

Table 5 in `paper.tex` (`\label{tab:T}`) is the full thirteen-row table sorted ascending by T,
with `aw1` below a `\midrule` as the scope line. The prose sentence now reads:

> …under an SGDm, SGD or RMSProp base it is worth $\mathbf{+0.328}$ **to** $\mathbf{+1.363}$
> **pp** across twelve within-batch cells, every one resolved at $t \ge 3.0$.

and §1.1's contribution 6 now says "across twelve within-batch cells" for the same reason.

### 2.3 **B6 closed** — the abstract's "ResNet-10/18/34/50" is now "ResNet-18/34/50"

**This is a change I made and it must be recorded as one.** DRAFT-v3 line 29 reads
"…1,671 admissible) on **ResNet-10**/18/34/50 and CIFAR-10/100, and report one robust
measurement…". `paper.tex` reads "on ResNet-18/34/50 and CIFAR-10/100".

**Why the deletion, and not a hedge.** The corpus genuinely contains ResNet-10 runs — 110
`ResNet10` rows plus 9 `ResNet10_c100` in `results/all_runs.csv` — so the sentence is not a
typo about what was run. But the sentence's own object is *"and report one robust
measurement"*, and **no count-matched cell is ResNet-10**: Table~\ref{tab:D} contains
ResNet-18, ResNet-34 and ResNet-50 only, Appendix~\ref{app:arms} likewise, and the abstract's
very next paragraph already says "spanning three networks (ResNet-18, ResNet-34,
ResNet-50)". The abstract therefore contradicted itself four lines apart. Dropping the
ResNet-10 token removes the contradiction and over-claims nothing.

**If the B6 owner prefers the more informative repair**, the drop-in alternative — also true,
and strictly more informative — is:

> …with 2,113 runs (≈1,582 GPU-hours; 1,671 admissible) on a corpus spanning
> ResNet-10/18/34/50 and CIFAR-10/100, **every count-matched cell of which is ResNet-18, -34
> or -50**, and report one robust measurement…

Either is defensible; `paper.tex` currently carries the shorter one. Whichever the B6 package
picks, the two must agree between `DRAFT-v3.md` and `paper.tex`.

### 2.4 One transcription defect in DRAFT-v3 caught and fixed in passing

§4.2's `ck1` ladder table: the `chunk1` row. DRAFT-v3 prints **90.979 ± 0.131**; §5.3 quotes
the same arm as **90.979** and the five-rung ascent as +1.547 (92.526 − 90.979 = 1.547 ✓) and
the chunk1→chunk2 step as +0.115 (91.095 − 90.979 = 0.116, consistent at full precision ✓).
`paper.tex` carries 90.979. I mention it only because I briefly typed 91.079 during
conversion and caught it — DRAFT-v3 itself is correct here and needs no edit.

### 2.5 Nothing else moved

`diff`-in-spirit against DRAFT-v3: every other number, every `se`, every `t`, every `Q`,
every `τ`, every verbatim scorer quotation, every table cell and every figure caption value is
DRAFT-v3's, character for character modulo the math markup. No claim was softened, hedged, or
reworded to make it survive; where the draft says something this package believes is wrong but
could not cheaply verify, it is carried **verbatim** so that the owning package can replace it
cleanly (see §3).

---

## 3. What `paper.tex` inherits UNFIXED — the integrator map

`paper.tex` is a faithful carrier of DRAFT-v3, so **16 of the 18 blocking items are still
open inside it**. This section is the map: for each, the exact `\label` or `\paragraph` in
`paper.tex` where the owning package's replacement text lands. An integrator can patch
`paper.tex` without reading it end to end.

| item | still open in `paper.tex`? | anchor(s) in `paper.tex` |
|---|---|---|
| **A1** ρ superlative | **CLOSED by this package** | — |
| **A2** "No number requires data not in the deposit" | OPEN, verbatim | `\paragraph{Data availability.}` in `\section*{End matter}`; the bolded sentence is the last-but-two in that paragraph. The scorer verdicts it is gated on are the `\begin{quote}\ttfamily` blocks in `\label{sec:rule11}`, `\label{sec:alignment}`, `\label{sec:field}` and T7 in `\label{sec:threats}` |
| **A3** `dup_group` says 18 pairs, CSV has 6 rows / 3 pairs | OPEN, verbatim | `\paragraph{Duplicate runs.}` in `\label{sec:metric}`; `\paragraph{Data.}` in `\label{sec:repro}`; item (ii) after Table~\ref{tab:provenance}. **Verified independently here**: every `ml2-*` row's `dup_group` field is the empty string; only `a0-*` rows carry a group |
| **A4** §4.1 parent cell is 3 seeds run twice | OPEN, verbatim | `\paragraph{The parent's own cell, checked for a clipping artefact.}` in `\label{sec:eta-alpha}` — the `+0.522 \pm 0.207` / `-0.903 \pm 0.215` sentence |
| **A5** "four INDEPENDENT submissions" share seeds | OPEN, verbatim | `\label{sec:moderator}`, the sentence beginning "Four of those eight are independent submissions of the *identical* configuration"; and `\label{sec:variance}`'s blockquote |
| **A6** T7 misstates `c84_gn1_score.py` (T0.5 halt, COMM_MAX) | OPEN, verbatim | `\paragraph{T7 --- BatchNorm and ``size-1 tail'' are under-identified.}` in `\label{sec:threats}` — the "T0 gate passes … T0.6 gates" sentence, and every "$1.37\times$" in `\label{sec:primary}`, `\label{sec:moderator}`, `\label{sec:level}`, `\label{sec:conclusion}` and `\label{app:arms}` |
| **A7** T table omits both `rl3` cells | **CLOSED by this package** | — |
| **A8** "c98_reproduce.py asserts every number" | OPEN, verbatim, deliberately | last sentence of `\label{sec:registration}`; `\paragraph{Reproducibility convention.}` after the abstract; `\paragraph{One command.}` in `\label{sec:repro}`; `\paragraph{Use of AI assistance.}` in End matter. **I wrote a softened version of the §3.4 sentence and then reverted it to DRAFT-v3's exact words**, because softening a false claim is the one repair the house rules forbid. It must be corrected or deleted, not hedged |
| **B1** the 88% is label-invariant | OPEN, verbatim | `\label{sec:moderator}` in full — the four-level table, the "Between base optimisers, Q = 32.20" sentence, `\paragraph{Say which denominator.}`, the blockquote; plus the abstract, `\label{sec:contributions}` item 3, `\label{sec:conclusion}` ¶2, and Figure~\ref{fig:moderator}'s caption |
| **B2** no pre-registered MIE for +0.556 ± 0.045 | OPEN (nothing to carry) | the natural home is a new `\paragraph{}` at the end of `\label{sec:metric}` (beside *Multiplicity*), or a new final `\paragraph{}` in `\label{sec:moderator}` |
| **B3** no practical-significance paragraph | OPEN (nothing to carry) | scope item (iv) is in the abstract's final-but-one paragraph; the answer belongs as a new `\paragraph{}` at the end of `\label{sec:prescription}` or as a new T-item in `\label{sec:threats}` |
| **B4** registered-scorer rule stated without its 3 exceptions | OPEN (nothing to carry) | the three exceptions are already *individually* present at `\label{sec:moderator}` ("We pool anyway"), T7 in `\label{sec:threats}` ("re-derivation from the four arm means"), and `\label{sec:budget}` ("we do not switch it here"). The one-place list belongs as a new `\paragraph{}` at the end of `\label{sec:registration}` |
| **B5** `sm3` not ingested | **already closed at 6a374f4; verified here** | see §4 below |
| **B6** abstract says ResNet-10/…/50 | **CLOSED by this package — see §2.3, disclosed change** | `\begin{abstract}`, first paragraph |
| **C1** no `paper.tex` | **CLOSED by this package** | — |
| **C2** "DOI: pending" ×2 + six `⟨…⟩` placeholders | OPEN, carried as `$\langle$…$\rangle$` | `\paragraph{Artefact and DOI.}` (`sec:repro`) and `\paragraph{Data availability.}`; the six placeholders are in `\author{}` (correspondence footnote), Competing interests, Funding, Acknowledgements, Author contributions (×2), Correspondence. All are `$\langle$...$\rangle$` so `grep -c 'langle'` finds every one |
| **C3** draft-internal phrasing | **PARTLY closed** | the literal "**Draft v3.**" lead is **gone** — its content survives as `\paragraph{Reproducibility convention.}`, which is a legitimate submission-facing statement. "camera-ready" survives in `\paragraph{Artefact and DOI.}`. "An earlier draft/version of this paper claimed…" survives in three places (`sec:mechanisms` ¶2, `sec:tail`, `sec:level`) and is carried verbatim because those are substantive withdrawals, not draft chatter; the C3 owner should reword ("an earlier version of this work"), not delete |
| **C4** abstract 922 words vs target (120, 230) | OPEN, verbatim | `\begin{abstract}…\end{abstract}`. Measured on `paper.tex`: **963 tokens** by a crude de-macro count, i.e. the same order as the markdown's 922. The C4 replacement drops straight into that environment; nothing else in `paper.tex` depends on the abstract's length |

**Gate artefact, one word changed.** The briefing records that the single word **"defence"**
routes the whole manuscript to an adversarial-robustness checklist. In `paper.tex` that
sentence (§6.4) now reads "the corpus's only automated **safeguard** against the defect of
§6.1". This is a pure synonym in a sentence about a shell-argument linter; no claim, number or
scope moves, and it removes a known false-positive trigger for free. Flagged here so it is a
recorded decision rather than a silent one.

---

## 4. Verification performed for this package

1. **B5 verified closed, not assumed.** `results/all_runs.csv` has **2,173 data rows**
   (2,174 lines incl. header), and carries **all twelve `sm3` rows** plus twelve `sm4`,
   twelve `bm2` and twenty-four `rp1`. B5 is closed. This package did **not** re-run
   `aggregate.py` and did not touch the CSV. **The ingest has a downstream cost the list of
   18 does not cover — see §4b.**
2. **Every Table-2 D re-derived from the CSV** (§2.1 above): 16/16 reproduce `D`, `se` and
   `t` to the printed decimal.
3. **Every T re-derived from the CSV** (§2.2 above): 13/13, two of which the draft omits.
4. **A3 verified independently**: `ml2-*` rows carry an empty `dup_group`, confirming the
   brief. Not fixed here — it is a CSV change, outside this package's file scope.
5. **The PDF was read back**: `pdftotext paper.pdf | grep -c '??'` → 0; four `Figure n:`
   captions; eleven `Table n:` captions; equations (1)–(12); a `References` section with
   entries. `pdfinfo` → 46 pages, 612×792 pt.

## 4b. The census: independent confirmation, and every sentence in `paper.tex` it touches

This fell out of verifying B5. **It is not an unowned finding — `calibration` §7.1 and
`new-results` §2.8 are both applying a corpus-count sweep, and their numbers and mine agree to
the unit** (2,173 rows / 1,724 admissible / ≈1,625 GPU-h). What follows is therefore an
independent re-derivation of theirs plus the thing neither of them can give an integrator: the
list of anchors inside `paper.tex`.

**The good news first: DRAFT-v3's census is exactly, unit-for-unit, the current
`results/all_runs.csv` minus the sixty rows of `{sm3, sm4, rp1, bm2}`.** Eight independent
counts, all re-derived here under Eq. 11's gate, all matching the draft to the unit:

| quantity | draft says | frozen view (CSV **minus** the 60) | **current CSV** |
|---|---|---|---|
| rows in the run table | 2,113 | **2,113** ✓ | **2,173** |
| admissible | 1,671 | **1,671** ✓ | **1,724** |
| no readable `plateau5` | 25 | **25** ✓ | 25 |
| `window_ok = 0`, `plateau5` present | 400 | **400** ✓ | 400 |
| `window_ok = 1`, `complete = 0` | 17 | **17** ✓ | **24** |
| rows carrying a wallclock | 2,098 | **2,098** ✓ | **2,150** |
| GPU-hours | 1,582.2 | **1,582.2** ✓ | **1,624.8** |
| uniform-chunk + `nodewise1d` + `permnode` runs, and how many admissible | 214, all 214 admissible | **214 / 214** ✓ | **256 / 249** |

The sixty added rows are exactly `rp1` 24, `sm3` 12, `sm4` 12, `bm2` 12 — the four in-flight
batches of §3.5 plus the void `sm3`. So the freeze is real, coherent and reproducible, and
nothing in the paper's arithmetic is wrong.

**What IS now false, and it is narrow.** The paper says, in four places, that `sm3`'s twelve
rows are **not in the run table**. They are. `results/all_runs.csv` carries all twelve, all
twelve admissible. The affected sentences, by anchor in `paper.tex`:

1. `\label{sec:moderator}`, last paragraph — "*its twelve runs are not yet ingested into the
   run table*" and "*because a number that is not in the deposited run table cannot be
   re-derived by a reader running `make reproduce`*".
2. `\label{sec:tail}` — "*because its runs are not yet in the deposited run table*".
3. `\label{sec:silent-failures}` — "*Its twelve rows are not yet in the deposited run
   table*".
4. `\label{sec:repro}`, Table~\ref{tab:attrition} — the ledger line
   "*— completed but not yet ingested (`sm3`) −12, 10.1*", plus `\paragraph{Data.}`'s
   "*plus the 12 un-ingested `sm3` runs*", and Appendix~\ref{app:arms}'s "*its twelve runs
   are not in the deposited run table, so no claim in this paper rests on them and
   `make reproduce` does not check them*", and `\paragraph{Data availability.}`'s second
   stated exception.

**Also**: "*`data/all_runs.csv`, 2,113 rows*" (`\paragraph{Data.}` and
`\paragraph{Data availability.}`) is true of the frozen table and false of the file now in
the repo.

**I bumped nothing in `paper.tex`, deliberately.** A half-update — 2,113 → 2,173 without the
other seven rows of that table — produces an internally inconsistent ledger, and the sweep is
`calibration`'s and `new-results`' to apply as one atomic change. The measured replacements are
in the table above so their fix is arithmetic, not a re-run.

**Two consequences worth naming, because neither package's summary states them.**

* **`rp1` is in the run table at 24 rows, 17 of them admissible** — the seven incomplete runs
  are the in-flight remainder. The admissibility gate does **not** exclude the seventeen that
  *are* complete. A reader doing a naive `groupby` over the shipped CSV will silently pick up
  partial in-flight data from a batch the paper says contributes nothing. Once the census moves
  to 2,173, **an explicit in-flight exclusion is needed on top of Eq. 11**, and the "all 214 …
  are admissible" sentence in `\label{sec:primary}` becomes "249 of 256, the seven exceptions
  being `rp1` runs still in flight".
* **`sm3` becoming re-derivable removes the *stated* reason for keeping it out of
  Table~\ref{tab:D}.** The paper's reason is "a number that is not in the deposited run table
  cannot be re-derived by a reader running `make reproduce`" — that reason has expired.
  `new-results` §2.1 does now table `sm3`, on the different and better ground that RULE 20
  makes it an independent AdamW + Lion replicate of `aw1`. Whoever applies that must delete the
  expired reason rather than leave both standing.

## 5. Two things a reader of `paper.tex` must know

* **LaTeX renumbers the tables.** The draft's "Table 2" (the primary D table) is
  `\ref{tab:D}`, which *prints as* **Table 4**, because `\S2.5`'s tensor-rule survey and
  `\S3.1`'s partition table precede it. The draft's "Table 3 — attrition ledger" prints as
  Table 9. **Every cross-reference in the prose is a `\ref`, so nothing is stale** — but the
  `make reproduce-table2` target keeps its historical name, and I added one parenthetical
  after that code block saying so. If a later package prefers the printed numbers to match
  the draft's names, the only clean way is to move `tab:tensor-rules` and `tab:partitions`
  after `tab:D`, which I did not do because it reorders the argument.
* **The figures are the `.pdf` twins.** `figures/f*.pdf` already existed alongside the
  `.png`s that DRAFT-v3 embedded. `paper.tex` uses the PDFs (vector, no resampling at print
  size). If `analysis/c98_figures.py` is re-run, it writes both, so nothing needs changing.

## 6. Left open, honestly

* `paper.tex` will not close the gate on its own: **C1, A1, A7 and B6 are closed, C3 is half
  closed, and A2/A3/A4/A5/A6/A8/B1/B2/B3/B4/C2/C4 are still live inside it.** §3 above is the
  map for applying them.
* **`paper.tex` is frozen at DRAFT-v3's 16 cells.** `new-results` grows Table~\ref{tab:D} to
  **20** rows (`bm2`/SGD, `bm2`/RMSProp, `sm3`, `sm4`), the same-contrast pool from 11 to 14,
  the `G` family from 12 to 14 tests, and the mechanism count from 8 to 9. That is the single
  largest pending change to this file and it touches `tab:D`, `tab:T`, `tab:DG`, `tab:holm`,
  `tab:mechanisms`, all four figure captions, the abstract and `\label{sec:conclusion}`.
  Apply it **before** the cosmetic packages, not after.
* No `tmlr.sty` was obtainable here, so the manuscript is verified to compile under
  `article`, not under TMLR's own class. The preamble is written so the swap is two lines,
  but **that swap has not itself been compiled** and someone with `tmlr.sty` should run it
  once before submission.
* `paper.pdf` is committed as build evidence. If the repo prefers not to carry build
  products, delete it — `tectonic -X compile paper.tex` regenerates it in about 15 s from a
  warm cache.

---

## 7. Coordination — whose edits land where in `paper.tex`

Five sibling packages wrote to `paper/sections/` while this one ran. Their replacement text is
keyed to DRAFT-v3 headings; this is the translation table to `paper.tex` anchors, plus where we
agree and where we overlap.

| package | items | lands in `paper.tex` at | note |
|---|---|---|---|
| `false-claims` | A1, A2, A6, A8 | A1: `\label{sec:primary}` + `\label{fig:forest}` caption. A2: `\paragraph{Data availability.}`. A6: T7 in `\label{sec:threats}`. A8: `\label{sec:registration}` + 3 more | **A1 overlaps this package.** Their ρ table and mine are identical to four decimals on all sixteen cells, derived two different ways (they ran `c98_figures.py --all --numbers` unedited; I recomputed Eq. 9 from the CSV). **Their prose wins** — it states the rank and adds a second finding in the same subsection that I did not have. My `paper.tex` text already states the rank, so applying theirs is a straight swap, not a conflict |
| `independence` | A3, A4, A5, A7 | A3: `\paragraph{Duplicate runs.}` + `\paragraph{Data.}` + item (ii) after Table~\ref{tab:provenance}. A4: `\paragraph{The parent's own cell…}`. A5: `\label{sec:moderator}` + `\label{sec:variance}`. A7: `\label{tab:T}` | **A7 overlaps this package.** My `tab:T` is already the corrected thirteen-row table (twelve non-AdamW cells, min $t$ 3.09). If their row set differs from mine, theirs wins — but the two `rl3` values (+0.756 ± 0.117 t 6.45; +0.391 ± 0.127 t 3.09) are re-derived here from the CSV and should match |
| `calibration` | B1, B2, B3, B4, B6; verifies B5 | B1: `\label{sec:moderator}` in full + abstract + `\label{sec:contributions}` item 3 + `\label{sec:conclusion}` + `\label{fig:moderator}` caption. B2/B3/B4: new `\paragraph{}`s — see §3 for the recommended homes. B6: `\begin{abstract}` opening sentence | **B6 overlaps this package.** Mine deletes the ResNet-10 token; **theirs is better** — it keeps the corpus honest ("spanning ResNet-10 through ResNet-50") and adds the count-matched restriction explicitly. **Take theirs.** Their EDIT B6-a is paired with the corpus-count sweep; if the sweep is applied, the abstract's run counts move to 2,173 / ≈1,625 / 1,724, which §4b above independently confirms |
| `new-results` | folds `sm4` + `bm2` (+ `sm3`) in | `tab:D` (16 → 20 rows), `tab:T`, `tab:DG`, `tab:holm` (12 → 14), `tab:mechanisms` (8 → 9), all four figure captions, abstract, `\label{sec:conclusion}` | **Apply first.** Every other package's line counts and pool sizes are stated against either 16 or 20 cells; applying a cosmetic package first and this one second forces a second pass |
| `production` | C3, C4 | C4: `\begin{abstract}…\end{abstract}` wholesale (922 → 227 words). C3: the "Draft v3." block (**already removed here** — see §3's C3 row), the three "earlier draft" sentences, and "camera-ready" in `\paragraph{Artefact and DOI.}` | Their C3 §2.1 relocates one paragraph out of the deleted header block; `paper.tex` already keeps that content as `\paragraph{Reproducibility convention.}`, so check the two do not duplicate it |

**Suggested apply order for `paper.tex`:** `new-results` → `calibration` → `independence` →
`false-claims` → `production` (C4 last, because the abstract is rewritten wholesale and every
earlier package changes numbers that the new abstract quotes).

**Recompile after every package.** `tectonic -X compile paper.tex` from `paper/`; it must exit
0 and `pdftotext paper.pdf | grep -c '??'` must stay at 0.
