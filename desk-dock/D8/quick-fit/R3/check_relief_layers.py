"""Independent layer-to-layer support screen of the final exact lip solid."""
from pathlib import Path
import json,math
import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import LineString,Point
from shapely.ops import unary_union,polygonize

r=Path(__file__).resolve().parent
lip=cq.Shape.importBrep(str(r/'lip-local.brep'))
vs,fs=lip.tessellate(.008,.06)
m=trimesh.Trimesh(vertices=[v.toTuple() for v in vs],faces=fs,process=True)
assert m.is_watertight and m.is_winding_consistent
def section(x):
    segments=trimesh.intersections.mesh_plane(m,plane_origin=[x,0,0],plane_normal=[1,0,0])
    polygons=list(polygonize([LineString(np.round(line[:,1:],7)) for line in segments]))
    assert polygons, x
    assert all(p.is_valid for p in polygons)
    return unary_union(polygons)
previous=section(.1)
rows=[]
for x in np.arange(.3,38.1,.2):
    current=section(x)
    # Project each layer onto the layer beneath. A 0.20 mm lateral advance
    # over a 0.20 mm layer is the 45-degree geometric support boundary.
    unsupported=current.difference(previous.buffer(.2001,resolution=32)).area
    assert unsupported<.0001,(float(x),unsupported)
    polygons=[current] if current.geom_type=='Polygon' else list(current.geoms)
    advance=max(previous.distance(Point(p))
                for poly in polygons for p in poly.exterior.coords)
    rows.append(dict(print_z_mm=round(float(x),3),advance_mm=advance,
                     area_beyond_45_degree_envelope_mm2=unsupported))
    previous=current
report=dict(passed=True,layer_height_mm=.2,layer_pairs=len(rows),
    maximum_sampled_lateral_advance_mm=max(x['advance_mm'] for x in rows),
    maximum_sampled_angle_from_vertical_deg=math.degrees(math.atan(max(x['advance_mm'] for x in rows)/.2)),
    area_outside_45_degree_support_envelope_mm2=max(x['area_beyond_45_degree_envelope_mm2'] for x in rows),
    scope='Final lip mesh sectioned normal to original X, the print-layer axis. Geometric screen, not a physical print test.',
    layers=rows)
(r/'layer-support-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='layers'}))
