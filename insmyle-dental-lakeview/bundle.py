#!/usr/bin/env python3
"""Bundle a landing page's linked CSS, JS and local images into one
self-contained, downloadable .html file (base64 data URIs for images)."""
import base64
import mimetypes
import re
import sys
from pathlib import Path

def bundle(src_html: Path, out_html: Path):
    base = src_html.parent
    html = src_html.read_text(encoding="utf-8")

    # Inline <link rel="stylesheet" href="...">
    def css_sub(m):
        href = m.group(1)
        if href.startswith("http"):
            return m.group(0)
        css_path = base / href
        css = css_path.read_text(encoding="utf-8")
        return f"<style>\n{css}\n</style>"

    html = re.sub(
        r'<link rel="stylesheet" href="((?!https?://)[^"]+)">',
        css_sub, html
    )

    # Inline <script src="..."></script> (local only)
    def js_sub(m):
        src = m.group(1)
        if src.startswith("http"):
            return m.group(0)
        js_path = base / src
        js = js_path.read_text(encoding="utf-8")
        return f"<script>\n{js}\n</script>"

    html = re.sub(
        r'<script src="((?!https?://)[^"]+)"></script>',
        js_sub, html
    )

    # Inline local image references (src="assets/img/..." and href="assets/img/...")
    def img_sub(m):
        attr, path = m.group(1), m.group(2)
        if path.startswith("http") or path.startswith("data:"):
            return m.group(0)
        img_path = base / path
        if not img_path.exists():
            return m.group(0)
        mime, _ = mimetypes.guess_type(str(img_path))
        mime = mime or "application/octet-stream"
        data = base64.b64encode(img_path.read_bytes()).decode("ascii")
        return f'{attr}="data:{mime};base64,{data}"'

    html = re.sub(
        r'(src|href)="((?:assets/img/)[^"]+)"',
        img_sub, html
    )

    out_html.write_text(html, encoding="utf-8")
    print(f"Wrote {out_html} ({out_html.stat().st_size/1024:.0f} KB)")

if __name__ == "__main__":
    bundle(Path(sys.argv[1]), Path(sys.argv[2]))
