"""Run with a local server: SITE_TEST_URL=http://localhost:8765/chysty-chyscec/ python tests/check_browser.py.
Requires Python playwright and Chromium (/usr/bin/chromium by default).
"""
import os
from playwright.sync_api import sync_playwright
URL = os.environ.get('SITE_TEST_URL', 'http://localhost:8765/chysty-chyscec/')
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
    context = browser.new_context()
    context.add_init_script("Object.defineProperty(navigator,'share',{value:undefined}); Object.defineProperty(navigator,'clipboard',{value:{writeText:async text=>window.sharedText=text}}); window.print=()=>window.printCalled=true;")
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda response: errors.append(f'HTTP {response.status}: {response.url}') if response.status >= 400 else None)
    page.goto(URL)
    page.locator('#assign').click()
    first = page.locator('#saint-name').inner_text()
    page.locator('#name').fill('Тэставае імя')
    page.locator('#names-form button').click()
    page.reload()
    assert page.locator('#saint-name').inner_text() == first
    assert page.locator('#names-list').inner_text().startswith('Тэставае імя')
    page.locator('#share').click()
    page.wait_for_function('window.sharedText')
    shared = page.evaluate('window.sharedText')
    assert shared.endswith(URL) and 'Тэставае імя' not in shared, shared
    page.locator('#replace').click()
    page.locator('#dialog-yes').click()
    page.wait_for_function('(first)=>document.getElementById("saint-name").textContent!==first', arg=first)
    assert 'Тэставае імя' in page.locator('#names-list').inner_text()
    page.locator('#print').click()
    if page.locator('#print-photo').is_visible():
        page.locator('#print-photo').evaluate('(img)=>img.decode()')
    expected = URL.split('://', 1)[1].rstrip('/')
    assert page.locator('#print-site-url').inner_text() == expected
    assert 'Тэставае імя' not in page.locator('#print-card').inner_text()
    page.locator('#print-confirm').click()
    page.wait_for_function('window.printCalled')
    page.pdf(path='/tmp/chysty-chyscec-print.pdf', format='A4')
    page.locator('#print-close').click()
    # Exercise every saint and both screen/print image paths through real rendering.
    ids = page.evaluate("async()=> (await import('./saints.mjs')).default.saints.map(s=>s.id)")
    assert len(ids) == 35
    for saint_id in ids:
        page.evaluate("id=>localStorage.setItem('chysty_chyscec.selection.v1',JSON.stringify({version:1,saintId:id,assignedAt:new Date().toISOString()}))", saint_id)
        page.reload()
        approved = page.evaluate("async id=>!!(await import('./image-sizes.mjs')).imageSizes[id]", saint_id)
        assert page.locator('.saint-photo').count() == int(approved)
        if approved:
            page.locator('.saint-photo').evaluate('(img)=>img.decode()')
        page.locator('#print').click()
        assert page.locator('#print-photo').is_visible() == approved
        if approved:
            page.locator('#print-photo').evaluate('(img)=>img.decode()')
        else:
            assert page.locator('#print-photo').get_attribute('src') is None
        page.locator('#print-close').click()
    page.locator('#clear-names').click()
    page.locator('#dialog-yes').click()
    page.wait_for_function('document.querySelectorAll("#names-list li").length===0')
    page.goto(URL + '#answer-11')
    assert page.locator('#answer-11').evaluate('(el)=>el.open')
    page.set_viewport_size({'width':390,'height':844})
    page.goto(URL)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    page.goto(URL + 'sources.html')
    page.locator('a[href="index.html"]').click()
    assert page.locator('#saint-card').is_visible()
    assert not errors, errors
    browser.close()
    print('PASS: 35 saints, verified screen/print images and safe fallbacks, selection/replacement, persistence, names, private sharing, print/PDF, fragments, mobile width, sources; no browser errors or HTTP failures')
