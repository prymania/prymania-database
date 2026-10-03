"""
passwords_tool.py — ดู / สร้างรหัสผ่านปุ่ม "ดูเฉลย" ของคำถามท้ายบท
  python tools/passwords_tool.py show   → เปิดตารางรหัสผ่านในเบราว์เซอร์ (ไฟล์ชั่วคราวในเครื่อง ไม่ขึ้นเว็บ)
  python tools/passwords_tool.py new    → เก็บรหัสปีเก่าไว้ใน password_history/ แล้วสุ่มรหัสชุดใหม่
(ปกติเรียกผ่าน ดูรหัสผ่าน.bat และ สร้างรหัสปีใหม่.bat)
"""
import html, json, pathlib, secrets, subprocess, sys, tempfile, webbrowser, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
FILE = ROOT / "passwords.json"
HISTORY = ROOT / "password_history"
sys.path.insert(0, str(ROOT))
from build import PAGES, chapter_key   # ชื่อบท + การแปลงชื่อไฟล์เป็น c1, c2, ...

# คำนำหน้ารหัสของแต่ละบท — อ่านออกเสียงบอกในห้องได้ง่าย
WORDS = {"c1": "intro", "c2": "er", "c3": "normal", "c4": "table", "c5": "select", "c6": "join",
         "c7": "view", "c8": "index", "c9": "commit", "c10": "secure", "c11": "proc", "c12": "trigger"}
CHAPTERS = {chapter_key(f): (no, title) for f, no, title, _ in PAGES if chapter_key(f)}


def load():
    return json.loads(FILE.read_text(encoding="utf-8"))


def save(data):
    FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def show(data, note=""):
    rows = "".join(
        f"<tr><td>{html.escape(CHAPTERS.get(k, ('', ''))[0])}</td><td>{CHAPTERS.get(k, ('', ''))[1]}</td>"
        f"<td><code>{html.escape(k)}</code></td><td class='pw'>{html.escape(v)}</td></tr>"
        for k, v in data["รหัสผ่าน"].items())
    old = ""
    for p in sorted(HISTORY.glob("passwords-*.json"), reverse=True) if HISTORY.exists() else []:
        d = json.loads(p.read_text(encoding="utf-8"))
        old += (f"<h3>ปีการศึกษา {html.escape(str(d.get('ปีการศึกษา', '?')))}</h3><p class='mute'>"
                + " · ".join(f"{k}: <b>{html.escape(v)}</b>" for k, v in d["รหัสผ่าน"].items()) + "</p>")
    page = f"""<!doctype html><html lang="th"><head><meta charset="utf-8"><title>รหัสผ่านดูเฉลย {html.escape(str(data['ปีการศึกษา']))}</title>
<style>body{{font-family:"Leelawadee UI",Tahoma,sans-serif;max-width:760px;margin:30px auto;padding:0 16px;color:#0B3A40}}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ccd;padding:8px 12px;text-align:left}}
th{{background:#0F4C54;color:#fff}}td.pw{{font:700 18px Consolas,monospace;color:#D9581A}}
.note{{background:#E6F5EC;border-left:4px solid #2E9E5B;padding:10px 14px;margin:12px 0}}.mute{{color:#667;font-size:14px}}
@media print{{.noprint{{display:none}}}}</style></head><body>
<h1>🔑 รหัสผ่านดูเฉลยคำถามท้ายบท</h1><h2>ปีการศึกษา {html.escape(str(data['ปีการศึกษา']))}</h2>
{f'<div class="note">{note}</div>' if note else ''}
<table><tr><th>บท</th><th>ชื่อบท</th><th>คีย์</th><th>รหัสผ่าน</th></tr>{rows}</table>
<p class="mute">แก้รหัสได้ที่ <code>{html.escape(str(FILE))}</code> แล้วดับเบิลคลิก <b>อัปเดตเว็บ.bat</b> · หน้านี้เปิดจากเครื่องอาจารย์เท่านั้น ไม่ได้อยู่บนเว็บ</p>
<p class="noprint"><button onclick="print()">🖨 พิมพ์</button></p>
{'<h2>รหัสปีก่อน ๆ</h2>' + old if old else ''}</body></html>"""
    out = pathlib.Path(tempfile.gettempdir()) / "db_lecture_passwords.html"
    out.write_text(page, encoding="utf-8")
    webbrowser.open(out.as_uri())
    print(f"เปิดตารางรหัสผ่านในเบราว์เซอร์แล้ว ({out})")


def new():
    data = load()
    old_year = str(data.get("ปีการศึกษา", ""))
    HISTORY.mkdir(exist_ok=True)
    backup = HISTORY / f"passwords-{old_year or datetime.date.today().isoformat()}.json"
    if backup.exists():
        backup = HISTORY / f"passwords-{old_year}-{datetime.datetime.now():%Y%m%d-%H%M%S}.json"
    backup.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"เก็บรหัสปี {old_year} ไว้ที่ {backup.parent.name}/{backup.name}")

    default = str(int(old_year) + 1) if old_year.isdigit() else ""
    year = input(f"ปีการศึกษาใหม่ [{default}] : ").strip() or default
    data["ปีการศึกษา"] = year
    data["รหัสผ่าน"] = {k: f"{WORDS.get(k, 'db')}-{secrets.randbelow(9000) + 1000}" for k in data["รหัสผ่าน"]}
    save(data)
    print(f"บันทึกรหัสปี {year} ลง passwords.json แล้ว")
    show(data, note=f"สร้างรหัสใหม่สำหรับปีการศึกษา {html.escape(year)} แล้ว — <b>เว็บจะใช้รหัสใหม่หลังจากอัปเดตเว็บ</b>")

    if input("อัปเดตเว็บด้วยรหัสใหม่เลยไหม (y/n) : ").strip().lower() in ("y", "yes", "ใช่"):
        subprocess.run([sys.executable, str(ROOT / "tools" / "publish.py")], cwd=ROOT)
    else:
        print("ยังไม่ได้อัปเดตเว็บ — เมื่อพร้อมให้ดับเบิลคลิก อัปเดตเว็บ.bat")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if not FILE.exists():
        sys.exit(f"ไม่พบ {FILE}")
    new() if cmd == "new" else show(load())
