import numpy as np
import torch
import time

class HF():
    # only for scalar stepsize
    def __init__(self, net, stepsize_groups, alpha0, args_base, args_meta, gamma, writer=None):
        '''
        stepsize_groups: in ['scalar', 'resnet18_blocks', 'resnet50_blocks', or [[name_layer1, name_layer2,...], [name_layer_i,...],...], or [int_1, int_2,...] where int_i=size_of_group_i ]
        args_base: a dictionary with attributes = required_attributes_base (see below)
        args_meta: a dictionary with attributes = required_attributes_meta (see below)
        alpha0 = 1e-6
        gamma = 1 or .99999
        '''
        
        self.args_base = args_base
        self.args_meta = args_meta
        self.gamma = gamma
        self.writer = writer
        self.num_layers = len([0 for _ in  net.parameters()])
        self._device = next(net.parameters()).device  # PATCH_GRANULARITY
        import os as _os  # PATCH_CLIP: SwiftTD/IDBD-style bounds on log step size
        self._hier = _os.environ.get('HIER','')            # PATCH_HIER
        self._hier_lam = float(_os.environ.get('LAM','0') or 0)
        self._hier_ratio = float(_os.environ.get('ETA_RATIO','1') or 1)
        self._beta_prev = None
        _bc = _os.environ.get('BETA_CLIP','')
        if _bc:
            lo,hi = _bc.split(':')
            self._beta_lo, self._beta_hi = float(lo), float(hi)
        else:
            self._beta_lo = self._beta_hi = None
        
        # Base alg
        if self.args_base['alg'] == 'SGD':
            required_attributes_base = ['weight_decay'] 
            self.base_update = self.SGD_base_update
        elif self.args_base['alg'] == 'SGDm':
            required_attributes_base = ['weight_decay', 'momentum_param']
            self.base_update = self.SGDm_base_update 
        elif self.args_base['alg'] == 'RMSProp':
            required_attributes_base = ['normalizer_param', 'weight_decay'] 
            self.base_update = self.RMSProp_base_update
        elif self.args_base['alg'] == 'AdamW':
            required_attributes_base = ['normalizer_param', 'momentum_param', 'weight_decay'] 
            self.base_update = self.AdamW_base_update
        elif self.args_base['alg'] == 'Lion':
            required_attributes_base = ['momentum_param', 'Lion_beta2', 'weight_decay']
            self.base_update =self.Lion_base_update

        # Meta alg
        if self.args_meta['alg'] == 'fixed':
            required_attributes_meta = []
            self.meta_update = self.no_meta_update
        elif self.args_meta['alg'] == 'RMSProp':
            required_attributes_meta = ['meta_stepsize', 'normalizer_param', 'weight_decay']
            self.meta_update = self.RMSProp_meta_update
        elif self.args_meta['alg'] == 'Adam':
            required_attributes_meta = ['meta_stepsize', 'normalizer_param', 'momentum_param', 'weight_decay']
            self.meta_update = self.Adam_meta_update
        elif self.args_meta['alg'] == 'Lion':
            required_attributes_meta = ['meta_stepsize', 'momentum_param', 'Lion_beta2', 'weight_decay']
            self.meta_update = self.Lion_meta_update

        self.check_required_attributes(args_base, args_meta, required_attributes_base, required_attributes_meta)
        self.init_base()
        self.init_meta(stepsize_groups, net_param_names_and_size=[(name,p.data.size()) for name,p in net.named_parameters()], alpha0=alpha0)
        
        
        self.h_condenced = [torch.zeros_like(p) for p in net.parameters()]
        self.epsilon = 1e-10
        self.counter = -1
        

    
    def step(self, net, loss):
        net.zero_grad()
        g = torch.autograd.grad(loss, net.parameters(), create_graph=False)

        with torch.no_grad():
            self.alpha = self.beta_to_alpha(self.beta)
            HtT_gradft = self.block_product(self.h_condenced, g)
            
            self.base_update(net,g)
            self.meta_update(HtT_gradft)
            if self._hier:  # PATCH_HIER
                self._apply_hier()
            if self._beta_lo is not None:  # PATCH_CLIP
                for _i in range(self.len_beta_list):
                    self.beta[_i] = self.beta[_i].clamp(self._beta_lo, self._beta_hi)
            self._probe(HtT_gradft)  # PATCH_PROBE
        
        
        ##---------------------------
        # plotting stepsizes
        self.counter+=1
        if self.counter%100==0 and True:
            if self.stepsize_type == 'scalar':
                self.writer.add_scalar("Optimizer_scalar/alpha_scalar", np.exp(self.beta[0].item()), self.counter)
                self.writer.add_scalar("Optimizer_scalar/beta_scalar", self.beta[0].item(), self.counter)
            elif self.stepsize_type == 'blockwise':
                for i in range(self.num_blocks):
                    self.writer.add_scalar("Optimizer_blockwise/alpha_block"+str(i), np.exp(self.beta[0][i].item()), self.counter)
                    self.writer.add_scalar("Optimizer_blockwise/beta_block"+str(i), self.beta[0][i].item(), self.counter)
            
            #self.writer.add_scalars("Optimizer/trace_layerwise", {'block_'+str(i): self.trace_meta[i].item() for i in range(self.num_groups)}, self.counter)
    

    #####---------------------------------
    # Functions:
    def beta_to_alpha(self, beta):
        if self.stepsize_type in 'scalar':
            self.alpha_for_printing = [np.exp(self.beta[0].cpu().numpy())]
            return [np.exp(beta[0].cpu().numpy()) for _ in range(self.num_layers)]
        if self.stepsize_type in 'blockwise':
            self.alpha_for_printing = np.exp(self.beta[0]).tolist()
            alpha_groupwise = np.exp(beta[0])
            return [alpha_groupwise[self.map_layers_to_blocks[i]] for i in range(self.num_layers)]
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
            return alphas
        
    def block_product(self, u, v):
        if self.stepsize_type == 'scalar':
            return [sum([(u_*v_).sum() for u_,v_ in zip(u,v)])]
        if self.stepsize_type == 'blockwise':
            return [torch.tensor([sum([(u[i]*v[i]).sum() for i in group_indices]) for group_indices in self.param_groups_indices])]
        # --- PATCH_GRANULARITY ---
        if self.stepsize_type == 'layerwise':
            return [torch.stack([(u[i]*v[i]).sum() for i in range(self.num_layers)])]
        if self.stepsize_type == 'weightwise':
            return [u[i]*v[i] for i in range(self.num_layers)]
        if self.stepsize_type == 'nodewise':
            return [(u[i]*v[i]).reshape(u[i].shape[0], -1).sum(dim=1) for i in range(self.num_layers)]
        
    
    def check_required_attributes(self, args_base, args_meta, required_attributes_base, required_attributes_meta):
        required_attributes_base.append('alg')
        required_attributes_meta.append('alg')
        if set(required_attributes_base)-set(args_base):
            print('\nattributes', set(required_attributes_base)-set(args_base), 'are missing from args_base\n')
            0/0
        if set(required_attributes_meta)-set(args_meta):
            print('\nattributes', set(required_attributes_meta)-set(args_meta), 'are missing from args_meta\n')
            0/0
        if set(args_base)-set(required_attributes_base):
            print('\nargs_base includes unnecessary attributes', set(args_base)-set(required_attributes_base),'\n')
        if set(args_meta)-set(required_attributes_meta):
            print('\nargs_meta includes unnecessary attributes', set(args_meta)-set(required_attributes_meta),'\n')
    

    def polish_the_stepsize_groups(self, stepsize_groups,net_param_names_and_size):
        if stepsize_groups == 'resnet18_blocks':
            stepsize_groups = [3,12,15,15,15,2]
        elif stepsize_groups == 'resnet50_blocks':
            stepsize_groups = [3,30,39,57,30,2]
        elif stepsize_groups[0]=='[' and stepsize_groups[-1]==']':
            stepsize_groups = [int(x) for x in stepsize_groups[1:-1].split(',')]
        if not isinstance(stepsize_groups, list): 0/0
        if isinstance(stepsize_groups[0], int):
            if not (sum(stepsize_groups)==len(net_param_names_and_size)): 0/0
            temp = []
            start_ind_of_block = 0
            for block_len in stepsize_groups:
                temp.append([name for (name,_) in net_param_names_and_size[start_ind_of_block:start_ind_of_block+block_len]])
                start_ind_of_block += block_len
            stepsize_groups = temp
        return stepsize_groups

###################################################
    # Initialization
    def init_base(self):
        self.trace_base = [0.0 for _ in range(self.num_layers)]
        self.momentum_base = [0.0 for _ in  range(self.num_layers)]
        self.lambda_base_t = 1.0

    def init_meta(self, stepsize_groups, net_param_names_and_size, alpha0):
        self.stepsize_type = stepsize_groups if stepsize_groups in ['scalar', 'layerwise', 'nodewise', 'weightwise'] else 'blockwise'
        if self.stepsize_type == 'blockwise': stepsize_groups = self.polish_the_stepsize_groups(stepsize_groups,net_param_names_and_size)

        if self.stepsize_type == 'scalar':
            self.beta = [torch.log(torch.tensor(alpha0, dtype=torch.float32, requires_grad=False))]
        elif self.stepsize_type == 'blockwise':
            self.num_blocks = len(stepsize_groups)
            self.param_groups_indices = [[index for (name,_),index in  zip(net_param_names_and_size,range(self.num_layers)) if name in group] for group in  stepsize_groups]
            self.map_layers_to_blocks = [[name in group for group in stepsize_groups].index(True) for (name,_) in  net_param_names_and_size]
            self.beta = [torch.log(torch.tensor(alpha0)) * torch.ones(len(stepsize_groups))]
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
                         for (_n, p_size) in net_param_names_and_size]
        
        # --- PATCH_GRANULARITY ---
        if not hasattr(self, 'beta'):
            raise ValueError('unsupported stepsize_groups: %r' % (stepsize_groups,))
        self.param_numels = [int(np.prod(list(p_size))) for (_n, p_size) in net_param_names_and_size]
        self.len_beta_list = len(self.beta)
        
        self.trace_meta = [0.0 for _ in  range(self.len_beta_list)]
        self.momentum_meta = [0.0 for _ in  range(self.len_beta_list)]
        self.lambda_meta_t = 1.0





    # ------------------------------------------------------------ PATCH_HIER
    def _apply_hier(self):
        """Partial pooling of the log step sizes across groups."""
        if self.stepsize_type == 'scalar':
            return
        if self.stepsize_type in ('layerwise', 'blockwise'):
            b = self.beta[0]
            if self._hier == 'shrink':
                self.beta[0] = b - self._hier_lam * (b - b.mean())
            elif self._hier == 'additive':
                if self._beta_prev is not None:
                    d = b - self._beta_prev                 # realised update
                    dm = d.mean()                            # shared component
                    self.beta[0] = self._beta_prev + dm + self._hier_ratio * (d - dm)
                self._beta_prev = self.beta[0].clone()
        else:  # weightwise / nodewise: pool across the whole network
            if self._hier == 'shrink':
                tot = sum(float(bb.sum()) for bb in self.beta)
                cnt = sum(bb.numel() for bb in self.beta)
                gm = tot / max(cnt, 1)
                for i in range(self.len_beta_list):
                    self.beta[i] = self.beta[i] - self._hier_lam * (self.beta[i] - gm)
            elif self._hier == 'additive':
                if self._beta_prev is not None:
                    ds = [self.beta[i] - self._beta_prev[i] for i in range(self.len_beta_list)]
                    tot = sum(float(d.sum()) for d in ds)
                    cnt = sum(d.numel() for d in ds)
                    dm = tot / max(cnt, 1)
                    for i in range(self.len_beta_list):
                        self.beta[i] = self._beta_prev[i] + dm + self._hier_ratio * (ds[i] - dm)
                self._beta_prev = [bb.clone() for bb in self.beta]

    # ----------------------------------------------------------- PATCH_PROBE
    def _probe_init(self):
        import os
        self._probe_every = int(os.environ.get('PROBE', '0'))
        self._probe_dir = os.environ.get('PROBE_DIR', '')
        self._z_n = 0
        self._z_sum = None
        self._z_sqsum = None
        if self._probe_every and self._probe_dir:
            os.makedirs(self._probe_dir, exist_ok=True)
            # group sizes n_b: the x-axis of the H1 SNR regression
            if self.stepsize_type == 'layerwise':
                nb = self.param_numels
            elif self.stepsize_type == 'scalar':
                nb = [sum(self.param_numels)]
            elif self.stepsize_type == 'blockwise':
                nb = [sum(self.param_numels[i] for i in gi) for gi in self.param_groups_indices]
            else:
                nb = self.param_numels
            with open(os.path.join(self._probe_dir, 'block_sizes.json'), 'w') as fh:
                import json; json.dump({'stepsize_type': self.stepsize_type, 'n_b': nb}, fh)

    def _probe(self, z):
        if not hasattr(self, '_probe_every'):
            self._probe_init()
        if not self._probe_every:
            return
        # flatten z to one vector of per-group scalars (weightwise/nodewise: per-tensor means)
        if self.stepsize_type in ('scalar', 'layerwise', 'blockwise'):
            zv = z[0].detach().reshape(-1).float()
        else:
            zv = torch.stack([zi.detach().float().mean() for zi in z])
        if self._z_sum is None:
            self._z_sum = torch.zeros_like(zv)
            self._z_sqsum = torch.zeros_like(zv)
        self._z_sum += zv
        self._z_sqsum += zv * zv
        self._z_n += 1
        if self.counter % self._probe_every:
            return
        import json, os
        mean = self._z_sum / max(self._z_n, 1)
        var = (self._z_sqsum / max(self._z_n, 1)) - mean * mean
        std = var.clamp_min(0).sqrt()
        snr = (mean.abs() / (std + 1e-12))
        if self.stepsize_type in ('scalar', 'layerwise', 'blockwise'):
            bv = self.beta[0].detach().reshape(-1).float()
        else:
            bv = torch.stack([b.detach().float().mean() for b in self.beta])
        # --- PATCH_PROBE2: mechanism diagnostics ---
        if self.stepsize_type in ('scalar', 'layerwise', 'blockwise'):
            zall = z[0].detach().reshape(-1).float()
        else:
            zall = torch.cat([zi.detach().float().reshape(-1) for zi in z])
        n_tot = zall.numel()
        try:  # PATCH_CLIP: true per-coordinate extremes (per-tensor means hide these)
            beta_true_min = min(float(bb.min()) for bb in self.beta)
            beta_true_max = max(float(bb.max()) for bb in self.beta)
        except Exception:
            beta_true_min = beta_true_max = float('nan')
        try:
            h_absmax = max(float(hh.abs().max()) for hh in self.h_condenced)
        except Exception:
            h_absmax = -1.0  # PATCH_PROBE3
        frac_neg = (zall < 0).sum().item() / max(n_tot, 1)
        frac_zero = (zall == 0).sum().item() / max(n_tot, 1)
        zm = zall.mean()
        zs = zall.std()
        z_skew = (((zall - zm) / (zs + 1e-30)) ** 3).mean().item() if n_tot > 1 else 0.0
        try:
            mom = self.momentum_meta
            mom_norm = float(sum(float((m * m).sum()) for m in mom if torch.is_tensor(m)) ** 0.5)
        except Exception:
            mom_norm = -1.0
        rec = {'step': int(self.counter),
               'beta': bv.cpu().tolist(),
               'z_mean': mean.cpu().tolist(),
               'z_std': std.cpu().tolist(),
               'snr': snr.cpu().tolist(),
               'frac_neg': frac_neg, 'frac_zero': frac_zero,
               'z_skew': z_skew, 'mom_norm': mom_norm, 'h_absmax': h_absmax, 'beta_true_min': beta_true_min, 'beta_true_max': beta_true_max}
        with open(os.path.join(self._probe_dir, 'probe.jsonl'), 'a') as fh:
            fh.write(json.dumps(rec) + chr(10))
        if self.writer is not None:
            self.writer.add_scalar('Probe/beta_mean', bv.mean().item(), self.counter)
            self.writer.add_scalar('Probe/beta_max', bv.max().item(), self.counter)
            self.writer.add_scalar('Probe/beta_min', bv.min().item(), self.counter)
            self.writer.add_scalar('Probe/snr_median', snr.median().item(), self.counter)
            self.writer.add_scalar('Probe/frac_neg', frac_neg, self.counter)
            self.writer.add_scalar('Probe/frac_zero', frac_zero, self.counter)
            self.writer.add_scalar('Probe/mom_norm', mom_norm, self.counter)

###################################################
###################################################
    # Updates
###################################################

    # SGD
    def SGD_base_update(self,net,g):
        for w, grad, a ,i in zip(net.parameters(), g, self.alpha, range(self.num_layers)):
            delta_w = a * (grad + self.args_base['weight_decay']*w.data)
            w.data = w.data - delta_w
            self.h_condenced[i] = self.gamma*(1-self.args_base['weight_decay']*a)*self.h_condenced[i] - delta_w
    
    def SGDm_base_update(self,net,g):
        #Base update
        for w, grad, a ,i in zip(net.parameters(), g, self.alpha, range(self.num_layers)):
            delta = a * (self.momentum_base[i] + self.args_base['weight_decay']*w.data)
            w.data = w.data - delta
            self.momentum_base[i] = self.args_base['momentum_param']*self.momentum_base[i] + (1 - self.args_base['momentum_param'])*grad
            self.h_condenced[i] = self.gamma*(1-self.args_base['weight_decay']*a)*self.h_condenced[i] - delta
                

        # # updating H
        # for j in range(self.m):
        #     for i in range(self.num_layers): 
        #         self.H[j][i] = self.gamma * self.H[j][i] -self.gamma*self.alpha[i]*self.H[j][i]*self.args_base['weight_decay']  -  self.gamma*self.alpha[i]*self.M_base[j][i]  -  delta_w[i] 
        #         self.M_base[j][i] = self.gamma*self.args_base['momentum_param']*self.M_base[j][i] + self.gamma*self.H[j][i]*(1-self.args_base['momentum_param'])


###################################################
    # RMSProp
    def RMSProp_base_update(self,net,g):
        self.lambda_base_t *= self.args_base['normalizer_param']
        mu_base = (1-self.args_base['normalizer_param'])/(1-self.lambda_base_t)
        self.trace_base = [self.args_base['normalizer_param']*self.trace_base[i] + g[i]**2 for i in range(self.num_layers)]
        for w, grad, a, tr_ ,i in zip(net.parameters(), g, self.alpha, self.trace_base, range(self.num_layers)):
            delta_w = a * (torch.div(grad, (mu_base*tr_+self.epsilon)**.5) + self.args_base['weight_decay']*w.data)
            w.data = w.data - delta_w
            self.h_condenced[i] = self.gamma*(1-self.args_base['weight_decay']*a)*self.h_condenced[i] - delta_w
        
    def RMSProp_meta_update(self,HtT_gradft):
        self.lambda_meta_t *= self.args_meta['normalizer_param']
        mu_meta = (1-self.args_meta['normalizer_param'])/(1-self.lambda_meta_t)
        for i in range(self.len_beta_list):
            self.trace_meta[i] = self.args_meta['normalizer_param'] * self.trace_meta[i] + HtT_gradft[i]**2 
            self.beta[i] = (1-self.args_meta['meta_stepsize']*self.args_meta['weight_decay'])*self.beta[i] - torch.div(self.args_meta['meta_stepsize'] * HtT_gradft[i], (mu_meta*self.trace_meta[i] + self.epsilon)**.5) 
        


###################################################
    # Lion
    def Lion_base_update(self,net,g):
        delta_w = []
        for w, grad, a, moment, i in zip(net.parameters(), g, self.alpha, self.momentum_base, range(self.num_layers)):
            delta_w = a * (torch.sign(self.args_base['Lion_beta2'] * moment + (1-self.args_base['Lion_beta2'])*grad) + self.args_base['weight_decay'] * w.data)
            w.data = w.data -  delta_w
            self.momentum_base[i] = self.args_base['momentum_param'] * moment + (1-self.args_base['momentum_param'])*grad
            self.h_condenced[i] = self.gamma*(1-self.args_base['weight_decay']*a)*self.h_condenced[i] - delta_w
        
    def Lion_meta_update(self,HtT_gradft):
        for i in range(self.len_beta_list):
            self.beta[i] = (1-self.args_meta['meta_stepsize']*self.args_meta['weight_decay'])*self.beta[i] - self.args_meta['meta_stepsize'] * torch.sign(self.args_meta['Lion_beta2']*self.momentum_meta[i] + (1-self.args_meta['Lion_beta2'])*HtT_gradft[i])
            self.momentum_meta[i] = self.args_meta['momentum_param'] * self.momentum_meta[i] + (1-self.args_meta['momentum_param'])*HtT_gradft[i]
        




###################################################
    # AdamW
    def AdamW_base_update(self,net,g):
        self.lambda_base_t *= self.args_base['normalizer_param']
        mu_base = (1-self.args_base['normalizer_param'])/(1-self.lambda_base_t)
        self.momentum_base = [self.args_base['momentum_param']*self.momentum_base[i] + g[i] for i in range(self.num_layers)]
        self.trace_base = [self.args_base['normalizer_param']*self.trace_base[i] + g[i]**2 for i in range(self.num_layers)]
        for w, m, a, tr_ ,i in zip(net.parameters(), self.momentum_base, self.alpha, self.trace_base, range(self.num_layers)):
            delta_w = a * (torch.div(m, (mu_base*tr_+self.epsilon)**.5) + self.args_base['weight_decay']*w.data)
            w.data = w.data - delta_w
            self.h_condenced[i] = self.gamma*(1-self.args_base['weight_decay']*a)*self.h_condenced[i] - delta_w
    
    def Adam_meta_update(self,HtT_gradft):
        self.lambda_meta_t *= self.args_meta['normalizer_param']
        mu_meta = (1-self.args_meta['normalizer_param'])/(1-self.lambda_meta_t)
        for i in range(self.len_beta_list):
            self.momentum_meta[i] = self.args_meta['momentum_param']*self.momentum_meta[i] + HtT_gradft[i]
            self.trace_meta[i] = self.args_meta['normalizer_param'] * self.trace_meta[i] + HtT_gradft[i]**2
            self.beta[i] = (1-self.args_meta['meta_stepsize']*self.args_meta['weight_decay'])*self.beta[i] - torch.div(self.args_meta['meta_stepsize'] * self.momentum_meta[i], (mu_meta*self.trace_meta[i] + self.epsilon)**.5)

###################################################
    # no_meta_update
    def no_meta_update(self,HtT_gradft): # no update for Meta. Only use for scalar stepsizes_type
        return None




