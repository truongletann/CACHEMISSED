export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const host = url.hostname;

    // Map host -> thư mục con trong _public
    const map = {
      'blog.cachemissed.lol': '/blog',
      'cachemissed.lol': '/coming-soon',
      'www.cachemissed.lol': '/coming-soon',
      'comingsoon.cachemissed.lol': '/coming-soon',
      'cs.cachemissed.lol': '/coming-soon',
      'contact.cachemissed.lol': '/contact',
    };

    // Mặc định (host lạ): cho về blog
    const base = map[host] ?? '/blog';

    // Chuẩn hóa đường dẫn
    let p = url.pathname;
    if (p === '' || p === '/') p = '/index.html';
    if (p.endsWith('/')) p += 'index.html';

    // Đường dẫn asset thực sự trong _public
    const assetPath = `${base}${p}`;

    // Trả đúng file
    const res = await env.ASSETS.fetch(
      new Request(new URL(assetPath, url), request)
    );

    // Nếu lỡ không có file (404) thì trả trang index của section
    if (res.status === 404) {
      return env.ASSETS.fetch(
        new Request(new URL(`${base}/index.html`, url), request)
      );
    }
    return res;
  },
};
