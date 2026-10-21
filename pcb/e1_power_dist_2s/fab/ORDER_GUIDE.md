# e1_power_dist_2s — Ordering Guide

> Generated 2026-10-21 00:03 JST · release_id: rel_20261021_000347
> This directory is the "ready to order" package. All files are in place; follow any of the paths below.
> (Paths below refer to the original release layout; in this repository everything lives under `pcb/e1_power_dist_2s/fab/` — `pcb_fab/*` → `fab/*`, `procurement/*` → `fab/procurement/*`. The `datasheets/` and `docs/` subfolders of the original release are not redistributed here.)

---

## Board Status Summary

| Item | Value |
|---|---|
| Thickness / layers | 1.6 mm / 2 layers |
| Board size | 74.68 × 94.56 mm (filled in from the routed board; the template field rendered as "?") |
| Parts | 41 (SMT 0, THT 41) |
| Unique MPNs | 4 |
| Gerber files ✓ | `e1_power_dist_2s_fab.zip` |
| Production BOM ✓ | `assembly/e1_power_dist_2s_assembly_bom.csv` |
| Procurement BOM ✓ | `procurement/bom_e1_power_dist_2s.csv` |
| check-pcb gate | PASS @ 2026-10-20T14:56:20.669188Z |

---

## Ordering Preferences (recorded in Phase 2, reused for this release)

| Axis | Choice |
|---|---|
| Channel | **LCSC + JLCPCB cheap combined order** (10–14 days, saves 5–10×) → ★ Path A |
| Brand | domestic_first |
| Price vs stock | tight |
| Blacklisted MPNs | (none) |
| Preferences recorded | 2026-10-20T11:43:53+00:00 |

> To change preferences: run `record_preferences.py` to rewrite `_artifacts/component_selecting/user_preferences.json`, then re-run the release.

---

## Ordering Paths

**Per the Phase 2 channel preference, Path A (JLCPCB combined order) is the primary route.**

### Path A: JLCPCB one-stop (PCB + SMT assembly) ★ primary
**Suits**: every SMT part findable on LCSC (coverage in `coverage_matrix.md`)
**Current coverage**: LCSC 4/4 ✅ recommended
**Steps**:
1. Open https://cart.jlcpcb.com/quote
2. Upload `e1_power_dist_2s_fab.zip`
3. Enable "PCB Assembly"
4. Upload the production BOM: `assembly/e1_power_dist_2s_assembly_bom.csv`
5. Upload the CPL: `assembly/e1_power_dist_2s_positions.csv`
6. Process parameters: 1.6 mm thickness / 2 oz copper / green mask / white silkscreen (details in `fab_options.md`)

### Path B: PCBWay turnkey (PCB + global-sourced assembly)
**Suits**: parts spread across DigiKey/Mouser, incomplete LCSC coverage
**Steps**:
1. https://www.pcbway.com/orderonline.aspx
2. Upload `e1_power_dist_2s_fab.zip`
3. Quote Assembly → upload `procurement/bom_e1_power_dist_2s.csv` (PCBWay accepts global MPNs)
4. CPL: `assembly/e1_power_dist_2s_positions.csv`

### Path C: bare PCB + self-sourced parts (cheapest, hand-soldering required)
Order the PCB as in Path A but **without** the assembly option. Source parts from any distributor:

#### C-1: DigiKey JP (coverage 0/4)
1. Open https://www.digikey.jp/en/mylists/list/bulk-add
2. Upload `procurement/digikey_bulk.csv`
3. Missing parts must come from Mouser or LCSC (see `coverage_matrix.md`)

#### C-2: Mouser JP (coverage 0/4)
1. Open https://www.mouser.jp/Bom/
2. Upload `procurement/mouser_bom.csv`

#### C-3: LCSC (coverage 4/4) ✅ recommended
1. Open https://www.lcsc.com/bom
2. Upload `procurement/lcsc_bom.csv`
3. Watch the international shipping cost

---

## Full Folder Index (original release layout)

- `pcb_fab/` — for the fab house: Gerbers / drill / CPL / production BOM
- `procurement/` — for distributors: procurement BOM + per-vendor upload CSVs
- `datasheets/` — datasheets for all MPNs (for pin lookups while soldering/debugging; not redistributed in this repository)
- `docs/` — HDD / manufacturing transfer pack produced by kidoc (not redistributed here)
- `coverage_matrix.md` — per-distributor stock coverage detail
- `fab_options.md` — JLCPCB vs PCBWay process comparison
- `release_rel_20261021_000347.zip` — the complete package, for e-mailing/hand-off

---

## Red Lines

- ❌ Do not hand the fab house the source `.kicad_pcb` / `.kicad_sch` directly — use the zip under the fab folder
- ❌ Never enter release without a passed check-pcb gate (this guide is only generated after the gate passes)
- ❌ After any MPN substitution, re-run the release (never hand-edit the CSVs only)
