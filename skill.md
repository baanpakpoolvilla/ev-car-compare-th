---
name: ev-car-compare
description: สร้าง PDF เปรียบเทียบรถไฟฟ้าในไทย — สเปค ราคา ผ่อน ประกัน EV vs น้ำมัน พร้อมโลโก้ AI Easy Pro ใช้ ReportLab + Sarabun + รูปจริงจากเว็บ
---

สร้าง PDF เปรียบเทียบรถไฟฟ้าภาษาไทยแบบ professional สำหรับใช้ประกอบการตัดสินใจซื้อรถ
ไฟล์ผลลัพธ์อยู่ที่ `~/Desktop/EV_Comparison_600K_2026.pdf`
สคริปต์หลัก: `~/Desktop/ev_comparison.py`

---

## โครงสร้าง PDF (10 หน้า)

| หน้า | เนื้อหา |
|------|---------|
| 1 | หน้าปก — โลโก้ AI Easy Pro + ชื่อคู่มือ + card รถ 4 รุ่น |
| 2 | ตารางเปรียบเทียบสเปคครบ |
| 3–6 | รีวิวรายคัน (รูปจริง + สเปค + ข้อดี/ข้อด้อย + เหมาะกับใคร) |
| 7 | ตารางผ่อน — พนักงานประจำ (2 rates × 3 down × 3 terms, 4 รุ่น) |
| 8 | EV vs รถน้ำมัน — ค่าพลังงาน / ค่า service / TCO 5 ปี |
| 9 | ค่าใช้จ่ายแฝง (7 รายการ) + ค่าประกันชั้น 1 แต่ละรุ่น |
| 10 | สรุปคำแนะนำ + Tips + เครดิต AI Easy Pro |

---

## รถที่อยู่ในเอกสาร (อัปเดต มิถุนายน 2026)

| รุ่น | ราคาเริ่มต้น | แบต | ระยะ NEDC | DC kW | ขับเคลื่อน |
|------|------------|-----|----------|-------|-----------|
| BYD Atto 1 Dynamic | 429,900 | 30.08 kWh | 300 กม. | 30 | FWD |
| BYD Atto 1 Premium | 459,900 | 38.88 kWh | 380 กม. | 40 | FWD |
| Geely EX2 Pro | 429,990 | 39.4 kWh | 395 กม. | 70 | RWD |
| Geely EX2 Max | 459,990 | 39.4 kWh | 395 กม. | 70 | RWD |
| BYD Dolphin Standard | 549,900 | 50.25 kWh | 435 กม. | 30 | FWD |
| BYD Dolphin Extended | 599,900 | 60.48 kWh | 490 กม. | 60 | FWD |
| MG4 D Standard | 579,900 | 50 kWh | 450 กม. | 120 | RWD |

---

## ค่าประกันชั้น 1 (ข้อมูล 2025–2026)

| รุ่น | ช่วงเบี้ย/ปี | หมายเหตุ |
|------|------------|---------|
| BYD Atto 1 | 18,000–24,000 | บางบริษัทยังไม่รับ |
| Geely EX2 | 20,000–25,000 | ยังไม่มีราคาทางการ (ประมาณ) |
| BYD Dolphin | 26,000–30,000 | Viriyah 26k / Thanachart 27k / Allianz 28.8k / AXA 30k |
| MG4 Electric | 18,000–22,000 | ประกอบไทย อะไหล่หาง่าย เบี้ยถูกกว่า |
| รถน้ำมัน Eco Car เทียบ | 14,000–20,000 | ถูกกว่า EV ~30–50% |

---

## ตัวเลขสำคัญ EV vs น้ำมัน (ใช้ตอบ search / update ข้อมูล)

| หัวข้อ | ค่า |
|--------|-----|
| น้ำมัน E95 ต่อ กม. | 2.8–3.7 บาท/กม. |
| EV ชาร์จบ้าน TOU กลางคืน | 0.3–0.4 บาท/กม. |
| EV ชาร์จบ้านปกติ | 0.6–0.8 บาท/กม. |
| EV ชาร์จ DC สาธารณะ | 1.2–1.6 บาท/กม. |
| ประหยัดค่าพลังงาน/ปี (15k กม.) | ~39,750 บาท (TOU vs น้ำมัน) |
| TCO 5 ปี รถน้ำมัน | ~1,100,000–1,250,000 บาท |
| TCO 5 ปี EV | ~750,000–900,000 บาท |
| ประหยัดรวม 5 ปี | ~300,000–450,000 บาท |

---

## อัตราดอกเบี้ยผ่อน

```python
RATE_PROMO  = 0.0199   # 1.99% flat/year  (Motor Show / Expo)
RATE_NORMAL = 0.0299   # 2.99% flat/year  (ปกติ)
DOWN_PCTS   = [0.10, 0.20, 0.30]
MONTHS_LIST = [60, 72, 84]

# สูตร flat rate
def calc_payment(price, down_pct, rate_flat, months):
    principal = price * (1 - down_pct)
    years = months / 12
    total = principal * (1 + rate_flat * years)
    return round(total / months)

# เงินเดือนขั้นต่ำ = ยอดผ่อน ÷ 0.35 ≈ ×2.86  (ธนาคารให้ผ่อนไม่เกิน 35% ของรายได้)
def min_salary(payment):
    return round(payment / 0.35 / 1000) * 1000
```

---

## AI Easy Pro Brand (สำหรับ credit / logo)

```python
AEP_NAVY   = "#0B1F3A"   # พื้นหลัง header
AEP_ACCENT = "#2F80ED"   # สีกล่อง logo / CTA
AEP_LIGHT  = "#7EB8F7"   # ข้อความในแถบ navy
AEP_WEB    = "aieasypro.com"
AEP_LINE   = "@117jyivt"
AEP_TEL    = "093-225-3253"
```

**โลโก้** = rounded square สีฟ้า `#2F80ED` + ตัว "AI" สีขาว (bold) + "Easy Pro" สีน้ำเงินข้างๆ
ดูโค้ดต้นแบบ: `~/Desktop/AI Easy Pro/web/lib/nav-logo-mark.tsx` และ `og-brand.tsx`

---

## Image URLs ที่ download ได้จริง (มิถุนายน 2026)

```python
# BYD Atto 1 — headlightmag.com
"https://www.headlightmag.com/hlmwp/wp-content/uploads/2026/03/ATTO_1_Exterior_4.jpg"
"https://www.headlightmag.com/hlmwp/wp-content/uploads/2026/03/ATTO_1_Exterior_1.jpg"

# Geely EX2 — headlightmag.com
"https://www.headlightmag.com/hlmwp/wp-content/uploads/2025/11/Geely-EX2-Exterior-1.jpg"
"https://www.headlightmag.com/hlmwp/wp-content/uploads/2025/11/Geely-EX2-Exterior-2-1.jpg"

# BYD Dolphin — 9carthai.com
"https://www.9carthai.com/wp-content/uploads/2023/07/BYD-DOLPHIN-2-1.jpg"

# MG4 MY2026 — headlightmag.com
"https://www.headlightmag.com/hlmwp/wp-content/uploads/2026/03/MG-4-MY2026-Exterior-2.jpg"
"https://www.headlightmag.com/hlmwp/wp-content/uploads/2026/03/MG-4-MY2026-Exterior-1.jpg"
```

> ถ้า URL เสีย ให้ WebFetch หน้า headlightmag.com ของรุ่นนั้น แล้ว grep `hlmwp/wp-content/uploads` หา URL ใหม่

---

## แหล่ง Search ข้อมูลอัปเดต

| ข้อมูล | แหล่ง |
|--------|-------|
| ราคาอย่างเป็นทางการ | autolifethailand.tv, headlightmag.com, 9carthai.com |
| สเปครถ | headlightmag.com/official-price-xxx, car250.com |
| ประกันภัย | money.priceza.com, heygoody.com/th/autoinsurance/evcar/ |
| ค่าผ่อน | bydchonburi.com, krungsri.com/auto |
| EV vs น้ำมัน | superbikemag.com, sanook.com/auto |
| ช่วงเวลาซื้อ | motorexpo.co.th, motor show coverage |

**Query pattern สำหรับ search:**
```
"[ชื่อรุ่น] ราคาอย่างเป็นทางการ [ปี] ไทย"
"ประกันชั้น 1 [ชื่อรุ่น] เบี้ยประกัน [ปี]"
"รถไฟฟ้าราคาไม่เกิน 600000 บาท [ปี] ไทย"
```

---

## Steps รวม

1. **Search** ราคา/สเปครถใหม่ก่อนเสมอ (ราคา EV เปลี่ยนบ่อย)
2. **อัปเดต** `CARS` dict ใน script — `price_low`, `price_high`, `price_rep`, `specs`, `image_urls`
3. **ทดสอบ download รูป** ด้วย `python3 -c "import urllib.request; ..."` ก่อน generate จริง
4. **Regenerate:** `cd ~/Desktop && python3 ev_comparison.py`
5. **เปิดดู:** `open ~/Desktop/EV_Comparison_600K_2026.pdf`

---

## เพิ่ม/ลดรุ่นรถ

```python
# เพิ่มรุ่นใหม่ใน CARS list
{
    "name":      "ชื่อรุ่น",
    "brand":     "แบรนด์",
    "segment":   "Hatchback / SUV / Sedan (X-Segment)",
    "price_low":  500000,    # แทนด้วยราคาจริง
    "price_high": 600000,
    "price_rep":  500000,   # ราคารุ่นที่ใช้คำนวณผ่อน
    "variants": ["รุ่นย่อย 1", "รุ่นย่อย 2"],
    "image_urls": ["URL1", "URL2"],
    "specs": [("หัวข้อ", "ค่า"), ...],
    "pros":    ["ข้อดี 1", ...],
    "cons":    ["ข้อด้อย 1", ...],
    "for_who": "เหมาะกับ...",
}

# เพิ่มสี brand card ใน C_CAR และ C_CAR_LIGHT
C_CAR["ชื่อรุ่น"]       = colors.HexColor("#XXXXXX")
C_CAR_LIGHT["ชื่อรุ่น"] = colors.HexColor("#XXXXXX")
```

---

## ⚠️ Pitfalls

| ปัญหา | วิธีแก้ |
|-------|--------|
| รูปไม่โหลด → PDF เล็ก ~70K | ทดสอบ URL ด้วย `urllib.request` ก่อน |
| ราคา EV เปลี่ยนบ่อย | search ก่อนทุกครั้ง — ราคาโปรงานอาจต่างจากปกติ 50k–120k |
| NEDC vs WLTP ต่างกัน | WLTP ≈ NEDC × 0.75–0.85 (จริงกว่า) — ใส่ทั้งคู่ |
| ค่าผ่อน flat rate vs reducing | สคริปต์ใช้ flat rate — ยอดจริงจากธนาคารอาจต่างเล็กน้อย |
| ReportLab `SPAN` ใน multi-row Table | ต้อง SPAN แบบ `(col_start, row_start), (col_end, row_end)` |
| ฟอนต์ไทยขาด | `ls ~/Library/Fonts/Sarabun*.ttf` — ต้องมี Regular, Bold, SemiBold |
