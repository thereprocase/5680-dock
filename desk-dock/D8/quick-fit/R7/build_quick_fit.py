"""R7: modular quick-fit bracket with drop-in pegs (user concept, 2026-09-18).

Frame (constant X profile): base, brace, a tower whose top is the deck at z 51,
the 8-degree lid rail (the only laptop-touching surface on the frame), and a
6-mm outer wall. Two channels run along X in the tower top, 22 mm deep: a 6-mm
channel under the fence line and a 13-mm channel under the seat.

Pegs (constant X profiles), dropped in from above:
- fence peg: a plank whose 5.4-mm foot fills the fence channel and whose 6-mm
  wall stands on the deck as the underside stop (64 mm tall at the plug end,
  15 mm at the far end). Laptop-thickness differences: offset the wall from
  the foot.
- seat peg: a 12.4-mm foot in the seat channel carrying the R2 seat curve with
  the V5 C relief. Hinge-geometry differences: change the head.
One 36-mm D9 fan pin from the outer face passes through the outer wall, the
fence foot, the tower web and the seat foot: it locates X, stops lift and is a
proper double-supported shear pin. Peg bores sit 0.15 mm lower than the frame
bore, so driving the pin cams both pegs down onto the deck: no rattle. The
moment on the fence goes into the channel walls by embedment, so no backing
wall is needed and the outer face is 6 mm beyond the fence. Disassembly: pull
the pin, lift the pegs; 4-mm push-out holes under both channels take a rod.

`--d9-source --base-thickness 4 --tag d9-source --lock-x 16` writes the frame,
pegs and the socket void (channels, bore, push-outs) the D9 builder subtracts
from its fused cradle before adding the pegs.
"""
from pathlib import Path
import argparse, hashlib, json, math, sys
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
parser.add_argument('--insert', choices=('plug', 'far'), default='plug', help='which insert goes on the standalone plate')
parser.add_argument('--lean', type=float, default=8.0)
parser.add_argument('--base-thickness', type=float, default=None)
parser.add_argument('--tag', default='')
parser.add_argument('--d9-source', action='store_true', help='export the 4-mm-base frame and both inserts for the D9 cradles')
parser.add_argument('--lock-x', type=float, default=None, help='X of the pin bore and knock-out (default: bracket centre; the D9 cradle crops x 8..24, so use 16)')
parser.add_argument('--demo-thickness', type=float, default=None, help='render the concept for a laptop of this thickness: same frame, lid face on the same rail, pegs re-headed; contact checks skipped (no data for that machine)')
args = parser.parse_args()
TAG = f'-{args.tag}' if args.tag else ''

P = json.loads((D/'parameters.json').read_text(encoding='utf-8'))
C = json.loads((D/'contact-profiles.json').read_text(encoding='utf-8'))
G = json.loads((D/'geometry.json').read_text(encoding='utf-8'))
F = json.loads((R/'fit-parameters.json').read_text(encoding='utf-8'))
H, T, W = P['rear_case_seat_z'], P['laptop_thickness'], P['laptop_width']
LEAN = args.lean
A = math.radians(LEAN)
B = 38.1
S = F['rail_outward_shift_mm']; RT = F['rail_thickness_mm']; BW = F['brace_width_mm']
BT = args.base_thickness if args.base_thickness is not None else F['base_thickness_mm']
OFFSET = F['lip_outward_shift_mm']             # R2 fence shift, 2 mm
RAIL_IN = T/2 + S                              # 14.585: the 8-degree bearing wall
FENCE_IN = -T/2 - .25 - OFFSET                 # -13.335: fence liner inner face (5680; fixes the fence channel)
DEMO = args.demo_thickness
TD = DEMO if DEMO else T                        # laptop thickness being shown
DY = (T - TD) / 2                              # shift of the laptop centreline so the lid stays on the fixed rail
WALL_IN = (T/2 - TD) - .25 - OFFSET             # fence wall inner face for that thickness (equals FENCE_IN for the 5680)
FENCE_T = F['fence_liner_thickness_mm']        # 6, fence wall
DECK_TOP = 51.0
FENCE_TOP = {'plug': F['fence_top_z_plug_mm'], 'far': F['fence_top_z_far_mm']}
PIN_LEN, PIN_MARKS = 36, 1                     # the D9 fan pin
BORE_R, PIN_R, KEY_BARB = 4.2, 4.1, 3.6
items = [p for p in G['parts'] if p['name'].startswith(('01_', '02_', 'bridge_key')) and '_desk_pad_' not in p['name']]
lo = [min(p['bounds_mm'][i] for p in items) for i in range(3)]
hi = [max(p['bounds_mm'][i+3] for p in items) for i in range(3)]
y0, y1 = lo[1] - F['base_outward_extension_mm'], hi[1]
xstarts = [lo[0], hi[0]-B]
gap = xstarts[1]-xstarts[0]-B


def poly(points, width=B, x=0):
    return cq.Workplane('YZ', origin=(x, 0, 0)).polyline(points).close().extrude(width).val()
def box(y, z, dy, dz, width=B, x=0):
    return poly([(y,z),(y+dy,z),(y+dy,z+dz),(y,z+dz)], width, x)
def lean(shape, deg=None):
    return shape.rotate((0,0,H), (1,0,H), -(LEAN if deg is None else deg))
def solid_box(x, y, z, dx, dy, dz):
    return cq.Workplane('XY').box(dx, dy, dz, centered=False).translate((x,y,z))
def unlean_yz(y, z):
    c, sn = math.cos(A), math.sin(A); dz = z-H
    return (c*y-sn*dz, sn*y+c*dz+H)
def lean_dir(v):
    """A direction vector in the unleaned frame, expressed in the leaned frame."""
    c, sn = math.cos(A), math.sin(A)
    return cq.Vector(v[0], c*v[1]-sn*v[2], sn*v[1]+c*v[2])

# ---- R2 contact extraction (unchanged) -------------------------------------
old_curve = [(a[0], H+min(c['rear_curve_local_yz_mm'][j][1] for c in C['curves'])) for j,a in enumerate(C['curves'][0]['rear_curve_local_yz_mm'])]
source = D.parent/'history/reference-assets/laptop.glb'
source_hash = hashlib.sha256(source.read_bytes()).hexdigest(); assert source_hash == C['source_sha256']
scene = trimesh.load(source); transform, geometry = scene.graph[C['case_node']]
case = scene.geometry[geometry].copy(); case.apply_transform(transform); case.apply_scale(1000); rear = case.bounds[0,2]
def section_values(x, ys):
    segments = trimesh.intersections.mesh_plane(case, [1,0,0], [x,0,0]); values = []
    for local_y in ys:
        hits = []
        for a,b in segments:
            if abs(b[1]-a[1]) < 1e-9: continue
            f = (local_y+T/2-a[1])/(b[1]-a[1])
            if 0 <= f <= 1: hits.append(float(a[2]+f*(b[2]-a[2])-rear+H))
        values.append(min(hits) if hits else None)
    return values
extra_ys = np.arange(old_curve[0][0]-F['seat_extension_toward_underside_mm'], old_curve[0][0]-.001, .2)
sections = [section_values(c['case_x_from_center_mm'], extra_ys) for c in C['curves']]
curve = [(float(y), min(s[j] for s in sections if s[j] is not None)) for j,y in enumerate(extra_ys)] + old_curve
r2_profile = json.loads((R2/'seat-profile.json').read_text(encoding='utf-8'))
assert all(abs(a-b[0]) < 1e-9 and abs(z-b[1]) < 1e-9 for (a,z),b in zip(curve, r2_profile['revised_yz_mm'])), 'R2 seat profile not reproduced'

# ---- D9 P4 pin and key (copied so the standalone plate carries a real pair) --
FLAT = PIN_R*math.cos(math.pi/8)
OCT = [(PIN_R*math.cos(math.pi/8+i*math.pi/4), PIN_R*math.sin(math.pi/8+i*math.pi/4)) for i in range(8)]
def cbox(x,y,z,dx,dy,dz): return cq.Workplane('XY').box(dx,dy,dz,centered=False).translate((x,y,z)).val()
def pin(length, marks):
    sh = cq.Workplane('XY').polyline(OCT).close().extrude(length).val()
    head = [(-5.5,-FLAT),(5.5,-FLAT),(7.5,2-FLAT),(7.5,4.2),(5.5,6.2),(-5.5,6.2),(-7.5,4.2),(-7.5,2-FLAT)]
    sh = sh.fuse(cq.Workplane('XY',origin=(0,0,-4)).polyline(head).close().extrude(4).val())
    sh = sh.cut(cbox(-2.7,-5,length-7.5-1.7,5.4,10,3.4))
    for i in range(marks): sh = sh.cut(cbox((i-(marks-1)/2)*3-0.6,4.8,-4.1,1.2,1.5,4.2))
    return sh.clean()
def key(grip=16):
    a = grip/2; head_length = 3
    sh = cbox(-4.5,-a-head_length,-1.4,9,head_length,2.8)
    tip = a+3.5
    outline = [(-2.4,-a),(-2.4,a+.2),(-KEY_BARB,a+.2),(-2.4,tip),(2.4,tip),(KEY_BARB,a+.2),(2.4,a+.2),(2.4,-a)]
    sh = sh.fuse(cq.Workplane('XY',origin=(0,0,-1.4)).polyline(outline).close().extrude(2.8).val())
    gapbox = cbox(-1.2,-a+3,-1.6,2.4,grip+8,3.2).fuse(cq.Solid.makeCylinder(1.2,3.2,cq.Vector(0,-a+3,-1.6),cq.Vector(0,0,1)))
    return sh.cut(gapbox).clean()

# ---- Frame ------------------------------------------------------------------
OUT_W = F['outer_wall_thickness_mm']
FENCE_OUT = FENCE_IN - FENCE_T
Y_OUT = FENCE_OUT - OUT_W                       # outer face of the stand at the socket
CH_D = F['channel_depth_mm']; PEG_GAP = F['peg_clearance_mm']
SEAT_CH = F['seat_channel_y_mm']
PIN_Z = F['pin_z_mm']; PIN_CAM = F['pin_cam_offset_mm']
def channel_solid(y_a, y_b, width=B, x=0):
    return box(y_a, DECK_TOP-CH_D, y_b-y_a, CH_D+1, width, x)
def frame_parts(width=B, x=0):
    base = box(y0, -1-BT, y1-y0, BT, width, x)
    tower = box(Y_OUT, -12, RAIL_IN+RT-Y_OUT, DECK_TOP+12, width, x)
    rail = box(RAIL_IN, DECK_TOP-1, RT, 134-DECK_TOP+1, width, x)
    void = channel_solid(FENCE_OUT, FENCE_IN, width, x).fuse(channel_solid(SEAT_CH[0], SEAT_CH[1], width, x))
    return base, lean(tower.fuse(rail)), void
def frame_solid(width=B, x=0):
    base, leaned, void = frame_parts(width, x)
    s = base.fuse(leaned.cut(lean(void)))
    top_y = (RAIL_IN+RT/2)*math.cos(A)+(134-H)*math.sin(A)
    s = s.fuse(poly([(top_y-BW/4,129),(top_y+3*BW/4,134),(y1,-1),(y1-BW-2,-1)], width, x))
    s = s.fuse(box(top_y+RT/2-1,131,3,hi[2]-131, width, x))
    return s.intersect(box(y0-5, -1-BT, y1-y0+10, 300, width+2, x-1)).clean()

# ---- Pegs -------------------------------------------------------------------
def seat_plate_extent():
    cy0, cy1 = curve[0][0]+DY, curve[-1][0]+DY
    return min(SEAT_CH[0], cy0)-1, max(SEAT_CH[1], cy1)+1
def seat_peg(width=B, x=0):
    foot = box(SEAT_CH[0]+PEG_GAP, DECK_TOP-CH_D+PEG_GAP, SEAT_CH[1]-SEAT_CH[0]-2*PEG_GAP, CH_D-PEG_GAP+.5, width, x)
    cy0, cy1 = curve[0][0]+DY, curve[-1][0]+DY
    plate_lo, plate_hi = seat_plate_extent()
    head = box(plate_lo, DECK_TOP, plate_hi-plate_lo, 2, width, x)   # 2-mm shoulder plate resting on the deck
    seat = poly([(cy0,DECK_TOP),(cy1,DECK_TOP)]+[(yy+DY, zz) for yy, zz in reversed(curve)], width, x)   # base at the deck so an overhanging head clears the tower
    s = foot.fuse(head).fuse(seat).clean()
    original = [(float(yy)+DY, float(zz)) for yy, zz in r2_profile['revised_yz_mm']]
    s = s.cut(poly(original+[(yy, zz-1.0) for yy, zz in reversed(original)], width, x)).clean()   # V5 C relief
    return lean(s)
def fence_peg(kind, width=B, x=0):
    top = FENCE_TOP[kind]
    foot = box(FENCE_OUT+PEG_GAP, DECK_TOP-CH_D+PEG_GAP, FENCE_T-2*PEG_GAP, CH_D-PEG_GAP+.5, width, x)
    lead_h, lead_d = F['fence_lead_in_height_mm'], F['fence_lead_in_depth_mm']
    w_out = WALL_IN-FENCE_T
    wall = poly([(w_out,DECK_TOP),(w_out,top),(WALL_IN-lead_d,top),(WALL_IN,top-lead_h),(WALL_IN,DECK_TOP)], width, x)
    edges = [e for e in wall.Edges() if e.BoundingBox().xlen > width-.01 and abs(e.Center().z-top) < .001]
    wall = wall.fillet(F['lip_top_edge_radius_mm'], edges)
    bar_lo, bar_hi = min(FENCE_OUT, w_out), max(FENCE_IN, WALL_IN)
    bar = box(bar_lo, DECK_TOP, bar_hi-bar_lo, 2.5, width, x)    # 2.5 mm: stays under the laptop bottom (z 54) when the wall is offset; rests on the deck and outer wall top
    s = foot.fuse(bar).fuse(wall).clean()
    plate_lo, plate_hi = seat_plate_extent()                      # never occupy the seat peg's shoulder plate (+0.3 mm)
    s = s.cut(box(plate_lo-PEG_GAP, DECK_TOP-1, plate_hi-plate_lo+2*PEG_GAP, 12, width, x)).clean()   # the whole seat head envelope
    assert s.isValid() and len(s.Solids()) == 1, 'fence peg split by the seat clearance cut'
    return lean(s)

def bore(xc, z, y_from, length):
    return lean(cq.Solid.makeCylinder(BORE_R, length, cq.Vector(xc, y_from, z), cq.Vector(0,1,0)))
def pushouts(xc):
    return [lean(cq.Solid.makeCylinder(F['pushout_radius_mm'], DECK_TOP, cq.Vector(xc, (a+b)/2, -30), cq.Vector(0,0,1))) for a, b in ((FENCE_OUT, FENCE_IN), (SEAT_CH[0], SEAT_CH[1]))]
def cut_lock(frame, seat, fence, xc):
    """One horizontal pin from the outer face through outer wall, fence foot, web and seat foot."""
    frame_bore = bore(xc, PIN_Z, Y_OUT-1, PIN_LEN+2)
    frame = frame.cut(frame_bore)
    for h in pushouts(xc): frame = frame.cut(h)
    seat = seat.cut(bore(xc, PIN_Z-PIN_CAM, Y_OUT-1, PIN_LEN+2)).clean()
    fence = fence.cut(bore(xc, PIN_Z-PIN_CAM, Y_OUT-1, PIN_LEN+2)).clean()
    return frame.clean(), seat, fence
def socket_void(xc, width=B, x=0):
    """What the D9 builder subtracts from its fused cradle: channels, bore and push-outs."""
    _, _, void = frame_parts(width, x)
    deck_clear = box(Y_OUT+OUT_W, DECK_TOP, RAIL_IN-(Y_OUT+OUT_W), 12, width, x)   # the D9 cap is unleaned; shave it flush with the leaned deck
    v = lean(void.fuse(deck_clear)).fuse(bore(xc, PIN_Z, Y_OUT-1, PIN_LEN+2))
    for h in pushouts(xc): v = v.fuse(h)
    return v.clean()
def pin_place(shape, xc):
    return lean(shape.rotate((0,0,0),(1,0,0),-90).translate((xc, Y_OUT, PIN_Z)))

LOCK_X = args.lock_x if args.lock_x is not None else B/2
frame = frame_solid(); seat = seat_peg(); liners = {k: fence_peg(k) for k in ('plug', 'far')}
frame, seat, liners['plug'] = cut_lock(frame, seat, liners['plug'], LOCK_X)
_, _, liners['far'] = cut_lock(frame_solid(), seat_peg(), liners['far'], LOCK_X)
void = socket_void(LOCK_X)
for name, sh in (('frame', frame), ('seat', seat), ('fence plug', liners['plug']), ('fence far', liners['far'])):
    assert sh.isValid() and len(sh.Solids()) == 1, name
the_pin = pin_place(pin(PIN_LEN, PIN_MARKS), LOCK_X)
assert Y_OUT + PIN_LEN > SEAT_CH[1] + 1.5, 'pin must pass fully through the seat foot into the tower beyond'
inserts = {k: seat.fuse(liners[k]).clean() for k in ('plug', 'far')}

# ---- Receipts ---------------------------------------------------------------
receipts = {}
for kind in ('plug', 'far'):
    pieces = {'seat': seat, 'liner': liners[kind]}
    assert seat.intersect(liners[kind]).Volume() < 1e-6, (kind, 'seat block interferes with liner')
    for name, piece in pieces.items():
        assert piece.intersect(frame).Volume() < 1e-6, (kind, name, 'interferes with frame')
        cam = piece.intersect(the_pin).Volume()      # the 0.15-mm cam offset shows as a thin designed interference
        assert cam < 40.0, (kind, name, 'pin interference beyond the cam offset', cam)
        moves = {}
        holder = frame.fuse(the_pin).fuse(seat if name == 'liner' else liners[kind])
        for label, d in (('+y',(0,1,0)),('-y',(0,-1,0)),('+z',(0,0,1)),('-z',(0,0,-1)),('+x',(1,0,0)),('-x',(-1,0,0))):
            v = lean_dir(d) if label[1] != 'x' else cq.Vector(*d)
            moves[label] = round(piece.translate((v*2.0).toTuple()).intersect(holder).Volume(), 2)
        assert all(v > 1.0 for v in moves.values()), (kind, name, moves)   # blocked within 2 mm in every direction
        receipts[f'{kind}_{name}'] = {'pin_cam_interference_mm3': cam, 'blocked_2mm_move_overlap_mm3': moves}

# Laptop checks at the chosen lean, like R2..R5, for each end (plug insert at x=0 end).
laptop = solid_box(0,T/2-TD,H,W,TD,P['laptop_depth']).edges('|Y').fillet(4)
if not DEMO:
    laptop = laptop.cut(solid_box(30,-7,H-1,W-60,17,5))
    heel = [(curve[0][0],H-6),(curve[-1][0],H-6)]+list(reversed(curve))
    for x, width in [(0,30),(W-30,30)]: laptop = laptop.cut(poly(heel,width,x))
    laptop = lean(laptop.val())
else:
    heel = [(curve[0][0]+DY,H-6),(curve[-1][0]+DY,H-6)]+[(yy+DY,zz) for yy,zz in reversed(curve)]
    for x, width in [(0,30),(W-30,30)]: laptop = laptop.cut(poly(heel,width,x))
    laptop = lean(laptop.val())
feet, keepouts = [], []
for f in C['rubber_feet']:
    a,b = f['untilted_case_relative_bounds_mm']
    feet.append(lean(solid_box(a[0],a[1],H+a[2],b[0]-a[0],b[1]-a[1],b[2]-a[2]).val()))
    keepouts.append(lean(solid_box(a[0]-2,a[1]-2,H+a[2]-2,b[0]-a[0]+4,b[1]-a[1]+4,b[2]-a[2]+4).val()))
ends = {'plug': (xstarts[0], inserts['plug']), 'far': (xstarts[1], inserts['far'])}
checks, motion = {}, []
for kind, (x, ins) in ends.items():
    q = frame.translate((x,0,0)).fuse(ins.translate((x,0,0))).clean()
    checks[kind] = dict(laptop_overlap_mm3=q.intersect(laptop).Volume(), rubber_foot_overlap_mm3=sum(q.intersect(f).Volume() for f in feet),
        expanded_foot_keepout_overlap_mm3=sum(q.intersect(f).Volume() for f in keepouts),
        seat_contact_probe_mm3=q.translate((0,.02*math.sin(A),.02*math.cos(A))).intersect(laptop).Volume())
    for lift in [0,.25,.5,1,2,3,5,10,20,40]:
        delta = (0,lift*math.sin(A),lift*math.cos(A))
        motion.append(dict(end=kind,lift_mm=lift,laptop_overlap_mm3=q.intersect(laptop.translate(delta)).Volume(),foot_keepout_overlap_mm3=sum(q.intersect(f.translate(delta)).Volume() for f in keepouts)))
if not DEMO:
    assert all(c['laptop_overlap_mm3']<.001 and c['rubber_foot_overlap_mm3']<.001 and c['expanded_foot_keepout_overlap_mm3']<.001 for c in checks.values()), checks
    assert all(m['laptop_overlap_mm3']<.001 and m['foot_keepout_overlap_mm3']<.001 for m in motion), motion
else:
    assert all(c['laptop_overlap_mm3']<.001 for c in checks.values()), ('demo laptop box overlaps the pegs or frame', checks)
# Tip receipt at the plug end and docking sweep (as R5).
pivot_y = curve[0][0]; plug = frame.translate((xstarts[0],0,0)).fuse(inserts['plug'].translate((xstarts[0],0,0)))
tip_hits = {deg: plug.intersect(laptop.rotate((0,pivot_y,H),(1,pivot_y,H),-deg)).Volume() for deg in (2,4,6,8,10)}
assert DEMO or max(tip_hits.values()) > 1.0, tip_hits
undock = P['undocked_x_offset_mm']; sweep = {}
for end, x0 in (('plug_end', xstarts[0]), ('far_end', xstarts[1])):
    worst = None
    for dx in np.arange(0, undock+1e-9, 2.0):
        for f in C['rubber_feet']:
            a, b_ = f['untilted_case_relative_bounds_mm']
            g = float(max(x0-(b_[0]+dx), (a[0]+dx)-(x0+B))); worst = g if worst is None else min(worst, g)
    sweep[end] = {'min_x_clearance_to_any_foot_mm': worst, 'foot_strip_overlaps_bracket_x_range_during_docking': bool(worst < 0)}
assert DEMO or not sweep['plug_end']['foot_strip_overlaps_bracket_x_range_during_docking']
# Lid clearance at the bearing wall is S regardless of lean.
lid_probe = lean(solid_box(xstarts[0], T/2, H+2, B, S-.05, 70).val())
assert lid_probe.intersect(plug).Volume() < 1e-6
if DEMO:
    outer_reach = min(WALL_IN-FENCE_T, FENCE_OUT)
    print(json.dumps({'demo_thickness_mm': TD, 'lid_face_y_mm': T/2, 'underside_face_y_mm': T/2-TD, 'fence_wall_y_mm': [WALL_IN-FENCE_T, WALL_IN], 'seat_curve_y_mm': [curve[0][0]+DY, curve[-1][0]+DY], 'stand_outer_face_y_mm': Y_OUT, 'fence_wall_hangs_outboard_mm': max(0.0, Y_OUT-(WALL_IN-FENCE_T))}))

# ---- Exports ----------------------------------------------------------------
def norm(shape):
    b = shape.BoundingBox(); return shape.translate((-b.xmin,-b.ymin,-b.zmin))
def print_pose(shape):
    printed = shape.rotate((0,0,0),(0,1,0),-90); b = printed.BoundingBox()
    return printed.translate((-b.xmin,-b.ymin,-b.zmin))
outputs = {}
def export(name, shape, pose):
    step = R/f'{name}{TAG}.step'; stl = R/f'{name}{TAG}.stl'
    cq.exporters.export(shape, str(step)); cq.exporters.export(pose, str(stl), tolerance=.04, angularTolerance=.1)
    mesh = trimesh.load_mesh(stl); assert mesh.is_watertight and len(mesh.split())==1, name
    outputs[name] = {'step': step.name, 'stl': stl.name, 'print_bounds_mm': mesh.extents.tolist(), 'volume_cm3': shape.Volume()/1000, 'sha256_stl': hashlib.sha256(stl.read_bytes()).hexdigest()}
    return mesh
export('D8-R7-frame', frame, print_pose(frame))
export('D8-R7-seat-peg', seat, print_pose(seat))
for kind, ln in liners.items(): export(f'D8-R7-fence-peg-{kind}', ln, print_pose(ln))
if args.d9_source:
    cq.exporters.export(void, str(R/f'D8-R7-socket-void{TAG}.step'))
else:
    export('D8-R7-insert-pin', the_pin, norm(pin(PIN_LEN, PIN_MARKS).rotate((0,0,0),(1,0,0),90)))

report = dict(passed=True, revision='R7 peg bracket: frame + seat peg + fence peg', lean_deg=LEAN, base_thickness_mm=BT, lock_x_mm=LOCK_X,
    rail_inner_face_unleaned_y_mm=RAIL_IN, fence_inner_face_unleaned_y_mm=FENCE_IN, stand_outer_face_unleaned_y_mm=Y_OUT,
    socket=dict(deck_top_z_mm=DECK_TOP, outer_face_y_mm=Y_OUT, channel_depth_mm=CH_D, peg_clearance_mm=PEG_GAP,
                fence_channel_y_mm=[FENCE_OUT, FENCE_IN], seat_channel_y_mm=SEAT_CH, fence_wall_thickness_mm=FENCE_T,
                pin=dict(length_mm=PIN_LEN, bore_mm=2*BORE_R, axis='+Y from the outer face', z_mm=PIN_Z, cam_offset_mm=PIN_CAM, tip_y_mm=Y_OUT+PIN_LEN, outer_wall_mm=OUT_W),
                pushout_radius_mm=F['pushout_radius_mm']),
    fence_top_z_mm=FENCE_TOP, insert_receipts=receipts, checks=checks, motion=motion, tip_overlap_by_deg_mm3=tip_hits, docking_sweep=sweep,
    inside_clear_gap_mm=gap, center_spacing_mm=xstarts[1]-xstarts[0], outputs=outputs,
    input_sha256={str(p.relative_to(D)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__), R/'fit-parameters.json', R2/'seat-profile.json', D/'parameters.json', D/'contact-profiles.json', D/'geometry.json']},
    scope='Modular bracket: frame + insert nominal CAD checks only; physical fit, insert retention, load and stability untested.')
(R/f'checks{TAG}.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')

colors = {'frame': (62,117,139), 'plug': (193,128,49), 'far': (180,75,63)}
scene_objs = [(frame.translate((x,0,0)), colors['frame']) for x in xstarts] + [(seat.translate((x,0,0)), (95,150,120)) for x in xstarts] + [(liners['plug'].translate((xstarts[0],0,0)), colors['plug']), (liners['far'].translate((xstarts[1],0,0)), colors['far'])] + [(the_pin.translate((x,0,0)), (115,132,141)) for x in xstarts] + [(laptop, (188,195,198))]
im,_ = render(scene_objs, (1500,950), (.8,-1,.65), pad=65)
canvas = Image.new('RGB',(1500,1070),'#f7f7f7'); canvas.paste(im,(0,75)); d = ImageDraw.Draw(canvas)
d.text((35,20), f'D8 R7 | frame (blue) + seat peg (green) + fence peg (amber tall plug end, red short far end) | lean {LEAN:g} deg | laptop {TD:.1f} mm thick' + (' (demo)' if DEMO else ''), font=font(29,True), fill='#20313c')
d.text((35,1020), f'Inside gap {gap:.2f} mm | pegs drop into {CH_D:g}-mm channels, one horizontal pin through the outer wall and both feet, {PIN_CAM:g}-mm cam offset', font=font(23), fill='#20313c')
canvas.save(R/f'D8-R7{TAG}-assembly.png')
im,_ = render([(frame.translate((0,-60,0)), colors['frame']), (seat, (95,150,120)), (liners['plug'].translate((0,40,0)), colors['plug']), (liners['far'].translate((0,70,0)), colors['far'])], (1400,900), (1,-.15,.13), pad=60)
im.save(R/f'D8-R7{TAG}-profiles.png')
im,_ = render([(frame, colors['frame']), (seat, (95,150,120)), (liners['plug'], colors['plug']), (the_pin, (115,132,141))], (1400,900), (1,-.15,.13), pad=60)
im.save(R/f'D8-R7{TAG}-assembled.png')
print(json.dumps({k: v for k, v in report.items() if k in ('lean_deg','socket','fence_top_z_mm','tip_overlap_by_deg_mm3','docking_sweep')}, indent=1))
print(json.dumps({k: {kk: round(vv, 1) if isinstance(vv, float) else vv for kk, vv in v.items() if kk != 'sha256_stl'} for k, v in outputs.items()}))
