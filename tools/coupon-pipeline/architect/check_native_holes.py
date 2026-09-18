from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,trimesh
root=Path(__file__).resolve().parents[3]
folder=root/'work/quartet-team/architect/v4-orca'
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
prod='{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'
with zipfile.ZipFile(folder/'coupons-sliced.3mf') as archive:
 settings=ET.fromstring(archive.read('Metadata/model_settings.config'))
 names={x.get('id'):x.find("metadata[@key='name']").get('value') for x in settings.findall('object')}
 model=ET.fromstring(archive.read('3D/3dmodel.model'))
 for item in model.findall('m:build/m:item',ns):
  ident=item.get('objectid');t=list(map(float,item.get('transform').split()));o=model.find(f"m:resources/m:object[@id='{ident}']/m:components/m:component",ns)
  sub=ET.fromstring(archive.read(o.get(prod+'path').lstrip('/')))
  vs=[[float(v.get(axis))+t[9+i] for i,axis in enumerate(('x','y','z'))] for v in sub.findall('.//m:vertices/m:vertex',ns)]
  fs=[[int(v.get(axis)) for axis in ('v1','v2','v3')] for v in sub.findall('.//m:triangles/m:triangle',ns)]
  mesh=trimesh.Trimesh(vertices=vs,faces=fs)
  print(names[ident], 'native3mf',mesh.bounds.tolist())
  sec=mesh.section(plane_origin=[0,0,12],plane_normal=[0,0,1])
  for ring in sec.discrete:
   if max(ring[:,0])-min(ring[:,0])<4 and max(ring[:,1])-min(ring[:,1])<4:
    print('HOLE',ring.min(axis=0).tolist(),ring.max(axis=0).tolist())
