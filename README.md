# ⚡ EV Car Compare — Claude Code Skill

**Claude Code Skill** สำหรับค้นหา เปรียบเทียบ และสร้าง PDF รถไฟฟ้าในไทย  
พิมพ์ `/ev-car-compare` ใน Claude Code — Claude จะรู้จักแหล่งข้อมูล ตัวเลขอ้างอิง และ workflow ทันที

> จัดทำโดย **[AI Easy Pro](https://aieasypro.com)** — AI ง่ายๆแบบมือโปร  
> LINE OA: [@117jyivt](https://line.me/R/ti/p/@117jyivt) · Tel: 093-225-3253

---

## Skill นี้ทำอะไรได้

เมื่อใช้ `/ev-car-compare` Claude จะ:

- **หาข้อมูลได้ถูกต้อง** — รู้ว่าต้อง search ที่ไหน query แบบไหน
- **มีตัวเลขอ้างอิงพร้อม** — ราคา สเปค ค่าประกัน อัตราดอกเบี้ยผ่อน EV vs น้ำมัน
- **คำนวณผ่อนให้ได้เลย** — flat rate formula + เงินเดือนขั้นต่ำสำหรับพนักงานประจำ
- **สร้าง PDF ได้** — Python script พร้อมใช้ ดาวน์โหลดรูปรถจากเว็บอัตโนมัติ

---

## ติดตั้ง Skill ใน Claude Code

```bash
mkdir -p ~/.claude/skills/ev-car-compare
curl -sL https://raw.githubusercontent.com/baanpakpoolvilla/ev-car-compare-th/main/skill.md \
  -o ~/.claude/skills/ev-car-compare/skill.md
```

แล้วพิมพ์ใน Claude Code:

```
/ev-car-compare
```

---

## ตัวอย่างการใช้งาน

```
/ev-car-compare
ช่วยเปรียบเทียบ BYD Dolphin กับ MG4 ให้หน่อย งบ 600,000 บาท
```

```
/ev-car-compare
คำนวณค่าผ่อน Geely EX2 ดาวน์ 20% พนักงานประจำเงินเดือนเท่าไรถึงกู้ผ่าน
```

```
/ev-car-compare
สร้าง PDF เปรียบเทียบรถ EV ราคาไม่เกิน 600k อัปเดตล่าสุด
```

---

## ข้อมูลที่ Skill รู้จัก (มิถุนายน 2026)

### รถ 4 รุ่นในกลุ่มราคาไม่เกิน 600,000 บาท

| รุ่น | ราคาเริ่มต้น | แบต | ระยะ NEDC | DC Fast Charge | ขับเคลื่อน |
|------|------------|-----|----------|----------------|-----------|
| BYD Atto 1 | 429,900 | 30/38.9 kWh | 300/380 กม. | 30/40 kW | FWD |
| Geely EX2 | 429,990 | 39.4 kWh | 395 กม. | 70 kW | RWD |
| BYD Dolphin | 549,900 | 50.25/60.48 kWh | 435/490 กม. | 30/60 kW | FWD |
| MG4 Electric | 579,900 | 50 kWh | 450 กม. | 120 kW | RWD |

### ตัวเลขอ้างอิงสำคัญ

| หัวข้อ | ค่า |
|--------|-----|
| น้ำมัน E95 ต่อ กม. | 2.8–3.7 บาท |
| EV ชาร์จบ้าน TOU กลางคืน | 0.3–0.4 บาท |
| ประหยัดค่าพลังงาน/ปี | ~39,750 บาท (วิ่ง 15,000 กม.) |
| ประหยัดรวม 5 ปี (TCO) | ~300,000–450,000 บาท |

---

## สร้าง PDF (Bonus Script)

สคริปต์ `ev_comparison.py` สร้าง PDF 10 หน้าภาษาไทยอัตโนมัติ

### Prerequisites

```bash
pip3 install reportlab

# ติดตั้งฟอนต์ Sarabun (macOS)
FONT_DIR="$HOME/Library/Fonts"
BASE="https://github.com/google/fonts/raw/main/ofl/sarabun"
for w in Regular Bold SemiBold Medium Light; do
  curl -sL "$BASE/Sarabun-${w}.ttf" -o "$FONT_DIR/Sarabun-${w}.ttf"
done
```

### รัน

```bash
python3 ev_comparison.py
# → สร้าง ~/Desktop/EV_Comparison_600K_2026.pdf
```

PDF ที่ได้มีครบ: สเปค · ตารางผ่อน · EV vs น้ำมัน · ค่าประกัน · ค่าใช้จ่ายแฝง · สรุปคำแนะนำ

---

## License

MIT — นำไปใช้ ดัดแปลง แจกต่อได้เสรี ไม่ต้องขออนุญาต
