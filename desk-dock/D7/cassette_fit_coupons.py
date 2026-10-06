"""Small actual-interface fit pieces; no dock build, slicer, or application."""
import hashlib
import json
from pathlib import Path
import cadquery as cq

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'cassette-review'


def export_coupons():
    OUT.mkdir(exist_ok=True)
    records=[]
    for bore in (6.8,6.9,7.0):
        part=cq.Workplane('XY').circle(7).circle(bore/2).extrude(8)
        shape=part.val()
        assert shape.isValid() and len(shape.Solids())==1
        path=OUT/f'cap_pin_receiver_bore_{bore:.1f}.stl'
        cq.exporters.export(shape,str(path),tolerance=.035,angularTolerance=.1)
        records.append({'file':path.name,'bore_mm':bore,'size_mm':[14,14,8],
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'purpose':'Use actual cassette_cap_push_pin_6p5 as male; diameter/friction screening only.'})
    report={'stl_count':len(records),'parts':records,
            'male':'cassette_cap_push_pin_6p5.stl (actual cap pin exported by cassette_isolated_check.py)',
            'print_pose':'Flat ring face on bed; pin upright on its head; same PETG profile as final parts.',
            'limits':'Full housing ears differ in compliance and engagement length. Ring fit does not qualify extraction load, pin fatigue, or cap squeeze.'}
    (OUT/'cap-pin-coupon-manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    export_coupons()
