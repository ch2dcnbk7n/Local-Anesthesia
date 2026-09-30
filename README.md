# Nerve Block Trainer

Interactive 3D study games for the DEN-626A lecture *Applied Anatomy for Local Anesthesia*.
Serve the folder (for example `python3 -m http.server`) and open `index.html`. The page loads three.js from jsDelivr.

## Games

- **Nerve Finder (3D)**: a skull with teeth, gingiva and the V2/V3 branches in place. Explore by tapping, find a named nerve or landmark, or name a glowing nerve. Slide *Bone* down to see nerves inside their canals, and use *Jaw* to open the mouth.
- **Numb Map (3D)**: tap the teeth (pulp) and buccal or palatal/lingual gingiva each block anesthetizes, plus lip, eyelid, nose, chin and tongue chips. A reverse mode shows a numb zone and asks for the block.
- **Needle Lab (3D)**: tap the insertion point for a block, then watch the syringe advance, the anesthetic spread, the nerve light up and the teeth go numb. Also includes "name the block from the needle" and a demo mode for every block.
- **Technique Drill**, **Branch Sort**, **Rapid Fire** and **Atlas**: text and sorting drills on heights, angles, depths, pathways, vessels and variations.

Scores are stored in the browser (`localStorage`).

## 3D model

- `model/head.glb`: skull, 28 teeth and gingiva from [BodyParts3D](https://lifesciencedb.jp/bp3d/) (DBCLS, CC BY-SA 2.1 JP), built by `tools/build_model.py` from the STL files. See `model/LICENSE.txt`.
- `model/nerves.json`: nerve courses written by `tools/nerves.py`. They are drawn to match the anatomy for teaching and are approximate.

```
pip install trimesh fast-simplification embreex numpy scipy
python3 tools/build_model.py path/to/BodyParts3D_data/stl   # writes model/head_raw.glb and model/meta.json
npx gltfpack -i model/head_raw.glb -o model/head.glb -kn -km -vp 14 -vn 10
python3 tools/nerves.py model/nerves.json
```
