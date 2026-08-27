"""Resize scraped production stills into responsive WebP sets under assets/img/."""
import json, os, shutil
from PIL import Image

WIDTHS = [640, 1280, 2000]
QUALITY = 80
SRC = 'scrape/images'
OUT = 'assets/img'

site = json.load(open('content/site.json'))
manifest = {}

def emit(src_file, slug, idx, prefix='p'):
    src = os.path.join(SRC, src_file)
    if not os.path.exists(src): return None
    im = Image.open(src).convert('RGB')
    w, h = im.size
    d = os.path.join(OUT, slug); os.makedirs(d, exist_ok=True)
    base = f'{prefix}{idx:02d}'
    # never upscale, but always keep the native width as the largest step
    targets = sorted({min(tw, w) for tw in WIDTHS})
    made = []
    for tw2 in targets:
        th = round(h * tw2 / w)
        r = im if tw2 == w else im.resize((tw2, th), Image.LANCZOS)
        p = os.path.join(d, f'{base}-{tw2}.webp')
        r.save(p, 'WEBP', quality=QUALITY, method=6)
        made.append((tw2, os.path.relpath(p).replace(os.sep, '/')))
    return {'base': base, 'w': w, 'h': h, 'ratio': round(w/h, 4), 'sizes': made,
            'src': made[-1][1], 'srcset': ', '.join(f'/{p} {tw}w' for tw, p in made)}

if os.path.isdir(OUT): shutil.rmtree(OUT)
for pr in site['projects']:
    entries = []
    for i, f in enumerate(pr['images']):
        e = emit(f, pr['slug'], i)
        if e: entries.append(e)
    manifest[pr['slug']] = entries
    if entries: print(f"  {pr['slug']:22} {len(entries):3} images")

h = emit(site['headshot'], '_about', 0, prefix='headshot')
manifest['_about'] = [h] if h else []
json.dump(manifest, open('content/images.json', 'w'), indent=1)
print('total files:', sum(len(os.listdir(os.path.join(OUT,d))) for d in os.listdir(OUT)))
