"""Verification suite for the BETA_SCHEDULE patch. CPU-only => bitwise reproducible."""
import os, sys, json, copy, importlib, itertools, shutil
import numpy as np, torch, torch.nn as nn

sys.path.insert(0, '/root/bs')
torch.use_deterministic_algorithms(True)

class W:                      # stub SummaryWriter
    def add_scalar(self, *a, **k): pass
    def add_scalars(self, *a, **k): pass

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.c = nn.Conv2d(3, 4, 3, padding=1); self.f = nn.Linear(4*8*8, 5)
    def forward(self, x): return self.f(torch.relu(self.c(x)).flatten(1))

AB = {'alg': 'SGDm', 'weight_decay': 0.1, 'momentum_param': 0.99}
AM = {'alg': 'Lion', 'meta_stepsize': 1e-3, 'momentum_param': 0.99,
      'Lion_beta2': 0.9, 'weight_decay': 0}

def data(n=64, seed=0):
    g = torch.Generator().manual_seed(seed)
    return [(torch.randn(8, 3, 8, 8, generator=g), torch.randint(0, 5, (8,), generator=g))
            for _ in range(n)]

def run(mod, sg, env, nsteps=120, seed=0, a0=1e-3):
    old = {k: os.environ.get(k) for k in
           ('BETA_SCHEDULE','BETA_TRACE','BETA_CLIP','HIER','LAM','ETA_RATIO',
            'PROBE','PROBE_DIR','BETA_SCHED_TAIL','BETA_SCHED_TOTAL','COS_TOTAL',
            'BETA_TRACE_FLUSH','BETA_TRACE_CAP','BETA_TRACE_EVERY')}
    for k in old: os.environ.pop(k, None)
    os.environ.update({k: str(v) for k, v in env.items()})
    try:
        torch.manual_seed(seed); np.random.seed(seed)
        net = Net()
        crit = nn.CrossEntropyLoss()
        HF = importlib.import_module(mod).HF
        opt = HF(net, stepsize_groups=sg, alpha0=a0, args_base=dict(AB),
                 args_meta=dict(AM), gamma=1, writer=W())
        betas = []
        for i, (x, y) in enumerate(itertools.islice(itertools.cycle(data(seed=seed)), nsteps)):
            opt.step(net, crit(net(x), y))
            betas.append(torch.cat([b.detach().reshape(-1) for b in opt.beta]).clone())
        return net, opt, torch.stack(betas)
    finally:
        for k, v in old.items():
            os.environ.pop(k, None)
            if v is not None: os.environ[k] = v

def same(n1, n2, b1, b2):
    ps = all(torch.equal(a, b) for a, b in zip(n1.parameters(), n2.parameters()))
    return ps and torch.equal(b1, b2)

FAIL = []
def check(name, cond, extra=''):
    print(('PASS  ' if cond else 'FAIL  ') + name + ('  ' + extra if extra else ''))
    if not cond: FAIL.append(name)

# ---------------- A. IDENTITY: schedule OFF == original, bit for bit ----------
print('--- A. identity (BETA_SCHEDULE/BETA_TRACE unset) ---')
CFGS = [('scalar', {}), ('scalar', {'BETA_CLIP': '-15:-2.3026'}),
        ([2, 2], {}), ('layerwise', {}), ('layerwise', {'BETA_CLIP': '-15:-2.3026'}),
        ('layerwise', {'BETA_CLIP': '-15:-2.3026', 'HIER': 'additive', 'ETA_RATIO': '0.2'}),
        ('layerwise', {'HIER': 'zmpool', 'ETA_RATIO': '0'}),
        ('nodewise', {'BETA_CLIP': '-15:-2.3026'}), ('weightwise', {'BETA_CLIP': '-15:-2.3026'}),
        ('nodewise', {'HIER': 'shrink', 'LAM': '0.1'})]
for sg, env in CFGS:
    n1, o1, b1 = run('Optimizers.HF_orig', sg, env)
    n2, o2, b2 = run('Optimizers.HF', sg, env)
    check('identity %-12s %s' % (sg, env or '{}'), same(n1, n2, b1, b2),
          'maxdiff=%.3g' % float((b1 - b2).abs().max()))

# identity of probe.jsonl bytes too
for sg in ('layerwise', 'weightwise'):
    outs = []
    for m, tag in (('Optimizers.HF_orig', 'o'), ('Optimizers.HF', 'p')):
        d = '/tmp/pr_%s_%s' % (sg, tag); shutil.rmtree(d, ignore_errors=True)
        run(m, sg, {'BETA_CLIP': '-15:-2.3026', 'PROBE': '10', 'PROBE_DIR': d})
        outs.append(open(d + '/probe.jsonl', 'rb').read())
    check('probe.jsonl byte-identical %s' % sg, outs[0] == outs[1],
          '%d bytes' % len(outs[0]))

for sg in ('layerwise', 'weightwise'):
    n1, o1, b1 = run('Optimizers.HF_orig', sg, {'BETA_CLIP': '-15:-2.3026'})
    n2, o2, b2 = run('Optimizers.HF', sg, {'BETA_CLIP': '-15:-2.3026',
                                           'BETA_TRACE': '/tmp/id_%s.npy' % sg})
    check('BETA_TRACE alone is read-only %s' % sg, same(n1, n2, b1, b2),
          'maxdiff=%.3g' % float((b1 - b2).abs().max()))

# ---------------- B. frozen ---------------------------------------------------
print('--- B. frozen ---')
for sg in ('scalar', 'layerwise', 'nodewise', 'weightwise'):
    n, o, b = run('Optimizers.HF', sg, {'BETA_SCHEDULE': 'frozen',
                                        'BETA_CLIP': '-15:-2.3026'})
    check('frozen %-11s beta constant at log(a0)' % sg,
          bool((b == np.float32(np.log(1e-3))).all()) and
          float(b.min()) == float(b.max()),
          'val=%.9g' % float(b[0, 0]))
n0, _, b0 = run('Optimizers.HF', 'layerwise', {'BETA_SCHEDULE': 'frozen'})
nf, _, bf = run('Optimizers.HF_orig', 'layerwise', {})
check('frozen actually changes the run', not torch.equal(b0, bf))

# ---------------- C. exact replay round-trip (the key arm) --------------------
print('--- C. dense trace -> replay reproduces the donor BITWISE ---')
for sg in ('scalar',):
    tp = '/tmp/tr_%s.npy' % sg
    n1, o1, b1 = run('Optimizers.HF', sg, {'BETA_TRACE': tp, 'BETA_CLIP': '-15:-2.3026',
                                           'BETA_TRACE_FLUSH': '7'})
    o1._btrace_flush()          # in a real run this is done by the atexit hook
    arr = np.load(tp)
    check('trace shape %s' % sg, arr.shape == (120, 2), str(arr.shape))
    check('trace col0==col1 for scalar', bool(np.array_equal(arr[:, 0], arr[:, 1])))
    check('trace == recorded beta', bool(np.allclose(arr[:, 0], b1[:, 0].numpy(), rtol=0, atol=0)))
    n2, o2, b2 = run('Optimizers.HF', sg, {'BETA_SCHEDULE': 'replay:%s#0' % tp,
                                           'BETA_CLIP': '-15:-2.3026'})
    check('replay(scalar) bitwise == donor', same(n1, n2, b1, b2),
          'maxdiff=%.3g' % float((b1 - b2).abs().max()))

# 2-D per-group replay: dump layerwise beta per step, replay it back
tpg = '/tmp/pg.npy'
n1, o1, b1 = run('Optimizers.HF', 'layerwise', {'BETA_CLIP': '-15:-2.3026'})
np.save(tpg, b1.numpy().astype(np.float64))
n2, o2, b2 = run('Optimizers.HF', 'layerwise', {'BETA_SCHEDULE': 'replay:%s' % tpg,
                                               'BETA_CLIP': '-15:-2.3026'})
check('replay 2-D per-group bitwise == donor', same(n1, n2, b1, b2),
      'maxdiff=%.3g' % float((b1 - b2).abs().max()))

# cross-granularity: scalar arm replaying a layerwise arm's param-weighted mean
tl = '/tmp/tr_lay.npy'
_, ol, _ = run('Optimizers.HF', 'layerwise', {'BETA_TRACE': tl, 'BETA_CLIP': '-15:-2.3026'})
ol._btrace_flush()
lay = np.load(tl)
np.save('/tmp/lay_pw.npy', lay[:, 0])
ns, os_, bs_ = run('Optimizers.HF', 'scalar',
                   {'BETA_SCHEDULE': 'replay:/tmp/lay_pw.npy', 'BETA_CLIP': '-15:-2.3026'})
check('scalar replays layerwise pw-mean', bool(np.allclose(
      bs_[:, 0].numpy().astype(np.float64), lay[:, 0].astype(np.float32).astype(np.float64),
      rtol=0, atol=0)), 'THE KEY ARM')
check('pw != gw on layerwise (weighting matters)',
      not np.allclose(lay[:, 0], lay[:, 1]),
      'max|pw-gw|=%.4g' % float(np.abs(lay[:, 0] - lay[:, 1]).max()))

# ---------------- D. clip interaction -----------------------------------------
print('--- D. beta_clip ---')
bad = np.linspace(-20.0, 0.0, 120)
np.save('/tmp/bad.npy', bad)
d = '/tmp/pr_clip'; shutil.rmtree(d, ignore_errors=True)
n, o, b = run('Optimizers.HF', 'layerwise',
              {'BETA_SCHEDULE': 'replay:/tmp/bad.npy', 'BETA_CLIP': '-15:-2.3026',
               'PROBE': '10', 'PROBE_DIR': d})
man = json.load(open(d + '/beta_schedule.json'))
check('clip: beta stays in box', float(b.min()) >= -15.0 - 1e-6 and float(b.max()) <= -2.3026 + 1e-6,
      '[%.4f,%.4f]' % (float(b.min()), float(b.max())))
check('clip: sched_clipped_steps reported', man['sched_clipped_steps'] > 0,
      str(man['sched_clipped_steps']))
rec = json.loads(open(d + '/probe.jsonl').readline())
check('probe carries sched_mode/sched_t', rec.get('sched_mode') == 'replay' and 'sched_t' in rec,
      str({k: rec[k] for k in rec if k.startswith('sched')}))
n2, o2, b2 = run('Optimizers.HF', 'layerwise', {'BETA_SCHEDULE': 'replay:/tmp/bad.npy'})
check('no clip => schedule followed exactly', float(b2.min()) < -15.0)

# ---------------- E. tail / cosine / errors -----------------------------------
print('--- E. tail, cosine, guards ---')
np.save('/tmp/short.npy', np.full(10, -8.0))
n, o, b = run('Optimizers.HF', 'scalar', {'BETA_SCHEDULE': 'replay:/tmp/short.npy'})
check('tail hold', float(b[-1, 0]) == np.float32(-8.0) and o._sched_tail_holds == 110,
      'holds=%d' % o._sched_tail_holds)
try:
    run('Optimizers.HF', 'scalar', {'BETA_SCHEDULE': 'replay:/tmp/short.npy',
                                    'BETA_SCHED_TAIL': 'error'})
    check('tail error raises', False)
except IndexError:
    check('tail error raises', True)
n, o, b = run('Optimizers.HF', 'layerwise',
              {'BETA_SCHEDULE': 'cosine:-6.907755:-11.0', 'BETA_SCHED_TOTAL': '120'})
check('cosine endpoints', abs(float(b[0, 0]) + 6.907755) < 3e-6 and abs(float(b[-1, 0]) + 11.0) < 3e-6,
      '%.6f -> %.6f' % (float(b[0, 0]), float(b[-1, 0])))
try:
    run('Optimizers.HF', 'layerwise', {'BETA_SCHEDULE': 'frozen', 'HIER': 'additive'})
    check('HIER+BETA_SCHEDULE refused', False)
except ValueError:
    check('HIER+BETA_SCHEDULE refused', True)
try:
    run('Optimizers.HF', 'layerwise', {'BETA_SCHEDULE': 'bogus'}); check('bad spec refused', False)
except ValueError:
    check('bad spec refused', True)

# ---------------- F. float32 / ulp accounting ---------------------------------
print('--- F. float32 resolution ---')
d = '/tmp/pr_ulp'; shutil.rmtree(d, ignore_errors=True)
tiny = -6.907755 + 1e-9 * np.arange(120)      # increments 1e-9 << ulp 4.77e-7
np.save('/tmp/tiny.npy', tiny)
n, o, b = run('Optimizers.HF', 'scalar', {'BETA_SCHEDULE': 'replay:/tmp/tiny.npy',
                                          'PROBE': '10', 'PROBE_DIR': d})
man = json.load(open(d + '/beta_schedule.json'))
check('sub-ulp fraction reported ~1', man['sched_subulp_frac'] > 0.99,
      '%.4f' % man['sched_subulp_frac'])
check('assignment error <= half ulp', man['sched_max_round_err'] <= np.spacing(np.float32(6.907755)) / 2 + 1e-12,
      '%.3g vs ulp/2=%.3g' % (man['sched_max_round_err'], np.spacing(np.float32(6.907755)) / 2))
check('sub-ulp target => staircase, no drift-away',
      abs(float(b[-1, 0]) - tiny[-1]) < np.spacing(np.float32(6.907755)),
      'final %.9f vs target %.9f' % (float(b[-1, 0]), tiny[-1]))
d2 = '/tmp/pr_ulp2'; shutil.rmtree(d2, ignore_errors=True)
run('Optimizers.HF', 'scalar', {'BETA_SCHEDULE': 'replay:/tmp/lay_pw.npy', 'PROBE': '10',
                                'PROBE_DIR': d2, 'BETA_CLIP': '-15:-2.3026'})
m2 = json.load(open(d2 + '/beta_schedule.json'))
check('real trajectory is above the ulp floor', m2['sched_subulp_frac'] < 0.5,
      'subulp=%.4f initgap=%.3g' % (m2['sched_subulp_frac'], m2['sched_init_gap']))

np.save('/tmp/a6.npy', np.linspace(-13.815510557964274, -12.0, 120))
n, o, b = run('Optimizers.HF', 'layerwise', {'BETA_SCHEDULE': 'replay:/tmp/a6.npy',
                                             'BETA_CLIP': '-15:-2.3026'}, a0=1e-6)
_u = float(np.spacing(np.float32(13.8155)))
check('a0=1e-6 magnitude replay',
      abs(float(b[0, 0]) + 13.815510557964274) < _u and abs(float(b[-1, 0]) + 12.0) < _u,
      'ulp(13.8155)=%.4e  %.7f -> %.7f' % (_u, float(b[0, 0]), float(b[-1, 0])))

# ---------------- G. cost / no-alloc at weightwise ----------------------------
print('--- G. weightwise broadcast ---')
np.save('/tmp/one.npy', np.full(200, -8.0))
n, o, b = run('Optimizers.HF', 'weightwise', {'BETA_SCHEDULE': 'replay:/tmp/one.npy',
                                              'BETA_CLIP': '-15:-2.3026'}, nsteps=30)
check('weightwise 1-D broadcast', bool((b == np.float32(-8.0)).all()) and
      o.beta[0].shape == n.c.weight.shape, str(tuple(o.beta[0].shape)))
check('weightwise broadcast is a stride-0 view (no alloc)',
      o.beta[0].stride() == (0,) * o.beta[0].dim(), str(o.beta[0].stride()))

# ---------------- H. atexit flush in a real process ---------------------------
print('--- H. atexit flush (real process exit) ---')
import subprocess, textwrap
prog = textwrap.dedent('''
    import os, sys
    os.environ['BETA_TRACE'] = '/tmp/ax.npy'; os.environ['BETA_TRACE_FLUSH'] = '1000'
    sys.argv = ['x']; sys.path.insert(0, '/root/bs')
    exec(open('/root/bs/t_bsched.py').read().split('FAIL = []')[0])
    run('Optimizers.HF', 'layerwise', {'BETA_TRACE': '/tmp/ax.npy',
                                       'BETA_TRACE_FLUSH': '1000'}, nsteps=25)
''')
subprocess.run([sys.executable, '-c', prog], check=True,
               capture_output=True, env=dict(os.environ, CUDA_VISIBLE_DEVICES=''))
ax = np.load('/tmp/ax.npy')
check('atexit flushed all 25 rows', ax.shape == (25, 2), str(ax.shape))

print()
print('FAILURES: %d %s' % (len(FAIL), FAIL))
sys.exit(1 if FAIL else 0)
