export default {
  async fetch(request, env) {
    const url  = new URL(request.url);
    const host = url.hostname;

    const serve = (path) =>
      env.ASSETS.fetch(new Request(new URL(path, url), request));

    // ===== blog.cachemissed.lol -> phục vụ nội dung trong /blog =====
    if (host === 'blog.cachemissed.lol') {
      let p = url.pathname;
      if (p === '/' || p === '') p = '/index.html';
      if (p.endsWith('/')) p += 'index.html';
      return serve(`/blog${p}`);   // <— quan trọng: prepend /blog
    }

    // ===== apex & coming soon subdomain -> /coming-soon =====
    if (
      host === 'cachemissed.lol' ||
      host === 'www.cachemissed.lol' ||
      host === 'comingsoon.cachemissed.lol' ||
      host === 'cs.cachemissed.lol'
    ) {
      let p = url.pathname;
      if (p === '/' || p === '') p = '/index.html';
      if (p.endsWith('/')) p += 'index.html';
      return serve(`/coming-soon${p}`);
    }

    // ===== (tuỳ) contact subdomain -> /contact =====
    if (host === 'contact.cachemissed.lol') {
      let p = url.pathname;
      if (p === '/' || p === '') p = '/index.html';
      if (p.endsWith('/')) p += 'index.html';
      return serve(`/contact${p}`);
    }

    // Fallback: trả blog trang chủ
    return serve('/blog/index.html');
  },
};
