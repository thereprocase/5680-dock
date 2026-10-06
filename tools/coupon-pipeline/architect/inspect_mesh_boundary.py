"""Read-only localization of a candidate STL's unmatched/nonmanifold edges."""
import argparse, json
from pathlib import Path
import numpy as np
import trimesh

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('stl', type=Path)
a=p.parse_args()
m=trimesh.load_mesh(a.stl, process=True)
edges,counts=np.unique(np.sort(m.edges,axis=1),axis=0,return_counts=True)
bad=edges[counts!=2]
components=trimesh.graph.connected_components(bad,min_len=2) if len(bad) else []
records=[]
for component in components:
 v=m.vertices[component]
 records.append({'vertices':len(component),'bounds_mm':[v.min(axis=0).tolist(),v.max(axis=0).tolist()], 'center_mm':v.mean(axis=0).tolist()})
print(json.dumps({'source':str(a.stl),'watertight':bool(m.is_watertight),'consistent_winding':bool(m.is_winding_consistent),'vertices':len(m.vertices),'faces':len(m.faces),'edge_incidence_counts':{str(int(n)):int(np.sum(counts==n)) for n in np.unique(counts)},'bad_edge_components':sorted(records,key=lambda x:x['vertices'],reverse=True),'zero_area_faces':int(np.sum(m.area_faces<1e-10))},indent=2))
