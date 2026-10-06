"""Prove a geometry change added material only: for each named part, old minus new must be (near) empty.
Usage: cadpy check_no_removed_material.py <prev-dir> <part> [<part> ...]  -> writes generated/no-removed-material.json"""
import sys,json
from pathlib import Path
import cadquery as cq
HERE=Path(__file__).resolve().parent;prev=HERE/sys.argv[1];out={}
for name in sys.argv[2:]:
    old=cq.importers.importStep(str(prev/(name+'.step'))).val();new=cq.importers.importStep(str(HERE/'generated'/(name+'.step'))).val()
    removed=old.cut(new).clean();added=new.cut(old).clean()
    comps=[]
    for s in added.Solids():
        if s.Volume()<1:continue
        b=s.BoundingBox();comps.append({'volume_mm3':round(s.Volume(),1),'bounds':[[round(b.xmin,1),round(b.ymin,1),round(b.zmin,1)],[round(b.xmax,1),round(b.ymax,1),round(b.zmax,1)]]})
    out[name]={'removed_mm3':round(removed.Volume(),3),'added_mm3':round(added.Volume(),1),'added_components':sorted(comps,key=lambda c:-c['volume_mm3'])}
    print(name,'removed',out[name]['removed_mm3'],'added',out[name]['added_mm3'],'components',len(comps),flush=True)
(HERE/'generated'/'no-removed-material.json').write_text(json.dumps(out,indent=2)+'\n')
assert all(v['removed_mm3']<0.5 for v in out.values()),'material was removed somewhere'
print('NO MATERIAL REMOVED')
