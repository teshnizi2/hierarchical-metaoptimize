"""Sign-agreement reducer for the LEGACY probe format (gate1/gate2: beta,snr,step,z_mean,z_std).

Those records carry no frac_neg/frac_zero.  They DO carry the per-coordinate meta-gradient
mean list `z_mean`, so agreement is computed directly:
    frac_zero = mean(z_mean == 0)
    p         = (z_mean < 0) / (nonzero count)
    agree_sys = max(p, 1-p)   averaged over the window as agree2.py does it
Also prints the per-step statistic and its independence null, identically to agree2.py, so the
two families are read on the same scale.  n_tot is EXACT here (len of the list), not inferred.
"""
import json, sys, os, math, statistics as st
SQ2PI = math.sqrt(2.0/math.pi)

def load(d):
    p = os.path.join(d, "probe.jsonl")
    if not os.path.exists(p): return []
    out=[]
    for l in open(p):
        l=l.strip()
        if not l: continue
        try: out.append(json.loads(l))
        except Exception: pass
    return out

def stats(w):
    fzs=[]; fns=[]; ps=[]; ntot=None
    for r in w:
        z=r.get("z_mean")
        if z is None: return None
        if not isinstance(z,list): z=[z]
        n=len(z); ntot=n
        nz=0; neg=0
        for v in z:
            if v!=v: continue
            if v==0: continue
            nz+=1
            if v<0: neg+=1
        if nz==0: continue
        fzs.append(1-nz/n); fns.append(neg/n)
        pr=neg/nz; ps.append(max(pr,1-pr))
    if not ps: return None
    fz=st.mean(fzs); fn=st.mean(fns)
    p_sys = fn/(1-fz) if fz<1 else float("nan")
    n_nz = ntot*(1-fz)
    sds=[st.pstdev(r["beta"]) for r in w if len(r.get("beta",[]))>1]
    b0,b1=st.mean(w[0]["beta"]),st.mean(w[-1]["beta"])
    ds=w[-1]["step"]-w[0]["step"]
    return dict(ntot=ntot, fz=fz, agree_sys=max(p_sys,1-p_sys), agree_step=st.mean(ps),
                null_step=0.5+SQ2PI*0.5/math.sqrt(n_nz) if n_nz>0 else float("nan"),
                sd_beta=st.mean(sds) if sds else float("nan"),
                drift=abs(b1-b0)/ds if ds else float("nan"))

def run(dirs, lo, hi, label):
    print(f"\n### {label}")
    hdr=(f"{'arm':32s} {'n_tot':>11} {'frac0':>7} {'sys%':>9} {'step%':>9} {'null%':>9} "
         f"{'step-null':>10} {'sd_beta':>9} {'drift/step':>11}")
    print(hdr); print("-"*len(hdr))
    for d in sorted(dirs):
        recs=load(d); nm=os.path.basename(d)
        if not recs: print(f"{nm:32s}  (no records)"); continue
        n=len(recs); w=recs[int(lo*n):max(int(hi*n),int(lo*n)+2)]
        if len(w)<2: print(f"{nm:32s}  (window too short)"); continue
        s=stats(w)
        if s is None: print(f"{nm:32s}  (no usable z_mean)"); continue
        if s['ntot']<2:
            print(f"{nm:32s} {s['ntot']:>11} {s['fz']:>7.3f} {'n/a':>9} {'n/a':>9} {'n/a':>9} "
                  f"{'n/a':>10} {'n/a':>9} {s['drift']:>11.3e}"); continue
        print(f"{nm:32s} {s['ntot']:>11,} {s['fz']:>7.3f} {100*s['agree_sys']:>9.4f} "
              f"{100*s['agree_step']:>9.4f} {100*s['null_step']:>9.4f} "
              f"{100*(s['agree_step']-s['null_step']):>10.4f} {s['sd_beta']:>9.4f} {s['drift']:>11.3e}")

if __name__=="__main__":
    dirs=[a for a in sys.argv[1:] if not a.startswith("-")]
    run(dirs,0.50,1.00,"STEADY window (last 50% of records)")
    run(dirs,0.00,0.20,"STARTUP window (first 20% of records)")
