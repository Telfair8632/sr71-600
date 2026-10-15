# SR-71 / 600 Procurement List

Version V1.0-P0-E2. P06 uses the self-built Pico 2 + MPU6050 controller; the budget is a procurement control value, not a vendor quote.

## A. Retained locked-in parts

| ID | Qty to buy | Item / search term | Acceptance criteria on arrival | Max onboard mass | Budget cap |
|---|---|---|---|---|---|
| P01 | 3 pcs | Happymodel EX1103 KV11000 | 2S; 1.5 mm shaft; approx. 13.5 x 15.5 mm; max 4.0 g each; one unit as spare | 8.0 g (2 installed) | CNY 330 |
| P02 | 3 sets | 2023R/2023 2-inch CW/CCW prop pairs, 1.5 mm bore | Each set contains CW + CCW; confirm a press fit that does not slip before use; never let glue reach the bearing | <=2.0 g | CNY 90 |
| P03 | 2 packs | 2S 550mAh LiPo, XT30 | Max 32 g each; max 60 x 30 x 16 mm; same batch; measure voltage sag; only one pack installed at a time | 32 g | CNY 180 |
| P04 | 1 unit + 2 cells | RadioMaster Pocket ELRS 2.4GHz + 2 x 18650 cells | Confirm the ELRS version; transmitter packaging usually excludes cells; use qualified same-batch 18650 cells | Ground equipment | CNY 650 |
| P05 | 1 pc | RadioMaster RP1 V2 2.4GHz ELRS | 5V, CRSF, max 2.2 g with antenna; verify the UFL antenna is intact | 2.2 g | CNY 150 |
| P07 | 3 pcs | EMAX ES9051 micro digital servos | 4.0-5.5 V; max 4.3 g each; approx. 19.8 x 8.9 x 23.1 mm; torque >= 0.8 kg·cm at 4.8 V | 8.6 g (2 installed) | CNY 150 |
| P08 | 1 pc | 5V 3A standalone BEC | 2S-capable input; max 5 g; must drive the control board and both servos without rebooting; output <= 5.25V | 5.0 g | CNY 80 |

## B. P06 self-built flight-control replacement parts

| ID | Qty to buy | Item / search term | Acceptance criteria on arrival | Max onboard mass | Budget cap |
|---|---|---|---|---|---|
| P06A | 1 board | Raspberry Pi Pico 2, no wireless, no pin headers | Genuine or fully pin-compatible; 51 x 21 mm; UART, I2C and PWM available; board mass <= 4 g | 4.0 g | CNY 50 |
| P06B | 2 boards | MPU6050 six-axis module with INT pin | Install 1, keep 1 for cross-check/spare; 400kHz I2C; SDA/SCL idle-high level <= 3.3V; max 3 g each | 3.0 g (1 installed) | CNY 40 |
| P06C | 2 chips | SN74AHCT125N, DIP-14 | Must be AHCT125, not HC125; 4 channels; install 1, spare 1 | Counted in the 3 g total below | CNY 20 |
| P06D | 1 set | Low-ESR capacitors, X7R capacitors and resistors | 470uF/10V low-ESR x2; 10uF/25V X7R x5; 0.1uF/100V ceramic x10; 10k ohm x10; 4.7k ohm x10 | Counted in the 3 g total below | CNY 30 |
| P06E | 2 boards + 1 set | Lightweight perfboard, pin headers/plugs, 26-30AWG signal wire | One board for the aircraft, one for practice/spare; no loose Dupont jumpers in the build; P06A-E target <= 10 g | <= 3.0 g (C-E total) | CNY 30 |

## C. Purchase after interface confirmation

| ID | Qty to buy | Item / spec | Purchase condition | Budget cap |
|---|---|---|---|---|
| C01 | 2 pcs | Brushless ESC: 2S, conventional 50Hz PWM, >= 12A continuous each, <= 6 g, <= 25 x 12 x 5 mm | Seller must confirm in writing that conventional receiver PWM works; do not buy DShot-only ESCs; BEC-less preferred | CNY 180 |
| C02 | 1 set | UHU POR-type foam-safe glue + 30-minute slow-set epoxy | Run corrosion/peel test coupons on same-batch foam first; epoxy only at local spots such as carbon rods and firewalls | CNY 100 |
| C03 | 1 set | Motor mounting screws/washers | After motors arrive, measure hole spacing, thread type and safe length; screws must not touch the windings | CNY 40 |
| C04 | 1 set | Phase wires, silicone wire, heat-shrink, XT30, signal wire | Select for the twin 18.4A peak sensitivity; extend phase wires, keep battery DC leads short | CNY 100 |
| C05 | As needed | 5V to 3.3V unidirectional level shifter | Buy only if the measured RP1 TX high level is > 3.6V; the part must handle the CRSF serial baud rate | CNY 30 |

## D. Airframe and structural materials

| ID | Qty | Material / size | Use and requirements | Budget |
|---|---|---|---|---|
| M01 | 2 sheets | 3 mm MPP/Depron-type paperless light foam, each sheet >= 650 x 450 mm | Wing/chines, central fuselage, elevons; weigh a 100 x 100 mm sample first, target density about 35-45 kg/m³ | CNY 100 |
| M02 | 1 sheet | 2 mm same-type paperless light foam, >= 650 x 400 mm | Roll skins for both nacelles, intake spike webs and finish parts; do not buy 10 mm XPS and split it yourself | CNY 50 |
| M03 | 1 sheet | 1 mm aircraft plywood, >= 300 x 300 mm | Battery tray, bulkheads, nacelle formers, firewall lamination | CNY 100 |
| M04 | 1 tube | Carbon tube OD4/ID2, >= 500 mm | Cut the 380 mm transverse main spar; must be straight and crack-free | CNY 50 |
| M05 | 2 rods | OD2 solid carbon rod, >= 300 mm each | Cut a 215 mm longeron from each; a solid rod has no inner diameter | CNY 40 |
| M06 | approx. 50 g | PETG 1.75mm | 8 printed parts; finished total mass <= 4 g; print one side as a sample first | CNY 60 |
| M07 | 1 set | 0.8 mm steel wire, micro control horns, tape hinges | Left/right pushrods, control horns, elevon hinges | CNY 40 |
| M08 | 1 set | Hook-and-loop straps, anti-slip pad, belly wear tape, removable steel plates | Dual battery retention; steel plates for CG adjustment, budget at most 16 g | CNY 80 |

## E. Tools and ground equipment

| Tool | Minimum capability | Notes |
|---|---|---|
| 0.01 g scale | Range >= 300 g | Weigh parts and the complete aircraft; a kitchen scale is unsuitable for 4 g parts |
| Power meter / ammeter | 2S, >= 30 A | Record voltage, current and voltage sag |
| Thrust stand | Range >= 500 gf, with prop guard | Can be homemade, but the motor and scale must be rigidly fixed |
| Multimeter | DC voltage, continuity | Verify the 5V rail and polarity |
| Balance charger | 2S capable, balance/storage modes | Do not use simple USB charge leads without balance management |
| Square / calipers / angle gauge | 0.1 mm class calipers | Verify hole spacing, axes, 15° fin cant and 3° initial elevon reflex |
| Low-wattage iron / hot air or lighter | Suitable for fine-wire soldering | Provide strain relief at joints; keep heat away from foam when shrinking |
| Adjustable current-limited PSU | 0-12 V, >= 3 A | Current-limit the control board at first power-up to avoid cascading damage from wiring errors |
| USB logic analyzer | >= 8 channels, >= 24 MHz | Check I2C, CRSF serial, PWM and control loop timing |
| Goggles and prop guard | Covers test personnel | Nobody stands in the prop disc plane during powered bench tests |

## F. Not purchased for now

- [ ] 2.5-inch propellers: they change current draw and prop-disc clearance; re-match only if the 2-inch setup measures insufficient.
- [ ] Parachute, release servo and shroud lines: only a space reservation exists so far, with no deployment-load or altitude validation.
- [ ] Landing gear, video link, autopilot equipment and decorative lights: they consume mass and CG margin.
- [ ] Whole-airframe 3D-print material: this design is foam-based; a fully printed shell would break the mass budget.
- [ ] Final motor hole template: transfer it only after the actual motors arrive; the current W03 is a blank.

## G. Compatibility review against original equipment

| Original equipment / interface | New-plan correspondence | Check conclusion |
|---|---|---|
| P04 Pocket ELRS -> P05 RP1 | ELRS radio link unchanged | Match |
| P05 RP1, 5V/CRSF | RP1 TX -> Pico UART0 RX; common ground | Protocol match; direct wiring only after the TX high level measures <= 3.6V |
| P06B MPU6050 | SDA->GP4, SCL->GP5, INT->GP3; I2C 400kHz | Function match; Pico timestamps on DATA_RDY and runs its own attitude fusion |
| P06A Pico 2 | UART0 to RP1; I2C0 to MPU6050; 4 PWM channels to AHCT125 | Sufficient resources |
| P07 ES9051, two units | AHCT125 5V PWM -> left/right servos | Voltage match; start at 50Hz; loaded test mandatory |
| C01 two conventional PWM ESCs | AHCT125 5V PWM -> left/right ESCs | Match; DShot-only ESCs do not match |
| P08 BEC | 5V/3A -> RP1, Pico VSYS, AHCT125 and servos | Match; an existing 2A version must pass the simultaneous load test |
| Front-bay installation space | Pico 51 x 21 mm, MPU6050 module per actual size, stacked installation X approx. 295-351 | Original A3 envelope void; dry-fit assembly before cutting the tray |
| Mass / CG | Planned mass 197.9 g, CG X=296.4 mm; CG stays inside the window with the battery at X=120 | 10 g control-stack target is feasible; recompute after weighing |
| Thrust margin | Manufacturer peak static thrust-to-weight ratio about 1.23; about 0.99 assuming 20% installation loss | Margin is thin; no powered flight if the measured installed static thrust-to-weight ratio is < 1.2 |

The current project budget is about CNY 3230, below the 3500 first-round target and the 5000 overall cap.