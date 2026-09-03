# v9-plan — R9: the main-body / appendix split, decided from measurement

**Scope.** R9 only. This file is a plan and a set of measurements; it edits neither
`paper/paper.tex` nor `paper/DRAFT-v4.md`. Every number below was produced by a command
recorded in §0 and re-derived at write time. Nothing here is quoted from a briefing,
from `docs/STATUS.md` or from any prose.

---

## VERDICT (read this first)

**DO NOT restructure to a 12–15 pp main body.** The target is not reachable by
reorganisation; reaching it requires roughly **7,600 words of new summary prose** carrying
several hundred re-derived numerals, which is a rewrite, which is exactly what the
instruction forbids and exactly what puts the eight green checks at risk.

**DO NOT execute the intermediate, renumber-free move either — not as a first action.**
It is technically clean and I cost it in full below (Plan B), but it lands the main body at
**≈ 44–48 pp**, not 15, and it forces a change to the one number the manuscript asserts
about *itself* (§3.4's coverage census) for a reason that is a regex bug rather than a
result. The goodwill bought at 46 pp is small; the surface opened is 109 unchecked
cross-reference edits plus a forced census fixpoint.

**DO execute Plan C: signposting in place.** A reader's guide and evidence map after
§1.1, a one-line "what this section is for / skip unless" opener on the eight long
subsections, and an appendix-style pointer at each long block. Measured cost: **zero moved
blocks, zero renumbering, zero `\label`/`\ref` churn, and the asserted census stays at
892** (verified by simulation, §5.4). It captures most of the reviewer-burden benefit —
a referee who can find any piece of evidence in one step does not experience 75 pp as 75 pp
— at a risk that is close to zero.

**One separable defect found while measuring, worth fixing on its own merits regardless of
R9:** §3.4's coverage census silently ignores the last **667 lines (16.4 %)** of
`DRAFT-v4.md`. See §5. It is not blocking, it is not a science error, and it is *not* part
of Plan C. It is written up here because it is the thing that makes any restructure
numerically non-neutral, and because a referee who re-runs the census as §3.4 invites them
to will find it.

---

## 0. How everything below was measured

```
pdftotext -layout paper/paper.pdf  -> page-accurate section spans and word counts
python3 analysis/c98_reproduce.py                 -> exit 0, ALL 636 CHECKS PASS
                                                     census 628 / 409 / 892 / 45.9 %
python3 analysis/paper_numeric_diff.py            -> 8 residuals (3 tex-only, 5 md-only)
```
plus four purpose-written probes over `paper.tex` and `DRAFT-v4.md`:
a heading/word/float counter, a `\label`↔`\ref` crossing matrix, a literal-cross-reference
counter for the Markdown, and a census-invariance simulator that feeds `c98_reproduce.census()`
mutated copies of the draft in the scratchpad. Baseline re-confirmed green before and
during this work: `c98_reproduce.py` exit 0 / 636 PASS, numeric diff at the same 8
residuals, byte for byte.

---

## 1. MEASUREMENT — the actual size of every section

Pages are from the compiled 75-pp PDF (start page of the heading to the page before the
next heading). Words are PDF words, i.e. what a reader reads, floats included. `T`/`F` are
`table` / `figure` environments whose `\begin` sits in that span.

| § | title | pages | pp | PDF words | T | F |
|---|---|---|---|---|---|---|
| 1 | Introduction (incl. title, abstract, §1.1 Contributions) | 1–4 | **4** | 2,984 | 0 | 0 |
| 2 | Related work, and what is left | 5–7 | **3** | 1,674 | 1 | 0 |
| 3 | Method and experimental setup | 8–17 | **10** | 7,045 | 2 | 0 |
| 4 | Results | 18–40 | **23** | 15,959 | 2 | 3 |
| 5 | Nine candidate mechanisms | 41–53 | **13** | 8,340 | 3 | 1 |
| 6 | Measurement discipline | 54–55 | **2** | 1,380 | 0 | 0 |
| 7 | Threats to validity | 56–61 | **6** | 4,581 | 0 | 0 |
| 8 | Reproducibility | 62–65 | **4** | 2,719 | 2 | 0 |
| 9 | Conclusion | 66–67 | **2** | 1,606 | 0 | 0 |
| | **body total** | 1–67 | **67** | **46,288** | 10 | 4 |
| A | Discrepancy register | 68–69 | 2 | 1,520 | 0 | 0 |
| B | Full arm table + End matter | 70–72 | 3 | 1,768 | 1 | 0 |
| | References | 73–75 | 3 | 1,148 | — | — |
| | **document** | | **75** | **50,724** | 11 | 4 |

### 1.1 Where the mass actually is (subsection level, measured — not guessed)

| unit | pages | PDF words | share of body |
|---|---|---|---|
| **§4.4** heterogeneity + moderator + endpoint sensitivity | 22–32 | **6,634** | **14.3 %** |
| §4.6 + §4.6.1 + §4.7 (alignment, replication, prescription) | 32–38 | 4,540 | 9.8 % |
| **§5.4** the tail as a universal carrier | 44–50 | **3,448** | 7.4 % |
| §3.5 four pre-registered batches | 15–18 | 2,702 | 5.8 % |
| §8 Reproducibility | 62–66 | 2,807 | 6.1 % |
| §3.3 metric, admissibility, multiplicity | 10–13 | 2,654 | 5.7 % |
| §7.2 limits of the review process | 59–62 | 2,354 | 5.1 % |
| §4.8 budget | 38–41 | 2,292 | 5.0 % |
| §7.1 limits of the included evidence | 56–59 | 1,795 | 3.9 % |
| §4.3 the primary + Table 2 + Figure 1 | 20–22 | 1,388 | 3.0 % |
| §3.4 registration discipline | 13–15 | 1,282 | 2.8 % |
| §2.4 + §2.5 (CAM-HD and the tensor-rule survey) | 6–8 | 1,241 | 2.7 % |
| §5.8 configuration-property null | 52–53 | 1,101 | 2.4 % |
| §6.1 … §6.4 all four | 54–56 | 1,745 | 3.8 % |
| everything else (24 further subsections) | — | 8,900 | 19.2 % |

**Two facts fall straight out of this table.**

1. **One subsection, §4.4, is 11 pages and 14.3 % of the body.** It is bigger than §2, §6,
   §8 and §9 put together. If anything is "the long section", it is §4.4, and it is the one
   section carrying Contribution 3.
2. **There is no fat tail to cut.** After the top four units the distribution is flat: 24
   subsections share the last 19 %. That is why "move the long sections" does not produce a
   15-pp paper — there is no small set of long sections to move.

---

## 2. MEASUREMENT — what 12–15 pp actually costs

Density of the current body: 46,288 words / 67 pp = **691 words per page**.

A 15-pp main body must carry, at minimum, Table 2 (≈ 1.3 pp, 20 rows), Figures 1–3
(≈ 1 pp each) and the reference list is excluded from the count — call it **4 pp of floats**.
That leaves **11 pp of prose = ≈ 7,600 words**.

- Body prose today: **46,288 words.**
- Main-body prose allowed at 15 pp: **≈ 7,600 words.**
- **Words that must leave the main body: ≈ 38,700 — 84 % of the body.**

Now the part that decides it. The argument the main body must still carry on its own is:
the design and the count-matching; the primary result in 20 cells; the moderator and its
rival; the alignment null and its replication; the prescription and its scope; the budget
reversal *and its four guard sentences*; the nine mechanisms and why none survives; the
threats; the audit. **Nine strands. 7,600 words is ≈ 840 words per strand.**

The current text of any one of those strands is 2,300–6,600 words. You cannot get a strand
from 6,600 words to 840 by moving material — a pointer is not an argument. You get there by
**writing a new digest**, and a digest of this paper's strands is not prose, it is numbers:
the moderator digest alone has to restate η², rank, the exact-enumeration p, the four
base-level pools and the between-base Q share.

Measured consequence of writing those digests:

- `paper_numeric_diff.py` is a **multiset** comparison. Every numeral in the new digests
  must appear the *same number of times* in `paper.tex` and in `DRAFT-v4.md`. The current
  residual set is 8; all 8 are exactly this failure mode (a number that landed in one
  markup and not the other). Adding ≈ 7,600 words of number-dense new prose to both files
  is the single highest-yield way to manufacture new residuals.
- Every restated number is a fresh opportunity to contradict `c98_reproduce.py`'s 636
  assertions, and a fresh census fixpoint (§5).
- **This is a rewrite.** The task statement forbids it: *"THIS IS A REORGANISATION, NOT A
  REWRITE. NO NUMBER MAY CHANGE."* Those two constraints — 15 pp, and no new prose — are
  mutually unsatisfiable on this manuscript. I am reporting that rather than picking one.

**Conclusion of §2: the 12–15 pp target is refused on arithmetic, not on taste.**

---

## 3. MEASUREMENT — the cross-reference surface (the real cost of any move)

### 3.1 `paper.tex` — cheap

- **74 `\label`s, 550 `\ref`/`\autoref` uses, 0 dangling.**
- Every one is symbolic. LaTeX renumbers them for free. A section that moves under
  `\appendix` renders as "Appendix C.4" with no edit.
- **9 literal `\S7.1`-style strings** exist and they all point at the *parent* paper
  (`paper.tex:97, 99, 101, 348, 354, 357, 358, 360, 362`). They must never be renumbered.
  In the `.tex` they are trivially distinguishable: `\S<digit>` = MetaOptimize's section,
  `\ref{}` = ours.
- Cost of a move in `paper.tex`: reorder blocks, place `\appendix`. Near zero.

### 3.2 `DRAFT-v4.md` — expensive, and unchecked

| hand-maintained cross-reference strings in `DRAFT-v4.md` | count |
|---|---|
| `§N` / `§N.M` / `§N.M.K` | **461** |
| `Table N` / `Figure N` / `Appendix A.N` / `Appendix B` | **86** |
| **total literal, hand-maintained** | **547** |

The Markdown has no `\ref`. Every one of those 547 strings is typed. And:

- **`§4.4` alone is referenced 64 times, `§7` 61 times, `§4.8` 24 times, `§4.3` 21 times,
  `§6.1` 21 times, `§5.5` 20 times, `§8` 19 times, `Table 2` 44 times.**
- **Nine of the 461 point at the parent paper, not at us** — `§7.1`, `§7.2` (×2), `§7.3`
  (×2), `§7.5`, `§9` and two more, at `DRAFT-v4.md:41, 43, 45, 250, 254, 257, 258, 260`.
  In the Markdown they are **typographically identical** to a reference to our own §7
  (Threats), which is referenced 61 times. A `sed` over `§7` corrupts all nine.
- **NO REGISTERED CHECK CAN SEE A MISTAKE HERE.** This is the finding that matters most
  for risk. `paper_numeric_diff.py` calls `_XREF`, which *deliberately excludes* any
  numeral preceded by `§`, `Table `, `Figure `, `Appendix `. `c98_reproduce.py`'s census
  excludes them for the same reason. So a `§4.4` that should have become `§C.2`, or a
  `§7.1` of theirs wrongly rewritten to `§E.1` of ours, produces **zero** diagnostic:
  numeric diff clean, 636 checks pass, `tectonic` exit 0 (the `.tex` is symbolic and
  correct), 0 undefined refs. **The only detector is a human reading 547 strings.**

### 3.3 How many references cross a main/appendix boundary

Computed by partitioning `paper.tex` at line level and counting `\ref` uses whose target
sits on the other side:

| plan | refs crossing the boundary | same-side | total |
|---|---|---|---|
| **Plan A** (aggressive, ≈ 15 pp: keep §1, §4.3, §4.8, §5 intro+Table 3, §9) | **185** | 365 | 550 |
| **Plan B** (renumber-free suffix move, ≈ 46 pp) | **250** | 300 | 550 |

Plan A crosses *fewer* only because so little is kept that most references become
appendix→appendix. In the `.tex` these are free. In the Markdown they are the 547 strings
above.

### 3.4 Float gravity — which tables and figures are cited from the other side

| float | home | cited from (top-level sections × count) |
|---|---|---|
| **Table 2 (`tab:D`)** | §4.3 | §3 ×11, §4 ×11, §8 ×6, §7 ×4, §1 ×3, §5 ×3, §6 ×3, App A ×2 — **8 sections, 43 uses** |
| Figure 1 (`fig:forest`) | §4.3 | §1, §3, §4, §5, §8 — 5 sections |
| Figure 2 (`fig:moderator`) | §4.4 | §1, §3 (never from §4 itself) |
| Figure 3 (`fig:budget`) | §4.8 | §8 |
| Table 3 (`tab:mechanisms`) | §5 | §5 |
| `tab:DG`, `tab:holm`, `fig:decomposition` | §5.4 | §5 only — **self-contained** |
| `tab:attrition` | §8 | §4, §8, App A |
| `tab:provenance` | §8 | §8 only — self-contained |
| `tab:partitions`, `tab:inflight`, `tab:tensor-rules` | §3, §3, §2 | their own section only |
| `tab:arms` | App B | §4 |
| 12 numbered equations | §3.2, §3.3 | **11 of 12 are cited from §4, §5 or §7** |

Two hard constraints fall out:

1. **Table 2 must stay in the main body under any split.** It is cited from 8 of the 11
   top-level units. Moving it makes 43 pointers forward-references into an appendix.
2. **The equation block of §3.2–§3.3 must stay in the main body** — `eq:D`, `eq:G`,
   `eq:A`, `eq:U`, `eq:T`, `eq:Tid`, `eq:AB`, `eq:welch`, `eq:rho`, `eq:Q`, `eq:adm` are
   all cited from §4/§5/§7. §3.2+§3.3 is 3,354 words / ≈ 4 pp, which alone consumes a
   quarter of a 15-pp budget before a single result is stated.

---

## 4. MEASUREMENT — which registered assertions parse the manuscript

Exactly **two** files in the repository read the manuscript:

- `analysis/c98_reproduce.py` — section **[16] THE COVERAGE CENSUS, ASSERTED**
- `analysis/paper_numeric_diff.py`

Everything else in `analysis/` reads the corpus, never the paper. The deposit ships no
manuscript, so `[16]` skips there by design (`"no manuscript in this tree (the deposit
ships none)"`), which is why `make reproduce` cold reports 547 and the source tree reports
628.

**Neither parses by position or by anchor.**
- `_census_claim()` flattens the *whole* file and searches one shape regex
  (`audit executes (\d+) … covering (\d+) of the (\d+) distinct quantity-numerals`).
  Position-independent; it survives any reordering.
- `paper_numeric_diff.quantities()` is a **multiset over the whole file**. Order-independent
  by construction. Verified: moving a block changes nothing in it.

So the *direct* structural exposure is nil. The census's **value**, however, is not — §5.

---

## 5. MEASUREMENT — the census is order-dependent, and it is a bug

### 5.1 The defect

`c98_reproduce.py:860`:

```python
_FENCE = re.compile(r"```.*?```|^ {4,}\S.*$", re.S | re.M)
```

`re.S` applies to the **whole** pattern, so the `.*$` of the second alternative — meant to
drop one indented verbatim line — matches across newlines and runs to the **last** `$` in
the file.

**Measured.** The first four-space-indented line outside a code fence is
`DRAFT-v4.md:3408` (`    make reproduce            # every headline, re-derived…`, the
one-command block that opens §8). From there to EOF, **667 of 4,074 lines — 16.4 % of the
manuscript** — is deleted before a single numeral is counted. That region is the rest of
§8, all of §9 Conclusion, Appendix A (Discrepancy register), Appendix B (the full arm
table) and the entire End matter.

Proof, run against the live tree:

```
census(full DRAFT-v4.md)                    -> (2594, 892, 2290, ...)
census(DRAFT-v4.md truncated at line 3406)  -> (2594, 892, 2290, ...)   IDENTICAL
```

`§3.4` therefore claims coverage of "the 892 distinct quantity-numerals **in this
manuscript**" while measuring 83.6 % of it. `paper_numeric_diff.py` does **not** share the
bug — its `norm_md` uses `(?m)^ {4,}\S.*$` with `re.M` only — which is why the diff sees
2,591 md quantity numerals against the census's 2,290.

### 5.2 What the census *would* say if the rule were line-wise

Re-running `c98_reproduce.py` with the one-character-class fix
`_FENCE = re.compile(r"```.*?```|(?m:^ {4,}\S.*$)")` and nothing else changed:

```
[16] distinct numerals in draft   984 | paper 892 | **FAIL**
     distinct numerals asserted    411 | paper 409 | **FAIL**
     coverage                     41.8 | paper 45.9 | **FAIL**
     sites executed                628 | paper 628 | PASS
```

**The corrected fixpoint is 628 / 411 / 984 / 41.8 %.** The advertised coverage falls
4.1 points. That is the honest number; today's 45.9 % is inflated by hiding a sixth of the
manuscript from the denominator.

### 5.3 Why this decides R9

Because the swallowed region is defined by the **position** of the first indented line,
**any reordering of `DRAFT-v4.md` moves the census** — for reasons that have nothing to do
with the science. Measured, by feeding mutated copies to `census()`:

| mutation to `DRAFT-v4.md` (content byte-identical, order only) | n_qd | §3.4 would have to print |
|---|---|---|
| **none (today)** | **892** | 628 / 409 / **892** / **45.9 %** |
| move §5 to sit after §9 | **745** | coverage would jump to **54.9 %** |
| **Plan B suffix move** (§2.2–2.5, §3.4, §3.5, §4.6.1, §5.5–5.10, §7.2, §8 tail → appendix) | **974** | coverage would fall to **42.0 %** |
| add a reader's guide in place, move nothing (**Plan C**) | **892** | **unchanged** |

So a restructure **cannot** be numerically neutral: §3.4's self-assertion moves by −147 or
+82 distinct numerals, and the paper's headline audit-coverage figure moves by ±4 to +9
points, driven entirely by where a `make` block lands. A referee who notices that the
number moved when nothing was measured differently has found a worse problem than a long
paper.

### 5.4 And it is fixable, cleanly, first

Under the corrected line-wise rule the census becomes **exactly order-invariant**:

```
corrected rule, original order   -> n_q 2599, n_qd 978
corrected rule, §5 moved to end  -> n_q 2599, n_qd 978   IDENTICAL
corrected rule, Plan B suffix    -> n_q 2599, n_qd 978   IDENTICAL
```

(The 978 here is from a standalone re-implementation of the rule; the number to write into
§3.4 is the one `c98_reproduce.py` itself prints under the patch, **984**, because the live
`_FENCE` keeps `re.S` on the fence branch. Re-measure with `--census` and take the script's
own output; do not copy either number from this file.)

**Therefore: fixing `_FENCE` is a precondition for any restructure, and is worth doing on
its own merits even if nothing moves.** It is a change to registered audit machinery, so it
must be declared in `docs/CORRECTIONS.md` and in §3.4 as a correction to the census rule,
with the old and new triples both stated — not slipped in.

### 5.5 One further census trap, measured

The census does **not** strip ATX heading numerals (`paper_numeric_diff.norm_md` does; the
census does not). A new numbered Markdown heading is a quantity token. Adding
`### 1.2 Reader's guide` leaked the token `1.2` into the quantity multiset — harmless here
only because `1.2` already occurs as a quantity elsewhere, so `n_qd` stayed at 892. A
heading numbered, say, `1.9` would push `n_qd` to 893 and force a fixpoint.

**Rule for whoever writes the signposts: run `python3 analysis/c98_reproduce.py --census`
before and after. If `n_qd` moved, reword until it has not, or take the fixpoint
deliberately and write it into §3.4 in BOTH markups.**

Also measured: `_XREF` knows `\bA\.` but no other appendix letter, so a renumber to
`§B.6.1`/`§C.4` style leaks the trailing numerals into the quantity count (+12 tokens in
simulation). If a restructure ever happens, `_XREF` must be widened to `\b[A-Z]\.` in the
same commit as the `_FENCE` fix.

---

## 6. MEASUREMENT — what a split would do to the science guards

### 6.1 The four "declines ≠ disappears" guard sites

| # | site | text | lives in |
|---|---|---|---|
| 1 | `paper.tex:1283` | *"…it does not vanish,"* | **§3.5** (in-flight batches) |
| 2 | `paper.tex:2742` | *"…has read it backwards"* | §4.8 |
| 3 | `paper.tex:2768` | *"The measured ladder stops at 300 epochs and so does the claim."* | §4.8 |
| 4 | `paper.tex:2830` | *"…a decline resolved at this budget and this design point rather than a law."* | §4.8 |

**Three of four sit in §4.8 and the fourth sits in §3.5.** Under Plan A (15 pp) §4.8 is
one of the very few units kept, so guards 2–4 survive — but guard 1 leaves with §3.5.
Under Plan B, §3.5 moves, so guard 1 leaves. Under **any** plan that moves §4.8 — and a
strict 12-pp budget will be tempted to, because §4.8 is 2,292 words — **the abstract would
state that the gap "declines … withdrawing our earlier flatness claim" with every
correction of the "disappears" misreading in an appendix.** That is the exact failure the
guard sites exist to prevent.

**Constraint for any future split: §4.8 stays in the main body, whole, or the split is
rejected.**

### 6.2 Contribution 1's four intact sites

Abstract, §1.1 item 1, §4.8, §9. Two of the four (abstract, §1.1) are safe under every
plan; §4.8 is covered by the constraint above; §9 is 2 pp and stays. **No plan may move
§9.**

### 6.3 Open red-team edits that collide with a move

R2 (§4.8 table caption + `se` column), R4 (the α ≈ 0.102 disclosure, also §4.8), the
CORRECTIONS-135 item 4 (§4.8's opening paragraph over-scoping) and item 2 (two `|`-leading
Markdown lines) are all **inside blocks a restructure would move**. Two agents editing the
same lines, one by line number and one by block, is how an integration loses an edit.

**Sequencing rule: land R2, R4, R10 and CORRECTIONS-135 items 2 and 4 on the current
structure first. Only then consider any move.** Plan C does not conflict with them.

### 6.4 The abstract has no headroom for signposting

The Markdown abstract is the binding one and sits within a few words of the 230 cap (my
own naive counter reads 225 on `DRAFT-v4.md:9–32`; the binding counter is the gate's
`_abstract_defects`, which is **not present in this tree**, so the true headroom must be
re-measured with that counter before anyone touches it). **Signposting must not add a
single word to the abstract.** UNSURE on the exact headroom; do not assume it is more than
two words.

---

## 7. The three plans, costed

### Plan A — aggressive, gate-literal, 12–15 pp main body

| | |
|---|---|
| **KEEP** | §1 + §1.1 (4 pp); §3.2–§3.3 equations, compressed (≈ 2 pp); §4.3 + Table 2 + Figure 1 (2 pp); §4.8 whole, guards 2–4 (3 pp); §5 intro + Table 3 (1 pp); §9 (2 pp) |
| **MOVE** | §2 entire, §3.1, §3.4, §3.5, §4.1, §4.2, §4.4, §4.5, §4.6, §4.6.1, §4.7, §5.1–§5.10, §6 entire, §7 entire, §8 all but the one-command block |
| **NEW PROSE REQUIRED** | ≈ 7,600 words of digest, in **both** markups, ≈ 84 % of the body displaced |
| refs crossing boundary | **185 of 550** |
| md strings to retype | **547**, unchecked, 9 traps |
| census | forced fixpoint, direction and size set by the `_FENCE` bug |
| **verdict** | **REJECT.** It is a rewrite. It contradicts the explicit "no rewrite / no number changes" constraint, and it is the largest possible regression surface against 636 assertions, 8 known residuals and 4 guard sites. |

### Plan B — renumber-free suffix move, ≈ 44–48 pp main body

The one honest way to move material without retyping 547 Markdown strings: move only
**trailing** subsections, so every surviving `§N.M` keeps its number.

| unit | action | why | pp freed |
|---|---|---|---|
| §2.2, §2.3, §2.4, §2.5 | **MOVE** → App C | four close readings of prior work; §2.1 alone carries the argument | ≈ 2.5 |
| §3.1, §3.2, §3.3 | **KEEP** | 11 of 12 equations are cited from §4/§5/§7 | — |
| §3.4, §3.5 | **MOVE** → App D | registration discipline and the four in-flight batches are provenance, not argument — **but §3.5 carries guard site 1, which must be re-sited in §4.8 first** | ≈ 5 |
| §4.1–§4.5, §4.6, §4.7, §4.8 | **KEEP** | the primary, the moderator, the null, the prescription, the reversal | — |
| §4.6.1 | **MOVE** → App E | the `rp1` replication is a self-contained confirmation of a null already stated in §4.6 | ≈ 2 |
| §5 intro + Table 3 + §5.1–§5.4 | **KEEP** | Table 3 is the mechanism ledger; §5.4 is the only mechanism that got *narrowed* rather than refuted | — |
| §5.5–§5.10 | **MOVE** → App F | six refutations and nulls, each self-contained; `tab:DG`, `tab:holm`, `fig:decomposition` are cited only from §5 | ≈ 4.5 |
| §6.1–§6.4 | **KEEP** | 2 pp total, and §6 is a distinctive strength; moving it saves nothing | — |
| §7.1 | **KEEP** | limits of the evidence belong with the evidence | — |
| §7.2 | **MOVE** → App G | limits of the *review process* is meta-commentary | ≈ 3 |
| §8, all but the one-command block and Table 6 | **MOVE** → App H | | ≈ 3 |
| §9 | **KEEP** | | — |
| | **total moved** | | **≈ 20–23 pp** |

| | |
|---|---|
| main body after | **≈ 44–48 pp** (from 67) |
| new prose required | **zero** — every move is a block move plus a one-line pointer |
| refs crossing boundary | **250 of 550**, all free in `.tex` |
| md strings to retype | **≈ 109** (the refs pointing *into* moved material: §2.2 ×2, §2.4 ×7, §2.5 ×3, §3.4 ×16, §3.5 ×16, §4.6.1 ×12, §5.5 ×20, §5.6 ×10, §5.7 ×3, §5.8 ×8, §5.9 ×9, §5.10 ×1, §7.2 ×2) — down from 547 because survivors keep their numbers |
| census | **892 → 974 measured.** Coverage falls 45.9 % → 42.0 %. Requires the `_FENCE` fix first, then a declared fixpoint at 628 / 411 / 984 / 41.8 % |
| guard sites | site 1 leaves with §3.5 — must be re-sited into §4.8 as a *move*, not a rewrite, before §3.5 goes |
| **verdict** | **Technically sound and I would execute it on request. Not recommended as the first action.** It does not reach the target; its whole benefit is the difference between a 67-pp body and a 46-pp body; and it forces a visible change to §3.4's self-audit number. |

### Plan C — signposting in place (RECOMMENDED)

Move nothing. Renumber nothing. Add navigation.

| element | where | content |
|---|---|---|
| **§1.2 Reader's guide and evidence map** | immediately after §1.1 Contributions | ≈ 1 page. See §8 below for the exact spec. |
| **Section-opener signposts** | first line of §3.3, §3.4, §3.5, §4.4, §4.6, §5.4, §7.2, §8 | one sentence each: what the section establishes, and what a referee who is not checking that can skip to |
| **Per-claim pointers** | §1.1 Contributions, one per item | the section, the float and the deposit target that carries each contribution |
| **A "what is load-bearing" note** | end of §1.2 | names §4.3, §4.4, §4.8 and Table 2 as the four things a referee must read, and says everything else is supporting evidence |

| | |
|---|---|
| main body after | 75 pp, unchanged — and honestly so |
| new prose | ≈ 500 words of pure navigation, **carrying no new quantities** |
| refs crossing boundary | 0 — nothing moves |
| md strings to retype | 0; the guide only **adds** references |
| census | **892, unchanged — verified by simulation with a full draft guide inserted** |
| numeric diff | neutral **if and only if** the guide's numerals are identical in both markups; the guide is designed to contain none |
| guard sites | untouched, all four |
| `tectonic` | 2 known overfull hboxes unchanged; a new `tabular` may add one — check and adjust column widths, do not accept a third |
| **verdict** | **RECOMMENDED.** |

---

## 8. Signposting specification — so a referee finds any evidence in one step

Both an evidence map **and** per-section pointers. The map answers "where is the evidence
for claim X"; the pointers answer "am I in a section I can skip". Neither alone is enough.

### 8.1 The evidence map (§1.2, one table)

One row per claim the paper makes. Columns, in this order:

`claim` · `stated in` · `measured in` · `float` · `scorer` · `deposit target`

Rows, one each, and **no others** — this is a map, not a summary:

1. C1 — the partition beats the count at fixed group count
2. C2 — nine mechanisms tested, none survives
3. C3 — the base optimiser moderates (conditional on the endpoint)
4. the budget result — the effect survives 3× the budget **and declines with it**
5. alignment refuted as the carrier; the permutation draw is exchangeable
6. the pre-registered self-reversal and what it did and did not withdraw
7. the corpus, the count-matching and admissibility
8. the scope limits (tuned SGD+cosine; CIFAR resolution; ImageNet-1k impossible)
9. the audit itself

**Construction rules, so the map is census- and diff-neutral:**

- Cite **only** `§N.M`, `Table N`, `Figure N`, `Appendix A.N`, and scorer/target filenames.
  Every one of those is excluded from the quantity multiset by `_XREF`, in both tools.
- **Put no measured quantity in the map.** Not "+0.556", not "20 of 20", not "p = 0.000200".
  The map points; §4.3 states. This is what keeps `n_qd` at 892 and adds zero diff residuals.
- If a number genuinely must appear, it must be re-derived at write time, appear the same
  number of times in both markups, and the census re-run to a fixpoint.
- Number the heading `1.2` — measured safe (`1.2` already occurs as a quantity, so `n_qd`
  does not move). **Verify with `--census` anyway.**
- In `paper.tex` use `\ref{}` for every pointer. In `DRAFT-v4.md` type the literal — and
  cross-check each against the heading list, because nothing else will.

### 8.2 Per-section openers (8 sentences, one per long unit)

Format, fixed, so a referee learns it once: *"This section establishes X. A referee
checking Y can go straight to §Z."*

Required at: **§3.3** (2,654 w), **§3.4** (1,282 w), **§3.5** (2,702 w), **§4.4**
(6,634 w — the single largest unit, and the one most likely to lose a reader),
**§4.6** (4,540 w with §4.6.1 and §4.7), **§5.4** (3,448 w), **§7.2** (2,354 w),
**§8** (2,807 w).

**§4.4 needs two**: one at the top of the subsection and one at the head of its endpoint-
sensitivity block, which is where an 11-page subsection changes subject.

### 8.3 Contribution pointers

Each of the items in §1.1 gains a trailing bracket naming its section, its float and its
deposit target. This is the cheapest single change in the whole plan: a referee who reads
only the Contributions list can then reach any piece of evidence in one hop.

### 8.4 What signposting must NOT do

- Must not touch the abstract (§6.4 — headroom unknown and small).
- Must not restate a result. A signpost that states a number is a second site for that
  number and a new way for the two markups to disagree.
- Must not add a numbered heading whose number is not already a quantity numeral in
  `DRAFT-v4.md`.
- Must not be added to `paper.tex` without the byte-equivalent landing in `DRAFT-v4.md` in
  the same edit.

---

## 9. If the operator overrules and wants Plan B executed anyway

Strict order. Each step is independently verifiable and independently revertible.

1. **Land the open red-team edits first** — R2, R4, R10, CORRECTIONS-135 items 2 and 4 —
   on the current structure. Re-green: `c98_reproduce.py` exit 0, numeric diff at 8
   residuals, `tectonic` exit 0.
2. **Fix `_FENCE`** (`re.S` scoped to the fence branch) **and widen `_XREF` to
   `\b[A-Z]\.`** in one commit. Re-run `--census`, write the printed triple into §3.4 in
   **both** markups, re-run to a fixpoint. Declare it in `docs/CORRECTIONS.md` as a
   correction to the census rule, stating the old triple (628 / 409 / 892 / 45.9 %) and the
   new one, and saying plainly that the old denominator omitted 16.4 % of the manuscript.
   Re-green everything.
3. **Re-site guard site 1** (`paper.tex:1283`, *"it does not vanish"*) from §3.5 into §4.8
   as a verbatim move, before §3.5 goes anywhere. Re-green.
4. **Move the seven suffix blocks** in `paper.tex` only. `tectonic` must come back exit 0,
   0 undefined, 0 `??`, 0 orphan labels, and the overfull-hbox count must not exceed 2.
5. **Mirror the move in `DRAFT-v4.md`,** then retype the ≈ 109 pointers **by hand, one at a
   time, against the heading list**. Before starting, extract the nine parent-paper `§7.x`
   references (`DRAFT-v4.md:41, 43, 45, 250, 254, 257, 258, 260`) into a hold-out list and
   confirm at the end that all nine are byte-identical to their pre-move state. **Do not
   `sed`.** Nothing mechanical will catch an error here.
6. **Re-run the whole green set** and, additionally, diff the rendered section-number list
   of the PDF against the Markdown headings by eye. That eye-diff is the only detector that
   exists for step 5.
7. **Rebuild the deposit** (TODO-FOR-AUTHOR item 4) — `release/REPRODUCTION-AUDIT.txt`
   carries the coverage figure generated at build time and will be stale after step 2.

**If any step turns a green check red and cannot be fixed in that step: revert that step.**

---

## 10. Answers to the four questions, in one place

**1. Section sizes.** §1 above. Body is 67 pp / 46,288 words. §4 is 23 pp; §5 is 13 pp;
§3 is 10 pp. The single largest unit is **§4.4 at 11 pp and 14.3 % of the body**. There is
no fat tail: 24 subsections share the last 19 %.

**2. The split.** §7 above, three plans, KEEP/MOVE stated per unit with reasons.
Plan A (12–15 pp) is **rejected on arithmetic** — it needs ≈ 7,600 words of new prose.
Plan B (renumber-free suffix move) reaches **≈ 46 pp** and is executable; it is costed and
sequenced in §9. Plan C (signpost in place) is **recommended**.

**3. Risks, specifically.**
- `\label`/`\ref`: 74 labels, 550 uses, 0 dangling. **185 cross under Plan A, 250 under
  Plan B** — free in `.tex`, since LaTeX renumbers.
- **The real crossing cost is in `DRAFT-v4.md`: 547 hand-typed cross-reference strings
  (461 `§`, 86 float/appendix), which no registered check can validate, containing nine
  references to the *parent paper's* §7.x that are typographically identical to references
  to our own §7.** Plan B's suffix design cuts this to ≈ 109 by preserving every surviving
  section number.
- Floats: **Table 2 is cited from 8 sections, 43 times — it must stay in the main body.**
  11 of 12 numbered equations (§3.2–§3.3) are cited from §4/§5/§7, so the equation block
  must stay too. `tab:DG`, `tab:holm`, `fig:decomposition` (§5.4) and `tab:provenance` (§8)
  are self-contained and move safely.
- `c98_reproduce.py` assertions: **none parses by position or anchor.** Section [16]
  searches one shape regex over the flattened whole file; `paper_numeric_diff.py` is a
  whole-file multiset. Both survive reordering.
- **The census DOES depend on document structure — through a bug, not through its design.**
  `_FENCE`'s `re.S` makes the indented-block branch swallow from the first indented line
  (`DRAFT-v4.md:3408`) to EOF, hiding 667 lines / 16.4 % of the manuscript. Measured:
  reordering alone moves §3.4's asserted denominator from **892** to **745** (§5 to the end)
  or to **974** (Plan B). Under a corrected line-wise rule the count is exactly
  order-invariant, and the true fixpoint is **628 / 411 / 984 / 41.8 %**.
- Science guards: **three of the four "declines ≠ disappears" sites are in §4.8 and the
  fourth is in §3.5.** §4.8 must never move. §3.5's guard must be re-sited before §3.5 does.

**4. Signposting.** §8 above — an evidence map **and** per-section pointers, with a
construction rule (cite identifiers, never quantities) that is measured to leave the census
at 892 and the numeric diff at its 8 pre-existing residuals.

---

## 11. UNSURE, stated rather than guessed

- **The abstract's exact headroom.** The binding counter is the gate's `_abstract_defects`,
  which is not in this tree; my naive count of `DRAFT-v4.md:9–32` is 225 words against a
  230 cap. Treat the headroom as unknown and small. Plan C does not touch the abstract.
- **Whether a 46-pp main body actually moves a TMLR reviewer.** I have no evidence either
  way. My reasoning is that desk-return risk is a first-impression risk and 46 pp still
  reads as long — but that is judgement, not measurement, and it is the one place in this
  plan where I am reasoning rather than measuring. If the operator's read of TMLR is that
  46 pp materially changes reviewer willingness, Plan B is the right call and §9 is the
  recipe.
- **Whether the `_FENCE` fix should ship at all.** It lowers a headline self-audit figure
  from 45.9 % to 41.8 %. I believe the honest number is the right one and that a referee
  re-running the census would find the discrepancy anyway, but publishing a *worse* coverage
  figure at desk-accept is an editorial call for the authors, not an agent's.
