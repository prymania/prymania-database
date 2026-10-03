# -*- coding: utf-8 -*-
"""
build.py — สร้างเว็บ lecture note จาก src/*.html  ->  docs/*.html (GitHub Pages เปิดจากโฟลเดอร์ docs/)

แท็กพิเศษในไฟล์ src:
  <sql title="..." [run] [exec] [reset] [temp] [error] [max="10"] [show="SELECT ..."]>SQL</sql>
      run    = รันจริงแล้วแสดงผลลัพธ์ของ result set สุดท้าย (หรือจำนวนแถวที่ถูกกระทบ)
      exec   = รันจริงแต่ไม่แสดงผลลัพธ์
      reset  = โหลดฐานข้อมูลกรณีศึกษาใหม่ก่อนรันบล็อกนี้
      temp   = รันใน transaction แล้ว ROLLBACK ทิ้ง (ข้อมูลไม่เปลี่ยนสำหรับบล็อกถัดไป)
      error  = คาดว่าจะเกิด error -> แสดงข้อความ error ที่ MySQL ตอบกลับจริง
      show   = รันคำสั่งเพิ่มเติมหลังจากบล็อกนี้ แล้วแสดงผลลัพธ์ (เช่น ดูข้อมูลหลังแก้ไข)
      max    = จำนวนแถวสูงสุดที่แสดง
  <ex no="5.1" title="..." level="1-3"> โจทย์ ... <answer> เฉลย ... </answer></ex>
  <review> <li>...</li> ... </review>

ทุกหน้าเริ่มต้นด้วยฐานข้อมูลที่โหลดจาก prymania_DBLabScript.sql ใหม่เสมอ
"""
import html, json, re, sys, datetime, decimal, pathlib
import mysql.connector

ROOT = pathlib.Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT / "docs"
LAB_SCRIPT = ROOT / "prymania_DBLabScript.sql"
DB = dict(host="localhost", user="root", password="abcd1234")
DBNAME = "zz_lecture_build"
SHOWDB = "std_66011200"   # ชื่อฐานข้อมูลที่แสดงในผลลัพธ์/ข้อความ error

PAGES = [  # (file, nav-no, nav title, group)
    ("index.html", "🏠", "หน้าแรก / ภาพรวม", "เริ่มต้นที่นี่"),
    ("01-intro.html", "01", "ความรู้เบื้องต้นเกี่ยวกับระบบฐานข้อมูล", "ส่วนที่ 1 · ออกแบบฐานข้อมูล"),
    ("02-er-model.html", "02", "แบบจำลอง ER", "ส่วนที่ 1 · ออกแบบฐานข้อมูล"),
    ("03-relational-normalization.html", "03", "แปลง ER เป็นตาราง &amp; Normalization", "ส่วนที่ 1 · ออกแบบฐานข้อมูล"),
    ("04-sql-ddl-dml.html", "04", "สร้างตาราง &amp; INSERT/UPDATE/DELETE", "ส่วนที่ 2 · ภาษา SQL"),
    ("05-select.html", "05", "การแสดงข้อมูลด้วยคำสั่ง SELECT", "ส่วนที่ 2 · ภาษา SQL"),
    ("06-join.html", "06", "JOIN, Subquery &amp; จัดการข้อมูลขั้นสูง", "ส่วนที่ 2 · ภาษา SQL"),
    ("07-view.html", "07", "วิว (View)", "ส่วนที่ 3 · ขั้นสูง"),
    ("08-index.html", "08", "ดัชนี (Index)", "ส่วนที่ 3 · ขั้นสูง"),
    ("09-transaction.html", "09", "ทรานแซกชัน (Transaction)", "ส่วนที่ 3 · ขั้นสูง"),
    ("10-security.html", "10", "ความปลอดภัยของฐานข้อมูล", "ส่วนที่ 4 · ความปลอดภัย &amp; การเขียนโปรแกรม"),
    ("11-stored-procedure.html", "11", "Stored Procedure &amp; Function", "ส่วนที่ 4 · ความปลอดภัย &amp; การเขียนโปรแกรม"),
    ("12-trigger.html", "12", "ทริกเกอร์ (Trigger)", "ส่วนที่ 4 · ความปลอดภัย &amp; การเขียนโปรแกรม"),
    ("appendix-a-script.html", "ก", "สคริปต์ฐานข้อมูลกรณีศึกษา", "ภาคผนวก"),
    ("appendix-b-cheatsheet.html", "ข", "สรุปคำสั่ง SQL (Cheat Sheet)", "ภาคผนวก"),
    ("appendix-c-dbeaver.html", "ค", "เชื่อมต่อฐานข้อมูลด้วย DBeaver", "ภาคผนวก"),
    ("appendix-d-university-web.html", "ง", "ตัวอย่าง Website University", "ภาคผนวก"),
    ("library_tutorial_site/index.html", "จ", "Library Tutorial ↗", "ภาคผนวก"),  # ลิงก์ภายนอก เปิดแท็บใหม่ (ไม่มีหน้า src)
]
LIB_SRC = ROOT / "library_tutorial_site"   # คัดลอกไปไว้ที่ docs/library_tutorial_site/ (ภาคผนวก จ เปิดแท็บใหม่)
LIB_OUT = OUT / "library_tutorial_site"

def is_external(f):
    return "/" in f

# ---------------------------------------------------------------- SQL helpers
def strip_comments(sql):
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.S)
    out = []
    for line in sql.split("\n"):
        # ตัด -- comment ที่อยู่นอก string
        q, i, cut = False, 0, None
        while i < len(line):
            c = line[i]
            if c == "'":
                q = not q
            elif not q and line.startswith("--", i):
                cut = i
                break
            i += 1
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)

def split_sql(sql):
    """แยกคำสั่งด้วย ; รองรับ DELIMITER"""
    sql = strip_comments(sql)
    stmts, buf, delim = [], [], ";"
    for line in sql.split("\n"):
        m = re.match(r"\s*delimiter\s+(\S+)\s*$", line, re.I)
        if m:
            delim = m.group(1)
            continue
        buf.append(line)
        joined = "\n".join(buf)
        if joined.rstrip().endswith(delim):
            st = joined.rstrip()[: -len(delim)].strip()
            if st:
                stmts.append(st)
            buf = []
    rest = "\n".join(buf).strip()
    if rest:
        stmts.append(rest)
    return stmts

class Runner:
    def __init__(self):
        self.cn = mysql.connector.connect(**DB, autocommit=True, charset="utf8mb4", collation="utf8mb4_unicode_ci")
        self.cur = self.cn.cursor()

    def reset(self):
        c = self.cur
        c.execute(f"DROP DATABASE IF EXISTS {DBNAME}")
        c.execute(f"CREATE DATABASE {DBNAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        c.execute(f"USE {DBNAME}")
        for st in split_sql(LAB_SCRIPT.read_text(encoding="utf-8")):
            c.execute(st)
            if c.with_rows:
                c.fetchall()

    def run(self, sql):
        """คืน (columns, rows, affected) ของคำสั่งสุดท้ายที่มี result set; ถ้าไม่มีคืน affected ของคำสั่งสุดท้าย"""
        res, affected = None, None
        for st in split_sql(sql):
            if re.match(r"\s*call\b", st, re.I):
                # CALL อาจคืนหลาย result set
                for rc in self.cur.execute(st, multi=True):
                    if rc.with_rows:
                        res = ([d[0] for d in rc.description], rc.fetchall())
                continue
            self.cur.execute(st)
            if self.cur.with_rows:
                cols = [d[0] for d in self.cur.description]
                res = (cols, self.cur.fetchall())
            else:
                affected = self.cur.rowcount
        return res, affected

# ---------------------------------------------------------------- rendering
def fmt(v):
    if v is None:
        return '<td class="null">NULL</td>'
    if isinstance(v, (bytes, bytearray)):
        v = v.decode("utf-8", "replace")
    if isinstance(v, set):   # คอลัมน์ชนิด SET เช่น sql_mode → แสดงแบบ MySQL (คั่นด้วย , เรียงคงที่)
        v = ",".join(sorted(v))
    if isinstance(v, decimal.Decimal):
        v = format(v, "f")
    if isinstance(v, (datetime.date, datetime.datetime)):
        v = v.isoformat(sep=" ") if isinstance(v, datetime.datetime) else v.isoformat()
    return f"<td>{html.escape(str(v).replace(DBNAME, SHOWDB))}</td>"

def frame_match(cols, r, frame):
    """frame="major=CS;gpa>=3.00" → แถวที่ตรงทุกเงื่อนไข (เทียบตัวเลขถ้าได้ ไม่สนตัวพิมพ์เล็ก/ใหญ่)"""
    for cond in frame.split(";"):
        c, op, v = re.match(r"\s*(\w+)\s*(>=|<=|<>|=|>|<)\s*(.*?)\s*$", cond).groups()
        x = r[cols.index(c)]
        if x is None:
            return False
        try:
            x, v = float(x), float(v)
        except ValueError:
            x, v = str(x).lower(), v.lower()
        if not {"=": x == v, "<>": x != v, ">": x > v, "<": x < v, ">=": x >= v, "<=": x <= v}[op]:
            return False
    return True

def table_html(cols, rows, mx=None, label="ผลลัพธ์", hl=None, keep=None, frame=None):
    """hl="คอลัมน์=ค่า" เน้นแถวที่ตรงเงื่อนไข · keep="c1,c2" เน้นคอลัมน์ที่เลือก (คอลัมน์อื่นจาง)
    frame="c1=v1;c2>=v2" ตีกรอบรอบแถวที่ตรงทุกเงื่อนไข (แถวต่อเนื่องกันเป็นกรอบเดียว)"""
    n = len(rows)
    shown = rows if not mx or n <= mx else rows[:mx]
    if n == 0:
        cap = f"{label} (0 แถว — ไม่มีข้อมูลที่ตรงเงื่อนไข)"
    elif len(shown) < n:
        cap = f"{label} (แสดง {len(shown)} จาก {n} แถว)"
    else:
        cap = f"{label} ({n} แถว)"
    kp = [c.strip() for c in keep.split(",")] if keep else None
    hk, hv = hl.split("=", 1) if hl else (None, None)
    def ccls(c):
        return "" if kp is None else (' class="keep"' if c in kp else ' class="dim"')
    fm = [bool(frame) and frame_match(cols, r, frame) for r in shown]
    def tr(i, r):
        on = hk is not None and str(r[cols.index(hk)]) == hv
        def cell(c, v):
            s = fmt(v)
            if not kp:
                return s
            name = "keep" if c in kp else "dim"
            return s.replace('class="', f'class="{name} ', 1) if s.startswith('<td class=') else s.replace("<td", f'<td class="{name}"', 1)
        cells = "".join(cell(c, v) for c, v in zip(cols, r))
        k = ["hl"] if on else []
        if fm[i]:
            k += ["fr"] + (["fr-top"] if i == 0 or not fm[i - 1] else []) + (["fr-bot"] if i == len(fm) - 1 or not fm[i + 1] else [])
        return (f'<tr class="{" ".join(k)}">' if k else "<tr>") + cells + "</tr>"
    head = "".join(f"<th{ccls(c)}>{html.escape(str(c))}</th>" for c in cols)
    body = "".join(tr(i, r) for i, r in enumerate(shown))
    cls = "tbl result" + (" demo" if (hl or kp or frame) else "")
    return f'<div class="result-t">▸ {cap}</div><div class="tbl-wrap"><table class="{cls}"><tr>{head}</tr>{body}</table></div>'

def attrs_of(s):
    a = {}
    for m in re.finditer(r'(\w+)(?:="([^"]*)")?', s):
        a[m.group(1)] = m.group(2) if m.group(2) is not None else True
    return a

def render_sql(m, runner, page):
    a, code = attrs_of(m.group(1)), m.group(2).strip("\n")
    code = re.sub(r"^\n+|\s+$", "", code)
    title = a.get("title", "SQL")
    out = [f'<div class="code"><div class="code-head"><span><span class="dots"><i></i><i></i><i></i></span>{title}</span></div><pre class="sql">{html.escape(code)}</pre></div>']
    if "hidden" in a:
        out = []
    if "reset" in a:
        runner.reset()
    if any(k in a for k in ("run", "exec", "error")):
        try:
            if "temp" in a:
                runner.cn.start_transaction()
            res, aff = runner.run(code)
            extra = runner.run(a["show"])[0] if "show" in a else None
            if "temp" in a:
                runner.cn.rollback()
            if "error" in a:
                sys.exit(f"[{page}] expected error but succeeded: {title}")
            if "run" in a:
                mx = int(a.get("max", 0)) or None
                if res:
                    out.append(table_html(*res, mx=mx, label=a.get("label", "ผลลัพธ์"), hl=a.get("hl"), keep=a.get("keep"), frame=a.get("frame")))
                else:
                    out.append(f'<div class="run-msg">✔ Query OK · {aff if aff is not None and aff >= 0 else 0} row(s) affected</div>')
                if extra:
                    out.append(table_html(*extra, mx=mx, label=a.get("showlabel", "ข้อมูลหลังรันคำสั่ง")))
        except mysql.connector.Error as e:
            if "temp" in a:
                runner.cn.rollback()
            if "error" not in a:
                sys.exit(f"[{page}] SQL error in '{title}': {e}")
            out.append(f'<div class="run-err"><b>✖ Error Code: {e.errno}.</b> {html.escape(e.msg.replace(DBNAME, SHOWDB))}</div>')
    return "\n".join(out)

LEVEL = {"1": "⭐ ง่าย", "2": "⭐⭐ ปานกลาง", "3": "⭐⭐⭐ ท้าทาย"}

def render_ex(m):
    a, body = attrs_of(m.group(1)), m.group(2)
    q, _, ans = body.partition("<answer>")
    ans = ans.replace("</answer>", "")
    lv = LEVEL.get(str(a.get("level", "1")), "")
    return (f'<div class="ex" id="ex{a.get("no","")}"><div class="ex-head"><span class="ex-badge">ฝึก {a.get("no","")}</span>'
            f'<span class="ex-title">{a.get("title","")}</span><span class="ex-level">{lv}</span></div>'
            f'<div class="ex-body">{q.strip()}\n<button type="button" class="ans-btn">👀 ดูเฉลย</button>'
            f'<div class="answer"><div class="answer-t">✅ เฉลย</div>{ans.strip()}</div></div></div>')

def render_review(m):
    return (f'<div class="review" id="review"><div class="review-head"><img src="icon/thinking.png" alt="">'
            f'<h2>คำถามท้ายบท</h2><button type="button" class="review-copy">📋 คัดลอกคำถามทั้งหมด</button>'
            f'<button type="button" class="review-key">🔑 ดูเฉลย</button></div>'
            f'<form class="review-lock" hidden><label>รหัสผ่านสำหรับดูเฉลย</label>'
            f'<input type="password" autocomplete="off" placeholder="รหัสผ่าน">'
            f'<button type="submit">ตกลง</button><span class="review-msg"></span></form>'
            f'<ol>{m.group(1)}</ol></div>')

def render_fig(m):
    n, w, no, cap = m.group(1), m.group(2), m.group(3), m.group(4)
    style = f' style="max-width:{w}px"' if w else ""
    no = no or n.replace("-", ".")
    return (f'<figure class="shot"><img src="image/fig{n}.jpg" alt="ภาพที่ {no}" loading="lazy"{style}>'
            f'<figcaption><b>ภาพที่ {no}</b> {cap}</figcaption></figure>')

def toc_html(body):
    items = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    lis = "".join(f'<li><a href="#{i}">{re.sub("<[^>]+>", " ", t).strip()}</a></li>' for i, t in items)
    return f'<div class="pagetoc"><div class="pagetoc-t">📑 ในบทนี้</div><ul>{lis}</ul></div>'

def sub_items(body):
    """หัวข้อย่อย (h2 ที่มี id) ของหน้า สำหรับเมนูด้านข้าง"""
    items = []
    for i, h in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body):
        sec = re.search(r'<span class="sec">(.*?)</span>', h)
        title = re.sub("<[^>]+>", "", re.sub(r'<span class="sec">.*?</span>', "", h)).strip()
        items.append((i, sec.group(1) if sec else "", title))
    if 'id="review"' in body:
        items.append(("review", "✎", "คำถามท้ายบท"))
    return items

def sidebar(active, subs=()):
    out, group = [], None
    for f, no, t, g in PAGES:
        if g != group:
            if group is not None:
                out.append("</div>")
            out.append(f'<div class="navgroup"><div class="navgroup-t">{g}</div>')
            group = g
        cls = ' class="active"' if f == active else ""
        if is_external(f):
            cls = ' target="_blank" rel="noopener"'
        out.append(f'<a href="{f}"{cls}><span class="no">{no}</span>{t}</a>')
        if f == active and subs:
            out.append('<div class="subnav">' + "".join(
                f'<a href="#{i}"><span class="sno">{s}</span>{tt}</a>' for i, s, tt in subs) + "</div>")
    out.append("</div>")
    return "\n".join(out)

def layout(fname, meta, body):
    pages = [p for p in PAGES if not is_external(p[0])]
    idx = [p[0] for p in pages].index(fname)
    prev = pages[idx - 1] if idx > 0 else None
    nxt = pages[idx + 1] if idx + 1 < len(pages) else None
    pg = '<div class="pager">'
    pg += f'<a class="pg" href="{prev[0]}">← {prev[1]} · {prev[2]}</a>' if prev else "<span></span>"
    pg += f'<a class="pg next" href="{nxt[0]}">{nxt[1]} · {nxt[2]} →</a>' if nxt else ""
    pg += "</div>"
    head = ""
    if not meta.get("hero"):
        head = (f'<div class="page-head"><span class="kicker">{meta.get("kicker","")}</span>'
                f'<h1>{meta["title"]}</h1><p class="sub">{meta.get("sub","")}</p></div>')
    return f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{re.sub("<[^>]+>", "", meta["title"])} — Database Lecture Note</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;800&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<button id="menuBtn" aria-label="menu">☰ เมนู</button>
<aside class="sidebar" id="sidebar">
  <div class="brand"><a href="index.html"><span class="logo">DB</span><span class="t1">Database Design<br>&amp; Management</span><span class="t2">1204202 · Lecture Note · MySQL + DBeaver</span></a></div>
  <nav>
{sidebar(fname, sub_items(body))}
  </nav>
  <img src="icon/{meta.get("img","me_cat.png")}" alt="" class="sidebar-img">
</aside>
<main class="content">
{head}
{body}
{pg}
<footer>Lecture Note · 1204202 การออกแบบและการจัดการฐานข้อมูล · อ.ดร.พรทิวา ปะวะระ · ภาควิชาวิทยาการคอมพิวเตอร์ คณะวิทยาการสารสนเทศ มหาวิทยาลัยมหาสารคาม</footer>
</main>
<script src="assets/password.js"></script>
<script src="assets/nav.js"></script>
</body>
</html>
"""

def build(only=None):
    runner = Runner()
    for fname, *_ in PAGES:
        src = SRC / fname
        if not src.exists() or (only and fname not in only):
            continue
        text = src.read_text(encoding="utf-8")
        mm = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->", text, re.S)
        meta = json.loads(mm.group(1)) if mm else {"title": fname}
        body = text[mm.end():] if mm else text
        runner.reset()
        body = re.sub(r'<sql\b((?:[^>"]|"[^"]*")*)>(.*?)</sql>', lambda m: render_sql(m, runner, fname), body, flags=re.S)
        body = re.sub(r'<ex\b((?:[^>"]|"[^"]*")*)>(.*?)</ex>', render_ex, body, flags=re.S)
        body = re.sub(r"<review>(.*?)</review>", render_review, body, flags=re.S)
        body = re.sub(r'<fig n="([^"]+)"(?: w="(\d+)")?(?: no="([^"]+)")?>(.*?)</fig>', render_fig, body, flags=re.S)
        body = body.replace("<toc/>", toc_html(body))
        (OUT / fname).write_text(layout(fname, meta, body), encoding="utf-8")
        print("built", fname)
    runner.cur.execute(f"DROP DATABASE IF EXISTS {DBNAME}")
    copy_library()
    zip_university()

def zip_university():
    """บีบอัด university_schema_site -> docs/university_schema_site.zip (ภาคผนวก ง ให้ดาวน์โหลด)"""
    import zipfile
    src = ROOT / "university_schema_site"
    if not src.exists():
        return
    with zipfile.ZipFile(OUT / "university_schema_site.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts:
                z.write(f, pathlib.Path(src.name) / f.relative_to(src))
    print("zipped university_schema_site.zip")

def copy_library():
    """คัดลอก library_tutorial_site -> docs/library_tutorial_site พร้อมเพิ่มลิงก์กลับ Lecture Note ในเมนู"""
    import shutil
    if not LIB_SRC.exists():
        return
    shutil.copytree(LIB_SRC, LIB_OUT, ignore=shutil.ignore_patterns("README.md", ".git*"), dirs_exist_ok=True)
    back = ('<nav><div class="navgroup"><a href="../index.html">'
            '← กลับ Lecture Note</a></div>')
    for p in LIB_OUT.glob("*.html"):
        s = p.read_text(encoding="utf-8")
        p.write_text(s.replace("<nav>", back, 1), encoding="utf-8")
    print("copied library_tutorial_site/")

if __name__ == "__main__":
    build(sys.argv[1:] or None)
