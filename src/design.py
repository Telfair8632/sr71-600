"""Shared geometry and explicit first-order engineering estimates. No flight claims."""
from pathlib import Path
import json, math, csv
ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'config'/'design.json'
def config(): return json.loads(CFG.read_text(encoding='utf-8'))
def half_outline(p):
    # Nose/chine and wing in a single 3 mm blank. Lifting reference is separate.
    s=p['wing_stations']; span=p['span_mm']/420
    return [(0,0),(70,22*span),(170,25*span),(225,45*span),(260,60*span),(285,75*span),(330,115*span),(465,p['span_mm']/2),(535,205*span),(535,130*span),(545,115*span),(545,60*span),(p['body_length_mm'],22*span)]
def full_outline(p):
    h=half_outline(p)
    return h+[(x,-y) for x,y in h[:0:-1]]
def area(poly): return abs(sum(x*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*y for i,(x,y) in enumerate(poly)))/2
def centroid(poly):
    terms=[x*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*y for i,(x,y) in enumerate(poly)]
    a=sum(terms)/2
    return tuple(sum((poly[i][k]+poly[(i+1)%len(poly)][k])*terms[i] for i in range(len(poly)))/(6*a) for k in (0,1))
def integration(p):
    # Midpoint strips converge for piecewise-linear LE/TE; all values in mm.
    strips=[]
    for a,b in zip(p['wing_stations'][:-1],p['wing_stations'][1:]):
        for i in range(1000):
            t=(i+.5)/1000; y=a[0]+t*(b[0]-a[0]); le=a[1]+t*(b[1]-a[1]); te=a[2]+t*(b[2]-a[2]); dy=(b[0]-a[0])/1000
            strips.append((y,le,te-le,dy))
    S=2*sum(c*dy for y,le,c,dy in strips)
    mac=2*sum(c*c*dy for y,le,c,dy in strips)/S
    xle=2*sum(le*c*dy for y,le,c,dy in strips)/S
    return S,mac,xle
def full_integration(p):
    # Treat complete horizontal planform as a lifting surface. Unlike wing-only
    # approximation this includes long forward chines. Still NOT a VLM/CFD solution.
    poly=full_outline(p); step=.025; count=round(p['span_mm']/2/step)
    S=C2=LC=0
    for i in range(count):
        y=(i+.5)*step;xs=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            if min(a[1],b[1])<=y<max(a[1],b[1]):
                xs.append(a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1]))
        le=min(xs);c=max(xs)-le
        S+=2*c*step;C2+=2*c*c*step;LC+=2*le*c*step
    return S,C2/S,LC/S
def bom(p):
    # qty, unit estimate mass, centroid x, budget CNY for all qty. Measurements blank.
    vals=[
      ('AIR01','3 mm unpapered foam blanks / body and wing',1,24,330,100,'estimated allowance; weigh offcuts and parts'),
      ('AIR02','2 mm foam nacelle skins and fins',1,12,425,50,'estimated allowance'),
      ('STR01','4x2 mm carbon tube transverse spar, 380 mm',1,5.73,480,50,'rho=1600 kg/m3'),
      ('STR02','2 mm carbon rods longitudinal, 2 x 215 mm',1,2.16,437.5,40,'rho=1600 kg/m3'),
      ('STR03','1 mm plywood mount rings, rails and tabs',1,8,365,100,'allowance; actual CAD solids separately listed'),
      ('PRT01','PETG saddles and local fittings',1,4,545,120,'STL volume is solid-volume upper bound; <=4g print budget'),
      ('PWR01','Happymodel EX1103 KV11000 motors',2,3.8,575.75,220,'manufacturer mass; verify mounting drawing'),
      ('PWR02','2023 two-inch CW/CCW matched prop pair',2,0.8,588,60,'estimate; exact 2023R test combination or retest'),
      ('PWR03','15 A 2S ESC, standard PWM, no BEC, <=6 g each',2,6,82.5,180,'front vented bay; 25x12x5 mm; extended PHASE leads'),
      ('PWR04','2S 550 mAh LiPo, <=32 g, >=25 A real burst',1,p['battery_nominal_g'],p['battery_center_x_mm'],180,'two packs in purchase allowance; ONE aboard'),
      ('PWR05','5 V 3 A BEC, <=5 g',1,5,295,80,'2S compatible; existing 2 A unit only after simultaneous servo stall-load test'),
      ('CTL01','RadioMaster RP1 V2 ELRS receiver',1,2.2,315,150,'manufacturer mass incl antenna'),
      ('CTL02A','Raspberry Pi Pico 2 non-wireless, no headers',1,4,325,50,'51x21 mm; VSYS from regulated 5 V; UART for receiver and I2C for IMU'),
      ('CTL02B','MPU6050 breakout with INT pin',1,3,300,40,'buy two modules; install one; 3.3 V I2C logic, DATA_RDY interrupt and actual mass must be verified'),
      ('CTL02C','SN74AHCT125, carrier, filters and signal harness',1,3,325,80,'four 3.3-to-5 V outputs; boot-disabled OE; combined carrier/filter/harness target <=3 g'),
      ('CTL03','EMAX ES9051 class 4.0-5.5 V micro servo',2,4.3,475,120,'candidate: 19.8x8.9x23.1 mm, >=0.8 kg.cm at 4.8V; verify genuine item and current'),
      ('CTL04','Pushrods, horns, tape hinges',1,4,498,40,'estimate'),
      ('ASM01','Wires, XT30, straps and heatshrink',1,10,300,100,'estimate; long phase leads required'),
      ('ASM02','Adhesive and belly skid allowance',1,10,340,100,'track cured adhesive mass; <=10g budget'),
      ('ASM03','Light finish and cockpit',1,3,210,40,'thin dark film/paint; visible tip markers'),
      ('RES01','Unallocated airborne growth allowance',1,20,340,0,'planning allowance; NOT installed component; CG uncertain'),
      ('TRIM01','Removable steel nose trim weight',1,16,80,40,'initial estimate; size by real CG; never exceed measured thrust mass gate'),
      ('GND01','RadioMaster Pocket ELRS + radio cells',1,0,0,650,'ground equipment; regional radio variant to be checked'),
      ('GND02','Balance charger and power supply',1,0,0,350,'2S balance and storage modes'),
      ('GND03','Wattmeter, scale and thrust fixture materials',1,0,0,250,'ground equipment'),
      ('GND04','Pico USB cable and soldering consumables',1,0,0,40,'ground equipment; data-capable USB cable required')]
    return [dict(id=i,item=n,qty=q,unit_mass_g=m,total_mass_g=q*m,x_mm=x,budget_cny=c,basis=b,measured_mass_g='',measured_x_mm='',purchase_status='NOT ORDERED') for i,n,q,m,x,c,b in vals]
def calculate(p):
    S,mac,xle=full_integration(p); wing_S,wing_mac,wing_xle=integration(p); rows=bom(p)
    mass=sum(r['total_mass_g'] for r in rows)
    moment=sum(r['total_mass_g']*r['x_mm'] for r in rows)
    bmass=p['battery_nominal_g']; bmom=bmass*p['battery_center_x_mm']
    cgr=[xle+f*mac for f in p['initial_cg_mac_fractions']]
    midpoint=sum(cgr)/2
    batt_req=(mass*midpoint-(moment-bmom))/bmass
    speed={str(cl):math.sqrt(2*(mass/1000)*9.80665/(p['rho_air_kg_m3']*(S/1e6)*cl)) for cl in p['clmax_sensitivity']}
    # Closed form rectangular end-loaded cantilever conservative spar check.
    L=0.190; force=mass/1000*9.80665*p['sizing_load_factor']/2
    I=math.pi/64*((.004)**4-(.002)**4); stress=force*L*.002/I; E=70e9
    return dict(revision=p['revision'],reference_area_mm2=S,reference_area_dm2=S/10000,outline_area_mm2=area(full_outline(p)),aspect_ratio=p['span_mm']**2/S,mac_mm=mac,mac_le_x_mm=xle,quarter_chord_x_mm=xle+.25*mac,wing_only_quarter_chord_x_mm=wing_xle+.25*wing_mac,initial_cg_x_mm=cgr,estimated_mass_g=mass,estimated_cg_x_mm=moment/mass,battery_x_for_cg_midpoint_mm=batt_req,battery_adjustable_cg_x_mm=[(moment-bmom+bmass*x)/mass for x in p['battery_adjustment_x_mm']],wing_loading_g_dm2=mass/(S/10000),clmax_sensitivity_speed_m_s=speed,max_manufacturer_pair_thrust_g=243.8,manufacturer_static_thrust_weight_ratio=243.8/mass,thrust_ratio_20pct_install_loss=243.8*.8/mass,manufacturer_max_pair_current_A=18.4,peak_nominal_power_W=18.4*7.4,endurance_min_sensitivity={str(a):.8*p['battery_capacity_mAh']/1000/a*60 for a in [4,6,8,18.4]},motor_out_yaw_Nm=0.1219*9.80665*p['nacelle_spacing_mm']/2000,spar_tip_load_N=force,spar_root_moment_Nm=force*L,spar_stress_MPa=stress/1e6,spar_tip_deflection_mm=force*L**3/(3*E*I)*1000,spar_modulus_assumption_GPa=70,estimated_purchase_cny=sum(r['budget_cny'] for r in rows),foam_plate_raw_mass_g=area(full_outline(p))*p['foam_thickness_mm']*p['foam_density_kg_m3']/1e6,flight_release=False)
def write_data():
    p=config(); a=calculate(p)
    (ROOT/'data'/'analysis.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8')
    for name,rows in [('bom',bom(p)),('motor_manufacturer_data',[dict(current_A=a,thrust_g=t,voltage_V=7.4,status='MANUFACTURER BENCH DATA - NOT OUR MEASUREMENT') for a,t in p['motor_test_A_thrust_g']])]:
        if name=='bom' and (ROOT/'data'/'bom.csv').exists():
            with (ROOT/'data'/'bom.csv').open(encoding='utf-8-sig',newline='') as old:
                saved={r['id']:r for r in csv.DictReader(old)}
            for row in rows:
                for key in ['measured_mass_g','measured_x_mm','purchase_status']:
                    if row['id'] in saved:row[key]=saved[row['id']].get(key,row[key])
        with (ROOT/'data'/f'{name}.csv').open('w',newline='',encoding='utf-8-sig') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return a
if __name__=='__main__': print(json.dumps(write_data(),ensure_ascii=True,indent=2))
