import os,sys,time,importlib,itertools
import numpy as np, torch, torch.nn as nn
sys.path.insert(0,'/root/bs')
exec(open('/root/bs/t_bsched.py').read().split('FAIL = []')[0])
import torchvision
dev='cuda'
def mk():
    m=torchvision.models.resnet18(num_classes=10); return m.to(dev)
def timed(sg, env, nsteps=60):
    for k in list(env): os.environ[k]=str(env[k])
    torch.manual_seed(0); net=mk(); crit=nn.CrossEntropyLoss().to(dev)
    HF=importlib.import_module('Optimizers.HF').HF
    o=HF(net,stepsize_groups=sg,alpha0=1e-3,args_base=dict(AB),args_meta=dict(AM),gamma=1,writer=W())
    x=torch.randn(100,3,32,32,device=dev); y=torch.randint(0,10,(100,),device=dev)
    for _ in range(10): o.step(net,crit(net(x),y))
    torch.cuda.synchronize(); t=time.time()
    for _ in range(nsteps): o.step(net,crit(net(x),y))
    torch.cuda.synchronize(); dt=(time.time()-t)/nsteps*1000
    for k in list(env): os.environ.pop(k,None)
    return dt
np.save('/tmp/flat.npy', np.full(200000,-7.0))
for sg in ('scalar','layerwise','weightwise'):
    base=timed(sg,{'BETA_CLIP':'-15:-2.3026'})
    rep =timed(sg,{'BETA_CLIP':'-15:-2.3026','BETA_SCHEDULE':'replay:/tmp/flat.npy'})
    tr  =timed(sg,{'BETA_CLIP':'-15:-2.3026','BETA_TRACE':'/tmp/pf.npy','BETA_TRACE_FLUSH':'1000'})
    print('R18/%-11s base %7.2f ms  replay %7.2f (%+.1f%%)  trace %7.2f (%+.1f%%)'
          %(sg,base,rep,100*(rep/base-1),tr,100*(tr/base-1)))
