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
        self._sched_init(alpha0)  # PATCH_BSCHED (must follow init_meta: reads self.beta)
        

    
    def step(self, net, loss):
        net.zero_grad()
        g = torch.autograd.grad(loss, net.parameters(), create_graph=False)

        with torch.no_grad():
            self.alpha = self.beta_to_alpha(self.beta)
            HtT_gradft = self.block_product(self.h_condenced, g)
            
            self.base_update(net,g)
            if self._hier == 'zpool':  # PATCH_ZPOOL
                HtT_gradft = self._zpool(HtT_gradft)
            elif self._hier == 'zmpool':  # PATCH_ZMPOOL
                HtT_gradft = self._zmpool(HtT_gradft)
            self.meta_update(HtT_gradft)
            if self._hier:  # PATCH_HIER
                self._apply_hier()
            if self._beta_lo is not None:  # PATCH_CLIP
                for _i in range(self.len_beta_list):
                    self.beta[_i] = self.beta[_i].clamp(self._beta_lo, self._beta_hi)
            if self._bsched_hook:  # PATCH_BSCHED (False unless BETA_SCHEDULE/BETA_TRACE set)
                self._bsched_step()
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





    # ----------------------------------------------------------- PATCH_ZPOOL
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

    # ---------------------------------------------------------- PATCH_ZMPOOL
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

    # ========================================================== PATCH_BSCHED
    # Externally-driven beta schedules, plus an optional dense per-step trace.
    #
    # Why (cycle 36): ms_eff is a SCHEDULE, not a constant -- drift/step decays
    # 11.8x-78.3x from startup to steady and the decay factor is ordered by the
    # granularity m -- so constant-meta-stepsize matching can never identify the
    # residual.  Driving beta from a RECORDED trajectory turns "does granularity
    # do anything beyond the beta trajectory it induces?" into a direct test.
    #
    # INERT BY DEFAULT.  With BETA_SCHEDULE and BETA_TRACE both unset this adds
    # exactly one `if self._bsched_hook:` test on a False bool inside step(),
    # and five attribute stores inside __init__.  No tensor is allocated, no RNG
    # is touched, self.beta is neither read nor written.
    #
    # ALIGNMENT CONTRACT (the thing to get right).  self.counter is -1 during
    # the no_grad block of the first step() call and is incremented at the END
    # of step(), so during call j (0-based) self.counter == j-1.  This hook runs
    # at the END of the no_grad block, i.e. it sets the beta that call j+1 will
    # consume.  Therefore:
    #       sched[t] is the value of beta at the END of step() call t,
    #       t = self.counter + 1,
    #       sched[0] is set after one base update at the *init* beta,
    #       a probe.jsonl record tagged {"step": s} holds sched[s+1].
    # analysis/make_beta_replay.py emits arrays in exactly this indexing.
    #
    # ENV
    #   BETA_SCHEDULE=frozen              beta pinned at its init value log(a0)
    #   BETA_SCHEDULE=replay:<file.npy>   beta driven from a recorded array;
    #                                     shape (T,) broadcasts to every group,
    #                                     shape (T,G) is per-group and requires
    #                                     len(self.beta)==1 and G==beta[0].numel()
    #   BETA_SCHEDULE=replay:<file.npy>#<c>   take column c of a (T,C) file
    #                                     (BETA_TRACE files are (T,2): 0=param-
    #                                     weighted mean, 1=group-equal mean)
    #   BETA_SCHEDULE=cosine:<b0>:<b1>    b(t)=b1+(b0-b1)*(1+cos(pi*t/T))/2,
    #                                     T=BETA_SCHED_TOTAL (default COS_TOTAL)
    #   BETA_SCHED_TAIL=hold|error        t>=T behaviour (default hold-last)
    #   BETA_TRACE=<file.npy>             dump the per-step mean beta, float64,
    #                                     shape (t+1,2) [param-wtd, group-equal]
    #   BETA_TRACE_EVERY / _FLUSH / _CAP  stride / flush period / capacity
    # ------------------------------------------------------------------------
    def _sched_init(self, alpha0):
        import os as _os
        self._bsched_hook = False
        self._sched_mode = None
        self._sched_buf = None
        self._sched_tail_holds = 0
        self._btrace_buf = None
        spec = _os.environ.get('BETA_SCHEDULE', '').strip()
        tpath = _os.environ.get('BETA_TRACE', '').strip()
        if not spec and not tpath:
            return                      # <-- the default path, provably inert

        import json as _json
        dev = self.beta[0].device
        dt = self.beta[0].dtype         # float32 in every granularity today
        man = {'stepsize_type': self.stepsize_type, 'alpha0': float(alpha0),
               'len_beta_list': int(self.len_beta_list),
               'beta_numel': [int(b.numel()) for b in self.beta],
               'beta_dtype': str(dt), 'beta_device': str(dev),
               'beta_clip': None if self._beta_lo is None else [self._beta_lo, self._beta_hi],
               'index_convention': 'sched[t] = beta at end of step() call t; probe step s == sched[s+1]'}

        # ---- parse + materialise the schedule ------------------------------
        if spec:
            if self._hier:
                raise ValueError('BETA_SCHEDULE is incompatible with HIER=%r: '
                                 '_apply_hier caches _beta_prev, which an imposed '
                                 'beta invalidates.' % (self._hier,))
            self._sched_tail = _os.environ.get('BETA_SCHED_TAIL', 'hold').strip() or 'hold'
            if self._sched_tail not in ('hold', 'error'):
                raise ValueError('BETA_SCHED_TAIL must be hold|error, got %r' % self._sched_tail)
            src64 = None
            if spec == 'frozen':
                self._sched_mode = 'frozen'
                b0 = self.beta[0].detach().reshape(-1)
                # every granularity inits to a single value log(alpha0); assert it
                lo_ = min(float(b.min()) for b in self.beta)
                hi_ = max(float(b.max()) for b in self.beta)
                if lo_ != hi_:
                    raise ValueError('frozen: init beta is not uniform (%r..%r)' % (lo_, hi_))
                # taken from the live tensor, so it is the init value bit-for-bit
                buf = b0[:1].clone()                                  # shape (1,)
                man['sched_src'] = 'init-beta'
                man['frozen_at'] = lo_
            elif spec.startswith('replay:'):
                self._sched_mode = 'replay'
                rest = spec[len('replay:'):]
                col = None
                if '#' in rest:
                    rest, c = rest.rsplit('#', 1)
                    col = int(c)
                path = rest
                import hashlib as _hl
                with open(path, 'rb') as _fh:
                    raw = _fh.read()
                man['sched_src'] = _os.path.abspath(path)
                man['sched_sha256'] = _hl.sha256(raw).hexdigest()
                arr = np.load(path)
                man['sched_file_shape'] = list(arr.shape)
                man['sched_file_dtype'] = str(arr.dtype)
                src64 = np.ascontiguousarray(arr, dtype=np.float64)
                if src64.ndim == 2 and col is not None:
                    src64 = src64[:, col]
                    man['sched_col'] = col
                if src64.ndim == 1:
                    pass
                elif src64.ndim == 2:
                    if self.len_beta_list != 1 or src64.shape[1] != self.beta[0].numel():
                        raise ValueError('per-group replay needs a single beta tensor of '
                                         'numel %d, got len_beta_list=%d numel=%d and (T,G)=%r'
                                         % (src64.shape[1], self.len_beta_list,
                                            self.beta[0].numel(), src64.shape))
                else:
                    raise ValueError('replay array must be 1-D or 2-D, got %r' % (src64.shape,))
                if not np.isfinite(src64).all():
                    raise ValueError('replay array contains non-finite values')
                buf = torch.as_tensor(src64, dtype=dt, device=dev)   # ONE round-to-nearest
            elif spec.startswith('cosine:'):
                self._sched_mode = 'cosine'
                _, b0s, b1s = spec.split(':')
                b0f, b1f = float(b0s), float(b1s)
                T = int(_os.environ.get('BETA_SCHED_TOTAL', _os.environ.get('COS_TOTAL', '0')) or 0)
                if T <= 1:
                    raise ValueError('BETA_SCHEDULE=cosine needs BETA_SCHED_TOTAL (or COS_TOTAL) > 1')
                t64 = np.arange(T, dtype=np.float64)
                src64 = b1f + (b0f - b1f) * (1.0 + np.cos(np.pi * t64 / (T - 1))) / 2.0
                man['sched_src'] = 'cosine:%r:%r:T=%d' % (b0f, b1f, T)
                buf = torch.as_tensor(src64, dtype=dt, device=dev)
            else:
                raise ValueError('unrecognised BETA_SCHEDULE=%r '
                                 '(frozen | replay:<f.npy>[#col] | cosine:<b0>:<b1>)' % spec)

            # ---- interact with beta_clip ONCE, at load, not per step --------
            n_clip = 0
            if self._beta_lo is not None:
                bc = buf.clamp(self._beta_lo, self._beta_hi)
                n_clip = int((bc != buf).reshape(bc.shape[0], -1).any(dim=1).sum())
                buf = bc
            man['sched_T'] = int(buf.shape[0])
            man['sched_ndim'] = int(buf.dim())
            man['sched_clipped_steps'] = n_clip
            man['sched_min'] = float(buf.min())
            man['sched_max'] = float(buf.max())

            # ---- float32 resolution audit (the ulp finding) -----------------
            # beta is float32.  ulp(|log a0|) is 4.7684e-7 at a0=1e-3 and
            # 9.5367e-7 at a0=1e-6.  Absolute ASSIGNMENT (what we do) tracks the
            # target to <= half an ulp at every step and cannot accumulate the
            # rounding error that an increment-based driver would; but a target
            # whose step-to-step change is below the ulp is reproduced as a
            # staircase, so report how often that happens.
            if src64 is not None and buf.shape[0] > 1:
                f32 = buf.detach().double().cpu().numpy()
                d64 = np.abs(np.diff(src64.reshape(src64.shape[0], -1), axis=0))
                mag = np.abs(src64.reshape(src64.shape[0], -1)[:-1])
                ulp = np.spacing(np.asarray(mag, dtype=np.float32)).astype(np.float64)
                man['sched_subulp_frac'] = float((d64 < ulp).mean())
                man['sched_max_round_err'] = float(np.abs(f32.reshape(f32.shape[0], -1)
                                                          - np.clip(src64.reshape(src64.shape[0], -1),
                                                                    -np.inf if self._beta_lo is None else self._beta_lo,
                                                                    np.inf if self._beta_lo is None else self._beta_hi)).max())
            else:
                man['sched_subulp_frac'] = 0.0
                man['sched_max_round_err'] = 0.0

            # ---- does the schedule start where this run starts? -------------
            b_init = float(self.beta[0].reshape(-1)[0])
            first = buf[0].reshape(-1)[0]
            man['beta_init'] = b_init
            man['sched_init_gap'] = float(first) - b_init
            self._sched_buf = buf
            self._sched_1d = (buf.dim() == 1)
            self._bsched_hook = True

        # ---- optional dense trace ------------------------------------------
        if tpath:
            self._btrace_path = tpath
            self._btrace_every = max(1, int(_os.environ.get('BETA_TRACE_EVERY', '1')))
            self._btrace_flushn = max(1, int(_os.environ.get('BETA_TRACE_FLUSH', '1000')))
            cap = int(_os.environ.get('BETA_TRACE_CAP', '400000'))
            self._btrace_cap = max(1, cap // self._btrace_every)
            self._btrace_buf = torch.zeros(self._btrace_cap, 2, dtype=torch.float64, device=dev)
            self._btrace_n = 0
            self._btrace_full = False
            # per-beta-entry weights = number of NETWORK PARAMETERS that entry governs.
            # This is the corrected weighting: agree2 averages per-tensor beta means
            # with EQUAL weight, which is the true group mean only for blk6/layerwise.
            if self.stepsize_type == 'scalar':
                w = [float(sum(self.param_numels))]
            elif self.stepsize_type == 'blockwise':
                w = [torch.tensor([float(sum(self.param_numels[i] for i in gi))
                                   for gi in self.param_groups_indices], dtype=torch.float64, device=dev)]
            elif self.stepsize_type == 'layerwise':
                w = [torch.tensor([float(n) for n in self.param_numels], dtype=torch.float64, device=dev)]
            elif self.stepsize_type == 'nodewise':
                # beta[i] has one entry per NODE; each governs numel_i/n_nodes_i params
                w = [float(self.param_numels[i]) / float(max(self.beta[i].numel(), 1))
                     for i in range(self.len_beta_list)]
            else:  # weightwise: one beta entry per parameter
                w = [1.0 for _ in range(self.len_beta_list)]
            self._bt_w = w
            self._bt_wsum = float(sum((wi.sum() if torch.is_tensor(wi) else wi * self.beta[i].numel())
                                      for i, wi in enumerate(w)))
            self._bt_cnt = float(sum(b.numel() for b in self.beta))
            man['btrace_path'] = _os.path.abspath(tpath)
            man['btrace_every'] = self._btrace_every
            man['btrace_cap_steps'] = self._btrace_cap * self._btrace_every
            man['btrace_w_sum'] = self._bt_wsum
            man['btrace_cols'] = ['param_weighted_mean_beta', 'group_equal_mean_beta']
            # train.py has no teardown hook, so the periodic flush would always
            # truncate the tail; flush once more on normal interpreter exit.
            import atexit as _atexit
            _atexit.register(self._btrace_flush)
            self._bsched_hook = True

        # ---- self-description (OPERATIONS gotcha 8) ------------------------
        man['sched_mode'] = self._sched_mode
        self._sched_manifest = man
        print('ENV: BETA_SCHEDULE=%s BETA_SCHED_SRC=%s BETA_SCHED_T=%s BETA_SCHED_SHA=%s '
              'BETA_SCHED_CLIPPED=%s BETA_SCHED_SUBULP=%s BETA_SCHED_INITGAP=%s '
              'BETA_SCHED_TAIL=%s BETA_TRACE=%s'
              % (self._sched_mode or 'none', man.get('sched_src', 'na'),
                 man.get('sched_T', 'na'), man.get('sched_sha256', 'na')[:16],
                 man.get('sched_clipped_steps', 'na'),
                 ('%.4g' % man['sched_subulp_frac']) if 'sched_subulp_frac' in man else 'na',
                 ('%.6g' % man['sched_init_gap']) if 'sched_init_gap' in man else 'na',
                 getattr(self, '_sched_tail', 'na'), tpath or 'none'), flush=True)
        mdir = _os.environ.get('PROBE_DIR', '') or (_os.path.dirname(tpath) if tpath else '')
        if mdir:
            _os.makedirs(mdir, exist_ok=True)
            with open(_os.path.join(mdir, 'beta_schedule.json'), 'w') as fh:
                _json.dump(man, fh, indent=1, sort_keys=True)

    def _bsched_step(self):
        """Runs at the END of step()'s no_grad block, AFTER meta_update, hier and
        the beta_clip clamp -- so the imposed value is what _probe records and
        what the next base update consumes."""
        t = self.counter + 1
        if self._sched_buf is not None:
            T = self._sched_buf.shape[0]
            if t >= T:
                if self._sched_tail == 'error':
                    raise IndexError('BETA_SCHEDULE exhausted at t=%d (T=%d)' % (t, T))
                self._sched_tail_holds += 1
                t = T - 1
            v = self._sched_buf[t]                 # already clamped at load time
            if self._sched_1d:
                for i in range(self.len_beta_list):
                    # 0-dim -> stride-0 view: no allocation even at weightwise
                    self.beta[i] = v.expand_as(self.beta[i])
            else:
                self.beta[0] = v.reshape(self.beta[0].shape)
        if self._btrace_buf is not None:
            s = self.counter + 1
            if s % self._btrace_every == 0:
                k = s // self._btrace_every
                if k < self._btrace_cap:
                    # float64 accumulation: an 11.2M-element float32 sum around
                    # -7 loses ~3 decimal digits, and steady drift is ~1e-5/step.
                    pw = 0.0
                    gw = 0.0
                    for i in range(self.len_beta_list):
                        b = self.beta[i]
                        wi = self._bt_w[i]
                        gw = gw + b.sum(dtype=torch.float64)
                        if torch.is_tensor(wi):
                            pw = pw + (b.to(torch.float64) * wi).sum(dtype=torch.float64)
                        else:
                            pw = pw + b.sum(dtype=torch.float64) * wi
                    self._btrace_buf[k, 0] = pw / self._bt_wsum
                    self._btrace_buf[k, 1] = gw / self._bt_cnt
                    self._btrace_n = k + 1
                    if (k + 1) % self._btrace_flushn == 0:
                        self._btrace_flush()
                elif not self._btrace_full:
                    self._btrace_full = True
                    print('ENV: BETA_TRACE_OVERFLOW=1 at step %d' % s, flush=True)
                    self._btrace_flush()

    def _btrace_flush(self):
        import os as _os
        try:
            a = self._btrace_buf[:self._btrace_n].detach().cpu().numpy()
            tmp = self._btrace_path + '.tmp.npy'
            np.save(tmp, a)
            _os.replace(tmp, self._btrace_path)
        except Exception as e:   # never let a trace flush kill a training run
            print('ENV: BETA_TRACE_FLUSH_ERROR=%r' % (e,), flush=True)

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
        if self._sched_mode is not None:  # PATCH_BSCHED (absent when unused)
            rec['sched_mode'] = self._sched_mode
            rec['sched_t'] = int(self.counter) + 1
            rec['sched_tail_holds'] = int(self._sched_tail_holds)
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




