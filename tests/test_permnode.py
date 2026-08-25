"""Correctness tests for PATCH_PERMNODE (`--stepsize-groups permnode<S>`).

STRATEGY, identical in spirit to tests/test_chunkwise.py: validate the new partition
against code paths that are ALREADY TRUSTED, via mathematical identities, rather than
against my expectation of what it should do.

  P0  DETERMINISM FIRST (STANDING RULE 20).  The SAME configuration run twice must give
      max|dW| = max|dbeta| = 0.  If this fails, every equivalence below is meaningless
      and the suite stops.  On CUDA this genuinely fails -- see the DEV note.
  P1  permnode<S> with the IDENTITY permutation == nodewise, BITWISE.  This is an EXACT
      equivalence, not an approximation: a row-major tensor of shape (d0, d1, ...)
      flattens with d0 slowest, so nodewise's group g IS the flat slice [g*gs,(g+1)*gs).
      Asserted against the UNPATCHED nodewise path, not against my reading of it.
  P2  THE PERMUTATIONS ARE REAL PERMUTATIONS.  For every tensor, sorted(perm) == arange
      and perm_inv is the true inverse (perm_inv[perm] == arange).  A "permutation" that
      repeated an index would silently drop weights from every group.
  P3  THE SIZE MULTISET IS NODEWISE'S, EXACTLY.  Per tensor and network-wide, permnode's
      group count and group sizes equal nodewise's -- not matched in mean, IDENTICAL as
      multisets.  This is the whole claim of the arm and it is measured, not asserted.
  P4  m(permnode<S>) == m(nodewise) == the ALLOCATED beta count, for several S.
  P5  REPRODUCIBILITY AND VARIATION.  The same S gives the same permutation twice; two
      different S give different permutations on tensors with room to differ.  Both
      matter: the first makes runs reproducible, the second makes seeds independent
      draws rather than three copies of one experiment.
  P6  meta_stepsize=0  =>  permnode trains identically to nodewise.  With beta frozen the
      partition cannot matter, so any difference here is a plumbing bug, not dynamics.
  P7  THE ALPHA ROUND-TRIP.  For a given beta, the alpha delivered to flat position
      perm[j] equals exp(beta[j // gs]).  This is the one place a scatter/gather sign
      error would be invisible in P1 (identity makes perm and perm_inv the same map).
  P8  permnode<S> != nodewise on a real net.  THE ANTI-VACUITY GUARD.  If this fails, P1
      and P6 are passing because nothing diverges, and the arm measures nothing.
  P9  THE PROBE SEES IT.  n_beta == 14,420 via the per-layer-LIST branch, the same branch
      nodewise and chunkwise take.
  P10 NOTHING REGRESSED.  chunk1 == weightwise and chunk<huge> == layerwise still hold,
      so PATCH_PERMNODE did not disturb PATCH_CHUNKWISE.

Any failure means the permuted-partition arm is not measuring what it claims and every
number taken from it is void.

RUN ON THE CLUSTER (needs torch + the patched HF.py):
  ssh alice "cd /data1/salehkaleybars/metaopt/hierarchical-metaoptimize && python3 tests/test_permnode.py"
"""
import sys, os
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
# from "completely different".  P0 asserts determinism rather than assuming it.
DEV = torch.device(os.environ.get("PERM_TEST_DEVICE", "cpu"))
BASE = {"alg": "SGDm", "weight_decay": 0.1, "momentum_param": 0.99}
# THE REGIME MATTERS (test_chunkwise learned this the hard way).  At alpha0=1e-6 and a
# small ms, beta barely moves and every partition produces the same weights, so the
# equivalences pass VACUOUSLY.  alpha0=1e-3 with ms=1e-2 over 25 steps moves beta enough
# for partitions to genuinely diverge; P8 is the standing guard that this is still true.
ALPHA0 = 1e-3
STEPS = 25
META = {"alg": "Lion", "meta_stepsize": 1e-2, "momentum_param": 0.99,
        "Lion_beta2": 0.9, "weight_decay": 0}
FAILS = []


class NullWriter:
    def add_scalar(self, *a, **k):
        pass


def fresh_net(seed=0):
    torch.manual_seed(seed)
    return build_network("ResNet18", DEV)


def make_opt(net, groups, meta_stepsize=None):
    meta = dict(META)
    if meta_stepsize is not None:
        meta["meta_stepsize"] = meta_stepsize
    return HF(net, stepsize_groups=groups, alpha0=ALPHA0, args_base=dict(BASE),
              args_meta=meta, gamma=1, writer=NullWriter())


def _beta_flat(opt):
    return torch.cat([b.detach().float().reshape(-1).cpu() for b in opt.beta])


def _identity_perm(opt):
    """Overwrite a permnode optimizer's permutation with the IDENTITY.

    This is how P1 tests the PLUMBING against nodewise without also testing the
    permutation GENERATOR -- P2/P5 test the generator separately.  Doing both at once
    would mean a failure could not be localised.
    """
    for i, n in enumerate(opt.perm_numel):
        idx = torch.arange(n, device=opt.perm_idx[i].device)
        opt.perm_idx[i] = idx
        opt.perm_inv[i] = idx.clone()
    return opt


def run_steps(groups, k=STEPS, seed=0, meta_stepsize=None, mutate=None):
    """Return (weights, flat beta).  BETA is where the partition actually lives, so the
    equivalences are asserted on it as well as on the weights."""
    net = fresh_net(seed)
    opt = make_opt(net, groups, meta_stepsize)
    if mutate is not None:
        mutate(opt)
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


def check(name, cond, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {name:56s} {detail}")
    if not cond:
        FAILS.append(name)
    return cond


print(f"device={DEV}")
_net = fresh_net()
SHAPES = [tuple(p.shape) for p in _net.parameters()]
NUMELS = [int(p.numel()) for p in _net.parameters()]
NODE_GROUPS = [s[0] for s in SHAPES]
M_NODE = sum(NODE_GROUPS)
print(f"ResNet18: {len(NUMELS)} param tensors, {sum(NUMELS)} weights, "
      f"nodewise m = {M_NODE}\n")

# --- P0  DETERMINISM FIRST (STANDING RULE 20) ------------------------------------
print("P0  the SAME configuration equals ITSELF (STANDING RULE 20)")
_a = run_steps("permnode0")
_b = run_steps("permnode0")
_det = compare("permnode0 twice", _a, _b, tol=0.0)
if not _det:
    print("\n  P0 FAILED -- this device is not deterministic, so no equivalence below")
    print("  can be tested.  Re-run with PERM_TEST_DEVICE=cpu.  STOPPING.")
    sys.exit(1)
compare("nodewise twice", run_steps("nodewise"), run_steps("nodewise"), tol=0.0)

# --- P1  IDENTITY PERMUTATION == NODEWISE, BITWISE --------------------------------
print("\nP1  permnode<S> with the IDENTITY permutation == nodewise, BITWISE")
_node = run_steps("nodewise")
for S in (0, 1, 7):
    compare(f"permnode{S} @ identity == nodewise",
            run_steps(f"permnode{S}", mutate=_identity_perm), _node, tol=0.0)

# --- P2  THE PERMUTATIONS ARE REAL PERMUTATIONS -----------------------------------
print("\nP2  every perm is a true permutation and perm_inv is its true inverse")
_opt = make_opt(fresh_net(), "permnode3")
_bad_perm, _bad_inv = [], []
for i, n in enumerate(_opt.perm_numel):
    pi = _opt.perm_idx[i].cpu()
    iv = _opt.perm_inv[i].cpu()
    ar = torch.arange(n)
    if not torch.equal(torch.sort(pi).values, ar):
        _bad_perm.append(i)
    if not torch.equal(iv[pi], ar):
        _bad_inv.append(i)
check("sorted(perm) == arange on every tensor", not _bad_perm,
      f"{len(_opt.perm_numel)} tensors, bad={_bad_perm[:5]}")
check("perm_inv[perm] == arange on every tensor", not _bad_inv,
      f"bad={_bad_inv[:5]}")

# --- P3  THE SIZE MULTISET IS NODEWISE'S, EXACTLY ---------------------------------
print("\nP3  the group-size multiset is nodewise's, per tensor and network-wide")
check("group COUNT per tensor == nodewise's",
      list(_opt.perm_groups) == NODE_GROUPS,
      f"first 5: {list(_opt.perm_groups)[:5]} vs {NODE_GROUPS[:5]}")
_want_gsize = [n // g for n, g in zip(NUMELS, NODE_GROUPS)]
check("group SIZE per tensor == nodewise's",
      list(_opt.perm_gsize) == _want_gsize,
      f"first 5: {list(_opt.perm_gsize)[:5]} vs {_want_gsize[:5]}")
_perm_multiset = sorted(gs for g, gs in zip(_opt.perm_groups, _opt.perm_gsize)
                        for _ in range(g))
_node_multiset = sorted(gs for g, gs in zip(NODE_GROUPS, _want_gsize)
                        for _ in range(g))
check("the WHOLE-NETWORK size multiset is identical",
      _perm_multiset == _node_multiset,
      f"{len(_perm_multiset)} groups, min={min(_perm_multiset)} "
      f"max={max(_perm_multiset)}")
check("groups x size covers every weight exactly once",
      sum(_perm_multiset) == sum(NUMELS),
      f"{sum(_perm_multiset)} vs {sum(NUMELS)}")
check("the multiset is genuinely HETEROGENEOUS (else the arm is trivial)",
      len(set(_perm_multiset)) > 1,
      f"{len(set(_perm_multiset))} distinct sizes")

# --- P4  m(permnode<S>) == m(nodewise), from the ALLOCATED beta -------------------
print("\nP4  m(permnode<S>) == m(nodewise), read from the ALLOCATED beta")
_m_node = int(sum(int(b.numel()) for b in make_opt(fresh_net(), "nodewise").beta))
check("nodewise allocates the expected m", _m_node == M_NODE, f"m={_m_node}")
for S in (0, 1, 2, 5):
    m = int(sum(int(b.numel()) for b in make_opt(fresh_net(), f"permnode{S}").beta))
    check(f"m(permnode{S}) == m(nodewise)", m == _m_node, f"m={m}")

# --- P5  REPRODUCIBILITY AND VARIATION --------------------------------------------
print("\nP5  same seed -> same permutation; different seeds -> different permutations")
_o1 = make_opt(fresh_net(), "permnode1")
_o1b = make_opt(fresh_net(), "permnode1")
_o2 = make_opt(fresh_net(), "permnode2")
check("permnode1 built twice gives the SAME permutation",
      all(torch.equal(a.cpu(), b.cpu())
          for a, b in zip(_o1.perm_idx, _o1b.perm_idx)))
_big = [i for i, n in enumerate(_o1.perm_numel) if n > 64]
_diff = sum(1 for i in _big
            if not torch.equal(_o1.perm_idx[i].cpu(), _o2.perm_idx[i].cpu()))
check("permnode1 != permnode2 on every sizeable tensor",
      _diff == len(_big), f"{_diff}/{len(_big)} tensors differ")
_same_tensor = sum(1 for i, j in zip(_big, _big[1:])
                   if _o1.perm_numel[i] == _o1.perm_numel[j]
                   and torch.equal(_o1.perm_idx[i].cpu(), _o1.perm_idx[j].cpu()))
check("two same-sized tensors get DIFFERENT permutations within one seed",
      _same_tensor == 0, f"{_same_tensor} colliding pairs")

# --- P6  ms=0 => permnode == nodewise ---------------------------------------------
print("\nP6  meta_stepsize=0 => permnode trains identically to nodewise")
compare("permnode4 @ ms=0 == nodewise @ ms=0",
        run_steps("permnode4", meta_stepsize=0.0),
        run_steps("nodewise", meta_stepsize=0.0), tol=0.0)

# --- P7  THE ALPHA ROUND-TRIP ------------------------------------------------------
print("\nP7  alpha at flat position perm[j] == exp(beta[j // gsize])")
_o = make_opt(fresh_net(), "permnode6")
torch.manual_seed(99)
_beta = [torch.randn_like(b) for b in _o.beta]
_alpha = _o.beta_to_alpha(_beta)
_worst, _checked = 0.0, 0
for i in range(len(_beta)):
    af = _alpha[i].reshape(-1)
    pi = _o.perm_idx[i]
    gs = _o.perm_gsize[i]
    want = torch.exp(_beta[i]).repeat_interleave(gs)
    got = af[pi]
    _worst = max(_worst, (got - want).abs().max().item())
    _checked += int(pi.numel())
check("alpha round-trips through the permutation exactly", _worst == 0.0,
      f"max|d| = {_worst:.3e} over {_checked} weights")
check("beta_to_alpha returns one tensor per parameter, in that parameter's shape",
      [tuple(a.shape) for a in _alpha] == SHAPES)
_o_id = _identity_perm(make_opt(fresh_net(), "permnode6"))
_a_id = _o_id.beta_to_alpha(_beta)
_o_nd = make_opt(fresh_net(), "nodewise")
_a_nd = _o_nd.beta_to_alpha(_beta)
_w2 = max((torch.broadcast_to(x, s).reshape(-1)
           - torch.broadcast_to(y, s).reshape(-1)).abs().max().item()
          for x, y, s in zip(_a_id, _a_nd, SHAPES))
check("identity-perm alpha == nodewise alpha, elementwise", _w2 == 0.0,
      f"max|d| = {_w2:.3e}")

# --- P8  THE ANTI-VACUITY GUARD ----------------------------------------------------
print("\nP8  permnode<S> genuinely DIVERGES from nodewise (else P1/P6 are vacuous)")
compare("permnode0 != nodewise on a real net", run_steps("permnode0"), _node,
        tol=1e-6, want_equal=False)
compare("permnode0 != permnode1 (seeds are independent draws)",
        run_steps("permnode0"), run_steps("permnode1"), tol=1e-6, want_equal=False)

# --- P9  THE PROBE SEES IT ---------------------------------------------------------
print("\nP9  the probe reads the permuted partition through the per-layer LIST branch")
_op = make_opt(fresh_net(), "permnode0")
check("beta is a per-layer LIST, not a single tensor",
      isinstance(_op.beta, list) and len(_op.beta) == len(SHAPES),
      f"len={len(_op.beta)}")
check("n_beta == m(nodewise)",
      int(sum(int(b.numel()) for b in _op.beta)) == M_NODE)
check("'permnode' is a substring of neither 'scalar' nor 'blockwise'",
      ("permnode" not in "scalar") and ("permnode" not in "blockwise"))
check("stepsize_type is exactly 'permnode'", _op.stepsize_type == "permnode",
      _op.stepsize_type)

# --- P10  NOTHING REGRESSED --------------------------------------------------------
print("\nP10  PATCH_CHUNKWISE still holds (the new patch disturbed nothing)")
_HUGE = max(NUMELS) + 1
compare("chunk1 == weightwise", run_steps("chunk1"), run_steps("weightwise"), tol=0.0)
compare(f"chunk{_HUGE} == layerwise", run_steps(f"chunk{_HUGE}"),
        run_steps("layerwise"), tol=0.0)

print()
if FAILS:
    print(f"FAILED {len(FAILS)}: " + ", ".join(FAILS))
    sys.exit(1)
print("ALL PERMNODE TESTS PASS")
