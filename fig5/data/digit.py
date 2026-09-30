import sys,numpy as np, emfrender as E, collections
def digit(fn,verbose=True):
    E.render(fn,'/tmp/emf/x.png'); pr=E.PRIMS
    lines=[p for p in pr if 'P' in p and 'text' not in p]
    seg=[p for p in lines if len(p['P'])==2]
    hl=[p for p in seg if abs(p['P'][0,1]-p['P'][1,1])<1e-3]; vl=[p for p in seg if abs(p['P'][0,0]-p['P'][1,0])<1e-3]
    Lh=max(np.ptp(p['P'][:,0]) for p in hl); Lv=max(np.ptp(p['P'][:,1]) for p in vl)
    H=[p for p in hl if np.ptp(p['P'][:,0])>0.95*Lh]; V=[p for p in vl if np.ptp(p['P'][:,1])>0.95*Lv]
    x0=min(p['P'][0,0] for p in V); x1=max(p['P'][0,0] for p in V); y0=min(p['P'][0,1] for p in H); y1=max(p['P'][0,1] for p in H)
    rects=H+V
    tk=[p for p in lines if len(p['P'])==2]
    L=np.array([np.hypot(*(p['P'][1]-p['P'][0])) for p in tk])
    c=collections.Counter(np.round(L,2))
    maj=max(k for k in c if c[k]>=3 and k<10)
    xt=sorted(set(np.round([p['P'][0][0] for p,l in zip(tk,L) if abs(p['P'][0][0]-p['P'][1][0])<1e-3 and abs(l-maj)<.05 and abs(p['P'][:,1].min()-y0)<.3],2)))
    yt=sorted(set(np.round([p['P'][0][1] for p,l in zip(tk,L) if abs(p['P'][0][1]-p['P'][1][1])<1e-3 and abs(l-maj)<.05 and abs(p['P'][:,0].min()-x0)<.3],2)))
    texts=[(p['text'],p['P']) for p in pr if 'text' in p]
    m=[p for p in pr if 'marker' in p]
    curves=[p for p in lines if len(p['P'])>5 and not any(np.allclose(p['P'].mean(0),q['marker'],atol=0.6) for q in m)]
    if verbose:
        print(fn,'frame',round(x0,2),round(y0,2),round(x1,2),round(y1,2)); print(' xmaj',xt); print(' ymaj',yt)
        print(' markers',collections.Counter(p['pen'] for p in m))
        print(' curves',collections.Counter((p['pen'],len(p['P'])) for p in curves))
    return dict(frame=(x0,y0,x1,y1),xt=xt,yt=yt,markers=m,curves=curves,texts=texts)
if __name__=='__main__':
    for f in sys.argv[1:]: digit(f)
