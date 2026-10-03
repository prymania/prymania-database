// ============================================================
//  common.js — ฟังก์ชันที่ทุกหน้าใช้ร่วมกัน
// ============================================================
const $ = (s) => document.querySelector(s);
const esc = (v) => String(v).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

async function api(url, opts) {
  try { return await (await fetch(url, opts)).json(); }
  catch (e) { return { ok: false, error: "เชื่อมต่อ server ไม่ได้ — ยังรัน python app.py อยู่หรือไม่" }; }
}

function setStatus(el, msg, cls = "") { el.className = "status " + cls; el.textContent = msg; }

// ปุ่ม "🔍 SQL" เปิด/ปิดกล่องแสดงคำสั่ง SQL ที่ server รันจริง
function sqlToggle(sql, label = "SQL ที่รันจริง") {
  if (!sql) return "";
  return '<details class="sql"><summary>🔍 ' + label + '</summary><pre>' + esc(sql) + "</pre></details>";
}

// ค่า 1 ช่องในตาราง — NULL แสดงให้เห็นชัดว่า "ไม่มีค่า" ไม่ใช่ 0 หรือข้อความว่าง
function cell(v) {
  return v === null || v === undefined ? '<td class="null">NULL</td>' : "<td>" + esc(v) + "</td>";
}

// รูปนิสิต / อาจารย์ (ถ้าไม่มีไฟล์ใช้ default.png)
function photo(id, cls = "avatar") {
  return '<img class="' + cls + '" src="/static/images/' + encodeURIComponent(id) +
    '.jpg" onerror="this.onerror=null;this.src=\'/static/images/default.png\'" alt="">';
}

// ตารางผลลัพธ์อย่างง่าย (ใช้ในหน้ารายละเอียด / dashboard)
function simpleTable(rows, bar) {
  if (!rows.length) return '<div class="status">ไม่มีข้อมูล</div>';
  const cols = Object.keys(rows[0]);
  const max = bar ? Math.max(...rows.map(r => Number(r[bar]) || 0)) || 1 : 0;
  return '<div class="table-wrap"><table><thead><tr>' + cols.map(c => "<th>" + esc(c) + "</th>").join("") +
    "</tr></thead><tbody>" + rows.map(r => "<tr>" + cols.map(c => {
      if (c === bar && r[c] !== null) {
        const w = Math.max(2, 100 * Number(r[c]) / max);
        return '<td class="barcell"><div class="bar" style="width:' + w + '%"></div><span>' + esc(r[c]) + "</span></td>";
      }
      return cell(r[c]);
    }).join("") + "</tr>").join("") + "</tbody></table></div>";
}

$("#btnReset").onclick = async () => {
  if (!confirm("ล้างข้อมูลทั้งหมดแล้วสร้างใหม่จาก schema.sql ?\n(ข้อมูลที่เพิ่ม/แก้/ลบไว้จะหายทั้งหมด)")) return;
  const r = await api("/reset", { method: "POST" });
  alert(r.ok ? "รีเซ็ตเรียบร้อย — ข้อมูลกลับเป็นชุดเดียวกับสคริปต์ในชั้นเรียน" : "⚠️ " + r.error);
  if (r.ok) location.reload();
};
