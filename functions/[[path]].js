// functions/[[path]].js
export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);

  // 1) Ánh xạ host -> thư mục trong _public
  const host = url.hostname.toLowerCase();
  let base = "/blog/"; // mặc định

  if (host === "cachemissed.lol" || host === "www.cachemissed.lol") {
    base = "/coming-soon/";
  } else if (host === "blog.cachemissed.lol") {
    base = "/blog/";
  } else if (host === "cs.cachemissed.lol") {
    base = "/coming-soon/";
  } else if (host === "contact.cachemissed.lol") {
    base = "/contact/";
  }

  // 2) Ghép lại đường dẫn tĩnh cần lấy trong _public
  //    - giữ nguyên phần path sau domain
  //    - nếu / thì trả index.html
  let subPath = url.pathname.replace(/^\/+/, ""); // bỏ dấu / đầu
  let pathname = base + subPath;
  if (pathname.endsWith("/")) pathname += "index.html";
  if (base && (url.pathname === "" || url.pathname === "/")) pathname = base + "index.html";

  // 3) Fetch từ binding ASSETS của Pages
  try {
    const assetURL = new URL(request.url);
    assetURL.pathname = pathname;

    // Bảo toàn method/headers/body của request gốc
    const newReq = new Request(assetURL.toString(), request);
    let res = await env.ASSETS.fetch(newReq);

    // 404 -> thử fallback index.html của base (SPA hoặc thư mục thiếu index)
    if (res.status === 404) {
      assetURL.pathname = base + "index.html";
      res = await env.ASSETS.fetch(new Request(assetURL.toString(), request));
    }
    return res;
  } catch (err) {
    // Nếu lỗi (gây 1101), trả text để không văng Worker
    return new Response(
      "Functions error:\n" + (err && err.stack ? err.stack : String(err)),
      { status: 500, headers: { "Content-Type": "text/plain" } }
    );
  }
}
