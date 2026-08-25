"""PATCH_PERMNODE -- nodewise's EXACT group-size multiset, with membership RANDOMISED.

WHY.  CORRECTIONS 105.7 ranked this first among all pending code changes, and cycle 77's
`mm1` M1 is what makes it the next thing to run.  M1 CONFIRMED at matched count: chunk777
(m=14,421) beats nodewise (m=14,420) by +0.485 pp within one batch, with the count matched to
ONE group and no cross-batch offset available to explain it.  So the partition matters.

**But "the partition matters" is not the sentence worth having.**  The sentence that would
bear on the Adam-mini / Adalayer / SGG line is "grouping weights BY ARCHITECTURE is worse than
grouping the same number of weights arbitrarily" -- and `mm1` cannot support it, because its
two arms differ in TWO ways at once:

    nodewise  -- groups = output channels; sizes HETEROGENEOUS across tensors
                 (a 3x3x512 conv gives groups of 4,608; a BatchNorm vector gives groups of 1)
    chunk777  -- groups = flat contiguous chunks; sizes UNIFORM at 777 everywhere

Matched m fixes the MEAN group size by construction and says nothing about the DISTRIBUTION.
CORRECTIONS 105.3 said this in advance and forbade the alignment sentence for exactly this
reason.

WHAT THIS PATCH ADDS.  `--stepsize-groups permnode<S>`: for each parameter tensor, keep
nodewise's group COUNT and nodewise's group SIZE, and randomise only WHICH weights land in
which group, using a permutation of that tensor's flat indices seeded by S and the tensor's
position.  Every tensor keeps exactly the group-size multiset nodewise gave it, so:

    m(permnode<S>) == m(nodewise) == 14,420   EXACTLY, for every S
    the per-tensor size multiset is IDENTICAL, not merely matched in mean

`permnode` vs `nodewise` therefore varies ONE thing: whether a group is an output channel or
an arbitrary same-sized subset of the SAME layer.  That is the architecture-alignment
contrast, with the count, the size distribution and the layer boundaries all held fixed.

THE THREE-WAY DECOMPOSITION IT COMPLETES, all at m ~ 14,420:
    nodewise  -> permnode  : ALIGNMENT      (sizes identical, membership randomised)
    permnode  -> chunk777  : SIZE DISTRIBUTION (membership arbitrary in both, sizes differ)
    nodewise  -> chunk777  : both at once   = mm1's measured +0.485 pp
The two legs must sum to +0.485 within noise, and that is a CHECK on the decomposition, not
an assumption of it.

WHY THE PERMUTATION IS WITHIN A TENSOR AND NOT ACROSS THE NETWORK.  Permuting across tensors
would change the size multiset's meaning and would also mix layers of wildly different scale
into one step size, which is a different intervention with a different story.  Within-tensor
permutation asks the narrow question the prior-art line actually asks: **is an output channel
special among the same-sized subsets of its own layer?**  The limit this leaves is stated
rather than hidden -- permnode does NOT test whether LAYER boundaries matter, only whether
within-layer channel structure does.

INERTNESS.  Four additions, every one inside `if self.stepsize_type == 'permnode'`, a type
that is set only when `--stepsize-groups` matches `^permnode(\\d+)$`.  Every prior batch fails
that regex, so no existing configuration can enter any new branch and every earlier run stays
reproducible.  'permnode' is a substring of neither 'scalar' nor 'blockwise', which matters
because HF.py:124 and HF.py:127 are `in` on a STRING, not on a tuple.  Every other dispatch in
the file is `in ('scalar','layerwise','blockwise')`, so 'permnode' takes the per-layer-LIST
branch everywhere -- the same branch nodewise and chunkwise take -- which is why the probe,
the clip guard and the PROBE5 sign counter all read it with no further change.

THE ENDPOINT EQUIVALENCE THAT MAKES IT TESTABLE.  A row-major tensor of shape (d0, d1, ...)
flattens with d0 as the slowest axis, so nodewise's group g is EXACTLY the flat slice
[g*gs, (g+1)*gs).  Therefore **permnode with the IDENTITY permutation is bitwise nodewise**,
and `tests/test_permnode.py` asserts that against the UNPATCHED nodewise code path rather than
against my expectation of it.  STANDING RULE 20 is observed: the suite runs on CPU and its
FIRST assertion is that a configuration equals ITSELF.

MEMORY.  Two int64 index tensors per parameter, 11.17M entries each in total => ~179 MB
resident on top of the model.  The batch requests 14 GB, so this is not a constraint, but it
is written down because it scales with parameter count and would matter on a larger net.
"""
import sys, os

P = os.environ.get(
    "HF_PATH",
    "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/"
    "MetaOptimize/cifar10/Optimizers/HF.py")
src = open(P).read()

if "PATCH_PERMNODE" in src:
    print("ALREADY_PATCHED")
    sys.exit(0)

assert "PATCH_GRANULARITY" in src, "PATCH_GRANULARITY must be applied before PATCH_PERMNODE"
assert "PATCH_CHUNKWISE" in src, "PATCH_CHUNKWISE must be applied before PATCH_PERMNODE"

# --- 1. TYPE DISPATCH ------------------------------------------------------------------
# Inserted BEFORE the chunkwise dispatch's `else:` chain by hooking the chunk regex block.
a1 = """        # --- PATCH_CHUNKWISE: `chunk<K>` = contiguous chunks of K weights ---
        import re as _re
        _cm = _re.match(r'^chunk(\\d+)$', stepsize_groups) if isinstance(stepsize_groups, str) else None
        if _cm:
            self.stepsize_type = 'chunkwise'
            self.chunk_size = int(_cm.group(1))
            if self.chunk_size < 1:
                raise ValueError('chunk size must be >= 1, got %r' % self.chunk_size)
        else:
"""
assert src.count(a1) == 1, f"anchor 1 count={src.count(a1)} -- refusing to patch"
n1 = """        # --- PATCH_CHUNKWISE: `chunk<K>` = contiguous chunks of K weights ---
        import re as _re
        _cm = _re.match(r'^chunk(\\d+)$', stepsize_groups) if isinstance(stepsize_groups, str) else None
        # --- PATCH_PERMNODE: `permnode<S>` = nodewise's sizes, membership permuted ---
        _pm = _re.match(r'^permnode(\\d+)$', stepsize_groups) if isinstance(stepsize_groups, str) else None
        if _pm:
            self.stepsize_type = 'permnode'
            self.perm_seed = int(_pm.group(1))
        elif _cm:
            self.stepsize_type = 'chunkwise'
            self.chunk_size = int(_cm.group(1))
            if self.chunk_size < 1:
                raise ValueError('chunk size must be >= 1, got %r' % self.chunk_size)
        else:
"""
src = src.replace(a1, n1, 1)

# --- 2. BETA INITIALISATION ------------------------------------------------------------
a2 = """        # --- PATCH_CHUNKWISE ---
        elif self.stepsize_type == 'chunkwise':
"""
assert src.count(a2) == 1, f"anchor 2 count={src.count(a2)} -- refusing to patch"
n2 = """        # --- PATCH_PERMNODE: nodewise's group COUNT and SIZE per tensor, membership
        # randomised by a per-tensor permutation of that tensor's flat indices.  The
        # permutation is generated on the CPU from an explicit torch.Generator so it is
        # identical on CPU and GPU and reproducible from (perm_seed, tensor index) alone.
        elif self.stepsize_type == 'permnode':
            _S = self.perm_seed
            _lb = torch.log(torch.tensor(alpha0, dtype=torch.float32, device=self._device))
            self.perm_shape = [tuple(p_size) for (_n, p_size) in net_param_names_and_size]
            self.perm_numel = [int(np.prod(list(p_size))) for (_n, p_size) in net_param_names_and_size]
            self.perm_groups = [int(p_size[0]) for (_n, p_size) in net_param_names_and_size]
            self.perm_gsize = []
            self.perm_idx = []
            self.perm_inv = []
            for _i2, (_ne, _g2) in enumerate(zip(self.perm_numel, self.perm_groups)):
                if _g2 <= 0 or _ne % _g2 != 0:
                    raise ValueError('permnode: tensor %d has numel %d not divisible by %d'
                                     % (_i2, _ne, _g2))
                self.perm_gsize.append(_ne // _g2)
                _gen = torch.Generator()
                _gen.manual_seed(_S * 1000003 + _i2)
                _pi = torch.randperm(_ne, generator=_gen)
                _iv = torch.empty_like(_pi)
                _iv[_pi] = torch.arange(_ne)
                self.perm_idx.append(_pi.to(self._device))
                self.perm_inv.append(_iv.to(self._device))
            self.beta = [_lb * torch.ones(_g2, dtype=torch.float32, device=self._device)
                         for _g2 in self.perm_groups]
""" + a2
src = src.replace(a2, n2, 1)

# --- 3. beta_to_alpha ------------------------------------------------------------------
a3 = """        # --- PATCH_CHUNKWISE: one alpha per contiguous chunk of K weights ---
        if self.stepsize_type == 'chunkwise':
"""
assert src.count(a3) == 1, f"anchor 3 count={src.count(a3)} -- refusing to patch"
n3 = """        # --- PATCH_PERMNODE: expand one alpha per group, then scatter it back to the
        # tensor's own layout through the inverse permutation.  Gathering with perm_inv is
        # the same map as scattering with perm_idx and costs no allocation per step.
        if self.stepsize_type == 'permnode':
            alphas = [torch.exp(b).repeat_interleave(_gs)[_iv].view(_sh)
                      for b, _gs, _iv, _sh in zip(beta, self.perm_gsize, self.perm_inv,
                                                  self.perm_shape)]
            self.alpha_for_printing = alphas
            return alphas
""" + a3
src = src.replace(a3, n3, 1)

# --- 4. block_product ------------------------------------------------------------------
a4 = """        # --- PATCH_CHUNKWISE: per-chunk sums, zero-padded to a whole number of chunks.
"""
assert src.count(a4) == 1, f"anchor 4 count={src.count(a4)} -- refusing to patch"
n4 = """        # --- PATCH_PERMNODE: gather each tensor's elementwise product into permuted
        # order, then sum in exact groups of gsize.  numel % groups == 0 was asserted at
        # construction, so no padding is possible and no group is silently rescaled.
        if self.stepsize_type == 'permnode':
            _out = []
            for i in range(self.num_layers):
                _p = (u[i]*v[i]).reshape(-1)[self.perm_idx[i]]
                _out.append(_p.view(self.perm_groups[i], self.perm_gsize[i]).sum(dim=1))
            return _out
""" + a4
src = src.replace(a4, n4, 1)

# --- structural assertions on the result -----------------------------------------------
assert "import numpy as np" in src, "expected numpy imported in HF.py"
assert "import torch" in src, "expected torch imported in HF.py"
# HF.py:124 and :127 are `in` on a STRING; 'permnode' must fall into neither.
assert "permnode" not in "scalar" and "permnode" not in "blockwise"
# Every new branch must be guarded by the new type and nothing else.
assert src.count("self.stepsize_type == 'permnode'") == 3, "expected 3 permnode branches"
assert src.count("self.stepsize_type = 'permnode'") == 1, "expected 1 permnode assignment"
assert src.count("PATCH_PERMNODE") == 4, "expected 4 PATCH_PERMNODE markers"
# The chunkwise branches must survive untouched.
assert src.count("self.stepsize_type == 'chunkwise'") == 3, "chunkwise branches disturbed"

open(P, "w").write(src)
print("PATCHED PATCH_PERMNODE ->", P)
