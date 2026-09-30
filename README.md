# Nerve Block Trainer

Interactive study games for the DEN-626A lecture *Applied Anatomy for Local Anesthesia*.
Open `index.html` in a browser (serve the folder, e.g. `python3 -m http.server`, so the images in `assets/` load).

## Games

- **Numb Map**: paint the teeth (pulp), buccal/labial and palatal/lingual gingiva, and skin/tongue areas each block anesthetizes, on maxillary and mandibular occlusal charts (Universal numbering). Reverse mode shows a numb zone and asks for the block.
- **Specimen Lab**: the lecture's dissections, skull plates and intraoral photos with the labels removed. Tap the pin for a named structure, name a highlighted pin, or tap the injection site on a real photo (nasopalatine, IANB, MSA/PSA/ASA reference teeth).
- **Name the Block**: identify PSA, MSA, ASA, supraperiosteal, long buccal and IANB from technique photos and models, plus infiltration vs field block vs nerve block.
- **Technique Drill**: height, angle, depth, aspiration, pulps and soft tissue for every block, plus anatomy, vessel, bone-density and variation questions.
- **Branch Sort**: sort V3 branches by division, V2 branches by segment, skull exits, palpable landmarks, maxillary artery parts, and infiltrate-vs-block.
- **Rapid Fire**: 60 seconds of mixed questions.
- **Atlas**: review card for every block with its numb zone, and the variations table.

Scores and best rounds are stored in the browser (`localStorage`).

## Rebuilding the images

`tools/extract_images.py` crops the figures from the lecture PDF, paints out labels and captions, and writes `assets/*.jpg`:

```
pip install pymupdf pillow opencv-python-headless numpy
python3 tools/extract_images.py Local_Anesthesia_Applied_Anatomy.pdf
```

The images come from the lecture slides, which credit Malamed, Fehrenbach & Herring, Netter and the cited studies. Because this repository is public, `assets/` is git-ignored: run the script above on your own copy of the lecture PDF to generate it locally.
