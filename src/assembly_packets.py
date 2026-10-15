"""Generate standalone procurement and assembly PDFs plus editable Markdown."""
from pathlib import Path
import sys,html,json
ROOT=Path(__file__).resolve().parents[1]
_pyd=ROOT.parent/'tools'/'pydeps'
if _pyd.exists():sys.path.insert(0,str(_pyd))
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image,KeepTogether
from design import config,calculate
p=config();a=calculate(p)
NAVY=colors.HexColor('#163448');TEAL=colors.HexColor('#087d91');LIGHT=colors.HexColor('#e4eef2');GRAY=colors.HexColor('#607987');ORANGE=colors.HexColor('#d97524')
S={
'title':ParagraphStyle('title',fontName='Helvetica',fontSize=22,leading=29,textColor=NAVY,spaceAfter=14),
'h1':ParagraphStyle('h1',fontName='Helvetica',fontSize=14,leading=20,textColor=TEAL,spaceBefore=10,spaceAfter=7),
'h2':ParagraphStyle('h2',fontName='Helvetica',fontSize=11,leading=16,textColor=NAVY,spaceBefore=6,spaceAfter=4),
'p':ParagraphStyle('p',fontName='Helvetica',fontSize=9.7,leading=16,textColor=NAVY,spaceAfter=7),
'small':ParagraphStyle('small',fontName='Helvetica',fontSize=7.8,leading=11,textColor=GRAY),
'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=7.5,leading=10.5,textColor=NAVY),
'check':ParagraphStyle('check',fontName='Helvetica',fontSize=9.2,leading=15,textColor=NAVY,leftIndent=3*mm,firstLineIndent=-3*mm,spaceAfter=4)}
def P(t,s='p'):return Paragraph(html.escape(str(t)).replace('\n','<br/>'),S[s])
def H(t,level=1):return P(t,'h1' if level==1 else 'h2')
def check(t):return P('[ ] '+t,'check')
def table(rows,widths):
    t=Table([[P(x,'cell') for x in r] for r in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('TEXTCOLOR',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#c4d4dc')),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));return t
def footer(label):
    def f(c,d):
        c.saveState();c.setStrokeColor(colors.HexColor('#c5d4dc'));c.line(18*mm,17*mm,192*mm,17*mm);c.setFont('Helvetica',8);c.setFillColor(GRAY);c.drawString(18*mm,12*mm,'SR71 / 600 · V1.0-P0-E2 · '+label);c.drawRightString(192*mm,12*mm,str(d.page));c.restoreState()
    return f
def write_doc(path,flow,title,label):
    SimpleDocTemplate(str(path),pagesize=A4,leftMargin=17*mm,rightMargin=17*mm,topMargin=16*mm,bottomMargin=22*mm,title=title).build(flow,onFirstPage=footer(label),onLaterPages=footer(label))
def md_table(rows):
    return '\n'.join(['| '+' | '.join(rows[0])+' |','|'+'|'.join(['---']*len(rows[0]))+'|']+['| '+' | '.join(r)+' |' for r in rows[1:]])

# Procurement list
locked=[
['ID','Qty to buy','Item / search term','Acceptance criteria on arrival','Max onboard mass','Budget cap'],
['P01','3 pcs','Happymodel EX1103 KV11000','2S; 1.5 mm shaft; approx. 13.5 x 15.5 mm; max 4.0 g each; one unit as spare','8.0 g (2 installed)','CNY 330'],
['P02','3 sets','2023R/2023 2-inch CW/CCW prop pairs, 1.5 mm bore','Each set contains CW + CCW; confirm a press fit that does not slip before use; never let glue reach the bearing','<=2.0 g','CNY 90'],
['P03','2 packs','2S 550mAh LiPo, XT30','Max 32 g each; max 60 x 30 x 16 mm; same batch; measure voltage sag; only one pack installed at a time','32 g','CNY 180'],
['P04','1 unit + 2 cells','RadioMaster Pocket ELRS 2.4GHz + 2 x 18650 cells','Confirm the ELRS version; transmitter packaging usually excludes cells; use qualified same-batch 18650 cells','Ground equipment','CNY 650'],
['P05','1 pc','RadioMaster RP1 V2 2.4GHz ELRS','5V, CRSF, max 2.2 g with antenna; verify the UFL antenna is intact','2.2 g','CNY 150'],
['P07','3 pcs','EMAX ES9051 micro digital servos','4.0-5.5 V; max 4.3 g each; approx. 19.8 x 8.9 x 23.1 mm; torque >= 0.8 kg·cm at 4.8 V','8.6 g (2 installed)','CNY 150'],
['P08','1 pc','5V 3A standalone BEC','2S-capable input; max 5 g; must drive the control board and both servos without rebooting; output <= 5.25V','5.0 g','CNY 80']]
flight_control=[
['ID','Qty to buy','Item / search term','Acceptance criteria on arrival','Max onboard mass','Budget cap'],
['P06A','1 board','Raspberry Pi Pico 2, no wireless, no pin headers','Genuine or fully pin-compatible; 51 x 21 mm; UART, I2C and PWM available; board mass <= 4 g','4.0 g','CNY 50'],
['P06B','2 boards','MPU6050 six-axis module with INT pin','Install 1, keep 1 for cross-check/spare; 400kHz I2C; SDA/SCL idle-high level <= 3.3V; max 3 g each','3.0 g (1 installed)','CNY 40'],
['P06C','2 chips','SN74AHCT125N, DIP-14','Must be AHCT125, not HC125; 4 channels; install 1, spare 1','Counted in the 3 g total below','CNY 20'],
['P06D','1 set','Low-ESR capacitors, X7R capacitors and resistors','470uF/10V low-ESR x2; 10uF/25V X7R x5; 0.1uF/100V ceramic x10; 10k ohm x10; 4.7k ohm x10','Counted in the 3 g total below','CNY 30'],
['P06E','2 boards + 1 set','Lightweight perfboard, pin headers/plugs, 26-30AWG signal wire','One board for the aircraft, one for practice/spare; no loose Dupont jumpers in the build; P06A-E target <= 10 g','<= 3.0 g (C-E total)','CNY 30']]
conditional=[
['ID','Qty to buy','Item / spec','Purchase condition','Budget cap'],
['C01','2 pcs','Brushless ESC: 2S, conventional 50Hz PWM, >= 12A continuous each, <= 6 g, <= 25 x 12 x 5 mm','Seller must confirm in writing that conventional receiver PWM works; do not buy DShot-only ESCs; BEC-less preferred','CNY 180'],
['C02','1 set','UHU POR-type foam-safe glue + 30-minute slow-set epoxy','Run corrosion/peel test coupons on same-batch foam first; epoxy only at local spots such as carbon rods and firewalls','CNY 100'],
['C03','1 set','Motor mounting screws/washers','After motors arrive, measure hole spacing, thread type and safe length; screws must not touch the windings','CNY 40'],
['C04','1 set','Phase wires, silicone wire, heat-shrink, XT30, signal wire','Select for the twin 18.4A peak sensitivity; extend phase wires, keep battery DC leads short','CNY 100'],
['C05','As needed','5V to 3.3V unidirectional level shifter','Buy only if the measured RP1 TX high level is > 3.6V; the part must handle the CRSF serial baud rate','CNY 30']]
materials=[
['ID','Qty','Material / size','Use and requirements','Budget'],
['M01','2 sheets','3 mm MPP/Depron-type paperless light foam, each sheet >= 650 x 450 mm','Wing/chines, central fuselage, elevons; weigh a 100 x 100 mm sample first, target density about 35-45 kg/m³','CNY 100'],
['M02','1 sheet','2 mm same-type paperless light foam, >= 650 x 400 mm','Roll skins for both nacelles, intake spike webs and finish parts; do not buy 10 mm XPS and split it yourself','CNY 50'],
['M03','1 sheet','1 mm aircraft plywood, >= 300 x 300 mm','Battery tray, bulkheads, nacelle formers, firewall lamination','CNY 100'],
['M04','1 tube','Carbon tube OD4/ID2, >= 500 mm','Cut the 380 mm transverse main spar; must be straight and crack-free','CNY 50'],
['M05','2 rods','OD2 solid carbon rod, >= 300 mm each','Cut a 215 mm longeron from each; a solid rod has no inner diameter','CNY 40'],
['M06','approx. 50 g','PETG 1.75mm','8 printed parts; finished total mass <= 4 g; print one side as a sample first','CNY 60'],
['M07','1 set','0.8 mm steel wire, micro control horns, tape hinges','Left/right pushrods, control horns, elevon hinges','CNY 40'],
['M08','1 set','Hook-and-loop straps, anti-slip pad, belly wear tape, removable steel plates','Dual battery retention; steel plates for CG adjustment, budget at most 16 g','CNY 80']]
tools=[
['Tool','Minimum capability','Notes'],
['0.01 g scale','Range >= 300 g','Weigh parts and the complete aircraft; a kitchen scale is unsuitable for 4 g parts'],
['Power meter / ammeter','2S, >= 30 A','Record voltage, current and voltage sag'],
['Thrust stand','Range >= 500 gf, with prop guard','Can be homemade, but the motor and scale must be rigidly fixed'],
['Multimeter','DC voltage, continuity','Verify the 5V rail and polarity'],
['Balance charger','2S capable, balance/storage modes','Do not use simple USB charge leads without balance management'],
['Square / calipers / angle gauge','0.1 mm class calipers','Verify hole spacing, axes, 15° fin cant and 3° initial elevon reflex'],
['Low-wattage iron / hot air or lighter','Suitable for fine-wire soldering','Provide strain relief at joints; keep heat away from foam when shrinking'],
['Adjustable current-limited PSU','0-12 V, >= 3 A','Current-limit the control board at first power-up to avoid cascading damage from wiring errors'],
['USB logic analyzer','>= 8 channels, >= 24 MHz','Check I2C, CRSF serial, PWM and control loop timing'],
['Goggles and prop guard','Covers test personnel','Nobody stands in the prop disc plane during powered bench tests']]
notnow=[
'2.5-inch propellers: they change current draw and prop-disc clearance; re-match only if the 2-inch setup measures insufficient.',
'Parachute, release servo and shroud lines: only a space reservation exists so far, with no deployment-load or altitude validation.',
'Landing gear, video link, autopilot equipment and decorative lights: they consume mass and CG margin.',
'Whole-airframe 3D-print material: this design is foam-based; a fully printed shell would break the mass budget.',
'Final motor hole template: transfer it only after the actual motors arrive; the current W03 is a blank.']
compatibility=[
['Original equipment / interface','New-plan correspondence','Check conclusion'],
['P04 Pocket ELRS -> P05 RP1','ELRS radio link unchanged','Match'],
['P05 RP1, 5V/CRSF','RP1 TX -> Pico UART0 RX; common ground','Protocol match; direct wiring only after the TX high level measures <= 3.6V'],
['P06B MPU6050','SDA->GP4, SCL->GP5, INT->GP3; I2C 400kHz','Function match; Pico timestamps on DATA_RDY and runs its own attitude fusion'],
['P06A Pico 2','UART0 to RP1; I2C0 to MPU6050; 4 PWM channels to AHCT125','Sufficient resources'],
['P07 ES9051, two units','AHCT125 5V PWM -> left/right servos','Voltage match; start at 50Hz; loaded test mandatory'],
['C01 two conventional PWM ESCs','AHCT125 5V PWM -> left/right ESCs','Match; DShot-only ESCs do not match'],
['P08 BEC','5V/3A -> RP1, Pico VSYS, AHCT125 and servos','Match; an existing 2A version must pass the simultaneous load test'],
['Front-bay installation space','Pico 51 x 21 mm, MPU6050 module per actual size, stacked installation X approx. 295-351','Original A3 envelope void; dry-fit assembly before cutting the tray'],
['Mass / CG',f"Planned mass {a['estimated_mass_g']:.1f} g, CG X={a['estimated_cg_x_mm']:.1f} mm; CG stays inside the window with the battery at X=120",'10 g control-stack target is feasible; recompute after weighing'],
['Thrust margin',f"Manufacturer peak static thrust-to-weight ratio about {a['manufacturer_static_thrust_weight_ratio']:.2f}; about {a['thrust_ratio_20pct_install_loss']:.2f} assuming 20% installation loss",'Margin is thin; no powered flight if the measured installed static thrust-to-weight ratio is < 1.2']]
f=[];f+=[P('SR-71 / 600 Procurement List','title'),P('For the V1.0-P0 small demonstrator. P06 uses the self-built Pico 2 + MPU6050 controller; IM600, IM900, IWT603 and HobbyEagle are not purchased. Accept the power and control sample units first, then close up the airframe. Current budget figures are not vendor quotes.')]
f+=[H('A. Retained locked-in parts'),table(locked,[12*mm,14*mm,38*mm,72*mm,20*mm,18*mm]),Spacer(1,4*mm),P('P01/P02 must be power-tested as one matched set; install two P07 units and keep the third as a spare. P08 is raised to 3A; retain an existing 2A BEC only if it holds voltage without reboot while simultaneously driving both servos and the control board.','small'),PageBreak()]
f+=[H('B. P06 self-built flight-control replacement parts'),table(flight_control,[12*mm,15*mm,42*mm,68*mm,20*mm,18*mm]),Spacer(1,4*mm),P('The MPU6050 supplies raw six-axis data; the Pico handles timestamping, calibration, attitude fusion and PID. The onboard target for P06A-E is <= 10 g; if exceeded, pause close-out and recompute the center of gravity and thrust-to-weight ratio.','small'),PageBreak()]
f+=[H('C. Purchase after interface confirmation'),table(conditional,[12*mm,15*mm,50*mm,78*mm,24*mm]),Spacer(1,5*mm),P('Both ESCs use conventional PWM input. Only 3.3V pull-ups are permitted on MPU6050 SDA/SCL; measure the RP1 TX high level before wiring it into the Pico. If an ESC carries a BEC, isolate its red wire; the control bus is powered only by the standalone BEC.'),H('D. Airframe and structural materials'),table(materials,[12*mm,14*mm,48*mm,82*mm,22*mm]),PageBreak()]
f+=[H('E. Tools and ground equipment'),table(tools,[38*mm,49*mm,89*mm]),Spacer(1,5*mm),H('F. Not purchased for now')]
for x in notnow:f.append(check(x))
f+=[H('G. Incoming acceptance checklist')]
for x in ['Weigh every item and enter measured values into data/bom.csv; never substitute vendor nominal masses.','Measure motor diameter, length, shaft diameter, hole spacing, thread and usable screw length with calipers.','Confirm CW/CCW prop bore, thrust direction and press-fit security; check rotation direction powered, without props installed.','Measure each battery pack for dimensions, mass, rest voltage and internal resistance/voltage sag; retire it immediately on swelling, damaged wrapper or an abnormal cell.','With the BEC feeding the control board and both servos, run simultaneous rapid-motion/light-load tests; the 5V bus must not sag or reboot.','Bench-verify each ESC individually for PWM, throttle calibration, temperature rise and protection before pairing them into the twin installation.','Repeatedly flash and power-cycle the Pico over USB; connect the RP1 to UART0 and the MPU6050 to I2C0 and INT, and log continuously for 10 minutes without dropped samples.','Measure the SDA/SCL idle-high levels and the RP1 TX high level; Pico GPIO must never directly withstand more than 3.6V.']:f.append(check(x))
f+=[PageBreak(),H('H. Compatibility review against original equipment'),table(compatibility,[43*mm,79*mm,54*mm]),Spacer(1,4*mm),P(f"Budget: the current project table totals about CNY {a['estimated_purchase_cny']}, which is CNY {max(0,a['estimated_purchase_cny']-3500)} above the 3500 first-round target; still below the 5000 overall cap, with about CNY {5000-a['estimated_purchase_cny']} of headroom. Prices vary by channel; passing the specification and mass checks takes priority.",'small'),H('Specification references')]
for x in ['Happymodel EX1103 KV11000: https://www.happymodel.cn/index.php/2022/09/05/bassline-spare-part-ex1103-kv11000-brushless-motor/','RadioMaster RP1 V2: https://www.radiomasterrc.com/products/rp1-expresslrs-2-4ghz-nano-receiver','Raspberry Pi Pico 2: https://www.raspberrypi.com/products/raspberry-pi-pico-2/','MPU6050 official datasheet: https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet.pdf','TI SN74AHCT125: https://www.ti.com/product/SN74AHCT125','EMAX ES9051: https://shop.emax-usa.com/products/emx-sv-0272-es9051']:f.append(P(x,'small'))
write_doc(ROOT/'docs'/'procurement_list.pdf',f,'SR-71 600 Procurement List','Procurement List')

md=['# SR-71 / 600 Procurement List','','Version V1.0-P0-E2. P06 uses the self-built Pico 2 + MPU6050 controller; the budget is a procurement control value, not a vendor quote.', '', '## A. Retained locked-in parts','',md_table(locked),'','## B. P06 self-built flight-control replacement parts','',md_table(flight_control),'','## C. Purchase after interface confirmation','',md_table(conditional),'','## D. Airframe and structural materials','',md_table(materials),'','## E. Tools and ground equipment','',md_table(tools),'','## F. Not purchased for now','']+['- [ ] '+x for x in notnow]+['','## G. Compatibility review against original equipment','',md_table(compatibility),'',f"The current project budget is about CNY {a['estimated_purchase_cny']}, below the 3500 first-round target and the 5000 overall cap."]
(ROOT/'docs'/'procurement_list.md').write_text('\n'.join(md),encoding='utf-8')

# Assembly instructions
stages=[
('0. Freeze physical interfaces before starting work',[
'Print the assembly dimension drawing and the wing template 100 mm check ruler; both horizontal and vertical measurement error must stay within 0.5 mm; set the printer to 100% and disable "fit to page".',
'Weigh and measure the motors, servos, battery, ESCs, BEC, receiver, Pico, MPU6050 and buffer board piece by piece; update bom.csv.',
'Transfer the motor hole pattern from the actual hardware onto the W03 blank; confirm the screws will not touch the windings. Adjust the servo pocket slots to the actual servo mounting lugs.',
'If the predicted takeoff mass exceeds 220 g, or the full 16 g of ballast still cannot bring the CG inside 292.2-298.6 mm, pause final close-out of the airframe.']),
('1. Produce material and load-path samples',[
'Cut and weigh a 100 x 100 mm foam sample to confirm the material is close to the design density; make corrosion and peel coupons with the chosen glue.',
'From the STLs, print one motor saddle and one fin saddle first; weigh them and test-fit the 2 mm carbon rod and the motor firewall.',
'Make a main-spar-to-foam bond sample and a motor-saddle-to-longeron sample. Load in steps, recording load, deflection and residual set after unloading; on any crack, debond or permanent deformation, redesign and redo.',
'Complete one motor/prop/ESC/battery set test on a guarded bench, then check how well the two sets match.']),
('2. Cut the wing and foam parts',[
'Cut the integral wing/chine from F01_Wing_chine_NET; cut the left/right F02 elevons, F03 fuselage sides, F04 roof frame, both F05 hatches and the F07 vertical fins.',
'Keep the wing perfectly flat and mark the X=0 nose datum, the X=292.2-298.6 CG window, the X=480 main spar and the Y=±95 longerons.',
'Cut shallow grooves on the SCORE lines: transverse tube center Z=4, above the wing plate; longeron center Z=1, below the wing plate. The two are tangent; do not drill through one another.',
'Round the leading edges and keep them symmetric left/right; no heavy paint finish yet.']),
('3. Install the carbon-fiber load structure',[
'Place the 380 mm main spar at X=480, spanning Y=-190 to 190; check that it is parallel to the trailing edge with equal length on both sides.',
'Place both 215 mm longerons at X=330-545, Y=±95; offset them above/below the main spar without crushing or cutting the carbon fibers.',
'After bonding, bridge the grooves with light tape to seal them and keep the wing plate flat while curing. Remove the weight boards only after full cure.',
'Check tip height difference, twist and bond voids; do not continue with nacelle installation if out of tolerance.']),
('4. Assemble the central fuselage and front bay',[
'Bond battery tray W01 and bulkheads W02; install both side walls and the roof frame starting at X=70, keeping both hatches removable for now.',
'Both ESCs sit in the front bay at X=70-95; the battery center can move between X=120-220; BEC center about X=295, RP1 about X=315; the Pico lies lengthwise at X approx. 300-351, with the MPU6050 as close as possible to X approx. 295 on the airframe centerline, fixed on a separate layer from the Pico.',
'Cut ventilation openings per the actual hardware; retain the battery with straps plus an anti-slip pad; a hatch must not be the sole retention.',
'Temporarily place the nose steel ballast at X approx. 80 without bonding it permanently; the final amount follows the measured center of gravity.']),
('5. Install nacelles, fins and motor mounts',[
'Roll each F06 skin to a 300° open-bottom shell on a 38 mm neutral-layer diameter, seat it on the three W04 formers, and trim the bottom to fit the wing plate.',
'Tie each intake spike to the main wing with a 77 x 15 mm foam web; it must not cantilever; keep a service seam in each nacelle skin.',
'Bond each motor saddle over the longeron and to the wing plate; laminate two W03 firewalls, drill them per the measured hole pattern, and install at X=566-568.',
'Both motor axes at Y=±95, Z=20 and parallel to each other; prop discs at X=586-590. Verify each axis with a straightedge from both the front and the rear.',
'Set each vertical fin to 15° inward cant using the fin saddles, mirrored left/right; check that fins and elevons reach the ±18° full travel without touching the prop discs.']),
('6. Install elevons and servos',[
'Connect the left and right elevons with tape hinges, keeping a gap of about 0.7 mm; the surfaces must reach ±18° freely without binding.',
'Surface-mount both ES9051 candidate servos at X approx. 465.5, Y=±145; center them mechanically first, then fit the output arms.',
'Bend the 0.8 mm wire pushrods to match the actual arms; the straight rods in CAD only indicate the connection, not the final bend geometry.',
'Set both trailing edges to 3° reflex at neutral; initial pitch ±10°, roll ±8°, with total travel limited to ±18° after mixing.']),
('7. Wiring and radio setup',[
'Power: the 2S battery splits through XT30 to both ESCs; the ESC phase wires run aft to the motors. When extending phase wires, secure every run and re-check commutation, temperature rise and interference.',
'Control power: 2S also feeds a standalone 5V switching UBEC/BEC (>= 3A continuous, 5A preferred); 5V powers the RP1, Pico VSYS, SN74AHCT125 and both servos. Choose an MPU6050 module that runs from a 3.3V supply; SDA/SCL must be pulled up to 3.3V; all signals share ground. If an ESC carries a BEC, isolate its red wire.',
'Inputs: RP1 TX to Pico UART0 RX (GP1 recommended); MPU6050 SDA to GP4, SCL to GP5, INT to GP3. Set I2C to 400kHz; the Pico records timestamps after DATA_RDY triggers.',
'Outputs: Pico GP6/GP7/GP8/GP9 each become 5V PWM through the SN74AHCT125, feeding the left servo, right servo, left ESC and right ESC. The four OE pins are tied together as OE_N with a 10k pull-up to 5V; Pico GP2 drives an NPN transistor through 4.7k to pull OE_N low before outputs are enabled. Outputs turn off automatically on reset or power loss.',
'AHCT125 DIP pinout: pin 14 to 5V, pin 7 to GND, 0.1uF next to pins 14 and 7; GP6 -> pin 2/pin 3 output, GP7 -> pin 5/pin 6 output, GP8 -> pin 9/pin 8 output, GP9 -> pin 12/pin 11 output; pins 1/4/10/13 are OE. Each of the four outputs on pins 3/6/8/11 gets a 10k pull-down to GND.',
'Place a 470uF/10V low-ESR plus 0.1uF in parallel at the 5V control bus entry; 10uF plus 0.1uF at the MPU6050 supply entry. If the module lacks 3.3V I2C pull-ups, pull SDA/SCL up to 3.3V with 4.7k ohm each.',
'Turn off delta mixing in the transmitter. CH1 roll, CH2 pitch, CH3 throttle, CH5 arm flag, CH6 mode; set the modes to OFF/NORMAL/NORMAL initially.',
'Set a physical-switch throttle lockout and arm only at low throttle; at equipment power-up keep throttle at minimum and hold the airframe still, waiting for IMU bias calibration and the controller self-check.']),
('8. Pre-close-out checks and center of gravity adjustment',[
'Remove the propellers and check control-surface directions: pulling the pitch stick raises both trailing edges; rolling right raises the right and drops the left trailing edge.',
'Check the self-built controller feedback polarity: raising the nose must command a nose-down correction; depressing the right wing must command a left-roll correction. If either is reversed, do not install props.',
'Cycle both servos rapidly back and forth under a controlled light load; the 5V bus must not sag, reboot or jitter.',
'Weigh the complete aircraft three times with all hatches, canopy, battery and harnesses installed. Move the battery and removable ballast so Xcg enters 292.2-298.6 mm; also check lateral balance.',
'Proceed to unpowered glide only if the measured installed total static thrust (gf) >= actual takeoff mass (g), the left/right thrust difference at equal throttle is <= 5%, and the temperature/current checks pass.']),
('9. Lost link, range and glide gate',[
'Still prop-less, test each case separately: transmitter off, receiver serial unplugged, receiver power removed. In every case both motors must stop, and they must not restart with throttle when the link is restored.',
'Complete the range check per the radio equipment manual and compare link and servo behavior with power off and on.',
'Have a pilot with fixed-wing experience perform a low-energy unpowered glide at full flying mass first; return to adjustment if the CG or trim tendency is unclear.',
'Powered takeoff does not use a live rear-prop hand launch. Validate the launch cradle, release attitude and field operating procedure separately first.',
'The field must be permitted and cleared of people, with airspace and applicable local requirements confirmed; no powered flight test before confirmation.'])
]
g=[P('SR-71 / 600 Assembly Instructions','title'),P('Applies to the V1.0-P0-E2 built-up airframe. P06 uses the self-built Pico 2 + MPU6050 controller. Work in the order: samples -> load structure -> dry-fit assembly -> electrical -> CG -> tests. Stop at the current stage whenever any check fails.'),Image(str(ROOT/'docs'/'cutaway.png'),width=176*mm,height=108*mm),Spacer(1,3*mm)]
g+=[table([['Key datum','Value'],['Overall envelope','590 mm; 600 mm limit'],['Wingspan','420 mm'],['Powerplant axes','Y=±95, Z=20, 190 mm axis spacing'],['Preliminary CG','X=292.2-298.6 from the nose'],['Planned mass',f"About {a['estimated_mass_g']:.1f} g; keep <= 220 g before close-out"],['Prop discs','diameter 50.8; X=586-590'],['Main spar / longerons','spar X=480, Z=4; longerons X=330-545, Y=±95, Z=1']],[48*mm,128*mm]),PageBreak()]
for idx,(title,items) in enumerate(stages):
    if idx in [2,5,7]:g.append(PageBreak())
    g.append(H(title))
    for item in items:g.append(check(item))
    g.append(Spacer(1,2*mm))
g+=[PageBreak(),H('Wiring summary'),table([['Endpoint','Connection'],['2S battery','XT30 harness -> left/right ESC power inputs; also -> standalone 5V UBEC/BEC (>= 3A continuous, 5A preferred)'],['UBEC 5V','-> Pico VSYS, RP1, AHCT125, both servos; all devices share ground'],['RP1','TX -> SN74LVC1G17 -> Pico GP1/UART0 RX; Pico GP0 through 1k -> RP1 RX; 5V/GND'],['MPU6050','choose a module that accepts a 3.3V supply; SDA->GP4, SCL->GP5, INT->GP3; I2C pulled up to 3.3V; common ground'],['Pico GP6/GP7','-> AHCT125 -> left/right elevon servos'],['Pico GP8/GP9','-> AHCT125 -> left/right ESC PWM; ESC BEC red wire isolated'],['AHCT125 OE','four channels tied into OE_N, 10k pull-up to 5V; Pico GP2 drives the NPN through 4.7k to pull OE_N low before outputs enable'],['Motors','contra-rotating on the two sides; CW and CCW props both produce forward thrust']],[36*mm,140*mm]),Spacer(1,5*mm),H('Records required before completion')]
for x in ['Actual part masses and positions: data/bom.csv','Thrust, current, temperature rise, lost link, structural loading, glide and three flights: data/test_records.csv','Motor hole pattern, servo pocket and other physical-fit changes: edit the CAD source files and rebuild all drawings','Current electronic master drawing: docs/assembly_dimensions.pdf; 1:1 paper templates: docs/cutting_templates_1to1.pdf']:g.append(check(x))
g+=[P('These instructions cover airframe assembly and ground verification; they do not constitute approval to fly. The first powered flight is to be performed by personnel with fixed-wing experience.','small')]
write_doc(ROOT/'docs'/'assembly_instructions.pdf',g,'SR-71 600 Assembly Instructions','Assembly Instructions')
imd=['# SR-71 / 600 Assembly Instructions','','Applies to the V1.0-P0-E2 built-up airframe. P06 uses the self-built Pico 2 + MPU6050 controller; all coordinates start at the nose X=0.','']
for title,items in stages:
    imd+=['## '+title,'']+['- [ ] '+x for x in items]+['']
(ROOT/'docs'/'assembly_instructions.md').write_text('\n'.join(imd),encoding='utf-8')
print('Dedicated procurement and assembly documents created')
