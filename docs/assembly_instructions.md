# SR-71 / 600 Assembly Instructions

Applies to the V1.0-P0-E2 built-up airframe. P06 uses the self-built Pico 2 + MPU6050 controller; all coordinates start at the nose X=0.

## 0. Freeze physical interfaces before starting work

- [ ] Print the assembly dimension drawing and the wing template 100 mm check ruler; both horizontal and vertical measurement error must stay within 0.5 mm; set the printer to 100% and disable "fit to page".
- [ ] Weigh and measure the motors, servos, battery, ESCs, BEC, receiver, Pico, MPU6050 and buffer board piece by piece; update bom.csv.
- [ ] Transfer the motor hole pattern from the actual hardware onto the W03 blank; confirm the screws will not touch the windings. Adjust the servo pocket slots to the actual servo mounting lugs.
- [ ] If the predicted takeoff mass exceeds 220 g, or the full 16 g of ballast still cannot bring the CG inside 292.2-298.6 mm, pause final close-out of the airframe.

## 1. Produce material and load-path samples

- [ ] Cut and weigh a 100 x 100 mm foam sample to confirm the material is close to the design density; make corrosion and peel coupons with the chosen glue.
- [ ] From the STLs, print one motor saddle and one fin saddle first; weigh them and test-fit the 2 mm carbon rod and the motor firewall.
- [ ] Make a main-spar-to-foam bond sample and a motor-saddle-to-longeron sample. Load in steps, recording load, deflection and residual set after unloading; on any crack, debond or permanent deformation, redesign and redo.
- [ ] Complete one motor/prop/ESC/battery set test on a guarded bench, then check how well the two sets match.

## 2. Cut the wing and foam parts

- [ ] Cut the integral wing/chine from F01_Wing_chine_NET; cut the left/right F02 elevons, F03 fuselage sides, F04 roof frame, both F05 hatches and the F07 vertical fins.
- [ ] Keep the wing perfectly flat and mark the X=0 nose datum, the X=292.2-298.6 CG window, the X=480 main spar and the Y=±95 longerons.
- [ ] Cut shallow grooves on the SCORE lines: transverse tube center Z=4, above the wing plate; longeron center Z=1, below the wing plate. The two are tangent; do not drill through one another.
- [ ] Round the leading edges and keep them symmetric left/right; no heavy paint finish yet.

## 3. Install the carbon-fiber load structure

- [ ] Place the 380 mm main spar at X=480, spanning Y=-190 to 190; check that it is parallel to the trailing edge with equal length on both sides.
- [ ] Place both 215 mm longerons at X=330-545, Y=±95; offset them above/below the main spar without crushing or cutting the carbon fibers.
- [ ] After bonding, bridge the grooves with light tape to seal them and keep the wing plate flat while curing. Remove the weight boards only after full cure.
- [ ] Check tip height difference, twist and bond voids; do not continue with nacelle installation if out of tolerance.

## 4. Assemble the central fuselage and front bay

- [ ] Bond battery tray W01 and bulkheads W02; install both side walls and the roof frame starting at X=70, keeping both hatches removable for now.
- [ ] Both ESCs sit in the front bay at X=70-95; the battery center can move between X=120-220; BEC center about X=295, RP1 about X=315; the Pico lies lengthwise at X approx. 300-351, with the MPU6050 as close as possible to X approx. 295 on the airframe centerline, fixed on a separate layer from the Pico.
- [ ] Cut ventilation openings per the actual hardware; retain the battery with straps plus an anti-slip pad; a hatch must not be the sole retention.
- [ ] Temporarily place the nose steel ballast at X approx. 80 without bonding it permanently; the final amount follows the measured center of gravity.

## 5. Install nacelles, fins and motor mounts

- [ ] Roll each F06 skin to a 300° open-bottom shell on a 38 mm neutral-layer diameter, seat it on the three W04 formers, and trim the bottom to fit the wing plate.
- [ ] Tie each intake spike to the main wing with a 77 x 15 mm foam web; it must not cantilever; keep a service seam in each nacelle skin.
- [ ] Bond each motor saddle over the longeron and to the wing plate; laminate two W03 firewalls, drill them per the measured hole pattern, and install at X=566-568.
- [ ] Both motor axes at Y=±95, Z=20 and parallel to each other; prop discs at X=586-590. Verify each axis with a straightedge from both the front and the rear.
- [ ] Set each vertical fin to 15° inward cant using the fin saddles, mirrored left/right; check that fins and elevons reach the ±18° full travel without touching the prop discs.

## 6. Install elevons and servos

- [ ] Connect the left and right elevons with tape hinges, keeping a gap of about 0.7 mm; the surfaces must reach ±18° freely without binding.
- [ ] Surface-mount both ES9051 candidate servos at X approx. 465.5, Y=±145; center them mechanically first, then fit the output arms.
- [ ] Bend the 0.8 mm wire pushrods to match the actual arms; the straight rods in CAD only indicate the connection, not the final bend geometry.
- [ ] Set both trailing edges to 3° reflex at neutral; initial pitch ±10°, roll ±8°, with total travel limited to ±18° after mixing.

## 7. Wiring and radio setup

- [ ] Power: the 2S battery splits through XT30 to both ESCs; the ESC phase wires run aft to the motors. When extending phase wires, secure every run and re-check commutation, temperature rise and interference.
- [ ] Control power: 2S also feeds a standalone 5V switching UBEC/BEC (>= 3A continuous, 5A preferred); 5V powers the RP1, Pico VSYS, SN74AHCT125 and both servos. Choose an MPU6050 module that runs from a 3.3V supply; SDA/SCL must be pulled up to 3.3V; all signals share ground. If an ESC carries a BEC, isolate its red wire.
- [ ] Inputs: RP1 TX to Pico UART0 RX (GP1 recommended); MPU6050 SDA to GP4, SCL to GP5, INT to GP3. Set I2C to 400kHz; the Pico records timestamps after DATA_RDY triggers.
- [ ] Outputs: Pico GP6/GP7/GP8/GP9 each become 5V PWM through the SN74AHCT125, feeding the left servo, right servo, left ESC and right ESC. The four OE pins are tied together as OE_N with a 10k pull-up to 5V; Pico GP2 drives an NPN transistor through 4.7k to pull OE_N low before outputs are enabled. Outputs turn off automatically on reset or power loss.
- [ ] AHCT125 DIP pinout: pin 14 to 5V, pin 7 to GND, 0.1uF next to pins 14 and 7; GP6 -> pin 2/pin 3 output, GP7 -> pin 5/pin 6 output, GP8 -> pin 9/pin 8 output, GP9 -> pin 12/pin 11 output; pins 1/4/10/13 are OE. Each of the four outputs on pins 3/6/8/11 gets a 10k pull-down to GND.
- [ ] Place a 470uF/10V low-ESR plus 0.1uF in parallel at the 5V control bus entry; 10uF plus 0.1uF at the MPU6050 supply entry. If the module lacks 3.3V I2C pull-ups, pull SDA/SCL up to 3.3V with 4.7k ohm each.
- [ ] Turn off delta mixing in the transmitter. CH1 roll, CH2 pitch, CH3 throttle, CH5 arm flag, CH6 mode; set the modes to OFF/NORMAL/NORMAL initially.
- [ ] Set a physical-switch throttle lockout and arm only at low throttle; at equipment power-up keep throttle at minimum and hold the airframe still, waiting for IMU bias calibration and the controller self-check.

## 8. Pre-close-out checks and center of gravity adjustment

- [ ] Remove the propellers and check control-surface directions: pulling the pitch stick raises both trailing edges; rolling right raises the right and drops the left trailing edge.
- [ ] Check the self-built controller feedback polarity: raising the nose must command a nose-down correction; depressing the right wing must command a left-roll correction. If either is reversed, do not install props.
- [ ] Cycle both servos rapidly back and forth under a controlled light load; the 5V bus must not sag, reboot or jitter.
- [ ] Weigh the complete aircraft three times with all hatches, canopy, battery and harnesses installed. Move the battery and removable ballast so Xcg enters 292.2-298.6 mm; also check lateral balance.
- [ ] Proceed to unpowered glide only if the measured installed total static thrust (gf) >= actual takeoff mass (g), the left/right thrust difference at equal throttle is <= 5%, and the temperature/current checks pass.

## 9. Lost link, range and glide gate

- [ ] Still prop-less, test each case separately: transmitter off, receiver serial unplugged, receiver power removed. In every case both motors must stop, and they must not restart with throttle when the link is restored.
- [ ] Complete the range check per the radio equipment manual and compare link and servo behavior with power off and on.
- [ ] Have a pilot with fixed-wing experience perform a low-energy unpowered glide at full flying mass first; return to adjustment if the CG or trim tendency is unclear.
- [ ] Powered takeoff does not use a live rear-prop hand launch. Validate the launch cradle, release attitude and field operating procedure separately first.
- [ ] The field must be permitted and cleared of people, with airspace and applicable local requirements confirmed; no powered flight test before confirmation.
