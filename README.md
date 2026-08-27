# zoecraigadams.com

Static site for **Zoë Adams**, theatre director. Plain HTML + CSS, no build step
required to deploy — GitHub Pages serves the committed files as-is.

Design direction: contemporary commercial Broadway marketing — marquee bulbs,
a poster-rack of key art with a brand colour per production, heavy condensed
caps, and a real billing block for credits.

## Adding photography for an incoming production

Both **To Have and to Hold** and **Cinderella** are already in the site as
"Coming Soon" teaser posters. When the images arrive:

1. Drop the photos into `scrape/images/` named with the show's prefix, then list
   the filenames under that project's `images` array in `content/site.json`.
   (Or copy them anywhere and point `images` at the paths.)
2. Fill in the `TODO` fields in `content/site.json` for that project — `venue`,
   `location`, `year`, `byline`, `credits`, `photography`.
3. Rebuild:

```bash
python3 tools/prepare_images.py && python3 tools/build.py
```

The teaser poster is replaced by real key art automatically — no template edits.
A production with an empty `images` array always renders the teaser treatment,
so shows can be announced before they are shot.

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

Push to `main`; GitHub Pages serves from the repo root. All asset paths are
relative, so the site works from a project subpath or a custom domain without
changes. To use the custom domain, add a `CNAME` file containing
`zoecraigadams.com` and point DNS at GitHub Pages.
