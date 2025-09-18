// functions/[[path]].js
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const host = url.hostname;

    // NHÓM HOST
    const BLOG_HOSTS    = new Set(['blog.cachemissed.lol']);
    const CS_HOSTS      = new Set(['cachemissed.lol', 'www.cachemissed.lol', 'comingsoon.cachemissed.lol', 'cs.cachemissed.lol']);
    const CONTACT_HOSTS = new Set(['contact.cachemissed.lol']);

    // helper: REWRITE (không đổi URL người dùng nhìn thấy)
    const rewrite = (toPath) => {
      const u = new URL(toPath, url.origin);
      u.search = url.search; // giữ query nếu có
      return fetch(new Request(u, request));
    };

    if (BLOG_HOSTS.has(host)) {
      // Toàn bộ blog.* lấy nội dung từ /blog (không redirect)
      const base = '/blog';
      const p = url.pathname;
      const toPath = (p === '/')
        ? `${base}/`
        : (p.startsWith(base) ? p : `${base}${p}`);
      return rewrite(toPath);
    }

    if (CS_HOSTS.has(host)) {
      // Các host coming-soon & apex: luôn trả /coming-soon/
      return rewrite('/coming-soon/');
    }

    if (CONTACT_HOSTS.has(host)) {
      return rewrite('/contact/');
    }

    // fallback: mặc định coi như blog
    const p = url.pathname;
    return rewrite(p.startsWith('/blog') ? p : `/blog${p}`);
  }
}
