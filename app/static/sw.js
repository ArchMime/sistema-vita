// app/static/sw.js
const CACHE_NAME = 'vita-cache-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/manifest.json',
  '/static/assets/icons/icon-192.png',
  '/static/assets/icons/icon-512.png'
];

// Evento de instalación: Guarda en caché los archivos base
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    }).then(() => self.skipWaiting())
  );
});

// Evento de activación: Limpia cachés antiguas
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Estrategia Network-First con Fallback a Caché (Ideal para un sistema local que cambia datos)
self.addEventListener('fetch', (event) => {
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Si la red responde bien, devolvemos la respuesta de inmediato
        return response;
      })
      .catch(() => {
        // Si no hay red (o el servidor local cayó momentáneamente), busca en la caché
        return caches.match(event.request);
      })
  );
});
