"""Independent nominal-CAD enclosure check using exterior subtraction.

Temporary port caps must cover only declared openings; they are audit helpers,
not physical candidate parts. No slicer or flow solver is called.
"""
from pathlib import Path
import argparse,hashlib,json
import cadquery as cq

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--assembly',type=Path,required=True)
parser.add_argument('--void',type=Path,required=True)
parser.add_argument('--caps',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
a=parser.parse_args()

def read(path):
 s=cq.importers.importStep(str(path)).val()
 assert s.isValid() and s.Solids(), str(path)
 return s

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def joined(shape):
 solids=shape.Solids()
 return solids[0].fuse(*solids[1:]).clean() if len(solids)>1 else solids[0]

assembly,void,caps=(read(path) for path in (a.assembly,a.void,a.caps))
assert len(void.Solids())==1, 'Intended void itself must be connected'
material=joined(assembly)
cap_material=joined(caps)
material_in_void=material.intersect(void).Volume()
target=void.cut(cap_material).clean()
assert target.isValid() and len(target.Solids())==1 and target.Volume()>0
sealed=material.fuse(cap_material).clean()
b=cq.Compound.makeCompound([sealed,target]).BoundingBox()
margin=10.0
extent=cq.Workplane('XY').box(b.xlen+2*margin,b.ylen+2*margin,b.zlen+2*margin,centered=False).translate((b.xmin-margin,b.ymin-margin,b.zmin-margin)).val()
free=extent.cut(sealed).clean()
assert free.isValid()
e=extent.BoundingBox()
records=[]; targets=[]
for index,solid in enumerate(free.Solids()):
 c=solid.BoundingBox()
 touches_exterior=any(abs(getattr(c,key)-getattr(e,key))<1e-4 for key in ('xmin','xmax','ymin','ymax','zmin','zmax'))
 overlap=solid.intersect(target).Volume()
 record={'component':index,'volume_mm3':solid.Volume(),'target_overlap_mm3':overlap,'touches_exterior_box':touches_exterior}
 records.append(record)
 if overlap>1e-4: targets.append((solid,record))
passed=material_in_void<1e-4 and len(targets)==1 and not targets[0][1]['touches_exterior_box']
difference=None
if len(targets)==1:
 measured=targets[0][0]
 difference={'unmodeled_enclosed_air_mm3':measured.cut(target).Volume(),'intended_air_missing_mm3':target.cut(measured).Volume()}
 passed=passed and all(abs(v)<max(1e-3,target.Volume()*1e-8) for v in difference.values())
port_checks=[]
# A sealed cavity alone does not prove that both named ports actually open.
# Remove exactly one temporary cap at a time; the same central air target
# must then reach exterior through that port. This rejects a blind terminal
# hidden under stock even when the fully capped volume matches perfectly.
cap_solids=caps.Solids()
for omitted,cap in enumerate(cap_solids):
 remaining=[item for index,item in enumerate(cap_solids) if index!=omitted]
 test_material=material.fuse(*remaining).clean() if remaining else material
 test_free=extent.cut(test_material).clean()
 assert test_free.isValid()
 hits=[]
 for solid in test_free.Solids():
  overlap=solid.intersect(target).Volume()
  if overlap<=1e-4:continue
  cb=solid.BoundingBox()
  outside=any(abs(getattr(cb,key)-getattr(e,key))<1e-4 for key in ('xmin','xmax','ymin','ymax','zmin','zmax'))
  hits.append({'target_overlap_mm3':overlap,'touches_exterior_box':outside})
 open_port=len(hits)==1 and hits[0]['touches_exterior_box']
 cb=cap.BoundingBox()
 port_checks.append({'omitted_cap_index':omitted,'cap_center_mm':list(cap.Center().toTuple()),
  'cap_bounds_mm':[cb.xmin,cb.ymin,cb.zmin,cb.xmax,cb.ymax,cb.zmax],
  'port_reaches_exterior_when_uncapped':bool(open_port),'target_components':hits})
 passed=passed and open_port
report={'passed':bool(passed),'input_sha256':{'assembly':digest(a.assembly),'intended_void':digest(a.void),'temporary_caps':digest(a.caps)},
 'auditor_sha256':digest(Path(__file__)),
 'method':'Expanded exterior box minus union of actual physical assembly and only declared port caps; identify candidate-air connected component',
 'physical_material_in_intended_void_mm3':material_in_void,'intended_void_after_port_caps_mm3':target.Volume(),
 'free_space_components':records,'actual_vs_intended_void':difference,
 'individual_port_opening_checks':port_checks,
 'qualification':'Nominal CAD enclosure and connectivity only. No measured seam seal, leakage, installed laptop contact, structural, airflow, acoustic or thermal result.'}
a.out.parent.mkdir(parents=True,exist_ok=True)
a.out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if not passed: raise SystemExit('Enclosure verification did not pass; inspect the reported geometry discrepancy.')
