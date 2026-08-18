"""Aggregate every MetaOptimize run into one tidy CSV.

Parses the Slurm .out files (which carry the exact ARGS line) plus TensorBoard
scalars, so results are reproducible from artefacts rather than memory.
Usage:  python aggregate.py <runs_dir> [<runs_dir> ...] > results.csv
"""
import sys, os, glob, re, csv, json

FIELDS = ["run", "job_id", "account", "granularity", "base", "meta", "meta_stepsize",
          "alpha0", "gamma", "augment", "seed", "epochs_done", "epochs_requested",
          "best_test", "final_test", "final_train", "collapsed", "node", "wallclock_min"]


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
    aug = (re.search(r"AUGMENT=(\d)", txt) or [None, "0"])[1]
    wall = (re.search(r"^(\d+)\s+minutes", txt, re.M) or [None, ""])[1]
    base = os.path.basename(path)
    jid = (re.search(r"-(\d+)\.out$", base) or [None, ""])[1]
    return {
        "run": a.get("run-name", base), "job_id": jid,
        "account": "s5014158" if "/home/s5014158" in path else "salehkaleybars",
        "granularity": a.get("stepsize-groups", "?"), "base": a.get("alg-base", a.get("optimizer", "?")),
        "meta": a.get("alg-meta", "?"), "meta_stepsize": a.get("meta-stepsize", ""),
        "alpha0": a.get("alpha0", ""), "gamma": a.get("gamma", ""), "augment": aug,
        "seed": a.get("seed", ""), "epochs_done": len(tests),
        "epochs_requested": a.get("num-epochs", ""),
        "best_test": max(tests), "final_test": tests[-1],
        "final_train": trains[-1] if trains else "",
        # collapse = ended at chance level after having been meaningfully better
        "collapsed": int(tests[-1] <= 11.0 and max(tests) > 20.0),
        "node": node, "wallclock_min": wall,
    }


rows = []
for d in sys.argv[1:]:
    for f in glob.glob(os.path.join(d, "**", "*.out"), recursive=True):
        r = parse_out(f)
        if r:
            rows.append(r)
rows.sort(key=lambda r: (r["base"], r["granularity"], r["seed"]))
w = csv.DictWriter(sys.stdout, fieldnames=FIELDS)
w.writeheader()
for r in rows:
    w.writerow(r)
print(f"# {len(rows)} runs aggregated", file=sys.stderr)
