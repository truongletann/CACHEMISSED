#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

# ============ Cấu hình cơ bản ============
ROOT = Path(__file__).parent.resolve()
TEMPLATES = ROOT / "templates"
POSTS_DIR = ROOT / "posts"          # nơi chứa *.md
ASSETS_DIR = ROOT / "assets"        # assets/css, assets/js
IMAGES_DIR = ROOT / "images"        # nếu bạn để images riêng
OUT = ROOT / "_public" / "blog"     # output blog
OUT_ROOT = ROOT / "_public"         # gốc _public
BASE_URL = os.environ.get("BASE_URL", "/")  # không cần /blog/ nữa

# ============ Jinja env ============
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
)

# ---------- Helpers ----------

SLUG_RE = re.compile(r"[^a-z0-9\-]+")

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = SLUG_RE.sub("-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "untitled"

def human_date(dt: datetime) -> str:
    # ví dụ "2025 Sep 06"
    return dt.strftime("%Y %b %d")

def ensure_clean_dir(p: Path):
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)

# ---------- Đọc & parse front matter ----------
FM_START = re.compile(r"^\s*---\s*$")
FM_END   = re.compile(r"^\s*---\s*$")

def parse_post_file(path: Path):
    """
    Parse file Markdown có front-matter YAML kiểu đơn giản:
    ---
    title: GYM BASE
    date: 2025-09-06
    pills: [aaa, bbbb, cccc]
    slug: gym-base
    ---
    (markdown body …)
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    meta = {}
    body_lines = []
    i = 0
    if i < len(lines) and FM_START.match(lines[i]):
        i += 1
        # đọc meta đến --- kế
        buf = []
        while i < len(lines) and not FM_END.match(lines[i]):
            buf.append(lines[i])
            i += 1
        # bỏ dòng '---'
        i += 1
        # parse YAML rất đơn giản (key: value, list dạng [a, b])
        for ln in buf:
            if ":" not in ln:
                continue
            k, v = ln.split(":", 1)
            k = k.strip()
            v = v.strip()
            # list [a, b, c]
            if v.startswith("[") and v.endswith("]"):
                items = [x.strip() for x in v[1:-1].split(",") if x.strip()]
                meta[k] = items
            else:
                meta[k] = v
    # phần còn lại coi là body (không cần render markdown ở bản tối giản)
    body_lines = lines[i:]

    # bắt buộc title, date
    title = meta.get("title") or path.stem
    date_raw = (meta.get("date") or "").strip()
    # hỗ trợ "2025-09-06" hoặc "2025/09/06"
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y %m %d"):
        try:
            dt = datetime.strptime(date_raw, fmt)
            break
        except Exception:
            dt = None
    if dt is None:
        # fallback mtime file
        dt = datetime.fromtimestamp(path.stat().st_mtime)

    pills = meta.get("pills") or meta.get("tags") or []
    if isinstance(pills, str):
        # "aaa, bbb"
        pills = [x.strip() for x in pills.split(",") if x.strip()]

    slug = meta.get("slug") or slugify(title)

    return {
        "title": title,
        "date": dt,
        "date_human": human_date(dt),
        "pills": pills,
        "slug": slug,
        "url": f"{BASE_URL.rstrip('/')}/{slug}/",  # nếu sau này có trang chi tiết
        "body": "\n".join(body_lines),
        "source": str(path),
    }

def load_posts():
    posts = []
    if not POSTS_DIR.exists():
        return posts
    for p in sorted(POSTS_DIR.glob("*.md")):
        posts.append(parse_post_file(p))
    # sort desc by date
    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts

def build_pills(posts):
    # từ tất cả tags/pills
    seen = {}
    for p in posts:
        for t in p["pills"]:
            slug = slugify(t)
            if slug not in seen:
                seen[slug] = {
                    "label": t,
                    "slug": slug,
                    "href": f"{BASE_URL.rstrip('/')}/category/{slug}.html",
                }
    pills = list(seen.values())
    # có thể sort theo alpha
    pills.sort(key=lambda x: x["label"].lower())
    return pills

def group_by_category(posts):
    cat = {}
    for p in posts:
        for t in p["pills"]:
            slug = slugify(t)
            cat.setdefault(slug, {"label": t, "slug": slug, "posts": []})
            cat[slug]["posts"].append(p)
    # sort mỗi group theo date desc
    for k in cat:
        cat[k]["posts"].sort(key=lambda x: x["date"], reverse=True)
    return cat

# ---------- Render ----------
def render_index(posts, pills):
    tmpl = env.get_template("index_body.html")
    html = tmpl.render(posts=posts, pills=pills, base_url=BASE_URL)
    (OUT / "index.html").write_text(html, encoding="utf-8")

def render_category_pages(cats, pills):
    tmpl = env.get_template("category_body.html")
    cat_dir = OUT / "category"
    cat_dir.mkdir(parents=True, exist_ok=True)
    for slug, c in cats.items():
        html = tmpl.render(
            category={"label": c["label"], "slug": c["slug"]},
            posts=c["posts"],
            pills=pills,
            base_url=BASE_URL,
        )
        (cat_dir / f"{slug}.html").write_text(html, encoding="utf-8")

# ---------- Copy assets ----------
def copy_assets():
    # css/js
    if ASSETS_DIR.exists():
        for sub in ("css", "js"):
            s = ASSETS_DIR / sub
            if s.exists():
                d = OUT / sub
                if d.exists():
                    shutil.rmtree(d)
                shutil.copytree(s, d)
    # images (nếu bạn để riêng)
    if IMAGES_DIR.exists():
        d = OUT / "images"
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(IMAGES_DIR, d)

# ---------- Coming soon ----------
def copy_coming_soon():
    src = None
    if (ROOT / "coming-soon" / "index.html").exists():
        src = ROOT / "coming-soon" / "index.html"
    elif (ROOT / "coming_soon" / "index.html").exists():
        src = ROOT / "coming_soon" / "index.html"

    if src:
        dst_dir = OUT_ROOT / "coming-soon"
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst_dir / "index.html")

# ---------- Sanity check ----------
def sanity_no_jinja(path: Path):
    s = path.read_text(encoding="utf-8")
    if "{{" in s or "{%" in s:
        # tránh f-string để khỏi phải escape {{ }}
        raise SystemExit(
            "ERROR: {} còn template markers ({{ hoặc {%)".format(path)
        )


# ---------- Entry ----------
def main():
    # reset output
    ensure_clean_dir(OUT)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)

    posts = load_posts()
    pills = build_pills(posts)
    cats = group_by_category(posts)

    render_index(posts, pills)
    render_category_pages(cats, pills)

    copy_assets()
    copy_coming_soon()

    # sanity
    sanity_no_jinja(OUT / "index.html")
    for f in (OUT / "category").glob("*.html"):
        sanity_no_jinja(f)

    # (tùy chọn) ghi index.json / sitemap / feed nếu muốn
    # (để gọn, mình chỉ xuất index.json cho nhanh)
    (OUT / "index.json").write_text(
        json.dumps(
            [
                {
                    "title": p["title"],
                    "date": p["date"].strftime("%Y-%m-%d"),
                    "slug": p["slug"],
                    "url": p["url"],
                    "pills": p["pills"],
                }
                for p in posts
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"[BLOG] Built -> {OUT}")
    print("[COMING] copied if exists -> _public/coming-soon/index.html")

if __name__ == "__main__":
    main()
