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


def run_check(listed, corpus, logs, with_runs=True):
    """listed: [(run, job, witness)]; corpus: [(run, job)]; logs: {(run, job): [lines]} -> (rc, stdout)."""
    tmp = tempfile.mkdtemp(prefix="ce_check_test_")
    try:
        os.makedirs(os.path.join(tmp, "analysis"))
        os.makedirs(os.path.join(tmp, "results"))
        shutil.copyfile(MODULE, os.path.join(tmp, "analysis", "corpus_exclusions.py"))
        with open(os.path.join(tmp, "results", "CORPUS-EXCLUSIONS.tsv"), "w") as f:
            f.write("# synthetic exclusion list\n" + "\t".join(tsv_header()) + "\n")
            for r in listed:
                f.write("\t".join(row(*r)) + "\n")
        with open(os.path.join(tmp, "results", "all_runs.csv"), "w") as f:
            f.write("run,job_id,network,superseded,collapsed,complete,plateau5\n")
            for run, job in corpus:
                f.write("%s,%s,PlainNet18_c100,0,0,1,\n" % (run, job))
        for (run, job), lines in logs.items():
            d = os.path.join(tmp, "runs", run.split("-")[0])
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "%s-%s.out" % (run, job)), "w") as f:
                f.write("ARGS: --network PlainNet18_c100 --seed 90\nNODE=synthetic\n")
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
    chk(CE.KINDS[4:] == [("REST_HOLD", "REST_HOLD: off"), ("WINDOW_HOLD", "WINDOW_HOLD: off")] and len(CE.KINDS) == 6,
        "C23 KINDS = 245's four + REST_HOLD + WINDOW_HOLD, appended", repr(CE.KINDS))
    kinds = [k for k, _off in CE.KINDS]
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
        chk(sorted(got) == sorted(SIX) and all(got[k] == [ln for ln in twelve if ln.split(":")[0] == k] for k in SIX),
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

    print("\n%s" % ("ALL PASS" if not FAILED else "FAILURES: %d" % len(FAILED)))
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
