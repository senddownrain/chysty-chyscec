"""Rebuild the approved CC0 derivatives; never processes unverified candidates."""
import hashlib,json
from pathlib import Path
from PIL import Image

root=Path(__file__).resolve().parents[1]
registry=json.loads((root/'docs/image-rights.json').read_text())
for row in registry['images']:
    if row['status']!='verified' or row['decision']!='accepted':continue
    assert row['web']['originalLicense']=='CC0-1.0', 'Review derivative license handling before adding other licenses'
    original=root/row['web']['original']
    assert hashlib.sha1(original.read_bytes()).hexdigest()==row['evidence']['commonsSHA1']
    with Image.open(original) as image:
        image=image.convert('RGB')
        for variant,box,quality in zip(row['web']['variants'],[(480,600),(640,800),(1200,1500)],[85,85,90],strict=True):
            derived=image.copy();derived.thumbnail(box,Image.Resampling.LANCZOS)
            path=root/variant['path'];path.parent.mkdir(parents=True,exist_ok=True)
            derived.save(path,quality=quality,method=6)
            assert hashlib.sha256(path.read_bytes()).hexdigest()==variant['sha256'], 'Encoder output changed; review and update registry hashes'
print('Rebuilt verified derivatives with no cropping or upscaling')
