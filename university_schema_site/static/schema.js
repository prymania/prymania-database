// ============================================================
//  schema.js — แสดงโครงสร้าง 5 ตาราง (อ่านจาก information_schema)
// ============================================================
(async () => {
  const [cols, fks] = await Promise.all([api("/schema/columns"), api("/schema/fks")]);
  if (!cols.ok) { $("#tables").innerHTML = '<div class="status err">⚠️ ' + esc(cols.error) + "</div>"; return; }
  $("#sqlBox").innerHTML = sqlToggle(cols.sql, "SQL: รายชื่อคอลัมน์") + " " + sqlToggle(fks.sql, "SQL: Foreign Key");
  const fk = {};
  (fks.data || []).forEach(f => fk[f.tbl + "." + f.col] = f.ref_tbl + "(" + f.ref_col + ")");
  const tables = {};
  cols.data.forEach(c => (tables[c.tbl] = tables[c.tbl] || []).push(c));
  $("#tables").innerHTML = Object.entries(tables).map(([t, cs]) =>
    '<div class="tcard"><div class="tcard-h">' + t + "</div><table>" + cs.map(c => {
      const ref = fk[t + "." + c.col];
      return "<tr><td>" + (c.col_key === "PRI" ? "🔑 " : "") + (ref ? "🔗 " : "") + "<b>" + c.col + "</b>" +
        (ref ? '<div class="ref">→ ' + ref + "</div>" : "") + "</td><td><code>" + c.type + "</code>" +
        (c.nullable === "NO" ? ' <span class="nn">NOT NULL</span>' : "") +
        (c.extra ? ' <span class="nn">' + c.extra + "</span>" : "") + "</td></tr>";
    }).join("") + "</table></div>").join("");
})();
