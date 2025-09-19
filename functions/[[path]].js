// functions/[[path]].js
export async function onRequest(context) {
  try {
    const { request, next, env } = context;
    const url = new URL(request.url);
    const host = url.hostname.toLowerCase();
    let path = url.pathname;

    // Helper: phục vụ file tĩnh trong Pages.
    // Trên Pages mới, env.ASSETS có thể không tồn tại -> fallback sang fetch().
    const serve = (assetPath) => {
      // Chuẩn hoá: thêm index.html nếu kết thúc bởi "/"
      const finalPath =
        assetPath.endsWith('/') ? `${assetPath}index.html` : assetPath;

      const req = new Request(new URL(finalPath, url), request);
      return env && env.ASSETS ? env.ASSETS.fetch(req) : fetch(req);
    };

    // ==========================
    // blog.cachemissed.lol  -> map /blog/* ra gốc
    // ==========================
    if (host === 'blog.cachemissed.lol') {
      // Nếu truy cập gốc -> trả blog/index.html (không redirect để khỏi lộ /blog)
      if (path === '/' || path === '/index.html') {
        return serve('/blog/index.html');
      }

      // Nếu người dùng gõ một path bất kỳ KHÔNG nằm dưới /blog
      // -> rewrite sang /blog/<path>
      if (!path.startsWith('/blog/')) {
        return serve(`/blog${path}`);
      }

      // Đã là /blog/* rồi thì cứ để engine tĩnh xử lý
      return next();
    }

    // ==========================
    // cachemissed.lol -> map /coming-soon/* ra gốc
    // ==========================
    if (host === 'cachemissed.lol') {
      if (path === '/' || path === '/index.html') {
        return serve('/coming-soon/index.html');
      }
      if (!path.startsWith('/coming-soon/')) {
        return serve(`/coming-soon${path}`);
      }
      return next();
    }

    // Các host khác: trả tĩnh mặc định
    return next();
  } catch (err) {
    // Có lỗi thì rơi về file tĩnh mặc định thay vì 1019
    return context.next();
  }
}
