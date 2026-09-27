"""Local browser smoke with a stub executor. Never invokes model/search services.

Run after npm run build; requires Playwright Chromium and its OS libraries.
"""
import argparse, json, tempfile, threading, time
from pathlib import Path
import uvicorn
from playwright.sync_api import sync_playwright
from novelty_agent_framework.main import create_app

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--pdf', type=Path, default=Path('examples/MF2033k6lC.pdf'))
parser.add_argument('--report', type=Path, required=True, help='Existing UTF-8 report containing a heading and table; used only as a UI fixture')
parser.add_argument('--screenshots', type=Path, default=Path('/tmp'))
args = parser.parse_args()
args.screenshots.mkdir(parents=True, exist_ok=True)
workspace = tempfile.TemporaryDirectory(prefix='novelty-browser-')

def local_runner(directory, update, publish):
    update(stage='parse', done='parse')
    time.sleep(1)
    target=directory/'original.md'
    sample=args.report
    target.write_bytes(sample.read_bytes())
    return target

app=create_app(runs_root=Path(workspace.name),runner=local_runner)
server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=18010,log_level='warning'))
thread=threading.Thread(target=server.run,daemon=True);thread.start()
while not server.started: time.sleep(.05)
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1080})
        errors=[];page.on('pageerror',lambda error: errors.append(str(error)))
        page.goto('http://127.0.0.1:18010')
        page.locator('#file').set_input_files(args.pdf)
        page.locator('#start').click()
        page.wait_for_url('**/?run=*')
        run_url=page.url
        page.reload()
        status_url=run_url.split('?')[0]+'api/runs/'+run_url.split('run=')[1]
        page.route(status_url, lambda route: route.abort())
        page.locator('#connection-error').wait_for(state='visible',timeout=15000)
        assert page.locator('#status').inner_text()!='运行失败'
        page.route(status_url+'/report', lambda route: route.fulfill(status=500, content_type='application/json', body='{"detail":{"message":"test report read error"}}'))
        page.unroute(status_url)
        page.locator('#report-error').wait_for(state='visible',timeout=15000)
        assert page.locator('#status').inner_text()=='查新完成'
        page.unroute(status_url+'/report')
        page.locator('#retry-report').click()
        page.locator('#download').wait_for(state='visible',timeout=20000)
        assert page.locator('#status').inner_text()=='查新完成'
        assert page.locator('#report h1').count()>0
        assert page.locator('#report table').count()>0
        with page.expect_download() as download:
            page.locator('#download').click()
        downloaded=download.value
        assert Path(downloaded.path()).read_bytes()==args.report.read_bytes()
        page.screenshot(path=str(args.screenshots/'novelty-desktop.png'),full_page=False)
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(args.screenshots/'novelty-mobile.png'),full_page=False)
        page.wait_for_function('navigator.serviceWorker.controller !== null')
        cache_keys=page.evaluate('caches.keys()')
        cached=page.evaluate('async () => (await Promise.all((await caches.keys()).map(async k => (await (await caches.open(k)).keys()).map(r=>r.url)))).flat()')
        assert not any('/api/' in url for url in cached)
        page.context.set_offline(True)
        page.reload()
        page.locator('#service').wait_for(state='visible', timeout=15000)
        assert page.locator('#status').inner_text() != '运行失败'
        browser.close()
        print(json.dumps({'url':run_url,'page_errors':errors,'service_worker_caches':cache_keys,'cached_api':False,'mobile_overflow':False,'sample':'existing real report, local stub executor; no live model calls'},ensure_ascii=False))
        assert not errors
finally:
    server.should_exit=True;thread.join(timeout=10)
    workspace.cleanup()
