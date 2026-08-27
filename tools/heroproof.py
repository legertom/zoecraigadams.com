"""Render each production hero exactly as the browser will crop it."""
import json, sys, os
from PIL import Image, ImageDraw
sp=sys.argv[1]; BOX=float(sys.argv[2]) if len(sys.argv)>2 else 2.45
m=json.load(open('content/images.json')); site=json.load(open('content/site.json'))
def hero_of(pr, ents):
    if not ents: return None,0
    i=pr.get('hero_index')
    if isinstance(i,int) and 0<=i<len(ents): return ents[i],i
    for n,e in enumerate(ents):
        if e['ratio']>=1.4: return e,n
    return ents[0],0
def parse(f):
    a,b=(f or '50% 35%').split(); return int(a.strip('%'))/100, int(b.strip('%'))/100
picks=[]
for p in site['projects']:
    e=m.get(p['slug']) or []
    h,i=hero_of(p,e)
    if h: picks.append((p['slug'],h,i,parse(p.get('focal'))))
CW,CH=470,int(470/BOX); cols=3; rows=(len(picks)+cols-1)//cols
sheet=Image.new('RGB',(cols*(CW+10),rows*(CH+34)),(12,11,14)); dr=ImageDraw.Draw(sheet)
for k,(slug,e,i,(fx,fy)) in enumerate(picks):
    im=Image.open(e['sizes'][-1][1]).convert('RGB'); w,h=im.size
    if w/h > BOX:
        nw=int(h*BOX); x0=int((w-nw)*fx); box=(x0,0,x0+nw,h)
    else:
        nh=int(w/BOX); y0=int((h-nh)*fy); box=(0,y0,w,y0+nh)
    im=im.crop(box).resize((CW,CH),Image.LANCZOS)
    x=(k%cols)*(CW+10)+5; y=(k//cols)*(CH+34)+5
    sheet.paste(im,(x,y)); dr.rectangle([x,y,x+CW,y+CH],outline=(90,80,70))
    dr.text((x+3,y+CH+6),f'{slug}  hero[{i}]  focal {int(fx*100)}%/{int(fy*100)}%',fill=(235,200,120))
out=os.path.join(sp,'hero-proof.jpg'); sheet.save(out,quality=90); print(out)
