"""`analysis/corpus_exclusions.py --check` on SYNTHETIC logs and TSV rows (CORRECTIONS 239).

WHY.  `--check` verified each listed row's witness against the run's `VOTE_W` lines only.  `cvt4` (CORRECTIONS 237)
holds a tensor's step size through `BETA_HOLD`; its held runs print `VOTE_W: off` plus a `BETA_HOLD: on ...` line,
and at landing they are listed with that `BETA_HOLD` line as their witness -- which the VOTE_W-only check FAILS.  It
also could not see an ON run that was simply missing from the list (e.g. a whole batch nobody appended).

STRATEGY.  Each case builds a throwaway repo layout in a temp dir -- `analysis/corpus_exclusions.py` (a byte copy of
the REAL module), `results/CORPUS-EXCLUSIONS.tsv` (the real header, synthetic rows), `results/all_runs.csv`
(synthetic keys) and `runs/<batch>/<run>-<job_id>.out` (synthetic witness lines) -- and runs the REAL CLI in a
subprocess.  The module resolves its TSV and CSV from its own location, so nothing is patched or mocked.

  C1  a BETA_HOLD-witnessed row passes (listed held run + unlisted plain run printing `BETA_HOLD: off`).
  C2  a mismatched BETA_HOLD witness fails, and the failure names the run's own BETA_HOLD line.
  C3  a VOTE_W row still passes exactly as before (same summary line, byte for byte); a VOTE_W mismatch still fails
      with the old message.
  C4  an ON run that is a corpus row but absent from the TSV fails: (a) a BETA_HOLD batch with no listed row at all,
      (b) one held run left out of an otherwise listed BETA_HOLD batch, (c) a VOTE_W run of an unlisted batch.
  C5  `off` runs are not required: runs printing `VOTE_W: off` / `BETA_HOLD: off` (or no witness line) stay unlisted.
  C6  an ON run that is not yet a corpus row (running, not ingested) is not required -- listing it would itself fail
      the "present exactly once in the CSV" check.
  C7  a listed run that prints an ON line of a kind other than its listed witness's kind fails.
  C8  a witness that names no registered intervention kind fails.
  C9  without --runs no log is read: no witness or completeness line, exit 0 (the existing behaviour).

ADDED AT CORRECTIONS 245 -- `cvt7`'s GROUP_HOLD (243) and `cvt6`'s COMP_HOLD (242), whose forced arms print TWO ON
lines (BETA_HOLD and COMP_HOLD) while a TSV row carries ONE witness:
  C10 a listed GROUP_HOLD row passes (cvt7-style: every run prints `VOTE_W: off` and `BETA_HOLD: off`).
  C11 a mismatched GROUP_HOLD witness fails, and the failure quotes the run's own GROUP_HOLD line.
  C12 cvt6-style runs with BETA_HOLD + COMP_HOLD ON pass when listed ONCE, by their BETA_HOLD line (242.7's plan) --
      and also when listed by their COMP_HOLD line instead (any one ON line may be the witness).
  C13 the same runs FAIL when the other ON line is wrong: (a) a replay sha that is not the registered one; (b) the
      other arm's complement path; (c) the COMP_HOLD line missing (`COMP_HOLD: off`); (d) an arm whose registration
      has ONE ON kind printing a second ON line; (e) listed by COMP_HOLD, the BETA_HOLD line wrong.
  C14 an ON GROUP_HOLD corpus run absent from the TSV fails: (a) a batch with no listed row; (b) one held run left out.
  C15 `off` runs are not required: unlisted runs printing `GROUP_HOLD: off` / `COMP_HOLD: off` pass; an unlisted run of
      a listed two-kind batch that prints no `COMP_HOLD: off` line fails, as 239's rule does for a listed kind.
  C16 prefix collisions: no KINDS prefix is a prefix of another (the necessary and sufficient condition for a
      `startswith` reader to select one line for two kinds); every patch prints exactly `<PREFIX>: off` / `<PREFIX>:
      on ...`; the module's MULTI_KIND lines == the registered cvt6 scorer's WITNESS_BH / WITNESS_CH, byte for byte.

ADDED AT CORRECTIONS 251 -- `cvt8`'s REST_HOLD (248) and `cvt9`'s WINDOW_HOLD (249).  cvt8's three forced arms print TWO ON
lines (GROUP_HOLD + REST_HOLD); cvt9's four path / dose arms print two (BETA_HOLD + COMP_HOLD) and EARLY / LATE THREE
(BETA_HOLD + COMP_HOLD + WINDOW_HOLD).  Each run is listed ONCE (248.7: by GROUP_HOLD; 249.7: by BETA_HOLD):
  C17 cvt8-style REST_HOLD two-kind runs pass, listed by their GROUP_HOLD line (248.7's plan) or by their REST_HOLD line;
      the unlisted k01 / ISO runs are held to `GROUP_HOLD: off` / `REST_HOLD: off`.
  C18 a wrong REST_HOLD line fails: (a) another replay sha; (b) `REST_HOLD: off`; (c) no REST_HOLD line; (d) HOLDHIGH
      (one ON kind) printing a REST_HOLD on-line; (e) listed by REST_HOLD, the GROUP_HOLD line wrong.
  C19 cvt9-style runs pass, listed by BETA_HOLD (249.7's plan): four two-kind arms and the three-kind EARLY / LATE; EARLY
      / LATE also pass listed by their WINDOW_HOLD or COMP_HOLD line; k01 is held to all three off lines.
  C20 a wrong or missing WINDOW_HOLD line fails: (a) EARLY printing LATE's window; (b) LATE printing `WINDOW_HOLD: off`;
      (c) EARLY with no WINDOW_HOLD line; (d) MIDDOSE (two kinds) printing a WINDOW_HOLD on-line; (e) EARLY listed by
      WINDOW_HOLD, its COMP_HOLD line wrong.
  C21 an unlisted ON corpus run of each new kind fails completeness: (a) / (c) a cvt8 / cvt9 batch with no listed row;
      (b) / (d) one forced / windowed run left out; (e) / (f) a run whose ONLY ON line is REST_HOLD / WINDOW_HOLD.
  C22 `off` lines are not required: unlisted runs printing `REST_HOLD: off` / `WINDOW_HOLD: off` pass; an unlisted run of
      a listed cvt8 / cvt9 batch with no `REST_HOLD: off` / `WINDOW_HOLD: off` line fails.
  C23 KINDS = 245's four unchanged + REST_HOLD + WINDOW_HOLD; no prefix of the six is a prefix of another (first letters
      V B G C R W); patch_resthold.py / patch_windowhold.py print only `<PREFIX>: off` / `<PREFIX>: on type=...`;
      witness_lines on one on and one off line of each of the six kinds; MULTI_KIND's cvt8 / cvt9 entries == the
      registered scorers' witness tables (and the arms whose registered witnesses are ON in 2+ kinds are exactly those
      entries); 245's `kinds scanned` line is unchanged byte for byte and a new line names the two added kinds.

ADDED AT CORRECTIONS 263 -- the ARGS-VALUE witness kinds for `cmo1` (255), whose M9* / W0* arms deviate from the
standard cell ONLY in CLI flags (`--momentum-param-base 0.9`, `--weight-decay-base 0`).  There is no `<KIND>: on`
line to read: the witness is the run's OWN `ARGS:` line, the prefix every run prints, read with argparse
last-wins semantics.  The kinds are `ARGS_MOMENTUM_BASE` / `ARGS_WD_BASE`; a TSV row's witness is
`<KIND>: <flag>=<value>`:
  C24 the parser and the registry: the module's re-typed ARGS reader == `analysis/argsline_guard.py`'s (RULE 20's
      registered parser, imported HERE only) on 9 real and synthetic ARGS lines, repeated flags and `--flag=value`
      included; ARGS_KINDS holds the two kinds with standards 0.99 / 0.1; PREFIX PROOF: no name of the 6 line kinds
      + 2 ARGS kinds is a prefix of another, `ARGS:` starts with no line-kind prefix, no kind name starts with
      `ARGS:`, and no ARGS-kind witness is itself an `ARGS:` line (so no kind can be misread).
  C25 a cmo1-style batch passes: 3 anchor arms unlisted at 0.99 / 0.1, 3 M9 arms listed by their
      ARGS_MOMENTUM_BASE witness and 3 W0 arms by their ARGS_WD_BASE witness -> exit 0, the three added lines
      reporting 6 listed, 6 deviating CSV rows in the standard cell, 0 cells mixing.
  C26 corruptions fail, each named: (a) an M9 row dropped from the list (a standard-cell CSV row whose ARGS
      deviates, unlisted); (b) a listed M9 run whose ARGS line says 0.99 (the flag never arrived); (c) a listed M9
      run whose ARGS says 0.8 (value != the listed witness); (d) a run deviating on BOTH flags listed by one;
      (e) a deviating, unlisted .out of the listed batch that is not yet a CSV row (the batch rule).
  C27 scope: an ingested run OUTSIDE the standard cell (300 epochs) whose ARGS carries 0.9 is counted DESCRIPTIVELY,
      not required to be listed; an absent flag is the standard (argparse default); a log with no ARGS line is
      counted, not failed.
  C28 cell mixing: two UNLISTED ingested runs of the SAME 15-key cell carrying different `--momentum-param-base`
      values fail (the pooling the list exists to prevent), and the same pair passes once one is listed.

ADDED AT CORRECTIONS 269 -- `cwd1` / `cwd2`'s DECAY_MASK (260 / 261) and `csv1`'s SHADOW_VOTE (262), two new
ENVIRONMENT switches whose `<PREFIX>: on ...` line no CSV column carries.  `cwd2`'s HIGHWD0 / LOWWD0 print THREE ON
lines (BETA_HOLD + COMP_HOLD + DECAY_MASK) and its HIGHHEADPATH two, so they are MULTI_KIND rows; `cwd1`'s masked arms
and `csv1`'s three switch arms print ONE:
  C29 a cwd1-style DECAY_MASK batch passes: k01 unlisted at `DECAY_MASK: off`, the 2 masked arms listed by their
      DECAY_MASK line, and the completeness line names the kind.
  C30 DECAY_MASK corruptions fail, each named: (a) a listed masked run printing `DECAY_MASK: off` (the mask never bit
      -- cwd1's BROKEN-MASK null, caught in the corpus layer); (b) a listed row whose witness is not the run's line;
      (c) one masked run dropped from the list; (d) a whole masked batch with no listed row; (e) an unlisted run of a
      listed DECAY_MASK batch that prints no `DECAY_MASK: off` line; `off` runs of an unlisted batch stay unlisted.
  C31 cwd2-style multi-kind runs listed ONCE pass, by their DECAY_MASK, BETA_HOLD or COMP_HOLD line, with the
      multi-kind line counting two 3-kind runs; and fail when another registered line is wrong: (a) HIGHWD0 printing
      `DECAY_MASK: off`; (b) LOWWD0 printing HIGHWD0's BETA_HOLD; (c) k01WD0 (one ON kind) printing a BETA_HOLD
      on-line; (d) HIGHHEADPATH (no mask) printing a DECAY_MASK on-line.
  C32 a csv1-style SHADOW_VOTE batch passes (INERT / SHADOWLOW / NAIVELOW listed by their SHADOW_VOTE line, MUTE by
      its VOTE_W line, k01 / HEAD unlisted at the off lines), and corruptions fail: (a) SHADOWLOW printing NAIVELOW's
      witness; (b) NAIVELOW printing `SHADOW_VOTE: off`; (c) INERT dropped from the list; (d) an unlisted run with no
      `SHADOW_VOTE: off` line; (e) MUTE, listed by VOTE_W, also printing a SHADOW_VOTE on-line.
  C33 KINDS = 251's six unchanged + DECAY_MASK + SHADOW_VOTE; the eight first letters differ (V B G C R W D S), so no
      prefix is a prefix of another and none collides with the ARGS reader; patch_decaymask.py / patch_shadowvote.py
      print only `<PREFIX>: off` / `<PREFIX>: on <field>=...`; witness_lines on one on and one off line of each of the
      eight kinds; MULTI_KIND's cwd2 entries == the registered cwd_design tables (and the cwd1 / cwd2 / csv1 arms whose
      registered witnesses are ON in 2+ kinds are exactly those entries, so cwd1 and csv1 register none); 245's and
      251's `kinds scanned` lines are unchanged byte for byte and ONE new line names the two added kinds.

ADDED AT CORRECTIONS 284 -- `cwd5`'s `CARW2` (281), the first run of the campaign that is TWO-AXIS: it BOTH prints an
ON `<KIND>` line (`DECAY_MASK`, the three `ctd1` carriers) AND deviates on an ARGS value (`--weight-decay-base 1e-2`,
its rung).  A TSV row carries ONE witness, and the two readers disagreed about which it must be (281.12): the KINDS
reader has a `MULTI_KIND` escape, the ARGS-value reader has none, so BOTH listings FAILed.  THE RULE: such a run is
listed with its **ARGS** witness and its ON kinds are registered in `MULTI_KIND` -- the only listing both readers
accept; the reverse listing still FAILs, so the rule is enforced by the module, not merely documented:
  C34 a cwd5-style ladder passes: the 2 anchor arms unlisted at `0.1` / `DECAY_MASK: off`, the 6 single-axis rung
      arms listed by their ARGS_WD_BASE value, and CARW2 listed by its ARGS_WD_BASE value with its DECAY_MASK line
      verified through MULTI_KIND; the new two-axis line counts the CARW2 run; and the single-axis batches that
      must keep working -- a cwd1-style kind-only batch and a cmo1-style ARGS-only batch -- pass merged in with it.
  C35 the rule is forced and every corruption FAILs, each named: (a) CARW2 listed by its DECAY_MASK line instead
      (the reverse listing, which has no escape); (b) its DECAY_MASK line carrying `wd=0.1`, the rung it never ran
      at; (c) `DECAY_MASK: off` (the mask never bit); (d) an ARGS line at the standard `0.1` (the rung never
      arrived); (e) an ARGS line at another rung's value (witness != the run's own value); (f) CARW2 dropped from
      the list (FAILs TWICE: completeness on the ON line, and the standard-cell ARGS rule); (g) a single-axis rung
      arm printing an ON DECAY_MASK line it has no MULTI_KIND entry for; (h) an unlisted anchor run with no
      `DECAY_MASK: off` line.
  C36 the registry and the print lines: MULTI_KIND gains exactly ONE entry, `("cwd5", "CARW2")`, registering exactly
      `DECAY_MASK`, whose literal == `analysis/cwd5_design.py`'s `CWD5.WITNESS_DM["CARW2"]` (the frozen table the
      registered cWD5 scorer imports) and whose `wd=` token is the arm's OWN rung; the single-kind entry does NOT
      disturb 251's `multi-kind runs` line, which is frozen over the entries registering `MULTI_KINDS_AT_251` or
      more kinds and stays byte-identical, as do 245's / 251's / 269's `kinds scanned` lines; `--check --runs` gains
      exactly ONE line.

ADDED AT CORRECTIONS 294 -- `caw2`'s XS / XL (290), the first runs of the campaign that deviate on TWO ARGS kinds at
once: AdamW base momentum `--momentum-param-base 0.9` AND the dose `--weight-decay-base 1.0`.  A TSV row carries ONE
witness, and 263's ARGS-value reader FAILs a run that deviates on a kind its witness does not name (C26d pins that for
an UNREGISTERED run, and it still does).  THE RULE: such a run is listed ONCE, by the ARGS witness of ANY one of its
deviating kinds (294's planned rows use `ARGS_WD_BASE`, the X cell's defining factor), and `MULTI_ARGS` registers the
witness of EVERY ARGS kind it deviates on; each registered value is then held to the run's OWN `ARGS:` line:
  C37 a caw2-style batch passes: K01 / MS / ML unlisted at 0.99 / 0.1, LS / LL / AS / AL listed by their
      ARGS_MOMENTUM_BASE value, XS / XL listed by their ARGS_WD_BASE value (and, separately, by their
      ARGS_MOMENTUM_BASE value) with the other kind verified through MULTI_ARGS; the new line counts 2 runs and is
      True; the ARGS block counts all 6 listed and 6 deviating standard-cell rows; and the cases that must keep
      working -- a cmo1-style single-ARGS batch, cwd5's switch + ARGS (two-axis) ladder and a cwd1-style kind-only
      batch -- pass merged in with it.
  C38 every corruption FAILs, each named: (a) XS's ARGS line at the standard wd 0.1 (the dose never arrived), listed
      by ARGS_WD_BASE; (b) the same, listed by ARGS_MOMENTUM_BASE (the REGISTERED kind is what catches it);
      (c) XS at momentum 0.99 (the base swap never arrived); (d) XS at wd 2.0, a wrong value of the LISTED kind;
      (e) XS at momentum 0.8, a wrong value of the kind the row does NOT carry; (f) XS dropped from the list;
      (g) AS run at wd 1.0 -- a two-ARGS run of an arm with NO MULTI_ARGS entry, which still FAILs as C26d does;
      (h) a deviating XS .out of the listed batch that is not yet a CSV row, unlisted (the batch rule).
  C39 the registry: MULTI_ARGS holds exactly two caw2 entries, (caw2, XS) and (caw2, XL), each registering exactly
      ARGS_MOMENTUM_BASE and ARGS_WD_BASE, whose witnesses == `args_witness(kind, value)` for the values in
      `analysis/caw2_design.py`'s registered ARGS (and `caw2_design.args_deviating_kinds` names exactly those two arms
      as two-kind); this test's caw2 ARGS payloads == `caw2_design.args_string` for all 9 arms; MULTI_KIND, KINDS and
      ARGS_KINDS are unchanged; 245's / 251's / 269's / 284's lines are unchanged byte for byte on their fixtures; and
      `--check --runs` gains exactly ONE line.
  C40 the registry guard: a MULTI_ARGS entry registering ONE kind, a witness of an unregistered kind, and a witness
      whose flag is not its kind's flag each FAIL, named, even without --runs.

ADDED AT CORRECTIONS 304 -- `cvl1`'s VAL_SPLIT (302 / 303), a train-set ENVIRONMENT switch (`VAL_SPLIT=5000:302`: 5,000
class-stratified training images held out, the model trains on 45,000) whose `VAL_SPLIT: on ...` line no CSV column
carries.  EVERY cvl1 run prints it; the 16 W1 runs (wd 0.1) are ONE-kind rows, and the 16 W4 runs (wd 5e-4) are
TWO-AXIS (284's rule: listed by their ARGS_WD_BASE witness, VAL_SPLIT registered in MULTI_KIND for (cvl1, <grain>W4)).
The fixture is cvl1's own shape: the 8 arms x seeds 184-187 with their REAL job ids (5080667-5080698, read from
alice2's queue) and ARGS payloads pinned to `analysis/cvl1_design.py`'s `args_line`; every log also carries `VAL:`
lines, which no reader may take:
  C41 a cvl1-style batch passes: 16 W1 runs listed by their VAL_SPLIT line, 16 W4 runs by `ARGS_WD_BASE:
      weight-decay-base=5e-4` with the VAL_SPLIT line held to MULTI_KIND; the completeness line names VAL_SPLIT (32
      ON, 32 CSV rows); 284's two-axis line counts the 16 W4 runs, True; the new `kinds scanned (CORRECTIONS 304)`
      line names VAL_SPLIT, 9 in all, True; and every earlier kind's batch passes MERGED IN with it (cvt8 / cvt9 /
      cwd1 / cwd2 / csv1 / cwd5 / cmo1 / caw2 fixtures).
  C42 every VAL_SPLIT corruption FAILs, each named: (a) a listed W1 run printing `VAL_SPLIT: off` (the switch never
      reached it); (b) split seed 303; (c) n_val 4999; (d) TWO witness lines; (e) a W1 run dropped from the list
      (completeness); (f) a W4 run listed by its VAL_SPLIT line (the REVERSE listing, no escape on the ARGS reader);
      (g) a W4 run printing split seed 303 and (h) `VAL_SPLIT: off` (MULTI_KIND); (i) a W4 ARGS line at the standard
      0.1 and (j) at 1e-3; (k) a W4 run dropped (completeness); (l) a W1 run at wd 5e-4, an UNREGISTERED two-axis run,
      listed either way; (m) a not-yet-ingested ON .out of the listed batch, unlisted (the batch rule); (n) an ON
      VAL_SPLIT corpus row of ANOTHER batch, unlisted.  And (o) an unlisted `VAL_SPLIT: off` run of the listed batch
      passes (off runs are not required).
  C43 the prefix proof and the line forms: no name of the 9 line kinds + 2 ARGS kinds is a prefix of another (VAL_SPLIT
      and VOTE_W share their first letter and diverge at the second, so 269's "first letters differ" is no longer the
      reason and is not claimed); the per-epoch `VAL:` line starts with no KINDS prefix and is not an `ARGS:` line;
      witness_lines puts one on and one off line of each of the NINE kinds under its own kind and collects no `VAL:`
      line; patch_valsplit.py prints only `VAL_SPLIT: off` / `VAL_SPLIT: on dataset=...` witness lines.
  C44 the registry: KINDS[:8] unchanged, KINDS[8] == ("VAL_SPLIT", "VAL_SPLIT: off"), KINDS_AT_269 == 8; MULTI_KIND's
      cvl1 entries are exactly (cvl1, <grain>W4) for cvl1_design.ARGS_DEVIATING, each registering exactly VAL_SPLIT
      with cvl1_design.witness_on(), byte for byte; MULTI_ARGS unchanged; the fixture's 32 ARGS payloads ==
      cvl1_design.args_line; on 284's cwd5 fixture `--check --runs` gains exactly ONE line over 294's module (the
      new `kinds scanned` line) and 269's `kinds scanned` line is unchanged byte for byte; without --runs nothing changes.
  C45 csh1's gamma (301.3): NO ARGS kind is added, and this pins why none is needed -- `gamma` is one of CELLKEYS and
      of aggregate.py's FIELDS; aggregate.parse_out writes each csh1 arm's `--gamma` token (1 / 0.999685 / 0.99941,
      csh1_design.GAMMA_TOKEN) into the row, verbatim; _pooled keeps gamma-1 and gamma<1 rows of one otherwise equal
      cell apart; ARGS_KINDS names no gamma flag; and a csh1-style batch (6 arms, real seed-180 job ids, payloads ==
      csh1_design.args_string) passes listed by `ARGS_WD_BASE: weight-decay-base=5e-4` ONLY (301.3's plan), while a
      dropped gamma<1 row still FAILs (standard-cell ARGS rule).

ADDED AT CORRECTIONS 308 -- PATCH_DECAYROUTE (305) and its two batches, `cai1` (306) and `crd1` (307).  The patched tree
prints `DECAY_ROUTE: off` or exactly ONE `DECAY_ROUTE: on mode=<m> base=<alg> wd=<repr> lambda=<repr|na> lambda_f32=<repr|na>
gamma=<repr>` line on EVERY run, which no CSV column carries.  `cai1`'s 32 runs ALL run at `--weight-decay-base 0` (the
patch refuses alpha_indep at any other value), so every one is TWO-AXIS (284's rule: listed by `ARGS_WD_BASE:
weight-decay-base=0`, the DECAY_ROUTE line registered in MULTI_KIND for its (cai1, <grain><rung>) arm).  `crd1`'s 12 SR* /
TR* runs are at the standard 0.1 and are ONE-kind rows listed by their DECAY_ROUTE line; its 6 AI* runs (wd 0) are
TWO-AXIS.  So crd1 owes 18 rows, not 24: a (run, job_id) key may be listed ONCE.  Every listed run of either batch is
also held to its ARM's registered line (DECAY_ROUTE_ARMS), so a TSV row that copied a wrong mode or LAMBDA FAILs too.
The fixtures carry the batches' REAL job ids (squeue on alice2, 2026-09-22: crd1 5081273-5081290, cai1 5081292-5081323)
and ARGS payloads pinned to `cai1_design.args_line` / `crd1_design.args_string`:
  C46 a cai1-style batch (32 two-axis runs) and a crd1-style batch (12 one-kind + 6 two-axis) pass, separately and merged
      with every earlier kind's fixture; the completeness line names DECAY_ROUTE; 284's two-axis line counts 32 / 6 / 38
      (+ earlier) runs; the new `kinds scanned (CORRECTIONS 308)` line names DECAY_ROUTE, 10 in all, True; the new
      `decay-route runs (CORRECTIONS 308)` line counts 32 / 18 / 50, True; crd1's AI* runs count on the ARGS block as
      standard-cell rows (the mechanism cell), cai1's do not (CIFAR-10).
  C47 every DECAY_ROUTE corruption FAILs, each named -- wrong MODE: (a) crd1 SRS printing trace_only's line; (b) the same
      with the TSV row copying the wrong line (caught ONLY by DECAY_ROUTE_ARMS); wrong LAMBDA: (c) a cai1 I4 run printing
      I5's line (MULTI_KIND); (d) crd1 AIS at lambda 0.0005; (e) a lambda_f32 token that is not LAMBDA's float32; (f) gamma
      0.97; (g) `DECAY_ROUTE: off` on a listed ON run (the switch never reached it), one-kind and two-axis; (h) TWO
      witness lines; (i) NO witness line; (j) a cai1 run dropped from the list; (k) a crd1 AIS run dropped (completeness
      AND the standard-cell ARGS rule); (l) a crd1 TRL run dropped; (m) the two-axis runs listed by their DECAY_ROUTE
      line (the REVERSE listing: no ARGS escape); (n) 307.9's owed list read as 24 rows (AI* listed twice: duplicate
      key); (o) a crd1 SR* run at wd 0 (an UNREGISTERED two-axis run); (p) a cai1 ARGS line at wd 0.1 (the removed
      decay came back); (q) a listed run of a route batch whose arm is not registered; (r) a not-yet-ingested ON .out of
      the listed batch, unlisted (the batch rule); (s) an ON DECAY_ROUTE corpus row of an UNLISTED batch.
  C48 `DECAY_ROUTE: off`, printed by every run of the patched tree with the switch unset: an unlisted corpus run printing
      it (in or out of a listed batch) passes and is not required to be listed; an unlisted run of a listed route batch
      with NO DECAY_ROUTE line FAILs (the batch rule); a DECAY_MASK tree's `DECAY_MASK: off` line beside it is read as
      DECAY_MASK only.
  C49 the prefix proof and the line forms: DECAY_ROUTE and DECAY_MASK share `DECAY_` and diverge at index 6 (`R` / `M`),
      so NEITHER is a prefix of the other; no name of the 10 line kinds + 2 ARGS kinds is a prefix of another; witness_lines
      puts one on and one off line of each of the TEN kinds under its own kind; kind_of reads both DECAY_ lines correctly;
      patch_decayroute.py prints only `DECAY_ROUTE: off` / `DECAY_ROUTE: on mode=...`; the registry literals ==
      cai1_design.witness_on / crd1_design.dr_witness, and == the three RR2 witness strings the real proof log 5081090
      recorded where it is on disk (skipped, not failed, where it is not).
  C50 the registry: KINDS[:9] unchanged, KINDS[9] == ("DECAY_ROUTE", "DECAY_ROUTE: off"), KINDS_AT_304 == 9; DECAY_ROUTE_ARMS
      is exactly cai1's 8 + crd1's 6 arms; MULTI_KIND gains exactly cai1's 8 + crd1's AIS / AIL, each registering exactly
      DECAY_ROUTE with its arm's line, == the arms the designs name as ARGS-deviating; MULTI_ARGS / ARGS_KINDS unchanged;
      this test's 50 payloads == the designs'; on every earlier fixture `--check --runs` gains exactly the TWO 308 lines
      (every other byte == 304's module output) and 304's `kinds scanned` line is unchanged byte for byte; without --runs
      nothing changes; the registry guard FAILs a malformed DECAY_ROUTE_ARMS entry and a MULTI_KIND line that disagrees.

RUN:  python3 tests/test_corpus_exclusions_check.py      (stdlib only; exit 0 all pass, 1 any fail)
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MODULE = os.path.join(REPO, "analysis", "corpus_exclusions.py")
REAL_TSV = os.path.join(REPO, "results", "CORPUS-EXCLUSIONS.tsv")
FAILED = []

# witness lines in the exact forms the patches print (patches/patch_voteweight.py, patches/patch_betahold.py, 237.4)
VW_MUTE = "VOTE_W: on type=scalar items=50:layer4.1.bn2.weight:w=0.0:group=0:groupsize=53"
BH_TRI = ("BETA_HOLD: on type=blockwise group=1 groupsize=1 name=layer4.1.bn2.weight mode=tri P=9428 "
          "b0=-13.815510749816895 ms=0.001 lo=-15.0 hi=-2.3026 peak=-4.387510749816894")
BH_TRI_5041 = ("BETA_HOLD: on type=blockwise group=1 groupsize=1 name=layer4.1.bn2.weight mode=tri P=5041 "
               "b0=-13.815510749816895 ms=0.001 lo=-15.0 hi=-2.3026 peak=-8.772510749816895")
BH_FLOOR = "BETA_HOLD: on type=blockwise group=1 groupsize=1 name=layer4.1.bn2.weight mode=floor value=-15.0"
# CORRECTIONS 245: the registered lines of patches/patch_grouphold.py (243.4) and patches/patch_comphold.py (242.4);
# C16 checks each against the registered scorer's own table.
GH_NAMES = "names=layer4.0.bn2.weight+layer4.0.shortcut.1.weight+layer4.1.bn2.weight"
GH_TRI = ("GROUP_HOLD: on type=blockwise group=1 groupsize=3 " + GH_NAMES + " mode=tri P=8609 b0=-13.815510749816895 "
          "ms=0.001 lo=-15.0 hi=-2.3026 peak=-5.2065107498168945")
GH_TRI_ISO = ("GROUP_HOLD: on type=blockwise group=1 groupsize=3 " + GH_NAMES + " mode=tri P=5153 b0=-13.815510749816895 "
              "ms=0.001 lo=-15.0 hi=-2.3026 peak=-8.662510749816894")
GH_FLOOR = "GROUP_HOLD: on type=blockwise group=1 groupsize=3 " + GH_NAMES + " mode=floor value=-15.0"
CH_REC = ("COMP_HOLD: on type=blockwise group=0 groupsize=52 mode=rec id=cvt6_headpath "
          "sha256=74be71fa524ad0122d1408e01dd2b633b004b2e27228393fe6e593f494358a5d knots=500 n0=2 n1=49902 "
          "b0=-13.815510749816895 lo=-15.0 hi=-2.3026 vmax=-4.852388381958008 vlast=-15.0")
CH_TRI = ("COMP_HOLD: on type=blockwise group=0 groupsize=52 mode=tri P=9428 b0=-13.815510749816895 ms=0.001 lo=-15.0 "
          "hi=-2.3026 peak=-4.387510749816894")
CH_REC_OTHER_SHA = CH_REC.replace("sha256=74be71fa", "sha256=00000000")
# CORRECTIONS 251: the registered lines of patches/patch_resthold.py (248.4) and patches/patch_windowhold.py (249.4), and
# the cvt8 / cvt9 lines of the older kinds; C23 checks each against the registered cVT8 / cVT9 scorers' tables.
GH_TRI_BIG = ("GROUP_HOLD: on type=blockwise group=1 groupsize=3 " + GH_NAMES + " mode=tri P=9428 b0=-13.815510749816895 "
              "ms=0.001 lo=-15.0 hi=-2.3026 peak=-4.387510749816894")
RH_REC = ("REST_HOLD: on type=blockwise group=0 groupsize=59 mode=rec id=cvt8_isopath "
          "sha256=08ab25f3a329cb260bb39fb72f3299c021e7169bf612fa27d539166296e28e70 knots=500 n0=2 n1=49902 "
          "b0=-13.815510749816895 lo=-15.0 hi=-2.3026 vmax=-4.985378742218018 vlast=-14.924964427947998")
RH_REC_OTHER_SHA = RH_REC.replace("sha256=08ab25f3", "sha256=00000000")
BH_TRI_7235 = ("BETA_HOLD: on type=blockwise group=1 groupsize=1 name=layer4.1.bn2.weight mode=tri P=7235 "
               "b0=-13.815510749816895 ms=0.001 lo=-15.0 hi=-2.3026 peak=-6.580510749816894")
BH_TRI_8609 = ("BETA_HOLD: on type=blockwise group=1 groupsize=1 name=layer4.1.bn2.weight mode=tri P=8609 "
               "b0=-13.815510749816895 ms=0.001 lo=-15.0 hi=-2.3026 peak=-5.2065107498168945")
WH_EARLY = ("WINDOW_HOLD: on type=blockwise group=1 name=layer4.1.bn2.weight base=tri P=9428 n0=0 n1=9429 outside=floor "
            "value=-15.0")
WH_LATE = ("WINDOW_HOLD: on type=blockwise group=1 name=layer4.1.bn2.weight base=tri P=9428 n0=9429 n1=end outside=floor "
           "value=-15.0")


def chk(cond, label, extra=""):
    print("  %-4s %s%s" % ("PASS" if cond else "FAIL", label, ("   " + extra) if extra else ""))
    if not cond:
        FAILED.append(label)
    return bool(cond)


def tsv_header():
    for ln in open(REAL_TSV):
        if ln.strip() and not ln.startswith("#"):
            return ln.rstrip("\n").split("\t")
    raise SystemExit("no header in %s" % REAL_TSV)


def row(run, job, witness):
    batch, arm = run.split("-")[0], run.split("-")[1]
    vals = {"run": run, "job_id": job, "batch": batch, "arm": arm, "looks_like": "HEAD (synthetic)",
            "intervention": "synthetic", "witness": witness, "registered_at": "test", "reason": "synthetic"}
    return [vals[c] for c in tsv_header()]


# CORRECTIONS 263: the CSV the fixture writes now carries the 15 cell-key columns at their standard-cell values, so
# the ARGS-value block can ask whether a deviating row sits in the standard cell (and which rows share a cell).  The
# defaults reproduce 239's / 245's / 251's behaviour exactly: `plateau5` stays empty, so the noise-floor lines are
# unchanged, and `args=` defaults to 239's ARGS line, which carries neither factor flag.
CSV_COLS = ["run", "job_id", "network", "dataset", "granularity", "base", "meta", "meta_stepsize", "alpha0", "gamma",
            "augment", "beta_clip", "batch_size", "epochs_requested", "hier", "lam", "eta_ratio",
            "superseded", "collapsed", "complete", "plateau5"]
CSV_STD = {"network": "PlainNet18_c100", "dataset": "CIFAR100", "granularity": "scalar", "base": "SGDm",
           "meta": "Lion", "meta_stepsize": "1e-3", "alpha0": "1e-6", "gamma": "1", "augment": "1",
           "beta_clip": "-15:-2.3026", "batch_size": "100", "epochs_requested": "100", "hier": "", "lam": "",
           "eta_ratio": "", "superseded": "0", "collapsed": "0", "complete": "1", "plateau5": ""}
DEFAULT_ARGS = "--network PlainNet18_c100 --seed 90"


def run_check(listed, corpus, logs, with_runs=True, args=None, cells=None, module_append=None):
    """listed: [(run, job, witness)]; corpus: [(run, job)]; logs: {(run, job): [lines]} -> (rc, stdout).

    args:  {(run, job): "<ARGS payload>"}  -- the run's own ARGS line (default: 239's, no factor flag).
    cells: {(run, job): {column: value}}   -- CSV cell-key overrides (default: the standard cell).
    module_append: source text inserted into the module COPY just before its `if __name__` block (CORRECTIONS 294's
                   C40 corrupts a registry that way); None (the default) copies the module byte for byte, as before."""
    args = args or {}
    cells = cells or {}
    tmp = tempfile.mkdtemp(prefix="ce_check_test_")
    try:
        os.makedirs(os.path.join(tmp, "analysis"))
        os.makedirs(os.path.join(tmp, "results"))
        shutil.copyfile(MODULE, os.path.join(tmp, "analysis", "corpus_exclusions.py"))
        if module_append is not None:
            mp = os.path.join(tmp, "analysis", "corpus_exclusions.py")
            src = open(mp).read()
            cut = src.rindex('\nif __name__ == "__main__":')
            with open(mp, "w") as f:
                f.write(src[:cut] + "\n" + module_append + "\n" + src[cut:])
        with open(os.path.join(tmp, "results", "CORPUS-EXCLUSIONS.tsv"), "w") as f:
            f.write("# synthetic exclusion list\n" + "\t".join(tsv_header()) + "\n")
            for r in listed:
                f.write("\t".join(row(*r)) + "\n")
        with open(os.path.join(tmp, "results", "all_runs.csv"), "w") as f:
            f.write(",".join(CSV_COLS) + "\n")
            for run, job in corpus:
                v = dict(CSV_STD, run=run, job_id=job)
                v.update(cells.get((run, job), {}))
                f.write(",".join(v[c] for c in CSV_COLS) + "\n")
        for (run, job), lines in logs.items():
            d = os.path.join(tmp, "runs", run.split("-")[0])
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "%s-%s.out" % (run, job)), "w") as f:
                al = args.get((run, job), DEFAULT_ARGS)
                f.write(("ARGS: %s\n" % al if al is not None else "") + "NODE=synthetic\n")
                for ln in lines:
                    f.write(ln + "\n")
                f.write("epoch 1 train 1.0 test 1.0\nRUN_DONE\n")
        cmd = [sys.executable, os.path.join(tmp, "analysis", "corpus_exclusions.py"), "--check"]
        if with_runs:
            cmd += ["--runs", os.path.join(tmp, "runs")]
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        return p.returncode, p.stdout.replace(tmp + os.sep, "<tmp>/")
    finally:
        shutil.rmtree(tmp)


def fails(out):
    return [ln.strip() for ln in out.splitlines() if ln.startswith("  FAIL ")]


def show(out):
    return " | ".join(fails(out)) or "(no FAIL line)"


# ---- fixtures ----------------------------------------------------------------------------------------------
# CORRECTIONS 251: C1-C9's synthetic batches were named `cvt9` / `cvt8` at 239, when no such batch existed.  Both are
# now registered batches with MULTI_KIND entries (a listed run of the batch holds its unlisted runs to the off line of
# every kind registered there), so the fixtures are renamed `syn9` / `syn8`; no assertion changed.
K01, HOLD, HOLDLOW = ("syn9-k01-s90", "5000001"), ("syn9-HOLDHIGH-s90", "5000002"), ("syn9-HOLDLOW-s90", "5000003")
VK01, VMUTE = ("syn8-k01-s78", "5000011"), ("syn8-MUTE-s78", "5000012")


def bh_batch():
    listed = [HOLD + (BH_TRI,)]
    corpus = [K01, HOLD]
    logs = {K01: ["VOTE_W: off", "BETA_HOLD: off"], HOLD: ["VOTE_W: off", BH_TRI]}
    return listed, corpus, logs


def vw_batch():
    listed = [VMUTE + (VW_MUTE,)]
    corpus = [VK01, VMUTE]
    logs = {VK01: ["VOTE_W: off"], VMUTE: [VW_MUTE]}
    return listed, corpus, logs


G_K01, G_ISO = ("cvt7-k01-s99", "5000041"), ("cvt7-ISO-s99", "5000042")
G_HIGH, G_LOW = ("cvt7-HOLDHIGH-s99", "5000043"), ("cvt7-HOLDLOW-s99", "5000044")
C_K01, C_LOW = ("cvt6-k01-s96", "5000051"), ("cvt6-HOLDLOW-s96", "5000052")
C_HHP, C_LMP, C_LHP = ("cvt6-HIGHHEADPATH-s96", "5000053"), ("cvt6-LOWMUTEPATH-s96", "5000054"), \
    ("cvt6-LOWHEADPATH-s96", "5000055")


def gh_batch():
    """cvt7-style (243): every run prints VOTE_W: off and BETA_HOLD: off; the held run is listed by GROUP_HOLD."""
    listed = [G_HIGH + (GH_TRI,)]
    corpus = [G_K01, G_ISO, G_HIGH]
    logs = {G_K01: ["VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off"],
            G_ISO: ["VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off"],
            G_HIGH: ["VOTE_W: off", "BETA_HOLD: off", GH_TRI]}
    return listed, corpus, logs


def ch_batch(by="BETA_HOLD"):
    """cvt6-style (242): HOLDLOW one ON kind; the three forced arms two (BETA_HOLD + COMP_HOLD), listed ONCE."""
    logs = {C_K01: ["VOTE_W: off", "BETA_HOLD: off", "COMP_HOLD: off"],
            C_LOW: ["VOTE_W: off", BH_FLOOR, "COMP_HOLD: off"],
            C_HHP: ["VOTE_W: off", BH_TRI, CH_REC],
            C_LMP: ["VOTE_W: off", BH_FLOOR, CH_TRI],
            C_LHP: ["VOTE_W: off", BH_FLOOR, CH_REC]}
    pick = 1 if by == "BETA_HOLD" else 2
    listed = [C_LOW + (BH_FLOOR,)] + [k + (logs[k][pick],) for k in (C_HHP, C_LMP, C_LHP)]
    corpus = [C_K01, C_LOW, C_HHP, C_LMP, C_LHP]
    return listed, corpus, logs


R_K01, R_ISO = ("cvt8-k01-s102", "5000071"), ("cvt8-ISO-s102", "5000072")
R_HH, R_HB = ("cvt8-HOLDHIGH-s102", "5000073"), ("cvt8-HOLDBIG-s102", "5000074")
R_HIP, R_BIP, R_LIP = ("cvt8-HIGHISOPATH-s102", "5000075"), ("cvt8-BIGISOPATH-s102", "5000076"), \
    ("cvt8-LOWISOPATH-s102", "5000077")
W_K01, W_LHP, W_HHP = ("cvt9-k01-s105", "5000081"), ("cvt9-LOWHEADPATH-s105", "5000082"), ("cvt9-HIGHHEADPATH-s105", "5000083")
W_MID, W_RES = ("cvt9-MIDDOSE-s105", "5000084"), ("cvt9-RESDOSE-s105", "5000085")
W_EARLY, W_LATE = ("cvt9-EARLY-s105", "5000086"), ("cvt9-LATE-s105", "5000087")


def rh_batch(by="GROUP_HOLD"):
    """cvt8-style (248): HOLDHIGH / HOLDBIG one ON kind (GROUP_HOLD); the three forced arms two (+ REST_HOLD); listed ONCE."""
    logs = {R_K01: ["VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off", "REST_HOLD: off"],
            R_ISO: ["VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off", "REST_HOLD: off"],
            R_HH: ["VOTE_W: off", "BETA_HOLD: off", GH_TRI, "REST_HOLD: off"],
            R_HB: ["VOTE_W: off", "BETA_HOLD: off", GH_TRI_BIG, "REST_HOLD: off"],
            R_HIP: ["VOTE_W: off", "BETA_HOLD: off", GH_TRI, RH_REC],
            R_BIP: ["VOTE_W: off", "BETA_HOLD: off", GH_TRI_BIG, RH_REC],
            R_LIP: ["VOTE_W: off", "BETA_HOLD: off", GH_FLOOR, RH_REC]}
    pick = 2 if by == "GROUP_HOLD" else 3
    listed = [k + (logs[k][2],) for k in (R_HH, R_HB)] + [k + (logs[k][pick],) for k in (R_HIP, R_BIP, R_LIP)]
    corpus = [R_K01, R_ISO, R_HH, R_HB, R_HIP, R_BIP, R_LIP]
    return listed, corpus, logs


def wh_batch(by="BETA_HOLD"):
    """cvt9-style (249): four arms with BETA_HOLD + COMP_HOLD ON, EARLY / LATE with + WINDOW_HOLD; listed ONCE."""
    logs = {W_K01: ["VOTE_W: off", "BETA_HOLD: off", "COMP_HOLD: off", "WINDOW_HOLD: off"],
            W_LHP: ["VOTE_W: off", BH_FLOOR, CH_REC, "WINDOW_HOLD: off"],
            W_HHP: ["VOTE_W: off", BH_TRI, CH_REC, "WINDOW_HOLD: off"],
            W_MID: ["VOTE_W: off", BH_TRI_7235, CH_REC, "WINDOW_HOLD: off"],
            W_RES: ["VOTE_W: off", BH_TRI_8609, CH_REC, "WINDOW_HOLD: off"],
            W_EARLY: ["VOTE_W: off", BH_TRI, CH_REC, WH_EARLY],
            W_LATE: ["VOTE_W: off", BH_TRI, CH_REC, WH_LATE]}
    pick = {"BETA_HOLD": 1, "COMP_HOLD": 2, "WINDOW_HOLD": 3}[by]
    listed = [k + (logs[k][1],) for k in (W_LHP, W_HHP, W_MID, W_RES)] + [k + (logs[k][pick],) for k in (W_EARLY, W_LATE)]
    corpus = [W_K01, W_LHP, W_HHP, W_MID, W_RES, W_EARLY, W_LATE]
    return listed, corpus, logs


# ---- CORRECTIONS 263: cmo1-style ARGS-value fixtures --------------------------------------------------------
# The payload is `cmo1`'s real ARGS line (255.10; read on alice2 from cmo1-k01-s108-5025983.out and its twins),
# with the two factor flags and the grouping substituted.
CMO_ARGS = ("--optimizer HF --alg-base SGDm --momentum-param-base %s --weight-decay-base %s --alg-meta Lion "
            "--momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0 --dataset CIFAR100 "
            "--NN-name ResNet18_c100 --batch-size 100 --max-time 999:00:00 --gamma 1 --meta-stepsize 1e-3 "
            "--alpha0 1e-6 --num-epochs 100 --stepsize-groups %s --seed 108 "
            "--save-directory /home/s5014158/metaopt/runs/cmo1 --run-name %s")
ISO_SETS = "sets:1-49,51-52,54-58,60-62/layer4.0.bn2.weight,layer4.0.shortcut.1.weight,layer4.1.bn2.weight"
W_MOM = "ARGS_MOMENTUM_BASE: momentum-param-base=0.9"
W_WD = "ARGS_WD_BASE: weight-decay-base=0"
CMO_ARMS = [("k01", "scalar", "0.99", "0.1"), ("kL", "layerwise", "0.99", "0.1"), ("ISO", ISO_SETS, "0.99", "0.1"),
            ("M9k01", "scalar", "0.9", "0.1"), ("M9kL", "layerwise", "0.9", "0.1"), ("M9ISO", ISO_SETS, "0.9", "0.1"),
            ("W0k01", "scalar", "0.99", "0"), ("W0kL", "layerwise", "0.99", "0"), ("W0ISO", ISO_SETS, "0.99", "0")]
CMO = dict((arm, ("cmo1-%s-s108" % arm, "502598%d" % (3 + i))) for i, (arm, _g, _m, _w) in enumerate(CMO_ARMS))


def cmo_batch():
    """cmo1-style (255): 3 anchor arms at 0.99 / 0.1 and 6 arms deviating in ONE CLI flag, listed by that value."""
    listed, corpus, logs, args, cells = [], [], {}, {}, {}
    for arm, grouping, mom, wd in CMO_ARMS:
        key = CMO[arm]
        corpus.append(key)
        logs[key] = ["VOTE_W: off", "BETA_HOLD: off"]
        args[key] = CMO_ARGS % (mom, wd, grouping, key[0])
        cells[key] = {"network": "ResNet18_c100",
                      "granularity": {"scalar": "scalar", "layerwise": "layerwise"}.get(grouping, "blockwise")}
        if mom != "0.99":
            listed.append(key + (W_MOM,))
        elif wd != "0.1":
            listed.append(key + (W_WD,))
    return listed, corpus, logs, args, cells


# ---- CORRECTIONS 269: cwd1 / cwd2 (DECAY_MASK) and csv1 (SHADOW_VOTE) fixtures -------------------------------
# The registered lines of patches/patch_decaymask.py (260.7 / 261.7) and patches/patch_shadowvote.py (262.7), re-typed;
# C33 checks each against the registered tables (analysis/cwd_design.py, imported UNEDITED by both cWD scorers, and the
# registered cSV1 scorer).  The keys below are the REAL run names and job ids of the three batches, so the synthetic
# cases have the shape the landing tracks will append.
DM_NS_IDX = "2,5,8,11,14,17,20,23,26,29,32,35,38,41,44,47,50,53,56,59"
DM_NS_NAMES = ("bn1.weight,layer1.0.bn1.weight,layer1.0.bn2.weight,layer1.1.bn1.weight,layer1.1.bn2.weight,"
               "layer2.0.bn1.weight,layer2.0.bn2.weight,layer2.0.shortcut.1.weight,layer2.1.bn1.weight,"
               "layer2.1.bn2.weight,layer3.0.bn1.weight,layer3.0.bn2.weight,layer3.0.shortcut.1.weight,"
               "layer3.1.bn1.weight,layer3.1.bn2.weight,layer4.0.bn1.weight,layer4.0.bn2.weight,"
               "layer4.0.shortcut.1.weight,layer4.1.bn1.weight,layer4.1.bn2.weight")
DM_NORMSCALE = ("DECAY_MASK: on base=SGDm wd=0.1 spec=normscale masked=20 of=62 numel=4800 idx=" + DM_NS_IDX
                + " names=" + DM_NS_NAMES)
DM_CARRIER = ("DECAY_MASK: on base=SGDm wd=0.1 spec=layer4.1.bn2.weight masked=1 of=53 numel=512 idx=50 "
              "names=layer4.1.bn2.weight")
DM_WRONG = DM_NORMSCALE.replace("masked=20", "masked=19")      # a corrupted witness: one scale short
SV_INERT = ("SHADOW_VOTE: on type=scalar base=SGDm vote=shadow applied=shared floor=na "
            "items=50:layer4.1.bn2.weight:numel=512")
SV_SHADOWLOW = ("SHADOW_VOTE: on type=scalar base=SGDm vote=shadow applied=floor floor=-15.0 "
                "items=50:layer4.1.bn2.weight:numel=512")
SV_NAIVELOW = ("SHADOW_VOTE: on type=scalar base=SGDm vote=natural applied=floor floor=-15.0 "
               "items=50:layer4.1.bn2.weight:numel=512")

D1_K01, D1_NWD, D1_LNWD = ("cwd1-k01-s128", "5045342"), ("cwd1-k01NWD-s128", "5045343"), ("cwd1-kLNWD-s128", "5045344")
D1_NWD2, D1_LNWD2 = ("cwd1-k01NWD-s129", "5045346"), ("cwd1-kLNWD-s129", "5045347")
D2_K01, D2_WD0 = ("cwd2-k01-s132", "5045380"), ("cwd2-k01WD0-s132", "5045381")
D2_HHP, D2_HWD, D2_LWD = ("cwd2-HIGHHEADPATH-s132", "5045382"), ("cwd2-HIGHWD0-s132", "5045383"), \
    ("cwd2-LOWWD0-s132", "5045384")
S1_K01, S1_HEAD, S1_MUTE = ("csv1-k01-s136", "5045359"), ("csv1-HEAD-s136", "5045364"), ("csv1-MUTE-s136", "5045363")
S1_IN, S1_SL, S1_NL = ("csv1-INERT-s136", "5045360"), ("csv1-SHADOWLOW-s136", "5045361"), \
    ("csv1-NAIVELOW-s136", "5045362")
CWD1_OFF = ["VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off", "REST_HOLD: off"]   # cvt8 lineage (260)


def dm_batch():
    """cwd1-style (260): k01 unlisted at `DECAY_MASK: off`; the masked arms listed by their DECAY_MASK line."""
    logs = {D1_K01: CWD1_OFF + ["DECAY_MASK: off"]}
    for k in (D1_NWD, D1_LNWD, D1_NWD2, D1_LNWD2):
        logs[k] = CWD1_OFF + [DM_NORMSCALE]
    listed = [k + (DM_NORMSCALE,) for k in (D1_NWD, D1_LNWD, D1_NWD2, D1_LNWD2)]
    corpus = [D1_K01, D1_NWD, D1_LNWD, D1_NWD2, D1_LNWD2]
    return listed, corpus, logs


def dm2_batch(by="DECAY_MASK"):
    """cwd2-style (261): k01WD0 ONE ON kind; HIGHHEADPATH two (BETA_HOLD + COMP_HOLD); HIGHWD0 / LOWWD0 THREE."""
    logs = {D2_K01: ["VOTE_W: off", "BETA_HOLD: off", "COMP_HOLD: off", "WINDOW_HOLD: off", "DECAY_MASK: off"],
            D2_WD0: ["VOTE_W: off", "BETA_HOLD: off", "COMP_HOLD: off", "WINDOW_HOLD: off", DM_CARRIER],
            D2_HHP: ["VOTE_W: off", BH_TRI, CH_REC, "WINDOW_HOLD: off", "DECAY_MASK: off"],
            D2_HWD: ["VOTE_W: off", BH_TRI, CH_REC, "WINDOW_HOLD: off", DM_CARRIER],
            D2_LWD: ["VOTE_W: off", BH_FLOOR, CH_REC, "WINDOW_HOLD: off", DM_CARRIER]}
    pick = {"BETA_HOLD": 1, "COMP_HOLD": 2, "DECAY_MASK": 4}[by]
    listed = ([D2_WD0 + (DM_CARRIER,), D2_HHP + (logs[D2_HHP][1 if by == "DECAY_MASK" else pick],)]
              + [k + (logs[k][pick],) for k in (D2_HWD, D2_LWD)])
    corpus = [D2_K01, D2_WD0, D2_HHP, D2_HWD, D2_LWD]
    return listed, corpus, logs


def sv_batch():
    """csv1-style (262): three SHADOW_VOTE arms with ONE ON kind, MUTE with VOTE_W, k01 / HEAD at every off line."""
    off3 = ["BETA_HOLD: off", "COMP_HOLD: off", "WINDOW_HOLD: off"]                 # cvt9 lineage (262)
    logs = {S1_K01: ["VOTE_W: off"] + off3 + ["SHADOW_VOTE: off"],
            S1_HEAD: ["VOTE_W: off"] + off3 + ["SHADOW_VOTE: off"],
            S1_MUTE: [VW_MUTE] + off3 + ["SHADOW_VOTE: off"],
            S1_IN: ["VOTE_W: off"] + off3 + [SV_INERT],
            S1_SL: ["VOTE_W: off"] + off3 + [SV_SHADOWLOW],
            S1_NL: ["VOTE_W: off"] + off3 + [SV_NAIVELOW]}
    listed = [S1_MUTE + (VW_MUTE,), S1_IN + (SV_INERT,), S1_SL + (SV_SHADOWLOW,), S1_NL + (SV_NAIVELOW,)]
    corpus = [S1_K01, S1_HEAD, S1_MUTE, S1_IN, S1_SL, S1_NL]
    return listed, corpus, logs


# ---- CORRECTIONS 284: cwd5's TWO-AXIS run (an ON <KIND> line AND a deviating ARGS value) ----------------------
# `cwd5` (281) is a four-rung coupled weight-decay ladder: `k01W1` / `kLW1` at the standard `0.1` and six arms at
# `1e-2` / `1e-3` / `5e-4` that deviate on `--weight-decay-base` ALONE, plus `CARW2` -- scalar at `1e-2` with
# PATCH_DECAYMASK on the three `ctd1` carriers, which therefore BOTH deviates on an ARGS value AND prints an ON
# DECAY_MASK line.  The run names, job ids and ARGS payload below are the batch's REAL ones (281.8); the DECAY_MASK
# line is the registered `cwd5_design.CWD5.WITNESS_DM["CARW2"]`, re-typed (C36 pins it to that table).
CWD5_ARGS = ("--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base %s --alg-meta Lion "
             "--momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0 --dataset CIFAR100 "
             "--NN-name ResNet18_c100 --batch-size 100 --max-time 999:00:00 --gamma 1 --meta-stepsize 1e-3 "
             "--alpha0 1e-6 --num-epochs 100 --stepsize-groups %s --seed 146 "
             "--save-directory /home/s5014158/metaopt/runs/cwd5 --run-name %s")
DM_CARRIERS3_W2 = ("DECAY_MASK: on base=SGDm wd=0.01 spec=layer4.0.bn2.weight+layer4.0.shortcut.1.weight+"
                   "layer4.1.bn2.weight masked=3 of=62 numel=1536 idx=50,53,59 "
                   "names=layer4.0.bn2.weight,layer4.0.shortcut.1.weight,layer4.1.bn2.weight")
DM_CARRIERS3_W1 = DM_CARRIERS3_W2.replace("wd=0.01", "wd=0.1")   # the rung CARW2 never ran at: a corrupted witness
# (arm, stepsize-groups / granularity, the rung's `--weight-decay-base` token, job id of seed 146)
CWD5_ARMS = [("k01W1", "scalar", "0.1", "5052142"), ("kLW1", "layerwise", "0.1", "5052143"),
             ("k01W2", "scalar", "1e-2", "5052144"), ("kLW2", "layerwise", "1e-2", "5052145"),
             ("k01W3", "scalar", "1e-3", "5052146"), ("kLW3", "layerwise", "1e-3", "5052147"),
             ("k01W4", "scalar", "5e-4", "5052148"), ("kLW4", "layerwise", "5e-4", "5052149"),
             ("CARW2", "scalar", "1e-2", "5052150")]
CWD5 = dict((arm, ("cwd5-%s-s146" % arm, job)) for arm, _g, _w, job in CWD5_ARMS)
CWD5_CAR = CWD5["CARW2"]


def wd5_batch(carw2_by="ARGS_WD_BASE"):
    """cwd5-style (281): 2 anchor arms at the standard 0.1, 6 single-axis rung arms, and the TWO-AXIS CARW2."""
    listed, corpus, logs, args, cells = [], [], {}, {}, {}
    for arm, grouping, wd, _job in CWD5_ARMS:
        key = CWD5[arm]
        corpus.append(key)
        logs[key] = CWD1_OFF + [DM_CARRIERS3_W2 if arm == "CARW2" else "DECAY_MASK: off"]
        args[key] = CWD5_ARGS % (wd, grouping, key[0])
        cells[key] = {"network": "ResNet18_c100", "granularity": grouping}
        if arm == "CARW2":
            listed.append(key + (DM_CARRIERS3_W2 if carw2_by == "DECAY_MASK"
                                 else "ARGS_WD_BASE: weight-decay-base=%s" % wd,))
        elif wd != "0.1":
            listed.append(key + ("ARGS_WD_BASE: weight-decay-base=%s" % wd,))
    return listed, corpus, logs, args, cells


def merge5(wd5, *parts):
    """merge(), for the fixtures that also carry `args` / `cells` (the cwd5 and cmo1 shapes)."""
    listed, corpus, logs, args, cells = wd5
    listed, corpus, logs = list(listed), list(corpus), dict(logs)
    args, cells = dict(args), dict(cells)
    for p in parts:
        listed += list(p[0])
        corpus += list(p[1])
        logs.update(p[2])
        if len(p) > 3:
            args.update(p[3])
            cells.update(p[4])
    return listed, corpus, logs, args, cells


# ---- CORRECTIONS 294: caw2's TWO-ARGS runs (two ARGS kinds deviating on the SAME run) ------------------------
# `caw2` (290) swaps the base optimiser to AdamW on six arms; the harness's AdamW takes `--momentum-param-base 0.9`,
# which is ARGS_MOMENTUM_BASE's non-standard value (the `base` column carries AdamW, but no column carries the flag),
# and the X cell runs that recipe at `--weight-decay-base 1.0` -- so XS / XL deviate on BOTH ARGS kinds.  The payload
# below is the batch's REAL ARGS line (read on alice2 from caw2-XS-s160-5079306.out and its 26 twins, and pinned in
# C39 to `analysis/caw2_design.py`'s registered `args_string`); the run names and job ids are the real seed-160 ones.
CAW2_BASE = {"SGDm": "--alg-base SGDm --momentum-param-base %s --weight-decay-base %s",
             "AdamW": "--alg-base AdamW --normalizer-param-base 0.999 --momentum-param-base %s --weight-decay-base %s"}
CAW2_META = {"Lion": "--alg-meta Lion --momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0",
             "Adam": "--alg-meta Adam --normalizer-param-meta 0.999 --momentum-param-meta 0.9 --weight-decay-meta 0"}
CAW2_COMMON = ("--dataset CIFAR100 --NN-name ResNet18_c100 --batch-size 100 --max-time 999:00:00 --gamma 1 "
               "--meta-stepsize 1e-3 --alpha0 1e-6 --num-epochs 100 --stepsize-groups %s --seed %d "
               "--save-directory /home/s5014158/metaopt/runs/caw2 --run-name %s")
# (arm, base, meta, grain, momentum token, wd token, job id of seed 160)
CAW2_ARMS = [("K01", "SGDm", "Lion", "scalar", "0.99", "0.1", "5079299"),
             ("MS", "SGDm", "Adam", "scalar", "0.99", "0.1", "5079300"),
             ("ML", "SGDm", "Adam", "layerwise", "0.99", "0.1", "5079301"),
             ("LS", "AdamW", "Lion", "scalar", "0.9", "0.1", "5079302"),
             ("LL", "AdamW", "Lion", "layerwise", "0.9", "0.1", "5079303"),
             ("AS", "AdamW", "Adam", "scalar", "0.9", "0.1", "5079304"),
             ("AL", "AdamW", "Adam", "layerwise", "0.9", "0.1", "5079305"),
             ("XS", "AdamW", "Adam", "scalar", "0.9", "1.0", "5079306"),
             ("XL", "AdamW", "Adam", "layerwise", "0.9", "1.0", "5079307")]
CAW2 = dict((r[0], ("caw2-%s-s160" % r[0], r[6])) for r in CAW2_ARMS)
CAW2_OFF = ["VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off", "REST_HOLD: off", "DECAY_MASK: off"]  # 290.8a
W_MOM9 = "ARGS_MOMENTUM_BASE: momentum-param-base=0.9"
W_WD10 = "ARGS_WD_BASE: weight-decay-base=1.0"


def caw2_args(arm, seed=160, mom=None, wd=None):
    """-> the ARGS payload of one caw2 run; `mom` / `wd` override the arm's registered tokens (for corruptions)."""
    r = dict((x[0], x) for x in CAW2_ARMS)[arm]
    return " ".join(["--optimizer HF", CAW2_BASE[r[1]] % (mom or r[4], wd or r[5]), CAW2_META[r[2]],
                     CAW2_COMMON % (r[3], seed, "caw2-%s-s%d" % (arm, seed))])


def caw2_batch(x_by="ARGS_WD_BASE"):
    """caw2-style (290): 3 arms at the standard 0.99 / 0.1, 4 AdamW arms at momentum 0.9 (ONE ARGS kind), and the
    two X arms at momentum 0.9 AND wd 1.0 (TWO ARGS kinds), listed once by `x_by`'s witness."""
    listed, corpus, logs, args, cells = [], [], {}, {}, {}
    for arm, base, meta, grain, mom, wd, _job in CAW2_ARMS:
        key = CAW2[arm]
        corpus.append(key)
        logs[key] = list(CAW2_OFF)
        args[key] = caw2_args(arm)
        cells[key] = {"network": "ResNet18_c100", "granularity": grain, "base": base, "meta": meta}
        if wd != "0.1":
            listed.append(key + ({"ARGS_WD_BASE": W_WD10, "ARGS_MOMENTUM_BASE": W_MOM9}[x_by],))
        elif mom != "0.99":
            listed.append(key + (W_MOM9,))
    return listed, corpus, logs, args, cells


# ---- CORRECTIONS 304: cvl1's VAL_SPLIT (a train-set switch; ONE-kind W1 rows, TWO-AXIS W4 rows) ------------------
# `cvl1` (303) runs cgw1's CIFAR-10 cell with PATCH_VALSPLIT on (VAL_SPLIT=5000:302).  Every run prints ONE `VAL_SPLIT:
# on ...` line and, every epoch, a `VAL: epoch <e> val_acc <x> % n_val 5000` line; the cgw1 tree prints no other kind's
# line.  The run names, the job ids (squeue on alice2, 2026-09-22: W1 5080667-5080682, W4 5080683-5080698, per seed ch /
# nd / k01 / kL) and the ARGS payload are the batch's REAL ones; C44 pins the payloads and the witness to cvl1_design.
VS_ON = ("VAL_SPLIT: on dataset=CIFAR10 n_val=5000 n_train=45000 classes=10 per_class=500 split_seed=302 "
         "val_sha=7d3a1489390161d637ad0b526ac32a10723210722879f8deead4462e4f69bb0e "
         "train_sha=2733a990cf7a76d8e92014cdd6aceeb8c055f7cd49cc7df913923b066c1e5e91")
VS_ON_303 = VS_ON.replace("split_seed=302", "split_seed=303")         # another split: a corrupted witness
VS_ON_4999 = VS_ON.replace("n_val=5000 n_train=45000", "n_val=4999 n_train=45001")
VS_VAL_LINES = ["VAL: epoch 0 val_acc 1.00 % n_val 5000", "VAL: epoch 1 val_acc 2.00 % n_val 5000"]  # synthetic values
CVL1_ARGS = ("--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base %s --alg-meta Lion "
             "--momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0 --dataset CIFAR10 --NN-name ResNet18 "
             "--batch-size 100 --max-time 999:00:00 --gamma 1 --meta-stepsize 1e-4 --alpha0 1e-3 --num-epochs 100 "
             "--stepsize-groups %s --seed %d --save-directory /home/s5014158/metaopt/runs/cvl1 --run-name %s")
CVL1_GRAINS = [("ch", "chunk777"), ("nd", "nodewise"), ("k01", "scalar"), ("kL", "layerwise")]
CVL1_RUNGS = [("W1", "0.1", 5080667), ("W4", "5e-4", 5080683)]
CVL1_SEEDS = (184, 185, 186, 187)
# (arm, grain spec, wd token, seed) -> (run, job id)
CVL1 = dict((("%s%s" % (g, r), s), ("cvl1-%s%s-s%d" % (g, r, s), str(j0 + 4 * (s - 184) + gi)))
            for r, _w, j0 in CVL1_RUNGS for s in CVL1_SEEDS for gi, (g, _spec) in enumerate(CVL1_GRAINS))
CVL1_SPEC = dict(("%s%s" % (g, r), spec) for r, _w, _j in CVL1_RUNGS for g, spec in CVL1_GRAINS)
CVL1_WD = dict(("%s%s" % (g, r), w) for r, w, _j in CVL1_RUNGS for g, _spec in CVL1_GRAINS)
W_WD5E4 = "ARGS_WD_BASE: weight-decay-base=5e-4"


def cvl1_args(arm, seed, wd=None):
    return CVL1_ARGS % (wd or CVL1_WD[arm], CVL1_SPEC[arm], seed, CVL1[(arm, seed)][0])


def cvl1_batch(w4_by="ARGS_WD_BASE"):
    """cvl1-style (303): 16 W1 runs listed by their VAL_SPLIT line, 16 TWO-AXIS W4 runs listed by `w4_by`."""
    listed, corpus, logs, args, cells = [], [], {}, {}, {}
    for (arm, seed), key in sorted(CVL1.items()):
        corpus.append(key)
        logs[key] = [VS_ON] + VS_VAL_LINES
        args[key] = cvl1_args(arm, seed)
        cells[key] = {"network": "ResNet18", "dataset": "CIFAR10", "granularity": CVL1_SPEC[arm],
                      "meta_stepsize": "1e-4", "alpha0": "1e-3"}
        if CVL1_WD[arm] != "0.1":
            listed.append(key + ({"ARGS_WD_BASE": W_WD5E4, "VAL_SPLIT": VS_ON}[w4_by],))
        else:
            listed.append(key + (VS_ON,))
    return listed, corpus, logs, args, cells


# ---- CORRECTIONS 304: csh1's gamma arms (301) -- a CSV column, so NO ARGS kind; ARGS_WD_BASE rows only -------------
# The payload is csh1_design.args_string (C45 pins it); job ids are the real seed-180 ones (squeue on alice2).
CSH1_ARMS = [("G1S", "scalar", "1", "5080645"), ("G1L", "layerwise", "1", "5080646"),
             ("GMS", "scalar", "0.999685", "5080647"), ("GML", "layerwise", "0.999685", "5080648"),
             ("GPS", "scalar", "0.99941", "5080649"), ("GPL", "layerwise", "0.99941", "5080650")]
CSH1_ARGS = ("--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base 5e-4 --alg-meta Lion "
             "--momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0 --dataset CIFAR100 "
             "--NN-name ResNet18_c100 --batch-size 100 --max-time 999:00:00 --gamma %s --meta-stepsize 1e-3 "
             "--alpha0 1e-6 --num-epochs 100 --stepsize-groups %s --seed 180 "
             "--save-directory /home/s5014158/metaopt/runs/csh1 --run-name csh1-%s-s180")
CSH1_OFF = ["VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off", "REST_HOLD: off", "DECAY_MASK: off"]  # csh1_design.OFF_LINES


def csh1_batch():
    listed, corpus, logs, args, cells = [], [], {}, {}, {}
    for arm, grain, g, job in CSH1_ARMS:
        key = ("csh1-%s-s180" % arm, job)
        corpus.append(key)
        logs[key] = list(CSH1_OFF)
        args[key] = CSH1_ARGS % (g, grain, arm)
        cells[key] = {"network": "ResNet18_c100", "granularity": grain, "gamma": g}
        listed.append(key + (W_WD5E4,))
    return listed, corpus, logs, args, cells


# ---- CORRECTIONS 308: PATCH_DECAYROUTE's cai1 (306, all TWO-AXIS) and crd1 (307, one-kind SR* / TR*, two-axis AI*) ------
# The witness lines are the harness's own format (patches/patch_decayroute.py `_dr_init`), re-typed; C49 pins them to
# cai1_design.witness_on / crd1_design.dr_witness and to the real proof log's RR2 lines.  The cdr1 tree is the live HF.py
# + PATCH_DECAYROUTE only, so it prints NO other kind's line (crd1_design.NO_LINE_KINDS); crd1 also prints a PROBE_TENSOR
# line, which is no kind.  Job ids: squeue on alice2, 2026-09-22 (cai1 in the launcher's order: rung, seed, grain).
DR_OFF = "DECAY_ROUTE: off"
DR_I5 = ("DECAY_ROUTE: on mode=alpha_indep base=SGDm wd=0.0 lambda=5e-05 lambda_f32=4.999999873689376e-05 "
         "gamma=1.0")
DR_I4 = ("DECAY_ROUTE: on mode=alpha_indep base=SGDm wd=0.0 lambda=0.0005 lambda_f32=0.0005000000237487257 "
         "gamma=1.0")
DR_SR = "DECAY_ROUTE: on mode=shrink_only base=SGDm wd=0.1 lambda=na lambda_f32=na gamma=1.0"
DR_TR = "DECAY_ROUTE: on mode=trace_only base=SGDm wd=0.1 lambda=na lambda_f32=na gamma=1.0"
DR_AI = ("DECAY_ROUTE: on mode=alpha_indep base=SGDm wd=0.0 lambda=0.000315 lambda_f32=0.0003150000120513141 "
         "gamma=1.0")
W_WD0 = "ARGS_WD_BASE: weight-decay-base=0"
CAI1_ARGS = ("--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base %s --alg-meta Lion "
             "--momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0 --dataset CIFAR10 --NN-name ResNet18 "
             "--batch-size 100 --max-time 999:00:00 --gamma 1 --meta-stepsize 1e-4 --alpha0 1e-3 --num-epochs 100 "
             "--stepsize-groups %s --seed %d --save-directory /home/s5014158/metaopt/runs/cai1 --run-name %s")
CAI1_GRAINS = [("ch", "chunk777"), ("nd", "nodewise"), ("k01", "scalar"), ("kL", "layerwise")]
CAI1_RUNGS = [("I5", DR_I5, 5081292), ("I4", DR_I4, 5081308)]
CAI1_SEEDS = (192, 193, 194, 195)
CAI1 = dict((("%s%s" % (g, r), s), ("cai1-%s%s-s%d" % (g, r, s), str(j0 + 4 * (s - 192) + gi)))
            for r, _w, j0 in CAI1_RUNGS for s in CAI1_SEEDS for gi, (g, _spec) in enumerate(CAI1_GRAINS))
CAI1_SPEC = dict(("%s%s" % (g, r), spec) for r, _w, _j in CAI1_RUNGS for g, spec in CAI1_GRAINS)
CAI1_DR = dict(("%s%s" % (g, r), w) for r, w, _j in CAI1_RUNGS for g, _spec in CAI1_GRAINS)
CRD1_ARGS = ("--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base %s --alg-meta Lion "
             "--momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0 --dataset CIFAR100 "
             "--NN-name ResNet18_c100 --batch-size 100 --max-time 999:00:00 --gamma 1 --meta-stepsize 1e-3 "
             "--alpha0 1e-6 --num-epochs 100 --stepsize-groups %s --seed %d "
             "--save-directory /home/s5014158/metaopt/runs/crd1 --run-name %s")
# (arm, grain, wd token, witness), in the launcher's order; job = 5081273 + 6 * (seed - 196) + index
CRD1_ARMS = [("SRS", "scalar", "0.1", DR_SR), ("SRL", "layerwise", "0.1", DR_SR),
             ("TRS", "scalar", "0.1", DR_TR), ("TRL", "layerwise", "0.1", DR_TR),
             ("AIS", "scalar", "0", DR_AI), ("AIL", "layerwise", "0", DR_AI)]
CRD1_SEEDS = (196, 197, 198)
CRD1 = dict(((a, s), ("crd1-%s-s%d" % (a, s), str(5081273 + 6 * (s - 196) + i)))
            for s in CRD1_SEEDS for i, (a, _g, _w, _dr) in enumerate(CRD1_ARMS))
CRD1_SPEC = dict((a, g) for a, g, _w, _dr in CRD1_ARMS)
CRD1_WD = dict((a, w) for a, _g, w, _dr in CRD1_ARMS)
CRD1_DR = dict((a, dr) for a, _g, _w, dr in CRD1_ARMS)
CRD1_PT = "PROBE_TENSOR: on every=100 type=%s tensors=62 meta_alg=Lion momentum_param=0.99 Lion_beta2=0.9"


def cai1_args(arm, seed, wd=None):
    return CAI1_ARGS % (wd or "0", CAI1_SPEC[arm], seed, CAI1[(arm, seed)][0])


def crd1_args(arm, seed, wd=None):
    return CRD1_ARGS % (wd or CRD1_WD[arm], CRD1_SPEC[arm], seed, CRD1[(arm, seed)][0])


def cai1_batch(by="ARGS_WD_BASE"):
    """cai1-style (306): 32 TWO-AXIS runs (DECAY_ROUTE on AND wd 0), listed by `by`'s witness."""
    listed, corpus, logs, args, cells = [], [], {}, {}, {}
    for (arm, seed), key in sorted(CAI1.items()):
        corpus.append(key)
        logs[key] = [CAI1_DR[arm]]
        args[key] = cai1_args(arm, seed)
        cells[key] = {"network": "ResNet18", "dataset": "CIFAR10", "granularity": CAI1_SPEC[arm],
                      "meta_stepsize": "1e-4", "alpha0": "1e-3"}
        listed.append(key + ({"ARGS_WD_BASE": W_WD0, "DECAY_ROUTE": CAI1_DR[arm]}[by],))
    return listed, corpus, logs, args, cells


def crd1_batch(ai_by="ARGS_WD_BASE"):
    """crd1-style (307): 12 one-kind SR* / TR* runs listed by their DECAY_ROUTE line, 6 TWO-AXIS AI* runs by `ai_by`."""
    listed, corpus, logs, args, cells = [], [], {}, {}, {}
    for (arm, seed), key in sorted(CRD1.items()):
        corpus.append(key)
        logs[key] = [CRD1_DR[arm], CRD1_PT % CRD1_SPEC[arm]]
        args[key] = crd1_args(arm, seed)
        cells[key] = {"network": "ResNet18_c100", "granularity": CRD1_SPEC[arm]}
        if CRD1_WD[arm] != "0.1":
            listed.append(key + ({"ARGS_WD_BASE": W_WD0, "DECAY_ROUTE": CRD1_DR[arm]}[ai_by],))
        else:
            listed.append(key + (CRD1_DR[arm],))
    return listed, corpus, logs, args, cells


def line_of(out, head):
    return [ln for ln in out.splitlines() if ln.startswith(head)]


def merge(*parts):
    listed, corpus, logs = [], [], {}
    for l, c, g in parts:
        listed += l
        corpus += c
        logs.update(g)
    return listed, corpus, logs


def main():
    print("C1  a BETA_HOLD-witnessed row passes")
    rc, out = run_check(*bh_batch())
    chk(rc == 0 and "VERDICT: PASS" in out, "C1 listed BETA_HOLD run + unlisted `BETA_HOLD: off` run -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))

    print("C2  a mismatched BETA_HOLD witness fails")
    listed, corpus, logs = bh_batch()
    logs[HOLD] = ["VOTE_W: off", BH_TRI_5041]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and "VERDICT: FAIL" in out, "C2 the log prints P=5041, the list says P=9428 -> exit 1 FAIL", "rc=%d" % rc)
    chk(any("syn9-HOLDHIGH-s90-5000002.out" in f and "P=5041" in f for f in fails(out)),
        "C2 the FAIL line names the run and quotes its own BETA_HOLD line", show(out))

    print("C3  a VOTE_W row still passes as before")
    rc, out = run_check(*vw_batch())
    chk(rc == 0 and "VERDICT: PASS" in out, "C3 listed VOTE_W run + unlisted `VOTE_W: off` run -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    want = "  raw .out witness: 1 listed runs carry their listed line; 1 unlisted runs of the same batch print `VOTE_W: off`"
    chk(want in out.splitlines(), "C3 the witness summary line is the pre-239 line, byte for byte")
    listed, corpus, logs = vw_batch()
    logs[VMUTE] = ["VOTE_W: off"]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and "FAIL syn8-MUTE-s78-5000012.out witness ['VOTE_W: off'] != listed" in fails(out),
        "C3 a VOTE_W mismatch still fails with the pre-239 message", show(out))

    print("C4  an ON corpus run absent from the TSV fails")
    listed, corpus, logs = vw_batch()
    corpus += [HOLD]
    logs[HOLD] = ["VOTE_W: off", BH_TRI]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and any("syn9-HOLDHIGH-s90-5000002.out" in f and "BETA_HOLD" in f for f in fails(out)),
        "C4a BETA_HOLD run of a batch with NO listed row -> exit 1, named", "rc=%d %s" % (rc, show(out)))
    listed, corpus, logs = bh_batch()
    corpus += [HOLDLOW]
    logs[HOLDLOW] = ["VOTE_W: off", BH_FLOOR]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and any("syn9-HOLDLOW-s90-5000003.out" in f for f in fails(out)),
        "C4b one held run left out of a listed BETA_HOLD batch (it prints `VOTE_W: off`) -> exit 1, named",
        "rc=%d %s" % (rc, show(out)))
    listed, corpus, logs = bh_batch()
    corpus += [VK01, VMUTE]
    logs.update({VK01: ["VOTE_W: off"], VMUTE: [VW_MUTE]})
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and any("syn8-MUTE-s78-5000012.out" in f and "VOTE_W" in f for f in fails(out)),
        "C4c VOTE_W run of an unlisted batch -> exit 1, named", "rc=%d %s" % (rc, show(out)))

    print("C5  `off` runs are not required")
    extra = ([], [("cvt7-k01-s1", "5000021"), ("cvt7-HEAD-s1", "5000022"), ("c50-k01-s1", "5000023")],
             {("cvt7-k01-s1", "5000021"): ["VOTE_W: off", "BETA_HOLD: off"],
              ("cvt7-HEAD-s1", "5000022"): ["VOTE_W: off"],
              ("c50-k01-s1", "5000023"): []})
    rc, out = run_check(*merge(vw_batch(), bh_batch(), extra))
    chk(rc == 0 and "VERDICT: PASS" in out, "C5 unlisted off / witness-less corpus runs -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))

    print("C6  an ON run not yet in the corpus is not required")
    listed, corpus, logs = merge(vw_batch(), bh_batch())
    logs[("cvt6-K13-s93", "5000031")] = ["VOTE_W: on type=blockwise items=47:layer4.1.bn1.weight:w=13.0:group=0:groupsize=52"]
    logs[("cvt6-HOLDLOW-s93", "5000032")] = ["VOTE_W: off", BH_FLOOR]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 0 and "VERDICT: PASS" in out, "C6 ON runs with no CSV row (not ingested) -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    chk(any(ln.startswith("  completeness") and "2 not in the CSV" in ln for ln in out.splitlines()),
        "C6 the completeness line reports the 2 not-ingested ON runs",
        repr([ln for ln in out.splitlines() if "completeness" in ln]))

    print("C7  a listed run with an ON line of another kind fails")
    listed, corpus, logs = bh_batch()
    logs[HOLD] = [VW_MUTE, BH_TRI]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and any("syn9-HOLDHIGH-s90-5000002.out" in f and "VOTE_W" in f for f in fails(out)),
        "C7 listed with its BETA_HOLD witness but also prints VOTE_W on -> exit 1, named", show(out))

    print("C8  a witness naming no registered kind fails")
    listed, corpus, logs = bh_batch()
    listed = [HOLD + ("GAMMA_X: on synthetic",)]
    logs[HOLD] = ["VOTE_W: off", "BETA_HOLD: off", "GAMMA_X: on synthetic"]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and any("GAMMA_X" in f for f in fails(out)), "C8 unregistered kind -> exit 1, named", show(out))

    print("C9  without --runs no log is read (existing behaviour)")
    listed, corpus, logs = bh_batch()
    logs[HOLD] = ["VOTE_W: off", BH_TRI_5041]
    rc, out = run_check(listed, corpus, logs, with_runs=False)
    chk(rc == 0 and "VERDICT: PASS" in out and "raw .out witness" not in out and "completeness" not in out,
        "C9 no --runs -> exit 0, no witness or completeness line", "rc=%d %s" % (rc, show(out)))

    # ---- CORRECTIONS 245 ------------------------------------------------------------------------------------
    print("C10 a GROUP_HOLD-witnessed row passes")
    rc, out = run_check(*gh_batch())
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C10 listed GROUP_HOLD run + unlisted `GROUP_HOLD: off` runs (cvt7-style) -> exit 0 PASS", "rc=%d %s" % (rc, show(out)))
    chk(any(ln.startswith("  raw .out witness: 1 listed runs carry their listed line; 2 unlisted runs")
            and ln.endswith("print `GROUP_HOLD: off`") for ln in out.splitlines()),
        "C10 the witness line names the off line the unlisted runs print", repr([l for l in out.splitlines() if "raw" in l]))

    print("C11 a mismatched GROUP_HOLD witness fails")
    listed, corpus, logs = gh_batch()
    logs[G_HIGH] = ["VOTE_W: off", "BETA_HOLD: off", GH_TRI_ISO]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and "VERDICT: FAIL" in out, "C11 the log prints P=5153, the list says P=8609 -> exit 1 FAIL", "rc=%d" % rc)
    chk(any("cvt7-HOLDHIGH-s99-5000043.out" in f and "P=5153" in f for f in fails(out)),
        "C11 the FAIL line names the run and quotes its own GROUP_HOLD line", show(out))

    print("C12 two-kind runs (BETA_HOLD + COMP_HOLD ON) listed ONCE pass")
    rc, out = run_check(*ch_batch("BETA_HOLD"))
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C12 HOLDLOW + the three forced arms listed by their BETA_HOLD line (242.7's plan) -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    chk(any(ln.startswith("  two-kind runs") and " 3 listed runs " in ln and ln.endswith(": True")
            for ln in out.splitlines()),
        "C12 the two-kind line counts the 3 forced runs, verified", repr([l for l in out.splitlines() if "two-kind" in l]))
    chk(any(ln.startswith("  raw .out witness: 4 listed runs carry their listed line; 1 unlisted runs")
            and ln.endswith("print `BETA_HOLD: off` / `COMP_HOLD: off`") for ln in out.splitlines()),
        "C12 the unlisted cvt6 run is held to both off lines", repr([l for l in out.splitlines() if "raw" in l]))
    rc, out = run_check(*ch_batch("COMP_HOLD"))
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C12 the forced arms listed by their COMP_HOLD line instead -> exit 0 PASS", "rc=%d %s" % (rc, show(out)))

    print("C13 a two-kind run whose OTHER ON line is wrong fails")
    for tag, key, lines, by, want in [
            ("a", C_HHP, ["VOTE_W: off", BH_TRI, CH_REC_OTHER_SHA], "BETA_HOLD", "COMP_HOLD"),
            ("b", C_LMP, ["VOTE_W: off", BH_FLOOR, CH_REC], "BETA_HOLD", "COMP_HOLD"),
            ("c", C_LHP, ["VOTE_W: off", BH_FLOOR, "COMP_HOLD: off"], "BETA_HOLD", "COMP_HOLD"),
            ("d", C_LOW, ["VOTE_W: off", BH_FLOOR, CH_TRI], "BETA_HOLD", "COMP_HOLD"),
            ("e", C_LHP, ["VOTE_W: off", BH_TRI, CH_REC], "COMP_HOLD", "BETA_HOLD")]:
        listed, corpus, logs = ch_batch(by)
        logs[key] = lines
        rc, out = run_check(listed, corpus, logs)
        name = "%s-%s.out" % key
        chk(rc == 1 and any(name in f and want in f for f in fails(out)),
            "C13%s %s prints a wrong %s line (listed by %s) -> exit 1, named" % (tag, key[0], want, by), show(out))

    print("C14 an ON GROUP_HOLD corpus run absent from the TSV fails")
    listed, corpus, logs = gh_batch()
    rc, out = run_check([], corpus, logs)
    chk(rc == 1 and any("cvt7-HOLDHIGH-s99-5000043.out" in f and "GROUP_HOLD" in f for f in fails(out)),
        "C14a GROUP_HOLD run of a batch with NO listed row -> exit 1, named", "rc=%d %s" % (rc, show(out)))
    listed, corpus, logs = gh_batch()
    corpus += [G_LOW]
    logs[G_LOW] = ["VOTE_W: off", "BETA_HOLD: off", GH_FLOOR]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and any("cvt7-HOLDLOW-s99-5000044.out" in f for f in fails(out)),
        "C14b one held run left out of a listed GROUP_HOLD batch -> exit 1, named", "rc=%d %s" % (rc, show(out)))

    print("C15 `off` runs of the new kinds are not required")
    extra = ([], [("cvt7-k01-s100", "5000061"), ("cvt6-HEAD-s97", "5000062")],
             {("cvt7-k01-s100", "5000061"): ["VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off"],
              ("cvt6-HEAD-s97", "5000062"): ["VOTE_W: off", "BETA_HOLD: off", "COMP_HOLD: off"]})
    rc, out = run_check(*merge(gh_batch(), ch_batch(), extra))
    chk(rc == 0 and "VERDICT: PASS" in out, "C15 unlisted GROUP_HOLD / COMP_HOLD off runs -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    listed, corpus, logs = ch_batch()
    logs[C_K01] = ["VOTE_W: off", "BETA_HOLD: off"]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and "FAIL cvt6-k01-s96-5000051.out is NOT listed but its witness is []" in fails(out),
        "C15 an unlisted run of a two-kind batch with no `COMP_HOLD: off` line -> exit 1, named", show(out))

    print("C16 prefix collisions, the patches' line forms, and MULTI_KIND against the registered scorer")
    import re
    sys.path.insert(0, os.path.join(REPO, "analysis"))
    import corpus_exclusions as CE
    kinds = [k for k, _off in CE.KINDS]
    # CORRECTIONS 251: was `... in CE.KINDS and len(CE.KINDS) == 4`; now the first four entries, in order (C23 checks the rest)
    chk(CE.KINDS[:4] == [("VOTE_W", "VOTE_W: off"), ("BETA_HOLD", "BETA_HOLD: off"), ("GROUP_HOLD", "GROUP_HOLD: off"),
                         ("COMP_HOLD", "COMP_HOLD: off")],
        "C16 KINDS starts with 239's two entries unchanged + GROUP_HOLD + COMP_HOLD", repr(CE.KINDS))
    chk(all(not a.startswith(b) for a in kinds for b in kinds if a != b),
        "C16 no KINDS prefix is a prefix of another (so no line starts with two of them)", repr(kinds))
    patches = {"VOTE_W": "patch_voteweight.py", "BETA_HOLD": "patch_betahold.py", "GROUP_HOLD": "patch_grouphold.py",
               "COMP_HOLD": "patch_comphold.py"}
    for k, fn in sorted(patches.items()):
        src = open(os.path.join(REPO, "patches", fn)).read()
        lits = re.findall(r"'((?:%s): [^']*)'" % "|".join(sorted(patches)), src)
        chk(("%s: off" % k) in lits and any(l.startswith("%s: on type=" % k) for l in lits)
            and all(l.startswith(k + ": ") for l in lits),
            "C16 %s prints only `%s: off` / `%s: on type=...` lines" % (fn, k, k), repr(sorted(set(lits))))
    tmp = tempfile.mkdtemp(prefix="ce_prefix_test_")
    try:
        p = os.path.join(tmp, "x.out")
        four = [VW_MUTE, BH_TRI, GH_TRI, CH_REC, "VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off", "COMP_HOLD: off"]
        open(p, "w").write("\n".join(four) + "\n")
        got = CE.witness_lines(p)
        chk(all(got[k] == [ln for ln in four if ln.split(":")[0] == k] for k in kinds),
            "C16 witness_lines (the startswith reader) puts each of 8 lines under its own kind only", repr(got)[:300])
    finally:
        shutil.rmtree(tmp)
    try:
        import cVT6_complementpath_score as S6
        mk = getattr(CE, "MULTI_KIND", None)
        want = dict((("cvt6", a), {"BETA_HOLD": S6.WITNESS_BH[a], "COMP_HOLD": S6.WITNESS_CH[a]}) for a in S6.FORCED)
        # CORRECTIONS 251: was `mk == want`; MULTI_KIND now also holds cvt8 / cvt9 entries (C23)
        mk6 = dict((k, v) for k, v in (mk or {}).items() if k[0] == "cvt6")
        chk(mk6 == want, "C16 MULTI_KIND's cvt6 entries == cvt6's FORCED arms x the registered scorer's WITNESS_BH / WITNESS_CH",
            repr(mk6)[:200])
        chk((S6.WITNESS_CH["HIGHHEADPATH"], S6.WITNESS_CH["LOWMUTEPATH"], S6.WITNESS_BH["HIGHHEADPATH"],
             S6.WITNESS_BH["LOWHEADPATH"]) == (CH_REC, CH_TRI, BH_TRI, BH_FLOOR),
            "C16 this test's cvt6 fixtures are the registered scorer's lines")
        import cVT7_grouphold_score as S7
        chk((S7.WITNESS_GH["HOLDHIGH"], S7.WITNESS_GH["HOLDISO"], S7.WITNESS_GH["HOLDLOW"]) == (GH_TRI, GH_TRI_ISO, GH_FLOOR),
            "C16 this test's cvt7 fixtures are the registered scorer's lines")
    except Exception as ex:  # a scorer that does not import is a FAIL here, not an error
        chk(False, "C16 the registered cvt6 / cvt7 scorers import", "%s: %s" % (type(ex).__name__, ex))

    # ---- CORRECTIONS 251 ------------------------------------------------------------------------------------
    print("C17 cvt8-style REST_HOLD two-kind runs listed ONCE pass")
    rc, out = run_check(*rh_batch("GROUP_HOLD"))
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C17 HOLDHIGH / HOLDBIG + the three forced arms listed by their GROUP_HOLD line (248.7's plan) -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    chk(any(" 3 listed runs " in ln and ln.endswith(": True") for ln in line_of(out, "  two-kind runs")),
        "C17 the multi-kind check counts the 3 forced runs, verified", repr(line_of(out, "  two-kind runs")))
    chk(line_of(out, "  multi-kind runs") and line_of(out, "  multi-kind runs")[0].endswith(": 2 kinds 3, 3 kinds 0"),
        "C17 the new breakdown line: 3 runs registered with 2 kinds", repr(line_of(out, "  multi-kind runs")))
    chk(any(ln.startswith("  raw .out witness: 5 listed runs carry their listed line; 2 unlisted runs")
            and ln.endswith("print `GROUP_HOLD: off` / `REST_HOLD: off`") for ln in out.splitlines()),
        "C17 the unlisted k01 / ISO runs are held to both off lines", repr(line_of(out, "  raw")))
    rc, out = run_check(*rh_batch("REST_HOLD"))
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C17 the forced arms listed by their REST_HOLD line instead -> exit 0 PASS", "rc=%d %s" % (rc, show(out)))

    # each case names the message it must FAIL with: the MULTI_KIND check ("is registered with <KIND> ON but prints"), or
    # for an arm registered with one ON kind, completeness ("prints an ON <KIND> line but is listed with a")
    reg, other = "%s is registered with %s ON but prints", "%s prints an ON %s line but is listed with a"
    print("C18 a wrong REST_HOLD line fails")
    for tag, key, lines, by, want, msg in [
            ("a", R_HIP, ["VOTE_W: off", "BETA_HOLD: off", GH_TRI, RH_REC_OTHER_SHA], "GROUP_HOLD", "REST_HOLD", reg),
            ("b", R_BIP, ["VOTE_W: off", "BETA_HOLD: off", GH_TRI_BIG, "REST_HOLD: off"], "GROUP_HOLD", "REST_HOLD", reg),
            ("c", R_LIP, ["VOTE_W: off", "BETA_HOLD: off", GH_FLOOR], "GROUP_HOLD", "REST_HOLD", reg),
            ("d", R_HH, ["VOTE_W: off", "BETA_HOLD: off", GH_TRI, RH_REC], "GROUP_HOLD", "REST_HOLD", other),
            ("e", R_LIP, ["VOTE_W: off", "BETA_HOLD: off", GH_TRI, RH_REC], "REST_HOLD", "GROUP_HOLD", reg)]:
        listed, corpus, logs = rh_batch(by)
        logs[key] = lines
        rc, out = run_check(listed, corpus, logs)
        name = "%s-%s.out" % key
        chk(rc == 1 and any((msg % (name, want)) in f for f in fails(out)),
            "C18%s %s prints a wrong %s line (listed by %s) -> exit 1, named" % (tag, key[0], want, by), show(out))

    print("C19 cvt9-style runs (two kinds; EARLY / LATE three kinds) listed ONCE pass")
    rc, out = run_check(*wh_batch("BETA_HOLD"))
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C19 the six held arms listed by their BETA_HOLD line (249.7's plan) -> exit 0 PASS", "rc=%d %s" % (rc, show(out)))
    chk(any(" 6 listed runs " in ln and ln.endswith(": True") for ln in line_of(out, "  two-kind runs")),
        "C19 the multi-kind check counts the 6 held runs, verified", repr(line_of(out, "  two-kind runs")))
    chk(line_of(out, "  multi-kind runs") and line_of(out, "  multi-kind runs")[0].endswith(": 2 kinds 4, 3 kinds 2"),
        "C19 the new breakdown line: 4 runs with 2 kinds, EARLY / LATE with 3", repr(line_of(out, "  multi-kind runs")))
    chk(any(ln.startswith("  raw .out witness: 6 listed runs carry their listed line; 1 unlisted runs")
            and ln.endswith("print `BETA_HOLD: off` / `COMP_HOLD: off` / `WINDOW_HOLD: off`") for ln in out.splitlines()),
        "C19 the unlisted k01 run is held to all three off lines", repr(line_of(out, "  raw")))
    for by in ("WINDOW_HOLD", "COMP_HOLD"):
        rc, out = run_check(*wh_batch(by))
        chk(rc == 0 and "VERDICT: PASS" in out,
            "C19 EARLY / LATE listed by their %s line instead -> exit 0 PASS" % by, "rc=%d %s" % (rc, show(out)))

    print("C20 a wrong or missing WINDOW_HOLD line fails")
    for tag, key, lines, by, want, msg in [
            ("a", W_EARLY, ["VOTE_W: off", BH_TRI, CH_REC, WH_LATE], "BETA_HOLD", "WINDOW_HOLD", reg),
            ("b", W_LATE, ["VOTE_W: off", BH_TRI, CH_REC, "WINDOW_HOLD: off"], "BETA_HOLD", "WINDOW_HOLD", reg),
            ("c", W_EARLY, ["VOTE_W: off", BH_TRI, CH_REC], "BETA_HOLD", "WINDOW_HOLD", reg),
            ("d", W_MID, ["VOTE_W: off", BH_TRI_7235, CH_REC, WH_EARLY], "BETA_HOLD", "WINDOW_HOLD", other),
            ("e", W_EARLY, ["VOTE_W: off", BH_TRI, CH_REC_OTHER_SHA, WH_EARLY], "WINDOW_HOLD", "COMP_HOLD", reg)]:
        listed, corpus, logs = wh_batch(by)
        logs[key] = lines
        rc, out = run_check(listed, corpus, logs)
        name = "%s-%s.out" % key
        chk(rc == 1 and any((msg % (name, want)) in f for f in fails(out)),
            "C20%s %s prints a wrong %s line (listed by %s) -> exit 1, named" % (tag, key[0], want, by), show(out))

    print("C21 an unlisted ON corpus run of each new kind fails completeness")
    for tag, batch, drop, key, want in [("a", rh_batch, "all", R_HIP, "REST_HOLD"), ("b", rh_batch, R_BIP, R_BIP, "REST_HOLD"),
                                        ("c", wh_batch, "all", W_EARLY, "WINDOW_HOLD"), ("d", wh_batch, W_LATE, W_LATE, "WINDOW_HOLD")]:
        listed, corpus, logs = batch()
        listed = [] if drop == "all" else [r for r in listed if r[:2] != drop]
        rc, out = run_check(listed, corpus, logs)
        name = "%s-%s.out" % key
        chk(rc == 1 and any(name in f and "ON %s line but is NOT listed" % want in f for f in fails(out)),
            "C21%s %s %s -> exit 1, named with %s" % (tag, key[0], "in a batch with NO listed row" if drop == "all"
                                                     else "left out of its listed batch", want), show(out))
    for tag, key, on, want in [("e", ("syn7-RH-s1", "5000091"), RH_REC, "REST_HOLD"),
                               ("f", ("syn7-WH-s1", "5000092"), WH_EARLY, "WINDOW_HOLD")]:
        others = ["VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off", "COMP_HOLD: off", "REST_HOLD: off", "WINDOW_HOLD: off"]
        logs = {key: [on if ln.startswith(want) else ln for ln in others]}
        rc, out = run_check([], [key], logs)
        chk(rc == 1 and any("%s-%s.out" % key in f and "ON %s line but is NOT listed" % want in f for f in fails(out)),
            "C21%s a corpus run whose ONLY ON line is %s, unlisted -> exit 1, named" % (tag, want), show(out))

    print("C22 `off` lines of the new kinds are not required")
    extra = ([], [("syn7-k01-s2", "5000093"), ("syn7-k01-s3", "5000094")],
             {("syn7-k01-s2", "5000093"): ["VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off", "REST_HOLD: off"],
              ("syn7-k01-s3", "5000094"): ["VOTE_W: off", "BETA_HOLD: off", "COMP_HOLD: off", "WINDOW_HOLD: off"]})
    rc, out = run_check(*merge(rh_batch(), wh_batch(), extra))
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C22 unlisted REST_HOLD / WINDOW_HOLD off runs (in listed cvt8 / cvt9 batches and in an unlisted batch) -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    for tag, batch, key, lines in [("R", rh_batch, R_ISO, ["VOTE_W: off", "BETA_HOLD: off", "GROUP_HOLD: off"]),
                                   ("W", wh_batch, W_K01, ["VOTE_W: off", "BETA_HOLD: off", "COMP_HOLD: off"])]:
        listed, corpus, logs = batch()
        logs[key] = lines
        rc, out = run_check(listed, corpus, logs)
        chk(rc == 1 and ("FAIL %s-%s.out is NOT listed but its witness is []" % key) in fails(out),
            "C22 an unlisted run of a listed %s batch with no `%s: off` line -> exit 1, named"
            % (key[0].split("-")[0], "REST_HOLD" if tag == "R" else "WINDOW_HOLD"), show(out))

    print("C23 the new KINDS, the prefix proof, the patches' line forms, and MULTI_KIND against the cvt8 / cvt9 scorers")
    # CORRECTIONS 269: was `CE.KINDS[4:] == [...] and len(CE.KINDS) == 6`; KINDS now also holds DECAY_MASK and
    # SHADOW_VOTE (C33 owns the total and the two added entries).  251's claim is unchanged over entries 5 and 6.
    chk(CE.KINDS[4:6] == [("REST_HOLD", "REST_HOLD: off"), ("WINDOW_HOLD", "WINDOW_HOLD: off")],
        "C23 KINDS = 245's four + REST_HOLD + WINDOW_HOLD, appended", repr(CE.KINDS[:6]))
    kinds = [k for k, _off in CE.KINDS[:6]]   # CORRECTIONS 269: 251's six, not every kind
    chk(len(kinds) == 6 and len(set(k[0] for k in kinds)) == len(kinds)
        and all(not a.startswith(b) for a in kinds for b in kinds if a != b),
        "C23 the six first letters differ (%s), so no prefix is a prefix of another" % " ".join(k[0] for k in kinds))
    SIX = ["VOTE_W", "BETA_HOLD", "GROUP_HOLD", "COMP_HOLD", "REST_HOLD", "WINDOW_HOLD"]  # literal, not read from the module
    six = "|".join(sorted(SIX))
    for k, fn in (("REST_HOLD", "patch_resthold.py"), ("WINDOW_HOLD", "patch_windowhold.py")):
        src = open(os.path.join(REPO, "patches", fn)).read()
        lits = re.findall(r"'((?:%s): [^']*)'" % six, src)
        chk(("%s: off" % k) in lits and any(l.startswith("%s: on type=" % k) for l in lits)
            and all(l.startswith(k + ": ") for l in lits),
            "C23 %s prints only `%s: off` / `%s: on type=...` lines" % (fn, k, k), repr(sorted(set(lits))))
    tmp = tempfile.mkdtemp(prefix="ce_prefix_test_")
    try:
        p = os.path.join(tmp, "x.out")
        twelve = [VW_MUTE, BH_TRI, GH_TRI, CH_REC, RH_REC, WH_EARLY] + ["%s: off" % k for k in SIX]
        open(p, "w").write("\n".join(twelve) + "\n")
        got = CE.witness_lines(p)
        # CORRECTIONS 269: was `sorted(got) == sorted(SIX)`; witness_lines now also returns the two added kinds' keys,
        # empty on these twelve lines -- so the kinds that COLLECT a line are still exactly 251's six.
        chk(sorted(k for k in got if got[k]) == sorted(SIX)
            and all(got[k] == [ln for ln in twelve if ln.split(":")[0] == k] for k in SIX),
            "C23 witness_lines puts each of 12 lines (one on, one off per kind) under its own kind only", repr(got)[:300])
    finally:
        shutil.rmtree(tmp)
    rc, out = run_check(*merge(rh_batch(), wh_batch()))
    chk(("  kinds scanned (CORRECTIONS 245): VOTE_W / BETA_HOLD / GROUP_HOLD / COMP_HOLD; no prefix is a prefix of another, "
         "so no line is read as two kinds: True") in out.splitlines(),
        "C23 245's `kinds scanned` line is unchanged, byte for byte", repr(line_of(out, "  kinds scanned")))
    chk(any("REST_HOLD / WINDOW_HOLD" in ln and ln.endswith(": True") for ln in line_of(out, "  kinds scanned (CORRECTIONS 251)")),
        "C23 a new line names the two added kinds, no prefix collision", repr(line_of(out, "  kinds scanned")))
    try:
        mk = getattr(CE, "MULTI_KIND", None) or {}
        import cVT8_doseroute_score as S8
        import cVT9_dosewindow_score as S9
        want8 = dict((("cvt8", a), {"GROUP_HOLD": S8.WITNESS_GH[a], "REST_HOLD": S8.WITNESS_RH[a]}) for a in S8.FORCED)
        want9 = dict((("cvt9", a), dict([("BETA_HOLD", S9.WITNESS_BH[a]), ("COMP_HOLD", S9.WITNESS_CH[a])]
                                        + ([("WINDOW_HOLD", S9.WITNESS_WH[a])] if a in S9.WINDOWED else [])))
                     for a in S9.FORCED)
        chk(dict((k, v) for k, v in mk.items() if k[0] == "cvt8") == want8,
            "C23 MULTI_KIND's cvt8 entries == cvt8's FORCED arms x the registered scorer's WITNESS_GH / WITNESS_RH",
            repr(dict((k, v) for k, v in mk.items() if k[0] == "cvt8"))[:200])
        chk(dict((k, v) for k, v in mk.items() if k[0] == "cvt9") == want9,
            "C23 MULTI_KIND's cvt9 entries == cvt9's held arms x WITNESS_BH / WITNESS_CH (+ WITNESS_WH for EARLY / LATE)",
            repr(dict((k, v) for k, v in mk.items() if k[0] == "cvt9"))[:200])
        offs = set(off for _k, off in CE.KINDS)
        on8 = dict((a, sorted(k for k, w in (("GROUP_HOLD", S8.WITNESS_GH[a]), ("REST_HOLD", S8.WITNESS_RH[a]),
                                             ("BETA_HOLD", S8.WITNESS_BH), ("VOTE_W", S8.WITNESS_VW)) if w not in offs))
                   for a in S8.ARMS)
        on9 = dict((a, sorted(k for k, w in (("BETA_HOLD", S9.WITNESS_BH[a]), ("COMP_HOLD", S9.WITNESS_CH[a]),
                                             ("WINDOW_HOLD", S9.WITNESS_WH[a]), ("VOTE_W", S9.WITNESS_VW)) if w not in offs))
                   for a in S9.ARMS)
        chk(set(("cvt8", a) for a, ks in on8.items() if len(ks) > 1) | set(("cvt9", a) for a, ks in on9.items() if len(ks) > 1)
            == set(k for k in mk if k[0] in ("cvt8", "cvt9"))
            and all(sorted(mk[("cvt8", a)]) == on8[a] for a in S8.FORCED) and all(sorted(mk[("cvt9", a)]) == on9[a] for a in S9.FORCED),
            "C23 the cvt8 / cvt9 arms whose registered witnesses are ON in 2+ kinds are exactly MULTI_KIND's, with those kinds",
            repr((on8, on9))[:300])
        chk((S8.WITNESS_GH["HOLDHIGH"], S8.WITNESS_GH["HOLDBIG"], S8.WITNESS_GH["LOWISOPATH"], S8.WITNESS_RH["HIGHISOPATH"])
            == (GH_TRI, GH_TRI_BIG, GH_FLOOR, RH_REC),
            "C23 this test's cvt8 fixtures are the registered scorer's lines")
        chk((S9.WITNESS_BH["LOWHEADPATH"], S9.WITNESS_BH["HIGHHEADPATH"], S9.WITNESS_BH["MIDDOSE"], S9.WITNESS_BH["RESDOSE"],
             S9.WITNESS_BH["EARLY"], S9.WITNESS_CH["LATE"], S9.WITNESS_WH["EARLY"], S9.WITNESS_WH["LATE"])
            == (BH_FLOOR, BH_TRI, BH_TRI_7235, BH_TRI_8609, BH_TRI, CH_REC, WH_EARLY, WH_LATE),
            "C23 this test's cvt9 fixtures are the registered scorer's lines")
    except Exception as ex:  # a scorer that does not import is a FAIL here, not an error
        chk(False, "C23 the registered cvt8 / cvt9 scorers import and MULTI_KIND holds their arms",
            "%s: %s" % (type(ex).__name__, ex))

    # ---- CORRECTIONS 263 ------------------------------------------------------------------------------------
    print("C24 the ARGS reader, the registry and the prefix proof")
    try:
        sys.path.insert(0, os.path.join(REPO, "analysis"))
        import corpus_exclusions as CE2
        import argsline_guard as AG  # RULE 20's registered parser: imported HERE, never by the module
        lines = [DEFAULT_ARGS,
                 CMO_ARGS % ("0.9", "0.1", "scalar", "cmo1-M9k01-s108"),
                 CMO_ARGS % ("0.99", "0", ISO_SETS, "cmo1-W0ISO-s110"),
                 "--momentum-param-base 0.99 --momentum-param-base 0.9",          # argparse: the LAST wins
                 "--momentum-param-base=0.9 --weight-decay-base=0",               # --flag=value
                 "--alg-base SGDm --Lion-beta2-base -1 --beta-clip -15:-2.3026",  # negative values are values
                 "--weight-decay-base 0.1 --run-name a b c",
                 "", "--wait --stepsize-groups scalar"]
        same = [dict(AG.effective(AG.parse_flags(AG.tokenize(l)))) == dict(CE2._args_effective(CE2._args_tokens(l)))
                for l in lines]
        chk(all(same), "C24 the module's re-typed ARGS reader == argsline_guard's on %d lines" % len(lines),
            repr([l for l, s in zip(lines, same) if not s])[:200])
        chk([tuple(e) for e in CE2.ARGS_KINDS] == [("ARGS_MOMENTUM_BASE", "momentum-param-base", "0.99"),
                                                   ("ARGS_WD_BASE", "weight-decay-base", "0.1")],
            "C24 ARGS_KINDS = the two cmo1 factors with the standard-cell values 0.99 / 0.1", repr(CE2.ARGS_KINDS))
        # CORRECTIONS 269: was `len(set(names)) == 8`; two line kinds were added, so the count is `len(names)` (C33
        # pins it at 10).  263's claim -- no name a prefix of another, across both readers -- is unchanged.
        names = [k for k, _o in CE2.KINDS] + [k for k, _f, _s in CE2.ARGS_KINDS]
        chk(len(set(names)) == len(names) and len(names) >= 8
            and not [(a, b) for a in names for b in names if a != b and a.startswith(b)],
            "C24 no name of the 6 line kinds + 2 ARGS kinds is a prefix of another", repr(names))
        chk(not [k for k, _o in CE2.KINDS if "ARGS:".startswith(k) or k.startswith("ARGS")],
            "C24 `ARGS:` starts with no line-kind prefix, so witness_lines never collects an ARGS line")
        chk(all(AG.ARGS_RE.match(CE2.args_witness(k, "0.9")) is None for k, _f, _s in CE2.ARGS_KINDS)
            and CE2.kind_of(W_MOM) == "ARGS_MOMENTUM_BASE" and CE2.kind_of(W_WD) == "ARGS_WD_BASE"
            and CE2.kind_of(BH_TRI) == "BETA_HOLD" and CE2.kind_of("ARGS: --momentum-param-base 0.9") is None,
            "C24 no ARGS-kind witness is itself an `ARGS:` line, and kind_of reads each witness as ONE kind",
            repr([CE2.args_witness(k, "0.9") for k, _f, _s in CE2.ARGS_KINDS]))
        chk(CE2.args_witness("ARGS_MOMENTUM_BASE", "0.9") == W_MOM and CE2.args_witness("ARGS_WD_BASE", "0") == W_WD,
            "C24 the witness form is `<KIND>: <flag>=<value>`, the value verbatim from the ARGS line")
    except Exception as ex:
        chk(False, "C24 the module and argsline_guard import and expose the ARGS reader", "%s: %s" % (type(ex).__name__, ex))

    print("C25 a cmo1-style batch passes")
    listed, corpus, logs, args, cells = cmo_batch()
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C25 3 anchor arms unlisted + 3 M9 and 3 W0 arms listed by their ARGS value -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    chk(any("6 listed runs carry their listed ARGS value" in ln for ln in line_of(out, "  ARGS witness")),
        "C25 the added line counts the 6 listed ARGS rows", repr(line_of(out, "  ARGS witness")))
    chk(any("6 deviate" in ln and "6 are CSV rows in the standard cell, every one listed: True" in ln
            for ln in line_of(out, "  ARGS witness")),
        "C25 completeness: the 6 deviating standard-cell CSV rows are all listed", repr(line_of(out, "  ARGS witness")))
    chk(any(ln.endswith(": True") for ln in line_of(out, "  ARGS cell mixing")),
        "C25 no cell pools two different (momentum, weight decay) values", repr(line_of(out, "  ARGS cell mixing")))
    chk(len(line_of(out, "  ARGS")) == 3, "C25 the block adds exactly three lines", repr(line_of(out, "  ARGS")))

    print("C26 corruptions fail, each named")
    listed, corpus, logs, args, cells = cmo_batch()
    rc, out = run_check([r for r in listed if r[:2] != CMO["M9kL"]], corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("cmo1-M9kL-s108-5025987.out" in f and "NOT listed" in f for f in fails(out)),
        "C26a an M9 row dropped from the list -> exit 1, named", show(out))
    for tag, arm, mom, wd, msg in [("b", "M9k01", "0.99", "0.1", "but its own ARGS line does not deviate"),
                                   ("c", "M9ISO", "0.8", "0.1", "ARGS witness"),
                                   ("d", "W0kL", "0.9", "0", "but is listed with a")]:
        listed, corpus, logs, args, cells = cmo_batch()
        key = CMO[arm]
        args[key] = CMO_ARGS % (mom, wd, "scalar", key[0])
        rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
        chk(rc == 1 and any(("%s-%s.out" % key) in f and msg in f for f in fails(out)),
            "C26%s %s runs at momentum %s / wd %s -> exit 1, named" % (tag, arm, mom, wd), show(out))
    listed, corpus, logs, args, cells = cmo_batch()
    extra = ("cmo1-M9k01-s109", "5025995")
    logs[extra] = ["VOTE_W: off"]
    args[extra] = CMO_ARGS % ("0.9", "0.1", "scalar", extra[0])
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("cmo1-M9k01-s109-5025995.out" in f and "unlisted run of a listed batch" in f for f in fails(out)),
        "C26e a deviating unlisted .out of the listed batch, not yet a CSV row -> exit 1, named", show(out))

    print("C27 scope: outside the standard cell, absent flags, no ARGS line")
    listed, corpus, logs, args, cells = cmo_batch()
    out300 = ("c300-ly-s7", "5000301")
    corpus.append(out300)
    logs[out300] = ["VOTE_W: off"]
    args[out300] = CMO_ARGS % ("0.9", "0.1", "layerwise", out300[0])
    cells[out300] = {"network": "ResNet18_c100", "granularity": "layerwise", "epochs_requested": "300"}
    noargs = ("c300-ly-s8", "5000302")
    corpus.append(noargs)
    logs[noargs] = ["VOTE_W: off"]
    args[noargs] = None
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C27 a 300-epoch ingested run at momentum 0.9 is NOT required to be listed -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    chk(any("1 deviating CSV row" in ln or "1 deviating CSV rows" in ln for ln in line_of(out, "  ARGS witness")),
        "C27 it is counted DESCRIPTIVELY on the added line", repr(line_of(out, "  ARGS witness")))
    chk(any("(1 without one)" in ln for ln in line_of(out, "  ARGS witness")),
        "C27 the log with no ARGS line is counted, not failed", repr(line_of(out, "  ARGS witness")))

    print("C28 two unlisted ingested runs of ONE cell with different momentum fail")
    listed, corpus, logs, args, cells = cmo_batch()
    twin = ("cmo1-k01-s109", "5025992")
    corpus.append(twin)
    logs[twin] = ["VOTE_W: off"]
    args[twin] = CMO_ARGS % ("0.9", "0.1", "scalar", twin[0])
    cells[twin] = {"network": "ResNet18_c100", "granularity": "scalar"}
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("cmo1-k01-s109" in f for f in fails(out)),
        "C28 an unlisted 0.9 run in the scalar cell of unlisted 0.99 runs -> exit 1, named", show(out))
    rc, out = run_check(listed + [twin + (W_MOM,)], corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out, "C28 the same pair passes once the 0.9 run is listed",
        "rc=%d %s" % (rc, show(out)))

    # ---- CORRECTIONS 269 ------------------------------------------------------------------------------------
    print("C29 a cwd1-style DECAY_MASK batch passes")
    rc, out = run_check(*dm_batch())
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C29 4 masked runs listed by their DECAY_MASK line, k01 unlisted at `DECAY_MASK: off` -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    chk(any("DECAY_MASK" in ln and "every one listed with its kind: True" in ln
            for ln in line_of(out, "  completeness")),
        "C29 the completeness line names DECAY_MASK and is True", repr(line_of(out, "  completeness")))

    print("C30 DECAY_MASK corruptions fail, each named")
    for tag, key, line, msg in [("a", D1_NWD, "DECAY_MASK: off", "witness"),
                                ("b", D1_LNWD, DM_WRONG, "witness")]:
        listed, corpus, logs = dm_batch()
        logs[key] = CWD1_OFF + [line]
        rc, out = run_check(listed, corpus, logs)
        chk(rc == 1 and any(("%s-%s.out" % key) in f and msg in f for f in fails(out)),
            "C30%s %s prints %r but is listed with its registered line -> exit 1, named"
            % (tag, key[0], line[:40]), show(out))
    listed, corpus, logs = dm_batch()
    rc, out = run_check([r for r in listed if r[:2] != D1_LNWD], corpus, logs)
    chk(rc == 1 and any(("%s-%s.out" % D1_LNWD) in f and "NOT listed" in f for f in fails(out)),
        "C30c one masked run dropped from the list -> exit 1, named", show(out))
    listed, corpus, logs = dm_batch()
    rc, out = run_check([], corpus, logs)
    chk(rc == 1 and len([f for f in fails(out) if "printing an ON DECAY_MASK line but is NOT listed" in f]) == 4,
        "C30d a masked batch with NO listed row -> exit 1, all four named", show(out))
    listed, corpus, logs = dm_batch()
    logs[D1_K01] = CWD1_OFF                                   # the k01 run prints no DECAY_MASK line at all
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and any(("%s-%s.out" % D1_K01) in f and "NOT listed but its witness is" in f for f in fails(out)),
        "C30e an unlisted run of a listed DECAY_MASK batch with no `DECAY_MASK: off` line -> exit 1, named", show(out))
    off_only = {("cwd9-k01-s1", "5000901"): CWD1_OFF + ["DECAY_MASK: off"]}
    rc, out = run_check(*merge(dm_batch(), ([], [("cwd9-k01-s1", "5000901")], off_only)))
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C30f an unlisted batch whose runs print `DECAY_MASK: off` stays unlisted -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))

    print("C31 cwd2-style multi-kind runs (BETA_HOLD + COMP_HOLD + DECAY_MASK) listed ONCE pass")
    for by in ("DECAY_MASK", "BETA_HOLD", "COMP_HOLD"):
        rc, out = run_check(*dm2_batch(by))
        chk(rc == 0 and "VERDICT: PASS" in out,
            "C31 the three held / masked arms listed by their %s line -> exit 0 PASS" % by, "rc=%d %s" % (rc, show(out)))
    rc, out = run_check(*dm2_batch())
    chk(any("3 kinds 2" in ln for ln in line_of(out, "  multi-kind runs")),
        "C31 the multi-kind line counts the two 3-kind runs (HIGHWD0 / LOWWD0)", repr(line_of(out, "  multi-kind runs")))
    for tag, key, lines, msg in [
            ("a", D2_HWD, ["VOTE_W: off", BH_TRI, CH_REC, "WINDOW_HOLD: off", "DECAY_MASK: off"], "MULTI_KIND"),
            ("b", D2_LWD, ["VOTE_W: off", BH_TRI, CH_REC, "WINDOW_HOLD: off", DM_CARRIER], "MULTI_KIND"),
            ("c", D2_WD0, ["VOTE_W: off", BH_TRI, "COMP_HOLD: off", "WINDOW_HOLD: off", DM_CARRIER], "BETA_HOLD"),
            ("d", D2_HHP, ["VOTE_W: off", BH_TRI, CH_REC, "WINDOW_HOLD: off", DM_CARRIER], "DECAY_MASK")]:
        listed, corpus, logs = dm2_batch()
        logs[key] = lines
        rc, out = run_check(listed, corpus, logs)
        chk(rc == 1 and any(("%s-%s.out" % key) in f and msg in f for f in fails(out)),
            "C31%s %s prints a wrong registered line -> exit 1, named with %s" % (tag, key[0], msg), show(out))

    print("C32 a csv1-style SHADOW_VOTE batch passes")
    rc, out = run_check(*sv_batch())
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C32 INERT / SHADOWLOW / NAIVELOW listed by SHADOW_VOTE, MUTE by VOTE_W, k01 / HEAD unlisted -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    chk(any("SHADOW_VOTE" in ln and "every one listed with its kind: True" in ln for ln in line_of(out, "  completeness")),
        "C32 the completeness line names SHADOW_VOTE and is True", repr(line_of(out, "  completeness")))
    for tag, key, lines, msg in [
            ("a", S1_SL, ["VOTE_W: off"] + ["BETA_HOLD: off", "COMP_HOLD: off", "WINDOW_HOLD: off"] + [SV_NAIVELOW],
             "witness"),
            ("b", S1_NL, ["VOTE_W: off"] + ["BETA_HOLD: off", "COMP_HOLD: off", "WINDOW_HOLD: off"] + ["SHADOW_VOTE: off"],
             "witness"),
            ("e", S1_MUTE, [VW_MUTE] + ["BETA_HOLD: off", "COMP_HOLD: off", "WINDOW_HOLD: off"] + [SV_INERT],
             "SHADOW_VOTE")]:
        listed, corpus, logs = sv_batch()
        logs[key] = lines
        rc, out = run_check(listed, corpus, logs)
        chk(rc == 1 and any(("%s-%s.out" % key) in f and msg in f for f in fails(out)),
            "C32%s %s prints a wrong SHADOW_VOTE line -> exit 1, named" % (tag, key[0]), show(out))
    listed, corpus, logs = sv_batch()
    rc, out = run_check([r for r in listed if r[:2] != S1_IN], corpus, logs)
    chk(rc == 1 and any(("%s-%s.out" % S1_IN) in f and "NOT listed" in f for f in fails(out)),
        "C32c INERT dropped from the list -> exit 1, named", show(out))
    listed, corpus, logs = sv_batch()
    logs[S1_HEAD] = ["VOTE_W: off", "BETA_HOLD: off", "COMP_HOLD: off", "WINDOW_HOLD: off"]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and any(("%s-%s.out" % S1_HEAD) in f and "NOT listed but its witness is" in f for f in fails(out)),
        "C32d an unlisted run of the listed batch with no `SHADOW_VOTE: off` line -> exit 1, named", show(out))

    print("C33 the new KINDS, the prefix proof, the patches' line forms, and MULTI_KIND against the cwd / csv tables")
    # CORRECTIONS 304: was `CE.KINDS[6:] == [...] and len(CE.KINDS) == 8`; KINDS now also holds VAL_SPLIT (C44 owns the
    # total and the added entry).  269's claim is unchanged over entries 7 and 8.
    chk(CE.KINDS[6:8] == [("DECAY_MASK", "DECAY_MASK: off"), ("SHADOW_VOTE", "SHADOW_VOTE: off")],
        "C33 KINDS = 251's six + DECAY_MASK + SHADOW_VOTE, appended", repr(CE.KINDS[6:]))
    kinds8 = [k for k, _off in CE.KINDS[:8]]   # CORRECTIONS 304: 269's eight, not every kind (C43 proves the nine)
    chk(len(kinds8) == 8 and len(set(k[0] for k in kinds8)) == 8
        and all(not a.startswith(b) for a in kinds8 for b in kinds8 if a != b),
        "C33 the eight first letters differ (%s), so no prefix is a prefix of another" % " ".join(k[0] for k in kinds8))
    names10 = kinds8 + [k for k, _f, _s in CE.ARGS_KINDS]
    chk(not [(a, b) for a in names10 for b in names10 if a != b and a.startswith(b)]
        and not [k for k in kinds8 if "ARGS:".startswith(k) or k.startswith("ARGS")]
        and CE.kind_of(DM_NORMSCALE) == "DECAY_MASK" and CE.kind_of(SV_INERT) == "SHADOW_VOTE"
        and CE.kind_of("DECAY_MASK: off") == "DECAY_MASK",
        "C33 no name of the 8 line kinds + 2 ARGS kinds is a prefix of another, and neither reader takes the other's line",
        repr(names10))
    EIGHT = ["VOTE_W", "BETA_HOLD", "GROUP_HOLD", "COMP_HOLD", "REST_HOLD", "WINDOW_HOLD", "DECAY_MASK",
             "SHADOW_VOTE"]  # literal, not read from the module
    eight = "|".join(sorted(EIGHT))
    for k, fn, on in (("DECAY_MASK", "patch_decaymask.py", "DECAY_MASK: on base="),
                      ("SHADOW_VOTE", "patch_shadowvote.py", "SHADOW_VOTE: on type=")):
        src = open(os.path.join(REPO, "patches", fn)).read()
        lits = re.findall(r"'((?:%s): [^']*)'" % eight, src)
        chk(("%s: off" % k) in lits and any(l.startswith(on) for l in lits) and all(l.startswith(k + ": ") for l in lits),
            "C33 %s prints only `%s: off` / `%s ...` lines" % (fn, k, on), repr(sorted(set(lits)))[:300])
    tmp = tempfile.mkdtemp(prefix="ce_prefix_test_")
    try:
        p = os.path.join(tmp, "x.out")
        sixteen = ([VW_MUTE, BH_TRI, GH_TRI, CH_REC, RH_REC, WH_EARLY, DM_NORMSCALE, SV_SHADOWLOW]
                   + ["%s: off" % k for k in EIGHT])
        open(p, "w").write("\n".join(sixteen) + "\n")
        got = CE.witness_lines(p)
        # CORRECTIONS 304: was `sorted(got) == sorted(EIGHT)`; witness_lines now also returns VAL_SPLIT's key, empty on
        # these sixteen lines -- so the kinds that COLLECT a line are still exactly 269's eight.
        chk(sorted(k for k in got if got[k]) == sorted(EIGHT)
            and all(got[k] == [ln for ln in sixteen if ln.split(":")[0] == k] for k in EIGHT),
            "C33 witness_lines puts each of 16 lines (one on, one off per kind) under its own kind only", repr(sorted(got)))
    finally:
        shutil.rmtree(tmp)
    rc, out = run_check(*merge(rh_batch(), wh_batch(), dm_batch(), dm2_batch(), sv_batch()))
    chk(("  kinds scanned (CORRECTIONS 245): VOTE_W / BETA_HOLD / GROUP_HOLD / COMP_HOLD; no prefix is a prefix of another, "
         "so no line is read as two kinds: True") in out.splitlines(),
        "C33 245's `kinds scanned` line is unchanged, byte for byte", repr(line_of(out, "  kinds scanned")))
    chk(("  kinds scanned (CORRECTIONS 251): also REST_HOLD / WINDOW_HOLD, 6 in all; no prefix of the 6 is a prefix of "
         "another: True") in out.splitlines(),
        "C33 251's `kinds scanned` line is unchanged, byte for byte", repr(line_of(out, "  kinds scanned")))
    chk(any("DECAY_MASK / SHADOW_VOTE" in ln and "8 in all" in ln and ln.endswith(": True")
            for ln in line_of(out, "  kinds scanned (CORRECTIONS 269)")),
        "C33 ONE new line names the two added kinds, no prefix collision", repr(line_of(out, "  kinds scanned")))
    # CORRECTIONS 304: was `len(line_of(out, "  kinds scanned")) == 3`; 304 adds ONE line of its own (C41 / C44 own it)
    # CORRECTIONS 308: was `... if not ln.startswith("  kinds scanned (CORRECTIONS 304)")]) == 3`; 308 adds ONE more (C46 /
    # C50 own it), so both later lines are excluded
    chk(len([ln for ln in line_of(out, "  kinds scanned") if not ln.startswith(("  kinds scanned (CORRECTIONS 304)",
                                                                                 "  kinds scanned (CORRECTIONS 308)"))]) == 3,
        "C33 exactly three `kinds scanned` lines",
        repr(line_of(out, "  kinds scanned")))
    try:
        mk = getattr(CE, "MULTI_KIND", None) or {}
        import cwd_design as DW              # the frozen tables both registered cWD scorers import UNEDITED
        import cSV1_shadowvote_score as SSV  # the registered csv1 scorer
        offs = set(off for _k, off in CE.KINDS)
        on1 = dict((a, dict((k, w) for k, w in [("DECAY_MASK", DW.CWD1.WITNESS_DM[a])] + list(zip(DW.CWD1.OFF_KINDS,
                                                                                                 DW.CWD1.OFF_LINES))
                            if w not in offs)) for a in DW.CWD1.ARMS)
        on2 = dict((a, dict((k, w) for k, w in (("VOTE_W", DW.CWD2.WITNESS_VW), ("BETA_HOLD", DW.CWD2.WITNESS_BH[a]),
                                                ("COMP_HOLD", DW.CWD2.WITNESS_CH[a]),
                                                ("WINDOW_HOLD", DW.CWD2.WITNESS_WH[a]),
                                                ("DECAY_MASK", DW.CWD2.WITNESS_DM[a])) if w not in offs))
                   for a in DW.CWD2.ARMS)
        onS = dict((a, dict((k, w) for k, w in ([("VOTE_W", SSV.WITNESS_VW[a]), ("SHADOW_VOTE", SSV.WITNESS_SV[a])]
                                                + list(zip(("BETA_HOLD", "COMP_HOLD", "WINDOW_HOLD"), SSV.WITNESS_OFF)))
                            if w not in offs)) for a in SSV.ARMS)
        want2 = dict((("cwd2", a), d) for a, d in on2.items() if len(d) > 1)
        chk(dict((k, v) for k, v in mk.items() if k[0] == "cwd2") == want2 and len(want2) == 3,
            "C33 MULTI_KIND's cwd2 entries == cwd_design's WITNESS_BH / WITNESS_CH / WITNESS_DM for its 2+-kind arms",
            repr(sorted(want2)))
        chk(not [k for k in mk if k[0] in ("cwd1", "csv1")]
            and not [a for a, d in on1.items() if len(d) > 1] and not [a for a, d in onS.items() if len(d) > 1],
            "C33 no cwd1 / csv1 arm turns on two kinds, and MULTI_KIND registers none for them",
            repr((sorted((a, sorted(d)) for a, d in on1.items()), sorted((a, sorted(d)) for a, d in onS.items()))))
        chk((DW.CWD1.WITNESS_DM["k01NWD"], DW.CWD1.WITNESS_DM["kLNWD"], DW.CWD1.WITNESS_DM["k01"],
             DW.CWD2.WITNESS_DM["HIGHWD0"], DW.CWD2.WITNESS_DM["LOWWD0"], DW.CWD2.WITNESS_DM["k01WD0"])
            == (DM_NORMSCALE, DM_NORMSCALE, "DECAY_MASK: off", DM_CARRIER, DM_CARRIER, DM_CARRIER),
            "C33 this test's DECAY_MASK fixtures are the registered cwd_design lines")
        chk((SSV.WITNESS_SV["INERT"], SSV.WITNESS_SV["SHADOWLOW"], SSV.WITNESS_SV["NAIVELOW"], SSV.WITNESS_SV["k01"],
             SSV.WITNESS_VW["MUTE"]) == (SV_INERT, SV_SHADOWLOW, SV_NAIVELOW, "SHADOW_VOTE: off", VW_MUTE),
            "C33 this test's SHADOW_VOTE fixtures are the registered cSV1 scorer's lines")
        chk((DW.CWD2.WITNESS_BH["HIGHWD0"], DW.CWD2.WITNESS_BH["LOWWD0"], DW.CWD2.WITNESS_CH["HIGHHEADPATH"])
            == (BH_TRI, BH_FLOOR, CH_REC),
            "C33 cwd2's hold lines are cvt9's, byte for byte (261.5: taken from the registered cvt9 scorer)")
    except Exception as ex:  # a table that does not import is a FAIL here, not an error
        chk(False, "C33 cwd_design and the registered cSV1 scorer import and MULTI_KIND holds cwd2's arms",
            "%s: %s" % (type(ex).__name__, ex))

    # ---- CORRECTIONS 284 ------------------------------------------------------------------------------------
    print("C34 a cwd5-style ladder with a TWO-AXIS arm passes")
    listed, corpus, logs, args, cells = wd5_batch()
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C34 6 single-axis rung arms + CARW2 listed by their ARGS_WD_BASE value, 2 anchors unlisted -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    chk(any("1 listed run" in ln and ln.endswith(": True") for ln in line_of(out, "  two-axis runs")),
        "C34 the new two-axis line counts the CARW2 run and is True", repr(line_of(out, "  two-axis runs")))
    chk(any("DECAY_MASK" in ln and "every one listed with its kind: True" in ln for ln in line_of(out, "  completeness")),
        "C34 completeness names DECAY_MASK and is True with CARW2 listed by its ARGS witness",
        repr(line_of(out, "  completeness")))
    chk(any("7 listed runs carry their listed ARGS value" in ln for ln in line_of(out, "  ARGS witness"))
        and any("7 deviate from the standard, 7 are CSV rows in the standard cell, every one listed: True" in ln
                for ln in line_of(out, "  ARGS witness")),
        "C34 the ARGS block counts all 7 deviating rung runs, CARW2 among them", repr(line_of(out, "  ARGS witness")))
    listed, corpus, logs, args, cells = merge5(wd5_batch(), dm_batch(), cmo_batch())
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C34 the single-axis batches still pass merged in: cwd1 (kind only) + cmo1 (ARGS only) + cwd5 -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))

    print("C35 the rule is forced and every two-axis corruption fails, each named")
    listed, corpus, logs, args, cells = wd5_batch("DECAY_MASK")
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any(("%s-%s.out" % CWD5_CAR) in f and "deviates on ARGS_WD_BASE" in f
                        and "listed with a DECAY_MASK witness" in f for f in fails(out)),
        "C35a the REVERSE listing (by the DECAY_MASK line) still FAILs: the ARGS reader has no escape", show(out))
    for tag, line, msg in [("b", DM_CARRIERS3_W1, "MULTI_KIND"), ("c", "DECAY_MASK: off", "MULTI_KIND")]:
        listed, corpus, logs, args, cells = wd5_batch()
        logs[CWD5_CAR] = CWD1_OFF + [line]
        rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
        chk(rc == 1 and any(("%s-%s.out" % CWD5_CAR) in f and msg in f for f in fails(out)),
            "C35%s CARW2 prints %r, not its registered line -> exit 1, named with %s" % (tag, line[:40], msg),
            show(out))
    for tag, wd, msg in [("d", "0.1", "does not deviate"), ("e", "1e-3", "ARGS witness")]:
        listed, corpus, logs, args, cells = wd5_batch()
        args[CWD5_CAR] = CWD5_ARGS % (wd, "scalar", CWD5_CAR[0])
        rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
        chk(rc == 1 and any(("%s-%s.out" % CWD5_CAR) in f and msg in f for f in fails(out)),
            "C35%s CARW2's own ARGS line says --weight-decay-base %s -> exit 1, named" % (tag, wd), show(out))
    listed, corpus, logs, args, cells = wd5_batch()
    rc, out = run_check([r for r in listed if r[:2] != CWD5_CAR], corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("printing an ON DECAY_MASK line but is NOT listed" in f for f in fails(out))
        and any("whose ARGS deviates" in f and "NOT listed" in f for f in fails(out)),
        "C35f CARW2 dropped from the list -> exit 1, named TWICE (completeness and the standard-cell ARGS rule)",
        show(out))
    listed, corpus, logs, args, cells = wd5_batch()
    logs[CWD5["k01W2"]] = CWD1_OFF + [DM_CARRIERS3_W2]     # a single-axis rung arm with no MULTI_KIND entry
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any(("%s-%s.out" % CWD5["k01W2"]) in f and "prints an ON DECAY_MASK line" in f
                        and "listed with a ARGS_WD_BASE witness" in f for f in fails(out)),
        "C35g a rung arm printing an ON DECAY_MASK line it is not registered for -> exit 1, named", show(out))
    listed, corpus, logs, args, cells = wd5_batch()
    logs[CWD5["k01W1"]] = CWD1_OFF                         # the anchor prints no DECAY_MASK line at all
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any(("%s-%s.out" % CWD5["k01W1"]) in f and "NOT listed but its witness is" in f
                        for f in fails(out)),
        "C35h an unlisted anchor of the listed batch with no `DECAY_MASK: off` line -> exit 1, named", show(out))

    print("C36 the two-axis registry entry and the print lines")
    mk5 = dict((k, v) for k, v in (getattr(CE, "MULTI_KIND", None) or {}).items() if k[0] == "cwd5")
    chk(list(mk5) == [("cwd5", "CARW2")] and sorted(mk5.get(("cwd5", "CARW2"), {})) == ["DECAY_MASK"],
        "C36 MULTI_KIND gains exactly one cwd5 entry, registering exactly DECAY_MASK", repr(sorted(mk5)))
    chk(mk5.get(("cwd5", "CARW2"), {}).get("DECAY_MASK") == DM_CARRIERS3_W2,
        "C36 its registered line is this test's fixture, byte for byte")
    try:
        import cwd5_design as D5                  # the frozen table the registered cWD5 scorer imports UNEDITED
        chk(D5.CWD5.WITNESS_DM["CARW2"] == DM_CARRIERS3_W2 and D5.CWD5.WD["CARW2"] == "1e-2"
            and "wd=0.01" in DM_CARRIERS3_W2 and D5.CWD5.DMASK["CARW2"] and D5.CWD5.MASKED == ("CARW2",),
            "C36 MULTI_KIND's cwd5 line == cwd5_design's WITNESS_DM['CARW2'], at the arm's OWN rung (wd=0.01)")
        chk([a for a in D5.CWD5.ARMS if D5.CWD5.WITNESS_DM[a] != "DECAY_MASK: off"] == ["CARW2"]
            and sorted(D5.CWD5.ARGS_DEVIATING) == ["CARW2", "k01W2", "k01W3", "k01W4", "kLW2", "kLW3", "kLW4"],
            "C36 CARW2 is the batch's ONLY ON-line arm and one of its 7 ARGS-deviating arms -- the two-axis run",
            repr(sorted(D5.CWD5.ARGS_DEVIATING)))
    except Exception as ex:                       # a table that does not import is a FAIL here, not an error
        chk(False, "C36 cwd5_design imports and MULTI_KIND holds its CARW2 line", "%s: %s" % (type(ex).__name__, ex))
    rc, out = run_check(*merge(rh_batch(), wh_batch(), dm_batch(), dm2_batch(), sv_batch()))
    chk(("  multi-kind runs (CORRECTIONS 251): those runs by the number of kinds MULTI_KIND registers for them: "
         "2 kinds 8, 3 kinds 4") in out.splitlines(),
        "C36 251's `multi-kind runs` line is unchanged by the single-kind entry, byte for byte",
        repr(line_of(out, "  multi-kind runs")))
    chk(line_of(out, "  two-kind runs")[0].split(":")[1].strip().startswith("%d listed runs"
                                                                            % sum(int(p.split()[-1]) for p in
                                                                                  line_of(out, "  multi-kind runs")[0]
                                                                                  .split(": ")[-1].split(", "))),
        "C36 245's count == the sum of 251's breakdown: neither line counts the one-kind two-axis entry",
        repr(line_of(out, "  two-kind runs") + line_of(out, "  multi-kind runs")))
    # CORRECTIONS 304: was `len(line_of(out, "  kinds scanned")) == 3`; 304's own line is excluded (C44 owns it)
    # CORRECTIONS 308: was `... if not ln.startswith("  kinds scanned (CORRECTIONS 304)")]) == 3`; 308's line is excluded too
    chk(len([ln for ln in line_of(out, "  kinds scanned") if not ln.startswith(("  kinds scanned (CORRECTIONS 304)",
                                                                                 "  kinds scanned (CORRECTIONS 308)"))]) == 3
        and len(line_of(out, "  two-axis runs")) == 1
        and len(line_of(out, "  multi-kind runs")) == 1,
        "C36 `--check --runs` gains exactly ONE line: three `kinds scanned`, one `multi-kind`, one `two-axis`",
        repr(line_of(out, "  two-axis runs")))
    chk(getattr(CE, "MULTI_KINDS_AT_251", None) == 2
        and sorted(set(len(d) for d in CE.MULTI_KIND.values())) == [1, 2, 3],
        "C36 the 251 line is frozen over entries of 2+ kinds while MULTI_KIND itself now holds a 1-kind entry",
        repr(sorted(set(len(d) for d in CE.MULTI_KIND.values()))))

    # ---- CORRECTIONS 294 ------------------------------------------------------------------------------------
    import hashlib
    NEWLINE = "  multi-ARGS runs (CORRECTIONS 294)"
    xs, xl = "%s-%s.out" % CAW2["XS"], "%s-%s.out" % CAW2["XL"]
    print("C37 a caw2-style batch with TWO-ARGS runs passes")
    for by in ("ARGS_WD_BASE", "ARGS_MOMENTUM_BASE"):
        listed, corpus, logs, args, cells = caw2_batch(by)
        rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
        chk(rc == 0 and "VERDICT: PASS" in out,
            "C37 XS / XL listed ONCE by their %s value, the other kind held to MULTI_ARGS -> exit 0 PASS" % by,
            "rc=%d %s" % (rc, show(out)))
        chk(any("2 listed runs" in ln and ln.endswith(": True") for ln in line_of(out, NEWLINE)),
            "C37 (%s) the new multi-ARGS line counts the 2 X runs and is True" % by, repr(line_of(out, NEWLINE)))
        chk(any("6 listed runs carry their listed ARGS value" in ln
                and "6 deviate from the standard, 6 are CSV rows in the standard cell, every one listed: True" in ln
                for ln in line_of(out, "  ARGS witness")),
            "C37 (%s) the ARGS block counts all 6 listed / deviating standard-cell rows, XS / XL among them" % by,
            repr(line_of(out, "  ARGS witness")))
    listed, corpus, logs, args, cells = merge5(caw2_batch(), cmo_batch(), wd5_batch(), dm_batch())
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out
        and any("1 listed runs" in ln and ln.endswith(": True") for ln in line_of(out, "  two-axis runs"))
        and any("2 listed runs" in ln and ln.endswith(": True") for ln in line_of(out, NEWLINE)),
        "C37 merged with cmo1 (single ARGS) + cwd5 (switch + ARGS) + cwd1 (kind only) -> exit 0 PASS, both lines True",
        "rc=%d %s" % (rc, show(out)))

    print("C38 every two-ARGS corruption fails, each named")
    for tag, by, arm, mom, wd, msg in [
            ("a", "ARGS_WD_BASE", "XS", None, "0.1", "but its own ARGS line does not deviate"),
            ("b", "ARGS_MOMENTUM_BASE", "XS", None, "0.1", "(MULTI_ARGS)"),
            ("c", "ARGS_WD_BASE", "XS", "0.99", None, "(MULTI_ARGS)"),
            ("d", "ARGS_WD_BASE", "XS", None, "2.0", "ARGS witness"),
            ("e", "ARGS_WD_BASE", "XL", "0.8", None, "(MULTI_ARGS)")]:
        listed, corpus, logs, args, cells = caw2_batch(by)
        key = CAW2[arm]
        args[key] = caw2_args(arm, mom=mom, wd=wd)
        rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
        chk(rc == 1 and any(("%s-%s.out" % key) in f and msg in f for f in fails(out)),
            "C38%s %s listed by %s, its own ARGS line at momentum %s / wd %s -> exit 1, named with %r"
            % (tag, arm, by, mom or "0.9", wd or "1.0", msg), show(out))
        if tag in ("b", "c", "e"):                     # the kind the row does NOT carry: MULTI_ARGS's own catch
            chk(any(ln.endswith(": False") for ln in line_of(out, NEWLINE)),
                "C38%s the multi-ARGS line itself reads False" % tag, repr(line_of(out, NEWLINE)))
    listed, corpus, logs, args, cells = caw2_batch()
    rc, out = run_check([r for r in listed if r[:2] != CAW2["XS"]], corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any(xs in f and "standard cell whose ARGS deviates" in f and "NOT listed" in f for f in fails(out)),
        "C38f XS dropped from the list -> exit 1, named (a standard-cell row deviating, unlisted)", show(out))
    listed, corpus, logs, args, cells = caw2_batch()
    args[CAW2["AS"]] = caw2_args("AS", wd="1.0")          # AS has NO MULTI_ARGS entry
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any(("%s-%s.out" % CAW2["AS"]) in f and "deviates on ARGS_WD_BASE" in f
                        and "listed with a ARGS_MOMENTUM_BASE witness" in f for f in fails(out)),
        "C38g a two-ARGS run of an UNREGISTERED arm (AS at wd 1.0) -> exit 1, named: the escape is per (batch, arm)",
        show(out))
    listed, corpus, logs, args, cells = caw2_batch()
    extra = ("caw2-XS-s161", "5079315")
    logs[extra] = list(CAW2_OFF)
    args[extra] = caw2_args("XS", seed=161)
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("caw2-XS-s161-5079315.out" in f and "unlisted run of a listed batch" in f for f in fails(out)),
        "C38h a deviating XS .out of the listed batch, not yet a CSV row, unlisted -> exit 1, named", show(out))

    print("C39 the MULTI_ARGS registry, the fixture against the registered design, and the print lines")
    ma = getattr(CE, "MULTI_ARGS", None) or {}
    chk(sorted(ma) == [("caw2", "XL"), ("caw2", "XS")],
        "C39 MULTI_ARGS holds exactly (caw2, XS) and (caw2, XL)", repr(sorted(ma)))
    chk(all(ma.get(k) == {"ARGS_MOMENTUM_BASE": W_MOM9, "ARGS_WD_BASE": W_WD10} for k in (("caw2", "XS"), ("caw2", "XL"))),
        "C39 each registers exactly ARGS_MOMENTUM_BASE=0.9 and ARGS_WD_BASE=1.0, in the args_witness form",
        repr([ma.get(k) for k in sorted(ma)]))
    try:
        import caw2_design as A2                   # the registered design; imported by the test only
        chk(all(caw2_args(a) == A2.args_string(a, 160, "/home/s5014158/metaopt/runs/caw2") for a in A2.ARMS)
            and sorted(A2.ARMS) == sorted(CAW2),
            "C39 this test's 9 caw2 ARGS payloads == caw2_design.args_string, byte for byte")
        two = [a for a in A2.ARMS if len(A2.args_deviating_kinds(a)) >= 2]
        chk(two == ["XS", "XL"] and all(A2.args_deviating_kinds(a) == ("ARGS_MOMENTUM_BASE",)
                                        for a in ("LS", "LL", "AS", "AL"))
            and all(A2.args_deviating_kinds(a) == () for a in ("K01", "MS", "ML")),
            "C39 caw2_design names XS / XL (and only they) as two-ARGS-kind arms; LS / LL / AS / AL one; K01 / MS / ML none",
            repr(dict((a, A2.args_deviating_kinds(a)) for a in A2.ARMS)))
        chk(all(ma.get(("caw2", a), {}).get(k) == CE.args_witness(k, dict(A2.args_pairs(a, 0, "x"))[f])
                for a in two for k, f, _s in CE.ARGS_KINDS),
            "C39 every MULTI_ARGS witness == args_witness(kind, the registered design's own value)")
    except Exception as ex:
        chk(False, "C39 caw2_design imports and MULTI_ARGS holds its X arms", "%s: %s" % (type(ex).__name__, ex))
    # CORRECTIONS 304: was `len(CE.KINDS) == 8 and len(CE.MULTI_KIND) == 16`; 304 appends VAL_SPLIT and four cvl1 entries
    # (C44 owns them), so the claim is now made over everything else
    chk(CE.ARGS_KINDS == [("ARGS_MOMENTUM_BASE", "momentum-param-base", "0.99"), ("ARGS_WD_BASE", "weight-decay-base", "0.1")]
        # CORRECTIONS 308: was `k[0] != "VAL_SPLIT"` and `k[0] != "cvl1"`; 308 appends DECAY_ROUTE and ten cai1 / crd1 entries
        and len([k for k in CE.KINDS if k[0] not in ("VAL_SPLIT", "DECAY_ROUTE")]) == 8
        and len([k for k in CE.MULTI_KIND if k[0] not in ("cvl1", "cai1", "crd1")]) == 16,
        "C39 ARGS_KINDS / KINDS / MULTI_KIND are unchanged (2 / 8 / 16 entries)",
        "%d %d %d" % (len(CE.ARGS_KINDS), len(CE.KINDS), len(CE.MULTI_KIND)))
    b = wd5_batch()
    rc, out = run_check(*b[:3], args=b[3], cells=b[4])
    # CORRECTIONS 304: 304's own `kinds scanned` line is dropped too (C44 proves it is the only line 304 adds)
    kept = "".join(ln + "\n" for ln in out.split("\n")[:-1]
                   if not ln.startswith(NEWLINE) and not ln.startswith("  kinds scanned (CORRECTIONS 304)")
                   # CORRECTIONS 308: was the two conditions above only; 308's two added lines are dropped too (C50)
                   and not ln.startswith(("  kinds scanned (CORRECTIONS 308)", "  decay-route runs (CORRECTIONS 308)")))
    chk(rc == 0 and hashlib.sha256(kept.encode()).hexdigest()
        == "115c74ed3d7e87d9b9a5a1637ae421de56d81bb1b0d94870b76e5172f72d65df" and len(line_of(out, NEWLINE)) == 1,
        "C39 on 284's cwd5 fixture `--check --runs` gains exactly ONE line; every other byte == 284's module output",
        hashlib.sha256(kept.encode()).hexdigest()[:16])
    l5, c5, g5, a5, e5 = merge5(cmo_batch())
    rc, out = run_check(l5, c5, g5, args=a5, cells=e5, with_runs=False)
    chk(rc == 0 and hashlib.sha256(out.encode()).hexdigest()
        == "8e67462ac2950669b206eacdfbe6f3cdf4b6790f448401d29b62a7663d7e121b"
        and not line_of(out, NEWLINE),
        "C39 without --runs no line is added: cmo1's no-runs output == 284's module output, byte for byte",
        hashlib.sha256(out.encode()).hexdigest()[:16])

    print("C40 the MULTI_ARGS registry guard")
    for tag, src, msg in [
            ("a", 'MULTI_ARGS[("caw2", "AS")] = {"ARGS_MOMENTUM_BASE": "ARGS_MOMENTUM_BASE: momentum-param-base=0.9"}',
             "registers 1 ARGS kind"),
            ("b", 'MULTI_ARGS[("syn", "Q")] = {"ARGS_MOMENTUM_BASE": "ARGS_MOMENTUM_BASE: momentum-param-base=0.9", '
                  '"ARGS_LR_BASE": "ARGS_LR_BASE: lr=1"}', "is not a well-formed"),
            ("c", 'MULTI_ARGS[("syn", "Q")] = {"ARGS_MOMENTUM_BASE": "ARGS_MOMENTUM_BASE: weight-decay-base=0.9", '
                  '"ARGS_WD_BASE": "ARGS_WD_BASE: weight-decay-base=1.0"}', "is not a well-formed")]:
        rc, out = run_check(*merge5(cmo_batch())[:3], args=cmo_batch()[3], cells=cmo_batch()[4], with_runs=False,
                            module_append=src)
        chk(rc == 1 and any("MULTI_ARGS entry" in f and msg in f for f in fails(out)),
            "C40%s a malformed MULTI_ARGS entry FAILs without --runs, named with %r" % (tag, msg), show(out))

    # ---- CORRECTIONS 304 ------------------------------------------------------------------------------------
    import math
    L304 = "  kinds scanned (CORRECTIONS 304)"
    L308S = ("  kinds scanned (CORRECTIONS 308)", "  decay-route runs (CORRECTIONS 308)")   # CORRECTIONS 308 (C46 / C50)
    ALL_PRIOR = (wd5_batch(), rh_batch(), wh_batch(), dm_batch(), dm2_batch(), sv_batch(), cmo_batch(), caw2_batch())
    print("C41 a cvl1-style VAL_SPLIT batch passes (16 one-kind W1 rows, 16 two-axis W4 rows)")
    listed, corpus, logs, args, cells = cvl1_batch()
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C41 W1 listed by the VAL_SPLIT line, W4 by ARGS_WD_BASE=5e-4 with VAL_SPLIT in MULTI_KIND -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    chk(any("VAL_SPLIT" in ln and "32 .out files print an ON line; 32 are CSV rows, every one listed with its kind: True" in ln
            for ln in line_of(out, "  completeness")),
        "C41 the completeness line names VAL_SPLIT: 32 ON runs, 32 CSV rows, every one listed",
        repr(line_of(out, "  completeness")))
    chk(any("16 listed runs deviate on an ARGS value AND print an ON line" in ln and ln.endswith(": True")
            for ln in line_of(out, "  two-axis runs")),
        "C41 284's two-axis line counts the 16 W4 runs, True", repr(line_of(out, "  two-axis runs")))
    chk(line_of(out, L304) == [L304 + ": also VAL_SPLIT, 9 in all; no prefix of the 9 is a prefix of another: True"],
        "C41 ONE new `kinds scanned` line names VAL_SPLIT, 9 in all, no prefix collision", repr(line_of(out, L304)))
    chk(any("16 listed runs carry their listed ARGS value" in ln
            and "16 deviate from the standard, 0 are CSV rows in the standard cell" in ln
            for ln in line_of(out, "  ARGS witness")),
        "C41 the ARGS block reads the 16 W4 values (CIFAR-10: outside the standard cell, so none is a std-cell row)",
        repr(line_of(out, "  ARGS witness")))
    listed, corpus, logs, args, cells = merge5(cvl1_batch(), *ALL_PRIOR)
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out
        and all(ln.endswith(": True") for ln in line_of(out, "  kinds scanned") + line_of(out, "  two-axis runs")
                + line_of(out, "  two-kind runs") + line_of(out, "  multi-ARGS runs")),
        "C41 merged with cvt8 / cvt9 / cwd1 / cwd2 / csv1 / cwd5 / cmo1 / caw2 fixtures -> exit 0 PASS, every line True",
        "rc=%d %s" % (rc, show(out)))
    chk(any("17 listed runs deviate on an ARGS value AND print an ON line" in ln for ln in line_of(out, "  two-axis runs"))
        and ("  multi-kind runs (CORRECTIONS 251): those runs by the number of kinds MULTI_KIND registers for them: "
             "2 kinds 8, 3 kinds 4") in out.splitlines(),
        "C41 merged: the two-axis line counts cwd5's CARW2 + cvl1's 16; 251's multi-kind line is unchanged",
        repr(line_of(out, "  two-axis runs") + line_of(out, "  multi-kind runs")))

    print("C42 every VAL_SPLIT corruption fails, each named")
    w1, w4 = ("chW1", 185), ("kLW4", 186)
    for tag, arm_seed, lines, msg in [
            ("a", w1, ["VAL_SPLIT: off"], "witness ['VAL_SPLIT: off'] != listed"),
            ("b", w1, [VS_ON_303], "split_seed=303"),
            ("c", w1, [VS_ON_4999], "n_val=4999"),
            ("d", w1, [VS_ON, VS_ON], "!= listed"),
            ("g", w4, [VS_ON_303], "registered with VAL_SPLIT ON but prints"),
            ("h", w4, ["VAL_SPLIT: off"], "registered with VAL_SPLIT ON but prints")]:
        listed, corpus, logs, args, cells = cvl1_batch()
        key = CVL1[arm_seed]
        logs[key] = lines + VS_VAL_LINES
        rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
        chk(rc == 1 and any(("%s-%s.out" % key) in f and msg in f for f in fails(out)),
            "C42%s %s prints %r -> exit 1, named with %r" % (tag, key[0], [ln[:34] for ln in lines], msg), show(out))
    for tag, arm_seed, msg in [("e", w1, "is a CSV row printing an ON VAL_SPLIT line but is NOT listed"),
                               ("k", w4, "is a CSV row printing an ON VAL_SPLIT line but is NOT listed")]:
        listed, corpus, logs, args, cells = cvl1_batch()
        key = CVL1[arm_seed]
        rc, out = run_check([r for r in listed if r[:2] != key], corpus, logs, args=args, cells=cells)
        chk(rc == 1 and any(("%s-%s.out" % key) in f and msg in f for f in fails(out)),
            "C42%s %s dropped from the list -> exit 1, named (completeness)" % (tag, key[0]), show(out))
    listed, corpus, logs, args, cells = cvl1_batch("VAL_SPLIT")
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and sum(1 for f in fails(out) if "deviates on ARGS_WD_BASE but is listed with a VAL_SPLIT witness" in f) == 16,
        "C42f the 16 W4 runs listed by their VAL_SPLIT line (the REVERSE listing) -> exit 1, each named: no ARGS escape",
        show(out)[:300])
    for tag, wd, msg in [("i", "0.1", "does not deviate"), ("j", "1e-3", "ARGS witness")]:
        listed, corpus, logs, args, cells = cvl1_batch()
        key = CVL1[w4]
        args[key] = cvl1_args(w4[0], w4[1], wd=wd)
        rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
        chk(rc == 1 and any(("%s-%s.out" % key) in f and msg in f for f in fails(out)),
            "C42%s %s's own ARGS line says --weight-decay-base %s -> exit 1, named" % (tag, key[0], wd), show(out))
    for by, msg in [("VAL_SPLIT", "deviates on ARGS_WD_BASE but is listed with a VAL_SPLIT witness"),
                    ("ARGS_WD_BASE", "prints an ON VAL_SPLIT line but is listed with a ARGS_WD_BASE witness")]:
        listed, corpus, logs, args, cells = cvl1_batch()
        key = CVL1[w1]
        args[key] = cvl1_args(w1[0], w1[1], wd="5e-4")        # a W1 arm has NO MULTI_KIND entry
        listed = [r if r[:2] != key else key + ({"VAL_SPLIT": VS_ON, "ARGS_WD_BASE": W_WD5E4}[by],) for r in listed]
        rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
        chk(rc == 1 and any(("%s-%s.out" % key) in f and msg in f for f in fails(out)),
            "C42l an UNREGISTERED two-axis run (a W1 arm at wd 5e-4) listed by %s -> exit 1, named" % by, show(out))
    listed, corpus, logs, args, cells = cvl1_batch()
    extra = ("cvl1-chW1-s188", "5099901")                    # an unused seed: an ON .out nobody ingested or listed
    logs[extra] = [VS_ON] + VS_VAL_LINES
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("cvl1-chW1-s188-5099901.out is NOT listed but its witness is" in f for f in fails(out)),
        "C42m a not-yet-ingested ON .out of the listed batch, unlisted -> exit 1, named (the batch rule)", show(out))
    listed, corpus, logs, args, cells = cvl1_batch()
    other = ("syn4-VS-s1", "5099902")                        # an ON corpus row of ANOTHER batch
    corpus.append(other)
    logs[other] = [VS_ON]
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("syn4-VS-s1-5099902.out is a CSV row printing an ON VAL_SPLIT line but is NOT listed" in f
                        for f in fails(out)),
        "C42n an ON VAL_SPLIT corpus row of an unlisted batch -> exit 1, named (completeness is corpus-wide)", show(out))
    listed, corpus, logs, args, cells = cvl1_batch()
    plain = ("cvl1-PLAIN-s184", "5099903")                   # an `off` run of the listed batch
    corpus.append(plain)
    logs[plain] = ["VAL_SPLIT: off"]
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C42o an unlisted `VAL_SPLIT: off` run of the listed batch -> exit 0 PASS (off runs are not required)",
        "rc=%d %s" % (rc, show(out)))
    logs[plain] = []
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("cvl1-PLAIN-s184-5099903.out is NOT listed but its witness is []" in f for f in fails(out)),
        "C42o ... and the same run printing NO VAL_SPLIT line -> exit 1, named", show(out))

    print("C43 the prefix proof, the VAL: lines, and patch_valsplit.py's line forms")
    NINE = ["VOTE_W", "BETA_HOLD", "GROUP_HOLD", "COMP_HOLD", "REST_HOLD", "WINDOW_HOLD", "DECAY_MASK", "SHADOW_VOTE",
            "VAL_SPLIT"]  # literal, not read from the module
    kinds9 = [k for k, _off in CE.KINDS[:9]]   # CORRECTIONS 308: was `CE.KINDS`; 304's nine, not every kind (C49 proves the ten)
    names11 = kinds9 + [k for k, _f, _s in CE.ARGS_KINDS]
    chk(kinds9 == NINE and not [(a, b) for a in names11 for b in names11 if a != b and a.startswith(b)],
        "C43 no name of the 9 line kinds + 2 ARGS kinds is a prefix of another", repr(names11))
    chk([k for k in kinds9 if k[0] == "V"] == ["VOTE_W", "VAL_SPLIT"] and "VOTE_W"[1] != "VAL_SPLIT"[1],
        "C43 VAL_SPLIT and VOTE_W share the first letter and diverge at the second (so neither prefixes the other)")
    chk(not [k for k in kinds9 if VS_VAL_LINES[0].startswith(k) or "VAL:".startswith(k) or "ARGS:".startswith(k)
             or k.startswith("ARGS")]
        and CE._ARGS_RE.match(VS_VAL_LINES[0]) is None and CE._ARGS_RE.match(VS_ON) is None
        and CE.kind_of(VS_ON) == "VAL_SPLIT" and CE.kind_of("VAL_SPLIT: off") == "VAL_SPLIT"
        and CE.kind_of(VS_VAL_LINES[0]) is None,
        "C43 a `VAL:` line starts with no KINDS prefix and is no ARGS line; kind_of reads VAL_SPLIT's lines as VAL_SPLIT only")
    tmp = tempfile.mkdtemp(prefix="ce_prefix_test_")
    try:
        p = os.path.join(tmp, "x.out")
        eighteen = ([VW_MUTE, BH_TRI, GH_TRI, CH_REC, RH_REC, WH_EARLY, DM_NORMSCALE, SV_SHADOWLOW, VS_ON]
                    + ["%s: off" % k for k in NINE])
        open(p, "w").write("\n".join(eighteen[:9] + VS_VAL_LINES + eighteen[9:]) + "\n")
        got = CE.witness_lines(p)
        # CORRECTIONS 308: was `sorted(got) == sorted(NINE)`; witness_lines now also returns DECAY_ROUTE's key, empty on
        # these lines -- so the kinds that COLLECT a line are still exactly 304's nine.
        chk(sorted(k for k in got if got[k]) == sorted(NINE)
            and all(got[k] == [ln for ln in eighteen if ln.split(":")[0] == k] for k in NINE)
            and not [ln for v in got.values() for ln in v if ln.startswith("VAL:")],
            "C43 witness_lines puts each of 18 lines (one on, one off per kind) under its own kind; no `VAL:` line is taken",
            repr(sorted(got)))
    finally:
        shutil.rmtree(tmp)
    src = open(os.path.join(REPO, "patches", "patch_valsplit.py")).read()
    lits = re.findall(r"'((?:%s): [^']*)'" % "|".join(sorted(NINE)), src)
    chk("VAL_SPLIT: off" in lits and any(l.startswith("VAL_SPLIT: on dataset=") for l in lits)
        and all(l.startswith("VAL_SPLIT: ") for l in lits),
        "C43 patch_valsplit.py prints only `VAL_SPLIT: off` / `VAL_SPLIT: on dataset=...` witness lines",
        repr(sorted(set(lits)))[:300])
    chk("'VAL: epoch %d val_acc" in src or "'VAL: epoch " in src,
        "C43 patch_valsplit.py's per-epoch line starts `VAL: epoch` (the form this test's VAL lines copy)")

    print("C44 the registry: KINDS, MULTI_KIND's cvl1 entries against cvl1_design, and the print lines")
    # CORRECTIONS 308: was `CE.KINDS[8:] == [...]`; KINDS now also holds DECAY_ROUTE (C50 owns the total and the added entry)
    chk(CE.KINDS[:8] == [(k, "%s: off" % k) for k in NINE[:8]] and CE.KINDS[8:9] == [("VAL_SPLIT", "VAL_SPLIT: off")]
        and getattr(CE, "KINDS_AT_269", None) == 8 and CE.KINDS_AT_251 == 6,
        "C44 KINDS = 269's eight unchanged + VAL_SPLIT, appended; KINDS_AT_269 == 8", repr(CE.KINDS[8:]))
    mkv = dict((k, v) for k, v in CE.MULTI_KIND.items() if k[0] == "cvl1")
    chk(sorted(mkv) == sorted(("cvl1", "%sW4" % g) for g, _s in CVL1_GRAINS)
        and all(v == {"VAL_SPLIT": VS_ON} for v in mkv.values())
        # CORRECTIONS 308: was `k[0] != "cvl1"`; 308's cai1 / crd1 entries are excluded too (C50 owns them)
        and len([k for k in CE.MULTI_KIND if k[0] not in ("cvl1", "cai1", "crd1")]) == 16,
        "C44 MULTI_KIND gains exactly the 4 cvl1 W4 entries, each registering exactly VAL_SPLIT == this test's VS_ON; "
        "the 16 earlier entries are unchanged in number", repr(sorted(mkv)))
    chk(sorted(CE.MULTI_ARGS) == [("caw2", "XL"), ("caw2", "XS")] and len(CE.ARGS_KINDS) == 2,
        "C44 MULTI_ARGS and ARGS_KINDS are unchanged")
    try:
        import cvl1_design as V1                  # the registered design; imported by the test only
        chk(V1.witness_on() == VS_ON, "C44 VS_ON == cvl1_design.witness_on(), byte for byte")
        chk(sorted(V1.ARGS_DEVIATING) == sorted(a for _b, a in mkv)
            and all(V1.WD[a] == "5e-4" for a in V1.ARGS_DEVIATING)
            and sorted(V1.RUNS) == sorted(CVL1) and V1.NJOBS == 32 and V1.N_EXCLUSION_ROWS == 32,
            "C44 MULTI_KIND's cvl1 arms == cvl1_design.ARGS_DEVIATING (the W4 arms, wd 5e-4); the fixture's 32 runs == RUNS",
            repr(V1.ARGS_DEVIATING))
        chk(all("ARGS: " + cvl1_args(a, s) == V1.args_line(a, s, "/home/s5014158/metaopt/runs/cvl1") for a, s in V1.RUNS),
            "C44 this test's 32 cvl1 ARGS payloads == cvl1_design.args_line, byte for byte")
    except Exception as ex:
        chk(False, "C44 cvl1_design imports and MULTI_KIND holds its W4 witness", "%s: %s" % (type(ex).__name__, ex))
    b = wd5_batch()
    rc, out = run_check(*b[:3], args=b[3], cells=b[4])
    # CORRECTIONS 308: was `if not ln.startswith(L304)`; 308's two added lines are dropped too (C50 proves they are the only two)
    kept = "".join(ln + "\n" for ln in out.split("\n")[:-1] if not ln.startswith((L304,) + L308S))
    chk(rc == 0 and hashlib.sha256(kept.encode()).hexdigest()
        == "0273bd078abe3d81f88b3a0369d25fd6a3aa529dcd295b61db760b9ee62ef8af" and len(line_of(out, L304)) == 1,
        "C44 on 284's cwd5 fixture `--check --runs` gains exactly ONE line; every other byte == 294's module output",
        hashlib.sha256(kept.encode()).hexdigest()[:16])
    b = merge5(*ALL_PRIOR)
    rc, out = run_check(*b[:3], args=b[3], cells=b[4])
    # CORRECTIONS 308: was `if not ln.startswith(L304)`; 308's two added lines are dropped too (C50 proves they are the only two)
    kept = "".join(ln + "\n" for ln in out.split("\n")[:-1] if not ln.startswith((L304,) + L308S))
    chk(rc == 0 and hashlib.sha256(kept.encode()).hexdigest()
        == "a472afe0f7c3c6890b8a9c68b90e3ba6324857cec3ab4a60420739bbdb95666c"
        and ("  kinds scanned (CORRECTIONS 269): also DECAY_MASK / SHADOW_VOTE, 8 in all; no prefix of the 8 is a prefix "
             "of another: True") in out.splitlines(),
        "C44 on every earlier kind's fixture merged, ONE line is added and 269's `kinds scanned` line is unchanged",
        hashlib.sha256(kept.encode()).hexdigest()[:16])
    l5, c5, g5, a5, e5 = merge5(cmo_batch())
    rc, out = run_check(l5, c5, g5, args=a5, cells=e5, with_runs=False)
    chk(rc == 0 and hashlib.sha256(out.encode()).hexdigest()
        == "8e67462ac2950669b206eacdfbe6f3cdf4b6790f448401d29b62a7663d7e121b",
        "C44 without --runs nothing changes: cmo1's no-runs output == 284's / 294's module output, byte for byte")

    print("C45 csh1's gamma: a CSV cell-key column, so NO ARGS kind (301.3), and the rows it does owe")
    import aggregate as AG                        # the ingest's own parser; imported by the test only
    chk("gamma" in CE.CELLKEYS and "gamma" in AG.FIELDS, "C45 `gamma` is one of CELLKEYS and of aggregate.py's FIELDS")
    chk(not [f for _k, f, _s in CE.ARGS_KINDS if "gamma" in f] and not [k for k in CE.KINDS if "GAMMA" in k[0]],
        "C45 no ARGS kind or line kind names gamma (none is needed)")
    tmp = tempfile.mkdtemp(prefix="ce_gamma_test_")
    try:
        got = {}
        for arm, grain, g, job in CSH1_ARMS:
            p = os.path.join(tmp, "csh1-%s-s180-%s.out" % (arm, job))
            open(p, "w").write("NODE=synthetic\nARGS: %s\nENV: AUGMENT=1 BETA_CLIP=-15:-2.3026 HIER=none LAM=na "
                               "ETA_RATIO=na\nEpoch 0, Train Accuracy: 1.0, Test Accuracy: 1.0\n" % (CSH1_ARGS % (g, grain, arm)))
            r = AG.parse_out(p)
            got[arm] = (r or {}).get("gamma")
        chk(got == dict((a, g) for a, _gr, g, _j in CSH1_ARMS),
            "C45 aggregate.parse_out writes each csh1 arm's --gamma token into the row, verbatim", repr(got))
    finally:
        shutil.rmtree(tmp)
    base = dict(CSV_STD, network="ResNet18_c100", plateau5="50.0")
    rows = [dict(base, gamma=g, plateau5=v) for g, v in (("1", "50.0"), ("1", "52.0"), ("0.999685", "70.0"),
                                                        ("0.999685", "72.0"), ("0.99941", "60.0"), ("0.99941", "62.0"))]
    sd, df, nc = CE._pooled(rows, "ResNet18_c100")
    chk(nc == 3 and df == 3 and abs(sd - math.sqrt(2.0)) < 1e-12,
        "C45 _pooled keeps gamma 1 / 0.999685 / 0.99941 rows of one otherwise equal cell apart (3 cells, sd sqrt 2)",
        "nc=%d df=%d sd=%r" % (nc, df, sd))
    try:
        import csh1_design as H1
        chk(all(CSH1_ARGS % (g, gr, a) == H1.args_string(a, 180, "/home/s5014158/metaopt/runs/csh1")
                for a, gr, g, _j in CSH1_ARMS) and sorted(H1.ARMS) == sorted(a for a, _g, _t, _j in CSH1_ARMS)
            and sorted(set(g for _a, _gr, g, _j in CSH1_ARMS)) == sorted(H1.GAMMA_TOKEN.values())
            and list(H1.OFF_LINES) == CSH1_OFF,
            "C45 this test's 6 csh1 payloads == csh1_design.args_string; gamma tokens == GAMMA_TOKEN; off lines == OFF_LINES")
    except Exception as ex:
        chk(False, "C45 csh1_design imports", "%s: %s" % (type(ex).__name__, ex))
    listed, corpus, logs, args, cells = csh1_batch()
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out
        and any("6 listed runs carry their listed ARGS value" in ln and "6 are CSV rows in the standard cell, every one "
                "listed: True" in ln for ln in line_of(out, "  ARGS witness")),
        "C45 a csh1-style batch listed by ARGS_WD_BASE=5e-4 ONLY (301.3's plan) -> exit 0 PASS, 6 standard-cell rows",
        "rc=%d %s" % (rc, show(out)))
    key = ("csh1-GMS-s180", "5080647")
    rc, out = run_check([r for r in listed if r[:2] != key], corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("csh1-GMS-s180-5080647.out is a CSV row in the standard cell whose ARGS deviates" in f
                        for f in fails(out)),
        "C45 a dropped gamma<1 row still FAILs (its wd 5e-4 is the axis the list must carry)", show(out))

    # ---- CORRECTIONS 308 ------------------------------------------------------------------------------------
    L308 = "  kinds scanned (CORRECTIONS 308)"
    LDR = "  decay-route runs (CORRECTIONS 308)"
    L308_TEXT = L308 + ": also DECAY_ROUTE, 10 in all; no prefix of the 10 is a prefix of another: True"
    L304_TEXT = L304 + ": also VAL_SPLIT, 9 in all; no prefix of the 9 is a prefix of another: True"
    MK_DR = "is registered with DECAY_ROUTE ON but prints"
    ARMS_DR = "not its arm's registered line (DECAY_ROUTE_ARMS)"
    print("C46 cai1-style (32 two-axis) and crd1-style (12 one-kind + 6 two-axis) DECAY_ROUTE batches pass")
    listed, corpus, logs, args, cells = cai1_batch()
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C46 cai1: 32 runs listed by ARGS_WD_BASE=0 with the DECAY_ROUTE line in MULTI_KIND -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    chk(any("DECAY_ROUTE" in ln and "32 .out files print an ON line; 32 are CSV rows, every one listed with its kind: True"
            in ln for ln in line_of(out, "  completeness")),
        "C46 cai1: the completeness line names DECAY_ROUTE, 32 ON runs, 32 CSV rows", repr(line_of(out, "  completeness")))
    chk(any("32 listed runs deviate on an ARGS value AND print an ON line" in ln and ln.endswith(": True")
            for ln in line_of(out, "  two-axis runs")),
        "C46 cai1: 284's two-axis line counts the 32 runs, True", repr(line_of(out, "  two-axis runs")))
    chk(line_of(out, L308) == [L308_TEXT] and line_of(out, L304) == [L304_TEXT],
        "C46 cai1: ONE new `kinds scanned` line names DECAY_ROUTE, 10 in all, True; 304's line unchanged",
        repr(line_of(out, "  kinds scanned")))
    chk(len(line_of(out, LDR)) == 1 and line_of(out, LDR)[0].startswith(LDR + ": 32 listed runs")
        and line_of(out, LDR)[0].endswith(": True"),
        "C46 cai1: the decay-route line counts 32 registered-arm runs, True", repr(line_of(out, LDR)))
    chk(any("32 listed runs carry their listed ARGS value" in ln
            and "32 deviate from the standard, 0 are CSV rows in the standard cell" in ln
            for ln in line_of(out, "  ARGS witness")),
        "C46 cai1: the ARGS block reads the 32 wd-0 values (CIFAR-10: outside the standard cell)",
        repr(line_of(out, "  ARGS witness")))
    listed, corpus, logs, args, cells = crd1_batch()
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out,
        "C46 crd1: 12 SR* / TR* listed by their DECAY_ROUTE line, 6 AI* by ARGS_WD_BASE=0 (18 rows) -> exit 0 PASS",
        "rc=%d %s" % (rc, show(out)))
    chk(any("DECAY_ROUTE" in ln and "18 .out files print an ON line; 18 are CSV rows, every one listed with its kind: True"
            in ln for ln in line_of(out, "  completeness")),
        "C46 crd1: completeness 18 ON / 18 CSV rows, every one listed", repr(line_of(out, "  completeness")))
    chk(any("6 listed runs deviate on an ARGS value AND print an ON line" in ln and ln.endswith(": True")
            for ln in line_of(out, "  two-axis runs")),
        "C46 crd1: the two-axis line counts the 6 AI* runs, True", repr(line_of(out, "  two-axis runs")))
    chk(any("6 listed runs carry their listed ARGS value" in ln
            and "6 are CSV rows in the standard cell, every one listed: True" in ln for ln in line_of(out, "  ARGS witness")),
        "C46 crd1: the 6 AI* runs are standard-cell ARGS rows (the mechanism cell), every one listed",
        repr(line_of(out, "  ARGS witness")))
    chk(len(line_of(out, LDR)) == 1 and line_of(out, LDR)[0].startswith(LDR + ": 18 listed runs")
        and line_of(out, LDR)[0].endswith(": True"),
        "C46 crd1: the decay-route line counts 18, True", repr(line_of(out, LDR)))
    ALL_308 = (cvl1_batch(),) + ALL_PRIOR
    listed, corpus, logs, args, cells = merge5(cai1_batch(), crd1_batch(), *ALL_308)
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out
        and all(ln.endswith(": True") for ln in line_of(out, "  kinds scanned") + line_of(out, "  two-axis runs")
                + line_of(out, "  two-kind runs") + line_of(out, "  multi-ARGS runs") + line_of(out, LDR)),
        "C46 merged with cvl1 and every earlier kind's fixture -> exit 0 PASS, every line True",
        "rc=%d %s" % (rc, show(out)))
    chk(any("55 listed runs deviate on an ARGS value AND print an ON line" in ln for ln in line_of(out, "  two-axis runs"))
        and line_of(out, LDR)[0].startswith(LDR + ": 50 listed runs")
        and ("  multi-kind runs (CORRECTIONS 251): those runs by the number of kinds MULTI_KIND registers for them: "
             "2 kinds 8, 3 kinds 4") in out.splitlines(),
        "C46 merged: two-axis 55 (cwd5 1 + cvl1 16 + cai1 32 + crd1 6); decay-route 50; 251's line unchanged",
        repr(line_of(out, "  two-axis runs") + line_of(out, LDR)))

    print("C47 every DECAY_ROUTE corruption fails, each named (wrong mode, wrong LAMBDA, the listing rules)")
    srs, srl, trs, trl = CRD1[("SRS", 197)], CRD1[("SRL", 196)], CRD1[("TRS", 197)], CRD1[("TRL", 196)]
    ais, ais8 = CRD1[("AIS", 196)], CRD1[("AIS", 198)]
    k4, c5, n5 = CAI1[("kLI4", 194)], CAI1[("chI5", 192)], CAI1[("ndI5", 193)]
    cases = [
        ("a", "crd1", srs, [DR_TR], None, ["!= listed", ARMS_DR]),                       # wrong MODE, row correct
        ("b", "crd1", srs, [DR_TR], DR_TR, [ARMS_DR]),                                  # wrong MODE, row copied it
        ("c", "cai1", k4, [DR_I5], None, [MK_DR]),                                      # wrong LAMBDA (the other rung)
        ("d", "crd1", ais8, [DR_AI.replace("lambda=0.000315", "lambda=0.0005")], None, [MK_DR]),
        ("e", "cai1", c5, [DR_I5.replace("lambda_f32=4.999999873689376e-05", "lambda_f32=5e-05")], None, [MK_DR]),
        ("f", "crd1", trl, [DR_TR.replace("gamma=1.0", "gamma=0.97")], None, ["!= listed", ARMS_DR]),
        ("g1", "crd1", srl, [DR_OFF], None, ["witness ['DECAY_ROUTE: off'] != listed", ARMS_DR]),
        ("g2", "cai1", n5, [DR_OFF], None, [MK_DR]),
        ("h", "crd1", srs, [DR_SR, DR_SR], None, ["!= listed", ARMS_DR]),
        ("i1", "crd1", ais, [], None, [MK_DR]),
        ("i2", "crd1", trs, [], None, ["witness [] != listed", ARMS_DR]),
        ("t", "crd1", srs, [DR_SR, "DECAY_ROUTE=shrink_only"], None, ["!= listed", ARMS_DR])]  # an echo would be collected
    for tag, batch, key, lines, row_w, msgs in cases:
        listed, corpus, logs, args, cells = cai1_batch() if batch == "cai1" else crd1_batch()
        logs[key] = lines + ([CRD1_PT % "scalar"] if batch == "crd1" else [])
        if row_w is not None:
            listed = [r if r[:2] != key else key + (row_w,) for r in listed]
        rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
        chk(rc == 1 and all(any(("%s-%s.out" % key) in f and m in f for f in fails(out)) for m in msgs)
            and (row_w is None or all(ARMS_DR in f for f in fails(out))),
            "C47%s %s prints %r%s -> exit 1, named with %r" % (tag, key[0], [ln[:48] for ln in lines],
                                                               " (TSV row copies it)" if row_w else "", msgs), show(out))
    for tag, batch, key, msgs in [
            ("j", "cai1", CAI1[("chI4", 195)], ["is a CSV row printing an ON DECAY_ROUTE line but is NOT listed",
                                                "is an unlisted run of a listed batch whose ARGS deviates"]),
            ("k", "crd1", CRD1[("AIS", 197)], ["is a CSV row printing an ON DECAY_ROUTE line but is NOT listed",
                                               "is a CSV row in the standard cell whose ARGS deviates"]),
            ("l", "crd1", CRD1[("TRL", 198)], ["is a CSV row printing an ON DECAY_ROUTE line but is NOT listed"])]:
        listed, corpus, logs, args, cells = cai1_batch() if batch == "cai1" else crd1_batch()
        rc, out = run_check([r for r in listed if r[:2] != key], corpus, logs, args=args, cells=cells)
        chk(rc == 1 and all(any(("%s-%s.out" % key) in f and m in f for f in fails(out)) for m in msgs),
            "C47%s %s dropped from the list -> exit 1, named %d way(s)" % (tag, key[0], len(msgs)), show(out))
    for tag, b, n in [("m1", cai1_batch("DECAY_ROUTE"), 32), ("m2", crd1_batch("DECAY_ROUTE"), 6)]:
        rc, out = run_check(*b[:3], args=b[3], cells=b[4])
        chk(rc == 1 and sum(1 for f in fails(out) if "deviates on ARGS_WD_BASE but is listed with a DECAY_ROUTE witness"
                            in f) == n,
            "C47%s the %d two-axis runs listed by their DECAY_ROUTE line (the REVERSE listing) -> exit 1, each named"
            % (tag, n), show(out)[:300])
    listed, corpus, logs, args, cells = crd1_batch()
    listed = listed + [CRD1[(a, s)] + (DR_AI,) for a in ("AIS", "AIL") for s in CRD1_SEEDS]
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("duplicate key in the list" in f for f in fails(out)) and len(listed) == 24,
        "C47n 307.9's owed list read as 24 rows (the 6 AI* runs listed twice) -> exit 1, `duplicate key in the list`",
        show(out)[:300])
    for by, msg in [("DECAY_ROUTE", "deviates on ARGS_WD_BASE but is listed with a DECAY_ROUTE witness"),
                    ("ARGS_WD_BASE", "prints an ON DECAY_ROUTE line but is listed with a ARGS_WD_BASE witness")]:
        listed, corpus, logs, args, cells = crd1_batch()
        key = CRD1[("SRS", 196)]
        args[key] = crd1_args("SRS", 196, wd="0")                  # an SR* arm has NO MULTI_KIND entry
        listed = [r if r[:2] != key else key + ({"DECAY_ROUTE": DR_SR, "ARGS_WD_BASE": W_WD0}[by],) for r in listed]
        rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
        chk(rc == 1 and any(("%s-%s.out" % key) in f and msg in f for f in fails(out)),
            "C47o an UNREGISTERED two-axis run (crd1 SRS at wd 0) listed by %s -> exit 1, named" % by, show(out))
    listed, corpus, logs, args, cells = cai1_batch()
    key = CAI1[("k01I5", 192)]
    args[key] = cai1_args("k01I5", 192, wd="0.1")
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any(("%s-%s.out" % key) in f and "does not deviate" in f for f in fails(out)),
        "C47p a cai1 run whose own ARGS line says --weight-decay-base 0.1 (the removed decay came back) -> exit 1, named",
        show(out))
    listed, corpus, logs, args, cells = crd1_batch()
    odd = ("crd1-XYZ-s196", "5099911")                          # a listed run of the route batch, arm not registered
    corpus.append(odd)
    logs[odd] = [DR_SR]
    args[odd] = crd1_args("SRS", 196).replace("crd1-SRS-s196", "crd1-XYZ-s196")
    cells[odd] = {"network": "ResNet18_c100"}
    listed.append(odd + (DR_SR,))
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("crd1-XYZ-s196-5099911.out" in f and "has no registered line (DECAY_ROUTE_ARMS)" in f
                        for f in fails(out)),
        "C47q a listed run of a route batch whose arm is not in DECAY_ROUTE_ARMS -> exit 1, named", show(out))
    listed, corpus, logs, args, cells = crd1_batch()
    extra = ("crd1-SRS-s199", "5099912")                        # an unused seed: an ON .out nobody ingested or listed
    logs[extra] = [DR_SR]
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("crd1-SRS-s199-5099912.out is NOT listed but its witness is" in f for f in fails(out)),
        "C47r a not-yet-ingested ON .out of the listed batch, unlisted -> exit 1, named (the batch rule)", show(out))
    listed, corpus, logs, args, cells = crd1_batch()
    other = ("syn5-DR-s1", "5099913")                           # an ON corpus row of an UNLISTED batch
    corpus.append(other)
    logs[other] = [DR_SR]
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("syn5-DR-s1-5099913.out is a CSV row printing an ON DECAY_ROUTE line but is NOT listed" in f
                        for f in fails(out)),
        "C47s an ON DECAY_ROUTE corpus row of an unlisted batch -> exit 1, named (completeness is corpus-wide)", show(out))

    print("C48 `DECAY_ROUTE: off` (every run of the patched tree, switch unset) is not required; a missing line is")
    listed, corpus, logs, args, cells = crd1_batch()
    plain = ("crd1-OFF-s196", "5099914")                        # an `off` run of the listed batch, at the standard 0.1
    corpus.append(plain)
    logs[plain] = [DR_OFF]
    args[plain] = crd1_args("SRS", 196).replace("crd1-SRS-s196", "crd1-OFF-s196")
    cells[plain] = {"network": "ResNet18_c100"}
    other = ("syn6-OFF-s1", "5099915")                          # an `off` corpus run of an UNLISTED batch, beside a mask line
    corpus.append(other)
    logs[other] = ["DECAY_MASK: off", DR_OFF]
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 0 and "VERDICT: PASS" in out
        and any("18 .out files print an ON line; 18 are CSV rows" in ln for ln in line_of(out, "  completeness")),
        "C48 unlisted `DECAY_ROUTE: off` runs (in the listed batch, and in an unlisted one) -> exit 0 PASS, not counted ON",
        "rc=%d %s" % (rc, show(out)))
    logs[plain] = []
    rc, out = run_check(listed, corpus, logs, args=args, cells=cells)
    chk(rc == 1 and any("crd1-OFF-s196-5099914.out is NOT listed but its witness is []" in f for f in fails(out))
        and not any("syn6-OFF-s1" in f for f in fails(out)),
        "C48 ... the same run of the listed batch printing NO DECAY_ROUTE line -> exit 1, named; the other batch's is not",
        show(out))
    tmp = tempfile.mkdtemp(prefix="ce_prefix_test_")
    try:
        p = os.path.join(tmp, "x.out")
        four = ["DECAY_MASK: off", DR_OFF, DM_NORMSCALE, DR_SR]
        open(p, "w").write("\n".join(four) + "\n")
        got = CE.witness_lines(p)
        chk(got.get("DECAY_MASK") == ["DECAY_MASK: off", DM_NORMSCALE] and got.get("DECAY_ROUTE") == [DR_OFF, DR_SR],
            "C48 witness_lines puts two DECAY_MASK and two DECAY_ROUTE lines each under its own kind only",
            repr((got.get("DECAY_MASK"), got.get("DECAY_ROUTE"))))
    finally:
        shutil.rmtree(tmp)

    print("C49 the prefix proof (DECAY_ROUTE vs DECAY_MASK), the line forms, and the literals against the designs")
    TEN = NINE + ["DECAY_ROUTE"]   # literal, not read from the module
    kinds10 = [k for k, _off in CE.KINDS]
    names12 = kinds10 + [k for k, _f, _s in CE.ARGS_KINDS]
    chk(kinds10 == TEN and not [(a, b) for a in names12 for b in names12 if a != b and a.startswith(b)],
        "C49 no name of the 10 line kinds + 2 ARGS kinds is a prefix of another", repr(names12))
    pre = os.path.commonprefix(["DECAY_ROUTE", "DECAY_MASK"])
    chk(pre == "DECAY_" and "DECAY_ROUTE"[6] == "R" and "DECAY_MASK"[6] == "M"
        and not "DECAY_ROUTE".startswith("DECAY_MASK") and not "DECAY_MASK".startswith("DECAY_ROUTE"),
        "C49 DECAY_ROUTE and DECAY_MASK share `DECAY_` and diverge at index 6 (R / M): neither is a prefix of the other")
    chk(CE.kind_of(DR_SR) == "DECAY_ROUTE" and CE.kind_of(DR_OFF) == "DECAY_ROUTE" and CE.kind_of(DR_I5) == "DECAY_ROUTE"
        and CE.kind_of(DM_NORMSCALE) == "DECAY_MASK" and CE.kind_of("DECAY_MASK: off") == "DECAY_MASK"
        and CE.kind_of("DECAY_ROUTE=shrink_only") is None and CE._ARGS_RE.match(DR_SR) is None
        and not [k for k in kinds10 if "ARGS:".startswith(k) or k.startswith("ARGS")],
        "C49 kind_of reads each DECAY_ line as its own kind; an `=` echo names no kind; no line is an ARGS line")
    tmp = tempfile.mkdtemp(prefix="ce_prefix_test_")
    try:
        p = os.path.join(tmp, "x.out")
        twenty = ([VW_MUTE, BH_TRI, GH_TRI, CH_REC, RH_REC, WH_EARLY, DM_NORMSCALE, SV_SHADOWLOW, VS_ON, DR_AI]
                  + ["%s: off" % k for k in TEN])
        open(p, "w").write("\n".join(twenty) + "\n")
        got = CE.witness_lines(p)
        chk(sorted(got) == sorted(TEN) and all(got[k] == [ln for ln in twenty if ln.split(":")[0] == k] for k in TEN),
            "C49 witness_lines puts each of 20 lines (one on, one off per kind) under its own kind only", repr(sorted(got)))
    finally:
        shutil.rmtree(tmp)
    src = open(os.path.join(REPO, "patches", "patch_decayroute.py")).read()
    lits = re.findall(r"'((?:%s): [^']*)'" % "|".join(sorted(TEN)), src)
    chk("DECAY_ROUTE: off" in lits and any(l.startswith("DECAY_ROUTE: on mode=") for l in lits)
        and all(l.startswith("DECAY_ROUTE: ") for l in lits),
        "C49 patch_decayroute.py prints only `DECAY_ROUTE: off` / `DECAY_ROUTE: on mode=...` witness lines",
        repr(sorted(set(lits)))[:300])
    try:
        import cai1_design as AI1                 # the registered designs; imported by the test only
        import crd1_design as RD1
        chk(AI1.witness_on("I5") == DR_I5 and AI1.witness_on("I4") == DR_I4
            and all(RD1.dr_witness(a) == CRD1_DR[a] for a in RD1.ARMS) and sorted(RD1.ARMS) == sorted(CRD1_DR),
            "C49 this test's DECAY_ROUTE lines == cai1_design.witness_on / crd1_design.dr_witness, byte for byte")
    except Exception as ex:
        chk(False, "C49 cai1_design / crd1_design import", "%s: %s" % (type(ex).__name__, ex))
    import hashlib as _hl
    plog = os.environ.get("DECAYROUTE_PROOF_LOG", "")
    if plog and os.path.exists(plog):
        raw = open(plog, "rb").read()
        txt = raw.decode("utf-8", "replace").splitlines()
        rr2 = dict((m, [ln.split("registered string   ", 1)[1] for ln in txt
                        if ln.startswith("  PASS RR2 %s: ONE witness line == the registered string   " % m)])
                   for m in ("shrink_only", "trace_only", "alpha_indep:5e-05"))
        chk(_hl.sha256(raw).hexdigest() == "dc73dfbabf25fa01f2d0669a46fdb3202502e0e4a5851d4b4cce99146c8f25b1"
            and rr2 == {"shrink_only": [DR_SR], "trace_only": [DR_TR], "alpha_indep:5e-05": [DR_I5]}
            and not [ln for ln in txt if ln.startswith("DECAY_ROUTE")],
            "C49 REAL proof log 5081090 (dc73dfba...): its RR2 real-run witnesses == DR_SR / DR_TR / DR_I5, and no line of it "
            "starts with DECAY_ROUTE (every mention is indented)", repr(rr2)[:300])
    else:
        print("  SKIP C49 the real proof log (set DECAYROUTE_PROOF_LOG to a copy of $WS/runs/cdr1/proof_decayroute.log)")

    print("C50 the registry: KINDS, DECAY_ROUTE_ARMS, MULTI_KIND's cai1 / crd1 entries, and the print lines")
    chk(CE.KINDS[:9] == [(k, "%s: off" % k) for k in NINE] and CE.KINDS[9:] == [("DECAY_ROUTE", "DECAY_ROUTE: off")]
        and getattr(CE, "KINDS_AT_304", None) == 9 and CE.KINDS_AT_269 == 8 and CE.KINDS_AT_251 == 6,
        "C50 KINDS = 304's nine unchanged + DECAY_ROUTE, appended; KINDS_AT_304 == 9", repr(CE.KINDS[9:]))
    dra = getattr(CE, "DECAY_ROUTE_ARMS", None) or {}
    want_arms = dict([(("cai1", a), CAI1_DR[a]) for a in CAI1_DR] + [(("crd1", a), CRD1_DR[a]) for a in CRD1_DR])
    chk(dra == want_arms and len(dra) == 14,
        "C50 DECAY_ROUTE_ARMS == cai1's 8 + crd1's 6 arms, each with this test's line, byte for byte", repr(sorted(dra)))
    mkr = dict((k, v) for k, v in CE.MULTI_KIND.items() if k[0] in ("cai1", "crd1"))
    want_mk = dict([(("cai1", a), {"DECAY_ROUTE": CAI1_DR[a]}) for a in CAI1_DR]
                   + [(("crd1", a), {"DECAY_ROUTE": CRD1_DR[a]}) for a in ("AIS", "AIL")])
    chk(mkr == want_mk and len([k for k in CE.MULTI_KIND if k[0] not in ("cai1", "crd1")]) == 20,
        "C50 MULTI_KIND gains exactly cai1's 8 + crd1's AIS / AIL (the two-axis arms), each registering exactly "
        "DECAY_ROUTE; the 20 earlier entries are unchanged in number", repr(sorted(mkr)))
    chk(sorted(CE.MULTI_ARGS) == [("caw2", "XL"), ("caw2", "XS")] and len(CE.ARGS_KINDS) == 2,
        "C50 MULTI_ARGS and ARGS_KINDS are unchanged")
    try:
        chk(sorted(AI1.RUNS) == sorted(CAI1) and AI1.NJOBS == 32 and AI1.N_EXCLUSION_ROWS == 32 and AI1.WD_TOKEN == "0"
            and all("ARGS: " + cai1_args(a, s) == AI1.args_line(a, s, "/home/s5014158/metaopt/runs/cai1")
                    for a, s in AI1.RUNS),
            "C50 this test's 32 cai1 runs == cai1_design.RUNS and their ARGS payloads == args_line, byte for byte")
        chk(sorted((a, s) for a in RD1.ARMS for s in RD1.SEEDS) == sorted(CRD1) and RD1.NJOBS == 18
            and all(crd1_args(a, s) == RD1.args_string(a, s, "/home/s5014158/metaopt/runs/crd1")
                    for a in RD1.ARMS for s in RD1.SEEDS),
            "C50 this test's 18 crd1 runs == crd1_design's arms x seeds and their ARGS payloads == args_string")
        chk(sorted(a for a in RD1.ARMS if RD1.args_deviating_kinds(a)) == ["AIL", "AIS"]
            and all(RD1.args_deviating_kinds(a) == ("ARGS_WD_BASE",) for a in ("AIS", "AIL"))
            and sorted(a for _b, a in mkr if _b == "crd1") == ["AIL", "AIS"],
            "C50 MULTI_KIND's crd1 arms == the arms crd1_design names as ARGS-deviating (AIS / AIL, ARGS_WD_BASE only)")
    except Exception as ex:
        chk(False, "C50 the designs import and pin the fixture", "%s: %s" % (type(ex).__name__, ex))
    # the sha256 of 304's module output (analysis/corpus_exclusions.py 4846f2e4...) on the same two fixtures, whole
    SHA304 = {"wd5": "6f532634d02c0130cf33d0187f705382a28570f87bc189fe047ec4880db653ec", "all": "b30fa47bc3909fa1252cda45d66b967fce5b08946198f6d571196bcc581b4a3f"}
    for tag, b in [("wd5", wd5_batch()), ("all", merge5(*ALL_308))]:
        rc, out = run_check(*b[:3], args=b[3], cells=b[4])
        kept = "".join(ln + "\n" for ln in out.split("\n")[:-1] if not ln.startswith(L308S))
        chk(rc == 0 and _hl.sha256(kept.encode()).hexdigest() == SHA304[tag]
            and len(line_of(out, L308)) == 1 and len(line_of(out, LDR)) == 1 and line_of(out, L304) == [L304_TEXT]
            and line_of(out, LDR)[0].startswith(LDR + ": 0 listed runs"),
            "C50 on the %s fixture `--check --runs` gains exactly the TWO 308 lines (decay-route 0 runs); every other byte "
            "== 304's module output; 304's `kinds scanned` line unchanged" % tag, _hl.sha256(kept.encode()).hexdigest()[:16])
    l5, c5, g5, a5, e5 = merge5(cmo_batch())
    rc, out = run_check(l5, c5, g5, args=a5, cells=e5, with_runs=False)
    chk(rc == 0 and _hl.sha256(out.encode()).hexdigest()
        == "8e67462ac2950669b206eacdfbe6f3cdf4b6790f448401d29b62a7663d7e121b",
        "C50 without --runs nothing changes: cmo1's no-runs output == 284's / 294's / 304's module output, byte for byte")
    for tag, src, msg in [
            ("a", 'DECAY_ROUTE_ARMS[("crd1", "SRS")] = "DECAY_ROUTE: off"', "is not a well-formed DECAY_ROUTE ON line"),
            ("b", 'DECAY_ROUTE_ARMS[("crd1", "SRS")] = "DECAY_MASK: on base=SGDm wd=0.1"',
             "is not a well-formed DECAY_ROUTE ON line"),
            ("c", 'MULTI_KIND[("crd1", "AIS")] = {"DECAY_ROUTE": DECAY_ROUTE_ARMS[("cai1", "chI5")]}',
             "disagrees with DECAY_ROUTE_ARMS")]:
        rc, out = run_check(*merge5(cmo_batch())[:3], args=cmo_batch()[3], cells=cmo_batch()[4], with_runs=False,
                            module_append=src)
        chk(rc == 1 and any("DECAY_ROUTE" in f and msg in f for f in fails(out)),
            "C50%s a malformed DECAY_ROUTE registry entry FAILs without --runs, named with %r" % (tag, msg), show(out))

    print("\n%s" % ("ALL PASS" if not FAILED else "FAILURES: %d" % len(FAILED)))
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
