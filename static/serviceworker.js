const CACHE_NAME = 'blackflagmc-cache-v1';
const urlsToCache = [
  '/static/images/login-bg.webp',
  '/static/manifest.json',
  '/static/serviceworker.js',
  '/static/web/apple-touch-icon.png',
  '/static/web/favicon.ico',
  '/static/web/icon-192.png',
  '/static/web/icon-192-maskable.png',
  '/static/web/icon-512.png',
  '/static/web/icon-512-maskable.png',
  // Diğer statik dosyalar buraya eklenebilir
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
}); 