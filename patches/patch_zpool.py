"""Corrected hierarchy: interpolate in META-GRADIENT space, not beta space.

The earlier `HIER=shrink` pooled beta toward a MEAN while the scalar arm aggregates the
meta-gradient as a SUM, a factor-of-m discrepancy that made the m=n column meaningless.

Key identity: for every granularity, sum_b z_b == z_scalar exactly (z_b = h_b .* g_b, and the
scalar arm's z is the total inner product). So define

    z'_b = (1 - r) * (sum_j z_j)  +  r * z_b

  r = 0  -> every group receives the scalar arm's meta-gradient  => EXACTLY scalar
  r = 1  -> every group receives its own meta-gradient           => EXACTLY plain per-group

Both endpoints are exact identities and are verified numerically before use.
"""
import sys
P="/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10/Optimizers/HF.py"
s=open(P).read()
if "PATCH_ZPOOL" in s: print("ALREADY"); sys.exit(0)
orig=s

a="            self.meta_update(HtT_gradft)"
assert s.count(a)==1, "anchor %d"%s.count(a)
s=s.replace(a, """            if self._hier == 'zpool':  # PATCH_ZPOOL
                HtT_gradft = self._zpool(HtT_gradft)
"""+a, 1)

a2="    # ------------------------------------------------------------ PATCH_HIER"
assert s.count(a2)==1
s=s.replace(a2, '''    # ----------------------------------------------------------- PATCH_ZPOOL
    def _zpool(self, z):
        """z'_b = (1-r)*sum(z) + r*z_b.  r=0 => scalar exactly; r=1 => plain exactly."""
        r = self._hier_ratio
        if r == 1.0:
            return z
        if self.stepsize_type == 'scalar':
            return z
        if self.stepsize_type in ('layerwise', 'blockwise'):
            tot = z[0].sum()
            return [tot + r * (z[0] - tot)] if r != 0.0 else [torch.full_like(z[0], 0.0) + tot]
        # weightwise / nodewise: z is a list of per-tensor tensors
        tot = sum(zz.sum() for zz in z)
        if r == 0.0:
            return [torch.zeros_like(zz) + tot for zz in z]
        return [tot + r * (zz - tot) for zz in z]

''' + a2, 1)
open(P+".bak_zpool","w").write(orig); open(P,"w").write(s)
print("PATCH_ZPOOL_OK")
