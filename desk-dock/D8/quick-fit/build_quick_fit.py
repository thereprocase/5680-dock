"""Two 38.1 mm wide, edge-printed D8 fit/footprint brackets; no main CAD changes."""
from pathlib import Path
import sys,json,math,hashlib
import cadquery as cq
import trimesh
R=Path(__file__).resolve().parent;D=R.parent
sys.path.insert(0,str(D))
from raster import render,font
from PIL import Image,ImageDraw
P=json.loads((D/'parameters.json').read_text(encoding='utf-8'))
C=json.loads((D/'contact-profiles.json').read_text(encoding='utf-8'))
H=P['rear_case_seat_z'];T=P['laptop_thickness'];W=P['laptop_width'];B=38.1
G=json.loads((D/'geometry.json').read_text(encoding='utf-8'))
items=[a for a in G['parts'] if a['name'].startswith(('01_','02_','bridge_key')) and '_desk_pad_' not in a['name']]
lo=[min(a['bounds_mm'][i] for a in items) for i in range(3)];hi=[max(a['bounds_mm'][i+3] for a in items) for i in range(3)]
y0,y1=lo[1],hi[1];xstarts=[lo[0],hi[0]-B];gap=xstarts[1]-xstarts[0]-B

def poly(pts):return cq.Workplane('YZ').polyline(pts).close().extrude(B).val()
def box(y,z,dy,dz):return poly([(y,z),(y+dy,z),(y+dy,z+dz),(y,z+dz)])
def lean(s):return s.rotate((0,0,H),(1,0,H),-P['laptop_lean_deg'])
curve=[(a[0],H+min(c['rear_curve_local_yz_mm'][j][1] for c in C['curves'])) for j,a in enumerate(C['curves'][0]['rear_curve_local_yz_mm'])]
# All structural members have a constant cross section across the 1.5 inch width.
s=box(y0,-5,y1-y0,4)
s=s.fuse(box(-6,-2,12,53))
s=s.fuse(lean(box(-15,46,32,5)))
s=s.fuse(lean(poly([(curve[0][0],49),(curve[-1][0],49)]+list(reversed(curve)))))
s=s.fuse(lean(poly([(-T/2-3,47),(-T/2-3,66),(-T/2-1,66),(-T/2-.25,62),(-T/2-.25,47)])))
s=s.fuse(lean(box(T/2,48,4,86)))
# Diagonal to the footprint toe braces the laptop-side rail.
a=math.radians(P['laptop_lean_deg']);top_y=(T/2+2)*math.cos(a)+(134-H)*math.sin(a)
s=s.fuse(poly([(top_y-1,129),(top_y+3,134),(y1-1,-1),(y1-7,-1)]))
# Small height flag reaches the complete body/fan/clip envelope.
s=s.fuse(box(top_y+1,131,3,hi[2]-131)).clean()
s=s.cut(cq.Workplane('YZ',origin=(B-.5,43,-3)).text(f'GAP {gap:.2f} mm',2.4,.6,font='Arial',combine=False).val()).clean()
assert s.isValid() and len(s.Solids())==1
# Print on the broad profile: original X becomes print Z, no supports.
printed=s.rotate((0,0,0),(0,1,0),-90)
b=printed.BoundingBox();printed=printed.translate((-b.xmin,-b.ymin,-b.zmin))
cq.exporters.export(printed,str(R/'D8-quick-fit-bracket-print-TWO.stl'),tolerance=.04,angularTolerance=.1)
cq.exporters.export(s,str(R/'D8-quick-fit-bracket.step'))
mesh=trimesh.load_mesh(R/'D8-quick-fit-bracket-print-TWO.stl')
assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split())==1
assert max(mesh.extents)<256
# Read the validated D8 reference without rebuilding the production dock.
cache=Path(sys.argv[1]);laptop=cq.Shape.importBrep(str(cache/'Precision_5680_REFERENCE.brep'))
feet=[cq.Shape.importBrep(str(p)) for p in cache.glob('RUBBER_FOOT*.brep')]
placed=[s.translate((x,0,0)) for x in xstarts]
checks=[]
for bracket in placed:
 checks.append(dict(laptop_overlap_mm3=bracket.intersect(laptop).Volume(),rubber_foot_overlap_mm3=sum(bracket.intersect(f).Volume() for f in feet),seat_contact_probe_mm3=bracket.translate((0,.02*math.sin(a),.02*math.cos(a))).intersect(laptop).Volume()))
assert all(c['laptop_overlap_mm3']<.001 and c['rubber_foot_overlap_mm3']<.001 and c['seat_contact_probe_mm3']>.01 for c in checks),checks
report=dict(passed=True,quantity=2,identical=True,bracket_width_mm=B,inside_clear_gap_mm=gap,center_spacing_mm=xstarts[1]-xstarts[0],outside_width_mm=hi[0]-lo[0],footprint_depth_mm=y1-y0,height_above_desk_mm=hi[2]+5,laptop_left_edge_from_left_bracket_outer_edge_mm=-lo[0],laptop_right_edge_from_right_bracket_outer_edge_mm=hi[0]-W,nominal_lean_degrees=P['laptop_lean_deg'],solid_volume_each_cm3=s.Volume()/1000,solid_PETG_mass_pair_g=s.Volume()/1000*1.27*2,print_bounds_mm=mesh.extents.tolist(),checks=checks,scope='Body/fans/grilles/fasteners envelope; excludes removable connector. Nominal CAD fit only, not a load test.')
(R/'checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
objects=[(q,(62,117,139)) for q in placed]+[(laptop,(188,195,198))]
im,_=render(objects,(1500,950),(.8,-1,.65),pad=65)
canvas=Image.new('RGB',(1500,1070),'#f7f7f7');canvas.paste(im,(0,75));d=ImageDraw.Draw(canvas)
d.text((35,20),'D8 quick-fit stand | Print the same bracket twice',font=font(29,True),fill='#20313c')
d.text((35,1020),f'Inside gap {gap:.2f} mm ({gap/25.4:.3f} in) | Each bracket 38.1 mm / 1.5 in wide',font=font(23),fill='#20313c')
canvas.save(R/'D8-quick-fit.png')
im,_=render([(s,(62,117,139))],(1100,900),(1,-.15,.13),pad=60);im.save(R/'D8-quick-fit-profile.png')
print(json.dumps(report),flush=True)
