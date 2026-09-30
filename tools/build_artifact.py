"""Strip index.html down to the body fragment the claude.ai Artifact publisher expects
(it adds its own doctype/head skeleton). Usage: python3 tools/build_artifact.py OUT.html"""
import sys, re, os
src = open(os.path.join(os.path.dirname(__file__), '..', 'index.html')).read()
frag = src.split('<!--ARTIFACT-START-->', 1)[1].split('<!--ARTIFACT-END-->', 1)[0]
frag = re.sub(r'</head>\s*<body>', '', frag, count=1)
open(sys.argv[1], 'w').write(frag.strip() + '\n')
