"""Prepare explicitly selected D9 plate poses, then verify once in native Orca."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, os, shutil, subprocess, sys, time
from collections import Counter
import xml.etree.ElementTree as ET
import zipfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
from prepare_coupon_plate import mesh,NS
GEN=HERE/'generated'
BASE=HERE/'profiles'
LABELS=['00-fit-and-alternate-parts','01-M1-outer-cradle','02-M1-inner','03-M2-inner',
        '04-M2-outer-cradle','05-frame-ties','06-contact-cassettes-and-splice-ring',
        '07-frame-pins-and-keys','08-accessory-and-polar-structure','09-plug-hardware','10-clamp-shoulder','11-clamp-cam-spatula-washers-and-shim']
manifest=json.loads((GEN/'manifest.json').read_text())
part_names={p['part'] for p in manifest['parts']}
frame_fasteners=sorted(n for n in part_names if n.endswith(('-pin','-key')) and not n.startswith('M'))
# Plate 08 packs the long inner arm and the socket on the first row, the carrier and outer arm on the second;
# plate 09 leads with the two large clamp rings so the small hardware fills the rows beneath.
plug_structure=['plug-holder-polar-inner-arm','accessory-socket-body','plug-holder-polar-plug-rotor','plug-holder-polar-outer-arm']
assert set(plug_structure)=={n for n in part_names if n.startswith('plug-holder-polar-')}|{'accessory-socket-body'}
clamp_big=['plug-holder-clamp-nut','plug-holder-clamp-pressure-washer']
cam_plate=['plug-holder-clamp-cam-spatula','plug-holder-tip-head-thrust-washer','plug-holder-tip-nut-thrust-washer','plug-holder-rotor-pinch-shim']   # the flat parts ride the spatula's spare row
plug_hardware=clamp_big+sorted(n for n in part_names if n.startswith(('plug-holder-','accessory-socket-clamp-','laptop-slide-endstop-')) and n not in plug_structure+clamp_big+cam_plate+['plug-holder-clamp-shoulder'])
PLATES=[['M1-outer-cradle-shell'],['M1-inner-shell'],['M2-inner-shell'],['M2-outer-cradle-shell'],
        ['front-tie-L','front-tie-R','rear-tie-L','rear-tie-R'],
        ['M1-contact-cassette','M2-contact-cassette','M1-insert-pin','M2-insert-pin','centre-contact-cassette','splice-ring-upper','splice-ring-lower'],
        frame_fasteners,plug_structure,plug_hardware,['plug-holder-clamp-shoulder'],cam_plate]
assert Counter(n for plate in PLATES for n in plate)==Counter(part_names), 'Every installed part must appear exactly once'
FIT=[p['part'] for p in manifest['fit_coupons'] if p['part']!='cradle-end-trial']
REVIEW=f'''D9 P5 large-shaft clamp manufacturing review

The manifest is authoritative: {len(part_names)} printed parts appear exactly once on
{len(PLATES)} assembly plates. Retired printed guards, separate seat/fence pegs, four-piece
splice clips and Cartesian plug-holder parts are invalid inputs. The two-piece
centre ring alternates M1/M2 capture; its fan arc seats in a shallow M1 pocket
and every arc passes a positive-engagement audit. Preserve supplied poses:
threaded hardware is thread-axis vertical and pins rest on longitudinal flats. The
clamp shoulder prints ring-down with its 75-mm shaft and 72-mm thread vertical; the
plug rotor prints on its pocket block with the tip bore crest up; the cam spatula
prints flat.
Physical fit, printed-thread strength, clamp holding force, structural load and
cooling remain to be qualified.
These frozen PETG slices are review candidates. The soft-tip geometry on plate
09 needs a separately reviewed flexible-material slice before use as a bumper.
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
        if len(names)==1:x,y=(256-size[0])/2,(256-size[1])/2
        else:
            if oid==1:cursor_x,cursor_y,row_h=24.0,34.0,0.0
            if cursor_x+size[0]>244:
                cursor_x=24.0;cursor_y+=row_h+12.0;row_h=0.0
            x,y=cursor_x,cursor_y
            cursor_x+=size[0]+12.0;row_h=max(row_h,size[1])
        shift=[x-lo[0],y-lo[1],-lo[2]]
        assert x>=10 and y>=10 and x+size[0]<=246 and y+size[1]<=246, (index,name,size,x,y)
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
    if index in (0,6,7,9):process['sparse_infill_density']='100%'
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

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only',action='store_true',help='Write placed 3MFs without slicing')
    args=parser.parse_args()
    folders=[prepare(i,names) for i,names in [(0,FIT),*enumerate(PLATES,1)]]
    print(f'Prepared one fit-test plate and {len(PLATES)} assembly plates',flush=True)
    if not args.prepare_only:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(run,folders))
        (HERE/'slice-results.json').write_text(json.dumps(results,indent=2)+'\n')
