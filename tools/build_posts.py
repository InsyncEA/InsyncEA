#!/usr/bin/env python3
"""Turns each article written in the CMS (content/blog/*.md) into a finished web page,
and keeps assets/posts.json and sitemap.xml up to date.
Run from the website's main folder:  python3 tools/build_posts.py
Needs:  pip install markdown pyyaml"""
import json, math, re, html
from datetime import datetime
from pathlib import Path
import markdown, yaml

ROOT = Path.cwd()
SITE = 'https://insyncea.com'
SVC = {'executive-support': 'executive support services',
       'business-operations-support': 'business operations support',
       'customer-partnership-operations': 'customer and partnership operations',
       'administrative-support': 'remote administrative support'}
e = lambda s: html.escape(str(s), quote=True)

def front(text):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text, re.S)
    return ((yaml.safe_load(m.group(1)) or {}), m.group(2)) if m else ({}, text)

def as_list(v): return [str(x) for x in v] if isinstance(v, list) else ([str(v)] if v else [])

def main():
    tpl = (ROOT / 'tools/blog-post-template.html').read_text(encoding='utf-8')
    pj = ROOT / 'assets/posts.json'
    old = json.loads(pj.read_text(encoding='utf-8')) if pj.exists() else {'posts': []}
    old = old.get('posts', []) if isinstance(old, dict) else old
    made, urls = [], []
    for f in sorted((ROOT / 'content/blog').glob('*.md')):
        meta, body = front(f.read_text(encoding='utf-8'))
        if meta.get('draft'): print('skipped draft:', f.name); continue
        need = [k for k in ('title', 'meta_title', 'meta_description', 'image', 'date') if not meta.get(k)]
        if need: print('WARNING:', f.name, 'is missing', ', '.join(need), '- page not built'); continue
        slug = str(meta.get('url_slug') or f.stem).strip().strip('/')
        title, mt, md = meta['title'], meta['meta_title'], meta['meta_description']
        d = str(meta['date'])[:10]; dt = datetime.strptime(d, '%Y-%m-%d')
        img = '/' + str(meta['image']).lstrip('/')
        alt = meta.get('image_alt') or title
        cat = meta.get('category') or 'Blog'
        excerpt = meta.get('excerpt') or md
        tags, aud, svcs = as_list(meta.get('tags')), as_list(meta.get('audience')), as_list(meta.get('services'))
        kws = [k for k in [meta.get('focus_keyword')] + as_list(meta.get('keywords')) if k]
        html_body = markdown.markdown(body, extensions=['extra', 'sane_lists']).replace('<h1', '<h2').replace('</h1>', '</h2>')
        words = len(re.findall(r'\w+', re.sub(r'<[^>]+>', ' ', html_body)))
        mins = max(1, math.ceil(words / 200))
        links = [f'<a href="/services/{s}/">{SVC[s]}</a>' for s in svcs if s in SVC]
        box = ''
        if links:
            joined = links[0] if len(links) == 1 else ', '.join(links[:-1]) + ' or ' + links[-1]
            box = f'<aside class="svc-box"><p class="svc-t">How InSyncEA can help</p><p>Explore {joined}, or <a href="/contact/#book">book a consultation</a>.</p></aside>'
        url = f'/blog/{slug}/'
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "BlogPosting", "headline": title, "description": md, "image": SITE + img, "datePublished": d, "dateModified": d,
             "keywords": ', '.join(kws), "articleSection": cat, "wordCount": words,
             "author": {"@type": "Person", "name": "Wendy Mwende", "url": SITE + "/about/"},
             "publisher": {"@type": "Organization", "name": "InSyncEA", "url": SITE + "/"}, "mainEntityOfPage": SITE + url},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"},
                {"@type": "ListItem", "position": 3, "name": title, "item": SITE + url}]}]}
        ld_tag = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script>'
        h = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: ld_tag, tpl, count=1, flags=re.S)
        for k, v in {'[META TITLE]': e(mt), '[META DESCRIPTION]': e(md), '[POST TITLE]': e(title), '[post-slug]': slug, '[CATEGORY]': e(cat),
                     '[ONE-SENTENCE SUMMARY OF THE ARTICLE]': e(excerpt), '[PUBLISH DATE YYYY-MM-DD]': d,
                     '[PUBLISH DATE TEXT]': f'{dt:%B} {dt.day}, {dt.year}', '[MINUTES]': str(mins), '[DESCRIBE THE IMAGE]': e(alt)}.items():
            h = h.replace(k, v)
        h = h.replace('/assets/blog/[IMAGE-FILE]', img)
        h = h.replace('<link rel="canonical"', '<meta name="robots" content="index,follow,max-image-preview:large"><link rel="canonical"', 1)
        h = re.sub(r'<!--body:start-->.*?<!--body:end-->', lambda m: '<!--body:start-->' + html_body + box + '<!--body:end-->', h, flags=re.S)
        out = ROOT / 'blog' / slug / 'index.html'; out.parent.mkdir(parents=True, exist_ok=True)
        if not out.exists() or out.read_text(encoding='utf-8') != h: out.write_text(h, encoding='utf-8'); print('built', url)
        urls.append((url, d))
        made.append({'url': url, 'title': title, 'excerpt': excerpt, 'image': img, 'imageAlt': alt, 'category': cat,
                     'tags': tags, 'audience': aud, 'services': svcs, 'date': d, 'auto': True})
    keep = [p for p in old if not p.get('auto') and p.get('url') not in {m['url'] for m in made}]
    new = json.dumps({'posts': keep + made}, indent=2, ensure_ascii=False) + '\n'
    if not pj.exists() or pj.read_text(encoding='utf-8') != new: pj.write_text(new, encoding='utf-8'); print('updated assets/posts.json')
    sm = ROOT / 'sitemap.xml'
    if sm.exists():
        s = sm.read_text(encoding='utf-8'); add = ''
        for u, d in urls:
            if SITE + u not in s: add += f'  <url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod></url>\n'
        if add and '</urlset>' in s: sm.write_text(s.replace('</urlset>', add + '</urlset>'), encoding='utf-8'); print('added to sitemap.xml')
    print('done,', len(made), 'article(s) built')

if __name__ == '__main__': main()
