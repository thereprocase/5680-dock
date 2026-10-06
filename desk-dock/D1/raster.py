from pathlib import Path
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cadquery as cq

FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,bold=False):
    return ImageFont.truetype(BOLD if bold else FONT,n)

def render(objects,size,camvec,target=None,pad=25):
    cam=np.array(camvec,dtype=float);cam/=np.linalg.norm(cam)
    right=np.cross(cam,[0,0,1.]);right/=np.linalg.norm(right)
    up=np.cross(right,cam)
    basis=np.array([right,up,cam]).T
    meshes=[]
    for shape,color in objects:
        vs,fs=shape.tessellate(.35,.2)
        vertices=np.array([v.toTuple() for v in vs])
        triangles=vertices[np.array(fs)]
        meshes.append((triangles,np.array(color,dtype=float)))
    allpts=np.concatenate([t.reshape(-1,3) for t,c in meshes])@basis
    lo=allpts[:,:2].min(0);hi=allpts[:,:2].max(0)
    scale=min((size[0]-2*pad)/(hi[0]-lo[0]),(size[1]-2*pad)/(hi[1]-lo[1]))
    center=(lo+hi)/2
    def project(points):
        pts=np.array(points)@basis
        pts[...,:2]=(pts[...,:2]-center)*scale
        pts[...,0]+=size[0]/2
        pts[...,1]=size[1]/2-pts[...,1]
        return pts
    pix=np.full((size[1],size[0],3),248,dtype=np.uint8)
    dep=np.full((size[1],size[0]),-np.inf,dtype=np.float32)
    normbuf=np.zeros((size[1],size[0],3),dtype=np.float32)
    light=np.array([-.3,.5,1]);light/=np.linalg.norm(light)
    for triangles,color in meshes:
        for tri in triangles:
            normal=np.cross(tri[1]-tri[0],tri[2]-tri[0])
            nl=np.linalg.norm(normal)
            if nl<1e-8:continue
            normal/=nl
            if np.dot(normal,cam)<0:normal=-normal
            p=project(tri)
            x0=max(0,int(np.floor(p[:,0].min())));x1=min(size[0]-1,int(np.ceil(p[:,0].max())))
            y0=max(0,int(np.floor(p[:,1].min())));y1=min(size[1]-1,int(np.ceil(p[:,1].max())))
            if x0>x1 or y0>y1:continue
            a,b,c=p
            det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(det)<1e-8:continue
            yy,xx=np.mgrid[y0:y1+1,x0:x1+1]
            xx=xx+.5;yy=yy+.5
            w0=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/det
            w1=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/det
            w2=1-w0-w1
            z=w0*a[2]+w1*b[2]+w2*c[2]
            old=dep[y0:y1+1,x0:x1+1]
            mask=(w0>=-1e-7)&(w1>=-1e-7)&(w2>=-1e-7)&(z>old)
            old[mask]=z[mask]
            shade=.58+.38*max(0,np.dot(normal,light))+.10*max(0,np.dot(normal,cam))
            rgb=np.clip(color*shade,0,255).astype(np.uint8)
            pix[y0:y1+1,x0:x1+1][mask]=rgb
            normbuf[y0:y1+1,x0:x1+1][mask]=normal
    # Crisp boundaries at real surface discontinuities, without triangle lines.
    edge=np.zeros(dep.shape,dtype=bool)
    for axis in (0,1):
        d2=np.roll(dep,1,axis);n2=np.roll(normbuf,1,axis)
        finite=np.isfinite(dep)&np.isfinite(d2)
        jump=np.zeros(dep.shape,dtype=bool)
        jump[finite]=(np.abs(dep[finite]-d2[finite])>1.3)|((normbuf[finite]*n2[finite]).sum(-1)<.78)
        edge|=jump
    pix[edge]=(pix[edge]*.68).astype(np.uint8)
    return Image.fromarray(pix),project

def arrow(draw,start,end,color,width=5):
    a=np.array(start,dtype=float);b=np.array(end,dtype=float)
    d=b-a;d/=np.linalg.norm(d);p=np.array([-d[1],d[0]])
    draw.line([tuple(a),tuple(b)],fill=color,width=width)
    draw.polygon([tuple(b),tuple(b-15*d+6*p),tuple(b-15*d-6*p)],fill=color)

