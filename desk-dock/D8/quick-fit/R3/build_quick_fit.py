"""R3 fit trial from physical R1 feedback; leaves production D8 and R1 intact.

Run with CadQuery, trimesh, NumPy and Pillow. Outputs beside this script.
The heel extension is re-extracted from the original visualization mesh.
"""
from pathlib import Path
import hashlib
import json
import math
import sys

import cadquery as cq
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from air_relief import relieve_lip

R = Path(__file__).resolve().parent
D = R.parents[1]
sys.path.insert(0, str(D))
from raster import render, font

P = json.loads((D/'parameters.json').read_text(encoding='utf-8'))
C = json.loads((D/'contact-profiles.json').read_text(encoding='utf-8'))
G = json.loads((D/'geometry.json').read_text(encoding='utf-8'))
F = json.loads((R/'fit-parameters.json').read_text(encoding='utf-8'))
H, T, W = P['rear_case_seat_z'], P['laptop_thickness'], P['laptop_width']
B = 38.1
A = math.radians(P['laptop_lean_deg'])
items = [p for p in G['parts'] if p['name'].startswith(('01_', '02_', 'bridge_key')) and '_desk_pad_' not in p['name']]
lo = [min(p['bounds_mm'][i] for p in items) for i in range(3)]
hi = [max(p['bounds_mm'][i+3] for p in items) for i in range(3)]
y0, y1 = lo[1], hi[1]
xstarts = [lo[0], hi[0]-B]
gap = xstarts[1]-xstarts[0]-B


def poly(points, width=B, x=0):
    return cq.Workplane('YZ', origin=(x, 0, 0)).polyline(points).close().extrude(width).val()


def box(y, z, dy, dz):
    return poly([(y,z), (y+dy,z), (y+dy,z+dz), (y,z+dz)])


def lean(shape):
    return shape.rotate((0,0,H), (1,0,H), -P['laptop_lean_deg'])


def solid_box(x, y, z, dx, dy, dz):
    return cq.Workplane('XY').box(dx, dy, dz, centered=False).translate((x,y,z))


# Retain all original contact samples and append only the requested extension.
old_curve = [(a[0], H+min(c['rear_curve_local_yz_mm'][j][1] for c in C['curves']))
             for j,a in enumerate(C['curves'][0]['rear_curve_local_yz_mm'])]
source = D.parent/'history/reference-assets/laptop.glb'
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
assert source_hash == C['source_sha256'], 'Reference source changed'
scene = trimesh.load(source)
transform, geometry = scene.graph[C['case_node']]
case = scene.geometry[geometry].copy()
case.apply_transform(transform)
case.apply_scale(1000)
rear = case.bounds[0,2]


def section_values(x, ys):
    segments = trimesh.intersections.mesh_plane(case, [1,0,0], [x,0,0])
    values = []
    for local_y in ys:
        hits = []
        for a,b in segments:
            if abs(b[1]-a[1]) < 1e-9:
                continue
            f = (local_y+T/2-a[1])/(b[1]-a[1])
            if 0 <= f <= 1:
                hits.append(float(a[2]+f*(b[2]-a[2])-rear+H))
        values.append(min(hits) if hits else None)
    return values


extra = F['seat_extension_toward_underside_mm']
extra_ys = np.arange(old_curve[0][0]-extra, old_curve[0][0]-.001, .2)
sections = [section_values(c['case_x_from_center_mm'], extra_ys) for c in C['curves']]
extension = [(float(y), min(s[j] for s in sections if s[j] is not None)) for j,y in enumerate(extra_ys)]
curve = extension+old_curve
assert all(z >= H for y,z in curve)


air_report = {}


def bracket(revised):
    offset = F['lip_outward_shift_mm'] if revised else 0
    rise = F['lip_height_increase_mm'] if revised else 0
    seat_curve = curve if revised else old_curve
    s = box(y0,-5,y1-y0,4).fuse(box(-6,-2,12,53))
    s = s.fuse(lean(box(-15-offset,46,32+offset,5)))
    s = s.fuse(lean(poly([(seat_curve[0][0],49),(seat_curve[-1][0],49)]+list(reversed(seat_curve)))))
    outer, tip, inner = -T/2-3-offset, -T/2-1-offset, -T/2-.25-offset
    top, shoulder = 66+rise, 62+rise
    lip = poly([(outer,47),(outer,top),(tip,top),(inner,shoulder),(inner,47)])
    if revised:
        edges = [e for e in lip.Edges() if e.BoundingBox().xlen > B-.01
                 and abs(e.Center().z-top) < .001]
        assert len(edges) == 2
        lip = lip.fillet(F['lip_top_edge_radius_mm'], edges)
        lip, details = relieve_lip(lip,B,outer,inner,top,F['air_relief'])
        air_report.update(details)
    s = s.fuse(lean(lip))
    s = s.fuse(lean(box(T/2,48,4,86)))
    top_y = (T/2+2)*math.cos(A)+(134-H)*math.sin(A)
    s = s.fuse(poly([(top_y-1,129),(top_y+3,134),(y1-1,-1),(y1-7,-1)]))
    s = s.fuse(box(top_y+1,131,3,hi[2]-131)).clean()
    label = f'R3 GAP {gap:.2f} mm' if revised else f'GAP {gap:.2f} mm'
    s = s.cut(cq.Workplane('YZ',origin=(B-.5,43,-3)).text(label,2.4,.6,font='Arial',combine=False).val()).clean()
    assert s.isValid() and len(s.Solids()) == 1
    return s, lip


s, lip = bracket(True)
lip.exportBrep(str(R/'lip-local.brep'))
baseline, old_lip = bracket(False)
# Independent STEP import checks that the reconstructed baseline matches R1.
old_step = cq.importers.importStep(str(R.parent/'D8-quick-fit-bracket.step')).val()
baseline_difference = baseline.cut(old_step).Volume()+old_step.cut(baseline).Volume()
# Font substitution may affect only the engraved label; validate structural section
# outside its Z=-3 mm engraving as exact geometry.
structural_window = solid_box(-1,-40,0,B+2,180,200).val()
structural_difference = baseline.intersect(structural_window).cut(old_step).Volume()+old_step.intersect(structural_window).cut(baseline).Volume()
assert structural_difference < .001, structural_difference

# Same nominal D8 envelope, with the heel cut extended using the source mesh.
# The published simplified reference ended at the old seat and cannot validate
# additional wrap beyond that artificial boundary.
laptop = solid_box(0,-T/2,H,W,T,P['laptop_depth']).edges('|Y').fillet(4)
laptop = laptop.cut(solid_box(30,-7,H-1,W-60,17,5))
heel = [(curve[0][0],H-6),(curve[-1][0],H-6)]+list(reversed(curve))
for x, width in [(0,30),(W-30,30)]:
    laptop = laptop.cut(poly(heel,width,x))
laptop = lean(laptop.val())
feet = []
keepouts = []
for f in C['rubber_feet']:
    a,b = f['untilted_case_relative_bounds_mm']
    feet.append(lean(solid_box(a[0],a[1],H+a[2],b[0]-a[0],b[1]-a[1],b[2]-a[2]).val()))
    keepouts.append(lean(solid_box(a[0]-2,a[1]-2,H+a[2]-2,b[0]-a[0]+4,b[1]-a[1]+4,b[2]-a[2]+4).val()))
placed = [s.translate((x,0,0)) for x in xstarts]
checks = []
motion = []
for i,q in enumerate(placed):
    checks.append(dict(laptop_overlap_mm3=q.intersect(laptop).Volume(),
        rubber_foot_overlap_mm3=sum(q.intersect(f).Volume() for f in feet),
        expanded_foot_keepout_overlap_mm3=sum(q.intersect(f).Volume() for f in keepouts),
        seat_contact_probe_mm3=q.translate((0,.02*math.sin(A),.02*math.cos(A))).intersect(laptop).Volume()))
    for lift in [0,.25,.5,1,2,3,5,10,20,40]:
        delta = (0,lift*math.sin(A),lift*math.cos(A))
        motion.append(dict(bracket=i+1,lift_mm=lift,
            laptop_overlap_mm3=q.intersect(laptop.translate(delta)).Volume(),
            foot_keepout_overlap_mm3=sum(q.intersect(f.translate(delta)).Volume() for f in keepouts)))
assert all(c['laptop_overlap_mm3']<.001 and c['rubber_foot_overlap_mm3']<.001
           and c['expanded_foot_keepout_overlap_mm3']<.001 and c['seat_contact_probe_mm3']>.01 for c in checks), checks
assert all(c['laptop_overlap_mm3']<.001 and c['foot_keepout_overlap_mm3']<.001 for c in motion), motion

# Independently sample the source at both physical bracket footprints. Compare
# only the new lip of the seat; original nominal contacts remain unchanged.
ys = np.linspace(curve[0][0],old_curve[0][0],41)
seat_z = np.interp(ys,[p[0] for p in curve],[p[1] for p in curve])
clearances = []
for x0 in xstarts:
    for x in np.arange(max(.25,x0),min(W-.25,x0+B),.25):
        for z,bearing_z in zip(section_values(x-W/2,ys),seat_z):
            if z is not None:
                clearances.append(float(z-bearing_z))
assert clearances and min(clearances)>-.015, min(clearances)

printed = s.rotate((0,0,0),(0,1,0),-90)
b = printed.BoundingBox()
printed = printed.translate((-b.xmin,-b.ymin,-b.zmin))
stl = R/'D8-R3-quick-fit-bracket-print-TWO.stl'
step = R/'D8-R3-quick-fit-bracket.step'
cq.exporters.export(printed,str(stl),tolerance=.04,angularTolerance=.1)
cq.exporters.export(s,str(step))
mesh = trimesh.load_mesh(stl)
assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split())==1
assert mesh.volume>0 and max(mesh.extents[:2])+16 < 256 and mesh.extents[2]<256
roundtrip = cq.importers.importStep(str(step)).val()
assert roundtrip.isValid() and len(roundtrip.Solids())==1
assert abs(roundtrip.Volume()-s.Volume())<.001

report = dict(passed=True,revision='R3 fit trial',quantity=2,identical=True,
    air_relief=air_report,
    changes=F,lip_nominal_clearance_mm=.25+F['lip_outward_shift_mm'],
    lip_top_above_seat_datum_mm=12+F['lip_height_increase_mm'],
    seat_contact_profile_width_mm=curve[-1][0]-curve[0][0],
    seat_rim_height_increase_mm=curve[0][1]-old_curve[0][1],
    seat_datum_and_lid_support_unchanged=True,bracket_width_mm=B,
    inside_clear_gap_mm=gap,center_spacing_mm=xstarts[1]-xstarts[0],
    outside_width_mm=hi[0]-lo[0],footprint_depth_mm=y1-y0,
    height_above_desk_mm=hi[2]+5,nominal_lean_degrees=P['laptop_lean_deg'],
    solid_volume_each_cm3=s.Volume()/1000,
    solid_PETG_mass_pair_g=s.Volume()/1000*1.27*2,
    print_bounds_mm=mesh.extents.tolist(),mesh_watertight=bool(mesh.is_watertight),
    mesh_connected_components=len(mesh.split()),step_roundtrip_valid=True,
    original_structural_difference_mm3=structural_difference,
    original_including_font_difference_mm3=baseline_difference,
    source_extension_sample_count=len(clearances),
    source_extension_min_sampled_clearance_mm=min(clearances),checks=checks,motion=motion,
    cadquery_version=cq.__version__,trimesh_version=trimesh.__version__,
    source_mesh_sha256=source_hash,
    input_sha256={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in [Path(__file__),R/'air_relief.py',R/'fit-parameters.json',D/'parameters.json',D/'contact-profiles.json',D/'geometry.json']},
    output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [stl,step]},
    scope='Separate fit prototype. Source visualization mesh and nominal CAD checks only. Vent noise, stability, strength and physical R3 fit untested. Main D8 unchanged.')
(R/'checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(R/'seat-profile.json').write_text(json.dumps(dict(original_yz_mm=old_curve,revised_yz_mm=curve,source_sha256=source_hash),indent=2)+'\n',encoding='utf-8')

im,_ = render([(q,(62,117,139)) for q in placed]+[(laptop,(188,195,198))],(1500,950),(.8,-1,.65),pad=65)
canvas = Image.new('RGB',(1500,1070),'#f7f7f7'); canvas.paste(im,(0,75)); draw=ImageDraw.Draw(canvas)
draw.text((35,20),'D8 R3 fit trial | Print the same bracket twice',font=font(29,True),fill='#20313c')
draw.text((35,1020),f'Inside gap {gap:.2f} mm | 2 mm more lip clearance | Deeper heel cradle',font=font(23),fill='#20313c')
canvas.save(R/'D8-R3-quick-fit.png')
im,_=render([(s,(62,117,139))],(1100,900),(1,-.15,.13),pad=60)
im.save(R/'D8-R3-quick-fit-profile.png')
print(json.dumps({k:v for k,v in report.items() if k not in ('motion','input_sha256','output_sha256')}),flush=True)
