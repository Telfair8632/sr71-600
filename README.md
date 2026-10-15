# SR71-600 — A Twin-Engine 600 mm RC Blackbird

A fully independent engineering project: the complete digital build package, firmware, and verification records for a twin-engine radio-controlled aircraft modeled on the SR-71.

> As a fully independent engineering project, I am designing and building a twin-engine radio-controlled aircraft modeled on the SR-71, with a 590 mm airframe and a 190.7 g mass budget. I completed the full digital design phase myself: a parametric CAD model, an engineering report with assembly documentation, full-scale manufacturing templates, a costed procurement plan, and automated design-verification checks. I then established a staged verification program for the flight controller, a Raspberry Pi Pico 2 microcontroller, progressing through fourteen defined debug levels. My level-three firmware—heartbeat indication, USB logging, and watchdog recovery—passed a 30-minute automated endurance test, and my level-four inertial-measurement firmware validated the MPU-6050 sensor, logging 200 Hz data for ten continuous minutes without a dropped sample. Next, I will construct motor mounts and a thrust-test bench, calibrate weight and balance, and complete ground checks before a supervised first flight. This project demonstrates my capacity for self-directed learning, systematic execution, and safety-conscious engineering practice.

**This repository is the V1.0-P0 digital trial-production release. It is not a flight-certified design.**

## Status Snapshot

| Area | State | Evidence |
|---|---|---|
| Parametric CAD model | Done (P0) | `cad/`, `qa/cad_checks.json` |
| Engineering report & assembly manual | Done | `docs/engineering_report.md` / `.pdf` |
| Manufacturing templates (14 laser-cut DXF, 8 printed STL, 1:1 print sheets) | Done | `cut/`, `print/`, `docs/cutting_templates_1to1.pdf` |
| Circuit design (E1) | Done | `docs/circuit_design.md`, `electronics/` |
| Firmware level 3 — minimal firmware, 30-min soak + watchdog | **PASS** (2026-10-07) | `data/test_records.csv` row PICO0, `firmware/scripts/soak_level3_*.log` |
| Firmware level 4 — MPU-6050 IMU @ 200 Hz, 10-min log | **PASS** (2026-10-13, 1 known issue) | `data/test_records.csv` row IMU0, `firmware/scripts/imu_10min.csv` |
| Physical build & flight test | Not started (parts arriving) | `ROADMAP.md` |

## Repository Layout

```
cad/                FreeCAD source model (.FCStd) and STEP export
config/             design.json — the parametric design entry point
cut/                14 laser-cutting DXF templates (foam sheets)
print/              8 3D-printed parts (motor saddles, fin saddles, control horns)
docs/               engineering report, assembly instructions, circuit design,
                    staged debug procedure, debug logs, assessments, learning path
electronics/        wiring diagram (SVG) and netlist (CSV), revision E1
firmware/           Pico 2 (RP2350) firmware: level3_minimal, level4_imu, bus_doctor,
                    plus the automated acceptance scripts and raw test logs
data/               BOM, procurement budget, test records, measurement records,
                    analysis outputs (JSON) consumed by the generators
src/                Python generators that build the CAD, drawings, PDFs, DXFs,
                    and the offline 3D viewer from config/design.json
qa/                 recorded verification evidence (CAD checks, document checks,
                    viewer checks, run logs)
references/         source links for the reference documents used during design
ROADMAP.md          phase plan, firmware ladder status, next actions, v2 gate
build.ps1           one-command regeneration of the digital package
```

Start here:

- Open `model_preview.html` in a browser — an offline interactive 3D view (drag to rotate; top/side/internal views).
- Read `docs/engineering_report.md` — design, calculations, assembly, wiring, testing, and budget.
- `docs/assembly_dimensions.pdf` and `docs/cutting_templates_1to1.pdf` — dimensioned drawings and 1:1 print templates.
- `docs/debug_procedure.md` — the 14-level staged verification program.
- `docs/debug_log_2026-10-13.md` — the level-4 troubleshooting retrospective.

## Design Baseline

- Envelope 590 mm long (including propeller thickness), 420 mm span, 190 mm motor axis spacing; belly landing.
- Two micro brushless motors (EX1103 KV11000) driving 2-inch normal/reverse propellers on a 2S battery.
- Mass budget 190.7 g, including a 20 g unallocated reserve and 16 g removable steel ballast; final ballast is set by measured CG.
- First-order CG window from the full chine projection: 292.2–298.6 mm from the nose (not an aerodynamically validated result).
- First-round procurement budget CNY 3420 with CNY 1580 held back for rework and spares; not live pricing.

## Reproducing the Build

Requirements: [FreeCAD 1.1.3](https://www.freecad.org) (its bundled Python 3.11) and a Python 3.12 with `ezdxf`, `shapely`, `reportlab`, `pymupdf` (or a `tools/pydeps` folder next to this repo, which the scripts pick up automatically).

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

The design entry points are `config/design.json` and `src/build_cad.py`. The FCStd spreadsheet is a readable parameter list; not every solid is driven by it in real time. The scripts contain explicit modeling stations — if you change overall proportions, revise them together and re-run all checks. STLs are at local origins; STEP/FCStd use whole-aircraft coordinates. Equipment in the CAD is envelope geometry; the appearance prototype is not a strict scale replica.

Rebuilds preserve the measured columns in `data/bom.csv` and all user records in `data/test_records.csv`.

Firmware rebuild instructions (Pico SDK toolchain): see `firmware/README.md`.

## Safety and Limitations

- This is a **digital trial-production release**: hole positions and flight parameters are not measured-and-released values.
- Blank test records must never be treated as passed; propeller-disc geometry is illustrative, not a manufacturable propeller.
- The parachute bay is reserved space only — there is no parachute recovery system.
- Propellers stay off for debug levels 0–7; powered tests only on a fixed bench, never with people in the propeller plane.
- First flights are conducted by an experienced pilot, at a field with confirmed permission, clearance, and people segregation.

## License

MIT — see `LICENSE`.
