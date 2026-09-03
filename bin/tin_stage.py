#!/usr/bin/env python3
"""tin_stage.py -- VERIFY and STAGE Tiny-ImageNet-200 for the CIFAR harness.

Tiny-ImageNet is the credential-free scale axis: 200 classes at 64x64, 100k
train / 10k val, and -- unlike ImageNet-1k's val split -- its validation labels
ship with the archive in `val/val_annotations.txt`, so accuracy is computable.

WHAT THIS SCRIPT DOES, in order:
  1.  MEASURES the extracted tree.  It never assumes 200/100000/10000; it counts
      what is on disk and prints it.  Every expectation is an assertion whose
      observed value is printed next to it, so a short download fails loudly
      instead of silently training on a subset (the exact failure mode that
      scoped ImageNet-1k out of this project -- 489 of 1000 classes present).
  2.  CHECKS the label file is real: every val image is named, every named wnid
      is a train class, and the per-class counts are reported.
  3.  DECODES every JPEG once into a uint8 array and writes a cache directory of
      .npy files.  Why cache: load_data.py builds its DataLoader with the shipped
      default num_workers=0, so JPEG decode would run in the training process and
      the run would be data-bound rather than GPU-bound.  torchvision's own
      CIFAR10 dataset holds a uint8 HWC array in memory and calls
      Image.fromarray in __getitem__; the cache makes Tiny-ImageNet behave
      IDENTICALLY, so the transform pipeline is the same object graph as CIFAR's.
  4.  COMPUTES the channel mean/std over the TRAIN split only and writes them
      into the manifest.  Nothing is quoted from the literature.

The cache is the only thing the training harness reads.  If it is absent,
tin_data.py raises rather than falling back to anything.

USAGE
    python3 bin/tin_stage.py --raw  /zfsstore/user/s5014158/tinyimagenet/tiny-imagenet-200 \
                             --out  <cifar10>/data/tiny-imagenet-200-cache
    python3 bin/tin_stage.py --verify-only --out <cache>     # re-check a built cache
"""
import argparse
import hashlib
import json
import os
import sys
import time

import numpy as np
from PIL import Image

EXPECT = {"classes": 200, "train_total": 100000, "val_total": 10000,
          "per_class_train": 500, "side": 64}


def _die(msg):
    print("STAGE FAIL: %s" % msg)
    sys.exit(2)


def measure_tree(raw):
    """Count what is actually on disk.  Returns a dict of MEASURED facts."""
    train_dir = os.path.join(raw, "train")
    val_dir = os.path.join(raw, "val")
    wnids_txt = os.path.join(raw, "wnids.txt")
    for p in (train_dir, val_dir, wnids_txt):
        if not os.path.exists(p):
            _die("missing %s" % p)

    listed = sorted(w for w in os.listdir(train_dir)
                    if os.path.isdir(os.path.join(train_dir, w)))
    declared = sorted(l.strip() for l in open(wnids_txt) if l.strip())

    per_class = {}
    for w in listed:
        d = os.path.join(train_dir, w, "images")
        if not os.path.isdir(d):
            _die("train class %s has no images/ subdirectory" % w)
        per_class[w] = sorted(f for f in os.listdir(d) if f.endswith(".JPEG"))

    ann = os.path.join(val_dir, "val_annotations.txt")
    if not os.path.exists(ann):
        _die("no val_annotations.txt -- the validation split would be unlabelled, "
             "which is precisely why ImageNet-1k was scoped out.  Do not proceed.")
    val_pairs = []
    for line in open(ann):
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 2:
            continue
        val_pairs.append((parts[0], parts[1]))
    val_files = sorted(f for f in os.listdir(os.path.join(val_dir, "images"))
                       if f.endswith(".JPEG"))

    return {"train_classes_listed": listed, "wnids_declared": declared,
            "per_class": per_class, "val_pairs": val_pairs,
            "val_files_on_disk": val_files,
            "train_dir": train_dir, "val_dir": val_dir}


def report_and_assert(m):
    listed, declared = m["train_classes_listed"], m["wnids_declared"]
    per_class, val_pairs = m["per_class"], m["val_pairs"]
    n_train = sum(len(v) for v in per_class.values())
    counts = sorted(set(len(v) for v in per_class.values()))
    named = set(f for f, _ in val_pairs)
    on_disk = set(m["val_files_on_disk"])
    val_wnids = set(w for _, w in val_pairs)
    per_val = {}
    for _, w in val_pairs:
        per_val[w] = per_val.get(w, 0) + 1
    val_counts = sorted(set(per_val.values()))

    print("---- MEASURED, not assumed -------------------------------------")
    print("train class directories        : %d   (expected %d)" % (len(listed), EXPECT["classes"]))
    print("wnids.txt entries              : %d" % len(declared))
    print("wnids.txt == train dirs        : %s" % (listed == declared))
    print("train images total             : %d   (expected %d)" % (n_train, EXPECT["train_total"]))
    print("train images per class         : %s" % counts)
    print("val_annotations.txt rows       : %d   (expected %d)" % (len(val_pairs), EXPECT["val_total"]))
    print("val JPEGs on disk              : %d" % len(on_disk))
    print("every val JPEG is labelled     : %s" % (on_disk == named))
    print("distinct wnids in val labels   : %d" % len(val_wnids))
    print("val labels subset of train     : %s" % val_wnids.issubset(set(listed)))
    print("val images per class           : %s" % val_counts)
    print("----------------------------------------------------------------")

    if len(listed) != EXPECT["classes"]:
        _die("%d train classes, not %d -- a partial archive" % (len(listed), EXPECT["classes"]))
    if listed != declared:
        _die("wnids.txt disagrees with the train directories")
    if n_train != EXPECT["train_total"]:
        _die("%d train images, not %d" % (n_train, EXPECT["train_total"]))
    if counts != [EXPECT["per_class_train"]]:
        _die("train classes are not all %d images: %s" % (EXPECT["per_class_train"], counts))
    if len(val_pairs) != EXPECT["val_total"]:
        _die("%d val label rows, not %d" % (len(val_pairs), EXPECT["val_total"]))
    if on_disk != named:
        _die("val images and val labels do not correspond 1:1")
    if not val_wnids.issubset(set(listed)):
        _die("val labels reference wnids absent from train")
    if len(val_wnids) != EXPECT["classes"]:
        _die("val covers %d classes, not %d" % (len(val_wnids), EXPECT["classes"]))
    print("all structural checks PASS")


def decode(paths, side):
    """Decode a list of JPEG paths into one (N, side, side, 3) uint8 array."""
    out = np.zeros((len(paths), side, side, 3), dtype=np.uint8)
    grey = 0
    t0 = time.time()
    for i, p in enumerate(paths):
        with Image.open(p) as im:
            if im.mode != "RGB":
                grey += 1
                im = im.convert("RGB")
            if im.size != (side, side):
                _die("%s is %s, not %dx%d" % (p, im.size, side, side))
            out[i] = np.asarray(im, dtype=np.uint8)
        if i and i % 20000 == 0:
            print("    decoded %d/%d (%.0fs)" % (i, len(paths), time.time() - t0))
    print("    decoded %d images in %.0fs; %d were not already RGB (converted)"
          % (len(paths), time.time() - t0, grey))
    return out


def sha256_of(path, cap=1 << 26):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def build(raw, out):
    m = measure_tree(raw)
    report_and_assert(m)

    classes = m["train_classes_listed"]           # sorted; this IS the label map
    class_to_idx = {w: i for i, w in enumerate(classes)}

    train_paths, train_y = [], []
    for w in classes:
        d = os.path.join(m["train_dir"], w, "images")
        for f in m["per_class"][w]:
            train_paths.append(os.path.join(d, f))
            train_y.append(class_to_idx[w])
    val_pairs = sorted(m["val_pairs"])            # deterministic order
    val_paths = [os.path.join(m["val_dir"], "images", f) for f, _ in val_pairs]
    val_y = [class_to_idx[w] for _, w in val_pairs]

    print("decoding train ...")
    tx = decode(train_paths, EXPECT["side"])
    print("decoding val ...")
    vx = decode(val_paths, EXPECT["side"])
    ty = np.asarray(train_y, dtype=np.int64)
    vy = np.asarray(val_y, dtype=np.int64)

    # Channel statistics over the TRAIN split only, in [0,1].  float64 accumulation.
    f = tx.astype(np.float64) / 255.0
    mean = f.mean(axis=(0, 1, 2))
    std = f.std(axis=(0, 1, 2))
    del f
    print("train channel mean = %s" % np.round(mean, 4).tolist())
    print("train channel std  = %s" % np.round(std, 4).tolist())

    os.makedirs(out, exist_ok=True)
    files = {"train_x.npy": tx, "train_y.npy": ty, "val_x.npy": vx, "val_y.npy": vy}
    for name, arr in files.items():
        np.save(os.path.join(out, name), arr)
    with open(os.path.join(out, "classes.txt"), "w") as fh:
        fh.write("\n".join(classes) + "\n")

    man = {
        "dataset": "TinyImageNet-200",
        "source_url": "https://cs231n.stanford.edu/tiny-imagenet-200.zip",
        "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "num_classes": len(classes),
        "train_n": int(tx.shape[0]), "val_n": int(vx.shape[0]),
        "side": EXPECT["side"],
        "train_mean_01": [float(x) for x in mean],
        "train_std_01": [float(x) for x in std],
        "label_map": "sorted(wnids); identical for train and val by construction",
        "sha256": {n: sha256_of(os.path.join(out, n)) for n in files},
    }
    with open(os.path.join(out, "MANIFEST.json"), "w") as fh:
        json.dump(man, fh, indent=2, sort_keys=True)
    print(json.dumps(man, indent=2, sort_keys=True))
    print("STAGE OK -> %s" % out)


def verify(out):
    man = json.load(open(os.path.join(out, "MANIFEST.json")))
    ok = True
    for n, want in sorted(man["sha256"].items()):
        got = sha256_of(os.path.join(out, n))
        print("%-12s %s %s" % (n, "OK  " if got == want else "BAD ", got))
        ok &= got == want
    tx = np.load(os.path.join(out, "train_x.npy"), mmap_mode="r")
    vx = np.load(os.path.join(out, "val_x.npy"), mmap_mode="r")
    ty = np.load(os.path.join(out, "train_y.npy"))
    vy = np.load(os.path.join(out, "val_y.npy"))
    print("train_x %s  val_x %s" % (tx.shape, vx.shape))
    print("train labels: %d distinct, min %d max %d" % (len(set(ty.tolist())), ty.min(), ty.max()))
    print("val   labels: %d distinct, min %d max %d" % (len(set(vy.tolist())), vy.min(), vy.max()))
    bc = np.bincount(vy, minlength=man["num_classes"])
    print("val per class: min %d max %d" % (bc.min(), bc.max()))
    ok &= tx.shape == (man["train_n"], man["side"], man["side"], 3)
    ok &= vx.shape == (man["val_n"], man["side"], man["side"], 3)
    ok &= len(set(ty.tolist())) == man["num_classes"]
    ok &= len(set(vy.tolist())) == man["num_classes"]
    print("VERIFY %s" % ("PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args()
    if a.verify_only:
        verify(a.out)
    else:
        if not a.raw:
            _die("--raw is required unless --verify-only")
        build(a.raw, a.out)
