"""Render every still of one show cropped as the wide hero will crop it."""
import json, sys, os
from PIL import Image, ImageDraw
sp, slug = sys.argv[1], sys.argv[2]
BOX = float(sys.argv[3]) if len(sys.argv)>3 else 2.45
fy  = float(sys.argv[4]) if len(sys.argv)>4 else 0.35
m = json.load(open('content/images.json')); ents = m[slug]
CW, CH = 420, int(420/BOX); cols = 3
rows = (len(ents)+cols-1)//cols
sheet = Image.new('RGB', (cols*(CW+10), rows*(CH+30)), (12,11,14)); dr = ImageDraw.Draw(sheet)
for i, e in enumerate(ents):
    im = Image.open(e['sizes'][-1][1]).convert('RGB'); w,h = im.size
    if w/h > BOX:
        nw=int(h*BOX); x0=(w-nw)//2; box=(x0,0,x0+nw,h)
    else:
        nh=int(w/BOX); y0=int((h-nh)*fy); box=(0,y0,w,y0+nh)
    im = im.crop(box).resize((CW,CH), Image.LANCZOS)
    x=(i%cols)*(CW+10)+5; y=(i//cols)*(CH+30)+5
    sheet.paste(im,(x,y)); dr.rectangle([x,y,x+CW,y+CH], outline=(90,80,70))
    dr.text((x+4,y+CH+6), '[%d] ratio %.2f  %s' % (i, e['ratio'], os.path.basename(e['sizes'][0][1])), fill=(235,200,120))
out=os.path.join(sp,'wide-%s.jpg'%slug); sheet.save(out,quality=90); print(out)
