# v11-signposting — Plan C, executed as text: an evidence map plus per-section pointers

**Scope.** Task 1 (Plan C signposting) only. This file contains finished replacement text and
EXACT replacement blocks. It edits neither `paper/paper.tex` nor `paper/DRAFT-v4.md`; a later
agent integrates. Every anchor below was verified `count == 1` against the live files at HEAD
`58c0c85`. Every structural number in this file was measured by a command recorded in §0;
nothing is quoted from a briefing, from `docs/STATUS.md`, or from `paper/sections/v9-plan.md`.

---

## 0. Commands run, and what they returned

```
git log --oneline -1                      -> 58c0c85 ; working tree clean
python3 analysis/c98_reproduce.py         -> ALL 636 CHECKS PASS
                                             census 628 / 411 / 982 / 41.9%
                                             (n_tok 2995, n_dis 997, n_q 2614)
python3 analysis/paper_numeric_diff.py    -> tex 2604 (994 distinct)
                                             md  2606 (994 distinct)
                                             3 tex-only, 5 md-only = 8 residuals, exit 1
```

Section word counts re-measured directly from `paper/DRAFT-v4.md` (own script, headings
`^#{2,4} `, words between one heading and the next):

| unit | words | unit | words |
|---|---|---|---|
| §1 Introduction | 1,838 | §4.7 | 2,430 |
| §1.1 Contributions | 999 | §4.8 | 2,916 |
| §3.3 | 2,645 | §5.4 | 2,745 |
| §3.4 | 1,306 | §7 *Limits of the included evidence* | 1,853 |
| §3.5 | 2,753 | §7 *Limits of the review process* | 2,411 |
| §4.3 | 1,906 | §8 | 3,139 |
| §4.4 | **6,324** | Appendix A | 1,833 |

This differs from `v9-plan.md`'s opener list in two places and I follow my own measurement:
`v9-plan.md` names §4.6 (measured **893** w) and §3.4 (**1,306** w) as long units and omits
§4.7 (**2,430** w) and §4.8 (**2,916** w). Openers below go on the ten largest units a referee
may legitimately triage.

---

## 1. VERDICT and what this package is

**Plan C, executed.** Nothing moves, nothing is renumbered, no `\label` or `\ref` changes, no
existing sentence is rewritten. Three elements are **added**:

| element | where | size |
|---|---|---|
| **§1.2 "Reader's guide and evidence map"** — lead, ten-row evidence map, closing caveat | after §1.1, before §2 | 494 words |
| **Ten one-shot section openers**, italic, fixed format | heads of §3.3, §3.4, §3.5, §4.4, §4.4's endpoint block, §4.7, §5.4, §7 *evidence*, §7 *process*, §8 | 426 words |
| **One forward pointer** to §1.2 | §1's closing sentence | 12 words |
| | **total** | **932 words** |

**The 932 is measured, and it is not the ~500 the briefing quotes.** `v9-plan.md` §7's Plan C
table says "≈ 500 words"; its own §8 specification asks for a **one-page** §1.2 (its own
measurement is 691 words/page) *plus* eight-to-nine openers *plus* per-contribution pointers.
The 500 was inconsistent with the spec it sat next to. I implemented the spec, dropped the one
element that turned out to be redundant (below), and report the measured total.

### Two deliberate deviations from `v9-plan.md` §8, with reasons

1. **No per-contribution pointers (its §8.3).** Re-read at HEAD, **all seven** items of §1.1
   already end in a bracket naming their sections and floats — item 1 `(§4.3–§4.5, Table 2,
   Figure 1 … §4.4)`, item 2 `(§4.6, §4.6.1)`, item 3 `(§4.4, Figure 2)`, item 4 `(§4.1–§4.2)`,
   item 5 `(§5 … §5.5, M9)`, item 6 `(§4.7, §5.4, §5.5)`, item 7 `(§6, Appendix A)`. The
   one-step property the plan wanted to buy there **already holds**. What §1.1 does *not* give
   is the route from a claim to the *script section* and the *deposit command* that re-derive it,
   and that is what the map supplies. Editing the most number-dense list in the paper to restate
   pointers it already carries is pure downside.
2. **A different opener set, from my own measurement.** `v9-plan.md` names §3.3, §3.4, §3.5,
   §4.4, §4.6, §5.4, §7.2, §8. My own count (§0) puts **§4.6 at 893 words** and omits **§4.7 at
   2,430** and **§4.8 at 2,916**. I dropped §4.6, added §4.7, and deliberately did **not** open
   §4.8: an opener's job is to license triage, and §4.8 is one of the four things a referee must
   not skip, so it is named in §1.2's load-bearing list instead. §4.3 is excluded for the same
   reason. Result: openers on the ten largest units a referee may legitimately triage.

### Why this passes the functional test

The test is that a referee reaches any claim's supporting evidence in **one step**. Three routes
now exist and each is one hop:

* from **§1.1** to the section and float — already true, unchanged;
* from **§1.2's map** to the section, the float, the audit section that re-derives the number,
  and the `make` target that re-runs it — new, and the only route to the last two;
* from a **section head** to "is this the section I want" — new, and the only route that answers
  it without reading the section.

---

## 2. Verification — run against the patched pair, not asserted

The full package was applied to **copies** of both markups and every registered check re-run
against the copies. `paper/paper.tex` and `paper/DRAFT-v4.md` in the repo were never touched.

| check | before | after the package | verdict |
|---|---|---|---|
| `c98_reproduce.py` | ALL 636 CHECKS PASS | **ALL 636 CHECKS PASS** | green |
| census triple | 628 / 411 / **982** / **41.9%** | 628 / 411 / **982** / **41.9%** | **fixpoint held, nothing to rewrite** |
| census internals | n_tok 2995, n_dis 997, n_q 2614 | n_tok 3026, n_dis 997, n_q **2615** | see note |
| new distinct quantity numerals | — | **none** (empty set, both directions) | green |
| `paper_numeric_diff.py` | tex 2604 (994 d) / md 2606 (994 d); 3 tex-only, 5 md-only | **byte-identical on all six figures**; same 8 residuals, same multiplicities | **exactly neutral** |
| `xref_check.py` | PASS, 545 refs, 8 allowlisted | **PASS**, 596 refs, 8 allowlisted, 0 unresolved, 0 stale | green **after the §4 edit** |
| `test_fence_mask.py` invariant | masks identical | masks identical (2,419 chars, 0.77% of draft) | green |
| CORRECTIONS-138 pipe guard `grep -nE '^\|(r\|Δ\|ρ\|t\|D)\|'` | nothing | nothing | green |
| `tectonic -X compile` | exit 0 | **exit 0**, 0 undefined, 0 `??` | green |
| distinct overfull hboxes | 2 — 7.28497pt, 12.25499pt | **2 — 7.28497pt, 12.25499pt** (identical) | green, no third |
| distinct underfull sites | 16 | **16** | green |
| **page count** | **75** | **76** | **+1 page — see below** |
| abstract | untouched | untouched | n/a |

**The one number that moves in the census is `n_q`, +1, and no check asserts it.** The `+1` is
the Markdown heading numeral `1.2`, which `c98_reproduce.py`'s `_FENCE`/`_XREF` pipeline counts
(it masks fences and indented blocks, and drops numerals preceded by `§`/`Table`/… — a bare ATX
heading numeral is preceded by `### ` and survives). `1.2` **already occurs twice** as a quantity
numeral in the draft, so `n_qd` — the asserted denominator — does not move:

```
β-box 0.7%, meta-stepsize 1.2%, budget 1.5%.
on the normal approximation `bn1` (adjusted p = 1.2e-8), `sm4` (0.017) ...
```

`analysis/paper_numeric_diff.py` drops heading numerals outright (`^\s*#{1,6}\s*\d+(?:\.\d+)*`),
so the heading is invisible to the diff. The remaining 30 new numerals the census sees are all
`§N.M` cross-references and all fall to `_XREF`. **Zero numerals reach either tool's quantity
multiset from anywhere in this package** — measured, not designed-and-hoped.

### The page count: 75 → 76, and it is not recoverable

Measured with `pdfinfo` on two builds from the same tree. I tried to buy the page back and could
not: a compact variant (`\footnotesize` table, the closing caveat paragraph deleted) still
measures **76**, because roughly half the growth is the ten openers spread across the document
rather than the guide block. `v9-plan.md`'s Plan C row asserts "75 pp, unchanged — and honestly
so"; that estimate is **wrong by one page** and I am reporting the measurement instead.
The trade is one page of navigation against seventy-five of content.

### One typographic detail worth keeping

The `tabular` uses `>{\raggedright\arraybackslash}p{...}` columns. Without `\raggedright` the map
generated **32 extra underfull-hbox warnings** (justification inside narrow `p` columns); with it
the distinct-underfull count is **16, identical to the base build**. `\arraybackslash` is
available — `array` is already loaded (preamble line 20) — and the build confirms it.

---

## 3. Design rules the text obeys (and one asymmetry that is required, not sloppy)

1. **No quantity anywhere.** Only `§N.M`, `Table N`, `Figure N`, `Appendix A`/`B`, threat labels
   `T1`–`T13`, audit section labels `[1]`–`[17]`, `make` targets and filenames. Nothing that
   `\d+\.\d+` or `\d{1,3}(?:,\d{3})+` can match outside an `_XREF` context.
2. **`§7.1` and `§7.2` are BANNED in `DRAFT-v4.md`.** In the Markdown those two strings refer to
   the **parent paper's** sections (`DRAFT-v4.md:41, 43, 45, 250, 254, 257, 258, 260` — the eight
   lines `xref_check.py` allowlists), and our own §7 subsections carry **no numbers** in the
   Markdown at all. So the map and the openers name §7's subsections by **threat label** (`§7
   T1–T8`, `T13`) and by title in the Markdown, while the TeX uses
   `\S\ref{sec:threats-evidence}` / `\S\ref{sec:threats-process}` and renders "§7.1" / "§7.2".
   The two markups therefore differ *in surface* here. That is the pre-existing convention, not
   a lapse: writing "§7.1" into the Markdown would make it collide with a parent-paper reference,
   and `xref_check.py` would be right to reject it.
3. **Float numbers differ between markups and the map respects that.** `tab:D` renders as
   **Table 4** in `paper.tex` (the TeX numbers `tab:tensor-rules`, `tab:partitions` and
   `tab:inflight` ahead of it) and is called **Table 2** in `DRAFT-v4.md` (which numbers only
   three tables and four figures). The TeX therefore uses `\ref` throughout and the Markdown
   uses its own numbers — the same split §1.1 already uses.
4. **No new float.** The map is a non-floating `center`+`tabular`, so it takes **no table
   number** and shifts nothing downstream in the TeX.
5. **The heading number is `1.2`,** which was verified to be an existing quantity numeral before
   it was used (§2), and `§2`…`§9` are untouched — §1.2 is a *sub*section, so nothing renumbers.
6. **Audit label `[15]` is never cited.** It is used **twice** in
   `analysis/c98_reproduce.py` (line 621, the partition-family meta-optimiser census; line 987,
   metric sensitivity) and is therefore ambiguous. See §6.

---

## 4. EXACT REPLACEMENT BLOCKS

Every anchor below was verified `count == 1` against the live file at HEAD `58c0c85`
(24 anchors, 24 hits). Apply with a literal string replace, not `sed`. The blocks are
independent of each other; order does not matter within §4.

**Round-tripped.** The 24 blocks were parsed back out of *this file*, applied to the live
`paper.tex` and `DRAFT-v4.md`, and the results compared byte-for-byte against the two patched
copies that every check in §2 was run against: **both identical**. So what is printed below is
exactly what was verified, not a transcription of it.

### A. `paper/DRAFT-v4.md` --- new subsection 1.2

#### A1. Insert the reader's guide (before the `---` that closes 1.1)

ANCHOR (verified `count == 1`):

```markdown
   batches, and an internal variance claim that did not reproduce (§6, Appendix A).

---

## 2. Related work, and what is left
```

REPLACE WITH:

```markdown
   batches, and an internal variance claim that did not reproduce (§6, Appendix A).

### 1.2 Reader's guide and evidence map

This paper is long because it reports a failed mechanism search alongside a positive result, and
both are evidence. It is not built to be read straight through, so this subsection says where
everything is.

**Four things carry the argument**: the count-matched contrast (§4.3, Table 2); the candidate
moderator and the endpoint knife taken to it (§4.4); the budget reading and the sentence of ours
it withdrew (§4.8); and the stated scope of the audit that re-derives all three (§3.4). A referee
who reads only those four has the argument in front of them. Every other section supports one of
them, bounds one of them, or reports something we looked for and did not find.

**The map below is an index, not a summary.** For each claim it names the subsection that states
it, the float that displays it, the numbered section of `analysis/c98_reproduce.py` that
re-derives it, and the deposit command that re-runs that derivation (§8). It carries no
quantities on purpose: every number in this paper is stated at one site, and the map points at
the site rather than repeating it.

| claim | stated in | shown in | audit | deposit |
|---|---|---|---|---|
| At fixed group count, the partition beats the count | §4.3, §4.5 | Table 2, Figure 1 | `[2]`, `[9]` | `make reproduce-table2` |
| The base optimiser moderates the effect — conditional on the endpoint | §4.4 | Figure 2 | `[3]` | `make reproduce` |
| Nine candidate mechanisms, and none of them is a general carrier | §5, §5.4, §5.5 | Figure 4 | `[6]`, `[17]` | `make reproduce` |
| The effect survives 3× the budget, and it declines with it | §4.8 | Figure 3 | `[7]` | `make reproduce` |
| Alignment is a bounded null, and the permutation draw is exchangeable | §4.6, §4.6.1, §5.10 | — | `[4]` | `make reproduce` |
| The one-dimensional-tensor prescription, and its base–meta exception | §4.7 | — | `[5]` | `make reproduce` |
| The corpus, the count-matching, admissibility and attrition | §3.1–§3.3, §8 | Table 1, Table 3 | `[1]`, `[13]` | `make verify`, `make reproduce` |
| The scope limits, including the competitiveness deficit | §7 T1–T8 | — | `[8]` | `make reproduce` |
| The four in-flight registrations, and the one that reversed us | §3.5, §4.8, Appendix A | Figure 3 | `[7]` | `make reproduce` |
| What the audit asserts, and what it does not | §3.4, §8 | — | `[16]`, `[14]` | `make reproduce` |

**What the map does not do.** It does not weight the evidence and it does not stand in for §7:
a row says where a claim is, not how much it will bear. Where a claim is conditional — §4.4's
moderator, §4.7's prescription and §4.8's slope each are — the condition is stated at the site
and only there.

---

## 2. Related work, and what is left
```

### B. `paper/paper.tex` --- new subsection, `\label{sec:guide}`

#### B1. Insert the reader's guide (after `\end{enumerate}`)

ANCHOR (verified `count == 1`):

```latex
  (\S\ref{sec:discipline}, Appendix~\ref{app:discrepancy}).
\end{enumerate}

\section{Related work, and what is left}
```

REPLACE WITH:

```latex
  (\S\ref{sec:discipline}, Appendix~\ref{app:discrepancy}).
\end{enumerate}

\subsection{Reader's guide and evidence map}
\label{sec:guide}

This paper is long because it reports a failed mechanism search alongside a positive result, and
both are evidence. It is not built to be read straight through, so this subsection says where
everything is.

\textbf{Four things carry the argument}: the count-matched contrast
(\S\ref{sec:primary}, Table~\ref{tab:D}); the candidate moderator and the endpoint knife taken
to it (\S\ref{sec:moderator}); the budget reading and the sentence of ours it withdrew
(\S\ref{sec:budget}); and the stated scope of the audit that re-derives all three
(\S\ref{sec:registration}). A referee who reads only those four has the argument in front of
them. Every other section supports one of them, bounds one of them, or reports something we
looked for and did not find.

\textbf{The map below is an index, not a summary.} For each claim it names the subsection that
states it, the float that displays it, the numbered section of
\texttt{analysis/c98\_reproduce.py} that re-derives it, and the deposit command that re-runs that
derivation (\S\ref{sec:repro}). It carries no quantities on purpose: every number in this paper
is stated at one site, and the map points at the site rather than repeating it.

\begin{center}
\small
\begin{tabular}{@{}>{\raggedright\arraybackslash}p{0.27\linewidth}>{\raggedright\arraybackslash}p{0.15\linewidth}>{\raggedright\arraybackslash}p{0.13\linewidth}>{\raggedright\arraybackslash}p{0.07\linewidth}>{\raggedright\arraybackslash}p{0.21\linewidth}@{}}
\toprule
claim & stated in & shown in & audit & deposit \\
\midrule
At fixed group count, the partition beats the count &
  \S\ref{sec:primary}, \S\ref{sec:rule11} & Table~\ref{tab:D}, Figure~\ref{fig:forest} &
  \texttt{[2]}, \texttt{[9]} & \texttt{make reproduce-table2} \\
The base optimiser moderates the effect --- conditional on the endpoint &
  \S\ref{sec:moderator} & Figure~\ref{fig:moderator} & \texttt{[3]} &
  \texttt{make reproduce} \\
Nine candidate mechanisms, and none of them is a general carrier &
  \S\ref{sec:mechanisms}, \S\ref{sec:tail}, \S\ref{sec:normalisation} &
  Figure~\ref{fig:decomposition} & \texttt{[6]}, \texttt{[17]} & \texttt{make reproduce} \\
The effect survives 3$\times$ the budget, and it declines with it &
  \S\ref{sec:budget} & Figure~\ref{fig:budget} & \texttt{[7]} & \texttt{make reproduce} \\
Alignment is a bounded null, and the permutation draw is exchangeable &
  \S\ref{sec:alignment}, \S\ref{sec:rp1}, \S\ref{sec:null-repeat} & --- & \texttt{[4]} &
  \texttt{make reproduce} \\
The one-dimensional-tensor prescription, and its base--meta exception &
  \S\ref{sec:prescription} & --- & \texttt{[5]} & \texttt{make reproduce} \\
The corpus, the count-matching, admissibility and attrition &
  \S\ref{sec:partitions}--\S\ref{sec:metric}, \S\ref{sec:repro} &
  Table~\ref{tab:partitions}, Table~\ref{tab:attrition} & \texttt{[1]}, \texttt{[13]} &
  \texttt{make verify}, \texttt{make reproduce} \\
The scope limits, including the competitiveness deficit &
  \S\ref{sec:threats-evidence} T1--T8 & --- & \texttt{[8]} & \texttt{make reproduce} \\
The four in-flight registrations, and the one that reversed us &
  \S\ref{sec:inflight}, \S\ref{sec:budget}, Appendix~\ref{app:discrepancy} &
  Figure~\ref{fig:budget} & \texttt{[7]} & \texttt{make reproduce} \\
What the audit asserts, and what it does not &
  \S\ref{sec:registration}, \S\ref{sec:repro} & --- & \texttt{[16]}, \texttt{[14]} &
  \texttt{make reproduce} \\
\bottomrule
\end{tabular}
\end{center}

\textbf{What the map does not do.} It does not weight the evidence and it does not stand in for
\S\ref{sec:threats}: a row says where a claim is, not how much it will bear. Where a claim is
conditional --- \S\ref{sec:moderator}'s moderator, \S\ref{sec:prescription}'s prescription and
\S\ref{sec:budget}'s slope each are --- the condition is stated at the site and only there.

\section{Related work, and what is left}
```

### C. The forward pointer in 1 that makes 1.2 discoverable

#### C1. `paper/DRAFT-v4.md`

ANCHOR (verified `count == 1`):

```markdown
§2 states exactly what is left, §1.1 lists what this paper adds,
and §3 fixes the partitions, the contrasts and the metric before any result is read.
```

REPLACE WITH:

```markdown
§2 states exactly what is left, §1.1 lists what this paper adds,
§1.2 maps every claim in it to the evidence for that claim, and §3 fixes the partitions,
the contrasts and the metric before any result is read.
```

#### C2. `paper/paper.tex`

ANCHOR (verified `count == 1`):

```latex
\S\ref{sec:related} states exactly what is left, \S\ref{sec:contributions} lists what this paper
adds, and \S\ref{sec:method} fixes the partitions, the contrasts and the metric before any result
is read.
```

REPLACE WITH:

```latex
\S\ref{sec:related} states exactly what is left, \S\ref{sec:contributions} lists what this paper
adds, \S\ref{sec:guide} maps every claim in it to the evidence for that claim, and
\S\ref{sec:method} fixes the partitions, the contrasts and the metric before any result
is read.
```

### D. The ten section openers

#### D1-md. `paper/DRAFT-v4.md` --- 3.3 Metric, admissibility, multiplicity

ANCHOR (verified `count == 1`):

```markdown
### 3.3 Metric, admissibility, multiplicity, and units of replication

**Metric.**
```

REPLACE WITH:

```markdown
### 3.3 Metric, admissibility, multiplicity, and units of replication

*This subsection fixes the endpoint, the admissibility filter, the multiplicity convention and
the unit of replication before any result is read. A referee who accepts those definitions can go
straight to §4.3; one who wants them varied wants §4.4's endpoint block and §7 T10.*

**Metric.**
```

#### D1-tex. `paper/paper.tex` --- 3.3 Metric, admissibility, multiplicity

ANCHOR (verified `count == 1`):

```latex
\subsection{Metric, admissibility, multiplicity, and units of replication}
\label{sec:metric}

\paragraph{Metric.}
```

REPLACE WITH:

```latex
\subsection{Metric, admissibility, multiplicity, and units of replication}
\label{sec:metric}

\emph{This subsection fixes the endpoint, the admissibility filter, the multiplicity convention
and the unit of replication before any result is read. A referee who accepts those definitions can
go straight to \S\ref{sec:primary}; one who wants them varied wants
\S\ref{sec:moderator}'s endpoint block and \S\ref{sec:threats} T10.}

\paragraph{Metric.}
```

#### D2-md. `paper/DRAFT-v4.md` --- 3.4 Registration discipline

ANCHOR (verified `count == 1`):

```markdown
### 3.4 Registration discipline

Where a batch has a scorer committed before its runs existed,
```

REPLACE WITH:

```markdown
### 3.4 Registration discipline

*This subsection states which scorers were registered before their runs existed, the three places
we knowingly depart from one, and — in its closing paragraph — what the audit asserts and what it
does not. That closing paragraph is what a referee checking a number's provenance wants.*

Where a batch has a scorer committed before its runs existed,
```

#### D2-tex. `paper/paper.tex` --- 3.4 Registration discipline

ANCHOR (verified `count == 1`):

```latex
\subsection{Registration discipline}
\label{sec:registration}

Where a batch has a scorer committed before its runs existed,
```

REPLACE WITH:

```latex
\subsection{Registration discipline}
\label{sec:registration}

\emph{This subsection states which scorers were registered before their runs existed, the three
places we knowingly depart from one, and --- in its closing paragraph --- what the audit asserts
and what it does not. That closing paragraph is what a referee checking a number's provenance
wants.}

Where a batch has a scorer committed before its runs existed,
```

#### D3-md. `paper/DRAFT-v4.md` --- 3.5 Four pre-registered batches

ANCHOR (verified `count == 1`):

```markdown
### 3.5 Four pre-registered batches: all four now scored, one after a forced redesign

Three weaknesses this paper states about itself,
```

REPLACE WITH:

```markdown
### 3.5 Four pre-registered batches: all four now scored, one after a forced redesign

*This subsection puts the four in-flight registrations on the record with their decision rules
ahead of their numbers. A referee who wants only the outcomes can read the table at its head and
follow it into §4.4, §4.6.1, §4.7, §4.8 and §5.5.*

Three weaknesses this paper states about itself,
```

#### D3-tex. `paper/paper.tex` --- 3.5 Four pre-registered batches

ANCHOR (verified `count == 1`):

```latex
\subsection{Four pre-registered batches: all four now scored, one after a forced redesign}
\label{sec:inflight}

Three weaknesses this paper states about itself,
```

REPLACE WITH:

```latex
\subsection{Four pre-registered batches: all four now scored, one after a forced redesign}
\label{sec:inflight}

\emph{This subsection puts the four in-flight registrations on the record with their decision
rules ahead of their numbers. A referee who wants only the outcomes can read
Table~\ref{tab:inflight} and follow it into \S\ref{sec:moderator}, \S\ref{sec:rp1},
\S\ref{sec:prescription}, \S\ref{sec:budget} and \S\ref{sec:normalisation}.}

Three weaknesses this paper states about itself,
```

#### D4-md. `paper/DRAFT-v4.md` --- 4.4 head (the longest subsection)

ANCHOR (verified `count == 1`):

```markdown
Restrict Table 2 to the fourteen cells that run the same ResNet-18 partition contrast
```

REPLACE WITH:

```markdown
*This is the longest subsection in the paper and it does two separable things: it identifies a
candidate moderator for the heterogeneity in D, then it attacks that moderator. The attack begins
at "The endpoint, varied" below; Figure 2, at the end, carries both halves.*

Restrict Table 2 to the fourteen cells that run the same ResNet-18 partition contrast
```

#### D4-tex. `paper/paper.tex` --- 4.4 head (the longest subsection)

ANCHOR (verified `count == 1`):

```latex
Restrict Table~\ref{tab:D} to the fourteen cells that run the same ResNet-18 partition contrast
```

REPLACE WITH:

```latex
\emph{This is the longest subsection in the paper and it does two separable things: it identifies
a candidate moderator for the heterogeneity in $\Dstat$, then it attacks that moderator. The
attack begins at ``The endpoint, varied'' below; Figure~\ref{fig:moderator}, at the end, carries
both halves.}

Restrict Table~\ref{tab:D} to the fourteen cells that run the same ResNet-18 partition contrast
```

#### D5-md. `paper/DRAFT-v4.md` --- 4.4 endpoint block (the subject change)

ANCHOR (verified `count == 1`):

```markdown
**The endpoint, varied — and the part of this subsection that does not survive it.** Everything
```

REPLACE WITH:

```markdown
*From here the subsection changes subject: everything above establishes the decomposition,
everything below tests it against the three other end-of-training columns the corpus carries, and
§7 T13 supplies the null those tests are referred to.*

**The endpoint, varied — and the part of this subsection that does not survive it.** Everything
```

#### D5-tex. `paper/paper.tex` --- 4.4 endpoint block (the subject change)

ANCHOR (verified `count == 1`):

```latex
\paragraph{The endpoint, varied --- and the part of this subsection that does not survive it.}
Everything above is computed on \plateau{},
```

REPLACE WITH:

```latex
\emph{From here the subsection changes subject: everything above establishes the decomposition,
everything below tests it against the three other end-of-training columns the corpus carries, and
\S\ref{sec:threats} T13 supplies the null those tests are referred to.}

\paragraph{The endpoint, varied --- and the part of this subsection that does not survive it.}
Everything above is computed on \plateau{},
```

#### D6-md. `paper/DRAFT-v4.md` --- 4.7 The prescription

ANCHOR (verified `count == 1`):

```markdown
### 4.7 The prescription, and its exact scope

The practitioner's move implied by
```

REPLACE WITH:

```markdown
### 4.7 The prescription, and its exact scope

*This subsection states the one designer-facing recommendation the paper makes and then attaches
its scope, which is narrower than the recommendation. A referee who wants the recommendation and
its exception wants the prescription table and the endpoint rows below it.*

The practitioner's move implied by
```

#### D6-tex. `paper/paper.tex` --- 4.7 The prescription

ANCHOR (verified `count == 1`):

```latex
\subsection{The prescription, and its exact scope}
\label{sec:prescription}

The practitioner's move implied by
```

REPLACE WITH:

```latex
\subsection{The prescription, and its exact scope}
\label{sec:prescription}

\emph{This subsection states the one designer-facing recommendation the paper makes and then
attaches its scope, which is narrower than the recommendation. A referee who wants the
recommendation and its exception wants Table~\ref{tab:T} and the endpoint rows below it.}

The practitioner's move implied by
```

#### D7-md. `paper/DRAFT-v4.md` --- 5.4 the tail

ANCHOR (verified `count == 1`):

```markdown
### 5.4 Narrowed to a base–meta pairing: the tail as a universal carrier

`D − G` (Eqs. 1–2)
```

REPLACE WITH:

```markdown
### 5.4 Narrowed to a base–meta pairing: the tail as a universal carrier

*This subsection asks whether the size-1 tail is the carrier of D and ends by narrowing it to a
base–meta pairing instead. A referee following the mechanism search as a whole can read §5's
opening table, this subsection's verdict and Figure 4.*

`D − G` (Eqs. 1–2)
```

#### D7-tex. `paper/paper.tex` --- 5.4 the tail

ANCHOR (verified `count == 1`):

```latex
\subsection{Narrowed to a base--meta pairing: the tail as a universal carrier}
\label{sec:tail}

$\Dstat - \Gstat$
```

REPLACE WITH:

```latex
\subsection{Narrowed to a base--meta pairing: the tail as a universal carrier}
\label{sec:tail}

\emph{This subsection asks whether the size-1 tail is the carrier of $\Dstat$ and ends by
narrowing it to a base--meta pairing instead. A referee following the mechanism search as a whole
can read Table~\ref{tab:mechanisms}, this subsection's verdict and
Figure~\ref{fig:decomposition}.}

$\Dstat - \Gstat$
```

#### D8-md. `paper/DRAFT-v4.md` --- 7 Limits of the included evidence

ANCHOR (verified `count == 1`):

```markdown
### Limits of the included evidence

**T1 — Almost one meta-optimiser.**
```

REPLACE WITH:

```markdown
### Limits of the included evidence

*These are limits of the evidence itself: only more runs would move them. A referee weighing
external validity wants T1, T3 and T4. The limits a reader can re-decide on the deposited run
table are in the next subsection instead.*

**T1 — Almost one meta-optimiser.**
```

#### D8-tex. `paper/paper.tex` --- 7 Limits of the included evidence

ANCHOR (verified `count == 1`):

```latex
\subsection{Limits of the included evidence}
\label{sec:threats-evidence}

\paragraph{T1 --- Almost one meta-optimiser.}
```

REPLACE WITH:

```latex
\subsection{Limits of the included evidence}
\label{sec:threats-evidence}

\emph{These are limits of the evidence itself: only more runs would move them. A referee weighing
external validity wants T1, T3 and T4. The limits a reader can re-decide on the deposited run
table are in \S\ref{sec:threats-process} instead.}

\paragraph{T1 --- Almost one meta-optimiser.}
```

#### D9-md. `paper/DRAFT-v4.md` --- 7 Limits of the review process

ANCHOR (verified `count == 1`):

```markdown
### Limits of the review process

**T9 — Excluded data, and one batch that is two.**
```

REPLACE WITH:

```markdown
### Limits of the review process

*These are decisions we made in excluding, filtering, scoring and scoping this audit, and a reader
can re-make every one of them on the deposited run table. A referee checking the statistics wants
T13, which supplies the calibrated null this paper's Cochran Q readings are referred to.*

**T9 — Excluded data, and one batch that is two.**
```

#### D9-tex. `paper/paper.tex` --- 7 Limits of the review process

ANCHOR (verified `count == 1`):

```latex
\subsection{Limits of the review process}
\label{sec:threats-process}

\paragraph{T9 --- Excluded data, and one batch that is two.}
```

REPLACE WITH:

```latex
\subsection{Limits of the review process}
\label{sec:threats-process}

\emph{These are decisions we made in excluding, filtering, scoring and scoping this audit, and a
reader can re-make every one of them on the deposited run table. A referee checking the statistics
wants T13, which supplies the calibrated null this paper's Cochran $Q$ readings are referred to.}

\paragraph{T9 --- Excluded data, and one batch that is two.}
```

#### D10-md. `paper/DRAFT-v4.md` --- 8 Reproducibility

ANCHOR (verified `count == 1`):

```markdown
## 8. Reproducibility

**One command.**
```

REPLACE WITH:

```markdown
## 8. Reproducibility

*This section is the deposit's manual and the corpus's attrition ledger. A referee who only wants
to re-derive the headlines needs the one-command block immediately below; everything after it
documents what the deposit cannot re-run, and why, rather than leaving it to be discovered.*

**One command.**
```

#### D10-tex. `paper/paper.tex` --- 8 Reproducibility

ANCHOR (verified `count == 1`):

```latex
\section{Reproducibility}
\label{sec:repro}

\paragraph{One command.}
```

REPLACE WITH:

```latex
\section{Reproducibility}
\label{sec:repro}

\emph{This section is the deposit's manual and the corpus's attrition ledger. A referee who only
wants to re-derive the headlines needs the one-command block immediately below; everything after
it documents what the deposit cannot re-run, and why, rather than leaving it to be discovered.}

\paragraph{One command.}
```


---

## 5. REQUIRED consequential edit — `analysis/xref_check.py`

`xref_check.py` allowlists the eight **parent-paper** `§7.x` references **by line number**:

```python
PARENT_LINES = {41, 43, 45, 250, 254, 257, 258, 260}
```

Five of those eight lines sit **after** the §1.2 insertion and move. Without this edit
`xref_check.py` exits 1 with *8 unresolved, 8 stale allowlist entries* — which is the file's own
anti-rot design working, not a defect.

**Measured new set, with this package as the only change to `DRAFT-v4.md` above line 300:**

```python
PARENT_LINES = {41, 43, 45, 287, 291, 294, 295, 297}
```

(41/43/45 are before both edits and do not move; the other five shift **+37** — `+1` from the
§1 forward pointer, `+36` from the guide block.)

**Do not trust that literal set if any other agent has also edited `DRAFT-v4.md` above line 300.
Re-derive it.** The recipe is self-checking, because our own §7 defines no numbered subsections
in the Markdown, so the parent references are exactly the unresolved `§7.x` strings:

```
python3 - <<'PY'
import sys; sys.path.insert(0, 'analysis')
import xref_check as X
X.PARENT_LINES = set()
bad, _ = X.check(quiet=True)
print(sorted({ln for k, v, ln, l in bad if k == 'section'}))
PY
```

It must print **exactly eight** line numbers and each must be a `§7.1`/`§7.2`/`§7.3`/`§7.5`
reference to the parent paper. Write them into `PARENT_LINES`, then `python3
analysis/xref_check.py` must print `PASS -- every reference resolves`, `0` unresolved, `0` stale.

This is an edit to a registered check's data, not to its logic, and the file's docstring
anticipates it: *"the allowlist is itself checked … so the allowlist cannot silently rot as the
draft moves."* RULE 16 is not in play — `xref_check.py` is a repo check, not a scorer registered
against a batch before its runs existed — but the edit must still be declared in
`docs/CORRECTIONS.md`.

---

## 6. Integration order, and the re-green set

1. Apply **§4 A1 and B1** (the guide) and **C1/C2** (the pointer) — the guide before the
   pointer is not required, but keeping them in one commit is, because C1/C2 reference §1.2.
2. Apply the ten opener pairs, **md and tex together per opener**. Each is independent; a bad one
   can be reverted alone.
3. Apply **§5** — re-derive `PARENT_LINES`, do not paste the literal blind.
4. Re-green, in this order, and every one must hold:

```
python3 analysis/c98_reproduce.py        # ALL 636 CHECKS PASS; census 628/411/982/41.9%
python3 analysis/xref_check.py           # exit 0, PASS, 0 unresolved, 0 stale
python3 analysis/test_fence_mask.py      # ALL PASS
python3 analysis/paper_numeric_diff.py   # the SAME 8 residuals, exit 1 -- 0 new
cd paper && tectonic -X compile paper.tex  # exit 0; 2 overfull hboxes, not 3
```

5. `paper.pdf` will be **76 pp**, not 75. That is the only intended change to the green state.
   Anything else that moves is a defect in the integration, not in this package.
6. Declare in `docs/CORRECTIONS.md` (next free number): the three added elements, the measured
   932 words, the two deviations from `v9-plan.md` §8 with their reasons, the `PARENT_LINES`
   shift with the recompute recipe, `n_q` 2614 → 2615 with `n_qd` held at 982, and the page
   count 75 → 76 as a disclosed cost.
7. **The deposit is unaffected by this package** and must still be rebuilt at the submission
   commit for the reason already on the books (a stale coverage figure shipped once) — that is
   author item 4, not this one.

---

## 7. NEW PROBLEMS FOUND while building this (reported, not silently fixed)

### 7.1 `§7`'s own index is off by one: it says `T9–T12`, and `T13` exists

`§7`'s opening paragraph splits the threats into `T1–T8` (limits of the evidence) and
**`T9–T12`** (limits of the review process). But `T13` exists and sits inside *Limits of the
review process* (`DRAFT-v4.md:3357`, `paper.tex:4189`), between `T12` and the end of the
subsection. So the paper's own threat index does not list one of its own threats — and `T13` is
not a minor one: it is the calibrated-null correction that several of the paper's own $Q$
readings are referred to, and §1.1 items 1 and 3 both cite it.

This is a **content** correction, not navigation, so I have not folded it into §4. It is a
one-token change in each markup, adds no numeral (`T9–T13` is not matched by either tool's
quantity regex), and a signposting package that leaves the §7 index wrong would defeat its own
purpose. **Both anchors verified `count == 1`; each string occurs exactly once in its file.**

`paper/DRAFT-v4.md`:

```markdown
T9–T12 are **limits of the review process**
```
→
```markdown
T9–T13 are **limits of the review process**
```

`paper/paper.tex`:

```latex
T9--T12 are \textbf{limits of the review process}
```
→
```latex
T9--T13 are \textbf{limits of the review process}
```

### 7.2 `analysis/c98_reproduce.py` prints the section label `[15]` twice

`[15]` is used for two different sections: `analysis/c98_reproduce.py:621`
(`THE PARTITION-FAMILY META-OPTIMISER CENSUS (§7 T1, §1 scope (iii), A.1)`) and
`analysis/c98_reproduce.py:987` (`METRIC SENSITIVITY -- the endpoint varied, everything else held
fixed`). A reader following the audit's own printed labels cannot tell them apart, and the
evidence map deliberately cites neither. **Not fixed here** — it is registered audit machinery,
the numbering is cosmetic, and renumbering it mid-cycle would change 636 lines of output for no
gain. Worth one line in `docs/CORRECTIONS.md` and a rename to `[18]` at the next machinery
change, not now.

### 7.3 The briefing's R10 note on `F(39,172)` does not hold at HEAD, and the reason is a space

The briefing states `F(39,172)` "was real and is already closed (was missing from the Markdown)".
Re-measured at HEAD, `paper_numeric_diff.py` **still** reports `39,172` as tex-only ×1, and the
cause is spacing, not absence. The string exists three times in each file; the diff's token
regex `\d{1,3}(?:,\d{3})+` needs the comma followed **immediately** by three digits, so
`F(39, 172)` registers nothing and `F(39,172)` registers one token:

| | `paper.tex` | `paper/DRAFT-v4.md` |
|---|---|---|
| `F(39,172)` — no space, **counts** | line 1845, line 4750 | line 3822 |
| `F(39, 172)` — space, **not counted** | line 3820 | line 1438, line 3038 |
| tokens seen by the diff | **2** | **1** |

Hence the residual. This is R10's item, not mine, and I have not touched it — but the fix is to
make the comma spacing identical **site for site** across the two files, not to add a fourth
occurrence. Flagging it because "already closed" is exactly the kind of inherited claim this
project has had to withdraw before.

### 7.4 Not a defect, but the integrator should know: the two markups number floats differently

`tab:D` is **Table 4** in the compiled PDF and **Table 2** in `DRAFT-v4.md`, because the TeX
numbers three tables (`tab:tensor-rules`, `tab:partitions`, `tab:inflight`) ahead of it that the
Markdown renders unnumbered. `DRAFT-v4.md` numbers three tables and four figures in total; the
TeX has eleven `tabular`s. §1.1 already handles this by using `\ref` in the TeX and literal
numbers in the Markdown, `xref_check.py` validates the Markdown's numbers against the Markdown's
own captions, and the evidence map follows the same rule. Nothing to fix — but do not "correct"
the map's `Table 2` to `Table 4` when reading the two blocks side by side.

---

## 8. UNSURE — stated rather than guessed

* **Whether 76 pp reads better to a TMLR referee than 75 pp did.** The package spends a page to
  buy navigation. I measured the page and I measured that the navigation works mechanically
  (three one-hop routes, §1); I have no evidence on how a referee trades those off, and the
  briefing's own framing — that reviewer burden at 75 pp is the one real venue risk — is the
  assumption I am acting on rather than something I verified. If the operator's read is that
  page count itself is the risk, the openers are the separable half: dropping all ten saves
  426 words but **not** the page (measured — the compact variant is still 76), so there is no
  configuration of this package that keeps 75 pp.
* **Whether §1.2 should sit before or after §2.** I put it immediately after §1.1 because that
  is where `v9-plan.md` §7 specifies it and because a referee triaging a 76-pp paper reaches
  §1.1 before §2. I did not test the alternative (a "how to read this paper" block in front of
  §7, next to the threats). No measurement distinguishes them.
* **Whether the `audit` column earns its width.** It is the only column that points at a
  *re-derivation* rather than a *statement*, which is the whole reason the map exists beyond
  what §1.1 already gives — but a referee who never runs the audit gets nothing from it. I kept
  it. If it is cut, the map's marginal value over §1.1 collapses to the `deposit` column alone
  and I would argue for cutting the map instead.
* **Whether the ten openers should be italic.** Italic makes the convention learnable at a
  glance and is what `\emph{}` gives for free, but ten italic paragraphs is a visible house
  style being introduced at desk-accept. An alternative is `\paragraph{Where this fits.}`
  run-in heads, which are more conventional and heavier. I have no basis for preferring one on
  anything but taste, and taste is the authors'.

---

## 9. What this package does NOT touch

* the abstract (either markup) — `v9-plan.md` §6.4's headroom warning stands and is untested here;
* any existing sentence, number, table cell, caption, `\label`, `\ref`, equation or float;
* section, subsection, table, figure, equation, appendix or threat **numbering** of any kind;
* the four "declines ≠ disappears" guard sites (`DRAFT-v4.md:1023` and `:2188`, `paper.tex:1283`
  and `:2762`) — all four re-read at HEAD and all four untouched;
* §9's Contribution-1-intact site;
* the end matter — CRediT roles, Funding statement, correspondence address, author list;
* `results/all_runs.csv`, any scorer, any registered ARGS line, the deposit, `docs/STATUS.md`;
* the six author items, which remain exactly six and all open.
