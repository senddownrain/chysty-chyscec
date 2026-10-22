"""The registry is the gate for every saint image, including direct asset publication."""
import hashlib,json,re,subprocess
from pathlib import Path
from PIL import Image

root=Path(__file__).resolve().parents[1]
registry=json.loads((root/'docs/image-rights.json').read_text())
runtime=json.loads(subprocess.check_output(['node','--input-type=module','-e',"import {imageSizes} from './image-sizes.mjs';import data from './saints.mjs';console.log(JSON.stringify({imageSizes,saints:data.saints}));"],cwd=root))
rows=registry['images'];ids={r['id'] for r in rows}
assert len(rows)==len(ids)==35
assert ids==set(runtime['imageSizes'])=={s['id'] for s in runtime['saints']}
names={s['id']:s['displayName'] for s in runtime['saints']}
allowed=set()
for row in rows:
    assert row['name']==names[row['id']]
    assert row['status'] in ['verified','needs-review','rejected']
    image=runtime['imageSizes'][row['id']]
    if image:
        assert row['status']=='verified' and row['decision']=='accepted'
        assert row['attribution']['sourcePage'] and row['attribution']['licenseURL']
        assert row['evidence']['localSHA1']==row['evidence']['commonsSHA1']
        orig=root/row['web']['original'];allowed.add(orig.resolve())
        assert hashlib.sha1(orig.read_bytes()).hexdigest()==row['evidence']['commonsSHA1']
        with Image.open(orig) as original:
            for v in row['web']['variants']:
                p=root/v['path'];allowed.add(p.resolve())
                assert p.stat().st_size==v['bytes']
                assert hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256']
                with Image.open(p) as im:
                    assert im.size==(v['width'],v['height'])
                    assert im.width<=original.width and im.height<=original.height
                    assert abs(im.width/im.height-original.width/original.height)<.002
        assert all(not v.startswith(('http:','https:','data:')) for v in [image['src'],image['print']])
    else:
        assert row['status']!='verified' and row['web'] is None and row['blocker']
    assert f'id="{row["id"]}"' in (root/'sources.html').read_text()
    for candidate in row['candidates']:
        assert candidate['status']=='candidate' and candidate['decision']=='needs-review'
        assert candidate['verifiedLicense'] is None
for asset in registry['otherAssets']:
    allowed.add((root/asset['path']).resolve())
published={p.resolve() for p in (root/'assets').rglob('*') if p.is_file()}
assert published==allowed, published^allowed
before={p:(root/p).read_bytes() for p in ['image-sizes.mjs','sources.html']}
subprocess.run(['python','scripts/build-image-metadata.py'],cwd=root,check=True)
assert all((root/p).read_bytes()==data for p,data in before.items()),'Regenerate metadata and sources'
print('PASS: 35 exact IDs/names, verified originals/hashes/variants, no upscaling, safe fallbacks, candidate separation, credits and published asset allowlist, reproducible metadata')
