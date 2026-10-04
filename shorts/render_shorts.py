import os,sys,json,math,subprocess,wave,bisect,re,functools
from pathlib import Path
import cv2,numpy as np
R=Path(__file__).resolve().parents[1];os.chdir(R);sys.path.insert(0,str(R/'v2'))
import render_motion as B
B.W=1080;B.H=1920;W,H=1080,1920;cv2.setNumThreads(1)
O=R/'shorts/output';O.mkdir(parents=True,exist_ok=True);(O/'qa').mkdir(exist_ok=True)
WORDS=json.load(open('voiceover.json'));P,I,RC,G,WH=B.PAPER,B.INK,B.RUST,B.GOLD,B.WHITE
CLIPS=json.load(open(O/'scene-plans.json'))
SAMPLE=float(os.environ.get('SAMPLE','0'))
for c in CLIPS:c['starts']=[s['start'] for s in c['scenes']]
grain=np.random.default_rng(321).normal(0,.5,(H,W,1))
BG={False:np.clip(np.array(P)[None,None,:]+grain,0,255).astype(np.uint8),True:np.clip(np.array(I)[None,None,:]+grain*.4,0,255).astype(np.uint8)}
@functools.lru_cache(maxsize=12)
def hero(art,dark):
 a,ink,ps=B.hero(art,False,dark);h,w=a.shape[:2];sc=min(830/w,435/h);wh=(round(w*sc),round(h*sc))
 a=cv2.resize(a,wh,interpolation=cv2.INTER_AREA);ink=cv2.resize(ink,wh,interpolation=cv2.INTER_AREA)
 ps=[(cv2.resize(p,(max(1,round(p.shape[1]*sc)),wh[1]),interpolation=cv2.INTER_AREA),round(off*sc)) for p,off in ps]
 return a,ink,ps
def art(f,s,t):
 a,ink,ps=hero(s['art'],s['dark']);h,w=a.shape[:2];r=t-s['start'];u=min(1,max(0,r/(s['end']-s['start'])))
 x=540-w/2;y=618-h/2;cap=int(w*B.ease((r+.04)/.45));fill=B.ease((r-.08)/.55)
 for j,(p,off) in enumerate(ps):
  n=min(p.shape[1],cap-off)
  if n<=0:continue
  dx=(1-B.spring(r/.6))*28*(1 if s['id']%2 else -1)+(B.ease(u)-.5)*(14 if j==0 else -10)
  dy=(1-B.spring(max(0,r-j*.06)/.6))*(20 if j==0 else -20)+(B.ease(u)-.5)*(6 if j==0 else -6)
  B.blit(f,ink[:,off:off+n],x+off+dx,y+dy,1-fill);B.blit(f,p[:,:n],x+off+dx,y+dy,fill)
def scene(c,j,t):
 s=c['scenes'][j];r=t-s['start'];fg=WH if s['dark'] else I
 f=BG[s['dark']].copy()
 B.text(f,'WHY WE BECOME',85,119,26,fg,400,weight='Black')
 B.text(f,c['topic'],534,124,21,RC,350)
 B.line(f,(85,181),(900,181),(52,61,66) if s['dark'] else (222,231,237),1)
 sz=86;a=B.glyph(s['title'],sz,fg,805,'Black')
 while a.shape[0]>244 and sz>62:sz-=2;a=B.glyph(s['title'],sz,fg,805,'Black')
 assert a.shape[0]<=260,(c['slug'],j,a.shape[0])
 en=1 if j==0 else B.spring(r/.42)
 B.blit(f,a,87,225+(1-en)*17,en)
 B.line(f,(90,490),(230,490),RC,5,B.ease((r+.05)/.45))
 art(f,s,t)
 B.diagram(f,s,t,87,1030,790,320)
 B.line(f,(85,1620),(900,1620),(55,62,67) if s['dark'] else (220,230,236),2)
 B.line(f,(85,1620),(900,1620),RC,4,t/c['duration'])
 B.text(f,'THINK DEEPER. LIVE BETTER.',85,1672,22,fg,810)
 return f
END=cv2.imread('assets/subscribe-end-card.jpeg');EW=935;EH=round(END.shape[0]*EW/END.shape[1]);END=cv2.resize(END,(EW,EH),interpolation=cv2.INTER_LANCZOS4)
def frame(c,t):
 if t>=c['vo']:
  f=BG[False].copy()
  B.text(f,'WHY WE BECOME',85,145,28,I,800,weight='Black')
  B.text(f,'THINK\nDEEPER.',85,310,100,I,815,weight='Black')
  x=(W-EW)//2;f[660:660+EH,x:x+EW]=END
  B.text(f,'LIVE BETTER.\nBECOME MORE.',85,1265,53,I,815,weight='Black')
  B.line(f,(90,1508),(900,1508),RC,5,B.ease((t-c['vo']-.2)/.8))
  a=B.ease((t-c['vo'])/.28)
  return cv2.addWeighted(scene(c,len(c['scenes'])-1,c['vo']-.001),1-a,f,a,0)
 j=max(0,bisect.bisect_right(c['starts'],t)-1);f=scene(c,j,t);r=t-c['starts'][j]
 if j and r<.18:
  prev=scene(c,j-1,c['starts'][j]-.01);a=B.ease(r/.18)
  if j%3==0 and c['scenes'][j]['dark']==c['scenes'][j-1]['dark']:
   y=int(H*a);f[y:]=prev[y:];cv2.line(f,(0,y),(W,y),RC,3)
  else:f=cv2.addWeighted(prev,1-a,f,a,0)
 return f
def render(c):
 f=O/('short-'+c['slug']+'.mp4')
 lim=math.ceil((SAMPLE if SAMPLE else c['duration'])*30)
 p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r','30','-i','-','-i',str(O/(c['slug']+'.wav')),'-vf','ass='+str(O/(c['slug']+'.ass'))+':fontsdir='+str(R/'assets/fonts'),'-c:v','libx264','-preset','veryfast','-crf','18','-threads','2','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(f)],stdin=subprocess.PIPE)
 try:
  for j in range(lim):
   p.stdin.write(frame(c,j/30).tobytes())
   if j%300==0:print(c['slug'],j,flush=True)
 finally:p.stdin.close()
 assert p.wait()==0
 return f
def poster(c):
 cv2.imwrite(str(O/('thumbnail-'+c['slug']+'.png')),frame(c,c['poster']))
def qa(c,f):
 for j,s in enumerate(c['scenes']):cv2.imwrite(str(O/'qa'/('%s-scene%02d.png'%(c['slug'],j))),frame(c,min(s['end']-.04,s['start']+max(.55,(s['end']-s['start'])*.7))))
 for j,t in enumerate([1.1,c['vo']*.55,c['vo']-.35,c['vo']+1.2]):subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(t),'-i',str(f),'-frames:v','1',str(O/'qa'/(c['slug']+'-actual%d.png'%j))],check=True)
 pr=json.loads(subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(f)],capture_output=True,text=True,check=True).stdout)
 s=next(x for x in pr['streams'] if x['codec_type']=='video');d=float(pr['format']['duration'])
 assert s['width']==W and s['height']==H and s['r_frame_rate']=='30/1',(s['width'],s['height'],s['r_frame_rate'])
 assert abs(d-c['duration'])<.5,(d,c['duration'])
 log=subprocess.run(['ffmpeg','-i',str(f),'-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
 ld=json.loads(log[log.rfind('{'):log.rfind('}')+1]);li=float(ld['input_i']);tp=float(ld['input_tp'])
 assert -17.5<=li<=-14.5,li
 (O/(c['slug']+'-technical-qa.json')).write_text(json.dumps(dict(probe=pr,loudness=ld),indent=2))
 return dict(file=f.name,title=c['title'],duration=d,voice_duration=c['vo'],scene_count=len(c['scenes']),loudness=li,true_peak=tp,thumbnail='thumbnail-'+c['slug']+'.png',source_ranges=c['ranges'])
if __name__=='__main__':
 only=os.environ.get('ONLY');res=[]
 for c in CLIPS:
  if only and only not in c['slug']:continue
  f=render(c);poster(c)
  if not SAMPLE:res.append(qa(c,f))
  print('rendered',c['slug'],flush=True)
 if res:
  json.dump(res,open(O/'shorts-manifest.json','w'),indent=2)
  (O/'release-notes.md').write_text('# Three native motion-first Shorts\n\n'+'\n'.join('- **%s** — %.2fs, 1080×1920, 30fps, %.2f LUFS.'%(x['title'],x['duration'],x['loudness']) for x in res)+'\n\nOriginal narration and supplied artwork, natively recomposed at 1080×1920. Each duration includes the 2.5-second ending.\n')
 print('RENDER OK')
