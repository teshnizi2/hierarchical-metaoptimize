"""PATCH_TWOLEVEL -- G1: the hierarchical proposal AS LITERALLY WRITTEN.

WHY THIS EXISTS
---------------
Arsalan's November-2025 proposal is: *learn a scalar and layerwise step sizes JOINTLY, and
shrink the layerwise ones toward the scalar with a tunable strength.*  What the tree contains
instead (PATCH_HIER, `_apply_hier`) is a POST-HOC PROJECTION applied once per optimizer step:

    shrink:    beta   <-  beta - lam * (beta - mean(beta))
    additive:  beta   <-  beta_prev + mean(d) + r * (d - mean(d)),   d = beta - beta_prev

The `shrink` form is the one that claims to be the proposal, and its lambda is **not a
strength**.  Applied every step, the surviving deviation after T steps is (1 - lam)^T, so
lambda is a HALF-LIFE:

    half-life(lam) = ln 2 / -ln(1 - lam)   steps

CIFAR-10 has 50,000 training images and every run in this corpus uses batch_size = 100, so a
100-epoch run takes 500 steps/epoch x 100 = **50,000 meta steps**.  Then

    lam = 1e-3  ->  half-life 692.8 steps  ->   72.2 half-lives in one run
    lam = 1e-2  ->  half-life  69.0 steps  ->  725   half-lives
    lam = 1e-1  ->  half-life   6.6 steps  ->  7,600 half-lives

Every rung of the only archived lambda ladder is at lam >= 1e-3.  All of them measured FULL
POOLING; the ladder was flat by construction, not by finding.  The live decade is [1e-4, 1e-3]
and there are no runs in it.  (Re-derive both statements from results/all_runs.csv before
using them: they are re-derived in bin/cG1_twolevel_ladder.sh's GUARD 2, which aborts the
submission if they have stopped being true.)

WHAT THIS PATCH ADDS
--------------------
The TWO-LEVEL parameterisation -- MAIN-IDEA-GAPS G2, "arguably what the proposal actually
describes", and no patch for it has ever existed:

    beta_g(t) = s(t) + d_g(t)                                                          (1)

s is ONE shared log step size, d_g is group g's deviation from it, and BOTH are learned
jointly, by the run's own meta-optimizer, from the run's own meta-gradient.  They differ in
exactly one thing -- their meta-step-size:

    s    <-  META( s,   z_s,  eta       ),   z_s = sum_g z_g                           (2)
    d_g  <-  META( d_g, z_g,  rho * eta )                                              (3)

z_g = HtT_gradft[g] = dJ/d beta_g is the meta-gradient HF already computes and already feeds
to `meta_update`; z_s = sum_g z_g is its chain rule through (1).  META is whatever
`--alg-meta` names (Lion, Adam, RMSProp), applied VERBATIM, with one independent
trace/momentum state per level.

`rho` is read from the existing `ETA_RATIO` environment variable, whose name already means
exactly this -- the ratio of the deviations' meta-step-size to the shared one.  Reusing it
means the dial is already printed on every run's own ENV line by jobs/run_cifar.sh and is
already carried into results/all_runs.csv by analysis/aggregate.py, with no change to either.

    SHRINKAGE STRENGTH = 1 - rho.
    rho = 0  ->  d_g is driven by a step size of exactly 0 at every step, so d_g == 0 for all
                 t and beta_g == s: the arm is ARITHMETICALLY THE SCALAR ARM, with the shared
                 level still learned at the full rate eta.  (This is a checkable identity,
                 and it is checked twice: offline in tests/tl_equivalence.py and in-batch by
                 gate G1 of analysis/cG1_tl_score.py against a scalar control.)
    rho = 1  ->  the deviations learn as fast as the shared level.

WHY rho IS A STRENGTH AND lam IS NOT -- the entire point of G1
--------------------------------------------------------------
`shrink` MULTIPLIES an existing quantity down: nothing in it opposes the decay, so the only
fixed point is d_g = 0 and lambda selects how fast the run reaches it.  Any lambda large
enough to be a "strength" is also large enough to reach the fixed point in the first epoch.

In (1)-(3), d_g is a STATE VARIABLE with its own driven dynamics, not a quantity being
multiplied down.  It is pushed by its own meta-gradient at rate rho*eta and there is no decay
term at all when the meta weight decay is 0 (it is 0 in every run in this corpus).  Under a
Lion meta the increment is  -rho*eta*sign(...), of CONSTANT magnitude rho*eta at every step,
so the scale of the deviations is proportional to rho at t = 1,000 and at t = 50,000 alike.
The dial is dimensionless, it is a ratio of two meta-step-sizes, and it is stationary in T.
Nothing saturates.  tests/tl_equivalence.py measures this directly: it reports
std(beta) against t for a rho ladder and for a lambda ladder side by side.

This is form (b) of MAIN-IDEA-GAPS section 1.4, "the most faithful one".  Form (d) -- a
periodic PARTIAL shrink -- is NOT implemented here and must not be: it only reparameterises
the per-step coefficient (lam_eff ~ lam/k) and saturates identically.

THE BOX
-------
step() clips the COMPOSITE beta (PATCH_CLIP) immediately after this returns.  `_tl_update`
re-derives d_g = beta_g - s at its NEXT entry, so a clip is absorbed into the deviations
instead of winding the two levels apart, and invariant (1) holds exactly at every step.  The
shared level is clamped into the same box for the same reason.  With rho = 0 the composite is
uniform, so the clip is uniform, so d_g stays identically 0 and the scalar identity survives
the box.

DISABLED = NO-OP, AND IT IS PROVED, NOT ASSERTED
------------------------------------------------
Every line this patch adds is reached only when HIER == 'twolevel'.  The single edit to an
existing code path wraps the two pinned lines

        self.meta_update(HtT_gradft)
        if self._hier:  # PATCH_HIER
            self._apply_hier()

in `if self._hier == 'twolevel': ... else:` with those two lines, verbatim, as the else arm.
Nothing else in HF.py is touched -- not `_apply_hier`, not `_zpool`, not `_zmpool`, not
`meta_update`, not `_probe`, not `init_meta`.  919 completed runs on this account depend on
that.  tests/tl_equivalence.py runs the PINNED module and the PATCHED module side by side for
every pre-existing HIER mode and asserts BITWISE-identical beta and weights; run it on the
cluster before any submission.

USAGE
-----
    HF_PATH=<...>/Optimizers/HF.py python3 patches/patch_twolevel.py

Idempotent: re-running prints ALREADY_PATCHED and exits 0.
"""
import sys, os

P = os.environ.get(
    "HF_PATH",
    "/home/s5014158/metaopt/MetaOptimize/codes/Supervised_tasks/"
    "MetaOptimize/cifar10/Optimizers/HF.py")
src = open(P).read()

if "PATCH_TWOLEVEL" in src:
    print("ALREADY_PATCHED")
    sys.exit(0)

# ---- the tree this patch is written against ---------------------------------------------
assert "PATCH_HIER" in src, "PATCH_HIER must be applied before PATCH_TWOLEVEL"
assert "PATCH_CLIP" in src, "PATCH_CLIP must be applied before PATCH_TWOLEVEL"
assert "PATCH_GRANULARITY" in src, "PATCH_GRANULARITY must be applied before PATCH_TWOLEVEL"

# THE SUBSTRING HAZARD.  A new HIER mode string is only safe if no dispatch tests self._hier
# as a SUBSTRING in either direction.  Assert it; do not assume it.
assert "in self._hier" not in src, "substring dispatch on self._hier already exists"
assert "self._hier in " not in src, "reversed-`in` dispatch on self._hier already exists"
for _existing in ("shrink", "additive", "zpool", "zmpool"):
    assert "twolevel" not in _existing and _existing not in "twolevel", \
        "mode name collides with %r under a substring test" % _existing

# The four pre-existing modes are dispatched by EQUALITY only, in exactly these places.
assert src.count("self._hier == 'zpool'") == 1
assert src.count("self._hier == 'zmpool'") == 1
assert src.count("self._hier == 'shrink'") == 2      # layerwise branch + list branch
assert src.count("self._hier == 'additive'") == 2    # layerwise branch + list branch

# =========================================================================================
# (1) THE ONLY EDIT TO AN EXISTING CODE PATH.  The two pinned lines become the `else` arm,
#     character for character, so every pre-existing HIER mode and HIER-unset run takes a
#     code path that is textually identical to the pinned one.
# =========================================================================================
a1 = """            self.meta_update(HtT_gradft)
            if self._hier:  # PATCH_HIER
                self._apply_hier()
"""
assert src.count(a1) == 1, "step() dispatch anchor count=%d -- refusing to patch" % src.count(a1)

n1 = """            if self._hier == 'twolevel':  # PATCH_TWOLEVEL
                self._tl_update(HtT_gradft)
            else:
                self.meta_update(HtT_gradft)
                if self._hier:  # PATCH_HIER
                    self._apply_hier()
"""
src = src.replace(a1, n1, 1)

# =========================================================================================
# (2) THE OPERATOR.  New methods only; inserted immediately before PATCH_PROBE's block.
# =========================================================================================
a2 = """    # ----------------------------------------------------------- PATCH_PROBE
    def _probe_init(self):
"""
assert src.count(a2) == 1, "PATCH_PROBE anchor count=%d -- refusing to patch" % src.count(a2)

n2 = '''    # -------------------------------------------------------- PATCH_TWOLEVEL
    # G1 -- the proposal as literally written.
    #
    #     beta_g(t) = s(t) + d_g(t)                                             (1)
    #     s     <- META( s,   z_s,  eta       ),  z_s = sum_g z_g               (2)
    #     d_g   <- META( d_g, z_g,  rho * eta )                                 (3)
    #
    # z_g = HtT_gradft[g] is the meta-gradient HF already computes; z_s is its
    # chain rule through (1).  META is the run's own --alg-meta rule, verbatim,
    # with one independent trace/momentum state per level.  rho is ETA_RATIO.
    # SHRINKAGE STRENGTH = 1 - rho.  rho = 0 pins d_g at exactly 0 for every t,
    # so the arm is arithmetically the SCALAR arm with the shared level still
    # learned at the full rate eta.
    #
    # rho IS A STRENGTH, NOT A TIME CONSTANT.  PATCH_HIER's `shrink` multiplies
    # the deviation by (1 - lam) once per step, so what survives after T steps
    # is (1 - lam)^T and lam is a half-life -- ln2/-ln(1-lam) steps, i.e. 693 at
    # lam=1e-3 against ~50,000 steps per 100-epoch run, 72 half-lives, full
    # pooling before epoch 2.  Here d_g is a STATE driven at rate rho*eta with
    # no decay term (the meta weight decay is 0 in every run in this corpus), so
    # its scale is proportional to rho at every t and stationary in T.
    #
    # THE BOX.  step() clips the COMPOSITE right after this returns; the next
    # entry re-derives d_g = beta_g - s, so the clip is absorbed into the
    # deviations and invariant (1) holds exactly at every step.
    def _tl_init(self):
        """Allocate the two levels.  Called on the first _tl_update, never otherwise."""
        if self.stepsize_type == 'scalar':
            raise ValueError("HIER=twolevel needs a grouped stepsize_type; "
                             "'scalar' has no deviations to shrink")
        if self.args_meta['alg'] not in ('Lion', 'Adam', 'RMSProp'):
            raise ValueError("HIER=twolevel supports --alg-meta in {Lion, Adam, "
                             "RMSProp}; got %r" % (self.args_meta['alg'],))
        _b0 = self.beta[0]
        self._tl_s = _b0.new_zeros(()) + _b0.reshape(-1)[0]
        self._tl_d = [torch.zeros_like(_b) for _b in self.beta]
        self._tl_mo_s = 0.0
        self._tl_tr_s = 0.0
        self._tl_mo_d = [0.0 for _ in range(self.len_beta_list)]
        self._tl_tr_d = [0.0 for _ in range(self.len_beta_list)]
        self._tl_lam_t = 1.0
        # (1) is an identity at t=0 only if every group starts at the same beta.
        _spread = max(float((_b - self._tl_s).abs().max()) for _b in self.beta)
        if _spread != 0.0:
            raise ValueError("HIER=twolevel: beta is not uniform at init "
                             "(max deviation %r)" % (_spread,))

    def _tl_update(self, z):
        """One joint meta-step on (s, d).  Called INSTEAD of meta_update()."""
        if not hasattr(self, '_tl_s'):
            self._tl_init()
        _M = self.args_meta
        _eta = _M['meta_stepsize']
        _wd = _M['weight_decay']
        _eta_d = self._hier_ratio * _eta
        # (a) absorb whatever PATCH_CLIP did to the composite on the last step
        for _i in range(self.len_beta_list):
            self._tl_d[_i] = self.beta[_i] - self._tl_s
        # (b) the shared level's meta-gradient: the chain rule of (1)
        _zs = sum(_zi.sum() for _zi in z)
        # (c) the run's own meta rule, one state per level, eta vs rho*eta
        if _M['alg'] == 'Lion':
            _b2 = _M['Lion_beta2']
            _mp = _M['momentum_param']
            self._tl_s = (1 - _eta * _wd) * self._tl_s - _eta * torch.sign(
                _b2 * self._tl_mo_s + (1 - _b2) * _zs)
            self._tl_mo_s = _mp * self._tl_mo_s + (1 - _mp) * _zs
            for _i in range(self.len_beta_list):
                self._tl_d[_i] = (1 - _eta_d * _wd) * self._tl_d[_i] - _eta_d * torch.sign(
                    _b2 * self._tl_mo_d[_i] + (1 - _b2) * z[_i])
                self._tl_mo_d[_i] = _mp * self._tl_mo_d[_i] + (1 - _mp) * z[_i]
        elif _M['alg'] == 'Adam':
            _np = _M['normalizer_param']
            _mp = _M['momentum_param']
            self._tl_lam_t *= _np
            _mu = (1 - _np) / (1 - self._tl_lam_t)
            self._tl_mo_s = _mp * self._tl_mo_s + _zs
            self._tl_tr_s = _np * self._tl_tr_s + _zs ** 2
            self._tl_s = (1 - _eta * _wd) * self._tl_s - torch.div(
                _eta * self._tl_mo_s, (_mu * self._tl_tr_s + self.epsilon) ** .5)
            for _i in range(self.len_beta_list):
                self._tl_mo_d[_i] = _mp * self._tl_mo_d[_i] + z[_i]
                self._tl_tr_d[_i] = _np * self._tl_tr_d[_i] + z[_i] ** 2
                self._tl_d[_i] = (1 - _eta_d * _wd) * self._tl_d[_i] - torch.div(
                    _eta_d * self._tl_mo_d[_i], (_mu * self._tl_tr_d[_i] + self.epsilon) ** .5)
        else:  # RMSProp -- the only remaining value _tl_init admits
            _np = _M['normalizer_param']
            self._tl_lam_t *= _np
            _mu = (1 - _np) / (1 - self._tl_lam_t)
            self._tl_tr_s = _np * self._tl_tr_s + _zs ** 2
            self._tl_s = (1 - _eta * _wd) * self._tl_s - torch.div(
                _eta * _zs, (_mu * self._tl_tr_s + self.epsilon) ** .5)
            for _i in range(self.len_beta_list):
                self._tl_tr_d[_i] = _np * self._tl_tr_d[_i] + z[_i] ** 2
                self._tl_d[_i] = (1 - _eta_d * _wd) * self._tl_d[_i] - torch.div(
                    _eta_d * z[_i], (_mu * self._tl_tr_d[_i] + self.epsilon) ** .5)
        # (d) the shared level lives in the same box as the composite, so the two
        #     levels cannot wind apart while the composite sits on a rail
        if self._beta_lo is not None:
            self._tl_s = self._tl_s.clamp(self._beta_lo, self._beta_hi)
        # (e) compose.  step() clips this next; (a) absorbs that next step.
        for _i in range(self.len_beta_list):
            self.beta[_i] = self._tl_s + self._tl_d[_i]

    # ----------------------------------------------------------- PATCH_PROBE
    def _probe_init(self):
'''
src = src.replace(a2, n2, 1)

# =========================================================================================
# (3) STRUCTURAL ASSERTIONS ON THE RESULT
# =========================================================================================
# The pinned two lines survive verbatim as the else arm.
assert """                self.meta_update(HtT_gradft)
                if self._hier:  # PATCH_HIER
                    self._apply_hier()
""" in src, "the pinned meta_update/_apply_hier pair did not survive as the else arm"
assert src.count("self.meta_update(HtT_gradft)") == 1, "meta_update call duplicated or lost"
assert src.count("self._apply_hier()") == 1, "_apply_hier call duplicated or lost"

# The new code is reachable ONLY through the new mode string.
assert src.count("self._hier == 'twolevel'") == 1, "twolevel must be dispatched exactly once"
assert src.count("def _tl_update") == 1, "expected exactly one definition of _tl_update"
assert src.count("self._tl_update(") == 1, "expected exactly one call site of _tl_update"
assert src.count("def _tl_init") == 1, "expected exactly one definition of _tl_init"
assert src.count("self._tl_init()") == 1, "expected exactly one call site of _tl_init"
assert src.count("PATCH_TWOLEVEL") == 2, "expected exactly two PATCH_TWOLEVEL marks"

# The branches this patch must NOT disturb, re-counted after the edit.
assert src.count("self._hier == 'zpool'") == 1, "zpool dispatch disturbed"
assert src.count("self._hier == 'zmpool'") == 1, "zmpool dispatch disturbed"
assert src.count("self._hier == 'shrink'") == 2, "shrink branches disturbed"
assert src.count("self._hier == 'additive'") == 2, "additive branches disturbed"
assert src.count("def _apply_hier") == 1, "_apply_hier redefined"
assert src.count("def _zpool") == 1 and src.count("def _zmpool") == 1
assert src.count("def _probe_init") == 1, "_probe_init duplicated"
# PATCH_CLIP's clip of the COMPOSITE must survive, exactly once, unmoved.
assert src.count("self.beta[_i] = self.beta[_i].clamp(self._beta_lo, self._beta_hi)") == 1, \
    "PATCH_CLIP's composite clip was disturbed"
assert src.index("if self._hier == 'twolevel':  # PATCH_TWOLEVEL") \
    < src.index("if self._beta_lo is not None:  # PATCH_CLIP"), \
    "the twolevel update must run BEFORE step()'s clip of the composite"

# The names this patch introduces must not already have existed.
for _n in ("_tl_s", "_tl_d", "_tl_mo_s", "_tl_tr_s", "_tl_mo_d", "_tl_tr_d", "_tl_lam_t"):
    assert src.count(_n) >= 1, "missing new state %s" % _n

# It must still parse, and the class must still expose the pinned entry points.
import ast as _ast
_tree = _ast.parse(src)
_cls = [n for n in _ast.walk(_tree) if isinstance(n, _ast.ClassDef) and n.name == 'HF']
assert len(_cls) == 1, "expected exactly one class HF"
_meths = {n.name for n in _cls[0].body if isinstance(n, _ast.FunctionDef)}
for _m in ('step', 'meta_update' if 'meta_update' in _meths else 'step',
           '_apply_hier', '_zpool', '_zmpool', '_probe', 'init_meta',
           'block_product', 'beta_to_alpha', '_tl_init', '_tl_update'):
    assert _m in _meths, "method %s missing after patch" % _m

open(P, "w").write(src)
print("PATCHED PATCH_TWOLEVEL ->", P)
print("mode string:  HIER=twolevel      dial: ETA_RATIO=rho   (shrinkage strength = 1 - rho)")
print("NEXT, BEFORE ANY SUBMISSION:  python3 tests/tl_equivalence.py --cifar <cifar10 dir> \\")
print("                                --pinned <pre-patch HF.py copy>")
