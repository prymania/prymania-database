// ---------- เมนูสำหรับจอมือถือ ----------
(function () {
  var btn = document.getElementById("menuBtn");
  var side = document.getElementById("sidebar");
  if (!btn || !side) return;
  btn.addEventListener("click", function () { side.classList.toggle("open"); });
  side.querySelectorAll("nav a").forEach(function (a) {
    a.addEventListener("click", function () { side.classList.remove("open"); });
  });
})();

// ---------- ไฮไลต์ SQL อัตโนมัติ (<pre class="sql">) + ปุ่มคัดลอก ----------
// เรียกซ้ำได้กับเนื้อหาที่เพิ่งใส่ลงหน้า (เช่น เฉลยที่เพิ่งถอดรหัส): window.dbEnhance(element)
window.dbEnhance = function (root) { highlightSql(root); addCopyButtons(root); };
function highlightSql(root) {
  var KW = ("select from where and or not in is null as distinct order by group having limit offset asc desc " +
    "insert into values update set delete create table database drop alter add column modify change rename to " +
    "primary key foreign references unique check default constraint auto_increment on cascade restrict " +
    "join inner left right full outer cross union all intersect except exists between like case when then else end " +
    "view index transaction start commit rollback savepoint grant revoke user role identified with option " +
    "procedure function trigger begin declare return returns if elseif while do loop leave call delimiter " +
    "before after for each row new old signal sqlstate describe show use truncate explain character collate " +
    "int integer varchar char decimal numeric date datetime timestamp text boolean tinyint bigint float double enum").split(" ");
  var kw = {}; KW.forEach(function (w) { kw[w] = 1; });
  var FN = { count: 1, sum: 1, avg: 1, max: 1, min: 1, round: 1, ifnull: 1, coalesce: 1, concat: 1, upper: 1, lower: 1,
    left: 1, substring: 1, char_length: 1, length: 1, year: 1, month: 1, day: 1, curdate: 1, now: 1,
    timestampdiff: 1, datediff: 1, last_insert_id: 1, trim: 1, replace: 1 };
  function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
  var re = /(--[^\n]*|\/\*[\s\S]*?\*\/)|('(?:[^'\\]|\\.)*')|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z0-9_]*)|([\s\S])/g;
  root.querySelectorAll("pre.sql").forEach(function (pre) {
    var src = pre.textContent, out = "", m;
    re.lastIndex = 0;
    while ((m = re.exec(src)) !== null) {
      if (m[1]) out += '<span class="c">' + esc(m[1]) + "</span>";
      else if (m[2]) out += '<span class="s">' + esc(m[2]) + "</span>";
      else if (m[3]) out += '<span class="n">' + m[3] + "</span>";
      else if (m[4]) {
        var w = m[4].toLowerCase();
        if (FN[w] && src.charAt(re.lastIndex) === "(") out += '<span class="f">' + m[4] + "</span>";
        else if (kw[w]) out += '<span class="k">' + m[4] + "</span>";
        else out += m[4];
      } else out += esc(m[5]);
    }
    pre.innerHTML = out;
  });
}

// ---------- ปุ่มคัดลอกในทุก code card ----------
function addCopyButtons(root) {
  root.querySelectorAll(".code").forEach(function (block) {
    var head = block.querySelector(".code-head");
    var pre = block.querySelector("pre");
    if (!head || !pre) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-btn";
    btn.textContent = "📋 คัดลอก";
    btn.addEventListener("click", function () {
      var text = pre.textContent;
      var done = function () {
        btn.textContent = "✓ คัดลอกแล้ว";
        btn.classList.add("copied");
        setTimeout(function () { btn.textContent = "📋 คัดลอก"; btn.classList.remove("copied"); }, 1500);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done);
      } else {
        var ta = document.createElement("textarea");
        ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select(); document.execCommand("copy");
        document.body.removeChild(ta); done();
      }
    });
    head.appendChild(btn);
  });
}
window.dbEnhance(document);

// ---------- ปุ่มดูเฉลย / ซ่อนเฉลย ----------
(function () {
  document.querySelectorAll(".ans-btn").forEach(function (btn) {
    var ans = btn.nextElementSibling;
    if (!ans || !ans.classList.contains("answer")) return;
    btn.addEventListener("click", function () {
      var open = ans.classList.toggle("show");
      btn.classList.toggle("open", open);
      btn.textContent = open ? "🙈 ซ่อนเฉลย" : "👀 ดูเฉลย";
    });
  });
})();

// ---------- ปุ่มคัดลอกคำถามท้ายบททั้งหมด (พร้อมเลขข้อ) ----------
(function () {
  document.querySelectorAll(".review").forEach(function (box) {
    var btn = box.querySelector(".review-copy");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var lines = [], n = 0;
      box.querySelectorAll("ol > li").forEach(function (li) {
        var c = li.cloneNode(true);
        c.querySelectorAll(".rv-ans").forEach(function (x) { x.remove(); });   // ไม่คัดลอกเฉลย
        var txt = c.textContent.replace(/\s+/g, " ").trim();
        if (li.classList.contains("part")) { lines.push("", "[" + txt + "]"); return; }
        n += 1;
        lines.push(n + ". " + txt);
      });
      var text = "คำถามท้ายบท — " + document.title.split(" — ")[0] + "\n" + lines.join("\n").replace(/^\n/, "");
      var done = function () {
        btn.textContent = "✓ คัดลอกแล้ว";
        btn.classList.add("copied");
        setTimeout(function () { btn.textContent = "📋 คัดลอกคำถามทั้งหมด"; btn.classList.remove("copied"); }, 1600);
      };
      if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done);
      else {
        var ta = document.createElement("textarea");
        ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select(); document.execCommand("copy");
        document.body.removeChild(ta); done();
      }
    });
  });
})();

// ---------- เฉลยคำถามท้ายบท (ต้องใส่รหัสผ่าน — กำหนดใน assets/password.js) ----------
(function () {
  var m = location.pathname.match(/(?:^|\/)(\d+)-[^\/]*$/);       // 07-view.html → c7
  var CH = m ? "c" + parseInt(m[1], 10) : null;
  var KEY = "dbAnswersUnlocked-" + CH;
  function ok() { try { return sessionStorage.getItem(KEY) === "1"; } catch (e) { return false; } }
  function remember() { try { sessionStorage.setItem(KEY, "1"); } catch (e) {} }
  document.querySelectorAll(".review").forEach(function (box) {
    var btn = box.querySelector(".review-key"), form = box.querySelector(".review-lock");
    if (!btn || !form) return;
    if (!box.querySelector(".rv-ans")) { btn.hidden = true; return; }
    var input = form.querySelector("input"), msg = form.querySelector(".review-msg");
    function show(on) {
      box.classList.toggle("unlocked", on);
      btn.textContent = on ? "🙈 ซ่อนเฉลย" : "🔑 ดูเฉลย";
      form.hidden = true;
    }
    btn.addEventListener("click", function () {
      if (box.classList.contains("unlocked")) { show(false); return; }
      if (ok()) { show(true); return; }
      form.hidden = !form.hidden;
      msg.textContent = "";
      if (!form.hidden) input.focus();
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var all = window.EXERCISE_PASSWORDS;
      if (!all) { msg.textContent = "ไม่พบไฟล์ assets/password.js"; return; }
      var pw = all[CH];
      if (pw === undefined) { msg.textContent = "ยังไม่ได้กำหนดรหัสผ่านของบทนี้ (" + CH + ") ใน password.js"; return; }
      if (input.value === String(pw)) { remember(); input.value = ""; show(true); }
      else { msg.textContent = "รหัสผ่านไม่ถูกต้อง"; input.select(); }
    });
  });
})();

// ---------- ไฮไลต์หัวข้อย่อยที่กำลังอ่านในเมนูด้านข้าง ----------
(function () {
  var links = document.querySelectorAll(".subnav a");
  if (!links.length || !("IntersectionObserver" in window)) return;
  var map = {};
  links.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
  var obs = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting && map[e.target.id]) {
        links.forEach(function (a) { a.classList.remove("here"); });
        map[e.target.id].classList.add("here");
      }
    });
  }, { rootMargin: "0px 0px -75% 0px" });
  Object.keys(map).forEach(function (id) { var el = document.getElementById(id); if (el) obs.observe(el); });
})();
