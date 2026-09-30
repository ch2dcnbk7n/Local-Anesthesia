"""Nerve courses for the 3D model. Usage: python3 tools/nerves.py model/nerves.json"""
import json, sys
# Right-side nerve courses in model millimetres (+X patient left, +Y up, +Z anterior); mirrored for the left in the app.
N = {}
def n(key, name, div, pts, r, info, twigs=None):
    N[key] = {'name': name, 'div': div, 'pts': pts, 'r': r, 'info': info, 'twigs': twigs or []}
AP = {  # tooth apices from model/meta.json (right side)
 2: [-18.6, 24.8, -14.0], 3: [-19.5, 23.2, -5.1], 4: [-20.4, 22.6, 2.8], 5: [-19.4, 23.9, 9.2], 6: [-14.1, 25.2, 12.9], 7: [-9.3, 21.5, 15.1], 8: [-3.7, 19.8, 16.3],
 25: [-2.4, -28.1, 6.6], 26: [-5.4, -27.8, 7.2], 27: [-11.7, -29.0, 4.9], 28: [-17.5, -24.3, 0.6], 29: [-21.0, -24.0, -4.4], 30: [-23.8, -17.7, -8.8], 31: [-28.1, -12.7, -20.3]}
GANG = [-19, 56, -50]
n('ganglion_v1', 'Ophthalmic nerve (V1)', 'V1', [[-17, 56, -46], [-17, 56, -36], [-17, 55, -24], [-16, 55, -13]], [1.5, 1.1],
  'Sensory. Leaves through the superior orbital fissure. Not blocked in dentistry, but solution reaching the orbit explains transient diplopia.')
n('v2', 'Maxillary nerve (V2)', 'V2', [[-18, 54, -46], [-19, 50, -36], [-19, 47, -30], [-21, 42, -25.5], [-24.5, 44, -18], [-25, 42.8, -8], [-25.8, 39.5, -1], [-25.9, 34.5, 3.8], [-26.2, 32.6, 5.2]], [1.6, 1.25],
  'Sensory. Foramen rotundum → pterygopalatine fossa → inferior orbital fissure → infraorbital groove and canal → infraorbital foramen. A V2 block catches it in the fossa.')
n('io_branches', 'Infraorbital terminal branches', 'V2', [[-26.2, 32.6, 5.2], [-27.5, 31.5, 8.5]], [0.9, 0.7],
  'Inferior palpebral, lateral nasal and superior labial branches: lower eyelid, side of the nose, upper lip.',
  twigs=[[[-27.5, 31.5, 8.5], [-30, 37, 10], [-31, 43, 10.5]], [[-27.5, 31.5, 8.5], [-22, 33, 12.5], [-15, 35, 14]], [[-27.5, 31.5, 8.5], [-24, 24, 14], [-19, 15, 20], [-13, 9, 25]]])
n('psa', 'Posterior superior alveolar nerve', 'V2', [[-21, 42, -25.5], [-24.5, 34, -23.5], [-26.5, 25, -22], [-25.5, 20.5, -20], [-22, 22.5, -16]], [0.7, 0.5],
  'Leaves V2 in the pterygopalatine fossa and runs down the tuberosity. Pulps of M3, M2 and M1 (MB root variable), buccal periodontium of the molars. PSA block.',
  twigs=[[[-22, 22.5, -16], AP[2]], [[-22, 22.5, -16], [-21.5, 23, -10], AP[3]], [[-26.5, 25, -22], [-29.5, 17, -18], [-31, 13, -12], [-30.5, 12, -5]]])
n('msa', 'Middle superior alveolar nerve', 'V2', [[-25.8, 39.5, -1], [-27.5, 32, 0], [-26, 26.5, 2.5], [-22.5, 24, 3]], [0.5, 0.4],
  'From the infraorbital canal (present in ~28–72%). PM1, PM2 and the MB root of M1, buccal periodontium of the premolars. MSA block.',
  twigs=[[[-22.5, 24, 3], AP[4]], [[-22.5, 24, 3], AP[5]], [[-26, 26.5, 2.5], [-22.5, 24.5, -2], [-21, 23.5, -4]]])
n('asa', 'Anterior superior alveolar nerve', 'V2', [[-25.9, 36.5, 2.5], [-23, 32.5, 8], [-18.5, 28.5, 11.5], [-14.1, 25.8, 12.9], [-9.3, 22.3, 15.1], [-3.7, 20.6, 16.3], [1.2, 20.2, 16.5]], [0.6, 0.4],
  'From the infraorbital canal, down the anterior sinus wall. Central and lateral incisors and canine; fibres cross the midline. ASA / infraorbital block.',
  twigs=[[[-14.1, 25.8, 12.9], AP[6]], [[-9.3, 22.3, 15.1], AP[7]], [[-3.7, 20.6, 16.3], AP[8]]])
n('gp', 'Greater palatine nerve', 'V2', [[-21, 42, -25.5], [-19.5, 33, -23], [-17, 23, -19.5], [-14.7, 16, -16.8], [-15.6, 13.6, -15], [-16.5, 13.3, -10], [-16.5, 11.0, -4], [-16.3, 10.0, 2], [-15.5, 7.8, 8], [-13.5, 6.5, 12]], [0.8, 0.5],
  'Down the palatine canal, out of the greater palatine foramen (usually opposite M3), forward near the alveolar–palatal junction. Palatal mucosa and gingiva from the molars to the canine region. GP block.')
n('lp', 'Lesser palatine nerve', 'V2', [[-17, 23, -19.5], [-15.5, 17, -21], [-15, 14, -21.8], [-12, 12.8, -28], [-8, 12, -34]], [0.5, 0.4],
  'Through the lesser palatine foramina, just behind the greater: soft palate.')
n('np', 'Nasopalatine nerve', 'V2', [[-21, 42, -25.5], [-16, 46, -24], [-6, 48.5, -21], [-2.7, 46, -17], [-2.7, 34, -4], [-2.2, 22, 8], [-1.2, 14, 13.4], [-0.6, 10.2, 15.3]], [0.6, 0.45],
  'Through the sphenopalatine foramen, down the nasal septum and the incisive canal to the incisive foramen. Anterior palate, canine to canine. NP block.',
  twigs=[[[-0.6, 10.2, 15.3], [-3.5, 7.0, 17.2], [-7, 5.6, 19]], [[-0.6, 10.2, 15.3], [-5.5, 9.4, 14], [-9.5, 9.8, 12]]])
n('v3', 'Mandibular nerve (V3)', 'V3', [[-21, 54, -50], [-24, 48, -47.5], [-26, 42, -46]], [2.2, 2.0],
  'Mixed: the only division with a motor root. Leaves through foramen ovale into the infratemporal fossa.')
n('ian', 'Inferior alveolar nerve', 'V3', [[-26, 42, -46], [-30, 32, -45], [-33.5, 20, -43.5], [-35.5, 13, -42], [-36.3, 10.5, -41], [-37, 3, -36], [-35.3, -8, -29], [-31, -17, -20], [-25.5, -21.5, -9], [-19.5, -25.5, -1.5], [-18.6, -24, 2.6]], [1.35, 1.0],
  'Posterior division of V3. Enters the mandibular foramen (guarded by the lingula) and runs in the canal below the apices. Pulps of all mandibular teeth on that side. IANB target.',
  twigs=[[[-31, -17, -20], AP[31]], [[-25.5, -21.5, -9], AP[30]], [[-21.5, -24.5, -4], AP[29]]])
n('mental', 'Mental nerve', 'V3', [[-18.6, -24, 2.6], [-21.3, -21.5, 4.6], [-23, -20, 7]], [0.9, 0.75],
  'Leaves the mental foramen below the premolar apices: lower lip, chin, buccal gingiva anterior to the foramen. Mental block.',
  twigs=[[[-23, -20, 7], [-21.5, -15, 13], [-16, -11.5, 21], [-8, -10, 26]], [[-23, -20, 7], [-22, -26, 11], [-15, -29.5, 18]]])
n('incisive', 'Incisive nerve', 'V3', [[-18.6, -24, 2.6], [-15.5, -27.3, 4.8], [-11.5, -30.7, 5.2], [-5.5, -30.2, 7.4], [-2.0, -30.0, 7.0], [1.5, -30.0, 7.0]], [0.65, 0.45],
  'Continues forward in bone to the canine and incisors. Incisive block.',
  twigs=[[[-17, -25.8, 3.5], AP[28]], [[-11.5, -30.7, 5.2], AP[27]], [[-5.5, -30.2, 7.4], AP[26]], [[-2.0, -30.0, 7.0], AP[25]]])
n('lingual', 'Lingual nerve', 'V3', [[-26, 42, -46], [-27, 32, -43], [-27.5, 20, -38], [-27, 6, -30], [-23, -3, -24], [-20, -8.5, -18], [-16.5, -12.5, -9], [-13, -14, -1], [-9, -11, 7]], [1.15, 0.8],
  'Posterior division of V3, joined by the chorda tympani. Runs anterior and medial to the IAN, then below the third molar lingually. Anterior ⅔ tongue, floor of mouth, lingual gingiva.')
n('buccal', 'Buccal (long buccal) nerve', 'V3', [[-26, 42, -46], [-30, 38, -40], [-34, 26, -30], [-38.5, 9, -21.5], [-37.8, 2, -17], [-35.6, -4.5, -11], [-34.2, -7.5, -3]], [0.75, 0.55],
  'The only sensory branch of the anterior division. Passes between the heads of lateral pterygoid and crosses the anterior ramus at about the occlusal level. Buccal gingiva of the molars. Long buccal block; the IANB misses it.')
n('mylohyoid', 'Nerve to mylohyoid', 'V3', [[-35.5, 13, -42], [-33.5, 2, -39], [-29, -10, -32], [-24, -20, -22], [-19, -26, -12]], [0.5, 0.4],
  'Leaves the IAN just before the mandibular foramen and runs in the mylohyoid groove. Motor to mylohyoid and anterior digastric.')
n('auriculotemporal', 'Auriculotemporal nerve', 'V3', [[-25, 45, -48], [-30, 44, -54], [-38, 43, -60], [-47, 46, -63], [-54, 60, -61]], [0.8, 0.6],
  'Posterior division; encircles the middle meningeal artery. TMJ, temple, parotid secretomotor fibres.')
n('masseteric', 'Masseteric nerve', 'V3', [[-24.5, 47, -47], [-32, 48, -45], [-40, 46, -44], [-47, 38, -44]], [0.7, 0.55],
  'Anterior division, motor to masseter (and the TMJ). Crosses the mandibular notch.')
n('deeptemporal', 'Deep temporal nerves', 'V3', [[-24.5, 47, -47], [-32, 51, -41], [-42, 58, -37], [-49, 70, -35]], [0.6, 0.45],
  'Anterior division, motor to temporalis.')
json.dump({'ganglion': GANG, 'nerves': N}, open(sys.argv[1], 'w'))
print(len(N), 'nerves')
