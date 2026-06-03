"""
VintageLab Filter Registry - Dazz Cam accurate presets
Each camera has icon_emoji, description, and fn (BGR uint8 → BGR uint8)
"""
import numpy as np
import cv2
from .effects import *


def _p(img, steps):
    f = to_float(img)
    for fn in steps:
        f = fn(f)
    return to_uint8(f)


# ═══════════════════════════════════════════════════════════════════════════════
# VIDEO / RETRO CAMERAS (top row in Dazz)
# ═══════════════════════════════════════════════════════════════════════════════

def cam_v_funs(img):
    """V FunS - fun VHS color shift with rainbow aberration"""
    return _p(img, [
        lambda i: rgb_shift(i, 6, -6),
        lambda i: sat(i, 1.3),
        lambda i: contrast(i, 1.1),
        lambda i: add_color_cast_channel(i, b_add=-10, r_add=15),
        lambda i: vhs_noise(i, 0.1),
        lambda i: scanlines(i, 3, 0.08),
        lambda i: add_grain(i, 14, colored=True),
        lambda i: vignette(i, 0.35),
    ])

def cam_kino(img):
    """Kino - cinema inspired, cool tones, high contrast"""
    return _p(img, [
        lambda i: temp(i, -15),
        lambda i: contrast(i, 1.2),
        lambda i: crush_blacks(i, 20),
        lambda i: desat(i, 0.1),
        lambda i: add_color_cast_channel(i, b_add=10, g_add=5),
        lambda i: add_grain_lum(i, 10),
        lambda i: vignette_oval(i, 0.5),
        lambda i: highlight_shadows(i, hl=-10, sh=0),
    ])

def cam_slide_p(img):
    """Slide P - slide film, warm, saturated, film borders"""
    return _p(img, [
        lambda i: temp(i, 12),
        lambda i: sat(i, 1.15),
        lambda i: contrast(i, 1.1),
        lambda i: halation(i, 0.2, (20,60,255)),
        lambda i: add_grain_lum(i, 12),
        lambda i: vignette(i, 0.3),
        lambda i: slide_film_border(i),
    ])

def cam_glow(img):
    """Glow - dreamy purple/lavender glow"""
    return _p(img, [
        lambda i: glow(i, 0.4, 35),
        lambda i: temp(i, -5),
        lambda i: add_color_cast_channel(i, b_add=12, r_add=8),
        lambda i: desat(i, 0.12),
        lambda i: fade(i, 18, 238),
        lambda i: add_grain_lum(i, 8),
        lambda i: vignette(i, 0.25),
    ])

def cam_v_classic(img):
    """V Classic - classic VHS camcorder"""
    return _p(img, [
        lambda i: vhs_blur(i, 3),
        lambda i: desat(i, 0.1),
        lambda i: rgb_shift(i, 3, -3),
        lambda i: scanlines(i, 3, 0.1),
        lambda i: vhs_noise(i, 0.09),
        lambda i: add_grain(i, 14),
        lambda i: vignette(i, 0.3),
        lambda i: date_stamp(i, '09/15/95'),
    ])

def cam_16mm(img):
    """16mm - 16mm film, cinematic grain"""
    return _p(img, [
        lambda i: temp(i, -8),
        lambda i: contrast(i, 1.15),
        lambda i: fade(i, 15, 235),
        lambda i: add_grain_lum(i, 22),
        lambda i: halation(i, 0.15),
        lambda i: vignette_oval(i, 0.55),
        lambda i: border_film(i),
    ])

def cam_8mm(img):
    """8mm - super 8 film, warm, heavy grain, borders"""
    return _p(img, [
        lambda i: temp(i, 20),
        lambda i: contrast(i, 1.1),
        lambda i: fade(i, 25, 230),
        lambda i: add_grain(i, 28),
        lambda i: dust(i, 40),
        lambda i: scratches(i, 4),
        lambda i: vignette(i, 0.5),
        lambda i: border_film(i),
        lambda i: add_color_cast_channel(i, b_add=-15, r_add=20),
    ])

def cam_dcr(img):
    """DCR - Sony DCR camcorder, neutral, slight blue"""
    return _p(img, [
        lambda i: temp(i, -8),
        lambda i: desat(i, 0.05),
        lambda i: contrast(i, 1.05),
        lambda i: scanlines(i, 4, 0.06),
        lambda i: add_grain(i, 10),
        lambda i: vignette(i, 0.25),
        lambda i: date_stamp(i, '03/22/01'),
    ])

def cam_vhs(img):
    """VHS - heavy VHS tape degradation"""
    return _p(img, [
        lambda i: vhs_blur(i, 5),
        lambda i: desat(i, 0.2),
        lambda i: rgb_shift(i, 7, -5),
        lambda i: scanlines(i, 2, 0.18),
        lambda i: vhs_noise(i, 0.2),
        lambda i: vhs_tracking(i, 12),
        lambda i: add_grain(i, 24),
        lambda i: vignette(i, 0.4),
        lambda i: interlace(i),
    ])

# ═══════════════════════════════════════════════════════════════════════════════
# FILM CAMERAS (second row in Dazz)
# ═══════════════════════════════════════════════════════════════════════════════

def cam_ofm(img):
    """OFM R - Olympus film, clean, slight green tint"""
    return _p(img, [
        lambda i: temp(i, -5),
        lambda i: tint_green(i, 8),
        lambda i: contrast(i, 1.08),
        lambda i: fade(i, 12, 240),
        lambda i: add_grain_lum(i, 11),
        lambda i: vignette(i, 0.28),
    ])

def cam_classic_u(img):
    """Classic U - classic 35mm, balanced, warm"""
    return _p(img, [
        lambda i: temp(i, 12),
        lambda i: contrast(i, 1.1),
        lambda i: split_tone(i, shadow=(8,5,0), highlight=(255,248,220), strength=0.06),
        lambda i: add_grain_lum(i, 14),
        lambda i: halation(i, 0.15),
        lambda i: vignette(i, 0.32),
    ])

def cam_cpm35(img):
    """CPM35 - classic point & shoot, neutral"""
    return _p(img, [
        lambda i: temp(i, 5),
        lambda i: contrast(i, 1.05),
        lambda i: fade(i, 15, 238),
        lambda i: add_grain_lum(i, 13),
        lambda i: vignette(i, 0.3),
    ])

def cam_original(img):
    """Original - no filter applied"""
    return img

def cam_dqs(img):
    """DQS - disposable, saturated, warm flash"""
    return _p(img, [
        lambda i: temp(i, 18),
        lambda i: sat(i, 1.15),
        lambda i: overexpose(i, 35),
        lambda i: add_grain_lum(i, 20),
        lambda i: lens_blur(i, 1),
        lambda i: vignette(i, 0.4),
    ])

def cam_fqs_r(img):
    """FQS R - Fuji disposable, green tint"""
    return _p(img, [
        lambda i: temp(i, -6),
        lambda i: tint_green(i, 12),
        lambda i: sat(i, 1.1),
        lambda i: contrast(i, 1.08),
        lambda i: add_grain_lum(i, 17),
        lambda i: vignette(i, 0.32),
    ])

def cam_d_classic(img):
    """D Classic - dark classic, muted tones"""
    return _p(img, [
        lambda i: desat(i, 0.15),
        lambda i: contrast(i, 1.15),
        lambda i: crush_blacks(i, 18),
        lambda i: temp(i, 5),
        lambda i: add_grain_lum(i, 14),
        lambda i: vignette_oval(i, 0.45),
    ])

def cam_fxn_r(img):
    """FXN R - vivid rangefinder, red pop"""
    return _p(img, [
        lambda i: temp(i, 15),
        lambda i: sat(i, 1.2),
        lambda i: contrast(i, 1.12),
        lambda i: halation(i, 0.22, (20,40,255)),
        lambda i: add_grain_lum(i, 12),
        lambda i: vignette(i, 0.35),
    ])

# ═══════════════════════════════════════════════════════════════════════════════
# INSTANT / SPECIAL CAMERAS
# ═══════════════════════════════════════════════════════════════════════════════

def cam_inst_c(img):
    """Inst C - Instax / Instant camera, white border"""
    return _p(img, [
        lambda i: temp(i, 8),
        lambda i: fade(i, 25, 232),
        lambda i: add_color_cast_channel(i, b_add=5, g_add=3),
        lambda i: glow(i, 0.1),
        lambda i: add_grain_lum(i, 10),
        lambda i: vignette(i, 0.3),
        lambda i: polaroid_border(i),
    ])

def cam_grd_r(img):
    """GRD R - Ricoh GR, street, cool blue"""
    return _p(img, [
        lambda i: temp(i, -12),
        lambda i: contrast(i, 1.15),
        lambda i: crush_blacks(i, 12),
        lambda i: desat(i, 0.08),
        lambda i: add_grain_lum(i, 9),
        lambda i: vignette(i, 0.35),
    ])

def cam_135sr(img):
    """135 SR - 35mm SLR, vibrant, sharp"""
    return _p(img, [
        lambda i: temp(i, 10),
        lambda i: sat(i, 1.18),
        lambda i: contrast(i, 1.12),
        lambda i: halation(i, 0.18),
        lambda i: add_grain_lum(i, 11),
        lambda i: vignette(i, 0.28),
    ])

def cam_kv80_r(img):
    """KV80 R - KV80 toy camera, lo-fi"""
    return _p(img, [
        lambda i: lens_blur(i, 2),
        lambda i: temp(i, 15),
        lambda i: sat(i, 0.9),
        lambda i: add_grain(i, 24, colored=True),
        lambda i: vignette(i, 0.55),
        lambda i: fade(i, 18, 230),
    ])

def cam_paf_r(img):
    """PAF R - compact auto, warm, soft"""
    return _p(img, [
        lambda i: temp(i, 18),
        lambda i: glow(i, 0.12),
        lambda i: fade(i, 20, 235),
        lambda i: add_grain_lum(i, 16),
        lambda i: vignette(i, 0.38),
    ])

def cam_collage(img):
    """Collage - multi-exposure, double exposure look"""
    return _p(img, [
        lambda i: sat(i, 1.2),
        lambda i: contrast(i, 1.1),
        lambda i: add_color_cast_channel(i, b_add=8, r_add=5),
        lambda i: add_grain_lum(i, 12),
        lambda i: vignette(i, 0.3),
    ])

def cam_ccd_r(img):
    """CCD R - CCD sensor, vintage digital, blue shadows"""
    return _p(img, [
        lambda i: temp(i, -10),
        lambda i: add_color_cast_channel(i, b_add=15, g_add=5),
        lambda i: sat(i, 1.1),
        lambda i: contrast(i, 1.08),
        lambda i: add_grain(i, 8),
        lambda i: vignette(i, 0.25),
        lambda i: date_stamp(i, '06/12/05', color=(255,255,255)),
    ])

def cam_hoga(img):
    """HOGA - toy camera, heavy vignette, warm"""
    return _p(img, [
        lambda i: temp(i, 22),
        lambda i: sat(i, 1.1),
        lambda i: lens_blur(i, 2),
        lambda i: add_grain(i, 22, colored=True),
        lambda i: vignette(i, 0.65),
        lambda i: fade(i, 15, 235),
    ])

def cam_golf(img):
    """Golf - vivid point & shoot, high sat"""
    return _p(img, [
        lambda i: sat(i, 1.3),
        lambda i: contrast(i, 1.15),
        lambda i: temp(i, 8),
        lambda i: halation(i, 0.1),
        lambda i: add_grain_lum(i, 10),
        lambda i: vignette(i, 0.25),
    ])

def cam_gr_f(img):
    """GR F - Ricoh film look, neutral-cool"""
    return _p(img, [
        lambda i: temp(i, -8),
        lambda i: contrast(i, 1.12),
        lambda i: fade(i, 12, 238),
        lambda i: add_grain_lum(i, 12),
        lambda i: vignette_oval(i, 0.4),
    ])

def cam_ir(img):
    """IR - Infrared look"""
    return _p(img, [
        lambda i: desat(i, 0.6),
        lambda i: add_color_cast_channel(i, b_add=-20, g_add=10, r_add=30),
        lambda i: contrast(i, 1.2),
        lambda i: add_grain_lum(i, 18),
        lambda i: glow(i, 0.15),
        lambda i: vignette(i, 0.4),
    ])

def cam_d_half(img):
    """D Half - half frame camera borders"""
    return _p(img, [
        lambda i: temp(i, 5),
        lambda i: contrast(i, 1.08),
        lambda i: fade(i, 18, 236),
        lambda i: add_grain_lum(i, 15),
        lambda i: vignette(i, 0.35),
        lambda i: half_frame_border(i),
    ])

def cam_inst_sqc(img):
    """Inst SQC - square instant, warm Instax"""
    return _p(img, [
        lambda i: temp(i, 12),
        lambda i: fade(i, 20, 235),
        lambda i: glow(i, 0.08),
        lambda i: add_grain_lum(i, 9),
        lambda i: vignette(i, 0.28),
        lambda i: polaroid_border(i),
    ])

def cam_d_slide(img):
    """D Slide - slide film mount"""
    return _p(img, [
        lambda i: temp(i, 15),
        lambda i: sat(i, 1.12),
        lambda i: contrast(i, 1.1),
        lambda i: halation(i, 0.18),
        lambda i: add_grain_lum(i, 12),
        lambda i: vignette(i, 0.3),
        lambda i: slide_film_border(i),
    ])

def cam_ct2f(img):
    """CT2F - compact film, neutral warm"""
    return _p(img, [
        lambda i: temp(i, 10),
        lambda i: contrast(i, 1.06),
        lambda i: fade(i, 14, 238),
        lambda i: add_grain_lum(i, 13),
        lambda i: vignette(i, 0.3),
    ])

def cam_s_classic(img):
    """S Classic - square classic, medium format"""
    return _p(img, [
        lambda i: temp(i, 5),
        lambda i: contrast(i, 1.08),
        lambda i: desat(i, 0.05),
        lambda i: fade(i, 12, 240),
        lambda i: add_grain_lum(i, 10),
        lambda i: vignette(i, 0.28),
    ])

def cam_135ne(img):
    """135 NE - film strip display"""
    return _p(img, [
        lambda i: temp(i, 8),
        lambda i: sat(i, 1.1),
        lambda i: contrast(i, 1.08),
        lambda i: add_grain_lum(i, 14),
        lambda i: border_film(i),
        lambda i: vignette(i, 0.3),
    ])

def cam_s67(img):
    """S 67 - medium format 6x7, sharp, crisp"""
    return _p(img, [
        lambda i: temp(i, -3),
        lambda i: contrast(i, 1.1),
        lambda i: desat(i, 0.08),
        lambda i: add_grain_lum(i, 8),
        lambda i: vignette_oval(i, 0.35),
    ])

def cam_d3d(img):
    """D3D - 3D stereo look, cyan-red fringing"""
    return _p(img, [
        lambda i: rgb_shift(i, 5, -5),
        lambda i: add_color_cast_channel(i, b_add=-8, r_add=8),
        lambda i: add_grain(i, 12),
        lambda i: vignette(i, 0.3),
    ])

def cam_d_funs(img):
    """D FunS - fun disposable, colorful"""
    return _p(img, [
        lambda i: temp(i, 20),
        lambda i: sat(i, 1.25),
        lambda i: overexpose(i, 30),
        lambda i: add_grain_lum(i, 20),
        lambda i: vignette(i, 0.38),
        lambda i: lens_blur(i, 1),
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

FILTER_REGISTRY = {
    # ── Video / Retro ──────────────────────────────────────────────────────────
    'v_funs':      {'fn': cam_v_funs,    'name': 'V FunS',    'category': 'Video',      'emoji': '🎬', 'desc': 'Fun VHS with rainbow color shift'},
    'kino':        {'fn': cam_kino,      'name': 'Kino',      'category': 'Video',      'emoji': '🎞', 'desc': 'Cinema cool tones, high contrast'},
    'slide_p':     {'fn': cam_slide_p,   'name': 'Slide P',   'category': 'Video',      'emoji': '📽', 'desc': 'Warm slide film with borders'},
    'glow_cam':    {'fn': cam_glow,      'name': 'Glow',      'category': 'Video',      'emoji': '✨', 'desc': 'Dreamy purple glow'},
    'v_classic':   {'fn': cam_v_classic, 'name': 'V Classic', 'category': 'Video',      'emoji': '📼', 'desc': 'Classic VHS camcorder'},
    '16mm':        {'fn': cam_16mm,      'name': '16mm',      'category': 'Video',      'emoji': '🎥', 'desc': '16mm cinematic film grain'},
    '8mm':         {'fn': cam_8mm,       'name': '8mm',       'category': 'Video',      'emoji': '🎦', 'desc': 'Super 8 warm with heavy grain'},
    'dcr':         {'fn': cam_dcr,       'name': 'DCR',       'category': 'Video',      'emoji': '📹', 'desc': 'Sony DCR digital camcorder'},
    'vhs':         {'fn': cam_vhs,       'name': 'VHS',       'category': 'Video',      'emoji': '📼', 'desc': 'Heavy VHS tape degradation'},
    # ── Film Cameras ───────────────────────────────────────────────────────────
    'original':    {'fn': cam_original,  'name': 'Original',  'category': 'Film',       'emoji': '📷', 'desc': 'No filter'},
    'ofm_r':       {'fn': cam_ofm,       'name': 'OFM R',     'category': 'Film',       'emoji': '📸', 'desc': 'Olympus film, cool green'},
    'classic_u':   {'fn': cam_classic_u, 'name': 'Classic U', 'category': 'Film',       'emoji': '🎞', 'desc': 'Classic 35mm warm balanced'},
    'cpm35':       {'fn': cam_cpm35,     'name': 'CPM35',     'category': 'Film',       'emoji': '📷', 'desc': 'Classic point & shoot'},
    'dqs':         {'fn': cam_dqs,       'name': 'DQS',       'category': 'Film',       'emoji': '📷', 'desc': 'Disposable saturated warm'},
    'fqs_r':       {'fn': cam_fqs_r,     'name': 'FQS R',     'category': 'Film',       'emoji': '🟢', 'desc': 'Fuji disposable green tint'},
    'd_classic':   {'fn': cam_d_classic, 'name': 'D Classic', 'category': 'Film',       'emoji': '⬛', 'desc': 'Dark classic muted tones'},
    'fxn_r':       {'fn': cam_fxn_r,     'name': 'FXN R',     'category': 'Film',       'emoji': '🔴', 'desc': 'Vivid rangefinder red pop'},
    's_classic':   {'fn': cam_s_classic, 'name': 'S Classic', 'category': 'Film',       'emoji': '⬜', 'desc': 'Square medium format'},
    '135ne':       {'fn': cam_135ne,     'name': '135 NE',    'category': 'Film',       'emoji': '🎞', 'desc': 'Film strip display'},
    's67':         {'fn': cam_s67,       'name': 'S 67',      'category': 'Film',       'emoji': '⬛', 'desc': 'Medium format 6x7 crisp'},
    'd3d':         {'fn': cam_d3d,       'name': 'D3D',       'category': 'Film',       'emoji': '🔵', 'desc': '3D stereo cyan-red fringe'},
    # ── Instant / Special ──────────────────────────────────────────────────────
    'inst_c':      {'fn': cam_inst_c,    'name': 'Inst C',    'category': 'Instant',    'emoji': '⬜', 'desc': 'Instax instant camera'},
    'grd_r':       {'fn': cam_grd_r,     'name': 'GRD R',     'category': 'Instant',    'emoji': '🔵', 'desc': 'Ricoh GR street cool'},
    '135sr':       {'fn': cam_135sr,     'name': '135 SR',    'category': 'Instant',    'emoji': '📷', 'desc': '35mm SLR vibrant sharp'},
    'kv80_r':      {'fn': cam_kv80_r,    'name': 'KV80 R',    'category': 'Instant',    'emoji': '🟡', 'desc': 'KV80 toy camera lo-fi'},
    'paf_r':       {'fn': cam_paf_r,     'name': 'PAF R',     'category': 'Instant',    'emoji': '🟠', 'desc': 'Compact auto warm soft'},
    'collage':     {'fn': cam_collage,   'name': 'Collage',   'category': 'Instant',    'emoji': '🎨', 'desc': 'Multi-exposure vivid'},
    'ccd_r':       {'fn': cam_ccd_r,     'name': 'CCD R',     'category': 'Instant',    'emoji': '🔴', 'desc': 'CCD sensor vintage digital'},
    'hoga':        {'fn': cam_hoga,      'name': 'HOGA',      'category': 'Instant',    'emoji': '🔴', 'desc': 'Toy camera heavy vignette'},
    'golf':        {'fn': cam_golf,      'name': 'Golf',      'category': 'Instant',    'emoji': '🟢', 'desc': 'Vivid point & shoot'},
    'gr_f':        {'fn': cam_gr_f,      'name': 'GR F',      'category': 'Instant',    'emoji': '⬛', 'desc': 'Ricoh film neutral cool'},
    'ir':          {'fn': cam_ir,        'name': 'IR',        'category': 'Instant',    'emoji': '🔴', 'desc': 'Infrared look'},
    'd_half':      {'fn': cam_d_half,    'name': 'D Half',    'category': 'Instant',    'emoji': '⬜', 'desc': 'Half frame camera'},
    'inst_sqc':    {'fn': cam_inst_sqc,  'name': 'Inst SQC',  'category': 'Instant',    'emoji': '⬜', 'desc': 'Square instant warm'},
    'd_slide':     {'fn': cam_d_slide,   'name': 'D Slide',   'category': 'Instant',    'emoji': '🟫', 'desc': 'Slide film mount'},
    'ct2f':        {'fn': cam_ct2f,      'name': 'CT2F',      'category': 'Instant',    'emoji': '🟫', 'desc': 'Compact film neutral warm'},
    'd_funs':      {'fn': cam_d_funs,    'name': 'D FunS',    'category': 'Instant',    'emoji': '🟡', 'desc': 'Fun disposable colorful'},
}

