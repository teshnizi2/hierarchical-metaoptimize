# Pure-compute ceiling: real ResNet-18(489) + the real campaign HF optimizer,
# fed from a resident random tensor so the input pipeline contributes ZERO.
# This separates "the GPU is the limit" from "BeeGFS is the limit", and it is the
# only way to see the per-granularity optimizer overhead, because in the smoke
# every arm was data-bound and therefore identical.
import sys, time, os
sys.path.insert(0,'/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10')
import torch, torch.nn as nn, torchvision.models as models
from torch.utils.tensorboard import SummaryWriter
from Optimizers.HF import HF
dev=torch.device('cuda'); torch.backends.cudnn.benchmark=True
BS=256
x=torch.randn(BS,3,224,224,device=dev); y=torch.randint(0,489,(BS,),device=dev)
crit=nn.CrossEntropyLoss().to(dev)
print("GPU:",torch.cuda.get_device_name(0),flush=True)
for g in ['scalar','layerwise','nodewise']:
    net=models.resnet18(num_classes=489).to(dev)
    opt=HF(net,stepsize_groups=g,alpha0=1e-6,
           args_base={'alg':'SGDm','momentum_param':0.99,'weight_decay':0.1},
           args_meta={'alg':'Lion','momentum_param':0.99,'Lion_beta2':0.9,
                      'weight_decay':0.0,'meta_stepsize':3e-2},
           gamma=1,writer=SummaryWriter('/data1/salehkaleybars/metaopt/scratch_in489/tb_'+g))
    m=int(sum(b.numel() if b.dim()>0 else 1 for b in opt.beta))
    for _ in range(10):                      # warmup
        opt.step(net,crit(net(x),y))
    torch.cuda.synchronize(); t=time.time(); N=40
    for _ in range(N):
        opt.step(net,crit(net(x),y))
    torch.cuda.synchronize(); d=time.time()-t
    ips=N*BS/d
    print("GPUONLY groups=%-10s m=%-6d steps=%d sec=%.2f IMG_PER_SEC %.1f  full_epoch_min %.1f"
          %(g,m,N,d,ips,627200/ips/60),flush=True)
