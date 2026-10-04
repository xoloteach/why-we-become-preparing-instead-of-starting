from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
root=Path(__file__).resolve().parent
W,H=1280,720;paper='#F7F4EE';ink='#16150F';rust='#C8623C'
im=Image.new('RGB',(W,H),ink);d=ImageDraw.Draw(im)
d.rectangle((0,0,580,H),fill=paper)
font=lambda size,w='Black':ImageFont.truetype(str(root/'assets/fonts'/f'Montserrat-{w}.ttf'),size)
d.text((50,36),'WHY WE BECOME',font=font(24),fill=ink)
art=Image.open(root/'v2/layers/s03_p7.png').convert('RGBA')
box=json.loads((root/'v2/upscale_report.json').read_text())['03-7']['bbox']
art=art.crop(box);art.thumbnail((535,545),Image.Resampling.LANCZOS)
im.paste(art,(round((580-art.width)/2),145),art)
d=ImageDraw.Draw(im)
d.text((635,152),'PREPARING',font=font(66),fill=paper)
d.text((635,250),'OR',font=font(66),fill=rust)
d.text((635,348),'HIDING?',font=font(88),fill=paper)
d.rectangle((636,489,1190,497),fill=rust)
d.text((638,542),'MAKE THE FIRST ATTEMPT.',font=font(23,'ExtraBold'),fill=paper)
im.save(root/'thumbnail.png')
print('Thumbnail created: 1280×720, supplied artwork and canonical typography/palette')
