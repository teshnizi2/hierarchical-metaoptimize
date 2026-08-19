"""Aggregate every MetaOptimize run into one tidy CSV.

Parses the Slurm .out files (which carry the exact ARGS line) plus TensorBoard
scalars, so results are reproducible from artefacts rather than memory.
Usage:  python aggregate.py <runs_dir> [<runs_dir> ...] > results.csv
"""
import sys, os, glob, re, csv, json

FIELDS = ["run", "job_id", "account", "granularity", "base", "meta", "meta_stepsize",
          "alpha0", "gamma", "augment", "beta_clip", "hier", "lam", "eta_ratio",
          "seed", "epochs_done", "epochs_requested",
          "best_test", "final_test", "final_train", "collapsed", "node", "wallclock_min", "provenance", "dup_group", "superseded",
          "ep_to_85", "ep_to_88", "ep_to_90", "plateau", "ep_in_band_90"]


def parse_args_line(line):
    """--foo bar --baz qux  ->  {'foo': 'bar', 'baz': 'qux'}"""
    toks = line.split()
    out, i = {}, 0
    while i < len(toks):
        if toks[i].startswith("--"):
            k = toks[i][2:]
            v = toks[i + 1] if i + 1 < len(toks) and not toks[i + 1].startswith("--") else "1"
            out[k] = v
            i += 2
        else:
            i += 1
    return out


# Runs predating the ENV line (19 Aug 2026) carry their guard/hierarchy settings only
# in the run name. Reconstruct them here, and mark the row provenance as "inferred"
# so no analysis silently treats a reconstruction as a recorded fact.
GUARD = "-15:-2.3026"


def infer_from_name(name):
    n = name.replace("_", "-")
    if n.startswith("hs-"):                      # hierarchical sweep, M0 shrink, guard on
        lam = {"lam001": "0.01", "lam01": "0.1", "lam05": "0.5"}
        for k, v in lam.items():
            if f"-{k}-" in n + "-":
                return {"beta_clip": GUARD, "hier": "shrink", "lam": v, "eta_ratio": "na"}
    if n.startswith("ha-"):                      # M1 additive, guard on
        r = {"r01": "0.1", "r03": "0.3"}
        for k, v in r.items():
            if f"-{k}-" in n + "-":
                return {"beta_clip": GUARD, "hier": "additive", "lam": "na", "eta_ratio": v}
    if n.startswith("d4-clip"):                  # the guard gate itself
        return {"beta_clip": GUARD, "hier": "", "lam": "na", "eta_ratio": "na"}
    if n.startswith("hv-"):                      # hierarchy identity-validation runs
        m = {"hv-plain": ("", "na", "na"), "hv-lam0": ("shrink", "0", "na"),
             "hv-lam1": ("shrink", "1", "na"), "hv-ratio1": ("additive", "na", "1")}
        for k, (h, l, r) in m.items():
            if n.startswith(k):
                return {"beta_clip": GUARD, "hier": h, "lam": l, "eta_ratio": r}
    # everything else predates the guard entirely
    return {"beta_clip": "none", "hier": "", "lam": "na", "eta_ratio": "na"}


def account_of(path, save_dir):
    """Which cluster account produced this run.

    The .out path is authoritative on the cluster but NOT in the local backup,
    where alice2's runs live under runs_alice2/ and no longer contain
    /home/s5014158. Falling back to the path alone silently relabelled all 168
    alice2 runs as salehkaleybars, so the recorded --save-directory is checked
    first -- it travels with the artefact.
    """
    for hay in (save_dir, path):
        if "s5014158" in hay or "runs_alice2" in hay:
            return "s5014158"
    return "salehkaleybars"


def ep_to(tests, target):
    """1-indexed epoch at which test accuracy first reaches target; "" if never."""
    for i, v in enumerate(tests):
        if v >= target:
            return i + 1
    return ""


def plateau_of(tests, k=20):
    """Mean test accuracy over the last k epochs -- the arm's asymptote.

    A threshold drawn through an arm's own plateau measures noise, not speed
    (OPERATIONS gotcha 17), so every epochs-to-target figure must be read
    against this. Undefined for runs shorter than k epochs.
    """
    return round(sum(tests[-k:]) / len(tests[-k:]), 3) if len(tests) >= k else ""


def in_band(tests, target, half=1.0):
    """How many epochs the curve spends inside +-half of target.

    Large means the threshold sits on the asymptote and the crossing epoch is
    a coin-flip; small means the curve crosses decisively.
    """
    return sum(1 for v in tests if target - half <= v <= target + half)


def parse_out(path):
    txt = open(path, errors="replace").read()
    m = re.search(r"^ARGS: (.+)$", txt, re.M)
    if not m:
        return None
    a = parse_args_line(m.group(1))
    tests = [float(x) for x in re.findall(r"Test Accuracy: ([0-9.]+)", txt)]
    trains = [float(x) for x in re.findall(r"Train Accuracy: ([0-9.]+)", txt)]
    if not tests:
        return None
    node = (re.search(r"NODE=(\S+)", txt) or [None, ""])[1]
    # ENV line (added 19 Aug 2026). Runs older than that have no env provenance:
    # their guard/hier settings are recorded only in the run name -- see FINDINGS.
    env = re.search(r"^ENV: (.+)$", txt, re.M)
    e = dict(kv.split("=", 1) for kv in env.group(1).split()) if env else {}
    aug = e.get("AUGMENT") or (re.search(r"AUGMENT=(\d)", txt) or [None, "?"])[1]
    wall = (re.search(r"^(\d+)\s+minutes", txt, re.M) or [None, ""])[1]
    base = os.path.basename(path)
    jid = (re.search(r"-(\d+)\.out$", base) or [None, ""])[1]
    return {
        "run": a.get("run-name", base), "job_id": jid,
        "account": account_of(path, a.get("save-directory", "")),
        "granularity": a.get("stepsize-groups", "?"), "base": a.get("alg-base", a.get("optimizer", "?")),
        "meta": a.get("alg-meta", "?"), "meta_stepsize": a.get("meta-stepsize", ""),
        "alpha0": a.get("alpha0", ""), "gamma": a.get("gamma", ""), "augment": aug,
        **({"beta_clip": e["BETA_CLIP"], "hier": e["HIER"] if e["HIER"] != "none" else "",
            "lam": e["LAM"], "eta_ratio": e["ETA_RATIO"], "provenance": "env"} if env
           else {**infer_from_name(a.get("run-name", base)), "provenance": "inferred"}),
        "seed": a.get("seed", ""), "epochs_done": len(tests),
        "epochs_requested": a.get("num-epochs", ""),
        "best_test": max(tests), "final_test": tests[-1],
        "final_train": trains[-1] if trains else "",
        # collapse = ended at chance level after having been meaningfully better
        "collapsed": int(tests[-1] <= 11.0 and max(tests) > 20.0),
        "node": node, "wallclock_min": wall,
        # PRIMARY metric: epochs to reach a target test accuracy (first crossing).
        "ep_to_85": ep_to(tests, 85.0), "ep_to_88": ep_to(tests, 88.0),
        "ep_to_90": ep_to(tests, 90.0),
        # Threshold-safety companions (see OPERATIONS gotcha 17): a crossing epoch
        # is only a speed measurement if 90 is comfortably below the plateau.
        "plateau": plateau_of(tests), "ep_in_band_90": in_band(tests, 90.0),
    }


rows = []
for d in sys.argv[1:]:
    for f in glob.glob(os.path.join(d, "**", "*.out"), recursive=True):
        r = parse_out(f)
        if r:
            rows.append(r)
# A resubmission reuses --run-name, so `run` is NOT a unique key: the same name
# can carry a finished run and an in-flight one. Any analysis that keys a dict on
# `run` then silently keeps whichever came last -- which is how three completed
# 100-epoch alpha0 controls were shadowed by partial reruns. Flag them here so a
# collision is visible in the CSV instead of being discovered downstream.
by_name = {}
for r in rows:
    by_name.setdefault(r["run"], []).append(r)
dups = {k: v for k, v in by_name.items() if len(v) > 1}
for name, group in dups.items():
    best = max(group, key=lambda r: int(r["epochs_done"] or 0))
    for r in group:
        r["dup_group"] = name
        r["superseded"] = 0 if r is best else 1

rows.sort(key=lambda r: (r["base"], r["granularity"], r["seed"]))
w = csv.DictWriter(sys.stdout, fieldnames=FIELDS, extrasaction="ignore")
w.writeheader()
for r in rows:
    r.setdefault("dup_group", "")
    r.setdefault("superseded", 0)
    w.writerow(r)
print(f"# {len(rows)} runs aggregated", file=sys.stderr)
if dups:
    print(f"# WARNING: {len(dups)} duplicated run-name(s); "
          f"filter superseded==0 before any per-run analysis:", file=sys.stderr)
    for name, group in sorted(dups.items()):
        detail = ", ".join(f"{r['job_id']}({r['epochs_done']}ep"
                           f"{'' if not r['superseded'] else ', superseded'})" for r in group)
        print(f"#   {name}: {detail}", file=sys.stderr)
