/* Offline cache for the QR card (/qr/): opens instantly at events, even without signal. */
var CACHE = "sda-qr-v1";
var FILES = ["/qr/", "/qr/manifest.webmanifest", "/assets/fonts/geist-latin.woff2", "/assets/brand/apple-touch-icon.png?v=2", "/assets/sda-ai-services.vcf"];
self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(FILES); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
// network first (always the latest version), cache when offline
self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  e.respondWith(fetch(e.request).then(function (r) {
    if (r.ok && new URL(e.request.url).origin === location.origin) { var copy = r.clone(); caches.open(CACHE).then(function (c) { c.put(e.request, copy); }); }
    return r;
  }).catch(function () { return caches.match(e.request, { ignoreSearch: false }).then(function (m) { return m || caches.match("/qr/"); }); }));
});
