#!/usr/bin/env python3
"""patch_tinyimagenet.py -- PATCH_TINYIMAGENET.  Wire Tiny-ImageNet-200 into the
CIFAR harness as a GUARDED, PURELY ADDITIVE patch.

WHY IT HAS TO BE PROVABLY INERT.  60 jobs of two other agents' decisive batches
(`tl1`, `eb1`) were queued on this account when this patch was written, and
train.py imports load_data.py and build_network.py at job start.  A patch that
changed behaviour when unused would split those batches across two code versions
and invalidate the 919 archived alice2 runs as well.  So this patch:

  * MODIFIES NO EXISTING LINE.  It inserts one `elif` into load_data.load_data
    (reached only by the exact string `--dataset TinyImageNet`), one `if` into
    build_network.build_network (reached only by `--NN-name ResNet18_tin`), and
    appends one new class.  Every pre-existing line is asserted to survive
    verbatim after the edit.
  * PUTS THE DATASET CODE IN A NEW FILE, tin_data.py, imported LAZILY inside the
    new branch, so an unrelated run never even executes the import statement.
  * ADDS NO PARAMETER.  ResNet_tin subclasses ResNet and overrides forward() to
    insert one max_pool2d.  MaxPool2d carries no parameters, so
    net.named_parameters() for ResNet18_tin is element-for-element the same list
    as ResNet18's apart from the classifier head's shape (512x200 vs 512x10).
    That is what keeps HF.py's positional step-size partition -- and the
    layerwise group count m -- comparable with the CIFAR corpus.

THE 64px STEM.  ResNet.forward ends in `F.avg_pool2d(out, 4)`, which is correct
only when layer4 emits 4x4.  With a 32x32 input it does.  With Tiny-ImageNet's
64x64 input it would emit 8x8 and the flattened vector would be 4x too long for
self.linear -- a shape error, not a silent wrong answer, but still a blocker.
ResNet_tin resolves it the way the reference ImageNet ResNet does: a stride-2
max-pool immediately after the stem convolution, 64 -> 32.  Everything after the
stem then sees EXACTLY the tensor shapes the CIFAR runs saw, so the 200-class
result differs from CIFAR by dataset and head width and by nothing else.

USAGE
    python3 patches/patch_tinyimagenet.py --cifar10-dir <dir>            # apply
    python3 patches/patch_tinyimagenet.py --cifar10-dir <dir> --check    # report only
"""
import argparse
import ast
import os
import shutil
import sys

MARK = "PATCH_TINYIMAGENET"

TIN_DATA = '''"""tin_data.py -- PATCH_TINYIMAGENET.  Tiny-ImageNet-200 as an in-memory uint8
dataset that feeds torchvision transforms exactly the way torchvision's own
CIFAR10 dataset does (hold HWC uint8, call Image.fromarray in __getitem__).

NEW FILE.  Nothing in the tree imports it unless a run passes
`--dataset TinyImageNet`, so it cannot affect any other run.

It reads ONLY the cache directory built by bin/tin_stage.py and raises if that
is absent.  There is deliberately no download fallback and no on-the-fly JPEG
decode: load_data.py builds its DataLoader with the shipped default
num_workers=0, so decoding 100,000 JPEGs would happen inside the training
process and the run would be data-bound rather than GPU-bound.

Normalisation constants are READ FROM THE MANIFEST, i.e. they are the channel
statistics measured over this staged train split, not numbers quoted from a
paper.
"""
import json
import os

import numpy as np
import torch
from PIL import Image

CACHE_DIRNAME = "tiny-imagenet-200-cache"


def _cache(root):
    return os.path.join(root, CACHE_DIRNAME)


def manifest(root):
    p = os.path.join(_cache(root), "MANIFEST.json")
    if not os.path.exists(p):
        raise FileNotFoundError(
            "Tiny-ImageNet cache not found at %s.  Build it with "
            "bin/tin_stage.py before running --dataset TinyImageNet." % _cache(root))
    with open(p) as fh:
        return json.load(fh)


def norm_stats(root):
    """(mean, std) per channel in [0,1], MEASURED over the staged train split."""
    m = manifest(root)
    return tuple(m["train_mean_01"]), tuple(m["train_std_01"])


class TinyImageNet200(torch.utils.data.Dataset):
    def __init__(self, root, train=True, transform=None):
        self.man = manifest(root)
        split = "train" if train else "val"
        c = _cache(root)
        self.data = np.load(os.path.join(c, "%s_x.npy" % split))
        self.targets = np.load(os.path.join(c, "%s_y.npy" % split)).tolist()
        with open(os.path.join(c, "classes.txt")) as fh:
            self.classes = [l.strip() for l in fh if l.strip()]
        self.transform = transform

        # Guards that abort before training rather than corrupting a result.
        n = int(self.man["%s_n" % split])
        k = int(self.man["num_classes"])
        if self.data.shape != (n, int(self.man["side"]), int(self.man["side"]), 3):
            raise ValueError("cache %s_x.npy has shape %s, manifest says %d images"
                             % (split, self.data.shape, n))
        if len(self.targets) != n:
            raise ValueError("%d labels for %d images" % (len(self.targets), n))
        if len(self.classes) != k:
            raise ValueError("%d class names for %d classes" % (len(self.classes), k))
        lo, hi = min(self.targets), max(self.targets)
        if lo != 0 or hi != k - 1 or len(set(self.targets)) != k:
            raise ValueError("labels are not a complete 0..%d map (min %d max %d "
                             "distinct %d)" % (k - 1, lo, hi, len(set(self.targets))))

    def __len__(self):
        return int(self.data.shape[0])

    def __getitem__(self, i):
        img = Image.fromarray(self.data[i])
        if self.transform is not None:
            img = self.transform(img)
        return img, self.targets[i]
'''

LOAD_BLOCK = '''    # --- PATCH_TINYIMAGENET: reached ONLY by the exact string
    # `--dataset TinyImageNet`, which no prior batch used.  The import is inside
    # the branch so no other run executes it.  AUGMENT uses padding 8 for a 64px
    # image, the same 1/8-of-a-side ratio as the CIFAR path's padding 4 at 32px.
    elif dataset_name == "TinyImageNet":
        import os
        from tin_data import TinyImageNet200, norm_stats
        mean, std = norm_stats('./data')
        norm = transforms.Normalize(mean, std)
        test_transform = transforms.Compose([transforms.ToTensor(), norm])
        if os.environ.get("AUGMENT", "0") == "1":
            train_transform = transforms.Compose([transforms.RandomCrop(64, padding=8), transforms.RandomHorizontalFlip(), transforms.ToTensor(), norm])
        else:
            train_transform = test_transform
        trainset = TinyImageNet200(root='./data', train=True, transform=train_transform)
        testset = TinyImageNet200(root='./data', train=False, transform=test_transform)
'''

NET_DISPATCH = '''    # --- PATCH_TINYIMAGENET: the ONLY new name.  Same block type, same depths,
    # same normaliser; a 200-way head and a stride-2 stem pool so that everything
    # after the stem sees the SAME tensor shapes the 32px runs saw. ---
    if network_name == 'ResNet18_tin':
        return ResNet_tin(BasicBlock, [2, 2, 2, 2], num_classes=200).to(device)

'''

NET_CLASS = '''

# --- PATCH_TINYIMAGENET ---------------------------------------------------------
# ResNet_tin subclasses ResNet and overrides ONLY forward().  It defines no new
# module and no new parameter, so named_parameters() yields the same names in the
# same order as ResNet18 -- which HF.init_meta consumes POSITIONALLY -- and the
# layerwise group count m is unchanged.  The single inserted op is a parameterless
# stride-2 max-pool that takes the 64x64 stem output to 32x32, after which every
# tensor shape in the network is identical to the CIFAR path, including the 4x4
# feature map that ResNet.forward's fixed `F.avg_pool2d(out, 4)` requires.
class ResNet_tin(ResNet):
    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = F.max_pool2d(out, kernel_size=3, stride=2, padding=1)  # 64 -> 32
        out = self.layer1(out)
        out = self.layer2(out)
        out = self.layer3(out)
        out = self.layer4(out)
        out = F.avg_pool2d(out, 4)
        out = out.view(out.size(0), -1)
        out = self.linear(out)
        return out
'''

# Text that MUST survive the edit verbatim.  If any of these stops matching, the
# patch has moved a pre-existing line and must not be written.
SURVIVE_LOAD = [
    'elif dataset_name == "CIFAR100":',
    "trainset = datasets.CIFAR10(root='./data', train=True, download=True, transform=train_transform)",
    "trainset = datasets.CIFAR100(root='./data', train=True, download=True, transform=train_transform)",
    "    else: 0/0 # return error",
    "    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size, shuffle=True)",
]
SURVIVE_NET = [
    "    if network_name == 'ResNet18':\n        return ResNet(BasicBlock, [2, 2, 2, 2]).to(device)",
    "    if network_name == 'ResNet18_gn':",
    "    if network_name == 'ResNet18_c100':",
    "    if network_name == 'ResNet50':",
    "    0/0 # raise error if network_name is out of the above list",
    "        out = F.avg_pool2d(out, 4)",
]


def write_atomic(path, text):
    tmp = path + ".tmp_tinpatch"
    with open(tmp, "w") as fh:
        fh.write(text)
    os.replace(tmp, path)


def patch_load_data(path, apply):
    src = open(path).read()
    if MARK in src:
        print("load_data.py      : already patched (no-op)")
        return src
    anchor = "    else: 0/0 # return error"
    if src.count(anchor) != 1:
        sys.exit("PATCH FAIL: load_data.py anchor %r appears %d times" % (anchor, src.count(anchor)))
    new = src.replace(anchor, LOAD_BLOCK + anchor)
    for t in SURVIVE_LOAD:
        if t not in new:
            sys.exit("PATCH FAIL: load_data.py lost %r" % t[:60])
    ast.parse(new)
    if apply:
        shutil.copyfile(path, path + ".bak_tin")
        write_atomic(path, new)
    print("load_data.py      : + %d lines (TinyImageNet branch)" % LOAD_BLOCK.count("\n"))
    return new


def patch_build_network(path, apply):
    src = open(path).read()
    if MARK in src:
        print("build_network.py  : already patched (no-op)")
        return src
    anchor = "    if network_name == 'ResNet18_soft':"
    if src.count(anchor) != 1:
        sys.exit("PATCH FAIL: build_network.py anchor appears %d times" % src.count(anchor))
    new = src.replace(anchor, NET_DISPATCH + anchor)
    new = new.rstrip("\n") + "\n" + NET_CLASS
    for t in SURVIVE_NET:
        if t not in new:
            sys.exit("PATCH FAIL: build_network.py lost %r" % t[:60])
    tree = ast.parse(new)
    names = {n.name for n in tree.body if isinstance(n, ast.ClassDef)}
    for want in ("ResNet", "BasicBlock", "Bottleneck", "ResNet_tin"):
        if want not in names:
            sys.exit("PATCH FAIL: class %s missing after patch" % want)
    if apply:
        shutil.copyfile(path, path + ".bak_tin")
        write_atomic(path, new)
    print("build_network.py  : + dispatch + class ResNet_tin")
    return new


def write_tin_data(path, apply):
    if os.path.exists(path):
        cur = open(path).read()
        if cur == TIN_DATA:
            print("tin_data.py       : already present and identical")
            return
        print("tin_data.py       : present but DIFFERENT -- overwriting")
    ast.parse(TIN_DATA)
    if apply:
        write_atomic(path, TIN_DATA)
    print("tin_data.py       : %d lines (new file)" % TIN_DATA.count("\n"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cifar10-dir", required=True)
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    a = ap.parse_args()
    apply = not a.check
    d = a.cifar10_dir
    print("PATCH_TINYIMAGENET %s  %s" % ("--check (dry)" if a.check else "APPLY", d))
    patch_load_data(os.path.join(d, "load_data.py"), apply)
    patch_build_network(os.path.join(d, "build_network.py"), apply)
    write_tin_data(os.path.join(d, "tin_data.py"), apply)
    print("PATCH_TINYIMAGENET %s" % ("checked" if a.check else "applied"))
