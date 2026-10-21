"""Run: python tests/check_static.py (Pillow required for image validation)."""
import re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.links = path, [], []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('src', 'href'):
            if attrs.get(key):
                self.links.append(attrs[key])

pages = {}
for path in ROOT.glob('*.html'):
    page = Page(path)
    page.feed(path.read_text())
    assert len(page.ids) == len(set(page.ids)), f'Duplicate IDs: {path}'
    pages[path] = page
for path, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        assert target.is_file(), (path.name, link)
        if url.fragment and target in pages:
            assert unquote(url.fragment) in pages[target].ids, (path.name, link)
for path in [*ROOT.glob('*.mjs'), ROOT / 'style.css']:
    text = path.read_text()
    for asset in re.findall(r'assets/[\w./-]+\.(?:jpg|png|webp)', text):
        assert (ROOT / asset).is_file(), (path.name, asset)
    for module in re.findall(r"from\s+['\"](\./[^'\"]+)", text):
        assert (path.parent / module).is_file(), (path.name, module)
images = list((ROOT / 'assets').rglob('*'))
images = [path for path in images if path.is_file()]
for path in images:
    with Image.open(path) as image:
        image.verify()
assert len(images) == 65, len(images)
assert (ROOT / '.nojekyll').is_file()
print(f'PASS: {len(pages)} HTML pages, local links/fragments/modules/assets, {len(images)} images, .nojekyll')
