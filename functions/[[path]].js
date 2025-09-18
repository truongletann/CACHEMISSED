export async function onRequest({ request }) {
  const url = new URL(request.url);
  const host = url.hostname.toLowerCase();
  const pathname = url.pathname;

  // Helper trả về nội bộ /index.html cho thư mục
  const toIndex = (p) => (p.endsWith('/') ? p + 'index.html' : p);

  // --- BLOG host: chỉ rewrite "/" -> "/blog/index.html". Không tự thêm /blog vào URL ---
  const isBlogHost =
    host === 'blog.cachemissed.lol' || host.endsWith('.blog.cachemissed.lol');

  if (isBlogHost) {
    let internalPath = pathname;
    if (pathname === '/') {
      internalPath = '/blog/index.html';
    } else if (pathname === '/blog') {
      internalPath = '/blog/index.html';
    } else {
      internalPath = toIndex(pathname);
    }
    const target = new URL(request.url);
    target.pathname = internalPath;
    return fetch(new Request(target, request));
  }

  // --- ROOT / COMING SOON host: chỉ rewrite "/" -> "/coming-soon/index.html" ---
  const isComingHost =
    host === 'cachemissed.lol' ||
    host === 'www.cachemissed.lol' ||
    host === 'cs.cachemissed.lol' ||
    host === 'comingsoon.cachemissed.lol';

  if (isComingHost) {
    let internalPath = pathname;
    if (pathname === '/') {
      internalPath = '/coming-soon/index.html';
    } else if (pathname === '/coming-soon') {
      internalPath = '/coming-soon/index.html';
    } else {
      internalPath = toIndex(pathname);
    }
    const target = new URL(request.url);
    target.pathname = internalPath;
    return fetch(new Request(target, request));
  }

  return fetch(request);
}
