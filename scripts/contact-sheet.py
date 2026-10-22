"""Create a labelled 35-card sheet; legacy images go only to a private output."""
import argparse,json,subprocess,textwrap
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('output'); p.add_argument('--legacy-root',type=Path); args=p.parse_args()
rows=json.loads((root/'docs/image-rights.json').read_text())['images']
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
sheet=Image.new('RGB',(1400,7*340+85),'#f4f0e7'); d=ImageDraw.Draw(sheet)
d.text((20,15),'Чысты чысцец · 35 картак · 2026-10-22',font=font,fill='#263a30')
d.text((20,42),'Прыватны агляд старых выяў; правы не пацверджаныя' if args.legacy_root else 'Прапанова: толькі пацверджаныя выявы; астатнія чакаюць праверкі',font=font,fill='#75452e')
for i,r in enumerate(rows):
    x=(i%5)*280+20;y=(i//5)*340+85
    box=(x+40,y,x+216,y+220); d.rectangle(box,fill='#dfe4d5')
    src=(args.legacy_root/r['previous']['path']) if args.legacy_root else (root/r['web']['src'] if r['web'] else None)
    if src:
        im=Image.open(src).convert('RGB');im.thumbnail((176,220),Image.Resampling.LANCZOS)
        sheet.paste(im,(box[0]+(176-im.width)//2,box[1]+(220-im.height)//2))
    else:
        d.text((x+65,y+90),'Без выявы',font=font,fill='#526244')
    for j,line in enumerate(textwrap.wrap(r['id']+' · '+r['name'],24)):
        d.text((x,y+228+j*19),line,font=small,fill='#263a30')
    d.text((x,y+306),r['status'],font=small,fill='#75452e')
Path(args.output).parent.mkdir(parents=True,exist_ok=True)
sheet.save(args.output,quality=90)
