"""Correctness tests for PATCH_NODEBN (`--stepsize-groups nodewise1d`).

STRATEGY, identical in spirit to tests/test_permnode.py and tests/test_chunkwise.py:
validate the new partition against code paths that are ALREADY TRUSTED, via mathematical
identities, rather than against my expectation of what it should do.

  N0  DETERMINISM FIRST (STANDING RULE 20).  The SAME configuration run twice must give
      max|dW| = max|dbeta| = 0.  If this fails, every equivalence below is meaningless
      and the suite stops.  On CUDA this genuinely fails -- see the DEV note.
  N1  **THE STRUCTURAL EQUIVALENCE.**  On a network with NO one-dimensional parameters,
      `nodewise1d` IS `nodewise`, BITWISE.  nodewise1d is implemented as one code path
      (`repeat_interleave(gsize).view(shape)` / `reshape(groups, gsize).sum(1)`) that
      reduces to nodewise whenever groups == shape[0], and a row-major tensor of shape
      (d0, d1, ...) flattens with d0 slowest, so nodewise's group g IS the flat slice
      [g*gs, (g+1)*gs).  Asserted against the UNPATCHED nodewise path on a purpose-built
      bias-free net, not against my reading of it.  This is the assertion that makes the
      whole arm trustworthy: it says the ONLY thing nodewise1d changes is the 1-D tensors.
  N2  THE GROUP COUNTS, ON THE REAL ResNet18, TENSOR BY TENSOR.  groups == 1 for every
      ndim == 1 tensor and shape[0] for every other, and the total m equals a value
      computed independently from the network's shapes.  This is the whole claim of the
      arm and it is MEASURED from the ALLOCATED beta, not read off a comment.
  N3  NO PADDING, NO RESCALING.  groups[i] * gsize[i] == numel[i] for every tensor, so no
      group is summed over fewer members than it is divided by.
  N4  THE ALPHA MAP.  For a given beta, the alpha delivered to flat position j equals
      exp(beta[j // gsize]) on every tensor, checked over all 11,173,962 weights.
  N5  meta_stepsize = 0  =>  nodewise1d trains identically to nodewise.  With beta frozen
      the partition cannot matter, so any weight difference is a plumbing bug, not
      dynamics.  (The beta VECTORS differ in length by construction, so this compares
      weights only, and says so.)
  N6  nodewise1d != nodewise on a real net at a real meta stepsize.  THE ANTI-VACUITY
      GUARD.  If this fails, N1 and N5 are passing because nothing diverges and the arm
      measures nothing.
  N7  THE PROBE SEES IT.  n_beta == m via the per-layer-LIST branch, the same branch
      nodewise, permnode and chunkwise take.
  N8  **THE MATCHED COUNT THE BATCH DEPENDS ON.**  m(chunk2325) == m(nodewise1d), both
      measured from the ALLOCATED beta on the real built network.  `bin/c78_degenerate_
      tail.sh`'s primary is a matched-count contrast, so if this is not exact the batch
      is not measuring what it claims.
  N9  **THE DEGENERATE TAIL IS GONE, AND IT IS THE ONLY THING THAT WENT.**  nodewise has
      9,610 groups of size 1; nodewise1d has none, and every group it does have is a
      group nodewise also had EXCEPT on the 1-D tensors.
  N10 NOTHING REGRESSED.  permnode@identity == nodewise, chunk1 == weightwise and
      chunk<huge> == layerwise still hold, so PATCH_NODEBN disturbed neither
      PATCH_PERMNODE nor PATCH_CHUNKWISE.

Any failure means the degenerate-tail arm is not measuring what it claims and every
number taken from it is void.

RUN ON THE CLUSTER (needs torch + the patched HF.py):
  ssh alice "cd /data1/salehkaleybars/metaopt/hierarchical-metaoptimize && \
             NODEBN_TEST_DEVICE=cpu python3 tests/test_nodebn.py"
"""
import sys, os
import collections
# CIFAR10_DIR lets this run against a SCRATCH copy of the tree, so the patch can be
# verified without editing the live HF.py that running jobs import.  Default is the
# real tree, so the test is still a check on what actually ships.
sys.path.insert(0, os.environ.get(
    "CIFAR10_DIR",
    "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10"))
import torch
import torch.nn as nn
from build_network import build_network
from Optimizers.HF import HF

# DEVICE: CPU BY DEFAULT, AND THAT IS NOT A CONVENIENCE -- IT IS THE TEST'S VALIDITY.
# Measured on this cluster (cycle 75, STANDING RULE 20): running the SAME config twice on
# CUDA gives max|dbeta| = 2.2e-01, because cuDNN's conv backward is nondeterministic and
# Lion's sign() amplifies any float-level difference into a full +-2*ms beta step at
# whichever coordinate sits nearest a sign boundary.  That is the SAME magnitude as a real
# partition difference, so an equivalence test run on CUDA cannot distinguish "identical"
# from "completely different".  N0 asserts determinism rather than assuming it.
DEV = torch.device(os.environ.get("NODEBN_TEST_DEVICE", "cpu"))
BASE = {"alg": "SGDm", "weight_decay": 0.1, "momentum_param": 0.99}
# THE REGIME MATTERS (test_chunkwise learned this the hard way).  At alpha0=1e-6 and a
# small ms, beta barely moves and every partition produces the same weights, so the
# equivalences pass VACUOUSLY.  alpha0=1e-3 with ms=1e-2 over 25 steps moves beta enough
# for partitions to genuinely diverge; N6 is the standing guard that this is still true.
ALPHA0 = 1e-3
STEPS = 25
META = {"alg": "Lion", "meta_stepsize": 1e-2, "momentum_param": 0.99,
        "Lion_beta2": 0.9, "weight_decay": 0}
CHUNK_MATCH = 2325          # the K bin/c78_degenerate_tail.sh registers for the match
FAILS = []


class NullWriter:
    def add_scalar(self, *a, **k):
        pass


class NoBiasNet(nn.Module):
    """A net whose parameters are ALL ndim >= 2.

    N1's whole point is that nodewise1d and nodewise can only differ on 1-D tensors, so
    the test needs a network that has none.  Conv2d(bias=False) and Linear(bias=False)
    give exactly that, and BatchNorm -- the source of every 1-D tensor in ResNet18 -- is
    deliberately absent.
    """

    def __init__(self):
        super().__init__()
        self.c1 = nn.Conv2d(3, 8, 3, padding=1, bias=False)
        self.c2 = nn.Conv2d(8, 16, 3, stride=2, padding=1, bias=False)
        self.c3 = nn.Conv2d(16, 16, 1, bias=False)
        self.fc = nn.Linear(16 * 16 * 16, 10, bias=False)

    def forward(self, x):
        x = torch.relu(self.c1(x))
        x = torch.relu(self.c2(x))
        x = torch.relu(self.c3(x))
        return self.fc(x.reshape(x.shape[0], -1))


def fresh_net(seed=0):
    torch.manual_seed(seed)
    return build_network("ResNet18", DEV)


def fresh_nobias(seed=0):
    torch.manual_seed(seed)
    return NoBiasNet().to(DEV)


def make_opt(net, groups, meta_stepsize=None):
    meta = dict(META)
    if meta_stepsize is not None:
        meta["meta_stepsize"] = meta_stepsize
    return HF(net, stepsize_groups=groups, alpha0=ALPHA0, args_base=dict(BASE),
              args_meta=meta, gamma=1, writer=NullWriter())


def _beta_flat(opt):
    return torch.cat([b.detach().float().reshape(-1).cpu() for b in opt.beta])


def run_steps(groups, k=STEPS, seed=0, meta_stepsize=None, builder=fresh_net):
    """Return (weights, flat beta).  BETA is where the partition actually lives, so the
    equivalences are asserted on it as well as on the weights."""
    net = builder(seed)
    opt = make_opt(net, groups, meta_stepsize)
    crit = nn.CrossEntropyLoss()
    g = torch.Generator().manual_seed(1234)
    for _ in range(k):
        x = torch.randn(8, 3, 32, 32, generator=g).to(DEV)
        y = torch.randint(0, 10, (8,), generator=g).to(DEV)
        loss = crit(net(x), y)
        opt.step(net, loss)
    return ([p.detach().float().cpu().clone() for p in net.parameters()],
            _beta_flat(opt))


def compare(name, ra, rb, tol=1e-6, want_equal=True):
    wa, ba = ra
    wb, bb = rb
    w_worst = max((x - y).abs().max().item() for x, y in zip(wa, wb))
    b_worst = ((ba - bb).abs().max().item() if ba.numel() == bb.numel()
               else float("inf"))
    worst = max(w_worst, b_worst)
    ok = (worst <= tol) if want_equal else (worst > tol)
    print(f"  {'PASS' if ok else 'FAIL'}  {name:52s} "
          f"w={w_worst:.3e} beta={b_worst:.3e}")
    if not ok:
        FAILS.append(name)
    return ok


def compare_w(name, ra, rb, tol=1e-6, want_equal=True):
    """WEIGHTS ONLY.  Used where the two arms have beta vectors of DIFFERENT LENGTH by
    construction, so a beta comparison is not defined.  Named differently so a
    weights-only pass can never be mistaken for a full equivalence."""
    w_worst = max((x - y).abs().max().item() for x, y in zip(ra[0], rb[0]))
    ok = (w_worst <= tol) if want_equal else (w_worst > tol)
    print(f"  {'PASS' if ok else 'FAIL'}  {name:52s} w={w_worst:.3e} "
          f"(WEIGHTS ONLY -- beta lengths differ by construction)")
    if not ok:
        FAILS.append(name)
    return ok


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name:56s} {detail}")
    if not cond:
        FAILS.append(name)
    return cond


def m_of(opt):
    return int(sum(int(b.numel()) for b in opt.beta))


print(f"device={DEV}")
_net = fresh_net()
SHAPES = [tuple(p.shape) for p in _net.parameters()]
NUMELS = [int(p.numel()) for p in _net.parameters()]
NODE_GROUPS = [s[0] for s in SHAPES]
# computed here from the SHAPES, independently of anything HF.py does
N1D_GROUPS = [1 if len(s) == 1 else s[0] for s in SHAPES]
M_NODE = sum(NODE_GROUPS)
M_N1D = sum(N1D_GROUPS)
N_ONED = sum(1 for s in SHAPES if len(s) == 1)
print(f"ResNet18: {len(NUMELS)} param tensors, {sum(NUMELS)} weights, "
      f"{N_ONED} one-dimensional tensors")
print(f"          nodewise m = {M_NODE}   nodewise1d m = {M_N1D}   "
      f"(removed {M_NODE - M_N1D})\n")

# --- N0  DETERMINISM FIRST (STANDING RULE 20) ------------------------------------
print("N0  the SAME configuration equals ITSELF (STANDING RULE 20)")
_a = run_steps("nodewise1d")
_b = run_steps("nodewise1d")
_det = compare("nodewise1d twice", _a, _b, tol=0.0)
if not _det:
    print("\n  N0 FAILED -- this device is not deterministic, so no equivalence below")
    print("  can be tested.  Re-run with NODEBN_TEST_DEVICE=cpu.  STOPPING.")
    sys.exit(1)
compare("nodewise twice", run_steps("nodewise"), run_steps("nodewise"), tol=0.0)

# --- N1  THE STRUCTURAL EQUIVALENCE ----------------------------------------------
print("\nN1  on a net with NO 1-D parameters, nodewise1d == nodewise, BITWISE")
_nb = fresh_nobias()
_nb_shapes = [tuple(p.shape) for p in _nb.parameters()]
check("the test net really has no 1-D parameters",
      all(len(s) >= 2 for s in _nb_shapes),
      f"shapes={_nb_shapes}")
compare("nodewise1d == nodewise on the bias-free net",
        run_steps("nodewise1d", builder=fresh_nobias),
        run_steps("nodewise", builder=fresh_nobias), tol=0.0)
_o1 = make_opt(fresh_nobias(), "nodewise1d")
_o2 = make_opt(fresh_nobias(), "nodewise")
check("and the two allocate the SAME beta count there",
      m_of(_o1) == m_of(_o2), f"{m_of(_o1)} == {m_of(_o2)}")

# --- N2  GROUP COUNTS ON THE REAL NET, FROM THE ALLOCATED BETA -------------------
print("\nN2  group counts on ResNet18, MEASURED from the ALLOCATED beta")
_on = make_opt(fresh_net(), "nodewise1d")
check("m(nodewise1d) equals the value computed from the shapes",
      m_of(_on) == M_N1D, f"allocated {m_of(_on)} == computed {M_N1D}")
check("HF's per-tensor group counts equal the independently computed ones",
      list(_on.n1d_groups) == N1D_GROUPS)
check("every 1-D tensor gets exactly ONE group",
      all(_on.n1d_groups[i] == 1 for i, s in enumerate(SHAPES) if len(s) == 1),
      f"{N_ONED} such tensors")
check("every ndim>=2 tensor keeps nodewise's shape[0] groups",
      all(_on.n1d_groups[i] == s[0] for i, s in enumerate(SHAPES) if len(s) >= 2))
check("m dropped by exactly (sum of 1-D channel counts) - (number of 1-D tensors)",
      M_NODE - M_N1D == sum(s[0] for s in SHAPES if len(s) == 1) - N_ONED,
      f"{M_NODE - M_N1D}")

# --- N3  NO PADDING, NO RESCALING ------------------------------------------------
print("\nN3  groups * gsize == numel on every tensor (no padding, no rescaling)")
check("groups[i]*gsize[i] == numel[i] for all tensors",
      all(_on.n1d_groups[i] * _on.n1d_gsize[i] == NUMELS[i]
          for i in range(len(NUMELS))))
check("no gsize is zero or negative", all(g > 0 for g in _on.n1d_gsize),
      f"min gsize {min(_on.n1d_gsize)}, max {max(_on.n1d_gsize)}")

# --- N4  THE ALPHA MAP -----------------------------------------------------------
print("\nN4  alpha at flat position j == exp(beta[j // gsize]), over every weight")
_g2 = torch.Generator().manual_seed(99)
for i in range(len(_on.beta)):
    _on.beta[i] = (torch.randn(_on.beta[i].shape, generator=_g2) * 0.3).to(DEV)
_al = _on.beta_to_alpha(_on.beta)
_worst, _checked = 0.0, 0
for i, a in enumerate(_al):
    want = torch.exp(_on.beta[i].detach().cpu()).repeat_interleave(_on.n1d_gsize[i])
    got = a.detach().float().reshape(-1).cpu()
    _worst = max(_worst, (want - got).abs().max().item())
    _checked += got.numel()
check("alpha round-trip exact over all weights", _worst == 0.0,
      f"max|d|={_worst:.3e} over {_checked} weights")
check("every weight was checked", _checked == sum(NUMELS), f"{_checked}")

# --- N5  ms = 0  =>  IDENTICAL TO NODEWISE ---------------------------------------
print("\nN5  meta_stepsize = 0  =>  nodewise1d trains identically to nodewise")
compare_w("nodewise1d == nodewise at ms=0",
          run_steps("nodewise1d", meta_stepsize=0.0),
          run_steps("nodewise", meta_stepsize=0.0), tol=0.0)

# --- N6  ANTI-VACUITY ------------------------------------------------------------
print("\nN6  ANTI-VACUITY: nodewise1d != nodewise on the real net at a real ms")
compare_w("nodewise1d diverges from nodewise", run_steps("nodewise1d"),
          run_steps("nodewise"), tol=1e-6, want_equal=False)

# --- N7  THE PROBE SEES IT -------------------------------------------------------
print("\nN7  the per-layer-LIST branch: beta is a LIST, so the probe counts m")
check("beta is a list of per-tensor tensors", isinstance(_on.beta, list),
      f"len {len(_on.beta)} == {len(NUMELS)} tensors")
check("one beta tensor per parameter tensor", len(_on.beta) == len(NUMELS))
check("stepsize_type is the new type, not 'nodewise' or 'blockwise'",
      _on.stepsize_type == "nodewise1d", _on.stepsize_type)
check("nodewise1d is a substring of neither 'scalar' nor 'blockwise'",
      ("nodewise1d" not in "scalar") and ("nodewise1d" not in "blockwise"))

# --- N8  THE MATCHED COUNT THE BATCH DEPENDS ON ----------------------------------
print(f"\nN8  m(chunk{CHUNK_MATCH}) == m(nodewise1d), both from the ALLOCATED beta")
_oc = make_opt(fresh_net(), f"chunk{CHUNK_MATCH}")
check(f"m(chunk{CHUNK_MATCH}) == m(nodewise1d)", m_of(_oc) == m_of(_on),
      f"{m_of(_oc)} vs {m_of(_on)}")
check("and both equal the independently computed m", m_of(_oc) == M_N1D, f"{M_N1D}")

# --- N9  THE DEGENERATE TAIL IS GONE, AND ONLY IT ---------------------------------
print("\nN9  the degenerate size-1 tail is gone, and it is the only thing that went")
_node_sizes = [NUMELS[i] // NODE_GROUPS[i]
               for i in range(len(NUMELS)) for _ in range(NODE_GROUPS[i])]
_n1d_sizes = [_on.n1d_gsize[i]
              for i in range(len(NUMELS)) for _ in range(_on.n1d_groups[i])]
_cn = collections.Counter(_node_sizes)
_c1 = collections.Counter(_n1d_sizes)
check("nodewise has 9,610 size-1 groups", _cn[1] == 9610, f"{_cn[1]}")
check("they are 66.6% of nodewise's groups covering 0.09% of weights",
      abs(100.0 * _cn[1] / M_NODE - 66.64) < 0.05
      and abs(100.0 * _cn[1] / sum(NUMELS) - 0.086) < 0.01,
      f"{100.0*_cn[1]/M_NODE:.2f}% of groups, {100.0*_cn[1]/sum(NUMELS):.3f}% of weights")
check("nodewise1d has NO size-1 groups", _c1[1] == 0, f"{_c1[1]}")
# The POOLED size histogram cannot be compared class by class: the 1-D tensors' new group
# sizes are their own numels (64, 128, 256, 512, 10), and 64/128/256/512 are ALSO conv
# group sizes, so nodewise1d legitimately adds to those classes.  The claim to assert is
# per TENSOR, which is what "only the 1-D tensors changed" actually means.
_nd2 = [i for i, s in enumerate(SHAPES) if len(s) >= 2]
_nd1 = [i for i, s in enumerate(SHAPES) if len(s) == 1]
check("every ndim>=2 tensor has the IDENTICAL (groups, gsize) under both",
      all((_on.n1d_groups[i], _on.n1d_gsize[i])
          == (NODE_GROUPS[i], NUMELS[i] // NODE_GROUPS[i]) for i in _nd2),
      f"{len(_nd2)} tensors")
check("the pooled size multiset over ndim>=2 tensors is UNCHANGED",
      collections.Counter(_on.n1d_gsize[i] for i in _nd2
                          for _ in range(_on.n1d_groups[i]))
      == collections.Counter(NUMELS[i] // NODE_GROUPS[i] for i in _nd2
                             for _ in range(NODE_GROUPS[i])))
check("every 1-D tensor went from (numel groups of 1) to (1 group of numel)",
      all((NODE_GROUPS[i], NUMELS[i] // NODE_GROUPS[i]) == (NUMELS[i], 1)
          and (_on.n1d_groups[i], _on.n1d_gsize[i]) == (1, NUMELS[i])
          for i in _nd1),
      f"{len(_nd1)} tensors")
check("so the 1-D tensors are the ONLY tensors whose partition changed",
      sorted(i for i in range(len(SHAPES))
             if (_on.n1d_groups[i], _on.n1d_gsize[i])
             != (NODE_GROUPS[i], NUMELS[i] // NODE_GROUPS[i])) == _nd1)
check("total weights covered is unchanged", sum(_n1d_sizes) == sum(_node_sizes)
      == sum(NUMELS), f"{sum(_n1d_sizes)}")

# --- N10  NOTHING REGRESSED -------------------------------------------------------
print("\nN10  PATCH_NODEBN disturbed neither PATCH_PERMNODE nor PATCH_CHUNKWISE")
_pn = make_opt(fresh_net(), "permnode0")
check("m(permnode0) is still nodewise's m", m_of(_pn) == M_NODE,
      f"{m_of(_pn)} == {M_NODE}")
_ow = make_opt(fresh_net(), "chunk1")
check("m(chunk1) is still the weight count", m_of(_ow) == sum(NUMELS),
      f"{m_of(_ow)}")
_ol = make_opt(fresh_net(), "chunk99999999")
check("m(chunk<huge>) is still the layer count", m_of(_ol) == len(NUMELS),
      f"{m_of(_ol)}")
compare("chunk1 == weightwise", run_steps("chunk1"), run_steps("weightwise"), tol=0.0)
compare("chunk99999999 == layerwise", run_steps("chunk99999999"),
        run_steps("layerwise"), tol=0.0)

# ---------------------------------------------------------------------------------
print()
if FAILS:
    print(f"FAILED {len(FAILS)}: " + "; ".join(FAILS))
    sys.exit(1)
print("ALL PASS -- nodewise1d is nodewise with the degenerate size-1 tail removed, "
      "and nothing else changed.")
