const ROOT = "cachemissed.lol";
const BLOG = `blog.${ROOT}`;
const CS   = `cs.${ROOT}`;                // << host mới
const OLD  = `comingsoon.${ROOT}`;        // << host cũ (để 301 về host mới)
const CONTACT = `contact.${ROOT}`;

function rewrite(env, request, pathname) {
  const u = new URL(request.url);
  u.pathname = pathname;
  return env.ASSETS.fetch(new Request(u.toString(), request));
}
function passthrough(env, request) { return env.ASSETS.fetch(request); }

export async function onRequest({ request, env }) {
  const url  = new URL(request.url);
  const host = url.host.toLowerCase();
  const path = url.pathname;

  // Apex -> Coming Soon
  if (host === ROOT || host === `www.${ROOT}`) {
    if (path === "/" || path === "/index.html") return rewrite(env, request, "/coming-soon/");
    return passthrough(env, request);
  }

  // Blog
  if (host === BLOG) {
    if (path === "/" || path === "/index.html") return rewrite(env, request, "/blog/");
    if (!path.startsWith("/blog/")) return rewrite(env, request, "/blog" + (path.startsWith("/") ? "" : "/") + path);
    return passthrough(env, request);
  }

  // NEW: cs.cachemissed.lol -> /coming-soon/*
  if (host === CS) {
    if (path === "/" || path === "/index.html") return rewrite(env, request, "/coming-soon/");
    if (!path.startsWith("/coming-soon/")) return rewrite(env, request, "/coming-soon" + (path.startsWith("/") ? "" : "/") + path);
    return passthrough(env, request);
  }

  // 301 migrate: comingsoon.cachemissed.lol -> cs.cachemissed.lol
  if (host === OLD) {
    url.host = CS;                      // đổi host sang cs.cachemissed.lol
    return new Response(null, { status: 301, headers: { Location: url.toString() } });
  }

  // Contact (nếu có)
  if (host === CONTACT) {
    if (path === "/" || path === "/index.html") return rewrite(env, request, "/contact/");
    if (!path.startsWith("/contact/")) return rewrite(env, request, "/contact" + (path.startsWith("/") ? "" : "/") + path);
    return passthrough(env, request);
  }

  return passthrough(env, request);
}
