export async function onRequest({ request }) {
  const url = new URL(request.url);
  const host = url.hostname.toLowerCase();

  // Helper: chuyển / -> /index.html
  const ensureIndex = (p) => (p === '/' ? '/index.html' : p);

  // ---- BLOG host ----
  // Dùng đúng host thật của bạn:
  const isBlogHost =
    host === 'blog.cachemissed.lol' || host.endsWith('.blog.cachemissed.lol');

  if (isBlogHost) {
    // Mọi request ở blog.* không bắt đầu bằng /blog => rewrite nội bộ sang /blog/...
    if (!url.pathname.startsWith('/blog')) {
      url.pathname = '/blog' + ensureIndex(url.pathname);
    } else {
      // /blog/ -> /blog/index.html
      if (url.pathname === '/blog/') url.pathname = '/blog/index.html';
    }
    return fetch(new Request(url.toString(), request));
  }

  // ---- COMING SOON (apex) ----
  // Thêm các alias nếu bạn dùng (vd: cs.cachemissed.lol, comingsoon.cachemissed.lol)
  const isComingSoonHost =
    host === 'cachemissed.lol' ||
    host === 'www.cachemissed.lol' ||
    host === 'cs.cachemissed.lol' ||
    host === 'comingsoon.cachemissed.lol';

  if (isComingSoonHost) {
    if (!url.pathname.startsWith('/coming-soon')) {
      url.pathname = '/coming-soon' + ensureIndex(url.pathname);
    } else {
      if (url.pathname === '/coming-soon/')
        url.pathname = '/coming-soon/index.html';
    }
    return fetch(new Request(url.toString(), request));
  }

  // Mặc định: cứ phục vụ như tĩnh
  return fetch(request);
}
