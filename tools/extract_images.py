"""Crop, mask and export the quiz images from the lecture PDF.

Usage: python3 tools/extract_images.py path/to/Local_Anesthesia_Applied_Anatomy.pdf

Needs: pymupdf, pillow, opencv-python-headless, numpy.
Label text that would give away an answer is painted out (flat fill on
white-background plates, inpainting on photos). Writes JPEGs to assets/.
"""
import sys, os
import numpy as np
import cv2
import pymupdf
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(OUT, exist_ok=True)
doc = pymupdf.open(sys.argv[1])


def region(page, idx=0, dpi=200):
    """Render the idx-th picture on a page (ignoring full-slide backgrounds)."""
    p = doc[page - 1]
    rects = [pymupdf.Rect(i['bbox']) & p.rect for i in p.get_image_info()]
    rects = [r for r in rects if r.width < 900]
    pix = p.get_pixmap(clip=rects[idx], dpi=dpi)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def white_out(im, boxes, scale=1.0, pad=4, fill=(255, 255, 255)):
    d = ImageDraw.Draw(im)
    for x0, y0, x1, y1 in boxes:
        d.rectangle([x0 * scale - pad, y0 * scale - pad, x1 * scale + pad, y1 * scale + pad], fill=fill)
    return im


def inpaint(im, boxes=(), lines=(), circles=(), scale=1.0, pad=5):
    arr = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    mask = np.zeros(arr.shape[:2], np.uint8)
    for x0, y0, x1, y1 in boxes:
        cv2.rectangle(mask, (int(x0 * scale - pad), int(y0 * scale - pad)),
                      (int(x1 * scale + pad), int(y1 * scale + pad)), 255, -1)
    for (x0, y0, x1, y1, w) in lines:
        cv2.line(mask, (int(x0 * scale), int(y0 * scale)), (int(x1 * scale), int(y1 * scale)), 255, int(w))
    for (x, y, r) in circles:
        cv2.circle(mask, (int(x * scale), int(y * scale)), int(r), 255, -1)
    out = cv2.inpaint(arr, mask, 9, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))


def trim_white(im, thresh=245):
    a = np.array(im.convert('L'))
    rows = np.where((a < thresh).sum(1) > a.shape[1] * 0.02)[0]
    cols = np.where((a < thresh).sum(0) > a.shape[0] * 0.02)[0]
    return im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))


def save(im, name, maxw=1100, q=80):
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    im.save(os.path.join(OUT, name + '.jpg'), quality=q, optimize=True, progressive=True)
    print(name, im.size)


# --- Specimen plates (labels removed, leader lines kept as pointers) ---
im = region(11).crop((0, 0, 1060, 1500))
save(im, 'plate_maxillary_nerve')

im = region(14)
white_out(im, [(300, 75, 605, 112), (40, 215, 392, 292), (35, 428, 402, 466), (10, 505, 400, 542),
               (180, 603, 392, 642), (1600, 120, 1910, 200), (1610, 290, 1965, 335),
               (1432, 705, 1710, 745), (180, 1150, 215, 1190)], scale=2197 / 2000)
save(im, 'plate_v3_fossa', maxw=1200)

im = region(34, 1)
white_out(im, [(418, 25, 657, 58), (210, 85, 455, 115), (95, 165, 385, 200), (38, 245, 262, 280),
               (793, 250, 1100, 285), (30, 440, 158, 527), (38, 560, 150, 640), (38, 672, 225, 775),
               (1015, 605, 1105, 640), (495, 825, 570, 860)])
save(im, 'plate_mandible')

im = region(19)
white_out(im, [(240, 105, 422, 137), (88, 280, 345, 350), (50, 610, 312, 682), (610, 780, 985, 850),
               (1030, 5, 1232, 42), (1145, 50, 1342, 87), (1200, 110, 1302, 147), (1220, 172, 1397, 207),
               (1220, 268, 1410, 304), (1248, 350, 1380, 387), (1245, 468, 1392, 504),
               (1272, 575, 1414, 612), (1330, 780, 1500, 900)])
save(im, 'plate_hard_palate')

im = region(15)
white_out(im, [(0, 250, 245, 310), (878, 228, 1030, 290), (878, 368, 1117, 462), (0, 622, 168, 687),
               (878, 708, 1064, 744), (878, 795, 1074, 832), (282, 852, 502, 917), (918, 955, 1097, 1024),
               (918, 1183, 1037, 1277), (918, 1305, 1027, 1372)])
save(im, 'plate_nerve_lateral')

im = region(24).crop((236, 175, 1450, 950))
save(im, 'photo_vestibule')

im = region(23, 1)
save(im, 'photo_palate')

im = region(37, 0)
im = inpaint(im, boxes=[(300, 588, 450, 628)],
             lines=[(440, 492, 830, 376, 26), (460, 492, 460, 760, 14), (352, 1032, 465, 752, 13)],
             circles=[(458, 486, 52), (460, 752, 18)])
save(im.crop((0, 0, 805, im.height)), 'photo_ianb_site')
save(region(37, 0), 'photo_ianb_technique')

# --- Technique images for "Name that block" ---
s = 2150 / 2000
im = region(30)
im = white_out(im, [], s)
left = inpaint(im.crop((0, 0, int(980 * s), im.height)),
               boxes=[(280, 30, 510, 100), (262, 462, 425, 498), (258, 525, 512, 562)], scale=s)
right = inpaint(im.crop((int(985 * s), 0, im.width, im.height)), boxes=[(0, 65, 330, 172)], scale=s)
save(left, 'tech_msa_model'); save(right, 'tech_msa_clinical')

s = 2124 / 2000
im = region(31)
left = inpaint(im.crop((0, 0, int(990 * s), im.height)),
               boxes=[(447, 152, 697, 222), (128, 457, 238, 527)], scale=s)
right = inpaint(im.crop((int(997 * s), 0, im.width, im.height)), boxes=[(13, 288, 385, 435)], scale=s)
save(left, 'tech_asa_model'); save(right, 'tech_asa_clinical')

im = region(29)
left = inpaint(im.crop((0, 0, 990, im.height)), boxes=[(75, 212, 345, 285), (122, 332, 335, 370)])
right = inpaint(im.crop((992, 0, im.width, im.height)), boxes=[(8, 265, 273, 375)])
save(left, 'tech_psa_model'); save(right, 'tech_psa_clinical')

im = region(28, 0).crop((0, 75, 926, 748))
save(inpaint(im, boxes=[(688, 170, 822, 270), (20, 625, 50, 655)]), 'tech_supraperiosteal_model')
im = region(28, 1).crop((0, 258, 920, 939))
save(inpaint(im, boxes=[(598, 280, 772, 344), (12, 625, 52, 668)]), 'tech_supraperiosteal_clinical')

im = region(38, 0).crop((0, 0, 1042, 740))
save(inpaint(im, boxes=[(22, 668, 62, 712)]), 'tech_long_buccal_skull')
im = trim_white(region(38, 1))
save(im.crop((70, 0, im.width, im.height - 70)), 'tech_long_buccal_clinical')

s = 2289 / 2000
im = region(39)
save(inpaint(im.crop((0, 0, int(1175 * s), im.height)), boxes=[(28, 715, 68, 765)], scale=s), 'tech_mand_infiltration_skull')
save(inpaint(im.crop((int(1195 * s), 0, im.width, im.height)), boxes=[(5, 715, 55, 765)], scale=s), 'tech_mand_infiltration_clinical')

for k, n in enumerate(['infiltration', 'field', 'nerveblock']):
    save(region(26, k), f'concept_{n}', maxw=800)
