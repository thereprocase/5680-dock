"""Extract reproducible fit evidence from Dell-linked glTF visualization meshes.
Usage: python extract_references.py /path/to/reference-download-directory
Downloads are scratch inputs. Published output is dimensions, hashes and a
small attributed inspection sheet, not redistributed Dell 3D assets.
"""
import sys,json,hashlib
from pathlib import Path
from urllib.request import urlopen
import gzip
import numpy as np,trimesh,cadquery as cq
from PIL import Image,ImageDraw
from raster import render,font
R=Path(__file__).resolve().parent;cache=Path(sys.argv[1]);cache.mkdir(exist_ok=True)
urls={
 'laptop.glb':'https://content.hmxmedia.com/precision-16-5680-laptop-AR/gltf/precision-16-5680-laptop-AR.glb',
 'dock.glb':'https://content.hmxmedia.com/dell-pro-sd25tb5-dock-AR/gltf/dell-pro-sd25tb5-dock-AR.glb',
 'left.jpg':'https://dl.dell.com/content/guides/public/Html/precision-5680-owners-manual/images/GUID-6CFE9489-9462-473E-B516-A962EB2845A2-low.jpg'}
for name,url in urls.items():
 if not (cache/name).exists():
  b=urlopen(url,timeout=60).read()
  if b[:2]==b'\x1f\x8b':b=gzip.decompress(b)
  (cache/name).write_bytes(b)
lap=trimesh.load(cache/'laptop.glb');dock=trimesh.load(cache/'dock.glb')
def node(scene,name):
 t,gn=scene.graph[name];g=scene.geometry[gn].copy();g.apply_transform(t);g.apply_scale(1000);return g
case=node(lap,'Dell4649');rear=case.bounds[0,2]
ports={n:node(lap,n) for n in ['Dell4768','Dell4694']}
plug=dock.geometry['Cube_8'].copy();plug.apply_scale(1000)
tip=dock.geometry['Cube_9'].copy();tip.apply_scale(1000)
report={'retrieved_utc':'2026-09-09','source_kind':'Dell-linked AR visualization meshes, not manufacturing CAD',
 'discovery_pages':['https://www.dell.com/en-us/shop/dell-laptops/precision-5680-workstation/spd/precision-16-5680-laptop','https://www.dell.com/en-us/shop/dell-pro-thunderbolt-5-smart-dock-sd25tb5/apd/210-brqs/docks'],
 'sources':{n:{'url':u,'sha256':hashlib.sha256((cache/n).read_bytes()).hexdigest()} for n,u in urls.items()},
 'rear_case_datum_glTF_mm':float(rear),'rear_case_width_mm':float(case.extents[0]),
 'ports':{n:{'world_bounds_mm':g.bounds.tolist(),'center_mm':g.bounds.mean(0).tolist(),'distance_from_rear_case_mm':float(g.bounds.mean(0)[2]-rear)} for n,g in ports.items()},
 'plug_overmold':{'geometry':'Cube_8','bounds_mm':plug.bounds.tolist(),'extents_mm':plug.extents.tolist()},
 'plug_tip':{'geometry':'Cube_9','bounds_mm':tip.bounds.tolist(),'extents_mm':tip.extents.tolist()},
 'image_scale_check':{'image_hinge_x_px':164,'image_front_x_px':1518,'depth_mm':240.33,'port_centers_x_px':[536,627],'distances_mm':[(x-164)/(1518-164)*240.33 for x in [536,627]]},
 'uncertainty':'Use +/-2 mm setup allowance for case/port reconstruction and +/-1 mm for overmold shape. These are engineering allowances, not statistical confidence intervals. Exact shell plane, overmold taper, metal engagement, lid compression and pad seating need adjustment on the physical hardware.'}
(R/'reference-extraction.json').write_text(json.dumps(report,indent=2)+'\n')
class Mesh:
 def __init__(self,g):self.g=g
 def tessellate(self,*args):return [cq.Vector(*v) for v in self.g.vertices],self.g.faces.tolist()
page=Image.new('RGB',(1600,1150),'#f8f8f8');d=ImageDraw.Draw(page)
d.text((50,30),'DELL SOURCE GEOMETRY / FIT EVIDENCE',font=font(35,True),fill='#253238')
im=Image.open(cache/'left.jpg');im.thumbnail((1500,360));page.paste(im,(50,110));d=ImageDraw.Draw(page)
d.text((65,490),'Near port: 66.0 mm from rear case datum',font=font(27,True),fill='#253238')
d.text((65,540),'Second port: 82.2 mm; spacing about 16.2 mm',font=font(24),fill='#5c696e')
pic,_=render([(Mesh(plug),(54,58,60)),(Mesh(tip),(174,182,188))],(650,370),(-1.7,2.4,1.2),pad=35)
page.paste(pic,(10,630));d=ImageDraw.Draw(page)
d.text((720,680),'SD25TB5 overmold: 25 x 12.5 x 6.5 mm',font=font(26,True),fill='#253238')
d.text((720,735),'Metal shell in mesh: 6.65 x 8.25 x 2.40 mm',font=font(23),fill='#5c696e')
d.text((720,795),'Extracted from the Dell-linked 3D model.',font=font(23),fill='#5c696e')
d.text((720,840),'Cassette adjustment covers residual fit error.',font=font(23),fill='#5c696e')
d.text((50,1050),'Dell service image and AR geometry, used for source inspection. Visualization assets are not factory toleranced drawings.',font=font(20),fill='#78674c')
page.save(R/'reference-evidence.png')
print('Extracted',report['ports'],report['plug_overmold']['extents_mm'])
