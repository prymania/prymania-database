# ============================================================
#  db.py — ชั้นติดต่อฐานข้อมูล (SQL ทุกคำสั่งของเว็บอยู่ในไฟล์นี้)
#  ฐานข้อมูล: student, lecturer, subject, section, enroll
#  (ชุดเดียวกับ prymania_DBLabScript.sql ที่ใช้ในชั้นเรียน)
#
#  ★ ทุกฟังก์ชันคืนค่า {"sql": ..., "rows": ...}
#    หน้าเว็บจะแสดงทั้ง "ผลลัพธ์" และ "SQL ที่รันจริง" (ปุ่ม 🔍 SQL)
#  ★ ใช้ %s เป็น placeholder เสมอ (กัน SQL injection)
# ============================================================
import re
import pathlib
import mysql.connector
import config


def get_connection(with_db=True):
    return mysql.connector.connect(
        host=config.DB_HOST, user=config.DB_USER, password=config.DB_PASSWORD,
        database=config.DB_NAME if with_db else None, port=config.DB_PORT)


def tidy(sql):
    """ตัดช่องว่างหน้าบรรทัดที่เกิดจากการย่อหน้าในโค้ด Python ให้ SQL ที่แสดงบนเว็บอ่านง่าย"""
    lines = sql.strip("\n").splitlines()
    ind = lambda l: len(l) - len(l.lstrip())
    base = [ind(l) for l in lines[1:] if re.match(r"\s+(FROM|WHERE|GROUP|ORDER)\b", l)]
    pad = base[0] if base else min((ind(l) for l in lines[1:] if l.strip()), default=7) - 7
    # บรรทัด AND ที่ add_filter ต่อท้าย ไม่มีย่อหน้าตามโค้ด → ย่อหน้าให้ 2 ช่องใต้ WHERE
    return "\n".join([lines[0].strip()] + [l[min(pad, ind(l)):] if ind(l) >= pad else "  " + l.strip()
                                           for l in lines[1:]])


def run_query(sql, params=None):
    """รัน SELECT → {"sql": คำสั่งที่รันจริง (แทนค่า %s แล้ว), "rows": list ของ dict}"""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ()); rows = cur.fetchall()
    out = {"sql": tidy(cur.statement), "rows": rows}
    cur.close(); conn.close(); return out


def run_command(sql, params=None):
    """รัน INSERT / UPDATE / DELETE แล้ว commit"""
    conn = get_connection(); cur = conn.cursor()
    cur.execute(sql, params or ()); conn.commit()
    out = {"sql": tidy(cur.statement), "rows": [], "affected": cur.rowcount}
    cur.close(); conn.close(); return out


def blank_to_none(value):
    """ช่องที่ไม่ได้กรอกในฟอร์มส่งมาเป็น "" → แปลงเป็น None (= NULL ใน SQL)"""
    return None if value in ("", None) else value


def add_filter(sql, params, cond, value):
    """ต่อเงื่อนไข WHERE เฉพาะช่องค้นหาที่กรอก"""
    if value not in ("", None):
        sql += "\n  AND " + cond
        params.append(value)
    return sql


# ============================================================
#  ข้อมูลสำหรับ dropdown  (/api/lookup/<name>)
# ============================================================
LOOKUPS = {
    "student_majors": "SELECT DISTINCT major AS value, major AS label FROM student WHERE major IS NOT NULL ORDER BY major",
    "lecturer_majors": "SELECT DISTINCT major AS value, major AS label FROM lecturer WHERE major IS NOT NULL ORDER BY major",
    "subject_majors": "SELECT DISTINCT major AS value, major AS label FROM subject WHERE major IS NOT NULL ORDER BY major",
    "terms": "SELECT DISTINCT term AS value, term AS label FROM section ORDER BY term",
    "students": "SELECT stdid AS value, CONCAT(stdid, ' · ', IFNULL(name, '(ไม่มีชื่อ)')) AS label FROM student ORDER BY stdid",
    "lecturers": "SELECT lecid AS value, CONCAT(lecid, ' · ', name) AS label FROM lecturer ORDER BY lecid",
    "subjects": "SELECT subid AS value, CONCAT(subid, ' · ', name) AS label FROM subject ORDER BY subid",
    "sections": """SELECT sec.secid AS value,
                          CONCAT(sec.secid, ' · ', sec.term, ' · ', sub.subid, ' ', sub.name, ' (', l.name, ')') AS label
                   FROM section sec
                   INNER JOIN subject sub ON sec.subid = sub.subid
                   INNER JOIN lecturer l  ON sec.lecid = l.lecid
                   ORDER BY sec.term, sec.secid""",
}


def lookup(name):
    return run_query(LOOKUPS[name])


# ============================================================
#  นิสิต (student)
# ============================================================
def search_students(f):
    """นิสิต + อายุ (คำนวณจาก birthday) + จำนวนวิชาที่ลงทะเบียน (LEFT JOIN enroll → คนที่ไม่เคยลงได้ 0)"""
    sql = """SELECT s.stdid, s.name, s.major, s.gpa, s.birthday,
                    TIMESTAMPDIFF(YEAR, s.birthday, CURDATE()) AS age,
                    COUNT(e.secid) AS n_enroll
             FROM student s
             LEFT JOIN enroll e ON s.stdid = e.stdid
             WHERE 1=1"""
    p = []
    sql = add_filter(sql, p, "s.stdid LIKE %s", f.get("stdid") and f["stdid"] + "%")
    sql = add_filter(sql, p, "s.name LIKE %s", f.get("name") and "%" + f["name"] + "%")
    sql = add_filter(sql, p, "s.major = %s", f.get("major"))
    sql = add_filter(sql, p, "s.gpa >= %s", f.get("gpa_min"))
    sql += "\nGROUP BY s.stdid\nORDER BY s.stdid"
    return run_query(sql, p)


def get_student(stdid):
    return run_query("SELECT * FROM student WHERE stdid = %s", (stdid,))


def create_student(d):
    return run_command("INSERT INTO student (stdid, name, major, gpa, birthday) VALUES (%s, %s, %s, %s, %s)",
                       (d["stdid"], blank_to_none(d["name"]), blank_to_none(d["major"]),
                        blank_to_none(d["gpa"]), blank_to_none(d["birthday"])))


def update_student(stdid, d):
    return run_command("UPDATE student SET name = %s, major = %s, gpa = %s, birthday = %s WHERE stdid = %s",
                       (blank_to_none(d["name"]), blank_to_none(d["major"]), blank_to_none(d["gpa"]),
                        blank_to_none(d["birthday"]), stdid))


def delete_student(stdid):
    return run_command("DELETE FROM student WHERE stdid = %s", (stdid,))


def student_transcript(stdid):
    """📄 ผลการเรียนของนิสิต 1 คน — JOIN enroll → section → subject → lecturer
    แปลงเกรดเป็นแต้มด้วย CASE (A=4 … F=0)"""
    sql = """SELECT sec.term, sub.subid AS sub_id, sub.name AS sub_name, sub.credit,
                    l.name AS lec_name, e.grade,
                    CASE e.grade WHEN 'A' THEN 4 WHEN 'B' THEN 3 WHEN 'C' THEN 2
                                 WHEN 'D' THEN 1 WHEN 'F' THEN 0 END AS point
             FROM enroll e
             INNER JOIN section sec ON e.secid = sec.secid
             INNER JOIN subject sub ON sec.subid = sub.subid
             INNER JOIN lecturer l  ON sec.lecid = l.lecid
             WHERE e.stdid = %s
             ORDER BY sec.term, sub.subid"""
    return run_query(sql, (stdid,))


# ============================================================
#  อาจารย์ (lecturer)
# ============================================================
def search_lecturers(f):
    """อาจารย์ + จำนวนกลุ่มเรียนที่สอน (LEFT JOIN section → คนที่ไม่มีกลุ่มเรียนได้ 0)"""
    sql = """SELECT l.lecid, l.name, l.salary, l.major,
                    COUNT(sec.secid) AS n_section
             FROM lecturer l
             LEFT JOIN section sec ON l.lecid = sec.lecid
             WHERE 1=1"""
    p = []
    sql = add_filter(sql, p, "l.name LIKE %s", f.get("name") and "%" + f["name"] + "%")
    sql = add_filter(sql, p, "l.major = %s", f.get("major"))
    sql = add_filter(sql, p, "l.salary >= %s", f.get("salary_min"))
    sql += "\nGROUP BY l.lecid\nORDER BY l.lecid"
    return run_query(sql, p)


def get_lecturer(lecid):
    return run_query("SELECT * FROM lecturer WHERE lecid = %s", (lecid,))


def create_lecturer(d):
    return run_command("INSERT INTO lecturer (lecid, name, salary, major) VALUES (%s, %s, %s, %s)",
                       (d["lecid"], blank_to_none(d["name"]), blank_to_none(d["salary"]), blank_to_none(d["major"])))


def update_lecturer(lecid, d):
    return run_command("UPDATE lecturer SET name = %s, salary = %s, major = %s WHERE lecid = %s",
                       (blank_to_none(d["name"]), blank_to_none(d["salary"]), blank_to_none(d["major"]), lecid))


def delete_lecturer(lecid):
    return run_command("DELETE FROM lecturer WHERE lecid = %s", (lecid,))


def lecturer_sections(lecid):
    """📚 กลุ่มเรียนที่อาจารย์สอน + จำนวนนิสิตในแต่ละกลุ่ม"""
    sql = """SELECT sec.secid, sec.term, sub.subid AS sub_id, sub.name AS sub_name,
                    COUNT(e.stdid) AS n_student
             FROM section sec
             INNER JOIN subject sub ON sec.subid = sub.subid
             LEFT JOIN enroll e     ON sec.secid = e.secid
             WHERE sec.lecid = %s
             GROUP BY sec.secid
             ORDER BY sec.term, sec.secid"""
    return run_query(sql, (lecid,))


# ============================================================
#  รายวิชา (subject) — มีวิชาบังคับก่อน (pre) อ้างถึงตารางตัวเอง
# ============================================================
def search_subjects(f):
    """วิชา + ชื่อวิชาบังคับก่อน — Self Join: subject s ⟕ subject p
    ใช้ LEFT JOIN เพราะวิชาที่ไม่มีวิชาบังคับก่อน (pre = NULL) ต้องยังแสดงอยู่"""
    sql = """SELECT s.subid, s.name, s.credit, s.major,
                    s.pre  AS pre_subid,
                    p.name AS pre_subname
             FROM subject s
             LEFT JOIN subject p ON s.pre = p.subid
             WHERE 1=1"""
    p = []
    sql = add_filter(sql, p, "s.subid LIKE %s", f.get("subid") and f["subid"] + "%")
    sql = add_filter(sql, p, "s.name LIKE %s", f.get("name") and "%" + f["name"] + "%")
    sql = add_filter(sql, p, "s.major = %s", f.get("major"))
    sql = add_filter(sql, p, "s.credit = %s", f.get("credit"))
    sql += "\nORDER BY s.subid"
    return run_query(sql, p)


def get_subject(subid):
    return run_query("SELECT * FROM subject WHERE subid = %s", (subid,))


def create_subject(d):
    return run_command("INSERT INTO subject (subid, name, credit, major, pre) VALUES (%s, %s, %s, %s, %s)",
                       (d["subid"], d["name"], blank_to_none(d["credit"]), blank_to_none(d["major"]),
                        blank_to_none(d["pre"])))


def update_subject(subid, d):
    return run_command("UPDATE subject SET name = %s, credit = %s, major = %s, pre = %s WHERE subid = %s",
                       (d["name"], blank_to_none(d["credit"]), blank_to_none(d["major"]),
                        blank_to_none(d["pre"]), subid))


def delete_subject(subid):
    return run_command("DELETE FROM subject WHERE subid = %s", (subid,))


def subject_next(subid):
    """🔗 วิชาที่ต้องเรียนวิชานี้ก่อน (วิชาต่อเนื่อง) + จำนวนกลุ่มเรียนที่เคยเปิด"""
    sql = """SELECT s.subid, s.name, s.credit,
                    (SELECT COUNT(*) FROM section sec WHERE sec.subid = s.subid) AS n_section
             FROM subject s
             WHERE s.pre = %s
             ORDER BY s.subid"""
    return run_query(sql, (subid,))


# ============================================================
#  กลุ่มเรียน (section) — JOIN subject + lecturer
# ============================================================
def search_sections(f):
    """กลุ่มเรียน + ชื่อวิชา + ชื่ออาจารย์ + จำนวนนิสิต
    INNER JOIN subject / lecturer (ทุกกลุ่มมีวิชาและอาจารย์) · LEFT JOIN enroll (กลุ่มที่ไม่มีคนลงได้ 0)"""
    sql = """SELECT sec.secid, sec.term,
                    sec.subid AS sub_id, sub.name AS sub_name, sub.credit,
                    sec.lecid AS lec_id, l.name   AS lec_name,
                    COUNT(e.stdid) AS n_student
             FROM section sec
             INNER JOIN subject sub ON sec.subid = sub.subid
             INNER JOIN lecturer l  ON sec.lecid = l.lecid
             LEFT JOIN enroll e     ON sec.secid = e.secid
             WHERE 1=1"""
    p = []
    sql = add_filter(sql, p, "sec.term = %s", f.get("term"))
    sql = add_filter(sql, p, "sec.subid = %s", f.get("subid"))
    sql = add_filter(sql, p, "sec.lecid = %s", f.get("lecid"))
    sql += "\nGROUP BY sec.secid\nORDER BY sec.term, sec.secid"
    return run_query(sql, p)


def get_section(secid):
    return run_query("SELECT * FROM section WHERE secid = %s", (secid,))


def create_section(d):
    """secid เป็น AUTO_INCREMENT → ไม่ต้องใส่ MySQL ออกเลขให้เอง"""
    return run_command("INSERT INTO section (subid, lecid, term) VALUES (%s, %s, %s)",
                       (d["subid"], d["lecid"], d["term"]))


def update_section(secid, d):
    return run_command("UPDATE section SET subid = %s, lecid = %s, term = %s WHERE secid = %s",
                       (d["subid"], d["lecid"], d["term"], secid))


def delete_section(secid):
    return run_command("DELETE FROM section WHERE secid = %s", (secid,))


def section_roster(secid):
    """👥 รายชื่อนิสิตในกลุ่มเรียน + เกรด"""
    sql = """SELECT st.stdid, st.name, st.major, e.grade
             FROM enroll e
             INNER JOIN student st ON e.stdid = st.stdid
             WHERE e.secid = %s
             ORDER BY st.stdid"""
    return run_query(sql, (secid,))


# ============================================================
#  การลงทะเบียน (enroll) — PK 2 คอลัมน์ (secid, stdid)
# ============================================================
def search_enrolls(f):
    """การลงทะเบียน + ภาคเรียน + วิชา + ชื่อนิสิต — JOIN 4 ตาราง"""
    sql = """SELECT e.secid, sec.term,
                    sub.subid AS sub_id, sub.name AS sub_name,
                    e.stdid, st.name AS std_name,
                    e.grade
             FROM enroll e
             INNER JOIN section sec ON e.secid = sec.secid
             INNER JOIN subject sub ON sec.subid = sub.subid
             INNER JOIN student st  ON e.stdid = st.stdid
             WHERE 1=1"""
    p = []
    sql = add_filter(sql, p, "e.stdid = %s", f.get("stdid"))
    sql = add_filter(sql, p, "sec.term = %s", f.get("term"))
    sql = add_filter(sql, p, "sec.subid = %s", f.get("subid"))
    sql = add_filter(sql, p, "e.grade = %s", f.get("grade"))
    sql += "\nORDER BY sec.term, e.secid, e.stdid"
    return run_query(sql, p)


def _enroll_key(key):
    secid, stdid = key.split("/", 1)
    return int(secid), stdid


def get_enroll(key):
    return run_query("SELECT * FROM enroll WHERE secid = %s AND stdid = %s", _enroll_key(key))


def create_enroll(d):
    return run_command("INSERT INTO enroll (secid, stdid, grade) VALUES (%s, %s, %s)",
                       (d["secid"], d["stdid"], blank_to_none(d["grade"])))


def update_enroll(key, d):
    """แก้ได้เฉพาะเกรด — secid, stdid เป็น PK"""
    return run_command("UPDATE enroll SET grade = %s WHERE secid = %s AND stdid = %s",
                       (blank_to_none(d["grade"]),) + _enroll_key(key))


def delete_enroll(key):
    return run_command("DELETE FROM enroll WHERE secid = %s AND stdid = %s", _enroll_key(key))


# ============================================================
#  ตารางที่หน้าเว็บใช้: ชื่อแท็บ → ฟังก์ชัน (app.py สร้าง URL ให้ครบจากรายการนี้)
# ============================================================
ENTITIES = {
    "students":  dict(search=search_students,  get=get_student,  create=create_student,
                      update=update_student,  delete=delete_student),
    "lecturers": dict(search=search_lecturers, get=get_lecturer, create=create_lecturer,
                      update=update_lecturer, delete=delete_lecturer),
    "subjects":  dict(search=search_subjects,  get=get_subject,  create=create_subject,
                      update=update_subject,  delete=delete_subject),
    "sections":  dict(search=search_sections,  get=get_section,  create=create_section,
                      update=update_section,  delete=delete_section),
    "enrolls":   dict(search=search_enrolls,   get=get_enroll,   create=create_enroll,
                      update=update_enroll,   delete=delete_enroll),
}

# ข้อมูลเชิงลึกของ 1 แถว (ปุ่มในตาราง) → /api/<entity>/<key>/<detail>
DETAILS = {
    ("students", "transcript"): student_transcript,
    ("lecturers", "sections"): lecturer_sections,
    ("subjects", "next"): subject_next,
    ("sections", "roster"): section_roster,
}


# ============================================================
#  Dashboard
# ============================================================
GRADE_POINT = "CASE e.grade WHEN 'A' THEN 4 WHEN 'B' THEN 3 WHEN 'C' THEN 2 WHEN 'D' THEN 1 WHEN 'F' THEN 0 END"


def report_summary():
    """การ์ดตัวเลขด้านบน — scalar subquery หลายตัวในคำสั่งเดียว"""
    sql = """SELECT (SELECT COUNT(*) FROM student)  AS 'นิสิต',
                    (SELECT COUNT(*) FROM lecturer) AS 'อาจารย์',
                    (SELECT COUNT(*) FROM subject)  AS 'รายวิชา',
                    (SELECT COUNT(*) FROM section)  AS 'กลุ่มเรียน',
                    (SELECT COUNT(*) FROM enroll)   AS 'การลงทะเบียน',
                    (SELECT ROUND(AVG(gpa), 2) FROM student) AS 'GPA เฉลี่ย (ตาราง student)',
                    (SELECT CONCAT(ROUND(100 * AVG(grade <> 'F'), 1), '%') FROM enroll) AS 'อัตราสอบผ่าน'"""
    return run_query(sql)


def report_students_by_major():
    """👩‍🎓 นิสิตแยกตามสาขา — GROUP BY + IFNULL แทนสาขาที่เป็น NULL"""
    sql = """SELECT IFNULL(major, '(ไม่ระบุ)') AS major,
                    COUNT(*)           AS n_student,
                    ROUND(AVG(gpa), 2) AS avg_gpa,
                    MAX(gpa)           AS max_gpa
             FROM student
             GROUP BY major
             ORDER BY COUNT(*) DESC, major"""
    return run_query(sql)


def report_grade_distribution():
    """🅰️ การกระจายของเกรด — COUNT + ร้อยละด้วย subquery หาจำนวนทั้งหมด"""
    sql = """SELECT IFNULL(grade, '(ยังไม่มีเกรด)') AS grade,
                    COUNT(*) AS n,
                    ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM enroll), 1) AS percent
             FROM enroll
             GROUP BY grade
             ORDER BY grade IS NULL, grade"""
    return run_query(sql)


def report_by_term():
    """🗓️ จำนวนกลุ่มเรียนและการลงทะเบียนแต่ละภาคเรียน — COUNT(DISTINCT) + LEFT JOIN"""
    sql = """SELECT sec.term,
                    COUNT(DISTINCT sec.secid) AS n_section,
                    COUNT(e.stdid)            AS n_enroll,
                    COUNT(DISTINCT e.stdid)   AS n_student
             FROM section sec
             LEFT JOIN enroll e ON sec.secid = e.secid
             GROUP BY sec.term
             ORDER BY sec.term"""
    return run_query(sql)


def report_popular_subjects():
    """🔥 วิชายอดนิยม 5 อันดับ (นับจำนวนครั้งที่ลงทะเบียนทุกภาคเรียน)"""
    sql = """SELECT sub.subid AS sub_id, sub.name AS sub_name,
                    COUNT(DISTINCT sec.secid) AS n_section,
                    COUNT(e.stdid)            AS n_enroll
             FROM subject sub
             INNER JOIN section sec ON sub.subid = sec.subid
             INNER JOIN enroll e    ON sec.secid = e.secid
             GROUP BY sub.subid
             ORDER BY n_enroll DESC, sub.subid
             LIMIT 5"""
    return run_query(sql)


def report_pass_rate():
    """✅ อัตราสอบผ่านรายวิชา — SUM(เงื่อนไข) นับเฉพาะแถวที่เงื่อนไขเป็นจริง"""
    sql = """SELECT sub.subid AS sub_id, sub.name AS sub_name,
                    COUNT(*)                AS n_student,
                    SUM(e.grade <> 'F')     AS n_pass,
                    SUM(e.grade = 'F')      AS n_fail,
                    ROUND(100 * AVG(e.grade <> 'F'), 1) AS pass_rate
             FROM enroll e
             INNER JOIN section sec ON e.secid = sec.secid
             INNER JOIN subject sub ON sec.subid = sub.subid
             GROUP BY sub.subid
             ORDER BY pass_rate, sub.subid"""
    return run_query(sql)


def report_top_students():
    """🏆 นิสิตเกรดเฉลี่ยสูงสุด 5 อันดับ — คำนวณจากผลการเรียนจริง (Σ แต้ม×หน่วยกิต / Σ หน่วยกิต)"""
    sql = f"""SELECT st.stdid, st.name, st.major,
                     SUM(sub.credit) AS credits,
                     ROUND(SUM({GRADE_POINT} * sub.credit) / SUM(sub.credit), 2) AS gpax
              FROM enroll e
              INNER JOIN student st  ON e.stdid = st.stdid
              INNER JOIN section sec ON e.secid = sec.secid
              INNER JOIN subject sub ON sec.subid = sub.subid
              GROUP BY st.stdid
              ORDER BY gpax DESC, credits DESC
              LIMIT 5"""
    return run_query(sql)


def report_lecturer_load():
    """👨‍🏫 ภาระงานสอนของอาจารย์ — LEFT JOIN 2 ชั้น อาจารย์ที่ไม่มีกลุ่มเรียนยังแสดงเป็น 0"""
    sql = """SELECT l.lecid AS lec_id, l.name AS lec_name, l.major,
                    COUNT(DISTINCT sec.secid) AS n_section,
                    COUNT(e.stdid)            AS n_student
             FROM lecturer l
             LEFT JOIN section sec ON l.lecid = sec.lecid
             LEFT JOIN enroll e    ON sec.secid = e.secid
             GROUP BY l.lecid
             ORDER BY n_student DESC, l.lecid"""
    return run_query(sql)


def report_salary_by_major():
    """💰 เงินเดือนอาจารย์แยกตามสาขา — AVG / MIN / MAX ไม่นับ NULL"""
    sql = """SELECT major,
                    COUNT(*)       AS n_lecturer,
                    COUNT(salary)  AS n_has_salary,
                    ROUND(AVG(salary)) AS avg_salary,
                    MIN(salary)    AS min_salary,
                    MAX(salary)    AS max_salary
             FROM lecturer
             GROUP BY major
             ORDER BY avg_salary DESC"""
    return run_query(sql)


def report_empty_sections():
    """💤 กลุ่มเรียนที่ไม่มีนิสิตลงทะเบียน — NOT EXISTS"""
    sql = """SELECT sec.secid, sec.term, sub.name AS sub_name, l.name AS lec_name
             FROM section sec
             INNER JOIN subject sub ON sec.subid = sub.subid
             INNER JOIN lecturer l  ON sec.lecid = l.lecid
             WHERE NOT EXISTS (SELECT *
                               FROM enroll e
                               WHERE e.secid = sec.secid)
             ORDER BY sec.secid"""
    return run_query(sql)


def report_never_enrolled():
    """🚫 นิสิตที่ยังไม่เคยลงทะเบียนเลย — LEFT JOIN ... WHERE e.stdid IS NULL"""
    sql = """SELECT st.stdid, st.name, st.major
             FROM student st
             LEFT JOIN enroll e ON st.stdid = e.stdid
             WHERE e.stdid IS NULL
             ORDER BY st.stdid"""
    return run_query(sql)


# (key, หัวข้อ, ฟังก์ชัน, คอลัมน์ที่วาดแท่งกราฟ)
REPORTS = [
    ("by-major",     "👩‍🎓 นิสิตแยกตามสาขา",                  report_students_by_major,  "n_student"),
    ("grades",       "🅰️ การกระจายของเกรด",                     report_grade_distribution, "n"),
    ("by-term",      "🗓️ กลุ่มเรียนและการลงทะเบียนแต่ละภาค",     report_by_term,            "n_enroll"),
    ("popular",      "🔥 วิชายอดนิยม 5 อันดับ",                  report_popular_subjects,   "n_enroll"),
    ("top-students", "🏆 เกรดเฉลี่ยสะสมสูงสุด 5 อันดับ (คำนวณจากผลการเรียน)", report_top_students, "gpax"),
    ("pass-rate",    "✅ อัตราสอบผ่านรายวิชา (เรียงจากผ่านน้อยไปมาก)", report_pass_rate,     "pass_rate"),
    ("load",         "👨‍🏫 ภาระงานสอนของอาจารย์",                 report_lecturer_load,      "n_student"),
    ("salary",       "💰 เงินเดือนอาจารย์แยกตามสาขา",            report_salary_by_major,    "avg_salary"),
    ("empty",        "💤 กลุ่มเรียนที่ไม่มีคนลงทะเบียน",           report_empty_sections,     None),
    ("never",        "🚫 นิสิตที่ยังไม่เคยลงทะเบียน",             report_never_enrolled,     None),
]


# ============================================================
#  โครงสร้างฐานข้อมูล (หน้า ER Diagram)
# ============================================================
def schema_columns():
    sql = """SELECT TABLE_NAME AS tbl, COLUMN_NAME AS col, COLUMN_TYPE AS type,
                    IS_NULLABLE AS nullable, COLUMN_KEY AS col_key, EXTRA AS extra
             FROM information_schema.COLUMNS
             WHERE TABLE_SCHEMA = DATABASE()
               AND TABLE_NAME IN ('student', 'lecturer', 'subject', 'section', 'enroll')
             ORDER BY FIELD(TABLE_NAME, 'student', 'lecturer', 'subject', 'section', 'enroll'),
                      ORDINAL_POSITION"""
    return run_query(sql)


def schema_foreign_keys():
    sql = """SELECT TABLE_NAME AS tbl, COLUMN_NAME AS col,
                    REFERENCED_TABLE_NAME AS ref_tbl, REFERENCED_COLUMN_NAME AS ref_col
             FROM information_schema.KEY_COLUMN_USAGE
             WHERE TABLE_SCHEMA = DATABASE() AND REFERENCED_TABLE_NAME IS NOT NULL
             ORDER BY TABLE_NAME, COLUMN_NAME"""
    return run_query(sql)


# ============================================================
#  รีเซ็ตข้อมูล — รัน schema.sql ใหม่ทั้งไฟล์ (สร้างฐานข้อมูลให้ถ้ายังไม่มี)
# ============================================================
def reset_database():
    text = (pathlib.Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)            # ตัด comment /* ... */
    text = re.sub(r"--[^\n]*", "", text)                         # ตัด comment -- ...
    stmts = [s.strip() for s in text.split(";") if s.strip()]
    stmts = [s for s in stmts if not re.match(r"(?i)(create database|use)\b", s)]
    conn = get_connection(with_db=False); cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}`")
    cur.execute(f"USE `{config.DB_NAME}`")
    for s in stmts:
        cur.execute(s)
    conn.commit(); cur.close(); conn.close()
    return {"sql": f"-- รัน schema.sql ใหม่ {len(stmts)} คำสั่ง", "rows": [], "affected": len(stmts)}
