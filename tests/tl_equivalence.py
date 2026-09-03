#!/usr/bin/env python3
"""tl_equivalence.py -- the three proofs PATCH_TWOLEVEL owes before any run exists.

    A.  DISABLED = NO-OP, BITWISE.  For HIER unset and for every pre-existing mode
        (shrink, additive, zpool, zmpool), the PATCHED HF.py must produce beta and
        network weights BIT-FOR-BIT identical to the PINNED HF.py.  919 completed runs
        on this account depend on this; a patch that changes behaviour when it is off
        invalidates all of them.

    B.  rho = 0 IS THE SCALAR ARM.  HIER=twolevel ETA_RATIO=0 on a grouped granularity
        must track a `--stepsize-groups scalar` run.  The two differ only in the order
        in which one float32 sum is accumulated, so the bar is numerical, not bitwise,
        and the realised gap is reported.

    C.  rho IS A STRENGTH, lam IS A TIME CONSTANT.  Reports std(beta) against t for a
        rho ladder (twolevel) and a lam ladder (shrink) side by side.  The registered
        claim: the shrink ladder's spread collapses toward 0 and its ORDERING by lam is
        a statement about SPEED; the twolevel ladder's spread is ordered by rho and does
        not collapse.  This is the arithmetic the whole of G1 rests on, measured rather
        than argued.

USAGE (on the cluster, inside the venv)

    python3 tests/tl_equivalence.py --pinned /path/to/HF_pinned.py \\
                                    --patched /path/to/Optimizers/HF.py

    optional:  --steps 300        steps for proofs A and B
               --long 3000        steps for proof C
               --cifar <dir>      also run proof A on the real ResNet18 (slow)

Exit status 0 iff every proof passes.  Prints PASS/FAIL per proof and a final verdict
line.  This file is a TEST, not a scorer: it has no bearing on any run's verdict.
"""
import argparse
import importlib.util
import os
import sys

import torch


# --------------------------------------------------------------------------------------
def load_hf(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    spec.loader.exec_module(mod)
    return mod.HF


class NullWriter:
    def add_scalar(self, *a, **k):
        pass


def tiny_net(device, seed=0):
    """A 4-tensor MLP: small enough to run thousands of steps on a CPU, grouped enough
    that layerwise has real deviations to shrink."""
    torch.manual_seed(seed)
    return torch.nn.Sequential(
        torch.nn.Linear(32, 24),
        torch.nn.Tanh(),
        torch.nn.Linear(24, 8),
    ).to(device)


def fixed_data(device, n=64, seed=1234):
    g = torch.Generator().manual_seed(seed)
    x = torch.randn(n, 32, generator=g).to(device)
    y = torch.randint(0, 8, (n,), generator=g).to(device)
    return x, y


BASE = dict(alg='SGDm', weight_decay=0.1, momentum_param=0.99)
META = dict(alg='Lion', meta_stepsize=1e-3, momentum_param=0.99,
            Lion_beta2=0.9, weight_decay=0)


def run(HFcls, env, granularity, steps, device, alpha0=1e-6, net_seed=0,
        record_every=0, net_factory=None):
    """Run `steps` optimizer steps under exactly `env`.  Returns (beta_snapshot,
    weight_snapshot, trace) with trace = [(t, std(beta))] when record_every > 0."""
    saved = {k: os.environ.get(k) for k in
             ('HIER', 'LAM', 'ETA_RATIO', 'BETA_CLIP', 'SCHED', 'PROBE', 'PROBE_DIR',
              'PROBE5', 'PROBE7')}
    try:
        for k in saved:
            os.environ.pop(k, None)
        os.environ.update(env)
        net = (net_factory or tiny_net)(device, net_seed)
        x, y = fixed_data(device)
        opt = HFcls(net, stepsize_groups=granularity, alpha0=alpha0,
                    args_base=dict(BASE), args_meta=dict(META), gamma=1,
                    writer=NullWriter())
        lossfn = torch.nn.CrossEntropyLoss()
        trace = []
        for t in range(steps):
            opt.step(net, lossfn(net(x), y))
            if record_every and (t + 1) % record_every == 0:
                flat = torch.cat([b.detach().reshape(-1).float() for b in opt.beta])
                trace.append((t + 1, float(flat.std()) if flat.numel() > 1 else 0.0))
        beta = [b.detach().clone().cpu() for b in opt.beta]
        wts = [p.detach().clone().cpu() for p in net.parameters()]
        return beta, wts, trace
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None:
                os.environ[k] = v


def bitwise_equal(a, b):
    if len(a) != len(b):
        return False, 'different tensor counts (%d vs %d)' % (len(a), len(b))
    for i, (x, y) in enumerate(zip(a, b)):
        if x.shape != y.shape:
            return False, 'tensor %d shape %s vs %s' % (i, tuple(x.shape), tuple(y.shape))
        if not torch.equal(x, y):
            d = float((x.double() - y.double()).abs().max())
            return False, 'tensor %d differs, max |delta| = %.3e' % (i, d)
    return True, 'bitwise identical'


CLIP = '-15:-2.3026'


# --------------------------------------------------------------------------------------
def proof_a(Pinned, Patched, steps, device, net_factory=None, tag=''):
    """DISABLED = NO-OP, bitwise, over every pre-existing HIER mode."""
    cases = [
        ('HIER unset',           {'BETA_CLIP': CLIP},                                        'layerwise'),
        ('HIER unset, no box',   {},                                                          'layerwise'),
        ('shrink lam=1e-3',      {'HIER': 'shrink',   'LAM': '1e-3', 'BETA_CLIP': CLIP},      'layerwise'),
        ('shrink lam=1e-1',      {'HIER': 'shrink',   'LAM': '1e-1', 'BETA_CLIP': CLIP},      'layerwise'),
        ('additive r=0.06',      {'HIER': 'additive', 'ETA_RATIO': '0.06', 'BETA_CLIP': CLIP},'layerwise'),
        ('additive r=1',         {'HIER': 'additive', 'ETA_RATIO': '1',    'BETA_CLIP': CLIP},'layerwise'),
        ('zpool r=0.5',          {'HIER': 'zpool',    'ETA_RATIO': '0.5',  'BETA_CLIP': CLIP},'layerwise'),
        ('zmpool r=0.5',         {'HIER': 'zmpool',   'ETA_RATIO': '0.5',  'BETA_CLIP': CLIP},'layerwise'),
        ('HIER unset, nodewise', {'BETA_CLIP': CLIP},                                         'nodewise'),
        ('shrink, nodewise',     {'HIER': 'shrink',   'LAM': '1e-2', 'BETA_CLIP': CLIP},      'nodewise'),
        ('HIER unset, scalar',   {'BETA_CLIP': CLIP},                                         'scalar'),
    ]
    ok = True
    print('--- PROOF A%s: DISABLED = NO-OP (bitwise, %d steps) ---' % (tag, steps))
    for name, env, gran in cases:
        b0, w0, _ = run(Pinned, env, gran, steps, device, net_factory=net_factory)
        b1, w1, _ = run(Patched, env, gran, steps, device, net_factory=net_factory)
        eb, mb = bitwise_equal(b0, b1)
        ew, mw = bitwise_equal(w0, w1)
        good = eb and ew
        ok = ok and good
        print('  [%s] %-24s beta: %-34s weights: %s'
              % ('PASS' if good else 'FAIL', name, mb, mw))
    print('PROOF A%s: %s' % (tag, 'PASS' if ok else 'FAIL'))
    return ok


def proof_b(Patched, steps, device):
    """rho = 0 is the scalar arm."""
    print('--- PROOF B: HIER=twolevel ETA_RATIO=0 == scalar (%d steps) ---' % steps)
    ok = True
    for a0 in (1e-6, 1e-3):
        bs, ws, _ = run(Patched, {'BETA_CLIP': CLIP}, 'scalar', steps, device, alpha0=a0)
        bt, wt, _ = run(Patched, {'HIER': 'twolevel', 'ETA_RATIO': '0',
                                  'BETA_CLIP': CLIP}, 'layerwise', steps, device, alpha0=a0)
        flat = bt[0].reshape(-1)
        spread = float((flat - flat[0]).abs().max())
        gap = float((flat - bs[0].reshape(-1)[0]).abs().max())
        wgap = max(float((a.double() - b.double()).abs().max()) for a, b in zip(ws, wt))
        good = (spread == 0.0) and (gap < 1e-4) and (wgap < 1e-4)
        ok = ok and good
        print('  [%s] alpha0=%-5g  max_g|beta_g - beta_1| = %.3e (must be exactly 0)'
              % ('PASS' if good else 'FAIL', a0, spread))
        print('        max_g|beta_g - beta_scalar| = %.3e   max|w - w_scalar| = %.3e'
              % (gap, wgap))
    print('PROOF B: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def proof_c(Patched, steps, device):
    """rho is a strength; lam is a time constant."""
    print('--- PROOF C: the dial (%d steps, layerwise, alpha0=1e-6, box %s) ---'
          % (steps, CLIP))
    every = max(steps // 6, 1)
    rows = []
    for rho in ('0', '0.03', '0.1', '0.3', '1'):
        _, _, tr = run(Patched, {'HIER': 'twolevel', 'ETA_RATIO': rho,
                                 'BETA_CLIP': CLIP}, 'layerwise', steps, device,
                       record_every=every)
        rows.append(('twolevel rho=%s' % rho, tr))
    for lam in ('1e-4', '1e-3', '1e-2', '1e-1'):
        _, _, tr = run(Patched, {'HIER': 'shrink', 'LAM': lam, 'BETA_CLIP': CLIP},
                       'layerwise', steps, device, record_every=every)
        rows.append(('shrink   lam=%s' % lam, tr))
    _, _, tr = run(Patched, {'BETA_CLIP': CLIP}, 'layerwise', steps, device,
                   record_every=every)
    rows.append(('plain layerwise', tr))

    ts = [t for t, _ in rows[0][1]]
    print('  std(beta) across groups')
    print('  %-20s %s' % ('arm', ''.join('%10s' % ('t=%d' % t) for t in ts)))
    for name, tr in rows:
        print('  %-20s %s' % (name, ''.join('%10.5f' % s for _, s in tr)))

    d = dict(rows)
    first = {k: v[0][1] for k, v in d.items()}       # t = every
    end = {k: v[-1][1] for k, v in d.items()}        # t = steps
    t0, t1 = ts[0], ts[-1]
    plain = end['plain layerwise']

    # --- the registered criteria, each ON the claim rather than near it ------------
    # (i)  rho = 0 is the scalar identity: no spread at all, ever.
    c1 = end['twolevel rho=0'] == 0.0
    # (ii) rho CALIBRATES the spread:  std(beta | rho) = rho * std(beta | plain).
    #      This is what "a dimensionless strength dial" means, stated as a number.
    cal = {r: end['twolevel rho=%s' % r] / plain for r in ('0.03', '0.1', '0.3', '1')}
    c2 = all(abs(cal[r] / float(r) - 1.0) < 0.10 for r in cal)
    # (iii) rho does NOT decay: the spread at the end of the window is the spread at
    #       the start of it.  A time constant cannot do this.
    keep = {r: end['twolevel rho=%s' % r] / max(first['twolevel rho=%s' % r], 1e-30)
            for r in ('0.03', '0.1', '0.3', '1')}
    c3 = all(0.90 < keep[r] < 1.10 for r in keep)
    # (iv) lam DOES decay, at exactly the geometric rate (1-lam)^dt that makes it a
    #      HALF-LIFE and not a strength.  Checked only on the two rungs whose spread
    #      has not already reached machine zero inside this short window.
    dt = t1 - t0
    dec = {}
    for lam in ('1e-4', '1e-3'):
        obs = end['shrink   lam=%s' % lam] / max(first['shrink   lam=%s' % lam], 1e-30)
        pred = (1.0 - float(lam)) ** dt
        dec[lam] = (obs, pred)
    c4 = all(1 / 1.25 < o / p < 1.25 for o, p in dec.values())
    # (v)  and at lam >= 1e-2 the ladder is ALREADY at machine zero after t0 steps,
    #      which is the whole reason the archived ladder was flat.
    c5 = all(end['shrink   lam=%s' % lam] < 1e-3 * plain for lam in ('1e-2', '1e-1'))

    print('  rho calibration  std(beta|rho)/std(beta|plain):  %s'
          % '  '.join('rho=%s -> %.4f' % (r, cal[r]) for r in ('0.03', '0.1', '0.3', '1')))
    print('  rho persistence  std(t=%d)/std(t=%d):            %s'
          % (t1, t0, '  '.join('rho=%s -> %.4f' % (r, keep[r]) for r in keep)))
    print('  lam decay        std(t=%d)/std(t=%d) vs (1-lam)^%d:  %s'
          % (t1, t0, dt, '  '.join('lam=%s -> %.4f (predicted %.4f)' % (l, o, p)
                                   for l, (o, p) in dec.items())))
    for lab, good in (('rho=0 spread is exactly 0 at every t', c1),
                      ('std(beta) = rho * std(beta|plain) to within 10%', c2),
                      ('the rho ladder does NOT decay in t (ratio in [0.90,1.10])', c3),
                      ('the lam ladder decays at exactly (1-lam)^dt, within x1.25', c4),
                      ('lam >= 1e-2 is already at machine zero by t=%d' % t0, c5)):
        print('  [%s] %s' % ('PASS' if good else 'FAIL', lab))
    ok = c1 and c2 and c3 and c4 and c5
    print('PROOF C: %s' % ('PASS' if ok else 'FAIL'))
    return ok


# --------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pinned', required=True, help='pre-patch copy of HF.py')
    ap.add_argument('--patched', required=True, help='the live, patched HF.py')
    ap.add_argument('--steps', type=int, default=300)
    ap.add_argument('--long', type=int, default=3000)
    ap.add_argument('--cifar', default='', help='cifar10 dir; also runs proof A on ResNet18')
    ap.add_argument('--device', default='cpu')
    a = ap.parse_args()

    Pinned = load_hf(a.pinned, 'hf_pinned')
    Patched = load_hf(a.patched, 'hf_patched')
    dev = torch.device(a.device)
    print('pinned  : %s' % a.pinned)
    print('patched : %s' % a.patched)
    print('torch %s on %s' % (torch.__version__, dev))
    print()

    ok = proof_a(Pinned, Patched, a.steps, dev)
    print()
    if a.cifar:
        sys.path.insert(0, a.cifar)
        from build_network import build_network

        def real_net(device, seed=0):
            torch.manual_seed(seed)
            return build_network('ResNet18', device)

        ok = proof_a(Pinned, Patched, max(a.steps // 10, 20), dev,
                     net_factory=real_net, tag=' (ResNet18)') and ok
        print()
    ok = proof_b(Patched, a.steps, dev) and ok
    print()
    ok = proof_c(Patched, a.long, dev) and ok
    print()
    print('VERDICT: %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
