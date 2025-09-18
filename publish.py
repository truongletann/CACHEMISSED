#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, re, json, shutil, datetime
from pathlib import Path
from urllib.parse import urljoin
import frontmatter, markdown
from slugify import slugify
import os, pathlib

# Ghi thẳng ra ./site (sau đó workflow sẽ copy -> _public/blog)
OUTPUT_DIR = pathlib.Path("site")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ================== CẤU HÌNH ĐẦU RA ==================
ROOT       = Path(__file__).resolve().parent
OUT_ROOT   = ROOT / "_public"              # Cloudflare Pages output
BLOG_DIR   = OUT_ROOT / "blog"             # Blog root (được mount làm "/" nhờ Pages Functions)
COMING_DIR = OUT_ROOT / "coming-soon"      # Coming soon site
CONTACT_DIR= OUT_ROOT / "contact"          # (tuỳ chọn)

# Input
POSTS      = ROOT / "posts"
IMAGES     = ROOT / "images"
ASSETS     = ROOT / "assets"               # assets/css | assets/js
TEMPLATES  = ROOT / "templates"            # index_body.html | post_body.html | category_body.html

# Thông tin site
BRAND      = os.environ.get("BRAND", "CacheMissed Blog")
BASE_URL   = "/"                           # vì Pages Functions mount blog thành "/"
YEAR_NOW   = datetime.date.today().year

# Tạo sẵn thư mục đích
for d in [OUT_ROOT, BLOG_DIR, COMING_DIR, CONTACT_DIR, BLOG_DIR/"posts", BLOG_DIR/"category", BLOG_DIR/"css", BLOG_DIR/"js", BLOG_DIR/"images"]:
    d.mkdir(parents=True, exist_ok=True)


# ================== HTML SHELL (HEADER/FOOTER) ==================
def header_html(brand_text: str, page_class: str, crumb_title: str|None=None) -> str:
    """Header sticky, nhỏ gọn; search là icon (trên mobile giống yêu cầu)."""
    # Breadcrumb: / [icon] Tên bài (nếu có)
    doc_svg = """<svg class="docico" viewBox="0 0 24 24" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M14 2v6h6" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>"""
    crumb = f'<span class="brand-path"><span class="sep">/</span> {doc_svg}<span class="crumb-txt">{crumb_title}</span></span>' if crumb_title else ""
    return f"""
<header class="site-head">
  <div class="head-inner">
    <a class="brand" href="/">
      <img class="logo logo-light" src="/images/logo-light.png" alt="logo">
      <img class="logo logo-dark"  src="/images/logo-dark.png"  alt="logo">
      <span class="txt">{brand_text}</span>
    </a>
    {crumb}
    <div class="spacer"></div>

    <!-- search: icon-only trên màn nhỏ -->
    <button class="s-ico-btn" id="miniSearch" aria-label="Search" title="Search">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
           stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="11" cy="11" r="7"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
    </button>

    <!-- theme toggle -->
    <button class="theme" id="themeToggle" type="button" aria-pressed="false" title="Toggle theme">
      <span class="label label-dark">DARK</span>
      <span class="track"><span class="knob"></span></span>
      <span class="label label-light">LIGHT</span>
    </button>
  </div>
</header>
"""

def footer_html() -> str:
    return f"""<footer class="site-foot">
  <p>© {YEAR_NOW} CacheMissed</p>
</footer>"""

def render_shell(title: str, body: str, page_class: str, canonical: str|None=None,
                 css_name: str|None=None, js_name: str|None=None, crumb: str|None=None) -> str:
    """Khung HTML hoàn chỉnh: chèn header/footer + CSS/JS theo trang."""
    # css theo trang (index.css | post.css | category.css)
    css_links = [
        '<link rel="stylesheet" href="/css/base.css">',
    ]
    if css_name:
        css_links.append(f'<link rel="stylesheet" href="/css/{css_name}">')

    # js dùng chung + theo trang
    js_links = ['<script defer src="/js/common.js"></script>']
    if js_name:
        js_links.append(f'<script defer src="/js/{js_name}"></script>')

    head_extra = f'<link rel="canonical" href="{canonical}">' if canonical else ""

    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
{head_extra}
{''.join(css_links)}
</head>
<body class="{page_class}">
{header_html(BRAND, page_class, crumb)}
{body}
{footer_html()}
{''.join(js_links)}
</body></html>"""


# ================== CSS BASE ==================
# (Giữ tinh gọn; palette xanh/vàng theo yêu cầu, header sticky, footer center)
BASE_CSS = r"""
:root{
  --brand:#2563eb;       /* xanh link (blue-600) */
  --accent:#f5d26b;      /* vàng */
  --ink:#0b1320; --muted:#6b7280; --rule:#e5e7eb; --bg:#ffffff;
  --d-bg:#0a0a0a; --d-ink:#f5d26b; --d-muted:#9c7f2b; --d-rule:#1f2937; --d-link:#ffd166;
  --w: clamp(640px, 86vw, 820px);
  --head-h: 60px;
}
@media (prefers-color-scheme: dark){
  :root{ --ink:var(--d-ink); --muted:var(--d-muted); --rule:var(--d-rule); --bg:var(--d-bg); }
}
:root[data-theme="light"]{ --ink:#0b1320; --muted:#6b7280; --rule:#e5e7eb; --bg:#fff; }
:root[data-theme="dark"]{ --ink:var(--d-ink); --muted:var(--d-muted); --rule:var(--d-rule); --bg:var(--d-bg); }

*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,Segoe UI,Roboto,Helvetica,Arial,"Noto Sans",sans-serif}
a{color:#1f6feb} img{max-width:100%;height:auto}

/* header */
.site-head{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:1px solid var(--rule)}
.head-inner{max-width:1200px;margin:0 auto;padding:14px 18px;display:flex;align-items:center;gap:12px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:600;min-width:0}
.brand .logo{width:28px;height:28px;display:block;flex:0 0 auto}
.brand .logo-dark{display:none}
:root[data-theme="dark"] .brand .logo-dark{display:block}
:root[data-theme="dark"] .brand .logo-light{display:none}
.brand .txt{display:block;max-width:30vw;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.brand-path{display:flex;align-items:center;gap:6px;color:var(--muted);font-weight:700}
.brand-path .crumb-txt{color:var(--ink);max-width:36vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.spacer{flex:1 1 auto}
.s-ico-btn{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:999px;border:0;background:transparent;cursor:pointer;color:#4c1d95}

/* theme */
.theme{display:inline-flex;align-items:center;gap:10px;border:0;background:none;cursor:pointer;padding:0}
.theme .label{font-weight:800;letter-spacing:.08em;font-size:12px;color:var(--muted);opacity:.35;transition:opacity .25s ease,color .25s ease}
:root[data-theme="light"] .theme .label-light{color:var(--ink);opacity:1}
:root[data-theme="dark"]  .theme .label-dark{color:var(--ink);opacity:1}
.theme .track{position:relative;width:58px;height:28px;border-radius:999px;background:#e9edf3;border:1px solid var(--rule)}
.theme .knob{position:absolute;top:3px;left:3px;width:22px;height:22px;border-radius:50%}
:root[data-theme="light"] .theme .knob{background:#ffd166;box-shadow:inset 0 0 0 2px rgba(0,0,0,.06);transform:translateX(28px)}
:root[data-theme="dark"] .theme .knob{background:transparent}

/* common layout */
main{max-width:var(--w); margin:24px auto; padding:0 16px}
h1{font-size:28px;margin:8px 0 12px}
.hr{height:1px;background:var(--rule);margin:12px 0}
footer.site-foot{max-width:var(--w);margin:30px auto 50px;padding:0 16px;color:var(--muted);font-size:14px;text-align:center}
footer.site-foot p{margin:0}

/* index + category: list item */
.post{ margin:18px 0 24px; text-align:left; }
.post .date{ color:var(--muted); font-size:13px; margin:0 0 6px; letter-spacing:.2px; }
.post h2{ margin:0 0 8px; font-size:clamp(20px, 2.2vw + .4rem, 28px); line-height:1.3; }
.post h2 a{ color:#1f6feb; text-decoration:none; }
.post h2 a:hover{ text-decoration:underline; }
@media (max-width:640px){
  .post{ margin:14px 0 20px; }
  .post .date{ font-size:12.5px; }
}

/* pills: trung tâm; mobile cuộn ngang */
.catbar{max-width:var(--w);margin:10px auto 0;padding:0 16px}
.pills{display:flex;gap:10px 14px;flex-wrap:wrap;align-items:center;justify-content:center;margin:0;padding:6px 0;overflow:auto;scroll-snap-type:x proximity}
.pill{
  display:inline-flex;align-items:center;white-space:nowrap;scroll-snap-align:start;
  height:36px;padding:0 14px;border-radius:999px;background:#f2f3f8;color:#111;
  font-weight:700;font-size:13.5px;letter-spacing:.2px;box-shadow:0 1px 0 0 var(--rule) inset,0 1px 6px rgba(0,0,0,.04);
  transition:background .15s, transform .12s, box-shadow .15s;
}
.pill:hover{ background:rgba(127,75,235,.10); transform:translateY(-1px); }
.pill.is-active{ background:rgba(127,75,235,.16); box-shadow:0 0 0 2px rgba(127,75,235,.14) inset; }
@media (max-width:680px){ .pills{flex-wrap:nowrap;justify-content:flex-start} }

/* post page: TOC trái */
.post-wrap{ max-width:1200px;margin:24px auto;padding:0 18px;display:grid;grid-template-columns:260px 1fr;gap:28px }
.toc{ position:sticky; top:calc(var(--head-h) + 18vh); align-self:start; max-height: calc(100vh - var(--head-h) - 18vh - 20px);
  overflow:auto; padding-left:10px; border-left:2px solid var(--rule); font-size:13px; line-height:1.35; color:var(--muted) }
.toc .toc-title{font-weight:700;color:var(--ink);margin:0 0 6px}
.toc a{color:var(--muted);text-decoration:none}
.toc a:hover{color:#1f6feb;text-decoration:underline}
.toc .lvl-2{padding-left:10px}.toc .lvl-3{padding-left:18px}
.toc-tools{margin-top:8px;border-top:1px solid var(--rule);padding-top:8px;display:flex;flex-direction:column;gap:6px}
.toc-tools a{color:var(--muted);text-decoration:none;font-size:12.5px}
@media (max-width:1024px){ .post-wrap{display:block} .toc{border:0;border-top:1px solid var(--rule);padding:10px 0;max-width:var(--w);margin:0 auto 12px} }

/* dark mode moon icon bold */
:root[data-theme="dark"] .theme .knob::after{content:"";position:absolute;left:50%;top:50%;width:20px;height:20px;transform:translate(-50%,-50%);
  background-repeat:no-repeat;background-position:center;background-size:20px 20px;filter: drop-shadow(0 0 1px rgba(0,0,0,.45));
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'><path d='M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z' fill='%23f5d26b' stroke='%23000000' stroke-width='1.6'/></svg>");}
"""


# ================== TIỆN ÍCH ==================
def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""

def write_text(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")

def copy_tree(src: Path, dst: Path):
    if not src.exists(): return
    for p in src.rglob("*"):
        if p.is_file():
            rel = p.relative_to(src)
            (dst/rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst/rel)

def parse_date(meta_date, name_hint: str) -> datetime.date:
    if meta_date:
        return datetime.date.fromisoformat(str(meta_date)[:10])
    m = re.search(r"(\d{4})[-_](\d{2})[-_](\d{2})", name_hint)
    if m:
        y,mo,d = map(int,m.groups()); return datetime.date(y,mo,d)
    return datetime.date.today()

def human(d: datetime.date) -> str:
    return d.strftime("%Y %b %d")

def collect_categories(meta) -> list[str]:
    cats=[]
    if meta.get("category"): cats.append(str(meta["category"]))
    if meta.get("categories"):
        c = meta["categories"]
        if isinstance(c, str): cats.append(c)
        else: cats.extend([str(x) for x in c])
    return [x.strip() for x in cats if str(x).strip()]


# ================== RENDER TỪ TEMPLATES ==================
# body templates (không gồm <html>…>)
TPL_INDEX_BODY    = read_text(TEMPLATES/"index_body.html")
TPL_POST_BODY     = read_text(TEMPLATES/"post_body.html")
TPL_CATEGORY_BODY = read_text(TEMPLATES/"category_body.html")

def render_index_body(posts: list[dict], pills: list[dict]) -> str:
    """Dùng template index_body.html (có placeholder {{...}} kiểu rất đơn giản)."""
    # Thay bằng render thủ công cho chắc (tránh phụ thuộc jinja). Template có các marker:
    # {{PILLS}} -> HTML các pill
    # {{POSTS}} -> HTML list bài
    pill_html = "".join([f'<a class="pill" href="{p["href"]}">{p["label"]}</a>' for p in pills])
    posts_html = "".join([
        f'<article class="post"><div class="date">{e["date_human"]}</div>'
        f'<h2><a href="{e["url"]}">{e["title"]}</a></h2></article>'
        for e in posts
    ])
    body = TPL_INDEX_BODY
    body = body.replace("{{PILLS}}", pill_html)
    body = body.replace("{{POSTS}}", posts_html)
    return body

def render_post_body(title: str, date_human: str, category: str|None, content_html: str) -> str:
    body = TPL_POST_BODY
    body = body.replace("{{TITLE}}", title)
    body = body.replace("{{DATE_HUMAN}}", date_human)
    body = body.replace("{{CATEGORY}}", category or "")
    body = body.replace("{{CONTENT}}", content_html)
    return body

def render_category_body(cat_name: str, posts: list[dict], pills: list[dict]) -> str:
    pill_html  = "".join([f'<a class="pill" href="{p["href"]}">{p["label"]}</a>' for p in pills])
    posts_html = "".join([
        f'<article class="post"><div class="date">{e["date_human"]}</div>'
        f'<h2><a href="{e["url"]}">{e["title"]}</a></h2></article>'
        for e in posts
    ])
    body = TPL_CATEGORY_BODY
    body = body.replace("{{CAT_NAME}}", cat_name)
    body = body.replace("{{PILLS}}", pill_html)
    body = body.replace("{{POSTS}}", posts_html)
    return body


# ================== BUILD BLOG ==================
def build_assets():
    # CSS/JS từ assets → BLOG_DIR
    write_text(BLOG_DIR/"css"/"base.css", BASE_CSS)
    copy_tree(ASSETS/"css", BLOG_DIR/"css")
    copy_tree(ASSETS/"js",  BLOG_DIR/"js")
    # images → BLOG_DIR/images
    copy_tree(IMAGES, BLOG_DIR/"images")

def render_post(md_path: Path, entries: list, cats_map: dict):
    fm = frontmatter.load(md_path)
    html = markdown.markdown(fm.content, extensions=["extra","toc","tables","codehilite"])
    title = fm.get("title") or md_path.stem.replace("-"," ").title()
    d = parse_date(fm.get("date"), md_path.as_posix())
    date_human = human(d)
    slug = fm.get("slug") or slugify(md_path.stem)
    out = BLOG_DIR/"posts"/f"{slug}.html"
    cats = collect_categories(fm.metadata)
    main_cat = cats[0] if cats else None
    post_url = f"/posts/{out.name}"

    # add vào map
    for c in cats:
        cats_map.setdefault(c, []).append({"title":title, "date":d, "date_human":date_human, "url":post_url})

    # body & shell
    body = render_post_body(title, date_human, main_cat, html)
    page_html = render_shell(
        title=title,
        body=body,
        page_class="page-post no-search",
        canonical=urljoin(BASE_URL, f"posts/{out.name}"),
        css_name="post.css",
        js_name="post.js",
        crumb=title
    )
    write_text(out, page_html)

    entries.append({"title":title, "date":d, "date_human":date_human, "url":post_url, "categories":cats})

def build_blog():
    build_assets()
    entries=[]; cats_map={}
    # quét posts
    for p in POSTS.rglob("*.md"):
        render_post(p, entries, cats_map)

    # sort mới nhất
    entries.sort(key=lambda x:x["date"], reverse=True)

    # pills theo category
    unique_cats = sorted({c for e in entries for c in e["categories"]}) if entries else []
    pills = [{"href": f"/category/{slugify(c)}.html", "label": c} for c in unique_cats]

    # index
    index_body = render_index_body(entries, pills)
    index_html = render_shell(
        title=BRAND,
        body=index_body,
        page_class="page-index",
        css_name="index.css",
        js_name="index.js"
    )
    write_text(BLOG_DIR/"index.html", index_html)

    # category pages
    for cat, posts in cats_map.items():
        posts.sort(key=lambda x:x["date"], reverse=True)
        body = render_category_body(cat, posts, pills)
        html = render_shell(
            title=cat,
            body=body,
            page_class="page-category",
            css_name="category.css",
            js_name="category.js"
        )
        write_text(BLOG_DIR/"category"/f"{slugify(cat)}.html", html)

    # RSS (50 bài)
    items=[]
    for e in entries[:50]:
        items.append(f"""<item>
  <title><![CDATA[{e['title']}]]></title>
  <link>{e['url']}</link>
  <guid isPermaLink="false">{e['url']}</guid>
  <pubDate>{e['date'].strftime('%a, %d %b %Y 00:00:00 +0000')}</pubDate>
</item>""")
    feed=f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<title>{BRAND}</title><link>{BASE_URL}</link><description>RSS</description>
{''.join(items)}
</channel></rss>"""
    write_text(BLOG_DIR/"feed.xml", feed.strip())

    # sitemap + index.json
    urls=[BASE_URL] + [e["url"] for e in entries]
    urls += [f"/category/{slugify(c)}.html" for c in cats_map.keys()]
    sm=["<?xml version='1.0' encoding='UTF-8'?>","<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"]
    for u in urls: sm.append(f"<url><loc>{u}</loc></url>")
    sm.append("</urlset>")
    write_text(BLOG_DIR/"sitemap.xml", "\n".join(sm))

    write_text(BLOG_DIR/"index.json", json.dumps([
        {"title":e["title"],"date":e["date"].isoformat(),"url":e["url"],"categories":e["categories"]} for e in entries
    ], ensure_ascii=False, indent=2))

    print(f"[BLOG] {len(entries)} post(s), {len(cats_map)} category page(s) → {BLOG_DIR}")


# ================== BUILD COMING-SOON & CONTACT ==================
def build_coming_soon():
    src = ROOT/"coming-soon"/"index.html"
    if src.exists():
        shutil.copy2(src, COMING_DIR/"index.html")
        print(f"[COMING] Copied → {COMING_DIR/'index.html'}")

def build_contact():
    src = ROOT/"contact"/"index.html"
    if src.exists():
        shutil.copy2(src, CONTACT_DIR/"index.html")
        print(f"[CONTACT] Copied → {CONTACT_DIR/'index.html'}")


# ================== MAIN ==================
def main():
    build_blog()
    build_coming_soon()
    build_contact()
    print(f"✅ Built to {OUT_ROOT}")

if __name__ == "__main__":
    main()
