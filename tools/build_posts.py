#!/usr/bin/env python3
"""Turns each article written in the CMS (content/blog/*.md) into a finished web page,
and keeps assets/posts.json and sitemap.xml up to date.
Run from the website's main folder:  python3 tools/build_posts.py
Needs:  pip install markdown pyyaml"""
import json, math, re, html
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
import markdown, yaml

ROOT = Path.cwd()
SITE = 'https://insyncea.com'
SVC = {'executive-support': 'executive support services',
       'business-operations-support': 'business operations support',
       'customer-partnership-operations': 'customer and partnership operations',
       'administrative-support': 'remote administrative support'}
e = lambda s: html.escape(str(s), quote=True)
# An article goes live as soon as it is published: any article dated today (Nairobi time) or earlier is built straight away.
# A later date schedules it, and it goes live at midnight Nairobi time on that date.
TODAY = datetime.now(ZoneInfo('Africa/Nairobi')).strftime('%Y-%m-%d')

def front(text):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text, re.S)
    return ((yaml.safe_load(m.group(1)) or {}), m.group(2)) if m else ({}, text)

def as_list(v): return [str(x) for x in v] if isinstance(v, list) else ([str(v)] if v else [])

TOPICS = [
    ('Business Operations', 'Systems, planning and day-to-day operations for growing teams.'),
    ('Workflows and Systems', 'How to map, build and improve the workflows your business runs on.'),
    ('SOPs and Process Documentation', 'Turn know-how into clear, repeatable procedures.'),
    ('Executive Support', 'Calendar, inbox and decision support for busy leaders.'),
    ('Productivity', 'Habits and tools that protect your focus and your time.'),
    ('E-commerce Operations', 'Orders, inventory and store management that run smoothly.'),
]

def topic_slug(name): return re.sub(r'[^a-z0-9]+', '-', str(name).lower()).strip('-')

def blog_index(tpl, posts):
    """Writes blog/index.html: the blog resource hub (topics, featured guides, latest articles)."""
    title = 'Business Operations & Executive Support Resources | InSyncEA'
    desc = 'Practical guides on business operations, workflows, SOPs, productivity and executive support to help founders and small teams build better systems.'
    posts = sorted(posts, key=lambda p: p.get('date') or '', reverse=True)

    def card(p):
        cat = p.get('category') or ''
        q = e((str(p['title']) + ' ' + str(p.get('excerpt') or '') + ' ' + cat).lower())
        return (f'<article class="ra-card" data-cat="{e(topic_slug(cat))}" data-q="{q}"><img src="{e(p.get("image") or "/assets/og-image.png")}" alt="{e(p.get("imageAlt") or p["title"])}" width="640" height="360" loading="lazy" decoding="async">'
                f'<div class="ra-b">' + (f'<p class="ra-c">{e(cat)}</p>' if cat else '') +
                f'<h3><a href="{e(p["url"])}">{e(p["title"])}</a></h3><p class="ra-e">{e((p.get("excerpt") or "")[:150])}</p><span class="ra-more" aria-hidden="true">Read article</span></div></article>')

    counts = {}
    for p in posts: counts[topic_slug(p.get('category') or '')] = counts.get(topic_slug(p.get('category') or ''), 0) + 1
    chips = '<button type="button" class="bh-topic" data-topic="all" aria-pressed="true"><span class="bh-tn">All topics</span><span class="bh-td">Every article, newest first.</span></button>'
    for name, blurb in TOPICS:
        n = counts.get(topic_slug(name), 0)
        chips += (f'<button type="button" class="bh-topic" data-topic="{topic_slug(name)}" aria-pressed="false"><span class="bh-tn">{e(name)}</span>'
                  f'<span class="bh-td">{e(blurb)}</span><span class="bh-tc">{n} article{"" if n == 1 else "s"}</span></button>')

    hero = ('<section class="hero"><div class="wrap"><h1>Business Operations &amp; Executive Support Resources</h1>'
            '<p class="intro">Practical insights, guides, and strategies to help growing businesses improve operations, streamline workflows, document processes, and stay organized.</p>'
            '<p>Whether you want better systems, more productivity, or simpler day-to-day operations, you will find actionable resources made for founders and small teams.</p>'
            '<form class="bh-search" role="search" onsubmit="return false"><label for="bh-q">Search the blog</label><input id="bh-q" type="search" placeholder="Search articles, for example workflows" autocomplete="off"></form></div></section>')
    topics = (f'<section class="sec alt" aria-labelledby="bh-topics-t"><div class="wrap"><h2 id="bh-topics-t">Browse by topic</h2>'
              f'<p>Pick a topic to see only those articles.</p><div class="bh-topics">{chips}</div></div></section>')
    featured = ''
    if len(posts) >= 4:
        featured = ('<section class="ra bh-feat" aria-labelledby="bh-feat-t"><div class="ra-in"><h2 class="ra-h" id="bh-feat-t">Featured guides</h2><div class="ra-grid">'
                    + ''.join(card(p).replace(' data-cat=', ' data-feat="1" data-cat=') for p in posts[:3]) + '</div></div></section>')
    learn = ('<section class="sec" aria-labelledby="bh-learn-t"><div class="wrap"><h2 id="bh-learn-t">What you will learn</h2><ul class="bh-learn">'
             '<li>Build systems that help your business scale.</li><li>Improve workflows and reduce repetitive work.</li>'
             '<li>Create clear processes and documentation.</li><li>Organize daily operations more effectively.</li>'
             '<li>Delegate with confidence and improve team productivity.</li></ul></div></section>')
    if posts:
        listing = (f'<section class="ra" id="bh-latest" aria-labelledby="bl-t"><div class="ra-in"><h2 class="ra-h" id="bl-t">Latest articles</h2>'
                   f'<div class="ra-grid" id="bh-list">{"".join(card(p) for p in posts)}</div>'
                   '<p id="bh-none" class="bh-none" hidden>No articles match yet. New ones are on the way, so try another topic or search.</p></div></section>')
    else:
        listing = '<section class="sec"><div class="wrap"><h2>New articles are on the way</h2><p>In the meantime, explore the <a href="/services/">services</a> or read the <a href="/case-studies/">case studies</a>.</p></div></section>'
    cta = ('<section class="sec final"><div class="wrap"><h2>Looking for hands-on support?</h2>'
           '<p>Explore our executive and operations support services, or book a consultation and tell me what is taking up your time.</p>'
           '<div class="cta" style="justify-content:center"><a class="btn" href="/services/">Explore our services</a><a class="btn ghost" href="/contact/#book">Book a Consultation</a></div></div></section>')
    js = ('<script>(function(){var b=document.querySelectorAll(".bh-topic"),c=document.querySelectorAll("#bh-list .ra-card"),s=document.getElementById("bh-q"),n=document.getElementById("bh-none"),t="all";'
          'if(!s||!n)return;function f(){var q=s.value.trim().toLowerCase(),k=0;c.forEach(function(x){var ok=(t==="all"||x.getAttribute("data-cat")===t)&&(!q||x.getAttribute("data-q").indexOf(q)>-1);x.hidden=!ok;if(ok)k++});n.hidden=k>0}'
          'b.forEach(function(x){x.addEventListener("click",function(){t=x.getAttribute("data-topic");b.forEach(function(y){y.setAttribute("aria-pressed",y===x?"true":"false")});f();var l=document.getElementById("bh-latest");if(l)l.scrollIntoView({behavior:"smooth"})})});'
          's.addEventListener("input",f)})();</script>')
    main = '<main id="main">' + hero + topics + featured + learn + listing + cta + js + '</main>'
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": title, "description": desc, "url": SITE + "/blog/"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog/"}]}]}
    h = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda m: '<script type="application/ld+json">' + json.dumps(ld) + '</script>', tpl, count=1, flags=re.S)
    h = h.replace('[META TITLE]', e(title)).replace('[META DESCRIPTION]', e(desc)).replace('https://insyncea.com/blog/[post-slug]/', SITE + '/blog/')
    h = h.replace('content="article"', 'content="website"').replace(SITE + '/assets/blog/[IMAGE-FILE]', SITE + '/assets/og-image.png')
    h = re.sub(r'<main id="main">.*</main>', lambda m: main, h, flags=re.S)
    h = h.replace('<script src="/assets/related-articles.js" defer></script>', '')
    h = h.replace('<link rel="stylesheet" href="/assets/related-articles.css">', '<link rel="stylesheet" href="/assets/related-articles.css"><link rel="stylesheet" href="/assets/blog-hub.css">')
    robots = '<meta name="robots" content="index,follow,max-image-preview:large">' if posts else '<meta name="robots" content="noindex">'
    h = h.replace('<link rel="canonical"', robots + '<link rel="canonical"', 1)
    out = ROOT / 'blog' / 'index.html'; out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists() or out.read_text(encoding='utf-8') != h: out.write_text(h, encoding='utf-8'); print('built /blog/ (' + str(len(posts)) + ' article(s))')


def add_toc(body_html):
    """Gives each H2 and H3 an id, and returns the contents list (empty if there are fewer than 3 H2 headings)."""
    used, items = set(), []
    def slug(text):
        base = re.sub(r'[^a-z0-9]+', '-', re.sub(r'<[^>]+>', '', html.unescape(text)).lower()).strip('-') or 'section'
        s_, n = base, 2
        while s_ in used: s_ = f'{base}-{n}'; n += 1
        used.add(s_); return s_
    def sub(m):
        lvl, text = m.group(1), m.group(2)
        sid = slug(text); items.append((lvl, sid, re.sub(r'<[^>]+>', '', text).strip()))
        return f'<h{lvl} id="{sid}">{text}</h{lvl}>'
    out = re.sub(r'<h([23])>(.*?)</h\1>', sub, body_html, flags=re.S)
    groups = []
    for lvl, sid, text in items:
        if lvl == '2' or not groups: groups.append([(sid, text), []])
        else: groups[-1][1].append((sid, text))
    if sum(1 for i in items if i[0] == '2') < 3: return out, ''
    link = lambda sid, text: f'<a href="#{sid}">{e(text)}</a>'
    lis = ''.join('<li>' + link(*head) + ('<ol>' + ''.join('<li>' + link(*s2) + '</li>' for s2 in subs) + '</ol>' if subs else '') + '</li>' for head, subs in groups)
    return out, '<aside class="toc-side"><details class="toc-d" open><summary>On this page</summary><ol>' + lis + '</ol></details></aside>'


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
        if d > TODAY: print('scheduled for', d, '-', f.name); continue
        img = '/' + str(meta['image']).lstrip('/')
        alt = meta.get('image_alt') or title
        cat = meta.get('category') or 'Blog'
        excerpt = meta.get('excerpt') or md
        tags, aud, svcs = as_list(meta.get('tags')), as_list(meta.get('audience')), as_list(meta.get('services'))
        kws = [k for k in [meta.get('focus_keyword')] + as_list(meta.get('keywords')) if k]
        html_body = markdown.markdown(body, extensions=['extra', 'sane_lists']).replace('<h1', '<h2').replace('</h1>', '</h2>')
        html_body, toc = add_toc(html_body)
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
        h = re.sub(r'<!--toc:start-->.*?<!--toc:end-->', lambda m: '<!--toc:start-->' + toc + '<!--toc:end-->', h, flags=re.S)
        if toc: h = h.replace('<div class="post-layout">', '<div class="post-layout has-toc">', 1)
        out = ROOT / 'blog' / slug / 'index.html'; out.parent.mkdir(parents=True, exist_ok=True)
        if not out.exists() or out.read_text(encoding='utf-8') != h: out.write_text(h, encoding='utf-8'); print('built', url)
        urls.append((url, d))
        made.append({'url': url, 'title': title, 'excerpt': excerpt, 'image': img, 'imageAlt': alt, 'category': cat,
                     'tags': tags, 'audience': aud, 'services': svcs, 'date': d, 'auto': True})
    keep = [p for p in old if not p.get('auto') and p.get('url') not in {m['url'] for m in made}]
    new = json.dumps({'posts': keep + made}, indent=2, ensure_ascii=False) + '\n'
    if not pj.exists() or pj.read_text(encoding='utf-8') != new: pj.write_text(new, encoding='utf-8'); print('updated assets/posts.json')
    blog_index(tpl, keep + made)
    if keep or made: urls.insert(0, ('/blog/', max([p.get('date') or '' for p in keep + made] or [''])[:10] or '2026-01-01'))
    sm = ROOT / 'sitemap.xml'
    if sm.exists():
        s = sm.read_text(encoding='utf-8'); add = ''
        for u, d in urls:
            if f'<loc>{SITE}{u}</loc>' not in s: add += f'  <url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod></url>\n'
        if add and '</urlset>' in s: sm.write_text(s.replace('</urlset>', add + '</urlset>'), encoding='utf-8'); print('added to sitemap.xml')
    print('done,', len(made), 'article(s) built')

if __name__ == '__main__': main()
