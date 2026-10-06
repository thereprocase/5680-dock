"""Verify physical enclosure by sequential exterior subtraction, avoiding unions."""
from pathlib import Path
import cadquery as cq,json,hashlib
G=Path(__file__).resolve().parent/'generated'
def read(name):return cq.importers.importStep(str(G/name)).val()
results=[]
for i in (1,2):
    parts=read(f'M{i}-audit-material.step').Solids()
    target=read(f'M{i}-air.step').Solids()[0]
    caps=read(f'M{i}-port-caps.step').Solids()
    b=cq.Compound.makeCompound(parts+[target]+caps).BoundingBox()
    extent=cq.Workplane('XY').box(b.xlen+20,b.ylen+20,b.zlen+20,centered=False).translate((b.xmin-10,b.ymin-10,b.zmin-10)).val()
    e=extent.BoundingBox()
    def classify(remaining_caps):
        free=extent
        for part in parts+remaining_caps:free=free.cut(part).clean()
        assert free.isValid()
        hits=[]
        for solid in free.Solids():
            overlap=solid.intersect(target).Volume()
            if overlap<.01:continue
            bb=solid.BoundingBox()
            exterior=any(abs(getattr(bb,k)-getattr(e,k))<1e-4 for k in ('xmin','xmax','ymin','ymax','zmin','zmax'))
            hits.append({'volume_mm3':solid.Volume(),'target_overlap_mm3':overlap,'exterior':exterior})
        return hits
    closed=classify(caps)
    openings=[classify([c for j,c in enumerate(caps) if j!=k]) for k in range(2)]
    passed=len(closed)==1 and not closed[0]['exterior'] and all(len(h)==1 and h[0]['exterior'] for h in openings)
    result={'module':i,'passed':passed,'closed':closed,'each_port_open':openings,
            'physical_part_count':2,'ideal_exterior_fastener_seals':0,
            'method':'Subtract the two exported housing solids and each named port cap separately from an exterior box. No fastener or seal helper patches are used.',
            'scope':'Nominal closed housing with blind external fan-pin sockets. Printed seam leakage is not measured; sealant may be used for airtightness. No physical airflow result.'}
    (G/f'M{i}-enclosure-final.json').write_text(json.dumps(result,indent=2)+'\n')
    results.append(result)
    print(json.dumps(result),flush=True)
assert all(r['passed'] for r in results),'Unenclosed plenum'
