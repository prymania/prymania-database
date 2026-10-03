import pathlib, re
L = pathlib.Path('work/old/08-security-procedure-trigger.html').read_text(encoding='utf-8').split('\n')
def seg(a, b): return '\n'.join(L[a-1:b-1])   # 1-based [a,b)
end = [i for i, l in enumerate(L, 1) if l.startswith('<review>')][0]
s1 = seg(13, 30); s2 = seg(30, 76); s3 = seg(76, 106)
sp_intro = seg(106, 115); sp1 = seg(115, 129); sp2 = seg(129, 152); sp3 = seg(152, 192); sp4 = seg(192, 229); spex = seg(229, 261)
fn = seg(261, 313)
tg_intro = seg(313, 322); tg1 = seg(322, 342); tg2 = seg(342, 369); tg3 = seg(369, 407); tg_cmp = seg(407, 415); tgex = seg(415, 468)
sq1 = seg(469, 487); sq2 = seg(487, 499); sqex = seg(499, end)

def h2(id_, no, title): return f'<h2 id="{id_}"><span class="sec">{no}</span> {title}</h2>'
def strip_h(x): return re.sub(r'^<h[23][^>]*>.*?</h[23]>\n?', '', x, count=1)
def obj(items):
    return ('<div class="objectives"><div class="box-t">🎯 เมื่อเรียนจบบทนี้ นิสิตจะสามารถ</div><ol>\n'
            + '\n'.join(f'<li>{i}</li>' for i in items) + '\n</ol></div>\n\n<toc/>\n')

# ---------------- ch10 security
c10 = '<!--meta {"title":"บทที่ 10 · ความปลอดภัยของฐานข้อมูล","kicker":"CHAPTER 10 · สัปดาห์ที่ 14","sub":"บัญชีผู้ใช้ การกำหนดและยกเลิกสิทธิ์ (GRANT / REVOKE) บทบาท (Role) วิวเพื่อควบคุมการเข้าถึง SQL Injection และแนวปฏิบัติด้านความปลอดภัย","img":"worker5.png"} -->\n\n'
c10 += obj(['อธิบายเป้าหมายและองค์ประกอบด้านความปลอดภัยของฐานข้อมูลได้', 'สร้างและจัดการบัญชีผู้ใช้ได้',
            'กำหนดและยกเลิกสิทธิ์ในระดับฐานข้อมูล ตาราง คอลัมน์ และวิวได้',
            'ออกแบบสิทธิ์ตามหลัก Least Privilege และใช้ Role ได้', 'อธิบาย SQL Injection และป้องกันด้วย Prepared Statement ได้'])
c10 += '''
<h2 id="s0"><span class="sec">10.1</span> ภาพรวมความปลอดภัยของฐานข้อมูล</h2>
<p>ความปลอดภัยของฐานข้อมูลครอบคลุม 3 เป้าหมายหลัก (CIA)</p>
<table class="tbl"><tr><th>เป้าหมาย</th><th>ความหมาย</th><th>ตัวอย่างภัย</th><th>เครื่องมือในบทนี้</th></tr>
<tr><td><b>C</b>onfidentiality</td><td>เฉพาะผู้มีสิทธิ์เท่านั้นที่เห็นข้อมูล</td><td>นิสิตแอบดูเกรดคนอื่น</td><td>GRANT, View, Role</td></tr>
<tr><td><b>I</b>ntegrity</td><td>ข้อมูลถูกแก้ได้เฉพาะผู้มีสิทธิ์ และถูกต้อง</td><td>แก้เกรดตัวเองผ่าน SQL Injection</td><td>สิทธิ์ระดับคอลัมน์, Prepared Statement, Trigger</td></tr>
<tr><td><b>A</b>vailability</td><td>ระบบและข้อมูลพร้อมใช้งาน</td><td>ลบตารางโดยไม่ตั้งใจ, ดิสก์เสีย</td><td>สิทธิ์ DROP เฉพาะผู้ดูแล, Backup</td></tr>
</table>
<div class="flow"><div class="st">Authentication<small>คุณคือใคร? (บัญชี + รหัสผ่าน)</small></div><span class="ar">→</span><div class="st">Authorization<small>คุณทำอะไรได้บ้าง? (GRANT)</small></div><span class="ar">→</span><div class="st">Auditing<small>คุณทำอะไรไปแล้ว? (Log / Trigger)</small></div></div>
'''
c10 += s1.replace('<h2 id="s1"><span class="sec">8.1</span>', '<h2 id="s1"><span class="sec">10.2</span>') + '\n'
c10 += s2.replace('<h2 id="s2"><span class="sec">8.2</span>', '<h2 id="s2"><span class="sec">10.3</span>').replace('<fig n="8-1">', '<fig n="8-1" no="10.1">').replace('<ex no="8.1"', '<ex no="10.1"') + '\n'
c10 += s3.replace('<h2 id="s3"><span class="sec">8.3</span>', '<h2 id="s3"><span class="sec">10.4</span>').replace('<ex no="8.2"', '<ex no="10.2"') + '\n'
c10 += h2('s4', '10.5', 'การแทรกคำสั่ง SQL (SQL Injection)') + '\n' + strip_h(sq1) + '\n'
c10 += h2('s5', '10.6', 'แนวปฏิบัติด้านความปลอดภัย') + '\n' + strip_h(sq2) + '\n' + sqex.replace('<ex no="8.9"', '<ex no="10.3"') + '\n<review>\n</review>\n'
c10 = c10.replace('หัวข้อ 8.1–8.3', 'หัวข้อ 10.2–10.4')
pathlib.Path('src/10-security.html').write_text(c10, encoding='utf-8')

# ---------------- ch11 stored procedure
c11 = '<!--meta {"title":"บทที่ 11 · สโตร์โพรซีเยอร์และฟังก์ชัน (Stored Procedure & Function)","kicker":"CHAPTER 11 · สัปดาห์ที่ 15","sub":"การสร้างและเรียกใช้สโตร์โพรซีเยอร์ พารามิเตอร์ IN/OUT/INOUT ตัวแปร คำสั่งควบคุม เคอร์เซอร์ การจัดการข้อผิดพลาดและทรานแซกชัน และฟังก์ชันที่ผู้ใช้สร้างขึ้น","img":"worker.png"} -->\n\n'
c11 += obj(['อธิบายแนวคิดและข้อดีของสโตร์โพรซีเยอร์ได้', 'สร้างและเรียกใช้โพรซีเยอร์ที่มีพารามิเตอร์ IN / OUT / INOUT ได้',
            'ใช้ตัวแปร IF / CASE / WHILE และเคอร์เซอร์ในโพรซีเยอร์ได้', 'จัดการข้อผิดพลาดด้วย HANDLER และ SIGNAL ร่วมกับทรานแซกชันได้',
            'สร้างฟังก์ชันและเรียกใช้ใน SELECT ได้ และเลือกใช้โพรซีเยอร์หรือฟังก์ชันได้เหมาะสม'])
c11 += sp_intro.replace('<h2 id="s4"><span class="sec">8.4</span>', '<h2 id="s1"><span class="sec">11.1</span>').replace('<fig n="8-2">', '<fig n="8-2" no="11.1">') + '\n'
c11 += h2('s2', '11.2', 'การสร้างและเรียกใช้สโตร์โพรซีเยอร์') + '\n' + strip_h(sp1) + '\n'
c11 += h2('s3', '11.3', 'ชนิดของพารามิเตอร์ IN / OUT / INOUT') + '\n' + strip_h(sp2) + '\nINOUT_PLACEHOLDER\n'
c11 += h2('s4', '11.4', 'ตัวแปรและคำสั่งควบคุม (IF, CASE, WHILE)') + '\n' + strip_h(sp3) + '\n'
c11 += h2('s5', '11.5', 'เคอร์เซอร์ (Cursor)') + '\n' + strip_h(sp4) + '\n' + spex.replace('<ex no="8.3"', '<ex no="11.1"').replace('<ex no="8.4"', '<ex no="11.2"') + '\nHANDLER_PLACEHOLDER\n'
c11 += fn.replace('<h2 id="s5"><span class="sec">8.5</span>', '<h2 id="s7"><span class="sec">11.7</span>').replace('<ex no="8.5"', '<ex no="11.4"') + '\n<review>\n</review>\n'
pathlib.Path('src/11-stored-procedure.html').write_text(c11, encoding='utf-8')

# ---------------- ch12 trigger
c12 = '<!--meta {"title":"บทที่ 12 · ทริกเกอร์ (Trigger)","kicker":"CHAPTER 12 · สัปดาห์ที่ 15","sub":"แนวคิดของทริกเกอร์ BEFORE / AFTER, OLD / NEW, การตรวจสอบข้อมูล การบันทึกประวัติ กฎธุรกิจข้ามตาราง การรักษาข้อมูลสรุปให้สอดคล้อง และข้อควรระวัง","img":"you-did-it.png"} -->\n\n'
c12 += obj(['อธิบายแนวคิด จังหวะการทำงาน (BEFORE / AFTER) และเหตุการณ์ของทริกเกอร์ได้', 'ใช้ OLD และ NEW ในทริกเกอร์ได้ถูกต้อง',
            'เขียนทริกเกอร์ตรวจสอบ/แก้ไขข้อมูลก่อนบันทึก และบันทึกประวัติการเปลี่ยนแปลงได้',
            'เขียนทริกเกอร์บังคับกฎธุรกิจที่ต้องอ่านข้อมูลหลายตาราง และรักษาข้อมูลสรุปให้สอดคล้องได้',
            'เลือกใช้ทริกเกอร์ เทียบกับ Constraint และ Stored Procedure ได้อย่างเหมาะสม'])
c12 += tg_intro.replace('<h2 id="s6"><span class="sec">8.6</span> ทริกเกอร์ (Trigger)', '<h2 id="s1"><span class="sec">12.1</span> แนวคิดของทริกเกอร์').replace('<fig n="8-3">', '<fig n="8-3" no="12.1">') + '\nSYNTAX_PLACEHOLDER\n'
c12 += h2('s3', '12.3', 'ทริกเกอร์ BEFORE — ตรวจสอบและแก้ไขข้อมูลก่อนบันทึก') + '\n' + strip_h(tg1) + '\n'
c12 += h2('s4', '12.4', 'ทริกเกอร์ AFTER — บันทึกประวัติการเปลี่ยนแปลง (Audit Log)') + '\n' + strip_h(tg2) + '\n'
c12 += h2('s5', '12.5', 'กฎธุรกิจที่ต้องอ่านข้อมูลหลายตาราง') + '\n' + strip_h(tg3) + '\nSUMMARY_PLACEHOLDER\n'
c12 += h2('s7', '12.7', 'การจัดการทริกเกอร์ และข้อควรระวัง') + '\n' + tg_cmp + '\n' + tgex.replace('<ex no="8.6"', '<ex no="12.1"').replace('<ex no="8.7"', '<ex no="12.2"').replace('<ex no="8.8"', '<ex no="12.3"') + '\n<review>\n</review>\n'
c12 = c12.replace("DELETE FROM student WHERE stdid LIKE '99%';", "DELETE FROM student WHERE stdid = '80011';")
pathlib.Path('src/12-trigger.html').write_text(c12, encoding='utf-8')
