"""Regression test for analysis/probe5_window.py reduce_dir() on degenerate probe dirs
(CORRECTIONS 224, safety sweep).

    python3 tests/test_probe5_window_degenerate.py

THE BUG.  reduce_dir() subscripted recompute_rho()'s result without checking it.
recompute_rho() returns None whenever the corrected floor is non-finite, and
corrected_floor() returns NaN whenever n_tot < 2.  parse_dirname() accepts the rung
token "scal" (a scalar arm, n_tot = 1), and decompose() happily returns a dict for
n_tot = 1, so a single scalar-arm probe dir under the root crashed the whole reducer
with `TypeError: 'NoneType' object is not subscriptable` -- and with it
probe5_time_ladder.reduce_arm() and neff_instrument.reduce_root(), which call it.
The same happens for n_tot >= 2 when neg_counts.json records n_records < 2 (the
heterogeneity term is NaN).

THE FIX skips that window, exactly as reduce_dir() already skips a window whose
decompose() is None.  On every non-degenerate dir the output is unchanged (P3).
"""
import json, math, os, subprocess, sys, tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AN = os.path.join(ROOT, "analysis")
sys.path.insert(0, AN)
import probe5_window as PW  # noqa: E402


def make_dir(root, name, n_tot, n_records_meta=400, T=400, seed=0):
    d = os.path.join(root, name)
    os.makedirs(d)
    rng = np.random.default_rng(seed)
    np.save(os.path.join(d, "neg_counts.npy"),
            rng.integers(0, n_records_meta + 1, size=n_tot).astype(np.int64))
    json.dump({"n_records": n_records_meta, "n_tot": n_tot},
              open(os.path.join(d, "neg_counts.json"), "w"))
    with open(os.path.join(d, "probe.jsonl"), "w") as f:
        for _ in range(T):
            p = float(rng.binomial(n_tot, 0.5)) / n_tot
            f.write(json.dumps({"frac_neg": p, "frac_zero": 0.0}) + "\n")
    return d


def reference_reduce_dir(d, windows=PW.WINDOWS):
    """The pre-fix body, verbatim, for the equivalence check on healthy dirs."""
    got = PW.read_probe5(d)
    if got is None:
        return None
    counts, meta = got
    T5, n_tot = int(meta["n_records"]), int(meta["n_tot"])
    recs = PW.load(d) if PW.load else []
    if not recs:
        return None
    fn = [r.get("frac_neg") for r in recs]
    fz = [r.get("frac_zero", 0.0) for r in recs]
    if any(v is None for v in fn):
        return None
    fam, rung, seed = PW.parse_dirname(os.path.basename(d))
    out = {}
    for lab, w in windows:
        dec = PW.decompose(fn, fz, n_tot, window=w)
        if not dec:
            continue
        hv, _, _, _ = PW.hetvar_from_counts(counts, T5, tau=dec["tau"])
        v_un, _ = PW.corrected_floor(dec["v_indep"], 0.0, n_tot)
        v_co, H = PW.corrected_floor(dec["v_indep"], hv, n_tot)
        c_un, c_co = PW.recompute_rho(dec, v_un), PW.recompute_rho(dec, v_co)
        out[lab] = dict(T=dec["T"], tau=dec["tau"], H=H,
                        rho_s_unc=c_un["rho_s"], rho_s=c_co["rho_s"],
                        rho_min=c_co["rho_min"], resolved=c_co["resolved"])
    return dict(dir=d, fam=fam, rung=rung, seed=seed, n_tot=n_tot, win=out)


def same(a, b):
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, float) and math.isnan(a):
        return isinstance(b, float) and math.isnan(b)
    return a == b


def p1_scalar_dir_does_not_crash(tmp):
    d = make_dir(tmp, "probe_scal_a3_s0", n_tot=1)
    try:
        reference_reduce_dir(d)
        raise AssertionError("the pre-fix body did not crash; the premise of this test is wrong")
    except TypeError:
        pass
    r = PW.reduce_dir(d)
    assert r is not None and r["n_tot"] == 1 and r["rung"] == "scal", r
    assert r["win"] == {}, r["win"]


def p2_torn_meta_does_not_crash(tmp):
    d = make_dir(tmp, "probe_node_a3_s1", n_tot=64, n_records_meta=1)
    try:
        reference_reduce_dir(d)
        raise AssertionError("pre-fix body did not crash on n_records < 2")
    except TypeError:
        pass
    r = PW.reduce_dir(d)
    assert r is not None and r["win"] == {}, r


def p3_healthy_dirs_unchanged(tmp):
    for i, (rung, n) in enumerate((("w", 5000), ("node", 256), ("lay", 62), ("blk6", 6))):
        d = make_dir(tmp, "probe_%s_a3_s%d" % (rung, i), n_tot=n, seed=10 + i)
        a, b = PW.reduce_dir(d), reference_reduce_dir(d)
        assert a["win"], (rung, a)
        assert same(a, b), (rung, a, b)


def p4_main_survives_a_scalar_arm(tmp):
    root = os.path.join(tmp, "root")
    os.makedirs(root)
    make_dir(root, "probe_w_a3_s0", n_tot=5000, seed=1)
    make_dir(root, "probe_node_a3_s0", n_tot=256, seed=2)
    make_dir(root, "probe_scal_a3_s0", n_tot=1, seed=3)
    p = subprocess.run([sys.executable, os.path.join(AN, "probe5_window.py"), root],
                       capture_output=True, text=True, cwd=ROOT)
    assert "Traceback" not in p.stderr, p.stderr[-1500:]
    assert "PROBE5 SCALE PROFILE" in p.stdout, p.stdout[-1500:]


if __name__ == "__main__":
    fails = 0
    for name, fn in (("P1 scalar dir", p1_scalar_dir_does_not_crash),
                     ("P2 n_records<2", p2_torn_meta_does_not_crash),
                     ("P3 healthy dirs unchanged", p3_healthy_dirs_unchanged),
                     ("P4 main() survives", p4_main_survives_a_scalar_arm)):
        with tempfile.TemporaryDirectory() as tmp:
            try:
                fn(tmp)
                print("PASS  %s" % name)
            except AssertionError as e:
                fails += 1
                print("FAIL  %s: %s" % (name, str(e)[:1500]))
            except Exception as e:  # a crash is a failure, not a test error
                fails += 1
                print("FAIL  %s: %s: %s" % (name, type(e).__name__, e))
    print("\n%s" % ("ALL PASS" if not fails else "%d FAILURES" % fails))
    sys.exit(1 if fails else 0)
