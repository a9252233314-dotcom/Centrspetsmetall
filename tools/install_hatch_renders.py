from pathlib import Path
import json,hashlib
from PIL import Image
root=Path(__file__).resolve().parents[1];folder=root.parent/'csm-hatch-renders';manifest={}
for b in json.loads((root/'hatches.json').read_text(encoding='utf-8')):
    info=json.loads((folder/f"{b['id']}-render.json").read_text(encoding='utf-8'));sha=hashlib.sha256((root/f"assets/hatches/{b['id']}-geometry.json").read_bytes()).hexdigest();assert sha==info['geometry_sha256'],b['id']
    for suffix in ['render','underside-render']:
        with Image.open(folder/f"{b['id']}-{suffix}.png") as im:im.convert('RGB').save(root/f"assets/hatches/{b['id']}-{suffix}.webp",quality=94)
    manifest[b['id']]=info
(root/'assets/hatches/render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print('Installed',len(manifest),'geometry-matched hatch renders')
