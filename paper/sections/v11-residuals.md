# v11-residuals — package **residuals-and-status**

**Scope.** Task 2 (R10, the tex↔md numeric residuals) and Task 3 (rewrite `docs/STATUS.md`).
This file edits nothing. It contains findings, then **exact replacement blocks** keyed to
anchors verified unique (`count == 1`) against the live files, then the **full replacement
text for `docs/STATUS.md`**.

**Tree state at write time.** HEAD `58c0c85`, `git status --short` empty. Corpus
`results/all_runs.csv` = **2,177** rows (2,178 lines, 1 header). `docs/CORRECTIONS.md`
highest number = **138**.

**Every number below was produced by a command run at write time.** Nothing is quoted from
the briefing, from `docs/STATUS.md`, from `docs/CORRECTIONS.md` or from
`paper/sections/v9-plan.md` — three of those four were found to carry stale or wrong
statements about exactly this material (§1.9).

---

## 0. How the residuals were localised

`analysis/paper_numeric_diff.py` reports *which* numerals are unbalanced but not *where*,
because its normalisers collapse the files. Two throwaway probes in the scratchpad
supplied the missing half; neither is proposed for the repo.

```
python3 analysis/paper_numeric_diff.py --show 200      -> exit 1, 3 tex-only + 5 md-only
scratchpad/locate.py <token> ...                       -> the same normalisers, rewritten so
                                                          every substitution preserves the
                                                          newline count it removes, so a
                                                          surviving numeral maps back to a
                                                          source line
scratchpad/dryrun.py   -> residual multisets for candidate edits, in memory
scratchpad/dryrun2.py  -> the exact census triple per candidate, using the real ASSERTED
                          list from a full in-process c98_reproduce.main() run
```

Baseline, re-derived:

| check | result |
|---|---|
| `python3 analysis/c98_reproduce.py` | exit 0, **ALL 636 CHECKS PASS** |
| census, measured on `DRAFT-v4.md`, asserted against both markups | **628 / 411 / 982 / 41.9%** (`411/982 = 41.86%`) |
| `python3 analysis/paper_numeric_diff.py` | exit 1 — **2,604 tex numerals (994 distinct) vs 2,606 md (994 distinct)**; 3 tex-only, 5 md-only |
| `python3 analysis/xref_check.py` | exit 0, **545 references resolved** (461 section, 47 table, 15 figure, 22 appendix), 8 allowlisted parent-paper refs, 0 errors |
| `python3 analysis/test_fence_mask.py` | **ALL PASS**; the two masks agree position-for-position, masking **0.78%** of the draft (bar 5.0%) |
| `tectonic -X compile paper.tex`, clean copy | exit 0, **75 pp**, **0** undefined, **2** `Overfull \hbox` (7.28497 pt, 12.25499 pt) |

---

## 1. R10 — the residuals, one at a time

**The count.** There are **7 distinct tokens over 8 occurrences**. That reconciles the
record's two numbers: CORRECTIONS 137 lists the tokens correctly
(`0.05 3.0 39,172` | `0.087 0.279 3.19 9.0 x2`) and then calls them "seven", which is the
distinct-token count, not the residual count. **Nothing has been closed since.** The
residual list at HEAD is byte-identical to the one CORRECTIONS 137 printed.

Verdict summary — **6 of 8 are formatting artefacts, 1 is a one-character typography slip,
2 are a real difference in what the two tables print (and no claim diverges).**

| # | token | side | site | cause | verdict |
|---|---|---|---|---|---|
| 1 | `0.05` | tex-only | `paper.tex:3157–3158` (`\label{tab:holm}`) | LaTeX float `\caption` | formatting — irreducible |
| 2 | `3.0` | tex-only | `paper.tex:2461–2463` (`\label{tab:T}`) | LaTeX float `\caption` | formatting — irreducible |
| 3 | `39,172` | tex-only | `DRAFT-v4.md:1438` | **one space**: `F(39, 172)` vs its tex twin `F(39,172)` | typography — **FIX (E1)** |
| 4 | `0.087` | md-only | `DRAFT-v4.md:2609` | inline-backtick scorer output; the tex sets the same block in `quote` | formatting — optional (E4) |
| 5 | `0.279` | md-only | `DRAFT-v4.md:2609` | same site, same cause | formatting — optional (E4) |
| 6 | `3.19` | md-only | `DRAFT-v4.md:2609` | same site, same cause | formatting — optional (E4) |
| 7 | `9.0` | md-only | `DRAFT-v4.md:1958` | §4.7's `T` table: the md row prints `box −30:9.0`, the tex row (`paper.tex:2471`) does not | **not formatting** — content differs, claim does not — **FIX (E3)** |
| 8 | `9.0` | md-only | `DRAFT-v4.md:1963` | same, second `rl3` rung | same — **FIX (E3)** |

### 1.1 `0.05`, tex-only ×1 — a LaTeX float caption. FORMATTING.

`paper.tex` carries **23** surviving `0.05` numerals, `DRAFT-v4.md` **22**. Pairing them
site by site leaves exactly one unmatched: `paper.tex:3157–3158`,

> `\caption{The twelve-test $\Gstat$ family under Holm--Bonferroni. At most three reach nominal $\alpha = 0.05$ and none survives Holm in either convention.}`

The Markdown renders that table as a bare pipe table (`DRAFT-v4.md:2485–2498`) and carries
no caption line, because Markdown pipe tables have no caption construct.

**Why this is not a content divergence.** The caption's claim is restated as the sentence
that immediately follows the table, and that sentence is in **both** files with the same
numeral: `paper.tex:3180` and `DRAFT-v4.md:2500` both read *"At most three of the
pre-specified twelve reach nominal α = 0.05 and none survives Holm."* The caption adds only
the four words "in either convention", which the following prose then spells out over two
sentences in both markups. Nothing is asserted in one file and absent from the other.

**Disposition: leave.** Closing it would mean inventing a caption line for a Markdown pipe
table — new prose carrying a quantity, in the markup the census reads, to satisfy a diff.
That is the wrong direction. **Irreducible by design.**

### 1.2 `3.0`, tex-only ×1 — the other LaTeX float caption. FORMATTING.

`paper.tex` carries **4**, `DRAFT-v4.md` **3**. The unmatched one is `paper.tex:2461–2463`,

> `\caption{$\Tstat = \arm{nodewise1d} - \arm{nodewise}$, within batch, \plateau. Twelve cells under SGDm, SGD and RMSProp bases, every one resolved at $t \ge 3.0$; under AdamW the move is worth nothing measurable.}`

The md's counterpart (`DRAFT-v4.md:1955–1971`) is again a caption-less pipe table.

**Why this is not a content divergence.** Both halves of the caption's claim are in the md
prose, in a *stronger* form than the caption's rounded bar:

* `DRAFT-v4.md:1985–1987` — *"under an SGDm, SGD or RMSProp base it is worth **+0.328 to
  +1.363 pp** across **twelve** within-batch cells, **every one of which is resolved, the
  weakest at t 3.09**"* — i.e. the exact weakest `t`, not the `≥ 3.0` bar;
* `DRAFT-v4.md:1994` — *"the move is worth nothing measurable"* under AdamW + Lion.

The tex prose says the same two things in the same words at `paper.tex:2507–2509` and
`paper.tex:2517`. So the numeral `3.0` exists only as a rounded restatement inside a float
caption, and the sharp number it rounds (`3.09`) is balanced across the two files.

**Disposition: leave. Irreducible by design**, same reason as §1.1.

### 1.3 `39,172`, tex-only ×1 — ONE SPACE. **THE RECORD IS WRONG ABOUT THIS ONE.**

Both prior claims about this residual are false and are withdrawn here.

* The briefing states it *"was real and is already closed (`F(39,172)`, was missing from the
  Markdown)"*. **It was never closed.** `git log -S` shows both md spellings entering at
  `ac098b6` (cycle 101) and never being touched since; the residual is present at HEAD.
* `docs/STATUS.md`'s R10 row states *"One is a real md prose gap (`F(39,172)`:
  `paper.tex:1845`, `:4658`; `DRAFT-v4.md:3739` only)"*. **There is no prose gap**, and two
  of those three line numbers are stale.

What is actually there — **three sites in each file, all three statements present in both**:

| statement | paper.tex | DRAFT-v4.md | spelling agrees? |
|---|---|---|---|
| §4.2, running prose, "with the batch variance component withdrawn" | `:1845` `F(39,172)` | `:1438` `F(39, 172)` | **NO — one space** |
| A.3 bullet list, bold | `:3820` `F(39, 172)` | `:3038` `F(39, 172)` | yes |
| A.3 prose, "batch is not resolvable" | `:4750` `F(39,172)` | `:3822` `F(39,172)` | yes |

`paper_numeric_diff.py`'s token class is `\d{1,3}(?:,\d{3})+|\d+\.\d+`. `39,172` matches
the thousands-grouped branch; `39, 172` does not, because the branch has no optional space.
So the diff sees tex 2 / md 1 and reports one tex-only residual. **The residual is a single
space character.**

The document has a convention here, and md:1438 is the only violation of it. Every other
`F(a,b)` pair is spelled *identically in the two files*:

```
grep -o "F([0-9]\+, *[0-9]\+)" paper/paper.tex | sort | uniq -c
   1 F(14, 30)   4 F(2,10)   1 F(30, 30)   4 F(30,30)
   1 F(39, 172)  2 F(39,172) 3 F(5,10)     1 F(62, 85)  3 F(62,85)

... paper/DRAFT-v4.md ...
   1 F(14, 30)   4 F(2,10)   1 F(30, 30)   4 F(30,30)
   2 F(39, 172)  1 F(39,172) 3 F(5,10)     1 F(62, 85)  3 F(62,85)
```

The two profiles differ in exactly one place. The spaced spelling is the one used inside
A.3's bold display block (`paper.tex:3820, 3836, 3837, 3838` / `DRAFT-v4.md:3038, 3049,
3050, 3051`); running prose uses the unspaced one. `DRAFT-v4.md:1438` is running prose.

**Disposition: FIX. Edit E1 — one character in one file.** It closes the residual, restores
the document's own spelling convention, and makes md:1438 byte-equivalent to its tex twin.
Measured: the census triple does not move (`39,172` is not a decimal, so the census's
`\d+\.\d+` never saw it at all).

### 1.4–1.6 `0.087`, `0.279`, `3.19`, md-only ×1 each — one line, one cause. FORMATTING.

All three come from a **single** Markdown line, `DRAFT-v4.md:2609`:

> ``--score aw1` prints `{'D_adamw': 0.279, 'se': 0.087, 't': 3.19, 'rule': "UNRESOLVED at n=6. …"}` ``

The TeX carries the identical dict at `paper.tex:3316–3320`, inside
`\begin{quote}\ttfamily\footnotesize … \end{quote}`. `norm_tex` strips the `quote`
environment as quoted scorer output; `norm_md` strips ``` ``` ``` fences, four-space-indented
blocks and `>` blocks, **but not an inline single-backtick span**. So the same three numerals
are excluded on the tex side and survive on the md side.

**Why this is not a content divergence.** The two blocks are the same scorer output with the
same three numbers, and both files print the same following sentence
(`paper.tex:3322–3327` / `DRAFT-v4.md:2611–2615`). This is a pure asymmetry between the two
normalisers' exclusion rules — the documented, intended exclusion, applied to a construct
that only one markup uses.

**Disposition: leave (justified). Optional edit E4** turns the md's inline span into a fenced
block, matching the tex's display-block treatment; it closes all three and is measured
census-neutral and fence-mask-neutral. It is cosmetic and an integrator may decline it.

### 1.7–1.8 `9.0`, md-only ×2 — **NOT a formatting artefact.** The tables differ.

`paper.tex` carries **22** surviving `9.0`, `DRAFT-v4.md` **24**. Every occurrence pairs
site for site except two, both in §4.7's `T` table:

| | paper.tex `\label{tab:T}` | DRAFT-v4.md pipe table |
|---|---|---|
| `rl3` @ η 3e-4 | `:2471` `R18 / C10 / SGDm, $\eta\ 3{\times}10^{-4}$` | `:1958` `R18 / C10 / SGDm, η 3e-4, box −30:9.0` |
| `rl3` @ η 1e-4 | `:2475` `R18 / C10 / SGDm, $\eta\ 10^{-4}$` | `:1963` `R18 / C10 / SGDm, η 1e-4, box −30:9.0` |

**The label "formatting" is wrong for these two, and I am not going to apply it.** No
normaliser is involved: the Markdown table prints a fact in its "network / setting" column
that the TeX table does not print. That is a difference in table content.

**But no claim diverges, and the fact is in both files.** The clip box for those two rungs is
carried in Table 2 rows 6 and 7 of **both** markups (`paper.tex:1494, 1496` /
`DRAFT-v4.md:1168, 1169`), and the `T` table's own footnote block, in **both** markups, points
there: *"The two `rl3` rungs share one batch and one clip box, as Table 2 rows 6 and 7
already note."* So the tex delegates by explicit pointer what the md repeats in the cell.
Nothing is asserted in one file and absent from the other; what differs is where the reader
meets it.

**Disposition: FIX, on the tex side — edit E3.** Add `, box $-30{:}9.0$` to the two tex rows.
Reasons, in order:

1. It closes the residual by making the tex table say what the md's already says, rather than
   by deleting a true and useful annotation from the md.
2. It is the better table. A referee reading `tab:T` sees that two of its twelve cells sit in
   a different clip box, instead of being sent to Table 2 by a footnote.
3. It cannot move the census at all: `censuscheck` measures on `DRAFT-v4.md` alone
   (`c98_reproduce.py:1401–1436`), and E3 does not touch the Markdown.
4. **The LaTeX cost was measured, not guessed.** Compiled on a clean copy of `paper/`
   with the edit applied: exit 0, **75 pp** (unchanged), **0** undefined, and the **same two**
   `Overfull \hbox` warnings at the **same widths** (7.28497 pt at `:1022`, 12.25499 pt at
   `:4546`). The row does not reflow.

If the integrator prefers not to touch `paper.tex` in this cycle, the alternative is E2
(strip `, box −30:9.0` from the two md rows); it closes the same two residuals and is also
census-neutral, but it removes information from the markup that currently has it. **E3 is the
recommendation; E2 is recorded in §2.5 and not recommended.**

### 1.9 Corrections to the record

| source | statement | status |
|---|---|---|
| the briefing | "`F(39,172)` … was real and is already closed" | **FALSE.** Never closed; open at HEAD; and it was never a prose gap (§1.3) |
| `docs/STATUS.md` R10 | "One is a real md prose gap (`F(39,172)`: `paper.tex:1845`, `:4658`; `DRAFT-v4.md:3739` only)" | **FALSE** diagnosis, and `:4658` / `:3739` are stale line numbers. Correct sites in §1.3 |
| `docs/CORRECTIONS.md` 137/138 | "R10's **seven** formatting residuals (all justified as formatting, not content)" | **Half right.** "Seven" is the distinct-token count; there are 8 occurrences. "All formatting" is **wrong for the `9.0` pair** (§1.7) |
| `paper/sections/v9-plan.md` | "the asserted census stays at **892**"; "census 628 / 409 / 892 / 45.9 %" | **STALE.** Those predate CORRECTIONS 136/137. The live triple is **628 / 411 / 982 / 41.9%**. Any Plan C census claim must be re-simulated against 982, not 892 |

**A recurring trap, worth a standing note.** Three separate "present in one markup, missing
from the other" alarms in this project — CORRECTIONS 138's §9 false alarm, and two of mine
this cycle (the CRediT "Funding acquisition" string, and §4.8's "identically in all three
readings below") — were all `grep` hitting a **line wrap**. The two markups wrap at different
columns, so a single-line `grep` for any phrase longer than ~60 characters will report a
false divergence. Search with `tr '\n' ' '` or on a normalised flat copy.

---

## 2. Exact replacement blocks

Every anchor below was checked with `str.count()` against the live file at HEAD `58c0c85`
and returned **1**. Anchors are verbatim, including the line breaks shown. **Nothing in this
package touches the end matter, the CRediT roles, the Funding statement, the correspondence
address or the author list.**

### 2.1 E1 — `paper/DRAFT-v4.md:1438`. RECOMMENDED.

One character. Closes residual #3. `count == 1` verified.

**FIND**
```
variance component withdrawn (sd_batch = 0.000 pp, F(39, 172) = 0.71), a second submission at
```

**REPLACE WITH**
```
variance component withdrawn (sd_batch = 0.000 pp, F(39,172) = 0.71), a second submission at
```

No `paper.tex` counterpart edit: `paper.tex:1845` already reads `$F(39,172) = 0.71$`. The
house rule "every edit lands in BOTH" is satisfied by this edit *bringing* the md into
agreement with the tex, not by a paired change.

### 2.2 E3 — `paper/paper.tex:2471` and `:2475`. RECOMMENDED.

Closes residuals #7 and #8. Two independent anchors, `count == 1` each. Compile impact
measured: 75 pp, exit 0, same two `Overfull \hbox` at the same widths.

**FIND (a)**
```
\arm{rl3} & R18 / C10 / SGDm, $\eta\ 3{\times}10^{-4}$ & 3 v 3 & $+0.391$ & 0.127 & 3.09 \\
```

**REPLACE WITH (a)**
```
\arm{rl3} & R18 / C10 / SGDm, $\eta\ 3{\times}10^{-4}$, box $-30{:}9.0$ & 3 v 3 & $+0.391$ & 0.127 & 3.09 \\
```

**FIND (b)**
```
\arm{rl3} & R18 / C10 / SGDm, $\eta\ 10^{-4}$ & 3 v 3 & $+0.756$ & 0.117 & 6.45 \\
```

**REPLACE WITH (b)**
```
\arm{rl3} & R18 / C10 / SGDm, $\eta\ 10^{-4}$, box $-30{:}9.0$ & 3 v 3 & $+0.756$ & 0.117 & 6.45 \\
```

No `DRAFT-v4.md` counterpart edit: `DRAFT-v4.md:1958` and `:1963` already carry
`box −30:9.0`. Again the edit closes an existing asymmetry rather than creating one.

The box string is written `$-30{:}9.0$` to match the spelling `paper.tex` uses everywhere
else for this box (e.g. `:1494`, `:1496`, `:1501`, `:2679`), not `-30:9.0`.

### 2.3 E4 — `paper/DRAFT-v4.md:2608–2610`. OPTIONAL, cosmetic.

Closes residuals #4, #5, #6 by giving the md's quoted scorer output the same display-block
treatment the tex gives it. `count == 1` verified on the three-line anchor. Measured
census-neutral and fence-mask-neutral (§2.6). **Decline this one freely** — §1.4–1.6 stands
on its own as the justification.

**FIND** (three consecutive lines, 2608–2610)

````
The same batch's D itself is **UNRESOLVED** on its own registered rule: `analysis/c88_scorers.py
--score aw1` prints `{'D_adamw': 0.279, 'se': 0.087, 't': 3.19, 'rule': "UNRESOLVED at n=6.
Report the interval. Do NOT re-cut the data, and do NOT describe it as 'partially transferring'."}`
````

**REPLACE WITH** (the outer four-backtick fence is this file's quoting; the inner
three-backtick lines are literal text to be written into the draft)

````
The same batch's D itself is **UNRESOLVED** on its own registered rule: `analysis/c88_scorers.py
--score aw1` prints

```
{'D_adamw': 0.279, 'se': 0.087, 't': 3.19,
 'rule': "UNRESOLVED at n=6. Report the interval. Do NOT re-cut the
   data, and do NOT describe it as 'partially transferring'."}
```
````

The block ends with one blank line before the existing
`The registered bar was a 95% lower bound…` line, which is untouched.

If E4 is applied, the tex needs no counterpart edit — `paper.tex:3316–3320` already sets the
same dict as a display block.

### 2.4 Not proposed — the two irreducible captions

Residuals #1 and #2 have **no replacement block**, by decision. Closing them requires adding
a caption line carrying a quantity to a Markdown pipe table, i.e. writing new number-bearing
prose into the markup the census reads, purely to satisfy a diff. §1.1 and §1.2 are the
justification the task asked for.

### 2.5 Recorded but NOT recommended — E2

The md-side alternative to E3. Also closes #7 and #8, also census-neutral, but it deletes a
true annotation from the markup that has it. Recorded so the integrator has the choice, not
because it is preferred.

```
FIND     | rl3§ | R18 / C10 / SGDm, η 3e-4, box −30:9.0 | 3 v 3 | +0.391 | 0.127 | 3.09 |
REPLACE  | rl3§ | R18 / C10 / SGDm, η 3e-4 | 3 v 3 | +0.391 | 0.127 | 3.09 |

FIND     | rl3§ | R18 / C10 / SGDm, η 1e-4, box −30:9.0 | 3 v 3 | +0.756 | 0.117 | 6.45 |
REPLACE  | rl3§ | R18 / C10 / SGDm, η 1e-4 | 3 v 3 | +0.756 | 0.117 | 6.45 |
```

**Apply E2 or E3, never both.**

### 2.6 Dry-run evidence — measured in memory, nothing written

`scratchpad/dryrun.py` recomputes both residual multisets; `scratchpad/dryrun2.py`
recomputes the census triple using the real `ASSERTED` list from a full in-process
`c98_reproduce.main()` (which itself returned 0 with ALL 636 PASS).

| variant | tex-only | md-only | census triple |
|---|---|---|---|
| **HEAD** | 3 — `0.05 3.0 39,172` | 5 — `0.087 0.279 3.19 9.0 9.0` | 628 / 411 / 982 / 41.9% |
| **E1** | 2 — `0.05 3.0` | 5 — unchanged | **628 / 411 / 982 / 41.9%** |
| **E1 + E2** | 3 | 3 — `0.087 0.279 3.19` | **628 / 411 / 982 / 41.9%** |
| **E3** (tex only) | 3 | 3 — `0.087 0.279 3.19` | 628 / 411 / 982 / 41.9% (md untouched) |
| **E4** | 3 | 2 — `9.0 9.0` | **628 / 411 / 982 / 41.9%** |
| **E1 + E2 + E4** | 2 — `0.05 3.0` | **0** | **628 / 411 / 982 / 41.9%** |
| **recommended: E1 + E3** | 2 — `0.05 3.0` | 3 — `0.087 0.279 3.19` | 628 / 411 / 982 / 41.9% |
| **E1 + E3 + E4** | 2 — `0.05 3.0` | **0** | 628 / 411 / 982 / 41.9% |

**Why the census cannot move under any of these.** `censuscheck` asserts four things: sites
executed (`CENSUS_MARK`), distinct numerals asserted (`n_cov`), **distinct** quantity
numerals in the draft (`n_qd`), and their ratio. The total count `n_q` is unpacked as `_n_q`
and never asserted. Every token these edits add to or remove from `DRAFT-v4.md` already
occurs elsewhere in the draft outside any fence, so the **distinct** set is unchanged.
Census-visible occurrence counts at HEAD, measured under `c98_reproduce._FENCE`:
`9.0` **24**, `0.087` **10**, `0.279` **9**, `3.19` **2** (the scarce one; its other site is
the Table 2 pipe-table row at `DRAFT-v4.md:1172`, which `_FENCE` does not mask). E2 takes
`9.0` to 22; E4 takes `0.087` to 9, `0.279` to 8 and `3.19` to 1. None reaches zero, so no
numeral leaves the distinct set. `39,172` is not a decimal, so the census never counted it at
all. The total `n_q` does move (2614 → 2612 → 2609) and nothing reads it.

`test_fence_mask.py`'s invariant also holds under E4: the two masks still agree
position-for-position, and the masked fraction goes 0.78% → 0.84% against a 5.0% bar.

### 2.7 Post-application checklist for the integrator

```
python3 analysis/c98_reproduce.py        # expect exit 0, ALL 636 CHECKS PASS,
                                         #        census 628 / 411 / 982 / 41.9%
python3 analysis/xref_check.py           # expect exit 0, 545 references, 0 errors
python3 analysis/test_fence_mask.py      # expect ALL PASS
python3 analysis/paper_numeric_diff.py   # expect exit 1 with the REDUCED list:
                                         #   E1+E3      -> tex-only 0.05 3.0 | md-only 0.087 0.279 3.19
                                         #   E1+E3+E4   -> tex-only 0.05 3.0 | md-only (none)
cd paper && tectonic -X compile paper.tex   # expect 0 errors, 75 pp, the same 2 Overfull \hbox
```

**`paper_numeric_diff.py` still exits 1 after every variant except none of them** — the two
caption residuals are irreducible, so exit 1 remains the green state and the check must be
read by its printed list, not its exit code. That is unchanged from HEAD; it is stated here
because a shrinking list makes it tempting to expect exit 0.

---

## 3. `docs/STATUS.md` — full replacement text

**Why a rewrite rather than edits.** The live file's "Open, carried from CORRECTIONS 135"
section lists items 2–6 as open; all five are closed, with evidence re-derived below. It also
carries stale line numbers (`paper.tex:2741`, `:4658`, `DRAFT-v4.md:3739`), a stale census
triple (`628 / 409 / 892 / 45.9%`), a wrong R10 diagnosis, and a `Manuscript at ae3951a`
header two commits behind. Every row of the replacement was re-derived at HEAD `58c0c85`;
none was copied forward.

**Verification of the five closures, at HEAD:**

| carried item | closure evidence, re-derived |
|---|---|
| 2 — two md prose lines starting with `\|` | `grep -nE '^\|(r\|Δ\|ρ\|t\|D\|\\)' paper/DRAFT-v4.md` → **no output** |
| 3 — §4.8 `se` column undefined (R2) | the rule is in both markups: `paper.tex:2744` / `DRAFT-v4.md:2172` — *"against a slope it is the paired-difference se; against a level, the Welch se"*. **The caption half of R2 is NOT closed** — see §4 |
| 4 — §4.8 opening over-scoped | *"identically in all three readings below. In the **as-published** reading alone…"* at `paper.tex:2675–2676` and `DRAFT-v4.md:2123–2124` |
| 5 — ALICE staging dirs | `ssh alice 'ls -d …/c99pkg …/c99pkg2'` → **No such file or directory**, both |
| 6 — §9 companion sentence | decided NO. The sentence is in both: `paper.tex:4608` / `DRAFT-v4.md:3693–3694` |

Replacement text follows between the fences. It contains no triple-backtick blocks, so it
can be copied verbatim.

````
# STATUS — operator dashboard

Updated 3 Sep 2026 (cycle 116). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **138**) > `docs/FINDINGS.md` > everything else.
HEAD = **58c0c85**, working tree clean. Draft = `paper/paper.tex` + `paper/DRAFT-v4.md` (**75 pp**). Corpus = **2,177 rows**.
**No Slurm job submitted. Both queues empty** — `squeue -u salehkaleybars` and `-u s5014158` both return a header only.
**Every row below was re-derived at HEAD. Do not quote this file as a source; re-run the command.**

## Verdict

| | |
|---|---|
| Q1 meta-gate | **DESK-ACCEPT, 9/10, `structural_gaps = []`, `passed = True`, 0 blocking.** Returned at cycle 111 on v8 (CORRECTIONS 135). **Carried, not re-derivable here** — the gate tool is not in this tree |
| Audit | `c98_reproduce.py` **exit 0, ALL 636 CHECKS PASS**; census at fixpoint **628 / 411 / 982 / 41.9%** |
| tex↔md | `paper_numeric_diff.py` **8 residuals over 7 distinct tokens, all pre-existing, 0 new.** Diagnosed one at a time in `paper/sections/v11-residuals.md` |
| Science overturned | **none.** Contribution 1 intact at 4 sites; the withdrawal stays confined to the slope |
| GPU to reach submission | **0 jobs, 0 hours** |

**Ready to submit: NO** — not for any manuscript defect, for the six author items.

## Mechanical verification — commands run at HEAD 58c0c85

| check | result |
|---|---|
| `python3 analysis/c98_reproduce.py` | exit 0, **ALL 636 CHECKS PASS** |
| census fixpoint (measured on `DRAFT-v4.md`, asserted against both markups) | **628 / 411 / 982 / 41.9%** |
| `python3 analysis/xref_check.py` | exit 0, **545 references** (461 section, 47 table, 15 figure, 22 appendix), 8 allowlisted parent-paper refs, **0 errors** |
| `python3 analysis/test_fence_mask.py` | **ALL PASS**; both masks agree position-for-position; **0.78%** of the draft masked (bar 5.0%) |
| `python3 analysis/paper_numeric_diff.py` | **exit 1 — and exit 1 IS the green state.** 2,604 tex numerals (994 distinct) vs 2,606 md (994 distinct); 3 tex-only (`0.05 3.0 39,172`), 5 md-only (`0.087 0.279 3.19 9.0 9.0`) |
| `tectonic -X compile paper.tex` | exit 0, **75 pp**, 0 TeX errors, **0** undefined, **74 labels / 74 refs**, **2** `Overfull \hbox` (7.28497 pt at `:1022`, 12.25499 pt at `:4546`) |
| `python3 analysis/dup_group_guard.py` | **21 groups, 42 rows stamped, 3 superseded — PASS**; `--selftest` **5/5 PASS** |
| `python3 analysis/c99_hz3q_score.py --selftest` | **59/59 PASS** |
| `c99` gates, raw records supplied | **H0 PASS** (all four arms L4 / `-30:9.0` / seed 5 / 300 ep) · **H1 PASS** worst coordinate fraction **0.000000**, bar 0.05, **n = 500/arm** · **H2** repaired `-0.238 / 0.093 / -2.57` → **NOT FLAT, D DECLINES WITH BUDGET** · **H3** repaired `D(300) +0.394 / 0.093 / +4.25`, `G(300) -0.048` · **HC** `+0.134 pp`, bar 1.00 → GPU class not first-order |
| `c87_hz3_score.py` unedited | **VERDICT: SURVIVES** · **MECHANISM SURVIVES THE HORIZON** · `D(300)-D(100) = +0.229` → **GROWS** · `grep -c hz3q` = **0** |
| abstract, plain word count | tex **222** (agrees with the gate's 222); md **231** by plain count — the gate's `clean_abstract_text` reports **228**, cap 230, and **the gate is the authority; its cleaner is not in this tree** |
| deposit, `release/` | `make verify` **140 files, 0 bad** · cold `make reproduce` **ALL 547 PASS**, both skips announced (`[7] BUDGET`, `censuscheck`) · after `make logs` **ALL 628 PASS** · `make clean` then verify **140 / 0 bad** |

**OPERATIONAL TRAP — read this before calling a scorer red.** The raw `.out` and `probe.jsonl`
records are **not in the repo** (`runs/` is gitignored). They live one level **above** it, at
`../runs` and `../runs_alice2`. `c98_figures.series()` finds them by itself; `c87_hz3_score.py`
and `c99_hz3q_score.py` do **not** — their `--runs` default is the relative `runs`. Run bare,
`c87` prints *"this batch has NOT been submitted"* and `c99` **REFUSES** under RULE 13. Correct
invocation:

    R="$(cd .. && pwd)/runs"
    python3 analysis/c87_hz3_score.py --runs "$R"
    python3 analysis/c99_hz3q_score.py --runs "$R" --probes "$R/hz3"

**Second trap — `grep` across a line wrap.** The two markups wrap at different columns, so a
single-line `grep` for a phrase longer than ~60 characters reports a **false** "missing from the
other markup". This has produced three false alarms so far (§9's companion sentence, CRediT's
"Funding acquisition", §4.8's "identically in all three readings below" — all present in both).
Search a flattened copy (`tr '\n' ' '`) before reporting a divergence.

## Contribution 1 — unweakened, four guard sites, both markups

| site | state |
|---|---|
| Abstract | *"wins all twenty count-matched cells … +0.556 ± 0.045 pp (calibrated 95% CI ± 0.121), homogeneous against that null (Q 4.21, median 9.4)"* — `paper.tex:71–72` / `DRAFT-v4.md:17` |
| §1 Contributions item 1 | untouched |
| §4.8 | insertions only; no existing sentence deleted or softened |
| §9 | *"…two findings, of which the second does not weaken the first"* — `paper.tex:4608` / `DRAFT-v4.md:3693–3694` |

- `hz3q` enters **no cell** of Table 2 — `grep -c hz3q` over the `tab:D` row block = **0**.
- **"Declines" cannot be read as "disappears"** — 4 guard sentences, each in **both** markups:
  `paper.tex:1283` *"does not vanish"* · `:2763` *"has read it backwards"* · `:2789` *"The measured
  ladder stops at 300 epochs and so does the claim"* · `:2851` *"a decline resolved at this budget
  and this design point rather than a law"*.

## Red team — 9 of 10 closed, 0 blocking

| # | finding | state |
|---|---|---|
| R1 | Abstract carried no trace of the reversal | **CLOSED** (135) — one clause, inside the 230-word cap |
| R2 | §4.8's budget table: no caption, undefined `se` column | **CLOSED on the `se` limb** (137) — both estimators named, general rule stated in both markups. **Caption limb answered by decision, not by edit** — see Open item 3 |
| R3 | No rebuttal to linear extrapolation | **CLOSED** (135) — arithmetic printed, four measured facts against it |
| R4 | Registered bar `\|t\| ≥ 2.0` at df 5 is two-sided α ≈ 0.102, undisclosed | **CLOSED** (137) — disclosed at the site, with both mitigations. Repaired reading clears a strict 0.05 by **0.0015 in t** (`p = 0.04991`, critical `\|t\| = 2.5706`) |
| R5 | Reversal's mechanics unstated | **CLOSED** (135) — location × precision, plus leave-one-out |
| R6 | T9 read as scoping all three readings | **CLOSED** (135) |
| R7 | `f3_budget` panel (b) drawn on the archive | **CLOSED** (135) — redrawn, all three readings |
| R8 | Deposit `make reproduce` cold-skips `[7] BUDGET` | **CLOSED as documented** (138) — soft skip is the correct behaviour; the README now names the section, why it cannot read, that the skip is announced, and the one-command fix |
| R9 | **75 pp.** Reviewer-burden desk-return is the biggest venue risk | **DECLINED ON MEASUREMENT** — body is 67 pp / 46,288 words at 691 w/pp, so a 15-pp body needs ≈ 7,600 words of new number-dense prose in both markups: a rewrite. Full costing in `paper/sections/v9-plan.md`. **Mitigation = Plan C signposting, still open** |
| R10 | tex↔md numeric residuals | **DIAGNOSED, partly closable** — 7 distinct tokens / **8** occurrences. 6 formatting, 1 a one-character md typography slip, 2 a real table-content difference with no claim divergence. See `paper/sections/v11-residuals.md`; 5 of the 8 have exact replacement blocks, 2 are irreducible by design |

## Census history — a printed claim that was wrong twice

| triple | why it moved |
|---|---|
| 628 / 409 / 892 / **45.9%** | the `_FENCE` masking bug: one mask swallowed 16.9% of the draft, so the denominator was measured on a manuscript with a sixth of it invisible |
| 628 / 411 / 978 / **42.0%** | CORRECTIONS 136 fixed the shared `re.S`; coverage ticked **down** and was reported, not absorbed |
| **628 / 411 / 982 / 41.9%** | CORRECTIONS 137's R2/R4 prose added four distinct quantity-numerals; re-iterated to a **fixpoint** in two passes |

- `paper/sections/v9-plan.md` still prints the pre-136 figures (`892`, `45.9%`). **Any Plan C census simulation must be re-run against 982.**
- Two checks are newly registered and must be run every cycle: **`analysis/xref_check.py`** (cycle 113, 545 refs) and **`analysis/test_fence_mask.py`** (CORRECTIONS 136 regression pin).

## Deposit

| | |
|---|---|
| built from | commit **`d1a3ed4`**, **and its own README records the working tree was DIRTY at build time** |
| HEAD is | **`58c0c85`** — the deposit on disk is already one commit stale |
| census in `release/README.md` | **41.9%** — correct. It shipped **45.9%** once (CORRECTIONS 138), which is the failure mode author item 4 exists to catch, and it had already bitten |
| state | `make verify` 140 / 0 bad; restored to shipped state (`make clean`) after testing |

**It must be rebuilt from a clean checkout at the submission commit.** `release/` is gitignored: a build product, regenerated, never committed.

## TODO-FOR-AUTHOR — 6 open, all outside agent scope, each verified open at HEAD

| # | item | evidence it is still open | effort |
|---|---|---|---|
| 1 | **CRediT ↔ Funding contradiction** — "Funding acquisition" on S. Salehkaleybar against a Funding statement reading "no dedicated project funding and no grant" | both strings present in **both** markups: `paper.tex:5026–5027` ("Funding\nacquisition", wrapped) + `:5005` / `DRAFT-v4.md:4062` + `:4042` | 1 min |
| 2 | **LIACS correspondence address** to replace the gmail of record | **4 sites, 2 per markup**: `paper.tex:56` (`\thanks`) and `:5059` (`\paragraph{Correspondence.}`) / `DRAFT-v4.md:5` and `:4091`. The LIACS *affiliation* is already in the CRediT block; this is the address only | 2 min |
| 3 | **ORCIDs, both authors** | `grep -ci orcid` = **0** in `paper.tex`, **0** in `DRAFT-v4.md` | 5 min |
| 4 | **Deposit rebuild at the submission commit** | on-disk deposit built from `d1a3ed4`, tree dirty, HEAD `58c0c85` | 2 min (`python3 analysis/c98_release.py`) |
| 5 | **Mint the artefact DOI** | *"The deposit has no DOI, because it has not been deposited"* — `paper.tex:4938` / `DRAFT-v4.md:3977` — honest, not a stub | 5 min + upload |
| 6 | **Authorship for the §5.9 design originator** | Competing Interests names them as *"a researcher … who is not an author"* and calls the origination *"a substantial intellectual contribution rather than an acknowledgeable courtesy"* — `paper.tex:4996`, `:4999` / `DRAFT-v4.md:4033`, `:4036` | **decision, not edit** |

- Items 1–5 are mechanical. **Item 6 is an ethics decision only the authors can make, and it must be settled before submission** — the paper's own Competing Interests says so.
- **Do not delegate 1, 2, 3 or 6.** End matter, CRediT, funding, correspondence and the author list are the authors' by standing instruction.
- The list is exactly six. Nothing was added; nothing was closed.

## Venue

| venue | fit | accept prob. (est.) | note |
|---|---|---|---|
| **TMLR** | **best** | **0.80** | No novelty bar, no length cap; "claims supported" + "of interest" both strongly met. The pre-registered self-reversal reaches the abstract |
| ReScience / MLRC | good | 0.60 | Strong reproduction framing; wants a tighter one-paper scope |
| NeurIPS D&B | fair | 0.30 | Corpus + deposit is a real artefact, but the paper is not framed as one |
| JMLR | fair | 0.25 | Length fine; wants methodological novelty, this is an audit |
| NeurIPS / ICML / ICLR main | poor | 0.15 | 9-page limit is fatal |

**Send to TMLR: YES**, after items 1–4 and a decision on 6. Path: fix 1–4 → settle 6 → rebuild the deposit at the submission commit → arXiv → TMLR. Item 5 (DOI) can follow acceptance; the deposit is commit-pinned and self-verifying.

## Standing

- `plateau5` PRIMARY; the CSV `plateau` column **BANNED** as primary.
- RULE 16 registered scorers run **unedited** · RULE 20 the ARGS line is the truth · RULE 21 scorer before batch · RULE 22 `dup_group` guard.
- **Ingest is `aggregate.py` THEN `args_repair.py --apply`** — `aggregate.py` alone silently reverts the `dup_group` repair and drops `ml2`'s `se` from 0.195 to 0.142.
- **Re-derive every number at write time. Never quote prose, including this dashboard.**
- Never fabricate an ORCID, affiliation, grant number or DOI.
- `release/` and `runs/` are gitignored build/data products.

## Open — re-derived at HEAD, nothing carried forward unchecked

| # | item | state |
|---|---|---|
| 1 | **Plan C signposting** (R9's mitigation) — ~500 words of navigation, no quantities, nothing moved or renumbered | **OPEN.** The one remaining content item |
| 2 | **R10's two irreducible residuals** — the `tab:holm` and `tab:T` LaTeX float captions | **OPEN BY DECISION.** Markdown pipe tables have no caption construct; both captions' claims appear in the adjacent prose of both markups. `paper_numeric_diff.py` will keep exiting 1 |
| 3 | **§4.8's budget table has no caption and no label** — `paper.tex:2717–2729` is an unfloated `center`/`tabular`; the md is a bare pipe table | **OPEN, recorded not closed.** R2's `se` limb is closed; this is R2's other limb. Nothing cross-references the table (it has no `\label`, and `xref_check.py` is clean), and the following prose *"In the table, se is…"* carries what a caption would. Acceptable as-is — but it was **not** fixed, and 137 did not say so |
| 4 | **R10's five closable residuals** | Exact replacement blocks ready in `paper/sections/v11-residuals.md` §2, dry-run-verified census-neutral. Not applied by that package |

**CLOSED this cycle, with evidence — do not re-open these:** the two `|`-leading md prose lines
(CORRECTIONS 138), §4.8's `se` column (137), §4.8's opening over-scoping (138), the ALICE staging
dirs (138, re-verified by `ssh` at HEAD), the §9 companion-sentence question (138 — decided **NO**),
R4 (137), R8 (138).
````

---

## 4. New problems found while doing this, and what I did not do

### 4.1 New — R2's caption limb was never closed

R2 as logged had two limbs: *"§4.8's budget table has no caption and an undefined `se`
column"*. CORRECTIONS 137 closed the `se` limb well and did not mention the caption limb;
`docs/STATUS.md` and CORRECTIONS 138 then both carry R2 as closed. At HEAD the table is
still an unfloated `center`/`tabular` at `paper.tex:2717–2729` with **no `\caption` and no
`\label`**, and a bare pipe table in the md.

**Not a defect that needs an edit**, and I am not proposing one: nothing cross-references
the table (it has no label, and `xref_check.py` returns 0 errors), and the prose immediately
after it — *"In the table, `se` is the standard error of the mean of the n per-seed paired
differences…"* — does a caption's job in both markups. **But it was not fixed, and the record
says it was.** Recorded as an open-by-decision item in the replacement dashboard.

### 4.2 New — the raw records are outside the repo, and two registered scorers cannot find them

`runs/` is gitignored and absent from this tree; the records live at `../runs` and
`../runs_alice2`. `c98_figures.series()` resolves them itself, so `c98_reproduce.py`'s
`[7] BUDGET` passes. `c87_hz3_score.py` and `c99_hz3q_score.py` default `--runs` to the
relative `runs`, so run bare they print *"this batch has NOT been submitted"* and **REFUSE
under RULE 13** respectively. Both reproduce their recorded verdicts exactly once `--runs`
and `--probes` are supplied. This is the single most likely way a future operator concludes
a green check has gone red. Written into the replacement dashboard as an operational trap.

### 4.3 New — the line-wrap `grep` trap has now produced three false divergence alarms

CORRECTIONS 138 already recorded one (§9's companion sentence). Two more surfaced this
cycle, both mine, both false: CRediT's "Funding acquisition" (`paper.tex:5026–5027`) and
§4.8's "identically in all three readings below" (`DRAFT-v4.md:2123–2124`). The two markups
wrap at different columns; any single-line `grep` for a phrase longer than roughly 60
characters can report a divergence that does not exist. Promoted to a standing note.

### 4.4 New — `paper/sections/v9-plan.md` carries pre-CORRECTIONS-136 census figures

It prints `628 / 409 / 892 / 45.9 %` and *"the asserted census stays at 892"*. The live
denominator is **982** and coverage **41.9%**. The Plan C package's census-invariance
argument therefore rests on a simulation run against a stale denominator and should be
re-simulated. Flagged, not edited — `v9-plan.md` is another package's file, and its
*conclusion* (Plan C adds no quantities, so the triple does not move) is unaffected by the
denominator's value; only the printed number is stale.

### 4.5 Observed, out of scope, no action proposed

- The `T` table's row order differs between markups: `paper.tex` runs
  `bn1, hz3, rl3, ml2, …`; `DRAFT-v4.md` runs `hz3, rl3, bn1, ml2, …`. Same twelve+three
  rows, same values. Produces no residual.
- The md `T` table carries inline footnote markers `‡ § ¶` on rows; the tex marks only
  `hz3` (`$^{\ddagger}$`) and runs the other two footnotes together as prose in the
  `minipage`. Produces no residual.
- Table 2's `hz3` row and the A-appendix box table print a parenthetical in the md
  (`(one seed at −15:−2.3026)`, `(seed-5 chunk arms at −15:−2.3026)`) that the tex rows omit.
  These add `2.3026` tokens to the md that happen to balance against other asymmetries, so
  the multiset test does not flag them. **A reminder that `paper_numeric_diff.py` is a
  multiset test and asymmetries can cancel**; a clean list is not proof of symmetry.

### 4.6 UNSURE — stated rather than guessed

- **The Q1 meta-gate verdict cannot be re-derived in this tree.** The gate tool is not here.
  The last recorded run is CORRECTIONS 135 (cycle 111, on v8). The replacement dashboard
  labels it carried.
- **The Markdown abstract's authoritative word count.** The gate's pipeline is
  `_extract_abstract` → `clean_abstract_text` → `_abstract_defects`; none is in this tree. A
  plain word count over `## Abstract` … next heading gives **231**; the recorded gate figure
  is **228** against a 230 cap. The tex agrees at **222** by both methods. I do **not** know
  which three words `clean_abstract_text` drops, so I have not asserted 228 as re-derived and
  the dashboard says so. **Anyone editing the abstract must run the gate, not this count** —
  231 vs 228 is the difference between over and under the cap.

### 4.7 What this package did not do

- Did not edit `paper/paper.tex`, `paper/DRAFT-v4.md` or `docs/STATUS.md`. All three arrive
  as replacement blocks / replacement text above, so the integrator applies one version.
- Did not run `git commit`.
- Did not submit any Slurm job. The only cluster contact was one read-only `ssh` running
  `ls -d` and `squeue` (carried item 5, and the queue check).
- Did not touch `docs/CORRECTIONS.md`. The corrections to the record in §1.9 and §4.1 need a
  CORRECTIONS 139 entry that only the integrator should write.
- Did not touch the end matter's CRediT roles, Funding statement, correspondence address or
  author list. The six author items are unchanged and each was verified still open.
- Did not touch Plan C signposting (Task 1, a separate package), `paper/sections/v9-plan.md`,
  or any registered scorer.
