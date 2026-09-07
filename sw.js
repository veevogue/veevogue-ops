/* ===== فيفوق — عامل الخدمة =====
   يخزّن التطبيق كامل على الجهاز: يفتح بدون إنترنت، ويفتح فوراً حتى لو الشبكة بطيئة
   أو كانت المكتبات محجوبة (مثل ما يصير في الصين). ما يلمس طلبات سوبابيس أبداً —
   تلك يتكفّل فيها طابور العمليات داخل التطبيق. */
/* النسخة تجي من رابط التسجيل sw.js?v=… فما نحتاج نعدّل هذا الملف كل مرة */
const V = new URL(self.location.href).searchParams.get("v") || "0";
const CACHE = "vv-shell-" + V;
const SHELL = [
  "./",
  "./index.html",
  "./fonts.css",
  "./manifest.json",
  "./apple-touch-icon.png?v=2",
  "./vendor/supabase.js",
  "./vendor/html2canvas.min.js",
  "./vendor/jsQR.js",
  "./fonts/almarai-tssoApxBaigK_hnnS-agtn-Wow.woff2",
  "./fonts/almarai-tssoApxBaigK_hnnS-agtnqWo572.woff2",
  "./fonts/almarai-tssoApxBaigK_hnnS_qjtn-Wow.woff2",
  "./fonts/almarai-tssoApxBaigK_hnnS_qjtnqWo572.woff2",
  "./fonts/almarai-tsstApxBaigK_hnnQ12Fow.woff2",
  "./fonts/almarai-tsstApxBaigK_hnnQ1iFo0C3.woff2",
  "./fonts/instrumentserif-jizBRFtNs2ka5fXjeivQ4LroWlx-6zUTjg.woff2",
  "./fonts/instrumentserif-jizHRFtNs2ka5fXjeivQ4LroWlx-6zAjjH7M.woff2",
  "./fonts/inter-UcC73FwrK3iLTeHuS_nVMrMxCp50SjIa1ZL7.woff2",
  "./fonts/italiana-QldNNTtLsx4E__B0XQmWaXw.woff2",
  "./fonts/outfit-QGYvz_MVcBeNP4NJtEtq.woff2",
  "./fonts/tajawal-Iura6YBj_oCad4k1nzGBCw.woff2",
  "./fonts/tajawal-Iura6YBj_oCad4k1nzSBC45I.woff2",
  "./fonts/tajawal-Iurf6YBj_oCad4k1l4qkHrFpiQ.woff2",
  "./fonts/tajawal-Iurf6YBj_oCad4k1l4qkHrRpiYlJ.woff2",
  "./fonts/tajawal-Iurf6YBj_oCad4k1l8KiHrFpiQ.woff2",
  "./fonts/tajawal-Iurf6YBj_oCad4k1l8KiHrRpiYlJ.woff2"
];
const HOME = new URL("./", self.registration.scope).href;

self.addEventListener("install", e=>{
  e.waitUntil((async ()=>{
    const c = await caches.open(CACHE);
    /* نضيفهم واحد واحد: ملف واحد يفشل ما يسقط التخزين كله */
    await Promise.all(SHELL.map(u => c.add(new Request(u, {cache:"reload"})).catch(()=>{})));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", e=>{
  e.waitUntil((async ()=>{
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k.startsWith("vv-shell-") && k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

function timeout(p, ms){
  return new Promise((res, rej)=>{
    const t = setTimeout(()=>rej(new Error("timeout")), ms);
    p.then(v=>{ clearTimeout(t); res(v); }, err=>{ clearTimeout(t); rej(err); });
  });
}

self.addEventListener("fetch", e=>{
  const req = e.request;
  if(req.method !== "GET") return;

  const url = new URL(req.url);
  if(url.origin !== self.location.origin) return;      /* سوبابيس والصور — نتركها للتطبيق */
  if(url.searchParams.has("cb")) return;               /* فحص النسخة — دايماً من الشبكة */

  /* فتح التطبيق: الشبكة أولاً بمهلة قصيرة، وإلا النسخة المخزّنة */
  if(req.mode === "navigate"){
    e.respondWith((async ()=>{
      try{
        const net = await timeout(fetch(req), 4000);
        if(net && net.ok){ const c = await caches.open(CACHE); c.put(HOME, net.clone()); }
        return net;
      }catch(err){
        const c = await caches.open(CACHE);
        return (await c.match(HOME)) ||
               (await c.match(req, {ignoreSearch:true})) ||
               new Response("<h1>بدون إنترنت</h1>", {status:503, headers:{"Content-Type":"text/html; charset=utf-8"}});
      }
    })());
    return;
  }

  /* المكتبات والخطوط والأيقونة: من الجهاز أولاً */
  e.respondWith((async ()=>{
    const c = await caches.open(CACHE);
    const hit = await c.match(req, {ignoreSearch:true});
    if(hit) return hit;
    try{
      const net = await fetch(req);
      if(net && net.ok && net.type === "basic") c.put(req, net.clone());
      return net;
    }catch(err){
      return new Response("", {status:504});
    }
  })());
});

self.addEventListener("message", e=>{ if(e.data === "skipWaiting") self.skipWaiting(); });
