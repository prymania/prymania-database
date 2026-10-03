# Database Lecture Note (1204202)

เว็บ lecture note แบบ static — เปิด `docs/index.html` ได้ทันที (ไม่ต้องมีเซิร์ฟเวอร์)

## โครงสร้าง
- `src/*.html` — เนื้อหาแต่ละบท (แก้ที่นี่)
- `build.py` — แปลง `src/` → `docs/` และ **รันทุกตัวอย่าง SQL กับ MySQL จริง** เพื่อสร้างตารางผลลัพธ์
- `prymania_DBLabScript.sql` — schema + data กรณีศึกษา (ทุกหน้าเริ่มจากข้อมูลชุดนี้ใหม่)
- `docs/` — ผลลัพธ์ (GitHub Pages เปิดจากโฟลเดอร์นี้) (assets/style.css, assets/nav.js, image/, icon/)

## Build
```
python build.py                 # ทุกหน้า
python build.py 05-select.html  # เฉพาะหน้า
```
ต้องมี MySQL ที่ localhost (root / abcd1234) และ `pip install mysql-connector-python`
build จะสร้างฐานข้อมูลชั่วคราว `zz_lecture_build` แล้วลบทิ้งเมื่อเสร็จ

## แท็กพิเศษใน src
| แท็ก | ความหมาย |
|---|---|
| `<sql title="..." run>...</sql>` | code card + รันแล้วแสดงผลลัพธ์ |
| `exec` / `error` / `temp` / `reset` / `max="10"` / `show="SELECT ..."` | รันไม่แสดงผล / คาดว่า error / rollback หลังรัน / โหลดข้อมูลใหม่ / จำกัดแถว / แสดงผลคำสั่งเพิ่ม |
| `<ex no="5.1" title="..." level="2">โจทย์<answer>เฉลย</answer></ex>` | แบบฝึกหัดระหว่างเรียน (ปุ่มดูเฉลย) |
| `<review><li>...</li></review>` | คำถามท้ายบท |
| `<fig n="2-28" w="500">คำบรรยาย</fig>` | รูป `docs/image/fig2-28.jpg` |
| `<toc/>` | สารบัญหน้า (จาก h2) |

## คำถามท้ายบท + เฉลย
แก้ที่ `src/reviews/<ชื่อบท>.txt` (เช่น `05-select.txt` → `05-select.html`) แล้วรัน
```
set PYTHONIOENCODING=utf-8
python apply_reviews.py && python build.py
```
- `## หัวข้อ` = กลุ่มคำถาม · `ข้อความ || hint` = คำถาม 1 ข้อ
- `A: ข้อความ` = เฉลย 1 ย่อหน้า · `A- ข้อความ` = เฉลยแบบรายการ
- บล็อก ```` ```run ```` … ```` ``` ```` = SQL ในเฉลย (attribute เดียวกับแท็ก `<sql>`: run / exec / temp / error / max / show / title) — ไม่มี attribute = แสดงโค้ดอย่างเดียว
- เฉลยแต่ละบทเริ่มจากฐานข้อมูลกรณีศึกษาใหม่ ยกเว้นไฟล์ที่มี `#!noreset` (บทที่ 7, 11 ใช้วิว/โพรซีเยอร์ที่สร้างในบท)
- รายละเอียดรูปแบบอยู่ต้นไฟล์ `apply_reviews.py`

เฉลยซ่อนอยู่หลังปุ่ม **🔑 ดูเฉลย** — รหัสผ่านแยกตามบทอยู่ที่ `docs/assets/password.js` ใน `window.EXERCISE_PASSWORDS` (คีย์ `c1`–`c12` ตรงกับเลขหน้าของไฟล์ เช่น 07-view.html = c7) แก้ได้โดยไม่ต้อง build ใหม่
ข้อควรรู้: เป็นการล็อกฝั่งเบราว์เซอร์ เนื้อหาเฉลยยังอยู่ใน HTML และรหัสผ่านทุกบทอ่านได้จาก password.js — กันการเปิดดูโดยไม่ตั้งใจได้ แต่ไม่ใช่ความปลอดภัยจริง

## ภาคผนวก ง · Library Tutorial

`build.py` คัดลอกโฟลเดอร์ `library_tutorial_site/` (ยกเว้น `.git*` และ README) ไปไว้ที่ `site/library_tutorial_site/`
และเพิ่มลิงก์ “กลับ Lecture Note” ในเมนูของทุกหน้า — แก้เนื้อหา tutorial ที่ `library_tutorial_site/` แล้วรัน `python build.py` ใหม่
ภาคผนวก ง ไม่มีหน้าของตัวเอง — เมนูและการ์ดหน้าแรกลิงก์ไป `library_tutorial_site/index.html` (เปิดแท็บใหม่)

หมายเหตุ: `src/07-view-transaction.html` และ `src/08-security-procedure-trigger.html` เป็นฉบับเก่า (ไม่อยู่ใน PAGES แล้ว)
