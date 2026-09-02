# PACKAGE `false-numbers` — closes F1, F2, R1

Cycle 102. Two false printed numbers and one deposit over-claim. Nothing is hedged, nothing is
softened: each number is re-derived from the CSV or from the code, and the false string is
replaced by the true one.

**This package does NOT edit `paper/paper.tex` or `paper/DRAFT-v4.md`.** It supplies the exact
replacement text for both, keyed to verbatim, verified-unique anchors. It DOES edit
`analysis/c98_reproduce.py` and `analysis/c98_release.py`, and it rebuilt `release/`.

---

## READ THIS FIRST — one number in this package is a moving target

F2's fix makes the audit **assert** §3.4's coverage sentence instead of merely measuring it.
That assertion compares three integers and a percentage against a fresh measurement of
`DRAFT-v4.md`. **Those four values change whenever any package adds or removes a `chk()` site,
or adds a decimal numeral to the draft.** They moved once *during* this task: the `M1`
metric-sensitivity package landed a new `[15] METRIC SENSITIVITY` section in
`analysis/c98_reproduce.py` at 21:35, taking the count from 283/216/747/28.9% to
353/231/747/30.9%.

Consequence, stated plainly:

* The §3.4 replacement text below is written with **353 / 231 / 747 / 30.9%**, which is the
  measured truth of the tree at the moment this package was finished, and it is a verified
  fixpoint against that tree (proof below).
* **The integrator must re-run `python3 analysis/c98_reproduce.py --census` once every
  cycle-102 package has landed and write the printed triple into the §3.4 sentence of BOTH
  files.** There is now exactly one place to update — the sentence itself — because the audit
  reads its "paper" value out of `DRAFT-v4.md` rather than duplicating it in a constant.
* Until that sentence lands, **`python3 analysis/c98_reproduce.py` exits 1 at the repo level.**
  That is the fix working, not a regression: the manuscript genuinely prints a false coverage
  number today, and the whole point of F2 is that it used to exit 0 while doing so. The failure
  block names the file, the expected sentence shape, and what to do.
* The deposit build is unaffected and was rebuilt green — see R1.

---

## F1 — §3.3 prints 24; the data says 17

### Re-derivation

`results/all_runs.csv`, 2,173 rows. Two independent readings of the same condition:

```
window_ok == 1  AND  complete != 1                          -> 17
epochs_done > 20  AND  epochs_done < 0.95*epochs_requested   -> 17   (recomputed from the
                                                                      epoch columns, ignoring
                                                                      the flag columns)
of the 17, epochs_done < 0.90*epochs_requested               -> 16
the one that is not:  rs-node-1e4-s1, 94 of 100  (ratio 0.940)
```

The seventeen, sorted by completion fraction:

```
rs-blk6-3e4-s2      24/100  0.240   plateau5 86.332
rs-blk6-1e4-s2      29/100  0.290   plateau5 85.228
rs-blk6-3e5-s2      36/100  0.360   plateau5 85.984
rs-node-1e3-s1      40/100  0.400   plateau5 91.020
rs-blk6-3e3-s1      44/100  0.440   plateau5 90.430
a0-blk6-1e4_s0      50/100  0.500   plateau5 90.866
a0-scal-1e4_s0      50/100  0.500   plateau5 90.828
rs-node-1e2-s1      52/100  0.520   plateau5 89.700
a0-layer-1e4_s0     55/100  0.550   plateau5 91.754
rs-blk6-3e4-s1      59/100  0.590   plateau5 91.328
rs-blk6-1e3-s1      60/100  0.600   plateau5 90.984
rs-node-3e3-s1      64/100  0.640   plateau5 91.082
rs-node-1e2-s0      69/100  0.690   plateau5 90.278
gate0c_scal_m2_s1   81/100  0.810   plateau5 91.616
gate0c_blk6_m2_s1   85/100  0.850   plateau5 90.954
rs-node-3e4-s1      89/100  0.890   plateau5 92.692
rs-node-1e4-s1      94/100  0.940   plateau5 91.892
```

**The paper already contradicts itself on this.** §8's attrition ledger books the same rows as
`− 17` on its `window_ok = 1, complete = 0` line, and its following paragraph says "Only 17 of
the 442 are full-budget runs". `analysis/c98_reproduce.py:93` hard-codes `("complete", 17)` and
PASSES. The stale numeral is §3.3's alone.

### The two dependent claims, both re-verified against 17

**"None of the 24 is in a count-matched arm."** Verified directly, not inherited. Rebuilding the
admissible set with the `complete` gate dropped (1,731 → 1,748 rows, i.e. all seventeen
re-admitted) and re-running `c98_figures.cells()` changes **no** cell's `n`, with or without the
GroupNorm cell:

```
adm 1731 loose 1748 delta 17
cells whose n changes if the 17 are re-admitted: NONE
with GN cell too:                                NONE
```

Consistent with §8's own "256 of 256": the seventeen are `resnet18_blocks` 8, `nodewise` 6,
`scalar` 2, `layerwise` 1 — none is a `chunk*`, `nodewise1d` or `permnode*` run.

**"moves that arm's mean by 1.22 pp and inflates its sem 19-fold."** REPRODUCES EXACTLY; kept
verbatim. The arm is ResNet18 / CIFAR-10 / bs 100 / SGDm base / Lion meta / meta-stepsize 1e-4 /
α₀ 1e-3 / `resnet18_blocks`, i.e. `{rs-blk6-1e4-s0, rs-blk6-1e4-s1, at1-blk6-s0, at1-blk6-s1,
at1-blk6-s2}`:

```
admissible only   n=5   mean 92.530  sem 0.064
+ rs-blk6-1e4-s2  n=6   mean 91.313  sem 1.218
                        Δmean 1.217 pp        sem ratio 19.0x
```

### F1b — one more word in the same sentence is wrong

"**The worst of them**, `rs-blk6-1e4-s2`, ran 29 of 100 epochs" reads as *most truncated*, and
`rs-blk6-1e4-s2` is not: `rs-blk6-3e4-s2` ran **24** of 100. What `rs-blk6-1e4-s2` is, is the
**lowest-accuracy** of the seventeen (`plateau5` 85.228 is the minimum of the column above). The
replacement says so. This is a correction, not a softening — the sentence as printed is false on
its most natural reading.

### REPLACEMENT — `paper/paper.tex`

Anchor: lines 641–648. Verified verbatim and unique (`grep -Fc` = 1).

REPLACE:

```latex
redundant: \textbf{24 of 2{,}173 runs pass \texttt{window\_ok} while having completed under 95\%
of their requested epochs} (23 of the 24 finished under 90\%; the twenty-fourth stopped at 94 of
100). The worst of them, \arm{rs-blk6-1e4-s2}, ran 29 of 100 epochs and still reports \plateau{}
85.228; it sits in a \arm{resnet18\_blocks} arm of the \arm{rs} meta-stepsize sweep, where
including it moves that arm's mean by 1.22 pp and inflates its sem 19-fold. \textbf{None of the
24 is in a count-matched arm of any cell reported in this paper} --- see
the attrition ledger in \S\ref{sec:repro}, where attrition
inside the primary contrasts is zero.
```

WITH:

```latex
redundant: \textbf{17 of 2{,}173 runs pass \texttt{window\_ok} while having completed under 95\%
of their requested epochs} (16 of the 17 finished under 90\%; the seventeenth stopped at 94 of
100). The lowest-accuracy of them, \arm{rs-blk6-1e4-s2}, ran 29 of 100 epochs and still reports
\plateau{} 85.228; it sits in a \arm{resnet18\_blocks} arm of the \arm{rs} meta-stepsize sweep,
where including it moves that arm's mean by 1.22 pp and inflates its sem 19-fold. \textbf{None of
the 17 is in a count-matched arm of any cell reported in this paper} --- see
the attrition ledger in \S\ref{sec:repro}, which books these same seventeen rows as its
\texttt{window\_ok = 1, complete = 0} line and where attrition
inside the primary contrasts is zero.
```

### REPLACEMENT — `paper/DRAFT-v4.md`

Anchor: lines 485–491 (through `is zero.`). Verified verbatim and unique.

REPLACE:

```markdown
redundant: **24 of 2,173 runs pass `window_ok` while having completed under 95% of their
requested epochs** (23 of the 24 finished under 90%; the twenty-fourth stopped at 94 of 100).
The worst of them, `rs-blk6-1e4-s2`, ran 29 of 100 epochs and still reports `plateau5`
85.228; it sits in a `resnet18_blocks` arm of the `rs` meta-stepsize sweep, where including
it moves that arm's mean by 1.22 pp and inflates its sem 19-fold. **None of the 24 is in a
count-matched arm of any cell reported in this paper** — see the attrition ledger in
§8, where attrition inside the primary contrasts is zero.
```

WITH:

```markdown
redundant: **17 of 2,173 runs pass `window_ok` while having completed under 95% of their
requested epochs** (16 of the 17 finished under 90%; the seventeenth stopped at 94 of 100).
The lowest-accuracy of them, `rs-blk6-1e4-s2`, ran 29 of 100 epochs and still reports `plateau5`
85.228; it sits in a `resnet18_blocks` arm of the `rs` meta-stepsize sweep, where including
it moves that arm's mean by 1.22 pp and inflates its sem 19-fold. **None of the 17 is in a
count-matched arm of any cell reported in this paper** — see the attrition ledger in
§8, which books these same seventeen rows as its `window_ok = 1, complete = 0` line and where
attrition inside the primary contrasts is zero.
```

Both replacements are census-neutral: `24`, `23`, `17`, `16` are integers, and the census counts
only `/\d+\.\d+/`. No decimal numeral is added or removed.

---

## F2 — §3.4 prints "216 of the 725 … 29.8%"; the code prints 747 and 28.9%

### Re-derivation, and why the sentence could go stale

`python3 analysis/c98_reproduce.py --census`, run before any edit in this cycle:

```
  every /\d+[.]\d+/ in the file                         2350  (858 distinct)
  ...minus code blocks and indented verbatim scorer
     output (numbers the SCORERS print, not ours)       1924  (759 distinct)
  ...minus section, table, figure and equation labels,
     arXiv ids and software versions  = QUANTITIES      1696  (747 distinct)
  chk() assertion sites executed in this run             283
  distinct quantity-numerals this run asserts            216
  coverage of distinct quantity-numerals                28.9%
```

So the manuscript's `725` and `29.8%` were both wrong, and `--census` exited 0 anyway, because
it only ever measured. The sentence that answers reviewer item A8 was itself unasserted.

**Then the number moved again inside this task.** After the `M1` package landed
`[15] METRIC SENSITIVITY` in `analysis/c98_reproduce.py`, the same command prints:

```
     arXiv ids and software versions  = QUANTITIES      1696  (747 distinct)
  chk() assertion sites executed in this run             353
  distinct quantity-numerals this run asserts            231
  coverage of distinct quantity-numerals                30.9%
```

The replacement text below uses **353 / 231 / 747 / 30.9%**. See the warning at the top.

### The code fix — the census now ASSERTS, and asserts against the paper itself

`analysis/c98_reproduce.py`:

1. New section `[16] THE COVERAGE CENSUS, ASSERTED`, registered **last** in `SECTIONS`.
2. **The `paper` value is parsed out of `DRAFT-v4.md`, not duplicated in a constant.** Every
   other `chk()` compares a derived value against a number a human copied from the manuscript;
   for this one the manuscript's own sentence *is* the constant. There is therefore no second
   place that can drift, and rewording the sentence out of shape fails loudly (`**FAIL** could
   not find §3.4's coverage sentence`, printing the expected shape) instead of passing quietly.
   The required shape:

   ```
   ... the audit executes **N claim-carrying assertions covering C of the Q distinct
   quantity-numerals** in this manuscript, which is P% of them ...
   ```

   matched after whitespace/`*`/`` ` `` normalisation, with `claim-carrying` optional so the
   parser also reads the *current*, pre-fix sentence and reports it as stale rather than
   unparseable.
3. **The census never counts itself.** `censuscheck()` freezes `CENSUS_MARK = len(ASSERTED)`
   before it asserts, and `census()` reads `ASSERTED[:CENSUS_MARK]`. The four self-referential
   sites are excluded from both the assertion count and the coverage they report, so the
   quantity is a fixpoint by construction rather than by luck.
4. `--census` alone **now exits 1** on a false sentence and prints the failing lines.
5. New `--allow-stale-census`: reports a stale §3.4 sentence but does not exit non-zero.
   `c98_release.py` passes it, because the deposit ships no manuscript and the README's own
   census sentence is generated from the *measured* census, never from §3.4 — so a stale
   coverage sentence is a manuscript defect, not an artefact defect. Every other failed check
   still refuses the build. The stale lines stay in `REPRODUCTION-AUDIT.txt`, and the build
   prints a three-line warning. **This flag must never be used to close F2.**

Behaviour, verified:

```
python3 analysis/c98_reproduce.py                       -> exit 1   (§3.4 stale today)
python3 analysis/c98_reproduce.py --census              -> exit 1   (§3.4 stale today)
python3 analysis/c98_reproduce.py --allow-stale-census  -> exit 0
python3 analysis/c98_reproduce.py --table2 --no-census  -> exit 0   (partial run: [16] skips)
release/  make reproduce                                -> exit 0   ([16] skips: no manuscript)
```

### FIXPOINT PROOF

`DRAFT-v4.md` was copied to a scratch file, **both** the F1 and the F2 replacements below were
applied to it, and the audit was re-run against that copy:

```
[16] THE COVERAGE CENSUS, ASSERTED  (§3.4 Registration and scope)
  chk() assertion sites executed                 353 | paper 353 | PASS   §3.4
  distinct quantity-numerals asserted            231 | paper 231 | PASS   §3.4
  distinct quantity-numerals in the draft        747 | paper 747 | PASS   §3.4
  coverage of distinct quantity-numerals         30.9 | paper 30.9 | PASS   §3.4

ALL 357 CHECKS PASS.

  ...minus section, table, figure and equation labels,
     arXiv ids and software versions  = QUANTITIES      1696  (747 distinct)
  chk() assertion sites executed in this run             353
  distinct quantity-numerals this run asserts            231
  coverage of distinct quantity-numerals                30.9%
```

Converged in one step. Why it converges: the only decimal numeral the edit touches is the
percentage, `29.8` → `30.9`; `29.8` occurred exactly once in the draft and `30.9` zero times, so
the distinct-quantity total is unchanged at 747, and neither string is an asserted paper value,
so the covered count is unchanged at 231. Every other numeral the two replacements touch (`24`,
`23`, `17`, `16`, `725`, `747`, `283`, `353`, `216`, `231`, `[16]`) is an integer and invisible to
the `/\d+\.\d+/` census.

### REPLACEMENT — `paper/paper.tex`

Anchor: lines 914–916. Verified verbatim and unique. **Note the `.tex` currently says "We print
the fraction" without printing a fraction — the replacement supplies it, which also brings the
two files into sync.**

REPLACE:

```latex
scorer, not re-derived. Measured by \texttt{python3 analysis/c98\_reproduce.py --census}, the
audit executes \textbf{283 assertions covering 216 of the 725 distinct quantity-numerals} in this
manuscript. We print the fraction rather than a superlative because a superlative is exactly the
```

WITH:

```latex
scorer, not re-derived. Measured by \texttt{python3 analysis/c98\_reproduce.py --census}, the
audit executes \textbf{353 claim-carrying assertions covering 231 of the 747 distinct
quantity-numerals} in this manuscript, which is 30.9\% of them. Those three figures are not
merely measured: section \texttt{[16]} of the audit reads this sentence back out of the
manuscript and asserts the triple against a fresh measurement, so a stale coverage claim now
exits non-zero instead of passing quietly, which is what it did for three review cycles. (The
four sites that do that self-check are excluded from the count and from the coverage they
report, so the census never counts itself.) We print the fraction rather than a superlative
because a superlative is exactly the
```

### REPLACEMENT — `paper/DRAFT-v4.md`

Anchor: lines 720–722. Verified verbatim and unique. **This is the file the parser reads: if only
the `.tex` is updated, the audit still exits 1.**

REPLACE:

```markdown
from the scorer, not re-derived. Measured by `python3 analysis/c98_reproduce.py --census`, the
audit executes **283 assertions covering 216 of the 725 distinct quantity-numerals** in this
manuscript, which is 29.8% of them. We print the fraction rather than a superlative because a superlative is exactly the
```

WITH:

```markdown
from the scorer, not re-derived. Measured by `python3 analysis/c98_reproduce.py --census`, the
audit executes **353 claim-carrying assertions covering 231 of the 747 distinct
quantity-numerals** in this manuscript, which is 30.9% of them. Those three figures are not
merely measured: section `[16]` of the audit reads this sentence back out of the manuscript
and asserts the triple against a fresh measurement, so a stale coverage claim now exits
non-zero instead of passing quietly, which is what it did for three review cycles. (The four
sites that do that self-check are excluded from the count and from the coverage they report,
so the census never counts itself.) We print the fraction rather than a superlative because a superlative is exactly the
```

---

## R1 — the deposit README's two surviving over-claims

`analysis/c98_release.py`. Line 343 was fixed last cycle; lines 256 and 320 were not. Both now
match §8's actual register.

### 320 — the README's "What this is"

WAS:

```
Everything behind every number in the paper, and a script that re-derives them
and checks them against what the paper prints.
```

Refuted by §8's own deposit-reachability register (2 REACHED / 2 PARTIAL / 6 BLOCKED) and by the
census. NOW (as generated into `release/README.md`):

```
The run table, the raw per-epoch logs, the submission scripts, the optimiser
patches, the registered scorers and the figure code behind the paper — and an
audit that re-derives *the numbers that carry a claim* and checks each one against
what the paper prints.

    make reproduce

runs in a few seconds on a laptop, needs `python3` and `matplotlib` and nothing
else, and exits non-zero if any of them fails to reproduce. It prints one line per
number: *derived value | paper value | PASS/FAIL | where it appears*.

**It does not check every numeral the paper prints, and neither this file nor the
paper claims it does.** The audit's own header lists what is in scope and what is
out — prose-only quantities, group counts, wallclock and byte counts, and any value
that exists only inside a registered scorer's printed output are out — and section
3.4 of the paper states the same scope.

Measured at build time against the manuscript, it executed 353 claim-carrying
assertions covering 231 of the 747 distinct quantity-numerals the manuscript
prints, which is 30.9% of them. The audit asserts that triple as well as
measuring it, so the coverage claim cannot drift unnoticed; the census block
it comes from is at the foot of `REPRODUCTION-AUDIT.txt`.

Two further limits, stated here rather than left to be found. This deposit ships
no manuscript, so `--census` has nothing to re-measure against here and the audit
reports that section as skipped. And of the ten registered scorers the paper
quotes or relies on, run unedited against this deposit alone, two reach their
quoted verdict in full, two reach part of it, and six halt or print `NO DATA`,
because they read the `probe*.jsonl` traces that *What is not here* excludes. Run
`code/c98_reproduce.py --deposit` for that register; section 8 of the paper prints
the same table.
```

The census paragraph is **generated, not typed** — new `census_sentence()` cuts the four figures
out of the audit's own output at build time, exactly as `headline_block()` already does for the
headline numbers, and falls back to a pointer at the command if the census could not run.

### 256 — `ENVIRONMENT.md`

WAS:

```
**The analysis side needs none of this.** Reproducing every number in the paper
needs `python3` and `matplotlib` only — no GPU, no PyTorch, no cluster. The
optimiser environment above is what would be needed to *re-run* the experiments.
```

NOW (as generated into `release/ENVIRONMENT.md`):

```
**The analysis side needs none of this.** `make reproduce` needs `python3` and
`matplotlib` only — no GPU, no PyTorch, no cluster. What it re-derives is *the
numbers that carry a claim*, which is a strict subset of the numerals the paper
prints: `code/c98_reproduce.py` states that scope in its own header, section 3.4 of
the paper states it in prose, and `--census` measures it against the manuscript.
The optimiser environment above is what would be needed to *re-run* the
experiments; section 8 of the paper lists, as a table rather than as a caveat, the
registered scorers that this deposit alone cannot re-run at all.
```

### Deposit rebuilt

```
[1/6] regenerating figures
[2/6] running the reproduction audit
    ** WARNING: the paper's section 3.4 coverage sentence is behind the
    ** code.  The deposit is unaffected and was built; the MANUSCRIPT
    ** must be fixed and the deposit rebuilt before the DOI is minted.
[3/6] copying data, code, scripts, patches, figures, docs
[4/6] archiving the raw per-epoch .out logs
[5/6] writing README, ENVIRONMENT, Makefile, CITATION
[6/6] writing MANIFEST.md5

release/ built: 137 files, 6.3 MB
```

### `make verify` — pasted verbatim

```
$ cd release && make verify
python3 code/verify_manifest.py
137 files checked, 0 bad
VERIFY EXIT=0
```

### `make reproduce` — pasted verbatim (455-line output; head and tail)

```
$ cd release && make reproduce
python3 code/c98_reproduce.py --csv data/all_runs.csv
==============================================================================
REPRODUCTION AUDIT -- data/all_runs.csv
==============================================================================

[1] CORPUS  (§8 Reproducibility, Appendix A.8)
  rows in results/all_runs.csv                   2173 | paper 2173 | PASS   abstract, §8
  admissible rows                                1731 | paper 1731 | PASS   §3.3, A.8
  runs carrying a wallclock                      2158 | paper 2158 | PASS   §8
  GPU-hours                                      1632 | paper 1632 | PASS   abstract, §8
  distinct nodes                                 29 | paper 29 | PASS   §8
  rows failing window_ok                         425 | paper 425 | PASS   §3.3 attrition
  rows failing complete                          17 | paper 17 | PASS   §3.3 attrition
  rows with no plateau5                          25 | paper 25 | PASS   §3.3 attrition

  ... [sections 2-15] ...

[16] THE COVERAGE CENSUS, ASSERTED  (§3.4 Registration and scope)
  no manuscript in this tree (the deposit ships none), so §3.4's coverage cannot be re-measured here -- SECTION SKIPPED (censuscheck)

==============================================================================
ALL 342 CHECKS PASS.
2 SECTION(S) COULD NOT RUN HERE, so this is not full coverage:
   [7] BUDGET             raw hz3 .out series not found
   censuscheck            no manuscript in this tree (the deposit ships none), so §3.4's coverage cannot be re-measured here
==============================================================================

[census] .../release/paper/DRAFT-v4.md not found -- census skipped
REPRODUCE EXIT=0
```

Note line 8 of that output: the deposit's own audit prints **`rows failing complete  17 | paper
17 | PASS`**. F1's `24` was contradicted by the artefact the paper ships.

---

## NEW PROBLEMS FOUND (not in the 15; flagged, two acted on)

1. **A stray backup file was about to ship in the deposit.** The first rebuild produced **138**
   files against a paper that prints 137, because `bin/c98_hz3_s5_box30.sh.bak_wall10` — a
   mid-flight backup left by the concurrent hz3-R2 work — was copied by
   `c98_release.py`'s blanket "every file in `bin/`" walk. **Acted on:** added `skipfile()`, a
   junk filter for `.bak*/.orig/.rej/.swp/.tmp/.old/~/dotfiles/.pyc`, applied to `bin/`,
   `patches/` and `tests/`. Rebuild is back to 137 files, and the deposit's file count can no
   longer move because somebody left an editor dropping beside a submission script. The stray
   file itself was **not** touched — it belongs to another agent.

2. **`6.2 MB` is now false in four places.** The rebuilt deposit is 6,264,386 bytes across 137
   files, which the build's own `%.1f` of `bytes/1e6` renders as **6.3 MB**. Printed at
   `paper.tex:3361`, `paper.tex:3951`, `DRAFT-v4.md:2657`, `DRAFT-v4.md:3131`. **Not acted on**
   and deliberately not given as replacement text: the figure is rounding-marginal (6.264) and
   genuinely volatile — it moves with `logs/raw_out.tar.gz`, which grows as hz3-R2's `.out`
   files land. **Re-derive it from `head -1 release/MANIFEST.md5` at the FINAL deposit build and
   fix all four sites then.** The `137 files` half of each sentence is currently correct.

3. **`--census` cannot run inside the deposit, but §8 tells the reader to run it there.**
   §8's "One command" paragraph says `python3 code/c98_reproduce.py --census` measures the
   scope; the deposit ships no `paper/DRAFT-v4.md`, so it prints `census skipped`. The rebuilt
   README now states this limit explicitly, but **§8's sentence is still misleading** and is
   outside this package's scope. Flagged for whoever owns §8.

---

## FILES TOUCHED BY THIS PACKAGE

* `analysis/c98_reproduce.py` — `CENSUS_MARK`; `census()` reads `ASSERTED[:CENSUS_MARK]` and
  prints that count; `_CENSUS_RE` / `_census_claim()` / `censuscheck()` (section `[16]`,
  registered last); `--allow-stale-census`; `--census` now exits 1 on failure; docstring.
  **No existing check was altered, removed, or loosened.**
* `analysis/c98_release.py` — `import re`; `skipfile()`; `census_sentence()`; the ENVIRONMENT
  over-claim (was line 256); the README over-claim (was line 320); `%(census)s` substitution;
  the audit invocation now passes `--allow-stale-census` and warns when it fires.
* `release/` — rebuilt, 137 files, 6.3 MB. `make verify` 0 bad; `make reproduce` exit 0.
* `paper/sections/v5-false-numbers.md` — this file.

**NOT touched:** `paper/paper.tex`, `paper/DRAFT-v4.md`, `results/all_runs.csv`, any registered
scorer, any file in `bin/`. No `git commit` was run. No Slurm job was submitted.
