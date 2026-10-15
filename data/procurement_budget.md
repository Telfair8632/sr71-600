# First-Round Procurement Budget List

All amounts are budget allowances; no orders have been placed with vendors, and these figures must not be read as live quotations. For the prototype, sample units are purchased first; verify dimensions, mass and electrical protocol before anything else.

| Item | Total budget/CNY | Airborne mass budget/g | Key requirements |
|---|---:|---:|---|
| AIR01 3 mm unpapered foam: main wing, strakes, center fuselage | 100 | 24.00 | estimated allowance; weigh offcuts and parts |
| AIR02 2 mm foam: nacelles and cosmetic parts | 50 | 12.00 | estimated allowance |
| STR01 4/2 mm carbon tube main spar, 380 mm | 50 | 5.73 | rho=1600 kg/m3 |
| STR02 2 mm carbon rods 215 mm ×2 | 40 | 2.16 | rho=1600 kg/m3 |
| STR03 thin plywood: mount trays, bulkheads, firewall | 100 | 8.00 | allowance; actual CAD solids separately listed |
| PRT01 PETG local printed parts | 120 | 4.00 | STL volume is solid-volume upper bound; <=4g print budget |
| PWR01 EX1103 KV11000 motors ×2 | 220 | 7.60 | manufacturer mass; verify mounting drawing |
| PWR02 2-inch 2023-series CW/CCW props and spares | 60 | 1.60 | estimate; exact 2023R test combination or retest |
| PWR03 15 A/2S/standard-PWM no-BEC ESCs ×2 | 180 | 12.00 | front vented bay; 25x12x5 mm; extended PHASE leads |
| PWR04 2S 550 mAh battery: buy two, only one aboard | 180 | 32.00 | two packs in purchase allowance; ONE aboard |
| PWR05 5 V/3 A standalone BEC | 80 | 5.00 | 2S compatible; existing 2 A unit only after simultaneous servo stall-load test |
| CTL01 RadioMaster RP1 V2 receiver | 150 | 2.20 | manufacturer mass incl antenna |
| CTL02A Raspberry Pi Pico 2 non-wireless, no-header version | 50 | 4.00 | 51x21 mm; VSYS from regulated 5 V; two UARTs required |
| CTL02B IWT603 and TTL harness | 350 | 8.00 | conditional: raw gyro, >=500 Hz, documented protocol, 3.3 V TTL and actual mass must be confirmed |
| CTL02C AHCT125 buffer, filtering and lightweight solder board | 80 | 3.00 | four 3.3-to-5 V outputs; boot-disabled OE; combined carrier/filter/harness target <=3 g |
| CTL03 EMAX ES9051-class micro servos ×2 | 120 | 8.60 | candidate: 19.8x8.9x23.1 mm, >=0.8 kg.cm at 4.8V; verify genuine item and current |
| CTL04 pushrods, horns, hinge tape | 40 | 4.00 | estimate |
| ASM01 wires, XT30, straps and heatshrink | 100 | 10.00 | estimate; long phase leads required |
| ASM02 adhesive, belly-skid wear layer | 100 | 10.00 | track cured adhesive mass; <=10g budget |
| ASM03 light finish, cockpit and identification markings | 40 | 3.00 | thin dark film/paint; visible tip markers |
| RES01 airborne mass-growth allowance (not a purchased item) | 0 | 20.00 | planning allowance; NOT installed component; CG uncertain |
| TRIM01 removable steel trim weight | 40 | 16.00 | initial estimate; size by real CG; never exceed measured thrust mass gate |
| GND01 Pocket ELRS transmitter and transmitter cells | 650 | 0.00 | ground equipment; regional radio variant to be checked |
| GND02 balance charger and power supply | 350 | 0.00 | 2S balance and storage modes |
| GND03 wattmeter, scale, thrust-stand materials | 250 | 0.00 | ground equipment |
| GND04 Pico data USB cable and soldering consumables | 40 | 0.00 | ground equipment; data-capable USB cable required |

First-round subtotal **CNY 3540**; overall cap CNY 5000, leaving a reserve of **CNY 1460**.

ESCs, BEC, servos and the battery are shortlisted by parameters first; specific vendor models are not yet locked in. The 15 A ESC must support 50 Hz standard PWM; do not purchase DShot-only models on current rating alone.
Motor screw holes, mounting screws and prop-shaft fits will be verified once the hardware is on hand; do not machine the final hole positions before verification.
