// Route theo hostname → subpath trong cùng 1 build
export async function onRequest(context) {
  const url = new URL(context.request.url);
  const host = url.hostname.toLowerCase();

  if (host.startsWith('blog.')) {
    url.pathname = '/blog' + (url.pathname === '/' ? '/' : url.pathname);
  } else if (host.startsWith('comingsoon.') || host.startsWith('coming-soon.')) {
    url.pathname = '/coming-soon' + (url.pathname === '/' ? '/' : url.pathname);
  } else if (host.startsWith('contact.')) {
    url.pathname = '/contact' + (url.pathname === '/' ? '/' : url.pathname);
  } else {
    // Apex: cachemissed.lol → Coming Soon (đổi nếu muốn)
    url.pathname = '/coming-soon' + (url.pathname === '/' ? '/' : url.pathname);
  }

  // Rewrite nội bộ (không đổi URL, tốt cho SEO)
  return context.next({ request: new Request(url, context.request) });
}
