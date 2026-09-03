#!/usr/bin/env python3
"""tin_equivalence.py -- prove PATCH_TINYIMAGENET is a BITWISE no-op when unused.

Run this ON THE CLUSTER, inside the venv, AFTER applying the patch.  It compares
the patched modules against the pre-patch backups the patch itself wrote
(load_data.py.bak_tin, build_network.py.bak_tin), loading both into ONE process
by explicit SourceFileLoader -- importlib cannot sniff a non-.py suffix.

PROOF A  build_network: every pre-existing --NN-name constructs a network whose
         parameters are bit-for-bit identical under the two modules at a fixed
         seed, with the same named_parameters ORDER (HF.init_meta consumes that
         list positionally), and whose forward pass on a fixed input is
         bit-for-bit identical.
PROOF B  load_data: CIFAR10 and CIFAR100, AUGMENT off and on, produce bit-for-bit
         identical image tensors and labels for the first batches under the two
         modules at a fixed seed.  This covers the augmentation RNG as well as
         the normalisation.
PROOF C  the new arms are UNREACHABLE on the pre-patch module: `ResNet18_tin`
         hits build_network's own 0/0 there, and `TinyImageNet` hits
         load_data's `else: 0/0`.
PROOF D  the new arm is CORRECT and COMPARABLE: ResNet18_tin accepts 64x64,
         emits 200 logits, and its named_parameters list matches ResNet18's
         name-for-name and shape-for-shape except the classifier head -- so the
         layerwise step-size group count m is identical to the CIFAR corpus's.

    python3 tests/tin_equivalence.py --cifar10-dir <dir>
"""
import argparse
import hashlib
import importlib.util
import os
import sys

import torch
from importlib.machinery import SourceFileLoader

FAILED = []


def load_module(name, path):
    loader = SourceFileLoader(name, path)
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


def h(t):
    return hashlib.sha256(t.detach().to(torch.float64).cpu().numpy().tobytes()).hexdigest()


def check(label, ok, extra=""):
    print("  %-58s %s %s" % (label, "PASS" if ok else "**FAIL**", extra))
    if not ok:
        FAILED.append(label)


def proof_a(pre, post, names):
    print("PROOF A -- build_network is bitwise unchanged for every existing name")
    for n in names:
        torch.manual_seed(0)
        a = pre.build_network(n, "cpu")
        torch.manual_seed(0)
        b = post.build_network(n, "cpu")
        na = [(k, tuple(v.shape)) for k, v in a.named_parameters()]
        nb = [(k, tuple(v.shape)) for k, v in b.named_parameters()]
        same_order = na == nb
        same_bits = all(h(x) == h(y) for (_, x), (_, y)
                        in zip(a.named_parameters(), b.named_parameters()))
        torch.manual_seed(1)
        # M1/M2 are the MNIST nets and reshape to 28*28; everything else is a
        # 32px CIFAR ResNet.  The probe input must match or forward() raises.
        x = torch.randn(2, 1, 28, 28) if n in ("M1", "M2") else torch.randn(2, 3, 32, 32)
        a.eval(); b.eval()
        with torch.no_grad():
            fa, fb = a(x), b(x)
        check("%-14s params bitwise + order + forward bitwise" % n,
              same_order and same_bits and h(fa) == h(fb),
              "m_params=%d" % len(na))


def _batches(mod, dataset, augment, cif, k=3, seed=0):
    os.environ["AUGMENT"] = "1" if augment else "0"
    cwd = os.getcwd()
    os.chdir(cif)
    try:
        tr, te = mod.load_data(dataset, 100, seed)
        out = []
        for i, (xb, yb) in enumerate(tr):
            out.append((h(xb), h(yb.to(torch.float64))))
            if i + 1 >= k:
                break
        for i, (xb, yb) in enumerate(te):
            out.append((h(xb), h(yb.to(torch.float64))))
            if i + 1 >= k:
                break
        return out
    finally:
        os.chdir(cwd)


def proof_b(pre, post, cif):
    print("PROOF B -- load_data is bitwise unchanged for every existing dataset")
    for ds in ("CIFAR10", "CIFAR100"):
        for aug in (False, True):
            a = _batches(pre, ds, aug, cif)
            b = _batches(post, ds, aug, cif)
            check("%-9s AUGMENT=%d  first 3 train + 3 test batches" % (ds, int(aug)),
                  a == b, "%d hashes" % len(a))


def proof_c(pre_bn, pre_ld, cif):
    print("PROOF C -- the new arms are unreachable on the pre-patch modules")
    try:
        pre_bn.build_network("ResNet18_tin", "cpu")
        check("pre-patch build_network('ResNet18_tin') raises", False, "it returned a net")
    except Exception as ex:
        check("pre-patch build_network('ResNet18_tin') raises", True, type(ex).__name__)
    cwd = os.getcwd()
    os.chdir(cif)
    try:
        pre_ld.load_data("TinyImageNet", 100, 0)
        check("pre-patch load_data('TinyImageNet') raises", False, "returned loaders")
    except Exception as ex:
        check("pre-patch load_data('TinyImageNet') raises", True, type(ex).__name__)
    finally:
        os.chdir(cwd)


def proof_d(post):
    print("PROOF D -- ResNet18_tin is correct and structurally comparable")
    torch.manual_seed(0)
    tin = post.build_network("ResNet18_tin", "cpu")
    torch.manual_seed(0)
    c10 = post.build_network("ResNet18", "cpu")
    x = torch.randn(2, 3, 64, 64)
    tin.eval()
    with torch.no_grad():
        y = tin(x)
    check("forward (2,3,64,64) -> (2,200)", tuple(y.shape) == (2, 200), str(tuple(y.shape)))

    nt = [(k, tuple(v.shape)) for k, v in tin.named_parameters()]
    nc = [(k, tuple(v.shape)) for k, v in c10.named_parameters()]
    check("same number of parameter tensors as ResNet18",
          len(nt) == len(nc), "%d vs %d" % (len(nt), len(nc)))
    check("same parameter NAMES in the same ORDER as ResNet18",
          [k for k, _ in nt] == [k for k, _ in nc])
    diff = [(a, b) for a, b in zip(nt, nc) if a != b]
    check("only the classifier head differs in shape",
          all(a[0].startswith("linear.") for a, _ in diff), str(diff))
    check("head is 200-wide",
          dict(nt)["linear.weight"][0] == 200 and dict(nt)["linear.bias"][0] == 200)
    npar_t = sum(v.numel() for v in tin.parameters())
    npar_c = sum(v.numel() for v in c10.parameters())
    print("    ResNet18_tin %d parameters; ResNet18 %d; difference %d (head only)"
          % (npar_t, npar_c, npar_t - npar_c))


def proof_m(post, cif):
    """m, the live number of adapted step sizes, measured on the live tree."""
    print("PROOF E -- step-size group counts, MEASURED on the live HF.py")
    sys.path.insert(0, cif)
    sys.path.insert(0, os.path.join(cif, "Optimizers"))
    try:
        from HF import HF
    except Exception as ex:
        check("import HF from the live tree", False, repr(ex))
        return

    class NW:
        def add_scalar(self, *a, **k):
            pass

    B = {"alg": "SGDm", "momentum_param": 0.99, "weight_decay": 0.1}
    M = {"alg": "Lion", "meta_stepsize": 1e-3, "momentum_param": 0.99,
         "Lion_beta2": 0.9, "weight_decay": 0}
    got = {}
    for net in ("ResNet18", "ResNet18_tin"):
        got[net] = {}
        for g in ("scalar", "layerwise", "nodewise"):
            torch.manual_seed(0)
            opt = HF(post.build_network(net, "cpu"), stepsize_groups=g, alpha0=1e-6,
                     args_base=dict(B), args_meta=dict(M), gamma=1, writer=NW())
            got[net][g] = sum(int(b.numel()) for b in opt.beta)
        print("    %-14s scalar=%d  layerwise=%d  nodewise=%d"
              % (net, got[net]["scalar"], got[net]["layerwise"], got[net]["nodewise"]))
    check("layerwise m identical to ResNet18",
          got["ResNet18_tin"]["layerwise"] == got["ResNet18"]["layerwise"],
          "%d" % got["ResNet18_tin"]["layerwise"])
    check("scalar m == 1", got["ResNet18_tin"]["scalar"] == 1)
    check("nodewise m > layerwise m",
          got["ResNet18_tin"]["nodewise"] > got["ResNet18_tin"]["layerwise"],
          "%d" % got["ResNet18_tin"]["nodewise"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cifar10-dir", required=True)
    a = ap.parse_args()
    cif = os.path.abspath(a.cifar10_dir)
    sys.path.insert(0, cif)

    pre_bn = load_module("bn_pre", os.path.join(cif, "build_network.py.bak_tin"))
    post_bn = load_module("bn_post", os.path.join(cif, "build_network.py"))
    pre_ld = load_module("ld_pre", os.path.join(cif, "load_data.py.bak_tin"))
    post_ld = load_module("ld_post", os.path.join(cif, "load_data.py"))

    print("torch %s   tree %s" % (torch.__version__, cif))
    NAMES = ["ResNet18", "ResNet18_gn", "ResNet18_c100", "ResNet10", "ResNet34",
             "ResNet10_c100", "ResNet34_c100", "ResNet50", "ResNet18_soft", "M1", "M2"]
    proof_a(pre_bn, post_bn, NAMES)
    proof_b(pre_ld, post_ld, cif)
    proof_c(pre_bn, pre_ld, cif)
    proof_d(post_bn)
    proof_m(post_bn, cif)

    print("=" * 68)
    if FAILED:
        print("FAIL -- %d check(s) failed: %s" % (len(FAILED), FAILED))
        sys.exit(1)
    print("PASS -- PATCH_TINYIMAGENET is a proven bitwise no-op when unused")
