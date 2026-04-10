# InSyncEA Website

Professional Executive Assistant website for InSyncEA, built with HTML and hosted on Cloudflare Pages.

## About

InSyncEA provides premium Executive Assistant and Executive Virtual Assistant services including calendar management, email management, travel coordination, project management and more. Available globally.

## Structure

```
index.html        — Main website (all pages)
admin/            — Blog editor login
_data/            — Website content data files
_posts/           — Blog posts (add new .md files here)
_redirects        — Cloudflare routing rules
package.json      — Build configuration
```

## Adding a Blog Post

1. Go to the `_posts` folder
2. Click Add file → Create new file
3. Name it: `YYYY-MM-DD-your-post-title.md`
4. Add this at the top:

```
---
title: "Your Post Title"
date: 2026-04-10
category: "Executive Assistant Tips"
excerpt: "Short summary of your post"
seo_description: "Description for Google search results"
---

Write your blog post content here.
```

5. Click Commit new file — Cloudflare deploys automatically

## Contact

hello@insync-ea.com
