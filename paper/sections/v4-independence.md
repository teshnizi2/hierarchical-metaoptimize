# v4 — PACKAGE `independence` (closes A3, A4, A5, A7)

Cycle 100. **Zero GPU. No Slurm job submitted.** No edit to `paper/DRAFT-v3.md`.

Authority for every number below: `results/all_runs.csv` (2,173 rows) and the runs' own
`ARGS:`/`ENV:` lines under `alice-backup/runs/` and `alice-backup/runs_alice2/`
(STANDING RULE 20). Every figure was re-derived at write time; nothing is quoted from prose,
including the briefing that commissioned this package.

**One file was written outside this document**, and it is the file the task named:
`results/all_runs.csv`, patched by `analysis/args_repair.py --apply` (§A3.1). A timestamped
backup was made by the script itself. Nothing else in the tree was touched. `git commit` was
not run.

---

## 0. Summary of what changes

| item | status | the substantive change |
|---|---|---|
| **A3** | **CLOSED** | `dup_group` now marks the 18 collapsed pairs. A reader following the paper's own rule recovers `ml2` se **0.195**, not 0.142. §3.3 and §8 rewritten to describe the column truthfully — including the nine pairs it still does not carry. |
| **A4** | **CLOSED** | §4.1's parent cell is **3 seeds run twice**, not 6 seeds. The parent's blockwise-beats-scalar step there becomes **+0.522 ± 0.293, t 1.78 — UNRESOLVED** (it was t 2.52). The claim is not softened; it is withdrawn at that cell and re-anchored on `ub9`, which is a genuine 3 v 3 and resolves it at t 4.26. |
| **A5** | **CLOSED** | The four "independent submissions" are **not** independent: 13 cell-seeds drawn from **6** distinct seeds, with nine of the runs literally the same experiment. Reworded, and explicitly reconciled with §6.3. |
| **A7** | **CLOSED** | Both `rl3` rungs put in the T table (+0.756, t 6.45 and +0.391, t 3.09). "Ten cells, every one resolved at t ≥ 3.3" becomes **twelve cells, the weakest at t 3.09**. |

Three things found on the way that this package does **not** own are referred, with evidence,
in §5. One of them (§5.1) is a live false number in ten places, the abstract among them.

---

# A3 — the `dup_group` column

## A3.1 What was run, and what it did

```
$ md5 -q results/all_runs.csv
f7f966a461fe5e441ff127d8f3b1c7f2
$ wc -l results/all_runs.csv
    2174 results/all_runs.csv          # 2,173 rows + header

$ python3 analysis/args_repair.py --report      # dry run, unedited
rows: 2173   groups declared: 18   rows in a group: 36
...
--- ARGS-AUDIT.md sec.5, re-derived from plateau5 ---
  D  (chunk777 - nodewise)
     as reported  6 v 6 : +0.456 +- 0.142   t 3.20
     honest  3 seeds x2 : +0.456 +- 0.195   t 2.34
  G  (chunk2325 - nodewise1d)
     as reported  6 v 6 : +0.173 +- 0.071   t 2.44
     honest  3 seeds x2 : +0.173 +- 0.073   t 2.38
  nondeterminism (same config, same seed): mean |d| 0.163  sd 0.183  max 0.472
  between-seed sd: mean 0.179   ratio to nondeterminism 0.98x

$ python3 analysis/args_repair.py --apply
APPLIED: 36 rows updated.
Backup: results/all_runs.csv.pre-argsrepair-20260902-191705.bak
```

`args_repair.py` was run **unedited**; `--apply` is a documented argument, not an edit
(RULE 16).

## A3.2 Verification, done against the backup rather than by assertion

| check | result |
|---|---|
| rows before / after | **2,173 / 2,173** — unchanged |
| columns that differ between backup and new file | **`dup_group` only**, on exactly **36 rows** (all 38 columns compared row-by-row) |
| accuracy / configuration values changed | **0** |
| rows marked `superseded` by this patch | **0** |
| `dup_group` populated, after | **21 groups / 42 rows**, every group of size 2 |
| of which pre-existing | **3** — the `a0-{scal,blk6,layer}-1e4_s0` reruns, one member of each carrying `superseded = 1` |
| of which new | **18** — `ml2` 12, `h2` 4, `c100smoke`/`c100pin` 2 |

**The reader test the task asked for**, run blind off the CSV — group by `dup_group`
(a row with an empty `dup_group` is its own group), average within group, count *n* as the
number of groups:

| `ml2` quantity | rule **applied** | rule **ignored** (6 v 6) | where it appears |
|---|---|---|---|
| D = chunk777 − nodewise | **+0.456 ± 0.195, t 2.34** | +0.456 ± 0.142, t 3.20 | Table 2 row 5 |
| G = chunk2325 − nodewise1d | **+0.173 ± 0.073, t 2.38** | +0.173 ± 0.071, t 2.44 | §5.4 |
| T = nodewise1d − nodewise | **+0.619 ± 0.176, t 3.52** | +0.619 ± 0.133, t 4.66 | §4.7 |

A reader following the stated rule now recovers **se 0.195**, and only a reader ignoring it
recovers 0.142. That is A3's test and it passes.

`analysis/c98_reproduce.py` was run after the patch: `D ml2 (n 3 v 3) +0.456 | paper +0.456 |
PASS`, `T ml2 +0.619 | PASS`, `G under ml2 after the collapse +0.173 | PASS`, and
`ml2 read as 6 v 6 (the WRONG reading) 0.142 | PASS`. Its five FAILs are all corpus counts
(§5.1) and none of them can be touched by a `dup_group` write.

## A3.3 What the column is exhaustive *of* — measured, not assumed

`docs/ARGS-AUDIT.md` §5 found 18 collapsed pairs by grouping runs **within a batch**. Repeating
the same test **across the whole corpus** — signature = the effective `ARGS` line after
last-wins resolution with `--save-directory` and `--run-name` dropped, plus the `ENV` line with
`PROBE_DIR` dropped, plus `--seed` — gives a much larger set:

| census over all 2,173 rows joined to their own `.out` | groups | runs |
|---|---|---|
| collapse groups, all runs | 167 | 413 |
| …restricted to groups where **every member logged an `ENV:` line** | **154** | **364** |
| …and every member admissible | 134 | 321 |
| …**within a single batch** (the case that can inflate a reported *n*) | **18** | **36** |

The restriction to ENV-logged runs matters and is not cosmetic: 109 runs in the corpus predate
the `ENV:` line, so for those the arm axis (`HIER`, `LAM`, `ETA_RATIO`) was never logged and
the signature cannot see it. Six apparent within-batch collapses — two in `ha`, two in `hs`,
one in `det`, one in `hv` — are exactly those, and they are **not** duplicates; they are runs
whose distinguishing axis is unlogged. Restricted to runs that do log an `ENV:` line, the
within-batch collapse set is **exactly the 18 pairs now marked, and all 18 are marked**.

The remaining 136 groups are cross-batch. They cannot inflate the *n* of a within-batch
primary — that is what "within batch" buys — but they are the mechanism behind A5, and one of
them is A4.

Reproduce:

```sh
python3 analysis/args_repair.py --report        # the 18, and ml2's arithmetic
python3 analysis/argsline_guard.py 'runs/**/*.out'   # the flag test (recursive; see §6.4)
```

## A3.4 EXACT REPLACEMENT — §3.3, the paragraph beginning `**Duplicate runs.**`

> Replaces the final paragraph of **§3.3 Metric, admissibility, multiplicity, and units of
> replication** (DRAFT-v3 lines 540–545), in full.

```markdown
**Duplicate runs.** Two differently-named runs are *duplicates*, not replicates, when they
resolve to the same experiment: the same effective argument line after `argparse`'s last-wins
resolution, the same `ENV` line, and the same `--seed`. The rule such runs carry is: **any n,
se or t computed over rows sharing a `dup_group` first drops rows marked `superseded`, then
averages within the group, and counts n as the number of distinct groups.** The run table's
`dup_group` column carries twenty-one groups — the eighteen collapsed pairs (twelve in `ml2`,
four in `h2`, two in the CIFAR-100 smoke tests) and the three `a0` reruns already on record,
where one member of each carries `superseded = 1`. Twelve of the eighteen are `ml2`'s, which is
why `ml2` is a 3 v 3 cell with se 0.195 and not a 6 v 6 cell with se 0.142 (§6.1).

Two facts about that column a reader should have before relying on it. **Within a batch it is
exhaustive, and we checked rather than assumed:** applying the signature above to every run
that logs an `ENV:` line returns exactly those eighteen pairs and no others. (One hundred and
nine runs predate the `ENV:` line; for those the hierarchical arm axis was never logged, and
six apparent collapses in `ha`, `hs`, `det` and `hv` are that blind spot rather than
duplicates.) **Across batches the same signature finds far more:** 154 groups covering 364
runs are the same experiment at the same seed in two or more submissions. None of those
inflates the n of a within-batch primary, which is one of the things "within batch" buys — but
they are why §4.4 no longer calls its four repeated cells independent, and one of them is
§4.1's parent cell, where nine `pp_`/`PP_` pairs are two submissions of one nine-run design at
the same three seeds. **The column does not yet carry those nine.** §4.1 applies the rule to
them by hand and reports that cell at n = 3; a reader who reads the cell off the run table
alone will recover n = 6. That is the one bookkeeping gap this paper ships open, we name it
rather than let the column imply a completeness it does not have, and
`analysis/args_repair.py` is the one-line place it would be closed.
```

## A3.5 EXACT REPLACEMENT — §8, **Data.**

> Replaces one clause in the **Data.** paragraph of **§8 Reproducibility** (DRAFT-v3 line 1880).
> The surrounding sentence is otherwise untouched. **Note:** the same paragraph's "2,113 rows"
> is stale and is *not* fixed here — see §5.1.

BEFORE (line 1880):

```
`complete`), and a `dup_group` column marking the eighteen pairs of differently-named runs
that resolve to the same experiment (§3.3).
```

AFTER:

```markdown
`complete`), and a `dup_group` column carrying twenty-one groups — the eighteen pairs of
differently-named runs that resolve to the same experiment plus the three `a0` reruns, where
one member of each carries `superseded = 1` (§3.3). The column is exhaustive within a batch
for every run that logs an `ENV:` line; it does not carry the nine cross-submission pairs of
§4.1's parent cell, which §4.1 handles in text.
```

## A3.6 EXACT REPLACEMENT — §8, numbered point (ii)

> Replaces point **(ii)** of the "Three things this table is meant to stop a reader from having
> to guess" list in **§8** (DRAFT-v3 lines 2007–2012).

```markdown
(ii) **`ml2`'s three seeds were each run twice** under two names; the run table's `dup_group`
column records the eighteen such within-batch pairs, and any n, se or t computed over rows
sharing a `dup_group` drops `superseded` rows, averages within the group, and counts n as the
number of distinct groups. That is what makes `ml2` a 3 v 3 cell with se 0.195, not a 6 v 6
cell with se 0.142 (§6.1). The reproduction audit enforces the rule, so a reader cannot
accidentally recover the wrong number for `ml2`. The column is **not** a census of every
same-seed re-measurement in the corpus: across batches there are 154 such groups over 364
runs, none of which enters the n of a within-batch primary, and nine of which — §4.1's
`pp_`/`PP_` pairs — sit inside one reported cell and are handled in §4.1's own text.
```

---

# A4 — §4.1's parent cell is three seeds, not six

## A4.1 The defect, verified from the `ARGS` lines

The cell is 18 runs: `pp_{scal,blk6,layer}_s{0,1,2}` (job ids 4683697–4683705) and
`PP_{scal,blk6,layer}_s{0,1,2}` (job ids 4700548–4700556), 16,851 job ids apart. For all nine
same-named-arm, same-seed pairs the effective argument line — with only `--save-directory` and
`--run-name` dropped — is **identical**, and so is the `ENV` line:

```
$ # for each of the nine pairs: ARGS identical (paths dropped), ENV identical, same --seed
pp_scal_s0     ARGS identical: True   ENV identical: True   seed=0
pp_scal_s1     ARGS identical: True   ENV identical: True   seed=1
pp_scal_s2     ARGS identical: True   ENV identical: True   seed=2
pp_blk6_s0     ARGS identical: True   ENV identical: True   seed=0
pp_blk6_s1     ARGS identical: True   ENV identical: True   seed=1
pp_blk6_s2     ARGS identical: True   ENV identical: True   seed=2
pp_layer_s0    ARGS identical: True   ENV identical: True   seed=0
pp_layer_s1    ARGS identical: True   ENV identical: True   seed=1
pp_layer_s2    ARGS identical: True   ENV identical: True   seed=2
```

Sample, `pp_scal_s0` versus `PP_scal_s0` — the whole difference:

```
--save-directory .../runs/pp   --run-name pp_scal_s0
--save-directory .../runs/PP   --run-name PP_scal_s0
```

Both carry `--seed 0`, `--alpha0 1e-6`, `--meta-stepsize 1e-3`, `--alg-base AdamW`,
`--alg-meta Adam`, `--num-epochs 100`, and `ENV: AUGMENT=0 BETA_CLIP=-15:-2.3026 HIER=none`.
`docs/ARGS-AUDIT.md` §5 did not find this pair because its collapse test grouped runs *within
a batch*, and `pp` and `PP` are two batches.

**So the cell is three seeds run twice, not six seeds** — the same shape as `ml2`, across two
submissions instead of inside one.

## A4.2 Re-derivation, `plateau5`, every number shown

Arm means (Welch se from the arm variance):

| arm | as drafted, n = 6 | dup-collapsed, n = 3 |
|---|---|---|
| scalar | 73.830 ± 0.103 | **73.830 ± 0.138** |
| six blocks | 74.352 ± 0.180 | **74.352 ± 0.259** |
| layerwise | 73.449 ± 0.119 | **73.449 ± 0.102** |

**Point estimates are identical** — averaging within a pair and then across three groups is the
same arithmetic as averaging six numbers when the groups are balanced. Only the standard errors
move.

| contrast | as drafted, n = 6 | dup-collapsed, n = 3 |
|---|---|---|
| step 1, six blocks − scalar | +0.522 ± 0.208, t 2.52 (Welch p 0.036 on 7.97 df) | **+0.522 ± 0.293, t 1.78** (Welch **p 0.17** on 3.05 df; normal-approx p 0.075) |
| step 2, layerwise − six blocks | −0.903 ± 0.216, t 4.18 (Welch p 0.0026 on 8.67 df) | **−0.903 ± 0.278, t 3.25** (Welch **p 0.058** on 2.61 df; normal-approx p 0.0012) |

Working, for step 1 at n = 3. The three group means are
scalar {73.784, 73.618, 74.088}, six blocks {74.265, 73.954, 74.838}.
Means 73.830 and 74.352, difference **+0.5223**.
Sample variances 0.056812 and 0.201085, so
se = √(0.056812/3 + 0.201085/3) = √0.085968 = **0.2932**, and t = 0.5223/0.2932 = **1.78**.
Welch–Satterthwaite df = (0.018937 + 0.067028)² / (0.018937²/2 + 0.067028²/2) = **3.05**.

Two incidental corrections while re-deriving: the draft's "± 0.207" for step 1 at n = 6 is
0.2076 → **0.208**, and its "± 0.215" for step 2 is 0.2160 → **0.216**. Both numbers are
replaced below, so neither survives into v4.

**Per-seed, the step is small and unstable**: after collapsing, six blocks − scalar reads
+0.481, +0.336, +0.750 across seeds 0, 1, 2. Neither submission resolves it on its own —
`pp` alone gives +0.477 ± 0.294 (t 1.62), `PP` alone +0.567 ± 0.358 (t 1.59). Pooling them as
six independent seeds is the only way the cell ever reached t > 2.

**What the pairs do buy.** Nine same-config, same-seed pairs across two submissions:
mean |Δ `plateau5`| **0.306 pp**, max **0.510 pp**; the arm-level offsets PP − pp are −0.037
(scalar), +0.053 (six blocks), +0.098 (layerwise) pp. One `PP` run (`PP_scal_s0`) ran on an
A100 where the rest ran on L4; §6.3's measured A100 − L4 offset is −0.021 pp (n = 21), so it
does not carry this.

## A4.3 What the registered scorer says, run unedited

RULE 16. `analysis/c88_scorers.py` was run with its documented argument and its output is
quoted, not paraphrased:

```
$ python3 analysis/c88_scorers.py --score ub9
{'arms': {'orig': {'scalar': [73.908, 73.66, 73.794, 73.442, 74.084, 74.092],
                   'resnet18_blocks': [74.512, 74.018, 74.106, 73.802, 74.822, 74.854],
                   'layerwise': [73.096, 73.4, 73.264, 73.774, 73.33, 73.83]},
          'wide':  {'scalar': [72.068, 71.806, 73.392],
                    'resnet18_blocks': [75.322, 74.508, 74.56],
                    'layerwise': [74.104, 73.85, 74.018]}},
 'rule': {'step1_wide': 2.375, 'step2_wide': -0.806, 'step1_orig': 0.522,
          'verdict': "REPRODUCTION STANDS. The parent's blockwise>scalar step survives a box
                      in which clipping is measured rather than assumed, AND the next rung
                      still reverses it. The non-monotonicity at the parent's own config is
                      real."}}
```

**The scorer's verdict is untouched by this correction, and that is a fact about the
registration rather than a convenience.** `_ub9_rule` tests `step1_wide > 0.30` and
`step2_wide < −0.30` — thresholds on **arm means only**, fixed before the runs existed. The
duplicate collapse changes no mean. The verdict therefore stands exactly as issued.

But the scorer's `orig` arm pools all six runs per granularity, three of which are reruns of
the other three, so its `step1_orig = 0.522` is a point estimate over a set that is not six
independent draws. The scorer never attaches an interval to it and never claims one; the paper
did.

`ub9` itself is a clean 3 v 3 — 9 runs, 3 arms × seeds 0–2, one submission, one box
(−60:6.0), no duplicate pair anywhere in it (checked against the corpus-wide collapse census):
scalar 72.422 ± 0.491, six blocks 74.797 ± 0.263, layerwise 73.991 ± 0.075;
step 1 **+2.375 ± 0.557, t 4.26** (Welch p 0.023 on 3.06 df),
step 2 **−0.806 ± 0.273, t 2.95** (Welch p 0.083 on 2.32 df; normal-approx p 0.0032).

## A4.4 EXACT REPLACEMENT — §4.1, the paragraph beginning `**The parent's own cell, checked for a clipping artefact.**`

> Replaces that paragraph in **§4.1** (DRAFT-v3 lines 688–698) in full. The η table and the α₀
> table above it are **not** touched by this package (see §5.2 for a defect in the latter that
> is referred, not fixed).

```markdown
**The parent's own cell, checked for a clipping artefact — and it is three seeds, not six.**
Eighteen unaugmented AdamW/Adam runs at η = 1e-3, α₀ = 1e-6 in the parent's own clip box are
the only runs in the corpus that touch the parent's actual experiment. They read scalar
73.830, six blocks 74.352, layerwise 73.449, so the parent's blockwise-beats-scalar step
reproduces at **+0.522** and the *next* rung reverses it at **−0.903**. The eighteen are not
eighteen independent runs. They are two submissions of one nine-run design — `pp_*`
(job ids 4683697–4683705) and `PP_*` (4700548–4700556) — and for all nine same-arm pairs the
effective argument line, the `ENV` line and the `--seed` are identical. Under this paper's own
duplicate rule (§3.3) the cell is **3 v 3**, and the two steps become

> **six blocks − scalar = +0.522 ± 0.293, t 1.78 — UNRESOLVED** (Welch p 0.17 on 3.05 df;
> normal-approximation p 0.075), where reading the eighteen as six seeds gave ± 0.208 and
> t 2.52; and **layerwise − six blocks = −0.903 ± 0.278, t 3.25**, which the Welch statistic
> §3.3 makes primary at 3 v 3 also leaves unresolved (p 0.058 on 2.61 df) though the
> normal approximation does not (p 0.0012).

**We state that plainly: at the parent's own configuration and in the parent's own clip box,
this corpus does not resolve the parent's blockwise-beats-scalar step.** Per seed the step
reads +0.481, +0.336, +0.750, and neither submission resolves it alone (`pp` +0.477 ± 0.294,
`PP` +0.567 ± 0.358). That is a finding about how thin the parent's own cell is, not a defect
in the replication, and it is the reason the reproduction question had to be bought with fresh
runs rather than settled on the eighteen.

It also had to be bought for a second reason. β₀ = ln(1e-6) = −13.8155 sits 1.1845 nats above
a −15 floor while the travel budget is 50 nats, so this cell is arithmetically capable of
binding on both guards, and `runs/PP` holds no `probe.jsonl` — occupancy is unmeasured in both
directions. We re-ran the cell (`ub9`, 9 jobs, three arms × seeds 0–2, one submission) in a
wide box with clip counting on. The registered scorer's verdict, verbatim: *"REPRODUCTION
STANDS. The parent's blockwise>scalar step survives a box in which clipping is measured rather
than assumed, AND the next rung still reverses it."* That scorer's rule is a threshold on arm
means fixed before the runs existed, so the duplicate correction above cannot move it. In the
wide box, and at a genuine 3 v 3 with no duplicate pair in it, the step is **+2.375 ± 0.557
(t 4.26)** and the reversal at the next rung is **−0.806 ± 0.273 (t 2.95)**.

**So the reproduction claim rests on `ub9` and not on the eighteen.** In the parent's own box
the step is +0.522 and unresolved; in a box where clipping is measured it is +2.375 and
resolved, and the non-monotonicity survives both. The eighteen are still worth their place —
nine same-config, same-seed pairs across two submissions give mean |Δ `plateau5`| 0.306 pp and
max 0.510 pp, one of the two direct re-measurement bounds in this corpus (§6.1 gives the
other) — but they are not six seeds and this paper no longer reports them as six.
```

---

# A5 — the four "independent submissions"

## A5.1 The defect, verified

The four cells are Table 2 rows 1–4: `cc1`, `mm1`, `pp1` and the BatchNorm arm of `gn1`. Their
D values re-derive exactly as drafted:

| cell | seeds | D (pp) | se | t |
|---|---|---|---|---|
| `cc1` | **3, 4, 5** | +0.7267 | 0.2001 | 3.63 |
| `mm1` | **0, 1, 2** | +0.4853 | 0.1613 | 3.01 |
| `pp1` | **0, 1, 2** | +0.5807 | 0.1414 | 4.11 |
| `gn1` (BN) | **0, 1, 2, 3** | +0.5870 | 0.1532 | 3.83 |

Inverse-variance pool +0.582 ± 0.080, **Q = 0.883 on 3 df, p = 0.829** — the draft's
"Q = 0.89 on 3 df, p = 0.83", confirmed.

**Thirteen cell-seeds are drawn from six distinct seeds.** Seeds 0, 1 and 2 are each used by
three of the four cells; seed 3 by two; seeds 4 and 5 by one each. And the overlap is not
nominal — it is the same experiment at the run level. From the corpus-wide collapse census
(§A3.3), identical effective `ARGS`, identical `ENV`, identical `--seed`:

* `gn1-bn-ch-s{0,1,2}` ≡ `mm1-ch-s{0,1,2}` ≡ `pp1-ch-s{0,1,2}`
* `gn1-bn-node-s{0,1,2}` ≡ `mm1-node-s{0,1,2}` ≡ `pp1-node-s{0,1,2}` ≡ `bn1-node-s{0,1,2}` ≡ `tw0-node-s{0,1,2}`
* `cc1-ch-s3` ≡ `gn1-bn-ch-s3`, and `cc1-node-s3` ≡ `gn1-bn-node-s3`

So `mm1` and `pp1` are two re-measurements of one six-run experiment, `gn1`'s BN arm is a third
over the same three seeds plus a fourth, and `cc1` shares its first seed with `gn1`. **The
largest mutually seed-disjoint subset of the four is two cells.**

## A5.2 What the numbers become

Restricted to the seeds all three share (0, 1, 2) — three measurements of one six-run
experiment:

| cell, seeds 0–2 only | D | se |
|---|---|---|
| `mm1` | +0.485 | 0.161 |
| `pp1` | +0.581 | 0.141 |
| `gn1` (BN) | +0.408 | 0.107 |

Q = 0.958 on 2 df, p = 0.62; spread max − min = **0.173 pp**, sd 0.086.

The two genuinely seed-disjoint comparisons available:

| comparison | Q | df | p |
|---|---|---|---|
| `cc1` (3,4,5) vs `mm1` (0,1,2) | 0.882 | 1 | 0.35 |
| `cc1` (3,4,5) vs `pp1` (0,1,2) | 0.355 | 1 | 0.55 |

At run level, the re-measurement spread of a single configuration at a fixed seed:

| arm, seed | values | range |
|---|---|---|
| chunk777 s0 (×3) | 92.558 / 92.572 / 92.572 | 0.014 |
| chunk777 s1 (×3) | 92.574 / 92.766 / 92.702 | 0.192 |
| chunk777 s2 (×3) | 92.450 / 92.250 / 92.504 | 0.254 |
| nodewise s0 (×5) | 92.228 / 92.312 / 92.160 / 92.114 / 92.026 | 0.286 |
| nodewise s1 (×5) | 92.204 / 92.064 / 91.992 / 91.756 / 91.876 | 0.448 |
| nodewise s2 (×5) | 92.120 / 91.982 / 91.980 / 92.166 / 91.980 | 0.186 |

## A5.3 The reconciliation with §6.3

§6.3 withdraws the batch variance component: within-config, across-batch,
**F(39, 172) = 0.71**, random-effects **sd_batch = 0.000 pp**, observed batch-mean spread
median 0.100 / mean 0.126 / max 0.319 pp. That withdrawal is precisely what removes the
difference between "replicate" and "rerun" *for cells that share their seeds*. If a second
submission at the same seeds carried a resolvable batch offset, the four cells' agreement would
be evidence that the offset is small. With the offset not resolvable, their agreement is a
statement about run-to-run nondeterminism and nothing else. It is still worth having — a corpus
in which D moved between reruns would be a different corpus — but it is not seed-level
replication, and the paper was reading it as though it were.

The consistency runs the other way too, and is worth stating: §6.3's own "largest single
replication series in the corpus", the seven `nodewise` batch means at η = 1e-4
(91.890 / 91.961 / 92.000 / 92.012 / 92.044 / 92.064 / 92.184, 0.294 pp), is the same
measurement seen from the other side. Those seven batches are `cc1`, `tw0`, `gn1`, `pp1`,
`mm1`, `ml2` and `bn1` — **four of them are §4.4's four cells, and their `nodewise` arms are
literally the same runs** (§A5.1). Because the batches share their seeds, the 0.294 pp has the
seed effect divided out of it by construction: it is a bound on batch offset plus
nondeterminism and not a seed bound. §6.3's bound and §4.4's agreement are one thing described
twice, and after this rewrite the paper says so.

## A5.4 EXACT REPLACEMENT — §4.4, the paragraph beginning `Four of those eight are independent submissions`

> Replaces that paragraph in **§4.4** (DRAFT-v3 lines 847–851) in full — from "Four of those
> eight" through "cluster account Q = 0.76/1 (p 0.38)."

```markdown
Four of those eight are submissions of the *identical* configuration — `cc1`, `mm1`, `pp1` and
the BatchNorm arm of `gn1` — and they land at +0.727, +0.485, +0.581 and +0.587, Q = 0.88 on
3 df, p = 0.83. **They are not four independent replications and we no longer describe them as
such.** Between them the four draw thirteen cell-seeds from **six** distinct seeds: `mm1`,
`pp1` and `gn1` all use seeds 0–2, `gn1` adds seed 3, and `cc1` uses 3–5. The overlap is exact
rather than nominal — `gn1-bn-ch-s0`, `mm1-ch-s0` and `pp1-ch-s0` are the same experiment, the
same effective argument line after last-wins resolution with the same `ENV` and the same
`--seed`, as are their `nodewise` partners (which `bn1` and `tw0` also re-run), and
`cc1-*-s3` is the same experiment as `gn1-bn-*-s3`. The largest mutually seed-disjoint subset
of the four is **two** cells: `cc1` against either `mm1` or `pp1`, which agree at Q = 0.88 and
Q = 0.36, each on 1 df. Restricted to the three seeds they share, `mm1`, `pp1` and `gn1` read
+0.485, +0.581 and +0.408 — a 0.173 pp spread over three measurements of one six-run
experiment.

**What their agreement measures is therefore re-measurement of a fixed seed set across
batches, not replication across seeds**, and §6.3 is where its worth is settled: with the batch
variance component withdrawn (sd_batch = 0.000 pp, F(39, 172) = 0.71), a second submission at
the same seeds is a rerun, not a replicate. Q = 0.88 on 3 df says that D does not move between
reruns, which is worth knowing and is not nothing; it does not say that D survives a change of
seed. The one comparison in this pool that does say that is `cc1` against `mm1` or `pp1`, and
it agrees. The within-SGDm residual inherits the same caveat and we flag it rather than let
the reader find it: four of the eight cells re-measure one seed set, which can only lower Q,
so **Q = 4.21 on 7 df is an upper bound on homogeneity's evidence, not a neutral test.**
Leave-one-cell-out over the eight never resolves heterogeneity (Q 1.21–4.17 on 6 df, pool
+0.544 to +0.603; τ = 0.000 in all eight subsets), and no other axis available inside the
subset competes with the base: β-box Q = 0.76/2 (p 0.68), meta-stepsize Q = 0.68/1 (p 0.41),
budget Q = 2.99/1 (p 0.084), cluster account Q = 0.76/1 (p 0.38).
```

## A5.5 EXACT INSERTION — §6.3, after the withdrawal block

> Insert as a new paragraph in **§6.3**, immediately after the indented block quote that ends
> "…which no variance model would have caught." (DRAFT-v3 line 1682) and before the paragraph
> beginning "Hardware was excluded by direct measurement".

```markdown
**One consequence of the withdrawal, spelled out because §4.4 used to depend on the opposite.**
If batch carried a resolvable variance component, then a second submission of a configuration
would be a *replicate* even at the same seeds, and the agreement of several such submissions
would be evidence about that component. With the component withdrawn, a submission at the same
seeds is a **rerun**: its agreement with the first bounds run-to-run nondeterminism and nothing
else. That is exactly the situation of §4.4's four repeated cells, three of which share seeds
0–2 and one of which shares seed 3 with a fourth, and §4.4 now says so. It is also the reason
the seven-batch `nodewise` series quoted above is a *tight* bound rather than a loose one: those
batches share their seeds, so the 0.294 pp spread has the seed effect divided out of it by
construction, and it is the same set of runs §4.4's Q = 0.88 is computed on. The two readings
are one measurement, and neither of them is a seed-level replication.
```

---

# A7 — the T table omits both `rl3` cells

## A7.1 Re-derivation of every row, `plateau5`, Welch se

T = `nodewise1d` − `nodewise`, within batch. All eleven existing rows reproduce to the printed
digit; the two `rl3` rows are new.

| batch | T (pp) | se | t | Welch df |
|---|---|---|---|---|
| `bn1` | +0.427 | 0.041 | 10.43 | 3.71 |
| **`rl3` @ η 3e-4** | **+0.391** | **0.127** | **3.09** | 3.94 |
| **`rl3` @ η 1e-4** | **+0.756** | **0.117** | **6.45** | 2.04 |
| `ml2` (dup-collapsed) | +0.619 | 0.176 | 3.52 | 2.40 |
| `fa1` | +0.649 | 0.110 | 5.88 | 7.45 |
| `g3m` | +0.758 | 0.093 | 8.13 | 13.70 |
| `cc1` | +0.816 | 0.159 | 5.13 | 3.11 |
| `r50` | +1.049 | 0.317 | 3.31 | 3.92 |
| `gm2` | +1.363 | 0.151 | 9.00 | 2.65 |
| `hz3` 6 v 6 | +0.337 | 0.069 | 4.85 | 5.88 |
| `hz3` 5 v 5 | +0.328 | 0.084 | 3.89 | 4.72 |
| `nl1` SGD | +0.692 | 0.135 | 5.12 | 2.65 |
| `nl1` RMSProp | +0.916 | 0.242 | 3.79 | 2.05 |
| `aw1` | +0.091 | 0.078 | 1.16 | 3.85 |

`rl3` @ 1e-4: `nodewise1d` {92.670, 92.642, 92.680}, `nodewise` {92.056, 91.678, 91.990};
means 92.6640 and 91.9080; T = **+0.7560**, se = √(0.000397/3 + 0.041049/3) = **0.1174**,
t = **6.45**. This is the same +0.756 the draft already quotes four lines below the table in
the Eq. 6 decomposition (+0.756 = 0.692 + 0.064) — the value was in the section but not in the
table it belongs to.

`rl3` @ 3e-4: `nodewise1d` {93.010, 92.950, 92.734}, `nodewise` {92.692, 92.450, 92.378};
means 92.8980 and 92.5067; T = **+0.3913**, se = √(0.021444/3 + 0.027497/3) = **0.1277**,
t = **3.09** (Welch p 0.037 on 3.94 df; normal-approximation p 0.0020).

**The sentence has to change.** With `rl3` in, the non-AdamW cells number **twelve**, not ten,
and the weakest is `rl3` at η = 3e-4 with **t 3.09**, not t ≥ 3.3. The range "+0.328 to
+1.363" is unaffected: `rl3`'s +0.391 sits above `hz3`'s +0.328/+0.337 floor and below `gm2`'s
ceiling.

Two independence caveats the enlarged table needs, both measured:

* **`rl3`'s two rungs share a batch** — the same convention Table 2 already flags for its rows
  6 and 7.
* **`bn1` and `ml2` are the same experiment at the same seeds, up to a flag Lion does not
  read.** All twelve `bn1`/`ml2` run pairs differ only by `--normalizer-param-meta 0.999`,
  which `ml2` carries as a last-wins residual and whose runtime message is
  `args_meta includes unnecessary attributes {'normalizer_param'}`; `ENV` and `--seed` match.
  Their T's, +0.427 ± 0.041 and +0.619 ± 0.176, differ by 0.192 ± 0.181 (z 1.06).

## A7.2 EXACT REPLACEMENT — §4.7, table and the paragraph beneath it

> Replaces the T table in **§4.7**, its `‡` footnote, and the paragraph beginning "The move
> costs nothing" (DRAFT-v3 lines 1061–1081: the table, the `‡` footnote, and the paragraph).
> The opening sentence of §4.7 and the Eq. 6
> decomposition paragraph that follows are unchanged.

```markdown
| batch | network / setting | n | T (pp) | se | t |
|---|---|---|---|---|---|
| hz3‡ | R18 / C10 / SGDm, **300 ep** | 6 v 6 | +0.337 | 0.069 | 4.85 |
| rl3§ | R18 / C10 / SGDm, η 3e-4, box −30:9.0 | 3 v 3 | +0.391 | 0.127 | 3.09 |
| bn1¶ | R18 / C10 / SGDm | 3 v 3 | +0.427 | 0.041 | 10.43 |
| ml2¶ | R18 / C10 / SGDm | 3 v 3 (×2 reruns) | +0.619 | 0.176 | 3.52 |
| fa1 | R18 / C10 / SGDm, η 3e-4 | 6 v 6 | +0.649 | 0.110 | 5.88 |
| nl1 | R18 / C10 / **SGD** | 3 v 3 | +0.692 | 0.135 | 5.12 |
| rl3§ | R18 / C10 / SGDm, η 1e-4, box −30:9.0 | 3 v 3 | +0.756 | 0.117 | 6.45 |
| g3m | **R34** / C10 / SGDm | 9 v 9 | +0.758 | 0.093 | 8.13 |
| cc1 | R18 / C10 / SGDm | 3 v 3 | +0.816 | 0.159 | 5.13 |
| nl1 | R18 / C10 / **RMSProp** | 3 v 3 | +0.916 | 0.242 | 3.79 |
| r50 | **R50** / C10 / SGDm | 3 v 3 | +1.049 | 0.317 | 3.31 |
| gm2 | R18 / **C100** / SGDm | 3 v 3 | +1.363 | 0.151 | 9.00 |
| aw1 | R18 / C10 / **AdamW** | 3 v 3 | **+0.091** | 0.078 | 1.16 |

‡ `hz3` matched at 5 v 5 (seed-5 trio excluded for the clip-box and hardware mismatch of §7 T9):
**+0.328 ± 0.084, t 3.89**.
§ The two `rl3` rungs share one batch and one clip box, as Table 2 rows 6 and 7 already note;
they are two operating points, not two submissions.
¶ `bn1` and `ml2` are the same experiment at the same seeds up to one flag Lion does not read:
all twelve of their run pairs differ only by `ml2`'s last-wins residual
`--normalizer-param-meta 0.999`, whose runtime message is `args_meta includes unnecessary
attributes {'normalizer_param'}`. Their T's differ by 0.192 ± 0.181 (z 1.06). Treat them as one
measurement made twice, not two.

The move costs nothing — it *reduces* the number of learned quantities from 14,420 to 4,851 —
and under an SGDm, SGD or RMSProp base it is worth **+0.328 to +1.363 pp** across **twelve**
within-batch cells, **every one of which is resolved, the weakest at t 3.09** (`rl3` at
η = 3e-4; Welch p 0.037 on 3.94 df) and the strongest at t 10.4. Twelve cells is not twelve
independent measurements, and the footnotes say why: `bn1` and `ml2` are one experiment measured
twice, so the count of distinct experiments behind the range is **eleven**, and two further
pairs — `rl3`'s two rungs and `nl1`'s two bases — share a batch with each other rather than
sitting in separate submissions. **Under AdamW the
move is worth nothing measurable (+0.091 ± 0.078, t 1.16).** That is the scope line, and §5.4
explains why it is where it is.
```

---

# 5. Found on the way, referred rather than fixed

These are outside this package's four items. Each is stated with the evidence needed to act on
it; none was edited.

## 5.1 `2,113` is now false everywhere it appears — and it is load-bearing in §3.3 and §8

The ingest at commit `6a374f4` took the run table from 2,113 to 2,173 rows. The draft still
says 2,113 at ten places: line 28 (abstract, with "≈1,582 GPU-hours; 1,671" alongside), 453 and
459 (§3.3: "17 of 2,113 runs pass `window_ok` while having completed under 95%" and "Of 2,113
rows, **1,671** are admissible"), 786 (§4.3, "of the 2,113 runs"), 1875 and 1904 (§8, the
**Data.** paragraph and the attrition ledger's first row, which also carries 1,582.2 and 2,098),
2212–2213 (Appendix A.8, "**2,113 rows, 1,671 admissible, 1,582 GPU-hours** summed over the
2,098"), 2279 (Data-availability statement) and 2344 (the CRediT line).
`analysis/c98_reproduce.py` fails on exactly these,
and the failures are **not** caused by this package's `dup_group` write (a `dup_group` value
cannot move a row count, an admissibility flag or a wallclock):

```
rows in results/all_runs.csv    2173 | paper 2113 | **FAIL**   abstract, §8
admissible rows                 1724 | paper 1671 | **FAIL**   §3.3, A.8
runs carrying a wallclock       2150 | paper 2098 | **FAIL**   §8
GPU-hours                       1625 | paper 1582 | **FAIL**   abstract, §8
rows failing window_ok           425 | paper  425 | PASS       §3.3 attrition
rows failing complete             24 | paper   17 | **FAIL**   §3.3 attrition
```

The derived values an integrator needs: **2,173** rows, **1,724** admissible, **2,150** with a
wallclock, **1,625** GPU-hours, **425** failing `window_ok`, **24** failing `complete`. Note
that the §3.3 sentence "17 of 2,113 runs pass `window_ok` while having completed under 95%"
must become **24 of 2,173**, and the seven added ones need the same one-line characterisation
the seventeen got, or the sentence should stop enumerating.

A second knock-on of the same ingest, in **§6.3**: the "largest single replication series"
there is quoted as seven batches over 25 runs. With `rp1` ingested it is **eight** batches over
**31** runs — `rp1`'s `nodewise` arm reads 92.066, which sits inside the quoted range, so the
0.294 pp spread is unchanged and only the counts move. (Under §3.3's duplicate rule the 25 is
also 22 distinct experiments, `ml2` contributing three groups rather than six runs.)

## 5.2 §4.1's α₀ table pools a batch this project ruled unreadable, and a hierarchical arm

I could not fix this without inventing a filter, so I did not touch the table. What is
established:

The cells reproduce as pools of whole batches at AdamW/Adam, η = 1e-3, `AUGMENT=1`,
ResNet-18/CIFAR-10: α₀ = 1e-6 scalar = `a0` (n 3, 91.630), six blocks = `a0` + `i3b`
(n 6, 91.681), layerwise = `a0` (n 3, 91.781); α₀ = 1e-3 scalar = `I1` + `a0` (n 6, 92.631),
six blocks = `I1` + `a0` + `i3b` (n 9, 92.237), layerwise = `I1` + `a0` + `dc`
(n 16, 91.382). All six match the printed values exactly.

Two problems with the α₀ = 1e-3 row:

1. **`I1` supplies 3 of the 16 layerwise runs, 3 of the 9 six-block runs and 3 of the 6 scalar
   runs.** `docs/CORRECTIONS.md` §29 and `docs/CLOSEOUT.md` establish that `I1` ran with an
   unidentified schedule active (`HF.py.bak_sched` timestamped 33 s before submission) and rule
   that it "is not readable as evidence"; §6.3 of this very draft cites that incident. `I1`'s
   layerwise arm reads **92.691** against `a0`'s 90.818 and `dc-awscal`'s 90.909 — a 1.873 pp
   gap, six times §6.3's own 0.319 pp cross-batch maximum. Dropping `I1` moves the layerwise
   cell from 91.382 to **91.080** (n 13); dropping `I1` and the `HIER=additive` half moves it
   to **90.875** (n 8).
2. **The `dc` contribution is half hierarchical.** `dc-aw-a1e3-s{0..4}` carry
   `ENV: HIER=additive ETA_RATIO=0.06`; only `dc-awscal-a1e3-s{0..4}` are the plain layerwise
   arm. The two halves read 91.409 and 90.909.

Also, for each of seeds 0, 1 and 2 the three runs `I1_layer_s`, `a0-layer-1e3_s` and
`dc-awscal-a1e3-s` have **identical** effective argument lines and identical seeds; the only
`ENV` difference anywhere among the nine is that `a0`'s line predates the inert
`COS_TOTAL=default COS_WARMUP=default` keys. Those nine runs are therefore three experiments,
so the n = 16 cell contains at most **10** distinct experiments (3 groups + 2 `dc-awscal`
singletons at seeds 3–4 + the 5 `HIER=additive` runs, which are a different arm again).

The table is labelled descriptive and the in-batch statement §4.1 rests on is the η pair, so no
headline moves. But "at the parent's own configuration" is doing work that this composition
does not support, and someone should either rebuild the cell without `I1` and without the
`HIER=additive` arm or say what it contains.

## 5.3 The `dup_group` column can still be applied wrongly to the three `a0` groups

The rule as §3.3 states it — "average within the group" — applied blind to the three
pre-existing `a0` groups would average a superseded run with the run that supersedes it.
`analysis/aggregate.py` already prints the correct guidance (`filter superseded==0 before any
per-run analysis`), and the replacement text in §A3.4 and §A3.6 above states the two-step rule
explicitly. If any other section restates the rule in the one-step form, it should be brought
into line.

---

# 6. Reproduction

```sh
cd hierarchical-metaoptimize

# A3 — the patch, and the reader test
python3 analysis/args_repair.py --report          # dry run + ml2 arithmetic
python3 analysis/args_repair.py --apply           # 36 rows, dup_group only, .bak first
python3 analysis/c98_reproduce.py                 # ml2 3 v 3 rows PASS

# A4 — the registered scorer, unedited
python3 analysis/c88_scorers.py --score ub9

# A4 / A5 / A7 — every contrast above is nodewise/nodewise1d/chunk777/chunk2325
# plateau5 arm means out of results/all_runs.csv with the Welch se of Eq. 8,
# restricted to window_ok = 1 AND complete = 1 AND a readable plateau5.
```

The duplicate census of §A3.3 is a corpus-wide re-run of `docs/ARGS-AUDIT.md` §5's collapse
test with the grouping key widened from within-batch to global and with `--run-name` dropped
from the signature; it joins all 2,173 CSV rows to their own `.out` by `job_id` and reads the
`ARGS:` and `ENV:` lines only.
