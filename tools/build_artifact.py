"""Strip index.html down to the body fragment the claude.ai Artifact publisher expects
(it adds its own doctype/head skeleton). Usage: python3 tools/build_artifact.py OUT.html"""
import sys, re, os
src = open(os.path.join(os.path.dirname(__file__), '..', 'index.html')).read()
frag = src.split('<!--ARTIFACT-START-->', 1)[1].split('<!--ARTIFACT-END-->', 1)[0]
frag = re.sub(r'</head>\s*<body>', '', frag, count=1)
open(sys.argv[1], 'w').write(frag.strip() + '\n')
# the Artifact host does not serve .glb, so also emit the model as a base64 ES module next to the page
import base64
root = os.path.join(os.path.dirname(__file__), '..')
out_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), 'model')
os.makedirs(out_dir, exist_ok=True)
data = open(os.path.join(root, 'model', 'head.glb'), 'rb').read()
open(os.path.join(out_dir, 'head.glb.js'), 'w').write('export default "' + base64.b64encode(data).decode() + '";\n')
