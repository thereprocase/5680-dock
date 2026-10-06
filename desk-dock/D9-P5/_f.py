import numpy as np, cadquery as cq
DOWN={'splice-plate':(-1,0,0),'center-contact':(-1,0,0),'gap-trim':(-1,0,0),'align-aid-front':(1,0,0),'align-aid-top':(1,0,0),'align-aid-fan':(1,0,0)}
for nm,dn in DOWN.items():
    sp=cq.importers.importStep('generated/%s.step'%nm).val(); d=np.array(dn,dtype=float); up=-d
    bed=min((np.array(f.Center().toTuple())@up) for f in sp.Faces())
    bad=[]
    for f in sp.Faces():
        if f.Area()<0.3:continue
        try:n=f.normalAt(f.Center())
        except Exception:continue
        nv=np.array([n.x,n.y,n.z]);nv/=np.linalg.norm(nv)
        if nv@d<=0.7071:continue
        h=(np.array(f.Center().toTuple())@up)-bed
        if h<0.4:continue
        b=f.BoundingBox();bad.append((f.Area(),h,b.ymin,b.ymax,b.zmin,b.zmax))
    print('%-16s %d face(s) over 45 deg, %.0f mm2'%(nm,len(bad),sum(x[0] for x in bad)))
    for a,h,y0,y1,z0,z1 in sorted(bad,reverse=True)[:5]:print('      %7.1f mm2 %5.2f up  y %7.2f..%-7.2f z %6.2f..%-6.2f'%(a,h,y0,y1,z0,z1))
