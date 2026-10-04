from pathlib import Path
import subprocess,json,re,zipfile,hashlib,math
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parent;video=root/'final.mp4';qa=root/'v2/qa_final';qa.mkdir(parents=True,exist_ok=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]))
(root/'technical-qa.json').write_text(json.dumps(probe,indent=2))
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
tl=json.loads((root/'timeline.json').read_text());sc=json.loads((root/'v2/scene_plan.json').read_text())
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(video),'-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
loud=json.loads(r.stderr[r.stderr.rfind('{'):r.stderr.rfind('}')+1]);(root/'loudness-qa.json').write_text(json.dumps(loud,indent=2))
fps=eval(v['r_frame_rate'],{'__builtins__':{}},{})
checks={'resolution_1920_1080':(v['width'],v['height'])==(1920,1080),'fps_30':fps==30,'duration_matches_narration':abs(float(probe['format']['duration'])-tl['vo_end'])<=.5,'audio_present':a['codec_name']=='aac','integrated_loudness_in_range':-17.5<=float(loud['input_i'])<=-14.5,'non_silent':float(loud['input_i'])>-40,'captions_nonempty':(root/'v2/captions.ass').read_text().count('Dialogue:')>0}
assert all(checks.values()),checks
frames=[]
for s in sc:
 t=max(s['start']+.25,s['end']-.2)
 p=qa/f'scene-{s["id"]:03d}.png'
 subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',f'{t:.4f}','-i',str(video),'-frames:v','1',str(p)],check=True)
 frames.append((s,t,p))
font=ImageFont.truetype(str(root/'assets/fonts/Montserrat-Bold.ttf'),18)
for idx in range(math.ceil(len(frames)/9)):
 sheet=Image.new('RGB',(1920,1188),'#F7F4EE');d=ImageDraw.Draw(sheet)
 for j,(s,t,p) in enumerate(frames[idx*9:(idx+1)*9]):
  col=j%3;row=j//3;x=col*640;y=row*396
  d.text((x+12,y+7),f'SCENE {s["id"]:03d} · {t:.2f}s · {s["art"]} · {s["kind"]}',fill='#16150F',font=font)
  with Image.open(p) as im:sheet.paste(im.resize((640,360),Image.Resampling.LANCZOS),(x,y+36))
 sheet.save(qa/f'contact-{idx+1:02d}.png')
for c in tl['chapters']:
 s=next(s for s in sc if s['chapter']==tl['chapters'].index(c)+1 and s['end']-s['start']>=2)
 t=s['start']+min(1.4,(s['end']-s['start'])*.55)
 subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(t),'-i',str(video),'-frames:v','1',str(qa/f'chapter-{s["chapter"]:02d}.png')],check=True)
for t in [tl['end_card_start']+.9,tl['total']-.1]:
 subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(t),'-i',str(video),'-frames:v','1',str(qa/f'end-{t:.2f}.png')],check=True)
report={'checks':checks,'duration':float(probe['format']['duration']),'voice_duration':tl['vo_end'],'loudness_LUFS':float(loud['input_i']),'true_peak_dBTP':float(loud['input_tp']),'scenes':len(sc),'distinct_panels_used':len({s['art'] for s in sc}),'caption_events':(root/'v2/captions.ass').read_text().count('Dialogue:'),'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'visual_review':'pending agent inspection of actual frames and sampled motion; do not claim full playback review'}
(root/'qa_summary.json').write_text(json.dumps(report,indent=2))
# Reproducible source: explicit allowlist, never private runtime state or logs.
files=[]
for pattern in ['*.py','script.txt','script_paragraphs.json','script_alignment.json','voiceover.json','narration_report.json','timeline.json','panel_inventory.json','requirements.txt','README.md','seo.md','transcript.txt','v2/*.py','v2/*.json','v2/*.md','v2/captions.ass','assets/**/*','inputs/**/*','.github/workflows/*.yml']:
 files.extend(p for p in root.glob(pattern) if p.is_file() and p.suffix not in ['.wav'] and p.name!='mix_raw.wav')
# Narration input is FLAC; root mastered WAV and raw intermediates are intentionally not archived.
with zipfile.ZipFile(root/'source-project-v1.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(set(files)):
  b=p.read_bytes()
  assert not re.search(rb'gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----',b),f'Potential credential in {p.name}'
  z.writestr(p.relative_to(root).as_posix(),b)
with zipfile.ZipFile(root/'technical-review-v1.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in [root/'technical-qa.json',root/'loudness-qa.json',root/'qa_summary.json']+list(qa.glob('*.png')):
  z.write(p,p.relative_to(root).as_posix())
print('Technical gates passed:',json.dumps(report),flush=True)
