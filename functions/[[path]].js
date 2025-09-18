export default {
  async fetch(request, env) {
    const url  = new URL(request.url);
    const host = url.hostname;

    const serve = (path) => env.ASSETS.fetch(new Request(new URL(path, url), request));

    // blog.cachemissed.lol -> phục vụ ROOT (blog)
    if (host === 'blog.cachemissed.lol') {
      // giữ nguyên path, nhưng map về root
      let p = url.pathname === '/' ? '/index.html' : url.pathname;
      if (p.endsWith('/')) p += 'index.html';
      return serve(p);
    }

    // apex + comingsoon sub -> coming-soon/
    if (
      host === 'cachemissed.lol' ||
      host === 'www.cachemissed.lol' ||
      host === 'comingsoon.cachemissed.lol' ||
      host === 'cs.cachemissed.lol'
    ) {
      let p = url.pathname === '/' ? '/coming-soon/index.html' : `/coming-soon${url.pathname}`;
      if (p.endsWith('/')) p += 'index.html';
      return serve(p);
    }

    // (tuỳ) contact sub
    if (host === 'contact.cachemissed.lol') {
      let p = url.pathname === '/' ? '/contact/index.html' : `/contact${url.pathname}`;
      if (p.endsWith('/')) p += 'index.html';
      return serve(p);
    }

    // mặc định về blog root
    return serve('/index.html');
  }
}
