"""Add HIER=zmpool -- the MEAN-normalised sibling of zpool.

WHY (cycle 12): zpool interpolates z'_b = (1-r)*sum(z) + r*z_b.  Both endpoints are exact,
but the shared term carries a factor of m (the group count), so the INTERIOR of the ladder
runs at a wildly different meta-gradient magnitude than either endpoint.  Measured on the
completed zsw block (layerwise, m=62): realised exp(mean beta) relative to r=1 is

    r=0 -> 0.895   r=0.1 -> 0.779   r=0.3 -> 0.149   r=0.5 -> 0.047   r=0.7 -> 0.029   r=1 -> 1.000

i.e. the interior trains at 3-35x SMALLER step size than the endpoints.  Any accuracy read
off the interior conflates pooling strength with step-size magnitude.

zmpool replaces sum with mean:   z'_b = (1-r)*mean(z) + r*z_b
so the shared term no longer scales with m and the ladder holds magnitude roughly fixed.
r=1 is still EXACTLY plain.  r=0 is uniform-beta at mean magnitude -- which is NOT the
scalar arm (the scalar arm's meta-gradient is genuinely the sum), so this ladder anchors
on r=1 only and must carry its own r=0 reference rather than borrowing zpool's.

The existing _zpool method is left BYTE-IDENTICAL; zmpool is a separate method reached by a
separate dispatch arm, so no previously measured zpool cell can change.
"""
import sys, os
P = os.environ.get("HF_PATH") or "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10/Optimizers/HF.py"
s = open(P).read()
if "PATCH_ZMPOOL" in s:
    print("ALREADY"); sys.exit(0)
assert "PATCH_ZPOOL" in s, "zpool patch must be applied first"
orig = s

# 1) dispatch arm, immediately after the existing zpool arm
a = """            if self._hier == 'zpool':  # PATCH_ZPOOL
                HtT_gradft = self._zpool(HtT_gradft)"""
assert s.count(a) == 1, "dispatch anchor %d" % s.count(a)
s = s.replace(a, a + """
            elif self._hier == 'zmpool':  # PATCH_ZMPOOL
                HtT_gradft = self._zmpool(HtT_gradft)""", 1)

# 2) the operator, inserted just before PATCH_HIER
a2 = "    # ------------------------------------------------------------ PATCH_HIER"
assert s.count(a2) == 1
s = s.replace(a2, '''    # ---------------------------------------------------------- PATCH_ZMPOOL
    def _zmpool(self, z):
        """z'_b = (1-r)*mean(z) + r*z_b.  r=1 => plain exactly; magnitude is m-invariant."""
        r = self._hier_ratio
        if r == 1.0:
            return z
        if self.stepsize_type == 'scalar':
            return z
        if self.stepsize_type in ('layerwise', 'blockwise'):
            mu = z[0].sum() / z[0].numel()
            return [mu + r * (z[0] - mu)]
        # weightwise / nodewise: z is a list of per-tensor tensors
        tot = sum(zz.sum() for zz in z)
        cnt = sum(zz.numel() for zz in z)
        mu = tot / cnt
        return [mu + r * (zz - mu) for zz in z]

''' + a2, 1)

open(P + ".bak_zmpool", "w").write(orig)
open(P, "w").write(s)
print("PATCH_ZMPOOL_OK")
