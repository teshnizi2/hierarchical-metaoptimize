#!/usr/bin/env python3
"""ebjz_probe.py -- resolve the one FAIL from the landing audit.

The landing audit found HIER=ebjz produced a state hash identical to the plain arm.
That was measured on a 4-tensor MLP, i.e. m=4 layerwise groups, and the James-Stein
factor carries an (m-3) numerator -- so m=4 is very nearly the degenerate case and may
not be diagnostic.  This re-runs the SAME comparison at the PRODUCTION group count:
ResNet18, layerwise, m=62, exactly what eb1 submits.
"""
import hashlib, importlib.util, os, sys
from importlib.machinery import SourceFileLoader
import torch

CIF = '/home/s5014158/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10'
sys.path.insert(0, CIF)

def load_mod(path, alias):
    ld = SourceFileLoader(alias, path)
    m = importlib.util.module_from_spec(importlib.util.spec_from_loader(alias, ld))
    sys.modules[alias] = m; ld.exec_module(m); return m

class NullWriter:
    def add_scalar(self, *a, **k): pass

BASE = dict(alg='SGDm', weight_decay=0.1, momentum_param=0.99)
META = dict(alg='Lion', meta_stepsize=1e-3, momentum_param=0.99,
            Lion_beta2=0.9, weight_decay=0)
ENVKEYS = ('HIER','LAM','ETA_RATIO','BETA_CLIP','SCHED','PROBE','PROBE_DIR',
           'PROBE5','PROBE7','EB_RHO','EB_LOG')
CLIP = '-15:-2.3026'

bn = load_mod(CIF + '/build_network.py', 'bn_probe')
HF = load_mod(CIF + '/Optimizers/HF.py', 'hf_probe').HF

def run(env, gran, steps, alpha0=1e-6):
    saved = {k: os.environ.get(k) for k in ENVKEYS}
    try:
        for k in ENVKEYS: os.environ.pop(k, None)
        os.environ.update(env)
        torch.manual_seed(11)
        net = bn.build_network('ResNet18', 'cpu')
        g = torch.Generator().manual_seed(99)
        x = torch.randn(16, 3, 32, 32, generator=g)
        y = torch.randint(0, 10, (16,), generator=g)
        opt = HF(net, stepsize_groups=gran, alpha0=alpha0,
                 args_base=dict(BASE), args_meta=dict(META), gamma=1,
                 writer=NullWriter())
        lf = torch.nn.CrossEntropyLoss()
        for _ in range(steps):
            opt.step(net, lf(net(x), y))
        flat = torch.cat([b.detach().reshape(-1).float() for b in opt.beta])
        h = hashlib.sha256()
        for b in opt.beta: h.update(b.detach().double().numpy().tobytes())
        return h.hexdigest(), len(opt.beta), float(flat.std()), float(flat.mean())
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None: os.environ[k] = v

STEPS = int(os.environ.get('PROBE_STEPS', '120'))
print('ResNet18 / layerwise / alpha0=1e-6 / %d steps  (production group count)\n' % STEPS)
arms = [('plain (HIER unset)', {'BETA_CLIP': CLIP}),
        ('ebjs',               {'HIER': 'ebjs', 'BETA_CLIP': CLIP}),
        ('ebjz',               {'HIER': 'ebjz', 'BETA_CLIP': CLIP}),
        ('ebjs EB_RHO=0.9',    {'HIER': 'ebjs', 'EB_RHO': '0.9', 'BETA_CLIP': CLIP}),
        ('additive r=0.06',    {'HIER': 'additive', 'ETA_RATIO': '0.06', 'BETA_CLIP': CLIP}),
        ('additive r=1',       {'HIER': 'additive', 'ETA_RATIO': '1', 'BETA_CLIP': CLIP})]
res = {}
for label, env in arms:
    hh, m, sd, mu = run(env, 'layerwise', STEPS)
    res[label] = hh
    print('  %-22s m=%3d  hash=%s  std(beta)=%.6e  mean=%.6f' % (label, m, hh[:16], sd, mu))

plain = res['plain (HIER unset)']
print()
ok = True
for label in ('ebjs', 'ebjz', 'ebjs EB_RHO=0.9'):
    same = res[label] == plain
    print('  %-22s %s' % (label, 'INERT -- identical to plain  <-- PROBLEM' if same
                          else 'ACTIVE -- differs from plain'))
    if same: ok = False
print()
print('m=4 CONTROL (the landing audit testbed), same comparison:')
sys.path.insert(0, '/home/s5014158/metaopt')
print('VERDICT: %s' % ('PASS -- every eb1 arm is live at m=62'
                       if ok else 'FAIL -- an eb1 arm is inert at m=62'))
sys.exit(0 if ok else 1)
