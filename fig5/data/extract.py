import numpy as np, digit, json, collections
def lin(a,b,va,vb): return lambda u:(u-a)/(b-a)*(vb-va)+va
cal={
 'image1':('lin',(24.57,80.32,-100,100),'lin',(-76.94,-13.54,0,1000)),
 'image4':None,
 'image2':('lin',(24.57,84.1,-100,100),'log',(-78.28,-17.56,-4,0)),
 'image3':('lin',(24.57,84.1,-100,100),'log',(-78.28,-17.56,-4,0)),
 'image10':('lin',(24.57,84.1,-100,100),'log',(-75.28,-13.23,-2,0)),
 'image5':('lin',(19.29,89.06,0,10),'log',(-64.65,-19.21,-3,0)),
 'image6':('lin',(19.29,89.06,0,10),'log',(-64.65,-19.21,-3,0)),
 'image7':('lin',(19.29,89.06,0,10),'log',(-64.65,-19.21,-3,0)),
 'image8':('lin',(0,1,0,1),'lin',(-59.96,-13.79,0,25)),
}
out={}
for k,c in cal.items():
    r=digit.digit(k+'.emf',False)
    if c is None:
        print(k,'frame',r['frame'],'xt',r['xt'],'yt',r['yt']); continue
    fx=lin(*c[1]); fy=lin(*c[3])
    tx=(lambda v:v) ; ty=(lambda v:10**v) if c[2]=='log' else (lambda v:v)
    D=collections.defaultdict(list)
    for m in r['markers']:
        D[m['pen']].append((fx(m['marker'][0]),ty(fy(m['marker'][1]))))
    C=collections.defaultdict(list)
    for cv in r['curves']:
        P=cv['P']; C[cv['pen']].append(np.c_[fx(P[:,0]),ty(fy(P[:,1]))].tolist())
    out[k]=dict(markers={kk:sorted(v) for kk,v in D.items()},curves=C)
json.dump(out,open('digitized.json','w'))
for k in out:
    print('==',k)
    for col,v in out[k]['markers'].items():
        print(' ',col,len(v),np.round(v,4).tolist()[:40])
