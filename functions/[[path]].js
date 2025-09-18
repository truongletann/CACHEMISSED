// functions/[[path]].js
// Cloudflare Pages Functions — Normalizer/Router

const BLOG_HOSTS = ['blog.cachemissed.lol'];               // blog subdomain
const COMING_HOSTS = ['cs.cachemissed.lol', 'comingsoon.cachemissed.lol']; // nếu bạn dùng subdomain cho Coming Soon
const APEX_HOST = 'cachemissed.lol';                       // domain gốc

export async function onRequest(context) {
  const req = context.request;
  const url = new URL(req.url);
  const host = url.hostname;
  const path = url.pathname;

  // --- 1) Blog subdomain: loại bỏ tiền tố /blog để tránh /blog/blog/ ---
  if (BLOG_HOSTS.includes(host)) {
    // Nếu URL đang là /blog hoặc bắt đầu bằng /blog/... => bóc /blog và 301
    if (path === '/blog' || path.startsWith('/blog/')) {
      url.pathname = path.replace(/^\/blog(\/|$)/, '/');
      // Bảo toàn query-string
      return Response.redirect(url.toString(), 301);
    }
    // Không động vào những request hợp lệ khác của blog
    return context.next();
  }

  // --- 2) Apex: chỉ route trang chủ "/" sang /coming-soon/ để tránh reload loop ---
  if (host === APEX_HOST) {
    if (path === '/' || path === '') {
      url.pathname = '/coming-soon/';
      return fetch(new Request(url.toString(), req));
    }
    return context.next();
  }

  // --- 3) (Tuỳ chọn) Subdomain Coming Soon: trang chủ -> /coming-soon/ ---
  if (COMING_HOSTS.includes(host)) {
    if (path === '/' || path === '') {
      url.pathname = '/coming-soon/';
      return fetch(new Request(url.toString(), req));
    }
    return context.next();
  }

  // --- Mặc định: để Pages tự trả asset tĩnh ---
  return context.next();
}
