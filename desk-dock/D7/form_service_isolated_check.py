"""Reproduce nominal fan/body service checks without full assembly export.

Extracts only the initial shell construction from the adjacent build source,
then exercises the owned service modules. Run explicitly; importing is inert.
CadQuery must already be available. No slicer, printer, or dependency install.
"""
from pathlib import Path
import sys, math, json

def run_check():
    ROOT=Path(__file__).resolve().parent
    sys.path.insert(0,str(ROOT))
    import cadquery as cq
    import fan_service
    from body_service import body_service
    ns={'__file__':str(ROOT/'build.py'),'baselines':[]}
    source,marker,_=(ROOT/'build.py').read_text().partition('    from fan_service import build_fan_service')
    assert marker,'Shell prefix marker changed; stop rather than execute the full build.'
    exec(compile(source+'    baselines.append((i,x0,x1,fx,roof))\n',ns['__file__'],'exec'),ns)
    box,rb,hole,add=map(ns.get,['box','rb','hole','add'])
    bodies=[]; fans=[]; poses={}
    for i,x0,x1,fx,roof in ns['baselines']:
     def pose(s,fx=fx):return s.translate((-fx,-91,-fan_service.POSE_ANCHOR_Z)).rotate((0,0,0),(1,0,0),ns['ANGLE']).translate((fx,ns['FAN_Y'],ns['FAN_Z']))
     poses[i]=pose
     roof=fan_service.build_fan_service(i,fx,roof,pose,box,rb,hole,add,thickness=ns['p']['fan_thickness'])
     print('FAN BODY',i,roof.val().isValid(),len(roof.val().Solids()),flush=True)
     assert roof.val().isValid() and len(roof.val().Solids())==1
     bodies.append((x0,x1,roof.val()))
     d=fan_service.fan_dimensions(ns['p']['fan_thickness'])
     fan=rb(fx-60,31,d['front'],120,120,d['thickness'],6).cut(hole((0,0,1),(fx,91,d['front']-1),56.5,d['thickness']+2))
     for xx in [fx-52.5,fx+52.5]:
      for yy in [38.5,143.5]:fan=fan.cut(hole((0,0,1),(xx,yy,d['front']-1),2.2,d['thickness']+2))
     fans.append(pose(fan).val())
    print('Starting body service',flush=True)
    meta=body_service(bodies,ns['W'],ns['front_y'],box,rb,hole,add)
    parts={p['name']:p['shape'] for p in ns['parts']}
    report={'scope':'Current shell prefix plus isolated fan/body/cable modules; excludes carrier, laptop and full export','fan_dimensions':d,'valid_parts':len(parts),'printed_only':all(not p['reference'] for p in ns['parts']),'fan':[],'body':[]}
    def overlap(a,b):
     ba,bb=a.BoundingBox(),b.BoundingBox()
     if ba.xmax<=bb.xmin or bb.xmax<=ba.xmin or ba.ymax<=bb.ymin or bb.ymax<=ba.ymin or ba.zmax<=bb.zmin or bb.zmax<=ba.zmin:return 0
     return a.intersect(b).Volume()
    for i,(x0,x1,body) in enumerate(bodies,1):
     guard=parts[f'{i:02}_fan_guard_retainer'];fan=fans[i-1]
     regions=fan_service.FRICTION_REGIONS[i]
     contact=guard.intersect(body)
     unexpected=contact
     for region in regions:unexpected=unexpected.cut(region)
     rec={'module':i,'fan_body_mm3':overlap(fan,body),'guard_body_mm3':contact.Volume(),'guard_body_outside_friction_mm3':unexpected.Volume(),'guard_fan_mm3':overlap(guard,fan),'slide':[]}
     bb=body.BoundingBox()
     rec['body_bounds_mm']=[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]
     fx=ns['baselines'][i-1][3]
     air=poses[i](hole((0,0,1),(fx,91,d['front']),56.49,d['thickness']))
     rec['air_aperture_body_mm3']=overlap(air,body)
     rec['fan_lead_clearance_mm3']=[]
     for z in [d['front']+.5,d['center']-2,d['back']-3.7]:
      wire=poses[i](box(fx+60.05,44,z,5,6,4)).val()
      rec['fan_lead_clearance_mm3'].append(overlap(wire,body))
     assert rec['air_aperture_body_mm3']<1e-5,rec
     assert max(rec['fan_lead_clearance_mm3'])<1e-5,rec
     assert max(rec[k] for k in ['fan_body_mm3','guard_body_outside_friction_mm3','guard_fan_mm3'])<1e-5,rec
     for lift in [0,.5,1,3,6,10,25,50,75,100,125,140]:
      shift=(0,math.cos(math.radians(ns['ANGLE']))*lift,math.sin(math.radians(ns['ANGLE']))*lift)
      moved=guard.translate(shift)
      cf=moved.intersect(body)
      if lift<6:
       for region in regions:cf=cf.cut(region)
      cfan=overlap(fan.translate(shift),body)
      row={'lift_mm':lift,'guard_body_unexpected_mm3':cf.Volume(),'guard_fan_mm3':overlap(moved,fan),'fan_body_mm3':cfan}
      rec['slide'].append(row)
      assert max(row[k] for k in ['guard_body_unexpected_mm3','guard_fan_mm3','fan_body_mm3'])<1e-5,row
     report['fan'].append(rec)
     plate=parts[f'{i:02}_bottom_panel']
     rec={'module':i,'body_panel_mm3':overlap(plate,body),'locks':[]}
     for j in [1,2]:
      lock=parts[f'{i:02}_bottom_thumb_lock_{j}']
      rec['locks'].append({'index':j,'body_mm3':overlap(lock,body),'panel_mm3':overlap(lock,plate)})
     outer=x0 if i==1 else x1
     probe=box(outer-1 if i==1 else outer-16,31,3,17,6,4).val()
     rec['wire_body_mm3']=overlap(probe,body);rec['wire_panel_mm3']=overlap(probe,plate)
     rec['panel_service_max_mm3']=max(overlap(plate.translate((0,0,-d)),probe) for d in range(11))
     rec['lug_passages_mm3']=[]
     for y,z in [(34,14),(50,29)]:
      lugprobe=box(outer+(6 if i==1 else -6)-1.25,y-7.5,z-.5,2.5,15,1).val()
      rec['lug_passages_mm3'].append(overlap(lugprobe,body))
     report['body'].append(rec)
     assert max(rec[k] for k in ['body_panel_mm3','wire_body_mm3','wire_panel_mm3','panel_service_max_mm3'])<1e-5,rec
     assert max(rec['lug_passages_mm3'])<1e-5,rec
     assert all(max(x['body_mm3'],x['panel_mm3'])<1e-5 for x in rec['locks']),rec
    report['bridge']=[]
    for j in [1,2]:
     bridge=parts[f'bridge_key_{j}']
     for i,(x0,x1,body) in enumerate(bodies,1):
      lock=parts[f'{i:02}_bridge_thumb_lock_{j}']
      row={'bridge':j,'module':i,'key_body_mm3':overlap(bridge,body),'lock_body_mm3':overlap(lock,body),'lock_key_mm3':overlap(lock,bridge)}
      assert max(row[k] for k in ['key_body_mm3','lock_body_mm3','lock_key_mm3'])<1e-5,row
      report['bridge'].append(row)
    report['passed']=True
    return report

if __name__ == '__main__':
    print(json.dumps(run_check(),indent=2))
