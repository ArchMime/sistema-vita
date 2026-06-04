// app/static/sw.js
const CACHE_NAME = 'vita-cache-v2'; // Incrementado a v2 para forzar la actualización en los clientes

// Recursos críticos unificados para garantizar un inicio offline impecable
const ASSETS_TO_CACHE = [
  '/',
  '/tutorial',
  '/static/manifest.json',
  '/static/css/estilos_panel.css',
  '/static/css/tutorial.css',
  '/static/assets/icons/icon-192.png',
  '/static/assets/icons/icon-512.png'
];

// Evento de instalación: Asegura el almacenamiento de los estilos y vistas base
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS_TO_CACHE))
      .then(() => self.skipWaiting())
  );
});

// Evento de activación: Purga de forma segura estructuras obsoletas en memoria
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

// Estrategia Network-First selectiva (Exclusiva para consultas de lectura GET)
self.addEventListener('fetch', (event) => {
  // CORRECCIÓN CRÍTICA: No interceptar peticiones de escritura (POST, PUT, DELETE) ni recursos externos
  if (event.request.method !== 'GET' || !event.request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Opcional: Podrías clonar y actualizar la caché dinámicamente aquí si fuera necesario
        return response;
      })
      .catch(() => {
        // Respaldo inmediato si el servidor local del negocio no responde
        return caches.match(event.request);
      })
  );
});
