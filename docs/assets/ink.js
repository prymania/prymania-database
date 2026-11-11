// ---------- ปากกาเขียนทับหน้าเว็บ (สำหรับสอนด้วย iPad + Apple Pencil) ----------
// • กด ✏️ เพื่อเปิดโหมดปากกา: Apple Pencil / เมาส์ = เขียน · นิ้ว = เลื่อน/ซูมหน้าตามปกติของ iPad
// • 📒 กระดานทด: กระดาษเต็มจอทับบทเรียน (เส้นบรรทัด / ตาราง / ว่าง) มีหลายหน้า แยกตามบท
// • หมึกบันทึกอัตโนมัติในเบราว์เซอร์เครื่องนั้น (localStorage คีย์ "ink:<ไฟล์>" และ "ink:board:<ไฟล์>")
// • ⬇️ สำรองหมึกทุกหน้า (รวมกระดาน) เป็นไฟล์ .json · ⬆️ นำไฟล์สำรองกลับเข้ามา
// • หมึกเก็บเป็นเส้น (SVG) ตามตำแหน่งในคอลัมน์เนื้อหา จึงคมทุกขนาดจอและพิมพ์ออก PDF ได้
(function () {
  var main = document.querySelector(".content");
  if (!main) return;
  var NS = "http://www.w3.org/2000/svg";
  var FILE = location.pathname.split("/").pop() || "index.html";
  var KEY = "ink:" + FILE, BKEY = "ink:board:" + FILE;
  var PENS = [
    { c: "#17202d", w: 2.6, o: 1, label: "ปากกาดำ" },
    { c: "#e0533f", w: 2.6, o: 1, label: "ปากกาแดง" },
    { c: "#2f80ed", w: 2.6, o: 1, label: "ปากกาน้ำเงิน" },
    { c: "#14a08e", w: 2.6, o: 1, label: "ปากกาเขียว" },
    { c: "#FFD6EE", w: 18, o: 1, h: 1, label: "ไฮไลต์ชมพู" },
    { c: "#CED1F8", w: 18, o: 1, h: 1, label: "ไฮไลต์ม่วง" },
    { c: "#EAFF4F", w: 18, o: 1, h: 1, label: "ไฮไลต์เหลืองสะท้อนแสง" }
  ];
  var PAPERS = [["lines", "≡", "เส้นบรรทัด"], ["grid", "▦", "ตาราง"], ["blank", "▢", "กระดาษว่าง"]];
  var st = { on: false, pen: 0, eraser: false, board: false };

  function getJSON(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } }
  function plainStrokes(a) { return a.map(function (s) { return { c: s.c, w: s.w, o: s.o, p: s.p }; }); }

  // ---- พื้นผิวที่ 1: หน้าบทเรียน
  var lesson = { host: main, svg: mkSvg("ink-layer"), data: null };
  main.appendChild(lesson.svg);
  lesson.load = function () { var d = getJSON(KEY); this.data = d && d.strokes ? d : { w: 0, strokes: [] }; };
  lesson.strokes = function () { return this.data.strokes; };
  lesson.setStrokes = function (a) { this.data.strokes = a; };
  lesson.save = function () {
    this.data.w = main.clientWidth;
    store(KEY, this.data.strokes.length ? { w: this.data.w, strokes: plainStrokes(this.data.strokes) } : null);
  };

  // ---- พื้นผิวที่ 2: กระดานทด (เต็มจอ หลายหน้า)
  var boardEl = document.createElement("div");
  boardEl.className = "ink-board";
  boardEl.hidden = true;
  boardEl.innerHTML = '<div class="ink-sheet"><div class="ink-paper"></div></div>';
  document.body.appendChild(boardEl);
  var sheet = boardEl.querySelector(".ink-sheet"), paper = boardEl.querySelector(".ink-paper");
  var board = { host: paper, svg: mkSvg("ink-layer ink-board-layer"), data: null };
  paper.appendChild(board.svg);
  board.load = function () {
    var d = getJSON(BKEY);
    this.data = d && d.pages && d.pages.length ? d : { paper: "lines", cur: 0, pages: [{ strokes: [] }] };
    this.data.cur = Math.min(this.data.cur || 0, this.data.pages.length - 1);
  };
  board.page = function () { return this.data.pages[this.data.cur]; };
  board.strokes = function () { return this.page().strokes; };
  board.setStrokes = function (a) { this.page().strokes = a; };
  board.save = function () {
    var d = this.data, used = d.pages.some(function (p) { return p.strokes.length; });
    store(BKEY, used || d.pages.length > 1 ? {
      paper: d.paper, cur: d.cur, pages: d.pages.map(function (p) { return { strokes: plainStrokes(p.strokes) }; })
    } : null);
  };

  var S = lesson;   // พื้นผิวที่กำลังเขียนอยู่

  function mkSvg(cls) {
    var s = document.createElementNS(NS, "svg");
    s.setAttribute("class", cls);
    s.setAttribute("aria-hidden", "true");
    return s;
  }
  function store(k, v) {
    try { if (v) localStorage.setItem(k, JSON.stringify(v)); else localStorage.removeItem(k); }
    catch (e) { say("บันทึกไม่ได้ (พื้นที่เต็มหรือถูกปิด) — กด ⬇️ เพื่อสำรองเป็นไฟล์", 5000); }
  }

  // ---- แถบเครื่องมือ
  var bar = document.createElement("div");
  bar.className = "ink-bar";
  bar.innerHTML =
    '<div class="ink-tools">' +
    '<span class="ink-pages">' +
    '<button type="button" class="ink-paper-kind" title="ชนิดกระดาษ" aria-label="ชนิดกระดาษ">≡</button>' +
    '<button type="button" class="ink-prev" title="หน้าก่อน" aria-label="หน้าก่อน">‹</button>' +
    '<span class="ink-pno" aria-live="polite">1/1</span>' +
    '<button type="button" class="ink-next" title="หน้าถัดไป" aria-label="หน้าถัดไป">›</button>' +
    '<button type="button" class="ink-add" title="เพิ่มหน้าใหม่" aria-label="เพิ่มหน้าใหม่">＋</button>' +
    '</span>' +
    PENS.map(function (p, i) {
      return '<button type="button" class="ink-pen" data-i="' + i + '" title="' + p.label + '" aria-label="' + p.label + '">' +
        '<span' + (p.h ? ' class="hl"' : "") + ' style="background:' + p.c + '"></span></button>';
    }).join("") +
    '<button type="button" class="ink-eraser" title="ยางลบ (แตะเส้นที่จะลบ)" aria-label="ยางลบ">🧽</button>' +
    '<button type="button" class="ink-undo" title="ย้อนกลับ" aria-label="ย้อนกลับ">↶</button>' +
    '<button type="button" class="ink-board-btn" title="กระดานทด (กระดาษเปล่า)" aria-label="เปิดกระดานทด" aria-pressed="false">📒</button>' +
    '<button type="button" class="ink-clear" title="ล้างหมึกหน้านี้" aria-label="ล้างหมึกหน้านี้">🗑</button>' +
    '<button type="button" class="ink-export" title="สำรองหมึกทุกหน้าเป็นไฟล์" aria-label="สำรองหมึกเป็นไฟล์">⬇️</button>' +
    '<button type="button" class="ink-import" title="นำไฟล์สำรองหมึกเข้ามา" aria-label="นำไฟล์สำรองเข้ามา">⬆️</button>' +
    '<input type="file" accept=".json,application/json" hidden>' +
    '</div>' +
    '<button type="button" class="ink-big" title="โหมดฉายจอ: ขยายตัวหนังสือ" aria-label="โหมดฉายจอ ขยายตัวหนังสือ" aria-pressed="false">A+</button>' +
    '<button type="button" class="ink-toggle" title="ปากกา" aria-label="เปิดโหมดปากกา" aria-pressed="false">✏️</button>' +
    '<div class="ink-toast" hidden></div>';
  document.body.appendChild(bar);
  var $ = function (s) { return bar.querySelector(s); };
  var toggle = $(".ink-toggle"), toast = $(".ink-toast"), file = $("input[type=file]");

  function say(msg, ms) {
    toast.textContent = msg; toast.hidden = false;
    clearTimeout(say.t); say.t = setTimeout(function () { toast.hidden = true; }, ms || 2500);
  }
  function refreshBar() {
    var html = document.documentElement;
    html.classList.toggle("ink-on", st.on);
    html.classList.toggle("ink-board-open", st.board);
    toggle.textContent = st.on ? "✕" : "✏️";
    toggle.setAttribute("aria-pressed", String(st.on));
    toggle.setAttribute("aria-label", st.on ? "ปิดโหมดปากกา" : "เปิดโหมดปากกา");
    bar.querySelectorAll(".ink-pen").forEach(function (b) { b.classList.toggle("active", !st.eraser && +b.dataset.i === st.pen); });
    $(".ink-eraser").classList.toggle("active", st.eraser);
    var bb = $(".ink-board-btn");
    bb.classList.toggle("active", st.board);
    bb.setAttribute("aria-pressed", String(st.board));
    bb.title = st.board ? "กลับไปบทเรียน" : "กระดานทด (กระดาษเปล่า)";
    $(".ink-clear").title = st.board ? "ล้างหน้านี้ (หน้าว่าง: ลบหน้าทิ้ง)" : "ล้างหมึกหน้านี้";
    if (board.data) {
      var d = board.data, kind = PAPERS.filter(function (p) { return p[0] === d.paper; })[0] || PAPERS[0];
      $(".ink-pno").textContent = (d.cur + 1) + "/" + d.pages.length;
      $(".ink-prev").disabled = d.cur === 0;
      $(".ink-next").disabled = d.cur === d.pages.length - 1;
      var pk = $(".ink-paper-kind");
      pk.textContent = kind[1]; pk.title = "ชนิดกระดาษ: " + kind[2] + " (แตะเพื่อเปลี่ยน)";
      paper.className = "ink-paper paper-" + kind[0];
    }
  }

  // ---- วาดเส้น
  function pathD(p) {
    if (p.length === 1) return "M" + p[0][0] + " " + p[0][1] + "l0.01 0";
    var d = "M" + p[0][0] + " " + p[0][1];
    for (var i = 1; i < p.length - 1; i++) {
      var xc = (p[i][0] + p[i + 1][0]) / 2, yc = (p[i][1] + p[i + 1][1]) / 2;
      d += "Q" + p[i][0] + " " + p[i][1] + " " + xc.toFixed(1) + " " + yc.toFixed(1);
    }
    var l = p[p.length - 1];
    return d + "L" + l[0] + " " + l[1];
  }
  function draw(s, svg) {
    var el = document.createElementNS(NS, "path");
    el.setAttribute("fill", "none");
    el.setAttribute("stroke", s.c);
    el.setAttribute("stroke-width", s.w);
    el.setAttribute("stroke-linecap", "round");
    el.setAttribute("stroke-linejoin", "round");
    if (s.o < 1) el.setAttribute("stroke-opacity", s.o);
    el.setAttribute("d", pathD(s.p));
    (svg || S.svg).appendChild(el);
    s.el = el;
    return el;
  }
  function render(surf) {
    while (surf.svg.firstChild) surf.svg.removeChild(surf.svg.firstChild);
    surf.strokes().forEach(function (s) { draw(s, surf.svg); });
  }

  // ---- อินพุต (ใช้ร่วมกันทั้งบทเรียนและกระดาน)
  var cur = null, eraseOn = false;
  function pt(e) {
    // โหมดฉายจอ (A+) ขยายคอลัมน์ด้วย CSS zoom: แปลงพิกัดจอกลับเป็นพิกัดก่อนขยาย หมึกจึงตรงทั้งสองโหมด
    var r = S.host.getBoundingClientRect(), z = (S.host.offsetWidth && r.width / S.host.offsetWidth) || 1;
    return [Math.round((e.clientX - r.left) / z * 10) / 10, Math.round((e.clientY - r.top) / z * 10) / 10];
  }
  function canDraw(e) { return e.pointerType === "pen" || e.pointerType === "mouse"; }   // นิ้ว (touch) ปล่อยให้เบราว์เซอร์เลื่อน/ซูม
  function segDist(q, a, b) {   // ระยะจากจุด q ถึงส่วนของเส้นตรง ab
    var vx = b[0] - a[0], vy = b[1] - a[1], L = vx * vx + vy * vy;
    var t = L ? Math.max(0, Math.min(1, ((q[0] - a[0]) * vx + (q[1] - a[1]) * vy) / L)) : 0;
    var dx = a[0] + t * vx - q[0], dy = a[1] + t * vy - q[1];
    return Math.sqrt(dx * dx + dy * dy);
  }
  function eraseAt(q) {
    var a = S.strokes(), hit = false;
    for (var i = a.length - 1; i >= 0; i--) {
      var s = a[i], r = s.w / 2 + 10;
      for (var j = 0; j < s.p.length; j++) {
        if (segDist(q, s.p[j], s.p[j + 1] || s.p[j]) < r) { s.el.remove(); a.splice(i, 1); hit = true; break; }
      }
    }
    return hit;
  }
  // iPad Safari: กันการเลื่อน/เลือกข้อความ/Scribble เฉพาะเมื่อแตะด้วย Apple Pencil (touchType "stylus")
  // ไม่อย่างนั้น Safari จะยกเลิกเส้น (pointercancel) ทำให้ขีดได้แค่เส้นสั้น ๆ — นิ้วไม่ถูกกัน จึงเลื่อน/ซูมได้ตามปกติ
  function stylus(e) {
    for (var i = 0; i < e.changedTouches.length; i++) if (e.changedTouches[i].touchType === "stylus") return true;
    return false;
  }
  function wire(surf) {
    var svg = surf.svg;
    svg.addEventListener("pointerdown", function (e) {
      if (!st.on || S !== surf || !canDraw(e)) return;
      e.preventDefault();
      try { svg.setPointerCapture(e.pointerId); } catch (err) {}
      if (st.eraser) { eraseOn = true; if (eraseAt(pt(e))) S.save(); return; }
      var p = PENS[st.pen];
      cur = { c: p.c, w: p.w, o: p.o, p: [pt(e)] };
      draw(cur);
    });
    svg.addEventListener("pointermove", function (e) {
      if (eraseOn) { if (eraseAt(pt(e))) S.save(); return; }
      if (!cur) return;
      var evs = e.getCoalescedEvents ? e.getCoalescedEvents() : [e];
      (evs.length ? evs : [e]).forEach(function (ev) {
        var q = pt(ev), l = cur.p[cur.p.length - 1];
        if (Math.abs(q[0] - l[0]) + Math.abs(q[1] - l[1]) >= 1) cur.p.push(q);
      });
      cur.el.setAttribute("d", pathD(cur.p));
    });
    function end() {
      if (eraseOn) { eraseOn = false; return; }
      if (!cur) return;
      S.strokes().push(cur); cur = null; S.save();
    }
    svg.addEventListener("pointerup", end);
    svg.addEventListener("pointercancel", end);
    ["touchstart", "touchmove"].forEach(function (t) {
      svg.addEventListener(t, function (e) { if (st.on && stylus(e)) e.preventDefault(); }, { passive: false });
    });
  }
  wire(lesson);
  wire(board);

  // แตะสั้น ๆ ด้วยนิ้วบนบทเรียนระหว่างโหมดปากกา → ส่งต่อไปยังปุ่ม/ลิงก์ที่อยู่ใต้ชั้นหมึก (เช่น ดูเฉลย)
  var tap = null, lsvg = lesson.svg;
  lsvg.addEventListener("pointerdown", function (e) {
    if (st.on && e.pointerType === "touch") tap = { id: e.pointerId, x: e.clientX, y: e.clientY, t: Date.now() };
  });
  lsvg.addEventListener("pointerup", function (e) {
    if (!tap || e.pointerId !== tap.id) return;
    var quick = Date.now() - tap.t < 500 && Math.abs(e.clientX - tap.x) + Math.abs(e.clientY - tap.y) < 12;
    tap = null;
    if (!quick) return;
    lsvg.style.pointerEvents = "none";
    var el = document.elementFromPoint(e.clientX, e.clientY);
    lsvg.style.pointerEvents = "";
    if (!el) return;
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)) el.focus();
    el.click();
  });
  lsvg.addEventListener("pointercancel", function () { tap = null; });

  // ---- กระดานทด
  function openBoard(on) {
    st.board = on;
    boardEl.hidden = !on;
    S = on ? board : lesson;
    if (on) { render(board); sheet.scrollTop = 0; }
    refreshBar();
  }
  function goPage(i) {
    board.data.cur = i; board.save(); render(board); sheet.scrollTop = 0; refreshBar();
  }
  $(".ink-board-btn").addEventListener("click", function () {
    openBoard(!st.board);
    if (st.board) say("กระดานทด หน้า " + (board.data.cur + 1) + " · แตะ 📒 อีกครั้งเพื่อกลับไปบทเรียน");
  });
  $(".ink-prev").addEventListener("click", function () { if (board.data.cur > 0) goPage(board.data.cur - 1); });
  $(".ink-next").addEventListener("click", function () { if (board.data.cur < board.data.pages.length - 1) goPage(board.data.cur + 1); });
  $(".ink-add").addEventListener("click", function () {
    board.data.pages.splice(board.data.cur + 1, 0, { strokes: [] });
    goPage(board.data.cur + 1);
    say("เพิ่มหน้า " + (board.data.cur + 1) + " แล้ว");
  });
  $(".ink-paper-kind").addEventListener("click", function () {
    var i = PAPERS.map(function (p) { return p[0]; }).indexOf(board.data.paper);
    board.data.paper = PAPERS[(i + 1) % PAPERS.length][0];
    board.save(); refreshBar();
    say("กระดาษ: " + PAPERS[(i + 1) % PAPERS.length][2]);
  });

  // ---- โหมดฉายจอ (A+): ขยายคอลัมน์เนื้อหา 125% จำค่าไว้ทุกหน้า (คลาส big-text ใส่ตั้งแต่ <head>)
  var big = $(".ink-big");
  function setBig(on) {
    document.documentElement.classList.toggle("big-text", on);
    big.textContent = on ? "A−" : "A+";
    big.setAttribute("aria-pressed", String(on));
    big.title = on ? "ปิดโหมดฉายจอ" : "โหมดฉายจอ: ขยายตัวหนังสือ";
    try { localStorage.setItem("big-text", on ? "1" : "0"); } catch (e) {}
  }
  big.addEventListener("click", function () {
    var on = !document.documentElement.classList.contains("big-text");
    var y = window.scrollY / Math.max(1, document.documentElement.scrollHeight);
    setBig(on);
    window.scrollTo(0, y * document.documentElement.scrollHeight);   // คงตำแหน่งอ่านไว้ใกล้เดิม
    say(on ? "โหมดฉายจอ: ตัวหนังสือใหญ่ขึ้น" : "กลับเป็นขนาดปกติ");
  });
  setBig(document.documentElement.classList.contains("big-text"));

  // ---- ปุ่มทั่วไป
  toggle.addEventListener("click", function () {
    st.on = !st.on;
    if (!st.on && st.board) openBoard(false);   // ปิดปากกา = ออกจากกระดานด้วย
    refreshBar();
    if (st.on) say("โหมดปากกา: Pencil เขียน · นิ้วเลื่อน/ซูมได้ตามปกติ");
  });
  bar.querySelectorAll(".ink-pen").forEach(function (b) {
    b.addEventListener("click", function () { st.pen = +b.dataset.i; st.eraser = false; refreshBar(); });
  });
  $(".ink-eraser").addEventListener("click", function () { st.eraser = !st.eraser; refreshBar(); });
  $(".ink-undo").addEventListener("click", function () {
    var s = S.strokes().pop(); if (s) { s.el.remove(); S.save(); }
  });
  var clearArmed = 0;
  $(".ink-clear").addEventListener("click", function () {
    var empty = !S.strokes().length;
    if (empty && !(st.board && board.data.pages.length > 1)) return;
    var what = empty ? "ลบหน้า " + (board.data.cur + 1) + " ของกระดานทิ้ง" : "ล้างหมึกหน้านี้ทั้งหมด";
    if (Date.now() - clearArmed > 3000) { clearArmed = Date.now(); say("แตะ 🗑 อีกครั้งเพื่อ" + what, 3000); return; }
    clearArmed = 0;
    if (empty) {   // กระดาน: หน้าว่าง → ลบหน้าทิ้ง
      board.data.pages.splice(board.data.cur, 1);
      goPage(Math.max(0, board.data.cur - 1));
      say("ลบหน้าแล้ว");
      return;
    }
    S.setStrokes([]); render(S); S.save(); say("ล้างหมึกหน้านี้แล้ว");
  });
  $(".ink-export").addEventListener("click", function () {
    var pages = {}, n = 0;
    for (var i = 0; i < localStorage.length; i++) {
      var k = localStorage.key(i);
      if (k && k.indexOf("ink:") === 0) { try { pages[k] = JSON.parse(localStorage.getItem(k)); n++; } catch (e) {} }
    }
    if (!n) { say("ยังไม่มีหมึกให้สำรอง"); return; }
    var blob = new Blob([JSON.stringify({ app: "database-ink", version: 1, saved: new Date().toISOString(), pages: pages })], { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "database-ink-" + new Date().toISOString().slice(0, 10) + ".json";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
    say("สำรองหมึก " + n + " รายการแล้ว (รวมกระดานทด)");
  });
  $(".ink-import").addEventListener("click", function () { file.click(); });
  file.addEventListener("change", function () {
    var f = file.files[0]; if (!f) return;
    var rd = new FileReader();
    rd.onload = function () {
      try {
        var d = JSON.parse(rd.result), n = 0;
        if (!d || d.app !== "database-ink" || !d.pages) throw 0;
        Object.keys(d.pages).forEach(function (k) {
          if (k.indexOf("ink:") === 0) { localStorage.setItem(k, JSON.stringify(d.pages[k])); n++; }
        });
        lesson.load(); render(lesson);
        board.load(); render(board); refreshBar();
        say("นำหมึกเข้ามา " + n + " รายการแล้ว");
      } catch (e) { say("ไฟล์นี้ไม่ใช่ไฟล์สำรองหมึก"); }
      file.value = "";
    };
    rd.readAsText(f);
  });

  lesson.load(); board.load();
  render(lesson);
  refreshBar();
  var ld = lesson.data;
  if (ld.strokes.length && ld.w && Math.abs(ld.w - main.clientWidth) > 40)
    say("หมึกหน้านี้เขียนตอนจอกว้างต่างจากตอนนี้ ตำแหน่งอาจเลื่อน — หมุนจอให้เหมือนตอนเขียน", 5000);
})();
