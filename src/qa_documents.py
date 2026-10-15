from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'tools'/'pydeps'))
import pymupdf,ezdxf
from PIL import Image,ImageOps,ImageDraw
qa=ROOT/'qa'/'pdf_render';qa.mkdir(parents=True,exist_ok=True)
results=[]
for pdf in sorted((ROOT/'docs').glob('*.pdf')):
    d=pymupdf.open(pdf);images=[]
    for i,page in enumerate(d):
        pix=page.get_pixmap(matrix=pymupdf.Matrix(1.25,1.25),alpha=False)
        name=f'{pdf.stem}_{i+1:02d}.png';pix.save(str(qa/name));images.append(qa/name)
        text=page.get_text()
        bad=[]
        for block in page.get_text('dict')['blocks']:
            if block['type']!=0:continue
            for line in block['lines']:
                for s in line['spans']:
                    x0,y0,x1,y1=s['bbox']
                    if x0<0 or y0<0 or x1>page.rect.width+.1 or y1>page.rect.height+.1:bad.append(s['text'])
        results.append(dict(pdf=pdf.name,page=i+1,characters=len(text),text_outside_page=bad,rendered=True))
    for batch in range(0,len(images),8):
        thumbs=[]
        for f in images[batch:batch+8]:
            im=Image.open(f).convert('RGB');im.thumbnail((420,550))
            thumb=Image.new('RGB',(440,590),'#dfe8ed');thumb.paste(im,((440-im.width)//2,20))
            ImageDraw.Draw(thumb).text((10,570),f.name.encode('ascii','replace').decode(),fill='black');thumbs.append(thumb)
        contact=Image.new('RGB',(440*4,590*2),'#dfe8ed')
        for n,im in enumerate(thumbs):contact.paste(im,((n%4)*440,(n//4)*590))
        contact.save(qa/f'{pdf.stem}_contact_{batch//8+1}.png')
dxfs=[]
for f in (ROOT/'cut').glob('*.dxf'):
    doc=ezdxf.readfile(f);audit=doc.audit()
    dxfs.append(dict(file=f.name,units_mm=doc.units==4,errors=len(audit.errors),cut_entities=sum(1 for e in doc.modelspace() if e.dxf.layer=='CUT')))
out=dict(pdf_pages=results,dxf_checks=dxfs,all_technical_checks_pass=all(not r['text_outside_page'] for r in results) and all(r['units_mm'] and r['errors']==0 and r['cut_entities']>0 for r in dxfs),visual_review='PENDING_MODEL_INSPECTION')
(ROOT/'qa'/'document_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('PDF pages:',len(results),'DXFs:',len(dxfs),'technical checks:',out['all_technical_checks_pass'])
