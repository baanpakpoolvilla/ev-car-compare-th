#!/usr/bin/env python3
"""EV Comparison PDF - รถไฟฟ้าราคาไม่เกิน 600,000 บาท  (Light Theme)"""

import os, io, urllib.request
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, HRFlowable, PageBreak,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus.flowables import Flowable

# ─── Fonts ────────────────────────────────────────────────────────────────────
FONT_DIR = os.path.expanduser("~/Library/Fonts")
pdfmetrics.registerFont(TTFont("Sara",    f"{FONT_DIR}/Sarabun-Regular.ttf"))
pdfmetrics.registerFont(TTFont("SaraB",   f"{FONT_DIR}/Sarabun-Bold.ttf"))
pdfmetrics.registerFont(TTFont("SaraSB",  f"{FONT_DIR}/Sarabun-SemiBold.ttf"))
pdfmetrics.registerFont(TTFont("SaraMd",  f"{FONT_DIR}/Sarabun-Medium.ttf"))
pdfmetrics.registerFont(TTFont("SaraLt",  f"{FONT_DIR}/Sarabun-Light.ttf"))

# ─── AI Easy Pro Brand ───────────────────────────────────────────────────────
AEP_NAVY    = colors.HexColor("#0B1F3A")
AEP_ACCENT  = colors.HexColor("#2F80ED")
AEP_LIGHT   = colors.HexColor("#7EB8F7")
AEP_WHITE   = colors.white
AEP_NAME    = "AI Easy Pro"
AEP_TAGLINE = "AI ง่ายๆแบบมือโปร"
AEP_LINE    = "@117jyivt"
AEP_WEB     = "aieasypro.com"
AEP_TEL     = "093-225-3253"

# ─── Light Color Palette ──────────────────────────────────────────────────────
C_BG       = colors.white
C_SURFACE  = colors.HexColor("#F4F6FA")
C_CARD     = colors.HexColor("#EBF0F8")
C_BORDER   = colors.HexColor("#CBD5E1")

C_TEXT     = colors.HexColor("#1E293B")   # body text
C_DARK     = colors.HexColor("#0F172A")   # headings
C_GRAY     = colors.HexColor("#64748B")   # labels/meta
C_LGRAY    = colors.HexColor("#94A3B8")   # very light text

C_BLUE     = colors.HexColor("#1D4ED8")   # accent headers
C_BLUE2    = colors.HexColor("#2563EB")   # links / secondary
C_NAVY     = colors.HexColor("#1E3A5F")   # header bars on white

C_GREEN    = colors.HexColor("#15803D")
C_GREEN_BG = colors.HexColor("#DCFCE7")
C_RED      = colors.HexColor("#DC2626")
C_RED_BG   = colors.HexColor("#FEE2E2")
C_AMBER    = colors.HexColor("#B45309")
C_AMBER_BG = colors.HexColor("#FEF3C7")
C_BLUE_BG  = colors.HexColor("#DBEAFE")

C_CAR = {
    "BYD Atto 1":   colors.HexColor("#1D4ED8"),
    "Geely EX2":    colors.HexColor("#15803D"),
    "BYD Dolphin":  colors.HexColor("#0369A1"),
    "MG4 Electric": colors.HexColor("#9B1C1C"),
}
C_CAR_LIGHT = {
    "BYD Atto 1":   colors.HexColor("#DBEAFE"),
    "Geely EX2":    colors.HexColor("#DCFCE7"),
    "BYD Dolphin":  colors.HexColor("#E0F2FE"),
    "MG4 Electric": colors.HexColor("#FEE2E2"),
}

W, H = A4

# ─── Logo helpers ─────────────────────────────────────────────────────────────
def draw_logo_canvas(c, x, y, box_size=18, gap=4):
    """Draw AI Easy Pro logo mark directly on a ReportLab canvas at (x, y)."""
    r = box_size * (8 / 28)
    c.saveState()
    c.setFillColor(AEP_ACCENT)
    c.roundRect(x, y, box_size, box_size, r, fill=1, stroke=0)
    c.setFillColor(AEP_WHITE)
    c.setFont("SaraB", box_size * 0.52)
    c.drawCentredString(x + box_size / 2, y + box_size * 0.22, "AI")
    tx = x + box_size + gap
    c.setFillColor(AEP_NAVY)
    c.setFont("SaraB", box_size * 0.62)
    c.drawString(tx, y + box_size * 0.22, "Easy Pro")
    c.restoreState()

class AepLogoFlowable(Flowable):
    """Inline flowable version of the AI Easy Pro logo mark."""
    def __init__(self, box_size=22, with_tagline=True):
        super().__init__()
        self.box_size = box_size
        self.with_tagline = with_tagline
        self._w = box_size * 5.5
        self._h = box_size + (box_size * 0.5 if with_tagline else 0)
        self.width  = self._w
        self.height = self._h

    def draw(self):
        bs = self.box_size
        r  = bs * (8 / 28)
        c  = self.canv
        c.saveState()
        # blue rounded box
        c.setFillColor(AEP_ACCENT)
        c.roundRect(0, self._h - bs, bs, bs, r, fill=1, stroke=0)
        # "AI" inside box
        c.setFillColor(AEP_WHITE)
        c.setFont("SaraB", bs * 0.52)
        c.drawCentredString(bs / 2, self._h - bs + bs * 0.22, "AI")
        # "Easy Pro" beside box
        gap = bs * 0.28
        c.setFillColor(AEP_NAVY)
        c.setFont("SaraB", bs * 0.65)
        c.drawString(bs + gap, self._h - bs + bs * 0.22, "Easy Pro")
        # tagline below
        if self.with_tagline:
            c.setFillColor(colors.HexColor("#64748B"))
            c.setFont("Sara", bs * 0.42)
            c.drawString(0, self._h - bs - bs * 0.35, AEP_TAGLINE)
        c.restoreState()

# ─── Style helper ─────────────────────────────────────────────────────────────
def S(name, font="Sara", size=11, color=C_TEXT, align=TA_LEFT, leading=None):
    return ParagraphStyle(
        name, fontName=font, fontSize=size, textColor=color,
        alignment=align, leading=leading or size * 1.5, wordWrap="CJK",
    )

sTitle   = S("Title",   "SaraB",  30, C_DARK,  TA_CENTER, 38)
sSub     = S("Sub",     "SaraMd", 13, C_GRAY,  TA_CENTER, 20)
sH1      = S("H1",      "SaraB",  18, C_BLUE,  TA_LEFT,   24)
sH2      = S("H2",      "SaraB",  12, C_DARK,  TA_LEFT,   18)
sBody    = S("Body",    "Sara",   10, C_TEXT,  TA_LEFT,   16)
sBodySm  = S("BodySm",  "Sara",    9, C_GRAY,  TA_LEFT,   14)
sCell    = S("Cell",    "Sara",    9, C_TEXT,  TA_CENTER, 13)
sCellB   = S("CellB",   "SaraB",   9, C_DARK,  TA_CENTER, 13)
sCellL   = S("CellL",   "SaraSB",  9, C_GRAY,  TA_LEFT,   13)
sCellBL  = S("CellBL",  "SaraB",  10, C_DARK,  TA_LEFT,   14)
sLabel   = S("Label",   "SaraSB",  8, C_BLUE,  TA_LEFT,   12)
sSmall   = S("Small",   "Sara",    8, C_GRAY,  TA_LEFT,   12)
sPrice   = S("Price",   "SaraB",  14, C_AMBER, TA_LEFT,   20)
sPriceSm = S("PriceSm", "SaraB",  11, C_AMBER, TA_CENTER, 16)
sGreen   = S("Green",   "SaraB",   9, C_GREEN, TA_LEFT,   13)
sRed     = S("Red",     "SaraB",   9, C_RED,   TA_LEFT,   13)
sBlue    = S("Blue",    "SaraB",   9, C_BLUE2, TA_LEFT,   13)

# ─── Installment calculator ───────────────────────────────────────────────────
def calc_payment(price, down_pct, rate_flat, months):
    principal = price * (1 - down_pct)
    years = months / 12
    total = principal * (1 + rate_flat * years)
    return round(total / months)

def min_salary(payment, ratio=0.35):
    return round(payment / ratio / 1000) * 1000

# ─── Image downloader ─────────────────────────────────────────────────────────
def try_image(url, w, h):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=10).read()
        buf = io.BytesIO(data)
        img = RLImage(buf)
        iw, ih = img.imageWidth, img.imageHeight
        aspect = iw / ih
        fw = min(w, h * aspect)
        fh = fw / aspect
        img._restrictSize(fw, fh)
        return img
    except Exception:
        return None

# ─── Car Data ─────────────────────────────────────────────────────────────────
CARS = [
    {
        "name":    "BYD Atto 1",
        "brand":   "BYD",
        "segment": "Hatchback ขนาดเล็ก (B-Segment)",
        "price_low":  429900,
        "price_high": 459900,
        "price_rep":  429900,   # representative price for installment calc
        "variants": ["Dynamic 429,900 บาท  |  แบต 30 kWh  |  300 กม. NEDC",
                     "Premium 459,900 บาท  |  แบต 38.9 kWh  |  380 กม. NEDC"],
        "image_urls": [
            "https://www.headlightmag.com/hlmwp/wp-content/uploads/2026/03/ATTO_1_Exterior_4.jpg",
            "https://www.headlightmag.com/hlmwp/wp-content/uploads/2026/03/ATTO_1_Exterior_1.jpg",
        ],
        "specs": [
            ("แบตเตอรี่",     "30.08 / 38.88 kWh (Blade LFP)"),
            ("ระยะทาง NEDC",  "300 / 380 กม."),
            ("ระยะทาง WLTP",  "240 / 304 กม."),
            ("มอเตอร์",       "55 kW (75 PS)  |  135 Nm"),
            ("ขับเคลื่อน",    "FWD (ล้อหน้า)"),
            ("ความเร็วสูงสุด","150 กม./ชม."),
            ("ชาร์จ AC",      "6.6 kW"),
            ("ชาร์จ DC",      "30 kW (Dynamic) / 40 kW (Premium)"),
            ("ขนาดรถ",        "3,925 × 1,720 × 1,590 มม."),
            ("ฐานล้อ",        "2,500 มม."),
            ("รับประกันรถ",   "6 ปี / 150,000 กม."),
            ("รับประกันแบต",  "8 ปี / 150,000 กม."),
        ],
        "pros": [
            "ราคาเริ่มต้นต่ำสุดในกลุ่ม (429,900 บาท)",
            "Blade Battery (LFP) ปลอดภัย — ไม่ลุก ไม่ระเบิด",
            "ขนาดกะทัดรัด จอดง่าย เหมาะใช้เมือง",
            "รับประกันรถ 6 ปี ยาวที่สุดในงบนี้",
            "ศูนย์ BYD กระจายทั่วประเทศ",
        ],
        "cons": [
            "กำลังต่ำสุดในกลุ่ม (75 PS) — ไม่เร้าใจ",
            "ชาร์จ DC ช้าสุด (30-40 kW)",
            "ห้องหลังคับสำหรับผู้ใหญ่ตัวสูง",
            "ระยะทางจริง Dynamic ~240 กม. (ขับออกต่างจังหวัดลำบาก)",
        ],
        "for_who": "คนเมือง / งบน้อย / รถคันแรก / ขับเข้าออฟฟิศทุกวัน",
    },
    {
        "name":    "Geely EX2",
        "brand":   "Geely",
        "segment": "Hatchback ขนาดกลาง (B/C-Segment)",
        "price_low":  429990,
        "price_high": 459990,
        "price_rep":  429990,
        "variants": ["Pro 429,990 บาท  |  แบต 39.4 kWh  |  395 กม. NEDC",
                     "Max 459,990 บาท  |  แบต 39.4 kWh  |  อุปกรณ์ครบกว่า"],
        "image_urls": [
            "https://www.headlightmag.com/hlmwp/wp-content/uploads/2025/11/Geely-EX2-Exterior-1.jpg",
            "https://www.headlightmag.com/hlmwp/wp-content/uploads/2025/11/Geely-EX2-Exterior-2-1.jpg",
        ],
        "specs": [
            ("แบตเตอรี่",     "39.4 kWh (LFP)"),
            ("ระยะทาง NEDC",  "395 กม."),
            ("ระยะทาง WLTP",  "325 กม."),
            ("มอเตอร์",       "86 kW (116 PS)  |  150 Nm"),
            ("ขับเคลื่อน",    "RWD (ล้อหลัง) ★"),
            ("0–100 กม./ชม.", "11.0 วินาที"),
            ("ความเร็วสูงสุด","130 กม./ชม."),
            ("ชาร์จ AC",      "6.6 kW"),
            ("ชาร์จ DC",      "70 kW (30→80% ใน ~25 นาที) ★"),
            ("ขนาดรถ",        "4,135 × 1,850 × 1,580 มม."),
            ("ฐานล้อ",        "2,650 มม."),
            ("รับประกันรถ",   "6 ปี / 150,000 กม."),
            ("รับประกันแบต",  "8 ปี / 150,000 กม."),
        ],
        "pros": [
            "ชาร์จ DC เร็วที่สุดในราคา ~430k (70 kW, 25 นาที 30→80%)",
            "RWD ขับสนุก พวงมาลัยตอบสนองดีกว่า FWD ราคาเดียวกัน",
            "ตัวถังกว้างที่สุดในกลุ่ม (1,850 มม.) นั่งสบาย",
            "ระยะทาง WLTP ดีสุดในราคาใต้ 460k",
            "รับประกันรถ 6 ปี / แบต 8 ปี",
        ],
        "cons": [
            "ศูนย์บริการ Geely ยังน้อยกว่า BYD/MG",
            "ความเร็วสูงสุดจำกัด 130 กม./ชม.",
            "Resale value ยังไม่มีข้อมูลระยะยาว (แบรนด์ใหม่ในไทย)",
            "อะไหล่เฉพาะทางหายากกว่า",
        ],
        "for_who": "ต้องการสเปคดีที่สุดในงบ ~430k / ชาร์จเร็ว / ขับสนุก",
    },
    {
        "name":    "BYD Dolphin",
        "brand":   "BYD",
        "segment": "Hatchback ขนาดกลาง (C-Segment)",
        "price_low":  549900,
        "price_high": 599900,
        "price_rep":  549900,
        "variants": ["Standard 549,900 บาท  |  แบต 50.25 kWh  |  435 กม. NEDC",
                     "Extended 599,900 บาท  |  แบต 60.48 kWh  |  490 กม. NEDC  |  204 PS"],
        "image_urls": [
            "https://www.9carthai.com/wp-content/uploads/2023/07/BYD-DOLPHIN-2-1.jpg",
            "https://www.9carthai.com/wp-content/uploads/2023/07/BYD-DOLPHIN-4.jpg",
        ],
        "specs": [
            ("แบตเตอรี่",     "50.25 / 60.48 kWh (Blade LFP)"),
            ("ระยะทาง NEDC",  "435 / 490 กม."),
            ("ระยะทาง WLTP",  "~340 / ~400 กม."),
            ("มอเตอร์",       "70 kW (95 PS) / 180 Nm  |  Extended: 150 kW (204 PS) / 310 Nm"),
            ("ขับเคลื่อน",    "FWD (ล้อหน้า)"),
            ("0–100 กม./ชม.", "12.3 วินาที (Standard)"),
            ("ความเร็วสูงสุด","160 กม./ชม."),
            ("ชาร์จ AC",      "6.6 kW"),
            ("ชาร์จ DC",      "30 kW (Standard) / 60 kW (Extended)"),
            ("ขนาดรถ",        "4,290 × 1,770 × 1,570 มม."),
            ("ฐานล้อ",        "2,700 มม."),
            ("รับประกันรถ",   "8 ปี / 160,000 กม. ★"),
            ("รับประกันแบต",  "ตลอดชีพ (Lifetime Warranty) ★★"),
        ],
        "pros": [
            "รับประกันแบตเตอรี่ตลอดชีพ — ไม่มีรุ่นอื่นในกลุ่มนี้ทำได้",
            "รับประกันรถยาวสุด 8 ปี / 160,000 กม.",
            "ห้องโดยสารกว้างที่สุด ฐานล้อ 2,700 มม.",
            "Extended 204 PS / 310 Nm — แรงมาก",
            "ประกอบในไทย — มีสิทธิ์ EV3.5 Subsidy 50,000 บาท",
        ],
        "cons": [
            "Standard ชาร์จ DC ช้า 30 kW — รอนาน",
            "Standard กำลังต่ำ 95 PS — ไม่สนุก",
            "FWD ทั้งสองรุ่น",
            "ราคาปกติ 549,900 — แพงที่สุดในกลุ่มเดียวกัน",
        ],
        "for_who": "ครอบครัว / เดินทางไกลบ่อย / ต้องการรับประกันยาวนาน / ใช้ยาว 8+ ปี",
    },
    {
        "name":    "MG4 Electric",
        "brand":   "MG",
        "segment": "Hatchback สปอร์ต (C-Segment)",
        "price_low":  579900,
        "price_high": 579900,
        "price_rep":  579900,
        "variants": ["D Standard Range 579,900 บาท  |  แบต 50 kWh  |  170 PS  |  120 kW DC"],
        "image_urls": [
            "https://www.headlightmag.com/hlmwp/wp-content/uploads/2026/03/MG-4-MY2026-Exterior-2.jpg",
            "https://www.headlightmag.com/hlmwp/wp-content/uploads/2026/03/MG-4-MY2026-Exterior-1.jpg",
        ],
        "specs": [
            ("แบตเตอรี่",     "50 kWh LFP (CATL)"),
            ("ระยะทาง NEDC",  "450 กม."),
            ("ระยะทาง WLTP",  "~380 กม."),
            ("มอเตอร์",       "125 kW (170 PS)  |  250 Nm ★"),
            ("ขับเคลื่อน",    "RWD (ล้อหลัง) ★"),
            ("ความเร็วสูงสุด","170 กม./ชม. ★"),
            ("ชาร์จ AC",      "6.6 kW"),
            ("ชาร์จ DC",      "120 kW (เร็วที่สุดในกลุ่ม) ★★"),
            ("ขนาดรถ",        "4,287 × 1,836 × 1,504 มม."),
            ("ฐานล้อ",        "2,705 มม."),
            ("รับประกันรถ",   "4 ปี / 120,000 กม."),
            ("รับประกันแบต",  "ตลอดชีพ (Lifetime) ★★"),
            ("รับประกันมอเตอร์","ตลอดชีพ (Lifetime) ★★"),
        ],
        "pros": [
            "ชาร์จ DC เร็วที่สุด 120 kW — 20-25 นาทีเต็ม",
            "RWD + 170 PS — ขับสนุกที่สุดในกลุ่ม",
            "ความเร็วสูงสุด 170 กม./ชม.",
            "รับประกันแบต+มอเตอร์ตลอดชีพ",
            "ประกอบในไทย — สิทธิ์ EV3.5 Subsidy 50,000 บาท",
        ],
        "cons": [
            "แพงที่สุดในกลุ่ม (579,900 บาท) มีรุ่นเดียวใต้ 600k",
            "รับประกันตัวรถสั้นที่สุด 4 ปี / 120,000 กม.",
            "ท้ายรถค่อนข้างเล็ก (ทรง coupe-like)",
            "Long Range 699,900 บาท เกินงบ 100k",
        ],
        "for_who": "ชอบขับสนุก / เดินทางระหว่างเมือง / ต้องการชาร์จเร็ว / สมรรถนะสูง",
    },
]

# ─── Installment scenarios ────────────────────────────────────────────────────
RATE_PROMO  = 0.0199   # 1.99% flat/year  (EV promo / งาน Motor Show/Expo)
RATE_NORMAL = 0.0299   # 2.99% flat/year  (ปกติทั่วไป)
DOWN_PCTS   = [0.10, 0.20, 0.30]
DOWN_LABELS = ["ดาวน์ 10%", "ดาวน์ 20%", "ดาวน์ 30%"]
MONTHS_LIST = [60, 72, 84]
MONTH_LABELS = ["60 เดือน (5 ปี)", "72 เดือน (6 ปี)", "84 เดือน (7 ปี)"]

# ─── Best Time to Buy ─────────────────────────────────────────────────────────
BUY_TIMING = [
    {
        "period": "Motor Expo  (ปลาย พ.ย. – ต้น ธ.ค.)",
        "rating": "★★★★★  ดีที่สุด",
        "clr_hdr": C_GREEN, "clr_bg": C_GREEN_BG,
        "detail": [
            "ลดราคาตรง 30,000–120,000 บาท",
            "ดอกเบี้ย 0% หรือ 1.99% ระยะนานสุด (36–60 เดือน)",
            "ของแถม: Home Charger ฟรีติดตั้ง + ประกันชั้น 1 ปีแรก",
            "ตัวแทนแข่งกันดุ — ยื่นข้อเสนอระหว่างบูธได้เพิ่ม",
        ],
    },
    {
        "period": "Thailand Motor Show  (มี.ค. – เม.ย.)",
        "rating": "★★★★☆  ดีมาก",
        "clr_hdr": C_BLUE2, "clr_bg": C_BLUE_BG,
        "detail": [
            "เปิดตัวรุ่นใหม่ — โปรแรงดึงลูกค้า",
            "ลดราคา 20,000–80,000 บาท",
            "Motor Show 2026: BYD Dolphin ลดถึง 120,000 บาท",
            "มักมีสีพิเศษ / รุ่น Limited Edition",
        ],
    },
    {
        "period": "สิ้นปี ธ.ค. (นอกงาน)",
        "rating": "★★★☆☆  ดี",
        "clr_hdr": C_AMBER, "clr_bg": C_AMBER_BG,
        "detail": [
            "ตัวแทนล้างสต็อก — ต่อของแถมได้ดี",
            "ไม่มีส่วนลดตรง แต่เจรจา Accessory Pack ได้",
            "เหมาะถ้าพลาดงาน Motor Expo",
        ],
    },
    {
        "period": "ต้นปี ม.ค. – ก.พ.",
        "rating": "★★☆☆☆  พอได้",
        "clr_hdr": C_RED, "clr_bg": C_RED_BG,
        "detail": [
            "หลัง Motor Expo โปรจางลง",
            "บางค่ายปรับราคาขึ้นต้นปี (Geely EX2 +30k บาท ม.ค. 2026)",
            "รอ Motor Show ดีกว่า ถ้ายังไม่ด่วน",
        ],
    },
]

# ─── Additional Costs ─────────────────────────────────────────────────────────
EXTRA_COSTS = [
    ("Wallbox (ชาร์จเร็วที่บ้าน 7.4 kW)",   "5,000–15,000 บาท",   "ขึ้นกับระยะสาย/ตู้ไฟ"),
    ("ประกันภัยชั้น 1 (ปีที่ 2+)",            "8,000–18,000 บาท/ปี","EV ยังแพงกว่าสันดาป ~20–30%"),
    ("พ.ร.บ.",                                  "600–900 บาท/ปี",     "ถูกกว่าสันดาป"),
    ("ภาษีรถยนต์ประจำปี",                      "300–800 บาท/ปี",     "EV ลดหย่อนภาษีประจำปี"),
    ("เปลี่ยนยาง (ทุก 3–5 ปี)",               "8,000–15,000 บาท",   "สึกเร็วกว่าสันดาปเพราะแรงบิดทันที"),
    ("บำรุงรักษาประจำปี",                      "2,000–5,000 บาท",    "ไม่มีน้ำมันเครื่อง แต่มีน้ำมันเบรก/หล่อลื่น"),
    ("ค่าไฟชาร์จที่บ้าน (TOU กลางคืน)",      "~200 บาท/เดือน",     "วิ่ง 1,000 กม./เดือน ประหยัดกว่าน้ำมัน 4–6 เท่า"),
]

# ─── EV vs ICE Comparison Data ───────────────────────────────────────────────

# ค่าพลังงาน/กม.
ENERGY_COMPARE = [
    # (fuel_type, price_per_unit, unit, consumption, cost_per_km, note)
    ("แก๊สโซฮอล 95 (EV เทียบ)",  "42–44 บาท/ลิตร",  "12–15 กม./ลิตร", "2.8–3.7",  "สันดาป City Car"),
    ("ดีเซล",                       "38–40 บาท/ลิตร",  "14–16 กม./ลิตร", "2.4–2.8",  "สันดาป SUV/Pickup"),
    ("EV — ชาร์จบ้าน (TOU กลางคืน)", "~2.0 บาท/kWh",  "15–18 kWh/100 กม.", "0.3–0.4",  "ถูกสุด — ชาร์จหลัง 22.00"),
    ("EV — ชาร์จบ้าน (ปกติ)",      "~3.95 บาท/kWh",  "15–18 kWh/100 กม.", "0.6–0.8",  "ค่าไฟบ้านอัตราปกติ"),
    ("EV — ชาร์จ DC สาธารณะ",      "7–9 บาท/kWh",    "15–18 kWh/100 กม.", "1.2–1.6",  "สถานีชาร์จ EA/PTT/Evolt"),
]

# ประมาณการค่าใช้จ่ายต่อปี (วิ่ง 15,000 กม./ปี)
KM_PER_YEAR = 15000
ANNUAL_COMPARE = [
    ("รถน้ำมัน (Eco Car ขนาดเดียวกัน)",  3.0,  KM_PER_YEAR, "ค่าน้ำมัน อัตรา 3.0 บาท/กม."),
    ("EV ชาร์จบ้าน TOU กลางคืน",          0.35, KM_PER_YEAR, "อัตรา ~2 บาท/kWh หลัง 22.00"),
    ("EV ชาร์จบ้านปกติ",                   0.70, KM_PER_YEAR, "อัตรา ~3.95 บาท/kWh"),
    ("EV ชาร์จ DC สาธารณะ 50%",            1.4,  KM_PER_YEAR, "ชาร์จบ้าน 50% + สถานี 50%"),
]

# ค่า service เทียบ (ต่อ 10,000 กม. หรือปีละครั้ง)
SERVICE_COMPARE = [
    # (item, ICE, EV, note)
    ("เปลี่ยนถ่ายน้ำมันเครื่อง (5,000-10,000 กม.)", "2,500–4,000 บาท", "ไม่มี ✓",           "EV ไม่มีเครื่องยนต์สันดาป"),
    ("กรองอากาศ / หัวเทียน",                          "500–1,500 บาท",   "ไม่มี ✓",           ""),
    ("น้ำมันเกียร์ / เฟืองท้าย",                      "1,500–3,000 บาท", "ไม่มี / น้อยมาก ✓","EV มีเกียร์เดียว"),
    ("เบรก / ผ้าเบรก",                                "3,000–6,000 บาท", "ถูกกว่า ~50% ✓",   "Regen braking ช่วยยืดอายุ"),
    ("ยาง (สึกเร็วกว่าเพราะแรงบิดทันที)",             "8,000–12,000 บาท","10,000–15,000 บาท ✗","EV สึกเร็วกว่า ~20%"),
    ("ตรวจเช็คตามระยะ (10,000 กม.)",                 "2,000–4,000 บาท", "1,500–3,000 บาท ✓", "EV ตรวจน้อยกว่า"),
    ("ค่าซ่อมใหญ่ (ทุก 50,000 กม.)",                 "5,000–15,000 บาท","น้อย/ไม่มี ✓",      "EV ชิ้นส่วนเคลื่อนไหวน้อยกว่า 90%"),
    ("ค่า service/ปี (รวม)",                           "15,000–35,000 บาท","5,000–12,000 บาท ✓","EV ประหยัดกว่า ~60%"),
]

# 5-year TCO
TCO_ITEMS = [
    # (item, ICE_amt, EV_amt)
    ("ราคารถ (ตัวอย่าง Eco Car vs BYD Atto 1)",        "479,000 บาท", "429,900 บาท"),
    ("ค่าพลังงาน 5 ปี (15,000 กม./ปี บ้าน TOU)",       "225,000 บาท",  "26,250 บาท"),
    ("ค่า service/บำรุงรักษา 5 ปี",                     "75,000–175,000 บาท", "25,000–60,000 บาท"),
    ("ประกันชั้น 1 (ปีที่ 1 แถมฟรีมักมี)",              "18,000–24,000 บาท/ปี", "20,000–30,000 บาท/ปี"),
    ("ค่าติดตั้ง Wallbox (one-time)",                   "ไม่มี",        "5,000–15,000 บาท"),
    ("ประมาณรวม 5 ปี",                                   "~1,100,000–1,250,000 บาท", "~750,000–900,000 บาท"),
    ("ประหยัดกว่าตลอด 5 ปี",                            "—",            "~300,000–450,000 บาท"),
]

# ค่าใช้จ่ายแฝง EV ที่คนมักไม่รู้
HIDDEN_COSTS = [
    ("แบตเตอรี่เสื่อม (ถ้าไม่อยู่ในประกัน)",
     "ราคาแพกแบต BYD ~320,000–378,000 บาท  |  MG4 ~300,000–500,000 บาท",
     "รุ่นที่มี Lifetime Warranty (BYD Dolphin, MG4) ไม่ต้องกังวล"),
    ("Resale Value ลดเร็วกว่า",
     "EV แบรนด์ใหม่ในไทยมูลค่าตกเร็ว ~20–30% ในปีแรก",
     "BYD/MG ดีกว่า Geely เพราะมีฐานลูกค้าใหญ่กว่า"),
    ("ยางสึกเร็วกว่า ~20%",
     "เปลี่ยนยางบ่อยกว่าสันดาป ค่าใช้จ่ายเพิ่ม ~2,000–4,000 บาท/ปี",
     "เลือกยาง EV-rated จะทนกว่า แต่แพงกว่า ~30%"),
    ("ค่าไฟเพิ่มถ้าไม่มี TOU",
     "ชาร์จอัตราปกติ (ไม่ใช้ TOU) จ่ายไฟ ~2 เท่าของอัตรา TOU",
     "ยื่นขอ TOU กับ กฟน./กฟภ. ก่อนใช้รถ"),
    ("ค่าซ่อมอุบัติเหตุแพงกว่า",
     "ชิ้นส่วนตัวถัง EV+เซ็นเซอร์ราคาสูง ค่าซ่อมสูงกว่าสันดาป ~30–40%",
     "ทำให้เบี้ยประกันสูงกว่ารถน้ำมันราคาเดียวกัน"),
    ("ชาร์จสาธารณะช่วง Peak hours",
     "ค่าชาร์จ DC 7–9 บาท/kWh vs บ้าน TOU 2 บาท/kWh — ต่างกัน 4 เท่า",
     "วางแผนชาร์จบ้านเป็นหลัก สาธารณะไว้เสริมเดินทางไกล"),
    ("อะไหล่และช่างเฉพาะทาง",
     "แบรนด์ใหม่ (Geely) อะไหล่อาจรอนาน 2–4 สัปดาห์",
     "BYD/MG มีอะไหล่ดีกว่าเพราะเปิดตลาดไทยนานกว่า"),
]

# ประกันภัย
INSURANCE_DATA = [
    # (model, class1_range, note, color)
    ("BYD Atto 1",   "18,000–24,000 บาท/ปี", "แบรนด์ใหม่ในไทย บางบริษัทยังไม่รับ — ราคาอาจสูงขึ้น",  "BYD Atto 1"),
    ("Geely EX2",    "20,000–25,000 บาท/ปี", "ยังไม่มีราคาทางการ ประมาณจากรุ่นใกล้เคียงราคา",          "Geely EX2"),
    ("BYD Dolphin",  "26,000–30,000 บาท/ปี", "Viriyah 26k · Thanachart 27k · Allianz 28.8k · AXA 30k", "BYD Dolphin"),
    ("MG4 Electric", "18,000–22,000 บาท/ปี", "ประกอบในไทย — บริษัทประกันคุ้นชินมากกว่า ราคาดีกว่า",    "MG4 Electric"),
]

INS_ICE_NOTE = "รถน้ำมัน Eco Car ราคา ~480k ชั้น 1: ~14,000–20,000 บาท/ปี (ถูกกว่า EV ราคาเดียวกัน ~30–50%)"

# ─── Lifestyle Recommendations ────────────────────────────────────────────────
RECS = [
    ("คนเมือง งบน้อย รถคันแรก",              "BYD Atto 1 Dynamic",   "429,900 บาท"),
    ("ชาร์จเร็ว ขับสนุก งบ ~430k",           "Geely EX2 Pro",        "429,990 บาท"),
    ("ครอบครัว รับประกันยาว เดินทางไกล",      "BYD Dolphin Extended", "599,900 บาท"),
    ("สมรรถนะสูง ชาร์จเร็วที่สุด",           "MG4 D Standard",       "579,900 บาท"),
    ("งบ ~460k ต้องการสเปคครบทุกด้าน",       "Geely EX2 Max",        "459,990 บาท"),
]

# ─── PDF Build ────────────────────────────────────────────────────────────────
OUTPUT = os.path.expanduser("~/Desktop/EV_Comparison_600K_2026.pdf")

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=12*mm, bottomMargin=14*mm,
    )
    story = []
    cw = W - 30*mm  # content width

    def page_deco(canvas, doc):
        canvas.saveState()
        # top stripe (navy brand color)
        canvas.setFillColor(AEP_NAVY)
        canvas.rect(0, H - 8*mm, W, 8*mm, fill=1, stroke=0)
        # logo mark in top-left of stripe
        draw_logo_canvas(canvas, 15*mm, H - 6.8*mm, box_size=5.2*mm, gap=1.5*mm)
        # doc title in top stripe (right side)
        canvas.setFont("Sara", 7.5)
        canvas.setFillColor(AEP_LIGHT)
        canvas.drawRightString(W - 15*mm, H - 5.5*mm,
                               "คู่มือเปรียบเทียบรถไฟฟ้าราคาไม่เกิน 600,000 บาท")
        # bottom bar
        canvas.setFillColor(C_SURFACE)
        canvas.rect(0, 0, W, 10*mm, fill=1, stroke=0)
        canvas.setFont("Sara", 8)
        canvas.setFillColor(C_GRAY)
        canvas.drawString(15*mm, 3.5*mm, f"{AEP_WEB}  |  LINE {AEP_LINE}  |  {AEP_TEL}")
        canvas.drawRightString(W - 15*mm, 3.5*mm, f"หน้า {doc.page}")
        canvas.restoreState()

    # ── COVER ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 14*mm))

    # Logo block
    story.append(AepLogoFlowable(box_size=28, with_tagline=True))
    story.append(Spacer(1, 6*mm))

    # Divider
    top_bar = Table([[""]], colWidths=[cw], rowHeights=[3*mm])
    top_bar.setStyle(TableStyle([("BACKGROUND",(0,0),(0,0), AEP_NAVY)]))
    story.append(top_bar)
    story.append(Spacer(1, 6*mm))

    story.append(Paragraph("คู่มือเปรียบเทียบรถไฟฟ้า", sTitle))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph("ราคาไม่เกิน 600,000 บาท", S("T2","SaraB",22,C_NAVY,TA_CENTER,30)))
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(cw, color=C_BORDER, thickness=1, spaceAfter=4*mm))
    story.append(Paragraph("อัปเดต มิถุนายน 2026  |  4 รุ่นเปรียบเทียบ  |  BYD · Geely · MG", sSub))
    story.append(Spacer(1, 8*mm))

    # 2×2 cover cards
    half = cw / 2 - 3*mm
    cover_items = [
        ("BYD Atto 1",   "429,900 บาท", "ถูกที่สุด"),
        ("Geely EX2",    "429,990 บาท", "ชาร์จเร็ว / RWD"),
        ("BYD Dolphin",  "549,900 บาท", "รับประกันดีที่สุด"),
        ("MG4 Electric", "579,900 บาท", "สมรรถนะสูงสุด"),
    ]
    for pair_start in range(0, len(cover_items), 2):
        row_cells = []
        for nm, pr, tag in cover_items[pair_start:pair_start+2]:
            clr  = C_CAR[nm]
            lclr = C_CAR_LIGHT[nm]
            inner = Table([
                [Paragraph(nm,  S(f"CN{nm}","SaraB",13,clr, TA_LEFT,18))],
                [Paragraph(pr,  S(f"CP{nm}","SaraB",16,C_AMBER,TA_LEFT,22))],
                [Paragraph(tag, S(f"CT{nm}","Sara",  9,C_GRAY,TA_LEFT,13))],
            ], colWidths=[half - 8*mm])
            inner.setStyle(TableStyle([
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
            ]))
            card = Table([[inner]], colWidths=[half])
            card.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(0,0), lclr),
                ("TOPPADDING",(0,0),(0,0),6),("BOTTOMPADDING",(0,0),(0,0),6),
                ("LEFTPADDING",(0,0),(0,0),8),("RIGHTPADDING",(0,0),(0,0),8),
                ("LINEBELOW",(0,0),(0,0), 3, clr),
                ("BOX",(0,0),(0,0), 0.5, C_BORDER),
                ("ROUNDEDCORNERS",(0,0),(0,0),5),
            ]))
            row_cells.append(card)
        grid_row = Table([row_cells], colWidths=[half + 3*mm, half + 3*mm])
        grid_row.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
            ("RIGHTPADDING",(0,0),(0,0),3*mm),
            ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),3*mm),
        ]))
        story.append(grid_row)

    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        "รวมข้อมูลสเปค · ราคา · ข้อดี/ข้อด้อย · ตารางผ่อนพนักงานประจำ · ช่วงเวลาซื้อที่ดีที่สุด",
        S("CovNote","Sara",10,C_GRAY,TA_CENTER,16)
    ))
    story.append(PageBreak())

    # ── SPEC COMPARISON TABLE ─────────────────────────────────────────────────
    story.append(Paragraph("ตารางเปรียบเทียบสเปค", sH1))
    story.append(Spacer(1, 3*mm))

    def green_cell(t):  return Paragraph(t, S("gc","SaraB",9,C_GREEN,TA_CENTER,13))
    def blue_cell(t):   return Paragraph(t, S("bc","SaraB",9,C_BLUE2,TA_CENTER,13))
    def amber_cell(t):  return Paragraph(t, S("ac","SaraB",9,C_AMBER,TA_CENTER,13))
    def plain_cell(t):  return Paragraph(t, sCell)

    cws = [cw*0.22, cw*0.195, cw*0.195, cw*0.195, cw*0.195]
    hdr = [Paragraph(t, S("ch","SaraB",9,colors.white,TA_CENTER,13)) for t in
           ["สเปค", "BYD Atto 1", "Geely EX2", "BYD Dolphin", "MG4 Electric"]]

    cmp = [
        hdr,
        [Paragraph("ราคาเริ่มต้น", sCellL),
         amber_cell("429,900"), amber_cell("429,990"), amber_cell("549,900"), amber_cell("579,900")],
        [Paragraph("แบตเตอรี่ (kWh)", sCellL),
         plain_cell("30/38.9"), plain_cell("39.4"), plain_cell("50.3/60.5"), plain_cell("50")],
        [Paragraph("ระยะทาง NEDC (กม.)", sCellL),
         plain_cell("300/380"), plain_cell("395"), green_cell("435/490"), green_cell("450")],
        [Paragraph("ระยะทาง WLTP (กม.)", sCellL),
         plain_cell("240/304"), green_cell("325"), plain_cell("~340"), green_cell("~380")],
        [Paragraph("กำลัง (PS)", sCellL),
         plain_cell("75"), plain_cell("116"), plain_cell("95/204"), green_cell("170")],
        [Paragraph("ขับเคลื่อน", sCellL),
         plain_cell("FWD"), green_cell("RWD ★"), plain_cell("FWD"), green_cell("RWD ★")],
        [Paragraph("ชาร์จ DC สูงสุด (kW)", sCellL),
         plain_cell("30/40"), blue_cell("70 ★"), plain_cell("30/60"), green_cell("120 ★★")],
        [Paragraph("ความเร็วสูงสุด (กม./ชม.)", sCellL),
         plain_cell("150"), plain_cell("130"), plain_cell("160"), green_cell("170 ★")],
        [Paragraph("รับประกันรถ", sCellL),
         blue_cell("6 ปี"), blue_cell("6 ปี"), green_cell("8 ปี ★"), plain_cell("4 ปี")],
        [Paragraph("รับประกันแบต", sCellL),
         plain_cell("8 ปี"), plain_cell("8 ปี"), green_cell("ตลอดชีพ ★★"), green_cell("ตลอดชีพ ★★")],
        [Paragraph("ผลิต/ประกอบ", sCellL),
         plain_cell("นำเข้า"), plain_cell("นำเข้า"),
         blue_cell("ประกอบไทย"), blue_cell("ประกอบไทย")],
    ]

    cmp_tbl = Table(cmp, colWidths=cws, repeatRows=1)
    cmp_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), C_NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_BG, C_SURFACE]),
        ("BACKGROUND",(0,1),(0,-1), C_CARD),
        ("GRID",(0,0),(-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),4), ("RIGHTPADDING",(0,0),(-1,-1),4),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(0,1),(0,-1),"LEFT"),
    ]))
    story.append(cmp_tbl)
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "★ = ดีที่สุดในหมวด  |  ★★ = โดดเด่นมาก  |  ระยะทาง NEDC = เงื่อนไขอุดมคติ (จริง ~75–85%)",
        sSmall
    ))
    story.append(PageBreak())

    # ── INDIVIDUAL CAR PAGES ──────────────────────────────────────────────────
    for car in CARS:
        clr  = C_CAR[car["name"]]
        lclr = C_CAR_LIGHT[car["name"]]

        # Header
        hdr_tbl = Table(
            [[Paragraph(car["name"], S("CH","SaraB",20,colors.white,TA_LEFT,26)),
              Paragraph(f"฿{car['price_low']:,}–{car['price_high']:,}", S("HP","SaraB",14,colors.white,TA_RIGHT,20))]],
            colWidths=[cw*0.6, cw*0.4],
        )
        hdr_tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), clr),
            ("TOPPADDING",(0,0),(-1,-1),7), ("BOTTOMPADDING",(0,0),(-1,-1),7),
            ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("ROUNDEDCORNERS",(0,0),(-1,-1),5),
        ]))
        story.append(hdr_tbl)
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph(car["segment"], sBodySm))
        story.append(Spacer(1, 3*mm))

        # Image + Specs
        img_obj = None
        for url in car["image_urls"]:
            img_obj = try_image(url, 82*mm, 52*mm)
            if img_obj:
                break

        spec_rows = [[Paragraph(k, sCellL), Paragraph(v, S(f"sv{k}","Sara",9,C_TEXT,TA_LEFT,13))]
                     for k, v in car["specs"]]
        spec_tbl = Table(spec_rows, colWidths=[36*mm, cw - 82*mm - 36*mm - 4*mm])
        spec_tbl.setStyle(TableStyle([
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_BG, C_SURFACE]),
            ("GRID",(0,0),(-1,-1), 0.3, C_BORDER),
            ("TOPPADDING",(0,0),(-1,-1),4), ("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LEFTPADDING",(0,0),(-1,-1),4), ("RIGHTPADDING",(0,0),(-1,-1),4),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ]))

        if img_obj:
            left = [img_obj, Spacer(1, 1*mm), Paragraph(car["name"], sSmall)]
        else:
            placeholder = Table([[Paragraph(car["name"], S("ph","SaraMd",11,clr,TA_CENTER,16))]],
                                  colWidths=[82*mm], rowHeights=[52*mm])
            placeholder.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(0,0), lclr),
                ("VALIGN",(0,0),(0,0),"MIDDLE"),
                ("BOX",(0,0),(0,0),0.5,clr),
                ("ROUNDEDCORNERS",(0,0),(0,0),5),
            ]))
            left = [placeholder]

        side = Table([[left, [Paragraph("สเปคหลัก", sH2), Spacer(1,2*mm), spec_tbl]]],
                     colWidths=[86*mm, cw - 86*mm])
        side.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
            ("LEFTPADDING",(1,0),(1,0),4*mm),
        ]))
        story.append(side)
        story.append(Spacer(1, 4*mm))

        # Pros / Cons
        half_pc = cw / 2 - 2*mm
        pros_rows = [[Paragraph("ข้อดี", S("pch","SaraB",10,C_GREEN,TA_LEFT,15))]]
        for p in car["pros"]:
            pros_rows.append([Paragraph(f"+ {p}", S(f"pro{p[:5]}","Sara",9,C_TEXT,TA_LEFT,14))])
        cons_rows = [[Paragraph("ข้อด้อย", S("cch","SaraB",10,C_RED,TA_LEFT,15))]]
        for c in car["cons"]:
            cons_rows.append([Paragraph(f"- {c}", S(f"con{c[:5]}","Sara",9,C_TEXT,TA_LEFT,14))])

        pros_t = Table(pros_rows, colWidths=[half_pc])
        pros_t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(0,0), C_GREEN_BG),
            ("BACKGROUND",(0,1),(0,-1), C_BG),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
            ("LINEAFTER",(0,0),(0,-1), 2, C_GREEN),
            ("BOX",(0,0),(0,-1), 0.4, C_BORDER),
        ]))
        cons_t = Table(cons_rows, colWidths=[half_pc])
        cons_t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(0,0), C_RED_BG),
            ("BACKGROUND",(0,1),(0,-1), C_BG),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
            ("LINEAFTER",(0,0),(0,-1), 2, C_RED),
            ("BOX",(0,0),(0,-1), 0.4, C_BORDER),
        ]))
        pc_tbl = Table([[pros_t, cons_t]], colWidths=[half_pc + 2*mm, half_pc + 2*mm])
        pc_tbl.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
            ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
            ("RIGHTPADDING",(0,0),(0,0),3*mm),
        ]))
        story.append(pc_tbl)
        story.append(Spacer(1, 3*mm))

        # For who
        fw_t = Table(
            [[Paragraph("เหมาะสำหรับ", sLabel), Paragraph(car["for_who"], sBody)]],
            colWidths=[26*mm, cw - 26*mm],
        )
        fw_t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), lclr),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("BOX",(0,0),(-1,-1), 0.5, clr),
            ("ROUNDEDCORNERS",(0,0),(-1,-1),4),
        ]))
        story.append(fw_t)

        # Variants
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph("รุ่นย่อยและราคา", sLabel))
        story.append(Spacer(1, 1*mm))
        vd = [[Paragraph(v, sBody)] for v in car["variants"]]
        vt = Table(vd, colWidths=[cw])
        vt.setStyle(TableStyle([
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_SURFACE, C_BG]),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
            ("BOX",(0,0),(-1,-1),0.4,C_BORDER),
        ]))
        story.append(vt)
        story.append(PageBreak())

    # ── INSTALLMENT PAGE ──────────────────────────────────────────────────────
    story.append(Paragraph("ตารางผ่อนสำหรับพนักงานประจำ", sH1))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "คำนวณจากอัตราดอกเบี้ย Flat Rate  |  โปรโมชั่น 1.99%/ปี  ·  ปกติ 2.99%/ปี  "
        "|  สินเชื่อสูงสุด 95% ของราคารถ  |  ผ่อนได้สูงสุด 84 เดือน",
        sBodySm
    ))
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph(
        "เงินเดือนขั้นต่ำที่แนะนำ = ยอดผ่อน × 3  (ธนาคารส่วนใหญ่กำหนดผ่อนไม่เกิน ~35% ของรายได้)",
        S("inc","Sara",9,C_BLUE,TA_LEFT,13)
    ))
    story.append(Spacer(1, 4*mm))

    for car in CARS:
        clr  = C_CAR[car["name"]]
        lclr = C_CAR_LIGHT[car["name"]]
        price = car["price_rep"]

        story.append(Paragraph(
            f"{car['name']}  —  ราคาอ้างอิง ฿{price:,} บาท",
            S(f"IH{car['name']}","SaraB",11,clr,TA_LEFT,16)
        ))
        story.append(Spacer(1, 1*mm))

        # Build installment table
        # Header row
        inst_hdr = (
            [Paragraph("ดาวน์ / เงินกู้", S("ih","SaraB",8,colors.white,TA_CENTER,12))]
            + [Paragraph(ml, S("ih2","SaraB",8,colors.white,TA_CENTER,12)) for ml in MONTH_LABELS]
            + [Paragraph("เงินเดือนขั้นต่ำ\n(ผ่อน 84 เดือน)", S("ih3","SaraB",8,colors.white,TA_CENTER,12))]
        )
        inst_rows = [inst_hdr]

        for rate_label, rate in [("โปร 1.99%", RATE_PROMO), ("ปกติ 2.99%", RATE_NORMAL)]:
            for down_pct, down_label in zip(DOWN_PCTS, DOWN_LABELS):
                down_amt  = round(price * down_pct / 1000) * 1000
                principal = price - down_amt
                pmts = [calc_payment(price, down_pct, rate, m) for m in MONTHS_LIST]
                min_sal = min_salary(pmts[-1])  # based on 84-month payment

                row = [
                    Paragraph(
                        f"{down_label} ({rate_label})\n"
                        f"ดาวน์ {down_amt:,} บาท  |  กู้ {principal:,} บาท",
                        S(f"dr{down_label}","Sara",8,C_TEXT,TA_LEFT,12)
                    )
                ] + [
                    Paragraph(f"{p:,}", S(f"p{m}","SaraB",9,C_DARK,TA_CENTER,13))
                    for p, m in zip(pmts, MONTHS_LIST)
                ] + [
                    Paragraph(f"{min_sal:,} บาท/เดือน",
                              S("ms","SaraB",9,C_BLUE,TA_CENTER,13))
                ]
                inst_rows.append(row)

        n_cols = 5
        inst_cw_total = cw
        col_widths_inst = [inst_cw_total * 0.30] + [inst_cw_total * 0.155] * 3 + [inst_cw_total * 0.185]

        inst_t = Table(inst_rows, colWidths=col_widths_inst, repeatRows=1)

        # Row background: alternate per rate group (every 3 rows = 1 promo group + 1 normal group)
        inst_t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0), clr),
            # promo rows (rows 1,2,3)
            ("ROWBACKGROUNDS",(0,1),(-1,3),[lclr]),
            # normal rows (rows 4,5,6)
            ("ROWBACKGROUNDS",(0,4),(-1,6),[C_SURFACE]),
            ("GRID",(0,0),(-1,-1), 0.3, C_BORDER),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LINEABOVE",(0,4),(-1,4), 1, clr),  # divider between promo/normal
        ]))
        story.append(inst_t)
        story.append(Spacer(1, 2*mm))
        # EV subsidy note for assembled-in-Thailand models
        if car["name"] in ("BYD Dolphin", "MG4 Electric"):
            story.append(Paragraph(
                f"  รถประกอบในไทย — มีสิทธิ์รับเงินอุดหนุน EV3.5 จำนวน 50,000 บาท "
                f"(หักจากราคาได้ เงินกู้ลดลง ยอดผ่อนจริงต่ำกว่าตาราง ~{calc_payment(price,0.20,RATE_NORMAL,84)-calc_payment(price-50000,0.20,RATE_NORMAL,84):,} บาท/เดือน)",
                S("sub","Sara",8,C_GREEN,TA_LEFT,12)
            ))
        story.append(Spacer(1, 4*mm))

    story.append(Paragraph(
        "หมายเหตุ: ยอดผ่อนเป็นการประมาณด้วย Flat Rate  —  ยอดจริงขึ้นกับธนาคาร เงื่อนไข และ Credit Score  "
        "|  ดาวน์ขั้นต่ำที่ธนาคารรับ 5% ของราคารถ  |  แนะนำดาวน์ 20%+ เพื่อยอดผ่อนสบาย",
        sSmall
    ))
    story.append(PageBreak())

    # ── EV VS ICE ─────────────────────────────────────────────────────────────
    story.append(Paragraph("เปรียบเทียบ EV vs รถน้ำมัน", sH1))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "วิ่ง 15,000 กม./ปี  |  ราคาน้ำมัน 42–44 บาท/ลิตร  |  ค่าไฟบ้าน TOU กลางคืน ~2 บาท/kWh",
        sBodySm
    ))
    story.append(Spacer(1, 4*mm))

    # — ค่าพลังงานต่อ กม. ———————————————————————————————————————————————
    story.append(Paragraph("ค่าพลังงานต่อกิโลเมตร", sH2))
    story.append(Spacer(1, 1*mm))

    eng_hdr = [Paragraph(t, S(f"eh{i}","SaraB",9,colors.white,TA_CENTER,13)) for i, t in
               enumerate(["ประเภท", "ราคา/หน่วย", "อัตราสิ้นเปลือง", "บาท/กม.", "หมายเหตุ"])]
    eng_rows = [eng_hdr]
    for i, (ft, ppu, cons, cpk, note) in enumerate(ENERGY_COMPARE):
        is_ev = "EV" in ft
        cpk_clr = C_GREEN if is_ev else C_RED
        eng_rows.append([
            Paragraph(ft,   S(f"ef{i}","SaraSB" if is_ev else "Sara",9,C_BLUE if is_ev else C_TEXT,TA_LEFT,13)),
            Paragraph(ppu,  sCell),
            Paragraph(cons, sCell),
            Paragraph(cpk,  S(f"ec{i}","SaraB",10,cpk_clr,TA_CENTER,14)),
            Paragraph(note, sSmall),
        ])
    eng_cws = [cw*0.27, cw*0.17, cw*0.18, cw*0.10, cw*0.28]
    eng_t = Table(eng_rows, colWidths=eng_cws, repeatRows=1)
    eng_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), C_NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_BG, C_SURFACE]),
        ("BACKGROUND",(0,3),(- 1,4), C_BLUE_BG),  # EV rows highlight
        ("GRID",(0,0),(-1,-1),0.3,C_BORDER),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(0,1),(0,-1),"LEFT"),
        ("LINEABOVE",(0,3),(- 1,3),1,C_BLUE),  # divider ICE/EV
    ]))
    story.append(eng_t)
    story.append(Spacer(1, 1*mm))
    story.append(Paragraph("EV ชาร์จบ้าน TOU กลางคืน ประหยัดกว่ารถน้ำมัน 7–10 เท่า", S("ev_note","SaraB",9,C_GREEN,TA_LEFT,13)))
    story.append(Spacer(1, 4*mm))

    # — ประมาณการค่าพลังงานต่อปี ————————————————————————————————————————
    story.append(Paragraph(f"ค่าพลังงานต่อปี (วิ่ง {KM_PER_YEAR:,} กม./ปี)", sH2))
    story.append(Spacer(1, 1*mm))

    ann_hdr = [Paragraph(t, S(f"ah{i}","SaraB",9,colors.white,TA_CENTER,13)) for i, t in
               enumerate(["ประเภท/วิธีชาร์จ", "บาท/กม.", f"ค่าพลังงาน/ปี ({KM_PER_YEAR:,} กม.)", "ประหยัดกว่าน้ำมัน/ปี"])]
    ann_rows = [ann_hdr]
    ice_annual = ANNUAL_COMPARE[0][1] * KM_PER_YEAR
    for i, (label, cpk, km, note) in enumerate(ANNUAL_COMPARE):
        annual = cpk * km
        saving = ice_annual - annual if i > 0 else 0
        is_ev  = i > 0
        ann_rows.append([
            Paragraph(label, S(f"al{i}","SaraSB" if is_ev else "Sara",9,C_BLUE if is_ev else C_TEXT,TA_LEFT,13)),
            Paragraph(f"{cpk:.2f}", sCell),
            Paragraph(f"{annual:,.0f} บาท",
                      S(f"aa{i}","SaraB",10, C_RED if not is_ev else C_GREEN, TA_CENTER, 14)),
            Paragraph(f"— " if not is_ev else f"ประหยัด {saving:,.0f} บาท",
                      S(f"as{i}","SaraB",10, C_GRAY if not is_ev else C_GREEN, TA_CENTER, 14)),
        ])
    ann_cws = [cw*0.37, cw*0.10, cw*0.27, cw*0.26]
    ann_t = Table(ann_rows, colWidths=ann_cws, repeatRows=1)
    ann_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), C_NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_RED_BG, C_BLUE_BG, C_BLUE_BG, C_BLUE_BG]),
        ("GRID",(0,0),(-1,-1),0.3,C_BORDER),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(0,1),(0,-1),"LEFT"),
    ]))
    story.append(ann_t)
    story.append(Spacer(1, 4*mm))

    # — ค่า service เทียบ ————————————————————————————————————————————————
    story.append(Paragraph("ค่าบำรุงรักษาเทียบกัน", sH2))
    story.append(Spacer(1, 1*mm))

    svc_hdr = [Paragraph(t, S(f"svh{i}","SaraB",9,colors.white,TA_CENTER,13)) for i, t in
               enumerate(["รายการ", "รถน้ำมัน (ICE)", "รถไฟฟ้า (EV)", "หมายเหตุ"])]
    svc_rows = [svc_hdr]
    for i, (item, ice, ev, note) in enumerate(SERVICE_COMPARE):
        ev_good = "✓" in ev
        ev_bad  = "✗" in ev
        svc_rows.append([
            Paragraph(item, S(f"si{i}","Sara",9,C_TEXT,TA_LEFT,13)),
            Paragraph(ice,  S(f"sc{i}","Sara",9,C_RED,  TA_CENTER,13)),
            Paragraph(ev,   S(f"se{i}","SaraB",9, C_GREEN if ev_good else (C_RED if ev_bad else C_TEXT), TA_CENTER,13)),
            Paragraph(note, sSmall),
        ])
    svc_cws = [cw*0.30, cw*0.21, cw*0.21, cw*0.28]
    svc_t = Table(svc_rows, colWidths=svc_cws, repeatRows=1)
    svc_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), C_NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_BG, C_SURFACE]),
        ("BACKGROUND",(0,8),(-1,8), C_CARD),  # summary row
        ("GRID",(0,0),(-1,-1),0.3,C_BORDER),
        ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(0,1),(0,-1),"LEFT"),
        ("FONTNAME",(0,8),(-1,8),"SaraB"),
        ("LINEABOVE",(0,8),(-1,8),1,C_NAVY),
    ]))
    story.append(svc_t)
    story.append(Spacer(1, 4*mm))

    # — 5-year TCO ———————————————————————————————————————————————————————
    story.append(Paragraph("ต้นทุนรวม 5 ปี (Total Cost of Ownership)", sH2))
    story.append(Spacer(1, 1*mm))

    tco_hdr = [Paragraph(t, S(f"th{i}","SaraB",9,colors.white,TA_CENTER,13)) for i, t in
               enumerate(["รายการ", "รถน้ำมัน Eco Car", "รถไฟฟ้า (BYD Atto 1)"])]
    tco_rows = [tco_hdr]
    for i, (item, ice_v, ev_v) in enumerate(TCO_ITEMS):
        is_total   = "รวม" in item
        is_saving  = "ประหยัด" in item
        tco_rows.append([
            Paragraph(item,  S(f"ti{i}","SaraB" if is_total or is_saving else "Sara",
                               9, C_DARK if is_total or is_saving else C_TEXT, TA_LEFT, 13)),
            Paragraph(ice_v, S(f"tv1{i}","SaraB" if is_total else "Sara",
                               9, C_RED if is_total else C_TEXT, TA_CENTER, 13)),
            Paragraph(ev_v,  S(f"tv2{i}","SaraB" if is_total or is_saving else "Sara",
                               9, (C_GREEN if is_saving else (C_BLUE if is_total else C_TEXT)), TA_CENTER, 13)),
        ])
    tco_cws = [cw*0.40, cw*0.30, cw*0.30]
    tco_t = Table(tco_rows, colWidths=tco_cws, repeatRows=1)
    tco_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), C_NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_BG, C_SURFACE]),
        ("BACKGROUND",(0,6),(-1,6), C_GREEN_BG),
        ("BACKGROUND",(0,7),(-1,7), C_GREEN_BG),
        ("GRID",(0,0),(-1,-1),0.3,C_BORDER),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(0,1),(0,-1),"LEFT"),
        ("LINEABOVE",(0,6),(-1,6),1.5,C_GREEN),
    ]))
    story.append(tco_t)
    story.append(PageBreak())

    # ── HIDDEN COSTS + INSURANCE ──────────────────────────────────────────────
    story.append(Paragraph("ค่าใช้จ่ายแฝงที่ควรรู้ก่อนซื้อ EV", sH1))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "EV ประหยัดในระยะยาวมาก แต่มีค่าใช้จ่ายที่ซ่อนอยู่ซึ่งคนมักมองข้าม",
        sBody
    ))
    story.append(Spacer(1, 4*mm))

    hc_hdr = [Paragraph(t, S(f"hh{i}","SaraB",9,colors.white,TA_CENTER,13)) for i, t in
              enumerate(["ค่าใช้จ่ายแฝง", "รายละเอียด / ตัวเลข", "วิธีรับมือ"])]
    hc_rows = [hc_hdr]
    for i, (item, detail, handle) in enumerate(HIDDEN_COSTS):
        hc_rows.append([
            Paragraph(item,   S(f"hi{i}","SaraSB",9,C_AMBER,TA_LEFT,13)),
            Paragraph(detail, S(f"hd{i}","Sara",  9,C_TEXT, TA_LEFT,13)),
            Paragraph(handle, S(f"hh{i}","Sara",  9,C_BLUE, TA_LEFT,13)),
        ])
    hc_cws = [cw*0.25, cw*0.38, cw*0.37]
    hc_t = Table(hc_rows, colWidths=hc_cws, repeatRows=1)
    hc_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), C_NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_BG, C_AMBER_BG]),
        ("GRID",(0,0),(-1,-1),0.3,C_BORDER),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(0,1),(0,-1),"LEFT"),
    ]))
    story.append(hc_t)
    story.append(Spacer(1, 5*mm))

    # — ประกันภัย ——————————————————————————————————————————————————————
    story.append(Paragraph("ค่าประกันภัยชั้น 1 แต่ละรุ่น", sH1))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "ประกันชั้น 1 EV แพงกว่ารถน้ำมันราคาเดียวกัน ~30–50%  "
        "เพราะแบตเตอรี่ + ชิ้นส่วนเฉพาะทางมีต้นทุนซ่อมสูง",
        sBody
    ))
    story.append(Spacer(1, 3*mm))

    ins_hdr = [Paragraph(t, S(f"ih{i}","SaraB",9,colors.white,TA_CENTER,13)) for i, t in
               enumerate(["รุ่น", "เบี้ยประกันชั้น 1 / ปี (โดยประมาณ)", "หมายเหตุ / บริษัทประกัน"])]
    ins_rows = [ins_hdr]
    for nm, price_ins, note, car_key in INSURANCE_DATA:
        clr_ins = C_CAR[car_key]
        ins_rows.append([
            Paragraph(nm,        S(f"in{nm}","SaraB",10,clr_ins,TA_LEFT,14)),
            Paragraph(price_ins, S(f"ip{nm}","SaraB",10,C_AMBER,TA_CENTER,14)),
            Paragraph(note,      sSmall),
        ])
    ins_cws = [cw*0.20, cw*0.28, cw*0.52]
    ins_t = Table(ins_rows, colWidths=ins_cws, repeatRows=1)
    ins_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), C_NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_BG, C_SURFACE]),
        ("GRID",(0,0),(-1,-1),0.3,C_BORDER),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(0,1),(0,-1),"LEFT"),
    ]))
    story.append(ins_t)
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(f"เปรียบเทียบ: {INS_ICE_NOTE}", S("icen","Sara",9,C_RED,TA_LEFT,13)))
    story.append(Spacer(1, 3*mm))

    # Insurance tips box
    ins_tips = [
        "ซื้อประกันในงาน Motor Show/Expo — บางค่ายแถมประกันชั้น 1 ปีแรกฟรี",
        "เปรียบเทียบเบี้ยผ่าน Priceza Money / Rabbit Care / Gettgo ก่อนตัดสินใจ",
        "เลือกแผนที่มี 'EV Battery Protection' ครอบคลุมแบตเตอรี่ไฮโวลต์ด้วย",
        "ปีที่ 2+ เบี้ยอาจลดลงถ้าไม่มีประวัติเคลม (No Claim Bonus 10–20%)",
        "รถประกอบในไทย (BYD Dolphin, MG4) อะไหล่หาง่ายกว่า → เบี้ยประกันถูกกว่า",
    ]
    ins_tips_rows = [[Paragraph("Tips เรื่องประกัน EV", S("ith","SaraB",10,C_BLUE,TA_LEFT,15))]]
    for t in ins_tips:
        ins_tips_rows.append([Paragraph(f"• {t}", sBody)])
    ins_tips_t = Table(ins_tips_rows, colWidths=[cw])
    ins_tips_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,0), C_BLUE_BG),
        ("BACKGROUND",(0,1),(0,-1), C_BG),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
        ("LINEBEFORE",(0,0),(0,-1),3,C_BLUE),
        ("BOX",(0,0),(0,-1),0.4,C_BORDER),
    ]))
    story.append(ins_tips_t)
    story.append(PageBreak())

    # ── BEST TIME TO BUY ──────────────────────────────────────────────────────
    story.append(Paragraph("ช่วงเวลาซื้อที่ดีที่สุด", sH1))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "เลือกช่วงเวลาให้ถูกต้องประหยัดได้ 30,000–120,000 บาท  โดยไม่ต้องต่อราคาเพิ่ม",
        sBody
    ))
    story.append(Spacer(1, 4*mm))

    for bt in BUY_TIMING:
        ch = bt["clr_hdr"];  bg = bt["clr_bg"]
        hdr_row = [
            Paragraph(bt["period"], S("bth","SaraB",11,ch,TA_LEFT,16)),
            Paragraph(bt["rating"], S("btr","SaraB",10,ch,TA_RIGHT,14)),
        ]
        detail_rows = [[Paragraph(f"• {d}", S("btd","Sara",9,C_TEXT,TA_LEFT,14)), ""]
                       for d in bt["detail"]]
        bt_t = Table([hdr_row] + detail_rows, colWidths=[cw*0.65, cw*0.35])
        bt_t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0), bg),
            ("BACKGROUND",(0,1),(-1,-1), C_BG),
            ("SPAN",(0,1),(-1,-1)),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("LINEBELOW",(0,0),(-1,0), 2, ch),
            ("BOX",(0,0),(-1,-1), 0.5, C_BORDER),
            ("ROUNDEDCORNERS",(0,0),(-1,-1),4),
        ]))
        story.append(bt_t)
        story.append(Spacer(1, 3*mm))

    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("ค่าใช้จ่ายที่ต้องวางแผนเพิ่มเติม", sH1))
    story.append(Spacer(1, 2*mm))

    ec_hdr_row = [Paragraph(t, S("ech","SaraB",9,colors.white,TA_CENTER,13)) for t in
                  ["รายการ", "ค่าใช้จ่ายโดยประมาณ", "หมายเหตุ"]]
    ec_rows = [ec_hdr_row]
    for nm, price_ec, note in EXTRA_COSTS:
        ec_rows.append([
            Paragraph(nm, sCellBL),
            Paragraph(price_ec, S("ep","SaraB",9,C_AMBER,TA_CENTER,13)),
            Paragraph(note, sSmall),
        ])
    ec_t = Table(ec_rows, colWidths=[cw*0.37, cw*0.25, cw*0.38], repeatRows=1)
    ec_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), C_NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_BG, C_SURFACE]),
        ("GRID",(0,0),(-1,-1), 0.3, C_BORDER),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(0,1),(0,-1),"LEFT"),
    ]))
    story.append(ec_t)
    story.append(PageBreak())

    # ── RECOMMENDATION SUMMARY ────────────────────────────────────────────────
    story.append(Paragraph("สรุปคำแนะนำ — เลือกตามไลฟ์สไตล์", sH1))
    story.append(Spacer(1, 3*mm))

    rec_hdr_row = [Paragraph(t, S("rh","SaraB",9,colors.white,TA_CENTER,13)) for t in
                   ["ไลฟ์สไตล์ / ความต้องการ", "รุ่นแนะนำ", "ราคา"]]
    rec_rows = [rec_hdr_row]
    for life, car_rec, pr in RECS:
        rec_rows.append([
            Paragraph(life, sBody),
            Paragraph(car_rec, S("rr","SaraB",10,C_BLUE2,TA_LEFT,14)),
            Paragraph(pr, S("rp","SaraB",10,C_AMBER,TA_RIGHT,14)),
        ])
    rec_t = Table(rec_rows, colWidths=[cw*0.42, cw*0.35, cw*0.23], repeatRows=1)
    rec_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), C_NAVY),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_BG, C_SURFACE]),
        ("GRID",(0,0),(-1,-1), 0.3, C_BORDER),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ALIGN",(0,1),(0,-1),"LEFT"),
    ]))
    story.append(rec_t)
    story.append(Spacer(1, 6*mm))

    # Tips
    tips = [
        "ทดลองขับก่อน — ความรู้สึกหลังพวงมาลัยสำคัญกว่าสเปคบนกระดาษ",
        "เช็คศูนย์บริการใกล้บ้าน — ระยะใกล้ = ความสะดวกระยะยาว",
        "ใช้ TOU (Time of Use) ชาร์จไฟกลางคืน ค่าไฟถูกกว่ากลางวัน 40–50%",
        "รถประกอบในไทย (BYD Dolphin, MG4) รับสิทธิ์ EV3.5 เงินอุดหนุน 50,000 บาท",
        "ถามเรื่อง Resale Value — ถ้าซื้อเพื่อใช้ยาว 5+ ปี ไม่ต้องกังวล",
        "พนักงานประจำขอสินเชื่อได้ง่ายกว่า — ควรเตรียม Slip เงินเดือน 3 เดือน + Statement 6 เดือน",
    ]
    tips_rows = [[Paragraph("Tips ก่อนซื้อ", S("th","SaraB",11,C_BLUE,TA_LEFT,16))]]
    for t in tips:
        tips_rows.append([Paragraph(f"• {t}", sBody)])
    tips_t = Table(tips_rows, colWidths=[cw])
    tips_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,0), C_BLUE_BG),
        ("BACKGROUND",(0,1),(0,-1), C_BG),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
        ("LINEBEFORE",(0,0),(0,-1), 3, C_BLUE),
        ("BOX",(0,0),(0,-1), 0.4, C_BORDER),
        ("ROUNDEDCORNERS",(0,0),(-1,-1),4),
    ]))
    story.append(tips_t)
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(cw, color=C_BORDER, thickness=1))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "ข้อมูล ณ มิถุนายน 2026  |  ราคาและโปรโมชั่นอาจเปลี่ยนแปลงตามนโยบายค่ายรถ  "
        "|  ยอดผ่อนเป็นการประมาณ ควรยืนยันกับสถาบันการเงินก่อนตัดสินใจ",
        sSmall
    ))
    story.append(Spacer(1, 8*mm))

    # ── CREDIT BLOCK ─────────────────────────────────────────────────────────
    credit_logo_col = [
        AepLogoFlowable(box_size=30, with_tagline=True),
        Spacer(1, 4*mm),
        Paragraph(
            '"เปลี่ยนคนธรรมดา ให้ใช้ AI เป็น"',
            S("cq","SaraSB",9,AEP_ACCENT,TA_LEFT,14)
        ),
    ]
    credit_info_col = [
        Paragraph("จัดทำโดย", S("cby","SaraSB",8,C_GRAY,TA_LEFT,12)),
        Spacer(1, 1*mm),
        Paragraph("AI Easy Pro", S("cname","SaraB",13,AEP_NAVY,TA_LEFT,18)),
        Spacer(1, 3*mm),
        Paragraph(f"🌐  {AEP_WEB}",   S("cw","Sara",9,C_TEXT,TA_LEFT,14)),
        Paragraph(f"💬  LINE OA  {AEP_LINE}", S("cl","Sara",9,C_TEXT,TA_LEFT,14)),
        Paragraph(f"📞  {AEP_TEL}",   S("ct","Sara",9,C_TEXT,TA_LEFT,14)),
        Spacer(1, 3*mm),
        Paragraph(
            "คอร์ส AI สำหรับธุรกิจ · การตลาด · Facebook Ads\n"
            "เรียนง่าย ใช้ได้จริง สร้างรายได้จริง",
            S("cs","Sara",8,C_GRAY,TA_LEFT,12)
        ),
    ]

    credit_tbl = Table(
        [[credit_logo_col, credit_info_col]],
        colWidths=[cw * 0.42, cw * 0.58],
    )
    credit_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#EBF4FF")),
        ("VALIGN",     (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",(0,0), (-1,-1), 10*mm),
        ("RIGHTPADDING",(0,0),(-1,-1), 8*mm),
        ("TOPPADDING", (0,0), (-1,-1), 8*mm),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8*mm),
        ("LINEBEFORE",  (0,0),(0,-1),  4, AEP_ACCENT),
        ("BOX",         (0,0),(-1,-1), 0.5, C_BORDER),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), 6),
    ]))
    story.append(credit_tbl)

    doc.build(story, onFirstPage=page_deco, onLaterPages=page_deco)
    print(f"Done: {OUTPUT}")

if __name__ == "__main__":
    build_pdf()
