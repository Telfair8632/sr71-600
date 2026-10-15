"""Run with the bundled FreeCAD Python. Regenerates native FCStd, STEP and STLs.
Physical solids and purchased-part keepouts are separate. No propeller blade STL.
"""
from pathlib import Path
import sys, json, math, traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import FreeCAD as App, Part, MeshPart
from design import config, full_outline, calculate
p=config(); a=calculate(p); V=App.Vector
doc=App.newDocument('SR71_600_P0')
groups={n:doc.addObject('App::DocumentObjectGroup',n) for n in ['Foam','Structure','Printed','Equipment','Keepouts']}
objects=[]; meshes=[]; templates=[]
palette={'Foam':(0.15,0.19,0.24),'Structure':(.75,.58,.30),'Printed':(.10,.65,.72),'Equipment':(.33,.44,.60),'Keepouts':(.9,.3,.12)}
def add(name,shape,group='Foam',material='',status='PROTOTYPE',color=None):
    o=doc.addObject('Part::Feature',name);o.Label=STEP_POSITION_LABELS.get(name,name);o.Shape=shape
    for prop,value in [('Material',material),('ReleaseStatus',status),('Source','config/design.json + src/build_cad.py')]:
        o.addProperty('App::PropertyString',prop,'Design');setattr(o,prop,value)
    groups[group].addObject(o);objects.append((o,group))
    c=color or palette[group]
    if App.GuiUp:
        o.ViewObject.ShapeColor=c
        if group=='Keepouts':o.ViewObject.Transparency=85
    if not shape.isNull():
        vs,ts=shape.tessellate(.65)
        meshes.append(dict(name=name,group=group,color=c,vertices=[[round(v.x,3),round(v.y,3),round(v.z,3)] for v in vs],triangles=ts))
    return o
def face_xy(poly,z=0):
    vs=[V(x,y,z) for x,y in poly];return Part.Face(Part.makePolygon(vs+[vs[0]]))
def slab(poly,z,t):return face_xy(poly,z).extrude(V(0,0,t))
def template(name,poly,material,thickness,qty=1,holes=None,note='NET OUTLINE; confirm stock thickness and kerf'):
    templates.append(dict(name=name,outline=poly,material=material,thickness_mm=thickness,qty=qty,holes=holes or [],note=note))
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
def cylinder_x(r,x,y,z,length):return Part.makeCylinder(r,length,V(x,y,z),V(1,0,0))
def extrude_xz(poly,y,t):
    pts=[V(x,y,z) for x,z in poly];return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,t,0))
def loft_rect(stations):
    wires=[]
    for x,w,z0,z1 in stations:
        vs=[V(x,-w,z0),V(x,w,z0),V(x,w,z1),V(x,-w,z1)]
        wires.append(Part.makePolygon(vs+[vs[0]]))
    return Part.makeLoft(wires,True,True)

# Part.export writes a flat STEP shape representation. Without names, many
# downstream viewers synthesize labels such as "Part 1". Keep the native
# FreeCAD identifiers stable, but write an explicit position label for every
# exported physical entity into the STEP representation item.
STEP_POSITION_LABELS={
    'Elevon_L':'Left elevon (left trailing-edge surface)', 'Elevon_R':'Right elevon (right trailing-edge surface)',
    'Wing_chine_base':'Integral wing and chine plate', 'Fuselage_side_L':'Central fuselage left side wall',
    'Fuselage_side_R':'Central fuselage right side wall', 'Fuselage_roof_frame':'Central fuselage roof frame',
    'Battery_hatch':'Forward battery hatch', 'Avionics_hatch':'Aft avionics hatch',
    'Nose_carve_block':'Nose foam carving block', 'Tail_carve_block':'Tail foam carving block',
    'Cockpit_foam':'Cockpit foam fairing', 'Battery_tray':'Battery tray',
    'Bulkhead_98':'Forward bulkhead (X=98)', 'Bulkhead_287':'Mid bulkhead (X=287)',
    'Bulkhead_419':'Aft bulkhead (X=419)', 'Carbon_main_spar':'Transverse carbon-tube main spar',
    'Carbon_longeron_L':'Left nacelle carbon longeron', 'Carbon_longeron_R':'Right nacelle carbon longeron',
    'Nacelle_skin_L':'Left engine nacelle foam skin', 'Nacelle_skin_R':'Right engine nacelle foam skin',
    'Intake_spike_L':'Left intake spike fairing', 'Intake_spike_R':'Right intake spike fairing',
    'Spike_web_L':'Left intake spike support web', 'Spike_web_R':'Right intake spike support web',
    'Nacelle_former_L_285':'Left nacelle forward former (X=285)',
    'Nacelle_former_L_430':'Left nacelle mid former (X=430)',
    'Nacelle_former_L_548':'Left nacelle aft former (X=548)',
    'Nacelle_former_R_285':'Right nacelle forward former (X=285)',
    'Nacelle_former_R_430':'Right nacelle mid former (X=430)',
    'Nacelle_former_R_548':'Right nacelle aft former (X=548)',
    'Motor_firewall_L':'Left motor firewall blank', 'Motor_firewall_R':'Right motor firewall blank',
    'Motor_saddle_L':'Left motor saddle', 'Motor_saddle_R':'Right motor saddle',
    'Vertical_fin_L':'Left vertical fin', 'Vertical_fin_R':'Right vertical fin',
    'Fin_saddle_L_474':'Left fin forward saddle (X=474)', 'Fin_saddle_L_515':'Left fin aft saddle (X=515)',
    'Fin_saddle_R_474':'Right fin forward saddle (X=474)', 'Fin_saddle_R_515':'Right fin aft saddle (X=515)',
    'Belly_skid_L':'Left belly wear skid', 'Belly_skid_R':'Right belly wear skid',
    'Motor_envelope_L':'Left brushless motor installation envelope', 'Motor_envelope_R':'Right brushless motor installation envelope',
    'Servo_envelope_L':'Left elevon servo installation envelope', 'Servo_envelope_R':'Right elevon servo installation envelope',
    'Pushrod_L':'Left elevon pushrod', 'Pushrod_R':'Right elevon pushrod',
    'Control_horn_L':'Left elevon control horn', 'Control_horn_R':'Right elevon control horn',
    'Battery_envelope':'2S battery installation envelope', 'ESC_envelope_L':'Left ESC installation envelope',
    'ESC_envelope_R':'Right ESC installation envelope', 'BEC_envelope':'Standalone BEC installation envelope',
    'Receiver_envelope':'ELRS receiver installation envelope', 'Gyro_envelope':'Delta-wing stabilizer installation envelope',
    'Removable_trim_steel':'Removable nose ballast installation envelope',
}
def export_named_step(path,physical):
    # Import.export creates one STEP product definition per source object;
    # Part.export flattens them and loses the labels in many CAD viewers.
    import Import
    Import.export(physical,str(path))
    raw=path.read_text(encoding='utf-8')
    missing=[]
    for obj in physical:
        label=STEP_POSITION_LABELS.get(obj.Name)
        if not label:
            raise RuntimeError(f'Missing STEP position label for {obj.Name}')
        if label not in raw:
            missing.append(obj.Name)
    if missing:
        raise RuntimeError('STEP export lost position labels: '+', '.join(missing))

# Spreadsheet is a readable parameter manifest. Regeneration from JSON is explicit.
sheet=doc.addObject('Spreadsheet::Sheet','Parameters')
sheet.set('A1','Parameter');sheet.set('B1','Value / mm unless stated')
for i,(key,val) in enumerate([(k,v) for k,v in p.items() if isinstance(v,(str,int,float))],2):
    sheet.set(f'A{i}',key);sheet.set(f'B{i}',str(val))
sheet.setColumnWidth('A',240);sheet.setColumnWidth('B',340)

# Main 3 mm base includes chines. Separate elevons have a 0.7 mm hinge gap.
base=slab(full_outline(p),0,p['foam_thickness_mm'])
for sign,side in [(1,'L'),(-1,'R')]:
    ep=[(x,sign*y) for x,y in p['elevon_half_outline']]
    cutpoly=[(494.3,sign*124.3),(494.3,sign*220),(536,sign*220),(536,sign*124.3)]
    base=base.cut(slab(cutpoly,-1,5))
    elev=slab(ep,0,3)
    # Neutral rigging is shown flat; reflex is a setup dimension, not hidden CAD rotation.
    add('Elevon_'+side,elev,material='3 mm foam')
    template('F02_Elevon_'+side,ep,'FOAM',3,note='NET; hinge x=495; rig 3 deg up provisionally')
    # Carbon rod grooves and servo pocket through-cut in blank.
    base=base.cut(cylinder_x(1.05,330,sign*95,1,215))
    base=base.cut(box(465.5,sign*145-4.7,-1,19,9.4,6))
base=base.cut(Part.makeCylinder(2.05,380,V(480,-190,4),V(0,1,0)))
add('Wing_chine_base',base,material='3 mm foam')
template('F01_Wing_chine_NET',full_outline(p),'FOAM',3,note='NET outline generated by subtracting elevon slots; grooves on SCORE layer')

# Simple folded-box central fuselage; tapered foam nose/tail carve blocks.
sidepoly=[(70,3),(460,3),(460,25),(70,25)]
for sign,side in [(1,'L'),(-1,'R')]:
    add('Fuselage_side_'+side,extrude_xz(sidepoly,sign*22-(3 if sign==1 else 0),3),material='3 mm foam')
template('F03_Fuselage_side',sidepoly,'FOAM',3,qty=2)
roofpoly=[(70,-22),(460,-22),(460,22),(70,22)]
roof=slab(roofpoly,25,3).cut(box(73,-19,24,210,38,5)).cut(box(299,-19,24,116,38,5))
add('Fuselage_roof_frame',roof,material='3 mm foam')
template('F04_Roof_frame',roofpoly,'FOAM',3,holes=[{'rect':[73,-19,210,38]},{'rect':[299,-19,116,38]}])
for name,x,dx in [('Battery_hatch',73.4,209.2),('Avionics_hatch',299.4,115.2)]:
    add(name,box(x,-18.6,25,dx,37.2,3),material='3 mm foam; tape hinge and front locking tab')
    template('F05_'+name,[(0,0),(dx,0),(dx,37.2),(0,37.2)],'FOAM',3)
add('Nose_carve_block',loft_rect([(0,.25,0,.5),(70,22,0,28)]),material='foam carve block; hollow/trim to mass budget')
add('Tail_carve_block',loft_rect([(460,22,3,28),(520,12,3,12),(570,1,3,4)]),material='foam carve block; hollow/trim to mass budget')
add('Cockpit_foam',loft_rect([(90,5,22,24),(125,10,28,42),(190,9,28,36),(213,2,28,29)]),material='light foam; fit underside to fuselage',color=(.27,.36,.43))

# Battery tray and cross-straps. Long adjustment range; electronic components aft.
traypoly=[(95,-17),(280,-17),(280,17),(95,17)]
tray=slab(traypoly,3,1)
slots=[]
for x in [111,145,179,213,247,269]:
    for y in [-15,11]:
        tray=tray.cut(box(x,y,2,3,4,3));slots.append({'rect':[x,y,3,4]})
add('Battery_tray',tray,'Structure','1 mm plywood')
template('W01_Battery_tray',traypoly,'PLY',1,holes=slots)
for x in [98,287,419]:
    bulk=box(x,-19,3,1,38,22).cut(box(x-1,-15,5,3,30,16))
    add('Bulkhead_'+str(x),bulk,'Structure','1 mm plywood')
template('W02_Bulkhead',[(0,0),(38,0),(38,22),(0,22)],'PLY',1,qty=3,holes=[{'rect':[4,2,30,16]}])

# Spar and rods have actual hollow/solid section geometry.
spar=Part.makeCylinder(2,380,V(480,-190,4),V(0,1,0)).cut(Part.makeCylinder(1,380,V(480,-190,4),V(0,1,0)))
add('Carbon_main_spar',spar,'Structure','carbon tube OD4 ID2; bonded above/below foam locally')
for sign,side in [(1,'L'),(-1,'R')]:
    cy=sign*p['nacelle_spacing_mm']/2
    add('Carbon_longeron_'+side,cylinder_x(1,330,cy,1,215),'Structure','carbon rod OD2')
    # 300 degree rolled nacelle: open bottom seats onto the wing plate.
    outer=[];inner=[]
    for i in range(81):
        th=math.radians(-60+300*i/80)
        outer.append(V(p['nacelle_start_x_mm'],cy+20*math.cos(th),20+20*math.sin(th)))
        inner.append(V(p['nacelle_start_x_mm'],cy+18*math.cos(th),20+18*math.sin(th)))
    wire=Part.makePolygon(outer+inner[::-1]+[outer[0]])
    shell=Part.Face(wire).extrude(V(p['nacelle_end_x_mm']-p['nacelle_start_x_mm'],0,0))
    add('Nacelle_skin_'+side,shell,material='2 mm rolled foam, 300 deg wrap; trim to base')
    cone=Part.makeCone(.6,12,40,V(238,cy,20),V(1,0,0))
    add('Intake_spike_'+side,cone,material='foam carve; NOT functional supersonic inlet')
    # Spike requires an actual supporting web, below centerline.
    add('Spike_web_'+side,box(258,cy-1,3,77,2,15),material='2 mm foam; reaches wing at x335')
    # Curved formers are 1mm ply C sections, open at bottom.
    for x in [285,430,548]:
        ring=cylinder_x(18,x,cy,20,1).cut(cylinder_x(16,x-1,cy,20,3)).cut(box(x-1,cy-22,-3,3,44,6))
        add('Nacelle_former_'+side+'_'+str(x),ring,'Structure','1 mm plywood; final fit to rolled foam')
    firewall=cylinder_x(18,566,cy,20,2).cut(cylinder_x(3,565,cy,20,4))
    add('Motor_firewall_'+side,firewall,'Structure','laminated 2 x 1mm plywood','MOTOR BOLT PATTERN MUST BE VERIFIED')
    # 2mm longeron ends x545; saddle overlaps last 12 mm and carries firewall at x566.
    saddle=box(533,cy-5,0,33,10,1.2)
    for sy in [cy-5,cy+3.8]:saddle=saddle.fuse(box(533,sy,0,33,1.2,5))
    saddle=saddle.fuse(box(564.8,cy-5,0,1.2,10,26))
    for sy in [cy-3,cy+2.2]:
        saddle=saddle.fuse(extrude_xz([(549,4),(564.8,4),(564.8,23)],sy,.8))
    saddle=saddle.cut(cylinder_x(1.1,532,cy,1,35)).removeSplitter()
    add('Motor_saddle_'+side,saddle,'Printed','PETG; load-test before use')
    MeshPart.meshFromShape(Shape=saddle,LinearDeflection=.08,AngularDeflection=.15,Relative=False).write(str(ROOT/'print'/('Motor_saddle_'+side+'.stl')))
    # Fins are flat foam blades tilted inward 15 deg, mounted above each nacelle.
    finpoly=[(420,42),(480,97),(527,92),(543,42)]
    fin=extrude_xz(finpoly,cy-1.5,3)
    fin.rotate(V(0,cy,42),V(1,0,0),sign*p['fin_cant_deg'])
    add('Vertical_fin_'+side,fin,material='3 mm foam; 15 deg inward cant')
    # Two slotted external cradles set the 15-degree fin angle; bond to nacelle crown.
    for x in [474,515]:
        block=box(x,cy-4,35,4,8,10)
        slot=box(x-1,cy-1.6,41.9,6,3.2,14);slot.rotate(V(0,cy,42),V(1,0,0),sign*p['fin_cant_deg'])
        block=block.cut(slot).cut(cylinder_x(20,x-1,cy,20,6))
        add('Fin_saddle_'+side+'_'+str(x),block,'Printed','PETG')
        MeshPart.meshFromShape(Shape=block,LinearDeflection=.08,AngularDeflection=.15,Relative=False).write(str(ROOT/'print'/('Fin_saddle_'+side+'_'+str(x)+'.stl')))
    # A low belly skid provides only nominal level-ground prop clearance, not a cage.
    skidpoly=[(510,0),(550,0),(568,-8),(560,-14),(525,-14)]
    add('Belly_skid_'+side,extrude_xz(skidpoly,cy-3,6),material='laminated foam + tape wear strip')
    motor=cylinder_x(p['motor_radius_mm'],568,cy,20,p['motor_length_mm'])
    add('Motor_envelope_'+side,motor,'Equipment','EX1103 envelope; shaft/mount verify',color=(.58,.61,.65))
    add('Prop_swept_disc_'+side,cylinder_x(p['prop_diameter_mm']/2,586,cy,20,4),'Keepouts','purchased prop sweep; NEVER print this disc')
    # Stylized crossed blades only for preview; no manufacturing export.
    vis=box(586.8,cy-25.4,18.8,2.4,50.8,2.4).fuse(box(586.8,cy-1.2,-5.4,2.4,2.4,50.8))
    add('Prop_visual_'+side,vis,'Keepouts','illustrative only; actual 2023 three-blade prop differs',color=(.75,.25,.15))
    # Servo placed ahead of hinge, outboard of nacelle, with a visible pushrod.
    sy=sign*145
    add('Servo_envelope_'+side,box(465.5,sy-4.45,-1,19.8,8.9,23.1),'Equipment','EMAX ES9051 candidate envelope; surface mount and verify tabs')
    add('Pushrod_'+side,cylinder_x(.4,479,sy,13,28),'Structure','0.8 mm wire; bend ends to actual arms')
    horn=box(503,sy-1,3,5,2,12).cut(Part.makeCylinder(.5,4,V(506,sy-2,12),V(0,1,0)))
    add('Control_horn_'+side,horn,'Printed','PETG; fit to actual pushrod')
    MeshPart.meshFromShape(Shape=horn,LinearDeflection=.05,AngularDeflection=.15,Relative=False).write(str(ROOT/'print'/('Control_horn_'+side+'.stl')))

template('F06_Nacelle_wrap',[(0,0),(288,0),(288,math.pi*38*300/360),(0,math.pi*38*300/360)],'FOAM',2,qty=2,note='ROLL BLANK; neutral diameter 38; 300deg open bottom; fit/trim seam')
template('F07_Vertical_fin',finpoly,'FOAM',3,qty=2,note='NET flat fin; assembly cant 15 deg inward')
template('F08_Belly_skid',skidpoly,'FOAM',3,qty=4,note='Laminate two per side to 6mm; add wear tape')
template('F09_Spike_web',[(0,0),(77,0),(77,15),(0,15)],'FOAM',2,qty=2)
# Circles are also represented as polygon outlines; explicit true circular holes.
circle=lambda r,n=96:[(r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n)) for i in range(n)]
template('W03_Motor_firewall',circle(18),'PLY',1,qty=4,holes=[{'circle':[0,0,3]}],note='Laminate 2; NO motor bolt holes supplied: transfer verified motor pattern; center bore D6')
template('W04_Nacelle_former_BLANK',circle(18),'PLY',1,qty=6,holes=[{'circle':[0,0,16]}],note='Ring blank; trim bottom to z=3 using assembly drawing')

# Purchased hardware envelope checks and a genuinely empty future chute zone.
bx=p['battery_center_x_mm'];dx,dy,dz=p['battery_envelope_mm']
add('Battery_envelope',box(bx-dx/2,-dy/2,5,dx,dy,dz),'Equipment','2S550mAh; envelope and mass provisional',color=(.88,.56,.15))
for side,y in [('L',2),('R',-14)]:add('ESC_envelope_'+side,box(70,y,5,25,12,5),'Equipment','15A PWM no BEC; vented front bay')
add('BEC_envelope',box(285,-7,5,20,14,6),'Equipment','regulated 5V2A')
add('Receiver_envelope',box(308.5,-5.5,5,13,11,3),'Equipment','RP1 V2')
add('Gyro_envelope',box(310,-9.75,10,30,19.5,7.5),'Equipment','A3 Mini; receiver below front end with >=2mm clearance')
add('Future_chute_zone',box(373,-17,4,40,34,20),'Keepouts','SPACE ONLY; no parachute/anchor load rating')
add('Battery_adjustment_zone',box(90,-15,5,160,30,16),'Keepouts','battery center x=120..220; straps and wiring must clear full range')
add('Removable_trim_steel',box(70,-10,-5.1,20,20,5.1),'Equipment','16g steel allowance; tape-secured and adjusted after weighing')

doc.recompute()
doc.saveAs(str(ROOT/'cad'/'SR71_600_P0.FCStd'))
physical=[o for o,g in objects if g!='Keepouts']
export_named_step(ROOT/'cad'/'SR71_600_P0.step',physical)
(ROOT/'data'/'templates.json').write_text(json.dumps(templates,indent=2),encoding='utf-8')
(ROOT/'data'/'meshes.json').write_text(json.dumps(meshes,separators=(',',':')),encoding='utf-8')
records=[]
for o,g in objects:
    s=o.Shape;b=s.BoundBox
    com=V()
    for sol in s.Solids:com+=sol.CenterOfMass*sol.Volume
    if s.Volume:com=com/s.Volume
    records.append(dict(name=o.Name,group=g,valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,center_of_mass_mm=list(com),bbox=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],material=o.Material,status=o.ReleaseStatus))
    if g=='Printed':
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
        mb=mesh.BoundBox
        mat=App.Matrix();mat.A14=-mb.XMin;mat.A24=-mb.YMin;mat.A34=-mb.ZMin
        mesh.transform(mat)
        mesh.write(str(ROOT/'print'/(o.Name+'.stl')))
# Check crucial collisions, not adhesive joints; discs include swept volume.
checks=[]
byname={o.Name:o for o,g in objects}
for side in ['L','R']:
    prop=byname['Prop_swept_disc_'+side]
    for o,g in objects:
        if g in ['Foam','Structure','Printed']:
            v=prop.Shape.common(o.Shape).Volume
            checks.append(dict(pair=[prop.Name,o.Name],intersection_mm3=v,pass_check=v<.001))
for name in ['Battery_envelope','Receiver_envelope','Gyro_envelope','BEC_envelope','ESC_envelope_L','ESC_envelope_R']:
    ob=byname[name]
    for n2 in ['Fuselage_side_L','Fuselage_side_R','Fuselage_roof_frame','Battery_tray','Battery_hatch','Avionics_hatch']:
        v=ob.Shape.common(byname[n2].Shape).Volume
        checks.append(dict(pair=[name,n2],intersection_mm3=v,pass_check=v<.001))
equipment=[o for o,g in objects if g=='Equipment']
for i,ob in enumerate(equipment):
    for ob2 in equipment[i+1:]:
        v=ob.Shape.common(ob2.Shape).Volume
        checks.append(dict(pair=[ob.Name,ob2.Name],intersection_mm3=v,pass_check=v<.001))
qa=dict(parts=records,collision_checks=checks,flight_release=False,all_shapes_valid=all(r['valid'] and r['solids']>0 for r in records),critical_collisions_clear=all(c['pass_check'] for c in checks))
(ROOT/'qa'/'cad_checks.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
print('CAD_CREATED',len(objects),'objects',len(templates),'templates')
print('CHECKS',qa['all_shapes_valid'],qa['critical_collisions_clear'])
App.closeDocument(doc.Name)
