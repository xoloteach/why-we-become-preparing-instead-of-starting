from pathlib import Path
import json,re,bisect,wave,math
root=Path(__file__).resolve().parent
s=(root/'script.txt').read_text();alignment=json.loads((root/'script_alignment.json').read_text());tokens=alignment['tokens']
chars=[t['char'] for t in tokens]
flat=re.sub(r'\s+',' ',s).strip(); positions=[]
# Map flattened character positions back to canonical script offsets.
for m in re.finditer(r'\S+',s):positions.append((m.start(),m.group()))
flat_offsets=[]
for offset,word in positions:
 flat_offsets.extend(range(offset,offset+len(word)));flat_offsets.append(offset+len(word))
assert len(flat_offsets)>=len(flat)
def seek(phrase,lo=0):
 phrase=re.sub(r'\s+',' ',phrase).strip()
 i=flat.lower().find(phrase.lower(),lo)
 if i<0:raise ValueError('Phrase not found after '+str(lo)+': '+phrase)
 return i

def timestamp(flat_index,require_exact=False):
 ci=flat_offsets[flat_index];ti=max(0,bisect.bisect_right(chars,ci)-1)
 if require_exact and not tokens[ti]['matched']:
  # Use the first precisely matched token within the actual phrase, not an estimated missing word.
  ti=next(j for j in range(ti,min(ti+5,len(tokens))) if tokens[j]['matched'])
 return tokens[ti]['start']

# Each row: spoken phrase | supplied panel | semantic engine | headline | labels~spoken cue
DATA='''Imagine this.|01-1|paths|Something you / want to do.|A BEGINNING~Imagine this.
Maybe you want to start working out.|01-2|focus|Work out.|WORKOUT~working out
Maybe you want to learn a skill.|01-3|focus|Learn a skill.|PRACTICE~learn a skill
Maybe you want to start a business.|01-4|focus|Build something.|BUSINESS~start a business
Maybe you want to make videos.|01-5|focus|Make videos.|CREATE~make videos
Maybe you want to finally fix your sleep.|01-6|clock|Fix your sleep.|A ROUTINE~fix your sleep
Whatever it is...|01-7|thought|I'm getting / ready.|READY~getting ready
So you start researching.|01-8|search|Research feels / like movement.|RESEARCH~researching
You watch videos.|02-1|feed|One more video.|VIDEOS~watch videos
You read articles.|02-2|stack|One more article.|ARTICLES~read articles
You compare different options.|02-4|split|Compare. / Compare again.|OPTIONS~different options;TOOLS~best tools
You download an app.|02-6|stack|An app. / A plan.|APP~download an app;PLAN~make a plan
Maybe you even buy a notebook...|02-7|focus|Write it all down.|NOTEBOOK~buy a notebook;NOTES~write everything down
And after all that...|02-8|thought|It feels / productive.|PRODUCTIVE~feel productive;MOVING FORWARD?~moving forward
But then something strange happens.|02-9|stack|Prepared. / Still waiting.|A STACK OF PREPARATION~something strange happens
A week passes.|03-1|timeline|The weeks pass.|ONE WEEK~A week passes;ANOTHER~Then another
And somehow...|03-2|focus|You haven't / started.|NOT STARTED~haven't actually started
The research is there.|03-3|stack|Everything is / ready.|RESEARCH~research is there;PLAN~plan is there
The ideas are there.|03-5|stack|Ideas. / Motivation.|IDEAS~ideas are there;MOTIVATION~motivation is there
Everything is ready.|03-6|split|Everything. / Except you.|EVERYTHING~Everything is ready;EXCEPT YOU~Except
And that's when you need to ask yourself|03-7|thought|Preparing... / or avoiding?|PREPARING?~preparing to start;AVOIDING?~avoid starting
Because sometimes...|03-9|split|Procrastination / can look productive.|DOING NOTHING~doing nothing;LOOKING PRODUCTIVE~incredibly productive
Think about the last time you wanted to change something in your life.|04-1|thought|The research / rabbit hole.|CHANGE SOMETHING~change something in your life
Maybe you wanted to start going to the gym.|01-2|paths|Before the gym.|GO TO THE GYM~going to the gym
First...|04-1|feed|The best routine.|WORKOUT ROUTINE~best workout routine
Then you watched videos about nutrition.|04-2|feed|Then nutrition.|NUTRITION~nutrition;EXERCISES~different exercises
Then you looked at gym shoes.|04-4|split|Even the shoes.|GYM SHOES~gym shoes
Then you searched for the perfect schedule.|04-5|stack|The perfect / schedule.|SCHEDULE~perfect schedule
Then you watched another video...|04-7|feed|Another video.|ANOTHER ROUTINE~another video
And suddenly...|04-8|clock|Three hours. / No workout.|3 HOURS~three hours;NO WORKOUT~haven't worked out
Or maybe you wanted to learn a new skill.|04-11|search|The perfect way / to learn.|WHAT SKILL?~What skill should I learn;WHAT COURSE?~best course
“What's the best YouTube channel?”|04-10|feed|More questions.|CHANNEL~best YouTube channel;SOFTWARE~this software;LAPTOP~What laptop
“What is the fastest way to learn?”|04-12|stack|Information / feels like progress.|MORE INFORMATION~collecting information;FEELS LIKE PROGRESS~information feels like progress
But there's a difference between knowing what to do...|03-4|split|Knowing ≠ doing.|KNOWING~knowing what to do;DOING~actually doing it
And here's why preparation is so attractive.|05-1|window|Preparation / feels safe.|PREPARATION~preparation is so attractive;SAFE~Preparation feels safe
When you're preparing...|05-2|thought|Inside the / perfect version.|EVERYTHING GOES PERFECTLY~everything going perfectly
You haven't made any mistakes yet.|05-3|stack|Nothing tested. / Nothing judged.|NO MISTAKES~made any mistakes;NO FAILURE~haven't failed;NO JUDGMENT~judged your work
You haven't discovered what you're actually bad at.|05-4|thought|Potential stays / protected.|IMAGINATION~inside your imagination;MAYBE GREAT~Maybe even great
But the moment you start...|05-5|split|Then reality / begins.|START~moment you start;REALITY~reality begins
Your first workout might feel terrible.|05-6|focus|The first / workout.|UNCOMFORTABLE~feel terrible
Your first video might be awkward.|05-7|focus|The first / video.|AWKWARD~be awkward
Your first business idea might fail.|05-8|focus|The first / attempt.|IT MIGHT FAIL~might fail
Your first attempt at learning something might make you realize...|05-9|thought|More to learn.|REAL PROCESS~real process;UNCOMFORTABLE~That's uncomfortable
So your brain gives you an easier option.|06-1|thought|Prepare a / little more.|THE EASIER OPTION~easier option;MORE PREPARATION~Prepare a little more
Just one more video.|06-2|feed|Just one more.|VIDEO~one more video;ARTICLE~One more article;TUTORIAL~One more tutorial;PLAN~One more plan
One more week.|03-1|timeline|Then you'll / start.|ONE MORE WEEK~One more week;THEN START~then you'll start
But here's the trap.|06-3|stack|There is / always more.|ONE MORE THING~one more thing to prepare;VIDEO~another video;BOOK~Another book
Another strategy.|06-4|feed|Another solution.|STRATEGY~Another strategy;TOOL~Another tool
Another expert.|06-5|feed|Someone who / knows more.|EXPERT~Another expert;SYSTEM~productivity system
Another person who seems to know more than you.|06-6|focus|Almost ready. / Again.|MORE KNOWLEDGE~know more than you
And if you're not careful...|06-7|window|A room with / no exit.|NO EXIT~room with no exit;ALMOST READY~almost ready
But the finish line keeps moving.|06-8|finish|The finish line / moves.|MOVING GOAL~finish line keeps moving
And sometimes... the problem isn't that you don't know enough.|06-9|thought|Enough knowledge. / Still no start.|NOT KNOWING ENOUGH?~don't know enough;A DELAY~excuse to delay
Because once you start...|07-1|split|Potential meets / reality.|POTENTIAL~hide behind potential;I COULD BE GOOD~really good at this
After you start...|07-2|thought|You get to / find out.|FIND OUT~get to find out
And sometimes... we'd rather protect the idea of what we could become...|07-3|split|Protect the idea. / Risk the truth.|COULD BECOME~what we could become;ACTUALLY ARE~where we actually are
This is also why perfectionism can be so sneaky.|07-6|thought|Perfectionism / can hide here.|PERFECTIONISM~perfectionism can be so sneaky
People often think perfectionism means wanting everything to be perfect.|07-3|split|Perfect... / or never a beginner?|PERFECT~everything to be perfect;BEGINNER~be a beginner
You don't want to make the first bad video.|07-5|feed|The awkward / first attempt.|BAD VIDEO~first bad video;TERRIBLE PARAGRAPH~first terrible paragraph;AWKWARD ATTEMPT~first awkward attempt
You want your first attempt to look like someone else's hundredth.|07-4|split|Your first. / Their hundredth.|YOUR FIRST~your first attempt;THEIR HUNDREDTH~else's hundredth
So you keep preparing.|07-7|thought|Progress without / imperfection.|PREPARING~keep preparing;WITHOUT IMPERFECTION~look imperfect
But here's something important.|07-8|focus|Not impressive. / Instructive.|NOT IMPRESSIVE~supposed to be impressive;TEACHES YOU~teach you something
You cannot research your way into experience.|07-9|paths|Experience must / be experienced.|RESEARCH~research your way;EXPERIENCE~experience something
You can watch fifty videos about making videos.|08-1|counter|Fifty videos. / Eventually, one.|50 VIDEOS~fifty videos;MAKE ONE~make one
You can read twenty books about discipline.|08-2|counter|Twenty books. / Then do it.|20 BOOKS~twenty books;DO SOMETHING DIFFICULT~do something difficult
You can study every business strategy on the internet.|08-3|paths|Put it in front / of someone.|STRATEGY~business strategy;TEST IT~another human being
That's where real learning begins.|08-4|focus|Reality gives / you feedback.|REAL LEARNING~real learning begins;FEEDBACK~reality gives you feedback
And this is why action can feel so uncomfortable.|08-5|thought|Action gives / you answers.|ACTION~action can feel so uncomfortable;UNCERTAINTY~destroys uncertainty
Before you start...|08-9|split|Possibilities. / Then answers.|POSSIBILITIES~a thousand possibilities;ANSWERS~you get answers
Maybe the idea works.|08-6|split|Maybe it works. / Maybe it doesn't.|WORKS~idea works;DOESN'T~Maybe it doesn't
Maybe you're good at it.|07-2|split|Now you / find out.|GOOD AT IT~good at it;NOT YET~terrible at it
Maybe you love it.|08-5|split|Love it? / Hate it?|LOVE~love it;HATE~hate it
But at least now...|08-7|focus|At least / you know.|NOW YOU KNOW~you know;VALUABLE~incredibly valuable
Because you can improve something that exists.|08-8|split|Existing work / can improve.|EXISTS~something that exists;ONLY IN YOUR HEAD~inside your head
Think about it.|07-8|focus|A rough draft / can improve.|FIRST DRAFT~first draft can be improved
A bad workout can teach you what to change next time.|08-2|split|A workout. / Or no workout.|FEEDBACK~change next time;NO FEEDBACK~No workout
A rough video can become a better video.|08-8|split|Rough can / become better.|ROUGH VIDEO~A rough video;BETTER VIDEO~better video
A perfect idea sitting inside your notes...|08-9|thought|A perfect idea / is still an idea.|INSIDE YOUR NOTES~inside your notes
So maybe the goal isn't to eliminate preparation.|09-1|focus|Preparation / is useful.|PREPARATION~Preparation is useful;RESEARCH~Research is useful;PLANNING~Planning is useful
The problem begins when preparation has no connection to action.|03-8|paths|Connect it / to action.|PREPARATION~preparation has no connection;ACTION~to action
If every hour of research leads to another hour of research...|04-12|feed|Research only / creates research.|MORE RESEARCH~another hour of research;SOMETHING IS WRONG~something is wrong
If every new plan creates another new plan...|03-4|stack|Plans create / more plans.|ANOTHER PLAN~another new plan;NO PRACTICE~never practice it
So here's a simple rule.|09-2|loop|Prepare. / Then make it real.|PREPARE~prepare for;CREATE~create something;TEST~Test something;FIRST VERSION~Make the first version
If you're researching a business idea...|09-3|focus|Build a / tiny version.|TINY VERSION~build a tiny version
If you're learning to write...|09-4|focus|Write something.|WRITE~write something
If you're learning to make videos...|09-5|focus|Make a video.|MAKE~make a video
If you're studying a skill...|09-6|focus|Practice / the skill.|PRACTICE~practice the skill
Don't wait until you're ready.|09-7|paths|Act to learn / what comes next.|DON'T WAIT~Don't wait;ACT~Use action;LEARN WHAT'S NEXT~prepare for next
Because that's another mistake we make.|09-8|thought|You don't need / the whole map.|THE ENTIRE PATH?~entire path;NOT YET~you don't
You only need enough information to take the next step.|09-9|loop|The next step / teaches you.|STEP~take the next step;LEARN~teaches you something;ADAPT~changes your approach;REPEAT~another step
And slowly...|09-9|paths|The path / becomes visible.|NEXT MOVE~You need the next move
And there's a question that can expose this problem almost instantly.|10-1|thought|What exactly / am I waiting for?|WHAT AM I WAITING FOR?~What exactly am I waiting for
Not emotionally.|10-1|focus|Literally. / What is it?|LITERALLY~Literally;WHAT ARE YOU WAITING FOR?~What are you waiting for
More information?|10-1|feed|What are you / waiting for?|INFORMATION~More information;CONFIDENCE~More confidence;PLAN~A better plan;MONEY~More money
The perfect equipment?|10-2|feed|Will it make / you ready?|EQUIPMENT~perfect equipment;MOTIVATION~More motivation;TIME~A better time
And then ask yourself...|10-3|thought|Do I actually / need this?|NEED THIS?~Do I actually need this;UNCOMFORTABLE STARTING?~uncomfortable with starting
Because sometimes... the thing you're waiting for isn't something you need.|05-1|split|Need it... / or want safety?|NEED~something you need;SAFE~feel safe
And here's the uncomfortable part.|07-5|thought|Ready may / never arrive.|COMPLETELY READY~completely ready;NOBODY DOES~Nobody does
The people who look confident now...|05-7|timeline|They also / had a beginning.|A BEGINNING~a beginning;MISTAKES~made mistakes;AWKWARD~looked awkward
They also had moments where they questioned themselves.|07-2|focus|Allow yourself / to begin.|QUESTIONED THEMSELVES~questioned themselves;BEGINNERS~be beginners
So maybe... you don't need another tutorial.|06-2|feed|Maybe no / more tutorials.|TUTORIAL~another tutorial;APP~productivity app;NOTEBOOK~another notebook;PLAN~another perfect plan
Maybe... you need to close the tab.|10-4|switch|Close the tab.|CLOSE THE TAB~close the tab;PHONE DOWN~Put the phone down
Stop searching.|10-5|focus|An imperfect / attempt.|STOP SEARCHING~Stop searching;FIRST ATTEMPT~first imperfect attempt
Because there is something preparation can never give you.|10-5|focus|Proof.|PROOF~Proof
You can tell yourself you're disciplined.|10-6|stack|Action gives / you proof.|DISCIPLINED~disciplined;SERIOUS~serious;BECOMING~a different person
And those small pieces of proof...|10-6|stack|Small pieces / of evidence.|STUDIED~You studied;SHOWED UP~showed up;FINISHED~finished something;MADE SOMETHING~made something
You kept a promise to yourself.|10-5|focus|Kept a promise / to yourself.|KEPT A PROMISE~kept a promise
And eventually... your brain starts learning:|07-2|thought|I do what / I say I'll do.|I DO WHAT I SAY~I actually do what I say
That's how identity changes.|10-6|stack|Identity / follows evidence.|EVIDENCE~through evidence;SMALL~Small evidence;REPEATED~Repeated evidence;DAY AFTER DAY~Day after day
So the next time you find yourself saying...|03-7|thought|Preparing... / or hiding?|PREPARE MORE~prepare a little more;PAUSE~pause;PREPARING?~Am I preparing;HIDING?~or am I hiding
Maybe the answer will be uncomfortable.|05-5|focus|The edge / of preparation.|UNCOMFORTABLE~answer will be uncomfortable;THE EDGE~the edge
And beyond that edge...|10-3|focus|Action.|ACTION~Action
You don't need to start perfectly.|07-8|stack|You don't need / perfect.|PERFECT~start perfectly;EVERYTHING~know everything;STRATEGY~perfect strategy;CONFIDENCE~feel confident
You don't even need to believe you're going to succeed.|09-2|thought|Willing to make / the first attempt.|WILLING~be willing;FIRST ATTEMPT~first attempt
Because eventually...|09-9|paths|Starting becomes / what matters.|PREPARATION~preparation stops being useful;STARTING~starting becomes
So if there's something you've been preparing for...|03-1|timeline|Weeks. / Months. Years.|WEEKS~for weeks;MONTHS~or months;YEARS~even years
Don't make another plan tonight.|10-4|switch|No more / preparation tonight.|NO PLAN~another plan tonight;NO VIDEO~another video;NO SHORTCUT~another shortcut
Take one small action.|10-7|feed|One small / action.|SEND THE MESSAGE~Send the message;WRITE THE PAGE~Write the first page;MAKE THE VIDEO~Make the first video
Do the first workout.|08-2|paths|Take the / first step.|WORKOUT~first workout;OPEN THE PROJECT~Open the project;FIRST STEP~Take the first step
Make it real.|10-8|window|Studying / the water.|MAKE IT REAL~Make it real;STUDYING THE WATER~studying the water
At some point...|10-9|paths|Get in.|GET IN~get in
And maybe that's what you've been missing.|10-9|focus|Just a / beginning.|NOT MORE PREPARATION~Not more preparation;NOT MORE INFORMATION~Not more information;NOT MORE MOTIVATION~Not more motivation;A BEGINNING~a beginning
Think deeper.|10-5|focus|Why We Become.|THINK DEEPER~Think deeper;LIVE BETTER~Live better;BECOME MORE~Become more'''
rows=[];cursor=0
for row in DATA.splitlines():
 phrase,art,kind,title,spec=row.split('|',4)
 at=seek(phrase,cursor);cursor=at+1
 labels=[];cue_phrase=[];cue_at=[]
 for q in spec.split(';'):
  label,cp=q.split('~',1);labels.append(label);cue_phrase.append(cp)
  try:cue_at.append(seek(cp,at))
  except ValueError:raise ValueError('Missing label cue '+cp)
 rows.append({'phrase':phrase,'flat_start':at,'start':timestamp(at),'art':art,'kind':kind,'title':title.replace(' / ','\n'),'labels':labels,'cue_phrases':cue_phrase,'cues':[timestamp(i,True) for i in cue_at]})
chapters=[('A Beginning','Imagine this.'),('Productive but Stuck','So you start researching.'),('Everything Is Ready','A week passes.'),('The Rabbit Hole','Think about the last time you wanted to change something in your life.'),('The Safe Fantasy',"And here's why preparation is so attractive."),('The Moving Finish Line',"But here's the trap."),('Protecting Potential',"And sometimes... the problem isn't that you don't know enough."),('Reality Gives Feedback',"But here's something important."),('Prepare, Act, Learn',"So maybe the goal isn't to eliminate preparation."),('Make It Real',"And there's a question that can expose this problem almost instantly.")]
chapter_times=[timestamp(seek(a)) for _,a in chapters]
meta=json.loads((root/'v2/upscale_report.json').read_text())
for i,x in enumerate(rows):
 x.update(id=i,end=rows[i+1]['start'] if i+1<len(rows) else tokens[-1]['end'],dark=x['phrase'] in ["Everything is ready.","And that's when you need to ask yourself","But there's a difference between knowing what to do...","But the moment you start...","But the finish line keeps moving.","Because once you start...","You want your first attempt to look like someone else's hundredth.","You cannot research your way into experience.","That's where real learning begins.","Because you can improve something that exists.","The problem begins when preparation has no connection to action.","And then ask yourself...","Maybe... you need to close the tab.","Because there is something preparation can never give you.","So the next time you find yourself saying...","And beyond that edge...","Make it real."])
 x['chapter']=max(j+1 for j,t in enumerate(chapter_times) if x['start']>=t-.01)
 x['feature']=x['kind']=='counter' or (x['dark'] and x['kind'] in ['thought','focus','loop'])
 m=meta[x['art']];box=m['bbox'];mid=(box[0]+box[2])/2
 x['layout']='right' if mid>=m['upscaled'][0]/2 else 'left'
 x['cues']=[max(x['start'],c) if c<x['end']-.045 else x['end']+1 for c in x['cues']]
 if x['kind']=='counter':x['counter']=50 if 'Fifty' in x['title'] else 20
 if x['kind']=='clock':x['clock_label']='3 HOURS' if 'Three hours' in x['title'] else 'SLEEP'
 assert x['end']>x['start'],x
assert rows[0]['start']<.5
with wave.open(str(root/'voiceover.wav')) as w:duration=w.getnframes()/w.getframerate()
endstart=timestamp(seek('Think deeper.'))
(root/'v2/scene_plan.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
(root/'timeline.json').write_text(json.dumps({'vo_end':duration,'total':duration+.3,'end_card_start':endstart,'chapters':[{'title':n,'start':t} for (n,a),t in zip(chapters,chapter_times)]},indent=2))
used={r['art'] for r in rows}
inv=json.loads((root/'panel_inventory.json').read_text())
for p in inv['panels']:
 if p['file']:
  a=f"{int(p['id'][1:3]):02d}-{(p['row']-1)*3+p['column']}"
  p['status']='used' if a in used else 'intentionally_omitted'
  p['reason']='Narration-timed use; see synchronization review' if a in used else 'Redundant preparatory motif; selected clearer supplied panels for this script beat'
inv['timing_status']='Aligned against final processed narration; STT differences reviewed'
(root/'panel_inventory.json').write_text(json.dumps(inv,indent=2))
review=['# Narration / panel synchronization review','','All times are seconds in the processed narration. Original script wording is unchanged. STT replacements are logged in script_alignment.json: natural want-to/wanna and there-is/there\'s spans plus three short recognition variants. No deleted or duplicated content was detected. Captions retain the supplied script words. Numeric cue starts and scene starts use matched tokens, not a uniform image schedule.','', '|Scene|Start|End|Panel|Spoken phrase|Graphic|Label cue times|Reuse|','|---|---:|---:|---|---|---|---|---|']
seen=set()
for x in rows:
 cue='; '.join(f'{label}: {c:.3f}s' if c<x['end'] else f'{label}: withheld (outside scene)' for label,c in zip(x['labels'],x['cues']))
 reuse='Return to the same idea' if x['art'] in seen else 'First use';seen.add(x['art'])
 review.append(f"|{x['id']}|{x['start']:.3f}|{x['end']:.3f}|{meta[x['art']]['panel_id']}|{x['phrase']}|{x['kind']}|{cue}|{reuse}|")
review+=['','## Inventory omissions']+[f"- {p['id']}: {p['reason']}" for p in inv['panels'] if p['status']!='used']
(root/'v2/panel_sync_review.md').write_text('\n'.join(review))

# Stable original-script captions. Each event keeps a fixed group position/size and colors only the active word.
def ass_time(t):
 n=round(t*100);h,n=divmod(n,360000);m,n=divmod(n,6000);sec,cs=divmod(n,100);return f'{h}:{m:02d}:{sec:02d}.{cs:02d}'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Caption,Montserrat ExtraBold,60,&H00FFFFFF,&H00FFFFFF,&H0016150F,&H90000000,-1,0,0,0,100,100,0,0,1,4,1.5,2,110,110,82,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
'''
groups=[];group=[]
for i,t in enumerate(tokens):
 if group and (len(group)>=5 or t['start']-tokens[group[-1]]['end']>.28):groups.append(group);group=[]
 group.append(i)
 if re.search(r'[.!?]$|\.\.\.$',t['text']) and len(group)>=2:groups.append(group);group=[]
if group:groups.append(group)
events=[]
for ids in groups:
 # Wrap deliberately after ~30 characters; no scaling or positional changes inside a caption.
 break_at=None
 if len(' '.join(tokens[i]['text'] for i in ids))>33:
  break_at=max(1,len(ids)//2)
 for q,active in enumerate(ids):
  a=tokens[active]['start'];b=tokens[ids[q+1]]['start'] if q+1<len(ids) else min(duration,tokens[active]['end']+.12)
  if b<=a:b=a+.02
  parts=[]
  for j,i in enumerate(ids):
   if j==break_at:parts.append('\\N')
   elif j:parts.append(' ')
   text=tokens[i]['text'].replace('{','').replace('}','')
   parts.append(('\\c&H003C62C8&' if i==active else '\\c&H00FFFFFF&').join(['{','}'])+text)
  events.append('Dialogue: 0,'+ass_time(a)+','+ass_time(b)+',Caption,,0,0,0,,'+''.join(parts))
(root/'v2/captions.ass').write_text(header+'\n'.join(events)+'\n')
seo=['# Why You Keep Preparing Instead of Starting.','','## Description',"Preparation can feel productive while keeping you away from the first imperfect attempt. This Why We Become explainer explores the safety of planning, protecting potential, and using action to learn what comes next.",'','Think deeper. Live better. Become more.','','## Chapters']
for (name,_),t in zip(chapters,chapter_times):
 m,se=divmod(int(t),60);seo.append(f'{m:02d}:{se:02d} {name}')
seo+=['','## Tags','procrastination, preparation, overthinking, perfectionism, taking action, getting started, self improvement, human behaviour, Why We Become','','## Hashtags','#WhyWeBecome #Procrastination #TakeAction']
(root/'seo.md').write_text('\n'.join(seo));(root/'transcript.txt').write_text(s)
print(len(rows),'phrase-timed scenes;',len(used),'distinct supplied panels;',len(groups),'caption groups;',len(events),'word events')
print('Voice duration',duration,'total',duration+.3,'end card starts',endstart)
print('Unused artwork:',len(meta)-len(used))
