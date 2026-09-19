"""Export the D9 P5 assembly (generated/*.step, assembly coordinates) to the site's indexed mesh format:
docs/models/desk-dock-p5/model.json + model.bin (+ provenance.json). Reference laptop and fans are rebuilt from parameters."""
import json,struct,hashlib,math,re,sys
from pathlib import Path
import cadquery as cq
HERE=Path(__file__).resolve().parent;GEN=HERE/'generated';OUT=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'viewer-export';OUT.mkdir(parents=True,exist_ok=True)
P=json.loads((HERE/'source-inputs/parameters.json').read_text());man=json.loads((GEN/'manifest.json').read_text())
LEAN=P['laptop_lean_deg'];FY,FZ,ANG=70.0,72.0,math.radians(108);EX=(0,math.cos(math.radians(18)),math.sin(math.radians(18)))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def posed(s,fx):return s.rotate((0,0,0),(1,0,0),108).translate((fx,FY,FZ))
def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,cq.Vector(x,y,z))
def cz(x,y,z,r,l):return cq.Solid.makeCylinder(r,l,cq.Vector(x,y,z),cq.Vector(0,0,1))
skip=lambda n:any(k in n for k in ('fit-fixture','T-joint-fit','cradle-end-trial'))
COL={'centre':[150,96,70],'cradle':[92,110,122],'plenum':[132,148,158],'guard':[70,84,92],'tie':[110,96,80],'pin':[214,178,92],'key':[236,206,120],'peg':[196,120,88],'lock':[214,178,92],'laptop':[46,52,58],'fan':[40,40,44]}
def group(n):
    if n=='splice-plate':return 'centre'
    if n=='center-contact':return 'peg'
    if 'outer-cradle' in n:return 'cradle'
    if 'inner-shell' in n:return 'plenum'
    if 'fan-guard' in n:return 'guard'
    if '-tie-' in n:return 'tie'
    if 'insert-pin' in n:return 'lock'
    if n.endswith('-pin'):return 'pin'
    if n.endswith('-key'):return 'key'
    if '-peg' in n:return 'peg'
    return 'other'
def explode(n,g,c):
    m=1 if n.startswith('M1') or 'front' in n else 2;s=-1 if m==1 else 1
    if g=='centre':return [0,0,45]
    if g=='cradle':return [s*70,0,0]
    if g=='plenum':return [-s*35,0,0]
    if g=='guard':return [0,EX[1]*100,EX[2]*100]
    if g=='tie':return [0,0,-60]
    if g=='peg':return [0,math.sin(math.radians(LEAN))*70,math.cos(math.radians(LEAN))*70]
    if g=='lock':return [0,-70,0]
    if 'fan' in n:return [0,EX[1]*130,EX[2]*130] if g=='pin' else [0,EX[1]*150,EX[2]*150+15]
    if 'seam' in n:return [0,0,90] if g=='pin' else [0,0,110]
    if 'frame' in n:return [s*90,0,0] if g=='pin' else [s*90,0,30]
    if 'lap' in n:return [0,-70,0] if g=='pin' else [0,-70,30]
    return [0,0,60]
NOTES={r['part']:r.get('manufacturing','') for r in man['parts']}
data=bytearray();entries=[];prov={}
def emit(name,shape,g,ref=False,tol=(0.35,0.2)):
    verts,faces=shape.tessellate(*tol)
    off=len(data)
    for v in verts:data.extend(struct.pack('<fff',v.x,v.y,v.z))
    ioff=len(data)
    for f in faces:data.extend(struct.pack('<III',*f))
    b=shape.BoundingBox();c=[(b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2,(b.zmin+b.zmax)/2]
    entries.append({'name':name,'group':g,'color':COL[g],'reference':ref,'positionOffset':off,'vertexCount':len(verts),'indexOffset':ioff,'indexCount':3*len(faces),'center':c,'explode':explode(name,g,c) if not ref else [0,0,0],'note':NOTES.get(name,'')})
    print(name,len(faces),'tris',flush=True)
for r in man['parts']:
    n=r['part']
    if skip(n):continue
    shape=cq.importers.importStep(str(GEN/r['step'])).val();g=group(n)
    emit(n,shape,g,tol=(0.18,0.12) if g in('cradle','plenum','guard','tie') else (0.15,0.1));prov[n]=sha(GEN/r['step'])
# reference bodies
T=P['laptop_thickness'];W=P['laptop_width']
laptop=cq.Workplane('XY').add(box(0,-T/2,62,W,T,232.33)).edges('|Y').fillet(4).val().rotate((0,0,54),(1,0,54),-LEAN)
emit('Precision_5680_REFERENCE',laptop,'laptop',ref=True,tol=(0.5,0.3))
for i,fx in enumerate(P['fan_centers_x'],1):
    fan=posed(box(-60,-60,-17.5,120,120,25).cut(cz(0,0,-17.6,56.5,25.2)).cut(cz(0,0,-17.7,20,25.4)),fx)
    emit(f'fan_120mm_M{i}',fan,'fan',ref=True,tol=(0.5,0.3))
up=[0,math.sin(math.radians(LEAN)),math.cos(math.radians(LEAN))]
manifest={'revision':'D9-P5','units':'mm','coordinate_frame':'assembly: X along the dock (plug end at low X), Y toward the lid, Z up','laptop_lean_deg':LEAN,'undocked_x_offset_mm':18,'laptop_up':up,'exhaust_axis':list(EX),'fan_centers_x':P['fan_centers_x'],
          'groups':{'centre':'Splice plate (epoxied); the centre contact is with the pegs','cradle':'Outer cradle shells (R7 frame ends)','plenum':'Inner plenum halves','guard':'Fan guards','tie':'Front and rear ties','pin':'Printed pins','key':'Locking keys','peg':'Seat and fence pegs','lock':'Peg lock pins','laptop':'Laptop reference','fan':'120 x 25 mm fans (purchased)'},'parts':entries}
(OUT/'model.bin').write_bytes(bytes(data));(OUT/'model.json').write_text(json.dumps(manifest))
(OUT/'provenance.json').write_text(json.dumps({'builder_sha256':sha(HERE/'build_d9.py'),'manifest_sha256':sha(GEN/'manifest.json'),'step_sha256':prov,'tessellation':'cadquery tessellate: shells and ties 0.18/0.12, small parts 0.15/0.1, reference bodies 0.5/0.3','model_bin_bytes':len(data)},indent=1))
print('parts',len(entries),'bytes',len(data),'MB %.1f'%(len(data)/1e6))
