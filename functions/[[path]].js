// functions/[[path]].js
export async function onRequest(ctx) {
  try {
    const req = ctx.request;
    const url = new URL(req.url);
    const host = url.hostname.toLowerCase();

    // helper: nếu là thư mục thì thêm index.html
    const toIndex = (p) => (p.endsWith('/') ? p + 'index.html' : p);

    if (host === 'blog.cachemissed.lol') {
      // /  -> /blog/index.html ; còn lại giữ nguyên (nhưng thêm index.html nếu cần)
      url.pathname = (url.pathname === '/' || url.pathname === '/blog')
        ? '/blog/index.html'
        : toIndex(url.pathname);
      return fetch(url.toString(), req);   // rewrite nội bộ, KHÔNG đổi URL hiển thị
    }

    // apex & coming-soon host
    if (
      host === 'cachemissed.lol' ||
      host === 'www.cachemissed.lol' ||
      host === 'comingsoon.cachemissed.lol' ||
      host === 'cs.cachemissed.lol'
    ) {
      url.pathname = (url.pathname === '/' || url.pathname === '/coming-soon')
        ? '/coming-soon/index.html'
        : toIndex(url.pathname);
      return fetch(url.toString(), req);
    }

    // host khác: để mặc định
    return fetch(req);
  } catch (err) {
    // Dập 1019: trả lỗi rõ ràng để debug
    return new Response(
      'Pages Function error:\n' + (err && err.stack ? err.stack : String(err)),
      { status: 500, headers: { 'content-type': 'text/plain; charset=utf-8' } }
    );
  }
}
