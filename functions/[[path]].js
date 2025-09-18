export async function onRequest({ request }) {
  const url = new URL(request.url);
  const host = url.hostname.toLowerCase();
  const p = url.pathname;

  // helper: nếu là thư mục, dùng index.html
  const toIndex = (x) => (x.endsWith('/') ? x + 'index.html' : x);

  // BLOG host
  if (host === 'blog.cachemissed.lol' || host.endsWith('.blog.cachemissed.lol')) {
    let internal = p === '/' ? '/blog/index.html'
                  : p === '/blog' ? '/blog/index.html'
                  : toIndex(p);
    const target = new URL(request.url);
    target.pathname = internal;
    return fetch(new Request(target, request));
  }

  // ROOT / COMING-SOON host
  if (
    host === 'cachemissed.lol' ||
    host === 'www.cachemissed.lol' ||
    host === 'cs.cachemissed.lol' ||
    host === 'comingsoon.cachemissed.lol'
  ) {
    let internal = p === '/' ? '/coming-soon/index.html'
                  : p === '/coming-soon' ? '/coming-soon/index.html'
                  : toIndex(p);
    const target = new URL(request.url);
    target.pathname = internal;
    return fetch(new Request(target, request));
  }

  return fetch(request);
}
