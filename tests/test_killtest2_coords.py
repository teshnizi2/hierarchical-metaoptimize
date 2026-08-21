#!/usr/bin/env python3
"""Ground-truth validation for analysis/killtest2_coords.py.

Builds synthetic probe dirs in the PATCH_PROBE4 format with KNOWN structure and checks
that the estimator recovers it:

  T1  independent coords, zero marginal bias  -> every stratum ~50.00 %, shift null ~50.00 %
  T2  independent coords WITH per-coord marginal bias p_i
      -> raw agreement > 50 % everywhere, but the circular-shift null MATCHES it,
         so DELTA ~ 0.  (This is the whole point: marginal bias is not dependence.)
  T3  genuine WITHIN-BLOCK dependence on top of marginal bias
      -> within-block DELTA strongly positive, across-block DELTA ~ 0
  T4  the exact pairwise identity: brute-force pair enumeration must equal the O(R*K)
      group-sum estimator to floating-point precision.
"""
import base64
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, '..', 'analysis', 'killtest2_coords.py')
sys.path.insert(0, os.path.join(HERE, '..', 'analysis'))
import killtest2_coords as KT  # noqa: E402

BLOCK_SIZES = KT.BLOCK_SIZES          # [3,12,15,15,15,2] -> 62 tensors
N_TENSOR = sum(BLOCK_SIZES)


def write_probe(path, S, t_n, idx, n_tot):
    """Serialise a sign matrix into the PATCH_PROBE4 on-disk format."""
    os.makedirs(path, exist_ok=True)
    R, k = S.shape
    json.dump({'sub_seed': 0, 'k': k, 'n_tot': int(n_tot), 'stepsize_type': 'weightwise',
               't_n': [int(v) for v in t_n], 'param_numels': [int(v) for v in t_n],
               'idx': [int(v) for v in idx]},
              open(os.path.join(path, 'probe_index.json'), 'w'))
    with open(os.path.join(path, 'probe.jsonl'), 'w') as fh:
        for r in range(R):
            p = (S[r] + 1).astype(np.int8)
            enc = base64.b64encode(np.packbits(
                np.stack([(p >> 1) & 1, p & 1]).astype(np.uint8)).tobytes()).decode()
            # t_neg consistent with the tracked coords, scaled to the full tensor
            neg = [int(t_n[t] * 0.5) for t in range(len(t_n))]
            rec = {'step': r, 't_neg': neg, 't_zero': [0] * len(t_n),
                   't_n': [int(v) for v in t_n], 'z_sub': enc,
                   'frac_neg': float(sum(neg)) / float(sum(t_n)), 'frac_zero': 0.0}
            fh.write(json.dumps(rec) + '\n')


def make_layout(k, per_tensor):
    t_n = np.full(N_TENSOR, per_tensor, dtype=np.int64)
    n_tot = int(t_n.sum())
    bounds = np.concatenate([[0], np.cumsum(t_n)])
    # place exactly k/N_TENSOR tracked coords in each tensor
    per = k // N_TENSOR
    idx = np.concatenate([np.arange(bounds[t], bounds[t] + per) for t in range(N_TENSOR)])
    return t_n, n_tot, idx


def analyse(S, t_n, idx, n_tot, nulls=60, boot=20):
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, 'probe')
        write_probe(p, S, t_n, idx, n_tot)
        d = KT.load_probe(p, 1.0)
        args = type('A', (), {'nulls': nulls, 'boot': boot})()
        rng = np.random.default_rng(7)
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            res = KT.run_one(d, args, rng)
        return res, buf.getvalue()


def gen(R, k, rng, bias=0.0, block_dep=0.0, tensor_dep=0.0, t_n=None, idx=None):
    """Sign matrix with controllable marginal bias and within-block dependence."""
    n_per = k // N_TENSOR
    blk_of_tensor = np.concatenate([[b] * n for b, n in enumerate(BLOCK_SIZES)])
    tid = np.repeat(np.arange(N_TENSOR), n_per)
    blk = blk_of_tensor[tid]
    # Per-coordinate marginal.  NOTE the offset is one-sided: independent coords with
    # marginals p_i agree at 0.5 + 2(p_i-.5)(p_j-.5), so a bias spread SYMMETRICALLY about
    # 0.5 averages to no pair bias at all.  A persistent direction is a MEAN offset.
    p_i = 0.5 + bias * rng.random(k)
    base = rng.random((R, k)) < p_i[None, :]
    S = np.where(base, -1, 1).astype(np.int8)
    if block_dep > 0:
        shared = rng.standard_normal((R, len(BLOCK_SIZES)))[:, blk]
        flip = rng.random((R, k)) < block_dep
        S = np.where(flip, np.sign(shared).astype(np.int8), S).astype(np.int8)
    if tensor_dep > 0:
        shared = rng.standard_normal((R, N_TENSOR))[:, tid]
        flip = rng.random((R, k)) < tensor_dep
        S = np.where(flip, np.sign(shared).astype(np.int8), S).astype(np.int8)
    return S.astype(np.int8)


def check(name, cond, detail=''):
    print('%-58s %s   %s' % (name, 'PASS' if cond else 'FAIL', detail))
    return cond


def main():
    rng = np.random.default_rng(0)
    R, k = 400, N_TENSOR * 20      # 1240 tracked coords
    t_n, n_tot, idx = make_layout(k, 4000)
    ok = True

    print('\n=== T4: exactness of the O(R*K) group-sum estimator ===')
    S = gen(R, k, rng, bias=0.3, block_dep=0.1)
    lab = np.repeat(np.arange(N_TENSOR), k // N_TENSOR)
    c, p = KT.group_pair_sums(S, lab)
    # brute force on one tensor
    sel = np.where(lab == 3)[0]
    Ssel = S[:, sel].astype(np.float64)
    brute = 0.0
    for i in range(len(sel)):
        for j in range(len(sel)):
            if i != j:
                brute += (Ssel[:, i] * Ssel[:, j]).mean()
    ok &= check('brute-force == group-sum (tensor 3)',
                abs(brute - c[3]) < 1e-8, 'brute=%.9f est=%.9f' % (brute, c[3]))

    print('\n=== T1: independent, no marginal bias -> everything at 50%% ===')
    S = gen(R, k, rng, bias=0.0)
    res, _ = analyse(S, t_n, idx, n_tot)
    st = res['strata']
    for key in ('within_tensor', 'across_tensor_within_block', 'across_block'):
        ok &= check('  %s obs ~ 50%%' % key, abs(st[key]['obs'] - 0.5) < 0.004,
                    '%.4f%%' % (100 * st[key]['obs']))
        ok &= check('  %s DELTA ~ 0' % key, abs(st[key]['delta_pp']) < 0.5,
                    '%+.4fpp' % st[key]['delta_pp'])

    print('\n=== T2: marginal bias only -> raw > 50%% but DELTA ~ 0 ===')
    S = gen(R, k, rng, bias=0.6)
    res, _ = analyse(S, t_n, idx, n_tot)
    st = res['strata']
    ok &= check('  all_pairs raw ABOVE 50%%', st['all_pairs']['obs'] > 0.503,
                '%.4f%%' % (100 * st['all_pairs']['obs']))
    ok &= check('  shift null ALSO above 50%%', st['all_pairs']['shift_null'] > 0.503,
                '%.4f%%' % (100 * st['all_pairs']['shift_null']))
    for key in ('within_tensor', 'across_block'):
        ok &= check('  %s DELTA ~ 0 (bias is not dependence)' % key,
                    abs(st[key]['delta_pp']) < 0.6, '%+.4fpp' % st[key]['delta_pp'])

    print('\n=== T3: real WITHIN-BLOCK dependence + marginal bias ===')
    S = gen(R, k, rng, bias=0.4, block_dep=0.25)
    res, _ = analyse(S, t_n, idx, n_tot)
    st = res['strata']
    ok &= check('  within_tensor DELTA strongly positive',
                st['within_tensor']['delta_pp'] > 2.0,
                '%+.4fpp' % st['within_tensor']['delta_pp'])
    ok &= check('  across_tensor_within_block DELTA positive',
                st['across_tensor_within_block']['delta_pp'] > 2.0,
                '%+.4fpp' % st['across_tensor_within_block']['delta_pp'])
    ok &= check('  across_block DELTA ~ 0',
                abs(st['across_block']['delta_pp']) < 1.0,
                '%+.4fpp' % st['across_block']['delta_pp'])
    ok &= check('  architecture BEATS random same-size grouping',
                res['random_grouping']['arch_minus_random_pp'] > 1.0,
                '%+.4fpp' % res['random_grouping']['arch_minus_random_pp'])

    print('\n=== T3b: dependence that IGNORES blocks -> arch must NOT beat random ===')
    S = gen(R, k, rng, bias=0.4, tensor_dep=0.25)
    res, _ = analyse(S, t_n, idx, n_tot)
    ok &= check('  arch - random ~ 0 when structure is tensor-local',
                abs(res['random_grouping']['arch_minus_random_pp']) < 1.0,
                '%+.4fpp' % res['random_grouping']['arch_minus_random_pp'])

    print('\n%s' % ('ALL PASS' if ok else 'FAILURES PRESENT'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
