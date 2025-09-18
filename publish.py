#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Static publisher for a dual-host site:
- Blog at /blog/ (with header/footer hard-coded here)
- Coming Soon at /coming-soon/ (copied as-is from your existing code)
- Host router at / (index.html) to switch by hostname
- Also builds posts, category pages, feed.xml, sitemap.xml, index.json

ENV VARS (optional but recommended):
  BASE_URL=/                      # or /repo/ for GitHub project pages
  SITE_URL=https://cachemissed.lol
  BRAND="CacheMissed Blog"
  APEX_HOST=cachemissed.lol
  BLOG_HOST=blog.cachemissed.lol
  COMING_SOON_SRC=coming_soon     # source folder that contains your coming soon code
"""

import os, re, shutil, datetime, json
from pathlib import Path
from urllib.parse import urljoin
import frontmatter, markdown
from slugify import slugify
from jinja2 import Template

# ---------- Paths & Config ----------
ROOT = Path(__file__).resolve().parent

POSTS     = ROOT / "posts"
IMAGES    = ROOT / "images"
TEMPL     = ROOT / "templates"          # index_body.html, post_body.html, category_body.html
ASSETS    = ROOT / "assets"             # assets/css/*, assets/js/*
COMING_SRC= ROOT / os.environ.get("COMING_SOON_SRC", "coming_soon")

SITE      = ROOT / "site"
OUT_POSTS = SITE / "posts"
CAT_DIR   = SITE / "category"
BLOG_DIR  = SITE / "blog"
COMING_DIR= SITE / "coming-soon"

BASE_URL  = os.environ.get("BASE_URL", "/").rstrip("/") + "/"
SITE_URL  = os.environ.get("SITE_URL", "").rstrip("/")          # absolute base for canonical/RSS
BRAND     = os.environ.get("BRAND", "CacheMissed Blog")
APEX_HOST = os.environ.get("APEX_HOST", "cachemissed.lol")
BLOG_HOST = os.environ.get("BLOG_HOST", "blog.cachemissed.lol")

YEAR = datetime.date.today().year

for d in [SITE, OUT_POSTS, CAT_DIR, BLOG_DIR, COMING_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ---------- Utils ----------
def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def write_text(p: Path, txt: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(txt, encoding="utf-8")

def ensure_assets():
    # copy assets/css -> site/css ; assets/js -> site/js
    for sub in ("css", "js"):
        src = ASSETS / sub
        if not src.exists(): continue
        dst = SITE / sub
        for f in src.rglob("*"):
            if f.is_file():
                out = dst / f.relative_to(src)
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, out)

def copy_images():
    if not IMAGES.exists(): return
    dst = SITE / "images"
    for p in IMAGES.rglob("*"):
        if p.is_file():
            out = dst / p.relative_to(IMAGES)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out)

def parse_date(meta_date, name_hint):
    if meta_date:
        return datetime.date.fromisoformat(str(meta_date)[:10])
    m = re.search(r"(\d{4})[-_](\d{2})[-_](\d{2})", name_hint)
    if m:
        y, mo, d = map(int, m.groups())
        return datetime.date(y, mo, d)
    return datetime.date.today()

def human(d): return d.strftime("%Y %b %d")

def collect_categories(meta):
    cats=[]
    if meta.get("category"): cats.append(str(meta["category"]))
    if meta.get("categories"):
        c = meta["categories"]
        cats += ([c] if isinstance(c, str) else list(c))
    return [x.strip() for x in cats if str(x).strip()]


# ---------- Header / Footer (hard-coded) ----------
def header_html(base: str, crumb_title: str | None = None) -> str:
    doc_svg = """<svg class="docico" viewBox="0 0 24 24" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M14 2v6h6" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>"""
    crumb = f'<span class="brand-path"> <span class="sep">/</span> {doc_svg}<span class="crumb-txt">{crumb_title}</span></span>' if crumb_title else ""
    return f"""
<header class="site-head">
  <div class="head-inner">
    <a class="brand" href="{base}">
      <img class="logo logo-light" src="{BASE_URL}images/logo-light.png" alt="logo">
      <img class="logo logo-dark"  src="{BASE_URL}images/logo-dark.png"  alt="logo">
      <span class="txt">{BRAND}</span>
    </a>
    {crumb}
    <div class="spacer"></div>
    <label class="search" role="search" aria-label="Search site">
      <input id="q" placeholder="Search posts…" autocomplete="off">
      <button type="button" class="s-clear" id="qClear" aria-label="Clear">✕</button>
      <button type="button" class="s-ico-btn" id="qIcon" aria-label="Search">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
             stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="11" cy="11" r="7"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
      </button>
    </label>
    <button class="theme" id="themeToggle" type="button" aria-pressed="false" title="Toggle theme">
      <span class="label label-dark">DARK</span>
      <span class="track"><span class="knob"></span></span>
      <span class="label label-light">LIGHT</span>
    </button>
  </div>
</header>
"""

def footer_html() -> str:
    return f"""
<footer class="site-footer" role="contentinfo">
  <div class="inner">© {YEAR} CacheMissed</div>
</footer>"""

# ---------- Page shell (wrap body template) ----------
from jinja2 import Template  # đảm bảo còn import này ở đầu file

SHELL = Template("""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }}</title>
<link rel="canonical" href="{{ canonical }}">
<link rel="stylesheet" href="{{ base }}css/base.css">
{% for href in page_css %}<link rel="stylesheet" href="{{ base }}css/{{ href }}">{% endfor %}
</head><body class="{{ body_class }}">
{{ header | safe }}
{{ body | safe }}
{{ footer | safe }}
<script src="{{ base }}js/common.js"></script>
{% for src in page_js %}<script src="{{ base }}js/{{ src }}"></script>{% endfor %}
</body></html>""")

def render_shell(*, title:str, canonical:str, body_class:str, base:str,
                 header:str, body:str, page_css:list[str], page_js:list[str]) -> str:
    return SHELL.render(
        title=title, canonical=canonical or "",
        base=base, header=header, body=body, footer=footer_html(),
        body_class=body_class, page_css=page_css, page_js=page_js,
    )



# ---------- Build: posts / categories ----------
def render_post(md_path: Path, slug_hint: str, entries: list, cats_map: dict):
    fm = frontmatter.load(md_path)
    html_md = markdown.markdown(fm.content, extensions=["extra","toc","tables","codehilite"])
    title = fm.get("title") or md_path.stem.replace("-"," ").title()
    d = parse_date(fm.get("date"), md_path.as_posix())
    date_human = human(d)
    slug = fm.get("slug") or slugify(slug_hint or title)
    out = OUT_POSTS / f"{slug}.html"
    out.parent.mkdir(parents=True, exist_ok=True)

    cats = collect_categories(fm.metadata)
    main_cat = cats[0] if cats else None

    rel_url = f"/posts/{out.name}"
    abs_url = (SITE_URL + rel_url) if SITE_URL else None
    page_url = abs_url or (BASE_URL + "posts/" + out.name)

    body_tpl = Template(read_text(TEMPL / "post_body.html"))
    body_html = body_tpl.render(
        title=title, date_human=date_human, category=main_cat, content=html_md, base=BASE_URL
    )

    page_html = render_shell(
        title=title,
        canonical=abs_url or urljoin(BASE_URL, f"posts/{out.name}"),
        body_class="no-search",
        base=BASE_URL,
        header=header_html(BASE_URL + "blog/", crumb_title=title),  # brand → /blog/
        body=body_html,
        page_css=["post.css"],
        page_js=["post.js"],
    )
    write_text(out, page_html)

    entries.append({"title": title, "date": d, "date_human": date_human,
                    "url": page_url, "categories": cats})
    for c in cats:
        cats_map.setdefault(c, []).append({"title": title, "date": d, "date_human": date_human, "url": page_url})


def build_index(entries, pills):
    body_tpl = Template(read_text(TEMPL / "index_body.html"))
    body = body_tpl.render(posts=entries, pills=pills, base=BASE_URL)
    html = render_shell(
        title=BRAND,
        canonical=(SITE_URL or "").rstrip("/") + "/blog/" if SITE_URL else BASE_URL + "blog/",
        body_class="page-index",
        base=BASE_URL,
        header=header_html(BASE_URL + "blog/"),
        body=body,
        page_css=["index.css"],
        page_js=["index.js"],
    )
    write_text(BLOG_DIR / "index.html", html)


def build_category(cat_name, posts, pills):
    body_tpl = Template(read_text(TEMPL / "category_body.html"))
    current_cat_href = f"{BASE_URL}category/{slugify(cat_name)}.html"
    body = body_tpl.render(posts=posts, pills=pills, base=BASE_URL,
                           current_cat_href=current_cat_href)

    html = render_shell(
        title=f"{cat_name} · {BRAND}",
        canonical=(SITE_URL + f"/category/{slugify(cat_name)}.html") if SITE_URL
                  else f"{BASE_URL}category/{slugify(cat_name)}.html",
        body_class="page-index page-category",      # dùng lại toàn bộ style của index
        base=BASE_URL,
        header=header_html(BASE_URL + "blog/"),
        body=body,
        page_css=["index.css"],                     # index.css là chính
        page_js=["index.js"],
    )
    (CAT_DIR / f"{slugify(cat_name)}.html").write_text(html, encoding="utf-8")

# ---------- Coming Soon (copy as-is to /coming-soon/) ----------
def build_coming_soon():
    if not COMING_SRC.exists():
        print(f"[coming-soon] Source not found: {COMING_SRC}")
        return
    # copy everything preserving structure
    for p in COMING_SRC.rglob("*"):
        if p.is_file():
            out = COMING_DIR / p.relative_to(COMING_SRC)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out)
    # if there's no index.html inside source root, try to locate one and place as index
    if not (COMING_DIR / "index.html").exists():
        # find an html file to become index
        candidates = list(COMING_DIR.rglob("*.html"))
        if candidates:
            shutil.copy2(candidates[0], COMING_DIR / "index.html")
    print(f"[coming-soon] Copied → {COMING_DIR}")


# ---------- Router at / (index.html) ----------
def build_host_router():
    router = f"""<!doctype html><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Loading…</title>
<script>
(function(){{
  var h = (location.hostname || "").toLowerCase();
  var apex = "{APEX_HOST}".toLowerCase();
  var blog = "{BLOG_HOST}".toLowerCase();
  if (h === blog) {{
    location.replace("{BASE_URL}blog/");
  }} else if (h === apex) {{
    location.replace("{BASE_URL}coming-soon/");
  }} else {{
    location.replace("{BASE_URL}blog/");
  }}
}})();
</script>
<noscript>
  <meta http-equiv="refresh" content="0; url={BASE_URL}blog/">
</noscript>
"""
    write_text(SITE / "index.html", router)


# ---------- Feed, sitemap, index.json ----------
def build_rss_and_maps(entries, cats_map):
    # RSS
    items=[]
    home_link = SITE_URL or BASE_URL
    for e in entries[:50]:
        link = e['url'] if e['url'].startswith('http') else (
            (SITE_URL + e['url']) if SITE_URL and e['url'].startswith('/') else e['url']
        )
        items.append(f"""<item>
  <title><![CDATA[{e['title']}]]></title>
  <link>{link}</link>
  <guid isPermaLink="false">{link}</guid>
  <pubDate>{e['date'].strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate>
</item>""")
    feed=f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>{BRAND}</title><link>{home_link}</link><description>RSS</description>
{''.join(items)}
</channel></rss>"""
    write_text(SITE / "feed.xml", feed.strip())

    # sitemap
    urls=[]
    urls.append((SITE_URL or "").rstrip("/") + "/") if SITE_URL else urls.append(BASE_URL)
    # blog home
    urls.append((SITE_URL + "/blog/") if SITE_URL else (BASE_URL + "blog/"))
    # coming soon home
    urls.append((SITE_URL + "/coming-soon/") if SITE_URL else (BASE_URL + "coming-soon/"))
    # posts
    for e in entries:
        if e["url"].startswith("http"): urls.append(e["url"])
        elif SITE_URL and e["url"].startswith("/"): urls.append(SITE_URL + e["url"])
        else: urls.append(e["url"])
    # categories
    for c in cats_map.keys():
        urls.append((SITE_URL + f"/category/{slugify(c)}.html") if SITE_URL
                    else f"{BASE_URL}category/{slugify(c)}.html")

    sm=["<?xml version='1.0' encoding='UTF-8'?>","<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"]
    for u in urls: sm.append(f"<url><loc>{u}</loc></url>")
    sm.append("</urlset>")
    write_text(SITE / "sitemap.xml", "\n".join(sm))

    # index.json
    data = [{"title":e["title"],"date":e["date"].isoformat(),"url":e["url"],"categories":e["categories"]}
            for e in entries]
    write_text(SITE / "index.json", json.dumps(data, ensure_ascii=False, indent=2))


# ---------- Main ----------
def build_all():
    ensure_assets()
    copy_images()

    entries=[]; cats_map={}

    # scan posts
    if POSTS.exists():
        for p in POSTS.rglob("*"):
            if p.is_file() and p.suffix.lower()==".md":
                render_post(p, p.stem, entries, cats_map)
            elif p.is_dir() and (p/"index.md").exists():
                render_post(p/"index.md", p.name, entries, cats_map)

    entries.sort(key=lambda x:x["date"], reverse=True)

    unique_cats = sorted({c for e in entries for c in e["categories"]}) if entries else []
    pills = [{"href": f"{BASE_URL}category/{slugify(c)}.html", "label": c} for c in unique_cats]

    build_index(entries, pills)
    for cat, posts in cats_map.items():
        posts.sort(key=lambda x:x["date"], reverse=True)
        build_category(cat, posts, pills)

    build_coming_soon()
    build_host_router()
    build_rss_and_maps(entries, cats_map)

    print(f"Built {len(entries)} post(s), {len(cats_map)} category page(s) → {SITE}")


if __name__ == "__main__":
    build_all()
