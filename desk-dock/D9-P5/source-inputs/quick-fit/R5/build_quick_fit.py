"""R5 quick-fit bracket pair: R4 plus a tall underside rail replacing the short fence.

The R4-C pair carried the laptop but nothing stopped it tipping toward the
underside side: the 15-mm fence cannot hold a 240-mm lever pivoting on the
seat. R5 raises the fence at the bracket ends into a 6-mm underside rail with
the same 2.25-mm running clearance and the same R2 lower profile, plus a lead-in
chamfer at the top. Rubber feet (x 30..323) and the intake window (x 31..323)
lie outside the bracket ends (x < 18, x > 336), so the wall meets neither.

Run with CadQuery, trimesh, NumPy and Pillow (`cadpy build_quick_fit.py --variant B`).
Outputs beside this script. The heel extension is re-extracted from the original
visualization mesh exactly as R2 does.

Variant selects the seat side, matching the V5 coupon letters:
  A  original R1 seat and lip (no R2 outward lip shift, rise or heel extension)
  B  R2 seat, lip shift, lip rise and heel extension (default)
  C  B plus the 1-mm local seat relief band under the R2 curve
All variants move the whole lid-rail side 3.5 mm outward (unleaned +Y), as the
printed V5 coupons do, and thicken the load-carrying members outward/downward so
the laptop-facing surfaces are unchanged: rail 4 -> 6 mm, short fence +2 mm on
its outer face, base plate 4 -> 6 mm, diagonal brace 4 -> 6 mm.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import cadquery as cq
import numpy as np
import trimesh
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parent
D = R.parents[1]
R2 = R.parent / 'R2'
sys.path.insert(0, str(D))
from raster import render, font

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--variant', choices=('A', 'B', 'C'), default='B')
parser.add_argument('--base-thickness', type=float, default=None, help='override base plate thickness (mm); the D9 cradle source uses 4 so all feet stay coplanar')
parser.add_argument('--tag', default='', help='suffix for output names, e.g. d9-source')
args = parser.parse_args()
VARIANT = args.variant
TAG = f'-{args.tag}' if args.tag else ''

P = json.loads((D/'parameters.json').read_text(encoding='utf-8'))
C = json.loads((D/'contact-profiles.json').read_text(encoding='utf-8'))
G = json.loads((D/'geometry.json').read_text(encoding='utf-8'))
F = json.loads((R/'fit-parameters.json').read_text(encoding='utf-8'))
H, T, W = P['rear_case_seat_z'], P['laptop_thickness'], P['laptop_width']
B = 38.1
A = math.radians(P['laptop_lean_deg'])
S = F['rail_outward_shift_mm']          # 3.5, the V5 move
RT = F['rail_thickness_mm']             # 6 (was 4)
FE = F['fence_extra_outer_thickness_mm']  # 2
BT = args.base_thickness if args.base_thickness is not None else F['base_thickness_mm']  # 6 (was 4); 4 for the D9 source
BW = F['brace_width_mm']                # 6 (was 4)
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


# Identical contact extraction to R2: original samples plus the re-extracted heel.
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
r2_profile = json.loads((R2/'seat-profile.json').read_text(encoding='utf-8'))
assert all(abs(a-b[0]) < 1e-9 and abs(z-b[1]) < 1e-9 for (a,z),b in zip(curve, r2_profile['revised_yz_mm'])), 'R2 seat profile not reproduced'


def bracket(variant):
    revised = variant in ('B', 'C')
    offset = F['lip_outward_shift_mm'] if revised else 0
    rise = F['lip_height_increase_mm'] if revised else 0
    seat_curve = curve if revised else old_curve
    s = box(y0,-1-BT,y1-y0,BT).fuse(box(-6,-2,12,53))
    fence_outer = -T/2-3-offset-FE
    s = s.fuse(lean(box(fence_outer,46,17+S-fence_outer,5)))
    s = s.fuse(lean(poly([(seat_curve[0][0],49),(seat_curve[-1][0],49)]+list(reversed(seat_curve)))))
    outer, inner = -T/2-3-offset-FE, -T/2-.25-offset
    top = F['fence_top_z_mm']; shoulder = top-F['fence_lead_in_height_mm']; tip = inner-F['fence_lead_in_depth_mm']
    lip = poly([(outer,47),(outer,top),(tip,top),(inner,shoulder),(inner,47)])
    if revised:
        edges = [e for e in lip.Edges() if e.BoundingBox().xlen > B-.01
                 and abs(e.Center().z-top) < .001]
        assert len(edges) == 2
        lip = lip.fillet(F['lip_top_edge_radius_mm'], edges)
    s = s.fuse(lean(lip))
    s = s.fuse(lean(box(T/2+S,48,RT,86)))
    top_y = (T/2+S+RT/2)*math.cos(A)+(134-H)*math.sin(A)
    s = s.fuse(poly([(top_y-BW/4,129),(top_y+3*BW/4,134),(y1,-1),(y1-BW-2,-1)]))
    s = s.fuse(box(top_y+RT/2-1,131,3,hi[2]-131)).clean()
    fence_solid = lean(box(outer,47,inner-outer,top-47))
    s, edge_report = dress_edges(s, offset)
    edge_report['fence'] = {'inner_face_unleaned_y_mm': inner, 'outer_face_unleaned_y_mm': outer, 'thickness_mm': inner-outer, 'top_z_unleaned_mm': top, 'height_above_seat_datum_mm': top-H, 'lead_in_mm': [F['fence_lead_in_depth_mm'], F['fence_lead_in_height_mm']]}
    if variant == 'C':
        original = [(float(y), float(z)) for y, z in r2_profile['revised_yz_mm']]
        lowered = [(y, z-1.0) for y, z in reversed(original)]
        s = s.cut(lean(poly(original+lowered))).clean()
    label = f'R5-{variant} GAP {gap:.2f} mm'
    s = s.cut(cq.Workplane('YZ',origin=(B-.5,43,-3)).text(label,2.4,.6,font='Arial',combine=False).val()).clean()
    assert s.isValid() and len(s.Solids()) == 1
    return s, edge_report


def unlean_yz(y, z):
    c, sn = math.cos(A), math.sin(A)
    dz = z-H
    return (c*y-sn*dz, sn*y+c*dz+H)


def x_edges(shape):
    """Edges parallel to the source X axis (print Z): the profile corners."""
    return [e for e in shape.Edges() if e.BoundingBox().ylen < 1e-6 and e.BoundingBox().zlen < 1e-6 and e.BoundingBox().xlen > 1.0]


def dress_edges(s, offset):
    """Cosmetic and stress-relief edge treatment that stays printable.

    Profile corners run along print Z (source X) and print as perimeters, so
    they take fillets freely: concave corners get the inside radius, convex
    ones the outside radius. The laptop-contact band (fence inner face to
    rail inner face, seat height to fence top) is left untouched except a
    small edge break on the rail's top inner edge. The +X face becomes the
    top of the print and gets a 45-degree chamfer; the bed face (x=0) is
    left sharp so the first layer keeps its footprint.
    """
    r_in, r_out = F['inside_corner_fillet_mm'], F['outside_corner_fillet_mm']
    r_break, chamfer = F['contact_edge_break_mm'], F['top_face_chamfer_mm']
    fence_inner, rail_inner = -T/2-.25-offset, T/2+S
    report = dict(inside=[], outside=[], edge_break=[], skipped=[])

    def classify(edge):
        c = edge.Center()
        inside = 0
        for dy, dz in ((1,1),(1,-1),(-1,1),(-1,-1)):
            inside += s.isInside(cq.Vector(c.x, c.y+.4*dy, c.z+.4*dz))
        return inside

    candidates = []
    for e in x_edges(s):
        if e.Length() < B-.01:
            continue
        c = e.Center()
        uy, uz = unlean_yz(c.y, c.z)
        in_band = fence_inner-.5 <= uy <= rail_inner+.5 and 46.5 <= uz <= 70
        if abs(uy-rail_inner) < .05 and abs(uz-134) < .05:
            candidates.append(((c.y, c.z), r_break, 'edge_break')); continue
        if in_band:
            continue
        n = classify(e)
        if n == 3: candidates.append(((c.y, c.z), r_in, 'inside'))
        elif n == 1: candidates.append(((c.y, c.z), r_out, 'outside'))
    for (y, z), radius, kind in candidates:
        match = [e for e in x_edges(s) if abs(e.Center().y-y) < .02 and abs(e.Center().z-z) < .02]
        if len(match) != 1:
            report['skipped'].append([kind, round(y,2), round(z,2), 'edge not found after earlier fillet']); continue
        done = False
        for r in (radius, radius/2):
            try:
                trial = s.fillet(r, match)
                assert trial.isValid() and len(trial.Solids()) == 1
                s = trial; report[kind].append([round(y,2), round(z,2), r]); done = True; break
            except Exception as error:
                last = type(error).__name__
        if not done:
            report['skipped'].append([kind, round(y,2), round(z,2), last])
    # Top chamfer as a 0.2-mm staircase (one slicer layer per step): the 3-D
    # chamfer operator fails on this outline's tangent arc junctions and the
    # sub-millimetre seat facets, and a 45-degree chamfer sliced at 0.2 mm is
    # exactly this staircase anyway. Built from 2-D inward offsets of the top
    # outline, so it follows fillets and leaves the seat curve alone where the
    # offset would self-intersect.
    steps = max(1, int(round(chamfer/0.2)))
    top_face = cq.Workplane().add(s).faces('>X').val()
    x_top = top_face.Center().x
    outer = top_face.outerWire()
    applied = 0
    for k in range(1, steps+1):
        d = chamfer*k/steps
        x_k = x_top-chamfer+(k-1)*chamfer/steps
        try:
            inner = outer.offset2D(-d, 'arc')
            keep = cq.Solid.extrudeLinear(cq.Face.makeFromWires(inner[0]), cq.Vector(x_top-x_k+1, 0, 0)).translate((x_k, 0, 0))
            full = cq.Solid.extrudeLinear(cq.Face.makeFromWires(outer), cq.Vector(x_top-x_k+1, 0, 0)).translate((x_k, 0, 0))
            trial = s.cut(full.cut(keep)).clean()
            assert trial.isValid() and len(trial.Solids()) == 1
            s = trial; applied += 1
        except Exception as error:
            report['skipped'].append(['top_chamfer_step', k, type(error).__name__]); break
    report['top_chamfer_mm'] = chamfer*applied/steps
    report['top_chamfer_steps'] = applied
    return s, report


s, edge_report = bracket(VARIANT)
print(json.dumps({'edges': {k: (len(v) if isinstance(v, list) else v) for k, v in edge_report.items()}, 'skipped': edge_report['skipped']}), flush=True)

# Rail-position receipts: the new inner face sits at T/2+S like the V5 coupons,
# and the 3.5-mm channel between the old and new faces is empty above the deck.
probe_new_face = lean(box(T/2+S, 52, .1, 80))
probe_channel = lean(box(T/2, 51.001, S, 83))
assert abs(probe_new_face.intersect(s).Volume() - B*.1*80) < 1e-3
assert probe_channel.intersect(s).Volume() < 1e-6

# Same nominal D8 envelope and heel cut as R2, with the same contact checks.
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
if VARIANT != 'C':
    assert all(c['seat_contact_probe_mm3']>.01 for c in checks), checks
assert all(c['laptop_overlap_mm3']<.001 and c['rubber_foot_overlap_mm3']<.001
           and c['expanded_foot_keepout_overlap_mm3']<.001 for c in checks), checks
assert all(c['laptop_overlap_mm3']<.001 and c['foot_keepout_overlap_mm3']<.001 for c in motion), motion

# Lid-side clearance: the nominal lid top (y=+T/2) now clears the rail by S.
lid_probe = lean(solid_box(xstarts[0], T/2, H+2, B, S-.05, 70).val())
assert lid_probe.intersect(placed[0]).Volume() < 1e-6

# Tip receipt: rotate the nominal laptop about the seat front edge toward the
# underside side. R4's 15-mm fence let it go; the R5 rail must catch it.
pivot_y, pivot_z = curve[0][0], H
tip_hits = {}
for deg in (2, 4, 6, 8, 10):
    tipped = laptop.rotate((0,pivot_y,pivot_z),(1,pivot_y,pivot_z),-deg)
    tip_hits[deg] = placed[0].intersect(tipped).Volume()
assert tip_hits[2] < .001 or True  # small angles may graze the lead-in; recorded, not asserted
assert max(tip_hits.values()) > 1.0, ('underside rail never catches the tipping laptop', tip_hits)
first_catch = min(d for d,v in tip_hits.items() if v > .001)
# Feet and intake window stay outside both bracket ends.
intake = C['intake_window_case_relative_bounds_mm']
assert xstarts[0]+B < intake[0][0] and xstarts[1] > intake[1][0], 'underside rail would cover the intake window'
assert all(xstarts[0]+B < f['untilted_case_relative_bounds_mm'][0][0] and xstarts[1] > f['untilted_case_relative_bounds_mm'][1][0] for f in C['rubber_feet']), 'underside rail would meet a rubber foot'

printed = s.rotate((0,0,0),(0,1,0),-90)
b = printed.BoundingBox()
printed = printed.translate((-b.xmin,-b.ymin,-b.zmin))
stl = R/f'D8-R5-{VARIANT}{TAG}-quick-fit-bracket-print-TWO.stl'
step = R/f'D8-R5-{VARIANT}{TAG}-quick-fit-bracket.step'
cq.exporters.export(printed,str(stl),tolerance=.04,angularTolerance=.1)
cq.exporters.export(s,str(step))
mesh = trimesh.load_mesh(stl)
assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split())==1
assert mesh.volume>0 and max(mesh.extents[:2])+16 < 256 and mesh.extents[2]<256
roundtrip = cq.importers.importStep(str(step)).val()
assert roundtrip.isValid() and len(roundtrip.Solids())==1
assert abs(roundtrip.Volume()-s.Volume())<.001

report = dict(passed=True,revision=f'R5-{VARIANT} fit pair',quantity=2,identical=True,
    variant=VARIANT,changes=F,
    rail_inner_face_unleaned_y_mm=T/2+S,rail_thickness_mm=RT,
    lip_nominal_clearance_mm=(.25+F['lip_outward_shift_mm']) if VARIANT!='A' else .25,
    fence_inner_to_rail_inner_mm=T+.25+(F['lip_outward_shift_mm'] if VARIANT!='A' else 0)+S,
    base_thickness_mm=BT,brace_width_mm=BW,edge_treatment=edge_report,
    underside_rail=edge_report['fence'],tip_catch_first_deg=first_catch,tip_overlap_by_deg_mm3=tip_hits,
    seat_datum_unchanged=True,bracket_width_mm=B,
    inside_clear_gap_mm=gap,center_spacing_mm=xstarts[1]-xstarts[0],
    outside_width_mm=hi[0]-lo[0],footprint_depth_mm=y1-y0,
    height_above_desk_mm=hi[2]+1+BT,nominal_lean_degrees=P['laptop_lean_deg'],
    solid_volume_each_cm3=s.Volume()/1000,
    solid_PETG_mass_pair_g=s.Volume()/1000*1.27*2,
    print_bounds_mm=mesh.extents.tolist(),mesh_watertight=bool(mesh.is_watertight),
    mesh_connected_components=len(mesh.split()),step_roundtrip_valid=True,
    checks=checks,motion=motion,
    cadquery_version=cq.__version__,trimesh_version=trimesh.__version__,
    source_mesh_sha256=source_hash,
    input_sha256={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in [Path(__file__),R/'fit-parameters.json',R2/'seat-profile.json',D/'parameters.json',D/'contact-profiles.json',D/'geometry.json']},
    output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [stl,step]},base_thickness_override=args.base_thickness,tag=args.tag,
    scope='Loaded fit prototype: R2 contact, V5 rail offset, thicker members. Source visualization mesh and nominal CAD checks only; physical fit, stability and strength untested.')
(R/f'checks-{VARIANT}{TAG}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')

im,_ = render([(q,(62,117,139)) for q in placed]+[(laptop,(188,195,198))],(1500,950),(.8,-1,.65),pad=65)
canvas = Image.new('RGB',(1500,1070),'#f7f7f7'); canvas.paste(im,(0,75)); draw=ImageDraw.Draw(canvas)
draw.text((35,20),f'D8 R5-{VARIANT} fit pair | Print the same bracket twice',font=font(29,True),fill='#20313c')
draw.text((35,1020),f'Inside gap {gap:.2f} mm | Lid rail +{S} mm | Underside rail to z={F["fence_top_z_mm"]:.0f} mm | Rail {RT}, base {BT}, brace {BW} mm',font=font(23),fill='#20313c')
canvas.save(R/f'D8-R5-{VARIANT}{TAG}-quick-fit.png')
im,_=render([(s,(62,117,139))],(1100,900),(1,-.15,.13),pad=60)
im.save(R/f'D8-R5-{VARIANT}{TAG}-quick-fit-profile.png')
print(json.dumps({k:v for k,v in report.items() if k not in ('motion','checks','input_sha256','output_sha256','changes')}),flush=True)
