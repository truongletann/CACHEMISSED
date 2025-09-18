// functions/[[path]].js
// Router cho Cloudflare Pages

const BLOG_HOSTS   = ['blog.cachemissed.lol'];                 // subdomain blog
const APEX_HOST    = 'cachemissed.lol';                        // domain gốc (trang coming soon)
const COMING_HOSTS = ['cs.cachemissed.lol', 'comingsoon.cachemissed.lol']; // nếu bạn dùng subdomain coming soon

export async function onRequest(context) {
  const req = context.request;
  const url = new URL(req.url);
  const host = url.hostname;
  const path = url.pathname;

  // === BLOG SUBDOMAIN ===
  if (BLOG_HOSTS.includes(host)) {
    // 1) Nếu lỡ vào /blog hoặc /blog/... -> bóc /blog và 301 về URL sạch
    if (path === '/blog' || path.startsWith('/blog/')) {
      url.pathname = path.replace(/^\/blog(\/|$)/, '/');
      return Response.redirect(url.toString(), 301);
    }

    // 2) Map nội bộ mọi đường dẫn của blog tới /blog/... trong asset tĩnh
    //    - "/"  -> "/blog/index.html"
    //    - "/feed.xml" -> "/blog/feed.xml"
    //    - "/category/abc.html" -> "/blog/category/abc.html", v.v.
    const mapped = path === '/' || path === ''
      ? '/blog/index.html'
      : `/blog${path.endsWith('/') ? `${path}index.html` : path}`;

    const mappedURL = new URL(mapped, url);
    return fetch(new Request(mappedURL.toString(), req));
  }

  // === APEX: chỉ route TRANG CHỦ sang coming-soon để tránh loop ===
  if (host === APEX_HOST) {
    if (path === '/' || path === '') {
      url.pathname = '/coming-soon/';
      return fetch(new Request(url.toString(), req));
    }
    return context.next();
  }

  // === (Tuỳ chọn) Subdomain Coming Soon: trang chủ -> /coming-soon/ ===
  if (COMING_HOSTS.includes(host)) {
    if (path === '/' || path === '') {
      url.pathname = '/coming-soon/';
      return fetch(new Request(url.toString(), req));
    }
    return context.next();
  }

  // Mặc định: để Pages tự phục vụ asset
  return context.next();
}
