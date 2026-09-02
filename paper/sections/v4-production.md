# REWRITE PACKAGE — `production` (v4)

Closes gate items **C2** (placeholders and `DOI: pending`), **C3** (draft-internal phrasing),
**C4** (the 922-word abstract), and clears the **gate artefact** at DRAFT-v3 line 1690.
Discharges **B6** as a side effect (the abstract's ResNet list), and half of **A8**
(the header block's "asserts every number" claim, deleted with the block).

**Concurrency.** `paper/DRAFT-v3.md` is **not edited by this package.** Every change is given
below as *exact replacement text keyed to an anchor that already exists in the draft*. Anchors are
quoted verbatim and line-break-exact so an integrator can `grep -n` for them. `paper/paper.tex`
is **not edited either** — it is being written by the latex package and grew from 1,687 to 2,676
lines while this package was being prepared — so §7 gives the same replacements in LaTeX, keyed to
text anchors rather than line numbers, for that package to consume.

**Files this package DID write, in the repository, because they are not the manuscript:**

| path | what changed | why it is this package's |
|---|---|---|
| `analysis/c98_reproduce.py` | five `paper=` constants in `[1] CORPUS` (2113→2173, 1671→1724, 2098→2150, 1582→1625, complete 17→24) | those five are the corpus numbers *the abstract prints*, and this package rewrites the abstract. See §6. |
| `analysis/c98_release.py` | README/CITATION templates: the DOI paragraph, a generated headline-numbers block, a *Minting the DOI* procedure, a `authors:` block in `CITATION.cff`, and the two draft-internal phrases the deposit shipped | the deposit is task (c) |
| `release/` | rebuilt: **137 files, 6.2 MB**, `make verify` 137/137 clean, `make reproduce` **exit 0, ALL 188 CHECKS PASS** | task (c) |
| `docs/STATUS.md` | appended the **TODO-FOR-AUTHOR** block of §11 | instructed by the task |

Nothing here was committed. `paper/DRAFT-v3.md`, `paper/paper.tex` and `paper/refs.bib` were not
touched.

**Nothing below was typed from prose.** Every number this package changes is re-derived in §8 from
`results/all_runs.csv` at HEAD, from the `.out` tree on both clusters, or from the registered tool
run unedited; the command is given beside each one.

---

## 0. The one-line summary of each change

| # | item | what happens |
|---|---|---|
| P1 | **C4** | The 922-word abstract becomes §1 prose (four blocks, one of them corrected, one deleted as duplicated). A **227-word** abstract replaces it. Verified against the gate's own `text_quality` module: **0 defects**, all four cascade defects gone. |
| P2 | **C3** | `**Draft v3.**` header block deleted (its one substantive paragraph moved to §3.3); the three *"An earlier draft…"* passages rewritten to keep the science and drop the changelog; `camera-ready` removed from §8. |
| P3 | **C2** | All six `⟨…⟩` placeholders replaced with finished prose: an author block, a two-part competing-interests statement, funding, acknowledgements, CRediT, correspondence. Nothing invented; four genuine author decisions go to `docs/STATUS.md` instead. |
| P4 | **C2** | Both `DOI: pending` strings replaced. The deposit is rebuilt, self-verifying, and carries a written minting procedure. `CITATION.cff` now has an `authors:` block and **no** `identifiers:` block, on purpose. |
| P5 | gate artefact | `defence` → `check` at line 1690. Verified to be the **only** match of the gate's 23 security signals in either file. |
| P6 | consequential | The corpus counts moved when `6a374f4` ingested 60 rows. Thirteen sites still print the pre-ingest numbers, and two of them are now **false**, not merely stale. Exact replacements, fully re-derived. |

---

## 1. P1 — C4: the abstract (922 → 227 words)

### 1.1 Why 227 and not "shorter"

The gate's blocking classification comes from `paperfactory/agents/text_quality.py`, whose
`_abstract_defects` runs six checks, not one. The 922-word block failed the length band and
**cascaded** into three more. The replacement below was written against that module and checked by
running it:

```
$ python3 -c "…; print(_abstract_defects(clean_abstract_text(open('abs.txt').read())))"
WORDS: 227
DEFECTS: NONE
```

All twelve sentences pass `_is_overloaded_sentence` (≤62 words, ≤430 chars, <2 semicolons, and no
sentence with ≥5 numeric claims that also carries a semicolon or two clause-dashes). The four
structured moves resolve on their cues. `_has_supported_final_stance` resolves on the last
sentence. Band is `(120, 230)`; 227 leaves three words of headroom, which is why the replacement
below must be applied **as written** — adding a clause puts it back over the cap.

### 1.2 REPLACEMENT — the abstract

**ANCHOR (DRAFT-v3 line 22 through line 92 inclusive):** the whole block from the line

```
## Abstract
```

down to and including the line

```
this paper.**
```

…i.e. everything between the `---` on line 20 and the `---` on line 93. **Replace all of it with:**

```markdown
## Abstract

MetaOptimize (Sharifnassab, Salehkaleybar & Sutton, ICML 2025) meta-learns one step size per
parameter group and reports that finer partitions help inconsistently. That inconsistency has
never been separated from the group *count*, so the partition's contribution remains unmeasured.
We hold the count fixed and swap an architecture-aligned partition (one step size per output
channel) for uniform chunks, over 2,173 runs on CIFAR-10 and CIFAR-100 with ResNet-18,
ResNet-34 and ResNet-50, every contrast taken within one submission, so batch effects cancel.

The uniform partition wins in every count-matched cell we measured. Pooled over the eight SGDm
cells the effect is +0.556 ± 0.045 pp and homogeneous there (Cochran Q 4.21 on 7 df), while cells
that differ in base optimiser are strongly heterogeneous. Alignment itself is a bounded null: at
fixed count and fixed size multiset, permuting which weights share a group is worth
−0.009 ± 0.157 pp, 95% CI [−55%, +51%] of it. Of nine candidate mechanisms, none survives as a
general carrier, and we report all nine.

Scope, stated here rather than deferred. The corpus is CIFAR-resolution vision, and a Lion
meta-optimiser carries every count-matched cell but one. Every accuracy is a test-set quantity
with no held-out validation split. The effect is ≈0.6 pp inside a method trailing tuned cosine
by 1.8–4.2 pp. This should be read as a constraint on partition design, not as support for
practitioners.
```

**Three deliberate properties of that text, so no one "improves" them back out:**

1. **It does not say "88%", and it names no moderator.** B1 establishes that the 88% share is
   label-invariant. The abstract states the two facts that survive B1 in either direction —
   heterogeneity across the eleven byte-identical cells (Q 36.4 / 10 df) and homogeneity inside the
   eight SGDm cells (Q 4.21 / 7 df) — and attributes neither. **B1 still owns Contribution 3 and
   the Conclusion.** It no longer owns the abstract.
2. **ResNet-18/34/50, not ResNet-10/18/34/50.** This is **B6**, and it is closed here: every
   count-matched cell is 18, 34 or 50 (§8 re-derives it). The corpus at large does contain
   ResNet-10 runs and one ResNet-101 run, which is why the wider list survives in §1, attached to
   the word "corpus", where it is true.
3. **"every count-matched cell but one uses a Lion meta-optimiser"** is the post-`sm4` form of
   scope item (iii). The pre-ingest text — "the meta-optimiser never" — is now false. See §5.4.
4. **It prints no cell count and no pooled Q for the cross-cell heterogeneity, on purpose.** Both
   quantities are moving under two other delivered packages: `new-results` grows Table 2 from 16
   cells to **20** (20/20 positive) and repools the contrast over **14** cells at Q 102.47/13;
   `calibration` repools it over **13** cells at Q 55.40/12. Those two disagree with each other,
   and `rp1` and `hz3`-R2 can move them again. The four numbers the abstract does print —
   +0.556 ± 0.045 with Q 4.21 on 7 df, the alignment null and its interval, and the 1.8–4.2 pp
   deficit — are the ones **both** packages leave unchanged, and each is asserted by
   `c98_reproduce.py`. An abstract that is right in every landing state needs no judgement call
   from the integrator, which is worth more than the two integers it gives up.

**If, and only if, the second-moment package does not add a ninth mechanism to §5**, change the one
word: `Of nine candidate mechanisms` → `Of eight candidate mechanisms`. Nothing else in the
abstract moves, and the word count changes by zero. This is the package's single external
dependency and it is restated in §10.

### 1.3 REPLACEMENT — where the 922 words go

The four content blocks move into §1. One block is **deleted** rather than moved, one is
**corrected**, and the opening quotation is **relocated** because it exists nowhere else in the
manuscript.

#### 1.3a The parent's closing observation, and the corpus sentence

`*"while increasing the number of step sizes is anticipated to enhance performance…"*` appears
**once in the whole manuscript**, in the abstract (`grep -n 'anticipated to enhance'` →
`DRAFT-v3.md:26`, `paper.tex:62`). Deleting the abstract without relocating it deletes the paper's
premise.

**ANCHOR (DRAFT-v3 line 108, the last line of §1's second paragraph):**

```
Limitations section asks for future work on *"the layer and weight levels"*.
```

**Insert immediately after that line, as a new paragraph:**

```markdown

That is also how the paper closes on the question: *"while increasing the number of step sizes
is anticipated to enhance performance, our experimental findings in Section 7 reveal that this
improvement is not consistent across the MetaOptimize approximations evaluated."* We take that
question up with 2,173 runs (≈1,625 GPU-hours; 1,724 admissible) on CIFAR-10 and CIFAR-100 —
ResNet-10, -18, -34 and -50 across the corpus, and ResNet-18, -34 and -50 in every count-matched
cell — and report one robust measurement, one bounded null, and a mechanism we could not find.
```

#### 1.3b The four blocks

**ANCHOR (DRAFT-v3 lines 129–137), the whole paragraph beginning:**

```
**We do not have a mechanism.** We think that is worth saying in the first section rather than the
```

…through its last line:

```
cross-validated success at n = 10 never is; we report both, and the null is the one that survives.
```

**Replace that entire paragraph with the following four blocks.** (The paragraph is not merely
displaced: two of its sentences duplicate §5's opening verbatim — *"Of the three refutations, one
rests on a gate registered before its data existed … data collected for other purposes"* is §5
lines 1163–1164 — and the surviving sentences are folded into the third block below.)

```markdown
**The measurement.** Replacing an architecture-aligned partition (one step size per output
channel, `nodewise`) by a uniform one of the *same group count* (fixed-size chunks of K weights)
is worth a positive amount of final accuracy in **every within-batch, count-matched cell we
measured** — Table 2 gives the cells and the count — spanning three networks (ResNet-18,
ResNet-34, ResNet-50), 2 datasets, 4 base optimisers, 2 meta-stepsizes and 2 budgets. On ResNet-18/CIFAR-10 with an SGDm base the
effect D = +0.456 ± 0.195 to +0.727 ± 0.200 pp across **six independent batches**; on ResNet-34
D = +0.666 ± 0.094 (9 v 9); on ResNet-50 D = +0.881 ± 0.261; on CIFAR-100 D = +1.640 ± 0.245 and
+1.485 ± 0.238. ⟪⟪ DO NOT PASTE THIS TOKEN — one sentence goes here, chosen by the rule in
§1.3b-bis; a manuscript containing this marker has been mis-integrated ⟫⟫ At a fixed base optimiser D does
not vary: over eight SGDm cells spanning seven separate submissions, two meta-stepsizes, two
budgets and three step-size clip boxes, D = **+0.556 ± 0.045 pp** with Q = 4.21 on 7 df (p = 0.76,
τ = 0.000). §4.4 takes up the base optimiser as the candidate moderator and states exactly what
that analysis can and cannot identify.

**The bounded null.** Architecture *alignment* is not a large carrier, and we can put a number on
how large it could still be. Permuting **which** weights share a group while holding the group
count **and the exact per-tensor group-size multiset** fixed is worth **−0.009 ± 0.157 pp
(t −0.06, 3 v 3, one batch)**, scored `NULL` against a symmetric band registered in advance. The
95% interval is **[−0.317, +0.298] pp = [−55%, +51%] of the same batch's D**, and the effect this
design could have detected at 80% power is **0.440 pp = 76% of D**. So an alignment effect
accounting for most of D is excluded; one accounting for half of it is **not** — power against
A = D/2 is 0.46. We also record a defect in our own registration: the NULL band's half-width (0.15)
is **narrower than the standard error the batch achieved** (0.157), so a genuinely zero effect would
have scored `NULL` only 66% of the time. What is left as the leading carrier is the group-**size
distribution**, which takes **+0.590 ± 0.107 (t 5.53)** of the same decomposition.

**What we could not find.** **We do not have a mechanism**, and that is worth saying in the first
section rather than the last. We examined nine candidate mechanisms and report the verdict on each
in §5 — which are refuted, which is narrowed to a single base optimiser, which is not separable
from the axes it is aliased with, and which cannot be decided by this instrument or this design —
because those verdicts are half the contribution. Chief among them: the obvious carrier —
degenerate size-1 groups — is not it (removing 100% of a network's singletons buys
+0.115 ± 0.133 pp, t 0.87); the tail story is base-specific (pooled D − G = +0.514 ± 0.056 under
SGDm, +0.047 ± 0.124 under AdamW); no summary statistic of the size distribution is *identifiable*
from this corpus, because at fixed count the design contains exactly one contrast type and every
candidate collapses to an indicator for the aligned arm; and **no measurable property of a
configuration predicts D out of sample** better than the corpus mean by a margin that survives the
power bound (|r| ≥ 0.632 needed at 10 design points). A cross-validated *null* at n = 10 is
defensible in a way a cross-validated success at n = 10 never is; we report both, and the null is
the one that survives.

**Scope, stated here and not deferred to a threats section.** (i) Everything is CIFAR-resolution
vision with ResNets and one meta-learning framework; ImageNet is out of reach on our data
allocation (489 of 1000 train classes present, validation set unlabelled). (ii) MetaOptimize trails
a tuned schedule at every scale we ran: on ResNet-18 its best plain cell reaches 93.317 ± 0.083 pp
against a tuned SGD+cosine baseline at 95.124 ± 0.047 (n=5, the interior maximum of a bracketed
grid), a **1.807 pp deficit**, and the deficit widens to 2.56 pp on ResNet-34 and 4.21 pp on
ResNet-50. We make no competitiveness claim. (iii) The base optimiser has been varied four ways and
the meta-optimiser once: of the 420 admissible runs in the partition families, 408 carry a **Lion**
meta-optimiser and 12 — one cell, the second-moment corner that §6.1's void batch failed to test —
carry RMSProp. One cell is not an axis, so no general statement about the meta-optimiser is
available from this corpus. (iv) The effect is ≈0.6 pp inside a method that is 1.8 to 4.2 pp
behind a cosine schedule. (v) Every accuracy here is a test-set quantity and no validation split was
held out anywhere (§3.3, §7 T12). (vi) We inherit, and partly overlap with, Choi et al. on
tuning-protocol sensitivity, Zheng & Kwok on blockwise adaptivity, and CAM-HD on the granularity
ladder and its interior optimum; §2 states exactly what is left.
```

#### 1.3b-bis The one slot this package does **not** fill

The `⟪⟪ … ⟫⟫` marker above stands where the sentence carrying *"88% of that variation is one
identified moderator"* used to be. **Three delivered packages own text at that position and two of
them disagree with each other**, so this package moves the container and does not write the claim.
The marker is deliberately un-pasteable: it is not a placeholder the manuscript may keep.

| source | what it puts there | pool |
|---|---|---|
| DRAFT-v3 as it stands | *"Over the eleven cells … Q = 36.4 on 10 df … and **88% of that variation is one identified moderator** …"* | 11 cells |
| `calibration`, EDIT B1-a | thirteen ResNet-18 cells (Table 2's eleven + `bm2`'s two), Q = 55.40 on 12 df, τ 0.231; **explicitly disclaims identification** — *"The defensible claim is that the base optimiser is the coarsest partition of these thirteen cells that leaves them internally homogeneous, not that it is the cause of their heterogeneity"* | 13 cells |
| `new-results`, §3.3 | fourteen cells (+`sm3`, `sm4` excluded by its own registered scope note), pool +0.530 ± 0.029, Q = 102.47 on 13 df, τ 0.295 | 14 cells |

**The rule, so this is not a judgement call:**

1. If `calibration` lands, its EDIT B1-a replacement text goes in the slot **verbatim**. It is the
   only one of the three that answers B1, and B1 is the reason the original sentence cannot stand.
2. If `new-results` also lands, its cell set and pool supersede `calibration`'s **numbers**
   (fourteen cells, +0.530 ± 0.029, Q 102.47/13) while `calibration`'s **argument** — that the
   share is a property of the grouping and not of the label, and that the defensible claim is
   "coarsest partition leaving them internally homogeneous" — is kept word for word. Neither
   package may be dropped in favour of the other: one owns the pool, the other owns the claim.
3. If neither lands, put in the slot: *"Over the eleven cells that run the same ResNet-18 partition
   contrast, D varies genuinely across configurations (**Q = 36.4 on 10 df, p = 7.2e-5**,
   τ = 0.203 pp against 0.152 pp rms measurement error)."* — i.e. DRAFT-v3's sentence **with the
   88% clause deleted**, which is B1's minimum requirement and is what this package would apply on
   its own authority.

The same three-way rule applies to `calibration`'s EDIT B2-b (the minimum-interesting-effect
clause, which attaches to the end of the SGDm sentence) and EDIT B3-b (scope item (iv)): both were
keyed to strings **in the abstract**, and after this package those strings are **in §1**. The
strings themselves are unchanged, so the edits still apply; only the section they land in moves.
`calibration`'s EDIT B6-a is **superseded** — it rewrites the abstract's opening sentence, and this
package replaces the whole abstract with one that already says ResNet-18/34/50 (§8 row 20).

#### 1.3c The block that is deleted, not moved

The abstract's fifth block — `**Four pre-registered batches are in flight** and are described in
§3.5 …` — is **not** relocated. §3.5 already carries the same four batches with a registration
table, a decision rule for each and the two standing rules they were submitted under (verified:
DRAFT-v3 lines 574–640). Moving the abstract's compressed version into §1 would put a second,
staler copy of a moving status in front of the reader. **Delete it.** Its one non-duplicated
sentence — *"None of them contributes a number to this draft"* — is a status claim that three of
the four batches have already outrun (`bm2` and `sm4` are complete and scored, `rp1` is 17/24), and
it is §3.5's to maintain, not §1's.

**What each block changed, and why — the complete list:**

| block | change | reason |
|---|---|---|
| The measurement | the whole heterogeneity sentence, including *"88% of that variation is one identified moderator, the base optimiser"*, is left as a marked slot rather than relocated | **B1**, and a live disagreement between two other packages. Relocating it unchanged would have carried a claim B1 requires be withdrawn into a section B1's package is not reading. §1.3b-bis gives the three-way rule and the fallback text — which is DRAFT-v3's sentence **with the 88% clause deleted**, not softened |
| The measurement | *"At a fixed base the effect is homogeneous"* → *"At a fixed base optimiser D does not vary"* | consequence of the slot above; the original clause read as the conclusion of the withheld claim |
| The measurement | *"every one of 16 within-batch, count-matched cells"* → *"every within-batch, count-matched cell we measured — Table 2 gives the cells and the count"* | same reason as the abstract: `new-results` takes Table 2 to 20 rows. One place should carry that integer, and it is Table 2, which is where a reader can count it |
| The bounded null | unchanged, verbatim | every number PASSes in the audit (§8) |
| What we could not find | *"We examined eight candidate mechanisms and refuted three of them, narrowed a fourth …, found a fifth …, and found the remaining three undecidable …; we report all eight"* → the tally is dropped and replaced by a pointer to §5 | the count moves to nine with the second-moment cell, and the *breakdown* is §5's index table to own. One place should state the tally; this is not it. |
| What we could not find | absorbed *"We do not have a mechanism … first section rather than the last"* and the cross-validated-null sentence from the deleted paragraph | fold-in, no content lost |
| Scope (iii) | rewritten | the old text asserts the meta-optimiser was **never** varied and that the fix is *"in flight"*. `sm4` has landed with 12 RMSProp-meta runs. See §6.4. |
| Scope (i), (ii), (iv), (v), (vi) | unchanged, verbatim | (iv) is **B3**'s: it still volunteers the practical-significance objection and still does not answer it. This package moves it; it does not answer it. |
| Four batches in flight | deleted | duplicated by §3.5, and stale |

---

## 2. P2 — C3: draft-internal phrasing

Four sites. Two of them carry science that must survive the edit, and it does.

### 2.1 The `**Draft v3.**` header block — deleted, with one paragraph relocated

**ANCHOR (DRAFT-v3 lines 3–18):** the two paragraphs between the title and the first `---`,
beginning

```
**Draft v3.** Every number in this document was re-derived from `results/all_runs.csv` and from the
```

and ending

```
referee who recomputes from the printed table alone finds no surprise.
```

**Action: delete lines 3–11 (the `**Draft v3.**` paragraph) outright, and MOVE lines 13–18 (the
`**Meta-analytic convention.**` paragraph) into §3.3.** Result: the manuscript opens on its title
and its abstract, as a manuscript does.

The deleted paragraph asserts five things. Four are stated elsewhere already, in the sections that
own them, and one of the four is a **claim the red team has flagged as false**:

| assertion in the header block | where it already lives | note |
|---|---|---|
| every number re-derived under the admissibility gate | §3.3, Eq. 11 | |
| `c98_reproduce.py` "asserts against what this text prints … exits non-zero if any headline fails" | §3.4, final paragraph | **A8.** The header's version says the script asserts *every number*; it asserts 188 sites covering 25.4% of the manuscript's distinct quantity-numerals, and the script now prints that census itself. Deleting the header removes one of A8's two false sites. **A8 still owns the §3.4 sentence.** |
| registered scorers run unedited, including where the verdict cost a subsection | §3.4 | |
| numbers that failed to reproduce are in Appendix A | Appendix A's own two-line preamble | |
| four batches in flight, none contributing a number | §3.5, in full | |

**REPLACEMENT — the relocated paragraph.** ANCHOR (DRAFT-v3 line 527, the last line of §3.3's
`**Heterogeneity.**` paragraph):

```
with degrees of freedom adding likewise. Figure 2(b) is that partition.
```

**Insert immediately after it, as a new paragraph:**

```markdown

**The precision every pooled quantity is computed at.** Every pooled estimate, Cochran *Q* and
DerSimonian–Laird τ in this paper is computed from full-precision arm means in the run table,
which is what the deposited code computes and what `make reproduce` re-derives. Computing the
same quantities from the three-decimal (D, se) pairs *as printed in Table 2* gives values that
differ in the second decimal (43.19 → 43.01 on twelve cells; 36.40 → 36.29 on eleven); both are
given in Appendix A.4 so that a referee who recomputes from the printed table alone finds no
surprise.
```

The only edit to that paragraph is its run-in heading: `**Meta-analytic convention.**` →
`**The precision every pooled quantity is computed at.**`, because in §3.3 it sits among
`**Unit of replication.**`, `**Heterogeneity.**`, `**Multiplicity.**` and `**Duplicate runs.**`,
and "convention" alone no longer says which one. Standing rule 22 is unaffected: this paragraph
*is* rule 22 in the manuscript, and it is now inside the methods section rather than above the
abstract.

### 2.2 "An earlier draft of this paper claimed four refutations" — §5, line 1167

This one carries real science: it is the paper's most expensive application of its own
registered-scorer rule. The content stays; the changelog framing goes.

**ANCHOR (DRAFT-v3 lines 1167–1171):**

```
**An earlier draft of this paper claimed four refutations**, the fourth being M7, on the strength of
a within-batch contrast that the relevant batch's own registered scorer refuses to compute (§5.6,
§7 T7). We withdrew the contrast and the refutation with it. That is the most expensive single
application of §3.4's rule in this paper and it is the reason the rule is worth stating as a
contribution.
```

**REPLACEMENT:**

```markdown
**M7 is not a fourth refutation, and the reason is worth stating.** The contrast that would make
it one is a within-batch separator that the relevant batch's own registered scorer **refuses to
compute** (§5.6, §7 T7). Under §3.4 we report the refusal and not the contrast, so the refutation
is unavailable and M7 stands at *not separable*. That is the most expensive single application of
§3.4's rule in this paper, and it is the reason the rule is worth stating as a contribution rather
than as a habit.
```

Nothing is lost: the withdrawal is still stated, the scorer's refusal is still the reason, the cost
is still owned, and §5.6 and §7 T7 still carry the detail. What goes is the implication that the
reader is holding a revision of something.

### 2.3 "An earlier draft claimed both, and that was wrong" — §7 T9, line 1814

**ANCHOR (DRAFT-v3 lines 1812–1816):**

```
Consequently §4.8's within-run pairing cancels seed, run and batch, but **not** the clip box (from
epoch 162) and **not** the GPU class (throughout). An earlier draft claimed both, and that was
wrong. The same applies to T = `nodewise1d` − `nodewise`; G and U are matched inside their pairs
at every seed and are unaffected.
```

**REPLACEMENT:**

```markdown
Consequently §4.8's within-run pairing cancels seed, run and batch, but **not** the clip box (from
epoch 162) and **not** the GPU class (throughout). Both exceptions are limits on the budget
reading and must be carried with it; neither is cancelled by the pairing, and §4.8 is to be read
with them attached. The same applies to T = `nodewise1d` − `nodewise`; G and U are matched inside
their pairs at every seed and are unaffected.
```

The correction's scientific content — *which* sources of variation the pairing does and does not
cancel — is in the first sentence already and is strengthened, not weakened, by the replacement.
No Appendix A entry is added, and none is needed: nothing here is a number that failed to
reproduce, which is what Appendix A registers.

### 2.4 "than the earlier draft implied" — Appendix A.5, line 2199

Appendix A *is* the corrections register, so a correction belongs here. What does not belong is
the phrase, because A.5's own frame is "the record said X, the data say Y" and "the earlier draft"
is a third thing.

**ANCHOR (DRAFT-v3 lines 2198–2200):**

```
functional form is a best-of-ten selection, and the power bound |r| ≥ 0.632 is not approached — but
the null now holds by less than the earlier draft implied, and we report that rather than the older
phrasing.
```

**REPLACEMENT:**

```markdown
functional form is a best-of-ten selection, and the power bound |r| ≥ 0.632 is not approached — but
the null now holds by a narrower margin than the record implied, and we report the margin that
re-derives rather than the record's phrasing.
```

### 2.5 "camera-ready" — §8, line 1873

Handled in §3.2 below, where the whole `**Artefact and DOI.**` paragraph is replaced. It is the
only occurrence of the word in the manuscript (`grep -n -i 'camera' paper/DRAFT-v3.md` → one hit,
line 1873). The deposit shipped it twice more, in `release/README.md` and `release/CITATION.cff`;
both are gone from the templates in `analysis/c98_release.py` and from the rebuilt deposit.

---

## 3. P3 / P4 — C2: the six placeholders, and both `DOI: pending` strings

### 3.0 The rule this section was written under

**Nothing is invented.** No affiliation, ORCID, grant number or DOI appears below that is not
already on the record in this repository. Where a value is a *decision* rather than a lookup —
whether a third contributor joins the author list, which address the venue wants, whether a grant
applies — the manuscript is given finished prose that is true of the paper **as it stands**, and
the decision is written into `docs/STATUS.md` under **TODO-FOR-AUTHOR** (§11). A placeholder is
not replaced by a better-disguised placeholder.

Sources used, so every filled value can be traced:

| filled value | source in this repository |
|---|---|
| both authors' names | DRAFT-v3 End matter, CRediT paragraph; `paper/paper.tex` line 51 |
| affiliation "LIACS, Leiden University" | DRAFT-v3 Funding paragraph ("an MSc research project at LIACS, Leiden University"); `paper/paper.tex` `\thanks` |
| "no dedicated project funding" | DRAFT-v3 Funding paragraph, already asserted |
| the ALICE acknowledgement wording | DRAFT-v3 Acknowledgements, already the cluster's required form |
| the supervisor's conflict | DRAFT-v3 Competing interests, already asserted; the parent paper's own author list |
| the third contributor's existence and the nature of the contribution | DRAFT-v3 Competing interests and CRediT placeholders, §2.4, §5.9 |
| the correspondence address | the author's own address of record on this repository |

**Not** used: the third contributor's identity. `docs/PLAN-appendix-collab.md` line 133 names a
person and asserts he originated the design. That is an internal advisory note, the credit
question it raises is unresolved, and putting a name into an author list or an acknowledgement is
the authors' decision and not this package's. The name is quoted in the STATUS.md TODO so the
decision can be taken with the source in front of it; it is not quoted in the manuscript.

### 3.1 NEW — an author block (closes the "author list" placeholder, line 2338)

**ANCHOR: DRAFT-v3 line 1, the title.** After deleting the `**Draft v3.**` block (§2.1), insert
the following between the title and the `---` on line 20:

```markdown

**M. Ahmaditeshnizi** · **S. Salehkaleybar**
LIACS, Leiden University, the Netherlands
Correspondence: `mohammadrezaahmaditeshnizi@gmail.com`
```

Two authors, both already named in the manuscript, both at the affiliation the manuscript already
states. The list is complete as the paper stands; the one open question about it is a credit
question, it is disclosed in the manuscript under Competing interests and Author contributions
below, and it is the first item of the TODO in §11.

### 3.2 REPLACEMENT — §8's `**Artefact and DOI.**` paragraph (first `DOI: pending`)

**ANCHOR (DRAFT-v3 lines 1870–1873):**

```
**Artefact and DOI.** The deposit is ≈6 MB in 137 files, with `MANIFEST.md5` covering
every one of them. **DOI: pending**; a reserved DOI is minted at submission and written
into the paper, into `CITATION.cff` and into the Data-availability statement before
camera-ready. Until then the artefact is identified by its repository commit.
```

**REPLACEMENT:**

```markdown
**Artefact and identifier.** The deposit is **6.2 MB in 137 files**, with `MANIFEST.md5`
covering every one of them and `make verify` checking all 137 against it. **It has no DOI, and
this paper prints none.** The artefact is identified by the repository commit stamped at the top
of the deposit's `README.md`, which `MANIFEST.md5` pins byte-for-byte; a DOI is attached when the
archive of record issues one, and the deposit carries the four-step procedure for doing that and
for writing the resulting string into the three places that must agree. We print the commit rather
than a promised identifier because a promised identifier does not resolve.
```

### 3.3 REPLACEMENT — the End matter's `DOI: pending` sentence (second occurrence)

This is a **single-sentence surgical replacement inside the Data-availability paragraph.** The
rest of that paragraph — in particular the sentence *"No number in this paper requires data that
is not in that deposit"* — is **A2's**, is known false, and is deliberately left alone here so the
two packages do not overwrite each other. See §10.

**ANCHOR (DRAFT-v3 lines 2283–2285), one sentence:**

```
**DOI: pending** — a reserved DOI is minted at submission and inserted here and in
`CITATION.cff`; until then the artefact is identified by its repository commit. The archive is
≈6 MB, carries an md5 manifest for every file, and reproduces every number in this paper with
```

**REPLACEMENT (same position, same paragraph):**

```markdown
**The deposit has no DOI**, because it has not been deposited; the artefact is identified by the
repository commit recorded in its `README.md`, and `CITATION.cff` carries no `identifiers:` block
rather than a stand-in for one. The archive is 6.2 MB, carries an md5 manifest for every file, and
reproduces every number in this paper with
```

### 3.4 REPLACEMENT — Competing interests (closes the conditional-second-COI placeholder, line 2319)

**ANCHOR (DRAFT-v3 lines 2319–2323), the tail of the paragraph:**

```
letting the reader assume coverage. ⟨If the final author list includes a further co-author
of the parent paper, that must be stated here in the same sentence, and §5.9's negative
result on hierarchical partial pooling — an idea originated by a proposed co-author — must
be disclosed as a second, independent conflict of the same kind.⟩ The authors declare no
financial competing interests.
```

**REPLACEMENT:**

```markdown
letting the reader assume coverage. Neither author holds any other interest in the audited
method, and the authors declare no financial competing interests.

**A second interest, of a different kind.** The hierarchical partial-pooling design that §2.4
motivates and §5.9 evaluates is not ours. It was proposed to us by a researcher who is also a
co-author of the parent work and who is not an author of this paper. §5.9 reports a **negative**
result on that proposal, so we state its origin here rather than let a reader take both the design
and the negative as ours. We regard origination of a design at that specificity as a substantial
intellectual contribution rather than an acknowledgeable courtesy, and §5.9's verdict was reached
under the same pre-registered rules as every other verdict in §5.
```

That paragraph does three things the placeholder only promised: it names the conflict's *kind*, it
attaches it to the specific negative result, and it commits to the credit position the project has
taken. It decides nothing about the author list, because the author list is not this package's to
decide — see §11, item 1.

### 3.5 REPLACEMENT — Funding (closes the grant-identifier placeholder, line 2325)

**ANCHOR (DRAFT-v3 lines 2325–2330):**

```
**Funding.** ⟨To be completed by the authors with any grant identifiers.⟩ This work was
carried out as an MSc research project at LIACS, Leiden University, and received no
dedicated project funding; compute was drawn from the institutional allocation
acknowledged below. The absence of a compute budget is a scope limit rather than a
formality: it is the reason ImageNet-scale replication is out of reach (§7) and the reason
the additive tail experiment proposed in §9 is registered but unfunded.
```

**REPLACEMENT:**

```markdown
**Funding.** This work was carried out as an MSc research project at LIACS, Leiden University.
It received **no dedicated project funding and no grant**; the compute it consumed was drawn from
the institutional allocation acknowledged below. The absence of a compute budget is a scope limit
rather than a formality: it is the reason ImageNet-scale replication is out of reach (§7) and the
reason the additive tail experiment proposed in §9 is registered but unfunded.
```

The placeholder asked for grant identifiers. The paragraph's own next clause says there was no
dedicated funding, so the honest fill is a positive statement that there is no grant, not a
blank waiting for one. If a grant does apply, §11 item 2 is where to say so.

### 3.6 REPLACEMENT — Acknowledgements (closes the further-acknowledgements placeholder, line 2334)

The placeholder invites "any further acknowledgements". Nobody in the repository record is owed
one that is not already here, and inventing a courtesy is the same failure as inventing a grant
number, so the fill closes the placeholder by saying what the record supports and pointing at the
one debt that is deliberately recorded elsewhere.

**ANCHOR (DRAFT-v3 lines 2332–2336):**

```
**Acknowledgements.** This work was performed using the compute resources from the
Academic Leiden Interdisciplinary Cluster Environment (ALICE) provided by Leiden
University. We thank the ALICE support team. ⟨Any further acknowledgements to be added by
the authors; note that a contribution of idea origination is co-authorship, not an
acknowledgement — see Author contributions.⟩
```

**REPLACEMENT:**

```markdown
**Acknowledgements.** This work was performed using the compute resources from the
Academic Leiden Interdisciplinary Cluster Environment (ALICE) provided by Leiden
University. We thank the ALICE support team. One further debt is recorded under Competing
interests rather than here, deliberately: origination of a design that this paper then evaluates
is an intellectual contribution, and listing it as an acknowledgement would understate it.
```

### 3.7 REPLACEMENT — Author contributions (closes the CRediT and third-contributor placeholders, lines 2338 and 2350)

**ANCHOR (DRAFT-v3 lines 2338–2354), the whole paragraph from:**

```
**Author contributions.** Stated in CRediT terms. ⟨The author list is to be finalised by
```

through:

```
All authors accept accountability for the integrity of the work as a whole.
```

**REPLACEMENT:**

```markdown
**Author contributions.** Stated in CRediT terms.
**M. Ahmaditeshnizi** (LIACS, Leiden University) — Conceptualization (equal), Methodology,
Software (the chunkwise, 1-D-tensor, permuted-node and probe partitions and their identity tests,
as patches to the released MetaOptimize implementation), Validation, Formal analysis,
Investigation (all 2,173 runs), Data curation, Writing – original draft, Visualization, Project
administration.
**S. Salehkaleybar** (LIACS, Leiden University) — Conceptualization (equal), Supervision,
Resources, Funding acquisition, Writing – review & editing, and continuity with the parent work.
Explicitly **not** involved in setting the pre-registered decision rules or acceptance bands used
for the negative results in §5.
No one else contributed to this paper in a CRediT role. The one intellectual contribution that
came from outside this list — the hierarchical partial-pooling design of §2.4 and §5.9 — is stated
under Competing interests above, where its origin is also the second interest we have to disclose.
Both authors accept accountability for the integrity of the work as a whole.
```

Two things were **not** changed inside that paragraph, on purpose:

* **"Funding acquisition" is left on the supervising author's roles**, even though the Funding
  paragraph says there was no grant. Removing a CRediT role is a statement about a person's
  contribution and is not a production edit. It is §11 item 3.
* **The roles themselves are verbatim** apart from `all 2,113 runs` → `all 2,173 runs` (§6), and
  the affiliations, which are added because the markdown manuscript had no author block at all
  until §3.1 above.

### 3.8 REPLACEMENT — Correspondence (closes the correspondence placeholder, line 2374)

**ANCHOR (DRAFT-v3 line 2374), the whole line:**

```
**Correspondence.** ⟨author email⟩.
```

**REPLACEMENT:**

```markdown
**Correspondence.** `mohammadrezaahmaditeshnizi@gmail.com` (M. Ahmaditeshnizi).
```

This is the corresponding author's own address of record on this repository. It is a real,
working address, which is the whole requirement; it is not an institutional one, and §11 item 4
says so in one line in case the venue insists on one. An invented `@…leidenuniv.nl` address would
have looked more like a paper and been a fabrication.

### 3.9 One further edit in the same block, for C3

**ANCHOR (DRAFT-v3 line 2356), inside `**Use of AI assistance.**`:**

```
register, the figures and this draft were produced with substantial assistance from a
```

**REPLACEMENT:**

```markdown
register, the figures and this manuscript were produced with substantial assistance from a
```

---

## 4. P5 — the gate artefact: `defence` at line 1690

The gate's `infer_reporting_profiles_from_tex` routes a paper to Carlini's
adversarial-robustness checklist — threat model, adaptive attacks, undefended-system ablation — as
soon as any of 23 `_SECURITY_SIGNALS` matches. One of them is `defen[cs]es?\b`.

**Measured, not assumed.** All 23 signals were run over both files:

```
$ python3 - <<'X'   # the 23 patterns from paperfactory/agents/reporting_profile.py:1150
== paper/DRAFT-v3.md
    defen[cs]es?\b [(1690, 'defence')]
== paper/paper.tex
    defen[cs]es?\b [(2219, 'defence')]
X
```

**One match per file, and it is the same word.** Nothing else in the manuscript trips the profile:
no `attack`, no `threat model`, no `robustness` in the certified sense, no `security`. The pattern
does **not** match `defend` or `defensible`, so §1's *"the measurement we can defend"* and the
project's use of "defensibility" are safe and must not be changed.

**ANCHOR (DRAFT-v3 lines 1690–1691):**

```
`analysis/argsline_guard.py` is the corpus's only automated defence against the defect of §6.1, and
its file collector globs `<dir>/*.out` without descending, so it silently skips the twelve local
```

**REPLACEMENT:**

```markdown
`analysis/argsline_guard.py` is the corpus's only automated check against the defect of §6.1, and
its file collector globs `<dir>/*.out` without descending, so it silently skips the twelve local
```

`check` is the better word in any case: the sentence is about a tool that reads `ARGS:` lines, and
the paragraph's own next clause calls it "a guard with a stated limit". The same one-word change is
needed in `paper/paper.tex` at its own line 2219 — see §7.4.

---

## 5. P6 — the corpus-count refresh forced by commit `6a374f4`

### 5.1 Why this is in this package

`6a374f4` ingested `sm3`, `sm4`, `bm2` and `rp1` — 60 rows, 2,113 → 2,173, zero pre-existing rows
changed. The abstract prints the corpus size, so this package cannot rewrite the abstract without
settling it. Thirteen sites in the manuscript still print the pre-ingest numbers. **Eleven are
stale; two are now false**, in the sense that the sentence asserts something the data now
contradicts. No other package's item covers them.

The five paper-side constants in `analysis/c98_reproduce.py` were updated to match, because they
are the assertion of exactly these numbers:

```
$ python3 analysis/c98_reproduce.py > /dev/null; echo $?
0                                # was 1, with 5 CHECK(S) FAILED
$ python3 analysis/c98_reproduce.py | tail -3
ALL 188 CHECKS PASS.
```

Without that edit `analysis/c98_release.py` refuses to build the deposit at all (it exits on the
audit's non-zero return), so task (c) is not reachable without it.

### 5.2 The ledger, re-derived end to end

Every line below is a command that was run, not a number that was copied.

```
$ find runs runs_alice2 -name '*.out' | wc -l                              2241
$ # of those, files with an ARGS: line                                     2237   (4 without)
$ wc -l results/all_runs.csv                                          2174 (= 2173 rows + header)
$ 2237 - 2173                                                                64   crashed pre-epoch-1
```

The chain closes exactly: **2,241 `.out` − 4 infrastructure jobs = 2,237 that entered the training
script; − 64 that crashed before epoch 1 = 2,173 rows.** The 64 is unchanged from the pre-ingest
ledger, and the four ARGS-less files are still `gtest`, `gtest2`, `mo-smoke`, `ts-pretok`.

From the CSV:

| quantity | pre-ingest | now | how |
|---|---|---|---|
| rows | 2,113 | **2,173** | `len(rows)` |
| carrying a wallclock | 2,098 | **2,150** | `wallclock_min` non-empty |
| GPU-hours | 1,582.2 | **1,624.8** | `sum(wallclock_min)/60` |
| no readable `plateau5` | 25 | **25** | unchanged |
| `window_ok = 0` | 425 | **425** | unchanged |
| `window_ok = 1, complete = 0` | 17 | **24** | +7, all `rp1` |
| inadmissible, total | 442 | **449** | 25 + 400 + 24 |
| **admissible** | 1,671 | **1,724** | the gate of Eq. 11 |
| admissible GPU-hours | 1,515.9 | **1,558.4** | |
| GPU-h in the excluded rows | 66.3 | **66.3** | 1,624.8 − 1,558.4 = 66.35 |
| `.out` files on the two clusters | 2,193 | **2,241** | |
| runs with an `ARGS:` line | 2,189 | **2,237** | |
| runs with a repeated flag | 36 | **36** | `argsline_guard.py`, run unedited, over all 2,241 files |

The `argsline_guard.py` sweep is the registered tool run unedited on documented arguments (a list
of `.out` paths), which Rule 16 permits:

```
$ find runs runs_alice2 -name '*.out' -print0 | xargs -0 \
      python3 hierarchical-metaoptimize/analysis/argsline_guard.py --quiet | tail -2
argsline_guard: 2201 clean, 36 WITH REPEATED FLAGS OR DESIGN MISMATCH, 4 without an ARGS line
VERDICT: FAIL -- STANDING RULE 20
```

2,201 + 36 + 4 = 2,241, and the 36 are still exactly `ml2`'s 24 and `sm3`'s 12. **No new batch
carries a repeated flag.**

### 5.3 The two sites that are now FALSE, not merely stale

**(a) §3.3, line 458–459 — "None of the 17 is in a count-matched arm".** There are now 24, and
**seven of them are `permnode` arms** — `rp1-p101-s{10,11}`, `rp1-p202-s{10,11}`,
`rp1-p303-s{9,10,11}` — i.e. runs of the alignment contrast, caught mid-flight by the aggregator
at 82–87 of 100 epochs. They contribute no number to this paper, but the sentence as written is
no longer true.

**(b) §4.3, line 790–791 — "all 214 uniform-chunk, `nodewise1d` and `permnode` runs in the corpus
are admissible".** Now 256 such rows, of which **249** are admissible. Excluding the in-flight
`rp1` batch, it is **238 of 238**, which is the statement the paragraph actually needs — the
enumeration argument is about cells that could have been *lost to the gate*, and a batch still
running has not been lost to anything.

```
$ # rows whose granularity is chunk*, nodewise1d or permnode*
  all: 256   admissible: 249
  rp1: 18    admissible: 11
  excluding rp1: 238  admissible: 238
```

### 5.4 A third site that the `sm4` ingest falsified — Appendix A.1

**ANCHOR (DRAFT-v3 lines 2157–2158):**

```
partition-programme run in the corpus (367/367) is meta = Lion. **No meta-optimiser axis may be
reported.**
```

**REPLACEMENT:**

```markdown
partition-programme run behind the cells of Table 2 is meta = Lion, and the one batch that varies
the meta-optimiser is a single cell: of the 420 admissible runs in the partition families,
408 are meta = Lion and 12 are meta = RMSProp. **One cell is not an axis, and no meta-optimiser
axis may be reported.**
```

Two changes and one non-change. The count `367/367` is **dropped rather than restated**: it does
not re-derive under any definition of "partition-programme run" reconstructible from the CSV
(the natural one — `granularity` in {`nodewise`, `nodewise1d`, `chunk*`, `permnode*`} — gives 535
rows, 420 admissible), and A.7 sets the precedent that a number which will not re-derive is
dropped, not rephrased. The verdict **"no meta-optimiser axis may be reported" is kept**, because
it is still true and is still the point.

### 5.5 The remaining ten sites — mechanical substitutions

Apply in this order; each anchor is unique in the file.

| # | line | find | replace |
|---|---|---|---|
| 1 | 453 | `redundant: **17 of 2,113 runs pass \`window_ok\` while having completed under 95% of their` | `redundant: **24 of 2,173 runs pass \`window_ok\` while having completed under 95% of their` |
| 2 | 454 | `requested epochs** (16 of the 17 finished under 90%; the seventeenth stopped at 94 of 100).` | `requested epochs** (23 of the 24 finished under 90%; the twenty-fourth stopped at 94 of 100).` |
| 3 | 457–459 | `it moves that arm's mean by 1.22 pp and inflates its sem 19-fold. **None of the 17 is in a`<br>`count-matched arm** — see the attrition ledger in §8, where attrition inside the primary`<br>`contrasts is zero. Of 2,113 rows, **1,671 are admissible**.` | `it moves that arm's mean by 1.22 pp and inflates its sem 19-fold. **None of the 24 is in a count-matched arm of any cell reported in this paper; seven are truncated snapshots of the in-flight \`rp1\` batch (§3.5), which contributes no number here** — see the attrition ledger in §8, where attrition inside the primary contrasts is zero. Of 2,173 rows, **1,724 are admissible**.` |
| 4 | 786 | `also positive.** We verified this by enumeration rather than by recollection: of the 2,113 runs,` | `also positive.** We verified this by enumeration rather than by recollection: of the 2,173 runs,` |
| 5 | 790–791 | `have been lost to the admissibility gate: all 214 uniform-chunk, \`nodewise1d\` and \`permnode\` runs in`<br>`the corpus are admissible, and the sixteen batches involved contribute 272 runs of which 272 are` | `have been lost to the admissibility gate: all 238 uniform-chunk, \`nodewise1d\` and \`permnode\` runs in the corpus outside the in-flight \`rp1\` batch are admissible, and the sixteen batches involved contribute 272 runs of which 272 are` |
| 6 | 1611 | `job's actual \`ARGS:\` line afterwards. Swept over the 2,189 runs carrying an \`ARGS:\` line on both` | `job's actual \`ARGS:\` line afterwards. Swept over the 2,237 runs carrying an \`ARGS:\` line on both` |
| 7 | 2044 | `run a different experiment from the one it declares. Over the 2,189 runs carrying an` | `run a different experiment from the one it declares. Over the 2,237 runs carrying an` |
| 8 | 2279 | `**Data availability.** The complete run table (\`results/all_runs.csv\`, 2,113 rows), the` | `**Data availability.** The complete run table (\`results/all_runs.csv\`, 2,173 rows), the` |
| 9 | 2280 | `raw per-epoch Slurm logs (2,181 \`.out\` files, each carrying its own \`ARGS:\` and \`ENV:\` line),` | `raw per-epoch Slurm logs (2,241 \`.out\` files, each carrying its own \`ARGS:\` and \`ENV:\` line),` |
| 10 | 2344 | `2,113 runs), Data curation, Writing – original draft, Visualization, Project` | superseded by the Author-contributions replacement in §3.7, which already reads `all 2,173 runs` |

### 5.6 §8's five blocks

**(a) Table 3, the attrition ledger. ANCHOR (DRAFT-v3 lines 1899–1908).** Replace the table body
with:

```markdown
| stage | n | GPU-h | note |
|---|---|---|---|
| Slurm `.out` files on the two clusters | 2,241 | — | `runs/` + `runs_alice2/` + the on-cluster copies |
| — infrastructure jobs, no training | −4 | — | `gtest`, `gtest2`, `mo-smoke`, `ts-pretok`; no `ARGS` line, no CSV row |
| **jobs that entered the training script** | **2,237** | — | each logs one `ARGS` line |
| — crashed or cancelled before epoch 1 | −64 | ≈0 | itemised below; **not one logged a single epoch** |
| **rows in `results/all_runs.csv`** | **2,173** | 1,624.8 | 2,150 carry a wallclock |
| — no readable `plateau5` | −25 | } 66.3 | 2–5-epoch smoke tests |
| — `window_ok = 0`, `plateau5` present | −400 | } | budget ≤ 20 epochs; `window_ok` is `epochs_done > 20` |
| — `window_ok = 1`, `complete = 0` | −24 | } | truncated runs, 7 of them in-flight `rp1` snapshots; `complete` is `epochs_done ≥ 0.95 × requested` |
| **admissible** | **1,724** | 1,558.4 | the gate of Eq. 11 |
```

The `sm3` row — `| — completed but not yet ingested (`sm3`) | −12 | 10.1 |` — is **deleted**: `sm3`
is ingested (**B5**), and the ledger no longer has a hole to explain. The paragraph above the table
(line 1895–1897) keeps its "exclusions applied in the order shown" note verbatim; the order and the
25/400 split are unchanged.

**(b) The paragraph introducing the deposit's log set. ANCHOR (DRAFT-v3 lines 1883–1885):**

```
is the authority on what that run actually did. The shipped log set is 2,181 files; the two
clusters together hold 2,189 with an `ARGS:` line, plus the 12 un-ingested `sm3` runs, and we
state the shortfall rather than the shipped count alone.
```

**REPLACEMENT:**

```markdown
is the authority on what that run actually did. The shipped log set is **2,241 files, which is
every `.out` file on either cluster**: 2,237 with an `ARGS:` line and the four infrastructure jobs
that have none. There is no shortfall to state, and the `sm3` runs that an earlier version of this
ledger carried as un-ingested are in the run table.
```

**(c) The inadmissible-rows paragraph. ANCHOR (DRAFT-v3 lines 1932–1937):** substitute
`442 → 449` (three occurrences), `17 → 24` (one), and extend the granularity census, which now
reads, re-derived:

```
layerwise 136, weightwise 111, nodewise 108, resnet18_blocks 56, scalar 30,
permnode 7, no-partition baseline 1        (total 449)
```

so the sentence becomes `… the 449 are: \`layerwise\` 136, \`weightwise\` 111, \`nodewise\` 108,
\`resnet18_blocks\` 56, \`scalar\` 30, \`permnode\` 7 (the in-flight \`rp1\` snapshots),
no-partition baseline 1 …`.

**(d) The Compute paragraph. ANCHOR (DRAFT-v3 line 1954):** `2,098 runs carry a wallclock; they
total **1,582 GPU-hours**` → `2,150 runs carry a wallclock; they total **1,625 GPU-hours**`.
"29 distinct nodes" is unchanged and still PASSes.

**(e) Appendix A.8. ANCHOR (DRAFT-v3 lines 2212–2215):**

```
**A.8 — Corpus size.** The record variously says 1,960 / 2,077 / 2,113 runs and ~1,200–1,400
GPU-hours. At write time: **2,113 rows, 1,671 admissible, 1,582 GPU-hours** summed over the 2,098
runs carrying a wallclock, with 2,189 jobs having entered the training script and 12 completed
`sm3` runs awaiting ingest (§8, Table 3). The correction register runs to entry 126.
```

**REPLACEMENT:**

```markdown
**A.8 — Corpus size.** The record variously says 1,960 / 2,077 / 2,113 runs and ~1,200–1,400
GPU-hours. At write time: **2,173 rows, 1,724 admissible, 1,625 GPU-hours** summed over the 2,150
runs carrying a wallclock, with 2,237 jobs having entered the training script and nothing awaiting
ingest (§8, Table 3). The correction register runs to entry 127.
```

---

## 6. P4 — the deposit, prepared so that a DOI can be minted

### 6.1 What was rebuilt, and what it now says

```
$ python3 analysis/c98_release.py
[1/6] regenerating figures
[2/6] running the reproduction audit
[3/6] copying data, code, scripts, patches, figures, docs
[4/6] archiving the raw per-epoch .out logs
[5/6] writing README, ENVIRONMENT, Makefile, CITATION
[6/6] writing MANIFEST.md5
release/ built: 137 files, 6.2 MB

$ cd release && make verify
137 files checked, 0 bad

$ make reproduce; echo $?
ALL 188 CHECKS PASS.
0
```

The builder **refuses to finish if the audit returns non-zero** (`c98_release.py`, "REFUSING TO
BUILD"), which is why §5's constant update had to land first. The deposit carries
`data/all_runs.csv` (2,173 rows), `logs/raw_out.tar.gz` (**2,241** `.out` files, 15.2 MB
uncompressed), the fourteen registered scorers including `c97_bm2_score.py`, `c97_rp1_score.py`
and `c97_sm4_score.py`, every submission script in `scripts/`, the optimiser patches and their
identity tests, the four figures, five `docs/` files, `REPRODUCTION-AUDIT.txt` and
`MANIFEST.md5`.

### 6.2 Four changes to the deposit's own text (`analysis/c98_release.py` templates)

1. **The README's DOI paragraph** no longer promises one. It now reads: *"**DOI: not yet minted.**
   This deposit is assembled, self-verifying and ready to upload; nobody has deposited it yet, so
   there is no DOI to print and none is printed. Cite this artefact by its repository commit … until
   one exists."*
2. **`CITATION.cff` has an `authors:` block** (it had none, which makes a CFF file invalid) and
   **no `identifiers:` block at all**. In its place is a commented-out template plus the reason:
   *"Rather than print a placeholder that a parser could mistake for one, the field is absent."*
   ORCIDs are omitted rather than guessed, with a comment saying so.
3. **A generated "headline numbers" block.** The README used to paste the audit's first eight
   lines. It now carries thirteen named headline lines — corpus size, admissible rows, GPU-hours,
   16/16 cells, the 11-cell pool, the SGDm pool and its Q, the alignment null and both CI ends, and
   the three numbers behind the 1.807 pp deficit — cut out of `REPRODUCTION-AUDIT.txt` **by the
   build script at build time**. A key that stops matching is skipped, never faked. This is the
   "README that reproduces the headline numbers" the task asks for, and it cannot drift from the
   CSV because nothing in it is typed.
4. **A `## Minting the DOI` section**, five numbered steps: drop the final manuscript in, verify
   and reproduce on a clean checkout, upload and reserve, write the string into exactly three
   places (README, `CITATION.cff`, the paper's Data-availability statement), rebuild so the
   manifest covers the edits. It ends: *"Steps 2 and 3 are the author's to take: they require an
   archive account and they publish a permanent public record."*

The two draft-internal phrases the deposit was shipping — *"withdrawn from an earlier draft"* and
*"before camera-ready"* — are gone from the templates and from the rebuilt files.

### 6.3 What is honestly still missing before a DOI exists

* **The build stamped `DIRTY`.** `release/README.md` says, because the builder detected uncommitted
  changes: *"The working tree was DIRTY at build time; re-build from a clean checkout before
  minting the DOI."* That is correct and must not be edited out — several packages have the tree
  open. Rebuild after the integration commit.
* **The manuscript is not in the deposit.** Step 0 of the minting procedure says so and says why.
* **A2's gap is not closed by this package.** Six of the fourteen scorers cannot run against the
  deposit because the ≈42 GB of probe traces are excluded; the audit now prints that as a register
  (`REACHED 2 / PARTIAL 2 / BLOCKED 6`). Shipping the kilobyte-scale occupancy summary is A2's fix,
  and until it lands the deposit does not regenerate every quoted verdict.

---

## 7. The same replacements in LaTeX, for `paper/paper.tex`

`paper/paper.tex` is the latex package's file and is being written live. These are the same edits,
keyed to text anchors so they survive the line numbers moving.

### 7.1 The abstract

Replace everything between `\begin{abstract}` and `\end{abstract}` with:

```latex
MetaOptimize \citep{sharifnassab2025metaoptimize} meta-learns one step size per parameter group
and reports that finer partitions help inconsistently. That inconsistency has never been
separated from the group \emph{count}, so the partition's contribution remains unmeasured. We
hold the count fixed and swap an architecture-aligned partition (one step size per output
channel) for uniform chunks, over 2{,}173 runs on CIFAR-10 and CIFAR-100 with ResNet-18,
ResNet-34 and ResNet-50, every contrast taken within one submission, so batch effects cancel.

The uniform partition wins in every count-matched cell we measured. Pooled over the eight SGDm
cells the effect is $+0.556 \pm 0.045\pp$ and homogeneous there (Cochran $Q$ 4.21 on 7 df), while
cells that differ in base optimiser are strongly heterogeneous. Alignment itself is a bounded
null: at fixed count and fixed size multiset, permuting which weights share a group is worth
$-0.009 \pm 0.157\pp$, 95\% CI $[-55\%, +51\%]$ of it. Of nine candidate mechanisms, none
survives as a general carrier, and we report all nine.

Scope, stated here rather than deferred. The corpus is CIFAR-resolution vision, and a Lion
meta-optimiser carries every count-matched cell but one. Every accuracy is a test-set quantity
with no held-out validation split. The effect is ${\approx}0.6\pp$ inside a method trailing tuned
cosine by 1.8--4.2\pp. This should be read as a constraint on partition design, not as support
for practitioners.
```

Note for the latex package: the gate counts abstract words **after** `_strip_latex_commands`, which
deletes `\citep{...}` entirely, so the LaTeX form scores **217 words** against the same 230 cap — more
headroom than the markdown, not less. Do not spend it.

### 7.2 The `\paragraph{Reproducibility convention.}` block

That block (immediately after `\end{abstract}`) is the LaTeX rendering of the deleted
`**Draft v3.**` paragraph. **Delete it**, for the reasons in §2.1, and move its companion —
the `\paragraph` beginning *"Every pooled estimate, Cochran"* — into §3.3 with the run-in heading
`\paragraph{The precision every pooled quantity is computed at.}`.

### 7.3 The author block

Replace:

```latex
\author{%
  M.\ Ahmaditeshnizi\thanks{LIACS, Leiden University. Correspondence:
  $\langle$author email$\rangle$.} \and S.\ Salehkaleybar$^{*}$%
}
```

with:

```latex
\author{%
  M.\ Ahmaditeshnizi\thanks{LIACS, Leiden University, the Netherlands.
  Correspondence: \texttt{mohammadrezaahmaditeshnizi@gmail.com}.}
  \and S.\ Salehkaleybar\footnotemark[1]%
}
```

(`\footnotemark[1]` rather than `$^{*}$`: with `\thanks` the first footnote is numbered, and a
bare star does not point at it.)

### 7.4 The remaining four

| anchor text in `paper.tex` | change |
|---|---|
| `An earlier draft of this paper claimed four refutations` … | replace the sentence with §2.2's replacement, in LaTeX |
| `An earlier draft claimed both, and that was wrong.` | replace with §2.3's replacement |
| `the corpus's only automated defence against the defect of` | `defence` → `check` (line 2219 at the time of writing) |
| every corpus count in §5.5 and §5.6 above | apply the same substitutions; `2{,}113` → `2{,}173` etc. |

---

## 8. Every number this package changes, and where it came from

| # | number, before → after | where it appears | re-derivation |
|---|---|---|---|
| 1 | 2,113 → **2,173** rows | abstract, §1, §3.3 ×2, §4.3, §8 ×3, A.8, CRediT | `len(list(csv.DictReader(open('results/all_runs.csv'))))`; audit `[1] CORPUS` PASS |
| 2 | 1,671 → **1,724** admissible | §1, §3.3, §8 Table 3, A.8 | `window_ok==1 AND complete==1 AND plateau5 readable`; audit PASS |
| 3 | ≈1,582 → **≈1,625** GPU-h | §1, §8 ×2, A.8 | `sum(wallclock_min)/60 = 1624.767`; audit PASS at `%.0f` |
| 4 | 2,098 → **2,150** with a wallclock | §8 ×2, A.8 | non-empty `wallclock_min`; audit PASS |
| 5 | 1,515.9 → **1,558.4** admissible GPU-h | §8 Table 3 | same sum over admissible rows; 1,624.8 − 1,558.4 = 66.35, so the table's `} 66.3` bracket is unchanged |
| 6 | 17 → **24** truncated rows | §3.3 ×2, §8 Table 3, §8 inadmissible ¶ | `window_ok==1 AND complete!=1 AND plateau5 readable`; audit `rows failing complete` PASS. The seven new ones are `rp1-p{101,202,303}-s{9,10,11}` at 82–87 of 100 epochs |
| 7 | 16 of 17 → **23 of 24** finished under 90% | §3.3 | epochs_done of the 24: only `rs-node-1e4-s1` (94/100) is ≥ 90% |
| 8 | 442 → **449** inadmissible | §8 ×3 | 25 + 400 + 24 |
| 9 | granularity census of the inadmissible rows | §8 | `layerwise` 136, `weightwise` 111, `nodewise` 108, `resnet18_blocks` 56, `scalar` 30, **`permnode` 7**, `?` 1 = 449 |
| 10 | 2,193 → **2,241** `.out` files | §8 Table 3, End matter | `find runs runs_alice2 -name '*.out' | wc -l` |
| 11 | 2,189 → **2,237** with an `ARGS:` line | §6.1, §7, §8 Table 3, A.8 | 2,241 − 4 (`gtest`, `gtest2`, `mo-smoke`, `ts-pretok`); `argsline_guard.py` reports "4 without an ARGS line" |
| 12 | 2,181 → **2,241** shipped log files | End matter, deposit README | the builder archives every `.out` on both clusters; `release/README.md` prints 2241, generated |
| 13 | 64 crashed pre-epoch-1 | **unchanged** | 2,237 − 2,173 = 64 |
| 14 | 36 runs with a repeated flag | **unchanged** | `argsline_guard.py` over all 2,241 files: "2201 clean, 36 WITH REPEATED FLAGS" — still `ml2` 24 + `sm3` 12 |
| 15 | 425 `window_ok = 0`, 25 without `plateau5` | **unchanged** | audit PASS both |
| 16 | 214 → **238** count-matched-family rows, all admissible | §4.3 | rows with `granularity` in {`chunk*`, `nodewise1d`, `permnode*`} = 256, admissible 249; **excluding `rp1`: 238 of 238** |
| 17 | 367/367 meta = Lion → **408 of 420** | scope (iii), A.1 | admissible rows in the partition families {`nodewise`, `nodewise1d`, `chunk*`, `permnode*`} = 420: **408 Lion, 12 RMSProp** (all 12 are `sm4`). The number 367 does not re-derive under any reconstructible definition and is dropped, per A.7's precedent |
| 18 | ≈6 MB → **6.2 MB** in 137 files | §8, End matter | `head -1 release/MANIFEST.md5` → "137 files, 6.2 MB"; `make verify` 137/137 |
| 19 | "entry 126" → **"entry 127"** | A.8 | `grep -n '^## 12' docs/CORRECTIONS.md` → 127 is the highest |
| 20 | ResNet-10/18/34/50 → **ResNet-18/34/50** in the abstract (**B6**) | abstract | networks of the count-matched family rows: ResNet18 199, ResNet34 27, ResNet18_c100 13, ResNet50 9, ResNet18_gn 8. **No ResNet-10.** The corpus at large has 110 ResNet-10 rows and 1 ResNet-101, which is why §1 keeps the longer list attached to the word "corpus" |
| 21 | "88% … one identified moderator" | **not relocated** — left as the marked slot of §1.3b-bis (**B1**) | not re-derived because not restated. If neither `calibration` nor `new-results` lands, the fallback text drops the clause outright. The audit still asserts `share of the live Q that is between-base 88.4` for §4.4, which is B1's section, not this one |
| 22 | 16 count-matched cells, Q 36.4 on 10 df | **not printed** in the new abstract | `new-results` derives 20 cells and a 14-cell pool at Q 102.47/13; `calibration` derives a 13-cell pool at Q 55.40/12. Nothing this package prints depends on which lands |

Numbers **quoted but not changed**, and therefore carrying their existing verification: every
Table 2 D/se pair, the 11-cell pool and its Q/τ, the SGDm pool +0.556 ± 0.045 with Q 4.21/7, the
alignment null and both CI ends, +0.590 ± 0.107, +0.115 ± 0.133, +0.514 ± 0.056, +0.047 ± 0.124,
93.317 / 95.124 / 1.807, 2.56 and 4.21. All are in the 188-check audit or in §7 T4, and all PASS.

---

## 9. Verification actually run

| what | command | result |
|---|---|---|
| the abstract against the gate's own module | `_abstract_defects(clean_abstract_text(...))` from `paperfactory/agents/text_quality.py` | markdown **227 words, DEFECTS: NONE**; LaTeX form **217 words, DEFECTS: NONE**. The three cascade defects the 922-word block caused — missing structured moves, unsupported final stance, overloaded Results sentence — are all clear |
| the security-signal sweep | all 23 `_SECURITY_SIGNALS` patterns over both files | exactly one match each, `defence` |
| the corpus ledger | `find`, `csv.DictReader`, `argsline_guard.py --quiet` | §5.2, closes exactly: 2,241 − 4 − 64 = 2,173 |
| the reproduction audit | `python3 analysis/c98_reproduce.py; echo $?` | **`ALL 188 CHECKS PASS.` exit 0** (was exit 1 with 5 failures) |
| the deposit | `python3 analysis/c98_release.py`, then `make verify`, `make reproduce` | 137 files / 6.2 MB; **137 checked, 0 bad**; audit exit 0 |
| the ⟨…⟩ census | `grep -n '⟨' paper/DRAFT-v3.md` | 6 before; **0 after** the six replacements of §3 |
| `camera-ready` census | `grep -n -i camera` | 1 in the manuscript, 2 in the deposit; **0 after** |
| "earlier draft" census | `grep -n -i 'earlier draft'` | 3 in the manuscript, 1 in the deposit; **0 after** |

---

## 10. Integration dependencies and collision notes

**One external dependency, and it is satisfied by a package that has already delivered.**

1. **"Of nine candidate mechanisms"** (abstract, and "nine candidate mechanisms" in §1's third
   block). The `new-results` package adds M9 — `sm4`'s pre-registered refutation of a
   second-moment normaliser *anywhere* in the loop — and rewrites §5's heading to
   `## 5. Nine candidate mechanisms — four refuted — and two nulls`. **Checked in that package's
   text, not assumed.** If `new-results` is dropped, change the one word to `eight` in both places;
   the abstract's word count is unaffected. Tripwire: `grep -c 'Eight candidate' paper/DRAFT-v3.md`
   at integration time.

**Two dependencies that were designed out rather than flagged.** The abstract prints neither a
Table 2 cell count nor a cross-cell pooled Q, because `new-results` moves Table 2 to 20 cells and
the contrast pool to 14, `calibration` moves the same pool to 13, and the two disagree. See §1.2
property 4 and §1.3b-bis. Everything the abstract does print survives both.

**Collisions, by package:**

| other package's item | overlap | how this package avoids it |
|---|---|---|
| **A2** (§8 deposit guarantee) | shares the End matter's Data-availability paragraph, and `analysis/c98_reproduce.py` already carries A2's scorer-coverage register | this package replaces **only** the `DOI: pending` sentence inside that paragraph (§3.3) and the two counts in its first two lines (§5.5 rows 8–9). It does **not** touch *"No number in this paper requires data that is not in that deposit"*. If A2's rewrite has already replaced those strings, skip those three edits — they are string-exact, so a failed `grep` is the signal |
| **A8** (`c98_reproduce.py` asserts every number) | shares that file, and the header block | this package changed five `paper=` constants in `[1] CORPUS` only; A8's work adds `chk(` sites elsewhere. Deleting the header block removes one of A8's two false sites; **the §3.4 sentence is still A8's** |
| **B1** (the 88% is label-invariant) | shares the abstract | the new abstract makes no moderator claim, and the relocated §1 block deletes the 88% clause. **Contribution 3 and the Conclusion are still B1's** |
| **B3** (practical significance) | shares scope item (iv) | (iv) is relocated verbatim into §1 and still unanswered. B3's paragraph should attach to it there |
| **B6** (ResNet-10 in the abstract) | **closed by this package**; `calibration` also closes it, with EDIT B6-a | that edit rewrites the *old* abstract's opening sentence and is **superseded**: the new abstract already reads ResNet-18, -34, -50, and the wider list survives in §1 attached to the word "corpus" (§8 row 20). Applying both would leave two opening sentences |
| **`calibration`** (B1, B2, B3) | EDITs B1-a, B2-b and B3-b are all keyed to strings **inside the abstract**, which this package moves to §1 | the strings are relocated **unchanged**, so those three edits still apply at their new location. §1.3b-bis gives the rule for the one slot where `calibration` and `new-results` collide with each other |
| **`new-results`** (`sm4`, `bm2`) | supplies M9 (this package's only dependency), grows Table 2 to 20 cells, repools §4.4 over 14 cells, and moves the same corpus counts this package's §5 moves | the corpus counts agree exactly — both derive 2,173 / 1,724 / ≈1,625 from the same CSV. The cell counts and pooled Q are **not** printed by this package's abstract, by construction |
| **B5** (`sm3` ingest) | already closed at `6a374f4`; this package removes the last three places the manuscript still says otherwise (§8's ledger row, §8's log paragraph, A.8) | |
| **latex package** (`paper.tex`) | shares every edit | §7 restates them in LaTeX against text anchors. `paper.tex` was **not** edited by this package |
| **A3** (`dup_group` census) | `results/all_runs.csv` was modified in the working tree by `args_repair.py` while this package ran | none of the counts in §5.2 depends on `dup_group`; they were re-derived after that change and the audit passes with it |

**Order of application.** §2.1 (delete the header block) must precede §3.1 (insert the author
block), because they occupy the same lines. §1.2 (the abstract) must precede §1.3 (the relocation),
because the relocation's source text is inside the block §1.2 deletes. Everything else is
order-independent.

---

## 11. TODO-FOR-AUTHOR

Seven decisions that cannot be taken from the repository. They are **not** placeholders in the
manuscript: every one of them has finished prose in place that is true of the paper as it stands,
and each item below says exactly what to edit if the answer changes. This list is mirrored verbatim
into `docs/STATUS.md`.

| # | decision | what the paper says now | if the answer changes |
|---|---|---|---|
| 1 | **Does the originator of the hierarchical partial-pooling design join the author list?** `docs/PLAN-appendix-collab.md` line 133 names him — *"Arsalan — co-author, not acknowledgement. He originated the hierarchical partial-pooling idea … Being at a non-partner institution affects paperwork, not credit"* — i.e. a co-author of the parent paper. This package did **not** put that name into the manuscript: an author list is a decision, and the source is an internal advisory note. | Two authors. Competing interests discloses that the §5.9 design came from *"a researcher who is also a co-author of the parent work and who is not an author of this paper"*, and that §5.9 is negative about it. | Add him to the author block (§3.1) and to CRediT with Conceptualization for §2.4/§5.9; **add a second sentence to Competing interests naming a second co-author of the audited method among the authors**; obtain his affiliation and ORCID from him. |
| 2 | **Is there any grant to declare?** | *"It received no dedicated project funding and no grant."* | Replace that clause with the funder and grant identifier. Do not add one that is not real. |
| 3 | **`Funding acquisition` is on the supervising author's CRediT roles while Funding says there was no grant.** Left untouched: removing a role is a statement about a person's contribution. | Both stand as written. | Either drop the role, or (if the institutional compute allocation is what it refers to) say so in Funding. |
| 4 | **Correspondence address.** The address used is the corresponding author's own address of record on this repository, not an institutional one. | `mohammadrezaahmaditeshnizi@gmail.com` | Substitute the LIACS address if the venue requires an institutional one. One string, three files: DRAFT-v3 End matter, `paper.tex` `\thanks`, and nothing else. |
| 5 | **ORCIDs.** Omitted rather than guessed. | `CITATION.cff` has an `authors:` block with names and affiliations and no `orcid:` fields, and a comment saying why. | Add `orcid: "https://orcid.org/…"` under each author and rebuild the deposit. |
| 6 | **Mint the DOI.** Steps 2 and 3 of `release/README.md`'s *Minting the DOI* need an archive account and publish a permanent public record, so they are not automatable from here. | The paper prints **no DOI** and identifies the artefact by commit; `CITATION.cff` has no `identifiers:` block. | Reserve the DOI, then write the same string into three places: `release/README.md`, `CITATION.cff`, and the paper's Data-availability statement. Rebuild so `MANIFEST.md5` covers the edits. |
| 7 | **Rebuild the deposit from a clean checkout.** | `release/README.md` carries the builder's own warning that the tree was dirty at build time. | After the integration commit, re-run `python3 analysis/c98_release.py` and `cd release && make verify`. |

Items 1 and 6 are the only two that block submission. Items 2–5 and 7 are one-line edits.

---

## 12. What this package deliberately did not do

* It did not answer **B3**. Scope item (iv) still volunteers the practical-significance objection
  and still does not answer it; it has only moved from the abstract to §1.
* It did not touch **A1** (the ρ superlative), **A2** (the deposit guarantee sentence), **A3–A7**,
  **B1**'s Contribution 3 and Conclusion, **B2** or **B4**.
* It did not add an Appendix A entry for the §7 T9 correction (§2.3). Appendix A registers numbers
  from the internal record that failed to re-derive; a sentence that overstated what a pairing
  cancels is not one, and the limit itself is now stated in the sentence that carries the reading.
* It did not name the third contributor in the manuscript (§11 item 1).
* It did not commit anything.
