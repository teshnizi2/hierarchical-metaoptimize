import os, sys, torch
sys.path.insert(0, "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10")
from build_network import build_network
from Optimizers.HF import HF
class W:
    def add_scalar(self, *a, **k): pass
    def add_scalars(self, *a, **k): pass
    def add_histogram(self, *a, **k): pass
META = {"alg": "Lion", "meta_stepsize": 1e-3, "momentum_param": 0.99, "Lion_beta2": 0.9, "weight_decay": 0}
ADAMW = {"alg": "AdamW", "weight_decay": 0.1, "momentum_param": 0.9, "normalizer_param": 0.999}
x = torch.randn(8, 3, 32, 32); y = torch.randint(0, 10, (8,)); lf = torch.nn.CrossEntropyLoss()
for hier, ratio in [("", ""), ("additive", "0.06"), ("additive", "1")]:
    os.environ.pop("HIER", None); os.environ.pop("ETA_RATIO", None)
    if hier:
        os.environ["HIER"] = hier; os.environ["ETA_RATIO"] = ratio
    os.environ["BETA_CLIP"] = "-15:-2.3026"
    net = build_network("ResNet18", torch.device("cpu"))
    label = (hier + "/r=" + ratio) if hier else "plain"
    try:
        opt = HF(net, stepsize_groups="resnet18_blocks", alpha0=1e-6, args_base=dict(ADAMW),
                 args_meta=dict(META), gamma=1, writer=W())
        for _ in range(3):
            l = lf(net(x), y); opt.step(net, l)
        b = opt.beta if isinstance(opt.beta, list) else [opt.beta]
        a = torch.cat([t.reshape(-1) for t in b])
        print("blk6 %-14s OK   m=%d  beta=[%.4f,%.4f]  finite=%s" %
              (label, sum(t.numel() for t in b), a.min(), a.max(), bool(torch.isfinite(a).all())))
    except Exception as e:
        print("blk6 %-14s FAILS  %s: %s" % (label, type(e).__name__, e))
