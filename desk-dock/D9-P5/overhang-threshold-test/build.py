"""Four cantilever wedges on a wall: which slopes does this plate's Orca profile support?"""
import cadquery as cq, math, sys, json, hashlib, shutil, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/quartet-team/architect'))
from prepare_coupon_plate import mesh,NS
parts=[]
for ang in (30,39,45,55):
    run=15*math.tan(math.radians(ang))   # 15 mm tall wedge, angle from vertical
    wall=cq.Workplane('XY').box(30,8,40,centered=(True,True,False)).val()
    wedge=cq.Workplane('XZ',origin=(0,-4,0)).polyline([(-15,25),(15,25),(15,25-15),(15-run,25)] if False else [(-15,25),(15,25),(15,10)]).close().extrude(-8).val()
    # cantilever: horizontal top face at z=25, sloped underside from (15,10) up to... use explicit: block top z=25..40 solid wall; wedge under a 15-mm shelf
    shelf=cq.Workplane('XY').box(15,8,15,centered=(False,True,False)).translate((15,0,25)).val()          # shelf x 15..30, z 25..40, hangs off the wall face at x=15
    gus=cq.Workplane('XZ',origin=(0,-4,0)).polyline([(15,25),(30,25),(15,25-run)]).close().extrude(-8).val()  # underside slope from shelf tip down to the wall
    body=wall.fuse(shelf).fuse(gus).clean()
    name=f'wedge-{ang}deg';cq.exporters.export(body,str(HERE/(name+'.stl')));parts.append(name)
root=ET.Element(f'{{{NS}}}model',{'unit':'millimeter','xml:lang':'en-US'});res=ET.SubElement(root,f'{{{NS}}}resources');build=ET.SubElement(root,f'{{{NS}}}build');objs=[]
for i,name in enumerate(parts,1):
    v,f,lo,hi=mesh(HERE/(name+'.stl'));x,y=40+(i-1)*50,60;shift=[x-lo[0],y-lo[1],-lo[2]]
    o=ET.SubElement(res,f'{{{NS}}}object',{'id':str(i),'type':'model','name':name});m=ET.SubElement(o,f'{{{NS}}}mesh');vv=ET.SubElement(m,f'{{{NS}}}vertices');ff=ET.SubElement(m,f'{{{NS}}}triangles')
    for p in v:ET.SubElement(vv,f'{{{NS}}}vertex',dict(zip(('x','y','z'),(format(n,'.9g') for n in p))))
    for t in f:ET.SubElement(ff,f'{{{NS}}}triangle',dict(zip(('v1','v2','v3'),map(str,t))))
    ET.SubElement(build,f'{{{NS}}}item',{'objectid':str(i),'transform':'1 0 0 0 1 0 0 0 1 '+' '.join(map(str,shift))})
    objs.append({'name':name,'source':str(HERE/(name+'.stl')),'sha256':hashlib.sha256((HERE/(name+'.stl')).read_bytes()).hexdigest(),'strict':False,'bed_bounds_mm':[[lo[j]+shift[j] for j in range(3)],[hi[j]+shift[j] for j in range(3)]],'translation_mm':shift})
with zipfile.ZipFile(HERE/'input.3mf','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
for n in ('machine.json','process.json','filament.json'):shutil.copy2(HERE.parent/'plates/02'/n,HERE/n)
(HERE/'plate-preparation.json').write_text(json.dumps({'stage':'prepared','objects':objs},indent=2))
print('built',parts)
