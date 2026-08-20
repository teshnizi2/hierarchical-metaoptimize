#!/usr/bin/env python3
"""Build a BETA_SCHEDULE=replay array from an existing run's PROBE output.

    python analysis/make_beta_replay.py <probe_dir> --alpha0 1e-3 --steps 10000 \
        --weight pw -o /path/to/replay.npy

INPUT   <probe_dir>/probe.jsonl      (the 'beta' field of every record)
        <probe_dir>/block_sizes.json ({'stepsize_type':..., 'n_b':[...]})

INDEXING (must match Optimizers/HF.py _bsched_step exactly)
    HF.counter is -1 during the first step() call and increments at the END of
    step(), so during call j: counter == j-1.  _probe writes {"step": counter},
    hence a record tagged step=s holds beta at the end of call s+1.  The replay
    array is indexed by "end of call t", so
            arr[s+1] = record(step=s).beta ,      arr[0] = log(alpha0).
    HF asserts nothing about this; the sidecar json records the convention and
    beta_schedule.json in the replay run records the one it used.

WEIGHTING  probe.jsonl stores, per record:
    scalar/layerwise/blockwise -> the FULL per-group beta vector
    nodewise/weightwise        -> the per-TENSOR MEAN of beta (62 numbers)
  agree2.py averages those per-tensor means with EQUAL weight; that is the true
  group mean only for blockwise and layerwise.  Options:
    --weight pw   parameter-weighted mean (the corrected weighting).
                  layerwise/blockwise/weightwise: sum(n_b*bv)/sum(n_b).
                  nodewise: ALSO sum(n_b*bv)/sum(n_b) -- each node of tensor i
                  governs numel_i/nnodes_i params, so tensor i's mean carries
                  total param weight numel_i.  Exactly recoverable.
    --weight gw   group-equal mean (one weight per beta COORDINATE).
                  weightwise: identical to pw.  layerwise/blockwise: plain mean.
                  nodewise: needs NODE counts, which block_sizes.json does not
                  store (it stores numels for nodewise too) -> supply
                  --node-counts n1,n2,... or the script refuses.
    --weight raw  the unweighted mean of the recorded vector, i.e. exactly what
                  bin/agree2.py currently reports.  Use only to build an arm
                  that reproduces the PUBLISHED convention.

RESOLUTION  probe stride is 100 steps (PROBE=100), so a 10 000-step run gives
  100 knots.  Values between knots are linearly interpolated in beta (that is,
  geometrically in alpha).  This RESAMPLES AWAY the +-meta_stepsize per-step
  jitter and keeps only the drift; it is a real approximation and the sidecar
  reports it.  For an exact source, re-run the donor arm with
  BETA_TRACE=<f.npy> (dense, every step, float64) and feed that file to
  BETA_SCHEDULE=replay:<f.npy>#0 directly -- no interpolation at all.
"""
import argparse, json, os, hashlib
import numpy as np


def load_probe(d):
    recs = []
    with open(os.path.join(d, 'probe.jsonl')) as fh:
        for line in fh:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    recs.sort(key=lambda r: r['step'])
    bs = json.load(open(os.path.join(d, 'block_sizes.json')))
    return recs, bs


def reduce_beta(bv, n_b, stype, weight, node_counts):
    bv = np.asarray(bv, dtype=np.float64)
    if stype == 'scalar':
        return float(bv[0])
    if weight == 'raw':
        return float(bv.mean())
    if weight == 'pw':
        w = np.asarray(n_b, dtype=np.float64)
    else:  # gw
        if stype == 'weightwise':
            w = np.asarray(n_b, dtype=np.float64)          # == pw
        elif stype == 'nodewise':
            if node_counts is None:
                raise SystemExit('--weight gw on a nodewise run needs --node-counts '
                                 '(block_sizes.json stores numels, not node counts; '
                                 'see bin/infer_ntot.py)')
            w = np.asarray(node_counts, dtype=np.float64)
        else:
            w = np.ones_like(bv)
    if w.shape != bv.shape:
        raise SystemExit('weight/beta length mismatch: %r vs %r' % (w.shape, bv.shape))
    return float((w * bv).sum() / w.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('probe_dir')
    ap.add_argument('--alpha0', type=float, required=True)
    ap.add_argument('--steps', type=int, required=True,
                    help='length T of the emitted array = optimizer steps in the replay run '
                         '(epochs * ceil(50000/batch_size))')
    ap.add_argument('--weight', choices=['pw', 'gw', 'raw'], default='pw')
    ap.add_argument('--node-counts', default=None,
                    help='comma-separated node counts, only for --weight gw on nodewise')
    ap.add_argument('--per-group', action='store_true',
                    help='emit (T,G) instead of (T,); scalar/layerwise/blockwise only')
    ap.add_argument('-o', '--out', required=True)
    a = ap.parse_args()

    recs, bs = load_probe(a.probe_dir)
    stype, n_b = bs['stepsize_type'], bs['n_b']
    nc = [int(x) for x in a.node_counts.split(',')] if a.node_counts else None

    knots_t = [0]
    if a.per_group:
        if stype not in ('scalar', 'layerwise', 'blockwise'):
            raise SystemExit('--per-group only for scalar/layerwise/blockwise '
                             '(probe stores per-tensor MEANS for %s)' % stype)
        G = len(recs[0]['beta'])
        knots_y = [np.full(G, np.log(a.alpha0), dtype=np.float64)]
        for r in recs:
            knots_t.append(int(r['step']) + 1)
            knots_y.append(np.asarray(r['beta'], dtype=np.float64))
        Y = np.stack(knots_y)                      # (K,G)
    else:
        knots_y = [float(np.log(a.alpha0))]
        for r in recs:
            knots_t.append(int(r['step']) + 1)
            knots_y.append(reduce_beta(r['beta'], n_b, stype, a.weight, nc))
        Y = np.asarray(knots_y, dtype=np.float64)[:, None]   # (K,1)

    kt = np.asarray(knots_t, dtype=np.float64)
    if len(set(knots_t)) != len(knots_t):
        raise SystemExit('duplicate probe steps in %s' % a.probe_dir)
    t = np.arange(a.steps, dtype=np.float64)
    out = np.empty((a.steps, Y.shape[1]), dtype=np.float64)
    for c in range(Y.shape[1]):
        out[:, c] = np.interp(t, kt, Y[:, c])      # holds last beyond the final knot
    if Y.shape[1] == 1 and not a.per_group:
        out = out[:, 0]

    np.save(a.out, out)
    with open(a.out, 'rb') as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    n_extrap = int((t > kt[-1]).sum())
    meta = {'source': os.path.abspath(a.probe_dir), 'stepsize_type': stype,
            'weight': a.weight, 'per_group': bool(a.per_group),
            'alpha0': a.alpha0, 'beta_init': float(np.log(a.alpha0)),
            'n_knots': len(knots_t), 'knot_stride': int(kt[2] - kt[1]) if len(kt) > 2 else 0,
            'last_knot_t': int(kt[-1]), 'steps': a.steps,
            'extrapolated_hold_steps': n_extrap,
            'shape': list(out.shape), 'dtype': 'float64',
            'sha256': sha, 'out': os.path.abspath(a.out),
            'index_convention': 'arr[t] = beta at end of step() call t; probe step s -> arr[s+1]',
            'interpolation': 'linear in beta between probe knots (geometric in alpha); '
                             'per-step meta-stepsize jitter is resampled away',
            'min': float(out.min()), 'max': float(out.max())}
    with open(a.out + '.json', 'w') as fh:
        json.dump(meta, fh, indent=1, sort_keys=True)
    print(json.dumps(meta, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
