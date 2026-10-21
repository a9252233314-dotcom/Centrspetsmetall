from pathlib import Path
import json,hashlib
from PIL import Image
root=Path(__file__).resolve().parents[1];folder=root.parent/'csm-lamp-renders';manifest={}
for b in json.loads((root/'lamps.json').read_text(encoding='utf-8')):
    info=json.loads((folder/f"{b['id']}-render.json").read_text(encoding='utf-8'));sha=hashlib.sha256((root/f"assets/lamps/{b['id']}-geometry.json").read_bytes()).hexdigest();assert sha==info['geometry_sha256'],b['id']
    for suffix in ['render','head-render']:
        with Image.open(folder/f"{b['id']}-{suffix}.png") as im:im.convert('RGB').save(root/f"assets/lamps/{b['id']}-{suffix}.webp",quality=94)
    manifest[b['id']]=info
(root/'assets/lamps/render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print('Installed',len(manifest),'geometry-matched lamp renders')
