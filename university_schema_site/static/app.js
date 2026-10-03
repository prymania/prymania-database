// ============================================================
//  app.js — หน้าจัดการข้อมูล (ค้นหา / เพิ่ม / แก้ไข / ลบ)
//  แต่ละแท็บกำหนดใน ENTITIES:
//    api      URL ที่แท็บนี้คุยด้วย (ฝั่ง server เรียกฟังก์ชันใน db.py)
//    idKeys   คอลัมน์ที่เป็น Primary Key (enroll มี 2 คอลัมน์)
//    joinCols คอลัมน์ที่มาจากตารางอื่นด้วย JOIN · calcCols คอลัมน์ที่คำนวณ/นับ
//    search   ช่องค้นหา · form ช่องในฟอร์ม · details ปุ่มดูข้อมูลเชิงลึกของแถว
// ============================================================
const GRADES = ["A", "B", "C", "D", "F"];

const ENTITIES = {
  students: {
    label: "นิสิต", table: "student", api: "/api/students", idKeys: ["stdid"], photo: "stdid",
    calcCols: ["age", "n_enroll"],
    deleteWarn: "ประวัติการลงทะเบียนของนิสิตคนนี้จะถูกลบไปด้วย (enroll … ON DELETE CASCADE)",
    search: [
      { key: "stdid", label: "รหัสนิสิต (ขึ้นต้นด้วย)", type: "text" },
      { key: "name", label: "ชื่อ", type: "text" },
      { key: "major", label: "สาขา", type: "select", lookup: "student_majors" },
      { key: "gpa_min", label: "GPA ตั้งแต่", type: "number", step: "0.01" }
    ],
    form: [
      { key: "stdid", label: "รหัสนิสิต (PK)", type: "text", lockOnEdit: true },
      { key: "name", label: "ชื่อ", type: "text" },
      { key: "major", label: "สาขา", type: "text" },
      { key: "gpa", label: "GPA (0.00 – 4.00)", type: "number", step: "0.01" },
      { key: "birthday", label: "วันเกิด", type: "date" }
    ],
    details: [{ key: "transcript", label: "📄 ผลการเรียน", title: r => "ผลการเรียนของ " + r.stdid + " · " + (r.name ?? "(ไม่มีชื่อ)") }]
  },
  lecturers: {
    label: "อาจารย์", table: "lecturer", api: "/api/lecturers", idKeys: ["lecid"], photo: "lecid",
    calcCols: ["n_section"],
    deleteWarn: "กลุ่มเรียนที่อาจารย์สอน และการลงทะเบียนในกลุ่มเหล่านั้นจะถูกลบไปด้วย (ON DELETE CASCADE)",
    search: [
      { key: "name", label: "ชื่อ", type: "text" },
      { key: "major", label: "สาขา", type: "select", lookup: "lecturer_majors" },
      { key: "salary_min", label: "เงินเดือนตั้งแต่", type: "number" }
    ],
    form: [
      { key: "lecid", label: "รหัสอาจารย์ (PK)", type: "text", lockOnEdit: true },
      { key: "name", label: "ชื่อ", type: "text" },
      { key: "salary", label: "เงินเดือน", type: "number" },
      { key: "major", label: "สาขา", type: "text" }
    ],
    details: [{ key: "sections", label: "📚 กลุ่มที่สอน", title: r => "กลุ่มเรียนที่ " + r.name + " สอน" }]
  },
  subjects: {
    label: "รายวิชา", table: "subject", api: "/api/subjects", idKeys: ["subid"],
    joinCols: ["pre_subname"],
    deleteWarn: "กลุ่มเรียนของวิชานี้จะถูกลบไปด้วย — แต่ถ้ามีวิชาอื่นใช้วิชานี้เป็นวิชาบังคับก่อน จะลบไม่ได้",
    search: [
      { key: "subid", label: "รหัสวิชา (ขึ้นต้นด้วย)", type: "text" },
      { key: "name", label: "ชื่อวิชา", type: "text" },
      { key: "major", label: "สาขา", type: "select", lookup: "subject_majors" },
      { key: "credit", label: "หน่วยกิต", type: "select", options: ["", "1", "2", "3", "4", "6"] }
    ],
    form: [
      { key: "subid", label: "รหัสวิชา (PK)", type: "text", lockOnEdit: true },
      { key: "name", label: "ชื่อวิชา (NOT NULL)", type: "text" },
      { key: "credit", label: "หน่วยกิต", type: "number" },
      { key: "major", label: "สาขา", type: "text" },
      { key: "pre", label: "วิชาบังคับก่อน (FK → subject)", type: "select", lookup: "subjects", blank: "— ไม่มี —" }
    ],
    details: [{ key: "next", label: "🔗 วิชาต่อเนื่อง", title: r => "วิชาที่ต้องเรียน " + r.subid + " " + r.name + " ก่อน" }]
  },
  sections: {
    label: "กลุ่มเรียน", table: "section", api: "/api/sections", idKeys: ["secid"],
    joinCols: ["sub_name", "credit", "lec_name"], calcCols: ["n_student"],
    deleteWarn: "การลงทะเบียนในกลุ่มนี้จะถูกลบไปด้วย (ON DELETE CASCADE)",
    search: [
      { key: "term", label: "ภาคเรียน", type: "select", lookup: "terms" },
      { key: "subid", label: "วิชา", type: "select", lookup: "subjects" },
      { key: "lecid", label: "อาจารย์", type: "select", lookup: "lecturers" }
    ],
    form: [
      { type: "note", label: "secid เป็น AUTO_INCREMENT — MySQL ออกเลขให้เอง" },
      { key: "subid", label: "วิชา (FK → subject)", type: "select", lookup: "subjects" },
      { key: "lecid", label: "อาจารย์ (FK → lecturer)", type: "select", lookup: "lecturers" },
      { key: "term", label: "ภาคเรียน เช่น 2026-1", type: "text" }
    ],
    details: [{ key: "roster", label: "👥 รายชื่อนิสิต", title: r => "กลุ่มเรียน " + r.secid + " · " + r.sub_id + " " + r.sub_name + " · " + r.term }]
  },
  enrolls: {
    label: "การลงทะเบียน", table: "enroll", api: "/api/enrolls", idKeys: ["secid", "stdid"],
    joinCols: ["term", "sub_id", "sub_name", "std_name"],
    search: [
      { key: "stdid", label: "นิสิต", type: "select", lookup: "students" },
      { key: "term", label: "ภาคเรียน", type: "select", lookup: "terms" },
      { key: "subid", label: "วิชา", type: "select", lookup: "subjects" },
      { key: "grade", label: "เกรด", type: "select", options: ["", ...GRADES] }
    ],
    form: [
      { key: "secid", label: "กลุ่มเรียน (PK, FK → section)", type: "select", lookup: "sections", lockOnEdit: true },
      { key: "stdid", label: "นิสิต (PK, FK → student)", type: "select", lookup: "students", lockOnEdit: true },
      { key: "grade", label: "เกรด", type: "select", options: GRADES, blank: "— ยังไม่มีเกรด (NULL) —" }
    ]
  }
};

let current = (location.hash.slice(1) in ENTITIES) ? location.hash.slice(1) : "students";
let editingKey = null;
let lastRows = [];
const cfg = () => ENTITIES[current];
const keyOf = (row) => cfg().idKeys.map(k => encodeURIComponent(row[k])).join("/");

// ---------- dropdown ----------
const lookupCache = {};
async function loadLookups(fields) {
  for (const f of fields.filter(f => f.lookup)) {
    if (!lookupCache[f.lookup]) {
      const r = await api("/lookup/" + f.lookup);
      lookupCache[f.lookup] = r.ok ? r.data : [{ value: "", label: "⚠️ " + r.error }];
    }
    f.options = lookupCache[f.lookup];
  }
}

function fieldHtml(f, prefix, value, locked) {
  if (f.type === "note") return '<div class="form-note">ℹ️ ' + f.label + "</div>";
  const v = value ?? "";
  let input;
  if (f.type === "select") {
    const opts = (f.options || []).map(o => typeof o === "object" ? o : { value: o, label: o || "ทั้งหมด" });
    if (prefix === "s_" && f.lookup) opts.unshift({ value: "", label: "ทั้งหมด" });
    if (prefix === "f_" && f.blank) opts.unshift({ value: "", label: f.blank });
    input = '<select id="' + prefix + f.key + '"' + (locked ? " disabled" : "") + ">" + opts.map(o =>
      '<option value="' + esc(o.value) + '"' + (String(o.value) === String(v) ? " selected" : "") + ">" + esc(o.label) + "</option>").join("") + "</select>";
  } else {
    input = '<input id="' + prefix + f.key + '" type="' + f.type + '"' + (f.step ? ' step="' + f.step + '"' : "") +
      ' value="' + esc(v) + '"' + (locked ? " disabled" : "") + ">";
  }
  return '<div class="field"><label>' + f.label + "</label>" + input + "</div>";
}

// ---------- แท็บ ----------
function buildTabs() {
  $("#tabs").innerHTML = Object.entries(ENTITIES).map(([k, e]) =>
    '<button class="tab' + (k === current ? " active" : "") + '" data-entity="' + k + '">' + e.label +
    ' <code>' + e.table + "</code></button>").join("");
  document.querySelectorAll(".tab").forEach(t => t.onclick = () => {
    current = t.dataset.entity; location.hash = current;
    buildTabs(); buildSearch().then(doSearch);
  });
}

async function buildSearch() {
  await loadLookups(cfg().search);
  $("#searchTitle").textContent = cfg().label;
  $("#searchFields").innerHTML = cfg().search.map(f => fieldHtml(f, "s_")).join("");
  $("#searchFields").querySelectorAll("input").forEach(i => i.onkeydown = e => { if (e.key === "Enter") doSearch(); });
}

// ---------- ค้นหา + วาดตาราง ----------
async function doSearch() {
  const params = new URLSearchParams();
  cfg().search.forEach(f => { const v = $("#s_" + f.key).value; if (v) params.append(f.key, v); });
  setStatus($("#status"), "กำลังค้นหา...");
  renderTable(await api(cfg().api + "?" + params.toString()));
}

function renderTable(r) {
  const head = $("#tableHead"), body = $("#tableBody"), st = $("#status");
  head.innerHTML = ""; body.innerHTML = ""; $("#sqlBox").innerHTML = "";
  if (!r.ok) { setStatus(st, "⚠️ " + r.error, "err"); return; }
  $("#sqlBox").innerHTML = sqlToggle(r.sql);
  lastRows = r.data || [];
  if (!lastRows.length) { setStatus(st, "ไม่พบข้อมูล (0 แถว)"); return; }
  setStatus(st, "พบ " + lastRows.length + " แถว");
  const c = cfg(), cols = Object.keys(lastRows[0]);
  const kind = col => (c.joinCols || []).includes(col) ? "join" : (c.calcCols || []).includes(col) ? "calc" : "own";
  head.innerHTML = (c.photo ? "<th></th>" : "") + cols.map(col => '<th class="' + kind(col) + '">' + col + "</th>").join("") + "<th>จัดการ</th>";
  body.innerHTML = lastRows.map((row, i) =>
    "<tr>" + (c.photo ? "<td>" + photo(row[c.photo]) + "</td>" : "") + cols.map(col => cell(row[col])).join("") +
    '<td class="actions">' + (c.details || []).map(d => '<button class="btn sm info" onclick="showDetail(' + i + ",'" + d.key + "')\">" + d.label + "</button>").join("") +
    '<button class="btn sm" onclick="editRow(' + i + ')">แก้ไข</button>' +
    '<button class="btn sm del" onclick="deleteRow(' + i + ')">ลบ</button></td></tr>').join("");
}

// ---------- รายละเอียด 1 แถว ----------
async function showDetail(i, key) {
  const row = lastRows[i], d = cfg().details.find(x => x.key === key);
  const r = await api(cfg().api + "/" + keyOf(row) + "/" + key);
  $("#detailTitle").textContent = d.title(row);
  const img = $("#detailPhoto");
  if (cfg().photo) { img.src = "/static/images/" + row[cfg().photo] + ".jpg"; img.onerror = () => { img.onerror = null; img.src = "/static/images/default.png"; }; img.classList.remove("hidden"); }
  else img.classList.add("hidden");
  let html = r.ok ? simpleTable(r.data) : '<div class="status err">⚠️ ' + esc(r.error) + "</div>";
  if (r.ok && key === "transcript") html += gpaxSummary(r.data);
  $("#detailBody").innerHTML = html + sqlToggle(r.sql);
  $("#detail").classList.remove("hidden");
}

// เกรดเฉลี่ยสะสม = Σ(แต้ม × หน่วยกิต) / Σ หน่วยกิต (ไม่นับวิชาที่ยังไม่มีเกรด)
function gpaxSummary(rows) {
  const done = rows.filter(r => r.point !== null);
  const cr = done.reduce((s, r) => s + r.credit, 0);
  const pts = done.reduce((s, r) => s + r.point * r.credit, 0);
  return '<div class="gpax">หน่วยกิตที่มีเกรด <b>' + cr + "</b> · เกรดเฉลี่ยสะสม (GPAX) <b>" + (cr ? (pts / cr).toFixed(2) : "—") + "</b></div>";
}

// ---------- เพิ่ม / แก้ไข / ลบ ----------
async function openForm(title, data = {}) {
  await loadLookups(cfg().form);
  $("#modalTitle").textContent = title;
  $("#formFields").innerHTML = cfg().form.map(f => fieldHtml(f, "f_", data[f.key], editingKey !== null && f.lockOnEdit)).join("");
  $("#modal").classList.remove("hidden");
}

async function editRow(i) {
  const r = await api(cfg().api + "/" + keyOf(lastRows[i]));
  if (!r.ok || !r.data.length) { alert("⚠️ " + (r.error || "ไม่พบข้อมูล")); return; }
  editingKey = keyOf(lastRows[i]);
  openForm("แก้ไข" + cfg().label, r.data[0]);
}

async function deleteRow(i) {
  const c = cfg(), row = lastRows[i];
  const label = c.idKeys.map(k => k + " = " + row[k]).join(", ");
  if (!confirm("ยืนยันการลบ " + c.table + " ที่ " + label + " ?" + (c.deleteWarn ? "\n\n⚠️ " + c.deleteWarn : ""))) return;
  showResult(await api(c.api + "/" + keyOf(row), { method: "DELETE" }));
}

async function save() {
  const data = {};
  cfg().form.filter(f => f.key).forEach(f => data[f.key] = $("#f_" + f.key).value);
  const url = editingKey !== null ? cfg().api + "/" + editingKey : cfg().api;
  const r = await api(url, { method: editingKey !== null ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
  if (!r.ok) { alert("⚠️ " + r.error); return; }
  $("#modal").classList.add("hidden");
  showResult(r);
}

// แสดงคำสั่ง INSERT / UPDATE / DELETE ที่เพิ่งรัน แล้วโหลดตารางใหม่ (dropdown อาจเปลี่ยน → ล้าง cache)
function showResult(r) {
  if (!r.ok) { alert("⚠️ " + r.error); return; }
  Object.keys(lookupCache).forEach(k => delete lookupCache[k]);
  $("#lastCmd").classList.remove("hidden");
  $("#lastCmdBody").innerHTML = '<pre class="sqlpre">' + esc(r.sql) + '</pre><div class="status ok">✔ Query OK · ' + r.affected + " row(s) affected</div>";
  doSearch();
}

$("#btnSearch").onclick = doSearch;
$("#btnClear").onclick = () => buildSearch().then(doSearch);
$("#btnAdd").onclick = () => { editingKey = null; openForm("เพิ่ม" + cfg().label + "ใหม่"); };
$("#btnSave").onclick = save;
$("#btnCancel").onclick = () => $("#modal").classList.add("hidden");
$("#btnDetailClose").onclick = () => $("#detail").classList.add("hidden");
document.addEventListener("keydown", e => { if (e.key === "Escape") document.querySelectorAll(".modal").forEach(m => m.classList.add("hidden")); });

buildTabs();
buildSearch().then(doSearch);
