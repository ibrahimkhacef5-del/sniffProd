
import re
import subprocess
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

OUT_DIR = Path("/sdcard/Sniffer")
COLORS = {"g": "\033[1;32m", "y": "\033[1;33m", "c": "\033[1;36m", "r": "\033[1;31m", "x": "\033[0m"}

def color(t, c):
    return f"{COLORS.get(c, '')}{t}{COLORS['x']}"

def detect_extension(url, content, content_type):
    path_ext = Path(urlparse(url).path).suffix.lower()
    if path_ext and len(path_ext) > 1:
        return path_ext

    if "text/html" in content_type: return ".html"
    if "text/css" in content_type: return ".css"
    if "javascript" in content_type: return ".js"
    if "application/json" in content_type: return ".json"
    if "image/png" in content_type: return ".png"
    if "image/jpeg" in content_type: return ".jpg"
    if "image/svg" in content_type: return ".svg"

    c = content.lower()
    if "<?php" in c: return ".php"
    if "import os" in c or "def __init__" in c or "if __name__" in c: return ".py"
    if "const " in c or "function(" in c or "=>" in c: return ".js"
    if "<html" in c or "<!doctype" in c: return ".html"
    if "<?xml" in c: return ".xml"
    if "SELECT " in c.upper() and "FROM " in c.upper(): return ".sql"
    if re.match(r'^\s*\{.*\}\s*$', c, re.DOTALL): return ".json"

    try:
        res = subprocess.run(['file', '-b', '-'], input=content.encode('utf-8', errors='ignore'), capture_output=True)
        out = res.stdout.decode('utf-8').strip().lower()
        if "php" in out: return ".php"
        if "python" in out: return ".py"
        if "html" in out: return ".html"
        if "json" in out: return ".json"
        if "ascii text" in out: return ".txt"
    except:
        pass

    return ".txt"

def save_file(url, content, ext, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    name = Path(urlparse(url).path).stem or "file"
    name = re.sub(r'[^\w\-]', '_', name) or "index"

    filepath = out_dir / f"{name}{ext}"
    counter = 1
    while filepath.exists():
        filepath = out_dir / f"{name}_{counter}{ext}"
        counter += 1

    with open(filepath, "wb") as f:
        f.write(content)
    return filepath

def scan(url, out_dir=None):
    out_dir = Path(out_dir) if out_dir else OUT_DIR
    print(color(f"\n🔍 جاري فحص الموقع: {url}", "c"))
    print(color("=" * 50, "y"))

    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        html = r.text
    except Exception as e:
        print(color(f"❌ فشل الاتصال: {e}", "r"))
        return []

    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for tag in soup.find_all(True):
        for attr in ("src", "href", "action", "data-src"):
            val = tag.get(attr)
            if val and isinstance(val, str) and not val.startswith(("mailto:", "javascript:", "#")):
                links.add(urljoin(url, val))

    print(color(f"📌 تم العثور على {len(links)} رابط. جاري تحميل وفحص الملفات...", "y"))

    report = []
    for i, link in enumerate(sorted(links), 1):
        print(f"\r  [{i}/{len(links)}] معالجة: {link[:50]}...", end="", flush=True)
        try:
            res = requests.get(link, timeout=10, headers={"User-Agent": "Mozilla/5.0"}, stream=True)
            content = res.content
            content_type = res.headers.get("Content-Type", "").lower()
            ext = detect_extension(link, content, content_type)
            saved_path = save_file(link, content, ext, out_dir)
            report.append((link, ext, saved_path, len(content)))
        except Exception:
            pass

    print("\n\n" + color("📊 التقرير النهائي:", "g"))
    print(color("-" * 50, "y"))
    for link, ext, saved_path, size in report:
        print(f"🔗 {color(link, 'c')}")
        print(f"   📦 الامتداد: {color(ext, 'y')} | الحجم: {round(size / 1024, 1)} KB")
        print(f"   💾 الحفظ: {saved_path}")
        print()

    print(color(f"\n✅ تم حفظ كل الملفات في: {out_dir}", "g"))
    return report
