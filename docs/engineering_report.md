# SR71 / 600 Engineering Report and Assembly Manual

## 01 / Project Conclusions and Version Status

Objective: complete a Blackbird-profile twin-propeller prototype with an overall length of no more than 600 mm, and consider the 1,400 mm large version only after the design, manufacture, and controlled flight have been verified. This delivery is the P0 digital trial-production package; it does not constitute a built aircraft or a verified flyer.

The model envelope is 590 mm long with a 420 mm wingspan; the fuselage length is 570 mm; the twin powerplant axes are 190 mm apart; the propeller diameter is 50.8 mm. Including the axial overhang of the motors and propellers, the complete aircraft still remains below 600 mm.

The current mass budget is 197.9 g, which includes a 20 g unallocated growth allowance and 16 g of removable nose ballast. The first-round procurement allowance is 3230 CNY, with 1770 CNY reserved for rework. These amounts are planning allowances, not current vendor quotations.

The overall concept has a feasible basis, but the mass and thrust margins of the twin 2-inch powerplants are narrow. Structural specimens must be fabricated and the propulsion tested first; the design must not proceed directly to batch machining on this basis, and the manufacturer's peak bench thrust must not be treated as sustainable thrust.

Digital modeling, calculations, and file generation are complete; mass, thrust, temperature rise, load capacity, radio range, field availability, and flight all still require physical verification. Estimates, manufacturer data, and measured records in this report are managed as separate categories.

## 02 / Geometry, Materials, and File Interfaces

Coordinate system: nose tip at X=0, with X increasing toward the tail; Y>0 is the aircraft left side (as viewed by the pilot facing the nose); Z is up. Units are mm. The nacelle axes are at Y=±95, Z=20; the motor mounting face is at X=568, with the axial envelope ending at 583.5; the propeller discs span X=586–590.

The main wing and chines are cut as one piece from 3 mm paperless foam board; the airfoil is a flat plate with a rounded leading edge. The control surfaces are cut separately, with a 0.7 mm hinge gap. No low-Reynolds-number airfoil optimization was performed for this version. The central fuselage comprises 3 mm side walls, a top frame, and a maintenance hatch; the nose tip, tail, and canopy are carved from lightweight foam.

Each nacelle is a 2 mm foam skin rolled into a 300° open-bottom shell with a nominal outside diameter of 40, trimmed to match the wing panel at the bottom. The intake cones are appearance features only and do not replicate supersonic intake function. The twin vertical tails are canted 15° inward, and there is no rudder.

The main spar is an OD 4 / ID 2 carbon tube, 380 long, centered at X=480, Z=4. The two longitudinal rods are OD 2, 215 long, at X=330–545, Y=±95, Z=1. The main spar and the rods are offset vertically from one another so that neither is pierced and the cross sections are not weakened.

The printed parts are PETG motor mounts, vertical-tail alignment jigs, and control horns, with the total mass held within 4 g. The parachute bay is only a candidate space reserved at X=373–413; this version includes no parachute, deployment actuator, or verified structural anchor points.

config/design.json is the parameter entry point; src/build_cad.py rebuilds the FreeCAD project, STEP, and STL files. The FCStd file contains grouped solids and a parameter table. That table is a parameter inventory and does not claim that every solid is driven by the table in real time; when stations or proportions are changed, the modeling script must be updated accordingly and rebuilt for checking.

Equipment is represented by installation envelopes, and the propellers are swept/schematic shapes; no STL for self-made propeller blades is provided. The motor bolt pattern lacks a physical basis; the firewall carries only a center hole and blank stock, and the hole positions must be transferred from the actual hardware.

## 03 / Mass, Aerodynamics, and Center of Gravity

The complete horizontal projected reference area is 10.312 dm², including the fuselage chines and neglecting small hinge gaps and small holes. The aspect ratio is 1.711. The mean aerodynamic chord is MAC=316.57 mm, with a weighted leading-edge position of X=235.27 mm.

Area and chord are obtained by spanwise integration: S is twice the integral of the local chord c over the semispan, MAC is twice the integral of c² divided by S, and XLE is twice the chord-weighted integral of the local leading-edge position divided by S. The script integrates in small spanwise strips and is reproducible. The mass center of gravity uses Xcg = sum(mi·xi)/sum(mi); the BOM retains blank columns for measured masses and positions.

The preliminary CG window is X=292.2–298.6 mm, corresponding to 18%–20% of the MAC of the complete projection. Under the current budget the CG is X=296.39 mm; the battery center adjustment range is X=120–220, and the position required to reach the window midpoint is approximately X=119.0.

The quarter-chord proxy lies at X=314.4 mm; considering only the aft main wing would give approximately 363.3 mm, a marked difference. The Blackbird's long chines must not be ignored. The current method is not a VLM, CFD, wind-tunnel, or stability proof; Cm-alpha, trim moments, and vortex lift were not solved.

Relative to the 25%-chord proxy, the current window sits 5%–7% MAC further forward; if the true neutral point moves to 20% MAC, the margin approaches zero. The CG stated above may therefore be used only for low-energy glide testing and must not by itself clear the first flight. A stabilizer cannot remedy an incorrect center of gravity.

The wing loading is 19.19 g/dm². Under the sensitivity assumptions CLmax=0.6/0.8/1.0, Vs=7.16/6.20/5.54 m/s, using Vs=sqrt(2mg/(rho·S·CLmax)) with rho=1.225 kg/m³. These are not measured stall speeds and are not a launch-speed directive.

With the actual battery, propellers, and hatches installed, measure the center of gravity three times using two-point support reactions. Move the battery first, then adjust the removable steel ballast; installing the full 16 g is not mandatory. The assumed position of the 20 g allowance is hypothetical; parts actually added must be re-entered in the moment calculation.

## 04 / Propulsion and Battery Matching

Propulsion baseline: two Happymodel EX1103 KV11000 brushless motors paired with the 2023R 2-inch series propeller pair (normal and reverse rotation) used in the manufacturer's test. S2 gives the bench point of 7.4 V, 9.2 A, and 121.9 gf per motor; 243.8 gf and 18.4 A for the pair. The manufacturer's page does not state how long that point can be sustained.

Assuming a 20% installation loss, the total thrust is approximately 195.0 gf, giving a thrust-to-weight ratio of about 0.99 against the current mass budget. The 20% figure is only a sensitivity scenario, not a measurement. If the measured installed thrust is insufficient, a value below 250 g shall not be treated as a pass condition.

The battery candidate is a 2S 550 mAh pack with an envelope of no more than 60×30×16 mm, a mass of no more than 32 g, and an XT30 connector. Demonstrated short-duration current delivery of at least 25 A is the procurement screening criterion; the C rating cannot replace voltage-sag, temperature-rise, and capacity tests.

The two ESCs are each rated 15 A and 2S, support conventional 50 Hz PWM, have no BEC, weigh no more than 6 g, and measure no more than 25×12×5 mm. DShot-only ESCs cannot be connected directly to the A3 Mini. Power the control equipment from a separate 5 V/2 A BEC.

The normal and reverse propellers must both produce forward thrust, with the two motors turning in opposite directions. Verify the thrust direction on the bench; do not judge from labels alone. After any change of pitch, blade count, diameter, or voltage, earlier manufacturer data no longer applies; the 2.5-inch propeller is not a verification-free upgrade.

First remove the propellers and check arming and lost-link (failsafe) behavior, then secure the powerplants to a guarded bench stand and record throttle, voltage, current, thrust, temperature, and duration in steps. Record RPM as well if a tachometer is available. Observe peaks with short pulses; verify sustained operating points against the component ratings. Stop immediately on abnormal vibration, unusual noise, voltage sag, or overheating.

Taking 80% usable capacity of the 550 mAh pack gives approximately 6.6/4.4/3.3 minutes at average currents of 4/6/8 A, and about 1.4 minutes at full power. The cruise current has not been measured, and no endurance is promised.

Maximum single-motor thrust produces a yaw moment of approximately 0.114 N·m. This version has no rudder and no automatic motor-failure detection; one side's power shall not be deliberately cut during the first flight. Upon a detected single-side failure, the pilot shuts down both motors and recovers the aircraft using the verified glide method.

## 05 / Structural Screening and Manufacturing Requirements

The main spar is conservatively screened for a 3 g load factor, a 190 mm cantilever per side, and the entire load concentrated at the wingtip. The load per side is 2.91 N, the root bending moment is 0.553 N·m, and the bending stress in the OD 4 / ID 2 round tube is approximately 93.9 MPa. Assuming E=70 GPa, the wingtip deflection is approximately 8.1 mm.

This is not a strength certification: no allowable stress for the same production lot of carbon tube is available, and bonding, local crushing, torsion, fatigue, and landing impact have not been verified. First produce joint specimens from the same material, recording stepped loads, deformation, and residual set after unloading; without specimen evidence, clearance shall not be granted on the basis of stress figures.

First weigh a 100×100 mm foam sample and back-calculate the density. Use paperless lightweight foam; avoid paper-faced board, solid printed shells, and heavy paint, which would invalidate the mass budget. The nose block and canopy may be hollowed; the thinnest wall actually retained must be verified by loading a specimen.

DXF units are mm: CUT cuts through, SCORE marks location lines/grooves, and DRILL_VERIFY marks hole positions pending verification—do not drill directly from that layer. Cut test coupons first to confirm the kerf and the fits. The main spar groove is about 1 mm deep, with the tube protruding upward; the longitudinal rods are laid into open-bottom grooves that are later sealed with tape. Avoid crushing damage where members cross.

The firewall is laminated from two layers of 1 mm plywood. The motor mounting holes are transferred from the actual hardware, and the effective screw length must avoid the windings. The printed motor mount transfers the load into the longitudinal rods and the wing panel; it must not be bonded to the thin nacelle skin alone.

The STL files are placed at local origins with the bottom face at Z=0. One side may first be trial-printed in PETG at 0.2 mm layer height to check the rod slots and interlayer strength, then adjusted for the sliced wall thickness and weighed. The vertical-tail alignment jigs must be fitted to the curved foam surfaces; the control-horn holes are finalized against the actual pushrod hardware.

The twin belly skids reach Z=-14 at the bottom, and the 2-inch propeller discs reach Z=-5.4; the level static clearance is 8.6 mm, which does not guarantee propeller clearance over grass or during pitched landings. Stop the propellers before landing, and retain easily replaceable belly wear layers and spare propellers.

## 06 / Assembly Sequence

1. Specimens: cut foam test coupons, a main-spar bonding specimen, and firewall blanks; print one set of motor mounts. Confirm the material, kerf, printed mass, motor hole positions, and screw lengths.

2. Wing panel: cut the main wing/chines, the left and right elevons, and the servo pockets; mark the nose datum, the CG window, and the spar and rod lines. Flatten the wing panel, machine the shallow grooves, bond the carbon tube and rods, and bridge the joints with tape on the upper and lower faces.

3. Powerplant mount: bond the motor mounts and the firewall whose holes have been verified against the hardware, ensuring the two axes are parallel. No deliberate thrust offset angle is set in the initial version. Motors and propellers are first checked only as an unpowered dry-fit assembly.

4. Forward bay: install the battery tray, bulkheads, and side walls. The two ESCs sit at X=70–95; the side walls need ventilation holes based on the actual heat dissipation, with the intake and exhaust paths preserved. Place the battery center near X=125 initially; the ballast remains removable for now.

5. Nacelles: roll the foam skins and install the formers; each intake cone is tied back to the main wing through a 77 mm longitudinal foam web and must not be left unsupported. Leave a separable seam on each nacelle and close it only after wiring. Align the vertical tails to the 15° inward cant using the alignment jigs.

6. Control surfaces: tape hinges free of binding; center the servos mechanically, then connect the pushrods and control horns. Determine the pushrod bends from the actual servo arms; the schematic straight rods are not finished parts. Set the reflex mechanically first, then fine-tune.

7. Electrical: the two power branches are independent, and the control supply is a common 5 V. The forward ESCs use extended motor phase wires; keep the battery DC leads as short as possible. Select the wire gauge for the current, and re-test voltage drop, commutation, temperature rise, and interference. Secure the harness and keep it clear of the propeller discs.

8. Closure: battery straps with an anti-slip layer; a hatch must not be the sole retention means. Install the lightweight canopy, the belly wear layers, and high-visibility markings. Re-weigh the mass, CG, and lateral balance. Re-measure after every battery change, repair, or ballast change.

## 07 / Wiring and Radio Setup

Radio link: choose the ELRS version of the Pocket transmitter, with the RP1 receiver on a compatible band, firmware, and binding setup. Configure at least 8 logical channels on the transmitter. Regionally applicable radio versions and field requirements must be confirmed separately.

Connect the RP1 TX line to the A3 Mini serial RX signal input; 5 V and GND are connected; the RP1 RX line is left unconnected. The RP1 must be powered at 5 V and must not be connected directly to 2S. The A3 Mini must support CRSF; the manufacturer's guide states this is available from V1.6 onward, and the configuration tool must also be compatible.

The 2S battery feeds the power inputs of the two ESCs separately and also powers the independent 5 V/2 A BEC. The BEC powers the control bus; all signals share a common ground. Select ESCs without a BEC; if the actual unit has one, insulate its red wire separately—multiple BEC outputs must not be connected in parallel.

Set the A3 Mini to Delta: the AIL port drives the left elevon and the ELE port the right elevon; the THR signal is split into two paths for the two ESCs. The pinout follows the markings on the actual hardware; do not judge by wire color alone.

CH1 roll, CH2 pitch, CH3 dual-motor throttle, CH4 unused, CH5 arming flag, CH6 three-position mode, CH7/8 reserved. The stabilizer mode mapping moves to CH6, and other unused inputs are set to None. The two-position character of CH5 does not carry the three-position mode.

Turn off delta mixing in the transmitter; mix only once, in the stabilizer. Assign CH3 a physical-switch throttle lock, permit arming only at low throttle, and lock at power-on. Start the servo/ESC outputs at 50 Hz; do not raise the frame rate for analog servos on your own initiative.

Initial ground throws: reflex 3°; pitch ±10° and roll ±8°, with the total mixed travel limited to ±18° and mechanical margin retained. These are only starting points for ground and glide testing. Start with the modes OFF/NORMAL/NORMAL; consider LEVEL only after the trim and gains have been verified.

Check the control directions with the propellers removed: pull stick -> both trailing edges up; right-roll command -> right trailing edge up and left trailing edge down. With the nose raised, the stabilizer commands a nose-down correction; with the right wing depressed, it commands a left-roll correction. The actual trailing-edge motion is authoritative; do not apply servo-reversal values that have not been calibrated.

## 08 / Lost Link, Ground, and Flight Verification

The lost-link (failsafe) behavior must be tested in three scenarios: transmitter switched off, receiver serial link disconnected, and receiver powered down. Both motors must stop, and there must be no sudden spool-up at throttle when the link recovers. The A3's lost-link mechanism returns the outputs to their power-on initial positions, so the unit must be powered on at low throttle. The CRSF link must not simply reuse the web failsafe settings written for PWM receivers.

Electrical checks: under rapid servo actuation and controlled loading, the 5 V bus must not fall out of the equipment operating range and must not restart; the throttle lock, directions, and stabilizer corrections must all be correct. Complete the range check as required by the equipment, and compare the interference with the propulsion on and off.

Propulsion release criterion: the measured installed total static thrust (gf) is at least the actual takeoff mass (g), with current, voltage sag, and temperature rise within the component ratings. The left/right thrust difference at equal throttle is screened at no more than 5% for this project. Do not test bare motors only, and do not ignore the nacelle and installation losses.

Structural release criterion: step-load the same-lot main-spar bond and motor-mount specimens, recording the deflection and the residual set after unloading; on any crack, debonding, or obvious permanent deformation, return to design. This report does not fabricate these test results.

First perform a low-energy unpowered glide in the complete flight-mass configuration, with an experienced person judging the trim trend. Nose-up, nose-down, or rolling tendencies that the CG cannot explain must be investigated first; stabilizer gain must not simply be increased.

The launch procedure uses an assistant or a cradle, but a powered hand launch is not presupposed. First verify the grip and release points and the departure attitude; the specific launch cradle, release speed, and power sequence must be determined from the field conditions and the glide results. No powered launch is performed before such a procedure has been defined.

The school's standard 400 m athletic field is only a candidate; permission, airspace clearance, personnel segregation, and the applicable local rules must still be checked. The city/school has not yet provided these, so this item cannot be completed. Choose calm conditions with a measured wind of no more than 2 m/s for the first round of trials; this is an engineering default condition, not a general regulation.

An experienced pilot flies the first flight on a short circuit; set a conservative timer based on the measured consumption. Complete at least three controlled takeoffs, turns, trims, and belly landings, and close the issues and revise the documents before advancing to the verified version.

## 09 / Deliverables, Budget, and Follow-on Work

Deliverables: the FreeCAD source project, STEP models, printed-part STLs, per-part DXFs, general arrangement/side/front/internal layout/wiring drawings, 1:1 tiled templates, the BOM, manufacturer propulsion data, calculation JSON, blank test records, and an interactive model preview that opens offline.

The flat patterns, carved blocks, and equipment envelopes in the CAD are trial-production references. Motor screw holes, servo lug positions, propeller shaft adaptation, actual battery dimensions, and all measured parameters remain open items; these are not production-release drawings. Template pages whose names contain BLANK are blanks and must be fitted per the assembly drawing.

The first-round budget is 3230 CNY, with at least 1770 CNY reserved. The BOM includes the procurement allowance for two flight batteries, but the mass table counts only the one installed; fabrication equipment purchases are excluded. Verify prices before procurement; if the first round exceeds 3,500 CNY, cut non-essential cosmetic parts first.

Phases: hardware interface confirmation -> propulsion and structural specimens -> complete-aircraft dry-fit assembly and weighing -> equipment fixing and closure -> electrical and load testing -> unpowered glide trim -> first flight -> three-flight review. Revise first whenever an item fails; failed parameters must not become the defaults for later phases.

v2_1400 retains only its start conditions. After the small version passes flight acceptance, set an independent budget for the large version and recalculate the aerodynamics, structure, propulsion, and takeoff/landing; test experience may be inherited, but direct proportional scaling is not permitted.

Keep the physical-measurement columns of data/test_records.csv blank. The qa directory holds the digital checks and renders already performed; parts must be re-checked after regeneration, and verification conclusions from an old version must not be reused.

## 10 / Sources and Evidence Boundaries

S1 NASA, original SR-71 dimensions. Used only for proportion reference; not a basis for the model's aerodynamic performance. https://www.nasa.gov/image-article/sr-71-takeoff-with-afterburner/

S2 Happymodel EX1103 KV11000: dimensions, mass, and 7.4 V / 2023R bench data. https://www.happymodel.cn/index.php/2022/09/05/bassline-spare-part-ex1103-kv11000-brushless-motor/

S3 HobbyEagle A3 Mini official manual: interfaces, delta mixing, lost-link mechanism, and output frequency. https://www.hobbyeagle.com/manuals/A3MINI_User_Manual_en.pdf

S4 HobbyEagle CRSF integration guide: compatible firmware and single-wire connection. https://www.hobbyeagle.com/quick_guide/crsf/?lang=zh-cn

S5 RadioMaster RP1 V2: equipment envelope, 5 V supply, CRSF, mass including antenna. https://www.radiomasterrc.com/products/rp1-expresslrs-2-4ghz-nano-receiver

S6 RadioMaster Pocket: transmitter series and ELRS versions. https://radiomasterrc.com/products/pocket-radio-controller-m2

Access date: 2026-09-11. The references directory holds the manufacturer documents already obtained. Re-check the actual hardware revision against the manufacturer documentation before procurement; prices, manufacturing fits, and aerodynamic parameters not yet measured remain estimates or items pending verification.

Geometric integration, mass moments, thrust-to-weight ratio, beam model, and endurance sensitivity are computed by the project scripts, with the principles and assumptions listed. No wind-tunnel, CFD, VLM, or real-flight simulation was performed, and no fabricated flow fields or compliance evidence are presented.
