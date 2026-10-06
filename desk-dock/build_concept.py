"""Rebuild review-only desk dock STEP and CAD-derived overview. Python/CadQuery 2.8.
X = laptop width/insertion axis, Y = closed thickness, Z = front edge to hinge.
The laptop translates in -X to dock; x=0 is its nominal docked left edge.
"""
from pathlib import Path
import json
import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parent
p = json.loads((ROOT/'parameters.json').read_text())
W,D,T = (p[k] for k in ['laptop_width','laptop_depth','laptop_thickness'])
S = p['support_z']; P = S+p['port_height_from_front_edge']
Y = p['port_offset_from_midplane']; G=T/2+p['guide_clearance_per_face']
parts=[]
def box(x,y,z,a,b,c):
    return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z))
def add(name,shape,color,reference=False):
    parts.append((name,shape,color,reference))

# Long metal spine shown as an envelope; two desktop feet receive desk screws.
spine=box(-55,-22,4,W+95,44,6)
add('Metal_spine_envelope',spine,'#536975')
for i,x in enumerate([45,W-65]):
    foot=box(x-26,-80,0,52,160,10)
    for yy in [-65,65]:
        foot=foot.cut(cq.Workplane('XY').center(x,yy).circle(2.7).extrude(12))
    saddle=box(x-22,-G-6,10,44,2*G+12,8)
    for sign in [-1,1]:
        yy=G if sign==1 else -G-5
        cheek=box(x-22,yy,18,44,5,38)
        saddle=saddle.union(cheek)
    add(f'Foot_{i+1}',foot,'#536975')
    add(f'Trough_saddle_{i+1}',saddle,'#168c93')
    add(f'Contact_pad_{i+1}',box(x-22,-T/2,18,44,T,2),'#e9b35c')

# Frame leaves the connector and its cable accessible. Slots indicate Z setup.
tower=box(-49,-43,10,24,86,9)
for yy in [-43,35]:
    col=box(-49,yy,19,24,8,P+30-19)
    slot=box(-43,yy-1,P-28,12,10,48)
    col=col.cut(slot)
    tower=tower.union(col)
tower=tower.union(box(-49,-43,P+30,24,86,8))
add('Slotted_connector_frame',tower,'#168c93')

L,B,H=(p[k] for k in ['plug_body_length','plug_body_width','plug_body_height'])
# Split cassette envelopes: actual cavity must follow the measured overmold.
for label,zz in [('lower',P-H/2-5),('upper',P+H/2)]:
    clamp=box(-L-3,Y-B/2-6,zz,L+2,B+12,5)
    for xx in [-L+3,-6]:
        for yy in [Y-B/2-3,Y+B/2+3]:
            clamp=clamp.cut(cq.Workplane('XY').center(xx,yy).circle(1.7).extrude(400))
    add('Cassette_'+label+'_envelope',clamp,'#e9b35c')
add('Dell_overmold_PLACEHOLDER',box(-L,Y-B/2,P-H/2,L,B,H),'#333b40',True)
add('USB_C_tip_PLACEHOLDER',box(0,Y-4.2,P-1.3,6.5,8.4,2.6),'#aebbc2',True)
# Upper face guides engage 25 mm of chassis before its edge reaches x=0.
for yy in [-G-5,G]:
    add('Port_level_guide_'+str(yy),box(-25,yy,P-22,50,5,44),'#168c93')
add('Chassis_stop_ENVELOPE',box(-5,-T/2,52,5,T,12),'#e9b35c')
add('Laptop_REFERENCE',box(0,-T/2,S,W,T,D),'#9bacb6',True)

assembly=cq.Assembly(name='5680_desk_dock_CONCEPT')
records=[]
for name,shape,color,ref in parts:
    v=shape.val()
    assert v.isValid() and v.Volume()>0 and len(shape.solids().vals())==1, name
    assembly.add(shape,name=name,color=cq.Color(color))
    records.append({'name':name,'valid':v.isValid(),'volume_mm3':v.Volume(),'reference':ref})
assembly.save(str(ROOT/'Desk_Dock_CONCEPT.step'))
(ROOT/'geometry_review.json').write_text(json.dumps({'scope':'Individual solid validity only. Assembly contains conceptual unfastened interfaces and intentional reference intersections; no fit or production acceptance.', 'parts':records},indent=2)+'\n')

fig=plt.figure(figsize=(14,8),facecolor='#f4f6f7')
ax=fig.add_subplot(111,projection='3d',facecolor='#f4f6f7')
for name,shape,color,ref in parts:
    verts,faces=shape.val().tessellate(1)
    vv=[v.toTuple() for v in verts]
    polys=[[vv[j] for j in f] for f in faces]
    ax.add_collection3d(Poly3DCollection(polys,facecolor=color,edgecolor='none',alpha=.20 if name=='Laptop_REFERENCE' else 1))
ax.set(xlim=(-70,390),ylim=(-95,95),zlim=(0,290))
ax.set_box_aspect((460,190,290)); ax.view_init(23,-59); ax.set_axis_off()
ax.quiver(170,0,285,-80,0,0,color='#168c93',arrow_length_ratio=.15,linewidth=3)
ax.text(100,0,299,'SLIDE TO DOCK',fontsize=10,color='#126c72')
fig.text(.05,.94,'PRECISION 5680 / SLIDE-IN DESK DOCK',fontsize=21,weight='bold',color='#243842')
fig.text(.05,.895,'D0 concept • closed laptop, hinge up • actual CAD geometry',fontsize=12,color='#536975')
fig.text(.05,.10,'TEAL  trough + alignment frame     GOLD  pads + split plug cassette\nGRAY  metal spine + desk feet     TRANSLUCENT  laptop envelope',fontsize=11,color='#243842',linespacing=1.7)
fig.text(.05,.035,'NOT A PRINT RELEASE — port location, overmold, guide attachments and lift interlock require development.',fontsize=10,color='#8e4b25')
fig.savefig(ROOT/'concept.png',dpi=160); plt.close(fig)
print('Built',len(parts),'valid concept solids; STEP and CAD overview exported.')
