import struct,sys,numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly
def I(d,o,n=1,f='i'): return struct.unpack_from('<'+f*n,d,o)
def bez(pts):
    out=[pts[0]]
    for k in range(1,len(pts)-2,3):
        p0=np.array(out[-1]);p1,p2,p3=map(np.array,pts[k:k+3])
        for t in np.linspace(0,1,8)[1:]:
            out.append(tuple((1-t)**3*p0+3*(1-t)**2*t*p1+3*(1-t)*t*t*p2+t**3*p3))
    return out
PRIMS=[]
def render(fn,out,dump=False):
    PRIMS.clear()
    d=open(fn,'rb').read()
    objs={}; st=dict(xf=np.eye(3),pen=('#000',1,True),brush=None,font=(12,0),tc='#000',win=[0,0,1,1],vp=[0,0,1,1],cur=(0,0))
    stack=[]; texts=[]
    fig,ax=plt.subplots(figsize=(10,8)); inpath=False; path=[]; cursub=[]
    def T(pts):
        p=np.array(pts,float); P=np.c_[p,np.ones(len(p))]@st['xf']
        wx,wy,wex,wey=st['win']; vx,vy,vex,vey=st['vp']
        x=(P[:,0]-wx)*vex/wex+vx; y=(P[:,1]-wy)*vey/wey+vy
        return np.c_[x,-y]
    def col(c): return '#%02x%02x%02x'%(c&255,(c>>8)&255,(c>>16)&255)
    def stroke(pts,closed=False,fill=False):
        P=T(pts)
        PRIMS.append(dict(P=P,pen=st['pen'][0] if st['pen'][2] else None,brush=st['brush'] if fill else None,closed=closed))
        if fill and st['brush']: ax.add_patch(MPoly(P,closed=True,fc=st['brush'],ec='none',lw=0))
        c,w,vis=st['pen']
        if vis:
            if closed: P=np.vstack([P,P[:1]])
            ax.plot(P[:,0],P[:,1],color=c,lw=0.6)
    i=0
    while i<len(d):
        t,s=I(d,i,2,'I')
        if s==0:break
        b=i+8
        if t==36:
            m=I(d,b,6,'f');mode=I(d,b+24,1,'I')[0]
            X=np.array([[m[0],m[1],0],[m[2],m[3],0],[m[4],m[5],1]])
            if mode==1: st['xf']=np.eye(3)
            elif mode==2: st['xf']=X@st['xf']
            elif mode==3: st['xf']=st['xf']@X
            elif mode==4: st['xf']=X
        elif t==35:
            m=I(d,b,6,'f');st['xf']=np.array([[m[0],m[1],0],[m[2],m[3],0],[m[4],m[5],1]])
        elif t==9: st['win'][2:]=I(d,b,2)
        elif t==10: st['win'][:2]=I(d,b,2)
        elif t==11: st['vp'][2:]=I(d,b,2)
        elif t==12: st['vp'][:2]=I(d,b,2)
        elif t==33: stack.append({k:(v.copy() if hasattr(v,'copy') else v) for k,v in st.items()})
        elif t==34:
            n=I(d,b)[0]; 
            for _ in range(-n if n<0 else 1):
                if stack: st.update(stack.pop())
        elif t==95:
            ih=I(d,b,1,'I')[0]; style,w,bs,c=I(d,b+20,4,'I'); objs[ih]=('pen',(col(c),w,(style&15)!=5))
        elif t==38:
            ih,style,w,_,c=I(d,b,5,'I'); objs[ih]=('pen',(col(c),w,(style&15)!=5))
        elif t==39:
            ih,style,c,h=I(d,b,4,'I'); objs[ih]=('brush',None if style==1 else col(c))
        elif t==82:
            ih=I(d,b,1,'I')[0]; h,w,esc=I(d,b+4,3); objs[ih]=('font',(abs(h),esc))
        elif t==37:
            ih=I(d,b,1,'I')[0]
            if ih&0x80000000:
                k=ih&0x7fffffff
                if k==8: st['pen']=('#000',0,False)
                elif k==7: st['pen']=('#000',1,True)
                elif k==6: st['pen']=('#fff',1,True)
                elif k==5: st['brush']=None
                elif k==0: st['brush']='#fff'
                elif k==4: st['brush']='#000'
            elif ih in objs:
                k,v=objs[ih]
                st[k]=v
        elif t==40: pass
        elif t==24: st['tc']=col(I(d,b,1,'I')[0])
        elif t in (87,86,85,88,89):
            n=I(d,b+16,1,'I')[0]; pts=list(zip(*[iter(I(d,b+20,2*n,'h'))]*2))
            if t==85: PRIMS.append(dict(marker=T(pts).mean(0),pen=st['pen'][0],brush=st['brush'])); pts=bez(pts)
            if t in (88,89): pts=[st['cur']]+ (bez([st['cur']]+pts)[1:] if t==88 else pts)
            if pts: st['cur']=pts[-1]
            if inpath:
                if t in (88,89): cursub.extend(pts[1:])
                else: path.append(cursub) if cursub else None; cursub=list(pts)
            else: stroke(pts,closed=(t==86),fill=(t==86))
        elif t in (90,91):
            npl,cnt=I(d,b+16,2,'I'); counts=I(d,b+24,npl,'I'); o=b+24+4*npl
            for c in counts:
                pts=list(zip(*[iter(I(d,o,2*c,'h'))]*2)); o+=4*c
                stroke(pts,closed=(t==91),fill=(t==91))
        elif t==27:
            st['cur']=I(d,b,2)
            if inpath:
                if cursub: path.append(cursub)
                cursub=[st['cur']]
        elif t==54:
            p=I(d,b,2)
            if inpath: cursub.append(p)
            else: stroke([st['cur'],p])
            st['cur']=p
        elif t==59: inpath=True; path=[]; cursub=[]
        elif t==60:
            inpath=False
            if cursub: path.append(cursub); cursub=[]
        elif t in (62,63,64):
            for sp in path:
                if len(sp)>1: stroke(sp,closed=(t!=64),fill=(t!=64))
        elif t in (42,43):
            l,tp,r,bt=I(d,b,4)
            if t==43: stroke([(l,tp),(r,tp),(r,bt),(l,bt)],True,True)
            else:
                th=np.linspace(0,2*np.pi,20); stroke(list(zip((l+r)/2+(r-l)/2*np.cos(th),(tp+bt)/2+(bt-tp)/2*np.sin(th))),True,True)
        elif t==84:
            ref=I(d,b+28,2); nch,offs=I(d,b+36,2,'I')
            txt=d[i+offs:i+offs+2*nch].decode('utf-16le','replace')
            P=T([ref])[0]; h,esc=st['font']
            texts.append((txt,P,esc)); PRIMS.append(dict(text=txt,P=P,esc=esc))
            ax.text(P[0],P[1],txt,fontsize=7,rotation=esc/10,color=st['tc'],va='top',ha='left')
        i+=s
    ax.set_aspect('equal'); ax.axis('off')
    if texts:
        P=np.array([t[1] for t in texts]); ax.set_xlim(P[:,0].min()-5,P[:,0].max()+25); ax.set_ylim(P[:,1].min()-8,P[:,1].max()+8); fig.savefig(out,dpi=150,bbox_inches='tight'); plt.close(fig)
    if dump:
        for tx in texts: print(repr(tx[0]),np.round(tx[1]),tx[2])
if __name__=='__main__':
  for fn in sys.argv[1:]:
    render(fn,fn.replace('.emf','_r.png'))
