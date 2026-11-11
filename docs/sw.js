// สร้างโดย build.py — อย่าแก้ไฟล์นี้ตรง ๆ
// เปิดเว็บได้แม้ไม่มีเน็ต: มีเน็ต = โหลดของใหม่เสมอ (แล้วเก็บสำเนา) · ไม่มีเน็ต = ใช้สำเนาในเครื่อง
var CACHE = "db-024f2e8f5c";
var CORE = ["./", "index.html", "01-intro.html", "02-er-model.html", "03-relational-normalization.html", "04-sql-ddl-dml.html", "05-select.html", "06-join.html", "07-view.html", "08-index.html", "09-transaction.html", "10-security.html", "11-stored-procedure.html", "12-trigger.html", "appendix-a-script.html", "appendix-b-cheatsheet.html", "appendix-c-dbeaver.html", "appendix-d-university-web.html", "appendix-f-course.html", "appendix-g-pen.html", "assets/style.css", "assets/nav.js", "assets/password.js", "assets/ink.js", "icon/awesome.png", "icon/drink.png", "icon/drink2.png", "icon/electricity.png", "icon/library-diagram.png", "icon/me_cat.png", "icon/nap.png", "icon/prymania.jpg", "icon/thinking.png", "icon/well-done2.png", "icon/worker.png", "icon/worker5.png", "icon/you-did-it.png"];
self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(CORE); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  e.respondWith(fetch(e.request).then(function (res) {
    if (res && (res.ok || res.type === "opaque")) {
      var copy = res.clone();
      caches.open(CACHE).then(function (c) { c.put(e.request, copy); });
    }
    return res;
  }).catch(function () {
    return caches.match(e.request, { ignoreSearch: true }).then(function (hit) {
      return hit || (e.request.mode === "navigate" ? caches.match("index.html") : undefined);
    });
  }));
});
