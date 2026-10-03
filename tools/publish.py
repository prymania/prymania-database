"""
publish.py — อัปเดตเว็บขึ้น GitHub Pages ในคำสั่งเดียว (ปกติเรียกผ่าน อัปเดตเว็บ.bat)
  1) build เว็บใหม่ทั้งหมด (เข้ารหัสเฉลยด้วยรหัสใน passwords.json + ตรวจว่าไม่มีเฉลย/รหัสหลุด)
  2) อัปโหลดโฟลเดอร์ site/ ขึ้น repo สาธารณะที่ตั้งไว้ใน publish_config.json
  3) ถ้าโฟลเดอร์โปรเจคเป็น git repo ที่มี remote (repo ส่วนตัว) → สำรองต้นฉบับขึ้นไปด้วย
"""
import datetime, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
CONFIG = ROOT / "publish_config.json"


def git(*args, cwd, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        sys.exit(f"✖ git {' '.join(args)} ไม่สำเร็จ:\n{r.stderr or r.stdout}")
    return r


def commit_and_push(cwd, label):
    git("add", "-A", cwd=cwd)
    if git("diff", "--cached", "--quiet", cwd=cwd, check=False).returncode == 0:
        print(f"   {label}: ไม่มีอะไรเปลี่ยน")
    else:
        git("commit", "-m", f"อัปเดต {datetime.datetime.now():%Y-%m-%d %H:%M}", cwd=cwd)
    branch = git("branch", "--show-current", cwd=cwd).stdout.strip() or "main"
    git("push", "-u", "origin", branch, cwd=cwd)
    print(f"✔ {label}: อัปโหลดแล้ว")


def main():
    print("① build เว็บ ...", flush=True)
    if subprocess.run([sys.executable, "build.py"], cwd=ROOT).returncode != 0:
        sys.exit("✖ build ไม่สำเร็จ — ยังไม่ได้อัปโหลด (ตรวจว่าเปิด MySQL แล้ว และอ่านข้อความ error ด้านบน)")

    cfg = json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    url = cfg.get("site_repo_url", "").strip()
    if not url:
        print("\n⚠ build เสร็จแล้ว แต่ยังไม่ได้ตั้งค่า repo ของเว็บ จึงยังไม่ได้อัปโหลด")
        print(f"   ใส่ URL ของ repo สาธารณะใน {CONFIG.name} ที่ช่อง site_repo_url เช่น")
        print('   "site_repo_url": "https://github.com/<ชื่อบัญชี>/<ชื่อ repo>.git"')
        return

    print("② อัปโหลดเว็บ (site/) ...", flush=True)
    (SITE / ".nojekyll").touch()             # ให้ GitHub Pages ส่งไฟล์ตามที่เป็น ไม่แปลงด้วย Jekyll
    if not (SITE / ".git").exists():
        git("init", "-b", "main", cwd=SITE)
    if git("remote", cwd=SITE).stdout.split() == []:
        git("remote", "add", "origin", url, cwd=SITE)
    else:
        git("remote", "set-url", "origin", url, cwd=SITE)
    commit_and_push(SITE, "เว็บ")

    if (ROOT / ".git").exists() and git("remote", cwd=ROOT, check=False).stdout.strip():
        print("③ สำรองต้นฉบับขึ้น repo ส่วนตัว ...")
        commit_and_push(ROOT, "ต้นฉบับ")
    print("\nเสร็จแล้ว — GitHub Pages จะแสดงเว็บใหม่ภายใน 1–2 นาที")


if __name__ == "__main__":
    main()
