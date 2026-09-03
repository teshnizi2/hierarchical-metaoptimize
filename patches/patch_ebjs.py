"""G16 -- PATCH_EBJS.  Empirical-Bayes / James-Stein shrinkage with NO DIAL.

WHY THIS EXISTS
---------------
Every hierarchical operator in the tree so far carries a hand-set strength:
`shrink` has LAM, `additive`/`zpool`/`zmpool` have ETA_RATIO.  The r-curve in
the primary cell (ResNet18/CIFAR10/layerwise/alpha0=1e-6/ms=1e-3/100ep, re-derived
from results/all_runs.csv at write time) peaks at r=0.06 and the peak had to be
FOUND by sweeping ten rungs.  A shrinkage strength that has to be tuned per
setting is not a method, it is a hyperparameter.

G16 removes the dial.  The retained-deviation fraction is ESTIMATED at every
meta-step from the data, by the positive-part James-Stein rule.

THE ESTIMATOR, EXACTLY
----------------------
Let x in R^m be the per-group statistic at this meta-step (see the two modes
below).  Model it as a one-way normal random-effects model

        x_b = mu + u_b + e_b ,   u_b ~ N(0, tau^2) ,   e_b ~ N(0, s2)

with u (real between-group signal) independent of e (observation noise).  The
posterior mean of mu + u_b given x is

        E[mu + u_b | x] = xbar + (tau^2 / (tau^2 + s2)) * (x_b - xbar) ,

i.e. keep a fraction r = tau^2/(tau^2+s2) of each group's deviation from the
mean.  The empirical-Bayes / positive-part James-Stein estimate of that fraction,
with mu estimated by xbar (hence m-3 rather than m-2 degrees of freedom), is

        SS  = sum_b (x_b - xbar)^2
        c   = min(1, (m-3) * s2 / SS)          # the SHRUNK fraction
        rhat = 1 - c                            # the RETAINED fraction

so rhat = 0 is full pooling and rhat = 1 is no pooling.  Nothing is tuned:
rhat is a function of the data at that step.

WHERE s2 COMES FROM, AND WHY NOT FROM GROUP SIZE
------------------------------------------------
The obvious noise model -- per-weight meta-gradients are near-independent, so a
group of n_b weights has noise ~ 1/n_b -- is REFUTED in this project's own
measurement (FINDINGS 8b: 53.1% of 11,173,962 per-weight meta-gradients agree on
sign against 50.0000 +- 0.0015% under independence; predicted drift slope -0.500,
measured -0.113).  So s2 must NOT be built from n_b.

It is built from the TEMPORAL fluctuation of each group's own statistic instead:

        v_b <- rho * v_b + (1-rho) * (x_b - mhat_b)^2      # EWMA, pre-update mean
        mhat_b <- rho * mhat_b + (1-rho) * x_b
        s2 = (1/m) sum_b v_b / (1 - rho^t)                 # pooled, bias-corrected

ASSUMPTIONS, STATED SO A REFEREE CAN ATTACK THEM:
  A1  the per-group signal mu+u_b is slowly varying relative to the EWMA horizon,
      so fluctuation about the EWMA mean is noise rather than signal;
  A2  the noise is homoscedastic across groups (s2 pooled, one number);
  A3  normality, for the James-Stein form itself;
  A4  the m groups are exchangeable a priori.
A1 is the weak one: drift in x_b inflates v_b, inflates s2, and OVER-shrinks.
The batch logs rhat so this is measurable rather than assumed.

rho DEFAULTS TO THE META-OPTIMISER'S OWN MOMENTUM CONSTANT (args_meta
['momentum_param'], 0.99 in the primary cell), so the patch introduces no new
hyperparameter at all.  EB_RHO overrides it for robustness checks only.

TWO MODES (distinct HIER strings; G1's block, if present, is untouched)
----------------------------------------------------------------------
  HIER=ebjs   x = the realised beta INCREMENT d_b = beta_b(t) - beta_b(t-1).
              beta_b(t) := beta_b(t-1) + dbar + rhat * (d_b - dbar)
              This is EXACTLY the existing `additive` operator with r replaced by
              rhat, so the archived ten-rung additive r-curve is its reference
              and rhat is directly comparable to the measured argmax r=0.06.
              PRIMARY.

  HIER=ebjz   x = the per-group meta-gradient z_b, shrunk BEFORE the meta update:
              z_b := zbar + rhat * (z_b - zbar)
              This is EXACTLY `zmpool` with r replaced by rhat.  SECONDARY.

WHY NOT SHRINK THE BETA LEVELS DIRECTLY.  Applying a James-Stein contraction to
the beta LEVELS every step is unstable toward collapse: each application scales
the spread by (1-c), so SS falls, so c = min(1,(m-3)s2/SS) rises, so the next
contraction is stronger -- a positive feedback whose only fixed point is SS=0,
i.e. the scalar arm.  It is also the saturating time-constant operator this
cycle exists to replace (LAM=1e-3 has half-life ln2/-ln(1-1e-3) = 692.8 steps
against 50,000 steps per run, i.e. 72.2 half-lives).  Both modes above act on an
INCREMENT or on a per-step meta-gradient, never on an accumulated level, so
neither saturates and neither collapses.

NO-OP WHEN DISABLED.  Every change below is (a) an unconditional assignment of a
NEW attribute in __init__, or (b) a NEW `elif` arm keyed on a HIER string that
did not previously exist, or (c) a NEW method never called from an existing path.
No existing statement is edited.  Proven, not asserted, by
analysis/cG16_noop_equiv.py, which loads the pre-patch and post-patch files as
two modules in ONE process and compares SHA-256 hashes of the full optimiser
state after fixed-seed step sequences, across every pre-existing HIER setting.

USAGE:  HF_PATH=<path to HF.py> python3 patches/patch_ebjs.py
"""
import sys, os

P = os.environ.get("HF_PATH") or (
    "/home/s5014158/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize"
    "/cifar10/Optimizers/HF.py")
s = open(P).read()
if "PATCH_EBJS" in s:
    print("ALREADY")
    sys.exit(0)
assert "PATCH_HIER" in s, "PATCH_HIER must already be present"
assert "PATCH_ZMPOOL" in s, "PATCH_ZMPOOL must already be present"
orig = s

# ---------------------------------------------------------------- 1) __init__
a1 = "        self._beta_prev = None\n"
assert s.count(a1) == 1, "init anchor %d" % s.count(a1)
s = s.replace(a1, a1 + """        # PATCH_EBJS: empirical-Bayes / James-Stein shrinkage.  NO DIAL -- the
        # retained-deviation fraction is estimated from the data each meta-step.
        # rho defaults to the meta-optimiser's OWN momentum constant, so nothing
        # new is introduced; EB_RHO overrides it for robustness checks only.
        self._ebjs_rho_env = _os.environ.get('EB_RHO', '')
        self._ebjs_log = int(_os.environ.get('EB_LOG', '0') or 0)
        self._ebjs_mean = None
        self._ebjs_var = None
        self._ebjs_t = 0
        self._ebjs_racc = None
        self._ebjs_rn = 0
""", 1)

# --------------------------------------------------------------- 2) dispatch
a2 = """            elif self._hier == 'zmpool':  # PATCH_ZMPOOL
                HtT_gradft = self._zmpool(HtT_gradft)"""
assert s.count(a2) == 1, "dispatch anchor %d" % s.count(a2)
s = s.replace(a2, a2 + """
            elif self._hier == 'ebjz':  # PATCH_EBJS
                HtT_gradft = self._ebjs_pool_z(HtT_gradft)""", 1)

# ---------------------------------------------------- 3) the estimator itself
a3 = "    # ------------------------------------------------------------ PATCH_HIER"
assert s.count(a3) == 1, "method anchor %d" % s.count(a3)
s = s.replace(a3, '''    # ------------------------------------------------------------ PATCH_EBJS
    def _ebjs_rho(self):
        """EWMA constant of the noise estimator.  Defaults to the meta-optimiser's
        own momentum constant so that PATCH_EBJS adds no new hyperparameter."""
        if self._ebjs_rho_env:
            return float(self._ebjs_rho_env)
        try:
            return float(self.args_meta['momentum_param'])
        except Exception:
            return 0.99

    def _ebjs_flat(self, xs):
        """Concatenate a per-tensor list into one flat vector of group statistics."""
        if len(xs) == 1:
            return xs[0].reshape(-1)
        return torch.cat([x.reshape(-1) for x in xs])

    def _ebjs_ratio(self, x):
        """Positive-part James-Stein RETAINED-deviation fraction for x in R^m.

            SS   = sum_b (x_b - xbar)^2
            s2   = pooled EWMA temporal variance of x about its own EWMA mean
            c    = min(1, (m-3) * s2 / SS)
            rhat = 1 - c

        Returned as a 0-dim tensor so no host sync is forced on the hot path.
        m < 4 has no positive-part JS form; rhat = 1 (identity) is returned."""
        m = x.numel()
        if m < 4:
            return torch.ones((), dtype=x.dtype, device=x.device)
        rho = self._ebjs_rho()
        if self._ebjs_mean is None or self._ebjs_mean.numel() != m:
            self._ebjs_mean = x.detach().clone()
            self._ebjs_var = torch.zeros_like(x)
            self._ebjs_t = 0
        d = x - self._ebjs_mean
        self._ebjs_var = rho * self._ebjs_var + (1.0 - rho) * d * d
        self._ebjs_mean = rho * self._ebjs_mean + (1.0 - rho) * x
        self._ebjs_t += 1
        bc = 1.0 - rho ** self._ebjs_t                 # EWMA bias correction
        s2 = (self._ebjs_var.sum() / m) / bc
        xb = x.mean()
        ss = ((x - xb) ** 2).sum()
        c = ((m - 3) * s2 / (ss + self.epsilon)).clamp(0.0, 1.0)
        r = 1.0 - c
        if self._ebjs_racc is None:
            self._ebjs_racc = torch.zeros((), dtype=r.dtype, device=r.device)
        self._ebjs_racc = self._ebjs_racc + r
        self._ebjs_rn += 1
        if self._ebjs_log and (self._ebjs_rn % self._ebjs_log == 0):
            print("EBJS: t=%d m=%d rho=%.6g s2=%.6e ss=%.6e r=%.6f rbar=%.6f"
                  % (self._ebjs_rn, m, rho, float(s2), float(ss), float(r),
                     float(self._ebjs_racc) / self._ebjs_rn), flush=True)
        return r

    def _ebjs_pool_z(self, z):
        """HIER=ebjz: zmpool with r estimated.  z_b := zbar + rhat*(z_b - zbar)."""
        if self.stepsize_type == 'scalar':
            return z
        if self.stepsize_type in ('layerwise', 'blockwise'):
            x = z[0]
            r = self._ebjs_ratio(x)
            mu = x.mean()
            return [mu + r * (x - mu)]
        x = self._ebjs_flat(z)
        r = self._ebjs_ratio(x)
        mu = x.mean()
        return [mu + r * (zz - mu) for zz in z]

''' + a3, 1)

# ------------------------------------------------- 4) the beta-increment mode
a4 = """            elif self._hier == 'additive':
                if self._beta_prev is not None:
                    d = b - self._beta_prev                 # realised update
                    dm = d.mean()                            # shared component
                    self.beta[0] = self._beta_prev + dm + self._hier_ratio * (d - dm)
                self._beta_prev = self.beta[0].clone()"""
assert s.count(a4) == 1, "layerwise additive anchor %d" % s.count(a4)
s = s.replace(a4, a4 + """
            elif self._hier == 'ebjs':  # PATCH_EBJS: additive with r ESTIMATED
                if self._beta_prev is not None:
                    d = b - self._beta_prev
                    dm = d.mean()
                    r = self._ebjs_ratio(d)
                    self.beta[0] = self._beta_prev + dm + r * (d - dm)
                self._beta_prev = self.beta[0].clone()""", 1)

a5 = """            elif self._hier == 'additive':
                if self._beta_prev is not None:
                    ds = [self.beta[i] - self._beta_prev[i] for i in range(self.len_beta_list)]
                    tot = sum(float(d.sum()) for d in ds)
                    cnt = sum(d.numel() for d in ds)
                    dm = tot / max(cnt, 1)
                    for i in range(self.len_beta_list):
                        self.beta[i] = self._beta_prev[i] + dm + self._hier_ratio * (ds[i] - dm)
                self._beta_prev = [bb.clone() for bb in self.beta]"""
assert s.count(a5) == 1, "list additive anchor %d" % s.count(a5)
s = s.replace(a5, a5 + """
            elif self._hier == 'ebjs':  # PATCH_EBJS: additive with r ESTIMATED
                if self._beta_prev is not None:
                    ds = [self.beta[i] - self._beta_prev[i] for i in range(self.len_beta_list)]
                    x = self._ebjs_flat(ds)
                    dm = x.mean()
                    r = self._ebjs_ratio(x)
                    for i in range(self.len_beta_list):
                        self.beta[i] = self._beta_prev[i] + dm + r * (ds[i] - dm)
                self._beta_prev = [bb.clone() for bb in self.beta]""", 1)

open(P + ".bak_ebjs", "w").write(orig)
open(P, "w").write(s)
print("PATCH_EBJS_OK")
