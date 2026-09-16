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
K01, HOLD, HOLDLOW = ("cvt9-k01-s90", "5000001"), ("cvt9-HOLDHIGH-s90", "5000002"), ("cvt9-HOLDLOW-s90", "5000003")
VK01, VMUTE = ("cvt8-k01-s78", "5000011"), ("cvt8-MUTE-s78", "5000012")


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
    chk(any("cvt9-HOLDHIGH-s90-5000002.out" in f and "P=5041" in f for f in fails(out)),
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
    chk(rc == 1 and "FAIL cvt8-MUTE-s78-5000012.out witness ['VOTE_W: off'] != listed" in fails(out),
        "C3 a VOTE_W mismatch still fails with the pre-239 message", show(out))

    print("C4  an ON corpus run absent from the TSV fails")
    listed, corpus, logs = vw_batch()
    corpus += [HOLD]
    logs[HOLD] = ["VOTE_W: off", BH_TRI]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and any("cvt9-HOLDHIGH-s90-5000002.out" in f and "BETA_HOLD" in f for f in fails(out)),
        "C4a BETA_HOLD run of a batch with NO listed row -> exit 1, named", "rc=%d %s" % (rc, show(out)))
    listed, corpus, logs = bh_batch()
    corpus += [HOLDLOW]
    logs[HOLDLOW] = ["VOTE_W: off", BH_FLOOR]
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and any("cvt9-HOLDLOW-s90-5000003.out" in f for f in fails(out)),
        "C4b one held run left out of a listed BETA_HOLD batch (it prints `VOTE_W: off`) -> exit 1, named",
        "rc=%d %s" % (rc, show(out)))
    listed, corpus, logs = bh_batch()
    corpus += [VK01, VMUTE]
    logs.update({VK01: ["VOTE_W: off"], VMUTE: [VW_MUTE]})
    rc, out = run_check(listed, corpus, logs)
    chk(rc == 1 and any("cvt8-MUTE-s78-5000012.out" in f and "VOTE_W" in f for f in fails(out)),
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
    chk(rc == 1 and any("cvt9-HOLDHIGH-s90-5000002.out" in f and "VOTE_W" in f for f in fails(out)),
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

    print("\n%s" % ("ALL PASS" if not FAILED else "FAILURES: %d" % len(FAILED)))
    raise SystemExit(1 if FAILED else 0)


if __name__ == "__main__":
    main()
