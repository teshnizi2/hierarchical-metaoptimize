"""PATCH_CHUNKWISE -- a CONTIGUOUS-CHUNK partition, so the three-decade hole between
nodewise (14,420 groups) and weightwise (11,173,962 groups) can be measured instead of
interpolated.

WHY.  CORRECTIONS 104.8.  The optimizer supports `scalar` / `blockwise` (of LAYERS) /
`layerwise` / `nodewise` / `weightwise` and nothing else, and `blockwise` is COARSER than
layerwise.  So the campaign's central curve -- accuracy, sign agreement and N_eff/m against
group count m -- has FIVE points and a hole three decades wide in exactly the interval where
both the accuracy collapse and the agreement collapse happen (FINDINGS 74.3, 74.4, 74.5).
Every statement about WHERE the fine end turns bad is currently an interpolation between two
points.  This patch turns that into a measurement.

WHAT IT ADDS.  `--stepsize-groups chunk<K>` (e.g. `chunk1024`): each parameter tensor's
weights are cut, in flat index order, into contiguous chunks of K, and each chunk carries one
beta.  m(K) = sum_layers ceil(numel_layer / K).  One knob interpolates the WHOLE range:

    K = 1        -> m = 11,173,962  == weightwise, exactly
    K >= max numel -> m = 62        == layerwise, exactly

Both endpoints are EXACT EQUIVALENCES, not approximations, and that is what makes the patch
testable: `Lion_meta_update` (HF.py:548) is `beta - ms*sign(...)` applied elementwise with no
norm and no cross-element reduction, so splitting one beta tensor into several list entries
cannot change any update.  `tests/test_chunkwise.py` asserts both equivalences numerically
against the UNPATCHED code paths rather than against my expectation of them.

WHY CONTIGUOUS CHUNKS AND NOT SOMETHING CLEVERER.  A chunk is the one grouping that is
defined identically at every K, needs no architecture knowledge, and has weightwise and
layerwise as literal endpoints.  Nodewise is NOT on this path -- it groups by output channel,
which is a different partition of the same weights -- so nodewise's own argmax `ms` (3e-4)
does not bear on the chunk ladder, and the chunk ladder does not supersede the nodewise datum.

INERTNESS.  Three additions, all inside `if self.stepsize_type == 'chunkwise'` branches that
no existing configuration can enter: the type is only set when `--stepsize-groups` matches
`^chunk(\\d+)$`, which every prior batch fails.  No existing code path is edited, so every
earlier run stays reproducible.  The name 'chunkwise' is also checked against HF.py's two
`in`-on-a-STRING tests (`self.stepsize_type in 'scalar'`, `... in 'blockwise'`): 'chunkwise'
is a substring of neither, so it cannot fall into a coarse branch by accident.  That check is
not cosmetic -- those two lines are `in` on a string, not on a tuple.

THE PROBE COMES FOR FREE, AND THAT IS CHECKED, NOT ASSUMED.  `_probe` branches on
`stepsize_type in ('scalar','layerwise','blockwise')` -> beta is a single tensor, else -> beta
is a per-layer LIST.  'chunkwise' takes the list branch, the same one nodewise and weightwise
take, so `n_beta`, `beta_true_min/max`, `n_at_lo/hi`, `frac_neg` and the PROBE5 sign counter
all read the chunk partition with no further change.
"""
import sys, os

P = os.environ.get(
    "HF_PATH",
    "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/"
    "MetaOptimize/cifar10/Optimizers/HF.py")
src = open(P).read()

if "PATCH_CHUNKWISE" in src:
    print("ALREADY_PATCHED")
    sys.exit(0)

# The patch depends on PATCH_GRANULARITY already being applied (it reuses self._device and
# sits beside the layerwise/nodewise/weightwise branches that patch created).
assert "PATCH_GRANULARITY" in src, "PATCH_GRANULARITY must be applied before PATCH_CHUNKWISE"
assert "import re" in src or True, ""

# --- 1. TYPE DISPATCH ------------------------------------------------------------------
a1 = ("        self.stepsize_type = stepsize_groups if stepsize_groups in "
      "['scalar', 'layerwise', 'nodewise', 'weightwise'] else 'blockwise'\n")
assert src.count(a1) == 1, f"anchor 1 count={src.count(a1)} -- refusing to patch"
n1 = ('''        # --- PATCH_CHUNKWISE: `chunk<K>` = contiguous chunks of K weights ---
        import re as _re
        _cm = _re.match(r'^chunk(\\d+)$', stepsize_groups) if isinstance(stepsize_groups, str) else None
        if _cm:
            self.stepsize_type = 'chunkwise'
            self.chunk_size = int(_cm.group(1))
            if self.chunk_size < 1:
                raise ValueError('chunk size must be >= 1, got %r' % self.chunk_size)
        else:
''' + "    " + a1.rstrip("\n") + "\n")
src = src.replace(a1, n1, 1)

# --- 2. BETA INITIALISATION ------------------------------------------------------------
a2 = """        elif self.stepsize_type == 'weightwise':
            _lb = torch.log(torch.tensor(alpha0, dtype=torch.float32, device=self._device))
            self.beta = [_lb * torch.ones(tuple(p_size), dtype=torch.float32, device=self._device)
                         for (_n, p_size) in net_param_names_and_size]
"""
assert src.count(a2) == 1, f"anchor 2 count={src.count(a2)} -- refusing to patch"
n2 = a2 + """        # --- PATCH_CHUNKWISE ---
        elif self.stepsize_type == 'chunkwise':
            _K = self.chunk_size
            _lb = torch.log(torch.tensor(alpha0, dtype=torch.float32, device=self._device))
            self.chunk_numel = [int(np.prod(list(p_size))) for (_n, p_size) in net_param_names_and_size]
            self.chunk_shape = [tuple(p_size) for (_n, p_size) in net_param_names_and_size]
            self.chunk_counts = [(_n2 + _K - 1) // _K for _n2 in self.chunk_numel]
            self.beta = [_lb * torch.ones(_c, dtype=torch.float32, device=self._device)
                         for _c in self.chunk_counts]
"""
src = src.replace(a2, n2, 1)

# --- 3. beta_to_alpha ------------------------------------------------------------------
a3 = """        if self.stepsize_type == 'nodewise':
            alphas = [torch.exp(b).view(v) for b, v in zip(beta, self.node_view)]
            self.alpha_for_printing = alphas
            return alphas
"""
assert src.count(a3) == 1, f"anchor 3 count={src.count(a3)} -- refusing to patch"
n3 = a3 + """        # --- PATCH_CHUNKWISE: one alpha per contiguous chunk of K weights ---
        if self.stepsize_type == 'chunkwise':
            _K = self.chunk_size
            alphas = [torch.exp(b).repeat_interleave(_K)[:_n].view(_s)
                      for b, _n, _s in zip(beta, self.chunk_numel, self.chunk_shape)]
            self.alpha_for_printing = alphas
            return alphas
"""
src = src.replace(a3, n3, 1)

# --- 4. block_product ------------------------------------------------------------------
a4 = ("        if self.stepsize_type == 'nodewise':\n"
      "            return [(u[i]*v[i]).reshape(u[i].shape[0], -1).sum(dim=1) "
      "for i in range(self.num_layers)]\n")
assert src.count(a4) == 1, f"anchor 4 count={src.count(a4)} -- refusing to patch"
n4 = a4 + """        # --- PATCH_CHUNKWISE: per-chunk sums, zero-padded to a whole number of chunks.
        # The pad contributes exactly 0 to its chunk's sum, so a ragged final chunk is
        # summed over its REAL members only and is not silently scaled.
        if self.stepsize_type == 'chunkwise':
            _K = self.chunk_size
            _out = []
            for i in range(self.num_layers):
                _p = (u[i]*v[i]).reshape(-1)
                _n3 = _p.numel()
                _c = (_n3 + _K - 1) // _K
                _pad = _c * _K - _n3
                if _pad:
                    _p = torch.cat([_p, _p.new_zeros(_pad)])
                _out.append(_p.view(_c, _K).sum(dim=1))
            return _out
"""
src = src.replace(a4, n4, 1)

# The inserted code uses np and torch; both are module-level imports in HF.py.
assert "import numpy as np" in src, "expected numpy imported in HF.py"
assert "import torch" in src, "expected torch imported in HF.py"
# 'chunkwise' must not be a substring of the two `in`-on-a-STRING tests.
assert "chunkwise" not in "scalar" and "chunkwise" not in "blockwise"

open(P, "w").write(src)
print("PATCHED PATCH_CHUNKWISE ->", P)
