#!/usr/bin/env python3
"""Render zoecraigadams.com to static HTML for GitHub Pages.

Every asset path is relative, so the output works unchanged from a repo
root, a project subpath (user.github.io/repo/), or a custom domain.
"""
import json, os, shutil, html, datetime

TODAY = datetime.date.today().isoformat()

SITE = json.load(open('content/site.json'))
IMGS = json.load(open('content/images.json'))
NAV = [('Work', ''), ('About', 'about/'), ('Contact', 'contact/')]
STAR = '&#9733;'
ARROW = '&#8599;'

def e(s):
    return html.escape(str(s or ''), quote=True)

def rel(depth):
    return '../' * depth

def pic(entry, sizes, alt='', eager=False, depth=0, cls=''):
    if not entry:
        return ''
    p = rel(depth)
    srcset = ', '.join(p + path + ' ' + str(w) + 'w' for w, path in entry['sizes'])
    big = p + entry['sizes'][-1][1]
    load = 'eager' if eager else 'lazy'
    prio = ' fetchpriority="high"' if eager else ''
    klass = ' class="' + cls + '"' if cls else ''
    return ('<img src="' + big + '" srcset="' + srcset + '" sizes="' + sizes + '"'
            ' width="' + str(entry['w']) + '" height="' + str(entry['h']) + '"'
            ' loading="' + load + '"' + prio + ' decoding="async" alt="' + e(alt) + '"'
            + klass + '>')

FONTS = ('https://fonts.googleapis.com/css2?'
         'family=Archivo:ital,wdth,wght@0,62..125,400..800;1,62..125,400..700'
         '&family=Big+Shoulders+Display:wght@600..900&display=swap')

def head(title, desc, depth, extra='', body_style=''):
    p = rel(depth)
    style = ' style="' + body_style + '"' if body_style else ''
    return ('<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>' + e(title) + '</title>\n'
        '<meta name="description" content="' + e(desc) + '">\n'
        '<meta name="theme-color" content="#08070A">\n'
        '<meta property="og:title" content="' + e(title) + '">\n'
        '<meta property="og:description" content="' + e(desc) + '">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:site_name" content="Zo&euml; Adams">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<link rel="icon" href="' + p + 'assets/favicon.svg" type="image/svg+xml">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="' + FONTS + '" rel="stylesheet">\n'
        '<link rel="stylesheet" href="' + p + 'assets/css/site.css">\n'
        '<script>document.documentElement.className+=" js"</script>\n'
        + extra + '</head>\n<body' + style + '>\n'
        '<a class="skip" href="#main">Skip to content</a>\n')

def nav(depth, current, solid=True):
    p = rel(depth)
    items = ''
    for lbl, href in NAV:
        cur = ' aria-current="page"' if href == current else ''
        items += '<li><a href="' + p + href + '"' + cur + '>' + lbl + '</a></li>'
    cls = 'nav nav--solid' if solid else 'nav'
    return ('<header class="' + cls + '">'
            '<a class="nav__home" href="' + p + '">ZO&Euml; <span>ADAMS</span></a>'
            '<nav aria-label="Primary"><ul class="nav__links">' + items + '</ul></nav></header>')

def foot(depth):
    p = rel(depth)
    return ('<footer class="foot"><div class="wrap"><div class="foot__grid">'
        '<p class="foot__name">ZO&Euml; <span>ADAMS</span></p>'
        '<ul class="foot__links">'
        '<li><a href="' + p + '">Work</a></li>'
        '<li><a href="' + p + 'about/">About</a></li>'
        '<li><a href="' + p + 'contact/">Contact</a></li>'
        '<li><a href="mailto:' + SITE['email'] + '">Email</a></li></ul></div>'
        '<p class="foot__fine">Theatre Director ' + STAR + ' Brooklyn, New York '
        + STAR + ' Member, Stage Directors and Choreographers Society</p>'
        '</div></footer>\n'
        '<script src="' + p + 'assets/js/site.js" defer></script>\n</body>\n</html>')


def running(pr):
    r = pr.get('run')
    return bool(r and r['start'] <= TODAY <= r['end'])

def now_band(pr, depth, show_title=True):
    """Marquee band for a production currently on stage."""
    r = pr.get('run')
    if not r:
        return ''
    venue = ' &middot; '.join(e(x) for x in (pr['venue'], pr['location']) if x)
    cta = ''
    if pr.get('tickets'):
        cta = ('<div class="now__cta"><a class="btn btn--ticket" href="' + e(pr['tickets'])
               + '" target="_blank" rel="noopener">Tickets</a></div>')
    href = rel(depth) + 'work/' + pr['slug'] + '/'
    return ('<section class="now" data-until="' + r['end'] + '" style="--show:'
        + pr['accent'] + '"><div class="wrap"><div class="now__inner"><div class="now__text">'
        '<p class="now__tag"><span class="now__pulse"></span>Now Playing Off-Broadway</p>'
        + ('<h2 class="now__title"><a href="' + href + '">' + e(pr['title']) + '</a></h2>'
           if show_title else '<h2 class="now__title">' + r['label'] + '</h2>')
        + ('<p class="now__meta"><b>' + r['label'] + '</b><br>' + venue if show_title
           else '<p class="now__meta">' + venue)
        + ('<br>' + e(r['note']) if r.get('note') else '') + '</p>'
        '</div>' + cta + '</div></div></section>')

def press_block(pr):
    items = pr.get('press') or []
    if not items:
        return ''
    out = ''
    for q in items:
        attr = '<b>' + e(q['outlet']) + '</b>'
        if q.get('critic'):
            attr += '<span>' + e(q['critic']) + '</span>'
        if q.get('url'):
            attr += ('<a href="' + e(q['url']) + '" target="_blank" rel="noopener">'
                     'Read the review</a>')
        out += ('<div class="press__item"><p class="press__quote">&ldquo;'
                + e(q['quote']) + '&rdquo;</p><p class="press__attr">' + attr + '</p></div>')
    return '<section class="press"><div class="wrap">' + out + '</div></section>'

def bits(pr, tag='span'):
    out = ''
    for b in (pr['venue'], pr['location']):
        if b:
            out += '<' + tag + '>' + e(b) + '</' + tag + '>'
    if pr['year']:
        out += '<i>' + e(pr['year']) + '</i>'
    return out

def write(path, content):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    open(path, 'w', encoding='utf-8').write(content)

# ------------------------------------------------------------------ home --
def build_home():
    lead = None
    for p in SITE['projects']:
        if IMGS.get(p['slug']):
            lead = IMGS[p['slug']][0]
            break

    cards = ''
    for i, pr in enumerate(SITE['projects'], 1):
        gal = IMGS.get(pr['slug']) or []
        badge = ''
        if pr.get('awards'):
            badge = '<span class="card__badge">' + STAR + ' Award Winner</span>'
        venue = ' &middot; '.join(e(x) for x in (pr['venue'], pr['location']) if x)
        if gal:
            art = ('<div class="card__art">'
                   + pic(gal[0], '(min-width:70rem) 22vw, (min-width:44rem) 33vw, 50vw',
                         alt=pr['title'] + ' - production photograph', eager=(i <= 4))
                   + '<span class="card__wash"></span><span class="card__shade"></span>' + badge
                   + '<div class="card__plate">'
                   + '<p class="card__year">' + e(pr['year'] or 'Forthcoming') + '</p>'
                   + '<h3 class="card__title">' + e(pr['title']) + '</h3>'
                   + ('<p class="card__venue">' + venue + '</p>' if venue else '')
                   + '</div></div>')
        else:
            tag = 'Now Playing' if running(pr) else 'Coming Soon'
            art = ('<div class="card__art bulbs"><div class="teaser">'
                   '<p class="teaser__tag">' + STAR + ' ' + tag + '</p>'
                   '<h3 class="teaser__title">' + e(pr['title']) + '</h3>'
                   '<div class="teaser__rule"></div>'
                   '<p class="teaser__note">' + (venue + '<br>' if venue else '')
                   + 'Production photography to come</p></div></div>')
        tcls = '' if gal else ' card--teaser'
        cards += ('<a class="card reveal' + tcls + '" style="--show:' + pr['accent'] + '" '
                  'href="work/' + pr['slug'] + '/">' + art + '</a>')

    hero_bg = ''
    if lead:
        hero_bg = '<div class="hero__bg">' + pic(lead, '100vw', alt='', eager=True) + '</div>'

    tag = ('Zo&euml; creates theatre to spark <b>imagination</b> and open hearts '
           'to the magic of <b>transformation</b>.')

    ld = json.dumps({"@context": "https://schema.org", "@type": "Person",
        "name": "Zoë Adams", "jobTitle": "Theatre Director",
        "email": "mailto:" + SITE['email'], "url": "https://" + SITE['domain'] + "/",
        "description": SITE['tagline']}, ensure_ascii=False)

    body = (nav(0, '', solid=False) + '\n<main id="main">\n'
        '<section class="hero">' + hero_bg
        + '<div class="hero__wash"></div><div class="hero__veil"></div>'
        '<div class="hero__inner">'
        '<p class="kicker kicker--paper rise rise--1">'
        '<span class="kicker__star">' + STAR + '</span> Theatre Director '
        '<span class="kicker__star">' + STAR + '</span></p>'
        '<h1 class="slab hero__name rise rise--2"><span>Zo&euml;</span>'
        '<span class="b">Adams</span></h1>'
        '<div class="hero__rule rise rise--3"></div>'
        '<p class="hero__tag rise rise--3">' + tag + '</p>'
        '<p class="hero__strip rise rise--4">'
        '<span>Brooklyn, New York</span><i>' + STAR + '</i>'
        '<span>Drama League Directing Fellow 2024&ndash;26</span><i>' + STAR + '</i>'
        '<span>Member SDC</span></p>'
        '</div></section>\n'
        + ''.join(now_band(p, 0) for p in SITE['projects'] if running(p)) +
        '<section class="section" id="work"><div class="wrap">'
        '<div class="section__head">'
        '<h2 class="slab section__title">Selected Work</h2>'
        '<p class="section__count">' + str(len(SITE['projects'])) + ' Productions</p></div>'
        '<div class="rack">' + cards + '</div></div></section>\n</main>\n' + foot(0))

    write('index.html', head('Zoë Adams — Theatre Director', SITE['tagline'], 0,
          '<script type="application/ld+json">' + ld + '</script>\n') + body)

# -------------------------------------------------------------- projects --
def build_projects():
    ps = SITE['projects']
    for i, pr in enumerate(ps):
        gal = IMGS.get(pr['slug']) or []
        byline = ' &middot; '.join(e(b) for b in pr['byline'])
        awards = ''
        if pr.get('awards'):
            lis = ''.join('<li>' + STAR + ' ' + e(a) + '</li>' for a in pr['awards'])
            awards = '<ul class="pawards">' + lis + '</ul>'

        meta = ('<p class="pbar">' + bits(pr) + '</p>'
                + ('<p class="pbyline">' + byline + '</p>' if byline else '') + awards)

        if gal:
            hero = ('<section class="phero"><div class="phero__bg">'
                + pic(gal[0], '100vw', alt='', eager=True, depth=2)
                + '</div><span class="phero__wash"></span><span class="phero__veil"></span>'
                '<div class="phero__inner">'
                '<p class="kicker">' + STAR + ' Production ' + ('%02d' % (i + 1)) + '</p>'
                '<h1 class="slab ptitle">' + e(pr['title']) + '</h1>' + meta
                + '</div></section>')
        else:
            hero = ('<section class="phero phero--teaser"><div class="phero__inner">'
                '<p class="kicker">' + STAR + ' '
                + ('Now Playing Off-Broadway' if running(pr) else 'Coming Soon') + '</p>'
                '<h1 class="slab ptitle">' + e(pr['title']) + '</h1>' + meta
                + '</div></section>'
                '<div class="wrap"><div class="teaser-band bulbs">'
                '<div class="teaser"><p class="teaser__tag">' + STAR + ' Key art in production</p>'
                '<h2 class="teaser__title">Production stills are on their way.</h2>'
                '<div class="teaser__rule"></div>'
                '<p class="teaser__note">Check back shortly</p></div></div></div>')

        figs = ''
        for n, g in enumerate(gal[1:], 1):
            wide = ' wide' if (n % 5 == 0 or g['ratio'] > 2.1) else ''
            figs += ('<figure class="reveal' + wide + '">'
                     + pic(g, '(min-width:44rem) 50vw, 100vw',
                           alt=pr['title'] + ' - production photograph ' + str(n + 1), depth=2)
                     + '</figure>')
        gallery = '<div class="wrap"><div class="gallery">' + figs + '</div></div>' if figs else ''

        band = now_band(pr, 2, show_title=False) if running(pr) else ''
        press = press_block(pr)

        billing = ''
        if pr['credits'] or pr['byline'] or pr.get('cast'):
            pairs = ''
            for c in pr['credits']:
                pairs += ('<div class="pair"><dt class="role">' + e(c['role']) + '</dt> '
                          '<dd>' + e(c['name']) + '</dd></div>')
            cast = ''
            if pr.get('cast'):
                cp = ''
                for c in pr['cast']:
                    cp += ('<div class="pair"><dt class="role">' + e(c['role']) + '</dt> '
                           '<dd class="name">' + e(c['name']) + '</dd></div>')
                cast = '<span class="block__cast"><dl>' + cp + '</dl></span>'
            lead = ('<span class="block__lead">' + byline + '</span>') if byline else ''
            photo = ''
            if pr.get('photography'):
                photo = ('<span class="block__photo">Photography by '
                         + e(pr['photography']) + '</span>')
            billing = ('<section class="billing"><div class="wrap">'
                '<div class="billing__head">'
                '<p class="kicker">' + STAR + ' The Company ' + STAR + '</p>'
                '<p class="billing__presents">' + e(pr['title']) + '</p></div>'
                '<div class="block">' + lead + cast
                + ('<dl>' + pairs + '</dl>' if pairs else '')
                + '<span class="block__dir">Directed by <b>Zo&euml; Adams</b></span>'
                + photo + '</div></div></section>')

        def pg(p2, dirn, cls):
            if not p2:
                return '<span class="pager__item pager__item--' + cls + ' pager__item--empty"></span>'
            return ('<a class="pager__item pager__item--' + cls + '" href="../' + p2['slug'] + '/">'
                    '<p class="pager__dir">' + dirn + '</p>'
                    '<p class="pager__name">' + e(p2['title']) + '</p></a>')
        prev = ps[i - 1] if i > 0 else None
        nxt = ps[i + 1] if i < len(ps) - 1 else None
        pager = ('<nav class="pager" aria-label="More productions">'
                 + pg(prev, 'Previous', 'prev') + pg(nxt, 'Next', 'next') + '</nav>')

        desc = pr['title']
        if pr['venue']:
            desc += ' at ' + pr['venue']
        if pr['year']:
            desc += ', ' + pr['year']
        desc += '. Directed by Zoë Adams.'

        body = (nav(2, '') + '<main id="main">' + hero + band + press + gallery
                + billing + '</main>' + pager + foot(2))
        write('work/' + pr['slug'] + '/index.html',
              head(pr['title'] + ' — Zoë Adams', desc, 2,
                   body_style='--show:' + pr['accent']) + body)

# ----------------------------------------------------------------- about --
def build_about():
    hs = (IMGS.get('_about') or [None])[0]
    paras = ''
    for n, t in enumerate(SITE['bio']):
        cls = ' class="lead"' if n == 0 else ''
        paras += '<p' + cls + '>' + e(t) + '</p>'
    portrait = ''
    if hs:
        portrait = ('<figure class="about__portrait reveal">'
            + pic(hs, '(min-width:56rem) 32vw, 100vw', alt='Zoë Adams', depth=1)
            + '<figcaption>Photograph by ' + e(SITE['headshot_credit'])
            + '</figcaption></figure>')

    body = (nav(1, 'about/') + '<main id="main"><div class="wrap"><div class="about">'
        + portrait + '<div>'
        '<p class="kicker">' + STAR + ' About</p>'
        '<blockquote class="quote">Zo&euml; creates theatre to spark <em>imagination</em> '
        'and open hearts to the magic of <em>transformation</em>.</blockquote>'
        '<div class="prose"><p class="lead">' + e(SITE['statement']) + '</p>'
        '<hr class="hr">'
        '<p class="kicker kicker--dim">Biography</p>' + paras
        + '<a class="btn" href="' + e(SITE['resume_url']) + '" target="_blank" '
        'rel="noopener">R&eacute;sum&eacute;</a>'
        '</div></div></div></div></main>' + foot(1))
    write('about/index.html', head('About — Zoë Adams', SITE['statement'][:180], 1) + body)

# --------------------------------------------------------------- contact --
def build_contact():
    body = (nav(1, 'contact/') + '<main id="main"><section class="contact"><div class="wrap">'
        '<p class="kicker">' + STAR + ' Contact</p>'
        '<a class="contact__mail" href="mailto:' + SITE['email'] + '">'
        + SITE['email'] + '</a>'
        '<div class="contact__grid">'
        '<div class="contact__item"><h3>Based In</h3><p>Brooklyn, New York</p></div>'
        '<div class="contact__item"><h3>Union</h3><p>Member, Stage Directors and '
        'Choreographers Society</p></div>'
        '<div class="contact__item"><h3>Representation</h3><p>Inquiries welcome by email</p></div>'
        '<div class="contact__item"><h3>R&eacute;sum&eacute;</h3><p><a href="'
        + e(SITE['resume_url']) + '" target="_blank" rel="noopener">View r&eacute;sum&eacute; '
        + ARROW + '</a></p></div>'
        '</div></div></section></main>' + foot(1))
    write('contact/index.html', head('Contact — Zoë Adams',
          'Contact Zoë Adams, theatre director, Brooklyn NY. ' + SITE['email'], 1) + body)

# ---------------------------------------------------------------- extras --
LEGACY = {
    'contact': 'about/', 'contact-1': 'contact/', 'new-page': '', 'work': '',
    'portfolio-3': '',
    'work/peaks-6dwyp-k2ktm': 'work/ursus-americanus/',
    'work/peaks-6dwyp-k2ktm-j6wl2': 'work/skin-flick-city/',
    'work/peaks-6dwyp-bzp4m': 'work/not-clown/',
    'work/peaks-6dwyp-k2ktm-j6wl2-ace8c': 'work/ragtime/',
    'work/peaks-6dwyp': 'work/the-cherry-orchard/',
    'work/meltdown-live-action-game-about-climate-change': 'work/meltdown/',
    'work/peaks-6dwyp-bzp4m-zhd3k': 'work/in-the-name-of-us/',
    'work/peaks-6dwyp-bzp4m-zhd3k-9yk8d': 'work/krav/',
}

def build_extras():
    for old, new in LEGACY.items():
        depth = old.count('/') + 1
        tgt = rel(depth) + new
        if not tgt:
            tgt = './'
        write(old + '/index.html',
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<title>Redirecting</title><link rel="canonical" href="' + tgt + '">'
            '<meta name="robots" content="noindex">'
            '<meta http-equiv="refresh" content="0; url=' + tgt + '"></head>'
            '<body style="background:#08070A;color:#FAF7F2;font-family:sans-serif;padding:3rem">'
            '<p>This page has moved. <a style="color:#FFC24A" href="' + tgt
            + '">Continue &rarr;</a></p></body></html>')

    urls = ['', 'about/', 'contact/'] + ['work/' + p['slug'] + '/' for p in SITE['projects']]
    sm = ''.join('<url><loc>https://' + SITE['domain'] + '/' + u + '</loc></url>' for u in urls)
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + sm + '</urlset>')
    write('robots.txt', 'User-agent: *\nAllow: /\n\nSitemap: https://'
          + SITE['domain'] + '/sitemap.xml\n')
    write('.nojekyll', '')
    write('assets/favicon.svg',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        '<rect width="64" height="64" fill="#08070A"/>'
        '<text x="32" y="47" font-family="Haettenschweiler,Arial Narrow,sans-serif" '
        'font-size="46" font-weight="900" fill="#FF3B1F" text-anchor="middle">Z</text></svg>')
    write('404.html', head('Not Found — Zoë Adams', 'Page not found', 0) + nav(0, '')
        + '<main id="main"><section class="contact"><div class="wrap">'
        '<p class="kicker">' + STAR + ' 404</p>'
        '<h1 class="slab" style="font-size:clamp(2.6rem,10vw,8rem);font-weight:900">'
        'Off <span style="color:var(--red)">Book</span></h1>'
        '<p class="pbyline">That page is not in this production.</p>'
        '<a class="btn" href="./">Back to the work</a>'
        '</div></section></main>' + foot(0))

if __name__ == '__main__':
    for d in ('work', 'about', 'contact', 'contact-1', 'new-page', 'portfolio-3'):
        if os.path.isdir(d):
            shutil.rmtree(d)
    build_home(); build_projects(); build_about(); build_contact(); build_extras()
    n = 0
    for root, dirs, files in os.walk('.'):
        if 'scrape' in root or '.git' in root:
            continue
        n += len([f for f in files if f.endswith('.html')])
    print('built', n, 'HTML pages')
