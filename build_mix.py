from pathlib import Path
import numpy as np,json,wave,subprocess
root=Path(__file__).resolve().parent;SR=44100
tl=json.loads((root/'timeline.json').read_text());sc=json.loads((root/'v2/scene_plan.json').read_text());N=round(tl['total']*SR)
with wave.open(str(root/'voiceover.wav')) as w:
 vo=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
v=np.zeros(N,np.float32);v[:len(vo)]=vo[:N];rms=float(np.sqrt(np.mean(vo*vo)))
bgm=np.zeros(N,np.float32)
chords=[[110,130.813,164.814],[87.307,110,130.813],[130.813,164.814,195.998],[97.999,123.471,146.832]]
seg=8;cross=3
for i in range(int(tl['total']/seg)+2):
 a=max(0,round((i*seg-cross/2)*SR));b=min(N,round(((i+1)*seg+cross/2)*SR))
 if b<=a:continue
 t=np.arange(a,b,dtype=np.float32)/SR
 env=np.minimum(np.clip((t-(i*seg-cross/2))/cross,0,1),np.clip((((i+1)*seg+cross/2)-t)/cross,0,1))
 env=np.sin(env*np.pi/2)**2
 pad=np.zeros(b-a,np.float32)
 for j,f in enumerate(chords[i%4]):
  for det in [-.35,.35]:
   pad+=(np.sin(2*np.pi*(f+det)*t+j*1.6)+.16*np.sin(4*np.pi*(f+det)*t))*(.7+.3*np.sin(2*np.pi*.07*t+j))
 bgm[a:b]+=pad*env
bgm/=float(np.sqrt(np.mean(bgm*bgm)))+1e-9
# Smooth sidechain at 100 Hz, not an unbounded full-sample convolution.
step=441;bins=np.pad(v,(0,(-N)%step)).reshape(-1,step)
slow=np.sqrt(np.mean(bins*bins,axis=1));slow=np.convolve(slow,np.ones(25)/25,'same')
activity=(slow>rms*.25).astype(np.float32);kernel=np.hanning(35);kernel/=kernel.sum();activity=np.convolve(activity,kernel,'same')
env=np.interp(np.arange(N,dtype=np.float32)/step,np.arange(len(activity)),activity).astype(np.float32)
gain=rms*10**((-22+(1-env)*4)/20)
fade=np.minimum(np.clip(np.arange(N)/SR/2,0,1),np.clip((tl['total']-np.arange(N)/SR)/2,0,1))
bgm*=gain*fade
sfx=np.zeros(N,np.float32)
def put(sig,t,level):
 a=max(0,round(t*SR));b=min(N,a+len(sig))
 if b>a:sfx[a:b]+=sig[:b-a]*rms*level
rng=np.random.default_rng(9)
t=np.arange(round(.18*SR))/SR;tick=(np.sin(2*np.pi*1180*t)*np.exp(-t*38)).astype(np.float32)
t=np.arange(round(.45*SR))/SR;whoosh=(rng.normal(0,1,len(t))*np.sin(np.pi*t/.45)**2*.13).astype(np.float32)
t=np.arange(round(.7*SR))/SR;thud=(np.sin(2*np.pi*130*t)*np.exp(-t*7)).astype(np.float32)
for i,s in enumerate(sc):
 if i and s['dark']!=sc[i-1]['dark']:put(whoosh,s['start']-.1,.12)
 if s['dark'] and i%3==0:put(thud,s['start']+.08,.10)
 if s['kind'] in ['feed','stack','loop','counter']:
  for cue in s['cues']:
   if cue<s['end']:put(tick,cue+.02,.09)
mix=v+bgm+sfx
peak=float(np.max(abs(mix)))
if peak>.92:mix*=.92/peak
raw=root/'v2/mix_raw.wav'
with wave.open(str(raw),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(raw),'-af','loudnorm=I=-16:LRA=11:TP=-1.2','-ar','44100','-ac','2',str(root/'v2/mix.wav')],check=True)
print('Final soundtrack:',tl['total'],'seconds. Original narration, locally synthesized ambient bed and restrained SFX; music ducked about -22 dB relative to speech RMS.')
