#!/usr/bin/env python3
r"""c69_c100_armset.py -- IS 68.6's "FULLY MATCHED" CIFAR-100 CELL ACTUALLY MATCHED?

PROVENANCE, STATED FIRST (this was NOT pre-registered)
-------------------------------------------------------
Found while re-deriving cycle-65..69 numbers from the CSV in order to bring `docs/MASTER-TABLE.md`
current (it cites c65/c66/c67/c68/c69 ZERO times, while STANDING RULE (15) makes it the mandatory
grep target before any cross-granularity claim -- a structural hazard in its own right).

It is therefore **POST-HOC**, and under CORRECTIONS 76(1)/79 a post-hoc finding may not overturn
a registered gate.  It does not: what is established here is a MECHANICAL fact about which runs
sit in which arm -- a membership count, not an inference -- and the registered verdict of 68.6
SURVIVES it.  Only the magnitude moves.

THE CLAIM UNDER TEST
--------------------
FINDINGS 68.6 / CORRECTIONS 97.5 report the campaign's newest load-bearing result as:

    "Fully matched cell, 100 epochs ... ResNet18_c100 / CIFAR-100 / a0=1e-3 / ms=1e-3 / Lion /
     HIER none / clip -15:-2.3026 / AUG=1 ... nodewise 71.415 +-0.049 (n=3) vs layerwise
     69.048 +-0.220 (n=14), D = +2.367 pp, resolved at 5.24x the 65.6/94.3 gate"

There is no configuration group in the CSV with n=14 CIFAR-100 layerwise runs at that config.
This instrument asks which arm set reproduces 69.048 +-0.220, and what the contrast becomes when
the NETWORK axis is held fixed -- which is what STANDING RULE (10) requires:

    STANDING RULE (10), installed cycle 64: "a series across any axis must hold the arm fixed."

STATISTIC AND GATE ARE THE PUBLISHED ONES, NOT NEW
--------------------------------------------------
`plateau5` (mean of the last 5 epochs, the documented window) and `plateau` (the CSV's k=20
column) are read straight from `results/all_runs.csv`; no re-windowing is done here.  The
resolution gate is 65.6/94.3's own rule, `margin > 2*sqrt(sem1^2 + sem2^2)`, and selftest T8
asserts it reproduces 68.6's published gate value of 0.452 on 68.6's own arm set.

GATES
-----
G1  RECONSTRUCTION.  Relaxing ONLY the network axis must reproduce every published 68.6 cell
    (layerwise n=14 / 69.048 / 0.220 and scalar n=11 / 22.208) to 3 decimals.  If it does not,
    the diagnosis is wrong and nothing below may be reported.
G2  CONTAMINATION IS ASYMMETRIC.  The arms alleged to be contaminated (layerwise, scalar) must
    contain >1 network; the arms alleged to be clean (nodewise, weightwise, blocks) must contain
    exactly 1.
G3  VERDICT SURVIVAL.  Under the network-matched arm set the ordering (interior maximum at
    nodewise), the no-seed-overlap property and the gate clearance are each re-scored and
    reported whether or not they survive.

USAGE
    python3 analysis/c69_c100_armset.py --selftest
    python3 analysis/c69_c100_armset.py --report
"""
import argparse
import collections
import csv
import math
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# 68.6's stated cell, verbatim, MINUS the network key (that omission is the finding).
CELL = dict(dataset='CIFAR100', epochs_done='100', window_ok='1', alpha0='1e-3',
            meta_stepsize='1e-3', base='SGDm', meta='Lion', augment='1', hier='',
            beta_clip='-15:-2.3026')
NETWORK = 'ResNet18_c100'          # the network 68.6's header names
ORDER = ['weightwise', 'nodewise', 'layerwise', 'resnet18_blocks', 'scalar']


def fnum(r, k):
    try:
        return float(r[k])
    except (ValueError, TypeError, KeyError):
        return None


def load(root=ROOT):
    with open(os.path.join(root, 'results', 'all_runs.csv')) as fh:
        return list(csv.DictReader(fh))


def cell_rows(rows):
    return [r for r in rows if all(r.get(k) == v for k, v in CELL.items())]


def arms(rows, network_matched):
    g = collections.defaultdict(list)
    for r in cell_rows(rows):
        if network_matched and r['network'] != NETWORK:
            continue
        g[r['granularity']].append(r)
    return g


def stat(rs, col='plateau5'):
    v = [fnum(r, col) for r in rs]
    v = [x for x in v if x is not None]
    if not v:
        return None
    sem = st.stdev(v) / math.sqrt(len(v)) if len(v) > 1 else 0.0
    return dict(n=len(v), mean=st.mean(v), sem=sem, min=min(v), max=max(v))


def gate(a, b):
    return 2.0 * math.sqrt(a['sem'] ** 2 + b['sem'] ** 2)


def contrast(g, col):
    a, b = stat(g['nodewise'], col), stat(g['layerwise'], col)
    gt = gate(a, b)
    return dict(a=a, b=b, delta=a['mean'] - b['mean'], gate=gt,
                mult=(a['mean'] - b['mean']) / gt, overlap=not (a['min'] > b['max']))


def selftest():
    t = 0

    def ck(cond, label):
        nonlocal t
        t += 1
        if not cond:
            print(f'  FAIL T{t}: {label}')
            sys.exit(1)
        print(f'  ok  T{t}: {label}')

    rows = load()
    ck(len(rows) == 1707, f'CSV has 1707 rows ({len(rows)})')
    gr = arms(rows, network_matched=False)
    gm = arms(rows, network_matched=True)

    # G1 reconstruction of 68.6's published cells
    ly = stat(gr['layerwise'])
    ck(ly['n'] == 14, f"G1: relaxed layerwise n=14 (got {ly['n']})")
    ck(abs(ly['mean'] - 69.048) < 5e-3, f"G1: relaxed layerwise mean=69.048 (got {ly['mean']:.3f})")
    ck(abs(ly['sem'] - 0.220) < 5e-3, f"G1: relaxed layerwise sem=0.220 (got {ly['sem']:.3f})")
    sc = stat(gr['scalar'])
    ck(sc['n'] == 11, f"G1: relaxed scalar n=11 (got {sc['n']})")
    ck(abs(sc['mean'] - 22.208) < 5e-3, f"G1: relaxed scalar mean=22.208 (got {sc['mean']:.3f})")
    nd = stat(gr['nodewise'])
    ck(nd['n'] == 3 and abs(nd['mean'] - 71.415) < 5e-3,
       f"G1: nodewise n=3 mean=71.415 (got {nd['n']}, {nd['mean']:.3f})")
    ck(abs(contrast(gr, 'plateau5')['gate'] - 0.452) < 1e-3,
       'G1/T8: gate rule reproduces 68.6\'s published 0.452')
    ck(abs(contrast(gr, 'plateau5')['delta'] - 2.367) < 5e-3,
       'G1: relaxed delta reproduces 68.6\'s published +2.367 pp')

    # G2 contamination is asymmetric
    nets = {k: {r['network'] for r in v} for k, v in gr.items()}
    ck(len(nets['layerwise']) == 3, f"G2: layerwise spans 3 networks ({sorted(nets['layerwise'])})")
    ck(len(nets['scalar']) == 3, f"G2: scalar spans 3 networks ({sorted(nets['scalar'])})")
    for a in ('nodewise', 'weightwise', 'resnet18_blocks'):
        ck(len(nets[a]) == 1, f'G2: {a} is single-network ({sorted(nets[a])})')

    # matched arm set is a strict subset
    ck(stat(gm['layerwise'])['n'] == 8, 'matched layerwise n=8')
    ck(stat(gm['nodewise'])['n'] == 3, 'matched nodewise n=3 (unchanged)')
    ck(all(stat(gm[a])['n'] <= stat(gr[a])['n'] for a in gr),
       'matched arm set is a subset of the relaxed one, arm by arm')

    print(f'\n{t}/{t} selftests PASS')
    return 0


def report():
    rows = load()
    for label, nm in [('68.6 AS PUBLISHED  (network axis RELAXED)', False),
                      ('NETWORK-MATCHED    (ResNet18_c100 only)', True)]:
        g = arms(rows, nm)
        print(f'== {label}')
        print(f'   {"arm":18s} {"n":>3s} {"plateau5":>9s} {"sem":>6s} {"min":>8s} {"max":>8s}  networks')
        for a in ORDER:
            s = stat(g[a])
            if not s:
                continue
            nets = ','.join(sorted({r['network'] for r in g[a]}))
            print(f'   {a:18s} {s["n"]:3d} {s["mean"]:9.3f} {s["sem"]:6.3f} '
                  f'{s["min"]:8.3f} {s["max"]:8.3f}  {nets}')
        for col, kk in [('plateau5', 'k=5 '), ('plateau', 'k=20')]:
            c = contrast(g, col)
            print(f'   {kk} nodewise-layerwise = {c["delta"]:+.3f} pp   gate {c["gate"]:.3f}   '
                  f'{c["mult"]:.2f}x   seed-overlap {"YES" if c["overlap"] else "NO"}')
        w, n, l = stat(g['weightwise']), stat(g['nodewise']), stat(g['layerwise'])
        print(f'   asymmetry: node-weight {n["mean"]-w["mean"]:+.3f} pp vs '
              f'node-layer {n["mean"]-l["mean"]:+.3f} pp  '
              f'= {(n["mean"]-w["mean"])/(n["mean"]-l["mean"]):.2f}x')
        print(f'   interior maximum at nodewise: '
              f'{"YES" if n["mean"] > w["mean"] and n["mean"] > l["mean"] else "NO"}')
        print()
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--report', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.report:
        return report()
    ap.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
