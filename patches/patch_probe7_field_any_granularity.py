"""PATCH_PROBE7 -- the per-COORDINATE meta-gradient sign field at ANY training granularity.

WHY THIS EXISTS
---------------
CORRECTIONS 94.7 (cycle 65) names what is now the binding uncertainty in direction C, and it
is a LIMIT OF THE INSTRUMENT, not of the science:

    The per-coordinate field is observable ONLY under weightwise training.  Coarse probes
    store per-GROUP counts -- `probe_c100_lay_s0` has n_tot = 62, `..._node_s0` 14,600,
    `..._blk6_s0` 6, against `..._w_s0` 11,220,132.  So every `E` in cycles 62-65 is measured
    in the weightwise arm, and every comparison assumes the field's SHAPE is not itself
    created by the training granularity.  That assumption is untested.

It is sharpened by FINDINGS 65.7: **weightwise is the WORST resolved granularity in every free
cell** (68.50 vs 74.52 layerwise on r18; 26.89 vs 38.17 on c100).  The campaign's entire field
measurement -- including the 53.1% sign-agreement headline -- is taken in the one arm that
trains worst.  Whether the kernel-scale peak (65.2, 17/17 arms) survives under a granularity
anyone would actually use is UNKNOWN, and with the recorded data it is UNKNOWABLE.

THE OBSERVATION THAT MAKES THIS CHEAP
-------------------------------------
`HF.block_product(u, v)` reduces the SAME elementwise product differently per granularity:

    scalar      sum over everything                       -> 1 scalar
    blockwise   sum per block                             -> n_blocks
    layerwise   (u[i]*v[i]).sum()                          -> n_tensors
    nodewise    (u[i]*v[i]).reshape(O,-1).sum(dim=1)       -> n_output_channels
    weightwise  u[i]*v[i]                       NO REDUCTION -> n_coordinates

So the per-coordinate field `u[i]*v[i]` **exists in every granularity** -- it is simply summed
away before it is ever seen.  A layerwise run can therefore record exactly the field a
weightwise run records, at no change to training whatsoever, by counting signs on the product
BEFORE the reduction.  Nothing about beta, the optimizer, or the update is touched.

WHAT THIS ADDS
--------------
One sidecar pair beside `probe.jsonl`, mirroring PATCH_PROBE5's format exactly so that every
existing reducer works unchanged (CORRECTIONS 18 is the rule this obeys -- no new field ever
enters the jsonl):

    coord_neg_counts.npy    float32 [n_coordinates]  running count of (u*v) < 0
    coord_neg_counts.json   {n_records, n_tot, stepsize_type, hier, patch: 'PROBE7'}

Written under a DIFFERENT filename from `neg_counts.npy` on purpose: in the weightwise arm both
exist and MUST agree (see the gate below); giving them one name would make that gate
unwriteable and would silently overwrite four cycles of corpus.

THE VALIDATION GATE -- REGISTERED HERE, BEFORE ANY DATA, AND NOT TO BE EDITED AFTER
-----------------------------------------------------------------------------------
In the **weightwise** arm `z = [u[i]*v[i]]` and PATCH_PROBE2 builds `zall` as
`torch.cat([zi.reshape(-1) for zi in z])` in tensor order 0..num_layers-1 -- which is the
identical expression, in the identical order, that this patch accumulates.  Therefore:

    GATE P7.  One weightwise run with PROBE5=1 AND PROBE7=1 must produce
              coord_neg_counts.npy EXACTLY EQUAL to neg_counts.npy (bitwise, not approximately).

    If they differ by even one coordinate, the two fields are NOT the same object and NO
    layerwise field measured by this patch may be compared to the cycle 62-65 corpus.  Run the
    gate FIRST; it costs one 20-epoch job.

    SCOPE OF THE GATE: it holds for `hier=''` ONLY.  `_probe` is called AFTER `_zpool` /
    `_zmpool`, so in a hier arm the existing `zall` is POST-pool while this patch's product is
    PRE-pool, and the two are different quantities BY CONSTRUCTION.  `hier` is recorded in the
    json so a hier run can never be mistaken for a gate pass.  All of 62-65 excludes hier arms
    anyway (CORRECTIONS 21).

WHAT IT WILL ANSWER, PRE-REGISTERED PER STANDING RULE (10)
-----------------------------------------------------------
Score the c62/c63 u-ladder on a LAYERWISE-trained and a NODEWISE-trained run and compare the
peak location u* to the weightwise corpus (65.2: u* ~ 0.0017, 1-9 coordinates, 17/17 arms):

  * u* stays at 1/512-1/1024 under layerwise/nodewise training
        -> the kernel-scale peak is a property of the FIELD, 94.7 is discharged, and the
           cycle 62-65 measurements generalise beyond the weightwise arm.  FINDINGS 65's
           separation result gets strictly stronger, because the field peak would then be
           ~5 decades from the training optimum measured IN THE SAME ARM.
  * u* moves to the training granularity's own scale (u ~ 1 nodewise, u ~ O layerwise)
        -> the peak is an ARTIFACT of what the optimizer was allowed to adapt, direction C's
           scale claims are conditioned on the weightwise arm, and 62.9 / 64 / 65.2 must all
           be restated with that condition attached.  This is the outcome that costs the most
           and it is the reason to run the test.
  * anything else -> written as UNDECIDED, not rounded to a verdict.

WHY THE GATE CAN BE EXPECTED TO PASS EXACTLY, AND THE ONE PLACE IT COULD NOT
-----------------------------------------------------------------------------
Order: PATCH_PROBE2 builds `zall` by iterating the list `z`, which `block_product` built as
`[u[i]*v[i] for i in range(self.num_layers)]`; this patch concatenates over the identical
`range(self.num_layers)`.  Same expression, same order, same tensor count.

Dtype: the existing path compares `zall < 0` AFTER a `.float()` widening cast, this patch
compares the product in its native dtype.  A widening cast is exact and sign-preserving, so
`(x.float() < 0) == (x < 0)` for every finite x and for +/-inf; the only value where the two
could differ is a NaN, which is False on both sides.  The gate is therefore an equality test
that a correct implementation passes BITWISE, not approximately -- which is why it is written
as bitwise, and why a near-miss must be treated as a failure and investigated, never rounded.

COST
----
One elementwise multiply plus one comparison over the full parameter vector, once per probe
RECORD (not per step) -- at PROBE=25 that is 1/25th of the step rate, and it is the same order
as the `frac_neg` pass PATCH_PROBE2 already runs.  Memory: one float32 accumulator the size of
the parameter vector (45 MB at 11.2M params) plus a transient of the same size, and a held
reference to `g` between the product and the probe call.  Fits every partition in use.

INERTNESS
---------
Pure read-only accumulation inside the existing `torch.no_grad()` emission block, gated on
PROBE7=1.  With PROBE7 unset the only added work is one attribute read per step, and every
output file is byte-identical to every earlier batch.
"""
import sys, os

P = os.environ.get(
    "HF_PATH",
    "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/"
    "MetaOptimize/cifar10/Optimizers/HF.py")
src = open(P).read()

if "PATCH_PROBE7" in src:
    print("ALREADY_PATCHED")
    sys.exit(0)

# ---------------------------------------------------------------------------------------
# (1) Stash the block_product OPERANDS at the call site.  `_probe` only ever receives the
#     REDUCED z, so the pre-reduction operands have to be captured in step().  Guarded by
#     getattr so the first step (before _probe_init has run) stashes and every later step
#     obeys the flag; `os` is not assumed to be bound in step()'s scope.
# ---------------------------------------------------------------------------------------
anchor_step = "            self._probe(HtT_gradft)  # PATCH_PROBE\n"
assert src.count(anchor_step) == 1, \
    f"step anchor count={src.count(anchor_step)} -- refusing to patch"

stash = ("            if getattr(self, '_p7_on', True):  # PATCH_PROBE7\n"
         "                self._p7_uv = (self.h_condenced, g)\n")
src = src.replace(anchor_step, stash + anchor_step, 1)

# ---------------------------------------------------------------------------------------
# (2) Resolve the flag once, in _probe_init, and drop the stash when it is off.
# ---------------------------------------------------------------------------------------
anchor_init = "        self._probe_every = int(os.environ.get('PROBE', '0'))\n"
assert src.count(anchor_init) == 1, \
    f"init anchor count={src.count(anchor_init)} -- refusing to patch"
src = src.replace(
    anchor_init,
    anchor_init +
    "        self._p7_on = (os.environ.get('PROBE7', '') == '1')  # PATCH_PROBE7\n"
    "        if not self._p7_on:\n"
    "            self._p7_uv = None\n",
    1)

# ---------------------------------------------------------------------------------------
# (3) Accumulate on the SAME cadence as PATCH_PROBE5, so the two fields are record-for-record
#     comparable.  Anchored on the PATCH_PROBE2 lines, which sit after the write gate; this is
#     the same anchor PATCH_PROBE5 uses, so the two patches compose in either order.
# ---------------------------------------------------------------------------------------
anchor = ("        frac_neg = (zall < 0).sum().item() / max(n_tot, 1)\n"
          "        frac_zero = (zall == 0).sum().item() / max(n_tot, 1)\n")
assert src.count(anchor) == 1, f"probe anchor count={src.count(anchor)} -- refusing to patch"

add = '''        # --- PATCH_PROBE7: per-COORDINATE sign field, ANY granularity ---
        if os.environ.get('PROBE7', '') == '1' and getattr(self, '_p7_uv', None) is not None:
            _u7, _v7 = self._p7_uv
            _prod7 = torch.cat([(_u7[_i] * _v7[_i]).reshape(-1)
                                for _i in range(self.num_layers)])
            _n7 = _prod7.numel()
            if getattr(self, '_p7_neg', None) is None or self._p7_neg.numel() != _n7:
                self._p7_neg = torch.zeros(_n7, dtype=torch.float32, device=_prod7.device)
                self._p7_n = 0
            self._p7_neg += (_prod7 < 0).float()
            self._p7_n += 1
            del _prod7
            _p7_every = int(os.environ.get('PROBE7_WRITE_EVERY', '20'))
            if self._p7_n % max(_p7_every, 1) == 0:
                import numpy as _np
                _t7 = os.path.join(self._probe_dir, 'coord_neg_counts.npy.tmp')
                _d7 = os.path.join(self._probe_dir, 'coord_neg_counts.npy')
                _np.save(_t7, self._p7_neg.detach().cpu().numpy())
                os.replace(_t7, _d7)
                with open(os.path.join(self._probe_dir, 'coord_neg_counts.json'), 'w') as _fh:
                    json.dump({'n_records': int(self._p7_n), 'n_tot': int(_n7),
                               'stepsize_type': self.stepsize_type,
                               'hier': str(getattr(self, '_hier', '')),
                               'patch': 'PROBE7'}, _fh)
'''

src = src.replace(anchor, anchor + add, 1)

# `json` is bound by `import json, os` at the top of _probe; assert it so the inserted block
# cannot reference an unbound name (the failure mode PATCH_PROBE5 guards the same way).
assert "import json, os" in src, "expected `import json, os` inside _probe"
assert src.count("PATCH_PROBE7") == 3, "expected exactly three PATCH_PROBE7 marks"

open(P, "w").write(src)
print("PATCHED PATCH_PROBE7 ->", P)
print("GATE P7 (registered): one weightwise run with PROBE5=1 PROBE7=1 and hier='' must give")
print("  coord_neg_counts.npy BITWISE EQUAL to neg_counts.npy.  Run it before any layerwise")
print("  field is compared to the cycle 62-65 corpus.")
