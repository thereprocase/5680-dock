"""Audit actual Orca extrusion paths and make a local toolpath preview.

No printer connection and no geometry edits. Fails on support paths, external
bridges, off-bed model/brim extrusion, or mismatched embedded G-code.
"""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
import zipfile
from PIL import Image, ImageDraw, ImageFont


def paths(text):
    pos = dict(X=0., Y=0., Z=0., E=0.)
    relative_e, absolute_xyz, role = True, True, 'Custom'
    segments = []
    for line in text.splitlines():
        if line.startswith('; FEATURE: '):
            role = line[11:]
            continue
        code = line.split(';')[0].strip()
        if not code:
            continue
        op = code.split()[0]
        if op == 'M83': relative_e = True
        if op == 'M82': relative_e = False
        if op == 'G90': absolute_xyz = True
        if op == 'G91': absolute_xyz = False
        values = {k:float(v) for k,v in re.findall(r'([XYZEIJ])([-+]?(?:\d*\.)?\d+)', code)}
        if op == 'G92':
            pos.update({k:v for k,v in values.items() if k in pos})
            continue
        if op not in ('G0','G1','G2','G3'):
            continue
        before = pos.copy()
        for k in ('X','Y','Z'):
            if k in values:
                pos[k] = values[k] if absolute_xyz else pos[k]+values[k]
        extrusion = values.get('E',0) if relative_e else values.get('E',pos['E'])-pos['E']
        if 'E' in values:
            pos['E'] = pos['E']+values['E'] if relative_e else values['E']
        if extrusion <= 0 or role == 'Custom':
            continue
        p0, p1 = (before['X'],before['Y']), (pos['X'],pos['Y'])
        if p0 == p1 and op not in ('G2','G3'):
            continue
        arc = [p0,p1]
        if op in ('G2','G3'):
            assert 'I' in values or 'J' in values, 'Unsupported arc encoding'
            cx,cy = p0[0]+values.get('I',0),p0[1]+values.get('J',0)
            a,b = math.atan2(p0[1]-cy,p0[0]-cx),math.atan2(p1[1]-cy,p1[0]-cx)
            sweep = (b-a)%(2*math.pi) if op == 'G3' else -((a-b)%(2*math.pi))
            if abs(sweep) < 1e-9: sweep = 2*math.pi*(1 if op == 'G3' else -1)
            count = max(2,math.ceil(abs(sweep)/.025))
            radius = math.hypot(p0[0]-cx,p0[1]-cy)
            arc = [(cx+radius*math.cos(a+sweep*i/count),cy+radius*math.sin(a+sweep*i/count)) for i in range(count+1)]
        segments.extend((a,b,pos['Z'],role) for a,b in zip(arc,arc[1:]))
    return segments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dir',type=Path,required=True)
    parser.add_argument('--project',default='coupons-sliced.3mf')
    args = parser.parse_args()
    folder = args.dir
    gcode = folder/'plate_1.gcode'
    data = gcode.read_bytes()
    text = data.decode('utf-8')
    prep = json.loads((folder/'plate-preparation.json').read_text())
    process = json.loads((folder/'process.json').read_text())
    assert str(process['enable_support']) == '1', 'Automatic support detection must be enabled'
    with zipfile.ZipFile(folder/args.project) as archive:
        assert archive.testzip() is None
        assert archive.read('Metadata/plate_1.gcode') == data
        assert archive.read('Metadata/plate_1.gcode.md5').decode().strip().lower() == hashlib.md5(data).hexdigest()
        settings = ET.fromstring(archive.read('Metadata/model_settings.config'))
        assert len(settings.findall('object')) == len(prep['objects']), 'Expected one object per prepared coupon'
        assert len(settings.findall('plate')) == 1, 'Expected a single plate'
        actual_objects = verify_placement(archive,settings,prep)
    machine = json.loads((folder/'machine.json').read_text())
    offsets = machine['extruder_offset']
    assert len(offsets)==1, 'This audit requires one physical extruder'
    offset = tuple(map(float,offsets[0].split('x')))
    assert len(offset)==2
    declared = re.search(r'^; extruder_offset = (.+)$',text,re.M).group(1).strip()
    assert declared==offsets[0], 'G-code/profile extruder offset mismatch'
    raw_segments = paths(text)
    segments = [((a[0]+offset[0],a[1]+offset[1]),(b[0]+offset[0],b[1]+offset[1]),z,role) for a,b,z,role in raw_segments]
    assert segments
    roles = Counter(s[3] for s in segments)
    supports = [s for s in segments if 'support' in s[3].lower()]
    bridges = [s for s in segments if 'bridge' in s[3].lower()]
    external = [s for s in bridges if 'internal' not in s[3].lower()]
    assert not supports, 'Unexpected support extrusion'
    assert not external, 'Unexpected external bridge; inspect before release'
    points = [p for a,b,z,role in segments for p in (a,b)]
    bounds = [min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points),max(p[1] for p in points)]
    assert all(.25 < p[0] < 255.75 and .25 < p[1] < 255.75 for p in points)
    assert all(not(p[0] < 18.5 and p[1] < 28.5) for p in points), 'Front-left excluded zone'
    height = max(s[2] for s in segments if s[3].lower() != 'brim')
    intended_height = max(o['bed_bounds_mm'][1][2] for o in prep['objects'])
    assert abs(height-intended_height) <= .21, 'Unexpected build-height/orientation change'
    layer = float(process['layer_height'])
    top_layers = int(process['top_shell_layers'])
    assert all(s[2] >= height-layer*(top_layers+1)-.01 for s in bridges), 'Internal bridge below expected top-skin closure'
    summary_lines = [s for s in text.splitlines() if s.startswith(('; generated by','; model printing time:','; filament used [g]','; total layer number:','; max_z_height:'))]
    report = {'passed':True, 'source':'actual Orca G-code roads in the declared nozzle/plate frame',
              'raw_motion_to_plate_xy_offset_mm':offset,
              'frame_note':'Raw motion plus the frozen single-extruder XY offset; this is a slicer-coordinate check, not a physical nozzle calibration.',
              'summary':summary_lines, 'support_segments':len(supports), 'external_bridge_segments':len(external),
              'internal_bridge_z_mm':sorted(set(s[2] for s in bridges)),
              'internal_bridge_note':'Only internal infill closure in the expected top-skin region is accepted.',
              'model_and_brim_bounds_xy_mm':bounds, 'actual_print_height_mm':height,
              'feature_segment_counts':dict(roles), 'embedded_gcode_matches':True,
              'actual_objects':actual_objects,
              'gcode_sha256':hashlib.sha256(data).hexdigest(),
              'qualification':'Orca toolpath verification only; physical fit, stand loads, airflow and acoustics untested.'}
    (folder/'toolpath-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    preview(segments,bounds,height,folder/'actual-toolpaths.png',prep['objects'])
    print(json.dumps(report,indent=2))


def verify_placement(archive,settings,prep):
    ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    production='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
    root=ET.fromstring(archive.read('3D/3dmodel.model'))
    expected={o['name']:o for o in prep['objects']}
    metadata={o.get('id'):o for o in settings.findall('object')}
    result=[]
    for item in root.findall('m:build/m:item',ns):
        oid=item.get('objectid')
        name=metadata[oid].find("metadata[@key='name']").get('value')
        transform=list(map(float,item.get('transform').split()))
        assert len(transform)==12
        assert all(abs(a-b)<1e-8 for a,b in zip(transform[:9],[1,0,0,0,1,0,0,0,1])), 'Source orientation changed'
        comp=root.find(f"m:resources/m:object[@id='{oid}']/m:components/m:component",ns)
        assert comp is not None
        ct=list(map(float,comp.get('transform').split()))
        assert ct==[1,0,0,0,1,0,0,0,1,0,0,0], 'Unexpected component transform'
        path=comp.get(production+'path').lstrip('/')
        meshroot=ET.fromstring(archive.read(path))
        vertices=[tuple(float(v.get(axis))+transform[9+i] for i,axis in enumerate(('x','y','z')))
                  for v in meshroot.findall('.//m:vertices/m:vertex',ns)]
        lo=[min(v[i] for v in vertices) for i in range(3)]
        hi=[max(v[i] for v in vertices) for i in range(3)]
        target=expected[name]['bed_bounds_mm']
        assert all(abs(a-b)<1e-4 for bounds,t in zip((lo,hi),target) for a,b in zip(bounds,t)), 'Orca moved a prepared object'
        result.append({'name':name,'bounds_mm':[lo,hi],'native_transform':transform})
    assert len(result)==len(prep['objects'])
    for i,a in enumerate(result):
        for b in result[i+1:]:
            gaps=[max(0,a['bounds_mm'][0][j]-b['bounds_mm'][1][j],b['bounds_mm'][0][j]-a['bounds_mm'][1][j]) for j in (0,1)]
            assert math.hypot(*gaps)>=15.99,'Prepared model spacing was not retained'
    return result


def preview(segments,bounds,height,out,objects):
    image = Image.new('RGB',(1600,560),'#f7f8fa')
    draw = ImageDraw.Draw(image)
    fontpath = 'C:/Windows/Fonts/arial.ttf'
    font = lambda n: ImageFont.truetype(fontpath,n)
    draw.text((35,25),'A / B / C contact coupons | Actual Orca toolpaths',font=font(32),fill='#17364b')
    draw.text((35,75),'Geometry-selected orientation; supports enabled for verification, zero support paths.',font=font(22),fill='#314854')
    levels = sorted(set(round(s[2],3) for s in segments))
    selected = [min(levels,key=lambda z:abs(z-target)) for target in (.2,height/2,height)]
    colors = {'Outer wall':'#087dad','Inner wall':'#42a9a0','Gap infill':'#d38421','Internal Bridge':'#a43583','Brim':'#a3acb2','Top surface':'#cc9366'}
    for column,z in enumerate(selected):
        x0,y0 = 30+column*525,145
        draw.text((x0,y0),f'Print Z {z:g} mm',font=font(23),fill='#17364b')
        scale = min(490/(bounds[2]-bounds[0]+4),285/(bounds[3]-bounds[1]+4))
        def project(p): return (x0+(p[0]-bounds[0]+2)*scale,y0+65+(bounds[3]+2-p[1])*scale)
        for a,b,zz,role in segments:
            if abs(zz-z)<.01:
                draw.line((project(a),project(b)),fill=colors.get(role,'#b7c1c8'),width=2)
        for obj in objects:
            lo,hi = obj['bed_bounds_mm']
            label = project(((lo[0]+hi[0])/2,lo[1]-3))
            draw.text(label,obj['name'][0],font=font(18),fill='#17364b',anchor='mt')
    draw.text((35,505),'Blue outside walls | Teal inside walls | Orange gap fill | Magenta internal bridge | Gray brim',font=font(20),fill='#314854')
    image.save(out)


if __name__ == '__main__':
    main()
