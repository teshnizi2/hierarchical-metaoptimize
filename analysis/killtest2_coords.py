#!/usr/bin/env python3
"""KILLTEST-idea2 sec.5 -- coordinate-level sign agreement.

Consumes the PATCH_PROBE4 fields (cycle 42):
    t_neg / t_zero / t_n   exact within-tensor sign split, all 62 tensors, every record
    z_sub                  packed raw signs of a FIXED ~20k-coordinate subsample
    probe_index.json       the subsample indices + tensor sizes

and answers, from RAW PER-COORDINATE SIGNS:

  1. overall agreement (the headline statistic) at m = n_tot, against its independence floor
  2. within-tensor / across-tensor-within-block / across-6-block pairwise agreement,
     each against (a) the naive 50 % null and (b) a marginal-preserving circular-shift null
  3. agreement vs block size
  4. a same-size RANDOM-GROUPING control (does architecture buy anything beyond size?)

Pairwise same-sign rate uses the identity  [s_i == s_j] = (1 + s_i s_j)/2  for s in {-1,+1},
so every stratum mean is obtained EXACTLY from group sums in O(R*K) -- no pair enumeration
and no pair subsampling.  For a group g with tracked coordinates I_g:

    sum_{i!=j in I_g} C_ij = (1/R) sum_r ( sum_{i in I_g} s_ri )^2  -  |I_g|

Usage:
    killtest2_coords.py PROBE_DIR [PROBE_DIR ...] [--window 0.5] [--nulls 200] [--boot 200]
"""
import argparse
import base64
import json
import os
import sys

import numpy as np

# ResNet18 6-block partition, in tensor counts (KILLTEST-idea2 sec.3)
BLOCK_SIZES = [3, 12, 15, 15, 15, 2]


# ----------------------------------------------------------------- loading
def load_probe(pdir, window):
    meta_p = os.path.join(pdir, 'probe_index.json')
    if not os.path.exists(meta_p):
        raise SystemExit('%s: no probe_index.json -- run predates PATCH_PROBE4' % pdir)
    meta = json.load(open(meta_p))
    k, n_tot = meta['k'], meta['n_tot']

    recs = []
    with open(os.path.join(pdir, 'probe.jsonl')) as fh:
        for line in fh:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    recs = [r for r in recs if r.get('z_sub') and not str(r['z_sub']).startswith('ERR:')]
    if not recs:
        raise SystemExit('%s: no usable records' % pdir)

    # steady window: last `window` fraction of records (the published convention)
    cut = int(len(recs) * (1.0 - window))
    recs = recs[cut:]

    S = np.empty((len(recs), k), dtype=np.int8)
    for r, rec in enumerate(recs):
        raw = np.frombuffer(base64.b64decode(rec['z_sub']), dtype=np.uint8)
        bits = np.unpackbits(raw)[:2 * k].reshape(2, k)
        S[r] = (bits[0].astype(np.int8) * 2 + bits[1]) - 1

    t_n = np.asarray(recs[0]['t_n'], dtype=np.int64)
    t_neg = np.asarray([r['t_neg'] for r in recs], dtype=np.float64)
    t_zero = np.asarray([r['t_zero'] for r in recs], dtype=np.float64)
    steps = np.asarray([r['step'] for r in recs], dtype=np.int64)
    frac_neg = np.asarray([r['frac_neg'] for r in recs], dtype=np.float64)
    frac_zero = np.asarray([r['frac_zero'] for r in recs], dtype=np.float64)

    idx = np.asarray(meta['idx'], dtype=np.int64)
    # tensor id of each tracked coordinate, from the tensor boundaries
    bounds = np.concatenate([[0], np.cumsum(t_n)])
    tid = np.searchsorted(bounds, idx, side='right') - 1

    # 6-block label of each tensor
    blk_of_tensor = np.concatenate([[b] * n for b, n in enumerate(BLOCK_SIZES)])
    if len(blk_of_tensor) != len(t_n):
        raise SystemExit('%s: %d tensors, BLOCK_SIZES covers %d'
                         % (pdir, len(t_n), len(blk_of_tensor)))

    return dict(dir=pdir, meta=meta, S=S, t_n=t_n, t_neg=t_neg, t_zero=t_zero,
                steps=steps, frac_neg=frac_neg, frac_zero=frac_zero,
                tid=tid, blk_of_tensor=blk_of_tensor, n_tot=n_tot, k=k,
                n_records_total=len(recs))


# ------------------------------------------------------- pairwise machinery
def group_pair_sums(S, labels):
    """(sum of C_ij over ordered i!=j within each group, number of such pairs).

    Exact, via  sum_{i,j in g} s_i s_j = (sum_{i in g} s_i)^2.
    """
    R = S.shape[0]
    uniq = np.unique(labels)
    # one-hot group sums: (R, n_groups)
    G = np.zeros((R, len(uniq)), dtype=np.float64)
    remap = {v: i for i, v in enumerate(uniq)}
    lab = np.fromiter((remap[v] for v in labels), dtype=np.int64, count=len(labels))
    Sf = S.astype(np.float64)
    for gi in range(len(uniq)):
        G[:, gi] = Sf[:, lab == gi].sum(axis=1)
    sizes = np.bincount(lab, minlength=len(uniq)).astype(np.float64)
    # diagonal contributes s_i^2 == 1 for nonzero signs
    diag = (S.astype(np.float64) ** 2)
    diag_g = np.zeros(len(uniq))
    for gi in range(len(uniq)):
        diag_g[gi] = diag[:, lab == gi].sum() / R
    csum = (G ** 2).mean(axis=0) - diag_g
    npairs = sizes * (sizes - 1)
    return csum, npairs


def strata(S, tid, blk):
    """(agreement, npairs) for within-tensor / across-tensor-in-block / across-block."""
    R, K = S.shape
    Sf = S.astype(np.float64)
    tot_c = (Sf.sum(axis=1) ** 2).mean() - (Sf ** 2).sum() / R
    tot_p = float(K) * (K - 1)

    c_t, p_t = group_pair_sums(S, tid)
    c_b, p_b = group_pair_sums(S, blk[tid])

    within_t = (c_t.sum(), p_t.sum())
    within_b = (c_b.sum(), p_b.sum())
    across_t = (within_b[0] - within_t[0], within_b[1] - within_t[1])   # diff tensor, same block
    across_b = (tot_c - within_b[0], tot_p - within_b[1])               # diff block

    def agr(cs):
        c, p = cs
        return 0.5 * (1.0 + c / p) if p > 0 else np.nan

    return {'within_tensor': agr(within_t),
            'across_tensor_within_block': agr(across_t),
            'across_block': agr(across_b),
            'all_pairs': agr((tot_c, tot_p))}, \
           {'within_tensor': within_t[1],
            'across_tensor_within_block': across_t[1],
            'across_block': across_b[1],
            'all_pairs': tot_p}


def circshift_null(S, tid, blk, n_rep, rng):
    """Marginal-preserving null: circularly shift EACH coordinate's own sign series by an
    independent random offset.  Preserves each coordinate's marginal p_i and its own
    autocorrelation exactly; destroys all cross-coordinate dependence."""
    R, K = S.shape
    rows = np.arange(R)[:, None]
    out = {k: [] for k in ('within_tensor', 'across_tensor_within_block',
                           'across_block', 'all_pairs')}
    for _ in range(n_rep):
        off = rng.integers(0, R, size=K)
        Sp = S[(rows + off[None, :]) % R, np.arange(K)[None, :]]
        a, _ = strata(Sp, tid, blk)
        for k in out:
            out[k].append(a[k])
    return {k: np.asarray(v) for k, v in out.items()}


def bootstrap_records(S, tid, blk, n_rep, rng):
    """Sampling error of each stratum statistic, resampling RECORDS with replacement."""
    R = S.shape[0]
    out = {k: [] for k in ('within_tensor', 'across_tensor_within_block',
                           'across_block', 'all_pairs')}
    for _ in range(n_rep):
        sel = rng.integers(0, R, size=R)
        a, _ = strata(S[sel], tid, blk)
        for k in out:
            out[k].append(a[k])
    return {k: np.asarray(v) for k, v in out.items()}


# --------------------------------------------------------------- reporting
def floor_majority(n):
    """E[max(p,1-p)] under independence with p~Binom(n,1/2)/n: 0.5 + 0.5*sqrt(2/pi)/sqrt(n)."""
    return 0.5 + 0.5 * np.sqrt(2.0 / np.pi) / np.sqrt(np.maximum(n, 1))


def pp(x):
    return '%.4f %%' % (100.0 * x)


def run_one(d, args, rng):
    S, tid, blk = d['S'], d['tid'], d['blk_of_tensor']
    K, R = d['k'], S.shape[0]

    print('=' * 78)
    print('RUN  %s' % d['dir'])
    print('  n_tot=%d  tracked=%d  records in window=%d  steps %d..%d'
          % (d['n_tot'], K, R, d['steps'][0], d['steps'][-1]))

    # ---- zero handling
    nz_frac = d['frac_zero'].mean()
    ever_zero = (S == 0).any(axis=0)
    print('  frac_zero (all coords, mean over window) = %.3e ; tracked coords ever zero = %d'
          % (nz_frac, ever_zero.sum()))
    if nz_frac > 0.5:
        print('  !! z is (near-)identically zero -- the sign statistic is UNDEFINED here.')
        return None
    if ever_zero.any():
        keep = ~ever_zero
        S, tid = S[:, keep], tid[keep]
        K = int(keep.sum())
        print('  dropped %d tracked coords that are zero at some step; %d remain'
              % (int(ever_zero.sum()), K))

    res = {'dir': d['dir'], 'n_tot': int(d['n_tot']), 'K': K, 'R': R}

    # ---- 1. the headline statistic, exact, over ALL n_tot coordinates
    n_eff = d['n_tot'] * (1.0 - d['frac_zero'])
    maj = np.maximum(d['frac_neg'], 1.0 - d['frac_neg'])
    fl = floor_majority(n_eff)
    print('\n-- 1. OVERALL AGREEMENT (headline statistic, cross-sectional majority) --')
    print('   m = n_tot = %d   (exact, from frac_neg -- not the subsample)' % d['n_tot'])
    print('   agreement          = %s  +- %s' % (pp(maj.mean()), pp(maj.std(ddof=1) / np.sqrt(R))))
    print('   independence floor = %s' % pp(fl.mean()))
    print('   EXCESS over floor  = %s' % pp(maj.mean() - fl.mean()))
    res['headline_agreement'] = float(maj.mean())
    res['headline_floor'] = float(fl.mean())
    res['headline_excess'] = float(maj.mean() - fl.mean())

    # the same statistic on the tracked subsample, so it can also be read against a
    # MARGINAL-PRESERVING null (the independence floor above assumes p_i == 1/2 for all i)
    def maj_sub(M):
        pn = (M < 0).mean(axis=1)
        return np.maximum(pn, 1.0 - pn).mean()

    obs_sub = maj_sub(S)
    rows_ = np.arange(R)[:, None]
    null_sub = []
    for _ in range(args.nulls):
        off = rng.integers(0, R, size=K)
        null_sub.append(maj_sub(S[(rows_ + off[None, :]) % R, np.arange(K)[None, :]]))
    null_sub = np.asarray(null_sub)
    print('   -- same statistic on the %d tracked coords (m=%d) --' % (K, K))
    print('   agreement          = %s' % pp(obs_sub))
    print('   independence floor = %s   -> excess %+.4f pp'
          % (pp(floor_majority(K)), 100 * (obs_sub - floor_majority(K))))
    print('   circular-shift null= %s   -> excess %+.4f pp   p=%.4f'
          % (pp(null_sub.mean()), 100 * (obs_sub - null_sub.mean()),
             float((null_sub >= obs_sub).mean())))
    res['headline_sub'] = dict(m=K, obs=float(obs_sub),
                               indep_floor=float(floor_majority(K)),
                               shift_null=float(null_sub.mean()),
                               excess_vs_indep_pp=float(100 * (obs_sub - floor_majority(K))),
                               excess_vs_shift_pp=float(100 * (obs_sub - null_sub.mean())),
                               p_shift=float((null_sub >= obs_sub).mean()))

    # ---- 2. stratified pairwise agreement at COORDINATE granularity
    obs, npairs = strata(S, tid, blk)
    print('\n-- 2. PAIRWISE SAME-SIGN RATE between INDIVIDUAL WEIGHTS --')
    nulls = circshift_null(S, tid, blk, args.nulls, rng)
    boots = bootstrap_records(S, tid, blk, args.boot, rng)
    print('   %-28s %12s %10s %12s %12s %10s %10s'
          % ('stratum', 'pairs', 'observed', 'vs 50% null', 'shift null', 'DELTA', 'p(shift)'))
    res['strata'] = {}
    for key in ('within_tensor', 'across_tensor_within_block', 'across_block', 'all_pairs'):
        o = obs[key]
        se = boots[key].std(ddof=1)
        nm = nulls[key].mean()
        delta = o - nm
        p = float((nulls[key] >= o).mean())
        print('   %-28s %12.3e %10s %+11.2f%s %12s %+9.4fpp %10.4f'
              % (key, npairs[key], pp(o), (o - 0.5) / se if se > 0 else np.nan, 'sd',
                 pp(nm), 100 * delta, p))
        res['strata'][key] = dict(pairs=float(npairs[key]), obs=float(o), se=float(se),
                                  z_vs_50=float((o - 0.5) / se) if se > 0 else None,
                                  shift_null=float(nm),
                                  shift_null_sd=float(nulls[key].std(ddof=1)),
                                  delta_pp=float(100 * delta), p_shift=p)

    # ---- 3. agreement vs block size
    print('\n-- 3. AGREEMENT vs BLOCK SIZE --')
    print('   (a) EXACT within-tensor majority excess over each tensor own floor, all %d tensors'
          % len(d['t_n']))
    p_t = d['t_neg'] / d['t_n'][None, :]
    maj_t = np.maximum(p_t, 1.0 - p_t).mean(axis=0)
    fl_t = floor_majority(d['t_n'].astype(float))
    exc_t = maj_t - fl_t
    lg = np.log10(d['t_n'].astype(float))
    if lg.std() < 1e-12 or exc_t.std() < 1e-12:   # degenerate (synthetic fixtures)
        r_a, sl_a = float('nan'), float('nan')
    else:
        r_a = float(np.corrcoef(lg, exc_t)[0, 1])
        sl_a = float(np.polyfit(lg, exc_t, 1)[0])
    print('       Pearson r(log10 n_t, within-tensor excess) = %+.3f' % r_a)
    print('       OLS slope = %+.4f pp/decade' % (100 * sl_a))
    for lo, hi in [(0, 2), (2, 3), (3, 4), (4, 5), (5, 8)]:
        m = (lg >= lo) & (lg < hi)
        if m.sum():
            print('       n_t in [1e%d,1e%d): %2d tensors  excess %+.4f pp'
                  % (lo, hi, m.sum(), 100 * exc_t[m].mean()))
    res['size_exact'] = dict(pearson_r=r_a, slope_pp_per_decade=100 * sl_a,
                             per_tensor_excess_pp=[float(100 * v) for v in exc_t],
                             t_n=[int(v) for v in d['t_n']])

    print('   (b) within-tensor PAIRWISE agreement from tracked coords (>=30 per tensor)')
    rows = []
    for t in np.unique(tid):
        sel = tid == t
        if sel.sum() >= 30:
            c, p = group_pair_sums(S[:, sel], np.zeros(int(sel.sum()), dtype=np.int64))
            rows.append((int(t), int(d['t_n'][t]), int(sel.sum()), 0.5 * (1 + c[0] / p[0])))
    if len(rows) >= 3:
        lgb = np.log10([r[1] for r in rows])
        ag = np.asarray([r[3] for r in rows])
        r_b = float(np.corrcoef(lgb, ag)[0, 1])
        sl_b = float(np.polyfit(lgb, ag, 1)[0])
        print('       %d tensors qualify; Pearson r = %+.3f ; slope = %+.4f pp/decade'
              % (len(rows), r_b, 100 * sl_b))
        res['size_pairwise'] = dict(n_tensors=len(rows), pearson_r=r_b,
                                    slope_pp_per_decade=100 * sl_b,
                                    rows=[[a, b, c_, float(dd)] for a, b, c_, dd in rows])
    else:
        print('       too few tensors with >=30 tracked coords (%d)' % len(rows))
        res['size_pairwise'] = None

    # ---- 4. same-size RANDOM-GROUPING control
    print('\n-- 4. SAME-SIZE RANDOM-GROUPING CONTROL --')
    print('   Does the 6-block partition beat a random partition of the same shape?')
    arch_within = obs['within_tensor'], obs['across_tensor_within_block']
    # architecture: within-block (excluding within-tensor) vs across-block
    arch_gap = obs['across_tensor_within_block'] - obs['across_block']
    rnd_gaps = []
    n_t = len(d['t_n'])
    for _ in range(args.nulls):
        perm = rng.permutation(n_t)
        rblk = np.empty(n_t, dtype=np.int64)
        pos = 0
        for b, nb in enumerate(BLOCK_SIZES):
            rblk[perm[pos:pos + nb]] = b
            pos += nb
        a, _ = strata(S, tid, rblk)
        rnd_gaps.append(a['across_tensor_within_block'] - a['across_block'])
    rnd_gaps = np.asarray(rnd_gaps)
    print('   architecture  within-block-minus-across-block gap = %+.4f pp' % (100 * arch_gap))
    print('   random same-size partitions (n=%d)                = %+.4f pp (sd %.4f)'
          % (len(rnd_gaps), 100 * rnd_gaps.mean(), 100 * rnd_gaps.std(ddof=1)))
    print('   ARCHITECTURE - RANDOM                             = %+.4f pp   p=%.4f'
          % (100 * (arch_gap - rnd_gaps.mean()), float((rnd_gaps >= arch_gap).mean())))
    res['random_grouping'] = dict(arch_gap_pp=float(100 * arch_gap),
                                  random_gap_pp=float(100 * rnd_gaps.mean()),
                                  random_sd_pp=float(100 * rnd_gaps.std(ddof=1)),
                                  arch_minus_random_pp=float(100 * (arch_gap - rnd_gaps.mean())),
                                  p=float((rnd_gaps >= arch_gap).mean()))
    del arch_within
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('dirs', nargs='+')
    ap.add_argument('--window', type=float, default=0.5,
                    help='steady window as a fraction of records (default last 50%%)')
    ap.add_argument('--nulls', type=int, default=200)
    ap.add_argument('--boot', type=int, default=200)
    ap.add_argument('--json', default='')
    args = ap.parse_args()

    rng = np.random.default_rng(12345)
    out = []
    for pdir in args.dirs:
        d = load_probe(pdir, args.window)
        r = run_one(d, args, rng)
        if r:
            out.append(r)
    if args.json:
        json.dump(out, open(args.json, 'w'), indent=1)
        print('\nwrote %s' % args.json)


if __name__ == '__main__':
    sys.exit(main())
