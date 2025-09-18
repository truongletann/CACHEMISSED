// functions/[[path]].js
export default {
  async fetch(request, env) {
    const url  = new URL(request.url);
    const host = url.hostname;

    const serve = (path) =>
      env.ASSETS.fetch(new Request(new URL(path, url), request));

    // ===== blog.cachemissed.lol -> phục vụ BLOG ở ROOT =====
    if (host === 'blog.cachemissed.lol') {
      let p = url.pathname;
      if (p.endsWith('/')) p += 'index.html';
      if (p === '/') p = '/index.html';
      return serve(p); // phục vụ từ root artifact
    }

    // ===== apex & các sub comingsoon -> /coming-soon/ =====
    if (
      host === 'cachemissed.lol' ||
      host === 'www.cachemissed.lol' ||
      host === 'comingsoon.cachemissed.lol' || // hoặc cs.cachemissed.lol
      host === 'cs.cachemissed.lol'
    ) {
      let p = url.pathname;
      if (p === '/' || p === '') p = '/index.html';
      if (p.endsWith('/')) p += 'index.html';
      return serve(`/coming-soon${p}`);
    }

    // ===== (tuỳ) contact subdomain -> /contact/ =====
    if (host === 'contact.cachemissed.lol') {
      let p = url.pathname;
      if (p === '/' || p === '') p = '/index.html';
      if (p.endsWith('/')) p += 'index.html';
      return serve(`/contact${p}`);
    }

    // Fallback: trả blog root
    return serve('/index.html');
  },
};
