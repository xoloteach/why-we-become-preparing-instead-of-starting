from pathlib import Path
import re,json,difflib,bisect
root=Path(__file__).resolve().parent
script=(root/'script.txt').read_text()
words=json.loads((root/'voiceover.json').read_text())
def norm(s):
 s=s.lower().replace('’',"'")
 table={'twenty':'20','fifty':'50','hundredth':'100th','hundred':'100','thousand':'1000','three':'3','first':'1st','one':'1','two':'2'}
 z=re.sub(r'[^a-z0-9]','',s)
 return table.get(z,z)
tokens=[{'text':m.group(),'char':m.start()} for m in re.finditer(r'\S+',script)]
a=[norm(x['text']) for x in tokens];b=[norm(x['word']) for x in words]
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
mapping={};differences=[]
for tag,i0,i1,j0,j1 in sm.get_opcodes():
 if tag=='equal':
  for i,j in zip(range(i0,i1),range(j0,j1)):
   mapping[i]={'start':words[j]['start'],'end':words[j]['end'],'recognized':words[j]['word'],'confidence':words[j].get('confidence'), 'matched':True}
 else:
  differences.append({'type':tag,'script':[x['text'] for x in tokens[i0:i1]],'spoken':[x['word'] for x in words[j0:j1]],'at_script_word':i0,'near_audio_time':words[min(j0,len(words)-1)]['start']})
  # Bridge contractions / split forms only inside their observed spoken span.
  if i1>i0 and j1>j0:
   start=words[j0]['start'];end=words[j1-1]['end']
   for i in range(i0,i1): mapping[i]={'start':start+(end-start)*(i-i0)/(i1-i0),'end':start+(end-start)*(i-i0+1)/(i1-i0),'recognized':' '.join(w['word'] for w in words[j0:j1]),'matched':False,'reason':'reviewed replacement span'}
for i,t in enumerate(tokens):
 if i in mapping:continue
 left=max((k for k in mapping if k<i),default=None);right=min((k for k in mapping if k>i),default=None)
 start=mapping[left]['end'] if left is not None else 0
 end=mapping[right]['start'] if right is not None else words[-1]['end']
 mapping[i]={'start':start,'end':max(start+.02,end),'recognized':'','matched':False,'reason':'unmatched script token: do not treat as exact cue'}
 for d in differences:
  if d['at_script_word']==i: d['review_required']=True
out={'tokens':[{**t,**mapping[i]} for i,t in enumerate(tokens)],'differences':differences,'matched_tokens':sum(m['matched'] for m in mapping.values()),'script_tokens':len(tokens),'coverage':sum(m['matched'] for m in mapping.values())/len(tokens)}
(root/'script_alignment.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print('Exact normalized token alignment:',out['matched_tokens'],'/',len(tokens),round(out['coverage']*100,2),'percent')
for d in differences:print(json.dumps(d,ensure_ascii=False))
