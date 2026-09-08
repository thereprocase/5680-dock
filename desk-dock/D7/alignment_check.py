"""D7 bearing-contact and open-intake geometry screen."""
from pathlib import Path
import json,math
import build
R=Path(__file__).resolve().parent
lap=next(a['shape'] for a in build.parts if a['name']=='Precision_5680_REFERENCE')
body=[a for a in build.parts if 'manifold' in a['name']]
liners=[a for a in build.parts if 'lid_bearing_liner' in a['name']]
checks=[]
for a in liners:
    # Faces touch the simplified lid; backing touches its supporting plenum.
    gap=lap.distance(a['shape']); backing=min(a['shape'].distance(b['shape']) for b in body)
    overlap=lap.intersect(a['shape']).Volume()
    assert gap<1e-5 and backing<1e-5 and overlap<1e-5,(a['name'],gap,backing,overlap)
    checks.append(dict(name=a['name'],lid_gap_mm=gap,backing_gap_mm=backing,overlap_mm3=overlap))
lo,hi=build.contacts['intake_window_case_relative_bounds_mm']
# Thin test slab outside the OEM underside, spanning the whole intake window.
slab=build.leaned(build.box(lo[0],lo[1]-5,build.H+lo[2],hi[0]-lo[0],2,hi[2]-lo[2]).val())
blocked=sum(slab.intersect(a['shape']).Volume() for a in body)
assert blocked<1e-5,blocked
# The continuous retention lip must leave its adjacent compliant exhaust
# strip intact. Soft parts are excluded from rigid-motion checks, so check
# these interfaces explicitly rather than hiding an interference there.
seal_checks=[]
for a in build.parts:
    if a['name'].startswith('hinge_seal_'):
        volume=sum(a['shape'].intersect(b['shape']).Volume() for b in body)
        assert volume<1e-5,(a['name'],volume)
        backing=min(a['shape'].distance(b['shape']) for b in body)
        assert backing<1e-5,(a['name'],backing)
        seal_checks.append(dict(name=a['name'],body_intersection_mm3=volume,backing_gap_mm=backing))
data=dict(bearing_contacts=checks,hinge_seal_clearance=seal_checks,intake_screen_blockage_mm3=blocked,rib_net_free_fraction=1.0,scope='Nominal geometry only. Added stand has no structure over the intake window; excludes OEM grille solidity. Direct plenum contact checked; no claim of passive self-centering, strength or friction qualification.')
(R/'alignment-validation.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps(data,indent=2))
