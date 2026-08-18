"""Does the cifar10 HF optimizer actually support layerwise/nodewise/weightwise?
Instantiate only (no training) and report per-granularity status."""
import sys, traceback
sys.path.insert(0, "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10")
import torch
from build_network import build_network
from Optimizers.HF import HF

dev = torch.device("cpu")
net = build_network("ResNet18", dev)
n_tensors = len(list(net.parameters()))
n_params = sum(p.numel() for p in net.parameters())
print(f"ResNet18: {n_tensors} param tensors, {n_params:,} params")

args_base = {"alg": "SGDm", "weight_decay": 0.1, "momentum_param": 0.99}
args_meta = {"alg": "Lion", "meta_stepsize": 1e-3, "momentum_param": 0.99,
             "Lion_beta2": 0.9, "weight_decay": 0}

for g in ["scalar", "resnet18_blocks", "layerwise", "nodewise", "weightwise"]:
    try:
        opt = HF(net, stepsize_groups=g, alpha0=1e-6, args_base=dict(args_base),
                 args_meta=dict(args_meta), gamma=1, writer=None)
        beta = getattr(opt, "beta", None)
        shape = [tuple(b.shape) if hasattr(b, "shape") else type(b).__name__ for b in beta] if beta else None
        # try one forward of the alpha mapping
        try:
            a = opt.beta_to_alpha(opt.beta)
            amsg = f"beta_to_alpha OK (n={len(a)})"
        except Exception as e:
            amsg = f"beta_to_alpha FAILS: {type(e).__name__}: {e}"
        print(f"  {g:18s} INIT_OK  type={opt.stepsize_type:10s} beta={shape}  {amsg}")
    except Exception as e:
        print(f"  {g:18s} INIT_FAILS  {type(e).__name__}: {e}")
