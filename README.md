# zoecraigadams.com

**Live: https://legertom.github.io/zoecraigadams.com/**

Static site for **Zoë Adams**, theatre director. Plain HTML + CSS, no build step
required to deploy — GitHub Pages serves the committed files as-is.

Design direction: contemporary commercial Broadway marketing — marquee bulbs,
a poster-rack of key art with a brand colour per production, heavy condensed
caps, and a real billing block for credits.

## Where the photography comes from

Masters live in `Zoë Website Photos/` (gitignored — Zoë's Squarespace export
plus the full-resolution originals for the 2026 shows). Each production's
`images` array in `content/site.json` holds paths to its source files, so
masters can sit anywhere without the templates caring.

To add or change photos for a show: put the files somewhere, list their paths
in that project's `images` array (first one becomes the hero), then rebuild:

```bash
python3 tools/prepare_images.py && python3 tools/build.py
```

A production with an empty `images` array renders a marquee "Coming Soon"
teaser poster instead, so a show can be announced before it is shot; adding
photos swaps in real key art with no template edits.

## Editing content

Everything lives in [`content/site.json`](content/site.json): bio, statement,
email, résumé link, and the 12 productions (order, venue, year, credits, awards,
and the `accent` brand colour used for the duotone and card).

## Commands

```bash
python3 tools/prepare_images.py   # resize masters into assets/img (responsive WebP)
python3 tools/build.py            # render all HTML
python3 -m http.server 4173       # preview at http://localhost:4173
```

## Structure

```
index.html            work / poster rack
about/  contact/      about + contact
work/<slug>/          12 production pages
assets/               css, js, favicon, responsive images
content/site.json     ← the editable content model
content/images.json   generated image manifest (do not hand-edit)
tools/                generator scripts
```

Legacy Squarespace URLs (`/contact`, `/work/peaks-6dwyp-k2ktm`, …) are kept as
redirect stubs so existing links and search results still land correctly.

## Deploying

Push to `main`; GitHub Pages builds automatically and serves from the repo root
(usually live within a minute). CSS and JS are CDN-cached for about 10 minutes,
so a hard refresh may be needed to see a style change immediately. All asset paths are
relative, so the site works from a project subpath or a custom domain without
changes. To use the custom domain, add a `CNAME` file containing
`zoecraigadams.com` and point DNS at GitHub Pages.
