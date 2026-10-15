# SR-71 600 mm Prototype: Brushless ESC Candidate Links

Screening criteria: single-channel ESC, 2S-capable, at least 12A continuous, no BEC or an isolatable BEC, preferably no more than 6g, and support for the ordinary PWM throttle output by the Pico.

## 1. AGFRC XR-30AL (in-stock first choice on Taobao, updated 2026-10-08)

- In stock at the AGFRC official Taobao store: about CNY 124 each; buy two from the same batch.
- Specs: 2–4S, 30A continuous / 35A peak, OPTO with no BEC, BLHeli_S, about 4.5g, 26×13×4mm.
- Same size and weight as the XR-20A with more current headroom; the XR-20A at $15.99 direct from the official site remains an equivalent fallback.
- The same store's XR-4A (1S/4A) and XR-7A (2S/7A) **do not qualify**: 4A is far below the single-motor peak of 9.2A; 7A is below the 12A screening floor.

## 2. AGFRC XR-20A (official-site direct-purchase fallback)

- Official purchase page: https://www.agf-rc.com/agfrc-xr-20a-20a-2-4s-blhelis-esc-p7186274.html
- Manufacturer spec page: https://www.agfrc.com/index.php?id=2509
- Domestic official store: https://agfrc-servo.taobao.com/
- Specs: 2–4S, 20A continuous / 25A peak, about 4.5g, about 26×13×4mm, no BEC.
- The manufacturer explicitly lists ordinary PWM throttle at 1000–2000us; OneShot and DShot are also supported.
- Buy two, from the same batch if possible.
- About 1mm wider/longer than the original 25×12mm envelope; dry-fit before installation.

## 2. EMAX Bullet 15A

- Official purchase page: https://shop.emaxmodel.com/products/emax-d-shot-bullet-series-15a-2-4s-blheli_s-esc-3-5g-support-onshot42-multishot
- Product number: 0111002007.
- Specs: 2–4S, 15A, about 3.5g, no BEC.
- Current capacity covers the single EX1103 manufacturer peak of 9.2A.
- The page explicitly lists DShot, MultiShot, OneShot42, and OneShot125 but never states 50Hz ordinary PWM; before ordering, get the seller's written confirmation that 1000–2000us ordinary PWM input is supported.

## 3. EMAX Bullet 20A

- Official purchase page: https://shop.emaxmodel.com/products/emax-d-shot-bullet-series-20a-2-4s-blheli_s-esc-3-5g-support-onshot42-multishot
- Product numbers: 0111002008 / EMX-SC-1773.
- Specs: 2–4S, 20A continuous, about 3.5–4g, about 11.9×19.6mm, no BEC.
- More current headroom than the 15A version.
- Likewise needs the seller to confirm ordinary PWM arming compatibility.
- AliExpress candidate listing ID: 1005001425903504; third-party stores require checks on authenticity, model, and same-batch consistency of the two units.

## 4. FVT LittleBee 20A (fallback)

- Purchase page: https://quadsrtf.com/product/20a-littlebee-esc/
- Specs: 2–4S, 20A continuous / 30A peak, about 4g, about 23×12.5×3mm, no BEC.
- An older design with many clones on the market; buy only after the seller confirms original manufacture, ordinary PWM, and 2S startup.

## 5. RadioLink RE15A 2S (easy to use but heavy)

- Official product page: https://www.radiolink.com/15a_esc
- Official spec page: https://www.radiolink.com/15a_esc_specs
- Specs: 2S only, 15A continuous / 20A peak, standard PWM 1000–2000us, about 7.4g, about 40×16mm, with a 5V/2A BEC.
- Purpose-built for fixed-wing, with the clearest ordinary-PWM support — well suited to first-time debugging.
- Each unit exceeds the current 6g target, and a pair adds about 5.6g or more; adopt only if the whole-aircraft weigh-in still leaves margin.
- The current design already has a dedicated 5V UBEC/BEC (≥3A continuous, 5A preferred), so the red BEC wire in these two ESCs' signal leads must be isolated at installation.

## Choosing the Input-Connector Version

Retail ESCs commonly come in versions such as "Deans T-plug soldered", "banana plugs soldered", or "XT60 soldered". Per `circuit_design.md` §2, this project solders both ESC power inputs, the XT30 battery leads, and the UBEC input to the same star point — no connector goes straight to the battery. Therefore:

1. If a bare-lead (no connector) version exists, buy that one first.
2. Otherwise buy the cheapest version of any kind, cut the connector off on arrival, and re-solder to the star point.
3. Do not buy adapter leads (e.g. XT60-to-XT30) to patch interfaces together: two extra contact-resistance points and several grams of weight — a bad trade.
4. Keep the cut-off banana plugs as spare detachable motor-phase connectors, convenient for swapping phase order per §8 to reverse rotation; note that 3.5mm banana plugs may be oversized for 1103-class thin silicone wire — match to the actual wire gauge.
5. The aircraft's connector standard is exactly one: XT30. If the battery's stock connector is not XT30 (e.g. PH2.0 or a small JST), the battery leads must be re-terminated with XT30 — the twin-motor peak of about 18.4A exceeds what small connectors are rated for.

## Confirmation Text To Send the Seller Before Ordering

> Please confirm that this is a single-channel brushless ESC that supports a 2S LiPo, directly recognizes a 1000–2000us ordinary PWM throttle signal, and can complete arming and throttle calibration on a 50Hz input — not DShot-only. Please also confirm that it contains no BEC, the actual weight with leads, the outline dimensions, and the current firmware version. I intend to purchase two units from the same batch.

## Conclusion

Priority order: AGFRC XR-30AL → AGFRC XR-20A → EMAX Bullet 15A → EMAX Bullet 20A → FVT LittleBee 20A. The RadioLink RE15A is the easier-to-debug but heavier fallback.

The current Pico firmware is designed for ordinary PWM. If, in the end, only ESCs that explicitly lack ordinary PWM but support OneShot125 can be obtained, the Pico output protocol must first be modified and bench-verified; do not enter powertrain testing on the existing wiring.
