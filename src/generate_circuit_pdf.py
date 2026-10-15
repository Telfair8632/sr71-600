from pathlib import Path
from html import escape

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "docs" / "circuit_design_E1.pdf"
SVG = ROOT / "electronics" / "wiring_diagram_E1.svg"
W, H = landscape(A4)
FONT = "Helvetica"

INK = HexColor("#10263b")
MUTED = HexColor("#496479")
BLUE = HexColor("#1677a8")
TEAL = HexColor("#0f8f8f")
GREEN = HexColor("#2f8b57")
ORANGE = HexColor("#d46a1f")
RED = HexColor("#b43b3b")
PANEL = HexColor("#edf5f8")
LINE = HexColor("#b9cbd5")


def setup(c):
    c.setTitle("SR-71 600 V1 Complete Circuit Design E1")
    c.setAuthor("Codex")
    c.setStrokeColor(INK)
    c.setFillColor(INK)


def text(c, x, y, value, size=9, color=INK, max_width=None, leading=None, center=False):
    c.setFont(FONT, size)
    c.setFillColor(color)
    leading = leading or size * 1.35
    lines = simpleSplit(value, FONT, size, max_width) if max_width else str(value).split("\n")
    yy = y
    for line in lines:
        if center:
            c.drawCentredString(x, yy, line)
        else:
            c.drawString(x, yy, line)
        yy -= leading
    return yy


def header(c, title, subtitle, page):
    c.setFillColor(INK)
    c.rect(0, H - 54, W, 54, stroke=0, fill=1)
    text(c, 28, H - 25, title, 18, white)
    text(c, 28, H - 42, subtitle, 8.5, HexColor("#c9e6ef"))
    text(c, W - 56, H - 38, f"E1  |  Page {page} / 4", 8.5, HexColor("#c9e6ef"), center=True)


def footer(c):
    c.setStrokeColor(LINE)
    c.line(28, 24, W - 28, 24)
    text(c, 28, 12, "SR-71 / 600 V1  •  Read circuit_design.md before building  •  Debug without props", 7.5, MUTED)


def box(c, x, y, w, h, title, body="", accent=BLUE, fill=PANEL, title_size=10, body_size=8):
    c.setFillColor(fill)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, w, h, 7, stroke=1, fill=1)
    c.setFillColor(accent)
    c.roundRect(x, y + h - 22, w, 22, 7, stroke=0, fill=1)
    c.rect(x, y + h - 7, w, 7, stroke=0, fill=1)
    text(c, x + 7, y + h - 15, title, title_size, white)
    if body:
        text(c, x + 7, y + h - 34, body, body_size, INK, w - 14, body_size * 1.35)


def arrow(c, x1, y1, x2, y2, color=BLUE, label=None, label_x=None, label_y=None):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.5)
    c.line(x1, y1, x2, y2)
    import math
    angle = math.atan2(y2-y1, x2-x1)
    s = 7
    for delta in (2.55, -2.55):
        c.line(x2, y2, x2 - s*math.cos(angle+delta), y2 - s*math.sin(angle+delta))
    if label:
        text(c, label_x if label_x is not None else (x1+x2)/2, label_y if label_y is not None else (y1+y2)/2+5, label, 7.5, color, center=True)


def page1(c):
    header(c, "Overall power and signal architecture", "Power current, 5V supply and control signals are routed as three separate paths", 1)
    box(c, 35, 243, 108, 78, "B1  2S LiPo / XT30", "7.4V nominal\n8.4V full charge\n18-20AWG main leads", ORANGE, HexColor("#fff4ea"))
    box(c, 183, 243, 116, 78, "PDB  power star point", "BATT+ / BATT-\nSoldered distribution node\nNot routed through perfboard", ORANGE, HexColor("#fff4ea"))
    box(c, 339, 384, 126, 72, "ESC-L", "2S, conventional PWM\nPower: 20-22AWG\nSignal + GND", RED, HexColor("#fff1f1"))
    box(c, 339, 148, 126, 72, "ESC-R", "2S, conventional PWM\nPower: 20-22AWG\nSignal + GND", RED, HexColor("#fff1f1"))
    box(c, 339, 243, 126, 78, "UBEC", "Input: 2S, 6.0V minimum\nOutput: fixed 5V\n>= 3A continuous, 5A preferred", GREEN, HexColor("#effaf3"))
    box(c, 507, 243, 122, 78, "5V_STAR", "Sole 5V source from the UBEC\nServo and logic branches\nEach branch has its own +/- leads", GREEN, HexColor("#effaf3"))
    box(c, 672, 382, 130, 76, "Left motor", "EX1103 KV11000\nProp-off debugging\nPhase wires may be extended", RED, HexColor("#fff1f1"))
    box(c, 672, 144, 130, 76, "Right motor", "EX1103 KV11000\nProp-off debugging\nPhase wires may be extended", RED, HexColor("#fff1f1"))
    box(c, 672, 236, 130, 94, "Control board", "Pico 2 + MPU6050\nRP1 + LVC input protection\nAHCT125 + hardware lockout", BLUE, PANEL)
    box(c, 674, 336, 128, 32, "Left/Right servos", "5V, GND, PWM", TEAL, HexColor("#edfbfb"), 9, 7.5)
    arrow(c, 143, 282, 183, 282, ORANGE, "Battery +/-", 163, 292)
    arrow(c, 299, 295, 339, 420, ORANGE, "Power", 319, 356)
    arrow(c, 299, 268, 339, 184, ORANGE, "Power", 319, 224)
    arrow(c, 299, 282, 339, 282, ORANGE, "Power", 319, 294)
    arrow(c, 465, 420, 672, 420, RED, "3-phase", 566, 432)
    arrow(c, 465, 184, 672, 184, RED, "3-phase", 566, 196)
    arrow(c, 465, 282, 507, 282, GREEN, "5V", 486, 294)
    arrow(c, 629, 282, 672, 282, GREEN, "Logic 5V", 649, 294)
    arrow(c, 629, 304, 674, 352, GREEN, "Servo 5V", 651, 339)
    arrow(c, 735, 330, 400, 456, BLUE, "PWM+GND", 570, 409)
    arrow(c, 735, 236, 400, 220, BLUE, "PWM+GND", 570, 232)
    text(c, 35, 202, "Key rules: power leads short and thick; motor phase wires may be extended. The 5V supply splits into two branches at the UBEC star point.\nAll devices ultimately share ground, but motor current never flows through the Pico perfboard.", 10, INK, 760)
    box(c, 35, 54, 594, 72, "Capacitors and placement", "C1 470uF/10V low-ESR: 5V servo star point; C2 470uF/10V low-ESR + C3 0.1uF: perfboard 5V entry; C4 10uF/25V + C5 0.1uF: next to the MPU6050. When ESC battery leads exceed 100mm, fit a low-ESR capacitor rated at least 16V at the ESC input.", TEAL, HexColor("#f1fbfb"), 10, 8.0)
    footer(c)


def page2(c):
    header(c, "Control board schematic", "On any Pico fault, the four outputs are disabled automatically in hardware", 2)
    box(c, 30, 150, 168, 305, "U0  Raspberry Pi Pico 2", "VSYS <- 5V_LOGIC\n3V3(OUT) -> IMU / U2\nGP0  UART0 TX -> RP1 RX\nGP1  UART0 RX <- U2 Y\nGP2  ARM_GATE -> Q1\nGP3  <- MPU INT\nGP4/5 <-> MPU SDA/SCL\nGP6/7/8/9 -> U1 A1/A2/A3/A4", BLUE, PANEL, 11, 9)
    box(c, 246, 329, 170, 126, "J_RX + U2  Receiver input", "RP1: 5V, GND, TX, RX\nRP1 TX -> U2 A\nU2 = SN74LVC1G17\nVCC = 3V3, input 5.5V tolerant\nU2 Y -> Pico GP1\nPico GP0 -- R1 1k -> RP1 RX", TEAL, HexColor("#edfbfb"), 10, 8)
    box(c, 246, 150, 170, 126, "J_IMU  Six-axis sensor", "MPU6050: 3V3 supply only\nSDA -> GP4, SCL -> GP5\nINT -> GP3\nIf the module lacks pull-ups:\nSDA/SCL each 4.7k to 3V3\nBypass: 10uF + 0.1uF", TEAL, HexColor("#edfbfb"), 10, 8)
    box(c, 461, 135, 160, 320, "U1  SN74AHCT125N", "Pin 14 = 5V_LOGIC\nPin 7 = GND\n\nPin 2   A1 <- GP6\nPin 3   Y1 -> left servo\nPin 5   A2 <- GP7\nPin 6   Y2 -> right servo\nPin 9   A3 <- GP8\nPin 8   Y3 -> left ESC\nPin 12  A4 <- GP9\nPin 11  Y4 -> right ESC\n\nEach A pin: 10k pull-down to GND\nEach Y pin: 220 ohm series + 10k pull-down to GND\n0.1uF next to pins 14/7", BLUE, PANEL, 11, 8.5)
    box(c, 665, 314, 145, 141, "Q1  Hardware enable", "U1 pins 1/4/10/13 tied as OE_N\nOE_N -- R11 10k -> 5V\nQ1 collector -> OE_N\nQ1 emitter -> GND\nGP2 -- R2 4.7k -> base\nBase -- R12 10k -> GND\n\nGP2 high: outputs allowed\nReset/power loss: outputs off", RED, HexColor("#fff1f1"), 10, 8)
    box(c, 665, 139, 145, 122, "J_OUT  Four outputs", "S-L: left servo PWM/5V/GND\nS-R: right servo PWM/5V/GND\nESC-L: PWM/GND (red wire cut)\nESC-R: PWM/GND (red wire cut)\n\nPWM start: 50Hz\nESC: 1000-2000us", ORANGE, HexColor("#fff4ea"), 10, 8)
    arrow(c, 198, 392, 246, 392, BLUE, "UART0", 222, 404)
    arrow(c, 198, 213, 246, 213, BLUE, "I2C0 + INT", 222, 225)
    arrow(c, 416, 392, 461, 392, BLUE, "GP1", 438, 404)
    arrow(c, 416, 213, 461, 213, BLUE, "GP3/4/5", 438, 225)
    arrow(c, 198, 300, 461, 300, BLUE, "GP6/7/8/9", 330, 312)
    text(c, 212, 466, "GP2 -> R2 -> Q1 base", 8, RED)
    arrow(c, 621, 370, 665, 370, RED, "OE_N", 643, 382)
    arrow(c, 621, 218, 665, 218, BLUE, "Four PWM", 643, 230)
    text(c, 30, 78, "Fail-safe logic: OE_N of U1 is pulled up to 5V by a 10k resistor; only when Pico GP2 is high and Q1 conducts is OE_N pulled low.\nTherefore, whenever the Pico has not started, is reset, loses power, or the firmware deliberately drives GP2 low, U1 is high-impedance and the four outputs are pulled to GND by 10k resistors.", 9.5, INK, 775)
    footer(c)


def table(c, x, y, cols, rows, widths, row_h=28, font_size=7.8):
    c.setStrokeColor(LINE)
    c.setFillColor(HexColor("#dcecf2"))
    c.rect(x, y-row_h, sum(widths), row_h, stroke=1, fill=1)
    xx=x
    for i, col in enumerate(cols):
        text(c, xx+4, y-18, col, font_size, INK, widths[i]-8)
        xx += widths[i]
    yy=y-row_h
    for ri, row in enumerate(rows):
        c.setFillColor(white if ri%2==0 else HexColor("#f6fafc"))
        c.rect(x, yy-row_h, sum(widths), row_h, stroke=1, fill=1)
        xx=x
        for i, cell in enumerate(row):
            c.setStrokeColor(LINE)
            c.line(xx, yy, xx, yy-row_h)
            text(c, xx+4, yy-14, cell, font_size, INK, widths[i]-8, font_size*1.15)
            xx += widths[i]
        c.line(x+sum(widths), yy, x+sum(widths), yy-row_h)
        yy -= row_h
    return yy


def page3(c):
    header(c, "Harness, connectors and perfboard layout", "Every PWM line is routed as a pair with a GND lead; power leads never enter the perfboard", 3)
    rows = [
        ("J1", "XT30", "BATT+ / BATT-", "2S battery input, power star point"),
        ("J2 / J3", "2-pin power + 2-pin signal", "ESC-L / ESC-R", "Power wired straight to the PDB; signal is PWM+GND only"),
        ("J4", "2-pin", "UBEC-IN", "To the PDB, short input leads"),
        ("J5", "2-pin", "UBEC-OUT", "To 5V_STAR"),
        ("J6", "4-pin", "RP1", "5V / GND / TX / RX"),
        ("J7", "5-pin", "MPU6050", "3V3 / GND / SDA / SCL / INT"),
        ("J8 / J9", "3-pin servo", "Left / right servo", "SIG / 5V / GND"),
        ("J10 / J11", "3-pin shell, 2 pins used", "Left / right ESC signal", "SIG / unused / GND; red wire not connected"),
    ]
    text(c, 35, 510, "Connector definitions", 13, INK)
    table(c, 35, 497, ["ID", "Suggested connector", "Connects to", "Pins and notes"], rows, [70, 145, 135, 410], 30, 8)
    box(c, 35, 74, 370, 100, "Perfboard physical layout", "Left: 5V/GND input, C2 470uF, C3 0.1uF.\nCenter: Pico socket. Beside the Pico: U2 and the RP1 socket.\nRight: U1, Q1, R2/R11/R12 and the four PWM output headers.\n5V and GND each use one continuous tinned copper bus wire; the MPU6050 does not sit on the perfboard - mount it separately near the center of gravity.", BLUE, PANEL, 10, 8.3)
    box(c, 430, 74, 372, 100, "Harness and interference control", "Battery to ESC: short, thick, parallel; when relocation is needed, extend the three motor phase wires first.\nPWM: twist each signal with its GND or run them side by side.\nRP1 antenna: at least 30mm from the UBEC, ESCs, motors and carbon rods; keep the two antennas as close to 90 degrees as possible.\nMPU6050: away from power leads and the UBEC; its axes must be parallel to the airframe axes.", TEAL, HexColor("#edfbfb"), 10, 8.3)
    footer(c)


def page4(c):
    header(c, "BOM, power-up sequence and acceptance conditions", "Verify the lockout first, then the outputs, and only last the power path", 4)
    bom = [
        ("U0", "Raspberry Pi Pico 2", "1", "Headerless version saves mass; 5V into VSYS"),
        ("U1", "SN74AHCT125N DIP-14", "1", "5V PWM output buffer; second unit as spare"),
        ("U2", "SN74LVC1G17DBV + SOT23-to-DIP adapter", "1", "RP1 TX input protection, 3.3V supply"),
        ("Q1", "2N3904 or S8050 NPN", "1", "Hardware enable switch for U1"),
        ("C1,C2", "470uF / 10V low-ESR", "2", "Servo star point, logic board entry"),
        ("C3,C5,C6,near U2", "0.1uF ceramic", "4", "Close to the respective chip/module supply pins"),
        ("C4", "10uF / 25V X7R", "1", "Next to the MPU6050"),
        ("R1", "1k", "1", "Pico GP0 -> RP1 RX"),
        ("R2,R17,R18", "4.7k", "3", "Q1 base; use R17/R18 when I2C pull-ups are missing"),
        ("R3-R6", "220 ohm", "4", "Series resistors in the four PWM lines"),
        ("R7-R16", "10k", "10", "U1 input/output state and enable protection"),
    ]
    text(c, 35, 510, "Added small-parts BOM", 13, INK)
    table(c, 35, 497, ["Ref", "Part", "Qty", "Purpose"], bom, [80, 270, 65, 345], 27, 7.8)
    text(c, 35, 145, "First power-up acceptance sequence", 13, INK)
    steps = [
        "1. Do not connect the Pico, receiver, IMU, servos or ESCs. Verify with a multimeter that 5V-GND, 3V3-GND and BATT+-BATT- show no shorts.",
        "2. From a current-limited supply, feed the UBEC at 7.4V, 0.2A. Confirm the UBEC output is 4.75-5.25V; the Pico 3V3 rail is 3.20-3.35V.",
        "3. Plug in the Pico without running output firmware: measure OE_N at about 5V and all four U1 Y pins at about 0V. Stop all further debugging if this step fails.",
        "4. Connect the RP1 and MPU6050; confirm CRSF frames, I2C detection and IMU axis orientation. Then connect the servos one by one and check directions.",
        "5. Connect both ESCs prop-less: calibrate minimum throttle; on radio lost link, receiver unplugged or Pico reset, OE_N must return to about 5V and the motors must stop.",
        "6. Only when 5V stays >= 4.75V and the Pico does not reboot during full-travel dual-servo and low-throttle dual-ESC operation may props be fitted for the powered bench.",
    ]
    yy=126
    for s in steps:
        yy = text(c, 38, yy, s, 8.7, INK, 755, 12)
        yy -= 3
    footer(c)


def svg_box(parts, x, y, w, h, title, body, color):
    body_lines = body.split("\n")
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#f6fafc" stroke="#b9cbd5"/>')
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="8" fill="{color}"/>')
    parts.append(f'<text x="{x+8}" y="{y+17}" class="title">{escape(title)}</text>')
    for i, line in enumerate(body_lines):
        parts.append(f'<text x="{x+8}" y="{y+44+i*15}" class="body">{escape(line)}</text>')


def make_svg():
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="820" viewBox="0 0 1400 820">',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#1677a8"/></marker><style>.title{font:600 18px Arial,Helvetica,sans-serif;fill:#fff}.body{font:15px Arial,Helvetica,sans-serif;fill:#10263b}.label{font:14px Arial,Helvetica,sans-serif;fill:#1677a8}.note{font:16px Arial,Helvetica,sans-serif;fill:#10263b}</style></defs>',
        '<rect width="1400" height="820" fill="#fff"/><rect width="1400" height="78" fill="#10263b"/>',
        '<text x="38" y="46" class="title" style="font-size:28px">SR-71 / 600 V1 Control Circuit Overview E1</text>',
        '<text x="38" y="68" style="font:14px Arial,Helvetica,sans-serif;fill:#c9e6ef">Power, 5V supply and signal lines separated; the four PWM channels shut off in hardware on any Pico fault</text>'
    ]
    svg_box(parts, 45, 290, 170, 100, "B1  2S LiPo / XT30", "7.4V nominal\n18-20AWG main leads", "#d46a1f")
    svg_box(parts, 275, 290, 175, 100, "Power star point PDB", "XT30, dual ESCs, UBEC\nPower current never enters the perfboard", "#d46a1f")
    svg_box(parts, 525, 155, 190, 95, "ESC-L -> Left motor", "2S / conventional PWM\nPower 20-22AWG", "#b43b3b")
    svg_box(parts, 525, 425, 190, 95, "ESC-R -> Right motor", "2S / conventional PWM\nPower 20-22AWG", "#b43b3b")
    svg_box(parts, 525, 290, 190, 95, "5V UBEC", "3A minimum, 5A preferred\nFixed 5V", "#2f8b57")
    svg_box(parts, 790, 290, 175, 95, "5V_STAR", "Servo branch\nLogic branch", "#2f8b57")
    svg_box(parts, 1045, 255, 280, 175, "Control board", "Pico 2\nRP1 -> SN74LVC1G17 -> UART\nMPU6050 -> I2C/INT\nSN74AHCT125 + Q1 hardware enable\nFour PWM outputs", "#1677a8")
    parts += [
        '<line x1="215" y1="340" x2="275" y2="340" stroke="#d46a1f" stroke-width="3" marker-end="url(#arrow)"/>',
        '<line x1="450" y1="335" x2="525" y2="202" stroke="#d46a1f" stroke-width="3" marker-end="url(#arrow)"/>',
        '<line x1="450" y1="345" x2="525" y2="337" stroke="#d46a1f" stroke-width="3" marker-end="url(#arrow)"/>',
        '<line x1="450" y1="355" x2="525" y2="472" stroke="#d46a1f" stroke-width="3" marker-end="url(#arrow)"/>',
        '<line x1="715" y1="337" x2="790" y2="337" stroke="#2f8b57" stroke-width="3" marker-end="url(#arrow)"/>',
        '<line x1="965" y1="337" x2="1045" y2="337" stroke="#2f8b57" stroke-width="3" marker-end="url(#arrow)"/>',
        '<line x1="1045" y1="295" x2="715" y2="220" stroke="#1677a8" stroke-width="2.5" marker-end="url(#arrow)"/>',
        '<line x1="1045" y1="390" x2="715" y2="472" stroke="#1677a8" stroke-width="2.5" marker-end="url(#arrow)"/>',
        '<text x="760" y="210" class="label">PWM + GND</text><text x="760" y="486" class="label">PWM + GND</text>',
        '<rect x="45" y="600" width="1280" height="128" rx="10" fill="#f1fbfb" stroke="#b9cbd5"/>',
        '<text x="65" y="632" class="note">Key fail-safe: OE_N of U1 is pulled up to 5V by 10k; Pico GP2 can pull OE_N low only through Q1.</text>',
        '<text x="65" y="660" class="note">So whenever the Pico resets, loses power, has not started, or the firmware deliberately flags a fault, U1 shuts off, the four outputs are pulled low by 10k, and the ESCs receive no throttle pulses.</text>',
        '<text x="65" y="703" class="note">Capacitors: 470uF/10V low-ESR at the servo star point; 470uF/10V low-ESR + 0.1uF at the logic entry; 10uF/25V + 0.1uF next to the MPU6050.</text>',
        '</svg>'
    ]
    SVG.write_text("\n".join(parts), encoding="utf-8")


def main():
    PDF.parent.mkdir(parents=True, exist_ok=True)
    SVG.parent.mkdir(parents=True, exist_ok=True)
    make_svg()
    c = canvas.Canvas(str(PDF), pagesize=(W, H))
    setup(c)
    for draw in (page1, page2, page3, page4):
        draw(c)
        c.showPage()
    c.save()
    print(PDF)
    print(SVG)


if __name__ == "__main__":
    main()
