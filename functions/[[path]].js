export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);

  // Chuẩn hoá host (bỏ www.)
  const host = url.hostname.replace(/^www\./i, "");
  const path = url.pathname;

  // Helper: fetch file từ output (_public) theo 1 đường dẫn tuyệt đối
  async function serveAsset(absPath) {
    // luôn dùng đường dẫn tuyệt đối bắt đầu bằng "/"
    const target = new URL(absPath, url);
    return env.ASSETS.fetch(target);
  }

  // 1) BLOG — host: blog.cachemissed.lol
  if (host === "blog.cachemissed.lol") {
    // /  ->  /blog/index.html
    if (path === "/") return serveAsset("/blog/index.html");

    // Nếu đã ở trong /blog/... thì cho tĩnh xử lý
    if (path.startsWith("/blog/")) return next();

    // Các đường dẫn khách (ví dụ /posts/abc.html) ta rewrite sang /blog/<path>
    // Nếu kết thúc "/", thêm index.html
    const p = path.endsWith("/") ? `${path}index.html` : path;
    return serveAsset(`/blog${p}`);
  }

  // 2) COMING SOON SUBDOMAIN — (tuỳ chọn)
  if (host === "cs.cachemissed.lol" || host === "comingsoon.cachemissed.lol") {
    // / -> /coming-soon/index.html
    if (path === "/") return serveAsset("/coming-soon/index.html");
    // Nếu đã ở /coming-soon/... thì để tĩnh xử lý
    if (path.startsWith("/coming-soon/")) return next();
    // Các đường dẫn khác: rewrite vào /coming-soon
    const p = path.endsWith("/") ? `${path}index.html` : path;
    return serveAsset(`/coming-soon${p}`);
  }

  // 3) APEX — cachemissed.lol  => làm trang Coming Soon
  if (host === "cachemissed.lol") {
    if (path === "/") return serveAsset("/coming-soon/index.html");
    if (path.startsWith("/coming-soon/")) return next();
    // Các đường dẫn khác rewrite vào coming-soon (không redirect để tránh loop client)
    const p = path.endsWith("/") ? `${path}index.html` : path;
    return serveAsset(`/coming-soon${p}`);
  }

  // 4) Mặc định: để Pages tự phục vụ (nếu còn host khác)
  return next();
}
