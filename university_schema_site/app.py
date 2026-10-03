# ============================================================
#  app.py — เว็บแอป Flask: ระบบทะเบียนนิสิต (University Demo)
#  รัน:  python app.py  แล้วเปิด http://127.0.0.1:9001
#  ★ SQL ทุกคำสั่งอยู่ใน db.py — ไฟล์นี้แค่รับคำขอจากหน้าเว็บแล้วเรียก db.py
# ============================================================
from datetime import date, datetime
from decimal import Decimal
from flask import Flask, request, jsonify, render_template
from flask.json.provider import DefaultJSONProvider
import mysql.connector
import db


class JSONProvider(DefaultJSONProvider):
    """วันที่ → YYYY-MM-DD (ให้ <input type="date"> อ่านได้) · Decimal → ตัวเลข
       ไม่เรียงชื่อคอลัมน์ใหม่ → หัวตารางเรียงตามลำดับใน SELECT"""
    sort_keys = False

    @staticmethod
    def default(o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        if isinstance(o, Decimal):
            return str(o)
        return DefaultJSONProvider.default(o)


app = Flask(__name__)
app.json = JSONProvider(app)

# แปลง error ของ MySQL ให้เป็นข้อความที่นิสิตอ่านแล้วเข้าใจ
MYSQL_ERRORS = {
    1062: "ข้อมูลซ้ำ — มีค่า PRIMARY KEY / UNIQUE นี้อยู่แล้ว",
    1451: "ลบ/แก้ไม่ได้ — มีข้อมูลในตารางอื่นอ้างถึงแถวนี้อยู่ (FOREIGN KEY)",
    1452: "ไม่พบข้อมูลที่อ้างถึง — ค่าใน FOREIGN KEY ต้องมีอยู่ในตารางแม่",
    3819: "ค่าไม่ผ่านเงื่อนไข CHECK",
    1048: "คอลัมน์นี้ห้ามว่าง (NOT NULL)",
    1049: "ยังไม่มีฐานข้อมูลนี้ — กดปุ่ม ↺ รีเซ็ตข้อมูล เพื่อสร้าง",
    1146: "ยังไม่มีตาราง — กดปุ่ม ↺ รีเซ็ตข้อมูล เพื่อสร้าง",
}


def safe(fn, *args):
    try:
        out = fn(*args)
        return jsonify({"ok": True, "data": out["rows"], "sql": out["sql"], "affected": out.get("affected")})
    except mysql.connector.Error as e:
        msg = MYSQL_ERRORS.get(e.errno, "")
        return jsonify({"ok": False, "error": f"{msg} [MySQL {e.errno}] {e.msg}".strip()}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500


# ---------- หน้าเว็บ ----------
@app.route("/")
def page_home():
    return render_template("index.html", page="home")

@app.route("/dashboard")
def page_dashboard():
    return render_template("dashboard.html", page="dashboard")

@app.route("/schema")
def page_schema():
    return render_template("schema.html", page="schema")


# ---------- API ข้อมูล 5 ตาราง: /api/<entity> และ /api/<entity>/<key> ----------
# key ของ enroll มี 2 ส่วน เช่น /api/enrolls/12/60004 → ใช้ <path:key>
@app.route("/api/<entity>", methods=["GET"])
def entity_search(entity):
    filters = {k: v for k, v in request.args.items() if v}
    return safe(db.ENTITIES[entity]["search"], filters)

@app.route("/api/<entity>", methods=["POST"])
def entity_create(entity):
    return safe(db.ENTITIES[entity]["create"], request.json)

@app.route("/api/<entity>/<path:key>", methods=["GET"])
def entity_get(entity, key):
    # ข้อมูลเชิงลึก เช่น /api/students/60001/transcript
    head, _, tail = key.rpartition("/")
    if (entity, tail) in db.DETAILS:
        return safe(db.DETAILS[(entity, tail)], head)
    return safe(db.ENTITIES[entity]["get"], key)

@app.route("/api/<entity>/<path:key>", methods=["PUT"])
def entity_update(entity, key):
    return safe(db.ENTITIES[entity]["update"], key, request.json)

@app.route("/api/<entity>/<path:key>", methods=["DELETE"])
def entity_delete(entity, key):
    return safe(db.ENTITIES[entity]["delete"], key)


# ---------- dropdown ----------
@app.route("/lookup/<name>")
def lookup(name):
    return safe(db.lookup, name)


# ---------- dashboard ----------
@app.route("/report/summary")
def report_summary():
    return safe(db.report_summary)

@app.route("/report/list")
def report_list():
    return jsonify({"ok": True, "data": [{"key": k, "title": t, "bar": b} for k, t, _, b in db.REPORTS]})

@app.route("/report/run/<key>")
def report_run(key):
    for k, _, fn, _ in db.REPORTS:
        if k == key:
            return safe(fn)
    return jsonify({"ok": False, "error": f"ไม่พบรายงาน '{key}'"}), 404


# ---------- โครงสร้างฐานข้อมูล / รีเซ็ต ----------
@app.route("/schema/columns")
def schema_columns():
    return safe(db.schema_columns)

@app.route("/schema/fks")
def schema_fks():
    return safe(db.schema_foreign_keys)

@app.route("/reset", methods=["POST"])
def reset():
    return safe(db.reset_database)


if __name__ == "__main__":
    app.run(debug=True, port=9001)
