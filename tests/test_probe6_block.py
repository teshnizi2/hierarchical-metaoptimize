"""Validate PATCH_PROBE6 against REAL torch, without a GPU or a training run.

Needs torch + numpy.  This Mac has neither, so cycle 61 ran it on the ROG offload node
(torch 2.6.0+cu124, numpy 2.4.6, CPU only):

    scp patches/patch_probe6_coord.py patches/HF_patched.py tests/test_probe6_block.py rog:C:/p6/
    ssh rog "wsl -d Ubuntu -u root -- /opt/ml/bin/python /mnt/c/p6/test_probe6_block.py"

Result at cycle 61: 26/26 pass.  It caught a real bug on the first run -- the cycle-47
numpy '.npy.tmp' extension bug (patches/patch_probe5_fix.py) reintroduced by copying
PATCH_PROBE5's idiom.  Keep this harness green before submitting bin/c61_coord_probe.sh.

Strategy: apply the patch to a copy of the real HF_patched.py, then EXTRACT the inserted
block from the patched file and exec it against a synthetic ResNet18-shaped `z`.  This tests
the code that will actually run, not a re-typed copy of it.
"""
import json, os, re, shutil, sys, tempfile
import numpy as np
import torch

# The patch and the optimizer snapshot live in ../patches/ relative to tests/, but this
# harness is also run standalone from a flat upload dir (the ROG offload node), so accept
# either layout rather than assuming one.
_T = os.path.dirname(os.path.abspath(__file__))
HERE = _T if os.path.exists(os.path.join(_T, "HF_patched.py")) \
    else os.path.join(_T, "..", "patches")
ok, fail = 0, []


def chk(cond, name):
    global ok
    if cond:
        ok += 1
        print(f"  PASS  {name}")
    else:
        fail.append(name)
        print(f"  FAIL  {name}")


# ---------------------------------------------------------------- apply the patch
work = tempfile.mkdtemp()
target = os.path.join(work, "HF.py")
shutil.copy(os.path.join(HERE, "HF_patched.py"), target)
env = dict(os.environ, HF_PATH=target)
PY = sys.executable
PATCH = os.path.join(HERE, "patch_probe6_coord.py")
r = os.system(f'HF_PATH="{target}" "{PY}" "{PATCH}"')
chk(r == 0, "patch applies cleanly to HF_patched.py")
src = open(target).read()
chk("PATCH_PROBE6" in src, "marker present after patch")

# idempotence
r2 = os.popen(f'HF_PATH="{target}" "{PY}" "{PATCH}"').read().strip()
chk(r2 == "ALREADY_PATCHED", "second application is a no-op (ALREADY_PATCHED)")

# the jsonl schema must be untouched
orig = open(os.path.join(HERE, "HF_patched.py")).read()
rec_o = orig[orig.index("        rec = {'step'"):orig.index("with open(os.path.join(self._probe_dir, 'probe.jsonl')")]
rec_p = src[src.index("        rec = {'step'"):src.index("with open(os.path.join(self._probe_dir, 'probe.jsonl')")]
chk(rec_o == rec_p, "probe.jsonl record schema is byte-identical")

# ---------------------------------------------------------------- extract the block
START = "        # --- PATCH_PROBE6:"
END = "        zm = zall.mean()"
chk(START in src and END in src, "inserted block is locatable in the patched source")
block = src[src.index(START):src.index(END)]
# de-indent from 8 spaces to 0 so it can be exec'd at module level
block = "\n".join(l[8:] if l.startswith(" " * 8) else l for l in block.split("\n"))
chk("PROBE6_K" in block and "coord_signs" in block, "block carries the expected body")


# ---------------------------------------------------------------- synthetic arm
class Stub:
    pass


def build_shapes():
    shapes = [(64, 3, 3, 3), (64,), (64,)]
    cin = 64
    for li, (cout, nb) in enumerate(zip([64, 128, 256, 512], [2, 2, 2, 2])):
        for b in range(nb):
            stride = 1 if (li == 0 or b > 0) else 2
            shapes += [(cout, cin, 3, 3), (cout,), (cout,), (cout, cout, 3, 3), (cout,), (cout,)]
            if stride != 1 or cin != cout:
                shapes += [(cout, cin, 1, 1), (cout,), (cout,)]
            cin = cout
    shapes += [(10, 512), (10,)]
    return shapes


SHAPES = build_shapes()
N_TOT = sum(int(np.prod(s)) for s in SHAPES)
print(f"\nsynthetic arm: {len(SHAPES)} tensors, n_tot={N_TOT}")

probe_dir = os.path.join(work, "probe")
os.makedirs(probe_dir, exist_ok=True)
self = Stub()
self._probe_dir = probe_dir
self._probe_every = 25
self.stepsize_type = "weightwise"

g = torch.Generator().manual_seed(7)
records = []
N_REC = 6
os.environ["PROBE6"] = "1"
os.environ["PROBE6_K"] = "20000"
os.environ["PROBE6_WRITE_EVERY"] = "3"

ns = dict(torch=torch, os=os, json=json, self=self)
for t in range(N_REC):
    z = [torch.randn(s, generator=g) * (1.0 if t % 2 else 0.5) for s in SHAPES]
    # inject exact zeros so the zero channel is exercised
    z[1] = torch.zeros_like(z[1])
    zall = torch.cat([zi.reshape(-1) for zi in z])
    records.append((z, zall))
    ns.update(z=z, zall=zall, n_tot=N_TOT)
    exec(block, ns)

# ---------------------------------------------------------------- checks
idx = np.load(os.path.join(probe_dir, "coord_idx.npy"))
sig = np.load(os.path.join(probe_dir, "coord_signs.npy"))
tns = np.load(os.path.join(probe_dir, "tensor_signs.npy"))
meta = json.load(open(os.path.join(probe_dir, "coord_meta.json")))

chk(idx.shape == (20000,), f"coord_idx is [k] ({idx.shape})")
chk(idx.dtype == np.int64, "coord_idx is int64")
chk(len(set(idx.tolist())) == 20000, "coord_idx has no duplicates")
chk(idx.max() < N_TOT and idx.min() >= 0, "coord_idx is in range")
# WRITE_EVERY=3 with 6 records -> last dump holds all 6
chk(sig.shape == (N_REC, 20000), f"coord_signs is [n_rec, k] ({sig.shape})")
chk(sig.dtype == np.int8, "coord_signs is int8")
chk(set(np.unique(sig).tolist()) <= {-1, 0, 1}, "coord_signs is a sign trit")
chk(tns.shape == (N_REC, len(SHAPES), 3), f"tensor_signs is [n_rec, T, 3] ({tns.shape})")

# the tracked coordinates must be the SAME set every record, and match sign(zall[idx])
for t, (z, zall) in enumerate(records):
    want = torch.sign(zall[torch.as_tensor(idx)]).to(torch.int8).numpy()
    if not np.array_equal(want, sig[t]):
        chk(False, f"record {t} signs match sign(zall[idx])")
        break
else:
    chk(True, "every record's signs match sign(zall[idx]) exactly")

# the per-tensor split must be EXACT and must total n_tot
for t, (z, zall) in enumerate(records):
    for j, zi in enumerate(z):
        if not (tns[t, j, 0] == int((zi < 0).sum()) and tns[t, j, 1] == int((zi == 0).sum())
                and tns[t, j, 2] == zi.numel()):
            chk(False, f"tensor split exact at record {t} tensor {j}")
            break
    else:
        continue
    break
else:
    chk(True, "per-tensor (neg, zero, n) split is exact on every tensor and record")

chk(bool((tns[:, :, 2].sum(axis=1) == N_TOT).all()), "per-tensor counts total to n_tot")
chk(int(tns[0, 1, 1]) == SHAPES[1][0], "the injected all-zero tensor is counted as zero, not negative")
# frac_neg reconstructed from the exact split must match the whole-vector value
for t, (z, zall) in enumerate(records):
    fn_direct = float((zall < 0).sum()) / N_TOT
    fn_split = tns[t, :, 0].sum() / N_TOT
    if abs(fn_direct - fn_split) > 1e-12:
        chk(False, f"frac_neg reconstructs from the split at record {t}")
        break
else:
    chk(True, "frac_neg reconstructs EXACTLY from the per-tensor split (free cross-check)")

chk(meta["n_records"] == N_REC and meta["n_tot"] == N_TOT and meta["k"] == 20000,
    "coord_meta.json agrees with the arrays")
chk(meta["n_tensors"] == len(SHAPES) and meta["stepsize_type"] == "weightwise",
    "coord_meta.json carries the arm identity")
chk(not os.path.exists(os.path.join(probe_dir, "coord_signs.npy.tmp")),
    "no .tmp file is left behind (atomic replace)")

# ---------------------------------------------------------------- inertness
probe_dir2 = os.path.join(work, "probe_off")
os.makedirs(probe_dir2, exist_ok=True)
self2 = Stub()
self2._probe_dir = probe_dir2
self2._probe_every = 25
self2.stepsize_type = "weightwise"
os.environ["PROBE6"] = "0"
ns2 = dict(torch=torch, os=os, json=json, self=self2)
z, zall = records[0]
ns2.update(z=z, zall=zall, n_tot=N_TOT)
exec(block, ns2)
chk(os.listdir(probe_dir2) == [], "PROBE6=0 writes NOTHING (inert)")
chk(not hasattr(self2, "_p6_idx"), "PROBE6=0 sets no optimizer state")

# ---------------------------------------------------------------- k clamping (layerwise arm)
probe_dir3 = os.path.join(work, "probe_lay")
os.makedirs(probe_dir3, exist_ok=True)
self3 = Stub()
self3._probe_dir = probe_dir3
self3._probe_every = 25
self3.stepsize_type = "layerwise"
os.environ["PROBE6"] = "1"
ns3 = dict(torch=torch, os=os, json=json, self=self3)
zl = [torch.randn(62, generator=g)]
ns3.update(z=zl, zall=zl[0], n_tot=62)
os.environ["PROBE6_WRITE_EVERY"] = "1"
exec(block, ns3)
i3 = np.load(os.path.join(probe_dir3, "coord_idx.npy"))
s3 = np.load(os.path.join(probe_dir3, "coord_signs.npy"))
chk(i3.shape == (62,), f"k clamps to n_tot on a small arm ({i3.shape})")
chk(s3.shape == (1, 62), f"coord_signs shaped by the clamped k ({s3.shape})")

print(f"\nvalidate_probe6: {ok} passed, {len(fail)} failed")
for f in fail:
    print("   FAIL:", f)
shutil.rmtree(work, ignore_errors=True)
sys.exit(1 if fail else 0)
