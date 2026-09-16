"""Tests for analysis/c98b_reproduce.py (CORRECTIONS 224).

    python3 tests/test_c98b_reproduce.py          # ~2 min: runs c98 and c98b in full once each

What must hold for c98b to be a faithful successor of the registered c98_reproduce.py:
  T1  ENUMERATION.  Every assertion line c98 prints is printed by c98b; the 618 SCIENCE
      lines are byte-identical (value, paper value, PASS/FAIL, where); the 18 DRIFT lines
      differ only in the status token and the [DRIFT] tag; 618 + 18 == c98's site count.
  T2  A science failure still fails c98b (a Table 2 paper value perturbed -> exit 1).
  T3  Drift alone does not fail c98b (--corpus on the live corpus -> exit 0, drift listed).
  T4  Guard G1 fires when an append-only count falls below the paper (truncated corpus).
  T5  Guard G2 fires when the deficit is no longer positive.
  T6  A declared drift site that is not matched makes the declaration STALE -> exit 2.
Each case runs in a fresh interpreter: c98 keeps module-global FAILS/ASSERTED lists.
"""
import os, re, subprocess, sys, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AN = os.path.join(ROOT, "analysis")
PY = sys.executable
LINE = re.compile(r"^  .*\| paper .*\| (PASS|\*\*FAIL\*\*|DRIFT   ) ")


def sh(args):
    p = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def snippet(code):
    pre = "import sys; sys.path.insert(0, %r)\nimport c98b_reproduce as B\n" % AN
    return sh(["-c", pre + textwrap.dedent(code)])


def assertion_lines(out):
    return [l for l in out.splitlines() if LINE.match(l)]


def t1_enumeration():
    rc98, o98 = sh([os.path.join(AN, "c98_reproduce.py")])
    rcb, ob = sh([os.path.join(AN, "c98b_reproduce.py")])
    a98, ab = assertion_lines(o98), assertion_lines(ob)
    assert len(a98) == len(ab), (len(a98), len(ab))
    sci = [(x, y) for x, y in zip(a98, ab) if not y.endswith("[DRIFT]")]
    dr = [(x, y) for x, y in zip(a98, ab) if y.endswith("[DRIFT]")]
    assert all(x == y for x, y in sci), [p for p in sci if p[0] != p[1]][:3]
    norm = lambda s: re.sub(r"\| (PASS|\*\*FAIL\*\*|DRIFT   ) ", "| ", s).replace("   [DRIFT]", "")
    assert all(norm(x) == norm(y) for x, y in dr)
    m = re.search(r"ALL (\d+) SCIENCE CHECKS PASS  \((\d+) assertion sites = (\d+) science "
                  r"\+ (\d+) drift", ob)
    assert m, "c98b footer missing"
    n_sci, n_all, n_sci2, n_dr = map(int, m.groups())
    assert (n_sci, n_sci2, n_dr) == (len(sci), len(sci), len(dr)) == (618, 618, 18), m.groups()
    assert n_all == n_sci + n_dr
    # c98 prints a site-count census line naming the same total it asserted.
    n98_fail = sum(1 for x in a98 if "**FAIL**" in x)
    assert all("**FAIL**" not in x for x, _ in sci), "a science check fails in c98"
    assert rcb == 0, ob[-2000:]
    print("    c98 exit %d, %d assertion lines, %d FAIL (all drift); c98b exit %d, "
          "%d science identical + %d drift" % (rc98, len(a98), n98_fail, rcb, len(sci), len(dr)))


def t2_science_failure_fails():
    rc, out = snippet("""
        B.R.TABLE2["cc1"] = (9.999, 0.200)
        sys.exit(B.run(["--table2", "--no-census"]))
    """)
    assert rc == 1, (rc, out[-1500:])
    assert "science 43/44 PASS" in out, out[-800:]


def t3_drift_does_not_fail():
    rc, out = snippet("""sys.exit(B.run(["--corpus", "--no-census"]))""")
    assert rc == 0, (rc, out[-1500:])
    assert "DIFFERS" in out and "declaration OK" in out


def t4_guard_g1():
    rc, out = snippet("""
        orig = B.R.load
        def trunc(p):
            rows, adm = orig(p)
            keep = rows[:1000]; ids = {id(r) for r in keep}
            return keep, [r for r in adm if id(r) in ids]
        B.R.load = trunc
        sys.exit(B.run(["--corpus", "--no-census"]))
    """)
    assert rc == 1, (rc, out[-1500:])
    assert "G1  rows in results/all_runs.csv" in out, out[-1500:]


def t5_guard_g2():
    rc, out = snippet("""
        B.install()
        B._STATE["section"] = "competitiveness"
        B.chk("deficit", -0.05, 1.807, "x", "%.3f")
        assert [g[0] for g in B.GUARD_FAILS] == ["G2"], B.GUARD_FAILS
        assert B.R.FAILS == [], B.R.FAILS
        B.chk("D  cc1", 9.0, 0.727, "x")          # a science site is not reclassified
        assert len(B.R.FAILS) == 1
    """)
    assert rc == 0, out


def t6_stale_declaration():
    rc, out = snippet("""
        B.DRIFT[("corpus", "a site c98 does not have")] = "count"
        sys.exit(B.run(["--corpus", "--no-census"]))
    """)
    assert rc == 2, (rc, out[-1500:])
    assert "DRIFT DECLARATION IS STALE" in out


if __name__ == "__main__":
    fails = 0
    for name, fn in [("T1 enumeration", t1_enumeration), ("T2 science failure", t2_science_failure_fails),
                     ("T3 drift only", t3_drift_does_not_fail), ("T4 guard G1", t4_guard_g1),
                     ("T5 guard G2", t5_guard_g2), ("T6 stale declaration", t6_stale_declaration)]:
        try:
            fn()
            print("PASS  %s" % name)
        except AssertionError as e:
            fails += 1
            print("FAIL  %s: %s" % (name, str(e)[:1500]))
    print("\n%s" % ("ALL PASS" if not fails else "%d FAILURES" % fails))
    sys.exit(1 if fails else 0)
