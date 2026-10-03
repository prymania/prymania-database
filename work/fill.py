import pathlib
p = pathlib.Path('src/11-stored-procedure.html'); t = p.read_text(encoding='utf-8')
t = t.replace('ตัวอย่างที่ 8.2 — หน่วยกิตรวมของนิสิต (OUT)', 'ตัวอย่างที่ 11.1 — หน่วยกิตรวมของนิสิต (OUT)')
t = t.replace('<p><b>ตัวอย่างที่ 8.2</b>', '<p><b>ตัวอย่างที่ 11.1</b>')
t = t.replace('INOUT_PLACEHOLDER', '''<p><b>INOUT</b> — ส่งค่าเข้าไป ให้โพรซีเยอร์ปรับ แล้วรับค่าใหม่กลับออกมาทางตัวแปรเดิม</p>
<sql title="ตัวอย่างที่ 11.2 — INOUT: คำนวณเงินเดือนหลังขึ้น" exec>DELIMITER $$

CREATE PROCEDURE sp_apply_raise (IN p_percent INT, INOUT p_salary INT)
BEGIN
    SET p_salary = p_salary + ROUND(p_salary * p_percent / 100);
END $$

DELIMITER ;</sql>
<sql title="เรียกใช้ — ตัวแปร @s ถูกเปลี่ยนค่า" run>SET @s = 40000;
CALL sp_apply_raise(10, @s);
CALL sp_apply_raise(10, @s);
SELECT @s AS salary_after_two_raises;</sql>
<div class="box note"><div class="box-t">📝 ตัวแปร @ กับ DECLARE</div><p><code>@ชื่อ</code> คือ <b>User Variable</b> อยู่ได้ตลอด session ใช้รับค่า OUT/INOUT จากภายนอก ส่วน <code>DECLARE</code> คือ <b>Local Variable</b> อยู่ได้เฉพาะภายใน BEGIN … END ของโพรซีเยอร์</p></div>''')
t = t.replace('HANDLER_PLACEHOLDER', '''<h2 id="s6"><span class="sec">11.6</span> การจัดการข้อผิดพลาดและทรานแซกชันในโพรซีเยอร์</h2>
<p>โพรซีเยอร์ที่ทำหลายขั้นตอนต้อง (1) <b>ตรวจเงื่อนไข</b>ก่อนบันทึก แล้วแจ้งข้อผิดพลาดที่เข้าใจง่ายด้วย <code>SIGNAL</code> และ (2) <b>ย้อนกลับทั้งหมด</b>เมื่อขั้นใดล้มเหลว ด้วย <code>HANDLER</code> + ทรานแซกชัน (บทที่ 9)</p>
<table class="tbl"><tr><th>คำสั่ง</th><th>หน้าที่</th></tr>
<tr><td><code>SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '…'</code></td><td>สร้าง error ของเราเอง (45000 = error ที่ผู้ใช้กำหนด)</td></tr>
<tr><td><code>DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN … END</code></td><td>เมื่อเกิด error ใด ๆ ให้ทำคำสั่งใน BEGIN…END แล้วออกจากโพรซีเยอร์</td></tr>
<tr><td><code>DECLARE CONTINUE HANDLER FOR NOT FOUND …</code></td><td>เมื่อไม่พบข้อมูล (เช่น เคอร์เซอร์อ่านหมด) ให้ทำงานต่อ</td></tr>
<tr><td><code>RESIGNAL</code></td><td>ส่ง error เดิมต่อออกไปให้ผู้เรียก (หลัง ROLLBACK แล้ว)</td></tr>
</table>
<h3>ตัวอย่างที่ 11.6 — sp_enroll: ลงทะเบียนพร้อมตรวจเงื่อนไข</h3>
<p>กฎ: (1) นิสิตและกลุ่มเรียนต้องมีอยู่จริง (2) ห้ามลงซ้ำ (3) ถ้าวิชามีวิชาบังคับก่อน ต้องเคยผ่านวิชานั้น (เกรด A–D)</p>
<sql title="สร้าง sp_enroll" exec>DELIMITER $$

CREATE PROCEDURE sp_enroll (IN p_sid VARCHAR(10), IN p_secid INT)
BEGIN
    DECLARE v_pre VARCHAR(10);

    IF NOT EXISTS (SELECT 1 FROM student WHERE stdid = p_sid) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ไม่พบรหัสนิสิต';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM section WHERE secid = p_secid) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ไม่พบกลุ่มเรียน';
    END IF;

    IF EXISTS (SELECT 1 FROM enroll WHERE secid = p_secid AND stdid = p_sid) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ลงทะเบียนกลุ่มนี้ไปแล้ว';
    END IF;

    SELECT sub.pre INTO v_pre
    FROM   section sec JOIN subject sub ON sec.subid = sub.subid
    WHERE  sec.secid = p_secid;

    IF v_pre IS NOT NULL AND NOT EXISTS (
          SELECT 1 FROM enroll e JOIN section s ON e.secid = s.secid
          WHERE  e.stdid = p_sid AND s.subid = v_pre
            AND  e.grade IN ('A', 'B', 'C', 'D')) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ยังไม่ผ่านวิชาบังคับก่อน';
    END IF;

    INSERT INTO enroll (secid, stdid) VALUES (p_secid, p_sid);
    SELECT CONCAT('ลงทะเบียน ', p_sid, ' ในกลุ่ม ', p_secid, ' สำเร็จ') AS message;
END $$

DELIMITER ;</sql>
<sql title="กรณีสำเร็จ — 60004 เคยได้ A วิชา CS004 จึงลง CS009 (secid 52) ได้" run>CALL sp_enroll('60004', 52);</sql>
<sql title="ลงซ้ำ" error>CALL sp_enroll('60004', 52);</sql>
<sql title="ยังไม่ผ่านวิชาบังคับก่อน — 60015 ไม่เคยเรียน CS004" error>CALL sp_enroll('60015', 52);</sql>
<sql title="ไม่พบรหัสนิสิต" error>CALL sp_enroll('99999', 52);</sql>
<h3>ตัวอย่างที่ 11.7 — sp_move_section: ทรานแซกชัน + EXIT HANDLER</h3>
<p>ย้ายนิสิตจากกลุ่มหนึ่งไปอีกกลุ่ม (ลบ + เพิ่ม) — ถ้าขั้นใดล้มเหลว HANDLER จะ ROLLBACK ทั้งหมด ข้อมูลไม่ค้างครึ่งทาง</p>
<sql title="สร้าง sp_move_section" exec>DELIMITER $$

CREATE PROCEDURE sp_move_section (IN p_sid VARCHAR(10), IN p_from INT, IN p_to INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;     -- ยกเลิกทุกอย่างที่ทำไปในทรานแซกชันนี้
        RESIGNAL;     -- ส่ง error เดิมกลับไปให้ผู้เรียกเห็น
    END;

    START TRANSACTION;
        DELETE FROM enroll WHERE secid = p_from AND stdid = p_sid;
        INSERT INTO enroll (secid, stdid) VALUES (p_to, p_sid);
    COMMIT;
    SELECT CONCAT('ย้าย ', p_sid, ' จากกลุ่ม ', p_from, ' ไปกลุ่ม ', p_to, ' สำเร็จ') AS message;
END $$

DELIMITER ;</sql>
<sql title="ย้ายไปกลุ่มที่ไม่มีอยู่จริง (999) → error และ ROLLBACK" error>CALL sp_move_section('60008', 51, 999);</sql>
<sql title="ตรวจ — 60008 ยังอยู่ในกลุ่ม 51 (การลบถูกย้อนกลับ)" run>SELECT * FROM enroll WHERE stdid = '60008' AND secid IN (51, 999);</sql>
<sql title="ย้ายไปกลุ่มที่มีอยู่จริง (44) → สำเร็จ" run>CALL sp_move_section('60008', 51, 44);
SELECT * FROM enroll WHERE stdid = '60008' AND secid IN (51, 44);</sql>

<ex no="11.3" title="sp_drop_enroll" level="2">
<p>จงเขียนโพรซีเยอร์ <code>sp_drop_enroll(p_sid, p_secid)</code> ถอนรายวิชา โดยอนุญาตเฉพาะรายการที่<b>ยังไม่มีเกรด</b> ถ้ามีเกรดแล้วหรือไม่พบรายการ ให้แจ้ง error</p>
<answer><sql title="เฉลย" exec>DELIMITER $$
CREATE PROCEDURE sp_drop_enroll (IN p_sid VARCHAR(10), IN p_secid INT)
BEGIN
    DECLARE v_grade CHAR(1);
    DECLARE v_found INT DEFAULT 0;

    SELECT COUNT(*), MAX(grade) INTO v_found, v_grade
    FROM   enroll WHERE secid = p_secid AND stdid = p_sid;

    IF v_found = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ไม่พบรายการลงทะเบียน';
    ELSEIF v_grade IS NOT NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'มีเกรดแล้ว ถอนไม่ได้';
    END IF;

    DELETE FROM enroll WHERE secid = p_secid AND stdid = p_sid;
    SELECT 'ถอนรายวิชาสำเร็จ' AS message;
END $$
DELIMITER ;</sql>
<sql title="ทดสอบ — มีเกรดแล้ว" error>CALL sp_drop_enroll('60001', 1);</sql>
<sql title="ทดสอบ — ยังไม่มีเกรด (70034 ใน secid 51)" run>CALL sp_drop_enroll('70034', 51);</sql></answer>
</ex>
''')
t = t.replace('<sql title="ดู / ลบโพรซีเยอร์" run>SHOW PROCEDURE STATUS WHERE Db = DATABASE();</sql>',
              '<sql title="ดู / ลบโพรซีเยอร์" run>SHOW PROCEDURE STATUS WHERE Db = DATABASE();</sql>\n<div class="code"><div class="code-head"><span>คำสั่งจัดการอื่น ๆ</span></div><pre class="sql">SHOW CREATE PROCEDURE sp_count_credit;   -- ดูโค้ด\nDROP PROCEDURE IF EXISTS sp_count_credit;  -- ลบ (แก้โค้ดต้อง DROP แล้ว CREATE ใหม่)</pre></div>')
p.write_text(t, encoding='utf-8')

# ---------------- ch12
p = pathlib.Path('src/12-trigger.html'); t = p.read_text(encoding='utf-8')
t = t.replace('SYNTAX_PLACEHOLDER', '''<h2 id="s2"><span class="sec">12.2</span> โครงสร้างคำสั่ง CREATE TRIGGER</h2>
<div class="code"><div class="code-head"><span>รูปแบบคำสั่ง</span></div><pre class="sql">DELIMITER $$
CREATE TRIGGER ชื่อทริกเกอร์
{BEFORE | AFTER} {INSERT | UPDATE | DELETE} ON ชื่อตาราง
FOR EACH ROW
[{FOLLOWS | PRECEDES} ทริกเกอร์อื่น]
BEGIN
    -- อ้างถึงค่าเดิมด้วย OLD.คอลัมน์ และค่าใหม่ด้วย NEW.คอลัมน์
END $$
DELIMITER ;</pre></div>
<ul>
<li><b>FOR EACH ROW</b> — ทำงาน<b>ทีละแถว</b> เช่น UPDATE กระทบ 10 แถว ทริกเกอร์ทำงาน 10 ครั้ง</li>
<li>ตั้งชื่อ <code>tg_ตาราง_จังหวะ_เหตุการณ์</code> เช่น <code>tg_enroll_before_insert</code> จะรู้ทันทีว่าทำงานเมื่อใด</li>
<li>ใน BEFORE แก้ค่า <code>NEW.คอลัมน์</code> ได้ (เปลี่ยนค่าก่อนบันทึก) ใน AFTER แก้ไม่ได้ เพราะบันทึกไปแล้ว</li>
<li>ห้ามแก้ไขตารางเดียวกับที่กระตุ้นทริกเกอร์ (Error 1442) และห้ามใช้ COMMIT / ROLLBACK ในทริกเกอร์</li>
</ul>
<sql title="ทริกเกอร์แรก — ทำรหัสวิชาให้เป็นตัวพิมพ์ใหญ่และตัดช่องว่างอัตโนมัติ" exec>DELIMITER $$

CREATE TRIGGER tg_subject_before_insert
BEFORE INSERT ON subject
FOR EACH ROW
BEGIN
    SET NEW.subid = UPPER(TRIM(NEW.subid));
    SET NEW.name  = TRIM(NEW.name);
END $$

DELIMITER ;</sql>
<sql title="ทดสอบ — ป้อน ' cs011 ' ตัวพิมพ์เล็กมีช่องว่าง" run show="SELECT * FROM subject WHERE subid = 'CS011'">INSERT INTO subject (subid, name, credit, major) VALUES (' cs011 ', '  Cloud Computing ', 3, 'CS');</sql>
''')
t = t.replace('SUMMARY_PLACEHOLDER', '''<h2 id="s6"><span class="sec">12.6</span> รักษาข้อมูลสรุปให้สอดคล้องอัตโนมัติ</h2>
<p>บางครั้งเราเลือก<b>ดีนอร์มัลไลซ์</b> (บทที่ 3) เก็บค่าสรุปไว้ในตาราง เพื่อให้อ่านเร็ว เช่น จำนวนนิสิตในแต่ละกลุ่มเรียน — ความเสี่ยงคือค่าไม่ตรงกับข้อมูลจริง ทริกเกอร์ช่วยปรับค่าให้อัตโนมัติทุกครั้งที่มีการเปลี่ยนแปลง</p>
<sql title="ขั้นที่ 1 — เพิ่มคอลัมน์ n_student ใน section และกำหนดค่าเริ่มต้นจากข้อมูลจริง" run max="6">ALTER TABLE section ADD COLUMN n_student INT NOT NULL DEFAULT 0;

UPDATE section sec
SET    n_student = (SELECT COUNT(*) FROM enroll e WHERE e.secid = sec.secid);

SELECT secid, subid, term, n_student FROM section WHERE term = '2026-1' OR secid <= 3;</sql>
<sql title="ขั้นที่ 2 — ทริกเกอร์เพิ่ม/ลดจำนวนเมื่อมีการลงทะเบียน/ถอน" exec>DELIMITER $$

CREATE TRIGGER tg_enroll_after_insert_count
AFTER INSERT ON enroll
FOR EACH ROW
BEGIN
    UPDATE section SET n_student = n_student + 1 WHERE secid = NEW.secid;
END $$

CREATE TRIGGER tg_enroll_after_delete_count
AFTER DELETE ON enroll
FOR EACH ROW
BEGIN
    UPDATE section SET n_student = n_student - 1 WHERE secid = OLD.secid;
END $$

DELIMITER ;</sql>
<sql title="ขั้นที่ 3 — ทดสอบ: ลง 2 คน ถอน 1 คน ในกลุ่ม 52" run>INSERT INTO enroll (secid, stdid) VALUES (52, '60014'), (52, '60016');
DELETE FROM enroll WHERE secid = 52 AND stdid = '60016';
SELECT sec.secid, sec.n_student AS stored_count,
       (SELECT COUNT(*) FROM enroll e WHERE e.secid = sec.secid) AS real_count
FROM   section sec WHERE secid = 52;</sql>
<div class="box note"><div class="box-t">📝 ทางเลือก: วิว vs ทริกเกอร์</div><p>วิว (บทที่ 7) คำนวณใหม่ทุกครั้ง — ถูกต้องเสมอแต่ช้าเมื่อข้อมูลมาก ส่วนเก็บค่าไว้ + ทริกเกอร์ — อ่านเร็วมากแต่ซับซ้อนกว่า และถ้ามีคนปิดทริกเกอร์หรือแก้ข้อมูลด้วยวิธีอื่น ค่าอาจไม่ตรง ควรมีคำสั่งตรวจ/คำนวณใหม่ (เช่นขั้นที่ 1) ไว้ใช้เป็นระยะ</p></div>
''')
t = t.replace('<ex no="12.1" title="ห้ามลดเงินเดือน"', '''<h3>ห้ามแก้ตารางเดียวกับที่กระตุ้นทริกเกอร์ (Error 1442)</h3>
<sql title="ทริกเกอร์บน student ที่พยายาม UPDATE student" exec>DELIMITER $$
CREATE TRIGGER tg_student_bad
AFTER INSERT ON student
FOR EACH ROW
BEGIN
    UPDATE student SET gpa = 0 WHERE stdid = NEW.stdid;
END $$
DELIMITER ;</sql>
<sql title="INSERT → error ตอนทริกเกอร์ทำงาน (แก้โดยใช้ BEFORE + SET NEW.gpa = 0 แทน)" error>INSERT INTO student (stdid, name, major) VALUES ('80020', 'Tanjiro', 'CS');</sql>
<sql title="ลบทริกเกอร์ที่ผิด" exec>DROP TRIGGER tg_student_bad;</sql>

<ex no="12.1" title="ห้ามลดเงินเดือน"''')
p.write_text(t, encoding='utf-8')
