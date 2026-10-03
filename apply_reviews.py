# -*- coding: utf-8 -*-
"""นำคำถามท้ายบท + เฉลย จาก src/reviews/*.txt ไปแทนบล็อก <review>...</review> ในไฟล์ src ที่ชื่อตรงกัน

รูปแบบไฟล์ src/reviews/<ชื่อบท>.txt  (เช่น 05-select.txt -> 05-select.html)
  # ...              คอมเมนต์
  ## หัวข้อ          หัวข้อกลุ่มคำถาม
  ข้อความ || hint     คำถาม 1 ข้อ (ใช้ `โค้ด` ได้ · ข้อย่อย (ก) (ข) ขึ้นบรรทัดใหม่อัตโนมัติ)
  A: ข้อความ         เฉลยของคำถามข้อล่าสุด 1 ย่อหน้า (ใช้ `โค้ด` <b> <br> ได้)
  A- ข้อความ         เฉลยแบบรายการ (bullet)
  ```run max="10"    เริ่มบล็อก SQL ในเฉลย ตามด้วย attribute ของแท็ก <sql> (run / exec / temp / error / hidden / max)
  ...                ไม่มี attribute = แสดงโค้ดอย่างเดียว ไม่รัน
  ```                ปิดบล็อก
บล็อก SQL แรกของแต่ละบทจะโหลดฐานข้อมูลกรณีศึกษาใหม่ (reset) ก่อนรันเสมอ
  ยกเว้นไฟล์ที่มีบรรทัด  #!noreset  (ใช้ต่อจากสถานะท้ายบท เช่น วิวที่สร้างไว้ในบท)
"""
import html, pathlib, re

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
RDIR = SRC / "reviews"
ALLOWED = ("b", "i", "u", "br", "sub", "sup", "code")

def inline(text):
    t = html.escape(text, quote=False)
    t = re.sub(r"&amp;(lt|gt|amp|nbsp);", r"&\1;", t)       # เขียน &lt; &gt; เองในข้อความได้
    for tag in ALLOWED:
        t = re.sub(rf"&lt;(/?){tag}\s*/?&gt;", rf"<\1{tag}>", t)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", t)

def fmt_q(text):
    t = inline(text)
    return re.sub(r"\s+(?=\([ก-ฮ]\))", "<br>", t)          # ข้อย่อย (ก) (ข) ... ขึ้นบรรทัดใหม่

class Q:
    def __init__(self, text):
        self.text, self.ans = text, []

def parse(path):
    items, cur, fence, buf = [], None, None, []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if fence is not None:
            if raw.strip() == "```":
                cur.ans.append(("sql", fence, "\n".join(buf)))
                fence, buf = None, []
            else:
                buf.append(raw)
            continue
        line = raw.strip()
        if not line or (line.startswith("#") and not line.startswith("##")):
            continue
        if line.startswith("```"):
            fence = line[3:].strip()
        elif line.startswith("##"):
            items.append(("part", line[2:].strip()))
            cur = None
        elif line.startswith("A:"):
            cur.ans.append(("p", line[2:].strip()))
        elif line.startswith("A-"):
            cur.ans.append(("li", line[2:].strip()))
        else:
            cur = Q(line)
            items.append(("q", cur))
    if fence is not None:
        raise SystemExit(f"{path.name}: ไม่ได้ปิด ``` ")
    return items

def render(items, reset=True):
    out, first_sql = [], reset
    for kind, obj in items:
        if kind == "part":
            out.append(f'<li class="part">{inline(obj)}</li>')
            continue
        q, _, hint = obj.text.partition("||")
        h = f' <span class="hint">({inline(hint.strip())})</span>' if hint.strip() else ""
        parts, ul = [], []
        def flush():
            if ul:
                parts.append("<ul>" + "".join(f"<li>{x}</li>" for x in ul) + "</ul>")
                ul.clear()
        for a in obj.ans:
            if a[0] == "li":
                ul.append(inline(a[1]))
                continue
            flush()
            if a[0] == "p":
                parts.append(f"<p>{inline(a[1])}</p>")
            else:
                attrs = a[1]
                if first_sql:
                    attrs = (attrs + " reset").strip()
                    first_sql = False
                title = "" if "title=" in attrs else 'title="เฉลย" '
                parts.append(f"<sql {title}{attrs}>{a[2]}</sql>")
        flush()
        ans = f'<div class="rv-ans">{"".join(parts)}</div>' if parts else ""
        out.append(f"<li>{fmt_q(q.strip())}{h}{ans}</li>")
    return out

if __name__ == "__main__":
    for path in sorted(RDIR.glob("*.txt")):
        target = SRC / (path.stem + ".html")
        items = parse(path)
        noreset = "#!noreset" in path.read_text(encoding="utf-8")
        block = "<review>\n" + "\n".join(render(items, reset=not noreset)) + "\n</review>"
        t = target.read_text(encoding="utf-8")
        t, n = re.subn(r"<review>.*?</review>", lambda m: block, t, flags=re.S)
        if n == 0:
            t = t.rstrip() + "\n\n" + block + "\n"
        target.write_text(t, encoding="utf-8")
        qs = [o for k, o in items if k == "q"]
        print(f"{target.name}: {len(qs)} ข้อ · มีเฉลย {sum(1 for o in qs if o.ans)} ข้อ")
