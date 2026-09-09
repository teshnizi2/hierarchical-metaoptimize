# -*- coding: utf-8 -*-
OUT = "/private/tmp/claude-501/-Users-teshnizi-Saber-Optimization/7abb0c79-bcc7-424b-856d-f4a9fed472c1/scratchpad/ledger.html"

# ---------- chart helpers ----------
def lin(v, lo, hi, a, b):
    return a + (v - lo) / (hi - lo) * (b - a)

def fmt(x, n=1):
    return ("%." + str(n) + "f") % x

# ============ CHART 1 : cut position ============
def chart_cutpos():
    W,H = 760,400; L,R,T,B = 62,18,20,54
    x0,x1 = L, W-R; y0,y1 = T, H-B
    kmin,kmax = 15,62; vmin,vmax = 18,74
    X = lambda k: lin(k,kmin,kmax,x0,x1)
    Y = lambda v: lin(v,vmin,vmax,y1,y0)
    s100 = [(17,25.9493),(24,27.4160),(31,33.0093),(38,35.9507),(42,41.0720),
            (45,42.2393),(47,45.6880),(49,55.4473),(52,38.3420),(55,23.3720),(60,24.7187)]
    s772 = [(45,43.7833),(46,49.5060),(47,46.7840),(48,46.8480),(49,56.0453),(50,37.7747)]
    p=[]
    # grid + y labels
    for v in range(20,75,10):
        p.append(f'<line x1="{X(kmin):.1f}" y1="{Y(v):.1f}" x2="{X(kmax):.1f}" y2="{Y(v):.1f}" class="grid"/>')
        p.append(f'<text x="{X(kmin)-10:.1f}" y="{Y(v)+4:.1f}" class="ax ax-r">{v}</text>')
    for k in (20,30,40,45,49,55,62):
        p.append(f'<text x="{X(k):.1f}" y="{y1+22:.1f}" class="ax ax-c">{k}</text>')
        p.append(f'<line x1="{X(k):.1f}" y1="{y1:.1f}" x2="{X(k):.1f}" y2="{y1+6:.1f}" class="tick"/>')
    # reference bands
    for v,lab,cls in ((69.7107,'layerwise  m=62','ref-hi'),(22.7207,'scalar  m=1','ref-lo')):
        p.append(f'<line x1="{X(kmin):.1f}" y1="{Y(v):.1f}" x2="{X(kmax):.1f}" y2="{Y(v):.1f}" class="{cls}"/>')
        p.append(f'<text x="{X(kmax)-4:.1f}" y="{Y(v)-8:.1f}" class="reflab ax-e">{lab}  {fmt(v,2)}</text>')
    def series(pts, cls, dot):
        d = "M " + " L ".join(f"{X(k):.1f} {Y(v):.1f}" for k,v in pts)
        p.append(f'<path d="{d}" class="{cls}"/>')
        for k,v in pts:
            p.append(f'<circle cx="{X(k):.1f}" cy="{Y(v):.1f}" r="3.6" class="{dot}"/>')
    series(s100,'ln ln-a','dot dot-a')
    series(s772,'ln ln-b','dot dot-b')
    # peak annotation
    p.append(f'<line x1="{X(49):.1f}" y1="{Y(56.0453)-12:.1f}" x2="{X(49):.1f}" y2="{Y(56.0453)-30:.1f}" class="lead"/>')
    p.append(f'<text x="{X(49):.1f}" y="{Y(56.0453)-36:.1f}" class="note ax-c">k* = 49</text>')
    p.append(f'<text x="{X(52):.1f}" y="{Y(38.3420)+22:.1f}" class="note-s ax-c">&#8722;18.3 pp at k+3</text>')
    p.append(f'<text x="{(x0+x1)/2:.1f}" y="{H-12:.1f}" class="axtitle ax-c">first group size k &#8212; partition [k, 62&#8722;k] over ResNet-18&#8217;s 62 tensors</text>')
    p.append(f'<text transform="translate(16,{(y0+y1)/2:.1f}) rotate(-90)" class="axtitle ax-c">plateau5  (%)</text>')
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Test accuracy against cut position">' + "".join(p) + '</svg>'

# ============ CHART 2 : isolation ============
def chart_iso():
    rows = [
        ("layerwise",            "m = 62 &#183; every tensor free",        69.0273, 98.9733, "hi"),
        ("ISO",                  "[59,3] &#183; 3 carriers &#183; 1,536 p", 70.2113, 94.2800, "win"),
        ("ONE",                  "[61,1] &#183; tensor 50 &#183; 512 p",    64.7500, 83.5500, "win"),
        ("CTRL",                 "[59,3] &#183; layer-2 twins &#183; 1,536 p", 23.2173, 23.1867, "null"),
        ("scalar",               "m = 1 &#183; one step size",              23.2807, 23.1767, "lo"),
    ]
    W,H = 760, 300; L,R,T,B = 178, 66, 26, 40
    x0,x1 = L, W-R
    vmax = 100.0
    X = lambda v: lin(v,0,vmax,x0,x1)
    band = (H-T-B)/len(rows)
    p=[]
    for v in range(0,101,20):
        p.append(f'<line x1="{X(v):.1f}" y1="{T-6:.1f}" x2="{X(v):.1f}" y2="{H-B:.1f}" class="grid"/>')
        p.append(f'<text x="{X(v):.1f}" y="{H-B+18:.1f}" class="ax ax-c">{v}</text>')
    for i,(name,sub,te,tr,kind) in enumerate(rows):
        yc = T + band*i + band/2
        p.append(f'<text x="{L-14:.1f}" y="{yc-2:.1f}" class="rowname ax-r">{name}</text>')
        p.append(f'<text x="{L-14:.1f}" y="{yc+13:.1f}" class="rowsub ax-r">{sub}</text>')
        h = 11
        p.append(f'<rect x="{x0:.1f}" y="{yc-h-3:.1f}" width="{max(X(tr)-x0,1):.1f}" height="{h}" rx="1.5" class="bar bar-train"/>')
        p.append(f'<rect x="{x0:.1f}" y="{yc+3:.1f}" width="{max(X(te)-x0,1):.1f}" height="{h}" rx="1.5" class="bar bar-{kind}"/>')
        p.append(f'<text x="{X(te)+8:.1f}" y="{yc+12.5:.1f}" class="val">{fmt(te,2)}</text>')
        p.append(f'<text x="{X(tr)+8:.1f}" y="{yc-3.5:.1f}" class="val val-dim">{fmt(tr,2)}</text>')
    p.append(f'<text x="{(x0+x1)/2:.1f}" y="{H-6:.1f}" class="axtitle ax-c">accuracy (%) &#8212; upper bar train, lower bar plateau5 test &#183; 3 seeds each, one batch</text>')
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Isolation arms">' + "".join(p) + '</svg>'

# ============ CHART 3 : denominator ============
def chart_denom():
    sgd = [("0.01",75.3733),("0.02",76.3660),("0.05",77.1567),("0.1",78.2103),("0.2",77.0900),("0.3",76.3700)]
    W,H = 760,300; L,R,T,B = 62,150,22,52
    x0,x1 = L, W-R; y0,y1 = T, H-B
    vmin,vmax = 70,80
    Y = lambda v: lin(v,vmin,vmax,y1,y0)
    n=len(sgd); bw=(x1-x0)/n*0.52
    p=[]
    for v in range(70,81,2):
        p.append(f'<line x1="{x0:.1f}" y1="{Y(v):.1f}" x2="{x1:.1f}" y2="{Y(v):.1f}" class="grid"/>')
        p.append(f'<text x="{x0-10:.1f}" y="{Y(v)+4:.1f}" class="ax ax-r">{v}</text>')
    for i,(lab,v) in enumerate(sgd):
        cx = x0 + (x1-x0)*(i+0.5)/n
        best = (lab=="0.1")
        p.append(f'<rect x="{cx-bw/2:.1f}" y="{Y(v):.1f}" width="{bw:.1f}" height="{y1-Y(v):.1f}" rx="2" class="bar {"bar-hi" if best else "bar-base"}"/>')
        p.append(f'<text x="{cx:.1f}" y="{Y(v)-8:.1f}" class="val ax-c">{fmt(v,2)}</text>')
        p.append(f'<text x="{cx:.1f}" y="{y1+20:.1f}" class="ax ax-c">{lab}</text>')
    meta = 71.8933
    p.append(f'<line x1="{x0:.1f}" y1="{Y(meta):.1f}" x2="{x1+118:.1f}" y2="{Y(meta):.1f}" class="ref-lo"/>')
    p.append(f'<text x="{x1+10:.1f}" y="{Y(meta)+4:.1f}" class="reflab">best MetaOptimize</text>')
    p.append(f'<text x="{x1+10:.1f}" y="{Y(meta)+19:.1f}" class="rowsub">CIFAR-100, 71.89</text>')
    # gap bracket
    gx = x1+4
    p.append(f'<line x1="{gx:.1f}" y1="{Y(78.2103):.1f}" x2="{gx:.1f}" y2="{Y(meta):.1f}" class="brk"/>')
    p.append(f'<text x="{x1+10:.1f}" y="{Y(75.0):.1f}" class="note">&#8722;5.699 pp</text>')
    p.append(f'<text x="{x1+10:.1f}" y="{Y(75.0)+15:.1f}" class="rowsub">18.80 SE, in batch</text>')
    p.append(f'<text x="{(x0+x1)/2:.1f}" y="{H-8:.1f}" class="axtitle ax-c">tuned plain SGD &#8212; learning rate &#183; plateau5 (%) &#183; CIFAR-100 / ResNet-18 / 100 ep</text>')
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Tuned SGD versus MetaOptimize on CIFAR-100">' + "".join(p) + '</svg>'

# ============ CHART 4 : rule 11 ladder ============
def chart_rule11():
    ms   = ["1e-5","3e-5","1e-4","3e-4","1e-3","3e-3"]
    lay  = [32.3207,53.5940,71.0827,70.1927,69.8393,69.8560]
    sca  = [24.7147,28.9507,35.7920,29.7820,22.3787,16.3547]
    W,H = 760,360; L,R,T,B = 62,120,24,54
    x0,x1 = L, W-R; y0,y1 = T, H-B
    vmin,vmax = 10,76
    Y = lambda v: lin(v,vmin,vmax,y1,y0)
    X = lambda i: x0 + (x1-x0)*i/(len(ms)-1)
    p=[]
    for v in range(10,80,10):
        p.append(f'<line x1="{x0:.1f}" y1="{Y(v):.1f}" x2="{x1:.1f}" y2="{Y(v):.1f}" class="grid"/>')
        p.append(f'<text x="{x0-10:.1f}" y="{Y(v)+4:.1f}" class="ax ax-r">{v}</text>')
    for i,m in enumerate(ms):
        p.append(f'<text x="{X(i):.1f}" y="{y1+20:.1f}" class="ax ax-c">{m}</text>')
    # shaded gap at own optima (both peak at 1e-4)
    i4 = 2
    p.append(f'<rect x="{X(i4)-15:.1f}" y="{Y(71.0827):.1f}" width="30" height="{Y(35.7920)-Y(71.0827):.1f}" class="gapband"/>')
    def series(vals, cls, dot):
        d = "M " + " L ".join(f"{X(i):.1f} {Y(v):.1f}" for i,v in enumerate(vals))
        p.append(f'<path d="{d}" class="{cls}"/>')
        for i,v in enumerate(vals):
            p.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.6" class="{dot}"/>')
    series(lay,'ln ln-a','dot dot-a')
    series(sca,'ln ln-b','dot dot-b')
    p.append(f'<text x="{x1+10:.1f}" y="{Y(lay[-1])+4:.1f}" class="reflab">layerwise</text>')
    p.append(f'<text x="{x1+10:.1f}" y="{Y(sca[-1])+4:.1f}" class="reflab">scalar</text>')
    p.append(f'<text x="{X(i4)+22:.1f}" y="{Y(53.4):.1f}" class="note">35.29 pp</text>')
    p.append(f'<text x="{X(i4)+22:.1f}" y="{Y(53.4)+15:.1f}" class="rowsub">gap at each arm&#8217;s own optimum</text>')
    p.append(f'<text x="{(x0+x1)/2:.1f}" y="{H-10:.1f}" class="axtitle ax-c">meta step size &#183; plateau5 (%) &#183; &#945;&#8320; = 1e-3, CIFAR-100 / ResNet-18 / 100 ep</text>')
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Granularity gap across the meta step-size ladder">' + "".join(p) + '</svg>'


# ============ CHART 5 : layer4 BN scales, magnitude x residual role ============
import math
def chart_layer4():
    # mean |L_i| on ciso1's k01 pinned records (945 pinned, pooled over 3 seeds)
    rows = [
        (59,"layer4.1.bn2.weight",        3.1880e-01, 1,  True),
        (50,"layer4.0.bn2.weight",        2.8115e-01, 2,  True),
        (53,"layer4.0.shortcut.1.weight", 1.8325e-01, 3,  True),
        (56,"layer4.1.bn1.weight",        1.2896e-03, 33, False),
        (47,"layer4.0.bn1.weight",        9.5915e-04, 38, False),
        (48,"layer4.0.bn1.bias",          1.7344e-06, 62, False),
    ]
    median = 1.9395e-03
    W,H = 760, 320; L,R,T,B = 210, 108, 26, 52
    x0,x1 = L, W-R
    lo,hi = -6.2, 0.2
    X = lambda v: lin(math.log10(v), lo, hi, x0, x1)
    band = (H-T-B)/len(rows)
    p=[]
    for e in range(-6,1):
        gx = lin(e,lo,hi,x0,x1)
        p.append(f'<line x1="{gx:.1f}" y1="{T-8:.1f}" x2="{gx:.1f}" y2="{H-B:.1f}" class="grid"/>')
        lab = "1" if e==0 else f"1e{e}"
        p.append(f'<text x="{gx:.1f}" y="{H-B+18:.1f}" class="ax ax-c">{lab}</text>')
    # median marker
    mx = X(median)
    p.append(f'<line x1="{mx:.1f}" y1="{T-8:.1f}" x2="{mx:.1f}" y2="{H-B:.1f}" class="ref-lo"/>')
    p.append(f'<text x="{mx:.1f}" y="{T-13:.1f}" class="rowsub ax-c">median tensor</text>')
    for i,(idx,name,v,rank,carrier) in enumerate(rows):
        yc = T + band*i + band/2
        p.append(f'<text x="{L-14:.1f}" y="{yc-1:.1f}" class="rowname ax-r" style="font-size:11.5px">{name}</text>')
        role = "feeds a residual add" if carrier else "mid-branch, behind ReLU"
        p.append(f'<text x="{L-14:.1f}" y="{yc+12:.1f}" class="rowsub ax-r">tensor {idx} &#183; {role}</text>')
        h=13
        p.append(f'<rect x="{x0:.1f}" y="{yc-h/2:.1f}" width="{max(X(v)-x0,1.5):.1f}" height="{h}" rx="1.5" class="bar bar-{"null" if carrier else "base"}"/>')
        p.append(f'<text x="{X(v)+8:.1f}" y="{yc+4.5:.1f}" class="val">{v:.2e}</text>')
        p.append(f'<text x="{W-10:.1f}" y="{yc+4.5:.1f}" class="rowsub ax-e">rank {rank}/62</text>')
    p.append(f'<text x="{(x0+x1)/2:.1f}" y="{H-8:.1f}" class="axtitle ax-c">mean |L&#7522;| on pinned records &#183; log scale &#183; the term the Lion sign consumes</text>')
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Layer-4 BatchNorm scales by meta-gradient magnitude and residual role">' + "".join(p) + '</svg>'

# ---------- content tables ----------
HOLDS = [
 ("Cut position beats group count","At m = 2, <em>where</em> the 62 tensors are split moves test accuracy by 25.07 pp; adding groups does not. Argmax <code>k* = 49</code>.","cpk1 / cpk2 / cpk3","39+18+21 runs, 3 fresh-seed batches, 100 &amp; 772 ep","158, 161"),
 ("The cut-position peak survives the horizon","Re-run at 772 epochs on fresh seeds {3,4,5} and again on {6,7,8}: the argmax does not move. The forecast predicted three rank swaps; zero occurred.","cpk2 / cpk3","772 ep &#183; converged budget","156, 158, 161"),
 ("The gap survives tuning (RULE 11)","Each arm at its <em>own</em> optimal meta step size, the scalar&#8594;layerwise gap goes 47.46 &#8594; 35.29 pp. Ratio 0.7436. It is not a distance-from-optimum artefact.","cru1","60 runs, 10 rungs &#215; 2 granularities","174"),
 ("The gap is not a clamp artefact","Releasing the <code>BETA_CLIP</code> floor at ms = 1e-3 <em>and</em> at 3e-4 leaves the granularity gap standing.","cfr1 / cfr2","two independent floor releases","153, 155"),
 ("Scope breaks at ImageNet-489","On 489-class ImageNet the ordering that holds on CIFAR does not: scalar collapses to 0.96 %, layerwise reaches 49.25 %, and a count-matched partition lands at 43.27 %.","in489g2","14 runs, 26 rows in corpus","163"),
 ("The reduction composes","Per-group normalisation is bitwise inert under Lion; what is operative is how per-tensor terms compose <em>before</em> the sign. <code>COMPOSITION-OPERATIVE</code>.","crn1","18 runs on the shared account","169, 173"),
 ("1,536 parameters recover the whole gap","Giving three <code>layer4</code> BatchNorm scales their own step size lifts plateau5 from 23.28 to 70.21 &#8212; +46.93 pp, +62.10 SE &#8212; and reaches the layerwise ceiling. The layer-2 structural twins recover nothing (&#8722;0.06 pp).","ciso1","15 runs, 5 arms, in batch","185, 187"),
]

DIES = [
 ("MetaOptimize beats a tuned baseline","On CIFAR-100 the family sits <strong>5.699 pp below</strong> tuned plain SGD &#8212; 18.80 SE, in batch, and <em>every</em> rung of the SGD ladder including the worst beats the best meta cell. On CIFAR-10 the deficit is 1.46 pp.","cdn1 / cdn2","171, 175"),
 ("The accuracy reversal is a granularity result","With each arm at its own optimal ms the epoch-10&#8594;40 trend runs the other way. Only writable with an &#8220;at a shared ms = 1e-3&#8221; qualifier.","hz9","MASTER-TABLE c73"),
 ("The class-count law","Refuted on its own registered band: Q(489) = 0.021 against 0.132 predicted.","in489g2","163"),
 ("Hierarchical pooling fixes (M0 shrink, M1 additive r, zpool)","All three refuted by their own controls; the r-dial is a meta-learning-rate knob, not a pooling knob.","hier series","MASTER-TABLE"),
 ("H-DOMINATE as named","Layer-4 convs + classifier carrying the sign down: <code>NAMED-CARRIED</code> = 0.0000 at tensor level, untestable at element level.","ctd1","181, 184, 186"),
 ("H-DISAGREE","Disagreement rate is monotone-decreasing in k (0.3834 at k=1 &#8594; 0.0414 at k=53&#8211;57), &#961; = &#8722;0.046 against the capture curve.","zero-GPU","179"),
 ("Domination is the operative quantity","<code>ONE</code> (tensor 50 alone, 512 params) also rescues, +41.47 pp. The operative quantity is the <em>sign of the remainder sum</em>, not domination.","ciso1","187"),
 ("Contiguity refuted with the sign reversed","Superseded in place &#8212; it conflated hole count with tensor identity. Co-grouping dies at &#8722;10.22 SE.","cpg1","164, 166"),
 ("A second cut-position site","Withdrawn: the two winners are the two branch gains of <em>one</em> residual add.","scl1","152, 147.6"),
]

CAND = [
 ("1&#8211;13","thirteen observational candidates","DEAD","refuted or unreachable on their own registered bands","144&#8211;168"),
 ("14","the reduction &#8212; <code>crn1</code>","LIVE","<code>COMPOSITION-OPERATIVE</code> on one clean pair; the null is excluded on all three","169, 173"),
 ("15","H-DISAGREE","DEAD","argmax at k = 1, &#961; = &#8722;0.05","179"),
 ("16","H-DOMINATE","DEAD","dead as named; element statistic does not exist on disk","181, 184, 186"),
 ("17","H-ISOLATE &#8212; <code>ciso1</code>","LIVE","<code>UNRESOLVED-PARTIAL</code>; two arms in flight to close it","185, 187"),
]

RUNNING = [
 ("cdep1","<strong>18 jobs</strong> &#183; 6 arms &#215; seeds {24,25,26} &#183; 100 ep. Isolates {47, 48, 56} at [59,3] &#8212; matched to ISO on group size, isolated numel (1,536 <em>exactly</em>), tensor width and depth, with no carrier. Plus DEPTH2, the class-pure two-tensor variant.","Identity vs depth. Primary is <code>&#916;_ID = ISO &#8722; DEPTH</code>, bounded in neither direction &#8212; not <code>D_DEPTH</code>, which is predicted <em>on</em> the floor and so could not disagree with the account predicting it.","188"),
 ("ciso2","<strong>12 jobs</strong> &#183; 4 arms &#215; seeds {31,32,33} &#183; <strong>250 ep</strong>, horizon derived from the measured descent, not chosen round. Spec strings byte-identical to <code>ciso1</code>&#8217;s. The 100-epoch control is read in-run and paired.","Whether the rescue is a regime or a ~68-epoch delay. <code>RHO = D_ISO@250 / D_ISO@100</code>. Survival bar 0.80 is corpus-anchored: it exceeds the best rescue <em>any</em> two-group partition of this cell has produced.","190"),
 ("cvg1","<strong>6 jobs</strong> &#183; scalar vs layerwise on <code>VGG11_bn_c100</code> &#183; 100 ep. <strong>The campaign&#8217;s first non-ResNet batch</strong> &#8212; 26 tensors, 9,274,532 params, BatchNorm kept, residual additions gone.","Whether the scalar&#8594;layerwise gap exists off ResNet at all. <code>GAP-REPLICATES</code> answers the scope objection for the gap; <code>GAP-ABSENT</code> is a real, publishable scope limit on the headline.","189"),
]

def tr_holds():
    out=[]
    for t,d,b,n,c in HOLDS:
        out.append(f'<tr><td class="c-st"><span class="pill pill-ok">holds</span></td>'
                   f'<td><div class="t-claim">{t}</div><div class="t-detail">{d}</div></td>'
                   f'<td class="c-mono">{b}<div class="t-detail">{n}</div></td>'
                   f'<td class="c-cite">{c}</td></tr>')
    return "".join(out)

def tr_dies():
    out=[]
    for t,d,b,c in DIES:
        out.append(f'<tr><td class="c-st"><span class="pill pill-bad">dead</span></td>'
                   f'<td><div class="t-claim">{t}</div><div class="t-detail">{d}</div></td>'
                   f'<td class="c-mono">{b}</td><td class="c-cite">{c}</td></tr>')
    return "".join(out)

def tr_cand():
    out=[]
    cls={"DEAD":"pill-bad","LIVE":"pill-ok"}
    for n,name,st,note,c in CAND:
        out.append(f'<tr><td class="c-num">{n}</td><td class="t-claim">{name}</td>'
                   f'<td class="c-st"><span class="pill {cls[st]}">{st.lower()}</span></td>'
                   f'<td class="t-detail">{note}</td><td class="c-cite">{c}</td></tr>')
    return "".join(out)

def tr_running():
    out=[]
    for tag,what,dec,ent in RUNNING:
        out.append(f'<tr><td class="c-mono c-tag">{tag}</td><td class="t-detail">{what}</td>'
                   f'<td class="t-detail">{dec}</td><td class="c-cite">{ent}</td></tr>')
    return "".join(out)

CORPUS = [("CIFAR-10","2,190","ResNet-10 / 18 / 34 / 50 / 101"),
          ("CIFAR-100","536","ResNet-18_c100, ResNet-34_c100, ResNet-10_c100"),
          ("ImageNet-489","26","ResNet-18"),
          ("Tiny-ImageNet","9","ResNet-18_tin")]

def tr_corpus():
    return "".join(f'<tr><td class="t-claim">{a}</td><td class="c-num c-mono">{b}</td><td class="t-detail">{c}</td></tr>'
                   for a,b,c in CORPUS)

HOUSE = [
 ("Account GPU budget is ~45.9 h across three concurrent batches","Each batch honoured its own ~30 h ceiling; no track could see the sum. Nothing is over-committed &#8212; two of the three can use <code>gpu-short</code>, an independent QOS pool &#8212; but a fourth batch should not launch on <code>alice2</code> before these drain.","warn"),
 ("RULE 20 coverage is 9 of 36","<code>cdep1</code> passes 9/9 on the unedited guard with a clean ENV audit. <code>ciso2</code> and <code>cvg1</code> have started no jobs, so the guard has nothing to read &#8212; <em>unverified</em>, not failed. No number from any of the three may be quoted before 36/36.","warn"),
 ("Seeds {31,32,33} are used twice","<code>ciso2</code> and <code>cvg1</code> both reserved them. Both freshness claims were correct against the corpus; neither track could see the other. Different architectures, different prefixes, every contrast in batch &#8212; not a defect, but next free triple is {34,35,36}.","warn"),
 ("<code>docs/MASTER-TABLE.md</code> is 14 cycles behind","Compiled at 2,537 runs / cycle 129. Everything since &#8212; <code>cdn1</code>, <code>cru1</code>, <code>crn1</code>, <code>ctd1</code>, <code>ciso1</code> &#8212; lives only in <code>CORRECTIONS</code> 144&#8211;187.","warn"),
 ("<code>paper/paper.tex</code> predates this week entirely","5,173 lines, untouched since 2026-09-03. None of the isolation, denominator or RULE 11 work is in it.","warn"),
 ("<code>analysis/c98_reproduce.py</code> exits 1","Ten stale-numeral failures, inherited, author scope. Deliberately not fixed &#8212; fixing it would edit registered scorers.","warn"),
 ("Zero failed runs this week","Every submitted job in cycles 141&#8211;148 completed. No arm was lost to a harness fault; 0 tracebacks across the 36 in flight.","ok"),
 ("Corpus integrity","Every ingest this week verified 0 pre-existing rows changed. 43 GB of probe logs pruned after proving the corpus rebuilds bit-identically.","ok"),
 ("Provenance","Private remote in sync at <code>712ff65</code>. <code>argsline_guard.py</code> byte-identical across the Mac and four deployed cluster trees, untouched since cycle 99. RULE 21 margins this cycle: +231 s, +152 s, +415 s by wall clock.","ok"),
]

def tr_house():
    out=[]
    for t,d,k in HOUSE:
        p = 'pill-ok' if k=='ok' else 'pill-warn'
        lab = 'clean' if k=='ok' else 'open'
        out.append(f'<tr><td class="c-st"><span class="pill {p}">{lab}</span></td>'
                   f'<td><div class="t-claim">{t}</div><div class="t-detail">{d}</div></td></tr>')
    return "".join(out)

HTML = f"""<title>MetaOptimize Granularity Ledger</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root {{
  --paper:#f4f6f8; --surface:#ffffff; --surface-2:#eef1f5;
  --ink:#141a21; --ink-2:#3d4855; --muted:#6b7784; --faint:#98a2ae;
  --rule:#dbe0e7; --rule-2:#c6ccd5;
  --accent:#1c5c9e; --accent-soft:#e4edf7;
  --ok:#0c7350; --ok-soft:#e0f0e9;
  --bad:#a92637; --bad-soft:#f8e6e8;
  --warn:#8d5c0d; --warn-soft:#f7edda;
  --series-a:#1c5c9e; --series-b:#a92637;
  --shadow:0 1px 2px rgba(20,26,33,.05), 0 6px 20px -12px rgba(20,26,33,.22);
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --paper:#0d1116; --surface:#141a21; --surface-2:#1a212a;
    --ink:#e7ebf0; --ink-2:#b6c0cb; --muted:#8b95a2; --faint:#6b7683;
    --rule:#242c36; --rule-2:#323c48;
    --accent:#6ba7e4; --accent-soft:#16293d;
    --ok:#3fb787; --ok-soft:#12291f;
    --bad:#e8717f; --bad-soft:#2c1519;
    --warn:#d5a24a; --warn-soft:#2a2113;
    --series-a:#6ba7e4; --series-b:#e8717f;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 6px 20px -12px rgba(0,0,0,.7);
  }}
}}
:root[data-theme="dark"] {{
  --paper:#0d1116; --surface:#141a21; --surface-2:#1a212a;
  --ink:#e7ebf0; --ink-2:#b6c0cb; --muted:#8b95a2; --faint:#6b7683;
  --rule:#242c36; --rule-2:#323c48;
  --accent:#6ba7e4; --accent-soft:#16293d;
  --ok:#3fb787; --ok-soft:#12291f;
  --bad:#e8717f; --bad-soft:#2c1519;
  --warn:#d5a24a; --warn-soft:#2a2113;
  --series-a:#6ba7e4; --series-b:#e8717f;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 6px 20px -12px rgba(0,0,0,.7);
}}

* {{ box-sizing:border-box; }}
body {{
  background:var(--paper); color:var(--ink);
  font-family:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  font-size:15px; line-height:1.55; margin:0;
  -webkit-font-smoothing:antialiased;
}}
.wrap {{ max-width:1080px; margin:0 auto; padding:0 28px 96px; }}

/* ---- masthead ---- */
header.mast {{ padding:56px 0 30px; border-bottom:2px solid var(--ink); }}
.eyebrow {{
  font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--muted); margin:0 0 14px;
  display:flex; gap:14px; flex-wrap:wrap; align-items:center;
}}
.eyebrow .dot {{ color:var(--rule-2); }}
h1 {{
  font-family:Newsreader,Georgia,serif; font-weight:500; font-size:clamp(34px,5.2vw,52px);
  line-height:1.07; letter-spacing:-.015em; margin:0 0 16px; text-wrap:balance;
}}
.standfirst {{
  font-family:Newsreader,Georgia,serif; font-size:19px; line-height:1.5; color:var(--ink-2);
  max-width:62ch; margin:0;
}}
.standfirst strong {{ color:var(--ink); font-weight:600; }}

/* ---- counters ---- */
.rail {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(128px,1fr));
  gap:0; border-bottom:1px solid var(--rule); margin-bottom:8px;
}}
.stat {{ padding:22px 20px 20px; border-right:1px solid var(--rule); }}
.stat:last-child {{ border-right:none; }}
.stat .n {{
  font-family:"IBM Plex Mono",monospace; font-size:27px; font-weight:500;
  letter-spacing:-.02em; font-variant-numeric:tabular-nums; line-height:1.1; display:block;
}}
.stat .k {{
  font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.11em;
  text-transform:uppercase; color:var(--muted); margin-top:7px; display:block;
}}

/* ---- sections ---- */
section {{ margin-top:56px; }}
.sechead {{ display:flex; align-items:baseline; gap:14px; margin-bottom:6px; flex-wrap:wrap; }}
h2 {{
  font-family:Newsreader,Georgia,serif; font-weight:500; font-size:27px;
  letter-spacing:-.01em; margin:0; line-height:1.2;
}}
.seckey {{
  font-family:"IBM Plex Mono",monospace; font-size:10.5px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--faint);
}}
.deck {{ color:var(--ink-2); max-width:66ch; margin:0 0 20px; font-size:14.5px; }}

/* ---- tables ---- */
.tscroll {{ overflow-x:auto; border-top:1px solid var(--ink); border-bottom:1px solid var(--rule); }}
table {{ width:100%; border-collapse:collapse; min-width:640px; }}
th {{
  font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--muted); text-align:left; font-weight:500;
  padding:10px 14px 10px 0; border-bottom:1px solid var(--rule);
}}
td {{ padding:14px 14px 14px 0; border-bottom:1px solid var(--rule); vertical-align:top; }}
tr:last-child td {{ border-bottom:none; }}
.t-claim {{ font-weight:500; color:var(--ink); font-size:14.5px; }}
.t-detail {{ color:var(--ink-2); font-size:13.5px; margin-top:4px; line-height:1.5; }}
.c-st {{ width:74px; padding-right:8px; }}
.c-mono, .c-cite, .c-num {{ font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums; }}
.c-mono {{ font-size:12.5px; color:var(--ink-2); white-space:nowrap; }}
.c-cite {{ font-size:11.5px; color:var(--faint); white-space:nowrap; width:88px; text-align:right; padding-right:0; }}
.c-num {{ font-size:13px; color:var(--ink-2); white-space:nowrap; }}
.c-tag {{ font-weight:600; color:var(--accent); font-size:13px; letter-spacing:.03em; }}
.c-cost {{ text-align:right; color:var(--muted); }}
code {{
  font-family:"IBM Plex Mono",monospace; font-size:.885em;
  background:var(--surface-2); padding:.1em .35em; border-radius:2px; color:var(--ink);
}}

/* ---- pills ---- */
.pill {{
  font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.08em; text-transform:uppercase;
  padding:3px 7px; border-radius:2px; font-weight:500; white-space:nowrap; display:inline-block;
}}
.pill-ok {{ background:var(--ok-soft); color:var(--ok); }}
.pill-bad {{ background:var(--bad-soft); color:var(--bad); }}
.pill-warn {{ background:var(--warn-soft); color:var(--warn); }}

/* ---- figures ---- */
figure {{
  margin:0 0 8px; background:var(--surface); border:1px solid var(--rule);
  border-radius:3px; padding:20px 20px 8px; box-shadow:var(--shadow); overflow-x:auto;
}}
figure svg {{ width:100%; height:auto; min-width:560px; display:block; }}
figcaption {{
  font-size:13px; color:var(--ink-2); padding:12px 2px 10px; border-top:1px solid var(--rule);
  margin-top:8px; line-height:1.5;
}}
figcaption b {{ color:var(--ink); font-weight:600; }}
.figkey {{
  display:flex; gap:18px; flex-wrap:wrap; font-family:"IBM Plex Mono",monospace;
  font-size:11px; color:var(--muted); margin-bottom:14px; letter-spacing:.02em;
}}
.figkey i {{ display:inline-block; width:13px; height:3px; vertical-align:middle; margin-right:6px; border-radius:2px; }}
.k-a {{ background:var(--series-a); }} .k-b {{ background:var(--series-b); }}
.k-tr {{ background:var(--rule-2); }}

/* svg classes */
.grid {{ stroke:var(--rule); stroke-width:1; }}
.tick {{ stroke:var(--rule-2); stroke-width:1; }}
.ax {{ font-family:"IBM Plex Mono",monospace; font-size:11px; fill:var(--muted); font-variant-numeric:tabular-nums; }}
.ax-r {{ text-anchor:end; }} .ax-c {{ text-anchor:middle; }} .ax-e {{ text-anchor:end; }}
.axtitle {{ font-family:"IBM Plex Sans",sans-serif; font-size:11.5px; fill:var(--muted); }}
.ln {{ fill:none; stroke-width:2; stroke-linejoin:round; stroke-linecap:round; }}
.ln-a {{ stroke:var(--series-a); }} .ln-b {{ stroke:var(--series-b); stroke-dasharray:5 3; }}
.dot {{ stroke:var(--surface); stroke-width:1.5; }}
.dot-a {{ fill:var(--series-a); }} .dot-b {{ fill:var(--series-b); }}
.ref-hi {{ stroke:var(--ok); stroke-width:1.2; stroke-dasharray:2 4; }}
.ref-lo {{ stroke:var(--faint); stroke-width:1.2; stroke-dasharray:2 4; }}
.reflab {{ font-family:"IBM Plex Mono",monospace; font-size:11px; fill:var(--muted); }}
.note {{ font-family:"IBM Plex Sans",sans-serif; font-size:12.5px; font-weight:600; fill:var(--ink); }}
.note-s {{ font-family:"IBM Plex Mono",monospace; font-size:11px; fill:var(--bad); }}
.lead {{ stroke:var(--rule-2); stroke-width:1; }}
.brk {{ stroke:var(--bad); stroke-width:2; }}
.gapband {{ fill:var(--accent-soft); }}
.bar {{ shape-rendering:crispEdges; }}
.bar-train {{ fill:var(--rule-2); }}
.bar-win {{ fill:var(--ok); }} .bar-hi {{ fill:var(--accent); }}
.bar-null {{ fill:var(--bad); }} .bar-lo {{ fill:var(--faint); }}
.bar-base {{ fill:var(--rule-2); }}
.rowname {{ font-family:"IBM Plex Mono",monospace; font-size:13px; font-weight:600; fill:var(--ink); }}
.rowsub {{ font-family:"IBM Plex Mono",monospace; font-size:10.5px; fill:var(--muted); }}
.val {{ font-family:"IBM Plex Mono",monospace; font-size:11.5px; fill:var(--ink); font-variant-numeric:tabular-nums; }}
.val-dim {{ fill:var(--muted); }}

/* ---- callout ---- */
.callout {{
  border-left:3px solid var(--bad); background:var(--surface); padding:18px 22px;
  margin:24px 0 0; border-radius:0 3px 3px 0; box-shadow:var(--shadow);
}}
.callout.pos {{ border-left-color:var(--ok); }}
.callout h3 {{
  font-family:Newsreader,Georgia,serif; font-weight:600; font-size:17px; margin:0 0 6px; letter-spacing:-.005em;
}}
.callout p {{ margin:0; color:var(--ink-2); font-size:14px; max-width:70ch; }}

/* ---- placement ---- */
.venues {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1px; background:var(--rule); border:1px solid var(--rule); border-radius:3px; overflow:hidden; }}
.venue {{ background:var(--surface); padding:20px; }}
.venue .vn {{ font-family:Newsreader,Georgia,serif; font-size:19px; font-weight:600; margin-bottom:2px; }}
.venue .vp {{ font-family:"IBM Plex Mono",monospace; font-size:26px; font-variant-numeric:tabular-nums; letter-spacing:-.02em; margin:6px 0 8px; }}
.venue .vd {{ font-size:13px; color:var(--ink-2); line-height:1.5; }}
.meter {{ height:4px; background:var(--surface-2); border-radius:2px; overflow:hidden; margin:10px 0 12px; }}
.meter i {{ display:block; height:100%; border-radius:2px; }}

footer {{
  margin-top:64px; padding-top:22px; border-top:1px solid var(--rule);
  font-family:"IBM Plex Mono",monospace; font-size:11.5px; color:var(--faint); line-height:1.8;
}}
@media (max-width:640px) {{
  .wrap {{ padding:0 18px 64px; }}
  header.mast {{ padding-top:36px; }}
  .stat {{ border-right:none; border-bottom:1px solid var(--rule); }}
}}
@media (prefers-reduced-motion:no-preference) {{ html {{ scroll-behavior:smooth; }} }}
</style>

<div class="wrap">

<header class="mast">
  <p class="eyebrow">
    <span>Hierarchical MetaOptimize</span><span class="dot">/</span>
    <span>ALICE &#183; Leiden</span><span class="dot">/</span>
    <span>cycles 1&#8211;148</span><span class="dot">/</span>
    <span>CORRECTIONS 191</span>
  </p>
  <h1>What 2,761 runs actually established</h1>
  <p class="standfirst">Step-size granularity in MetaOptimize, audited end to end. <strong>Seven results hold.</strong> Nine died, including the one the project was named for. The strongest surviving finding is that <strong>1,536 of 11.2 million parameters</strong> carry the entire scalar-to-layerwise accuracy gap. Three batches are in flight to decide what that fact is about.</p>
</header>

<div class="rail">
  <div class="stat"><span class="n">2,761</span><span class="k">runs</span></div>
  <div class="stat"><span class="n">2,914</span><span class="k">GPU-hours</span></div>
  <div class="stat"><span class="n">191</span><span class="k">corrections</span></div>
  <div class="stat"><span class="n" style="color:var(--ok)">7</span><span class="k">results hold</span></div>
  <div class="stat"><span class="n" style="color:var(--bad)">9</span><span class="k">results dead</span></div>
  <div class="stat"><span class="n" style="color:var(--accent)">36</span><span class="k">jobs in flight</span></div>
</div>

<section>
  <div class="sechead"><h2>The headline, stated against us</h2><span class="seckey">CORRECTIONS 171 &#183; 175</span></div>
  <div class="callout">
    <h3>MetaOptimize does not beat a tuned plain baseline.</h3>
    <p>Nobody in this corpus had run a tuned non-meta baseline outside CIFAR-10. On CIFAR-100 it now exists, and the family sits <strong>5.699 pp below</strong> tuned SGD &#8212; 18.80 SE, measured in batch &#8212; with every rung of the SGD learning-rate ladder, including the worst, beating the best MetaOptimize cell the corpus owns. On CIFAR-10 the deficit is 1.46 pp and does not close with budget.</p>
  </div>
  <div class="callout pos">
    <h3>That reframes the contribution rather than ending it.</h3>
    <p>The paper this campaign can honestly write is not &#8220;MetaOptimize wins.&#8221; It is a partition audit: <em>within</em> the method, how the step-size parameters are grouped is worth 25&#8211;47 pp, the grouping that matters is a handful of named tensors rather than a count, and the whole effect survives tuning each arm at its own optimum.</p>
  </div>
</section>

<section>
  <div class="sechead"><h2>Results that hold</h2><span class="seckey">each measured within one batch</span></div>
  <p class="deck">Batch is the unit of replication in this campaign &#8212; F(62,85) = 5.47, p = 6.9e-13 &#8212; while seed is null, F(11,1976) = 0.152. Every comparison below is in-batch. Primary metric is <code>plateau5</code>, the mean of the last five test epochs.</p>
  <div class="tscroll"><table>
    <thead><tr><th></th><th>Finding</th><th>Evidence</th><th>Entry</th></tr></thead>
    <tbody>{tr_holds()}</tbody>
  </table></div>
</section>

<section>
  <div class="sechead"><h2>Cut position, not group count</h2><span class="seckey">figure 1</span></div>
  <p class="deck">Split the 62 tensors of ResNet-18 into exactly two step-size groups, and slide the boundary. Accuracy swings 25.07 pp across cut positions at fixed group count &#8212; and adding groups does not buy that. The peak sits at <code>k = 49</code> and does not move when the horizon is extended 7.7&#215; on fresh seeds.</p>
  <div class="figkey"><span><i class="k-a"></i>100 epochs &#183; cpk1</span><span><i class="k-b"></i>772 epochs &#183; cpk3, fresh seeds</span></div>
  <figure>
    {chart_cutpos()}
    <figcaption><b>Three seeds per point, all in batch.</b> The 772-epoch series re-runs the consecutive grid k = 45&#8230;50, turning cpk2&#8217;s two-tensor steps into five single-tensor steps. The forecast built on cpk1&#8217;s curve predicted three rank swaps at the longer horizon; <b>zero occurred</b>. Note the asymmetry: three tensors past the peak costs 18.3 pp, and by k = 55 the partition is worth less than no partition at all.</figcaption>
  </figure>
</section>

<section>
  <div class="sechead"><h2>1,536 parameters carry the gap</h2><span class="seckey">figure 2 &#183; CORRECTIONS 185, 187</span></div>
  <p class="deck">A probe on the scalar trajectory found three <code>layer4</code> BatchNorm scales &#8212; <code>layer4.0.bn2.weight</code>, <code>layer4.0.shortcut.1.weight</code>, <code>layer4.1.bn2.weight</code>, 0.014 % of the model &#8212; carrying the Lion sign against the other 59 tensors on 944 of 944 pinned records. <code>ciso1</code> tested that causally: move exactly those three into their own step-size group and nothing else.</p>
  <div class="figkey"><span><i class="k-tr"></i>train</span><span><i class="k-a"></i>test &#8212; layerwise ceiling</span><span><i class="k-b"></i>test &#8212; at the scalar floor</span></div>
  <figure>
    {chart_iso()}
    <figcaption><b>ISO reaches the layerwise ceiling by freeing 1,536 of 11,220,132 parameters</b> &#8212; +46.93 pp over scalar, +62.10 SE, statistically indistinguishable from full layerwise (+1.18 pp = 1.57 SE). Their layer-2 structural homologues, isolated at identical group sizes, recover <b>nothing</b> (&#8722;0.06 pp). One tensor alone recovers +41.47 pp. ISO also reaches that ceiling with <b>4.6 pp less train accuracy</b> than layerwise &#8212; unexplained, and being measured now.</figcaption>
  </figure>
  <div class="callout">
    <h3>What this does <em>not</em> yet establish.</h3>
    <p>ISO and CTRL differ in tensor identity <em>and</em> network depth <em>and</em> isolated parameter count at once, so the design cannot say which is operative &#8212; ResNet-18 has exactly five 512-wide BatchNorm scales and all five are in <code>layer4</code>, so a depth-matched, size-matched, carrier-free control had to be built separately. That arm is running. The verdict stands at <code>UNRESOLVED-PARTIAL</code> until it lands.</p>
  </div>
</section>

<section>
  <div class="sechead"><h2>The gap survives tuning</h2><span class="seckey">figure 3 &#183; RULE 11 &#183; CORRECTIONS 174</span></div>
  <p class="deck">The obvious objection to any granularity result is that one arm was simply run further from its own optimum. Comparing each arm at its <em>own</em> best meta step size instead of a shared one shrinks the gap &#8212; but does not remove it. It retains 74.4 % of its size.</p>
  <div class="figkey"><span><i class="k-a"></i>layerwise &#183; m = 62</span><span><i class="k-b"></i>scalar &#183; m = 1</span></div>
  <figure>
    {chart_rule11()}
    <figcaption><b>Both arms peak at ms = 1e-4, and the gap there is 35.29 pp</b> against 47.46 pp at the shared ms = 1e-3 &#8212; ratio 0.7436. Ten rungs, three seeds each, in batch. This closes RULE 11 for scalar-vs-layerwise on CIFAR-100. It does <b>not</b> overturn the earlier <code>hz9</code> result, which was never tested here: different dataset, different contrast, and a gap 41&#215; smaller.</figcaption>
  </figure>
</section>

<section>
  <div class="sechead"><h2>The denominator nobody had measured</h2><span class="seckey">figure 4 &#183; CORRECTIONS 171, 175</span></div>
  <p class="deck">Every granularity number above is a comparison <em>within</em> MetaOptimize. This is the comparison against the plain optimiser the method is implicitly measured against &#8212; and until cycle 141 it did not exist anywhere in the corpus outside CIFAR-10.</p>
  <figure>
    {chart_denom()}
    <figcaption><b>The tuned SGD optimum is interior</b> (argmax at lr = 0.1, not at a ladder edge), so the baseline is honest rather than under-tuned. The gap is <b>5.699 pp = 18.80 SE</b>, more than three times the CIFAR-10 deficit. The first registered scorer for this batch crashed unconditionally in its scoring path; it was frozen unedited under RULE 16 and a successor re-derived the number line for line.</figcaption>
  </figure>
</section>

<section>
  <div class="sechead"><h2>What the carriers have in common</h2><span class="seckey">figure 5 &#183; CORRECTIONS 188.3, 189.2</span></div>
  <p class="deck">ResNet-18 has exactly five 512-wide BatchNorm scales and all five sit in <code>layer4</code>. Three are the carriers. Reading them against <code>BasicBlock.forward</code> on the live model gives a sharp split &#8212; and reading them against the probe gives an equally sharp one, on a different axis.</p>
  <div class="figkey"><span><i class="k-b"></i>carrier &#183; output is a summand of a residual add</span><span><i class="k-tr"></i>non-carrier &#183; sits behind a ReLU, feeds no add</span></div>
  <figure>
    {chart_layer4()}
    <figcaption><b>The three carriers are exactly the 512-wide BatchNorm scales whose output enters a residual addition; the two non-carriers are exactly the mid-branch <code>bn1</code> scales. Three-two, no exceptions.</b> They are also ranks 1, 2 and 3 of 62 by meta-gradient magnitude, while every 512-parameter <code>layer4</code> non-carrier sits <em>below</em> the median tensor. Recorded as a hypothesis, not a result.</figcaption>
  </figure>
  <div class="callout">
    <h3>Two confounds, both stated before the arms were launched.</h3>
    <p>On a ResNet, &#8220;feeds a residual add&#8221; and &#8220;is the deepest, widest BatchNorm scale&#8221; are the same measurement seen twice &#8212; the campaign has never manipulated residual structure, which is why <code>cvg1</code> runs an architecture with no residual additions at all. Separately, the best carrier-free triple that exists on this model still carries <b>225&#215; less</b> meta-gradient mass than the carriers, so <code>cdep1</code> can rule out &#8220;any three matched <code>layer4</code> BatchNorm parameters&#8221; but <em>cannot</em> separate tensor identity from term magnitude. No batch on this architecture can.</p>
  </div>
</section>

<section>
  <div class="sechead"><h2>Results that died</h2><span class="seckey">refuted, withdrawn or superseded</span></div>
  <p class="deck">Recording these is the point of the ledger. Roughly a dozen of my own claims were corrected in place this week, including three index-convention errors and one mass prediction that came out backwards.</p>
  <div class="tscroll"><table>
    <thead><tr><th></th><th>Claim</th><th>Batch</th><th>Entry</th></tr></thead>
    <tbody>{tr_dies()}</tbody>
  </table></div>
</section>

<section>
  <div class="sechead"><h2>Mechanism ledger</h2><span class="seckey">seventeen registered &#183; fifteen dead &#183; two live</span></div>
  <p class="deck">Why granularity matters at all &#8212; not that it does. Each candidate was pre-registered with its bars and branch map before any run of its batch existed, and scored by a committed, unedited scorer.</p>
  <div class="tscroll"><table>
    <thead><tr><th>#</th><th>Candidate</th><th></th><th>Standing</th><th>Entry</th></tr></thead>
    <tbody>{tr_cand()}</tbody>
  </table></div>
</section>

<section>
  <div class="sechead"><h2>Running now</h2><span class="seckey">launched this cycle</span></div>
  <div class="tscroll"><table>
    <thead><tr><th>Arm</th><th>What it is</th><th>What it decides</th><th>Cost</th></tr></thead>
    <tbody>{tr_running()}</tbody>
  </table></div>
</section>

<section>
  <div class="sechead"><h2>Corpus</h2><span class="seckey">results/all_runs.csv</span></div>
  <p class="deck">Every one of the 2,761 rows is ResNet &#8212; eleven <code>network</code> values, zero exceptions. That is the campaign&#8217;s single largest scope limit and the objection every tensor-level finding shares: &#8220;three <code>layer4</code> BatchNorm scales&#8221; is a claim about one architecture&#8217;s parameter list until it is shown elsewhere.</p>
  <div class="tscroll"><table>
    <thead><tr><th>Dataset</th><th>Runs</th><th>Architectures</th></tr></thead>
    <tbody>{tr_corpus()}</tbody>
  </table></div>
  <div class="callout pos">
    <h3>It was never an infrastructure limit &#8212; and now it cannot be excused as one.</h3>
    <p>Scoping the port found the harness is architecture-agnostic: <code>train.py</code> touches the network through one <code>build_network</code> call, <code>HF.py</code> derives every granularity from <code>named_parameters()</code> and holds no architecture logic, and neither the args guard nor the launcher library carries a tensor-count assumption. A new architecture costs one <code>if</code> and one class. <code>VGG11_bn_c100</code> is built, proved additive byte-for-byte, backward-compatible across all eleven existing network values, and launched. The caveat still stands on every finding until <code>cvg1</code> lands &#8212; but it is now measurable rather than structural.</p>
  </div>
</section>

<section>
  <div class="sechead"><h2>Publication placement</h2><span class="seckey">assessed against the four-lens rubric</span></div>
  <p class="deck">An honest read, not an encouraging one. The gap between these two columns is the mechanism &#8212; a confirmed causal account plus one non-ResNet architecture is roughly what moves the middle number.</p>
  <div class="venues">
    <div class="venue">
      <div class="vn">TMLR</div>
      <div class="vp" style="color:var(--ok)">75&#8211;80&#8202;%</div>
      <div class="meter"><i style="width:78%;background:var(--ok)"></i></div>
      <div class="vd">Claims-and-evidence venue. The audit discipline, the negative denominator result and the correction ledger are assets here rather than liabilities.</div>
    </div>
    <div class="venue">
      <div class="vn">ICML &#8212; cut-position paper</div>
      <div class="vp" style="color:var(--warn)">10&#8211;15&#8202;%</div>
      <div class="meter"><i style="width:13%;background:var(--warn)"></i></div>
      <div class="vd">Rises to <strong>25&#8211;30&#8202;%</strong> with a confirmed mechanism <em>and</em> a non-BatchNorm architecture. Both are in flight.</div>
    </div>
    <div class="venue">
      <div class="vn">ICML &#8212; current manuscript</div>
      <div class="vp" style="color:var(--bad)">~3&#8202;%</div>
      <div class="meter"><i style="width:3%;background:var(--bad)"></i></div>
      <div class="vd"><code>paper/paper.tex</code> predates all of this week&#8217;s work and still leads with a claim the denominator result contradicts.</div>
    </div>
  </div>
</section>

<section>
  <div class="sechead"><h2>Housekeeping</h2><span class="seckey">stated rather than quietly carried</span></div>
  <div class="tscroll"><table>
    <thead><tr><th></th><th>Item</th></tr></thead>
    <tbody>{tr_house()}</tbody>
  </table></div>
</section>

<footer>
  Compiled from <code>results/all_runs.csv</code> at 2,761 rows and <code>docs/CORRECTIONS.md</code> at entry 191. HEAD <code>712ff65</code>.<br>
  Primary metric <code>plateau5</code>; the CSV <code>plateau</code> column is barred as primary and <code>best_test</code> is not a plateau.<br>
  Tensor indices are 1-based. Every comparison in-batch. Numbers re-derived for this report, not copied from prose.
</footer>

</div>
"""

open(OUT,"w").write(HTML)
print("wrote", OUT, len(HTML), "bytes")
