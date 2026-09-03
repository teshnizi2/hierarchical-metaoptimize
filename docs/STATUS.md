# STATUS — operator dashboard

Updated 3 Sep 2026 (cycle 110, **post-reversal gate**). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **134**) > `docs/FINDINGS.md` > everything else.
Manuscript at `a65e7e1`; HEAD = this dashboard commit. Draft = `paper/paper.tex` + `paper/DRAFT-v4.md` (**74 pp**, `tectonic` exit 0, 0 TeX errors, 0 undefined refs). Corpus = **2,177 rows**.
**No Slurm job was submitted this cycle. Cluster untouched — every number below re-derived locally.**

## Verdict

| | |
|---|---|
| Cycle 98 (v2) | **DESK-REJECT**, 6/10, 15 blocking |
| Cycle 100 (v3) | **MAJOR REVISIONS**, 8/10, 18 blocking |
| Cycle 103 (v4) | **MAJOR REVISIONS**, 7/10, 15 blocking |
| Cycle 105 (v5) | **MAJOR REVISIONS**, 7/10, 7 blocking |
| Cycle 107 (v6) | **MAJOR REVISIONS**, 8/10, 2 blocking |
| **Cycle 110 (v7)** | **DESK-ACCEPT**, **9/10**, **0 blocking** |
| Gate static half | `structural_gaps = []`, `passed = True` on `track=empirical` — third cycle running |
| N1 / N2 | closed at `2fe91dd`, re-verified here |
| N3 (stale R2) | **closed at `a65e7e1`** — `grep -c hz3q` = 31 tex / 29 md; every surviving "queued" is past-tense narration of the cancellation |
| Audit | `c98_reproduce.py` **exit 0, ALL 592 CHECKS PASS**, census at fixpoint 584 / 389 / 872 / 44.6% |
| Science overturned | **none.** Contribution 1 verified intact; the withdrawal is confined to the slope |
| GPU to reach submission | **0 jobs, 0 hours.** Six author items, all administrative or editorial |

**Ready to submit: NO.** Not for any manuscript defect — for six items only the authors can close (below).

## Gate checks — executed, not paraphrased

`/Users/teshnizi/PaperFactory/paperfactory/agents/q1_meta_gate.py`, `_static_checks` + `_apply_static_gate`, run under `.venv` at `track=empirical`.

| check | rubric | value | verdict |
|---|---|---|---|
| `placeholder_figures` | S1 | `False`; 4 figures, 4 `\includegraphics` | PASS |
| `hardcoded_hex` | S2 | `False` — 0 `{HTML}{……}` in any figure body | PASS |
| equations labelled + `\ref`'d | S3 | 12 display envs, 12 labels, **0 unreferenced** | PASS |
| dangling refs / orphans / dupes | S4 | 74 labels, **0 / 0 / 0** (orphan half run separately — the shipped check omits it) | PASS |
| `endmatter_missing` | S5 | `[]` — all 6 + AI-assistance disclosure | PASS |
| `unicode_math` | S6 | `False`. One U+2026 at `paper.tex:3305`, inside a quoted scorer block; not a math glyph | PASS |
| `hyperref` | S8 | `\usepackage[hidelinks]{hyperref}` | PASS |
| TODO / TBD / `[TO BE ASSIGNED]` / `??` | S9 | **0 / 0 / 0 / 0**. DOI absence is *stated*, not stubbed | PASS |
| draft-internal phrasing | S10 | 0 — the 5 `DRAFT` / 2 `v4` hits are the filename `paper/DRAFT-v4.md` | PASS |
| absolute novelty claims | S11 | 0. All 24 "the first" are ordinal; all 3 "for the first time" scope a *proposed future* design | PASS |
| compile hygiene | S12 | exit 0, **74 pp**, 0 `!`, 0 undefined, 2 overfull hbox (7.28 / 12.25 pt) | PASS |
| `abstract_missing_items` | — | `[]`; 227 words | PASS |
| `reporting_missing_items` | — | `[]` (profile auto-inferred `se_empirical`) | PASS |
| `text_quality_defects` | — | `[]` | PASS |
| `empirical_substance_gaps` | — | `[]` — sub-gate no-ops (no PaperFactory experiment envelope). Its three conditions are met independently: significance signal everywhere, attrition disclosed (425/17/25 + 64 crashed), no sub-MIE-as-positive | PASS |

**Review-article family (`over_venue_cap`, `sections_over_budget`, `likely_text_heavy`) fires and is gated off** by `_REVIEW_ARTICLE_ONLY_CHECKS` / FLW16 — correct for an empirical paper. Body **33,684 words**. Not a gate failure; see R9.

## The reversal — re-run, and attacked

`c99_hz3q_score.py` run **UNEDITED**. `sha256 50d95083c8…`; its `PARENT_SHA256` pin `0be1f5201d…` matches the committed `c87_hz3_score.py` byte for byte. `--selftest` **59/59 PASS**.

| gate | result |
|---|---|
| H0 provenance | **PASS** — all four arms `node883` / `NVIDIA L4` / `-30:9.0` / seed 5 / 300 ep, read off each run's own header. Same gate **REFUSES the archive** on both counts |
| H1 box | **NOT MEASURABLE HERE** — the four `runs/hz3/probe_*_hz3q_s5/` are empty in the backup; scorer refuses rather than passing silently. Open item (i) |
| H2 primary | published `-0.149` se `0.105` t `-1.42` → FLAT · s5-dropped `-0.207` se `0.107` t `-1.94` → FLAT · **repaired `-0.238` se `0.093` t `-2.57` df 5 → `NOT FLAT — D DECLINES WITH BUDGET`** |
| H3 secondary | published D(300) `+0.428` se `0.086` t `4.94`, G `-0.057` · **repaired `+0.394` se `0.093` t `4.25`, G `-0.048`, D−G `+0.442`** |
| HC cross-class | `92.908` (L4) vs `92.774` (2080 Ti), δ **`+0.134` pp** vs bar 1.00 → `GPU CLASS NOT FIRST-ORDER ON THE LEVEL` |
| non-overwrite | `c87_hz3_score.py` re-run unedited → `grep -c hz3q` = **0**; verdicts unchanged (`SURVIVES`; `MECHANISM SURVIVES THE HORIZON`) |

**Independent hand re-derivation, no scorer**, from the per-seed `plateau5` table:
`-0.1487/0.1047/-1.419` · `-0.2068/0.1067/-1.938` · `-0.2383/0.0927/-2.572`. Exact match to all three.

**New verification this cycle — the hardest available attack, and it fails.** Read the GPU model and `BETA_CLIP` off **every** archived `hz3` `.out` header directly:

| seed | box | class | matched? |
|---|---|---|---|
| 0, 1, 2 | `-30:9.0` ×4 | L4 ×4 | yes |
| 3, 4 | `-30:9.0` ×4 | 2080 Ti ×4 | yes |
| **5 (archived)** | `-30:9.0` ×1, `-15:-2.3026` ×3 | 2080 Ti ×1, A100 ×3 | **no — both axes** |

→ Seed 5 was the **only** contaminated seed. The repaired pool is box- and class-matched **within every seed**. The one-seed repair scope is correct, measured rather than declared.

### Which way does the draft err? — **mildly toward under-reporting, in exactly one place**

| site | handling |
|---|---|
| §4.8 title | "…survives 3× the budget, **and it declines with it**" — states both halves |
| §4.8 body | level *before* withdrawal; three readings tabled; explicit "read the withdrawal for exactly what it is" paragraph |
| §3.5 R2 row + result para | "flatness **WITHDRAWN**"; all three readings |
| Fig 3 caption, A.2, T9, §9, AI-disclosure | withdrawal named at each; A.2 and Fig 3 correctly scope "does not resolve" to the archive |
| **Abstract** | **silent** — no budget, no 300-epoch reading, no withdrawal, while its threats paragraph lists four *other* qualifiers |

- **7 mention sites in 74 pp — proportionate. Not over-dramatised.** Not in the title, not in the abstract, not repeated per section.
- **Contribution 1 intact and verified.** 20/20 count-matched cells untouched; §9 states the two findings separately — *"two findings, of which the second does not weaken the first"*.
- **"Declines" cannot be read as "disappears"** at the two guard sites (`paper.tex:1283` "does not vanish"; `:2741` "has read it backwards").

## Red team — 10 findings, 0 blocking

| # | finding | severity |
|---|---|---|
| R1 | **Abstract carries no trace of the reversal**, while listing four other threats. The paper's strongest integrity evidence is absent from the one paragraph an AE reads first | med |
| R2 | §4.8's budget table has **no caption and an undefined `se` column**; it prints 0.109/0.115/0.071 where the prose 2 lines below prints ±0.086/±0.096/±0.093. Table = sem of six per-seed D, prose = Welch 6v6. Both audited, neither labelled | med |
| R3 | **No rebuttal to linear extrapolation.** A referee computes `0.394 ÷ (0.238/200) ≈ 331` → zero-crossing ≈ **631 epochs**. The paper's only guard is assertion ("read it backwards") | med |
| R4 | The registered bar `\|t\| ≥ 2.0` at df 5 is a two-sided **α ≈ 0.102** test, not 0.05 — undisclosed. This *helps*: a permissive bar means the withdrawal was not bar-shopped, and repaired `p = 0.0500` sits at the conventional line anyway | low |
| R5 | The reversal's mechanics are unstated. **Dropping the bad seed does not produce it** (t −1.94, still FLAT); the *replacement* does, by being more negative than the 5-seed mean **and** restoring n = 6 (se 0.107 → 0.093). Saying so turns "one seed flipped your headline" into the answer | med |
| R6 | T9's "…§4.8 is to be read with them attached" is scoped to the archive by context but reads as scoping **all three** readings — including the repaired one, which by construction carries neither exception. Understates the repair | low |
| R7 | `figures/f3_budget` panel (b) still drawn on the archive — `c98_figures.py:469` regex `hz3-(ch\|node)-s(\d+)$` does not match `hz3q-*`. **Disclosed in the caption**, so nothing false prints | low |
| R8 | Deposit `make reproduce` does **not** depend on `make logs`; run cold it skips the `[7] BUDGET` block — the one that reproduces the reversal. Fails *soft* (announces the skip). After `make logs`: **ALL 584 CHECKS PASS**, exit 0 | low |
| R9 | **74 pp / 33,684 body words.** No TMLR cap, but this is the far tail — reviewer-burden desk-return is the single biggest venue risk | med |
| R10 | tex↔md numeric diff **not clean: 8 residuals**, all pre-existing (3 tex-only, 5 md-only). Seven are caption / quote-wrapping asymmetries; **one is a real md prose gap** — `F(39,172)` appears at `paper.tex:1845` and `:4658` but only at `DRAFT-v4.md:3739` | low |

## TODO-FOR-AUTHOR — 6 open, each re-verified this cycle

| # | item | evidence it is still open | effort |
|---|---|---|---|
| 1 | **CRediT ↔ Funding contradiction.** "Funding acquisition" on S. Salehkaleybar against a Funding statement reading "**no dedicated project funding and no grant**" | both strings present verbatim in the end matter | 1 min |
| 2 | **LIACS correspondence address** to replace the gmail of record, **2 sites** | `paper.tex:56` `\thanks{}` and the `\paragraph{Correspondence.}` in the end matter | 2 min |
| 3 | **ORCIDs, both authors** | `grep -ci orcid` = **0 / 0** in tex and md | 5 min |
| 4 | **Deposit rebuild at the submission commit** | `release/README.md` pins `a65e7e1`; any further commit (this one included) makes it stale | 2 min |
| 5 | **Mint the artefact DOI** | Data Availability: "The deposit has no DOI, because it has not been deposited". Honest, not a stub — S9 clean either way | 5 min + upload |
| 6 | **Authorship for the §5.9 design originator** | Competing Interests still names them as "a researcher … who is not an author of this paper" and calls the origination "a substantial intellectual contribution rather than an acknowledgeable courtesy" | **decision, not edit** |

Items 1–5 are mechanical. **Item 6 is an ethics decision only the authors can make, and it should be settled before submission, not after.**

## Venue

| venue | fit | accept prob. (est.) | note |
|---|---|---|---|
| **TMLR** | **best** | **0.78** | No novelty bar, no length cap; rubric is "claims supported" + "of interest" — both strongly met. Pre-registered self-reversal is exactly what it rewards. Was 0.72 |
| ReScience / MLRC | good | 0.60 | Strong reproduction framing; wants a tighter one-paper scope |
| NeurIPS D&B | fair | 0.30 | Corpus + deposit is a real artefact, but the paper is not framed as one |
| JMLR | fair | 0.25 | Length fine; wants methodological novelty, this is an audit |
| NeurIPS / ICML / ICLR main | poor | 0.15 | 9-page limit is fatal; negative-result audit with no new method |

**Send to TMLR: YES**, after items 1–4 and a decision on 6. Path: fix 1–4 (~10 min) → settle 6 → rebuild deposit at the submission commit → arXiv → TMLR. R1/R2/R3/R5 are ~30 min of editing that measurably raise the reversal's defensibility; do them in the same pass. Item 5 (DOI) can follow acceptance — the deposit is commit-pinned and self-verifying.

## Standing

- `plateau5` PRIMARY; CSV `plateau` column BANNED as primary.
- RULE 16 run-unedited · RULE 20 ARGS-line · RULE 21 scorer-before-batch · RULE 22 `dup_group` guard.
- **Ingest is `aggregate.py` THEN `args_repair.py --apply`** — `aggregate.py` alone silently reverts the A3 duplicate-pair repair.
- Re-derive every number at write time. Never quote prose, including this dashboard.

## Open, carried from CORRECTIONS 134

1. Sync `probe_{node,ch,n1d,c23}_hz3q_s5/probe.jsonl` from ALICE → H1 is not re-derivable from the backup or the deposit (re-confirmed: scorer prints `NO OCCUPANCY IS MEASURABLE`).
2. Redraw `f3_budget` panel (b) — needs `c98_figures.py:469`.
3. The 8 tex↔md numeric residuals (R10).
4. Two `DRAFT-v4.md` prose lines beginning with `|` will render as table rows.
5. Staging dirs `c99pkg/`, `c99pkg2/` left on ALICE — currently the only path by which H1 reproduces.
