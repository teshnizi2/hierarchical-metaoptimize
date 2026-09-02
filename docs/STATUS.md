# STATUS — operator dashboard

Updated 2 Sep 2026 (cycle 103). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **129**) > `docs/FINDINGS.md` > everything else.
HEAD = `d1a714b`. Draft = `paper/DRAFT-v4.md` + `paper/paper.tex` (61 pp, `tectonic` exit 0).

## Verdict — Q1 meta-gate re-run on v4

| | |
|---|---|
| Cycle 98 (v2) | **DESK-REJECT**, 6/10, 15 blocking |
| Cycle 100 (v3) | **MAJOR REVISIONS**, 8/10, 18 blocking |
| **Cycle 103 (v4)** | **MAJOR REVISIONS**, **7/10**, **15 blocking** |
| `paper.tex` branch | **no longer fails outright.** C1 closed: the file exists, compiles, 61 pp, 0 unresolved refs, 0 `??`, 0 `!` lines, 0 undefined citations |
| Static gate result | `passed=False`, **4 gap families** on `track=empirical`; **7** if the track resolves to the default `systematic_review` |
| Substance gate | **silent on all three conditions** — significance evidence everywhere, attrition fully disclosed, no sub-MIE effect sold as positive |
| Why the score fell 8 → 7 | not a regression in the work. One **new** first-order vulnerability was measured for the first time (M1), and four mechanical checks were never re-run after `rp1` landed |
| GPU to clear all 15 | **0 jobs, 0 hours** |
| Science overturned | **one contribution demoted to conditional** (Contribution 3). Contributions 1 and 2 survive intact |

**Not desk-reject:** every v3 item verified genuinely closed; compile clean; no placeholders; substance gate silent.
**Not desk-accept:** the gate returns `passed=False` deterministically, and **two printed numbers are false**.

## The 15 blocking items

### G — gate-deterministic (mechanical, zero science)

| # | item | evidence |
|---|---|---|
| G1 | **All six required end-matter sections report MISSING.** Content is all present, but under one `\section*{End matter}` + `\paragraph{}`. The gate matches `\section*?{<exact title>}`, case-sensitive | `endmatter_missing = ['Competing Interests','Funding','Data Availability','Code Availability','Ethics','Author Contributions']` |
| G2 | **Abstract missing 6 of 7 `se_empirical` reporting items** — objective/research question, study type, artifact/tool/harness, sampling frame + unit of analysis, baseline/SOTA comparison, threats/construct validity | `assess_reporting_completeness`, profile auto-resolved to `se_empirical` |
| G3 | **Methods reporting gap**: "Workload or usage profile specified in replicable detail" — needs `workload`/`task suite`/`scenario` anywhere in the source | `reporting_missing_items` |
| G4 | **3 blocking text-quality defects**: abstract **255 words** (band 120–230); sentence 6 overloaded (**67 words** > 62); Threats section never separates evidence limits from process limits | `_abstract_defects`, `_section_defects` |

**G2 × G4 is the design constraint:** six keyword families must go IN while ≥25 words come OUT.

### F — printed numbers that are false at HEAD

| # | item | prose | data |
|---|---|---|---|
| F1 | §3.3 attrition | "**24** of 2,173 runs pass `window_ok` while under 95%… 23 under 90%… None of the 24" (`tex:641`, `md:485`) | **17** (16 under 90%; one at 94/100). `c98_reproduce.py:81` hardcodes `("complete",17)` and **PASSES** — audit and prose disagree |
| F2 | §3.4 census | "283 assertions covering 216 of the **725** distinct quantity-numerals… **29.8%**" (`tex:915`, `md:721`) | script prints **747** and **28.9%**. The fixpoint broke when `rp1` landed; `--census` measures, never asserts, so exit 0 |

### S — internal contradictions (S3/S4/S10 class)

| # | item | where |
|---|---|---|
| S1 | §3.5 heading "two scored, **two** still in flight" vs its own next paragraph "**three** … have since completed and been scored" | `tex:920`, `md:726` |
| S2 | "There is no third" — `rp1` **is** a third count-matched contrast reported outside Table 2 | `tex:1355`, `md:1029` |
| S3 | §4.3 "we quote no `D` for it **here or anywhere else**" vs §4.4 quoting `gn1`-GroupNorm `D = +0.202 ± 0.137` and the 5-level pool built on it | `tex:1336` vs `tex` §4.4 |
| S4 | **Five stale "sixteen"** against a twenty-row Table 2. §5.8's LOO-RMSE table is computed on the superseded 16-cell set | `tex:1349, 1860, 1965, 2799, 3469` |
| S5 | **Withdrawn statistic still load-bearing**: `F(62,85)=5.47` motivates §4.4's rival label and caveats §5.4, while §6.3 withdraws it and A.3 says it does not reproduce | `tex:1479, 2546` |
| S6 | **15 defined labels never cross-referenced** — incl. `fig:decomposition` (1 of 4 figures), **6 of 11 tables** (`tab:DG, tab:T, tab:arms, tab:holm, tab:inflight, tab:mechanisms`), 2 equations (`eq:A, eq:U`) | direct S3/S4 hit |
| S7 | Abstract attributes all 2,173 runs to ResNet-18/34/50. CSV: **110 ResNet10 + 9 ResNet10_c100 + 1 ResNet101 = 120 rows outside the list** | `tex:69` |

### R — deposit README repeats the exact A8 over-claim

| # | item | where |
|---|---|---|
| R1 | "Everything behind every number in the paper, and a script that re-derives them and checks them" + "Reproducing **every** number in the paper needs `python3` and `matplotlib` only" — refuted by §8's own register (6 of 10 scorer verdicts need the excluded 42 GB) and by the 28.9% census | `analysis/c98_release.py:256, 320`. Line 343 was fixed last cycle; these two were not, and are the more prominent |

### M — the one science item

| # | item |
|---|---|
| M1 | **Contribution 3 is conditional on a post-hoc endpoint.** §3.3 item 6 concedes `plateau5` "was not fixed before the first analysis". Re-derived today from the CSV with the paper's own `arm()`/`welch()`/`dup_group` logic, varying **only** the column |

| column | 14-cell pool | Q / 13 df | p | τ | base share | cells > 0 |
|---|---|---|---|---|---|---|
| `plateau5` | +0.5297 ± 0.0294 | 102.4739 | 5.5e-16 | 0.295 | **92.8%** | 20/20 |
| `plateau` | +0.4493 ± 0.0238 | 29.3677 | 0.0058 | 0.102 | 62.5% | 20/20 |
| **`best_test`** | +0.3956 ± 0.0251 | **9.8729** | **0.704** | **0.000** | **37.5%** | 20/20 |
| `final_test` | +0.6144 ± 0.0426 | 39.9113 | 1.4e-4 | 0.251 | 86.8% | 19/20 |

* On `best_test` there is **no between-cell heterogeneity to decompose** (τ = 0), and the base levels collapse from a 5.3× spread to +0.261 / +0.386 / +0.411 / +0.432.
* The level **rank order inverts**: `plateau5` SGD 1.000 > RMSProp 0.720 > SGDm 0.556 > AdamW 0.189; `final_test` RMSProp 1.518 > SGDm 0.588 > AdamW 0.420 > SGD 0.139.
* **Contribution 1 survives all four** (20/20, 20/20, 20/20, 19/20). Say so explicitly.
* `paper.tex` mentions `best_test`/`final_test` **zero times**. §7 T10 is row-filter sensitivity, not metric sensitivity.

## Venue table

| venue | fit | P(accept) as-is | P(accept) after G+F+S+R+M | note |
|---|---|---|---|---|
| **TMLR** | **best** | **0.15** | **0.60** | No novelty bar; criterion 1 is *claims supported by evidence* — F1/F2/M1 attack exactly that, and are exactly what the fix list closes |
| ReScience C / repro track | strong | 0.30 | 0.70 | Audit-of-a-published-method is native; length is not a problem |
| "I Can't Believe It's Not Better" (NeurIPS/ICML workshop) | strong | 0.55 | 0.85 | Nine mechanisms, none survives — a natural fit, but a workshop, not a journal |
| JMLR | weak | 0.04 | 0.18 | Wants a method, not a measurement |
| ICLR | weak | 0.08 | 0.25 | Novelty bar; negative framing |
| NeurIPS main | weak | 0.05 | 0.18 | Same, plus 9-page pressure on a 61-pp manuscript |
| AISTATS | weak | 0.06 | 0.20 | Wants theory |
| MLSys / NeurIPS D&B | poor | — | — | Not a system, not a dataset |

**Recommendation: do not submit yet.** TMLR is the right venue and the paper is ~1 zero-GPU cycle from being submittable. Sending it now spends the desk read on F1/F2 (two false printed numbers) and hands a methods referee M1 as a four-line script.

## Running / blocked

| | |
|---|---|
| `rp1` | **DONE** — 24/24, ingested, scored, landed at `d1a714b`. Nothing owed |
| `hz3`-R2 (4848866/7/8) | **STILL PENDING, NEVER STARTED** — `0:00`, `START_TIME N/A`, no `.out`. Reason (Priority) |
| RULE 20 on `hz3`-R2 | **STILL OWED.** Discharge the moment a `.out` appears; `scancel` on any `BETA_CLIP` ≠ `-30:9.0` |
| §4.8 budget verdict | **UNCHANGED.** `c87_hz3_score.py` not re-run; the paper says so |
| Slurm | **submit nothing.** All 15 blocking items are zero-GPU |

## User must supply personally — nothing here can be invented

| # | item | blocks submission? |
|---|---|---|
| 1 | **Author-list decision** on the originator of the §5.9 hierarchical partial-pooling design (a co-author of the audited parent work; §5.9 is negative about his design). If he joins: affiliation + ORCID + a second COI sentence | **YES** |
| 6 | **Mint the DOI** — needs an archive account and publishes a permanent public record. Then write the same string into `release/README.md`, `CITATION.cff`, Data availability | **YES** |
| 2 | Grant / funder identifier, if any (paper currently states none, truthfully) | no |
| 3 | `Funding acquisition` CRediT role vs "no grant" — resolve or scope to the compute allocation | no |
| 4 | Institutional correspondence address (currently the gmail of record) | no |
| 5 | ORCIDs for both authors | no |
| 7 | Rebuild deposit from a clean checkout (current build stamped `DIRTY`, correctly) | no |

## Next action

**One zero-GPU cycle, in this order.** G1 first (six `\section*{}` promotions, ~10 min, clears the single largest gap family), then F1/F2 (two false numbers, re-derive don't hedge), then M1 (add the metric-sensitivity table above to §4.4 + a `chk()` site, and restate Contribution 3 as conditional in the paper's own withdrawal idiom), then S1–S7 and R1, then G2/G4 together as one abstract rewrite. Re-run `c98_reproduce.py`, `_abstract_defects`, and this gate before claiming any of it closed.

---

## Corpus of record (`d1a714b`)

| | |
|---|---|
| rows in `results/all_runs.csv` | **2,173** |
| admissible | **1,731** |
| `window_ok=1, complete=0` | **17** (16 under 90%; one at 94/100) — F1 |
| `dup_group` | **42 rows / 21 groups** (18 registered pairs + 3 `a0` reruns) |
| count-matched cells | **20** (Table 2); same-contrast pool **14** |
| GPU-h | **1,632** |
| network census | ResNet18 1667, ResNet18_c100 188, ResNet34 141, **ResNet10 110**, ResNet50 31, ResNet18_gn 17, **ResNet10_c100 9**, ResNet34_c100 9, **ResNet101 1** |

## House rules (unchanged)

* `plateau5` is PRIMARY; the CSV `plateau` column is BANNED as primary. **M1 does not change this** — it requires the choice to be *disclosed as post-hoc and shown to be load-bearing*, not reversed.
* RULE 16 — run a registered scorer UNEDITED, quote its verdict. Documented args are not edits.
* RULE 20 — a batch's science is what the runs' own `ARGS` line says, never the script header.
* RULE 21 — no batch is submitted without a registered scorer.
* BATCH is the unit of replication; primaries must be within-batch.
* **Re-derive every number at write time. Never quote prose, including this file.**
* A null is a valid deliverable. A false claim is deleted or corrected, **never hedged**.
