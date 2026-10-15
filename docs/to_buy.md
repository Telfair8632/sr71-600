# Next-Step Purchase List

Date: 2026-10-08. Based on: physical parts check-in (`hardware_checkin_guide.md` §1) + ESC selection (`esc_candidates.md`).
Prices are budget allowances except where marked verified. The already-arrived list is in the check-in guide §1 and is not repeated here.

**Ordering cadence**: Order 1+2 (tools + small parts) → Order 3 (radio system) → Order 4 (ESCs + charger + props). `debug_procedure.md` §3–§7 needs no ESCs; the charger must arrive no later than the ESCs.

## Order 1: Tools (P0 — the missing iron blocks Pico header soldering and the direct MPU6050 hookup)

- [x] Temperature-controlled soldering iron kit — **Deli kit purchased 2026-10-08**; if it only came with knife/bevel tips, add a fine conical tip for SOT-23-5 soldering; if no flux was included, add a small tin
- [x] Multimeter — **purchased 2026-10-08**
- [x] Data-capable USB cable (micro-USB) — **already on hand**

## Order 2: Small Parts (LCSC + Taobao combined into two orders)

**LCSC order** (search the part number to land directly on it; verified in stock):

- [ ] SN74LVC1G17 SOT-23-5 ×10 (part no. C22469943, about CNY 3 for 10) — U2 receiver buffer
- [ ] 2N3904BU TO-92 ×5 (part no. C124482, about CNY 1) — Q1 hardware enable

**Taobao order**:

- [x] SOT23-5-to-DIP adapter boards (double-sided: SOT23-6 front / SOT23-5 back) — **purchased 2026-10-08**
- [x] 1/4W metal-film resistor assortment — **ordered 2026-10-08** (through-hole, includes 220Ω/1k/4.7k/10k)
- [ ] AMASS XT30UPB male-female pairs ×2 (one pair reserved for battery re-termination) — about CNY 12
- [x] Silicone wire (tinned copper) — **purchased 2026-10-08**
- [x] Heat-shrink tubing assortment — **purchased 2026-10-08**
- [ ] Hook-and-loop straps (battery retention, maps to ASM01) — about CNY 5
- [ ] PH2.0 4-pin to Dupont female jumper leads ×2 — about CNY 6 (the MPU6050 module's V/G/SCL/SDA is a PH2.0 socket; drop one lead if the supplied cable is enough)
- [ ] JST 1.0mm to 2.54mm servo adapter leads ×2 — about CNY 10 (**buy only after confirming the ES9051 connector on arrival**; skip if it is a standard 2.54mm header)

## Order 3: Radio System (ELRS 2.4G — the two items must share the same protocol)

- [ ] RadioMaster RP1 V2 receiver ×1 — budget CNY 150
- [ ] RadioMaster Pocket ELRS transmitter ×1 — budget CNY 650 (batteries not included)
- [ ] 18650 cells ×2 (for the Pocket, USB-C direct charging) — about CNY 40

## Order 4: Powertrain (final batch)

- [x] **AGFRC XR-30AL ESCs ×2** — **purchased 2026-10-08**; on arrival, accept per §0: no BEC/OPTO, actual weight ≤6g, size 26×13×4mm, both from the same batch
- [ ] 2S balance charger ×1 — budget CNY 350 (any model covering 2S balance/storage modes will do; simple ones run as low as CNY 100–200). **ESCs already purchased — this item is now mandatory before powertrain testing**
- [ ] 2-inch 2023-series CW/CCW propeller pair + spares — budget CNY 60 (fitted only at the bench stage)

## Airframe Materials (does not block ground debugging; combine with Order 2 to save shipping)

- [ ] 3mm paperless foam board (main wing / chines / fuselage) — CNY 100
- [ ] 2mm foam board (nacelles / cosmetic parts) — CNY 50
- [ ] 4×2mm carbon tube 380mm ×1 + 2mm carbon rod 215mm ×2 — CNY 90
- [ ] 1mm thin plywood (trays / bulkheads / firewall) — CNY 100
- [ ] Foam adhesive / CA (502), control horns, pushrods, hinge tape, straps, light finish — CNY 180
- [ ] Eight 3D-printed STL parts (PETG, `print/` directory) — about CNY 120 outsourced (filament only if you own a printer)

## Totals

| Batch | Amount |
|---|---:|
| Order 1 tools | CNY 170–260 |
| Order 2 small parts | ≈CNY 88 |
| Order 3 radio | ≈CNY 840 |
| Order 4 powertrain | ≈CNY 673 |
| Airframe materials + printing | ≈CNY 640 |
| **Total** | **≈CNY 2410–2500** |

Against the budget: the XR-30AL overspends the ESC budget by about CNY 68, and the CNY 40 transmitter cells are a new item; both fall within the CNY 1460 rework reserve.

## Companion To-Dos (cost nothing but are blocking)

1. Confirm whether the four KV11000 motors are EX1103 spec (3.8g / 1.5mm shaft / 2-inch prop hole) — this decides whether the motor-mount STLs and the thrust budget must be recalculated.
2. Weigh the 2S 800mAh battery (target ≤55g) and check its stock connector (if not XT30, re-terminate with the reserved pair).
3. On arrival, check the ES9051 connector pitch and decide whether to buy adapter leads.
4. As soon as the small parts arrive, solder the board per check-in guide §6 milestone B — do not wait for the ESCs.
