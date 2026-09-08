"""Export every D8 production part using an explicit, reviewed print pose.

Run directly, or import export_all() from the combined review runner to reuse
its built assembly. No slicer or printer is invoked here.
"""
from pathlib import Path
import json,hashlib
import cadquery as cq
ROOT=Path(__file__).resolve().parent

def export_all(build):
    from fan_service import PRINT_OVERRIDES
    from breakaway_geometry import make_spring
    specs={}
    def spec(n,rotations,face,stress,support='Accessible local support/bridge review',unlean=True,material='PETG'):
        specs[n]=dict(rotations=rotations,face_on_bed=face,load_orientation=stress,support=support,unlean=unlean,material=material)
    for i in [1,2]:
        prefix=f'{i:02}_'
        spec(prefix+'manifold_with_cradle',[],'Flat shell lower perimeter and corner feet','Vertical perimeter walls carry gravity; upright roof ribs provide short bridge landings. Local fan-pocket supports remain accessible.',unlean=False)
        spec(prefix+'fan_guard_retainer',[('X',-build.ANGLE)],'Broad front grille face','Grille bars lie in bed plane.','None expected',False)
        spec(prefix+'bottom_panel',[],'Broad exterior skin','Plate and ribs carry cover handling only; shell feet bypass it.','Short cable-saddle roof bridge',False)
        for j in [1,2]:
            spec(prefix+f'fan_top_clip_{j}',[('X',-build.ANGLE),('Y',-90)],'Broad fan-local YZ side; unloaded shape','Leaf length and bending stress lie in bed plane.','None expected',False)
            spec(prefix+f'bottom_thumb_lock_{j}',[],'Hand head','Threads upright; axial strength depends on layer bonding.','None expected',False)
            spec(prefix+f'bridge_thumb_lock_{j}',[('X',180)],'Hand head','Threads upright; axial strength depends on layer bonding.','None expected',False)
    for j in [1,2]:spec(f'bridge_key_{j}',[],'Broad underside','Plate load path lies in bed plane.','None expected',False)
    spec('connector_module_body',[('X',-90)],'Broad rear Y=50 support face','Main arm and root XZ load path lies in layers; cam working face grows upward.')
    spec('chassis_stop_bracket',[('X',-90)],'Broad rear support face','Stop bending lies in XZ bed plane; local horizontal thread needs path review.')
    spec('breakaway_carrier',[],'Reinforced carrier lower face and guide feet','Docking X loads lie in the bed plane; vertical-web bending still depends on layer bonding.','Small accessible supports; upright pose screened at about 5.6 g support')
    spec('cassette_Z_saddle',[('X',-90)],'Broad Y=17.5 outside face','X/Z saddle load path lies in bed plane; check local open gusset bridge.')
    spec('X_depth_overmold_clamp',[],'Broad cradle underside','XY base and axial thrust shoulders lie along layers; clamp has open cable cavity.')
    spec('sliding_plug_cap',[('X',180)],'Broad cap outside face','Cap bending spans the bed plane; gripping features grow upward.')
    spec('breakaway_spring_cartridge',[('X',-90)],'Common unloaded spring outside face','Leaf length and bending stress lie in bed plane.','None expected')
    spec('breakaway_pivot_pin_10mm',[],'Shaft horizontal; accessible support beneath','Continuous deposited paths run along shaft.','Accessible support beneath round shaft and head')
    spec('cassette_cap_push_pin_6p5',[],'Shaft horizontal; accessible support beneath','Continuous deposited paths run along shaft.','Accessible support beneath round shaft and head')
    spec('breakaway_preload_hand_nut',[('X',-90)],'Hand face','Thread axis upright; dense part.','None expected')
    spec('independent_printed_chassis_stop_screw',[('Y',-90)],'Hand face','Thread axis upright; verify layer-bond strength.','None expected')
    spec('stop_soft_tip',[('Y',90)],'Closed soft contact face','Low-load contact bumper; socket upward.','None expected',material='TPU or purchased compliant bumper')
    for j in [0,1]:
        spec(f'breakaway_spring_hand_screw_{j}',[('X',-90)],'Hand face','Thread axis upright; verify preload tension.','None expected')
        spec(f'breakaway_spring_spacer_{j}',[('X',90)],'Flat spacer end','Compressive spacer load along build Z; continuous walls.','None expected')
        spec(f'connector_mount_lock_{j}',[('X',-90)],'Hand face','Thread axis upright; keys carry docking thrust.','None expected')
        spec(f'chassis_stop_mount_lock_{j}',[('X',90)],'Hand face','Thread axis upright; bracket key carries thrust.','None expected')
        spec(f'cassette_Z_lock_{j}',[('Y',-90)],'Hand face','Thread axis upright; broad thrust land carries X reaction.','None expected')
        spec(f'cassette_Y_lock_{j}',[],'Hand face','Thread axis upright; rail shoulders carry X reaction.','None expected')
    external=lambda n: any(k in n for k in ['desk_pad_','corner_pad_','liner_','hinge_seal_'])
    production=[a for a in build.parts if not a['reference'] and not external(a['name'])]
    names={a['name'] for a in production}
    missing=names-set(specs)
    if missing:raise ValueError('No explicit print pose: '+', '.join(sorted(missing)))
    out=ROOT/'print';out.mkdir(exist_ok=True)
    records=[]
    for a in production:
        n=a['name'];cfg=specs[n];shape=a['shape']
        if n in PRINT_OVERRIDES:
            shape=PRINT_OVERRIDES[n];shape=shape.val() if isinstance(shape,cq.Workplane) else shape
        if cfg['unlean']:shape=shape.rotate((0,0,build.H),(1,0,build.H),build.LEAN)
        if n=='breakaway_spring_cartridge':shape=make_spring(build.p,delta=0).val()
        for axis,angle in cfg['rotations']:
            direction={'X':(1,0,0),'Y':(0,1,0),'Z':(0,0,1)}[axis]
            shape=shape.rotate((0,0,0),direction,angle)
        bb=shape.BoundingBox();shape=shape.translate((-bb.xmin,-bb.ymin,-bb.zmin));bb=shape.BoundingBox()
        file=out/(n+'.stl');cq.exporters.export(shape,str(file),tolerance=.06,angularTolerance=.12)
        # Exact solid intersection provides an independent first-layer area.
        slab=cq.Workplane('XY').box(bb.xlen+2,bb.ylen+2,.2,centered=False).translate((-1,-1,0)).val()
        rec={k:v for k,v in cfg.items() if k!='unlean'}
        rec.update(part=n,file=file.name,dimensions_mm=[bb.xlen,bb.ylen,bb.zlen],
                   volume_mm3=shape.Volume(),first_layer_mean_contact_mm2=shape.intersect(slab).Volume()/.2,
                   sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
                   unloaded_export=(n in PRINT_OVERRIDES or n=='breakaway_spring_cartridge'),
                   layer_mm=.2,nozzle_mm=.4,walls=5,top_bottom_layers=6,
                   initial_infill='100% for dense initial qualification; CAD cavities remain hollow')
        records.append(rec)
    (ROOT/'print-manifest.json').write_text(json.dumps(dict(revision='D8',scope='Explicit manufacturing poses, not physical print qualification.',parts=records),indent=2)+'\n')
    print('D8 print exports',len(records),flush=True)
    return records

if __name__=='__main__':
    import build
    export_all(build)
