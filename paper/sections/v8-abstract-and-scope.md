# v8 — package `abstract-and-scope` (R1 + R2)

**Scope.** Two edits, both about saying precisely what is true of *which* readings.
**R1** puts the budget decline into the abstract's threats paragraph, inside a 230-word cap.
**R2** rescopes T9's box/class caveat so it attaches to the as-published reading only.

**Status of this file.** Package only. `paper/paper.tex` and `paper/DRAFT-v4.md` were **not**
edited and nothing was committed. Every replacement below was applied to *copies* in a sandbox and
put through the full gate set; the results are in §5.

---

## 1. R1 — the abstract's one asymmetry

### 1.1 The problem, restated from the live file

The abstract's third paragraph exists to list qualifiers. It lists four: CIFAR resolution; a Lion
meta-optimiser carrying every count-matched cell but one; no held-out validation split; the
1.8–4.2 pp deficit against tuned baselines. It says nothing about the budget — no 300-epoch
reading, no withdrawal — while §4.8 carries a registered withdrawal of a flatness claim the project
itself published. A paragraph that lists four qualifiers and omits the fifth reads as selective,
and it leaves the manuscript's strongest piece of integrity evidence out of the paragraph an action
editor reads first.

### 1.2 The binding constraint, re-measured (do not take the briefing's number)

`paperfactory.agents.text_quality._abstract_defects` with the module default band
`ABSTRACT_TARGET_WORDS = (120, 230)`, run on the **live** files at HEAD `fe957e4`:

```
paper/paper.tex        words: 219  (band (120, 230))   _abstract_defects -> []
paper/DRAFT-v4.md      words: 228  (band (120, 230))   _abstract_defects -> []
```

**The briefing's "227 words" is not what the checker returns.** The binding file is
`DRAFT-v4.md` at **228**, i.e. **two** words of headroom, not three; `paper.tex` measures **219**
because `clean_abstract_text` strips `\citep{...}` and `\pp` before counting, so the two markups
are nine words apart for the same prose. Any word budget must be run against the Markdown.

Sentence caps checked at the same time (`MAX_ABSTRACT_SENTENCE_WORDS = 62`,
`MAX_ABSTRACT_SENTENCE_CHARS = 430`, `>= 2` semicolons, or `>= 5` numeric claims together with a
semicolon or two clause-dashes): the longest live sentence is 32 words, none is overloaded.

### 1.3 What the added clause has to say, and what it must not say

Four things had to fit: (a) the gap declines with budget; (b) it is still positive at 300 epochs;
(c) we withdraw our own earlier claim; (d) **the scope** — this is one batch's within-run budget
ladder, *not* the pooled twenty-cell contrast.

(d) is the trap. `+0.632` and `+0.394` straddle the pooled `+0.556`, so an unscoped clause would
read as "the pooled effect decays to +0.394", which is false: the pooled figure is a 20-cell
count-matched contrast and the ladder is `hz3`/`hz3q` alone. Hence **"Within one batch"**. The
corpus has 72 runs at 300+ epochs across `hz3`, `e3a`, `i3a300`, `i3b300`, `e300`, `hz3q` and the
`bg300/bg600` baselines, so the *definite* article ("the one batch run to 300 epochs") would have
been false; the indefinite scoping is the true one.

A second trap: A.2 states **"All three are reported wherever any of them is."** A clause that
quoted `+0.632`/`+0.394` without saying which reading they come from would be in tension with the
project's own rule. **"on repaired data"** discloses the reading in three words and tells the reader
that others exist — §4.8 carries all three columns.

Numbers used are `+0.632` and `+0.394`, the repaired column of §4.8's budget table, exactly as
printed there; no new decimal enters `DRAFT-v4.md`, which matters because c98 §[16] asserts the
count of **distinct** quantity-numerals in that file (see §5.3).

### 1.4 Where the words came from

The clause costs 24 words in the Markdown. The abstract had two. The other 22 come from six
compressions, none of which drops evidence:

| # | was | is | md words |
|---|---|---|---|
| 1 | "Its contribution therefore remains unmeasured. Our research question is whether it survives at fixed count." | "Its contribution therefore remains unmeasured: does it survive at fixed count?" | −4 |
| 2 | "We answer with a benchmarking experiment on the released artefact" | "We answer by benchmarking the released artefact" | −3 |
| 3 | "corpus; the unit of analysis is a within-batch count-matched contrast" | "corpus, the unit a within-batch count-matched contrast" | −3 |
| 4 | "wins in all twenty" / "the effect size is" | "wins all twenty" / "the effect is" | −2 |
| 5 | "−0.018 ± 0.079 **pp** in a pre-registered replication" (unit already given three words earlier) | "−0.018 ± 0.079 in a pre-registered replication" | −1 |
| 6 | "Threats to validity: … vision, **and** a Lion" | "Threats: … vision; a Lion" | −3 |
| 7 | "(SGD+cosine on ResNet-18, AdamW+cosine on ResNet-34 and ResNet-50)" | *dropped* — the claim is the 1.8–4.2 pp deficit; §7 T4 and c98's `chk("tuned SGD+cosine baseline, ResNet-18/C10", …)` name the baselines | −8 |

Two constraints found by measurement rather than by guessing, both of which cost a rewrite:

* **"remains" is load-bearing.** `_missing_structured_moves` needs a Background cue from
  `(background|problem|need|yet|gap|challenge|lack|limited|remains?|despite|however)`; "remains
  unmeasured" is the only one in the abstract. Rewriting it away fires the defect.
* **"Every accuracy" is load-bearing.** The Results cue list matches `\baccuracy\b`; "reports" does
  *not* match (`\breport\b` fails on the trailing *s*). An earlier draft that read "Accuracies are
  test-set quantities" produced
  `['abstract missing one or more structured moves: Background, Methods, Results, Conclusions']`.
  The singular is kept.

The final sentence is untouched: `_has_supported_final_stance` needs "support" in the last
sentence, which "not support for practitioners" supplies.

### 1.5 The measured result (this is the deliverable, not an estimate)

`_abstract_defects` run on the **edited** files:

```
paper/paper.tex        words: 217  (band (120, 230))   _abstract_defects -> []
paper/DRAFT-v4.md      words: 228  (band (120, 230))   _abstract_defects -> []
```

`DRAFT-v4.md` is **228 of 230** — the same headroom the abstract had before the clause was added,
and the clause is in. `paper.tex` is **217**. Per-sentence, after the edit:

```
paper.tex     S1 22  S2 11  S3 12  S4 16  S5 13  S6 30  S7 29
              S8  9  S9 15  S10 23 S11 14 S12 11 S13 12       max 30 (cap 62)
DRAFT-v4.md   S1 27  S2 11  S3 12  S4 16  S5 13  S6 31  S7 30
              S8  9  S9 15  S10 24 S11 14 S12 14 S13 12       max 31 (cap 62)
```

No sentence exceeds 62 words; the longest is 31. No sentence exceeds 430 characters (max 209).
No sentence carries two semicolons. The new sentence carries four numeric claims with no semicolon
and no clause-dash, so it is under the `>= 5 numerals + separator` overload rule with one to spare.

---

## 2. R2 — T9 over-scopes its own caveat

### 2.1 The current text, verbatim

`paper/paper.tex:4020–4025`:

> Consequently \S\ref{sec:budget}'s within-run pairing cancels seed, run and batch, but \textbf{not}
> the clip box (from epoch 162) and \textbf{not} the GPU class (throughout). Both exceptions are
> limits on the budget reading and must be carried with it; neither is cancelled by the pairing, and
> \S\ref{sec:budget} is to be read with them attached.
> The same applies to $\Tstat = \arm{nodewise1d} - \arm{nodewise}$;
> $\Gstat$ and $\Ustat$ are matched inside their pairs at every seed and are unaffected.

`paper/DRAFT-v4.md:3208–3212` is the same sentence in Markdown.

### 2.2 The ambiguity

The subject of every clause is *"§4.8's within-run pairing"* and *"§4.8"* — the whole subsection.
§4.8 reports **three** readings. The sentence therefore says, on its face, that all three carry the
clip-box and GPU-class exceptions, and closes with an instruction — *"§4.8 is to be read with them
attached"* — that a reader will apply to the repaired column three paragraphs above it. Context
scopes it to the archive; the words do not. The cost is not cosmetic: the repaired reading is the
one whose entire purpose was to remove those two exceptions, and the sentence as written hands that
back.

The scoping is in fact **narrower than "the archived readings"**. Measured below, the five-seed
archived reading is box- and class-matched too, because the offending seed is exactly the seed it
drops. Only the **six-seed as-published** reading carries the exceptions.

### 2.3 The evidence, read off the `.out` headers

Each run's `NODE=`, `BETA_CLIP=` and GPU-model lines are its own first four lines. Nothing here is
declared; the batch's registered scorer's `gpu-2080ti-11g` label is a declaration and is not used.
Per seed, across the four arms `nodewise` / `chunk777` / `nodewise1d` / `chunk2325`:

```
### as published (6 archived seeds)
  seed  src    GPU class (4 arms)           clip box     node(s)     MATCHED?
  0     hz3    NVIDIA L4                    -30:9.0      881,882,884 yes
  1     hz3    NVIDIA L4                    -30:9.0      881,882,884 yes
  2     hz3    NVIDIA L4                    -30:9.0      882,883,884 yes
  3     hz3    NVIDIA GeForce RTX 2080 Ti   -30:9.0      852,855     yes
  4     hz3    NVIDIA GeForce RTX 2080 Ti   -30:9.0      852,853,855 yes
  5     hz3    MIXED: A100 80GB | RTX 2080 Ti   MIXED: -15:-2.3026 | -30:9.0    NO
  -> every seed box- AND class-matched: NO

### seed 5 dropped (archived 0-4)
  -> every seed box- AND class-matched: YES

### repaired (archived 0-4 + hz3q seed 5)
  5     hz3q   NVIDIA L4                    -30:9.0      883         yes
  -> every seed box- AND class-matched: YES
```

and, contrast by contrast, inside the archived seed 5:

```
  D  = ch    - node    box CROSS     class CROSS     -> CARRIES THE EXCEPTION
  T  = n1d   - node    box CROSS     class CROSS     -> CARRIES THE EXCEPTION
  G  = c23   - n1d     box same      class same      -> matched
  U  = c23   - ch      box same      class same      -> matched
```

This confirms T9's existing statement that `G` and `U` are unaffected while `T` is not, and adds
what T9 does not say: the exception lives in **one seed of one reading**, and both the level and
the sign of the scoping are measurable rather than asserted.

The registered scorer agrees, run unedited with its own documented `--runs` / `--probes`
(`python3 analysis/c99_hz3q_score.py --runs …/alice-backup/runs --probes …/alice-backup/runs/hz3`):

```
    -- hz3q --
    c23    hz3q-c23-s5-4864635.ou node883   NVIDIA L4                    -30:9.0        300
    ch     hz3q-ch-s5-4864633.out node883   NVIDIA L4                    -30:9.0        300
    n1d    hz3q-n1d-s5-4864634.ou node883   NVIDIA L4                    -30:9.0        300
    node   hz3q-node-s5-4864632.o node883   NVIDIA L4                    -30:9.0        300
    -- hz3 ARCHIVE --
    c23    hz3-c23-s5-4814295.out node868   NVIDIA A100 80GB PCIe        -15:-2.3026    300
    ch     hz3-ch-s5-4814293.out  node872   NVIDIA A100 80GB PCIe        -15:-2.3026    300
    n1d    hz3-n1d-s5-4814294.out node873   NVIDIA A100 80GB PCIe        -15:-2.3026    300
    node   hz3-node-s5-4782027.ou node855   NVIDIA GeForce RTX 2080 Ti   -30:9.0        300

    RULE 13 -- THE SAME GATE, TURNED ON THE ARCHIVE IT IS MEANT TO REFUSE:
      REFUSED: GPU MODEL IS NOT SHARED across the four arms
      REFUSED: BETA_CLIP IS NOT SHARED across the four arms
    The gate cuts in both directions.

    H0 PASS -- all four arms: GPU 'NVIDIA L4', BETA_CLIP -30:9.0, seed 5, 300 epochs.
    D(s5) and G(s5) are now WITHIN-BOX and WITHIN-GPU-CLASS contrasts.
```

Note the scorer's own header line for the failing reading: **"hz3 AS PUBLISHED (6 archived seeds;
s5 cross-box, cross-class)"**. The registration already scopes the defect to that one reading; only
the prose does not.

### 2.4 What the rewrite does

Four things: it makes the subject *the as-published reading* rather than *§4.8*; it says in bold
that neither exception attaches to the other two readings; it gives the measured basis (one box,
one class per seed, off the headers rather than off a declaration) instead of asserting it; and it
keeps T9's existing `T` / `G` / `U` sentence but scopes it to the archived seed 5 as well. Nothing
is softened — the two exceptions are still stated, still un-cancellable by pairing, and the
as-published column still has to be read with them attached.

---

## 3. EXACT replacement text — `paper/paper.tex`

Both anchors were verified against the live file at HEAD `fe957e4` with `src.count(old) == 1`.

### 3.1 `paper.tex` — R1 (abstract body, currently lines 65–83)

**ANCHOR (count == 1) — replace this block:**

```latex
MetaOptimize \citep{sharifnassab2025metaoptimize} meta-learns one step size per parameter group and
reports that finer partitions help inconsistently, never separating that from the group
\emph{count}. Its contribution therefore remains unmeasured. Our research question is whether
it survives at fixed count. We answer with a benchmarking experiment on the released
artefact, patched only to add partitions. The sampling frame is a 2{,}177-run
CIFAR-10/CIFAR-100 corpus; the unit of analysis is a within-batch count-matched contrast.

The uniform partition wins in all twenty count-matched cells, on ResNet-18, ResNet-34 and
ResNet-50. Pooled over eight SGDm cells the effect size is $+0.556 \pm 0.045\pp$ (calibrated 95\% CI $\pm 0.121$), homogeneous against that null ($Q$ 4.21, median 9.4), while
cells differing in base optimiser are not. Alignment
is a bounded null: at fixed count and size multiset, permuting group membership is worth
$-0.009 \pm 0.157\pp$, and $-0.018 \pm 0.079\pp$ in a pre-registered replication at twice the
resolution. Of nine candidate mechanisms, none is a general carrier.

Threats to validity: the corpus is CIFAR-resolution vision, and a Lion meta-optimiser carries every
count-matched cell but one. Every accuracy is a test-set quantity with no held-out validation
split, bounding construct validity. The method trails tuned baselines (SGD $+$ cosine on
ResNet-18, AdamW $+$ cosine on ResNet-34 and ResNet-50) by 1.8--4.2\pp, dwarfing this
${\approx}0.6\pp$ effect. Read this as a constraint on partition design, not support for practitioners.
```

**REPLACEMENT:**

```latex
MetaOptimize \citep{sharifnassab2025metaoptimize} meta-learns one step size per parameter group and
reports that finer partitions help inconsistently, never separating that from the group
\emph{count}. Its contribution therefore remains unmeasured: does it survive at fixed count?
We answer by benchmarking the released artefact, patched only to add partitions. The sampling
frame is a 2{,}177-run CIFAR-10/CIFAR-100 corpus, the unit a within-batch count-matched contrast.

The uniform partition wins all twenty count-matched cells, on ResNet-18, ResNet-34 and
ResNet-50. Pooled over eight SGDm cells the effect is $+0.556 \pm 0.045\pp$ (calibrated 95\% CI $\pm 0.121$), homogeneous against that null ($Q$ 4.21, median 9.4), while
cells differing in base optimiser are not. Alignment
is a bounded null: at fixed count and size multiset, permuting group membership is worth
$-0.009 \pm 0.157\pp$, and $-0.018 \pm 0.079$ in a pre-registered replication at twice the
resolution. Of nine candidate mechanisms, none is a general carrier.

Threats: the corpus is CIFAR-resolution vision; a Lion meta-optimiser carries every
count-matched cell but one. Within one batch, on repaired data, the gap declines from
$+0.632\pp$ at 100 epochs to $+0.394$ at 300, withdrawing our earlier flatness claim. Every
accuracy is a test-set quantity with no held-out validation split, bounding construct validity.
The method trails tuned baselines by 1.8--4.2\pp, dwarfing this ${\approx}0.6\pp$ effect. Read
this as a constraint on partition design, not support for practitioners.
```

### 3.2 `paper.tex` — R2 (T9 tail, currently lines 4020–4025)

**ANCHOR (count == 1) — replace this block:**

```latex
Consequently \S\ref{sec:budget}'s within-run pairing cancels seed, run and batch, but \textbf{not}
the clip box (from epoch 162) and \textbf{not} the GPU class (throughout). Both exceptions are
limits on the budget reading and must be carried with it; neither is cancelled by the pairing, and
\S\ref{sec:budget} is to be read with them attached.
The same applies to $\Tstat = \arm{nodewise1d} - \arm{nodewise}$;
$\Gstat$ and $\Ustat$ are matched inside their pairs at every seed and are unaffected.
```

**REPLACEMENT:**

```latex
Consequently the within-run pairing behind \S\ref{sec:budget}'s \textbf{as-published} reading
cancels seed, run and batch, but \textbf{not} the clip box (from epoch 162) and \textbf{not} the
GPU class (throughout): that reading is the one that contains \arm{hz3}'s archived seed 5. Both
exceptions are limits on \emph{that} reading, neither is cancelled by the pairing, and the
as-published column is to be read with them attached. \textbf{Neither exception attaches to
\S\ref{sec:budget}'s other two readings.} The five-seed reading drops the offending seed and the
repaired reading replaces it, and both are matched on both counts --- read off the runs' own
headers rather than declared. Every seed of both sits in the single clip box $-30{:}9.0$, and every
seed of both has its four arms on one GPU class: L4 at seeds 0, 1 and 2 and at \arm{hz3q}'s seed 5,
RTX 2080 Ti at seeds 3 and 4, with \arm{hz3q}'s four arms additionally on one node,
\texttt{node883}. That is what the quartet was submitted to achieve, and it is why the repaired
column carries neither exception \emph{by construction}.
Inside the as-published reading the same exception applies to
$\Tstat = \arm{nodewise1d} - \arm{nodewise}$, whose archived seed-5 pair is cross-box and
cross-class; $\Gstat$ and $\Ustat$ are matched inside their pairs at every seed, archived seed 5
included, and are unaffected.
```

---

## 4. EXACT replacement text — `paper/DRAFT-v4.md`

### 4.1 `DRAFT-v4.md` — R1 (abstract body, currently lines 11–29)

**ANCHOR (count == 1) — replace this block:**

```markdown
MetaOptimize (Sharifnassab, Salehkaleybar & Sutton, ICML 2025) meta-learns one step size per
parameter group and reports that finer partitions help inconsistently, never separating that from
the group *count*. Its contribution therefore remains unmeasured. Our research question is
whether it survives at fixed count. We answer with a benchmarking experiment on the
released artefact, patched only to add partitions. The sampling frame is a 2,177-run
CIFAR-10/CIFAR-100 corpus; the unit of analysis is a within-batch count-matched contrast.

The uniform partition wins in all twenty count-matched cells, on ResNet-18, ResNet-34 and
ResNet-50. Pooled over eight SGDm cells the effect size is +0.556 ± 0.045 pp (calibrated 95% CI ± 0.121), homogeneous against that null (Q 4.21, median 9.4), while cells
differing in base optimiser are not. Alignment
is a bounded null: at fixed count and size multiset, permuting group membership is worth
−0.009 ± 0.157 pp, and −0.018 ± 0.079 pp in a pre-registered replication at twice the resolution.
Of nine candidate mechanisms, none is a general carrier.

Threats to validity: the corpus is CIFAR-resolution vision, and a Lion meta-optimiser carries every
count-matched cell but one. Every accuracy is a test-set quantity with no held-out validation
split, bounding construct validity. The method trails tuned baselines (SGD+cosine on ResNet-18,
AdamW+cosine on ResNet-34 and ResNet-50) by 1.8–4.2 pp, dwarfing this ≈0.6 pp effect. Read this as a
constraint on partition design, not support for practitioners.
```

**REPLACEMENT:**

```markdown
MetaOptimize (Sharifnassab, Salehkaleybar & Sutton, ICML 2025) meta-learns one step size per
parameter group and reports that finer partitions help inconsistently, never separating that from
the group *count*. Its contribution therefore remains unmeasured: does it survive at fixed count?
We answer by benchmarking the released artefact, patched only to add partitions. The sampling
frame is a 2,177-run CIFAR-10/CIFAR-100 corpus, the unit a within-batch count-matched contrast.

The uniform partition wins all twenty count-matched cells, on ResNet-18, ResNet-34 and
ResNet-50. Pooled over eight SGDm cells the effect is +0.556 ± 0.045 pp (calibrated 95% CI ± 0.121), homogeneous against that null (Q 4.21, median 9.4), while cells
differing in base optimiser are not. Alignment
is a bounded null: at fixed count and size multiset, permuting group membership is worth
−0.009 ± 0.157 pp, and −0.018 ± 0.079 in a pre-registered replication at twice the resolution.
Of nine candidate mechanisms, none is a general carrier.

Threats: the corpus is CIFAR-resolution vision; a Lion meta-optimiser carries every
count-matched cell but one. Within one batch, on repaired data, the gap declines from +0.632 pp at
100 epochs to +0.394 at 300, withdrawing our earlier flatness claim. Every accuracy is a test-set
quantity with no held-out validation split, bounding construct validity. The method trails tuned
baselines by 1.8–4.2 pp, dwarfing this ≈0.6 pp effect. Read this as a constraint on partition
design, not support for practitioners.
```

> Character note for the integrator: the Markdown block uses U+2212 MINUS (`−0.009`, `−0.018`),
> U+00B1 (`±`), U+2013 EN DASH (`1.8–4.2`) and U+2248 (`≈`), exactly as the live file does.
> `+0.632` and `+0.394` use ASCII `+`.

### 4.2 `DRAFT-v4.md` — R2 (T9 tail, currently lines 3208–3212)

**ANCHOR (count == 1) — replace this block:**

```markdown
Consequently §4.8's within-run pairing cancels seed, run and batch, but **not** the clip box (from
epoch 162) and **not** the GPU class (throughout). Both exceptions are limits on the budget
reading and must be carried with it; neither is cancelled by the pairing, and §4.8 is to be read
with them attached. The same applies to T = `nodewise1d` − `nodewise`; G and U are matched inside
their pairs at every seed and are unaffected.
```

**REPLACEMENT:**

```markdown
Consequently the within-run pairing behind §4.8's **as-published** reading cancels seed, run and
batch, but **not** the clip box (from epoch 162) and **not** the GPU class (throughout): that
reading is the one that contains `hz3`'s archived seed 5. Both exceptions are limits on *that*
reading, neither is cancelled by the pairing, and the as-published column is to be read with them
attached. **Neither exception attaches to §4.8's other two readings.** The five-seed reading drops
the offending seed and the repaired reading replaces it, and both are matched on both counts —
read off the runs' own headers rather than declared. Every seed of both sits in the single clip box
`−30:9.0`, and every seed of both has its four arms on one GPU class: L4 at seeds 0, 1 and 2 and at
`hz3q`'s seed 5, RTX 2080 Ti at seeds 3 and 4, with `hz3q`'s four arms additionally on one node,
`node883`. That is what the quartet was submitted to achieve, and it is why the repaired column
carries neither exception *by construction*. Inside the as-published reading the same exception
applies to T = `nodewise1d` − `nodewise`, whose archived seed-5 pair is cross-box and cross-class;
G and U are matched inside their pairs at every seed, archived seed 5 included, and are unaffected.
```

> Character note: `−30:9.0` and `T = nodewise1d − nodewise` use U+2212 MINUS, matching the live
> file; the clause dash after "on both counts" is U+2014 EM DASH.

---

## 5. Verification — all four replacements applied to copies, full gate set run

The four blocks above were applied programmatically to copies of the two files (`str.count(old)`
asserted `== 1` for each) in a sandbox whose `analysis/`, `results/` and `jobs/` are symlinks to the
live tree, so every scorer ran unedited against the real data.

### 5.1 Anchor uniqueness

```
TEX R1   anchor count = 1   OK
TEX R2   anchor count = 1   OK
MD R1    anchor count = 1   OK
MD R2    anchor count = 1   OK
```

### 5.2 `_abstract_defects` — before and after

```
BEFORE  paper.tex     219 words   []          AFTER  paper.tex     217 words   []
BEFORE  DRAFT-v4.md   228 words   []          AFTER  DRAFT-v4.md   228 words   []
```

Longest sentence after the edit: 30 words (tex) / 31 words (md), against the 62-word cap.

### 5.3 `analysis/paper_numeric_diff.py` — **no NEW residuals**

| | baseline (live tree) | after the four edits |
|---|---|---|
| quantity numerals, `paper.tex` | 2530 (**970 distinct**) | 2533 (**970 distinct**) |
| quantity numerals, `DRAFT-v4.md` | 2532 (**970 distinct**) | 2535 (**970 distinct**) |
| tex-only residuals | 3 | 3 |
| md-only residuals | 5 | 5 |

The residual list is byte-identical before and after: tex-only `0.05`, `3.0`, `39,172`; md-only
`0.087`, `0.279`, `3.19`, `9.0 ×2`. **The 8 known pre-existing residuals, and nothing else.** Token
counts rise by exactly 3 in *each* file (`0.632`, `0.394`, `9.0`), which is the balanced multiset
the diff requires; distinct counts do not move, because all three numerals already occur in both
markups. Exit code 1 in both cases, unchanged — that is the pre-existing 8-residual state, not a
regression.

### 5.4 `analysis/c98_reproduce.py` — exit 0, ALL 592 CHECKS PASS

Run from the sandbox with only its documented `METAOPT_RUNS` override so `[7] BUDGET` can reach the
raw `.out` series:

```
c98 exit=0
ALL 592 CHECKS PASS.
```

Identical to the live-tree baseline. §[16] — the coverage census, which asserts §3.4's own sentence
against the **distinct** quantity-numeral count of `DRAFT-v4.md` — still passes, because neither
edit adds or removes a distinct decimal in that file. **This is the constraint that dictated using
`+0.632`/`+0.394` rather than rounded `+0.63`/`+0.39`: a rounded form would be a new distinct
numeral and would take §3.4's triple stale, failing c98.**

### 5.5 `tectonic` — exit 0, 74 pp, warning parity

| | baseline `paper.tex` | edited `paper.tex` |
|---|---|---|
| exit | 0 | 0 |
| pages | 74 | 74 |
| `Overfull \hbox` | 8 | 8 |
| `Underfull \hbox` | 108 | 108 |

No new over/underfull boxes, no undefined references or citations. The rendered abstract and the
rendered T9 paragraph were extracted from the produced PDF and read correctly (abstract on p. 1,
T9 on p. 58).

---

## 6. Notes for the integrator

1. **`docs/STATUS.md` rows R1 and R6 are the items this package closes.** R1 ("Abstract carries no
   trace of the reversal, while listing four other threats") and R6 ("T9's '…§4.8 is to be read with
   them attached' … reads as scoping **all three** readings"). Not edited here — `STATUS.md` is
   shared with the concurrent packages.
2. **§4.8 has the same over-scoping in its opening paragraph, deliberately left alone.**
   `paper.tex:2673–2676` reads *"That pairing cancels the seed, the run and the batch identically.
   It does \textbf{not} cancel the step-size clip box or the GPU class, because \arm{hz3} is two
   submissions…"*. Context resolves it two sentences later ("That seed has since been re-run…"), and
   the sentence names `hz3` explicitly, so it is weaker than T9's version — but it is the same
   pattern. Out of this package's scope; flagged rather than silently changed.
3. **Nothing in the twenty-cell isolation is touched.** The abstract's Contribution-1 sentences
   ("wins all twenty count-matched cells", the `+0.556 ± 0.045` pool, the `Q 4.21` homogeneity, the
   alignment null) keep every number and every qualifier; the only changes there are "wins **in**
   all twenty" → "wins all twenty", "the effect **size** is" → "the effect is", and one redundant
   `pp` unit.
4. **Interaction with the concurrent R3 and R5 packages.** Both touch §4.8 prose, not T9's tail and
   not the abstract, so the anchors above should survive. If R5 rewrites the T9 paragraph's *earlier*
   sentences, the R2 anchor (which begins at "Consequently") is still expected to be unique — re-run
   the `count == 1` check before applying.
