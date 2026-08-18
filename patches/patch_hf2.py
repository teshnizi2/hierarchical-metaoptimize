"""Patch cifar10/Optimizers/HF.py: implement layerwise/nodewise/weightwise granularities.

DESIGN RULE: existing 'scalar' and 'blockwise' paths are NOT modified, so Gate 0
must reproduce bit-for-bit. Uses single-line anchors (whitespace-robust).
"""
import sys

P = "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10/Optimizers/HF.py"
src = open(P).read()
orig = src

if "PATCH_GRANULARITY" in src:
    print("ALREADY_PATCHED"); sys.exit(0)


def after(anchor, addition, s):
    """Insert `addition` immediately after the single line `anchor`."""
    assert s.count(anchor) == 1, f"anchor not unique/found ({s.count(anchor)}): {anchor[:70]}"
    return s.replace(anchor, anchor + addition, 1)


def before(anchor, addition, s):
    assert s.count(anchor) == 1, f"anchor not unique/found ({s.count(anchor)}): {anchor[:70]}"
    return s.replace(anchor, addition + anchor, 1)


# 1. capture device
src = after("        self.num_layers = len([0 for _ in  net.parameters()])",
            "\n        self._device = next(net.parameters()).device  # PATCH_GRANULARITY", src)

# 2. beta_to_alpha: new granularity branches
src = after(
    "            return [alpha_groupwise[self.map_layers_to_blocks[i]] for i in range(self.num_layers)]",
    """
        # --- PATCH_GRANULARITY: GPU-resident, no host syncs ---
        if self.stepsize_type == 'layerwise':
            alpha_vec = torch.exp(beta[0])
            self.alpha_for_printing = alpha_vec
            return [alpha_vec[i] for i in range(self.num_layers)]
        if self.stepsize_type == 'weightwise':
            alphas = [torch.exp(b) for b in beta]
            self.alpha_for_printing = alphas
            return alphas
        if self.stepsize_type == 'nodewise':
            alphas = [torch.exp(b).view(v) for b, v in zip(beta, self.node_view)]
            self.alpha_for_printing = alphas
            return alphas""", src)

# 3. block_product: z must match self.beta structure
src = after(
    "            return [torch.tensor([sum([(u[i]*v[i]).sum() for i in group_indices]) for group_indices in self.param_groups_indices])]",
    """
        # --- PATCH_GRANULARITY ---
        if self.stepsize_type == 'layerwise':
            return [torch.stack([(u[i]*v[i]).sum() for i in range(self.num_layers)])]
        if self.stepsize_type == 'weightwise':
            return [u[i]*v[i] for i in range(self.num_layers)]
        if self.stepsize_type == 'nodewise':
            return [(u[i]*v[i]).reshape(u[i].shape[0], -1).sum(dim=1) for i in range(self.num_layers)]""", src)

# 4. init_meta: the three missing branches (continue the existing if/elif chain)
src = after(
    "            self.beta = [torch.log(torch.tensor(alpha0)) * torch.ones(len(stepsize_groups))]",
    """
        # --- PATCH_GRANULARITY: the three granularities that were never implemented ---
        elif self.stepsize_type == 'layerwise':
            _lb = torch.log(torch.tensor(alpha0, dtype=torch.float32, device=self._device))
            self.beta = [_lb * torch.ones(self.num_layers, dtype=torch.float32, device=self._device)]
        elif self.stepsize_type == 'nodewise':
            _lb = torch.log(torch.tensor(alpha0, dtype=torch.float32, device=self._device))
            self.beta = [_lb * torch.ones(int(p_size[0]), dtype=torch.float32, device=self._device)
                         for (_n, p_size) in net_param_names_and_size]
            self.node_view = [(-1,) + (1,) * (len(p_size) - 1) for (_n, p_size) in net_param_names_and_size]
        elif self.stepsize_type == 'weightwise':
            _lb = torch.log(torch.tensor(alpha0, dtype=torch.float32, device=self._device))
            self.beta = [_lb * torch.ones(tuple(p_size), dtype=torch.float32, device=self._device)
                         for (_n, p_size) in net_param_names_and_size]""", src)

# 5. guard + record block sizes n_b (needed for the H1 SNR-vs-sqrt(n_b) plot)
src = before(
    "        self.len_beta_list = len(self.beta)",
    """        # --- PATCH_GRANULARITY ---
        if not hasattr(self, 'beta'):
            raise ValueError('unsupported stepsize_groups: %r' % (stepsize_groups,))
        self.param_numels = [int(np.prod(list(p_size))) for (_n, p_size) in net_param_names_and_size]
""", src)

open(P + ".bak_gran", "w").write(orig)
open(P, "w").write(src)
print("PATCH_A_OK (backup HF.py.bak_gran); +%d lines" % (src.count("\n") - orig.count("\n")))
