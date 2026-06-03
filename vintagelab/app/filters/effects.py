"""
VintageLab Effect Modules - Dazz Cam accurate implementations
All functions: numpy float32 BGR 0-255 in/out
"""
import cv2
import numpy as np
import random

def to_float(img): return img.astype(np.float32)
def to_uint8(img): return np.clip(img, 0, 255).astype(np.uint8)

def build_lut(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return np.interp(np.arange(256), xs, ys).astype(np.float32)

def apply_lut(img, lut):
    out = img.copy()
    for c in range(3):
        idx = np.clip(img[:,:,c], 0, 255).astype(np.uint8)
        out[:,:,c] = lut[idx]
    return out

def apply_lut_per_channel(img, lut_b, lut_g, lut_r):
    out = img.copy()
    out[:,:,0] = lut_b[np.clip(img[:,:,0],0,255).astype(np.uint8)]
    out[:,:,1] = lut_g[np.clip(img[:,:,1],0,255).astype(np.uint8)]
    out[:,:,2] = lut_r[np.clip(img[:,:,2],0,255).astype(np.uint8)]
    return out

# ── Grain ──────────────────────────────────────────────────────────────────────
def add_grain(img, strength=18, colored=False):
    h, w = img.shape[:2]
    if colored:
        noise = np.random.normal(0, strength, (h, w, 3)).astype(np.float32)
    else:
        noise = np.random.normal(0, strength, (h, w)).astype(np.float32)
        noise = np.stack([noise]*3, axis=-1)
    return img + noise

def add_grain_lum(img, strength=14):
    lab = cv2.cvtColor(to_uint8(img), cv2.COLOR_BGR2LAB).astype(np.float32)
    h, w = img.shape[:2]
    noise = np.random.normal(0, strength, (h, w)).astype(np.float32)
    lab[:,:,0] = np.clip(lab[:,:,0] + noise, 0, 255)
    return cv2.cvtColor(to_uint8(lab), cv2.COLOR_LAB2BGR).astype(np.float32)

# ── Color Ops ──────────────────────────────────────────────────────────────────
def temp(img, t):
    out = img.copy()
    if t > 0:
        out[:,:,2] = np.clip(out[:,:,2]+t, 0, 255)
        out[:,:,0] = np.clip(out[:,:,0]-t*0.4, 0, 255)
    else:
        out[:,:,0] = np.clip(out[:,:,0]+abs(t), 0, 255)
        out[:,:,2] = np.clip(out[:,:,2]-abs(t)*0.4, 0, 255)
    return out

def sat(img, scale):
    hsv = cv2.cvtColor(to_uint8(img), cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:,:,1] = np.clip(hsv[:,:,1]*scale, 0, 255)
    return cv2.cvtColor(to_uint8(hsv), cv2.COLOR_HSV2BGR).astype(np.float32)

def contrast(img, factor, mid=128):
    return np.clip((img - mid)*factor + mid, 0, 255)

def brightness(img, amt):
    return np.clip(img + amt, 0, 255)

def fade(img, black=20, white=235):
    lut = build_lut([(0,black),(255,white)])
    return apply_lut(img, lut)

def crush_blacks(img, amt=15):
    lut = build_lut([(0,0),(amt,0),(255,255)])
    return apply_lut(img, lut)

def desat(img, amt=0.3):
    gray = cv2.cvtColor(to_uint8(img), cv2.COLOR_BGR2GRAY)
    gray3 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR).astype(np.float32)
    return img*(1-amt) + gray3*amt

def split_tone(img, shadow=(0,0,0), highlight=(255,255,255), strength=0.07):
    lum = cv2.cvtColor(to_uint8(img), cv2.COLOR_BGR2GRAY).astype(np.float32)/255.0
    out = img.copy()
    for c in range(3):
        sh_w = (1-lum)*strength
        hl_w = lum*strength
        out[:,:,c] = np.clip(img[:,:,c]+sh_w*(shadow[c]-img[:,:,c])+hl_w*(highlight[c]-img[:,:,c]),0,255)
    return out

def tint_green(img, amt=8):
    out = img.copy()
    out[:,:,1] = np.clip(out[:,:,1]+amt, 0, 255)
    return out

# ── Vignette ───────────────────────────────────────────────────────────────────
def vignette(img, strength=0.5, radius=0.75):
    h, w = img.shape[:2]
    cx, cy = w/2, h/2
    Y, X = np.ogrid[:h,:w]
    dist = np.sqrt(((X-cx)/cx)**2 + ((Y-cy)/cy)**2)
    mask = np.clip(1-(dist-radius)/(1-radius),0,1)**2
    return np.clip(img * (1-strength*(1-mask[...,np.newaxis])), 0, 255)

def vignette_oval(img, strength=0.55, rx=0.65, ry=0.70):
    h, w = img.shape[:2]
    cx, cy = w/2, h/2
    Y, X = np.ogrid[:h,:w]
    dist = np.sqrt(((X-cx)/(cx*rx))**2 + ((Y-cy)/(cy*ry))**2)
    mask = np.clip(1-(dist-1.0)/0.5, 0, 1)**2
    return np.clip(img * (1-strength*(1-mask[...,np.newaxis])), 0, 255)

# ── Blur / Glow ────────────────────────────────────────────────────────────────
def glow(img, strength=0.2, r=21):
    blurred = cv2.GaussianBlur(to_uint8(img), (r|1, r|1), 0).astype(np.float32)
    return np.clip(img*(1-strength)+blurred*strength*1.15, 0, 255)

def lens_blur(img, amt=1):
    k = amt*2+1
    return cv2.GaussianBlur(to_uint8(img),(k,k),0).astype(np.float32)

def halation(img, strength=0.25, color=(20,60,255)):
    gray = cv2.cvtColor(to_uint8(img), cv2.COLOR_BGR2GRAY).astype(np.float32)
    bright = np.clip((gray-190)/65, 0, 1)
    blurred = cv2.GaussianBlur(bright,(61,61),0)
    out = img.copy()
    for c, col in enumerate(color[::-1]):
        out[:,:,c] = np.clip(out[:,:,c]+blurred*col*strength, 0, 255)
    return out

# ── Dust / Scratches ───────────────────────────────────────────────────────────
def dust(img, n=30, seed=42):
    rng = np.random.RandomState(seed)
    out = img.copy(); h,w=img.shape[:2]
    for _ in range(n):
        x,y=rng.randint(0,w),rng.randint(0,h)
        r=rng.randint(1,3); br=rng.randint(140,255)
        cv2.circle(out,(x,y),r,(br,br,br),-1)
    return out

def scratches(img, n=3, seed=7):
    rng = np.random.RandomState(seed)
    out = img.copy(); h,w=img.shape[:2]
    for _ in range(n):
        x=rng.randint(0,w); br=rng.randint(160,230)
        cv2.line(out,(x,0),(x+rng.randint(-4,4),h),(br,br,br),1)
    return out

# ── Light Leaks ────────────────────────────────────────────────────────────────
def light_leak(img, color=(255,120,30), pos='top-right', intensity=0.35, spread=0.5):
    h,w=img.shape[:2]
    leak=np.zeros((h,w,3),np.float32)
    pm={'top-right':(w,0),'top-left':(0,0),'bottom-right':(w,h),'bottom-left':(0,h),'right':(w,h//2),'left':(0,h//2),'top':(w//2,0),'bottom':(w//2,h)}
    cx,cy=pm.get(pos,(w,0))
    Y,X=np.ogrid[:h,:w]
    dist=np.sqrt((X-cx)**2+(Y-cy)**2).astype(np.float32)
    radius=np.sqrt(h**2+w**2)*spread
    mask=np.clip(1-dist/radius,0,1)**1.6
    for c,col in enumerate(color[::-1]):
        leak[:,:,c]=mask*col
    return np.clip(img+leak*intensity*2,0,255)

# ── VHS Effects ────────────────────────────────────────────────────────────────
def vhs_noise(img, s=0.12):
    h,w=img.shape[:2]; out=img.copy()
    for _ in range(int(h*0.06)):
        y=random.randint(0,h-1); bh=random.randint(1,4)
        nv=random.uniform(-s*255,s*255)
        out[y:y+bh,:]=np.clip(out[y:y+bh,:]+nv,0,255)
    return out

def rgb_shift(img, r=4, b=-4):
    h,w=img.shape[:2]; out=img.copy()
    if r>0: out[:,r:,2]=img[:,:w-r,2]; out[:,:r,2]=img[:,0:1,2]
    elif r<0: sr=abs(r); out[:,:w-sr,2]=img[:,sr:,2]
    if b<0: sb=abs(b); out[:,:w-sb,0]=img[:,sb:,0]
    elif b>0: out[:,b:,0]=img[:,:w-b,0]
    return out

def scanlines(img, gap=3, s=0.12):
    h,w=img.shape[:2]; mask=np.ones((h,w,3),np.float32)
    mask[::gap,:]=1-s
    return np.clip(img*mask,0,255)

def vhs_tracking(img, s=8):
    h,w=img.shape[:2]; out=img.copy()
    for _ in range(random.randint(2,5)):
        y0=random.randint(0,h-20); y1=y0+random.randint(3,18)
        sh=random.randint(-s,s)
        if sh>0: out[y0:y1,sh:]=img[y0:y1,:w-sh]; out[y0:y1,:sh]=0
        elif sh<0: s2=abs(sh); out[y0:y1,:w-s2]=img[y0:y1,s2:]; out[y0:y1,w-s2:]=0
    return out

def vhs_blur(img, k=3):
    kern=np.zeros((k,k)); kern[k//2,:]=1.0/k
    return cv2.filter2D(to_uint8(img),-1,kern).astype(np.float32)

def interlace(img):
    h,w=img.shape[:2]; out=img.copy(); sh=2
    out[1::2,sh:]=img[1::2,:w-sh]
    return out

def date_stamp(img, text='12/25/98', color=(40,40,220), alpha=0.9):
    out=to_uint8(img).copy(); h,w=out.shape[:2]
    font=cv2.FONT_HERSHEY_COMPLEX_SMALL
    scale=max(0.55,w/700); thick=max(1,int(scale))
    (tw,th),_=cv2.getTextSize(text,font,scale,thick)
    x=w-tw-int(w*0.03); y=h-int(h*0.03)
    ov=out.copy()
    cv2.putText(ov,text,(x,y),font,scale,color,thick,cv2.LINE_AA)
    return cv2.addWeighted(out,1-alpha,ov,alpha,0).astype(np.float32)

def border_film(img):
    """Film strip perforations border"""
    h,w=img.shape[:2]; out=img.copy()
    bw=int(w*0.06); bh=int(h*0.05)
    out[:bh,:]=0; out[h-bh:,:]=0
    # sprocket holes top
    rng=np.random.RandomState(0)
    hole_w,hole_h=int(w*0.025),int(h*0.025)
    for x in range(int(w*0.02),w,int(w*0.07)):
        cv2.rectangle(out,(x,int(bh*0.15)),(x+hole_w,int(bh*0.15)+hole_h),(20,20,20),-1)
        cv2.rectangle(out,(x,h-bh+int(bh*0.6)),(x+hole_w,h-bh+int(bh*0.6)+hole_h),(20,20,20),-1)
    return out

def sepia(img, strength=1.0):
    r,g,b=img[:,:,2],img[:,:,1],img[:,:,0]
    sr=np.clip(r*0.393+g*0.769+b*0.189,0,255)
    sg=np.clip(r*0.349+g*0.686+b*0.168,0,255)
    sb=np.clip(r*0.272+g*0.534+b*0.131,0,255)
    sep=np.stack([sb,sg,sr],axis=-1)
    return img*(1-strength)+sep*strength

def overexpose(img, amt=60):
    lum=cv2.cvtColor(to_uint8(img),cv2.COLOR_BGR2GRAY).astype(np.float32)/255
    mask=np.clip((lum-0.55)/0.45,0,1)[...,np.newaxis]
    return np.clip(img+mask*amt,0,255)

def crt_barrel(img):
    h,w=img.shape[:2]
    k1,k2=0.04,0.015; cx,cy=w/2.0,h/2.0
    map_x=np.zeros((h,w),np.float32); map_y=np.zeros((h,w),np.float32)
    Y,X=np.mgrid[0:h,0:w]
    dx=(X-cx)/cx; dy=(Y-cy)/cy; r2=dx*dx+dy*dy
    fac=1+k1*r2+k2*r2*r2
    map_x=(dx*fac*cx+cx).astype(np.float32)
    map_y=(dy*fac*cy+cy).astype(np.float32)
    d=cv2.remap(to_uint8(img),map_x,map_y,cv2.INTER_LINEAR)
    return d.astype(np.float32)

def highlight_shadows(img, hl=0, sh=0):
    lum=cv2.cvtColor(to_uint8(img),cv2.COLOR_BGR2GRAY).astype(np.float32)/255
    hl_m=lum[...,np.newaxis]; sh_m=(1-lum)[...,np.newaxis]
    return np.clip(img+hl_m*hl+sh_m*sh,0,255)

def add_color_cast_channel(img, b_add=0, g_add=0, r_add=0):
    out=img.copy()
    out[:,:,0]=np.clip(out[:,:,0]+b_add,0,255)
    out[:,:,1]=np.clip(out[:,:,1]+g_add,0,255)
    out[:,:,2]=np.clip(out[:,:,2]+r_add,0,255)
    return out

def polaroid_border(img):
    """Add white polaroid border"""
    h,w=img.shape[:2]
    border_side=int(w*0.06); border_top=int(h*0.06); border_bottom=int(h*0.14)
    new_h=h+border_top+border_bottom; new_w=w+border_side*2
    canvas=np.ones((new_h,new_w,3),np.float32)*245
    canvas[border_top:border_top+h, border_side:border_side+w]=img
    canvas=cv2.GaussianBlur(to_uint8(canvas),(3,3),0).astype(np.float32)
    return canvas

def half_frame_border(img):
    """Half frame camera border - black bars left/right"""
    h,w=img.shape[:2]; out=img.copy()
    bw=int(w*0.04)
    out[:,:bw]=0; out[:,w-bw:]=0
    return out

def slide_film_border(img):
    """Slide film mount border"""
    h,w=img.shape[:2]; out=img.copy()
    bw=int(w*0.05); bh=int(h*0.05)
    out[:bh,:]=0; out[h-bh:,:]=0; out[:,:bw]=0; out[:,w-bw:]=0
    return out

