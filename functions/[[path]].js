// functions/[[path]].js
export default {
  async fetch(request, env) {
    const url  = new URL(request.url);
    const host = url.hostname;

    // Helper: phục vụ file tĩnh từ thư mục build (ASSETS) mà KHÔNG tái chạy Functions
    const serve = (path) => {
      const assetURL = new URL(path, url.origin);
      return env.ASSETS.fetch(new Request(assetURL, request));
    };

    // BLOG — host blog.cachemissed.lol -> map vào /blog
    if (host === 'blog.cachemissed.lol') {
      // / -> /blog/index.html ; /abc -> /blog/abc ; /abc/ -> /blog/abc/index.html
      let p = url.pathname === '/' ? '/blog/index.html' : `/blog${url.pathname}`;
      if (p.endsWith('/')) p += 'index.html';
      return serve(p);
    }

    // COMING SOON — apex + các sub tương ứng -> /coming-soon
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

    // CONTACT (nếu có)
    if (host === 'contact.cachemissed.lol') {
      let p = url.pathname === '/' ? '/contact/index.html' : `/contact${url.pathname}`;
      if (p.endsWith('/')) p += 'index.html';
      return serve(p);
    }

    // Mặc định: cho về blog
    return serve('/blog/index.html');
  }
}
