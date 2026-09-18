"""Exercise the enclosure auditor against known closed and deliberately leaky CAD."""
import cadquery as cq,json,subprocess,sys
from pathlib import Path
p=Path(__file__).resolve().parent
out=p/'enclosure-auditor-fixtures-v2';out.mkdir(exist_ok=True)
def box(x,y,z,a,b,c):return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z)).val()
inner=box(5,5,5,10,10,10)
ports=cq.Solid.makeCylinder(2,20,cq.Vector(10,10,0),cq.Vector(0,0,1))
void=inner.fuse(ports).clean()
body=box(0,0,0,20,20,20).cut(void).clean()
caps=cq.Compound.makeCompound([box(7,7,-.5,6,6,1),box(7,7,19.5,6,6,1)])
leaky=body.cut(box(14,9.5,9.5,7,1,1)).clean()
blind=body.fuse(box(7,7,20,6,6,1)).clean()
for name,shape in [('closed',body),('leaky',leaky),('blind_port',blind),('void',void),('caps',caps)]:cq.exporters.export(shape,str(out/(name+'.step')))
results={}
for case,expected in [('closed',True),('leaky',False),('blind_port',False)]:
 command=[sys.executable,str(p/'audit_closed_intake.py'),'--assembly',str(out/(case+'.step')),'--void',str(out/'void.step'),'--caps',str(out/'caps.step'),'--out',str(out/(case+'.json'))]
 result=subprocess.run(command,capture_output=True,text=True)
 receipt=json.loads((out/(case+'.json')).read_text())
 assert receipt['passed'] is expected and (result.returncode==0) is expected, result.stdout+result.stderr
 if case=='blind_port':
  assert not all(item['port_reaches_exterior_when_uncapped'] for item in receipt['individual_port_opening_checks'])
  assert all(abs(value)<1e-3 for value in receipt['actual_vs_intended_void'].values())
 results[case]={'passed':receipt['passed'],'components':len(receipt['free_space_components']),'port_open_checks':[item['port_reaches_exterior_when_uncapped'] for item in receipt['individual_port_opening_checks']],'returncode':result.returncode}
print(json.dumps(results,indent=2))
