"""Render a show's stills cropped exactly as the 2:3 poster card crops them."""
import json, sys, os
from PIL import Image, ImageDraw
sp, slug = sys.argv[1], sys.argv[2]
BOX = 2/3.0
m = json.load(open('content/images.json'))
ents = m[slug]
CW, CH = 250, int(250/BOX)
cols = min(6, len(ents)); rows = (len(ents)+cols-1)//cols
sheet = Image.new('RGB', (cols*(CW+10), rows*(CH+30)), (12,11,14))
dr = ImageDraw.Draw(sheet)
for i, e in enumerate(ents):
    im = Image.open(e['sizes'][-1][1]).convert('RGB'); w,h = im.size
    if w/h > BOX:                      # crop sides
        nw = int(h*BOX); x0 = (w-nw)//2; box = (x0,0,x0+nw,h)
    else:                              # crop top/bottom
        nh = int(w/BOX); y0 = int((h-nh)*0.35); box = (0,y0,w,y0+nh)
    im = im.crop(box).resize((CW,CH), Image.LANCZOS)
    x=(i%cols)*(CW+10)+5; y=(i//cols)*(CH+30)+5
    sheet.paste(im,(x,y)); dr.rectangle([x,y,x+CW,y+CH], outline=(90,80,70))
    dr.text((x+4,y+CH+6), '[%d] %s' % (i, os.path.basename(e['sizes'][0][1])), fill=(235,200,120))
out = os.path.join(sp, 'card-%s.jpg' % slug); sheet.save(out, quality=90); print(out)
