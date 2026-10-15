# SR-71 600 mm Prototype: Post-Delivery Debug Procedure

Applies to the Pico 2, MPU6050, RP1, SN74AHCT125N, two ES9051 servos, two ESCs, and the twin-EX1103 powerplant. Do not enter the next level until the current one has passed.

## General Principles

- Levels 0–7: keep all propellers removed.
- Check for shorts and polarity with a multimeter before connecting the battery.
- Use an adjustable current-limited power supply for the first power-up; if no current-limited supply is available, debug the Pico alone over USB first, then add the 5V devices level by level.
- Powered tests with propellers mounted are performed only on a rigid thrust stand; no person stands in the propeller-disc plane.
- Record every result in `data/test_records.csv`; on any failure, stop at the current level.

## 0. Arrival Inspection

- [ ] Photograph, weigh, and dimension every item; record part numbers and labels.
- [ ] Confirm the battery is 2S; check for no swelling, torn sheath, odor, or abnormal cell voltage spread.
- [ ] Motors are EX1103 KV11000 with a 1.5 mm shaft; the propeller bore fits reliably.
- [ ] The ESCs explicitly support 2S and ordinary PWM input.
- [ ] The UBEC/BEC input supports 2S; output is fixed 5V, at least 3A continuous, 5A preferred.
- [ ] The Pico 2 can enter download (BOOTSEL) mode over USB.
- [ ] The MPU6050 module carries SDA, SCL, INT, and GND pins.
- [ ] The RP1 antenna and UFL socket are intact.

Pass criteria: part numbers, weights, and dimensions meet the procurement constraints; nonconforming parts do not go to soldering.

## 1. Unpowered Electrical Checks

- [ ] Verify that every red wire is power positive and every black wire is GND.
- [ ] On the multimeter continuity range, confirm no shorts between 5V-GND, 3.3V-GND, or battery positive and negative.
- [ ] The 470uF electrolytics have their positive lead to 5V and negative to GND.
- [ ] AHCT125 pin 14 goes to 5V and pin 7 to GND, with 0.1uF near pins 14 and 7.
- [ ] AHCT125 pins 1/4/10/13 are tied together as OE_N with a 10k pull-up to 5V; the NPN collector goes to OE_N and the emitter to GND, Pico GP2 reaches the base through 4.7k, and the base also has a 10k pull-down to GND.
- [ ] Each AHCT125 output on pins 3/6/8/11 has a 10k pull-down to GND.
- [ ] The MPU6050 SDA/SCL pull-ups connect to 3.3V only, never to 5V.
- [ ] If an ESC carries its own BEC, disconnect the red wire in its three-wire signal lead; the control bus is powered only by the independent BEC.

Pass criteria: no shorts, no reverse polarity, no 5V entering a Pico GPIO directly.

## 2. BEC and the 5V Bus

1. Temporarily disconnect the Pico, MPU6050, RP1, servos, and ESC signal leads.
2. Set the adjustable supply to 7.4V with an initial 0.2A current limit and feed the BEC input.
3. Measure the BEC output; it should sit at about 5V and never exceed 5.25V.
4. Reconnect the Pico VSYS, RP1, AHCT125, and MPU6050 one at a time, re-measuring voltage and current after each addition.

Pass criteria: 5V stable, no component overheating, no repeated reboots; no abnormal jump in static current.

## 3. Pico Minimal Firmware

- [ ] Run only the LED, USB logging, and the 1ms system tick at first.
- [ ] Run 30 minutes continuously, with no hangs and no unexpected resets.
- [ ] Enable the watchdog, deliberately stall the main loop, and confirm it resets and keeps throttle output disabled.
- [ ] The power-on default state is disarmed; the AHCT125 stays off.

Pass criteria: the program is stable; on reset or firmware fault the four outputs stay low or carry no valid pulses.

## 4. MPU6050

Wiring: SDA to GP4, SCL to GP5, INT to GP3, common ground. Run I2C at 400kHz.

- [ ] Read WHO_AM_I; the expected value is 0x68.
- [ ] Configure 200Hz sampling, gyro ±1000 deg/s, accelerometer ±8g.
- [ ] The DATA_RDY interrupt only records the Pico microsecond timestamp and sets a new-data flag; the main loop reads the six-axis data.
- [ ] Compute the gyro bias over 10 stationary seconds; the airframe must be still during calibration.
- [ ] Log 10 continuous minutes at an average sample interval of about 5ms; there must be no consecutive dropped samples, no frozen data, and no FIFO overflow.
- [ ] Raise the nose, lower the nose, raise the left wing, raise the right wing, and verify all three axes and their signs.
- [ ] Flat and stationary, the angular rates sit near zero and the accelerometer magnitude near 1g.

Pass criteria: no frozen data in the 10-minute log; no consecutive sampling gap beyond 15ms; all axes and signs confirmed.

## 5. RP1 and the Transmitter

- [ ] Set the transmitter to ELRS 2.4GHz and bind it to the RP1.
- [ ] The Pico reads CRSF data over UART0 and prints channels only, with servos and ESCs not connected.
- [ ] Channel map: CH1 roll, CH2 pitch, CH3 throttle, CH5 arm, CH6 mode.
- [ ] Check center, maximum, minimum, and switch states.
- [ ] Switch the transmitter off; the Pico must detect the lost link. After the link returns it stays disarmed and must not automatically restore throttle.

Pass criteria: all channels correct in direction with no jumps; the lost link is detected reliably.

## 6. Four-Channel Output Waveforms

Keep servos and ESCs disconnected; inspect the AHCT125 outputs with a logic analyzer.

- [ ] Disarmed, self-test failed, or Pico reset: none of the four channels carries valid throttle/servo pulses.
- [ ] After the self-test passes, the servo outputs start at 50Hz, about 1500us center.
- [ ] The ESC outputs start at 50Hz, about 1000us minimum throttle.
- [ ] GP6/GP7 map to the left/right servos; GP8/GP9 map to the left/right ESCs.
- [ ] Signal highs sit at about 5V; period and pulse width are stable.

Pass criteria: no channel crosstalk, no startup glitches, no wide throttle pulse on reset.

## 7. Servos, Mixing, and Stabilization Direction

- [ ] Test with only one servo connected first, then add the second.
- [ ] Center each servo mechanically before fitting the servo arm; do not fix arm positions with large electronic offsets.
- [ ] Pull the elevator stick: both elevon trailing edges rise together.
- [ ] Command right roll: right trailing edge up, left trailing edge down.
- [ ] Neutral reflex about 3 degrees; initial pitch travel ±10 degrees and roll ±8 degrees, total mixed throw not exceeding ±18 degrees.
- [ ] In stabilization mode, raising the nose must produce a nose-down correction.
- [ ] Dropping the right wing must produce a left-roll correction.
- [ ] Drive both servos rapidly back and forth under light load: the 5V rail must not sag, and the Pico, RP1, and MPU6050 must not reboot.

Pass criteria: all manual-command and automatic-correction directions correct; if any direction is reversed, no propeller is mounted.

## 8. ESC and Motor Tests Without Propellers

- [ ] Connect only the left ESC and motor first and complete the throttle-range calibration.
- [ ] Raise throttle slowly from minimum; check startup, rotation direction, abnormal noise, and current.
- [ ] Swapping any two motor phase wires reverses rotation.
- [ ] After the left side passes, test the right side alone.
- [ ] Confirm the two sides spin in opposite directions, so that with the final CW/CCW props both push air toward the tail.
- [ ] Transmitter off, receiver serial unplugged, Pico reset: in every case the motors must stop, and after recovery they must not automatically re-arm.

Pass criteria: both motors run smoothly without propellers; lost link and reset never start the motors.

## 9. Single-Motor Bench Test With Propeller

Rigidly mount the power unit on a guarded thrust stand; do not test by hand.

- [ ] Verify propeller model, rotation direction, front/back orientation, and a secure press-fit.
- [ ] Test 25%, 50%, and 75% throttle in turn, about 10 seconds each; record voltage, current, thrust, and temperature.
- [ ] Start full throttle with 3–5 second short runs and extend gradually once the data looks normal.
- [ ] Stop immediately on abnormal vibration, propeller slippage, battery swelling, odor, distinct stall noise, or a fast temperature rise.
- [ ] Complete the same test separately on both sides.

Program stop limits: motor or ESC reaching 70 degrees Celsius, battery reaching 50 degrees Celsius, 2S voltage under load below about 7.0V, or current exceeding any component rating.

## 10. Twin Motors and Installed Thrust

- [ ] Run both sides simultaneously and record total current and total thrust.
- [ ] Left/right thrust difference at the same throttle must not exceed 5%.
- [ ] Repeated runs must show consistent thrust, current, and temperature trends.
- [ ] While running, check the RP1 link, Pico logs, and MPU6050 data for dropped frames or reboots.
- [ ] Once finally installed in the airframe, measure installed thrust again; bare-bench thrust is not a substitute.

Flight release threshold: `measured twin-motor installed static thrust (gf) / actual takeoff mass (g) >= 1.2`.

## 11. Fault Injection

Test with all propellers removed:

- [ ] Transmitter off: throttle to zero; after the link returns, still disarmed.
- [ ] RP1 serial unplugged: same.
- [ ] RP1 power removed: same.
- [ ] MPU6050 unplugged or its data frozen: the controller drops to direct-manual pass-through and must not drive the surfaces from bad attitude data; raise a fault flag.
- [ ] Pico watchdog reset: throttle stays off; the stationary calibration and manual arming must be performed again.
- [ ] Momentary 5V sag followed by recovery: throttle must not return directly.

Pass criteria: no single fault may produce sudden full throttle or surfaces driven to the mechanical stops.

## 12. Whole-Airframe Mechanics, Weight, and Center of Gravity

- [ ] Check the main spar, longitudinal rods, motor mounts, vertical fins, hinges, and pushrods for looseness.
- [ ] Left and right control surfaces have identical neutral angles and maximum travel.
- [ ] The two motor shafts are parallel, with adequate clearance between the propeller discs and the surfaces, fins, and harness.
- [ ] Fit the battery, hatches, harness, and all flying parts, and weigh the actual takeoff mass.
- [ ] Start with the 52g battery centered about 138mm from the nose tip, then shift it until the measured CG lands inside X=292.2–298.6mm.
- [ ] Do not pre-install steel nose ballast; add a small amount only if the measured CG requires it.

## 13. Conditions for Entering Glide and Powered Flight Tests

- [ ] All preceding tests are logged PASS.
- [ ] The unpowered glide is flown by someone with fixed-wing experience, after confirming the CG and trim tendency.
- [ ] Complete a radio range test, comparing link quality with motors off and running.
- [ ] The powered takeoff method has been verified separately; a motor-on hand launch is not used.
- [ ] Site permission, clear airspace, and personnel segregation are all complete.
- [ ] The first powered flight is flown by someone with fixed-wing experience, with full data logging throughout.

Any item not passed means continue debugging — it never means a flight test may substitute for ground validation.
