"""Install only studio images verified against the current geometry."""
from pathlib import Path
import json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
manifest={}
for b in json.loads((ROOT/'benches.json').read_text(encoding='utf-8')):
    source=ROOT.parent/'csm-bench-renders'/f"{b['id']}-render.png"
    info=json.loads(source.with_suffix('.json').read_text(encoding='utf-8'))
    geometry=ROOT/'assets/benches'/f"{b['id']}-geometry.json"
    assert info['geometry_sha256']==hashlib.sha256(geometry.read_bytes()).hexdigest(),(b['id'],'Stale render')
    with Image.open(source) as im:
        im.convert('RGB').save(ROOT/'assets/benches'/f"{b['id']}-render.webp",quality=94)
    manifest[b['id']]=info
(ROOT/'assets/benches/render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print('Installed',len(manifest),'geometry-matched Cycles renders')
