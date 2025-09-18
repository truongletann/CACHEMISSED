// functions/[[path]].js
export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const host = (request.headers.get("host") || "").toLowerCase();

  // Helper: rewrite nội bộ tới 1 path trong _public (ASSETS) mà không redirect
  const rewriteTo = (pathname) => {
    const u = new URL(request.url);
    u.pathname = pathname;
    // Giữ nguyên phương thức/headers… khi gọi ASSETS
    return env.ASSETS.fetch(new Request(u.toString(), request));
  };

  // Trả thẳng asset theo path hiện tại (mặc định)
  const passThrough = () => env.ASSETS.fetch(request);

  // --- Routing theo hostname ---
  // 1) Apex domain -> show Coming Soon (thư mục _public/coming-soon/)
  if (host === "cachemissed.lol" || host === "www.cachemissed.lol") {
    // / -> /coming-soon/ (rewrite nội bộ – KHÔNG redirect)
    if (url.pathname === "/" || url.pathname === "/index.html") {
      return rewriteTo("/coming-soon/");
    }
    // Cho phép truy cập trực tiếp các asset của coming-soon
    if (url.pathname.startsWith("/coming-soon/")) {
      return passThrough();
    }
    // Các trang khác (favicon, robots …) cứ để ASSETS xử lý
    return passThrough();
  }

  // 2) blog.* -> phục vụ từ thư mục /blog
  if (host.startsWith("blog.")) {
    // Map /... trên subdomain về /blog/...
    if (url.pathname === "/") return rewriteTo("/blog/");
    // Nếu chưa có prefix /blog, thêm vào
    if (!url.pathname.startsWith("/blog/")) {
      return rewriteTo("/blog" + (url.pathname.startsWith("/") ? "" : "/") + url.pathname);
    }
    return passThrough();
  }

  // 3) comingsoon.* -> phục vụ từ thư mục /coming-soon
  if (host.startsWith("comingsoon.")) {
    if (url.pathname === "/") return rewriteTo("/coming-soon/");
    if (!url.pathname.startsWith("/coming-soon/")) {
      return rewriteTo("/coming-soon" + (url.pathname.startsWith("/") ? "" : "/") + url.pathname);
    }
    return passThrough();
  }

  // 4) contact.* -> phục vụ từ thư mục /contact (nếu bạn có)
  if (host.startsWith("contact.")) {
    if (url.pathname === "/") return rewriteTo("/contact/");
    if (!url.pathname.startsWith("/contact/")) {
      return rewriteTo("/contact" + (url.pathname.startsWith("/") ? "" : "/") + url.pathname);
    }
    return passThrough();
  }

  // Mặc định: trả asset bình thường
  return passThrough();
}
