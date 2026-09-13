/* Ovryk — service worker: cache-first for the app shell so it loads with no
   network after the first visit. Bump CACHE_VERSION whenever a static asset
   listed in PRECACHE_URLS changes shape; the old cache is dropped on activate. */
var CACHE_VERSION = 'v63';
var CACHE_NAME = 'ovryk-static-' + CACHE_VERSION;

var PRECACHE_URLS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './favicon.png',
  './apple-touch-icon.png'
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function (cache) { return cache.addAll(PRECACHE_URLS); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(
          keys
            .filter(function (key) { return key.indexOf('ovryk-static-') === 0 && key !== CACHE_NAME; })
            .map(function (key) { return caches.delete(key); })
        );
      })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (event) {
  var request = event.request;
  if (request.method !== 'GET') return;

  event.respondWith(
    caches.match(request).then(function (cached) {
      if (cached) return cached;

      return fetch(request).then(function (response) {
        var isCacheable = response && (response.status === 200 || response.type === 'opaque');
        if (isCacheable) {
          var responseClone = response.clone();
          caches.open(CACHE_NAME).then(function (cache) { cache.put(request, responseClone); });
        }
        return response;
      }).catch(function () {
        if (request.mode === 'navigate') return caches.match('./index.html');
        return undefined;
      });
    })
  );
});
