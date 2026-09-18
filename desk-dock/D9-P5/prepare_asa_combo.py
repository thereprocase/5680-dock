"""Prepare one calibrated-ASA overnight plate: both inner plenum halves plus the four contact pegs and two insert pins.

Same translation-only placement rules as prepare_and_slice.py (10-mm bed margin, 5-mm brims, no rotation), the
plate-02 process (five walls, 40 % gyroid, snug supports) and the calibrated Polymaker PolyLite ASA filament used
for plate 01. Writes asa/<label>/ ready for slice_asa.py and verify_mixed_plate.py.
"""
from pathlib import Path
import hashlib, json, shutil, sys
import xml.etree.ElementTree as ET
import zipfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'work/quartet-team/architect'))
from prepare_coupon_plate import mesh,NS
GEN=HERE/'generated'
LABEL=sys.argv[1] if len(sys.argv)>1 else '10-inner-pair-pegs'
LAYOUT=[('M1-fence-peg',19,34),('M2-fence-peg',19,62),
        ('M1-seat-peg',19,88),('M2-seat-peg',60,88),
        ('M1-insert-pin',19,120),('M2-insert-pin',50,120),
        ('front-frame-L-pin',19,170),('front-frame-R-pin',40,170),('rear-frame-L-pin',61,170),('rear-frame-R-pin',82,170),
        ('front-frame-L-key',19,213),('front-frame-R-key',34,213),('rear-frame-L-key',49,213),('rear-frame-R-key',64,213),
        ('M1-inner-shell',114,10),('M2-inner-shell',114,131)]
# Peg column on the left starting at y=34 so its 5-mm brim clears the 18 x 28 mm purge exclusion; shells to the right.
folder=HERE/'asa'/LABEL
assert not folder.exists(),folder
folder.mkdir(parents=True)
root=ET.Element(f'{{{NS}}}model',{'unit':'millimeter','xml:lang':'en-US'})
resources=ET.SubElement(root,f'{{{NS}}}resources');build=ET.SubElement(root,f'{{{NS}}}build')
records=[];objects=[];boxes=[]
for oid,(name,x,y) in enumerate(LAYOUT,1):
    path=GEN/(name+'.stl');vertices,faces,lo,hi=mesh(path)
    size=[hi[i]-lo[i] for i in range(3)]
    shift=[x-lo[0],y-lo[1],-lo[2]]
    assert x>=19 and y>=10  # x>=19 keeps every part clear of the P1S front-left purge exclusion (18 x 28 mm) and x+size[0]<=246 and y+size[1]<=246,(name,x,y,size)
    for (n2,x0,y0,x1,y1) in boxes:
        assert x+size[0]+6<=x0 or x1+6<=x or y+size[1]+6<=y0 or y1+6<=y,(name,n2)  # brims may merge between the shells and the peg column
    boxes.append((name,x,y,x+size[0],y+size[1]))
    obj=ET.SubElement(resources,f'{{{NS}}}object',{'id':str(oid),'type':'model','name':name})
    m=ET.SubElement(obj,f'{{{NS}}}mesh');vv=ET.SubElement(m,f'{{{NS}}}vertices');ff=ET.SubElement(m,f'{{{NS}}}triangles')
    for v in vertices:ET.SubElement(vv,f'{{{NS}}}vertex',dict(zip(('x','y','z'),(format(n,'.9g') for n in v))))
    for f in faces:ET.SubElement(ff,f'{{{NS}}}triangle',dict(zip(('v1','v2','v3'),map(str,f))))
    ET.SubElement(build,f'{{{NS}}}item',{'objectid':str(oid),'transform':'1 0 0 0 1 0 0 0 1 '+' '.join(map(str,shift))})
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    records.append({'name':name,'source_sha256':sha,'bounds':[lo,hi],'translation':shift})
    objects.append({'name':name,'source':str(path),'sha256':sha,'strict':False,
                    'bed_bounds_mm':[[lo[i]+shift[i] for i in range(3)],[hi[i]+shift[i] for i in range(3)]],'translation_mm':shift})
with zipfile.ZipFile(folder/'input.3mf','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
shutil.copy2(HERE/'plates/02/machine.json',folder/'machine.json')
shutil.copy2(HERE/'plates/02/process.json',folder/'process.json')  # plate-01 recipe: snug normal supports, 0.35-mm XY (organic trial withdrawn 2026-09-18)
shutil.copy2(HERE/'asa/01/filament.json',folder/'filament.json')
shutil.copy2(HERE/'asa/01/profile-selection.json',folder/'profile-selection.json')
(folder/'geometry-review.md').write_text((HERE/'plates/02/geometry-review.md').read_text()+
 '\nOvernight ASA plate: both inner halves (broad X side on bed, cavity up) with the four contact pegs and two insert\n'
 'pins (profile on bed, as plate 08) and the four frame-end pins and keys (as plate 07). Whole-plate 40 % gyroid: the pegs,\n'
 'pins and keys are not at plates 07/08\'s 100 % infill. Snug normal supports as plate 01; the four frame-end pins\n'
 'carry the round-shaft trial.\n')
(folder/'preparation.json').write_text(json.dumps({'plate':LABEL,'objects':records,'pose_change':'translation only'},indent=2)+'\n')
(folder/'plate-preparation.json').write_text(json.dumps({'stage':'prepared','objects':objects},indent=2)+'\n')
print(json.dumps({o['name']:[[round(v,1) for v in b] for b in o['bed_bounds_mm']] for o in objects},indent=1))
