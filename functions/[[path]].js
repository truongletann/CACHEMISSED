export async function onRequest(context) {
  const url = new URL(context.request.url);
  const host = url.hostname;

  // BLOG host: serve blog dưới /blog, KHÔNG đẩy về coming-soon
  if (host === "blog.cachemissed.lol") {
    if (url.pathname === "/" || url.pathname === "") {
      return await context.env.ASSETS.fetch(new URL("/blog/index.html", url), context.request);
    }
    return await context.env.ASSETS.fetch(url, context.request);
  }

  // Apex & các host khác: coming-soon
  if (url.pathname === "/" || url.pathname === "") {
    return await context.env.ASSETS.fetch(new URL("/coming-soon/index.html", url), context.request);
  }
  return await context.env.ASSETS.fetch(url, context.request);
}
