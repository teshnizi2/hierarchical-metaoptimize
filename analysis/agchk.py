"""Cycle-28 zero-GPU structural check: AdamW BASE x {blk6, nodewise, weightwise} x
{plain, M1 additive}, the exact arms `ag-*`/`ap-*` are about to queue.  Cycle-18 gotcha 5."""
import os, sys, torch
sys.path.insert(0, "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10")
from build_network import build_network
from Optimizers.HF import HF
dev = torch.device("cpu")
META = {"alg": "Lion", "meta_stepsize": 1e-3, "momentum_param": 0.99, "Lion_beta2": 0.9, "weight_decay": 0}
ADAMW = {"alg": "AdamW", "weight_decay": 0.1, "momentum_param": 0.9, "normalizer_param": 0.999}
x = torch.randn(8, 3, 32, 32); y = torch.randint(0, 10, (8,))
lossf = torch.nn.CrossEntropyLoss()
for g in ["resnet18_blocks", "nodewise", "weightwise"]:
    for hier, ratio in [("", ""), ("additive", "0.06"), ("additive", "1")]:
        os.environ.pop("HIER", None); os.environ.pop("ETA_RATIO", None)
        if hier:
            os.environ["HIER"] = hier; os.environ["ETA_RATIO"] = ratio
        os.environ["BETA_CLIP"] = "-15:-2.3026"
        net = build_network("ResNet18", dev)
        tag = f"{g:16s} {(hier+'/r='+ratio) if hier else 'plain':14s}"
        try:
            opt = HF(net, stepsize_groups=g, alpha0=1e-6, args_base=dict(ADAMW),
                     args_meta=dict(META), gamma=1, writer=None)
            for _ in range(3):
                loss = lossf(net(x), y)
                opt.step(net, loss)
            b = opt.beta if isinstance(opt.beta, list) else [opt.beta]
            n = sum(t.numel() for t in b)
            a = torch.cat([t.reshape(-1) for t in b])
            print(f"{tag} OK   m={n:>10,}  loss={loss.item():.3f}  "
                  f"beta[min,max]=[{a.min():.4f},{a.max():.4f}]  finite={bool(torch.isfinite(a).all())}")
        except Exception as e:
            print(f"{tag} FAILS  {type(e).__name__}: {e}")
