// functions/[[path]].js  — Cloudflare Pages Functions
export async function onRequest({ request, next }) {
  const url = new URL(request.url);
  const host = url.hostname;

  // Map host → mount path trong _public
  const MOUNT = {
    'blog.cachemissed.lol': '/blog',
    'cs.cachemissed.lol': '/coming-soon',
    'comingsoon.cachemissed.lol': '/coming-soon',
    'contact.cachemissed.lol': '/contact',
    // apex dùng root (_public/index.html)
    'cachemissed.lol': '',
  };

  const base = MOUNT[host];

  // Nếu host có mount path
  if (base !== undefined && base !== '') {
    // ĐÃ ở dưới base? -> không đụng nữa
    if (url.pathname === base || url.pathname.startsWith(base + '/')) {
      return next();
    }

    // Chưa ở dưới base -> rewrite vào base (giữ nguyên phần path còn lại)
    const rest = url.pathname === '/' ? '' : url.pathname;
    url.pathname = base + rest;

    // Rewrite nội bộ, KHÔNG 301/302
    return fetch(new Request(url.toString(), request));
  }

  // Các host/route khác: đi tiếp
  return next();
}
