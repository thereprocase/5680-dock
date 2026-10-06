"""Validate a viewer mesh bundle (model.json + model.bin) without assuming any fixed
entry count or byte size: every entry's position/index ranges must lie inside the
binary, index values must address that entry's own vertices, ranges must not
overlap, and together they must cover the whole file. Counts are cross-checked
against generated/manifest.json when it is present."""
import json,struct,sys
from pathlib import Path
d=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent/'viewer-export'
man=json.loads((d/'model.json').read_text());data=(d/'model.bin').read_bytes();n=len(data)
spans=[]
for e in man['parts']:
    po,vc,io,ic=e['positionOffset'],e['vertexCount'],e['indexOffset'],e['indexCount']
    assert po%4==0 and io%4==0 and vc>0 and ic>0 and ic%3==0,e['name']
    assert po+12*vc<=n and io+4*ic<=n,(e['name'],'range outside binary')
    idx=struct.unpack_from('<%dI'%ic,data,io)
    assert max(idx)<vc,(e['name'],'index addresses a vertex outside its block')
    spans+=[(po,po+12*vc,e['name']),(io,io+4*ic,e['name'])]
spans.sort()
for (a0,a1,an),(b0,b1,bn) in zip(spans,spans[1:]):assert a1<=b0,('overlap',an,bn)
assert spans[0][0]==0 and spans[-1][1]==n and all(a1==b0 for (a0,a1,_),(b0,_,_) in zip(spans,spans[1:])),'binary not fully covered'
printed=[e for e in man['parts'] if not e['reference']];refs=[e for e in man['parts'] if e['reference']]
g=Path(__file__).resolve().parent/'generated/manifest.json'
if g.exists():
    m=json.loads(g.read_text());assert len(printed)==len(m['parts']),(len(printed),len(m['parts']))
    assert {e['name'] for e in printed}=={p['part'] for p in m['parts']}
print(json.dumps({'revision':man['revision'],'entries':len(man['parts']),'printed':len(printed),'references':[e['name'] for e in refs],'model_bin_bytes':n,'valid':True}))
