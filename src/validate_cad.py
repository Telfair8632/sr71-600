from pathlib import Path
import json,math,sys
import FreeCAD as App,Part,Mesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from design import config,calculate
p=config();a=calculate(p)
doc=App.openDocument(str(ROOT/'cad'/'SR71_600_P0.FCStd'))
checks=[];details={}
def check(name,ok,value=None):
    checks.append(dict(name=name,passed=bool(ok),value=value))
parts=[o for o in doc.Objects if hasattr(o,'Shape') and not o.Shape.isNull()]
check('FCStd_reopens',len(parts)>=60,len(parts))
check('all_native_shapes_valid',all(o.Shape.isValid() and len(o.Shape.Solids)>0 for o in parts))
whole=Part.makeCompound([o.Shape for o in parts])
b=whole.BoundBox
check('total_length_including_prop_envelope_le_600',b.XLength<=600+1e-6,b.XLength)
check('span_420',abs(b.YLength-420)<.01,b.YLength)
details['bounding_box_mm']=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
for base in ['Nacelle_skin','Motor_envelope','Prop_swept_disc','Elevon','Carbon_longeron','Servo_envelope']:
    l=doc.getObject(base+'_L').Shape;r=doc.getObject(base+'_R').Shape
    check(base+'_symmetric_volume',abs(l.Volume-r.Volume)<.01)
    check(base+'_symmetric_centers',abs(l.CenterOfMass.y+r.CenterOfMass.y)<.01)
native_qa=json.loads((ROOT/'qa'/'cad_checks.json').read_text())
check('critical_collision_checks',native_qa['critical_collisions_clear'],len(native_qa['collision_checks']))
check('carbon_members_do_not_interpenetrate',all(doc.getObject('Carbon_main_spar').Shape.common(doc.getObject('Carbon_longeron_'+s).Shape).Volume<.001 for s in ['L','R']))
for sign,side in [(1,'L'),(-1,'R')]:
    # Full ±18deg pitch around hinge line, not merely neutral clearance.
    for angle in [-18,0,18]:
        elev=doc.getObject('Elevon_'+side).Shape.copy()
        elev.rotate(App.Vector(495,0,0),App.Vector(0,1,0),angle)
        for fixed in ['Nacelle_skin_'+side,'Vertical_fin_'+side,'Prop_swept_disc_'+side]:
            check(f'{side}_elevon_{angle}_clear_{fixed}',elev.common(doc.getObject(fixed).Shape).Volume<.001)
# STEP import verifies exchange file rather than assuming the exporter succeeded.
stp=Part.Shape();stp.read(str(ROOT/'cad'/'SR71_600_P0.step'))
check('STEP_reimports_valid',stp.isValid() and len(stp.Solids)>0,len(stp.Solids))
check('STEP_length',stp.BoundBox.XLength<=600,stp.BoundBox.XLength)
for path in sorted((ROOT/'print').glob('*.stl')):
    mesh=Mesh.Mesh(str(path))
    check(path.name+'_closed_solid',mesh.isSolid(),mesh.CountFacets)
    check(path.name+'_origin_on_print_bed',abs(mesh.BoundBox.ZMin)<.001,mesh.BoundBox.ZMin)
printed=[r for r in native_qa['parts'] if r['group']=='Printed']
printed_mass=sum(r['volume_mm3'] for r in printed)*1.27/1000
details['printed_solid_mass_upper_bound_g_PETG_1_27']=printed_mass
check('printed_solid_volume_fits_4g_budget',printed_mass<=4,printed_mass)
# Mass-CG assertion rejects infeasible battery location; no stability assertion.
check('budget_CG_inside_provisional_window',a['initial_cg_x_mm'][0]<=a['estimated_cg_x_mm']<=a['initial_cg_x_mm'][1],a['estimated_cg_x_mm'])
check('battery_can_reach_CG_midpoint',p['battery_adjustment_x_mm'][0]<=a['battery_x_for_cg_midpoint_mm']<=p['battery_adjustment_x_mm'][1],a['battery_x_for_cg_midpoint_mm'])
check('purchase_budget_le_3500',a['estimated_purchase_cny']<=3500,a['estimated_purchase_cny'])
out=dict(checks=checks,details=details,all_digital_checks_pass=all(c['passed'] for c in checks),flight_release=False,not_tested=['actual motor mounts','real hardware dimensions','structural loads','installed thrust','thermal','radio fail-safe','glide stability','flight'])
(ROOT/'qa'/'validation.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
App.closeDocument(doc.Name)
print(json.dumps(out,ensure_ascii=True,indent=2))
if not out['all_digital_checks_pass']:sys.exit(1)
