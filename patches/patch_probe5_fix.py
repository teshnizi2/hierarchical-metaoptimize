"""PATCH_PROBE5_FIX -- repairs a fatal filename bug in PATCH_PROBE5 (cycle 47).

THE BUG.  patch_probe5.py writes the per-group negative counts with

    _tmp = os.path.join(self._probe_dir, 'neg_counts.npy.tmp')
    _np.save(_tmp, ...)
    os.replace(_tmp, _dst)

`numpy.save` appends `.npy` to a STRING path that does not already end in `.npy`.
'neg_counts.npy.tmp' does not, so numpy writes **neg_counts.npy.tmp.npy** and the
very next line `os.replace('neg_counts.npy.tmp', ...)` raises FileNotFoundError.

Measured, not inferred (cycle 47):
    >>> np.save('/tmp/d/neg_counts.npy.tmp', np.zeros(3)); os.listdir('/tmp/d')
    ['neg_counts.npy.tmp.npy']
    >>> os.path.exists('/tmp/d/neg_counts.npy.tmp')
    False

CONSEQUENCE HAD IT SHIPPED.  The write fires at probe record 500, i.e. 2,500 steps
= 5 epochs into a 20-epoch run.  Every job in the 8-job c44 PROBE5 batch would have
crashed at 5 epochs with FileNotFoundError, after burning ~25% of its wallclock, and
`neg_counts.json` -- the file the batch's own structural check #2 requires -- would
never exist.  The batch would have returned nothing.

THE FIX.  Hand numpy an open file OBJECT instead of a path.  numpy.save does not
append an extension to a file object, so the atomic write-then-rename semantics are
preserved exactly and the on-disk name is the intended one.

WHAT IS *NOT* A BUG, checked and recorded so it is not "fixed" again.  `os` and
`json` are NOT module-level imports in HF.py, and an AST scope check shows the
`import os` at line 298 lives in `_probe_init`, a DIFFERENT function from `_probe`
where the PROBE5 block sits.  That looks fatal and is not: `_probe` does its own
`import json, os` at line 335, which executes before the PROBE5 block at line 363
on every record.  Both names resolve.  Verified by reading the executing scope, not
by grepping the file for `import os`.

IDEMPOTENT: prints ALREADY_FIXED and exits 0 on a second run.
"""
import os
import sys

P = os.environ.get(
    "HF_PATH",
    "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/"
    "MetaOptimize/cifar10/Optimizers/HF.py")
src = open(P).read()

if "PATCH_PROBE5" not in src:
    print("NOT_PATCHED -- apply patch_probe5.py first; refusing to fix")
    sys.exit(1)

if "PATCH_PROBE5_FIX" in src:
    print("ALREADY_FIXED")
    sys.exit(0)

old = ("                _np.save(_tmp, self._p5_neg.detach().cpu().numpy())\n"
       "                os.replace(_tmp, _dst)\n")
new = ("                # PATCH_PROBE5_FIX: np.save appends '.npy' to a STRING path that\n"
       "                # lacks it, so save(_tmp) would write neg_counts.npy.tmp.npy and the\n"
       "                # replace below would fail.  A file OBJECT gets no extension added.\n"
       "                with open(_tmp, 'wb') as _fh5:\n"
       "                    _np.save(_fh5, self._p5_neg.detach().cpu().numpy())\n"
       "                os.replace(_tmp, _dst)\n")

n = src.count(old)
assert n == 1, f"anchor count={n} -- refusing to patch"

open(P, "w").write(src.replace(old, new))
print(f"FIXED PATCH_PROBE5_FIX -> {P}")
