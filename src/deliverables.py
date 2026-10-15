from pathlib import Path
import sys,json,math,csv,html
ROOT=Path(__file__).resolve().parents[1]
_pyd=ROOT.parent/'tools'/'pydeps'
if _pyd.is_dir():sys.path.insert(0,str(_pyd))
import ezdxf
from shapely.geometry import Polygon,box
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4,A3,landscape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image
from reportlab.lib.styles import ParagraphStyle
from design import config,write_data,full_outline
from manual_content import SECTIONS
p=config();a=write_data();templates=json.loads((ROOT/'data'/'templates.json').read_text())
NAVY=colors.HexColor('#183448');TEAL=colors.HexColor('#087d91');GRAY=colors.HexColor('#637b8a')
style=ParagraphStyle('body',fontName='Helvetica',fontSize=10.5,leading=18,spaceAfter=11,textColor=NAVY)
heading=ParagraphStyle('heading',parent=style,fontSize=22,leading=29,spaceAfter=17)
tokens=dict(mass=f"{a['estimated_mass_g']:.1f}",cost=a['estimated_purchase_cny'],reserve=5000-a['estimated_purchase_cny'],area=f"{a['reference_area_dm2']:.3f}",ar=f"{a['aspect_ratio']:.3f}",mac=f"{a['mac_mm']:.2f}",xle=f"{a['mac_le_x_mm']:.2f}",cg0=f"{a['initial_cg_x_mm'][0]:.1f}",cg1=f"{a['initial_cg_x_mm'][1]:.1f}",cg=f"{a['estimated_cg_x_mm']:.2f}",battery_x=f"{a['battery_x_for_cg_midpoint_mm']:.1f}",np=f"{a['quarter_chord_x_mm']:.1f}",loading=f"{a['wing_loading_g_dm2']:.2f}",speeds='/'.join(f'{v:.2f}' for v in a['clmax_sensitivity_speed_m_s'].values()),twloss=f"{a['thrust_ratio_20pct_install_loss']:.2f}",force=f"{a['spar_tip_load_N']:.2f}",moment=f"{a['spar_root_moment_Nm']:.3f}",stress=f"{a['spar_stress_MPa']:.1f}",deflection=f"{a['spar_tip_deflection_mm']:.1f}")
def footer(c,d):
    c.setStrokeColor(colors.HexColor('#c5d4dc'));c.line(18*mm,17*mm,192*mm,17*mm)
    c.setFont('Helvetica',8);c.setFillColor(GRAY);c.drawString(18*mm,12*mm,'SR71 / 600   V1.0-P0   Digital trial-production build · Not cleared for flight');c.drawRightString(192*mm,12*mm,str(d.page))
flow=[];md=['# SR71 / 600 Engineering Report and Assembly Manual','']
for i,(title,paragraphs) in enumerate(SECTIONS):
    if i:flow.append(PageBreak())
    flow.append(Paragraph(html.escape(title),heading));md.extend(['## '+title,''])
    for t in paragraphs:
        if t.startswith('@IMAGE:'):
            flow.append(Image(str(ROOT/'docs'/t.split(':')[1]),width=172*mm,height=106*mm));flow.append(Spacer(1,4*mm))
        else:
            t=t.format(**tokens);flow.append(Paragraph(html.escape(t),style));md.extend([t,''])
SimpleDocTemplate(str(ROOT/'docs'/'engineering_report.pdf'),pagesize=A4,rightMargin=19*mm,leftMargin=19*mm,topMargin=18*mm,bottomMargin=23*mm,title='SR-71 600 Engineering Report and Assembly Manual').build(flow,onFirstPage=footer,onLaterPages=footer)
(ROOT/'docs'/'engineering_report.md').write_text('\n'.join(md),encoding='utf-8')

def net_polys(t):
    shape=Polygon(t['outline'])
    if t['name'].startswith('F01'):
        for sign in [1,-1]:
            lo,hi=sorted([124.3*sign,220*sign]);shape=shape.difference(box(494.3,lo,536,hi))
        for sign in [1,-1]:shape=shape.difference(box(465.5,sign*145-4.7,484.5,sign*145+4.7))
    for h in t['holes']:
        if 'rect' in h:
            x,y,w,hh=h['rect'];shape=shape.difference(box(x,y,x+w,y+hh))
    return [shape] if shape.geom_type=='Polygon' else list(shape.geoms)
def draw_poly(c,pts):
    path=c.beginPath();path.moveTo(*pts[0])
    for pt in pts[1:]:path.lineTo(*pt)
    path.close();c.drawPath(path)
def graphics(c,t):
    c.setStrokeColor(colors.black);c.setLineWidth(.15)
    for sh in net_polys(t):
        draw_poly(c,list(sh.exterior.coords)[:-1])
        for ring in sh.interiors:draw_poly(c,list(ring.coords)[:-1])
    for h in t['holes']:
        if 'circle' in h:c.circle(*h['circle'],stroke=1,fill=0)
    if t['name'].startswith('F01'):
        c.setStrokeColor(TEAL);c.setDash(3,2);c.line(480,-190,480,190)
        for y in [-95,95]:c.line(330,y,545,y)
        c.setDash();c.setStrokeColor(colors.HexColor('#cc6622'))
        for x in a['initial_cg_x_mm']:c.line(x,-30,x,30)
for t in templates:
    d=ezdxf.new('R2010');d.units=4;ms=d.modelspace()
    for name,col in [('CUT',7),('SCORE',4),('DRILL_VERIFY',1),('ANNOTATION',8)]:d.layers.new(name,dxfattribs={'color':col})
    for sh in net_polys(t):
        ms.add_lwpolyline(list(sh.exterior.coords)[:-1],close=True,dxfattribs={'layer':'CUT'})
        for ring in sh.interiors:ms.add_lwpolyline(list(ring.coords)[:-1],close=True,dxfattribs={'layer':'CUT'})
    for h in t['holes']:
        if 'circle' in h:cx,cy,r=h['circle'];ms.add_circle((cx,cy),r,dxfattribs={'layer':'CUT'})
    if t['name'].startswith('F01'):
        ms.add_line((480,-190),(480,190),dxfattribs={'layer':'SCORE'})
        for y in [-95,95]:ms.add_line((330,y),(545,y),dxfattribs={'layer':'SCORE'})
    if t['name'].startswith('W03'):
        ms.add_line((-6,0),(6,0),dxfattribs={'layer':'DRILL_VERIFY'});ms.add_line((0,-6),(0,6),dxfattribs={'layer':'DRILL_VERIFY'})
    minx=min(x for x,y in t['outline']);miny=min(y for x,y in t['outline'])
    ms.add_text(t['name']+' | '+t['material']+' '+str(t['thickness_mm'])+'mm | QTY '+str(t['qty']),dxfattribs={'height':3,'insert':(minx,miny-9),'layer':'ANNOTATION'})
    d.saveas(ROOT/'cut'/(t['name']+'.dxf'))

# 1:1 printing: every drawing coordinate is multiplied by reportlab's physical mm.
c=canvas.Canvas(str(ROOT/'docs'/'cutting_templates_1to1.pdf'),pagesize=A4);index=[];page_num=0
for t in templates:
    xmin=min(x for x,y in t['outline']);ymin=min(y for x,y in t['outline']);xmax=max(x for x,y in t['outline']);ymax=max(y for x,y in t['outline'])
    W,H=190,245;stepx,stepy=180,235
    nx=max(1,math.ceil(max(0,xmax-xmin-W)/stepx)+1);ny=max(1,math.ceil(max(0,ymax-ymin-H)/stepy)+1)
    for row in range(ny):
        for col in range(nx):
            page_num+=1;x0=xmin+col*stepx;y0=ymin+row*stepy
            c.setFont('Helvetica',9);c.setFillColor(NAVY);c.drawString(10*mm,286*mm,t['name']+f" | {t['material']} {t['thickness_mm']}mm | QTY {t['qty']}")
            c.setFont('Helvetica',8);c.drawString(10*mm,280*mm,f'Row {row+1}/{ny} Col {col+1}/{nx} | Origin ({x0:.1f},{y0:.1f}) | Print at 100%; do not fit to page')
            c.saveState();c.translate(10*mm,30*mm);c.scale(mm,mm);clip=c.beginPath();clip.rect(0,0,W,H);c.clipPath(clip,stroke=0);c.translate(-x0,-y0);graphics(c,t);c.restoreState()
            c.setStrokeColor(colors.HexColor('#aebcc5'));c.setLineWidth(.4);c.rect(10*mm,30*mm,W*mm,H*mm)
            c.saveState();c.translate(10*mm,30*mm);c.scale(mm,mm);c.setLineWidth(.12);c.setStrokeColor(GRAY)
            for gx in range(math.ceil(x0/50)*50,math.floor((x0+W)/50)*50+1,50):
                for gy in range(math.ceil(y0/50)*50,math.floor((y0+H)/50)*50+1,50):
                    xx=gx-x0;yy=gy-y0;c.line(xx-1.5,yy,xx+1.5,yy);c.line(xx,yy-1.5,xx,yy+1.5)
            c.restoreState()
            c.setStrokeColor(NAVY);c.setLineWidth(.7);c.line(10*mm,18*mm,110*mm,18*mm);c.line(10*mm,16*mm,10*mm,20*mm);c.line(110*mm,16*mm,110*mm,20*mm)
            c.setFont('Helvetica',8);c.drawString(115*mm,17*mm,'Horizontal check 100 mm');c.drawString(10*mm,10*mm,'Grid cross spacing 50 mm; adjacent pages overlap 10 mm; blue lines = score/locate, black lines = cut through.')
            c.drawRightString(200*mm,5*mm,str(page_num));index.append(dict(page=page_num,part=t['name'],row=row+1,col=col+1,origin_x_mm=x0,origin_y_mm=y0));c.showPage()
c.save();(ROOT/'data'/'tile_index.json').write_text(json.dumps(index,indent=2),encoding='utf-8')

c=canvas.Canvas(str(ROOT/'docs'/'assembly_dimensions.pdf'),pagesize=landscape(A3))
def frame(title,sub):
    c.setFont('Helvetica',18);c.setFillColor(NAVY);c.drawString(15*mm,280*mm,title);c.setFont('Helvetica',9);c.setFillColor(GRAY);c.drawString(15*mm,272*mm,sub)
    c.setStrokeColor(GRAY);c.line(15*mm,17*mm,405*mm,17*mm);c.setFont('Helvetica',8);c.drawString(15*mm,11*mm,'V1.0-P0 | Units: mm | Digital trial-production build: hole positions and flight parameters not measured or released')
def dim(x1,y1,x2,y2,label):
    c.setStrokeColor(GRAY);c.setLineWidth(.25);c.line(x1,y1,x2,y2);c.setFont('Helvetica',6)
    if abs(y1-y2)<.01:
        c.line(x1,y1-3,x1,y1+3);c.line(x2,y2-3,x2,y2+3);c.drawCentredString((x1+x2)/2,y1+4,label)
    else:c.line(x1-3,y1,x1+3,y1);c.line(x2-3,y2,x2+3,y2);c.drawString(x1+4,(y1+y2)/2,label)
frame('01 / General Arrangement, Top View and Assembly Datums','Scale 1:2; X from nose to tail; +Y is the aircraft left side. Teal lines: structural members; orange lines: preliminary CG window.')
c.saveState();c.translate(36*mm,138*mm);c.scale(.5*mm,.5*mm);c.setStrokeColor(NAVY);c.setLineWidth(.5);draw_poly(c,full_outline(p))
for t in templates:
    if t['name'].startswith('F02'):draw_poly(c,t['outline'])
c.setStrokeColor(TEAL)
for yy in [-95,95]:
    c.rect(278,yy-20,288,40);c.line(330,yy,545,yy);c.setDash(3,2);c.line(238,yy,600,yy);c.setDash();c.rect(586,yy-25.4,4,50.8)
c.line(480,-190,480,190);c.rect(70,-22,390,44);c.setStrokeColor(colors.HexColor('#dc7c24'));c.rect(p['battery_center_x_mm']-30,-15,60,30)
for x in a['initial_cg_x_mm']:c.line(x,-70,x,70)
dim(0,-235,590,-235,'Overall envelope 590 / limit 600');dim(0,-215,570,-215,'Fuselage 570');dim(620,-210,620,210,'Wingspan 420');dim(560,-95,560,95,'Axis spacing 190');c.restoreState()
c.setFont('Helvetica',9);c.setFillColor(NAVY);c.drawString(30*mm,250*mm,f"Preliminary CG X={a['initial_cg_x_mm'][0]:.1f}-{a['initial_cg_x_mm'][1]:.1f}; first-order estimate from the full chine projection, to be confirmed by glide testing.")
c.drawString(30*mm,242*mm,'Nacelle OD 40; motor axis Z=20; propeller diameter 50.8; elevon hinge at X=495, gap 0.7.');c.showPage()
frame('02 / Side View, Front View, and Height','Side/front views at 1:2. Equipment shown as assembly envelopes only; motor hole positions and screw lengths to be verified against hardware.')
c.saveState();c.translate(35*mm,190*mm);c.scale(.5*mm,.5*mm);c.setStrokeColor(NAVY);c.setLineWidth(.5)
draw_poly(c,[(0,0),(70,28),(460,28),(570,4),(570,0)]);c.rect(278,0,288,40);draw_poly(c,[(420,42),(480,97),(527,92),(543,42)])
c.rect(568,13.25,15.5,13.5);c.rect(586,-5.4,4,50.8);draw_poly(c,[(510,0),(550,0),(568,-8),(560,-14),(525,-14)]);c.rect(95,5,60,16)
dim(0,-35,590,-35,'590');dim(610,-14,610,97,'Height envelope approx. 110');c.setStrokeColor(GRAY);c.setDash(4,2);c.line(0,20,600,20);c.setDash();c.restoreState()
c.saveState();c.translate(200*mm,76*mm);c.scale(.5*mm,.5*mm);c.setStrokeColor(NAVY);c.line(-210,0,210,0)
for sign in [-1,1]:
    y=sign*95;c.circle(y,20,20);c.setStrokeColor(colors.HexColor('#c66626'));c.circle(y,20,25.4);c.setStrokeColor(NAVY);c.line(y,42,y-sign*55*math.sin(math.radians(15)),42+55*math.cos(math.radians(15)))
dim(-210,-35,210,-35,'420');dim(-95,-55,95,-55,'190');c.restoreState()
c.setFont('Helvetica',10)
for i,t in enumerate(['Main spar center Z=4, longitudinal rods center Z=1; vertically offset—do not drill through the carbon tubes.','Skid bottom Z=-14; propeller disc bottom Z=-5.4; level static clearance 8.6.','Vertical tails canted 15° inward. No rudder in the initial version; continued flight on a single motor is not verified.']):c.drawString(35*mm,(143-i*9)*mm,t)
c.showPage()
frame('03 / Internal Layout and Part Classification','Teal: printed parts; gold: plywood/carbon rods; orange: battery. Rendered from CAD geometry; no scale indicated.')
c.drawImage(str(ROOT/'docs'/'cutaway.png'),15*mm,40*mm,width=295*mm,height=182*mm,mask='auto');c.setFont('Helvetica',10);c.setFillColor(NAVY)
for i,t in enumerate(['Forward ESCs X=70–95','Battery center X=120–220','BEC center X=295','Receiver center X=315','Stabilizer center X=325','Empty parachute bay X=373–413','Motor mounts X=566–568','Removable ballast X~80','Weigh and measure CG before closing']):c.drawString(315*mm,(225-i*16)*mm,t)
c.showPage()
frame('04 / Electrical Block Diagram and Signal Interfaces','Functional block diagram; does not represent actual connector pin orders. Control supply 5 V throughout; propulsion 2S.')
def block(x,y,w,h,label):
    c.setFillColor(colors.HexColor('#e2edf1'));c.setStrokeColor(TEAL);c.roundRect(x*mm,y*mm,w*mm,h*mm,3*mm,fill=1);c.setFillColor(NAVY);c.setFont('Helvetica',10)
    for i,l in enumerate(label.split('\n')):c.drawCentredString((x+w/2)*mm,(y+h/2+3-i*5)*mm,l)
def line(x1,y1,x2,y2,color=TEAL):c.setStrokeColor(color);c.setLineWidth(1);c.line(x1*mm,y1*mm,x2*mm,y2*mm)
block(22,205,62,26,'2S 550mAh\nXT30');block(118,228,67,24,'Left ESC -> left motor');block(118,190,67,24,'Right ESC -> right motor');block(118,146,67,25,'Independent BEC\n5V / 2A')
line(84,218,100,218);line(100,218,100,240);line(100,240,118,240);line(100,218,100,202);line(100,202,118,202);line(100,202,100,158);line(100,158,118,158)
block(224,146,76,25,'5V control bus\nall signals common ground');line(185,158,224,158)
block(223,91,77,30,'RP1 TX -> A3 serial\n5V / GND / signal');block(325,185,65,31,'A3 Mini\nDelta / 50Hz');block(325,112,65,25,'AIL -> left elevon servo\nELE -> right elevon servo')
line(300,158,317,158);line(317,158,317,200);line(317,200,325,200);line(260,146,260,121);line(300,106,312,106);line(312,106,312,190);line(312,190,325,190);line(358,185,358,137)
orange=colors.HexColor('#dc7c24');line(325,210,205,210,orange);line(205,210,205,240,orange);line(205,240,185,240,orange);line(205,210,205,202,orange);line(205,202,185,202,orange)
c.setFont('Helvetica',9);c.setFillColor(NAVY);c.drawString(210*mm,222*mm,'THR signal split into two paths; ESCs have no BEC')
for i,t in enumerate(['CH1 roll, CH2 pitch, CH3 dual-motor throttle, CH5 arm flag, CH6 mode; CH4/7/8 reserved.','Disable delta mixing in the transmitter; the A3 Mini mixes once; the RP1 must be powered at 5 V.','With propellers removed, check all three lost-link cases: transmitter off, serial disconnected, receiver unpowered; both motors must stop.','Select CRSF-compatible firmware on the A3; the mode channel moves to CH6. Verify every pin against the hardware markings.']):c.drawString(22*mm,(66-i*10)*mm,t)
c.showPage();c.save()

records=[('MASS','All-up mass and CG'),('FIT','Hole positions and actual equipment dimensions'),('THRUST','Thrust/current/voltage/temperature/duration'),('POWER','BEC bus loading and restarts'),('FAIL1','Transmitter switched off'),('FAIL2','Receiver serial link disconnected'),('FAIL3','Receiver power loss'),('STRUCT','Load/deflection/residual set after unloading'),('RANGE','Range/interference'),('GLIDE','Unpowered glide trim'),('FLIGHT1','First flight'),('FLIGHT2','Second flight'),('FLIGHT3','Third flight')]
fpath=ROOT/'data'/'test_records.csv'
if not fpath.exists():
    with fpath.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['id','test','status','date','operator','configuration','measurement','result','issue']);w.writerows([(i,t,'NOT TESTED','','','','','','') for i,t in records])
print('PDFs, DXFs and test records generated; tile pages:',len(index))
