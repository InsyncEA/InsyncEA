#!/usr/bin/env python3
"""Speeds up every InSyncEA page. Run from the website's main folder:  python3 tools/optimize_pages.py
1. Uses fonts stored on your own site instead of Google Fonts (removes a render-blocking request).
2. Replaces small inline style attributes with CSS classes.
Safe to run many times. Pages that do not use /assets/site.css are left alone."""
import re
from pathlib import Path

ROOT = Path.cwd()
SKIP = {'.git', 'node_modules', 'tools', 'named'}
GF = re.compile(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?family=DM\+Sans[^"]*">')
PRE = ['<link rel="preconnect" href="https://fonts.googleapis.com">', '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>']
PRELOAD = ('<link rel="preload" href="/assets/fonts/dm-sans-400.woff2" as="font" type="font/woff2" crossorigin>'
           '<link rel="preload" href="/assets/fonts/source-serif-4-600.woff2" as="font" type="font/woff2" crossorigin>')
CSS = '<link rel="stylesheet" href="/assets/site.css">'
MAP = {'justify-content:center': 'ctr', 'margin-top:28px': 'mt28', 'margin-top:20px': 'mt20', 'overflow-x:auto': 'tw', 'margin-top:0': None}

fonts_ready = (ROOT / 'assets/fonts/dm-sans-400.woff2').exists() and '@font-face' in (ROOT / 'assets/site.css').read_text(encoding='utf-8')

def fix_styles(h):
    def sub(m):
        tag = m.group(0)
        sm = re.search(r'\sstyle="([^"]*)"', tag)
        key = sm.group(1).strip().rstrip(';').replace(' ', '') if sm else None
        if key not in MAP: return tag
        tag = tag.replace(sm.group(0), '', 1)
        cls = MAP[key]
        if cls:
            if re.search(r'\sclass="', tag): tag = re.sub(r'(\sclass=")([^"]*)"', lambda x: x.group(1) + x.group(2) + ' ' + cls + '"', tag, count=1)
            else: tag = re.sub(r'^<(\w+)', lambda x: '<' + x.group(1) + ' class="' + cls + '"', tag, count=1)
        return tag
    return re.sub(r'<(?!/|!)[^>]*\sstyle="[^"]*"[^>]*>', sub, h)

def main():
    changed = 0
    for f in ROOT.rglob('*.html'):
        if SKIP & set(f.relative_to(ROOT).parts): continue
        h = old = f.read_text(encoding='utf-8')
        if '/assets/site.css' not in h: continue
        if fonts_ready:
            h = GF.sub('', h)
            for p in PRE: h = h.replace(p, '')
            if 'dm-sans-400.woff2' not in h: h = h.replace(CSS, PRELOAD + CSS, 1)
        h = fix_styles(h)
        if h != old: f.write_text(h, encoding='utf-8'); changed += 1; print('optimized', f.relative_to(ROOT))
    print('done,', changed, 'page(s) changed' + ('' if fonts_ready else ' (fonts not found, so the font step was skipped)'))

if __name__ == '__main__': main()
