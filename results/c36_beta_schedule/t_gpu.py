import os, sys, importlib, itertools, json
import numpy as np, torch, torch.nn as nn
sys.path.insert(0,'/root/bs')
exec(open('/root/bs/t_bsched.py').read().split('FAIL = []')[0])
dev='cuda'
class NetG(nn.Module):
    def __init__(s):
        super().__init__(); s.c=nn.Conv2d(3,4,3,padding=1); s.f=nn.Linear(4*8*8,5)
    def forward(s,x): return s.f(torch.relu(s.c(x)).flatten(1))
def rung(sg, env, nsteps=200, a0=1e-3):
    for k in list(env): os.environ[k]=str(env[k])
    torch.manual_seed(0); np.random.seed(0)
    net=NetG().to(dev); crit=nn.CrossEntropyLoss().to(dev)
    HF=importlib.import_module('Optimizers.HF').HF
    o=HF(net,stepsize_groups=sg,alpha0=a0,args_base=dict(AB),args_meta=dict(AM),gamma=1,writer=W())
    bs=[]
    for x,y in itertools.islice(itertools.cycle(data()),nsteps):
        o.step(net,crit(net(x.to(dev)),y.to(dev)))
        bs.append(torch.cat([b.detach().reshape(-1) for b in o.beta]).float().cpu().clone())
    for k in list(env): os.environ.pop(k,None)
    return o, torch.stack(bs)
arr=np.load('/root/bs/real_lay_pw.npy')
print('array', arr.shape, arr.dtype, arr[:3], arr[-1])
ok=True
for sg in ('scalar','layerwise','nodewise','weightwise'):
    o,b = rung(sg, {'BETA_SCHEDULE':'replay:/root/bs/real_lay_pw.npy','BETA_CLIP':'-15:-2.3026',
                    'PROBE':'50','PROBE_DIR':'/tmp/g_%s'%sg})
    tgt = arr[:b.shape[0]].astype(np.float32)
    good = np.array_equal(b[:,0].numpy(), tgt) and bool((b==b[:,:1]).all())
    print('GPU %-11s beta==array %s  dev(beta)=%s  final=%.6f' % (sg, good, o.beta[0].device, float(b[-1,0])))
    ok &= good
    m=json.load(open('/tmp/g_%s/beta_schedule.json'%sg))
    print('    manifest: T=%d clipped=%d subulp=%.4f initgap=%.3g dev=%s'
          % (m['sched_T'],m['sched_clipped_steps'],m['sched_subulp_frac'],m['sched_init_gap'],m['beta_device']))
o,b = rung('layerwise', {'BETA_TRACE':'/tmp/g_tr.npy','BETA_CLIP':'-15:-2.3026'})
o._btrace_flush(); tr=np.load('/tmp/g_tr.npy')
print('GPU trace', tr.shape, 'pw/gw differ:', not np.allclose(tr[:,0],tr[:,1]))
print('GPU OK' if ok else 'GPU FAIL')
