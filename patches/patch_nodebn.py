"""PATCH_NODEBN -- `nodewise1d`: nodewise with the DEGENERATE size-1 TAIL REMOVED.

WHY.  cycle 78's `pp1` decomposed mm1's matched-count partition gap into two legs and put the
whole of it on ONE of them:

    A  nodewise -> permnode  (ALIGNMENT: identical count, identical per-tensor size
                              multiset, membership randomised)      -0.009 pp, t = -0.06
    B  permnode -> chunk777  (SIZE DISTRIBUTION)                    +0.590 pp, t =  5.53
    D  nodewise -> chunk777  (both)                                 +0.581 pp, t =  4.11
                                                     (mm1 read D = +0.485; pooled +0.533, n=6)

So architecture alignment is worth nothing and the group-size DISTRIBUTION is worth everything.
CORRECTIONS 107.2/107.4.

**WHAT THE SIZE DISTRIBUTION ACTUALLY IS, MEASURED ON THE BUILT ResNet18** (FINDINGS 77.6):

    nodewise group size    1 :  9,610 groups = 66.64% of all groups, covering 0.09% of weights
                          27 :     64        BN-adjacent and tiny convs
                     ...
                       4,608 :  1,536 groups = 10.65% of groups, covering 63.34% of weights

Every ONE-DIMENSIONAL tensor -- all 40 BatchNorm scales and shifts, plus `linear.bias`, 41
tensors holding 9,610 scalars -- has `numel // shape[0] == 1`, so nodewise gives each of those
scalars its OWN step size.  **On ResNet18, "one step size per output channel" is two-thirds
WEIGHTWISE meta-learning on the normalisation parameters, by group count.**  chunk777 gives
each of those tensors exactly ONE group, because every channel count on this net (64..512) is
below 777.

That is the concrete, measured difference the B leg is made of, and it suggests a sharper
hypothesis than "heterogeneity is bad": **the gap is carried by the degenerate size-1 tail**.

WHAT THIS PATCH ADDS.  `--stepsize-groups nodewise1d`: nodewise on every tensor with ndim >= 2,
and ONE group for every tensor with ndim == 1.  It changes nothing else -- the conv and linear
weight matrices keep their exact per-output-channel partition, so the ARCHITECTURE ALIGNMENT
that pp1 showed is worth nothing is left in place rather than removed.  Only the degenerate
tail goes.

    m(nodewise)   = 14,420
    m(nodewise1d) =  4,851        (9,569 degenerate groups removed, 41 added)
    m(chunk2325)  =  4,851        EXACTLY -- a perfectly matched count, better than mm1's
                                  one-group-apart, found by search over K

THE CONTRAST IT MAKES POSSIBLE.  `nodewise1d` vs `chunk2325` is the mm1/pp1 matched-count
design run again with the degenerate tail taken off the architecture-aligned side.  If the
size-1 groups were the carrier, the +0.53 pp gap COLLAPSES.  If it survives, size heterogeneity
per se -- and not the degenerate tail -- is the carrier, and that is a different and more
general claim.  Either way the answer is registered before the data exists, in
`bin/c78_degenerate_tail.sh`.

WHY NOT JUST TEST "nodewise1d BEATS nodewise".  That is a real question and it is registered as
a secondary, but it is NOT the primary, because nodewise1d and nodewise differ in COUNT
(4,851 vs 14,420) and this campaign has spent three cycles establishing that count and partition
are separate axes (CORRECTIONS 105.2/105.3, 106.2).  The matched-count contrast is the one that
carries no count confound.

IMPLEMENTATION, AND THE EQUIVALENCE THAT MAKES IT TESTABLE.  A row-major tensor of shape
(d0, d1, ...) flattens with d0 as the slowest axis, so nodewise's group g is EXACTLY the flat
slice [g*gs, (g+1)*gs).  `nodewise1d` is therefore implemented as ONE code path --
`exp(beta).repeat_interleave(gsize).view(shape)` and `(u*v).reshape(groups, gsize).sum(1)` --
which, when groups == shape[0], is nodewise.  **So on a network with NO one-dimensional
parameters, `nodewise1d` must be BITWISE nodewise**, and `tests/test_nodebn.py` asserts that
against the UNPATCHED nodewise code path rather than against my expectation of it.  On the real
ResNet18, where 1-D tensors do exist, the test instead asserts the group counts tensor by
tensor and the total m against an independently computed value.

STANDING RULE 20 is observed: the suite runs on CPU and its FIRST assertion is that a
configuration equals ITSELF.

INERTNESS.  Four additions, three of them guarded by `self.stepsize_type == 'nodewise1d'`, a
type reachable only when `--stepsize-groups` is the exact string 'nodewise1d'.  Every prior
batch used a different exact string, so no existing configuration can enter any new branch and
every earlier run stays reproducible.  'nodewise1d' is a substring of neither 'scalar' nor
'blockwise', which matters because HF.py's `in`-on-a-STRING dispatches (`stepsize_type in
'scalar'`, `in 'blockwise'`) would otherwise misroute it.  Every other dispatch in the file is
`in ('scalar','layerwise','blockwise')` or an exact `==`, so 'nodewise1d' takes the
per-layer-LIST branch everywhere -- the same branch nodewise, permnode and chunkwise take --
which is why the probe, the clip guard and the PROBE5 sign counter read it with no change.
There is NO substring test on 'nodewise' anywhere in the file (verified by grep over all 40
`stepsize_type` sites), so adding a type whose name CONTAINS 'nodewise' cannot leak into the
nodewise branches.  That is asserted below rather than trusted.

MEMORY.  Nothing per-weight is stored: two small python lists of per-tensor ints.  Unlike
PATCH_PERMNODE this adds no index tensors and no resident memory.
"""
import sys, os

P = os.environ.get(
    "HF_PATH",
    "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/"
    "MetaOptimize/cifar10/Optimizers/HF.py")
src = open(P).read()

if "PATCH_NODEBN" in src:
    print("ALREADY_PATCHED")
    sys.exit(0)

assert "PATCH_GRANULARITY" in src, "PATCH_GRANULARITY must be applied before PATCH_NODEBN"
assert "PATCH_CHUNKWISE" in src, "PATCH_CHUNKWISE must be applied before PATCH_NODEBN"
assert "PATCH_PERMNODE" in src, "PATCH_PERMNODE must be applied before PATCH_NODEBN"

# THE SUBSTRING HAZARD, CHECKED BEFORE ANYTHING IS WRITTEN.  A new type whose name contains
# 'nodewise' is only safe if no dispatch in the file tests 'nodewise' as a SUBSTRING of
# stepsize_type.  Assert that, do not assume it.
assert "'nodewise' in self.stepsize_type" not in src, "a substring dispatch on nodewise exists"
assert '"nodewise" in self.stepsize_type' not in src, "a substring dispatch on nodewise exists"
assert src.count("self.stepsize_type == 'nodewise'") == 3, \
    "expected exactly 3 exact-match nodewise branches before patching"

# --- 1. TYPE DISPATCH ------------------------------------------------------------------
a1 = """            self.stepsize_type = stepsize_groups if stepsize_groups in ['scalar', 'layerwise', 'nodewise', 'weightwise'] else 'blockwise'
"""
assert src.count(a1) == 1, f"anchor 1 count={src.count(a1)} -- refusing to patch"
n1 = """            # --- PATCH_NODEBN: nodewise1d joins the exact-match list.  Membership is
            # tested on the WHOLE string, so it cannot be mistaken for plain nodewise.
            self.stepsize_type = stepsize_groups if stepsize_groups in ['scalar', 'layerwise', 'nodewise', 'weightwise', 'nodewise1d'] else 'blockwise'
"""
src = src.replace(a1, n1, 1)

# --- 2. BETA INITIALISATION ------------------------------------------------------------
a2 = """        # --- PATCH_PERMNODE: nodewise's group COUNT and SIZE per tensor, membership
"""
assert src.count(a2) == 1, f"anchor 2 count={src.count(a2)} -- refusing to patch"
n2 = """        # --- PATCH_NODEBN: nodewise on every tensor with ndim >= 2, ONE group on every
        # tensor with ndim == 1.  The 1-D tensors are exactly the BatchNorm scales and
        # shifts and the output bias -- the 9,610 groups that make 66.64% of nodewise's
        # group budget and cover 0.09% of its weights (FINDINGS 77.6).
        elif self.stepsize_type == 'nodewise1d':
            _lb = torch.log(torch.tensor(alpha0, dtype=torch.float32, device=self._device))
            self.n1d_shape = [tuple(p_size) for (_n, p_size) in net_param_names_and_size]
            self.n1d_numel = [int(np.prod(list(p_size))) for (_n, p_size) in net_param_names_and_size]
            self.n1d_groups = [1 if len(p_size) == 1 else int(p_size[0])
                               for (_n, p_size) in net_param_names_and_size]
            self.n1d_gsize = []
            for _i3, (_ne3, _g3) in enumerate(zip(self.n1d_numel, self.n1d_groups)):
                if _g3 <= 0 or _ne3 % _g3 != 0:
                    raise ValueError('nodewise1d: tensor %d has numel %d not divisible by %d'
                                     % (_i3, _ne3, _g3))
                self.n1d_gsize.append(_ne3 // _g3)
            self.beta = [_lb * torch.ones(_g3, dtype=torch.float32, device=self._device)
                         for _g3 in self.n1d_groups]
""" + a2
src = src.replace(a2, n2, 1)

# --- 3. beta_to_alpha ------------------------------------------------------------------
a3 = """        # --- PATCH_PERMNODE: expand one alpha per group, then scatter it back to the
"""
assert src.count(a3) == 1, f"anchor 3 count={src.count(a3)} -- refusing to patch"
n3 = """        # --- PATCH_NODEBN: one alpha per group, repeated over that group's members.  For a
        # row-major tensor group g is the flat slice [g*gs, (g+1)*gs), so when groups ==
        # shape[0] this is nodewise's broadcast, expressed as a dense expand.
        if self.stepsize_type == 'nodewise1d':
            alphas = [torch.exp(b).repeat_interleave(_gs).view(_sh)
                      for b, _gs, _sh in zip(beta, self.n1d_gsize, self.n1d_shape)]
            self.alpha_for_printing = alphas
            return alphas
""" + a3
src = src.replace(a3, n3, 1)

# --- 4. block_product ------------------------------------------------------------------
a4 = """        # --- PATCH_PERMNODE: gather each tensor's elementwise product into permuted
"""
assert src.count(a4) == 1, f"anchor 4 count={src.count(a4)} -- refusing to patch"
n4 = """        # --- PATCH_NODEBN: per-group sums.  numel % groups == 0 was asserted at
        # construction, so no padding is possible and no group is silently rescaled.
        if self.stepsize_type == 'nodewise1d':
            _out = []
            for i in range(self.num_layers):
                _out.append((u[i]*v[i]).reshape(self.n1d_groups[i],
                                                self.n1d_gsize[i]).sum(dim=1))
            return _out
""" + a4
src = src.replace(a4, n4, 1)

# --- structural assertions on the result -----------------------------------------------
assert "import numpy as np" in src, "expected numpy imported in HF.py"
assert "import torch" in src, "expected torch imported in HF.py"
# HF.py's `in`-on-a-STRING dispatches; 'nodewise1d' must fall into neither.
assert "nodewise1d" not in "scalar" and "nodewise1d" not in "blockwise"
# Every new branch must be guarded by the new type and nothing else.
assert src.count("self.stepsize_type == 'nodewise1d'") == 3, "expected 3 nodewise1d branches"
assert src.count("'nodewise1d'") == 4, "expected 4 mentions: 3 branches + 1 dispatch list"
assert src.count("PATCH_NODEBN") == 4, "expected 4 PATCH_NODEBN markers"
# The branches this patch must NOT disturb.
assert src.count("self.stepsize_type == 'nodewise'") == 3, "nodewise branches disturbed"
assert src.count("self.stepsize_type == 'permnode'") == 3, "permnode branches disturbed"
assert src.count("self.stepsize_type == 'chunkwise'") == 3, "chunkwise branches disturbed"
assert src.count("self.stepsize_type = 'permnode'") == 1, "permnode assignment disturbed"

open(P, "w").write(src)
print("PATCHED PATCH_NODEBN ->", P)
