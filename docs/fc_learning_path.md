# SR-71 600 mm Prototype: Self-Developed Flight Controller Learning Roadmap

## Four Core Areas To Learn

1. **Basic circuits and electronics fabrication**: understanding power, grounding, resistors, capacitors, logic levels, regulation, and measurement.
2. **Embedded systems**: using C/C++ on the Pico 2 to read sensors, receive radio commands, generate servo and ESC signals, and implement fail-safes.
3. **IMU and digital signal processing**: understanding sampling, noise, bias, coordinate frames, filtering, and attitude estimation.
4. **Automatic control**: understanding feedback, stability, PID, cascaded rate/attitude control, and elevon mixing.

Fixed-wing aerodynamics is a fifth, supporting area, needed to understand center of gravity, static stability, stall, wing loading, control surfaces, and flight-test methods.

## Stage 1: Build and Measure Circuits Safely (about 2–3 weeks)

Study list:

- Voltage, current, resistance, and power; Ohm's law.
- Series, parallel, and divider circuits; Kirchhoff's current and voltage laws.
- Capacitors for energy storage, filtering, and decoupling.
- DC supplies, BECs, 3.3 V and 5 V logic levels.
- Common ground, shorts, reverse polarity, overcurrent, and battery safety.
- Multimeter voltage, resistance, continuity, and current measurement.
- Soldering, heat-shrink tubing, connectors, and strain relief.

Completion criteria:

- Able to read VCC, GND, inputs, and outputs.
- Able to independently identify the polarity of an electrolytic capacitor.
- Able to measure a BEC output with nothing connected.
- Able to track down a short with a current-limited supply or fused precautions.
- Able to explain why a 5 V signal must not enter an input that accepts only 3.3 V.

Project exercise: build a BEC, capacitor, and dummy-load test board and record the unloaded and loaded voltages.

## Stage 2: Master Pico 2 Embedded Development (about 4–6 weeks)

Study list:

- C/C++ variables, functions, arrays, structs, pointers, bit operations, and modular source files.
- Pico SDK projects, building, flashing, and serial logging.
- GPIO, PWM, timers, interrupts, I2C, UART, and the watchdog.
- Fixed-period tasks, state machines, buffers, timeouts, and fault states.
- Floating point, unit conversion, and data logging.

Recommended order:

1. Blink an LED.
2. USB serial output.
3. Timestamped output on a fixed period.
4. PWM-control one servo.
5. Read data from the radio receiver.
6. Cut the throttle immediately upon lost link.

Completion criteria: the program runs 30 minutes straight with no blocking and no unexpected resets; after signal loss it reaches a safe state within the specified time.

## Stage 3: Read Out and Verify the MPU6050 (about 3–4 weeks)

Study list:

- The physical meaning and units of three-axis acceleration and three-axis angular rate.
- Body frame, sensor frame, and sign conventions.
- Sample rate, aliasing, digital low-pass, noise, and temperature drift.
- Static bias calibration, scale error, and mounting error.
- DATA_RDY interrupts, Pico timestamps, and FIFO.

Project exercises:

1. Read WHO_AM_I and confirm the device communicates.
2. Log six-axis data with Pico timestamps at 200 Hz.
3. Record 10 minutes at rest; compute the mean, standard deviation, and drift.
4. Rotate about each of the three axes in turn and verify axis mapping and signs.
5. Run both motors for a vibration test and inspect the spectrum and anomalous samples.

Completion criteria: effective sample rate steady; no consecutive dropped samples; angular rate near zero with the sensor at rest; data direction correct under attitude changes.

## Stage 4: Signal Processing and Attitude Estimation (about 3–5 weeks)

Study list:

- First-order low-pass filters and cutoff frequency.
- Why gyro integration drifts.
- Why the accelerometer provides a long-term tilt reference yet is disturbed by maneuver accelerations.
- The uses of Euler angles, quaternions, and rotation matrices.
- Complementary filtering and the Mahony algorithm; leave Kalman filtering for later.

Project exercise: implement two-axis roll and pitch attitude estimation first, comparing against a protractor during slow tilts on the desk; then rotate quickly and check lag and return-to-zero.

Completion criteria: static angles stable; slow-tilt error acceptable; no visible jumps during fast motion; returns to near zero when laid flat again.

## Stage 5: Feedback Control and Flight-Controller Architecture (about 4–8 weeks)

Study list:

- Open loop vs closed loop, error, feedback, stability, and oscillation.
- The roles of P, I, and D, and integrator windup.
- Continuous vs discrete control, sample period, and delay.
- Cascaded control: the outer attitude loop commands a target angular rate; the inner rate loop commands the surfaces.
- Output limiting, rate limiting, anti-windup, and sensor-fault handling.
- Elevon mixing: left surface = pitch + roll; right surface = pitch − roll.

Verification order:

1. Propellers off; hand-hold the airframe and check the stabilization direction of the surfaces.
2. Inner rate loop only, starting from low gains.
3. Add the outer attitude loop.
4. Inject sensor-disconnect, lost-link, and program-timeout faults.
5. Tune from logged data, never by feel alone.

Completion criteria: when the airframe rolls right, the controller immediately commands a left-recovery surface — likewise in pitch — and no fault can start the motors.

## Stage 6: Fixed-Wing and Test Methodology (runs parallel to the stages above)

Study list:

- Lift, drag, angle of attack, stall, wing loading, and Reynolds number.
- Center of gravity, aerodynamic center, and static stability margin.
- Delta wings, tailless layouts, elevons, and fixed vertical fins.
- Thrust line, twin-motor thrust mismatch, and single-motor failure.
- Ground checks, glide tests, progressive flight-envelope expansion, and flight logging.

Completion criteria: able to explain the current CG range, surface directions, expected stall risk, and why only one parameter changes at a time.

## Recommended Instruments

Needed from day one:

- A digital multimeter.
- A temperature-controlled soldering iron, solder, and flux.
- An adjustable DC supply with current limiting; without one, use a low-risk fused supply for initial measurements.
- A USB-to-serial adapter.

Add when sensor and flight-controller development begins:

- A USB logic analyzer, for observing I2C, UART, and PWM.
- An oscilloscope, for checking supply dips, noise, and signal waveforms.
- A thrust stand and RPM / current / temperature instrumentation.

## Recommended Reading Order

1. Qiu Guanyuan, *Circuit Theory* (Chinese textbook, 6th edition): start with DC, capacitors, transients, and basic analysis methods.
2. MIT OpenCourseWare 6.002 Circuits and Electronics: systematic coverage of circuits, MOS transistors, dynamic circuits, and frequency-domain concepts.
3. Raspberry Pi's official Pico C/C++ SDK getting-started guides, examples, and API documentation.
4. The official MPU-6000/MPU-6050 datasheet and register map.
5. University of Michigan Control Tutorials: system modeling, PID, and digital control.
6. The ArduPilot Plane documentation on roll and pitch control structure and tuning, for understanding the cascaded architecture of a mature fixed-wing flight controller.

## Time Expectations

At 5–8 hours per week:

- About 2–3 months: able to read wiring, solder, and write basic Pico peripheral programs.
- About 4–6 months: able to independently complete sensor readout, attitude estimation, mixing, and ground verification.
- About 6–12 months: able to understand and debug a basic fixed-wing stability controller.

"Mastery" usually takes multiple projects and years of repeated design, measurement, failure analysis, and flight-data review. The current prototype need not wait for mastery before moving forward, but each stage must meet its corresponding test standard before the next stage begins.
