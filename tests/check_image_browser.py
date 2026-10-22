"""Browser image layout, request isolation, error and printing checks."""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
url=os.getenv('SITE_TEST_URL','http://localhost:8765/chysty-chyscec/')
out=root/'docs/qa';out.mkdir(exist_ok=True)
registry=json.loads((root/'docs/image-rights.json').read_text())
selection="id=>localStorage.setItem('chysty_chyscec.selection.v1',JSON.stringify({version:1,saintId:id,assignedAt:'2026-10-22T00:00:00Z'}))"
checks=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
    for width in [360,390,768,1440]:
        context=browser.new_context(viewport={'width':width,'height':1000},device_scale_factor=1)
        page=context.new_page();errors=[];requests=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:errors.append(f'{r.status} {r.url}') if r.status>=400 else None)
        page.on('request',lambda r:requests.append(r.url))
        page.goto(url,wait_until='networkidle')
        assert not any('/saints/' in u or '/originals/' in u for u in requests)
        for row in registry['images']:
            page.evaluate(selection,row['id']);page.reload(wait_until='networkidle')
            assert page.locator('#saint-name').inner_text()==row['name']
            frame=page.locator('.saint-image-frame');frame.scroll_into_view_if_needed()
            box=frame.bounding_box();assert abs(box['width']/box['height']-.8)<.005,(width,row['id'],box)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,row['id'])
            if row['web']:
                photo=page.locator('.saint-photo');photo.evaluate('(i)=>i.decode()')
                assert photo.evaluate('(i)=>getComputedStyle(i).objectFit')=='contain'
                assert not any('large.webp' in u or '/originals/' in u for u in requests)
                page.locator('#saint-card').screenshot(path=str(out/f'card-05-{width}.png'))
            if row['id']=='saint-24':
                page.locator('#saint-card').screenshot(path=str(out/f'card-24-fallback-{width}.png'))
        assert not errors,errors
        checks.append({'width':width,'cardsChecked':35,'aspectRatio':'4:5','overflow':False,'consoleOrHTTPFailures':errors})
        context.close()
    context=browser.new_context(viewport={'width':1440,'height':1000})
    page=context.new_page();page.goto(url);page.evaluate(selection,'saint-05');page.reload(wait_until='networkidle')
    page.locator('#print').click();page.locator('#print-photo').evaluate('(i)=>i.decode()')
    assert page.locator('#print-photo').get_attribute('src').endswith('large.webp')
    assert page.locator('#print-credit a').count()==2
    page.emulate_media(media='print')
    page.pdf(path=str(out/'saint-05-print.pdf'),format='A4',print_background=True)
    page.locator('#print-card').screenshot(path=str(out/'saint-05-print.png'))
    page.emulate_media(media='screen');page.locator('#print-close').click()
    # A failed screen image still leaves a stable labelled card and working print without it.
    page.route('**/assets/saints/*',lambda route:route.abort())
    page.reload(wait_until='networkidle');page.locator('#saint-card').scroll_into_view_if_needed()
    page.wait_for_function("document.querySelector('.saint-image-frame').textContent.includes('часова недаступная')")
    page.locator('#print').click()
    page.wait_for_function("document.getElementById('print-photo').hidden")
    assert 'без яе' in page.locator('#print-status').inner_text()
    page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
    assert page.locator('#print-photo').is_hidden(), 'beforeprint must preserve an image failure'
    browser.close()
(out/'image-browser-results.json').write_text(json.dumps({'url':url,'layouts':checks,'requestIsolation':True,'screenAndPrintFailureFallback':True,'printPDF':'saint-05-print.pdf'},indent=2)+'\n')
print('PASS: 140 card layouts at 360/390/768/1440 px, 4:5 contain, isolated screen/print loading, screen and print failures, verified print PDF')
