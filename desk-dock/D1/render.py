from PIL import Image,ImageDraw
import cadquery as cq
from raster import render,font,arrow
from pathlib import Path
R=Path(__file__).resolve().parent

def make_images(parts,p):
    def objects(test=lambda a:True):return [(a['shape'],a['color']) for a in parts if test(a)]
    page=Image.new('RGB',(1800,1330),'#f8f8f8');d=ImageDraw.Draw(page)
    d.text((60,35),'5680 / HINGE-DOWN DESK DOCK',font=font(42,True),fill='#253238')
    d.text((60,96),'D1  /  Two slim 120 mm extraction fans on the lid side',font=font(25),fill='#5c696e')
    pic,proj=render(objects(),(1050,980),(-1.7,2.9,1.4),pad=40)
    page.paste(pic,(0,150))
    pic2,_=render(objects(lambda a:a['name']!='Precision_5680_REFERENCE' and not 'suction_roof' in a['name']),(700,650),(-1.7,2.6,2.7),pad=35)
    page.paste(pic2,(1080,300));d=ImageDraw.Draw(page)
    d.text((1110,190),'INSIDE THE LOW DECK',font=font(25,True),fill='#253238')
    d.text((1110,235),'Roofs removed to show the fans',font=font(22),fill='#5c696e')
    d.text((1110,970),'Original Dell plug in a removable cap',font=font(22),fill='#253238')
    d.text((1110,1010),'Height / lateral / depth adjustment',font=font(22),fill='#253238')
    d.text((60,1160),'Set down. Slide sideways. Connect.',font=font(29,True),fill='#253238')
    d.text((60,1210),'Air enters the exposed underside, leaves at the hinge, then follows the duct to the lid-side fans.',font=font(23),fill='#5c696e')
    d.text((60,1270),'CAD design study. Dell mesh dimensions guide the fit; insertion, printability and cooling still require qualification.',font=font(20),fill='#78674c')
    page.save(R/'overview.png')

    # Exact center section through the first fan. Camera nearly along X.
    slab=cq.Solid.makeBox(3,230,400,cq.Vector(82.5,-40,-2))
    sect=[]
    for a in parts:
      cut=a['shape'].intersect(slab)
      if cut.Volume()>1e-6:sect.append((cut,a['color']))
    im,pr=render(sect,(920,980),(1,0.0001,.0001),pad=55)
    page=Image.new('RGB',(1500,1190),'#f8f8f8');page.paste(im,(0,135));d=ImageDraw.Draw(page)
    d.text((55,30),'AIR PATH / SECTION THROUGH A FAN',font=font(36,True),fill='#253238')
    d.text((55,88),'Intake face stays exposed. The duct couples only to the hinge exhaust.',font=font(23),fill='#5c696e')
    def pt(y,z):
      q=pr([[84,y,z]])[0];return (q[0],q[1]+135)
    for a,b in [((-52,130),(-13,130)),((0,53),(0,39)),((5,39),(75,39)),((91,37),(91,8)),((100,9),(160,9))]:
      arrow(d,pt(*a),pt(*b),(22,139,136),4)
    d.text((950,240),'1  Exposed underside intake',font=font(23,True),fill='#253238')
    d.text((950,330),'2  Laptop fans + heat sink',font=font(23,True),fill='#253238')
    d.text((950,420),'3  Hinge exhaust below case',font=font(23,True),fill='#253238')
    d.text((950,510),'4  Curved suction chamber',font=font(23,True),fill='#253238')
    d.text((950,600),'5  120 x 15 mm fan, downward',font=font(23,True),fill='#253238')
    d.text((950,690),'6  Discharge toward lid side',font=font(23,True),fill='#253238')
    d.text((950,805),'Arrows show intended direction.',font=font(21),fill='#5c696e')
    d.text((950,845),'No CFD or measured flow claim.',font=font(21),fill='#5c696e')
    d.text((55,1120),'Soft hinge seals limit room-air bypass. The outlet skirt separates discharge from the underside intake.',font=font(22),fill='#5c696e')
    page.save(R/'air-path.png')

    names=['plug_support','carrier','clamp','cap','REFERENCE','lock','jack','stop']
    subset=[a for a in parts if any(n in a['name'] for n in names) and 'Precision' not in a['name']]
    P=p['rear_case_seat_z']+p['port_from_rear_case']
    crop=cq.Solid.makeBox(75,90,60,cq.Vector(-60,-40,P-38))
    close=[]
    for a in subset:
      s=a['shape'].intersect(crop)
      if s.Volume()>1e-6:close.append((s,a['color']))
    im,_=render(close,(900,900),(-2.8,-2.2,1.5),pad=55)
    page=Image.new('RGB',(1500,1050),'#f8f8f8');page.paste(im,(0,130));d=ImageDraw.Draw(page)
    d.text((50,28),'DIAL IN THE CONNECTOR AFTER ASSEMBLY',font=font(35,True),fill='#253238')
    d.text((950,210),'Z  Height: +/-5 mm',font=font(27,True),fill='#253238')
    d.text((950,255),'M3 x 0.5 jack + two lock screws',font=font(22),fill='#5c696e')
    d.text((950,345),'Y  Lateral: +/-3 mm',font=font(27,True),fill='#253238')
    d.text((950,390),'Transverse slots + two lock screws',font=font(22),fill='#5c696e')
    d.text((950,480),'X  Depth: +/-5 mm',font=font(27,True),fill='#253238')
    d.text((950,525),'Longitudinal slots below cassette',font=font(22),fill='#5c696e')
    d.text((950,615),'Separate chassis stop',font=font(27,True),fill='#253238')
    d.text((950,660),'Calibrate only after full seating',font=font(22),fill='#5c696e')
    d.text((950,750),'Replaceable cap + soft liners',font=font(25,True),fill='#253238')
    d.text((950,795),'Release cable without moving stages',font=font(22),fill='#5c696e')
    d.text((50,995),'Adjustment layout: threads, nut captures and fastener access need the final production-detail pass.',font=font(21),fill='#78674c')
    page.save(R/'adjustment.png')
    print('Rendered overview, section and adjustment views.',flush=True)
