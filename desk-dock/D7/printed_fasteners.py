"""Coarse, matched, fully printable PETG screw/nut geometry for D7.

These are custom trapezoidal threads, NOT ISO metric threads.  The default
8 mm major diameter has a 6.7 mm solid core, 2 mm pitch and 45 degree flanks.
All lengths are millimetres.  Parts have real swept helical thread geometry.

Datum: screw shank z=0..length, head z=-head_height..0; nut and hole z=0..length.
To align a nut at z=B with a screw whose shank starts z=A, give the nut
phase_z=A-B.  A translated screw can instead be rotated to the matching phase.
"""
from functools import lru_cache
import math
import cadquery as cq

THREAD_SPEC = {
    "family": "D7 custom trapezoidal matched pair; not ISO metric",
    "major_diameter_mm": 8.0,
    "pitch_mm": 2.0,
    "core_diameter_mm": 6.7,
    "crest_width_mm": 0.45,
    "default_radial_clearance_mm": 0.25,
    "default_axial_clearance_per_flank_mm": 0.15,
    "minimum_recommended_engagement_mm": 6.0,
    "print_orientation": "Screw knob flat on bed, shaft upright; nut axis upright",
    "qualification": "PETG fit and hand torque coupon required; no strength certification",
}


def _dimensions(diameter, pitch, core_diameter):
    diameter, pitch = float(diameter), float(pitch)
    core = diameter - 1.3 if core_diameter is None else float(core_diameter)
    if diameter < 8 or pitch < 2 or core < 6 or core >= diameter:
        raise ValueError("Use diameter >=8, pitch >=2 and solid core >=6 below major diameter")
    depth = (diameter-core)/2
    crest = .45
    base = crest+2*depth  # equal radial/axial movement => 45 degree flanks
    if base >= pitch-.1:
        raise ValueError("Pitch too small for 45-degree flanks and this thread depth")
    return diameter, pitch, core, crest, base


@lru_cache(maxsize=64)
def _thread_volume(length, diameter, pitch, core_diameter, radial_clearance,
                   axial_clearance, phase_z):
    """Positive threaded shaft, also used as an expanded female-hole cutter."""
    diameter,pitch,core,crest,base = _dimensions(diameter,pitch,core_diameter)
    length=float(length)
    if length <= 0 or radial_clearance < 0 or axial_clearance < 0:
        raise ValueError("Positive length and nonnegative clearances required")
    if axial_clearance:
        # Widen a valid thread by overlapping shifted copies.  Sweeping a
        # profile wider than one pitch can self-intersect inside the core.
        # For our linear flanks these copies give the same clearance envelope.
        if axial_clearance > crest/2:
            raise ValueError("Axial clearance must not exceed half the crest width")
        base_thread=_thread_volume(length+4*axial_clearance,diameter,pitch,core,
                                  radial_clearance,0.,phase_z+2*axial_clearance)
        base_thread=base_thread.translate((0,0,-2*axial_clearance))
        result=cq.Workplane(obj=base_thread.translate((0,0,-axial_clearance))).union(
            base_thread.translate((0,0,axial_clearance)))
        trim=cq.Workplane("XY").circle(diameter/2+radial_clearance+.1).extrude(length)
        solid=result.intersect(trim).val()
        if not solid.isValid() or len(solid.Solids()) != 1:
            raise ValueError("Clearance envelope did not yield one valid solid")
        return solid
    r0=core/2+radial_clearance
    r1=diameter/2+radial_clearance
    # Extend and trim both ends: no open/non-manifold helical end faces.
    start=-2*pitch+(phase_z % pitch)
    helix=cq.Wire.makeHelix(pitch,length+4*pitch,r0,
                            center=cq.Vector(0,0,start))
    overlap=.08
    profile=cq.Workplane("XZ",origin=(0,0,start)).polyline([
        (r0-overlap,-base/2-overlap),
        (r1,-crest/2),
        (r1,crest/2),
        (r0-overlap,base/2+overlap),
    ]).close()
    ridge=profile.sweep(cq.Workplane(obj=helix),isFrenet=True)
    core_solid=cq.Workplane("XY",origin=(0,0,start-pitch)).circle(r0).extrude(length+7*pitch)
    trim=cq.Workplane("XY").circle(r1+.1).extrude(length)
    solid=core_solid.union(ridge).intersect(trim).val()
    if not solid.isValid() or len(solid.Solids()) != 1:
        raise ValueError("Thread construction did not yield one valid solid")
    return solid


def make_threaded_hole(length, diameter=8, pitch=2, radial_clearance=.25,
                       axial_clearance=.15, core_diameter=None, phase_z=0,
                       lead_in=.6):
    """Return expanded helical cutter.  Subtract from a boss >=14 mm diameter.

    Clearance is radial and axial per flank; it is deliberately independent
    of the printed core size.  The entry is chamfered at both open ends.
    """
    diameter,pitch,core,_,_=_dimensions(diameter,pitch,core_diameter)
    result=cq.Workplane(obj=_thread_volume(float(length),diameter,pitch,core,
                        float(radial_clearance),float(axial_clearance),float(phase_z)))
    if lead_in:
        h=min(float(lead_in),float(length)/3)
        minor=core/2+radial_clearance
        outer=diameter/2+radial_clearance+.2
        result=result.union(cq.Solid.makeCone(outer,minor,h))
        result=result.union(cq.Solid.makeCone(minor,outer,h,
                            cq.Vector(0,0,length-h)))
    return result


def make_threaded_shaft(length, diameter=8, pitch=2, core_diameter=None, phase_z=0):
    """Positive real threaded shaft, no head; useful for a larger smooth axle."""
    diameter,pitch,core,_,_=_dimensions(diameter,pitch,core_diameter)
    return cq.Workplane(obj=_thread_volume(float(length),diameter,pitch,core,
                                          0.,0.,float(phase_z)))


def _hand_grip(diameter, height, z=0):
    if diameter < 14 or height < 4:
        raise ValueError("Hand grips require diameter >=14 and height >=4")
    result=cq.Workplane("XY",origin=(0,0,z)).circle(diameter/2).extrude(height)
    for angle in range(0,360,60):
        a=math.radians(angle)
        center=(diameter/2+1.2)*math.cos(a),(diameter/2+1.2)*math.sin(a),z-.1
        cut=cq.Workplane("XY",origin=center).circle(2.3).extrude(height+.2)
        result=result.cut(cut)
    return result


def make_screw(length, diameter=8, pitch=2, head_diameter=18, head_height=5,
               core_diameter=None, phase_z=0, tip_chamfer=.65):
    """One-piece screw and scalloped hand knob; under-head length is `length`."""
    diameter,pitch,core,_,_=_dimensions(diameter,pitch,core_diameter)
    if head_diameter < diameter+6:
        raise ValueError("Head must exceed nominal shaft diameter by at least 6 mm")
    shaft=cq.Workplane(obj=_thread_volume(float(length),diameter,pitch,core,0.,0.,float(phase_z)))
    if tip_chamfer:
        h=min(float(tip_chamfer),float(length)/3)
        envelope=cq.Workplane("XY").circle(diameter/2+.05).extrude(length-h)
        envelope=envelope.union(cq.Solid.makeCone(diameter/2+.05,core/2-.15,h,
                                                cq.Vector(0,0,length-h)))
        shaft=shaft.intersect(envelope)
    return _hand_grip(float(head_diameter),float(head_height),-float(head_height)).union(shaft)


def make_nut(thickness=8, diameter=8, pitch=2, outer_diameter=18,
             radial_clearance=.25, axial_clearance=.15, core_diameter=None,
             phase_z=0):
    """Scalloped hand nut; minimum 6 mm thickness before entry chamfers."""
    if thickness < 6 or outer_diameter < diameter+6:
        raise ValueError("Nut needs thickness >=6 and at least 3 mm radial wall")
    return _hand_grip(float(outer_diameter),float(thickness)).cut(
        make_threaded_hole(thickness,diameter,pitch,radial_clearance,
                           axial_clearance,core_diameter,phase_z))


def validate_and_export():
    """Standalone fit/orientation checks; does not import or mutate the dock."""
    import hashlib
    import json
    from pathlib import Path
    root=Path(__file__).resolve().parent
    out=root/"printed-fastener-review"
    out.mkdir(exist_ok=True)
    checks=[]
    screw=make_screw(16)
    for gap in (.20,.25,.30):
        nut=make_nut(radial_clearance=gap,phase_z=-4)
        placed=nut.translate((0,0,4))
        collision=screw.intersect(placed).val().Volume()
        wrong=screw.intersect(placed.rotate((0,0,0),(0,0,1),180)).val().Volume()
        assert collision < 1e-4, (gap,collision)
        assert wrong > .1, (gap,wrong,"Thread too loose to engage")
        checks.append({"radial_clearance_mm":gap,"aligned_interference_mm3":collision,
                       "half_turn_out_of_phase_interference_mm3":wrong})
        shape=nut.val()
        assert shape.isValid() and len(shape.Solids())==1
        cq.exporters.export(shape,str(out/f"custom8_nut_gap_{gap:.2f}.stl"),
                            tolerance=.035,angularTolerance=.1)
    # Uneven start datum must preserve thread phase after assembly.
    fractional=make_nut(phase_z=-4.5).translate((0,0,4.5))
    fractional_overlap=screw.intersect(fractional).val().Volume()
    assert fractional_overlap < 1e-4,fractional_overlap
    screw10=make_screw(12,diameter=10,head_diameter=20)
    for gap in (.20,.25,.30):
        nut10=make_nut(diameter=10,outer_diameter=20,radial_clearance=gap,phase_z=-2)
        placed=nut10.translate((0,0,2))
        collision=screw10.intersect(placed).val().Volume()
        wrong=screw10.intersect(placed.rotate((0,0,0),(0,0,1),180)).val().Volume()
        assert collision < 1e-4 and wrong > .1,(gap,collision,wrong)
        assert nut10.val().isValid() and len(nut10.val().Solids())==1
        checks.append({"diameter_mm":10,"radial_clearance_mm":gap,
                       "aligned_interference_mm3":collision,
                       "half_turn_out_of_phase_interference_mm3":wrong})
        cq.exporters.export(nut10.val(),str(out/f"custom10_nut_gap_{gap:.2f}.stl"),
                            tolerance=.035,angularTolerance=.1)
    examples={"custom8_screw_L16":screw.translate((0,0,5)),
              "custom10_screw_L12":make_screw(12,diameter=10,head_diameter=20).translate((0,0,5)),
              "custom12_screw_L12":make_screw(12,diameter=12,head_diameter=22).translate((0,0,5))}
    parts=[]
    for name,part in examples.items():
        shape=part.val()
        assert shape.isValid() and len(shape.Solids())==1,name
        b=shape.BoundingBox()
        assert abs(b.zmin)<1e-5
        cq.exporters.export(shape,str(out/(name+".stl")),tolerance=.035,angularTolerance=.1)
        parts.append({"name":name,"size_mm":[b.xlen,b.ylen,b.zlen],
                      "valid_solid":True,"volume_mm3":shape.Volume()})
    exported=[out/f"custom{diameter}_nut_gap_{gap:.2f}.stl"
              for diameter in (8,10) for gap in (.20,.25,.30)]
    exported += [out/(name+'.stl') for name in examples]
    export_manifest=[{'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
                     for path in exported]
    report={"thread_spec":THREAD_SPEC,"fit_checks":checks,
            "stl_count":len(export_manifest),"export_files":export_manifest,
            "fractional_phase_interference_mm3":fractional_overlap,"parts":parts,
            "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "limits":"Geometric fit, not printed fit or PETG stripping/creep qualification; print coupons first."}
    (out/"validation.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2),flush=True)


if __name__=="__main__":
    validate_and_export()
