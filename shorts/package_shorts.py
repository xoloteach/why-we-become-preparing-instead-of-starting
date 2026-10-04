import json,os,shutil,zipfile,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'shorts/output'
man=json.load(open(O/'shorts-manifest.json'))
for m in man:
 slug=m['file'].replace('short-','').replace('.mp4','')
 d=O/'deliver'/slug;d.mkdir(parents=True,exist_ok=True)
 shutil.move(str(O/m['file']),str(d/'short.mp4'))
 shutil.move(str(O/m['thumbnail']),str(d/'thumbnail.png'))
 for extra in [slug+'.ass',slug+'-script.md',slug+'-seo.md',slug+'-words.json',slug+'-technical-qa.json',slug+'.wav']:
  if (O/extra).exists():shutil.move(str(O/extra),str(d/extra))
 with zipfile.ZipFile(O/'shorts-source-v1.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in ['shorts/build_shorts.py','shorts/render_shorts.py','shorts/package_shorts.py','.github/workflows/render-shorts.yml','v2/render_motion.py','v2/scene_plan.json','script.txt','script_alignment.json','voiceover.json','timeline.json','requirements.txt']:
   f=R/p
   if f.exists():z.write(f,p)
print('packaged',[m['file'] for m in man])
