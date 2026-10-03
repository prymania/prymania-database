# University Demo — ระบบทะเบียนนิสิต (Flask + MySQL)

เว็บตัวอย่างที่ใช้ฐานข้อมูลกรณีศึกษาของวิชา (student, lecturer, subject, section, enroll)
เพื่อให้เห็นว่า "ตารางที่เราเขียน SQL กันในชั้นเรียน" เมื่อเป็นเว็บจริงจะหน้าตาอย่างไร
ทุกตารางบนเว็บมีปุ่ม **🔍 SQL ที่รันจริง** ให้ดูคำสั่งที่อยู่เบื้องหลัง

## วิธีรัน

```
pip install -r requirements.txt
python app.py
```

เปิดเบราว์เซอร์ไปที่ http://127.0.0.1:9001

1. แก้ `config.py` ให้ตรงกับ MySQL ที่ใช้ (ค่าเริ่มต้น: localhost / root / ฐานข้อมูล `university`)
2. ครั้งแรกกดปุ่ม **↺ รีเซ็ตข้อมูล** มุมขวาบน → เว็บจะสร้างฐานข้อมูลและรัน `schema.sql` ให้
   (หรือรัน `schema.sql` เองใน DBeaver ก็ได้)
3. ทดลองเพิ่ม/แก้/ลบได้ตามสบาย อยากได้ข้อมูลเดิมคืนกด **↺ รีเซ็ตข้อมูล** อีกครั้ง

## หน้าเว็บ

| หน้า | เนื้อหา |
|---|---|
| จัดการข้อมูล | 5 แท็บ ค้นหา / เพิ่ม / แก้ไข / ลบ — ตารางแสดงข้อมูลที่ JOIN แล้ว เช่น subject แสดง `pre_subid, pre_subname`, section แสดง `sub_id, sub_name, lec_id, lec_name` + ปุ่มดูผลการเรียน / กลุ่มที่สอน / รายชื่อนิสิต |
| Dashboard | การ์ดตัวเลข + รายงาน 10 รายการ (GROUP BY, LEFT JOIN, NOT EXISTS, CASE, subquery) |
| โครงสร้างฐานข้อมูล | ER Diagram + โครงสร้างตารางที่อ่านจาก `information_schema` |

## ไฟล์

```
app.py        รับคำขอจากหน้าเว็บ แล้วเรียกฟังก์ชันใน db.py
db.py         ★ SQL ทุกคำสั่งของเว็บอยู่ที่นี่ (ค้นหา / CRUD / รายงาน)
config.py     ค่าเชื่อมต่อ MySQL
schema.sql    สร้างตาราง + ข้อมูล (ชุดเดียวกับ prymania_DBLabScript.sql)
templates/    หน้า HTML (index, dashboard, schema)
static/       JavaScript + CSS + รูปนิสิต/อาจารย์ (images/<รหัส>.jpg)
```

เพิ่มรายงานใหม่: เขียนฟังก์ชัน `report_xxx()` ใน `db.py` แล้วเพิ่ม 1 บรรทัดในรายการ `REPORTS` ท้ายไฟล์ — ไม่ต้องแก้ไฟล์อื่น
