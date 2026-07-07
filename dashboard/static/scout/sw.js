// Service worker do Hunter Scout — cacheia só o shell do app (HTML/manifest/ícone)
// para abrir rápido e sobreviver a sinal ruim em campo. As chamadas de API
// (/scout/api/*) NUNCA são cacheadas — avaliação sempre precisa de rede.
const CACHE = 'hunter-scout-v1';
const SHELL = ['/scout', '/static/scout/manifest.json', '/static/scout/icon.svg'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/scout/api/')) return; // sempre rede, nunca cache

  event.respondWith(
    caches.match(event.request).then((cached) => {
      const network = fetch(event.request)
        .then((resp) => {
          if (resp.ok) caches.open(CACHE).then((c) => c.put(event.request, resp.clone()));
          return resp;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
