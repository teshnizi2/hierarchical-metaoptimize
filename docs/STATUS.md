# STATUS — operator dashboard

Updated 2 Sep 2026 (cycle 105). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **130**) > `docs/FINDINGS.md` > everything else.
HEAD = `a2ae73c`. Draft = `paper/paper.tex` + `paper/DRAFT-v4.md` (65 pp, `tectonic` exit 0, 0 TeX errors).

## Verdict — Q1 meta-gate re-run on `paper.tex`

| | |
|---|---|
| Cycle 98 (v2) | **DESK-REJECT**, 6/10, 15 blocking |
| Cycle 100 (v3) | **MAJOR REVISIONS**, 8/10, 18 blocking |
| Cycle 103 (v4) | **MAJOR REVISIONS**, 7/10, 15 blocking |
| **Cycle 105 (candidate)** | **MAJOR REVISIONS**, **7/10**, **7 blocking** |
| Gate static half | **`structural_gaps = []`, `passed = True`** on `track=empirical`. First time ever |
| Substance gate | silent (no experiment envelope; `_n_real_calls = 0` → no-op, by design) |
| Prior 15 items | **15 / 15 genuinely closed**, verified by running the checks, not by reading prose |
| Why 7 → 7, not up | item **count** halved, but the new top item (B1) is more severe than anything on the old list **and it is in the abstract** |
| GPU to clear all 7 | **0 jobs, 0 hours** |
| Science overturned | none. Every finding survived independent attack this cycle |

**Not desk-reject:** the gate's own blocking-gap list is empty; structure is Q1-clean.
**Not desk-accept:** four sentences are verifiably false as printed, and the whole meta-analytic layer is referred to the wrong null distribution — by 14–17 orders of magnitude, in the abstract.

## Gate checks — run, not paraphrased

`/Users/teshnizi/PaperFactory/paperfactory/agents/q1_meta_gate.py`, `_static_checks` + `_apply_static_gate`, `track=empirical`.

| check | rubric | value | verdict |
|---|---|---|---|
| `placeholder_figures` | S1 | `False` | PASS |
| `hardcoded_hex` | S2 | `False` | PASS |
| equations labelled + `\ref`'d | S3 | 12 envs, 0 starred, 12 labels, **0 unreferenced** | PASS |
| `unresolved_refs` / orphan labels | S4 | 74 labels, 74 refs, **0 / 0** | PASS |
| `endmatter_missing` | S5 | `[]` — all 6 found | PASS |
| `unicode_math` | S6 | `False` | PASS |
| `abstract_missing_items` | — | `[]` (was 6 of 7) | PASS |
| `reporting_missing_items` | — | `[]` (`se_empirical`, 17/17) | PASS |
| `text_quality_defects` | — | `[]` — abstract 0, section 0, caption 0 | PASS |
| `hyperref` | S8 | `\usepackage[hidelinks]{hyperref}` | PASS |
| TODO/TBD/XXX/FIXME/placeholder/`??`/DOI stub | S9 | **0 / 0 / 0 / 0 / 0 / 0 / 0** | PASS |
| draft-internal phrasing | S10 | "earlier draft" 0, "camera-ready" 0, "this draft" 0 | PASS |
| compile hygiene | S12 | `tectonic` exit 0, 65 pp, 0 `!`, 3 overfull hbox | PASS |
| `empirical_substance_gaps` | — | `[]` | PASS |

**Track sensitivity — the one live fragility.** `_resolve_track` defaults to `systematic_review` when the track blob is absent. On that track four more checks block: `over_venue_cap` (body **28,874** words vs cap 5,000), `sections_over_budget` (6 sections, Results +806%), `likely_text_heavy`, `sections_without_display_support` (Conclusion 1,007 w, Discrepancy register 1,209 w). `display_items_total = 36`. Irrelevant to TMLR; fatal at a page-limited venue.

## The 7 blocking items — all zero GPU, shortest path first

| # | item | evidence (re-derived this cycle) | cost |
|---|---|---|---|
| **B3** | `paper.tex` A.4 asserts the **superseded 88.4%** in the present tense, two lines before the live **92.8%**. `paper.tex`-only; `DRAFT-v4.md` carries the corrected form alone | tex 4144–4146 vs 4146–4149; `88.4` ×4 in tex, ×3 in md | 5 min |
| **B5** | Abstract attributes the whole **1.8–4.2 pp** deficit to SGD+cosine and calls it *"the state-of-the-art alternative"*. Only 1.807 is vs SGD+cosine; 2.558 and 4.214 are vs **AdamW+cosine**. Superlative appears nowhere in the body | tex:81, md:27; §7 T4 names the three comparators | 10 min |
| **B4** | §8 and **Data Availability** claim each of 2,241 `.out` files *"carries its own `ARGS:` and `ENV:` line"*. Measured: **4 lack `ARGS:`, 128 lack `ENV:`**. §8 contradicts its own universal two sentences later ("2,237 with an `ARGS:` line") | `find ../runs ../runs_alice2 -name '*.out'` → 2241; `grep -L` → 4 / 128 | 10 min |
| **B7** | §3.4's census sentence says the audit *"reads this sentence back out of the manuscript"* — but `c98_reproduce.py` section [16] measures **`DRAFT-v4.md` only**, and its `_FENCE` 4-space rule guts LaTeX. In `paper.tex` that clause is false | `c98_reproduce.py:709,713,731,948`; tex:966–971 | 5 min |
| **B6** | §5.8's stated design-point rule yields **10**, not the 11 it uses. `rl3 @3e-4` and `fa1` are identical on network, dataset, base–meta, η and budget — differing **only** in `beta_clip`, which the same enumeration collapses across for rows 1–6. §4.4 separately argues box is not a moderator, removing the defence | CSV: both ResNet18/CIFAR10/SGDm/Lion/3e-4/1e-3/γ1/aug1/100ep; clip `-30:9.0` vs `-25:-2.3026` | 1–2 h |
| **B1** | **THE SCIENCE ITEM. The meta-analytic layer is referred to the wrong null and the paper never says so.** Weights `w=se⁻²` come from Welch se's at **2.04–9.68 df (median 2.91)**, so `Q` is not χ²ₖ₋₁ | see block below | 3–4 h |
| **B2** | Same family: the abstract's interval **undercovers**, and a **fixed-effect** pool is printed beside I² = 87% | see block below | (with B1) |
| B8 | *(major, not blocking)* §4.4's endpoint knife is never applied to §4.7's prescription `T` — Contribution 6, the paper's only actionable recommendation | — | 1–2 h |

### B1/B2 — independently re-derived, 20,000 draws, using `c98_figures.meta/welch/cells`

Paper's live pool reproduces exactly: pool **0.5297 ± 0.0294**, `Q` **102.47** on 13 df, τ **0.295**, between-base `Q` **95.12** on 3 df, share **92.8%**, SGDm pool **0.5556 ± 0.0448** with `Q` **4.21** on 7 df.

| quantity | paper prints | null under the paper's own estimator | honest value |
|---|---|---|---|
| `Q` = 102.47 / 13 df | `p = 5.5×10⁻¹⁶` | null `Q` mean **26.86**, median 21.38, p95 62.67 | Monte-Carlo **p 0.012** (0.002 common-sd) |
| between-base `Q` = 95.12 / 3 df | `p = 1.7×10⁻²⁰` | null median **5.55** | Monte-Carlo **p 0.005** (0.0003 common-sd) |
| fixed-effect pool `±0.029` | 95% CI | true sd **0.046**; coverage **65.1%** | random-effects / equal-weight pool |
| abstract `+0.556 ± 0.045` | 95% CI | true sd **0.062**; coverage **72.6%** | `±0.062`, or equal-weight |
| "homogeneous (`Q` 4.21 on 7 df)" | reads vs χ²₇ | null median **9.41**, p5 2.68, p95 31.34 | 4.21 is at the **14th percentile of its own null** |
| τ = 0.295, I² = 87% | — | DL subtracts k−1 = 13 where the null mean is ~27 | both are **upper bounds** |

Disclosure vocabulary in `paper.tex`: `bootstrap` **0**, `Monte Carlo` **0**, `calibrat` **0**, `anticonservative` **0**, `simulat` **0**, `random effects` **0**, `HKSJ` **0**.
**Self-inconsistent:** tex:804–806 already concedes 2–4 df and applies Welch–Satterthwaite to every `t`, then hands `Q` built from those same variance estimates to χ² uncorrected.
**The findings survive.** Unweighted permutation over the 14 cells (base labels shuffled) → η² 0.840, p 0.00023. Sign survives all four endpoints (20/20, 20/20, 20/20, 19/20). Zero differential attrition (170/170 admissible), all 20 cells exactly n v n.

## Prior 15 items — closure verified by execution

| | |
|---|---|
| G1 end-matter | `endmatter_missing = []`, 6 of 6 matched by the gate's own regex |
| G2 / G3 / G4 | `abstract_missing_items []`, `reporting_missing_items []`, `text_quality_defects []` |
| F1 / F2 | `c98_reproduce.py` → **exit 0, ALL 357 CHECKS PASS** (incl. `complete 17 \| paper 17`, census 353 / 256 / 786 / 32.6%) |
| S1–S7, R1 | 74 labels / 74 refs / 0 orphans / 0 dangling; §4.4 endpoint table present at tex:1732–1736 |
| M1 | Contribution 3 disclosed as conditional; all four endpoint rows asserted by audit section [15] |

## TODO-FOR-AUTHOR — verified 2 Sep 2026, nothing invented

| # | item | state | evidence |
|---|---|---|---|
| A1 | **Author-list decision on the originator of the §5.9 hierarchical-pooling design** (co-author of the audited parent work; §5.9 is negative about it) — name, affiliation, ORCID, CRediT role | **OPEN** | tex:4337 "who is **not** an author of this paper" |
| A1b | second competing-interests sentence for that person | **CLOSED** | "A second interest, of a different kind." paragraph now present |
| A2 | **Mint the artefact DOI** | **OPEN** | "The deposit has no DOI, because it has not been deposited" (honest, not false) |
| A3 | grant identifier | **CLOSED — none exists** | Funding: "no dedicated project funding and no grant" |
| A4 | **"Funding acquisition" on S. Salehkaleybar's CRediT contradicts a Funding statement that says there was no grant** | **OPEN** | Author Contributions lists it; Funding denies a grant. Live self-contradiction |
| A5 | **Institutional LIACS correspondence address to replace the gmail of record** | **OPEN** | gmail at 2 sites: `\thanks` (tex:56) and Correspondence (tex:4397–4398) |
| A6 | **ORCIDs for both authors** | **OPEN** | `grep -ic orcid paper.tex` → **0** |
| A7 | **Approval to rebuild the deposit from a clean checkout** | **OPEN** | `release/README.md:9` — "The working tree was **DIRTY** at build time"; built from `2a499e4`, HEAD is `a2ae73c`. The commit is the artefact's **only** identifier, so the shipped archive names the wrong tree |

## Submission readiness

**Send to TMLR today: NO.** Four sentences are false as printed and the abstract's headline interval undercovers at 73%. All seven items are arithmetic and editing — **zero GPU, zero new runs**. Estimated one working day for B3+B5+B4+B7+B6, one more for B1/B2+B8.

| venue | fit | P(accept) as-is | P(accept) after the 7 | note |
|---|---|---|---|---|
| **TMLR** | **best** | **0.15** | **0.70** | criterion 2 (audience interest) is easily met; criterion 1 (claims supported) currently fails **in the abstract**. No page limit, so 65 pp is fine |
| JMLR | good | 0.05 | 0.35 | long-form welcome; wants a stronger general claim than "nine mechanisms, none survives" |
| Machine Learning (Springer) | good | 0.08 | 0.45 | empirical-audit shape fits; would demand the calibration repair first |
| NeurIPS D&B / Datasets & Benchmarks | fair | 0.05 | 0.25 | artefact is strong, but the contribution is a measurement, not a resource |
| TMLR *Reproducibility Certification* | fair | — | 0.55 | worth requesting alongside submission |
| Neurocomputing / IEEE Access | poor | 0.03 | 0.10 | 28,874-word body vs a ~5,000-word band; would desk-return on length alone |
| ICML/NeurIPS main track | poor | 0.02 | 0.10 | negative-leaning audit, 8-page limit incompatible |

## Cluster — hz3-R2

| | |
|---|---|
| State | **PENDING**, 0:00 elapsed, `Reason=Priority` — 4855960 `hz3-ch-s5`, 4855961 `hz3-c23-s5`, 4855962 `hz3-n1d-s5` |
| `.out` files | **none exist** |
| RULE 20 check | **OWED** — run it the moment the first `.out` lands: confirm `BETA_CLIP=-30:9.0` and `PROBE=5` on the run's own `ENV:` line, every flag exactly once on `ARGS:`; `scancel` on any mismatch |
| Box verified | **NO** — cannot be, before the runs start |
| Actions taken | **none.** No `sbatch`, no `scancel`, nothing disturbed |
| Corpus | `results/all_runs.csv` = **2,173 rows**, unchanged |

## House rules (unchanged)

- `plateau5` is PRIMARY; the CSV `plateau` column is BANNED as a primary.
- RULE 16 run a registered scorer UNEDITED and quote its verdict; documented args are not edits.
- RULE 20 a batch's science is what the runs' own `ARGS:` line says, never the script header.
- RULE 21 no batch is submitted without a registered scorer.
- Re-derive every number at write time. Never quote prose.
- Do not close an item by softening wording. A false claim is deleted or corrected.
- Never fabricate an affiliation, ORCID, grant number or DOI — it goes on TODO-FOR-AUTHOR.
