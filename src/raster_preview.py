"""Accurate depth-buffered orthographic raster of CAD triangles, without OpenGL."""
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'tools'/'pydeps'))
import numpy as np
from PIL import Image,ImageDraw,ImageFont
data=json.loads((ROOT/'data'/'meshes.json').read_text())
font=ImageFont.truetype(r'C:\Windows\Fonts\arialbd.ttf',42)
small=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',17)
def render(name,cut=False):
    W,H=1800,1100
    img=np.empty((H,W,3),dtype=np.uint8);img[:]=[237,241,244]
    zb=np.full((H,W),-np.inf)
    yaw=.55;pitch=.92;cy,sy,cp,sp=math.cos(yaw),math.sin(yaw),math.cos(pitch),math.sin(pitch)
    R=np.array([[cy,-sy,0],[-sy*cp,-cy*cp,-sp],[-sy*sp,-cy*sp,cp]])
    selected=[]
    for m in data:
        if m['group']=='Keepouts' and not m['name'].startswith('Prop_visual'):continue
        if cut and m['name'] in ['Fuselage_roof_frame','Battery_hatch','Avionics_hatch','Cockpit_foam','Nacelle_skin_L','Nacelle_skin_R']:continue
        vs=np.array(m['vertices']);ts=np.array(m['triangles']);selected.append((m,vs,ts,vs@R.T))
    allv=np.concatenate([s[3] for s in selected]);mins=allv.min(axis=0);maxs=allv.max(axis=0)
    scale=min(1460/(maxs[0]-mins[0]),740/(maxs[1]-mins[1]));offset=np.array([W/2,610])-(mins[:2]+maxs[:2])/2*scale
    light=np.array([-.3,-.4,.866])
    for m,vs,ts,proj in selected:
        proj=proj.copy();proj[:,:2]=proj[:,:2]*scale+offset
        for ids in ts:
            tri=proj[ids];n=np.cross(vs[ids[1]]-vs[ids[0]],vs[ids[2]]-vs[ids[0]])
            lum=.58+.42*abs(float(n@light))/(np.linalg.norm(n)+1e-12)
            color=np.clip(np.array(m['color'])*255*lum+9,0,255).astype(np.uint8)
            x0=max(0,int(np.floor(tri[:,0].min())));x1=min(W-1,int(np.ceil(tri[:,0].max())))
            y0=max(0,int(np.floor(tri[:,1].min())));y1=min(H-1,int(np.ceil(tri[:,1].max())))
            if x1<x0 or y1<y0:continue
            x,y=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
            xa,ya,za=tri[0];xb,yb,zbb=tri[1];xc,yc,zc=tri[2]
            den=(yb-yc)*(xa-xc)+(xc-xb)*(ya-yc)
            if abs(den)<1e-10:continue
            u=((yb-yc)*(x-xc)+(xc-xb)*(y-yc))/den
            v=((yc-ya)*(x-xc)+(xa-xc)*(y-yc))/den;w=1-u-v
            z=u*za+v*zbb+w*zc
            target=zb[y0:y1+1,x0:x1+1]
            mask=(u>=-1e-7)&(v>=-1e-7)&(w>=-1e-7)&(z>target)
            target[mask]=z[mask];img[y0:y1+1,x0:x1+1][mask]=color
    im=Image.fromarray(img);d=ImageDraw.Draw(im)
    d.text((85,60),'SR-71 / 600',font=font,fill='#183448')
    d.text((85,117),'TWIN PUSHER  |  420 mm SPAN  |  '+('INTERNAL LAYOUT' if cut else 'P0 ENGINEERING PROTOTYPE'),font=small,fill='#607888')
    d.text((85,1040),'CAD geometry. Purchased hardware shown as envelopes. Propellers illustrative. NOT FLIGHT RELEASED.',font=small,fill='#607888')
    im.save(ROOT/'docs'/name)
render('overview.png');render('cutaway.png',True)
print('Depth-buffer previews rendered')
