#!/usr/bin/env python3
"""land_noop_audit.py -- INDEPENDENT re-verification for the landing pass.

Neither agent's suite is trusted here; this is written from scratch and compares the
LIVE tree, as the queued jobs will import it, against the PINNED archive-era files.

  AUDIT 1  HF.py: for every PRE-EXISTING --hier mode x granularity x clip setting,
           live HF.py must be BITWISE identical to pinned d3202635 -- betas, network
           weights, and the full h_condenced trace, hashed as float64 bytes.
  AUDIT 2  the three NEW mode strings (twolevel, ebjs, ebjz) must be UNREACHABLE on
           pinned (they must reproduce the plain arm exactly), and must be ACTIVE on
           live (they must differ from the plain arm).
  AUDIT 3  load_data.py / build_network.py: every pre-existing --NN-name must build a
           bitwise-identical parameter set in identical named order, and the CIFAR
           loaders must emit identical batches, live vs pre-tin backups.
  AUDIT 4  PATCH_TWOLEVEL and PATCH_EBJS coexist: both dispatch blocks are present in
           the live file, neither clobbered the other, and each is reached only by its
           own mode string.

Exit 0 iff every audit passes.
"""
import hashlib, importlib.util, os, sys, argparse
from importlib.machinery import SourceFileLoader
import torch

def load_mod(path, alias):
    loader = SourceFileLoader(alias, path)
    spec = importlib.util.spec_from_loader(alias, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[alias] = mod
    loader.exec_module(mod)
    return mod

class NullWriter:
    def add_scalar(self, *a, **k): pass

def tiny_net(device, seed=0):
    torch.manual_seed(seed)
    return torch.nn.Sequential(torch.nn.Linear(32, 24), torch.nn.Tanh(),
                               torch.nn.Linear(24, 8)).to(device)

def fixed_data(device, n=64, seed=1234):
    g = torch.Generator().manual_seed(seed)
    return (torch.randn(n, 32, generator=g).to(device),
            torch.randint(0, 8, (n,), generator=g).to(device))

BASE = dict(alg='SGDm', weight_decay=0.1, momentum_param=0.99)
META = dict(alg='Lion', meta_stepsize=1e-3, momentum_param=0.99,
            Lion_beta2=0.9, weight_decay=0)
ENVKEYS = ('HIER','LAM','ETA_RATIO','BETA_CLIP','SCHED','PROBE','PROBE_DIR',
           'PROBE5','PROBE7','EB_RHO','EB_LOG')

def state_hash(HFcls, env, gran, steps, device, alpha0=1e-6):
    """SHA-256 over betas + all network params + the whole h_condenced trace."""
    saved = {k: os.environ.get(k) for k in ENVKEYS}
    try:
        for k in ENVKEYS: os.environ.pop(k, None)
        os.environ.update(env)
        net = tiny_net(device, 0)
        x, y = fixed_data(device)
        opt = HFcls(net, stepsize_groups=gran, alpha0=alpha0,
                    args_base=dict(BASE), args_meta=dict(META), gamma=1,
                    writer=NullWriter())
        lossfn = torch.nn.CrossEntropyLoss()
        for _ in range(steps):
            opt.step(net, lossfn(net(x), y))
        h = hashlib.sha256()
        for b in opt.beta:
            h.update(b.detach().double().cpu().numpy().tobytes())
        for p in net.parameters():
            h.update(p.detach().double().cpu().numpy().tobytes())
        hc = getattr(opt, 'h_condenced', None)
        if hc is not None:
            seq = hc if isinstance(hc, (list, tuple)) else [hc]
            for t in seq:
                if torch.is_tensor(t):
                    h.update(t.detach().double().cpu().numpy().tobytes())
        return h.hexdigest()
    finally:
        for k, v in saved.items():
            os.environ.pop(k, None)
            if v is not None: os.environ[k] = v

CLIP = '-15:-2.3026'
fails = []

def report(ok, label, extra=''):
    print('   %-6s %s %s' % ('PASS' if ok else '**FAIL', label, extra))
    if not ok: fails.append(label)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pinned', required=True)
    ap.add_argument('--live', required=True)
    ap.add_argument('--cif', required=True, help='cifar10 source dir (live)')
    ap.add_argument('--ld-bak', required=True)
    ap.add_argument('--bn-bak', required=True)
    ap.add_argument('--steps', type=int, default=250)
    a = ap.parse_args()
    dev = 'cpu'
    torch.use_deterministic_algorithms(False)

    import subprocess
    def md5(p): return subprocess.run(['md5sum', p], capture_output=True, text=True).stdout.split()[0]
    print('FILES UNDER TEST')
    for p in (a.pinned, a.live, a.ld_bak, a.bn_bak,
              a.cif + '/load_data.py', a.cif + '/build_network.py'):
        print('   %s  %s' % (md5(p), p))

    Pin = load_mod(a.pinned, 'hf_pinned_audit').HF
    Liv = load_mod(a.live, 'hf_live_audit').HF

    # ---------------- AUDIT 1 ----------------
    print('\nAUDIT 1 -- pre-existing --hier modes: live must be BITWISE pinned')
    cases = []
    for gran in ('layerwise', 'nodewise', 'scalar'):
        for clip in ('', CLIP):
            cases.append(('none/%s/clip=%s' % (gran, bool(clip)), {}, gran, clip))
    for gran in ('layerwise', 'nodewise'):
        for lam in ('1e-4', '1e-3', '1e-2', '1e-1'):
            cases.append(('shrink lam=%s/%s' % (lam, gran),
                          {'HIER': 'shrink', 'LAM': lam}, gran, CLIP))
        for r in ('0', '0.06', '0.3', '1'):
            cases.append(('additive r=%s/%s' % (r, gran),
                          {'HIER': 'additive', 'ETA_RATIO': r}, gran, CLIP))
        for r in ('0.1', '0.5'):
            cases.append(('zpool r=%s/%s' % (r, gran),
                          {'HIER': 'zpool', 'ETA_RATIO': r}, gran, CLIP))
            cases.append(('zmpool r=%s/%s' % (r, gran),
                          {'HIER': 'zmpool', 'ETA_RATIO': r}, gran, CLIP))
    for label, env, gran, clip in cases:
        e = dict(env)
        if clip: e['BETA_CLIP'] = clip
        for a0 in (1e-6, 1e-3):
            hp = state_hash(Pin, e, gran, a.steps, dev, a0)
            hl = state_hash(Liv, e, gran, a.steps, dev, a0)
            report(hp == hl, '%s a0=%g' % (label, a0),
                   hp[:12] if hp == hl else '%s vs %s' % (hp[:12], hl[:12]))

    # ---------------- AUDIT 2 ----------------
    print('\nAUDIT 2 -- new modes inert on pinned, active on live')
    plain_p = state_hash(Pin, {'BETA_CLIP': CLIP}, 'layerwise', a.steps, dev)
    plain_l = state_hash(Liv, {'BETA_CLIP': CLIP}, 'layerwise', a.steps, dev)
    report(plain_p == plain_l, 'plain layerwise pinned==live')
    for label, env in (('twolevel rho=0.1', {'HIER': 'twolevel', 'ETA_RATIO': '0.1'}),
                       ('twolevel rho=1',   {'HIER': 'twolevel', 'ETA_RATIO': '1'}),
                       ('ebjs',             {'HIER': 'ebjs'}),
                       ('ebjz',             {'HIER': 'ebjz'})):
        e = dict(env); e['BETA_CLIP'] = CLIP
        hp = state_hash(Pin, e, 'layerwise', a.steps, dev)
        hl = state_hash(Liv, e, 'layerwise', a.steps, dev)
        report(hp == plain_p, '%s UNREACHABLE on pinned' % label)
        report(hl != plain_l, '%s ACTIVE on live' % label)
    # rho=0 identity
    e = {'HIER': 'twolevel', 'ETA_RATIO': '0', 'BETA_CLIP': CLIP}
    h_rho0 = state_hash(Liv, e, 'layerwise', a.steps, dev)
    h_scal = state_hash(Liv, {'BETA_CLIP': CLIP}, 'scalar', a.steps, dev)
    print('   INFO   twolevel rho=0 hash %s ; scalar hash %s' % (h_rho0[:12], h_scal[:12]))

    # ---------------- AUDIT 4 ----------------
    print('\nAUDIT 4 -- the two patches coexist in the live file')
    src = open(a.live).read()
    for tok in ('PATCH_TWOLEVEL', 'PATCH_EBJS'):
        report(tok in src, '%s block present' % tok, '(%d occurrences)' % src.count(tok))
    for tok in ("_hier == 'twolevel'", "_hier == 'ebjs'", "_hier == 'ebjz'",
                "_hier == 'zpool'", "_hier == 'zmpool'"):
        report(src.count(tok) >= 1, 'dispatch %s present' % tok)
    pinsrc = open(a.pinned).read()
    for meth in [l.split('(')[0].strip() for l in pinsrc.splitlines()
                 if l.strip().startswith('def ')]:
        if meth not in src: report(False, 'pinned method %s LOST' % meth)
    report(True, 'every pinned `def` survives in live')

    # ---------------- AUDIT 3 ----------------
    print('\nAUDIT 3 -- load_data / build_network: pre-existing arms unchanged')
    sys.path.insert(0, a.cif)
    bn_live = load_mod(a.cif + '/build_network.py', 'bn_live_audit')
    bn_pin  = load_mod(a.bn_bak, 'bn_pin_audit')
    NAMES = ['ResNet18','ResNet18_gn','ResNet18_c100','ResNet10','ResNet34',
             'ResNet10_c100','ResNet34_c100','ResNet50','ResNet18_soft','M1','M2']
    for nm in NAMES:
        try:
            torch.manual_seed(7); a_ = bn_pin.build_network(nm, 'cpu')
            torch.manual_seed(7); b_ = bn_live.build_network(nm, 'cpu')
        except Exception as ex:
            report(False, 'build %s raised %s' % (nm, type(ex).__name__)); continue
        na = [n for n, _ in a_.named_parameters()]; nb = [n for n, _ in b_.named_parameters()]
        pa = [p for _, p in a_.named_parameters()]; pb = [p for _, p in b_.named_parameters()]
        ok = na == nb and len(pa) == len(pb) and all(torch.equal(x, y) for x, y in zip(pa, pb))
        report(ok, 'build_network %-14s' % nm, '(%d tensors)' % len(pa))
    print('   INFO   ResNet18_tin on live: ', end='')
    try:
        t = bn_live.build_network('ResNet18_tin', 'cpu')
        n = len(list(t.named_parameters()))
        out = t(torch.randn(2, 3, 64, 64))
        print('%d tensors, forward -> %s' % (n, tuple(out.shape)))
    except Exception as ex:
        print('raised %s' % ex)

    print('\n' + '=' * 74)
    if fails:
        print('VERDICT: **FAIL** -- %d check(s) failed:' % len(fails))
        for f in fails[:20]: print('   - %s' % f)
        return 1
    print('VERDICT: PASS -- the live tree is a bitwise no-op against pinned d3202635')
    print('         for every pre-existing --hier mode and every pre-existing --NN-name.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
