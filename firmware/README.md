# SR71-600 Firmware (Pico 2 / RP2350)

Level-by-level bring-up corresponding to `docs/debug_procedure.md`. Each level is a standalone project, flashed and verified one level at a time.

**Two pre-built firmwares are included** (ready to flash as-is):
- `level3_minimal/sr71fc_level3.uf2` — bring-up level 3: minimal firmware
- `level4_imu/sr71fc_level4.uf2` — bring-up level 4: MPU-6050 readout

## Rebuilding

The toolchain is installed at **`D:\pico-tools`** (outside this workspace, because the ARM toolchain cannot handle non-ASCII paths):
`pico-sdk` (SDK 2.3.1), `gcc-arm` (14.2.1), `cmake`, `bin\ninja.exe`, `uf2conv.py`.

To rebuild after editing the sources (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1 level3_minimal
powershell -ExecutionPolicy Bypass -File build.ps1 level4_imu
```

The script syncs the sources into `D:\pico-tools\build\` for compilation (a pure-ASCII path), then copies the resulting `.uf2/.elf` back into the level directory.

## Flashing

1. Hold the Pico 2 BOOTSEL button while plugging in USB; an `RP2350` drive appears.
2. Drag the `.uf2` onto the drive; the board reboots automatically and runs it.
3. A USB serial port (COMx) appears in Device Manager; connect with any serial terminal (any baud rate, e.g. 115200).

> Note: at startup the firmware **waits for the host to open the serial port (up to 8 seconds)
> before printing the boot banner** — otherwise the banner is dropped by USB CDC, and the key
> lines `reset cause: ...` / `WHO_AM_I=...` are never visible. So either connect within 8
> seconds of powering up, or use the script below (it captures the banner automatically).

## Level 3: Minimal Firmware (level3_minimal)

No peripheral wiring required; USB power alone is sufficient.

- [ ] On power-up prints `state=DISARMED oe_gate=OFF all_outputs=LOW`; LED flashes 60 ms every 1 s
- [ ] Prints `t=... ticks=... missed=0` once per second (missed staying 0 confirms no dropped ticks on the 1 ms time base)
- [ ] Runs continuously for **30 minutes**: no hang, no unexpected reset, no growth in missed
- [ ] Send `w` over serial: after the STALL line it should reset within ≤2 s, and the reboot log shows `reset cause: WATCHDOG`
- [ ] After the reset, the output state is still `DISARMED / oe=OFF / all_outputs=LOW`

Record results in `data/test_records.csv` (Pico stability pre-verification).

**Recommended: the automated acceptance script** (unattended monitoring + sends `w` automatically + reconnects automatically after the reset to verify the banner, and prints a direct PASS/FAIL verdict):

```powershell
python scripts/soak_level3.py --minutes 2    # 2-minute smoke test first
python scripts/soak_level3.py                # formal 30-minute run
```

A manual approach (PuTTY or any other serial terminal, any baud rate such as 115200) also works, but after the `w` reset the USB device re-enumerates, and the terminal must reconnect within 8 seconds to see the `reset cause: WATCHDOG` line — the script is recommended.

## Level 4: MPU-6050 (level4_imu)

Direct Dupont jumper-wire connections (**no soldering, no battery**):

| MPU6050 module | Pico 2 |
|---|---|
| VCC | 3V3(OUT) |
| GND | GND |
| SDA | GP4 |
| SCL | GP5 |
| INT | GP3 |

- [ ] On power-up prints `WHO_AM_I=0x68 ... PASS`
- [ ] Keep the board flat and still for 10 s → prints `calibration done ... bias gx= gy= gz=`
- [ ] Summary line `S,...` shows `rate≈200.0Hz`, `gap15=0`, `fifo=0`, `|a|≈1.0g`
- [ ] At rest gx, gy, gz are near 0; slowly raise/lower the nose and raise each wing to verify the pitch/roll directions and **write down the sign convention**
- [ ] Send `v` to start the 200 Hz data stream and record continuously for **10 minutes**: no freeze, no gap >15 ms (gap15=0), no FIFO overflow; send `v` again afterwards to stop the stream
- [ ] Record results in the IMU0 row of `data/test_records.csv`

10-minute capture command (run it in another window on the computer, or first confirm the connection with a serial terminal):

```powershell
pip install pyserial
python scripts/imu_capture.py --port COM5 --seconds 600 --out imu_10min.csv
```
