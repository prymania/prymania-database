// ============================================================
//  dashboard.js — การ์ดตัวเลข + กล่องรายงาน (สร้างจาก db.REPORTS อัตโนมัติ)
// ============================================================
async function loadSummary() {
  const r = await api("/report/summary");
  if (!r.ok) { $("#summary").innerHTML = '<div class="status err" style="grid-column:1/-1">⚠️ ' + esc(r.error) + "</div>"; return; }
  // report_summary() คืน 1 แถว — 1 คอลัมน์ = 1 การ์ด
  $("#summary").innerHTML = Object.entries(r.data[0]).map(([label, num]) =>
    '<div class="metric"><div class="metric-num">' + esc(num ?? "—") + '</div><div class="metric-label">' + esc(label) + "</div></div>").join("");
  $("#summarySql").innerHTML = sqlToggle(r.sql);
}

async function loadReports() {
  const list = await api("/report/list");
  for (const rep of list.data || []) {
    const sec = document.createElement("section");
    sec.className = "card";
    sec.innerHTML = "<h3>" + rep.title + '</h3><div class="status">กำลังโหลด...</div>';
    $("#reports").appendChild(sec);
    api("/report/run/" + rep.key).then(r => {
      sec.innerHTML = "<h3>" + rep.title + "</h3>" +
        (r.ok ? simpleTable(r.data, rep.bar) : '<div class="status err">⚠️ ' + esc(r.error) + "</div>") + sqlToggle(r.sql);
    });
  }
}

loadSummary();
loadReports();
