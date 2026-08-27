"""Resize source photography into responsive WebP sets under assets/img/.

Sources are listed per production in content/site.json as paths relative to
the repo root, so masters can live anywhere (Zoe's Squarespace export, the
original scrape) without the templates caring.
"""
import json, os, shutil
from PIL import Image, ImageOps

WIDTHS = [640, 1280, 2000]
BIG = 2800          # extra step, only for originals large enough to fill it
BIG_MIN = 3000
QUALITY = 82
OUT = 'assets/img'

site = json.load(open('content/site.json'))
manifest = {}

def emit(src, slug, idx, prefix='p'):
    if not os.path.exists(src):
        print('  MISSING', src)
        return None
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)          # honour camera rotation
    im = im.convert('RGB')
    w, h = im.size
    d = os.path.join(OUT, slug)
    os.makedirs(d, exist_ok=True)
    base = '%s%02d' % (prefix, idx)
    targets = sorted({min(t, w) for t in WIDTHS})
    if w >= BIG_MIN:
        targets.append(min(BIG, w))
    made = []
    for tw in sorted(set(targets)):
        th = round(h * tw / w)
        r = im if tw == w else im.resize((tw, th), Image.LANCZOS)
        p = os.path.join(d, '%s-%d.webp' % (base, tw))
        r.save(p, 'WEBP', quality=QUALITY, method=6)
        made.append((tw, os.path.relpath(p).replace(os.sep, '/')))
    return {'base': base, 'w': w, 'h': h, 'ratio': round(w / h, 4),
            'sizes': made, 'src': made[-1][1]}

if os.path.isdir(OUT):
    shutil.rmtree(OUT)

for pr in site['projects']:
    entries = []
    for i, src in enumerate(pr['images']):
        e = emit(src, pr['slug'], i)
        if e:
            entries.append(e)
    manifest[pr['slug']] = entries
    if entries:
        mx = max(x['w'] for x in entries)
        print('  %-24s %3d images  (largest source %dpx)' % (pr['slug'], len(entries), mx))

h = emit(site['headshot'], '_about', 0, prefix='headshot')
manifest['_about'] = [h] if h else []
json.dump(manifest, open('content/images.json', 'w'), indent=1)
print('total files:', sum(len(os.listdir(os.path.join(OUT, d))) for d in os.listdir(OUT)))
