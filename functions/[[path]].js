// functions/[[path]].js
export default {
  async fetch(request) {
    const url  = new URL(request.url);
    const host = url.hostname;

    // Nhóm host
    const BLOG      = new Set(['blog.cachemissed.lol']);
    const COMINGSOON= new Set(['cachemissed.lol','www.cachemissed.lol','comingsoon.cachemissed.lol','cs.cachemissed.lol']);
    const CONTACT   = new Set(['contact.cachemissed.lol']);

    // helper: REWRITE (không đổi URL người dùng, tránh loop)
    const rewrite = (toPath) => {
      const target = new URL(toPath, url.origin);
      target.search = url.search; // giữ query
      return fetch(new Request(target, request));
    };

    if (BLOG.has(host)) {
      // /  -> /blog/
      // /abc -> /blog/abc
      const p = url.pathname;
      const toPath = (p === '/')
        ? '/blog/'
        : (p.startsWith('/blog') ? p : `/blog${p}`);
      return rewrite(toPath);
    }

    if (COMINGSOON.has(host)) {
      return rewrite('/coming-soon/');       // trang Coming Soon
    }

    if (CONTACT.has(host)) {
      return rewrite('/contact/');           // nếu có trang contact
    }

    // fallback: coi như blog
    const p = url.pathname;
    return rewrite(p.startsWith('/blog') ? p : `/blog${p}`);
  }
}
