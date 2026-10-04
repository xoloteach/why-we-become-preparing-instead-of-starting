"""Neural reconstruction and soft masking of supplied panels; native originals preserved."""
from pathlib import Path
import sys,os,json,time
sys.path.insert(0,'/data/cv_sr')
import cv2,numpy as np
root=Path(__file__).resolve().parent
cv2.setNumThreads(2)
for p in ['v2/native','v2/upscaled','v2/layers','v2/qa']: (root/p).mkdir(parents=True,exist_ok=True)
sr=cv2.dnn_superres.DnnSuperResImpl_create();sr.readModel('/data/sr_models/FSRCNN_x4.pb');sr.setModel('fsrcnn',4)
inv=json.loads((root/'panel_inventory.json').read_text());report={}
for item in inv['panels']:
 if not item['file']:continue
 sheet=int(item['id'][1:3]);p=(item['row']-1)*3+item['column'];art=f'{sheet:02d}-{p}';name=f's{sheet:02d}_p{p}.png'
 native=cv2.imread(str(root/item['file']))
 target=root/'v2/upscaled'/name
 if target.exists():b=cv2.imread(str(target))
 else:
  b=sr.upsample(native);l=cv2.resize(native,(b.shape[1],b.shape[0]),interpolation=cv2.INTER_LANCZOS4)
  b=cv2.addWeighted(b,.78,l,.22,0);b=cv2.addWeighted(b,1.10,cv2.GaussianBlur(b,(0,0),.8),-.10,0)
  tmp=target.with_name(name+'.tmp.png');cv2.imwrite(str(tmp),b);os.replace(tmp,target)
 cv2.imwrite(str(root/'v2/native'/name),native)
 gray=cv2.cvtColor(b,cv2.COLOR_BGR2GRAY)
 edges=np.concatenate([b[:16].reshape(-1,3),b[-16:].reshape(-1,3),b[:,:16].reshape(-1,3),b[:,-16:].reshape(-1,3)])
 paper=np.percentile(edges,80,axis=0)
 delta=np.max(abs(b.astype(np.float32)-paper),axis=2)
 alpha=np.clip((delta-15)/40,0,1).astype(np.float32)
 # Fill enclosed pale faces/interiors from external object contours, not a convex hull across unrelated objects.
 solid=(gray<215).astype(np.uint8)*255
 contours,_=cv2.findContours(solid,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
 fill=np.zeros_like(solid)
 for ct in contours:
  if cv2.contourArea(ct)>220:cv2.drawContours(fill,[ct],-1,255,-1)
 alpha=np.maximum(alpha,cv2.GaussianBlur(fill,(5,5),.8)/255.)
 # Suppress isolated dust without slicing connected artwork.
 count,labels,stats,_=cv2.connectedComponentsWithStats((alpha>.35).astype(np.uint8),8)
 for j in range(1,count):
  if stats[j,cv2.CC_STAT_AREA]<80:alpha[labels==j]=0
 layer=np.dstack([b,(alpha*255).astype(np.uint8)])
 lp=root/'v2/layers'/name;tmp=lp.with_name(name+'.tmp.png');cv2.imwrite(str(tmp),layer);os.replace(tmp,lp)
 yy,xx=np.where(alpha>.5)
 box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else [0,0,b.shape[1],b.shape[0]]
 report[art]={'panel_id':item['id'],'native':list(native.shape[:2][::-1]),'upscaled':list(b.shape[:2][::-1]),'bbox':box,'method':'FSRCNN x4 + 22% Lanczos blend, mild sharpen','paper_cut_backing':sheet==10 and p in [8,9] or sheet==6 and p==7}
 print('Prepared',art,flush=True)
(root/'v2/upscale_report.json').write_text(json.dumps(report,indent=2))
(root/'upscale_report.json').write_text(json.dumps({'status':'reconstructed; visual edge QA pending','method':'FSRCNN x4, 22% Lanczos blend','neural_reconstruction_performed':True,'panels':report},indent=2))
print('DONE:',len(report),'neural-reconstructed panels',flush=True)
