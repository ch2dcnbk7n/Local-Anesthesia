"""Build model/head.glb from BodyParts3D (CC BY-SA 2.1 JP, DBCLS) STL files.

Usage: python3 tools/build_model.py /path/to/BodyParts3D_data/stl

- decimates each part, converts to a Y-up frame in millimetres centred on the
  occlusal plane (+X = patient's left, +Y = up, +Z = anterior),
- bakes ambient occlusion (embree rays) and material tint into vertex colours,
- splits the upper/lower gingiva into buccal and palatal/lingual segments per
  tooth (Universal numbering) so they can be picked individually,
- writes model/head.glb and model/meta.json (pivot for jaw opening, tooth data).
Needs: trimesh, fast-simplification, embreex, numpy, scipy.
"""
import sys, os, json
import numpy as np
import trimesh
import fast_simplification

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), '..', 'model')
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

BONES = {  # key: (FMA id, target faces)
    'frontal': ('FMA52734', 14000), 'occipital': ('FMA52735', 7000), 'sphenoid': ('FMA52736', 14000),
    'temporal_r': ('FMA52738', 9000), 'temporal_l': ('FMA52739', 9000), 'ethmoid': ('FMA52740', 5000),
    'parietal_r': ('FMA52788', 7000), 'parietal_l': ('FMA52789', 7000),
    'zygomatic_r': ('FMA52892', 4600), 'zygomatic_l': ('FMA52893', 4600),
    'lacrimal_r': ('FMA53645', 1100), 'lacrimal_l': ('FMA53646', 1100),
    'nasal_r': ('FMA53647', 1100), 'nasal_l': ('FMA53648', 1100),
    'maxilla_r': ('FMA53649', 14000), 'maxilla_l': ('FMA53650', 14000),
    'palatine_r': ('FMA53655', 3600), 'palatine_l': ('FMA53656', 3600),
    'concha_r': ('FMA54737', 1600), 'concha_l': ('FMA54738', 1500), 'vomer': ('FMA9710', 2400),
    'mandible': ('FMA52748', 21000),
}
MUSCLES = {}
TEETH = {  # Universal number: FMA id (third molars are not in BodyParts3D)
    2: 'FMA55697', 3: 'FMA55698', 4: 'FMA55688', 5: 'FMA55689', 6: 'FMA55798', 7: 'FMA55680', 8: 'FMA55681',
    9: 'FMA55682', 10: 'FMA55683', 11: 'FMA55799', 12: 'FMA55690', 13: 'FMA55691', 14: 'FMA55699', 15: 'FMA55700',
    18: 'FMA55703', 19: 'FMA55704', 20: 'FMA55692', 21: 'FMA55693', 22: 'FMA55687', 23: 'FMA57141', 24: 'FMA57143',
    25: 'FMA57142', 26: 'FMA57140', 27: 'FMA55686', 28: 'FMA55694', 29: 'FMA55695', 30: 'FMA55705', 31: 'FMA55706',
}
GUMS = {'U': 'FMA59763', 'L': 'FMA59764'}
CROWN = {'CI': 10.5, 'LI': 9.5, 'C': 10.5, 'PM1': 8.2, 'PM2': 7.6, 'M1': 7.2, 'M2': 6.8}
TYPES = ['CI', 'LI', 'C', 'PM1', 'PM2', 'M1', 'M2', 'M3']
def ttype(n):
    q = (n - 1) // 8; i = (n - 1) % 8
    return TYPES[7 - i] if q in (0, 2) else TYPES[i]

def to_three(v):  # BodyParts3D (X left, -Y anterior, Z up) -> three (X left, Y up, Z anterior)
    return np.column_stack([v[:, 0], v[:, 2] - 1470.0, -(v[:, 1] + 160.0)])

def load(fma, target=None):
    m = trimesh.load(os.path.join(SRC, fma + '.stl'))
    m.merge_vertices()
    if target and len(m.faces) > target * 1.05:
        v, f = fast_simplification.simplify(m.vertices, m.faces, target_reduction=1 - target / len(m.faces))
        m = trimesh.Trimesh(v, f)
    m = trimesh.Trimesh(to_three(np.asarray(m.vertices)), np.asarray(m.faces), process=True)
    m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m)
    return m

parts = {}
for k, (fma, t) in BONES.items(): parts['bone_' + k] = load(fma, t)
for k, (fma, t) in MUSCLES.items(): parts['muscle_' + k] = load(fma, t)
for n, fma in TEETH.items(): parts[f'tooth_{n}'] = load(fma, 3200)
gum_src = {a: load(fma) for a, fma in GUMS.items()}

# --- gingiva segmentation (per tooth, buccal vs palatal/lingual)
tooth_info = {}
for n in TEETH:
    v = parts[f'tooth_{n}'].vertices
    upper = n <= 16
    occl = v[:, 1].min() if upper else v[:, 1].max()
    apex = v[:, 1].max() if upper else v[:, 1].min()
    crown_mask = (v[:, 1] < occl + 4) if upper else (v[:, 1] > occl - 4)
    c = v[crown_mask].mean(0)
    tooth_info[n] = {'center': c.tolist(), 'occl': float(occl), 'apex': float(apex), 'upper': upper,
                     'type': ttype(n), 'apexPoint': v[np.argmax(v[:, 1]) if upper else np.argmin(v[:, 1])].tolist()}
def arch_normals(nums):
    """outward (buccal) unit normal in the XZ plane for each tooth of one arch"""
    order = sorted(nums, key=lambda n: np.arctan2(tooth_info[n]['center'][0], tooth_info[n]['center'][2] + 20))
    pts = np.array([[tooth_info[n]['center'][0], tooth_info[n]['center'][2]] for n in order])
    centroid = np.array([0.0, pts[:, 1].mean() - 12])
    out = {}
    for i, n in enumerate(order):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        t = (b - a) / np.linalg.norm(b - a); nrm = np.array([-t[1], t[0]])
        if np.dot(nrm, pts[i] - centroid) < 0: nrm = -nrm
        out[n] = nrm
    return out
for arch, nums in (('U', [n for n in TEETH if n <= 16]), ('L', [n for n in TEETH if n > 16])):
    g = gum_src[arch]; nrm = arch_normals(nums)
    fc = g.triangles_center
    cs = np.array([[tooth_info[n]['center'][0], tooth_info[n]['center'][2]] for n in nums])
    d = np.linalg.norm(fc[:, None, [0, 2]] - cs[None], axis=2)
    near = np.array(nums)[d.argmin(1)]
    side = np.array(['b' if np.dot(fc[i, [0, 2]] - np.array(tooth_info[near[i]]['center'])[[0, 2]], nrm[near[i]]) > 0 else 'l' for i in range(len(fc))])
    for n in nums:
        for sd in 'bl':
            sel = np.where((near == n) & (side == sd))[0]
            if len(sel) == 0: continue
            sub = g.submesh([sel], append=True)
            parts[f'gum_{sd}{n}'] = sub

# --- ambient occlusion bake
def lower(k):  # parts that move with the jaw
    if k == 'bone_mandible': return True
    if k.startswith('tooth_') or k.startswith('gum_'): return int(''.join(ch for ch in k if ch.isdigit())) > 16
    return False
# bake the jaw and the cranium separately so opening the mouth does not leave baked shadows behind
inters = {g: trimesh.ray.ray_pyembree.RayMeshIntersector(trimesh.util.concatenate([m for k, m in parts.items() if not k.startswith('muscle') and lower(k) == g])) for g in (True, False)}
N = 28
def hemi(normals):
    u1 = rng.random((len(normals), N)); u2 = rng.random((len(normals), N))
    r = np.sqrt(u1); th = 2 * np.pi * u2
    x, y, z = r * np.cos(th), r * np.sin(th), np.sqrt(1 - u1)
    up = np.where(np.abs(normals[:, 2:3]) < .9, np.array([[0., 0, 1]]), np.array([[1., 0, 0]]))
    tx = np.cross(up, normals); tx /= np.linalg.norm(tx, axis=1, keepdims=True); ty = np.cross(normals, tx)
    return x[..., None] * tx[:, None] + y[..., None] * ty[:, None] + z[..., None] * normals[:, None]
def ao(m, inter, maxd=14.0):
    nv = np.nan_to_num(np.asarray(m.vertex_normals, dtype=float))
    bad = np.linalg.norm(nv, axis=1) < .5; nv[bad] = [0, 1, 0]
    o = m.vertices + nv * 0.08
    dirs = hemi(nv).reshape(-1, 3); orig = np.repeat(o, N, axis=0)
    loc, idx, _ = inter.intersects_location(orig, dirs, multiple_hits=False)
    hit = np.zeros(len(orig)); dist = np.linalg.norm(loc - orig[idx], axis=1)
    hit[idx[dist < maxd]] = 1 - dist[dist < maxd] / maxd * .5
    return 1 - hit.reshape(-1, N).mean(1)

def noise(p, s):
    return (np.sin(p[:, 0] * s + 1.3) * np.sin(p[:, 1] * s * 1.3 + .7) * np.sin(p[:, 2] * s * .9 + 2.1))
for k, m in parts.items():
    v = m.vertices
    a = ao(m, inters[lower(k)]) if not k.startswith('muscle') else np.ones(len(v))
    if k.startswith('bone'):
        base = np.array([.90, .86, .77]); stain = np.array([.62, .50, .36])
        var = .5 + .5 * noise(v, .21) * noise(v, .057)
        cav = np.clip(1 - a, 0, 1) ** 1.2
        col = base * (1 - .06 * var[:, None]) * (1 - cav[:, None] * .55) + stain * (cav[:, None] * .25)
        col *= (.55 + .45 * a[:, None] ** .8)
    elif k.startswith('tooth'):
        n = int(k.split('_')[1]); ti = tooth_info[n]; cl = CROWN[ti['type']] * (1 if ti['upper'] else .92)
        h = (v[:, 1] - ti['occl']) * (1 if ti['upper'] else -1)
        enamel, root = np.array([.95, .93, .87]), np.array([.87, .78, .58])
        t = np.clip((h - cl + .8) / 1.6, 0, 1)[:, None]
        col = enamel * (1 - t) + root * t
        edge = np.clip(1 - h / 2.2, 0, 1)[:, None] * (ti['type'] in ('CI', 'LI')); col = col * (1 - .10 * edge) + np.array([.78, .82, .88]) * .10 * edge
        col *= (.62 + .38 * a[:, None])
    elif k.startswith('gum'):
        col = np.array([.88, .52, .52]) * (.6 + .4 * a[:, None]) * (1 + .04 * noise(v, .5)[:, None])
    else:
        col = np.array([.70, .30, .28]) * (1 + .08 * noise(v, .9)[:, None])
    m.visual.vertex_colors = np.column_stack([np.clip(col, 0, 1) * 255, np.full(len(v), 255)]).astype(np.uint8)

# jaw pivot: axis through the tops of both condyles
mv = parts['bone_mandible'].vertices
cond = []
for s in (-1, 1):
    sel = mv[(np.sign(mv[:, 0]) == s) & (mv[:, 2] < -45)]
    cond.append(sel[np.argmax(sel[:, 1])])
cond = np.array(cond)

sc = trimesh.Scene()
for k, m in parts.items(): sc.add_geometry(m, node_name=k, geom_name=k)
sc.export(os.path.join(OUT, 'head_raw.glb'))
meta = {'condyles': cond.round(2).tolist(), 'teeth': {str(k): {kk: (np.round(vv, 2).tolist() if isinstance(vv, list) else vv) for kk, vv in v.items()} for k, v in tooth_info.items()},
        'faces': int(sum(len(m.faces) for m in parts.values())), 'parts': len(parts)}
json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'), indent=1)
print('parts', len(parts), 'faces', meta['faces'], 'condyles', cond.round(1).tolist())
