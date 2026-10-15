#!/usr/bin/env python3
"""SR71-600 bring-up level 3: 30-minute stability + watchdog acceptance script.

Automates the four checklist items of the level 3 list in firmware/README.md:
  1. Connect to the Pico USB serial port and log all output, with timestamps,
     to a file
  2. Soak for N minutes (default 30): monitor that missed stays 0, no
     unexpected resets, no gap in the log
  3. When time is up, send 'w' automatically: the firmware should print STALL
     and be reset by the watchdog (2 s period)
  4. Reconnect automatically after the reset and verify the reboot banner
     reset cause: WATCHDOG and state=DISARMED
Prints a PASS/FAIL summary at the end; the full log is in the --out file and
can be entered into data/test_records.csv.

Usage (first hold BOOTSEL while plugging in USB and drag sr71fc_level3.uf2
onto the RP2350 drive):
    python soak_level3.py                    # auto-find the Pico port, default 30 minutes
    python soak_level3.py --minutes 2        # 2-minute smoke test first
    python soak_level3.py --port COM5
    python soak_level3.py --wait-boot        # start before dragging the UF2; auto-captures the boot banner
Note: do not hold the same serial port open with PuTTY etc. while this runs.
Dependencies:
    pip install pyserial
"""
import argparse
import re
import sys
import time

import serial
from serial.tools import list_ports

PICO_VID = 0x2E8A  # Raspberry Pi

BANNER = "level3 minimal"
STALL = "STALL on purpose"
RESET_WD = "reset cause: WATCHDOG"
DISARMED = "state=DISARMED"

T_RE = re.compile(r"t=(\d+)s ticks=(\d+) missed=(\d+) maxloop=(\d+)us")


def find_pico_port():
    """Return the sole Pico serial port name; print a hint and return None if none or several."""
    ports = [p for p in list_ports.comports() if p.vid == PICO_VID]
    if len(ports) == 1:
        return ports[0].device
    if not ports:
        print("No Raspberry Pi (VID 2E8A) serial port found. Current ports:")
        for p in list_ports.comports():
            print(f"  {p.device}  {p.description}")
        return None
    print("Multiple Pico serial ports found; specify one with --port:")
    for p in ports:
        print(f"  {p.device}  {p.description}")
    return None


def open_serial(name):
    """Open the serial port; may fail while the device re-enumerates after a reset, so retry."""
    for _ in range(50):
        try:
            return serial.Serial(name, 115200, timeout=1)
        except serial.SerialException:
            time.sleep(0.3)
    raise serial.SerialException(f"could not open {name}")


class Soak:
    def __init__(self, logf):
        self.logf = logf
        self.max_missed = 0
        self.status_lines = 0
        self.unexpected_reboots = 0
        self.max_silence = 0.0
        self.last_rx = time.time()
        self.seen_status = False
        self.w_phase = False  # after 'w' is sent, a reboot banner is expected and not counted as unexpected

    def feed(self, line):
        """Process one firmware output line: write to log + update statistics. Returns the raw line text."""
        ts = time.strftime("%H:%M:%S")
        self.logf.write(f"{ts} {line}\n")
        self.logf.flush()
        print(f"[{ts}] {line}", flush=True)
        self.last_rx = time.time()

        m = T_RE.search(line)
        if m:
            self.status_lines += 1
            self.seen_status = True
            missed = int(m.group(3))
            if missed > self.max_missed:
                self.max_missed = missed
        elif BANNER in line:
            # boot banner: appearing mid-soak = unexpected reset (acceptance item 2 FAIL);
            # a reboot banner during the 'w' test phase is expected behavior, not counted
            if self.seen_status and not self.w_phase:
                self.unexpected_reboots += 1
                print(">>> ANOMALY: reboot banner appeared during the run (unexpected reset)", flush=True)
        return line


def read_for(ser, soak, seconds=5.0):
    """Read lines for a fixed duration (the firmware prints one line per second and never goes silent, so we cannot finish by waiting for silence)."""
    t_end = time.time() + seconds
    while time.time() < t_end:
        try:
            raw = ser.readline()
        except serial.SerialException:
            return
        if raw:
            soak.feed(raw.decode("ascii", errors="ignore").strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", help="Pico COM port, e.g. COM5 (default: auto-scan for VID 2E8A)")
    ap.add_argument("--minutes", type=float, default=30.0, help="soak duration in minutes (default 30)")
    ap.add_argument("--out", default=time.strftime("soak_level3_%Y%m%d_%H%M%S.log"),
                    help="log output file")
    ap.add_argument("--wait-boot", action="store_true",
                    help="scan and wait for the port to appear (use right after dragging the UF2, to capture the boot banner)")
    args = ap.parse_args()

    port = args.port
    if not port:
        print("Scanning for Pico serial port (VID 2E8A)...")
        while True:
            port = find_pico_port()
            if port or not args.wait_boot:
                break
            time.sleep(0.5)
    if not port:
        sys.exit(1)

    print(f"Port: {port}  Duration: {args.minutes} minutes  Log: {args.out}")
    print("Note: right after power-up the firmware waits for a serial connection (up to 8 s) before printing the banner.\n")
    ser = open_serial(port)

    fail = []
    stall_seen = False
    wd_cause_seen = False
    disarmed_after_reset = False

    with open(args.out, "w", encoding="utf-8") as logf:
        soak = Soak(logf)

        # ---- Phase 1: soak ----
        print(f"===== Phase 1: soak for {args.minutes} minutes (Ctrl+C to abort) =====")
        t_end = time.time() + args.minutes * 60
        try:
            while time.time() < t_end:
                try:
                    raw = ser.readline()
                except serial.SerialException as e:
                    fail.append(f"serial error during soak: {e}")
                    break
                if raw:
                    soak.feed(raw.decode("ascii", errors="ignore").strip())
                silence = time.time() - soak.last_rx
                if silence > soak.max_silence:
                    soak.max_silence = silence
                if silence > 5.0:
                    # the one-line-per-second cadence stopped for >5 s: a sign of a hang
                    # that even the watchdog did not recover
                    fail.append(f"log silence {silence:.0f}s (one line per second expected)")
                    break
        except KeyboardInterrupt:
            print("\nAborted by user.")
            ser.close()
            sys.exit(2)

        if not soak.seen_status:
            fail.append("no t=...s status line received (check firmware/serial port)")

        # ---- Phase 2: watchdog test ----
        if soak.seen_status and not fail:
            print("\n===== Phase 2: send 'w' to trigger the watchdog reset =====")
            soak.w_phase = True  # any banner from now on is the expected reset
            ser.write(b"w")
            t_send = time.time()

            # 2a. Wait for the STALL line (should appear immediately)
            while time.time() - t_send < 3.0:
                try:
                    raw = ser.readline()
                except serial.SerialException:
                    break
                if raw and STALL in soak.feed(raw.decode("ascii", errors="ignore").strip()):
                    stall_seen = True
                    break
            if not stall_seen:
                fail.append("STALL on purpose line not seen within 3 s of sending 'w'")

            # 2b. Reset -> USB re-enumeration -> reconnect, capture the boot banner
            #     (the firmware waits <=8 s for a serial connection)
            print("Waiting for reset and reconnecting (Windows re-enumeration takes about 1-5 s)...")
            try:
                ser.close()
            except serial.SerialException:
                pass
            ser = open_serial(port)
            t_reconnect = time.time()
            while time.time() - t_reconnect < 15.0:
                try:
                    raw = ser.readline()
                except serial.SerialException:
                    time.sleep(0.3)
                    try:
                        ser.close()
                    except Exception:
                        pass
                    ser = open_serial(port)
                    continue
                if not raw:
                    continue
                line = soak.feed(raw.decode("ascii", errors="ignore").strip())
                if RESET_WD in line:
                    wd_cause_seen = True
                if DISARMED in line:
                    disarmed_after_reset = True
                if wd_cause_seen and disarmed_after_reset:
                    break
            # read a few more lines to confirm normal operation after the
            # reset (t restarts from a small value)
            read_for(ser, soak, seconds=5.0)

        ser.close()

        # ---- Verdict ----
        print("\n===== Result =====")
        print(f"Status lines: {soak.status_lines}  Max missed: {soak.max_missed}  "
              f"Unexpected resets: {soak.unexpected_reboots}  Max silence: {soak.max_silence:.1f}s")
        if soak.max_missed != 0:
            fail.append(f"missed reached {soak.max_missed} (must stay 0)")
        if soak.unexpected_reboots:
            fail.append(f"{soak.unexpected_reboots} unexpected reset(s) during soak")
        if not stall_seen:
            fail.append("STALL line not captured")
        if not wd_cause_seen:
            fail.append("reset cause: WATCHDOG line not captured after reset")
        if not disarmed_after_reset:
            fail.append("state=DISARMED line not captured after reset")

        if fail:
            print("FAIL:")
            for f in fail:
                print(f"  - {f}")
            print(f"Full log: {args.out}")
            sys.exit(1)
        print(f"PASS: {args.minutes:g} minutes with no dropped ticks and no unexpected reset + watchdog reset + outputs disabled after reset, all passed")
        print(f"Full log: {args.out} (can be entered into data/test_records.csv)")


if __name__ == "__main__":
    main()
