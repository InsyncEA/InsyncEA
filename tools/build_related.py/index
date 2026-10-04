#!/usr/bin/env python3
"""Writes the Related Articles cards into each blog page's HTML (no JavaScript needed).
Run from the website's main folder:  python3 tools/build_related.py
Reads assets/posts.json, edits blog/<slug>/index.html pages, safe to run many times."""
import json, re, sys, html
from pathlib import Path

ROOT = Path.cwd()
STOP = set('about after also and are but can does for from have how into just more not our out that the their them then they this what when where which why will with you your'.split())
CSS_LINK = '<link rel="stylesheet" href="/assets/related-articles.css">'

def norm(u):
    u = re.sub(r'^https?://[^/]+', '', str(u or '').split('#')[0].split('?')[0])
    u = re.sub(r'index\.html$', '', u)
    if not u.startswith('/'): u = '/' + u
    if not u.endswith('/'): u += '/'
    return u.lower()

def sset(a): return {str(x).lower().strip() for x in (a or []) if str(x).strip()}
def words(p): return [w for w in re.findall(r'[a-z0-9]{4,}', ((p.get('title') or '') + ' ' + (p.get('excerpt') or '')).lower()) if w not in STOP]

def score(a, b):
    s = 0.0
    if a.get('category') and str(a['category']).lower() == str(b.get('category') or '').lower(): s += 5
    s += 2 * len(sset(a.get('tags')) & sset(b.get('tags')))
    s += 2 * min(len(sset(a.get('audience')) & sset(b.get('audience'))), 2)
    s += 3 * min(len(sset(a.get('services')) & sset(b.get('services'))), 1)
    s += .5 * min(len(sset(words(a)) & sset(words(b))), 3)
    return s

def pick(posts, me, n=5):
    out = [p for p in posts if norm(p['url']) != norm(me['url'])]
    out.sort(key=lambda p: p.get('date') or '', reverse=True)          # newest first for ties
    out.sort(key=lambda p: -score(me, p))                              # stable: score wins, then newest
    return out[:n]

def cut(s):
    s = (s or '').strip()
    return s if len(s) <= 150 else re.sub(r'\s+\S*$', '', s[:150]) + '...'

def card(p):
    e = html.escape
    cat = f'<p class="ra-c">{e(p["category"])}</p>' if p.get('category') else ''
    return (f'<article class="ra-card"><img src="{e(p.get("image") or "/assets/og-image.png")}" alt="{e(p.get("imageAlt") or p["title"])}" '
            f'width="640" height="360" loading="lazy" decoding="async"><div class="ra-b">{cat}<h3><a href="{e(p["url"])}">{e(p["title"])}</a></h3>'
            f'<p class="ra-e">{e(cut(p.get("excerpt")))}</p><span class="ra-more" aria-hidden="true">Read article</span></div></article>')

def main():
    data = json.loads((ROOT / 'assets/posts.json').read_text(encoding='utf-8'))
    posts = [p for p in (data.get('posts') if isinstance(data, dict) else data) if p.get('url') and p.get('title')]
    known = {norm(p['url']) for p in posts}
    changed = 0
    for p in posts:
        f = ROOT / norm(p['url']).strip('/') / 'index.html'
        if not f.exists():
            print('WARNING: no page found for', p['url']); continue
        h = f.read_text(encoding='utf-8'); old = h
        rel = pick(posts, p)
        cards = ''.join(card(x) for x in rel)
        h = h.replace('<div class="ra-grid" id="ra-grid"></div>', '<div class="ra-grid" id="ra-grid"><!--ra:start--><!--ra:end--></div>')
        if '<!--ra:start-->' not in h:
            print('WARNING: Related Articles section missing in', f.relative_to(ROOT)); continue
        h = re.sub(r'<!--ra:start-->.*?<!--ra:end-->', lambda m: '<!--ra:start-->' + cards + '<!--ra:end-->', h, flags=re.S)
        h = re.sub(r'class="ra-grid[^"]*" id="ra-grid"', f'class="ra-grid ra-n{len(rel)}" id="ra-grid"', h, count=1)
        if CSS_LINK not in h: h = h.replace('</head>', CSS_LINK + '</head>', 1)
        if h != old: f.write_text(h, encoding='utf-8'); changed += 1; print('updated', f.relative_to(ROOT), f'({len(rel)} related)')
    for slug in ('executive-support', 'business-operations-support', 'customer-partnership-operations', 'administrative-support'):
        f = ROOT / 'services' / slug / 'index.html'
        if not f.exists(): continue
        h = f.read_text(encoding='utf-8'); old = h
        if '<!--sa:start-->' not in h: continue
        mine = sorted([p for p in posts if slug in (p.get('services') or [])], key=lambda p: p.get('date') or '', reverse=True)[:4]
        h = re.sub(r'<!--sa:start-->.*?<!--sa:end-->', lambda m: '<!--sa:start-->' + ''.join(card(x) for x in mine) + '<!--sa:end-->', h, flags=re.S)
        h = re.sub(r'class="ra-grid[^"]*" id="sa-grid"', f'class="ra-grid ra-n{len(mine)}" id="sa-grid"', h, count=1)
        h = re.sub(r'<section class="ra" id="service-articles"[^>]*>', lambda m: re.sub(r'\s+hidden', '', m.group(0)) if mine else (m.group(0) if ' hidden' in m.group(0) else m.group(0).replace('id="service-articles"', 'id="service-articles" hidden')), h, count=1)
        if CSS_LINK not in h: h = h.replace('</head>', CSS_LINK + '</head>', 1)
        if h != old: f.write_text(h, encoding='utf-8'); changed += 1; print('updated', f.relative_to(ROOT), f'({len(mine)} articles)')
    for f in (ROOT / 'blog').glob('*/index.html'):
        if norm('/' + str(f.parent.relative_to(ROOT))) not in known: print('NOTE: blog page not listed in posts.json:', f.relative_to(ROOT))
    print('done,', changed, 'page(s) changed')

if __name__ == '__main__': sys.exit(main())
