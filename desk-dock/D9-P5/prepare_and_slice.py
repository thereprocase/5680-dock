"""Prepare explicitly selected D9 plate poses, then verify once in native Orca."""
from pathlib import Path
import concurrent.futures, hashlib, json, os, shutil, subprocess, sys, time
import xml.etree.ElementTree as ET
import zipfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'work/quartet-team/architect'))
from prepare_coupon_plate import mesh,NS
GEN=HERE/'generated'
BASE=HERE/'profiles'
PLATES=[['M1-outer-cradle-shell'],['M1-inner-shell'],['M2-inner-shell'],['M2-outer-cradle-shell'],
        ['M1-fan-guard','front-tie-L','front-tie-R'],['M2-fan-guard','rear-tie-L','rear-tie-R']]
manifest=json.loads((GEN/'manifest.json').read_text())
fasteners=[p['part'] for p in manifest['parts'] if p['part'].endswith(('-pin','-key')) and '-insert-' not in p['part']]
assert len(fasteners)==40
PLATES.append(fasteners)
PLATES.append(['M1-seat-peg','M2-seat-peg','M1-fence-peg','M2-fence-peg','M1-insert-pin','M2-insert-pin'])
PLATES.append(['cradle-end-trial','M1-fence-peg','M1-seat-peg','M1-insert-pin'])
FIT=['fan-socket-fit-fixture','M1-fan-3-pin','M1-fan-3-key','side-socket-fit-fixture','M1-fan-1-pin','M1-fan-1-key','T-joint-fit-L','T-joint-fit-R','front-lap-pin','front-lap-key']
REVIEW='''D9 P5 geometry-selected manufacturing review

P5: lean 8 degrees; each cradle end is the R7 frame with a drop-in seat peg
and fence peg locked by one horizontal fan pin (plate 08, 100 % infill,
profile on bed like the cradles). Plate 09 is the M1 cradle end sliced to its
16-mm frame width with the M1 pegs and pin: the cheap 8-degree seat trial,
same pose and profile as the cradle. The plenum, guard, tie and fastener plates
are P4, except that the T tongue returns to its P2/P3 12.7-mm height: the P4
trim to 12.1 mm chased stuck support debris, and the cleaned printed pair nests
flush. The lid rail is the only laptop-touching surface left on the frame.


P4 = P3 plus the R5-C underside rail on both outer cradles and three fit
corrections from the printed P2 fit plate: 8.4-mm pin bores (0.2-mm diametral
clearance), key barbs 7.2 mm wide (1.8 mm total interference through the
5.4-mm slot), T tongue 12.1 mm tall (0.6 mm lower). Plate 00 is regenerated so
the new clearances can be trialled before the large parts.

P3 = P2 with the cradle contact taken from the R4-C bracket profile (V5 C seat
relief, lid rail moved 3.5 mm outward, 4-mm base so feet stay coplanar) and a
printable cosmetic edge treatment: fillets on profile corners that run along
each part's print Z (perimeter-only, no overhang), a 0.8-mm chamfer on the
ties' top edges, nothing on bed edges, and every mating zone protected (air
cavity, fan seats, sockets, pin bores, key slots, T joints, guard bars,
laptop contact band). Pins, keys and coupons are byte-identical to P2.


Outer cradle sides: complete broad exterior X face on bed; cavity opens upward.
Inner halves: broad X side on bed; cavity opens upward. Circular fan aperture
opens progressively toward its centre in this orientation. Supports under the
three seam tabs and blind fan sockets are reachable before assembly.
No blanket rejection for downward-facing area is used.
Guards: broad exterior face on bed, bars and spacer towers grow upwards.
Male T ties: broad top on bed; female ties: broad base on bed. The floor-backed
T shoulders carry longitudinal loads. The transverse pin prevents lifting.
Pins: octagonal longitudinal flat on bed; long axes and tension loads in layers.
Keys: broad flat on bed, locking leaves bend in XY. Printed keys are replaceable.
The 8.8-mm transverse bores have two-ended bridge landings and open access.
The selected shell/end-side orientation keeps supported undersides away from
the broad cosmetic outer side. Bed texture is intentional on those faces.
Five walls, six top/bottom layers and 40% gyroid are prototype settings.
Physical contact, load capacity and cooling are untested.
'''

def prepare(index,names):
    folder=HERE/'plates'/f'{index:02d}'
    assert not folder.exists(),folder
    folder.mkdir(parents=True)
    root=ET.Element(f'{{{NS}}}model',{'unit':'millimeter','xml:lang':'en-US'})
    resources=ET.SubElement(root,f'{{{NS}}}resources');build=ET.SubElement(root,f'{{{NS}}}build')
    records=[]
    for oid,name in enumerate(names,1):
        path=GEN/(name+'.stl');vertices,faces,lo,hi=mesh(path)
        size=[hi[i]-lo[i] for i in range(3)]
        if index==0:
            x,y=[(25,40),(80,40),(110,40),(145,40),(198,40),(225,40),(25,130),(95,130),(165,130),(198,130)][oid-1]
        elif index==9:
            x,y=[(12,12),(20,178),(125,178),(200,20)][oid-1]
        elif index==8:
            x,y=[(20,30),(60,30),(20,90),(120,30),(170,30),(200,30)][oid-1]
        elif index==7:
            joint=(oid-1)//2;column=joint%5;row=joint//5
            x=20+column*46+(25 if name.endswith('-key') else 0);y=35+row*52
        elif len(names)==1:x,y=(256-size[0])/2,(256-size[1])/2
        elif oid==1:x,y=62,30
        else:x,y=45,181+(oid-2)*33
        shift=[x-lo[0],y-lo[1],-lo[2]]
        assert x>=10 and y>=10 and x+size[0]<=246 and y+size[1]<=246
        obj=ET.SubElement(resources,f'{{{NS}}}object',{'id':str(oid),'type':'model','name':name})
        m=ET.SubElement(obj,f'{{{NS}}}mesh');vv=ET.SubElement(m,f'{{{NS}}}vertices');ff=ET.SubElement(m,f'{{{NS}}}triangles')
        for v in vertices:ET.SubElement(vv,f'{{{NS}}}vertex',dict(zip(('x','y','z'),(format(n,'.9g') for n in v))))
        for f in faces:ET.SubElement(ff,f'{{{NS}}}triangle',dict(zip(('v1','v2','v3'),map(str,f))))
        ET.SubElement(build,f'{{{NS}}}item',{'objectid':str(oid),'transform':'1 0 0 0 1 0 0 0 1 '+' '.join(map(str,shift))})
        records.append({'name':name,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds':[lo,hi],'translation':shift})
    with zipfile.ZipFile(folder/'input.3mf','w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model',ET.tostring(root,encoding='utf-8',xml_declaration=True))
    for name in ('machine.json','filament.json','profile-selection.json'):shutil.copy2(BASE/name,folder/name)
    process=json.loads((BASE/'process.json').read_text())
    process.update({'wall_loops':'5','top_shell_layers':'6','bottom_shell_layers':'6','sparse_infill_density':'40%',
                    'sparse_infill_pattern':'gyroid','enable_support':'1','support_type':'normal(auto)',
                    'support_style':'snug','support_threshold_angle':'45','support_on_build_plate_only':'0',
                    'support_top_z_distance':'0.2','support_bottom_z_distance':'0.2','support_interface_top_layers':'3',
                    'brim_width':'5','brim_type':'outer_only','layer_height':'0.2'})
    if index in (0,7,8):process['sparse_infill_density']='100%'
    if index==9:process['sparse_infill_density']='40%'
    (folder/'process.json').write_text(json.dumps(process,indent=2)+'\n')
    (folder/'geometry-review.md').write_text(REVIEW)
    (folder/'preparation.json').write_text(json.dumps({'plate':index,'objects':records,'pose_change':'translation only'},indent=2)+'\n')
    return folder

def run(folder):
    (folder/'data').mkdir();(folder/'temp').mkdir()
    cmd=[r'C:\Program Files\OrcaSlicer\orca-slicer.exe','--datadir',str(folder/'data'),'--debug','2',
         '--logfile',str(folder/'slice.log'),'--load-settings',str(folder/'machine.json')+';'+str(folder/'process.json'),
         '--load-filaments',str(folder/'filament.json'),'--arrange','0','--orient','0','--slice','0',
         '--export-3mf','sliced.3mf','--outputdir',str(folder),str(folder/'input.3mf')]
    env=os.environ.copy();env.update(TEMP=str(folder/'temp'),TMP=str(folder/'temp'))
    start=time.time()
    with (folder/'console.log').open('w') as log:
        p=subprocess.run(cmd,cwd=folder,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    result={'plate':folder.name,'exit_code':p.returncode,'elapsed_s':time.time()-start,'command':cmd}
    (folder/'slice-execution.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
    assert p.returncode==0 and (folder/'plate_1.gcode').is_file(),folder
    return result

folders=[prepare(i,names) for i,names in [(0,FIT),*enumerate(PLATES,1)]]
print('Prepared one fit-test plate and seven assembly plates',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    results=list(pool.map(run,folders))
(HERE/'slice-results.json').write_text(json.dumps(results,indent=2)+'\n')
