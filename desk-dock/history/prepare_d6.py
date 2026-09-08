from pathlib import Path
import json, shutil, hashlib
import numpy as np
import trimesh

repo=Path(r'D:\Code\Modeling\dell-5560-wall-mount')
old=repo/'desk-dock/D5'; new=repo/'desk-dock/D6'; new.mkdir(exist_ok=True)
for name in ['build.py','validate.py','alignment_check.py','contact_study.py','animate.py','raster.py','export_viewer.py','parameters.json','contact-profiles.json','extract_contacts.py','.gitignore']:
    shutil.copy2(old/name,new/name)
source=Path(r'D:\Code\Modeling\local-transfer\reference-assets\laptop.glb')
s=trimesh.load(source)
def node(n):
    t,g=s.graph[n]; m=s.geometry[g].copy();m.apply_transform(t);m.apply_scale(1000);return m
rear=float(node('Dell4649').bounds[0,2])
ports=[]
for name,n,side,kind in [('TB4_rear','Dell4768','keyboard-left','Thunderbolt 4'),('TB4_front','Dell4694','keyboard-left','Thunderbolt 4'),('USB_C_right','Dell4638','keyboard-right','USB 3.2 Gen 2 / DisplayPort; not Thunderbolt')]:
    m=node(n); c=m.bounds.mean(0)
    ports.append(dict(name=name,node=n,side=side,kind=kind,source_bounds_mm=m.bounds.tolist(),source_center_mm=c.tolist(),case_offset_from_rear_mm=float(c[2]-rear),case_y_mm=float(c[1]-22.17/2),opening_height_mm=float(m.extents[2]),opening_thickness_mm=float(m.extents[1]),case_edge_x_mm=0 if side=='keyboard-left' else 353.68))
data=dict(source_url='https://content.hmxmedia.com/precision-16-5680-laptop-AR/gltf/precision-16-5680-laptop-AR.glb',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),retrieved_utc='2026-09-08',rear_case_datum_source_mm=rear,ports=ports,source_to_untilted_case_translation_mm=[353.68/2,-22.17/2,-rear],linear_transform_determinant=1,limits='Visualization mesh dimensions, not factory toleranced openings. Labels corroborated by Dell left/right owner manual views.')
(new/'port-study.json').write_text(json.dumps(data,indent=2)+'\n')
p=json.loads((new/'parameters.json').read_text())
p.update(revision='D6 - source-handed ports and consistent camera projection',port_from_rear_case=ports[0]['case_offset_from_rear_mm'],second_port_from_rear_case=ports[1]['case_offset_from_rear_mm'],port_y=ports[0]['case_y_mm'],docking_travel_direction='-X',undocked_x_offset_mm=18)
p['coordinate_frame']=dict(x='Positive from keyboard-left/plug end (x=0) toward keyboard-right end (x=353.68). Plug appears screen-right in a lid-facing view.',y='Positive toward lid/user/fans; negative toward underside/intake.',z='Positive upward from desk; hinge down.',construction='Preserve Dell source handedness; translation then rigid lean, no reflection. Positive depth_adjustment inserts plug along +X; laptop docks along -X.')
p['notes']='D6 re-extracts all three USB-C centers from the source mesh, preserving handedness. Port types follow Dell owner manual. Source visualization dimensions require physical calibration; no reflection is used to orient the laptop.'
(new/'parameters.json').write_text(json.dumps(p,indent=2)+'\n')
def edit(name,fn):
    f=new/name; f.write_text(fn(f.read_text(encoding='utf-8')),encoding='utf-8')
def build(t):
    t=t.replace('D5','D6').replace('Exported +X runs toward the far/plug end in the lid-facing view','Exported +X runs away from keyboard-left/plug end')
    t=t.replace("contacts=json.loads((R/'contact-profiles.json').read_text())", "contacts=json.loads((R/'contact-profiles.json').read_text())\nport_study=json.loads((R/'port-study.json').read_text())")
    t=t.replace("inner.val().mirror('YZ',(W/2,0,0))","inner.val()")
    t=t.replace("leaned(keep).mirror('YZ',(W/2,0,0))","leaned(keep)")
    start=t.index('for zport in [H+p['); end=t.index('# Replace the generic heel',start)
    t=t[:start]+'''# Each opening retains its own source center and rounded USB-C envelope.
for port in port_study['ports']:
    x=-1 if port['side']=='keyboard-left' else W-7
    z=H+port['case_offset_from_rear_mm']; y=port['case_y_mm']
    h=port['opening_height_mm']; w=port['opening_thickness_mm']
    opening=box(x,y-w/2,z-h/2,8,w,h).edges('|X').fillet(w/2-.05)
    laptop=laptop.cut(opening)
''' +t[end:]
    start=t.index('# D6 corrects the handedness'); end=t.index('# Replace ambiguous',start)
    t=t[:start]+'''# Preserve source handedness. Dell keyboard-left is source -X, hence x=0.
# With a right-handed camera at +Y and +Z up, x=0 appears screen-right.
# Laptop withdrawal is +X; insertion is -X. No final reflection is permitted.
''' +t[end:]
    return t
edit('build.py',build)
edit('export_viewer.py',lambda t:t.replace('desk-dock-d5','desk-dock-d6').replace("revision='D5'","revision='D6'").replace("units='mm',parts=entries","units='mm',coordinate_frame=build.p['coordinate_frame'],undocked_x_offset_mm=18,laptop_lean_deg=build.LEAN,parts=entries"))
edit('alignment_check.py',lambda t:t.replace('shift=(-18,','shift=(18,'))
edit('contact_study.py',lambda t:t.replace('D5','D6').replace('build.W-hi[0]','lo[0]'))
edit('raster.py',lambda t:t.replace("FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'", "FONT=next(str(p) for p in [Path('C:/Windows/Fonts/arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')] if p.exists())").replace("BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'", "BOLD=next(str(p) for p in [Path('C:/Windows/Fonts/arialbd.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')] if p.exists())").replace('right=np.cross(cam,[0,0,1.])','right=np.cross([0,0,1.],cam)').replace('up=np.cross(right,cam)','up=np.cross(cam,right)'))
edit('animate.py',lambda t:t.replace('D5','D6').replace('[-22,build.W+52]','[-52,build.W+22]').replace('(1.15,2.4,.95)','(-1.15,2.4,.95)').replace('(1.25,2.4,.7)','(-1.25,2.4,.7)').replace("a['shape'].BoundingBox().xmax>build.W-20","a['shape'].BoundingBox().xmin<20").replace('[build.W-35,build.W+50]','[-50,35]').replace('(-18,','(18,').replace('(-18*','(18*').replace('(build.W+15,20,build.P+15)','(-15,20,build.P+15)'))
edit('extract_contacts.py',lambda t:t.replace('X before D3 reflection','X preserving source handedness').replace('reflects X and applies lean','applies lean without reflection'))
contacts=json.loads((new/'contact-profiles.json').read_text()); contacts['datum']='Source handedness preserved. X translated by W/2; Y about closed-envelope midplane; Z from rear case datum. Build adds seat height and rigid lean; no reflection.'
(new/'contact-profiles.json').write_text(json.dumps(contacts,indent=2)+'\n')
def validate(t):
    t=t.replace('(-18,z)','(18,z)').replace('(-x,0)','(x,0)').replace('Precision_5680_D5.step','Precision_5680_D6.step')
    start=t.index('# Check orientation independently'); end=t.index('back=cq.importers',start)
    t=t[:start]+'''# Cross-check against source coordinates, not a reflected CAD expectation.
import numpy as np
from raster import render
plug=next(a['shape'] for a in parts if a['name']=='USB_C_shell_REFERENCE')
assert plug.BoundingBox().xmin<0 and 0<plug.BoundingBox().xmax<7
assert all(a['shape'].Center().y>build.T/2 for a in parts if 'fan_frame' in a['name'])
port_probes=[]
for port in build.port_study['ports']:
    left=port['side']=='keyboard-left'
    assert (port['source_center_mm'][0]<0)==left
    z=build.H+port['case_offset_from_rear_mm']; y=port['case_y_mm']
    x=.2 if left else build.W-1
    other=build.W-1 if left else .2
    probe=build.leaned(build.box(x,y-.5,z-.5,.8,1,1).val())
    opposite=build.leaned(build.box(other,y-.5,z-.5,.8,1,1).val())
    v=overlap(laptop,probe); ov=overlap(laptop,opposite)
    assert v<1e-6 and ov>.79,(port['name'],v,ov)
    port_probes.append(dict(name=port['name'],side=port['side'],opening_material_mm3=v,opposite_edge_material_mm3=ov))
# Standard +Y lid camera sees the source -X (keyboard-left) end at screen-right.
_,project=render([(laptop,(180,180,180))],(300,250),(0,1,0))
screen=project([[0,0,build.P],[build.W,0,build.P]])
assert screen[0,0]>screen[1,0]
assert all(not row['collisions'] and not row['expanded_foot_keepout_collisions'] for row in motion),motion
assert not hits,hits
''' +t[end:]
    t=t.replace("'docking_direction':'+X'","'docking_direction':'-X'").replace("'port_probes':port_probes","'port_probes':port_probes,'lid_camera_keyboard_left_screen_right':True,'source_handedness_preserved':True")
    t=t.replace("'scope':'Simplified nominal", "'scope':'Simplified nominal")
    return t
edit('validate.py',validate)
print('Prepared D6 source; ports:',[(v['name'],v['case_edge_x_mm'],v['case_offset_from_rear_mm']) for v in ports])
