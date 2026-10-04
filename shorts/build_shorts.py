import json,math,re,wave,subprocess
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'shorts/output';O.mkdir(parents=True,exist_ok=True)
T=json.loads((R/'script_alignment.json').read_text())['tokens']
WORDS=json.loads((R/'voiceover.json').read_text())
def norm(s):return ''.join(ch.lower() for ch in s if ch.isalnum())
NW=[norm(t['text']) for t in T]
def cue_lookup(phrase,lo,hi):
 q=[norm(x) for x in phrase.split()]
 for i in range(len(NW)-len(q)+1):
  if T[i]['start']<lo-0.02:continue
  if T[i]['start']>hi:return None
  if NW[i:i+len(q)]==q:return T[i]['start']
 return None
def phrase_anywhere(phrase):
 q=[norm(x) for x in phrase.split()]
 for i in range(len(NW)-len(q)+1):
  if NW[i:i+len(q)]==q:return T[i]['start']
 return None
CLIPS=[
 dict(slug='01-productive-procrastination',title="Procrastination Doesn't Look Like Doing Nothing",topic='THE PRODUCTIVITY ILLUSION',poster=2.4,
  ranges=[(61.010,66.050),(66.050,93.660),(108.365,115.770)],
  scenes=[
   (61.010,'03-9','split',"PROCRASTINATION\nDOESN'T LOOK LIKE DOING NOTHING",[('DOING NOTHING','doing nothing'),('LOOKING PRODUCTIVE',None)],False),
   (63.400,'03-9','split','SOMETIMES IT LOOKS\nINCREDIBLY PRODUCTIVE',[('DOING NOTHING',None),('LOOKING PRODUCTIVE','productive')],False),
   (66.050,'04-1','thought','THINK ABOUT THE\nLAST TIME.',[('CHANGE SOMETHING','change something')],False),
   (69.250,'01-2','paths','YOU WANTED TO\nSTART GOING TO THE GYM.',[('GO TO THE GYM','the gym')],False),
   (73.580,'04-1','feed','THE BEST\nWORKOUT ROUTINE.',[('WORKOUT ROUTINE','workout routine')],False),
   (76.860,'04-2','feed','THEN NUTRITION.\nTHEN EXERCISES.',[('NUTRITION','nutrition'),('EXERCISES','exercises')],False),
   (81.340,'04-4','split','THEN THE\nPERFECT SHOES.',[('GYM SHOES','gym shoes')],False),
   (82.940,'04-5','stack','THEN THE PERFECT\nSCHEDULE.',[('SCHEDULE','schedule')],False),
   (84.860,'04-7','feed','THEN ANOTHER VIDEO.',[('ANOTHER ROUTINE','another video')],False),
   (89.580,'04-8','clock','THREE HOURS.\nNO WORKOUT.',[('3 HOURS','three hours'),('NO WORKOUT','worked out')],True),
   (108.365,'04-12','stack','INFORMATION\nFEELS LIKE PROGRESS.',[('MORE INFORMATION','collecting information'),('FEELS LIKE PROGRESS','feels like progress')],False),
   (112.490,'03-4','split',"KNOWING\nISN'T DOING.",[('KNOWING','knowing'),('DOING','doing')],True)]),
 dict(slug='02-everything-is-ready',title='Everything Is Ready. Except You.',topic='THE SAFE FANTASY',poster=7.0,
  ranges=[(42.550,58.815),(118.970,141.420)],
  scenes=[
   (42.550,'03-3','stack','THE RESEARCH.\nTHE PLAN.',[('RESEARCH','research'),('PLAN','plan')],False),
   (44.900,'03-5','stack','THE IDEAS.\nTHE MOTIVATION.',[('IDEAS','ideas'),('MOTIVATION','motivation')],False),
   (47.850,'03-6','split','EVERYTHING IS READY.\nEXCEPT YOU.',[('EVERYTHING','everything is ready'),('EXCEPT YOU','except')],True),
   (50.820,'03-7','thought',"WHAT IF YOU'RE\nNOT PREPARING TO START?",[('PREPARING?','preparing'),('AVOIDING?',None)],False),
   (54.900,'03-7','thought','USING PREPARATION\nTO AVOID STARTING.',[('PREPARING?',None),('AVOIDING?','avoid')],False),
   (118.970,'05-1','window','PREPARATION\nFEELS SAFE.',[('PREPARATION','preparation'),('SAFE','safe')],False),
   (120.730,'05-2','thought','EVERYTHING\nGOES PERFECTLY.',[('EVERYTHING GOES PERFECTLY','everything going perfectly')],False),
   (124.480,'05-3','stack','NOTHING TESTED.\nNOTHING JUDGED.',[('NO MISTAKES','mistakes'),('NO FAILURE','failed'),('NO JUDGMENT','judged')],False),
   (130.970,'05-4','thought','POTENTIAL STAYS\nPROTECTED.',[('IMAGINATION','imagination'),('MAYBE GREAT','great')],False),
   (139.820,'05-5','split','THEN REALITY\nBEGINS.',[('START','the moment you start'),('REALITY','reality begins')],True)]),
 dict(slug='03-preparing-or-hiding',title='Am I Preparing… Or Am I Hiding?',topic='THE HONEST QUESTION',poster=5.2,
  ranges=[(518.040,524.365),(525.405,535.485),(537.070,547.790),(574.425,586.900)],
  scenes=[
   (518.040,'03-7','thought','“I JUST NEED TO PREPARE A LITTLE MORE…”',[('PREPARE MORE','prepare'),('PAUSE','pause')],False),
   (521.500,'03-7','thought','AM I PREPARING…\nOR AM I HIDING?',[('PREPARING?','preparing'),('HIDING?','hiding')],True),
   (525.405,'05-5','focus','THE ANSWER WILL\nBE UNCOMFORTABLE.',[('UNCOMFORTABLE','uncomfortable')],False),
   (530.000,'05-5','focus','THE EDGE\nOF PREPARATION.',[('THE EDGE','edge')],False),
   (533.570,'10-3','focus','ONLY ONE\nTHING LEFT.',[('ACTION','Action')],True),
   (537.070,'07-8','stack',"YOU DON'T NEED\nTO START PERFECTLY.",[('PERFECT','perfectly'),('EVERYTHING','everything'),('STRATEGY','strategy'),('CONFIDENCE','confident')],False),
   (542.990,'09-2','thought','JUST WILLING TO MAKE\nTHE FIRST ATTEMPT.',[('WILLING','willing'),('FIRST ATTEMPT','first attempt')],False),
   (574.425,'10-8','window','STUDYING\nTHE WATER.',[('MAKE IT REAL','Make it real'),('STUDYING THE WATER','studying the water')],False),
   (577.780,'10-9','paths','AT SOME POINT,\nYOU HAVE TO GET IN.',[('GET IN','get in')],False),
   (579.460,'10-9','focus','JUST…\nA BEGINNING.',[('NOT MORE PREPARATION','more preparation'),('NOT MORE INFORMATION','more information'),('NOT MORE MOTIVATION','more motivation'),('A BEGINNING','beginning')],True)]),
]
def build():
 for c in CLIPS:
  off=0;segs=[]
  for a,b in c['ranges']:segs.append((a,b,off));off+=b-a
  def loc(t):
   for a,b,o in segs:
    if a-.002<=t<b-.002:return o+t-a
   return None
  vo=off;c['vo']=vo;c['duration']=vo+2.5
  sc=[]
  for k,(st,art,kind,title,labels,dark) in enumerate(c['scenes']):
   nxt=c['scenes'][k+1][0] if k+1<len(c['scenes']) else None
   s0=loc(st)
   s1=loc(nxt) if nxt is not None else vo
   if nxt is not None and s1 is None:
    for a,b,o in segs:
     if abs(nxt-b)<.002:s1=o+b-a
   assert s0 is not None and s1 is not None and s1>s0,(c['slug'],k,st,nxt)
   cues=[]
   for lab,ph in labels:
    t=cue_lookup(ph,st,(nxt if nxt is not None else st+30)) if ph else None
    if t is None:
     cues.append(s1+1 if (ph is None or phrase_anywhere(ph) is None) else s0-1.0)
    else:
     z=loc(t)
     cues.append(z if z is not None else s0-1.0)
   d=dict(id=k,start=round(s0,3),end=round(s1,3),art=art,kind=kind,title=title,labels=[l for l,_ in labels],cues=[round(q,3) for q in cues],dark=dark,feature=False,layout='right',chapter=1)
   if kind=='clock':d['clock_label']='3 HOURS'
   sc.append(d)
  c['scenes']=sc
  for i,s in enumerate(sc):assert s['end']>s['start'] and len(s['cues'])==len(s['labels'])
  print('%-30s %2d scenes  vo=%.2f total=%.2f  cues_ok=%d'%(c['slug'],len(sc),vo,c['duration'],sum(1 for s in sc for q in s['cues'] if s['start']-1.5<q<s['end'])))
 return CLIPS
def captions(c):
 arr=[]
 for a,b in c['ranges']:
  off=sum(x[1]-x[0] for x in c['ranges'][:c['ranges'].index((a,b))])
  for w in WORDS:
   if a-.015<=w['start']<b-.025:
    z=dict(w);z['start']=max(off,off+w['start']-a);z['end']=min(off+b-a,off+w['end']-a);arr.append(z)
 json.dump(arr,open(O/(c['slug']+'-words.json'),'w'),indent=1)
 hdr='''[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Montserrat ExtraBold,60,&H00FFFFFF,&H003C62C8,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,1.5,2,80,200,420,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
 groups=[];cur=[]
 for w in arr:
  if cur and (len(cur)>=5 or w['start']-cur[-1]['end']>.24):groups.append(cur);cur=[]
  cur.append(w)
  if re.search(r'[.!?]$',w.get('punctuated_word',w['word'])):groups.append(cur);cur=[]
 if cur:groups.append(cur)
 def tm(t):
  v=max(0,round(t*100));h,v=divmod(v,360000);m,v=divmod(v,6000);s,v=divmod(v,100);return '%d:%02d:%02d.%02d'%(h,m,s,v)
 out=hdr;nl_max=0
 for g in groups:
  start=g[0]['start'];stop=min(c['vo'],max(start+.08,g[-1]['end']+.025));parts=[];line='';nl=1
  for w in g:
   word=w.get('punctuated_word',w['word']).replace('{','').replace('}','')
   z=(line+' '+word).strip()
   if line and len(z)>33:parts.append('\\N');line=word;nl+=1
   else:line=z
   lo=max(0,round((w['start']-start)*1000));hi=max(lo+25,round((w['end']-start)*1000))
   parts.append('{\\1c&HFFFFFF&\\t('+str(lo)+','+str(lo+12)+',\\1c&H3C62C8&)\\t('+str(hi)+','+str(hi+12)+',\\1c&HFFFFFF&)}'+word+' ')
  nl_max=max(nl_max,nl);assert nl<=2,(c['slug'],'caption overflow',nl)
  out+='Dialogue: 0,'+tm(start)+','+tm(stop)+',Default,,0,0,0,,'+''.join(parts).strip()+'\n'
 (O/(c['slug']+'.ass')).write_text(out)
 text=' '.join(w.get('punctuated_word',w['word']) for w in arr)
 (O/(c['slug']+'-script.md')).write_text('# '+c['title']+'\n\n'+text+'\n')
 (O/(c['slug']+'-seo.md')).write_text('# '+c['title']+'\n\nOriginal narration excerpt from Why You Keep Preparing Instead of Starting, with supplied artwork recomposed natively for 9:16.\n\nThink deeper. Live better. Become more.\n\n#Shorts #Procrastination #SelfImprovement #WhyWeBecome\n')
 print('%-30s captions: %d groups, %d words, max %d lines'%(c['slug'],len(groups),len(arr),nl_max))
 return groups
def audio(c,vo,sr):
 ps=[]
 for a,b in c['ranges']:
  p=vo[round(a*sr):round(b*sr)].copy();n=min(660,len(p)//2);p[:n]*=np.linspace(0,1,n);p[-n:]*=np.linspace(1,0,n);ps.append(p)
 speech=np.concatenate(ps);N=round(c['duration']*sr);v=np.zeros(N,np.float32);v[:len(speech)]=speech
 vr=float(np.sqrt(np.mean(speech**2)));t=np.arange(N,dtype=np.float32)/sr;music=np.zeros(N,np.float32)
 for j,fs in enumerate([[220,261.626,329.628],[174.614,220,261.626],[130.813,164.814,196],[196,246.942,293.665]]*3):
  a=j*5.5;b=min(c['duration'],a+7)
  if a>=c['duration']:break
  ix=(t>=a)&(t<b);x=t[ix]-a;en=np.minimum(1,x/.75)*np.minimum(1,(b-t[ix])/.9)
  for f in fs:music[ix]+=en*(np.sin(2*np.pi*f*x)+.18*np.sin(2*np.pi*f*2*x))*.2
 st=round(sr/100);bins=np.pad(v,(0,(-N)%st)).reshape(-1,st);en=np.sqrt(np.mean(bins*bins,1));en=np.convolve((en>vr*.2).astype(float),np.ones(25)/25,'same');duck=np.interp(np.arange(N)/st,np.arange(len(en)),en)
 music*=vr*.0794/max(float(np.sqrt(np.mean(music**2))),1e-5);music*=1-.72*duck
 mix=np.column_stack([v+music,v+music]).astype(np.float32)
 def put(x,t_,g):
  k=round(t_*sr)
  if k<0:x=x[-k:];k=0
  n=min(len(x),N-k)
  if n>0:mix[k:k+n]+=x[:n,None]*g
 x=np.arange(round(sr*.085))/sr;tick=np.sin(2*np.pi*(950-700*x)*x)*np.exp(-x*65)
 x=np.arange(round(sr*.24))/sr;wh=np.random.default_rng(31).normal(0,1,len(x));wh=np.convolve(wh,np.ones(5)/5,'same');wh*=np.sin(np.pi*np.minimum(1,x/.24))**2;wh/=max(abs(wh))
 for j,s in enumerate(c['scenes']):
  if j and (s['dark'] or j%3==0):put(wh,s['start']-.075,vr*.15)
  for q in s['cues']:
   if 0<=q<s['end']:put(tick,q+.015,vr*.1)
 put(tick,c['vo']+.3,vr*.1);n=round(sr*.35);mix[-n:]*=np.linspace(1,0,n)[:,None]
 with wave.open(str(O/(c['slug']+'-raw.wav')),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(mix,-.98,.98)*32767).astype('<i2').tobytes())
 subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(O/(c['slug']+'-raw.wav')),'-af','loudnorm=I=-16:LRA=11:TP=-1.5','-ar','44100',str(O/(c['slug']+'.wav'))],check=True)
 print('%-30s audio mastered'%c['slug'])
if __name__=='__main__':
 clips=build()
 with wave.open(str(R/'voiceover.wav'),'rb') as w:sr=w.getframerate();assert w.getnchannels()==1;vo=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float32)/32768
 for c in clips:captions(c);audio(c,vo,sr)
 json.dump([{k:v for k,v in c.items()} for c in clips],open(O/'scene-plans.json','w'),indent=1)
 print('BUILD OK')
