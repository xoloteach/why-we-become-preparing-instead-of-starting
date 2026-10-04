"""Synthesize locked script, process final audio, then request timestamp alignment.
Provider secret is read from an external protected file, never copied to project outputs.
Resume-safe: synthesis chunks are keyed by their exact input text.
"""
from pathlib import Path
import json,hashlib,re,subprocess,wave,time,requests,os
root=Path(__file__).resolve().parent
private=Path('/data/_private')
key=json.loads((private/'credentials.json').read_text())['DEEPGRAM_API_KEY']
headers={'Authorization':'Token '+key,'Content-Type':'application/json'}
s=(root/'script.txt').read_text()
# Preserve all words and punctuation; insert paragraph boundaries at the supplied section starts.
anchors=['Imagine this.','Think about the last time you wanted to change something in your life.',"And here's why preparation is so attractive.","But here's the trap.","And sometimes...\nthe problem isn't that you don't know enough.",'This is also why perfectionism can be so sneaky.',"But here's something important.","And this is why action can feel so uncomfortable.","So maybe the goal isn't to eliminate preparation.","So here's a simple rule.","Because that's another mistake we make.","And there's a question that can expose this problem almost instantly.","And here's the uncomfortable part.",'So maybe...\nyou don\'t need another tutorial.',"Because there is something preparation can never give you.",'So the next time you find yourself saying...',"You don't need to start perfectly.","So if there's something you've been preparing for...",'Make it real.',"And maybe that's what you've been missing.",'Think deeper.']
positions=[s.index(a) for a in anchors]
assert positions==sorted(positions)
paras=[s[a:b].strip() for a,b in zip(positions,positions[1:]+[len(s)])]
assert re.sub(r'\s+',' ',s).strip()==re.sub(r'\s+',' ','\n\n'.join(paras)).strip()
(root/'script_paragraphs.json').write_text(json.dumps(paras,ensure_ascii=False,indent=2))
chunks=root/'audio_chunks';chunks.mkdir(exist_ok=True)
for i,text in enumerate(paras):
 digest=hashlib.sha256((text+'|flux-cole-en|0.95|-1').encode()).hexdigest()[:12]
 path=chunks/f'{i:02d}-{digest}.wav'
 if path.exists() and path.stat().st_size>1000:
  print('Cached narration section',i+1,flush=True);continue
 r=requests.post('https://api.deepgram.com/v2/speak',params={'model':'flux-cole-en','encoding':'linear16','container':'wav','sample_rate':44100,'speed':0.95,'expressivity':-1,'mip_opt_out':'true'},headers=headers,json={'text':text},timeout=180)
 if not r.ok: raise RuntimeError('Narration provider rejected section '+str(i+1)+'; status '+str(r.status_code)+'; '+r.text[:400])
 tmp=path.with_suffix('.tmp.wav');tmp.write_bytes(r.content)
 with wave.open(str(tmp)) as w:
  assert w.getnframes()>1000
 tmp.replace(path)
 print('Synthesized narration section',i+1,'of',len(paras),flush=True)
concat=root/'audio_concat.txt'
files=sorted(chunks.glob('*.wav'))
assert len(files)==len(paras)
concat.write_text('\n'.join("file '"+str(p)+"'" for p in files))
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-ac','1','-ar','44100',str(root/'voiceover_raw.wav')],check=True)
chain='highpass=f=80,equalizer=f=220:width_type=o:width=1.2:g=2.5,equalizer=f=3500:width_type=o:width=1.5:g=-2.2,equalizer=f=10000:width_type=o:width=1:g=1.8,acompressor=threshold=0.12:ratio=3.2:attack=15:release=220,silenceremove=stop_periods=-1:stop_duration=0.4:stop_threshold=-45dB,loudnorm=I=-16:LRA=11:TP=-1.0'
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(root/'voiceover_raw.wav'),'-af',chain,'-ar','44100','-ac','1',str(root/'voiceover.wav')],check=True)
with wave.open(str(root/'voiceover.wav')) as w: duration=w.getnframes()/w.getframerate()
print('Final processed narration duration',round(duration,3),'seconds',flush=True)
if not (root/'voiceover_full.json').exists():
 h={'Authorization':'Token '+key,'Content-Type':'audio/wav'}
 r=requests.post('https://api.deepgram.com/v1/listen',params={'model':'nova-3','language':'en','punctuate':'true','smart_format':'false','mip_opt_out':'true'},headers=h,data=(root/'voiceover.wav').read_bytes(),timeout=240)
 if not r.ok: raise RuntimeError('Alignment provider rejected audio; status '+str(r.status_code)+'; '+r.text[:400])
 (root/'voiceover_full.json').write_text(r.text)
full=json.loads((root/'voiceover_full.json').read_text())
alt=full['results']['channels'][0]['alternatives'][0]
words=alt['words']
assert len(words)>len(s.split())*.9
(root/'voiceover.json').write_text(json.dumps(words,indent=2))
(root/'narration_report.json').write_text(json.dumps({'model':'flux-cole-en','speed':0.95,'expressivity':-1,'alignment_model':'nova-3','script_words':len(s.split()),'recognized_words':len(words),'duration':duration,'audio_timing_final':True,'stt_confidence':alt.get('confidence'),'script_sha256':hashlib.sha256(s.encode()).hexdigest()},indent=2))
print('Narration and raw word timestamp estimates complete:',len(words),'words',flush=True)
