"""Local cold-cache measurements; not a production Lighthouse benchmark."""
import json, os, sys
from playwright.sync_api import sync_playwright

url, output = sys.argv[1:]
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.getenv('CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
    for selected in (False, True):
        context = browser.new_context(viewport={'width':390,'height':844}, device_scale_factor=2)
        if selected:
            context.add_init_script("localStorage.setItem('chysty_chyscec.selection.v1',JSON.stringify({version:1,saintId:'saint-05',assignedAt:'2026-10-22T00:00:00Z'}))")
        page = context.new_page()
        page.add_init_script("window.vitals={};new PerformanceObserver(l=>{for(const e of l.getEntries())window.vitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.vitals.cls=(window.vitals.cls||0)+e.value}).observe({type:'layout-shift',buffered:true});")
        responses=[]
        page.on('response',lambda r: responses.append(r))
        page.goto(url+('#moy-svyaty' if selected else ''),wait_until='networkidle')
        if selected:
            page.locator('#saint-card').scroll_into_view_if_needed()
            if page.locator('.saint-photo').count(): page.locator('.saint-photo').evaluate('(i)=>i.decode()')
        page.wait_for_timeout(500)
        entries=[]
        for r in responses:
            if r.ok:
                entries.append({'path':r.url.removeprefix(url),'bytes':len(r.body()),'type':r.request.resource_type})
        results.append({'scenario':'restored-05-at-card' if selected else 'first-visit-top','resources':entries,'requestCount':len(entries),'bodyBytes':sum(r['bytes'] for r in entries),'imageBytes':sum(r['bytes'] for r in entries if r['type']=='image'),'vitalsLocalUnthrottled':page.evaluate('window.vitals')})
        context.close()
    browser.close()
with open(output,'w') as f: json.dump({'url':url,'method':'Chromium, 390x844, DPR 2, fresh context per scenario; local HTTP response body bytes, no compression/throttling. LCP/CLS are lab observations, not field Web Vitals. No INP without real interactions.','results':results},f,indent=2)
