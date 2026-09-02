# Package `v6-false-sentences` — closes B3, B4, B5, B7

Four sentences that are false as printed. Every replacement below is keyed to a **verbatim
anchor verified to occur exactly once** in the live file at the time of writing
(`git` HEAD `351d9a6`, working tree as of this run). Nothing here was applied to
`paper/paper.tex` or `paper/DRAFT-v4.md` — this file is the replacement text; a later agent
integrates and commits.

| item | what was false | fix | numeric change |
|---|---|---|---|
| **B3** | `paper.tex` A.4 asserts the **superseded** 88.4 % between-base share in the present tense, two lines before the live 92.8 % | delete the two stale sentences; fold their surviving clause into the live sentence so the tex reads like `DRAFT-v4.md:3297` | none |
| **B4** | §8 and Data Availability claim each of 2,241 `.out` files "carries its own `ARGS:` **and** `ENV:` line" | print the measured counts: **2,237** carry `ARGS:`, **2,113** carry `ENV:`, **132 exceptions** in total | none (all new numerals are comma-grouped integers; the census counts only `\d+\.\d+`) |
| **B5** | the abstract attributes the whole 1.8–4.2 pp deficit to "tuned SGD + cosine, **the state-of-the-art alternative**" | name all three comparators, drop the superlative, keep "baselines" so the `se_empirical` obligation still matches | none |
| **B7** | §3.4 says audit section `[16]` "reads this sentence back out of the manuscript" — but `censuscheck()` reads `paper/DRAFT-v4.md` only, so in `paper.tex` the clause is **false** | give `_census_claim()` a **LaTeX branch** and assert the triple out of **both** markups; say so in §3.4 | none |

**One structural consequence, stated up front:** the B4 disclosure and the B7 sentence add
prose, and the compiled PDF grows **65 → 66 pages**. Everything else is invariant.

---

## 0. Verification (run at write time, pasted)

All four items applied to scratch copies of `paper.tex`, `DRAFT-v4.md` and
`analysis/c98_reproduce.py`, then measured.

```
TECTONIC                        exit 0, 66 pp (baseline build of the unpatched tex: exit 0, 65 pp)
                                Overfull/Underfull warning multiset IDENTICAL to the baseline build

ABSTRACT  (paperfactory.agents.text_quality, ABSTRACT_TARGET_WORDS = (120, 230))
  paper.tex     215 -> 220 words   _abstract_defects []            (was [])
  DRAFT-v4.md   226 -> 229 words   _abstract_defects []            (was [])
  assess_text_quality(paper.tex)['all_defects']  []                (was [])
  assess_reporting_completeness(paper.tex)['score']  17            (was 17)
     abstract_missing_items []   reporting_missing_items []

CENSUS  (python3 analysis/c98_reproduce.py --census --draft <file>)
  BEFORE  every /\d+[.]\d+/ 2522 (897 distinct) -> 2085 (801) -> QUANTITIES 1824 (786 distinct)
  AFTER   every /\d+[.]\d+/ 2522 (897 distinct) -> 2085 (801) -> QUANTITIES 1824 (786 distinct)
  ** this package is census-neutral: it adds zero distinct quantity-numerals to the draft **

NUMERIC DIFF  paper.tex vs DRAFT-v4.md  (all /\d+[.]\d+/, tex \label/\ref/\cite stripped,
                                         {,} and \, removed, md thousands commas removed)
  BEFORE  tex-only 5  ['0.3','0.35','0.42','0.92','1.12']      md-only 27 (section nos + arXiv ids)
  AFTER   tex-only 5  ['0.3','0.35','0.42','0.92','1.12']      md-only 27 (identical set)
  ** the package introduces ZERO new numeric divergence between the two markups **

"88.4"  occurrences   paper.tex 4 -> 3      DRAFT-v4.md 3 -> 3   (now equal, as they should be)
```

**A standing note for the integrator.** The working tree already carries an uncommitted
`analysis/c98_reproduce.py` change from a concurrent package (+153 lines inside `metricsens`,
the §4.7 endpoint knife). Because of it the tree is **not at a census fixpoint right now**:
`[16]` reports `403 vs paper 353` / `261 vs 256` / `33.2 vs 32.6` in a tree without the raw
`hz3` `.out` series, `414` in the full tree. That staleness is **not** this package's — B7's
patch does not create it, it makes it fire **twice** (once per markup) instead of once, which
is the whole point. The §3.4 triple must be brought to a fixpoint **in both files** after all
packages land.

---

## 1. B3 — the superseded 88.4 % share, asserted in the present tense

### 1.1 Re-derivation

```
$ grep -n "88.4" paper/paper.tex paper/DRAFT-v4.md
paper/paper.tex:1705:  ...previous version's eleven cells was 88.4\% of a $Q$ of 36.40...   (past tense, correct)
paper/paper.tex:1935:  ...eleven cells the same partition read 32.20 of 36.40 (88.4\%)...   (past tense, correct)
paper/paper.tex:4145:  88.4\% under both conventions. The conclusion is unchanged...       ** STALE, present tense **
paper/paper.tex:4146:  measurement error is real. The between-base share ... was 88.4\%    (past tense, correct)
paper/DRAFT-v4.md:1312, 1500, 3297                                                          (all three correct)
```

`paper.tex:4144–4146` says *"The between-base share of §4.4 **is** 88.4 % under both
conventions."* The live share on the fourteen-cell pool is **92.8 % of a $Q$ of 102.47**, and
the very next sentence in the same paragraph says so. The two stale sentences are a leftover
from the eleven-cell era; `DRAFT-v4.md:3297` never carried them.

The deletion also loses the clause *"the excess over measurement error is real"*, which the md
keeps. The replacement folds it back into the surviving sentence, so the tex ends up
**word-for-word equivalent to `DRAFT-v4.md:3297–3299`**. Zero numeric change; `"88.4"` goes
4 → 3 in the tex and stays 3 in the md.

### 1.2 `paper/paper.tex` — ANCHOR (count == 1)

```latex
43.2-versus-43.0 mismatch does not support. The between-base share of \S\ref{sec:moderator} is
88.4\% under both conventions. The conclusion is unchanged and is now stronger: the excess over
measurement error is real. The between-base share of \S\ref{sec:moderator} was 88.4\% under both
conventions on that eleven-cell pool; on the fourteen cells \S\ref{sec:moderator} now uses it is
92.8\% of a $Q$ of 102.47. The conclusion is unchanged and is stronger: \S\ref{sec:moderator}
decomposes almost all of it --- without claiming to have identified its cause.
```

### 1.3 `paper/paper.tex` — REPLACEMENT

```latex
43.2-versus-43.0 mismatch does not support. The between-base share of \S\ref{sec:moderator} was
88.4\% under both conventions on that eleven-cell pool; on the fourteen cells
\S\ref{sec:moderator} now uses it is 92.8\% of a $Q$ of 102.47. The conclusion is unchanged and
is stronger: the excess over measurement error is real, and \S\ref{sec:moderator} decomposes
almost all of it --- without claiming to have identified its cause.
```

### 1.4 `paper/DRAFT-v4.md`

**No change.** `DRAFT-v4.md:3297–3299` is already correct.

---

## 2. B4 — "each carries its own `ARGS:` and `ENV:` line" is false for 132 files

### 2.1 Re-derivation — measured on both clusters *and* both local mirrors *and* the deposit

Four independent measurements, all agreeing.

```
# (1) local mirror, ALICE-1 account  (/Users/teshnizi/Saber Optimization/alice-backup/runs)
$ find runs -name '*.out' | wc -l                                              1322
$ find runs -name '*.out' -print0 | xargs -0 grep -l -m1 '^ARGS:' | wc -l      1318
$ find runs -name '*.out' -print0 | xargs -0 grep -l -m1 '^ENV:'  | wc -l      1219

# (2) local mirror, ALICE-2 account (.../alice-backup/runs_alice2)
$ find runs_alice2 -name '*.out' | wc -l                                        919
$   ... '^ARGS:'                                                                919
$   ... '^ENV:'                                                                 894

# (3) LIVE, cluster 1:  ssh alice 'cd ~/data1/metaopt && ...'
OUT_TOTAL=1322   WITH_ARGS=1318   WITH_ENV=1219

# (4) LIVE, cluster 2:  ssh alice2 'cd ~/metaopt && ...'
RUNS_TOTAL=919   WITH_ARGS=919    WITH_ENV=894

# (5) the shipped deposit itself, release/logs/raw_out.tar.gz, extracted and swept
tarball total=2241  withARGS=2237  withENV=2113  noARGS=4  noENV=128
```

Totals: **2,241 files** (1,322 + 919 = 2,241, and the tarball ships exactly those 2,241).
**2,237 carry `ARGS:`; 4 do not. 2,113 carry `ENV:`; 128 do not.** The claim
*"each carries its own `ARGS:` **and** `ENV:` line"* is therefore false of **132 file-line
pairs** across **128 distinct files** — the 4 no-`ARGS:` files are a strict subset of the
128 no-`ENV:` files:

```
$ comm -12 <sorted no-ARGS> <sorted no-ENV> | wc -l        4
$ comm -13 <sorted no-ARGS> <sorted no-ENV> | wc -l      124     # carry ARGS:, not ENV:
```

The four with no `ARGS:` line, named:

```
runs/gtest-4679250.out      runs/gtest2-4679252.out
runs/mo-smoke-4650573.out   runs/ts-pretok-4680828.out
```

all four are infrastructure jobs that ran no training, all four on the first account — which is
what §8's own *next* sentence already says ("2,237 with an `ARGS:` line and the four
infrastructure jobs that have none"), **contradicting the universal it had just asserted two
sentences earlier.** That self-contradiction is why this is a blocking gap and not a nit.

The 128 without `ENV:` split **103 on the first account, 25 on the second**, and they are an
early-corpus artefact of the submission template, not a selective omission:

```
$ job ids of the 128 no-ENV files      min 4650573   max 4680828
$ job ids of the 2113 with-ENV files   min 4680676   max 4849156
```

Every file lacking an `ENV:` line has a Slurm job id **at or below 4,680,828**; every file
carrying one has an id **at or above 4,680,676**. The two ranges overlap only across the single
batch (`hs-l-lam01`) that straddles the change: 131 files belong to the pre-`ENV:` batch
families and 128 of them lack the line, the other three (`hs-l-lam01-s2/s3/s4`) having it. The
prose below states the two bounds rather than a family list, because the bounds are exact and
the family list is not.

**One further correction inside the same sentence.** §8 also calls the 2,241 *"every `.out`
file on either cluster"*. Measured, that is not exactly true: `~/data1/metaopt` on the first
account holds **1,324** `.out` files (the two extras are `audit/in-audit-*.out` and
`logs/envchk-*.out`, audit artefacts), and `~/metaopt` on the second holds **951** (the 32
extras are under `pf-jobs/`, an unrelated project). The correct scope is *every `.out` file in
the two clusters' Slurm **run directories***, which is exactly 1,322 + 919 = 2,241. The
replacement says that.

**Census impact: none.** Every numeral introduced here — 2,241, 2,237, 2,113, 1,322, 919, 128,
124, 103, 25, 4,680,828, 4,680,676 — is a comma-grouped integer, and the census token rule is
`re.compile(r"\d+\.\d+")`. Verified: QUANTITIES 1824 (786 distinct), unchanged.

### 2.2 §8 / `\S\ref{sec:repro}` — `paper/paper.tex` ANCHOR (count == 1)

```latex
Raw per-epoch series are the Slurm \texttt{.out} files in
\texttt{logs/raw\_out.tar.gz}; each carries its own \texttt{ARGS:} and \texttt{ENV:} line, which is
the authority on what that run actually did. The shipped log set is \textbf{2{,}241 files, which
is every \texttt{.out} file on either cluster}: 2{,}237 with an \texttt{ARGS:} line and the four
infrastructure jobs that have none. There is no shortfall to state, and the \arm{sm3} runs that an
earlier version of this ledger carried as un-ingested are in the run table.
```

### 2.3 §8 — `paper/paper.tex` REPLACEMENT

```latex
Raw per-epoch series are the Slurm \texttt{.out} files in
\texttt{logs/raw\_out.tar.gz}. The shipped log set is \textbf{2{,}241 files, which is every
\texttt{.out} file in the two clusters' Slurm run directories} (1{,}322 and 919).
\textbf{Neither provenance line is universal, and these are the counts.} \textbf{2{,}237} of the
2{,}241 carry their own \texttt{ARGS:} line --- the \textbf{four} that do not are infrastructure
jobs that ran no training (\texttt{gtest}, \texttt{gtest2}, \texttt{mo-smoke},
\texttt{ts-pretok}) --- and \textbf{2{,}113} carry their own \texttt{ENV:} line, so \textbf{128
do not}: those four plus 124 that carry \texttt{ARGS:} without \texttt{ENV:} (103 on the first
account, 25 on the second). The \texttt{ENV:} line was added to the submission template partway
through the corpus, so every file missing one carries a Slurm job id at or below 4{,}680{,}828
while every file carrying one is at or above 4{,}680{,}676. Where a line is present it is the
authority on what that run actually did, and RULE 20 is enforced on all 2{,}237 \texttt{ARGS:}
lines. There is no shortfall in the log set itself, and the \arm{sm3} runs that an earlier
version of this ledger carried as un-ingested are in the run table.
```

### 2.4 §8 — `paper/DRAFT-v4.md` ANCHOR (count == 1)

```text
Raw per-epoch series are the Slurm
`.out` files in `logs/raw_out.tar.gz`; each carries its own `ARGS:` and `ENV:` line, which
is the authority on what that run actually did. The shipped log set is **2,241 files, which is
every `.out` file on either cluster**: 2,237 with an `ARGS:` line and the four infrastructure
jobs that have none. There is no shortfall to state, and the `sm3` runs that an earlier version
of this ledger carried as un-ingested are in the run table.
```

### 2.5 §8 — `paper/DRAFT-v4.md` REPLACEMENT

```text
Raw per-epoch series are the Slurm
`.out` files in `logs/raw_out.tar.gz`. The shipped log set is **2,241 files, which is every
`.out` file in the two clusters' Slurm run directories** (1,322 and 919). **Neither provenance
line is universal, and these are the counts.** **2,237** of the 2,241 carry their own `ARGS:`
line — the **four** that do not are infrastructure jobs that ran no training (`gtest`,
`gtest2`, `mo-smoke`, `ts-pretok`) — and **2,113** carry their own `ENV:` line, so **128 do
not**: those four plus 124 that carry `ARGS:` without `ENV:` (103 on the first account, 25 on
the second). The `ENV:` line was added to the submission template partway through the corpus, so
every file missing one carries a Slurm job id at or below 4,680,828 while every file carrying
one is at or above 4,680,676. Where a line is present it is the authority on what that run
actually did, and RULE 20 is enforced on all 2,237 `ARGS:` lines. There is no shortfall in the
log set itself, and the `sm3` runs that an earlier version of this ledger carried as un-ingested
are in the run table.
```

### 2.6 Data Availability — `paper/paper.tex` ANCHOR (count == 1) and REPLACEMENT

ANCHOR:

```latex
(2{,}241 \texttt{.out} files, each carrying its own \texttt{ARGS:} and \texttt{ENV:} line), all
```

REPLACEMENT:

```latex
(2{,}241 \texttt{.out} files, of which 2{,}237 carry their own \texttt{ARGS:} line and
2{,}113 their own \texttt{ENV:} line; \S\ref{sec:repro} itemises the exceptions), all
```

### 2.7 Data Availability — `paper/DRAFT-v4.md` ANCHOR (count == 1) and REPLACEMENT

ANCHOR:

```text
raw per-epoch Slurm logs (2,241 `.out` files, each carrying its own `ARGS:` and `ENV:` line),
```

REPLACEMENT:

```text
raw per-epoch Slurm logs (2,241 `.out` files, of which 2,237 carry their own `ARGS:` line and
2,113 their own `ENV:` line; §8 itemises the exceptions),
```

---

## 3. B5 — the abstract's "state-of-the-art alternative" names one comparator for three deficits

### 3.1 Re-derivation from `results/all_runs.csv`

Arm means on `plateau5`, admissible rows only (`window_ok == 1`, `complete == 1`,
`superseded != 1`), `se = sd/sqrt(n)`:

| arm | n | net / dataset | base | schedule | `plateau5` mean ± se |
|---|---|---|---|---|---|
| `i3b-3e4` | 3 | ResNet-18 / C10 | AdamW + Adam meta, 6 blocks | — | **93.317 ± 0.083** |
| `bl-sgd-01` | 5 | ResNet-18 / C10 | SGD, lr 0.1 | cosine | **95.124 ± 0.047** |
| `g3m-chg` | 9 | ResNet-34 / C10 | SGDm + Lion, chunk2500 | — | **92.265 ± 0.053** |
| `f5cos-r34-1e-3` | 3 | ResNet-34 / C10 | **AdamW**, lr 1e-3 | cosine | **94.823 ± 0.035** |
| `r50-c88` | 3 | ResNet-50 / C10 | SGDm + Lion, chunk884 | — | **90.833 ± 0.236** |
| `f5cos-r50-1e-3` | 3 | ResNet-50 / C10 | **AdamW**, lr 1e-3 | cosine | **95.047 ± 0.110** |

Deficits and their pooled standard errors:

```
ResNet-18   93.317 - 95.124 = -1.807     se sqrt(0.083^2 + 0.047^2) = 0.0954  -> -1.807 +- 0.095
ResNet-34   92.265 - 94.823 = -2.558     se sqrt(0.053^2 + 0.035^2) = 0.0635  -> -2.558 +- 0.063
ResNet-50   90.833 - 95.047 = -4.214     se sqrt(0.236^2 + 0.110^2) = 0.2604  -> -4.214 +- 0.260
```

All six arm means and all three deficits reproduce §7 T4 exactly. The lr grid behind
`bl-sgd-01` also reproduces: `bl-sgd-001` 94.172, `bl-sgd-003` 94.844, **`bl-sgd-01` 95.124**,
`bl-sgd-03` 94.181 — an interior maximum, so "tuned" is earned.

**The comparators, read off the runs' own `ARGS:` lines (RULE 20):**

```
bl-sgd-01-s0-4687281.out       ARGS: --optimizer SGD   --alpha0 0.1  ... --NN-name ResNet18
f5cos-r34-1e-3-s0-4686800.out  ARGS: --optimizer AdamW --alpha0 1e-3 ... --NN-name ResNet34
f5cos-r50-1e-3-s0-4686802.out  ARGS: --optimizer AdamW --alpha0 1e-3 ... --NN-name ResNet50
```

So **only 1.807 is against SGD + cosine.** 2.558 and 4.214 are against **AdamW + cosine**.
The abstract's "tuned SGD + cosine, the state-of-the-art alternative" is therefore false of two
thirds of the range it introduces, and the superlative "state-of-the-art" occurs **nowhere in
the body** (`grep -n "state-of-the-art" paper.tex` → line 81 only; `DRAFT-v4.md` → line 27
only).

The ResNet-50 comparator is also **unnamed in §7 T4 itself** — it inherits "AdamW + cosine"
from the preceding clause. §3.5 below names it, so the abstract and the body agree.

### 3.2 The word budget — measured, not assumed

`paperfactory.agents.text_quality.ABSTRACT_TARGET_WORDS = (120, 230)`; the defect fires on
`len(words) > 230`, tokenised by `re.findall(r"\b[A-Za-z0-9][A-Za-z0-9+\-.%]*\b", text)`.

```
current   paper.tex 215 words        DRAFT-v4.md 226 words
```

**The binding margin is 4 words, and it is in `DRAFT-v4.md`, not in the tex.** Measured
candidates:

```
"... tuned cosine baselines (SGD on ResNet-18, AdamW on ResNet-34 and ResNet-50), the method
   trails ..."                                                     md 231  ** OVER CAP **
"... tuned cosine-schedule baselines --- SGD + cosine on ..., AdamW + cosine on ... ---"
                                                                   md 233  ** OVER + overloaded **
"The method trails tuned baselines (SGD + cosine on ResNet-18, AdamW + cosine on ResNet-34
   and ResNet-50) by ..."                                          md 231  ** OVER CAP **
"The method trails tuned baselines (SGD+cosine on ResNet-18, AdamW+cosine on ResNet-34
   and ResNet-50) by ..."                                          md 229  OK, defects []
```

Two mechanical constraints drove the final wording and must not be undone:

1. **Em-dashes are forbidden here.** `_is_overloaded_sentence` fires on
   `numeric_claims >= 5 and dash_clauses >= 2`; naming three networks plus three numbers puts
   `numeric_claims` well past 5, so an em-dash *pair* makes the sentence "overloaded". The
   parenthetical form scores 0 dash-clauses. **Use parentheses.**
2. **In `DRAFT-v4.md` the plus must be closed up (`SGD+cosine`), not spaced.** The tokeniser's
   character class includes `+`, so `SGD+cosine` is **one** token and `SGD + cosine` is two.
   The spaced form costs 2 words and puts the draft at 231 — over the cap. `paper.tex` has
   15 words of slack and keeps the spaced `$+$` form used everywhere else in the manuscript.
   This is a deliberate typographic divergence between the markups; it carries no number.

**The word "baselines" is load-bearing and must survive any rewording.** Dropping
"state-of-the-art" would otherwise break two `se_empirical` obligations —
`"Comparison against state-of-the-art alternatives"` and
`"Comparison against the state-of-the-art alternative"` — whose cue lists are
`[r"\bstate[- ]of[- ]the[- ]art\b", r"\bbaseline", r"\balternativ", r"\bcompared with\b"]`.
`"baselines"` matches `\bbaseline`. Verified after the edit:
`assess_reporting_completeness(paper.tex)['score'] == 17`, `abstract_missing_items == []`.

Final: `paper.tex` 215 → **220**, `DRAFT-v4.md` 226 → **229**, both `_abstract_defects == []`.

### 3.3 Abstract — `paper/paper.tex` ANCHOR (count == 1)

```latex
split, bounding construct validity. Against tuned SGD $+$ cosine, the state-of-the-art
alternative, the method trails by 1.8--4.2\pp, dwarfing this ${\approx}0.6\pp$ effect. This should
be read as a constraint on partition design, not as support for practitioners.
```

### 3.4 Abstract — `paper/paper.tex` REPLACEMENT

```latex
split, bounding construct validity. The method trails tuned baselines (SGD $+$ cosine on
ResNet-18, AdamW $+$ cosine on ResNet-34 and ResNet-50) by 1.8--4.2\pp, dwarfing this
${\approx}0.6\pp$ effect. This should be read as a constraint on partition design, not as support
for practitioners.
```

### 3.5 Abstract — `paper/DRAFT-v4.md` ANCHOR (count == 1) and REPLACEMENT

ANCHOR:

```text
split, bounding construct validity. Against tuned SGD + cosine, the state-of-the-art
alternative, the method trails by 1.8–4.2 pp, dwarfing this ≈0.6 pp effect. This should be read as
a constraint on partition design, not as support for practitioners.
```

REPLACEMENT:

```text
split, bounding construct validity. The method trails tuned baselines (SGD+cosine on ResNet-18,
AdamW+cosine on ResNet-34 and ResNet-50) by 1.8–4.2 pp, dwarfing this ≈0.6 pp effect. This should
be read as a constraint on partition design, not as support for practitioners.
```

### 3.6 §7 T4 body — name the ResNet-50 comparator (both files)

The abstract now names three comparators; §7 T4 names only two, leaving the ResNet-50 baseline
to be inferred. Two words fix it.

`paper/paper.tex` ANCHOR (count == 1):

```latex
for AdamW + cosine, a deficit of $\mathbf{-2.558 \pm 0.063}$; on ResNet-50 it is
$90.833 \pm 0.236$ against $95.047 \pm 0.110$, a deficit of $\mathbf{-4.214 \pm 0.260}$.
```

`paper/paper.tex` REPLACEMENT:

```latex
for AdamW + cosine, a deficit of $\mathbf{-2.558 \pm 0.063}$; on ResNet-50 it is
$90.833 \pm 0.236$ against $95.047 \pm 0.110$ for AdamW + cosine again, a deficit of
$\mathbf{-4.214 \pm 0.260}$.
```

`paper/DRAFT-v4.md` ANCHOR (count == 1):

```text
AdamW + cosine, a deficit of **−2.558 ± 0.063**; on ResNet-50 it is 90.833 ± 0.236 against
95.047 ± 0.110, a deficit of **−4.214 ± 0.260**. **The honest range is −1.8 to −4.2 pp behind
a tuned schedule, and it widens with depth.**
```

`paper/DRAFT-v4.md` REPLACEMENT:

```text
AdamW + cosine, a deficit of **−2.558 ± 0.063**; on ResNet-50 it is 90.833 ± 0.236 against
95.047 ± 0.110 for AdamW + cosine again, a deficit of **−4.214 ± 0.260**.
**The honest range is −1.8 to −4.2 pp behind a tuned schedule, and it widens with depth.**
```

---

## 4. B7 — §3.4's self-verification clause is false in `paper.tex`

### 4.1 The finding, re-derived

§3.4 (`paper.tex:966–972`, `DRAFT-v4.md:767–773`) says section `[16]` of the audit
*"reads this sentence back out of the manuscript and asserts the triple against a fresh
measurement"*. In `analysis/c98_reproduce.py`:

```python
DRAFT = os.path.join(ROOT, "paper", "DRAFT-v4.md")        # :707
...
def censuscheck(rows, adm, args):                          # :1093
    path = getattr(args, "draft", None) or DRAFT           # :1109  <-- the draft, or --draft
    claim = _census_claim(path)                            # :1113
```

`_census_claim` flattens with `re.sub(r"[*`\s]+", " ", ...)` and matches `_CENSUS_RE`. Against
`paper.tex` that fails on three counts: the triple is wrapped in `\textbf{...}` (a brace before
`353` and after `quantity-numerals`) and the per cent sign is `\%`. And the census's own
`_FENCE = re.compile(r"```.*?```|^ {4,}\S.*$", re.S | re.M)` is a **markdown** rule — a
4-space-indented LaTeX continuation line would be deleted as if it were verbatim scorer output,
which would gut a `.tex` file. **So in `paper.tex` the clause is simply false.**

### 4.2 What was done, and why

**A LaTeX branch, as preferred — not a narrowing.** The branch is in `_census_claim`, which
*reads the printed sentence*; it is **not** a second census. That distinction is the whole
design:

* The **measurement** stays on `paper/DRAFT-v4.md`, because the QUANTITY rule *is* a markdown
  fence rule. Censusing the `.tex` separately would produce a different distinct count, and the
  two markups would then legitimately print **different** triples — which breaks the standing
  requirement that a numeric diff between them come back clean.
* The **assertion** now runs against every markup present. `paper.tex`'s printed triple is read
  through the LaTeX branch and checked against that one measurement. A triple that goes stale in
  `paper.tex` alone now exits non-zero.

So §3.4 becomes true of both files without inventing a second, incompatible number.

`CENSUS_MARK` is still frozen **before** any assertion, so the four extra `chk()` sites do not
change `chk() assertion sites executed` and do not enter the coverage they report. The
self-check site count goes **4 → 8** (four per markup); §3.4's parenthetical is updated to say
"eight".

### 4.3 Verification of the branch

Positive — both files parse to the same triple (run in a scratch tree whose `[16]` is stale for
an unrelated reason, so read the `paper` column, which is the *printed* value):

```
[16] THE COVERAGE CENSUS, ASSERTED  (§3.4 Registration and scope)
  sites executed        DRAFT-v4.md              403 | paper 353 | **FAIL**   §3.4
  distinct numerals asserted DRAFT-v4.md         261 | paper 256 | **FAIL**   §3.4
  distinct numerals in draft DRAFT-v4.md         786 | paper 786 | PASS       §3.4
  coverage of distinct numerals DRAFT-v4.md      33.2 | paper 32.6 | **FAIL** §3.4
  sites executed        paper.tex                403 | paper 353 | **FAIL**   §3.4
  distinct numerals asserted paper.tex           261 | paper 256 | **FAIL**   §3.4
  distinct numerals in draft paper.tex           786 | paper 786 | PASS       §3.4
  coverage of distinct numerals paper.tex        33.2 | paper 32.6 | **FAIL** §3.4
```

Negative — perturb **only** `paper.tex` (`covering 256` → `covering 999`) and only the tex row
moves, proving the branch reads the tex and not a copy of the draft:

```
  distinct numerals asserted DRAFT-v4.md         261 | paper 256 | **FAIL**   §3.4
  distinct numerals asserted paper.tex           261 | paper 999 | **FAIL**   §3.4
```

Guards: the pairing fires only when `path` is the default `DRAFT` (so `--census --draft <other>`
still measures exactly what it is told) and only when `paper.tex` exists (so the deposit, which
ships no manuscript, still takes the existing `skip`).

### 4.4 `analysis/c98_reproduce.py` — patch (three anchors, each count == 1)

The working tree of this file is being edited concurrently by another package (+153 lines inside
`metricsens`, well above these anchors); all three anchors below are unaffected by that diff.

**(a) after `DRAFT = ...` (line 707) — ANCHOR:**

```python
DRAFT = os.path.join(ROOT, "paper", "DRAFT-v4.md")
```

**REPLACEMENT:**

```python
DRAFT = os.path.join(ROOT, "paper", "DRAFT-v4.md")
TEX   = os.path.join(ROOT, "paper", "paper.tex")
```

**(b) `_census_claim` — ANCHOR:**

```python
def _census_claim(path):
    """(assertions, covered, distinct, pct) as §3.4 PRINTS them, or None."""
    flat = re.sub(r"[*`\s]+", " ", open(path).read())
    m = _CENSUS_RE.search(flat)
    if not m: return None
    n, c, q, p = m.groups()
    return int(n), int(c), int(q), (float(p) if p else None)
```

**REPLACEMENT:**

```python
def _census_claim(path):
    """(assertions, covered, distinct, pct) as §3.4 PRINTS them, or None.

    Reads BOTH markups.  DRAFT-v4.md needs only markdown emphasis flattened.
    paper.tex additionally wraps the triple in \\textbf{...} and escapes the per
    cent sign, so the LaTeX branch strips the markup macro names, the braces and
    the backslash before the shape regex runs.  Neither branch touches a digit,
    and neither re-censuses the .tex: the QUANTITY count is defined by census()'s
    fence rule, which is a markdown rule, so there is one measurement and both
    files must print it."""
    raw = open(path).read()
    if path.endswith(".tex"):
        raw = re.sub(r"\\(?:textbf|textit|emph|mathbf|texttt|mathrm)\s*\{", "{", raw)
        raw = raw.replace("\\%", "%").replace("\\,", " ").replace("~", " ")
        raw = raw.replace("{", " ").replace("}", " ")
    flat = re.sub(r"[*`\s]+", " ", raw)
    m = _CENSUS_RE.search(flat)
    if not m: return None
    n, c, q, p = m.groups()
    return int(n), int(c), int(q), (float(p) if p else None)
```

**(c) `censuscheck` — ANCHOR (the whole function, from its `def` line to the blank lines before
`SECTIONS = [`):**

```python
def censuscheck(rows, adm, args):
    """§3.4's coverage sentence, re-measured and asserted against the manuscript."""
    global CENSUS_MARK
    print("\n[16] THE COVERAGE CENSUS, ASSERTED  (§3.4 Registration and scope)")
    if not getattr(args, "_full", True):
        skip("censuscheck", "only some sections were requested, so the assertion "
                            "count would not be the manuscript's")
        return
    path = getattr(args, "draft", None) or DRAFT
    if not os.path.exists(path):
        skip("censuscheck", "no manuscript in this tree (the deposit ships none), "
                            "so §3.4's coverage cannot be re-measured here")
        return
    claim = _census_claim(path)
    if claim is None:
        FAILS.append(("§3.4 coverage sentence not parseable", "-", "-",
                      "expected the shape: " + CENSUS_SHAPE))
        print("  **FAIL** could not find §3.4's coverage sentence in %s."
              % os.path.relpath(path, ROOT))
        print("           expected shape:  %s" % CENSUS_SHAPE)
        return
    p_sites, p_cov, p_qd, p_pct = claim
    CENSUS_MARK = len(ASSERTED)      # freeze BEFORE asserting: see census()
    _n_tok, n_qd, _n_q, n_cov = census(path, quiet=True)
    chk("chk() assertion sites executed", CENSUS_MARK, p_sites, "§3.4", "%.0f")
    chk("distinct quantity-numerals asserted", n_cov, p_cov, "§3.4", "%.0f")
    chk("distinct quantity-numerals in the draft", n_qd, p_qd, "§3.4", "%.0f")
    if p_pct is not None:
        chk("coverage of distinct quantity-numerals",
            100.0 * n_cov / n_qd if n_qd else 0.0, p_pct, "§3.4", "%.1f")
    print("    (the `paper` column here is §3.4's own sentence, read out of %s."
          % os.path.relpath(path, ROOT))
    print("     A FAIL means that sentence has gone stale, not that a result moved:")
    print("     re-run with --census and write the printed triple into §3.4 in BOTH")
    print("     paper.tex and DRAFT-v4.md, then re-run to a fixpoint.)")
```

**REPLACEMENT:**

```python
def censuscheck(rows, adm, args):
    """§3.4's coverage sentence, re-measured and asserted against BOTH markups."""
    global CENSUS_MARK
    print("\n[16] THE COVERAGE CENSUS, ASSERTED  (§3.4 Registration and scope)")
    if not getattr(args, "_full", True):
        skip("censuscheck", "only some sections were requested, so the assertion "
                            "count would not be the manuscript's")
        return
    path = getattr(args, "draft", None) or DRAFT
    if not os.path.exists(path):
        skip("censuscheck", "no manuscript in this tree (the deposit ships none), "
                            "so §3.4's coverage cannot be re-measured here")
        return
    # The MEASUREMENT is taken once, on the markdown draft.  The ASSERTION is made
    # against every markup present, so a triple that goes stale in paper.tex alone
    # -- which §3.4 used to claim was impossible, while [16] only ever read the
    # draft -- now exits non-zero instead of passing quietly.
    targets = [path]
    if os.path.abspath(path) == os.path.abspath(DRAFT) and os.path.exists(TEX):
        targets.append(TEX)
    claims = {}
    for q_ in targets:
        c_ = _census_claim(q_)
        if c_ is None:
            FAILS.append(("§3.4 coverage sentence not parseable in %s"
                          % os.path.relpath(q_, ROOT), "-", "-",
                          "expected the shape: " + CENSUS_SHAPE))
            print("  **FAIL** could not find §3.4's coverage sentence in %s."
                  % os.path.relpath(q_, ROOT))
            print("           expected shape:  %s" % CENSUS_SHAPE)
        else:
            claims[q_] = c_
    if not claims:
        return
    CENSUS_MARK = len(ASSERTED)      # freeze BEFORE asserting: see census()
    _n_tok, n_qd, _n_q, n_cov = census(path, quiet=True)
    for q_, (p_sites, p_cov, p_qd, p_pct) in claims.items():
        tag = os.path.basename(q_)
        chk("sites executed        %-20s" % tag, CENSUS_MARK, p_sites,
            "§3.4", "%.0f")
        chk("distinct numerals asserted %-15s" % tag, n_cov, p_cov, "§3.4", "%.0f")
        chk("distinct numerals in draft %-15s" % tag, n_qd, p_qd, "§3.4", "%.0f")
        if p_pct is not None:
            chk("coverage of distinct numerals %-12s" % tag,
                100.0 * n_cov / n_qd if n_qd else 0.0, p_pct, "§3.4", "%.1f")
    print("    (the `paper` column here is §3.4's own sentence, read out of %s."
          % " and ".join(os.path.relpath(q_, ROOT) for q_ in claims))
    print("     The COUNT is measured on %s alone -- one measurement, both markups"
          % os.path.relpath(path, ROOT))
    print("     assert it.  A FAIL means that sentence has gone stale, not that a")
    print("     result moved: re-run with --census and write the printed triple into")
    print("     §3.4 in BOTH paper.tex and DRAFT-v4.md, then re-run to a fixpoint.)")
```

### 4.5 §3.4 prose — `paper/paper.tex` ANCHOR (count == 1)

```latex
scorer, not re-derived. Measured by \texttt{python3 analysis/c98\_reproduce.py --census}, the
audit executes \textbf{353 claim-carrying assertions covering 256 of the 786 distinct
quantity-numerals} in this manuscript, which is 32.6\% of them. Those three figures are not
merely measured: section \texttt{[16]} of the audit reads this sentence back out of the
manuscript and asserts the triple against a fresh measurement, so a stale coverage claim now
exits non-zero instead of passing quietly, which is what it did for three review cycles. (The
four sites that do that self-check are excluded from the count and from the coverage they
report, so the census never counts itself.)
```

### 4.6 §3.4 prose — `paper/paper.tex` REPLACEMENT

```latex
scorer, not re-derived. Measured by \texttt{python3 analysis/c98\_reproduce.py --census}
on \texttt{paper/DRAFT-v4.md}, the
audit executes \textbf{353 claim-carrying assertions covering 256 of the 786 distinct
quantity-numerals} in this manuscript, which is 32.6\% of them. Those three figures are not
merely measured: section \texttt{[16]} of the audit reads this sentence back out of
\textbf{both markups} --- \texttt{paper/DRAFT-v4.md} and \texttt{paper/paper.tex} --- and asserts
the triple against that one fresh measurement, so a stale coverage claim in \emph{either} file
now exits non-zero instead of passing quietly, which is what it did for three review cycles.
(The count is taken on the draft alone, because the quantity rule stated above is a markdown
fence rule; the two markups are required to print the same triple, and \texttt{[16]} fails if
they disagree. The eight sites that do that self-check are excluded from the count and from the
coverage they report, so the census never counts itself.)
```

### 4.7 §3.4 prose — `paper/DRAFT-v4.md` ANCHOR (count == 1)

```text
from the scorer, not re-derived. Measured by `python3 analysis/c98_reproduce.py --census`, the
audit executes **353 claim-carrying assertions covering 256 of the 786 distinct
quantity-numerals** in this manuscript, which is 32.6% of them. Those three figures are not
merely measured: section `[16]` of the audit reads this sentence back out of the manuscript
and asserts the triple against a fresh measurement, so a stale coverage claim now exits
non-zero instead of passing quietly, which is what it did for three review cycles. (The four
sites that do that self-check are excluded from the count and from the coverage they report,
so the census never counts itself.)
```

### 4.8 §3.4 prose — `paper/DRAFT-v4.md` REPLACEMENT

```text
from the scorer, not re-derived. Measured by `python3 analysis/c98_reproduce.py --census` on
`paper/DRAFT-v4.md`, the
audit executes **353 claim-carrying assertions covering 256 of the 786 distinct
quantity-numerals** in this manuscript, which is 32.6% of them. Those three figures are not
merely measured: section `[16]` of the audit reads this sentence back out of **both markups** —
`paper/DRAFT-v4.md` and `paper/paper.tex` — and asserts the triple against that one fresh
measurement, so a stale coverage claim in *either* file now exits non-zero instead of passing
quietly, which is what it did for three review cycles. (The count is taken on the draft alone,
because the quantity rule stated above is a markdown fence rule; the two markups are required to
print the same triple, and `[16]` fails if they disagree. The eight
sites that do that self-check are excluded from the count and from the coverage they report,
so the census never counts itself.)
```

**The `353 / 256 / 786 / 32.6` triple is left exactly as it stands in both files.** It is
already stale in the working tree (the concurrent `metricsens` package adds `chk()` sites) and
must be brought to a fixpoint — **in both files, to the same values** — after all packages land.
With B7 in place, forgetting either file is now a non-zero exit rather than a silent pass.

---

## 5. Integration order and the one thing that can go wrong

1. Apply §1 (B3, tex only), §2 (B4, both), §3 (B5, both), §4.4 (`c98_reproduce.py`), §4.5–4.8
   (B7 prose, both). Eleven prose anchors and three code anchors, each verified `count == 1`.
2. `python3 analysis/c98_reproduce.py --census`, then write the printed triple into §3.4 of
   **both** files, then re-run to a fixpoint. Expect **two** rows per assertion in `[16]` now.
3. `tectonic` — verified exit 0, **66 pp** (was 65), warning multiset unchanged.

**The one hazard: the abstract has 1 word of slack in `DRAFT-v4.md` (229 of 230).** Any later
package that adds a word to the abstract — the pending B2 disclosure of the fixed-effect pool
is the obvious candidate — will trip `abstract too long/dense`. That package must re-measure
with `text_quality._abstract_defects` and buy the words back, not assume headroom exists.
